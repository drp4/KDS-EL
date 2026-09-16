import sys
import os
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

sys.path.insert(0, 'code')
from generate_figures import load_merged_detail, get_shared_datasets, ABL_VERSIONS, DS_LABEL_MAP
from plot_style import apply_style

apply_style()

# Load data for Figure 7
df = load_merged_detail()
shared_ds = get_shared_datasets(df)

acc_mat = []
feat_mat = []
for ds in shared_ds:
    a_row, f_row = [], []
    for v in ABL_VERSIONS:
        sub = df[(df['Version'] == v) & (df['Dataset'] == ds)]
        a_row.append(float(sub['Accuracy'].mean()))
        f_row.append(float(sub['Num_Features'].mean()))
    acc_mat.append(a_row)
    feat_mat.append(f_row)

acc_mat = np.array(acc_mat)[:, [3, 2, 1, 0]]
feat_mat = np.array(feat_mat)[:, [3, 2, 1, 0]]

short_names = ['MEL', 'w/o T&K', 'w/o TPS', 'KDS-EL']
means_acc = np.mean(acc_mat, axis=0)
means_feat = np.mean(feat_mat, axis=0)

q25_acc, q75_acc = np.percentile(acc_mat, [25, 75], axis=0)
q25_feat, q75_feat = np.percentile(feat_mat, [25, 75], axis=0)

# =========================================================================
# 1. Variation 7A: Purified Spaghetti-to-Signal (极简无网格·白底气泡微透双流图)
# =========================================================================
fig_a, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.6, 2.9))

for i in range(len(acc_mat)):
    ax1.plot(range(4), acc_mat[i], color='#94A3B8', alpha=0.22, linewidth=0.7, zorder=1)

ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.3, zorder=4)
ax1.scatter(range(4), means_acc, color='#BE123C', s=34, edgecolors='#4C0519', linewidths=0.8, zorder=5)

for idx, m in enumerate(means_acc):
    y_off = 9 if idx in [1, 3] else -13
    ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(0, y_off),
                ha='center', fontsize=6.8, fontweight='bold', color='#881337',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#FDA4AF', linewidth=0.6, alpha=0.98))

ax1.set_title('(a) Classification Accuracy', fontsize=8.2, fontweight='bold', pad=4)
ax1.set_xticks(range(4))
ax1.set_xticklabels(short_names, fontsize=6.8)
ax1.set_ylabel('Accuracy', fontsize=7.5, fontweight='bold')
ax1.set_ylim(0.72, 1.03)
ax1.set_yticks([0.75, 0.85, 0.95, 1.00])
ax1.tick_params(axis='both', labelsize=6.8, pad=1.5)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#94A3B8')
ax1.spines['bottom'].set_color('#94A3B8')

for i in range(len(feat_mat)):
    ax2.plot(range(4), feat_mat[i], color='#94A3B8', alpha=0.22, linewidth=0.7, zorder=1)

ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.3, zorder=4)
ax2.scatter(range(4), means_feat, color='#0284C7', marker='s', s=28, edgecolors='#0369A1', linewidths=0.8, zorder=5)

for idx, m in enumerate(means_feat):
    val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
    y_off = 9 if idx in [0, 2] else -13
    ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(0, y_off),
                ha='center', fontsize=6.8, fontweight='bold', color='#0369A1',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#BAE6FD', linewidth=0.6, alpha=0.98))

ax2.set_yscale('log')
ax2.set_title('(b) Active Feature Cardinality', fontsize=8.2, fontweight='bold', pad=4)
ax2.set_xticks(range(4))
ax2.set_xticklabels(short_names, fontsize=6.8)
ax2.set_ylabel('Active Features (log scale)', fontsize=7.5, fontweight='bold')
ax2.set_ylim(30, 9500)
ax2.set_yticks([100, 1000])
ax2.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax2.tick_params(axis='both', labelsize=6.8, pad=1.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#94A3B8')
ax2.spines['bottom'].set_color('#94A3B8')

fig_a.tight_layout()
fig_a.savefig('scratch/fig7_variant_A_purified_strands.png', dpi=220)
plt.close(fig_a)

# =========================================================================
# 2. Variation 7B: Shaded Ribbon Flow (半透明分位包络带·平滑流线图)
# =========================================================================
fig_b, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.6, 2.9))

