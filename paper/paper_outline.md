# KDS-EL 期刊论文结构大纲 (Paper Outline)
> 目标期刊: Applied Soft Computing (Elsevier) | 类型: Original Research Article
> 篇幅: 8000-10000 words (不含参考文献), 目标 ~8500±500 | 引用: Elsevier numbered
> 作者侧备忘: 本大纲基于 `output/实验数据汇总.md` 与 `paper/references_master.md` 编写。

---

## 全局字数预算 (总计 ~8650 words + 摘要 250)

| 编号 | Section | 字数 | 图表(主文) | 表格(主文) |
|---|---|---|---|---|
| 1 | Introduction | 1000 | 无 | 无 |
| 2 | Related Work | 1250 | 无 | 无 |
| 3 | Preliminaries | 450 | 无 | 无 |
| 4 | Proposed KDS-EL | 1700 | F1, F2(可选) | 无 |
| 5 | Experimental Setup | 800 | 无 | T1, T2, T3 |
| 6 | Results and Discussion | 1700 | F4, F5, F7, F8, F10, F13 | T4, T5, T6, T6b |
| 7 | Ablation Study | 700 | F6, F9 | T7 |
| 8 | Parameter Sensitivity | 500 | F11(交叉引用) | T8 |
| 9 | Conclusion | 300 | 无 | 无 |
| — | **正文小计** | **8400** | — | — |
| 0 | Abstract | 250 | — | — |
| — | **总计** | **~8650** | — | — |

> 附注: 运行时间对比 T (附录 T-A5) 用 F11 散点图在主文呈现趋势; 复杂度分析用文字 + 可选 T9 表。
>
> ⚠️ **数字口径已统一为 20-DS**（见 `paper/authoritative_numbers.md`）。正文所有聚合数字（0.9574 / 88 特征 / +3.97pp vs FWPSO / +4.42pp vs W-MOPSO / 消融 +4.58/+1.63/+0.86pp）以此文件为准，禁止使用 25-DS 过时数字（0.9442 / 107 / +2.65 / +3.10 / +3.89 / +1.42 / +1.07）。

---

# 1. Introduction (~1000 words, 5 段)

**段落结构**

- **P1 问题背景 (180w)**: 高维数据（基因表达微阵列、文本、图像）维度灾难 —— 数十万特征 vs 数十样本 (p≫n)，引发过拟合、计算爆炸、可解释性差。引用: Li et al. 2017 [4], Guyon & Elisseeff 2003 [6], Bermingham 2015 [2], Glaab 2009 [1]。
- **P2 现有 FS 方法不足 (250w)**: 过滤/封装/嵌入式三类的优缺点一句话概括（详见 Related Work），点出**高维基因数据是进化特征选择的标杆场景**（N=几十, D=数千~数万）。进化方法（GA/PSO/DE）在此场景的优势与挑战。引用: Kohavi & John 1997 [12], Xue et al. PSO-FS 综述类 [23], Li 2017 [4]。
- **P3 三大不适配→引出 KDS-EL (300w)**: 以 MEL (Wang et al. TKDE 2024) 为基线，指出**通用 PSO 在高维 FS 上的三个适配缺口**（本论文核心卖点，逐条展开）:
  1. **随机初始化浪费搜索预算** —— 高维稀疏解空间中随机起点远离可行区 → MI 引导初始化;
  2. **变异算子无视特征重要性** —— 传统翻转/二进制算子均匀随机，不利用历史知识 → KER 知识引导精英翻转;
  3. **固定目标权重无法平衡探索-利用** —— 精度与特征数两个目标的权重全程固定 → 两阶段自适应权重调度。
  - 逐条引出一一对应的三个组件（MEL→MEL+MI→KDS-EL_KER→KDS-EL 的增量构建叙事在此埋下伏笔）。引用: Kennedy & Eberhart 1995 [25], Shi & Eberhart 1998 [51], MEL [Wang 2024]。
