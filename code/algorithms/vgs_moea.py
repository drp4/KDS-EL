"""
VGS-MOEA — Variable-length Genetic String Multi-Objective EA for FS
====================================================================
可变基因组长度 MOEA：每个个体是选中的特征索引列表（非固定长度二元串）。
特殊算子：
  - 交叉：两父代交换各自特征集的子集
  - 变异：随机添加或移除特征
NSGA-II 风格的非支配排序 + 拥挤距离选择。
双目标：[分类错误率, 特征数量]。
"""
import numpy as np
from utils import jFitness, fast_nds, crowding_dist


def _list_to_mask(indices, dim):
    """将特征索引列表转为 bool mask。"""
    mask = np.zeros(dim, dtype=bool)
    for idx in indices:
        if 0 <= idx < dim:
            mask[int(idx)] = True
    return mask


def _mask_to_list(mask):
    return np.where(mask)[0].tolist()


def _ensure_min_features(indices, dim, min_f=3):
    """确保至少选 min_f 个特征。"""
    if len(indices) < min_f:
        need = min_f - len(indices)
        avail = list(set(range(dim)) - set(int(i) for i in indices))
        if len(avail) >= need:
            extra = np.random.choice(avail, need, replace=False).tolist()
            indices = indices + extra
        else:
            indices = indices + avail
    return indices


def run_VGS_MOEA(X, y, opts):
    N = opts["N"]
    T_gens = opts["T"]
    dim = X.shape[1]
    pc = 0.8
    pm_add = 0.15
    pm_del = 0.10

    # ── 初始化可变长度种群 ────────────────────────────────────────
    P_indices = []
    P_fit = np.zeros((N, 2))
    for i in range(N):
        size = np.random.randint(max(3, dim // 100), max(10, dim // 10))
        indices = np.random.choice(dim, size, replace=False).tolist()
        P_indices.append(indices)
        mask = _list_to_mask(indices, dim)
        P_fit[i, 0] = jFitness(X, y, mask, opts)
        P_fit[i, 1] = len(indices) / dim

    curve = np.zeros(T_gens + 1)
    curve[0] = np.min(P_fit[:, 0])

    for t in range(1, T_gens + 1):
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

        # ── 生成子代 ──────────────────────────────────────────────
        Q_indices = []
        Q_fit = np.zeros((N, 2))

        for i in range(N):
            # 二元锦标赛选亲本
            a, b = np.random.choice(N, 2, replace=False)
            p1 = P_indices[a] if (rank[a] < rank[b] or (rank[a] == rank[b] and cd[a] > cd[b])) else P_indices[b]

            a2, b2 = np.random.choice(N, 2, replace=False)
            p2 = P_indices[a2] if (rank[a2] < rank[b2] or (rank[a2] == rank[b2] and cd[a2] > cd[b2])) else P_indices[b2]

            p1_set = set(int(x) for x in p1)
            p2_set = set(int(x) for x in p2)

            # ── 交叉：交换各自独有的特征 ──────────────────────────
            if np.random.rand() < pc and p1_set != p2_set:
                only_p1 = list(p1_set - p2_set)
                only_p2 = list(p2_set - p1_set)
                common = list(p1_set & p2_set)
                # 随机交换部分独有特征
                if only_p1 and only_p2:
                    n_swap = min(len(only_p1), len(only_p2))
                    if n_swap > 1:
                        n_swap = np.random.randint(1, n_swap + 1)
                    swap_1 = np.random.choice(only_p1, n_swap, replace=False).tolist()
                    swap_2 = np.random.choice(only_p2, min(n_swap, len(only_p2)), replace=False).tolist()
                    child_set = set(common + swap_2 + [x for x in only_p1 if x not in swap_1])
                else:
                    child_set = p1_set | p2_set
                child = list(child_set)
            else:
                child = list(p1_set)

            # ── 变异：添加/删除特征 ───────────────────────────────
            if np.random.rand() < pm_add:
                avail = list(set(range(dim)) - set(int(x) for x in child))
                if avail:
                    n_add = min(50, max(1, int(dim * 0.005)))  # 上限 50
                    child += np.random.choice(avail, min(n_add, len(avail)), replace=False).tolist()

            if np.random.rand() < pm_del and len(child) > 3:
                n_del = max(1, len(child) // 10)
                to_remove = np.random.choice(child, min(n_del, len(child) - 3), replace=False)
                child = [x for x in child if x not in to_remove]

            child = _ensure_min_features(child, dim, min_f=3)
            Q_indices.append(child)
            mask = _list_to_mask(child, dim)
            Q_fit[i, 0] = jFitness(X, y, mask, opts)
            Q_fit[i, 1] = len(child) / dim

        # ── 合并 + 精英选择 ──────────────────────────────────────
        R_indices = P_indices + Q_indices
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

        P_indices = [R_indices[s] for s in selected]
        P_fit = R_fit[selected].copy()
        curve[t] = np.min(P_fit[:, 0])

    # ── 最终选择 ──────────────────────────────────────────────────
    best_idx = np.argmin(P_fit[:, 0])
    Gbest = _list_to_mask(P_indices[best_idx], dim)

    return {
        "fitG": float(P_fit[best_idx, 0]),
        "nf": int(Gbest.sum()),
        "curve": curve,
        "nhd_curve": np.zeros(T_gens + 1),
    }
