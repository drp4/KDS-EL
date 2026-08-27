"""Exhaustive 1:1 mathematical mirror of Matplotlib scripts to Draw.io XML:
- Figure 1: code/generate_figure1_pipeline.py
- Figure 2: code/generate_figure2_mi.py
- Figure 3: code/generate_figure3_ker.py

Every single coordinate, particle angle, bar height, scatter point, formula, font size,
and color code is mathematically translated directly from the Matplotlib code.
"""

import os
import numpy as np
import xml.etree.ElementTree as ET

def create_drawio_xml(filename, diagram_id, diagram_name, width, height, elements, connections):
    root_el = ET.Element('mxfile', host='Electron', agent='Draw.io', version='24.0.0')
    diag_el = ET.SubElement(root_el, 'diagram', id=diagram_id, name=diagram_name)
    model_el = ET.SubElement(diag_el, 'mxGraphModel',
                             dx=str(int(width)), dy=str(int(height)),
                             grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1',
                             page='1', pageScale='1', pageWidth=str(int(width)), pageHeight=str(int(height)),
                             math='1', shadow='0')
    mx_root = ET.SubElement(model_el, 'root')
    ET.SubElement(mx_root, 'mxCell', id='0')
    ET.SubElement(mx_root, 'mxCell', id='1', parent='0')

    for el in elements:
        cell = ET.SubElement(mx_root, 'mxCell',
                             id=str(el['id']),
                             value=str(el.get('value', '')),
                             style=str(el.get('style', '')),
                             parent=str(el.get('parent', '1')),
                             vertex='1')
        geom_kwargs = {
            'x': str(round(el['x'], 1)),
            'y': str(round(el['y'], 1)),
            'width': str(round(el['w'], 1)),
            'height': str(round(el['h'], 1)),
            'as': 'geometry'
        }
        ET.SubElement(cell, 'mxGeometry', **geom_kwargs)

    for conn in connections:
        edge = ET.SubElement(mx_root, 'mxCell',
                             id=str(conn['id']),
                             value=str(conn.get('value', '')),
                             style=str(conn.get('style', '')),
                             parent=str(conn.get('parent', '1')),
                             edge='1')
        if 'source' in conn:
            edge.set('source', str(conn['source']))
        if 'target' in conn:
            edge.set('target', str(conn['target']))
        
        geom = ET.SubElement(edge, 'mxGeometry', relative='1', **{'as': 'geometry'})
        if 'points' in conn:
            pts_el = ET.SubElement(geom, 'Array', **{'as': 'points'})
            for pt in conn['points']:
                ET.SubElement(pts_el, 'mxPoint', x=str(round(pt[0], 1)), y=str(round(pt[1], 1)))
        if 'sourcePoint' in conn:
            ET.SubElement(geom, 'mxPoint', x=str(round(conn['sourcePoint'][0], 1)), y=str(round(conn['sourcePoint'][1], 1)), **{'as': 'sourcePoint'})
        if 'targetPoint' in conn:
            ET.SubElement(geom, 'mxPoint', x=str(round(conn['targetPoint'][0], 1)), y=str(round(conn['targetPoint'][1], 1)), **{'as': 'targetPoint'})

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    tree = ET.ElementTree(root_el)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    print(f"Generated Draw.io XML: {filename}")


