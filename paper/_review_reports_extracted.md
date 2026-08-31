########## TRANSCRIPT LINE 120 ##########

我已完成对 17 页论文全文（extracted_text.txt，16 页正文）的完整读取与主编视角评审。以下为独立评审报告。

---

# 副主编评审报告（Editor-in-Chief / Associate Editor 视角）

**投稿标题**：Multi-Task Particle Swarm Optimization with Knowledge-Guided Elite Refinement and Two-Phase Weight Scheduling for High-Dimensional Feature Selection
**建议期刊定位**：Expert Systems with Applications / Swarm and Evolutionary Computation 级别（Q1）
**评审范围**：仅主编视角（期刊适配、原创性、整体质量、读者价值），不深入方法学细节

---

## 1. 总体评价

论文提出 KDS-EL（Knowledge-Guided Dual-Phase Swarm Evolutionary Learning），在直接前身 MEL（IEEE TKDE 2024）的双子种群多任务 PSO 骨架上叠加三个机制——MI 引导初始化+自适应重注入、基于累积特征重要度的精英细化（KER）、两阶段权重调度（TPS）——统合为"闭环知识引导"框架。整体写作专业、结构完整，实验规模（20 数据集 × 14 方法 × 10 次运行）与统计协议（Friedman / Wilcoxon / Holm–Bonferroni）达到 Q1 门槛，消融与参数敏感性分析设计规范，且明确面向高维基因表达生物标志物发现（RT-qPCR 可验证性叙事），契合 ESWA 读者群。主要短板：相对 MEL 的原创性增量有限且最大贡献机制的创新度最低；统计显著性 p 值报告口径不清、与胜/平计数自相矛盾；多处命名与数值不一致（表列标错、图/文秩不一致、MEL 归属作者错误）。建议 **Major Revision**。

## 2. 推荐意见

**Major Revision**，置信度 **4/5**。
理由：实验证据的体量与规范化程度足以支撑 Q1 发表，但统计报告的可复现性、原创性归因的干净程度、以及多处数据/命名不一致必须在重投前解决。

## 3. 优点 S1–S3

**S1. 实验规模与统计协议达到 Q1 门槛，且证据结构完整。**
20 个数据集（D∈[500, 54,675]，n∈[36, 2,600]，Table 3）× 14 方法 × 10 次独立运行（Section 5.1.3），并严格采用 Demšar 协议：Friedman 平均秩、配对 Wilcoxon、Holm–Bonferroni 校正（Section 5.1.4 / 5.4）。除主对比外还覆盖 ceiling-effect 分析（Section 5.5）、收敛动态（Fig. 5）、运行时与 Pareto 前沿（Section 5.7 / Fig. 6）、逐机制消融（Table 9）与五参数 OFAT 敏感性（Section 5.9 / Table 10）。Table 5 逐数据集给出 +/≈/− 标注，便于读者独立核查——这是高水平投稿的标志性做法。

**S2. 消融叙事诚实且口径统一（subtractive reading）。**
Table 9 把完整 KDS-EL 当主角、逐层剥离量化边际贡献（w/o TPS −0.86pp；再 w/o KER −1.63pp；MEL −4.58pp），避免了 incremental addition 的批评；5.8.3 还补充了 in-place replacement 对比 2N pooling 的设计验证。效率上也如实报告"排名第二、落后 FWPSO 仅 1.7 秒"（Section 5.7），而非只报 3.4× 对 MEL 的加速，增加了可信度。

**S3. 论证链与读者价值清晰。**
"PSO 三缺陷 → 三机制 → 闭环框架"的因果链在摘要、引言（Section 1）、方法（Section 4）与结论（Section 6）口径一致；"soft MI seeding vs hard truncation""bounded KER budget（ke=3）""Phase 1 稀疏压缩 / Phase 2 精度精修"等定位（Table 1、Section 2.5）具说服力。高维基因表达 + 临床生物标志物（40–80 基因签名可直接 RT-qPCR 验证，Section 5.5）对 ESWA/SWEVO 读者有明确吸引力，且引用多为 2024–2026 年同刊论文（[14][15][29][41]），定位精准。

## 4. 缺点 W1–W5

**W1（Critical→Major）：统计显著性 p 值报告口径不清且与自身胜/平计数自相矛盾。**
Table 8 对全部 13 个对手（含仅 13 胜 7 平 0 负的 KDS-EL w/o TPS，Table 7）均报告 p < 10⁻¹⁵。但对 20 个数据集做配对单侧 Wilcoxon 时，13 个非零差分的检验 p 值**下限**约为 (1/2)¹³ ≈ 1.2×10⁻⁴，**数学上不可能**达到 10⁻¹⁵。除非 "Combined p" 是 20 个数据集内检验的 Fisher 组合（meta-analysis），但正文与表注（"Combined p and Holm p represent unadjusted and adjusted p-values"）均未说明组合方式、自由度与数据来源。摘要与结论（第 16 页）却直接引用 "p < 10⁻¹⁵" 作为卖点。为何重要：统计严谨性直接关系证据强度判定，夸大或不可复现的证据会削弱整篇可信度。建议：明确 Fisher 组合公式与各数据集 p 值来源；摘要只保留"全部 13 对手在 α=0.05 水平显著"这一可辩护结论。

**W2（Major）：表列命名错误——"w/o KER"实为"w/o TPS&KER"。**
Table 5 第三列均值 0.9325、Table 6 第三列 290.6，与 Table 9 的 "KDS-EL w/o TPS&KER"（0.9325 / 291）完全一致，但列标题仅写 "w/o KER"。字面解读会误以为该变体仍保留 TPS、只去掉 KER（那是一个不同的消融点）。同时同一数值在正文 Section 5.3 写 290.5、Table 6 写 290.6、Table 9 写 291，三处不一致。建议统一全表列名与数值。

**W3（Major）：正文对直接前身 MEL 的作者归属错误。**
Section 2.3（"Zhang et al. [12] introduced Multi-Task Evolutionary Learning"）与 Section 3.3（"recently proposed by Zhang et al. [12]"）均写 "Zhang et al."，但参考文献 [12]（第 16 页）第一作者为 **X. Wang**（Wang, Shangguan, Huang, Wu, Jia, IEEE TKDE 2024）。对直接前身方法的事实性归属错误必须修正。

**W4（Major）：原创性增量有限，且消融贡献排序与标题主打机制错位。**
消融显示最大贡献者是 MI 引导初始化（−4.58pp，Table 9），而它恰恰是三个机制中新颖性最低的——论文自己承认 "one-shot offline injection"（MI-MPODE [15]、FWPSO [8] 已做 MI 排序初始化，Section 2.4）是已有范式；标题主打的 KER 与 TPS 分别只贡献 1.63pp 与 0.86pp。更关键的是，消融链最后一环 "MEL" 并**不等价于**"仅去掉 MI 初始化"：MEL 在 W 矩阵累积规则、记忆折扣、子种群机制上与 KDS-EL 存在论文自己列出的多项差异（Section 2.3 的三个 MEL 瓶颈），因此将 4.58pp 全部归因于 MI 初始化在归因上不干净。建议补充"仅移除 MI 初始化、保留 KER/TPS 与 W 更新规则"的中间变体以支撑归因。

**W5（Minor）：多处数据/表述不一致损伤证据可信度。**
(a) **Friedman 秩文本与图矛盾**：Fig. 4 中 fMOPSO 5.90 / FWPSO 6.20 / NSGA-II 6.93 / MOEA-D 7.78 / PSO-CSM 8.60 / BPSO 13.35，而正文 Section 5.4.3 写为 5.75 / 6.10 / 6.25 / 6.80 / 7.15 / 13.80，两套数字对不上；(b) Section 5.3 声称特征缩减"20-至 50-fold"，但对最强单目标 FWPSO 仅 1068.9/87.8 ≈ 12 倍；(c) Section 5.3 的 FSR "约 2–3%"若按全体特征总量计算实为 87.8/10,993 ≈ 0.8%，口径不清。建议逐表核对并统一表述口径。

## 5. 分节详细评论（主编视角相关部分）

**标题与摘要**
标题不含缩写 KDS-EL，且与正文方法名"Dual-Phase"不一致（标题用"Two-Phase Weight Scheduling"，缩写全称用"Dual-Phase Swarm Evolutionary Learning"）。摘要数据内部自洽（0.9574 / 87.8 / +3.97 / +4.42 均与 Table 5 吻合），但"Wilcoxon+Holm 确认显著"未披露组合检验口径（见 W1）。Highlights 5 条均准确（95.74% 与 87.8 特征与正文一致），与正文/摘要无实质出入，仅建议标题纳入 KDS-EL 或统一 Two-/Dual-Phase 用词。

