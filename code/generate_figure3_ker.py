"""Publication-grade Figure 3 for KER Strategy in KDS-EL.
Harmonized Color System:
- Pure Academic Cobalt Blue & Slate Neutral palette (Zero orange/green color clash).
- Clean Porcelain White cards (#FFFFFF).
- Fully aligned with Figure 1: Matrix W naming, discrete cell format, and blue colormap.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle

def create_figure3():
    # Times New Roman & STIX math typography (Unified with Figure 1, 2, 4)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(15.5, 9.6), dpi=300)
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
    c_blue_primary = '#1D4ED8'    # Blue 700 (Flow arrows, highlights, active bits)
    c_blue_mid = '#2563EB'        # Blue 600 (Secondary arrows, borders)
    c_blue_cell = '#EFF6FF'       # Blue 50 (Active binary bit background)
    c_blue_cell_hi = '#DBEAFE'    # Blue 100 (Newly flipped bit 1 background)
    c_blue_border = '#93C5FD'     # Blue 300 (Subtle box borders)
    
    # Structural Neutrals
    c_gray_border = '#CBD5E1'     # Slate 300
    c_gray_fill = '#F8FAFC'       # Slate 50
    c_slate_dark = '#334155'      # Slate 700

    def draw_box(x, y, w, h, bg, border, lw=1.1, r=0.3, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.04,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 1. LEFT: POPULATION MATRIX & FITNESS EVALUATION
    # =========================================================================
    pop_data = [
        (r'$P_1$', [1, 0, 1, 0, 1, 0, '...', 1, 0, 0]),
        (r'$P_2$', [0, 1, 0, 1, 1, 0, '...', 0, 1, 1]),
        (r'$P_3$', [1, 1, 0, 0, 1, 0, '...', 1, 0, 0]),
        ('dots', None),
        (r'$P_N$', [0, 1, 1, 0, 0, 1, '...', 1, 1, 0])
    ]

    cell_w, cell_h = 2.3, 3.2
    y_start = 80.5
    y_spacing = 7.0
    lx_start = 6.2

    # Feature headers aligned with cell columns
    feat_labels = [r'$f_1$', r'$f_2$', r'$f_3$', r'$\dots$', r'$f_D$']
    feat_x = [lx_start + cell_w*0.5, lx_start + cell_w*1.5, lx_start + cell_w*2.5, lx_start + cell_w*6 + 1.1, lx_start + cell_w*7 + 2.2 + cell_w*1.0]
    for lbl, fx in zip(feat_labels, feat_x):
        ax.text(fx, 86.0, lbl, fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_text_dark)

    for row_idx, (p_name, bits) in enumerate(pop_data):
        curr_y = y_start - row_idx * y_spacing
        if p_name == 'dots':
            ax.text(17.5, curr_y + 1.2, r'$\vdots$', fontsize=16, fontweight='bold', ha='center', va='center', color=c_text_dark)
            continue
        
        ax.text(3.5, curr_y + cell_h/2, p_name, fontsize=12, fontweight='bold', ha='center', va='center', color=c_text_dark)

        x_c = lx_start
        for b in bits:
            if b == '...':
                ax.text(x_c + 1.1, curr_y + cell_h/2, r'$\dots$', fontsize=11, fontweight='bold', ha='center', va='center', color=c_text_dark)
                x_c += 2.2
            else:
                bg = c_blue_cell if b == 1 else '#FFFFFF'
                draw_box(x_c, curr_y, cell_w, cell_h, bg, c_gray_border, lw=0.9, r=0.25)
                ax.text(x_c + cell_w/2, curr_y + cell_h/2, str(b), fontsize=10.5, ha='center', va='center', color=c_text_dark)
                x_c += cell_w

    # Down arrow to Fitness Evaluation
    ax.annotate('', xy=(17.5, 43.5), xytext=(17.5, 49.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0, mutation_scale=14))

    # Fitness Evaluation Box (Porcelain White)
    draw_box(7.5, 17.5, 20.0, 24.5, c_card_bg, c_blue_border, lw=1.3, r=0.6)
    
    # 3 Evaluation metric bars
    ax.add_patch(patches.Rectangle((11.5, 27.5), 2.6, 8.5, facecolor='#3B82F6', edgecolor='none', zorder=3))
    ax.add_patch(patches.Rectangle((16.2, 27.5), 2.6, 11.5, facecolor=c_blue_primary, edgecolor='none', zorder=3))
    ax.add_patch(patches.Rectangle((20.9, 27.5), 2.6, 6.5, facecolor='#60A5FA', edgecolor='none', zorder=3))
    
    # Title centered inside box
    ax.text(17.5, 22.0, 'Fitness Evaluation', fontsize=12.5, fontweight='bold', ha='center', va='center', color=c_blue_navy, zorder=4)

    # =========================================================================
    # 2. TOP & CENTER: KNOWLEDGE UPDATE & CUMULATIVE FEATURE-IMPORTANCE MATRIX W
    # =========================================================================
    # Fitness Feedback curved arrow (Top Left)
    ax.annotate('', xy=(42.0, 93.0), xytext=(22.0, 93.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.14', mutation_scale=16))
    ax.text(32.0, 96.5, 'Fitness Feedback', fontsize=12.0, fontweight='bold', color=c_blue_primary, ha='center', va='center')

    # Knowledge Update Title
    ax.text(49.0, 91.0, 'Knowledge Update', fontsize=13.5, fontweight='bold', color=c_text_dark, ha='center', va='center')
    ax.text(49.0, 85.5, 'Accumulated Evolutionary Experience', fontsize=9.5, fontstyle='italic', color=c_text_muted, ha='center', va='center')

    # Arrow down to history cards
    ax.annotate('', xy=(49.0, 82.0), xytext=(49.0, 84.0),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.6, mutation_scale=11))

    # History cards (t-2, t-1, ..., t) - Clean Porcelain White cards with blue dots
    cards = [
        (r'$t-2$', 40.5, '#60A5FA', [(-0.3, 0.4), (0.2, 0.6), (0.0, 0.0), (-0.2, -0.4), (0.3, -0.3)]),
        (r'$t-1$', 46.8, '#3B82F6', [(0.1, 0.5), (-0.2, 0.3), (0.0, 0.0), (0.2, -0.4), (-0.1, -0.5)]),
        (r'$t$', 55.2, c_blue_primary, [(0.2, 0.4), (-0.3, 0.5), (0.0, 0.1), (0.1, -0.3), (-0.2, -0.4)])
    ]

    for lbl, cx, col, pts in cards:
        draw_box(cx, 71.0, 5.0, 9.5, c_card_bg, c_gray_border, lw=1.0, r=0.4)
        for px, py in pts:
            ax.add_patch(Circle((cx + 2.5 + px*1.2, 76.8 + py*1.5), 0.38, facecolor=col, edgecolor='none', zorder=4))
        ax.plot([cx + 2.5, cx + 2.5], [74.2, 79.2], color=col, lw=1.0, alpha=0.6, zorder=3)
        ax.text(cx + 2.5, 72.4, lbl, fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark)

    ax.text(52.9, 75.8, r'$\dots$', fontsize=13, fontweight='bold', ha='center', va='center', color=c_text_dark)

    # Three arrows from cards down to Matrix W
    for cx in [43.0, 49.3, 57.7]:
        ax.annotate('', xy=(cx, 63.5), xytext=(cx, 70.0),
                    arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.5, mutation_scale=10))

    # EXACT NAME ALIGNMENT WITH FIGURE 1: Cumulative Feature-Importance Matrix W
    ax.text(49.0, 60.5, r'Cumulative Feature-Importance Matrix $W$', fontsize=12.5, fontweight='bold', color=c_text_dark, ha='center', va='center')

    # EXACT VISUAL & COLOR ALIGNMENT WITH FIGURE 1: Blues colormap
    w_strip_labels = [r'$f_1$', r'$f_2$', r'$f_3$', r'$\dots$', r'$f_{D-2}$', r'$f_{D-1}$', r'$f_D$']
    w_strip_vals = [0.92, 0.74, 0.41, None, 0.88, 0.22, 0.65]
    
    w_box_w = 4.0
    w_box_h = 4.2
    w_gap = 0.8
    total_w_width = len(w_strip_labels) * w_box_w + (len(w_strip_labels) - 1) * w_gap
    w_x_start = 49.0 - total_w_width / 2.0
    w_y_base = 48.0

    for si, (s_lbl, s_v) in enumerate(zip(w_strip_labels, w_strip_vals)):
        sx = w_x_start + si * (w_box_w + w_gap)
        if s_v is not None:
            scol = plt.cm.Blues(0.25 + 0.70 * s_v)
            st_color = '#FFFFFF' if s_v > 0.6 else '#0F172A'
            bd_color = '#94A3B8' if s_v <= 0.6 else c_blue_primary
            
            draw_box(sx, w_y_base, w_box_w, w_box_h, scol, bd_color, lw=1.0, r=0.3, zorder=3)
            ax.text(sx + w_box_w/2, w_y_base + w_box_h/2, s_lbl, fontsize=10.5, fontweight='bold',
                    ha='center', va='center', color=st_color, zorder=4)
        else:
            # Ellipsis box
            draw_box(sx, w_y_base, w_box_w, w_box_h, '#F1F5F9', '#CBD5E1', lw=0.9, r=0.3, zorder=3)
            ax.text(sx + w_box_w/2, w_y_base + w_box_h/2, r'$\dots$', fontsize=11.5, fontweight='bold',
                    ha='center', va='center', color='#475569', zorder=4)

    # Clean semantic legend below Matrix W (Harmonized with Blue Palette)
    leg_y = 42.5
    draw_box(33.5, leg_y, 2.0, 1.6, plt.cm.Blues(0.85), c_blue_primary, r=0.1, zorder=3)
    ax.text(36.0, leg_y + 0.8, r'High $W_j$ (Key features $\to$ guide $0 \to 1$)', fontsize=9.0, fontweight='bold', ha='left', va='center', color=c_blue_navy)
    
    draw_box(52.0, leg_y, 2.0, 1.6, plt.cm.Blues(0.35), '#94A3B8', r=0.1, zorder=3)
    ax.text(54.5, leg_y + 0.8, r'Low $W_j$ (Redundant $\to$ prune $1 \to 0$)', fontsize=9.0, fontweight='bold', ha='left', va='center', color=c_text_muted)

    # Memory dynamic feedback circular arrow
    ax.annotate('', xy=(54.5, 29.5), xytext=(43.5, 29.5),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.6,
                                connectionstyle='arc3,rad=-0.70', mutation_scale=12))
    ax.annotate('', xy=(43.5, 29.5), xytext=(54.5, 29.5),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.6,
                                connectionstyle='arc3,rad=-0.70', mutation_scale=12))
    ax.text(49.0, 29.5, 'Dynamic Memory Decay\n' + r'($W \leftarrow \gamma W$)',
            fontsize=9.5, fontstyle='italic', ha='center', va='center', color=c_text_dark)

    # =========================================================================
    # 3. RIGHT: ELITE REFINEMENT (KER) - Harmonized Academic Blue & Slate
    # =========================================================================
    # Top curved arrow from Knowledge Update to KER (Cobalt Blue arch)
    ax.annotate('', xy=(78.0, 93.0), xytext=(58.0, 93.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.2,
                                connectionstyle='arc3,rad=-0.14', mutation_scale=16))

    # Section Title in Navy
    ax.text(81.0, 85.5, 'Elite Refinement (KER)', fontsize=13.0, fontweight='bold', color=c_blue_navy, ha='center', va='center')

    # Elite (before)
    ax.text(81.0, 80.0, 'Elite (before)', fontsize=11.0, fontstyle='italic', fontweight='bold', ha='center', va='center', color=c_text_dark)
    
    bits_eb = [0, 1, 1, 0, 1, 0, 0, 1, '...', 0, 1, 0]
    bx_start = 68.0
    bx_w = 2.3
    bx_h = 3.2
    
    for idx, b in enumerate(bits_eb):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + 1.15, 75.6, r'$\dots$', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark)
        else:
            draw_box(cur_bx, 74.0, bx_w, bx_h, '#FFFFFF', c_gray_border, lw=0.9, r=0.2)
            ax.text(cur_bx + bx_w/2, 75.6, str(b), fontsize=10.5, ha='center', va='center', color=c_text_dark)

    # Target indicator highlights (Subtle blue border for target 0, Slate border for target 1)
    draw_box(bx_start - 0.1, 73.9, bx_w + 0.2, bx_h + 0.2, 'none', c_blue_primary, lw=1.8, r=0.3)
    draw_box(bx_start + 7*bx_w - 0.1, 73.9, bx_w + 0.2, bx_h + 0.2, 'none', c_slate_dark, lw=1.8, r=0.3)

    # Down arrow in Slate
    ax.annotate('', xy=(81.0, 69.5), xytext=(81.0, 73.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=12))

    # Knowledge-guided Flip Header in Navy
    ax.text(81.0, 67.5, 'Knowledge-guided Directional Flip', fontsize=11.5, fontstyle='italic', fontweight='bold', color=c_blue_navy, ha='center', va='center')

    bits_kf = [1, 1, 1, 0, 0, 0, 0, 0, '...', 1, 0]
    for idx, b in enumerate(bits_kf):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + 1.15, 63.6, r'$\dots$', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark)
        else:
            # Active flipped 1 is Soft Ice Blue + Blue border; Pruned 0 is Soft Gray + Slate border
            bg = c_blue_cell_hi if idx == 0 else ('#F1F5F9' if idx == 7 else '#FFFFFF')
            bd = c_blue_primary if idx == 0 else (c_slate_dark if idx == 7 else c_gray_border)
            draw_box(cur_bx, 62.0, bx_w, bx_h, bg, bd, lw=1.3 if idx in [0, 7] else 0.9, r=0.2)
            ax.text(cur_bx + bx_w/2, 63.6, str(b), fontsize=10.5, fontweight='bold' if idx in [0, 7] else 'normal',
                    ha='center', va='center', color=c_blue_navy if idx == 0 else c_text_dark)

    # Flip indicators below bits (Blue for 0->1, Slate for 1->0)
    x_cell0 = bx_start + 0.5 * bx_w
    ax.annotate('', xy=(x_cell0 + 1.0, 59.8), xytext=(x_cell0 - 1.0, 59.8),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.5, connectionstyle='arc3,rad=-0.45', mutation_scale=10))
    ax.text(x_cell0, 57.2, r'$0 \to 1$', fontsize=10.5, fontweight='bold', color=c_blue_primary, ha='center', va='center')

    x_cell7 = bx_start + 7.5 * bx_w
    ax.annotate('', xy=(x_cell7 + 1.0, 59.8), xytext=(x_cell7 - 1.0, 59.8),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.5, connectionstyle='arc3,rad=-0.45', mutation_scale=10))
    ax.text(x_cell7, 57.2, r'$1 \to 0$', fontsize=10.5, fontweight='bold', color=c_slate_dark, ha='center', va='center')

    # Clean guidance arrow from Matrix W right edge to KER (Cobalt Blue)
    ax.annotate('', xy=(67.5, 63.6), xytext=(w_x_start + total_w_width + 0.6, 50.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.0,
                                connectionstyle='arc3,rad=-0.16', mutation_scale=14), zorder=5)

    # Down arrow to Fitness Re-evaluation
    ax.annotate('', xy=(81.0, 54.0), xytext=(81.0, 57.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=12))

    # Fitness Re-evaluation Text & Balance Scale Icon (Deep Navy & Slate)
    ax.text(78.0, 51.0, 'Fitness Re-evaluation', fontsize=11.5, fontstyle='italic', fontweight='bold', color=c_blue_navy, ha='center', va='center')
    
    # Balance Scale Icon (Cobalt Blue)
    sc_x, sc_y = 88.5, 51.0
    ax.plot([sc_x - 2.2, sc_x + 2.2], [sc_y + 0.8, sc_y + 0.8], color=c_blue_navy, lw=1.6)
    ax.plot([sc_x, sc_x], [sc_y - 1.2, sc_y + 0.8], color=c_blue_navy, lw=1.6)
    ax.plot([sc_x - 2.2, sc_x - 2.2], [sc_y - 0.2, sc_y + 0.8], color=c_blue_navy, lw=1.0)
    ax.plot([sc_x + 2.2, sc_x + 2.2], [sc_y - 0.2, sc_y + 0.8], color=c_blue_navy, lw=1.0)
    ax.add_patch(patches.Polygon([[sc_x - 2.8, sc_y - 0.2], [sc_x - 1.6, sc_y - 0.2], [sc_x - 2.2, sc_y - 0.9]], facecolor=c_blue_navy, edgecolor='none'))
    ax.add_patch(patches.Polygon([[sc_x + 1.6, sc_y - 0.2], [sc_x + 2.8, sc_y - 0.2], [sc_x + 2.2, sc_y - 0.9]], facecolor=c_blue_navy, edgecolor='none'))

    # Down arrow to Decision Diamond
    ax.annotate('', xy=(81.0, 45.0), xytext=(81.0, 48.0),
                arrowprops=dict(arrowstyle='-|>', color=c_slate_dark, lw=1.8, mutation_scale=12))

    # Decision Diamond (Porcelain White with Navy border)
    diamond = patches.Polygon([[81.0, 44.5], [87.0, 41.0], [81.0, 37.5], [75.0, 41.0]],
                              facecolor=c_card_bg, edgecolor=c_blue_navy, linewidth=1.5, zorder=3)
    ax.add_patch(diamond)
    ax.text(81.0, 41.0, 'Improved?', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=4)

    # Yes / No Branch Arrows
    # Yes -> Left Down (Cobalt Blue)
    ax.annotate('', xy=(72.5, 36.0), xytext=(75.0, 41.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.8, mutation_scale=12))
    ax.text(70.5, 41.5, 'Yes', fontsize=10.5, fontweight='bold', color=c_blue_primary, ha='center', va='center')
    ax.text(72.5, 33.5, 'Accept\n(refined elite)', fontsize=9.5, fontstyle='italic', fontweight='bold', color=c_blue_primary, ha='center', va='center')

    # Arrow from Accept down to Elite (after)
    ax.annotate('', xy=(78.5, 25.5), xytext=(72.5, 30.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=1.5, connectionstyle='arc3,rad=-0.12', mutation_scale=10))

    # No -> Right Down (Slate Muted)
    ax.annotate('', xy=(89.5, 36.0), xytext=(87.0, 41.0),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.8, mutation_scale=12))
    ax.text(91.5, 41.5, 'No', fontsize=10.5, fontweight='bold', color=c_text_light, ha='center', va='center')
    ax.text(89.5, 33.5, 'Retain\n(original elite)', fontsize=9.5, fontstyle='italic', fontweight='bold', color=c_text_light, ha='center', va='center')

    # Arrow from Retain down to Elite (after)
    ax.annotate('', xy=(83.5, 25.5), xytext=(89.5, 30.5),
                arrowprops=dict(arrowstyle='-|>', color=c_text_light, lw=1.5, connectionstyle='arc3,rad=0.12', mutation_scale=10))

    # Converge down to Elite (after)
    ax.text(81.0, 25.0, 'Elite (after)', fontsize=11.5, fontstyle='italic', fontweight='bold', ha='center', va='center', color=c_text_dark)

    bits_ea = [1, 1, 1, 0, 0, 0, 0, 1, '...', 1, 0]
    for idx, b in enumerate(bits_ea):
        cur_bx = bx_start + idx * bx_w
        if b == '...':
            ax.text(cur_bx + 1.15, 19.5, r'$\dots$', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark)
        else:
            bg = c_blue_cell_hi if idx == 0 else ('#F8FAFC' if idx == 7 else '#FFFFFF')
            bd = c_blue_primary if idx == 0 else (c_slate_dark if idx == 7 else c_gray_border)
            draw_box(cur_bx, 17.9, bx_w, bx_h, bg, bd, lw=1.3 if idx in [0, 7] else 0.9, r=0.2)
            ax.text(cur_bx + bx_w/2, 19.5, str(b), fontsize=10.5, fontweight='bold' if idx in [0, 7] else 'normal',
                    ha='center', va='center', color=c_blue_navy if idx == 0 else c_text_dark)

    # =========================================================================
    # 4. BOTTOM: CLOSED-LOOP KNOWLEDGE LEARNING ARROW (Academic Cobalt Blue)
    # =========================================================================
    ax.annotate('', xy=(18.0, 17.5), xytext=(81.0, 17.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_primary, lw=2.4,
                                connectionstyle='arc3,rad=-0.20', mutation_scale=18))

    ax.text(49.5, 3.2, 'Closed-loop Knowledge Learning (1-to-1 Replacement)', fontsize=13.0, fontweight='bold',
            color=c_blue_navy, ha='center', va='center')

    # Output paths
    out_dir = 'output/figures'
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F3_ker_strategy_journal.pdf')
    png_path = os.path.join(out_dir, 'F3_ker_strategy_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated harmonized Cobalt Blue Figure 3 successfully!')

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

    add_cell('w_title', '&lt;b&gt;Cumulative Feature-Importance Matrix $$W$$&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=14;fontColor=#0F172A;', 480, 290, 280, 30)
    add_cell('w_headers', '$$f_1 \\quad f_2 \\quad f_3 \\quad \\dots \\quad f_{D-2} \\quad f_{D-1} \\quad f_D$$', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;', 480, 320, 280, 25)

    out_file = 'output/figures/F3_ker_strategy_journal.drawio'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure3()
    generate_drawio()
