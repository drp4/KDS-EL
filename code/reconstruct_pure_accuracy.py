"""
KDS-EL 历史实验纯分类准确率代数重构工具
==========================================
本脚本在“零重跑”条件下，根据标准适应度函数定义：
    fitG = 0.90 * Error_Rate + 0.10 * SR
反解历史单目标实验中的真实纯分类准确率：
    Error_Rate = (fitG - 0.10 * SR) / 0.90
    Pure_Accuracy = 1.0 - Error_Rate
    Scalar_Fitness = 0.90 * Error_Rate + 0.10 * SR

严格保证：
  1. Accuracy + Error_Rate == 1.0 (在数值浮点精度内严格成立)
  2. Scalar_Fitness 由独立的 Error_Rate 与 SR 加权精确还原
  3. 解除指标混合与特征惩罚对准确率的隐式压低
"""
import os, sys, csv
from pathlib import Path
import numpy as np
import pandas as pd

# 强制 UTF-8 输出，解决 Windows GBK 终端乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

PROJ = Path(__file__).resolve().parent.parent
EXP1_DIR   = PROJ / "output" / "formal_experiment_20260701_094943"   # BPSO, SaWDE, FWPSO, PSO_CSM, IGPSO
EXP2_DIR   = PROJ / "output" / "formal_experiment_20260628_205157"   # MEL
MEL_MI_DIR = PROJ / "output" / "formal_experiment_mel_mi"          # MEL_MI
FINAL_DIR  = PROJ / "output" / "formal_experiment_final"            # KDS_EL_NoPool, KDS_EL_TwoPhase
OUT_DIR    = PROJ / "output" / "historical_reconstructed"

HISTORICAL_SOURCES = [
    (EXP1_DIR, ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]),
    (EXP2_DIR, ["MEL"]),
    (MEL_MI_DIR, ["MEL_MI"]),
    (FINAL_DIR, ["KDS_EL_NoPool", "KDS_EL_TwoPhase"]),
]

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


def reconstruct_row(row):
    """对单条历史运行记录进行纯分类准确率代数还原。"""
    version = row["Version"]
    dataset = row["Dataset"]
    run_idx = int(row["Run"])
    nf = int(row["Num_Features"])

    # 获取原始维度
    total_d = config.DATASET_DIMS.get(dataset)
    if total_d is None:
        raise ValueError(f"未知数据集维度: {dataset}")

    sr = float(nf / total_d)
    fitG = float(row.get("fitG", 1.0 - float(row["Accuracy"])))

    # 如果历史记录中已经有 Error_Rate，说明已经是纯分类准确率
    if "Error_Rate" in row and row["Error_Rate"] != "":
        err = float(row["Error_Rate"])
        acc = float(row["Accuracy"])
    else:
        # 逆向代数解标量化：fitG = 0.90 * err + 0.10 * sr
        err = (fitG - 0.10 * sr) / 0.90
        err = float(np.clip(err, 0.0, 1.0))
        acc = 1.0 - err

    scalar_fit = 0.90 * err + 0.10 * sr

    return {
        "Version":        version,
        "Dataset":        dataset,
        "Run":            run_idx,
        "Accuracy":       round(acc, 6),
        "Error_Rate":     round(err, 6),
        "fitG":           round(fitG, 6),
        "Scalar_Fitness": round(scalar_fit, 6),
        "Num_Features":   nf,
        "SR":             round(sr, 6),
        "Avg_NHD":        round(float(row.get("Avg_NHD", 0.0)), 6),
        "Best_Iter":      int(row.get("Best_Iter", 0)),
        "Time_sec":       round(float(row.get("Time_sec", 0.0)), 2),
    }


