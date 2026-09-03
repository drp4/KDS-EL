import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def generate_figure4_lesion_drawio_xml():
    mxfile = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diagram = ET.SubElement(mxfile, 'diagram', id='f4-random-mutation-lesion', name='Figure 4: Physical Lesions of Conventional Random Mutation')
    graph_model = ET.SubElement(diagram, 'mxGraphModel', 
                                dx='1000', dy='1000', grid='1', gridSize='10', 
                                guides='1', tooltips='1', connect='1', arrows='1', 
                                fold='1', page='1', pageScale='1', pageWidth='1060', pageHeight='640', 
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
    s_box_shaded = 'rounded=0;whiteSpace=wrap;html=1;fillColor=#F2F2F2;strokeColor=#000000;strokeWidth=1;fontSize=10;fontFamily=Times New Roman;'
    s_container = 'rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor=none;strokeColor=#000000;strokeWidth=1.2;verticalAlign=top;spacingTop=8;fontSize=11;fontStyle=1;fontFamily=Times New Roman;pointerEvents=0;'

    # 1. Top Section: High-Dimensional Context (x in [30, 1030], width = 1000, y = 30)
    add_node('n_ctx', '<b>High-Dimensional Feature Selection Context (<i>D</i> &gg; 10<sup>3</sup>, e.g., <i>D</i> = 12,600+ features)</b>&#xa;Current Elite Candidate Solution: <b><i>x</i></b><sub><i>e</i></sub> = [<i>x</i><sub><i>e</i>,1</sub>, <i>x</i><sub><i>e</i>,2</sub>, ..., <i>x</i><sub><i>e</i>,<i>D</i></sub>] &#8712; {0, 1}<sup><i>D</i></sup> with fitness <i>f</i>(<b><i>x</i></b><sub><i>e</i></sub>) = 0.0820', s_box_bold, 30, 30, 1000, 48)

    # 2. Main Concrete Numerical Feature Comparison Grid (y in [95, 335])
    # Table headers
    add_node('th_dim', '<b>Feature Index</b>', s_box_shaded, 30, 95, 160, 32)
    add_node('th_f1', '<b>Feature <i>f</i><sub>1</sub></b>&#xa;(Core Biomarker)', s_box, 190, 95, 150, 32)
    add_node('th_f2', '<b>Feature <i>f</i><sub>2</sub></b>&#xa;(Uncorrelated Noise)', s_box, 340, 95, 150, 32)
    add_node('th_f3', '<b>Feature <i>f</i><sub>3</sub></b>&#xa;(Redundant Gene)', s_box, 490, 95, 150, 32)
    add_node('th_f4', '<b>Feature <i>f</i><sub>4</sub></b>&#xa;(Synergistic Pair)', s_box, 640, 95, 150, 32)
    add_node('th_dots', '<b>...</b>', s_box_shaded, 790, 95, 90, 32)
    add_node('th_fd', '<b>Feature <i>f</i><sub><i>D</i></sub></b>&#xa;(Background)', s_box, 880, 95, 150, 32)

    # Row 1: True Feature Contribution
    add_node('r1_lbl', '<b>Underlying True Contribution</b>', s_box_shaded, 30, 127, 160, 32)
    add_node('r1_f1', '<b>Strong Positive</b>&#xa;(High Discriminative)', s_box, 190, 127, 150, 32)
    add_node('r1_f2', '<b>Strong Negative</b>&#xa;(Pure Noise / Overfitting)', s_box, 340, 127, 150, 32)
    add_node('r1_f3', '<b>Negative</b>&#xa;(Redundant Copy of <i>f</i><sub>1</sub>)', s_box, 490, 127, 150, 32)
    add_node('r1_f4', '<b>Strong Positive</b>&#xa;(Synergistic with <i>f</i><sub>1</sub>)', s_box, 640, 127, 150, 32)
    add_node('r1_dots', '...', s_box_shaded, 790, 127, 90, 32)
    add_node('r1_fd', '<b>Neutral / Zero</b>&#xa;(Zero Correlation)', s_box, 880, 127, 150, 32)

    # Row 2: Current Elite Selection State x_e
    add_node('r2_lbl', '<b>Current Elite Subset <i>x</i><sub><i>e</i></sub></b>', s_box_shaded, 30, 159, 160, 32)
    add_node('r2_f1', '<b>1 (Selected)</b>', s_box, 190, 159, 150, 32)
    add_node('r2_f2', '<b>0 (Excluded)</b>', s_box, 340, 159, 150, 32)
    add_node('r2_f3', '<b>0 (Excluded)</b>', s_box, 490, 159, 150, 32)
    add_node('r2_f4', '<b>1 (Selected)</b>', s_box, 640, 159, 150, 32)
    add_node('r2_dots', '...', s_box_shaded, 790, 159, 90, 32)
    add_node('r2_fd', '<b>0 (Excluded)</b>', s_box, 880, 159, 150, 32)

    # Row 3: Traditional Random Bit Mutation (1/D stochastic flip)
    add_node('r3_lbl', '<b>Conventional Random Bit Mutation</b>&#xa;(Uniform <i>p</i><sub>mut</sub> = 1/<i>D</i> flip)', s_box_shaded, 30, 191, 160, 48)
    add_node('r3_f1', '<b>Blind Flip: 1 &#8594; 0</b>&#xa;(Mistakenly Pruned)', s_box, 190, 191, 150, 48)
    add_node('r3_f2', '<b>Blind Flip: 0 &#8594; 1</b>&#xa;(Mistakenly Activated)', s_box, 340, 191, 150, 48)
    add_node('r3_f3', '<b>0 &#8594; 0</b> (No flip)', s_box, 490, 191, 150, 48)
    add_node('r3_f4', '<b>1 &#8594; 1</b> (No flip)', s_box, 640, 191, 150, 48)
    add_node('r3_dots', '...', s_box_shaded, 790, 191, 90, 48)
    add_node('r3_fd', '<b>0 &#8594; 0</b> (No flip)', s_box, 880, 191, 150, 48)

    # Row 4: Physical Consequences (The Lesion / Why)
    add_node('r4_lbl', '<b>Physical Search Lesion (The Why)</b>', s_box_shaded, 30, 239, 160, 68)
    add_node('r4_f1', '<b>[Lesion 1] Fatal Synergistic Loss:</b>&#xa;Verified critical biomarker is discarded;&#xa;Accuracy collapses drastically&#xa;(&#916;Acc = -14.2%)', s_box, 190, 239, 150, 68)
    add_node('r4_f2', '<b>[Lesion 2] Noise Infiltration:</b>&#xa;Uncorrelated noisy gene is activated;&#xa;Bloats feature count &amp; causes&#xa;severe wrapper overfitting', s_box, 340, 239, 150, 68)
    add_node('r4_f3', 'Redundant dimension remains unpruned', s_box, 490, 239, 150, 68)
    add_node('r4_f4', 'Synergy broken due to loss of <i>f</i><sub>1</sub>', s_box, 640, 239, 150, 68)
    add_node('r4_dots', '...', s_box_shaded, 790, 239, 90, 68)
    add_node('r4_fd', 'No guidance received', s_box, 880, 239, 150, 68)

    # Row 5: Degraded Output Vector
    add_node('r5_lbl', '<b>Resulting Degraded Candidate <i>x</i>&apos;</b>', s_box_shaded, 30, 307, 160, 36)
    add_node('r5_res', '<b><i>x</i>&apos; = [0, 1, 0, 1, ..., 0] &#8712; {0, 1}<sup><i>D</i></sup></b>&#xa;Degraded Fitness: <i>f</i>(<b><i>x</i></b>&apos;) = 0.2250 &gg; <i>f</i>(<b><i>x</i></b><sub><i>e</i></sub>) = 0.0820 (Severe Fitness Deterioration &amp; Wasted Classifier Budget)', s_box_bold, 190, 307, 840, 36)

    # 3. Bottom Theoretical Summary Container (y in [360, 600])
    add_node('c_summary', 'Theoretical Bottlenecks of Blind Perturbations in Ultra-High-Dimensional Search Spaces (<i>D</i> &gg; 10<sup>3</sup>)', s_container, 30, 360, 1000, 240)

    add_node('n_box_s1', '<b>Bottleneck 1: Infinitesimal Probability of Beneficial Modification</b>&#xa;In spaces with <i>D</i> &#8805; 10<sup>4</sup> dimensions, the combinatorial neighborhood is 2<sup><i>D</i></sup>. An undirected random bit flip has an infinitesimal hit probability O(1/<i>D</i>) &#8776; 10<sup>-4</sup> of modifying the few decisive biomarkers, while having an overwhelming probability (1 - <i>d</i><sup>*</sup>/<i>D</i>) &#8776; 99.8% of perturbing irrelevant background noise.', s_box, 50, 395, 460, 95)

    add_node('n_box_s2', '<b>Bottleneck 2: Memoryless Search Amnesia</b>&#xa;Standard meta-heuristics immediately discard the fitness evaluation feedback of trial solutions after particle updates. The optimizer fails to accumulate historical knowledge regarding which features systematically improved classification accuracy versus which features induced error spikes.', s_box, 550, 395, 460, 95)

    add_node('n_box_s3', '<b>The KDS-EL Theoretical Solution (Section 3.3)</b>&#xa;KDS-EL resolves these dilemmas through a closed loop: cumulative trial feedback is preserved in the continuous importance matrix <b><i>W</i></b> &#8712; &#8477;<sup><i>D</i></sup> with exponential decay &gamma; = 0.99. The KER operator computes directional scores &sigma;<sub><i>j</i></sub> = (1 - 2<i>x</i><sub><i>e</i>,<i>j</i></sub>) &middot; <i>W</i><sub><i>j</i></sub> to deterministically prune weak features (1 &#8594; 0) and add strong features (0 &#8594; 1) under bounded computation.', s_box_bold, 50, 505, 960, 80)

    xml_str = ET.tostring(mxfile, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')

if __name__ == '__main__':
    xml_content = generate_figure4_lesion_drawio_xml()
    base_dir = r'e:\多目标优化\KDS-EL'
    target_files = [
        os.path.join(base_dir, 'output', 'figures', 'F4_random_mutation_lesion.drawio'),
        os.path.join(base_dir, 'output', 'figures', 'F4_lesion_why_journal.drawio')
    ]
    
    for tf in target_files:
        with open(tf, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f'Successfully generated Figure 4 Lesion Draw.io: {tf}')
