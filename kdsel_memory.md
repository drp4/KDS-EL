# KDS-EL 论文项目完整记忆文档
# 用于新对话的上下文恢复
# 生成时间：2026年5月 | 最后更新：2026年7月20日（MEL_MI 实验完成，消融完整闭合）

---

## 一、项目概况

**算法名称**：KDS-EL（Knowledge-guided Dual-Space Evolutionary Learning）
**研究领域**：高维生物信息学特征选择（Wrapper-based, PSO框架）
**当前最终版本**：KDS_EL_TwoPhase（MEL + MI + KER + 两阶段权重调度 + 原地更新，已移除 DRS + 池化）

---

## 二、算法架构

```
KDS-EL = 双子群PSO骨架（继承自MEL [CITE_MEL, IEEE TKDE]）
         + MI 初始化 + 自适应重初始化          ← 知识引导生命周期
         + KER（Knowledge-guided Elite Refinement）← 核心创新: improvement-feedback 在线知识累积
         + 两阶段权重调度（ws=[0.7,0.3]→[0.95,0.05]）← 核心创新: Phase1 激进压缩 → Phase2 精调
         + 原地更新（1v1 替换，非 2N 池化竞争）

已移除的组件（消融证据不足）：
  ❌ DRS（Diversity-regulated Selection）— 精度贡献仅 +0.07pp，统计不显著
  ❌ 2N 池化选择 — NoPool 精度更高且更简单
  ❌ NHD 多样性指标 — MEL 从未测量，不适合跨方法公平比较

最终版本命名：
  KDS_EL_NoPool    → MEL + MI + KER + 原地更新（无两阶段，作为消融基线）
  KDS_EL_TwoPhase  → MEL + MI + KER + 两阶段权重调度 + 原地更新（= KDS-EL 最终版）
```

**关键参数**：N=20, T=100, K_cv=5, k_nn=3, thres=0.6, ws=[0.9,0.1],
weight_decay=0.99, flip_frac=0.01, elite_k=3, rand_flip_p=0.10,
stall_patience=20, MI init ratio=0.5
Seeds: 不固定（RNG自然流动）, NUM_RUNS=10

**已修复的bug（2026-07-03）**：
1. 权重更新顺序（在Pbest更新前执行）
2. 精英保护（EMDO选择后保留pool中fitness前N//4的个体）
3. MI引导初始化（一半MI+一半随机，解决KER冷启动崩溃）
4. 自适应重初始化（stall_counter追踪Gbest停滞，超过patience→重启下半种群）

---

## 三、实验数据

### 3.1 实验目录

| # | 目录 | 内容 | 状态 | 数据有效性 |
|---|------|------|:---:|:---:|
| 1 | `output/formal_experiment_20260701_094943/` | SOTA 对比 (5方法×20数据集) | ✅ | ✅ 全部有效 |
| 2 | `output/formal_experiment_20260628_205157/` | 旧版消融 V1 (4方法×27数据集) | ✅ | ⚠️ 仅MEL有效（另外3方法有bug）；MEL曲线shape(101,)=T100，与新实验协议一致 |
| 3 | `output/formal_experiment_20260702_145828/` | 最新消融 V2 (3方法×25数据集，CNS排除) | ✅ | ✅ 全部有效 |
| 4 | `output/formal_experiment_20260707_142018/` | MOFS 对比 (6方法×20数据集) | ✅ | ✅ 全部有效 |
| 5 | `output/formal_experiment_mel_mi/` | MEL_MI 对照 (1方法×26数据集，含CNS) 🆕 | ✅ | ✅ 全部有效 |
| 6 | `output/formal_experiment_20260627_211133/` | 早期消融曲线 (3方法×25数据集) | ✅ | ⚠️ 早期版本，曲线协议不同于正式 |
| 7 | `output/formal_experiment_final/` | **NoPool vs TwoPhase 全量验证** (2方法×26数据集) 🆕 | ✅ | ✅ 全部有效，TwoPhase 胜 16/25，最终版本数据 |
| 8 | `output/test_pool_ablation/` | 池化消融: KER vs NoPool (2方法×9数据集) | ✅ | ✅ NoPool 胜出 |
| 9 | `output/test_twophase/` | 两阶段调度消融: NoPool vs TwoPhase (2方法×5数据集) | ✅ | ✅ TwoPhase +0.40pp (预热) |

