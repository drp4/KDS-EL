"""
F8 + F9: 收敛曲线 & TwoPhase 消融收敛
=====================================
从 npy 文件读取迭代曲线数据，生成：
  F8 — 适应度/准确率收敛曲线 (爱斯维尔顶刊标准: 2×3 平衡网格，包含全局均值与5个典型数据集)
  F9 — TwoPhase vs NoPool 消融收敛对比 (全量 20 数据集网格)

数据来源：
  - Exp1: output/formal_experiment_20260701_094943/curves/
  - Exp2: output/formal_experiment_20260628_205157/curves/
  - Exp4: output/formal_experiment_20260707_142018/curves/
  - MEL_MI: output/formal_experiment_mel_mi/curves/
  - Final: output/formal_experiment_final/curves/

用法：python code/plot_convergence.py [--out output/figures/]
"""
import os, sys, argparse, re
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

PROJ = Path(__file__).resolve().parent.parent
EXP1_CURVES = PROJ / "output" / "formal_experiment_20260701_094943" / "curves"
EXP2_CURVES = PROJ / "output" / "formal_experiment_20260628_205157" / "curves"
EXP4_CURVES = PROJ / "output" / "formal_experiment_20260707_142018" / "curves"
MEL_MI_CURVES = PROJ / "output" / "formal_experiment_mel_mi" / "curves"
FINAL_CURVES = PROJ / "output" / "formal_experiment_final" / "curves"

ALL_CURVE_DIRS = [EXP1_CURVES, EXP2_CURVES, EXP4_CURVES, MEL_MI_CURVES, FINAL_CURVES]

# ── 全局样式 (对标 Elsevier 5p 顶刊排版规范) ──
mpl.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 8.0,
    "axes.titlesize": 8.5,
    "axes.labelsize": 8.0,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
    "legend.fontsize": 7.5,
    "legend.framealpha": 0.95,
    "legend.edgecolor": "#d0d0d0",
    "legend.borderpad": 0.4,
    "axes.linewidth": 0.7,
    "grid.linewidth": 0.35,
    "lines.linewidth": 1.0,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.03,
})

# ── 颜色和标签 ──
COLORS = {
    "KDS_EL_TwoPhase": "#D93829",  # Proposed — vibrant crimson / coral
    "KDS_EL_NoPool":   "#2B6CB0",  # NoPool — slate blue
    "MEL_MI":          "#2A9D8F",  # MEL+MI — deep teal
    "MEL":             "#718096",  # MEL baseline — neutral gray
    "FWPSO":           "#5D7E99",
    "IGPSO":           "#6C8BA3",
    "PSO_CSM":         "#7F99AE",
    "SaWDE":           "#94AABD",
    "BPSO":            "#AABBC8",
    "NSGA_II_FS":      "#7E8D96",
    "W_MOPSO_FS":      "#8F9DA4",
    "fMOPSO_FS":       "#9FABB2",
    "MOEA_D_FS":       "#AEB8BD",
    "MOPSO_FS":        "#BCC4C8",
}

V_LABELS = {
    "KDS_EL_TwoPhase": "KDS-EL",
    "KDS_EL_NoPool":   "KDS-EL w/o TPS",
    "MEL_MI":          "KDS-EL w/o TPS&KER",
    "MEL":             "MEL",
    "FWPSO": "FWPSO", "BPSO": "BPSO",
    "SaWDE": "SaWDE", "PSO_CSM": "PSO-CSM", "IGPSO": "IGPSO",
    "NSGA_II_FS": "NSGA-II-FS", "MOPSO_FS": "MOPSO-FS",
    "MOEA_D_FS": "MOEA-D-FS", "fMOPSO_FS": "fMOPSO-FS",
    "W_MOPSO_FS": "W-MOPSO-FS",
}

LINE_STYLES = {
    "KDS_EL_TwoPhase": "-",
    "KDS_EL_NoPool":   "--",
    "MEL_MI":          "-.",
    "MEL":             ":",
    "FWPSO": "-", "BPSO": "--",
    "SaWDE": "-.", "PSO_CSM": ":", "IGPSO": "--",
    "NSGA_II_FS": "-", "MOPSO_FS": "--", "MOEA_D_FS": "-.",
    "fMOPSO_FS": "-", "W_MOPSO_FS": "-.",
}

