# ════════════════════════════════════════════════════════════════════════════
# 生成 SOTA 对比表（读取 results_all_merged.csv）
# 输出：LaTeX + CSV + Excel（7 个方法 × 10 数据集）
# ════════════════════════════════════════════════════════════════════════════
import os
import numpy as np
import pandas as pd

ALL_CSV = '/kaggle/working/results_all_merged.csv'
OUT_DIR = '/kaggle/working/sota_tables'
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(ALL_CSV)
for col in ['Accuracy','Num_Features','Time_sec']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['Accuracy','Num_Features','Time_sec'])

DATASETS = [
    'Adenoma','ALL_AML','ALL3','ALL4','CNS',
    'Colon','DLBCL','Leukaemia','Lymphoma','Stroke'
]

# 所有方法（对比顺序：从 baseline 到 proposed）
ALL_VERSIONS = ['BPSO','SaWDE','FWPSO','MEL','MEL_NHD','MEL_KGEF_noNHD','MEL_KGEF']
avail = [v for v in ALL_VERSIONS if (df['Version']==v).any()]
print("Available versions:", avail)

def gmean(v, ds, metric):
    s = df[(df['Version']==v)&(df['Dataset']==ds)][metric]
    return float(s.mean()) if len(s) else np.nan

def gstd(v, ds, metric):
    s = df[(df['Version']==v)&(df['Dataset']==ds)][metric]
    return float(s.std(ddof=1)) if len(s)>1 else 0.0

# ── CSV 透视表（mean±std）───────────────────────────────────────────────────
for metric, dec_m, dec_s, hi in [
        ('Accuracy', 4, 4, True),
        ('Num_Features', 1, 1, False),
        ('Time_sec', 1, 1, False)]:
    rows = []
    for ds in DATASETS:
        row = {'Dataset': ds}
        for v in avail:
            m = gmean(v, ds, metric)
            s = gstd(v, ds, metric)
            row[v] = f"{m:.{dec_m}f}±{s:.{dec_s}f}" if not np.isnan(m) else '-'
        rows.append(row)
    pd.DataFrame(rows).to_csv(
        os.path.join(OUT_DIR, f'sota_{metric}_pivot.csv'), index=False)
    print(f"✅ sota_{metric}_pivot.csv")

# ── LaTeX booktabs（最优值加粗）────────────────────────────────────────────
def gen_latex_sota(metric, caption, label, hi=True, dec_m=4, dec_s=4):
    lines = [
        r'\begin{table*}[htbp]',
        r'\centering',
        r'\caption{' + caption + '}',
        r'\label{' + label + '}',
        r'\resizebox{\textwidth}{!}{%',
        r'\begin{tabular}{l' + 'c'*len(avail) + '}',
        r'\toprule',
        'Dataset & ' + ' & '.join(avail) + r' \\',
        r'\midrule',
    ]
    for ds in DATASETS:
        vals = [gmean(v, ds, metric) for v in avail]
        finite = [v for v in vals if not np.isnan(v)]
        best = (max(finite) if hi else min(finite)) if finite else np.nan
        cells = []
        for v in avail:
            m = gmean(v, ds, metric)
            s = gstd(v, ds, metric)
            if np.isnan(m):
                cells.append('-')
                continue
            cell = f"{m:.{dec_m}f}$\\pm${s:.{dec_s}f}"
            if abs(m - best) < 1e-9:
                cell = r'\textbf{' + cell + '}'
            cells.append(cell)
        lines.append(ds + ' & ' + ' & '.join(cells) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}}', r'\end{table*}']
    return '\n'.join(lines)

for metric, cap, lbl, hi, dm, ds in [
    ('Accuracy',    'Accuracy comparison vs. SOTA methods (mean$\\pm$std, 10 runs).',
     'tab:sota_acc',  True,  4, 4),
    ('Num_Features','Feature subset size vs. SOTA methods (mean$\\pm$std, 10 runs).',
     'tab:sota_feat', False, 1, 1),
    ('Time_sec',    'Runtime comparison vs. SOTA methods (mean$\\pm$std, 10 runs).',
     'tab:sota_time', False, 1, 1),
]:
    tex = gen_latex_sota(metric, cap, lbl, hi, dm, ds)
    fname = os.path.join(OUT_DIR, f'sota_{metric}.tex')
    with open(fname, 'w') as f:
        f.write(tex)
    print(f"✅ {fname}")

# ── Excel（多 sheet）────────────────────────────────────────────────────────
xlsx = os.path.join(OUT_DIR, 'sota_comparison.xlsx')
with pd.ExcelWriter(xlsx, engine='openpyxl') as wr:
    for metric, dec_m, dec_s in [
            ('Accuracy',4,4),('Num_Features',1,1),('Time_sec',1,1)]:
        rows = []
        for ds in DATASETS:
            row = {'Dataset': ds}
            for v in avail:
                m = gmean(v, ds, metric)
                s = gstd(v, ds, metric)
                row[v] = f"{m:.{dec_m}f}±{s:.{dec_s}f}" if not np.isnan(m) else '-'
            rows.append(row)
        pd.DataFrame(rows).to_excel(wr, sheet_name=metric[:20], index=False)
print(f"✅ {xlsx}")

print(f"\n🎉 SOTA 对比表生成完毕：{OUT_DIR}")