"""
KDS-EL 正式实验脚本（MEL 协议，支持断点续跑）
==============================================
完全对标 MEL 论文实验标准：
  - 10 次独立运行（每轮不固定随机种子，让 RNG 自然随机）
  - 报告 Mean ± Std
  - 可做 Wilcoxon / Friedman 统计检验

断点续跑：
  - 指定 --out-dir 指向已有输出目录，自动跳过已完成的运行
  - 使用 --restart 强制从头开始（清空已有 CSV）
  - 每次运行完成后立即写入 CSV，中断最多丢失 1 次运行

实验内容：
  - 消融实验：MEL → KDS_EL_DRS → KDS_EL_KER → KDS_EL
  - SOTA 对比：BPSO, SaWDE, FWPSO, PSO_CSM, IGPSO + KDS_EL
"""
import os, sys, csv, argparse
import numpy as np
from time import time
from datetime import datetime

# 强制 UTF-8 输出，解决 Windows GBK 终端中文乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from utils import load_dataset
from algorithms import RUNNERS

# ── 实验配置 ─────────────────────────────────────────────────────────────
NUM_RUNS = 10          # 对标 MEL: numRun = 10

ABLATION_METHODS = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]
SOTA_METHODS     = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
ALL_METHODS      = ABLATION_METHODS + SOTA_METHODS

# CSV 字段
FIELDS_DETAIL  = ["Version", "Dataset", "Run",
                  "Accuracy", "fitG", "Num_Features", "SR",
                  "Avg_NHD", "Best_Iter", "Time_sec"]
FIELDS_SUMMARY = ["Version", "Dataset",
                  "Mean_Acc", "Std_Acc",
                  "Mean_Feat", "Std_Feat",
                  "Mean_SR", "Std_SR",
                  "Mean_NHD", "Std_NHD",
                  "Mean_Best_Iter", "Std_Best_Iter",
                  "Mean_Time", "Std_Time"]