# =============================================================================
# FIGURE 1: 100% Mirror of code/generate_figure1_pipeline.py
# =============================================================================
def build_f1(out_path):
    sx = 8.4
    sy = 13.35
    W_canvas = 100 * sx
    H_canvas = 100 * sy

    def tx(x): return x * sx
    def ty(y, h=0): return (100 - y - h) * sy
    def tw(w): return w * sx
    def th(h): return h * sy

    elements = []
    connections = []
    f_serif = "fontFamily=Times New Roman, Times, serif;"

    c_card_bg = '#FFFFFF'
    c_container_bg = '#F8FAFC'
    c_border_neutral = '#CBD5E1'
    c_border_dark = '#64748B'
    c_text_dark = '#0F172A'
    c_text_muted = '#475569'
    c_navy_title = '#1E3A8A'
    c_blue_primary = '#1D4ED8'
    c_blue_mid = '#3B82F6'
    c_blue_subtle = '#EFF6FF'
    c_blue_border = '#93C5FD'
    c_slate_dark = '#334155'
    c_slate_mid = '#64748B'
    c_slate_border = '#CBD5E1'

    # 1. Dataset Input: draw_badge(12, 93.0, 76, 5.8)
    elements.append({
        'id': 'f1_dataset',
        'value': f'<b><font color="{c_text_dark}" size="3">High-Dimensional Dataset <i><b>X</b></i>, <i><b>Y</b></i></font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_border_neutral};strokeWidth=1.2;fontSize=13;{f_serif}",
        'x': tx(12), 'y': ty(93.0, 5.8), 'w': tw(76), 'h': th(5.8)
    })

    # Down arrow: (50, 93.0) -> (50, 88.5)
    connections.append({
        'id': 'f1_arr_dset_mi',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.8;endArrow=block;endFill=1;',
        'sourcePoint': [tx(50), ty(93.0)],
        'targetPoint': [tx(50), ty(87.7)]
    })

    # 2. MI-Prior Seeding: draw_badge(12, 81.5, 76, 6.2)
    elements.append({
        'id': 'f1_mi_seed',
        'value': f'<b><font color="{c_navy_title}" size="3">MI-Prior Seeding</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_blue_subtle};strokeColor={c_blue_border};strokeWidth=1.3;fontSize=13;{f_serif}",
        'x': tx(12), 'y': ty(81.5, 6.2), 'w': tw(76), 'h': th(6.2)
    })

    # Fork arrows from Seeding: (38, 81.5) -> (26.25, 73.0) and (62, 81.5) -> (73.75, 73.0)
    connections.append({
        'id': 'f1_fork_sub1',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.6;endArrow=block;endFill=1;',
        'sourcePoint': [tx(38), ty(81.5)],
        'targetPoint': [tx(26.25), ty(73.0)],
        'points': [(tx(26.25), ty(81.5))]
    })
    connections.append({
        'id': 'f1_fork_sub2',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_slate_dark};strokeWidth=1.6;endArrow=block;endFill=1;',
        'sourcePoint': [tx(62), ty(81.5)],
        'targetPoint': [tx(73.75), ty(73.0)],
        'points': [(tx(73.75), ty(81.5))]
    })

    # 3. Main Loop Container: (4.5, 14.5, 91, 59.5)
    elements.append({
        'id': 'f1_main_loop',
        'value': f'<b><font color="{c_text_dark}" size="2">Main Evolutionary Optimization Loop</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor={c_container_bg};strokeColor={c_border_dark};strokeWidth=1.3;verticalAlign=top;spacingTop=8;fontSize=12;{f_serif}",
        'x': tx(4.5), 'y': ty(14.5, 59.5), 'w': tw(91), 'h': th(59.5)
    })

    # Matrix W Box: (7.5, 61.0, 85.0, 9.0)
    elements.append({
        'id': 'f1_mat_w',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_border_neutral};strokeWidth=1.1;{f_serif}",
        'x': tx(7.5), 'y': ty(61.0, 9.0), 'w': tw(85.0), 'h': th(9.0)
    })
    elements.append({
        'id': 'f1_w_title',
        'value': f'<b><font color="{c_text_dark}">Cumulative Feature-Importance Matrix <i><b>W</b></i></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=11;{f_serif}",
        'x': tx(7.5), 'y': ty(61.0 + 6.5, 2.0), 'w': tw(85.0), 'h': th(2.0)
    })

    # 7 Feature strips: f_1, f_2, f_3, ..., f_{D-2}, f_{D-1}, f_D
    strip_labels = ['<i>f</i><sub>1</sub>', '<i>f</i><sub>2</sub>', '<i>f</i><sub>3</sub>', '&hellip;', '<i>f</i><sub><i>D</i>-2</sub>', '<i>f</i><sub><i>D</i>-1</sub>', '<i>f</i><sub><i>D</i></sub>']
    strip_weights = [0.92, 0.85, 0.20, None, 0.88, 0.15, 0.78]
    strip_w = 9.0
    strip_gap = 2.4
    total_strips_w = len(strip_labels) * strip_w + (len(strip_labels) - 1) * strip_gap
    strip_x_start = 7.5 + (85.0 - total_strips_w) / 2.0
    strip_y = 61.0 + 1.2
    strip_h = 3.2

    for si, (s_lbl, s_w) in enumerate(zip(strip_labels, strip_weights)):
        sx_val = strip_x_start + si * (strip_w + strip_gap)
        if s_w is not None:
            scol = '#084594' if s_w > 0.9 else ('#2171B5' if s_w > 0.8 else ('#3682BE' if s_w > 0.7 else ('#C6DBEF' if s_w > 0.18 else '#D9E6F4')))
            tcol = '#FFFFFF' if s_w > 0.6 else '#0F172A'
            elements.append({
                'id': f'f1_strip_{si}',
                'value': f'<b>{s_lbl}</b>',
                'style': f"rounded=0;whiteSpace=wrap;html=1;fillColor={scol};strokeColor=#94A3B8;fontColor={tcol};fontSize=9;align=center;verticalAlign=middle;strokeWidth=0.7;{f_serif}",
                'x': tx(sx_val), 'y': ty(strip_y, strip_h), 'w': tw(strip_w), 'h': th(strip_h)
            })
        else:
            elements.append({
                'id': f'f1_strip_{si}',
                'value': f'<b>{s_lbl}</b>',
                'style': f"rounded=0;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#CBD5E1;fontColor=#475569;fontSize=10;align=center;verticalAlign=middle;strokeWidth=0.7;{f_serif}",
                'x': tx(sx_val), 'y': ty(strip_y, strip_h), 'w': tw(strip_w), 'h': th(strip_h)
            })

    # Subpopulation 1: (7.5, 35.8, 37.5, 22.2)
    elements.append({
        'id': 'f1_sub1_box',
        'value': f'<b><font color="{c_navy_title}" size="2">Subpopulation 1 (&Pscr;<sub>1</sub>)</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.2;verticalAlign=top;spacingTop=8;{f_serif}",
        'x': tx(7.5), 'y': ty(35.8, 22.2), 'w': tw(37.5), 'h': th(22.2)
    })

    # Particles in Subpop 1
    ar_f1 = 5.6 / 8.9
    p1_coords = [(15.5, 47.0), (25.5, 50.0), (35.0, 46.5), (18.0, 39.5), (30.0, 39.0)]
    p1_angles = [35.0, 80.0, -35.0, -125.0, 145.0]
    for pi, ((px_val, py_val), ang) in enumerate(zip(p1_coords, p1_angles)):
        rad = np.radians(ang)
        dx_val = 3.85 * np.cos(rad)
        dy_val = 3.85 * ar_f1 * np.sin(rad)
        elements.append({
            'id': f'f1_p1_dot_{pi}',
            'value': '',
            'style': f'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={c_blue_primary};strokeColor=#FFFFFF;strokeWidth=0.9;',
            'x': tx(px_val - 1.47), 'y': ty(py_val - 1.47*ar_f1, 2.95*ar_f1), 'w': tw(2.95), 'h': th(2.95*ar_f1)
        })
        connections.append({
            'id': f'f1_p1_arr_{pi}',
            'style': f'edgeStyle=none;html=1;strokeColor={c_blue_mid};strokeWidth=1.5;endArrow=classic;endFill=1;',
            'sourcePoint': [tx(px_val), ty(py_val)],
            'targetPoint': [tx(px_val + dx_val), ty(py_val + dy_val)]
        })

    # Subpopulation 2: (55.0, 35.8, 37.5, 22.2)
    elements.append({
        'id': 'f1_sub2_box',
        'value': f'<b><font color="{c_slate_dark}" size="2">Subpopulation 2 (&Pscr;<sub>2</sub>)</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_slate_border};strokeWidth=1.2;verticalAlign=top;spacingTop=8;{f_serif}",
        'x': tx(55.0), 'y': ty(35.8, 22.2), 'w': tw(37.5), 'h': th(22.2)
    })

    # Particles in Subpop 2
    p2_coords = [(63.0, 47.0), (73.0, 50.0), (83.0, 46.5), (65.5, 39.5), (78.0, 39.0)]
    p2_angles = [-55.0, 45.0, 140.0, -140.0, 95.0]
    for pi, ((px_val, py_val), ang) in enumerate(zip(p2_coords, p2_angles)):
        rad = np.radians(ang)
        dx_val = 3.85 * np.cos(rad)
        dy_val = 3.85 * ar_f1 * np.sin(rad)
        elements.append({
            'id': f'f1_p2_dot_{pi}',
            'value': '',
            'style': f'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={c_slate_dark};strokeColor=#FFFFFF;strokeWidth=0.9;',
            'x': tx(px_val - 1.47), 'y': ty(py_val - 1.47*ar_f1, 2.95*ar_f1), 'w': tw(2.95), 'h': th(2.95*ar_f1)
        })
        connections.append({
            'id': f'f1_p2_arr_{pi}',
            'style': f'edgeStyle=none;html=1;strokeColor={c_slate_mid};strokeWidth=1.5;endArrow=classic;endFill=1;',
            'sourcePoint': [tx(px_val), ty(py_val)],
            'targetPoint': [tx(px_val + dx_val), ty(py_val + dy_val)]
        })

    # Inter-Subpop Transfer Badge: (42.5, 42.8, 15.0, 7.8)
    elements.append({
        'id': 'f1_trans_badge',
        'value': f'<b><font color="{c_navy_title}"><i><b>g</b></i><sub>best,2</sub> Transfer</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.1;fontSize=9;{f_serif}",
        'x': tx(42.5), 'y': ty(42.8, 7.8), 'w': tw(15.0), 'h': th(7.8)
    })
    connections.append({
        'id': 'f1_arr_transfer',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.6;endArrow=block;endFill=1;',
        'sourcePoint': [tx(54.5), ty(48.0)],
        'targetPoint': [tx(45.5), ty(48.0)]
    })

    # Arrows between Subpops and W
    connections.append({
        'id': 'f1_arr_sub1_w',
        'value': f'<b><font color="{c_blue_primary}" size="1">Reward Feedback</font></b>',
        'style': f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.4;endArrow=block;endFill=1;align=right;verticalAlign=bottom;{f_serif}",
        'sourcePoint': [tx(26.25), ty(58.0)],
        'targetPoint': [tx(26.25), ty(61.0)]
    })
    connections.append({
        'id': 'f1_arr_w_sub2',
        'value': f'<b><font color="{c_blue_primary}" size="1">Sample from <i><b>W</b></i></font></b>',
        'style': f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.4;endArrow=block;endFill=1;align=left;verticalAlign=bottom;{f_serif}",
        'sourcePoint': [tx(73.75), ty(61.0)],
        'targetPoint': [tx(73.75), ty(58.0)]
    })

    # Tier 1: Two-Phase Objective Weight Scheduling Bar: (7.5, 26.5, 85.0, 5.8)
    elements.append({
        'id': 'f1_tps_bar',
        'value': f'<b><font color="{c_navy_title}" size="2">Two-Phase Dynamic Objective Scheduling</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.1;fontSize=10;{f_serif}",
        'x': tx(7.5), 'y': ty(26.5, 5.8), 'w': tw(85.0), 'h': th(5.8)
    })
    connections.append({
        'id': 'f1_arr_sub1_tps',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.3;endArrow=block;endFill=1;',
        'sourcePoint': [tx(26.25), ty(35.8)],
        'targetPoint': [tx(26.25), ty(32.3)]
    })
    connections.append({
        'id': 'f1_arr_sub2_tps',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.3;endArrow=block;endFill=1;',
        'sourcePoint': [tx(73.75), ty(35.8)],
        'targetPoint': [tx(73.75), ty(32.3)]
    })

    # Tier 2: KER Card: (7.5, 16.0, 37.5, 6.2)
    elements.append({
        'id': 'f1_ker_card',
        'value': f'<b><font color="{c_navy_title}" size="2">Knowledge-Guided Elite Refinement</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.1;fontSize=10;{f_serif}",
        'x': tx(7.5), 'y': ty(16.0, 6.2), 'w': tw(37.5), 'h': th(6.2)
    })
    # Tier 2: Adaptive MI Re-injection Card: (55.0, 16.0, 37.5, 6.2)
    elements.append({
        'id': 'f1_reinit_card',
        'value': f'<b><font color="{c_navy_title}" size="2">Adaptive MI Re-injection</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.1;fontSize=10;{f_serif}",
        'x': tx(55.0), 'y': ty(16.0, 6.2), 'w': tw(37.5), 'h': th(6.2)
    })

    connections.append({
        'id': 'f1_arr_tps_ker',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.3;endArrow=block;endFill=1;',
        'sourcePoint': [tx(26.25), ty(26.5)],
        'targetPoint': [tx(26.25), ty(22.2)]
    })
    connections.append({
        'id': 'f1_arr_tps_reinit',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.3;endArrow=block;endFill=1;',
        'sourcePoint': [tx(73.75), ty(26.5)],
        'targetPoint': [tx(73.75), ty(22.2)]
    })

    # Re-injection feedback loop back to Subpop 2 (dashed)
    connections.append({
        'id': 'f1_arr_reinit_loop',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;dashed=1;strokeColor={c_blue_primary};strokeWidth=1.3;endArrow=block;endFill=1;',
        'sourcePoint': [tx(92.5), ty(19.1)],
        'targetPoint': [tx(92.5), ty(47.0)],
        'points': [(tx(97.0), ty(19.1)), (tx(97.0), ty(47.0))]
    })

    # Left Loop Arrow & Horizontal Badge: (t <- t + 1)
    connections.append({
        'id': 'f1_arr_left_loop',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.4;endArrow=block;endFill=1;',
        'sourcePoint': [tx(7.5), ty(19.1)],
        'targetPoint': [tx(7.5), ty(47.0)],
        'points': [(tx(2.0), ty(19.1)), (tx(2.0), ty(47.0))]
    })

    # Output Block:
    connections.append({
        'id': 'f1_arr_term',
        'value': '',
        'style': f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.8;endArrow=block;endFill=1;align=left;{f_serif}",
        'sourcePoint': [tx(50), ty(14.5)],
        'targetPoint': [tx(50), ty(8.5)]
    })
    elements.append({
        'id': 'f1_out_card',
        'value': f'<b><font color="{c_navy_title}" size="3">Optimal Compact Feature Subset <i><b>x</b></i><sup>&starf;</sup></font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_blue_subtle};strokeColor={c_blue_border};strokeWidth=1.3;fontSize=13;{f_serif}",
        'x': tx(10.0), 'y': ty(2.0, 6.0), 'w': tw(80.0), 'h': th(6.0)
    })

    create_drawio_xml(out_path, 'f1-architecture-pipeline', 'Figure 1: KDS-EL Architecture', W_canvas, H_canvas, elements, connections)


