"""Publication-style figure for the Two-Phase Weight Scheduling mechanism."""

import os

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "output", "figures")

mpl.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.7,
    "lines.linewidth": 1.1,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})


def main():
    T = 100
    alpha = 0.7
    split = alpha * T

    t = np.linspace(0, T, 2001)
    wa = np.where(t <= split, 0.7, 0.95)
    wf = np.where(t <= split, 0.3, 0.05)

    fig, ax = plt.subplots(figsize=(5.6, 3.0))

    ax.axvspan(0, split, color="0.93", zorder=0)
    ax.axvline(split, color="0.25", linestyle="--", linewidth=0.9, zorder=3)

    ax.step(t, wa, where="post", color="k", linewidth=1.5,
            label=r"$w_a(t)$  (accuracy)")
    ax.step(t, wf, where="post", color="0.42", linestyle="--", linewidth=1.3,
            label=r"$w_f(t)$  (feature ratio)")

    ax.axhline(0.9, color="0.72", linestyle=":", linewidth=1.0)
    ax.axhline(0.1, color="0.72", linestyle=":", linewidth=1.0)

    ax.text(0.09, 0.90, r"$[0.7,\ 0.3]$", fontsize=8, transform=ax.transAxes)
    ax.text(0.73, 0.90, r"$[0.95,\ 0.05]$", fontsize=8, transform=ax.transAxes)
    ax.text(0.705, 0.62, r"$t = \alpha T = 0.7T$", fontsize=7,
            rotation=90, va="top", ha="right", transform=ax.transAxes)

    ax.text(0.32, 0.55, "Phase 1\naggressive feature reduction",
            ha="center", va="center", fontsize=7.5, transform=ax.transAxes)
    ax.text(0.83, 0.55, "Phase 2\naccuracy refinement",
            ha="center", va="center", fontsize=7.5, transform=ax.transAxes)

    ax.set_xlim(0, T)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Iteration $t$")
    ax.set_ylabel("Objective weight")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    ax.legend(loc="lower right", frameon=True, framealpha=0.95,
              edgecolor="0.6", borderpad=0.4, handlelength=1.8)

    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.join(OUT_DIR, "F14_twophase_schedule")
    fig.savefig(base + ".pdf")
    fig.savefig(base + ".png")
    print("wrote", base + ".pdf", base + ".png")


if __name__ == "__main__":
    main()