- **P4 主要贡献 (250w, 编号列表)**: 4 条贡献，每条一句话 + 支撑数字:
  1. 提出 MI 引导初始化（互信息排序 + 自适应重初始化），缓解冷启动;
  2. 提出 KER 知识引导精英翻转算子（累积特征权重矩阵 + 指数衰减），将历史知识注入变异;
  3. 提出两阶段自适应权重调度（Phase1 激进压缩 / Phase2 精细调精度），动态平衡双目标;
  4. 系统性实验: 20 数据集 × 14 方法，KDS-EL 精度 0.9574 领先定长第二名 +0.86pp、最强单目标 SOTA(FWPSO) +3.97pp、最强 MOFS(W-MOPSO-FS) +4.42pp; 特征数压缩至 88 维均值; 相比基线 MEL 3.4× 加速; 20/20 显著优于 MEL。
- **P5 论文组织 (80w)**: 标准 "本文其余部分组织如下" 一段。

**引用需求**: FS 综述 [4][6]; 基因数据 [1][2][3]; wrapper [12]; PSO 奠基 [25][51]; MEL 基线 (Wang TKDE 2024); 高维 PSO [20]。

---

# 2. Related Work (~1250 words, 5-6 段)

**段落结构**

- **P1 特征选择三范式 (250w)**: 过滤式/封装式/嵌入式定义与代表方法。
  - 过滤式: mRMR/FCBF [7 Yu & Liu], 方差/相关系数类 [5][9][10][11];
  - 封装式: 搜索+分类器评估 [12 Kohavi & John], 混合 GA [15 Oh et al.];
  - 嵌入式: L1/Lasso 类 [19 Bolasso], FS-GBDT [18], ILRC [46]。
  - 收尾点出: 高维下过滤式快但忽略交互、封装式准但搜索难、嵌入式依赖模型假设 —— 引出进化方法。
- **P2 单目标进化特征选择 (250w)**: PSO/GA/DE/ACO 等经典进化 FS。
  - BPSO [Kennedy & Eberhart 1997], ACO [50], ABC [49], GA-SVM [58];
  - 高维专用: 自适应 PSO [20 Xue et al. 2019], 渐进精化 PSO [26], 特征加权 PSO (FWPSO) [17 Wang & Jia 2022], 自适应加权 DE (SaWDE) [21 Wang et al. 2022], 重要性引导 PSO (IGPSO) [Xue & Zhang 2024], 综合评分 PSO-CSM [Wei et al. 2025]。
  - 收尾: 这些方法多靠改进搜索算子/编码，但**未系统利用"特征重要性"这类领域知识**。
- **P3 多目标进化特征选择 (250w)**: 精度 vs 特征数双目标。
  - 奠基: Xue et al. MOPSO 2012 [23], 带模糊代价的 MOPSO [28 Hu 2020];
  - MOEA 系: NSGA-II-FS, MOEA/D-FS, MOPSO-FS;
  - 高维专用: 变粒度搜索 VGS-MOEA [66 Cheng et al.], 多目标进化过滤 Hancer [67]。
  - 收尾: MOFS 保持 Pareto 前沿开销大（本实验 >110s），且固定编码高维下收敛慢。
- **P4 进化多任务学习 (200w)**: MTL 综述 [24 Zhang & Yang], 进化多任务 FS [42 Zhang Minions, 43 Chen, 44 Chen], 多任务蜂群波段选择 [40], 大尺度多目标多任务 [39]。
  - 重点介绍 **MEL 基线** (Wang TKDE 2024): 双子群多任务进化学习，D→F 双空间协同; 说明为何选它做基线（定长编码、高维高效、可增量式增强），并诚实指出其随机初始化/无知识利用/固定权重的三个局限。
- **P5 高维基因数据特征选择 (200w)**: 基因表达/微阵列场景专述。
  - 引用: [2] genomic prediction, [8] SNP selection, [9][10] 癌症分期/阿尔茨海默, [17] biomarker genes, [46] ILRC, [18] 多癌风险模块。
  - 点出: 该场景典型 "N 小 D 大"、强冗余、方法间在天花板数据集上难分伯仲 → **需同时看特征数**。
- **P6 与本文差异小结 (100w)**: 一段收束，明确 KDS-EL 的定位 —— 在 MEL 多任务框架内，用**互信息知识初始化 + 累积知识 KER 算子 + 两阶段权重调度**补足上述三个缺口，同时保持定长编码的效率优势。

