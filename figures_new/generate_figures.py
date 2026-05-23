import os, warnings
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from scipy import stats

warnings.filterwarnings("ignore")

# ── Data ─────────────────────────────────────────────────────────────
df = pd.read_csv("all_data1.csv")
df = df[df["Dataset"] != "ALL3"].copy()

DATASETS = ["Adenoma","ALL_AML","ALL4","CNS","Colon","DLBCL","Leukaemia","Lymphoma","Stroke"]
DS_LABELS = ["Adenoma","ALL-AML","ALL4","CNS","Colon","DLBCL","Leukaemia","Lymphoma","Stroke"]
ALL_V  = ["MEL_KGEF","MEL_NHD","MEL_KGEF_noNHD","MEL","FWPSO","PSO_CSM","IGPSO","SaWDE","BPSO"]
ABL_V  = ["MEL_KGEF","MEL_NHD","MEL_KGEF_noNHD","MEL"]
ABL_LB = ["KDS-EL\n(Proposed)","KDS-EL/DRS","KDS-EL/KER","MEL\n(Baseline)"]

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
HATCHES = {
    "BPSO":"////","SaWDE":"\\\\\\\\","FWPSO":"----","MEL":"....",
    "MEL_NHD":"xxxx","MEL_KGEF_noNHD":"++++",
    "MEL_KGEF":"","PSO_CSM":"oooo","IGPSO":"****",
}

mpl.rcParams.update({
    "font.family":"DejaVu Serif","font.size":8,
    "axes.titlesize":8,"axes.labelsize":8,
    "xtick.labelsize":7,"ytick.labelsize":7,
    "legend.fontsize":6.5,"legend.framealpha":0.92,"legend.edgecolor":"0.6",
    "axes.linewidth":0.7,"grid.linewidth":0.35,"patch.linewidth":0.45,
    "xtick.major.width":0.7,"ytick.major.width":0.7,
    "xtick.major.size":2.5,"ytick.major.size":2.5,
    "axes.spines.top":False,"axes.spines.right":False,
    "figure.dpi":300,"savefig.dpi":300,
    "savefig.bbox":"tight","savefig.pad_inches":0.03,
})

OUT = "figures_final"
os.makedirs(OUT, exist_ok=True)

def g(v, ds, m="Accuracy"):
    return df[(df.Version==v)&(df.Dataset==ds)][m].values

def make_handles(versions, labels=None):
    out = []
    for i,v in enumerate(versions):
        lbl = labels[i] if labels else V_LABELS.get(v,v)
        out.append(mpatches.Patch(
            facecolor=COLORS[v], hatch=HATCHES[v],
            edgecolor="k" if HATCHES[v] else COLORS[v],
            linewidth=0.4, label=lbl))
    return out

def save(fig, name):
    for ext in (".pdf",".png"):
        fig.savefig(os.path.join(OUT, name+ext))
    plt.close(fig)
    print(f"  [OK] {name}")


# ══════════════════════════════════════════════════════════
# Fig 4 — Accuracy grouped bar 3×3
# ══════════════════════════════════════════════════════════
print("Fig 4: Accuracy...")
fig, axes = plt.subplots(3,3, figsize=(7.16,5.4))
axes = axes.ravel()
for ax, ds, lbl in zip(axes, DATASETS, DS_LABELS):
    x = np.arange(len(ALL_V)); w = 0.62
    means = [g(v,ds).mean() for v in ALL_V]
    stds  = [g(v,ds).std()  for v in ALL_V]
    bars = ax.bar(x, means, w, color=[COLORS[v] for v in ALL_V],
                  edgecolor="k", linewidth=0.4,
                  yerr=stds, error_kw=dict(elinewidth=0.55,capsize=1.5,
                                           capthick=0.55,ecolor="0.35"))
    for bar,v in zip(bars,ALL_V):
        if HATCHES[v]: bar.set_hatch(HATCHES[v])
    ki = ALL_V.index("MEL_KGEF")
    bars[ki].set_edgecolor("#b71c1c"); bars[ki].set_linewidth(1.1)
    ax.set_title(lbl, fontsize=8, pad=2)
    ax.set_xticks(x)
    ax.set_xticklabels([V_LABELS[v] for v in ALL_V], rotation=45, ha="right", fontsize=6.2)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
    mn = min(m-s for m,s in zip(means,stds))
    mx = max(m+s for m,s in zip(means,stds))
    pad = (mx-mn)*0.15
    ax.set_ylim(max(0,mn-pad-0.005), min(1.0,mx+pad+0.005))
    ax.grid(axis="y", linestyle="--", alpha=0.4)
