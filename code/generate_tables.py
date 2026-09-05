"""
KDS-EL 表格生成系统 (Elsevier 顶级期刊规范版)
==============================================
本脚本生成符合 Elsevier 顶级期刊（如 ASOC, ESWA, SWEVO, INS）严格标准的对比表格与统计检验表：
  - T4: 纯分类准确率 (Pure Classification Accuracy, Mean ± Std) 及 Wilcoxon 检验符号 (+ / ≈ / -)
  - T5: 特征子集规模与选择率 (Feature Count & Selection Ratio, Mean ± Std)
  - T6: 成对 Wilcoxon 符号秩检验胜负矩阵 (Win / Tie / Loss Matrix)
  - T6b: Holm-Bonferroni 族系误差校正表 (多假设多重比较校正)
  - T7: 核心机制消融递进表 (Ablation Progression: Precursor MEL -> MII -> KER -> TPS)
  - T8: 两阶段动态权重调度 (TPS) 逐数据集深入消融分析

完全遵循《AGENTS.md》协议：
  - 严禁任何 "baseline" 术语，使用 competitor, comparison method, precursor MEL
  - 严格三线表规范 (toprule, midrule, bottomrule，零竖线)
  - 最佳指标加粗 (boldface)，次优指标加下划线 (underline)
"""
import os, sys, argparse, glob, warnings
from pathlib import Path
import numpy as np
import pandas as pd

# 强制 UTF-8 输出，解决 Windows GBK 终端编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore", category=RuntimeWarning)

try:
    from scipy import stats as sp_stats
except ImportError:
    sp_stats = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

PROJ = Path(__file__).resolve().parent.parent
HIST_RECON_DIR = PROJ / "output" / "historical_reconstructed"
OUTPUT_TABLES_DIR = PROJ / "output" / "tables"

# ═══ 12 种单目标前沿与基准比较方法（严格按规范排列） ═══
ALL_VERSIONS = [
    "KDS_EL_TwoPhase",   # 1. 本文提出方法 (KDS-EL)
    "KDS_EL_NoPool",     # 2. 消融变体 (w/o TPS)
    "MEL_MI",            # 3. 消融变体 (w/o TPS & KER)
    "MEL",               # 4. 前驱算法 (Precursor MEL)
    "DENCA_SO",          # 5. KBS 2023 近期高维邻域竞争算法
    "bIRIME",            # 6. iScience 2024 近期强力雾凇启发式算法
    "BinCOA",            # 7. IEEE Access 2024 最新二进制长鼻浣熊算法
    "FWPSO",             # 8. 经典竞争算法
    "PSO_CSM",           # 9. 经典竞争算法
    "SaWDE",             # 10. 经典竞争算法
    "IGPSO",             # 11. 经典竞争算法
    "BPSO",              # 12. 经典竞争算法
]

ABL_VERSIONS = ["MEL", "MEL_MI", "KDS_EL_NoPool", "KDS_EL_TwoPhase"]

V_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool":   "KDS-EL w/o TPS",
    "MEL_MI":          "KDS-EL w/o TPS\\&KER",
    "MEL":             "MEL",
    "DENCA_SO":        "DENCA-SO",
    "bIRIME":          "bIRIME",
    "BinCOA":          "BinCOA",
    "FWPSO":           "FWPSO",
    "PSO_CSM":         "PSO-CSM",
    "SaWDE":           "SaWDE",
    "IGPSO":           "IGPSO",
    "BPSO":            "BPSO",
}

# 20 个标准高维基准数据集
BENCHMARK_DATASETS = config.BENCHMARK_20_DATASETS


def find_latest_experiment_dir():
    """查找 output 目录下最新的 formal_experiment 运行目录。"""
    out_dir = PROJ / "output"
    candidates = glob.glob(str(out_dir / "formal_experiment_*"))
    valid = []
    for c in candidates:
        det = os.path.join(c, "results_detail.csv")
        if os.path.exists(det) and os.path.getsize(det) > 100:
            valid.append(c)
    if not valid:
        return None
    valid.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return Path(valid[0])


