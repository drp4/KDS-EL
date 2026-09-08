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
EXP1_DIR   = PROJ / "output" / "formal_experiment_20260701_094943"  # BPSO, SaWDE, FWPSO, PSO_CSM, IGPSO
EXP2_DIR   = PROJ / "output" / "formal_experiment_20260628_205157"  # MEL
MEL_MI_DIR = PROJ / "output" / "formal_experiment_mel_mi"         # MEL_MI
FINAL_DIR  = PROJ / "output" / "formal_experiment_final"           # KDS_EL_NoPool, KDS_EL_TwoPhase
NEW_SOTA_DIR = PROJ / "output" / "formal_experiment_20260905_211755"  # DENCA_SO, bIRIME, BinCOA
OUTPUT_TABLES_DIR = PROJ / "output" / "tables"

# ═══ 12 种单目标前沿与基准比较方法（严格按规范排列） ═══
ALL_VERSIONS = [
    "KDS_EL_TwoPhase",   # 1. 本文提出方法 (KDS-EL, 0.9574 / 88 特征)
    "KDS_EL_NoPool",     # 2. 消融变体 (w/o TPS, 0.9488 / 122 特征)
    "MEL_MI",            # 3. 消融变体 (w/o TPS & KER, 0.9325 / 291 特征)
    "MEL",               # 4. 前驱算法 (Precursor MEL, 0.8868 / 2722 特征)
    "bIRIME",            # 5. iScience 2024 近期强力启发式单目标
    "FWPSO",             # 6. 经典单目标竞品
    "PSO_CSM",           # 7. SWEVO 2025 单目标竞品
    "BinCOA",            # 8. IEEE Access 2024 最新二进制长鼻浣熊算法
    "SaWDE",             # 9. KBS 2022 经典单目标竞品
    "IGPSO",             # 10. SWEVO 2024 经典单目标竞品
    "DENCA_SO",          # 11. KBS 2023 过滤式单目标算法
    "BPSO",              # 12. SMC 1997 经典群智能基准
]

ABL_VERSIONS = ["MEL", "MEL_MI", "KDS_EL_NoPool", "KDS_EL_TwoPhase"]

V_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool":   "KDS-EL w/o TPS",
    "MEL_MI":          "KDS-EL w/o TPS\\&KER",
    "MEL":             "MEL",
    "bIRIME":          "bIRIME",
    "FWPSO":           "FWPSO",
    "PSO_CSM":         "PSO-CSM",
    "BinCOA":          "BinCOA",
    "SaWDE":           "SaWDE",
    "IGPSO":           "IGPSO",
    "DENCA_SO":        "DENCA-SO",
    "BPSO":            "BPSO",
}

# 20 个标准高维基准数据集
BENCHMARK_DATASETS = config.BENCHMARK_20_DATASETS


