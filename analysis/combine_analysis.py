#!/usr/bin/env python3
"""
Combine results from two experiment directories and compute full statistics.
- formal_experiment_20260701_094943: External methods (BPSO, SaWDE, FWPSO, IGPSO, PSO_CSM) on 17 datasets
- formal_experiment_20260628_205157: KDS-EL variants (MEL, KDS-EL/DRS, KDS-EL/KER, KDS-EL) on 25 datasets
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import friedmanchisquare, wilcoxon
import warnings
warnings.filterwarnings('ignore')

# Load data
ext_df = pd.read_csv(r'F:\zym\KDS-EL\output\formal_experiment_20260701_094943\results_summary.csv')
kds_df = pd.read_csv(r'F:\zym\KDS-EL\output\formal_experiment_20260628_205157\results_summary.csv')

print("=" * 80)
print("EXPERIMENT DATA SUMMARY")
print("=" * 80)
print(f"\nExternal methods experiment (20260701): {ext_df['Version'].nunique()} methods × {ext_df['Dataset'].nunique()} datasets")
print(f"  Methods: {sorted(ext_df['Version'].unique())}")
print(f"  Datasets: {sorted(ext_df['Dataset'].unique())}")

print(f"\nKDS-EL variants experiment (20260628): {kds_df['Version'].nunique()} methods × {kds_df['Dataset'].nunique()} datasets")
print(f"  Methods: {sorted(kds_df['Version'].unique())}")
print(f"  Datasets: {sorted(kds_df['Dataset'].unique())}")

# Map KDS-EL method names to match paper naming
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
}
kds_df['Version'] = kds_df['Version'].map(name_map)
ext_df['Version'] = ext_df['Version'].map(name_map)

# Find common datasets
ext_datasets = set(ext_df['Dataset'].unique())
kds_datasets = set(kds_df['Dataset'].unique())
common = sorted(ext_datasets & kds_datasets)
print(f"\nCommon datasets ({len(common)}): {common}")

# Combine on common datasets
ext_common = ext_df[ext_df['Dataset'].isin(common)][['Version', 'Dataset', 'Mean_Acc', 'Std_Acc', 'Mean_Feat', 'Std_Feat', 'Mean_Time', 'Std_Time']]
kds_common = kds_df[kds_df['Dataset'].isin(common)][['Version', 'Dataset', 'Mean_Acc', 'Std_Acc', 'Mean_Feat', 'Std_Feat', 'Mean_Time', 'Std_Time']]
combined = pd.concat([ext_common, kds_common], ignore_index=True)

print(f"\nCombined: {combined['Version'].nunique()} methods × {len(common)} datasets")
print(f"  Methods: {sorted(combined['Version'].unique())}")

# ============================================================
# 1. Overall Average Accuracy per method
# ============================================================
print("\n" + "=" * 80)
print("1. OVERALL ACCURACY (mean across 17 datasets)")
print("=" * 80)
acc_by_method = combined.groupby('Version')['Mean_Acc'].agg(['mean', 'std']).sort_values('mean', ascending=False)
for method, row in acc_by_method.iterrows():
    print(f"  {method:25s}: {row['mean']:.4f} ± {row['std']:.4f}")

# ============================================================
# 2. Per-dataset Rankings (Friedman)
# ============================================================
print("\n" + "=" * 80)
print("2. PER-DATASET RANKINGS (for Friedman test)")
print("=" * 80)

methods_list = sorted(combined['Version'].unique())
rank_data = {}
for ds in common:
    ds_data = combined[combined['Dataset'] == ds].set_index('Version')
    accs = ds_data['Mean_Acc']
    ranks = accs.rank(ascending=False)
    for m in methods_list:
        if m not in rank_data:
            rank_data[m] = []
        rank_data[m].append(ranks.get(m, np.nan))

print(f"\n{'Method':<25s}", end='')
for ds in common:
    print(f"{ds:<12s}", end='')
print(f"{'AvgRank':>10s}")
for m in methods_list:
    print(f"{m:<25s}", end='')
    for r in rank_data[m]:
        if np.isnan(r):
            print(f"{'N/A':<12s}", end='')
        else:
            print(f"{r:<12.1f}", end='')
    avg = np.nanmean(rank_data[m])
    print(f"{avg:>10.3f}")

# Friedman test
print("\n--- Friedman Test ---")
# Build data matrix: rows=datasets, cols=methods
friedman_data = []
for ds in common:
    row = []
    for m in methods_list:
        val = combined[(combined['Dataset'] == ds) & (combined['Version'] == m)]['Mean_Acc']
        row.append(val.values[0] if len(val) > 0 else np.nan)
    friedman_data.append(row)
friedman_arr = np.array(friedman_data)

# Check for NaN
if np.any(np.isnan(friedman_arr)):
    print("WARNING: NaN values present, removing incomplete rows")
    valid_rows = ~np.any(np.isnan(friedman_arr), axis=1)
    friedman_arr = friedman_arr[valid_rows]
    print(f"Using {friedman_arr.shape[0]} complete datasets")

stat, p = friedmanchisquare(*[friedman_arr[:, i] for i in range(friedman_arr.shape[1])])
print(f"Friedman chi2 = {stat:.4f}")
print(f"Friedman p-value = {p:.2e}")
n_datasets = friedman_arr.shape[0]
n_methods = friedman_arr.shape[1]
print(f"n_datasets = {n_datasets}, n_methods = {n_methods}")

# Average ranks
avg_ranks = {m: np.mean(rank_data[m]) for m in methods_list}
sorted_ranks = sorted(avg_ranks.items(), key=lambda x: x[1])
print("\nAverage Ranks:")
for m, r in sorted_ranks:
    print(f"  {m:25s}: {r:.3f}")

# ============================================================
# 3. Head-to-head comparison: KDS-EL vs each method
# ============================================================
print("\n" + "=" * 80)
print("3. HEAD-TO-HEAD: KDS-EL (Proposed) vs each competitor")
print("=" * 80)

kds_name = 'KDS-EL (Proposed)'
for competitor in [m for m in methods_list if m != kds_name]:
    wins = 0
    losses = 0
    ties = 0
    sig_wins = 0
    print(f"\n  vs {competitor}:")
    for ds in common:
        kds_acc = combined[(combined['Dataset']==ds) & (combined['Version']==kds_name)]['Mean_Acc'].values
        comp_acc = combined[(combined['Dataset']==ds) & (combined['Version']==competitor)]['Mean_Acc'].values
        if len(kds_acc) == 0 or len(comp_acc) == 0:
            continue
        kds_acc = kds_acc[0]
        comp_acc = comp_acc[0]
        if kds_acc > comp_acc:
            wins += 1
        elif kds_acc < comp_acc:
            losses += 1
        else:
            ties += 1

    print(f"    Wins: {wins}/{len(common)}, Losses: {losses}/{len(common)}, Ties: {ties}/{len(common)}")

# ============================================================
# 4. Average Features
# ============================================================
print("\n" + "=" * 80)
print("4. AVERAGE FEATURES SELECTED")
print("=" * 80)
feat_by_method = combined.groupby('Version')['Mean_Feat'].agg(['mean', 'median']).sort_values('mean')
for method, row in feat_by_method.iterrows():
    print(f"  {method:25s}: mean={row['mean']:.1f}, median={row['median']:.1f}")

# KDS vs MEL feature reduction
mel_feat = feat_by_method.loc['MEL (Baseline)', 'mean'] if 'MEL (Baseline)' in feat_by_method.index else None
kds_feat = feat_by_method.loc['KDS-EL (Proposed)', 'mean'] if 'KDS-EL (Proposed)' in feat_by_method.index else None
if mel_feat and kds_feat:
    reduction = (mel_feat - kds_feat) / mel_feat * 100
    print(f"\n  KDS-EL vs MEL feature reduction: {reduction:.1f}%")

# Per-dataset feature reduction
print("\n  Per-dataset KDS-EL vs MEL feature reduction:")
for ds in common:
    kds_f = combined[(combined['Dataset']==ds) & (combined['Version']=='KDS-EL (Proposed)')]['Mean_Feat'].values
    mel_f = combined[(combined['Dataset']==ds) & (combined['Version']=='MEL (Baseline)')]['Mean_Feat'].values
    if len(kds_f) > 0 and len(mel_f) > 0:
        red = (mel_f[0] - kds_f[0]) / mel_f[0] * 100
        print(f"    {ds:15s}: MEL={mel_f[0]:.0f} → KDS-EL={kds_f[0]:.0f} ({red:+.1f}%)")

# ============================================================
# 5. Runtime Analysis
# ============================================================
print("\n" + "=" * 80)
print("5. RUNTIME ANALYSIS")
print("=" * 80)
time_by_method = combined.groupby('Version')['Mean_Time'].mean().sort_values()
for method, t in time_by_method.items():
    print(f"  {method:25s}: {t:.1f}s")

# ============================================================
# 6. Ablation: Synergy Analysis
# ============================================================
print("\n" + "=" * 80)
print("6. ABLATION / SYNERGY ANALYSIS")
print("=" * 80)

ablation_methods = ['MEL (Baseline)', 'KDS-EL/DRS', 'KDS-EL/KER', 'KDS-EL (Proposed)']
ablation_data = kds_df[kds_df['Dataset'].isin(common)][kds_df['Version'].isin(ablation_methods)]

# Synergy: delta_full vs delta_drs + delta_ker
positive_synergy = 0
negative_synergy = 0
print(f"\n{'Dataset':<15s} {'MEL(Base)':>10s} {'+DRS':>10s} {'+KER':>10s} {'Full':>10s} {'DRS+KER':>10s} {'Synergy':>10s}")
synergies = []
for ds in common:
    ds_data = ablation_data[ablation_data['Dataset'] == ds].set_index('Version')
    if len(ds_data) < 4:
        continue
    base = ds_data.loc['MEL (Baseline)', 'Mean_Acc']
    drs = ds_data.loc['KDS-EL/DRS', 'Mean_Acc']
    ker = ds_data.loc['KDS-EL/KER', 'Mean_Acc']
    full = ds_data.loc['KDS-EL (Proposed)', 'Mean_Acc']

    delta_drs = drs - base
    delta_ker = ker - base
    delta_full = full - base
    synergy = delta_full - (delta_drs + delta_ker)
    synergies.append(synergy)

    if synergy > 0:
        positive_synergy += 1
    else:
        negative_synergy += 1

    print(f"{ds:<15s} {base:.4f}     {drs:.4f} (+{delta_drs:+.4f})  {ker:.4f} (+{delta_ker:+.4f})  {full:.4f} (+{delta_full:+.4f})  {delta_drs+delta_ker:+.4f}  {synergy:+.4f}")

print(f"\nPositive synergy: {positive_synergy}/{len(synergies)}")
print(f"Negative synergy: {negative_synergy}/{len(synergies)}")
print(f"Mean synergy: {np.mean(synergies):+.4f}")

# ============================================================
# 7. Per-dataset feature counts (for the KDS-EL methods)
# ============================================================
print("\n" + "=" * 80)
print("7. KDS-EL FAMILY FEATURE COMPARISON")
print("=" * 80)
for ds in common:
    ds_data = kds_df[kds_df['Dataset'] == ds][kds_df['Version'].isin(ablation_methods)].set_index('Version')
    if len(ds_data) < 4:
        continue
    print(f"\n  {ds}:")
    for m in ablation_methods:
        if m in ds_data.index:
            row = ds_data.loc[m]
            print(f"    {m:20s}: acc={row['Mean_Acc']:.4f}, feat={row['Mean_Feat']:.0f}, time={row['Mean_Time']:.1f}s")

# ============================================================
# 8. NHD Analysis
# ============================================================
print("\n" + "=" * 80)
print("8. NHD / DIVERSITY ANALYSIS (KDS-EL variants only)")
print("=" * 80)
nhd_data = kds_df[kds_df['Dataset'].isin(common)][kds_df['Version'].isin(ablation_methods)]
nhd_by_method = nhd_data.groupby('Version')['Mean_NHD'].mean()
for method, nhd in nhd_by_method.items():
    print(f"  {method:25s}: mean NHD = {nhd:.4f}")

print("\n" + "=" * 80)
print("SUMMARY STATISTICS READY")
print("=" * 80)
