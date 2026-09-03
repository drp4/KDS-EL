"""Publication-grade Figure 4: Knowledge-Guided Elite Refinement (KER) Strategy.
Designed specifically for Single-Column format (width: ~8.5 cm, ~3.35 in).
Eliminates double-column billboard monotony in Section 4.
Pure academic engineering matrix/vector transformation with 100% EMSWOA-grade crisp aesthetics.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_figure4_single_column():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    # Single-column dimensions: 5.2 x 6.4 inches (scaled to single column ~8.5 cm)
    fig_w, fig_h = 5.2, 6.4
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 125)
    ax.axis('off')

    # Color definitions
    c_grid_line = '#64748B'
    c_text = '#000000'
    c_blue_text = '#0284C7'
    c_red_text = '#DC2626'
    c_green_text = '#059669'
    c_strategy_box = '#BAE6FD'      # Soft light cyan (exact EMSWOA style)
    c_row_shade_purple = '#EEF2FF'  # Soft purple/lavender for x_best
    c_row_shade_grey = '#F8FAFC'
    c_add_bg = '#DCFCE7'
    c_prune_bg = '#FEE2E2'

    def draw_vector(x0, y0, cols, cell_w, cell_h, data,
                    row_bg='#FFFFFF', text_colors=None, is_dotted=False,
                    box_border='#000000', cell_bgs=None):
        """Draw a single-row vector grid."""
        vec_w = cols * cell_w
        # Outer border
        outer = patches.Rectangle((x0, y0), vec_w, cell_h,
                                  facecolor='none', edgecolor=box_border, lw=0.8, zorder=3)
        ax.add_patch(outer)

        for c in range(cols):
            cx = x0 + c * cell_w
            bg_c = cell_bgs[c] if (cell_bgs and c < len(cell_bgs) and cell_bgs[c]) else row_bg
            if bg_c != '#FFFFFF':
                cell_bg = patches.Rectangle((cx, y0), cell_w, cell_h,
                                            facecolor=bg_c, edgecolor='none', zorder=1)
                ax.add_patch(cell_bg)

            # Divider
            if c > 0:
                style_line = ':' if is_dotted else '-'
                ax.plot([cx, cx], [y0, y0 + cell_h],
                        color=c_grid_line, lw=0.5, linestyle=style_line, zorder=2)

            val = data[c]
            t_color = c_text
            t_weight = 'normal'
            if text_colors and c in text_colors:
                t_color = text_colors[c][0]
                t_weight = text_colors[c][1]

            ax.text(cx + cell_w / 2, y0 + cell_h / 2, str(val),
                    fontsize=8.0, color=t_color, fontweight=t_weight,
                    ha='center', va='center', zorder=4)

    def draw_arrow_down(x, y_start, y_end, label=None):
        """Draw a neat downward arrow with optional side label."""
        ax.annotate('', xy=(x, y_end), xytext=(x, y_start),
                    arrowprops=dict(arrowstyle="->", color="#000000", lw=0.9))
        if label:
            ax.text(x + 1.5, (y_start + y_end) / 2, label,
                    fontsize=7.8, color="#000000", va='center', ha='left')

    # Grid parameters
    cols = 8
    cell_w = 9.5
    cell_h = 7.0
    x_start = 18.0
    feats = [r'$f_1$', r'$f_2$', r'$f_3$', r'$f_4$', r'$f_5$', r'$f_6$', r'$\cdots$', r'$f_D$']

    # -------------------------------------------------------------
    # 1. TOP: Column Headers & Inputs
    # -------------------------------------------------------------
    y_feats = 118.0
    for c in range(cols):
        ax.text(x_start + c * cell_w + cell_w / 2, y_feats, feats[c],
                fontsize=7.8, color='#334155', ha='center', va='bottom')

    # Row 1: Elite solution x_e
    y_xe = 108.0
    ax.text(x_start - 2.0, y_xe + cell_h / 2, r'$\mathbf{x}_e$:',
            fontsize=8.5, fontweight='bold', color='#000000', ha='right', va='center')
    xe_data = [0, 0, 1, 0, 1, 0, r'$\dots$', 0]
    draw_vector(x_start, y_xe, cols, cell_w, cell_h, xe_data,
                row_bg=c_row_shade_purple)

    # Row 2: Importance Memory W
    y_w = 98.0
    ax.text(x_start - 2.0, y_w + cell_h / 2, r'$\mathbf{W}$:',
            fontsize=8.5, fontweight='bold', color='#000000', ha='right', va='center')
    w_data = ['+0.4', '+3.8', '-2.1', '-0.1', '+4.2', '+0.1', r'$\dots$', '-0.0']
    w_tcolors = {
        1: (c_green_text, 'bold'),
        2: (c_red_text, 'bold'),
        4: (c_blue_text, 'normal')
    }
    draw_vector(x_start, y_w, cols, cell_w, cell_h, w_data,
                row_bg=c_row_shade_grey, text_colors=w_tcolors, is_dotted=True)

    # -------------------------------------------------------------
    # 2. CENTER: KER Directional Scoring Operator Box
    # -------------------------------------------------------------
    draw_arrow_down(x_start + 4 * cell_w, y_w - 0.5, y_w - 6.5)

    y_strat = 75.0
    strat_h = 16.0
    strat_w = 8 * cell_w
    r_strat = patches.Rectangle((x_start, y_strat), strat_w, strat_h,
                                facecolor=c_strategy_box, edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_strat)

    ax.text(x_start + strat_w / 2, y_strat + strat_h - 4.2,
            r'Knowledge-Guided Elite Refinement (KER)',
            fontsize=8.5, fontweight='bold', color='#000000', ha='center', va='center', zorder=5)
    ax.text(x_start + strat_w / 2, y_strat + 4.5,
            r'Directional Score: $\sigma_j = (1 - 2x_{e,j}) \cdot W_j$',
            fontsize=8.2, color='#000000', ha='center', va='center', zorder=5)

    draw_arrow_down(x_start + 4 * cell_w, y_strat - 0.5, y_strat - 6.5)

    # Row 3: Directional Flip Score sigma
    y_sig = 55.0
    ax.text(x_start - 2.0, y_sig + cell_h / 2, r'$\boldsymbol{\sigma}$:',
            fontsize=8.5, fontweight='bold', color='#000000', ha='right', va='center')
    sig_data = ['+0.4', '+3.8', '+2.1', '-0.1', '-4.2', '+0.1', r'$\dots$', '-0.0']
    sig_tcolors = {
        1: (c_green_text, 'bold'),
        2: (c_red_text, 'bold'),
        4: ('#64748B', 'normal')
    }
    sig_bgs = [None, c_add_bg, c_prune_bg, None, None, None, None, None]
    draw_vector(x_start, y_sig, cols, cell_w, cell_h, sig_data,
                row_bg='#FFFFFF', text_colors=sig_tcolors, cell_bgs=sig_bgs, is_dotted=True)

    # Annotated action tags (vertically staggered to guarantee zero overlap)
    ax.text(x_start + 1.5 * cell_w - 0.5, y_sig - 3.5,
            r'Directional Add ($0 \rightarrow 1$)',
            fontsize=7.0, fontweight='bold', color=c_green_text, ha='center', va='top')
    ax.text(x_start + 2.5 * cell_w + 3.0, y_sig - 8.0,
            r'Directional Prune ($1 \rightarrow 0$)',
            fontsize=7.0, fontweight='bold', color=c_red_text, ha='center', va='top')

    # Arrow down to Mutant
    draw_arrow_down(x_start + 4 * cell_w, y_sig - 1.0, y_sig - 9.0)

    # Row 4: Mutated Elite Candidate x'_e
    y_mut = 37.0
    ax.text(x_start - 2.0, y_mut + cell_h / 2, r"$\mathbf{x}'_e$:",
            fontsize=8.5, fontweight='bold', color='#000000', ha='right', va='center')
    mut_data = [0, 1, 0, 0, 1, 0, r'$\dots$', 0]
    mut_tcolors = {
        1: (c_green_text, 'bold'),
        2: (c_red_text, 'bold')
    }
    mut_bgs = [None, c_add_bg, c_prune_bg, None, None, None, None, None]
    draw_vector(x_start, y_mut, cols, cell_w, cell_h, mut_data,
                row_bg=c_row_shade_purple, text_colors=mut_tcolors, cell_bgs=mut_bgs)

    # -------------------------------------------------------------
    # 3. BOTTOM: Strict 1-to-1 Greedy Replacement
    # -------------------------------------------------------------
    draw_arrow_down(x_start + 4 * cell_w, y_mut - 0.5, y_mut - 6.5, label=r'Evaluate $f(\mathbf{x})$')

    y_greedy = 9.0
    greedy_h = 15.0
    box_w = (strat_w - 4.0) / 2

    # Left Outcome: Success (Accept mutant)
    r_yes = patches.Rectangle((x_start, y_greedy), box_w, greedy_h,
                              facecolor='#DCFCE7', edgecolor='#16A34A', lw=0.8, zorder=3)
    ax.add_patch(r_yes)
    ax.text(x_start + box_w / 2, y_greedy + greedy_h - 4.5,
            r"If $f(\mathbf{x}'_e) < f(\mathbf{x}_e)$ (Improved)",
            fontsize=7.5, fontweight='bold', color='#166534', ha='center', va='center')
    ax.text(x_start + box_w / 2, y_greedy + 4.2,
            r"$\mathbf{x}_e^{\star} \leftarrow \mathbf{x}'_e$ (Accept mutant)",
            fontsize=7.2, color='#14532D', ha='center', va='center')

    # Right Outcome: Preserve existing elite
    r_no = patches.Rectangle((x_start + box_w + 4.0, y_greedy), box_w, greedy_h,
                             facecolor='#F1F5F9', edgecolor='#94A3B8', lw=0.8, zorder=3)
    ax.add_patch(r_no)
    ax.text(x_start + box_w + 4.0 + box_w / 2, y_greedy + greedy_h - 4.5,
            r'Otherwise (Worse / Equal)',
            fontsize=7.5, fontweight='bold', color='#475569', ha='center', va='center')
    ax.text(x_start + box_w + 4.0 + box_w / 2, y_greedy + 4.2,
            r'$\mathbf{x}_e^{\star} \leftarrow \mathbf{x}_e$ (Preserve elite)',
            fontsize=7.2, color='#334155', ha='center', va='center')

    # Outer dashed frame wrapping the entire micro-operator (clean and compact)
    outer_frame = patches.Rectangle((4.0, 3.0), 93.0, 120.0,
                                    facecolor='none', edgecolor='#CBD5E1', lw=0.8, linestyle='--', zorder=1)
    ax.add_patch(outer_frame)

    out_dir = r'e:\多目标优化\KDS-EL\output\figures'
    targets = [
        ('F4_ker_strategy_journal.pdf', 'F4_ker_strategy_journal.png'),
        ('F5_ker_strategy_journal.pdf', 'F5_ker_strategy_journal.png')
    ]

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    for pdf_name, png_name in targets:
        plt.savefig(os.path.join(out_dir, pdf_name), format='pdf', bbox_inches='tight', dpi=300)
        plt.savefig(os.path.join(out_dir, png_name), format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print('SUCCESS: Generated Single-Column Figure 4 Assets!')

if __name__ == '__main__':
    generate_figure4_single_column()