**引用需求**: 覆盖 references_master 中 [1]-[68] 大部分与 [MEL][BPSO][FWPSO][SaWDE][IGPSO][PSO-CSM] 对比文献; 新增需补引: mRMR (Peng et al. 2005), VGS-MOEA [66], Demsar 2006 (统计检验, 用在 Results)。

---

# 3. Preliminaries (~450 words, 2 段)

**段落结构**

- **P1 离散 PSO / BPSO 回顾 (150w)**: 位置-速度更新公式 (Shi & Eberhart 1998 [51], Kennedy & Eberhart 1995 [25], BPSO [Kennedy 1997]), 二进制映射与 sigmoid 阈值 (thres=0.6)。一句话点出其在高维 FS 的普遍问题。
- **P2 MEL 基线概述 (300w)**: 精炼描述 MEL 双子群多任务进化学习核心机制 —— 双种群协同、特征子集/权重双表示、多任务间知识迁移; 给出其总体复杂度一行的量级 O(·); **明确说明读者可参考原论文 (Wang TKDE 2024) 获取细节**，本文只重述与后续增强相关的接口（权重表示、精英选择、目标函数定义）。给出 FS 目标函数: fitness = ws[0]·(1-Acc) + ws[1]·(Dsel/D)，为 Section 4 的两阶段调度做铺垫。

**引用需求**: [51][25][Kennedy 1997][MEL][4]。

---

# 4. Proposed KDS-EL (~1700 words, 核心章节)

**章节目标**: 完整、可复现地描述 KDS-EL = MEL + MI 引导初始化 + 权重衰减(0.99) + KER + 两阶段自适应权重调度 + 原地更新(非池化) + 自适应 MI 重初始化。配 F1 框架图 + 伪代码 + 复杂度分析。

**段落结构**

- **4.1 总体框架 (250w)**: 引导读者看 **F1** (框架图, 主文第 1 图)。用文字走一遍数据流: 原始 D 维数据 → MI 排序得分 → 初始化混合种群 (MI_init_ratio=0.5) → 迭代循环 {双目标评估 → 权重矩阵累积(KER_decay) → 精英选择(elite_k=3) → KER 翻转(90% 知识 / 10% 随机) → 两阶段权重调度 → 原地更新 → 自适应 MI 重初始化} → 输出最优子集。指出 KDS-EL 是**单流程无池化**设计（与旧版对比，强调简洁）。图: F1 (main)。
- **4.2 MI 引导初始化 (250w)**: 算法动机（随机初始化高维稀疏解浪费预算）+ 实现（互信息排序每个特征与类别标签 → 前 top-k 构建高质量起点; MI_init_ratio=0.5 混合随机个体保多样性; 二进制阈值化 thres）。给出 MI 公式。**自适应 MI 重初始化**: 停滞 stall_patience=20 代时，用最新 MI 得分重置部分个体（reinit interval=10, rounds=10），增强早熟逃逸。伪代码片段 A。引用: 信息论 MI (Cover & Thomas), [7]。
- **4.3 累积特征权重矩阵 + 权重衰减 (250w)**: 定义累积权重矩阵 W∈R^D，每次评估后按贡献更新（入选特征 +δ，未入选 -δ 或按权重），并用**指数衰减 decay=0.99** 折扣历史（防止陈旧信息累积与特征膨胀）。给出 W 更新公式与衰减公式。这是 KER 的知识底座。引用: 指数遗忘/折扣学习的一般概念 [21 相关]。
- **4.4 KER 知识引导精英翻转 (300w)**: 核心算子。
  - 选 top elite_k=3 精英个体;
  - 以 rand_flip_p=0.10 概率走"纯随机探索"分支，否则走"知识翻转"分支;
  - 知识翻转: 依 W 排序，高分特征当前=0 → 翻为 1，低分特征当前=1 → 翻为 0（翻转比例 flip_frac=0.01）;
  - 直觉解释: 把"种群累积学到的特征重要性"注入精英解，实现知识引导的局部精炼与高阶项利用。给出翻转规则公式。图: 可选 F2 (机制示意, 附录)。伪代码片段 B。