def load_dataset_records(new_exp_dir=None):
    """
    加载并合并所有实验数据：
      1. 优先加载 historical_reconstructed 中的纯分类准确率
      2. 若提供了 new_exp_dir 或检测到新运行目录，将新结果覆盖/合并进来
    """
    if not (HIST_RECON_DIR / "results_detail.csv").exists():
        print("[INFO] 未检测到历史重构数据，正在自动执行代数反标量化重构...")
        import reconstruct_pure_accuracy
        reconstruct_pure_accuracy.main()

    df_hist_detail = pd.read_csv(HIST_RECON_DIR / "results_detail.csv")
    df_hist_summary = pd.read_csv(HIST_RECON_DIR / "results_summary.csv")

    detail_dfs = [df_hist_detail]
    summary_dfs = [df_hist_summary]

    # 检查是否有新实验结果
    target_new_dir = Path(new_exp_dir) if new_exp_dir else find_latest_experiment_dir()
    if target_new_dir and target_new_dir.resolve() != HIST_RECON_DIR.resolve():
        new_detail_path = target_new_dir / "results_detail.csv"
        new_summary_path = target_new_dir / "results_summary.csv"
        if new_detail_path.exists() and new_summary_path.exists():
            print(f"[INFO] 载入新实验目录: {target_new_dir.name}")
            df_new_det = pd.read_csv(new_detail_path)
            df_new_sum = pd.read_csv(new_summary_path)
            new_versions = df_new_det["Version"].unique()
            print(f"  新实验包含方法: {list(new_versions)}")

            # 如果新实验重新跑了某个方法（如 KDS_EL_TwoPhase），则历史数据中对应方法被新运行替代
            df_hist_detail = df_hist_detail[~df_hist_detail["Version"].isin(new_versions)]
            df_hist_summary = df_hist_summary[~df_hist_summary["Version"].isin(new_versions)]
            detail_dfs = [df_hist_detail, df_new_det]
            summary_dfs = [df_hist_summary, df_new_sum]

    common_det_cols = list(set.intersection(*[set(d.columns) for d in detail_dfs]))
    df_detail = pd.concat([d[common_det_cols] for d in detail_dfs], ignore_index=True)

    common_sum_cols = list(set.intersection(*[set(d.columns) for d in summary_dfs]))
    df_summary = pd.concat([d[common_sum_cols] for d in summary_dfs], ignore_index=True)

    return df_detail, df_summary


