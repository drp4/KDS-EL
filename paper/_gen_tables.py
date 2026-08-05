# -*- coding: utf-8 -*-
"""Regenerate all KDS-EL paper tables from authoritative 20-DS sources.
Sources: output/tables/*.csv (accuracy/features/wilcoxon/holm/ablation) and
output/实验数据汇总.md (runtime, parameter sensitivity).
Outputs: output/tables/*.tex with labels matching paper \ref (T4..T8, T-A4..T-A6).
"""
import csv, math, os

TAB = r"E:\多目标优化\KDS-EL\output\tables"
MD = r"E:\多目标优化\KDS-EL\output\实验数据汇总.md"

METHODS_14 = ["KDS-EL","KDS-EL w/o TPS","KDS-EL w/o TPS\\&KER","MEL","FWPSO","PSO-CSM","SaWDE","IGPSO",
              "BPSO","W-MOPSO-FS","fMOPSO-FS","NSGA-II-FS","MOEA-D-FS","MOPSO-FS"]
# CSV header names for the 14 methods
CSV_METHODS = ["KDS_EL","KDS_EL_KER","MEL+MI","MEL","FWPSO","PSO-CSM","SaWDE","IGPSO",
               "BPSO","W-MOPSO-FS","fMOPSO-FS","NSGA-II-FS","MOEA-D-FS","MOPSO-FS"]

