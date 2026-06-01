# KDS-EL 论文修改路线图

> 基于模拟同行评审的修改建议（4 位审稿人 + 魔鬼辩护人）
> 决定：**大修（Major Revision）**
> 建议截止日期：收到决定后 **6 周**

---

## 优先级 1——必须修改（Required Revisions）

### R1：替换所有占位符引用

**来源**：全体审稿人
**严重性**：关键（投稿阻断）
**预估工作量**：1 天

**问题**：以下引用键为占位符，编译后将产生未解析引用：

| 占位符键 | 出现位置 | 需要替换为 |
|---------|---------|-----------|
| `\citep{MEL_CITE}` | kdsel.tex:263, 265, 291 | MEL 论文的实际 BibTeX 键 |
| `\citep{IGPSO_CITE}` | kdsel.tex:269, 292, 796 | IGPSO (2024) 论文的实际 BibTeX 键 |
| `\citep{PSOCSM_CITE}` | kdsel.tex:267, 293, 793 | PSO-CSM (2025) 论文的实际 BibTeX 键 |
| `\citep{SARMTPSO_CITE}` | kdsel.tex:349 | SAR-MTPSO 论文的实际 BibTeX 键 |

**修改步骤**：
1. 在 `references.bib` 中为上述 4 篇论文添加完整条目
2. 在 `kdsel.tex` 中将占位符键替换为实际 BibTeX 键
3. 编译验证所有引用正确解析

---

### R2：填写作者和机构信息

**来源**：主编（EIC）
**严重性**：关键（投稿阻断）
**预估工作量**：0.5 天

**问题**：kdsel.tex 第 39-52 行包含占位符信息。

**需要修改的位置**（kdsel.tex:39-55）：
```latex
% 当前内容（占位符）：
\author[1]{\textcolor[RGB]{0,0,1}{First Author}}
\fnmark[1]
\ead{first@university.edu.cn}

\author[1]{\textcolor[RGB]{0,0,1}{Second Author}}
\fnmark[1]
\cormark[1]
\ead{second@university.edu.cn}

\author[1]{\textcolor[RGB]{0,0,1}{Third Author}}
\fnmark[1]
\ead{third@university.edu.cn}

\address[1]{School of Computer Science and Technology, University Name, City, Country}

\cortext[cor1]{Corresponding author.}
\fntext[fn1]{Equal Contribution.}
```

**修改为**：实际作者姓名、邮箱、单位地址和通讯作者标注。

---

### R3：补充 Nemenyi 事后检验和 CD 图

**来源**：主编、审稿人 1（方法学）、审稿人 2（领域）
**严重性**：重大
**预估工作量**：2 天

**问题**：Friedman 检验（χ²=47.38，p=1.30×10⁻⁷）确认了全局显著性，但缺少事后检验来确定哪些具体方法对之间存在显著差异。

**修改要求**：
1. 对 9 个方法在 9 个数据集上的精度结果执行 Nemenyi 事后检验
2. 报告临界差异（CD）值
3. 添加 CD 图（Critical Difference Diagram）作为新图

**推荐工具**：
- Python：`scikit-posthocs` 库（`scikit_posthocs.posthoc_nemenyi`）
- 或 `autorank` 库（自动生成 CD 图）
- 或 Orange 数据挖掘软件的 CD 图功能

**添加位置**：
- 在第 4.5 节（Statistical Significance Analysis）中添加 Nemenyi 检验结果
- 在 Wilcoxon 表（表 6）之后添加 CD 图

**新增图表建议**：
```
图 X：Nemenyi 事后检验的临界差异（CD）图
- x 轴：平均排名（Average Rank）
- 横线连接的方法对之间无显著差异（p > 0.05）
- CD 值标注在图上
```

---

### R4：对 Wilcoxon 检验施加 Holm-Bonferroni 校正

**来源**：审稿人 1（方法学）、主编
**严重性**：重大
**预估工作量**：1 天

**问题**：表 6 报告了每个数据集的 8 次成对 Wilcoxon 检验（KDS-EL vs. 每个对比方法），共计 72 次比较，未进行多重比较校正。以 α=0.05 进行 8 次比较，族错误率为 1-(0.95)^8 ≈ 34%。

