"""Generate Draw.io XML for Single-Column Figure 4 (Knowledge-Guided Elite Refinement).
Matches F4_ker_strategy_journal.pdf 100% in geometry, text, colors, and layout.
"""

import os
import xml.etree.ElementTree as ET

def generate_figure4_single_column_drawio():
    out_dir = r'e:\多目标优化\KDS-EL\output\figures'
    os.makedirs(out_dir, exist_ok=True)
    drawio_path = os.path.join(out_dir, 'F4_ker_strategy_journal.drawio')

    mxfile = ET.Element('mxfile', host="app.diagrams.net", modified="2026-09-03T11:20:00.000Z",
                        agent="Mozilla/5.0", version="21.0.0", type="device")
    diagram = ET.SubElement(mxfile, 'diagram', id="F4_Single_Column_KER", name="Page-1")
    model = ET.SubElement(diagram, 'mxGraphModel', dx="1000", dy="900", grid="1", gridSize="10",
                          guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                          pageScale="1", pageWidth="700", pageHeight="850", math="1", shadow="0")
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
            geo = ET.SubElement(c, 'mxGeometry', relative="1", as_="geometry")
        else:
            c.set('vertex', '1')
            geo = ET.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), as_="geometry")
        return cid

    # Outer dashed frame
    add_cell("", "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#CBD5E1;strokeWidth=1;dashed=1;",
             20, 20, 580, 780)

    # Geometry
    x0 = 110
    cw = 55
    ch = 40
    cols = 8

    # Feature headers
    feats = ["`f_1`", "`f_2`", "`f_3`", "`f_4`", "`f_5`", "`f_6`", "`\\dots`", "`f_D`"]
    y_feats = 45
    for c in range(cols):
        add_cell(feats[c], "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;fontFamily=Times New Roman;",
                 x0 + c*cw, y_feats, cw, 25)

    # Row 1: Elite x_e
    y_xe = 75
    add_cell("`\\mathbf{x}_e:`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;fontStyle=1;",
             x0 - 70, y_xe, 60, ch)
    xe_vals = [0, 0, 1, 0, 1, 0, "`\\dots`", 0]
    for c in range(cols):
        add_cell(str(xe_vals[c]),
                 "rounded=0;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#000000;strokeWidth=1;fontSize=12;fontFamily=Times New Roman;",
                 x0 + c*cw, y_xe, cw, ch)

    # Row 2: Memory W
    y_w = 125
    add_cell("`\\mathbf{W}:`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;fontStyle=1;",
             x0 - 70, y_w, 60, ch)
    w_vals = ["+0.4", "+3.8", "-2.1", "-0.1", "+4.2", "+0.1", "`\\dots`", "-0.0"]
    w_colors = {1: "#059669", 2: "#DC2626", 4: "#0284C7"}
    for c in range(cols):
        font_c = w_colors.get(c, "#000000")
        bld = "1" if c in [1, 2] else "0"
        add_cell(w_vals[c],
                 f"rounded=0;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;strokeWidth=1;dashed=1;fontSize=12;fontColor={font_c};fontFamily=Times New Roman;fontStyle={bld};",
                 x0 + c*cw, y_w, cw, ch)

    # Arrow to KER Box
    add_cell("", "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;",
             x0 + 4*cw, y_w + ch + 5, 0, 30)

    # KER Strategy Box
    y_strat = 195
    strat_w = cols * cw
    strat_h = 80
    add_cell("<b>Knowledge-Guided Elite Refinement (KER)</b><br><br>`\\text{Directional Score: } \\sigma_j = (1 - 2x_{e,j}) \\cdot W_j`",
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#BAE6FD;strokeColor=#000000;strokeWidth=1.2;fontSize=12;fontFamily=Times New Roman;",
             x0, y_strat, strat_w, strat_h)

    # Arrow to Score sigma
    add_cell("", "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;",
             x0 + 4*cw, y_strat + strat_h + 5, 0, 30)

    # Row 3: Score sigma
    y_sig = 305
    add_cell("`\\boldsymbol{\\sigma}:`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;fontStyle=1;",
             x0 - 70, y_sig, 60, ch)
    sig_vals = ["+0.4", "+3.8", "+2.1", "-0.1", "-4.2", "+0.1", "`\\dots`", "-0.0"]
    sig_bgs = {1: "#DCFCE7", 2: "#FEE2E2"}
    sig_colors = {1: "#059669", 2: "#DC2626", 4: "#64748B"}
    for c in range(cols):
        bg = sig_bgs.get(c, "#FFFFFF")
        font_c = sig_colors.get(c, "#000000")
        bld = "1" if c in [1, 2] else "0"
        add_cell(sig_vals[c],
                 f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg};strokeColor=#64748B;strokeWidth=1;dashed=1;fontSize=12;fontColor={font_c};fontFamily=Times New Roman;fontStyle={bld};",
                 x0 + c*cw, y_sig, cw, ch)

    # Staggered Tag Labels
    add_cell("<b>Directional Add (0 &rarr; 1)</b>",
             "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=11;fontColor=#059669;fontFamily=Times New Roman;",
             x0 + cw - 10, y_sig + ch + 5, cw + 60, 25)
    add_cell("<b>Directional Prune (1 &rarr; 0)</b>",
             "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=11;fontColor=#DC2626;fontFamily=Times New Roman;",
             x0 + 2*cw + 10, y_sig + ch + 28, cw + 60, 25)

    # Arrow to Mutant
    add_cell("", "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;",
             x0 + 4*cw, y_sig + ch + 5, 0, 50)

    # Row 4: Mutant x'_e
    y_mut = 425
    add_cell("`\\mathbf{x}'_e:`", "text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontSize=13;fontFamily=Times New Roman;fontStyle=1;",
             x0 - 70, y_mut, 60, ch)
    mut_vals = [0, 1, 0, 0, 1, 0, "`\\dots`", 0]
    mut_bgs = {1: "#DCFCE7", 2: "#FEE2E2"}
    mut_colors = {1: "#059669", 2: "#DC2626"}
    for c in range(cols):
        bg = mut_bgs.get(c, "#EEF2FF")
        font_c = mut_colors.get(c, "#000000")
        bld = "1" if c in [1, 2] else "0"
        add_cell(str(mut_vals[c]),
                 f"rounded=0;whiteSpace=wrap;html=1;fillColor={bg};strokeColor=#000000;strokeWidth=1;fontSize=12;fontColor={font_c};fontFamily=Times New Roman;fontStyle={bld};",
                 x0 + c*cw, y_mut, cw, ch)

    # Arrow Evaluate f(x)
    add_cell("Evaluate `f(\\mathbf{x})`",
             "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontFamily=Times New Roman;",
             x0 + 4*cw + 15, y_mut + ch + 20, 120, 25)
    add_cell("", "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;",
             x0 + 4*cw, y_mut + ch + 5, 0, 45)

    # Greedy Selection Boxes
    y_grd = 540
    box_w = (strat_w - 20) / 2
    grd_h = 90

    # Yes Outcome
    add_cell("<b>If `f(\\mathbf{x}'_e) < f(\\mathbf{x}_e)` (Improved)</b><br><br>`\\mathbf{x}_e^{\\star} \\leftarrow \\mathbf{x}'_e` (Accept mutant)",
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;strokeWidth=1.2;fontSize=11;fontColor=#166534;fontFamily=Times New Roman;",
             x0, y_grd, box_w, grd_h)

    # No Outcome
    add_cell("<b>Otherwise (Worse / Equal)</b><br><br>`\\mathbf{x}_e^{\\star} \\leftarrow \\mathbf{x}_e` (Preserve elite)",
             "rounded=0;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#94A3B8;strokeWidth=1.2;fontSize=11;fontColor=#475569;fontFamily=Times New Roman;",
             x0 + box_w + 20, y_grd, box_w, grd_h)

    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ", level=0)
    tree.write(drawio_path, encoding="utf-8", xml_declaration=True)
    print(f"SUCCESS: Generated Single-Column Draw.io at {drawio_path}")

if __name__ == '__main__':
    generate_figure4_single_column_drawio()
