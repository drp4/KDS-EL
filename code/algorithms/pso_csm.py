"""
PSO-CSM — PSO with Comprehensive Scoring Framework
===================================================
基于 Wei et al., Journal of King Saud University CIS, 2025。
综合评分驱动渐进式特征空间缩减：
  score[j] = w_rel · rel[j] + w_fb · fb[j]
  - rel[j]: 基于 F-score 的特征相关度（预计算，一次性）
  - fb[j]:  种群反馈（Pbest 选择频率，每 R_csm 轮更新）
渐进式移除低分特征，实现特征空间缩减。
"""
import numpy as np
from sklearn.feature_selection import f_classif
from utils import jFitness, pairwise_nhd


def run_PSO_CSM(X, y, opts):
    N, T, dim = opts["N"], opts["T"], X.shape[1]
    Vmax = 0.5
    w_inertia = 0.9
    c1 = c2 = 2.0

    w_rel = opts.get("w_rel", 0.5)
    w_fb = opts.get("w_fb", 0.5)
    R_csm = opts.get("R_csm", 10)
    sigma = opts.get("sigma", 0.04)
    min_feats = max(10, dim // 100)

    # ── 预计算特征相关度（F-score） ─────────────────────────────────────
    F, _ = f_classif(X, y)
    F = np.nan_to_num(F, nan=0.0, posinf=0.0, neginf=0.0)
    rel = F / (F.max() + 1e-9)

    # ── 初始化 ──────────────────────────────────────────────────────────
    init_prob = np.clip(0.1 + 0.8 * rel, 0.05, 0.95)
    P = (np.random.rand(N, dim) < init_prob).astype(float)
    V = np.zeros((N, dim))

    fit = np.array([jFitness(X, y, P[i].astype(bool), opts)
                    for i in range(N)])
    Pbest = P.copy()
    fitP = fit.copy()
    gbest = P[np.argmin(fit)].copy()
    fitG = float(np.min(fit))

    active = np.ones(dim, dtype=bool)

    curve = np.zeros(T + 1)
    curve[0] = fitG

    for t in range(1, T + 1):
        # ── 标准二值 PSO 更新 ──────────────────────────────────────────
        r1 = np.random.rand(N, dim)
        r2 = np.random.rand(N, dim)
        V = np.clip(
            w_inertia * V + c1 * r1 * (Pbest - P) + c2 * r2 * (gbest - P),
            -Vmax, Vmax,
        )
        prob = 1.0 / (1.0 + np.exp(-V))
        P_new = (np.random.rand(N, dim) < prob).astype(float)
        P_new[:, ~active] = 0.0

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

        # ── 综合评分 + 渐进式特征移除 ─────────────────────────────────
        if t % R_csm == 0:
            pb_bin = (Pbest[:, active] > 0.5).astype(float)
            fb_active = pb_bin.mean(axis=0)
            fb_norm = fb_active / (fb_active.max() + 1e-9)

            rel_active = rel[active]
            score = w_rel * rel_active + w_fb * fb_norm

            n_remove = int(sigma * (t / T) * active.sum())

            if n_remove > 0 and (active.sum() - n_remove) >= min_feats:
                local_low = np.argsort(score)[:n_remove]
                active_idx = np.where(active)[0]
                global_low = active_idx[local_low]

                active[global_low] = False
                P[:, global_low] = 0.0
                Pbest[:, global_low] = 0.0
                gbest[global_low] = 0.0

    nhd_mat = pairwise_nhd((Pbest > 0.5).astype(int))
    avg_nhd = float(nhd_mat.sum() / (N * (N - 1))) if N > 1 else 0.0

    return {
        "fitG": fitG,
        "nf": int(gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
