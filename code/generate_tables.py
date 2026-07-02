"""
KDS-EL 表格生成脚本
===================
根据《图表规划.md》生成 T4-T7（共4张表）。

用法：
    python generate_tables.py
    python generate_tables.py --out tables/
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
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"

ALL_VERSIONS = [
    "BPSO", "SaWDE", "FWPSO", "MEL",
    "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL",
    "PSO_CSM", "IGPSO",
]
ABL_VERSIONS = ["MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

V_LABELS = {
    "BPSO": "BPSO", "SaWDE": "SaWDE", "FWPSO": "FWPSO",
    "MEL": "MEL", "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "KDS_EL": "KDS-EL",
    "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
}


def load_detail(path):
    df = pd.read_csv(path)
    for col in ["Accuracy", "Num_Features", "Time_sec", "Avg_NHD"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Accuracy"])


def load_merged_detail():
    df1 = load_detail(EXP1_DIR / "results_detail.csv")
    df2 = load_detail(EXP2_DIR / "results_detail.csv")
    common_cols = [c for c in df1.columns if c in df2.columns]
    return pd.concat([df1[common_cols], df2[common_cols]], ignore_index=True)


def load_merged_summary():
    df1 = pd.read_csv(EXP1_DIR / "results_summary.csv")
    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    common_cols = [c for c in df1.columns if c in df2.columns]
    return pd.concat([df1[common_cols], df2[common_cols]], ignore_index=True)


def g(df, version, dataset, metric="Accuracy"):
    s = df[(df.Version == version) & (df.Dataset == dataset)][metric].values
    return s if len(s) > 0 else np.array([np.nan])


# ══════════════════════════════════════════════════════════════════════════════
# T4: 准确率 Mean ± Std
# ══════════════════════════════════════════════════════════════════════════════

def table_t4_accuracy(df_summary, out_dir):
    """T4: Classification accuracy Mean ± Std for all methods on all datasets."""
    print("T4: Accuracy Mean ± Std table...")
    # Get all datasets from both experiments
    all_ds = sorted(set(df_summary["Dataset"].unique()))

    # Build table: columns = versions, rows = datasets
    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in ALL_VERSIONS:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
            else:
                row[V_LABELS[v]] = "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    # Mark best per row
    outpath = os.path.join(out_dir, "T4_accuracy.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    # Also write a LaTeX version
    latex_path = os.path.join(out_dir, "T4_accuracy.tex")
    latex = df_t.to_latex(index=False, column_format="l" + "c" * len(ALL_VERSIONS),
                          caption="Classification Accuracy (Mean $\\pm$ Std) across all datasets.",
                          label="tab:accuracy")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T5: 特征数 Mean
# ══════════════════════════════════════════════════════════════════════════════

def table_t5_features(df_summary, out_dir):
    """T5: Number of selected features Mean for all methods on all datasets."""
    print("T5: Feature count Mean table...")
    all_ds = sorted(set(df_summary["Dataset"].unique()))

    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in ALL_VERSIONS:
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
    latex = df_t.to_latex(index=False, column_format="l" + "c" * len(ALL_VERSIONS),
                          caption="Number of Selected Features (Mean) across all datasets.",
                          label="tab:features")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T6: Wilcoxon p-value matrix
# ══════════════════════════════════════════════════════════════════════════════

def table_t6_wilcoxon(df_summary, out_dir):
    """T6: Wilcoxon signed-rank p-value matrix (aggregate over shared datasets)."""
    print("T6: Wilcoxon p-value matrix...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    # Load detail for per-run data
    df_detail = load_merged_detail()
    shared_ds = sorted(set(
        pd.read_csv(EXP1_DIR / "results_summary.csv")["Dataset"].unique()
    ) & set(
        pd.read_csv(EXP2_DIR / "results_summary.csv")["Dataset"].unique()
    ))

    n_v = len(ALL_VERSIONS)
    # Build p-value matrix: count wins/losses/ties
    pval_matrix = np.zeros((n_v, n_v))
    win_matrix = np.zeros((n_v, n_v), dtype=int)
    total_matrix = np.zeros((n_v, n_v), dtype=int)

    for ds in shared_ds:
        for i, v1 in enumerate(ALL_VERSIONS):
            a1 = g(df_detail, v1, ds)
            if len(a1) < 3:
                continue
            for j, v2 in enumerate(ALL_VERSIONS):
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
                pval_matrix[i, j] += -np.log10(max(p, 1e-10))  # aggregate -log10(p)
                pval_matrix[j, i] += -np.log10(max(p, 1e-10))
                total_matrix[i, j] += 1
                total_matrix[j, i] += 1
                if p < 0.05 and np.mean(a1) > np.mean(a2):
                    win_matrix[i, j] += 1
                elif p < 0.05 and np.mean(a2) > np.mean(a1):
                    win_matrix[j, i] += 1

    # Average the -log10(p)
    for i in range(n_v):
        for j in range(n_v):
            if total_matrix[i, j] > 0:
                pval_matrix[i, j] /= total_matrix[i, j]

    # Build output: format = "win / total (avg -log10 p)"
    table = []
    for i, v1 in enumerate(ALL_VERSIONS):
        row = {"Method": V_LABELS[v1]}
        for j, v2 in enumerate(ALL_VERSIONS):
            if i == j:
                row[V_LABELS[v2]] = "—"
            else:
                w = win_matrix[i, j]
                t = total_matrix[i, j]
                lp = pval_matrix[i, j]
                row[V_LABELS[v2]] = f"{w}/{int(t)}" if t > 0 else "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T6_wilcoxon.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    # LaTeX with proper formatting
    latex_lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Wilcoxon Signed-Rank Test Results — Win Count / Total Shared Datasets.}",
        r"\label{tab:wilcoxon}",
        r"\small",
        r"\begin{tabular}{l" + "c" * len(ALL_VERSIONS) + "}",
        r"\toprule",
        r"Method & " + " & ".join(V_LABELS[v] for v in ALL_VERSIONS) + r" \\",
        r"\midrule",
    ]
    for i, v1 in enumerate(ALL_VERSIONS):
        cells = [V_LABELS[v1]]
        for j, v2 in enumerate(ALL_VERSIONS):
            if i == j:
                cells.append("—")
            else:
                w = win_matrix[i, j]
                t = total_matrix[i, j]
                lp = pval_matrix[i, j]
                cells.append(f"{w}/{int(t)}" if t > 0 else "—")
        latex_lines.append(" & ".join(cells) + r" \\")
    latex_lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ])

    latex_path = os.path.join(out_dir, "T6_wilcoxon.tex")
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_lines))
    print(f"  {outpath}")
    print(f"  {latex_path}")


# ══════════════════════════════════════════════════════════════════════════════
# T7: 消融实验 ACC + Features
# ══════════════════════════════════════════════════════════════════════════════

def table_t7_ablation(df_summary, out_dir):
    """T7: Ablation study — Accuracy and Features for 4 variants."""
    print("T7: Ablation study table...")

    # Use only exp2 data
    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    all_ds = sorted(df2["Dataset"].unique())

    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        best_acc = -1
        best_feat = float("inf")
        best_acc_v = best_feat_v = ""
        for v in ABL_VERSIONS:
            sub = df2[(df2["Version"] == v) & (df2["Dataset"] == ds)]
            if len(sub) > 0:
                acc = sub["Mean_Acc"].values[0]
                feat = sub["Mean_Feat"].values[0]
                nhd = sub["Mean_NHD"].values[0]
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
                row[f"{V_LABELS[v]}_Acc"] = "—"
                row[f"{V_LABELS[v]}_Feat"] = "—"
                row[f"{V_LABELS[v]}_NHD"] = "—"
        row["Best_Acc"] = best_acc_v
        table.append(row)

    df_t = pd.DataFrame(table)

    # Save CSV
    outpath = os.path.join(out_dir, "T7_ablation.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    # Save a compact version for LaTeX (Acc only)
    compact = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in ABL_VERSIONS:
            sub = df2[(df2["Version"] == v) & (df2["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
            else:
                row[V_LABELS[v]] = "—"
        compact.append(row)
    df_compact = pd.DataFrame(compact)

    latex_path = os.path.join(out_dir, "T7_ablation.tex")
    latex = df_compact.to_latex(index=False,
                                column_format="l" + "c" * len(ABL_VERSIONS),
                                caption="Ablation Study — Classification Accuracy (Mean $\\pm$ Std).",
                                label="tab:ablation")
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
                        help="Specific tables to generate (T4 T5 T6 T7)")
    args = parser.parse_args()

    out_dir = args.out or str(PROJ / "output" / "tables")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading summary data...")
    df_summary = load_merged_summary()
    print(f"  {len(df_summary)} rows, datasets={df_summary.Dataset.nunique()}, versions={df_summary.Version.nunique()}")
    print(f"\nGenerating tables → {out_dir}\n")

    all_tabs = {
        "T4": table_t4_accuracy,
        "T5": table_t5_features,
        "T6": table_t6_wilcoxon,
        "T7": table_t7_ablation,
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