# =============================================================================
# FIGURE 2: 100% Mirror of code/generate_figure2_mi.py
# =============================================================================
def build_f2(out_path):
    sx = 16.5
    sy = 9.2
    W_canvas = 100 * sx
    H_canvas = 100 * sy

    def tx(x): return x * sx
    def ty(y, h=0): return (100 - y - h) * sy
    def tw(w): return w * sx
    def th(h): return h * sy

    elements = []
    connections = []
    f_serif = "fontFamily=Times New Roman, Times, serif;"

    c_card_bg = '#FFFFFF'
    c_panel_bg = '#F8FAFC'
    c_border_neutral = '#CBD5E1'
    c_text_dark = '#0F172A'
    c_text_muted = '#475569'
    c_blue_navy = '#1E3A8A'
    c_blue_primary = '#1D4ED8'
    c_blue_mid = '#3B82F6'
    c_blue_border = '#93C5FD'
    c_blue_cell = '#EFF6FF'
    c_slate_dark = '#334155'
    c_slate_mid = '#64748B'

    # -------------------------------------------------------------------------
    # STAGE 1 CONTAINER: (2.0, 3.0, 33.5, 94.0)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f2_s1_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(2.0), 'y': ty(3.0, 94.0), 'w': tw(33.5), 'h': th(94.0)
    })
    elements.append({
        'id': 'f2_s1_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="4">Offline Filter-Level MI Estimation</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(2.0), 'y': ty(85.5, 10.0), 'w': tw(33.5), 'h': th(10.0)
    })
    elements.append({
        'id': 'f2_s1_t1',
        'value': f'<b><font color="{c_text_dark}" size="2">Feature Space <i><b>X</b></i>, <i><b>Y</b></i></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(2.5), 'y': ty(77.5, 5.0), 'w': tw(15.5), 'h': th(5.0)
    })

    # Feature column badges: (3.2, 25.0, col_w=0.95, col_h=50.0)
    col_x_start = 3.2
    col_w = 0.95
    col_h = 50.0
    col_y = 25.0
    for c_idx in range(11):
        cx_val = col_x_start + c_idx * (col_w + 0.35)
        if c_idx == 5:
            elements.append({
                'id': f'f2_col_dots',
                'value': '&hellip;',
                'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=14;fontColor=#64748B;{f_serif}",
                'x': tx(cx_val), 'y': ty(col_y + 20.0, 10.0), 'w': tw(col_w), 'h': th(10.0)
            })
            continue
        b_col = '#93C5FD' if c_idx in [0, 1, 7, 9] else '#CBD5E1'
        elements.append({
            'id': f'f2_col_{c_idx}',
            'value': '',
            'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={b_col};strokeWidth=0.8;{f_serif}",
            'x': tx(cx_val), 'y': ty(col_y, col_h), 'w': tw(col_w), 'h': th(col_h)
        })

    # Column header labels
    elements.append({
        'id': 'f2_lbl_f1',
        'value': f'<b><font color="{c_text_dark}"><i>f</i><sub>1</sub></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=bottom;fontSize=11;{f_serif}",
        'x': tx(col_x_start), 'y': ty(col_y + col_h + 0.5, 3.0), 'w': tw(1.0), 'h': th(3.0)
    })
    elements.append({
        'id': 'f2_lbl_f2',
        'value': f'<b><font color="{c_text_dark}"><i>f</i><sub>2</sub></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=bottom;fontSize=11;{f_serif}",
        'x': tx(col_x_start + 1.3), 'y': ty(col_y + col_h + 0.5, 3.0), 'w': tw(1.0), 'h': th(3.0)
    })
    elements.append({
        'id': 'f2_lbl_f3',
        'value': f'<b><font color="{c_text_dark}"><i>f</i><sub>3</sub></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=bottom;fontSize=11;{f_serif}",
        'x': tx(col_x_start + 2.6), 'y': ty(col_y + col_h + 0.5, 3.0), 'w': tw(1.0), 'h': th(3.0)
    })
    elements.append({
        'id': 'f2_lbl_fD',
        'value': f'<b><font color="{c_text_dark}"><i>f</i><sub><i>D</i></sub></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=bottom;fontSize=11;{f_serif}",
        'x': tx(col_x_start + 10.3), 'y': ty(col_y + col_h + 0.5, 3.0), 'w': tw(1.0), 'h': th(3.0)
    })

    # Target Vector Y: (16.0, 25.0, 1.4, 50.0)
    y_vec_x = col_x_start + 12.8
    elements.append({
        'id': 'f2_vec_y',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_blue_cell};strokeColor={c_blue_border};strokeWidth=1.1;{f_serif}",
        'x': tx(y_vec_x), 'y': ty(col_y, col_h), 'w': tw(1.4), 'h': th(col_h)
    })
    elements.append({
        'id': 'f2_lbl_y',
        'value': f'<b><font color="{c_blue_navy}"><i><b>Y</b></i></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=bottom;fontSize=12;{f_serif}",
        'x': tx(y_vec_x), 'y': ty(col_y + col_h + 0.5, 3.0), 'w': tw(1.4), 'h': th(3.0)
    })

    # Arrow from Stage 1 left to MI: (18.2, 50.0) -> (21.5, 50.0)
    connections.append({
        'id': 'f2_arr_feat_mi',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.2;endArrow=block;endFill=1;',
        'sourcePoint': [tx(18.2), ty(50.0)],
        'targetPoint': [tx(21.5), ty(50.0)]
    })

    # MI Estimation Header: (26.8, 81.5)
    elements.append({
        'id': 'f2_s1_t2',
        'value': f'<b><font color="{c_blue_navy}" size="2">Mutual Information Profile</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(19.0), 'y': ty(77.5, 5.0), 'w': tw(15.5), 'h': th(5.0)
    })

    # Continuous MI Relevance Profile: (22.2, 39.0, 9.2, 36.0)
    elements.append({
        'id': 'f2_mi_bar_high',
        'value': f'<b><font color="{c_blue_navy}">High MI</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_blue_primary};strokeColor=none;fontColor=#FFFFFF;fontSize=10;align=left;spacingLeft=6;{f_serif}",
        'x': tx(22.2), 'y': ty(65.0, 10.0), 'w': tw(9.2), 'h': th(10.0)
    })
    elements.append({
        'id': 'f2_mi_bar_mid',
        'value': f'<font color="{c_blue_navy}">Medium MI</font>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_blue_mid};strokeColor=none;fontColor=#FFFFFF;fontSize=10;align=left;spacingLeft=6;{f_serif}",
        'x': tx(22.2), 'y': ty(52.0, 10.0), 'w': tw(6.5), 'h': th(10.0)
    })
    elements.append({
        'id': 'f2_mi_bar_low',
        'value': f'<font color="{c_text_muted}">Low MI</font>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=none;fontColor=#0F172A;fontSize=10;align=left;spacingLeft=6;{f_serif}",
        'x': tx(22.2), 'y': ty(39.0, 10.0), 'w': tw(3.5), 'h': th(10.0)
    })

    # Down arrow from profile to norm: (26.8, 37.5) -> (26.8, 33.5)
    connections.append({
        'id': 'f2_arr_mi_norm',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.6;endArrow=block;endFill=1;',
        'sourcePoint': [tx(26.8), ty(37.5)],
        'targetPoint': [tx(26.8), ty(33.5)]
    })

    # Min-Max Normalization Box: (20.0, 19.0, 13.6, 12.5)
    elements.append({
        'id': 'f2_norm_box',
        'value': f'<b><font color="{c_blue_navy}" size="2">MI-Derived Prior Vector</font></b><br><br><b><font color="{c_text_dark}" size="2">m&#771; = (I - <i>I</i><sub>min</sub>) / (<i>I</i><sub>max</sub> - <i>I</i><sub>min</sub>) &isin; [0, 1]<sup><i>D</i></sup></font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.2;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(20.0), 'y': ty(19.0, 12.5), 'w': tw(13.6), 'h': th(12.5)
    })

    # -------------------------------------------------------------------------
    # STAGE 2 CONTAINER: (36.8, 3.0, 35.2, 94.0)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f2_s2_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(36.8), 'y': ty(3.0, 94.0), 'w': tw(35.2), 'h': th(94.0)
    })
    elements.append({
        'id': 'f2_s2_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="4">Knowledge-Informed Swarm Seeding</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(37.5), 'y': ty(85.5, 10.0), 'w': tw(34.0), 'h': th(10.0)
    })

    # Prior Vector Feed Arrow from Stage 1 into Stage 2 (MI-Guided Branch ONLY)
    connections.append({
        'id': 'f2_arr_fork_ub',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.2;endArrow=block;endFill=1;',
        'sourcePoint': [tx(33.6), ty(25.25)],
        'targetPoint': [tx(38.5), ty(67.0)],
        'points': [(tx(36.0), ty(25.25)), (tx(36.0), ty(67.0))]
    })

    # Upper Branch: (38.5, 52.0, 14.8, 30.0)
    elements.append({
        'id': 'f2_ub_card',
        'value': f'<b><font color="{c_blue_navy}" size="3">MI-Guided Seeding</font></b><br><br><b><font color="{c_blue_primary}">p</font></b><sub><i>i</i></sub> = clip(<b>m&#771;</b> + <b>&epsilon;</b><sub><i>i</i></sub>, 0, 1)<br><font color="{c_text_muted}" size="1"><b>&epsilon;</b><sub><i>i</i></sub> ~ &Nscr;(0, &sigma;<sup>2</sup><b>I</b>)</font>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.3;verticalAlign=top;spacingTop=6;{f_serif}",
        'x': tx(38.5), 'y': ty(52.0, 30.0), 'w': tw(14.8), 'h': th(30.0)
    })
    # 7 bars in Upper Branch (Exact heights: [6.0, 5.2, 2.0, 1.5, 2.8, 4.8, 5.8])
    ub_bars = [6.0, 5.2, 2.0, 1.5, 2.8, 4.8, 5.8]
    for b_idx, bh in enumerate(ub_bars):
        bx_val = 38.5 + 1.6 + b_idx * 1.7
        bc_val = c_blue_primary if bh > 3.5 else c_blue_border
        elements.append({
            'id': f'f2_ub_bar_{b_idx}',
            'value': '',
            'style': f'rounded=0;whiteSpace=wrap;html=1;fillColor={bc_val};strokeColor=none;',
            'x': tx(bx_val), 'y': ty(56.5, bh), 'w': tw(1.1), 'h': th(bh)
        })

    # Lower Branch: (38.5, 18.0, 14.8, 30.0)
    elements.append({
        'id': 'f2_lb_card',
        'value': f'<b><font color="{c_slate_dark}" size="3">Uniform Random Seeding</font></b><br><br><br><b><font color="{c_slate_dark}">p</font></b><sub><i>i</i></sub> ~ &Uscr;(0, 1)<sup><i>D</i></sup>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_border_neutral};strokeWidth=1.3;verticalAlign=top;spacingTop=6;{f_serif}",
        'x': tx(38.5), 'y': ty(18.0, 30.0), 'w': tw(14.8), 'h': th(30.0)
    })
    # 7 bars in Lower Branch (Seed 99 exact random heights)
    np.random.seed(99)
    lb_bars = [float(np.random.uniform(1.8, 5.2)) for _ in range(7)]
    for b_idx, bh in enumerate(lb_bars):
        bx_val = 38.5 + 1.6 + b_idx * 1.7
        elements.append({
            'id': f'f2_lb_bar_{b_idx}',
            'value': '',
            'style': f'rounded=0;whiteSpace=wrap;html=1;fillColor={c_slate_mid};strokeColor=none;',
            'x': tx(bx_val), 'y': ty(22.5, bh), 'w': tw(1.1), 'h': th(bh)
        })

    # Merging arrows:
    connections.append({
        'id': 'f2_arr_ub_pop',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.2;endArrow=block;endFill=1;',
        'sourcePoint': [tx(53.3), ty(67.0)],
        'targetPoint': [tx(55.5), ty(62.0)]
    })
    connections.append({
        'id': 'f2_arr_lb_pop',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_slate_dark};strokeWidth=2.2;endArrow=block;endFill=1;',
        'sourcePoint': [tx(53.3), ty(33.0)],
        'targetPoint': [tx(55.5), ty(38.0)]
    })

    # Initial PSO Swarm Box: (55.5, 18.0, 15.0, 64.0)
    elements.append({
        'id': 'f2_pop_box',
        'value': f'<b><font color="{c_blue_navy}" size="3">Initial PSO Swarm</font></b><br><font color="{c_text_muted}" size="1">&Pscr; = {{<b>p</b><sub>1</sub>, ..., <b>p</b><sub><i>N</i></sub>}}</font>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor=#94A3B8;strokeWidth=1.4;verticalAlign=top;spacingTop=6;{f_serif}",
        'x': tx(55.5), 'y': ty(18.0, 64.0), 'w': tw(15.0), 'h': th(64.0)
    })
    elements.append({
        'id': 'f2_pop_sub1_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="1">Subpopulation 1: MI-Guided</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(55.5), 'y': ty(66.5, 4.0), 'w': tw(15.0), 'h': th(4.0)
    })

    # Particles in Subpop 1 (Exact 9 angles from script)
    aspect_f2 = 16.5 / 9.2
    p1_angles_f2 = [25.0, 65.0, 10.0, 80.0, 45.0, -20.0, 60.0, 35.0, 75.0]
    idx_p1 = 0
    np.random.seed(77)
    for row in range(3):
        for col in range(3):
            dot_x = 55.5 + 3.0 + col * 4.4 + float(np.random.uniform(-0.3, 0.3))
            dot_y = 18.0 + 36.5 + row * 4.0 + float(np.random.uniform(-0.3, 0.3))
            rad = np.radians(p1_angles_f2[idx_p1 % len(p1_angles_f2)])
            dx = 1.3 * np.cos(rad)
            dy = 1.3 * aspect_f2 * np.sin(rad)
            idx_p1 += 1
            elements.append({
                'id': f'f2_p1_dot_{row}_{col}',
                'value': '',
                'style': f'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={c_blue_primary};strokeColor=#FFFFFF;strokeWidth=0.9;',
                'x': tx(dot_x - 0.5), 'y': ty(dot_y - 0.5*aspect_f2, 1.0*aspect_f2), 'w': tw(1.0), 'h': th(1.0*aspect_f2)
            })
            connections.append({
                'id': f'f2_p1_v_{row}_{col}',
                'style': f'edgeStyle=none;html=1;strokeColor={c_blue_mid};strokeWidth=1.5;endArrow=classic;endFill=1;',
                'sourcePoint': [tx(dot_x), ty(dot_y)],
                'targetPoint': [tx(dot_x + dx), ty(dot_y + dy)]
            })

    # Divider line
    elements.append({
        'id': 'f2_pop_divider',
        'value': '',
        'style': 'line;strokeWidth=1.1;strokeColor=#CBD5E1;dashed=1;',
        'x': tx(57.0), 'y': ty(50.0, 0.5), 'w': tw(12.0), 'h': th(0.5)
    })

    elements.append({
        'id': 'f2_pop_sub2_hdr',
        'value': f'<b><font color="{c_slate_dark}" size="1">Subpopulation 2: Random</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(55.5), 'y': ty(44.5, 4.0), 'w': tw(15.0), 'h': th(4.0)
    })

    # Particles in Subpop 2 (Exact 9 angles from script)
    p2_angles_f2 = [135.0, -45.0, 210.0, 30.0, -120.0, 85.0, 165.0, -70.0, 0.0]
    idx_p2 = 0
    np.random.seed(88)
    for row in range(3):
        for col in range(3):
            dot_x = 55.5 + 3.0 + col * 4.4 + float(np.random.uniform(-0.3, 0.3))
            dot_y = 18.0 + 13.5 + row * 4.0 + float(np.random.uniform(-0.3, 0.3))
            rad = np.radians(p2_angles_f2[idx_p2 % len(p2_angles_f2)])
            dx = 1.3 * np.cos(rad)
            dy = 1.3 * aspect_f2 * np.sin(rad)
            idx_p2 += 1
            elements.append({
                'id': f'f2_p2_dot_{row}_{col}',
                'value': '',
                'style': f'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={c_slate_mid};strokeColor=#FFFFFF;strokeWidth=0.9;',
                'x': tx(dot_x - 0.5), 'y': ty(dot_y - 0.5*aspect_f2, 1.0*aspect_f2), 'w': tw(1.0), 'h': th(1.0*aspect_f2)
            })
            connections.append({
                'id': f'f2_p2_v_{row}_{col}',
                'style': f'edgeStyle=none;html=1;strokeColor={c_slate_dark};strokeWidth=1.5;endArrow=classic;endFill=1;',
                'sourcePoint': [tx(dot_x), ty(dot_y)],
                'targetPoint': [tx(dot_x + dx), ty(dot_y + dy)]
            })

    # -------------------------------------------------------------------------
    # STAGE 3 CONTAINER: (73.2, 3.0, 24.8, 94.0)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f2_s3_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(73.2), 'y': ty(3.0, 94.0), 'w': tw(24.8), 'h': th(94.0)
    })
    elements.append({
        'id': 'f2_s3_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="4">Search Space &amp; Stagnation Recovery</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(74.0), 'y': ty(85.5, 10.0), 'w': tw(23.2), 'h': th(10.0)
    })

    # Arrow from Pop to Search Space: (70.5, 50.0) -> (74.5, 50.0)
    connections.append({
        'id': 'f2_arr_pop_search',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_navy};strokeWidth=2.2;endArrow=block;endFill=1;',
        'sourcePoint': [tx(70.5), ty(50.0)],
        'targetPoint': [tx(74.5), ty(50.0)]
    })

    # 2D Fitness Contour Landscape Box: (74.5, 18.0, 22.2, 64.0)
    elements.append({
        'id': 'f2_landscape_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(74.5), 'y': ty(18.0, 64.0), 'w': tw(22.2), 'h': th(64.0)
    })

    # Concentric Contours around center (85.6, 60.0):
    c_center = (85.6, 60.0)
    contour_specs_d = [(19.5, 14.5, '0.35'), (15.0, 11.0, '0.50'), (10.8, 7.8, '0.65'), (6.8, 4.8, '0.80'), (3.4, 2.4, '0.95')]
    for r_idx, (rw, rh, c_alpha) in enumerate(contour_specs_d):
        elements.append({
            'id': f'f2_contour_{r_idx}',
            'value': '',
            'style': f'ellipse;whiteSpace=wrap;html=1;fillColor=none;strokeColor={c_blue_border};strokeWidth=1.3;opacity={int(float(c_alpha)*100)};',
            'x': tx(c_center[0] - rw/2), 'y': ty(c_center[1] - rh/2, rh), 'w': tw(rw), 'h': th(rh)
        })

    # Optimum Star
    elements.append({
        'id': 'f2_opt_star',
        'value': f'<b><font color="{c_blue_navy}" size="3">&starf; <b>x</b><sup>&starf;</sup> Optimum</font></b>',
        'style': f"text;html=1;align=left;verticalAlign=middle;{f_serif}",
        'x': tx(c_center[0] + 1.2), 'y': ty(c_center[1] + 1.2, 4.0), 'w': tw(10.0), 'h': th(4.0)
    })

    # Converging trajectories
    connections.append({
        'id': 'f2_traj_1',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.8;endArrow=block;endFill=1;',
        'sourcePoint': [tx(76.7), ty(72.0)],
        'targetPoint': [tx(84.2), ty(61.2)],
        'points': [(tx(81.3), ty(67.0))]
    })
    connections.append({
        'id': 'f2_traj_2',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_mid};strokeWidth=1.8;endArrow=block;endFill=1;',
        'sourcePoint': [tx(77.1), ty(46.0)],
        'targetPoint': [tx(84.8), ty(58.8)],
        'points': [(tx(82.0), ty(52.0))]
    })

    # Stagnation Trap Node: (84.1, 29.0)
    elements.append({
        'id': 'f2_stag_basin',
        'value': f'<b><font color="{c_slate_dark}" size="2">Stagnation Detected</font></b>',
        'style': f"ellipse;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor={c_slate_dark};strokeWidth=1.3;dashed=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(84.1 - 5.25), 'y': ty(29.0 - 3.25, 6.5), 'w': tw(10.5), 'h': th(6.5)
    })

    # Adaptive MI Re-injection Card: (48.0, 4.5, 42.0, 9.2)
    elements.append({
        'id': 'f2_reinit_card',
        'value': f'<b><font color="{c_blue_navy}" size="3">Adaptive MI Re-injection</font></b><br><font color="{c_text_dark}" size="2"><b>p</b><sub>inferior</sub> &larr; clip(<b>m&#771;</b> + <b>&epsilon;</b><sub><i>i</i></sub>, 0, 1)</font>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.2;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(48.0), 'y': ty(4.5, 9.2), 'w': tw(42.0), 'h': th(9.2)
    })

    # Leg 1: Stagnation Trap -> Re-injection Badge:
    connections.append({
        'id': 'f2_arr_stag_reinit',
        'value': '<b><font color="{c_blue_navy}">Trigger</font></b>',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.0;endArrow=block;endFill=1;align=center;{f_serif}',
        'sourcePoint': [tx(84.1), ty(25.75)],
        'targetPoint': [tx(85.0), ty(13.7)]
    })

    # Leg 2: Re-injection Badge -> Initial PSO Swarm:
    connections.append({
        'id': 'f2_arr_reinit_pop',
        'value': '<b><font color="{c_blue_navy}">Re-inject</font></b>',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.0;endArrow=block;endFill=1;align=center;{f_serif}',
        'sourcePoint': [tx(58.0), ty(13.7)],
        'targetPoint': [tx(63.0), ty(18.0)]
    })

    create_drawio_xml(out_path, 'f2-mi-seeding', 'Figure 2: MI-Prior Seeding & Re-injection', W_canvas, H_canvas, elements, connections)