- **4.5 两阶段自适应权重调度 (300w)**: 动机（固定权重无法同时保证"先压缩后精调"）。
  - 定义 Phase 划分: 前 70% 迭代 (PhaseSplit=0.7) 用 ws=[0.7, 0.3] 激进压缩特征; 后 30% 用 ws=[0.95, 0.05] 聚焦精度。
  - 论证为何"先粗后精"优于固定/线性衰减（对比固定 ws=[0.9,0.1] 的 NoPool 变体，见 Ablation）。给出权重切换公式。**原地更新 (in-place, 非池化)** 说明: 精英个体直接被 KER 翻转后的版本替换，省去 2N 池化选择 → 更简单、更快、精度不降反升（见 7.1）。伪代码片段 C。
- **4.6 算法主流程与伪代码 (250w)**: 给出 Algorithm 1 完整伪代码（输入参数、初始化、主循环、各组件调用、输出最优子集）。图上: 伪代码 Algorithm 1 (main)。
- **4.7 复杂度分析 (100w)**: 逐组件给出复杂度并汇总为一行:
  - 初始化: MI 排序 O(D log D)（或近似 O(D)）;
  - 每代: 评估 O(N·T_eval)（T_eval = KNN 评估开销, 与所选特征相关）; 权重矩阵更新 O(N·D); KER O(elite_k·flip_frac·D); MI 重初始化（仅停滞时）O(D)。
  - 总: O(T·(N·T_eval + D·N + elite_k·D))，并对比 MEL 的 O(T·N·T_eval) 说明增量开销可忽略（用实验运行时间佐证: 51.3s vs MEL 175s，KDS-EL 反而更快因早收敛+MI起点好）。可选 T9 复杂度表 (main) 或纯文字。

**图表**: F1 (main), Algorithm 1 (main), 可选 F2 机制图 (appendix); T9 复杂度表 (main, 可选)。

**引用需求**: MI [7]/Cover & Thomas; 折扣学习 [21]; 精英策略 [12 wrapper 传统]; PSO [51][25]; MEL 基线对照 [MEL]。

---

# 5. Experimental Setup (~800 words, 4 段)

**段落结构**

- **P1 数据集 (250w)**: 20 个基准数据集，覆盖基因表达/文本/图像/语音/人工。含特征维度从 500 (madelon) 到 54675 (T1D)，样本从 36 (Adenoma) 到 2600 (madelon)。分类数与领域分布。**表 T2 (main)**。强调数据选择的两条准则: (1) 覆盖低-中-超高维; (2) 含 8 个可达精度天花板的基因数据集（为 6.4 节天花板分析铺垫）。
- **P2 对比方法 (200w)**: 14 个定长方法分三组: 基线与改进 (MEL, MEL+MI, KDS-EL_KER)、单目标 SOTA (FWPSO, PSO-CSM, SaWDE, IGPSO, BPSO)、多目标 MOFS (W-MOPSO-FS, fMOPSO-FS, NSGA-II-FS, MOEA-D-FS, MOPSO-FS)。参数取各自原论文推荐值。**表 T1 (main, 方法-文献对照摘要)**; 文献完整清单见 References。
- **P3 参数设置与实现 (200w)**: 统一 KNN(k=3) 基分类器、5-fold CV、N=20、T=100、thres=0.6、10 次独立运行。KDS-EL 全部参数（WeightDecay=0.99, PhaseSplit=0.7, ws=[0.7,0.3]/[0.95,0.05], flip_frac=0.01, MI_init_ratio=0.5, elite_k=3, rand_flip_p=0.10, KER_decay=0.9, MI 重初始化等）。**表 T3 (main)**。实现语言/硬件环境（Intel i5-13700KF, 32GB）。
- **P4 评价指标与统计检验 (150w)**: 分类精度 Acc（10 次均值±std）、特征数 Feat 与选择率、运行时间 s。统计: Friedman 排名 → Wilcoxon 符号秩检验（两两, p<0.05）→ Holm-Bonferroni 多重比较校正（vs 13 方法）。引用: Demsar 2006; [23][66] 等 MOFS 惯例。

**图表**: T1, T2, T3 (全 main)。

**引用需求**: 各对比方法原文 (BPSO/FWPSO/SaWDE/IGPSO/PSO-CSM/W-MOPSO-FS/fMOPSO-FS/NSGA-II-FS/MOEA-D-FS/MOPSO-FS/VGS-MOEA); Demsar 2006 统计检验。

---

# 6. Results and Discussion (~1700 words, 6 小节)

