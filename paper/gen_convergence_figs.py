"""
Generate publication-quality convergence (Fig 8) and NHD (Fig 9) figures
matching the ESWA/Q1 style of generate_figures.py.
"""
import os, re, sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

# ── Paths ────────────────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPY2    = os.path.join(BASE, "all_data", "npy_2")
NPY1    = os.path.join(BASE, "all_data", "npy_1")
OUT_DIR = os.path.join(BASE, "figures_new")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Data config ──────────────────────────────────────────────────────
DATASETS  = ["Adenoma","ALL_AML","ALL3","ALL4","CNS",
             "Colon","DLBCL","Lymphoma","Stroke"]
DS_LABELS = ["Adenoma","ALL-AML","ALL3","ALL4","CNS",
             "Colon","DLBCL","Lymphoma","Stroke"]
SHOW_DS   = ["Adenoma","ALL_AML","DLBCL","Lymphoma","CNS","Stroke"]
SHOW_LBLS = [DS_LABELS[DATASETS.index(d)] for d in SHOW_DS]

# Methods for convergence (all 9, proposed first)
CONV_V = ["MEL_KGEF","MEL_NHD","MEL_KGEF_noNHD","MEL",
          "FWPSO","PSO_CSM","IGPSO","SaWDE","BPSO"]
# Key methods for 3×3 all-dataset version
KEY_V  = ["MEL_KGEF","FWPSO","MEL","PSO_CSM","IGPSO"]
# NHD variants
NHD_V  = ["MEL_KGEF","MEL_NHD"]

V_LABELS = {
    "BPSO":"BPSO","SaWDE":"SaWDE","FWPSO":"FWPSO","MEL":"MEL",
    "MEL_NHD":"KDS-EL/DRS","MEL_KGEF_noNHD":"KDS-EL/KER",
    "MEL_KGEF":"KDS-EL","PSO_CSM":"PSO-CSM","IGPSO":"IGPSO",
}
COLORS = {
    "BPSO":"#9e9e9e","SaWDE":"#bdbdbd","FWPSO":"#1565c0","MEL":"#00838f",
    "MEL_NHD":"#2e7d32","MEL_KGEF_noNHD":"#f57f17",
    "MEL_KGEF":"#b71c1c","PSO_CSM":"#6a1b9a","IGPSO":"#e65100",
}
LS = {
    "BPSO":":","SaWDE":":","FWPSO":"--",
    "MEL":"-.","MEL_NHD":"--","MEL_KGEF_noNHD":"--",
    "MEL_KGEF":"-","PSO_CSM":"--","IGPSO":"--",
}
LW = {
    "BPSO":0.7,"SaWDE":0.7,"FWPSO":1.0,"MEL":0.9,
    "MEL_NHD":1.0,"MEL_KGEF_noNHD":1.0,
    "MEL_KGEF":1.8,"PSO_CSM":1.0,"IGPSO":1.0,
}
ZO = {
    "BPSO":1,"SaWDE":1,"FWPSO":3,"MEL":2,
    "MEL_NHD":4,"MEL_KGEF_noNHD":4,
    "MEL_KGEF":10,"PSO_CSM":3,"IGPSO":3,
}

# ── Style (matching generate_figures.py) ─────────────────────────────
mpl.rcParams.update({
    "font.family":"DejaVu Serif","font.size":8,
    "axes.titlesize":8,"axes.labelsize":8,
    "xtick.labelsize":7,"ytick.labelsize":7,
    "legend.fontsize":6.5,"legend.framealpha":0.92,"legend.edgecolor":"0.6",
    "axes.linewidth":0.7,"grid.linewidth":0.35,
    "xtick.major.width":0.7,"ytick.major.width":0.7,
    "xtick.major.size":2.5,"ytick.major.size":2.5,
    "axes.spines.top":False,"axes.spines.right":False,
    "figure.dpi":300,"savefig.dpi":300,
    "savefig.bbox":"tight","savefig.pad_inches":0.03,
})

# ── Pattern matching ─────────────────────────────────────────────────
DS_RE     = "|".join(DATASETS)
CURVE_PAT = re.compile(rf"^curve_(.+?)_({DS_RE})_run(\d+)\.npy$")
NHD_PAT   = re.compile(rf"^nhd_(.+?)_({DS_RE})_run(\d+)\.npy$")


def load_dir(folder, pattern):
    result = {}
    if not os.path.isdir(folder):
        print(f"  [!] Directory not found: {os.path.abspath(folder)}")
        return result
    matched = 0
    for fname in os.listdir(folder):
        m = pattern.match(fname)
        if not m: continue
        ver, ds, run = m.group(1), m.group(2), int(m.group(3))
        arr = np.load(os.path.join(folder, fname))
        result.setdefault(ver, {}).setdefault(ds, {})[run] = arr
        matched += 1
    print(f"  {folder}: {matched} files matched")
    for v in result:
        for ds in result[v]:
            rd  = result[v][ds]
            T1  = len(next(iter(rd.values())))
            mat = np.zeros((max(rd)+1, T1))
            for r, a in rd.items():
                mat[r] = a[:T1]
            result[v][ds] = mat
    return result


def merge(*dicts):
    out = {}
    for d in dicts:
        for v, dd in d.items():
            out.setdefault(v, {}).update(dd)
    return out


