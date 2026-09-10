import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 7.5
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.titlesize'] = 8.5
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7.5
plt.rcParams['pdf.fonttype'] = 42

methods = [
    'KDS-EL', 'bIRIME', 'KDS-EL w/o TPS', 'KDS-EL w/o TPS & KER',
    'FWPSO', 'BinCOA', 'PSO-CSM', 'SaWDE', 'DENCA-SO', 'IGPSO', 'MEL', 'BPSO'
]
ranks = [1.75, 2.25, 2.90, 5.10, 5.50, 6.55, 7.00, 7.80, 8.90, 9.55, 9.85, 10.85]
cd_val = 3.25
cd_cutoff = 1.75 + cd_val  # 5.00

# -------------------------------------------------------------
# Design 1: Sleek Slim Bars + Tiered Palette + Clean CD Whisker Bracket
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.48, 3.2), dpi=300)
y_pos = np.arange(len(methods))[::-1]

colors = []
edgecolors = []
for r in ranks:
    if r == 1.75:
        colors.append('#C82423')
        edgecolors.append('#991B1B')
    elif r < cd_cutoff:
        colors.append('#4A6984')
        edgecolors.append('#2C3E50')
    else:
        colors.append('#94A3B8')
        edgecolors.append('#64748B')

bars = ax.barh(y_pos, ranks, height=0.50, color=colors, edgecolor=edgecolors, linewidth=0.6, zorder=3)

for bar, r in zip(bars, ranks):
    w = bar.get_width()
    is_hero = (r == 1.75)
    color = '#C82423' if is_hero else '#334155'
    weight = 'bold' if is_hero else 'normal'
    ax.text(w + 0.22, bar.get_y() + bar.get_height()/2, f'{r:.2f}',
            va='center', ha='left', fontsize=6.8, color=color, weight=weight)

ax.axvline(x=cd_cutoff, color='#C82423', linestyle='--', linewidth=0.8, alpha=0.85, zorder=2)
ax.text(cd_cutoff + 0.15, len(methods) - 0.5, r'Critical Difference ( < 0.05$)',
        color='#C82423', fontsize=6.8, weight='bold', va='center')

ax.set_yticks(y_pos)
ytick_labels = ax.set_yticklabels(methods)
ytick_labels[0].set_color('#C82423')
ytick_labels[0].set_weight('bold')

ax.set_xlim(0, 12.6)
ax.set_xlabel('Average Friedman rank', fontsize=8, labelpad=3)

ax.grid(axis='x', linestyle=':', linewidth=0.5, color='#CBD5E1', alpha=0.7, zorder=0)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color('#94A3B8')
ax.spines['bottom'].set_color('#94A3B8')
ax.tick_params(colors='#475569')

plt.tight_layout(pad=0.4)
plt.savefig('scratch/fig6_opt1_tiered_bars.png')
plt.close()

# -------------------------------------------------------------
# Design 2: Modern Dot / Lollipop Chart (Nature / Cell Style)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.48, 3.2), dpi=300)
y_pos = np.arange(len(methods))[::-1]

for y, r, m in zip(y_pos, ranks, methods):
    if r == 1.75:
        line_color = '#C82423'
        dot_color = '#C82423'
        lw = 1.8
        ms = 6.0
    elif r < cd_cutoff:
        line_color = '#4A6984'
        dot_color = '#4A6984'
        lw = 1.0
        ms = 4.8
    else:
        line_color = '#CBD5E1'
        dot_color = '#64748B'
        lw = 0.9
        ms = 4.5
    
    ax.plot([0, r], [y, y], color=line_color, linewidth=lw, zorder=2)
    ax.plot(r, y, 'o', color=dot_color, markersize=ms, zorder=3,
            markeredgecolor='white' if r == 1.75 else dot_color, markeredgewidth=0.8)
    
    is_hero = (r == 1.75)
    color = '#C82423' if is_hero else '#475569'
    weight = 'bold' if is_hero else 'normal'
    ax.text(r + 0.28, y, f'{r:.2f}', va='center', ha='left', fontsize=6.8, color=color, weight=weight)

ax.axvline(x=cd_cutoff, color='#C82423', linestyle=':', linewidth=1.0, alpha=0.9, zorder=1)
ax.text(cd_cutoff + 0.15, len(methods) - 0.6, r'CD threshold ( < 0.05$)',
        color='#C82423', fontsize=6.8, weight='bold', va='center')

ax.set_yticks(y_pos)
ytick_labels = ax.set_yticklabels(methods)
ytick_labels[0].set_color('#C82423')
ytick_labels[0].set_weight('bold')

ax.set_xlim(0, 12.6)
ax.set_xlabel('Average Friedman rank', fontsize=8, labelpad=3)
ax.grid(axis='x', linestyle=':', linewidth=0.5, color='#E2E8F0', zorder=0)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
ax.spines['left'].set_color('#94A3B8')
ax.spines['bottom'].set_color('#94A3B8')
ax.tick_params(colors='#475569')

plt.tight_layout(pad=0.4)
plt.savefig('scratch/fig6_opt2_lollipop.png')
plt.close()

# -------------------------------------------------------------
# Design 3: Ultra-Clean Rounded/Refined Horizontal Bar Chart (Nature Minimalist)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.48, 3.1), dpi=300)
y_pos = np.arange(len(methods))[::-1]

bar_colors = ['#C82423' if r == 1.75 else '#64748B' for r in ranks]
bars = ax.barh(y_pos, ranks, height=0.46, color=bar_colors, edgecolor='none', zorder=3)

for bar, r in zip(bars, ranks):
    w = bar.get_width()
    is_hero = (r == 1.75)
    color = '#C82423' if is_hero else '#475569'
    weight = 'bold' if is_hero else '500'
    ax.text(w + 0.2, bar.get_y() + bar.get_height()/2, f'{r:.2f}',
            va='center', ha='left', fontsize=6.8, color=color, weight=weight)

ax.axvline(x=cd_cutoff, color='#DC2626', linestyle='--', linewidth=0.8, zorder=2)
ax.annotate(r'CD ( < 0.05$)', xy=(cd_cutoff, len(methods)-0.2), xytext=(cd_cutoff + 0.2, len(methods)-0.2),
            fontsize=6.5, color='#DC2626', weight='bold', va='center')

ax.set_yticks(y_pos)
ytick_labels = ax.set_yticklabels(methods)
ytick_labels[0].set_color('#C82423')
ytick_labels[0].set_weight('bold')

ax.set_xlim(0, 12.4)
ax.set_xlabel('Average Friedman rank', fontsize=8, labelpad=2.5)
ax.grid(axis='x', linestyle='-', linewidth=0.5, color='#F1F5F9', zorder=0)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#CBD5E1')
ax.tick_params(left=False)
ax.tick_params(colors='#64748B')

plt.tight_layout(pad=0.3)
plt.savefig('scratch/fig6_opt3_minimalist.png')
plt.close()

print('All 3 options generated.')