**段落结构**

- **6.1 总体精度对比 (300w)**: 呈现 **T4 (main)** 与 **F4** (20 数据集分组柱状图)。
  - KDS-EL Mean Acc=0.9574, 领先定长第二名 KDS-EL_KER +0.86pp、最强 SOTA FWPSO +3.97pp、最强 MOFS W-MOPSO-FS +4.42pp;
  - 在多数数据集取得最优（ALL4, ALL_AML, Colon, DLBCL, Gastric, Gastric1, Gastric2, Lymphoma, Myeloma, PCMAC, Prostate, T1D, madelon 等 13+ 个）;
  - 诚实讨论: ALL1/COIL20/SRBCT 等 3 个数据集非最优（对手 NSGA-II/W-MOPSO 达 1.0），归因于天花板效应（见 6.4）。图: F4 (main)。
- **6.2 特征数对比 (250w)**: **T5 (main 或附录, 建议 main)** 与 **F5**。
  - KDS-EL 平均特征 88（选择率 ~2-3%），远低于 MEL 2722 与 MOFS 的 3000-5300;
  - 强调"同等/更高精度下压缩 20-50×"的 Pareto 意义; 用 F12 气泡图（精度 vs 特征 vs 时间，main）直观展示 KDS-EL 位于左上（高精度、低特征）。图: F5 (main), F12 (main)。
- **6.3 统计显著性 (300w)**: **T6 (main, KDS-EL vs 13 方法胜场表)**、**T6b (main, Holm-Bonferroni 表)**、**F10** (Wilcoxon 热图, main)、**F13** (Friedman 平均排名, main)。
  - Wilcoxon: KDS-EL 20/20 优于 MEL, 19/20 优于 MEL+MI, 19/20 优于 FWPSO, 14-16/20 优于 MOFS 系;
  - Holm-Bonferroni: 13 个对手全部拒绝 H0 (p<1e-15 到 1.02e-14);
  - Friedman 排名第 1。点出"对 MOFS 胜场数较低(14/20)但 ΔAcc 显著 +3~5pp"的解读（天花板数据集上精度打平、靠特征数取胜）。图: F10 (main), F13 (main)。
- **6.4 天花板效应分析 (250w)**: 专节讨论 8 个 Acc≥0.998 数据集（ALL1, ALL_AML, Adenoma, DLBCL, Gastric2, Leukaemia, Lymphoma, SRBCT）。
  - 精度已饱和（差 <0.002, 仅 1-2 个样本），此时**特征数是唯一有意义的区分指标**;
  - KDS-EL 在此类数据集选 39~83 特征，竞争对手数百至数千 → 论证 KDS-EL 在高维基因场景的实际价值。图: F4 高亮 + F5 对比 (交叉引用)。
- **6.5 收敛性分析 (200w)**: **F8** (收敛曲线, main) 与 **F9** (两阶段收敛, main 或 ablation)。
  - KDS-EL 借助 MI 初始化快速进入高精度区，KER 提供后期精炼，两阶段调度使曲线呈"快降-平台-微升"特征;
  - 对比 MEL 缓慢收敛与 MOFS 后期停滞。图: F8 (main)。
- **6.6 运行时间分析 (200w)**: **F11** (时间散点, main); 完整逐数据集运行时间表 T-A5 (appendix)。
  - KDS-EL 51.3s 排名第 2，仅比 FWPSO 慢 1.6s;
  - 相对 MEL (175s) **3.4× 加速**（MI 起点好 + KER 精炼 + 两阶段早停，共同减少冗余评估）;
  - MOFS 全部 >110s（Pareto 维护开销），是 KDS-EL 的 2×+;
  - 高维优势最显著: T1D 比 PSO-CSM 快 2.2×, BASEHOCK 比 SaWDE 快 4.7×。

**图表**: T4, T5, T6, T6b (main); F4, F5, F7(箱线图, main, 方差稳健性), F8, F10, F11, F12, F13 (main)。附录: 全量 14×14 Wilcoxon 矩阵 (T-A3), 全量运行时间表 (T-A5), performance profile 图 (F4_pp, appendix)。

**引用需求**: 统计检验 (Demsar 2006); 各对比方法原文; MOFS 前沿维护开销讨论 [23][66]。

