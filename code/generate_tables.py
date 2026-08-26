"""
KDS-EL 表格生成脚本 (2026-07-29 修订版)
=========================================
根据《图表规划.md》生成 T4-T8, T6b。

变更:
  - 新增 FINAL_DIR (KDS_EL_TwoPhase / KDS_EL_NoPool)
  - 移除 VGS-MOEA, 废弃变体 (KDS_EL_DRS/KER/old)
  - 14 定长方法主表, 4 变体消融链
  - T8 改为 TwoPhase 消融逐数据集表

用法: python generate_tables.py [--out output/tables/] [--tab T4]
"""
import os, sys, argparse
import numpy as np
import pandas as pd
from pathlib import Path

try:
    from scipy import stats as sp_stats
except ImportError:
    sp_stats = None

# ═══ 路径 ═══
PROJ = Path(__file__).resolve().parent.parent
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"   # SOTA
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # MEL
EXP4_DIR = PROJ / "output" / "formal_experiment_20260707_142018"   # MOFS
MEL_MI_DIR = PROJ / "output" / "formal_experiment_mel_mi"          # MEL+MI
FINAL_DIR = PROJ / "output" / "formal_experiment_final"            # NoPool + TwoPhase

# ═══ 14 定长方法 (顶刊顺序: Proposed → 消融 → 基线 → SOTA → MOFS) ═══
ALL_VERSIONS = [
    "KDS_EL_TwoPhase",   # 1. 本文最终版
    "KDS_EL_NoPool",     # 2. 消融变体 (去两阶段)
    "MEL_MI",            # 3. 消融基线 (MI+Reinit)
    "MEL",               # 4. 绝对基线
    "FWPSO",             # 5. SOTA #1
    "PSO_CSM",           # 6. SOTA
    "SaWDE",             # 7. SOTA
    "IGPSO",             # 8. SOTA
    "BPSO",              # 9. SOTA
    "W-MOPSO-FS",        # 10. MOFS #1
    "fMOPSO-FS",         # 11. MOFS
    "NSGA-II-FS",        # 12. MOFS
    "MOEA-D-FS",         # 13. MOFS
    "MOPSO-FS",          # 14. MOFS
]

# 消融 4 变体 (无 DRS)
ABL_VERSIONS = ["MEL", "MEL_MI", "KDS_EL_NoPool", "KDS_EL_TwoPhase"]

# MOFS 定长 5 方法 (不含 VGS-MOEA)
MOFS_VERSIONS = ["NSGA-II-FS", "MOPSO-FS", "MOEA-D-FS",
                 "fMOPSO-FS", "W-MOPSO-FS"]

V_LABELS = {
    "BPSO": "BPSO", "SaWDE": "SaWDE", "FWPSO": "FWPSO",
    "MEL": "MEL", "MEL_MI": "KDS-EL w/o TPS\\&KER",
    "KDS_EL_NoPool": "KDS-EL w/o TPS",
    "KDS_EL_TwoPhase": "KDS-EL",
    "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
    "NSGA-II-FS": "NSGA-II-FS", "MOPSO-FS": "MOPSO-FS",
    "MOEA-D-FS": "MOEA-D-FS", "fMOPSO-FS": "fMOPSO-FS",
    "W-MOPSO-FS": "W-MOPSO-FS",
}

# 主表 20 数据集
MOFS_DATASETS = [
    "ALL1", "ALL4", "ALL_AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon",
]

# 消融 25 数据集 (20 + ALL2, ALL3, RELATHE, Stroke, USPS, 排除 CNS)
ABL_DATASETS = MOFS_DATASETS + ["ALL2", "ALL3", "RELATHE", "Stroke", "USPS"]


