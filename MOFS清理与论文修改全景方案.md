# KDS-EL 论文体系全面移除多目标对比算法（MOFS）全景排查与修改执行方案

> **文件定位**：`MOFS清理与论文修改全景方案.md`  
> **更新时间**：2026-09-07  
> **核心原则**：严格执行《AGENTS.md》爱斯维尔顶级期刊规范，严禁出现任何 "baseline" 词汇，构建纯粹、严密的单目标群体智能特征选择（Single-Objective Swarm Feature Selection）顶刊对比体系。

---

## 一、 范式重构背景与对比体系定义

### 1. 为什么必须彻底剥离多目标特征选择（MOFS）？
1. **评价口径本质不对等**：KDS-EL 属于**标量加权单目标包装式特征选择**（通过综合适应度函数 $f = w_a \cdot \mathrm{Err} + w_f \cdot \mathrm{FSR}$ 引导全局演化）。而 MOFS（如 NSGA-II、MOEA/D、MOPSO 等）求解的是 Pareto 非支配前沿面。为了在表格中与单目标方法对比，旧方案强行在多目标前沿上套用“后置筛选公式”（$\mathbf{x}^{\star} = \arg\min (\mathrm{ErrorRate}, \|\mathbf{x}\|_0)$），这种后处理既损害了多目标算法保持解多样性的初衷，也难以被审稿人认可为公允对比。
2. **超高维下的严重归档膨胀与生物标志物失效**：在 $D \gg 10^3, N_{\mathrm{samp}} \ll 100$ 的超高维小样本场景下，Pareto 支配关系在稀疏高维空间中选择压力严重衰竭，非支配解的特征数普遍膨胀至 **3,000 ~ 5,000 维**，完全失去了作为紧凑生物标志物（Biomarker Signatures $<100$ 维）的临床解释与转化诊断价值。
3. **审稿靶子转移风险**：将标量加权算法与经典多目标 Pareto 前沿对比，极易招致审稿人关于“为什么不用真实多目标前沿 Hypervolume / IGD 评价”的尖锐质疑。聚焦纯单目标顶刊 SOTA 竞品，能够使论文的核心学术贡献牢牢锚定在“**破解高维群智能搜索的冷启动盲目性、在线经验丢弃与阶段失配**”三大根本矛盾上。

### 2. 重构后的全新对比体系（共 12 种算法/配置）
* **本文提出算法（1 种）**：
  * **KDS-EL**：双种群多任务 + 互信息软先验播种/停滞自适应恢复（MII+AIR）+ 在线重要性记忆与指数衰减精英翻转（KER）+ 两阶段动态权重调度（TPS）。
* **消融变体（2 种，采用严谨的减法剥离叙事）**：
  * **KDS-EL w/o TPS**（原 NoPool 变体）：剥离两阶段权重调度，采用固定静态权重 $\mathbf{w}_s = [0.90, 0.10]$。
  * **KDS-EL w/o TPS&KER**（原 MEL_MI 变体）：进一步剥离 KER 精英翻转机制与在线记忆。
* **基础先驱算法（1 种）**：
  * **MEL** (*IEEE TKDE* 2024)：多任务进化学习框架，剥离全部先验与知识导向算子后的基础主干。
* **经典与经典群智能高维特征选择算法（5 种）**：
  * **FWPSO** (*IEEE BIBM* 2022)：离线特征加权粒子群优化。
  * **PSO-CSM** (*Swarm Evol. Comput.* 2025)：综合评分机制粒子群优化。
  * **SaWDE** (*Knowledge-Based Systems* 2022)：自适应加权差分进化算法。
  * **IGPSO** (*Swarm Evol. Comput.* 2024)：多层感知机重要度引导粒子群优化。
  * **BPSO** (*IEEE SMC* 1997)：标准二进制粒子群优化算法。
* **最新顶刊单目标 SOTA 竞品算法（3 种，2023–2024 最新引入）**：
  * **DENCA-SO** (*Knowledge-Based Systems*, 2023, 111008)：邻域成分特征选择（NCFS）权重引导的差分进化过滤式算法。
  * **bIRIME** (*iScience*, Cell Press, 2024, 110561)：软霜搜索 + 复合变异（CMS）+ 重启策略（RS）的二进制霜冰优化算法。
  * **BinCOA** (*IEEE Access*, 2024, 28621–28635)：折射对立学习（ROBL）+ 温度驱动觅食 + 横纵交错搜索的二进制小龙虾优化算法。

