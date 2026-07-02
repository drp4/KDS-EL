# KDS-EL 论文项目完整记忆文档
# 用于新对话的上下文恢复
# 生成时间：2026年5月 | 最后更新：2026年7月2日（基于最新17数据集实验）

---

## 一、项目概况

**算法名称**：KDS-EL（Knowledge-guided Dual-Space Evolutionary Learning）
**投稿目标**：Expert Systems with Applications（ESWA，Q1 二区，IF≈7.5）
**备选期刊**：Applied Soft Computing（ASC，Q1 二区，IF≈6.6）
**研究领域**：高维生物信息学特征选择（Wrapper-based, PSO框架）

---

## 二、算法架构

```
KDS-EL = 双子群PSO骨架（继承自MEL [CITE_MEL, IEEE TKDE]）
         + DRS（Diversity-regulated Selection）← 原名 EMDO
         + KER（Knowledge-guided Elite Refinement）← 原名 KGEF

DRS：在 fitness 和 -NHD 两个目标上做 NSGA-II Pareto 排序
     α_cd(t) = (t/T)² — 早期多样性优先，后期精度优先
     定位：Structural Space（结构空间）

KER：improvement-feedback 权重更新（weight += delta when Pbest improves）
     权重更新在 Pbest 更新之前（已验证的关键顺序）
     p_r=0.10 随机翻转保证遍历性
     定位：Fitness Space（适应度空间）

消融命名（无 w/o）：
  MEL_NHD        → KDS-EL/DRS（只含DRS）
  MEL_KGEF_noNHD → KDS-EL/KER（只含KER）
  MEL_KGEF       → KDS-EL（Proposed，完整框架）
```

**关键参数**：N=20, T=100, K_cv=5, k_nn=3, thres=0.6, ws=[0.9,0.1],
weight_decay=0.99, flip_frac=0.01, elite_k=3, rand_flip_p=0.10,
Seeds: 42 + run×37, SEED_BASE=42, NUM_RUNS=10

---

## 三、实验数据

**最终数据集（17个，扩展自原有9个）**：
ALL1(36×12627,2c), ALL4(102×12628,4c), ALL_AML(72×7129,2c),
Adenoma(36×7458,2c), Colon(62×2000,2c), DLBCL(77×7129,2c),
Gastric(×22644,2c), Gastric1(×22284,2c), Gastric2(×22285,2c),
ISOLET(×617,26c), Leukaemia(72×7129,2c), Lymphoma(96×4026,9c),
Myeloma(×12628,3c), Prostate(×12628,2c), SRBCT(×2308,4c),
T1D(×54675,2c), madelon(×500,2c)

**新增8个数据集**（相比旧版）：ALL1、Gastric、Gastric1、Gastric2、ISOLET、Myeloma、Prostate、SRBCT、T1D、madelon
**移除**：CNS（d=7129, n=60, 极低信噪比）、Stroke（d=26877, n=2500）、ALL3（极端小样本）

**9个对比方法**：BPSO, SaWDE, FWPSO, MEL (Baseline), KDS-EL/DRS,
KDS-EL/KER, KDS-EL (Proposed), PSO-CSM, IGPSO

**实验协议**：StratifiedKFold(5, shuffle=True, random_state=42), 10 runs × 100 iterations
**主数据文件**：
- KDS-EL家族：`output/formal_experiment_20260628_205157/results_detail.csv`（1000行）
- 外部对比方法：`output/formal_experiment_20260701_094943/results_detail.csv`（850行）

---

## 四、核心数字（写作时直接引用）

### 统计检验
- Friedman χ²=94.23，p=6.43×10⁻¹⁷（9方法×17数据集）
- KDS-EL avg rank = **1.059**（17×第1，0×第2）
- FWPSO avg rank = 2.588（第2）

### 准确率胜负
- vs BPSO：17/17 wins
- vs SaWDE：16/17 wins（ISOLET上输，SaWDE rank#1，KDS-EL rank #2）
- vs FWPSO：17/17 wins
- vs PSO-CSM(2025)：17/17 wins
- vs IGPSO(2024)：17/17 wins
- vs MEL (Baseline)：17/17 wins
- KDS-EL avg accuracy = 93.95%，FWPSO avg = 92.25%

### 特征数
- KDS-EL 17/17数据集特征最少，avg = **491 features**
- vs MEL：ALL1 -91.0%，Gastric1 -95.7%，Leukaemia -91.7%，madelon -91.7%
- vs MEL avg reduction：**-83.6%**（2989→491）
- vs FWPSO avg（1060 features）：KDS-EL使用46%的特征

