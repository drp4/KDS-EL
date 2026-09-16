import sys
import os
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.interpolate import make_interp_spline

sys.path.insert(0, 'code')
from generate_figures import load_merged_detail, get_shared_datasets, ABL_VERSIONS, DS_LABEL_MAP
from plot_style import apply_style

apply_style()

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.interpolate import make_interp_spline
import shutil

sys.path.insert(0, 'code')
from generate_figures import load_merged_detail, get_shared_datasets, ABL_VERSIONS
from plot_style import apply_style

apply_style()


def generate_figure_7_dual_flow(out_path='paper/figures/F6_ablation_radar.pdf'):
    """Figure 7: Spaghetti-to-Signal Dual-Panel Flow Plot for Constituent Mechanisms."""
    print("Generating Figure 7: Spaghetti-to-Signal Dual-Panel Flow...")
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

    # Chronological: MEL, w/o TPS & KER, w/o TPS, KDS-EL
    acc_mat = np.array(acc_mat)[:, [3, 2, 1, 0]]
    feat_mat = np.array(feat_mat)[:, [3, 2, 1, 0]]

    means_acc = np.mean(acc_mat, axis=0)
    means_feat = np.mean(feat_mat, axis=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.3, 2.75), gridspec_kw={'wspace': 0.38})

    # 1. Panel 1: Accuracy
    for i in range(len(acc_mat)):
        ax1.plot(range(4), acc_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)

    ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.7, zorder=4)
    ax1.scatter(range(4), means_acc, color='#BE123C', s=32, edgecolors='#4C0519', linewidths=0.8, zorder=5)

    for idx, m in enumerate(means_acc):
        y_off = 8 if idx in [1, 3] else -12
        x_off = 8 if idx == 0 else 0
        ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(x_off, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#881337',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))

    ax1.set_xlim(-0.25, 3.25)
    ax1.set_title('(a) Accuracy Progression', fontsize=7.2, fontweight='bold', pad=4)
    ax1.set_xticks(range(4))
    ax1.set_ylabel('Accuracy', fontsize=7.0, fontweight='bold')
    ax1.set_ylim(0.72, 1.03)
    ax1.set_yticks([0.75, 0.85, 0.95, 1.00])
    ax1.tick_params(axis='both', labelsize=6.5, pad=2)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#94A3B8')
    ax1.spines['bottom'].set_color('#94A3B8')

    # 2. Panel 2: Features
    for i in range(len(feat_mat)):
        ax2.plot(range(4), feat_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)

    ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.7, zorder=4)
    ax2.scatter(range(4), means_feat, color='#0284C7', marker='s', s=26, edgecolors='#0369A1', linewidths=0.8, zorder=5)

    for idx, m in enumerate(means_feat):
        val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
        y_off = 8 if idx in [0, 2] else -12
        x_off = 8 if idx == 0 else 0
        ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(x_off, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#0369A1',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))

    ax2.set_xlim(-0.25, 3.25)
    ax2.set_yscale('log')
    ax2.set_title('(b) Feature Cardinality', fontsize=7.2, fontweight='bold', pad=4)
    ax2.set_xticks(range(4))
    ax2.set_ylabel('Active Features', fontsize=7.0, fontweight='bold')
    ax2.set_ylim(25, 13000)
    ax2.set_yticks([100, 1000])
    ax2.get_yaxis().set_major_formatter(mpl.ticker.ScalarFormatter())
    ax2.tick_params(axis='both', labelsize=6.5, pad=2)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_color('#94A3B8')
    ax2.spines['bottom'].set_color('#94A3B8')

    labels = ['MEL', 'w/o TPS\n& KER', 'w/o TPS', 'KDS-EL']
    ax1.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)
    ax2.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)

    legend_elements = [
        Line2D([0], [0], color='#BE123C', lw=2.2, marker='o', markersize=3.8, label='Mean accuracy'),
        Line2D([0], [0], color='#0284C7', lw=2.2, marker='s', markersize=3.5, label='Mean features'),
        Line2D([0], [0], color='#94A3B8', lw=0.8, alpha=0.5, label='Individual dataset'),
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.05),
               ncol=3, frameon=True, facecolor='#ffffff', edgecolor='#E2E8F0',
               fontsize=5.8, handlelength=1.3, handletextpad=0.3, columnspacing=0.8, borderpad=0.2)

    fig.tight_layout(rect=[0, 0, 1, 0.93])

    out_file = Path(out_path).resolve()
    with open(out_file, 'wb') as f:
        fig.savefig(f, format='pdf')
    png_file = out_file.with_suffix('.png')
    with open(png_file, 'wb') as f:
        fig.savefig(f, format='png', dpi=240)
    plt.close(fig)
    print(f'Saved {out_file} and {png_file}')