def plot_curves(ax, curves, versions, ds, show_std=True):
    plotted = []
    for v in versions:
        if v not in curves or ds not in curves[v]: continue
        mat   = curves[v][ds]
        T     = mat.shape[1] - 1
        iters = np.arange(T+1)
        mean  = mat.mean(axis=0)
        std   = mat.std(axis=0)
        ax.plot(iters, mean, color=COLORS[v], lw=LW.get(v, 0.9),
                linestyle=LS.get(v, "-"), zorder=ZO.get(v, 2),
                label=V_LABELS[v])
        if show_std:
            ax.fill_between(iters, mean-std, mean+std,
                            color=COLORS[v], alpha=0.08, zorder=ZO.get(v,2)-1)
        plotted.append(v)
    return plotted


def make_handles(versions, show_std=True):
    return [Line2D([0],[0], color=COLORS[v],
                   lw=LW.get(v, 0.9),
                   linestyle=LS.get(v, "-"),
                   label=V_LABELS[v])
            for v in versions]


def save_fig(fig, name):
    for ext in (".pdf", ".png"):
        fig.savefig(os.path.join(OUT_DIR, name+ext))
    plt.close(fig)
    print(f"  saved: {name}")


# ── Load data ────────────────────────────────────────────────────────
print("=== Scanning npy files ===")
c2    = load_dir(NPY2, CURVE_PAT)
c1    = load_dir(NPY1, CURVE_PAT)
nhd   = load_dir(NPY2, NHD_PAT)
all_c = merge(c2, c1)

print("\nLoaded fitness curves:")
for v in sorted(all_c):
    print(f"  {V_LABELS.get(v,v):22s}: {len(all_c[v])} datasets")

print("\nLoaded NHD curves:")
for v in sorted(nhd):
    print(f"  {V_LABELS.get(v,v):22s}: {len(nhd[v])} datasets")

if not all_c:
    print("\n[Abort] No curve_*.npy files found")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
# Fig 8: Convergence curves — 2×3, 6 representative datasets
# ══════════════════════════════════════════════════════════════════════
print("\n=== Fig 8: Convergence curves (2×3) ===")
fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.4))
axes      = axes.ravel()
all_used  = []
for ax, ds, lbl in zip(axes, SHOW_DS, SHOW_LBLS):
    used = plot_curves(ax, all_c, CONV_V, ds, show_std=True)
    all_used.extend(used)
    ax.set_title(lbl, fontsize=8, pad=2)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("Fitness", fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
    ax.grid(linestyle="--", alpha=0.4)

shown   = [v for v in CONV_V if v in set(all_used)]
handles = make_handles(shown)
fig.legend(handles=handles, loc="lower center", ncol=5,
           bbox_to_anchor=(0.5,-0.04), frameon=True, fontsize=7,
           columnspacing=0.8, handlelength=2.0)
fig.text(0.025, 0.5, "Fitness Value", va="center",
         rotation="vertical", fontsize=8)
fig.tight_layout(rect=[0.04, 0.07, 1, 1])
save_fig(fig, "fig8_convergence")


# ══════════════════════════════════════════════════════════════════════
# Fig 9: NHD diversity curves — 2×3, 6 representative datasets
# ══════════════════════════════════════════════════════════════════════
print("=== Fig 9: NHD curves (2×3) ===")
nhd_present = [v for v in NHD_V
               if v in nhd and any(ds in nhd[v] for ds in SHOW_DS)]
if nhd_present:
    fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.4))
    axes      = axes.ravel()
    for ax, ds, lbl in zip(axes, SHOW_DS, SHOW_LBLS):
        plot_curves(ax, nhd, nhd_present, ds, show_std=True)
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.set_xlabel("Iteration", fontsize=7)
        ax.set_ylabel("Population NHD", fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.grid(linestyle="--", alpha=0.4)
    handles = make_handles(nhd_present)
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5,-0.04), frameon=True, fontsize=7)
    fig.text(0.025, 0.5, "Normalised Hamming Distance", va="center",
             rotation="vertical", fontsize=8)
    fig.tight_layout(rect=[0.04, 0.07, 1, 1])
    save_fig(fig, "fig9_nhd_curves")
else:
    print("  [Skipped] nhd_* files not found")


# ══════════════════════════════════════════════════════════════════════
# Fig S1: All 9 datasets convergence — 3×3, key methods
# ══════════════════════════════════════════════════════════════════════
print("=== Fig S1: All-dataset convergence (3×3) ===")
fig, axes = plt.subplots(3, 3, figsize=(7.16, 6.5))
axes      = axes.ravel()
all_used  = []
for ax, ds, lbl in zip(axes, DATASETS, DS_LABELS):
    used = plot_curves(ax, all_c, KEY_V, ds, show_std=True)
    all_used.extend(used)
    ax.set_title(lbl, fontsize=8, pad=2)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("Fitness", fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
    ax.grid(linestyle="--", alpha=0.4)

shown   = [v for v in KEY_V if v in set(all_used)]
handles = make_handles(shown)
fig.legend(handles=handles, loc="lower center", ncol=5,
           bbox_to_anchor=(0.5,-0.03), frameon=True, fontsize=7,
           columnspacing=0.8, handlelength=2.0)
fig.text(0.025, 0.5, "Fitness Value", va="center",
         rotation="vertical", fontsize=8)
fig.tight_layout(rect=[0.04, 0.05, 1, 1])
save_fig(fig, "figS1_convergence_all9")

print("\n=== Done ===")
for f in sorted(os.listdir(OUT_DIR)):
    if f.startswith("fig8") or f.startswith("fig9") or f.startswith("figS1"):
        sz = os.path.getsize(os.path.join(OUT_DIR, f))
        print(f"  {f}  ({sz//1024} KB)")
