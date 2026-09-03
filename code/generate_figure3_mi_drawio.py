"""Generate publication-grade Draw.io XML for Figure 3:
MI Prior Seeding and Adaptive Stagnation Recovery (Bead Lattice Paradigm).
Outputs directly to output/figures/F3_mi_initialization_journal.drawio.
"""

import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def generate_figure3_drawio():
    base_dir = r'e:\多目标优化\KDS-EL'
    out_path = os.path.join(base_dir, 'output', 'figures', 'F3_mi_initialization_journal.drawio')

    canvas_w = 1200
    canvas_h = 700

    root_el = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diag_el = ET.SubElement(root_el, 'diagram', id='f3-mi-seeding-recovery', name='Figure 3: MI Prior Seeding and Adaptive Stagnation Recovery')
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
    s_panel = f'rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;strokeWidth=1.2;{font}'
    s_elite_box = f'rounded=1;whiteSpace=wrap;html=1;fillColor=#F0F7FF;strokeColor=#2563EB;strokeWidth=1.3;{font}'
    s_stag_box = f'rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=1.2;{font}'
    s_arrow = f'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0F172A;strokeWidth=2;endArrow=classic;endFill=1;{font}'
    
    s_bead_inactive = f'ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#94A3B8;strokeWidth=1;{font}'
    s_bead_active = f'ellipse;whiteSpace=wrap;html=1;fillColor=#F97316;strokeColor=#C2410C;strokeWidth=1.2;{font}'
    s_bead_rec = f'ellipse;whiteSpace=wrap;html=1;fillColor=#10B981;strokeColor=#047857;strokeWidth=1.3;{font}'

    # -------------------------------------------------------------------------
    # TOP SECTION: MI Prior (Feature Relevance Profile)
    # -------------------------------------------------------------------------
    add_node('top_title', '<b>MI Prior</b> (feature relevance: <i>m</i> &in; [0, 1]<sup><i>D</i></sup>)',
             f'{s_label}fontSize=12;align=left;fontStyle=1;fontColor=#0F172A;', 30, 15, 300, 25)

    features_top = ['f<sub>1</sub>', 'f<sub>2</sub>', 'f<sub>3</sub>', 'f<sub>4</sub>', 'f<sub>5</sub>',
                    'f<sub>6</sub>', 'f<sub>7</sub>', 'f<sub>8</sub>', 'f<sub>9</sub>', 'f<sub>10</sub>',
                    '...', 'f<sub>D-1</sub>', 'f<sub>D</sub>']
    mi_scores = [0.18, 0.12, 0.88, 0.20, 0.82, 0.16, 0.19, 0.92, 0.22, 0.15, None, 0.15, 0.13]
    
    top_x0 = 310
    pitch_top = 46
    axis_y = 80
    max_h = 50

    # Baseline axis
    add_edge('axis_line', '', f'endArrow=none;strokeColor=#334155;strokeWidth=1.5;{font}',
             top_x0 - 25, axis_y, top_x0 + (len(features_top)-1) * pitch_top + 25, axis_y)

    # Threshold dashed line
    th_y = axis_y - 0.55 * max_h
    add_edge('th_line', '', f'endArrow=none;dashed=1;strokeColor=#EA580C;strokeWidth=1.1;{font}',
             top_x0 - 20, th_y, top_x0 + (len(features_top)-1) * pitch_top + 20, th_y)
    add_node('th_text', '&theta; = 0.60 (Cut-off)',
             f'{s_label}fontSize=9;fontColor=#EA580C;fontStyle=1;align=left;',
             top_x0 + (len(features_top)-1) * pitch_top + 25, th_y - 10, 90, 20)

    for idx, (lbl, score) in enumerate(zip(features_top, mi_scores)):
        bx = top_x0 + idx * pitch_top
        add_node(f'flbl_{idx}', lbl, f'{s_label}fontSize=9.5;fontColor=#0F172A;', bx - 15, axis_y + 4, 30, 18)
        if score is not None:
            bh = score * max_h
            is_high = score >= 0.55
            b_color = '#EA580C' if is_high else '#CBD5E1'
            b_stroke = '#C2410C' if is_high else '#94A3B8'
            s_bar = f'rounded=0;whiteSpace=wrap;html=1;fillColor={b_color};strokeColor={b_stroke};strokeWidth=1;{font}'
            add_node(f'bar_{idx}', '', s_bar, bx - 8, axis_y - bh, 16, bh)
        else:
            add_node(f'ellipsis_top', '...', f'{s_label}fontSize=12;fontColor=#64748B;', bx - 10, axis_y - 25, 20, 20)

    # -------------------------------------------------------------------------
    # MAIN FOUR PANELS
    # -------------------------------------------------------------------------
    panel_w = 255
    panel_h = 430
    panel_y = 150
    gap = 42
    pxs = [30, 30 + panel_w + gap, 30 + 2 * (panel_w + gap), 30 + 3 * (panel_w + gap)]

    stages_meta = [
        {'step': '<i>i</i> = 0', 'title': 'MI-guided Initialization', 'sub': 'Prior-injected sparse population'},
        {'step': '<i>i</i> = 1', 'title': 'Evolutionary Search', 'sub': 'Population evolves and refines'},
        {'step': '<i>i</i> = 2', 'title': 'Stagnation Detected (<i>t</i><sub>stag</sub> &ge; &tau;)', 'sub': 'No improvement for &tau; consecutive generations'},
        {'step': '<i>i</i> = 3', 'title': 'Selective Recovery Activated', 'sub': 'Stagnant non-elites are regenerated with new masks'}
    ]

    for p_idx, px in enumerate(pxs):
        meta = stages_meta[p_idx]
        # Step header
        add_node(f'step_{p_idx}', meta['step'], f'{s_label}fontSize=12;fontStyle=1;fontColor=#0F172A;',
                 px, panel_y - 38, panel_w, 20)
        # Stage title
        t_col = '#1E40AF' if p_idx == 2 else '#0F172A'
        add_node(f'title_{p_idx}', f'<b>{meta["title"]}</b>', f'{s_label}fontSize=10;fontColor={t_col};',
                 px, panel_y - 18, panel_w, 20)
        # Panel card
        add_node(f'panel_card_{p_idx}', '', s_panel, px, panel_y, panel_w, panel_h)
        # Subtitle description
        add_node(f'sub_{p_idx}', meta['sub'], f'{s_label}fontSize=9;fontColor=#334155;whiteSpace=wrap;',
                 px, panel_y + panel_h + 8, panel_w, 25)

    # Inter-panel transition arrows
    arrow_y = panel_y + panel_h / 2
    for i in range(3):
        add_edge(f'arrow_{i}', '', s_arrow, pxs[i] + panel_w + 6, arrow_y, pxs[i+1] - 6, arrow_y)

    # -------------------------------------------------------------------------
    # BEADS AND FEATURES
    # -------------------------------------------------------------------------
    col_feat = ['f<sub>1</sub>', 'f<sub>2</sub>', 'f<sub>3</sub>', 'f<sub>4</sub>', 'f<sub>5</sub>',
                'f<sub>6</sub>', 'f<sub>7</sub>', 'f<sub>8</sub>', 'f<sub>9</sub>', 'f<sub>10</sub>',
                '...', 'f<sub>D</sub>']
    num_f = len(col_feat)
    bead_d = 12
    p_labels = ['<i>x</i><sub>1</sub>', '<i>x</i><sub>2</sub>', '<i>x</i><sub>3</sub>', '<i>x</i><sub>4</sub>']
    row_rel_ys = [75, 140, 245, 310]

    def render_bead_grid(panel_idx, matrix, new_activated=None):
        px = pxs[panel_idx]
        pitch_f = (panel_w - 50) / (num_f - 1)
        grid_x0 = px + 35

        # Feature headers
        for j in range(num_f):
            fx = grid_x0 + j * pitch_f
            add_node(f'p{panel_idx}_f{j}', col_feat[j], f'{s_label}fontSize=8.5;fontColor=#64748B;',
                     fx - 12, panel_y + 18, 24, 16)

        # Rows
        for r in range(4):
            ry = panel_y + row_rel_ys[r]
            add_node(f'p{panel_idx}_lbl_{r}', p_labels[r], f'{s_label}fontSize=9.5;fontColor=#0F172A;align=right;',
                     px + 8, ry - 3, 22, 18)

            for c in range(num_f):
                bx = grid_x0 + c * pitch_f - bead_d / 2
                by = ry
                if col_feat[c] == '...':
                    add_node(f'p{panel_idx}_dot_{r}_{c}', '...', f'{s_label}fontSize=9;fontColor=#64748B;',
                             bx - 2, by - 4, 16, 16)
                    continue

                val = matrix[r][c]
                is_new = (new_activated is not None and (r, c) in new_activated)
                if is_new:
                    st = s_bead_rec
                elif val == 1:
                    st = s_bead_active
                else:
                    st = s_bead_inactive
                add_node(f'p{panel_idx}_bead_{r}_{c}', '', st, bx, by, bead_d, bead_d)

    # Matrix 1
    mat_1 = [
        [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, None, 0],
        [0, 1, 1, 0, 1, 0, 0, 1, 0, 0, None, 0],
        [0, 1, 1, 0, 1, 0, 0, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 0, 0, 1, 1, 0, 0, None, 0]
    ]
    render_bead_grid(0, mat_1)

    # Matrix 2
    mat_2 = [
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, None, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, None, 0]
    ]
    render_bead_grid(1, mat_2)

    # Matrix 3 (Partition)
    mat_3 = [
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, None, 0]
    ]
    # Elite enclosure
    add_node('box_elite_3', '', s_elite_box, pxs[2] + 6, panel_y + 45, panel_w - 12, 130)
    # Stagnant enclosure
    add_node('box_stag_3', '', s_stag_box, pxs[2] + 6, panel_y + 215, panel_w - 12, 130)
    render_bead_grid(2, mat_3)

    # Side labels
    add_node('lbl_elite', '<b>Elite</b><br>(retained)', f'{s_label}fontSize=8.5;fontColor=#1E40AF;align=center;',
             pxs[2] + panel_w + 5, panel_y + 85, 30, 30)
    add_node('lbl_stag', '<b>Stagnant</b><br>(non-elite)', f'{s_label}fontSize=8.5;fontColor=#64748B;align=center;',
             pxs[2] + panel_w + 5, panel_y + 255, 30, 30)

    # Matrix 4 (Recovery)
    mat_4 = [
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 0, None, 0],
        [0, 1, 0, 1, 1, 0, 0, 1, 0, 0, None, 0],
        [0, 0, 1, 0, 1, 0, 1, 1, 0, 0, None, 1]
    ]
    new_recovered = [(2, 1), (2, 3), (2, 7), (3, 2), (3, 7), (3, 11)]
    add_node('box_elite_4', '', s_elite_box, pxs[3] + 6, panel_y + 45, panel_w - 12, 130)
    add_node('box_stag_4', '', s_stag_box, pxs[3] + 6, panel_y + 215, panel_w - 12, 130)
    render_bead_grid(3, mat_4, new_activated=new_recovered)

    # Recovery curved arrows
    s_curved_rec = f'curved=1;endArrow=classic;strokeColor=#10B981;strokeWidth=1.8;fillColor=none;{font}'
    add_edge('rec_arrow_1', '', s_curved_rec,
             pxs[3] + panel_w - 8, panel_y + row_rel_ys[2] - 8,
             pxs[3] + panel_w - 8, panel_y + row_rel_ys[2] + 18,
             points=[(pxs[3] + panel_w + 6, panel_y + row_rel_ys[2] + 5)])
    add_edge('rec_arrow_2', '', s_curved_rec,
             pxs[3] + panel_w - 8, panel_y + row_rel_ys[3] - 8,
             pxs[3] + panel_w - 8, panel_y + row_rel_ys[3] + 18,
             points=[(pxs[3] + panel_w + 6, panel_y + row_rel_ys[3] + 5)])
    add_node('lbl_rec', '<b>Recovered</b><br>(regenerated)', f'{s_label}fontSize=8.5;fontColor=#047857;align=left;',
             pxs[3] + panel_w + 10, panel_y + 255, 60, 30)

    # -------------------------------------------------------------------------
    # BOTTOM LEGEND
    # -------------------------------------------------------------------------
    leg_y = panel_y + panel_h + 46
    leg_x0 = 360

    # Item 1: Selected
    add_node('leg_c1', '', s_bead_active, leg_x0, leg_y, 14, 14)
    add_node('leg_t1', '1 (selected)', f'{s_label}fontSize=9.5;fontColor=#0F172A;align=left;',
             leg_x0 + 18, leg_y - 2, 80, 18)

    # Item 2: Unselected
    leg_x1 = leg_x0 + 150
    add_node('leg_c2', '', s_bead_inactive, leg_x1, leg_y, 14, 14)
    add_node('leg_t2', '0 (unselected)', f'{s_label}fontSize=9.5;fontColor=#0F172A;align=left;',
             leg_x1 + 18, leg_y - 2, 90, 18)

    # Item 3: Recovered
    leg_x2 = leg_x1 + 160
    add_node('leg_c3', '', s_bead_rec, leg_x2, leg_y, 14, 14)
    add_node('leg_t3', 'Recovered feature (<b><i>m</i></b> + <b><i>&epsilon;</i></b><sub><i>i</i></sub>)',
             f'{s_label}fontSize=9.5;fontColor=#047857;fontStyle=1;align=left;',
             leg_x2 + 18, leg_y - 2, 170, 18)

    # Save to file with pretty formatting
    xml_str = ET.tostring(root_el, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f"SUCCESS: Generated Draw.io XML at: {out_path}")

if __name__ == '__main__':
    generate_figure3_drawio()
