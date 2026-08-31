# 参考 EMSWOA (Applied Soft Computing 2024) 的 KDS-EL 全文逐章学术写作与规范指南

> **参考文献基准**：Miao et al., *"Dynamic multi-swarm whale optimization algorithm based on elite tuning for high-dimensional feature selection classification problems"*, *Applied Soft Computing*, 169 (2025) 112634. (DOI: 10.1016/j.asoc.2024.112634, 简称 **EMSWOA**)
> **适配目标成果**：Knowledge-guided Dual-swarm Evolutionary Learning for High-dimensional Feature Selection (简称 **KDS-EL**)
> **目标期刊**：*Applied Soft Computing* (Elsevier, Top SCI, IF≈7.2, JCR Q1)

---

## 总体编排与篇章映射大纲（100% 对齐 EMSWOA 范式）

| EMSWOA 原始章节 (ASOC 2024) | KDS-EL 规范对应章节 | 本章核心借鉴价值 (写法 / 表达 / 规范) |
| :--- | :--- | :--- |
| **Title / Abstract / Highlights** | **Title / Abstract / Highlights / Keywords** | ASOC 标准“四段式摘要公式”、5条动作导向 Highlights、标题结构定式 |
| **1. Introduction** | **1. Introduction** | “问题背景 $\to$ 现有方法局限 $\to$ 核心不适配缺口 $\to$ 本文机制 $\to$ 4大贡献点（带量化指标）$\to$ 组织结构”漏斗模型 |
| **2. Related work**<br>• 2.1 Feature selection<br>• 2.2 Base algorithm (WOA)<br>• 2.3 Literature review (EC & Non-EC) | **2. Related Work & Preliminaries**<br>• 2.1 Problem formulation and binary mapping<br>• 2.2 Baseline: Multi-task Evolutionary Learning (MEL)<br>• 2.3 Literature review on high-dimensional FS | 规范的双目标单/多目标数学建模形式；基线算法公式化展开；分类综述表（Table 1）分类逻辑与评述范式 |
| **3. The proposed method**<br>• 3.1 Framework<br>• 3.2 Mechanism 1 (Multi-swarm)<br>• 3.3 Mechanism 2 (Elite tuning)<br>• 3.4 Fitness function<br>• 3.5 Time-complexity analysis | **3. The Proposed KDS-EL Framework**<br>• 3.1 Overall architecture & discrete mapping<br>• 3.2 Mutual information-guided initialization<br>• 3.3 Global feature importance matrix & decay<br>• 3.4 Knowledge-guided elite refinement (KER)<br>• 3.5 Two-phase weight scheduling (TPS)<br>• 3.6 Overall flow & pseudocode<br>• 3.7 Time-complexity analysis | 机制可视化流程图设计；精英操作数学形式化表达；渐进时间复杂度（Big-$O$）严格分项推导表 |
| **4. Experimental results and discussion**<br>• 4.1 Experimental setup<br>• 4.2.1 Comparison of average accuracy rates<br>• 4.2.2 Average number of features<br>• 4.2.3 Fitness value analysis<br>• 4.2.4 P value tests of Wilcoxon rank-sum test<br>• 4.2.5 Performance comparison before and after algorithm improvement<br>• 4.2.6 Comparison with SOTA EA algorithms<br>• 4.2.7 Non-EA & Parameter analysis<br>• 4.2.8 Discussion | **4. Experimental Results and Discussion**<br>• 4.1 Experimental setup<br>• 4.2.1 Comparison of classification accuracy<br>• 4.2.2 Comparison of the number of selected features<br>• 4.2.3 Fitness value and convergence analysis<br>• 4.2.4 Statistical significance analysis via Wilcoxon test<br>• 4.2.5 Performance comparison before and after algorithm improvement<br>• 4.2.6 Computational efficiency and runtime analysis<br>• 4.2.7 Parameter sensitivity and robustness analysis<br>• 4.2.8 Discussion | 严格分为 Setup 与 Analysis 两大主干；地道群体智能/进化计算命名（杜绝 Ablation 等机器学习术语）；主表 Mean±Std 规范；多维统计检验；组件逐步剥离与天花板效应深入探讨 |
| **5. Conclusions and future work** | **5. Conclusions and Future Work** | 结论两段式黄金范式（前瞻性总结 + 诚实局限性与未来路线） |

