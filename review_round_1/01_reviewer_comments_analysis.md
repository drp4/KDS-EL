# KDS-EL 首次同行评审意见深度解析与审稿人诉求剖析报告

**文档归属**：`review_round_1/01_reviewer_comments_analysis.md`  
**评审周期**：First Round Review (Reviewer 1: 2026-10-24; Reviewer 4: 2026-11-02)  
**总体结论**：两位审稿人均具有极高的演化计算、特征选择与生物医学数据分析专业水平。评审意见直指论文最薄弱的实验协议设计、数据泄露隐患、消融设计混杂、统计检验规范及过度学术宣称。审稿人认为论文工作具有合理性，但目前处于“渐进式改进（incremental）、实验设计支撑不足、结论过度乐观”的状态，必须进行深度的实验重构与理论澄清。

---

## 一、评审专家总体倾向与核心态度概述

### 1. Reviewer 1 总体画像
* **身份特征**：对生物医学高维特征选择实验协议、演化算法动力学、统计学假设检验极其内行的资深专家。
* **态度评语**：*"The paper is clearly organised and candid about its protocol, but the contribution is incremental and the evidence supports the headline claims less than the text suggests... The manuscript is not ready for publication."*
* **审稿逻辑**：
  1. 肯定作者对实验协议的坦诚（candid），但严厉指出当前的实验协议存在严重的**数据泄露与乐观偏差**（Full-data MI + 内部 5-fold CV）。
  2. 抓住公式和代码细节展开推导，指出文章自述机制与实际数学逻辑的矛盾（如高维下规模惩罚压强不足、P2 越界惩罚对权重向量 $W$ 的冲击、KER 翻转步长在超高维下的巨大失效风险）。
  3. 统计检验与数据集存在硬伤（如 ALL_AML 与 Leukaemia 疑似同一数据重复计算、表格标记矛盾、p 值自由度与近似误用）。

### 2. Reviewer 4 总体画像
* **身份特征**：严格遵循机器学习可复现性（Open Science）、严谨因果归因与基准公平对比的评审专家。
* **态度评语**：*"The paper is relevant and well organized, but the experimental design does not support its central claims."*
* **审稿逻辑**：
  1. 认为 KDS-EL 是在基础算法（MEL）之上的现有组件堆叠组合，必须证明每一个改进机制具有不可替代的独立贡献。
  2. 核心痛斥信息泄露与不公平对比：KDS-EL 获得了全标签先验引导、更严厉的惩罚函数以及不平等的评估预算（Budget 2300 vs 2000）。
  3. 强调科研规范性：反对口头宣称（如 Winner's curse、破坏性变异概率），要求提供标签置换检验、开源代码、完整随机种子与真实数据分布。

---

## 二、Reviewer 1 逐条审稿意见深度解析（12 条）

### 意见 1：信息泄露、乐观偏差与分类器泛化评估缺陷
* **【审稿人原文】**
  
  > "The authors acknowledge that reported accuracy is the same 5-fold CV score the search optimizes and that the MI prior uses all samples' labels, but with n = 36–173 and D up to 54,675 this makes the figures strongly optimistic. Colon is 94.52% in Table 4, yet section 4.2.8 gives 88.59% for its 14-feature signature with 3-NN (protocol not stated in the main text), and SVM and Random Forest do worse with it than with all features. Nested CV with MI computed inside the training folds, plus label-permutation nulls, is needed."
* **【具体含义剖析】**
  1. **双重数据泄露（Double Information Leakage）**：
     * **先验知识计算泄露**：互信息（MI）是在包含全部 $N_{\mathrm{samp}}$ 个样本的完整数据集上预先计算的，测试折的标签信息提前渗透到了特征排序与初始化中。
     * **目标函数评价泄露**：演化搜索过程直接在 5 折交叉验证上优化分类精度，最终汇报的也是这个被优化的内部交叉验证得分，没有独立的留出测试集（Hold-out Test Set）。
  2. **小样本高维（Small-$n$, Large-$D$）加剧虚高**：在样本量仅几十到一百多、特征数高达数万的生物医学数据上，这种泄露会导致灾难性的“假阳性”和乐观偏差（Optimistic Bias）。
  3. **分类器泛化反噬（Colon 数据集的实证破绽）**：论文在 Colon 数据集上汇报的 3-NN 交叉验证精度为 94.52%，但在特征子集泛化评估（Section 4.2.8）中，用该子集测试 3-NN 仅有 88.59%，而在 SVM 和随机森林上甚至不如使用全部特征！这直接证明所选特征严重过拟合于 3-NN 目标函数，并没有学到真实的生物判别信号。
* **【审稿人观点与意图】**
  * 审稿人认为作者虽然在文中坦承了该协议，但这掩盖不了结果“被严重人为高估”的本质。审稿人怀疑目前的顶尖精度纯粹是数据泄露和优化器死记硬背训练样本的结果。
* **【审稿人期望的交付成果】**
  * 必须采用**嵌套交叉验证（Nested Cross-Validation, 5×5 Nested CV）**：外层划分测试集，内层进行特征选择与优化；互信息 MI 必须**严格限制在外层训练折内部计算**，严禁使用外层测试集标签。
  * 补充**标签置换零假设检验（Label-Permutation Null Test）**：打乱样本标签后重新运行算法，证明算法在随机数据下精度崩塌，从而证实原始结果的真实统计显著性。
  * 规范且完整说明下游独立分类器（SVM、RF）评估协议。