# 20 权威基准数据集
CORE_20 = [
    "ALL1", "ALL4", "ALL_AML", "Adenoma", "BASEHOCK", "COIL20",
    "Colon", "DLBCL", "Gastric", "Gastric1", "Gastric2", "ISOLET",
    "Leukaemia", "Lymphoma", "Myeloma", "PCMAC", "Prostate",
    "SRBCT", "T1D", "madelon"
]

# 4 变体消融链
F8_ABL_VERSIONS = ["KDS_EL_TwoPhase", "KDS_EL_NoPool", "MEL_MI", "MEL"]

# F9: TwoPhase vs NoPool 消融收敛对比
F9_VERSIONS = ["KDS_EL_NoPool", "KDS_EL_TwoPhase"]


def _get_curve_shared_datasets(versions, prefix="curve"):
    """Compute datasets that have curve data for all specified versions."""
    all_dirs = ALL_CURVE_DIRS
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
       - KDS-EL 变体 → FINAL_CURVES
       - MEL_MI → MEL_MI_CURVES
       - MEL → EXP2_CURVES / EXP1_CURVES
       - MOFS → EXP4_CURVES / EXP1_CURVES
       - SOTA → EXP1_CURVES / EXP2_CURVES
    """
    KDS_VERSIONS = {"KDS_EL_NoPool", "KDS_EL_TwoPhase"}
    MOFS_NAMES = {"NSGA_II_FS", "MOPSO_FS", "MOEA_D_FS",
                   "fMOPSO_FS", "W_MOPSO_FS"}

    if version in KDS_VERSIONS:
        data = load_curves(version, dataset, FINAL_CURVES, prefix)
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


def plot_with_band(ax, data, color, label, linestyle, alpha_fill=0.12, linewidth=1.1):
    """绘制均值 ± 标准差曲线。"""
    if data is None or len(data) == 0:
        return
    T = data.shape[1]
    x = np.arange(T)
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    ax.plot(x, mean, color=color, linestyle=linestyle, linewidth=linewidth, label=label)
    ax.fill_between(x, mean - std, mean + std, color=color, alpha=alpha_fill,
                    linewidth=0)
    return mean, std


def save_fig(fig, name, out_dir):
    for ext in (".pdf", ".png"):
        p = os.path.join(out_dir, name + ext)
        fig.savefig(p)
    print(f"  [OK] {name}")


# ══════════════════════════════════════════════════════════════════════════════
# F8: 适应度收敛曲线 (爱斯维尔顶刊标准: 2×3 平衡网格)
# ══════════════════════════════════════════════════════════════════════════════

def fig_f8_convergence(out_dir):
    """F8: Convergence — Balanced 2×3 grid: (a) Overall Mean (20 DS) + (b)-(f) 5 representative datasets."""
    # 5 代表性数据集涵盖各类高维特征场景：
    # 1. Adenoma: 微阵列小样本基因 (N=36, D=7457)
    # 2. DLBCL: 多类别生物医疗 (N=77, D=5469)
    # 3. T1D: 超高维基因芯片 (N=101, D=54675)
    # 4. BASEHOCK: 大样本高维文本 (N=1993, D=4862)
    # 5. Madelon: 强非线性特征交互/人工合成 (N=2000, D=500)
    REP_DS_CONFIGS = [
        ("Adenoma", "(b) Adenoma ($N=36, D=7{,}457$)", (0.93, 1.005)),
        ("DLBCL", "(c) DLBCL ($N=77, D=5{,}469$)", (0.92, 1.005)),
        ("T1D", "(d) T1D ($N=101, D=54{,}675$)", (0.68, 0.88)),
        ("BASEHOCK", "(e) BASEHOCK ($N=1{,}993, D=4{,}862$)", (0.81, 0.93)),
        ("madelon", "(f) Madelon ($N=2{,}000, D=500$)", (0.68, 0.91)),
    ]

    ABL_PLOT_COLORS = {
        "KDS_EL_TwoPhase": "#D93829",   # 珊瑚红 (本文方法)
        "KDS_EL_NoPool":   "#2B6CB0",   # 钢蓝 (消融变体)
        "MEL_MI":          "#2A9D8F",   # 墨绿/青蓝 (去KER&TPS)
        "MEL":             "#718096",   # 石板灰 (原始基线)
    }
    ABL_PLOT_STYLES = {
        "KDS_EL_TwoPhase": "-",
        "KDS_EL_NoPool":   "--",
        "MEL_MI":          "-.",
        "MEL":             ":",
    }
    ABL_PLOT_WIDTHS = {
        "KDS_EL_TwoPhase": 1.6,
        "KDS_EL_NoPool":   1.2,
        "MEL_MI":          1.1,
        "MEL":             1.1,
    }
    ABL_PLOT_LABELS = {
        "KDS_EL_TwoPhase": "KDS-EL",
        "KDS_EL_NoPool":   "KDS-EL w/o TPS",
        "MEL_MI":          "KDS-EL w/o TPS&KER",
        "MEL":             "MEL",
    }

    print("F8: Convergence — Balanced 2x3 Grid (Overall Mean + 5 Representative Datasets)...")

    # ── 1. 全局 20 数据集均值预计算 ──
    all_curves = {v: [] for v in F8_ABL_VERSIONS}
    for v in F8_ABL_VERSIONS:
        for ds in CORE_20:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                all_curves[v].append(np.mean(1.0 - data, axis=0))

    fig, axes = plt.subplots(2, 3, figsize=(9.2, 5.0))
    axes = axes.ravel()

    # ── (a) Overall Mean Convergence (Top-Left Subplot) ──
    ax0 = axes[0]
    for v in F8_ABL_VERSIONS:
        if all_curves[v]:
            stacked = np.array(all_curves[v])
            mean_c = np.mean(stacked, axis=0)
            sem_c = np.std(stacked, axis=0) / np.sqrt(len(stacked))
            x = np.arange(len(mean_c))
            ax0.plot(x, mean_c, color=ABL_PLOT_COLORS[v], linestyle=ABL_PLOT_STYLES[v],
                     linewidth=ABL_PLOT_WIDTHS[v])
            ax0.fill_between(x, mean_c - sem_c, mean_c + sem_c,
                             color=ABL_PLOT_COLORS[v], alpha=0.14, linewidth=0)

    ax0.set_title("(a) Overall Mean (20 Datasets)", fontsize=8.5, fontweight="bold", pad=4)
    ax0.set_xlabel("Iteration", fontsize=7.5)
    ax0.set_ylabel("Mean Accuracy", fontsize=7.5)
    ax0.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax0.set_xlim(0, 100)
    ax0.set_ylim(0.83, 0.97)
    ax0.grid(True, linestyle="--", alpha=0.35, linewidth=0.4)
    ax0.axvline(x=70, color="#888888", linestyle=":", linewidth=0.8, alpha=0.7)
    ax0.text(71, 0.84, "t=70 (Phase 2)", fontsize=6.0, color="#555555", rotation=90)

    # ── (b)-(f) 5 个代表性数据集 ──
    for idx, (ds, title, ylim) in enumerate(REP_DS_CONFIGS, start=1):
        ax = axes[idx]
        for v in F8_ABL_VERSIONS:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                acc_data = 1.0 - data
                mean_c = np.mean(acc_data, axis=0)
                std_c = np.std(acc_data, axis=0)
                x = np.arange(len(mean_c))
                ax.plot(x, mean_c, color=ABL_PLOT_COLORS[v], linestyle=ABL_PLOT_STYLES[v],
                        linewidth=ABL_PLOT_WIDTHS[v])
                ax.fill_between(x, mean_c - std_c, mean_c + std_c,
                                color=ABL_PLOT_COLORS[v], alpha=0.10, linewidth=0)

        ax.set_title(title, fontsize=8.5, fontweight="bold", pad=4)
        ax.set_xlabel("Iteration", fontsize=7.5)
        ax.set_ylabel("Accuracy", fontsize=7.5)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.set_xlim(0, 100)
        ax.set_ylim(ylim)
        ax.grid(True, linestyle="--", alpha=0.35, linewidth=0.4)
        ax.axvline(x=70, color="#888888", linestyle=":", linewidth=0.8, alpha=0.7)

    # ── 全局统一顶部图例 (Elsevier 标准规范) ──
    handles = [
        Line2D([0], [0], color=ABL_PLOT_COLORS[v], linestyle=ABL_PLOT_STYLES[v],
               linewidth=1.6 if "TwoPhase" in v else 1.2, label=ABL_PLOT_LABELS[v])
        for v in F8_ABL_VERSIONS
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.025),
               ncol=4, frameon=True, facecolor="#fafafa", edgecolor="#d0d0d0",
               fontsize=7.8, handlelength=2.2, columnspacing=1.4, framealpha=0.95)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_fig(fig, "F8_convergence", out_dir)
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# F9: TwoPhase vs NoPool 消融收敛对比
# ══════════════════════════════════════════════════════════════════════════════

def fig_f9_nhd(out_dir):
    """F9: TwoPhase vs NoPool convergence — fitness curves, all shared datasets."""
    ds_list = _get_curve_shared_datasets(F9_VERSIONS, prefix="curve")
    ds_list = [d for d in ds_list if d in CORE_20]
    n_ds = len(ds_list)
    rows, cols = _auto_grid(n_ds, max_cols=5)
    print(f"F9: TwoPhase vs NoPool convergence ({n_ds} datasets, {rows}x{cols})...")

    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 1.8 * rows))
    if n_ds == 1:
        axes = np.array([axes])
    axes = axes.ravel()

    for i, ds in enumerate(ds_list):
        ax = axes[i]
        for v in F9_VERSIONS:
            data = load_from_all(v, ds, prefix="curve")
            if data is not None:
                acc_data = 1.0 - data  # fitness -> accuracy
                plot_with_band(ax, acc_data, COLORS.get(v, "#333333"),
                               V_LABELS.get(v, v),
                               LINE_STYLES.get(v, "-"), alpha_fill=0.15)

        ax.set_title(ds, fontsize=7, pad=1.5)
        ax.set_xlabel("Iteration", fontsize=6.5)
        ax.set_ylabel("Accuracy", fontsize=6.5)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(4, prune="lower"))
        ax.grid(linestyle="--", alpha=0.4, which="both")
        ax.set_xlim(0, 100)

    for j in range(n_ds, len(axes)):
        axes[j].set_visible(False)

    handles = []
    for v in F9_VERSIONS:
        handles.append(Line2D([0], [0], color=COLORS.get(v, "#333333"),
                              linestyle=LINE_STYLES.get(v, "-"),
                              linewidth=1.3, label=V_LABELS.get(v, v)))
    fig.legend(handles=handles, loc="lower center", ncol=2,
               bbox_to_anchor=(0.5, -0.03), frameon=True,
               columnspacing=0.6, handlelength=1.2, fontsize=6)
    fig.suptitle("F9: Convergence of KDS-EL and KDS-EL w/o TPS (Mean Accuracy ± Std across 10 runs)",
                 fontsize=9, y=1.01)
    fig.tight_layout(rect=[0, 0.06, 1, 0.97])
    save_fig(fig, "F9_twophase_convergence", out_dir)
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

    print("Curve data sources:")
    print(f"  Exp1 (SOTA):  {EXP1_CURVES}")
    print(f"  Exp2 (MEL):   {EXP2_CURVES}")
    print(f"  Exp4 (MOFS):  {EXP4_CURVES}")
    print(f"  MEL+MI:       {MEL_MI_CURVES}")
    print(f"  Final:        {FINAL_CURVES}")
    print(f"\nGenerating -> {out_dir}\n")

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

    print(f"\nDone! -> {out_dir}")


if __name__ == "__main__":
    main()
