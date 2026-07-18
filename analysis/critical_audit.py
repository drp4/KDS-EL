#!/usr/bin/env python3
"""
CRITICAL ANALYSIS: Verify synergy, KER-only vs Full Wilcoxon, ceiling-filtered analysis.
Addresses C1, C2, C3 from the audit.
"""
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import wilcoxon
from pathlib import Path
import sys
import io
import warnings
warnings.filterwarnings('ignore')

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PROJ = Path(__file__).resolve().parent.parent

# Load summary data
EXP2_DIR = PROJ / "output" / "formal_experiment_20260628_205157"   # MEL
EXP3_DIR = PROJ / "output" / "formal_experiment_20260702_145828"   # KDS-EL variants

exp2_df = pd.read_csv(EXP2_DIR / "results_summary.csv")
exp3_df = pd.read_csv(EXP3_DIR / "results_summary.csv")

# Load detail (per-run) data for Wilcoxon
exp2_detail = pd.read_csv(EXP2_DIR / "results_detail.csv")
exp3_detail = pd.read_csv(EXP3_DIR / "results_detail.csv")

# --- Ablation datasets ---
abl_ds = sorted(set(exp2_df['Dataset'].unique()) & set(exp3_df['Dataset'].unique()))
print(f"Ablation datasets (Exp2 & Exp3): {len(abl_ds)}")
print(f"Datasets: {abl_ds}")

# --- Filter to ablation variants ---
mel_sum = exp2_df[exp2_df['Version'] == 'MEL'].set_index('Dataset')
kds_sum = exp3_df[exp3_df['Version'] == 'KDS_EL'].set_index('Dataset')
drs_sum = exp3_df[exp3_df['Version'] == 'KDS_EL_DRS'].set_index('Dataset')
ker_sum = exp3_df[exp3_df['Version'] == 'KDS_EL_KER'].set_index('Dataset')

# ======================================================================
# 1. VERIFY SYNERGY NUMBERS (25 datasets)
# ======================================================================
print("\n" + "=" * 80)
print("1. SYNERGY VERIFICATION (25 datasets)")
print("=" * 80)

synergies = []
positive_syn = 0
ceiling_ds = []
all_results = []

for ds in abl_ds:
    if ds not in mel_sum.index or ds not in kds_sum.index:
        continue
    if ds not in drs_sum.index or ds not in ker_sum.index:
        continue

    base = mel_sum.loc[ds, 'Mean_Acc']
    drs = drs_sum.loc[ds, 'Mean_Acc']
    ker = ker_sum.loc[ds, 'Mean_Acc']
    full = kds_sum.loc[ds, 'Mean_Acc']

    delta_drs = drs - base
    delta_ker = ker - base
    delta_full = full - base
    synergy = delta_full - (delta_drs + delta_ker)
    synergies.append(synergy)

    if synergy > 0.0:
        positive_syn += 1

    is_ceiling = max(drs, ker, full) > 0.99
    if is_ceiling:
        ceiling_ds.append(ds)

    all_results.append({
        'Dataset': ds, 'MEL': base, 'DRS': drs, 'KER': ker, 'Full': full,
        'dDRS': delta_drs, 'dKER': delta_ker, 'dFull': delta_full,
        'Synergy': synergy, 'Ceiling': is_ceiling,
        'DRS_vs_KER': drs - ker,
    })

df_syn = pd.DataFrame(all_results)
print(f"\n  Mean dDRS  = {df_syn['dDRS'].mean():+.4f}")
print(f"  Mean dKER  = {df_syn['dKER'].mean():+.4f}")
print(f"  Mean dFull = {df_syn['dFull'].mean():+.4f}")
print(f"  Mean Synergy = {df_syn['Synergy'].mean():+.4f}")
print(f"  Positive synergy: {positive_syn}/{len(synergies)} ({positive_syn/len(synergies)*100:.1f}%)")
print(f"  Ceiling datasets (Acc>0.99): {len(ceiling_ds)}/{len(synergies)}")
print(f"    -> {ceiling_ds}")