---

## 逐章深度剖析与借鉴指南

---

### 【Title, Highlights & Abstract】

#### 1. EMSWOA 优秀之处剖析
*   **标题定式**：`[核心机制组合 (Adjective + Noun)] + [Backbone Algorithm] + [based on/with Strategy] + for [Problem Domain]`
    *   *EMSWOA 原文*：*Dynamic multi-swarm whale optimization algorithm based on elite tuning for high-dimensional feature selection classification problems*
*   **Highlights (ASOC 强制要求 3-5 条，每条 ≤ 85 字符含空格)**：
    *   全部采用统一的动词过去分词/主动语态（Proposed ..., Developed ..., Introduced ..., Proved ...）。
    *   结构覆盖：机制1 + 机制2 + 整体算法 + 应用场景 + 核心性能结论。
*   **Abstract “四步黄金公式” (200~250 词)**：
    1.  **Sentence 1-2 (Background & Challenge)**：特征选择重要性 $\to$ 高维导致解空间指数爆炸与局部最优陷阱。
    2.  **Sentence 3-4 (Method & Mechanism 1)**：提出算法名称 $\to$ 第一机制如何解决全局探索与早熟问题。
    3.  **Sentence 5-6 (Mechanism 2 & Key Insight)**：针对离散状态无效概率翻转问题 $\to$ 设计精英调优机制，纠正翻转方向。
    4.  **Sentence 7-8 (Experimental Validation & Quantitative Proof)**：在多个数据集对比多种代表算法，给出明确量化数据（如平均精度提升 xx%，特征减少 xx 倍）。

#### 2. KDS-EL 借鉴与写作规范

##### 推荐标题
*   **Option A (推荐)**：*Knowledge-guided dual-swarm evolutionary learning with two-phase scheduling for high-dimensional feature selection*
*   **Option B**：*Closed-loop knowledge-guided evolutionary learning based on elite refinement for high-dimensional feature selection classification*

##### Highlights 拟定参考
```markdown
- A closed-loop knowledge-guided dual-swarm evolutionary framework (KDS-EL) is proposed.
- Mutual information-guided initialization relieves the severe cold-start dilemma.
- Knowledge-guided elite refinement is devised to direct mutation via cumulative feedback.
- Two-phase weight scheduling dynamically resolves the objective conflict of accuracy and sparsity.
- KDS-EL achieves 0.9574 accuracy with 88 features on 20 benchmarks, outperforming 13 rivals with 3.4x speedup.
```

##### 实用英文学术句型库 (Abstract)
*   *Feature selection (FS) is a pivotal technique for mitigating the curse of dimensionality in high-dimensional biomedical data.*
*   *However, the vast search space and severe sparsity render conventional evolutionary algorithms vulnerable to premature convergence and random blind search.*
*   *To address these issues, we propose a [Framework Name], termed [Acronym]...*
*   *First, ... is introduced to inject domain prior knowledge and alleviate the cold-start problem.*
*   *Second, a novel [Mechanism Name] is devised to transform evolutionary feedback into directed mutation, eliminating futile search operations.*
*   *Extensive experiments on 20 benchmark datasets against 13 competitive baselines demonstrate that [Acronym] yields superior classification accuracy (0.9574) and ultra-sparse feature subsets (87.8 features on average), achieving a 3.4x acceleration over the baseline.*

---

### 【Section 1: Introduction】

#### 1. EMSWOA 优秀之处剖析
*   **倒金字塔/漏斗式叙事 (Funnel Structure)**：
    *   **P1**: 从具体应用（生物基因微阵列、癌症诊断、高维文本）切入，阐明 $D \gg N$ 场景下的过拟合和计算开销。
    *   **P2**: 梳理 Filter, Wrapper, Embedded 的核心差异，点出为什么 Evolutionary Computation (EC) 是高维组合优化的首选。
    *   **P3 (核心痛点聚焦)**：明确指出基础算法搬到高维 FS 时的结构性病灶。
    *   **P4 (方法引出与机制呼应)**：针对上述病灶，分别提出针对性解法。
    *   **P5 (4大贡献点列表)**：清晰列出 4 条贡献，前 3 条是方法机制创新，第 4 条是系统性实验验证（带具体数据支撑）。
    *   **P6 (文章结构)**：标准的 Section 2 ~ 5 导航段。

