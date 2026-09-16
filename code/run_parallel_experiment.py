"""
KDS-EL 高并发多进程实验调度系统 (High-Concurrency Parallel Experiment Runner)
========================================================================
设计目标：
  1. 便携移植：在另一台机器（无论 Windows 还是 Linux/Ubuntu 服务器）上开箱即用。
  2. 算力压榨：自动检测 CPU 物理/逻辑核心数，支持 --workers 参数自定义并发数。
  3. 线程隔离：子进程强制绑定 OMP/MKL/BLAS/NUMEXPR 为单线程，杜绝物理核多线程争抢。
  4. 智能调度：按数据集计算复杂度降序调度（LPT，最长作业优先），规避分布式长尾等待。
  5. 绝对安全：主进程独占文件写盘，彻底杜绝 Windows/Linux 下多进程写盘的文件锁竞争。
  6. 断点续跑：自动扫描输出目录下的 results_detail.csv，中断后重启直接跳过已完成轮次。
  7. 结构兼容：输出格式与标准实验完全一致（masks/, curves/, predictions/, results_detail.csv, results_summary.csv）。

用法示例：
  # 1. 默认运行 EMSWOA（自动使用 CPU核心数 - 2 的进程数）：
  python code/run_parallel_experiment.py --methods EMSWOA

  # 2. 指定使用 8 个核心并发，输出到指定目录：
  python code/run_parallel_experiment.py --methods EMSWOA --workers 8 --out-dir output/formal_experiment_emswoa

  # 3. 指定跑特定数据集或测试可用性：
  python code/run_parallel_experiment.py --methods EMSWOA --datasets Colon Lymphoma --num-runs 3 --dry-run
"""
import os
import sys
import csv
import time
import argparse
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict

# 强制限制底层线性代数库单线程，在导入 numpy/scipy 之前生效
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# 强制 UTF-8 输出，规避 Windows 终端 GBK 乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 确保脚本根目录位于 sys.path
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR)
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import numpy as np
import config
from utils import load_dataset, evaluate_subset
from algorithms import RUNNERS

# ── CSV 字段定义（与 run_formal_experiment.py 保持 100% 同步）──────────────────
FIELDS_DETAIL = [
    "Version", "Dataset", "Run",
    "Accuracy", "Error_Rate", "fitG", "Scalar_Fitness",
    "Num_Features", "SR", "Avg_NHD", "Best_Iter", "Time_sec"
]

FIELDS_SUMMARY = [
    "Version", "Dataset",
    "Mean_Acc", "Std_Acc",
    "Mean_Err", "Std_Err",
    "Mean_Scalar_Fit", "Std_Scalar_Fit",
    "Mean_Feat", "Std_Feat",
    "Mean_SR", "Std_SR",
    "Mean_NHD", "Std_NHD",
    "Mean_Best_Iter", "Std_Best_Iter",
    "Mean_Time", "Std_Time"
]

# 数据集先验复杂度评估（用于 LPT 最长作业优先调度）
DATASET_WEIGHTS = {
    "BASEHOCK": 100, "PCMAC": 80, "T1D": 50, "Gastric1": 40,
    "Gastric2": 35, "COIL20": 30, "Myeloma": 28, "madelon": 25,
    "ISOLET": 25, "ALL1": 22, "Gastric": 20, "ALL4": 18,
    "Prostate": 18, "DLBCL": 12, "Leukaemia": 12, "ALL_AML": 12,
    "Adenoma": 10, "SRBCT": 8, "Lymphoma": 7, "Colon": 5
}


def _worker_initializer():
    """
    子进程初始化器：
    强制将底层 C/Fortran 库的并行度限制为单线程，
    确保多进程并发时每个进程独立占用单核，不会发生核间线程抢占引发性能骤降。
    """
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    # 让子进程拥有独立的系统级随机源
    np.random.seed(int(time.time() * 1000) % 2**32 + os.getpid())


# 进程内数据集懒加载缓存（每个 worker 子进程在内存中各保存一份，避免跨进程 IPC 传输超大矩阵）
_WORKER_DATA_CACHE = {}


