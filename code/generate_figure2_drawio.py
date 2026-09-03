import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def generate_figure2_drawio_xml():
    mxfile = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f2-mi-initialization-recovery', name='Figure 2: MII Seeding and Adaptive Stagnation Recovery')
    graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                dx='1000', dy='1000', grid='1', gridSize='10', 
                                guides='1', tooltips='1', connect='1', arrows='1', 
                                fold='1', page='1', pageScale='1', pageWidth='1060', pageHeight='720', 
                                math='1', shadow='0')
    root = ET.SubElement(graph_model, 'root')
    
    ET.SubElement(root, 'mxCell', id='0')
    ET.SubElement(root, 'mxCell', id='1', parent='0')

    def add_node(node_id, value, style, x, y, w, h):
        cell = ET.SubElement(root, 'mxCell', id=node_id, value=value, style=style, parent='1', vertex='1')
        ET.SubElement(cell, 'mxGeometry', x=str(round(x, 1)), y=str(round(y, 1)), 
                      width=str(round(w, 1)), height=str(round(h, 1)), **{'as': 'geometry'})
        return cell

    def add_edge(edge_id, value, style, source_id, target_id, points=None):
        cell = ET.SubElement(root, 'mxCell', id=edge_id, value=value, style=style, parent='1', edge='1')
        if source_id:
            cell.set('source', source_id)
        if target_id:
            cell.set('target', target_id)
        geo = ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
        if points:
            pts_elem = ET.SubElement(geo, 'Array', **{'as': 'points'})
            for px, py in points:
                ET.SubElement(pts_elem, 'mxPoint', x=str(round(px, 1)), y=str(round(py, 1)))
        return cell

    # Academic Monochrome Styles (EMSWOA Standard)
    s_box = 'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_diamond = 'rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_container = 'rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor=none;strokeColor=#000000;strokeWidth=1.2;verticalAlign=top;spacingTop=8;fontSize=11;fontStyle=1;fontFamily=Times New Roman;pointerEvents=0;'
    s_edge = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1;endArrow=classic;endFill=1;fontSize=10;fontFamily=Times New Roman;'

    # =========================================================================
    # LEFT PANEL: (a) Prior-Guided Sparse Population Initialization
    # x in [30, 520], width = 490, y in [20, 680], height = 660
    # =========================================================================
    p1_x = 30
    p1_w = 490
    p1_cx = p1_x + p1_w / 2.0  # 275
    add_node('c_panel_a', '(a) Prior-guided sparse population initialization', s_container, p1_x, 20, p1_w, 660)

    # Step A1: Training Dataset Input
    add_node('na_data', 'Training dataset <i>D</i> = {(<b><i>f</i></b><sub><i>i</i></sub>, <i>y</i><sub><i>i</i></sub>)} with <i>N</i><sub>samp</sub> samples &amp; <i>D</i> features', s_box, p1_cx - 215, 60, 430, 36)
    
    # Step A2: MI Calculation & Normalization
    add_node('na_mi', 'Mutual information quantification &amp; normalization to prior relevance profile <b><i>m</i></b> &in; [0, 1]<sup><i>D</i></sup>', s_box, p1_cx - 215, 122, 430, 36)
    add_edge('ea_data_mi', '', s_edge, 'na_data', 'na_mi')

    # Step A3: Hybrid Seeding Strategy Dispatcher
    add_node('na_seed_disp', 'Hybrid population seeding strategy (Swarm size <i>N</i>, seeding ratio &rho; &in; (0, 1))', s_box, p1_cx - 215, 184, 430, 36)
    add_edge('ea_mi_disp', '', s_edge, 'na_mi', 'na_seed_disp')

    # Two Parallel Branches under Seeding Dispatcher
    sub_w = 205
    sub_l_x = p1_x + 30
    sub_r_x = p1_x + p1_w - 30 - sub_w

    # Branch A-Left: Guided Seeds
    add_node('na_guided_title', 'Prior-guided candidate seeding&#xa;(&lfloor;&rho;<i>N</i>&rfloor; particles)', s_box, sub_l_x, 246, sub_w, 38)
    add_node('na_guided_pert', 'Gaussian continuous coordinate perturbation:&#xa;<b><i>p</i></b><sub><i>i</i></sub> = clip(<b><i>m</i></b> + <b><i>&epsilon;</i></b><sub><i>i</i></sub>, 0, 1), <b><i>&epsilon;</i></b><sub><i>i</i></sub> ~ &Nscr;(<b>0</b>, &sigma;<sup>2</sup><b><i>I</i></b><sub><i>D</i></sub>)', s_box, sub_l_x, 308, sub_w, 52)
    add_edge('ea_disp_guided', '', s_edge, 'na_seed_disp', 'na_guided_title', [(p1_cx, 230), (sub_l_x + sub_w/2.0, 230)])
    add_edge('ea_gtitle_pert', '', s_edge, 'na_guided_title', 'na_guided_pert')

    # Branch A-Right: Uniform Stochastic Seeds
    add_node('na_unif_title', 'Uniform stochastic exploration&#xa;(<i>N</i> - &lfloor;&rho;<i>N</i>&rfloor; particles)', s_box, sub_r_x, 246, sub_w, 38)
    add_node('na_unif_samp', 'Uniform random continuous coordinate sampling:&#xa;<b><i>p</i></b><sub><i>i</i></sub> = <b><i>u</i></b><sub><i>i</i></sub>, <b><i>u</i></b><sub><i>i</i></sub> ~ &Uscr;(0, 1)<sup><i>D</i></sup>', s_box, sub_r_x, 308, sub_w, 52)
    add_edge('ea_disp_unif', '', s_edge, 'na_seed_disp', 'na_unif_title', [(p1_cx, 230), (sub_r_x + sub_w/2.0, 230)])
    add_edge('ea_utitle_samp', '', s_edge, 'na_unif_title', 'na_unif_samp')

    # Step A4: Deterministic Step Binarization
    add_node('na_bin', 'Deterministic Heaviside step binarization with threshold &theta; &gt; 0.50:&#xa;<i>x</i><sub><i>i</i>,<i>j</i></sub> = 1 if <i>p</i><sub><i>i</i>,<i>j</i></sub> &ge; &theta;, else 0', s_box, p1_cx - 215, 390, 430, 42)
    add_edge('ea_gpert_bin', '', s_edge, 'na_guided_pert', 'na_bin', [(sub_l_x + sub_w/2.0, 375), (p1_cx, 375)])
    add_edge('ea_usamp_bin', '', s_edge, 'na_unif_samp', 'na_bin', [(sub_r_x + sub_w/2.0, 375), (p1_cx, 375)])

    # Step A5: Initial Population Matrix Output
    add_node('na_pop', 'Initial sparse population matrix <b><i>X</i></b> &in; {0, 1}<sup><i>N</i> &times; <i>D</i></sup>&#xa;(<i>d</i> &ll; <i>D</i>/2, focused biomarker subspace)', s_box, p1_cx - 215, 460, 430, 42)
    add_edge('ea_bin_pop', '', s_edge, 'na_bin', 'na_pop')

    # Step A6: Initial Evaluation & Objective Assignment
    add_node('na_eval', 'Evaluate initial candidate fitness under TPS objective weights <b><i>w</i></b>(1)&#xa;and initialize personal bests {<b><i>p</i></b><sub>best,<i>i</i></sub>} and global best <b><i>g</i></b><sub>best</sub>', s_box, p1_cx - 215, 530, 430, 42)
    add_edge('ea_pop_eval', '', s_edge, 'na_pop', 'na_eval')

    # Step A7: Ready for Co-Evolution
    add_node('na_ready', 'Transfer sparse initialized population into dual collaborative subpopulations &Pscr;<sub>1</sub> &amp; &Pscr;<sub>2</sub>', s_box, p1_cx - 215, 600, 430, 42)
    add_edge('ea_eval_ready', '', s_edge, 'na_eval', 'na_ready')

    # =========================================================================
    # RIGHT PANEL: (b) Adaptive Stagnation Recovery via Diversity Re-Injection
    # x in [540, 1030], width = 490, y in [20, 680], height = 660
    # =========================================================================
    p2_x = 540
    p2_w = 490
    p2_cx = p2_x + p2_w / 2.0  # 785
    add_node('c_panel_b', '(b) Adaptive stagnation recovery via diversity re-injection', s_container, p2_x, 20, p2_w, 660)

    # Step B1: Stagnation Detection Trigger
    add_node('nb_stag_eval', 'Evolutionary progress monitoring: global best fitness fails to improve', s_box, p2_cx - 215, 60, 430, 36)
    
    # Step B2: Stagnation Decision Diamond
    add_node('nb_dia_stag', '<i>t</i><sub>stag</sub> &ge; &tau;', s_diamond, p2_cx - 70, 116, 140, 44)
    add_edge('eb_eval_dia', '', s_edge, 'nb_stag_eval', 'nb_dia_stag')

    # Step B3: Sort Particles by Fitness
    add_node('nb_sort', 'Sort all <i>N</i> particles in ascending order of personal-best fitness values <i>f</i>(<b><i>p</i></b><sub>best,<i>i</i></sub>)', s_box, p2_cx - 215, 184, 430, 36)
    add_edge('eb_dia_sort', '<b>Y</b>', s_edge, 'nb_dia_stag', 'nb_sort')

    # Two Parallel Branches under Sorting (Elite Preservation vs Stagnant Re-seeding)
    sub2_w = 205
    sub2_l_x = p2_x + 30
    sub2_r_x = p2_x + p2_w - 30 - sub2_w

    # Branch B-Left: Superior Half (Elites)
    add_node('nb_elite_title', 'Superior half sub-swarm&#xa;(Top <i>N</i>/2 elite particles)', s_box, sub2_l_x, 246, sub2_w, 38)
    add_node('nb_elite_keep', 'Retain intact without modification:&#xa;safeguard verified biomarker combinations&#xa;and historical optimization trajectory', s_box, sub2_l_x, 308, sub2_w, 52)
    add_edge('eb_sort_elite', '', s_edge, 'nb_sort', 'nb_elite_title', [(p2_cx, 230), (sub2_l_x + sub2_w/2.0, 230)])
    add_edge('eb_etitle_keep', '', s_edge, 'nb_elite_title', 'nb_elite_keep')

    # Branch B-Right: Inferior Half (Stagnant Particles Re-injection)
    add_node('nb_stagnant_title', 'Inferior half sub-swarm&#xa;(Bottom <i>N</i>/2 stagnant particles)', s_box, sub2_r_x, 246, sub2_w, 38)
    add_node('nb_stagnant_reseed', 'Targeted Gaussian prior re-injection:&#xa;<b><i>p</i></b><sub><i>i</i></sub> &larr; clip(<b><i>m</i></b> + <b><i>&epsilon;</i></b><sub><i>i</i></sub>, 0, 1), <b><i>&epsilon;</i></b><sub><i>i</i></sub> ~ &Nscr;(<b>0</b>, &sigma;<sup>2</sup><b><i>I</i></b><sub><i>D</i></sub>)&#xa;<i>x</i><sub><i>i</i>,<i>j</i></sub> &larr; 1 if <i>p</i><sub><i>i</i>,<i>j</i></sub> &ge; &theta;, else 0', s_box, sub2_r_x, 308, sub2_w, 52)
    add_edge('eb_sort_stag', '', s_edge, 'nb_sort', 'nb_stagnant_title', [(p2_cx, 230), (sub2_r_x + sub2_w/2.0, 230)])
    add_edge('eb_stitle_reseed', '', s_edge, 'nb_stagnant_title', 'nb_stagnant_reseed')

    # Step B4: Recombine Swarm
    add_node('nb_recombine', 'Recombine retained elite half and refreshed prior half into recovered population &Pscr;', s_box, p2_cx - 215, 390, 430, 42)
    add_edge('eb_elite_recomb', '', s_edge, 'nb_elite_keep', 'nb_recombine', [(sub2_l_x + sub2_w/2.0, 375), (p2_cx, 375)])
    add_edge('eb_reseed_recomb', '', s_edge, 'nb_stagnant_reseed', 'nb_recombine', [(sub2_r_x + sub2_w/2.0, 375), (p2_cx, 375)])

    # Step B5: Re-evaluation & Stagnation Reset
    add_node('nb_reeval', 'Re-evaluate objective fitness of refreshed candidate particles&#xa;and reset stagnation counter: <i>t</i><sub>stag</sub> &larr; 0', s_box, p2_cx - 215, 460, 430, 42)
    add_edge('eb_recomb_reeval', '', s_edge, 'nb_recombine', 'nb_reeval')

    # Step B6: Diversity Restored
    add_node('nb_restored', 'Exploratory diversity successfully restored within high-potential subspace;&#xa;swarm resumes dual collaborative co-evolution', s_box, p2_cx - 215, 530, 430, 42)
    add_edge('eb_reeval_restored', '', s_edge, 'nb_reeval', 'nb_restored')

    # Normal bypass branch from Diamond (N: t_stag < tau)
    add_edge('eb_dia_bypass', '<b>N</b> (Continue normal evolution)', s_edge, 'nb_dia_stag', 'nb_restored', [(p2_cx + 70, 138), (p2_x + p2_w - 15, 138), (p2_x + p2_w - 15, 551), (p2_cx + 215, 551)])

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')

if __name__ == '__main__':
    xml_content = generate_figure2_drawio_xml()
    base_dir = r'e:\多目标优化\KDS-EL'
    target_files = [
        os.path.join(base_dir, 'output', 'figures', 'F2_mi_initialization_journal.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F2_mi_seeding_recovery.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F2_mi_initialization.drawio')
    ]
    
    for tf in target_files:
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f'Successfully updated: {tf}')
