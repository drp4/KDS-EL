"""
NSGA-II-FS — Non-dominated Sorting Genetic Algorithm II for Feature Selection
==============================================================================
基于 Deb et al. (2002) IEEE TEVC。
二元编码，双目标：[分类错误率, 特征比例]。
Pareto 非支配排序 + 拥挤距离选择，二元锦标赛选出父代，均匀交叉 + 位翻转变异。
最终输出前沿中错误率最低的解。
"""
import numpy as np
from utils import jFitness, fast_nds, crowding_dist


def run_NSGA_II_FS(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    pc = 0.9       # 交叉概率
    pm = max(0.001, 1.0 / dim)  # 变异概率（保底 0.1%，适配 dim≤1000→1/dim）

    # ── 初始化 ────────────────────────────────────────────────────
    P = (np.random.rand(N, dim) < 0.5).astype(float)
    P_fit = np.zeros((N, 2))
    for i in range(N):
        mask = P[i].astype(bool)
        P_fit[i, 0] = jFitness(X, y, mask, opts)
        P_fit[i, 1] = mask.sum() / dim

    curve = np.zeros(T + 1)
    curve[0] = np.min(P_fit[:, 0])

    for t in range(1, T + 1):
        # ── 非支配排序 + 拥挤距离 ────────────────────────────────
        fronts = fast_nds(P_fit)
        rank = np.zeros(N, dtype=int)
        cd = np.zeros(N)
        for f_idx, front in enumerate(fronts):
            for idx in front:
                rank[idx] = f_idx
            cd_f = crowding_dist(P_fit, front)
            for idx in front:
                cd[idx] = cd_f[idx]

        # ── 二元锦标赛选择 ────────────────────────────────────────
        parents = np.zeros((N, dim))
        for i in range(N):
            a, b = np.random.choice(N, 2, replace=False)
            if rank[a] < rank[b] or (rank[a] == rank[b] and cd[a] > cd[b]):
                parents[i] = P[a].copy()
            else:
                parents[i] = P[b].copy()

        # ── 均匀交叉 + 位翻转变异 ─────────────────────────────────
        Q = parents.copy()
        for i in range(0, N - 1, 2):
            if np.random.rand() < pc:
                mask = np.random.rand(dim) < 0.5
                # 至少交换一个位
                if not mask.any():
                    mask[np.random.randint(dim)] = True
                Q[i, mask], Q[i + 1, mask] = Q[i + 1, mask].copy(), Q[i, mask].copy()

        # 变异
        for i in range(N):
            mut_mask = np.random.rand(dim) < pm
            if mut_mask.any():
                Q[i, mut_mask] = 1 - Q[i, mut_mask]

        # ── 评估子代 ──────────────────────────────────────────────
        Q_fit = np.zeros((N, 2))
        for i in range(N):
            mask = Q[i].astype(bool)
            Q_fit[i, 0] = jFitness(X, y, mask, opts)
            Q_fit[i, 1] = mask.sum() / dim

        # ── 合并父代+子代，精英选择 ──────────────────────────────
        R = np.vstack([P, Q])
        R_fit = np.vstack([P_fit, Q_fit])
        fronts_all = fast_nds(R_fit)
        selected = []
        for front in fronts_all:
            if len(selected) + len(front) <= N:
                selected.extend(front)
            else:
                needed = N - len(selected)
                cd_f = crowding_dist(R_fit, front)
                order = sorted(front, key=lambda i: cd_f[i], reverse=True)
                selected.extend(order[:needed])
                break

        P = R[selected].copy()
        P_fit = R_fit[selected].copy()
        curve[t] = np.min(P_fit[:, 0])

    # ── 从最终 Pareto 前沿选最佳解（最低 error，相等时最少特征） ──
    fronts_final = fast_nds(P_fit)
    best_front = fronts_final[0]
    best_idx = min(best_front, key=lambda i: (P_fit[i, 0], P_fit[i, 1]))
    Gbest = (P[best_idx] > 0.5).astype(bool)

    return {
        "fitG": float(P_fit[best_idx, 0]),
        "nf": int(Gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