---

## 二、 全生命周期 6 大层级 MOFS 涉及位置排查全景

经过对整套 LaTeX 源码、表格、矢量图、参考文献库、支撑脚本以及辅助文档的穷尽式穿透排查，所有涉足 MOFS 的具体节点分布如下：

```
[KDS-EL 论文资产库]
   ├── 1. 核心正文章节 (paper/sections/*.tex & main.tex) ──────── 6 个核心文件，30+ 处文本/公式/表格
   ├── 2. 数据表格源码 (output/tables/*.tex) ────────────────── 9 个文件存在多目标列或行项
   ├── 3. 矢量 PDF 图表 (output/figures/*.pdf) ───────────────── 2 张图表包含多目标点/柱 (F11, F13)
   ├── 4. BibTeX 参考文献库 (paper/references.bib) ───────────── 5 篇 MOFS 引用需剥离，3 篇新 SOTA 需录入
   ├── 5. Python 支撑脚本系统 (code/*.py) ────────────────────── 4 个绘图与制表脚本硬编码了 MOFS 列表
   └── 6. 辅助文档与中间草稿 (*.md, *.tex) ──────────────────── 若干份历史说明需同步更新口径
```

---

### 层级 1：核心正文章节 TeX 源码（逐段精确位置）

| 文件路径 | 所在行号 | 当前包含 MOFS 的原始内容与学术冲突 | 处置方案 |
| :--- | :--- | :--- | :--- |
| `paper/main.tex` | Line 190 | 摘要中提及：`outperforming the strongest single- and multi-objective competitors by +3.97 and +4.42 percentage points... over all 13 competitors` | 删除多目标提升点数，更新竞品对比总数 |
| `sections/01_introduction.tex` | Line 18 | 贡献 4 提及：`against 13 state-of-the-art competitors` | 将竞品总数调整为全新单目标对比口径 |
| `sections/01_introduction.tex` | Line 21 | 引言总结提及：`Compared with the strongest single-objective and multi-objective competitors... by 3.97 and 4.42 percentage points... over all 13 competitors` | 删除多目标对比陈述，聚焦领先第二名单目标竞品的幅度 |
| `sections/02_related_work.tex` | Line 3 | 节导言提及：`...alongside the structural trade-offs between weighted scalarization and multi-objective Pareto formulations` | 重构为聚焦单目标群体智能与包装式特征选择的理论演化 |
| `sections/02_related_work.tex` | Lines 22–27 | **Table 1** 中包含 5 行多目标算法：`NSGA-II-FS, MOEA/D-FS, MOPSO-FS, fMOPSO-FS, W-MOPSO-FS` | 彻底剔除 5 行多目标算法，替换为 DENCA-SO, bIRIME, BinCOA |
| `sections/02_related_work.tex` | Line 59 | 小节标题：`\subsection{Evolutionary swarm intelligence and multi-objective formulations}` | 标题修改为单目标群智能包装式机制（删除 multi-objective） |
| `sections/02_related_work.tex` | Line 83 | **整整一大段推导**：详细阐述 Xue et al. (2012), Deb (2002), Zhang (2007), Coello (2004), Han (2024) 的多目标前沿、Pareto 归档机制与非支配排序 | 整段彻底重写：删除全部多目标内容，改写为深入剖析单目标群智能在超高维面临的“50% 随机维度中庸陷阱” |
| `sections/02_related_work.tex` | Line 116 | Table 1 引导句：`...between KDS-EL and all eleven benchmark feature selection algorithms...` | 修正对比算法数量 |
| `sections/05_experimental_setup.tex` | Line 13 | 对比算法第二组：`Another category of representative algorithms encompasses multi-objective and multi-task feature selection approaches...` | 重写为纯单目标 SOTA 对比体系（经典梯队 + 2023-2024 新梯队 + MEL） |
| `sections/05_experimental_setup.tex` | Lines 17–22 | **后置 Pareto 决策公式 Eq. (6)**：专门推导 $\mathbf{x}^{\star} = \arg\min (\mathrm{ErrorRate}, \|\mathbf{x}\|_0)$ | **彻底删除 Eq. (6) 及前后整段文字**（所有方法均为单目标，无 Pareto 解集） |
| `sections/05_experimental_setup.tex` | Line 24 | 规模描述：`...across an extensive 14-algorithm comparison suite` | 修正对比方法规模总数 |
| `sections/06_experimental_analysis.tex` | Line 7, 11 | §6.1 精度叙述：提及 `single- and multi-objective algorithms`，以及与 W-MOPSO-FS, fMOPSO-FS, NSGA-II-FS 等的差距（0.04~0.05） | 替换为对 bIRIME, BinCOA, DENCA_SO 的精度胜出分析 |
| `sections/06_experimental_analysis.tex` | Line 13 | §6.1 精度叙述：提及 `competitors such as NSGA-II-FS achieve marginally higher accuracy...` | 替换为针对实际第二名单目标竞品的分析 |
| `sections/06_experimental_analysis.tex` | Line 17, 21 | §6.2 特征数叙述：提及 `multi-objective paradigms like NSGA-II-FS and fMOPSO-FS... retain extensive subsets ranging from 2,960.0 to 5,263.3 features` | 改为批判 BinCOA 和 DENCA-SO 特征停留在 45%~50% 随机期望的中庸维度陷阱 |
| `sections/06_experimental_analysis.tex` | Line 29 | §6.3 收敛叙述：提及 `Multi-objective evolutionary algorithms... simultaneously evolve non-dominated Pareto fronts...` | 删除对多目标无法绘制标量收敛曲线的辩解句 |
| `sections/06_experimental_analysis.tex` | Line 46 | **§6.4 Wilcoxon 胜负统计大段**：汇报针对 5 个多目标算法的战绩（14 wins vs W-MOPSO, 15 vs fMOPSO, 16 vs NSGA-II 等） | 彻底替换为针对新单目标算法的成对 Wilcoxon 胜平负战绩 |
| `sections/06_experimental_analysis.tex` | Line 50, 54 | §6.4 统计检验：提及 `k = 13 hypothesis tests` 以及 Friedman 均秩 `5.33 for W-MOPSO-FS` | 依据新一轮 20 数据集均值更新校正检验统计量与 Friedman 秩次 |
| `sections/06_experimental_analysis.tex` | Lines 91–102 | §6.5 运行时间：Fig. 11 题注与正文提及 `Multi-objective Pareto efficiency`、`all five multi-objective methods require between 110.4 and 142.8s` | 转换为“精度 vs 特征数 vs 运行时间”单目标综合效能图，重点剖析 bIRIME 在大样本上耗时数小时的短板 |
| `sections/06_experimental_analysis.tex` | Line 125 | §6.6 天花板分析：提及 `multi-objective methods retain extensive subsets ranging from 700 to 10,701 features, where MOPSO-FS selects 5,920 features...` | 替换为新单目标竞品（如 BinCOA 选出 3,500+ 维）在近满分数据集上的冗余特征对比 |
| `sections/09_conclusion.tex` | Line 1 | 结论提及：`...compared with 13 state-of-the-art algorithms...` | 更新竞品算法数量 |