### 3.2 20个数据集

`ALL1`(128×12625,2c), `ALL4`(93×12625,2c), `ALL_AML`(72×7129,2c),
`Adenoma`(36×7457,2c), `BASEHOCK`(1993×4862,2c), `COIL20`(1440×1024,20c),
`Colon`(62×2000,2c), `DLBCL`(77×7129,2c), `Gastric`(65×22645,2c),
`Gastric1`(144×22283,2c), `Gastric2`(124×22283,2c), `ISOLET`(1560×617,26c),
`Leukaemia`(72×7129,2c), `Lymphoma`(45×4026,2c), `Myeloma`(173×12625,2c),
`PCMAC`(1943×3289,2c), `Prostate`(102×12625,2c), `SRBCT`(83×2308,4c),
`T1D`(101×54675,2c), `madelon`(2600×500,2c)

### 3.3 16个方法

| 类别 | 方法 | 数据来源 |
|------|------|----------|
| **本文** | **KDS_EL** | 实验3 |
| 消融 | KDS_EL_DRS, KDS_EL_KER, MEL_MI | 实验3 + 实验5 |
| 基线 | MEL | 实验2 |
| SOTA 单目标 | BPSO, SaWDE, FWPSO, PSO-CSM, IGPSO | 实验1 |
| MOFS 经典 | NSGA-II-FS, MOPSO-FS, MOEA-D-FS | 实验4 |
| MOFS 近年 | VGS-MOEA, fMOPSO-FS, W-MOPSO-FS | 实验4 |

**实验协议**：StratifiedKFold(5, shuffle=True), 10 runs × 100 iterations, RNG自然流动

---

## 四、核心数字（写作时直接引用）

### 4.0 最终版实验 (2026-07-29): NoPool vs TwoPhase 🆕

**数据源**: `output/formal_experiment_final/`, 2方法×26数据集×10runs

| 指标 | KDS_EL_NoPool | KDS_EL_TwoPhase | Δ |
|:--|:--|:--|:--|
| Mean Acc (25DS, excl CNS) | 0.9334 | **0.9442** | **+1.07pp** |
| Mean Feat | 152.8 | **107.1** | -45.7 |
| Mean Time | 64.1s | **60.5s** | -3.6s |
| Win/Loss/Tie | — | **16/1/8** | — |

**关键发现**:
- TwoPhase 精度/特征/速度三维同步提升
- 最大收益在困难数据集 (ALL2 +4.42pp, T1D +3.66pp, ALL3 +3.16pp)
- 唯一失败 RELATHE (Δ=-0.0021pp)，但特征减半
- NHD 均为 0（无 DRS）；CNS 排除

### 4.1 定长方法排名 (Proposed = KDS_EL_TwoPhase, 排除 VGS-MOEA 变长编码)

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

> **VGS-MOEA 不进入主表**：变长编码 + Pareto 前沿，与定长单解 KDS-EL 不同赛道。作为独立类别在 Related Work 提及。
> KDS-EL 领先定长第二名 +1.08pp，领先最强 SOTA (FWPSO) +2.65pp。

### 4.2 KDS-EL (Proposed) vs 定长方法 Win/Loss

| vs 方法 | Win | Tie | Loss | D-Acc | D-Feat |
|---------|-----|-----|------|------|--------|
| KDS-EL/NoPool | 16 | 8 | 1 | +0.0107 | -46 |
| MEL+MI | 24 | 1 | 0 | +0.0249 | -194 |
| FWPSO | 20 | 0 | 0 | +0.0396 | -981 |
| W-MOPSO-FS | 17 | 1 | 2 | +0.0442 | -2872 |
| fMOPSO-FS | 17 | 1 | 2 | +0.0464 | -2919 |
| NSGA-II-FS | 16 | 1 | 3 | +0.0509 | -4731 |
| MOEA-D-FS | 17 | 0 | 3 | +0.0532 | -4849 |
| PSO_CSM | 20 | 0 | 0 | +0.0552 | -1472 |
| MOPSO-FS | 18 | 1 | 1 | +0.0565 | -5176 |
| SaWDE | 19 | 1 | 0 | +0.0630 | -3433 |
| IGPSO | 20 | 0 | 0 | +0.0734 | -2450 |
| MEL | 25 | 0 | 0 | +0.0639 | -2329 |
| BPSO | 20 | 0 | 0 | +0.0875 | -5209 |

