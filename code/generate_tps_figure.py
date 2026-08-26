"""Publication-grade Figure 4 for Two-Phase Dynamic Weight Scheduling (TPS) in KDS-EL.
Strictly adheres to Top-Tier Journal (Elsevier SWEVO/KBS/INS, IEEE TEVC) design standards:
- Clear 2-Container Architecture (Timeline & Dynamic Specifications + Continuous Search Landscape).
- Clean theoretical notations without hardcoded empirical hyperparameter clutter or redundant parentheses.
- Pure academic palette: Cobalt Blue + Slate Neutral.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle
from scipy.interpolate import make_interp_spline
import numpy as np

def create_figure4():
    # Set Times New Roman & STIX typography
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(16.5, 8.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color System - Harmonized Academic Cobalt Blue & Slate Neutral
    c_card_bg = '#FFFFFF'
    c_panel_bg = '#F8FAFC'        # Slate 50
    c_text_dark = '#0F172A'       # Slate 900
    c_text_muted = '#475569'      # Slate 600
    c_text_light = '#64748B'      # Slate 500
    
    c_blue_navy = '#1E3A8A'       # Blue 900
    c_blue_primary = '#1D4ED8'    # Blue 700
    c_blue_mid = '#2563EB'        # Blue 600
    c_blue_light = '#EFF6FF'      # Blue 50
    c_blue_border = '#93C5FD'     # Blue 300
    
    c_slate_dark = '#334155'      # Slate 700
    c_border_neutral = '#CBD5E1'  # Slate 300

    def draw_badge(x, y, w, h, bg, border, lw=1.1, r=0.4, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.03,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 0. MAIN STRUCTURAL BOUNDING CONTAINERS (方框/面板结构)
    # =========================================================================
    # 0. MAIN STRUCTURAL BOUNDING CONTAINERS (方框/面板结构)
    # =========================================================================
    # Top Timeline & Dynamic Objective Container
    draw_badge(2.0, 69.5, 96.0, 28.5, c_panel_bg, c_border_neutral, lw=1.2, r=0.5, zorder=1)
    
    # Central Continuous Search Landscape Container
    draw_badge(2.0, 3.0, 96.0, 64.5, '#FFFFFF', c_border_neutral, lw=1.2, r=0.5, zorder=1)

    # =========================================================================
    # 1. TOP EVOLUTIONARY TIMELINE
    # =========================================================================
    t_y = 93.8
    t_x_start = 8.0
    t_x_split = 62.0
    t_x_end = 92.0

    # Phase 1 segment (Cobalt Blue)
    ax.plot([t_x_start, t_x_split], [t_y, t_y], color=c_blue_primary, lw=3.2, solid_capstyle='round', zorder=3)
    # Phase 2 segment (Deep Navy Blue)
    ax.plot([t_x_split, t_x_end], [t_y, t_y], color=c_blue_navy, lw=3.2, solid_capstyle='round', zorder=3)

    # Timeline Nodes
    # Iteration 1
    ax.add_patch(Circle((t_x_start, t_y), 0.75, facecolor=c_blue_primary, edgecolor='#FFFFFF', lw=1.5, zorder=5))
    ax.text(t_x_start, t_y + 2.5, r'Initialization ($t = 1$)', fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=6)

    # Phase Transition Point (Precisely Aligned at x=62.0)
    ax.add_patch(Circle((t_x_split, t_y), 0.95, facecolor='#FFFFFF', edgecolor=c_blue_navy, lw=2.4, zorder=5))
    ax.text(t_x_split, t_y + 2.5, r'Phase Transition ($t = \tau T$)', fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_blue_navy, zorder=6)

    # Termination Point
    ax.add_patch(Circle((t_x_end, t_y), 0.75, facecolor=c_blue_navy, edgecolor='#FFFFFF', lw=1.5, zorder=5))
    ax.text(t_x_end, t_y + 2.5, r'Termination ($t = T$)', fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=6)

    # Subtle Phase Transition Vertical Dashed Line across the landscape
    ax.plot([62.0, 62.0], [5.0, 64.0], color='#CBD5E1', lw=1.2, linestyle=(0, (4, 4)), alpha=0.8, zorder=2)

    # =========================================================================
    # 2. UPPER MODULAR SPECIFICATION CARDS (CLEAN, BOLD, NO FILLER TEXT)
    # =========================================================================
    card_h = 16.5
    card_y = 72.0

    # CARD 1: Phase 1 (Left)
    c1_x, c1_w = 4.0, 30.0
    draw_badge(c1_x, card_y, c1_w, card_h, c_card_bg, c_blue_border, lw=1.2, r=0.4, zorder=2)
    ax.text(c1_x + c1_w/2, card_y + 13.0, 'Phase 1: Sparse Exploration', fontsize=12.2, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=3)
    ax.text(c1_x + c1_w/2, card_y + 8.2, r'$f(\mathbf{x}, \mathbf{w}) = w_{\mathrm{acc}} \cdot \mathrm{Error}(\mathbf{x}) + w_{\mathrm{feat}} \cdot \frac{\|\mathbf{x}\|_0}{D}$', fontsize=9.8, color=c_text_dark, ha='center', va='center', zorder=3)
    ax.text(c1_x + c1_w/2, card_y + 3.5, r'$w_{\mathrm{feat}} > w_{\mathrm{acc}}$', fontsize=11.0, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=3)

    # CARD 2: Adaptive Weight Shift (Center)
    c2_x, c2_w = 36.0, 28.0
    draw_badge(c2_x, card_y, c2_w, card_h, c_card_bg, c_border_neutral, lw=1.2, r=0.4, zorder=2)
    ax.text(c2_x + c2_w/2, card_y + 13.0, 'Adaptive Weight Shift', fontsize=12.2, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(c2_x + c2_w/2, card_y + 8.2, r'$\mathbf{w}_{\mathrm{Phase\ 1}} \;\longrightarrow\; \mathbf{w}_{\mathrm{Phase\ 2}}$', fontsize=11.5, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)
    ax.text(c2_x + c2_w/2, card_y + 3.5, r'Switch at $t = \tau T$', fontsize=11.0, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    # CARD 3: Phase 2 (Right)
    c3_x, c3_w = 66.0, 30.0
    draw_badge(c3_x, card_y, c3_w, card_h, c_card_bg, c_border_neutral, lw=1.2, r=0.4, zorder=2)
    ax.text(c3_x + c3_w/2, card_y + 13.0, 'Phase 2: Accuracy Refinement', fontsize=12.2, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)
    ax.text(c3_x + c3_w/2, card_y + 8.2, r'$f(\mathbf{x}, \mathbf{w}) = w_{\mathrm{acc}} \cdot \mathrm{Error}(\mathbf{x}) + w_{\mathrm{feat}} \cdot \frac{\|\mathbf{x}\|_0}{D}$', fontsize=9.8, color=c_text_dark, ha='center', va='center', zorder=3)
    ax.text(c3_x + c3_w/2, card_y + 3.5, r'$w_{\mathrm{acc}} \gg w_{\mathrm{feat}}$', fontsize=11.0, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    # =========================================================================
    # 3. CONTINUOUS OPTIMIZATION LANDSCAPE (CONTOUR BACKGROUND)
    # =========================================================================
    # Create smooth meshgrid across canvas [3.0 to 97.0, 4.0 to 65.0]
    nx, ny = 320, 240
    gx = np.linspace(3.0, 97.0, nx)
    gy = np.linspace(4.0, 65.0, ny)
    X, Y = np.meshgrid(gx, gy)

    # Broad Phase 1 Basin centered around (34, 36)
    Z1 = ((X - 34.0)/25.0)**2 + ((Y - 36.0)/20.0)**2
    # Focused Phase 2 Basin centered around (85, 35)
    Z2 = ((X - 85.0)/9.5)**2 + ((Y - 35.0)/10.5)**2
    # Combined smooth potential field
    blend = 1.0 / (1.0 + np.exp(-(X - 62.0) / 4.5))
    Z = (1.0 - blend) * Z1 + blend * Z2 * 1.6

    # Draw smooth translucent contour lines
    levels_all = [0.35, 0.75, 1.3, 2.0, 2.8, 3.8]
    ax.contour(X, Y, Z, levels=levels_all, colors='#CBD5E1', linewidths=0.75, linestyles='solid', alpha=0.7, zorder=1)

    # Soft subtle basin shading
    ax.contourf(X, Y, Z1, levels=[0.0, 1.0, 2.4], colors=['#EFF6FF', '#F8FAFC', '#FFFFFF'], alpha=0.6, zorder=0)
    ax.contourf(X, Y, Z2, levels=[0.0, 0.6, 1.6], colors=['#DBEAFE', '#EFF6FF', '#FFFFFF'], alpha=0.5, zorder=0)

    # Clean Landscape Labels
    ax.text(34.0, 5.5, 'Sparsity-Oriented Fitness Landscape', fontsize=10.0, fontweight='bold', color='#64748B', ha='center', va='center', zorder=2)
    ax.text(85.0, 5.5, 'Accuracy-Oriented Fitness Landscape', fontsize=10.0, fontweight='bold', color=c_blue_navy, alpha=0.9, ha='center', va='center', zorder=2)

    # =========================================================================
    # 4. CONTINUOUS EVOLUTIONARY SEARCH TRAJECTORY & CANDIDATE PATHS
    # =========================================================================
    # Secondary candidate exploration paths in Phase 1
    cand_paths_p1 = [
        np.array([[10.0, 56.0], [19.0, 52.0], [29.0, 47.0], [40.0, 46.0], [50.0, 40.0], [59.0, 38.0]]),
        np.array([[11.0, 19.0], [19.0, 25.0], [31.0, 22.0], [43.0, 27.0], [52.0, 31.0], [60.0, 34.0]]),
        np.array([[13.0, 39.0], [22.0, 30.0], [34.0, 36.0], [45.0, 33.0], [56.0, 37.0]])
    ]
    for cpath in cand_paths_p1:
        t_pts = np.linspace(0, 1, len(cpath))
        t_dense = np.linspace(0, 1, 80)
        spl_x = make_interp_spline(t_pts, cpath[:, 0], k=2)(t_dense)
        spl_y = make_interp_spline(t_pts, cpath[:, 1], k=2)(t_dense)
        ax.plot(spl_x, spl_y, color='#93C5FD', lw=1.1, linestyle='--', alpha=0.7, zorder=2)
        for pt in cpath[::2]:
            ax.add_patch(Circle((pt[0], pt[1]), 0.35, facecolor='#BFDBFE', edgecolor=c_blue_mid, lw=0.6, alpha=0.8, zorder=3))

    # Primary Continuous Evolutionary Trajectory
    main_waypoints = np.array([
        [8.5, 47.5],    # Iter 1 (Global initial state)
        [15.5, 32.0],   # Broad global exploration dip
        [24.5, 43.5],   # Exploration crest
        [35.0, 31.0],   # Feature reduction trough
        [46.5, 40.0],   # Intermediate convergence crest
        [55.5, 34.0],   # Pre-transition guidance
        [62.0, 36.0],   # Phase transition pivot point
        [69.0, 39.5],   # Phase 2 refinement step 1
        [76.0, 32.5],   # Phase 2 refinement step 2
        [81.5, 36.5],   # Phase 2 local convergence
        [84.0, 34.0],   # Fine-scale elite tuning
        [85.5, 35.5],   # Final Elite Convergence
    ])

    # Spline interpolation for smooth organic curve
    t_wp = np.linspace(0, 1, len(main_waypoints))
    t_smooth = np.linspace(0, 1, 400)
    curve_x = make_interp_spline(t_wp, main_waypoints[:, 0], k=3)(t_smooth)
    curve_y = make_interp_spline(t_wp, main_waypoints[:, 1], k=3)(t_smooth)

    # Color transition along main trajectory: Cobalt Blue -> Deep Navy Blue
    for i in range(len(curve_x) - 1):
        cx_val = curve_x[i]
        if cx_val <= 62.0:
            seg_col = c_blue_primary
            lw_val = 2.6
        else:
            seg_col = c_blue_navy
            lw_val = 2.8
        ax.plot([curve_x[i], curve_x[i+1]], [curve_y[i], curve_y[i+1]], color=seg_col, lw=lw_val, solid_capstyle='round', zorder=4)

    # Directional Flow Arrows along main trajectory
    arrow_indices = [35, 110, 175, 255, 330]
    for idx in arrow_indices:
        p_start = (curve_x[idx], curve_y[idx])
        p_end = (curve_x[idx+4], curve_y[idx+4])
        arr_col = c_blue_primary if curve_x[idx] < 62.0 else c_blue_navy
        ax.annotate('', xy=p_end, xytext=p_start,
                    arrowprops=dict(arrowstyle='-|>', color=arr_col, lw=2.2, mutation_scale=11), zorder=5)

    # Milestone Trajectory Checkpoints (t=1, t=\tau T, t=T)
    checkpoints = [
        (main_waypoints[0], r'$t=1$', c_blue_primary, 'bottom', (0, 2.0)),
        (main_waypoints[6], r'$t=\tau T$', c_blue_navy, 'top', (0, -2.2)),
        (main_waypoints[11], r'$t=T$', c_blue_navy, 'bottom', (-1.2, 2.2))
    ]
    for pt, lbl, col, va_align, offset in checkpoints:
        ax.add_patch(Circle((pt[0], pt[1]), 0.65, facecolor=col, edgecolor='#FFFFFF', lw=1.3, zorder=6))
        ax.text(pt[0] + offset[0], pt[1] + offset[1], lbl, fontsize=10.5, fontweight='bold', color=col, ha='center', va=va_align, zorder=6)

    # Subtle Transition Marker Circle at t=tau T
    p_trans = main_waypoints[6]
    ax.add_patch(Circle((p_trans[0], p_trans[1]), 1.2, facecolor='none', edgecolor=c_blue_navy, lw=1.8, linestyle='--', zorder=7))

    # Secondary Local Refinement Orbit Paths in Phase 2
    r_loc = 2.8
    for la in [0.4, 2.0, 3.8, 5.2]:
        lx = 85.5 + r_loc * np.cos(la)
        ly = 35.5 + r_loc * 0.7 * np.sin(la)
        ax.add_patch(Circle((lx, ly), 0.3, facecolor=c_blue_border, edgecolor=c_blue_navy, lw=0.5, zorder=5))
        ax.annotate('', xy=(85.5 + 0.7*np.cos(la), 35.5 + 0.5*np.sin(la)), xytext=(lx, ly),
                    arrowprops=dict(arrowstyle='->', color=c_blue_mid, lw=0.8, mutation_scale=7), zorder=4)

    # Final Elite Solution Node (Cobalt/Navy Star & Concentrated Core)
    p_final = main_waypoints[11]
    ax.plot(p_final[0], p_final[1], marker='*', markersize=16, color=c_blue_primary, markeredgecolor=c_blue_navy, markeredgewidth=1.2, zorder=9)
    ax.text(p_final[0] + 3.2, p_final[1] + 0.4, r'$\mathbf{x}^\star\ \mathrm{Optimal\ Feature\ Subset}$',
            fontsize=11.0, fontweight='bold', color=c_blue_navy, ha='left', va='center', zorder=9)

    # Clean, Bold Search Mode Annotations (NO redundant filler subtitles)
    ax.text(26.0, 19.5, 'Global Exploration', fontsize=11.5, fontweight='bold', color=c_blue_primary, ha='center', va='center', zorder=3)
    ax.text(85.5, 19.5, 'Local Refinement', fontsize=11.5, fontweight='bold', color=c_blue_navy, ha='center', va='center', zorder=3)

    # Save Outputs
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F4_tps_strategy_journal.pdf')
    png_path = os.path.join(out_dir, 'F4_tps_strategy_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated Clean Publication-Grade Figure 4 PDF and PNG successfully!')

def generate_drawio():
    import xml.etree.ElementTree as ET
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f4-tps-continuous', name='Figure 4: TPS Continuous Mechanism')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1422', dy='798', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='1400', pageHeight='850', math='1', shadow='0')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def add_cell(cid, value, style, x, y, w, h, parent='1'):
        cell = ET.SubElement(root, 'mxCell', id=str(cid), value=str(value), style=style, parent=parent, vertex='1')
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})
        return cell

    # Outer containers
    add_cell('f4_top', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 20, 15, 1360, 240)
    add_cell('f4_main', '', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 20, 270, 1360, 600)

    # Timeline elements
    add_cell('it1', '&lt;b&gt;Initialization ($t=1$)&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 60, 30, 140, 25)
    add_cell('it70', '&lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;Phase Transition ($t=\\tau T$)&lt;/font&gt;&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 580, 30, 220, 25)
    add_cell('it100', '&lt;b&gt;Termination ($t=T$)&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 1140, 30, 140, 25)

    # Phase 1 & 2 Cards
    add_cell('p1_card', '&lt;b&gt;&lt;font size=\"4\" color=\"#1D4ED8\"&gt;Phase 1: Sparse Exploration&lt;/font&gt;&lt;/b&gt;&lt;br&gt;$$f(\\mathbf{x}, \\mathbf{w}) = w_{\\mathrm{acc}} \\cdot \\mathrm{Error}(\\mathbf{x}) + w_{\\mathrm{feat}} \\cdot \\frac{\\|\\mathbf{x}\\|_0}{D}$$&lt;br&gt;&lt;b&gt;$$w_{\\mathrm{feat}} > w_{\\mathrm{acc}}$$&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#93C5FD;align=center;verticalAlign=top;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 60, 80, 420, 140)
    add_cell('trans_card', '&lt;b&gt;&lt;font size=\"4\" color=\"#1E3A8A\"&gt;Adaptive Weight Shift&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;b&gt;$$\\mathbf{w}_{\\mathrm{Phase\\ 1}} \\longrightarrow \\mathbf{w}_{\\mathrm{Phase\\ 2}}$$&lt;/b&gt;&lt;br&gt;&lt;b&gt;Switch at $t = \\tau T$&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;align=center;verticalAlign=top;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 510, 80, 380, 140)
    add_cell('p2_card', '&lt;b&gt;&lt;font size=\"4\" color=\"#1E3A8A\"&gt;Phase 2: Accuracy Refinement&lt;/font&gt;&lt;/b&gt;&lt;br&gt;$$f(\\mathbf{x}, \\mathbf{w}) = w_{\\mathrm{acc}} \\cdot \\mathrm{Error}(\\mathbf{x}) + w_{\\mathrm{feat}} \\cdot \\frac{\\|\\mathbf{x}\\|_0}{D}$$&lt;br&gt;&lt;b&gt;$$w_{\\mathrm{acc}} \\gg w_{\\mathrm{feat}}$$&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;align=center;verticalAlign=top;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 920, 80, 420, 140)

    out_file = 'output/figures/F4_tps_strategy_journal.drawio'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated Clean Figure 4 Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure4()
    generate_drawio()

