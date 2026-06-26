"""
FWPSO — Feature Weighting PSO
===============================
基于 Wang et al. IEEE TCYB 2022。
用特征权重矩阵引导第二子群搜索，权重根据适应度变化动态更新。
"""
import numpy as np
from utils import jFitness


def run_FWPSO(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    thres = opts["thres"]
    dim = X.shape[1]
    c1 = c2 = 2.0
    w = 0.9
    Vmax = 0.5

    weight = np.zeros(dim)
    P = np.random.rand(N, dim)
    V = np.zeros((N, dim))

    fitP = np.array([jFitness(X, y, (P[i] > thres).astype(bool), opts)
                     for i in range(N)])
    Pbest = P.copy()
    g = np.argmin(fitP)
    Gbest, fitG = Pbest[g].copy(), float(fitP[g])

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        for i in range(N):
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w * V[i] + c1 * r1 * (Pbest[i] - P[i]) + c2 * r2 * (Gbest - P[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)

            vf = np.maximum(weight, 0.0)
            sv = vf.sum()
            if sv > 0 and np.random.rand() < 0.3:
                prob = vf / sv
                P[i] = (np.random.rand(dim) < prob).astype(float)
            else:
                P[i] = np.clip(P[i] + V[i], 0, 1)

            f = jFitness(X, y, (P[i] > thres).astype(bool), opts)
            pb = (Pbest[i] > thres)
            pn = (P[i] > thres)
            if f < fitP[i]:
                inc = fitP[i] - f
                change = np.logical_xor(pb, pn)
                weight[change & pn & (~pb)] += inc
                weight[change & pb & (~pn)] -= inc
                Pbest[i] = P[i].copy()
                fitP[i] = f
            if f < fitG:
                fitG = float(f)
                Gbest = P[i].copy()

        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
