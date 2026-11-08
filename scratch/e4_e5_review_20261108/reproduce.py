"""Current E4/E5 review probes; no production edits, synthetic inputs only.
Run from repository root: python scratch/e4_e5_review_20261108/reproduce.py
"""
from pathlib import Path
import sys, json, hashlib, io, contextlib, copy
from unittest.mock import patch
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code'))
import run_experiment_e4 as e4
import run_experiment_e5 as e5
import algorithms_nested as alg
import nested_evaluator as ne
from algorithms import birime as original_birime

rng = np.random.RandomState(123)
X = rng.normal(size=(60, 12))
y = np.tile([0, 1], 30)
fold_tests = [np.arange(i * 12, (i + 1) * 12) for i in range(5)]
results = {}

def quiet(fn, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(**kwargs)

def error_of(fn):
    try:
        fn()
        return {'raised': False}
    except Exception as exc:
        return {'raised': True, 'type': type(exc).__name__, 'message': str(exc)}

# Real single-run E4 execution on synthetic data, including the real optimizer,
# evaluator, split manager and all five downstream classifiers.
with patch.object(e4, 'load_dataset', return_value=(X, y)):
    real_e4_record = quiet(e4.execute_e4_single_run,
        dataset_name='toy', variant_name='Abl_Static_095', outer_fold_idx=1,
        run_idx=1, seed=7, max_fes=43, pop_size=20,
        splits_dir=str(OUT / 'splits'), out_base_dir=str(OUT / 'single'), verbose=False)
(OUT / 'real_e4_single_record.json').write_text(json.dumps(real_e4_record, indent=2), encoding='utf-8')

def e4_orchestrate(record, dirname):
    with patch.object(e4, 'load_dataset', return_value=(X, y)), \
         patch.object(e4, 'execute_e4_single_run', return_value=record):
        quiet(e4.run_experiment_e4, datasets=['toy'], variants=['Abl_Static_095'],
            folds=[1], seeds=[7], workers=1, out_dir=str(OUT / dirname),
            splits_dir=str(OUT / 'splits'), verbose=False)

results['e4_missing_test_indices'] = {
    'record_has_test_indices': 'test_indices' in real_e4_record,
    **error_of(lambda: e4_orchestrate(real_e4_record, 'e4_schema_failure')),
}
real_splits = ne.NestedSplitsManager(str(OUT / 'splits')).get_outer_splits('toy', y)
augmented_e4_record = copy.deepcopy(real_e4_record)
# Full-coverage synthetic record forces evaluation of the undefined outer_folds
# operand (the single-fold case short-circuits that operand).
augmented_e4_record['test_indices'] = np.arange(len(y)).tolist()
augmented_e4_record['outer_test_metrics']['knn']['y_pred'] = y.tolist()
results['e4_undefined_outer_folds_after_schema_repair'] = error_of(
    lambda: e4_orchestrate(augmented_e4_record, 'e4_name_failure'))
assert results['e4_missing_test_indices']['type'] == 'KeyError'
assert results['e4_undefined_outer_folds_after_schema_repair']['type'] == 'NameError'
assert 'outer_folds' in results['e4_undefined_outer_folds_after_schema_repair']['message']

with patch.object(e4, 'outer_folds', [1,2,3,4,5], create=True):
    results['e4_missing_metric_import_after_prior_repairs'] = error_of(
        lambda: e4_orchestrate(augmented_e4_record, 'e4_import_failure'))
assert results['e4_missing_metric_import_after_prior_repairs']['type'] == 'NameError'

# E4 downstream aggregation probes explicitly bypass the THREE blockers above:
# synthesize valid prediction records and provide its missing global name.
def fake_e4(**kw):
    rec = copy.deepcopy(real_e4_record)
    idx = fold_tests[kw['outer_fold_idx'] - 1]
    rec.update(dataset=kw['dataset_name'], variant=kw['variant_name'],
        outer_fold=kw['outer_fold_idx'], seed=kw['seed'], test_indices=idx.tolist(),
        ker_attempts=10, ker_accepts=0 if kw['seed'] == 7 else 10,
        ker_accept_rate=0.0 if kw['seed'] == 7 else 1.0,
        audit_passed=True)
    rec['outer_test_metrics']['knn']['y_pred'] = y[idx].tolist()
    return rec

with patch.object(e4, 'load_dataset', return_value=(X, y)), \
     patch.object(e4, 'execute_e4_single_run', side_effect=fake_e4), \
     patch.object(e4, 'outer_folds', [1, 2, 3, 4, 5], create=True), \
     patch.object(e4, 'accuracy_score', accuracy_score, create=True), \
     patch.object(e4, 'balanced_accuracy_score', balanced_accuracy_score, create=True), \
     patch.object(e4, 'f1_score', f1_score, create=True):
    quiet(e4.run_experiment_e4, datasets=['toy'], variants=['Abl_Static_095'],
        folds=[1, 2, 3, 4, 5], seeds=[7, 30], workers=1,
        out_dir=str(OUT / 'e4_zero_accept'), verbose=False)
    quiet(e4.run_experiment_e4, datasets=['toy'], variants=['Abl_Static_095'],
        folds=[1], seeds=[7], workers=1,
        out_dir=str(OUT / 'e4_partial'), verbose=False)
summary = json.loads((OUT / 'e4_zero_accept/e4_summary_table.json').read_text(encoding='utf-8'))
results['e4_zero_acceptance_seed_dropped'] = {
    'prerequisite': 'bypass missing record field, undefined outer_folds, missing metric imports only',
    'seed_rates': [0.0, 1.0], 'expected_mean': 0.5,
    'reported_mean': summary['variant_summary']['Abl_Static_095']['mean_ker_accept_rate'],
}
partial4 = json.loads((OUT / 'e4_partial/e4_summary_table.json').read_text(encoding='utf-8'))
results['e4_partial_completion_after_blocker_bypass'] = {
    'is_complete': partial4['is_complete'],
    'complete_5fold_seeds': partial4['variant_summary']['Abl_Static_095']['complete_5fold_seeds'],
}
assert results['e4_zero_acceptance_seed_dropped']['reported_mean'] == 1.0

# DENCA: real BudgetEvaluator, mocked only the costly NCFS prior estimation.
def denca_probe(budget):
    ev = ne.BudgetEvaluator(X, y, [(np.arange(40), np.arange(40, 60))], max_fes=budget)
    with patch.object(alg, '_compute_ncfs_weights_nested', return_value=np.linspace(0, 1, X.shape[1])):
        outcome = error_of(lambda: alg.run_nested_DENCA_SO(X, y, ev, {'N': 20}, seed=7))
    return {**outcome, 'budget': budget, 'candidate_requests': ev.candidate_eval_requests,
        'shortcut_requests': ev.shortcut_eval_requests, 'cv_calls': ev.cv_eval_calls,
        'unique_masks': len(ev.unique_masks)}
results['denca_budget_failure'] = [denca_probe(b) for b in [20, 41, 2000]]
assert all(r.get('type') == 'BudgetExhaustedException' for r in results['denca_budget_failure'])

# bIRIME adaptation fidelity: identical deterministic objective and seed,
# capture the requests before any objective-dependent CV differences.
class StopReference(Exception):
    pass

class TraceEvaluator:
    def __init__(self, max_requests):
        self.masks = []
        self.max_requests = max_requests
    def has_budget(self):
        return len(self.masks) < self.max_requests
    def evaluate(self, mask, ws=None):
        self.masks.append(np.asarray(mask, bool).copy())
        return float(np.dot(np.asarray(mask, float), np.arange(1, X.shape[1] + 1)) / 100)

reference_trace = TraceEvaluator(100)
def reference_fitness(_X, _y, mask, opts):
    if not reference_trace.has_budget():
        raise StopReference()
    return reference_trace.evaluate(mask)
np.random.seed(7)
with patch.object(original_birime, 'jFitness', side_effect=reference_fitness):
    try:
        original_birime.run_bIRIME(X, y, {'N': 20, 'T': 100})
    except StopReference:
        pass
nested_trace = TraceEvaluator(100)
alg.run_nested_bIRIME(X, y, nested_trace, {'N': 20}, seed=7)
first_diff = next((i + 1 for i, (a,b) in enumerate(zip(reference_trace.masks,nested_trace.masks))
                   if not np.array_equal(a,b)), None)
results['birime_candidate_fidelity'] = {
    'seed': 7, 'initial_20_masks_identical': all(np.array_equal(a,b) for a,b in
        zip(reference_trace.masks[:20], nested_trace.masks[:20])),
    'first_different_request_1based': first_diff,
    'original_cosine_at_t10_T100': float(np.cos(np.pi * 10 / 10)),
    'adapter_cosine_at_t10': float(np.cos(np.pi * (10 % 10) / 10)),
}
assert results['birime_candidate_fidelity']['initial_20_masks_identical']
assert first_diff is not None

# E5 aggregation gate: inject deterministic run records, exercising the real
# orchestrator, OOF assembler, JSON serialization, and markdown generator.
def fake_e5(audit_passed=True, corrupt_predictions=False):
    def run(**kw):
        idx = fold_tests[kw['outer_fold_idx'] - 1]
        preds = y[idx].tolist()
        if corrupt_predictions:
            preds = preds[:-1]
        return {'dataset': kw['dataset_name'], 'algorithm': kw['algo_name'],
            'outer_fold': kw['outer_fold_idx'], 'seed': kw['seed'], 'run_idx': kw['run_idx'],
            'test_indices': idx.tolist(),
            'outer_predictions': {clf: preds for clf in e5.CLASSIFIER_NAMES},
            'selected_features': 3, 'total_run_time_sec': 1.0, 'internal_acc': 0.9,
            'audit': {'all_passed': audit_passed, 'details': {'probe': audit_passed}}}
    return run

def e5_case(name, folds, audit_passed=True, corrupt_predictions=False):
    with patch.object(e5, 'load_dataset', return_value=(X,y)), \
         patch.object(e5, 'execute_e5_single_run', side_effect=fake_e5(audit_passed,corrupt_predictions)):
        quiet(e5.run_experiment_e5, datasets=['toy'], algorithms=['MEL'], outer_folds=folds,
            seeds=[7], workers=1, out_dir=str(OUT / name), verbose=False)
    payload = json.loads((OUT / name / 'e5_summary_table.json').read_text(encoding='utf-8'))
    report = (OUT / name / 'e5_generalization_report.md').read_text(encoding='utf-8')
    return {'is_complete': payload['is_complete'],
        'results_nonempty': bool(payload['results']),
        'summary_has_coverage': 'coverage_ratio' in json.dumps(payload),
        'warning_banner': 'Incomplete Execution Diagnostic Banner' in report}

results['e5_partial_marked_complete'] = e5_case('e5_partial', [1])
results['e5_audit_failure_marked_complete'] = e5_case('e5_failed_audit', [1,2,3,4,5], False)
results['e5_oof_assembly_failure_marked_complete'] = e5_case('e5_bad_oof', [1,2,3,4,5], True, True)
partial_rec = fake_e5()(dataset_name='toy', algo_name='MEL', outer_fold_idx=1, seed=7, run_idx=1)
partial_metric = e5.compute_pooled_oof_for_run([partial_rec], y)
results['e5_partial_assembler_actual_flags'] = partial_metric['oof_metrics']['knn']
assert results['e5_partial_marked_complete']['is_complete']
assert results['e5_audit_failure_marked_complete']['is_complete']
assert results['e5_oof_assembly_failure_marked_complete']['is_complete']
assert not results['e5_oof_assembly_failure_marked_complete']['results_nonempty']

# E5 report can emit positive empirical claims with no observations.
empty_report = OUT / 'e5_empty_report.md'
e5.generate_e5_markdown_report({}, ['KDS_EL_TwoPhase'], ['toy'], str(empty_report),
    0.0, is_complete=False, n_completed=0, n_planned=5)
report_text = empty_report.read_text(encoding='utf-8')
results['e5_empty_report_claims'] = {
    'completed': 0, 'warning_banner': 'Incomplete Execution Diagnostic Banner' in report_text,
    'asserts_persist': 'advantages persist' in report_text,
    'asserts_superior_tradeoff': 'superior multi-criteria trade-off' in report_text,
    'asserts_cross_model_generalization': 'robust geometric transferability' in report_text,
}

# LDA resource guard/fallback trace: fake just LDA estimators. Other downstream
# models and preprocessing execute normally on small synthetic sample counts.
lda_configs = []
force_initial_svd_failure = False
class ProbeLDA(ClassifierMixin, BaseEstimator):
    def __init__(self, config, should_fail=False):
        self.config, self.should_fail = config, should_fail
    def fit(self, X, y):
        if self.should_fail:
            raise ValueError('Synthetic SVD failure')
        self.label = int(y[0])
        self.classes_ = np.unique(y)
        self.n_features_in_ = X.shape[1]
        return self
    def predict(self, X):
        return np.full(len(X), self.label, dtype=int)
def lda_factory(**kwargs):
    lda_configs.append(kwargs.copy())
    return ProbeLDA(kwargs, should_fail=force_initial_svd_failure and len(lda_configs) == 1)
wide_X = rng.normal(size=(30,1001))
wide_y = np.tile([0,1],15)
with patch.object(ne, 'LinearDiscriminantAnalysis', side_effect=lda_factory):
    lda_configs.clear()
    ne.BlindOuterEvaluator.evaluate(wide_X[:20],wide_y[:20],wide_X[20:],wide_y[20:],np.arange(1001)<1000)
    compact_configs = copy.deepcopy(lda_configs)
    lda_configs.clear()
    ne.BlindOuterEvaluator.evaluate(wide_X[:20],wide_y[:20],wide_X[20:],wide_y[20:],np.ones(1001,bool))
    wide_configs = copy.deepcopy(lda_configs)
    lda_configs.clear()
    force_initial_svd_failure = True
    ne.BlindOuterEvaluator.evaluate(wide_X[:20],wide_y[:20],wide_X[20:],wide_y[20:],np.ones(1001,bool))
    wide_fallback_configs = copy.deepcopy(lda_configs)
results['lda_classifier_and_fallback'] = {
    'D1000_estimators': compact_configs, 'D1001_estimators': wide_configs,
    'D1001_after_svd_failure_estimators': wide_fallback_configs,
}
assert wide_fallback_configs[1]['solver'] == 'lsqr'

# Current shared KDS and E4 Full trajectory consistency checks. These cheap
# deterministic surrogate objectives are NOT empirical benchmark evidence.
class CheapEvaluator(ne.BudgetEvaluator):
    def __init__(self, data, labels, objective):
        super().__init__(data, labels, [], max_fes=2000)
        self.trace, self.objective = [], objective
    def evaluate(self, mask, ws=(0.9,0.1)):
        mask = np.asarray(mask, bool)
        self.trace.append((mask.copy(), list(ws)))
        self.candidate_eval_requests += 1
        nf = int(mask.sum())
        err = self.objective(mask)
        self.cache[mask.tobytes()] = err
        return 1+(3-nf)*0.1 if nf < 3 else ws[0]*err+ws[1]*nf/len(mask)

consistency_X = rng.normal(size=(30,40))
consistency_y = np.tile([0,1],15)
consistency_checks = []
objectives = [('constant', lambda m:0.25),
    ('target', lambda m:0.1+0.2*np.logical_xor(m,np.arange(40)<10).mean())]
for kind, objective in objectives:
    for seed in [7,30,1,42,100]:
        a = CheapEvaluator(consistency_X,consistency_y,objective)
        b = CheapEvaluator(consistency_X,consistency_y,objective)
        with patch.object(e4,'compute_mi_scores',return_value=np.linspace(0,1,40)), \
             patch.object(alg,'compute_mi_scores',return_value=np.linspace(0,1,40)):
            ra = e4.run_e4_variant_optimization(consistency_X,consistency_y,a,'KDS_EL_Full',seed=seed)
            rb = alg.run_nested_KDS_EL_TwoPhase(consistency_X,consistency_y,b,{},seed=seed)
        equal_trace = len(a.trace)==len(b.trace) and all(np.array_equal(p[0],q[0]) and p[1]==q[1]
            for p,q in zip(a.trace,b.trace))
        consistency_checks.append({'objective':kind,'seed':seed,'equal_all_2000_requests':equal_trace,
            'same_final_mask':bool(np.array_equal(ra['mask'],rb['mask'])),
            'e4_air_triggers':ra['air_triggers'],'e5_air_triggers':rb['air_triggers']})
        assert equal_trace
results['current_e4_full_vs_e5_kds_consistency'] = consistency_checks
assert compact_configs == [{'solver':'lsqr','shrinkage':'auto'}]
assert wide_configs == [{'solver':'svd'}]
assert wide_fallback_configs == [{'solver':'svd'},{'solver':'lsqr','shrinkage':0.1}]

# Verify all production files stayed byte-identical during the review probes.
hashes = json.loads((OUT/'source_hashes.json').read_text(encoding='utf-8'))
results['production_files_unchanged'] = all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest() == h
    for f,h in hashes.items())
assert results['production_files_unchanged']
(OUT/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(results,indent=2,ensure_ascii=False))
