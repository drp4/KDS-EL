"""Generate publication-grade Draw.io XML for Figure 3:
Pure EMSWOA 1:1 Minimalist Layout (Zero redundant text).
Outputs directly to output/figures/F3_mi_initialization_journal.drawio.
"""

import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def generate_figure3_binary_drawio():
    base_dir = r'e:\多目标优化\KDS-EL'
    out_path = os.path.join(base_dir, 'output', 'figures', 'F3_mi_initialization_journal.drawio')

    canvas_w = 1200
    canvas_h = 320

    root_el = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diag_el = ET.SubElement(root_el, 'diagram', id='f3-mi-seeding-recovery-pure', name='Figure 3: Sparse Seeding and Adaptive Recovery Grid')
    model_el = ET.SubElement(diag_el, 'mxGraphModel',
                             dx=str(canvas_w), dy=str(canvas_h),
                             grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1',
                             page='1', pageScale='1', pageWidth=str(canvas_w), pageHeight=str(canvas_h),
                             math='1', shadow='0')
    mx_root = ET.SubElement(model_el, 'root')
    ET.SubElement(mx_root, 'mxCell', id='0')
    ET.SubElement(mx_root, 'mxCell', id='1', parent='0')

    def add_node(node_id, value, style, x, y, w, h):
        cell = ET.SubElement(mx_root, 'mxCell', id=node_id, value=value, style=style, parent='1', vertex='1')
        ET.SubElement(cell, 'mxGeometry', x=str(round(x, 1)), y=str(round(y, 1)),
                      width=str(round(w, 1)), height=str(round(h, 1)), **{'as': 'geometry'})
        return cell

    def add_edge(edge_id, value, style, x1, y1, x2, y2, points=None):
        cell = ET.SubElement(mx_root, 'mxCell', id=edge_id, value=value, style=style, parent='1', edge='1')
        geo = ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
        ET.SubElement(geo, 'mxPoint', x=str(round(x1, 1)), y=str(round(y1, 1)), **{'as': 'sourcePoint'})
        ET.SubElement(geo, 'mxPoint', x=str(round(x2, 1)), y=str(round(y2, 1)), **{'as': 'targetPoint'})
        if points:
            pts_elem = ET.SubElement(geo, 'Array', **{'as': 'points'})
            for px, py in points:
                ET.SubElement(pts_elem, 'mxPoint', x=str(round(px, 1)), y=str(round(py, 1)))
        return cell

    # Typography & Styles
    font = 'fontFamily=Times New Roman;'
    s_label = f'text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;{font}'
    s_box_frame = f'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;{font}'
    s_arrow = f'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;{font}'
    s_dash_line = f'endArrow=none;dashed=1;dashPattern=4 3;strokeColor=#64748B;strokeWidth=0.9;{font}'

    # Cell styles for 0 and 1
    s_cell_1 = f'rounded=0;whiteSpace=wrap;html=1;fillColor=#1E293B;strokeColor=#0F172A;strokeWidth=0.9;fontColor=#FFFFFF;fontStyle=1;fontSize=10;{font}'
    s_cell_0 = f'rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;strokeWidth=0.8;fontColor=#94A3B8;fontSize=9.5;{font}'
    s_cell_rec = f'rounded=0;whiteSpace=wrap;html=1;fillColor=#10B981;strokeColor=#047857;strokeWidth=1;fontColor=#FFFFFF;fontStyle=1;fontSize=10;{font}'

    # 4 Pure Boxes Layout (EMSWOA Fig. 3 pure format)
    box_w = 255
    box_h = 215
    box_y = 45
    gap = 40
    pxs = [30, 30 + box_w + gap, 30 + 2 * (box_w + gap), 30 + 3 * (box_w + gap)]

    headers = [
        '<b>Step 1</b> (<i>t</i> = 0)',
        '<b>Step 2</b> (<i>t</i> = <i>t</i><sub>1</sub>)',
        '<b>Step 3</b> (<i>t</i><sub>stag</sub> &ge; &tau;)',
        '<b>Step 4</b> (<i>t</i> = <i>t</i><sub>stag</sub> + 1)'
    ]

    for idx, (bx, hdr) in enumerate(zip(pxs, headers)):
        # Header text
        add_node(f'hdr_{idx}', hdr, f'{s_label}fontSize=11;fontColor=#000000;fontStyle=1;', bx, box_y - 26, box_w, 20)
        # Box frame
        add_node(f'frame_{idx}', '', s_box_frame, bx, box_y, box_w, box_h)
        # Zero footers below boxes! (Pure EMSWOA minimalism)

    # 3 Transition Arrows
    arrow_y = box_y + box_h / 2
    for i in range(3):
        add_edge(f'arr_{i}', '', s_arrow, pxs[i] + box_w + 5, arrow_y, pxs[i+1] - 5, arrow_y)

    # Grid parameters
    col_feat = ['f<sub>1</sub>', 'f<sub>2</sub>', 'f<sub>3</sub>', 'f<sub>4</sub>', 'f<sub>5</sub>',
                'f<sub>6</sub>', 'f<sub>7</sub>', 'f<sub>8</sub>', 'f<sub>9</sub>', 'f<sub>10</sub>',
                '...', 'f<sub>D</sub>']
    num_f = len(col_feat)
    p_labels = ['<b>x</b><sub>1</sub>', '<b>x</b><sub>2</sub>', '<b>x</b><sub>3</sub>', '<b>x</b><sub>4</sub>']
    
    # 4 rows inside each box
    row_ys = [box_y + 34, box_y + 76, box_y + 128, box_y + 170]
    cell_w = 14
    cell_h = 30

    def render_cells_drawio(panel_idx, matrix, new_rec=None):
        bx = pxs[panel_idx]
        pitch_f = (box_w - 42) / (num_f - 1)
        grid_x0 = bx + 32

        # Header feature labels
        for j in range(num_f):
            fx = grid_x0 + j * pitch_f
            add_node(f'p{panel_idx}_f{j}', col_feat[j], f'{s_label}fontSize=9;fontColor=#475569;',
                     fx - 10, box_y + 8, 20, 18)

        # 4 particle rows
        for r in range(4):
            ry = row_ys[r]
            add_node(f'p{panel_idx}_lbl_{r}', p_labels[r], f'{s_label}fontSize=10;fontColor=#0F172A;align=right;',
                     bx + 6, ry + 6, 20, 18)

            for c in range(num_f):
                cx = grid_x0 + c * pitch_f - cell_w / 2
                cy = ry
                if col_feat[c] == '...':
                    add_node(f'p{panel_idx}_dots_{r}_{c}', '...', f'{s_label}fontSize=9;fontColor=#94A3B8;',
                             cx - 2, cy + 6, 18, 18)
                    continue

                val = matrix[r][c]
                is_recovered = (new_rec is not None and (r, c) in new_rec)

                if is_recovered:
                    add_node(f'p{panel_idx}_cell_{r}_{c}', '1', s_cell_rec, cx, cy, cell_w, cell_h)
                elif val == 1:
                    add_node(f'p{panel_idx}_cell_{r}_{c}', '1', s_cell_1, cx, cy, cell_w, cell_h)
                else:
                    add_node(f'p{panel_idx}_cell_{r}_{c}', '0', s_cell_0, cx, cy, cell_w, cell_h)

    # Matrix data
    mat_1 = [
        [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, None, 0],
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, None, 0],
        [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 0, 0, 1, 1, 0, 0, None, 0]
    ]
    render_cells_drawio(0, mat_1)

    mat_2 = [
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, None, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, None, 0]
    ]
    render_cells_drawio(1, mat_2)

    mat_3 = [
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, None, 0]
    ]
    # Box 3 divider line
    div_y = box_y + 115
    add_edge('div_line_3', '', s_dash_line, pxs[2] + 4, div_y, pxs[2] + box_w - 4, div_y)
    render_cells_drawio(2, mat_3)

    mat_4 = [
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 0, 1, 1, 0, 0, 1, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, None, 1]
    ]
    new_recovered = [(2, 1), (2, 3), (2, 7), (3, 2), (3, 7), (3, 11)]
    add_edge('div_line_4', '', s_dash_line, pxs[3] + 4, div_y, pxs[3] + box_w - 4, div_y)
    render_cells_drawio(3, mat_4, new_rec=new_recovered)

    # Bottom Legend (Compact, centered)
    leg_y = box_y + box_h + 20
    leg_x0 = 400

    # 1: Selected
    add_node('leg_c1', '1', s_cell_1, leg_x0, leg_y, 14, 20)
    add_node('leg_t1', 'Selected feature', f'{s_label}fontSize=10;fontColor=#0F172A;align=left;',
             leg_x0 + 18, leg_y, 100, 20)

    # 0: Unselected
    leg_x1 = leg_x0 + 140
    add_node('leg_c0', '0', s_cell_0, leg_x1, leg_y, 14, 20)
    add_node('leg_t0', 'Unselected feature', f'{s_label}fontSize=10;fontColor=#0F172A;align=left;',
             leg_x1 + 18, leg_y, 110, 20)

    # 1: Recovered
    leg_x2 = leg_x1 + 150
    add_node('leg_cr', '1', s_cell_rec, leg_x2, leg_y, 14, 20)
    add_node('leg_tr', 'Recovered feature (<b><i>m</i></b> + <b><i>&epsilon;</i></b><sub><i>i</i></sub>)',
             f'{s_label}fontSize=10;fontColor=#047857;fontStyle=1;align=left;',
             leg_x2 + 18, leg_y, 180, 20)

    # Output to file
    xml_str = ET.tostring(root_el, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f"SUCCESS: Generated Pure EMSWOA Draw.io XML at: {out_path}")

if __name__ == '__main__':
    generate_figure3_binary_drawio()
