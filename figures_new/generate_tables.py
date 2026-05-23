import pandas as pd, numpy as np
from scipy import stats

df = pd.read_csv("all_data1.csv")
df = df[df["Dataset"] != "ALL3"].copy()

DATASETS = ["Adenoma","ALL_AML","ALL4","CNS","Colon","DLBCL","Leukaemia","Lymphoma","Stroke"]
DS_LABELS = ["Adenoma","ALL-AML","ALL4","CNS","Colon","DLBCL","Leukaemia","Lymphoma","Stroke"]
ALL_V  = ["MEL_KGEF","MEL_NHD","MEL_KGEF_noNHD","MEL","FWPSO","PSO_CSM","IGPSO","SaWDE","BPSO"]
ABL_V  = ["MEL_KGEF","MEL_NHD","MEL_KGEF_noNHD","MEL"]

V_LABELS = {
    "BPSO":"BPSO","SaWDE":"SaWDE","FWPSO":"FWPSO","MEL":"MEL",
    "MEL_NHD":"KDS-EL/DRS","MEL_KGEF_noNHD":"KDS-EL/KER",
    "MEL_KGEF":"KDS-EL","PSO_CSM":"PSO-CSM","IGPSO":"IGPSO",
}

def g(v,ds,m="Accuracy"): return df[(df.Version==v)&(df.Dataset==ds)][m].values

OUT = "tables_final.tex"
lines = []

def emit(s=""): lines.append(s)

# ════════════════════════════════════════════════════════════
# Helper: find best and second-best per row
# ════════════════════════════════════════════════════════════
def rank_vals(vals):
    """Return (best_idx, second_idx) by descending value."""
    order = np.argsort(vals)[::-1]
    return order[0], order[1]

def rank_vals_asc(vals):
    """For features: best=smallest, second=second-smallest."""
    order = np.argsort(vals)
    return order[0], order[1]

# ════════════════════════════════════════════════════════════
# Table 4 — Classification Accuracy
# ════════════════════════════════════════════════════════════
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"% Table 4: Classification Accuracy (mean ± std)")
emit(r"% Bold = best, underline = second-best per dataset")
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"\begin{table*}[t]")
emit(r"\centering")
emit(r"\caption{Comparison of mean classification accuracy (\%) and standard deviation.")
emit(r"Bold values indicate the best result; underlined values indicate the second-best.}")
emit(r"\label{tab:accuracy}")
emit(r"\setlength{\tabcolsep}{3.5pt}")
# columns: Dataset + 9 methods
col_spec = "l" + "c"*len(ALL_V)
emit(r"\begin{tabular}{" + col_spec + r"}")
emit(r"\toprule")
header = r"\textbf{Dataset} & " + " & ".join(
    r"\textbf{" + V_LABELS[v] + r"}" for v in ALL_V) + r" \\"
emit(header)
emit(r"\midrule")

for ds, dslbl in zip(DATASETS, DS_LABELS):
    means = np.array([g(v,ds).mean() for v in ALL_V])
    stds  = np.array([g(v,ds).std()  for v in ALL_V])
    best, second = rank_vals(means)
    cells = []
    for i,(m,s) in enumerate(zip(means,stds)):
        cell = f"{m*100:.2f}$\\pm${s*100:.2f}"
        if i == best:
            cell = r"\textbf{" + cell + r"}"
        elif i == second:
            cell = r"\underline{" + cell + r"}"
        cells.append(cell)
    row = dslbl + " & " + " & ".join(cells) + r" \\"
    emit(row)

emit(r"\midrule")
# Average row
avg_means = np.array([np.mean([g(v,ds).mean() for ds in DATASETS]) for v in ALL_V])
best_avg, second_avg = rank_vals(avg_means)
avg_cells = []
for i, m in enumerate(avg_means):
    cell = f"{m*100:.2f}"
    if i == best_avg: cell = r"\textbf{" + cell + r"}"
    elif i == second_avg: cell = r"\underline{" + cell + r"}"
    avg_cells.append(cell)
