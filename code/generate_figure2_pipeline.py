import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, w, h, text, fs=7.0, bold=False):
    rect = patches.Rectangle((x, y), w, h, linewidth=0.9, edgecolor='#000000',
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

def draw_dashed_container(ax, x, y, w, h, title, lw=1.0, title_fs=8.5):
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor='#000000',
                             facecolor='none', linestyle=(0, (6, 4)), zorder=1)
    ax.add_patch(rect)
    ax.text(x + w/2.0, y + h - 2.8, title, ha='center', va='top',
            fontsize=title_fs, color='#000000', fontweight='bold', zorder=2)
    return rect

def create_figure2():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
    plt.rcParams['mathtext.fontset'] = 'stix'

    fig, ax = plt.subplots(figsize=(11.0, 7.5), dpi=300)
    ax.set_xlim(1.5, 98.5)
    ax.set_ylim(2.5, 97.5)
    ax.axis('off')

    arr_lw = 0.75

    # =========================================================================
    # LEFT PANEL: (a) Prior-Guided Sparse Population Initialization
    # x in [3.0, 48.5], width = 45.5, y in [4.0, 96.0], height = 92.0
    # =========================================================================
    p1_x = 3.0
    p1_w = 46.0
    p1_y = 4.0
    p1_h = 92.0
    p1_cx = p1_x + p1_w / 2.0  # 26.0

    draw_dashed_container(ax, p1_x, p1_y, p1_w, p1_h, 
                          '(a) Prior-guided sparse population initialization', lw=1.0, title_fs=8.2)

    # Step A1: Training Dataset Input
    a1_w = 40.0
    a1_h = 4.8
    a1_y = 85.0
    draw_box(ax, p1_cx - a1_w/2.0, a1_y, a1_w, a1_h,
             r'Training dataset $\mathcal{D} = \{(\mathbf{f}_i, y_i)\}_{i=1}^{N_{\mathrm{samp}}}$ with $N_{\mathrm{samp}}$ samples and $D$ features', fs=6.8)

    # Down arrow to A2
    ax.annotate('', xy=(p1_cx, 76.5 + 4.8), xytext=(p1_cx, a1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step A2: MI Calculation & Normalization
    a2_y = 76.5
    draw_box(ax, p1_cx - a1_w/2.0, a2_y, a1_w, a1_h,
             r'Mutual information quantification & normalization to prior profile $\mathbf{m} \in [0, 1]^D$', fs=6.8)

    # Down arrow to A3
    ax.annotate('', xy=(p1_cx, 68.0 + 4.8), xytext=(p1_cx, a2_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step A3: Hybrid Seeding Strategy Dispatcher
    a3_y = 68.0
    draw_box(ax, p1_cx - a1_w/2.0, a3_y, a1_w, a3_h:=4.8,
             r'Hybrid population seeding strategy (Swarm size $N$, prior seeding ratio $\rho \in (0, 1)$)', fs=6.8)

    # Sub-columns for Guided vs Uniform Seeds
    sub_w = 18.5
    sub_l_cx = p1_x + 3.0 + sub_w/2.0  # 15.25
    sub_r_cx = p1_x + p1_w - 3.0 - sub_w/2.0  # 36.75

    # Connect A3 to Left and Right sub-branches
    ax.plot([p1_cx, sub_l_cx, sub_l_cx], [a3_y, a3_y - 2.0, 59.5 + 5.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(sub_l_cx, 59.5 + 5.0), xytext=(sub_l_cx, 59.5 + 5.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([p1_cx, sub_r_cx, sub_r_cx], [a3_y, a3_y - 2.0, 59.5 + 5.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(sub_r_cx, 59.5 + 5.0), xytext=(sub_r_cx, 59.5 + 5.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Branch A-Left: Guided Seeds
    al1_y = 59.5
    al1_h = 5.0
    draw_box(ax, sub_l_cx - sub_w/2.0, al1_y, sub_w, al1_h,
             r'Prior-guided candidate seeding' + '\n' + r'($\lfloor \rho N \rfloor$ particles)', fs=6.2)

    al2_y = 50.5
    al2_h = 6.8
    draw_box(ax, sub_l_cx - sub_w/2.0, al2_y, sub_w, al2_h,
             r'Gaussian coordinate perturbation:' + '\n' + 
             r'$\mathbf{p}_i = \mathrm{clip}(\mathbf{m} + \boldsymbol{\varepsilon}_i, 0, 1)$' + '\n' + 
             r'$\boldsymbol{\varepsilon}_i \sim \mathcal{N}(\mathbf{0}, \sigma^2 \mathbf{I}_D)$', fs=5.8)
    ax.annotate('', xy=(sub_l_cx, al2_y + al2_h), xytext=(sub_l_cx, al1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Branch A-Right: Uniform Stochastic Seeds
    draw_box(ax, sub_r_cx - sub_w/2.0, al1_y, sub_w, al1_h,
             r'Uniform stochastic exploration' + '\n' + r'($(N - \lfloor \rho N \rfloor)$ particles)', fs=6.2)

    draw_box(ax, sub_r_cx - sub_w/2.0, al2_y, sub_w, al2_h,
             r'Uniform coordinate sampling:' + '\n' + 
             r'$\mathbf{p}_i = \mathbf{u}_i$' + '\n' + 
             r'$\mathbf{u}_i \sim \mathcal{U}(0, 1)^D$', fs=6.0)
    ax.annotate('', xy=(sub_r_cx, al2_y + al2_h), xytext=(sub_r_cx, al1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Converge Left and Right branches to A4 (Binarization)
    a4_y = 40.0
    a4_h = 5.8
    ax.plot([sub_l_cx, sub_l_cx, p1_cx], [al2_y, al2_y - 2.4, al2_y - 2.4], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([sub_r_cx, sub_r_cx, p1_cx], [al2_y, al2_y - 2.4, al2_y - 2.4], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(p1_cx, a4_y + a4_h), xytext=(p1_cx, al2_y - 2.4),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step A4: Deterministic Step Binarization
    draw_box(ax, p1_cx - a1_w/2.0, a4_y, a1_w, a4_h,
             r'Deterministic Heaviside step binarization with threshold $\theta > 0.50$:' + '\n' + 
             r'$x_{i,j} = 1$ if $p_{i,j} \geq \theta$, else $0$', fs=6.5)

    # Down arrow to A5
    ax.annotate('', xy=(p1_cx, 30.5 + 5.5), xytext=(p1_cx, a4_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step A5: Initial Population Matrix Output
    a5_y = 30.5
    a5_h = 5.5
    draw_box(ax, p1_cx - a1_w/2.0, a5_y, a1_w, a5_h,
             r'Initial sparse population matrix $\mathbf{X} \in \{0, 1\}^{N \times D}$' + '\n' + 
             r'($d \ll D/2$, intrinsically focused on high-relevance biomarker subspace)', fs=6.4)

    # Down arrow to A6
    ax.annotate('', xy=(p1_cx, 21.0 + 5.5), xytext=(p1_cx, a5_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step A6: Initial Evaluation & Objective Assignment
    a6_y = 21.0
    a6_h = 5.5
    draw_box(ax, p1_cx - a1_w/2.0, a6_y, a1_w, a6_h,
             r'Evaluate initial candidate fitness under TPS objective weights $\mathbf{w}(1)$' + '\n' + 
             r'and initialize personal bests $\{\mathbf{p}_{\mathrm{best},i}\}$ and global best $\mathbf{g}_{\mathrm{best}}$', fs=6.3)

    # Down arrow to A7
    ax.annotate('', xy=(p1_cx, 11.5 + 5.5), xytext=(p1_cx, a6_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step A7: Ready for Co-Evolution
    a7_y = 11.5
    a7_h = 5.5
    draw_box(ax, p1_cx - a1_w/2.0, a7_y, a1_w, a7_h,
             r'Transfer sparse initialized population into dual collaborative' + '\n' + 
             r'subpopulations $\mathcal{P}_1$ (Continuous Explorer) & $\mathcal{P}_2$ (Discrete Exploiter)', fs=6.3)

    # =========================================================================
    # RIGHT PANEL: (b) Adaptive Stagnation Recovery via Diversity Re-Injection
    # x in [51.0, 97.0], width = 46.0, y in [4.0, 96.0], height = 92.0
    # =========================================================================
    p2_x = 51.0
    p2_w = 46.0
    p2_cx = p2_x + p2_w / 2.0  # 74.0

    draw_dashed_container(ax, p2_x, p1_y, p2_w, p1_h, 
                          '(b) Adaptive stagnation recovery via diversity re-injection', lw=1.0, title_fs=8.2)

    # Step B1: Stagnation Detection Trigger
    b1_y = 85.0
    draw_box(ax, p2_cx - a1_w/2.0, b1_y, a1_w, a1_h,
             r'Evolutionary progress monitoring: Global-best fitness $f_{\mathrm{gbest}}$ fails to improve', fs=6.8)

    # Down arrow to B2 (Diamond)
    ax.annotate('', xy=(p2_cx, 75.8 + 3.0), xytext=(p2_cx, b1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step B2: Stagnation Decision Diamond
    b2_cy = 75.8
    b2_w = 15.0
    b2_h = 6.0
    draw_diamond(ax, p2_cx, b2_cy, b2_w, b2_h, r'$t_{\mathrm{stag}} \geq \tau$', fs=7.2)

    # Y branch (Down): Trigger recovery
    ax.text(p2_cx + 0.6, b2_cy - b2_h/2.0 - 1.2, 'Y', fontsize=7.2, fontweight='bold')
    # N branch (Right): Bypass recovery
    ax.text(p2_cx + b2_w/2.0 + 0.6, b2_cy + 0.6, 'N', fontsize=7.2, fontweight='bold')

    # Step B3: Sort Particles by Fitness
    b3_y = 65.5
    draw_box(ax, p2_cx - a1_w/2.0, b3_y, a1_w, a1_h,
             r'Sort all $N$ particles in ascending order of personal-best fitness values $f(\mathbf{p}_{\mathrm{best},i})$', fs=6.6)
    ax.annotate('', xy=(p2_cx, b3_y + a1_h), xytext=(p2_cx, b2_cy - b2_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Sub-columns for Superior Elite Half vs Inferior Stagnant Half
    sub2_l_cx = p2_x + 3.0 + sub_w/2.0  # 63.25
    sub2_r_cx = p2_x + p2_w - 3.0 - sub_w/2.0  # 84.75

    # Connect B3 to Left and Right sub-branches
    ax.plot([p2_cx, sub2_l_cx, sub2_l_cx], [b3_y, b3_y - 2.0, 56.5 + 5.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(sub2_l_cx, 56.5 + 5.0), xytext=(sub2_l_cx, 56.5 + 5.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    ax.plot([p2_cx, sub2_r_cx, sub2_r_cx], [b3_y, b3_y - 2.0, 56.5 + 5.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(sub2_r_cx, 56.5 + 5.0), xytext=(sub2_r_cx, 56.5 + 5.3),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Branch B-Left: Superior Elite Half
    bl1_y = 56.5
    draw_box(ax, sub2_l_cx - sub_w/2.0, bl1_y, sub_w, al1_h,
             r'Superior half sub-swarm' + '\n' + r'(Top $N/2$ elite particles)', fs=6.2)

    bl2_y = 47.0
    bl2_h = 7.2
    draw_box(ax, sub2_l_cx - sub_w/2.0, bl2_y, sub_w, bl2_h,
             r'Preserve intact without change:' + '\n' + 
             r'safeguard verified biomarker' + '\n' + 
             r'synergies & historical trajectory', fs=5.8)
    ax.annotate('', xy=(sub2_l_cx, bl2_y + bl2_h), xytext=(sub2_l_cx, bl1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Branch B-Right: Inferior Stagnant Half Re-seeding
    draw_box(ax, sub2_r_cx - sub_w/2.0, bl1_y, sub_w, al1_h,
             r'Inferior half sub-swarm' + '\n' + r'(Bottom $N/2$ stagnant particles)', fs=6.2)

    draw_box(ax, sub2_r_cx - sub_w/2.0, bl2_y, sub_w, bl2_h,
             r'Targeted Gaussian prior re-injection:' + '\n' + 
             r'$\mathbf{p}_i \leftarrow \mathrm{clip}(\mathbf{m} + \boldsymbol{\varepsilon}_i, 0, 1)$' + '\n' + 
             r'$x_{i,j} \leftarrow 1$ if $p_{i,j} \geq \theta$, else $0$', fs=5.8)
    ax.annotate('', xy=(sub2_r_cx, bl2_y + bl2_h), xytext=(sub2_r_cx, bl1_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Converge Left and Right branches to B4 (Recombination)
    b4_y = 36.5
    b4_h = 5.5
    ax.plot([sub2_l_cx, sub2_l_cx, p2_cx], [bl2_y, bl2_y - 2.4, bl2_y - 2.4], color='#000000', lw=arr_lw, zorder=4)
    ax.plot([sub2_r_cx, sub2_r_cx, p2_cx], [bl2_y, bl2_y - 2.4, bl2_y - 2.4], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(p2_cx, b4_y + b4_h), xytext=(p2_cx, bl2_y - 2.4),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step B4: Recombine Swarm
    draw_box(ax, p2_cx - a1_w/2.0, b4_y, a1_w, b4_h,
             r'Recombine retained elite half and refreshed prior half into recovered population $\mathcal{P}$', fs=6.5)

    # Down arrow to B5
    ax.annotate('', xy=(p2_cx, 26.5 + 5.5), xytext=(p2_cx, b4_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step B5: Re-evaluation & Stagnation Reset
    b5_y = 26.5
    b5_h = 5.5
    draw_box(ax, p2_cx - a1_w/2.0, b5_y, a1_w, b5_h,
             r'Re-evaluate objective fitness of refreshed particles & reset stagnation counter: $t_{\mathrm{stag}} \leftarrow 0$', fs=6.5)

    # Down arrow to B6
    ax.annotate('', xy=(p2_cx, 16.5 + 5.5), xytext=(p2_cx, b5_y),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)

    # Step B6: Diversity Restored
    b6_y = 16.5
    b6_h = 5.5
    draw_box(ax, p2_cx - a1_w/2.0, b6_y, a1_w, b6_h,
             r'Exploratory diversity successfully restored within high-potential biomarker subspace;' + '\n' + 
             r'swarm resumes dual collaborative co-evolution', fs=6.3)

    # N Branch Bypass from Stagnation Diamond (t_stag < tau)
    bypass_x = p2_x + p2_w - 1.5
    ax.plot([p2_cx + b2_w/2.0, bypass_x, bypass_x, p2_cx + a1_w/2.0],
            [b2_cy, b2_cy, b6_y + b6_h/2.0, b6_y + b6_h/2.0], color='#000000', lw=arr_lw, zorder=4)
    ax.annotate('', xy=(p2_cx + a1_w/2.0, b6_y + b6_h/2.0), xytext=(p2_cx + a1_w/2.0 + 0.3, b6_y + b6_h/2.0),
                arrowprops=dict(arrowstyle='->', color='#000000', lw=arr_lw), zorder=4)
    ax.text(bypass_x - 0.8, (b2_cy + b6_y)/2.0, r'Continue normal evolution', fontsize=6.2, rotation=90, va='center', ha='right')

    # Save Output
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'output', 'figures')
    tex_fig_dir = os.path.join(base_dir, 'Template-LaTeX-Elsevier-CAS-DC-master', 'figs')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(tex_fig_dir, exist_ok=True)

    pdf_path = os.path.join(out_dir, 'F2_mi_initialization_journal.pdf')
    png_path = os.path.join(out_dir, 'F2_mi_initialization_journal.png')
    tex_pdf_path = os.path.join(tex_fig_dir, 'Fig2.pdf')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)
    plt.savefig(tex_pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f'Successfully generated 100% EMSWOA-Exact Figure 2 at:\n- {pdf_path}\n- {png_path}\n- {tex_pdf_path}')

if __name__ == '__main__':
    create_figure2()
