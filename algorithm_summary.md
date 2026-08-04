# KDS-EL 算法框架与创新点完整总结
# Knowledge-guided Elite Refinement with Two-Phase Weight Scheduling

> 最后更新：2026-07-29（NoPool vs TwoPhase 全量 26DS 验证完成，TwoPhase 胜 16/25，确认为最终版本）
> 重大简化：移除 DRS + NHD + 池化，最终算法 = MEL + MI + KER + 两阶段权重调度 + 原地更新

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
         + MI 初始化 + 自适应重初始化          ← 知识引导生命周期
         + KER（Knowledge-guided Elite Refinement）← 在线知识累积
         + 两阶段权重调度（Two-Phase Weight Scheduling）← 探索-利用
         + 原地更新（1v1 替换，非池化竞争）

整体架构：
┌─────────────────────────────────────────────┐
│          MI 引导初始化 N=20 粒子              │
│  一半: clip(MI + noise, 0, 1) — 暖启动       │
│  一半: uniform(0, 1) — 保持多样性             │
├──────────────────┬──────────────────────────┤
│   Sub1（探索）    │      Sub2（知识采样）       │
│   三引导PSO速度   │   weight向量概率采样        │
│   ×10粒子        │   ×10粒子                  │
└──────────────────┴──────────────────────────┘
         ↓ 双群各自生成新解
┌─────────────────────────────────────────────┐
│          两阶段权重调度（环境选择）             │
│  Phase1 (前70%迭代): ws=[0.7, 0.3]          │
│    → 激进压缩特征，快速淘汰噪声特征             │
│  Phase2 (后30%迭代): ws=[0.95, 0.05]        │
│    → 精细调精度，保守保留                       │
└─────────────────────────────────────────────┘
         ↓ 1v1 原地更新 Pbest（优于池化 2N 竞争）
         ↓ 检测 improvement → 更新 weight
┌─────────────────────────────────────────────┐
│              KER（在线知识累积）               │
│  检测improvement事件 → 更新weight向量          │
│  weight[feat_added] += Δfitness             │
│  weight[feat_removed] -= Δfitness           │
│  → 定向精英bit-flip（top-k重要特征）           │
│  → k_e=3 精英解精化                           │
└─────────────────────────────────────────────┘
         ↓ 更新Gbest
         ↓ 若停滞 ≥20 代 → MI 重初始化下半种群
         ↓ 重复 T=100 次迭代
         ↓ 输出最优特征子集
