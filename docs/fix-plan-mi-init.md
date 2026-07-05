# KDS-EL 冷启动修复方案

> 2026-07-03

---

## 一、问题诊断

### 现象
KDS_EL_KER / KDS_EL 在 Adenoma（7458 特征）上 10 次独立运行中，约 40%-50% 的 run 崩溃：
- 选中 2500+ 特征（SR > 33%）
- 准确率仅 ~0.94
- 其中不少 `Best_Iter = 1`（第一轮后再无改进）

### 根因：知识权重冷启动

```
            weight = zeros(dim)        ← 全零
                    ↓
        知识引导子群用 prob=0.5 均匀随机采样
                    ↓
        前几轮碰不到好解 → 权重永远累积不到正确方向
                    ↓
        40%-50% 概率陷入不可逆的差稳态
```

MEL、KER、KDS_EL 共享同一个权重矩阵初始化方式（全零），所以三个方法都有这个问题。

### 已完成的修复（部分有效）

| 修复 | 效果 |
|------|------|
| 权重更新移到池选择之前 | 修复错位比较，权重不被污染 |
| 精英保护（N//4 强制存活） | 消除 Best_Iter=1 崩溃 |

-- 崩溃率从 5/10 降到 2/10，但仍有 40% 跑出中等偏差结果。

---

## 二、文献调研

### 搜到的三篇 2024-2025 顶刊论文，全部用同一个思路

#### 1. fMOPSO-FS（Han et al., 2024, *Neural Processing Letters*）
**策略**：一半粒子用互信息（MI）引导初始化，一半随机。

> "This brings the initial population closer to the true Pareto front, accelerating convergence."

具体做法：
- 计算每个特征的 MI(feature, label)
- 高 MI 特征编码区间偏向 [0.6, 1]（高概率被选）
- 低 MI 特征编码区间偏向 [0, 0.4]（低概率被选）

#### 2. PPSO-EDT（Pan et al., 2024, *Int. J. Machine Learning & Cybernetics*）
**策略**：基于标签-特征相关性的概率初始化。

> "Fully utilizes the correlation between labels and features to accelerate population convergence."

应用在 12 个高维数据集上，取得最优分类性能和最短计算时间。

#### 3. SAR-MTPSO（Deng et al., 2025, *Swarm and Evolutionary Computation*）
**策略**：精英特征保留策略（EFP）— 重要特征在进化中受保护不被丢失。

> "Each individual particle preserves key features during the evolution process."

21 个 >1000D 数据集，17/21 上最优。

---

## 三、三篇论文的共同点

**不是改算法结构，而是给算法一个更好的起点。**

- 用互信息（MI）在初始化阶段给粒子位置一个先验偏好
- 高 MI 特征 → 初始位置接近 1 → 第一轮就被选中
- 第一轮就有好解 → 权重从第一轮开始正确累积
- 不再依赖纯运气

**互信息计算是一次性的（O(d)），算力开销可忽略。**

---

## 四、KDS-EL 的具体改法

### 改动范围

仅改动 `config.py` 或各算法的初始化部分。不影响算法迭代逻辑。

### 新增函数（utils.py）

```python
def compute_mi_scores(X, y):
    """计算每个特征与标签的互信息，归一化到 [0, 1]"""
    from sklearn.feature_selection import mutual_info_classif
    mi = mutual_info_classif(X, y, random_state=42)
    mi = np.nan_to_num(mi, nan=0.0)
    if mi.max() > mi.min():
        mi = (mi - mi.min()) / (mi.max() - mi.min())
    return mi
```

### 改动：种群初始化（kds_el.py / kds_el_ker.py / kds_el_drs.py / mel.py）

**现状**：
```python
P = np.random.uniform(lb, ub, (N, dim))
```

**改为**：
```python
mi = compute_mi_scores(X, y)

# 一半粒子：MI 引导（高 MI → 高概率接近 1，低 MI → 接近 0）
half = N // 2
for i in range(half):
    noise = np.random.normal(0, 0.1, dim)
    P[i] = np.clip(mi + noise, lb, ub)

# 另一半：均匀随机（保持多样性）
for i in range(half, N):
    P[i] = np.random.uniform(lb, ub, dim)
```

### 改动量估计

| 文件 | 改动 |
|------|------|
| `utils.py` | 新增 `compute_mi_scores()` 函数 |
| `kds_el.py` | 改 2 行（初始化） + 传入 `mi` |
| `kds_el_ker.py` | 改 2 行（初始化） |
| `kds_el_drs.py` | 改 2 行（初始化） |
| `mel.py` | 改 2 行（初始化） |

总计：~20 行改动，4 个方法受益。

---

## 五、预期效果

1. **崩溃率**：从 40% 降到接近 0%
2. **平均特征数**：大幅下降（好解从一开始就被找到）
3. **运行时间**：可能缩短（更早收敛到好解）
4. **所有四个方法**（MEL / DRS / KER / KDS_EL）同时受益

---

## 六、风险

- 互信息偏向过于强可能降低种群多样性 → 用 50/50 混合（一半 MI 引导 + 一半随机）来平衡
- MI 计算需要标签信息 → 在监督学习场景下天然可用，无额外风险