emit(r"\textbf{Average} & " + " & ".join(avg_cells) + r" \\")

# Friedman rank row
ranks = {v:[] for v in ALL_V}
for ds in DATASETS:
    ms = {v: g(v,ds).mean() for v in ALL_V}
    for r,v in enumerate(sorted(ms,key=ms.get,reverse=True),1): ranks[v].append(r)
avg_ranks = [np.mean(ranks[v]) for v in ALL_V]
best_r, second_r = rank_vals_asc(avg_ranks)
rank_cells = []
for i,r in enumerate(avg_ranks):
    cell = f"{r:.3f}"
    if i==best_r: cell=r"\textbf{"+cell+r"}"
    elif i==second_r: cell=r"\underline{"+cell+r"}"
    rank_cells.append(cell)
matrix = np.array([[g(v,ds).mean() for v in ALL_V] for ds in DATASETS])
chi2,p = stats.friedmanchisquare(*[matrix[:,i] for i in range(len(ALL_V))])
emit(r"\textbf{Avg. Rank} & " + " & ".join(rank_cells) + r" \\")
emit(r"\midrule")
emit(r"\multicolumn{" + str(len(ALL_V)+1) + r"}{l}{"
     r"Friedman test: $\chi^2=" + f"{chi2:.2f}" + r"$, $p=" + f"{p:.2e}" + r"$} \\")
emit(r"\bottomrule")
emit(r"\end{tabular}")
emit(r"\end{table*}")
emit()

# ════════════════════════════════════════════════════════════
# Table 5 — Number of Selected Features
# ════════════════════════════════════════════════════════════
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"% Table 5: Number of Selected Features (mean)")
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"\begin{table*}[t]")
emit(r"\centering")
emit(r"\caption{Comparison of the mean number of selected features.")
emit(r"Bold values indicate the fewest features; underlined values indicate the second-fewest.}")
emit(r"\label{tab:features}")
emit(r"\setlength{\tabcolsep}{3.5pt}")
emit(r"\begin{tabular}{" + col_spec + r"}")
emit(r"\toprule")
emit(header)
emit(r"\midrule")
for ds, dslbl in zip(DATASETS, DS_LABELS):
    means = np.array([g(v,ds,"Num_Features").mean() for v in ALL_V])
    best, second = rank_vals_asc(means)
    cells = []
    for i,m in enumerate(means):
        cell = f"{int(round(m)):,}"
        if i==best: cell=r"\textbf{"+cell+r"}"
        elif i==second: cell=r"\underline{"+cell+r"}"
        cells.append(cell)
    emit(dslbl + " & " + " & ".join(cells) + r" \\")
emit(r"\midrule")
avg_feat = np.array([np.mean([g(v,ds,"Num_Features").mean() for ds in DATASETS]) for v in ALL_V])
best_f, second_f = rank_vals_asc(avg_feat)
avg_fcells = []
for i,m in enumerate(avg_feat):
    cell=f"{int(round(m)):,}"
    if i==best_f: cell=r"\textbf{"+cell+r"}"
    elif i==second_f: cell=r"\underline{"+cell+r"}"
    avg_fcells.append(cell)
emit(r"\textbf{Average} & " + " & ".join(avg_fcells) + r" \\")
emit(r"\bottomrule")
emit(r"\end{tabular}")
emit(r"\end{table*}")
emit()

