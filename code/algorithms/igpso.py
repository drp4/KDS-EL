"""
IGPSO — Importance-Guided Particle Swarm Optimization
======================================================
基于 Applied Soft Computing, 2024。
两阶段特征重要性估计指导 PSO 参数调节：
  - w_j（惯性权重）与重要性负相关：重要特征 → 低惯性 → 快速收敛
  - c1_j/c2_j（学习因子）与重要性正相关：重要特征 → 强引导
重要性 = max(0, f_classif(真实标签) − f_classif(置乱标签))
"""
import numpy as np
from sklearn.feature_selection import f_classif
from utils import jFitness, pairwise_nhd


def run_IGPSO(X, y, opts):
    lb, ub, thres = 0.0, 1.0, opts["thres"]
    N, T, dim = opts["N"], opts["T"], X.shape[1]
    Vmax = 0.5

    W_max, W_min = 0.9, 0.1
    C_max, C_min = 2.0, 0.1

    # ── 两阶段重要性估计 ──────────────────────────────────────────────
    F1, _ = f_classif(X, y)
    F1 = np.nan_to_num(F1, nan=0.0, posinf=0.0, neginf=0.0)

    rng = np.random.default_rng(seed=0)
    y_neg = rng.permutation(y)
    F2, _ = f_classif(X, y_neg)
    F2 = np.nan_to_num(F2, nan=0.0, posinf=0.0, neginf=0.0)

    imp = np.maximum(0.0, F1 - F2)
    imp_max = imp.max()
    if imp_max > 1e-9:
        imp = imp / imp_max
    else:
        imp = np.full(dim, 0.5)

    # ── 参数映射 ───────────────────────────────────────────────────────
    w_j = W_min + (W_max - W_min) * (1.0 - imp)
    c1_j = C_min + (C_max - C_min) * imp
    c2_j = C_min + (C_max - C_min) * imp

    # ── 重要性偏置初始化 ───────────────────────────────────────────────
    init_prob = 0.2 + 0.6 * imp
    P = (np.random.rand(N, dim) < init_prob).astype(float)
    V = np.zeros((N, dim))

    fit = np.array([jFitness(X, y, P[i].astype(bool), opts)
                    for i in range(N)])
    Pbest = P.copy()
    fitP = fit.copy()
    gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        r1 = np.random.rand(N, dim)
        r2 = np.random.rand(N, dim)

        V = (w_j * V
             + c1_j * r1 * (Pbest - P)
             + c2_j * r2 * (gbest - P))
        V = np.clip(V, -Vmax, Vmax)

        prob = 1.0 / (1.0 + np.exp(-V))
        P_new = (np.random.rand(N, dim) < prob).astype(float)

        fit_new = np.array([jFitness(X, y, P_new[i].astype(bool), opts)
                            for i in range(N)])

        improved = fit_new < fitP
        Pbest = np.where(improved[:, None], P_new, Pbest)
        fitP = np.minimum(fit_new, fitP)
        P = P_new

        bi = int(np.argmin(fitP))
        if fitP[bi] < fitG:
            fitG = float(fitP[bi])
            gbest = Pbest[bi].copy()

        curve[t] = fitG

    # 最终种群多样性
    sb = Pbest.astype(int)
    nhd_mat = pairwise_nhd(sb)
    avg_nhd = float(nhd_mat.sum() / (N * (N - 1))) if N > 1 else 0.0

    return {
        "fitG": fitG,
        "nf": int(gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
