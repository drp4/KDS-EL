"""Windows spawn smoke test. Only toy data loading is replaced."""
from pathlib import Path
import sys, json, contextlib
from unittest.mock import patch
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
import run_experiment_e4 as e4
import run_experiment_e5 as e5
X=np.random.RandomState(123).normal(size=(60,6))
y=np.tile([0,1],30)
e4_single=e4.execute_e4_single_run
e5_single=e5.execute_e5_single_run

def toy_e4_worker(*args,**kwargs):
    with patch.object(e4,'load_dataset',return_value=(X,y)):
        return e4_single(*args,**kwargs)

def toy_e5_worker(*args,**kwargs):
    with patch.object(e5,'load_dataset',return_value=(X,y)):
        return e5_single(*args,**kwargs)

def main():
    with (OUT/'parallel_smoke.log').open('w',encoding='utf-8') as log, contextlib.redirect_stdout(log):
        with patch.object(e4,'load_dataset',return_value=(X,y)),patch.object(e4,'execute_e4_single_run',toy_e4_worker):
            p4=e4.run_experiment_e4(datasets=['toy_parallel'],variants=list(e4.E4_VARIANT_SPECS)[:2],folds=[1,2],seeds=[7],workers=2,splits_dir=str(OUT/'parallel_splits'),out_dir=str(OUT/'parallel_e4'),verbose=False)
        with patch.object(e5,'load_dataset',return_value=(X,y)),patch.object(e5,'execute_e5_single_run',toy_e5_worker),patch.object(e5,'PROJECT_ROOT',str(OUT/'parallel_project')):
            e5.run_experiment_e5(datasets=['toy_parallel'],algorithms=['KDS_EL_TwoPhase','DENCA_SO'],outer_folds=[1,2],seeds=[7],workers=2,out_dir=str(OUT/'parallel_e5'),verbose=False)
    p5=json.loads((OUT/'parallel_e5/e5_summary_table.json').read_text(encoding='utf-8'))
    result={'workers':2,'e4_completed':p4['total_runs_completed'],'e4_all_audits_passed':p4['all_audits_passed'],'e4_partial_rejected':not p4['valid_for_formal_claims'],'e5_completed':p5['total_completed_runs'],'e5_all_audits_passed':p5['all_audits_passed'],'e5_partial_rejected':not p5['valid_for_formal_claims']}
    assert result['e4_completed']==result['e5_completed']==4
    assert all(result[k] for k in ['e4_all_audits_passed','e4_partial_rejected','e5_all_audits_passed','e5_partial_rejected'])
    (OUT/'parallel_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