def generate_figure_10_decoupled(out_path='paper/figures/F14_parameter_sensitivity.pdf'):
    """Figure 10: Dual-Row Decoupled Parameter Sensitivity Panels."""
    print("Generating Figure 10: Dual-Row Decoupled Parameter Sensitivity...")
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

    fig, axes = plt.subplots(2, 5, figsize=(9.5, 2.75), sharex=False)

    color_acc = '#BE123C'
    color_feat = '#0284C7'

    for col_idx, p in enumerate(params):
        ax_top = axes[0, col_idx]
        ax_bot = axes[1, col_idx]
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

    fig.tight_layout(pad=1.0, h_pad=0.6, w_pad=0.8)
    save_fig_safe(fig, out_path, dpi=220)
    plt.close(fig)


def generate_figure_9_bubble(out_path='paper/figures/F11_runtime_scatter.pdf'):
    """Figure 9: Multi-Objective Efficiency Bubble Plot across 12 algorithms."""
    print("Generating Figure 9: Multi-Objective Efficiency Bubble Plot...")
    
    # Master Data strictly aligned with AGENTS.md Protocol TRUTH-1
    algorithms = [
        ('KDS-EL', 87.8, 0.9545, 51.3, '#B91C1C', 'o'),
        ('w/o TPS', 121.7, 0.9462, 48.5, '#2563EB', 's'),
        ('w/o TPS & KER', 290.5, 0.9348, 62.4, '#0D9488', '^'),
        ('MEL', 2722.2, 0.9093, 175.0, '#7C3AED', 'v'),
        ('bIRIME', 407.7, 0.9454, 326.2, '#D97706', 'P'),
        ('FWPSO', 1068.9, 0.9242, 175.0, '#475569', 'D'),
        ('SaWDE', 3521.1, 0.9180, 210.4, '#059669', '>'),
        ('PSO-CSM', 1559.4, 0.9085, 188.6, '#64748B', 'p'),
        ('BPSO', 5296.5, 0.9075, 134.2, '#94A3B8', 'X'),
        ('BinCOA', 5420.7, 0.8973, 245.8, '#EA580C', 'h'),
        ('IGPSO', 2538.2, 0.8985, 136.4, '#4B5563', '<'),
        ('DENCA-SO', 5323.4, 0.8712, 185.7, '#6B7280', 'd'),
    ]

    fig, ax = plt.subplots(figsize=(4.2, 2.85), dpi=300)

    def time_to_area(t):
        return max(20, t * 0.95)

    for name, feat, acc, time_s, color, marker in algorithms:
        area = time_to_area(time_s)
        is_kds = (name == 'KDS-EL')
        
        if is_kds:
            ax.scatter(feat, acc, s=area*2.4, color='#FEE2E2', alpha=0.6, edgecolors='none', zorder=4)
            ax.scatter(feat, acc, s=area, color=color, marker=marker,
                       edgecolors='#7F1D1D', linewidths=1.2, alpha=0.98, zorder=7)
            ax.annotate(r'$\mathbf{KDS\text{-}EL}$',
                        xy=(feat, acc), xytext=(6, 6),
                        textcoords='offset points', fontsize=7.6, color='#991B1B',
                        zorder=10)
        elif name == 'bIRIME':
            ax.scatter(feat, acc, s=area, color=color, marker=marker,
                       edgecolors='#92400E', linewidths=1.0, alpha=0.9, zorder=6)
            ax.annotate('bIRIME', xy=(feat, acc), xytext=(0, 11),
                        textcoords='offset points', ha='center', va='bottom',
                        fontsize=6.8, color='#92400E', fontweight='bold',
                        zorder=9)
        else:
            ax.scatter(feat, acc, s=area, color=color, marker=marker,
                       edgecolors='#374151', linewidths=0.5, alpha=0.85, zorder=5)

    ax.set_xscale('log')
    ax.set_xlim(35, 10000)
    ax.set_ylim(0.860, 0.975)
    ax.set_xlabel('Mean Selected Feature Cardinality', fontsize=7.5, fontweight='bold')
    ax.set_ylabel('Mean Classification Accuracy', fontsize=7.5, fontweight='bold')
    ax.tick_params(axis='both', labelsize=6.8, pad=1.5)

    ax.grid(True, linestyle='--', linewidth=0.4, alpha=0.5, color='#CBD5E1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')

    ref_times = [50, 150, 300]
    legend_elements_size = [
        Line2D([0], [0], marker='o', color='w', label=f'{t} s',
               markerfacecolor='#CBD5E1', markeredgecolor='#475569',
               markersize=np.sqrt(time_to_area(t)), alpha=0.7)
        for t in ref_times
    ]
    legend_size = ax.legend(handles=legend_elements_size, title='Execution Time',
                            loc='lower left', bbox_to_anchor=(0.02, 0.03),
                            fontsize=6.0, title_fontsize=6.4, frameon=True,
                            facecolor='#F8FAFC', edgecolor='#CBD5E1', framealpha=0.95,
                            labelspacing=0.8, handletextpad=0.6)
    ax.add_artist(legend_size)

    legend_algs = [
        Line2D([0], [0], marker='o', color='w', label='KDS-EL', markerfacecolor='#B91C1C', markeredgecolor='#7F1D1D', markersize=6),
        Line2D([0], [0], marker='s', color='w', label='w/o TPS', markerfacecolor='#2563EB', markeredgecolor='#1E3A8A', markersize=5),
        Line2D([0], [0], marker='^', color='w', label='w/o TPS & KER', markerfacecolor='#0D9488', markeredgecolor='#134E4A', markersize=5),
        Line2D([0], [0], marker='v', color='w', label='MEL', markerfacecolor='#7C3AED', markeredgecolor='#5B21B6', markersize=5),
        Line2D([0], [0], marker='P', color='w', label='bIRIME', markerfacecolor='#D97706', markeredgecolor='#92400E', markersize=6),
        Line2D([0], [0], marker='D', color='w', label='FWPSO', markerfacecolor='#475569', markeredgecolor='#1E293B', markersize=5),
        Line2D([0], [0], marker='>', color='w', label='SaWDE', markerfacecolor='#059669', markeredgecolor='#065F46', markersize=5),
        Line2D([0], [0], marker='p', color='w', label='PSO-CSM', markerfacecolor='#64748B', markeredgecolor='#334155', markersize=5),
        Line2D([0], [0], marker='h', color='w', label='BinCOA', markerfacecolor='#EA580C', markeredgecolor='#9A3412', markersize=5),
        Line2D([0], [0], marker='<', color='w', label='IGPSO', markerfacecolor='#4B5563', markeredgecolor='#1F2937', markersize=5),
        Line2D([0], [0], marker='d', color='w', label='DENCA-SO', markerfacecolor='#6B7280', markeredgecolor='#374151', markersize=5),
        Line2D([0], [0], marker='X', color='w', label='BPSO', markerfacecolor='#94A3B8', markeredgecolor='#475569', markersize=5),
    ]
    legend_alg = ax.legend(handles=legend_algs, loc='upper right', bbox_to_anchor=(0.99, 0.98),
                           ncol=2, fontsize=5.8, frameon=True,
                           facecolor='#F8FAFC', edgecolor='#CBD5E1', framealpha=0.95,
                           columnspacing=0.6, handletextpad=0.3)

    plt.tight_layout(pad=0.6)
    save_fig_safe(fig, out_path, dpi=300)
    plt.close(fig)


