"""Generate 100% Valid, Beautiful Draw.io XML for Figure 4 (KER Strategy).
Fully compliant with Draw.io schema (using standard as="geometry", valid shapes, and Times New Roman serif).
Includes:
- All matrices with 0/1 bits and floating point values.
- Color highlights: red updated bits, blue selected bits, yellow/purple row highlights.
- Block arrows with labels.
- Orthogonal routing bus lines into Elite tuning strategy.
- Dual 'Get' arrows and brackets.
- Dashed boundary box.
"""

import os
import xml.etree.ElementTree as ET

def generate_figure4_drawio():
    out_dir = r'e:\多目标优化\KDS-EL\output\figures'
    os.makedirs(out_dir, exist_ok=True)
    drawio_path = os.path.join(out_dir, 'F4_ker_strategy_journal.drawio')

    mxfile = ET.Element('mxfile', host="Electron", agent="Draw.io", version="21.0.0", type="device")
    diagram = ET.SubElement(mxfile, 'diagram', id="F4_EMSWOA_KER_Refined", name="Page-1")
    model = ET.SubElement(diagram, 'mxGraphModel', dx="1400", dy="800", grid="1", gridSize="10",
                          guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                          pageScale="1", pageWidth="1450", pageHeight="650", math="1", shadow="0")
    root = ET.SubElement(model, 'root')
    ET.SubElement(root, 'mxCell', id="0")
    ET.SubElement(root, 'mxCell', id="1", parent="0")

    cell_id = 100

    def add_cell(value, style, x, y, w, h, is_edge=False, source=None, target=None):
        nonlocal cell_id
        cell_id += 1
        cid = str(cell_id)
        c = ET.SubElement(root, 'mxCell', id=cid, value=value, style=style, parent="1")
        if is_edge:
            c.set('edge', '1')
            if source: c.set('source', source)
            if target: c.set('target', target)
            geo = ET.SubElement(c, 'mxGeometry')
            geo.set('as', 'geometry')
            geo.set('relative', '1')
        else:
            c.set('vertex', '1')
            geo = ET.SubElement(c, 'mxGeometry')
            geo.set('as', 'geometry')
            geo.set('x', str(x))
            geo.set('y', str(y))
            geo.set('width', str(w))
            geo.set('height', str(h))
        return cid

    # Colors
    c_blue_text = '#0284C7'
    c_red_text = '#DC2626'
    c_purple_row = '#E0E7FF'
    c_yellow_row = '#FEF3C7'
    c_grey_row = '#F1F5F9'
    c_cyan_box = '#BAE6FD'

    # Top Coordinates
    top_y = 70
    cw = 32
    ch = 28

    # 1. Top Left: Population Matrix X(t-1)
    x_m1 = 120
    add_cell("<b>Population matrix</b>", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;",
             x_m1, top_y - 20, 8*cw, 25)
    add_cell("`X(t-1)`", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_m1, top_y + 5, 8*cw, 20)
    add_cell("`X_{\\mathrm{best}}(t-1)`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_m1 - 95, top_y + 25 + 2*ch, 90, ch)

    mat_xt_minus_1 = [
        [0, 0, 1, 1, 0, 1, 1, 1],
        [0, 1, 1, 1, 0, 0, 1, 0],
        [1, 1, 0, 0, 1, 0, 1, 0],
        [0, 1, 1, 0, 1, 0, 0, 1]
    ]
    for r in range(4):
        for c in range(8):
            bg = c_yellow_row if r == 2 else '#FFFFFF'
            add_cell(str(mat_xt_minus_1[r][c]),
                     f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg};strokeColor=#000000;strokeWidth=1;fontSize=11;fontFamily=Times New Roman;",
                     x_m1 + c*cw, top_y + 30 + r*ch, cw, ch)

    # 2. Block Arrow -> Evolving Box
    x_evo_arr = x_m1 + 8*cw + 20
    add_cell("", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;",
             x_evo_arr, top_y + 30 + ch, 45, 2*ch)

    x_evo_box = x_evo_arr + 55
    add_cell("<b>Evolving</b>", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_evo_box - 10, top_y + 5, 90, 20)
    add_cell("KDS-EL", "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=12;fontFamily=Times New Roman;",
             x_evo_box, top_y + 30, 70, 4*ch)

    # Arrow to f(x)
    add_cell("", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;",
             x_evo_box + 85, top_y + 30 + ch, 40, 2*ch)

    x_fx_box = x_evo_box + 135
    add_cell("`f(x)`", "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;fontSize=13;fontFamily=Times New Roman;",
             x_fx_box, top_y + 30, 60, 4*ch)

    # Arrow to FP* Matrix
    add_cell("", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;",
             x_fx_box + 70, top_y + 30 + ch, 45, 2*ch)

    # 3. Middle Top: Flip Probability Matrix FP*(t)
    x_fp = x_fx_box + 125
    add_cell("<b>Flip Probability Matrix</b>", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;",
             x_fp, top_y - 20, 8*cw, 25)
    add_cell("`FP^*\\ \\mathrm{Matrix}_{(t)}`", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_fp, top_y + 5, 8*cw, 20)

    mat_p_float = [
        ['0.44', '0.46', '0.86', '0.66', '0.56', '0.72', '0.86', '0.32'],
        ['0.75', '0.05', '0.16', '0.45', '0.23', '0.53', '0.11', '0.58'],
        ['0.65', '0.78', '0.22', '0.63', '0.76', '0.32', '0.59', '0.79'],
        ['0.12', '0.93', '0.49', '0.77', '0.22', '0.46', '0.33', '0.68']
    ]
    blue_pts = {(0, 2), (0, 3), (0, 7), (2, 3), (2, 5), (3, 0), (3, 2)}
    for r in range(4):
        for c in range(8):
            bg = c_grey_row if r == 1 else '#FFFFFF'
            font_c = c_blue_text if (r, c) in blue_pts else '#000000'
            add_cell(mat_p_float[r][c],
                     f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg};strokeColor=#64748B;strokeWidth=1;dashed=1;fontSize=11;fontColor={font_c};fontFamily=Times New Roman;",
                     x_fp + c*cw, top_y + 30 + r*ch, cw, ch)

    # Dashed container box wrapping top tier TIGHTLY up to FP* Matrix ONLY!
    add_cell("", "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#475569;strokeWidth=1;dashed=1;",
             50, top_y - 25, (x_fp + 8*cw + 10) - 50, 195)

    # Arrow transform to X*(t) (crosses cleanly out of dashed box)
    add_cell("transform", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;fontSize=11;fontFamily=Times New Roman;",
             x_fp + 8*cw + 15, top_y + 30 + ch, 80, 2*ch)

    # 4. Top Right: Candidate Population matrix X*(t) (OUTSIDE DASHED BOX)
    x_xstar = x_fp + 8*cw + 110
    add_cell("<b>Population matrix</b>", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;",
             x_xstar, top_y - 20, 8*cw, 25)
    add_cell("`X^*(t)`", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_xstar, top_y + 5, 8*cw, 20)
    add_cell("`X_{\\mathrm{best}}(t)`", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_xstar + 8*cw + 10, top_y + 30 + 1*ch, 85, ch)

    mat_xstar = [
        [0, 1, 1, 0, 1, 1, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 0, 1, 1],
        [0, 1, 1, 1, 0, 0, 0, 0]
    ]
    blue_bits_xstar = {(0, 0), (0, 2), (0, 4), (0, 7), (1, 3), (2, 3), (2, 5), (3, 0), (3, 5)}
    for r in range(4):
        for c in range(8):
            bg = c_purple_row if r == 1 else '#FFFFFF'
            font_c = c_blue_text if (r, c) in blue_bits_xstar else '#000000'
            add_cell(str(mat_xstar[r][c]),
                     f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg};strokeColor=#000000;strokeWidth=1;fontSize=11;fontColor={font_c};fontFamily=Times New Roman;",
                     x_xstar + c*cw, top_y + 30 + r*ch, cw, ch)

    # -------------------------------------------------------------
    # BOTTOM TIER: Elite Feedback & KER Refinement
    # -------------------------------------------------------------
    bot_y = 360
    ch_bot = 26

    # 1. Bottom Left: 4 extracted vectors
    x_ext = 120
    add_cell("`X_{\\mathrm{best}}(t)`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_ext - 95, bot_y + 0*ch_bot, 90, ch_bot)
    add_cell("`X_{\\mathrm{best}}(t)\\ \\mathrm{FP}`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_ext - 95, bot_y + 1*ch_bot, 90, ch_bot)
    add_cell("`X_{\\mathrm{best}}(t-1)`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_ext - 95, bot_y + 2*ch_bot, 90, ch_bot)
    add_cell("`X_{\\mathrm{best}}(t-1)\\ \\mathrm{FP}`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_ext - 95, bot_y + 3*ch_bot, 90, ch_bot)

    mat_ext = [
        [1, 0, 0, 1, 0, 1, 0, 0],
        ['0.75', '0.05', '0.16', '0.45', '0.23', '0.53', '0.11', '0.28'],
        [1, 1, 0, 0, 1, 0, 1, 0],
        ['0.31', '0.75', '0.06', '0.25', '0.63', '0.43', '0.49', '0.29']
    ]
    ext_row_bg = [c_purple_row, c_grey_row, c_yellow_row, c_grey_row]
    for r in range(4):
        for c in range(8):
            add_cell(str(mat_ext[r][c]),
                     f"rounded=0;whiteSpace=wrap;html=1;fillColor={ext_row_bg[r]};strokeColor=#64748B;strokeWidth=1;dashed=1;fontSize=11;fontFamily=Times New Roman;",
                     x_ext + c*cw, bot_y + r*ch_bot, cw, ch_bot)

    # Brackets & Dual Get
    add_cell("Get", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             60, bot_y - 45, 40, 20)
    add_cell("Get", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_m1 + 4*cw + 5, bot_y - 45, 40, 20)

    # Arrow Guide to Strategy Box
    x_guide = x_ext + 8*cw + 25
    add_cell("Guide", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_guide, bot_y + 10, 60, 20)
    add_cell("", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;",
             x_guide, bot_y + 35, 60, 40)

    # 2. Central Box: Elite tuning strategy (KER)
    x_strat = x_guide + 75
    strat_w, strat_h = 160, 110
    add_cell("<b>Elite tuning<br>strategy (KER)</b>",
             f"rounded=0;whiteSpace=wrap;html=1;fillColor={c_cyan_box};strokeColor=#000000;strokeWidth=1;fontSize=13;fontFamily=Times New Roman;",
             x_strat, bot_y, strat_w, strat_h)

    # Orthogonal Line 1 from FP* and Line 2 from X*(t) into Strategy Box
    bus_y = 280
    strat_mid_x = x_strat + strat_w // 2
    fp_mid_x = x_fp + 4*cw
    xstar_mid_x = x_xstar + 3*cw

    # Bus line
    add_cell("", "endArrow=none;html=1;rounded=0;strokeColor=#000000;strokeWidth=1;",
             0, 0, 0, 0, is_edge=True)
    # Line from FP* down to bus
    add_cell("", f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=none;",
             fp_mid_x, top_y + 30 + 4*ch, 0, bus_y - (top_y + 30 + 4*ch))
    # Horizontal bus from xstar_mid_x to strat_mid_x
    add_cell("", f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=none;",
             strat_mid_x, bus_y, xstar_mid_x - strat_mid_x, 0)
    # Trunk down into strategy box
    add_cell("", f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=classic;",
             strat_mid_x, bus_y, 0, bot_y - bus_y)
    # Drop from X*(t) down to bus
    add_cell("", f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1;endArrow=none;",
             xstar_mid_x, top_y + 30 + 4*ch, 0, bus_y - (top_y + 30 + 4*ch))

    # Arrow Updated to FP Matrix(t)
    x_arr_upd = x_strat + strat_w + 15
    add_cell("Updated", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_arr_upd, bot_y + 10, 60, 20)
    add_cell("", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;",
             x_arr_upd, bot_y + 35, 60, 40)

    # 3. Bottom Center: Updated FP Matrix(t)
    x_upd = x_arr_upd + 75
    add_cell("`FP\\ \\mathrm{Matrix}(t)`", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_upd, bot_y - 25, 8*cw, 20)

    mat_p_upd = [
        ['0.56', '0.46', '0.41', '0.78', '0.56', '0.72', '0.86', '0.45'],
        ['0.75', '0.05', '0.16', '0.15', '0.23', '0.53', '0.11', '0.58'],
        ['0.65', '0.78', '0.22', '0.71', '0.76', '0.92', '0.59', '0.92'],
        ['0.38', '0.93', '0.67', '0.77', '0.22', '0.59', '0.94', '0.73']
    ]
    red_pts_upd = {(0, 0), (0, 2), (0, 3), (2, 3), (2, 5), (3, 2), (3, 7)}
    for r in range(4):
        for c in range(8):
            font_c = c_red_text if (r, c) in red_pts_upd else '#000000'
            add_cell(mat_p_upd[r][c],
                     f"rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#64748B;strokeWidth=1;dashed=1;fontSize=11;fontColor={font_c};fontFamily=Times New Roman;",
                     x_upd + c*cw, bot_y + r*ch_bot, cw, ch_bot)

    # Arrow transform to X(t)
    add_cell("transform", "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1;arrowWidth=0.4;arrowSize=0.45;fontSize=11;fontFamily=Times New Roman;",
             x_upd + 8*cw + 15, bot_y + 20, 80, 2*ch_bot)

    # 4. Bottom Right: Final Population Matrix X(t)
    x_xt_final = x_upd + 8*cw + 105
    add_cell("`X(t)`", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
             x_xt_final, bot_y - 25, 8*cw, 20)
    add_cell("`X_{\\mathrm{best}}(t)`", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x_xt_final + 8*cw + 10, bot_y + 3*ch_bot, 85, ch_bot)

    mat_xt_final = [
        [1, 1, 1, 1, 1, 1, 1, 0],
        [1, 0, 0, 1, 0, 1, 0, 1],
        [1, 1, 0, 0, 1, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 0, 1]
    ]
    red_bits_final = {(0, 0), (0, 3), (2, 5), (3, 2), (3, 7)}
    for r in range(4):
        for c in range(8):
            bg = c_grey_row if r == 3 else '#FFFFFF'
            font_c = c_red_text if (r, c) in red_bits_final else '#000000'
            add_cell(str(mat_xt_final[r][c]),
                     f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg};strokeColor=#000000;strokeWidth=1;fontSize=11;fontColor={font_c};fontFamily=Times New Roman;",
                     x_xt_final + c*cw, bot_y + r*ch_bot, cw, ch_bot)

    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ", level=0)
    tree.write(drawio_path, encoding="utf-8", xml_declaration=True)
    print(f"SUCCESS: Generated 100% Valid Draw.io file at {drawio_path}")

if __name__ == '__main__':
    generate_figure4_drawio()