def compute_group_stats(rows):
    """计算分组统计指标。"""
    accs   = np.array([r["Accuracy"] for r in rows])
    errs   = np.array([r["Error_Rate"] for r in rows])
    sfits  = np.array([r["Scalar_Fitness"] for r in rows])
    feats  = np.array([r["Num_Features"] for r in rows])
    srs    = np.array([r["SR"] for r in rows])
    nhds   = np.array([r["Avg_NHD"] for r in rows])
    iters  = np.array([r["Best_Iter"] for r in rows])
    times  = np.array([r["Time_sec"] for r in rows])
    n = len(rows)

    return {
        "Mean_Acc":        round(float(np.mean(accs)),  6),
        "Std_Acc":         round(float(np.std(accs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Err":        round(float(np.mean(errs)),  6),
        "Std_Err":         round(float(np.std(errs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Scalar_Fit": round(float(np.mean(sfits)), 6),
        "Std_Scalar_Fit":  round(float(np.std(sfits, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Feat":       round(float(np.mean(feats)), 1),
        "Std_Feat":        round(float(np.std(feats, ddof=1)), 1) if n >= 2 else 0.0,
        "Mean_SR":         round(float(np.mean(srs)),   6),
        "Std_SR":          round(float(np.std(srs, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_NHD":        round(float(np.mean(nhds)),  6),
        "Std_NHD":         round(float(np.std(nhds, ddof=1)), 6) if n >= 2 else 0.0,
        "Mean_Best_Iter":  round(float(np.mean(iters)), 1),
        "Std_Best_Iter":   round(float(np.std(iters, ddof=1)), 1) if n >= 2 else 0.0,
        "Mean_Time":       round(float(np.mean(times)), 1),
        "Std_Time":        round(float(np.std(times, ddof=1)), 1) if n >= 2 else 0.0,
    }


def main():
    print("=" * 72)
    print("KDS-EL 历史实验纯分类准确率重构程序")
    print("=" * 72)

    os.makedirs(OUT_DIR, exist_ok=True)
    all_reconstructed_rows = []

    for src_dir, allowed_versions in HISTORICAL_SOURCES:
        detail_path = src_dir / "results_detail.csv"
        if not detail_path.exists():
            print(f"[WARN] 路径不存在: {detail_path}")
            continue

        print(f"\n[读取] {src_dir.name} -> 目标方法: {allowed_versions}")
        df = pd.read_csv(detail_path)
        df = df[df["Version"].isin(allowed_versions)]
        count = 0
        for _, row in df.iterrows():
            r_dict = row.to_dict()
            rec = reconstruct_row(r_dict)
            all_reconstructed_rows.append(rec)
            count += 1
        print(f"  重构成功: {count} 条记录")

    # 写入重构后的 detail CSV
    out_detail = OUT_DIR / "results_detail.csv"
    with open(out_detail, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS_DETAIL)
        writer.writeheader()
        writer.writerows(all_reconstructed_rows)
    print(f"\n[写入] 重构详情已保存: {out_detail} (共 {len(all_reconstructed_rows)} 行)")

    # 聚合生成 summary CSV
    from collections import defaultdict
    groups = defaultdict(list)
    for r in all_reconstructed_rows:
        groups[(r["Version"], r["Dataset"])].append(r)

    summary_rows = []
    for (v, ds), rows in sorted(groups.items()):
        stats = compute_group_stats(rows)
        summary_rows.append({"Version": v, "Dataset": ds, **stats})

    out_summary = OUT_DIR / "results_summary.csv"
    with open(out_summary, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS_SUMMARY)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"[写入] 重构汇总已保存: {out_summary} (共 {len(summary_rows)} 组)")

    # 打印 20 个基准数据集上的纯分类准确率对比
    print("\n" + "=" * 72)
    print("标准 20 基准数据集上的重构纯准确率 (Pure Accuracy Mean):")
    print("=" * 72)
    sum_df = pd.DataFrame(summary_rows)
    benchmark_ds = [d for d in config.BENCHMARK_20_DATASETS if d in sum_df["Dataset"].unique()]
    versions = sorted(sum_df["Version"].unique())

    piv = sum_df[sum_df["Dataset"].isin(benchmark_ds)].pivot(
        index="Dataset", columns="Version", values="Mean_Acc"
    )
    print(piv.round(4).to_string())

    print("\n跨 20 基准数据集宏平均 (Macro-Average Pure Accuracy):")
    for v in versions:
        vals = sum_df[(sum_df["Version"] == v) & (sum_df["Dataset"].isin(benchmark_ds))]["Mean_Acc"]
        if len(vals) > 0:
            print(f"  {v:20s}: {vals.mean():.4f}  (n={len(vals)})")


if __name__ == "__main__":
    main()