# Per-dataset synergy
print(f"\n{'Dataset':<15s} {'dDRS':>8s} {'dKER':>8s} {'dFull':>8s} {'Synergy':>8s} {'Ceiling':>8s}")
print("-" * 60)
for _, r in df_syn.sort_values('Synergy').iterrows():
    flag = "[CEIL]" if r['Ceiling'] else ""
    print(f"  {r['Dataset']:<13s} {r['dDRS']:+8.4f} {r['dKER']:+8.4f} {r['dFull']:+8.4f} {r['Synergy']:+8.4f} {flag:>8s}")

# ======================================================================
# 2. KER-ONLY vs FULL -- PAIRED WILCOXON (per-dataset, per-run)
# ======================================================================
print("\n" + "=" * 80)
print("2. KER-ONLY vs FULL -- PER-DATASET PAIRED WILCOXON")
print("=" * 80)

ker_detail = exp3_detail[exp3_detail['Version'] == 'KDS_EL_KER']
full_detail = exp3_detail[exp3_detail['Version'] == 'KDS_EL']

wilcoxon_results = []
for ds in abl_ds:
    ker_acc = ker_detail[ker_detail['Dataset'] == ds]['Accuracy'].values
    full_acc = full_detail[full_detail['Dataset'] == ds]['Accuracy'].values

    if len(ker_acc) < 3 or len(full_acc) < 3:
        continue

    # Paired Wilcoxon (same dataset, same run indices)
    if len(ker_acc) == len(full_acc):
        try:
            stat, p = wilcoxon(full_acc, ker_acc, alternative='two-sided')
        except Exception:
            stat, p = np.nan, np.nan
    else:
        # Fallback to Mann-Whitney
        try:
            stat, p = stats.mannwhitneyu(full_acc, ker_acc, alternative='two-sided')
        except Exception:
            stat, p = np.nan, np.nan

    mean_diff = full_acc.mean() - ker_acc.mean()
    wilcoxon_results.append({
        'Dataset': ds,
        'KER_mean': ker_acc.mean(),
        'Full_mean': full_acc.mean(),
        'dAcc': mean_diff,
        'p_value': p,
        'significant_05': p < 0.05 if not np.isnan(p) else False,
        'Full_better': mean_diff > 0,
    })

df_wilc = pd.DataFrame(wilcoxon_results)
print(f"\n{'Dataset':<15s} {'KER':>8s} {'Full':>8s} {'dAcc':>8s} {'p':>10s} {'p<0.05':>8s} {'Full>KER':>10s}")
print("-" * 70)
for _, r in df_wilc.sort_values('p_value').iterrows():
    print(f"  {r['Dataset']:<13s} {r['KER_mean']:8.4f} {r['Full_mean']:8.4f} {r['dAcc']:+8.4f} {r['p_value']:10.4f} "
          f"{str(r['significant_05']):>8s} {str(r['Full_better']):>10s}")

# Summary
n_sig = df_wilc['significant_05'].sum()
n_full_better = df_wilc['Full_better'].sum()
print(f"\n  Datasets with p<0.05: {n_sig}/{len(df_wilc)}")
print(f"  Datasets where Full > KER: {n_full_better}/{len(df_wilc)}")
print(f"  Mean dAcc (Full - KER): {df_wilc['dAcc'].mean():+.4f}")

# Combined test: Fisher's method
valid_ps = df_wilc['p_value'].dropna().values
if len(valid_ps) > 0:
    chi2 = -2 * np.sum(np.log(np.maximum(valid_ps, 1e-300)))
    combined_p = 1 - stats.chi2.cdf(chi2, 2 * len(valid_ps))
    print(f"  Fisher's combined p-value: {combined_p:.4e}")
    print(f"  --> {'SIGNIFICANT' if combined_p < 0.05 else 'NOT SIGNIFICANT'} at alpha=0.05")