---

### 意见 2：类别不平衡描述前后矛盾与评价指标单一 [✅ 已完成]
* **【审稿人原文】**
  
  > "Section 4.1.1 acknowledges intrinsic class imbalance, whereas section 4.1.3 asserts that classes are balanced; Colon (40/22) and DLBCL (58/19) clearly are not. Balanced accuracy or AUC should be reported, and class counts added to Table 2."
* **【具体含义剖析】**
  1. **正文自相矛盾**：在 Section 4.1.1 中承认生物医学数据集存在内在的类别不平衡，但在 Section 4.1.3 中却声称样本类别是平衡的。审稿人指出了明显的硬伤：Colon 样本比例为 40:22，DLBCL 比例为 58:19，失衡比例接近 2:1 和 3:1，绝对不是平衡数据。
  2. **单一 Accuracy 指标在失衡数据上的失效**：在类别不平衡时，普通分类准确率（Accuracy）会被多数类支配，无法反映对少数类（如稀有疾病表型）的识别能力。
* **【审稿人观点与意图】**
  * 论文在基础数据集描述上存在逻辑粗糙和不一致，且缺乏对高维不平衡特征选择的严谨态度，试图用简单的总体准确率掩盖少数类的分类退化。
* **【审稿人期望的交付成果】**
  * 彻底修改正文前后冲突，并在 Table 2（数据集特征表）中明确增加每一类样本的具体数量（Class Distribution / Sample Counts）。
  * 增加并汇报抗失衡的评估指标：**平衡准确率（Balanced Accuracy, BAcc）** 或 **受试者工作特征曲线下面积（ROC-AUC）**。

---

### 意见 3：缺失经典 Filter 基准、未包含同类知识引导方法且评估预算不公平
* **【审稿人原文】**
  
  > "No simple filter baselines (top-k MI, mRMR, ReliefF, L1-based selection) are included, even though the seeded half of the swarm is effectively a noisy thresholded MI ranking, and the closest knowledge-guided methods the authors cite ([17], [18], [36]) are omitted. BinCOA, DENCA-SO and BPSO finish at roughly 50% of D (about 27,000 of 54,675 features on T1D), i.e. essentially at random initialization, so beating them says little. KDS-EL's defaults were also justified on four of the same 20 datasets, and evaluation budgets are unmatched (about 2,300 vs 2,000 evaluations for most competitors)."
* **【具体含义剖析】**
  1. **缺少最直接的竞争对手（Filter Baselines）**：KDS-EL 的初始种群有一半直接根据互信息（MI）排序进行概率播种。审稿人敏锐指出：如果直接取 Top-$k$ MI、mRMR、ReliefF 或 LASSO (L1) 选出的特征给 3-NN 分类，精度是否就已经接近 95%？如果不对比纯 Filter，无法证明耗费大量计算资源运行演化搜索的必要性。
  2. **遗漏参考文献中同类知识引导方法**：正文引用了知识引导特征选择文献（[17], [18], [36]），但在对比实验中全部缺席，反而选了一批在超高维下表现极差的“稻草人”算法。
  3. **对比算法选型偏弱（Strawman Competitors）**：BinCOA、DENCA-SO、BPSO 在超高维（如 T1D 54,675 维）上最终选出约 50% 维度的特征（约 27,000 个），这说明这些对比算法在超高维空间中完全没有收敛能力，几乎等于随机初始化的状态。击败这些算法毫无说服力。
  4. **参数微调存在数据泄露**：KDS-EL 的默认超参数是在 20 个测试数据集中的 4 个上调优出来的，存在用测试集调参的嫌疑。
  5. **评估预算不平等（Unmatched Fitness Evaluations）**：KDS-EL 运行了约 2,300 次适应度评估（由于引入了 KER 等额外评估开销），而多数对比算法仅设置了 2,000 次，在优化预算上占了便宜。
* **【审稿人观点与意图】**
  * 审稿人认为论文的优越性可能来自于“不公平的评估预算 + 挑软柿子捏（对比无收敛能力的算法）+ MI 先验本身的功劳”，而非演化协同机制的精妙。
* **【审稿人期望的交付成果】**
  * 补充经典 Filter 方法（Top-$k$ MI, mRMR, ReliefF, LASSO）的分类性能基准线。
  * 严格**对齐函数评估次数预算（Budget = 2,000 FEs）**，消除评估次数差异带来的不公平优势。
  * 合理解释超参数设定依据（如采用留出集调优或跨领域通用默认值）。

---

### 意见 4：消融实验打包耦合与两阶段调度（TPS）参数缺乏隔离
* **【审稿人原文】**
  
  > "Each ablation stage bundles several components (e.g., credit memory, decay and KER together), and 'w/o TPS' uses static 0.90/0.10, which matches neither TPS phase. The TPS (+0.83 pp) and KER (+1.14 pp) gains are comparable to the ±0.7–1.3 pp swings in Table 9, so factorial ablations are needed (static 0.95/0.05 and 0.70/0.30, a reversed schedule, γ = 1, each component alone)."