**引言**
问题定位清晰，"随机初始化浪费评估预算 / 均匀扰动丢弃跨代知识 / 静态权重不适应阶段"三缺陷框架明确，贡献清单与三个机制一一对应。但"3.4× 加速"作为开篇卖点应注明 KDS-EL 在 14 方法中效率仅居第二（Section 5.7）。

**文献综述（Section 2）**
组织良好，明确对位 MEL 与 MOFS 的瓶颈，Section 2.5 的差异化定位（soft seeding vs hard truncation、online distillation vs memoryless mutation、dynamic vs static weights）是全文最有说服力的部分。但存在 MEL 归属错误（W3）；且综述承认 MI 预排序已有先例，反而弱化了第一个机制的原创性主张。

**方法（Section 4）**
算法 1/2 完整可复现，KER 的评估开销被严格界定（ke=3，Section 4.4.1）；复杂度分析诚实（与 MEL 同渐近阶，实际加速源于稀疏化，Section 4.7.2）。一个值得向作者核实的技术点：KER 扰动预算 ⌊ϕD⌋ 随维度线性增长，T1D（54,675 维）单次扰动约 547 个特征，而敏感性分析（Table 10）只在 ≤12,625 维数据集上测试，T1D 上的 ϕ 行为未被覆盖。

**结果（Section 5）**
全文最强部分，但承载了主要问题：统计口径（W1）、消融归因（W4）、"w/o KER"列标错（W2）、Friedman 秩图/文矛盾（W5）。ceiling-effect 处理（Section 5.5）值得肯定——8 个饱和数据集上以特征数作为判别指标，是诚实且专业的做法。另需提示：以标量化加权和方法对比输出 Pareto 前端的 MO 方法，属于"单点 vs 前沿"的非对称比较，论文仅在 5.2 用文字说明而未讨论协议差异，建议在重投时明确 MO 方法报告点的选取规则。

**讨论**
无独立 Discussion 节；Section 5.5（ceiling effect）、5.6（收敛）、5.9（敏感性）部分承担了讨论职能，可接受。

**结论**
与摘要/正文数据一致，但再次引用 p < 10⁻¹⁵（W1）。未来工作（多标签、流式 FS、深度特征）合理。

**参考文献**
47 条，时效好（多为 2024–2026），格式规范，覆盖 ESWA/SWEVO/TEVC/TKDE 核心出处。主要问题是 [12] 作者与正文归属不一致（W3）。

## 6. 给作者的问题

1. Table 8 的 "Combined p" 究竟如何组合？在 13 胜 7 平（Table 7）下，20 数据集配对的单侧 Wilcoxon p 值下限约为 1.2×10⁻⁴，无法达到 <10⁻¹⁵；若为 Fisher 组合，请给出公式、自由度与各数据集 p 值来源，并相应弱化摘要/结论中的表述。
2. Fig. 4 的 fMOPSO/FWPSO/NSGA-II/MOEA-D/PSO-CSM/BPSO 秩与 Section 5.4.3 正文数值不一致，哪套是正确结果？请统一并附 Friedman 统计量。
3. 消融链最后一环 "MEL" 是否仅等于"去掉 MI 初始化"？请提供"保留 KER/TPS/W 更新规则、仅移除 MI 初始化"的中间变体，以支撑 Table 9 中 4.58pp 的归因。
4. 标题为何不含缩写 KDS-EL，"Two-Phase"与"Dual-Phase"是否应统一？Table 5/6/7 的 "w/o KER" 列实际对应 "w/o TPS&KER"，可否修正列名？

## 7. 维度评分（0–100）

| 维度 | 权重 | 得分 | 说明 |
|---|---|---|---|
| Originality | 20% | 60 | 相对 MEL 为集成式增量，三机制各自有先例，最大贡献机制新颖性最低 |
| Methodological Rigor | 25% | 70 | 实验协议规范，但统计 p 值口径不清、MO 对比协议非对称 |
| Evidence Sufficiency | 25% | 75 | 规模充分，但 Friedman 秩图/文矛盾、特征数三处不一致损伤信任 |
| Argument Coherence | 15% | 72 | 三缺陷→三机制叙事连贯，但命名/缩写/表列不一致 |
| Writing Quality | 15% | 78 | 专业、结构完整，MEL 归属错误等事实性瑕疵待修 |
| **加权平均** | | **71** | |

**结语**：这是一篇实验证据扎实、叙事清晰、应用价值贴合期刊定位的高维特征选择论文，修稿潜力高。作者若能解决统计报告口径、原创性归因与若干数据/命名不一致问题，可在重投后达到发表标准；建议接受 Major Revision 并交由两名方法学评审人对统计协议与 MEL 增量做专项复核。

########## TRANSCRIPT LINE 120 ##########

agentId: a5b41fdcf48ea16b6 (use SendMessage with to: 'a5b41fdcf48ea16b6' to continue this agent)
<usage>total_tokens: 73839
tool_uses: 9
duration_ms: 168032</usage>

########## TRANSCRIPT LINE 121 ##########

I have now read the full paper (all 17 pages / 16 text pages). Below is my independent review.

---

# Peer Review 2 — 领域评审报告

**论文标题**：Multi-Task Particle Swarm Optimization with Knowledge-Guided Elite Refinement and Two-Phase Weight Scheduling for High-Dimensional Feature Selection
**稿件编号**：匿名双盲
**评审人角色**：Peer Reviewer 2（高维特征选择 / 生物标志物 / MI filter / 进化 wrapper 方向）

---

## 1. 总体评价

这是一篇方法清晰、实验量大、统计规范的高维特征选择论文。KDS-EL 在 MEL 双子群多任务骨架上叠加 MI 软播种 + 自适应重注入、带指数遗忘的知识引导精英精炼（KER）、两阶段权重调度（TPS）三个机制，用 20 个数据集（D 最高 54,675）与 10 个外部进化基线做了成体系对比，消融链条（Table 9）单调递减、统计检验（Friedman/Wilcoxon/Holm–Bonferroni）符合 Demšar 协议，工程完整性较高。但作为领域评审人，我对其**CV 协议中的数据泄漏风险**（MI 先验向量 m 究竟在何处计算）高度关切，这直接关系到"0.9574 精度 / 87.8 特征"这一核心主张的可信度；此外，MEL 对比的忠实度、MI 播种相对 MI-MPODE/NNS-DFPG-CSA 的新颖性、缺失非进化与近期知识引导基线、"RT-qPCR 直接验证"的临床宣称均需实质修订。方法学潜力真实存在，但当前证据链不足以支撑"最佳分类性能"与临床可转化性的表述。

## 2. 推荐意见

**Major Revision**（重大修改）
置信度：**4/5**（介于"大概率成立"与"需要验证"之间，关键在于 W1 的泄漏问题若确认则可能降为 Reject & Resubmit）

## 3. 优点

- **S1. 结构自洽的三机制设计，直指 MEL 的三个明确缺陷。** Section 4.1–4.6 对 MI 软播种（式 8–10）、KER（式 12–18, Algorithm 1）、TPS（式 19–20）的数学刻画完整，且每个机制都能在 Section 3.3 对 MEL"随机初始化 / 无衰减记忆 / 静态权重"三个瓶颈上找到一一对应；KER 的评估预算严格有界（ke=3，Algorithm 1 与 Section 4.4.1），复杂度分析（Section 4.7，式 21–25）交代了离线 MI 与迭代主循环的量级。
- **S2. 减法消融链条干净，且做了逐数据集拆解。** Table 9（第 14 页）给出 KDS-EL→w/o TPS→w/o TPS&KER→MEL 的单调退化（0.9574→0.9488→0.9325→0.8868），Section 5.8.2 又按"天花板数据集 / 中难度数据集"两族分别解释退化形态（如 BASEHOCK 0.9113→0.8997→0.8597→0.8518），比单纯报均值更可信。
- **S3. 统计验证遵循多数据集标准协议，且参数敏感性充分。** Section 5.4 采用 Friedman 秩检验 + 逐对 Wilcoxon + Holm–Bonferroni 校正（Table 7–8），符合 Demšar [45] 建议；Section 5.9 对 γ、α、ϕ、ρ、ke 五个超参做 OFAT 敏感性分析并给出稳定区间（Table 10），默认参数鲁棒性论证到位。
- **S4. 以特征稀疏性而非仅精度立论，天花板分析与 Pareto 视角有说服力。** Section 5.5 明确 8 个天花板基因数据集（ALL1、ALL_AML、Adenoma、DLBCL、Gastric2、Leukaemia、Lymphoma、SRBCT）上精度饱和、以特征数论英雄，并用 Fig. 6 的准确率-特征数 Pareto 图展示 KDS-EL 的相对优势（如 ALL1 仅 39 特征 vs MEL 4,248、NSGA-II-FS 2,847），这比单纯比较精度更贴合高维生物标志物场景。