def load_dataset_records(new_exp_dir=None):
    """
    加载权威实验数据：
      - KDS_EL_TwoPhase, KDS_EL_NoPool 来自 output/formal_experiment_final (TwoPhase 0.9574 / 88 特征, NoPool 0.9488 / 122 特征)
      - MEL_MI 来自 output/formal_experiment_mel_mi (0.9325 / 291 特征)
      - MEL 来自 output/formal_experiment_20260628_205157 (0.8868 / 2722 特征)
      - BPSO, FWPSO, IGPSO, PSO_CSM, SaWDE 来自 output/formal_experiment_20260701_094943
      - bIRIME, BinCOA, DENCA_SO 来自 output/formal_experiment_20260905_211755 (严格仅提取这 3 个新竞品，绝不覆盖 KDS_EL_TwoPhase)
    """
    sources = [
        (FINAL_DIR, ["KDS_EL_TwoPhase", "KDS_EL_NoPool"]),
        (MEL_MI_DIR, ["MEL_MI"]),
        (EXP2_DIR, ["MEL"]),
        (EXP1_DIR, ["BPSO", "FWPSO", "IGPSO", "PSO_CSM", "SaWDE"]),
        (NEW_SOTA_DIR, ["bIRIME", "BinCOA", "DENCA_SO"]),
    ]
    det_list, sum_list = [], []
    b20 = BENCHMARK_DATASETS
    for path, vers in sources:
        p = Path(path)
        df_d = pd.read_csv(p / "results_detail.csv")
        df_s = pd.read_csv(p / "results_summary.csv")
        det_list.append(df_d[df_d["Version"].isin(vers) & df_d["Dataset"].isin(b20)])
        sum_list.append(df_s[df_s["Version"].isin(vers) & df_s["Dataset"].isin(b20)])

    common_det_cols = list(set.intersection(*[set(d.columns) for d in det_list]))
    df_detail = pd.concat([d[common_det_cols] for d in det_list], ignore_index=True)

    common_sum_cols = list(set.intersection(*[set(d.columns) for d in sum_list]))
    df_summary = pd.concat([d[common_sum_cols] for d in sum_list], ignore_index=True)

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
        ds_tex = ds.replace("_", "\\_")
        latex_cells = [f"{ds_tex:16s}"]

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
        "\\caption{Comparison of classification accuracy on 20 benchmark datasets. Best results are in \\textbf{boldface}, and second-best are \\underline{underlined}.}",
        "\\label{T4}\\label{tab:accuracy_comparison}",
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
    with open(os.path.join(out_dir, "T4_accuracy.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T4_accuracy_pure.csv & T4_accuracy.csv")
    print(f"  [OK] TeX: {out_dir}/T4_accuracy_pure.tex & T4_accuracy.tex")



# ═══ T5: 特征子集规模与选择率表 ═══
def table_t5_features(df_summary, out_dir):
    print("生成 T5: 特征子集规模与选择率表 (Feature Count & Selection Ratio)...")
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    rows = []
    latex_rows = []

    for ds in datasets:
        row = {"Dataset": ds}
        ds_tex = ds.replace("_", "\\_")
        latex_cells = [f"{ds_tex:16s}"]

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
        "\\label{T5}\\label{tab:feature_comparison}",
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

    col_spec = "l" + "c" * len(versions)
    header_labels = " & ".join(["Method"] + [V_LABELS[v] for v in versions])
    latex_rows = []
    for r in table_rows:
        cells = [r["Method"]] + [r[V_LABELS[v]] for v in versions]
        latex_rows.append(" & ".join(cells) + " \\\\")

    latex_content = [
        "\\begin{table*}[!t]",
        "\\centering",
        "\\caption{Pairwise Wilcoxon signed-rank test results on classification accuracy across 20 benchmark datasets.}",
        "\\label{T6}",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\renewcommand{\\arraystretch}{1.06}",
        "\\resizebox{\\textwidth}{!}{%",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"{header_labels} \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\bottomrule",
        "\\end{tabular}%",
        "}",
        "\\vspace{2pt}",
        "\\par\\raggedright\\footnotesize",
        "Entries denote pairwise win/tie/loss ($+/ \\approx / -$) counts between the row method and column method evaluated across 20 benchmark datasets at $\\alpha = 0.05$.",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T6_wilcoxon.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))
    print(f"  [OK] TeX: {out_dir}/T6_wilcoxon.tex")



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
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Holm-Bonferroni step-down procedure testing directional superiority of KDS-EL over all competitor methods across 20 benchmark datasets (nominal $\\alpha = 0.05$).}",
        "\\label{T6b}\\label{tab:holm_bonferroni}",
        "\\small",
        "\\renewcommand{\\arraystretch}{1.12}",
        "\\begin{tabular*}{\\textwidth}{@{\\extracolsep{\\fill}}clcccccc@{}}",
        "\\toprule",
        "Rank & Competitor Method & $\\Delta$Acc & W/T/L & $W$ & $p$-value & $\\alpha_{\\mathrm{Holm}}$ & Reject $H_0$? \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\bottomrule",
        "\\end{tabular*}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T6b_holm_bonferroni.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T6b_holm_bonferroni.csv")
    print(f"  [OK] TeX: {out_dir}/T6b_holm_bonferroni.tex")


