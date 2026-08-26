"""Publication-grade Figure 3 for Knowledge-guided Elite Refinement (KER) Strategy in KDS-EL.
Strictly adheres to Top-Tier Journal (Elsevier SWEVO/KBS/INS, IEEE TEVC) design standards:
- 3 Clear Modular Stage Containers (Swarm Evaluation, Knowledge Accumulation, 1-to-1 Elite Refinement).
- Clean theoretical notations without empirical hyperparameter clutter or redundant parentheses.
- Pure academic palette: Cobalt Blue + Slate Neutral.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle

def create_figure3():
    # Times New Roman & STIX math typography (Unified with Figure 1, 2, 4)
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
    c_blue_cell = '#EFF6FF'       # Blue 50
    c_blue_cell_hi = '#DBEAFE'    # Blue 100
    c_blue_border = '#93C5FD'     # Blue 300
    
    # Structural Neutrals
    c_border_neutral = '#CBD5E1'  # Slate 300
    c_slate_dark = '#334155'      # Slate 700

    def draw_badge(x, y, w, h, bg, border, lw=1.1, r=0.4, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.03,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 0. MAIN STRUCTURAL BOUNDING CONTAINERS (方框/面板结构)
    # =========================================================================
    # Container 1: Swarm Evaluation
    draw_badge(2.0, 13.0, 29.5, 84.5, c_panel_bg, c_border_neutral, lw=1.2, r=0.6, zorder=1)
    
    # Container 2: Knowledge Accumulation (Matrix W)
    draw_badge(33.0, 13.0, 32.5, 84.5, c_panel_bg, c_border_neutral, lw=1.2, r=0.6, zorder=1)

    # Container 3: Knowledge-Guided Elite Refinement (KER)
    draw_badge(67.0, 13.0, 31.0, 84.5, c_panel_bg, c_border_neutral, lw=1.2, r=0.6, zorder=1)

    # Bottom Spanning Closed-Loop Learning Container
    draw_badge(2.0, 2.0, 96.0, 9.0, c_panel_bg, c_border_neutral, lw=1.2, r=0.5, zorder=1)

    # =========================================================================
    # 1. SWARM EVALUATION & POPULATION MATRIX
    # =========================================================================
    s1_cx = 16.7
    ax.text(s1_cx, 93.0, 'Swarm Evaluation', fontsize=13.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)

    pop_data = [
        (r'$\mathbf{p}_1$', [1, 0, 1, 0, 1, 0, '...', 1, 0, 0]),
        (r'$\mathbf{p}_2$', [0, 1, 0, 1, 1, 0, '...', 0, 1, 1]),
        (r'$\mathbf{p}_3$', [1, 1, 0, 0, 1, 0, '...', 1, 0, 0]),
        ('dots', None),
        (r'$\mathbf{p}_N$', [0, 1, 1, 0, 0, 1, '...', 1, 1, 0])
    ]

    cell_w, cell_h = 2.1, 2.9
    y_start = 82.5
    y_spacing = 6.4
    lx_start = 6.2

    # Feature headers
    feat_labels = [r'$f_1$', r'$f_2$', r'$f_3$', r'$\dots$', r'$f_D$']
    feat_x = [lx_start + cell_w*0.5, lx_start + cell_w*1.5, lx_start + cell_w*2.5, lx_start + cell_w*6 + 0.8, lx_start + cell_w*7 + 1.6 + cell_w*1.0]
    for lbl, fx in zip(feat_labels, feat_x):
        ax.text(fx, 87.5, lbl, fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)

    for row_idx, (p_name, bits) in enumerate(pop_data):
        curr_y = y_start - row_idx * y_spacing
        if p_name == 'dots':
            ax.text(s1_cx, curr_y + 1.0, r'$\vdots$', fontsize=14, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
            continue
        
        ax.text(3.8, curr_y + cell_h/2, p_name, fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)

        x_c = lx_start
        for b in bits:
            if b == '...':
                ax.text(x_c + 0.9, curr_y + cell_h/2, r'$\dots$', fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
                x_c += 1.8
            else:
                bg = c_blue_cell if b == 1 else '#FFFFFF'
                draw_badge(x_c, curr_y, cell_w, cell_h, bg, c_border_neutral, lw=0.8, r=0.2, zorder=3)
                ax.text(x_c + cell_w/2, curr_y + cell_h/2, str(b), fontsize=10.2, ha='center', va='center', color=c_text_dark, zorder=4)
                x_c += cell_w

    # Down arrow to Fitness Evaluation
    ax.annotate('', xy=(s1_cx, 47.0), xytext=(s1_cx, 52.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0, mutation_scale=12), zorder=5)

    # Fitness Evaluation Box
    eval_x = 4.5
    eval_y = 16.5
    eval_w = 24.5
    eval_h = 28.0
    draw_badge(eval_x, eval_y, eval_w, eval_h, c_card_bg, c_blue_border, lw=1.3, r=0.5, zorder=3)
    
    # 3 Evaluation metric bars
    bar_base_y = eval_y + 8.5
    ax.add_patch(patches.Rectangle((eval_x + 3.5, bar_base_y), 4.2, 9.5, facecolor='#3B82F6', edgecolor='none', zorder=4))
    ax.add_patch(patches.Rectangle((eval_x + 9.8, bar_base_y), 4.2, 13.5, facecolor=c_blue_primary, edgecolor='none', zorder=4))
    ax.add_patch(patches.Rectangle((eval_x + 16.1, bar_base_y), 4.2, 7.0, facecolor='#60A5FA', edgecolor='none', zorder=4))
    
    # Baseline axis
    ax.plot([eval_x + 2.0, eval_x + eval_w - 2.0], [bar_base_y, bar_base_y], color=c_slate_dark, lw=1.1, zorder=4)

    ax.text(eval_x + eval_w/2, eval_y + 5.0, 'Fitness Evaluation', fontsize=12.2, fontweight='bold', ha='center', va='center', color=c_blue_navy, zorder=4)
    ax.text(eval_x + eval_w/2, eval_y + 2.0, r'$f(\mathbf{x}, \mathbf{w}) = w_{\mathrm{acc}} \cdot \mathrm{Error}(\mathbf{x}) + w_{\mathrm{feat}} \cdot \frac{\|\mathbf{x}\|_0}{D}$',
            fontsize=9.2, color=c_text_muted, ha='center', va='center', zorder=4)

    # =========================================================================
    # 2. KNOWLEDGE ACCUMULATION & FEATURE-IMPORTANCE MATRIX W
    # =========================================================================
    s2_cx = 49.2
    ax.text(s2_cx, 93.0, 'Knowledge Accumulation', fontsize=13.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)

    # Fitness Feedback curved arrow (Top Left into Stage 2)
    ax.annotate('', xy=(38.0, 95.8), xytext=(22.0, 95.8),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.18', mutation_scale=13), zorder=5)
    ax.text(30.0, 95.5, 'Fitness Feedback', fontsize=10.5, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=6)

    # Multi-Generation Experience Title
    ax.text(s2_cx, 87.5, 'Historical Multi-Generation Experience', fontsize=11.0, fontstyle='italic', color=c_text_muted, ha='center', va='center', zorder=3)

    # History generation cards with correctly sequenced subscripts: P(t-2), P(t-1), P(t)
    cards = [
        (r'$\mathcal{P}^{(t-2)}$', 36.0, '#60A5FA', [(-0.3, 0.4), (0.2, 0.6), (0.0, 0.0), (-0.2, -0.4), (0.3, -0.3)]),
        (r'$\mathcal{P}^{(t-1)}$', 46.0, '#3B82F6', [(0.1, 0.5), (-0.2, 0.3), (0.0, 0.0), (0.2, -0.4), (-0.1, -0.5)]),
        (r'$\mathcal{P}^{(t)}$',   56.0, c_blue_primary, [(0.2, 0.4), (-0.3, 0.5), (0.0, 0.1), (0.1, -0.3), (-0.2, -0.4)])
    ]

    for lbl, cx, col, pts in cards:
        draw_badge(cx, 73.0, 6.5, 10.5, c_card_bg, c_border_neutral, lw=1.0, r=0.4, zorder=3)
        for px, py in pts:
            ax.add_patch(Circle((cx + 3.25 + px*1.5, 79.5 + py*1.6), 0.38, facecolor=col, edgecolor='none', zorder=4))
        ax.plot([cx + 3.25, cx + 3.25], [76.5, 81.8], color=col, lw=1.0, alpha=0.6, zorder=3)
        ax.text(cx + 3.25, 74.8, lbl, fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=4)

    # Three arrows from cards down to Matrix W
    for cx in [39.25, 49.25, 59.25]:
        ax.annotate('', xy=(cx, 66.0), xytext=(cx, 72.0),
                    arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.6, mutation_scale=10), zorder=5)

    # Cumulative Feature-Importance Matrix W
    ax.text(s2_cx, 63.0, r'Cumulative Feature-Importance Matrix $\mathbf{W}$', fontsize=12.2, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)

    w_strip_labels = [r'$f_1$', r'$f_2$', r'$f_3$', r'$\dots$', r'$f_{D-2}$', r'$f_{D-1}$', r'$f_D$']
    w_strip_vals = [0.92, 0.74, 0.41, None, 0.88, 0.22, 0.65]
    
    w_box_w = 3.6
    w_box_h = 4.2
    w_gap = 0.6
    total_w_width = len(w_strip_labels) * w_box_w + (len(w_strip_labels) - 1) * w_gap
    w_x_start = s2_cx - total_w_width / 2.0
    w_y_base = 51.0

    for si, (s_lbl, s_v) in enumerate(zip(w_strip_labels, w_strip_vals)):
        sx = w_x_start + si * (w_box_w + w_gap)
        if s_v is not None:
            scol = plt.cm.Blues(0.25 + 0.70 * s_v)
            st_color = '#FFFFFF' if s_v > 0.6 else '#0F172A'
            bd_color = '#94A3B8' if s_v <= 0.6 else c_blue_primary
            
            draw_badge(sx, w_y_base, w_box_w, w_box_h, scol, bd_color, lw=1.0, r=0.3, zorder=3)
            ax.text(sx + w_box_w/2, w_y_base + w_box_h/2, s_lbl, fontsize=10.5, fontweight='bold',
                    ha='center', va='center', color=st_color, zorder=4)
        else:
            # Ellipsis box
            draw_badge(sx, w_y_base, w_box_w, w_box_h, '#F1F5F9', '#CBD5E1', lw=0.9, r=0.3, zorder=3)
            ax.text(sx + w_box_w/2, w_y_base + w_box_h/2, r'$\dots$', fontsize=11.5, fontweight='bold',
                    ha='center', va='center', color='#475569', zorder=4)

    # Clean semantic legend below Matrix W (WITHOUT parentheses)
    leg_y = 45.0
    draw_badge(34.5, leg_y, 2.0, 1.8, plt.cm.Blues(0.85), c_blue_primary, r=0.1, zorder=3)
    ax.text(37.2, leg_y + 0.9, r'High $W_j$: Key Features', fontsize=9.5, fontweight='bold', ha='left', va='center', color=c_blue_navy, zorder=3)
    
    draw_badge(49.5, leg_y, 2.0, 1.8, plt.cm.Blues(0.35), '#94A3B8', r=0.1, zorder=3)
    ax.text(52.2, leg_y + 0.9, r'Low $W_j$: Redundant Features', fontsize=9.5, fontweight='bold', ha='left', va='center', color=c_text_muted, zorder=3)

    # Redesigned Dynamic Memory Decay Box (Decay Curve & Mathematical Retention Visualization)
    decay_bx = 35.0
    decay_by = 16.5
    decay_bw = 28.5
    decay_bh = 24.5
    draw_badge(decay_bx, decay_by, decay_bw, decay_bh, c_card_bg, c_border_neutral, lw=1.2, r=0.5, zorder=3)

    ax.text(s2_cx, decay_by + 21.5, 'Dynamic Memory Decay', fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_blue_navy, zorder=4)
    ax.text(s2_cx, decay_by + 18.0, r'$\mathbf{W}^{(t)} = \gamma \mathbf{W}^{(t-1)} + \Delta \mathbf{W}^{(t)}$', fontsize=10.5, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)

    # Mini Decay Curve Plot
    plot_x0 = decay_bx + 4.5
    plot_y0 = decay_by + 4.5
    plot_w = 20.0
    plot_h = 10.5

    # Plot axes
    ax.plot([plot_x0, plot_x0 + plot_w], [plot_y0, plot_y0], color='#64748B', lw=1.1, zorder=4)
    ax.plot([plot_x0, plot_x0], [plot_y0, plot_y0 + plot_h], color='#64748B', lw=1.1, zorder=4)

    # Exponential decay curve points
    cx_vals = np.linspace(0, 1, 40)
    cy_vals = np.exp(-2.5 * cx_vals)  # Exponential decay e^(-2.5 x)
    px_curve = plot_x0 + cx_vals * (plot_w - 1.0)
    py_curve = plot_y0 + cy_vals * (plot_h - 1.5)

    # Fill under curve
    poly_pts = [[plot_x0, plot_y0]] + list(zip(px_curve, py_curve)) + [[px_curve[-1], plot_y0]]
    ax.add_patch(patches.Polygon(poly_pts, facecolor='#EFF6FF', edgecolor='none', alpha=0.9, zorder=3))
    ax.plot(px_curve, py_curve, color=c_blue_primary, lw=1.8, zorder=5)

    # Points on curve: t, t-1, t-2
    for t_idx, (t_frac, t_name) in enumerate([(0.0, r'$t$'), (0.35, r'$t-1$'), (0.75, r'$t-2$')]):
        t_px = plot_x0 + t_frac * (plot_w - 1.0)
        t_py = plot_y0 + np.exp(-2.5 * t_frac) * (plot_h - 1.5)
        ax.add_patch(Circle((t_px, t_py), 0.45, facecolor=c_blue_primary if t_idx == 0 else '#60A5FA', edgecolor='#FFFFFF', lw=0.8, zorder=6))
        ax.text(t_px, plot_y0 - 1.8, t_name, fontsize=8.8, fontweight='bold', ha='center', va='top', color=c_text_dark, zorder=6)

    ax.text(plot_x0 + plot_w - 0.5, plot_y0 + 3.0, r'$\propto \gamma^\tau$', fontsize=9.5, fontstyle='italic', color=c_blue_navy, ha='right', va='bottom', zorder=5)
    ax.text(plot_x0 + 0.5, plot_y0 + plot_h + 0.8, 'Weight Retention', fontsize=8.2, fontstyle='italic', color=c_text_muted, ha='left', va='bottom', zorder=4)

    # =========================================================================
    # 3. KNOWLEDGE-GUIDED ELITE REFINEMENT (KER)
    # =========================================================================
    s3_cx = 82.5
    ax.text(s3_cx, 93.0, 'Knowledge-Guided Elite Refinement', fontsize=13.5, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)

    # Top curved arrow from Stage 2 into Stage 3
    ax.annotate('', xy=(72.0, 95.8), xytext=(58.0, 95.8),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.18', mutation_scale=13), zorder=5)

    # Synchronized 10-element arrays for exact vertical consistency
    # Structure: 7 individual bits + '...' + 2 tail bits (Total = 10 columns)
    bits_eb = [0, 1, 1, 0, 1, 0, 1, '...', 0, 1]
    bits_kf = [1, 1, 1, 0, 0, 0, 1, '...', 0, 1]  # Bit 0 flipped 0->1, Bit 4 flipped 1->0
    bits_ea = [1, 1, 1, 0, 0, 0, 1, '...', 0, 1]

    bx_start = 69.5
    bx_w = 2.4
    bx_h = 2.9

    # Array 1: Elite Solution (Before Refinement)
    ax.text(s3_cx, 87.5, r'Elite Solution $\mathbf{x}_e$ (Before Refinement)', fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
    
    for idx, b in enumerate(bits_eb):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + bx_w/2, 82.6, r'$\dots$', fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
        else:
            draw_badge(cur_bx, 81.2, bx_w, bx_h, '#FFFFFF', c_border_neutral, lw=0.9, r=0.2, zorder=3)
            ax.text(cur_bx + bx_w/2, 82.6, str(b), fontsize=10.2, ha='center', va='center', color=c_text_dark, zorder=4)

    # Highlight markers on target bit positions (Position 0 and Position 4)
    draw_badge(bx_start - 0.1, 81.1, bx_w + 0.2, bx_h + 0.2, 'none', c_blue_primary, lw=1.6, r=0.25, zorder=5)
    draw_badge(bx_start + 4*bx_w - 0.1, 81.1, bx_w + 0.2, bx_h + 0.2, 'none', c_slate_dark, lw=1.6, r=0.25, zorder=5)

    # Down arrow
    ax.annotate('', xy=(s3_cx, 77.2), xytext=(s3_cx, 80.2),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=10), zorder=5)

    # Array 2: Directional Mutation / Flip
    ax.text(s3_cx, 75.5, 'Knowledge-Guided Directional Flip', fontsize=11.0, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    for idx, b in enumerate(bits_kf):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + bx_w/2, 71.0, r'$\dots$', fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
        else:
            bg = c_blue_cell_hi if idx == 0 else ('#F1F5F9' if idx == 4 else '#FFFFFF')
            bd = c_blue_primary if idx == 0 else (c_slate_dark if idx == 4 else c_border_neutral)
            draw_badge(cur_bx, 69.6, bx_w, bx_h, bg, bd, lw=1.3 if idx in [0, 4] else 0.9, r=0.2, zorder=3)
            ax.text(cur_bx + bx_w/2, 71.0, str(b), fontsize=10.2, fontweight='bold' if idx in [0, 4] else 'normal',
                    ha='center', va='center', color=c_blue_navy if idx == 0 else c_text_dark, zorder=4)

    # Flip indicators below bits
    x_cell0 = bx_start + 0.5 * bx_w
    ax.annotate('', xy=(x_cell0 + 0.9, 67.8), xytext=(x_cell0 - 0.9, 67.8),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.4, connectionstyle='arc3,rad=-0.45', mutation_scale=9), zorder=4)
    ax.text(x_cell0, 65.5, r'$0 \to 1$', fontsize=9.8, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)

    x_cell4 = bx_start + 4.5 * bx_w
    ax.annotate('', xy=(x_cell4 + 0.9, 67.8), xytext=(x_cell4 - 0.9, 67.8),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.4, connectionstyle='arc3,rad=-0.45', mutation_scale=9), zorder=4)
    ax.text(x_cell4, 65.5, r'$1 \to 0$', fontsize=9.8, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=4)

    # Guidance arrow from Matrix W right edge to KER
    ax.annotate('', xy=(69.0, 71.0), xytext=(w_x_start + total_w_width + 0.6, 53.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.16', mutation_scale=13), zorder=5)

    # Down arrow to Fitness Re-evaluation
    ax.annotate('', xy=(s3_cx, 62.0), xytext=(s3_cx, 65.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=10), zorder=5)

    # Fitness Re-evaluation & In-Place Selection Header (Precisely Centered on s3_cx)
    ax.text(s3_cx, 59.5, 'Fitness Re-evaluation', fontsize=11.5, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    # Down arrow to Decision Diamond
    ax.annotate('', xy=(s3_cx, 54.5), xytext=(s3_cx, 57.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=10), zorder=5)

    # Decision Diamond (In-Place Selection)
    diamond = patches.Polygon([[s3_cx, 54.0], [s3_cx + 5.8, 51.0], [s3_cx, 48.0], [s3_cx - 5.8, 51.0]],
                              facecolor=c_card_bg, edgecolor=c_blue_navy, linewidth=1.4, zorder=3)
    ax.add_patch(diamond)
    ax.text(s3_cx, 51.0, 'Improved?', fontsize=10.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=4)

    # Yes / No Branch Arrows
    # Yes -> Left Down (Cobalt Blue)
    ax.annotate('', xy=(s3_cx - 7.5, 46.5), xytext=(s3_cx - 5.8, 51.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.8, mutation_scale=10), zorder=5)
    ax.text(s3_cx - 8.2, 51.5, 'Yes', fontsize=10.0, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)
    ax.text(s3_cx - 8.2, 44.5, 'Accept Refined', fontsize=9.5, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)

    # Arrow from Accept down to Elite (after)
    ax.annotate('', xy=(s3_cx - 2.5, 37.0), xytext=(s3_cx - 8.2, 41.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.5, connectionstyle='arc3,rad=-0.12', mutation_scale=9), zorder=5)

    # No -> Right Down (Slate Muted)
    ax.annotate('', xy=(s3_cx + 7.5, 46.5), xytext=(s3_cx + 5.8, 51.0),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.8, mutation_scale=10), zorder=5)
    ax.text(s3_cx + 8.2, 51.5, 'No', fontsize=10.0, fontweight='bold', color=c_text_light, ha='center', va='center', zorder=4)
    ax.text(s3_cx + 8.2, 44.5, 'Retain Original', fontsize=9.5, fontweight='bold', color=c_text_light, ha='center', va='center', zorder=4)

    # Arrow from Retain down to Elite (after)
    ax.annotate('', xy=(s3_cx + 2.5, 37.0), xytext=(s3_cx + 8.2, 41.5),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.5, connectionstyle='arc3,rad=0.12', mutation_scale=9), zorder=5)

    # Array 3: Elite Solution (After Selection)
    ax.text(s3_cx, 36.5, r'Elite Solution $\mathbf{x}_e^\star$ (After In-Place Selection)', fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)

    for idx, b in enumerate(bits_ea):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + bx_w/2, 31.0, r'$\dots$', fontsize=11.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
        else:
            bg = c_blue_cell_hi if idx == 0 else ('#F8FAFC' if idx == 4 else '#FFFFFF')
            bd = c_blue_primary if idx == 0 else (c_slate_dark if idx == 4 else c_border_neutral)
            draw_badge(cur_bx, 29.6, bx_w, bx_h, bg, bd, lw=1.3 if idx in [0, 4] else 0.9, r=0.2, zorder=3)
            ax.text(cur_bx + bx_w/2, 31.0, str(b), fontsize=10.2, fontweight='bold' if idx in [0, 4] else 'normal',
                    ha='center', va='center', color=c_blue_navy if idx == 0 else c_text_dark, zorder=4)

    # =========================================================================
    # 4. BOTTOM SPANNING CLOSED-LOOP LEARNING CHANNEL
    # =========================================================================
    ax.annotate('', xy=(16.7, 11.0), xytext=(s3_cx, 11.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.14', mutation_scale=16), zorder=6)

    ax.text(50.0, 5.5, 'Closed-Loop Evolutionary Knowledge Feedback Channel',
            fontsize=12.0, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=4)

    # Save Outputs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F3_ker_strategy_journal.pdf')
    png_path = os.path.join(out_dir, 'F3_ker_strategy_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated Clean Publication-Grade Figure 3 PDF and PNG successfully!')

def generate_drawio():
    import xml.etree.ElementTree as ET
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f3-ker-flow', name='Figure 3: KER Strategy')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1422', dy='798', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1400', pageHeight='900', math='1', shadow='0')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def add_cell(cid, value, style, x, y, w, h, parent='1'):
        cell = ET.SubElement(root, 'mxCell', id=str(cid), value=str(value), style=style, parent=parent, vertex='1')
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})
        return cell

    # Outer containers
    add_cell('f3_c1', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 20, 20, 420, 760)
    add_cell('f3_c2', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 460, 20, 460, 760)
    add_cell('f3_c3', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 940, 20, 440, 760)
    add_cell('f3_bot', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 20, 800, 1360, 90)

    add_cell('w_title', '&lt;b&gt;Cumulative Feature-Importance Matrix $$W$$&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=14;fontColor=#0F172A;', 480, 290, 280, 30)
    add_cell('w_headers', '$$f_1 \\quad f_2 \\quad f_3 \\quad \\dots \\quad f_{D-2} \\quad f_{D-1} \\quad f_D$$', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;', 480, 320, 280, 25)

    out_file = 'output/figures/F3_ker_strategy_journal.drawio'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated Clean Figure 3 Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure3()
    generate_drawio()