# ======================================================================
# 3. CEILING-FILTERED ANALYSIS (Acc < 0.95 subset)
# ======================================================================
print("\n" + "=" * 80)
print("3. CEILING-FILTERED ANALYSIS (Non-saturated: best variant Acc < 0.95)")
print("=" * 80)

# A dataset is "non-saturated" if the best variant's accuracy < 0.95
non_sat = df_syn[df_syn[['DRS', 'KER', 'Full']].max(axis=1) < 0.95]
sat = df_syn[df_syn[['DRS', 'KER', 'Full']].max(axis=1) >= 0.95]

print(f"\n  Non-saturated datasets (best Acc<0.95): {len(non_sat)}")
print(f"    {list(non_sat['Dataset'].values)}")
print(f"  Saturated datasets (best Acc>=0.95): {len(sat)}")
print(f"    {list(sat['Dataset'].values)}")

for label, subset in [("ALL (25 DS)", df_syn), ("NON-SATURATED (Acc<0.95)", non_sat), ("SATURATED (Acc>=0.95)", sat)]:
    if len(subset) == 0:
        continue
    print(f"\n  --- {label} ---")
    print(f"  Mean dDRS  = {subset['dDRS'].mean():+.4f}")
    print(f"  Mean dKER  = {subset['dKER'].mean():+.4f}")
    print(f"  Mean dFull = {subset['dFull'].mean():+.4f}")
    print(f"  Mean Synergy = {subset['Synergy'].mean():+.4f}")
    pos = (subset['Synergy'] > 0).sum()
    print(f"  Positive synergy: {pos}/{len(subset)} ({pos/len(subset)*100:.1f}%)")

    # KER vs Full on this subset
    sub_ds = set(subset['Dataset'].values)
    sub_wilc = df_wilc[df_wilc['Dataset'].isin(sub_ds)]
    if len(sub_wilc) > 0:
        print(f"  Full vs KER dAcc = {sub_wilc['dAcc'].mean():+.4f}")
        valid_ps_sub = sub_wilc['p_value'].dropna().values
        if len(valid_ps_sub) > 0:
            chi2_sub = -2 * np.sum(np.log(np.maximum(valid_ps_sub, 1e-300)))
            cp_sub = 1 - stats.chi2.cdf(chi2_sub, 2 * len(valid_ps_sub))
            print(f"  Full vs KER combined p = {cp_sub:.4e}")

# ======================================================================
# 4. DRS CONTRIBUTION DECOMPOSITION
# ======================================================================
print("\n" + "=" * 80)
print("4. DRS CONTRIBUTION DECOMPOSITION (Accuracy vs Diversity vs Compression)")
print("=" * 80)

for label, subset in [("ALL", df_syn), ("NON-SAT", non_sat)]:
    sub_ds = set(subset['Dataset'].values)

    # Feature counts from summary
    ker_feats = []
    full_feats = []
    drs_feats = []
    for ds in sub_ds:
        if ds in ker_sum.index:
            ker_feats.append(ker_sum.loc[ds, 'Mean_Feat'])
        if ds in kds_sum.index:
            full_feats.append(kds_sum.loc[ds, 'Mean_Feat'])
        if ds in drs_sum.index:
            drs_feats.append(drs_sum.loc[ds, 'Mean_Feat'])

    print(f"\n  --- {label} ---")
    if ker_feats:
        print(f"  KER mean features: {np.mean(ker_feats):.0f}")
    if full_feats:
        print(f"  Full mean features: {np.mean(full_feats):.0f}")
    if drs_feats:
        print(f"  DRS mean features: {np.mean(drs_feats):.0f}")

    # NHD
    ker_nhd_vals = []
    full_nhd_vals = []
    drs_nhd_vals = []
    for ds in sub_ds:
        if ds in ker_sum.index and 'Mean_NHD' in ker_sum.columns:
            ker_nhd_vals.append(ker_sum.loc[ds, 'Mean_NHD'])
        if ds in kds_sum.index and 'Mean_NHD' in kds_sum.columns:
            full_nhd_vals.append(kds_sum.loc[ds, 'Mean_NHD'])
        if ds in drs_sum.index and 'Mean_NHD' in drs_sum.columns:
            drs_nhd_vals.append(drs_sum.loc[ds, 'Mean_NHD'])

    if ker_nhd_vals:
        print(f"  KER mean NHD: {np.mean(ker_nhd_vals):.4f}")
    if full_nhd_vals:
        print(f"  Full mean NHD: {np.mean(full_nhd_vals):.4f}")
    if drs_nhd_vals:
        print(f"  DRS mean NHD: {np.mean(drs_nhd_vals):.4f}")

