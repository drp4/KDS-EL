import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_cell(ax, x, y, w, h, text, fs=6.5, bold=False, shaded=False, lw=0.8):
    fc = '#F4F4F4' if shaded else '#FFFFFF'
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor='#000000',
                             facecolor=fc, zorder=3)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2.0, y + h/2.0, text, ha='center', va='center',
            fontsize=fs, color='#000000', weight=weight, zorder=4,
            multialignment='center')
    return rect

def draw_dashed_container(ax, x, y, w, h, title, lw=1.0, title_fs=8.2):
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor='#000000',
                             facecolor='none', linestyle=(0, (6, 4)), zorder=1)
    ax.add_patch(rect)
    ax.text(x + w/2.0, y + h - 2.8, title, ha='center', va='top',
            fontsize=title_fs, color='#000000', fontweight='bold', zorder=2)
    return rect

def create_figure4_lesion():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(11.0, 6.8), dpi=300)
    ax.set_xlim(1.5, 98.5)
    ax.set_ylim(2.0, 98.0)
    ax.axis('off')

    # Top Context Header Box
    draw_cell(ax, 3.0, 89.5, 94.0, 6.5,
              r'$\mathbf{High\text{-}Dimensional\ Feature\ Selection\ Context}\ (D \gg 10^3,\ \text{e.g.},\ D = 12{,}600+\ \text{features})$' + '\n' +
              r'Current Elite Candidate Subset: $\mathbf{x}_e = [x_{e,1}, x_{e,2}, \dots, x_{e,D}] \in \{0, 1\}^D$ with optimal fitness $f(\mathbf{x}_e) = 0.0820$',
              fs=6.6, bold=True, shaded=False, lw=1.1)

    # Main Numerical Feature Table Grid (y in [43.0, 86.0])
    tbl_x = 3.0
    w_lbl = 17.0
    w_col = 13.5
    w_dots = 7.5
    
    x_lbl = tbl_x
    x_f1 = x_lbl + w_lbl            # 20.0
    x_f2 = x_f1 + w_col             # 33.5
    x_f3 = x_f2 + w_col             # 47.0
    x_f4 = x_f3 + w_col             # 60.5
    x_dots = x_f4 + w_col           # 74.0
    x_fd = x_dots + w_dots          # 81.5

    # Header Row (Feature Indices)
    h0 = 5.2
    y0 = 82.5
    draw_cell(ax, x_lbl, y0, w_lbl, h0, 'Feature Index', fs=6.5, bold=True, shaded=True)
    draw_cell(ax, x_f1, y0, w_col, h0, r'$\mathbf{Feature\ f_1}$' + '\n' + '(Core Biomarker)', fs=6.2)
    draw_cell(ax, x_f2, y0, w_col, h0, r'$\mathbf{Feature\ f_2}$' + '\n' + '(Pure Noise Gene)', fs=6.2)
    draw_cell(ax, x_f3, y0, w_col, h0, r'$\mathbf{Feature\ f_3}$' + '\n' + '(Redundant Gene)', fs=6.2)
    draw_cell(ax, x_f4, y0, w_col, h0, r'$\mathbf{Feature\ f_4}$' + '\n' + '(Synergistic Pair)', fs=6.2)
    draw_cell(ax, x_dots, y0, w_dots, h0, r'$\dots$', fs=6.8, shaded=True)
    draw_cell(ax, x_fd, y0, w_col + 2.0, h0, r'$\mathbf{Feature\ f_D}$' + '\n' + '(Background)', fs=6.2)

    # Row 1: Underlying True Contribution
    h1 = 5.2
    y1 = y0 - h1
    draw_cell(ax, x_lbl, y1, w_lbl, h1, 'True Contribution', fs=6.3, bold=True, shaded=True)
    draw_cell(ax, x_f1, y1, w_col, h1, r'$\mathbf{Strong\ Positive}$' + '\n' + '(High Relevance)', fs=5.8)
    draw_cell(ax, x_f2, y1, w_col, h1, r'$\mathbf{Strong\ Negative}$' + '\n' + '(Noise / Overfitting)', fs=5.8)
    draw_cell(ax, x_f3, y1, w_col, h1, r'$\mathbf{Negative}$' + '\n' + r'(Redundant of $f_1$)', fs=5.8)
    draw_cell(ax, x_f4, y1, w_col, h1, r'$\mathbf{Strong\ Positive}$' + '\n' + r'(Synergy with $f_1$)', fs=5.8)
    draw_cell(ax, x_dots, y1, w_dots, h1, r'$\dots$', fs=6.8, shaded=True)
    draw_cell(ax, x_fd, y1, w_col + 2.0, h1, r'$\mathbf{Neutral\ /\ Zero}$' + '\n' + '(No Correlation)', fs=5.8)

    # Row 2: Current Elite Selection State x_e
    h2 = 4.8
    y2 = y1 - h2
    draw_cell(ax, x_lbl, y2, w_lbl, h2, r'Current Subset $\mathbf{x}_e$', fs=6.3, bold=True, shaded=True)
    draw_cell(ax, x_f1, y2, w_col, h2, r'$\mathbf{1\ (Selected)}$', fs=6.2, bold=True)
    draw_cell(ax, x_f2, y2, w_col, h2, r'$\mathbf{0\ (Excluded)}$', fs=6.2)
    draw_cell(ax, x_f3, y2, w_col, h2, r'$\mathbf{0\ (Excluded)}$', fs=6.2)
    draw_cell(ax, x_f4, y2, w_col, h2, r'$\mathbf{1\ (Selected)}$', fs=6.2, bold=True)
    draw_cell(ax, x_dots, y2, w_dots, h2, r'$\dots$', fs=6.8, shaded=True)
    draw_cell(ax, x_fd, y2, w_col + 2.0, h2, r'$\mathbf{0\ (Excluded)}$', fs=6.2)

    # Row 3: Conventional Random Bit Mutation (1/D stochastic flip)
    h3 = 6.2
    y3 = y2 - h3
    draw_cell(ax, x_lbl, y3, w_lbl, h3, r'$\mathbf{Conventional\ Mutation}$' + '\n' + r'(Uniform $p_{\mathrm{mut}} = 1/D$)', fs=6.0, bold=True, shaded=True)
    draw_cell(ax, x_f1, y3, w_col, h3, r'$\mathbf{Blind\ Flip:\ 1 \rightarrow 0}$' + '\n' + '(Mistakenly Pruned)', fs=5.8, bold=True)
    draw_cell(ax, x_f2, y3, w_col, h3, r'$\mathbf{Blind\ Flip:\ 0 \rightarrow 1}$' + '\n' + '(Mistakenly Activated)', fs=5.8, bold=True)
    draw_cell(ax, x_f3, y3, w_col, h3, r'$0 \rightarrow 0$' + '\n' + '(No flip)', fs=5.8)
    draw_cell(ax, x_f4, y3, w_col, h3, r'$1 \rightarrow 1$' + '\n' + '(No flip)', fs=5.8)
    draw_cell(ax, x_dots, y3, w_dots, h3, r'$\dots$', fs=6.8, shaded=True)
    draw_cell(ax, x_fd, y3, w_col + 2.0, h3, r'$0 \rightarrow 0$' + '\n' + '(No flip)', fs=5.8)

    # Row 4: Physical Search Lesion (The Why)
    h4 = 11.5
    y4 = y3 - h4
    draw_cell(ax, x_lbl, y4, w_lbl, h4, 'Physical Search Lesion\n(The "Why")', fs=6.2, bold=True, shaded=True)
    draw_cell(ax, x_f1, y4, w_col, h4, r'$\mathbf{[Lesion\ 1]\ Fatal\ Loss:}$' + '\n' + 'Critical biomarker\nis discarded; accuracy\ncollapses drastically\n' + r'($\Delta\mathrm{Acc} = -14.2\%$)', fs=5.4)
    draw_cell(ax, x_f2, y4, w_col, h4, r'$\mathbf{[Lesion\ 2]\ Noise\ Influx:}$' + '\n' + 'Noisy gene activated;\nbloats feature subset\nand induces severe\noverfitting', fs=5.4)
    draw_cell(ax, x_f3, y4, w_col, h4, 'Redundant gene\nremains unpruned;\nwastes model budget', fs=5.5)
    draw_cell(ax, x_f4, y4, w_col, h4, r'Synergy with $f_1$' + '\nis destroyed due to\nthe loss of ' + r'$f_1$', fs=5.5)
    draw_cell(ax, x_dots, y4, w_dots, h4, r'$\dots$', fs=6.8, shaded=True)
    draw_cell(ax, x_fd, y4, w_col + 2.0, h4, 'Vast background\nremains unguided\nby fitness memory', fs=5.5)

    # Row 5: Resulting Degraded Candidate Vector
    h5 = 5.6
    y5 = y4 - h5
    draw_cell(ax, x_lbl, y5, w_lbl, h5, r"Resulting Mutant $\mathbf{x}'$", fs=6.2, bold=True, shaded=True)
    draw_cell(ax, x_f1, y5, 94.0 - w_lbl, h5,
              r"$\mathbf{x}' = [0, 1, 0, 1, \dots, 0] \in \{0, 1\}^D \quad \Longrightarrow \quad \mathbf{Degraded\ Fitness:}\ f(\mathbf{x}') = 0.2250 \gg f(\mathbf{x}_e) = 0.0820$" + "\n" +
              r"(Destructive Trial: Massive Evaluation Overhead Incurred with Zero Exploration Progress)", fs=6.0, bold=True)

    # Bottom Theoretical Summary Container
    c_y = 3.5
    c_h = 37.0
    draw_dashed_container(ax, 3.0, c_y, 94.0, c_h,
                          r'Theoretical Bottlenecks of Blind Perturbations in Ultra-High-Dimensional Spaces ($D \gg 10^3$)', lw=1.0, title_fs=7.8)

    # Sub-box 1: Hit Probability
    s_w = 44.5
    s_h = 14.5
    s_y1 = 20.0
    draw_cell(ax, 5.5, s_y1, s_w, s_h,
              r'$\mathbf{Bottleneck\ 1:\ Infinitesimal\ Probability\ of\ Beneficial\ Modification}$' + '\n' +
              r'In spaces with $D \geq 10^4$ dimensions, the combinatorial neighborhood is $2^D$. An undirected random' + '\n' +
              r'bit flip has an infinitesimal hit probability $\mathcal{O}(1/D) \approx 10^{-4}$ of modifying the few decisive' + '\n' +
              r'biomarkers, while having an overwhelming probability $(1 - d^{\star}/D) \approx 99.8\%$ of perturbing irrelevant noise.', fs=5.8)

    # Sub-box 2: Search Amnesia
    draw_cell(ax, 52.0, s_y1, s_w, s_h,
              r'$\mathbf{Bottleneck\ 2:\ Memoryless\ Search\ Amnesia}$' + '\n' +
              r'Standard meta-heuristics immediately discard the fitness evaluation feedback of trial solutions after' + '\n' +
              r'particle updates. The optimizer fails to accumulate historical knowledge regarding which features systematically' + '\n' +
              r'improved classification accuracy versus which features induced error spikes.', fs=5.8)

    # Sub-box 3: KDS-EL Closed Loop
    draw_cell(ax, 5.5, 5.5, 90.0, 12.5,
              r'$\mathbf{The\ KDS\text{-}EL\ Theoretical\ Closed\text{-}Loop\ Solution\ (Section\ 3.3)}$' + '\n' +
              r'KDS-EL resolves these dilemmas through a closed loop: cumulative trial feedback is preserved in the continuous importance' + '\n' +
              r'vector $\mathbf{W} \in \mathbb{R}^D$ with exponential decay $\gamma = 0.99$. The KER operator computes directional scores $\sigma_j = (1 - 2x_{e,j}) \cdot W_j$' + '\n' +
              r'to deterministically prune weak features ($1 \rightarrow 0$) and add strong features ($0 \rightarrow 1$) under bounded computational cost ($k_e \ll N$).', fs=5.8, bold=True)

    # Save Output
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    tex_fig_dir = os.path.join(base_dir, 'Template-LaTeX-Elsevier-CAS-DC-master', 'figs')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tex_fig_dir, exist_ok=True)

    pdf_path = os.path.join(out_dir, 'F4_lesion_why_journal.pdf')
    png_path = os.path.join(out_dir, 'F4_lesion_why_journal.png')
    tex_pdf_path = os.path.join(tex_fig_dir, 'Fig4.pdf')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.savefig(tex_pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f'Successfully generated EMSWOA-Exact Figure 4 Lesion at:\n- {pdf_path}\n- {png_path}\n- {tex_pdf_path}')

if __name__ == '__main__':
    create_figure4_lesion()
