# KDS-EL 论文项目完整记忆文档
# 用于新对话的上下文恢复
# 生成时间：2026年5月 | 最后更新：2026年7月18日（多审稿人审查完成，消融叙事重构，VGS-MOEA策略确定）

---

## 一、项目概况

**算法名称**：KDS-EL（Knowledge-guided Dual-Space Evolutionary Learning）
**研究领域**：高维生物信息学特征选择（Wrapper-based, PSO框架）

---

## 二、算法架构

```
KDS-EL = 双子群PSO骨架（继承自MEL [CITE_MEL, IEEE TKDE]）
         + MI 初始化 + 自适应重初始化          ← 知识引导生命周期
         + DRS（Diversity-regulated Selection）← 原名 EMDO
         + KER（Knowledge-guided Elite Refinement）← 原名 KGEF

DRS：在 fitness 和 -NHD 两个目标上做 NSGA-II Pareto 排序
     α_cd(t) = (t/T)² — 早期多样性优先，后期精度优先
     定位：Structural Space（结构空间）

KER：improvement-feedback 权重更新（weight += delta when Pbest improves）
     权重更新在 Pbest 更新之前（已验证的关键顺序）
     p_r=0.10 随机翻转保证遍历性
     定位：Fitness Space（适应度空间）

消融命名：
  KDS_EL_DRS       → KDS-EL/DRS（只含DRS + MI初始化 + 自适应重初始化）
  KDS_EL_KER       → KDS-EL/KER（只含KER + MI初始化 + 自适应重初始化）
  KDS_EL           → KDS-EL（Proposed，完整框架）
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
| 2 | `output/formal_experiment_20260628_205157/` | 旧版消融 V1 (4方法×27数据集) | ✅ | ⚠️ 仅MEL有效 |
| 3 | `output/formal_experiment_20260702_145828/` | 最新消融 V2 (3方法×26数据集) | ✅ | ✅ 全部有效 |
| 4 | `output/formal_experiment_20260707_142018/` | MOFS 对比 (6方法×20数据集) | ✅ | ✅ 全部有效 |

### 3.2 20个数据集

`ALL1`(128×12625,2c), `ALL4`(93×12625,2c), `ALL_AML`(72×7129,2c),
`Adenoma`(36×7457,2c), `BASEHOCK`(1993×4862,2c), `COIL20`(1440×1024,20c),
`Colon`(62×2000,2c), `DLBCL`(77×7129,2c), `Gastric`(65×22645,2c),
`Gastric1`(144×22283,2c), `Gastric2`(124×22283,2c), `ISOLET`(1560×617,26c),
`Leukaemia`(72×7129,2c), `Lymphoma`(45×4026,2c), `Myeloma`(173×12625,2c),
`PCMAC`(1943×3289,2c), `Prostate`(102×12625,2c), `SRBCT`(83×2308,4c),
`T1D`(101×54675,2c), `madelon`(2600×500,2c)

### 3.3 15个方法

| 类别 | 方法 | 数据来源 |
|------|------|----------|
| **本文** | **KDS_EL** | 实验3 |
| 消融 | KDS_EL_DRS, KDS_EL_KER | 实验3 |
| 基线 | MEL | 实验2 |
| SOTA 单目标 | BPSO, SaWDE, FWPSO, PSO-CSM, IGPSO | 实验1 |
| MOFS 经典 | NSGA-II-FS, MOPSO-FS, MOEA-D-FS | 实验4 |
| MOFS 近年 | VGS-MOEA, fMOPSO-FS, W-MOPSO-FS | 实验4 |

**实验协议**：StratifiedKFold(5, shuffle=True), 10 runs × 100 iterations, RNG自然流动

---

## 四、核心数字（写作时直接引用）

### 4.1 15方法排名（20数据集，真实分类准确率）

| 排名 | 方法 | True Acc | Feat | Time(s) | 类别 |
|:----:|------|----------|------|---------|------|
| 🥇 | VGS-MOEA | **0.9463** | 51 | 34.2 | MOFS 变长 |
| 🥈 | **KDS_EL** | **0.9450** | 220 | 96.2 | **本文** |
| 🥉 | KDS_EL_KER | 0.9438 | 236 | 97.5 | 消融 |
| 4 | KDS_EL_DRS | 0.9383 | 166 | 188.0 | 消融 |
| 5 | FWPSO | 0.9177 | 1069 | 49.7 | SOTA |
| 6 | W-MOPSO-FS | 0.9132 | 2960 | 110.4 | MOFS |
| 7 | fMOPSO-FS | 0.9110 | 3007 | 119.9 | MOFS |
| 8 | NSGA-II-FS | 0.9064 | 4818 | 135.9 | MOFS |
| 9 | MOEA-D-FS | 0.9042 | 4937 | 138.5 | MOFS |
| 10 | PSO-CSM | 0.9021 | 1559 | 122.5 | SOTA |
| 11 | MOPSO-FS | 0.9009 | 5263 | 142.8 | MOFS |
| 12 | SaWDE | 0.8944 | 3521 | 110.5 | SOTA |
| 13 | MEL | 0.8868 | 2722 | 175.0 | 基线 |
| 14 | IGPSO | 0.8839 | 2538 | 136.4 | SOTA |
| 15 | BPSO | 0.8698 | 5297 | 146.2 | SOTA |

### 4.2 Friedman排名（20数据集）

| 方法 | Avg Rank |
|------|----------|
| KDS_EL | 3.000 |
| KDS_EL_KER | 3.200 |
| KDS_EL_DRS | 3.600 |
| FWPSO | 5.050 |
| PSO_CSM | 6.250 |
| SaWDE | 6.850 |
| IGPSO | 8.150 |
| MEL | 8.500 |
| BPSO | 9.400 |

> KDS-EL三变体占据前三，与第4名FWPSO差距**1.45**。

### 4.3 KDS_EL vs各方法Win/Loss（20数据集）

| vs 方法 | Win | Tie | Loss | 胜率 | 类别 |
|---------|-----|-----|------|------|------|
| MEL | 20 | 0 | 0 | **100%** | 基线 |
| BPSO | 20 | 0 | 0 | **100%** | SOTA |
| PSO-CSM | 20 | 0 | 0 | **100%** | SOTA |
| IGPSO | 20 | 0 | 0 | **100%** | SOTA |
| SaWDE | 19 | 0 | 1 | 95.0% | SOTA |
| FWPSO | 18 | 0 | 2 | 90.0% | SOTA |
| MOPSO-FS | 17 | 1 | 2 | 85.0% | MOFS |
| MOEA-D-FS | 16 | 0 | 4 | 80.0% | MOFS |
| fMOPSO-FS | 16 | 1 | 3 | 80.0% | MOFS |
| NSGA-II-FS | 15 | 1 | 4 | 75.0% | MOFS |
| W-MOPSO-FS | 15 | 2 | 3 | 75.0% | MOFS |
| VGS-MOEA | 8 | 1 | **11** | 40.0% | MOFS |

> KDS_EL唯一Acc落后的对手是VGS-MOEA（Δ=-0.0013）。排除VGS-MOEA后对所有其他方法胜率≥75%。
> ISOLET仍唯一输给SaWDE。COIL20成为第二个输给FWPSO的数据集（天花板效应）。

### 4.4 消融分析：模块贡献度（26数据集）

| 指标 | 数值 |
|------|------|
| Δtotal (KDS_EL vs MEL) | **+4.68pp** |
| ΔDRS (DRS vs MEL) | +3.81pp |
| ΔKER (KER vs MEL) | +4.43pp |

**消融三层论证框架**：
1. 每个模块独立有效：DRS +3.81pp, KER +4.43pp
2. 每个模块有结构性缺陷：DRS牺牲accuracy，KER牺牲多样性
3. 完整框架是唯一兼得方案：accuracy达KER水平 + NHD保持0.324 + 特征-93.4%

**天花板效应**：9/26数据集Acc>0.99，压低了跨数据集平均协同。在3个困难数据集（ALL2/ALL3/Stroke）上DRS单独为负贡献，KDS_EL完整版实现互相纠错（协同+0.9~3.5pp）。

**PCMAC — 三模块协同最强证据**：Δtotal=+0.0608，正协同，同时显著优于两变体。

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

## 五、图表规划（9 Tables + 12 Figures = 21个）

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
| T7 | 消融实验ACC+Features（4变体×26数据集） | §4.5 消融分析 | ✅ 已生成 |
| T8 | MOFS六方法单独对比 | §4.6 MOFS对比 | 🆕 新增 |
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
| F6 | 消融双面板（4变体×26数据集） | ✅ 已生成 |
| F7 | 稳定性箱线图（10方法，auto-grid，20数据集） | 🔄 需重新生成 |
| F8 | 收敛曲线（10方法，auto-grid，20数据集） | 🔄 需重新生成 |
| F9 | NHD多样性曲线（KDS_EL+DRS，auto-grid，20数据集） | 🔄 需重新生成 |
| F10 | Wilcoxon热图（10方法×20数据集） | 🔄 需重新生成 |
| F11 | 运行时间对比（对数轴，10方法，20数据集） | 🔄 需重新生成 |
| F12 | 精度-特征-时间气泡图（10方法，20数据集） | 🔄 需重新生成 |

### 生成脚本

```
generate_figures.py   → F4-F7, F10-F12 (7个)   ← 需适配10方法
generate_tables.py    → T4-T8 (5个)             ← 需新增T8 MOFS表
plot_convergence.py   → F8-F9 (2个)             ← 需适配新数据目录
手动 (draw.io)        → F1-F3 (3个)
手动 (LaTeX表格)      → T1-T3, T9 (4个)
```

---

## 六、论文定位与包装

**核心叙事**："Dual-Space"框架 — 第三种路径（third pathway）

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

**创新点1（中等偏高）**：DRS将NHD首次升格为Pareto选择目标
- 文献中NHD只作诊断指标，本文首次纳入选择算子
- 证据：NHD从0.000→0.451(KDS-EL/DRS)→0.324(KDS-EL)，特征减少93.4%

**创新点2（中等）**：KER的improvement-feedback在线知识积累
- 不同于IGPSO(MLP预训练)和FWPSO(即时权重)
- 跨迭代累积，无需额外评估
- 证据：KER单独+4.43pp over MEL（26数据集）

**创新点3（高）**：Dual-Space协同框架
- 困难数据集上互相纠错（ALL2/ALL3/Stroke），天花板数据集上至少不差
- PCMAC：Δtotal=+0.0608，正协同，同时显著优于两变体
- 是整篇论文最有说服力的卖点

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

## 十一、npy文件说明

**输出目录**：
- `output/formal_experiment_20260702_145828/curves/` — KDS-EL家族3变体，每run一个文件
  - `curve_{VERSION}_{DATASET}_run{N}.npy` — fitness收敛曲线
  - `nhd_{VERSION}_{DATASET}_run{N}.npy` — NHD曲线（DRS和KDS_EL有非零值）
- `output/formal_experiment_20260701_094943/curves/` — SOTA 5方法，每run一个文件
  - `curve_{VERSION}_{DATASET}_run{N}.npy` — fitness收敛曲线
- `output/formal_experiment_20260707_142018/curves/` — MOFS 6方法
  - `curve_{VERSION}_{DATASET}_run{N}.npy`

收敛图脚本：`code/plot_convergence.py`
综合分析脚本：`code/analyze_experiments.py`
消融分析脚本：`code/analyze_ablation_validity.py`
