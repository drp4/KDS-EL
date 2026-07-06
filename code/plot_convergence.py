"""
F8 + F9: 收敛曲线 & NHD 多样性曲线
=====================================
从 npy 文件读取迭代曲线数据，生成：
  F8  — 适应度收敛曲线 (2×3)
  F9  — NHD 多样性曲线 (2×3)

数据来源：
  - Exp1: output/formal_experiment_20260701_094943/curves/
  - Exp2: output/formal_experiment_20260628_205157/curves/

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

# ── 颜色和标签 ──
COLORS = {
    "KDS_EL": "#b71c1c", "KDS_EL_DRS": "#2e7d32",
    "KDS_EL_KER": "#f57f17", "MEL": "#00838f",
    "FWPSO": "#1565c0", "BPSO": "#9e9e9e",
    "SaWDE": "#bdbdbd", "PSO_CSM": "#6a1b9a", "IGPSO": "#e65100",
}
V_LABELS = {
    "KDS_EL": "KDS-EL (Proposed)", "KDS_EL_DRS": "KDS-EL/DRS",
    "KDS_EL_KER": "KDS-EL/KER", "MEL": "MEL",
    "FWPSO": "FWPSO", "BPSO": "BPSO",
    "SaWDE": "SaWDE", "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
}
LINE_STYLES = {
    "KDS_EL": "-", "KDS_EL_DRS": "--", "KDS_EL_KER": "-.",
    "MEL": ":", "FWPSO": "-", "BPSO": "--",
    "SaWDE": "-.", "PSO_CSM": ":", "IGPSO": "--",
}


# ── 计算共有数据集（所有方法都有 curve 数据）──
def _get_curve_shared_datasets(versions, prefix="curve"):
    """Compute datasets that have curve data for all specified versions."""
    ds_sets = []
    for v in versions:
        files = set()
        for d in [EXP3_CURVES, EXP2_CURVES, EXP1_CURVES]:
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

# F8 算法: FWPSO (best baseline) + Ablation variants
F8_VERSIONS = ["FWPSO", "MEL", "KDS_EL_DRS", "KDS_EL_KER", "KDS_EL"]

# F9 算法: 显示有 NHD 的和没有 NHD 的对比
F9_VERSIONS = ["FWPSO", "MEL", "KDS_EL_DRS", "KDS_EL"]  # FWPSO/MEL NHD=0


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
    # 对齐长度（取最小长度）
    min_len = min(len(r) for r in runs)
    runs = np.array([r[:min_len] for r in runs])
    return runs


def load_from_both(version, dataset, prefix="curve"):
    """从正确的实验目录加载曲线：
       - KDS-EL 三变体 → Exp3 (V2, 已修复所有 bug)
       - MEL → Exp2 (V1 有效)
       - SOTA → Exp1
    """
    KDS_VERSIONS = {"KDS_EL", "KDS_EL_DRS", "KDS_EL_KER"}
    if version in KDS_VERSIONS:
        data = load_curves(version, dataset, EXP3_CURVES, prefix)
        if data is None:
            data = load_curves(version, dataset, EXP2_CURVES, prefix)
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
# F8: 适应度收敛曲线 (2×3)
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
            data = load_from_both(v, ds, prefix="curve")
            if data is not None:
                # 转换为 accuracy = 1 - fitness
                acc_data = 1.0 - data
                plot_with_band(ax, acc_data, COLORS[v], V_LABELS[v],
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

    # 统一图例
    handles = []
    for v in F8_VERSIONS:
        from matplotlib.lines import Line2D
        handles.append(Line2D([0], [0], color=COLORS[v],
                              linestyle=LINE_STYLES.get(v, "-"),
                              linewidth=1.3, label=V_LABELS[v]))
    fig.legend(handles=handles, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.8, handlelength=1.3, fontsize=6.5)
    fig.suptitle("F8: Convergence Curves (Mean Accuracy ± Std across 10 runs)",
                 fontsize=9, y=1.01)
    fig.tight_layout(rect=[0, 0.06, 1, 0.97])
    save_fig(fig, "F8_convergence_all", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F9: NHD 多样性曲线 (全部共有数据集)
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
            data = load_from_both(v, ds, prefix="nhd")
            if data is not None:
                # 检查是否全为 0
                if np.all(data < 1e-8):
                    # 基线 NHD=0，画虚线标注
                    ax.axhline(y=0, color=COLORS[v], linestyle=":",
                               linewidth=0.6, alpha=0.5)
                    ax.text(50, 0.02, f"{V_LABELS[v]}: NHD=0",
                            color=COLORS[v], fontsize=5, alpha=0.7,
                            ha="center", va="bottom")
                else:
                    plot_with_band(ax, data, COLORS[v], V_LABELS[v],
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

    # 图例
    handles = []
    for v in F9_VERSIONS:
        from matplotlib.lines import Line2D
        handles.append(Line2D([0], [0], color=COLORS[v],
                              linestyle=LINE_STYLES.get(v, "-"),
                              linewidth=1.3, label=V_LABELS[v]))
    fig.legend(handles=handles, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.8, handlelength=1.3, fontsize=6.5)
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
    print(f"  Exp1 (SOTA): {EXP1_CURVES}")
    print(f"  Exp2 (MEL): {EXP2_CURVES}")
    print(f"  Exp3 (KDS-EL): {EXP3_CURVES}")
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
