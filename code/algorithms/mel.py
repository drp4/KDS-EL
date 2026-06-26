"""
MEL — Multi-task Ensemble Learning (baseline)
=============================================
双子群多任务 PSO：
  - 子群1: 标准 PSO 速度-位置更新
  - 子群2: 基于权重矩阵的概率采样（加权特征选择）
池选择机制：合并 Pbest 和新种群，按适应度排序保留 Top-N。
"""
import numpy as np
from utils import jFitness


def run_MEL(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]

    weight = np.zeros(dim)
    P = np.random.uniform(lb, ub, (N, dim))
    V = np.zeros((N, dim))

    subSize = N // 2

    fit = np.array([jFitness(X, y, (P[i] > thres).astype(bool), opts)
                    for i in range(N)])
    fitP = fit.copy()
    Pbest = P.copy()
    Gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        P_new = P.copy()
        Xsub_best = Pbest[subSize + np.argmin(fitP[subSize:])].copy()

        for i in range(N):
            if i < subSize:
                r1, r2, r3 = np.random.rand(dim), np.random.rand(dim), np.random.rand(dim)
                V[i] = np.clip(
                    w * V[i] + c1 * r1 * (Pbest[i] - P[i])
                    + c2 * r2 * (Gbest - P[i])
                    + c3 * r3 * (Xsub_best - P[i]),
                    -Vmax, Vmax,
                )
                P_new[i] = np.clip(P[i] + V[i], lb, ub)
            else:
                vf = np.maximum(weight, 0.0)
                sv = vf.sum()
                prob = vf / sv if sv > 0 else np.full(dim, 0.5)
                P_new[i] = (np.random.rand(dim) < prob).astype(float)

        # 池选择（按适应度排序）
        pool = np.vstack([Pbest, P_new])
        pool_bin = (pool > thres).astype(bool)
        pool_fit = np.array([jFitness(X, y, pool_bin[i], opts)
                             for i in range(2 * N)])
        idx = np.argsort(pool_fit)[:N]
        P = pool[idx]
        fit_sel = pool_fit[idx]
        bin_sel = pool_bin[idx]

        # 权重更新
        for i in range(N):
            fv_n = bin_sel[i]
            fv_o = (Pbest[i] > thres)
            if fit_sel[i] < fitP[i]:
                inc = fitP[i] - fit_sel[i]
                change = np.logical_xor(fv_n, fv_o)
                weight[change & (fv_n > fv_o)] += inc
                weight[change & (fv_n < fv_o)] -= inc

        improved = fit_sel < fitP
        Pbest = np.where(improved[:, None], P, Pbest)
        fitP = np.minimum(fit_sel, fitP)

        bi = np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG = float(fitP[bi])
            Gbest = Pbest[bi].copy()

        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