def compute_stats(rows):
    """从多次运行结果计算 Mean ± Std（ddof=1）。"""
    accs   = np.array([r["Accuracy"]     for r in rows])
    feats  = np.array([r["Num_Features"] for r in rows])
    srs    = np.array([r["SR"]           for r in rows])
    nhds   = np.array([r["Avg_NHD"]      for r in rows])
    iters  = np.array([r["Best_Iter"]    for r in rows])
    times  = np.array([r["Time_sec"]     for r in rows])
    n = len(rows)
    return {
        "Mean_Acc":       round(float(np.mean(accs)),  6),
        "Std_Acc":        round(float(np.std(accs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Feat":      round(float(np.mean(feats)), 1),
        "Std_Feat":       round(float(np.std(feats, ddof=1)), 1) if n >= 2 else 0.0,
        "Mean_SR":        round(float(np.mean(srs)),   6),
        "Std_SR":         round(float(np.std(srs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_NHD":       round(float(np.mean(nhds)),  6),
        "Std_NHD":        round(float(np.std(nhds, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Best_Iter": round(float(np.mean(iters)), 1),
        "Std_Best_Iter":  round(float(np.std(iters, ddof=1)), 1) if n >= 2 else 0.0,
        "Mean_Time":      round(float(np.mean(times)), 1),
        "Std_Time":       round(float(np.std(times, ddof=1)), 1) if n >= 2 else 0.0,
    }


def load_completed(csv_path):
    """从已有 detail CSV 加载已完成的 (Method, Dataset, Run) 集合。
    如果 CSV 不存在或损坏，返回空集合和空行列表。
    """
    done = set()
    rows = []
    if not os.path.exists(csv_path):
        return done, rows
    try:
        with open(csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                key = (r["Version"], r["Dataset"], int(r["Run"]))
                done.add(key)
                # 恢复数值类型以便后续计算
                r["Accuracy"]     = float(r["Accuracy"])
                r["fitG"]         = float(r.get("fitG", 1 - r["Accuracy"]))
                r["Num_Features"] = int(r["Num_Features"])
                r["SR"]           = float(r.get("SR", 0.0))
                r["Avg_NHD"]      = float(r["Avg_NHD"])
                r["Best_Iter"]    = int(r.get("Best_Iter", 0))
                r["Time_sec"]     = float(r["Time_sec"])
                rows.append(r)
    except Exception as e:
        print(f"  [WARN] 读取已有结果失败: {e}，视为新实验")
        return set(), []
    return done, rows


def write_detail_row(csv_path, row):
    """追加一行到 detail CSV（每跑完一次立即写入，保证断点安全）。"""
    with open(csv_path, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS_DETAIL).writerow(row)


def regenerate_summary(csv_summary_path, all_detail_rows):
    """从所有 detail 行重建 summary CSV。"""
    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_detail_rows:
        groups[(r["Version"], r["Dataset"])].append(r)

    with open(csv_summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS_SUMMARY)
        writer.writeheader()
        for (method, ds), rows in sorted(groups.items()):
            stats = compute_stats(rows)
            writer.writerow({"Version": method, "Dataset": ds, **stats})


def build_summary_lookup(all_detail_rows):
    """从 detail 行构建 (method, dataset) -> stats 字典。"""
    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_detail_rows:
        groups[(r["Version"], r["Dataset"])].append(r)
    lookup = {}
    for (method, ds), rows in groups.items():
        lookup[(method, ds)] = compute_stats(rows)
    return lookup


def main():
    parser = argparse.ArgumentParser(description="KDS-EL 正式实验 (MEL 协议, 支持断点续跑)")
    parser.add_argument("--methods", type=str, default="all",
                        help="实验范围: all/ablation/sota 或逗号分隔的方法名")
    parser.add_argument("--out-dir", type=str, default=None,
                        help="输出目录。若已存在则自动续跑，默认 output/formal_experiment_<timestamp>")
    parser.add_argument("--datasets", type=str, default="all",
                        help="数据集列表(逗号分隔)或 all")
    parser.add_argument("--restart", action="store_true",
                        help="强制从头开始，清空已有 CSV")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅扫描数据集，不跑实验")
    args = parser.parse_args()

    # ── 方法列表 ─────────────────────────────────────────────────────
    method_scope = args.methods
    if method_scope == "all":
        methods = ALL_METHODS
    elif method_scope == "ablation":
        methods = ABLATION_METHODS
    elif method_scope == "sota":
        methods = SOTA_METHODS  # KDS_EL 复用消融结果，不重跑
    else:
        methods = [m.strip() for m in args.methods.split(",") if m.strip()]

    # 验证方法名
    valid = set(ALL_METHODS)
    for m in methods:
        if m not in valid:
            print(f"[ERROR] 未知方法: {m}，可选: {sorted(valid)}")
            return

    # ── 输出目录 ─────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.out_dir:
        out_dir = args.out_dir
    else:
        out_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", f"formal_experiment_{timestamp}")

    is_resume = False
    if os.path.exists(out_dir) and not args.restart:
        # 检查是否有已有结果可以续跑
        test_csv = os.path.join(out_dir, "results_detail.csv")
        if os.path.exists(test_csv) and os.path.getsize(test_csv) > 0:
            is_resume = True

    os.makedirs(out_dir, exist_ok=True)
    curves_dir = os.path.join(out_dir, "curves")
    os.makedirs(curves_dir, exist_ok=True)

    # ── 数据集扫描 ───────────────────────────────────────────────────
    if args.datasets == "all":
        candidates = config.ALL_DATASETS
    else:
        candidates = [d.strip() for d in args.datasets.split(",") if d.strip()]

    print("=" * 72)
    print("KDS-EL 正式实验 (MEL 协议: 10 次独立运行, 不固定种子)")
    print(f"时间     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"方法     : {', '.join(methods)} ({len(methods)} 种)")
    print(f"候选数据集: {len(candidates)} 个")
    print(f"独立重复 : {NUM_RUNS} 次 (对标 MEL, 种子自然随机)")
    print(f"输出目录 : {out_dir}")
    if is_resume:
        print(f"模式     : 🔄 断点续跑 (已有结果将被跳过)")
    elif args.restart:
        print(f"模式     : 🔁 强制重启 (清空已有结果)")
    print("=" * 72)

    # ── 处理 restart ─────────────────────────────────────────────────
    csv_detail_path  = os.path.join(out_dir, "results_detail.csv")
    csv_summary_path = os.path.join(out_dir, "results_summary.csv")

    if args.restart:
        for p in [csv_detail_path, csv_summary_path]:
            if os.path.exists(p):
                os.remove(p)
        is_resume = False

    # ── 加载已完成列表 ───────────────────────────────────────────────
    if is_resume:
        done_set, existing_rows = load_completed(csv_detail_path)
        print(f"已加载 {len(done_set)} 条已完成记录 ({len(existing_rows)} 行)")
    else:
        done_set = set()
        existing_rows = []

    # ── 初始化/恢复 CSV ──────────────────────────────────────────────
    if not os.path.exists(csv_detail_path) or args.restart:
        with open(csv_detail_path, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS_DETAIL).writeheader()

    print("\n[扫描] 检查数据集可用性...")
    available = []
    for ds in candidates:
        try:
            X, y = load_dataset(ds, config.DATA_DIR_TXT, config.DATA_DIR_MAT)
            available.append((ds, X, y))
            uc = np.unique(y)
            print(f"  [OK] {ds:25s}  shape={str(X.shape):20s}  classes={len(uc)}")
        except Exception as e:
            print(f"  [FAIL] {ds:25s}  {e}")

    print(f"\n可用数据集: {len(available)}/{len(candidates)}")
    if args.dry_run:
        print("Dry-run 模式，结束。")
        return

    if not available:
        print("[ERROR] 无可用数据集，退出。")
        return

    # ── 统计待跑任务 ─────────────────────────────────────────────────
    total_runs = len(methods) * len(available) * NUM_RUNS
    already_done = 0
    for method_name in methods:
        for ds_name, _, _ in available:
            for run_idx in range(1, NUM_RUNS + 1):
                if (method_name, ds_name, run_idx) in done_set:
                    already_done += 1
    pending = total_runs - already_done

    if is_resume:
        print(f"\n续跑统计: {already_done}/{total_runs} 已完成, {pending} 待跑")

    if pending == 0:
        print("\n✅ 所有任务已完成，无需运行。")
        # 仍然重建 summary 并打印汇总表
        all_rows = list(existing_rows)
        regenerate_summary(csv_summary_path, all_rows)
        _print_final_tables(all_rows, available, methods)
        return

    # ── 实验参数 ─────────────────────────────────────────────────────
    opts = dict(config.OPTS)

    # ── 开始运行 ─────────────────────────────────────────────────────
    completed = already_done
    grand_start = time()

    print(f"\n{'=' * 72}")
    print(f"开始运行: {len(methods)} 方法 × {len(available)} 数据集 × {NUM_RUNS} 次 = {total_runs} 次")
    print(f"断点续跑: {'是' if is_resume else '否'}, 待跑 {pending} 次")
    print(f"对标 MEL: numRun={NUM_RUNS}, 不固定随机种子 (RNG 自然流动)")
    print(f"{'=' * 72}")

    # 在内存中维护所有已完成行（包括本次新跑的），用于最后重建 summary
    all_rows = list(existing_rows)

    for method_name in methods:
        if method_name not in RUNNERS:
            print(f"\n  [SKIP] {method_name} — 未在 RUNNERS 中注册")
            continue
        runner_fn = RUNNERS[method_name]

        print(f"\n{'─' * 72}")
        print(f"方法: {method_name}")
        print(f"{'─' * 72}")

        for ds_name, X, y in available:
            ds_start = time()
            ds_pending = 0
            ds_done = 0
            run_rows_this_ds = []

            for run_idx in range(1, NUM_RUNS + 1):
                key = (method_name, ds_name, run_idx)
                if key in done_set:
                    # 已跑过，收集已有行（用于后续统计）
                    existing = [r for r in existing_rows
                                if r["Version"] == method_name
                                and r["Dataset"] == ds_name
                                and r["Run"] == run_idx]
                    if existing:
                        run_rows_this_ds.append(existing[0])
                    ds_done += 1
                    continue

                ds_pending += 1

                # 对标 MEL: 不调用 np.random.seed()，让 RNG 自然随机
                t0 = time()
                res = runner_fn(X, y, opts)
                elapsed = time() - t0

                fitG = float(res["fitG"])
                acc  = 1.0 - fitG
                nf   = int(res["nf"])
                d    = X.shape[1]
                sr   = nf / d if d > 0 else 0.0
                nhd  = res.get("nhd_curve", np.zeros(opts["T"] + 1))
                avg_nhd = float(np.mean(nhd[1:])) if np.any(nhd[1:]) else 0.0
                best_iter = int(np.argmin(res["curve"]))

                row = {
                    "Version":      method_name,
                    "Dataset":      ds_name,
                    "Run":          run_idx,
                    "Accuracy":     round(acc, 6),
                    "fitG":         round(fitG, 6),
                    "Num_Features": nf,
                    "SR":           round(sr, 6),
                    "Avg_NHD":      round(avg_nhd, 6),
                    "Best_Iter":    best_iter,
                    "Time_sec":     round(elapsed, 2),
                }
                run_rows_this_ds.append(row)
                all_rows.append(row)
                done_set.add(key)

                # ⚡ 立即写入 CSV（断点安全：中断最多丢失当前这一条）
                write_detail_row(csv_detail_path, row)

                # 保存曲线
                np.save(os.path.join(curves_dir,
                    f"curve_{method_name}_{ds_name}_run{run_idx}.npy"), res["curve"])
                np.save(os.path.join(curves_dir,
                    f"nhd_{method_name}_{ds_name}_run{run_idx}.npy"), nhd)

                completed += 1
                print(f"  [{completed:4d}/{total_runs}] {method_name:10s}  {ds_name:20s}  "
                      f"run={run_idx:2d}  Acc={acc:.4f}  Feat={nf:4d}({sr:.1%})  "
                      f"Best={best_iter:3d}  "
                      f"NHD={avg_nhd:.3f}  t={elapsed:6.1f}s")

            # ── 每数据集跑完后更新 summary ──────────────────────────
            ds_n = len(run_rows_this_ds)
            if ds_n > 0:
                stats = compute_stats(run_rows_this_ds)
                ds_elapsed = time() - ds_start
                skip_info = f" (跳过{ds_done}条)" if ds_done > 0 else ""
                print(f"  └── [{method_name:10s}  {ds_name:20s}]  "
                      f"n={ds_n}/{NUM_RUNS}  "
                      f"Acc={stats['Mean_Acc']:.4f}±{stats['Std_Acc']:.4f}  "
                      f"Feat={stats['Mean_Feat']:.0f}±{stats['Std_Feat']:.0f}  "
                      f"({ds_elapsed:.0f}s){skip_info}")
            else:
                print(f"  └── [{method_name:10s}  {ds_name:20s}]  全部已跳过")

    # ── 重建 summary CSV ──────────────────────────────────────────────
    regenerate_summary(csv_summary_path, all_rows)

    # ── 打印最终汇总 ─────────────────────────────────────────────────
    _print_final_tables(all_rows, available, methods, out_dir)

    grand_elapsed = time() - grand_start
    print(f"\nDone. 结果目录: {out_dir}")
    print(f"本次耗时: {grand_elapsed:.0f}s ({grand_elapsed/3600:.2f}h)")


def _print_final_tables(all_rows, available, methods, out_dir=None):
    """打印最终汇总表。"""
    lookup = build_summary_lookup(all_rows)

    print(f"\n{'=' * 72}")
    print("汇总表: 各方法在各数据集上的 Accuracy (Mean ± Std)")
    print(f"{'=' * 72}")

    ds_order = [ds for ds, _, _ in available]
    method_order = methods

    header = f"{'Dataset':20s}" + "".join(f"{m:16s}" for m in method_order)
    print(header)
    print("-" * len(header))

    for ds in ds_order:
        vals = []
        for m in method_order:
            r = lookup.get((m, ds))
            if r:
                vals.append(f"{r['Mean_Acc']:.4f}±{r['Std_Acc']:.4f}")
            else:
                vals.append("      N/A       ")
        print(f"{ds:20s}" + "".join(f"{v:16s}" for v in vals))

    # ── 跨数据集平均 ─────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("跨数据集平均 Accuracy:")
    print(f"{'=' * 72}")
    for m in methods:
        accs = [lookup[(m, ds)]["Mean_Acc"]
                for ds in ds_order if (m, ds) in lookup]
        if accs:
            print(f"  {m:12s}:  {np.mean(accs):.4f}  (n={len(accs)} datasets)")


if __name__ == "__main__":
    main()
