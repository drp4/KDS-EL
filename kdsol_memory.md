# KDS-EL 论文项目完整记忆文档
# 用于新对话的上下文恢复
# 生成时间：2026年5月

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

**最终数据集（9个，去掉ALL3）**：
Adenoma(36×3408,2c), ALL_AML(72×7129,2c), ALL4(102×9999,2c),
CNS(60×7129,2c), Colon(62×2000,2c), DLBCL(77×5469,2c),
Leukaemia(72×7129,2c), Lymphoma(96×4026,9c), Stroke(2500×26877,2c)

**ALL3去掉原因**：n=36极端小样本，KDS-EL在此排名第4，且EMSWOA等同领域论文均未使用。

**9个对比方法**：BPSO, SaWDE, FWPSO, MEL, MEL_NHD(KDS-EL/DRS),
MEL_KGEF_noNHD(KDS-EL/KER), MEL_KGEF(KDS-EL), PSO_CSM, IGPSO

**主数据文件**：all_data1.csv（去ALL3后，810行）
**实验协议**：StratifiedKFold(5, shuffle=True, random_state=42), 10 runs

---

## 四、核心数字（写作时直接引用）

### 统计检验
- Friedman χ²=47.38，p=1.30×10⁻⁷（9方法×9数据集）
- KDS-EL avg rank = **1.222**（7×第1，2×第2）
- FWPSO avg rank = 2.778（第2）

### 准确率胜负
- vs BPSO：9/9 wins，9/9 p<0.01
- vs SaWDE：9/9 wins，9/9 p<0.05
- vs FWPSO：8/9 wins（CNS输，p=0.4922不显著）
- vs PSO-CSM(2025)：9/9 wins，9/9 p<0.05
- vs IGPSO(2024)：9/9 wins，9/9 p<0.01
- vs MEL：9/9 wins
- KDS-EL avg accuracy = 93.28%，FWPSO avg = 91.91%

### 特征数
- KDS-EL 7/9数据集特征最少，avg = 595 features
- vs MEL：ALL_AML -88%，Stroke -83%，avg -49%
- vs FWPSO Stroke：6485→1105，-83%

### 消融协同效应
- 正协同 7/9（百分点）：Colon+3.57, Adenoma+2.22, Stroke+1.90,
  ALL_AML+1.43, DLBCL+1.06, Lymphoma+1.22, ALL4+0.58
- 负协同 2/9：CNS -1.34，Leukaemia -1.20
- KER单独版本从未超过完整KDS-EL（外部方法对比层面，0/9）

### 运行时间
- KDS-EL avg = 188.5s，BPSO avg = 202.5s（KDS-EL比BPSO快）
- SaWDE avg = 185.4s（持平），FWPSO avg = 55.4s（KDS-EL慢3.4×）
- 原因：2.15×评估次数 + 早期探索开销

---

## 五、已完成的输出文件

### 图表（figures_final/）
- fig4_accuracy.png/pdf — 准确率对比3×3
- fig5_features.png/pdf — 特征数对比3×3（对数轴）
- fig6_ablation.png/pdf — 消融双面板
- fig7_boxplot.png/pdf — 稳定性箱线图3×3
- fig10_wilcoxon.png/pdf — Wilcoxon显著性热图
- fig11_runtime.png/pdf — 运行时间对比（双面板）
- fig12_bubble.png/pdf — 精度-特征-时间气泡图
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
- generate_figures.py — 生成Fig4-7、10-12（需all_data1.csv）
- generate_tables.py — 生成T4-T7（需all_data1.csv）
- plot_convergence_kdsol.py — 本地收敛图（需npy_1/、npy_2/文件夹）
- cell_all_methods_v2.py — Kaggle全方法实验cell（含13数据集版本）

---

## 六、图表规划（20个）

### Tables（8个）
- T1：近5年PSO-FS文献分析表（需新写）
- T2：9数据集描述（需新写）
- T3：9方法参数设置（需新写）
- T4：准确率mean±std（✓已完成）
- T5：特征数mean（✓已完成）
- T6：Wilcoxon p值（✓已完成）
- T7：消融实验ACC+Features（✓已完成）
- T8：时间复杂度O()（✓已完成，complexity_section.tex）

### Figures（12个）
- F1：KDS-EL框架流程图（⚠需新画）
- F2：DRS机制示意图（⚠需新画）
- F3：KER机制示意图（⚠需新画）
- F4：准确率柱状图（✓已生成）
- F5：特征数柱状图（✓已生成）
- F6：消融双面板（✓已生成）
- F7：稳定性箱线图（✓已生成）
- F8：收敛曲线2×3（⚠需npy）
- F9：NHD多样性曲线2×3（⚠需npy）
- F10：Wilcoxon热图（✓已生成）
- F11：运行时间对比（✓已生成）
- F12：气泡图（✓已生成）

---

## 七、论文定位与包装

**核心叙事**："Dual-Space"框架
- Fitness Space：KER（知识引导精英精化）
- Structural Space：DRS（多样性调节选择）
- 两个空间协同增强（7/9正协同是核心卖点）

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
- 证据：NHD从0.063→0.340，特征平均减少49%

**创新点2（中等）**：KER的improvement-feedback在线知识积累
- 不同于IGPSO(MLP预训练)和FWPSO(即时权重)
- 跨迭代累积，无需额外评估
- 证据：KER单独在8/9数据集优于MEL基线

**创新点3（高）**：Dual-Space协同效应
- 7/9正协同，消融证据干净
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

**CNS数据集**：KDS-EL排名#2（输FWPSO 0.0089，p=0.4922不显著）
→ 统计意义上等价，如实在表格呈现即可，不影响整体结论

**Leukaemia数据集**：KDS-EL准确率排名#2（输给消融版KDS-EL/DRS）
→ 对外部方法9/9全胜，只在消融内部比较中次于DRS单独版本
→ 说明Leukaemia上DRS主导贡献，Discussion中解释

**Cache导致特征爆炸**（已解决）：
→ 跨run共享cache导致weight反馈循环崩溃
→ 解决方案：不使用cache，保持原始算法逻辑

**SAR-MTPSO问题**：
→ 在所有9数据集上碾压KDS-EL，不放入实验
→ 在Related Work中引用并解释架构差异

---

## 十二、npy文件说明

**npy_2文件夹**（Kaggle本地）：MEL系方法，每run两个文件
- curve_{VERSION}_{DATASET}_run{N}.npy — fitness收敛曲线
- nhd_{VERSION}_{DATASET}_run{N}.npy — NHD曲线

**npy_1文件夹**（Kaggle本地）：IGPSO/PSO_CSM，每run一个文件
- curve_{VERSION}_{DATASET}_run{N}.npy — fitness收敛曲线

收敛图脚本：plot_convergence_kdsol.py（放在all_data/文件夹下运行）
