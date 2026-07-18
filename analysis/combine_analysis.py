#!/usr/bin/env python3
"""
Combine results from FOUR experiment directories and compute full statistics.
- formal_experiment_20260701_094943: SOTA methods (BPSO, SaWDE, FWPSO, IGPSO, PSO_CSM) on 20 datasets
- formal_experiment_20260628_205157: Ablation V1 (MEL only, valid) on 26 datasets
- formal_experiment_20260702_145828: Ablation V2 (KDS_EL, KDS_EL_DRS, KDS_EL_KER, bug-fixed) on 26 datasets
- formal_experiment_20260707_142018: MOFS methods (NSGA-II-FS, MOPSO-FS, MOEA-D-FS, fMOPSO-FS, VGS-MOEA, W-MOPSO-FS) on 20 datasets
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import friedmanchisquare, wilcoxon
from pathlib import Path
import sys
import io
import warnings
warnings.filterwarnings('ignore')

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJ = Path(__file__).resolve().parent.parent

# Load data from all 4 experiments
EXP1_DIR = PROJ / "output" / "formal_experiment_20260701_094943"   # SOTA
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # Ablation V1 (MEL only)
EXP3_DIR = PROJ / "output" / "formal_experiment_20260702_145828"   # Ablation V2 (KDS-EL variants)
EXP4_DIR = PROJ / "output" / "formal_experiment_20260707_142018"   # MOFS

exp1_df = pd.read_csv(EXP1_DIR / "results_summary.csv")  # SOTA: 5 methods
exp2_df = pd.read_csv(EXP2_DIR / "results_summary.csv")  # Ablation V1: MEL only
exp3_df = pd.read_csv(EXP3_DIR / "results_summary.csv")  # Ablation V2: KDS_EL/DRS/KER
exp4_df = pd.read_csv(EXP4_DIR / "results_summary.csv")  # MOFS: 6 methods

# Map method names to paper naming
name_map = {
    'MEL': 'MEL (Baseline)',
    'KDS_EL_DRS': 'KDS-EL/DRS',
    'KDS_EL_KER': 'KDS-EL/KER',
    'KDS_EL': 'KDS-EL (Proposed)',
    'BPSO': 'BPSO',
    'SaWDE': 'SaWDE',
    'FWPSO': 'FWPSO',
    'IGPSO': 'IGPSO',
    'PSO_CSM': 'PSO-CSM',
    'NSGA-II-FS': 'NSGA-II-FS',
    'MOPSO-FS': 'MOPSO-FS',
    'MOEA-D-FS': 'MOEA-D-FS',
    'fMOPSO-FS': 'fMOPSO-FS',
    'VGS-MOEA': 'VGS-MOEA',
    'W-MOPSO-FS': 'W-MOPSO-FS',
}

# Apply name mapping
for df in [exp1_df, exp2_df, exp3_df, exp4_df]:
    df['Version'] = df['Version'].map(name_map)

# Build merged: each method from its valid source
# SOTA methods from Exp1
sota_methods = ['BPSO', 'SaWDE', 'FWPSO', 'IGPSO', 'PSO-CSM']
sota_data = exp1_df[exp1_df['Version'].isin(sota_methods)]

# MEL from Exp2
mel_data = exp2_df[exp2_df['Version'] == 'MEL (Baseline)']

# KDS-EL variants from Exp3
kds_methods = ['KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)']
kds_data = exp3_df[exp3_df['Version'].isin(kds_methods)]

# MOFS methods from Exp4
mofs_methods = ['NSGA-II-FS', 'MOPSO-FS', 'MOEA-D-FS', 'fMOPSO-FS', 'VGS-MOEA', 'W-MOPSO-FS']
mofs_data = exp4_df[exp4_df['Version'].isin(mofs_methods)]

# Merge all
common_cols = ['Version', 'Dataset', 'Mean_Acc', 'Std_Acc', 'Mean_Feat', 'Std_Feat', 'Mean_Time', 'Std_Time']
all_data = pd.concat([sota_data[common_cols], mel_data[common_cols],
                       kds_data[common_cols], mofs_data[common_cols]], ignore_index=True)

print("=" * 80)
print("EXPERIMENT DATA SUMMARY (4 directories)")
print("=" * 80)
print(f"  Exp1 (SOTA):    {exp1_df['Version'].nunique()} methods × {exp1_df['Dataset'].nunique()} datasets")
print(f"  Exp2 (Abl V1):  {exp2_df['Version'].nunique()} methods × {exp2_df['Dataset'].nunique()} datasets")
print(f"  Exp3 (Abl V2):  {exp3_df['Version'].nunique()} methods × {exp3_df['Dataset'].nunique()} datasets")
print(f"  Exp4 (MOFS):    {exp4_df['Version'].nunique()} methods × {exp4_df['Dataset'].nunique()} datasets")
print(f"\n  Merged: {all_data['Version'].nunique()} methods × {all_data['Dataset'].nunique()} datasets")

# Find common datasets across ALL methods
all_methods_list = sorted(all_data['Version'].unique())
ds_sets = []
for m in all_methods_list:
    ds = set(all_data[all_data['Version'] == m]['Dataset'].unique())
    if ds:
        ds_sets.append(ds)
common = sorted(set.intersection(*ds_sets))
print(f"  Common datasets (all {len(all_methods_list)} methods): {len(common)}")
print(f"  Method list: {all_methods_list}")

# Filter to common datasets
combined = all_data[all_data['Dataset'].isin(common)]

# ============================================================
# 1. Overall Average Accuracy per method (15 methods)
# ============================================================
print("\n" + "=" * 80)
print(f"1. OVERALL ACCURACY (mean across {len(common)} datasets, 15 methods)")
print("=" * 80)
acc_by_method = combined.groupby('Version')['Mean_Acc'].agg(['mean', 'std']).sort_values('mean', ascending=False)
for i, (method, row) in enumerate(acc_by_method.iterrows()):
    medal = ['[1]','[2]','[3]'][i] if i < 3 else f'[{i+1}]'
    print(f"  {medal} {method:25s}: {row['mean']:.4f} ± {row['std']:.4f}")

# ============================================================
# 2. Per-dataset Rankings (Friedman) — 9 SOTA + ablation methods
# ============================================================
print("\n" + "=" * 80)
print("2. FRIEDMAN RANKINGS (9 methods: SOTA + KDS-EL family, excluding MOFS)")
print("=" * 80)

# Friedman on the 9 core methods (SOTA + ablation, excluding MOFS)
friedman_methods = ['BPSO', 'SaWDE', 'FWPSO', 'IGPSO', 'PSO-CSM',
                    'MEL (Baseline)', 'KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)']
friedman_methods = [m for m in friedman_methods if m in combined['Version'].unique()]

rank_data = {}
for ds in common:
    ds_data = combined[combined['Dataset'] == ds].set_index('Version')
    accs = ds_data['Mean_Acc']
    ranks = accs.rank(ascending=False)
    for m in friedman_methods:
        if m not in rank_data:
            rank_data[m] = []
        rank_data[m].append(ranks.get(m, np.nan))

print(f"\n{'Method':<25s} {'AvgRank':>10s}")
sorted_ranks = sorted(rank_data.items(), key=lambda x: np.nanmean(x[1]))
for m, ranks in sorted_ranks:
    avg = np.nanmean(ranks)
    print(f"  {m:<25s}: {avg:.3f}")

# Friedman test
friedman_arr = []
for ds in common:
    row = []
    for m in friedman_methods:
        val = combined[(combined['Dataset'] == ds) & (combined['Version'] == m)]['Mean_Acc']
        row.append(val.values[0] if len(val) > 0 else np.nan)
    friedman_arr.append(row)
friedman_arr = np.array(friedman_arr)
if np.any(np.isnan(friedman_arr)):
    valid_rows = ~np.any(np.isnan(friedman_arr), axis=1)
    friedman_arr = friedman_arr[valid_rows]
    print(f"  (using {friedman_arr.shape[0]} complete datasets)")

stat, p = friedmanchisquare(*[friedman_arr[:, i] for i in range(friedman_arr.shape[1])])
print(f"\n  Friedman chi2 = {stat:.4f}")
print(f"  Friedman p-value = {p:.2e}")
print(f"  n_datasets = {friedman_arr.shape[0]}, n_methods = {friedman_arr.shape[1]}")

# ============================================================
# 3. Head-to-head: KDS-EL vs each method
# ============================================================
print("\n" + "=" * 80)
print("3. HEAD-TO-HEAD: KDS-EL (Proposed) vs ALL 14 competitors")
print("=" * 80)

kds_name = 'KDS-EL (Proposed)'
all_competitors = [m for m in all_methods_list if m != kds_name]

# Category labels
CATEGORIES = {
    'BPSO': 'SOTA', 'SaWDE': 'SOTA', 'FWPSO': 'SOTA', 'IGPSO': 'SOTA', 'PSO-CSM': 'SOTA',
    'MEL (Baseline)': 'Ablation', 'KDS-EL/DRS': 'Ablation', 'KDS-EL/KER': 'Ablation',
    'NSGA-II-FS': 'MOFS-Classic', 'MOPSO-FS': 'MOFS-Classic', 'MOEA-D-FS': 'MOFS-Classic',
    'fMOPSO-FS': 'MOFS-Hybrid', 'VGS-MOEA': 'MOFS-Variable', 'W-MOPSO-FS': 'MOFS-Hybrid',
}

for competitor in sorted(all_competitors):
    wins = losses = ties = 0
    acc_diffs = []
    for ds in common:
        kds_acc = combined[(combined['Dataset']==ds) & (combined['Version']==kds_name)]['Mean_Acc'].values
        comp_acc = combined[(combined['Dataset']==ds) & (combined['Version']==competitor)]['Mean_Acc'].values
        if len(kds_acc) == 0 or len(comp_acc) == 0:
            continue
        diff = kds_acc[0] - comp_acc[0]
        acc_diffs.append(diff)
        if diff > 0.001:
            wins += 1
        elif diff < -0.001:
            losses += 1
        else:
            ties += 1
    cat = CATEGORIES.get(competitor, 'Unknown')
    win_rate = wins / len(acc_diffs) * 100 if acc_diffs else 0
    mean_diff = np.mean(acc_diffs) if acc_diffs else 0
    print(f"  vs {competitor:25s} [{cat:15s}]: {wins:2d}W/{ties:1d}T/{losses:2d}L  ({win_rate:5.1f}%)  ΔAcc={mean_diff:+.4f}")

# ============================================================
# 4. Average Features (15 methods)
# ============================================================
print("\n" + "=" * 80)
print("4. AVERAGE FEATURES SELECTED (15 methods)")
print("=" * 80)
feat_by_method = combined.groupby('Version')['Mean_Feat'].agg(['mean', 'median']).sort_values('mean')
for method, row in feat_by_method.iterrows():
    print(f"  {method:25s}: mean={row['mean']:.0f}, median={row['median']:.0f}")

# Feature reduction vs MEL
mel_feat = feat_by_method.loc['MEL (Baseline)', 'mean'] if 'MEL (Baseline)' in feat_by_method.index else None
kds_feat = feat_by_method.loc['KDS-EL (Proposed)', 'mean'] if 'KDS-EL (Proposed)' in feat_by_method.index else None
if mel_feat and kds_feat:
    reduction = (mel_feat - kds_feat) / mel_feat * 100
    print(f"\n  KDS-EL vs MEL feature reduction: {reduction:.1f}% ({mel_feat:.0f} → {kds_feat:.0f})")

# ============================================================
# 5. Runtime Analysis (15 methods)
# ============================================================
print("\n" + "=" * 80)
print("5. RUNTIME ANALYSIS (15 methods)")
print("=" * 80)
time_by_method = combined.groupby('Version')['Mean_Time'].mean().sort_values()
for method, t in time_by_method.items():
    print(f"  {method:25s}: {t:.1f}s")

# ============================================================
# 6. Ablation: Synergy Analysis (26 datasets)
# ============================================================
print("\n" + "=" * 80)
print("6. ABLATION / SYNERGY ANALYSIS (26 datasets)")
print("=" * 80)

ablation_methods = ['MEL (Baseline)', 'KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)']
# IMPORTANT: MEL from Exp2 only; KDS variants from Exp3 only (Exp2 KDS variants are buggy old runs)
ablation_data = pd.concat([
    exp2_df[(exp2_df['Version'] == 'MEL (Baseline)')],
    exp3_df[exp3_df['Version'].isin(['KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)'])]
], ignore_index=True)
ablation_common = sorted(set(exp2_df['Dataset'].unique()) & set(exp3_df['Dataset'].unique()))
print(f"  Ablation datasets: {len(ablation_common)} (Exp2 ∩ Exp3)")

positive_synergy = 0
negative_synergy = 0
synergies = []
ceiling_ds = []

for ds in ablation_common:
    ds_data = ablation_data[ablation_data['Dataset'] == ds]
    if ds_data['Version'].nunique() < 4:
        continue
    # Get scalar values safely via groupby-first
    base = ds_data[ds_data['Version'] == 'MEL (Baseline)']['Mean_Acc'].values[0]
    drs = ds_data[ds_data['Version'] == 'KDS-EL/DRS']['Mean_Acc'].values[0]
    ker = ds_data[ds_data['Version'] == 'KDS-EL/KER']['Mean_Acc'].values[0]
    full = ds_data[ds_data['Version'] == 'KDS-EL (Proposed)']['Mean_Acc'].values[0]

    delta_drs = drs - base
    delta_ker = ker - base
    delta_full = full - base
    synergy = delta_full - (delta_drs + delta_ker)
    synergies.append(synergy)

    if synergy > 0.001:
        positive_synergy += 1
    else:
        negative_synergy += 1

    # Flag ceiling effects
    if max(drs, ker) > 0.99:
        ceiling_ds.append(ds)

print(f"\n  Positive synergy: {positive_synergy}/{len(synergies)} ({positive_synergy/len(synergies)*100:.1f}%)")
print(f"  Negative synergy: {negative_synergy}/{len(synergies)}")
print(f"  Mean synergy: {np.mean(synergies):+.4f}")
print(f"  Ceiling effect datasets (max module Acc > 0.99): {len(ceiling_ds)}/{len(synergies)}")

if ceiling_ds:
    print(f"    → {', '.join(ceiling_ds)}")

# ============================================================
# 7. MOFS Generation Gap Analysis
# ============================================================
print("\n" + "=" * 80)
print("7. MOFS GENERATION GAP ANALYSIS")
print("=" * 80)

mofs_gen_map = {
    'NSGA-II-FS': 'Classic (2002-2007)',
    'MOPSO-FS': 'Classic (2002-2007)',
    'MOEA-D-FS': 'Classic (2002-2007)',
    'fMOPSO-FS': 'Hybrid (recent)',
    'W-MOPSO-FS': 'Hybrid (recent)',
    'VGS-MOEA': 'Variable-length (2021)',
}

for gen_label in ['Classic (2002-2007)', 'Hybrid (recent)', 'Variable-length (2021)']:
    methods_in_gen = [m for m, g in mofs_gen_map.items() if g == gen_label]
    gen_data = combined[combined['Version'].isin(methods_in_gen)]
    if len(gen_data) > 0:
        avg_acc = gen_data.groupby('Version')['Mean_Acc'].mean().mean()
        avg_feat = gen_data.groupby('Version')['Mean_Feat'].mean().mean()
        print(f"  {gen_label:30s}: Acc={avg_acc:.4f}, Feat={avg_feat:.0f}  ({', '.join(methods_in_gen)})")

# ============================================================
# 8. NHD Analysis
# ============================================================
print("\n" + "=" * 80)
print("8. NHD / DIVERSITY ANALYSIS")
print("=" * 80)

if 'Mean_NHD' in exp3_df.columns:
    nhd_data = exp3_df[exp3_df['Dataset'].isin(ablation_common)]
    # Also include MEL from Exp2
    if 'Mean_NHD' in exp2_df.columns:
        nhd_mel = exp2_df[(exp2_df['Version'] == 'MEL (Baseline)') &
                          (exp2_df['Dataset'].isin(ablation_common))]
        nhd_data = pd.concat([nhd_data, nhd_mel], ignore_index=True)

    nhd_by_method = nhd_data.groupby('Version')['Mean_NHD'].mean()
    for method, nhd in nhd_by_method.items():
        print(f"  {method:25s}: mean NHD = {nhd:.4f}")
else:
    print("  (NHD data not available in summary CSVs — use detail CSVs for per-run NHD)")

# ============================================================
# 9. Category-level summary
# ============================================================
print("\n" + "=" * 80)
print("9. CATEGORY-LEVEL SUMMARY")
print("=" * 80)

cat_map = {
    'KDS-EL (Proposed)': 'KDS-EL Family',
    'KDS-EL/DRS': 'KDS-EL Family',
    'KDS-EL/KER': 'KDS-EL Family',
    'BPSO': 'SOTA Single-obj',
    'SaWDE': 'SOTA Single-obj',
    'FWPSO': 'SOTA Single-obj',
    'IGPSO': 'SOTA Single-obj',
    'PSO-CSM': 'SOTA Single-obj',
    'MEL (Baseline)': 'SOTA Single-obj',
    'NSGA-II-FS': 'MOFS Classic',
    'MOPSO-FS': 'MOFS Classic',
    'MOEA-D-FS': 'MOFS Classic',
    'fMOPSO-FS': 'MOFS Advanced',
    'W-MOPSO-FS': 'MOFS Advanced',
    'VGS-MOEA': 'MOFS Advanced',
}

combined['Category'] = combined['Version'].map(cat_map)
cat_summary = combined.groupby('Category').agg(
    Avg_Acc=('Mean_Acc', 'mean'),
    Avg_Feat=('Mean_Feat', 'mean'),
    Avg_Time=('Mean_Time', 'mean'),
    Count=('Version', 'nunique'),
).sort_values('Avg_Acc', ascending=False)

for cat, row in cat_summary.iterrows():
    print(f"  {cat:20s}: Acc={row['Avg_Acc']:.4f}, Feat={row['Avg_Feat']:.0f}, "
          f"Time={row['Avg_Time']:.1f}s, Methods={int(row['Count'])}")

# ============================================================
# 10. KER-ONLY vs FULL — PAIRED WILCOXON (per-run, per-dataset)
# ============================================================
print("\n" + "=" * 80)
print("10. KER-ONLY vs FULL PAIRED WILCOXON (per-dataset, per-run)")
print("=" * 80)

# Load per-run detail data for KER and Full
exp3_detail = pd.read_csv(EXP3_DIR / "results_detail.csv")
ker_detail = exp3_detail[exp3_detail['Version'] == 'KDS_EL_KER']
full_detail = exp3_detail[exp3_detail['Version'] == 'KDS_EL']

abl_ds_ker_full = sorted(set(ker_detail['Dataset'].unique()) & set(full_detail['Dataset'].unique()))
print(f"  Datasets with both KER and Full per-run data: {len(abl_ds_ker_full)}")

wilc_results = []
for ds in abl_ds_ker_full:
    ker_acc = ker_detail[ker_detail['Dataset'] == ds]['Accuracy'].values
    full_acc = full_detail[full_detail['Dataset'] == ds]['Accuracy'].values
    if len(ker_acc) < 3 or len(full_acc) < 3:
        continue
    try:
        if len(ker_acc) == len(full_acc):
            _, p = wilcoxon(full_acc, ker_acc, alternative='two-sided')
        else:
            _, p = stats.mannwhitneyu(full_acc, ker_acc, alternative='two-sided')
    except Exception:
        p = np.nan
    mean_diff = full_acc.mean() - ker_acc.mean()
    wilc_results.append({
        'Dataset': ds, 'KER_mean': ker_acc.mean(), 'Full_mean': full_acc.mean(),
        'dAcc': mean_diff, 'p_value': p,
        'significant_05': p < 0.05 if not np.isnan(p) else False,
        'Full_better': mean_diff > 0,
    })

df_wilc = pd.DataFrame(wilc_results)
n_sig = df_wilc['significant_05'].sum()
n_full_better = df_wilc['Full_better'].sum()
mean_dacc = df_wilc['dAcc'].mean()

print(f"\n  Datasets with p<0.05: {n_sig}/{len(df_wilc)}")
print(f"  Datasets where Full > KER: {n_full_better}/{len(df_wilc)}")
print(f"  Mean dAcc (Full - KER): {mean_dacc:+.4f}")

# Fisher's combined test
valid_ps = df_wilc['p_value'].dropna().values
if len(valid_ps) > 0:
    chi2 = -2 * np.sum(np.log(np.maximum(valid_ps, 1e-300)))
    combined_p = 1 - stats.chi2.cdf(chi2, 2 * len(valid_ps))
    print(f"  Fisher's combined p-value: {combined_p:.4e}")
    print(f"  --> {'SIGNIFICANT' if combined_p < 0.05 else 'NOT SIGNIFICANT'} at alpha=0.05")

# Per-dataset detail
print(f"\n  {'Dataset':<15s} {'KER':>8s} {'Full':>8s} {'dAcc':>8s} {'p':>10s} {'p<0.05':>8s}")
print("  " + "-" * 60)
for _, r in df_wilc.sort_values('p_value').iterrows():
    print(f"  {r['Dataset']:<13s} {r['KER_mean']:8.4f} {r['Full_mean']:8.4f} {r['dAcc']:+8.4f} {r['p_value']:10.4f} {str(r['significant_05']):>8s}")

# ============================================================
# 11. CEILING-FILTERED SYNERGY (Acc<0.95 subset)
# ============================================================
print("\n" + "=" * 80)
print("11. CEILING-FILTERED ABLATION ANALYSIS (Non-saturated subset)")
print("=" * 80)

# Reconstruct ablation data for 25 datasets
ablation_methods_25 = ['MEL (Baseline)', 'KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)']
abl_data_25 = pd.concat([
    exp2_df[(exp2_df['Version'] == 'MEL (Baseline)')],
    exp3_df[exp3_df['Version'].isin(['KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)'])]
], ignore_index=True)
abl_common_25 = sorted(set(exp2_df['Dataset'].unique()) & set(exp3_df['Dataset'].unique()))

# Build per-dataset ablation table
abl_rows = []
for ds in abl_common_25:
    ds_data = abl_data_25[abl_data_25['Dataset'] == ds]
    if ds_data['Version'].nunique() < 4:
        continue
    try:
        base = ds_data[ds_data['Version'] == 'MEL (Baseline)']['Mean_Acc'].values[0]
        drs = ds_data[ds_data['Version'] == 'KDS-EL/DRS']['Mean_Acc'].values[0]
        ker = ds_data[ds_data['Version'] == 'KDS-EL/KER']['Mean_Acc'].values[0]
        full = ds_data[ds_data['Version'] == 'KDS-EL (Proposed)']['Mean_Acc'].values[0]
        abl_rows.append({
            'Dataset': ds, 'MEL': base, 'DRS': drs, 'KER': ker, 'Full': full,
            'dDRS': drs-base, 'dKER': ker-base, 'dFull': full-base,
            'Synergy': (full-base) - ((drs-base) + (ker-base)),
            'BestAcc': max(drs, ker, full),
        })
    except (KeyError, IndexError):
        continue

df_abl = pd.DataFrame(abl_rows)
non_sat = df_abl[df_abl['BestAcc'] < 0.95]
sat = df_abl[df_abl['BestAcc'] >= 0.95]

print(f"  Non-saturated (Acc<0.95): {len(non_sat)} datasets")
print(f"    {list(non_sat['Dataset'].values)}")
print(f"  Saturated (Acc>=0.95): {len(sat)} datasets")

for label, subset in [("ALL (25DS)", df_abl), ("NON-SAT (Acc<0.95)", non_sat), ("SAT (Acc>=0.95)", sat)]:
    print(f"\n  --- {label} ---")
    print(f"    dDRS={subset['dDRS'].mean():+.4f}, dKER={subset['dKER'].mean():+.4f}, dFull={subset['dFull'].mean():+.4f}")
    print(f"    Synergy={subset['Synergy'].mean():+.4f}, Positive={(subset['Synergy']>0).sum()}/{len(subset)}")

# ============================================================
# 12. VGS-MOEA vs KDS-EL STABILITY COMPARISON
# ============================================================
print("\n" + "=" * 80)
print("12. KDS-EL vs VGS-MOEA STABILITY (per-dataset Std_Acc)")
print("=" * 80)

kds_20 = combined[(combined['Version'] == 'KDS-EL (Proposed)') & (combined['Dataset'].isin(common))]
vgs_20 = combined[(combined['Version'] == 'VGS-MOEA') & (combined['Dataset'].isin(common))]

kds_std_mean = kds_20['Std_Acc'].mean()
vgs_std_mean = vgs_20['Std_Acc'].mean()

kds_better = 0
vgs_better = 0
for ds in common:
    kds_s = kds_20[kds_20['Dataset']==ds]['Std_Acc'].values
    vgs_s = vgs_20[vgs_20['Dataset']==ds]['Std_Acc'].values
    if len(kds_s) > 0 and len(vgs_s) > 0:
        if kds_s[0] < vgs_s[0]:
            kds_better += 1
        else:
            vgs_better += 1

print(f"  KDS-EL mean Std: {kds_std_mean:.4f}")
print(f"  VGS-MOEA mean Std: {vgs_std_mean:.4f}")
print(f"  KDS-EL more stable on: {kds_better}/{len(common)} datasets")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