#### 2. KDS-EL 借鉴与写作规范

##### 关键段落布局与论证逻辑
1.  **P1 (高维生物数据痛点)**：微阵列/基因表达数据维度高达数万（T1D 达 54,675 维），样本仅几十例。特征空间为 $2^D$，存在海量冗余与噪声特征。
2.  **P2 (进化特征选择与双子群多任务)**：简述 EC-based FS 优势，引出多任务学习（MEL）通过子群协作提升搜索能力的先进性。
3.  **P3 (三大结构性不适配 —— 本文核心问题驱动)**：
    *   *Defect 1 (Cold Start)*: 随机初始化在万维空间远离有效特征子空间，浪费前期搜索预算 $\to$ 引出 **MI 引导初始化与自适应重启**。
    *   *Defect 2 (Knowledge Waste in Mutation)*: 传统变异/翻转对所有特征无差别均匀随机翻转，忽略历史代际反馈 $\to$ 引出 **KER 知识引导精英翻转**。
    *   *Defect 3 (Static Preference Dilemma)*: 固定适应度权重全程僵化，无法兼顾“前期粗筛压缩”与“后期精细调优”的不同需求 $\to$ 引出 **TPS 两阶段权重调度**。
4.  **P4 (Contributions 列表标准表达)**：

##### 实用英文学术句型库 (Introduction)
*   *Despite the promising performance of [Baseline], directly migrating standard evolutionary algorithms to ultra-high-dimensional FS tasks reveals three fundamental structural bottlenecks:*
*   *(1) **Knowledge-blind initialization**: Randomly initialized populations in high-dimensional sparse spaces contain negligible discriminative signals, incurring an immense cold-start penalty.*
*   *(2) **Feedback-decoupled mutation**: Conventional bit-flip operators treat all candidate dimensions uniformly, discarding the rich historical fitness feedback accumulated across generations.*
*   *(3) **Static objective preference**: A time-invariant fitness weighting scheme fails to reconcile the conflicting demands of aggressive dimensionality reduction in early iterations and fine-grained subset refinement in late iterations.*
*   *The principal contributions of this paper are summarized as follows:*
    *   *We propose the KDS-EL framework, which establishes a closed-loop knowledge-guided paradigm for high-dimensional feature selection.*
    *   *We design a knowledge-guided elite refinement (KER) strategy that leverages an accumulated feature importance matrix to direct mutation, achieving targeted exploration with bounded evaluation budget.*
    *   *We introduce a two-phase weight scheduling (TPS) mechanism to temporally decouple feature compression and accuracy optimization.*
    *   *Comprehensive empirical evaluations across 20 high-dimensional datasets against 13 state-of-the-art algorithms confirm the comprehensive superiority of KDS-EL in accuracy, sparsity, and runtime efficiency.*

---

### 【Section 2: Related Work & Preliminaries】

#### 1. EMSWOA 优秀之处剖析
*   **严密的数学形式化定义 (2.1节)**：
    *   严格给出单目标/多目标特征选择的数学优化模型：
        $$\min_{x} f(x) = \alpha \cdot \text{ErrorRate} + \beta \cdot \frac{|x|}{D}, \quad \text{s.t. } x = (x_1, x_2, \dots, x_D) \in \{0, 1\}^D$$
        明确说明 $\alpha + \beta = 1$，$\alpha$ 与 $\beta$ 的物理含义。
*   **基础算法机制清晰呈现 (2.2节)**：
    *   公式化描述基础算法的位置更新、探索与利用平衡机制，配合关键变量定义。
*   **结构化的文献分类综述与对比表 (2.3节 & Table 1)**：
    *   将现有方法分为“EC-based”与“Non-EC-based”，并详细分析各自在高维场景下的优劣。
    *   **Table 1 的学术规范**：列出 Category, Algorithm, Core Technique, Advantages, Disadvantages, Reference。

#### 2. KDS-EL 借鉴与写作规范

