"""Publication-grade Harmonized Palette Figure 1 for KDS-EL.
Strictly adheres to Top-Tier Journal (IEEE TEVC/TCYB, Elsevier KBS) 2-Hue Color Harmony:
- Removes rainbow patchwork.
- Standardizes background cards to clean Porcelain White (#FFFFFF) & Soft Ice Slate (#F8FAFC).
- Uses semantic accent borders & typography (Cobalt Blue for PSO/Transfer, Amber for Refinement, Crimson for Re-injection).
- Preserves crystal-clear contrast while eliminating visual noise.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle

def create_figure1():
    # Times New Roman & STIX math typography
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    # Single-column aspect ratio (width: 5.6 in, height: 8.9 in)
    fig, ax = plt.subplots(figsize=(5.6, 8.9), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Sophisticated Harmonized Academic Palette (100% Unified with Figures 2, 3, 4)
    c_card_bg = '#FFFFFF'         # Porcelain White
    c_container_bg = '#F8FAFC'    # Ultra-soft Slate Tint (Slate 50)
    c_border_neutral = '#CBD5E1'  # Slate 300
    c_border_dark = '#64748B'     # Slate 500
    c_text_dark = '#0F172A'       # Slate 900
    c_text_muted = '#475569'      # Slate 600
    
    # Primary Academic Blues
    c_navy_title = '#1E3A8A'      # Blue 900 (Main titles & headers)
    c_blue_primary = '#1D4ED8'    # Blue 700 (Flow arrows, key focus)
    c_blue_mid = '#3B82F6'        # Blue 500
    c_blue_subtle = '#EFF6FF'     # Blue 50 (Soft Ice Blue fills)
    c_blue_border = '#93C5FD'     # Blue 300 (Subtle Blue borders)
    
    # Structural Neutrals
    c_slate_dark = '#334155'      # Slate 700
    c_slate_mid = '#64748B'       # Slate 500
    c_slate_border = '#CBD5E1'    # Slate 300

    def draw_badge(x, y, w, h, bg, border, lw=1.1, r=0.5, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 1. TOP: INPUT & MI-PRIOR SEEDING
    # =========================================================================
    # Dataset Input
    draw_badge(12, 93.0, 76, 5.8, c_card_bg, c_border_neutral, lw=1.2, r=0.5, zorder=2)
    ax.text(50, 95.9, r'High-Dimensional Dataset $\mathbf{X}, \; \mathbf{Y}$',
            fontsize=13.5, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)

    # Down arrow (Exact touchpoint at MI-Prior Seeding top edge y=87.7)
    ax.annotate('', xy=(50, 87.7), xytext=(50, 93.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.8, mutation_scale=11), zorder=4)

    # MI-Prior Seeding Box
    draw_badge(12, 81.5, 76, 6.2, c_blue_subtle, c_blue_border, lw=1.3, r=0.5, zorder=2)
    ax.text(50, 84.6, 'MI-Prior Seeding',
            fontsize=13.5, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)

    # Fork arrows from Seeding to Subpop 1 and Subpop 2
    ax.annotate('', xy=(26.25, 73.0), xytext=(38, 81.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.6,
                                connectionstyle='arc3,rad=0.12', mutation_scale=11), zorder=4)
    ax.annotate('', xy=(73.75, 73.0), xytext=(62, 81.5),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.6,
                                connectionstyle='arc3,rad=-0.12', mutation_scale=11), zorder=4)

    # =========================================================================
    # 2. MAIN EVOLUTIONARY LOOP CONTAINER
    # =========================================================================
    loop_box = FancyBboxPatch((4.5, 14.5), 91, 59.5, boxstyle="round,pad=0.02,rounding_size=1.0",
                              facecolor=c_container_bg, edgecolor=c_border_dark, linewidth=1.3, linestyle='--', zorder=1)
    ax.add_patch(loop_box)
    ax.text(50, 71.8, r'Main Evolutionary Optimization Loop',
            fontsize=12.5, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)

    # TOP OF LOOP: Cumulative Feature Importance Matrix W
    mat_x = 7.5
    mat_y = 61.0
    mat_w = 85.0
    mat_h = 9.0
    draw_badge(mat_x, mat_y, mat_w, mat_h, c_card_bg, c_border_neutral, lw=1.1, r=0.5, zorder=2)
    ax.text(mat_x + mat_w/2, mat_y + 6.5, r'Cumulative Feature-Importance Matrix $\mathbf{W}$',
            fontsize=10.5, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)
    
    # Feature strips with 1..D arrangement: f_1, f_2, f_3, ..., f_{D-2}, f_{D-1}, f_D
    strip_labels = [r'$f_1$', r'$f_2$', r'$f_3$', r'$\dots$', r'$f_{D-2}$', r'$f_{D-1}$', r'$f_D$']
    strip_weights = [0.92, 0.85, 0.20, None, 0.88, 0.15, 0.78]
    strip_w = 9.0
    strip_gap = 2.4
    total_strips_w = len(strip_labels) * strip_w + (len(strip_labels) - 1) * strip_gap
    strip_x_start = mat_x + (mat_w - total_strips_w) / 2.0
    strip_y = mat_y + 1.2
    strip_h = 3.2

    for si, (s_lbl, s_w) in enumerate(zip(strip_labels, strip_weights)):
        sx = strip_x_start + si * (strip_w + strip_gap)
        if s_w is not None:
            scol = plt.cm.Blues(0.25 + 0.70 * s_w)
            ax.add_patch(patches.Rectangle((sx, strip_y), strip_w, strip_h, facecolor=scol, edgecolor='#94A3B8', lw=0.7, zorder=4))
            ax.text(sx + strip_w/2, strip_y + strip_h/2, s_lbl, fontsize=9.0, fontweight='bold',
                    ha='center', va='center', color='#FFFFFF' if s_w > 0.6 else '#0F172A', zorder=5)
        else:
            ax.add_patch(patches.Rectangle((sx, strip_y), strip_w, strip_h, facecolor='#F1F5F9', edgecolor='#CBD5E1', lw=0.7, zorder=4))
            ax.text(sx + strip_w/2, strip_y + strip_h/2, s_lbl, fontsize=9.8, fontweight='bold',
                    ha='center', va='center', color='#475569', zorder=5)

    # -------------------------------------------------------------------------
    # DUAL SUBPOPULATIONS: Subpop 1 (Left) and Subpop 2 (Right)
    # -------------------------------------------------------------------------
    # Subpopulation 1: Continuous PSO (Crisp Porcelain White + Cobalt Blue Accent)
    sub1_x = 7.5
    sub1_y = 35.8
    sub1_w = 37.5
    sub1_h = 22.2
    draw_badge(sub1_x, sub1_y, sub1_w, sub1_h, c_card_bg, c_blue_border, lw=1.2, r=0.6, zorder=2)
    ax.text(sub1_x + sub1_w/2, sub1_y + 18.5, r'Subpopulation 1 ($\mathcal{P}_1$)', fontsize=11.2, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)

    # Aspect ratio scaling so circles and arrows strictly calibrated to F2 Initial PSO Swarm
    ar_f1 = 5.6 / 8.9

    # Particles in Subpop 1 (Cobalt Blue)
    p1_coords = [(15.5, 47.0), (25.5, 50.0), (35.0, 46.5), (18.0, 39.5), (30.0, 39.0)]
    p1_angles = [35.0, 80.0, -35.0, -125.0, 145.0]
    for (px, py), ang in zip(p1_coords, p1_angles):
        rad = np.radians(ang)
        dx = 3.85 * np.cos(rad)
        dy = 3.85 * ar_f1 * np.sin(rad)
        ax.add_patch(patches.Ellipse((px, py), 2.95, 2.95 * ar_f1, facecolor=c_blue_primary, edgecolor='#FFFFFF', lw=0.9, zorder=3))
        ax.annotate('', xy=(px + dx, py + dy), xytext=(px, py),
                    arrowprops=dict(arrowstyle='->', color=c_blue_mid, lw=1.5, mutation_scale=9), zorder=5)

    # Subpopulation 2: Discrete Importance Sampling (Crisp Porcelain White + Slate Accent)
    sub2_x = 55.0
    sub2_y = 35.8
    sub2_w = 37.5
    sub2_h = 22.2
    draw_badge(sub2_x, sub2_y, sub2_w, sub2_h, c_card_bg, c_slate_border, lw=1.2, r=0.6, zorder=2)
    ax.text(sub2_x + sub2_w/2, sub2_y + 18.5, r'Subpopulation 2 ($\mathcal{P}_2$)', fontsize=11.2, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=3)

    # Particles in Subpop 2 (Slate Neutral)
    p2_coords = [(63.0, 47.0), (73.0, 50.0), (83.0, 46.5), (65.5, 39.5), (78.0, 39.0)]
    p2_angles = [-55.0, 45.0, 140.0, -140.0, 95.0]
    for (px, py), ang in zip(p2_coords, p2_angles):
        rad = np.radians(ang)
        dx = 3.85 * np.cos(rad)
        dy = 3.85 * ar_f1 * np.sin(rad)
        ax.add_patch(patches.Ellipse((px, py), 2.95, 2.95 * ar_f1, facecolor=c_slate_dark, edgecolor='#FFFFFF', lw=0.9, zorder=3))
        ax.annotate('', xy=(px + dx, py + dy), xytext=(px, py),
                    arrowprops=dict(arrowstyle='->', color=c_slate_mid, lw=1.5, mutation_scale=9), zorder=5)

    # Inter-Subpopulation Knowledge Transfer Arrow (Clean gap with arrow above text)
    draw_badge(42.0, 42.8, 16.0, 7.8, c_card_bg, c_blue_border, lw=1.1, r=0.4, zorder=4)
    ax.annotate('', xy=(45.0, 48.0), xytext=(55.0, 48.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.6, mutation_scale=10), zorder=5)
    ax.text(50.0, 44.8, r'$\mathbf{g}_{\mathrm{best},2}\ \mathrm{Transfer}$', fontsize=8.2, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=6)

    # Arrows: Subpopulations update W (Upwards) and Subpop 2 learns from W (Downwards)
    ax.annotate('', xy=(26.25, mat_y), xytext=(26.25, sub1_y + sub1_h),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.4, mutation_scale=9), zorder=4)
    ax.text(24.8, 59.5, 'Reward Feedback', fontsize=8.6, fontweight='bold', color=c_blue_primary, ha='right', va='center')

    ax.annotate('', xy=(73.75, sub2_y + sub2_h), xytext=(73.75, mat_y),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.4, mutation_scale=9), zorder=4)
    ax.text(75.2, 59.5, r'Sample from $\mathbf{W}$', fontsize=8.6, fontweight='bold', color=c_blue_primary, ha='left', va='center')

    # -------------------------------------------------------------------------
    # CORE STRATEGY COORDINATORS: CLEAN MINIMAL JOURNAL ARCHITECTURE
    # -------------------------------------------------------------------------
    # Tier 1: Two-Phase Objective Weight Scheduling Spanning Bar (Clean, no hyperparameter clutter)
    tps_x = 7.5
    tps_y = 26.5
    tps_w = 85.0
    tps_h = 5.8
    draw_badge(tps_x, tps_y, tps_w, tps_h, c_card_bg, c_blue_border, lw=1.1, r=0.5, zorder=2)
    ax.text(tps_x + tps_w/2, tps_y + tps_h/2, 'Two-Phase Dynamic Objective Scheduling',
            fontsize=10.5, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)

    # Inward down arrows from Subpop 1 and Subpop 2 into TPS
    ax.annotate('', xy=(26.25, tps_y + tps_h), xytext=(26.25, sub1_y),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_mid, lw=1.3, mutation_scale=9), zorder=4)
    ax.annotate('', xy=(73.75, tps_y + tps_h), xytext=(73.75, sub2_y),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_mid, lw=1.3, mutation_scale=9), zorder=4)

    # Tier 2: Symmetrical Dual Operators Row (KER Left + Adaptive Re-injection Right)
    # Left Card: Knowledge-guided Elite Refinement
    ker_x = 7.5
    ker_y = 16.0
    ker_w = 37.5
    ker_h = 6.2
    draw_badge(ker_x, ker_y, ker_w, ker_h, c_card_bg, c_blue_border, lw=1.1, r=0.5, zorder=2)
    ax.text(ker_x + ker_w/2, ker_y + ker_h/2, 'Knowledge-Guided Elite Refinement',
            fontsize=9.0, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)

    # Right Card: Adaptive MI Re-injection
    re_x = 55.0
    re_y = 16.0
    re_w = 37.5
    re_h = 6.2
    draw_badge(re_x, re_y, re_w, re_h, c_card_bg, c_blue_border, lw=1.1, r=0.5, zorder=2)
    ax.text(re_x + re_w/2, re_y + re_h/2, 'Adaptive MI Re-injection',
            fontsize=9.0, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)

    # Arrows from TPS down into KER and Adaptive Re-injection
    ax.annotate('', xy=(26.25, ker_y + ker_h), xytext=(26.25, tps_y),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_mid, lw=1.3, mutation_scale=9), zorder=4)
    ax.annotate('', xy=(73.75, re_y + re_h), xytext=(73.75, tps_y),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_mid, lw=1.3, mutation_scale=9), zorder=4)

    # Re-injection feedback loop back to Subpopulations (Clean dashed loop, zero hyperparameter clutter)
    ax.annotate('', xy=(sub2_x + sub2_w, 47.0), xytext=(re_x + re_w, re_y + re_h/2),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.3,
                                connectionstyle='arc3,rad=0.35', linestyle='--', mutation_scale=8), zorder=4)

    # -------------------------------------------------------------------------
    # LEFT EVOLUTIONARY LOOP ARROW
    # -------------------------------------------------------------------------
    ax.annotate('', xy=(sub1_x, 47.0), xytext=(ker_x, ker_y + ker_h/2),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_mid, lw=1.4,
                                connectionstyle='arc3,rad=-0.48', mutation_scale=9), zorder=4)

    # =========================================================================
    # 3. TERMINATION & OUTPUT BLOCK
    # =========================================================================
    # Down arrow from Main Loop exit to Output (Exact touchpoint at Output top edge y=8.0)
    ax.annotate('', xy=(50, 8.0), xytext=(50, 14.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.8, mutation_scale=11), zorder=4)

    draw_badge(10, 2.0, 80, 6.0, c_blue_subtle, c_blue_border, lw=1.3, r=0.5, zorder=2)
    ax.text(50, 5.0, r'Optimal Compact Feature Subset $\mathbf{x}^\star$', fontsize=13.5, fontweight='bold',
            color=c_navy_title, ha='center', va='center', zorder=3)

    # Save Outputs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F1_architecture_journal.pdf')
    png_path = os.path.join(out_dir, 'F1_architecture_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated Clean Publication-Grade Figure 1 PDF and PNG successfully!')

def generate_drawio():
    from generate_journal_drawio import build_f1
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_file = os.path.join(base_dir, 'output', 'figures', 'F1_architecture_journal.drawio')
    build_f1(out_file)

if __name__ == '__main__':
    create_figure1()
    generate_drawio()