def load_detail(path):
    df = pd.read_csv(path)
    for col in ["Accuracy", "Num_Features", "Time_sec", "Avg_NHD"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Accuracy"])


def load_merged_detail():
    """合并所有实验的 detail 数据"""
    SOTA_V = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    FINAL_V = ["KDS_EL_NoPool", "KDS_EL_TwoPhase"]

    dfs = []
    # SOTA
    df1 = load_detail(EXP1_DIR / "results_detail.csv")
    dfs.append(df1[df1["Version"].isin(SOTA_V)])
    # MEL
    df2 = load_detail(EXP2_DIR / "results_detail.csv")
    dfs.append(df2[df2["Version"] == "MEL"])
    # MOFS
    df4 = load_detail(EXP4_DIR / "results_detail.csv")
    dfs.append(df4[df4["Version"].isin(MOFS_VERSIONS)])
    # MEL+MI
    df_mi = load_detail(MEL_MI_DIR / "results_detail.csv")
    dfs.append(df_mi[df_mi["Version"] == "MEL_MI"])
    # Final (NoPool + TwoPhase)
    df_fin = load_detail(FINAL_DIR / "results_detail.csv")
    dfs.append(df_fin[df_fin["Version"].isin(FINAL_V)])

    common_cols = list(set.intersection(*[set(d.columns) for d in dfs]))
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def load_merged_summary():
    """合并所有实验的 summary 数据"""
    SOTA_V = ["BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"]
    FINAL_V = ["KDS_EL_NoPool", "KDS_EL_TwoPhase"]

    dfs = []
    df1 = pd.read_csv(EXP1_DIR / "results_summary.csv")
    dfs.append(df1[df1["Version"].isin(SOTA_V)])
    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    dfs.append(df2[df2["Version"] == "MEL"])
    df4 = pd.read_csv(EXP4_DIR / "results_summary.csv")
    dfs.append(df4[df4["Version"].isin(MOFS_VERSIONS)])
    df_mi = pd.read_csv(MEL_MI_DIR / "results_summary.csv")
    dfs.append(df_mi[df_mi["Version"] == "MEL_MI"])
    df_fin = pd.read_csv(FINAL_DIR / "results_summary.csv")
    dfs.append(df_fin[df_fin["Version"].isin(FINAL_V)])

    common_cols = list(set.intersection(*[set(d.columns) for d in dfs]))
    return pd.concat([d[common_cols] for d in dfs], ignore_index=True)


def g(df, version, dataset, metric="Accuracy"):
    s = df[(df.Version == version) & (df.Dataset == dataset)][metric].values
    return s if len(s) > 0 else np.array([np.nan])


# ═══ T4: 准确率 Mean ± Std ═══
def table_t4_accuracy(df_summary, out_dir):
    print("T4: Accuracy Mean ± Std (14 methods x 20 datasets)...")
    all_ds = [d for d in MOFS_DATASETS if d in df_summary["Dataset"].unique()]
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]

    # Full 14-method table
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
    print(f"  {outpath}")

    # Compact 10-method for main paper
    main_v = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    compact = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in main_v:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
            else:
                row[V_LABELS[v]] = "—"
        compact.append(row)
    df_compact = pd.DataFrame(compact)
    compact_path = os.path.join(out_dir, "T4_accuracy_10method.csv")
    df_compact.to_csv(compact_path, index=False, encoding="utf-8-sig")
    print(f"  {compact_path} (10-method compact)")


# ═══ T4 符号：逐数据集 two-sided Wilcoxon signed-rank ═══
T4_SYMBOL_METHODS = [
    "KDS_EL_KER", "MEL+MI", "MEL", "FWPSO", "PSO-CSM", "SaWDE",
    "IGPSO", "BPSO", "W-MOPSO-FS", "fMOPSO-FS", "NSGA-II-FS",
    "MOEA-D-FS", "MOPSO-FS",
]

T4_SYMBOL_VERSION_MAP = {
    "KDS_EL_KER": "KDS_EL_NoPool",
    "MEL+MI": "MEL_MI",
    "MEL": "MEL",
    "FWPSO": "FWPSO",
    "PSO-CSM": "PSO_CSM",
    "SaWDE": "SaWDE",
    "IGPSO": "IGPSO",
    "BPSO": "BPSO",
    "W-MOPSO-FS": "W-MOPSO-FS",
    "fMOPSO-FS": "fMOPSO-FS",
    "NSGA-II-FS": "NSGA-II-FS",
    "MOEA-D-FS": "MOEA-D-FS",
    "MOPSO-FS": "MOPSO-FS",
}