## 4. 缺点

### W1（严重级：Critical）——CV 协议中 MI 先验向量的计算位置不明，存在测试折信息泄漏风险

**问题与引用**：Section 5.1.1（第 9 页）声明"stratified 5-fold cross-validation with random shuffling is strictly enforced. The cross-validation partitioning is performed prior to feature selection, ensuring that candidate subsets are evaluated strictly on validation folds."但 MI 先验向量 m（式 8，第 5 页；Algorithm 2 第 1 行 Stage 1，第 8 页）被多处描述为在**整个数据集上离线计算一次**：Section 4.1 Stage 1 称"Mutual information (MI) between each feature and class labels is **computed once prior to evolution**"（第 6 页），Section 4.7.1 复杂度分析也称"this step is **executed only once** prior to the evolutionary loop"（第 7 页）。若 m 在 5 折划分之前于全数据上计算，则每一折测试折的标签信息都已渗入 MI 播种（式 9）与自适应重注入（式 11）所构造的初始搜索盆地。而消融显示 MI 初始化+重注入恰是**最大贡献源**（4.58pp，Table 9），泄漏会直接虚增 KDS-EL 相对一切无 MI 先验方法的优势。论文从未明确"每折在训练子集内重算 m"，也未说明式 (20)/Algorithm 2 第 27 行所用的**内层 5 折 CV 精度**与外层 5 折报告协议之间如何嵌套。
**为何重要**：这不是措辞问题，而是决定了"0.9574 / 87.8"是否成立的根本问题。KDS-EL 的精度优势恰由 MI 播种带来的早收敛与稀疏化驱动（Section 5.6 收敛曲线、Table 9 的 4.58pp），若先验来自全数据，则优势部分为泄漏假象，且**所有 13 个对比方法的相对结论均被扭曲**。
**修改建议**：明确写出嵌套协议——"对外层每个测试折：仅在剩余 4 折训练子集上重算 m、重跑 Algorithm 2，用 gbest 在外层测试折上打分；内部 5 折仅用于 wrapper 适应度估计"。若当前实现确为逐折计算，请在正文明确并在复杂度分析中将 T_pre 改为 O(5·(D·Nsamp_tr + D log D))；若为全数据计算，则必须修正后重跑全部实验。
**严重级**：Critical（若无法澄清，核心结论不可采信）。

### W2（严重级：High）——MEL 复现忠实度存疑，且消融末段把"MEL 基线"当作"KDS-EL 剥掉 MI 初始化"，归因混杂了骨干实现差异

**问题与引用**：Table 5/6（第 11 页）报告 MEL 平均精度 0.8868、平均特征 2,722.2、运行 175.0 s（Section 5.7），KDS-EL 相对 MEL 提升 7.06pp（第 10 页）。Section 5.1.2 只称"All comparison algorithms adopt the hyper-parameter settings recommended in their original publications"，未说明是否使用 MEL 原作者代码/官方实现。更关键的是 Section 5.8.1 第 3 点把"Stripping the MI-guided initialization and adaptive re-initialization … reduces the framework to the unguided multi-task swarm (MEL [12])"，据此把 4.58pp 全部记在"MI 初始化"名下；但 KDS-EL 无 TPS&KER 变体（0.9325，保留 MI init，Table 4 参数 ρ=0.50）与作者重实现的"standard MEL"之间，除 MI 播种外还差着 P2 子群的 W 引导采样（Algorithm 2 第 22–24 行 Pj=1/(1+exp(−Wj))）、Heaviside 阈值化（式 10）等骨干细节。因此 4.58pp 是"MI 初始化+骨干实现差异"的混合效应，直接记在单一机制头上是过度归因。
**为何重要**：MEL 是 TKDE 2024 的工作，是本文最直接的对照；若复现水平低于 MEL 原文（原文若干数据集报告精度明显更高），则"KDS-EL 大胜 MEL"与"MI 是最大贡献者"两条叙事同时被削弱。
**修改建议**：(a) 说明 MEL 复现是否来自官方代码，并给出与 MEL 原文重叠数据集上的精度对照表以证忠实；(b) 将消融末段改为"KDS-EL w/o MI seeding"（在同一骨干下仅关闭式 9/11），再与标准 MEL 基线并列，使"MI 播种的净贡献"与"MEL 基线水平"两个量分离。
**严重级**：High。

### W3（严重级：Medium-High）——基线全部是进化算法，"best classification performance"主张范围过窄；且引用了近期知识引导方法 KMHBO [41] 却不做对比

**问题与引用**：Section 5.1.2 的 14 个方法中，3 个是本文自己的消融变体，1 个是 MEL，外部基线仅 10 个且全部为 EC（5 单目标+5 多目标，Table 2）。缺少任何**纯 filter**（如 mRMR [17] 定长 top-k + kNN）与 **embedded**（LASSO/Bolasso [20]）基线，因此摘要与结论中"KDS-EL achieves the best classification performance"（第 2 页 Abstract、第 16 页 Conclusion）只在"进化方法间"成立——而 mRMR+kNN 或 Bolasso 在多数这些数据集上的精度/特征数常不劣于或优于包装法。同时，Section 2.4（第 4 页）明确引用了 2026 年的知识引导高维 FS 方法 KMHBO [41]，却未纳入 14 个对比之列，属于"引了却不比"。
**为何重要**：领域读者关心的是 KDS-EL 相对"最好用/最相关"的工具是否真的更好，而非相对一组进化基线是否最好。缺 filter/embedded 会让"最佳性能"主张在方法学上显得局促；缺 KMHBO 则错失了与"同类知识引导 2024–2026 工作"的直接对位。
**修改建议**：至少补 (i) mRMR-top-k+kNN、(ii) Bolasso/LASSO、(iii) KMHBO [41] 三个基线（后二者已有引用，实现成本可控）；并将所有"best / optimal"表述限定为"among the compared evolutionary methods"。同时将 Abstract 中"all 13 competitors"改为不把 3 个自家消融变体计入"state-of-the-art competitors"之数。
**严重级**：Medium-High。

### W4（严重级：Medium）——MI 播种相对 MI-MPODE/NNS-DFPG-CSA 的新颖性被夸大，且 MI 估计与多类处理完全未交代

**问题与引用**：Section 2.5 第 1 点宣称"Soft filter-wrapper seeding vs. hard truncation…KDS-EL uses normalized MI scores as continuous Gaussian-perturbed seeds, preserving the full search space"。但 Section 2.4 自己写道 MI-MPODE [15] 和 NNS-DFPG-CSA [14] "compute MI rankings offline and **initialize the population** or restrict the search space to the top-k"——即 MI 排序初始化人口本身在 [14,15] 已存在；KDS-EL 的增量只是"归一化软种子 + 高斯噪声 + 自适应重注入"，属同一范式内的改进而非范式差。此外：式 (4)（第 4 页）对连续微阵列特征求 I(fj;Y) 需离散化/密度估计，但全文未给出估计器（直方图分箱？kNN 互信息估计器？），无法复现；对 20 类 COIL20 与 26 类 ISOLET（Table 3，第 9 页），式 (4) 的 H(Y) 随 log C 增长，MI 绝对值被压低、每特征信号噪声比下降，且两数据集的 FSR（84/1,024≈8.2%、60/617≈9.7%）显著高于基因集，说明"θ=0.60 保证稀疏种子（∥x∥0≈0.15–0.30D）"的论断（第 5 页）在多类数据上是否仍成立完全没有讨论。
**为何重要**：新颖性主张（贡献 1）与可复现性（式 4 的估计方式）直接受影响；多类场景是多类 FS 用户的最常见实际需求。
**修改建议**：明确 MI 估计器与分箱参数；补充 COIL20/ISOLET 上 MI 播种的实际稀疏度与是否有针对多类的处理；在贡献 1 的定位里承认 MI 初始化来自 [14,15] 的血统，把差异点收敛到"soft continuous seeding + adaptive re-injection"上。
**严重级**：Medium。

### W5（严重级：Medium）——临床/实际转化主张过度宣称，且仅有 kNN 单一分类器

