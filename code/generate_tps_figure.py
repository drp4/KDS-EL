"""Publication-grade Figure 4 for Two-Phase Dynamic Weight Scheduling (TPS) in KDS-EL.
Harmonized with Figure 3 Academic Color System:
- Strict 2-Family Academic Palette: Cobalt/Navy Blue (#1D4ED8 / #1E3A8A) + Slate Neutral (#334155 / #64748B / #CBD5E1).
- Smooth scientific contour landscape, no boxes, no cards.
- Zero color clash, professional, clean layout.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle
from scipy.interpolate import make_interp_spline
import numpy as np

def create_figure4():
    # Set Times New Roman & STIX typography
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(16, 9.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color System - Harmonized Academic Cobalt Blue & Slate Neutral
    c_text_dark = '#0F172A'       # Slate 900
    c_text_muted = '#475569'      # Slate 600
    c_text_light = '#64748B'      # Slate 500
    
    c_blue_navy = '#1E3A8A'       # Blue 900 (Phase 2 & Milestone & Main titles)
    c_blue_primary = '#1D4ED8'    # Blue 700 (Phase 1 & Flow arrows)
    c_blue_mid = '#2563EB'        # Blue 600
    c_blue_light = '#EFF6FF'      # Blue 50
    c_blue_border = '#93C5FD'     # Blue 300
    
    c_slate_dark = '#334155'      # Slate 700
    c_slate_line = '#64748B'      # Slate 500
    c_grid_line = '#CBD5E1'       # Slate 300

    # =========================================================================
    # 1. TOP EVOLUTIONARY TIMELINE
    # =========================================================================
    t_y = 92.5
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
    ax.text(t_x_start, t_y + 2.8, r'Initialization ($t = 1$)', fontsize=10.8, fontweight='bold', ha='center', va='center', color=c_text_dark)

    # Phase Transition Point
    ax.add_patch(Circle((t_x_split, t_y), 0.95, facecolor='#FFFFFF', edgecolor=c_blue_navy, lw=2.4, zorder=5))
    ax.text(t_x_split, t_y + 2.8, r'Phase Transition ($t = \tau T$)', fontsize=10.8, fontweight='bold', ha='center', va='center', color=c_blue_navy)

    # Termination Point
    ax.add_patch(Circle((t_x_end, t_y), 0.75, facecolor=c_blue_navy, edgecolor='#FFFFFF', lw=1.5, zorder=5))
    ax.text(t_x_end, t_y + 2.8, r'Termination ($t = T$)', fontsize=10.8, fontweight='bold', ha='center', va='center', color=c_text_dark)

    # Subtle Phase Transition Vertical Dashed Line across the whole height
    ax.plot([t_x_split, t_x_split], [15.0, t_y - 1.5], color='#CBD5E1', lw=1.2, linestyle=(0, (4, 4)), alpha=0.8, zorder=2)

    # =========================================================================
    # 2. CONTINUOUS OPTIMIZATION LANDSCAPE (CONTOUR BACKGROUND)
    # =========================================================================
    # Create smooth meshgrid across canvas [5 to 95, 16 to 70]
    nx, ny = 320, 220
    gx = np.linspace(5.0, 95.0, nx)
    gy = np.linspace(16.0, 70.0, ny)
    X, Y = np.meshgrid(gx, gy)

    # Broad Phase 1 Basin centered around (34, 42)
    Z1 = ((X - 34.0)/25.0)**2 + ((Y - 42.0)/18.0)**2
    # Focused Phase 2 Basin centered around (85, 41)
    Z2 = ((X - 85.0)/9.5)**2 + ((Y - 41.0)/9.5)**2
    # Combined smooth potential field
    blend = 1.0 / (1.0 + np.exp(-(X - 62.0) / 4.5))
    Z = (1.0 - blend) * Z1 + blend * Z2 * 1.6

    # Draw smooth translucent contour lines
    levels_all = [0.35, 0.75, 1.3, 2.0, 2.8, 3.8]
    ax.contour(X, Y, Z, levels=levels_all, colors='#CBD5E1', linewidths=0.75, linestyles='solid', alpha=0.7, zorder=1)

    # Soft subtle basin shading (Harmonized Ice Blue and Soft Slate)
    ax.contourf(X, Y, Z1, levels=[0.0, 1.0, 2.4], colors=['#EFF6FF', '#F8FAFC', '#FFFFFF'], alpha=0.6, zorder=0)
    ax.contourf(X, Y, Z2, levels=[0.0, 0.6, 1.6], colors=['#DBEAFE', '#EFF6FF', '#FFFFFF'], alpha=0.5, zorder=0)

    # Subtle Landscape Auxiliary Labels
    ax.text(34.0, 18.5, r'Sparsity-Oriented Fitness Landscape', fontsize=8.5, fontstyle='italic', color='#64748B', ha='center', va='center')
    ax.text(85.0, 18.5, r'Accuracy-Oriented Fitness Landscape', fontsize=8.5, fontstyle='italic', color=c_blue_navy, alpha=0.85, ha='center', va='center')

    # =========================================================================
    # 3. UPPER MATHEMATICAL & PREFERENCE SPECIFICATIONS
    # =========================================================================
    # LEFT REGION: Phase 1: Sparse Subset Exploration
    p1_tx = 8.0
    ax.text(p1_tx, 83.5, 'Phase 1: Sparse Subset Exploration', fontsize=12.5, fontweight='bold', color=c_blue_primary, va='center')
    ax.text(p1_tx, 79.5, r'$f(\mathbf{x}, \mathbf{w}) = w_{\mathrm{acc}} \cdot \mathrm{Error}(\mathbf{x}) + w_{\mathrm{feat}} \cdot \frac{\|\mathbf{x}\|_0}{D}$', fontsize=10.5, color=c_text_dark, va='center')
    ax.text(p1_tx, 75.8, r'High Feature-Ratio Penalty ($w_{\mathrm{feat}} > w_{\mathrm{acc}}$)', fontsize=10.5, fontweight='bold', color=c_blue_primary, va='center')
    ax.text(p1_tx, 72.2, r'Sparsity-oriented exploration $\cdot$ Progressive feature reduction', fontsize=9.2, fontstyle='italic', color=c_text_muted, va='center')

    # CENTER: Adaptive Weight Scheduling Transition Marker
    t_center_x = 62.0
    ax.text(t_center_x, 83.5, 'Adaptive Weight Scheduling', fontsize=12.5, fontweight='bold', color=c_blue_navy, ha='center', va='center')
    ax.text(t_center_x, 79.5, r'$\mathbf{w}_{\mathrm{Phase\ 1}} \;\longrightarrow\; \mathbf{w}_{\mathrm{Phase\ 2}}$',
            fontsize=12.0, fontweight='bold', color=c_text_dark, ha='center', va='center')

    # RIGHT REGION: Phase 2: Accuracy Refinement
    p2_tx = 72.0
    ax.text(p2_tx, 83.5, 'Phase 2: Accuracy Refinement', fontsize=12.5, fontweight='bold', color=c_blue_navy, va='center')
    ax.text(p2_tx, 79.5, r'$f(\mathbf{x}, \mathbf{w}) = w_{\mathrm{acc}} \cdot \mathrm{Error}(\mathbf{x}) + w_{\mathrm{feat}} \cdot \frac{\|\mathbf{x}\|_0}{D}$', fontsize=10.5, color=c_text_dark, va='center')
    ax.text(p2_tx, 75.8, r'Classification Fidelity Priority ($w_{\mathrm{acc}} \gg w_{\mathrm{feat}}$)', fontsize=10.5, fontweight='bold', color=c_blue_navy, va='center')
    ax.text(p2_tx, 72.2, r'Accuracy-oriented refinement $\cdot$ Elite subset fine-tuning', fontsize=9.2, fontstyle='italic', color=c_text_muted, va='center')

    # =========================================================================
    # 4. CONTINUOUS EVOLUTIONARY SEARCH TRAJECTORY & CANDIDATE PATHS
    # =========================================================================
    # Secondary candidate exploration paths in Phase 1
    cand_paths_p1 = [
        np.array([[10.0, 62.0], [19.0, 58.0], [29.0, 53.0], [40.0, 52.0], [50.0, 46.0], [59.0, 43.5]]),
        np.array([[11.0, 24.0], [19.0, 31.0], [31.0, 27.0], [43.0, 33.0], [52.0, 37.0], [60.0, 39.5]]),
        np.array([[13.0, 45.0], [22.0, 36.0], [34.0, 42.0], [45.0, 39.0], [56.0, 42.5]])
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
        [8.5, 53.5],    # Iter 1 (Global initial state)
        [15.5, 38.0],   # Broad global exploration dip
        [24.5, 49.5],   # Exploration crest
        [35.0, 37.0],   # Feature reduction trough
        [46.5, 46.0],   # Intermediate convergence crest
        [55.5, 39.5],   # Pre-transition guidance
        [62.0, 41.5],   # Phase transition pivot point
        [69.0, 45.0],   # Phase 2 refinement step 1
        [76.0, 37.8],   # Phase 2 refinement step 2
        [81.5, 42.2],   # Phase 2 local convergence
        [84.0, 39.5],   # Fine-scale elite tuning
        [85.5, 41.0],   # Final Elite Convergence
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
        ax.text(pt[0] + offset[0], pt[1] + offset[1], lbl, fontsize=10, fontweight='bold', color=col, ha='center', va=va_align, zorder=6)

    # Subtle Transition Marker Circle at t=70
    p_trans = main_waypoints[6]
    ax.add_patch(Circle((p_trans[0], p_trans[1]), 1.2, facecolor='none', edgecolor=c_blue_navy, lw=1.8, linestyle='--', zorder=7))

    # Secondary Local Refinement Orbit Paths in Phase 2
    r_loc = 2.8
    for la in [0.4, 2.0, 3.8, 5.2]:
        lx = 85.5 + r_loc * np.cos(la)
        ly = 41.0 + r_loc * 0.7 * np.sin(la)
        ax.add_patch(Circle((lx, ly), 0.3, facecolor=c_blue_border, edgecolor=c_blue_navy, lw=0.5, zorder=5))
        ax.annotate('', xy=(85.5 + 0.7*np.cos(la), 41.0 + 0.5*np.sin(la)), xytext=(lx, ly),
                    arrowprops=dict(arrowstyle='->', color=c_blue_mid, lw=0.8, mutation_scale=7), zorder=4)

    # Final Elite Solution Node (Cobalt/Navy Star & Concentrated Core)
    p_final = main_waypoints[11]
    ax.plot(p_final[0], p_final[1], marker='*', markersize=16, color=c_blue_primary, markeredgecolor=c_blue_navy, markeredgewidth=1.2, zorder=9)
    ax.text(p_final[0] + 3.2, p_final[1] + 0.4, r'$\mathbf{x}^\star\ \mathrm{Refined\ Elite\ Subset}$' + '\n' + r'(Low Error & High Sparsity)',
            fontsize=9.5, fontweight='bold', color=c_blue_navy, ha='left', va='center', zorder=9)

    # Dynamic Annotations of Behavioral Change
    ax.text(26.0, 24.5, r'$\mathbf{Broad\ Exploration}$' + '\n' + r'(Progressive feature reduction)',
            fontsize=9.5, fontstyle='italic', color=c_blue_primary, ha='center', va='center')

    ax.text(85.5, 24.5, r'$\mathbf{Focused\ Local\ Refinement}$' + '\n' + r'(Elite feature subset tuning)',
            fontsize=9.5, fontstyle='italic', color=c_blue_navy, ha='center', va='center')

    # =========================================================================
    # 5. BOTTOM CONTINUOUS MECHANISM SUMMARY STATEMENT
    # =========================================================================
    sum_y = 6.8
    ax.plot([8.0, 92.0], [12.2, 12.2], color=c_grid_line, lw=1.0, zorder=2)

    summary_items = [
        (16.0, 'Exploration', c_blue_primary),
        (33.0, 'Feature Reduction', c_blue_primary),
        (51.0, 'Weight Transition', c_blue_navy),
        (70.0, 'Accuracy Refinement', c_blue_navy),
        (88.0, 'High-Quality Compact Subset', c_blue_navy)
    ]
    for sx, stext, scol in summary_items:
        ax.text(sx, sum_y, stext, fontsize=10.5, fontweight='bold', color=scol, ha='center', va='center')

    # Connecting arrows between summary concepts
    arrow_positions = [(22.0, 25.0), (41.0, 44.0), (60.0, 63.0), (79.0, 81.5)]
    for ax_start, ax_end in arrow_positions:
        ax.annotate('', xy=(ax_end, sum_y), xytext=(ax_start, sum_y),
                    arrowprops=dict(arrowstyle='-|>', color=c_slate_line, lw=1.4, mutation_scale=10), zorder=3)

    # Save Outputs
    out_dir = 'output/figures'
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F4_tps_strategy_journal.pdf')
    png_path = os.path.join(out_dir, 'F4_tps_strategy_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated Continuous Harmonized Figure 4 PDF and PNG successfully!')

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

    # Timeline elements
    add_cell('it1', '&lt;b&gt;Iteration 1&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 60, 20, 100, 25)
    add_cell('it70', '&lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;Phase Transition: $$t = 0.70T$$&lt;/font&gt;&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 540, 20, 220, 25)
    add_cell('it100', '&lt;b&gt;Iteration 100&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 1140, 20, 120, 25)

    # Phase 1 & 2 Labels
    add_cell('p1_lbl', '&lt;b&gt;&lt;font size=\"4\" color=\"#1D4ED8\"&gt;Phase 1: Sparse Subset Exploration&lt;/font&gt;&lt;/b&gt;&lt;br&gt;$$f = \\alpha \\times \\text{Error Rate} + \\beta \\times \\text{Feature Ratio}$$&lt;br&gt;&lt;b&gt;$$\\alpha = 0.70, \\quad \\beta = 0.30$$&lt;/b&gt;&lt;br&gt;&lt;i&gt;Sparsity-oriented exploration $\\cdot$ Progressive feature reduction&lt;/i&gt;', 'text;html=1;align=left;verticalAlign=top;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 80, 80, 420, 90)
    add_cell('trans_lbl', '&lt;b&gt;&lt;font size=\"4\" color=\"#1E3A8A\"&gt;Adaptive Weight Scheduling&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;b&gt;$$(\\alpha, \\beta): (0.70, 0.30) \\longrightarrow (0.95, 0.05)$$&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=top;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 500, 80, 300, 70)
    add_cell('p2_lbl', '&lt;b&gt;&lt;font size=\"4\" color=\"#1E3A8A\"&gt;Phase 2: Accuracy Refinement&lt;/font&gt;&lt;/b&gt;&lt;br&gt;$$f = \\alpha \\times \\text{Error Rate} + \\beta \\times \\text{Feature Ratio}$$&lt;br&gt;&lt;b&gt;$$\\alpha = 0.95, \\quad \\beta = 0.05$$&lt;/b&gt;&lt;br&gt;&lt;i&gt;Accuracy-oriented refinement $\\cdot$ Elite subset fine-tuning&lt;/i&gt;', 'text;html=1;align=left;verticalAlign=top;fontSize=12;fontColor=#0F172A;fontFamily=Times New Roman;', 920, 80, 420, 90)

    # Bottom Summary
    add_cell('summary_flow', '&lt;b&gt;&lt;font color=\"#1D4ED8\"&gt;Exploration&lt;/font&gt;&lt;/b&gt;  $$\\longrightarrow$$  &lt;b&gt;&lt;font color=\"#1D4ED8\"&gt;Feature Reduction&lt;/font&gt;&lt;/b&gt;  $$\\longrightarrow$$  &lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;Weight Transition&lt;/font&gt;&lt;/b&gt;  $$\\longrightarrow$$  &lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;Accuracy Refinement&lt;/font&gt;&lt;/b&gt;  $$\\longrightarrow$$  &lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;High-Quality Compact Subset&lt;/font&gt;&lt;/b&gt;', 'text;html=1;align=center;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;', 100, 780, 1200, 30)

    out_file = 'output/figures/F4_tps_strategy_journal.drawio'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated Harmonized Figure 4 Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure4()
    generate_drawio()
