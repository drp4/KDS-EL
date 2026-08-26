"""Publication-grade Figure 2 for MI-Prior Seeding and Adaptive Re-injection in KDS-EL.
Harmonized with Figure 3 Academic Color System:
- Strict 2-Family Academic Palette: Cobalt/Navy Blue (#1D4ED8 / #1E3A8A) + Slate Neutral (#334155 / #64748B / #CBD5E1).
- Crisp Porcelain White backgrounds (#FFFFFF).
- Zero color clash, professional, clean layout.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
from scipy.interpolate import make_interp_spline

def create_figure2():
    # Times New Roman & STIX math typography (Unified with Figure 1, 3, 4)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(16.5, 9.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Unified Harmonized Palette (Cobalt Blue + Slate Neutral)
    c_card_bg = '#FFFFFF'
    c_text_dark = '#0F172A'       # Slate 900
    c_text_muted = '#475569'      # Slate 600
    c_text_light = '#64748B'      # Slate 500
    
    # Primary Academic Blues
    c_blue_navy = '#1E3A8A'       # Blue 900 (Main titles & headers)
    c_blue_primary = '#1D4ED8'    # Blue 700 (Flow arrows, MI-guided, active components)
    c_blue_mid = '#3B82F6'        # Blue 500
    c_blue_cell = '#EFF6FF'       # Blue 50
    c_blue_border = '#93C5FD'     # Blue 300
    
    # Structural Neutrals
    c_slate_dark = '#334155'      # Slate 700 (Random exploration)
    c_slate_mid = '#64748B'       # Slate 500
    c_slate_border = '#CBD5E1'    # Slate 300
    c_gray_fill = '#F8FAFC'       # Slate 50

    def draw_badge(x, y, w, h, bg, border, lw=1.1, r=0.4, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.03,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 1. LEFT: HIGH-DIMENSIONAL FEATURE SPACE
    # =========================================================================
    sec1_cx = 9.5
    ax.text(sec1_cx, 89.5, 'High-Dimensional\nFeature Space', fontsize=12.5, fontweight='bold',
            color=c_text_dark, ha='center', va='center')
    ax.text(sec1_cx, 82.5, r'$\mathbf{X} \in \mathbb{R}^{N_{\mathrm{samp}} \times D}, \quad D \gg 10^3$',
            fontsize=10.0, color=c_text_muted, ha='center', va='center')

    col_x_start = 3.2
    col_w = 0.95
    col_h = 39.0
    col_y = 35.0
    
    num_cols = 11
    np.random.seed(101)
    for c_idx in range(num_cols):
        cx = col_x_start + c_idx * (col_w + 0.35)
        if c_idx == 5:
            ax.text(cx + 0.3, col_y + col_h/2, r'$\dots$', fontsize=13, fontweight='bold', ha='center', va='center', color=c_text_light)
            continue
        
        col_color = '#FFFFFF'
        border_col = '#CBD5E1' if c_idx not in [0, 1, 7, 9] else '#93C5FD'
        draw_badge(cx, col_y, col_w, col_h, col_color, border_col, lw=0.8, r=0.15, zorder=3)
        
        for sy in np.linspace(col_y + 2.5, col_y + col_h - 2.5, 7):
            stripe_alpha = 0.4 + 0.4 * np.random.rand()
            ax.plot([cx + 0.15, cx + col_w - 0.15], [sy, sy], color=border_col, lw=0.7, alpha=stripe_alpha, zorder=4)

    # Column header labels
    ax.text(col_x_start + 0.5, col_y + col_h + 1.8, r'$f_1$', fontsize=10.0, fontweight='bold', ha='center', va='bottom', color=c_text_dark)
    ax.text(col_x_start + 1.8, col_y + col_h + 1.8, r'$f_2$', fontsize=10.0, fontweight='bold', ha='center', va='bottom', color=c_text_dark)
    ax.text(col_x_start + 3.1, col_y + col_h + 1.8, r'$f_3$', fontsize=10.0, fontweight='bold', ha='center', va='bottom', color=c_text_dark)
    ax.text(col_x_start + 10.8, col_y + col_h + 1.8, r'$f_D$', fontsize=10.0, fontweight='bold', ha='center', va='bottom', color=c_text_dark)

    # Target Label Vector Y (Soft Ice Blue + Slate Navy text)
    y_vec_x = col_x_start + 12.8
    draw_badge(y_vec_x, col_y, 1.3, col_h, c_blue_cell, c_blue_border, lw=1.1, r=0.2, zorder=3)
    ax.text(y_vec_x + 0.65, col_y + col_h + 1.8, r'$\mathbf{Y}$', fontsize=11.0, fontweight='bold', ha='center', va='bottom', color=c_blue_navy)
    for sy in np.linspace(col_y + 3.0, col_y + col_h - 3.0, 8):
        ax.add_patch(Circle((y_vec_x + 0.65, sy), 0.25, facecolor=c_blue_primary, edgecolor='none', zorder=4))

    ax.text(sec1_cx, 29.5, 'Feature Matrix & Target Labels', fontsize=9.5, fontstyle='italic',
            color=c_text_muted, ha='center', va='center')

    # =========================================================================
    # 2. MI TRANSFORMATION & PRIOR NORMALIZATION
    # =========================================================================
    ax.annotate('', xy=(20.8, 55.0), xytext=(17.2, 55.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2, mutation_scale=14), zorder=5)

    sec2_cx = 26.5
    ax.text(sec2_cx, 89.5, 'Mutual Information\nEstimation', fontsize=12.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center')
    ax.text(sec2_cx, 82.5, r'$I(f_j; \mathbf{Y}) = \sum p(f_j, y) \log \frac{p(f_j, y)}{p(f_j)p(y)}$',
            fontsize=9.5, color=c_text_dark, ha='center', va='center')

    # Continuous MI Relevance Profile (Blue gradient)
    p_x_start = 22.0
    p_w = 9.0
    p_h = 28.0
    p_y = 46.0

    prof_y = np.linspace(p_y, p_y + p_h, 80)
    for idx, py_val in enumerate(prof_y):
        frac = (py_val - p_y) / p_h
        bar_len = p_w * (0.15 + 0.85 * (frac ** 1.6))
        col_r = int(239 - (239 - 29) * (frac ** 1.2))
        col_g = int(246 - (246 - 78) * (frac ** 1.2))
        col_b = int(255 - (255 - 216) * (frac ** 1.2))
        hex_col = f"#{col_r:02x}{col_g:02x}{col_b:02x}"
        ax.plot([p_x_start, p_x_start + bar_len], [py_val, py_val], color=hex_col, lw=2.4, solid_capstyle='round', zorder=3)

    ax.plot([p_x_start, p_x_start], [p_y, p_y + p_h], color=c_blue_primary, lw=1.5, zorder=4)
    
    ax.text(p_x_start + p_w + 0.6, p_y + p_h - 2.0, 'High MI', fontsize=9.2, fontweight='bold', color=c_blue_navy, va='center')
    ax.text(p_x_start + p_w * 0.6 + 0.6, p_y + p_h * 0.55, 'Medium MI', fontsize=9.0, color=c_blue_mid, va='center')
    ax.text(p_x_start + p_w * 0.25 + 0.6, p_y + 3.0, 'Low MI', fontsize=9.0, color=c_text_muted, va='center')

    # Down arrow from profile to normalization
    ax.annotate('', xy=(26.5, 42.0), xytext=(26.5, 45.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.6, mutation_scale=10), zorder=4)

    # Min-Max Normalization Box (Porcelain White)
    norm_bx = 20.0
    norm_by = 31.0
    norm_bw = 13.0
    norm_bh = 10.5
    draw_badge(norm_bx, norm_by, norm_bw, norm_bh, c_card_bg, c_blue_border, lw=1.2, r=0.4, zorder=3)
    ax.text(norm_bx + norm_bw/2, norm_by + 7.8, 'MI-Derived Prior Vector', fontsize=10.2, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=4)
    ax.text(norm_bx + norm_bw/2, norm_by + 3.8, r'$\widetilde{\mathbf{m}} = \frac{\mathbf{I} - I_{\min}}{I_{\max} - I_{\min}} \in [0, 1]^D$',
            fontsize=9.8, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=4)

    # =========================================================================
    # 3. CENTRAL: HYBRID POPULATION SEEDING (TWO-BRANCH FORK)
    # =========================================================================
    ax.annotate('', xy=(37.5, 68.5), xytext=(33.0, 38.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.16', mutation_scale=14), zorder=5)
    
    ax.annotate('', xy=(37.5, 42.0), xytext=(33.0, 35.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=2.2,
                                connectionstyle='arc3,rad=0.12', mutation_scale=14), zorder=5)

    # UPPER BRANCH: 50% MI-Guided Seeding (Porcelain White with Blue border)
    ub_x = 38.0
    ub_y = 59.0
    ub_w = 14.5
    ub_h = 19.0
    draw_badge(ub_x, ub_y, ub_w, ub_h, c_card_bg, c_blue_border, lw=1.3, r=0.5, zorder=2)
    
    ax.text(ub_x + ub_w/2, ub_y + 16.0, '50% MI-Guided Seeding', fontsize=11.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(ub_x + ub_w/2, ub_y + 12.2, r'$\mathbf{p}_i = \mathrm{clip}\left(\widetilde{\mathbf{m}} + \boldsymbol{\varepsilon}_i, \; 0, \; 1\right)$',
            fontsize=10.2, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=3)
    ax.text(ub_x + ub_w/2, ub_y + 8.8, r'$\boldsymbol{\varepsilon}_i \sim \mathcal{N}(\mathbf{0}, \, \sigma^2 \mathbf{I})$ (Stochastic Perturbation)',
            fontsize=8.8, color=c_text_muted, ha='center', va='center', zorder=3)

    bar_x_start = ub_x + 1.8
    bar_y_base = ub_y + 2.5
    mi_bar_heights = [3.8, 3.4, 1.2, 0.9, 1.6, 2.9, 3.7]
    for b_i, bh in enumerate(mi_bar_heights):
        bx = bar_x_start + b_i * 1.6
        bar_c = c_blue_primary if bh > 2.5 else c_blue_border
        ax.add_patch(patches.Rectangle((bx, bar_y_base), 1.0, bh, facecolor=bar_c, edgecolor='none', zorder=4))
    ax.text(ub_x + ub_w/2, ub_y + 0.8, r'Informative Bias: $p_{i,j} \propto \widetilde{m}_j$',
            fontsize=8.5, fontstyle='italic', color=c_blue_primary, ha='center', va='bottom', zorder=3)

    # LOWER BRANCH: 50% Uniform Random Seeding (Porcelain White with Slate border)
    lb_x = 38.0
    lb_y = 32.5
    lb_w = 14.5
    lb_h = 19.0
    draw_badge(lb_x, lb_y, lb_w, lb_h, c_card_bg, c_slate_border, lw=1.3, r=0.5, zorder=2)

    ax.text(lb_x + lb_w/2, lb_y + 16.0, '50% Uniform Random Seeding', fontsize=11.5, fontweight='bold',
            color=c_slate_dark, ha='center', va='center', zorder=3)
    ax.text(lb_x + lb_w/2, lb_y + 12.2, r'$\mathbf{p}_i \sim \mathcal{U}(0, \, 1)^D$',
            fontsize=10.5, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=3)
    ax.text(lb_x + lb_w/2, lb_y + 8.8, r'Full Exploration: $p_{i,j} \in [0, 1]$ stochastic',
            fontsize=9.0, color=c_text_muted, ha='center', va='center', zorder=3)

    np.random.seed(99)
    for b_i in range(7):
        bx = bar_x_start + b_i * 1.6
        bh = np.random.uniform(1.2, 3.6)
        ax.add_patch(patches.Rectangle((bx, lb_y + 2.5), 1.0, bh, facecolor=c_slate_mid, edgecolor='none', zorder=4))
    ax.text(lb_x + lb_w/2, lb_y + 0.8, r'Global Exploration: Maximum Diversity',
            fontsize=8.5, fontstyle='italic', color=c_slate_dark, ha='center', va='bottom', zorder=3)

    # =========================================================================
    # 4. MERGE INTO INITIAL PSO POPULATION
    # =========================================================================
    ax.annotate('', xy=(56.0, 59.0), xytext=(53.0, 68.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.12', mutation_scale=14), zorder=5)
    ax.annotate('', xy=(56.0, 51.0), xytext=(53.0, 42.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=2.2,
                                connectionstyle='arc3,rad=0.12', mutation_scale=14), zorder=5)

    pop_x = 56.5
    pop_y = 32.5
    pop_w = 14.5
    pop_h = 45.5
    draw_badge(pop_x, pop_y, pop_w, pop_h, c_card_bg, '#94A3B8', lw=1.4, r=0.6, zorder=2)

    # Header and Synergy subtitle
    ax.text(pop_x + pop_w/2, pop_y + 42.5, 'Initial PSO Population', fontsize=12.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(pop_x + pop_w/2, pop_y + 39.2, 'Knowledge Prior + Global Diversity', fontsize=9.2, fontweight='bold',
            color=c_blue_primary, ha='center', va='center', zorder=3)
    ax.text(pop_x + pop_w/2, pop_y + 36.5, r'$\mathcal{P} = \{\mathbf{p}_1, \dots, \mathbf{p}_N\}$',
            fontsize=9.5, color=c_text_muted, ha='center', va='center', zorder=3)

    # Top half: MI-guided particles
    ax.text(pop_x + pop_w/2, pop_y + 33.0, 'Subpopulation 1: MI-Guided', fontsize=9.2, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)
    np.random.seed(77)
    for row in range(3):
        for col in range(3):
            dot_x = pop_x + 3.0 + col * 4.2 + np.random.uniform(-0.5, 0.5)
            dot_y = pop_y + 23.5 + row * 2.6 + np.random.uniform(-0.3, 0.3)
            ax.add_patch(Circle((dot_x, dot_y), 0.45, facecolor=c_blue_primary, edgecolor='#FFFFFF', lw=0.9, zorder=4))
            ax.annotate('', xy=(dot_x + 0.8, dot_y + 0.4), xytext=(dot_x, dot_y),
                        arrowprops=dict(arrowstyle='->', color=c_blue_mid, lw=1.2, mutation_scale=8), zorder=3)

    ax.plot([pop_x + 1.5, pop_x + pop_w - 1.5], [pop_y + 21.0, pop_y + 21.0], color='#CBD5E1', lw=1.0, linestyle='--', zorder=3)

    # Bottom half: Uniform random particles
    ax.text(pop_x + pop_w/2, pop_y + 18.5, 'Subpopulation 2: Uniform Random', fontsize=9.2, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=3)
    np.random.seed(88)
    for row in range(3):
        for col in range(3):
            dot_x = pop_x + 2.5 + col * 4.6 + np.random.uniform(-0.6, 0.6)
            dot_y = pop_y + 9.5 + row * 2.6 + np.random.uniform(-0.3, 0.3)
            ax.add_patch(Circle((dot_x, dot_y), 0.45, facecolor=c_slate_mid, edgecolor='#FFFFFF', lw=0.9, zorder=4))
            ax.annotate('', xy=(dot_x + np.random.uniform(-0.7, 0.7), dot_y + np.random.uniform(-0.7, 0.7)), xytext=(dot_x, dot_y),
                        arrowprops=dict(arrowstyle='->', color=c_slate_dark, lw=1.2, mutation_scale=8), zorder=3)

    ax.text(pop_x + pop_w/2, pop_y + 3.2, 'Informative Bias + Exploration', fontsize=8.8, fontstyle='italic',
            color=c_text_muted, ha='center', va='center', zorder=4)

    # =========================================================================
    # 5. EVOLUTIONARY SEARCH & STAGNATION RE-INJECTION
    # =========================================================================
    ax.annotate('', xy=(74.5, 55.5), xytext=(71.5, 55.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_navy, lw=2.2, mutation_scale=14), zorder=5)

    sec5_cx = 85.5
    ax.text(sec5_cx, 89.5, 'Evolutionary Search Space\n& Convergence', fontsize=12.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center')

    # 2D Fitness Contour Landscape
    search_x = 74.0
    search_y = 32.5
    search_w = 23.0
    search_h = 45.5
    draw_badge(search_x, search_y, search_w, search_h, '#F8FAFC', '#CBD5E1', lw=1.2, r=0.6, zorder=2)

    # Centered contours
    c_center = (search_x + 13.5, search_y + 26.5)
    for r_idx, (rw, rh, c_alpha) in enumerate([(8.5, 5.8, 0.4), (6.0, 4.0, 0.6), (3.6, 2.4, 0.8), (1.6, 1.1, 1.0)]):
        ellipse = patches.Ellipse(c_center, rw*2, rh*2, angle=-10, facecolor='none',
                                  edgecolor='#93C5FD', lw=1.0, alpha=c_alpha, linestyle='-', zorder=3)
        ax.add_patch(ellipse)

    # Global Optimum Star in Deep Cobalt/Navy Blue
    ax.plot(c_center[0], c_center[1], marker='*', markersize=14, color=c_blue_primary, markeredgecolor=c_blue_navy, markeredgewidth=1.0, zorder=8)
    ax.text(c_center[0] + 1.2, c_center[1] + 1.2, r'$\mathbf{x}^\star\ \mathrm{Optimum}$', fontsize=9.5, fontweight='bold', color=c_blue_navy, zorder=8)

    # Particle trajectories converging smoothly (Cobalt Blue + Slate)
    traj_pts = [
        np.array([[search_x + 2.5, search_y + 36.0], [search_x + 6.5, search_y + 32.0], [c_center[0] - 1.2, c_center[1] + 0.8]]),
        np.array([[search_x + 3.0, search_y + 17.0], [search_x + 7.5, search_y + 21.0], [c_center[0] - 0.5, c_center[1] - 0.8]]),
        np.array([[search_x + 19.5, search_y + 12.0], [search_x + 16.0, search_y + 19.0], [c_center[0] + 0.8, c_center[1] - 0.4]])
    ]
    for idx, t_arr in enumerate(traj_pts):
        t_eval = np.linspace(0, 1, len(t_arr))
        t_dense = np.linspace(0, 1, 50)
        sx = make_interp_spline(t_eval, t_arr[:, 0], k=2)(t_dense)
        sy = make_interp_spline(t_eval, t_arr[:, 1], k=2)(t_dense)
        t_col = c_blue_primary if idx == 0 else (c_blue_mid if idx == 1 else c_slate_mid)
        ax.plot(sx, sy, color=t_col, lw=1.4, linestyle='-', alpha=0.85, zorder=4)
        ax.add_patch(Circle((sx[0], sy[0]), 0.4, facecolor=t_col, edgecolor='#FFFFFF', lw=0.8, zorder=5))

    # Stagnation Trap Node (Local Minima Basin - Slate & Subtle Ice Blue)
    stag_center = (search_x + 5.5, search_y + 9.5)
    ax.add_patch(patches.Ellipse(stag_center, 6.0, 3.8, facecolor='#F1F5F9', edgecolor=c_slate_dark, lw=1.2, linestyle=':', zorder=4))
    ax.add_patch(Circle(stag_center, 0.45, facecolor=c_slate_dark, edgecolor='#FFFFFF', lw=0.8, zorder=6))
    ax.text(stag_center[0], stag_center[1] + 2.8, r'Stagnation Detected' + '\n' + r'(Local Optimum Trap)', fontsize=8.8,
            fontweight='bold', color=c_slate_dark, ha='center', va='bottom', zorder=7)

    # =========================================================================
    # 6. ADAPTIVE MI RE-INJECTION (FEEDBACK LOOP) - Porcelain White with Blue
    # =========================================================================
    rein_x = 54.0
    rein_y = 15.5
    rein_w = 31.0
    rein_h = 7.5
    draw_badge(rein_x, rein_y, rein_w, rein_h, c_card_bg, c_blue_border, lw=1.2, r=0.4, zorder=8)
    ax.text(rein_x + rein_w/2, rein_y + 5.0, 'Adaptive MI Re-injection', fontsize=10.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=9)
    ax.text(rein_x + rein_w/2, rein_y + 2.2, r'Re-seed inferior particles: $\mathbf{p}_{\mathrm{inferior}} \leftarrow \mathrm{clip}(\widetilde{\mathbf{m}} + \boldsymbol{\varepsilon}_i, 0, 1)$',
            fontsize=8.8, color=c_text_dark, ha='center', va='center', zorder=9)

    # Leg 1: Stagnation Trap -> Re-injection Badge (Downward Arrow with high zorder)
    ax.annotate('', xy=(79.5, rein_y + rein_h), xytext=(stag_center[0], stag_center[1] - 2.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2, mutation_scale=15), zorder=10)
    ax.text(80.5, (stag_center[1] - 2.0 + rein_y + rein_h) / 2.0, 'Trigger', fontsize=8.5, fontweight='bold',
            color=c_blue_navy, ha='left', va='center', zorder=10)

    # Leg 2: Re-injection Badge top-left -> Bottom of Initial PSO Population box (Upward Curved Arrow)
    ax.annotate('', xy=(pop_x + pop_w/2, pop_y), xytext=(rein_x + 7.5, rein_y + rein_h),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.18', mutation_scale=15), zorder=10)
    ax.text(57.5, 27.5, 'Re-inject', fontsize=8.5, fontweight='bold',
            color=c_blue_navy, ha='right', va='center', zorder=10)

    # =========================================================================
    # BOTTOM CAUSAL CHAIN SUMMARY STATEMENT
    # =========================================================================
    sum_y = 5.0
    summary_items = [
        (8.5, 'Raw High-D Data', c_text_dark),
        (25.0, 'MI-Derived Prior', c_blue_navy),
        (46.0, 'Hybrid Population Seeding', c_blue_primary),
        (68.0, 'Knowledge-Biased Swarm', c_blue_navy),
        (88.5, 'Stagnation Resilience', c_blue_primary)
    ]
    for sx, stext, scol in summary_items:
        ax.text(sx, sum_y, stext, fontsize=10.5, fontweight='bold', color=scol, ha='center', va='center', zorder=4)

    flow_arrows = [(15.5, 18.5), (34.0, 37.0), (57.5, 60.5), (78.5, 81.5)]
    for ax_s, ax_e in flow_arrows:
        ax.annotate('', xy=(ax_e, sum_y), xytext=(ax_s, sum_y),
                    arrowprops=dict(arrowstyle='-|>', color=c_slate_mid, lw=1.4, mutation_scale=10), zorder=4)

    # Save Outputs
    out_dir = 'output/figures'
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F2_mi_initialization_journal.pdf')
    png_path = os.path.join(out_dir, 'F2_mi_initialization_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated Harmonized Figure 2 PDF and PNG successfully!')

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

    add_cell('h1', '&lt;b&gt;High-Dimensional Feature Space&lt;/b&gt;&lt;br&gt;$$X \\in \\mathbb{R}^{N \\times D}$$', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 40, 20, 200, 40)
    add_cell('h2', '&lt;b&gt;&lt;font color=\"#1D4ED8\"&gt;Mutual Information Prior&lt;/font&gt;&lt;/b&gt;&lt;br&gt;$$I(f_j; Y)$$', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 280, 20, 200, 40)
    add_cell('h3', '&lt;b&gt;&lt;font color=\"#1D4ED8\"&gt;50% MI-Guided&lt;/font&gt; + &lt;font color=\"#334155\"&gt;50% Random&lt;/font&gt;&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 520, 20, 240, 40)
    add_cell('h4', '&lt;b&gt;Initial PSO Population&lt;/b&gt;&lt;br&gt;Knowledge + Diversity', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 790, 20, 200, 40)
    add_cell('h5', '&lt;b&gt;Evolutionary Search &amp; Re-injection&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;', 1020, 20, 240, 40)

    out_file = 'output/figures/F2_mi_initialization_journal.drawio'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated Harmonized Figure 2 Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure2()
    generate_drawio()