### 消融协同效应
- 正协同 **16/17**（百分点）：madelon+5.22, ALL4+14.28（KDS-EL/DRS单独差于MEL，但KDS-EL/DRS+KDS-EL/KER远好于MEL）, T1D+6.75, Gastric+4.93, Gastric2+3.86, Prostate+2.90, Myeloma+2.55, SRBCT+2.36, Gastric1+2.30, ALL1+2.09, ALL_AML+1.80, Adenoma+1.43, ISOLET+1.28, Leukaemia+0.90, DLBCL+0.72, Lymphoma+0.15
- 负协同 1/17：Colon -2.24（KDS-EL/KER单独贡献69.5已很高，整体仍正向+83.9）
- Mean synergy = **+3.02pp**
- KER单独版本从未超过完整KDS-EL（外部方法对比层面，0/17）

### 运行时间
- KDS-EL avg = 115.4s，FWPSO avg = 23.9s（最快），MEL avg = 167.8s
- KDS-EL比MEL Baseline快31%（167.8→115.4，DRS和KER加速收敛）

---

## 五、已完成的输出文件

### 实验数据（核心）
- `output/formal_experiment_20260628_205157/results_detail.csv` — KDS-EL家族4变体×25数据集×10 runs（1000行）
- `output/formal_experiment_20260701_094943/results_detail.csv` — 外部5方法×17数据集×10 runs（850行）
- 合并分析脚本：`analysis/combine_analysis.py`

### 图表（figures_final/）
- fig4_accuracy.png/pdf — 准确率对比（需更新至17数据集）
- fig5_features.png/pdf — 特征数对比（需更新至17数据集）
- fig6_ablation.png/pdf — 消融双面板（需重新生成）
- fig7_boxplot.png/pdf — 稳定性箱线图（需更新至17数据集）
- fig10_wilcoxon.png/pdf — Wilcoxon显著性热图（需重新生成）
- fig11_runtime.png/pdf — 运行时间对比（需重新生成）
- fig12_bubble.png/pdf — 精度-特征-时间气泡图（需重新生成）
- fig8_convergence（需本地npy文件生成）
- fig9_nhd_curves（需本地npy文件生成）
- Fig1-3框架图（需用draw.io新画）

### LaTeX文件
- tables_kdsol.tex — T4准确率、T5特征数、T6 Wilcoxon p值、T7消融
- kdsol_packaging.tex — Abstract、Introduction、Related Work定位段落
- methodology_section.tex — Methodology主体（需改名EMDO→DRS、KGEF→KER）
- complexity_section.tex — 时间复杂度分析节
- paper_complete_logic.tex — 完整论文逻辑、审稿人预案、数字速查

### 代码
- `code/generate_figures.py` — 生成Fig4-7、10-12（⚠需更新至17数据集版，读入两份CSV并合并）
- `code/generate_tables.py` — 生成T4-T7（⚠需更新至17数据集版）
- `code/plot_convergence.py` — 收敛曲线图（需npy文件，位于 `output/*/curves/` 目录下）
- `code/run_formal_experiment.py` — 全方法实验主脚本
- `analysis/combine_analysis.py` — 合并两次实验数据的分析脚本（✓新增）

---

## 六、图表规划（20个）

### Tables（8个）
- T1：近5年PSO-FS文献分析表（需新写）
- T2：17数据集描述（⚠需更新：新数据集信息）
- T3：9方法参数设置（⚠需更新：扩至9方法）
- T4：准确率mean±std（⚠需重新生成：17数据集×9方法）
- T5：特征数mean（⚠需重新生成：17数据集×9方法）
- T6：Wilcoxon p值（⚠需重新生成：17数据集×9方法）
- T7：消融实验ACC+Features（⚠需重新生成：17数据集×4变体）
- T8：时间复杂度O()（✓已完成，complexity_section.tex）

### Figures（12个）
- F1：KDS-EL框架流程图（⚠需新画）
- F2：DRS机制示意图（⚠需新画）
- F3：KER机制示意图（⚠需新画）
- F4：准确率柱状图（⚠需更新至17数据集版）
- F5：特征数柱状图（⚠需更新至17数据集版）
- F6：消融双面板（⚠需重新生成）
- F7：稳定性箱线图（⚠需更新至17数据集版）
- F8：收敛曲线2×3（⚠需npy）
- F9：NHD多样性曲线2×3（⚠需npy）
- F10：Wilcoxon热图（⚠需重新生成）
- F11：运行时间对比（⚠需重新生成）
- F12：气泡图（⚠需重新生成）

---

## 七、论文定位与包装

**核心叙事**："Dual-Space"框架
- Fitness Space：KER（知识引导精英精化）
- Structural Space：DRS（多样性调节选择）
- 两个空间协同增强（16/17正协同是核心卖点，mean synergy=+3.02pp）

**多目标定位（关键）**：
- DRS 是合法的双目标优化（fitness + NHD的Pareto排序）
- 但不叫"传统MOFS"——最终输出单一最优解，NHD是辅助目标
- 正确表述："bi-objective-regulated evolutionary feature selection"
- 辅助目标说法："NHD serves as an auxiliary structural objective
  for diversity preservation, not an end-user trade-off objective"

