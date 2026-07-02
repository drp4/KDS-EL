# KDS-EL 算法框架与创新点完整总结
# Knowledge-guided Dual-Space Evolutionary Learning

---

## 一、问题定义

高维生物信息学特征选择目标：从 $d$ 个特征（$d \gg n$）中选出最优子集 $\mathbf{x} \in \{0,1\}^d$，

$$\min_{\mathbf{x}} f(\mathbf{x}) = 0.9 \times \text{ErrorRate}(\mathbf{x}) + 0.1 \times \frac{|\mathbf{x}|}{d}$$

其中 ErrorRate 由 KNN（k=3）5折交叉验证计算。

**现有方法的两个结构性缺陷：**

1. **结构空间盲点**：所有方法只在 fitness 空间优化，忽视二进制解空间的拓扑结构。高维下种群自然趋向同质化（NHD → 0），陷入局部最优。

2. **知识浪费**：每次发现更优子集后，"哪些特征位翻转带来了提升"的信息被丢弃，下一轮仍从头探索。

---

## 二、算法总框架

```
KDS-EL = 双子群PSO骨架（继承自MEL）
         + DRS（Diversity-regulated Selection）  ← 结构空间
         + KER（Knowledge-guided Elite Refinement）← 适应度空间

整体架构：
┌─────────────────────────────────────────────┐
│              初始化 N=20 粒子                 │
├──────────────────┬──────────────────────────┤
│   Sub1（探索）    │      Sub2（知识采样）       │
│   三引导PSO速度   │   weight向量概率采样        │
│   ×10粒子        │   ×10粒子                  │
└──────────────────┴──────────────────────────┘
         ↓ 合并为 Pool（2N=40个候选解）
┌─────────────────────────────────────────────┐
│              DRS（结构空间调节）               │
│  目标1: min fitness                          │
│  目标2: max NHD（种群结构多样性）              │
│  → NSGA-II Pareto排序 + 自适应拥挤距离         │
│  → 选出N=20个解进入下一代                      │
└─────────────────────────────────────────────┘
         ↓ 更新Pbest（先更新weight）
┌─────────────────────────────────────────────┐
│              KER（适应度空间精化）             │
│  检测improvement事件 → 更新weight向量          │
│  weight[feat_added] += Δfitness             │
│  weight[feat_removed] -= Δfitness           │
│  → 定向精英bit-flip（top-k重要特征）           │
│  → k_e=3 精英解精化                           │
└─────────────────────────────────────────────┘
         ↓ 更新Gbest
         ↓ 重复 T=100 次迭代
         ↓ 输出最优特征子集
```

**关键超参数**：
N=20, T=100, K_cv=5, k_nn=3, thres=0.6, ws=[0.9,0.1],
weight_decay=0.99, flip_frac=0.01, elite_k=3, rand_flip_p=0.10

---

## 三、核心机制详解

### 3.1 Sub1 — 三引导PSO探索

$$V_i^{t+1} = wV_i^t + c_1r_1(\text{Pbest}_i - P_i) + c_2r_2(\text{Gbest} - P_i) + c_3r_3(\text{Xsub\_best} - P_i)$$

- **第三引导项**：Sub2 的局部最优 Xsub\_best，实现跨子群知识传递
- w=0.9，c1=c2=c3=2.0，Vmax=0.5

### 3.2 Sub2 — 权重引导知识采样

$$P_i^{t+1}[j] = \begin{cases} 1 & \text{if } r_j < \text{prob}[j] \\ 0 & \text{otherwise} \end{cases}$$

$$\text{prob} = \frac{\max(\mathbf{w}, 0)}{\sum \max(\mathbf{w}, 0)}, \quad \text{若} \sum=0 \text{ 则 prob}=0.5$$

- weight 向量编码了历史改进经验，引导 Sub2 优先选择有效特征
- 后备概率 0.5 保证权重失效时正常工作

### 3.3 DRS — 双目标 Pareto 选择（结构空间）

**Pool 构建**：$\text{Pool} = \text{Pbest} \cup P_{\text{new}}$（大小 2N）

**两个目标**：
$$\text{obj}_1 = f(\mathbf{x}), \quad \text{obj}_2 = -\text{NHD}(\mathbf{x}, \text{Pool})$$

