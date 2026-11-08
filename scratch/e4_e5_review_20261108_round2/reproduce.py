"""Second review of user-modified E4/E5, synthetic data only; source unchanged."""
from pathlib import Path
import sys, json, hashlib, io, contextlib, copy, time
from unittest.mock import patch
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'code'))
import run_experiment_e4 as e4
import run_experiment_e5 as e5
import nested_evaluator as ne
import algorithms_nested as alg
from algorithms import birime as original_birime

rng = np.random.RandomState(123)
X = rng.normal(size=(60,6))
y = np.tile([0,1],30)
results = {}

def save():
    (OUT/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')

def logged(name, fn, **kwargs):
    with (OUT/(name+'.log')).open('w',encoding='utf-8') as log, contextlib.redirect_stdout(log):
        return fn(**kwargs)

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

# E4: real algorithms, real 2000-request evaluator, real five-model downstream,
# all 7 variants and all 5 outer folds on a tiny synthetic dataset.
with patch.object(e4,'load_dataset',return_value=(X,y)):
    payload4=logged('real_e4',e4.run_experiment_e4,datasets=['toy_round2'],
        variants=list(e4.E4_VARIANT_SPECS),folds=[1,2,3,4,5],seeds=[7],workers=1,
        splits_dir=str(OUT/'splits'),out_dir=str(OUT/'real_e4'),verbose=False)
records4=read_json(OUT/'real_e4/e4_detailed_runs.json')
results['real_e4_all_variants_fivefold']={
    'planned':payload4['total_runs_planned'],'completed':len(records4),
    'all_audits_passed':payload4['all_audits_passed'],
    'valid_for_formal_claims':payload4['valid_for_formal_claims'],
    'all_records_have_test_indices':all('test_indices' in r for r in records4),
    'all_used_2000_requests':all(r['candidate_eval_requests']==2000 for r in records4),
}
assert len(records4)==35
assert payload4['valid_for_formal_claims']
save()
print('E4: all 35 real synthetic runs complete.',flush=True)

# E5 core: no synthetic record injection. Only dataset loading and output root
# are isolated, so no formal output/split cache gets touched.
with patch.object(e5,'load_dataset',return_value=(X,y)), \
     patch.object(e5,'PROJECT_ROOT',str(OUT/'isolated_project')):
    logged('real_e5',e5.run_experiment_e5,datasets=['toy_round2'],
        algorithms=e5.STAGE1_CORE_ALGOS,outer_folds=[1,2,3,4,5],seeds=[7],workers=1,
        out_dir=str(OUT/'real_e5'),verbose=False)
payload5=read_json(OUT/'real_e5/e5_summary_table.json')
records5=read_json(OUT/'real_e5/e5_detailed_runs.json')
results['real_e5_core_fivefold']={
    'planned':payload5['total_planned_runs'],'completed':len(records5),
    'real_nested_audits_all_passed':all(r['audit']['all_passed'] for r in records5),
    'summary_all_audits_passed':payload5['all_audits_passed'],
    'summary_valid_for_formal_claims':payload5['valid_for_formal_claims'],
    'record_has_top_level_audit_passed':any('audit_passed' in r for r in records5),
    'all_used_2000_requests':all(r['evaluator_counters']['candidate_eval_requests']==2000 for r in records5),
}
assert len(records5)==25
assert all(r['audit']['all_passed'] for r in records5)
assert not payload5['all_audits_passed']
assert not payload5['valid_for_formal_claims']
for name in e5.STAGE1_CORE_ALGOS:
    recs=[r for r in records5 if r['algorithm']==name]
    pooled=e5.compute_pooled_oof_for_run(recs,y)
    results.setdefault('real_e5_pooled_flags',{})[name]={
        'is_complete_5fold':pooled['is_complete_5fold'],'coverage_ratio':pooled['coverage_ratio'],
        'all_audits_passed':pooled['all_audits_passed'],'is_statistically_valid':pooled['is_statistically_valid']}
save()
print('E5 core: all 25 real synthetic runs complete; audit schema mismatch confirmed.',flush=True)

# DENCA: real NCFS, actual default 2000 budget, real single-run audit.
with patch.object(e5,'load_dataset',return_value=(X,y)):
    den=logged('real_denca',e5.execute_e5_single_run,dataset_name='toy_round2',algo_name='DENCA_SO',
        outer_fold_idx=1,run_idx=1,seed=7,max_fes=2000,pop_size=20,
        splits_dir=str(OUT/'splits'),verbose=False)
(OUT/'real_denca_record.json').write_text(json.dumps(den,indent=2),encoding='utf-8')
c=den['evaluator_counters']
results['real_denca_accounting']={
    'returned_without_budget_exception':True,'candidate_requests':c['candidate_eval_requests'],
    'accounted_request_sum':c['shortcut_eval_requests']+c['cache_hit_count']+c['cv_eval_calls'],
    'audit_all_passed':den['audit']['all_passed'],
    'failed_audit_checks':[k for k,v in den['audit']['details'].items() if not v],
}
assert c['candidate_eval_requests']==2000
assert not den['audit']['details']['9_requests_accounting_closed']
save()
print('DENCA: now returns, but real audit accounting fails.',flush=True)

# KER aggregation regression: zero-success seeds must be included.
template=copy.deepcopy(records4[0])
fold_indices=[b for a,b in ne.NestedSplitsManager(str(OUT/'splits')).get_outer_splits('toy_round2',y)]
def fake_e4(**kw):
    r=copy.deepcopy(template);idx=fold_indices[kw['outer_fold_idx']-1]
    r.update(dataset=kw['dataset_name'],variant=kw['variant_name'],seed=kw['seed'],
        outer_fold=kw['outer_fold_idx'],test_indices=idx.tolist(),audit_passed=True,
        ker_attempts=10,ker_accepts=0 if kw['seed']==7 else 10,
        ker_accept_rate=0.0 if kw['seed']==7 else 1.0)
    r['outer_test_metrics']['knn']['y_pred']=y[idx].tolist()
    return r
with patch.object(e4,'load_dataset',return_value=(X,y)), \
     patch.object(e4,'execute_e4_single_run',side_effect=fake_e4):
    ker=logged('ker_regression',e4.run_experiment_e4,datasets=['toy_round2'],variants=['KDS_EL_Full'],
        folds=[1,2,3,4,5],seeds=[7,30],workers=1,out_dir=str(OUT/'ker_regression'),verbose=False)
    partial=logged('e4_partial',e4.run_experiment_e4,datasets=['toy_round2'],variants=['KDS_EL_Full'],
        folds=[1],seeds=[7],workers=1,out_dir=str(OUT/'e4_partial'),verbose=False)
results['e4_ker_and_partial_fixes']={
    'rates_injected':[0.0,1.0],'reported_ker_rate':ker['variant_summary']['KDS_EL_Full']['mean_ker_accept_rate'],
    'partial_valid_for_formal_claims':partial['valid_for_formal_claims']}
assert results['e4_ker_and_partial_fixes']['reported_ker_rate']==0.5
assert not partial['valid_for_formal_claims']

# bIRIME same fixed schedule: compare every one of 2000 requests, not only initialization.
class StopReference(Exception):pass
class TraceEvaluator:
    def __init__(self):self.max_fes=2000;self.masks=[]
    def has_budget(self):return len(self.masks)<self.max_fes
    def evaluate(self,mask,ws=None):
        self.masks.append(np.asarray(mask,bool).copy())
        return float(np.dot(np.asarray(mask,float),np.arange(1,7))/100)
a,b=TraceEvaluator(),TraceEvaluator()
def reference_fitness(_X,_y,mask,opts):
    if not a.has_budget():raise StopReference()
    return a.evaluate(mask)
np.random.seed(7)
with patch.object(original_birime,'jFitness',side_effect=reference_fitness):
    try:original_birime.run_bIRIME(X,y,{'N':20,'T':100})
    except StopReference:pass
alg.run_nested_bIRIME(X,y,b,{'N':20,'T':100},seed=7)
first_diff=next((i+1 for i,(p,q) in enumerate(zip(a.masks,b.masks)) if not np.array_equal(p,q)),None)
results['birime_fidelity']={'requests':len(b.masks),'first_different_request':first_diff}
assert len(a.masks) == len(b.masks) == 2000
assert first_diff is None
save()

# LDA: inspect actual estimator routes with a lightweight classifier probe.
configs=[]
fail_first_svd=False
class ProbeLDA(ClassifierMixin,BaseEstimator):
    def __init__(self,config,should_fail=False):self.config=config;self.should_fail=should_fail
    def fit(self,X,y):
        if self.should_fail:raise ValueError('Injected SVD failure')
        self.classes_=np.unique(y);self.label=int(y[0]);self.n_features_in_=X.shape[1]
        return self
    def predict(self,X):return np.full(len(X),self.label,dtype=int)
def factory(**kw):
    configs.append(kw.copy())
    return ProbeLDA(kw,fail_first_svd and len(configs)==1)
wide=rng.normal(size=(30,1001));wy=np.tile([0,1],15)
with patch.object(ne,'LinearDiscriminantAnalysis',side_effect=factory):
    r=ne.BlindOuterEvaluator.evaluate(wide[:20],wy[:20],wide[20:],wy[20:],np.ones(1001,bool))
    normal_cfg=copy.deepcopy(configs)
    configs.clear();fail_first_svd=True
    rfb=ne.BlindOuterEvaluator.evaluate(wide[:20],wy[:20],wide[20:],wy[20:],np.ones(1001,bool))
    fallback_cfg=copy.deepcopy(configs)
results['lda_wide_safeguard']={'normal_estimators':normal_cfg,'fallback_estimators':fallback_cfg,
    'normal_model_variant':r['lda'].get('model_variant'),'fallback_used':rfb['lda']['fallback_used'],
    'e5_record_preserves_model_variant':'model_variant' in records5[0]['outer_metrics']['lda']}
assert all(k['solver']=='svd' for k in fallback_cfg)

# Empty report is fixed, but valid-data adverse outcomes still get positive wording.
e5.generate_e5_markdown_report({},['KDS_EL_TwoPhase'],['toy_round2'],str(OUT/'empty_report.md'),
    0,is_complete=False,valid_for_formal_claims=False,n_completed=0,n_planned=5)
empty=(OUT/'empty_report.md').read_text(encoding='utf-8')
entry=copy.deepcopy(payload5['results']['KDS_EL_TwoPhase']['toy_round2'])
for name,acc in [('knn',0.95),('svm',0.10),('random_forest',0.15)]:
    entry['classifiers'][name]['accuracy_mean']=acc
adverse={'KDS_EL_TwoPhase':{'toy_round2':entry}}
e5.generate_e5_markdown_report(adverse,['KDS_EL_TwoPhase'],['toy_round2'],str(OUT/'adverse_report.md'),
    0,is_complete=True,valid_for_formal_claims=True,n_completed=5,n_planned=5)
adverse_text=(OUT/'adverse_report.md').read_text(encoding='utf-8')
results['report_fixes_and_remaining_wording']={
    'empty_suppresses_takeaways':'takeaways regarding' in empty and 'are withheld' in empty,
    'adverse_knn_acc':0.95,'adverse_svm_acc':0.10,'adverse_rf_acc':0.15,
    'adverse_report_asserts_consistent_generalization':'exhibit consistent generalization' in adverse_text}
assert results['report_fixes_and_remaining_wording']['empty_suppresses_takeaways']
assert results['report_fixes_and_remaining_wording']['adverse_report_asserts_consistent_generalization']

hashes=read_json(OUT/'source_hashes.json')
results['production_files_unchanged']=all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h for f,h in hashes.items())
assert results['production_files_unchanged']
save()
print(json.dumps(results,indent=2,ensure_ascii=False))
