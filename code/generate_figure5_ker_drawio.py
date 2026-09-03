import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def generate_figure5_ker_drawio_xml():
    mxfile = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f5-ker-refinement-dataflow', name='Figure 5: KER Directional Refinement Data Flow')
    graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                dx='1000', dy='1000', grid='1', gridSize='10', 
                                guides='1', tooltips='1', connect='1', arrows='1', 
                                fold='1', page='1', pageScale='1', pageWidth='1060', pageHeight='700', 
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

    # EMSWOA Academic Monochrome Styles
    s_box = 'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_box_bold = 'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.2;fontSize=10;fontStyle=1;fontFamily=Times New Roman;'
    s_diamond = 'rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_container = 'rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor=none;strokeColor=#000000;strokeWidth=1.2;verticalAlign=top;spacingTop=8;fontSize=11;fontStyle=1;fontFamily=Times New Roman;pointerEvents=0;'
    s_edge = 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1;endArrow=classic;endFill=1;fontSize=10;fontFamily=Times New Roman;'

    # 1. Top Section: Cumulative Importance Learning Data Flow (x in [30, 1030], width = 1000, y = 20)
    add_node('c_mem_accum', 'Stage 1: Closed-Loop Feature-Importance Learning &amp; Accumulation (W Matrix)', s_container, 30, 20, 1000, 140)

    add_node('n_step_eval', '<b>Swarm Trial Evaluation</b>&#xa;Particle <b><i>x</i></b><sub><i>i</i></sub><sup>(<i>t</i>)</sup> improves over personal best <b><i>p</i></b><sub>best,<i>i</i></sub>:&#xa;&delta;<sub><i>i</i></sub><sup>(<i>t</i>)</sup> = <i>f</i>(<b><i>p</i></b><sub>best,<i>i</i></sub>, <b><i>w</i></b>) - <i>f</i>(<b><i>x</i></b><sub><i>i</i></sub><sup>(<i>t</i>)</sup>, <b><i>w</i></b>) &gt; 0', s_box, 50, 55, 290, 85)

    add_node('n_diff_feat', '<b>Differential Feature Mask Extraction</b>&#xa;Harvest features whose selection status changed:&#xa;<i>C</i><sub><i>i</i></sub><sup>(<i>t</i>)</sup> = { <i>j</i> &#8712; {1, ..., <i>D</i>} | <i>x</i><sub><i>i</i>,<i>j</i></sub><sup>(<i>t</i>)</sup> &#8800; <i>p</i><sub>best,<i>i</i>,<i>j</i></sub> }', s_box, 380, 55, 290, 85)
    add_edge('e_eval_diff', '', s_edge, 'n_step_eval', 'n_diff_feat')

    add_node('n_mem_update', '<b>Importance Update with Decay &gamma; = 0.99</b>&#xa;<i>W</i><sub><i>j</i></sub> &larr; &gamma;<i>W</i><sub><i>j</i></sub> + &delta;<sub><i>i</i></sub><sup>(<i>t</i>)</sup> &middot; (2<i>x</i><sub><i>i</i>,<i>j</i></sub><sup>(<i>t</i>)</sup> - 1),  &forall;<i>j</i> &#8712; <i>C</i><sub><i>i</i></sub><sup>(<i>t</i>)</sup>&#xa;<b><i>W</i></b> = [<i>W</i><sub>1</sub>, ..., <i>W</i><sub><i>D</i></sub>]<sup><i>T</i></sup> &#8712; &#8477;<sup><i>D</i></sup>', s_box_bold, 710, 55, 300, 85)
    add_edge('e_diff_mem', '', s_edge, 'n_diff_feat', 'n_mem_update')

    # 2. Middle Section: Knowledge-Guided Elite Refinement Operator (y in [180, 530])
    add_node('c_ker_exec', 'Stage 2: Knowledge-Guided Elite Refinement Operator (KER State Machine)', s_container, 30, 180, 1000, 350)

    # Input node to KER
    add_node('n_ker_input', '<b>Inputs to KER Operator:</b>  Elite candidate <b><i>x</i></b><sub><i>e</i></sub> &#8712; {0, 1}<sup><i>D</i></sup> (Top <i>k</i><sub><i>e</i></sub> pool), Importance vector <b><i>W</i></b> &#8712; &#8477;<sup><i>D</i></sup>, Dynamic weights <b><i>w</i></b>(<i>t</i>)', s_box, 50, 215, 960, 36)

    # Dispatch Diamond: r < p_rand
    add_node('n_dia_rand', '<i>r</i> &lt; <i>p</i><sub>rand</sub>', s_diamond, 460, 275, 140, 42)
    add_edge('e_in_dia', '', s_edge, 'n_ker_input', 'n_dia_rand')

    # Branch 1 (Left): Ergodic Random Exploration (probability p_rand)
    add_node('n_br1_title', '<b>Branch 1: Ergodic Random Exploration</b>&#xa;(Probability <i>p</i><sub>rand</sub>)', s_box, 50, 340, 280, 40)
    add_node('n_br1_op', 'Sample <i>k</i><sub>flip</sub> random indices <i>S</i><sub>rand</sub> &#8834; {1, ..., <i>D</i>}&#xa;Invert bits: <i>x</i>&apos;<sub><i>e</i>,<i>j</i></sub> &larr; 1 - <i>x</i><sub><i>e</i>,<i>j</i></sub>, &forall;<i>j</i> &#8712; <i>S</i><sub>rand</sub>&#xa;(Preserves search ergodicity &amp; diversity)', s_box, 50, 405, 280, 60)
    add_edge('e_dia_br1', '<b>Y</b> (Explore)', s_edge, 'n_dia_rand', 'n_br1_title', [(460, 296), (190, 296)])
    add_edge('e_b1_op', '', s_edge, 'n_br1_title', 'n_br1_op')

    # Branch 2 (Right): Knowledge-Guided Directional Refinement (probability 1 - p_rand)
    add_node('n_br2_title', '<b>Branch 2: Knowledge-Guided Directional Refinement</b>&#xa;(Probability 1 - <i>p</i><sub>rand</sub>)', s_box_bold, 380, 340, 630, 40)
    add_edge('e_dia_br2', '<b>N</b> (Exploit Knowledge)', s_edge, 'n_dia_rand', 'n_br2_title', [(600, 296), (695, 296)])

    # Inside Branch 2: Flip score calculation + directional dispatch
    add_node('n_score_calc', 'Compute Directional Flip Score: <b>&sigma;<sub><i>j</i></sub> = (1 - 2<i>x</i><sub><i>e</i>,<i>j</i></sub>) &middot; <i>W</i><sub><i>j</i></sub></b>,  &forall;<i>j</i> = 1, ..., <i>D</i>&#xa;Identify subset <i>S</i><sub>know</sub> of size <i>k</i><sub>flip</sub> with highest &sigma;<sub><i>j</i></sub> scores', s_box, 380, 395, 630, 42)
    add_edge('e_b2_calc', '', s_edge, 'n_br2_title', 'n_score_calc')

    # Sub-branches of Directional Flip: Prune Weak vs Add Strong
    add_node('n_prune_weak', '<b>Directional Prune (Weak Features):</b>&#xa;If <i>x</i><sub><i>e</i>,<i>j</i></sub> = 1 and <i>W</i><sub><i>j</i></sub> &lt; 0 (&sigma;<sub><i>j</i></sub> &gt; 0)&#xa;Action: <b><i>x</i>&apos;<sub><i>e</i>,<i>j</i></sub> &larr; 0</b> (Prune noisy dimension)', s_box, 380, 450, 305, 58)

    add_node('n_add_strong', '<b>Directional Add (Strong Biomarkers):</b>&#xa;If <i>x</i><sub><i>e</i>,<i>j</i></sub> = 0 and <i>W</i><sub><i>j</i></sub> &gt; 0 (&sigma;<sub><i>j</i></sub> &gt; 0)&#xa;Action: <b><i>x</i>&apos;<sub><i>e</i>,<i>j</i></sub> &larr; 1</b> (Activate synergistic biomarker)', s_box, 705, 450, 305, 58)

    add_edge('e_calc_prune', '', s_edge, 'n_score_calc', 'n_prune_weak', [(695, 437), (532, 437)])
    add_edge('e_calc_add', '', s_edge, 'n_score_calc', 'n_add_strong', [(695, 437), (857, 437)])

    # 3. Bottom Section: Strict 1-to-1 Greedy Replacement (y in [550, 670])
    add_node('c_greedy', 'Stage 3: Strict 1-to-1 Greedy Replacement', s_container, 30, 550, 1000, 120)

    add_node('n_dia_greedy', '<i>f</i>(<b><i>x</i></b>&apos;<sub><i>e</i></sub>, <b><i>w</i></b>) &lt; <i>f</i>(<b><i>x</i></b><sub><i>e</i></sub>, <b><i>w</i></b>)', s_diamond, 460, 580, 140, 44)

    # Connect Branch 1 and Branch 2 to Greedy Diamond
    add_edge('e_b1_greedy', '', s_edge, 'n_br1_op', 'n_dia_greedy', [(190, 485), (190, 565), (530, 565)])
    add_edge('e_prune_greedy', '', s_edge, 'n_prune_weak', 'n_dia_greedy', [(532, 520), (532, 565), (530, 565)])
    add_edge('e_add_greedy', '', s_edge, 'n_add_strong', 'n_dia_greedy', [(857, 520), (857, 565), (530, 565)])

    # Accept vs Reject
    add_node('n_accept', '<b>Accept Superior Mutant:</b>&#xa;<b><i>x</i></b><sub><i>e</i></sub><sup>*</sup> &larr; <b><i>x</i></b>&apos;<sub><i>e</i></sub> (Update elite candidate)', s_box_bold, 180, 605, 240, 50)
    add_node('n_reject', '<b>Preserve Existing Elite:</b>&#xa;<b><i>x</i></b><sub><i>e</i></sub><sup>*</sup> &larr; <b><i>x</i></b><sub><i>e</i></sub> (Safeguard convergence)', s_box, 640, 605, 240, 50)

    add_edge('e_g_accept', '<b>Y</b> (Improved)', s_edge, 'n_dia_greedy', 'n_accept', [(460, 602), (420, 602), (420, 630)])
    add_edge('e_g_reject', '<b>N</b> (Worse/Equal)', s_edge, 'n_dia_greedy', 'n_reject', [(600, 602), (640, 602), (640, 630)])

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')

if __name__ == '__main__':
    xml_content = generate_figure5_ker_drawio_xml()
    base_dir = r'e:\多目标优化\KDS-EL'
    target_files = [
        os.path.join(base_dir, 'output', 'figures', 'F5_ker_refinement_dataflow.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F5_ker_strategy_journal.drawio')
    ]
    
    for tf in target_files:
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f'Successfully generated Figure 5 KER Draw.io: {tf}')