---

# 7. Ablation Study (~700 words, 3 小节)

**段落结构**

- **7.1 组件贡献总览 (300w)**: **T7 (main, 4 变体 × 20 数据集汇总; 全量逐数据集可放附录 T-A4)** 与 **F6** (热图/瀑布图)。
  - 消融链路: MEL(0.8868) → MEL+MI(0.9325, **+4.58pp**) → KDS-EL_KER(0.9488, **+6.20pp**) → KDS-EL(0.9574, **+7.06pp**);
  - 特征数: 2722 → 291 → 122 → 88，逐级压缩;
  - 逐组件归因: MI 初始化贡献精度提升与特征压缩双收益; KER 贡献 +1.62pp（NoPool 变体）; 两阶段调度贡献 +0.86pp 且进一步压缩特征;
  - 强调 KER 在**不增加评估开销**的前提下带来 +1.63pp 精度收益（KER 只是精英翻转，无需额外 KNN 评估之外的代价；MI 初始化贡献最大单步 +4.58pp）。图: F6_heatmap (main), F6_delta_waterfall (main 或 appendix), F6_radar (appendix)。
- **7.2 逐数据集消融分析 (250w)**: 引用 T-A4 (appendix) 或 T7 中代表行。
  - 分组讨论: (a) 天花板数据集——MI/KER 快速打满精度、特征数显著下降（如 ALL1: 4248→39, Adenoma: 2483→66）; (b) 中等难度——各组件的精度增益逐级累加（如 BASEHOCK 0.8518→0.9113, madelon 0.7521→0.8822）;
  - 指出 MEL→MEL+MI 阶段特征数骤降（2722→291）源于 MI 初始化 + 自适应重初始化的"起点+逃逸"双重作用。
- **7.3 两阶段调度与原地更新验证 (150w)**: KDS_EL_NoPool(固定 ws=[0.9,0.1] + 原地更新) vs KDS-EL(两阶段)。
  - 精度 0.9488→0.9574 (+0.86pp), 特征 122→88, 时间 54.2→51.3s（20-DS 同批对比）;
  - 逐数据集: 以 T7 (20-DS) 为准，KDS-EL 在绝大多数数据集不劣于 NoPool;
  - **F9** (两阶段收敛对比, main): Phase2 权重切换后精度再提升、特征进一步压缩的可视化证据。同时一句话回应旧版池化/DRS 已弃用（附录或脚注），保持方法叙事简洁。

**图表**: T7 (main), F6 (main), F9 (main); 附录: T-A4 全量逐数据集, F6_radar, F9_nhd_diversity (弃用指标, 可删除)。

**引用需求**: MEL 基线 [MEL]; 无新增强依赖（自我消融）。

---

# 8. Parameter Sensitivity Analysis (~500 words, 3 段)

**段落结构**

- **P1 敏感性分析协议 (100w)**: 在 4 个代表数据集 (Adenoma, Colon, ALL4, BASEHOCK) 上逐一变化 5 参数（其余默认），报告平均 Acc/Feat/Time。**表 T8 (main, 汇总表)**; 各参数全量表放附录 T-A6。
- **P2 逐参数解读 (300w)**: 引用 T8 五行（每参数 2-3 句）:
  - WeightDecay (0.9~1.0): 最优 0.99，稳定区间 [0.95,0.995]; 不衰减(1.0)特征膨胀 40%;
  - PhaseSplit (0.3~0.9): 最优 0.7，稳定 [0.6,0.8]，波动 <0.5pp;
  - flip_frac (0.005~0.10): 最优 0.01（约每 100 维翻 1 个特征），过大随机性主导;
  - MI_init_ratio (0.0~1.0): **最敏感参数**，最优 0.5，全 MI 早熟 / 无 MI 冷启动;
  - elite_k (1~10): 最优 3（种群 15%），过多稀释。
- **P3 鲁棒性结论 (100w)**: 全部 5 参数波动 ≤±1.5pp → 默认配置可直接用于新数据集，无需逐数据集调参; 强调 MI_init_ratio 与 flip_frac 是应用时优先保持默认的两个参数。

**图表**: T8 (main); T-A6 (appendix, 5 张参数-表)。

**引用需求**: 无需新引用（自我分析）。

