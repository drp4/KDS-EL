"""
MOEA-D-FS — Multi-Objective Evolutionary Algorithm based on Decomposition
=========================================================================
基于 Zhang & Li (2007) IEEE TEVC，适配特征选择。
将 MOP 分解为 N 个标量子问题（Tchebycheff 法），邻域内繁殖+更新。
二元编码 + 均匀交叉 + 位翻转变异。
参考点 z* 追踪各目标的历史最佳值。
"""
import numpy as np
from utils import jFitness


def _tchebycheff(fv, w, z_star):
    """Tchebycheff 分解值。w_i=0 时用极小 epsilon 避免退化为单目标。"""
    eps = 1e-6
    w_safe = np.where(w < eps, eps, w)
    return np.max(w_safe * np.abs(fv - z_star))


def run_MOEA_D_FS(X, y, opts):
    N = opts["N"]
    T_gens = opts["T"]
    dim = X.shape[1]
    T_nb = max(2, N // 5)  # 邻域大小
    pc = 0.9
    pm = max(0.001, 1.0 / dim)  # 确保高维数据也有足够突变（保底 0.1%）

    # ── 均匀权重向量 (2 目标) ─────────────────────────────────────
    lam = np.zeros((N, 2))
    lam[:, 0] = np.arange(N) / (N - 1) if N > 1 else np.array([0.5])
    lam[:, 1] = 1.0 - lam[:, 0]

    # ── 邻域 (基于权重向量距离) ───────────────────────────────────
    dist = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            dist[i, j] = np.sqrt(np.sum((lam[i] - lam[j]) ** 2))
    B = np.argsort(dist, axis=1)[:, :T_nb]

    # ── 初始化 ────────────────────────────────────────────────────
    P = (np.random.rand(N, dim) < 0.5).astype(float)
    P_fit = np.zeros((N, 2))
    for i in range(N):
        mask = P[i].astype(bool)
        P_fit[i, 0] = jFitness(X, y, mask, opts)
        P_fit[i, 1] = mask.sum() / dim

    # 参考点 z* (理想点，每个目标的历史最小值)
    z_star = np.min(P_fit, axis=0)

    curve = np.zeros(T_gens + 1)
    curve[0] = np.min(P_fit[:, 0])

    for t in range(1, T_gens + 1):
        # 为每个子问题生成一个新解
        for i in range(N):
            # ── 从邻域选亲本 ──────────────────────────────────────
            nb = B[i]
            p1, p2 = np.random.choice(nb, 2, replace=False)

            # ── 均匀交叉 ──────────────────────────────────────────
            child = P[p1].copy()
            if np.random.rand() < pc:
                cross_mask = np.random.rand(dim) < 0.5
                if not cross_mask.any():
                    cross_mask[np.random.randint(dim)] = True
                child[cross_mask] = P[p2][cross_mask]

            # ── 位翻转变异 ────────────────────────────────────────
            mut_mask = np.random.rand(dim) < pm
            if mut_mask.any():
                child[mut_mask] = 1 - child[mut_mask]

            # ── 评估子代 ──────────────────────────────────────────
            cmask = child.astype(bool)
            child_fit = np.array([
                jFitness(X, y, cmask, opts),
                cmask.sum() / dim,
            ])

            # ── 更新参考点 ────────────────────────────────────────
            z_star = np.minimum(z_star, child_fit)

            # ── 更新邻域内的解 ────────────────────────────────────
            updated = 0
            for j in nb:
                old_val = _tchebycheff(P_fit[j], lam[j], z_star)
                new_val = _tchebycheff(child_fit, lam[j], z_star)
                if new_val < old_val:
                    P[j] = child.copy()
                    P_fit[j] = child_fit.copy()
                    updated += 1
                if updated >= 2:  # 限制每个子代最多更新 2 个邻居
                    break

        curve[t] = np.min(P_fit[:, 0])

    # ── 选择最佳解 (最低 error，相等时最少特征) ──────────────────
    best_idx = int(np.argmin(P_fit[:, 0]))
    Gbest = (P[best_idx] > 0.5).astype(bool)

    return {
        "fitG": float(P_fit[best_idx, 0]),
        "nf": int(Gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T_gens + 1),
    }