# ======================================================================
# 5. PER-DATASET KDS-EL RANKING (among KDS-EL variants only)
# ======================================================================
print("\n" + "=" * 80)
print("5. KDS-EL VARIANT RANKING PER DATASET")
print("=" * 80)

for ds in abl_ds:
    if ds not in drs_sum.index or ds not in ker_sum.index or ds not in kds_sum.index:
        continue
    accs = {
        'DRS': drs_sum.loc[ds, 'Mean_Acc'],
        'KER': ker_sum.loc[ds, 'Mean_Acc'],
        'Full': kds_sum.loc[ds, 'Mean_Acc'],
    }
    ranked = sorted(accs.items(), key=lambda x: x[1], reverse=True)
    ranks_str = ' > '.join([f"{name}({acc:.4f})" for name, acc in ranked])
    is_ceil = max(accs.values()) > 0.99
    flag = " [CEIL]" if is_ceil else ""
    print(f"  {ds:<15s}: {ranks_str}{flag}")

# Count: how many datasets does Full rank #1?
full_wins = 0
ker_wins = 0
drs_wins = 0
for ds in abl_ds:
    if ds not in drs_sum.index or ds not in ker_sum.index or ds not in kds_sum.index:
        continue
    accs = {
        'DRS': drs_sum.loc[ds, 'Mean_Acc'],
        'KER': ker_sum.loc[ds, 'Mean_Acc'],
        'Full': kds_sum.loc[ds, 'Mean_Acc'],
    }
    best = max(accs, key=accs.get)
    if best == 'Full': full_wins += 1
    elif best == 'KER': ker_wins += 1
    elif best == 'DRS': drs_wins += 1

print(f"\n  Full ranks #1: {full_wins}/{len(abl_ds)}")
print(f"  KER ranks #1:  {ker_wins}/{len(abl_ds)}")
print(f"  DRS ranks #1:  {drs_wins}/{len(abl_ds)}")

# ======================================================================
# 6. DIFFICULT DATASET ANALYSIS
# ======================================================================
print("\n" + "=" * 80)
print("6. KEY DATASET DEEP-DIVE (ALL2, ALL3, Stroke, PCMAC, BASEHOCK)")
print("=" * 80)