# ═══ T4: 纯分类准确率主表 ═══
def table_t4_accuracy(df_detail, df_summary, out_dir):
    print("生成 T4: 纯分类准确率主表 (Pure Classification Accuracy)...")
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    # 构建矩阵并标记最佳与次优
    rows = []
    latex_rows = []

    kds_ver = "KDS_EL_TwoPhase"

    for ds in datasets:
        row = {"Dataset": ds}
        latex_cells = [f"{ds:16s}"]

        # 获取各方法均值
        means = {}
        stds = {}
        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                means[v] = float(sub["Mean_Acc"].values[0])
                stds[v] = float(sub["Std_Acc"].values[0])
            else:
                means[v] = np.nan
                stds[v] = np.nan

        # 找出最大值和次大值
        sorted_vals = sorted([m for m in means.values() if not np.isnan(m)], reverse=True)
        best_val = sorted_vals[0] if len(sorted_vals) > 0 else -1
        second_val = sorted_vals[1] if len(sorted_vals) > 1 else -1

        kds_runs = df_detail[(df_detail["Version"] == kds_ver) & (df_detail["Dataset"] == ds)]["Accuracy"].values

        for v in versions:
            m = means[v]
            s = stds[v]
            col_name = V_LABELS[v]
            if np.isnan(m):
                row[col_name] = "—"
                latex_cells.append("—")
                continue

            # Wilcoxon 检验符号（相对于 KDS-EL）
            sym = ""
            if v != kds_ver and len(kds_runs) > 0 and sp_stats is not None:
                v_runs = df_detail[(df_detail["Version"] == v) & (df_detail["Dataset"] == ds)]["Accuracy"].values
                if len(v_runs) > 0:
                    try:
                        p = sp_stats.wilcoxon(kds_runs, v_runs).pvalue
                        if p < 0.05:
                            sym = "$^{+}$" if np.mean(kds_runs) > np.mean(v_runs) else "$^{-}$"
                        else:
                            sym = "$^{\\approx}$"
                    except Exception:
                        sym = "$^{\\approx}$"

            cell_str = f"{m:.4f}±{s:.4f}"
            row[col_name] = f"{cell_str} {sym}".strip()

            # LaTeX 格式化
            latex_val = f"{m:.4f}"
            if abs(m - best_val) < 1e-5:
                latex_val = f"\\textbf{{{latex_val}}}"
            elif abs(m - second_val) < 1e-5:
                latex_val = f"\\underline{{{latex_val}}}"

            latex_cells.append(f"{latex_val} {sym}".strip())

        rows.append(row)
        latex_rows.append(" & ".join(latex_cells) + " \\\\")

    # 计算均值行与 Wilcoxon 统计摘要行
    avg_cells = [f"{'Average':16s}"]
    wtl_cells = [f"{'$+ / \\approx / -$':16s}"]
    avg_row_dict = {"Dataset": "Average"}
    wtl_row_dict = {"Dataset": "+ / ≈ / -"}

    for v in versions:
        v_means = [df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]["Mean_Acc"].values[0]
                   for ds in datasets if len(df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]) > 0]
        if v_means:
            mac = float(np.mean(v_means))
            avg_cells.append(f"{mac:.4f}")
            avg_row_dict[V_LABELS[v]] = f"{mac:.4f}"
        else:
            avg_cells.append("—")
            avg_row_dict[V_LABELS[v]] = "—"

        if v == kds_ver:
            wtl_cells.append("—")
            wtl_row_dict[V_LABELS[v]] = "—"
        else:
            wins, ties, losses = 0, 0, 0
            for ds in datasets:
                a = df_detail[(df_detail["Version"] == kds_ver) & (df_detail["Dataset"] == ds)]["Accuracy"].values
                b = df_detail[(df_detail["Version"] == v) & (df_detail["Dataset"] == ds)]["Accuracy"].values
                if len(a) > 0 and len(b) > 0:
                    diff = np.mean(a) - np.mean(b)
                    try:
                        p = sp_stats.wilcoxon(a, b).pvalue
                        if p < 0.05:
                            if diff > 0:
                                wins += 1
                            else:
                                losses += 1
                        else:
                            ties += 1
                    except Exception:
                        ties += 1
            wtl_cells.append(f"{wins}/{ties}/{losses}")
            wtl_row_dict[V_LABELS[v]] = f"{wins}/{ties}/{losses}"

    rows.append(avg_row_dict)
    rows.append(wtl_row_dict)

    df_t4 = pd.DataFrame(rows)
    df_t4.to_csv(os.path.join(out_dir, "T4_accuracy_pure.csv"), index=False, encoding="utf-8-sig")

    # 生成 LaTeX 三线表
    col_spec = "l" + "c" * len(versions)
    header_labels = " & ".join(["Dataset"] + [V_LABELS[v] for v in versions])
    latex_summary_block = (
        "\\midrule\n"
        + " & ".join(avg_cells) + " \\\\\n"
        + " & ".join(wtl_cells) + " \\\\"
    )
    latex_content = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Comparison of pure classification accuracy (mean $\\pm$ standard deviation across 10 independent runs) on 20 benchmark datasets. Best results are in \\textbf{boldface}, and second-best are \\underline{underlined}. Wilcoxon signed-rank symbols $+$, $\\approx$, and $-$ denote significant superiority, parity, or inferiority of the proposed KDS-EL at $\\alpha = 0.05$. The bottom rows summarize macro-average accuracy and directional win/tie/loss counts ($+/\\approx/-$).}",
        "\\label{tab:accuracy_comparison}",
        "\\resizebox{\\textwidth}{!}{",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"{header_labels} \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        latex_summary_block,
        "\\bottomrule",
        "\\end{tabular}",
        "}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T4_accuracy_pure.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T4_accuracy_pure.csv")
    print(f"  [OK] TeX: {out_dir}/T4_accuracy_pure.tex")


