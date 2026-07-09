"""
KDS-EL 表格生成脚本
===================
根据《图表规划.md》生成 T4-T8（共5张表）。
数据来源：四个正式实验目录。

用法：
    python generate_tables.py
    python generate_tables.py --out tables/ --tab T4
"""
import os, sys, argparse
import numpy as np
import pandas as pd
from pathlib import Path

try:
    from scipy import stats as sp_stats
except ImportError:
    sp_stats = None

# ══════════════════════════════════════════════════════════════════════════════
# 路径
# ══════════════════════════════════════════════════════════════════════════════

PROJ = Path(__file__).resolve().parent.parent
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"   # SOTA
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # Ablation V1 (MEL only)
EXP3_DIR = PROJ / "output" / "formal_experiment_20260702_145828"   # Ablation V2 (KDS-EL variants)
EXP4_DIR = PROJ / "output" / "formal_experiment_20260707_142018"   # MOFS

# ── 全部15个方法 ──
ALL_VERSIONS = [
    "BPSO", "SaWDE", "FWPSO", "MEL",
    "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL",
    "PSO_CSM", "IGPSO",
    "NSGA_II_FS", "MOPSO_FS", "MOEA_D_FS",
    "fMOPSO_FS", "VGS_MOEA", "W_MOPSO_FS",
]

# ── 主表10方法（正文用）──
MAIN_VERSIONS = [
    "KDS_EL", "KDS_EL_KER", "KDS_EL_DRS", "MEL",
    "FWPSO", "PSO_CSM", "SaWDE",
    "VGS_MOEA", "W_MOPSO_FS", "NSGA_II_FS",
]

ABL_VERSIONS = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

# ── 消融方法（T7用）──
MOFS_VERSIONS = ["NSGA_II_FS", "MOPSO_FS", "MOEA_D_FS",
                 "fMOPSO_FS", "VGS_MOEA", "W_MOPSO_FS"]

V_LABELS = {
    "BPSO": "BPSO", "SaWDE": "SaWDE", "FWPSO": "FWPSO",
    "MEL": "MEL", "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "KDS_EL": "KDS-EL",
    "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
    "NSGA_II_FS": "NSGA-II-FS", "MOPSO_FS": "MOPSO-FS",
    "MOEA_D_FS": "MOEA-D-FS", "fMOPSO_FS": "fMOPSO-FS",
    "VGS_MOEA": "VGS-MOEA", "W_MOPSO_FS": "W-MOPSO-FS",
}

# ── 20个MOFS数据集 ──
MOFS_DATASETS = [
    "ALL1", "ALL4", "ALL_AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon",
]