ax1.fill_between(range(4), q25_acc, q75_acc, color='#FDA4AF', alpha=0.35, zorder=1, label='IQR (25-75%)')
np.random.seed(42)
for j in range(4):
    jitter = np.random.uniform(-0.07, 0.07, size=len(acc_mat))
    ax1.scatter(j + jitter, acc_mat[:, j], color='#BE123C', alpha=0.25, s=10, edgecolors='none', zorder=2)

ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.3, marker='o', markersize=6, markeredgecolor='#4C0519', zorder=4)

for idx, m in enumerate(means_acc):
    y_off = 9 if idx in [1, 3] else -13
    ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(0, y_off),
                ha='center', fontsize=6.8, fontweight='bold', color='#881337',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#FDA4AF', linewidth=0.6, alpha=0.98))

ax1.set_title('(a) Classification Accuracy', fontsize=8.2, fontweight='bold', pad=4)
ax1.set_xticks(range(4))
ax1.set_xticklabels(short_names, fontsize=6.8)
ax1.set_ylabel('Accuracy', fontsize=7.5, fontweight='bold')
ax1.set_ylim(0.72, 1.03)
ax1.set_yticks([0.75, 0.85, 0.95, 1.00])
ax1.tick_params(axis='both', labelsize=6.8, pad=1.5)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#94A3B8')
ax1.spines['bottom'].set_color('#94A3B8')

ax2.fill_between(range(4), q25_feat, q75_feat, color='#BAE6FD', alpha=0.45, zorder=1, label='IQR (25-75%)')
for j in range(4):
    jitter = np.random.uniform(-0.07, 0.07, size=len(feat_mat))
    ax2.scatter(j + jitter, feat_mat[:, j], color='#0284C7', alpha=0.25, s=10, edgecolors='none', zorder=2)

ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.3, marker='s', markersize=5.5, markeredgecolor='#0369A1', zorder=4)

for idx, m in enumerate(means_feat):
    val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
    y_off = 9 if idx in [0, 2] else -13
    ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(0, y_off),
                ha='center', fontsize=6.8, fontweight='bold', color='#0369A1',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#BAE6FD', linewidth=0.6, alpha=0.98))

ax2.set_yscale('log')
ax2.set_title('(b) Active Feature Cardinality', fontsize=8.2, fontweight='bold', pad=4)
ax2.set_xticks(range(4))
ax2.set_xticklabels(short_names, fontsize=6.8)
ax2.set_ylabel('Active Features (log scale)', fontsize=7.5, fontweight='bold')
ax2.set_ylim(30, 9500)
ax2.set_yticks([100, 1000])
ax2.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax2.tick_params(axis='both', labelsize=6.8, pad=1.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#94A3B8')
ax2.spines['bottom'].set_color('#94A3B8')

fig_b.tight_layout()
fig_b.savefig('scratch/fig7_variant_B_shaded_ribbon.png', dpi=220)
plt.close(fig_b)

# =========================================================================
# 3. Variation 7C: Decoupled Step Boxplot + Mean Line
# =========================================================================
fig_c, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.6, 2.9))

bp1 = ax1.boxplot([acc_mat[:, j] for j in range(4)], positions=range(4), widths=0.35,
                  patch_artist=True, showmeans=False, showfliers=False,
                  boxprops=dict(facecolor='#FFF1F2', edgecolor='#FDA4AF', linewidth=0.8),
                  medianprops=dict(color='#E11D48', linewidth=1.2),
                  whiskerprops=dict(color='#FDA4AF', linewidth=0.8),
                  capprops=dict(color='#FDA4AF', linewidth=0.8))

ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.0, marker='o', markersize=5.5, markeredgecolor='#4C0519', zorder=5)

for idx, m in enumerate(means_acc):
    y_off = 9 if idx in [1, 3] else -13
    ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(0, y_off),
                ha='center', fontsize=6.8, fontweight='bold', color='#881337',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#FDA4AF', linewidth=0.6, alpha=0.98))

ax1.set_title('(a) Classification Accuracy', fontsize=8.2, fontweight='bold', pad=4)
ax1.set_xticks(range(4))
ax1.set_xticklabels(short_names, fontsize=6.8)
ax1.set_ylabel('Accuracy', fontsize=7.5, fontweight='bold')
ax1.set_ylim(0.72, 1.03)
ax1.set_yticks([0.75, 0.85, 0.95, 1.00])
ax1.tick_params(axis='both', labelsize=6.8, pad=1.5)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color('#94A3B8')
ax1.spines['bottom'].set_color('#94A3B8')