```

**关键超参数**：
N=20, T=100, K_cv=5, k_nn=3, thres=0.6, 
Phase1: ws=[0.7, 0.3] (0~0.7T), Phase2: ws=[0.95, 0.05] (0.7T~T),
weight_decay=0.99, flip_frac=0.01, elite_k=3, rand_flip_p=0.10, stall_patience=20

**已移除的组件及原因**：
- ❌ DRS（多样性调节选择）：精度贡献仅 +0.07pp，统计不显著
- ❌ 2N 池化竞争：NoPool (1v1 原地更新) 精度更高且更简单
- ❌ NHD 多样性指标：MEL 从未测量，且与选择率机械耦合

---

## 三、核心机制详解

### 3.0 MI 引导初始化 + 自适应重初始化（知识引导生命周期）

**MI 引导初始化**：

$$P_i[0] = \begin{cases} \text{clip}(\text{MI} + \mathcal{N}(0, 0.1), 0, 1) & i < N/2 \quad \text{(暖启动)} \\ \mathcal{U}(0, 1) & i \geq N/2 \quad \text{(多样性保持)} \end{cases}$$

其中 $\text{MI}[j] = \text{MI}(X[:,j], y)$ 为特征 $j$ 与标签的归一化互信息。

**冷启动问题**：KER 的 weight 向量初始为全零，Sub2 前几轮只能用 prob=0.5 均匀随机采样。若初始种群碰不到好解，weight 永远无法正确累积，导致约 40%-50% 的运行崩溃（选中 2500+ 特征，Best_Iter=1 后再无改进）。

**自适应重初始化**：

$$\text{如果 } stall\_counter \geq patience(=20): \quad \text{重启 } \{P_i \mid i \in \text{bottom-half by fitness}\}$$

重启粒子使用 `clip(MI + noise, 0, 1)` 重新初始化（同 MI 初始化策略），而非纯随机重启。

**设计理念**：MI 知识在算法"启动"和"恢复"两个节点都被复用——不是一次性信息，而是贯穿全生命周期的引导信号。这一设计是 DRS、KER、Dual-Space 三个主创新点的**地基**。

**强度**：辅助级（supporting contribution）。不是独立的理论创新，而是工程上解决了冷启动和停滞问题。在论文中作为 "Design choice: knowledge-guided initialization and recovery" 呈现。

### 3.1 Sub1 — 三引导PSO探索

$$V_i^{t+1} = wV_i^t + c_1r_1(\text{Pbest}_i - P_i) + c_2r_2(\text{Gbest} - P_i) + c_3r_3(\text{Xsub\_best} - P_i)$$

- **第三引导项**：Sub2 的局部最优 Xsub\_best，实现跨子群知识传递
- w=0.9，c1=c2=c3=2.0，Vmax=0.5

### 3.2 Sub2 — 权重引导知识采样

$$P_i^{t+1}[j] = \begin{cases} 1 & \text{if } r_j < \text{prob}[j] \\ 0 & \text{otherwise} \end{cases}$$

$$\text{prob} = \frac{\max(\mathbf{w}, 0)}{\sum \max(\mathbf{w}, 0)}, \quad \text{若} \sum=0 \text{ 则 prob}=0.5$$

- weight 向量编码了历史改进经验，引导 Sub2 优先选择有效特征

### 3.3 两阶段权重调度（Two-Phase Weight Scheduling）

不同于传统固定权重（ws=[0.9, 0.1]），KDS-EL 采用两阶段权重调度：

$$\text{ws}(t) = \begin{cases} [0.7, 0.3] & t < 0.7T \quad \text{(Phase 1: 激进压缩)} \\ [0.95, 0.05] & t \geq 0.7T \quad \text{(Phase 2: 精细调精度)} \end{cases}$$

**设计理念**：
- Phase 1（前 70% 迭代）：给特征数项更大权重 → 快速淘汰噪声特征，缩小搜索空间
- Phase 2（后 30% 迭代）：给误差率更大权重 → 在已压缩的特征空间上精细调优分类精度
- 这一设计利用了 FS 问题的结构特性：噪声特征的排除是早期一次性工作，精度提升是后期持续工作

**消融证据**（2026-07-29, 25 数据集）：
- vs NoPool（固定 ws=[0.9, 0.1]）：ΔAcc=+1.07pp, ΔFeat=-46, 胜率 16/25

### 3.4 KER — 在线知识积累精英精化

**权重更新**（在 Pbest 更新之前执行）：
```
for i in range(N):
    if fit_new[i] < fitP[i]:           # 发现改进
        delta = fitP[i] - fit_new[i]   # 改进量
        changed = XOR(new_mask, old_mask)
        weight[changed & (new==1)] += delta   # 新增特征：权重+
        weight[changed & (new==0)] -= delta   # 移除特征：权重-
```

**精英扰动**（每轮 k_e=3 个精英解，flip_count = max(1, int(0.01 × d))）：
- 以 rand_flip_p=0.10 概率随机翻转（保证遍历性）
- 否则定向翻转 weight 得分最高的位

**Design Observation（遍历性说明）**：由于 rand_flip_p=0.10 > 0，任意二进制掩码都有正概率被探索。

**消融证据**（25 数据集）：
- KER 单独 +4.68pp over MEL，+0.79pp over MEL+MI

---

### 3.5 原地更新（In-place Update）

新解与对应粒子的 Pbest 做 1v1 比较，直接替换：

```
if fit(new) < fit(Pbest[i]):
    Pbest[i] = new
```

而非池化方案中的 2N 竞争（合并新旧种群 → 选出 Top N）：
- 原地更新更简单、更快
- 消融证据：NoPool Acc 0.9851 > KER (含池化) 0.9821 (9 数据集)

---

## 四、消融链路与贡献分解

### 四变体消融链

```
MEL（随机初始化）
  → MEL+MI（MI 引导初始化 + 自适应重初始化）
  → KDS_EL_NoPool（+ KER + 原地更新，固定 ws=[0.9, 0.1]）
  → KDS_EL_TwoPhase（+ 两阶段权重调度 ws=[0.7,0.3]→[0.95,0.05]）= KDS-EL 最终版