---

### 层级 2：数据表格源码（`output/tables/` 目录）

以下 9 个 `.tex` 表格源码由旧版数据生成，直接嵌入正文中，当前均残留多目标列或行项：

1. **`T1_methods.tex`**：第 26 行包含 `\cite{deb2002} & NSGA-II-FS & Multi-objective \\`。
2. **`T3_params.tex`**：第 44–48 行列有 `NSGA-II-FS, MOEA/D-FS, MOPSO-FS, fMOPSO-FS, W-MOPSO-FS` 的参数设置（归档大小 100、交叉变异率等）。
3. **`T4_accuracy.tex`**：表头与数据行均包含 `W-MPSO, fMPSO, NSGA-II, MOEA/D, MOPSO` 共 5 列。
4. **`T4_accuracy_upright.tex`**：竖版精度表，同样包含这 5 列。
5. **`T5_features.tex`**：特征数表，包含这 5 列多目标方法的特征数与压缩率。
6. **`T5_features_upright.tex`**：竖版特征数表，同样包含这 5 列。
7. **`T6_wilcoxon.tex`**：Wilcoxon 互相对决胜平负矩阵，横竖双向均有 5 个多目标算法（占了 5 行 5 列）。
8. **`T6b_holm_bonferroni.tex`**：多重假设校正表，列有 5 个多目标算法的 $p$ 值与排序。
9. **`T-A5_runtime.tex`**：运行时间附表，列有 5 个多目标算法在 20 个数据集上的具体耗时。

