"""Publication-grade Harmonized Palette Figure 1 for KDS-EL.
Strictly adheres to Top-Tier Journal (IEEE TEVC/TCYB, Elsevier KBS) 2-Hue Color Harmony:
- Removes rainbow patchwork.
- Standardizes background cards to clean Porcelain White (#FFFFFF) & Soft Ice Slate (#F8FAFC).
- Uses semantic accent borders & typography (Cobalt Blue for PSO/Transfer, Amber for Refinement, Crimson for Re-injection).
- Preserves crystal-clear contrast while eliminating visual noise.
"""

import os
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

    # Sophisticated Harmonized Academic Palette
    c_card_bg = '#FFFFFF'         # Porcelain White
    c_container_bg = '#F8FAFC'    # Ultra-soft Slate Tint
    c_border_neutral = '#CBD5E1'  # Slate 300
    c_border_dark = '#64748B'     # Slate 500
    c_text_dark = '#0F172A'       # Slate 900
    c_text_muted = '#475569'      # Slate 600
    
    # Semantic Functional Accents
    c_navy_title = '#1E3A8A'      # Blue 900 (Main theme)
    c_blue_dark = '#1D4ED8'       # Blue 700
    c_blue_subtle = '#EFF6FF'     # Blue 50
    c_blue_border = '#93C5FD'     # Blue 300
    
    c_green_dark = '#15803D'      # Green 700 (PSO / Output)
    c_green_subtle = '#F0FDF4'    # Green 50
    c_green_border = '#86EFAC'    # Green 300
    
    c_amber_dark = '#B45309'      # Amber 700 (KER)
    c_amber_border = '#FCD34D'    # Amber 300
    
    c_crimson_dark = '#BE123C'    # Rose 700 (Re-injection)
    c_crimson_border = '#FDA4AF'  # Rose 300

    def draw_badge(x, y, w, h, bg, border, lw=1.1, r=0.5, zorder=2):
        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r}",
                             facecolor=bg, edgecolor=border, linewidth=lw, zorder=zorder)
        ax.add_patch(box)
        return box

    # =========================================================================
    # 1. TOP: INPUT & MI-PRIOR SEEDING
    # =========================================================================
    # Dataset Input
    draw_badge(8, 93.2, 84, 5.5, c_card_bg, c_border_neutral, lw=1.1, r=0.6, zorder=2)
    ax.text(50, 95.95, r'High-Dimensional Dataset $\mathbf{X}, \; \mathbf{Y}$',
            fontsize=11.0, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)

    # Down arrow
    ax.annotate('', xy=(50, 89.2), xytext=(50, 93.2),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_dark, lw=1.6, mutation_scale=11), zorder=4)

    # MI-Prior Seeding Box
    draw_badge(6, 80.5, 88, 8.2, c_blue_subtle, c_blue_border, lw=1.2, r=0.6, zorder=2)
    ax.text(50, 86.0, 'MI-Prior Seeding (Offline Bootstrap)',
            fontsize=10.5, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)
    ax.text(50, 82.6, r'Informed Prior Injection $\quad\longleftrightarrow\quad$ Stochastic Exploration',
            fontsize=8.8, color=c_text_muted, ha='center', va='center', zorder=3)

    # Fork arrows from Seeding to Subpop 1 and Subpop 2
    ax.annotate('', xy=(26, 73.0), xytext=(38, 80.5),
                arrowprops=dict(arrowstyle='-|>', color=c_green_dark, lw=1.6,
                                connectionstyle='arc3,rad=0.12', mutation_scale=11), zorder=4)
    ax.annotate('', xy=(74, 73.0), xytext=(62, 80.5),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_dark, lw=1.6,
                                connectionstyle='arc3,rad=-0.12', mutation_scale=11), zorder=4)

    # =========================================================================
    # 2. MAIN EVOLUTIONARY LOOP CONTAINER
    # =========================================================================
    loop_box = FancyBboxPatch((4.5, 14.5), 91, 59.5, boxstyle="round,pad=0.02,rounding_size=1.0",
                              facecolor=c_container_bg, edgecolor=c_border_dark, linewidth=1.3, linestyle='--', zorder=1)
    ax.add_patch(loop_box)
    ax.text(50, 71.8, r'Main Evolutionary Optimization Loop ($t = 1 \dots T$)',
            fontsize=10.8, fontweight='bold', color=c_text_dark, ha='center', va='center', zorder=3)

    # TOP OF LOOP: Cumulative Feature Importance Matrix W
    mat_x = 8.0
    mat_y = 61.0
    mat_w = 84.0
    mat_h = 9.0
    draw_badge(mat_x, mat_y, mat_w, mat_h, c_card_bg, c_border_neutral, lw=1.1, r=0.5, zorder=2)
    ax.text(mat_x + 3.5, mat_y + 6.5, r'Cumulative Feature-Importance Matrix $W$',
            fontsize=9.2, fontweight='bold', color=c_text_dark, ha='left', va='center', zorder=3)
    ax.text(mat_x + mat_w - 3.5, mat_y + 6.5, 'Dynamic Exponential Memory',
            fontsize=8.2, fontstyle='italic', color=c_navy_title, ha='right', va='center', zorder=3)
    
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
            ax.text(sx + strip_w/2, strip_y + strip_h/2, s_lbl, fontsize=7.8, fontweight='bold',
                    ha='center', va='center', color='#FFFFFF' if s_w > 0.6 else '#0F172A', zorder=5)
        else:
            ax.add_patch(patches.Rectangle((sx, strip_y), strip_w, strip_h, facecolor='#F1F5F9', edgecolor='#CBD5E1', lw=0.7, zorder=4))
            ax.text(sx + strip_w/2, strip_y + strip_h/2, s_lbl, fontsize=8.5, fontweight='bold',
                    ha='center', va='center', color='#475569', zorder=5)

    # -------------------------------------------------------------------------
    # DUAL SUBPOPULATIONS: Subpop 1 (Left) and Subpop 2 (Right)
    # -------------------------------------------------------------------------
    # Subpopulation 1: Continuous PSO (Soft Sage)
    sub1_x = 7.5
    sub1_y = 35.8
    sub1_w = 39.5
    sub1_h = 22.2
    draw_badge(sub1_x, sub1_y, sub1_w, sub1_h, c_green_subtle, c_green_border, lw=1.2, r=0.6, zorder=2)
    ax.text(sub1_x + sub1_w/2, sub1_y + 19.5, r'Subpopulation 1 ($\mathcal{P}_1$)', fontsize=9.8, fontweight='bold', color=c_green_dark, ha='center', va='center', zorder=3)
    ax.text(sub1_x + sub1_w/2, sub1_y + 16.8, 'Continuous PSO Search', fontsize=8.4, color=c_text_muted, ha='center', va='center', zorder=3)

    # Particles in Subpop 1
    p1_coords = [(15.5, 47.0), (25.5, 50.0), (37.0, 46.5), (19.0, 40.0), (31.0, 39.0)]
    for px, py in p1_coords:
        ax.add_patch(Circle((px, py), 1.2, facecolor=c_green_dark, edgecolor='#FFFFFF', lw=1.0, zorder=4))
        ax.annotate('', xy=(px + 2.5, py + 1.2), xytext=(px, py),
                    arrowprops=dict(arrowstyle='->', color='#16A34A', lw=1.5, mutation_scale=8), zorder=3)

    # Subpopulation 2: Discrete Importance Sampling (Soft Ice Blue)
    sub2_x = 53.0
    sub2_y = 35.8
    sub2_w = 39.5
    sub2_h = 22.2
    draw_badge(sub2_x, sub2_y, sub2_w, sub2_h, c_blue_subtle, c_blue_border, lw=1.2, r=0.6, zorder=2)
    ax.text(sub2_x + sub2_w/2, sub2_y + 19.5, r'Subpopulation 2 ($\mathcal{P}_2$)', fontsize=9.8, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)
    ax.text(sub2_x + sub2_w/2, sub2_y + 16.8, 'Probability-Driven Sampling', fontsize=8.4, color=c_text_muted, ha='center', va='center', zorder=3)

    # Discrete binary solution blocks in Subpop 2
    p2_coords = [(61.0, 47.0), (72.5, 50.0), (83.0, 46.5), (64.5, 40.0), (78.0, 39.0)]
    for px, py in p2_coords:
        ax.add_patch(patches.Rectangle((px - 2.2, py - 1.0), 4.4, 2.0, facecolor=c_blue_dark, edgecolor='#FFFFFF', lw=1.0, zorder=4))

    # Inter-Subpopulation Knowledge Transfer Arrow (Center)
    draw_badge(42.0, 43.5, 16.0, 7.0, c_card_bg, '#93C5FD', lw=1.1, r=0.4, zorder=4)
    ax.annotate('', xy=(sub1_x + sub1_w, 48.0), xytext=(sub2_x, 48.0),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_dark, lw=1.6, mutation_scale=10), zorder=5)
    ax.text(50.0, 45.3, r'$\mathbf{g}_{\mathrm{best},2}\ \mathrm{Transfer}$', fontsize=8.2, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=6)

    # Arrows: Subpopulations update W (Upwards) and Subpop 2 learns from W (Downwards)
    ax.annotate('', xy=(27.0, mat_y), xytext=(27.0, sub1_y + sub1_h),
                arrowprops=dict(arrowstyle='-|>', color=c_green_dark, lw=1.4, mutation_scale=9), zorder=4)
    ax.text(25.5, 59.5, 'Reward Feedback', fontsize=7.8, fontweight='bold', color=c_green_dark, ha='right', va='center')

    ax.annotate('', xy=(73.0, sub2_y + sub2_h), xytext=(73.0, mat_y),
                arrowprops=dict(arrowstyle='-|>', color=c_blue_dark, lw=1.4, mutation_scale=9), zorder=4)
    ax.text(74.5, 59.5, r'Sample from $W$', fontsize=7.8, fontweight='bold', color=c_blue_dark, ha='left', va='center')

    # -------------------------------------------------------------------------
    # CORE STRATEGY COORDINATORS (TPS & KER) - Unified Crisp Porcelain White
    # -------------------------------------------------------------------------
    # Two-Phase Objective Weight Scheduling (TPS) Badge
    tps_x = 7.5
    tps_y = 25.2
    tps_w = 39.5
    tps_h = 7.8
    draw_badge(tps_x, tps_y, tps_w, tps_h, c_card_bg, c_blue_border, lw=1.1, r=0.5, zorder=2)
    ax.text(tps_x + tps_w/2, tps_y + 5.4, 'Two-Phase Scheduling (TPS)', fontsize=8.8, fontweight='bold', color=c_navy_title, ha='center', va='center', zorder=3)
    ax.text(tps_x + tps_w/2, tps_y + 2.2, r'Pruning Phase $\;\longrightarrow\;$ Accuracy Phase', fontsize=7.6, color=c_text_muted, ha='center', va='center', zorder=3)

    # Knowledge-guided Elite Refinement (KER) Badge
    ker_x = 53.0
    ker_y = 25.2
    ker_w = 39.5
    ker_h = 7.8
    draw_badge(ker_x, ker_y, ker_w, ker_h, c_card_bg, c_amber_border, lw=1.1, r=0.5, zorder=2)
    ax.text(ker_x + ker_w/2, ker_y + 5.4, 'Elite Refinement (KER)', fontsize=8.8, fontweight='bold', color=c_amber_dark, ha='center', va='center', zorder=3)
    ax.text(ker_x + ker_w/2, ker_y + 2.2, 'Knowledge Perturbation & Greedy Update', fontsize=7.6, color=c_text_muted, ha='center', va='center', zorder=3)

    # Arrows from Subpops to TPS / KER
    ax.annotate('', xy=(tps_x + tps_w/2, tps_y + tps_h), xytext=(sub1_x + sub1_w/2, sub1_y),
                arrowprops=dict(arrowstyle='-|>', color='#94A3B8', lw=1.3, mutation_scale=9), zorder=4)
    ax.annotate('', xy=(ker_x + ker_w/2, ker_y + ker_h), xytext=(sub2_x + sub2_w/2, sub2_y),
                arrowprops=dict(arrowstyle='-|>', color='#94A3B8', lw=1.3, mutation_scale=9), zorder=4)

    # Adaptive MI Re-injection Badge (Bottom-Right) - Crisp Porcelain White with subtle Crimson tint
    draw_badge(53.0, 15.6, 39.5, 6.8, c_card_bg, c_crimson_border, lw=1.1, r=0.4, zorder=2)
    ax.text(53.0 + 19.75, 20.4, 'Adaptive MI Re-injection', fontsize=8.5, fontweight='bold', color=c_crimson_dark, ha='center', va='center', zorder=3)
    ax.text(53.0 + 19.75, 17.6, 'Stagnation-Triggered Recovery', fontsize=7.5, color='#9F1239', ha='center', va='center', zorder=3)

    # Arrow from KER to Adaptive Re-injection
    ax.annotate('', xy=(72.75, 22.4), xytext=(72.75, 25.2),
                arrowprops=dict(arrowstyle='-|>', color=c_crimson_dark, lw=1.2, mutation_scale=8), zorder=4)

    # Re-injection feedback loop back to Subpopulations
    ax.annotate('', xy=(92.5, 47.0), xytext=(92.5, 19.0),
                arrowprops=dict(arrowstyle='-|>', color=c_crimson_dark, lw=1.2,
                                connectionstyle='arc3,rad=0.35', linestyle='--', mutation_scale=8), zorder=4)

    # -------------------------------------------------------------------------
    # LEFT LOOP ARROW & UN-OCCLUDED BADGE (t <- t + 1)
    # -------------------------------------------------------------------------
    ax.annotate('', xy=(sub1_x, 48.0), xytext=(tps_x, 29.1),
                arrowprops=dict(arrowstyle='-|>', color='#64748B', lw=1.4,
                                connectionstyle='arc3,rad=-0.52', mutation_scale=9), zorder=4)
    # Badge on loop to ensure 0% text occlusion
    draw_badge(0.6, 36.8, 3.6, 6.5, c_card_bg, c_border_neutral, lw=0.8, r=0.3, zorder=5)
    ax.text(2.4, 40.05, r'$t \leftarrow t + 1$', fontsize=7.8, fontweight='bold', color='#334155', rotation=90, ha='center', va='center', zorder=6)

    # =========================================================================
    # 3. TERMINATION & OUTPUT BLOCK
    # =========================================================================
    # Down arrow from Main Loop exit to Output
    ax.annotate('', xy=(50, 8.5), xytext=(50, 14.5),
                arrowprops=dict(arrowstyle='-|>', color=c_green_dark, lw=1.8, mutation_scale=11), zorder=4)
    ax.text(54.0, 11.5, r'Termination ($t = T$)', fontsize=8.2, fontstyle='italic', color=c_green_dark, va='center')

    draw_badge(6, 1.8, 88, 6.7, c_green_subtle, c_green_border, lw=1.3, r=0.6, zorder=2)
    ax.text(50, 6.0, r'Optimal Compact Feature Subset $\mathbf{x}^\star$', fontsize=10.5, fontweight='bold',
            color=c_green_dark, ha='center', va='center', zorder=3)
    ax.text(50, 3.4, 'High Classification Accuracy & Minimal Feature Redundancy',
            fontsize=8.4, color=c_text_muted, ha='center', va='center', zorder=3)

    # Save Outputs
    out_dir = 'output/figures'
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, 'F1_architecture_journal.pdf')
    png_path = os.path.join(out_dir, 'F1_architecture_journal.png')

    plt.tight_layout()
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('Generated unified color palette Figure 1 successfully!')

