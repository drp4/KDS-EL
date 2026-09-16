import sys
import os
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, 'code')
from generate_figures import load_merged_detail, get_shared_datasets, ABL_VERSIONS
from plot_style import apply_style

apply_style()

def run_test():
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
    means_acc = np.mean(acc_mat, axis=0)
    means_feat = np.mean(feat_mat, axis=0)
    labels = ['MEL', 'w/o TPS\n& KER', 'w/o TPS', 'KDS-EL']

    legend_elements = [
        Line2D([0], [0], color='#BE123C', lw=2.2, marker='o', markersize=3.8, label='Mean accuracy'),
        Line2D([0], [0], color='#0284C7', lw=2.2, marker='s', markersize=3.5, label='Mean features'),
        Line2D([0], [0], color='#94A3B8', lw=0.8, alpha=0.5, label='Individual dataset'),
    ]

    # Opt 1: xlim(-0.35, 3.35)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.3, 2.75), gridspec_kw={'wspace': 0.38})
    for i in range(len(acc_mat)):
        ax1.plot(range(4), acc_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)
        ax2.plot(range(4), feat_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)
    ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.7, zorder=4)
    ax1.scatter(range(4), means_acc, color='#BE123C', s=32, edgecolors='#4C0519', linewidths=0.8, zorder=5)
    ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.7, zorder=4)
    ax2.scatter(range(4), means_feat, color='#0284C7', marker='s', s=26, edgecolors='#0369A1', linewidths=0.8, zorder=5)

    for idx, m in enumerate(means_acc):
        y_off = 8 if idx in [1, 3] else -12
        ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(0, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#881337',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))
    for idx, m in enumerate(means_feat):
        val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
        y_off = 8 if idx in [0, 2] else -12
        ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(0, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#0369A1',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))

    ax1.set_xlim(-0.35, 3.35)
    ax2.set_xlim(-0.35, 3.35)
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

    ax1.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)
    ax2.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)

    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.05),
               ncol=3, frameon=True, facecolor='#ffffff', edgecolor='#E2E8F0',
               fontsize=5.8, handlelength=1.3, handletextpad=0.3, columnspacing=0.8, borderpad=0.2)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig('scratch/test_opt1_xlim.png', dpi=240)
    plt.close(fig)

    # Opt 2: shift numbers slightly to the right inside (x_off=10)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.3, 2.75), gridspec_kw={'wspace': 0.38})
    for i in range(len(acc_mat)):
        ax1.plot(range(4), acc_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)
        ax2.plot(range(4), feat_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)
    ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.7, zorder=4)
    ax1.scatter(range(4), means_acc, color='#BE123C', s=32, edgecolors='#4C0519', linewidths=0.8, zorder=5)
    ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.7, zorder=4)
    ax2.scatter(range(4), means_feat, color='#0284C7', marker='s', s=26, edgecolors='#0369A1', linewidths=0.8, zorder=5)

    for idx, m in enumerate(means_acc):
        y_off = 8 if idx in [1, 3] else -12
        x_off = 10 if idx == 0 else 0
        ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(x_off, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#881337',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))
    for idx, m in enumerate(means_feat):
        val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
        y_off = 8 if idx in [0, 2] else -12
        x_off = 10 if idx == 0 else 0
        ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(x_off, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#0369A1',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))

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

    ax1.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)
    ax2.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)

    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.05),
               ncol=3, frameon=True, facecolor='#ffffff', edgecolor='#E2E8F0',
               fontsize=5.8, handlelength=1.3, handletextpad=0.3, columnspacing=0.8, borderpad=0.2)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig('scratch/test_opt2_xoff.png', dpi=240)
    plt.close(fig)

    # Opt 3: Combined - xlim(-0.25, 3.25) AND x_off=8
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(4.3, 2.75), gridspec_kw={'wspace': 0.38})
    for i in range(len(acc_mat)):
        ax1.plot(range(4), acc_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)
        ax2.plot(range(4), feat_mat[i], color='#94A3B8', alpha=0.15, linewidth=0.65, zorder=1)
    ax1.plot(range(4), means_acc, color='#BE123C', linewidth=2.7, zorder=4)
    ax1.scatter(range(4), means_acc, color='#BE123C', s=32, edgecolors='#4C0519', linewidths=0.8, zorder=5)
    ax2.plot(range(4), means_feat, color='#0284C7', linewidth=2.7, zorder=4)
    ax2.scatter(range(4), means_feat, color='#0284C7', marker='s', s=26, edgecolors='#0369A1', linewidths=0.8, zorder=5)

    for idx, m in enumerate(means_acc):
        y_off = 8 if idx in [1, 3] else -12
        x_off = 6 if idx == 0 else 0
        ax1.annotate(f'{m:.3f}', (idx, m), textcoords='offset points', xytext=(x_off, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#881337',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))
    for idx, m in enumerate(means_feat):
        val_str = f'{m:.0f}' if m >= 100 else f'{m:.1f}'
        y_off = 8 if idx in [0, 2] else -12
        x_off = 6 if idx == 0 else 0
        ax2.annotate(val_str, (idx, m), textcoords='offset points', xytext=(x_off, y_off),
                    ha='center', fontsize=6.2, fontweight='bold', color='#0369A1',
                    bbox=dict(boxstyle='round,pad=0.14', facecolor='#ffffff', edgecolor='#E2E8F0', linewidth=0.4, alpha=0.98))

    ax1.set_xlim(-0.25, 3.25)
    ax2.set_xlim(-0.25, 3.25)
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

    ax1.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)
    ax2.set_xticklabels(labels, fontsize=6.0, linespacing=0.9, rotation=0)

    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.05),
               ncol=3, frameon=True, facecolor='#ffffff', edgecolor='#E2E8F0',
               fontsize=5.8, handlelength=1.3, handletextpad=0.3, columnspacing=0.8, borderpad=0.2)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig('scratch/test_opt3_comb.png', dpi=240)
    plt.close(fig)

    print('ALL DONE!')

run_test()