---

# 9. Conclusion (~300 words, 2 段)

**段落结构**

- **P1 总结 (180w)**: 回顾 KDS-EL 三大组件如何对应解决三大不适配; 重申关键数字（0.9574 Acc, 88 特征, 20/20 Wilcoxon, 3.4× 加速, ≤1.5pp 敏感性）。一句话定位: 在高维 FS 上同时实现"精度-稀疏性-效率"三赢的定长进化方法。
- **P2 局限与展望 (120w)**: 局限: (1) MI 排序在高维仍 O(D log D)，D>10^5 时需近似; (2) 未覆盖多标签/流式特征选择场景; (3) 未与深度嵌入方法结合。展望: 大规模 GPU 加速的 MI 近似、扩展到多标签与类别不平衡数据、与 transformer 特征表示结合、跨数据集迁移（multi-task 扩展）。

---

# 0. Abstract (~250 words)

- 背景一句 → 问题（三大不适配）一句 → 方法三组件各一句 → 结果三句（精度/特征/统计/效率）→ 意义一句。附 5-6 个关键词（Feature selection, High-dimensional data, Particle swarm optimization, Mutual information, Knowledge-guided search, Two-phase weight scheduling）。

---

# 附录结构 (Appendix)

| 编号 | 内容 | 对应主文 |
|---|---|---|
| A1 | 全量逐数据集精度表 (14 方法, mean±std) | T4 简化版 |
| A2 | 全量逐数据集特征数表 (含选择率) | T5 简化版 |
| A3 | 全量 14×14 Wilcoxon 矩阵 | T6 (KDS-EL 行) |
| A4 | 全量逐数据集消融表 (4 变体 Acc+Feat) | T7 汇总 |
| A5 | 全量逐数据集运行时间表 (14 方法) | F11 散点 |
| A6 | 5 参数敏感性全量表 | T8 汇总 |
| A7 | (可选) MOFS 扩展对比 (VGS-MOEA 等) | Section 6 交叉引用 |

---

# 主文 vs 附录 图表清单汇总

**主文 (Figures)**: F1 (框架), F4 (精度), F5 (特征), F7 (箱线图), F8 (收敛), F10 (Wilcoxon 热图), F11 (时间散点), F12 (气泡), F13 (Friedman 排名), F9 (两阶段收敛), F6 (消融热图/瀑布, 选 1-2 张)。Algorithm 1 伪代码。
**附录 (Figures)**: F6_radar, F4_performance_profile, F2 (KER 机制示意, 可选), F9_nhd_diversity (建议删除——NHD 指标已弃用)。

**主文 (Tables)**: T1 (方法-文献), T2 (数据集), T3 (参数), T4 (精度), T5 (特征, 可下放附录), T6 (Wilcoxon), T6b (Holm), T7 (消融汇总), T8 (参数敏感性汇总), T9 (复杂度, 可选)。
**附录 (Tables)**: A1-A7 如上。

> **排版决策建议**: 若 ASOC 单栏 LaTeX 版面紧张，优先将 T5 (特征数)、T7 逐数据集细化、T9 下放附录; 主文保留 F4/F5 图以承载特征-精度双信息。

---

# 引用需求按节汇总 (References)

| Section | 必引 | 建议补引 |
|---|---|---|
| 1 | [4][6][2][12][25][51], MEL | Peng mRMR 2005; Demsar 2006 |
| 2 | [4][5][6][7][9][10][11][12][15][18][19][46], BPSO/FWPSO/SaWDE/IGPSO/PSO-CSM, [23][28][66][67], [24][42][43][44][39][40], MEL, [2][8][9][17][18][46] | Peng mRMR; FS 最新综述 (2023-2025) |
| 3 | [25][51], Kennedy1997, MEL, [4] | — |
| 4 | [7] (MI), [21] (自适应加权/折扣), MEL, [25][51] | Cover & Thomas (MI 教材); 指数遗忘学习 |
| 5 | 14 个对比方法原文, Demsar 2006, [23][66] | Holm-Bonferroni (Holm 1979) |
| 6 | Demsar 2006, 各对比原文, [23][66] | Friedman test (Friedman 1937/1940) |
| 7 | MEL | — |
| 8 | — | — |
| 9 | MEL | — |
