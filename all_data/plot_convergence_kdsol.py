# plot_convergence_kdsol.py
# KDS-EL 收敛曲线本地生成脚本
#
# 使用方法：
#   cd /d E:\360MoveData\Users\86185\Desktop\all_data
#   python plot_convergence_kdsol.py
#
# 目录结构：
#   all_data/
#     npy_2/   curve_MEL_KGEF_Adenoma_run0.npy  nhd_MEL_NHD_Stroke_run3.npy ...
#     npy_1/   curve_IGPSO_ALL4_run2.npy  curve_PSO_CSM_Colon_run0.npy ...
#     plot_convergence_kdsol.py
#     figures/  (自动创建)
#
# 命名规范（与正文统一）：
#   MEL_KGEF       → KDS-EL (Proposed)
#   MEL_NHD        → KDS-EL/DRS
#   MEL_KGEF_noNHD → KDS-EL/KER
#   MEL            → MEL
#   其余           → 保持原名

import os, re
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

NPY2_DIR = "npy_2"   # MEL系，含 curve_* 和 nhd_*
NPY1_DIR = "npy_1"   # IGPSO / PSO_CSM，只含 curve_*
OUT_DIR  = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

DATASETS  = ["Adenoma","ALL_AML","ALL3","ALL4","CNS",
             "Colon","DLBCL","Lymphoma","Stroke"]
DS_LABELS = ["Adenoma","ALL-AML","ALL3","ALL4","CNS",
             "Colon","DLBCL","Lymphoma","Stroke"]

SHOW_DS   = ["Adenoma","ALL_AML","DLBCL","Lymphoma","CNS","Stroke"]
SHOW_LBLS = [DS_LABELS[DATASETS.index(d)] for d in SHOW_DS]

# 收敛图展示的方法（按重要性排序）
CONV_V = ["BPSO","SaWDE","FWPSO","MEL",
          "MEL_NHD","MEL_KGEF_noNHD","PSO_CSM","IGPSO","MEL_KGEF"]
KEY_V  = ["FWPSO","MEL","PSO_CSM","IGPSO","MEL_KGEF"]
NHD_V  = ["MEL_NHD","MEL_KGEF"]

# ── 与正文完全统一的命名 ──────────────────────────────────────────────────
V_LABELS = {
    "BPSO":           "BPSO",
    "SaWDE":          "SaWDE",
    "FWPSO":          "FWPSO",
    "MEL":            "MEL",
    "MEL_NHD":        "KDS-EL/DRS",
    "MEL_KGEF_noNHD": "KDS-EL/KER",
    "MEL_KGEF":       "KDS-EL",
    "PSO_CSM":        "PSO-CSM",
    "IGPSO":          "IGPSO",
}
COLORS = {
    "BPSO":           "#9e9e9e",
    "SaWDE":          "#bdbdbd",
    "FWPSO":          "#1565c0",
    "MEL":            "#00838f",
    "MEL_NHD":        "#2e7d32",
    "MEL_KGEF_noNHD": "#f57f17",
    "MEL_KGEF":       "#b71c1c",
    "PSO_CSM":        "#6a1b9a",
    "IGPSO":          "#e65100",
}
LS = {
    "BPSO":":", "SaWDE":":", "FWPSO":"--",
    "MEL":"-.", "MEL_NHD":"--", "MEL_KGEF_noNHD":"--",
    "MEL_KGEF":"-", "PSO_CSM":"--", "IGPSO":"--",
}

mpl.rcParams.update({
    "font.family":"DejaVu Serif", "font.size":8,
    "axes.titlesize":8, "axes.labelsize":8,
    "xtick.labelsize":7, "ytick.labelsize":7,
    "legend.fontsize":6.5, "legend.framealpha":0.92,
    "legend.edgecolor":"0.6",
    "axes.linewidth":0.7, "grid.linewidth":0.35,
    "axes.spines.top":False, "axes.spines.right":False,
    "figure.dpi":300, "savefig.dpi":300,
    "savefig.bbox":"tight", "savefig.pad_inches":0.03,
})

DS_RE     = "|".join(DATASETS)
CURVE_PAT = re.compile(rf"^curve_(.+?)_({DS_RE})_run(\d+)\.npy$")
NHD_PAT   = re.compile(rf"^nhd_(.+?)_({DS_RE})_run(\d+)\.npy$")


def load_dir(folder, pattern):
    result = {}
    if not os.path.isdir(folder):
        print(f"  [!] 目录不存在: {os.path.abspath(folder)}")
        return result
    matched = 0
    for fname in os.listdir(folder):
        m = pattern.match(fname)
        if not m: continue
        ver, ds, run = m.group(1), m.group(2), int(m.group(3))
        arr = np.load(os.path.join(folder, fname))
        result.setdefault(ver, {}).setdefault(ds, {})[run] = arr
        matched += 1
    print(f"  {folder}: {matched} 文件匹配")
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