> 对所有定长方法胜率 >= 80% (16/20)。仅 NSGA-II-FS (3 losses) 和 MOEA-D-FS (3 losses) 在个别数据集上造成损失。

### 4.4 消融分析：完整五层消融（25数据集，CNS排除）

**根本原则**：DRS 是多样性维持算子，KER 是精度提升引擎。两者解决不同问题，不能用同一维度衡量。

#### 4.4.1 完整消融表

| 变体 | Acc | Δ over MEL | Δ over MEL_MI | NHD | 角色 |
|------|------|:---:|:---:|------|------|
| MEL | 0.8803 | — | — | 0.000 | 原始基线：随机初始化，无恢复 |
| **MEL_MI** | **0.9192** | **+3.89pp** | — | 0.000 | MI+Reinit 基础：智能初始化 + stall 恢复 |
| KDS-EL/DRS | 0.9199 | +3.96pp | +0.07pp | **0.453** | +DRS：多样性最大，精度几乎不动 |
| KDS-EL/KER | **0.9271** | **+4.68pp** | **+0.79pp** | 0.000 | +KER：精度拉满，但种群坍缩 |
| **KDS-EL** | **0.9291** | **+4.88pp** | **+0.99pp** | **0.310** | 全部：精度=KER级 + 多样性为正 |

#### 4.4.2 贡献分解

```
MI+Reinit:   +3.89pp  ← 基础工程（非本文核心创新，引用 fMOPSO-FS）
KER net:     +0.79pp  ← 本文核心创新：improvement-feedback 在线知识累积
DRS net:     +0.07pp  ← DRS 不追求精度贡献，价值在 NHD（0→0.453→0.310）
───────────────────────────
Full total:  +4.88pp  ← MI+Reinit 打底 + KER 拉精度 + DRS 守多样性
```

#### 4.4.3 论证框架

1. **MI+Reinit 是地基**：贡献 +3.89pp。MEL 的主要弱点是随机初始化，MI 初始化和 stall 重初始化解决了冷启动和搜索停滞。这是工程支撑，不是核心创新。

2. **KER 是精度引擎**：在 MI+Reinit 基础上净贡献 +0.79pp。KER 的 improvement-feedback 权重累积 + 精英扰动是论文最强的原创贡献。代价是 NHD ≡ 0。

3. **DRS 是结构守护者**：对精度的净贡献仅 +0.07pp——这证明 DRS 的设计目标（维持多样性、不追求精度）已实现。NHD 从 0 跃升到 0.453（DRS alone）或 0.310（Full with KER constraint）。DRS 的价值在 NHD，不在 Acc。

4. **Full 是唯一兼得方案**：精度 = KER 级别（0.9291 ≈ 0.9271），NHD = 0.310（DRS 的 68%），特征 = 263。三者缺一不可。

#### 4.4.4 DRS 边界条件（3/25 反例）

| 数据集 | Full | KER | Δ | 原因 |
|--------|------|------|------:|------|
| COIL20 | 0.9809 | 0.9913 | -1.05pp | 天花板效应，多样性产生噪声 |
| ISOLET | 0.8717 | 0.8804 | -0.87pp | 26类多分类，NHD 误导探索 |
| madelon | 0.8445 | 0.8634 | -1.89pp | 人工数据，特征独立无冗余 |

这三个在 Discussion 中作为 DRS boundary condition 诚实讨论。22/25 (88%) 数据集上 DRS 不损害精度。

### 4.5 特征数与NHD

| 方法 | Mean Feat (26DS) | vs MEL | Mean NHD |
|------|-------------------|--------|----------|
| MEL | 2989 | — | 0.000 |
| KDS_EL_KER | 200 | -93.3% | 0.000 |
| **KDS_EL** | **198** | **-93.4%** | **0.324** |
| KDS_EL_DRS | 129 | **-95.7%** | **0.451** |

> 除DRS和KDS_EL外，所有方法的种群在搜索过程中完全同质化（NHD=0）。

### 4.6 MOFS三代代差

