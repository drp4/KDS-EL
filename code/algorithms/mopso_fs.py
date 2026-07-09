"""
MOPSO-FS — Multi-Objective Particle Swarm Optimization for Feature Selection
=============================================================================
基于 Coello & Lechuga (2002) 的 MOPSO 框架，适配特征选择。
二元 PSO + sigmoid 传输函数，双目标：[分类错误率, 特征比例]。
外部存档存储非支配解，拥挤距离管理存档大小。
Leader 从存档中选择，Pbest 基于 Pareto 支配更新。
"""
import numpy as np
from utils import jFitness, fast_nds, crowding_dist


def dominates(a, b):
    """a dominates b: all(a <= b) and any(a < b)"""
    return np.all(a <= b) and np.any(a < b)


def run_MOPSO_FS(X, y, opts):
    N = opts["N"]
    T = opts["T"]
    dim = X.shape[1]
    w, c1, c2 = 0.9, 1.5, 1.5
    Vmax = 6.0
    archive_size = N

    # ── 初始化 ────────────────────────────────────────────────────
    P = (np.random.rand(N, dim) < 0.5).astype(float)
    V = np.zeros((N, dim))

    P_fit = np.zeros((N, 2))
    for i in range(N):
        mask = P[i].astype(bool)
        P_fit[i, 0] = jFitness(X, y, mask, opts)
        P_fit[i, 1] = mask.sum() / dim

    Pbest = P.copy()
    Pbest_fit = P_fit.copy()

    # ── 初始化 archive ────────────────────────────────────────────
    archive = []
    archive_fit = []
    for i in range(N):
        is_dominated = False
        for a_fit in archive_fit:
            if dominates(a_fit, P_fit[i]):
                is_dominated = True
                break
        if not is_dominated:
            # 移除被新解支配的
            archive = [a for a, a_fit in zip(archive, archive_fit)
                       if not dominates(P_fit[i], a_fit)]
            archive_fit = [a_fit for a_fit in archive_fit
                           if not dominates(P_fit[i], a_fit)]
            archive.append(P[i].copy())
            archive_fit.append(P_fit[i].copy())

    curve = np.zeros(T + 1)
    curve[0] = min(archive_fit, key=lambda x: x[0])[0] if archive_fit else np.min(P_fit[:, 0])

    for t in range(1, T + 1):
        for i in range(N):
            # ── Leader 选择 (拥挤距离) ────────────────────────────
            if len(archive) > 1:
                arch_arr = np.array(archive_fit)
                fronts = fast_nds(arch_arr)
                best_front = fronts[0]
                if len(best_front) > 1:
                    cd = crowding_dist(arch_arr, best_front)
                    weights = np.array([max(cd[j], 1e-6) for j in best_front])
                    weights = np.where(np.isinf(weights), 1.0, weights)
                    leader_idx = best_front[np.random.choice(len(best_front), p=weights / weights.sum())]
                else:
                    leader_idx = best_front[0]
                leader = archive[leader_idx].copy()
            elif len(archive) == 1:
                leader = archive[0].copy()
            else:
                leader = Pbest[i].copy()

            # ── 速度+位置更新 ─────────────────────────────────────
            r1, r2 = np.random.rand(dim), np.random.rand(dim)
            V[i] = w * V[i] + c1 * r1 * (Pbest[i] - P[i]) + c2 * r2 * (leader - P[i])
            V[i] = np.clip(V[i], -Vmax, Vmax)

            prob = 1.0 / (1.0 + np.exp(-V[i]))
            P[i] = (np.random.rand(dim) < prob).astype(float)

            # ── 评估 ──────────────────────────────────────────────
            mask = P[i].astype(bool)
            P_fit[i, 0] = jFitness(X, y, mask, opts)
            P_fit[i, 1] = mask.sum() / dim

            # ── Pbest 更新 (Pareto 支配) ──────────────────────────
            if dominates(P_fit[i], Pbest_fit[i]):
                Pbest[i] = P[i].copy()
                Pbest_fit[i] = P_fit[i].copy()
            elif not dominates(Pbest_fit[i], P_fit[i]):
                # 互不支配，随机选
                if np.random.rand() < 0.5:
                    Pbest[i] = P[i].copy()
                    Pbest_fit[i] = P_fit[i].copy()

            # ── Archive 更新 ──────────────────────────────────────
            is_dominated = False
            for a_fit in archive_fit:
                if dominates(a_fit, P_fit[i]):
                    is_dominated = True
                    break
            if not is_dominated:
                archive = [a for a, a_fit in zip(archive, archive_fit)
                           if not dominates(P_fit[i], a_fit)]
                archive_fit = [a_fit for a_fit in archive_fit
                               if not dominates(P_fit[i], a_fit)]
                archive.append(P[i].copy())
                archive_fit.append(P_fit[i].copy())

        # ── 存档大小控制 (拥挤距离裁剪) ──────────────────────────
        if len(archive) > archive_size:
            arch_arr = np.array(archive_fit)
            cd = np.zeros(len(archive))
            for m in range(2):
                order = np.argsort(arch_arr[:, m])
                cd[order[0]] = cd[order[-1]] = np.inf
                span = arch_arr[order[-1], m] - arch_arr[order[0], m]
                if span > 0:
                    for k in range(1, len(order) - 1):
                        cd[order[k]] += (arch_arr[order[k + 1], m] - arch_arr[order[k - 1], m]) / span
            # 移除最拥挤的
            worst = np.argsort(cd)[:len(archive) - archive_size]
            archive = [a for j, a in enumerate(archive) if j not in worst]
            archive_fit = [a_fit for j, a_fit in enumerate(archive_fit) if j not in worst]

        # 记录当前
        curr_best = min(archive_fit, key=lambda x: x[0])[0] if archive_fit else np.min(P_fit[:, 0])
        curve[t] = curr_best

    # ── 从最终 archive 选最佳解 ──────────────────────────────────
    if archive_fit:
        arch_arr = np.array(archive_fit)
        best_idx = np.argmin(arch_arr[:, 0])
        Gbest = (archive[best_idx] > 0.5).astype(bool)
        fitG = float(archive_fit[best_idx][0])
    else:
        best_idx = np.argmin(Pbest_fit[:, 0])
        Gbest = (Pbest[best_idx] > 0.5).astype(bool)
        fitG = float(Pbest_fit[best_idx, 0])

    return {
        "fitG": fitG,
        "nf": int(Gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T + 1),
    }