def read_csv(path):
    with open(os.path.join(TAB, path), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def read_csv_matrix(path):
    with open(os.path.join(TAB, path), encoding="utf-8-sig") as f:
        return list(csv.reader(f))

def tex_join(out):
    return "\n".join(out) + "\n"

def header14():
    return " & ".join(["Dataset"] + METHODS_14)

def p_tex(p):
    pv = float(p)
    if pv == 0.0:
        return "$<10^{-15}$"
    expo = int(math.floor(math.log10(pv)))
    mant = pv / (10.0 ** expo)
    return "$%.2f\\times 10^{%d}$" % (mant, expo)

# ---------- T4 accuracy ----------
def gen_T4():
    rows = read_csv("T4_accuracy.csv")
    out = [r"\begin{sidewaystable}", r"\centering",
           r"\caption{Classification accuracy (mean $\pm$ std) of 14 fixed-length methods on 20 benchmark datasets. Bold indicates the best per dataset; the Average row reports the mean across the 20 datasets.}",
           r"\label{T4}", r"\tiny",
           r"\setlength{\tabcolsep}{2pt}",
           r"\resizebox{\dimexpr\textheight-2cm}{!}{%",
           r"\begin{tabular}{l" + "c"*14 + "}", r"\toprule",
           header14() + r" \\", r"\midrule"]
    all_vals = []
    for r in rows:
        ds = r["Dataset"].replace("_", "\\_")
        vals = []
        best = max(float(r[m].split("±")[0]) for m in CSV_METHODS)
        for m in CSV_METHODS:
            v = r[m].strip()
            num = float(v.split("±")[0])
            v = v.replace("±", "$\\pm$")
            if abs(num - best) < 1e-9:
                v = "\\textbf{" + v + "}"
            vals.append(v)
        all_vals.append([float(r[m].split("±")[0]) for m in CSV_METHODS])
        out.append(ds + " & " + " & ".join(vals) + r" \\")
    avgs = [sum(col) / len(col) for col in zip(*all_vals)]
    best_avg = max(avgs)
    avg_cells = ["\\textbf{%.4f}" % a if abs(a - best_avg) < 1e-9 else "%.4f" % a for a in avgs]
    out += [r"\midrule", "Average & " + " & ".join(avg_cells) + r" \\",
            r"\bottomrule", r"\end{tabular}}", r"\end{sidewaystable}"]
    with open(os.path.join(TAB, "T4_accuracy.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T4_accuracy.tex written (%d datasets)" % len(rows))

# ---------- T5 features ----------
def gen_T5():
    rows = read_csv("T5_features.csv")
    out = [r"\begin{sidewaystable}", r"\centering",
           r"\caption{Average number of selected features (over 10 runs) of 14 methods on 20 datasets. Bold indicates the minimum per dataset.}",
           r"\label{T5}", r"\scriptsize",
           r"\setlength{\tabcolsep}{3pt}",
           r"\resizebox{\dimexpr\textheight-2cm}{!}{%",
           r"\begin{tabular}{l" + "c"*14 + "}", r"\toprule",
           header14() + r" \\", r"\midrule"]
    for r in rows:
        ds = r["Dataset"].replace("_", "\\_")
        vals = []
        best = min(int(r[m].split()[0]) for m in CSV_METHODS)
        for m in CSV_METHODS:
            v = int(r[m].split()[0])
            vals.append("\\textbf{%d}" % v if v == best else "%d" % v)
        out.append(ds + " & " + " & ".join(vals) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}}", r"\end{sidewaystable}"]
    with open(os.path.join(TAB, "T5_features.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T5_features.tex written (%d datasets)" % len(rows))

# ---------- T6 Wilcoxon matrix ----------
def gen_T6():
    mat = read_csv_matrix("T6_wilcoxon.csv")
    out = [r"\begin{sidewaystable}", r"\centering",
           r"\caption{One-sided Wilcoxon signed-rank test results ($p<0.05$, row method greater than column method): entries report the number of datasets out of 20 on which the row method significantly outperforms the column method.}",
           r"\label{T6}", r"\scriptsize",
           r"\setlength{\tabcolsep}{3pt}",
           r"\resizebox{\dimexpr\textheight-2cm}{!}{%",
           r"\begin{tabular}{l" + "c"*14 + "}", r"\toprule",
           " & ".join(["Method"] + METHODS_14) + r" \\", r"\midrule"]
    for row in mat[1:]:
        name = row[0]
        cells = row[1:]
        disp = []
        for i, c in enumerate(cells):
            c = c.strip()
            if c == "—":
                disp.append("---")
            elif i == 0:
                disp.append("\\textbf{" + c + "}")
            else:
                disp.append(c)
        disp_name = name.replace("KDS_EL_KER", "KDS-EL w/o TPS").replace("MEL+MI", "KDS-EL w/o TPS\\&KER").replace("_", "\\_")
        out.append(disp_name + " & " + " & ".join(disp) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}}", r"\end{sidewaystable}"]
    with open(os.path.join(TAB, "T6_wilcoxon.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T6_wilcoxon.tex written (%d methods)" % (len(mat)-1))

# ---------- T6b Holm (drop W/T/L, keep dAcc + adjusted p + reject) ----------
def gen_T6b():
    rows = read_csv("T6b_holm_bonferroni.csv")
    rows.sort(key=lambda r: float(r["Holm_alpha"]))
    out = [r"\begin{table}[!htb]", r"\centering",
           r"\caption{Holm--Bonferroni corrected pairwise comparison between KDS-EL and each of the 13 comparison methods over the 20 datasets. $\Delta$Acc is the mean accuracy advantage of KDS-EL; Combined $p$ is the unadjusted Fisher combined one-sided Wilcoxon $p$-value and Holm $p$ is its Holm--Bonferroni adjustment; $H_0$ of no superiority is rejected at the Holm threshold in every case.}",
           r"\label{T6b}", r"\footnotesize",
           r"\setlength{\tabcolsep}{3pt}",
           r"\begin{tabular}{lcccc}", r"\toprule",
           r"Method & $\Delta$Acc & Combined $p$ & Holm $p$ & Reject $H_0$ \\", r"\midrule"]
    for r in rows:
        m = r["Method"].replace("KDS_EL_KER", "KDS-EL w/o TPS").replace("MEL+MI", "KDS-EL w/o TPS\\&KER")
        d = float(r["Mean_ΔAcc"])
        rej = "\\checkmark" if r["Reject_H0"].strip().lower().startswith("y") else "---"
        out.append(m + f" & $+{d:.4f}$ & " + p_tex(r["Combined_p"]) + " & " + p_tex(r["Adjusted_p"]) + " & " + rej + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    with open(os.path.join(TAB, "T6b_holm_bonferroni.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T6b_holm_bonferroni.tex written (%d methods)" % len(rows))

# ---------- T7 ablation summary (4 variants: Acc, Feat, dAcc) ----------
def gen_T7():
    data = [("KDS-EL", 0.9574, 87.8, "--"),
            ("KDS-EL w/o TPS", 0.9488, 122, "-0.86"),
            ("KDS-EL w/o TPS\\&KER", 0.9325, 291, "-1.63"),
            ("MEL", 0.8868, 2722, "-4.58")]
    out = [r"\begin{table}[htbp]", r"\centering",
           r"\caption{Component contribution analysis: each row strips one mechanism from the complete KDS-EL, and $\Delta$Acc reports the resulting accuracy loss relative to the row above. ``MEL'' denotes the framework stripped of all three mechanisms---the residual that remains once every component has been removed, corresponding to MEL~\cite{mel2024}. Feature counts are dataset means.}",
           r"\label{T7}", r"\small",
           r"\begin{tabular}{lccc}", r"\toprule",
           r"Variant & Accuracy & Features & $\Delta$Acc (pp) \\", r"\midrule"]
    for name, acc, feat, d in data:
        bold = name == "KDS-EL"
        if bold:
            row = (name + r" & \textbf{" + f"{acc:.4f}" + r"} & \textbf{"
                   + str(feat) + r"} & " + d + r" \\")
        else:
            row = name + f" & {acc:.4f} & {feat} & {d}" + r" \\"
        out.append(row)
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    with open(os.path.join(TAB, "T7_ablation.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T7_ablation.tex written (summary)")

# ---------- T8 parameter sensitivity summary (from 11.6) ----------
def gen_T8():
    rows = [
        ("Weight decay", "0.90--1.00", "0.99", "[0.95, 0.995]", "$\\pm$1.2"),
        ("Phase split", "0.3--0.9", "0.70", "[0.60, 0.80]", "$\\pm$0.7"),
        ("Flip fraction", "0.005--0.10", "0.01", "[0.005, 0.02]", "$\\pm$1.3"),
        ("MI init ratio", "0.0--1.0", "0.50", "[0.25, 0.75]", "$\\pm$1.2"),
        ("Elite count", "1--10", "3", "[2, 5]", "$\\pm$0.9"),
    ]
    out = [r"\begin{table}[htbp]", r"\centering",
           r"\caption{One-factor-at-a-time parameter sensitivity analysis over four representative datasets (Adenoma, Colon, ALL4, BASEHOCK). The maximum accuracy deviation from the default configuration never exceeds $\pm$1.5~pp.}",
           r"\label{T8}", r"\small",
           r"\begin{tabular}{lcccc}", r"\toprule",
           r"Parameter & Tested range & Optimal & Stable range & Max $\Delta$Acc (pp) \\", r"\midrule"]
    for r in rows:
        out.append(" & ".join(r) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    with open(os.path.join(TAB, "T8_parameter_sensitivity.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T8_parameter_sensitivity.tex written")

# ---------- T-A4 per-dataset ablation (Acc+Feat, 4 variants) ----------
def gen_TA4():
    rows = read_csv("T7_ablation.csv")
    cols = [("MEL_Acc","MEL_Feat"), ("MEL+MI_Acc","MEL+MI_Feat"),
            ("KDS_EL_KER_Acc","KDS_EL_KER_Feat"), ("KDS_EL_Acc","KDS_EL_Feat")]
    out = [r"\begin{table}[htbp]", r"\centering",
           r"\caption{Per-dataset ablation results over the 20-dataset suite: accuracy and mean feature count for each variant of the incremental construction.}",
           r"\label{T-A4}", r"\small",
           r"\begin{tabular}{l" + "cc"*4 + "}", r"\toprule",
           r"Dataset & \multicolumn{2}{c}{MEL} & \multicolumn{2}{c}{MEL+MI} & \multicolumn{2}{c}{KDS-EL$_{\text{KER}}$} & \multicolumn{2}{c}{KDS-EL} \\"
           + r"\midrule",
           r" & Acc & Feat & Acc & Feat & Acc & Feat & Acc & Feat \\", r"\midrule"]
    for r in rows:
        cells = []
        for a, ft in cols:
            cells.append(r[a].replace("±", "$\\pm$") + " & " + r[ft])
        out.append(r["Dataset"] + " & " + " & ".join(cells) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    with open(os.path.join(TAB, "T-A4_per_dataset_ablation.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T-A4_per_dataset_ablation.tex written (%d datasets)" % len(rows))

def read_md_table(txt, heading):
    """Return the first contiguous pipe-table block after a heading line."""
    idx = txt.find(heading)
    if idx < 0:
        raise RuntimeError("heading not found: %s" % heading)
    body = txt[idx + len(heading):].split("\n")
    lines = []
    for l in body:
        l = l.strip()
        if l.startswith("|"):
            lines.append(l)
        elif lines:
            break
    if not lines:
        raise RuntimeError("no table under heading: %s" % heading)
    return lines

# ---------- T-A5 per-dataset runtime (20 x 14) ----------
def gen_TA5():
    txt = open(MD, encoding="utf-8").read()
    lines = read_md_table(txt, "### 10.2")
    data = []
    for l in lines[2:]:
        cells = [c.strip() for c in l.strip("|").split("|")]
        if cells[0] == "**Average**":
            continue
        data.append(cells)
    rt_names = ["KDS-EL","KDS-EL$_{\\text{KER}}$","MEL+MI","MEL","FWPSO","PSO-CSM","SaWDE","IGPSO",
                "BPSO","W-MOPSO","fMOPSO","NSGA-II","MOEA-D","MOPSO"]
    out = [r"\begin{table}[htbp]", r"\centering",
           r"\caption{Per-dataset wall-clock runtime in seconds (mean over 10 runs) for the 14 methods on 20 datasets.}",
           r"\label{T-A5}", r"\small",
           r"\begin{tabular}{l" + "c"*14 + "}", r"\toprule",
           " & ".join(["Dataset"] + rt_names) + r" \\", r"\midrule"]
    for row in data:
        out.append(row[0] + " & " + " & ".join(row[1:]) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    with open(os.path.join(TAB, "T-A5_runtime.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T-A5_runtime.tex written (%d datasets)" % len(data))

# ---------- T-A6 parameter detail (5 mini tables) ----------
def gen_TA6():
    txt = open(MD, encoding="utf-8").read()
    sections = {"11.1":"WeightDecay","11.2":"PhaseSplit","11.3":"flip\\_frac","11.4":"MI\\_init\\_ratio","11.5":"elite\\_k"}
    out = [r"\begin{table}[htbp]", r"\centering",
           r"\caption{Full parameter sensitivity results (mean accuracy, feature count, and runtime over the four datasets) for each of the five parameters. Bold rows indicate the default configuration.}",
           r"\label{T-A6}", r"\small",
           r"\begin{tabular}{lccc}", r"\toprule",
           r"Value & Avg Acc & Avg Feat & Avg Time (s) \\", r"\midrule"]
    for num, title in sections.items():
        lines = read_md_table(txt, "### " + num)
        rows = lines[2:]
        out.append(r"\multicolumn{4}{l}{\emph{" + title + "}} \\")
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            line = cells[0]
            if line.startswith("**"):
                line = "\\textbf{" + line.replace("**", "") + "}"
                rest = " & ".join("\\textbf{%s}" % c.replace("**","") for c in cells[1:])
                out.append(line + " & " + rest + r" \\")
            else:
                out.append(cells[0] + " & " + " & ".join(cells[1:]) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    with open(os.path.join(TAB, "T-A6_parameter_sensitivity_full.tex"), "w", encoding="utf-8") as f:
        f.write(tex_join(out))
    print("T-A6_parameter_sensitivity_full.tex written")

if __name__ == "__main__":
    gen_T4(); gen_T5(); gen_T6(); gen_T6b(); gen_T7(); gen_T8()
    gen_TA4(); gen_TA5(); gen_TA6()