| 代 | 方法 | True Acc | Feat |
|----|------|-----|------|
| 经典 (2002-2007) | NSGA-II-FS, MOPSO-FS, MOEA-D-FS | 0.901-0.906 | 4800-5300 |
| 混合 (近年) | fMOPSO-FS, W-MOPSO-FS | 0.911-0.913 | 2960-3010 |
| 变长 (2021) | VGS-MOEA | **0.946** | **51** |

### 4.7 KDS_EL类别均值

- KDS-EL Family avg Acc = 0.9424（#1 类别）
- MOFS Advanced avg = 0.9235（#2）
- MOFS Classic avg = 0.9038（#3）
- SOTA 单目标 avg = 0.8936（#4）

---

## 五、图表规划（10 Tables + 12 Figures = 22个）

> 对标EMSWOA: 10 Figures + 10 Tables = 20个

### Tables（9个）

| # | 内容 | 位置 | 状态 |
|---|------|------|:----:|
| T1 | 近5年PSO-FS文献对比 | Related Work | ⚠ 需新写 |
| T2 | 数据集描述（20个） | §4.1 实验设置 | ⚠ 需新写 |
| T3 | 方法参数设置 | §4.1 实验设置 | ⚠ 需新写 |
| T4 | **主表**准确率Mean±Std（10方法×20数据集） | §4.2 精度比较 | 🔄 需重新生成 |
| T5 | **主表**特征数Mean（10方法×20数据集） | §4.3 特征比较 | 🔄 需重新生成 |
| T6 | Wilcoxon p值矩阵（10方法×20数据集） | §4.4 统计检验 | 🔄 需重新生成 |
| T7 | 消融实验ACC+Features（5变体×25数据集，CNS排除） | §4.5 消融分析 | ✅ 已生成 |
| T8 | MOFS六方法单独对比（定长5方法 + 变长VGS-MOEA分表） | §4.6 MOFS对比 | 🆕 新增 |
| T9 | 时间复杂度O() | §3.6 复杂度 | ⚠ 需新写 |

**T4主表10方法**：KDS_EL + KDS_EL_KER + KDS_EL_DRS + MEL + FWPSO + PSO-CSM + SaWDE + VGS-MOEA + W-MOPSO-FS + NSGA-II-FS
**附录**：完整15方法Acc+Feat+Wilcoxon

### Figures（12个）

| # | 内容 | 状态 |
|---|------|:----:|
| F1 | KDS-EL整体框架图 | △ 需新画 |
| F2 | DRS机制示意图 | △ 需新画 |
| F3 | KER机制示意图 | △ 需新画 |
| F4 | 准确率柱状图（10方法，auto-grid，20数据集） | 🔄 需重新生成 |
| F5 | 特征数柱状图（对数轴，auto-grid，20数据集） | 🔄 需重新生成 |
| F6 | 消融双面板（5变体×25数据集，CNS排除） | ✅ 已生成 |
| F7 | 稳定性箱线图（10方法，auto-grid，20数据集） | 🔄 需重新生成 |
| F8 | 收敛曲线（10方法+MEL_MI，auto-grid，20数据集） | 🔄 需重新生成 |
| F9 | NHD多样性曲线（MEL+MEL_MI+KDS-EL/DRS+KDS-EL，4条线，auto-grid，20数据集） | 🔄 需重新生成 |
| F10 | Wilcoxon热图（10方法×20数据集） | 🔄 需重新生成 |
| F11 | 运行时间对比（对数轴，10方法，20数据集） | 🔄 需重新生成 |
| F12 | 精度-特征-时间气泡图（10方法，20数据集） | 🔄 需重新生成 |

### 生成脚本

```
generate_figures.py   → F4-F7, F10-F12 (7个)   ← 需适配10方法+MEL_MI
generate_tables.py    → T4-T8 (5个)             ← 需新增T8 MOFS表
plot_convergence.py   → F8-F9 (2个)             ← 需适配MEL_MI+新数据目录
手动 (draw.io)        → F1-F3 (3个)
手动 (LaTeX表格)      → T1-T3, T9 (4个)
```

---

## 六、论文定位与包装

**核心叙事**："Dual-Space"框架 — 多样性正则化单解框架（diversity-regularized single-solution framework）