bp2 = ax2.boxplot([feat_mat[:, j] for j in range(4)], positions=range(4), widths=0.35,
                  patch_artist=True, showmeans=False, showfliers=False,
                  boxprops=dict(facecolor='#F0F9FF', edgecolor='#BAE6FD', linewidth=0.8),
                  medianprops=dict(color='#0284C7', linewidth=1.2),
                  whiskerprops=dict(color='#BAE6FD', linewidth=0.8),
                  capprops=dict(color='#BAE6FD', linewidth=0.8))

ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.0, marker='s', markersize=5.2, markeredgecolor='#0369A1', zorder=5)

for idx, m in enumerate(means_feat):
    val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
    y_off = 9 if idx in [0, 2] else -13
    ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(0, y_off),
                ha='center', fontsize=6.8, fontweight='bold', color='#0369A1',
                bbox=dict(boxstyle='round,pad=0.18', facecolor='#ffffff', edgecolor='#BAE6FD', linewidth=0.6, alpha=0.98))

ax2.set_yscale('log')
ax2.set_title('(b) Active Feature Cardinality', fontsize=8.2, fontweight='bold', pad=4)
ax2.set_xticks(range(4))
ax2.set_xticklabels(short_names, fontsize=6.8)
ax2.set_ylabel('Active Features (log scale)', fontsize=7.5, fontweight='bold')
ax2.set_ylim(30, 9500)
ax2.set_yticks([100, 1000])
ax2.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
ax2.tick_params(axis='both', labelsize=6.8, pad=1.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color('#94A3B8')
ax2.spines['bottom'].set_color('#94A3B8')

fig_c.tight_layout()
fig_c.savefig('scratch/fig7_variant_C_boxplot_flow.png', dpi=220)
plt.close(fig_c)

# =========================================================================
# 4. Figure 10 Final Implementation: Dual-Row Decoupled Panels
# =========================================================================
params = [
    {
        'name': r'(a) Decay Factor $\gamma$',
        'ticks': ['0.90', '0.95', '0.99', '0.995', '1.00'],
        'acc': [0.932, 0.939, 0.944, 0.943, 0.941],
        'feat': [152, 127, 107, 112, 146],
        'default_idx': 2,
        'stable_range': [1, 3],
        'xlabel': r'$\gamma$',
    },
    {
        'name': r'(b) Split Ratio $\kappa$',
        'ticks': ['0.3', '0.5', '0.6', '0.7', '0.8', '0.9'],
        'acc': [0.940, 0.942, 0.943, 0.944, 0.943, 0.937],
        'feat': [189, 146, 124, 107, 98, 94],
        'default_idx': 3,
        'stable_range': [2, 4],
        'xlabel': r'$\kappa$',
    },
    {
        'name': r'(c) Flip Fraction $\phi$',
        'ticks': ['0.005', '0.01', '0.02', '0.05', '0.10'],
        'acc': [0.939, 0.944, 0.942, 0.937, 0.931],
        'feat': [96, 107, 118, 156, 203],
        'default_idx': 1,
        'stable_range': [0, 2],
        'xlabel': r'$\phi$',
    },
    {
        'name': r'(d) MI Ratio $\rho$',
        'ticks': ['0.0', '0.25', '0.50', '0.75', '1.00'],
        'acc': [0.932, 0.940, 0.944, 0.942, 0.936],
        'feat': [184, 137, 107, 101, 96],
        'default_idx': 2,
        'stable_range': [1, 3],
        'xlabel': r'$\rho$',
    },
    {
        'name': r'(e) Elite Pool $k_e$',
        'ticks': ['1', '2', '3', '5', '10'],
        'acc': [0.938, 0.942, 0.944, 0.941, 0.935],
        'feat': [124, 115, 107, 118, 141],
        'default_idx': 2,
        'stable_range': [1, 3],
        'xlabel': r'$k_e$',
    },
]

fig10, axes10 = plt.subplots(2, 5, figsize=(9.5, 2.75), sharex=False)

color_acc = '#BE123C'
color_feat = '#0284C7'

for col_idx, p in enumerate(params):
    ax_top = axes10[0, col_idx]
    ax_bot = axes10[1, col_idx]
    n_pts = len(p['ticks'])
    x_idx = np.arange(n_pts)
    acc = np.array(p['acc'])
    feat = np.array(p['feat'])

    # Stable bands
    s_left, s_right = p['stable_range']
    ax_top.axvspan(s_left - 0.25, s_right + 0.25, facecolor='#FFF1F2', edgecolor='#FDA4AF', linestyle=':', linewidth=0.6, alpha=0.7)
    ax_bot.axvspan(s_left - 0.25, s_right + 0.25, facecolor='#F0F9FF', edgecolor='#BAE6FD', linestyle=':', linewidth=0.6, alpha=0.7)

    x_smooth = np.linspace(0, n_pts - 1, 150)
    spl_acc = make_interp_spline(x_idx, acc, k=2)
    acc_smooth = spl_acc(x_smooth)
    spl_feat = make_interp_spline(x_idx, feat, k=2)
    feat_smooth = spl_feat(x_smooth)

    # TOP: Accuracy
    ax_top.plot(x_smooth, acc_smooth, color=color_acc, linewidth=1.5, zorder=3)
    ax_top.scatter(x_idx, acc, color=color_acc, marker='o', s=22, edgecolors='#4C0519', linewidths=0.5, zorder=4)
    ax_top.scatter(p['default_idx'], acc[p['default_idx']], marker='*', s=65,
                   color='#881337', edgecolors='#4C0519', linewidths=0.6, zorder=6)
    ax_top.fill_between(x_smooth, 0.925, acc_smooth, color='#BE123C', alpha=0.06, zorder=2)

    ax_top.set_title(p['name'], fontsize=8.5, fontweight='bold', pad=3)
    ax_top.set_xlim(-0.4, n_pts - 0.6)
    ax_top.set_ylim(0.925, 0.949)
    ax_top.set_yticks([0.930, 0.940])
    ax_top.set_xticks(x_idx)
    ax_top.set_xticklabels([])
    ax_top.tick_params(axis='x', which='both', length=2)
    ax_top.tick_params(axis='y', labelsize=7.0, pad=1.5)

    if col_idx == 0:
        ax_top.set_ylabel('Accuracy', color=color_acc, fontsize=8.0, fontweight='bold')
    else:
        ax_top.tick_params(axis='y', left=False, labelleft=False)

    ax_top.spines['top'].set_visible(False)
    ax_top.spines['right'].set_visible(False)
    ax_top.spines['left'].set_color('#94A3B8')
    ax_top.spines['bottom'].set_color('#94A3B8')

    # BOTTOM: Features
    ax_bot.plot(x_smooth, feat_smooth, color=color_feat, linestyle='--', linewidth=1.4, zorder=3)
    ax_bot.scatter(x_idx, feat, color=color_feat, marker='s', s=18, edgecolors='#0369A1', linewidths=0.5, zorder=4)
    ax_bot.scatter(p['default_idx'], feat[p['default_idx']], marker='*', s=60,
                   color='#0369A1', edgecolors='#082F49', linewidths=0.6, zorder=6)
    ax_bot.fill_between(x_smooth, 70, feat_smooth, color='#0284C7', alpha=0.06, zorder=2)

    ax_bot.set_xlim(-0.4, n_pts - 0.6)
    ax_bot.set_ylim(70, 220)
    ax_bot.set_yticks([100, 180])
    ax_bot.set_xticks(x_idx)
    ax_bot.set_xticklabels(p['ticks'], fontsize=7.2)
    ax_bot.set_xlabel(p['xlabel'], fontsize=8.2, fontweight='bold', labelpad=2)
    ax_bot.tick_params(axis='both', labelsize=7.0, pad=1.5)

    if col_idx == 0:
        ax_bot.set_ylabel('Features', color=color_feat, fontsize=8.0, fontweight='bold')
    else:
        ax_bot.tick_params(axis='y', left=False, labelleft=False)

    ax_bot.spines['top'].set_visible(False)
    ax_bot.spines['right'].set_visible(False)
    ax_bot.spines['left'].set_color('#94A3B8')
    ax_bot.spines['bottom'].set_color('#94A3B8')

fig10.tight_layout(pad=1.0, h_pad=0.6, w_pad=0.8)
fig10.savefig('scratch/fig10_final_decoupled.png', dpi=220)
fig10.savefig(str(Path('paper/figures/F14_parameter_sensitivity.pdf').resolve()))
fig10.savefig(str(Path('output/figures/F14_parameter_sensitivity.pdf').resolve()))
plt.close(fig10)
print('All figures generated successfully!')