key_ds = ['ALL2', 'ALL3', 'Stroke', 'PCMAC', 'BASEHOCK', 'Myeloma', 'T1D', 'madelon', 'ALL4']
for ds in key_ds:
    if ds not in abl_ds:
        continue
    row = df_syn[df_syn['Dataset'] == ds].iloc[0]
    print(f"\n  {ds}:")
    print(f"    MEL={row['MEL']:.4f}, DRS={row['DRS']:.4f}, KER={row['KER']:.4f}, Full={row['Full']:.4f}")
    print(f"    dDRS={row['dDRS']:+.4f}, dKER={row['dKER']:+.4f}, dFull={row['dFull']:+.4f}")
    print(f"    Synergy={row['Synergy']:+.4f}, DRS_vs_KER={row['DRS_vs_KER']:+.4f}")

    # Check if KER vs Full is significant
    wilc_row = df_wilc[df_wilc['Dataset'] == ds]
    if len(wilc_row) > 0:
        wr = wilc_row.iloc[0]
        print(f"    KER vs Full: dAcc={wr['dAcc']:+.4f}, p={wr['p_value']:.4f}")

    # Interpretation
    print(f"    Interpretation: ", end="")
    if row['dDRS'] < 0:
        print(f"DRS alone hurts accuracy ({row['dDRS']:+.4f}). ", end="")
    if row['dFull'] > row['dKER']:
        print(f"Full improves over KER (+{row['dFull']-row['dKER']:+.4f}). ", end="")
    elif abs(row['dFull'] - row['dKER']) < 0.005:
        print(f"Full ~= KER (within noise). ", end="")
    else:
        print(f"Full worse than KER ({row['dFull']-row['dKER']:+.4f}) -- DRS interference. ", end="")
    print()

# ======================================================================
# 7. VGS-MOEA DOMINANCE ANALYSIS
# ======================================================================
print("\n" + "=" * 80)
print("7. KDS-EL vs VGS-MOEA: FINDING KDS-EL'S EXCLUSIVE ADVANTAGE")
print("=" * 80)

EXP4_DIR = PROJ / "output" / "formal_experiment_20260707_142018"
exp4_df = pd.read_csv(EXP4_DIR / "results_summary.csv")
exp4_detail = pd.read_csv(EXP4_DIR / "results_detail.csv")

vgs_sum = exp4_df[exp4_df['Version'] == 'VGS-MOEA'].set_index('Dataset')
vgs_detail = exp4_detail[exp4_detail['Version'] == 'VGS-MOEA']

# Common 20 datasets
common_20 = sorted(set(kds_sum.index) & set(vgs_sum.index))
print(f"  Common datasets (20DS): {len(common_20)}")

# Compare std (stability)
kds_std_list = []
vgs_std_list = []
kds_better_std = 0
vgs_better_std = 0

for ds in common_20:
    kds_std = kds_sum.loc[ds, 'Std_Acc']
    vgs_std = vgs_sum.loc[ds, 'Std_Acc']
    kds_std_list.append(kds_std)
    vgs_std_list.append(vgs_std)
    if kds_std < vgs_std:
        kds_better_std += 1
    else:
        vgs_better_std += 1

print(f"\n  Stability (Std_Acc):")
print(f"    KDS-EL mean std: {np.mean(kds_std_list):.4f}")
print(f"    VGS-MOEA mean std: {np.mean(vgs_std_list):.4f}")
print(f"    KDS-EL more stable on: {kds_better_std}/{len(common_20)} datasets")

# Per-dataset std comparison
print(f"\n  {'Dataset':<15s} {'KDS-EL Std':>12s} {'VGS-MOEA Std':>14s} {'More Stable':>12s}")
print(f"  " + "-" * 55)
for ds in common_20:
    ks = kds_sum.loc[ds, 'Std_Acc']
    vs = vgs_sum.loc[ds, 'Std_Acc']
    better = "KDS-EL" if ks < vs else "VGS-MOEA"
    print(f"  {ds:<13s} {ks:12.4f} {vs:14.4f} {better:>12s}")

# Features comparison
print(f"\n  Features:")
print(f"    KDS-EL mean feat: {kds_sum.loc[common_20, 'Mean_Feat'].mean():.0f}")
print(f"    VGS-MOEA mean feat: {vgs_sum.loc[common_20, 'Mean_Feat'].mean():.0f}")

# Runtime
print(f"\n  Runtime:")
print(f"    KDS-EL mean time: {kds_sum.loc[common_20, 'Mean_Time'].mean():.1f}s")
print(f"    VGS-MOEA mean time: {vgs_sum.loc[common_20, 'Mean_Time'].mean():.1f}s")

