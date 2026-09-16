import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
import numpy as np

# Set publication style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# Master Data from AGENTS.md Protocol TRUTH-1
algorithms = [
    # Proposed & Configurations
    ('KDS-EL', 87.8, 0.9545, 51.3, '#B91C1C', 'o'),
    ('w/o TPS', 121.7, 0.9462, 48.5, '#2563EB', 's'),
    ('w/o TPS & KER', 290.5, 0.9348, 62.4, '#0D9488', '^'),
    ('MEL', 2722.2, 0.9093, 175.0, '#7C3AED', 'v'),
    
    # Competitor Algorithms
    ('bIRIME', 407.7, 0.9454, 326.2, '#D97706', 'P'),
    ('FWPSO', 1068.9, 0.9242, 175.0, '#475569', 'D'),
    ('SaWDE', 3521.1, 0.9180, 210.4, '#059669', '>'),
    ('PSO-CSM', 1559.4, 0.9085, 188.6, '#64748B', 'p'),
    ('BPSO', 5296.5, 0.9075, 134.2, '#94A3B8', 'X'),
    ('BinCOA', 5420.7, 0.8973, 245.8, '#EA580C', 'h'),
    ('IGPSO', 2538.2, 0.8985, 136.4, '#4B5563', '<'),
    ('DENCA-SO', 5323.4, 0.8712, 185.7, '#6B7280', 'd'),
]

fig, ax = plt.subplots(figsize=(6.8, 4.4), dpi=300)

# Scale factor for bubble size: area proportional to runtime
def time_to_area(t):
    return max(40, t * 1.6)

# Plot bubbles
for name, feat, acc, time_s, color, marker in algorithms:
    area = time_to_area(time_s)
    is_kds = (name == 'KDS-EL')
    
    if is_kds:
        # Subtle clean halo for KDS-EL
        ax.scatter(feat, acc, s=area*2.4, color='#FEE2E2', alpha=0.6, edgecolors='none', zorder=4)
        ax.scatter(feat, acc, s=area, color=color, marker=marker,
                   edgecolors='#7F1D1D', linewidths=1.5, alpha=0.98, zorder=7)
        # Minimalist bold label
        ax.annotate(r'$\mathbf{KDS\text{-}EL}$',
                    xy=(feat, acc), xytext=(10, 8),
                    textcoords='offset points', fontsize=9.0, color='#991B1B',
                    zorder=10)
    elif name == 'bIRIME':
        ax.scatter(feat, acc, s=area, color=color, marker=marker,
                   edgecolors='#92400E', linewidths=1.2, alpha=0.9, zorder=6)
        ax.annotate('bIRIME', xy=(feat, acc), xytext=(12, 2),
                    textcoords='offset points', fontsize=8.0, color='#92400E', fontweight='semibold',
                    zorder=9)
    else:
        ax.scatter(feat, acc, s=area, color=color, marker=marker,
                   edgecolors='#374151', linewidths=0.6, alpha=0.85, zorder=5)

# Formatting axes - zero parenthetical clutter
ax.set_xscale('log')
ax.set_xlim(35, 10000)
ax.set_ylim(0.860, 0.975)
ax.set_xlabel('Mean Selected Feature Cardinality', fontsize=9.0)
ax.set_ylabel('Mean Classification Accuracy', fontsize=9.0)

# Grid & Spines
ax.grid(True, linestyle='--', linewidth=0.4, alpha=0.5, color='#CBD5E1')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#94A3B8')
ax.spines['bottom'].set_color('#94A3B8')

# Bubble Size Reference Legend (In lower left corner, clean and minimalist)
ref_times = [50, 150, 300]
legend_elements_size = [
    Line2D([0], [0], marker='o', color='w', label=f'{t} s',
           markerfacecolor='#CBD5E1', markeredgecolor='#475569',
           markersize=np.sqrt(time_to_area(t)), alpha=0.7)
    for t in ref_times
]
legend_size = ax.legend(handles=legend_elements_size, title='Execution Time',
                        loc='lower left', bbox_to_anchor=(0.02, 0.03),
                        fontsize=7.0, title_fontsize=7.5, frameon=True,
                        facecolor='#F8FAFC', edgecolor='#CBD5E1', framealpha=0.95,
                        labelspacing=1.0, handletextpad=0.8)
ax.add_artist(legend_size)

# Algorithm Markers Legend (In upper right, zero parenthetical clutter)
legend_algs = [
    Line2D([0], [0], marker='o', color='w', label='KDS-EL', markerfacecolor='#B91C1C', markeredgecolor='#7F1D1D', markersize=8),
    Line2D([0], [0], marker='s', color='w', label='w/o TPS', markerfacecolor='#2563EB', markeredgecolor='#1E3A8A', markersize=7),
    Line2D([0], [0], marker='^', color='w', label='w/o TPS & KER', markerfacecolor='#0D9488', markeredgecolor='#134E4A', markersize=7),
    Line2D([0], [0], marker='v', color='w', label='MEL', markerfacecolor='#7C3AED', markeredgecolor='#5B21B6', markersize=7),
    Line2D([0], [0], marker='P', color='w', label='bIRIME', markerfacecolor='#D97706', markeredgecolor='#92400E', markersize=8),
    Line2D([0], [0], marker='D', color='w', label='FWPSO', markerfacecolor='#475569', markeredgecolor='#1E293B', markersize=7),
    Line2D([0], [0], marker='>', color='w', label='SaWDE', markerfacecolor='#059669', markeredgecolor='#065F46', markersize=7),
    Line2D([0], [0], marker='p', color='w', label='PSO-CSM', markerfacecolor='#64748B', markeredgecolor='#334155', markersize=7),
    Line2D([0], [0], marker='h', color='w', label='BinCOA', markerfacecolor='#EA580C', markeredgecolor='#9A3412', markersize=7),
    Line2D([0], [0], marker='<', color='w', label='IGPSO', markerfacecolor='#4B5563', markeredgecolor='#1F2937', markersize=7),
    Line2D([0], [0], marker='d', color='w', label='DENCA-SO', markerfacecolor='#6B7280', markeredgecolor='#374151', markersize=7),
    Line2D([0], [0], marker='X', color='w', label='BPSO', markerfacecolor='#94A3B8', markeredgecolor='#475569', markersize=7),
]
legend_alg = ax.legend(handles=legend_algs, loc='upper right', bbox_to_anchor=(0.99, 0.98),
                       ncol=2, fontsize=6.8, frameon=True,
                       facecolor='#F8FAFC', edgecolor='#CBD5E1', framealpha=0.95,
                       columnspacing=0.8, handletextpad=0.4)

plt.tight_layout()
plt.savefig(r'scratch\test_fig9_bubble_minimal.png', dpi=300)
print('Successfully generated scratch/test_fig9_bubble_minimal.png')