* **【具体含义剖析】**
  1. **多组件打包消融（Bundled Ablation）**：论文从 MEL 到 MEL_MI 再到 NoPool 再到 KDS-EL，每一步都同时引入了多个机制（例如同时加入特征信用记忆 $W$、遗忘衰减 $\gamma$ 和 KER 局部精炼），无法证明这三者中到底是谁在起作用，甚至无法排除某个组件实际上带来了负面影响。
  2. **TPS 消融基准设置失当**：“w/o TPS”变体使用的是固定的静态权重 $(w_a, w_f) = (0.90, 0.10)$，然而 TPS 自身运行的两阶段权重分别是 $(0.70, 0.30)$ 和 $(0.95, 0.05)$。静态 0.90/0.10 与 TPS 的任何一个阶段都不匹配，这属于“为了证明动态调度好，故意挑了一个效果差的静态基准”。
  3. **增益幅度与参数扰动相当**：TPS 带来的精度增益仅为 +0.83 个百分点，KER 增益为 +1.14 个百分点，这个数值与 Table 9 中超参数随机波动产生的幅度（$\pm 0.7 \sim 1.3\text{ pp}$）处于同一量级，统计上极不稳固。
* **【审稿人观点与意图】**
  * 审稿人质疑各个组件的有效性缺乏因果说服力，怀疑 TPS 的提升只是随机扰动，要求用严格的析因实验（Factorial Ablation）将各组件彻底解耦。
* **【审稿人期望的交付成果】**
  * 提供完整的**析因消融实验（Factorial Ablation Study）**：
    * 隔离测试各个静态权重组合：如静态 $(0.95, 0.05)$、静态 $(0.70, 0.30)$；
    * 补充**反向阶段调度（Reversed TPS Schedule）**测试：先精细调优（0.95/0.05）再激进压缩（0.70/0.30），证明由粗到精的正向调度因果逻辑；
    * 单独剥离衰减因子消融：测试无衰减（$\gamma = 1.0$）下的性能变化；
    * 分别独立测试信用记忆更新与 KER。

---

### 意见 5：高维下适应度尺度失衡导致 TPS 剪枝压强失效的数学质疑
* **【审稿人原文】**
  
  > "Because the size term is divided by D, even under Phase 1 weights one extra misclassified sample outweighs the cost of a few hundred extra features at D ≈ 12.6k and over a thousand at D ≈ 55k. The claimed 'aggressive pruning' therefore exerts little per-feature pressure on sparse candidates, so the mechanism behind TPS's compaction is unclear. Per-generation subset-size traces for static-weight variants, and results with a differently normalised size term, would help."
* **【具体含义剖析】**
  1. **尺度权重的数学穿透**：适应度函数为 $f = w_a \cdot \mathrm{Error} + w_f \cdot \frac{d}{D}$。
     * 当样本量 $N_{\mathrm{samp}} \approx 60$ 时，多错分一个样本，错误率变化为 $\Delta \mathrm{Error} \approx \frac{1}{60} \approx 0.0167$。在阶段 1（$w_a = 0.70$）下，适应度恶化 $0.70 \times 0.0167 \approx 0.0117$。
     * 而增加一个特征带来的适应度恶化仅为 $w_f \cdot \frac{1}{D} = 0.30 \cdot \frac{1}{D}$。
     * 在 $D = 12{,}600$ 时，增加一个特征的惩罚为 $2.38 \times 10^{-5}$；多错分一个样本的代价相当于增加 **490 个特征**！
     * 在 $D = 54{,}675$ 时，多错分一个样本的代价相当于增加 **2,130 个特征**！
  2. **“激进剪枝”在数学上的矛盾**：在稀疏特征子集（几十到上百个特征）的状态下，每多选或少选一个特征，适应度变化极其微弱（小于 $10^{-5}$）。因此，审稿人指出：所谓的“激进特征剪枝”在单特征层面上对粒子的压力微乎其微，算法为什么能把特征数压缩到 87.8 个，背后的驱动力绝非公式本身宣称的那么简单。
* **【审稿人观点与意图】**
  * 审稿人通过极其深厚的数学直觉，直接撕开了经验公式与物理机制之间的裂痕。审稿人认为论文对 TPS 压缩机制的解释流于表面，要求通过动态轨迹图和不同归一化方式来证明真相。
* **【审稿人期望的交付成果】**
  * 绘制每一代子集特征规模的演化收敛轨迹图（Per-generation subset-size traces），对比 TPS 与不同静态权重变体的实际收敛曲线。
  * 探讨或对比采用非线性或不同归一化尺度（如以最大允许特征数或对数尺度归一化）的适应度函数表现，诚实解释超高维下特征数量项的实际驱动行为。

---

### 意见 6：子种群 $\mathcal{P}_2$ 稀疏初始化引发越界惩罚对信用记忆 $W$ 的剧烈污染
* **【审稿人原文】**
  
  > "Section 3.1 states that P2's sum-normalised sampling has expected cardinality 1, so at most about 8% of its masks reach d_min = 3 and the rest receive the barrier fitness (≥ 1.1). The text says credit feedback is preserved for these masks, which, if applied through Eqs. (18)–(19), assigns Δ ≈ 1 to every changed coordinate, two to three orders of magnitude above genuine fitness differentials, and could swamp W. A P1-only ablation and plots of W and the P2 feasibility rate would show whether the memory learns real signal."