# ======================================================================
# 8. FEATURE COMPRESSION CONTRIBUTION OF DRS
# ======================================================================
print("\n" + "=" * 80)
print("8. DRS FEATURE COMPRESSION ANALYSIS")
print("=" * 80)

print(f"\n  Feature reduction vs MEL baseline (25 DS avg):")
ker_feats_all = [ker_sum.loc[ds, 'Mean_Feat'] for ds in abl_ds if ds in ker_sum.index]
full_feats_all = [kds_sum.loc[ds, 'Mean_Feat'] for ds in abl_ds if ds in kds_sum.index]
drs_feats_all = [drs_sum.loc[ds, 'Mean_Feat'] for ds in abl_ds if ds in drs_sum.index]
mel_feats_all = [mel_sum.loc[ds, 'Mean_Feat'] for ds in abl_ds if ds in mel_sum.index]

print(f"    MEL:   {np.mean(mel_feats_all):.0f}")
print(f"    KER:   {np.mean(ker_feats_all):.0f} (reduction: {(1-np.mean(ker_feats_all)/np.mean(mel_feats_all))*100:.1f}%)")
print(f"    Full:  {np.mean(full_feats_all):.0f} (reduction: {(1-np.mean(full_feats_all)/np.mean(mel_feats_all))*100:.1f}%)")
print(f"    DRS:   {np.mean(drs_feats_all):.0f} (reduction: {(1-np.mean(drs_feats_all)/np.mean(mel_feats_all))*100:.1f}%)")

# KER vs Full feature difference
ker_full_feat_diff = []
for ds in abl_ds:
    if ds in ker_sum.index and ds in kds_sum.index:
        ker_full_feat_diff.append(ker_sum.loc[ds, 'Mean_Feat'] - kds_sum.loc[ds, 'Mean_Feat'])
print(f"\n  Mean feature reduction: KER->Full = {np.mean(ker_full_feat_diff):.0f} features")
print(f"  (Full uses fewer features than KER on {(np.array(ker_full_feat_diff) > 0).sum()}/{len(ker_full_feat_diff)} datasets)")

# ======================================================================
# 9. SUMMARY FOR PAPER REVISION
# ======================================================================
print("\n" + "=" * 80)
print("9. SUMMARY: KEY FACTS FOR PAPER REVISION")
print("=" * 80)

print(f"""
  C1 - SYNERGY:
    Synergy = {df_syn['Synergy'].mean():+.4f} (negative!)
    Positive synergy: {positive_syn}/{len(synergies)} ({positive_syn/len(synergies)*100:.1f}%)
    -> Synergy narrative is FALSE. Must reframe.

  C2 - VGS-MOEA DOMINANCE:
    VGS-MOEA Acc = 0.9463 (#1), KDS-EL Acc = 0.9450 (#2), delta = -0.0013
    KDS-EL more stable on: {kds_better_std}/{len(common_20)} datasets
    -> KDS-EL advantage: single-solution output (no decision-maker needed)
    -> Also: deterministic single optimum vs Pareto front

  C3 - DRS ACCURACY CONTRIBUTION ~ 0:
    KER-only = {df_wilc['KER_mean'].mean():.4f}, Full = {df_wilc['Full_mean'].mean():.4f}
    dAcc (Full - KER) = {df_wilc['dAcc'].mean():+.4f}
    Fisher combined p = {combined_p:.4e} ({'NOT significant' if combined_p >= 0.05 else 'SIGNIFICANT'})
    Full > KER on {n_full_better}/{len(df_wilc)} datasets
    -> DRS adds diversity (NHD>0) + compression, not accuracy

  NON-SATURATED SUBSET (Acc<0.95, n={len(non_sat)}):
    Synergy = {non_sat['Synergy'].mean():+.4f}
    Positive synergy: {(non_sat['Synergy'] > 0).sum()}/{len(non_sat)}
    dFull = {non_sat['dFull'].mean():+.4f}
    dKER = {non_sat['dKER'].mean():+.4f}
""")

print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
