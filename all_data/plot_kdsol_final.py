"""
plot_kdsol_final.py
===================
KDS-EL 完整作图脚本（IEEE / Applied Soft Computing Q1 标准）

命名规范（全文统一）
--------------------
CSV 版本名          → 图中显示名
BPSO               → BPSO
SaWDE              → SaWDE
FWPSO              → FWPSO
MEL                → MEL
MEL_NHD            → KDS-EL/DRS      (只含DRS，无KER)
MEL_KGEF_noNHD     → KDS-EL/KER      (只含KER，无DRS)
MEL_KGEF           → KDS-EL          (proposed，完整框架)
PSO_CSM            → PSO-CSM
IGPSO              → IGPSO

消融组名称（无 w/o）
MEL                → MEL (Baseline)
MEL_NHD            → KDS-EL/DRS
MEL_KGEF_noNHD     → KDS-EL/KER
MEL_KGEF           → KDS-EL (Proposed)
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

try:
    from scipy import stats
except ImportError:
    class _StatsFallback:
        @staticmethod
        def wilcoxon(*args, **kwargs):
            return 0.0, float('nan')

        @staticmethod
        def friedmanchisquare(*args, **kwargs):
            return 0.0, float('nan')

    stats = _StatsFallback()

warnings.filterwarnings("ignore")

CSV_PATH = "all_data.csv"
OUT_DIR  = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

DATASETS  = ['Adenoma','ALL_AML','ALL3','ALL4','CNS','Colon','DLBCL','Lymphoma','Stroke']
DS_LABELS = ['Adenoma','ALL-AML','ALL3','ALL4','CNS','Colon','DLBCL','Lymphoma','Stroke']

ALL_V  = ['BPSO','SaWDE','FWPSO','MEL','MEL_NHD','MEL_KGEF_noNHD','MEL_KGEF','PSO_CSM','IGPSO']
ABL_V  = ['MEL','MEL_NHD','MEL_KGEF_noNHD','MEL_KGEF']

# ── 统一命名映射 ────────────────────────────────────────────────────────────
V_LABELS = {
    'BPSO':           'BPSO',
    'SaWDE':          'SaWDE',
    'FWPSO':          'FWPSO',
    'MEL':            'MEL',
    'MEL_NHD':        'KDS-EL/DRS',
    'MEL_KGEF_noNHD': 'KDS-EL/KER',
    'MEL_KGEF':       'KDS-EL',
    'PSO_CSM':        'PSO-CSM',
    'IGPSO':          'IGPSO',
}

ABL_LABELS = {
    'MEL':            'MEL (Baseline)',
    'MEL_NHD':        'KDS-EL/DRS',
    'MEL_KGEF_noNHD': 'KDS-EL/KER',
    'MEL_KGEF':       'KDS-EL (Proposed)',
}

# ── 颜色 + 填充（colorblind-safe，IEEE标准） ─────────────────────────────────
COLORS = {
    'BPSO':           '#9e9e9e',
    'SaWDE':          '#bdbdbd',
    'FWPSO':          '#1565c0',
    'MEL':            '#00838f',
    'MEL_NHD':        '#2e7d32',
    'MEL_KGEF_noNHD': '#f57f17',
    'MEL_KGEF':       '#b71c1c',
    'PSO_CSM':        '#6a1b9a',
    'IGPSO':          '#e65100',
}
HATCHES = {
    'BPSO':'////', 'SaWDE':'\\\\\\\\', 'FWPSO':'----',
    'MEL':'....', 'MEL_NHD':'xxxx', 'MEL_KGEF_noNHD':'++++',
    'MEL_KGEF':'', 'PSO_CSM':'oooo', 'IGPSO':'****',
}
LS = {
    'BPSO':':', 'SaWDE':':', 'FWPSO':'--',
    'MEL':'-.', 'MEL_NHD':'--', 'MEL_KGEF_noNHD':'--',
    'MEL_KGEF':'-', 'PSO_CSM':'--', 'IGPSO':'--',
}

# ── IEEE rcParams ─────────────────────────────────────────────────────────────
mpl.rcParams.update({
    'font.family':'DejaVu Serif', 'font.size':8,
    'axes.titlesize':8, 'axes.labelsize':8,
    'xtick.labelsize':7, 'ytick.labelsize':7,
    'legend.fontsize':6.5, 'legend.framealpha':0.92,
    'legend.edgecolor':'0.6', 'legend.borderpad':0.4,
    'axes.linewidth':0.7, 'grid.linewidth':0.35,
    'lines.linewidth':0.9, 'patch.linewidth':0.45,
    'xtick.major.width':0.7, 'ytick.major.width':0.7,
    'xtick.major.size':2.5, 'ytick.major.size':2.5,
    'axes.spines.top':False, 'axes.spines.right':False,
    'figure.dpi':300, 'savefig.dpi':300,
    'savefig.bbox':'tight', 'savefig.pad_inches':0.03,
})

def g(v, ds, m='Accuracy'):
    return df[(df.Version==v)&(df.Dataset==ds)][m].values

def make_handles(versions, use_abl=False):
    out = []
    for v in versions:
        lbl = ABL_LABELS[v] if use_abl else V_LABELS.get(v, v)
        p = mpatches.Patch(
            facecolor=COLORS[v],
            hatch=HATCHES[v],
            edgecolor='k' if HATCHES[v] else COLORS[v],
            linewidth=0.4, label=lbl)
        out.append(p)
    return out

def bar_group(ax, versions, ds, metric, use_abl=False, log=False):
    n = len(versions)
    x = np.arange(n)
    w = 0.62
    means = [g(v,ds,metric).mean() for v in versions]
    stds  = [g(v,ds,metric).std()  for v in versions]
    bars  = ax.bar(x, means, w,
                   color=[COLORS[v] for v in versions],
                   edgecolor='k', linewidth=0.4,
                   yerr=stds,
                   error_kw=dict(elinewidth=0.55,capsize=1.5,
                                 capthick=0.55,ecolor='0.35'))
    for bar, v in zip(bars, versions):
        if HATCHES[v]: bar.set_hatch(HATCHES[v])
    if 'MEL_KGEF' in versions:
        ki = versions.index('MEL_KGEF')
        bars[ki].set_edgecolor('#b71c1c')
        bars[ki].set_linewidth(1.1)
    lbls = [ABL_LABELS[v] if use_abl else V_LABELS.get(v,v) for v in versions]
    ax.set_xticks(x)
    ax.set_xticklabels(lbls, rotation=45, ha='right', fontsize=6.2)
    ax.grid(axis='y', linestyle='--', alpha=0.45, linewidth=0.35)
    if log: ax.set_yscale('log')
    return bars

def save(fig, name):
    for ext in ('.pdf','.png'):
        fig.savefig(os.path.join(OUT_DIR, name+ext))
    print(f'  saved: {name}')


# ═══════════════════════════════════════════════════════════════════════════
# Fig 1 — Accuracy (3×3)
# ═══════════════════════════════════════════════════════════════════════════
def fig_accuracy():
    print('Fig 1: Accuracy comparison...')
    fig, axes = plt.subplots(3, 3, figsize=(7.16, 5.4))
    axes = axes.ravel()
    for ax, ds, lbl in zip(axes, DATASETS, DS_LABELS):
        bar_group(ax, ALL_V, ds, 'Accuracy')
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune='lower'))
        mn = min(g(v,ds).mean()-g(v,ds).std() for v in ALL_V)
        mx = max(g(v,ds).mean()+g(v,ds).std() for v in ALL_V)
        pad = (mx-mn)*0.15
        ax.set_ylim(max(0, mn-pad-0.005), min(1.0, mx+pad+0.005))
    handles = make_handles(ALL_V)
    fig.legend(handles=handles, loc='lower center', ncol=5,
               bbox_to_anchor=(0.5,-0.04), frameon=True,
               columnspacing=0.7, handlelength=1.1, handleheight=0.85)
    fig.text(0.025, 0.5, 'Classification Accuracy', va='center',
             rotation='vertical', fontsize=8)
    fig.tight_layout(rect=[0.04, 0.07, 1, 1])
    save(fig, 'fig1_accuracy')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 2 — Features (3×3, log)
# ═══════════════════════════════════════════════════════════════════════════
def fig_features():
    print('Fig 2: Feature count...')
    fig, axes = plt.subplots(3, 3, figsize=(7.16, 5.4))
    axes = axes.ravel()
    for ax, ds, lbl in zip(axes, DATASETS, DS_LABELS):
        bar_group(ax, ALL_V, ds, 'Num_Features', log=True)
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda y,_: f'{int(y):,}'))
        ax.grid(axis='y', linestyle='--', alpha=0.45, which='both')
    handles = make_handles(ALL_V)
    fig.legend(handles=handles, loc='lower center', ncol=5,
               bbox_to_anchor=(0.5,-0.04), frameon=True,
               columnspacing=0.7, handlelength=1.1, handleheight=0.85)
    fig.text(0.025, 0.5, 'Number of Selected Features (log scale)',
             va='center', rotation='vertical', fontsize=8)
    fig.tight_layout(rect=[0.04, 0.07, 1, 1])
    save(fig, 'fig2_features')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 3 — Ablation (dual panel, KDS-EL naming, no w/o)
# ═══════════════════════════════════════════════════════════════════════════
def fig_ablation():
    print('Fig 3: Ablation...')
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.1))
    n_ds = len(DATASETS)
    x    = np.arange(n_ds)
    n_v  = len(ABL_V)
    w    = 0.68 / n_v
    offs = np.linspace(-(n_v-1)/2*w, (n_v-1)/2*w, n_v)

    for panel, (ax, metric, ylabel) in enumerate(zip(
        axes,
        ['Accuracy', 'Num_Features'],
        ['Classification Accuracy', 'Number of Selected Features']
    )):
        for v, off in zip(ABL_V, offs):
            lbl   = ABL_LABELS[v]
            means = [g(v, ds, metric).mean() for ds in DATASETS]
            stds  = [g(v, ds, metric).std()  for ds in DATASETS]
            bars  = ax.bar(x+off, means, w,
                           color=COLORS[v], edgecolor='k', linewidth=0.4,
                           label=lbl, yerr=stds,
                           error_kw=dict(elinewidth=0.5, capsize=1.2,
                                         capthick=0.5, ecolor='0.35'))
            for bar in bars:
                if HATCHES[v]: bar.set_hatch(HATCHES[v])

        ax.set_xticks(x)
        ax.set_xticklabels(DS_LABELS, rotation=40, ha='right', fontsize=7)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.45)
        if metric == 'Num_Features':
            ax.set_yscale('log')
            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(lambda y,_: f'{int(y):,}'))
            ax.grid(axis='y', linestyle='--', alpha=0.45, which='both')
        if panel == 0:
            handles = make_handles(ABL_V, use_abl=True)
            ax.legend(handles=handles, fontsize=7, ncol=2,
                      loc='lower right', frameon=True,
                      handlelength=1.1, handleheight=0.85)

    fig.tight_layout(w_pad=2.5)
    save(fig, 'fig3_ablation')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 4 — Boxplots
# ═══════════════════════════════════════════════════════════════════════════
def fig_boxplot():
    print('Fig 4: Boxplots...')
    BOX_V  = ['FWPSO','PSO_CSM','IGPSO','MEL_KGEF']
    BOX_LB = ['FWPSO','PSO-CSM','IGPSO','KDS-EL\n(Proposed)']

    fig, axes = plt.subplots(3, 3, figsize=(7.16, 5.5))
    axes = axes.ravel()
    for ax, ds, dslbl in zip(axes, DATASETS, DS_LABELS):
        data = [g(v, ds) for v in BOX_V]
        bp   = ax.boxplot(data, patch_artist=True, widths=0.52,
                          medianprops=dict(color='k', linewidth=1.1),
                          whiskerprops=dict(linewidth=0.65),
                          capprops=dict(linewidth=0.65),
                          flierprops=dict(marker='o', markersize=2,
                                          linewidth=0.4,
                                          markeredgecolor='0.5',
                                          markerfacecolor='none'),
                          boxprops=dict(linewidth=0.55))
        for patch, v in zip(bp['boxes'], BOX_V):
            patch.set_facecolor(COLORS[v]); patch.set_alpha(0.72)

        kgef = g('MEL_KGEF', ds)
        all_vals = np.concatenate(data)
        ymax = all_vals.max(); rng = all_vals.max()-all_vals.min()
        for ci, v in enumerate(BOX_V[:-1]):
            _, p = stats.wilcoxon(kgef, g(v, ds))
            if p < 0.05:
                y   = ymax + rng*0.04*(ci+1)
                sym = '***' if p<0.001 else '**' if p<0.01 else '*'
                ax.plot([ci+1,ci+1,4,4],
                        [y, y+rng*0.015, y+rng*0.015, y],
                        lw=0.7, c='k')
                ax.text((ci+1+4)/2, y+rng*0.015, sym,
                        ha='center', va='bottom', fontsize=5.5)

        ax.set_title(dslbl, fontsize=8, pad=2)
        ax.set_xticks(range(1,5))
        ax.set_xticklabels(BOX_LB, fontsize=6.2)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4))
        ax.grid(axis='y', linestyle='--', alpha=0.45)
    fig.text(0.025, 0.5, 'Classification Accuracy', va='center',
             rotation='vertical', fontsize=8)
    fig.tight_layout(rect=[0.04, 0, 1, 1])
    save(fig, 'fig4_boxplot')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 5 — Trade-off scatter
# ═══════════════════════════════════════════════════════════════════════════
def fig_tradeoff():
    print('Fig 5: Trade-off scatter...')
    SHOW = ['Adenoma','ALL_AML','Colon','DLBCL','Lymphoma','Stroke']
    SLBL = [DS_LABELS[DATASETS.index(d)] for d in SHOW]

    fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.2))
    axes = axes.ravel()
    for ax, ds, lbl in zip(axes, SHOW, SLBL):
        total = df[df.Dataset==ds]['Num_Features'].max()*1.05+1
        for v in ALL_V:
            vals = df[(df.Version==v)&(df.Dataset==ds)]
            acc  = vals['Accuracy'].values * 100
            nf   = vals['Num_Features'].values / total * 100
            ms_  = 30 if v=='MEL_KGEF' else 12
            mk_  = '*' if v=='MEL_KGEF' else 'o'
            zo_  = 10 if v=='MEL_KGEF' else 2
            ax.scatter(nf, acc, color=COLORS[v], s=ms_, zorder=zo_,
                       marker=mk_, linewidths=0, alpha=0.85,
                       label=V_LABELS[v])
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.set_xlabel('Feature ratio (%)', fontsize=7)
        ax.set_ylabel('Accuracy (%)', fontsize=7)
        ax.grid(linestyle='--', alpha=0.38)

    handles = make_handles(ALL_V)
    fig.legend(handles=handles, loc='lower center', ncol=5,
               bbox_to_anchor=(0.5,-0.04), frameon=True, fontsize=7,
               columnspacing=0.7, handlelength=1.0)
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    save(fig, 'fig5_tradeoff')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 6 — Average Friedman Rank
# ═══════════════════════════════════════════════════════════════════════════
def fig_rank():
    print('Fig 6: Friedman rank...')
    ranks = {v:[] for v in ALL_V}
    for ds in DATASETS:
        means = {v: g(v,ds).mean() for v in ALL_V}
        for r, v in enumerate(sorted(means, key=means.get, reverse=True), 1):
            ranks[v].append(r)
    avg = {v: np.mean(ranks[v]) for v in ALL_V}
    se  = {v: np.std(ranks[v])/np.sqrt(len(DATASETS)) for v in ALL_V}
    sv  = sorted(avg, key=avg.get)

    fig, ax = plt.subplots(figsize=(3.54, 2.9))
    y    = np.arange(len(sv))
    vals = [avg[v] for v in sv]
    errs = [se[v]  for v in sv]
    bars = ax.barh(y, vals, 0.6,
                   color=[COLORS[v] for v in sv],
                   edgecolor='k', linewidth=0.4,
                   xerr=errs,
                   error_kw=dict(elinewidth=0.55, capsize=2, capthick=0.55))
    for bar, v in zip(bars, sv):
        if HATCHES[v]: bar.set_hatch(HATCHES[v])

    ki = sv.index('MEL_KGEF')
    ax.annotate('KDS-EL\n(Proposed)',
                xy=(avg['MEL_KGEF'], ki),
                xytext=(avg['MEL_KGEF']+1.1, ki),
                arrowprops=dict(arrowstyle='->', lw=0.75, color='k'),
                fontsize=6.5, va='center')

    ax.set_yticks(y)
    ax.set_yticklabels([V_LABELS[v] for v in sv], fontsize=7)
    ax.set_xlabel('Average Friedman Rank', fontsize=8)
    ax.set_xlim(0, max(vals)+2.2)
    ax.grid(axis='x', linestyle='--', alpha=0.45)
    ax.invert_yaxis()

    matrix = np.array([[g(v,ds).mean() for v in ALL_V] for ds in DATASETS])
    chi2, p = stats.friedmanchisquare(*[matrix[:,i] for i in range(len(ALL_V))])
    ax.set_title(f'Friedman: $\\chi^2$={chi2:.2f}, p={p:.2e}', fontsize=7.5, pad=3)
    fig.tight_layout()
    save(fig, 'fig6_rank')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 7 — NHD Diversity
# ═══════════════════════════════════════════════════════════════════════════
def fig_nhd():
    print('Fig 7: NHD diversity...')
    NHD_V  = ['MEL_NHD','MEL_KGEF','PSO_CSM','IGPSO']
    valid  = [v for v in NHD_V
              if df[(df.Version==v)]['Avg_NHD'].mean() > 0]

    fig, ax = plt.subplots(figsize=(7.16, 2.7))
    n_ds = len(DATASETS); n_v = len(valid)
    w    = 0.68 / n_v
    x    = np.arange(n_ds)
    offs = np.linspace(-(n_v-1)/2*w, (n_v-1)/2*w, n_v)

    for v, off in zip(valid, offs):
        means = [g(v, ds, 'Avg_NHD').mean() for ds in DATASETS]
        stds  = [g(v, ds, 'Avg_NHD').std()  for ds in DATASETS]
        bars  = ax.bar(x+off, means, w,
                       color=COLORS[v], edgecolor='k', linewidth=0.4,
                       label=V_LABELS[v], yerr=stds,
                       error_kw=dict(elinewidth=0.5, capsize=1.2,
                                     capthick=0.5, ecolor='0.35'))
        for bar in bars:
            if HATCHES[v]: bar.set_hatch(HATCHES[v])

    ax.set_xticks(x)
    ax.set_xticklabels(DS_LABELS, fontsize=7)
    ax.set_ylabel('Mean Population NHD', fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
    ax.grid(axis='y', linestyle='--', alpha=0.45)
    handles = make_handles(valid)
    ax.legend(handles=handles, ncol=2, fontsize=7,
              loc='upper right', frameon=True, handlelength=1.1)
    fig.tight_layout()
    save(fig, 'fig7_nhd')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 8 — Runtime (split panel)
# ═══════════════════════════════════════════════════════════════════════════
def fig_runtime():
    print('Fig 8: Runtime...')
    RT_V  = ['BPSO','SaWDE','FWPSO','MEL','PSO_CSM','IGPSO','MEL_KGEF']
    RT_LB = [V_LABELS[v] for v in RT_V]
    EXCL  = [ds for ds in DATASETS if ds != 'Stroke']
    EXCL_LB = [DS_LABELS[DATASETS.index(d)] for d in EXCL]

    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.7))

    # Panel A: all datasets except Stroke
    ax = axes[0]
    n_ds = len(EXCL); n_v = len(RT_V)
    w = 0.68/n_v; x = np.arange(n_ds)
    offs = np.linspace(-(n_v-1)/2*w, (n_v-1)/2*w, n_v)
    for v, off in zip(RT_V, offs):
        means = [g(v, ds, 'Time_sec').mean() for ds in EXCL]
        bars  = ax.bar(x+off, means, w,
                       color=COLORS[v], edgecolor='k', linewidth=0.35,
                       label=V_LABELS[v])
        for bar in bars:
            if HATCHES[v]: bar.set_hatch(HATCHES[v])
    ax.set_xticks(x)
    ax.set_xticklabels(EXCL_LB, rotation=38, ha='right', fontsize=7)
    ax.set_ylabel('Avg. Runtime (s)', fontsize=8)
    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y,_: f'{int(y)}' if y>=10 else f'{y:.1f}'))
    ax.grid(axis='y', linestyle='--', alpha=0.45, which='both')
    ax.set_title('Datasets (excl. Stroke)', fontsize=8, pad=2)

    # Panel B: Stroke only
    ax = axes[1]
    means_stroke = [g(v, 'Stroke', 'Time_sec').mean() for v in RT_V]
    x2 = np.arange(len(RT_V))
    bars = ax.bar(x2, means_stroke, 0.58,
                  color=[COLORS[v] for v in RT_V],
                  edgecolor='k', linewidth=0.4)
    for bar, v in zip(bars, RT_V):
        if HATCHES[v]: bar.set_hatch(HATCHES[v])
    ki = RT_V.index('MEL_KGEF')
    ax.annotate(f"{means_stroke[ki]:.0f}s",
                xy=(ki, means_stroke[ki]),
                xytext=(ki+0.35, means_stroke[ki]+25),
                arrowprops=dict(arrowstyle='->', lw=0.7),
                fontsize=6.5, color='#b71c1c')
    ax.set_xticks(x2)
    ax.set_xticklabels(RT_LB, rotation=38, ha='right', fontsize=7)
    ax.set_ylabel('Avg. Runtime (s)', fontsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.45)
    ax.set_title('Stroke ($d=26,877$)', fontsize=8, pad=2)

    handles = make_handles(RT_V, False)
    fig.legend(handles=handles, loc='lower center', ncol=4,
               bbox_to_anchor=(0.5,-0.08), frameon=True, fontsize=7,
               columnspacing=0.7, handlelength=1.1)
    fig.tight_layout(rect=[0, 0.1, 1, 1])
    save(fig, 'fig8_runtime')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 9 — Wilcoxon significance heatmap
# ═══════════════════════════════════════════════════════════════════════════
def fig_wilcoxon():
    print('Fig 9: Wilcoxon heatmap...')
    COMP_V  = ['BPSO','SaWDE','FWPSO','MEL','MEL_NHD',
               'MEL_KGEF_noNHD','PSO_CSM','IGPSO']
    COMP_LB = ['BPSO','SaWDE','FWPSO','MEL',
               'KDS-EL/DRS','KDS-EL/KER','PSO-CSM','IGPSO']

    pmat = np.zeros((len(DATASETS), len(COMP_V)))
    dmat = np.zeros_like(pmat)
    for i, ds in enumerate(DATASETS):
        a = g('MEL_KGEF', ds)
        for j, v in enumerate(COMP_V):
            b = g(v, ds)
            n = min(len(a), len(b))
            try:
                _, p = stats.wilcoxon(a[:n], b[:n])
            except:
                p = 1.0
            pmat[i,j] = p
            dmat[i,j] = 1 if a.mean() > b.mean() else -1

    fig, ax = plt.subplots(figsize=(5.6, 3.3))
    cmap_w = plt.cm.Greens
    cmap_l = plt.cm.Reds
    img = np.zeros((*pmat.shape, 4))
    for i in range(pmat.shape[0]):
        for j in range(pmat.shape[1]):
            p   = pmat[i,j]
            sig = 0.82 if p<0.001 else 0.62 if p<0.01 else 0.42 if p<0.05 else 0.17
            img[i,j] = cmap_w(sig) if dmat[i,j]>0 else cmap_l(sig)
    ax.imshow(img, aspect='auto')

    for i in range(pmat.shape[0]):
        for j in range(pmat.shape[1]):
            p   = pmat[i,j]
            txt = '***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'ns'
            col = 'white' if p<0.05 else '0.55'
            ax.text(j, i, txt, ha='center', va='center',
                    fontsize=6.5, color=col,
                    fontweight='bold' if p<0.05 else 'normal')

    ax.set_xticks(range(len(COMP_V)))
    ax.set_xticklabels(COMP_LB, fontsize=7)
    ax.set_yticks(range(len(DATASETS)))
    ax.set_yticklabels(DS_LABELS, fontsize=7)
    ax.set_title('Wilcoxon Signed-Rank Test: KDS-EL vs. Competitors',
                 fontsize=8, pad=4)

    from matplotlib.patches import Patch
    legend_elems = [
        Patch(facecolor=cmap_w(0.82), label='Win (p<0.001)'),
        Patch(facecolor=cmap_w(0.62), label='Win (p<0.01)'),
        Patch(facecolor=cmap_w(0.42), label='Win (p<0.05)'),
        Patch(facecolor=cmap_w(0.17), label='Win (ns)'),
        Patch(facecolor=cmap_l(0.42), label='Loss (p<0.05)'),
        Patch(facecolor=cmap_l(0.17), label='Loss (ns)'),
    ]
    ax.legend(handles=legend_elems, loc='lower center',
              bbox_to_anchor=(0.5,-0.42), ncol=3, fontsize=6.5, frameon=True)
    fig.tight_layout(rect=[0, 0.12, 1, 1])
    save(fig, 'fig9_wilcoxon')
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════
# Fig 11 — Radar chart
# ═══════════════════════════════════════════════════════════════════════════
def fig_radar():
    print('Fig 11: Radar chart...')
    RV   = ['FWPSO','MEL','MEL_NHD','MEL_KGEF_noNHD','PSO_CSM','IGPSO','MEL_KGEF']
    cats = ['Accuracy','Feature\nReduction','Stability','Speed','Diversity']
    N    = len(cats)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    def sc_acc(v):
        return np.mean([g(v,ds).mean() for ds in DATASETS])
    def sc_feat(v):
        vals = np.array([g(v,ds,'Num_Features').mean() for ds in DATASETS])
        mx   = max(g(vv,ds,'Num_Features').mean() for vv in RV for ds in DATASETS)
        return np.mean(1-vals/mx)
    def sc_stab(v):
        vals = np.array([g(v,ds).std() for ds in DATASETS])
        mx   = max(g(vv,ds).std() for vv in RV for ds in DATASETS)
        return np.mean(1-vals/mx)
    def sc_speed(v):
        vals = np.array([g(v,ds,'Time_sec').mean() for ds in DATASETS])
        mx   = max(g(vv,ds,'Time_sec').mean() for vv in RV for ds in DATASETS)
        return np.mean(1-vals/mx)
    def sc_nhd(v):
        vals  = [g(v,ds,'Avg_NHD').mean() for ds in DATASETS]
        valid = [x for x in vals if x>0]
        if not valid: return 0.0
        mx = max(g(vv,ds,'Avg_NHD').mean()
                 for vv in RV for ds in DATASETS
                 if g(vv,ds,'Avg_NHD').mean()>0)
        return np.mean([x/mx for x in valid])

    fig, ax = plt.subplots(figsize=(3.54, 3.54),
                           subplot_kw=dict(polar=True))
    for v in RV:
        sc  = [sc_acc(v), sc_feat(v), sc_stab(v), sc_speed(v), sc_nhd(v)]
        sc += sc[:1]
        lw  = 1.8 if v=='MEL_KGEF' else 0.9
        ls  = '-' if v=='MEL_KGEF' else '--'
        alp = 0.25 if v=='MEL_KGEF' else 0.0
        ax.plot(angles, sc, color=COLORS[v], lw=lw, ls=ls,
                label=V_LABELS[v])
        ax.fill(angles, sc, color=COLORS[v], alpha=alp)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, fontsize=7.5)
    ax.set_yticklabels([])
    ax.set_ylim(0, 1)
    ax.grid(linewidth=0.45, linestyle='--', alpha=0.55)
    ax.spines['polar'].set_linewidth(0.6)

    handles = [Line2D([0],[0], color=COLORS[v],
                      lw=1.8 if v=='MEL_KGEF' else 0.9,
                      ls='-' if v=='MEL_KGEF' else '--',
                      label=V_LABELS[v])
               for v in RV]
    ax.legend(handles=handles, loc='upper right',
              bbox_to_anchor=(1.42, 1.18), fontsize=6.5,
              frameon=True, ncol=1)
    fig.tight_layout()
    save(fig, 'fig11_radar')
    plt.close(fig)


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print(f'Data: {len(df)} rows | {df.Version.nunique()} versions\n')
    fig_accuracy()
    fig_features()
    fig_ablation()
    fig_boxplot()
    fig_tradeoff()
    fig_rank()
    fig_nhd()
    fig_runtime()
    fig_wilcoxon()
    fig_radar()
    print(f'\nAll figures → ./{OUT_DIR}/')