* **【具体含义剖析】**
  1. **$\mathcal{P}_2$ 初始化的极端稀疏性**：正文叙述 $\mathcal{P}_2$ 采用和归一化概率抽样，其期望采样特征数仅为 1。这意味着根据二项/泊松分布，绝大多数掩码选出的特征数都小于最低特征约束 $d_{\mathrm{min}} = 3$（能够达到 3 个特征的概率不超过 8%）。
  2. **越界惩罚引发巨大的虚假适应度梯度**：未达到 $d_{\mathrm{min}}$ 的无效粒子被直接赋予屏障惩罚适应度（Barrier Fitness $\ge 1.1$）。
  3. **信用记忆 $W$ 被严重污染**：正文提到这些越界粒子依然参与信用记忆更新。当一个粒子从正常适应度（$\approx 0.05 \sim 0.15$）跳变到惩罚值 $1.1$ 时，适应度差值 $\Delta = f(\mathbf{x}) - f(\mathbf{p}_{\mathrm{best}}) \approx 1.0$。而正常两代之间由于分类精度变动引起的真实适应度差值通常仅为 $10^{-2} \sim 10^{-3}$！这一高达 2 到 3 个数量级的虚假惩罚会瞬间淹没（swamp）权重向量 $W$，导致其记录的特征重要性被完全带偏。
* **【审稿人观点与意图】**
  * 审稿人极其敏锐地发现了公式更新规则与可行性边界处理之间的潜在逻辑漏洞。审稿人怀疑所谓的特征信用记忆 $W$ 学到的根本不是真实的特征判别信号，而是被无效解的惩罚噪声彻底污染的混沌数值。
* **【审稿人期望的交付成果】**
  * 开展**单种群 $\mathcal{P}_1$ 的独立消融实验**（评估移除 $\mathcal{P}_2$ 后的算法表现）。
  * 汇报并绘制 $\mathcal{P}_2$ 在演化初期的**可行解比例（Feasibility Rate）**以及权重向量 $\mathbf{W}$ 随代数的演化动力学图，确切证明权重向量学到的是真实有效特征还是随机噪声。

---

### 意见 7：KER 翻转规模在超高维下过大导致变异极易被拒绝且缺乏多样性实测
* **【审稿人原文】**
  
  > "With k_flip = ⌊0.01D⌋, KER flips 126–546 coordinates at once on the 12k–55k-feature datasets, against elite subsets of tens to hundreds of features, so most mutants are probably rejected by the greedy rule. Please report KER acceptance rates and its share of g_best updates. The claims that seeding preserves diversity and defends against the Winner's curse are likewise asserted rather than measured (no diversity metric, no noisy-prior experiment)."
* **【具体含义剖析】**
  1. **翻转步长在超高维下的荒谬性**：KER 设定的翻转维度比例为 $k_{\mathrm{flip}} = \lfloor 0.01 D \rfloor$。在 $D = 12{,}600 \sim 54{,}675$ 的数据集上，一次变异就要同时强行翻转 **126 到 546 个特征**！而当前精英解本身一共才选了十几个到几十个特征（平均 87.8 个）。一次性改动比整个解的特征数还要大几倍的位点，大概率会使原本精挑细选的精英子集瞬间失效，导致贪婪选择机制（Greedy Rule）直接拒绝这一变异。
  2. **KER 的实际执行率存疑**：审稿人怀疑绝大多数 KER 生成的变异个体都被丢弃了，其在整个算法中可能根本没有实质贡献，纯属多余的计算开销。
  3. **核心机理缺乏实证度量**：文中口头宣称“播种策略保护了种群多样性”、“防御了胜者诅咒（Winner's curse）”，但全文没有任何种群多样性度量指标（如种群汉明距离或方差），也没有噪声先验扰动实验。
* **【审稿人观点与意图】**
  * 审稿人指出作者在参数设计上缺乏对维度的尺度自适应思考（固定比例在高维下失效），并对文章中的口头宣称提出强烈质疑，要求拿出硬核的数据统计。
* **【审稿人期望的交付成果】**
  * 统计并汇报 **KER 的真实接受率（Acceptance Rate）** 以及 KER 产生全局最优更新（$g_{\mathrm{best}}$ updates）的真实贡献占比。
  * 提供具体的**种群多样性度量变化曲线**，或通过噪声先验实验（Noisy-prior experiment）正面验证抗胜者诅咒能力。

---

### 意见 8：运行时间加速（3.4×）归因不当与消融变体耗时缺失
* **【审稿人原文】**
  
  > "The 3.4× speed-up (51.3 s vs 175.0 s) is, by the authors' own account, a consequence of smaller subsets rather than a cheaper algorithm, and KDS-EL performs about 15% more evaluations than MEL. Runtimes for the seeded ablation variants should be given in the main text to show how much of the gain comes from seeding alone."