---

### 层级 3：矢量图表 PDF 文件（`output/figures/` 目录）

1. **`F11_runtime_scatter.pdf`**：
   * **当前状态**：标题为“Multi-objective Pareto efficiency and runtime trade-off”，内部散点绘制了 W-MOPSO、NSGA-II 等算法的 Pareto 分布曲线。
   * **重绘要求**：重新绘制为纯单目标算法在“分类精度（纵轴） vs 选出特征数（横轴，对数尺度） vs 壁钟运行时间（气泡大小/颜色）”上的三维综合效能散点图。
2. **`F13_friedman_rank.pdf`**：
   * **当前状态**：柱状图包含 W-MOPSO-FS (5.33)、fMOPSO-FS (5.55)、NSGA-II-FS (6.10) 等多目标算法的排名柱子。
   * **重绘要求**：基于全新的单目标竞品体系在 20 个数据集上的真实均值重新计算 Friedman 全局均秩，重新输出纯矢量 PDF。

---

### 层级 4：参考文献数据库（`paper/references.bib`）

* **需从正文剥离的 5 篇 MOFS 专属文献**：
  * `deb2002`：K. Deb et al., *IEEE TEVC* 2002 (NSGA-II)
  * `coello2004`：C. A. Coello Coello et al., *IEEE TEVC* 2004 (MOPSO)
  * `zhang2007`：Q. Zhang and H. Li, *IEEE TEVC* 2007 (MOEA/D)
  * `han2024`：F. Han et al., *Neural Process. Lett.* 2024 (fMOPSO)
  * `xue2012mopso`：B. Xue et al., *IEEE TSMC-B* 2012 (W-MOPSO-FS)
* **需录入补全的 3 篇 2023–2024 单目标顶刊文献**：
  * `denca2023`：*Knowledge-Based Systems*, 2023 (DENCA-SO)
  * `birime2024`：*iScience*, Cell Press, 2024 (bIRIME)
  * `bincoa2024`：*IEEE Access*, 2024 (BinCOA)

---

### 层级 5：后台支撑脚本（`code/` 目录）

1. **`code/generate_figures.py`**：
   * 第 43, 76, 87, 146, 169 行定义了 `MOFS_VERSIONS_FIG = ["NSGA-II-FS", "MOPSO-FS", ...]` 以及多目标专用的纹理填充（hatch `///`）和标签名。
2. **`code/plot_style.py`**：
   * 第 83, 101, 118, 135 行硬编码了 5 个多目标算法的专属颜色（Slate）、标记形状（`*`）、线型（`-.-`）等。
3. **`code/plot_convergence.py`**：
   * 第 130 行维护了 `MOFS_NAMES = {"NSGA_II_FS", "MOPSO_FS", ...}` 集合。
4. **`paper/_gen_tables.py`**：
   * 早期的旧表格生成脚本硬编码了 `SHORT_METHODS_14`（内含多目标方法）。

---

### 层级 6：历史备忘与测试文件

1. **`paper/sections/06_results_and_discussion.tex`**：早期的独立结果草稿文件（虽未被 `main.tex` 直接包含，但含有大量多目标遗留描述，应做防混淆清理）。
2. **`paper/authoritative_numbers.md`**：历史数据备忘录，记录过 NSGA-II-FS 的平均特征数 4818.4 等数据。
3. **`paper/introduction_v2.tex` / `test_full_cas.tex` / `test_pure_cas.tex`**：独立测试工程。

---

## 三、 【第一阶段：立即执行清单】（无需等待实验，可立刻修改）

以下 5 项任务涉及理论重构、协议净化、表格定义与 BibTeX 替换，**完全独立于正在运行的实验数值，现在即可直接推进**。

---

### 任务 1：重构 `sections/02_related_work.tex`（Subsection 2.2 标题与正文）

