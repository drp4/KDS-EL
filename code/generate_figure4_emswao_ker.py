"""Publication-grade Figure 4: Knowledge-Guided Elite Refinement (KER) Process.
Exact 1:1 structural and stylistic alignment with EMSWOA Fig. 6 (Applied Soft Computing, 2025).
Pure academic engineering matrix/vector transformation with 100% clean orthogonal routing.
Outputs both F4_ker_strategy_journal and F5_ker_strategy_journal to seamlessly support paper compilation.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_figure4():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    # Canvas dimensions matching EMSWOA Fig. 6: 15.0 x 6.6 inches
    fig_w, fig_h = 15.0, 6.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color definitions (strictly following EMSWOA Fig. 6)
    c_grid_line = '#64748B'
    c_text = '#000000'
    c_blue_text = '#0284C7'
    c_red_text = '#DC2626'
    c_strategy_box = '#BAE6FD'      # Soft light cyan (exact EMSWOA style)
    c_row_shade_purple = '#E0E7FF'  # Soft purple/lavender for x_best(t)
    c_row_shade_yellow = '#FEF3C7'  # Soft yellow for x_best(t-1)
    c_row_shade_grey = '#F1F5F9'

    def draw_matrix(x0, y0, rows, cols, cell_w, cell_h, data,
                    row_colors=None, text_colors=None, is_dotted=False,
                    box_border='#000000'):
        """Draw a rectangular grid matrix like EMSWOA Fig. 6."""
        mat_w = cols * cell_w
        mat_h = rows * cell_h
        
        # Outer border
        outer = patches.Rectangle((x0, y0), mat_w, mat_h,
                                  facecolor='none', edgecolor=box_border, lw=0.9, zorder=3)
        ax.add_patch(outer)

        # Cells
        for r in range(rows):
            cy = y0 + (rows - 1 - r) * cell_h
            bg_c = row_colors[r] if (row_colors and r < len(row_colors) and row_colors[r]) else '#FFFFFF'
            
            for c in range(cols):
                cx = x0 + c * cell_w
                # Cell background
                if bg_c != '#FFFFFF':
                    cell_bg = patches.Rectangle((cx, cy), cell_w, cell_h,
                                                facecolor=bg_c, edgecolor='none', zorder=1)
                    ax.add_patch(cell_bg)
                
                # Grid dividers
                style_line = ':' if is_dotted else '-'
                if r > 0:
                    ax.plot([cx, cx + cell_w], [cy + cell_h, cy + cell_h],
                            color=c_grid_line, lw=0.5, linestyle=style_line, zorder=2)
                if c > 0:
                    ax.plot([cx, cx], [cy, cy + cell_h],
                            color=c_grid_line, lw=0.5, linestyle=style_line, zorder=2)

                # Text content
                val = data[r][c]
                t_color = c_text
                t_weight = 'normal'
                if text_colors and (r, c) in text_colors:
                    t_color = text_colors[(r, c)][0]
                    t_weight = text_colors[(r, c)][1]

                ax.text(cx + cell_w / 2, cy + cell_h / 2, str(val),
                        fontsize=7.6, color=t_color, fontweight=t_weight,
                        ha='center', va='center', zorder=4)

    def draw_clean_block_arrow(x0, y0, w, h, label=None, label_top=None):
        """Draw a clean, elegant open block arrow exactly like EMSWOA Fig. 6."""
        head_len = min(h * 0.70, w * 0.45)
        body_h = h * 0.38
        body_len = w - head_len
        body_y0 = y0 + (h - body_h) / 2
        body_y1 = body_y0 + body_h
        
        verts = [
            (x0, body_y0),
            (x0 + body_len, body_y0),
            (x0 + body_len, y0),
            (x0 + w, y0 + h / 2),
            (x0 + body_len, y0 + h),
            (x0 + body_len, body_y1),
            (x0, body_y1)
        ]
        poly = patches.Polygon(verts, closed=True, facecolor='#FFFFFF', edgecolor='#000000', lw=0.8, zorder=5)
        ax.add_patch(poly)
        if label:
            ax.text(x0 + body_len / 2, y0 + h / 2, label,
                    fontsize=7.5, color='#000000', ha='center', va='center', zorder=6)
        if label_top:
            ax.text(x0 + w / 2, y0 + h + 2.0, label_top,
                    fontsize=7.8, color='#000000', ha='center', va='bottom', zorder=6)

    # -------------------------------------------------------------
    # TOP ROW: Standard Evolutionary Search & Probability Mapping
    # -------------------------------------------------------------
    top_y = 65.0
    cell_w = 3.2
    cell_h = 6.2

    # 1. Top Left: Population matrix X(t-1)
    x_m1 = 12.0
    ax.text(x_m1 + 4 * cell_w, top_y + 4 * cell_h + 8.5, 'Population matrix',
            fontsize=9.8, fontweight='bold', color='#000000', ha='center', va='bottom')
    ax.text(x_m1 + 4 * cell_w, top_y + 4 * cell_h + 2.2, r'$\mathbf{X}(t-1)$',
            fontsize=8.8, color='#000000', ha='center', va='bottom')
    ax.text(x_m1 - 1.5, top_y + 1.5 * cell_h, r'$\mathbf{x}_{\mathrm{best}}(t-1)$',
            fontsize=7.8, color='#000000', ha='right', va='center')

    mat_xt_minus_1 = [
        [0, 0, 1, 1, 0, 1, 1, 1],
        [0, 1, 1, 1, 0, 0, 1, 0],
        [1, 1, 0, 0, 1, 0, 1, 0],  # row 3 = x_best(t-1)
        [0, 1, 1, 0, 1, 0, 0, 1]
    ]
    draw_matrix(x_m1, top_y, 4, 8, cell_w, cell_h, mat_xt_minus_1,
                row_colors=['#FFFFFF', '#FFFFFF', c_row_shade_yellow, '#FFFFFF'])

    # 2. Middle Top: Evolving block and f(x) block
    x_evo = x_m1 + 8 * cell_w + 3.0
    draw_clean_block_arrow(x_evo, top_y + 8.5, 5.5, 7.5)
    
    # Evolving Box
    x_box_evo = x_evo + 7.0
    ax.text(x_box_evo + 4.5, top_y + 4 * cell_h + 2.2, 'Evolving',
            fontsize=8.8, color='#000000', ha='center', va='bottom')
    r_evo = patches.Rectangle((x_box_evo, top_y + 1.0), 9.0, 23.0,
                              facecolor='#FFFFFF', edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_evo)
    ax.text(x_box_evo + 4.5, top_y + 12.5, 'KDS-EL\nDual-Swarm',
            fontsize=7.5, color='#000000', ha='center', va='center', zorder=5)

    # Arrow to f(x)
    draw_clean_block_arrow(x_box_evo + 10.5, top_y + 8.5, 4.5, 7.5)

    # f(x) Box
    x_fx = x_box_evo + 16.5
    r_fx = patches.Rectangle((x_fx, top_y + 1.0), 6.5, 23.0,
                             facecolor='#FFFFFF', edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_fx)
    ax.text(x_fx + 3.25, top_y + 12.5, r'$f(\mathbf{x})$',
            fontsize=8.5, color='#000000', ha='center', va='center', zorder=5)

    # Arrow to Continuous Probability Matrix
    x_arr_fx = x_fx + 8.0
    draw_clean_block_arrow(x_arr_fx, top_y + 8.5, 5.5, 7.5)

    # 3. Middle Top: Continuous Position / Probability Matrix P*(t)
    x_fp = x_arr_fx + 7.0
    ax.text(x_fp + 4 * cell_w, top_y + 4 * cell_h + 8.5, 'Continuous Position Matrix',
            fontsize=9.8, fontweight='bold', color='#000000', ha='center', va='bottom')
    ax.text(x_fp + 4 * cell_w, top_y + 4 * cell_h + 2.2, r'$\mathbf{P}^*\ (t)$',
            fontsize=8.8, color='#000000', ha='center', va='bottom')

    mat_p_float = [
        ['0.44', '0.46', '0.86', '0.66', '0.56', '0.72', '0.86', '0.32'],
        ['0.75', '0.05', '0.16', '0.45', '0.23', '0.53', '0.11', '0.58'],
        ['0.65', '0.78', '0.22', '0.63', '0.76', '0.32', '0.59', '0.79'],
        ['0.12', '0.93', '0.49', '0.77', '0.22', '0.46', '0.33', '0.68']
    ]
    tcolors_p = {
        (0, 2): (c_blue_text, 'normal'), (0, 3): (c_blue_text, 'normal'), (0, 7): (c_blue_text, 'normal'),
        (2, 3): (c_blue_text, 'normal'), (2, 5): (c_blue_text, 'normal'),
        (3, 0): (c_blue_text, 'normal'), (3, 2): (c_blue_text, 'normal')
    }
    draw_matrix(x_fp, top_y, 4, 8, cell_w, cell_h, mat_p_float,
                row_colors=['#FFFFFF', c_row_shade_grey, '#FFFFFF', '#FFFFFF'],
                text_colors=tcolors_p, is_dotted=True)

    # Arrow transform to X*(t)
    x_trans1 = x_fp + 8 * cell_w + 2.0
    draw_clean_block_arrow(x_trans1, top_y + 8.5, 9.0, 7.5, label='transform')

    # 4. Top Right: Candidate Population matrix X*(t)
    x_xstar = x_trans1 + 10.5
    ax.text(x_xstar + 4 * cell_w, top_y + 4 * cell_h + 8.5, 'Population matrix',
            fontsize=9.8, fontweight='bold', color='#000000', ha='center', va='bottom')
    ax.text(x_xstar + 4 * cell_w, top_y + 4 * cell_h + 2.2, r'$\mathbf{X}^*(t)$',
            fontsize=8.8, color='#000000', ha='center', va='bottom')
    ax.text(x_xstar + 8 * cell_w + 1.5, top_y + 2.5 * cell_h, r'$\mathbf{x}_{\mathrm{best}}(t)$',
            fontsize=7.8, color='#000000', ha='left', va='center')

    mat_xstar = [
        [0, 1, 1, 0, 1, 1, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1],  # row 2 = x_best(t)
        [1, 1, 0, 0, 1, 0, 1, 1],
        [0, 1, 1, 1, 0, 0, 0, 0]
    ]
    tcolors_xstar = {
        (0, 0): (c_blue_text, 'normal'), (0, 2): (c_blue_text, 'normal'), (0, 4): (c_blue_text, 'normal'), (0, 7): (c_blue_text, 'normal'),
        (1, 3): (c_blue_text, 'normal'),
        (2, 3): (c_blue_text, 'normal'), (2, 5): (c_blue_text, 'normal'),
        (3, 0): (c_blue_text, 'normal'), (3, 5): (c_blue_text, 'normal')
    }
    draw_matrix(x_xstar, top_y, 4, 8, cell_w, cell_h, mat_xstar,
                row_colors=['#FFFFFF', c_row_shade_purple, '#FFFFFF', '#FFFFFF'],
                text_colors=tcolors_xstar)

    # -------------------------------------------------------------
    # BOTTOM ROW: Elite Extraction & KER Targeted Refinement
    # -------------------------------------------------------------
    bot_y = 14.0
    cell_h_bot = 5.6

    # 1. Bottom Left: 4 extracted vectors
    x_ext = 8.5
    ax.text(x_ext - 1.5, bot_y + 3.5 * cell_h_bot, r'$\mathbf{x}_{\mathrm{best}}(t)$',
            fontsize=7.8, color='#000000', ha='right', va='center')
    ax.text(x_ext - 1.5, bot_y + 2.5 * cell_h_bot, r'$\mathbf{p}_{\mathrm{best}}(t)$',
            fontsize=7.8, color='#000000', ha='right', va='center')
    ax.text(x_ext - 1.5, bot_y + 1.5 * cell_h_bot, r'$\mathbf{x}_{\mathrm{best}}(t-1)$',
            fontsize=7.8, color='#000000', ha='right', va='center')
    ax.text(x_ext - 1.5, bot_y + 0.5 * cell_h_bot, r'$\mathbf{p}_{\mathrm{best}}(t-1)$',
            fontsize=7.8, color='#000000', ha='right', va='center')

    mat_extracted = [
        [1, 0, 0, 1, 0, 1, 0, 0],
        ['0.75', '0.05', '0.16', '0.45', '0.23', '0.53', '0.11', '0.28'],
        [1, 1, 0, 0, 1, 0, 1, 0],
        ['0.31', '0.75', '0.06', '0.25', '0.63', '0.43', '0.49', '0.29']
    ]
    draw_matrix(x_ext, bot_y, 4, 8, cell_w, cell_h_bot, mat_extracted,
                row_colors=[c_row_shade_purple, c_row_shade_grey, c_row_shade_yellow, c_row_shade_grey],
                is_dotted=True)

    # Dashed Extraction Line: from X(t-1) down to extracted vectors
    ax.plot([x_m1 + 4 * cell_w, x_m1 + 4 * cell_w], [top_y - 0.5, bot_y + 4 * cell_h_bot + 1.0],
            color='#000000', lw=0.85, linestyle='--', zorder=6)
    ax.text(x_m1 + 4 * cell_w + 1.2, top_y - 8.0, 'Get', fontsize=7.8, color='#000000', ha='left')

    # Arrow Guide to Strategy Box
    x_guide = x_ext + 8 * cell_w + 3.0
    draw_clean_block_arrow(x_guide, bot_y + 7.0, 7.5, 8.0, label_top='Guide')

    # 2. Central Box: Elite tuning strategy / KER Refinement
    x_strat = x_guide + 9.0
    strat_w, strat_h = 16.5, 20.0
    r_strat = patches.Rectangle((x_strat, bot_y + 1.0), strat_w, strat_h,
                                facecolor=c_strategy_box, edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_strat)
    ax.text(x_strat + strat_w/2, bot_y + 11.0, 'Knowledge-guided\nelite refinement\nstrategy (KER)',
            fontsize=8.5, color='#000000', ha='center', va='center', zorder=5)

    # Clean Orthogonal Connector 1: from P* Matrix down to KER box
    x_fp_drop = x_fp + 4.5 * cell_w
    y_bus_fp = 44.0
    ax.plot([x_fp_drop, x_fp_drop], [top_y - 0.5, y_bus_fp], color='#000000', lw=0.85, zorder=6)
    ax.plot([x_fp_drop, x_strat + strat_w * 0.70], [y_bus_fp, y_bus_fp], color='#000000', lw=0.85, zorder=6)
    ax.annotate('', xy=(x_strat + strat_w * 0.70, bot_y + strat_h + 1.0),
                xytext=(x_strat + strat_w * 0.70, y_bus_fp),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=0.85))

    # Clean Orthogonal Connector 2: from X*(t) down to KER box
    x_xstar_drop = x_xstar + 2.5 * cell_w
    y_bus_xstar = 48.0
    ax.plot([x_xstar_drop, x_xstar_drop], [top_y - 0.5, y_bus_xstar], color='#000000', lw=0.85, zorder=6)
    ax.plot([x_xstar_drop, x_strat + strat_w * 0.35], [y_bus_xstar, y_bus_xstar], color='#000000', lw=0.85, zorder=6)
    ax.annotate('', xy=(x_strat + strat_w * 0.35, bot_y + strat_h + 1.0),
                xytext=(x_strat + strat_w * 0.35, y_bus_xstar),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=0.85))

    # Arrow Updated
    x_arr_upd = x_strat + strat_w + 1.5
    draw_clean_block_arrow(x_arr_upd, bot_y + 7.0, 7.5, 8.0, label_top='Updated')

    # 3. Bottom Center: Updated Probability Matrix P(t)
    x_upd = x_arr_upd + 9.0
    ax.text(x_upd + 4 * cell_w, bot_y + 4 * cell_h_bot + 3.0, r'$\mathbf{P}\ \mathrm{Matrix}(t)$',
            fontsize=8.5, color='#000000', ha='center', va='bottom')

    mat_p_upd = [
        ['0.56', '0.46', '0.41', '0.78', '0.56', '0.72', '0.86', '0.45'],
        ['0.75', '0.05', '0.16', '0.15', '0.23', '0.53', '0.11', '0.58'],
        ['0.65', '0.78', '0.22', '0.71', '0.76', '0.92', '0.59', '0.92'],
        ['0.38', '0.93', '0.67', '0.77', '0.22', '0.59', '0.94', '0.73']
    ]
    tcolors_p_upd = {
        (0, 0): (c_red_text, 'normal'), (0, 2): (c_red_text, 'normal'), (0, 3): (c_red_text, 'normal'),
        (2, 3): (c_red_text, 'normal'), (2, 5): (c_red_text, 'normal'),
        (3, 2): (c_red_text, 'normal'), (3, 7): (c_red_text, 'normal')
    }
    draw_matrix(x_upd, bot_y, 4, 8, cell_w, cell_h_bot, mat_p_upd,
                text_colors=tcolors_p_upd, is_dotted=True)

    # Arrow transform to X(t)
    x_trans2 = x_upd + 8 * cell_w + 2.0
    draw_clean_block_arrow(x_trans2, bot_y + 7.0, 9.0, 7.5, label='transform')

    # 4. Bottom Right: Final Corrected Population matrix X(t)
    x_xt_final = x_trans2 + 10.5
    ax.text(x_xt_final + 4 * cell_w, bot_y + 4 * cell_h_bot + 3.0, r'$\mathbf{X}(t)$',
            fontsize=9.0, color='#000000', ha='center', va='bottom')
    ax.text(x_xt_final + 8 * cell_w + 1.5, bot_y + 0.5 * cell_h_bot, r'$\mathbf{x}_{\mathrm{best}}(t)$',
            fontsize=7.8, color='#000000', ha='left', va='center')

    mat_xt_final = [
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 0, 1]  # Bottom row = refined x_best
    ]
    tcolors_xt_final = {
        (0, 0): (c_red_text, 'normal'), (0, 3): (c_red_text, 'normal'),
        (2, 5): (c_red_text, 'normal'),
        (3, 2): (c_red_text, 'normal'), (3, 7): (c_red_text, 'normal')
    }
    draw_matrix(x_xt_final, bot_y, 4, 8, cell_w, cell_h_bot, mat_xt_final,
                row_colors=['#FFFFFF', '#FFFFFF', '#FFFFFF', c_row_shade_grey],
                text_colors=tcolors_xt_final)

    # Surrounding Dashed Box wrapping top flow (exact EMSWOA style)
    dash_box = patches.Rectangle((x_m1 - 7.0, top_y - 2.5),
                                 (x_xstar + 8 * cell_w + 10.0) - (x_m1 - 7.0),
                                 4 * cell_h + 8.5,
                                 facecolor='none', edgecolor='#475569', lw=0.85, linestyle='--', zorder=1)
    ax.add_patch(dash_box)

    out_dir = r'e:\多目标优化\KDS-EL\output\figures'
    
    # Save to both F4 and F5 filenames for 100% backward/forward compatibility
    targets = [
        ('F4_ker_strategy_journal.pdf', 'F4_ker_strategy_journal.png'),
        ('F5_ker_strategy_journal.pdf', 'F5_ker_strategy_journal.png')
    ]

    plt.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.05)
    for pdf_name, png_name in targets:
        plt.savefig(os.path.join(out_dir, pdf_name), format='pdf', bbox_inches='tight', dpi=300)
        plt.savefig(os.path.join(out_dir, png_name), format='png', bbox_inches='tight', dpi=300)
    
    plt.close(fig)
    print('SUCCESS: Saved refined PDF and PNG for both F4 and F5!')

if __name__ == '__main__':
    generate_figure4()
