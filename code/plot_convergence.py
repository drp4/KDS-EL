"""
F8 + F9: 收敛曲线 & NHD 多样性曲线
=====================================
从 npy 文件读取迭代曲线数据，生成：
  F8  — 适应度收敛曲线 (auto-grid, 所有共有数据集)
  F9  — NHD 多样性曲线 (auto-grid, 所有共有数据集)

数据来源：
  - Exp1: output/formal_experiment_20260701_094943/curves/
  - Exp2: output/formal_experiment_20260628_205157/curves/
  - Exp3: output/formal_experiment_20260702_145828/curves/
  - Exp4: output/formal_experiment_20260707_142018/curves/

用法：
    python plot_convergence.py
    python plot_convergence.py --out figures/
"""
import os, sys, argparse, re
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PROJ = Path(__file__).resolve().parent.parent
EXP1_CURVES = PROJ / "output" / "formal_experiment_20260701_094943" / "curves"
EXP2_CURVES = PROJ / "output" / "formal_experiment_20260628_205157" / "curves"
EXP3_CURVES = PROJ / "output" / "formal_experiment_20260702_145828" / "curves"
EXP4_CURVES = PROJ / "output" / "formal_experiment_20260707_142018" / "curves"
MEL_MI_CURVES = PROJ / "output" / "formal_experiment_mel_mi" / "curves"