def load_detail(path):
    df = pd.read_csv(path)
    for col in ["Accuracy", "Num_Features", "Time_sec", "Avg_NHD"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Accuracy"])


def load_merged_detail():
    """合并四个实验的 detail 数据：各方法从各自有效来源加载"""
    SOTA_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    KDS_VERSIONS = ["KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"]

    dfs = []
    df1 = load_detail(EXP1_DIR / "results_detail.csv")
    dfs.append(df1[df1["Version"].isin(SOTA_VERSIONS)])
    df2 = load_detail(EXP2_DIR / "results_detail.csv")
    dfs.append(df2[df2["Version"] == "MEL"])
    df3 = load_detail(EXP3_DIR / "results_detail.csv")
    dfs.append(df3[df3["Version"].isin(KDS_VERSIONS)])
    df4 = load_detail(EXP4_DIR / "results_detail.csv")
    dfs.append(df4[df4["Version"].isin(MOFS_VERSIONS)])

    common_cols = None
    for d in dfs:
        if common_cols is None:
            common_cols = set(d.columns)
        else:
            common_cols &= set(d.columns)
    common_cols = list(common_cols) if common_cols else []
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def load_merged_summary():
    """合并四个实验的 summary 数据：各方法从各自有效来源加载"""
    SOTA_VERSIONS = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    KDS_VERSIONS = ["KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"]

    dfs = []
    df1 = pd.read_csv(EXP1_DIR / "results_summary.csv")
    dfs.append(df1[df1["Version"].isin(SOTA_VERSIONS)])
    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    dfs.append(df2[df2["Version"] == "MEL"])
    df3 = pd.read_csv(EXP3_DIR / "results_summary.csv")
    dfs.append(df3[df3["Version"].isin(KDS_VERSIONS)])
    df4 = pd.read_csv(EXP4_DIR / "results_summary.csv")
    dfs.append(df4[df4["Version"].isin(MOFS_VERSIONS)])

    common_cols = None
    for d in dfs:
        if common_cols is None:
            common_cols = set(d.columns)
        else:
            common_cols &= set(d.columns)
    common_cols = list(common_cols) if common_cols else []
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def g(df, version, dataset, metric="Accuracy"):
    s = df[(df.Version == version) & (df.Dataset == dataset)][metric].values
    return s if len(s) > 0 else np.array([np.nan])


# ══════════════════════════════════════════════════════════════════════════════
# T4: 准确率 Mean ± Std（主表10方法 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def table_t4_accuracy(df_summary, out_dir):
    """T4: Classification accuracy Mean ± Std — 10 main methods × 20 datasets."""
    print("T4: Accuracy Mean ± Std table (10 methods × 20 datasets)...")
    all_ds = [d for d in MOFS_DATASETS if d in df_summary["Dataset"].unique()]
    versions = [v for v in MAIN_VERSIONS if v in df_summary["Version"].unique()]

    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
            else:
                row[V_LABELS[v]] = "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T4_accuracy.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    latex_path = os.path.join(out_dir, "T4_accuracy.tex")
    latex = df_t.to_latex(index=False, column_format="l" + "c" * len(versions),
                          caption="Classification Accuracy (Mean $\\pm$ Std) — 10 methods on 20 datasets.",
                          label="tab:accuracy")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  {outpath}")
    print(f"  {latex_path}")

    # Also generate appendix table with ALL 15 methods
    print("  → T4-Appendix: all 15 methods...")
    all_versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    table_app = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in all_versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
            else:
                row[V_LABELS[v]] = "—"
        table_app.append(row)

    df_app = pd.DataFrame(table_app)
    app_path = os.path.join(out_dir, "T4_appendix_accuracy.csv")
    df_app.to_csv(app_path, index=False, encoding="utf-8-sig")
    print(f"  {app_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T5: 特征数 Mean（主表10方法 × 20数据集）
# ══════════════════════════════════════════════════════════════════════════════

def table_t5_features(df_summary, out_dir):
    """T5: Number of selected features Mean — 10 main methods × 20 datasets."""
    print("T5: Feature count Mean table (10 methods × 20 datasets)...")
    all_ds = [d for d in MOFS_DATASETS if d in df_summary["Dataset"].unique()]
    versions = [v for v in MAIN_VERSIONS if v in df_summary["Version"].unique()]

    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Feat'].values[0]:.0f}"
            else:
                row[V_LABELS[v]] = "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T5_features.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    latex_path = os.path.join(out_dir, "T5_features.tex")
    latex = df_t.to_latex(index=False, column_format="l" + "c" * len(versions),
                          caption="Number of Selected Features (Mean) — 10 methods on 20 datasets.",
                          label="tab:features")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T6: Wilcoxon p-value matrix（10方法）
# ══════════════════════════════════════════════════════════════════════════════

def table_t6_wilcoxon(df_summary, out_dir):
    """T6: Wilcoxon signed-rank p-value matrix — 10 main methods."""
    print("T6: Wilcoxon p-value matrix (10 methods)...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    df_detail = load_merged_detail()
    versions = [v for v in MAIN_VERSIONS if v in df_summary["Version"].unique()]
    n_v = len(versions)

    # Find shared datasets for these versions
    ds_sets = []
    for v in versions:
        ds = set(df_detail[df_detail["Version"] == v]["Dataset"].unique())
        if ds:
            ds_sets.append(ds)
    shared_ds = sorted(set.intersection(*ds_sets))
    print(f"  Shared datasets: {len(shared_ds)}")

    pval_matrix = np.zeros((n_v, n_v))
    win_matrix = np.zeros((n_v, n_v), dtype=int)
    total_matrix = np.zeros((n_v, n_v), dtype=int)

    for ds in shared_ds:
        for i, v1 in enumerate(versions):
            a1 = g(df_detail, v1, ds)
            if len(a1) < 3:
                continue
            for j, v2 in enumerate(versions):
                if i >= j:
                    continue
                a2 = g(df_detail, v2, ds)
                if len(a2) < 3:
                    continue
                try:
                    if len(a1) == len(a2):
                        _, p = sp_stats.wilcoxon(a1, a2)
                    else:
                        _, p = sp_stats.mannwhitneyu(a1, a2, alternative='two-sided')
                except Exception:
                    continue
                pval_matrix[i, j] += -np.log10(max(p, 1e-10))
                pval_matrix[j, i] += -np.log10(max(p, 1e-10))
                total_matrix[i, j] += 1
                total_matrix[j, i] += 1
                if p < 0.05 and np.mean(a1) > np.mean(a2):
                    win_matrix[i, j] += 1
                elif p < 0.05 and np.mean(a2) > np.mean(a1):
                    win_matrix[j, i] += 1

    for i in range(n_v):
        for j in range(n_v):
            if total_matrix[i, j] > 0:
                pval_matrix[i, j] /= total_matrix[i, j]

    table = []
    for i, v1 in enumerate(versions):
        row = {"Method": V_LABELS[v1]}
        for j, v2 in enumerate(versions):
            if i == j:
                row[V_LABELS[v2]] = "—"
            else:
                w = win_matrix[i, j]
                t = total_matrix[i, j]
                row[V_LABELS[v2]] = f"{w}/{int(t)}" if t > 0 else "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T6_wilcoxon.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    latex_lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Wilcoxon Signed-Rank Test — Win Count / Total Shared Datasets (10 methods).}",
        r"\label{tab:wilcoxon}",
        r"\small",
        r"\begin{tabular}{l" + "c" * n_v + "}",
        r"\toprule",
        r"Method & " + " & ".join(V_LABELS[v] for v in versions) + r" \\",
        r"\midrule",
    ]
    for i, v1 in enumerate(versions):
        cells = [V_LABELS[v1]]
        for j, v2 in enumerate(versions):
            if i == j:
                cells.append("—")
            else:
                w = win_matrix[i, j]
                t = total_matrix[i, j]
                cells.append(f"{w}/{int(t)}" if t > 0 else "—")
        latex_lines.append(" & ".join(cells) + r" \\")
    latex_lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])

    latex_path = os.path.join(out_dir, "T6_wilcoxon.tex")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_lines))
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T7: 消融实验 ACC + Features（4变体 × 26数据集, 不受MOFS影响）
# ══════════════════════════════════════════════════════════════════════════════