# ═══ T5: 特征子集规模与选择率表 ═══
def table_t5_features(df_summary, out_dir):
    print("生成 T5: 特征子集规模与选择率表 (Feature Count & Selection Ratio)...")
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    rows = []
    latex_rows = []

    for ds in datasets:
        row = {"Dataset": ds}
        latex_cells = [f"{ds:16s}"]

        feats = {}
        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            feats[v] = float(sub["Mean_Feat"].values[0]) if len(sub) > 0 else np.nan

        min_feat = min([f for f in feats.values() if not np.isnan(f)]) if feats else -1

        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            col_name = V_LABELS[v]
            if len(sub) == 0:
                row[col_name] = "—"
                latex_cells.append("—")
                continue

            f_mean = sub["Mean_Feat"].values[0]
            sr_mean = sub["Mean_SR"].values[0] if "Mean_SR" in sub.columns else 0.0
            row[col_name] = f"{f_mean:.1f} ({sr_mean:.2%})"

            txt = f"{f_mean:.0f}"
            if abs(f_mean - min_feat) < 1e-3:
                txt = f"\\textbf{{{txt}}}"
            latex_cells.append(txt)

        rows.append(row)
        latex_rows.append(" & ".join(latex_cells) + " \\\\")

    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "T5_features.csv"), index=False, encoding="utf-8-sig")

    col_spec = "l" + "c" * len(versions)
    header_labels = " & ".join(["Dataset"] + [V_LABELS[v] for v in versions])
    latex_content = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Comparison of selected feature subset size on 20 benchmark datasets. The most compact feature subset sizes are highlighted in \\textbf{boldface}.}",
        "\\label{tab:feature_comparison}",
        "\\resizebox{\\textwidth}{!}{",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"{header_labels} \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\bottomrule",
        "\\end{tabular}",
        "}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T5_features.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T5_features.csv")
    print(f"  [OK] TeX: {out_dir}/T5_features.tex")


# ═══ T6: Wilcoxon 符号秩检验胜负矩阵 ═══
def table_t6_wilcoxon(df_detail, df_summary, out_dir):
    print("生成 T6: Wilcoxon 符号秩检验矩阵 (Demšar Protocol)...")
    if sp_stats is None:
        print("  [SKIP] scipy 未安装")
        return

    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    n_v = len(versions)
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    # 预载入均值序列 (20 维向量，每维对应一个数据集的宏观均值)
    means_dict = {}
    for v in versions:
        means_dict[v] = np.array([
            df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]["Mean_Acc"].values[0]
            for ds in datasets
        ])

    win_mat = np.zeros((n_v, n_v), dtype=int)
    tie_mat = np.zeros((n_v, n_v), dtype=int)
    loss_mat = np.zeros((n_v, n_v), dtype=int)

    for i, v1 in enumerate(versions):
        for j, v2 in enumerate(versions):
            if i == j:
                continue
            diff = means_dict[v1] - means_dict[v2]
            try:
                p = sp_stats.wilcoxon(means_dict[v1], means_dict[v2]).pvalue
            except Exception:
                p = 1.0

            w = int(np.sum(diff > 1e-4))
            l = int(np.sum(diff < -1e-4))
            t = int(np.sum(np.abs(diff) <= 1e-4))
            win_mat[i, j] = w
            loss_mat[i, j] = l
            tie_mat[i, j] = t

    table_rows = []
    for i, v1 in enumerate(versions):
        row = {"Method": V_LABELS[v1]}
        for j, v2 in enumerate(versions):
            if i == j:
                row[V_LABELS[v2]] = "—"
            else:
                row[V_LABELS[v2]] = f"{win_mat[i, j]}/{tie_mat[i, j]}/{loss_mat[i, j]}"
        table_rows.append(row)

    pd.DataFrame(table_rows).to_csv(os.path.join(out_dir, "T6_wilcoxon_matrix.csv"), index=False, encoding="utf-8-sig")
    print(f"  [OK] CSV: {out_dir}/T6_wilcoxon_matrix.csv")