def _worker_run_task(task_args):
    """
    单次实验任务工作函数（在子进程中执行）：
    输入：(method_name, ds_name, run_idx, opts, txt_dir, mat_dir)
    返回：包含评测结果字典及相关数组的 package
    """
    method_name, ds_name, run_idx, opts, txt_dir, mat_dir = task_args

    # 1. 懒加载数据集
    cache_key = (ds_name, txt_dir, mat_dir)
    if cache_key not in _WORKER_DATA_CACHE:
        X, y = load_dataset(ds_name, txt_dir, mat_dir)
        _WORKER_DATA_CACHE[cache_key] = (X, y)
    else:
        X, y = _WORKER_DATA_CACHE[cache_key]

    if method_name not in RUNNERS:
        raise ValueError(f"未注册的算法: {method_name}")

    runner_fn = RUNNERS[method_name]

    # 2. 执行算法
    t0 = time.time()
    res = runner_fn(X, y, opts)
    elapsed = time.time() - t0

    # 3. 提取特征掩码
    if "mask" in res and res["mask"] is not None:
        mask = np.asarray(res["mask"], dtype=bool)
    elif "Gbest" in res:
        mask = (np.asarray(res["Gbest"]) > opts.get("thres", 0.6)).astype(bool)
    else:
        raise ValueError(f"算法 {method_name} 未返回特征掩码 mask 或 Gbest")

    # 4. 统一外部后验评价器（严格 5 折分层交叉验证）
    eval_res = evaluate_subset(X, y, mask, opts)

    acc = float(eval_res["accuracy"])
    err = float(eval_res["error_rate"])
    fitG = float(res["fitG"])
    scalar_fit = float(eval_res["scalar_fitness"])
    nf = int(eval_res["num_features"])
    sr = float(eval_res["feature_ratio"])
    nhd = res.get("nhd_curve", np.zeros(opts.get("T", 100) + 1))
    avg_nhd = float(np.mean(nhd[1:])) if np.any(nhd[1:]) else 0.0
    best_iter = int(np.argmin(res["curve"]))

    row = {
        "Version": method_name,
        "Dataset": ds_name,
        "Run": run_idx,
        "Accuracy": round(acc, 6),
        "Error_Rate": round(err, 6),
        "fitG": round(fitG, 6),
        "Scalar_Fitness": round(scalar_fit, 6),
        "Num_Features": nf,
        "SR": round(sr, 6),
        "Avg_NHD": round(avg_nhd, 6),
        "Best_Iter": best_iter,
        "Time_sec": round(elapsed, 2),
    }

    return {
        "method_name": method_name,
        "ds_name": ds_name,
        "run_idx": run_idx,
        "row": row,
        "mask": mask,
        "y_pred": eval_res["y_pred"],
        "y_true": eval_res["y_true"],
        "curve": res["curve"],
        "nhd": nhd,
        "elapsed": elapsed,
    }