**问题与引用**：Section 5.5（第 13 页）称"a compact gene signature of 40–80 biomarkers **can be directly validated via RT-qPCR assays**, analyzed through pathway enrichment, and translated into cost-effective diagnostic panels"。但所选特征是以 kNN(k=3) 的 5 折 CV 精度为适应度函数（式 20）优化出来的，选出的 40–80 基因是"让 kNN 在 36–173 个样本上分开的训练集判别特征"，既无跨折/跨 10 次运行的**特征稳定性**报告，也无任何独立生物学/临床验证（无外部数据集、无 RT-qPCR 实测、无通路富集分析实际结果），"directly validated"是对方法学产物的过度宣称。同时，全部结论建立在 kNN 单分类器上，未给出 SVM/RF/逻辑回归下的泛化验证；在 Adenoma(n=36) 上选 66 基因（Table 6）是典型的过拟合风险区。
**为何重要**：生物标志物领域的核心可信度标准是"稳定、可复现、跨分类器稳健"。kNN 特异性选择会让特征集随分类器迁移而崩坏，"临床可转化"主张将沦为修辞。
**修改建议**：删除或降级"RT-qPCR 直接验证"的表述，改为"规模落在临床可验证范围内，但需后续稳定性与湿实验验证"；补充至少 1–2 个替代分类器（SVM/RF）下的特征子集泛化评估；报告跨折/跨运行的特征重合率（如 Jaccard 稳定性指标）。
**严重级**：Medium。

## 5. 分节详细评论

### 5.1 文献综述（Section 2）
- **覆盖较全但偏"进化方法中心"**：filter/wrapper/embedded 三分（2.1）、MOFS（2.2）、EMTO（2.3）、知识引导元启发（2.4）脉络清晰，对 EMTO 相关工作（[36–40]）与知识引导（[14,15,41]）的盘点在进化框架内是合格的。
- **遗漏**：(i) 未讨论特征选择结果的**稳定性（stability）**文献——这恰是生物标志物可复现性的关键维度；(ii) 知识引导小节仅限 MI，未覆盖如基尼/卡方/拉普拉斯打分引导、以及近年 transformer/深度表示做先验的工作；(iii) KMHBO [41] 只引不比（见 W3）。
- **理论框架恰当性**：以 PSO、BPSO、MI、EMTO、知识引导元启发五个支柱定位 KDS-EL 是合理的；但缺少对"MI 在高维连续特征上的估计误差随 p≫n 的退化"的讨论，这直接影响软播种先验的质量上限。

### 5.2 方法（Section 3–4）
- **理论与符号清楚**：式 (1)–(10) 的 PSO/BPSO/MI/播种定义规范；KER 的方向翻转得分（式 16–17）与 1-to-1 贪心替换（式 18）逻辑自洽；TPS 的相变（式 19）直观。
- **三处需注意**：
  1. MI"offline/once"的表述与逐折重算的冲突（W1）。
  2. KER 的翻转预算 ϕ=0.01 在 D=54,675 的 T1D 上约为 547 个特征被翻转/精英，Section 5.9.1 又称该值"localized、约每 100 维翻 1 维"——比例上如此，但**绝对翻转数随 D 线性放大**，"localized elite refinement"的措辞对超高阶数据集有误导，建议在正文按数据规模说明。
  3. Section 4.7.2 声称"per-evaluation over an order of magnitude faster"，但其论证基于 dKDS−EL≈88；而初始 MI 种子的 ∥x∥0≈0.15–0.30D（T1D 上约 8,000–16,000 维，第 5 页），搜索前期每评估成本远高于"88 维"，3.4× 的实测加速是可信的，但"数量级更快"的推演前提不成立，建议改写为纯经验表述。

### 5.3 实验设置与数据集（Section 5.1）
- **数据集构造是优点**：20 个数据集覆盖基因表达（15）、文本（2）、图像（1）、语音（1）、合成（1），D∈[500, 54,675]，17 个 p≫n（Section 5.1.1），并显式纳入了 8 个天花板数据集与 n 低至 36 的 Adenoma，挑战度合理。
- **对比协议问题**：全部对比方法共用 N=20、T=100（Section 5.1.3）——这对 MEL（原论文常使用更大 N/T）可能并非其推荐设置，进一步加重 W2 的复现疑虑；kNN(k=3) 单分类器（见 W5）。
- **统计框架**：Friedman + Wilcoxon + Holm–Bonferroni 到位；但注意 **Fig. 4 与正文秩值不一致**——正文（第 14 页）称 fMOPSO-FS 5.75、FWPSO 6.10、NSGA-II-FS 6.25、MOEA-D-FS 6.80，而图内数值为 5.90、6.20、6.93、7.78，需统一。

### 5.4 结果（Section 5.2–5.9）
- **Table 5/6 的可读性**：+ / ≈ / − 逐数据集标注（基于 10 次配对运行的两侧 Wilcoxon）是加分项；Table 6 特征数对比（87.8 vs MEL 2,722.2 vs MOPSO-FS 5,263.3）极具冲击力。
- **对反例的处理诚实**：ALL1/SRBCT 上多目标方法取 1.0000、BASEHOCK/COIL20/ISOLET 上 NSGA-II-FS 精度略高（第 10 页），论文用天花板波动与大特征数代价解释，态度可接受。
- **消融的归因问题**：见 W2。另注意 Section 5.8.1 第 1 点把"去 TPS"记 -0.86pp，但 w/o TPS 用的是固定权重 ws=[0.90,0.10]（Table 4），其特征权重(0.10)低于 Phase 1 的 0.30，故特征数上升（87.8→121.7）是预期内，逻辑自洽。
- **参数敏感性**（Section 5.9）是本文亮点之一，五个超参的稳定区间与机制解释（γ 太低忘得快、ρ=0/1 两极退化等）质量高。

### 5.5 讨论 / 临床意义（Section 5.5, Conclusion）
- 天花板分析与"精度饱和后比特征数"的讨论方向正确，这是高维生物标志物论文应有的视角。
- 但"40–80 genes 可直接 RT-qPCR 验证 / 转化诊断 panel"属于方法学产物到临床产品的跳跃（W5）；结论（Section 6）对未来方向的展望（多标签、流式 FS、深度特征）合理，但未提及最迫切的稳定性验证与外部数据评估，遗憾。
- Conclusion 中"reducing average runtime from 175.0 s to 51.4 s"再次依赖 MEL 复现水平（W2）。

## 6. 给作者的问题

1. **（数据泄漏，必答）** MI 先验向量 m（式 8）到底是在 5 折划分**之前于全数据集**上计算一次，还是在**每个外层折的训练子集内**重算？若为前者，测试折标签已渗入每折的播种与重注入，请说明如何保证无泄漏；若为后者，请明确写出内层 5 折 CV 适应度（式 20）与外层报告协议（Table 5 精度来源）的嵌套关系，并修正 Section 4.7.1"executed only once"的表述。
2. **（MEL 忠实度）** 你们复现 MEL 用的是原作者官方代码/参数吗？Table 5 中 MEL 的 0.8868 精度与 2,722.2 特征，在重叠数据集上是否与 MEL 原文（IEEE TKDE 2024）报告的水平一致？若原文水平更高，请解释差距来源。
3. **（消融归因）** Table 9 把 4.58pp 记在"MI 初始化"名下，但末段从"KDS-EL w/o TPS&KER"（含 MI init，0.9325）切换到"标准 MEL 基线"（0.8868），两者还差 P2 采样与阈值化等骨干差异。能否在同一 KDS-EL 骨干下提供"仅关闭 MI seeding"的变体，以分离 MI 播种的净贡献？
4. **（基线与多类 MI）** 为什么 KMHBO [41]（2026，知识引导高维 FS）只在 Section 2.4 引用却不进入对比？为何不加入 mRMR-top-k+kNN 与 Bolasso/LASSO 基线？另外，式 (4) 对连续微阵列特征的 MI 用什么估计器/分箱实现？COIL20（20 类）与 ISOLET（26 类）上是否做过多类专门处理，θ=0.60 的稀疏种子保证在这两数据集上是否仍成立？
5. **（临床宣称与泛化）** Section 5.5 的"RT-qPCR 直接验证"基于哪些证据？能否报告所选 40–80 基因在 5 折×10 次运行间的特征稳定性指标，以及换成 SVM/RF 分类器后该特征子集的泛化精度？在无外部数据集或湿实验验证前，是否考虑将相关表述改为"可验证范围内的规模、但需稳定性与生物学验证"？

## 7. 维度评分（0–100）

| 维度 | 得分 |
|---|---|
| Originality（创新性） | 67 |
| Methodological Rigor（方法严谨性） | 73 |
| Evidence Sufficiency（证据充分性） | 65 |
| Argument Coherence（论证连贯性） | 70 |
| Writing Quality（写作质量） | 76 |
| Literature Integration（文献整合） | 68 |

**加权平均**（0.25/0.25/0.20/0.15/0.05/0.10）= **69.4**

---