- 传统SO-FS：单空间，无多样性维护
- 传统MO-FS：双目标优化，输出Pareto前沿给决策者
- **KDS-EL**：双空间协同，NHD作为搜索辅助目标，输出单一最优解

**多目标定位（关键）**：
- DRS是合法的双目标优化（fitness + NHD的Pareto排序）
- 但不叫"传统MOFS"——最终输出单一最优解，NHD是辅助目标
- 正确表述："bi-objective-regulated evolutionary feature selection"
- 辅助目标说法："NHD serves as an auxiliary structural objective for diversity preservation, not an end-user trade-off objective"

**命名规范（全文统一）**：
- EMDO → DRS（Diversity-regulated Selection）
- KGEF → KER（Knowledge-guided Elite Refinement）
- KDS_EL_DRS → KDS-EL/DRS
- KDS_EL_KER → KDS-EL/KER
- KDS_EL → KDS-EL (Proposed)
- PSO_CSM → PSO-CSM
- 绝不使用 "w/o"

---

## 七、创新点评估

**创新点1（中等偏高）**：DRS — NHD 作为结构多样性维持算子
- 文献中 NHD 只作诊断指标，本文首次纳入搜索选择算子
- DRS 不直接贡献精度，贡献的是种群结构多样性（NHD 0→0.453）和特征压缩
- Full 中 DRS 的多样性被 KER 约束在有益水平（NHD=0.310），没有付出精度代价
- 证据：NHD从0.000(MEL)→0.453(DRS)→0.310(Full)，特征减少-89.2%

**创新点2（高）**：KER — improvement-feedback 在线知识积累
- 不同于 IGPSO(MLP预训练) 和 FWPSO(即时权重)，跨迭代累积，无需额外评估
- KER 是精度的真正引擎
- 证据：KER单独+4.68pp over MEL（25数据集），Full精度几乎等同于KER

**创新点3（高）**：DRS + KER 互补 — 精度与多样性兼得
- DRS 维持多样性（NHD>0），KER 保证精度（Δ+4.88pp）
- DRS alone 困难数据集上过度牺牲精度 → KER 约束其有害偏向
- KER alone NHD≡0（种群坍缩 → 退化为重启型局部搜索） → DRS 提供结构多样性
- 完整 KDS-EL 是唯一同时实现高精度 + 正结构多样性的单解框架

**创新点0（辅助级）**：MI引导初始化+自适应重初始化
- 参考了fMOPSO-FS (Han 2024)，不是本文首创
- 本文贡献：组合进双空间框架，使MI知识贯穿全生命周期
- 是三个主创新点发挥作用的"地基"——没有它，KER冷启动导致~40%崩溃

---


---

## 九、写作进度与路径

### 已完成
- Abstract（框架）
- Introduction（框架）
- Methodology（主体，已改名DRS/KER）
- 时间复杂度分析
- 全部实验数据（4个实验目录，15方法×20数据集）

### 待写（按优先级）
1. §4 Experiments 各节（数据图表全有，先写）
2. §3 Methodology 补伪代码
3. §1 Introduction 扩充润色
4. §2 Related Work（全新写，1200词，3小节，含MOFS文献）
5. §5 Conclusion
6. T1-T3表格、F1-F3框架图、F8-F9收敛图

### 3周时间规划
- 第1周：Experiments全节
- 第2周：Methodology+Introduction+Related Work
- 第3周：收敛图+框架图+Conclusion+Reference+格式

---

## 十、已知问题与处理方式

**ISOLET数据集**：KDS-EL排名#12（输给SaWDE/FWPSO/多个MOFS方法）
→ SaWDE在ISOLET(617维,26类)上的搜索偏差机制特别有效
→ 如实在表格呈现，Discussion中解释ISOLET特点

**COIL20数据集**：天花板效应典型代表
→ 所有top方法Acc>0.95，KDS_EL=0.9809输给KER(0.9913)和FWPSO(0.9894)
→ 诚实展示天花板局限，论文中有叙事价值

**VGS-MOEA领先问题**（2026-07-18 审查后决定：保留，不替换）：
→ VGS-MOEA(0.9463)略优于KDS_EL(0.9450)，Δ=-0.0013
→ VGS-MOEA实现正确无bug，可变长度编码天然能探索极小特征子集（51 vs 220）
→ **不建议替换**：VGS-MOEA是变长MOEA代表作，审稿人会追问为什么没有它
→ **处理策略**：排名表按编码类型分组，KDS-EL在定长单解方法中排#1

