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
    ax.text(s1_cx, 93.0, 'Swarm Evaluation', fontsize=15.0, fontweight='bold',
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
        ax.text(fx, 87.5, lbl, fontsize=12.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)

    for row_idx, (p_name, bits) in enumerate(pop_data):
        curr_y = y_start - row_idx * y_spacing
        if p_name == 'dots':
            ax.text(s1_cx, curr_y + 1.0, r'$\vdots$', fontsize=15.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
            continue
        
        ax.text(3.8, curr_y + cell_h/2, p_name, fontsize=12.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)

        x_c = lx_start
        for b in bits:
            if b == '...':
                ax.text(x_c + 0.9, curr_y + cell_h/2, r'$\dots$', fontsize=12.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
                x_c += 1.8
            else:
                bg = c_blue_cell if b == 1 else '#FFFFFF'
                draw_badge(x_c, curr_y, cell_w, cell_h, bg, c_border_neutral, lw=0.8, r=0.2, zorder=3)
                ax.text(x_c + cell_w/2, curr_y + cell_h/2, str(b), fontsize=11.5, ha='center', va='center', color=c_text_dark, zorder=4)
                x_c += cell_w

    # Down arrow to Fitness Evaluation (Exact touchpoint at Fitness Evaluation top edge y=44.5)
    ax.annotate('', xy=(s1_cx, 44.5), xytext=(s1_cx, 52.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0, mutation_scale=12), zorder=5)

    # Fitness Evaluation Box
    eval_x = 4.5
    eval_y = 16.5
    eval_w = 24.5
    eval_h = 28.0
    draw_badge(eval_x, eval_y, eval_w, eval_h, c_card_bg, c_blue_border, lw=1.3, r=0.5, zorder=3)
    
    # 3 Evaluation metric bars
    bar_base_y = eval_y + 8.0
    ax.add_patch(patches.Rectangle((eval_x + 3.5, bar_base_y), 4.2, 10.0, facecolor='#3B82F6', edgecolor='none', zorder=4))
    ax.add_patch(patches.Rectangle((eval_x + 9.8, bar_base_y), 4.2, 14.0, facecolor=c_blue_primary, edgecolor='none', zorder=4))
    ax.add_patch(patches.Rectangle((eval_x + 16.1, bar_base_y), 4.2, 7.5, facecolor='#60A5FA', edgecolor='none', zorder=4))
    
    # Baseline axis
    ax.plot([eval_x + 2.0, eval_x + eval_w - 2.0], [bar_base_y, bar_base_y], color=c_slate_dark, lw=1.1, zorder=4)

    # Title cleanly centered in lower half
    ax.text(eval_x + eval_w/2, eval_y + 4.0, 'Fitness Evaluation', fontsize=14.0, fontweight='bold', ha='center', va='center', color=c_blue_navy, zorder=4)

    # =========================================================================
    # 2. KNOWLEDGE ACCUMULATION & FEATURE-IMPORTANCE MATRIX W
    # =========================================================================
    s2_cx = 49.2
    ax.text(s2_cx, 93.0, 'Knowledge Accumulation', fontsize=15.0, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)

    # Fitness Feedback curved arrow (Top Left into Stage 2)
    ax.annotate('', xy=(38.0, 95.8), xytext=(22.0, 95.8),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.18', mutation_scale=13), zorder=5)
    ax.text(30.0, 95.5, 'Fitness Feedback', fontsize=12.0, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=6)

    # History generation cards with correctly sequenced subscripts: P(t-2), P(t-1), P(t)
    cards = [
        (r'$\mathcal{P}^{(t-2)}$', 36.0, '#60A5FA', [(-0.3, 0.4), (0.2, 0.6), (0.0, 0.0), (-0.2, -0.4), (0.3, -0.3)]),
        (r'$\mathcal{P}^{(t-1)}$', 46.0, '#3B82F6', [(0.1, 0.5), (-0.2, 0.3), (0.0, 0.0), (0.2, -0.4), (-0.1, -0.5)]),
        (r'$\mathcal{P}^{(t)}$',   56.0, c_blue_primary, [(0.2, 0.4), (-0.3, 0.5), (0.0, 0.1), (0.1, -0.3), (-0.2, -0.4)])
    ]

    card_y = 75.5
    card_h = 10.5
    for lbl, cx, col, pts in cards:
        draw_badge(cx, card_y, 6.5, card_h, c_card_bg, c_border_neutral, lw=1.0, r=0.4, zorder=3)
        for px, py in pts:
            ax.add_patch(Circle((cx + 3.25 + px*1.5, card_y + 6.5 + py*1.6), 0.38, facecolor=col, edgecolor='none', zorder=4))
        ax.plot([cx + 3.25, cx + 3.25], [card_y + 3.5, card_y + 8.8], color=col, lw=1.0, alpha=0.6, zorder=3)
        ax.text(cx + 3.25, card_y + 1.8, lbl, fontsize=12.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=4)

    # Three arrows from cards down to Matrix W
    for cx in [39.25, 49.25, 59.25]:
        ax.annotate('', xy=(cx, 66.0), xytext=(cx, card_y - 1.0),
                    arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.6, mutation_scale=10), zorder=5)

    # Cumulative Feature-Importance Matrix W
    ax.text(s2_cx, 63.0, r'Cumulative Feature-Importance Matrix $\mathbf{W}$', fontsize=13.5, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)

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
            ax.text(sx + w_box_w/2, w_y_base + w_box_h/2, s_lbl, fontsize=12.0, fontweight='bold',
                    ha='center', va='center', color=st_color, zorder=4)
        else:
            # Ellipsis box
            draw_badge(sx, w_y_base, w_box_w, w_box_h, '#F1F5F9', '#CBD5E1', lw=0.9, r=0.3, zorder=3)
            ax.text(sx + w_box_w/2, w_y_base + w_box_h/2, r'$\dots$', fontsize=13.0, fontweight='bold',
                    ha='center', va='center', color='#475569', zorder=4)

    # Clean semantic legend below Matrix W
    leg_y = 45.0
    draw_badge(34.0, leg_y, 2.2, 2.0, plt.cm.Blues(0.85), c_blue_primary, r=0.1, zorder=3)
    ax.text(37.0, leg_y + 1.0, r'High $W_j$: Key Features', fontsize=11.0, fontweight='bold', ha='left', va='center', color=c_blue_navy, zorder=3)
    
    draw_badge(49.8, leg_y, 2.2, 2.0, plt.cm.Blues(0.35), '#94A3B8', r=0.1, zorder=3)
    ax.text(52.8, leg_y + 1.0, r'Low $W_j$: Redundant Features', fontsize=11.0, fontweight='bold', ha='left', va='center', color=c_text_muted, zorder=3)

    # Redesigned Dynamic Memory Decay Box (Decay Curve & Retention Visualization)
    decay_bx = 35.0
    decay_by = 16.5
    decay_bw = 28.5
    decay_bh = 24.5
    draw_badge(decay_bx, decay_by, decay_bw, decay_bh, c_card_bg, c_border_neutral, lw=1.2, r=0.5, zorder=3)

    # Clean centered title without formula clutter
    ax.text(s2_cx, decay_by + 20.8, 'Dynamic Memory Decay', fontsize=13.5, fontweight='bold', ha='center', va='center', color=c_blue_navy, zorder=4)

    # Mini Decay Curve Plot (Centered and spacious)
    plot_x0 = decay_bx + 4.5
    plot_y0 = decay_by + 4.8
    plot_w = 20.0
    plot_h = 12.0

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
        ax.text(t_px, plot_y0 - 1.8, t_name, fontsize=10.5, fontweight='bold', ha='center', va='top', color=c_text_dark, zorder=6)

    ax.text(plot_x0 + plot_w - 0.5, plot_y0 + 3.5, r'$\propto \gamma^\tau$', fontsize=11.5, fontstyle='italic', color=c_blue_navy, ha='right', va='bottom', zorder=5)

    # =========================================================================
    # 3. KNOWLEDGE-GUIDED ELITE REFINEMENT (KER) - EXPANDED & BALANCED LAYOUT
    # =========================================================================
    s3_cx = 82.5
    ax.text(s3_cx, 93.0, 'Knowledge-Guided Elite Refinement', fontsize=15.0, fontweight='bold',
            color=c_blue_navy, ha='center', va='center', zorder=3)

    # Synchronized 10-element arrays for exact vertical consistency
    # Structure: 7 individual bits + '...' + 2 tail bits (Total = 10 columns)
    bits_eb = [0, 1, 1, 0, 1, 0, 1, '...', 0, 1]
    bits_kf = [1, 1, 1, 0, 0, 0, 1, '...', 0, 1]  # Bit 0 flipped 0->1, Bit 4 flipped 1->0
    bits_ea = [1, 1, 1, 0, 0, 0, 1, '...', 0, 1]

    bx_w = 2.5
    bx_h = 3.3
    bx_start = s3_cx - (len(bits_eb) * bx_w) / 2.0  # Exactly centered at s3_cx

    # Array 1: Elite Solution (Before Refinement)
    ax.text(s3_cx, 87.5, r'Elite Solution $\mathbf{x}_e$ (Before Refinement)', fontsize=13.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
    
    for idx, b in enumerate(bits_eb):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + bx_w/2, 82.1, r'$\dots$', fontsize=13.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
        else:
            draw_badge(cur_bx, 80.5, bx_w, bx_h, '#FFFFFF', c_border_neutral, lw=0.9, r=0.25, zorder=3)
            ax.text(cur_bx + bx_w/2, 82.1, str(b), fontsize=12.0, ha='center', va='center', color=c_text_dark, zorder=4)

    # Highlight markers on target bit positions (Position 0 and Position 4)
    draw_badge(bx_start - 0.1, 80.4, bx_w + 0.2, bx_h + 0.2, 'none', c_blue_primary, lw=1.6, r=0.3, zorder=5)
    draw_badge(bx_start + 4*bx_w - 0.1, 80.4, bx_w + 0.2, bx_h + 0.2, 'none', c_slate_dark, lw=1.6, r=0.3, zorder=5)

    # Down arrow 1
    ax.annotate('', xy=(s3_cx, 75.5), xytext=(s3_cx, 79.5),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=11), zorder=5)

    # Array 2: Directional Mutation / Flip
    ax.text(s3_cx, 73.5, 'Knowledge-Guided Directional Flip', fontsize=13.0, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    for idx, b in enumerate(bits_kf):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + bx_w/2, 68.1, r'$\dots$', fontsize=13.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
        else:
            bg = c_blue_cell_hi if idx == 0 else ('#F1F5F9' if idx == 4 else '#FFFFFF')
            bd = c_blue_primary if idx == 0 else (c_slate_dark if idx == 4 else c_border_neutral)
            draw_badge(cur_bx, 66.5, bx_w, bx_h, bg, bd, lw=1.3 if idx in [0, 4] else 0.9, r=0.25, zorder=3)
            ax.text(cur_bx + bx_w/2, 68.1, str(b), fontsize=12.0, fontweight='bold' if idx in [0, 4] else 'normal',
                    ha='center', va='center', color=c_blue_navy if idx == 0 else c_text_dark, zorder=4)

    # Flip indicators below bits
    x_cell0 = bx_start + 0.5 * bx_w
    ax.annotate('', xy=(x_cell0 + 0.9, 64.5), xytext=(x_cell0 - 0.9, 64.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.4, connectionstyle='arc3,rad=-0.45', mutation_scale=9), zorder=4)
    ax.text(x_cell0, 62.2, r'$0 \to 1$', fontsize=11.5, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)

    x_cell4 = bx_start + 4.5 * bx_w
    ax.annotate('', xy=(x_cell4 + 0.9, 64.5), xytext=(x_cell4 - 0.9, 64.5),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.4, connectionstyle='arc3,rad=-0.45', mutation_scale=9), zorder=4)
    ax.text(x_cell4, 62.2, r'$1 \to 0$', fontsize=11.5, fontweight='bold', color=c_slate_dark, ha='center', va='center', zorder=4)

    # Guidance arrow from Matrix W right edge to KER
    ax.annotate('', xy=(69.0, 68.0), xytext=(w_x_start + total_w_width + 0.6, 53.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.16', mutation_scale=13), zorder=5)

    # Down arrow 2 to Fitness Re-evaluation
    ax.annotate('', xy=(s3_cx, 55.5), xytext=(s3_cx, 59.5),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=11), zorder=5)

    # Fitness Re-evaluation Header
    ax.text(s3_cx, 53.5, 'Fitness Re-evaluation', fontsize=13.5, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    # Down arrow 3 to Decision Diamond
    ax.annotate('', xy=(s3_cx, 47.5), xytext=(s3_cx, 51.5),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=11), zorder=5)

    # Decision Diamond (Enlarged)
    dia_w, dia_h = 6.5, 3.5
    diamond = patches.Polygon([[s3_cx, 44.0 + dia_h], [s3_cx + dia_w, 44.0], [s3_cx, 44.0 - dia_h], [s3_cx - dia_w, 44.0]],
                              facecolor=c_card_bg, edgecolor=c_blue_navy, linewidth=1.4, zorder=3)
    ax.add_patch(diamond)
    ax.text(s3_cx, 44.0, 'Improved?', fontsize=12.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=4)

    # Yes / No Branch Arrows
    # Yes -> Left Down (Cobalt Blue)
    ax.annotate('', xy=(s3_cx - 8.5, 39.5), xytext=(s3_cx - dia_w, 44.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.8, mutation_scale=10), zorder=5)
    ax.text(s3_cx - 9.0, 44.5, 'Yes', fontsize=12.0, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)
    ax.text(s3_cx - 9.0, 37.0, 'Accept Refined', fontsize=11.0, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=4)

    # Arrow from Accept down to Elite (after)
    ax.annotate('', xy=(s3_cx - 2.5, 27.5), xytext=(s3_cx - 9.0, 34.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.5, connectionstyle='arc3,rad=-0.12', mutation_scale=9), zorder=5)

    # No -> Right Down (Slate Muted)
    ax.annotate('', xy=(s3_cx + 8.5, 39.5), xytext=(s3_cx + dia_w, 44.0),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.8, mutation_scale=10), zorder=5)
    ax.text(s3_cx + 9.0, 44.5, 'No', fontsize=12.0, fontweight='bold', color=c_text_light, ha='center', va='center', zorder=4)
    ax.text(s3_cx + 9.0, 37.0, 'Retain Original', fontsize=11.0, fontweight='bold', color=c_text_light, ha='center', va='center', zorder=4)

    # Arrow from Retain down to Elite (after)
    ax.annotate('', xy=(s3_cx + 2.5, 27.5), xytext=(s3_cx + 9.0, 34.5),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.5, connectionstyle='arc3,rad=0.12', mutation_scale=9), zorder=5)

    # Array 3: Elite Solution (After Selection)
    ax.text(s3_cx, 26.5, r'Elite Solution $\mathbf{x}_e^\star$ (After In-Place Selection)', fontsize=13.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)

    for idx, b in enumerate(bits_ea):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + bx_w/2, 21.1, r'$\dots$', fontsize=13.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=3)
        else:
            bg = c_blue_cell_hi if idx == 0 else ('#F8FAFC' if idx == 4 else '#FFFFFF')
            bd = c_blue_primary if idx == 0 else (c_slate_dark if idx == 4 else c_border_neutral)
            draw_badge(cur_bx, 19.5, bx_w, bx_h, bg, bd, lw=1.3 if idx in [0, 4] else 0.9, r=0.25, zorder=3)
            ax.text(cur_bx + bx_w/2, 21.1, str(b), fontsize=12.0, fontweight='bold' if idx in [0, 4] else 'normal',
                    ha='center', va='center', color=c_blue_navy if idx == 0 else c_text_dark, zorder=4)

    # =========================================================================
    # 4. BOTTOM SPANNING CLOSED-LOOP LEARNING CHANNEL (Fully Connected Path)
    # =========================================================================
    # 1. Downward line from Elite Solution x_e* (y=19.5) to bottom channel (y=6.5)
    ax.plot([s3_cx, s3_cx], [19.5, 6.5], color=c_blue_primary, lw=2.0, zorder=5)
    
    # 2. Horizontal line across bottom channel from Stage 3 (x=82.5) to Stage 1 (x=16.7)
    ax.plot([s3_cx, s1_cx], [6.5, 6.5], color=c_blue_primary, lw=2.0, zorder=5)
    
    # 3. Upward arrow into Stage 1 container bottom (y=13.0)
    ax.annotate('', xy=(s1_cx, 13.0), xytext=(s1_cx, 6.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0, mutation_scale=13), zorder=6)

    # Centered pill badge on channel line
    draw_badge(26.0, 4.0, 48.0, 5.0, c_card_bg, c_blue_border, lw=1.0, r=0.3, zorder=6)
    ax.text(50.0, 6.5, 'Closed-Loop Evolutionary Knowledge Feedback Channel',
            fontsize=12.5, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=7)

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
    from generate_journal_drawio import build_f3
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_file = os.path.join(base_dir, 'output', 'figures', 'F3_ker_strategy_journal.drawio')
    build_f3(out_file)

if __name__ == '__main__':
    create_figure3()
    generate_drawio()