**修改要求**：
1. 对每个数据集的 8 个 p 值应用 Holm-Bonferroni 校正
2. 在表 6 中同时报告原始 p 值和校正后的 p 值
3. 更新表中加粗/下划线标注以反映校正后的显著性

**校正方法**（Holm-Bonferroni）：
```
对每个数据集：
1. 将 8 个 p 值从小到大排序：p(1) ≤ p(2) ≤ ... ≤ p(8)
2. 校正后 p 值：p'(i) = max(p(i) × (9-i), 1.0)，其中 i = 1,...,8
3. 从 i=1 开始，找到第一个 p'(i) > 0.05 的位置，该位置及之后的所有比较均不显著
```

**表 6 修改格式建议**：
```latex
% 在表注中添加：
% $p$-values adjusted via Holm-Bonferroni correction. Original $p$-values in parentheses.
```

---

### R5：用双因素 ANOVA 替换加法协同指标

**来源**：主编、审稿人 1（方法学）、魔鬼辩护人
**严重性**：重大
**预估工作量**：2 天

**问题**：当前协同指标（公式 8）为：
$$\Delta_{\mathrm{syn}} = \Delta_{\mathrm{Full}} - \Delta_{\mathrm{DRS}} - \Delta_{\mathrm{KER}}$$
这是简单加法模型，假设 DRS 和 KER 独立贡献，与论文声称的"协同耦合"自相矛盾。

**修改要求**：
1. 对 9 个数据集 × 4 个变体（MEL、DRS-only、KER-only、Full）的精度数据执行双因素 ANOVA
   - 因素 A：DRS（有/无）
   - 因素 B：KER（有/无）
   - 关注交互项 A×B 的显著性
2. 报告 F 值、p 值和效应量（η²）
3. 如果交互项显著，说明存在真正的协同效应；如果不显著，说明是加法效应
4. 更新公式 8 和相关讨论

**修改位置**：
- 第 4.6 节（Ablation Study）：重写协同效应分析
- 公式 8：替换或补充为 ANOVA 交互项检验
- 表 7：可考虑添加 ANOVA 结果行

**新增表格建议**：
```
表 X：双因素 ANOVA 结果（DRS × KER 交互效应）

| 来源 | df | SS | MS | F | p | η² |
|------|----|----|----|---|---|-----|
| DRS 主效应 | 1 | ... | ... | ... | ... | ... |
| KER 主效应 | 1 | ... | ... | ... | ... | ... |
| DRS × KER 交互 | 1 | ... | ... | ... | ... | ... |
| 误差 | ... | ... | ... | | | |
```

---

### R6：添加等计算预算对比实验

**来源**：魔鬼辩护人、审稿人 3（实践视角）
**严重性**：重大
**预估工作量**：3 天

**问题**：KDS-EL 每次运行执行 4,300 次适应度评估（(2N + k_e) × T = 43 × 100），而 BPSO/SaWDE/FWPSO 仅执行 2,000 次（N × T = 20 × 100）。精度提升可能完全来自 2.15 倍的计算预算增加。

**修改要求**：
1. 使用更大的迭代次数 T' 运行 FWPSO，使其总评估次数等于 KDS-EL（约 4,300 次）
   - FWPSO: N × T' = 20 × T' = 4,300 → T' ≈ 215
2. 在所有 9 个数据集上比较 KDS-EL（T=100）和 FWPSO（T'=215）
3. 报告精度、特征数量和运行时间
4. 讨论结果：如果 FWPSO（T'=215）与 KDS-EL（T=100）精度相当，说明 KDS-EL 的优势来自计算预算而非机制设计

**新增表格建议**：
```
表 X：等计算预算对比（KDS-EL vs. FWPSO 扩展）

| 数据集 | KDS-EL (T=100, 4300次) | FWPSO (T'=215, 4300次) | 差异 |
|--------|----------------------|----------------------|------|
| Adenoma | 98.37±1.42 | ? | ? |
| ... | ... | ... | ... |
```

**添加位置**：在第 4.3 节（Classification Accuracy Comparison）之后新增小节。

---

### R7：补充生物学验证或删除生物标志物声明