* **【具体含义剖析】**
  1. **加速原因并非算法本身的复杂度降低**：KDS-EL 运行时间为 51.3 秒，原版 MEL 为 175.0 秒（加速 3.4 倍）。但根据 3-NN 距离计算的物理机制，耗时与当前评估子集的特征数量 $d_{\mathrm{selected}}$ 成严格正比。MEL 处于 $d \approx 2{,}722$ 的高维泥潭，而 KDS-EL 处于 $d \approx 88$ 的超稀疏状态。
  2. **评估次数其实增加了 15%**：由于 KER 的额外评估，KDS-EL 实际执行的适应度评价次数比 MEL 还要多 15%。因此所谓的 3.4 倍加速，纯粹是“挑选更少特征导致下游 3-NN 算得快”，而不是“算法搜索效率更高”。
  3. **先验播种占了多大功劳未知**：消融实验中只加入了播种机制的变体（MEL_MI）的运行时间未在正文中充分交代，读者无法判断是 MI 播种直接压低了特征数，还是协同演化机制的功劳。
* **【审稿人观点与意图】**
  * 审稿人要求作者保持学术诚实：不要把下游分类器的计算捷径伪装成演化算法本身的轻量化，必须透明化展示各个消融变体的耗时分解。
* **【审稿人期望的交付成果】**
  * 在正文主表及分析中，完整列出所有消融变体（MEL_MI、NoPool 等）的**真实运行时间（Wall-Clock Time）**。
  * 客观重构关于加速比的叙述，明确说明加速的物理根源来自于稀疏子集对 $k$-NN 欧氏距离维度的几何级压缩。

---

### 意见 9：数据集重复造假嫌疑（ALL_AML vs Leukaemia）与统计检验缺陷
* **【审稿人原文】**
  
  > "ALL_AML and Leukaemia have identical size (72 × 7,129) and near-identical results for every method, so they look like the same data counted twice and inflate N in the Friedman and Wilcoxon tests. The 10-run Mann–Whitney tests appear to use one fixed CV split (a synchronized seed) and so capture only optimizer noise, and the Friedman ranks use accuracy alone despite the multi-criteria claims. PSO-CSM's p = 1.91e-6 is an exact value, whereas the repeated 1.32e-4 entries match the normal approximation (the exact value for n = 19 is about 3.8e-6)."
* **【具体含义剖析】**
  1. **极其严重的数据集重复致命伤（Fatal Issue）**：生物信息学领域经典公开数据集中的 `ALL_AML` 和 `Leukaemia` 均源自 Golub et al. (1999) 的同一批白血病芯片数据，两者的样本和特征数完全相同（72 样本，7,129 基因），所有对比算法在这两个数据集上的表现几乎分毫不差。审稿人明确指出这等同于**同一个数据集被计算了两次**，在统计检验（Friedman 和 Wilcoxon 检验）中人为虚增了样本量 $N$！
  2. **10 次独立运行基于固定划分**：10 次运行全部在同一个固定的 5 折划分下进行，只能反映优化器的随机寻优噪声，根本无法评估算法对样本划分变动的稳健性。
  3. **多目标宣称与单目标排名的矛盾**：论文通篇宣称算法实现了精度与特征数量的“多准则/多目标平衡”，但在 Friedman 排名和统计检验时却只采用准确率指标。
  4. **统计 $p$ 值的计算混乱与造假嫌疑**：表格中对 PSO-CSM 给出了精确值 $1.91 \times 10^{-6}$，但其余多处却出现了完全相同的 $1.32 \times 10^{-4}$，审稿人推导指出这明显是用了渐近正态近似（Normal Approximation）而非精确置换值（当 $N = 19$ 时，Wilcoxon 符号秩检验双尾最小精确 $p$ 值为 $3.8 \times 10^{-6}$），计算标准前后不一致。
* **【审稿人观点与意图】**
  * 审稿人在这里指出了严肃的学术规范与统计严谨性问题，必须进行扎实客观的技术澄清与统计纠正。
* **【审稿人期望的交付成果】**
  * 彻底核查并治理 `ALL_AML` 与 `Leukaemia` 数据集重叠问题（合并或替换为一个全新的独立数据集，重新计算统计全景）。
  * 规范非参数统计检验计算流程，统一采用严格的精确检验（Exact Test）重算所有 Wilcoxon 和 Friedman $p$ 值。
  * 明确统计检验所覆盖的维度，将特征规模和综合表现纳入统计评估考量。

---

### 意见 10：表格标记前后矛盾与正负号反转
* **【审稿人原文】**
  
  > "By my count, Table 4's cell markers disagree with its summary row and Table 6 for w/o TPS (10/9/1 vs 11/8/1), SaWDE (15/4/1 vs 15/3/2) and BPSO (16/3/1 vs 17/2/1). The table note also defines +/− backwards, since '+' marks cells where KDS-EL is better."
* **【具体含义剖析】**
  1. **计数不一致的低级错误**：Table 4 中实际带有标记的单元格数量，与表格底部的汇总统计行（Win/Tie/Loss）以及 Table 6 中的汇总数据存在出入：
     * w/o TPS：单格标记统计为 10/9/1，汇总行却写着 11/8/1；
     * SaWDE：单格标记统计为 15/4/1，汇总行写着 15/3/2；
     * BPSO：单格标记统计为 16/3/1，汇总行写着 17/2/1。
  2. **符号定义反转**：表格注释中对“$+$”和“$- $”的学术定义搞反了（通常惯例应严谨定义“$+$”表示提议算法显著优于对比算法）。
* **【审稿人观点与意图】**
  * 暴露出论文在最终校对阶段极不认真，给审稿人留下了“数据存在手工拼接、甚至数字不可信”的恶劣印象。