**NHD 计算**（向量化，Jaccard距离变体）：
$$\text{NHD}(x_i, x_j) = \frac{|x_i \oplus x_j|}{\max(|x_i|+|x_j|-|x_i \wedge x_j|, 1)}$$

其中分母为Jaccard并集大小 $|x_i \cup x_j| = |x_i|+|x_j|-|x_i \wedge x_j|$

**选择过程**：
1. NSGA-II 非支配排序（fast\_nds）
2. 拥挤距离计算（crowding\_dist）
3. 自适应权重调度：
   $$\alpha_{cd}(t) = \left(\frac{t}{T}\right)^2$$
   早期（t小）：多样性优先；后期（t大）：精度优先
4. 综合得分：$\text{score} = \alpha_{cd} \cdot CD_{norm} + (1-\alpha_{cd}) \cdot NHD_{norm}$

**Proposition 1（多样性下界）**：对 t<T，DRS 保证选出的种群 NHD>0。

### 3.4 KER — 在线知识积累精英精化（适应度空间）

**权重更新**（在 Pbest 更新之前执行）：
```
for i in range(N):
    if fit_new[i] < fitP[i]:           # 发现改进
        delta = fitP[i] - fit_new[i]   # 改进量
        changed = XOR(new_mask, old_mask)
        weight[changed & (new==1)] += delta   # 新增特征：权重+
        weight[changed & (new==0)] -= delta   # 移除特征：权重-
```

**精英扰动**（每轮 k_e=3 个精英解）：
```
with prob rand_flip_p=0.10:
    随机选 flip_count 个位翻转（保证遍历性）
else:
    score = weight*(1-elite) - weight*elite + noise
    翻转 top flip_count 个得分最高的位
```

flip_count = max(1, int(0.01 × d))

**Proposition 2（遍历性）**：由于 rand_flip_p=0.10 > 0，任意二进制掩码都有正概率被探索。

---

## 四、双空间协同机制

```
DRS（结构空间）← → KER（适应度空间）
      ↑                    ↑
  维持种群多样性         定向精英扰动
      |                    |
  → 为KER提供         → 产生高质量多样候选
    异质改进信号           丰富DRS选择池
```

**正向协同**：DRS 维持的结构多样性 → KER 接收到来自不同方向的改进信号 → weight 向量更准确 → KER 精英扰动更有效 → 高质量多样解丰富 DRS Pool

**消融证据**：16/17 数据集 $\Delta_{Full} > \Delta_{DRS} + \Delta_{KER}$（正协同），mean synergy = +3.02pp

---

## 五、四个变体与消融设计

| CSV版本名 | 图表显示名 | 含义 |
|---|---|---|
| MEL | MEL (Baseline) | 双子群PSO，无DRS无KER |
| MEL_NHD | KDS-EL/DRS | 含DRS，无KER |
| MEL_KGEF_noNHD | KDS-EL/KER | 含KER，无DRS |
| MEL_KGEF | **KDS-EL (Proposed)** | 完整双空间框架 |

---

## 六、创新点总结

### 创新点1：DRS — NHD 首次作为第一类 Pareto 选择目标

**现状**：所有 wrapper-based FS 方法中，NHD 仅作为事后诊断指标，从未进入选择算子。

**本文**：将 NHD 与 fitness 并列为两个 Pareto 目标，直接嵌入环境选择过程，提供可证明的多样性下界（Proposition 1）。

**证据**：
- 种群平均 NHD：MEL=0.000 → KDS-EL/DRS=0.417 → KDS-EL (Proposed)=0.350
- 特征数 vs MEL baseline：平均减少 **83.6%**（2989→491）

**强度**：中等偏高。机制新颖，有数学形式化，有实验验证。

---

### 创新点2：KER — improvement-feedback 在线知识学习

**现状**：
- IGPSO：预训练 MLP 估计特征重要性（一次性，非自适应）
- FWPSO：即时权重更新（只利用当前步信息）
- 其他方法：改进信号完全丢弃

**本文**：跨迭代累积所有改进事件，weight 向量是整个搜索历史的压缩知识表示，无需额外 fitness 评估，自适应更新。