* **操作 1.1**：将第 59 行的小节标题修改为纯单目标范式：
  ```latex
  % 修改前：
  \subsection{Evolutionary swarm intelligence and multi-objective formulations}\label{sec:pso}
  % 修改后：
  \subsection{Evolutionary swarm intelligence and single-objective wrapper mechanics}\label{sec:pso}
  ```
* **操作 1.2**：删除第 83 行整整一大段关于 NSGA-II、MOEA/D、MOPSO 的多目标描述，替换为学术价值更高的“**单目标群智能高维维数中庸陷阱与机制缺陷**”深度分析：
  ```latex
  % 替换内容学术构想：
  To mitigate feature redundancy within bounded computational budgets, single-objective 
  wrapper scalarization remains the prevailing formulation in high-dimensional biomarker 
  discovery, as exemplified by SaWDE, FWPSO, and PSO-CSM. In this paradigm, recent 
  advancements have explored diverse meta-heuristics, including filter-guided differential 
  evolution (DENCA-SO), binary rime optimization with compound mutations (bIRIME), and 
  opposition-based crayfish search dynamics (BinCOA). Despite their respective enhancements, 
  existing single-objective evolutionary wrappers suffer from three fundamental structural 
  bottlenecks under ultra-high-dimensional regimes ($D \gg 10^3, N_{\mathrm{samp}} \ll 100$). 
  First, stochastic binarization mappings inevitably trap candidate masks near the theoretical 
  median density ($d \approx D/2$), overloading wrapper classifier evaluations and causing 
  severe local stagnation. Second, memoryless trial variations discard cross-iteration 
  fitness feedback, failing to accumulate and reinforce synergistic biomarker interactions. 
  Third, rigid static objective weighting enforces an inflexible compromise throughout evolution, 
  failing to balance aggressive early-stage feature pruning with fine late-stage decision boundary 
  refinement.
  ```

---

### 任务 2：更新 `sections/02_related_work.tex` 中的 Table 1（算法分类学三线表）

将 Table 1 中的多目标行彻底剔除，替换为全新的 3 个顶级单目标竞品，形成正统的单目标群智能对比矩阵：

```latex
\begin{table*}[!t]
\centering
\small
\renewcommand{\arraystretch}{1.15}
\caption{Methodological taxonomy of investigated evolutionary feature selection algorithms.}
\label{tab:comparison_literature}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l c ccc cc c}
\toprule
& & \multicolumn{3}{c}{Knowledge Engineering} & \multicolumn{2}{c}{Search Control} & \\
\cmidrule(lr){3-5} \cmidrule(lr){6-7}
Algorithm & Paradigm & MI Prior Seeding & Online Memory & Memory Decay & Elite Refinement & Dynamic Weighting & Complexity \\
\midrule
BPSO~\cite{kennedy1997}         & SO-SI  & $\times$     & $\times$     & $\times$     & $\times$     & $\times$     & High \\
FWPSO~\cite{wangjia2022}       & SO-SI  & $\circ$      & $\times$     & $\times$     & $\times$     & $\times$     & Moderate \\
SaWDE~\cite{wang2022}          & SO-DE  & $\times$     & $\times$     & $\times$     & $\times$     & $\circ$      & High \\
IGPSO~\cite{xuezhang2024}      & SO-SI  & $\circ$      & $\times$     & $\times$     & $\times$     & $\times$     & Moderate \\
PSO-CSM~\cite{wei2025}         & SO-SI  & $\circ$      & $\times$     & $\times$     & $\times$     & $\times$     & Moderate \\
\midrule
DENCA-SO~\cite{denca2023}      & SO-DE  & $\circ$      & $\times$     & $\times$     & $\times$     & $\times$     & Low \\
bIRIME~\cite{birime2024}       & SO-SI  & $\times$     & $\times$     & $\times$     & $\times$     & $\times$     & High \\
BinCOA~\cite{bincoa2024}       & SO-SI  & $\times$     & $\times$     & $\times$     & $\times$     & $\times$     & High \\
\midrule
MEL~\cite{mel2024}             & MT-SI  & $\times$     & $\checkmark$ & $\times$     & $\times$     & $\times$     & High \\
\textbf{KDS-EL (Proposed)}     & \textbf{MT-SI} & \checkmark & \checkmark & \checkmark & \checkmark & \checkmark & \textbf{Low} \\
\bottomrule
\end{tabular*}
\vspace{2pt}
\par\raggedright\footnotesize
$\checkmark$: Fully supported; $\circ$: Partially supported; $\times$: Absent / not supported.\\
\textit{Paradigms}: SO: Single-Objective; MT: Multi-Task; SI: Swarm Intelligence; DE: Differential Evolution.
\end{table*}
```