* **【审稿人期望的交付成果】**
  * 编写自动化脚本对全表所有单元格符号和汇总统计进行绝对一致性核查与修复。
  * 规范 Table 4 及所有表格的注释说明。

---

### 意见 11：生物学特征解释流于表面且缺乏富集验证
* **【审稿人原文】**
  
  > "HPN and AMACR are classic prostate-cancer markers that a plain univariate filter would be expected to surface, and DES and ACTG2 in the Alon colon data are commonly attributed to differing smooth-muscle content of normal and tumour biopsies. Without enrichment tests, stability across runs, or baseline-selected genes for comparison, this does not support the claim that the selected genes reflect biological relevance rather than computational artifacts."
* **【具体含义剖析】**
  1. **选出的基因纯属平凡基因（Trivial Markers）**：论文列举了前列腺癌中的 HPN 和 AMACR，审稿人直接指出：任何一个最简单的单变量 Filter（如方差分析、T 检验、单变量 MI）闭着眼睛都能把这两个基因选在最前面，根本不需要演化算法去发现。
  2. **Colon 数据集基因的病理学混淆**：论文提到的 DES 和 ACTG2 在 Alon 结肠癌数据集中之所以表达差异巨大，是因为正常组织和肿瘤组织活检样本中平滑肌（Smooth-muscle）细胞的比例天然不同，这在生物医学领域是众所周知的非肿瘤特异性混杂因素（Confounder），并不能作为演化算法具有“癌症靶点识别能力”的证据。
  3. **三无验证**：缺乏基因功能富集分析（No enrichment tests）、缺乏跨运行子集稳定性分析（No stability across runs）、缺乏与对比算法所选基因的差异对比。
* **【审稿人观点与意图】**
  * 审稿人极其精通肿瘤生物学机制，强烈反对计算机领域学者拿两三个文献中见过的经典基因做“故事拼接（Just-so storytelling）”。没有系统性的通路富集和稳定性证明，所谓的生物学意义毫无价值。
* **【审稿人期望的交付成果】**
  * 补充基于权威数据库（如 KEGG、Gene Ontology [GO]）的**基因集功能富集分析（Gene Set Enrichment Analysis）**。
  * 测定并汇报多次独立运行中挑选基因的**稳定性指数（如 Jaccard 相似度或 Kuncheva 稳定性指数）**。
  * 将 KDS-EL 选择的基因签名与经典 Filter 及其他对比算法所选特征进行交集对比分析。

---

### 意见 12：问题场景包装过度与文本规范缺失
* **【审稿人原文】**
  
  > "Fewer than half the datasets have n < 100 (9 of 20) and three have D ≈ 500–1,000, so the 'N ≪ 100, D ≫ 10³' framing fits only part of the suite. MII and AIR are undefined in section 4.2.5 and there is no code availability statement."
* **【具体含义剖析】**
  1. **前言与实验集脱节**：文章反复强调面向“超高维极度小样本（$N \ll 100, D \gg 10^3$）”的极端挑战，但审稿人清点发现：20 个数据集中样本量小于 100 的只有 9 个（不到一半），甚至有 3 个数据集维度只有 500 到 1000。论文的包装口径与实验基准范围不符。
  2. **缩写未定义**：Section 4.2.5 中突兀出现了 MII 和 AIR 等缩写，全文此前未作任何形式化定义。
  3. **缺失代码可用性声明**：未提供公共代码仓库链接。
* **【审稿人观点与意图】**
  * 语言表述存在浮夸包装的倾向，文本细节存在疏漏，缺乏顶级期刊要求的代码公开与透明性。
* **【审稿人期望的交付成果】**
  * 客观修正引言和实验部分的表述，科学、准确地界定高维小样本的实际覆盖范围。
  * 在首次出现处严谨定义所有策略机制的完整术语及缩写。
  * 补充完整的代码与数据开源声明（Code & Data Availability Statement）。

---

## 三、Reviewer 4 逐条审稿意见深度解析（Major 4 条 + Minor 11 条）

### 1. Major Comments 深度剖析（4 条核心痛点）

#### Major 1：全数据集先验与目标函数导致评估失真、对比不公
* **【审稿人原文】**
  
  > "Because the MI prior and the fitness both use the full dataset, the reported accuracy is the optimization objective itself rather than a true generalization estimate. KDS-EL receives label-based guidance, harsher penalty weights, and a different evaluation budget than the competitors, so the comparison is not fair."
* **【具体含义与诉求】**
  * 与 Reviewer 1 意见 1 完全共振：全样本计算 MI 先验构成了**监督信息标签泄露**；以内部优化指标替代真实泛化性；对提议方法使用了更严格的惩罚偏向以及更高的评价次数预算（2300 vs 2000）。
  * **审稿人观点**：这场比赛是不公平的（The comparison is not fair），KDS-EL 凭借“抢跑（全量标签先验）+ 多吃预算”取得了表观胜利。
  * **期望成果**：剥离全量标签泄露（Fold-internal 先验）、统一定格评估预算至 2,000 FEs、在相同约束条件下重新对齐。

#### Major 2：核心理论宣称被正文自身细节所削弱与证伪
* **【审稿人原文】**
  
  > "Several claims, including the role of P2, the source of the speedup, the TPS ablation, and the fitness plots, are undermined by the paper’s own details."
