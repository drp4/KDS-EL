"""
SaWDE — Self-adaptive Weighted Differential Evolution
======================================================
基于 Wang et al. IEEE TEVC 2021。
三种 DE 变异策略自适应加权，连续空间 sigmoid 二值化。
"""
import numpy as np
from utils import jFitness


def run_SaWDE(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    thres = opts["thres"]
    dim = X.shape[1]

    P = np.random.rand(N, dim)
    fit = np.array([jFitness(X, y, (P[i] > thres).astype(bool), opts)
                    for i in range(N)])

    Gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))

    w_strat = np.ones(3) / 3.0
    F_hist = [0.5] * 3
    CR_hist = [0.5] * 3

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        w_norm = w_strat / (w_strat.sum() + 1e-12)
        success = np.zeros(3)
        count = np.zeros(3)
        P_new = P.copy()

        for i in range(N):
            s = np.random.choice(3, p=w_norm)
            F = np.clip(np.random.normal(F_hist[s], 0.1), 0.1, 1.0)
            CR = np.clip(np.random.normal(CR_hist[s], 0.1), 0.0, 1.0)

            idx = list(range(N))
            idx.remove(i)
            r1, r2, r3 = np.random.choice(idx, 3, replace=False)

            if s == 0:
                mut = P[r1] + F * (P[r2] - P[r3])
            elif s == 1:
                mut = P[i] + F * (Gbest - P[i]) + F * (P[r1] - P[r2])
            else:
                mut = Gbest + F * (P[r1] - P[r2])

            mut = np.clip(mut, 0, 1)
            cross = np.random.rand(dim) < CR
            if not cross.any():
                cross[np.random.randint(dim)] = True
            trial = np.where(cross, mut, P[i])

            f_trial = jFitness(X, y, (trial > thres).astype(bool), opts)
            if f_trial <= fit[i]:
                P_new[i] = trial
                fit[i] = f_trial
                success[s] += 1
                F_hist[s] = 0.9 * F_hist[s] + 0.1 * F
                CR_hist[s] = 0.9 * CR_hist[s] + 0.1 * CR
                if f_trial < fitG:
                    fitG = float(f_trial)
                    Gbest = trial.copy()
            count[s] += 1

        sr = np.where(count > 0, success / count, 0.0)
        w_strat = 0.9 * w_strat + 0.1 * (sr + 0.01)
        w_strat = w_strat / (w_strat.sum() + 1e-12)
        P = P_new
        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