handles = make_handles(ALL_V)
fig.legend(handles=handles, loc="lower center", ncol=5,
           bbox_to_anchor=(0.5,-0.04), frameon=True,
           columnspacing=0.7, handlelength=1.1, handleheight=0.85)
fig.text(0.025, 0.5, "Classification Accuracy", va="center",
         rotation="vertical", fontsize=8)
fig.tight_layout(rect=[0.04,0.07,1,1])
save(fig, "fig4_accuracy")


# ══════════════════════════════════════════════════════════
# Fig 5 — Features grouped bar 3×3 log
# ══════════════════════════════════════════════════════════
print("Fig 5: Features...")
fig, axes = plt.subplots(3,3, figsize=(7.16,5.4))
axes = axes.ravel()
for ax, ds, lbl in zip(axes, DATASETS, DS_LABELS):
    x = np.arange(len(ALL_V)); w = 0.62
    means = [g(v,ds,"Num_Features").mean() for v in ALL_V]
    stds  = [g(v,ds,"Num_Features").std()  for v in ALL_V]
    bars = ax.bar(x, means, w, color=[COLORS[v] for v in ALL_V],
                  edgecolor="k", linewidth=0.4,
                  yerr=stds, error_kw=dict(elinewidth=0.55,capsize=1.5,
                                           capthick=0.55,ecolor="0.35"))
    for bar,v in zip(bars,ALL_V):
        if HATCHES[v]: bar.set_hatch(HATCHES[v])
    ki = ALL_V.index("MEL_KGEF")
    bars[ki].set_edgecolor("#b71c1c"); bars[ki].set_linewidth(1.1)
    ax.set_title(lbl, fontsize=8, pad=2)
    ax.set_xticks(x)
    ax.set_xticklabels([V_LABELS[v] for v in ALL_V], rotation=45, ha="right", fontsize=6.2)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y,_: f"{int(y):,}"))
    ax.grid(axis="y", linestyle="--", alpha=0.4, which="both")
handles = make_handles(ALL_V)
fig.legend(handles=handles, loc="lower center", ncol=5,
           bbox_to_anchor=(0.5,-0.04), frameon=True,
           columnspacing=0.7, handlelength=1.1, handleheight=0.85)
fig.text(0.025, 0.5, "Number of Selected Features (log scale)",
         va="center", rotation="vertical", fontsize=8)
fig.tight_layout(rect=[0.04,0.07,1,1])
save(fig, "fig5_features")


# ══════════════════════════════════════════════════════════
# Fig 6 — Ablation dual panel
# ══════════════════════════════════════════════════════════
print("Fig 6: Ablation...")
fig, axes = plt.subplots(1,2, figsize=(7.16,3.1))
n_ds = len(DATASETS); x = np.arange(n_ds)
n_v = len(ABL_V); w = 0.68/n_v
offs = np.linspace(-(n_v-1)/2*w, (n_v-1)/2*w, n_v)
for panel,(ax,metric,ylabel) in enumerate(zip(
        axes, ["Accuracy","Num_Features"],
        ["Classification Accuracy","Number of Selected Features"])):
    for v,off,lbl in zip(ABL_V, offs, ABL_LB):
        means = [g(v,ds,metric).mean() for ds in DATASETS]
        stds  = [g(v,ds,metric).std()  for ds in DATASETS]
        bars = ax.bar(x+off, means, w, color=COLORS[v], edgecolor="k",
                      linewidth=0.4, label=lbl, yerr=stds,
                      error_kw=dict(elinewidth=0.5,capsize=1.2,
                                    capthick=0.5,ecolor="0.35"))
        for bar in bars:
            if HATCHES[v]: bar.set_hatch(HATCHES[v])
    ax.set_xticks(x)
    ax.set_xticklabels(DS_LABELS, rotation=40, ha="right", fontsize=7)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    if metric=="Num_Features":
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y,_: f"{int(y):,}"))
        ax.grid(axis="y", linestyle="--", alpha=0.45, which="both")
    if panel==0:
        handles = make_handles(ABL_V, ABL_LB)
        ax.legend(handles=handles, fontsize=7, ncol=2,
                  loc="lower right", frameon=True,
                  handlelength=1.1, handleheight=0.85)