* **【具体含义与诉求】**
  * 审稿人直接指出论文存在**内部自我矛盾**：
    * 声称 $\mathcal{P}_2$ 促进了极端稀疏探索，但参数推导却显示其绝大多数粒子越界受罚；
    * 声称算法实现了 3.4 倍加速，但实际开销完全受 3-NN 特征维度支配；
    * TPS 消融设计不匹配；
    * 适应度收敛图掩盖了真实特征项权重的极微弱驱动。
  * **审稿人观点**：作者对算法机理的包装站不住脚，只要仔细阅读文章自己披露的技术细节，就能发现前后矛盾。
  * **期望成果**：必须重构理论解释，剔除虚妄的假说，用真实严密的数学推导和代码实际行为重新论述。

#### Major 3：相对核心对手优势微弱、排名失真与检验族人为填充
* **【审稿人原文】**
  
  > "The advantage over bIRIME is only borderline significant, ties and ceiling effects distort the rankings, and the Holm family is padded with the authors’ own variants."
* **【具体含义与诉求】**
  1. **对顶尖对比算法（bIRIME）优势极小**：在 20 个数据集上，KDS-EL 相比于顶尖同行 bIRIME（2024 年发表于 *iScience*）的优势处于临界边缘（Borderline significant, 准确率均值 95.45% vs 94.54%，差值不足 1%，且存在大量打平）。
  2. **天花板效应与排名失真**：部分数据集上多个算法均达到了 98%~100% 的准确率天花板（Ceiling effect），使得平均排名失真。
  3. **Holm 多重假设检验作弊嫌疑**：在事后统计检验（Holm-Bonferroni post-hoc test）中，作者把自己的消融变体（如 MEL_MI、NoPool 等）当成了独立对比算法塞进比较族中进行校正，人为稀释了排位阈值。
  * **期望成果**：客观承认与 bIRIME 在纯精度上的接近，突出 KDS-EL 在特征压缩比（87.8 vs 407.7）和综合计算成本上的双重权衡价值；将自身消融变体从对比同行 Holm 检验族中剔除，重新计算纯正算法梯队的统计检验。

#### Major 4：技术组件拼凑组合，缺乏原创本质创新
* **【审稿人原文】**
  
  > "Every component is already known, so the contribution is a combination on top of MEL that needs stronger evidence."
* **【具体含义与诉求】**
  * 审稿人认为互信息播种、信用记忆更新、精英位翻转、动态权重调度在演化计算领域均已有现成概念，KDS-EL 属于在 MEL 基础上的“组合拼装（Engineering Combination）”。
  * **期望成果**：必须通过极其清晰深刻的“协同机理分析”证明：这些组件不是简单的生硬拼接，而是针对超高维生物特征选择中特定病态退化（搜索空间维数灾难、特征冗余震荡）所设计的紧密闭环。

---

### 2. Minor Comments 逐条深度剖析（11 条具体技术点）

* **Minor 1：权重记忆 $W$ 判别力证据缺失与噪声项漂移**
  * 【原文】*"There is no evidence that the importance memory W separates informative from noise features, and the noise term in Eq. (23) shifts as W decays."*
  * 【剖析与诉求】审稿人质疑 $W$ 到底有没有把有效特征和噪声特征分开。并且随着代数增加，$W$ 不断衰减其整体方差变小，导致高斯扰动项发生系统性漂移。需绘制 $W$ 在真实信息基因与伪基因上的分布分离度图，并证明公式的稳定性。
* **Minor 2：口头宣称抗胜者诅咒必须补充置换实验**
  * 【原文】*"The defense against the Winner’s curse is only verbal and should be tested with a label-permutation experiment."*
  * 【剖析与诉求】在小样本高维优化中，“胜者诅咒”特指优化器选出的特征在训练折上表现极佳但纯属偶然。审稿人要求执行标签打乱置换实验（Label-permutation test），用实测数据证明提议方法不会在打乱数据上过拟合。
* **Minor 3：应汇报初始真实子集规模**
  * 【原文】*"The actual initial subset sizes should be reported, since they depend heavily on the MI distribution."*
  * 【剖析与诉求】初始化子集的实际特征数量完全取决于该数据集的互信息分布形态，不能只给理论比例，必须在表格中列出每个数据集在初始化完成时的真实特征数。
* **Minor 4：敏感性分析数据集过少且存在测试集调参嫌疑**
  * 【原文】*"Sensitivity is tested on only four datasets, and the defaults appear tuned on the same benchmarks used for the final results."*
  * 【剖析与诉求】超参数敏感性仅在 4 个数据集上汇报，且这 4 个数据集直接混在 20 个最终测试集中。需澄清超参数的鲁棒性，并在文本中明确调优隔离原则。
* **Minor 5：Colon 在 SVM/RF 上的精度骤降表明对 3-NN 过拟合**
  * 【原文】*"The accuracy drop on Colon with SVM and Random Forest suggests overfitting to the 3-NN wrapper."*
  * 【剖析与诉求】严厉指出所选特征严重过拟合 3-NN Wrapper，缺乏分类器无关的内在泛化价值。必须补充更多数据集上的跨分类器泛化实验（SVM、RF、Naive Bayes、LDA）以证伪纯粹过拟合的质疑。