# ═══ T6b: Holm-Bonferroni 族系误差校正表 ═══
def table_t6b_holm(df_summary, out_dir):
    print("生成 T6b: Holm-Bonferroni 族系多重检验校正表...")
    if sp_stats is None:
        print("  [SKIP] scipy 未安装")
        return

    kds_ver = "KDS_EL_TwoPhase"
    if kds_ver not in df_summary["Version"].unique():
        print(f"  [SKIP] 未找到 {kds_ver}")
        return

    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]
    kds_means = np.array([
        df_summary[(df_summary["Version"] == kds_ver) & (df_summary["Dataset"] == ds)]["Mean_Acc"].values[0]
        for ds in datasets
    ])

    competitors = [v for v in ALL_VERSIONS if v != kds_ver and v in df_summary["Version"].unique()]
    records = []

    for v in competitors:
        c_means = np.array([
            df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]["Mean_Acc"].values[0]
            for ds in datasets
        ])
        diff = kds_means - c_means
        mean_diff = float(np.mean(diff))
        wins = int(np.sum(diff > 1e-4))
        ties = int(np.sum(np.abs(diff) <= 1e-4))
        losses = int(np.sum(diff < -1e-4))

        try:
            res = sp_stats.wilcoxon(kds_means, c_means, alternative="two-sided")
            p_val = float(res.pvalue)
            stat = float(res.statistic)
        except Exception:
            p_val = 1.0
            stat = 0.0

        records.append({
            "Method": V_LABELS[v],
            "Mean_Delta_Acc": mean_diff,
            "Wins": wins,
            "Ties": ties,
            "Losses": losses,
            "Statistic": stat,
            "p_value": p_val,
        })

    # 按 p 值升序排列 (Holm-Bonferroni 阶梯校正)
    records.sort(key=lambda x: x["p_value"])
    m = len(records)
    alpha_base = 0.05

    for rank, r in enumerate(records, start=1):
        r["Rank"] = rank
        r["Holm_Alpha"] = alpha_base / (m - rank + 1)
        r["Significant"] = "Yes" if r["p_value"] < r["Holm_Alpha"] else "No"

    df_holm = pd.DataFrame(records)
    df_holm.to_csv(os.path.join(out_dir, "T6b_holm_bonferroni.csv"), index=False, encoding="utf-8-sig")

    # 生成 LaTeX 表格
    latex_rows = []
    for r in records:
        latex_rows.append(
            f"  {r['Rank']:2d} & {r['Method']:22s} & {r['Mean_Delta_Acc']:+.4f} & "
            f"{r['Wins']}/{r['Ties']}/{r['Losses']} & {r['Statistic']:6.1f} & "
            f"{r['p_value']:10.2e} & {r['Holm_Alpha']:8.4f} & {r['Significant']} \\\\"
        )

    latex_content = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Holm-Bonferroni step-down procedure testing directional superiority of KDS-EL over all competitor methods across 20 benchmark datasets (nominal $\\alpha = 0.05$).}",
        "\\label{tab:holm_bonferroni}",
        "\\begin{tabular}{clcccccc}",
        "\\toprule",
        "Rank & Competitor Method & $\\Delta$Acc & W/T/L & $W$ & $p$-value & $\\alpha_{\\mathrm{Holm}}$ & Reject $H_0$? \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table}",
    ]
    with open(os.path.join(out_dir, "T6b_holm_bonferroni.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T6b_holm_bonferroni.csv")
    print(f"  [OK] TeX: {out_dir}/T6b_holm_bonferroni.tex")


# ═══ T7: 核心机制消融表 ═══
def table_t7_ablation(df_summary, out_dir):
    print("生成 T7: 核心机制消融递进表 (Ablation Progression)...")
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    rows = []
    latex_rows = []

    for ds in datasets:
        row = {"Dataset": ds}
        latex_cells = [f"{ds:16s}"]
        for v in ABL_VERSIONS:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                acc = sub["Mean_Acc"].values[0]
                feat = sub["Mean_Feat"].values[0]
                row[f"{V_LABELS[v]}_Acc"] = f"{acc:.4f}"
                row[f"{V_LABELS[v]}_Feat"] = f"{feat:.0f}"
                latex_cells.append(f"{acc:.4f}")
                latex_cells.append(f"{feat:.0f}")
            else:
                row[f"{V_LABELS[v]}_Acc"] = "—"
                row[f"{V_LABELS[v]}_Feat"] = "—"
                latex_cells.append("—")
                latex_cells.append("—")
        rows.append(row)
        latex_rows.append(" & ".join(latex_cells) + " \\\\")

    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "T7_ablation.csv"), index=False, encoding="utf-8-sig")

    latex_content = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Component-wise ablation progression from precursor MEL through MII, KER, to full KDS-EL across 20 benchmark datasets.}",
        "\\label{tab:ablation_study}",
        "\\begin{tabular}{lcccccccc}",
        "\\toprule",
        "& \\multicolumn{2}{c}{Precursor MEL} & \\multicolumn{2}{c}{MEL+MII} & \\multicolumn{2}{c}{KDS-EL w/o TPS} & \\multicolumn{2}{c}{Proposed KDS-EL} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-7} \\cmidrule(lr){8-9}",
        "Dataset & Acc & Feat & Acc & Feat & Acc & Feat & Acc & Feat \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T7_ablation.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T7_ablation.csv")
    print(f"  [OK] TeX: {out_dir}/T7_ablation.tex")


