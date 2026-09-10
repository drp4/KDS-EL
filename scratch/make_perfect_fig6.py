import os, sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

PROJ = Path(r"e:\多目标优化\KDS-EL")
sys.path.insert(0, str(PROJ / "code"))

from generate_figures import load_merged_detail, ALL_VERSIONS, PLOT_DATASETS, g
from plot_style import apply_style

apply_style()

df = load_merged_detail()
versions = [v for v in ALL_VERSIONS if v in df.Version.unique()]
ds_list = [d for d in PLOT_DATASETS if d in df.Dataset.unique()]

ranks = {v: [] for v in versions}
for ds in ds_list:
    ds_means = {}
    for v in versions:
        arr = g(df, v, ds)
        if len(arr) > 0 and not np.isnan(arr).all():
            ds_means[v] = np.nanmean(arr)
    if ds_means:
        sorted_v = sorted(ds_means, key=ds_means.get, reverse=True)
        i = 0
        while i < len(sorted_v):
            j = i
            while (j + 1 < len(sorted_v) and ds_means[sorted_v[j + 1]] == ds_means[sorted_v[i]]):
                j += 1
            avg_rank = (i + 1 + j + 1) / 2.0
            for v in sorted_v[i:j + 1]:
                ranks[v].append(avg_rank)
            i = j + 1

avg_ranks = {v: np.mean(ranks[v]) for v in versions if ranks[v]}
sorted_methods = sorted(avg_ranks, key=avg_ranks.get)

V_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool": "KDS-EL w/o TPS",
    "MEL_MI": "KDS-EL w/o TPS & KER",
    "MEL": "MEL",
    "bIRIME": "bIRIME",
    "FWPSO": "FWPSO",
    "PSO_CSM": "PSO-CSM",
    "BinCOA": "BinCOA",
    "SaWDE": "SaWDE",
    "IGPSO": "IGPSO",
    "DENCA_SO": "DENCA-SO",
    "BPSO": "BPSO",
}

values = [avg_ranks[v] for v in sorted_methods]
labels = [V_LABELS.get(v, v) for v in sorted_methods]
n_m = len(sorted_methods)
y_pos = np.arange(n_m)

# Native single-column size: 3.48 in width x 3.10 in height
fig, ax = plt.subplots(figsize=(3.48, 3.10), dpi=300)

# Colors: Hero KDS-EL in Nature Vermilion; all competitors in refined, cohesive slate
colors = ["#C82423" if v == "KDS_EL_TwoPhase" else "#5A6E85" for v in sorted_methods]
edges = ["#991B1B" if v == "KDS_EL_TwoPhase" else "#3B4A5A" for v in sorted_methods]

bars = ax.barh(y_pos, values, height=0.68, color=colors, edgecolor=edges, linewidth=0.65, zorder=3)

# Critical Difference cutoff at CD = 5.00 (Demšar Bonferroni-Dunn, alpha=0.05)
cd_val = 5.00
ax.axvline(x=cd_val, color="#DC2626", linestyle="--", linewidth=0.85, alpha=0.85, zorder=2)

# Shaded statistically inferior zone (ranks > 5.00)
ax.axvspan(cd_val, 12.5, facecolor="#F8FAFC", alpha=0.75, zorder=1)

# Annotate CD line cleanly at the top margin
ax.text(cd_val, -0.65, r"CD cutoff ($p < 0.05$)", color="#DC2626", fontsize=6.5,
        fontweight="bold", ha="center", va="bottom", zorder=4)

# Value labels at the end of each bar
for i, (v, bar) in enumerate(zip(sorted_methods, bars)):
    val_str = f"{values[i]:.2f}"
    is_kds = (v == "KDS_EL_TwoPhase")
    txt_col = "#C82423" if is_kds else "#1E293B"
    font_wt = "bold" if is_kds else "normal"
    ax.text(bar.get_width() + 0.18, bar.get_y() + bar.get_height() / 2,
            val_str, va="center", ha="left", fontsize=6.8,
            fontweight=font_wt, color=txt_col, zorder=4)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=7.2)
for tick_label in ax.get_yticklabels():
    if tick_label.get_text() == "KDS-EL":
        tick_label.set_fontweight("bold")
        tick_label.set_color("#C82423")

ax.invert_yaxis()
ax.set_ylim(n_m - 0.35, -1.0)  # Room for the top CD label
ax.set_xlim(0, 12.0)
ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
ax.set_xlabel("Average Friedman rank (lower is better)", fontsize=7.5, labelpad=2.5)

ax.grid(axis="x", linestyle="--", alpha=0.45, linewidth=0.4, color="#CBD5E0", zorder=0)
ax.tick_params(axis="both", which="both", labelsize=6.8, length=2.0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.6)
ax.spines["bottom"].set_linewidth(0.6)

plt.tight_layout(pad=0.20)

out_fig = PROJ / "output" / "figures"
for ext in (".png", ".pdf"):
    fig.savefig(out_fig / f"F13_friedman_rank{ext}", dpi=300)
fig.savefig(PROJ / "scratch" / "test_fig6_perfect.png", dpi=300)
plt.close(fig)
print("Saved perfect F13_friedman_rank!")
