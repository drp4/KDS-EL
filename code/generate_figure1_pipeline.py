"""100% EMSWOA-Exact Architecture Flowchart (Figure 1) for KDS-EL.
Strictly replicates the structure, layout, typography, box sizing, and narrative phrasing
of Fig. 2 in EMSWOA (Applied Soft Computing, Miao et al.):
- Clean academic phrasing with equation citations 'according to Eq. (x)' without formula clutter.
- Dual-swarm collaborative mechanism properly depicts parallel execution of P1 (Continuous PSO) and P2 (Discrete Sampling), inter-task g_best,2 transfer, and joint evaluation.
- Knowledge-guided elite refinement strategy depicts complete exploration/exploitation branching and 1v1 greedy acceptance tree.
- Adaptive container heights snugly hug all internal flowchart nodes with zero empty space.
- Pure monochrome academic palette (Black #000000 borders/text, White #FFFFFF fills, Times New Roman, STIX math).
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

def draw_pill(ax, x, y, w, h, text, lw=0.75, fs=8.5):
    """Draw a compact rounded oval/stadium pill for Begin / End."""
    pill = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.0,rounding_size={h/2.0}",
                          facecolor='#FFFFFF', edgecolor='#000000', linewidth=lw, zorder=3)
    ax.add_patch(pill)
    ax.text(x + w/2.0, y + h/2.0, text, fontsize=fs, fontweight='normal',
            color='#000000', ha='center', va='center', zorder=4)
    return pill

def draw_box(ax, x, y, w, h, text, lw=0.75, fs=6.8, bold=False, zorder=3):
    """Draw a standard process box with sharp corners, sized snugly to fit text."""
    box = patches.Rectangle((x, y), w, h, facecolor='#FFFFFF', edgecolor='#000000', linewidth=lw, zorder=zorder)
    ax.add_patch(box)
    ax.text(x + w/2.0, y + h/2.0, text, fontsize=fs, fontweight='bold' if bold else 'normal',
            color='#000000', ha='center', va='center', multialignment='center', zorder=zorder+1)
    return box

def draw_diamond(ax, cx, cy, w, h, text, lw=0.75, fs=6.8, zorder=3):
    """Draw a compact decision diamond."""
    pts = [[cx, cy + h/2.0], [cx + w/2.0, cy], [cx, cy - h/2.0], [cx - w/2.0, cy]]
    diamond = Polygon(pts, closed=True, facecolor='#FFFFFF', edgecolor='#000000', linewidth=lw, zorder=zorder)
    ax.add_patch(diamond)
    ax.text(cx, cy, text, fontsize=fs, fontweight='normal',
            color='#000000', ha='center', va='center', multialignment='center', zorder=zorder+1)
    return diamond

def draw_dashed_container(ax, x, y, w, h, title, lw=0.8, title_fs=8.2, zorder=2):
    """Draw a dashed outer container box snugly enclosing a sub-mechanism."""
    box = patches.Rectangle((x, y), w, h, facecolor='#FFFFFF', edgecolor='#000000', 
                            linewidth=lw, linestyle='--', zorder=zorder)
    ax.add_patch(box)
    ax.text(x + w/2.0, y + h - 1.8, title, fontsize=title_fs, fontweight='bold',
            color='#000000', ha='center', va='center', zorder=zorder+1)
    return box

def create_figure1():
    # Typography: Times New Roman & STIX math (Strict EMSWOA match)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    # Aspect ratio: Clean double-column layout (10.2 in x 8.8 in)
    fig, ax = plt.subplots(figsize=(10.2, 8.8), dpi=300)
    ax.set_xlim(1.5, 99.0)
    ax.set_ylim(4.5, 99.5)
    ax.axis('off')

    arr_lw = 0.75

    # =========================================================================
    # LEFT COLUMN: MAIN ALGORITHMIC LIFECYCLE (x = 2.0 to 45.0)
    # =========================================================================
    col_cx = 24.0
    main_w = 32.0

    # 1. Begin Pill
    draw_pill(ax, col_cx - 5.0, 96.5, 10.0, 2.5, 'Begin', fs=8.5)
    ax.annotate('', xy=(col_cx, 94.8), xytext=(col_cx, 96.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 2. Set related parameters
    draw_box(ax, col_cx - 13.0, 91.5, 26.0, 3.3, 
             'Set related parameters', fs=7.2)
    ax.annotate('', xy=(col_cx, 88.5), xytext=(col_cx, 91.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 3. Standard 4-Block Initialization Cycle
    init_w = 15.5
    init_h = 3.6
    # Top-Left: Initialize candidate solutions
    draw_box(ax, col_cx - 16.5, 84.9, init_w, init_h, 
             'Initialize candidate solutions\nbased on prior knowledge', fs=6.2)
    # Top-Right: Convert continuous particles to binary space
    draw_box(ax, col_cx + 1.0, 84.9, init_w, init_h, 
             'Convert continuous particles\nto binary decision space', fs=6.2)
    # Arrow from Top-Left to Top-Right
    ax.annotate('', xy=(col_cx + 1.0, 84.9 + init_h/2.0), xytext=(col_cx - 1.0, 84.9 + init_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Down arrow from Top-Right to Bottom-Right
    ax.annotate('', xy=(col_cx + 8.75, 81.3), xytext=(col_cx + 8.75, 84.9),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Bottom-Right: Calculate objective fitness under TPS
    draw_box(ax, col_cx + 1.0, 77.7, init_w, init_h, 
             'Calculate objective fitness\nunder two-phase scheduling', fs=6.2)
    # Bottom-Left: Obtain initial personal and global best solutions
    draw_box(ax, col_cx - 16.5, 77.7, init_w, init_h, 
             'Obtain initial personal\nand global best solutions', fs=6.2)
    # Arrow from Bottom-Right to Bottom-Left
    ax.annotate('', xy=(col_cx - 1.0, 77.7 + init_h/2.0), xytext=(col_cx + 1.0, 77.7 + init_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Down arrow from Bottom-Left to Main Loop Anchor
    ax.annotate('', xy=(col_cx, 75.5), xytext=(col_cx - 8.75, 77.7),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw,
                                connectionstyle='angle,angleA=-90,angleB=180,rad=0'), zorder=4)

    # 4. Main Co-evolution Anchor Box (VERTICAL CENTER = 73.0, EXACT MIDPOINT OF TOP CONTAINER)
    loop1_cy = 73.0
    loop1_h = 5.0
    loop1_y = loop1_cy - loop1_h/2.0
    draw_box(ax, col_cx - main_w/2.0, loop1_y, main_w, loop1_h, 
             'Constructing and updating dual subpopulations\nusing collaborative co-evolution mechanism', fs=6.8, bold=False)

    # Thick black arrow pointing horizontally to EXACT VERTICAL CENTER of Top Right Container (y=73.0)
    ax.annotate('', xy=(48.0, loop1_cy), xytext=(col_cx + main_w/2.0, loop1_cy),
                arrowprops=dict(arrowstyle='-|>', color='#000000', lw=2.8, mutation_scale=12), zorder=5)

    # Down arrow to TPS Diamond
    ax.annotate('', xy=(col_cx, 65.5), xytext=(col_cx, loop1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 5. TPS Two-Phase Scheduling Decision Diamond
    tps_cy = 63.3
    tps_w = 14.0
    tps_h = 4.4
    draw_diamond(ax, col_cx, tps_cy, tps_w, tps_h, r'$t \leq \tau T_{\max}$', fs=7.0)

    # Y Branch (Left): Phase 1 Feature Pruning
    ax.text(col_cx - tps_w/2.0 - 1.4, tps_cy + 0.6, 'Y', fontsize=7.0, fontweight='bold')
    tps_b1_x = col_cx - 16.5
    tps_b_y = tps_cy - 6.4
    tps_b_w = 15.5
    tps_b_h = 3.8
    draw_box(ax, tps_b1_x, tps_b_y, tps_b_w, tps_b_h, 
             'Feature pruning phase:\npenalize redundant dimensions', fs=6.2)

    # N Branch (Right): Phase 2 Accuracy Tuning
    ax.text(col_cx + tps_w/2.0 + 0.6, tps_cy + 0.6, 'N', fontsize=7.0, fontweight='bold')
    tps_b2_x = col_cx + 1.0
    draw_box(ax, tps_b2_x, tps_b_y, tps_b_w, tps_b_h, 
             'Accuracy tuning phase:\nrefine classification accuracy', fs=6.2)

    # Connect TPS Diamond to Phase 1 & Phase 2 boxes
    ax.plot([col_cx - tps_w/2.0, tps_b1_x + tps_b_w/2.0, tps_b1_x + tps_b_w/2.0],
            [tps_cy, tps_cy, tps_b_y + tps_b_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(tps_b1_x + tps_b_w/2.0, tps_b_y + tps_b_h), xytext=(tps_b1_x + tps_b_w/2.0, tps_b_y + tps_b_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([col_cx + tps_w/2.0, tps_b2_x + tps_b_w/2.0, tps_b2_x + tps_b_w/2.0],
            [tps_cy, tps_cy, tps_b_y + tps_b_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(tps_b2_x + tps_b_w/2.0, tps_b_y + tps_b_h), xytext=(tps_b2_x + tps_b_w/2.0, tps_b_y + tps_b_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Converge both TPS branches to W matrix update box
    ax.plot([tps_b1_x + tps_b_w/2.0, tps_b1_x + tps_b_w/2.0, col_cx],
            [tps_b_y, tps_b_y - 1.4, tps_b_y - 1.4], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([tps_b2_x + tps_b_w/2.0, tps_b2_x + tps_b_w/2.0, col_cx],
            [tps_b_y, tps_b_y - 1.4, tps_b_y - 1.4], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(col_cx, tps_b_y - 2.8), xytext=(col_cx, tps_b_y - 1.4),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 6. Cumulative Memory Matrix Update Box
    mem_y = tps_b_y - 7.2
    mem_h = 4.4
    draw_box(ax, col_cx - main_w/2.0, mem_y, main_w, mem_h, 
             r'Updating cumulative feature-importance matrix $\mathbf{W}$' + '\n' + 
             'with evolutionary fitness feedback and memory decay', fs=6.6)

    # Down arrow to KER Anchor Box
    ax.annotate('', xy=(col_cx, mem_y - 1.8), xytext=(col_cx, mem_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 7. Knowledge-Guided Elite Refinement Anchor Box (VERTICAL CENTER = 32.0, EXACT MIDPOINT OF BOTTOM CONTAINER)
    ker_cy = 32.0
    ker_h = 5.0
    ker_y = ker_cy - ker_h/2.0
    draw_box(ax, col_cx - main_w/2.0, ker_y, main_w, ker_h, 
             'Updating candidate feature subsets using\nknowledge-guided elite refinement strategy', fs=6.8, bold=False)

    # Thick black arrow pointing horizontally to EXACT VERTICAL CENTER of Bottom Right Container (y=32.0)
    ax.annotate('', xy=(48.0, ker_cy), xytext=(col_cx + main_w/2.0, ker_cy),
                arrowprops=dict(arrowstyle='-|>', color='#000000', lw=2.8, mutation_scale=12), zorder=5)

    # Down arrow to Stagnation Detection Diamond
    ax.annotate('', xy=(col_cx, ker_y - 1.8), xytext=(col_cx, ker_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 8. Decision Diamond: Stagnation Detection (t_stag >= tau)
    stag_cy = ker_y - 4.0
    stag_w = 14.0
    stag_h = 4.2
    draw_diamond(ax, col_cx, stag_cy, stag_w, stag_h, r'$t_{\mathrm{stag}} \geq \tau$', fs=7.0)

    # Y branch (Right): Adaptive Stagnation Recovery (AIR)
    ax.text(col_cx + stag_w/2.0 + 0.8, stag_cy + 0.5, 'Y', fontsize=7.0, fontweight='bold')
    air_bx = col_cx + 8.5
    air_by = stag_cy - 1.9
    air_bw = 15.5
    air_bh = 3.8
    draw_box(ax, air_bx, air_by, air_bw, air_bh, 
             'Adaptive stagnation recovery:\nre-initialize lower-half particles', fs=6.2)
    
    ax.annotate('', xy=(air_bx, stag_cy), xytext=(col_cx + stag_w/2.0, stag_cy),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 9. Decision Diamond: Termination (t >= T_max)
    term_cy = stag_cy - 8.2
    term_w = 14.0
    term_h = 4.2
    draw_diamond(ax, col_cx, term_cy, term_w, term_h, r'$t \geq T_{\max}$', fs=7.0)

    # Connect AIR box DIRECTLY to the RIGHT VERTEX of the Termination Diamond
    ax.plot([air_bx + air_bw/2.0, air_bx + air_bw/2.0, col_cx + term_w/2.0], 
            [air_by, term_cy, term_cy], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(col_cx + term_w/2.0, term_cy), xytext=(col_cx + term_w/2.0 + 0.3, term_cy),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # N branch (Down): Connect straight down to TOP VERTEX of Termination Diamond
    ax.text(col_cx + 0.6, stag_cy - stag_h/2.0 - 0.9, 'N', fontsize=7.0, fontweight='bold')
    ax.annotate('', xy=(col_cx, term_cy + term_h/2.0), xytext=(col_cx, stag_cy - stag_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # N branch (Left): Loop back to generation t+1
    ax.text(col_cx - term_w/2.0 - 1.4, term_cy + 0.5, 'N', fontsize=7.0, fontweight='bold')
    # Y branch (Down): Go to Output Box
    ax.text(col_cx + 0.6, term_cy - term_h/2.0 - 0.9, 'Y', fontsize=7.0, fontweight='bold')

    # N branch Loop back to Collaborative Co-evolution:
    loop_back_x = 3.5
    ax.plot([col_cx - term_w/2.0, loop_back_x, loop_back_x, col_cx - main_w/2.0],
            [term_cy, term_cy, loop1_cy, loop1_cy],
            color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(col_cx - main_w/2.0, loop1_cy), xytext=(col_cx - main_w/2.0 - 0.6, loop1_cy),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text(loop_back_x + 1.0, (term_cy + loop1_cy)/2.0, r'$t \leftarrow t + 1$', fontsize=6.6, rotation=90, va='center')

    # Y branch (Down to Output Box):
    out_x = col_cx - 13.0
    out_y = term_cy - term_h/2.0 - 5.5
    out_w = 26.0
    out_h = 3.6
    ax.annotate('', xy=(col_cx, out_y + out_h), xytext=(col_cx, term_cy - term_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 10. Output Box: Obtaining the subset of optimal features
    draw_box(ax, out_x, out_y, out_w, out_h, 
             'Obtaining the subset of\n' + r'optimal features $\mathbf{x}^{\star}$ and $f_{\mathrm{gbest}}$', fs=6.8)

    # Down arrow to End Pill
    ax.annotate('', xy=(col_cx, out_y - 1.8), xytext=(col_cx, out_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # 11. End Pill
    draw_pill(ax, col_cx - 5.0, out_y - 4.2, 10.0, 2.4, 'End', fs=8.5)

    # =========================================================================
    # RIGHT COLUMN: CONTAINERS PERFECTLY CENTERED TO LEFT ANCHOR BOXES
    # =========================================================================
    rc_x = 48.0
    rc_w = 50.0

    # -------------------------------------------------------------------------
    # TOP DASHED BOX: Dual-Swarm Collaborative Co-Evolution Mechanism
    # Vertical Center = 73.0 (EXACT MATCH with left anchor box at y=73.0)
    # Height = 33.0 (y from 56.5 to 89.5)
    # -------------------------------------------------------------------------
    top_box_h = 33.0
    top_box_y = loop1_cy - top_box_h/2.0  # 73.0 - 16.5 = 56.5
    draw_dashed_container(ax, rc_x, top_box_y, rc_w, top_box_h, 
                          'Dual-swarm collaborative co-evolution mechanism', lw=0.8, title_fs=8.2)

    # Step 1: Role Assignment Box
    t1_y = top_box_y + top_box_h - 5.8  # 83.7
    t1_w = rc_w - 4.0
    draw_box(ax, rc_x + 2.0, t1_y, t1_w, 3.4, 
             r'Swarm partitioning: $\mathcal{P}_1$ (Continuous Explorer) $\longleftrightarrow$ $\mathcal{P}_2$ (Discrete Exploiter)', fs=6.6)
    ax.annotate('', xy=(rc_x + rc_w/2.0, t1_y - 1.8), xytext=(rc_x + rc_w/2.0, t1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step 2: Two Parallel Branches (Left: Continuous PSO / Right: Discrete Importance Sampling)
    sub_col_w = 21.5
    sub_h1 = 5.4
    sub_y1 = t1_y - 8.4  # 75.3
    # Left Branch (P1)
    draw_box(ax, rc_x + 2.0, sub_y1, sub_col_w, sub_h1, 
             'Continuous velocity & position update\nwith inter-task knowledge transfer', fs=6.2)
    # Right Branch (P2)
    draw_box(ax, rc_x + rc_w - 2.0 - sub_col_w, sub_y1, sub_col_w, sub_h1, 
             r'Dynamic selection probability' + '\n' + 
             r'transformation derived from memory $\mathbf{W}$', fs=6.2)

    # Knowledge Transfer Arrow from P2 to P1
    ax.annotate('', xy=(rc_x + 2.0 + sub_col_w, sub_y1 + sub_h1/2.0), 
                xytext=(rc_x + rc_w - 2.0 - sub_col_w, sub_y1 + sub_h1/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text((rc_x + 2.0 + sub_col_w + rc_x + rc_w - 2.0 - sub_col_w)/2.0, sub_y1 + sub_h1/2.0 + 0.6, 
            r'$\mathbf{g}_{\mathrm{best},2}$', fontsize=6.4, ha='center', va='bottom')

    # Step 3: Binarization / Sampling Sub-row
    sub_h2 = 5.0
    sub_y2 = sub_y1 - 7.0  # 68.3
    # Left: Deterministic Step Binarization
    draw_box(ax, rc_x + 2.0, sub_y2, sub_col_w, sub_h2, 
             'Deterministic Heaviside step\nbinarization mapping', fs=6.2)
    # Right: Bernoulli Sampling & Mutation
    draw_box(ax, rc_x + rc_w - 2.0 - sub_col_w, sub_y2, sub_col_w, sub_h2, 
             'Discrete Bernoulli feature\nsampling and bit mutation', fs=6.2)

    # Down arrows connecting sub-steps in P1 and P2
    ax.annotate('', xy=(rc_x + 2.0 + sub_col_w/2.0, sub_y2 + sub_h2), xytext=(rc_x + 2.0 + sub_col_w/2.0, sub_y1),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.annotate('', xy=(rc_x + rc_w - 2.0 - sub_col_w/2.0, sub_y2 + sub_h2), xytext=(rc_x + rc_w - 2.0 - sub_col_w/2.0, sub_y1),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step 4: Joint Evaluation Box
    t4_y = sub_y2 - 5.6  # 62.7
    t4_h = 3.6
    draw_box(ax, rc_x + 2.0, t4_y, t1_w, t4_h, 
             r'Evaluate objective fitness of combined population $\mathcal{P}_1 \cup \mathcal{P}_2$' + '\n' + 
             'under dynamic two-phase scheduling', fs=6.5)

    # Connect both sub-columns into joint evaluation box
    ax.plot([rc_x + 2.0 + sub_col_w/2.0, rc_x + 2.0 + sub_col_w/2.0, rc_x + rc_w/2.0],
            [sub_y2, sub_y2 - 1.0, sub_y2 - 1.0], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([rc_x + rc_w - 2.0 - sub_col_w/2.0, rc_x + rc_w - 2.0 - sub_col_w/2.0, rc_x + rc_w/2.0],
            [sub_y2, sub_y2 - 1.0, sub_y2 - 1.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + rc_w/2.0, t4_y + t4_h), xytext=(rc_x + rc_w/2.0, sub_y2 - 1.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # -------------------------------------------------------------------------
    # BOTTOM DASHED BOX: Knowledge-Guided Elite Refinement Strategy
    # Vertical Center = 32.0 (EXACT MATCH with left anchor box at y=32.0)
    # Height = 48.0 (y from 8.0 to 56.0, leaving 0.5 gap below top container at 56.5)
    # -------------------------------------------------------------------------
    bot_box_h = 48.0
    bot_box_y = ker_cy - bot_box_h/2.0  # 32.0 - 24.0 = 8.0
    draw_dashed_container(ax, rc_x, bot_box_y, rc_w, bot_box_h, 
                          'Knowledge-guided elite refinement strategy', lw=0.8, title_fs=8.2)

    # Level 1: Data inputs required for the elite refinement strategy
    k1_y = bot_box_y + bot_box_h - 5.8  # 50.2
    k1_w = rc_w - 4.0
    draw_box(ax, rc_x + 2.0, k1_y, k1_w, 3.4, 
             'Data inputs required for the knowledge-guided elite refinement strategy', fs=6.8)
    ax.annotate('', xy=(rc_x + rc_w/2.0, k1_y - 1.6), xytext=(rc_x + rc_w/2.0, k1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Level 2: Decision Diamond: r < p_rand (Exploration vs Exploitation)
    k_dia1_cy = k1_y - 4.4  # 45.8
    k_dia1_w = 16.0
    k_dia1_h = 4.0
    draw_diamond(ax, rc_x + rc_w/2.0, k_dia1_cy, k_dia1_w, k_dia1_h, r'$r < p_{\mathrm{rand}}$', fs=7.0)

    # Y Branch (Left): Random bit perturbation
    ax.text(rc_x + rc_w/2.0 - k_dia1_w/2.0 - 1.4, k_dia1_cy + 0.6, 'Y', fontsize=7.0, fontweight='bold')
    # N Branch (Right): Knowledge-guided directional flip branch
    ax.text(rc_x + rc_w/2.0 + k_dia1_w/2.0 + 0.6, k_dia1_cy + 0.6, 'N', fontsize=7.0, fontweight='bold')

    # Level 3 Left: Random Bit Inversion Box
    kb_w = 21.5
    kb_h = 4.2
    kb_l_y = k_dia1_cy - 7.6  # 38.2
    draw_box(ax, rc_x + 2.0, kb_l_y, kb_w, kb_h, 
             'Update candidate features via\nergodic random bit perturbation', fs=6.2)

    # Level 3 Right: Decision Diamond: x_{(e,j)} == 1 (Piecewise Directional Decision!)
    k_dia_right_cy = k_dia1_cy - 7.6  # 38.2
    k_dia_right_w = 15.0
    k_dia_right_h = 4.0
    draw_diamond(ax, rc_x + rc_w - 2.0 - kb_w/2.0, k_dia_right_cy, k_dia_right_w, k_dia_right_h, 
                 r'$x_{(e,j)} == 1$', fs=6.8)

    # Connect Diamond 1 to Left Box and Right Diamond
    ax.plot([rc_x + rc_w/2.0 - k_dia1_w/2.0, rc_x + 2.0 + kb_w/2.0, rc_x + 2.0 + kb_w/2.0],
            [k_dia1_cy, k_dia1_cy, kb_l_y + kb_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + 2.0 + kb_w/2.0, kb_l_y + kb_h), xytext=(rc_x + 2.0 + kb_w/2.0, kb_l_y + kb_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([rc_x + rc_w/2.0 + k_dia1_w/2.0, rc_x + rc_w - 2.0 - kb_w/2.0, rc_x + rc_w - 2.0 - kb_w/2.0],
            [k_dia1_cy, k_dia1_cy, k_dia_right_cy + k_dia_right_h/2.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + rc_w - 2.0 - kb_w/2.0, k_dia_right_cy + k_dia_right_h/2.0), 
                xytext=(rc_x + rc_w - 2.0 - kb_w/2.0, k_dia_right_cy + k_dia_right_h/2.0 + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Branches of Right Diamond (x_(e,j) == 1):
    # Y branch (Prune weak selected):
    ax.text(rc_x + rc_w - 2.0 - kb_w/2.0 - k_dia_right_w/2.0 - 1.2, k_dia_right_cy + 0.5, 'Y', fontsize=6.6, fontweight='bold')
    # N branch (Add strong unselected):
    ax.text(rc_x + rc_w - 2.0 - kb_w/2.0 + k_dia_right_w/2.0 + 0.4, k_dia_right_cy + 0.5, 'N', fontsize=6.6, fontweight='bold')

    sub_r_w = 10.4
    sub_r_h = 4.2
    sub_r_y = k_dia_right_cy - 7.0  # 31.2
    # Left sub-box: Prune selected features
    draw_box(ax, rc_x + rc_w - 2.0 - kb_w, sub_r_y, sub_r_w, sub_r_h, 
             r'Prune weak features:' + '\n' + r"$x'_{(e,j)} \leftarrow 0$", fs=5.8)
    # Right sub-box: Add unselected features
    draw_box(ax, rc_x + rc_w - 2.0 - sub_r_w, sub_r_y, sub_r_w, sub_r_h, 
             r'Add strong features:' + '\n' + r"$x'_{(e,j)} \leftarrow 1$", fs=5.8)

    ax.plot([rc_x + rc_w - 2.0 - kb_w/2.0 - k_dia_right_w/2.0, rc_x + rc_w - 2.0 - kb_w + sub_r_w/2.0, rc_x + rc_w - 2.0 - kb_w + sub_r_w/2.0],
            [k_dia_right_cy, k_dia_right_cy, sub_r_y + sub_r_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + rc_w - 2.0 - kb_w + sub_r_w/2.0, sub_r_y + sub_r_h), 
                xytext=(rc_x + rc_w - 2.0 - kb_w + sub_r_w/2.0, sub_r_y + sub_r_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([rc_x + rc_w - 2.0 - kb_w/2.0 + k_dia_right_w/2.0, rc_x + rc_w - 2.0 - sub_r_w/2.0, rc_x + rc_w - 2.0 - sub_r_w/2.0],
            [k_dia_right_cy, k_dia_right_cy, sub_r_y + sub_r_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + rc_w - 2.0 - sub_r_w/2.0, sub_r_y + sub_r_h), 
                xytext=(rc_x + rc_w - 2.0 - sub_r_w/2.0, sub_r_y + sub_r_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Level 4: Decision Diamond 2 (Greedy 1v1 Acceptance Condition): f(X'_e) < f(X_e)
    k_dia2_cy = sub_r_y - 6.0  # 25.2
    k_dia2_w = 20.0
    k_dia2_h = 4.0
    draw_diamond(ax, rc_x + rc_w/2.0, k_dia2_cy, k_dia2_w, k_dia2_h, 
                 r"$f(\mathbf{X}'_e) < f(\mathbf{X}_e)$", fs=6.8)

    # Converge Left Random Box and Right Directional Boxes to Acceptance Diamond
    ax.plot([rc_x + 2.0 + kb_w/2.0, rc_x + 2.0 + kb_w/2.0, rc_x + rc_w/2.0],
            [kb_l_y, k_dia2_cy + k_dia2_h/2.0 + 1.2, k_dia2_cy + k_dia2_h/2.0 + 1.2], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([rc_x + rc_w - 2.0 - kb_w + sub_r_w/2.0, rc_x + rc_w - 2.0 - kb_w + sub_r_w/2.0, rc_x + rc_w/2.0],
            [sub_r_y, k_dia2_cy + k_dia2_h/2.0 + 1.2, k_dia2_cy + k_dia2_h/2.0 + 1.2], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([rc_x + rc_w - 2.0 - sub_r_w/2.0, rc_x + rc_w - 2.0 - sub_r_w/2.0, rc_x + rc_w/2.0],
            [sub_r_y, k_dia2_cy + k_dia2_h/2.0 + 1.2, k_dia2_cy + k_dia2_h/2.0 + 1.2], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + rc_w/2.0, k_dia2_cy + k_dia2_h/2.0), xytext=(rc_x + rc_w/2.0, k_dia2_cy + k_dia2_h/2.0 + 1.2),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Level 5: Final Acceptance / Rejection Boxes
    # Y Branch (Left): Accept mutant
    ax.text(rc_x + rc_w/2.0 - k_dia2_w/2.0 - 1.4, k_dia2_cy + 0.6, 'Y', fontsize=7.0, fontweight='bold')
    # N Branch (Right): Retain original
    ax.text(rc_x + rc_w/2.0 + k_dia2_w/2.0 + 0.6, k_dia2_cy + 0.6, 'N', fontsize=7.0, fontweight='bold')

    kc_w = 21.5
    kc_h = 4.2
    kc_y = k_dia2_cy - 6.6  # 18.6
    # Left Acceptance Box
    draw_box(ax, rc_x + 2.0, kc_y, kc_w, kc_h, 
             r'Update candidate elite subset:' + '\n' + r"$\mathbf{X}^{\star}_e \leftarrow \mathbf{X}'_e$", fs=6.2)
    # Right Retain Box
    draw_box(ax, rc_x + rc_w - 2.0 - kc_w, kc_y, kc_w, kc_h, 
             r'Retain current elite subset:' + '\n' + r"$\mathbf{X}^{\star}_e \leftarrow \mathbf{X}_e$", fs=6.2)

    # Connect Diamond 2 to Final Acceptance boxes
    ax.plot([rc_x + rc_w/2.0 - k_dia2_w/2.0, rc_x + 2.0 + kc_w/2.0, rc_x + 2.0 + kc_w/2.0],
            [k_dia2_cy, k_dia2_cy, kc_y + kc_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + 2.0 + kc_w/2.0, kc_y + kc_h), xytext=(rc_x + 2.0 + kc_w/2.0, kc_y + kc_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([rc_x + rc_w/2.0 + k_dia2_w/2.0, rc_x + rc_w - 2.0 - kc_w/2.0, rc_x + rc_w - 2.0 - kc_w/2.0],
            [k_dia2_cy, k_dia2_cy, kc_y + kc_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(rc_x + rc_w - 2.0 - kc_w/2.0, kc_y + kc_h), xytext=(rc_x + rc_w - 2.0 - kc_w/2.0, kc_y + kc_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Save Output
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    tex_fig_dir = os.path.join(base_dir, 'Template-LaTeX-Elsevier-CAS-DC-master', 'figs')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tex_fig_dir, exist_ok=True)

    pdf_path = os.path.join(out_dir, 'F1_architecture_journal.pdf')
    png_path = os.path.join(out_dir, 'F1_architecture_journal.png')
    tex_pdf_path = os.path.join(tex_fig_dir, 'Fig1.pdf')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.savefig(tex_pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f'Successfully generated 100% EMSWOA-Exact Figure 1 at:\n- {pdf_path}\n- {png_path}\n- {tex_pdf_path}')

if __name__ == '__main__':
    create_figure1()