**评审结语**：KDS-EL 的三个机制设计成熟、实验工程与统计规范超出同类论文平均水平，作为"MEL 的改进与系统验证"是扎实的工作。但 W1（MI 先验的 CV 泄漏）是决定结论成立与否的关卡，W2（MEL 忠实度与消融归因）直接关系相对贡献叙事，W3/W5 涉及主张边界。若作者能澄清或修正 CV 协议、用同一骨干分离 MI 净贡献、补齐 filter/embedded 与 KMHBO 基线、并收敛临床表述，本文可达到领域内的发表水平；若 W1 无法澄清，则现有实验结论需要重新评估。

*本报告仅基于稿件正文（16 页）与表图文字，未参考任何其他评审人意见或审稿系统讨论。*

########## TRANSCRIPT LINE 121 ##########

agentId: a76088d3d6e09e40c (use SendMessage with to: 'a76088d3d6e09e40c' to continue this agent)
<usage>total_tokens: 72216
tool_uses: 7
duration_ms: 156866</usage>

########## TRANSCRIPT LINE 124 ##########

我已完整读取论文全文（含 Highlights、正文 16 页、参考文献）。以下为交叉学科视角的独立评审报告。

---

# Peer Reviewer 3 评审报告（交叉学科视角）

**论文**：Multi-Task Particle Swarm Optimization with Knowledge-Guided Elite Refinement and Two-Phase Weight Scheduling for High-Dimensional Feature Selection
**评审人定位**：信息论 × 优化 × 现代机器学习接口处（MI/信息论特征选择、online learning、contextual bandit、credit assignment/RL、深度特征与基础模型嵌入）

---

## 1. 总体评价

KDS-EL 是一个工程完成度较高、实证验证规范的高维特征选择框架：它把"MI filter 先验注入 + wrapper 反馈驱动的特征重要性累积（带指数遗忘）+ 精英邻域翻转变异 + 两阶段权重调度"四块拼进 MEL 的双子群骨架。动机清晰，统计检验、消融链与参数敏感性分析齐全。但从交叉学科视角看，其核心新意被"closed-loop knowledge"的修辞放大了：式(12)-(13) 的 δ 全量 credit 分配是粗粒度 Hebbian 广播式归因，与 Shapley/UCB/Thompson 等更细致的机制相比缺少对照；P2 的 sigmoid 采样在 logit 尺度上不稳定（跨数据集跨越约两个数量级）；MI 估计的离散化与归一化噪声处理均未交代。对现代 ≥10⁶ 维深度特征的可移植性主张缺少现实路径。**大修后可发表**。

## 2. 推荐意见

**Major Revision（大修）**，置信度 **4/5**。核心方法论（credit assignment、sigmoid 采样、MI 先验）有可复现性缺口与理论脆弱性，但实证面足够强，有修订基础。

## 3. 优点

- **S1. 问题诊断精确、机制-缺陷一一对应**（Section 1, ms p.1；Section 2.3 对 MEL 的三点批评，ms p.3）：把随机初始化、memoryless 扰动、静态权重三个缺陷分别映射到 MI seeding、KER、TPS，Table 1 的六维分类定位清晰，这在 EC-FS 文献中属于较高的写作起点。
- **S2. 实证协议规范且自洽**：20 数据集 × 14 方法，Wilcoxon + Holm–Bonferroni（5.4.2，Table 8）、Friedman 平均秩（5.4.3，Fig. 4）对齐 Demšar 协议；5.8 用 subtractive ablation 链（Table 9: 0.9574→0.9488→0.9325→0.8868）而非 incremental addition 叙事，规避了主流的累加式争议，值得肯定。
- **S3. 复杂度分析透明并抓住关键洞见**：式(24) 明确给出 `T_total = O(T·N·N_samp²·d_selected)` 由 wrapper 主导，并指出 kNN 距离计算随 `d_selected` 线性缩减是 3.4× 加速的机理（4.7.2, 5.7）——这个"评估代价 ∝ 活动特征数"的观察是正确且实用的，也是相对 MEL 最有说服力的效率论点。
- **S4. 识别 accuracy ceiling 现象并据此重定义判别标准**（5.5, ms p.11）：在 8 个近饱和数据集上承认 accuracy 失去判别力、转而以特征数作为算法优劣判据，并给出 RT-qPCR panel 的临床论证——这种对"指标失效"的自省在同类论文中不多见。

## 4. 缺点

**W1（核心·中-高严重级）粗粒度 credit assignment 未被验证，且存在 free-riding 偏差。**
- **问题+引用**：式(12)-(13)（ms p.6）把一次改善的全部 δ 均等地记入所有翻转特征（`Wj ← Wj + δ·(2x−1), ∀j∈C(t)_i`）。若一次变异同时翻转 50 个特征、其中仅 1 个真正有益，其余 49 个也获得全额 credit——这正是 RL 中"naive reward distribution"的老问题，相比 Shapley/leave-one-out/边际贡献或 SAGE 式归因是粗粒度广播。同时，只有改善性移动会更新 W（"Non-improving particles (δ≤0) exert zero impact on W"，ms p.6），负面证据从不入账，与 bandit 中"每次被选臂都记录收益"形成不对称。而消融链（Table 9）只对比"全有/全无"，**从未隔离 credit 机制本身**（例如 pbest 频次统计、±1 单位奖励、或 δ 按位置变化量 |Δp| 加权的替代）。
- **为何重要**：这直接决定"KDS-EL 是否只是 wrapper 评价驱动的重要性加权 + 精英邻域搜索的重包装"。若单位奖励或频次统计能达到同等效果，式(13) 的"credit assignment"贡献即被证伪为装饰。
- **修改建议**：新增一组"credit 机制"消融（同一骨架下替换 credit 规则），或至少与 pbest 群体的简单频次/相关性统计基线对照。
- **严重级**：中-高。

**W2（高严重级·复现障碍）P2 采样机制未定义，且 sigmoid logit 尺度在跨数据集/跨阶段不稳定。**
- **问题+引用**：Algorithm 2 line 23 令 `Pj = 1/(1+exp(−Wj))`，line 24 仅写 "blended with personal best pbest,2,i" 而无任何公式（ms p.8）——混合比例、混合对象、是逐特征取 max/加权平均还是概率插值，全部缺失，构成直接复现障碍。更严重的是尺度：δ 来自 5-fold kNN 精度台阶 ≈1/N_samp（n=36 时 ≈0.028，n=2600 时 ≈0.00038），叠加式(14) 的 γ=0.99 稳态放大 1/(1−γ)=100 倍，W 的绝对尺度在数据集间跨越约两个数量级；sigmoid 在 n 小（W≈2.8→P≈0.94）时饱和为确定性采样，在 n 大（W≈0.04→P≈0.51）时退化为近 50% 的伯努利采样。两阶段权重切换（式(19)）又使 δ 的量纲在 t=0.7T 前后突变。
- **为何重要**：P2 是整个框架的一半搜索机制，其行为随样本量剧烈漂移却不为人知；logit 尺度的不稳定性使"知识引导"在多数数据集上名不副实。这正是 online learning/bandit 文献早就处理过的问题：UCB 用 visit count 归一化并加探索项，Thompson 用后验（自带不确定性）。KDS-EL 既无 per-feature 计数，也无不确定性项，探索全靠 prand=0.10 随机分支，是启发式而非原则性方案。
- **修改建议**：定义 blend 公式；对 W 做尺度归一化（如除以 running mean|W|），或改用 `Pj = 1/(1+exp(−(Wj−μ)/s))`；并报告 n 大/小数据集上 P2 的实际采样熵。
- **严重级**：高。

**W3（高严重级·信息论正确性）MI 的连续特征估计未定义，min-max 归一化放大单点噪声。**
- **问题+引用**：式(4)（ms p.4）是对离散 `Val(fj)` 的求和定义，但数据是连续表达值，Algorithm 2 line 1 却称 "Compute continuous mutual information"（ms p.8）——离散化方案（等宽/等频、分箱数）或 KSG 核估计均未给出，实验无法复现。Adenoma 仅 36 样本（Table 3, ms p.9）下，7,457 个特征的 plug-in MI 估计偏差大、方差高；式(8)（ms p.5）的 min-max 归一化使最大 MI 特征恒为 1，等价于把"7,457 个含噪估计取最大值"（winner's curse/多重比较膨胀）直接放大为满权重先验，同时把所有特征压缩进 [0,1] 的相对位置——一个泄露或离群特征即可压低全场。
- **为何重要**：MI 先验是第一阶段的主导贡献（Table 9 中剥离 MI 造成 −4.58pp，为三机制中最大），其估计质量直接决定框架上限；信息论正确性不达标则"信息论混合"的卖点不成立。
- **修改建议**：明确 MI 估计器与离散化细节；用置换/置空 null 阈值过滤显著特征再做归一化；敏感性分析中纳入 bin 数与估计器类型。
- **严重级**：高。