def plot_curves(ax, curves, versions, ds):
    plotted = []
    for v in versions:
        if v not in curves or ds not in curves[v]: continue
        mat   = curves[v][ds]
        T     = mat.shape[1] - 1
        iters = np.arange(T+1)
        mean  = mat.mean(axis=0)
        std   = mat.std(axis=0)
        lw    = 1.6 if v == "MEL_KGEF" else 0.85
        zo    = 10  if v == "MEL_KGEF" else 2
        ax.plot(iters, mean, color=COLORS[v], lw=lw,
                linestyle=LS.get(v,"-"), zorder=zo,
                label=V_LABELS[v])
        ax.fill_between(iters, mean-std, mean+std,
                        color=COLORS[v], alpha=0.10, zorder=zo-1)
        plotted.append(v)
    return plotted


def make_legend(versions):
    return [Line2D([0],[0], color=COLORS[v],
                   lw=1.6 if v=="MEL_KGEF" else 0.9,
                   linestyle=LS.get(v,"-"),
                   label=V_LABELS[v])
            for v in versions]


def save_fig(fig, name):
    for ext in (".pdf", ".png"):
        fig.savefig(os.path.join(OUT_DIR, name+ext))
    print(f"  saved: {name}")


# ── 载入数据 ──────────────────────────────────────────────────────────────
print("=== 扫描 npy 文件 ===")
c2    = load_dir(NPY2_DIR, CURVE_PAT)
c1    = load_dir(NPY1_DIR, CURVE_PAT)
nhd   = load_dir(NPY2_DIR, NHD_PAT)
all_c = merge(c2, c1)

print("\n已载入 fitness 曲线：")
for v in sorted(all_c):
    ds_list = sorted(all_c[v])
    runs    = [all_c[v][d].shape[0] for d in ds_list]
    print(f"  {V_LABELS.get(v,v):22s}: {len(ds_list)} 数据集  runs={runs}")

print("\n已载入 NHD 曲线：")
for v in sorted(nhd):
    print(f"  {V_LABELS.get(v,v):22s}: {len(nhd[v])} 数据集")

if not all_c:
    print("\n[中止] 未找到任何 curve_*.npy 文件")
    raise SystemExit(1)


# ── Fig 10a: 6 数据集 × 全方法，2×3 ─────────────────────────────────────
print("\n=== Fig 10a: 收敛曲线（6 数据集）===")
fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.4))
axes      = axes.ravel()
all_used  = []
for ax, ds, lbl in zip(axes, SHOW_DS, SHOW_LBLS):
    used = plot_curves(ax, all_c, CONV_V, ds)
    all_used.extend(used)
    ax.set_title(lbl, fontsize=8, pad=2)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("Fitness", fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
    ax.grid(linestyle="--", alpha=0.4)

shown   = [v for v in CONV_V if v in set(all_used)]
handles = make_legend(shown)
fig.legend(handles=handles, loc="lower center", ncol=5,
           bbox_to_anchor=(0.5,-0.04), frameon=True, fontsize=7,
           columnspacing=0.8, handlelength=2.0)
fig.tight_layout(rect=[0, 0.07, 1, 1])
save_fig(fig, "fig10a_convergence")
plt.close(fig)


# ── Fig 10b: NHD 曲线，2×3 ────────────────────────────────────────────────
print("=== Fig 10b: NHD 曲线 ===")
nhd_present = [v for v in NHD_V
               if v in nhd and any(ds in nhd[v] for ds in SHOW_DS)]
if nhd_present:
    fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.4))
    axes      = axes.ravel()
    for ax, ds, lbl in zip(axes, SHOW_DS, SHOW_LBLS):
        plot_curves(ax, nhd, nhd_present, ds)
        ax.set_title(lbl, fontsize=8, pad=2)
        ax.set_xlabel("Iteration", fontsize=7)
        ax.set_ylabel("Population NHD", fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.grid(linestyle="--", alpha=0.4)
    handles = make_legend(nhd_present)
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5,-0.04), frameon=True, fontsize=7)
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    save_fig(fig, "fig10b_nhd_curves")
    plt.close(fig)
else:
    print("  [跳过] nhd_* 文件未找到")


# ── Fig 10c: 全 9 数据集 × 关键方法，3×3 ────────────────────────────────
print("=== Fig 10c: 全数据集收敛曲线（3×3）===")
fig, axes = plt.subplots(3, 3, figsize=(7.16, 6.5))
axes      = axes.ravel()
all_used  = []
for ax, ds, lbl in zip(axes, DATASETS, DS_LABELS):
    used = plot_curves(ax, all_c, KEY_V, ds)
    all_used.extend(used)
    ax.set_title(lbl, fontsize=8, pad=2)
    ax.set_xlabel("Iteration", fontsize=7)
    ax.set_ylabel("Fitness", fontsize=7)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
    ax.grid(linestyle="--", alpha=0.4)

shown   = [v for v in KEY_V if v in set(all_used)]
handles = make_legend(shown)
fig.legend(handles=handles, loc="lower center", ncol=5,
           bbox_to_anchor=(0.5,-0.03), frameon=True, fontsize=7,
           columnspacing=0.8, handlelength=2.0)
fig.tight_layout(rect=[0, 0.05, 1, 1])
save_fig(fig, "fig10c_convergence_all")
plt.close(fig)

print("\n=== 完成 ===")
print("输出目录:", os.path.abspath(OUT_DIR))
for f in sorted(os.listdir(OUT_DIR)):
    if "fig10" in f:
        sz = os.path.getsize(os.path.join(OUT_DIR, f))
        print(f"  {f}  ({sz//1024} KB)")