**来源**：审稿人 2（领域）、审稿人 3（实践）、魔鬼辩护人
**严重性**：重大
**预估工作量**：2-5 天（取决于选择方案 A 或 B）

**问题**：结论中声称 KDS-EL 是"生物标志物发现的引人注目的选择"（第 1466 行），但未提供任何生物学验证。

**方案 A：添加生物学验证（推荐）**

选择 1-2 个数据集（建议 Leukaemia 或 Colon，因为有已知的癌症基因），执行以下分析：
1. **通路富集分析**：
   - 提取 KDS-EL 选定的特征（基因）
   - 使用 DAVID、Enrichr 或 g:Profiler 进行 GO/KEGG 通路富集
   - 讨论富集的通路是否与已知的癌症生物学相关
2. **与已知生物标志物的重叠**：
   - 检查选定特征是否包含文献中已报道的癌症生物标志物
   - 报告重叠比例
3. **特征重要性排名**：
   - 展示 KER 权重向量中排名前 20 的特征
   - 讨论其生物学意义

**方案 B：删除/改写生物标志物声明**

如果选择不添加生物学验证，需要修改以下位置：

| 位置 | 当前措辞 | 建议改为 |
|------|---------|---------|
| 摘要第 29-30 行 | 未提及生物标志物 | 无需修改 |
| 第 1465-1467 行 | "makes KDS-EL a compelling choice for biomarker discovery and other high-stakes biomedical classification tasks where both predictive performance and interpretability are essential" | "makes KDS-EL a promising candidate for high-dimensional biomedical classification tasks where feature compactness and predictive performance are both critical" |
| Highlights 第 66-67 行 | "Achieve superior classification accuracy and substantial feature reduction against eight competitors" | 无需修改（未提生物标志物） |

---

## 优先级 2——建议修改（Suggested Revisions）

### S1：区分与多目标 FS 方法的差异

**来源**：审稿人 2（领域）
**优先级**：P2
**预估工作量**：1 天

**问题**：论文声称 NHD"从未在基于包装器的进化 FS 中作为首选选择目标"，但多目标 FS 方法（NSGA-II-FS、MOEA/D-FS）已使用多样性作为显式目标。

**修改位置**：第 2.2 节（Population Diversity in Evolutionary Feature Selection），在第 323-328 行之后添加段落。

**建议添加内容**：
```latex
\par{
Multi-objective feature selection methods, such as those based on
NSGA-II~\citep{deb2002fast} and MOEA/D~\citep{zhang2007moea},
have incorporated diversity metrics as explicit optimisation objectives.
However, these approaches formulate feature selection as a genuinely
multi-objective problem, where diversity is one of several competing
objectives to be Pareto-optimised.
In contrast, KDS-EL's DRS operates within a single-objective PSO
framework, using NHD as a \emph{secondary selection criterion} alongside
fitness within a bi-objective selection pool, rather than as a
full Pareto objective in a multi-objective optimisation sense.
The key distinction is that DRS's adaptive schedule
$\alpha_{\mathrm{cd}}(t)$ dynamically transitions from diversity
exploration to fitness exploitation, whereas multi-objective methods
maintain diversity throughout the search without such a transition.
}
```

---

### S2：论证 KNN 分类器选择并考虑添加额外分类器

**来源**：审稿人 2（领域）、审稿人 3（实践）
**优先级**：P2
**预估工作量**：3 天

**问题**：KNN（k=3）被用作适应度评估器，但在生物信息学中 SVM 和随机森林更常用。KNN 对维度诅咒敏感。

**修改 1——添加论证**（第 3.1 节 Problem Formulation，第 412 行附近）：
```latex
% 在 "we set $\alpha = 0.9$, $K = 5$, and $k_{\mathrm{nn}} = 3$." 之后添加：
The choice of KNN as the fitness evaluator is motivated by its
computational efficiency and simplicity, which is critical given
the large number of fitness evaluations required by evolutionary
methods (4,300 per run in KDS-EL).
More complex classifiers such as SVM or Random Forest would
substantially increase per-evaluation cost.
Additionally, KNN's sensitivity to the curse of dimensionality
makes it a suitable stress test for feature selection methods:
if KDS-EL can improve KNN classification on high-dimensional data,
it demonstrates effective dimensionality reduction.
```