fig.tight_layout(w_pad=2.5)
save(fig, "fig6_ablation")


# ══════════════════════════════════════════════════════════
# Fig 7 — Boxplots 3×3
# ══════════════════════════════════════════════════════════
print("Fig 7: Boxplots...")
BOX_V  = ["MEL_KGEF","FWPSO","PSO_CSM","IGPSO"]
BOX_LB = ["KDS-EL\n(Proposed)","FWPSO","PSO-CSM","IGPSO"]
fig, axes = plt.subplots(3,3, figsize=(7.16,5.5))
axes = axes.ravel()
for ax, ds, dslbl in zip(axes, DATASETS, DS_LABELS):
    data = [g(v,ds) for v in BOX_V]
    bp = ax.boxplot(data, patch_artist=True, widths=0.52,
                    medianprops=dict(color="k",linewidth=1.1),
                    whiskerprops=dict(linewidth=0.65),
                    capprops=dict(linewidth=0.65),
                    flierprops=dict(marker="o",markersize=2,linewidth=0.4,
                                    markeredgecolor="0.5",markerfacecolor="none"),
                    boxprops=dict(linewidth=0.55))
    for patch,v in zip(bp["boxes"],BOX_V):
        patch.set_facecolor(COLORS[v]); patch.set_alpha(0.72)
    kgef = g("MEL_KGEF",ds)
    allv = np.concatenate(data)
    ymax=allv.max(); rng=allv.max()-allv.min()
    for ci,v in enumerate(BOX_V[1:]):
        try:
            _,p=stats.wilcoxon(kgef,g(v,ds))
            if p<0.05:
                y=ymax+rng*0.04*(ci+1)
                sym="***" if p<0.001 else "**" if p<0.01 else "*"
                ax.plot([ci+2,ci+2,1,1],[y,y+rng*0.015,y+rng*0.015,y],lw=0.7,c="k")
                ax.text((ci+2+1)/2, y+rng*0.015, sym,
                        ha="center",va="bottom",fontsize=5.5)
        except: pass
    ax.set_title(dslbl, fontsize=8, pad=2)
    ax.set_xticks(range(1,5))
    ax.set_xticklabels(BOX_LB, fontsize=6.2)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(4))
    ax.grid(axis="y", linestyle="--", alpha=0.45)
fig.text(0.025, 0.5, "Classification Accuracy", va="center",
         rotation="vertical", fontsize=8)
fig.tight_layout(rect=[0.04,0,1,1])
save(fig, "fig7_boxplot")


# ══════════════════════════════════════════════════════════
# Fig 10 — Wilcoxon heatmap
# ══════════════════════════════════════════════════════════
print("Fig 10: Wilcoxon heatmap...")
COMP_V  = ["MEL","MEL_NHD","MEL_KGEF_noNHD","FWPSO","PSO_CSM","IGPSO","SaWDE","BPSO"]
COMP_LB = ["MEL","KDS-EL/DRS","KDS-EL/KER","FWPSO","PSO-CSM","IGPSO","SaWDE","BPSO"]
pmat = np.zeros((len(DATASETS),len(COMP_V)))
dmat = np.zeros_like(pmat)
for i,ds in enumerate(DATASETS):
    a = g("MEL_KGEF",ds)
    for j,v in enumerate(COMP_V):
        b = g(v,ds); n=min(len(a),len(b))
        try: _,p=stats.wilcoxon(a[:n],b[:n])
        except: p=1.0
        pmat[i,j]=p; dmat[i,j]=1 if a.mean()>b.mean() else -1
fig, ax = plt.subplots(figsize=(5.6,3.3))
cw=plt.cm.Greens; cl=plt.cm.Reds
img=np.zeros((*pmat.shape,4))
for i in range(pmat.shape[0]):
    for j in range(pmat.shape[1]):
        p=pmat[i,j]
        sig=0.82 if p<0.001 else 0.62 if p<0.01 else 0.42 if p<0.05 else 0.17
        img[i,j]=cw(sig) if dmat[i,j]>0 else cl(sig)
ax.imshow(img, aspect="auto")
for i in range(pmat.shape[0]):
    for j in range(pmat.shape[1]):
        p=pmat[i,j]
        txt="***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "ns"
        col="white" if p<0.05 else "0.55"
        ax.text(j,i,txt,ha="center",va="center",fontsize=6.5,color=col,
                fontweight="bold" if p<0.05 else "normal")
