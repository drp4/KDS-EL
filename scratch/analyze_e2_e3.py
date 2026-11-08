import json

e2 = json.load(open('output/nested_cv/e2_reanalysis/e2_summary_table.json'))
e3 = json.load(open('output/nested_cv/e3_filters/e3_summary_table.json'))
e3_detailed = json.load(open('output/nested_cv/e3_filters/e3_detailed_runs.json'))

print("=== Max Filter Accuracy per Dataset (k in 20, 50, 100) vs bIRIME Acc ===")
ds_filter_max = {}
for entry in e3_detailed:
    if entry['k'] in [20, 50, 100]:
        ds = entry['dataset']
        acc = entry['pooled_metrics']['accuracy']
        bacc = entry['pooled_metrics']['balanced_accuracy']
        f1 = entry['pooled_metrics']['macro_f1']
        filt = entry['filter']
        k = entry['k']
        if ds not in ds_filter_max or acc > ds_filter_max[ds]['acc']:
            ds_filter_max[ds] = {'acc': acc, 'bacc': bacc, 'f1': f1, 'filter': filt, 'k': k}

for ds in sorted(ds_filter_max.keys()):
    fmax = ds_filter_max[ds]
    b = e2['per_dataset_summary']['bIRIME'][ds]
    b_acc = b['acc_mean']
    b_bacc = b['bacc_mean']
    b_feats = b['feats_mean']
    gap = b_acc - fmax['acc']
    print(f"{ds:12s} | Best Filter: {fmax['filter']:15s} (k={fmax['k']:3d}) Acc={fmax['acc']:.4f}, BAcc={fmax['bacc']:.4f} | bIRIME Acc={b_acc:.4f}, BAcc={b_bacc:.4f} (d={b_feats:5.1f}) | Wrapper Lead={gap:+.4f}")
