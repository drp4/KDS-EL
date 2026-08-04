# KDS-EL 论文摘要（双语文稿）

> 目标期刊 Applied Soft Computing（Elsevier，纯英文期刊）。主稿使用下方英文摘要（160 词 / 约 1370 字符，与四篇参考论文摘要长度对齐；全文仅 1 个括号缩写 KDS-EL）。中文版仅作作者参考/中文论文复用，不进入英文主稿。

## 英文摘要（用于论文 main.tex）

Feature selection in high-dimensional data remains a central challenge for evolutionary computation. Particle swarm optimization suffers from three structural deficiencies: random initialization wastes budget in sparse spaces, uniform mutation discards cross-iteration feature-importance signals, and fixed objective weights misalign with search phases. To address them, we propose KDS-EL (Knowledge-Guided Dual-Phase Swarm Evolutionary Learning), a closed-loop knowledge-guided evolutionary method. First, to overcome cold-start inefficiency, we propose mutual-information-guided initialization with adaptive re-initialization, injecting prior knowledge and restarting stagnated individuals. Second, to exploit the discarded cross-iteration feature-importance signals, we propose a knowledge-guided elite refinement strategy that accumulates feature-importance knowledge and flips elites toward effective features. Third, to align objective weights with search phases, we propose two-phase weight scheduling with aggressive early compression and late accuracy refinement. On 20 high-dimensional benchmarks, KDS-EL ranks first with 0.9574 mean accuracy and 87.8 selected features, outperforming the strongest single- and multi-objective competitors by +3.97 and +4.42 percentage points; Wilcoxon and Holm--Bonferroni tests confirm significance over all 13 competitors.

## 中文摘要（仅供作者参考）

高维特征选择对进化计算构成持续挑战。粒子群优化存在三个结构性缺陷：随机初始化在稀疏空间中浪费搜索预算、均匀变异丢弃跨代际特征重要性信号、固定目标权重与搜索阶段错位。为此，本文提出 KDS-EL（Knowledge-Guided Dual-Phase Swarm Evolutionary Learning），一种闭环知识引导进化学习方法。首先，为克服冷启动低效，提出互信息引导初始化与自适应再初始化，注入先验知识并重启停滞个体。其次，为利用被均匀变异丢弃的跨代际特征重要性信号，提出知识引导精英精化策略，累积特征重要性知识并将精英解向有效特征翻转。第三，为使目标权重与搜索阶段对齐，提出两阶段权重调度：前期激进压缩、后期精细调精度。在 20 个高维基准数据集上，KDS-EL 以 0.9574 平均精度与 87.8 个选中特征排名第一，分别领先最强单目标与多目标方法 3.97 与 4.42 个百分点；Wilcoxon 与 Holm-Bonferroni 检验确认其对全部 13 个对比方法显著。