**修改 2——可选地添加 SVM 结果**（建议在附录或补充材料中）：
- 使用 SVM（RBF 核）替代 KNN，在 2-3 个代表性数据集上运行所有方法
- 报告结果表，讨论排名是否保持一致

---

### S3：添加特征选择稳定性分析

**来源**：审稿人 3（实践）
**优先级**：P2
**预估工作量**：1 天

**问题**：生物标志物发现要求所选特征在不同运行间保持一致。当前仅报告了平均特征数量，未报告稳定性。

**修改要求**：
1. 计算 10 次运行间特征选择的 Kuncheva 指数或平均 Jaccard 相似度
2. 报告每个数据集的稳定性指标

**Kuncheva 指数计算**：
```python
import numpy as np

def kuncheva_index(s1, s2, d):
    """s1, s2: 选定特征的索引集合; d: 总特征数"""
    r = len(s1)
    k = len(s1 & s2)  # 交集大小
    expected = r**2 / d  # 随机期望重叠
    return (k - expected) / (r - expected)
```

**添加位置**：在第 4.6 节（Ablation Study）或新增第 4.X 节（Stability Analysis）

**新增表格建议**：
```
表 X：特征选择稳定性（10 次运行间的平均 Jaccard 相似度）

| 数据集 | KDS-EL | KDS-EL/DRS | KDS-EL/KER | MEL |
|--------|--------|-----------|-----------|-----|
| Adenoma | ? | ? | ? | ? |
| ... | ... | ... | ... | ... |
```

---

### S4：添加现代组学数据集

**来源**：审稿人 2（领域）、审稿人 3（实践）
**优先级**：P2
**预估工作量**：3-5 天

**问题**：9 个数据集中 7 个来自 2000 年代初期的微阵列时代，可能无法代表现代生物信息学挑战。

**推荐数据集**：
1. **TCGA 泛癌 RNA-seq**：
   - 来源：The Cancer Genome Atlas
   - 特点：n≈500-1000，d≈20,000（基因）
   - 任务：癌症亚型分类
   - 获取：通过 TCGA 数据门户或 `TCGAbiolinks` R 包

2. **GTEx 正常组织 RNA-seq**：
   - 来源：Genotype-Tissue Expression
   - 特点：n≈1000+，d≈20,000
   - 任务：组织类型分类

3. **单细胞数据集**（如果计算资源允许）：
   - 来源：10x Genomics 示例数据或 Human Cell Atlas
   - 特点：n≈10,000+，d≈20,000+
   - 任务：细胞类型分类

**注意**：如果添加新数据集，需要在表 2（数据集汇总表）中添加对应行，并更新所有结果表格。

---

### S5：澄清"不需要额外的适应度评估"措辞

**来源**：魔鬼辩护人
**优先级**：P2
**预估工作量**：0.5 天

**问题**：第 604-606 行声称 KER"不需要额外的适应度评估"，但变异体被评估一次以检查是否改善了 P_best，这就是一次适应度评估。

**需要修改的位置**：

| 位置 | 当前措辞 | 建议改为 |
|------|---------|---------|
| 第 90 行（摘要） | "without additional fitness evaluations" | "with a single additional fitness evaluation per elite perturbation" |
| 第 205-206 行（贡献列表） | "with no additional fitness evaluations and a single interpretable parameter" | "with only one additional fitness evaluation per elite perturbation and a single interpretable parameter" |
| 第 604-606 行（KER 描述） | "without additional fitness evaluations" | "requiring only one additional fitness evaluation per elite perturbation to verify improvement" |
| 第 1451-1452 行（结论） | "without additional fitness evaluations" | "with minimal additional fitness evaluations" |

---

### S6：在收敛曲线上添加置信带

**来源**：审稿人 1（方法学）
**优先级**：P2
**预估工作量**：1 天

**问题**：收敛曲线（图 5 / fig8_convergence.png）未显示运行间方差的置信带。

**修改要求**：
1. 对每个迭代点，计算 10 次运行的均值和标准差
2. 在均值曲线周围绘制 ±1 标准差的阴影区域
3. 使用半透明填充（alpha=0.2-0.3）