# =============================================================================
# FIGURE 3: 100% Mirror of code/generate_figure3_ker.py
# =============================================================================
def build_f3(out_path):
    sx = 16.5
    sy = 9.2
    W_canvas = 100 * sx
    H_canvas = 100 * sy

    def tx(x): return x * sx
    def ty(y, h=0): return (100 - y - h) * sy
    def tw(w): return w * sx
    def th(h): return h * sy

    elements = []
    connections = []
    f_serif = "fontFamily=Times New Roman, Times, serif;"

    c_card_bg = '#FFFFFF'
    c_panel_bg = '#F8FAFC'
    c_border_neutral = '#CBD5E1'
    c_text_dark = '#0F172A'
    c_text_muted = '#475569'
    c_blue_navy = '#1E3A8A'
    c_blue_primary = '#1D4ED8'
    c_blue_mid = '#3B82F6'
    c_blue_border = '#93C5FD'
    c_blue_cell = '#EFF6FF'
    c_slate_dark = '#334155'
    c_slate_mid = '#64748B'

    # -------------------------------------------------------------------------
    # STAGE 1: Swarm Evaluation (2.0, 13.0, 29.5, 84.5)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f3_s1_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(2.0), 'y': ty(13.0, 84.5), 'w': tw(29.5), 'h': th(84.5)
    })
    elements.append({
        'id': 'f3_s1_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="3">Swarm Evaluation</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(2.0), 'y': ty(91.0, 5.0), 'w': tw(29.5), 'h': th(5.0)
    })

    # Pop Data Table headers: f_1, f_2, f_3, ..., f_D
    feat_labels = ['<i>f</i><sub>1</sub>', '<i>f</i><sub>2</sub>', '<i>f</i><sub>3</sub>', '&hellip;', '<i>f</i><sub><i>D</i></sub>']
    feat_x = [6.2 + 2.1*0.5, 6.2 + 2.1*1.5, 6.2 + 2.1*2.5, 6.2 + 2.1*6 + 0.8, 6.2 + 2.1*7 + 1.6 + 2.1*1.0]
    for lbl, fx in zip(feat_labels, feat_x):
        elements.append({
            'id': f'f3_hdr_{lbl}',
            'value': f'<b>{lbl}</b>',
            'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=10;{f_serif}",
            'x': tx(fx - 1.0), 'y': ty(86.5, 2.5), 'w': tw(2.0), 'h': th(2.5)
        })

    pop_data = [
        ('<b>p</b><sub>1</sub>', [1, 0, 1, 0, 1, 0, '...', 1, 0, 0]),
        ('<b>p</b><sub>2</sub>', [0, 1, 0, 1, 1, 0, '...', 0, 1, 1]),
        ('<b>p</b><sub>3</sub>', [1, 1, 0, 0, 1, 0, '...', 1, 0, 0]),
        ('dots', None),
        ('<b>p</b><sub><i>N</i></sub>', [0, 1, 1, 0, 0, 1, '...', 1, 1, 0])
    ]
    cell_w, cell_h = 2.1, 2.9
    y_start = 82.5
    y_spacing = 6.4
    lx_start = 6.2

    for row_idx, (p_name, bits) in enumerate(pop_data):
        curr_y = y_start - row_idx * y_spacing
        if p_name == 'dots':
            elements.append({
                'id': 'f3_pop_dots',
                'value': '&vellip;',
                'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=14;fontColor=#0F172A;{f_serif}",
                'x': tx(16.7 - 2.0), 'y': ty(curr_y, cell_h), 'w': tw(4.0), 'h': th(cell_h)
            })
            continue

        elements.append({
            'id': f'f3_pop_lbl_{row_idx}',
            'value': p_name,
            'style': f"text;html=1;align=right;verticalAlign=middle;fontSize=10;fontColor={c_text_dark};{f_serif}",
            'x': tx(3.0), 'y': ty(curr_y, cell_h), 'w': tw(3.0), 'h': th(cell_h)
        })

        x_c = lx_start
        for b_idx, b in enumerate(bits):
            if b == '...':
                elements.append({
                    'id': f'f3_cell_dots_{row_idx}',
                    'value': '&hellip;',
                    'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=10;fontColor={c_text_dark};{f_serif}",
                    'x': tx(x_c), 'y': ty(curr_y, cell_h), 'w': tw(1.8), 'h': th(cell_h)
                })
                x_c += 1.8
            else:
                bg = c_blue_cell if b == 1 else c_card_bg
                elements.append({
                    'id': f'f3_bit_{row_idx}_{b_idx}',
                    'value': str(b),
                    'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={bg};strokeColor={c_border_neutral};fontSize=9;align=center;verticalAlign=middle;{f_serif}",
                    'x': tx(x_c), 'y': ty(curr_y, cell_h), 'w': tw(cell_w), 'h': th(cell_h)
                })
                x_c += cell_w

    # Down arrow to Fitness Evaluation: (16.7, 52.5) -> (16.7, 44.5)
    connections.append({
        'id': 'f3_arr_pop_eval',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.0;endArrow=block;endFill=1;',
        'sourcePoint': [tx(16.7), ty(52.5)],
        'targetPoint': [tx(16.7), ty(44.5)]
    })

    # Fitness Evaluation Box: (4.5, 16.5, 24.5, 28.0)
    elements.append({
        'id': 'f3_eval_box',
        'value': f'<b><font color="{c_blue_navy}" size="2">Fitness Evaluation</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.3;verticalAlign=bottom;spacingBottom=10;{f_serif}",
        'x': tx(4.5), 'y': ty(16.5, 28.0), 'w': tw(24.5), 'h': th(28.0)
    })
    # 3 Evaluation metric bars
    elements.append({
        'id': 'f3_bar_acc',
        'value': '',
        'style': f'rounded=0;whiteSpace=wrap;html=1;fillColor={c_blue_mid};strokeColor=none;',
        'x': tx(4.5 + 3.5), 'y': ty(16.5 + 8.5, 9.5), 'w': tw(4.2), 'h': th(9.5)
    })
    elements.append({
        'id': 'f3_bar_feat',
        'value': '',
        'style': f'rounded=0;whiteSpace=wrap;html=1;fillColor={c_blue_primary};strokeColor=none;',
        'x': tx(4.5 + 9.8), 'y': ty(16.5 + 8.5, 13.5), 'w': tw(4.2), 'h': th(13.5)
    })
    elements.append({
        'id': 'f3_bar_comp',
        'value': '',
        'style': 'rounded=0;whiteSpace=wrap;html=1;fillColor=#60A5FA;strokeColor=none;',
        'x': tx(4.5 + 16.1), 'y': ty(16.5 + 8.5, 7.0), 'w': tw(4.2), 'h': th(7.0)
    })

    # -------------------------------------------------------------------------
    # STAGE 2: Knowledge Accumulation (33.0, 13.0, 32.5, 84.5)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f3_s2_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(33.0), 'y': ty(13.0, 84.5), 'w': tw(32.5), 'h': th(84.5)
    })
    elements.append({
        'id': 'f3_s2_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="3">Knowledge Accumulation</font></b><br><font color="{c_text_muted}" size="1"><i>Historical Multi-Generation Experience</i></font>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(33.0), 'y': ty(87.5, 8.0), 'w': tw(32.5), 'h': th(8.0)
    })

    # Fitness Feedback curved top arrow: (22.0, 95.8) -> (38.0, 95.8)
    connections.append({
        'id': 'f3_arr_fb',
        'value': f'<b><font color="{c_blue_primary}" size="1">Fitness Feedback</font></b>',
        'style': f"edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.0;endArrow=block;endFill=1;align=center;{f_serif}",
        'sourcePoint': [tx(22.0), ty(95.8)],
        'targetPoint': [tx(38.0), ty(95.8)]
    })

    # Generation cards: P(t-2), P(t-1), P(t) (cx = 36.0, 46.0, 56.0, y=75.5, w=6.5, h=10.5)
    g_cards_data = [
        (r'&Pscr;<sup>(<i>t</i>-2)</sup>', 36.0, '#60A5FA', [(-0.3, 0.4), (0.2, 0.6), (0.0, 0.0), (-0.2, -0.4), (0.3, -0.3)]),
        (r'&Pscr;<sup>(<i>t</i>-1)</sup>', 46.0, c_blue_mid, [(0.1, 0.5), (-0.2, 0.3), (0.0, 0.0), (0.2, -0.4), (-0.1, -0.5)]),
        (r'&Pscr;<sup>(<i>t</i>)</sup>', 56.0, c_blue_primary, [(0.2, 0.4), (-0.3, 0.5), (0.0, 0.1), (0.1, -0.3), (-0.2, -0.4)])
    ]
    for glbl, gcx, gcol, pts in g_cards_data:
        elements.append({
            'id': f'f3_gcard_{glbl}',
            'value': f'<b><font color="{c_text_dark}">{glbl}</font></b>',
            'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_border_neutral};strokeWidth=1.0;verticalAlign=bottom;spacingBottom=3;fontSize=10;{f_serif}",
            'x': tx(gcx), 'y': ty(75.5, 10.5), 'w': tw(6.5), 'h': th(10.5)
        })
        for pt_idx, (px, py) in enumerate(pts):
            elements.append({
                'id': f'f3_gcard_pt_{glbl}_{pt_idx}',
                'value': '',
                'style': f'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={gcol};strokeColor=none;',
                'x': tx(gcx + 3.25 + px*1.5 - 0.38), 'y': ty(82.0 + py*1.6 - 0.38, 0.76), 'w': tw(0.76), 'h': th(0.76)
            })
        connections.append({
            'id': f'f3_arr_card_w_{glbl}',
            'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.6;endArrow=block;endFill=1;',
            'sourcePoint': [tx(gcx + 3.25), ty(74.5)],
            'targetPoint': [tx(gcx + 3.25), ty(66.0)]
        })

    # Matrix W Title: (49.2, 63.0)
    elements.append({
        'id': 'f3_w_title',
        'value': f'<b><font color="{c_text_dark}" size="2">Cumulative Feature-Importance Matrix <i><b>W</b></i></font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(33.0), 'y': ty(61.5, 3.5), 'w': tw(32.5), 'h': th(3.5)
    })

    # Strips: f_1, f_2, f_3, ..., f_{D-2}, f_{D-1}, f_D
    w_strip_labels = ['<i>f</i><sub>1</sub>', '<i>f</i><sub>2</sub>', '<i>f</i><sub>3</sub>', '&hellip;', '<i>f</i><sub><i>D</i>-2</sub>', '<i>f</i><sub><i>D</i>-1</sub>', '<i>f</i><sub><i>D</i></sub>']
    w_strip_vals = [0.92, 0.74, 0.41, None, 0.88, 0.22, 0.65]
    w_box_w = 3.6
    w_box_h = 4.2
    w_gap = 0.6
    total_w_width = len(w_strip_labels) * w_box_w + (len(w_strip_labels) - 1) * w_gap
    w_x_start = 49.2 - total_w_width / 2.0
    w_y_base = 51.0

    for si, (s_lbl, s_v) in enumerate(zip(w_strip_labels, w_strip_vals)):
        sx_val = w_x_start + si * (w_box_w + w_gap)
        if s_v is not None:
            scol = '#084594' if s_v > 0.9 else ('#2171B5' if s_v > 0.7 else ('#4292C6' if s_v > 0.5 else ('#9ECAE1' if s_v > 0.3 else '#C6DBEF')))
            st_color = '#FFFFFF' if s_v > 0.6 else '#0F172A'
            bd_color = '#94A3B8' if s_v <= 0.6 else '#1D4ED8'
            elements.append({
                'id': f'f3_w_strip_{si}',
                'value': f'<b>{s_lbl}</b>',
                'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={scol};strokeColor={bd_color};fontColor={st_color};fontSize=10;align=center;verticalAlign=middle;strokeWidth=1.0;{f_serif}",
                'x': tx(sx_val), 'y': ty(w_y_base, w_box_h), 'w': tw(w_box_w), 'h': th(w_box_h)
            })
        else:
            elements.append({
                'id': f'f3_w_strip_{si}',
                'value': f'<b>{s_lbl}</b>',
                'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor={c_border_neutral};fontColor=#475569;fontSize=11;align=center;verticalAlign=middle;strokeWidth=0.9;{f_serif}",
                'x': tx(sx_val), 'y': ty(w_y_base, w_box_h), 'w': tw(w_box_w), 'h': th(w_box_h)
            })

    # Legend below Matrix W:
    elements.append({
        'id': 'f3_leg1',
        'value': f'<b><font color="{c_blue_navy}" size="1">High <i>W<sub>j</sub></i>: Key Features</font></b>',
        'style': f"rounded=0;whiteSpace=wrap;html=1;fillColor={c_blue_primary};strokeColor=none;fontColor=#FFFFFF;fontSize=9;{f_serif}",
        'x': tx(34.5), 'y': ty(45.0, 2.0), 'w': tw(13.0), 'h': th(2.0)
    })
    elements.append({
        'id': 'f3_leg2',
        'value': f'<b><font color="{c_text_muted}" size="1">Low <i>W<sub>j</sub></i>: Redundant Features</font></b>',
        'style': f"rounded=0;whiteSpace=wrap;html=1;fillColor={c_border_neutral};strokeColor=none;fontColor=#0F172A;fontSize=9;{f_serif}",
        'x': tx(49.5), 'y': ty(45.0, 2.0), 'w': tw(15.0), 'h': th(2.0)
    })

    # Dynamic Memory Decay Box: (35.0, 16.5, 28.5, 24.5)
    elements.append({
        'id': 'f3_decay_box',
        'value': f'<b><font color="{c_blue_navy}" size="2">Dynamic Memory Decay</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_border_neutral};strokeWidth=1.2;align=center;verticalAlign=top;spacingTop=6;{f_serif}",
        'x': tx(35.0), 'y': ty(16.5, 24.5), 'w': tw(28.5), 'h': th(24.5)
    })

    # -------------------------------------------------------------------------
    # STAGE 3: Knowledge-Guided Elite Refinement (67.0, 13.0, 31.0, 84.5)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f3_s3_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(67.0), 'y': ty(13.0, 84.5), 'w': tw(31.0), 'h': th(84.5)
    })
    elements.append({
        'id': 'f3_s3_hdr',
        'value': f'<b><font color="{c_blue_navy}" size="3">Knowledge-Guided Elite Refinement</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(67.0), 'y': ty(91.0, 5.0), 'w': tw(31.0), 'h': th(5.0)
    })

    # Array 1: Elite Solution (Before Refinement)
    elements.append({
        'id': 'f3_arr1_title',
        'value': f'<b><font color="{c_text_dark}" size="2">Elite Solution <b>x</b><sub><i>e</i></sub> (Before Refinement)</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(68.0), 'y': ty(86.0, 3.0), 'w': tw(29.0), 'h': th(3.0)
    })
    bits_eb = [0, 1, 1, 0, 1, 0, 1, '...', 0, 1]
    bx_w = 2.5
    bx_h = 3.3
    bx_start = 82.5 - (len(bits_eb) * bx_w) / 2.0
    for bi, b in enumerate(bits_eb):
        cur_bx = bx_start + bi * bx_w
        if b == '...':
            elements.append({
                'id': f'f3_eb_dots',
                'value': '&hellip;',
                'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor={c_text_dark};{f_serif}",
                'x': tx(cur_bx), 'y': ty(80.5, bx_h), 'w': tw(bx_w), 'h': th(bx_h)
            })
        else:
            bc = c_blue_primary if bi == 0 else (c_slate_dark if bi == 4 else c_border_neutral)
            bw = '1.6' if bi in [0, 4] else '0.9'
            elements.append({
                'id': f'f3_eb_{bi}',
                'value': str(b),
                'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={bc};strokeWidth={bw};fontSize=11;align=center;verticalAlign=middle;{f_serif}",
                'x': tx(cur_bx), 'y': ty(80.5, bx_h), 'w': tw(bx_w), 'h': th(bx_h)
            })

    # Down arrow 1: (82.5, 79.5) -> (82.5, 75.5)
    connections.append({
        'id': 'f3_arr_eb_kf',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_dark};strokeWidth=1.8;endArrow=block;endFill=1;',
        'sourcePoint': [tx(82.5), ty(79.5)],
        'targetPoint': [tx(82.5), ty(75.5)]
    })

    # Array 2: Knowledge-Guided Directional Flip (y=66.5)
    elements.append({
        'id': 'f3_arr2_title',
        'value': f'<b><font color="{c_blue_navy}" size="2">Knowledge-Guided Directional Flip</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(68.0), 'y': ty(72.0, 3.0), 'w': tw(29.0), 'h': th(3.0)
    })
    bits_kf = [1, 1, 1, 0, 0, 0, 1, '...', 0, 1]
    for bi, b in enumerate(bits_kf):
        cur_bx = bx_start + bi * bx_w
        if b == '...':
            elements.append({
                'id': f'f3_kf_dots',
                'value': '&hellip;',
                'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor={c_text_dark};{f_serif}",
                'x': tx(cur_bx), 'y': ty(66.5, bx_h), 'w': tw(bx_w), 'h': th(bx_h)
            })
        else:
            bg = '#DBEAFE' if bi == 0 else ('#F1F5F9' if bi == 4 else c_card_bg)
            bc = c_blue_primary if bi == 0 else (c_slate_dark if bi == 4 else c_border_neutral)
            bw = '1.3' if bi in [0, 4] else '0.9'
            elements.append({
                'id': f'f3_kf_{bi}',
                'value': str(b),
                'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={bg};strokeColor={bc};strokeWidth={bw};fontSize=11;align=center;verticalAlign=middle;{f_serif}",
                'x': tx(cur_bx), 'y': ty(66.5, bx_h), 'w': tw(bx_w), 'h': th(bx_h)
            })

    # Flip indicators: 0 -> 1 and 1 -> 0
    elements.append({
        'id': 'f3_flip_ind1',
        'value': f'<b><font color="{c_blue_primary}">0 &rarr; 1</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=10;{f_serif}",
        'x': tx(bx_start), 'y': ty(61.5, 2.2), 'w': tw(bx_w), 'h': th(2.2)
    })
    elements.append({
        'id': 'f3_flip_ind2',
        'value': f'<b><font color="{c_slate_dark}">1 &rarr; 0</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=10;{f_serif}",
        'x': tx(bx_start + 4*bx_w), 'y': ty(61.5, 2.2), 'w': tw(bx_w), 'h': th(2.2)
    })

    # Guidance arrow from Matrix W to KER
    connections.append({
        'id': 'f3_arr_w_ker',
        'style': f'edgeStyle=orthogonalEdgeStyle;curved=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.0;endArrow=block;endFill=1;',
        'sourcePoint': [tx(63.5), ty(53.0)],
        'targetPoint': [tx(69.0), ty(68.0)]
    })

    # Down arrow 2: (82.5, 59.5) -> (82.5, 55.5)
    connections.append({
        'id': 'f3_arr_kf_reeval',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_dark};strokeWidth=1.8;endArrow=block;endFill=1;',
        'sourcePoint': [tx(82.5), ty(59.5)],
        'targetPoint': [tx(82.5), ty(55.5)]
    })

    # Fitness Re-evaluation Title: (82.5, 53.5)
    elements.append({
        'id': 'f3_reeval_title',
        'value': f'<b><font color="{c_blue_navy}" size="2">Fitness Re-evaluation</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(70.0), 'y': ty(52.0, 3.0), 'w': tw(25.0), 'h': th(3.0)
    })

    # Down arrow 3 to Diamond: (82.5, 51.5) -> (82.5, 47.5)
    connections.append({
        'id': 'f3_arr_reeval_dec',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_dark};strokeWidth=1.8;endArrow=block;endFill=1;',
        'sourcePoint': [tx(82.5), ty(51.5)],
        'targetPoint': [tx(82.5), ty(47.5)]
    })

    # Decision Diamond (Enlarged): (82.5, 44.0, 13.0, 7.0)
    elements.append({
        'id': 'f3_decision_diamond',
        'value': f'<b><font color="{c_text_dark}">Improved?</font></b>',
        'style': f"rhombus;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_navy};strokeWidth=1.4;align=center;verticalAlign=middle;fontSize=11;{f_serif}",
        'x': tx(82.5 - 6.5), 'y': ty(40.5, 7.0), 'w': tw(13.0), 'h': th(7.0)
    })

    # Yes Branch: Left Down (Accept Refined)
    connections.append({
        'id': 'f3_arr_yes',
        'value': f'<b><font color="{c_blue_primary}" size="1">Yes<br>Accept Refined</font></b>',
        'style': f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=1.8;endArrow=block;endFill=1;align=right;{f_serif}",
        'sourcePoint': [tx(82.5 - 6.5), ty(44.0)],
        'targetPoint': [tx(80.0), ty(27.5)],
        'points': [(tx(73.5), ty(44.0)), (tx(73.5), ty(34.5))]
    })

    # No Branch: Right Down (Retain Original)
    connections.append({
        'id': 'f3_arr_no',
        'value': f'<b><font color="{c_slate_mid}" size="1">No<br>Retain Original</font></b>',
        'style': f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_slate_mid};strokeWidth=1.8;endArrow=block;endFill=1;align=left;{f_serif}",
        'sourcePoint': [tx(82.5 + 6.5), ty(44.0)],
        'targetPoint': [tx(85.0), ty(27.5)],
        'points': [(tx(91.5), ty(44.0)), (tx(91.5), ty(34.5))]
    })

    # Array 3: Elite Solution (After Selection) (y=19.5)
    elements.append({
        'id': 'f3_arr3_title',
        'value': f'<b><font color="{c_text_dark}" size="2">Elite Solution <b>x</b><sub><i>e</i></sub><sup>&starf;</sup> (After In-Place Selection)</font></b>',
        'style': f"text;html=1;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(68.0), 'y': ty(25.0, 3.0), 'w': tw(29.0), 'h': th(3.0)
    })
    bits_ea = [1, 1, 1, 0, 0, 0, 1, '...', 0, 1]
    for bi, b in enumerate(bits_ea):
        cur_bx = bx_start + bi * bx_w
        if b == '...':
            elements.append({
                'id': f'f3_ea_dots',
                'value': '&hellip;',
                'style': f"text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor={c_text_dark};{f_serif}",
                'x': tx(cur_bx), 'y': ty(19.5, bx_h), 'w': tw(bx_w), 'h': th(bx_h)
            })
        else:
            bg = '#DBEAFE' if bi == 0 else ('#F8FAFC' if bi == 4 else c_card_bg)
            bc = c_blue_primary if bi == 0 else (c_slate_dark if bi == 4 else c_border_neutral)
            bw = '1.3' if bi in [0, 4] else '0.9'
            elements.append({
                'id': f'f3_ea_{bi}',
                'value': str(b),
                'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={bg};strokeColor={bc};strokeWidth={bw};fontSize=11;align=center;verticalAlign=middle;{f_serif}",
                'x': tx(cur_bx), 'y': ty(19.5, bx_h), 'w': tw(bx_w), 'h': th(bx_h)
            })

    # -------------------------------------------------------------------------
    # STAGE 4: Bottom Spanning Container (2.0, 2.0, 96.0, 9.0)
    # -------------------------------------------------------------------------
    elements.append({
        'id': 'f3_bottom_box',
        'value': '',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_panel_bg};strokeColor={c_border_neutral};strokeWidth=1.2;{f_serif}",
        'x': tx(2.0), 'y': ty(2.0, 9.0), 'w': tw(96.0), 'h': th(9.0)
    })
    # Fully connected path: (82.5, 19.5) -> (82.5, 6.5) -> (16.7, 6.5) -> (16.7, 13.0)
    connections.append({
        'id': 'f3_arr_closed_loop',
        'style': f'edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeColor={c_blue_primary};strokeWidth=2.2;endArrow=block;endFill=1;',
        'sourcePoint': [tx(82.5), ty(19.5)],
        'targetPoint': [tx(16.7), ty(13.0)],
        'points': [(tx(82.5), ty(6.5)), (tx(16.7), ty(6.5))]
    })
    elements.append({
        'id': 'f3_bottom_badge',
        'value': f'<b><font color="{c_blue_navy}" size="2">Closed-Loop Evolutionary Knowledge Feedback Channel</font></b>',
        'style': f"rounded=1;whiteSpace=wrap;html=1;fillColor={c_card_bg};strokeColor={c_blue_border};strokeWidth=1.0;align=center;verticalAlign=middle;{f_serif}",
        'x': tx(28.0), 'y': ty(4.2, 4.6), 'w': tw(44.0), 'h': th(4.6)
    })

    create_drawio_xml(out_path, 'f3-ker-flow', 'Figure 3: KER Strategy', W_canvas, H_canvas, elements, connections)


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fig_dir = os.path.join(base_dir, 'output', 'figures')
    
    build_f1(os.path.join(fig_dir, 'F1_architecture_journal.drawio'))
    build_f2(os.path.join(fig_dir, 'F2_mi_initialization_journal.drawio'))
    build_f3(os.path.join(fig_dir, 'F3_ker_strategy_journal.drawio'))
    print("All Draw.io XML files successfully generated!")
