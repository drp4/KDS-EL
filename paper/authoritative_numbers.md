# KDS-EL 论文权威数字（20-DS 统一口径）

> 本文件是论文起草的唯一数字来源。所有数字均基于 **20 个共同数据集**（与主对比表 T4-T6 一致）从原始 results_detail.csv 重算。
> 生成日期：2026-08-01
> 严禁在论文中混用 25-DS/26-DS 数字（0.9442/0.9334/107 等为过时口径）。

## 一、14 方法排名表（20-DS 均值）

| Rank | Method | Acc | Feat | 类别 |
|---|---|---|---|---|
| **1** | **KDS-EL** | **0.9574** | **87.8** | 本文方法 |
| 2 | KDS-EL_KER (NoPool) | 0.9488 | 121.7 | 消融基线 |
| 3 | MEL+MI | 0.9325 | 290.5 | 改进基线 |
| 4 | FWPSO | 0.9177 | 1068.9 | 单目标 SOTA |
| 5 | W-MOPSO-FS | 0.9132 | 2960.0 | 多目标 MOFS |
| 6 | fMOPSO-FS | 0.9110 | 3006.8 | 多目标 MOFS |
| 7 | NSGA-II-FS | 0.9064 | 4818.4 | 多目标 MOFS |
| 8 | MOEA-D-FS | 0.9042 | 4936.6 | 多目标 MOFS |
| 9 | PSO-CSM | 0.9021 | 1559.4 | 单目标 SOTA |
| 10 | MOPSO-FS | 0.9009 | 5263.3 | 多目标 MOFS |
| 11 | SaWDE | 0.8944 | 3521.1 | 单目标 SOTA |
| 12 | MEL | 0.8868 | 2722.2 | 原始基线 |
| 13 | IGPSO | 0.8839 | 2538.2 | 单目标 SOTA |
| 14 | BPSO | 0.8698 | 5296.5 | 单目标 SOTA |

## 二、核心论断（论文摘要/引言/结论使用）

- KDS-EL 排名第 1，领先定长第二名 (KDS-EL_KER) **+0.86pp**
- 领先最强单目标 SOTA (FWPSO) **+3.97pp**
- 领先最强 MOFS (W-MOPSO-FS) **+4.42pp**
- 平均特征数 **87.8**（选择率 ~2-3%），vs MEL 2722 减少 **96.8%**
- vs 基线 MEL 精度 **+7.06pp**
- 运行时间 **51.3s**（14 方法中第 2，仅慢于 FWPSO 49.7s）
- vs 原始 MEL (175.0s) **3.4× 加速**
- Wilcoxon：KDS-EL **20/20** 显著优于 MEL，19/20 优于 MEL+MI
- Holm-Bonferroni：对全部 13 个对比方法显著（p<1e-15 ~ 1.02e-14）

## 三、消融表（20-DS）

| Variant | Mean_Acc | Mean_Feat | Acc_Δ_vs_MEL | Feat_Δ_vs_MEL |
|---|---|---|---|---|
| MEL | 0.8868 | 2722.2 | — | — |
| MEL+MI | 0.9325 | 290.5 | +4.58pp | +2432 |
| KDS-EL_KER | 0.9488 | 121.7 | +6.20pp | +2601 |
| **KDS-EL** | **0.9574** | **87.8** | **+7.06pp** | **+2634** |

### 逐组件贡献（add-in-sequence）
- MI+Reinit (MEL→MEL+MI)：**+4.58pp**，特征 2722→291
- KER+原地更新 (MEL+MI→KDS-EL_KER)：**+1.63pp**，特征 291→122
- 两阶段调度 (KDS-EL_KER→KDS-EL)：**+0.86pp**，特征 122→88，时间 54.2→51.3s（-5.4%）

### 两阶段 vs 无两阶段（同批直接对比）
- KDS-EL_KER (NoPool) vs KDS-EL (TwoPhase)：+0.86pp，特征 122→88（-28%），时间 54.2→51.3s
- 逐数据集：以 Section 7 表为准（20-DS），KDS-EL 在绝大多数数据集不劣于 NoPool