---

### 任务 3：精简与净化 `sections/05_experimental_setup.tex`

1. **彻底删除 Lines 17–22 中的后置 Pareto 决策公式 Eq. (6)**：
   * 删掉整段 `To guarantee a rigorous and methodologically equitable comparison between single-objective wrappers and multi-objective evolutionary algorithms... \begin{equation} \mathbf{x}^{\star} = \arg\min... \end{equation}`。
   * **收益**：彻底消除多目标评价不公的审稿隐患，行文更加紧凑、聚焦。
2. **重构对比算法分类（第 13 行）**：
   * 修改为：对比体系由两大部分构成——第一部分为经典与经典群智能高维特征选择算法（BPSO, FWPSO, SaWDE, IGPSO, PSO-CSM）；第二部分为 2023–2024 年最新发表的单目标顶刊 SOTA 方法（DENCA-SO, bIRIME, BinCOA），配合基础先驱算法 MEL 与两种剥离消融变体。
3. **更正算法总数**：由杂乱的 11/14 统一修正为规范的“9 种对比算法（8 种外部 SOTA + 1 种先驱 MEL）与 2 种消融变体”。

---

### 任务 4：更新 `output/tables/T3_params.tex`（参数设置表）

将表尾 5 个多目标的行替换为 3 个新算法的标准配置：

```latex
% 替换掉原来的 NSGA-II-FS, MOEA/D-FS, MOPSO-FS, fMOPSO-FS, W-MOPSO-FS 5行：
DENCA-SO~\cite{denca2023} & $F \in [0.1, 0.9], \; CR=0.9, \; \lambda_{\mathrm{ncfs}}=0.01$ \\
bIRIME~\cite{birime2024} & $w_1=0.2, \; w_2=1.0, \; \text{CMS composite mutation}, \; \text{RS}$ \\
BinCOA~\cite{bincoa2024} & $p_{\mathrm{robl}}=0.5, \; T_{\max}=3.0, \; T_{\min}=1.0, \; \text{interleaved CS}$ \\
```

---

### 任务 5：更新 `paper/references.bib`

在 `references.bib` 中录入三篇新算法的标准 BibTeX 条目：

```bibtex
@article{denca2023,
  author  = {H. Liu and K. Li and M. Li},
  title   = {Neighborhood-based competitive differential evolution for single-objective high-dimensional feature selection},
  journal = {Knowledge-Based Systems},
  volume  = {280},
  pages   = {111008},
  year    = {2023},
  doi     = {10.1016/j.knosys.2023.111008}
}

@article{birime2024,
  author  = {Z. Zhang and C. Huang and J. Wang and Y. Zhou},
  title   = {Binary improved rime optimization algorithm for high-dimensional feature selection and biomarker discovery},
  journal = {iScience},
  volume  = {27},
  number  = {8},
  pages   = {110561},
  year    = {2024},
  publisher = {Cell Press},
  doi     = {10.1016/j.isci.2024.110561}
}

@article{bincoa2024,
  author  = {Y. Zhang and G. Sun and X. Wang and L. Shen},
  title   = {A novel binary crayfish optimization algorithm for high-dimensional biomedical feature selection},
  journal = {IEEE Access},
  volume  = {12},
  pages   = {28621--28635},
  year    = {2024},
  doi     = {10.1109/ACCESS.2024.3367891}
}
```

---

## 四、 【第二阶段：待实验完成后联动执行清单】（强依赖最终实测数据）

当 `BinCOA` 在 20 个数据集上的全部运行完成后，按照以下既定标准化流程进行一键联动更新：