##### 章节建议编排
*   **2.1. Problem Formulation and Binary Mapping**: 形式化定义高维特征选择问题、二进制解编码 $x \in \{0, 1\}^D$、KNN 分类误差评估与综合适应度函数。
*   **2.2. Baseline: Multi-task Evolutionary Learning (MEL)**: 给出 MEL 的双子群（Sub1 连续速度-位置更新 + Sub2 概率权重采样）数学模型，指出其知识更新机制的雏形与不足。
*   **2.3. Literature Review on High-dimensional Feature Selection**:
    *   2.3.1. Single-objective & Multi-objective Evolutionary FS (FWPSO, PSO-CSM, SaWDE, W-MOPSO-FS, VGS-MOEA 等).
    *   2.3.2. Knowledge-guided and Multi-task Evolutionary Methods.
    *   **Table 1**: 现有高维特征选择代表算法分类对比表。

---

### 【Section 3: The Proposed KDS-EL Framework】

#### 1. EMSWOA 优秀之处剖析
*   **全景架构图与流程图 (Fig. 1 & Fig. 2)**：
    *   Fig. 1 展示特征选择宏观数据流（原始高维矩阵 $\to$ 种群更新 $\to$ 精英纠错 $\to$ 过滤子集 $\to$ 分类评估）。
    *   Fig. 2 展示算法主循环的严密状态迁移（判断条件、分支路径）。
*   **核心机制的深入机理剖析与示意图 (Fig. 5 & Fig. 6)**：
    *   深入剖析问题本质并绘制机制示意图，让审稿人一目了然看懂机制设计逻辑。
*   **完备的渐进时间复杂度推导 (3.5节 & Table 4/5/6)**：
    *   分步骤推导每个阶段的 Big-$O$ 复杂度（初始化、适应度评估、子群更新、核心算子操作），最后汇总为整体复杂度，并与原算法并列对比，严格证明“**算法改进未增加渐进复杂度阶数**”。

#### 2. KDS-EL 借鉴与写作规范

##### 章节与机制展开要点
1.  **3.1. Overall Framework of KDS-EL**: 引入整体架构图 **Fig. 1**，清晰展示三大环节（MI 启动 $\to$ W 矩阵积累与衰减 $\to$ KER 反哺 $\to$ TPS 时序控制）。
2.  **3.2. Mutual Information-Guided Initialization and Adaptive Restart**:
    *   给出互信息公式 $I(X_j; Y)$，混合初始化比例 $\mu_{\text{init}}=0.5$，以及停滞检测与自适应重初始化条件。
3.  **3.3. Global Feature Importance Weight Matrix with Exponential Decay**:
    *   给出 Case 1（个体变优）与 Case 2（个体变差）下权重矩阵 $W_j$ 的离散累加公式及衰减因子 $\gamma = 0.99$。
4.  **3.4. Knowledge-Guided Elite Refinement (KER)**:
    *   形式化描述精英选择（Top $elite\_k = 3$），知识打分机制，$\delta=0.01$ 翻转比例，以及 1v1 原地评估检验（有界精化预算）。
5.  **3.5. Two-Phase Weight Scheduling (TPS)**:
    *   定义两阶段分段权重函数（Phase 1 压缩 $\alpha=0.7, \beta=0.3$ vs Phase 2 精调 $\alpha=0.95, \beta=0.05$，切点 $\tau=0.7$）。
6.  **3.6. Overall Algorithmic Flow and Pseudocode (Algorithm 1)**: 标准 LaTeX 伪代码。
7.  **3.7. Time-Complexity Analysis (严格对比)**：
    *   证明整体渐进复杂度为 $\mathcal{O}(T_{\max} \cdot (N \cdot T_{\text{eval}} + N \cdot D))$，与 MEL 同阶，并通过稀疏子集评估解释实测 3.4× 加速机理。

---

### 【Section 4: Experimental Results and Discussion】（100% 对齐 ASOC / EMSWOA 地道规范）

#### 1. EMSWOA 优秀之处剖析
*   **结构划分极度纯粹**：全章直接划分为 **4.1. Experimental setup** 与 **4.2. Experimental analysis** 两大主干。
*   **专业术语符合群体智能/进化计算习惯**：
    *   在 SI / EC 领域顶刊中，很少使用 CV / ML 领域的 "Ablation study" 字样，而是采用更加精准、地道的 **"Performance comparison before and after algorithm improvement"** 或 **"Effectiveness analysis of proposed strategies"**。
    *   三级标题全部采用纯净名词短语。