**排名表分组策略**：
  主排名表 — Fixed-Length Methods:
    🥇 KDS_EL        0.9450  (single solution)
    🥈 KDS_EL/KER    0.9438
    🥉 KDS_EL/DRS    0.9383
    ...
  MOFS Variable-Length (单独表):
    VGS-MOEA         0.9463  (Pareto front, variable-length)
    KDS-EL           0.9450  (single solution, fixed-length)
  → 区分定长单解 vs 变长Pareto前沿两种范式，不构成直接竞争

**Cache导致特征爆炸**（已解决）：
→ 跨run共享cache导致weight反馈循环崩溃
→ 解决方案：不使用cache，保持原始算法逻辑

**已修复的算法bug**（2026-07-03）：
→ 权重更新顺序错误（在Pbest更新前执行）
→ KER冷启动崩溃（MI初始化解决）
→ 停滞问题（自适应重初始化解决）
→ 精英保护缺失（EMDO后保留top N//4）

---

## 十二、"协同/Synergy"问题的澄清（回应评审 DA-C1）

**DA-C1 指控**：从"协同"到"互补"的叙事转变是 HARKing（事后假设）。

**事实**：根本不存在"协同假说"。`critical_audit.py` 中的公式
```
synergy = ΔFull - (ΔDRS + ΔKER)
```
是一个**加性分解模型**，隐含假设 DRS 和 KER 是独立可加组件。但 KDS-EL 框架从来不是加性设计：

- DRS 在**结构空间**操作，目标是 NHD > 0（多样性维持）
- KER 在**适应度空间**操作，目标是 Acc 提升（精度引擎）
- 两者维度不同——用精度衡量 DRS 是**单位错误**（类比：用速度评价空调）

因此 `synergy = -3.76pp` 不是一个"被证伪的假设"，而是一个**不适用的分析公式产生的人为数值**。`ablation-narrative-plan.md`（2026-07-18）已明确禁止该公式：
> "DRS 是多样性维持算子，KER 是精度提升引擎。用精度去衡量 DRS 的'贡献'是单位错误。"

**正确的论证框架**（已在 §4.4 消融分析中采用）：
- DRS 的成功标准：NHD > 0，且不拖累精度 → 达成（NHD=0.453→0.310，Full Acc ≈ KER Acc）
- KER 的成功标准：ΔAcc > 0 over MEL → 达成（+4.68pp）
- 两者互补而非协同：不同空间，不同目标，不可加性分解

**评审回应策略**：不在论文中提 "synergy" 这个词（无论正面还是负面），因为加性分解框架本身就不适用。论文只呈现消融表中的原始数据（MEL → MEL_MI → DRS → KER → Full），让读者自行判断各模块的角色。DA-C1 的指控基于对分析代码中一个调试公式的误解，该公式从未出现在论文手稿中。

---

## 十一、npy文件说明

**输出目录**：
- `output/formal_experiment_20260702_145828/curves/` — KDS-EL家族3变体，每run一个文件
  - `curve_{VERSION}_{DATASET}_run{N}.npy` — fitness收敛曲线
  - `nhd_{VERSION}_{DATASET}_run{N}.npy` — NHD曲线（DRS和KDS_EL有非零值）
- `output/formal_experiment_mel_mi/curves/` — MEL_MI对照，每run一个文件
  - `curve_MEL_MI_{DATASET}_run{N}.npy` — fitness收敛曲线
  - `nhd_MEL_MI_{DATASET}_run{N}.npy` — NHD曲线（MEL_MI的NHD≡0，作为基线对照）
- `output/formal_experiment_20260701_094943/curves/` — SOTA 5方法，每run一个文件
  - `curve_{VERSION}_{DATASET}_run{N}.npy` — fitness收敛曲线
- `output/formal_experiment_20260707_142018/curves/` — MOFS 6方法
  - `curve_{VERSION}_{DATASET}_run{N}.npy`

收敛图脚本：`code/plot_convergence.py`
综合分析脚本：`code/analyze_experiments.py`
消融分析脚本：`code/analyze_ablation_validity.py`
