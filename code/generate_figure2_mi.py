"""Publication-grade Figure 2 for MI-Prior Seeding and Adaptive Re-injection in KDS-EL.
Strictly adheres to Top-Tier Journal (Elsevier SWEVO/KBS/INS, IEEE TEVC) design standards:
- 3 Clear Modular Stage Containers perfectly filled without empty whitespace.
- Prominent Top Headers for all 3 Stages (Offline Filter MI, Swarm Seeding, Search & Recovery).
- Clear Directional Convergence Arrows pointing to x* Optimum.
- Pure theoretical notations without hardcoded empirical hyperparameter clutter.
- Pure academic palette: Cobalt Blue + Slate Neutral.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
from scipy.interpolate import make_interp_spline

def create_figure2():
    # Times New Roman & STIX math typography
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(16.5, 9.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Unified Harmonized Palette (Cobalt Blue + Slate Neutral)
    c_card_bg = '#FFFFFF'
    c_panel_bg = '#F8FAFC'        # Slate 50
    c_text_dark = '#0F172A'       # Slate 900
    c_text_muted = '#475569'      # Slate 600
    c_text_light = '#64748B'      # Slate 500
    
    # Primary Academic Blues
    c_blue_navy = '#1E3A8A'       # Blue 900
    c_blue_primary = '#1D4ED8'    # Blue 700
    c_blue_mid = '#3B82F6'        # Blue 500
    c_blue_cell = '#EFF6FF'       # Blue 50
    c_blue_border = '#93C5FD'     # Blue 300
    
    # Structural Neutrals
    c_slate_dark = '#334155'      # Slate 700
    c_slate_mid = '#64748B'       # Slate 500
    c_border_neutral = '#CBD5E1'  # Slate 300

    def draw_badge(x, y, w, h, bg, border, lw=1.1, r=0.4, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.03,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 0. MAIN STRUCTURAL BOUNDING CONTAINERS (方框/面板结构)
    # =========================================================================
    # Stage 1 Container: Offline Filter-Level MI Estimation
    draw_badge(2.0, 3.0, 33.5, 94.0, c_panel_bg, c_border_neutral, lw=1.2, r=0.6, zorder=1)
    
    # Stage 2 Container: Knowledge-Informed Swarm Seeding
    draw_badge(36.8, 3.0, 35.2, 94.0, c_panel_bg, c_border_neutral, lw=1.2, r=0.6, zorder=1)

    # Stage 3 Container: Search Space & Stagnation Recovery
    draw_badge(73.2, 3.0, 24.8, 94.0, c_panel_bg, c_border_neutral, lw=1.2, r=0.6, zorder=1)

    # =========================================================================
    # 1. LEFT: HIGH-DIMENSIONAL FEATURE SPACE & MI ESTIMATION
    # =========================================================================
    sec1_cx = 9.5
    ax.text(sec1_cx, 92.5, 'High-Dimensional\nFeature Space', fontsize=12.5, fontweight='bold',
            color=c_text_dark, ha='center', va='center', zorder=3)
    ax.text(sec1_cx, 86.2, r'$\mathbf{X} \in \mathbb{R}^{N \times D}$',
            fontsize=11.0, color=c_text_muted, ha='center', va='center', zorder=3)

    col_x_start = 3.2
    col_w = 0.95
    col_h = 50.0
    col_y = 28.0
    
    num_cols = 11
    np.random.seed(101)
    for c_idx in range(num_cols):
        cx = col_x_start + c_idx * (col_w + 0.35)
        if c_idx == 5:
            ax.text(cx + 0.3, col_y + col_h/2, r'$\dots$', fontsize=14, fontweight='bold', ha='center', va='center', color=c_text_light, zorder=3)
            continue
        
        col_color = '#FFFFFF'
        border_col = '#CBD5E1' if c_idx not in [0, 1, 7, 9] else '#93C5FD'
        draw_badge(cx, col_y, col_w, col_h, col_color, border_col, lw=0.8, r=0.15, zorder=3)
        
        for sy in np.linspace(col_y + 2.5, col_y + col_h - 2.5, 10):
            stripe_alpha = 0.4 + 0.4 * np.random.rand()
            ax.plot([cx + 0.15, cx + col_w - 0.15], [sy, sy], color=border_col, lw=0.7, alpha=stripe_alpha, zorder=4)

    # Column header labels
    ax.text(col_x_start + 0.5, col_y + col_h + 1.8, r'$f_1$', fontsize=10.5, fontweight='bold', ha='center', va='bottom', color=c_text_dark, zorder=3)
    ax.text(col_x_start + 1.8, col_y + col_h + 1.8, r'$f_2$', fontsize=10.5, fontweight='bold', ha='center', va='bottom', color=c_text_dark, zorder=3)
    ax.text(col_x_start + 3.1, col_y + col_h + 1.8, r'$f_3$', fontsize=10.5, fontweight='bold', ha='center', va='bottom', color=c_text_dark, zorder=3)
    ax.text(col_x_start + 10.8, col_y + col_h + 1.8, r'$f_D$', fontsize=10.5, fontweight='bold', ha='center', va='bottom', color=c_text_dark, zorder=3)

    # Target Label Vector Y
    y_vec_x = col_x_start + 12.8
    draw_badge(y_vec_x, col_y, 1.4, col_h, c_blue_cell, c_blue_border, lw=1.1, r=0.2, zorder=3)
    ax.text(y_vec_x + 0.7, col_y + col_h + 1.8, r'$\mathbf{Y}$', fontsize=11.5, fontweight='bold', ha='center', va='bottom', color=c_blue_navy, zorder=3)
    for sy in np.linspace(col_y + 3.0, col_y + col_h - 3.0, 11):
        ax.add_patch(Circle((y_vec_x + 0.7, sy), 0.28, facecolor=c_blue_primary, edgecolor='none', zorder=4))

    ax.text(sec1_cx, 22.5, 'Feature Matrix & Labels', fontsize=10.0, fontstyle='italic',
            color=c_text_muted, ha='center', va='center', zorder=3)

    # =========================================================================
    # 2. MI TRANSFORMATION & PRIOR NORMALIZATION
    # =========================================================================
    ax.annotate('', xy=(21.5, 53.0), xytext=(18.2, 53.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2, mutation_scale=14), zorder=5)

    sec2_cx = 26.8
    ax.text(sec2_cx, 92.5, 'Mutual Information\nEstimation', fontsize=12.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(sec2_cx, 86.2, r'$I(f_j; \mathbf{Y}) = H(\mathbf{Y}) - H(\mathbf{Y} \mid f_j)$',
            fontsize=10.2, color=c_text_dark, ha='center', va='center', zorder=3)

    # Continuous MI Relevance Profile (Enlarged)
    p_x_start = 22.2
    p_w = 9.2
    p_h = 36.0
    p_y = 42.0

    prof_y = np.linspace(p_y, p_y + p_h, 90)
    for idx, py_val in enumerate(prof_y):
        frac = (py_val - p_y) / p_h
        bar_len = p_w * (0.15 + 0.85 * (frac ** 1.6))
        col_r = int(239 - (239 - 29) * (frac ** 1.2))
        col_g = int(246 - (246 - 78) * (frac ** 1.2))
        col_b = int(255 - (255 - 216) * (frac ** 1.2))
        hex_col = f"#{col_r:02x}{col_g:02x}{col_b:02x}"
        ax.plot([p_x_start, p_x_start + bar_len], [py_val, py_val], color=hex_col, lw=2.5, solid_capstyle='round', zorder=3)

    ax.plot([p_x_start, p_x_start], [p_y, p_y + p_h], color=c_blue_primary, lw=1.5, zorder=4)
    
    ax.text(p_x_start + p_w + 0.6, p_y + p_h - 2.0, 'High MI', fontsize=9.8, fontweight='bold', color=c_blue_navy, va='center', zorder=3)
    ax.text(p_x_start + p_w * 0.6 + 0.6, p_y + p_h * 0.55, 'Medium MI', fontsize=9.5, color=c_blue_mid, va='center', zorder=3)
    ax.text(p_x_start + p_w * 0.25 + 0.6, p_y + 3.0, 'Low MI', fontsize=9.5, color=c_text_muted, va='center', zorder=3)

    # Down arrow from profile to normalization
    ax.annotate('', xy=(sec2_cx, 36.5), xytext=(sec2_cx, 40.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.6, mutation_scale=10), zorder=4)

    # Min-Max Normalization Box
    norm_bx = 20.0
    norm_by = 22.0
    norm_bw = 13.6
    norm_bh = 12.5
    draw_badge(norm_bx, norm_by, norm_bw, norm_bh, c_card_bg, c_blue_border, lw=1.2, r=0.4, zorder=3)
    ax.text(norm_bx + norm_bw/2, norm_by + 8.8, 'MI-Derived Prior Vector', fontsize=10.8, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=4)
    ax.text(norm_bx + norm_bw/2, norm_by + 4.0, r'$\widetilde{\mathbf{m}} = \frac{\mathbf{I} - I_{\min}}{I_{\max} - I_{\min}} \in [0, 1]^D$',
            fontsize=10.2, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=4)

    # =========================================================================
    # 3. CENTRAL: KNOWLEDGE-INFORMED SWARM SEEDING (ENLARGED)
    # =========================================================================
    sec2_main_cx = 54.4
    ax.text(sec2_main_cx, 92.5, 'Knowledge-Informed Swarm Seeding', fontsize=13.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(sec2_main_cx, 86.2, 'Hybrid Dual-Subpopulation Initialization',
            fontsize=10.5, color=c_text_muted, ha='center', va='center', zorder=3)

    # Dual Fork Arrows from Stage 1 into Stage 2
    ax.annotate('', xy=(38.0, 67.0), xytext=(33.6, 28.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.16', mutation_scale=14), zorder=5)
    
    ax.annotate('', xy=(38.0, 33.0), xytext=(33.6, 26.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=2.2,
                                connectionstyle='arc3,rad=0.12', mutation_scale=14), zorder=5)

    # UPPER BRANCH: MI-Guided Seeding (Scaled up)
    ub_x = 38.5
    ub_y = 52.0
    ub_w = 14.8
    ub_h = 30.0
    draw_badge(ub_x, ub_y, ub_w, ub_h, c_card_bg, c_blue_border, lw=1.3, r=0.5, zorder=2)
    
    ax.text(ub_x + ub_w/2, ub_y + 26.0, 'MI-Guided Seeding', fontsize=12.0, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(ub_x + ub_w/2, ub_y + 20.5, r'$\mathbf{p}_i = \mathrm{clip}\left(\widetilde{\mathbf{m}} + \boldsymbol{\varepsilon}_i, \; 0, \; 1\right)$',
            fontsize=10.5, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=3)
    ax.text(ub_x + ub_w/2, ub_y + 15.5, r'$\boldsymbol{\varepsilon}_i \sim \mathcal{N}(\mathbf{0}, \, \sigma^2 \mathbf{I})$',
            fontsize=9.6, color=c_text_muted, ha='center', va='center', zorder=3)

    bar_x_start = ub_x + 1.6
    bar_y_base = ub_y + 4.5
    mi_bar_heights = [5.5, 4.8, 1.8, 1.3, 2.4, 4.2, 5.3]
    for b_i, bh in enumerate(mi_bar_heights):
        bx = bar_x_start + b_i * 1.7
        bar_c = c_blue_primary if bh > 3.5 else c_blue_border
        ax.add_patch(patches.Rectangle((bx, bar_y_base), 1.1, bh, facecolor=bar_c, edgecolor='none', zorder=4))
    ax.text(ub_x + ub_w/2, ub_y + 1.8, r'$p_{i,j} \propto \widetilde{m}_j$',
            fontsize=9.5, fontstyle='italic', color=c_blue_primary, ha='center', va='bottom', zorder=3)

    # LOWER BRANCH: Uniform Random Seeding (Scaled up)
    lb_x = 38.5
    lb_y = 18.0
    lb_w = 14.8
    lb_h = 30.0
    draw_badge(lb_x, lb_y, lb_w, lb_h, c_card_bg, c_border_neutral, lw=1.3, r=0.5, zorder=2)

    ax.text(lb_x + lb_w/2, lb_y + 26.0, 'Uniform Random Seeding', fontsize=12.0, fontweight='bold',
            color=c_slate_dark, ha='center', va='center', zorder=3)
    ax.text(lb_x + lb_w/2, lb_y + 20.5, r'$\mathbf{p}_i \sim \mathcal{U}(0, \, 1)^D$',
            fontsize=10.5, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=3)
    ax.text(lb_x + lb_w/2, lb_y + 15.5, r'$p_{i,j} \sim \mathcal{U}(0, \, 1)$',
            fontsize=9.6, color=c_text_muted, ha='center', va='center', zorder=3)

    np.random.seed(99)
    for b_i in range(7):
        bx = bar_x_start + b_i * 1.7
        bh = np.random.uniform(1.8, 5.2)
        ax.add_patch(patches.Rectangle((bx, lb_y + 4.5), 1.1, bh, facecolor=c_slate_mid, edgecolor='none', zorder=4))
    ax.text(lb_x + lb_w/2, lb_y + 1.8, 'Stochastic Exploration',
            fontsize=9.5, fontstyle='italic', color=c_slate_dark, ha='center', va='bottom', zorder=3)

    # =========================================================================
    # 4. MERGE INTO INITIAL PSO POPULATION (Full Height)
    # =========================================================================
    ax.annotate('', xy=(55.5, 62.0), xytext=(53.3, 67.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.12', mutation_scale=14), zorder=5)
    ax.annotate('', xy=(55.5, 38.0), xytext=(53.3, 33.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=2.2,
                                connectionstyle='arc3,rad=0.12', mutation_scale=14), zorder=5)

    pop_x = 55.5
    pop_y = 18.0
    pop_w = 15.0
    pop_h = 64.0
    draw_badge(pop_x, pop_y, pop_w, pop_h, c_card_bg, '#94A3B8', lw=1.4, r=0.6, zorder=2)

    # Header
    ax.text(pop_x + pop_w/2, pop_y + 59.5, 'Initial PSO Swarm', fontsize=13.0, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(pop_x + pop_w/2, pop_y + 55.5, r'$\mathcal{P} = \{\mathbf{p}_1, \dots, \mathbf{p}_N\}$',
            fontsize=10.2, color=c_text_muted, ha='center', va='center', zorder=3)

    # Aspect ratio correction for visual arrow uniformity (figsize 16.5 x 9.2)
    aspect_ratio = 16.5 / 9.2

    # Top half: MI-guided particles (Varied dynamic directions, zorder on top)
    ax.text(pop_x + pop_w/2, pop_y + 50.5, 'Subpopulation 1: MI-Guided', fontsize=10.2, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)
    p1_angles = [25.0, 65.0, 10.0, 80.0, 45.0, -20.0, 60.0, 35.0, 75.0]
    idx_p1 = 0
    np.random.seed(77)
    for row in range(3):
        for col in range(3):
            dot_x = pop_x + 3.0 + col * 4.4 + np.random.uniform(-0.3, 0.3)
            dot_y = pop_y + 36.5 + row * 4.0 + np.random.uniform(-0.3, 0.3)
            rad = np.radians(p1_angles[idx_p1 % len(p1_angles)])
            dx = 1.3 * np.cos(rad)
            dy = 1.3 * aspect_ratio * np.sin(rad)
            idx_p1 += 1
            ax.add_patch(patches.Ellipse((dot_x, dot_y), 1.0, 1.0 * aspect_ratio, facecolor=c_blue_primary, edgecolor='#FFFFFF', lw=0.9, zorder=3))
            ax.annotate('', xy=(dot_x + dx, dot_y + dy), xytext=(dot_x, dot_y),
                        arrowprops=dict(arrowstyle='->', color=c_blue_mid, lw=1.5, mutation_scale=9), zorder=5)

    ax.plot([pop_x + 1.5, pop_x + pop_w - 1.5], [pop_y + 32.0, pop_y + 32.0], color='#CBD5E1', lw=1.1, linestyle='--', zorder=3)

    # Bottom half: Uniform random particles (Varied scrambled directions, matching size, zorder on top)
    ax.text(pop_x + pop_w/2, pop_y + 27.5, 'Subpopulation 2: Random', fontsize=10.2, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=3)
    p2_angles = [135.0, -45.0, 210.0, 30.0, -120.0, 85.0, 165.0, -70.0, 0.0]
    idx_p2 = 0
    np.random.seed(88)
    for row in range(3):
        for col in range(3):
            dot_x = pop_x + 3.0 + col * 4.4 + np.random.uniform(-0.3, 0.3)
            dot_y = pop_y + 13.5 + row * 4.0 + np.random.uniform(-0.3, 0.3)
            rad = np.radians(p2_angles[idx_p2 % len(p2_angles)])
            dx = 1.3 * np.cos(rad)
            dy = 1.3 * aspect_ratio * np.sin(rad)
            idx_p2 += 1
            ax.add_patch(patches.Ellipse((dot_x, dot_y), 1.0, 1.0 * aspect_ratio, facecolor=c_slate_mid, edgecolor='#FFFFFF', lw=0.9, zorder=3))
            ax.annotate('', xy=(dot_x + dx, dot_y + dy), xytext=(dot_x, dot_y),
                        arrowprops=dict(arrowstyle='->', color=c_slate_dark, lw=1.5, mutation_scale=9), zorder=5)

    # =========================================================================
    # 5. RIGHT: SEARCH SPACE & STAGNATION RECOVERY (ENLARGED)
    # =========================================================================
    ax.annotate('', xy=(74.5, 50.0), xytext=(70.5, 50.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_navy, lw=2.2, mutation_scale=14), zorder=5)

    sec3_main_cx = 85.6
    ax.text(sec3_main_cx, 92.5, 'Search Space & Recovery', fontsize=13.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(sec3_main_cx, 86.2, 'Evolutionary Convergence & Resilience',
            fontsize=10.5, color=c_text_muted, ha='center', va='center', zorder=3)

    # 2D Fitness Contour Landscape (Scaled up to fill height)
    search_x = 74.5
    search_y = 23.0
    search_w = 22.2
    search_h = 59.0
    draw_badge(search_x, search_y, search_w, search_h, '#F8FAFC', '#CBD5E1', lw=1.2, r=0.6, zorder=2)

    # Centered contours
    c_center = (search_x + 12.5, search_y + 38.0)
    for r_idx, (rw, rh, c_alpha) in enumerate([(8.8, 6.0, 0.4), (6.2, 4.2, 0.6), (3.8, 2.6, 0.8), (1.8, 1.2, 1.0)]):
        ellipse = patches.Ellipse(c_center, rw*2, rh*2, angle=-10, facecolor='none',
                                  edgecolor='#93C5FD', lw=1.1, alpha=c_alpha, linestyle='-', zorder=3)
        ax.add_patch(ellipse)

    # Global Optimum Star in Deep Cobalt/Navy Blue
    ax.plot(c_center[0], c_center[1], marker='*', markersize=15, color=c_blue_primary, markeredgecolor=c_blue_navy, markeredgewidth=1.1, zorder=8)
    ax.text(c_center[0] + 1.2, c_center[1] + 1.2, r'$\mathbf{x}^\star\ \mathrm{Optimum}$', fontsize=10.8, fontweight='bold', color=c_blue_navy, zorder=8)

    # Particle trajectories converging smoothly with PROPERLY TERMINATING ARROWS (No line protrusion)
    traj_pts = [
        np.array([[search_x + 2.5, search_y + 48.0], [search_x + 6.5, search_y + 44.0], [c_center[0] - 1.2, c_center[1] + 1.0]]),
        np.array([[search_x + 3.0, search_y + 24.0], [search_x + 7.5, search_y + 30.0], [c_center[0] - 0.6, c_center[1] - 1.0]]),
        np.array([[search_x + 18.5, search_y + 20.0], [search_x + 15.5, search_y + 29.0], [c_center[0] + 0.9, c_center[1] - 0.5]])
    ]
    for idx, t_arr in enumerate(traj_pts):
        t_eval = np.linspace(0, 1, len(t_arr))
        t_dense = np.linspace(0, 1, 60)
        sx = make_interp_spline(t_eval, t_arr[:, 0], k=2)(t_dense)
        sy = make_interp_spline(t_eval, t_arr[:, 1], k=2)(t_dense)
        t_col = c_blue_primary if idx == 0 else (c_blue_mid if idx == 1 else c_slate_mid)
        # Draw curve up to 90%
        ax.plot(sx[:-5], sy[:-5], color=t_col, lw=1.5, linestyle='-', alpha=0.85, zorder=4)
        ax.add_patch(Circle((sx[0], sy[0]), 0.45, facecolor=t_col, edgecolor='#FFFFFF', lw=0.8, zorder=5))
        # Draw final segment cleanly as arrowhead pointing exactly to target point
        ax.annotate('', xy=(sx[-1], sy[-1]), xytext=(sx[-6], sy[-6]),
                    arrowprops=dict(arrowstyle='-|>', color=t_col, lw=1.6, mutation_scale=12), zorder=6)

    # Stagnation Trap Node (Local Minima Basin)
    stag_center = (search_x + 5.5, search_y + 9.5)
    ax.add_patch(patches.Ellipse(stag_center, 6.5, 4.2, facecolor='#F1F5F9', edgecolor=c_slate_dark, lw=1.2, linestyle=':', zorder=4))
    ax.add_patch(Circle(stag_center, 0.5, facecolor=c_slate_dark, edgecolor='#FFFFFF', lw=0.8, zorder=6))
    ax.text(stag_center[0], stag_center[1] + 3.0, 'Stagnation Detected', fontsize=10.0,
            fontweight='bold', color=c_slate_dark, ha='center', va='bottom', zorder=7)

    # =========================================================================
    # 6. ADAPTIVE MI RE-INJECTION (FEEDBACK LOOP - CLEAN UNBOXED TEXT)
    # =========================================================================
    rein_x = 51.5
    rein_y = 5.0
    rein_w = 36.5
    rein_h = 8.8
    draw_badge(rein_x, rein_y, rein_w, rein_h, c_card_bg, c_blue_border, lw=1.2, r=0.4, zorder=8)
    ax.text(rein_x + rein_w/2, rein_y + 5.7, 'Adaptive MI Re-injection', fontsize=11.2, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=9)
    ax.text(rein_x + rein_w/2, rein_y + 2.3, r'$\mathbf{p}_{\mathrm{inferior}} \leftarrow \mathrm{clip}\left(\widetilde{\mathbf{m}} + \boldsymbol{\varepsilon}_i, \; 0, \; 1\right)$',
            fontsize=10.0, color=c_text_dark, ha='center', va='center', zorder=9)

    # Leg 1: Stagnation Trap -> Re-injection Badge (Clean text directly beside line on left)
    ax.annotate('', xy=(rein_x + rein_w - 4.0, rein_y + rein_h), xytext=(stag_center[0], stag_center[1] - 2.2),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0, mutation_scale=14), zorder=10)
    ax.text(81.2, 22.0, 'Trigger', fontsize=9.8, fontweight='bold', color=c_blue_navy, ha='right', va='center', zorder=12)

    # Leg 2: Re-injection Badge -> Bottom of Initial PSO Swarm box (Clean text directly beside line)
    ax.annotate('', xy=(pop_x + pop_w/2, pop_y), xytext=(rein_x + 8.0, rein_y + rein_h),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.16', mutation_scale=14), zorder=10)
    ax.text(58.5, 16.0, 'Re-inject', fontsize=9.8, fontweight='bold', color=c_blue_navy, ha='right', va='center', zorder=12)

    # Save Outputs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F2_mi_initialization_journal.pdf')
    png_path = os.path.join(out_dir, 'F2_mi_initialization_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated Scaled & Filled Clean Figure 2 PDF and PNG successfully!')

def generate_drawio():
    import xml.etree.ElementTree as ET
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f2-mi-seeding', name='Figure 2: MI-Prior Seeding & Re-injection')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1422', dy='798', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1400', pageHeight='850', math='1', shadow='0')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def add_cell(cid, value, style, x, y, w, h, parent='1'):
        cell = ET.SubElement(root, 'mxCell', id=str(cid), value=str(value), style=style, parent=parent, vertex='1')
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})
        return cell

    # Structural Outer Containers
    add_cell('f2_c1', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 20, 20, 440, 800)
    add_cell('f2_c2', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 480, 20, 480, 800)
    add_cell('f2_c3', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 980, 20, 380, 800)

    # Headers & elements
    add_cell('h1', '&lt;b&gt;High-Dimensional Feature Space&lt;/b&gt;&lt;br&gt;$$X \\in \\mathbb{R}^{N \\times D}$$', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 40, 30, 200, 40)
    add_cell('h2', '&lt;b&gt;&lt;font color=\"#1D4ED8\"&gt;Mutual Information Prior&lt;/font&gt;&lt;/b&gt;&lt;br&gt;$$I(f_j; Y)$$', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 260, 30, 180, 40)
    add_cell('h3', '&lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;Stage 2: Knowledge-Informed Swarm Seeding&lt;/font&gt;&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;', 500, 30, 440, 40)
    add_cell('h4', '&lt;b&gt;Initial PSO Swarm&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 740, 30, 200, 40)
    add_cell('h5', '&lt;b&gt;Stage 3: Search Space &amp; Recovery&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;', 1000, 30, 240, 40)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_file = os.path.join(base_dir, 'output', 'figures', 'F2_mi_initialization_journal.drawio')
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated Clean Figure 2 Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure2()
    generate_drawio()
    generate_drawio()