#### 2. KDS-EL 规范章节编排与正文要点

```latex
4. Experimental results and discussion
   4.1. Experimental setup
        4.1.1. High-dimensional benchmark datasets
        4.1.2. Comparison algorithms and parameter settings
        4.1.3. Evaluation metrics and statistical test protocols
   4.2. Experimental analysis
        4.2.1. Comparison of classification accuracy
        4.2.2. Comparison of the number of selected features
        4.2.3. Fitness value and convergence analysis
        4.2.4. Statistical significance analysis via Wilcoxon test
        4.2.5. Performance comparison before and after algorithm improvement
        4.2.6. Computational efficiency and runtime analysis
        4.2.7. Parameter sensitivity and robustness analysis
        4.2.8. Discussion
```

##### 各小节正文内容与图表承载规划
*   **4.1. Experimental setup**:
    *   `4.1.1. High-dimensional benchmark datasets`: 介绍 20 个高维基准数据集（含样本数、特征数、类别数、应用领域），承载 **Table 2**。
    *   `4.1.2. Comparison algorithms and parameter settings`: 介绍 14 种定长对比方法（单目标 SOTA、多目标 MOFS、消融基线）及统一的参数设定，承载 **Table 1 & Table 3**。
    *   `4.1.3. Evaluation metrics and statistical test protocols`: 介绍 3-NN、5-fold CV、10 次独立运行，以及 Wilcoxon 符号秩检验与 Holm-Bonferroni 校正协议。
*   **4.2.1. Comparison of classification accuracy**:
    *   报告 20 个数据集上的 Mean $\pm$ Std 分类精度，最优值加粗，次优值加下划线，承载 **Table 4 & Figure 4 (柱状图)**。
*   **4.2.2. Comparison of the number of selected features**:
    *   报告平均选中特征数与特征压缩率，用 **Figure 5 (特征柱状图) & Figure 12 (精度-特征气泡图)** 证明 KDS-EL 在左上角（高精度、超稀疏）。承载 **Table 5**。
*   **4.2.3. Fitness value and convergence analysis**:
    *   展示代表性数据集上的适应度与精度进化轨迹，分析 KDS-EL 快速收敛与持续跳出局部最优的能力，承载 **Figure 8 (收敛曲线)**。
*   **4.2.4. Statistical significance analysis via Wilcoxon test**:
    *   报告对 13 种对比方法的两两 Wilcoxon 检验胜/平/负场次（20/20, 19/20 等）以及校正后的 $p$ 值与 Friedman 平均排名，承载 **Table 6, Table 6b & Figure 10, Figure 13**。
*   **4.2.5. Performance comparison before and after algorithm improvement**:
    *   在正文中采用严密的**组件逐步剥离与增量分析**（对应 EMSWOA 4.2.5 节）：
        $$\text{KDS-EL (0.9574)} \xrightarrow{- \text{TPS}} \text{w/o TPS (0.9488)} \xrightarrow{- \text{KER}} \text{w/o TPS\&KER (0.9325)} \xrightarrow{- \text{MI}} \text{MEL (0.8868)}$$
        定量论证 TPS (+0.86pp / -28% feats)、KER (+1.63pp / -58% feats)、MI (+4.58pp / -89% feats) 的独立贡献与协同价值，承载 **Table 7 & Figure 6 (热图/瀑布图)**。
*   **4.2.6. Computational efficiency and runtime analysis**:
    *   对比各算法在不同维度数据集上的平均运行耗时，阐述实测 51.3s vs MEL 175.0s（**3.4× 加速**）的内在机制（稀疏子集加速单次评估），承载 **Figure 11 (时间散点图)**。
*   **4.2.7. Parameter sensitivity and robustness analysis**:
    *   在 4 个代表数据集上分析 5 个超参数（$\gamma, \tau, \delta, \mu_{\text{init}}, elite\_k$）的变动影响，证明波动均 $\le \pm 1.5$pp，默认参数具备极佳通用性，承载 **Table 8**。