# ════════════════════════════════════════════════════════════
# Table 6 — Wilcoxon p-values
# ════════════════════════════════════════════════════════════
COMP_V  = ["MEL","MEL_NHD","MEL_KGEF_noNHD","FWPSO","PSO_CSM","IGPSO","SaWDE","BPSO"]
COMP_LB = ["MEL","KDS-EL/DRS","KDS-EL/KER","FWPSO","PSO-CSM","IGPSO","SaWDE","BPSO"]
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"% Table 6: Wilcoxon Signed-Rank Test p-values")
emit(r"% Bold = p > 0.05 (not significant); underline = 0.01 < p ≤ 0.05")
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"\begin{table*}[t]")
emit(r"\centering")
emit(r"\caption{$p$-values of the Wilcoxon signed-rank test between KDS-EL and each competitor.")
emit(r"Bold values denote $p>0.05$ (not significant); underlined values denote $0.01<p\leq0.05$.}")
emit(r"\label{tab:wilcoxon}")
emit(r"\setlength{\tabcolsep}{4pt}")
w_col = "l" + "c"*len(COMP_V)
emit(r"\begin{tabular}{" + w_col + r"}")
emit(r"\toprule")
emit(r"\textbf{Dataset} & " + " & ".join(
    r"\textbf{" + l + r"}" for l in COMP_LB) + r" \\")
emit(r"\midrule")
for ds, dslbl in zip(DATASETS, DS_LABELS):
    a = g("MEL_KGEF",ds)
    cells = []
    for v in COMP_V:
        b=g(v,ds); n=min(len(a),len(b))
        try: _,pv=stats.wilcoxon(a[:n],b[:n])
        except: pv=1.0
        if pv<0.001: cell=f"{pv:.2e}"
        elif pv<0.01: cell=f"{pv:.4f}"
        else: cell=f"{pv:.4f}"
        if pv>0.05: cell=r"\textbf{"+cell+r"}"
        elif pv<=0.05 and pv>0.01: cell=r"\underline{"+cell+r"}"
        cells.append(cell)
    emit(dslbl + " & " + " & ".join(cells) + r" \\")
emit(r"\bottomrule")
emit(r"\end{tabular}")
emit(r"\end{table*}")
emit()

# ════════════════════════════════════════════════════════════
# Table 7 — Ablation Study
# ════════════════════════════════════════════════════════════
ABL_LB_SHORT = ["MEL","KDS-EL/DRS","KDS-EL/KER","KDS-EL"]
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"% Table 7: Ablation Study")
emit(r"% ─────────────────────────────────────────────────────────────")
emit(r"\begin{table*}[t]")
emit(r"\centering")
emit(r"\caption{Ablation study results. For each dataset, accuracy (mean\,$\pm$\,std, \%) and")
emit(r"number of selected features (mean) are reported for four variants.")
emit(r"Bold = best accuracy; $\dagger$ = best feature count per dataset.}")
emit(r"\label{tab:ablation}")
emit(r"\setlength{\tabcolsep}{4pt}")
# 4 variants × 2 metrics = 8 columns + dataset
abl_header_top = (r"\textbf{Dataset} & "
    r"\multicolumn{2}{c}{\textbf{KDS-EL}} & "
    r"\multicolumn{2}{c}{\textbf{KDS-EL/DRS}} & "
    r"\multicolumn{2}{c}{\textbf{KDS-EL/KER}} & "
    r"\multicolumn{2}{c}{\textbf{MEL}} \\")
abl_header_sub = (r" & Acc. & Feat. "
    r"& Acc. & Feat. "
    r"& Acc. & Feat. "
    r"& Acc. & Feat. \\")
emit(r"\begin{tabular}{lcccccccc}")
emit(r"\toprule")
emit(abl_header_top)
emit(r"\cmidrule(r){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(l){8-9}")
emit(abl_header_sub)
emit(r"\midrule")
for ds, dslbl in zip(DATASETS, DS_LABELS):
    acc_vals  = [g(v,ds).mean()*100         for v in ABL_V]
    feat_vals = [g(v,ds,"Num_Features").mean() for v in ABL_V]
    acc_stds  = [g(v,ds).std()*100           for v in ABL_V]
    best_acc  = np.argmax(acc_vals)
    best_feat = np.argmin(feat_vals)
    cells = []
    for i,(acc,std,feat) in enumerate(zip(acc_vals,acc_stds,feat_vals)):
        a_cell = f"{acc:.2f}$\\pm${std:.2f}"
        f_cell = f"{int(round(feat)):,}"
        if i==best_acc:  a_cell = r"\textbf{"+a_cell+r"}"
        if i==best_feat: f_cell = f_cell+r"$^\dagger$"
        cells += [a_cell, f_cell]
    emit(dslbl + " & " + " & ".join(cells) + r" \\")
