"""
Generate Zero-Crossing Draw.io XML for Figure 1:
Example of the feature selection process via KDS-EL.
- Title 'KDS-EL Optimization Engine' placed OUTSIDE on top of the big engine box
- Curly brace wraps ONLY Collaborative Dual-Swarm
- Arrow from brace to Transfer Function is a straight horizontal line
- Fitness feedback is a clean horizontal arrow into Memory W (135px below curly brace, 0 crossing!)
- Left loop is 100% planar with 'Adaptive Recovery'
- Out arrow exits through engine right border to Optimal Feature Subset
"""

import os
import base64
import zlib
import urllib.parse

def generate_figure1_drawio():
    xml_content = r'''<mxfile host="app.diagrams.net" modified="2026-09-03T10:15:00.000Z" agent="Mozilla/5.0" version="21.0.0" type="device">
  <diagram id="kdsel-f1-dataflow" name="Figure 1 Dataflow">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1350" pageHeight="720" math="1" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- ========================================== -->
        <!-- TOP BAND: INITIALIZATION & BINARIZATION     -->
        <!-- ========================================== -->

        <!-- 1. High-Dimensional Dataset -->
        <mxCell id="box_dataset" value="&lt;b&gt;High-Dimensional&lt;br&gt;Dataset&lt;/b&gt;&lt;br&gt;&lt;br&gt;`D \gg N_{\mathrm{samp}}`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#F8F9FA;strokeColor=#000000;strokeWidth=1.5;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="30" y="40" width="160" height="150" as="geometry" />
        </mxCell>

        <!-- Arrow: Dataset -> MI-Guided Initialization -->
        <mxCell id="arr_data_mi" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;" edge="1" parent="1" source="box_dataset" target="box_mi">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 2. MI-Guided Initialization -->
        <mxCell id="box_mi" value="&lt;b&gt;MI-Guided&lt;br&gt;Initialization&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="230" y="40" width="170" height="150" as="geometry" />
        </mxCell>

        <!-- Arrow: MI -> Continuous Population -->
        <mxCell id="arr_mi_cont" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;" edge="1" parent="1" source="box_mi" target="brace_pop">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 3. Continuous Population -->
        <mxCell id="title_pop" value="&lt;b&gt;Continuous Population&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="460" y="15" width="200" height="20" as="geometry" />
        </mxCell>

        <mxCell id="brace_pop" value="{" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=65;fontStyle=0" vertex="1" parent="1">
          <mxGeometry x="430" y="38" width="30" height="155" as="geometry" />
        </mxCell>

        <!-- Row 1: X_{i=1} -->
        <mxCell id="lbl_x1" value="`X_{i=1}`" style="text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="455" y="45" width="40" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_x1" value="`x_1`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="500" y="45" width="32" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_x2" value="`x_2`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="532" y="45" width="32" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_xdots" value="`\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="564" y="45" width="60" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_xt" value="`x_D`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="624" y="45" width="32" height="25" as="geometry" />
        </mxCell>

        <!-- Row 2: X_{i=2} (Highlighted Yellow) -->
        <mxCell id="lbl_x2" value="`X_{i=2}`" style="text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontFamily=Times New Roman;fontSize=12;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="455" y="85" width="40" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_x1" value="&lt;font style=&quot;font-size: 10px;&quot;&gt;`x_1`&lt;/font&gt;&lt;br&gt;&lt;b&gt;0.82&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="500" y="85" width="32" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_x2" value="&lt;font style=&quot;font-size: 10px;&quot;&gt;`x_2`&lt;/font&gt;&lt;br&gt;&lt;b&gt;0.15&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="532" y="85" width="32" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_xdots" value="`\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="564" y="85" width="60" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_xt" value="&lt;font style=&quot;font-size: 10px;&quot;&gt;`x_D`&lt;/font&gt;&lt;br&gt;&lt;b&gt;0.91&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="624" y="85" width="32" height="40" as="geometry" />
        </mxCell>

        <!-- Vertical dots -->
        <mxCell id="lbl_vdots_l" value="`\vdots`" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="465" y="130" width="30" height="20" as="geometry" />
        </mxCell>
        <mxCell id="lbl_vdots_c" value="`\vdots`" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="580" y="130" width="30" height="20" as="geometry" />
        </mxCell>

        <!-- Row N: X_{i=N} -->
        <mxCell id="lbl_xN" value="`X_{i=N}`" style="text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="455" y="155" width="40" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_x1" value="`x_1`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="500" y="155" width="32" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_x2" value="`x_2`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="532" y="155" width="32" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_xdots" value="`\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="564" y="155" width="60" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_xt" value="`x_D`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="624" y="155" width="32" height="25" as="geometry" />
        </mxCell>

        <!-- Arrow: Continuous Pop -> Binarization -->
        <mxCell id="arr_cont_bin" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;" edge="1" parent="1" source="c_r2_xt" target="box_bin">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 4. Explicit Binarization Box -->
        <mxCell id="box_bin" value="&lt;b&gt;Binarization&lt;/b&gt;&lt;br&gt;&lt;br&gt;`x_{i,j} = \mathbb{I}(p_{i,j} \ge \theta)`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="700" y="40" width="160" height="150" as="geometry" />
        </mxCell>

        <!-- Arrow: Binarization -> Binary Feature Subsets -->
        <mxCell id="arr_bin_sub" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;" edge="1" parent="1" source="box_bin" target="c_r2_r_x1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 5. Binary Feature Subsets -->
        <mxCell id="title_bin_pop" value="&lt;b&gt;Binary Feature Subsets&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="930" y="15" width="200" height="20" as="geometry" />
        </mxCell>

        <!-- Row 1: Subset 1 -->
        <mxCell id="lbl_sub1" value="Subset 1" style="text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="900" y="45" width="60" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_r_x1" value="`x_1`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="970" y="45" width="35" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_r_x2" value="`x_2`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="1005" y="45" width="35" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_r_xdots" value="`\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="1040" y="45" width="65" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_r1_r_xt" value="`x_D`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="1105" y="45" width="35" height="25" as="geometry" />
        </mxCell>

        <!-- Row 2: Subset 2 (Highlighted Yellow) -->
        <mxCell id="lbl_sub2" value="&lt;b&gt;Subset 2&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="900" y="85" width="60" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_r_x1" value="&lt;font style=&quot;font-size: 10px;&quot;&gt;`x_1`&lt;/font&gt;&lt;br&gt;&lt;b&gt;1&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="970" y="85" width="35" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_r_x2" value="&lt;font style=&quot;font-size: 10px;&quot;&gt;`x_2`&lt;/font&gt;&lt;br&gt;&lt;b&gt;0&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="1005" y="85" width="35" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_r_xdots" value="`\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="1040" y="85" width="65" height="40" as="geometry" />
        </mxCell>
        <mxCell id="c_r2_r_xt" value="&lt;font style=&quot;font-size: 10px;&quot;&gt;`x_D`&lt;/font&gt;&lt;br&gt;&lt;b&gt;1&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="1105" y="85" width="35" height="40" as="geometry" />
        </mxCell>

        <!-- Vertical dots -->
        <mxCell id="lbl_sub_vdots_l" value="`\vdots`" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="915" y="130" width="30" height="20" as="geometry" />
        </mxCell>
        <mxCell id="lbl_sub_vdots_c" value="`\vdots`" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="1055" y="130" width="30" height="20" as="geometry" />
        </mxCell>

        <!-- Row N: Subset N -->
        <mxCell id="lbl_subN" value="Subset N" style="text;html=1;strokeColor=none;fillColor=none;align=right;verticalAlign=middle;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="900" y="155" width="60" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_r_x1" value="`x_1`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="970" y="155" width="35" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_r_x2" value="`x_2`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="1005" y="155" width="35" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_r_xdots" value="`\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="1040" y="155" width="65" height="25" as="geometry" />
        </mxCell>
        <mxCell id="c_rN_r_xt" value="`x_D`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="1105" y="155" width="35" height="25" as="geometry" />
        </mxCell>

        <!-- ========================================== -->
        <!-- BOTTOM BAND: KDS-EL OPTIMIZATION ENGINE    -->
        <!-- ========================================== -->

        <!-- Main KDS-EL Container Box -->
        <mxCell id="box_kdsel" value="" style="rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#000000;strokeWidth=2;" vertex="1" parent="1">
          <mxGeometry x="30" y="240" width="940" height="440" as="geometry" />
        </mxCell>
        <!-- Title positioned OUTSIDE on top of the big engine box, exactly like EMSWOA -->
        <mxCell id="title_kdsel" value="&lt;b&gt;KDS-EL Optimization Engine&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=#FFFFFF;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=16;" vertex="1" parent="1">
          <mxGeometry x="400" y="225" width="300" height="30" as="geometry" />
        </mxCell>

        <!-- Input Arrow from Subset N horizontally ABOVE title at y=210, drops down to sub_dualswarm -->
        <mxCell id="arr_input" value="&lt;b&gt;Input&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=12;verticalAlign=bottom;" edge="1" parent="1" source="c_rN_r_xdots" target="sub_dualswarm">
          <mxGeometry x="-0.2" y="10" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1072" y="210" />
              <mxPoint x="280" y="210" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- 1. Collaborative Dual-Swarm Container -->
        <mxCell id="sub_dualswarm" value="&lt;b&gt;Collaborative Dual-Swarm Co-evolution&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;verticalAlign=top;" vertex="1" parent="1">
          <mxGeometry x="200" y="285" width="440" height="90" as="geometry" />
        </mxCell>
        <mxCell id="sub_p1" value="`\mathcal{P}_1`: Continuous Exploration" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="220" y="325" width="190" height="38" as="geometry" />
        </mxCell>
        <mxCell id="sub_p2" value="`\mathcal{P}_2`: Discrete Feature Sampling" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="430" y="325" width="190" height="38" as="geometry" />
        </mxCell>

        <!-- Arrow Dual Swarm -> TPS -->
        <mxCell id="arr_ds_tps" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;" edge="1" parent="1" source="sub_dualswarm" target="sub_tps">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 2. Two-Phase Weight Scheduling (TPS) -->
        <mxCell id="sub_tps" value="&lt;b&gt;Two-Phase Weight Scheduling&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="200" y="405" width="440" height="48" as="geometry" />
        </mxCell>

        <!-- Arrow TPS -> W -->
        <mxCell id="arr_tps_w" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;" edge="1" parent="1" source="sub_tps" target="sub_w">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 3. Feature-Importance Memory W -->
        <mxCell id="sub_w" value="&lt;b&gt;Feature-Importance Memory&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="200" y="485" width="440" height="48" as="geometry" />
        </mxCell>

        <!-- Arrow W -> KER (Knowledge Guidance) -->
        <mxCell id="arr_w_ker" value="&lt;b&gt;&lt;font color=&quot;#b25900&quot;&gt;Knowledge guidance&lt;/font&gt;&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=11;align=center;" edge="1" parent="1" source="sub_w" target="sub_ker">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- 4. Knowledge-Guided Elite Refinement (KER) -->
        <mxCell id="sub_ker" value="&lt;b&gt;Knowledge-Guided Elite Refinement&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="200" y="580" width="440" height="48" as="geometry" />
        </mxCell>

        <!-- ========================================== -->
        <!-- ZERO-CROSSING LEFT LOOP & ADAPTIVE RECOVERY-->
        <!-- ========================================== -->

        <!-- Exit from KER into generational decision node -->
        <mxCell id="arr_ker_stag" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endFill=1;" edge="1" parent="1" source="sub_ker" target="cond_stag">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="145" y="604" />
            </Array>
          </mxGeometry>
        </mxCell>

        <!-- Stagnation decision diamond -->
        <mxCell id="cond_stag" value="&lt;b&gt;Stagnation?&lt;/b&gt;" style="rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="100" y="505" width="90" height="55" as="geometry" />
        </mxCell>

        <!-- Branch 1: "No" -> Normal While(t < T) loop up to Dual-Swarm -->
        <mxCell id="arr_loop_no" value="&lt;b&gt;While(`t &lt; T`)&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.5;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=11;verticalAlign=bottom;" edge="1" parent="1" source="cond_stag" target="sub_dualswarm">
          <mxGeometry x="-0.4" y="-15" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="145" y="330" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- Branch 2: "Yes" -> Left into Adaptive Recovery -->
        <mxCell id="arr_stag_air" value="&lt;b&gt;Yes&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=11;" edge="1" parent="1" source="cond_stag" target="box_air">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <mxCell id="box_air" value="&lt;b&gt;Adaptive&lt;br&gt;Recovery&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=11;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="35" y="500" width="65" height="65" as="geometry" />
        </mxCell>

        <!-- Merge: Adaptive Recovery Re-inject cleanly joins the return bus at y=430 -->
        <mxCell id="arr_air_reinject" value="&lt;b&gt;Re-inject&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=10;" edge="1" parent="1" source="box_air" target="sub_dualswarm">
          <mxGeometry x="-0.7" y="-15" relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="68" y="430" />
              <mxPoint x="145" y="430" />
              <mxPoint x="145" y="330" />
            </Array>
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <!-- ========================================== -->
        <!-- RIGHT-INSIDE: EVALUATION & FITNESS BUS     -->
        <!-- Curly brace wraps ONLY sub_dualswarm (y=285..375) -->
        <!-- ========================================== -->
        <mxCell id="brace_eval" value="}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=85;fontStyle=0" vertex="1" parent="1">
          <mxGeometry x="645" y="285" width="30" height="90" as="geometry" />
        </mxCell>

        <!-- Straight horizontal arrow from brace to Transfer Function -->
        <mxCell id="arr_brace_tf" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endFill=1;" edge="1" parent="1" source="brace_eval" target="box_tf_eval">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Transfer Function Box -->
        <mxCell id="box_tf_eval" value="&lt;b&gt;Transfer Function&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="760" y="305" width="180" height="50" as="geometry" />
        </mxCell>

        <!-- Text in open space: Evaluating feature subset quality -->
        <mxCell id="lbl_eval_text" value="&lt;b&gt;Evaluating&lt;br&gt;feature subset&lt;br&gt;quality&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="670" y="380" width="85" height="55" as="geometry" />
        </mxCell>

        <!-- Fitness Function Container -->
        <mxCell id="box_fitness" value="&lt;b&gt;Fitness Function&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=12;verticalAlign=top;" vertex="1" parent="1">
          <mxGeometry x="760" y="380" width="180" height="260" as="geometry" />
        </mxCell>
        <mxCell id="arr_tf_fit" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endFill=1;" edge="1" parent="1" source="box_tf_eval" target="box_fitness">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Sub-box 1: Classification Error Rate -->
        <mxCell id="sub_err" value="&lt;b&gt;Classification Error Rate&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#F8F9FA;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="775" y="420" width="150" height="65" as="geometry" />
        </mxCell>

        <!-- Sub-box 2: Feature Subset Ratio -->
        <mxCell id="sub_num" value="&lt;b&gt;Feature Subset Ratio&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#F8F9FA;strokeColor=#000000;fontFamily=Times New Roman;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="775" y="515" width="150" height="65" as="geometry" />
        </mxCell>

        <!-- Feedback Arrow to W: 135px BELOW curly brace, 100% ZERO CROSSING! -->
        <mxCell id="arr_feedback" value="&lt;b&gt;Fitness feedback&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.2;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=11;align=center;" edge="1" parent="1" source="box_fitness" target="sub_w">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- ========================================== -->
        <!-- BOTTOM RIGHT: OUTPUT & OPTIMAL SUBSET      -->
        <!-- ========================================== -->

        <!-- Out Arrow exiting through engine border to Optimal Feature Subset -->
        <mxCell id="arr_out" value="&lt;b&gt;&lt;font style=&quot;font-size: 14px;&quot;&gt;Out&lt;/font&gt;&lt;/b&gt;" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1.8;endArrow=classic;endFill=1;fontFamily=Times New Roman;fontSize=14;verticalAlign=bottom;" edge="1" parent="1" source="box_fitness" target="c_opt_x1">
          <mxGeometry x="-0.1" y="10" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>

        <mxCell id="title_opt" value="&lt;b&gt;Optimal Feature Subset&lt;/b&gt;" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="1030" y="415" width="220" height="25" as="geometry" />
        </mxCell>

        <!-- Grid Cells for Optimal Subset -->
        <mxCell id="c_opt_x1" value="&lt;font style=&quot;font-size: 11px;&quot;&gt;`x_1`&lt;/font&gt;&lt;br&gt;&lt;b&gt;0&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="1040" y="445" width="45" height="55" as="geometry" />
        </mxCell>
        <mxCell id="c_opt_x2" value="&lt;font style=&quot;font-size: 11px;&quot;&gt;`x_2`&lt;/font&gt;&lt;br&gt;&lt;b&gt;0&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="1085" y="445" width="45" height="55" as="geometry" />
        </mxCell>
        <mxCell id="c_opt_xdots" value="`\dots\dots`" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="1130" y="445" width="80" height="55" as="geometry" />
        </mxCell>
        <mxCell id="c_opt_xt" value="&lt;font style=&quot;font-size: 11px;&quot;&gt;`x_D`&lt;/font&gt;&lt;br&gt;&lt;b&gt;1&lt;/b&gt;" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#000000;strokeWidth=1.2;fontFamily=Times New Roman;fontSize=13;" vertex="1" parent="1">
          <mxGeometry x="1210" y="445" width="45" height="55" as="geometry" />
        </mxCell>

        <!-- Compact Formula Notation Underneath -->
        <mxCell id="lbl_opt_formula" value="`d^{\star} = \|\mathbf{x}^{\star}\|_0 \ll D`" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=14;" vertex="1" parent="1">
          <mxGeometry x="1030" y="520" width="220" height="35" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

    base_dir = r"e:\多目标优化\KDS-EL"
    drawio_path = os.path.join(base_dir, 'output', 'figures', 'F1_dataflow_journal.drawio')
    os.makedirs(os.path.dirname(drawio_path), exist_ok=True)
    with open(drawio_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    compressed = zlib.compress(xml_content.encode('utf-8'))[2:-4]
    b64 = base64.b64encode(compressed).decode('utf-8')
    url = f"https://app.diagrams.net/#R{urllib.parse.quote(b64)}"

    print(f"Successfully generated Zero-Crossing F1 Draw.io XML at: {drawio_path}")
    print(f"Online Draw.io URL: {url}")
    return drawio_path, url

if __name__ == '__main__':
    generate_figure1_drawio()