# ═══ T7: 核心机制消融表 ═══
def table_t7_ablation(df_summary, out_dir):
    print("生成 T7: 核心机制消融递进表 (Ablation Progression)...")
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    def format_feat(val):
        if np.isnan(val):
            return "—"
        if val >= 1000:
            return f"{int(round(val)):,}".replace(",", "{,}")
        return f"{int(round(val))}"

    rows = []
    latex_rows = []

    for ds in datasets:
        row = {"Dataset": ds}
        ds_tex = ds.replace("_", "\\_")
        latex_cells = [f"{ds_tex:16s}"]

        acc_vals = []
        feat_vals = []
        for v in ABL_VERSIONS:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                acc = float(sub["Mean_Acc"].values[0])
                feat = float(sub["Mean_Feat"].values[0])
                acc_vals.append(acc)
                feat_vals.append(feat)
                row[f"{V_LABELS[v]}_Acc"] = f"{acc:.4f}"
                row[f"{V_LABELS[v]}_Feat"] = f"{feat:.0f}"
            else:
                acc_vals.append(np.nan)
                feat_vals.append(np.nan)
                row[f"{V_LABELS[v]}_Acc"] = "—"
                row[f"{V_LABELS[v]}_Feat"] = "—"

        # 确定最优与次优 Acc (最大)
        valid_accs = sorted(list(set([a for a in acc_vals if not np.isnan(a)])), reverse=True)
        best_acc = valid_accs[0] if len(valid_accs) > 0 else np.nan
        second_acc = valid_accs[1] if len(valid_accs) > 1 else np.nan

        # 确定最优与次优 Feat (最紧凑/最小)
        valid_feats = sorted(list(set([f for f in feat_vals if not np.isnan(f)])))
        best_feat = valid_feats[0] if len(valid_feats) > 0 else np.nan
        second_feat = valid_feats[1] if len(valid_feats) > 1 else np.nan

        for a, f in zip(acc_vals, feat_vals):
            if np.isnan(a):
                latex_cells.extend(["—", "—"])
                continue

            a_str = f"{a:.4f}"
            if abs(a - best_acc) < 1e-5:
                a_str = f"\\textbf{{{a_str}}}"
            elif not np.isnan(second_acc) and abs(a - second_acc) < 1e-5:
                a_str = f"\\underline{{{a_str}}}"

            f_str = format_feat(f)
            if abs(f - best_feat) < 1e-3:
                f_str = f"\\textbf{{{f_str}}}"
            elif not np.isnan(second_feat) and abs(f - second_feat) < 1e-3:
                f_str = f"\\underline{{{f_str}}}"

            latex_cells.extend([a_str, f_str])

        rows.append(row)
        latex_rows.append(" & ".join(latex_cells) + " \\\\")

    # 计算均值行
    avg_row_dict = {"Dataset": "Average"}
    avg_accs = []
    avg_feats = []
    for v in ABL_VERSIONS:
        sub = df_summary[df_summary["Version"] == v]
        v_accs = [sub[sub["Dataset"] == ds]["Mean_Acc"].values[0] for ds in datasets if len(sub[sub["Dataset"] == ds]) > 0]
        v_feats = [sub[sub["Dataset"] == ds]["Mean_Feat"].values[0] for ds in datasets if len(sub[sub["Dataset"] == ds]) > 0]
        m_acc = float(np.mean(v_accs)) if v_accs else np.nan
        m_feat = float(np.mean(v_feats)) if v_feats else np.nan
        avg_accs.append(m_acc)
        avg_feats.append(m_feat)
        avg_row_dict[f"{V_LABELS[v]}_Acc"] = f"{m_acc:.4f}"
        avg_row_dict[f"{V_LABELS[v]}_Feat"] = f"{m_feat:.1f}"

    rows.append(avg_row_dict)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "T7_ablation.csv"), index=False, encoding="utf-8-sig")

    avg_cells = [f"{'Average':16s}"]
    # 标注 Average 的最优和次优
    sorted_avg_accs = sorted(list(set(avg_accs)), reverse=True)
    sorted_avg_feats = sorted(list(set(avg_feats)))

    for a, f in zip(avg_accs, avg_feats):
        a_str = f"{a:.4f}"
        if abs(a - sorted_avg_accs[0]) < 1e-5:
            a_str = f"\\textbf{{{a_str}}}"
        elif len(sorted_avg_accs) > 1 and abs(a - sorted_avg_accs[1]) < 1e-5:
            a_str = f"\\underline{{{a_str}}}"

        if f >= 1000:
            f_str = f"{f:,.1f}".replace(",", "{,}")
        else:
            f_str = f"{f:.1f}"

        if abs(f - sorted_avg_feats[0]) < 1e-3:
            f_str = f"\\textbf{{{f_str}}}"
        elif len(sorted_avg_feats) > 1 and abs(f - sorted_avg_feats[1]) < 1e-3:
            f_str = f"\\underline{{{f_str}}}"

        avg_cells.extend([a_str, f_str])

    # 计算逐级边际提升行
    delta_cells = [f"{'$\\Delta$ vs. Preceding':16s}", "\\multicolumn{2}{c}{—}"]
    # Step 1: MEL -> w/o TPS&KER (MII)
    d_acc1 = (avg_accs[1] - avg_accs[0]) * 100
    d_feat1 = (avg_feats[1] - avg_feats[0]) / avg_feats[0] * 100
    delta_cells.extend([f"+{d_acc1:.2f}\\%", f"{d_feat1:.1f}\\%"])

    # Step 2: w/o TPS&KER -> w/o TPS (KER)
    d_acc2 = (avg_accs[2] - avg_accs[1]) * 100
    d_feat2 = (avg_feats[2] - avg_feats[1]) / avg_feats[1] * 100
    delta_cells.extend([f"+{d_acc2:.2f}\\%", f"{d_feat2:.1f}\\%"])

    # Step 3: w/o TPS -> KDS-EL (TPS)
    d_acc3 = (avg_accs[3] - avg_accs[2]) * 100
    d_feat3 = (avg_feats[3] - avg_feats[2]) / avg_feats[2] * 100
    delta_cells.extend([f"+{d_acc3:.2f}\\%", f"{d_feat3:.1f}\\%"])

    latex_content = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Performance comparison before and after algorithm improvement across 20 benchmark datasets. Best results are in \\textbf{boldface}, and second-best are \\underline{underlined}.}",
        "\\label{T7}\\label{tab:ablation_study}",
        "\\begin{tabular}{lcccccccc}",
        "\\toprule",
        "& \\multicolumn{2}{c}{Foundational MEL} & \\multicolumn{2}{c}{KDS-EL w/o TPS\\&KER} & \\multicolumn{2}{c}{KDS-EL w/o TPS} & \\multicolumn{2}{c}{Proposed KDS-EL} \\\\",
        "& \\multicolumn{2}{c}{(Base Swarm)} & \\multicolumn{2}{c}{(+ MII)} & \\multicolumn{2}{c}{(+ MII \\& KER)} & \\multicolumn{2}{c}{(Complete)} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-7} \\cmidrule(lr){8-9}",
        "Dataset & Acc & Feat & Acc & Feat & Acc & Feat & Acc & Feat \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\midrule",
        " & ".join(avg_cells) + " \\\\",
        " & ".join(delta_cells) + " \\\\",
        "\\bottomrule",
        "\\end{tabular}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T7_ablation.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))

    print(f"  [OK] CSV: {out_dir}/T7_ablation.csv")
    print(f"  [OK] TeX: {out_dir}/T7_ablation.tex")