### 补充：全量 25-DS 鲁棒性验证（正式实验 6，`formal_experiment_final/`）— 已停用
> ⚠️ **2026-08-01 用户决策：论文改为严格 20-DS only，此 25-DS 补充句已从 §7.3 正文删除。** 以下历史数字仅供内部参考，禁止再写入论文。
- TwoPhase vs NoPool，全部 26 数据集运行、剔除退化集 CNS 后 25 集：**+1.07pp**，**22/25 胜**（输 3 个：Adenoma≈平、ISOLET、RELATHE），特征 **-45.6**（152.8→107.1），时间 **-3.6s**（64.1→60.5）
- 若未来再次启用，仅允许原批准写法："On the full 25-dataset suite where both variants have complete results, KDS-EL improves accuracy by a further +1.07pp over its no-scheduling counterpart (22/25 wins) while removing 46 features on average and reducing runtime by 3.6s."
- ⚠️ 即使启用也只作为"清晰标注的鲁棒性验证"，禁止给出该集合上的聚合名次/0.9442 作为全局性能宣称；全局性能一律用 20-DS（0.9574/88）

## 四、统计显著性（20-DS）

- 两两 Wilcoxon（Section 5）：KDS-EL vs MEL 20/20；vs MEL+MI 19/20；vs FWPSO 19/20
- Holm-Bonferroni（Section 6）：13 个对比方法全部拒绝 H0，Mean_ΔAcc 全部为正值

## 五、天花板效应数据集（8 个，Acc ≥ 0.998）

ALL1, ALL_AML, Adenoma, DLBCL, Gastric2, Leukaemia, Lymphoma, SRBCT
- 精度差 < 0.002（仅 1~2 个样本），以特征数区分方法优劣
- KDS-EL 在这些数据集选 39~83 个特征，竞争对手数百至数千

## 六、运行时间（20-DS）

| Method | Avg Time (s) | Rank |
|---|---|---|
| FWPSO | 49.7 | 1 |
| **KDS-EL** | **51.3** | **2** |
| KDS-EL/NoPool | 54.2 | 3 |
| MEL+MI | 57.6 | 4 |
| W-MOPSO-FS | 110.4 | 5 |
| SaWDE | 110.5 | 6 |
| PSO-CSM | 122.5 | 7 |
| fMOPSO-FS | 124.9 | 8 |
| NSGA-II-FS | 135.9 | 9 |
| IGPSO | 136.4 | 10 |
| MOEA-D-FS | 138.5 | 11 |
| MOPSO-FS | 142.8 | 12 |
| BPSO | 146.2 | 13 |
| MEL | 175.0 | 14 |

## 七、参数敏感性（4 代表数据集均值）

5 参数（WeightDecay / PhaseSplit / flip_frac / MI_init_ratio / elite_k）波动均 ≤ ±1.5pp。MI_init_ratio 最敏感（关闭降 1.2pp），flip_frac 次之（极端值降 1.3pp）。稳定区间与最优值见 Section 11 表。

## 八、数据集构成（20-DS）

15 个生物医学基因表达（ALL1/ALL4/ALL_AML/Adenoma/Colon/DLBCL/Gastric/Gastric1/Gastric2/Leukaemia/Lymphoma/Myeloma/Prostate/SRBCT/T1D），5 个其他（BASEHOCK/COIL20/ISOLET/madelon/PCMAC）。
维度 500 (madelon) ~ 54675 (T1D)，样本 36 (Adenoma) ~ 2600 (madelon)。

## 九、论文中禁止出现的过时数字

| 过时数字 | 来源 | 正确数字 |
|---|---|---|
| 0.9442 | 25-DS 均值 | **0.9574** |
| 107 特征 | 25-DS | **87.8** |
| +1.08pp (vs #2) | 25-DS | **+0.86pp** |
| +2.65pp (vs FWPSO) | 25-DS | **+3.97pp** |
| +3.10pp (vs W-MOPSO) | 25-DS | **+4.42pp** |
| +3.89pp (MI) | 25-DS | **+4.58pp** |
| +1.42pp (KER) | 25-DS | **+1.63pp** |
| +1.07pp (TwoPhase) | 25-DS | **+0.86pp** |
| +6.38pp (总) | 25-DS | **+7.06pp** |
| MEL rank #13 | 25-DS | **#12** |
| KDS-EL_NoPool 0.9334 | 25-DS | **0.9488** |
| MEL+MI 0.9192 | 25-DS | **0.9325** |