**修改位置**：`paper/gen_convergence_figs.py`（如果存在）或生成图 5 的脚本

**代码修改建议**：
```python
# 在绘制均值曲线的基础上添加：
plt.fill_between(
    iterations,
    mean_fitness - std_fitness,
    mean_fitness + std_fitness,
    alpha=0.2,
    color=color,
    label=f'{method} ± 1 std'
)
```

---

### S7：添加 α_cd 调度敏感性分析（可选）

**来源**：审稿人 2（领域）
**优先级**：P3
**预估工作量**：2 天

**问题**：自适应调度 α_cd(t) = (t/T)² 未与替代方案比较。

**修改要求**：
1. 测试 3 种调度函数：
   - 二次（当前）：α_cd(t) = (t/T)²
   - 线性：α_cd(t) = t/T
   - 指数：α_cd(t) = (e^(t/T) - 1) / (e - 1)
2. 在 2-3 个代表性数据集上比较精度和特征数量
3. 报告结果，讨论调度选择的敏感性

**添加位置**：在第 4.6 节（Ablation Study）或附录中

---

## 优先级 3——文本与格式修改

### F1：验证参考文献样式兼容性

**问题**：使用了 `elsarticle-num` 参考文献样式，但文档类别为 `cas-dc`。
**修改**：确认 ESWA 投稿模板要求，必要时更改为兼容的样式。

### F2：修复表 1 缺失的年份

**位置**：kdsel.tex 第 291 行
```latex
% 当前：
MEL      & --   & \citep{MEL_CITE}                  & ...
% 应改为（填入 MEL 的发表年份）：
MEL      & 2024 & \citep{MEL_CITE}                  & ...
```
（年份请根据 MEL 实际发表年份填写）

### F3：添加 Stroke 数据集引用

**位置**：kdsel.tex 第 747 行
```latex
% 当前：
(CNS~\citep{pomeroy2002prediction}, Stroke)
% 应改为：
(CNS~\citep{pomeroy2002prediction}, Stroke~\citep{STROKE_CITE})
```
在 `references.bib` 中添加 Stroke 数据集的引用。

### F4：验证图 5 的 y 轴范围

**问题**：收敛曲线的 y 轴从 0 开始，可能无法有效可视化收敛差异。
**修改**：将 y 轴起点设为所有方法达到的最小适应度值的 90% 左右。

### F5：总体校对

- 检查全文拼写和语法
- 确认所有图表引用正确（\ref 和 \label 匹配）
- 确认所有公式编号正确

---

## 修改进度跟踪

| 编号 | 项目 | 状态 | 完成日期 |
|------|------|------|---------|
| R1 | 替换占位符引用 | ☐ 待修改 | |
| R2 | 填写作者信息 | ☐ 待修改 | |
| R3 | Nemenyi 事后检验 + CD 图 | ☐ 待修改 | |
| R4 | Holm-Bonferroni 校正 | ☐ 待修改 | |
| R5 | 双因素 ANOVA 替换协同指标 | ☐ 待修改 | |
| R6 | 等计算预算对比实验 | ☐ 待修改 | |
| R7 | 生物学验证或删除生物标志物声明 | ☐ 待修改 | |
| S1 | 区分与多目标 FS 的差异 | ☐ 待修改 | |
| S2 | 论证 KNN 选择 + 可选 SVM 结果 | ☐ 待修改 | |
| S3 | 特征选择稳定性分析 | ☐ 待修改 | |
| S4 | 添加现代组学数据集 | ☐ 待修改 | |
| S5 | 澄清"无额外评估"措辞 | ☐ 待修改 | |
| S6 | 收敛曲线置信带 | ☐ 待修改 | |
| S7 | α_cd 调度敏感性分析 | ☐ 待修改 | |
| F1 | 验证参考文献样式 | ☐ 待修改 | |
| F2 | 修复表 1 年份 | ☐ 待修改 | |
| F3 | 添加 Stroke 引用 | ☐ 待修改 | |
| F4 | 验证图 5 y 轴 | ☐ 待修改 | |
| F5 | 总体校对 | ☐ 待修改 | |