*   **4.2.8. Discussion**:
    *   深入探讨高维生物医学数据的 **“天花板效应 (Ceiling Effect)”**：在 8 个精度饱和数据集上，精度无法继续拉开差距，此时 KDS-EL 的极简特征数（39~83 vs 数千）具有重大的临床标志物发现价值与生物可解释性。

##### 实用英文学术句型库 (Section 4)
*   *Table 4 reports the mean classification accuracy and standard deviation across 10 independent runs on 20 benchmark datasets. The best performance is highlighted in **bold**, and the second-best is <u>underlined</u>.*
*   *As evidenced by Table 4, KDS-EL consistently outperforms all 13 competitors, achieving the highest overall mean accuracy of 0.9574, which surpasses the strongest single-objective SOTA (FWPSO, 0.9177) by 3.97 percentage points and the leading multi-objective algorithm (W-MOPSO-FS, 0.9132) by 4.42 percentage points.*
*   *Regarding feature reduction (Table 5), KDS-EL shrinks the feature space down to merely 87.8 features on average (a compression ratio exceeding 99.1%), outperforming MEL by a factor of 30.9×.*
*   *To rigorously assess whether the improvements are statistically significant, two-tailed Wilcoxon signed-rank tests were conducted at a significance level of $\alpha = 0.05$. Furthermore, the Holm-Bonferroni correction was applied to control the family-wise error rate.*
*   *To validate the efficacy of each constituent mechanism, Table 7 presents the performance comparison before and after algorithm improvement: removing TPS leads to a 0.86% accuracy drop alongside a 38.6% increase in feature subset size; further stripping KER results in an additional 1.63% accuracy degradation and a 2.38× feature explosion. This confirms that all integrated strategies contribute significantly to the overall framework.*

---

### 【Section 5: Conclusions and Future Work】

#### 1. EMSWOA 优秀之处剖析
*   **精炼的两段式结构**：
    *   **P1 (总结)**：精炼概括研究动机、核心架构、机制作用与核心量化结论。
    *   **P2 (局限性与展望)**：提出 2-3 个切实可行的未来演进方向。

#### 2. KDS-EL 借鉴与写作规范
*   **Paragraph 1 (Summary)**：重申 0.9574 精度、87.8 个紧凑特征、20/20 显著优于 MEL、3.4× 加速等里程碑。
*   **Paragraph 2 (Limitations & Future Work)**：
    1.  *Adaptive Phase Transition*: 探索自适应动态切换准则；
    2.  *Classifier Generalization*: 扩展至 SVM、LightGBM 及轻量化深度网络；
    3.  *Pareto Frontier Integration*: 探索 KER 算子与非支配排序多目标框架（如 NSGA-III / MOEA/D）的融合；
    4.  *Ultra-Large-Scale & Multi-label Scenarios*: 支持百万维组学数据与多标签学习。

---

## 总结：KDS-EL 论文撰写执行检查清单 (Checklist)

| 检查维度 | 达标要求 (参照 EMSWOA / ASOC 标准) | KDS-EL 落地状态 |
| :--- | :--- | :--- |
| **标题与摘要** | 包含核心机制、Backbone、应用场景；摘要严格四段式；5 条动词导向 Highlights | 已规划，直接套用 |
| **引言动机** | 明确挖出通用算法在高维 FS 的“三大结构性缺陷”，并与三大机制一一映射 | 逻辑完全闭环 |
| **数学规范** | 单/双目标优化数学定义完整；所有算法变量符号统一；给出严格 Big-$O$ 复杂度推导 | 公式体系完备 |
| **图表规范** | 流程图/架构图美观；主表加粗最优值/下划线次优值；附录支撑明细数据 | 图表体系齐全 (F1-F13, T1-T8) |
| **实验结构** | 严格两大主干（4.1 Setup & 4.2 Analysis），8 节地道 SI/EC 学术标题 | 20-DS 全量数据就绪 |
| **术语地道性** | 采用 "Performance comparison before and after algorithm improvement"，杜绝 Ablation 等跨领域术语 | 100% 对齐 EMSWOA |
| **学术诚实** | 深入剖析天花板数据集（8个数据集精度饱和下看特征压缩比） | 极具说服力 |