**W4（中严重级）对现代高维/深度特征的可移植性被显著高估。**
- **问题+引用**：结论（ms p.15）宣称可扩展至 "foundation model embeddings / attention-based saliency"，但式(21) 的 MI 预处理 `O(D·N_samp + D log D)` 与式(24) 的每代 5-fold kNN wrapper 评估 `O(T·N·N_samp²·d)` 在 D≥10⁶ 下完全不现实（论文自己也承认 O(D log D) 是瓶颈）。更本质的是语义错配：对深度嵌入，特征已语义化，kNN 距离近/远不构成"选择该维度"的理由，attention saliency 是 soft 先验而非二进制掩码——用一个 wrapper 在 10⁶ 个嵌入维度上做 2000 次 5-fold kNN 评估既昂贵又无必要。
- **为何重要**：这是论文声称的"next-generation biomarker discovery"方向的落地瓶颈；若不给出替代评估路径，"可扩展性"只是口号。
- **修改建议**：给出交叉验证替代路径——例如 (a) 用 attention saliency 直接初始化 W（替代 MI 先验），(b) 深度场景下退化到 filter-only 对照，(c) GPU 并行/随机子采样 MI，并在文本中明确"复杂度随 D 而非随 d_selected 增长的部分"才是真正的扩展性天花板。
- **严重级**：中。

**W5（中严重级·部署与伦理盲区）精度导向 + 极稀疏在医疗场景隐含漏检风险，且签名稳定性缺失。**
- **问题+引用**：式(20)（ms p.7）只优化 `w_a(1−Acc) + w_f·∥x∥0/D`，不涉及 sensitivity/specificity 或类别不平衡；5.5（ms p.11）自己承认 8 个数据集上 accuracy 饱和到"单样本随机波动"级别，却仍以 Acc 为全局主指标。对一个想拿紧凑生物标志物签名的临床用户，论文既未报告所选子集跨 10 次运行的稳定性（如 Jaccard 系数），也未给出所选特征的冗余度/复现性——而 RT-qPCR panel 的翻译（5.5 论证）恰恰要求签名跨数据扰动稳定。5.9.2（ms p.14）的 "plug-and-play" 主张给出了默认参数与稳定区间（Table 10），但未说明"何时应放弃 wrapper 改用纯 filter"或"精度 vs 灵敏度"的取舍。
- **为何重要**：在医疗诊断部署中，"宁缺毋滥式"的极稀疏签名（如 Colon 14 特征、Prostate 26 特征）可能以高整体精度掩盖少数类漏检；accuracy 对不平衡标签无感知。论文只把 class imbalance 列为未来工作（ms p.15），却未承认当前部署主张下的风险。
- **修改建议**：补充 sensitivity/specificity/balanced accuracy 或 AUC 报告；增加跨 run/跨 fold 的子集稳定性（Jaccard）与平均特征相关性；新增一段部署指引（默认参数、何时调参、filter-only 对照何时更合适、对不平衡数据的警告）。
- **严重级**：中。

## 5. 分节详细评论

**Section 4.2（MI seeding + 自适应重注入）**：式(9) 的 ρ=0.50 混合与式(10) 的 θ=0.60 二值化是合理的软注入设计；但 (i) "only features possessing above-average MI"（ms p.6）措辞不准确——θ=0.60 对应 MI 值域前 60% 分位而非均值以上，且 `∥x∥0≈0.15D~0.30D` 的断言依赖 MI 分布形状，未给出推导；(ii) 重注入（式(11)）用的仍是**静态** m（离线 MI 先验），而非在线学习的 W——"adaptive"只体现在触发时机，先验本身从不更新，"闭环"仅由 W 单侧承担；(iii) 重注入的下半群体与 P2 的 W 采样在语义上重复/冲突，未讨论二者协同。

**Section 4.3（W 矩阵）**：除 W1/W2 外，γ=0.99 与 T=100 的匹配值得注意——有效记忆窗口 1/(1−γ)=100 恰等于全程代数，意味着早期贡献到末期仍残留 γ^100≈0.37，"exponential forgetting"的叙事弱于其实际行为（近似准均匀累积器）。与在线学习的对应：这是带静态学习率的**有符号 EMA**（类似 RMSProp/Adam 的梯度 EMA 但无二阶归一），是 discounted bandit（sliding-window/d-UCB）的无计数变体，也是 RL eligibility trace 的退化形式——论文未与任何一支建立连接，错失了把"closed-loop knowledge"落回"reward 驱动的非平稳重要性统计"的理论锚点。

**Section 4.4（KER）**：式(16)-(17) 的状态相关翻转分数 σ_j 方向自洽（激活正 W 特征、停用负 W 特征）；但翻转数量 ⌊ϕD⌋ 随 D **线性增长**——T1D（D=54,675）下 ϕ=0.01 意味着每次翻 546 个特征，这与其在 5.9.1 声称的"localized elite refinement"（ms p.14）自相矛盾；参数敏感性（Table 10）只在 D≤7,457 的 4 个数据集上测过 ϕ，未覆盖 D>20k 的放大效应。建议翻转预算相对活动特征数 d_selected（如 ⌊ϕ·d_selected⌋）而非全维 D。

**Section 4.5（TPS）**：式(19) 是硬切换而非 5.6 声称的"smoothly transition"（ms p.12），仅措辞问题；更实质的是 W 共享于两阶段但 70% 的 credit 在 Phase-1 权重下累积，而最终 gbest 按 Phase-2 适应度选出——存在"W 偏 Phase-1、终解偏 Phase-2"的内在张力，论文未分析（这也加剧 W2 的 logit 尺度漂移）。

**结论/未来方向（ms p.15）**：(a) streaming feature selection 实际与 W+EMA 机制天然契合（γ 本就是流式统计量），是论文**最被低估**的方向，建议作者正面论证而非并列带过；(b) attention saliency 可作为 W 的替代初始化源，但 wrapper 瓶颈（式(24)）是前提障碍，需先给出可扩展的评估替代；(c) class imbalance 下式(20) 的 accuracy 目标恰是错误损失，需 balanced accuracy/AUC——这也再次影响 δ 尺度。

## 6. 给作者的问题

1. Algorithm 2 line 24 中 P2 与 pbest 的 "blended" 具体公式与混合比例是什么？若未定义，如何保证结果可复现？
2. 式(4) 对连续特征如何计算？离散化（分箱数/等宽/等频）还是 KSG 估计？为何 line 1 称 "continuous"？Adenoma 的 36 样本下如何控制 MI 估计偏差与 winner's curse？
3. 既然 δ 的精度台阶≈1/N_samp、γ 稳态放大 100 倍使 W 尺度跨数据集跨越约两个数量级，是否评估过 W 归一化或 per-feature 计数（UCB/Thompson 式）的替代方案？P2 在大样本数据集上是否实质退化为 50% 随机采样？
4. 是否与更简单的 credit 基线（pbest 频次统计、±1 单位奖励、leave-one-out/Shapley 归因）做过隔离消融？"全量 δ 记入所有翻转特征"的 free-riding 偏差影响多大？
5. KER 翻转数 ⌊ϕD⌋ 在 D=54,675 时为 546，与 "localized refinement" 定位冲突——是否应按活动特征数 d_selected 缩放翻转预算？
6. 医疗场景下能否报告 sensitivity/specificity/balanced accuracy 与所选子集的跨运行 Jaccard 稳定性？极稀疏签名在不平衡数据上是否有漏检（false negative）风险？

## 7. 维度评分（0-100）

| 维度 | 得分 |
|---|---|
| Originality | 65 |
| Methodological Rigor | 60 |
| Evidence Sufficiency | 70 |
| Argument Coherence | 70 |
| Writing Quality | 75 |
| Significance & Impact | 65 |

- 简单平均：**67.5 / 100**
- 加权平均（Originality 0.15 / Methodological Rigor 0.25 / Evidence 0.15 / Coherence 0.15 / Writing 0.10 / Significance 0.20）：**66.3 / 100**

加权与简单平均均落在 65-68 区间，与"Major Revision、实证扎实但方法论与可复现性需大修"的定位一致。

---