def table_t4_symbols(df_detail, out_dir):
    """Generate per-dataset T4 symbols via two-sided Wilcoxon signed-rank tests."""
    print("T4: per-dataset Wilcoxon signed-rank symbols...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return
    rows = []
    for ds in MOFS_DATASETS:
        a = g(df_detail, "KDS_EL_TwoPhase", ds)
        if len(a) == 0:
            continue
        row = {"Dataset": ds}
        for method in T4_SYMBOL_METHODS:
            b = g(df_detail, T4_SYMBOL_VERSION_MAP[method], ds)
            if len(b) == 0:
                row[method] = "—"
                continue
            p = sp_stats.wilcoxon(a, b).pvalue
            if p < 0.05:
                row[method] = "+" if np.nanmean(a) > np.nanmean(b) else "-"
            else:
                row[method] = "≈"
        rows.append(row)
    outpath = os.path.join(out_dir, "T4_symbols.csv")
    pd.DataFrame(rows).to_csv(outpath, index=False, encoding="utf-8-sig")
    print(f"  {outpath}")


# ═══ T5: 特征数 Mean ═══
def table_t5_features(df_summary, out_dir):
    print("T5: Feature count + Selection Ratio (14 methods x 20 datasets)...")
    all_ds = [d for d in MOFS_DATASETS if d in df_summary["Dataset"].unique()]
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]

    # Integer feature count
    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in versions:
            sub = df_summary[(df_summary["Version"] == v) & (df_summary["Dataset"] == ds)]
            if len(sub) > 0:
                feat = sub['Mean_Feat'].values[0]
                sr = sub['Mean_SR'].values[0] if 'Mean_SR' in sub.columns else 0
                row[V_LABELS[v]] = f"{feat:.0f} ({sr:.4f})"
            else:
                row[V_LABELS[v]] = "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T5_features.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")
    print(f"  {outpath}")