**证据**：
- KER 单独在 13/17 数据集优于 MEL baseline（KDS-EL/KER avg 90.92% vs MEL 89.02%）
- KER 平均准确率提升 vs MEL：+1.90pp（KDS-EL/KER 90.92% vs MEL 89.02%）

**强度**：中等。思路类似强化学习 reward 累积，在 FS 领域是新的组合。

---

### 创新点3：Dual-Space 协同框架

**现状**：现有方法要么只在 fitness 空间优化（单空间），要么做传统多目标 FS（输出 Pareto 前沿解集，面向决策者）。

**本文**：提出第三种范式——双空间协同框架：
- fitness 空间：KER 驱动精准收敛
- structural 空间：DRS 驱动多样探索
- 最终输出单一最优解（不是 Pareto 前沿）
- NHD 是"辅助目标"（auxiliary objective），不是用户级 trade-off 目标

**证据**：
- 16/17 正协同（仅Colon除外，KER单独已贡献+0.070），mean synergy +3.02pp
- KER 单独版本从未超过完整框架（外部方法比较层面，0/17）

**强度**：高。消融设计严格，协同证据极强，17个数据集覆盖广泛，是整篇论文最强的卖点。

---

## 七、整体性能数据

**实验规模**：17 数据集（d∈[500, 54675]，n∈[36, 2500]）× 9 方法 × 10 runs

### 7.1 数据集
ALL1(36×12627), ALL4(102×12628), ALL_AML(72×7129), Adenoma(36×7458),
Colon(62×2000), DLBCL(77×7129), Gastric(×22644), Gastric1(×22284),
Gastric2(×22285), ISOLET(×617), Leukaemia(72×7129), Lymphoma(96×4026),
Myeloma(×12628), Prostate(×12628), SRBCT(×2308), T1D(×54675), madelon(×500)

### 7.2 9个对比方法
BPSO, SaWDE, FWPSO, MEL (Baseline), KDS-EL/DRS, KDS-EL/KER, KDS-EL (Proposed), PSO-CSM, IGPSO

### 7.3 关键统计

| 指标 | 数值 |
|---|---|
| Friedman χ² | 94.23 |
| Friedman p | 6.43×10⁻¹⁷ |
| KDS-EL avg rank | **1.059**（17×第1，0×第2）|
| KDS-EL avg accuracy | 93.95% |
| vs BPSO | 17/17 wins |
| vs SaWDE | 16/17 wins（ISOLET上SaWDE排名#1，KDS-EL排名#2）|
| vs FWPSO | 17/17 wins |
| vs PSO-CSM(2025) | 17/17 wins |
| vs IGPSO(2024) | 17/17 wins |
| vs MEL (Baseline) | 17/17 wins |
| KDS-EL avg features | 491（vs MEL 2989，**-83.6%**）|
| FWPSO avg rank | 2.588（第2名）|
| 正协同 | **16/17** 数据集（仅Colon为负协同）|
| 平均协同效应 | +3.02pp |
| 运行时间 | 115.4s（FWPSO 23.9s最快，MEL Baseline 167.8s）|
| KDS-EL 平均 NHD | 0.350（vs MEL 0.000，KDS-EL/DRS 0.417）|

### 7.4 数据集维度

新增数据集（相比旧版9数据集实验）：ALL1、Gastric、Gastric1、Gastric2、ISOLET、Myeloma、Prostate、SRBCT、T1D、madelon（共新增8个，移除CNS和Stroke）

---

## 八、与同类方法的本质区别

| 方法 | 多样性机制 | 知识机制 | 输出 |
|---|---|---|---|
| BPSO/SaWDE/FWPSO | 无（或随机） | 无 | 单解 |
| IGPSO | 无 | MLP预训练（一次性）| 单解 |
| PSO-CSM | 无 | 综合评分（即时）| 单解 |
| SAR-MTPSO | 无 | 跨任务知识迁移 | 双任务解 |
| 传统MOFS(NSGA-II) | 有 | 无 | **Pareto前沿** |
| **KDS-EL** | **DRS（持续，结构空间）** | **KER（累积，在线学习）** | **单解** |

KDS-EL 是唯一同时具备：持续结构多样性维护 + 在线知识积累 + 单解输出 的框架。