**核心结论（供汇总）**：KDS-EL 的实证价值（尤以"稀疏化→评估代价线性下降"的 3.4× 加速与规范统计检验）成立；但"closed-loop knowledge guidance"的方法论新意被高估——其本质是 *MI filter 先验 + wrapper 反馈驱动的有符号 EMA 重要性加权 + 精英邻域翻转变异*，主要增益（−4.58pp）来自既有的 MI filter 先验而非新机制。复现性瓶颈集中于 P2 blend 未定义、MI 离散化未说明、sigmoid logit 尺度跨数据集不稳定三处；对深度嵌入/10⁶ 维的扩展主张缺少现实路径。推荐大修，置信度 4/5。

（文件：`E:\多目标优化\KDS-EL\paper\extracted_text.txt`，原 PDF `E:\多目标优化\KDS-EL\paper\main.pdf`；评审为只读操作，未修改任何论文文件。）

########## TRANSCRIPT LINE 124 ##########

agentId: a40080f82019e7d2a (use SendMessage with to: 'a40080f82019e7d2a' to continue this agent)
<usage>total_tokens: 72298
tool_uses: 7
duration_ms: 174533</usage>

########## TRANSCRIPT LINE 127 ##########

我已通读全文（17 页，含 Highlights、正文 16 页、参考文献）。以下是评审报告。

---

# 评审报告：KDS-EL（Devil's Advocate / Peer Reviewer 4，只挑战不评分）

## 0. 先肯定论文做对的地方

论文在实验纪律上有可称道之处：采用 Demšar [45] 统计协议并施加 Holm–Bonferroni 校正（§5.4.2，Table 8），这在多数 FS 论文中已属高标准；Table 9 的减法消融链呈现单调退化（0.9574→0.8868，87.8→2722），叙事自洽；Fig 6 的 Pareto 图与逐数据集特征数（Table 6）的披露也较完整。这些使论文"看起来"严谨，正因如此其内部矛盾更值得被钉死。

---

## 1. 最强反论（Strongest Counter-Argument）

KDS-EL 的核心主张——三种机制（MI 播种、KER、TPS）协同带来"全部 13 个对手之上"的最优——经不起审读。第一，MI 先验存在泄漏嫌疑：MI 在进化开始前一次性基于全数据（含全部 5 折标签）计算（§4.1 Stage 1；Algorithm 2 第 1 行；§4.7.1 "only once prior to the evolutionary loop"），而 §5.1.1 的防泄漏声明只覆盖 wrapper 的 CV 划分、未声明 MI 按训练折内计算。若属实，KDS-EL 归功于"MI 初始化"的 4.58pp 与对 MEL 的 7.06pp 优势，部分来自 test 折标签被 filter 先验偷看，而非算法创新。第二，MEL 稻草人未排除：作者未说明用原作者代码还是自行复现，未与 MEL 原文（IEEE TKDE 2024）在相同基因数据集上的报告结果对照，MEL 被统一压到 N=20/T=100、以保留 2722 特征的次优工况呈现（Table 4）。第三，"identical evaluation budgets"（§5.1.2）为假：KER 每代 3 次精英评估（§4.4.1）加停滞重注入，使 KDS-EL 比对手多 15% 以上的适应度评估，消融边际与对比增益与评估预算混淆。最后，即便数据全对，更省约的解释存在：MI top-k 预筛 + k-NN 即可复现大半结果，"进化机制"（KER+TPS 合计仅 2.49pp）才是真正的增量，而这 2.49pp 又因 TPS/KER 未分离消融、且跨阶段权重下 pbest 簿记不自洽而被进一步高估。

---

## 2. 问题清单（Issue List）

### CRITICAL（致命缺陷）

**C1. MI 先验在全数据上计算 → 潜在标签泄漏（维度 4 逻辑链 / 维度 3 确认偏误）**
MI 在"offline"阶段"computed once prior to evolution"（P5，§4.1 Stage 1；Algorithm 2 第 1 行，P8）；§4.7.1 明言"executed only once prior to the evolutionary loop"（P8，式 21）。整篇未出现"在每折训练集内重算 MI"的表述，§5.1.1（P9）的防泄漏声明仅针对 CV 划分与 wrapper 评估。若 MI 用了 test 折标签，则 KDS-EL 独有的 MI 播种（式 9）与自适应重注入（式 11）均受污染，对不依赖 MI 的 13 个对手不公平——这直接击中"统计显著优于全部 13 个对手"（Abstract）的根基。**要求作者明示 MI 的折内计算方式**。

**C2. MEL 稻草人 / 复现失真（维度 1 核心论点 / 维度 2 Cherry-Picking）**
MEL 作为底线被打到 0.8868、2722 特征、175s（Table 5/6，§5.7）。论文既未声明用原作者代码还是自行复现，也未与 MEL 原文在同一批基因数据集（Colon、Leukaemia/ALL_AML、SRBCT、DLBCL、Prostate、COIL20、ISOLET 等均为 MEL 原文常用基准）上的报告值交叉核对。Table 4 给 MEL 的参数仅 ω=0.90、c1,2,3=2.0、ws=[0.90,0.10]，未交代 MEL 自带的 P2 概率采样细节是否按原文实现；且 §5.1.3 将 N=20/T=100 强加给所有方法。若 MEL 原文声称在这些数据上高效优异，则 7.06pp 差距的部分来源是复现弱化，而非 KDS-EL 更强。这是对全文核心结论最直接的釜底抽薪点。

**C3. "identical evaluation budgets"为假，评估次数不对等（维度 3 / 4）**
§5.1.2 声称"14 fixed-length methods are compared under identical evaluation budgets"（P9）。但 KDS-EL 除 N=20×T=100=2000 次基准评估外，每代另付 ke=3 次 KER 精英评估（§4.4.1，"exact bounded overhead of ke = 3 evaluations per generation"，P7），并可能在停滞时每次重注入 10 个粒子（§4.2.1，式 11）。总计至少 2300+ 次，超出对手 ≥15%。因此 Table 9 中"KER 1.63pp""MI+重注入 4.58pp"的归因与评估次数差混叠——多给评估次数也能涨精度，"机制贡献"被系统性高估。

### MAJOR（严重削弱可信度但可大修）

**M1. Table 5 注释与 Table 7 计数直接矛盾（维度 8 内外部一致性）**
Table 5（P11）在 ALL1、BASEHOCK、COIL20、ISOLET、SRBCT 上对 W-MPSO/fMPSO/NSGA-II/MOEA/D/MOPSO 标"−"（KDS-EL 显著更差）。逐一数出：W-MPSO 3 胜、fMPSO 3 胜、NSGA-II 4 胜、MOEA/D 2 胜、MOPSO 2 胜。但 Table 7（P12）这些方法的行对 KDS-EL 列全部记"0/20"。若"−"真由双侧 Wilcoxon（p<0.05，10 次配对）得出，则 Table 7 应为 3/20、3/20、4/20、2/20、2/20。"无任何对手在任何数据集上显著胜出"的暗示被自己的数据推翻。

**M2. 消融混淆：机制从未被干净分离（维度 4）**
(a) Table 5/6/7 列头写"w/o KER"，但 Table 2、§5.2、§5.8.1 称"w/o TPS&KER"——一次剥离了两个机制，名称却不一致；(b) KER 的 1.63pp 是在 TPS 已缺席的变体上测得（0.9488→0.9325），"KER 在 TPS 在场时的贡献"从未测量；(c) "MI 初始化"与"自适应重注入"永远一起剥离（w/o TPS&KER vs MEL，P14 Table 9），二者各自贡献未知。§5.8.1 却总结"three mechanisms operate orthogonally and synergistically"——没有 2^k 全组合交互分析，"正交/协同"毫无证据。

**M3. Friedman 秩：文字与图不一致，且缺统计量与 p 值（维度 8）**
§5.4.3 文字（P12）：fMOPSO 5.75、FWPSO 6.10、NSGA-II 6.25、MOEA-D 6.80、PSO-CSM 7.15、BPSO 13.80；Fig 4（P12）为：fMOPSO 5.90、FWPSO 6.20、NSGA-II 6.93、MOEA-D 7.78、MOPSO 7.73、PSO-CSM 8.60、BPSO 13.35——几乎每个值都不一致，MOEA-D 与 MOPSO 的相对次序都反了，且文字漏掉 MOPSO。同时 §5.1.4 承诺的 Friedman 检验只给了秩，χ²_F 统计量与 p 值缺失，按 Demšar 协议还缺 Nemenyi CD 图。§5.4.3 结论"KDS-EL 稳居第一梯队"建立在无法复现的秩上。

**M4. "best classification performance among all competitors"过度宣称（维度 5 / 8）**
Abstract（P2）与 Highlights（P1）宣称全局最优，但 Table 5 显示 KDS-EL 在 5/20 数据集被显著击败（ALL1、BASEHOCK、COIL20、ISOLET、SRBCT），其中 BASEHOCK（-1.25pp vs NSGA-II）与 ISOLET（-1.96pp vs NSGA-II）并非天花板数据集，无法用 §5.5 的"ceiling effect"开脱。诚实的表述只能是"20 数据集平均精度最高（0.9574）"，而非"对全部竞争者最优"。