```

**贡献分解**：

| 步骤 | ΔAcc | 贡献来源 |
|:--|:--|:--|
| MEL → MEL+MI | +3.89pp | MI 初始化 + 自适应重初始化（地基） |
| MEL+MI → NoPool | +1.42pp | KER 在线知识累积 + 原地更新 |
| NoPool → TwoPhase | **+1.07pp** | **两阶段权重调度** |
| MEL → TwoPhase (总计) | **+6.38pp** | 以上三者累积 |

**三维综合优势**（25 数据集，CNS 排除）：

| 方法 | Acc | Feat | Time | NHD |
|:--|:--|:--|:--|:--|
| MEL | 0.8803 | ~2440 | 175s | 0.000 |
| MEL+MI | 0.9192 | 300.6 | — | 0.000 |
| KDS_EL_NoPool | 0.9334 | 152.8 | 64.1s | 0.000 |
| **KDS_EL_TwoPhase** | **0.9442** | **107.1** | **60.5s** | 0.000 |

> 注：TwoPhase 比 NoPool 精度更高、特征更少、速度更快 — 三维同步提升。
>
> 所有变体 NHD 均为 0（已移除 DRS），NHD 指标仅在前文历史数据中出现，不再作为评估指标。
>
> ---
>
> ## 五、变体命名对照

| CSV版本名 | 图表显示名 | 含义 | 两阶段调度 |
|---|---|---|---|
| MEL | MEL (Baseline) | 双子群PSO，随机初始化 | ✗ |
| MEL_MI | MEL+MI | + MI 初始化 + 自适应重初始化 | ✗ |
| KDS_EL_NoPool | KDS-EL/NoPool | + KER + 原地更新，固定 ws=[0.9,0.1] | ✗ |
| KDS_EL_TwoPhase | **KDS-EL (Proposed)** | + 两阶段权重调度 ws=[0.7,0.3]→[0.95,0.05] | ✓ |

> 所有 KDS-EL 变体共享 MI 引导初始化 + 自适应重初始化 + 原地更新设计。

---

## 六、创新点总结

### 创新点1：KER — improvement-feedback 在线知识学习（高）

**现状**：IGPSO 预训练 MLP（一次性），FWPSO 即时权重更新（只利用当前步），其他方法改进信号完全丢弃。

**本文**：跨迭代累积所有改进事件，weight 向量是整个搜索历史的压缩知识表示，无需额外 fitness 评估，自适应更新。

**证据**：KER 单独 +4.68pp over MEL（25 数据集），weight 向量无需预训练即可准确识别重要特征。

### 创新点2：两阶段权重调度（中高）

**现状**：所有 FS 方法使用固定目标权重（通常 ws=[0.9, 0.1]），未考虑搜索阶段的特性变化。

**本文**：Phase1 (前70%迭代) ws=[0.7,0.3] 激进压缩 → Phase2 (后30%迭代) ws=[0.95,0.05] 精细调精度。利用 FS 问题的结构特性——噪声特征排除是早期一次性工作，精度提升是后期精细化工作。

**证据**：TwoPhase vs NoPool (固定 ws) ΔAcc=+1.07pp, ΔFeat=-46, 胜率 16/25。最大收益在困难数据集：ALL2 (+4.42pp), T1D (+3.66pp), ALL3 (+3.16pp)。

### 创新点 0：MI 引导初始化 + 自适应重初始化（辅助级）

- MI 引导初始化参考了 fMOPSO-FS (Han et al., 2024)，**不是本文首创**
- 本文贡献：将 MI 初始化 + 自适应 MI 重初始化组合进框架，使 MI 知识在全生命周期持续发挥作用
- 是主创新点的**支撑性设计**——没有它，KER 的 weight 冷启动会导致约 40% 运行崩溃

### 已废弃创新方向

- **DRS（多样性调节选择）**：精度贡献仅 +0.07pp（噪声级），已从最终版本移除
- **NHD 多样性指标**：不适合跨方法公平比较，不再作为评估指标
- **Dual-Space 框架**：随着 DRS 移除而不再成立

---

## 七、SOTA 对比数据（来自 2026-07-01~07 实验批次，旧版 KDS-EL 含 DRS）

> ⚠️ **数据版本说明**：以下 SOTA/MOFS 对比数据来自旧版实验（`formal_experiment_20260701_094943/` 等），其中 KDS_EL/KDS_EL_KER/KDS_EL_DRS 为**含 DRS 和池化的旧版本**。新版简化 KDS-EL (TwoPhase, 无 DRS 无池化) 的全量数据见上方 §3.3 和 §四。
> 
> SOTA 对比方法 (FWPSO, PSO-CSM, SaWDE, BPSO, IGPSO) 和 MOFS 方法的数据仍然有效，可作为 KDS-EL 框架整体性能参考。

**实验规模**：20 数据集（d∈[500, 54675]，n∈[36, 2600]）× 15 方法 × 10 runs

### 7.1 数据集（20 个）

`ALL1`, `ALL4`, `ALL_AML`, `Adenoma`, `BASEHOCK`, `COIL20`, `Colon`, `DLBCL`, `Gastric`, `Gastric1`, `Gastric2`, `ISOLET`, `Leukaemia`, `Lymphoma`, `Myeloma`, `PCMAC`, `Prostate`, `SRBCT`, `T1D`, `madelon`

### 7.2 15 个方法

| 类别 | 方法 | 说明 |
|------|------|------|
| **本文** | KDS_EL (旧版含DRS+池化) | 旧版完整框架 |
| 消融 | KDS_EL_DRS, KDS_EL_KER, MEL | 旧版模块贡献验证 |
| SOTA 单目标 | BPSO, SaWDE, FWPSO, PSO-CSM, IGPSO | 5 个单目标 EC 方法 |
| MOFS 经典 | NSGA-II-FS (Pareto), MOPSO-FS (PSO), MOEA-D-FS (分解) | 三种主流 MOFS 范式 |
| MOFS 近年 | VGS-MOEA (变长), fMOPSO-FS (PSO+MI), W-MOPSO-FS (混合) | MOFS 前沿方法 |

> 🆕 新版简化 KDS-EL (KDS_EL_TwoPhase, 无 DRS 无池化) 数据见 `output/formal_experiment_final/`，25 数据集 Acc=0.9442, Feat=107.1。

### 7.4 14 定长方法完整排名 (Proposed = KDS_EL_TwoPhase)

> VGS-MOEA (变长, Acc=0.9463, Feat=51) 不进入主表——不同赛道。在 Related Work 作为变长 MOFS 代表作介绍。

| 排名 | 方法 | True Acc | Feat | Time(s) | 类别 |
|:----:|------|----------|------|---------|------|
| **1** | **KDS-EL (Proposed)** | **0.9442** | **107** | **61** | **本文** |
| 2 | KDS-EL/NoPool | 0.9334 | 153 | 64 | 消融基线 |
| 3 | MEL+MI | 0.9192 | 301 | 66 | 消融对照 |
| 4 | FWPSO | 0.9177 | 1069 | 50 | SOTA #1 |
| 5 | W-MOPSO-FS | 0.9132 | 2960 | 110 | MOFS #1 |
| 6 | fMOPSO-FS | 0.9110 | 3007 | 120 | MOFS |
| 7 | NSGA-II-FS | 0.9064 | 4818 | 136 | MOFS |
| 8 | MOEA-D-FS | 0.9041 | 4937 | 138 | MOFS |
| 9 | PSO_CSM | 0.9021 | 1559 | 122 | SOTA |
| 10 | MOPSO-FS | 0.9009 | 5263 | 143 | MOFS |
| 11 | SaWDE | 0.8944 | 3521 | 110 | SOTA |
| 12 | IGPSO | 0.8839 | 2538 | 136 | SOTA |
| 13 | MEL | 0.8803 | 2436 | 192 | 基线 |
| 14 | BPSO | 0.8698 | 5297 | 146 | SOTA |

### 7.5 KDS-EL (Proposed) vs 各定长方法 Win/Loss

| vs 方法 | Win | Tie | Loss | D-Acc | 类别 |
|---------|-----|-----|------|------|------|
| MEL | 25 | 0 | 0 | **+6.39pp** | 基线 |
| BPSO | 20 | 0 | 0 | **+8.75pp** | SOTA |
| PSO_CSM | 20 | 0 | 0 | **+5.52pp** | SOTA |
| IGPSO | 20 | 0 | 0 | **+7.34pp** | SOTA |
| SaWDE | 19 | 1 | 0 | **+6.30pp** | SOTA |
| FWPSO | 20 | 0 | 0 | **+3.96pp** | SOTA |
| MEL+MI | 24 | 1 | 0 | **+2.49pp** | 消融 |
| KDS-EL/NoPool | 16 | 8 | 1 | **+1.07pp** | 消融 |
| MOPSO-FS | 18 | 1 | 1 | +5.65pp | MOFS |
| MOEA-D-FS | 17 | 0 | 3 | +5.32pp | MOFS |
| fMOPSO-FS | 17 | 1 | 2 | +4.64pp | MOFS |
| NSGA-II-FS | 16 | 1 | 3 | +5.09pp | MOFS |
| W-MOPSO-FS | 17 | 1 | 2 | +4.42pp | MOFS |

> 对所有定长方法胜率 >= 80%。

### 7.6 三类 MOFS 代差

| 代 | 方法 | True Acc | Feat | 特点 |
|----|------|-----|------|------|
| 经典 (2002-2007) | NSGA-II-FS, MOPSO-FS, MOEA-D-FS | 0.901-0.906 | 4800-5300 | 选 ~40% 特征 |
| 混合 (近年) | fMOPSO-FS, W-MOPSO-FS | 0.911-0.913 | 2960-3010 | +0.7pp Acc，-40% 特征 |
| 变长 (2021) | VGS-MOEA | **0.946** | **51** | +3.3pp Acc，-98% 特征 |

### 7.7 PCMAC — 三模块协同最强证据

| 指标 | 数值 |
|------|------|
| KDS_EL Acc | **0.8478**（最强 SOTA SaWDE = 0.8256） |
| Δtotal (vs MEL 0.7870) | **+0.0608**（25 数据集中第 4 大） |
| ΔDRS (vs MEL) | +0.0221 |
| ΔKER (vs MEL) | +0.0379 |
| vs DRS Wilcoxon | p=0.002 |
| vs KER Wilcoxon | p=0.021 |

**PCMAC 是唯一同时满足 Δtotal > 0.06 + 同时显著优于两个变体的数据集**。

---

## 八、与同类定长方法的本质区别

| 方法 | 知识引导 | 权重调度 | 更新方式 | 输出 |
|---|---|---|---|---|
| BPSO/SaWDE/FWPSO | 无 | 无 | — | 单解 |
| IGPSO | MLP预训练（一次性） | 无 | — | 单解 |
| PSO-CSM | 综合评分（即时） | 无 | — | 单解 |
| 经典 MOFS (NSGA-II/MOPSO/MOEA-D) | 无 | 无 | Pareto 选择 | Pareto前沿 |
| 混合 MOFS (fMOPSO/W-MOPSO) | MI 引导（一次性） | 无 | Pareto 选择 | Pareto前沿 |
| **KDS-EL** | **KER（累积，在线学习）** | **两阶段权重调度** | **原地更新** | **单解** |

> **VGS-MOEA (变长编码 + Pareto 前沿)** 不在此表——编码方式和输出类型均不同。在 Related Work 作为变长 MOFS 代表作单独介绍。
>
> KDS-EL 是唯一同时具备：在线知识累积 + 自适应阶段调度 + 简单原地更新 的定长单解框架。

### 7.7（旧版）PCMAC — 三模块协同最强证据

> ⚠️ 以下数据来自旧版含 DRS 的实验，仅保留作为历史参考。

| 指标 | 数值 |
|------|------|
| KDS_EL Acc | **0.8478**（最强 SOTA SaWDE = 0.8256） |
| Δtotal (vs MEL 0.7870) | **+0.0608**（25 数据集中第 4 大） |

KDS-EL 是唯一同时具备：持续结构多样性维护 + 在线知识积累 + 单解输出 的框架。与传统 MOFS 的本质区别：NHD 是辅助目标（优化搜索过程），最终输出单一最优解而非 Pareto 前沿。

---

## 九、图表规划（9 Tables + 12 Figures = 21 个）

### Tables（9 个）

| # | 内容 | 状态 |
|---|------|:----:|
| T1 | 近 5 年 PSO-FS 文献对比 | ⚠ 需新写 |
| T2 | 数据集描述（20 个） | ⚠ 需新写 |
| T3 | 方法参数设置 | ⚠ 需新写 |
| T4 | **主表**准确率 Mean ± Std（10 方法 × 20 数据集） | 🔄 需重新生成 |
| T5 | **主表**特征数 Mean（10 方法 × 20 数据集） | 🔄 需重新生成 |
| T6 | Wilcoxon p 值矩阵（10 方法 × 20 数据集） | 🔄 需重新生成 |
| T7 | 消融实验 ACC + Features（5 变体 × 25 数据集，CNS 排除） | ✅ 已生成 |
| T8 | MOFS 六方法单独对比 | 🆕 新增 |
| T9 | 时间复杂度 O() | ⚠ 需新写 |

**主表 10 方法**：KDS_EL + KDS_EL_KER + KDS_EL_DRS + MEL + FWPSO + PSO-CSM + SaWDE + VGS-MOEA + W-MOPSO-FS + NSGA-II-FS（完整 15 方法放附录）

### Figures（12 个）

| # | 内容 | 状态 |
|---|------|:----:|
| F1-F3 | 框架图 / DRS 示意图 / KER 示意图 | △ 需新画 |
| F4 | 准确率柱状图（10 方法 × 20 数据集） | 🔄 需重新生成 |
| F5 | 特征数柱状图（对数轴，10 方法 × 20 数据集） | 🔄 需重新生成 |
| F6 | 消融双面板（5 变体 × 25 数据集，CNS 排除） | ✅ 已生成 |
| F7 | 稳定性箱线图（10 方法 × 20 数据集） | 🔄 需重新生成 |
| F8 | 收敛曲线（10 方法 × 20 数据集） | 🔄 需重新生成 |
| F9 | NHD 多样性曲线（KDS_EL + DRS × 20 数据集） | 🔄 需重新生成 |
| F10 | Wilcoxon 热图（10 方法 × 20 数据集） | 🔄 需重新生成 |
| F11 | 运行时间对比（对数轴，10 方法 × 20 数据集） | 🔄 需重新生成 |
| F12 | 精度-特征-时间气泡图（10 方法 × 20 数据集） | 🔄 需重新生成 |

---

## 十、实验数据源

| 实验 | 目录 | 方法 | 数据集 | 状态 |
|------|------|------|:---:|:---:|
| SOTA | `output/formal_experiment_20260701_094943/` | BPSO, FWPSO, IGPSO, PSO_CSM, SaWDE | 20 | ✅ |
| 消融 V1（仅 MEL） | `output/formal_experiment_20260628_205157/` | MEL | 26→筛选 20 | ✅ |
| 消融 V2 | `output/formal_experiment_20260702_145828/` | KDS_EL, KDS_EL_DRS, KDS_EL_KER | 26→筛选 20 | ✅ |
| MOFS | `output/formal_experiment_20260707_142018/` | NSGA-II-FS, MOPSO-FS, MOEA-D-FS, fMOPSO-FS, VGS-MOEA, W-MOPSO-FS | 20 | ✅ |

---

## 十一、论文叙事建议

**核心定位**："Dual-Space" 框架 —— 多样性正则化单解框架（diversity-regularized single-solution framework）

- 传统 SO-FS：单空间，无多样性维护
- 传统 MO-FS：双目标优化，输出 Pareto 前沿给决策者
- **KDS-EL**：双空间协同，NHD 作为搜索辅助目标，输出单一最优解

**核心叙事线**：
1. 现有方法存在结构空间盲点（NHD → 0）和知识浪费两个结构性缺陷
2. DRS 首次将 NHD 升格为 Pareto 选择目标（结构空间）
3. KER 首次实现跨迭代 improvement-feedback 在线知识积累（适应度空间）
4. 双空间协同：在困难数据集（ALL2/ALL3/Stroke/PCMAC）上互相纠错，在简单数据集上至少不差
5. 15 方法 × 20 数据集：KDS_EL 排名 #2（仅次 VGS-MOEA），Friedman rank 3.0，对所有非 MOFS 方法胜率 ≥ 90%

**与 VGS-MOEA 的关系**：VGS-MOEA 是 MOFS 方法，KDS-EL 是单解输出框架，两者不是直接竞争关系。VGS-MOEA 领先证明了可变长度编码的优势（极小特征子集），KDS-EL 领先于所有其他 13 个方法证明了双空间框架的有效性。