emit(r"\midrule")
# Average row
avg_acc  = [np.mean([g(v,ds).mean()*100         for ds in DATASETS]) for v in ABL_V]
avg_feat = [np.mean([g(v,ds,"Num_Features").mean() for ds in DATASETS]) for v in ABL_V]
best_acc_avg  = np.argmax(avg_acc)
best_feat_avg = np.argmin(avg_feat)
avg_cells = []
for i,(a,f) in enumerate(zip(avg_acc,avg_feat)):
    a_cell = f"{a:.2f}"
    f_cell = f"{int(round(f)):,}"
    if i==best_acc_avg:  a_cell = r"\textbf{"+a_cell+r"}"
    if i==best_feat_avg: f_cell = f_cell+r"$^\dagger$"
    avg_cells += [a_cell, f_cell]
emit(r"\textbf{Average} & " + " & ".join(avg_cells) + r" \\")
emit(r"\midrule")
# Synergy row — clean full-width
syn_cells = []
for ds in DATASETS:
    mel=g("MEL",ds).mean(); drs=g("MEL_NHD",ds).mean()
    ker=g("MEL_KGEF_noNHD",ds).mean(); full=g("MEL_KGEF",ds).mean()
    syn=(full-mel)-(drs-mel)-(ker-mel)
    sym=r"$+$" if syn>0 else r"$-$"
    syn_cells.append(f"{sym}{abs(syn)*100:.2f}")
emit(r"\multicolumn{9}{l}{\textit{Synergy} ($\Delta_\text{Full}-\Delta_\text{DRS}-\Delta_\text{KER}$): "
     + ", ".join(f"{dslbl} {sc}" for dslbl,sc in zip(DS_LABELS,syn_cells))
     + r"} \\")
emit(r"\bottomrule")
emit(r"\end{tabular}")
emit(r"\end{table*}")

# Write file
with open(OUT,"w") as f:
    f.write("\n".join(lines))
print(f"Tables written to {OUT} ({len(lines)} lines)")

# Print preview stats
print("\n=== Key numbers in tables ===")
matrix = np.array([[g(v,ds).mean() for v in ALL_V] for ds in DATASETS])
chi2,p=stats.friedmanchisquare(*[matrix[:,i] for i in range(len(ALL_V))])
ranks={v:[] for v in ALL_V}
for ds in DATASETS:
    ms={v:g(v,ds).mean() for v in ALL_V}
    for r,v in enumerate(sorted(ms,key=ms.get,reverse=True),1): ranks[v].append(r)
print(f"Friedman: chi2={chi2:.2f}  p={p:.2e}")
print(f"KDS-EL avg rank: {np.mean(ranks['MEL_KGEF']):.3f}")
print(f"KDS-EL rank list: {ranks['MEL_KGEF']}")
wins_fwpso=sum(g('MEL_KGEF',ds).mean()>g('FWPSO',ds).mean() for ds in DATASETS)
print(f"vs FWPSO: {wins_fwpso}/9 wins")
syn_pos=sum(1 for ds in DATASETS if
    (g('MEL_KGEF',ds).mean()-g('MEL',ds).mean())
    -(g('MEL_NHD',ds).mean()-g('MEL',ds).mean())
    -(g('MEL_KGEF_noNHD',ds).mean()-g('MEL',ds).mean())>0)
print(f"Synergy positive: {syn_pos}/9")
