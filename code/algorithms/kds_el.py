"""
KDS-EL (Proposed)
===================
完整框架：MEL + DRS (EMDO多样性选择) + KER (KGEF精英微调)。
对应论文提出的 KDS-EL 方法。
"""
import numpy as np
from utils import jFitness, pairwise_nhd, emdo_select, kgef_flip


def run_KDS_EL(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    c1 = c2 = c3 = 2.0
    w = 0.9
    Vmax = (ub - lb) / 2
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    decay = opts["weight_decay"]
    flip_count = max(1, int(opts["flip_frac"] * dim))
    rand_p = opts["rand_flip_p"]

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
    nhd_curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        weight *= decay
        alpha_cd = (t / T) ** 2

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

        # EMDO 选择（联合优化适应度 + 多样性）
        pool = np.vstack([Pbest, P_new])
        pool_bin = (pool > thres).astype(int)
        pool_fit = np.array([jFitness(X, y, pool_bin[i].astype(bool), opts)
                             for i in range(2 * N)])
        nhd_mat = pairwise_nhd(pool_bin)

        sel = emdo_select(pool_fit, nhd_mat, N, alpha_cd)
        P = pool[sel]
        fit_sel = pool_fit[sel]

        improved = fit_sel < fitP
        Pbest = np.where(improved[:, None], P, Pbest)
        fitP = np.minimum(fit_sel, fitP)

        # KGEF 精英微调
        for e in np.argsort(fitP)[:opts["elite_k"]]:
            elite_bin = (Pbest[e] > thres).astype(int)
            mutant = kgef_flip(weight, elite_bin, flip_count, rand_p)
            mfit = jFitness(X, y, mutant.astype(bool), opts)
            if mfit < fitP[e]:
                Pbest[e] = mutant
                fitP[e] = mfit

        bi = np.argmin(fitP)
        if fitP[bi] < fitG:
            fitG = float(fitP[bi])
            Gbest = Pbest[bi].copy()

        # 记录种群 NHD 多样性
        sb = (Pbest > thres).astype(int)
        nm = pairwise_nhd(sb)
        nhd_curve[t] = nm.sum() / (N * (N - 1)) if N > 1 else 0.0
        curve[t] = fitG

    mask = (Gbest > thres)
    return {
        "fitG": fitG,
        "nf": int(mask.sum()),
        "curve": curve,
        "nhd_curve": nhd_curve,
    }