ax.set_xticks(range(len(COMP_V))); ax.set_xticklabels(COMP_LB,fontsize=7)
ax.set_yticks(range(len(DATASETS))); ax.set_yticklabels(DS_LABELS,fontsize=7)
ax.set_title("Wilcoxon Signed-Rank Test: KDS-EL vs. Competitors",fontsize=8,pad=4)
from matplotlib.patches import Patch
leg=[Patch(facecolor=cw(0.82),label="Win ($p<0.001$)"),
     Patch(facecolor=cw(0.62),label="Win ($p<0.01$)"),
     Patch(facecolor=cw(0.42),label="Win ($p<0.05$)"),
     Patch(facecolor=cw(0.17),label="Win (ns)"),
     Patch(facecolor=cl(0.42),label="Loss ($p<0.05$)"),
     Patch(facecolor=cl(0.17),label="Loss (ns)")]
ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5,-0.42),
          ncol=3, fontsize=6.5, frameon=True)
fig.tight_layout(rect=[0,0.12,1,1])
save(fig, "fig10_wilcoxon")


# ══════════════════════════════════════════════════════════
# Fig 11 — Runtime split panel
# ══════════════════════════════════════════════════════════
print("Fig 11: Runtime...")
RT_V  = ["MEL_KGEF","FWPSO","MEL","PSO_CSM","IGPSO","SaWDE","BPSO"]
RT_LB = [V_LABELS[v] for v in RT_V]
EXCL  = [ds for ds in DATASETS if ds!="Stroke"]
EXCL_LB = [DS_LABELS[DATASETS.index(d)] for d in EXCL]
fig, axes = plt.subplots(1,2, figsize=(7.16,2.7))
ax=axes[0]
n_ds=len(EXCL); n_v=len(RT_V); w=0.68/n_v; x=np.arange(n_ds)
offs=np.linspace(-(n_v-1)/2*w,(n_v-1)/2*w,n_v)
for v,off in zip(RT_V,offs):
    means=[g(v,ds,"Time_sec").mean() for ds in EXCL]
    bars=ax.bar(x+off,means,w,color=COLORS[v],edgecolor="k",linewidth=0.35)
    for bar in bars:
        if HATCHES[v]: bar.set_hatch(HATCHES[v])
ax.set_xticks(x); ax.set_xticklabels(EXCL_LB,rotation=38,ha="right",fontsize=7)
ax.set_ylabel("Avg. Runtime (s)",fontsize=8); ax.set_yscale("log")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y,_: f"{int(y)}" if y>=10 else f"{y:.1f}"))
ax.grid(axis="y",linestyle="--",alpha=0.45,which="both")
ax.set_title("Datasets (excl. Stroke)",fontsize=8,pad=2)
ax=axes[1]
ms=[g(v,"Stroke","Time_sec").mean() for v in RT_V]
x2=np.arange(len(RT_V))
bars=ax.bar(x2,ms,0.58,color=[COLORS[v] for v in RT_V],edgecolor="k",linewidth=0.4)
for bar,v in zip(bars,RT_V):
    if HATCHES[v]: bar.set_hatch(HATCHES[v])
ki=RT_V.index("MEL_KGEF")
ax.annotate(f"{ms[ki]:.0f}s",xy=(ki,ms[ki]),xytext=(ki+0.5,ms[ki]+30),
            arrowprops=dict(arrowstyle="->",lw=0.7),fontsize=6.5,color="#b71c1c")
ax.set_xticks(x2); ax.set_xticklabels(RT_LB,rotation=38,ha="right",fontsize=7)
ax.set_ylabel("Avg. Runtime (s)",fontsize=8)
ax.grid(axis="y",linestyle="--",alpha=0.45)
ax.set_title("Stroke ($d=26{,}877$)",fontsize=8,pad=2)
handles=make_handles(RT_V)
fig.legend(handles=handles,loc="lower center",ncol=4,
           bbox_to_anchor=(0.5,-0.08),frameon=True,fontsize=7,
           columnspacing=0.7,handlelength=1.1)
fig.tight_layout(rect=[0,0.1,1,1])
save(fig, "fig11_runtime")