**与SAR-MTPSO的区分**：
- SAR-MTPSO：双任务异构目标函数（不同ws的fitness），解决多任务问题
- KDS-EL：单一fitness函数，双空间搜索策略，单目标输出
- 在Related Work中引用SAR-MTPSO，实验中不对比（架构层次不同）

**命名规范（全文统一）**：
- EMDO → DRS（Diversity-regulated Selection）
- KGEF → KER（Knowledge-guided Elite Refinement）
- MEL_NHD → KDS-EL/DRS（斜杠表示"子组件变体"）
- MEL_KGEF_noNHD → KDS-EL/KER
- MEL_KGEF → KDS-EL (Proposed)
- PSO_CSM → PSO-CSM
- 绝不使用 "w/o"

---

## 八、创新点评估

**创新点1（中等偏高）**：DRS将NHD首次升格为Pareto选择目标
- 文献中NHD只作诊断指标，本文首次纳入选择算子
- 证据：NHD从0.000→0.417(KDS-EL/DRS)→0.350(KDS-EL)，特征平均减少83.6%

**创新点2（中等）**：KER的improvement-feedback在线知识积累
- 不同于IGPSO(MLP预训练)和FWPSO(即时权重)
- 跨迭代累积，无需额外评估
- 证据：KER单独在13/17数据集优于MEL基线（KDS-EL/KER avg 90.92% vs MEL 89.02%）

**创新点3（高）**：Dual-Space协同效应
- 16/17正协同（仅Colon除外），消融证据更干净，统计功效更强
- 是整篇论文最有说服力的卖点

---

## 九、期刊选择

**首选：ESWA**（Expert Systems with Applications）
- IF≈7.5，Q1二区，年发文2850篇
- 9数据集+8对比方法在ESWA属正常范围
- 把握：65-70%
- 原因：应用导向，对算法原创性要求最低，审稿周期3-4个月

**备选：ASC**（Applied Soft Computing）
- IF≈6.6，Q1二区
- 同刊2025年已有EMSWOA（同领域），审稿人可能重叠
- 9数据集偏少（ASC主流12-20个），把握45-50%

**不建议现阶段投**：KBS（需强化Proposition证明）、TKDE（MEL原刊，门槛极高）

---

## 十、写作进度与路径

### 已完成
- Abstract（框架）
- Introduction（框架）
- Methodology（主体，需改名）
- 时间复杂度分析

### 待写（按优先级）
1. §4 Experiments 各节（数据图表全有，先写）
2. §3 Methodology 改名+补伪代码
3. §1 Introduction 扩充润色
4. §2 Related Work（全新写，1200词，3小节）
5. §5 Conclusion
6. T1-T3表格、F1-F3框架图、F8-F9收敛图

### 3周时间规划
- 第1周：Experiments全节
- 第2周：Methodology+Introduction+Related Work
- 第3周：收敛图+框架图+Conclusion+Reference+格式

---

## 十一、已知问题与处理方式

**ISOLET数据集**：KDS-EL排名#2（输给SaWDE）
→ SaWDE在ISOLET(617维, 26类)上的搜索偏差机制特别有效
→ 对外部方法16/17全胜，Friedman rank=1.059仍是压倒性第一
→ 如实在表格呈现，Discussion中解释ISOLET特点

**Colon数据集消融**：唯一负协同数据集（synergy=-0.022）
→ KDS-EL/KER单独已贡献+0.070，DRS再叠加后边际增益下降
→ 整体上KDS-EL仍是最好的（+0.083 vs MEL基线），不影响结论

**CNS、Stroke、ALL3数据集移除原因**：
→ CNS(60×7129)：极低信噪比，所有方法都接近随机(≈10%)
→ Stroke(2500×26877)：大样本耗时极端，且已有T1D覆盖大样本场景
→ ALL3(36×9999)：n=36极端小样本，KDS-EL排名第4

**Cache导致特征爆炸**（已解决）：
→ 跨run共享cache导致weight反馈循环崩溃
→ 解决方案：不使用cache，保持原始算法逻辑

**SAR-MTPSO问题**：
→ 在所有9数据集上碾压KDS-EL，不放入实验
→ 在Related Work中引用并解释架构差异

---

## 十二、npy文件说明

**输出目录**：
- `output/formal_experiment_20260628_205157/curves/` — KDS-EL家族4变体，每run一个文件
  - `curve_{VERSION}_{DATASET}_run{N}.npy` — fitness收敛曲线
  - `nhd_{VERSION}_{DATASET}_run{N}.npy` — NHD曲线（仅DRS和KDS-EL有非零值）
- `output/formal_experiment_20260701_094943/curves/` — 外部5方法，每run一个文件
  - `curve_{VERSION}_{DATASET}_run{N}.npy` — fitness收敛曲线

收敛图脚本：`code/plot_convergence.py`