def compute_stats(rows):
    """计算指标均值与样本标准差（ddof=1）。"""
    accs = np.array([r["Accuracy"] for r in rows])
    errs = np.array([r.get("Error_Rate", 1.0 - r["Accuracy"]) for r in rows])
    sfits = np.array([r.get("Scalar_Fitness", r.get("fitG", 1.0 - r["Accuracy"])) for r in rows])
    feats = np.array([r["Num_Features"] for r in rows])
    srs = np.array([r.get("SR", 0.0) for r in rows])
    nhds = np.array([r.get("Avg_NHD", 0.0) for r in rows])
    iters = np.array([r.get("Best_Iter", 0) for r in rows])
    times = np.array([r.get("Time_sec", 0.0) for r in rows])
    n = len(rows)
    return {
        "Mean_Acc": round(float(np.mean(accs)), 6),
        "Std_Acc": round(float(np.std(accs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Err": round(float(np.mean(errs)), 6),
        "Std_Err": round(float(np.std(errs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Scalar_Fit": round(float(np.mean(sfits)), 6),
        "Std_Scalar_Fit": round(float(np.std(sfits, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Feat": round(float(np.mean(feats)), 1),
        "Std_Feat": round(float(np.std(feats, ddof=1)), 1) if n >= 2 else 0.0,
        "Mean_SR": round(float(np.mean(srs)), 6),
        "Std_SR": round(float(np.std(srs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_NHD": round(float(np.mean(nhds)), 6),
        "Std_NHD": round(float(np.std(nhds, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Best_Iter": round(float(np.mean(iters)), 1),
        "Std_Best_Iter": round(float(np.std(iters, ddof=1)), 1) if n >= 2 else 0.0,
        "Mean_Time": round(float(np.mean(times)), 1),
        "Std_Time": round(float(np.std(times, ddof=1)), 1) if n >= 2 else 0.0,
    }


def load_completed_records(csv_path):
    """从 detail CSV 读取已完成的 (Version, Dataset, Run) 集合与数据行。"""
    done = set()
    rows = []
    if not os.path.exists(csv_path):
        return done, rows
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                key = (r["Version"], r["Dataset"], int(r["Run"]))
                done.add(key)
                r["Accuracy"] = float(r["Accuracy"])
                r["Error_Rate"] = float(r.get("Error_Rate", 1.0 - r["Accuracy"]))
                r["fitG"] = float(r.get("fitG", 1.0 - r["Accuracy"]))
                r["Scalar_Fitness"] = float(r.get("Scalar_Fitness", r["fitG"]))
                r["Num_Features"] = int(r["Num_Features"])
                r["SR"] = float(r.get("SR", 0.0))
                r["Avg_NHD"] = float(r.get("Avg_NHD", 0.0))
                r["Best_Iter"] = int(r.get("Best_Iter", 0))
                r["Time_sec"] = float(r.get("Time_sec", 0.0))
                rows.append(r)
    except Exception as e:
        print(f"  [WARN] 读取已有结果失败: {e}，将视为新实验")
        return set(), []
    return done, rows


def regenerate_summary(csv_summary_path, all_rows):
    """从所有 detail 行重新构建 summary CSV。"""
    groups = defaultdict(list)
    for r in all_rows:
        groups[(r["Version"], r["Dataset"])].append(r)

    with open(csv_summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS_SUMMARY)
        writer.writeheader()
        for (method, ds), rows in sorted(groups.items()):
            stats = compute_stats(rows)
            writer.writerow({"Version": method, "Dataset": ds, **stats})


def format_duration(seconds):
    """将秒格式化为易读的 hh:mm:ss 或 mm:ss。"""
    s = int(round(seconds))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}h {m:02d}m {sec:02d}s"
    return f"{m}m {sec:02d}s"


def main():
    parser = argparse.ArgumentParser(
        description="KDS-EL 高并发多进程并行实验调度系统",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--methods", nargs="+", default=["EMSWOA"],
                        help="待评测算法列表，如 EMSWOA, BPSO, bIRIME 等")
    parser.add_argument("--datasets", nargs="+", default=None,
                        help="指定评测的数据集列表（默认使用标准 20 个基准数据集）")
    parser.add_argument("--num-runs", type=int, default=10,
                        help="每个数据集独立运行的重复次数")
    parser.add_argument("--workers", type=int, default=None,
                        help="并发工作进程数（默认自动使用: max(1, CPU核心数 - 2)）")
    parser.add_argument("--out-dir", type=str, default=None,
                        help="输出目录路径（默认自动生成带时间戳的独立目录，或传入已有目录以支持断点续跑）")
    parser.add_argument("--restart", action="store_true",
                        help="强制清空已有输出目录，从头开始运行")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅扫描数据集可用性及调度任务计划，不启动实际计算")
    parser.add_argument("--txt-dir", type=str, default=config.DATA_DIR_TXT,
                        help="TXT 格式微阵列数据集目录")
    parser.add_argument("--mat-dir", type=str, default=config.DATA_DIR_MAT,
                        help="MAT 格式高维数据集目录")
    args = parser.parse_args()

    # ── 1. 计算核心数与并发配置 ───────────────────────────────────────
    cpu_count = os.cpu_count() or 4
    if args.workers is None:
        workers = max(1, cpu_count - 2)
    else:
        workers = max(1, min(args.workers, cpu_count))

    print(f"\n{'=' * 78}")
    print(f"  ⚡ KDS-EL 高并发多进程实验调度系统")
    print(f"  CPU 逻辑核心: {cpu_count} | 设定并发进程数: {workers}")
    print(f"  线程隔离防护: OMP/MKL/BLAS 线程限制为 1 (杜绝核心争抢)")
    print(f"{'=' * 78}")

    # ── 2. 输出目录与路径初始化 ───────────────────────────────────────
    if args.out_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = os.path.join(config.OUT_DIR, f"formal_experiment_parallel_{timestamp}")
    else:
        out_dir = os.path.abspath(args.out_dir)

    os.makedirs(out_dir, exist_ok=True)
    masks_dir = os.path.join(out_dir, "masks")
    preds_dir = os.path.join(out_dir, "predictions")
    curves_dir = os.path.join(out_dir, "curves")
    os.makedirs(masks_dir, exist_ok=True)
    os.makedirs(preds_dir, exist_ok=True)
    os.makedirs(curves_dir, exist_ok=True)

    csv_detail_path = os.path.join(out_dir, "results_detail.csv")
    csv_summary_path = os.path.join(out_dir, "results_summary.csv")

    print(f"输出根目录: {out_dir}")

    # ── 3. 扫描数据集可用性 ───────────────────────────────────────────
    candidate_datasets = args.datasets if args.datasets else config.BENCHMARK_20_DATASETS
    print(f"\n[1/4] 扫描数据集可用性...")
    available_datasets = []
    for ds in candidate_datasets:
        try:
            X, y = load_dataset(ds, args.txt_dir, args.mat_dir)
            available_datasets.append((ds, X.shape[0], X.shape[1], len(np.unique(y))))
            print(f"  [OK] {ds:20s}  样本量={X.shape[0]:4d}  特征数={X.shape[1]:5d}  类别数={len(np.unique(y)):2d}")
        except Exception as e:
            print(f"  [FAIL] {ds:20s}  无法加载: {e}")

    if not available_datasets:
        print("\n[ERROR] 没有可用数据集，程序退出。")
        return

    # ── 4. 断点续跑扫描 ───────────────────────────────────────────────
    if args.restart and os.path.exists(csv_detail_path):
        print("\n[WARN] 检测到 --restart 参数，清空已有结果...")
        os.remove(csv_detail_path)
        done_set = set()
        all_rows = []
    else:
        done_set, all_rows = load_completed_records(csv_detail_path)

    # 初始化 detail CSV 表头
    if not os.path.exists(csv_detail_path):
        with open(csv_detail_path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS_DETAIL).writeheader()

    # ── 5. 构建任务队列并应用 LPT 最长作业优先排序 ─────────────────────
    opts = dict(config.OPTS)
    pending_tasks = []
    for method in args.methods:
        if method not in RUNNERS:
            print(f"[ERROR] 算法 {method} 未在 RUNNERS 中注册，可选算法包括: {list(RUNNERS.keys())}")
            return
        for ds, n_samp, n_feat, _ in available_datasets:
            # 计算该数据集的估计计算权重
            weight = DATASET_WEIGHTS.get(ds, int((n_samp ** 2) * (n_feat / 1000)))
            for run_idx in range(1, args.num_runs + 1):
                if (method, ds, run_idx) in done_set:
                    continue
                # 记录 (任务参数, 调度权重)
                task_args = (method, ds, run_idx, opts, args.txt_dir, args.mat_dir)
                pending_tasks.append((task_args, weight))

    # 按权重降序排序（最重的数据集如 BASEHOCK, PCMAC 先跑，轻量级微阵列后跑填空）
    pending_tasks.sort(key=lambda x: x[1], reverse=True)
    task_list = [item[0] for item in pending_tasks]

    total_tasks = len(args.methods) * len(available_datasets) * args.num_runs
    already_done = len(done_set)
    pending_count = len(task_list)

    print(f"\n[2/4] 任务统计:")
    print(f"  总任务量: {len(args.methods)} 算法 × {len(available_datasets)} 数据集 × {args.num_runs} 轮 = {total_tasks} 运行")
    print(f"  已完成:   {already_done} 项")
    print(f"  待执行:   {pending_count} 项")

    if args.dry_run:
        print("\n[Dry-run 模式] 调度计划检查完毕，退出。")
        return

    if pending_count == 0:
        print("\n✅ 所有实验任务已全部完成！无需重复计算。")
        regenerate_summary(csv_summary_path, all_rows)
        _print_terminal_summary(all_rows, [d[0] for d in available_datasets], args.methods)
        return

    # ── 6. 启动多进程高并发调度 ───────────────────────────────────────
    print(f"\n[3/4] 启动高并发调度池（{workers} Workers，主进程独立安全写盘）...")
    print(f"{'─' * 78}")
    start_time = time.time()
    completed_in_this_session = 0
    recent_durations = []

    with ProcessPoolExecutor(max_workers=workers, initializer=_worker_initializer) as executor:
        # 提交所有待跑任务
        future_to_task = {executor.submit(_worker_run_task, task): task for task in task_list}

        for future in as_completed(future_to_task):
            task_info = future_to_task[future]
            try:
                result = future.result()
            except Exception as e:
                method_name, ds_name, run_idx = task_info[0], task_info[1], task_info[2]
                print(f"\n[ERROR] 任务执行失败: {method_name} - {ds_name} - Run {run_idx}: {e}")
                continue

            # ── 主进程独占安全写盘（绝无锁冲突）────────────────────────
            row = result["row"]
            all_rows.append(row)
            done_set.add((result["method_name"], result["ds_name"], result["run_idx"]))

            # 1. 追加写入 detail CSV
            with open(csv_detail_path, "a", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDS_DETAIL).writerow(row)

            # 2. 保存特征掩码
            mask_file = os.path.join(masks_dir, f"mask_{result['method_name']}_{result['ds_name']}_run{result['run_idx']}.npy")
            np.save(mask_file, result["mask"])

            # 3. 保存样本级折外预测
            pred_file = os.path.join(preds_dir, f"pred_{result['method_name']}_{result['ds_name']}_run{result['run_idx']}.npz")
            np.savez_compressed(pred_file, y_pred=result["y_pred"], y_true=result["y_true"])

            # 4. 保存收敛曲线
            curve_file = os.path.join(curves_dir, f"curve_{result['method_name']}_{result['ds_name']}_run{result['run_idx']}.npy")
            np.save(curve_file, result["curve"])
            if result["nhd"] is not None:
                nhd_file = os.path.join(curves_dir, f"nhd_{result['method_name']}_{result['ds_name']}_run{result['run_idx']}.npy")
                np.save(nhd_file, result["nhd"])

            # ── 进度计算与动态 ETA 预估 ──────────────────────────────
            completed_in_this_session += 1
            current_total_done = already_done + completed_in_this_session
            progress_pct = (current_total_done / total_tasks) * 100.0

            recent_durations.append(result["elapsed"])
            if len(recent_durations) > 20:
                recent_durations.pop(0)

            elapsed_total = time.time() - start_time
            # 动态 ETA：基于并发进程吞吐率
            throughput = completed_in_this_session / elapsed_total if elapsed_total > 0 else 0
            remaining_tasks = total_tasks - current_total_done
            eta_sec = (remaining_tasks / throughput) if throughput > 0 else 0

            # 打印格式化进度单行
            print(f"[{current_total_done:3d}/{total_tasks:3d} {progress_pct:5.1f}%] "
                  f"{result['method_name']:8s} | {result['ds_name']:12s} | "
                  f"Run {result['run_idx']:2d} | "
                  f"Acc: {row['Accuracy']:.4f} | Feat: {row['Num_Features']:4d} | "
                  f"t: {row['Time_sec']:6.1f}s | "
                  f"已用: {format_duration(elapsed_total)} | ETA: {format_duration(eta_sec)}",
                  flush=True)

            # 每完成 10 项，刷新一次 summary CSV
            if completed_in_this_session % 10 == 0:
                regenerate_summary(csv_summary_path, all_rows)

    # ── 7. 实验收尾与汇总打印 ─────────────────────────────────────────
    total_elapsed = time.time() - start_time
    print(f"\n{'=' * 78}")
    print(f"[4/4] ✅ 所有计算任务圆满完成！")
    print(f"  本次总耗时: {format_duration(total_elapsed)} ({total_elapsed:.1f} 秒)")
    print(f"  更新最终汇总文件...")
    regenerate_summary(csv_summary_path, all_rows)
    print(f"  详细数据: {csv_detail_path}")
    print(f"  汇总统计: {csv_summary_path}")
    print(f"{'=' * 78}")

    _print_terminal_summary(all_rows, [d[0] for d in available_datasets], args.methods)


def _print_terminal_summary(all_rows, available_datasets, methods):
    """在终端格式化输出均值与标准差对比汇总表。"""
    groups = defaultdict(list)
    for r in all_rows:
        groups[(r["Version"], r["Dataset"])].append(r)

    lookup = {}
    for (method, ds), rows in groups.items():
        lookup[(method, ds)] = compute_stats(rows)

    print("\n" + "=" * 78)
    print("各算法在各数据集上的纯分类准确率 (Mean ± Std, 10 Runs)")
    print("=" * 78)
    header = f"{'Dataset':20s}" + "".join(f"{m:>18s}" for m in methods)
    print(header)
    print("-" * len(header))

    for ds in available_datasets:
        vals = []
        for m in methods:
            item = lookup.get((m, ds))
            if item:
                vals.append(f"{item['Mean_Acc']:.4f}±{item['Std_Acc']:.4f}")
            else:
                vals.append("        N/A       ")
        print(f"{ds:20s}" + "".join(f"{v:>18s}" for v in vals))

    print("\n" + "=" * 78)
    print("跨数据集平均分类准确率:")
    print("=" * 78)
    for m in methods:
        acc_list = [lookup[(m, ds)]["Mean_Acc"] for ds in available_datasets if (m, ds) in lookup]
        feat_list = [lookup[(m, ds)]["Mean_Feat"] for ds in available_datasets if (m, ds) in lookup]
        time_list = [lookup[(m, ds)]["Mean_Time"] for ds in available_datasets if (m, ds) in lookup]
        if acc_list:
            print(f"  {m:15s} -> 平均 Acc: {np.mean(acc_list):.4f} | "
                  f"平均特征数: {np.mean(feat_list):6.1f} | "
                  f"平均耗时: {np.mean(time_list):6.1f}s (n={len(acc_list)} 数据集)")


if __name__ == "__main__":
    main()
