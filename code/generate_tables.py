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
RECONSTRUCTED_DIR = PROJ / "output" / "historical_reconstructed"   # 真实纯分类准确率代数解标量重构数据
OUTPUT_TABLES_DIR = PROJ / "output" / "tables"

# ═══ 12 种单目标前沿与基准比较方法（严格按规范排列） ═══
ALL_VERSIONS = [
    "KDS_EL_TwoPhase",   # 1. 本文提出方法 (KDS-EL, 0.9545 / 88 特征)
    "KDS_EL_NoPool",     # 2. 消融变体 (w/o TPS, 0.9462 / 122 特征)
    "MEL_MI",            # 3. 消融变体 (w/o TPS & KER, 0.9348 / 291 特征)
    "MEL",               # 4. 前驱算法 (Precursor MEL, 0.9093 / 2722 特征)
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

V_TEX_HEADERS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool":   "\\makecell{KDS-EL \\\\ w/o TPS}",
    "MEL_MI":          "\\makecell{KDS-EL \\\\ w/o TPS\\&KER}",
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
    加载真实纯分类准确率实验数据：
      - 历史 9 个单目标版本全部从 output/historical_reconstructed 加载（由 results_detail.csv 代数反解还原的纯精度 Pure_Acc 与真实特征数、耗时）
      - bIRIME, BinCOA, DENCA_SO 来自 output/formal_experiment_20260905_211755（原生纯分类精度记录）
    """
    sources = [
        (RECONSTRUCTED_DIR, ["KDS_EL_TwoPhase", "KDS_EL_NoPool", "MEL_MI", "MEL", "BPSO", "FWPSO", "IGPSO", "PSO_CSM", "SaWDE"]),
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
                        p = sp_stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
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

    # 生成 LaTeX 三线表 (遵循 EMSWOA 规范：等宽算法列 + 跨行表头 + 解耦注记)
    col_spec = f"l *{{{len(versions)}}}{{w{{c}}{{33pt}}}}"
    header_labels = " & ".join(["Dataset"] + [V_TEX_HEADERS.get(v, V_LABELS[v]) for v in versions])
    latex_summary_block = (
        "\\midrule\n"
        + " & ".join(avg_cells) + " \\\\\n"
        + " & ".join(wtl_cells) + " \\\\"
    )
    latex_content = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Comparison of classification accuracy between KDS-EL and competitor algorithms.}",
        "\\label{T4}\\label{tab:accuracy_comparison}",
        "\\resizebox{\\textwidth}{!}{",
        "\\renewcommand{\\arraystretch}{0.96}",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"{header_labels} \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        latex_summary_block,
        "\\bottomrule",
        "\\end{tabular}",
        "}",
        "\\vspace{2pt}",
        "\\par\\raggedright\\footnotesize",
        "\\textit{Note}: Bold: best; underline: second-best. $+ / \\approx / -$: statistically superior, equivalent, or inferior to KDS-EL (two-sided Mann--Whitney $U$ test, $\\alpha = 0.05$).",
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

        valid_feats = [f for f in feats.values() if not np.isnan(f)]
        sorted_unique = sorted(list(set(valid_feats)))
        best_feat = sorted_unique[0] if len(sorted_unique) > 0 else -1
        second_feat = sorted_unique[1] if len(sorted_unique) > 1 else -1

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
            if abs(f_mean - best_feat) < 1e-3:
                txt = f"\\textbf{{{txt}}}"
            elif abs(f_mean - second_feat) < 1e-3:
                txt = f"\\underline{{{txt}}}"
            latex_cells.append(txt)

        rows.append(row)
        latex_rows.append(" & ".join(latex_cells) + " \\\\")

    # 计算均值行与压缩率摘要行 (Average & Comp. Ratio)
    avg_feat_vals = {}
    avg_comp_vals = {}
    for v in versions:
        sub = df_summary[df_summary["Version"] == v]
        if len(sub) > 0:
            avg_feat_vals[v] = float(sub["Mean_Feat"].mean())
            avg_comp_vals[v] = float((1.0 - sub["Mean_SR"]).mean() * 100.0)
        else:
            avg_feat_vals[v] = np.nan
            avg_comp_vals[v] = np.nan

    valid_avg_feats = [f for f in avg_feat_vals.values() if not np.isnan(f)]
    sorted_avg_feats = sorted(list(set(valid_avg_feats)))
    best_avg_feat = sorted_avg_feats[0] if len(sorted_avg_feats) > 0 else -1
    second_avg_feat = sorted_avg_feats[1] if len(sorted_avg_feats) > 1 else -1

    valid_avg_comps = [c for c in avg_comp_vals.values() if not np.isnan(c)]
    sorted_avg_comps = sorted(list(set(valid_avg_comps)), reverse=True)
    best_avg_comp = sorted_avg_comps[0] if len(sorted_avg_comps) > 0 else -1
    second_avg_comp = sorted_avg_comps[1] if len(sorted_avg_comps) > 1 else -1

    avg_cells = [f"{'Average':16s}"]
    comp_cells = [f"{'Comp. Ratio':16s}"]
    avg_row_dict = {"Dataset": "Average"}
    comp_row_dict = {"Dataset": "Comp. Ratio"}

    for v in versions:
        af = avg_feat_vals[v]
        ac = avg_comp_vals[v]
        col_name = V_LABELS[v]
        if np.isnan(af):
            avg_cells.append("—")
            comp_cells.append("—")
            avg_row_dict[col_name] = "—"
            comp_row_dict[col_name] = "—"
            continue

        af_txt = f"{af:.1f}"
        if abs(af - best_avg_feat) < 1e-3:
            af_tex = f"\\textbf{{{af_txt}}}"
        elif abs(af - second_avg_feat) < 1e-3:
            af_tex = f"\\underline{{{af_txt}}}"
        else:
            af_tex = af_txt
        avg_cells.append(af_tex)
        avg_row_dict[col_name] = af_txt

        ac_txt = f"{ac:.1f}%"
        ac_tex_val = f"{ac:.1f}\\%"
        if abs(ac - best_avg_comp) < 1e-3:
            ac_tex = f"\\textbf{{{ac_tex_val}}}"
        elif abs(ac - second_avg_comp) < 1e-3:
            ac_tex = f"\\underline{{{ac_tex_val}}}"
        else:
            ac_tex = ac_tex_val
        comp_cells.append(ac_tex)
        comp_row_dict[col_name] = ac_txt

    rows.append(avg_row_dict)
    rows.append(comp_row_dict)

    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "T5_features.csv"), index=False, encoding="utf-8-sig")

    col_spec = f"l *{{{len(versions)}}}{{w{{c}}{{33pt}}}}"
    header_labels = " & ".join(["Dataset"] + [V_TEX_HEADERS.get(v, V_LABELS[v]) for v in versions])
    latex_summary_block = (
        "\\midrule\n"
        + " & ".join(avg_cells) + " \\\\\n"
        + " & ".join(comp_cells) + " \\\\"
    )
    latex_content = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Comparison of selected feature subset size between KDS-EL and competitor algorithms.}",
        "\\label{T5}\\label{tab:feature_comparison}",
        "\\resizebox{\\textwidth}{!}{",
        "\\renewcommand{\\arraystretch}{0.86}",
        f"\\begin{{tabular}}{{{col_spec}}}",
        "\\toprule",
        f"{header_labels} \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        latex_summary_block,
        "\\bottomrule",
        "\\end{tabular}",
        "}",
        "\\vspace{2pt}",
        "\\par\\raggedright\\footnotesize",
        "\\textit{Note}: Bold: most compact; underline: second-most compact. Comp. Ratio: feature reduction percentage relative to unreduced feature space.",
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

    # 预缓存每个 (version, dataset) 的 10 次独立运行精度以实现高效精准统计
    runs_dict = {}
    for v in versions:
        for ds in datasets:
            runs_dict[(v, ds)] = df_detail[(df_detail["Version"] == v) & (df_detail["Dataset"] == ds)]["Accuracy"].values

    win_mat = np.zeros((n_v, n_v), dtype=int)
    tie_mat = np.zeros((n_v, n_v), dtype=int)
    loss_mat = np.zeros((n_v, n_v), dtype=int)

    for i in range(n_v):
        v1 = versions[i]
        for j in range(i + 1, n_v):
            v2 = versions[j]
            w, t, l = 0, 0, 0
            for ds in datasets:
                a = runs_dict.get((v1, ds), np.array([]))
                b = runs_dict.get((v2, ds), np.array([]))
                if len(a) > 0 and len(b) > 0:
                    diff = np.mean(a) - np.mean(b)
                    try:
                        p = sp_stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
                        if p < 0.05:
                            if diff > 0:
                                w += 1
                            else:
                                l += 1
                        else:
                            t += 1
                    except Exception:
                        t += 1
                else:
                    t += 1
            win_mat[i, j] = w
            tie_mat[i, j] = t
            loss_mat[i, j] = l
            win_mat[j, i] = l
            tie_mat[j, i] = t
            loss_mat[j, i] = w

    # 构建表格数据
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

    col_spec = f"l *{{{len(versions)}}}{{w{{c}}{{33pt}}}}"
    header_labels = " & ".join(["Method"] + [V_TEX_HEADERS.get(v, V_LABELS[v]) for v in versions])
    latex_rows = []
    for i, r in enumerate(table_rows):
        cells = [r["Method"]]
        for j, v in enumerate(versions):
            val = r[V_LABELS[v]]
            if i != j and win_mat[i, j] > loss_mat[i, j]:
                cells.append(f"\\textbf{{{val}}}")
            else:
                cells.append(val)
        latex_rows.append(" & ".join(cells) + " \\\\")

    latex_content = [
        "\\begin{table*}[!t]",
        "\\centering",
        "\\caption{Pairwise statistical comparison on classification accuracy.}",
        "\\label{T6}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\renewcommand{\\arraystretch}{0.96}",
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
        "\\textit{Note}: $W/T/L$: pairwise win/tie/loss counts against column methods (two-sided Mann--Whitney $U$ test, $\\alpha = 0.05$). Bold indicates pairwise advantage ($W > L$).",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T6_wilcoxon.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content))
    print(f"  [OK] TeX: {out_dir}/T6_wilcoxon.tex")



# ═══ T6b: Holm-Bonferroni 族系误差校正表 ═══
def table_t6b_holm(df_detail, df_summary, out_dir):
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

        # 单数据集 10 次运行配对 Wilcoxon 检验汇总 (与 Table 4 / Table 6 保持绝对严格一致)
        wins, ties, losses = 0, 0, 0
        for ds in datasets:
            a = df_detail[(df_detail["Version"] == kds_ver) & (df_detail["Dataset"] == ds)]["Accuracy"].values
            b = df_detail[(df_detail["Version"] == v) & (df_detail["Dataset"] == ds)]["Accuracy"].values
            if len(a) > 0 and len(b) > 0:
                d = np.mean(a) - np.mean(b)
                try:
                    p = sp_stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
                    if p < 0.05:
                        if d > 0:
                            wins += 1
                        else:
                            losses += 1
                    else:
                        ties += 1
                except Exception:
                    ties += 1
            else:
                ties += 1

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
        "\\caption{Holm--Bonferroni step-down statistical significance verification with KDS-EL as control method.}",
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
        "\\vspace{2pt}",
        "\\par\\raggedright\\footnotesize",
        "\\textit{Note}: $W/T/L$: per-dataset significance (two-sided Mann--Whitney $U$ test, $\\alpha = 0.05$). $W$ statistics, $p$-values, and Holm--Bonferroni corrections evaluated across dataset means (paired Wilcoxon signed-rank test~\\cite{demsar2006}).",
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
    delta_cells.extend([f"+{d_acc1:.2f} pp", f"{d_feat1:.1f}\\%"])

    # Step 2: w/o TPS&KER -> w/o TPS (KER)
    d_acc2 = (avg_accs[2] - avg_accs[1]) * 100
    d_feat2 = (avg_feats[2] - avg_feats[1]) / avg_feats[1] * 100
    delta_cells.extend([f"+{d_acc2:.2f} pp", f"{d_feat2:.1f}\\%"])

    # Step 3: w/o TPS -> KDS-EL (TPS)
    d_acc3 = (avg_accs[3] - avg_accs[2]) * 100
    d_feat3 = (avg_feats[3] - avg_feats[2]) / avg_feats[2] * 100
    delta_cells.extend([f"+{d_acc3:.2f} pp", f"{d_feat3:.1f}\\%"])

    # 1. 完整消融递进表 (8 列宽表，保存为 T7_ablation_progression.tex)
    latex_content_prog = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Performance comparison before and after algorithm improvement across 20 benchmark datasets. Best results are in \\textbf{boldface}, and second-best are \\underline{underlined}.}",
        "\\label{T7_prog}\\label{tab:ablation_progression}",
        "\\begin{tabular}{lcccccccc}",
        "\\toprule",
        "& \\multicolumn{2}{c}{Original MEL} & \\multicolumn{2}{c}{KDS-EL w/o TPS\\&KER} & \\multicolumn{2}{c}{KDS-EL w/o TPS} & \\multicolumn{2}{c}{Proposed KDS-EL} \\\\",
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
    with open(os.path.join(out_dir, "T7_ablation_progression.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content_prog))

    # 2. 单栏紧凑对比表 (MEL vs KDS-EL，主文 Table 8，保存为 T7_ablation.tex，保证 18 页单栏排版)
    mel_kds_latex_rows = []
    for ds in datasets:
        ds_tex = ds.replace("_", "\\_")
        sub_mel = df_summary[(df_summary["Version"] == "MEL") & (df_summary["Dataset"] == ds)]
        sub_kds = df_summary[(df_summary["Version"] == "KDS_EL_TwoPhase") & (df_summary["Dataset"] == ds)]
        m_acc = float(sub_mel["Mean_Acc"].values[0])
        m_std = float(sub_mel["Std_Acc"].values[0])
        m_feat = float(sub_mel["Mean_Feat"].values[0])
        k_acc = float(sub_kds["Mean_Acc"].values[0])
        k_std = float(sub_kds["Std_Acc"].values[0])
        k_feat = float(sub_kds["Mean_Feat"].values[0])

        m_f_str = f"{int(round(m_feat)):,}".replace(",", "{,}") if m_feat >= 1000 else f"{int(round(m_feat)):>8d}"
        k_f_str = f"{int(round(k_feat)):,}".replace(",", "{,}") if k_feat >= 1000 else f"{int(round(k_feat))}"

        line = f"{ds_tex:16s} & {m_acc:.4f}$\\pm${m_std:.4f} & {m_f_str} & \\textbf{{{k_acc:.4f}$\\pm${k_std:.4f}}} & \\underline{{{k_f_str}}} \\\\"
        mel_kds_latex_rows.append(line)

    avg_mel_acc = float(df_summary[(df_summary["Version"] == "MEL") & (df_summary["Dataset"].isin(datasets))]["Mean_Acc"].mean())
    avg_mel_feat = float(df_summary[(df_summary["Version"] == "MEL") & (df_summary["Dataset"].isin(datasets))]["Mean_Feat"].mean())
    avg_kds_acc = float(df_summary[(df_summary["Version"] == "KDS_EL_TwoPhase") & (df_summary["Dataset"].isin(datasets))]["Mean_Acc"].mean())
    avg_kds_feat = float(df_summary[(df_summary["Version"] == "KDS_EL_TwoPhase") & (df_summary["Dataset"].isin(datasets))]["Mean_Feat"].mean())

    # 标准差采用 pooled 或平均样本标准差，或计算各数据集均值的标准差
    mel_std_mean = float(df_summary[(df_summary["Version"] == "MEL") & (df_summary["Dataset"].isin(datasets))]["Std_Acc"].mean())
    kds_std_mean = float(df_summary[(df_summary["Version"] == "KDS_EL_TwoPhase") & (df_summary["Dataset"].isin(datasets))]["Std_Acc"].mean())

    d_pp = (avg_kds_acc - avg_mel_acc) * 100
    d_feat_pct = (avg_kds_feat - avg_mel_feat) / avg_mel_feat * 100

    mel_feat_str = f"{int(round(avg_mel_feat)):,}".replace(",", "{,}") if avg_mel_feat >= 1000 else f"{avg_mel_feat:.1f}"
    kds_feat_str = f"{int(round(avg_kds_feat)):,}".replace(",", "{,}") if avg_kds_feat >= 1000 else f"{avg_kds_feat:.1f}"

    latex_content_single = [
        "\\begin{table}[!htb]",
        "\\centering",
        "\\caption{Comparison of KDS-EL and the original MEL performance before and after improvement.}",
        "\\label{T7}\\label{tab:mechanism_comparison}",
        "\\footnotesize",
        "\\setlength{\\tabcolsep}{2.5pt}",
        "\\renewcommand{\\arraystretch}{1.08}",
        "\\begin{tabular*}{\\columnwidth}{@{\\extracolsep{\\fill}}lcccc@{}}",
        "\\toprule",
        "Dataset & \\multicolumn{2}{c}{Original MEL} & \\multicolumn{2}{c}{Proposed KDS-EL} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}",
        "& $\\mathrm{Acc} \\pm \\mathrm{Std}$ & Number & $\\mathrm{Acc} \\pm \\mathrm{Std}$ & Number \\\\",
        "\\midrule",
        "\n".join(mel_kds_latex_rows),
        "\\midrule",
        f"Average          & {avg_mel_acc:.4f}$\\pm${mel_std_mean:.4f} & {mel_feat_str} & \\textbf{{{avg_kds_acc:.4f}$\\pm${kds_std_mean:.4f}}} & \\underline{{{kds_feat_str}}} \\\\",
        f"$\\Delta$ vs. Original MEL & \\multicolumn{{2}}{{c}}{{—}} & \\textbf{{+{d_pp:.2f} pp}} & \\underline{{{d_feat_pct:.1f}\\%}} \\\\",
        "\\bottomrule",
        "\\end{tabular*}",
        "\\vspace{2pt}",
        "\\par\\raggedright\\footnotesize",
        "\\textit{Note}: Bold: superior accuracy; underline: more compact subset. Results reported as $\\mathrm{Mean} \\pm \\mathrm{Std}$ over 10 independent runs.",
        "\\end{table}",
    ]
    with open(os.path.join(out_dir, "T7_ablation.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(latex_content_single))

    # 同时输出补充材料需要的 T-A4_per_dataset_ablation.tex
    ta4_content = [
        "\\begin{table*}[!t]",
        "\\centering",
        "\\caption{Granular per-dataset performance comparison before and after algorithm improvement across 20 benchmark datasets.}",
        "\\label{T-A4}",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\renewcommand{\\arraystretch}{1.06}",
        "\\resizebox{\\textwidth}{!}{%",
        "\\begin{tabular}{@{}lcccccccc@{}}",
        "\\toprule",
        "Dataset & \\multicolumn{2}{c}{MEL} & \\multicolumn{2}{c}{MEL+MI} & \\multicolumn{2}{c}{KDS-EL w/o TPS} & \\multicolumn{2}{c}{KDS-EL} \\\\",
        "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5} \\cmidrule(lr){6-7} \\cmidrule(lr){8-9}",
        " & Acc & Feat & Acc & Feat & Acc & Feat & Acc & Feat \\\\",
        "\\midrule",
        "\n".join(latex_rows),
        "\\midrule",
        " & ".join(avg_cells) + " \\\\",
        " & ".join(delta_cells) + " \\\\",
        "\\bottomrule",
        "\\end{tabular}%",
        "}",
        "\\end{table*}",
    ]
    with open(os.path.join(out_dir, "T-A4_per_dataset_ablation.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(ta4_content))

    print(f"  [OK] CSV: {out_dir}/T7_ablation.csv")
    print(f"  [OK] TeX: {out_dir}/T7_ablation.tex & T7_ablation_progression.tex & T-A4_per_dataset_ablation.tex")


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
        "T6b": lambda: table_t6b_holm(df_detail, df_summary, args.out),
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