def table_t7_ablation(df_summary, out_dir):
    """T7: Ablation study — Accuracy, Features, NHD for 4 variants on 26 datasets."""
    print("T7: Ablation study table (4 variants × 26 datasets)...")

    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    df_mel = df2[df2["Version"] == "MEL"]
    df3 = pd.read_csv(EXP3_DIR / "results_summary.csv")
    df3_abl = df3[df3["Version"].isin(["KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"])]
    df_abl = pd.concat([df_mel, df3_abl], ignore_index=True)
    all_ds = sorted(set(df_mel["Dataset"].unique()) & set(df3_abl["Dataset"].unique()))
    print(f"  Ablation datasets: {len(all_ds)}")

    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        best_acc = -1
        best_feat = float("inf")
        best_acc_v = best_feat_v = ""
        for v in ABL_VERSIONS:
            sub = df_abl[(df_abl["Version"] == v) & (df_abl["Dataset"] == ds)]
            if len(sub) > 0:
                acc = sub["Mean_Acc"].values[0]
                feat = sub["Mean_Feat"].values[0]
                nhd = sub["Mean_NHD"].values[0] if "Mean_NHD" in sub.columns else 0
                row[f"{V_LABELS[v]}_Acc"] = f"{acc:.4f}±{sub['Std_Acc'].values[0]:.4f}"
                row[f"{V_LABELS[v]}_Feat"] = f"{feat:.0f}"
                row[f"{V_LABELS[v]}_NHD"] = f"{nhd:.4f}"
                if acc > best_acc:
                    best_acc = acc
                    best_acc_v = V_LABELS[v]
                if feat < best_feat and acc >= best_acc * 0.98:
                    best_feat = feat
                    best_feat_v = V_LABELS[v]
            else:
                for suffix in ["_Acc", "_Feat", "_NHD"]:
                    row[f"{V_LABELS[v]}{suffix}"] = "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T7_ablation.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    # Compact LaTeX version (Acc only)
    compact = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in ABL_VERSIONS:
            sub = df_abl[(df_abl["Version"] == v) & (df_abl["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
            else:
                row[V_LABELS[v]] = "—"
        compact.append(row)
    df_compact = pd.DataFrame(compact)

    latex_path = os.path.join(out_dir, "T7_ablation.tex")
    latex = df_compact.to_latex(index=False,
                                column_format="l" + "c" * len(ABL_VERSIONS),
                                caption="Ablation Study — Classification Accuracy (Mean $\\pm$ Std) on 26 datasets.",
                                label="tab:ablation")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T8: MOFS 六方法单独对比（NEW）
# ══════════════════════════════════════════════════════════════════════════════

def table_t8_mofs(df_summary, out_dir):
    """T8: MOFS comparison — Acc, Feat, SR, Time for 6 MOFS methods + KDS_EL for reference."""
    print("T8: MOFS comparison table (6 MOFS + KDS_EL)...")
    mofs_v = [v for v in MOFS_VERSIONS if v in df_summary["Version"].unique()]
    # Include KDS_EL as baseline
    kds_ref = "KDS_EL"
    all_methods = mofs_v + [kds_ref] if kds_ref in df_summary["Version"].unique() else mofs_v
    all_ds = [d for d in MOFS_DATASETS if d in df_summary["Dataset"].unique()]

    # Overall averages
    table = []
    for v in all_methods:
        sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"].isin(all_ds))]
        if len(sub) > 0:
            row = {
                "Method": V_LABELS[v],
                "True_Acc": f"{sub['Mean_Acc'].mean():.4f}",
                "Mean_Feat": f"{sub['Mean_Feat'].mean():.0f}",
            }
            # Compute average selection ratio
            row["SR_pct"] = f"{sub['Mean_Feat'].mean() / 5000 * 100:.1f}%"
            row["Time_s"] = f"{sub['Mean_Time'].mean():.1f}"
            table.append(row)

    df_t = pd.DataFrame(table)
    # Sort by True_Acc descending
    df_t = df_t.sort_values("True_Acc", ascending=False)

    outpath = os.path.join(out_dir, "T8_mofs.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    latex_path = os.path.join(out_dir, "T8_mofs.tex")
    latex = df_t.to_latex(index=False,
                          column_format="lcccc",
                          caption="MOFS Methods Comparison — True Accuracy, Features, Selection Ratio, Runtime (Mean over 20 datasets).",
                          label="tab:mofs")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="KDS-EL Table Generator")
    parser.add_argument("--out", default=None,
                        help="Output directory (default: output/tables/)")
    parser.add_argument("--tab", nargs="*", default=None,
                        help="Specific tables to generate (T4 T5 T6 T7 T8)")
    args = parser.parse_args()

    out_dir = args.out or str(PROJ / "output" / "tables")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading summary data from 4 experiments...")
    print(f"  Exp1 (SOTA):  {EXP1_DIR}")
    print(f"  Exp2 (MEL):   {EXP2_DIR}")
    print(f"  Exp3 (KDS-EL): {EXP3_DIR}")
    print(f"  Exp4 (MOFS):  {EXP4_DIR}")
    df_summary = load_merged_summary()
    print(f"  {len(df_summary)} rows, datasets={df_summary.Dataset.nunique()}, versions={df_summary.Version.nunique()}")
    print(f"  Methods: {sorted(df_summary['Version'].unique())}")
    print(f"\nGenerating tables → {out_dir}\n")

    all_tabs = {
        "T4": table_t4_accuracy,
        "T5": table_t5_features,
        "T6": table_t6_wilcoxon,
        "T7": table_t7_ablation,
        "T8": table_t8_mofs,
    }

    requested = args.tab if args.tab else list(all_tabs.keys())
    for key in requested:
        if key in all_tabs:
            try:
                all_tabs[key](df_summary, out_dir)
            except Exception as e:
                print(f"  [FAIL] {key}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  [SKIP] Unknown table: {key}")

    print(f"\nDone! All tables saved to: {out_dir}")


if __name__ == "__main__":
    main()