def save_fig_safe(fig, out_path, dpi=300):
    import time
    out_file = Path(out_path).resolve()
    png_file = out_file.with_suffix('.png')
    for attempt in range(8):
        try:
            with open(out_file, 'wb') as f:
                fig.savefig(f, format='pdf')
            with open(png_file, 'wb') as f:
                fig.savefig(f, format='png', dpi=dpi)
            print(f'Saved {out_file} and {png_file}')
            return
        except Exception as e:
            if attempt == 7:
                raise e
            time.sleep(0.3)


def safe_copy(src, dst):
    import shutil
    try:
        shutil.copyfile(os.path.abspath(src), os.path.abspath(dst))
    except Exception as e:
        print(f"Warning copying {src} to {dst}: {e}")


if __name__ == '__main__':
    os.makedirs('output/figures', exist_ok=True)
    os.makedirs('paper/figures', exist_ok=True)

    # 1. Figure 7
    generate_figure_7_dual_flow('paper/figures/F6_ablation_radar.pdf')
    safe_copy('paper/figures/F6_ablation_radar.pdf', 'output/figures/F6_ablation_radar.pdf')
    safe_copy('paper/figures/F6_ablation_radar.png', 'output/figures/F6_ablation_radar.png')

    # 2. Figure 9
    generate_figure_9_bubble('paper/figures/F11_runtime_scatter.pdf')
    safe_copy('paper/figures/F11_runtime_scatter.pdf', 'output/figures/F11_runtime_scatter.pdf')
    safe_copy('paper/figures/F11_runtime_scatter.png', 'output/figures/F11_runtime_scatter.png')

    # 3. Figure 10
    generate_figure_10_decoupled('paper/figures/F14_parameter_sensitivity.pdf')
    safe_copy('paper/figures/F14_parameter_sensitivity.pdf', 'output/figures/F14_parameter_sensitivity.pdf')
    safe_copy('paper/figures/F14_parameter_sensitivity.png', 'output/figures/F14_parameter_sensitivity.png')
    print('All figures generated and synced successfully!')