# ── 样式 ──
mpl.rcParams.update({
    "font.family": "DejaVu Serif", "font.size": 8,
    "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 6.5, "legend.framealpha": 0.92,
    "legend.edgecolor": "0.6", "legend.borderpad": 0.3,
    "axes.linewidth": 0.7, "grid.linewidth": 0.3,
    "lines.linewidth": 0.9,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

# ── 颜色和标签（扩展到15方法）──
COLORS = {
    # === KDS-EL family — Coral/Red (the ONE standout hue) ===
    "KDS_EL":     "#E8594A",  # Proposed — brightest coral
    "KDS_EL_KER": "#F09080",  # light coral
    "KDS_EL_DRS": "#D0685C",  # deep coral

    # === MEL baselines — Steel Blue ===
    "MEL":        "#6A94B2",  # MEL baseline
    "MEL_MI":     "#8BB3CC",  # MEL+MI (lighter)

    # === SOTA — Blue-Gray gradient (wide L spread) ===
    "FWPSO":      "#5D7E99",  # darkest blue-gray
    "IGPSO":      "#6C8BA3",  # dark blue-gray
    "PSO_CSM":    "#7F99AE",  # medium blue-gray
    "SaWDE":      "#94AABD",  # medium-light blue-gray
    "BPSO":       "#AABBC8",  # lightest blue-gray

    # === MOFS — Cool Gray gradient (wide L spread) ===
    "VGS_MOEA":   "#6B7B85",  # darkest cool gray
    "NSGA_II_FS": "#7E8D96",  # dark cool gray
    "W_MOPSO_FS": "#8F9DA4",  # medium-dark cool gray
    "fMOPSO_FS":  "#9FABB2",  # medium cool gray
    "MOEA_D_FS":  "#AEB8BD",  # medium-light cool gray
    "MOPSO_FS":   "#BCC4C8",  # lightest cool gray
}
V_LABELS = {
    "KDS_EL": "KDS-EL (Proposed)", "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "MEL": "MEL (Baseline)",
    "MEL_MI": "MEL+MI (w/ reinit)",
    "FWPSO": "FWPSO", "BPSO": "BPSO",
    "SaWDE": "SaWDE", "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
    "NSGA_II_FS": "NSGA-II-FS", "MOPSO_FS": "MOPSO-FS",
    "MOEA_D_FS": "MOEA-D-FS", "fMOPSO_FS": "fMOPSO-FS",
    "VGS_MOEA": "VGS-MOEA", "W_MOPSO_FS": "W-MOPSO-FS",
}
LINE_STYLES = {
    "KDS_EL": "-", "KDS_EL_DRS": "--", "KDS_EL_KER": "-.",
    "MEL": ":", "MEL_MI": (0, (3, 1, 1, 1)),
    "FWPSO": "-", "BPSO": "--",
    "SaWDE": "-.", "PSO_CSM": ":", "IGPSO": "--",
    "NSGA_II_FS": "-", "MOPSO_FS": "--", "MOEA_D_FS": "-.",
    "fMOPSO_FS": "-", "VGS_MOEA": "--", "W_MOPSO_FS": "-.",
}


def _get_curve_shared_datasets(versions, prefix="curve"):
    """Compute datasets that have curve data for all specified versions."""
    all_dirs = [EXP3_CURVES, EXP2_CURVES, EXP1_CURVES, EXP4_CURVES, MEL_MI_CURVES]
    ds_sets = []
    for v in versions:
        files = set()
        for d in all_dirs:
            if d.exists():
                pattern = re.compile(rf"{re.escape(prefix)}_{re.escape(v)}_(\w+)_run\d+\.npy")
                for f in d.iterdir():
                    m = pattern.match(f.name)
                    if m:
                        files.add(m.group(1))
        if files:
            ds_sets.append(files)
    shared = set.intersection(*ds_sets) if ds_sets else set()
    return sorted(shared)


def _auto_grid(n, max_cols=5):
    cols = min(n, max_cols)
    rows = (n + cols - 1) // cols
    return rows, cols


# F8 算法: KDS-EL family + FWPSO (best SOTA) + MEL + MEL_MI + Top MOFS
F8_VERSIONS = ["FWPSO", "MEL", "MEL_MI", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL",
               "VGS_MOEA", "NSGA_II_FS"]

# F9 算法: NHD curves — MEL(0) → MEL_MI(0) → DRS(>0) → Full(>0)
F9_VERSIONS = ["MEL", "MEL_MI", "KDS_EL_DRS", "KDS_EL"]


def load_curves(version, dataset, curves_dir, prefix="curve"):
    """加载某个 version+dataset 的所有 run 曲线，返回 (n_runs, T) 数组。"""
    pattern = re.compile(
        rf"{prefix}_{re.escape(version)}_{re.escape(dataset)}_run(\d+)\.npy"
    )
    runs = []
    if not curves_dir.exists():
        return None
    for fname in sorted(curves_dir.iterdir()):
        m = pattern.match(fname.name)
        if m:
            arr = np.load(fname, allow_pickle=True)
            runs.append(arr.astype(np.float64))
    if not runs:
        return None
    min_len = min(len(r) for r in runs)
    runs = np.array([r[:min_len] for r in runs])
    return runs


def load_from_all(version, dataset, prefix="curve"):
    """从正确的实验目录加载曲线：
       - KDS-EL 三变体 → Exp3 (V2, 已修复所有 bug)
       - MEL → Exp2 (V1 有效)
       - SOTA → Exp1
       - MOFS → Exp4
    """
    KDS_VERSIONS = {"KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"}
    MOFS_NAMES = {"NSGA_II_FS", "MOPSO_FS", "MOEA_D_FS",
                   "fMOPSO_FS", "VGS_MOEA", "W_MOPSO_FS"}
    SOTA_NAMES = {"BPSO", "SaWDE", "FWPSO", "PSO_CSM", "IGPSO"}

    if version in KDS_VERSIONS:
        data = load_curves(version, dataset, EXP3_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP2_CURVES, prefix)
    elif version == "MEL_MI":
        data = load_curves(version, dataset, MEL_MI_CURVES, prefix)
    elif version in MOFS_NAMES:
        data = load_curves(version, dataset, EXP4_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP1_CURVES, prefix)
    elif version == "MEL":
        data = load_curves(version, dataset, EXP2_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP1_CURVES, prefix)
    else:
        data = load_curves(version, dataset, EXP1_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP2_CURVES, prefix)
    return data


def plot_with_band(ax, data, color, label, linestyle, alpha_fill=0.15):
    """绘制均值 ± 标准差曲线。"""
    if data is None or len(data) == 0:
        return
    T = data.shape[1]
    x = np.arange(T)
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    ax.plot(x, mean, color=color, linestyle=linestyle, linewidth=1.1, label=label)
    ax.fill_between(x, mean - std, mean + std, color=color, alpha=alpha_fill,
                    linewidth=0)
    return mean, std


def save_fig(fig, name, out_dir):
    for ext in (".pdf", ".png"):
        p = os.path.join(out_dir, name + ext)
        fig.savefig(p)
    print(f"  [OK] {name}")


# ══════════════════════════════════════════════════════════════════════════════
# F8: 适应度收敛曲线 (auto-grid, 所有共有数据集)
# ══════════════════════════════════════════════════════════════════════════════

def fig_f8_convergence(out_dir):
    """F8: Fitness convergence curves — auto-grid, all shared datasets."""
    ds_list = _get_curve_shared_datasets(F8_VERSIONS, prefix="curve")
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    print(f"F8: Convergence curves ({n_ds} datasets, {rows}x{cols})...")

    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.8 * rows))
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        for v in F8_VERSIONS:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                acc_data = 1.0 - data  # fitness → accuracy
                plot_with_band(ax, acc_data, COLORS.get(v, "#333333"),
                               V_LABELS.get(v, v),
                               LINE_STYLES.get(v, "-"), alpha_fill=0.12)

        ax.set_title(ds, fontsize=7, pad=1.5)
        ax.set_xlabel("Iteration", fontsize=6.5)
        ax.set_ylabel("Accuracy", fontsize=6.5)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        ax.grid(linestyle="--", alpha=0.4, which="both")
        ax.set_xlim(0, 100)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    from matplotlib.lines import Line2D
    handles = []
    for v in F8_VERSIONS:
        handles.append(Line2D([0], [0], color=COLORS.get(v, "#333333"),
                              linestyle=LINE_STYLES.get(v, "-"),
                              linewidth=1.3, label=V_LABELS.get(v, v)))
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.6, handlelength=1.2, fontsize=5.5)
    fig.suptitle("F8: Convergence Curves (Mean Accuracy ± Std across 10 runs)",
                 fontsize=9, y=1.01)
    fig.tight_layout(rect=[0, 0.06, 1, 0.97])
    save_fig(fig, "F8_convergence_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F9: NHD 多样性曲线 (auto-grid, 所有共有数据集)
# ══════════════════════════════════════════════════════════════════════════════

def fig_f9_nhd(out_dir):
    """F9: NHD diversity curves — auto-grid, all shared datasets."""
    ds_list = _get_curve_shared_datasets(F9_VERSIONS, prefix="nhd")
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    print(f"F9: NHD diversity curves ({n_ds} datasets, {rows}x{cols})...")

    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.8 * rows))
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        for v in F9_VERSIONS:
            data = load_from_all(v, ds, prefix="nhd")
            if data is not None:
                if np.all(data < 1e-8):
                    ax.axhline(y=0, color=COLORS.get(v, "#333333"), linestyle=":",
                               linewidth=0.6, alpha=0.5)
                    ax.text(50, 0.02, f"{V_LABELS.get(v, v)}: NHD=0",
                            color=COLORS.get(v, "#333333"), fontsize=5, alpha=0.7,
                            ha="center", va="bottom")
                else:
                    plot_with_band(ax, data, COLORS.get(v, "#333333"),
                                   V_LABELS.get(v, v),
                                   LINE_STYLES.get(v, "-"), alpha_fill=0.12)

        ax.set_title(ds, fontsize=7, pad=1.5)
        ax.set_xlabel("Iteration", fontsize=6.5)
        ax.set_ylabel("NHD", fontsize=6.5)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        ax.grid(linestyle="--", alpha=0.4)
        ax.set_xlim(0, 100)
        ymax = ax.get_ylim()[1]
        ax.set_ylim(-0.02, max(ymax, 0.5) * 1.1)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    from matplotlib.lines import Line2D
    handles = []
    for v in F9_VERSIONS:
        handles.append(Line2D([0], [0], color=COLORS.get(v, "#333333"),
                              linestyle=LINE_STYLES.get(v, "-"),
                              linewidth=1.3, label=V_LABELS.get(v, v)))
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.6, handlelength=1.2, fontsize=5.5)
    fig.suptitle("F9: NHD Diversity Curves (Mean ± Std across 10 runs)",
                 fontsize=9, y=1.01)
    fig.tight_layout(rect=[0, 0.06, 1, 0.97])
    save_fig(fig, "F9_nhd_diversity_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="KDS-EL Convergence Plotter")
    parser.add_argument("--out", default=None,
                        help="Output directory (default: output/figures/)")
    parser.add_argument("--fig", nargs="*", default=None,
                        help="Specific figures: F8 F9")
    args = parser.parse_args()

    out_dir = args.out or str(PROJ / "output" / "figures")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Curve data sources:")
    print(f"  Exp1 (SOTA):  {EXP1_CURVES}")
    print(f"  Exp2 (MEL):   {EXP2_CURVES}")
    print(f"  Exp3 (KDS-EL): {EXP3_CURVES}")
    print(f"  Exp4 (MOFS):  {EXP4_CURVES}")
    print(f"\nGenerating → {out_dir}\n")

    all_figs = {"F8": fig_f8_convergence, "F9": fig_f9_nhd}
    requested = args.fig if args.fig else list(all_figs.keys())

    for key in requested:
        if key in all_figs:
            try:
                all_figs[key](out_dir)
            except Exception as e:
                print(f"  [FAIL] {key}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  [SKIP] Unknown figure: {key}")

    print(f"\nDone! → {out_dir}")


if __name__ == "__main__":
    main()
