import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def generate_drawio_xml():
    mxfile = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f1-kds-el-architecture', name='Figure 1: KDS-EL Architecture')
    graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                dx='1000', dy='1000', grid='1', gridSize='10', 
                                guides='1', tooltips='1', connect='1', arrows='1', 
                                fold='1', page='1', pageScale='1', pageWidth='1050', pageHeight='1000', 
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
    s_pill = 'rounded=1;arcSize=50;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=12;fontFamily=Times New Roman;'
    s_box = 'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_diamond = 'rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_container = 'rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor=none;strokeColor=#000000;strokeWidth=1.2;verticalAlign=top;spacingTop=6;fontSize=11;fontStyle=1;fontFamily=Times New Roman;pointerEvents=0;'
    s_callout = 'shape=flexArrow;endArrow=classic;startArrow=none;html=1;fillColor=#000000;strokeColor=#000000;width=3.5;endSize=7;'
    s_edge = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1;endArrow=classic;endFill=1;fontSize=10;fontFamily=Times New Roman;'

    # -------------------------------------------------------------------------
    # LEFT COLUMN: MAIN LIFECYCLE
    # -------------------------------------------------------------------------
    add_node('n_begin', 'Begin', s_pill, 190, 10, 100, 25)
    add_node('n_params', 'Set related parameters', s_box, 110, 52, 260, 33)
    add_edge('e_begin_params', '', s_edge, 'n_begin', 'n_params')

    # 4-Box Initialization Cycle
    add_node('n_init_seed', 'Initialize candidate solutions&#xa;based on prior knowledge', s_box, 75, 115, 155, 36)
    add_node('n_init_bin', 'Convert continuous particles&#xa;to binary decision space', s_box, 250, 115, 155, 36)
    add_node('n_init_tps', 'Calculate objective fitness&#xa;under two-phase scheduling', s_box, 250, 187, 155, 36)
    add_node('n_init_opt', 'Obtain initial personal&#xa;and global best solutions', s_box, 75, 187, 155, 36)

    add_edge('e_params_init', '', s_edge, 'n_params', 'n_init_seed', [(240, 98), (152.5, 98)])
    add_edge('e_init_bin', '', s_edge, 'n_init_seed', 'n_init_bin')
    add_edge('e_bin_tps', '', s_edge, 'n_init_bin', 'n_init_tps')
    add_edge('e_tps_opt', '', s_edge, 'n_init_tps', 'n_init_opt')

    # Co-evolution Loop Anchor (y=245..295, center=(240, 270))
    add_node('n_coevol', 'Constructing and updating dual subpopulations&#xa;using collaborative co-evolution mechanism', s_box, 80, 245, 320, 50)
    add_edge('e_opt_coevol', '', s_edge, 'n_init_opt', 'n_coevol', [(152.5, 235), (240, 235)])

    # Top Callout Arrow (Perfect Horizontal Alignment from (400, 270) to (480, 270) - Midpoint of top container!)
    add_edge('e_callout_top', '', s_callout + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;entryDx=0;entryDy=0;', 'n_coevol', 'c_top_swarm')

    # TPS Decision Diamond
    add_node('n_dia_tps', '<i>t</i> &le; &tau;<i>T</i><sub>max</sub>', s_diamond, 170, 345, 140, 44)
    add_edge('e_coevol_tps', '', s_edge, 'n_coevol', 'n_dia_tps')

    add_node('n_tps_prune', 'Feature pruning phase:&#xa;penalize redundant dimensions', s_box, 75, 403, 155, 38)
    add_node('n_tps_tune', 'Accuracy tuning phase:&#xa;refine classification accuracy', s_box, 250, 403, 155, 38)

    add_edge('e_tps_prune', '<b>Y</b>', s_edge, 'n_dia_tps', 'n_tps_prune', [(170, 367), (152.5, 367)])
    add_edge('e_tps_tune', '<b>N</b>', s_edge, 'n_dia_tps', 'n_tps_tune', [(310, 367), (327.5, 367)])

    # Memory Matrix Update Box
    add_node('n_mem_w', 'Updating cumulative feature-importance matrix <b><i>W</i></b>&#xa;with evolutionary fitness feedback and memory decay', s_box, 80, 475, 320, 44)
    add_edge('e_prune_mem', '', s_edge, 'n_tps_prune', 'n_mem_w', [(152.5, 455), (240, 455)])
    add_edge('e_tune_mem', '', s_edge, 'n_tps_tune', 'n_mem_w', [(327.5, 455), (240, 455)])

    # KER Anchor Box (y=655..705, center=(240, 680))
    add_node('n_ker_anchor', 'Updating candidate feature subsets using&#xa;knowledge-guided elite refinement strategy', s_box, 80, 655, 320, 50)
    add_edge('e_mem_ker', '', s_edge, 'n_mem_w', 'n_ker_anchor')

    # Bottom Callout Arrow (Perfect Horizontal Alignment from (400, 680) to (480, 680) - Midpoint of bottom container!)
    add_edge('e_callout_bot', '', s_callout + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;entryDx=0;entryDy=0;', 'n_ker_anchor', 'c_bot_ker')

    # Stagnation Diamond
    add_node('n_dia_stag', '<i>t</i><sub>stag</sub> &ge; &tau;', s_diamond, 170, 725, 140, 42)
    add_edge('e_ker_stag', '', s_edge, 'n_ker_anchor', 'n_dia_stag')

    add_node('n_air', 'Adaptive stagnation recovery:&#xa;re-initialize lower-half particles', s_box, 325, 727, 155, 38)
    add_edge('e_stag_air', '<b>Y</b>', s_edge, 'n_dia_stag', 'n_air')

    # Termination Diamond (t >= T_max)
    add_node('n_dia_term', '<i>t</i> &ge; <i>T</i><sub>max</sub>', s_diamond, 170, 805, 140, 42)
    add_edge('e_stag_term', '<b>N</b>', s_edge + 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;', 'n_dia_stag', 'n_dia_term')
    add_edge('e_air_term', '', s_edge + 'exitX=0.5;exitY=1;entryX=1;entryY=0.5;', 'n_air', 'n_dia_term', [(402.5, 826), (310, 826)])

    # Loopback Arrow (t <- t + 1)
    add_edge('e_loopback', '<b>N</b> &nbsp; <i>t</i> &larr; <i>t</i> + 1', s_edge + 'exitX=0;exitY=0.5;entryX=0;entryY=0.5;', 'n_dia_term', 'n_coevol', [(170, 826), (35, 826), (35, 270), (80, 270)])

    # Output Box & End
    add_node('n_output', 'Obtaining the subset of&#xa;optimal features <b><i>x</i></b><sup>&lowast;</sup> and <i>f</i><sub>gbest</sub>', s_box, 110, 868, 260, 36)
    add_edge('e_term_out', '<b>Y</b>', s_edge + 'exitX=0.5;exitY=1;entryX=0.5;entryY=0;', 'n_dia_term', 'n_output')

    add_node('n_end', 'End', s_pill, 190, 920, 100, 24)
    add_edge('e_out_end', '', s_edge, 'n_output', 'n_end')

    # -------------------------------------------------------------------------
    # RIGHT TOP CONTAINER: DUAL-SWARM COLLABORATIVE CO-EVOLUTION MECHANISM
    # (y = 105..435, height = 330, center = 270) -> EXACT MATCH WITH LEFT ANCHOR AT 270!
    # -------------------------------------------------------------------------
    add_node('c_top_swarm', 'Dual-swarm collaborative co-evolution mechanism', s_container, 480, 105, 500, 330)

    add_node('n_swarm_part', 'Swarm partitioning: &Pscr;<sub>1</sub> (Continuous Explorer) &longleftrightarrow; &Pscr;<sub>2</sub> (Discrete Exploiter)', s_box, 500, 139, 460, 34)
    add_edge('e_part_sub', '', s_edge, 'n_swarm_part', 'n_p1_update', [(607.5, 173), (607.5, 193)])
    add_edge('e_part_p2', '', s_edge, 'n_swarm_part', 'n_p2_update', [(852.5, 173), (852.5, 193)])

    add_node('n_p1_update', 'Continuous velocity &amp; position update&#xa;with inter-task knowledge transfer', s_box, 500, 193, 215, 54)
    add_node('n_p2_update', 'Dynamic selection probability&#xa;transformation derived from memory <b><i>W</i></b>', s_box, 745, 193, 215, 54)

    add_edge('e_trans_gbest2', '<b><i>g</i></b><sub>best,2</sub>', s_edge, 'n_p2_update', 'n_p1_update')

    add_node('n_p1_bin', 'Deterministic Heaviside step&#xa;binarization mapping', s_box, 500, 267, 215, 50)
    add_node('n_p2_sample', 'Discrete Bernoulli feature&#xa;sampling and bit mutation', s_box, 745, 267, 215, 50)

    add_edge('e_p1_up_bin', '', s_edge, 'n_p1_update', 'n_p1_bin')
    add_edge('e_p2_up_samp', '', s_edge, 'n_p2_update', 'n_p2_sample')

    add_node('n_joint_eval', 'Evaluate objective fitness of combined population &Pscr;<sub>1</sub> &cup; &Pscr;<sub>2</sub>&#xa;under dynamic two-phase scheduling', s_box, 500, 337, 460, 36)
    add_edge('e_p1_eval', '', s_edge, 'n_p1_bin', 'n_joint_eval', [(607.5, 317), (607.5, 327), (730, 327)])
    add_edge('e_p2_eval', '', s_edge, 'n_p2_sample', 'n_joint_eval', [(852.5, 317), (852.5, 327), (730, 327)])

    # -------------------------------------------------------------------------
    # RIGHT BOTTOM CONTAINER: KNOWLEDGE-GUIDED ELITE REFINEMENT STRATEGY
    # (y = 440..920, height = 480, center = 680) -> EXACT MATCH WITH LEFT ANCHOR AT 680!
    # -------------------------------------------------------------------------
    add_node('c_bot_ker', 'Knowledge-guided elite refinement strategy', s_container, 480, 440, 500, 480)

    add_node('n_ker_input', 'Data inputs required for the knowledge-guided elite refinement strategy', s_box, 500, 464, 460, 34)

    add_node('n_dia_rand', '<i>r</i> &lt; <i>p</i><sub>rand</sub>', s_diamond, 650, 522, 160, 40)
    add_edge('e_ker_in_dia', '', s_edge, 'n_ker_input', 'n_dia_rand')

    add_node('n_ker_rand_mut', 'Update candidate features via&#xa;ergodic random bit perturbation', s_box, 500, 576, 215, 42)
    add_edge('e_rand_y', '<b>Y</b>', s_edge, 'n_dia_rand', 'n_ker_rand_mut', [(650, 542), (607.5, 542)])

    add_node('n_dia_dir', '<i>x</i><sub>(<i>e</i>,<i>j</i>)</sub> == 1', s_diamond, 777.5, 576, 150, 40)
    add_edge('e_rand_n', '<b>N</b>', s_edge, 'n_dia_rand', 'n_dia_dir', [(810, 542), (852.5, 542)])

    add_node('n_ker_prune', 'Prune weak features:&#xa;<i>x</i>&apos;<sub>(<i>e</i>,<i>j</i>)</sub> &larr; 0', s_box, 745, 646, 104, 42)
    add_node('n_ker_add', 'Add strong features:&#xa;<i>x</i>&apos;<sub>(<i>e</i>,<i>j</i>)</sub> &larr; 1', s_box, 856, 646, 104, 42)

    add_edge('e_dir_y', '<b>Y</b>', s_edge, 'n_dia_dir', 'n_ker_prune', [(777.5, 596), (797, 596)])
    add_edge('e_dir_n', '<b>N</b>', s_edge, 'n_dia_dir', 'n_ker_add', [(927.5, 596), (908, 596)])

    # Acceptance Condition Diamond
    add_node('n_dia_accept', '<i>f</i>(<b><i>X</i></b>&apos;<sub><i>e</i></sub>) &lt; <i>f</i>(<b><i>X</i></b><sub><i>e</i></sub>)', s_diamond, 630, 728, 200, 40)
    add_edge('e_rand_to_acc', '', s_edge, 'n_ker_rand_mut', 'n_dia_accept', [(607.5, 618), (607.5, 712), (730, 712)])
    add_edge('e_prune_to_acc', '', s_edge, 'n_ker_prune', 'n_dia_accept', [(797, 688), (797, 712), (730, 712)])
    add_edge('e_add_to_acc', '', s_edge, 'n_ker_add', 'n_dia_accept', [(908, 688), (908, 712), (730, 712)])

    add_node('n_ker_acc_y', 'Update candidate elite subset:&#xa;<b><i>X</i></b><sup>&lowast;</sup><sub><i>e</i></sub> &larr; <b><i>X</i></b>&apos;<sub><i>e</i></sub>', s_box, 500, 792, 215, 42)
    add_node('n_ker_acc_n', 'Retain current elite subset:&#xa;<b><i>X</i></b><sup>&lowast;</sup><sub><i>e</i></sub> &larr; <b><i>X</i></b><sub><i>e</i></sub>', s_box, 745, 792, 215, 42)

    add_edge('e_acc_y', '<b>Y</b>', s_edge, 'n_dia_accept', 'n_ker_acc_y', [(630, 748), (607.5, 748)])
    add_edge('e_acc_n', '<b>N</b>', s_edge, 'n_dia_accept', 'n_ker_acc_n', [(830, 748), (852.5, 748)])

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')

if __name__ == '__main__':
    xml_content = generate_drawio_xml()
    
    base_dir = r'e:\多目标优化\KDS-EL'
    target_files = [
        os.path.join(base_dir, 'output', 'figures', 'F1_architecture_journal.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F1_kds_el_framework_journal.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F1_kds_el_framework.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F1_kds_el_framework_v4.drawio')
    ]
    
    for tf in target_files:
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f'Successfully updated: {tf}')