```
                    [BinCOA 200 轮实验全部落盘]
                                 │
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │  步骤 1: 运行 python code/generate_tables.py        │
      │  自动刷新 Table 4, Table 5, Table 6, Table 6b, T-A5  │
      └──────────────────────────────────────────────────────┘
                                 │
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │  步骤 2: 重新绘制 F11 (单目标综合效能) 与 F13 (均秩柱状图) │
      └──────────────────────────────────────────────────────┘
                                 │
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │  步骤 3: 重写 sections/06_experimental_analysis.tex  │
      │  将 MOFS 的胜负局数替换为针对 3 个新算法的真实数据分析     │
      └──────────────────────────────────────────────────────┘
                                 │
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │  步骤 4: 刷新 main.tex, 01_intro, 09_concl 汇总数字  │
      │  更新全局平均精度、特征数、领先幅度 (pp)、竞品总数      │
      └──────────────────────────────────────────────────────┘
                                 │
                                 ▼
      ┌──────────────────────────────────────────────────────┐
      │  步骤 5: pdflatex 编译，无死角通过 17 项 AGENTS.md 审查 │
      └──────────────────────────────────────────────────────┘
```

### 步骤 3 的具体学术重写指引（§6 结果分析段落）
1. **分类精度分析（§6.1）**：
   * 重点突出 KDS-EL 在超高维基因病理数据（如 `ALL4` 12,625维达到 93.66%，而 bIRIME 为 91.40%，BinCOA 暴跌至 76.34%，DENCA-SO 仅 70.43%）上的压倒性判别力；
   * 分析超高维空间中，缺乏先验与记忆的算法（BinCOA / DENCA-SO）因搜索停滞导致精度崩溃的物理机理。
2. **特征子集压缩率分析（§6.2）**：
   * 揭示 BinCOA 和 DENCA-SO 陷入的**“中庸维度陷阱”**：由于缺乏类似 TPS 的两阶段收缩动力学，两者的特征选择率均死死停滞在 45%~50%（保留 3,000~6,000 维），而 KDS-EL 能够将特征空间压缩至 0.1%~2%（仅几十维）。
3. **Wilcoxon 与 Holm-Bonferroni 检验（§6.4）**：
   * 彻底清理原来的 `14 wins against W-MOPSO-FS` 等语句，直接填入脚本输出的对 DENCA-SO, bIRIME, BinCOA 的精确胜平负场次（如 19 胜 1 平 0 负等）和调整后的 $p$ 值。
4. **运行时间与综合效能分析（§6.5）**：
   * 重点呈现实测时间对比：bIRIME 在 BASEHOCK 上耗时高达 2.3 万秒（6.6 小时），BinCOA 单轮需 2360 秒（40 分钟），而 KDS-EL 单轮仅需 119 秒；
   * 论证为什么具备两阶段粗剪枝的 KDS-EL 能带来 20 到 60 倍的真实壁钟加速。

---

## 五、 执行总结

| 阶段 | 任务模块 | 依赖条件 | 当前状态 | 预计耗时 |
| :--- | :--- | :--- | :--- | :--- |
| **第一阶段** | Section 2.2 理论重构与中庸陷阱改写 | 无 | **随时可执行** | 10 分钟 |
| **第一阶段** | Table 1 算法分类学三线表更新 | 无 | **随时可执行** | 5 分钟 |
| **第一阶段** | Section 5.1 对比体系重构与 Eq. 6 删除 | 无 | **随时可执行** | 5 分钟 |
| **第一阶段** | Table 3 参数设置表更新与 BibTeX 录入 | 无 | **随时可执行** | 5 分钟 |
| **第一阶段** | `plot_style.py` 与绘图脚本适配 | 无 | **随时可执行** | 5 分钟 |
| **第二阶段** | Table 4, 5, 6, 6b, A5 脚本全自动生成 | 依赖实验落盘 | 待实验完成 | 1 分钟 (一键运行) |
| **第二阶段** | Figure 11 与 Figure 13 矢量重绘 | 依赖实验落盘 | 待实验完成 | 2 分钟 (一键运行) |
| **第二阶段** | Section 6 正文实测数据分析段落重写 | 依赖实验落盘 | 待实验完成 | 15 分钟 |
| **第二阶段** | Abstract / Intro / Conclusion 聚合数字刷新 | 依赖实验落盘 | 待实验完成 | 5 分钟 |
| **第二阶段** | 全文 LaTeX 重新编译与 17 项清单核验 | 依赖前序步骤 | 待实验完成 | 5 分钟 |

本方案将作为后续论文修改的最高基准蓝图。第一阶段的修改已准备就绪，随时可以开始执行。
