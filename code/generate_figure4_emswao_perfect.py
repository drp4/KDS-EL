"""Publication-grade Figure 4: Knowledge-Guided Elite Refinement (KER) Process.
Exact 100% 1:1 structural, topological, and stylistic alignment with EMSWOA Fig. 6 (Applied Soft Computing, 2025).
Includes:
1. Dashed bounding box closed tightly after FP* Matrix (X*(t) is cleanly outside).
2. Orthogonal bus line merging cleanly into single trunk into Elite tuning strategy box.
3. Dual 'Get' dashed lines and brackets [---] and ] around extracted elite block.
4. Professional Times New Roman serif typography throughout.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_figure4_emswao_perfect():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    # Canvas dimensions: 14.8 x 6.5 inches (exact EMSWOA Fig. 6 publication aspect ratio)
    fig_w, fig_h = 14.8, 6.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, 152)
    ax.set_ylim(0, 95)
    ax.axis('off')

    # Color palette strictly from EMSWOA Fig. 6
    c_grid_line = '#64748B'
    c_text = '#000000'
    c_blue_text = '#0284C7'
    c_red_text = '#DC2626'
    c_strategy_box = '#BAE6FD'       # Soft light cyan (exact EMSWOA style)
    c_row_shade_purple = '#E0E7FF'   # Soft purple/lavender for x_best(t)
    c_row_shade_yellow = '#FEF3C7'   # Soft yellow for x_best(t-1)
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

        for r in range(rows):
            cy = y0 + (rows - 1 - r) * cell_h
            bg_c = row_colors[r] if (row_colors and r < len(row_colors) and row_colors[r]) else '#FFFFFF'

            for c in range(cols):
                cx = x0 + c * cell_w
                if bg_c != '#FFFFFF':
                    cell_bg = patches.Rectangle((cx, cy), cell_w, cell_h,
                                                facecolor=bg_c, edgecolor='none', zorder=1)
                    ax.add_patch(cell_bg)

                # Grid lines
                style_line = ':' if is_dotted else '-'
                if r > 0:
                    ax.plot([cx, cx + cell_w], [cy + cell_h, cy + cell_h],
                            color=c_grid_line, lw=0.5, linestyle=style_line, zorder=2)
                if c > 0:
                    ax.plot([cx, cx], [cy, cy + cell_h],
                            color=c_grid_line, lw=0.5, linestyle=style_line, zorder=2)

                val = data[r][c]
                t_color = c_text
                t_weight = 'normal'
                if text_colors and (r, c) in text_colors:
                    t_color = text_colors[(r, c)][0]
                    t_weight = text_colors[(r, c)][1]

                ax.text(cx + cell_w / 2, cy + cell_h / 2, str(val),
                        fontsize=7.8, color=t_color, fontweight=t_weight,
                        ha='center', va='center', zorder=4)

    def draw_clean_block_arrow(x0, y0, w, h, label=None, label_top=None):
        """Draw a crisp open block arrow matching EMSWOA Fig. 6."""
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
                    fontsize=7.6, color='#000000', ha='center', va='center', zorder=6)
        if label_top:
            ax.text(x0 + w / 2, y0 + h + 1.8, label_top,
                    fontsize=8.0, color='#000000', ha='center', va='bottom', zorder=6)

    # -------------------------------------------------------------
    # TOP TIER: Standard Evolutionary Search & Probability Mapping
    # -------------------------------------------------------------
    cell_w = 3.2
    cell_h = 6.2
    top_y = 56.0

    # 1. Top Left: Population matrix X(t-1)
    x_m1 = 15.0
    ax.text(x_m1 + 4 * cell_w, top_y + 4 * cell_h + 8.5, 'Population matrix',
            fontsize=10.0, fontweight='bold', color='#000000', ha='center', va='bottom')
    ax.text(x_m1 + 4 * cell_w, top_y + 4 * cell_h + 2.2, r'$X(t-1)$',
            fontsize=9.0, color='#000000', ha='center', va='bottom')
    ax.text(x_m1 - 1.5, top_y + 1.5 * cell_h, r'$X_{\mathrm{best}}(t-1)$',
            fontsize=8.0, color='#000000', ha='right', va='center')

    mat_xt_minus_1 = [
        [0, 0, 1, 1, 0, 1, 1, 1],
        [0, 1, 1, 1, 0, 0, 1, 0],
        [1, 1, 0, 0, 1, 0, 1, 0],  # row 3 = X_best(t-1)
        [0, 1, 1, 0, 1, 0, 0, 1]
    ]
    draw_matrix(x_m1, top_y, 4, 8, cell_w, cell_h, mat_xt_minus_1,
                row_colors=['#FFFFFF', '#FFFFFF', c_row_shade_yellow, '#FFFFFF'])

    # 2. Evolving Block & f(x) Block
    x_arr_evo1 = x_m1 + 8 * cell_w + 2.5
    draw_clean_block_arrow(x_arr_evo1, top_y + 8.5, 4.8, 7.5)

    x_box_evo = x_arr_evo1 + 6.0
    ax.text(x_box_evo + 3.8, top_y + 4 * cell_h + 2.2, 'Evolving',
            fontsize=9.0, color='#000000', ha='center', va='bottom')
    r_evo = patches.Rectangle((x_box_evo, top_y + 1.0), 7.5, 23.0,
                              facecolor='#FFFFFF', edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_evo)
    ax.text(x_box_evo + 3.75, top_y + 12.5, 'KDS-EL',
            fontsize=8.0, color='#000000', ha='center', va='center', zorder=5)

    x_arr_evo2 = x_box_evo + 8.8
    draw_clean_block_arrow(x_arr_evo2, top_y + 8.5, 4.2, 7.5)

    x_fx = x_arr_evo2 + 5.5
    r_fx = patches.Rectangle((x_fx, top_y + 1.0), 6.5, 23.0,
                             facecolor='#FFFFFF', edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_fx)
    ax.text(x_fx + 3.25, top_y + 12.5, r'$f(x)$',
            fontsize=8.5, color='#000000', ha='center', va='center', zorder=5)

    x_arr_fx = x_fx + 7.8
    draw_clean_block_arrow(x_arr_fx, top_y + 8.5, 4.8, 7.5)

    # 3. Middle Top: Flip Probability Matrix FP*(t)
    x_fp = x_arr_fx + 6.2
    ax.text(x_fp + 4 * cell_w, top_y + 4 * cell_h + 8.5, 'Flip Probability Matrix',
            fontsize=10.0, fontweight='bold', color='#000000', ha='center', va='bottom')
    ax.text(x_fp + 4 * cell_w, top_y + 4 * cell_h + 2.2, r'$FP^*\ \mathrm{Matrix}_{(t)}$',
            fontsize=9.0, color='#000000', ha='center', va='bottom')

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

    # 4. Arrow transform to X*(t) (crosses OUT of dashed box)
    x_trans1 = x_fp + 8 * cell_w + 2.0
    draw_clean_block_arrow(x_trans1, top_y + 8.5, 9.0, 7.5, label='transform')

    # 5. Top Right: Candidate Population matrix X*(t) (CLEANLY OUTSIDE DASHED BOX)
    x_xstar = x_trans1 + 10.5
    ax.text(x_xstar + 4 * cell_w, top_y + 4 * cell_h + 8.5, 'Population matrix',
            fontsize=10.0, fontweight='bold', color='#000000', ha='center', va='bottom')
    ax.text(x_xstar + 4 * cell_w, top_y + 4 * cell_h + 2.2, r'$X^*(t)$',
            fontsize=9.0, color='#000000', ha='center', va='bottom')
    ax.text(x_xstar + 8 * cell_w + 1.5, top_y + 2.5 * cell_h, r'$X_{\mathrm{best}}(t)$',
            fontsize=8.0, color='#000000', ha='left', va='center')

    mat_xstar = [
        [0, 1, 1, 0, 1, 1, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1],  # row 2 = X_best(t)
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
    # EXACT EMSWOA DASHED BOX: Tight wrap up to FP* Matrix ONLY!
    # -------------------------------------------------------------
    dash_x_left = 6.0
    dash_x_right = x_fp + 8 * cell_w + 1.2
    dash_y_top = top_y + 4 * cell_h + 8.5
    dash_y_bot = top_y - 1.5

    # Trace dashed line: starts at top-left, goes right over FP*, goes down, goes left to X(t-1), goes down
    # Top dashed line
    ax.plot([dash_x_left, dash_x_right], [dash_y_top, dash_y_top], color='#475569', lw=0.85, linestyle='--', zorder=2)
    # Right vertical dashed line (drops down right after FP*)
    ax.plot([dash_x_right, dash_x_right], [dash_y_top, dash_y_bot], color='#475569', lw=0.85, linestyle='--', zorder=2)
    # Bottom dashed line under top tier
    ax.plot([dash_x_left, dash_x_right], [dash_y_bot, dash_y_bot], color='#475569', lw=0.85, linestyle='--', zorder=2)
    # Left outer vertical dashed line (drops all the way down to Get bracket!)
    ax.plot([dash_x_left, dash_x_left], [dash_y_top, bot_y_top_bracket := 40.5], color='#475569', lw=0.85, linestyle='--', zorder=2)

    # -------------------------------------------------------------
    # BOTTOM TIER: Elite Feedback & KER Refinement
    # -------------------------------------------------------------
    bot_y = 10.0
    cell_h_bot = 5.6

    # 1. Bottom Left: 4 Extracted Elite Rows
    x_ext = 15.0
    ax.text(x_ext - 1.5, bot_y + 3.5 * cell_h_bot, r'$X_{\mathrm{best}}(t)$',
            fontsize=7.8, color='#000000', ha='right', va='center')
    ax.text(x_ext - 1.5, bot_y + 2.5 * cell_h_bot, r'$X_{\mathrm{best}}(t)\ \mathrm{FP}$',
            fontsize=7.8, color='#000000', ha='right', va='center')
    ax.text(x_ext - 1.5, bot_y + 1.5 * cell_h_bot, r'$X_{\mathrm{best}}(t-1)$',
            fontsize=7.8, color='#000000', ha='right', va='center')
    ax.text(x_ext - 1.5, bot_y + 0.5 * cell_h_bot, r'$X_{\mathrm{best}}(t-1)\ \mathrm{FP}$',
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

    # DUAL 'GET' DASHED LINES & BRACKET [-------] (Exact EMSWOA style)
    # Horizontal bracket over extracted rows
    y_brk_top = bot_y + 4 * cell_h_bot + 2.5
    brk_x0 = x_ext - 0.5
    brk_x1 = x_ext + 8 * cell_w + 0.5
    ax.plot([brk_x0, brk_x1], [y_brk_top, y_brk_top], color='#000000', lw=0.85, zorder=6)
    ax.plot([brk_x0, brk_x0], [y_brk_top, y_brk_top - 2.0], color='#000000', lw=0.85, zorder=6)
    ax.plot([brk_x1, brk_x1], [y_brk_top, y_brk_top - 2.0], color='#000000', lw=0.85, zorder=6)

    # Left Get arrow (from left vertical dashed line down to bracket)
    ax.annotate('', xy=(brk_x0, y_brk_top), xytext=(dash_x_left, bot_y_top_bracket),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=0.85, linestyle='--'))
    ax.text(dash_x_left + 1.2, 43.5, 'Get', fontsize=8.0, color='#000000', ha='left', va='center')

    # Middle Get arrow (from X(t-1) bottom down to bracket)
    x_get_mid = x_m1 + 4 * cell_w
    ax.annotate('', xy=(x_get_mid, y_brk_top), xytext=(x_get_mid, top_y - 1.5),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=0.85, linestyle='--'))
    ax.text(x_get_mid + 1.2, 43.5, 'Get', fontsize=8.0, color='#000000', ha='left', va='center')

    # Right aggregation bracket ']' on extracted rows
    x_brk_r = x_ext + 8 * cell_w + 1.5
    y_brk_r0 = bot_y
    y_brk_r1 = bot_y + 4 * cell_h_bot
    y_brk_mid = (y_brk_r0 + y_brk_r1) / 2
    ax.plot([x_brk_r, x_brk_r + 1.5], [y_brk_r0, y_brk_r0], color='#000000', lw=0.85, zorder=6)
    ax.plot([x_brk_r, x_brk_r + 1.5], [y_brk_r1, y_brk_r1], color='#000000', lw=0.85, zorder=6)
    ax.plot([x_brk_r + 1.5, x_brk_r + 1.5], [y_brk_r0, y_brk_r1], color='#000000', lw=0.85, zorder=6)
    ax.plot([x_brk_r + 1.5, x_brk_r + 3.0], [y_brk_mid, y_brk_mid], color='#000000', lw=0.85, zorder=6)

    # Arrow Guide to Strategy Box
    x_guide = x_brk_r + 3.5
    draw_clean_block_arrow(x_guide, bot_y + 7.2, 6.5, 8.0, label_top='Guide')

    # 2. Central Box: Elite tuning strategy (KER)
    x_strat = x_guide + 7.8
    strat_w, strat_h = 16.0, 20.5
    r_strat = patches.Rectangle((x_strat, bot_y + 1.0), strat_w, strat_h,
                                facecolor=c_strategy_box, edgecolor='#000000', lw=0.9, zorder=4)
    ax.add_patch(r_strat)
    ax.text(x_strat + strat_w / 2, bot_y + 11.2, 'Elite tuning\nstrategy (KER)',
            fontsize=8.8, color='#000000', ha='center', va='center', zorder=5)

    # -------------------------------------------------------------
    # ORTHOGONAL BUS ROUTING (Exact EMSWOA Merged Trunk Topology)
    # -------------------------------------------------------------
    y_bus = 43.5
    x_strat_center = x_strat + strat_w / 2

    # Drop from X*(t) down to y_bus (completely outside dashed box!)
    x_xstar_drop = x_xstar + 2.5 * cell_w
    ax.plot([x_xstar_drop, x_xstar_drop], [top_y - 0.5, y_bus], color='#000000', lw=0.85, zorder=6)

    # Drop from FP* Matrix down to y_bus
    x_fp_drop = x_fp + 4.0 * cell_w
    ax.plot([x_fp_drop, x_fp_drop], [top_y - 1.5, y_bus], color='#000000', lw=0.85, zorder=6)

    # Horizontal bus connecting X*(t) drop, FP* drop, and Strategy Center
    ax.plot([x_xstar_drop, x_strat_center], [y_bus, y_bus], color='#000000', lw=0.85, zorder=6)

    # Single vertical trunk dropping into Strategy Box
    ax.annotate('', xy=(x_strat_center, bot_y + strat_h + 1.0),
                xytext=(x_strat_center, y_bus),
                arrowprops=dict(arrowstyle="->", color="#000000", lw=0.85))

    # Arrow Updated to FP Matrix(t)
    x_arr_upd = x_strat + strat_w + 1.5
    draw_clean_block_arrow(x_arr_upd, bot_y + 7.2, 6.8, 8.0, label_top='Updated')

    # 3. Bottom Center: Updated FP Matrix(t)
    x_upd = x_arr_upd + 8.0
    ax.text(x_upd + 4 * cell_w, bot_y + 4 * cell_h_bot + 3.0, r'$FP\ \mathrm{Matrix}(t)$',
            fontsize=9.0, color='#000000', ha='center', va='bottom')

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
    draw_clean_block_arrow(x_trans2, bot_y + 7.2, 9.0, 7.5, label='transform')

    # 4. Bottom Right: Final Population matrix X(t)
    x_xt_final = x_trans2 + 10.5
    ax.text(x_xt_final + 4 * cell_w, bot_y + 4 * cell_h_bot + 3.0, r'$X(t)$',
            fontsize=9.5, color='#000000', ha='center', va='bottom')
    ax.text(x_xt_final + 8 * cell_w + 1.5, bot_y + 0.5 * cell_h_bot, r'$X_{\mathrm{best}}(t)$',
            fontsize=8.0, color='#000000', ha='left', va='center')

    mat_xt_final = [
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 0, 1]  # Bottom row = refined X_best(t)
    ]
    tcolors_xt_final = {
        (0, 0): (c_red_text, 'normal'), (0, 3): (c_red_text, 'normal'),
        (2, 5): (c_red_text, 'normal'),
        (3, 2): (c_red_text, 'normal'), (3, 7): (c_red_text, 'normal')
    }
    draw_matrix(x_xt_final, bot_y, 4, 8, cell_w, cell_h_bot, mat_xt_final,
                row_colors=['#FFFFFF', '#FFFFFF', '#FFFFFF', c_row_shade_grey],
                text_colors=tcolors_xt_final)

    out_dir = r'e:\多目标优化\KDS-EL\output\figures'
    targets = [
        ('F4_ker_strategy_journal.pdf', 'F4_ker_strategy_journal.png'),
        ('F5_ker_strategy_journal.pdf', 'F5_ker_strategy_journal.png')
    ]

    plt.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.03)
    for pdf_name, png_name in targets:
        plt.savefig(os.path.join(out_dir, pdf_name), format='pdf', bbox_inches='tight', dpi=300)
        plt.savefig(os.path.join(out_dir, png_name), format='png', bbox_inches='tight', dpi=300)

    plt.close(fig)
    print('SUCCESS: Rendered Pixel-Perfect EMSWOA Fig. 6 Replica with Micro-Refinements!')

if __name__ == '__main__':
    generate_figure4_emswao_perfect()