**M5. §5.3 "clear Pareto dominance / equal or higher accuracy + 20–50x"与数据、与 Fig 6 矛盾（维度 5）**
§5.3（P11）称"delivers equal or higher classification accuracy while achieving a 20- to 50-fold reduction"。但 FWPSO 平均仅 12.2×（1068.9/87.8），NSGA-II 等超 50×（54.9×），且"equal or higher accuracy"在 BASEHOCK/COIL20/ISOLET 上为假（NSGA-II 0.9238/0.9971/0.9090 vs KDS-EL 0.9113/0.9939/0.8894）。COIL20 上 NSGA-II(0.9971, 283 特征) 与 KDS-EL(0.9939, 84) 互不支配，恰在 Fig 6 前缘两端——正文的"dominance"与自己的 Fig 6 相悖。

**M6. 跨阶段适应度不可比，可能系统性利好 KDS-EL（维度 4）**
TPS 在 t=0.7T 切换权重（式 19，P7）。Algorithm 2（P8）中 pbest 更新（fi < f_pbest）比较的是不同权重体制下记录的适应度：Phase 2 里粒子与 t<70 的 pbest 比较，等效于直接切换到精度主导目标。W 矩阵按 δ=f_pbest−f_i 奖励（式 13）同样混用跨体制差值。这一"簿记不自洽"可能反过来帮了 KDS-EL——§5.6 的 Phase-2 "micro-rise"可能只是权重切换后 swarm 在无惩罚下重优化精度，被包装成 TPS 的"temporal decoupling"收益；且对 w/o TPS 的对照用的是固定 [0.90,0.10]，而非 [0.95,0.05] 或 [0.70,0.30]，没排除"只是精度权重更高"这一平凡解释。

**M7. 单标量点 vs Pareto front 的比较在方法学上倾斜（维度 3）**
KDS-EL 是标量化单目标方法，对手却是一批 MO 方法。论文用每个 MO 方法 front 中"精度最高"的一员与 KDS-EL 单点比精度，再宣称"多目标方法保留 2960–5263 特征"——这既忽略了 front 的多样性（决策者可能要的不是单点），又默认"少特征即胜"。MO 方法还在 N=20（远低于 NSGA-II/NSGA 常规 100+ 种群）下被评估，交叉/多样性严重受限，属于系统性有利于 KDS-EL 的设置。

**M8. 过度概括：声称"跨多样模态与维度普遍最优"却在自己最该强的多样模态上失败（维度 5）**
20 个数据集中 17 个是二元小样本基因表达，仅 3 个多类/多样态（SRBCT、COIL20、ISOLET）+2 文本 +1 图像 +1 语音 +1 合成。而 KDS-EL 恰恰在 COIL20（图像）、ISOLET（语音）、BASEHOCK（文本）上显著被击败——正是样本量最大、最"多样"的模态。§6 结论（P16）"top overall performance across diverse modalities"与 §5.4.3"diverse data modalities"的概括超出了数据支持范围：优势集中于小样本二元基因域的窄区间。

### MINOR

- **m1. 命名不一致**：Table 5/6/7 列头"w/o KER"（P11/P12）vs Table 2 与正文"KDS-EL w/o TPS&KER"（P10）。
- **m2. Table 7 自身有一处对不上**：KDS-EL 行对 fMOPSO 记 15/20，但从 Table 5 数 fMPSO 列只有 14 个"+"（另有 3 个"≈"、3 个"−"）。
- **m3. 统计报告不完整**：Table 8 全部 13 行 Combined p 与 Holm p 都写"<10⁻¹⁵"（P12），Holm 排序需要精确 p 值；Friedman 的 χ² 与 p 缺失（同 M3）。
- **m4. 数值舍入漂移**：§5.8.1 说 KER 剥离后特征从 121.7 增至 290.5，Table 6 记 290.6；§5.3 记 290.5。
- **m5. TPS 并非普遍有利**：ISOLET 上 w/o TPS(0.8898) 反而略高于 KDS-EL(0.8894)（Table 5，P11）；且在 Adenoma/Lymphoma/Prostate/SRBCT/Leukaemia/DLBCL/COIL20 等约 8 个数据集上 w/o TPS 更稀疏（Table 6）——TPS 的"同步提升精度+稀疏+速度"只是聚合结果，个体数据上多为精度/稀疏度在时间维度上的转移。
- **m6. 报告精度即选择期 5 折 CV 精度，无独立测试集**：各方法一致故相对比较尚公允，但 0.9574 等绝对值含选择偏差；在天花板数据集上 0.9998 vs 1.0000 的"−"显著性本质是 1 个样本内的方差伪影（n=128 时 5 折单样本≈0.008），与 §5.2 自己"negligible disparity"的辩解自相矛盾。

---

## 3. 被忽略的替代解释/路径（Alternative Explanations）

1. **纯 filter 复现测试从未运行**：KDS-EL 的 4.58pp 归功于 MI 先验。一个"MI top-100 或 top-50 + k-NN"、"mRMR top-k + k-NN"基线从未出现在 Table 5。若此类简化基线达到 ~0.95 精度 + 约 100 特征，则 KDS-EL 相对 MEL 的优势大半来自 filter 排名 + 激进稀疏化，而非任何进化机制——进化机器（KER+TPS）真正贡献仅 2.49pp。
2. **两阶段"先稀疏化、后精度重优化"是成熟廉价套路**：TPS 的 0.86pp 可能就是"递归消除/LASSO 稀疏化后再用精度权重重优化"的平凡翻版；对照应加入静态 w=[0.95,0.05]、静态 w=[0.70,0.30] 两个单权重基线以排除"只是权重取值不同"。
3. **MEL+（在 MEL 上做 γ/记忆衰减/权重调优）**：作者从未尝试把 MEL 自己的超参（权重、种群、迭代、重要性矩阵更新）调到公平操作点再比，7.06pp 可能大幅缩水。

---

## 4. 缺失的利益相关者视角（Stakeholder Blind Spots）

- **MEL 原作者**：作为被当作稻草人的方法作者，其关于复现保真度、参数与评估协议的声音完全缺失（无代码来源声明、无原文数值对照）。
- **纯 filter/mRMR 阵营**：会指出 MI 先验已承载主要信息，进化部分被过度包装。
- **多目标决策者**：需要的是 Pareto front 与超体积/IGD 等 front 级指标，而非被强行压成单点的"精度最高成员"。
- **临床/生物学专家**：87.8 个特征从未做通路富集、与已知 biomarker 的重叠验证或 RT-qPCR 可行性分析，"临床可验证性"停留在动机话术。
- **下游从业者**：无独立测试集，0.9574 的绝对值对实际部署不可信。

---

## 5. 未检视的前提假设（Unexamined Premise）

以 **k-NN(k=3) 5 折 CV 精度的简单平均** 作为唯一的跨数据集标量目标：20 个数据集里 8 个精度≈0.999 的饱和数据、3 个≈0.87 的困难数据被等权平均，使得"平均精度排名（Friedman 秩、Wilcoxon）"实质由"能在多少个天花板数据集上触顶"决定，而非一般性的特征选择质量。§5.5 自己承认天花板数据集上精度失去判别力，却仍用同一套精度指标生产全文的头条数字与全部显著性结论。

---

## 6. 观察（非缺陷）

1. **Fig 6 比正文诚实**：Pareto 图明确把 KDS-EL 画成前缘上的一个角点（而非支配者），与 §5.3 的"clear Pareto dominance"文字相矛盾——图的证据反而支持 NSGA-II 等在 COIL20/ISOLET 上与 KDS-EL 存在真实取舍。
2. **Table 9 的减法链（0.9574 / 87.8 → 0.8868 / 2722.2）本身干净且单调**，作为"w/o"减法叙事（MEL 是被剥到只剩骨架的残骸）在结构上是诚实的手法；问题出在每一格"机制归因"被预算混淆与 TPS/KER 耦合污染，而非链的方向。
3. **代码可用性声明**（P16 Data Availability）仅承诺"upon publication"，对双盲评审与复现性无帮助；考虑到 C1/C2 的严重性，公开代码与数据拆分是修复的最低门槛。

########## TRANSCRIPT LINE 127 ##########

agentId: a0515a8c846db856a (use SendMessage with to: 'a0515a8c846db856a' to continue this agent)
<usage>total_tokens: 86170
tool_uses: 10
duration_ms: 262799</usage>