* **Minor 6：生物学验证缺乏富集分析与 Baseline 对比**
  * 【原文】*"A few literature-backed genes are anecdotal and need enrichment analysis or comparison with baseline-selected genes to support the biological claim."*
  * 【剖析与诉求】与 Reviewer 1 意见 11 完全一致，要求使用 GO/KEGG 进行定量富集分析，并与对比算法选取的基因做交叉比较。
* **Minor 7：部分数据集存在类别失衡，需汇报 Balanced Accuracy / F1** [✅ 已完成]
  * 【原文】*"Some datasets are not perfectly balanced, so balanced accuracy or F1 should be reported."*
  * 【剖析与诉求】与 Reviewer 1 意见 2 完全一致，要求增加 Balanced Accuracy 或 F1-Score 指标。
* **Minor 8：硬编码概率（>99.9% 破坏性变异）缺乏严密数学推导**
  * 【原文】*"Claims such as '>99.9% probability' of destructive mutations are stated without derivation."*
  * 【剖析与诉求】文中随手写的“变异破坏性概率大于 99.9%”属于典型的缺乏推导的夸大说辞，必须补上基于超几何分布或二项分布的组合数学推导，或者直接删除该口语化表述。
* **Minor 9：Table 1 存在刻意设计的引导性偏见**
  * 【原文】*"Table 1 appears designed to make the proposed method look uniquely complete."*
  * 【剖析与诉求】现有特征选择算法特性对比表（Table 1）将机制勾选列全部倾向于自身，存在“自卖自夸”的刻意引导感。需将其改为客观的特性维度对比。
* **Minor 10：公开代码、随机种子与划分文件**
  * 【原文】*"Code, seeds, and CV splits should be publicly released instead of being 'available on request.'"*
  * 【剖析与诉求】坚决反对“代码数据索取即得（available on request）”的虚伪套话，要求提供匿名公共代码链接（如 GitHub / Zenodo）。
* **Minor 11：正文存在重复性宣传用语及引文顺序混乱**
  * 【原文】*"The text is repetitive and promotional, and some references are uncited or out of order."*
  * 【剖析与诉求】论文存在重复夸赞自身机制的宣传性语言（Promotional language），存在引文序号错乱或未引用的文献。需全面清洗学术语调，修复参考文献。

---

## 四、两位审稿人共识焦点与高危预警交叉矩阵

为了让修改方案能够“一针见血”击中要害，以下将两位审稿人共同关注的 7 大核心危机进行归纳定性：

| 危机维度 | Reviewer 1 对应点 | Reviewer 4 对应点 | 致命程度 | 审稿人核心诉求本质 |
| :--- | :--- | :--- | :---: | :--- |
| **1. 实验协议与数据泄露** | 意见 1 (Nested CV, MI leakage) | Major 1, Minor 2, 5 (Overfitting, Label leakage) | **⭐⭐⭐⭐⭐<br>(一票否决项)** | 必须阻断全数据 MI 先验渗透；采用严谨测试协议破除乐观偏差假象。 |
| **2. 实验公平性与 Baseline 缺失** | 意见 3 (Budget 2300 vs 2000, Filter baselines) | Major 1 (Budget, guidance fairness) | **⭐⭐⭐⭐⭐<br>(一票否决项)** | 统一评估预算（FEs = 2,000）；补齐简单 Filter 基准以证明演化算法价值。 |
| **3. 机制因果与消融有效性** | 意见 4, 5, 6, 7 (打包消融, TPS/W/KER 机制质疑) | Major 2, Minor 1, 8 (机制前后矛盾, W 信号漂移) | **⭐⭐⭐⭐<br>(核心理论关)** | 解耦阶乘消融；用微观动力学图和实测数据（KER 接受率、P2 可行率）打破“口头宣称”。 |
| **4. 统计检验规范与数据真实性** | 意见 9, 10 (ALL_AML 重复, Table 4 符号冲突, p 值误用) | Major 3 (bIRIME 边界优势, Holm 族掺水) | **⭐⭐⭐⭐<br>(学术诚信关)** | 剔除重复数据集；重算精确 p 值；纠正表格与符号前后不一致。 |
| **5. 评估指标与类别不平衡** | 意见 2 (类别失衡矛盾, BAcc/AUC) | Minor 7 (Balanced Accuracy / F1) | **⭐⭐⭐<br>(指标完整性)** | 修改前后矛盾，全量补充 Balanced Accuracy / F1 指标及类别分布。 |
| **6. 生物学机制验证深度** | 意见 11 (平滑肌混杂, 平凡基因, 无富集) | Minor 6 (轶事式举例, 需富集和基线对比) | **⭐⭐⭐<br>(跨学科说服力)** | 引入 KEGG/GO 基因通路富集分析与跨运行选择稳定性（Jaccard 指数）。 |
| **7. 学术态度与开源可复现性** | 意见 12 (N/D 包装过度, 无开源代码) | Minor 9, 10, 11 (宣传性语言, 必须公开代码种子) | **⭐⭐⭐<br>(学术规范性)** | 降调去吹捧；全面开源代码与固定测试折划分。 |

---
*报告生成完毕，请参阅配套文档 `review_round_1/02_revision_plan_outline.md` 查看整体修改方案大纲与应对战略。*