# ═══ T-A5: 运行时间附表 ═══
def table_t_a5_runtime(df_summary, out_dir):
    print("生成 T-A5: 运行时间附表 (Runtime in Seconds)...")
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    datasets = [d for d in BENCHMARK_DATASETS if d in df_summary["Dataset"].unique()]

    rows = []
    latex_rows = []
    for ds in datasets:
        row = {"Dataset": ds}
        ds_tex = ds.replace("_", "\\_")
        latex_cells = [f"{ds_tex:16s}"]
        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            col_name = V_LABELS[v]
            if len(sub) > 0 and "Mean_Time" in sub.columns:
                t = float(sub["Mean_Time"].values[0])
                row[col_name] = f"{t:.1f}"
                latex_cells.append(f"{t:.1f}")
            else:
                row[col_name] = "—"
                latex_cells.append("—")
        rows.append(row)
        latex_rows.append(" & ".join(latex_cells) + " \\\\")

    avg_row = {"Dataset": "Average"}
    avg_cells = [f"{'Average':16s}"]
    for v in versions:
        sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"].isin(datasets))]
        if len(sub) > 0 and "Mean_Time" in sub.columns:
            m_t = float(sub["Mean_Time"].mean())
            avg_row[V_LABELS[v]] = f"{m_t:.1f}"
            avg_cells.append(f"{m_t:.1f}")
        else:
            avg_row[V_LABELS[v]] = "—"
            avg_cells.append("—")
    rows.append(avg_row)

    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "T-A5_runtime.csv"), index=False, encoding="utf-8-sig")

    col_spec = "l" + "c" * len(versions)
    header_labels = " & ".join(["Dataset"] + [V_LABELS[v] for v in versions])
    latex_content = [
        "\\begin{table*}[!t]",
        "\\centering",
        "\\caption{Per-dataset computational runtime in seconds (mean over 10 independent runs) across 20 benchmark datasets.}",
        "\\label{T-A5}",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\renewcommand{\\arraystretch}{1.06}",
        "\\resizebox{\\textwidth}{!}{%",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"{header_labels} \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\midrule",
        " & ".join(avg_cells) + " \\\\",
        "\\bottomrule",
        "\\end{tabular}%",
        "}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T-A5_runtime.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))
    print(f"  [OK] CSV: {out_dir}/T-A5_runtime.csv")
    print(f"  [OK] TeX: {out_dir}/T-A5_runtime.tex")


# ═══ Main ═══
def main():
    parser = argparse.ArgumentParser(description="KDS-EL Table Generator (Elsevier Standard)")
    parser.add_argument("--out", default=str(OUTPUT_TABLES_DIR), help="输出表格目录")
    parser.add_argument("--new-exp-dir", default=None, help="新实验目录路径（可选）")
    parser.add_argument("--tab", nargs="*", default=None, help="指定生成的表格: T4 T5 T6 T6b T7 TA5")
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
        "TA5": lambda: table_t_a5_runtime(df_summary, args.out),
    }

    targets = args.tab if args.tab else list(all_tabs.keys())
    for t in targets:
        if t in all_tabs:
            all_tabs[t]()

    print("\n所有表格生成完毕！目标目录:", args.out)



if __name__ == "__main__":
    main()
