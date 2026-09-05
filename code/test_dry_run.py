import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import evaluate_subset
from algorithms import RUNNERS

def main():
    np.random.seed(42)
    # 测试维度 D=50, 样本数=30
    X = np.random.randn(30, 50)
    y = np.array([0] * 15 + [1] * 15)
    opts = {
        'N': 6,
        'T': 4,
        'k': 3,
        'cv_splits': 3,
        'cv_shuffle': True,
        'cv_random_state': 42,
        'ws': [0.9, 0.1],
        'thres': 0.6,
        'phase_switch': 0.7,
        'ws_phase1': [0.70, 0.30],
        'ws_phase2': [0.95, 0.05],
        'weight_decay': 0.99,
        'flip_frac': 0.01,
        'rand_flip_p': 0.10,
        'stall_patience': 5,
        'elite_k': 2,
    }

    # 仅测试新增的三个方法和需要重跑的 KDS_EL_TwoPhase
    test_algos = ['DENCA_SO', 'bIRIME', 'BinCOA', 'KDS_EL_TwoPhase']

    print("=== Testing New Algorithms (Dry Run Verification) ===")
    for name in test_algos:
        fn = RUNNERS[name]
        res = fn(X, y, opts)

        assert "mask" in res, f"[{name}] did not return mask"
        assert "fitG" in res, f"[{name}] did not return fitG"
        assert "curve" in res, f"[{name}] did not return curve"
        assert len(res["curve"]) == opts["T"] + 1, f"[{name}] curve length mismatch: {len(res['curve'])}"

        mask = res["mask"]
        assert mask.shape == (50,), f"[{name}] mask shape mismatch: {mask.shape}"
        assert mask.sum() > 0, f"[{name}] mask selected 0 features!"

        ev = evaluate_subset(X, y, mask, opts)
        assert abs((ev["accuracy"] + ev["error_rate"]) - 1.0) < 1e-9, f"[{name}] Acc + Err != 1.0"

        print(
            f"{name:16s} | nf={res['nf']:2d}/{X.shape[1]} ({res['nf']/X.shape[1]:.1%}) "
            f"| fitG={res['fitG']:.4f} | Pure Acc={ev['accuracy']:.4f} "
            f"| Scalar Fit={ev['scalar_fitness']:.4f}"
        )

    print("\n>>> All new algorithm dry-run tests PASSED successfully! <<<")

if __name__ == '__main__':
    main()