def generate_drawio():
    import xml.etree.ElementTree as ET
    mxfile = ET.Element('mxfile', host='app.diagrams.net', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f1-kds-el-conceptual', name='Figure 1: KDS-EL Architecture Framework')
    model = ET.SubElement(diagram, 'mxGraphModel', dx='1000', dy='1000', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth='850', pageHeight='1100', math='1', shadow='0')
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def add_cell(cid, value, style, x, y, w, h, parent='1'):
        cell = ET.SubElement(root, 'mxCell', id=str(cid), value=str(value), style=style, parent=parent, vertex='1')
        ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})
        return cell

    add_cell('in', '&lt;b&gt;High-Dimensional Dataset&lt;/b&gt;&lt;br&gt;$$X, Y$$', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 150, 40, 400, 50)
    add_cell('s1', '&lt;b&gt;&lt;font color=\"#1E3A8A\"&gt;MI-Prior Seeding&lt;/font&gt;&lt;/b&gt;&lt;br&gt;Informed Prior &amp; Stochastic Diversity', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#93C5FD;fontFamily=Times New Roman;', 150, 110, 400, 55)
    add_cell('loop', '&lt;b&gt;Main Evolutionary Loop (t = 1..T)&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;dashed=1;fillColor=#F8FAFC;strokeColor=#64748B;fontFamily=Times New Roman;verticalAlign=top;', 120, 190, 460, 400)
    add_cell('w', '&lt;b&gt;Cumulative Feature-Importance Matrix $$W$$&lt;/b&gt;&lt;br&gt;$$f_1, f_2, f_3, \\dots, f_{D-2}, f_{D-1}, f_D$$', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;fontFamily=Times New Roman;', 150, 230, 400, 45)
    add_cell('p1', '&lt;b&gt;Subpop 1 (Continuous PSO)&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDF4;strokeColor=#86EFAC;fontFamily=Times New Roman;', 150, 300, 180, 90)
    add_cell('p2', '&lt;b&gt;Subpop 2 (Probability Sampling)&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#93C5FD;fontFamily=Times New Roman;', 370, 300, 180, 90)
    add_cell('tps', '&lt;b&gt;Two-Phase Scheduling (TPS)&lt;/b&gt;&lt;br&gt;Pruning → Accuracy', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#93C5FD;fontFamily=Times New Roman;', 150, 410, 180, 45)
    add_cell('ker', '&lt;b&gt;Elite Refinement (KER)&lt;/b&gt;&lt;br&gt;Knowledge Perturbation', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#FCD34D;fontFamily=Times New Roman;', 370, 410, 180, 45)
    add_cell('out', '&lt;b&gt;&lt;font color=\"#15803D\"&gt;Optimal Compact Feature Subset $$x^\\star$$&lt;/font&gt;&lt;/b&gt;', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FDF4;strokeColor=#86EFAC;fontFamily=Times New Roman;', 150, 610, 400, 50)

    out_file = 'output/figures/F1_architecture_journal.drawio'
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    tree = ET.ElementTree(mxfile)
    tree.write(out_file, encoding='utf-8', xml_declaration=True)
    print(f'Generated conceptual Figure 1 Draw.io XML successfully: {out_file}')

if __name__ == '__main__':
    create_figure1()
    generate_drawio()
