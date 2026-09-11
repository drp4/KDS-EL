# KDS-EL 论文与代码库决定性问题深度核验与证据审计报告

> **核验日期**：2026-09-11  
> **核验对象**：KDS-EL 代码库 (`code/`)、实验输出数据 (`output/`)、LaTeX 论文源码 (`paper/`) 及补充材料 (`paper/supplementary_material.tex`)  
> **核验结论**：**用户指出的所有 6 大决定性问题 100% 真实存在，无一虚构。** 均为直接影响论文科学诚信、数据真实性、算法可复现性与逻辑自洽性的阻断性缺陷（Fatal Flaws）。

---

## 目录
1. [问题一：主表与摘要中 0.9574 伪准确率（1-fitG 复合适应度指标混淆）](#问题一主表与摘要中-09574-伪准确率1-fitg-复合适应度指标混淆)
2. [问题二：50 Distinct Folds 虚假宣称、MI 标签全泄漏与缺乏外部验证](#问题二50-distinct-folds-虚假宣称mi-标签全泄漏与缺乏外部验证)
3. [问题三：论文公式描述与代码执行逻辑严重背离（W 更新与高斯噪声）](#问题三论文公式描述与代码执行逻辑严重背离w-更新与高斯噪声)
4. [问题四：实验评价预算不公平与 Wilcoxon 配对检验方法学滥用](#问题四实验评价预算不公平与-wilcoxon-配对检验方法学滥用)
5. [问题五：对比算法实现失真（IGPSO 宣称 MLP 实际为 ANOVA F-score）](#问题五对比算法实现失真igpso-宣称-mlp-实际为-anova-f-score)
6. [问题六：正文与表格数据直接打架及结论过度夸大（bIRIME、表 S9、超参敏感性）](#问题六正文与表格数据直接打架及结论过度夸大birime表-s9超参敏感性)
7. [总结与整改行动建议](#总结与整改行动建议)

---

## 问题一：主表与摘要中 0.9574 伪准确率（1-fitG 复合适应度指标混淆）

### 1. 真实性判定：【100% 真实存在，致命缺陷】
论文正文、摘要和主表 Table 4 中反复宣称的 KDS-EL 平均分类准确率 **0.9574**，根本不是真实的 3-NN 分类准确率，而是优化目标函数标量化适应度 $fitG$ 的补数（$1.0 - fitG$）。

### 2. 代码与数据铁证
- **实验明细文件证据**：  
  在 [`output/formal_experiment_final/results_detail.csv`](file:///e:/多目标优化/KDS-EL/output/formal_experiment_final/results_detail.csv) 中，对 `KDS_EL_TwoPhase` 的全部 260 条记录执行数值检测：
  $$\max |(\text{Accuracy} + fitG) - 1.0| = 0.0$$
  全部 260 行中，`Accuracy + fitG` **在浮点精度内严格精确等于 1.000000**。
- **20 个基准数据集均值复现**：  
  在 20 个标准基准数据集（200 次独立运行）上计算 `Accuracy` 均值：
  $$\text{Mean(Accuracy)} = 0.95736075 \approx 0.9574$$
  这证实论文中的 0.9574 完全来自该列。
- **数学本质推导**：  
  根据 [`code/utils.py:179-186`](file:///e:/多目标优化/KDS-EL/code/utils.py#L179-L186) 与 [`code/config.py:73`](file:///e:/多目标优化/KDS-EL/code/config.py#L73) 的定义：
  $$fitG = w_{\mathrm{err}} \cdot \mathrm{ErrorRate} + w_{\mathrm{feat}} \cdot \frac{d}{D} = 0.90 \cdot (1 - \mathrm{Acc}_{\mathrm{pure}}) + 0.10 \cdot \mathrm{SR}$$
  因此代码直接执行 `acc = 1.0 - fitG` 得到的所谓“Accuracy”实际上是：
  $$\text{Reported Accuracy} = 1 - fitG = 0.90 \cdot \mathrm{Acc}_{\mathrm{pure}} + 0.10 \cdot (1 - \mathrm{SR})$$
  这是一个**分类准确率与特征稀疏率 $(1 - \mathrm{SR})$ 的加权混合指标**！
  - 对于 KDS-EL：选择的特征极少（$d \approx 88$），$\mathrm{SR} \approx 0.01$，因此 $(1 - \mathrm{SR}) \approx 0.99$。这一项人为地将准确率向上抬升了约 $+0.099$！
  - 对于对比算法（如 MEL 或 BPSO）：选择特征数高达数千个（$\mathrm{SR} \approx 0.4 \sim 0.5$），$(1 - \mathrm{SR}) \approx 0.5 \sim 0.6$，这一项不仅没有加分，反而将它们的准确率人为下拉了 $-0.04 \sim -0.05$！
- **表格生成脚本的人工刻意拼接**：  
  在 [`code/generate_tables.py:104-112`](file:///e:/多目标优化/KDS-EL/code/generate_tables.py#L104-L112) 中：
  ```python
  # 第 104 行注释清晰写明：
  # bIRIME, BinCOA, DENCA_SO 来自 output/formal_experiment_20260905_211755 (严格仅提取这 3 个新竞品，绝不覆盖 KDS_EL_TwoPhase)
  sources = [
      (FINAL_DIR, ["KDS_EL_TwoPhase", "KDS_EL_NoPool"]),  # 来自含 1-fitG 的旧目录
      (MEL_MI_DIR, ["MEL_MI"]),
      (EXP2_DIR, ["MEL"]),
      (EXP1_DIR, ["BPSO", "FWPSO", "IGPSO", "PSO_CSM", "SaWDE"]),
      (NEW_SOTA_DIR, ["bIRIME", "BinCOA", "DENCA_SO"]),   # 来自后验 evaluate_subset 算纯精度的目录
  ]
  ```
- **重新评价后的真实纯准确率**：  
  在通过 `evaluate_subset` 真正计算折外分类准确率的实验记录 [`output/formal_experiment_20260905_211755/results_detail.csv`](file:///e:/多目标优化/KDS-EL/output/formal_experiment_20260905_211755/results_detail.csv) 中，`KDS_EL_TwoPhase` 在 20 个基准数据集上的真实平均纯分类准确率实际上为：
  $$\text{Mean}(\mathrm{Pure\_Accuracy}) = \mathbf{0.94602062 \approx 0.9460}$$
  并非 0.9574！虚高了整整 **1.14 个百分点**！

### 3. 致命影响
审稿人一旦运行代码或核对 CSV，会立即发现“Accuracy + fitG = 1”，并认定这是严重的**数据定义错误与指标操纵**。整个 Table 4、Friedman 秩、Wilcoxon 假设检验、领先优势百分点及摘要结论全部必须作废重构。

---

## 问题二：50 Distinct Folds 虚假宣称、MI 标签全泄漏与缺乏外部验证

### 1. 真实性判定：【100% 真实存在，学术规范严重缺陷】
论文声称每个数据集通过 10 次独立运行覆盖了 50 个互不相同的交叉验证折（"50 distinct folds"），但实现代码中全局写死了固定的随机种子 `random_state=42`。此外，互信息（MI）在全数据集上一次性计算完成，造成了典型的标签泄漏与模型选择偏差。

### 2. 代码与数据铁证
- **论文表述**：  
  [`paper/sections/05_experimental_setup.tex:17`](file:///e:/多目标优化/KDS-EL/paper/sections/05_experimental_setup.tex#L17)：
  > *"Conducting 10 independent runs corresponds to **50 distinct stratified cross-validation folds** per benchmark dataset, providing an adequate sample size to capture stochastic optimization variance..."*
- **代码实现**：  
  [`code/config.py:76`](file:///e:/多目标优化/KDS-EL/code/config.py#L76)：
  ```python
  "cv_random_state": 42,
  ```
  [`code/utils.py:167-170`](file:///e:/多目标优化/KDS-EL/code/utils.py#L167-L170)：
  ```python
  skf = StratifiedKFold(
      n_splits=n_splits,
      shuffle=opts["cv_shuffle"],
      random_state=opts["cv_random_state"])  # 永远传入 42
  ```
  每次优化运行（Run 1 到 10）在评估个体时，传入的 `cv_random_state` 永远是 42！这意味着 10 次运行在数据划分上**使用的是完全一模一样的一组 5 折**，根本不存在 50 个不同的折！所谓 50 distinct folds 是纯粹的虚假陈述。
- **全数据标签泄漏**：  
  [`code/algorithms/kds_el_twophase.py:54`](file:///e:/多目标优化/KDS-EL/code/algorithms/kds_el_twophase.py#L54)：
  ```python
  mi = compute_mi_scores(X, y)  # 直接使用包含所有样本的 X 和包含所有真实标签的 y！
  ```
  在特征选择和交叉验证划分开始之前，先用全部数据（包括后续作为验证折的样本）计算了互信息先验，使验证折的信息提前泄漏到了演化算法的初始化和停滞恢复机制中。
- **缺乏嵌套外部验证**：  
  论文把内部 5 折交叉验证既用作包装式优化的搜索目标，又用最终找到的最优特征子集在这一组 5 折上的成绩作为论文汇报的性能。这是一种典型的选择偏差（Selection Bias），汇报的只是内部拟合性能，无法代表对未知独立样本的泛化能力。

---

## 问题三：论文公式描述与代码执行逻辑严重背离（W 更新与高斯噪声）

### 1. 真实性判定：【100% 真实存在，算法真实性与可重复性危机】
论文正文白纸黑字写明的内容，与代码的真实执行逻辑存在直接矛盾。审稿人根本无法确定论文究竟提出并验证了哪个版本的算法。

### 2. 代码与数据铁证

#### (1) 失败候选解是否更新重要性向量 $\mathbf{W}$
- **论文正文描述**：  
  [`paper/sections/04_kds_el.tex:124`](file:///e:/多目标优化/KDS-EL/paper/sections/04_kds_el.tex#L124)：
  > *"Conversely, candidate solutions that **fail to improve fitness leave the cumulative importance vector $\mathbf{W}$ unaltered**, shielding the learned landscape from noisy perturbations."*  
  （反之，未能提升适应度的候选解保持累计重要性向量 $\mathbf{W}$ 不变，从而保护所学拓扑不受噪声扰动。）
- **代码实际执行**：  
  [`code/algorithms/kds_el_twophase.py:133-142`](file:///e:/多目标优化/KDS-EL/code/algorithms/kds_el_twophase.py#L133-L142)：
  ```python
  else:
      dec = fit_new - fitP[i]
      change = np.logical_xor(fv_o, fv_n)
      case_emerge = np.where(change & (fv_o > fv_n))[0]
      case_disappear = np.where(change & (fv_o < fv_n))[0]
      for j in case_emerge:
          weight[j] -= dec  # 失败分支在反向更新权重！
      for j in case_disappear:
          weight[j] += dec  # 失败分支在反向更新权重！
  ```
  代码在 `else` 分支（即候选解变差、未能提升时）执行了极其激进的反向惩罚，与论文所谓“leave $\mathbf{W}$ unaltered”完全相反！

#### (2) 精英翻转（KER）中加入的高斯扰动方差
- **论文正文描述**：  
  [`paper/sections/04_kds_el.tex:196`](file:///e:/多目标优化/KDS-EL/paper/sections/04_kds_el.tex#L196)：
  > *"To resolve potential ties among identical flip scores, **an infinitesimal stochastic jitter $\zeta_j \sim \mathcal{N}(0, 10^{-12})$ is added to $\sigma_j$**, ensuring consistent subset identification."*  
  （为了消除相同翻转得分之间的潜在平局，向得分中加入极微小的高斯随机抖动 $\mathcal{N}(0, 10^{-12})$。）
- **代码实际执行**：  
  [`code/utils.py:369-371`](file:///e:/多目标优化/KDS-EL/code/utils.py#L369-L371)：
  ```python
  sc = np.where(elite_bin == 0, weight, -weight)
  sc += np.random.normal(0.0, np.std(weight) + 1e-5, dim)  # 实际加的是整个权重的标准差！
  fi = np.argsort(-sc)[:flip_count]
  ```
  代码加入的不是 $10^{-12}$ 的破平小量，而是**权重向量自身的整体标准差** `np.std(weight) + 1e-5`！这种幅度的噪声与信号本身量级一致，实质上改变了被选取的特征子集，绝非仅仅为了“破除平局”。

---

## 问题四：实验评价预算不公平与 Wilcoxon 配对检验方法学滥用

### 1. 真实性判定：【100% 真实存在，方法学严重硬伤】

### 2. 代码与数据铁证

#### (1) 虚假的“同等评价预算（Identical Evaluation Budgets）”
- **论文宣称**：  
  [`paper/sections/05_experimental_setup.tex:11, L15`](file:///e:/多目标优化/KDS-EL/paper/sections/05_experimental_setup.tex#L11)：
  > *"These competitors systematically evaluate single-objective scalarized wrapper fitness under identical evaluation budgets, guaranteeing empirical parity."*
- **实际评价次数统计**：
  - **BPSO / FWPSO**：每代严格评估 $N=20$ 个个体，100 代固定执行 $20 + 100 \times 20 = 2020$ 次评估。
  - **KDS-EL**：每代除 20 次个体评估外，还要在 KER 阶段额外评估 `elite_k=3` 个变异解（见 [`kds_el_twophase.py:146-150`](file:///e:/多目标优化/KDS-EL/code/algorithms/kds_el_twophase.py#L146-L150)），且每当停滞触发时还要重新评估 10 个重启个体（见 [`kds_el_twophase.py:167-170`](file:///e:/多目标优化/KDS-EL/code/algorithms/kds_el_twophase.py#L167-L170)）。总评估次数达 $2320 \sim 2500+$ 次。
  - **bIRIME**：在 [`birime.py:119, 140-190`](file:///e:/多目标优化/KDS-EL/code/algorithms/birime.py#L119) 中，每个粒子除基础候选评估外，在 CMS 策略中还会额外评估最多 3 个突变体，每代最多评估 80 次，总评估次数高达 $8000+$ 次！
- **结论**：各算法评估预算相差数倍，耗时差异（如 KDS-EL 51.3s vs bIRIME 326.2s 或 FWPSO 175.0s）很大程度上是因为 bIRIME 执行了 4 倍以上的评价，论文却把时间加速完全归功于“KDS-EL 的特征压缩”，这是不严谨的归因谬误。

#### (2) 无共同随机种子的非配对样本被强行做配对 Wilcoxon 检验
- **代码实现**：  
  [`code/generate_tables.py:461-469`](file:///e:/多目标优化/KDS-EL/code/generate_tables.py#L461-L469)：
  ```python
  for ds in datasets:
      a = runs_dict.get((v1, ds), np.array([]))  # 方法1的10次运行
      b = runs_dict.get((v2, ds), np.array([]))  # 方法2的10次运行
      if len(a) > 0 and len(b) > 0:
          p = sp_stats.wilcoxon(a, b).pvalue     # 强行调用配对符号秩检验！
  ```
- **统计学违规**：  
  在 [`code/run_formal_experiment.py:342`](file:///e:/多目标优化/KDS-EL/code/run_formal_experiment.py#L342) 中已明确指出，各算法运行并不固定随机种子（RNG 自然随机），且不同算法来自相差数月的不同历史批次。把方法 A 的第 $k$ 次运行与方法 B 的第 $k$ 次运行一一绑定进行配对 Wilcoxon 检验，违背了“配对样本必须具有共同控制随机环境”的统计学前提，属于典型的统计方法误用。

---

## 问题五：对比算法实现失真（IGPSO 宣称 MLP 实际为 ANOVA F-score）

### 1. 真实性判定：【100% 真实存在，文献对比不实】

### 2. 代码与数据铁证
- **论文中的描述**：  
  在文本检索记录与草稿说明（如 `paper/main_raw.txt:207` 及 `parens_audit.txt:74`）中：
  > *"multi-layer perceptron-guided PSO (IGPSO)~\cite{xuezhang2024}"* / *"IGPSO [24], which estimates relevance via a multi-layer [perceptron]..."*
- **代码实际实现**：  
  [`code/algorithms/igpso.py:8-11, 24-32`](file:///e:/多目标优化/KDS-EL/code/algorithms/igpso.py#L8-L11)：
  ```python
  # 重要性 = max(0, f_classif(真实标签) − f_classif(置乱标签))
  F1, _ = f_classif(X, y)
  F2, _ = f_classif(X, y_neg)
  imp = np.maximum(0.0, F1 - F2)
  ```
  代码中用的是 `sklearn.feature_selection.f_classif`（即单因素方差分析 ANOVA F-检验），通过计算“真实标签的 F 统计量”减去“置乱标签的 F 统计量”作为特征重要性，**整个文件没有任何一层神经网络或 MLP 代码**！
- **后果**：论文把一个基于方差分析特征过滤的简化实现，当作顶刊发表的“基于多层感知机引导的 IGPSO”来汇报，审稿人一旦核验算法来源，便构成学术不诚信。

---

## 问题六：正文与表格数据直接打架及结论过度夸大（bIRIME、表 S9、超参敏感性）

### 1. 真实性判定：【100% 真实存在，严重质控疏漏】

### 2. 代码与数据铁证

#### (1) bIRIME 正文数据与表格数据不一致
- **正文声称**：  
  [`paper/sections/06_experimental_analysis.tex:13`](file:///e:/多目标优化/KDS-EL/paper/sections/06_experimental_analysis.tex#L13)：
  > *"retaining an average of **424.8** features across the benchmark suite... incurring a steep wall-clock runtime penalty averaging **375.2** seconds..."*
- **实际数据**：  
  在 [`output/formal_experiment_20260905_211755/results_detail.csv`](file:///e:/多目标优化/KDS-EL/output/formal_experiment_20260905_211755/results_detail.csv) 及由其生成的表格 Table 5 和 Table 8 中：
  - bIRIME 真实平均特征数为 **407.74**（表格显示 407.7，正文却错写成 424.8）；
  - bIRIME 真实平均运行时间为 **326.18 s**（表格显示 326.2，正文却错写成 375.2 s）。
  正文数据与同页表格数据赫然矛盾！

#### (2) 跨分类器泛化分析（表 S9）直接打脸正文论断
- **正文声称**：  
  [`paper/sections/06_experimental_analysis.tex:127`](file:///e:/多目标优化/KDS-EL/paper/sections/06_experimental_analysis.tex#L127)：
  > *"As documented in Supplementary Table S9, compact subsets deliver **substantial classification gains across all architectures**..."*  
  [`paper/supplementary_material.tex:173`](file:///e:/多目标优化/KDS-EL/paper/supplementary_material.tex#L173)：
  > *"Across all three datasets, the compact subsets achieve substantial performance gains over full-dimensional inputs..."*
- **补充表 S9 真实数据**：  
  查看 [`output/tables/T_supp_cross_classifier.tex:12-13`](file:///e:/多目标优化/KDS-EL/output/tables/T_supp_cross_classifier.tex#L12-L13)：
  ```latex
  \textit{Colon} & Full ($D = 2{,}000$) & 79.23 $\pm$ 7.68 & 85.51 $\pm$ 6.13 & 85.38 $\pm$ 6.33 \\
                 & KDS-EL ($d = 14$)   & \textbf{88.59 $\pm$ 6.80} & 80.51 $\pm$ 4.53 & 82.18 $\pm$ 10.39 \\
  ```
  在 Colon 数据集上：
  - **SVM (RBF)**：全特征准确率 85.51%，用 KDS-EL 选出的特征后**暴跌至 80.51%**（下降 -5.00 pp）；
  - **Random Forest**：全特征准确率 85.38%，用 KDS-EL 选出的特征后**下降至 82.18%**（下降 -3.20 pp）。
  正文声称“在所有架构上均获得大幅提升”，然而补充材料表格中清清楚楚记录着：3 个分类器中有 2 个发生严重性能退化！

#### (3) 仅凭 4 个数据集断言通用超参数鲁棒性
- [`paper/sections/08_parameter_sensitivity.tex:3, 32`](file:///e:/多目标优化/KDS-EL/paper/sections/08_parameter_sensitivity.tex#L3) 中，仅在 4 个数据集上做了 OFAT 单变量调节，且固定了其余所有参数，便断言算法拥有即插即用（plug-and-play）鲁棒性、对任何未知问题均无需调参。这属于典型的过度外推。

---

## 总结与整改行动建议

上述 6 类问题**完全属实、证据链完整闭环**。它们直接触碰了顶级期刊同行评阅的底线。

### 核心整改原则
1. **全面回归真实验证**：彻底废弃旧的 `1 - fitG` 伪数据源，统一以纯分类准确率（0.9460）和真实特征数重新生成 Table 4、Table 5、Friedman 秩、Wilcoxon 检验与 Holm 校正结果。
2. **论文-代码严格逐行核准**：
   - 决定 W 更新机制：统一选择论文版本（失败分支不更新 W）或代码版本（失败分支减权），并保持论文和代码 100% 同步。
   - 修正 KER 高斯扰动说明或代码实现：统一扰动幅度定义。
3. **修复数据泄漏与实验协议表述**：
   - 将 50 distinct folds 的不实表述修正为严谨的“在固定的分层 5 折交叉验证上执行 10 次独立随机优化”。
   - 诚实披露 MI 与内部评价协议的性质，明确其为包装式优化的搜索性能，并客观讨论外层泛化验证的边界。
4. **统一统计检验方法**：逐数据集比较改用独立样本检验（如 Mann-Whitney U 检验），多数据集总体比较使用以数据集均值为单位的 Wilcoxon 检验。
5. **严审文献与竞品实现**：如实描述 IGPSO 的具体实现方式（基于 ANOVA F 统计量的两阶段引导），避免在正文中张冠李戴成多层感知机（MLP）。
6. **消除文本与表格的数值冲突**：严格核准 bIRIME 的特征数和运行时间，如实客观报道 Colon 数据集在 SVM 和 RF 上的表现，摒弃绝对化的过度宣称。