# ══════════════════════════════════════════════════════════
# Fig 12 — Bubble chart
# ══════════════════════════════════════════════════════════
print("Fig 12: Bubble chart...")
stats_v = {}
for v in ALL_V:
    stats_v[v] = {
        "acc":  df[df.Version==v]["Accuracy"].mean()*100,
        "feat": df[df.Version==v]["Num_Features"].mean(),
        "time": df[df.Version==v]["Time_sec"].mean(),
    }
tmin=min(stats_v[v]["time"] for v in ALL_V)
tmax=max(stats_v[v]["time"] for v in ALL_V)
def bsz(t): return 80+680*((t-tmin)/(tmax-tmin))**0.65
LCFG = {
    "FWPSO":(1.7,0.25),"MEL":(1.7,-0.40),"MEL_NHD":(1.7,0.25),"MEL_KGEF_noNHD":(1.7,-0.40),
    "PSO_CSM":(1.7,0.25),"IGPSO":(1.7,-0.40),
    "SaWDE":(2.0,-0.40),"BPSO":(2.0,0.25),
}
fig, ax = plt.subplots(figsize=(5.8,4.5))
for v in ALL_V:
    if v=="MEL_KGEF": continue
    x=stats_v[v]["feat"]; y=stats_v[v]["acc"]; s=bsz(stats_v[v]["time"])
    ax.scatter(x,y,s=s,c=COLORS[v],alpha=0.72,
               edgecolors="white",linewidths=0.9,zorder=3)
    mx,dy=LCFG.get(v,(2.0,0.2))
    ax.text(x*mx,y+dy,V_LABELS[v],fontsize=6.5,color=COLORS[v],
            ha="left",va="center",zorder=4)
v="MEL_KGEF"
x=stats_v[v]["feat"]; y=stats_v[v]["acc"]; s=bsz(stats_v[v]["time"])
ax.scatter(x,y,s=s*1.5,c=COLORS[v],alpha=0.95,
           edgecolors="#7f0000",linewidths=1.8,marker="*",zorder=10)
ax.annotate("KDS-EL\n(Proposed)",xy=(x,y),xytext=(x*4.5,y-1.8),
            fontsize=8,color="#b71c1c",fontweight="bold",va="top",ha="left",
            arrowprops=dict(arrowstyle="->",color="#b71c1c",lw=1.0,
                           connectionstyle="arc3,rad=-0.15"))
ax.axhspan(91,97,xmin=0.0,xmax=0.18,alpha=0.06,color="#b71c1c",zorder=0)
ax.text(340,95.5,"Dominant\nregion",fontsize=6.3,color="#b71c1c",
        alpha=0.6,ha="center",fontstyle="italic")
ax.text(0.015,0.54,"← Fewer features",transform=ax.transAxes,
        fontsize=6.2,color="0.55",ha="left",va="center",fontstyle="italic")
ax.text(0.5,0.985,"Higher accuracy ↑",transform=ax.transAxes,
        fontsize=6.2,color="0.55",ha="center",va="top",fontstyle="italic")
ax.set_xlabel("Mean Selected Features (log scale)",fontsize=8.5)
ax.set_ylabel("Mean Classification Accuracy (%)",fontsize=8.5)
ax.set_title("Accuracy–Feature–Runtime Trade-off\n"
             "(bubble area $\\propto$ avg. runtime per dataset)",fontsize=8.5,pad=5)
ax.set_xscale("log")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda y,_: f"{int(y):,}"))
ax.set_ylim(82,97); ax.grid(linestyle="--",alpha=0.35,which="both")
h1=Line2D([],[],marker="o",linestyle="None",markersize=np.sqrt(bsz(55)),
           color="#cccccc",markeredgecolor="#aaaaaa",label="Runtime $\\approx$ 55 s")
h2=Line2D([],[],marker="o",linestyle="None",markersize=np.sqrt(bsz(140)),
           color="#cccccc",markeredgecolor="#aaaaaa",label="Runtime $\\approx$ 140 s")
h3=Line2D([],[],marker="o",linestyle="None",markersize=np.sqrt(bsz(200)),
           color="#cccccc",markeredgecolor="#aaaaaa",label="Runtime $\\approx$ 200 s")
ax.legend(handles=[h1,h2,h3],loc="lower right",frameon=True,
          title="Bubble size:",title_fontsize=6.5,
          handlelength=1.0,borderpad=0.7,labelspacing=0.9)
fig.tight_layout()
save(fig, "fig12_bubble")

print("\nAll figures done.")
