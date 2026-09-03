"""
Generate Figure 1 without parenthetical acronym clutter:
- 'Two-Phase Weight Scheduling' (removed (TPS))
- 'Feature-Importance Memory' (removed (W))
- 'Knowledge-Guided Elite Refinement' (removed (KER))
Maintains 100% style consistency with all other boxes in the diagram.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_cell(ax, x, y, w, h, text, subtext=None, fc='#FFFFFF', ec='#000000', lw=1.0, fs_main=8.8, fs_sub=9.5, bold_sub=True):
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(rect)
    if subtext is None:
        ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center',
                fontsize=fs_main, color='#000000', zorder=4)
    else:
        ax.text(x + w/2.0, y + h*0.72, text, ha='center', va='center',
                fontsize=fs_main, color='#000000', zorder=4)
        weight = 'bold' if bold_sub else 'normal'
        ax.text(x + w/2.0, y + h*0.28, subtext, ha='center', va='center',
                fontsize=fs_sub, color='#000000', weight=weight, zorder=4)
    return rect

def draw_curly_brace_left(ax, x, y_bottom, y_top, w=0.7, lw=1.0):
    y_mid = (y_bottom + y_top) / 2.0
    ax.plot([x + w, x + w*0.3, x + w*0.3, x, x + w*0.3, x + w*0.3, x + w],
            [y_top, y_top - 0.6, y_mid + 0.6, y_mid, y_mid - 0.6, y_bottom + 0.6, y_bottom],
            color='#000000', lw=lw, zorder=4, solid_capstyle='round')

def draw_curly_brace_right(ax, x, y_bottom, y_top, w=0.7, lw=1.0):
    y_mid = (y_bottom + y_top) / 2.0
    ax.plot([x - w, x - w*0.3, x - w*0.3, x, x - w*0.3, x - w*0.3, x - w],
            [y_top, y_top - 0.6, y_mid + 0.6, y_mid, y_mid - 0.6, y_bottom + 0.6, y_bottom],
            color='#000000', lw=lw, zorder=4, solid_capstyle='round')

def create_figure1_clean_names():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(12.0, 5.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 52)
    ax.axis('off')

    c_yellow = "#FFF2CC"
    c_green = "#D5E8D4"
    c_blue = "#DAE8FC"
    c_orange = "#FFE6CC"
    c_purple = "#E1D5E7"
    c_white = "#FFFFFF"
    c_border = "#000000"

    # =========================================================================
    # TOP BAND: Initialization & Binarization Pipeline
    # =========================================================================

    # 1. High-Dimensional Dataset
    rect_data = patches.Rectangle((1.5, 36.5), 14.0, 12.5, linewidth=1.1, edgecolor=c_border, facecolor='#F8F9FA', zorder=3)
    ax.add_patch(rect_data)
    ax.text(8.5, 44.5, 'High-Dimensional\nDataset', ha='center', va='center', fontsize=9.8, weight='bold', multialignment='center', zorder=4)
    ax.text(8.5, 39.5, r'$D \gg N_{\mathrm{samp}}$', ha='center', va='center', fontsize=9.0, zorder=4)

    # Arrow: Dataset -> MI-Guided Initialization
    ax.annotate('', xy=(18.0, 42.75), xytext=(15.5, 42.75),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # 2. MI-Guided Initialization Box
    rect_mi = patches.Rectangle((18.0, 36.5), 14.5, 12.5, linewidth=1.1, edgecolor=c_border, facecolor=c_white, zorder=3)
    ax.add_patch(rect_mi)
    ax.text(25.25, 42.75, 'MI-Guided\nInitialization', ha='center', va='center', fontsize=10.0, weight='bold', multialignment='center', zorder=4)

    # Arrow: MI-Guided -> Continuous Population
    ax.annotate('', xy=(35.0, 42.75), xytext=(32.5, 42.75),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # 3. Continuous Population (Matrix Grid)
    ax.text(45.5, 50.2, 'Continuous Population', ha='center', va='bottom', fontsize=9.2, weight='bold')
    draw_curly_brace_left(ax, 35.5, 34.5, 49.5, w=0.7, lw=1.0)

    # Row 1: X_{i=1}
    ax.text(39.0, 48.0, r'$X_{i=1}$', ha='right', va='center', fontsize=9.5)
    draw_cell(ax, 39.5, 46.8, 2.8, 2.4, r'$x_1$', fs_main=8.0)
    draw_cell(ax, 42.3, 46.8, 2.8, 2.4, r'$x_2$', fs_main=8.0)
    draw_cell(ax, 45.1, 46.8, 5.2, 2.4, r'$\dots$', fs_main=8.5)
    draw_cell(ax, 50.3, 46.8, 2.8, 2.4, r'$x_D$', fs_main=8.0)

    # Row 2: X_{i=2} (Highlighted Yellow)
    ax.text(39.0, 42.75, r'$X_{i=2}$', ha='right', va='center', fontsize=9.5)
    draw_cell(ax, 39.5, 41.0, 2.8, 3.5, r'$x_1$', '0.82', fc=c_yellow, fs_main=7.5, fs_sub=8.5)
    draw_cell(ax, 42.3, 41.0, 2.8, 3.5, r'$x_2$', '0.15', fc=c_yellow, fs_main=7.5, fs_sub=8.5)
    draw_cell(ax, 45.1, 41.0, 5.2, 3.5, r'$\dots$', fc=c_yellow, fs_main=8.5)
    draw_cell(ax, 50.3, 41.0, 2.8, 3.5, r'$x_D$', '0.91', fc=c_yellow, fs_main=7.5, fs_sub=8.5)

    # Vertical dots
    ax.text(39.0, 38.5, r'$\vdots$', ha='right', va='center', fontsize=11.0)
    ax.text(46.5, 38.5, r'$\vdots$', ha='center', va='center', fontsize=10.0)

    # Row N: X_{i=N}
    ax.text(39.0, 35.7, r'$X_{i=N}$', ha='right', va='center', fontsize=9.5)
    draw_cell(ax, 39.5, 34.5, 2.8, 2.4, r'$x_1$', fs_main=8.0)
    draw_cell(ax, 42.3, 34.5, 2.8, 2.4, r'$x_2$', fs_main=8.0)
    draw_cell(ax, 45.1, 34.5, 5.2, 2.4, r'$\dots$', fs_main=8.5)
    draw_cell(ax, 50.3, 34.5, 2.8, 2.4, r'$x_D$', fs_main=8.0)

    # Arrow: Continuous Population -> Binarization
    ax.annotate('', xy=(56.0, 42.75), xytext=(53.5, 42.75),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # 4. Explicit Binarization Box
    rect_bin = patches.Rectangle((56.0, 36.5), 13.5, 12.5, linewidth=1.1, edgecolor=c_border, facecolor=c_white, zorder=3)
    ax.add_patch(rect_bin)
    ax.text(62.75, 45.0, 'Binarization', ha='center', va='center', fontsize=9.8, weight='bold', zorder=4)
    ax.text(62.75, 40.0, r'$x_{i,j} = \mathbb{I}(p_{i,j} \geq \theta)$', ha='center', va='center', fontsize=9.2, zorder=4)

    # Arrow: Binarization -> Binary Feature Subsets
    ax.annotate('', xy=(72.5, 42.75), xytext=(69.5, 42.75),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # 5. Binary Feature Subsets
    ax.text(85.5, 50.2, 'Binary Feature Subsets', ha='center', va='bottom', fontsize=9.2, weight='bold')

    # Row 1: Subset 1
    ax.text(78.5, 48.0, 'Subset 1', ha='right', va='center', fontsize=8.5)
    draw_cell(ax, 79.5, 46.8, 3.2, 2.4, r'$x_1$', fs_main=8.0)
    draw_cell(ax, 82.7, 46.8, 3.2, 2.4, r'$x_2$', fs_main=8.0)
    draw_cell(ax, 85.9, 46.8, 5.8, 2.4, r'$\dots$', fs_main=8.5)
    draw_cell(ax, 91.7, 46.8, 3.2, 2.4, r'$x_D$', fs_main=8.0)

    # Row 2: Subset 2 (Highlighted Yellow)
    ax.text(78.5, 42.75, 'Subset 2', ha='right', va='center', fontsize=8.5, weight='bold')
    draw_cell(ax, 79.5, 41.0, 3.2, 3.5, r'$x_1$', '1', fc=c_yellow, fs_main=7.5, fs_sub=9.0)
    draw_cell(ax, 82.7, 41.0, 3.2, 3.5, r'$x_2$', '0', fc=c_yellow, fs_main=7.5, fs_sub=9.0)
    draw_cell(ax, 85.9, 41.0, 5.8, 3.5, r'$\dots$', fc=c_yellow, fs_main=8.5)
    draw_cell(ax, 91.7, 41.0, 3.2, 3.5, r'$x_D$', '1', fc=c_yellow, fs_main=7.5, fs_sub=9.0)

    # Vertical dots
    ax.text(78.5, 38.5, r'$\vdots$', ha='right', va='center', fontsize=11.0)
    ax.text(87.0, 38.5, r'$\vdots$', ha='center', va='center', fontsize=10.0)

    # Row N: Subset N
    ax.text(78.5, 35.7, 'Subset N', ha='right', va='center', fontsize=8.5)
    draw_cell(ax, 79.5, 34.5, 3.2, 2.4, r'$x_1$', fs_main=8.0)
    draw_cell(ax, 82.7, 34.5, 3.2, 2.4, r'$x_2$', fs_main=8.0)
    draw_cell(ax, 85.9, 34.5, 5.8, 2.4, r'$\dots$', fs_main=8.5)
    draw_cell(ax, 91.7, 34.5, 3.2, 2.4, r'$x_D$', fs_main=8.0)

    # =========================================================================
    # BOTTOM BAND: KDS-EL Optimization Engine Container (Matching EMSWOA Style)
    # =========================================================================

    # Big Engine Container Box: from y=2.0 to y=28.5, x from 1.5 to 74.5
    kdsel_box = patches.Rectangle((1.5, 2.0), 73.0, 26.5, linewidth=1.3, edgecolor=c_border, facecolor='none', zorder=2)
    ax.add_patch(kdsel_box)

    # Title centered right ON TOP OF the top border (with white patch to break line cleanly)
    ax.text(38.0, 28.5, 'KDS-EL Optimization Engine', ha='center', va='center', fontsize=12.0, weight='bold', zorder=4,
            bbox=dict(facecolor='#FFFFFF', edgecolor='none', pad=2.5))

    # Input Arrow: Runs horizontally at y=32.2 ABOVE the title, drops down at x=22.0
    ax.plot([87.0, 87.0, 22.0, 22.0], [34.0, 32.2, 32.2, 27.2], color='#000000', lw=1.1, zorder=3)
    ax.annotate('', xy=(22.0, 27.2), xytext=(22.0, 27.7),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)
    ax.text(54.0, 32.6, 'Input', ha='center', va='bottom', fontsize=9.5, weight='bold')

    # -------------------------------------------------------------------------
    # CENTER-INSIDE: Evolutionary Core Search Architecture (Zero Parenthetical Clutter!)
    # -------------------------------------------------------------------------

    # 1. Collaborative Dual-Swarm Container
    rect_ds = patches.Rectangle((16.0, 21.2), 33.0, 6.0, linewidth=1.0, edgecolor=c_border, facecolor=c_green, zorder=3)
    ax.add_patch(rect_ds)
    ax.text(32.5, 25.8, 'Collaborative Dual-Swarm Co-evolution', ha='center', va='center', fontsize=9.0, weight='bold', zorder=4)

    rect_p1 = patches.Rectangle((17.0, 21.8), 15.0, 2.9, linewidth=0.8, edgecolor=c_border, facecolor=c_white, zorder=4)
    ax.add_patch(rect_p1)
    ax.text(24.5, 23.25, r'$\mathcal{P}_1$: Continuous Exploration', ha='center', va='center', fontsize=8.0, zorder=5)

    rect_p2 = patches.Rectangle((33.0, 21.8), 15.0, 2.9, linewidth=0.8, edgecolor=c_border, facecolor=c_white, zorder=4)
    ax.add_patch(rect_p2)
    ax.text(40.5, 23.25, r'$\mathcal{P}_2$: Discrete Feature Sampling', ha='center', va='center', fontsize=8.0, zorder=5)

    # Arrow from Dual-Swarm to TPS
    ax.annotate('', xy=(32.5, 18.5), xytext=(32.5, 21.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # 2. Two-Phase Weight Scheduling (Pure Name!)
    rect_tps = patches.Rectangle((16.0, 15.5), 33.0, 3.0, linewidth=1.0, edgecolor=c_border, facecolor=c_blue, zorder=3)
    ax.add_patch(rect_tps)
    ax.text(32.5, 17.0, 'Two-Phase Weight Scheduling', ha='center', va='center', fontsize=9.2, weight='bold', zorder=4)

    # Arrow from TPS to Feature-Importance Memory
    ax.annotate('', xy=(32.5, 12.8), xytext=(32.5, 15.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # 3. Feature-Importance Memory (Pure Name!)
    rect_w = patches.Rectangle((16.0, 9.6), 33.0, 3.2, linewidth=1.0, edgecolor=c_border, facecolor=c_yellow, zorder=3)
    ax.add_patch(rect_w)
    ax.text(32.5, 11.2, 'Feature-Importance Memory', ha='center', va='center', fontsize=9.2, weight='bold', zorder=4)

    # Arrow from Memory to Knowledge-Guided Elite Refinement
    ax.annotate('', xy=(32.5, 6.8), xytext=(32.5, 9.6),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)
    ax.text(33.5, 8.2, 'Knowledge guidance', ha='left', va='center', fontsize=7.5, weight='bold', color='#B25900')

    # 4. Knowledge-Guided Elite Refinement (Pure Name!)
    rect_ker = patches.Rectangle((16.0, 3.6), 33.0, 3.2, linewidth=1.0, edgecolor=c_border, facecolor=c_orange, zorder=3)
    ax.add_patch(rect_ker)
    ax.text(32.5, 5.2, 'Knowledge-Guided Elite Refinement', ha='center', va='center', fontsize=9.2, weight='bold', zorder=4)

    # -------------------------------------------------------------------------
    # LEFT-INSIDE: ZERO-CROSSING Generational Loop & Adaptive Recovery
    # -------------------------------------------------------------------------
    # Exit left from KER at (16.0, 5.2) to (11.5, 5.2)
    ax.plot([16.0, 11.5], [5.2, 5.2], color='#000000', lw=1.1, zorder=4)

    # Arrow up into Stagnation diamond at (11.5, 7.8)
    ax.annotate('', xy=(11.5, 7.8), xytext=(11.5, 5.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)

    # Diamond at (11.5, 9.6)
    poly_diamond = patches.Polygon([[11.5, 11.4], [14.2, 9.6], [11.5, 7.8], [8.8, 9.6]],
                                   linewidth=1.0, edgecolor=c_border, facecolor='#FFF2CC', zorder=4)
    ax.add_patch(poly_diamond)
    ax.text(11.5, 9.6, 'Stagnation?', ha='center', va='center', fontsize=6.8, weight='bold', zorder=5)

    # Branch 1: "No" -> Normal While(t < T) loop
    ax.plot([11.5, 11.5, 16.0], [11.4, 24.2, 24.2], color='#000000', lw=1.1, zorder=4)
    ax.annotate('', xy=(16.0, 24.2), xytext=(15.2, 24.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.1), zorder=4)
    ax.text(12.2, 12.0, 'No', ha='left', va='bottom', fontsize=7.2, weight='bold')
    ax.text(12.3, 17.5, r'While($t < T$)', ha='left', va='center', fontsize=7.8, weight='bold', rotation=90)

    # Branch 2: "Yes" -> Left into Adaptive Recovery
    ax.annotate('', xy=(7.4, 9.6), xytext=(8.8, 9.6),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.0), zorder=4)
    ax.text(8.1, 10.3, 'Yes', ha='center', va='bottom', fontsize=7.2, weight='bold')

    # Adaptive Recovery box at x=[2.2, 7.4], y=[7.0, 12.2]
    rect_air = patches.Rectangle((2.2, 7.0), 5.2, 5.2, linewidth=1.0, edgecolor=c_border, facecolor=c_purple, zorder=4)
    ax.add_patch(rect_air)
    ax.text(4.8, 9.6, 'Adaptive\nRecovery', ha='center', va='center', fontsize=7.2, weight='bold', multialignment='center', zorder=5)

    # From Adaptive Recovery: Goes UP along x=4.8 to y=20.5, then turns RIGHT into loop bus at (11.5, 20.5)
    ax.plot([4.8, 4.8, 11.5], [12.2, 20.5, 20.5], color='#000000', lw=1.0, zorder=4)
    ax.annotate('', xy=(11.5, 20.5), xytext=(10.7, 20.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.0), zorder=4)
    ax.text(4.4, 16.5, 'Re-inject', ha='right', va='center', fontsize=7.0, weight='bold', rotation=90)

    # -------------------------------------------------------------------------
    # RIGHT-INSIDE: EVALUATION BUS (CURLY BRACE WRAPS ONLY DUAL-SWARM!)
    # Exact EMSWOA alignment: Curly brace wraps ONLY the swarm generation stage!
    # Height of Dual-Swarm = [21.2, 27.2]. Midpoint = 24.2.
    # -------------------------------------------------------------------------
    draw_curly_brace_right(ax, 49.8, 21.2, 27.2, w=0.7, lw=1.0)

    # PURE STRAIGHT HORIZONTAL ARROW FROM BRACE TIP TO TRANSFER FUNCTION!
    ax.annotate('', xy=(59.0, 24.2), xytext=(49.8, 24.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.0), zorder=4)

    # Transfer function box at y in [22.2, 26.2]
    rect_tf_in = patches.Rectangle((59.0, 22.2), 14.0, 4.0, linewidth=0.9, edgecolor=c_border, facecolor=c_white, zorder=3)
    ax.add_patch(rect_tf_in)
    ax.text(66.0, 24.2, 'Transfer Function', ha='center', va='center', fontsize=8.8, weight='bold', zorder=4)

    # Arrow from Transfer function to Fitness engine
    ax.annotate('', xy=(66.0, 19.8), xytext=(66.0, 22.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.0), zorder=4)

    # Evaluation text: Generous open bay, COMPLETELY CLEAR!
    ax.text(54.4, 17.5, 'Evaluating\nfeature subset\nquality', ha='center', va='center', fontsize=7.8, multialignment='center')

    # Fitness Function Container: y in [3.6, 19.8]
    rect_fit = patches.Rectangle((59.0, 3.6), 14.0, 16.2, linewidth=1.0, edgecolor=c_border, facecolor=c_white, zorder=3)
    ax.add_patch(rect_fit)
    ax.text(66.0, 18.2, 'Fitness Function', ha='center', va='center', fontsize=8.8, weight='bold', zorder=4)

    rect_err = patches.Rectangle((60.0, 11.8), 12.0, 4.5, linewidth=0.8, edgecolor=c_border, facecolor='#F8F9FA', zorder=4)
    ax.add_patch(rect_err)
    ax.text(66.0, 14.05, 'Classification Error Rate', ha='center', va='center', fontsize=8.0, weight='bold', zorder=5)

    rect_num = patches.Rectangle((60.0, 5.2), 12.0, 4.5, linewidth=0.8, edgecolor=c_border, facecolor='#F8F9FA', zorder=4)
    ax.add_patch(rect_num)
    ax.text(66.0, 7.45, 'Feature Subset Ratio', ha='center', va='center', fontsize=8.0, weight='bold', zorder=5)

    # =========================================================================
    # FITNESS FEEDBACK: 10 UNITS BELOW THE CURLY BRACE! (100% ZERO CROSSING)
    # Curly brace ends at y=21.2, while this arrow is at y=11.2!
    # =========================================================================
    ax.annotate('', xy=(49.0, 11.2), xytext=(59.0, 11.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.0), zorder=4)
    ax.text(54.0, 12.0, 'Fitness feedback', ha='center', va='bottom', fontsize=7.2, weight='bold')

    # =========================================================================
    # BOTTOM RIGHT: Out -> Optimal Feature Subset (OUTSIDE THE ENGINE BOX)
    # =========================================================================
    # Clean Out arrow exiting from Fitness Function at y=14.05 through engine border (at x=74.5)
    ax.annotate('', xy=(78.5, 14.05), xytext=(73.0, 14.05),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=1.3), zorder=4)
    ax.text(75.75, 15.0, 'Out', ha='center', va='bottom', fontsize=11.0, weight='bold')

    ax.text(88.5, 19.5, 'Optimal Feature Subset', ha='center', va='bottom', fontsize=10.5, weight='bold')

    draw_cell(ax, 78.5, 11.3, 4.2, 5.5, r'$x_1$', '0', fc=c_orange, fs_main=8.8, fs_sub=10.5)
    draw_cell(ax, 82.7, 11.3, 4.2, 5.5, r'$x_2$', '0', fc=c_orange, fs_main=8.8, fs_sub=10.5)
    draw_cell(ax, 86.9, 11.3, 7.5, 5.5, r'$\dots\dots$', fc=c_orange, fs_main=10.0)
    draw_cell(ax, 94.4, 11.3, 4.2, 5.5, r'$x_D$', '1', fc=c_orange, fs_main=8.8, fs_sub=10.5)

    ax.text(88.5, 7.3, r'$d^{\star} = \|\mathbf{x}^{\star}\|_0 \ll D$', ha='center', va='center', fontsize=10.5, weight='bold')

    # Save to all required destinations
    base_dir = r"e:\多目标优化\KDS-EL"
    out_dir = os.path.join(base_dir, 'output', 'figures')
    tex_fig_dir = os.path.join(base_dir, 'Template-LaTeX-Elsevier-CAS-DC-master', 'figs')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tex_fig_dir, exist_ok=True)

    pdf_path = os.path.join(out_dir, 'F1_dataflow_journal.pdf')
    png_path = os.path.join(out_dir, 'F1_dataflow_journal.png')
    tex_pdf_path = os.path.join(tex_fig_dir, 'Fig1.pdf')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.savefig(tex_pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f'Successfully generated clean names Figure 1 at: {png_path}')

if __name__ == '__main__':
    create_figure1_clean_names()
