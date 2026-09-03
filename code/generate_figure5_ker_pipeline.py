import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, w, h, text, fs=7.0, bold=False, lw=0.9):
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor='#000000',
                             facecolor='#FFFFFF', zorder=3)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center',
            fontsize=fs, color='#000000', weight=weight, zorder=4,
            multialignment='center')
    return rect

def draw_diamond(ax, cx, cy, w, h, text, fs=7.0):
    half_w = w / 2.0
    half_h = h / 2.0
    polygon = patches.Polygon([
        (cx, cy + half_h),
        (cx + half_w, cy),
        (cx, cy - half_h),
        (cx - half_w, cy)
    ], closed=True, linewidth=0.9, edgecolor='#000000', facecolor='#FFFFFF', zorder=3)
    ax.add_patch(polygon)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs, color='#000000', zorder=4)
    return polygon

def draw_dashed_container(ax, x, y, w, h, title, lw=1.0, title_fs=8.2):
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor='#000000',
                             facecolor='none', linestyle=(0, (6, 4)), zorder=1)
    ax.add_patch(rect)
    ax.text(x + w/2.0, y + h - 2.8, title, ha='center', va='top',
            fontsize=title_fs, color='#000000', fontweight='bold', zorder=2)
    return rect

def create_figure5_ker():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(11.0, 7.6), dpi=300)
    ax.set_xlim(1.5, 98.5)
    ax.set_ylim(1.5, 98.5)
    ax.axis('off')

    arr_lw = 0.75

    # =========================================================================
    # STAGE 1: Closed-Loop Feature-Importance Learning (y in [77.0, 97.0])
    # =========================================================================
    s1_x = 3.0
    s1_w = 94.0
    s1_y = 77.0
    s1_h = 20.0
    draw_dashed_container(ax, s1_x, s1_y, s1_w, s1_h,
                          r'Stage 1: Closed-Loop Feature-Importance Learning & Accumulation ($\mathbf{W}$ Matrix)', lw=1.0, title_fs=8.2)

    box_w = 28.0
    box_h = 11.5
    y_s1_box = 80.5

    # Stage 1 Box 1
    draw_box(ax, 5.0, y_s1_box, box_w, box_h,
             r'$\mathbf{Swarm\ Trial\ Evaluation}$' + '\n' +
             r'Particle $\mathbf{x}_i^{(t)}$ improves fitness over $\mathbf{p}_{\mathrm{best},i}$:' + '\n' +
             r'$\delta_i^{(t)} = f(\mathbf{p}_{\mathrm{best},i}, \mathbf{w}) - f(\mathbf{x}_i^{(t)}, \mathbf{w}) > 0$', fs=6.2)

    # Arrow to Box 2
    ax.annotate('', xy=(36.0, y_s1_box + box_h/2.0), xytext=(33.0, y_s1_box + box_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Stage 1 Box 2
    draw_box(ax, 36.0, y_s1_box, box_w, box_h,
             r'$\mathbf{Differential\ Mask\ Extraction}$' + '\n' +
             r'Harvest features with altered status:' + '\n' +
             r'$C_i^{(t)} = \{ j \mid x_{i,j}^{(t)} \neq p_{\mathrm{best},i,j} \}$', fs=6.2)

    # Arrow to Box 3
    ax.annotate('', xy=(67.0, y_s1_box + box_h/2.0), xytext=(64.0, y_s1_box + box_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Stage 1 Box 3
    draw_box(ax, 67.0, y_s1_box, box_w, box_h,
             r'$\mathbf{Importance\ Update\ (\gamma = 0.99)}$' + '\n' +
             r'$W_j \leftarrow \gamma W_j + \delta_i^{(t)} \cdot (2x_{i,j}^{(t)} - 1),\ \forall j \in C_i^{(t)}$' + '\n' +
             r'$\mathbf{W} = [W_1, \dots, W_D]^T \in \mathbb{R}^D$', fs=6.2, bold=True)

    # =========================================================================
    # STAGE 2: Knowledge-Guided Elite Refinement Operator (y in [25.0, 74.0])
    # =========================================================================
    s2_x = 3.0
    s2_w = 94.0
    s2_y = 25.0
    s2_h = 49.0
    draw_dashed_container(ax, s2_x, s2_y, s2_w, s2_h,
                          r'Stage 2: Knowledge-Guided Elite Refinement Operator (KER State Machine)', lw=1.0, title_fs=8.2)

    # Inputs bar
    in_w = 90.0
    in_h = 5.2
    draw_box(ax, 5.0, 67.5, in_w, in_h,
             r'$\mathbf{Inputs\ to\ KER\ Operator:}\ \text{Elite candidate}\ \mathbf{x}_e \in \{0, 1\}^D\ (\text{Top}\ k_e\ \text{pool}),\ \text{Importance vector}\ \mathbf{W} \in \mathbb{R}^D,\ \text{Dynamic weights}\ \mathbf{w}(t)$', fs=6.4)

    # Arrow from Input to Random Decision Diamond
    ax.annotate('', xy=(50.0, 58.5 + 3.0), xytext=(50.0, 67.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Random Diamond: r < p_rand
    dia1_cy = 58.5
    dia1_w = 16.0
    dia1_h = 6.0
    draw_diamond(ax, 50.0, dia1_cy, dia1_w, dia1_h, r'$r < p_{\mathrm{rand}}$', fs=7.0)

    # Branch 1 (Left: r < p_rand, Explore)
    ax.plot([50.0 - dia1_w/2.0, 20.0, 20.0], [dia1_cy, dia1_cy, 51.5 + 4.5], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(20.0, 51.5 + 4.5), xytext=(20.0, 51.5 + 4.8),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text(32.0, dia1_cy + 0.8, r'$\mathbf{Y}\ (p_{\mathrm{rand}})$', fontsize=6.5, ha='center', va='bottom')

    b1_w = 30.0
    draw_box(ax, 5.0, 51.5, b1_w, 4.5, r'$\mathbf{Branch\ 1:\ Ergodic\ Random\ Exploration}$', fs=6.2)

    ax.annotate('', xy=(20.0, 42.0 + 7.5), xytext=(20.0, 51.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    draw_box(ax, 5.0, 42.0, b1_w, 7.5,
             r"Sample $k_{\mathrm{flip}}$ random indices $\mathcal{S}_{\mathrm{rand}} \subset \{1, \dots, D\}$" + "\n" +
             r"Invert bits: $x'_{e,j} \leftarrow 1 - x_{e,j},\ \forall j \in \mathcal{S}_{\mathrm{rand}}$" + "\n" +
             r"(Preserves search ergodicity & diversity)", fs=5.8)

    # Branch 2 (Right: r >= p_rand, Knowledge Directional Refinement)
    ax.plot([50.0 + dia1_w/2.0, 68.0, 68.0], [dia1_cy, dia1_cy, 51.5 + 4.5], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(68.0, 51.5 + 4.5), xytext=(68.0, 51.5 + 4.8),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text(58.0, dia1_cy + 0.8, r'$\mathbf{N}\ (1 - p_{\mathrm{rand}})$', fontsize=6.5, ha='center', va='bottom')

    b2_w = 56.0
    draw_box(ax, 40.0, 51.5, b2_w, 4.5, r'$\mathbf{Branch\ 2:\ Knowledge\text{-}Guided\ Directional\ Refinement}$', fs=6.2, bold=True)

    ax.annotate('', xy=(68.0, 43.5 + 6.2), xytext=(68.0, 51.5),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    draw_box(ax, 40.0, 43.5, b2_w, 6.2,
             r"Compute Directional Score: $\sigma_j = (1 - 2x_{e,j}) \cdot W_j,\ \forall j = 1, \dots, D$" + "\n" +
             r"Identify subset $\mathcal{S}_{\mathrm{know}}$ of size $k_{\mathrm{flip}} = \max(1, \lfloor \phi D \rfloor)$ with largest $\sigma_j$", fs=6.0, bold=True)

    # Directional Prune vs Add sub-boxes
    sub_k_w = 26.5
    sub_k_h = 8.5
    y_sub_k = 32.0

    # Prune box
    draw_box(ax, 40.0, y_sub_k, sub_k_w, sub_k_h,
             r"$\mathbf{Directional\ Prune\ (Weak\ Features):}$" + "\n" +
             r"If $x_{e,j} = 1$ and $W_j < 0\ (\sigma_j > 0)$:" + "\n" +
             r"$\mathbf{x'_{e,j} \leftarrow 0}$ (Prune weak noise dimension)", fs=5.6)

    # Add box
    draw_box(ax, 69.5, y_sub_k, sub_k_w, sub_k_h,
             r"$\mathbf{Directional\ Add\ (Strong\ Biomarkers):}$" + "\n" +
             r"If $x_{e,j} = 0$ and $W_j > 0\ (\sigma_j > 0)$:" + "\n" +
             r"$\mathbf{x'_{e,j} \leftarrow 1}$ (Activate synergistic biomarker)", fs=5.6)

    # Connect Score box to Prune and Add
    ax.plot([68.0, 53.25, 53.25], [43.5, 41.5, y_sub_k + sub_k_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(53.25, y_sub_k + sub_k_h), xytext=(53.25, y_sub_k + sub_k_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([68.0, 82.75, 82.75], [43.5, 41.5, y_sub_k + sub_k_h], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(82.75, y_sub_k + sub_k_h), xytext=(82.75, y_sub_k + sub_k_h + 0.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # =========================================================================
    # STAGE 3: Strict 1-to-1 Greedy Replacement (y in [3.0, 22.0])
    # =========================================================================
    s3_x = 3.0
    s3_w = 94.0
    s3_y = 3.0
    s3_h = 19.5
    draw_dashed_container(ax, s3_x, s3_y, s3_w, s3_h,
                          r'Stage 3: Strict 1-to-1 Greedy Replacement', lw=1.0, title_fs=8.2)

    dia2_cy = 13.0
    dia2_w = 20.0
    dia2_h = 5.8
    draw_diamond(ax, 50.0, dia2_cy, dia2_w, dia2_h, r"$f(\mathbf{x}'_e, \mathbf{w}) < f(\mathbf{x}_e, \mathbf{w})$", fs=6.8)

    # Connect Branch 1 & Branch 2 outputs to Greedy Diamond
    ax.plot([20.0, 20.0, 50.0], [42.0, 21.0, 21.0], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([53.25, 53.25, 50.0], [y_sub_k, 21.0, 21.0], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([82.75, 82.75, 50.0], [y_sub_k, 21.0, 21.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(50.0, dia2_cy + dia2_h/2.0), xytext=(50.0, 21.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Accept Mutant (Left)
    ax.plot([50.0 - dia2_w/2.0, 25.0, 25.0], [dia2_cy, dia2_cy, 6.0 + 5.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(25.0, 6.0 + 5.0), xytext=(25.0, 6.0 + 5.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text(32.0, dia2_cy + 0.8, r'$\mathbf{Y}\ (\text{Improved})$', fontsize=6.5, ha='center', va='bottom')

    draw_box(ax, 10.0, 6.0, 30.0, 5.0,
             r"$\mathbf{Accept\ Superior\ Mutant:}\ \mathbf{x}_e^{\star} \leftarrow \mathbf{x}'_e$" + "\n" +
             r"(Update candidate elite subset)", fs=6.2, bold=True)

    # Preserve Elite (Right)
    ax.plot([50.0 + dia2_w/2.0, 75.0, 75.0], [dia2_cy, dia2_cy, 6.0 + 5.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(75.0, 6.0 + 5.0), xytext=(75.0, 6.0 + 5.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text(68.0, dia2_cy + 0.8, r'$\mathbf{N}\ (\text{Worse/Equal})$', fontsize=6.5, ha='center', va='bottom')

    draw_box(ax, 60.0, 6.0, 30.0, 5.0,
             r'$\mathbf{Preserve\ Existing\ Elite:}\ \mathbf{x}_e^{\star} \leftarrow \mathbf{x}_e$' + '\n' +
             r'(Safeguard monotonic convergence)', fs=6.2)

    # Save Output
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    tex_fig_dir = os.path.join(base_dir, 'Template-LaTeX-Elsevier-CAS-DC-master', 'figs')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tex_fig_dir, exist_ok=True)

    pdf_path = os.path.join(out_dir, 'F5_ker_strategy_journal.pdf')
    png_path = os.path.join(out_dir, 'F5_ker_strategy_journal.png')
    tex_pdf_path = os.path.join(tex_fig_dir, 'Fig5.pdf')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.savefig(tex_pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f'Successfully generated EMSWOA-Exact Figure 5 KER at:\n- {pdf_path}\n- {png_path}\n- {tex_pdf_path}')

if __name__ == '__main__':
    create_figure5_ker()