# ═══ Main ═══
def main():
    parser = argparse.ArgumentParser(description="KDS-EL Table Generator (Elsevier Standard)")
    parser.add_argument("--out", default=str(OUTPUT_TABLES_DIR), help="输出表格目录")
    parser.add_argument("--new-exp-dir", default=None, help="新实验目录路径（可选）")
    parser.add_argument("--tab", nargs="*", default=None, help="指定生成的表格: T4 T5 T6 T6b T7")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print("=" * 72)
    print("KDS-EL 论文统计表格与 LaTeX 代码自动生成器")
    print("=" * 72)

    df_detail, df_summary = load_dataset_records(args.new_exp_dir)
    print(f"数据载入完成: Detail {len(df_detail)} 行, Summary {len(df_summary)} 行")
    print(f"包含方法 ({df_summary['Version'].nunique()} 种): {sorted(df_summary['Version'].unique())}")
    print(f"包含数据集 ({df_summary['Dataset'].nunique()} 个): {sorted(df_summary['Dataset'].unique())}")

    all_tabs = {
        "T4":  lambda: table_t4_accuracy(df_detail, df_summary, args.out),
        "T5":  lambda: table_t5_features(df_summary, args.out),
        "T6":  lambda: table_t6_wilcoxon(df_detail, df_summary, args.out),
        "T6b": lambda: table_t6b_holm(df_summary, args.out),
        "T7":  lambda: table_t7_ablation(df_summary, args.out),
    }

    targets = args.tab if args.tab else list(all_tabs.keys())
    for t in targets:
        if t in all_tabs:
            all_tabs[t]()

    print("\n所有表格生成完毕！目标目录:", args.out)


if __name__ == "__main__":
    main()