# ═══ T6: Wilcoxon Win/Total ═══
def table_t6_wilcoxon(df_summary, out_dir):
    print("T6: Wilcoxon Win/Total matrix...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    df_detail = load_merged_detail()
    versions = [v for v in ALL_VERSIONS if v in df_summary["Version"].unique()]
    n_v = len(versions)

    ds_sets = [set(df_detail[df_detail["Version"]==v]["Dataset"].unique()) for v in versions if v in df_detail["Version"].unique()]
    shared_ds = sorted(set.intersection(*ds_sets)) if ds_sets else []
    print(f"  Shared datasets: {len(shared_ds)}")

    win_matrix = np.zeros((n_v, n_v), dtype=int)
    total_matrix = np.zeros((n_v, n_v), dtype=int)

    for ds in shared_ds:
        for i, v1 in enumerate(versions):
            a1 = g(df_detail, v1, ds)
            if len(a1) < 3: continue
            for j, v2 in enumerate(versions):
                if i >= j: continue
                a2 = g(df_detail, v2, ds)
                if len(a2) < 3: continue
                try:
                    _, p = sp_stats.wilcoxon(a1, a2, alternative='greater') if len(a1)==len(a2) else \
                           sp_stats.mannwhitneyu(a1, a2, alternative='greater')
                except: continue
                total_matrix[i,j] += 1; total_matrix[j,i] += 1
                if p < 0.05 and np.mean(a1) > np.mean(a2): win_matrix[i,j] += 1
                elif p < 0.05 and np.mean(a2) > np.mean(a1): win_matrix[j,i] += 1

    table = []
    for i, v1 in enumerate(versions):
        row = {"Method": V_LABELS[v1]}
        for j, v2 in enumerate(versions):
            row[V_LABELS[v2]] = f"{int(win_matrix[i,j])}/{int(total_matrix[i,j])}" if i!=j and total_matrix[i,j]>0 else ("—" if i==j else "—")
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T6_wilcoxon.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")
    print(f"  {outpath}")


# ═══ T7: 消融实验 (4 变体 x 20 数据集) ═══
def table_t7_ablation(df_summary, out_dir):
    print("T7: Ablation study (4 variants: MEL -> MEL+MI -> KDS_EL_KER -> KDS_EL)...")

    # Load from respective sources
    dfs = []
    df2 = pd.read_csv(EXP2_DIR / "results_summary.csv")
    dfs.append(df2[df2["Version"] == "MEL"])
    df_mi = pd.read_csv(MEL_MI_DIR / "results_summary.csv")
    dfs.append(df_mi[df_mi["Version"] == "MEL_MI"])
    df_fin = pd.read_csv(FINAL_DIR / "results_summary.csv")
    dfs.append(df_fin[df_fin["Version"].isin(["KDS_EL_NoPool", "KDS_EL_TwoPhase"])])
    df_abl = pd.concat(dfs, ignore_index=True)

    all_ds = sorted(set.intersection(*[set(d["Dataset"].unique()) for d in dfs]))
    all_ds = [d for d in all_ds if d != "CNS"]
    # Use same 20 DS as main table
    all_ds = [d for d in MOFS_DATASETS if d in all_ds]
    print(f"  Ablation datasets: {len(all_ds)}")

    # Full table with Acc + Feat
    table = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in ABL_VERSIONS:
            sub = df_abl[(df_abl["Version"] == v) & (df_abl["Dataset"] == ds)]
            if len(sub) > 0:
                row[f"{V_LABELS[v]}_Acc"] = f"{sub['Mean_Acc'].values[0]:.4f}±{sub['Std_Acc'].values[0]:.4f}"
                row[f"{V_LABELS[v]}_Feat"] = f"{sub['Mean_Feat'].values[0]:.0f}"
            else:
                row[f"{V_LABELS[v]}_Acc"] = "—"
                row[f"{V_LABELS[v]}_Feat"] = "—"
        table.append(row)

    df_t = pd.DataFrame(table)
    outpath = os.path.join(out_dir, "T7_ablation.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")

    # Compact Acc-only for LaTeX
    compact = []
    for ds in all_ds:
        row = {"Dataset": ds}
        for v in ABL_VERSIONS:
            sub = df_abl[(df_abl["Version"] == v) & (df_abl["Dataset"] == ds)]
            row[V_LABELS[v]] = f"{sub['Mean_Acc'].values[0]:.4f}" if len(sub) > 0 else "—"
        compact.append(row)
    df_compact = pd.DataFrame(compact)
    compact_path = os.path.join(out_dir, "T7_ablation_acc_only.csv")
    df_compact.to_csv(compact_path, index=False, encoding="utf-8-sig")

    print(f"  {outpath}")
    print(f"  {compact_path}")


# ═══ T8: TwoPhase 消融逐数据集表 ═══
def table_t8_twophase_ablation(out_dir):
    print("T8: TwoPhase vs NoPool per-dataset ablation...")

    df_fin = pd.read_csv(FINAL_DIR / "results_summary.csv")
    all_ds = sorted(df_fin["Dataset"].unique())
    all_ds = [d for d in all_ds if d != "CNS"]

    table = []
    for ds in all_ds:
        np_sub = df_fin[(df_fin["Version"]=="KDS_EL_NoPool") & (df_fin["Dataset"]==ds)]
        tp_sub = df_fin[(df_fin["Version"]=="KDS_EL_TwoPhase") & (df_fin["Dataset"]==ds)]
        if len(np_sub) > 0 and len(tp_sub) > 0:
            d_acc = tp_sub["Mean_Acc"].values[0] - np_sub["Mean_Acc"].values[0]
            d_feat = tp_sub["Mean_Feat"].values[0] - np_sub["Mean_Feat"].values[0]
            result = "WIN" if d_acc > 0.001 else ("LOSE" if d_acc < -0.001 else "TIE")
            table.append({
                "Dataset": ds,
                "NoPool_Acc": f"{np_sub['Mean_Acc'].values[0]:.4f}",
                "TwoPhase_Acc": f"{tp_sub['Mean_Acc'].values[0]:.4f}",
                "ΔAcc": f"{d_acc:+.4f}",
                "NoPool_Feat": f"{np_sub['Mean_Feat'].values[0]:.0f}",
                "TwoPhase_Feat": f"{tp_sub['Mean_Feat'].values[0]:.0f}",
                "ΔFeat": f"{d_feat:+.0f}",
                "Result": result,
            })

    df_t = pd.DataFrame(table)
    df_t = df_t.sort_values("ΔAcc", ascending=False)
    outpath = os.path.join(out_dir, "T8_twophase_ablation.csv")
    df_t.to_csv(outpath, index=False, encoding="utf-8-sig")
    print(f"  {outpath}")

    # Summary stats
    deltas = [float(r["ΔAcc"]) for r in table]
    wins = sum(1 for d in deltas if d > 0.001)
    losses = sum(1 for d in deltas if d < -0.001)
    print(f"  Mean ΔAcc={np.mean(deltas):+.4f} | Wins={wins} Losses={losses} Ties={len(deltas)-wins-losses}")


# ═══ T6b: Holm-Bonferroni ═══
def table_holm_bonferroni(df_summary, out_dir):
    print("T6b: Holm-Bonferroni correction (KDS-EL Proposed vs all)...")
    if sp_stats is None:
        print("  [SKIP] scipy not available")
        return

    df_detail = load_merged_detail()
    kds_name = "KDS_EL_TwoPhase"
    others = [v for v in ALL_VERSIONS if v != kds_name and v in df_summary["Version"].unique()]

    ds_with_both = []
    for ds in sorted(df_summary["Dataset"].unique()):
        kds_data = df_detail[(df_detail["Version"]==kds_name)&(df_detail["Dataset"]==ds)]["Accuracy"].values
        if len(kds_data) < 3: continue
        if all(len(df_detail[(df_detail["Version"]==v)&(df_detail["Dataset"]==ds)]["Accuracy"].values) >= 3 for v in others):
            ds_with_both.append(ds)
    print(f"  Shared datasets: {len(ds_with_both)}")

    rows = []
    for v in others:
        diffs = []
        for ds in ds_with_both:
            kds_acc = df_detail[(df_detail["Version"]==kds_name)&(df_detail["Dataset"]==ds)]["Accuracy"].values
            o_acc = df_detail[(df_detail["Version"]==v)&(df_detail["Dataset"]==ds)]["Accuracy"].values
            try:
                _, p = sp_stats.wilcoxon(kds_acc, o_acc, alternative='greater') if len(kds_acc)==len(o_acc) else \
                       sp_stats.mannwhitneyu(kds_acc, o_acc, alternative='greater')
            except: continue
            diffs.append((ds, p, kds_acc.mean()-o_acc.mean()))
        if diffs:
            avg_diff = np.mean([d[2] for d in diffs])
            chi2 = -2*np.sum(np.log([max(d[1],1e-300) for d in diffs]))
            combined_p = 1 - sp_stats.chi2.cdf(chi2, 2*len(diffs))
            rows.append({
                "Method": V_LABELS[v],
                "Mean_ΔAcc": avg_diff,
                "Wins": sum(1 for d in diffs if d[2] > 0.001),
                "Ties": sum(1 for d in diffs if abs(d[2]) <= 0.001),
                "Losses": sum(1 for d in diffs if d[2] < -0.001),
                "Combined_p": combined_p,
            })

    rows.sort(key=lambda r: r["Combined_p"])
    m = len(rows)
    prev_adj = 0.0
    for i, r in enumerate(rows):
        r["Holm_alpha"] = 0.05 / (m - i)
        raw_p = float(r["Combined_p"])
        r["Adjusted_p"] = max(prev_adj, (m - i) * raw_p)
        prev_adj = r["Adjusted_p"]
        r["Reject_H0"] = "Yes" if r["Combined_p"] < r["Holm_alpha"] else "No"

    print(f"\n{'Method':20s} {'ΔAcc':>8s} {'W/T/L':>10s} {'Combined_p':>12s} {'Adjusted_p':>12s} {'α_holm':>10s} {'Reject?':>8s}")
    print("-" * 84)
    for r in rows:
        wtl = f"{r['Wins']}/{r['Ties']}/{r['Losses']}"
        print(f"  {r['Method']:18s} {r['Mean_ΔAcc']:+8.4f} {wtl:>10s} {r['Combined_p']:12.2e} {r['Adjusted_p']:12.2e} {r['Holm_alpha']:10.4f} {r['Reject_H0']:>8s}")

    outpath = os.path.join(out_dir, "T6b_holm_bonferroni.csv")
    pd.DataFrame(rows).to_csv(outpath, index=False, encoding="utf-8-sig")
    print(f"\n  {outpath}")


# ═══ Main ═══
def main():
    parser = argparse.ArgumentParser(description="KDS-EL Table Generator")
    parser.add_argument("--out", default=str(PROJ / "output" / "tables"))
    parser.add_argument("--tab", nargs="*", default=None,
                        help="Tables to generate: T4 T5 T6 T6b T7 T8")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("Loading summary data...")
    print(f"  SOTA:  {EXP1_DIR}")
    print(f"  MEL:   {EXP2_DIR}")
    print(f"  MOFS:  {EXP4_DIR}")
    print(f"  MEL+MI:{MEL_MI_DIR}")
    print(f"  Final: {FINAL_DIR}")
    df_summary = load_merged_summary()
    print(f"  {len(df_summary)} rows, {df_summary.Dataset.nunique()} datasets, {df_summary.Version.nunique()} versions")
    print(f"  Methods: {sorted(df_summary['Version'].unique())}")
    print(f"\nGenerating tables -> {args.out}\n")

    all_tabs = {
        "T4": table_t4_accuracy,
        "T4sym": table_t4_symbols,
        "T5": table_t5_features,
        "T6": table_t6_wilcoxon,
        "T6b": table_holm_bonferroni,
        "T7": table_t7_ablation,
        "T8": table_t8_twophase_ablation,
    }

    requested = args.tab if args.tab else list(all_tabs.keys())
    for key in requested:
        if key in all_tabs:
            try:
                if key == "T8":
                    all_tabs[key](args.out)
                elif key == "T4sym":
                    all_tabs[key](load_merged_detail(), args.out)
                else:
                    all_tabs[key](df_summary, args.out)
            except Exception as e:
                print(f"  [FAIL] {key}: {e}")
                import traceback
                traceback.print_exc()

    print(f"\nDone! Tables saved to: {args.out}")


if __name__ == "__main__":
    main()
