# KDS-EL 顶刊修回补充实验全景详细设计方案

**文档归属**：`review_round_1/04_detailed_supplementary_experiment_design.md`  
**对接标准**：Elsevier 顶刊（ASOC, SWEVO, ESWA, KBS）严谨同行评审规范  
**设计目标**：针对 Reviewer 1 与 Reviewer 4 合并后的核心关切，规定可复现且计算可控的补充实验方案。本文件是待实现、待验收的设计规范，不代表代码已实现或实验结果已验证。

---

## 📌 一、 补充实验全景架构与审稿意见闭环矩阵

本设计包含 **6 大相互支撑的实验套件（Experimental Suites）**，每一套件均系统响应审稿专家的特定技术关切与质询：

| 实验套件编号 | 实验套件名称 | 解决的审稿意见条目 | 核心攻坚性质与科学目的 | 初步估计运行耗时*<br>(待压力测试校准) |
| :---: | :--- | :--- | :--- | :---: |
| **套件 1** | **外层隔离嵌套式评估方案<br>（Nested Evaluation 方案 A）** | R1-1, R1-2, R1-7, R1-8<br>R4-Major 1, Minor 2, 3, 5, 7 | **【核心主攻项】**<br>彻底阻断外层测试集数据泄露；外层盲测 BAcc/F1；SVM/RF/NB/LDA 跨分类器泛化；埋点实测 KER 接受率与 P2 可行率。 | 初步估计 ~2–3 小时*<br>(多进程并行) |
| **套件 2** | **经典 Filter 过滤式对照方法对比实验** | R1-3<br>R4-Major 4 | **【对照对齐项】**<br>补齐 Top-$k$ MI, mRMR, ReliefF, LASSO (L1) 等过滤式对照方法，检验演化包装搜索相比纯特征排序的增量价值。 | 初步估计 ~15 分钟* |
| **套件 3** | **模块解耦与受控组件贡献分析** | R1-4, R1-5, R1-6<br>R4-Major 2, Minor 1 | **【机理归因项】**<br>解耦参数调度（静态 0.95/0.05、静态 0.70/0.30、反向排期、无衰减 $\gamma=1.0$）与受控对照（等人口单种群 $\mathcal{P}_1$ 架构、等预算无 KER 策略）。 | 初步估计 ~1.5 小时* |
| **套件 4** | **标签置换零假设检验<br>（Label-Permutation Test）** | R1-1<br>R4-Minor 2 | **【假设检验项】**<br>在 Colon、SRBCT 上比较完整训练流程的真实与置换标签统计量；默认固定单种子、每条件完整 5 个外层折、100 次置换。 | 待单折压力测试后估计<br>默认 1,000 次置换优化运行 |
| **套件 5** | **历史掩码离线多维指标提取** | R1-2, R1-10<br>R4-Minor 7 | **【复用项】**<br>读取已存的 bIRIME、BinCOA、DENCA_SO 掩码，免于重新演化，但仍须拟合分类器并预测，补充历史内部评估的 BAcc 与 Macro-F1。 | 无演化开销；拟合与预测耗时待测 |
| **套件 6** | **受控肿瘤微阵列 KEGG/GO 功能富集与特征稳定性** | R1-11<br>R4-Minor 6 | **【跨学科真实性项】**<br>严格限定生物芯片；建立可溯源探针映射与芯片封闭背景全集；严格可证伪假设检验 KEGG/GO 富集（FDR $q<0.05$）；客观剖析平滑肌组织异质性；以同一外层训练折内 10 次运行的 Jaccard 为主衡量随机搜索稳定性。 | 初步估计 ~30 分钟* |

> \*注：上述耗时均为基于小规模特征子集、哈希缓存命中与单层受控并发架构的**理论初步估计**。由于嵌套式评估方案（Nested Evaluation Scheme）、10 次独立随机运行、5 个外层折、5 个内层代理折与 2,000 FEs 叠加多款下游分类器时，实际计算负载与内存开销客观较大，各实验套件的**最终实际执行耗时与并行资源配置，必须严格以代表性数据集（如 Colon、T1D、BASEHOCK、COIL20）上的单折/多进程压力测试监测数据为准**，严禁在未测前断言执行窗口，从工程制度上防范资源耗尽与执行计划失控风险。

---

## 🔬 二、 套件 1 详细设计：外层测试集严格隔离、外层训练集受限先验的嵌套式评估方案（方案 A）与多维指标协同收割

### 1. 方案 A 理论定位与方法论边界 (Methodological Boundary of Scheme A)
本次补充实验采用**方案 A：外层测试集隔离、外层训练集受限先验的嵌套式评估方案**。评估对象是从外层训练数据计算 MI、初始化与搜索、选择子集直至拟合分类器的完整训练流程，而不是把内层代理分数当作最终泛化结果。

**外层测试隔离边界。** 每个外层测试折约占样本的 20%，不得参与 MI 计算、初始化、信用更新、子集搜索、超参数选择、预处理统计量拟合或最优运行挑选。全部配置及主报告口径须在查看外层结果前固定；搜索结束后只将训练折拟合好的变换与模型应用于测试折。该设计控制面向外层测试集的信息泄露，用于评估流程的样本外预测表现，**不承诺有限样本估计绝对无偏，也不等同于独立临床队列验证**。

**外层训练先验与内层代理的分工。** MI 仅在当前外层训练集上计算一次，作为该次搜索的问题级启发式先验，服务于 MII 与 AIR。内层 5 折为候选子集提供搜索代理分数；由于整个外层训练集的标签参与 MI 估计，内层验证标签也间接影响搜索先验，故内层分数不是对先验拟合完全隔离的泛化估计。分类器及需要拟合的预处理仍须在各内层训练折内拟合，内层验证折仅应用变换和预测。

**采用方案 A 的理由与适用范围。** 本轮选择在每个外层训练划分内保留一套 MI 先验及完整协同搜索流程，以便评估既定算法的训练过程。更深层的先验隔离或在内层分别搜索属于其他可设计的评估流程，不能声称它们必然破坏群体协同或无法实现；本轮不开展这些额外方案，也不将方案 A 称为唯一科学方案。

### 2. 实验协议与数据流闭环设计
* **先验知识计算边界（零外层泄露保障）**：
  * **只能且仅能在 $\mathcal{D}_{\mathrm{train\_outer}}^{(k)}$ 上计算特征与标签的互信息**：
    $$\mathbf{I}^{(k)} = \mathrm{mutual\_info\_classif}\left(\mathbf{X}_{\mathrm{train\_outer}}^{(k)}, \mathbf{y}_{\mathrm{train\_outer}}^{(k)}\right)$$
  * 严禁 $\mathcal{D}_{\mathrm{test\_outer}}^{(k)}$ 的任何样本或标签参与 $\mathbf{I}^{(k)}$ 的计算或种群初始化。
* **内层包装搜索与候选请求预算（Inner Optimization & Candidate Request Budget）**：
  在外层训练集内，使用固定内层 5 折为可行子集计算真实分类误差。对当前阶段与子群规则允许进入分类评价的候选，适应度为
  $$f(\mathbf{x}) = w_a \cdot \mathrm{Error}_{\mathrm{inner\_CV}}(\mathbf{x}) + w_f \cdot \frac{d}{D}.$$
  不可行分支沿用对应子群的约束定义；若该分支未执行分类评价，不得把占位返回值解释为真实分类误差。

  **历史协议与新增协议分开报告。** 原稿采用相同人口规模 $N=20$ 与名义代数上限 $T=100$，并非等候选请求预算。若仅作算例，初始化 20 次、100 代各 23 次请求及一次恰好 20 次的切换重评分合计为 2,340 次；该数未计 AIR，且依赖实际调用方式，不能当作历史日志实测值。本轮新增实验采用统一上限 $\mathrm{Max\_FEs}=2{,}000$，按候选适应度请求计数，而非按分类器拟合次数计数。

  **预算扣除与终止。** 初始化、常规更新、KER、AIR 以及 TPS 切换时所有实际发出的重评分请求均计入 `candidate_eval_requests`；缓存命中也计 1 次。每次请求前检查剩余额度，不能等整代结束才检查并超额。允许最后一代只执行部分事件，记录完整代数、末代事件及终止原因。静态权重配置不执行无意义的 TPS 切换重评。最终外层模型拟合与预测不占搜索额度，另行记录。

  **阶段无关缓存。** 缓存保存掩码对应的内层误差、必要预测与特征数等阶段无关结果，**不得直接返回旧阶段的标量 fitness**。每次请求按当前子群可行性规则与当前权重重新组装适应度。作用域至少绑定数据版本、外层训练索引、内层划分、预处理配置及评价器/分类器版本；置换实验还须绑定标签指纹或置换编号。默认每次优化运行独立建缓存，不通过跨算法或跨运行预热影响耗时对比。未做 CV 的不可行占位结果不能登记为真实误差缓存。

  **互斥请求计数与实际拟合计数。** 先判断是否为无需 CV 的快捷分支，其余请求再查缓存，并在命中与完整 CV 计算之间二选一。对正常完成的运行，应满足
  $$\mathrm{candidate\_eval\_requests}=\mathrm{shortcut\_eval\_requests}+\mathrm{cache\_hit\_count}+\mathrm{cv\_eval\_calls}\le 2{,}000.$$
  `inner_model_fits` 单独累计实际内层模型拟合次数；仅在每次 CV 均完整完成 5 折、无失败或提前退出时，才有
  $$\mathrm{inner\_model\_fits}=5\,\mathrm{cv\_eval\_calls}.$$
  例如 1,200 次完整 CV 对应 6,000 次内层拟合，而非 1,200 次。`outer_model_fits` 另计各下游模型及回退拟合。失败运行保留日志与已消耗预算，标为失败，不能静默丢弃或重新抽种子直至成功。缓存命中率和节省的实际拟合数均待测，不能预填经验区间。相同候选请求配额不保证相同唯一掩码数、实际模型拟合数或物理计算量，须同时报告这些差异。

  **预算进度与 TPS 调度。** 初始化 20 次请求后，以已使用请求数 $E\in[20,2000]$ 定义
  $$q=\frac{E-20}{2000-20}\in[0,1].$$
  每代开始读取 $q$；正向 TPS 在首个 $q\ge 0.70$ 的代开始前，由 $0.70/0.30$ 切换为 $0.95/0.05$，反向配置在同一边界交换权重。切换时，所有继续参与比较的 pbest、gbest 及其他保留解均须按新目标重评分，防止跨阶段比较不同标尺；实际请求照常扣预算，不能假定恰好 20 次。若额度不足以完成必要重评，记录未完成状态，不混用不同阶段分数。保存切换前的 $E,q$、重评请求数及两阶段实际请求数，承认代边界离散误差，不能把阈值 0.70 解释为恰好 70% 的物理成本。

  其他原公式中明确依赖 $t/T$ 的进度型参数也统一按 $q$ 映射，在所有比较配置中披露同一规则。这是**新增等请求预算协议的进度归一化配置**，不是原固定代数协议的逐步复现。按代施加的信用衰减 $\gamma$ 与事件触发的 AIR 保持各自定义，记录实际触发次数；不同代数产生的累计作用不能声称完全相同。

  **实际代数只由事件日志决定。** 在初始化 20 次、切换恰好重评 20 次且无 AIR 的条件算例中，Full 剩余 1,960 次请求，可完成 85 代各 23 次并余 5 次；无 KER 配置可完成 98 代各 20 次。实际切换重评、AIR 及尾部事件均可能改变该结果，不预设“实测约 85 代”。搜索终止后保存最终阶段下的最优掩码 $\mathbf{x}^{\star(k,r)}\in\{0,1\}^D$，动力学分母一律使用实际事件数。

### 3. 四级实验分级架构、重复单位与随机种子规程 (Hierarchical Replication Architecture, Units & Seeds)
为了彻底理顺实验重复单位、严防“伪重复抽样（Pseudo-Replication）”导致的统计自由度虚增，本实验建立清晰的四级层次化实验规程：

```
Level 1: 独立数据集实例级 (Dataset Level, N = 19 严格独立问题)  <--- 唯一合法的非参数统计检验单元！
   └── Level 2: 外层折划分级 (Outer Folds, K_outer = 5, seed = 42 绝对固定)
          └── Level 3: 内层代理折级 (Inner Surrogate Folds, K_inner = 5, seed = 42 绝对固定)
                 └── Level 4: 优化器随机独立运行级 (Optimizer Replication, R = 10 独立种子)
```

* **Level 1: 独立数据集实例级（Dataset Level / Independent Problem Instance）**
  * 采用去重后的受控独立基准集（**$N=19$ 严格独立数据集**，正式剔除同源重复项 `ALL_AML`，保留 `Leukaemia`）；
  * **统计学铁律（绝对底线）**：跨数据集的非参数统计检验（Friedman 秩次检验、Wilcoxon 符号秩检验、Holm--Bonferroni 逐步下调校正）的样本量 $N$ **严格且只能等于独立数据集的个数（$N=19$）**！绝对禁止将 5 个外层折（$N=95$）或 50 次运行（$N=950$）当成独立统计样本，坚决杜绝“伪重复抽样（Pseudo-Replication）”，彻底呼应并封死 Reviewer 1 Point 9 的批评。
* **Level 2: 外层折划分级（Outer Fold Level, $K_{\mathrm{outer}} = 5$）**
  * **外层划分固定与文件持久化**：采用 `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` 产生 5 个外层折（Outer Folds）：
    $$\mathcal{D} = \mathcal{D}_{\mathrm{train\_outer}}^{(k)} \cup \mathcal{D}_{\mathrm{test\_outer}}^{(k)}, \quad k \in \{1, 2, 3, 4, 5\}$$
    其中 $\mathcal{D}_{\mathrm{train\_outer}}^{(k)}$ 占 80% 样本，$\mathcal{D}_{\mathrm{test\_outer}}^{(k)}$ 占 20% 样本；
  * **划分文件持久化与跨算法共享**：外层划分索引在首次运行时统一序列化并持久化保存为独立文件：
    `output/nested_cv/splits/{dataset}_outer_splits.json`
    所有对比算法（KDS-EL、MEL、bIRIME、Filter 等）强行从该文件读取完全相同的训练折与测试折索引，保证折划分跨算法绝对共享与零偏差。
* **Level 3: 内层代理折级（Inner Fold Level, $K_{\mathrm{inner}} = 5$）**
  * **内层代理划分固定与文件持久化**：在每个外层训练集 $\mathcal{D}_{\mathrm{train\_outer}}^{(k)}$ 内部，内层 5 折交叉验证同样采用固定随机种子划分，并持久化保存至：
    `output/nested_cv/splits/{dataset}_inner_splits_fold{k}.json`
  * 5 折内层划分在整个搜索过程中保持完全静态，纯粹作为包装器候选特征子集的代理适应度评估器（Surrogate Fitness Evaluator）。
* **Level 4: 优化器随机独立运行级（Optimizer Replication Level, $R = 10$ Runs per Outer Fold）**
  * **确定性随机种子派生规程（解决历史无序随机性）**：
    * 历史正文实验（`code/run_formal_experiment.py`）遵循了原始 MEL 算法的基准设定，随机数生成器在 10 次运行间自然流动，未逐次指定确定性 seed 且未记入 CSV；
    * **待实现的固定种子规程**：每个试验四元组均记录可复现的种子，优化器种子只按运行编号从下列列表读取：
      $$\mathrm{SEEDS} = [7, 30, 1, 42, 100, 2024, 999, 1234, 555, 888]$$
      $$\mathrm{run\_seed} = \mathrm{SEEDS}[(\mathrm{run\_idx} - 1) \pmod{10}]$$
    * 在每次执行搜索前显式调用 `np.random.seed(run_seed)` 和 `random.seed(run_seed)`；
    * **运行器验收要求，而非已实现声明**：每次优化须记录 dataset、algorithm、outer_fold、run_idx 与实际 seed，保存划分及随机数生成器设置。上式仅依赖 run_idx，同一运行编号在不同数据集、折与算法间复用相同整数，不声称已为各四元组派生互不相同的随机流。相同 seed 也不意味着不同算法的随机调用逐步配对。
  * **全量计算规模精算法则**：
    * 单个数据集的优化试验总数（Trials）：$5 \text{ 外层折} \times 10 \text{ 独立运行} = 50 \text{ 次优化运行}$；
    * 19 个独立基准数据集的总优化试验总数：$19 \times 50 = 950 \text{ 次独立优化运行}$；
  * **计算开销初步估计与资源压力测试管理准则**：
    * 虽然单算法累计执行 950 次优化运行，且在小样本训练折（$N_{\mathrm{samp}} \le 100$）及特征快速压缩（如降至数十维）场景下具备掩码哈希缓存（命中缓存跳过分类器拟合）的理论优势，但在嵌套式评估方案（方案 A）架构下叠加 10 次运行、5 个外层折、5 个内层代理折以及多下游分类器盲测，整体计算负载与内存开销依然客观存在；
    * **初步估计与压力测试校准准则**：
      初步估计单算法全流程耗时为 2–3 小时（基于多进程并发），但**严禁在尚未执行真实基准测试前将其断言为“完全处于可承受范围”或“数小时内平稳完成”**。所有耗时数据均属理论初步估计，最终必须以代表性跨尺度数据集（如高维小样本的 `Colon`、`T1D` 与大样本高密度的 `BASEHOCK`、`COIL20`）上的单折/多进程压力测试（Stress Test）实测结果为准；
    * **阶段化工程调度与防失控机制**：
      正式全量挂机前，必须先在选定代表性数据集上实测记录单折平均耗时、内存峰值（RSS）与 Windows 进程冷启动开销，根据真实监测曲线动态核定全量作业的预计完成窗口与并发度配置，从工程制度上防范资源耗尽与执行计划失控风险；实验调度严格遵循单层进程级并发规范（继承 `code/run_parallel_experiment.py` 设计），强制底层线性代数库单线程化（`OMP/MKL/OPENBLAS_NUM_THREADS=1`）且模型内部 `n_jobs=1`，确保每一个工作进程稳定独占单一物理 CPU 核心。

### 4. 分层存储架构与两级指标聚合规范 (Hierarchical Storage & Two-Level Aggregation Pipeline)
* **分层存储路径规范**：
  为确保每一次运行的数据完全可追溯，脚本按“数据集—外层折—运行”的三层目录树结构保存所有原始数据：
  `output/nested_cv/{algorithm}/{dataset}/fold_{k}/run_{r}/`
  * 持久化文件结构：
    * `selected_mask.npy`：该运行挑选的最优特征子集二进制掩码；
    * `metrics.json`：包含外层 Acc、BAcc、Macro-F1、特征数、耗时、实际 seed、`candidate_eval_requests`、`shortcut_eval_requests`、`cache_hit_count`、`cv_eval_calls`、`inner_model_fits`、`outer_model_fits`、唯一掩码数、完整代数及尾部事件、TPS 切换进度、KER 实际事件与 P2 可行率；失败及回退另行标注；
    * `fold_summary.csv`：折内 10 次运行指标流水明细（显式包含 `Seed` 列）；
    * `dataset_summary.csv`：该数据集 5 个外层折聚合汇总。
* **外层指标聚合规范：全样本外拼接（Pooled OOF）为主，折级均值（Fold-Level Mean）为辅**：
  在嵌套式评估方案（方案 A）中，针对包含类别失衡与小样本的生物数据集，必须严格区分两种指标聚合范式，并明确其数理适用边界：
  
  1. **主结果基准：全样本外预测拼接指标（Pooled Out-of-Fold Metric，论文主表采纳标准）**：
     * **计算流程**：在每一次独立随机运行 $r \in \{1, \dots, 10\}$ 中，演化算法在 5 个互斥的外层折上分别产生盲测预测。将这 5 个外层测试折的样本外预测标签按照原始样本索引进行全局拼装，组合成覆盖整个数据集全部 $N_{\mathrm{samp}}$ 个样本的完整预测向量：
       $$\hat{\mathbf{y}}_{\mathrm{OOF}}^{(r)} = \bigoplus_{k=1}^5 \hat{\mathbf{y}}_{\mathrm{test}}^{(k, r)} \in \{1, \dots, C\}^{N_{\mathrm{samp}}}$$
     * **全局混淆矩阵计算**：基于全数据集真实标签 $\mathbf{y}$ 与拼接后的预测向量 $\hat{\mathbf{y}}_{\mathrm{OOF}}^{(r)}$，构建全局 $C \times C$ 混淆矩阵 $\mathbf{C}^{(r)}$，统一计算运行 $r$ 的全样本外综合指标：
       $$\mathrm{Acc}_{\mathrm{OOF}}^{(r)} = \frac{1}{N_{\mathrm{samp}}} \sum_{i=1}^{N_{\mathrm{samp}}} \mathbb{I}\left(\hat{y}_{i, \mathrm{OOF}}^{(r)} = y_i\right)$$
       $$\mathrm{BAcc}_{\mathrm{OOF}}^{(r)} = \frac{1}{C} \sum_{c=1}^C \mathrm{Sensitivity}_c\left(\mathbf{y}, \hat{\mathbf{y}}_{\mathrm{OOF}}^{(r)}\right)$$
       $$\mathrm{Macro\text{-}F1}_{\mathrm{OOF}}^{(r)} = \frac{1}{C} \sum_{c=1}^C \mathrm{F1}_c\left(\mathbf{y}, \hat{\mathbf{y}}_{\mathrm{OOF}}^{(r)}\right)$$
     * **跨 10 次运行汇总**：在获取 10 次独立随机运行的 Pooled OOF 指标 $\{\mathrm{Metric}_{\mathrm{OOF}}^{(1)}, \dots, \mathrm{Metric}_{\mathrm{OOF}}^{(10)}\}$ 后，计算最终汇报的均值与样本标准差（ddof=1）：
       $$\overline{\mathrm{Metric}}_{\mathrm{OOF}}(\mathcal{D}) = \frac{1}{10} \sum_{r=1}^{10} \mathrm{Metric}_{\mathrm{OOF}}^{(r)}, \quad \sigma(\mathcal{D}) = \sqrt{\frac{1}{10 - 1} \sum_{r=1}^{10} \left( \mathrm{Metric}_{\mathrm{OOF}}^{(r)} - \overline{\mathrm{Metric}}_{\mathrm{OOF}}(\mathcal{D}) \right)^2}$$
     * **统计量边界**：Pooled OOF 按样本拼接后计算，折级均值按折等权平均，两者不是同一统计量，尤其 Macro-F1 通常不相等。本轮预先固定 Pooled OOF 为主口径，折级均值仅作附录，不按结果高低切换。跨 10 次种子的 SD 只描述固定外层划分下优化随机性，不是总体抽样不确定性的置信区间；不声称该口径“最无偏”。

  2. **辅助对比指标：折级均值（Fold-Level Mean，作为诊断附录输出）**：
     * **计算流程**：先在每个外层折 $k$ 的测试集上独立计算该折的分类指标 $M_{k, r}$，然后对 5 个外层折计算折级算术平均值 $\bar{M}_{\mathrm{fold}}^{(r)} = \frac{1}{5} \sum_{k=1}^5 M_{k, r}$，最后再跨 10 次运行取均值与标准差；
     * **定位与保留**：脚本同时输出 Fold-Level Mean 指标作为次级参考附录，用于对比观察各折之间的划分方差波动。

* **统计假设检验样本量绝对锁死（严禁 50 个混合样本伪重复）**：
  * **坚决禁止的操作**：**绝对禁止将 5 个外层折与 10 次运行简单混合为 50 个‘独立样本’进行显著性检验！** 5 个折划分与 10 次优化器运行共享了相同的数据集底层分布，不满足统计学独立同分布（i.i.d.）假设，混同计算属于严重的伪重复抽样（Pseudo-Replication）；
  * **合规统计检验准则**：跨算法的非参数统计检验（Friedman 秩次检验、Wilcoxon 符号秩检验、Holm--Bonferroni 逐步下调校正）中，**每个算法在每个独立基准数据集上严格且只能输入单一统计观测值 $\overline{\mathrm{Metric}}_{\mathrm{OOF}}(\mathcal{D}_i)$**；
  * 去重后的 19 个数据集提供至多 19 个数据集级配对观测，不将其统称为“总自由度”。Wilcoxon 的有效配对数取决于零差值处理等规则，须记录；Friedman 的参考分布自由度由比较算法数量决定。不得用折数或运行数扩增问题实例数。

### 5. “一鱼多吃”盲测与外层泛化评估（Outer Evaluation）
利用演化算法在外层训练折上选出的最优特征子集掩码 $\mathbf{x}^{\star(k, r)} \in \{0, 1\}^D$，**仅使用外层训练集 $\mathcal{D}_{\mathrm{train\_outer}}^{(k)}$ 上对应的特征列拟合分类器模型，在独立的盲态外层测试集 $\mathcal{D}_{\mathrm{test\_outer}}^{(k)}$ 上执行一次性绝对盲测（One-Shot Blind Evaluation）**。

#### (1) 特征子集绝对一致性锁定与缺失值防御
* **特征子集 100% 相同**：所有下游分类器（3-NN、SVM、RF、Naive Bayes、Shrinkage LDA）在给定折 $k$ 与运行 $r$ 上评估时，**强制且只能传入完全相同的活跃特征子集索引** $\mathcal{S}^{\star(k, r)} = \{j \mid x_j^{\star(k, r)} = 1\}$，严禁不同分类器使用不同特征子集，确保子集迁移性（Generalization Transferability）对比的绝对公正；
* **数据稠密性断言与缺失值防御**：经代码审计，19 个独立基准数据集均为全观测数值矩阵，无缺失值。评估脚本内嵌严格防御断言：`assert not np.isnan(X).any() and not np.isinf(X).any()`。若在未来扩展数据集中出现缺失值，强制使用在训练折拟合的 `SimpleImputer(strategy='median')` 进行流水线填补，严禁测试集参与填补统计量计算。

#### (2) 多维度评估指标体系（彻底解决 R1-2 与 R4-Minor 7）
在测试折样本量为 $N_{\mathrm{test}}$、类别数为 $C$ 的测试集上，同时计算并记录以下三组核心指标：
* **标准分类准确率**：$\mathrm{Acc} = \frac{1}{N_{\mathrm{test}}} \sum_{i=1}^{N_{\mathrm{test}}} \mathbb{I}(\hat{y}_i = y_i)$；
* **平衡准确率（Balanced Accuracy，抵御类别失衡偏倚）**：
  $$\mathrm{BAcc} = \frac{1}{C} \sum_{c=1}^C \frac{\mathrm{TP}_c}{\mathrm{TP}_c + \mathrm{FN}_c} = \frac{1}{C} \sum_{c=1}^C \mathrm{Sensitivity}_c$$
* **宏平均 F1 指数（Macro-Averaged F1-Score）**：
  $$\mathrm{Macro\text{-}F1} = \frac{1}{C} \sum_{c=1}^C \frac{2 \cdot \mathrm{Precision}_c \cdot \mathrm{Recall}_c}{\mathrm{Precision}_c + \mathrm{Recall}_c}$$

#### (3) 跨分类器无泄露标准化 Pipeline 与超参数锁定规程（彻底解决 R1-1 与 R4-Minor 5）
各基准数据集的特征量纲动态范围差异极其显著（例如 `Adenoma` 特征值跨越 $-5{,}655 \sim +6{,}628$，`madelon` 为 $0 \sim 999$，`BASEHOCK` 词频为 $0 \sim 113$，而 `COIL20` 归一化为 $0 \sim 1$）。对于基于距离与几何间隔的分类器（尤其是 RBF-SVM），若不进行折内特征标准化，核距离将发生严重的数值溢出或下溢导致模型崩溃。为此，所有跨分类器评测均通过严密的 Pipeline 封装，严格执行**“训练折内部拟合标准化统计量、验证/盲测折仅应用变换”**原则：

1. **分类器 1：Support Vector Machine (SVM) 严格流水线**
   * **量纲敏感性防御**：采用 `sklearn.pipeline.Pipeline` 将 `StandardScaler` 与 `SVC` 紧密封装：
     ```python
     from sklearn.pipeline import Pipeline
     from sklearn.preprocessing import StandardScaler
     from sklearn.svm import SVC

     svm_pipeline = Pipeline([
         ('scaler', StandardScaler()),
         ('svm', SVC(
             kernel='rbf',
             C=1.0,
             gamma='scale',           # gamma = 1 / (d_selected * Var(X))
             class_weight='balanced',  # 针对失衡数据集自适应加权类别惩罚
             probability=False,
             random_state=42
         ))
     ])
     # 严格执行规则：
     svm_pipeline.fit(X_train[:, active_features], y_train)
     y_pred_svm = svm_pipeline.predict(X_test[:, active_features])
     ```
   * **零泄露硬红线**：`StandardScaler` 的均值 $\boldsymbol{\mu}_{\mathrm{train}}$ 与标准差 $\boldsymbol{\sigma}_{\mathrm{train}}$ 只能由训练折样本计算，测试折仅调用 `transform()`，杜绝任何未来量纲泄露。
2. **分类器 2：Random Forest (RF) 严格超参数与资源隔离**
   * **树模型尺度不变性**：基于贪婪分裂阈值的决策树集成对单调特征缩放具有天然不变性（Scale-Invariant），无需额外执行 `StandardScaler`；
   * **严格参数与线程隔离**：
     ```python
     from sklearn.ensemble import RandomForestClassifier

     rf_clf = RandomForestClassifier(
         n_estimators=100,
         criterion='gini',
         max_features='sqrt',
         class_weight='balanced',     # 类别失衡自适应加权
         random_state=42,             # 固化树构建随机性，保证跨实验绝对可复现
         n_jobs=1                     # 严格单线程运行！
     )
     rf_clf.fit(X_train[:, active_features], y_train)
     y_pred_rf = rf_clf.predict(X_test[:, active_features])
     ```
   * **为何强制 `n_jobs=1` 与单层并发原则**：实验调度系统严格遵循“单层并行”原则。既然外层已采用受控进程级并发，底层分类器（包括 RF 与 SVM）必须严格锁死 `n_jobs=1`，且子进程强制限制底层线性代数库单线程（`OMP/MKL/OPENBLAS_NUM_THREADS=1`），彻底杜绝由于“外层折并发 × 算法运行并发 × RF 树内部多线程 × BLAS 矩阵并行”多层嵌套引发的灾难性 CPU 线程过度订阅（Thread Oversubscription）、上下文频繁颠簸与系统假死。
3. **分类器 3：3-NN（包装器原生目标分类器）**
   * 作为演化包装器搜索的原生驱动分类器，采用欧氏距离多数表决（`n_neighbors=3`, `weights='uniform'`），原生运行在所选特征子集上；同时记录折内标准化后的 `StandardScaler + 3-NN` 结果作为稳健性对照。
4. **分类器 4：Gaussian Naive Bayes (GaussianNB)**
   * `GaussianNB(var_smoothing=1e-9)` 作为概率生成模型对照方法，在训练折内部按类别估计条件高斯分布参数 $(\mu_{c, j}, \sigma_{c, j}^2)$，在测试折执行后验贝叶斯判决。
5. **分类器 5：Linear Discriminant Analysis (Shrinkage LDA) 协方差收缩正则化严格流水线**
   * **审稿诉求闭环与物理瓶颈分析（响应 Reviewer 4 Minor 5）**：
     审稿人明确点名要求补充 LDA 跨分类器泛化实验。但在小样本超高维（$n \ll 100, D \gg 10^3$）生物医学数据中，即便特征经过选择压缩至数十维，若当前折训练样本数 $N_{\mathrm{train}} < d_{\mathrm{selected}}$，经验类内散度协方差矩阵 $\mathbf{\Sigma}_w$ 仍会发生数学上的秩亏损（Rank-Deficient）与奇异性崩溃，经典求逆算法直接失效。为此，**严格禁止使用无正则化的标准 LDA，强制采用基于 Ledoit--Wolf 解析估计的协方差收缩正则化 LDA（Shrinkage Regularized LDA）**；
   * **折内标准化与收缩流水线 Pipeline**：
     ```python
     from sklearn.pipeline import Pipeline
     from sklearn.preprocessing import StandardScaler
     from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

     lda_pipeline = Pipeline([
         ('scaler', StandardScaler()),
         ('lda', LinearDiscriminantAnalysis(
             solver='lsqr',             # 采用支持协方差收缩正则化的最小二乘求解器
             shrinkage='auto'           # 采用 Ledoit-Wolf 自动解析公式估计最优收缩系数 lambda
         ))
     ])
     lda_pipeline.fit(X_train[:, active_features], y_train)
     y_pred_lda = lda_pipeline.predict(X_test[:, active_features])
     ```
   * **零泄露硬红线**：`StandardScaler` 严格仅在训练折 $\mathcal{D}_{\mathrm{train\_outer}}^{(k)}$ 上拟合均值与标准差，盲测折 $\mathcal{D}_{\mathrm{test\_outer}}^{(k)}$ 仅执行 `transform()`，杜绝任何量纲外泄；
   * **协方差收缩机理与奇异性防御**：
     Ledoit--Wolf 收缩将经验协方差矩阵 $\mathbf{\Sigma}_w$ 平滑收缩至等方差标量阵：
     $$\mathbf{\Sigma}_{\mathrm{shrink}} = (1 - \lambda^*) \mathbf{\Sigma}_w + \lambda^* \frac{\mathrm{Tr}(\mathbf{\Sigma}_w)}{d} \mathbf{I}_d, \quad \lambda^* \in [0, 1]$$
     该收缩形式可缓解高维样本不足引起的协方差病态，但当收缩系数或数据退化时，不保证任意情形下都严格正定或良态可逆。须检查常数特征和拟合异常，并执行预设回退与状态记录；不能用该公式直接宣称数值问题已被完全解决；
   * **多分类场景原生支持**：
     LDA 对二分类（$C=2$）与多分类（$C > 2$，如 `SRBCT` 4 类别、`COIL20` 20 类别）天然支持，基于广义特征值问题投影至至多 $\min(C - 1, d)$ 维典型判别子空间中执行贝叶斯判决；
   * **数值异常与退化回退保护规则（Fallback Protocol）**：
     若在某些小样本折上遇到特征常数化导致收缩估计触发数值告警，脚本内置自动回退保护：
     * 回退等级 1：显式使用固定收缩系数 `shrinkage=0.1`；
     * 回退等级 2：若仍不收敛，平稳回退至基于奇异值分解伪逆求解的 `LinearDiscriminantAnalysis(solver='svd', tol=1e-4)`；
     * 回退事件与最终采用的分类器配置均须写入元数据；若全部预设回退失败，保留日志并标记该评估失败，不丢弃后重新抽样，也不宣称所有数值情况均保证成功。

#### (4) 真实初始子集规模统计（解决 R4-Minor 3）
在每个外层折初始化完成时，直接记录 $\mathcal{P}_1$（MI 概率播种）生成的初始特征平均数：
$$d_{\mathrm{init}}^{(k)} = \frac{1}{|\mathcal{P}_1|} \sum_{i \in \mathcal{P}_1} \|\mathbf{x}_i^{(0)}\|_0$$

### 6. 运行期微观动力学与信用归因解耦埋点 (Telemetry Hooks & Attribution Audit)
针对 Reviewer 1 关于极稀疏约束反馈可能影响信用权重的质疑，本节规定仅用于记录的带符号分解与事件追踪，不预设分类反馈或约束反馈必定主导。全部日志须跟随实际子群规则、更新事件及衰减时点，不以审计逻辑改变原搜索轨迹。

#### (1) 带符号信用分解与逐事件重构校验 (Signed Credit Attribution)
对同一次比较的新候选 $\mathbf{x}\in\{0,1\}^D$ 与更新前个人最优 $\mathbf{p}\in\{0,1\}^D$，先确认两者已按**同一当前阶段与子群规则**评分，再定义带符号改善量
$$\delta=f(\mathbf{p})-f(\mathbf{x})\in\mathbb{R}.$$
分类改善与尺寸变化可能互相抵消，因此不能把各分量取绝对值后相加。以 $d_p=\|\mathbf{p}\|_0$、$d_x=\|\mathbf{x}\|_0$ 定义
$$\delta_{\mathrm{class}}=\begin{cases}
w_a\bigl[\mathrm{Err}(\mathbf{p})-\mathrm{Err}(\mathbf{x})\bigr], & \text{两者按当前子群规则均可行，且均有真实内层分类误差},\\
0, & \text{其他情形},
\end{cases}$$
$$\delta_{\mathrm{size}}=w_f\frac{d_p-d_x}{D},\qquad
\delta_{\mathrm{barrier}}=\delta-\delta_{\mathrm{class}}-\delta_{\mathrm{size}}.$$
这里 barrier 是**约束分支及未执行分类评价带来的剩余贡献**，不一概解释成独立的固定屏障高度。未做 CV 的解不得补造零误差或零准确率；分类分量取 0 仅表示该事件不归入“双可行分类反馈”。可行性分别遵循实际子群定义，不能给所有子群机械套用同一条 $d\ge3$。每次比较另标记“双可行、跨可行边界、双不可行”。

为保留实际信用更新的方向，设改变位集合为 $\mathcal{C}\subseteq\{1,\ldots,D\}$，定义方向向量 $\mathbf{s}\in\{-1,0,1\}^D$，其中
$$s_j=(2x_j-1)\,\mathbb{I}(j\in\mathcal{C}).$$
各追踪分量仅在搜索开始时初始化为零向量，之后在实际更新 W 的同一事件上分别执行 $\mathbf{W}_h\leftarrow\mathbf{W}_h+\delta_h\mathbf{s}$，其中 $\mathbf{W}_h\in\mathbb{R}^D$， $h\in\{\mathrm{class},\mathrm{size},\mathrm{barrier}\}$。成功与失败分支均保留符号，改变位、更新对象和时点须与实际 W 一致；所有分量使用相同衰减时点和因子。若 W 初始值非零，另存并同步衰减 $\mathbf{W}_{\mathrm{init}}\in\mathbb{R}^D$，不能把初值遗漏或冒充分类贡献。

在每次更新与衰减后核对
$$\mathbf{W}_{\mathrm{total}}=\mathbf{W}_{\mathrm{init}}+\mathbf{W}_{\mathrm{class}}+\mathbf{W}_{\mathrm{size}}+\mathbf{W}_{\mathrm{barrier}}.$$
分量统一按 float64 记录，建议使用逐元素 rtol=$10^{-8}$、atol=$10^{-10}$ 校验并保存最大重构残差。若不满足，须先排查归因实现与浮点误差，不得依据未闭合的分量输出机制结论。本节只是审计设计，不代表已经取得重构通过结果。

#### (2) 消除循环论证与特征组划分规范 (Eliminating Circular Reasoning & Non-Circular Quantile Protocol)
* **循环论证防范与认知边界界定 (Epistemological Demarcation)**：
  在真实生物基因表达数据集（如 Colon、Prostate、Leukaemia 等）中，由于缺乏预先已知的无偏生物真值金标准（Ground Truth），直接将“互信息前 10%”命名为“真实信号（$\mathcal{S}_{\mathrm{signal}}$）”、将“互信息后 50%”命名为“噪声（$\mathcal{S}_{\mathrm{noise}}$）”，再用 $\mathbf{W}$ 偏向高 MI 组来证明“$\mathbf{W}$ 成功识别了真实信号”，在方法论上构成了**严重的同义反复与循环论证（Circular Tautology）**。因为 MI 本身已使用了类别标签信息，且初始概率播种（MII）天然赋予了高 MI 特征更高的初态采样概率。
* **客观分位组划分规范 (Quantile-Based Partitioning)**：
  在所有真实基准数据集上，坚决废弃主观的“真实信号/噪声”强定义，严格形式化为客观的分位统计组：
  * **高 MI 分位组（$\mathcal{Q}_{\mathrm{high\_MI}}$）**：特征互信息排名前 10% 的候选特征（Top 10% MI quantile）；
  * **低 MI 分位组（$\mathcal{Q}_{\mathrm{low\_MI}}$）**：特征互信息排名后 50% 的候选特征（Bottom 50% MI quantile）。
* **“真实信号/噪声（Signal/Noise）”强定义的唯一定义边界**：
  Madelon 的生成机制由 5 个信息维度、15 个由其构造的线性组合维度以及 480 个干扰维度组成，不能写成 20 个独立原始信号。已知生成机制不等于已知本地矩阵的列身份：只有取得与当前文件列序一致的权威真值映射，记录来源、数据指纹与列重排关系后，才计算已知信息维度的恢复率，并区分原始与冗余信息维度。不能用 MI 排名反推出真值；若没有可核验映射，Madelon 本轮仅作分类基准，不输出 TPR、噪声选择比例或信号恢复结论。确需此类验证时，可另行选择具有明确列级真值的自生成数据，但不列为本轮强制新增套件。

#### (3) 描述性轨迹与预设置换统计量 (Descriptive Traces & Prespecified Statistic)
在每个外层训练折，仅用该折的当前训练标签计算 MI。真实条件与每个置换条件均须重新按自身 MI 排名划组：前 10% 为高 MI 组，后 50% 为低 MI 组，高组大小取 ceil(0.10D)，低组大小取 floor(0.50D)，并列时按原列索引升序排序；本轮 D 足够大，两组均非空且互不重叠。MI 组是统计先验分组，不是真实信号身份。

**描述性记录。** 逐代记录分类分量、尺寸分量及剩余分量在两组中的均值、SD 与 IQR，以及 $\mathbf{W}_{\mathrm{class}}$ 与当前 MI 的 Spearman 相关。相关性仅描述反馈与先验的一致性；常向量的相关系数记为未定义，不填 0。标签置换后，由于 MI 播种、尺寸惩罚与选择反馈仍存在，权重可以保留非零均值、非零相关或组间差异，**不得预设它必然退化为零均值白噪声**。

**固定主统计量。** 对每个外层折 $k$，只在搜索结束时计算分类分量的分位组均值差
$$\Delta W_{\mathrm{class}}^{(k)}=\operatorname{mean}_{j\in\mathcal{Q}_{\mathrm{high\_MI}}^{(k)}}W_{\mathrm{class},j}^{(k)}-\operatorname{mean}_{j\in\mathcal{Q}_{\mathrm{low\_MI}}^{(k)}}W_{\mathrm{class},j}^{(k)},$$
并定义数据集级统计量
$$T_W=\frac{1}{5}\sum_{k=1}^{5}\Delta W_{\mathrm{class}}^{(k)}.$$
真实与置换条件必须比较同一分类分量，不能以真实分类分量对比置换总 W；不按轨迹挑选最显著代数。本轮默认按套件 4 固定优化器 seed=7；若在运行前改为 10 种子统计量，真实与全部置换均须先按相同 10 种子取均值再形成各自统计量。

**推断规则统一。** $T_W$ 的经验零分布来自套件 4 中相同完整流程的置换结果，不额外假设正态或零均值。Colon、SRBCT 各自的 $T_W$ 与 Pooled OOF BAcc 构成共 4 个预设检验，统一使用 Holm 校正与家族显著性水平 $\alpha=0.05$。经验 p、描述性标准化偏离量及经验分位数按套件 4 报告；分位数范围不是效应置信区间。显著结果只支持当前统计量超出该流程的置换参照，不证明生物真值身份、临床因果或分类反馈必然主导。

**屏蔽约束反馈的附加诊断。** 定义“本次新候选或对照旧解任一个不可行，则该比较不更新 W”的保护配置，其他规则保持一致。默认仅在 Colon、SRBCT 上使用与 Full 相同的外层折及 10 个优化器种子，比较预测表现、重构分量和事件比例；这是 7 组主矩阵之外的局部诊断，不预设结果方向，也不自动借用 Full 的置换零分布进行正式检验。

#### (4) KER 动力学与全局最优更新来源追踪 (KER Dynamics & Event Source Tracking)
将局部精英接受、瞬时胜过 gbest 和最终 gbest 更新来源分别计数，不能互相替代，更不能把事件来源比例解释成独立的因果效应。

**实际尝试与局部接受。** 每次确实完成 KER 候选评价时，累加 actual_ker_attempts；缓存命中的评价也计一次，未获预算的候选不计。该计数覆盖最后一个未完成代中的已执行事件，不用“完整代数乘 3”代替。只有 KER 解按当前阶段评分严格优于对应精英 pbest 时，才累加 ker_accepted_pbest，并报告
$$\mathrm{Acc\_Rate}_{\mathrm{KER}}=\frac{\mathrm{ker\_accepted\_pbest}}{\mathrm{actual\_ker\_attempts}}.$$
无尝试时记 NA。实际尝试数、接受数和接受率都由日志给出，不预填 255 或 300。

**瞬时胜过与最终来源。** 每次 KER 候选评价时另记其是否严格优于当时同阶段的 gbest。最终统一检查 gbest 时，按胜出解最后一次有效产生的事件标记来源为 KER、常规群体更新或 AIR；不得仅因其索引属于精英集合就归给 KER。TPS 重评分改变目标标尺，不算搜索突破；初始化单列。若预算在代中耗尽，仍对已完成候选按同一规则做终止前最优检查并记录尾部事件，不能遗漏。

**来源占比。** 设 $N_{\mathrm{gbest\_events}}$ 为上述实际记录的有效最优刷新事件数，则
$$\mathrm{Share}_{\mathrm{KER}}=\frac{N_{\mathrm{gbest\_from\_KER}}}{N_{\mathrm{gbest\_events}}}.$$
分母为 0 时记 NA，其余来源同口径报告，确保分类互斥且计数闭合。该指标是观察到的更新事件来源占比，不证明 KER 对精度提升的独立因果贡献或必然帮助跳出局部极值。机制增量价值须结合套件 3 的受控性能对比判断。

#### (5) 核心辅助动力学指标全景记录
* **$\mathcal{P}_2$ 可行解演化曲线**：
  * 每代记录 $\mathcal{P}_2$ 中满足 $d \ge 3$ 的粒子比例：$\mathrm{Feas\_Rate}_{\mathcal{P}_2}(t) = \frac{1}{|\mathcal{P}_2|} \sum_{i \in \mathcal{P}_2} \mathbb{I}(\|\mathbf{x}_i^{(t)}\|_0 \ge 3)$。
* **屏蔽越界更新对照测试（Barrier-Isolated Protection）**：
  * 保护配置按前述“新候选或旧解任一个不可行则该比较不更新 W”执行，限定为 Colon、SRBCT 的附加诊断；比较结果可以支持或削弱屏障反馈解释，不预先宣称分类分量占绝对支配地位。

### 7. 论文与答复信方法声明模板 (Methodological Statement)
以下文字说明方案边界；用于手稿时须与实际完成的实验及最终配置一致，不能把待执行方案写成已有结果。

> “We use an outer-test-isolated evaluation scheme with priors restricted to the outer training partition. Within each of five outer folds, MI is estimated from the outer training data and used to guide initialization and search. The outer test partition is excluded from prior estimation, feature selection, preprocessing fitting, hyperparameter selection, and model fitting. Inner five-fold cross-validation supplies a search surrogate; its scores are not treated as independent generalization estimates because the prior uses the complete outer training partition. After search, the selected subset is evaluated using models fitted only on the outer training data, with configurations fixed before inspecting outer scores. Pooled out-of-fold predictions are reported as the primary measure of out-of-sample performance. This protocol controls outer-test information leakage but does not imply exact finite-sample unbiasedness or validation in an independent clinical cohort.”

---

## 📊 三、 套件 2 详细设计：经典 Filter 过滤式对照方法严格折内对比与帕累托前沿分析

### 1. 严格折内无泄露原则 (Strict Fold-Internal Fitting)
为彻底杜绝审稿人指责的“特征选择数据泄露（Filter Selection Leakage）”，本套件严格遵守**“折内训练拟合、外层测试折隔离评估”**原则：
* **零泄露红线**：所有过滤方法（Top-$k$ MI、mRMR、ReliefF、LASSO）**只能且仅能在当前训练折内部拟合与打分**；
* 严禁在交叉验证切分前在完整数据集上运行特征选择；测试折（Test Fold / Outer Test Fold）在特征选择阶段绝对隔离，仅用于最终盲测。

### 2. 评测维度设计：固定网格与全景帕累托对比
彻底废弃“由完整数据最终结果倒推 $k$”的潜在泄露做法，设立两个完全客观的对比维度：
1. **先验固定网格对比（A Priori Fixed Grids）**：
   * 预先固定三个特征截断深度：
     * **$k = 20$**：极简生物标志物签名（匹配临床小基因组筛查需求）；
     * **$k = 50$**：中等规模特征子集；
     * **$k = 100$**：与 KDS-EL 全局平均 88 个特征高度相近的参考特征尺度。
   * 在每个训练折内，过滤方法独立筛选 Top-$k$ 特征并输入 3-NN 分类器测试，计算 Acc 与 BAcc。
2. **特征数量—精度帕累托前沿分析（Pareto Front Trajectory）**：
   * 在代表性数据集上绘制 $k \in [10, 20, 50, 100, 200]$ 下各 Filter 的准确率收敛曲线；
   * 将 KDS-EL 的特征数—精度结果叠加于同一外层评估图，检验其与 Filter 的权衡关系。完整展示预设各个 k，允许优势、持平或退化；不得预设左上支配，也不得按外层得分挑选最佳 k 后将其作为独立验证结果。

### 3. 4 款 Filter 的工程死锁参数与超高维（T1D）优化规范

#### (1) 两阶段极速 mRMR 机制（Two-Stage Fast mRMR，彭汉川标准）
* **超高维（$D = 54,675$）瓶颈对策**：成对特征间冗余计算复杂度为 $\mathcal{O}(D^2)$，全量计算将耗费数小时并引发内存溢出。
* **顶刊标准两阶段加速方案**：
  * **第一阶段（相关性初筛）**：在训练折内，使用单变量互信息对全部 $D$ 个特征快速打分，保留前 $M = 1{,}000$ 个高相关特征（初步估计单折初筛耗时在秒级）；
  * **第二阶段（冗余极小化精选）**：仅在这 $1{,}000$ 个特征的候选池中运行贪婪 mRMR 互信息极值选择，提取前 $k \in \{20, 50, 100\}$ 个特征（初步估计单折精选耗时在数秒级）。
* **保障**：既完整保留了 mRMR 的互补除冗本质，又大幅规避了超高维全量成对特征冗余矩阵计算引发的显存溢出与时间爆炸瓶颈。

#### (2) ReliefF：确定性多分类实现规范
* **近邻数设定**：设定近邻数 $k_{\mathrm{relief}} = 5$；
* **全样本无抽样策略**：鉴于生物医学微阵列样本量极小（$N \le 173$），设置采样数 $m_{\mathrm{samples}} = N_{\mathrm{train}}$，遍历训练折全部样本以彻底消除随机抽样方差，确保结果 100% 确定性可复现；
* **距离度量**：标准化后的曼哈顿距离（Manhattan Distance，缓解超高维欧氏距离集中效应）。

#### (3) LASSO（L1-Regularized Logistic Regression）规范死锁
* **数据预处理**：在训练折内拟合 `StandardScaler()`，严禁测试折信息参与均值与方差计算；
* **求解器与模式**：
  * 二分类：`penalty='l1'`, `solver='liblinear'`, `max_iter=2000`, `tol=1e-4`；
  * 多分类：采用 One-vs-Rest (OvR) 策略（`multi_class='ovr'`, `solver='liblinear'`）；
* **类别权重**：强制设置 `class_weight='balanced'`（呼应类别失衡评审诉求）；
* **排序与平稳截断机制（解决特征数不足问题）**：
  * 设定正则化强度 $C = 0.1$，拟合后提取特征系数绝对值之和：
    $$\mathrm{Score}_j = \sum_{c=1}^C |\beta_{c, j}|$$
  * 按绝对值降序稳定提取前 $k \in \{20, 50, 100\}$ 个特征，避免特征稀疏过度或选不够的崩溃问题。

#### (4) Top-$k$ MI
* 在训练折内调用 `mutual_info_classif(X_tr, y_tr, n_neighbors=3, random_state=42)`，直接按得分降序截断前 $k$ 个特征。

---

## 🧩 四、 套件 3 详细设计：模块解耦与受控组件贡献分析 (Modular Decoupling & Controlled Component Contribution Analysis)

### 1. 分层受控实验设计原则与参数死锁
为深入响应 Reviewer 1 (Point 4) 与 Reviewer 4 (Major 2) 关于“多机制打包升级、参数未完全隔离”的技术质询，本套件摒弃将所有变体均笼统套用“正交单变量”的过度宣称，确立**分层受控实验设计原则（Hierarchical Controlled Experimental Protocol）**：
* **两级受控对比范式界定**：
  1. **参数与调度受控变体**：保持架构与非目标参数配置一致，只改变指定权重、调度方向或信用衰减因子。随机轨迹、实际代数、累计衰减次数和 AIR 事件可随搜索结果改变，不能宣称所有内部状态完全相同。
  2. **架构与预算分配对照**：单种群和无 KER 配置统一保持人口规模 20 与候选请求上限 2,000。该设计控制人口与请求配额，但不保证相同唯一掩码数、拟合数、代数或实际计算量，相关日志须随结果一并报告。
* **真实默认配置死锁（遵循 `code/config.py:77` 真实实现）**：
  * 基准信用衰减因子严格锁定为 **$\gamma = 0.99$**（纠正早期草案中误写成 0.95 的隐患）；
  * 全局种群规模严格锁定为 **$N = 20$**；
  * 函数评估预算严格锁定为 **$\mathrm{Max\_FEs} = 2{,}000$**；
  * 各变体在未受控维度上的参数均与完整改进算法严格保持一致。

### 2. 7 组受控解耦组件贡献分析矩阵
系统解耦各个关键模块，构建如下涵盖 1 组完整改进算法与 6 组受控对照配置的分析矩阵：

| 变体代号 | 变体性质与受控维度 | 阶段权重调度 $(w_a,w_f)$ | 信用衰减 $\gamma$ | 种群结构 | KER | 预算与代数 | 检验目的 |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **KDS-EL (Full)** | 完整改进算法 | 正向 TPS：$0.70/0.30\to0.95/0.05$ | 0.99 | $\mathcal{P}_1(10)+\mathcal{P}_2(10)$ | $k_e=3$ | 请求上限 2,000，实际代数待测 | 作为同一新增协议下的完整配置参照。 |
| **Abl_Static_095** | 静态权重受控 | 始终 $0.95/0.05$ | 0.99 | 同 Full | $k_e=3$ | 同上，无 TPS 切换重评 | 检验持续高精度偏好下的特征数与分类表现，不预设尺寸膨胀。 |
| **Abl_Static_070** | 静态权重受控 | 始终 $0.70/0.30$ | 0.99 | 同 Full | $k_e=3$ | 同上，无 TPS 切换重评 | 检验持续高压缩偏好下的权衡，不预设准确率下降。 |
| **Abl_Reversed** | 调度方向受控 | 反向 TPS：$0.95/0.05\to0.70/0.30$ | 0.99 | 同 Full | $k_e=3$ | 同上，按相同 q 阈值切换 | 检验反向与正向时序的差异，允许优势、持平或退化，不预设必然破坏收敛。 |
| **Abl_No_Decay** | 信用衰减受控 | 正向 TPS | 1.00 | 同 Full | $k_e=3$ | 同上，实际衰减次数另记 | 检验不遗忘历史反馈对性能与权重轨迹的影响。 |
| **Abl_Single_P1** | 等人口架构对照 | 正向 TPS | 0.99 | 全部 20 个个体按 $\mathcal{P}_1$ 规则运行 | $k_e=3$ | 同上，实际代数待测 | 评估移除异构双群协同后的系统级变化，不视为单一标量参数效应。 |
| **Abl_No_KER** | 精炼与预算分配对照 | 正向 TPS | 0.99 | 同 Full | 禁用 | 同上，通常可执行更多常规更新，数量待测 | 检验等请求配额下精炼与更多群体更新之间的资源分配权衡。 |

### 3. 关键对照配置的方法论深入剖析 (In-Depth Methodological Clarification of Key Benchmarks)

#### (1) Abl_Single_P1：等人口的系统级架构对照
单种群配置保留 20 个个体，全部继承 $\mathcal{P}_1$ 的初始化、可行性与更新规则，不额外替换为另一套随机初始化或新增算法；若初始化含 MI 先验，仍受同一外层训练边界约束。移除 $\mathcal{P}_2$ 后，引导来源、个体组成与知识交互路径随之改变，因此这是系统级架构对照，不能声称“只改变一个内部状态”。最终报告须列明保留与改变的规则。

与 Full 对齐的是人口规模、候选请求上限、划分、种子列表与非目标配置，不是完全相同的搜索轨迹或累计衰减事件数。结果用于评估本轮预算协议下异构双群结构的整体影响，不预设双群必然更优。

#### (2) Abl_No_KER：等请求配额为主，代数快照为辅
Full 的常规完整代包含 20 次群体更新与至多 3 次 KER 请求，无 KER 配置只有 20 次常规更新。两者均将初始化、必要 TPS 重评和 AIR 计入 2,000 次上限，并执行同一预算进度调度。因此，无 KER 配置通常可把释放的配额用于更多群体更新，但实际增加多少代与精炼占比须由日志给出，不能固定为 13 代或 13%。

仅作核算示例：若初始化 20 次、切换恰好重评 20 次且无 AIR，则剩余请求为 1,960；Full 可完成 $\lfloor1960/23\rfloor=85$ 个完整代并余 5 次，无 KER 可完成 $1960/20=98$ 个完整代。此处 85 和 98 不是预设实测值，静态权重配置也不人为增加 20 次重评。

主结论以等请求配额下的最终性能、唯一掩码数、拟合次数及耗时为依据。若保留等代数辅助快照，应预先固定观察点并仅报告两者实际都到达的完整代；例如第 85 代在上述简化条件下，无 KER 已用 $20+20+85\times20=1,740$ 次请求，而非 1,720。快照不能用于最终子集的事后选择，也不替代主预算对比；两者相同代数下的 q 与阶段可能不同，须同时标注，不能称为阶段状态完全匹配的纯组件效应。

### 4. 测量与可视化交付物规范
* **子集规模轨迹**：主图按已用候选请求数或 q 对齐 7 组配置，标注实际 TPS 切换点；按代数绘图仅作辅助，避免不同每代开销被误读为相同搜索成本；
* **综合多维性能指标对比表**：全面汇报各配置变体在外层测试集上的平均准确率（Acc）、平衡准确率（BAcc）、Macro-F1、特征选择数量以及真实运行耗时（Wall-Clock Time）；
* **微观遥测**：报告 KER 实际尝试数与接受率、gbest 刷新事件来源占比、P2 可行率、各类请求及拟合数；来源占比不等同于独立因果效应。

---

## 🎲 五、 套件 4 详细设计：标签置换经验零假设检验 (Label-Permutation Null Hypothesis Test)

### 1. 检验目标与适用条件
在 Colon 与 SRBCT 上检验：真实标签下，完整特征选择与训练流程的预设统计量是否高于标签可交换零假设下的经验参照。$H_0$ 是当前数据与置换约束下 X 与 y 无可检测预测关联，不将其直接等同于“无生物因果关联”。显著结果也不能证明特定基因身份、临床有效性或排除所有数据偏差。

全局置换以样本在零假设下可交换为前提。先检查是否有同一患者重复样本、配对、家系或批次依赖；存在相关结构时须采用预先确定的分组 CV 与受限置换，不能仍盲用全局任意打乱。本轮默认协议仅适用于满足独立样本可交换条件的数据。

### 2. 预先锁定重复单位、统计量与计算规模
**默认省时配置。** 仅对 Full KDS-EL 执行，每数据集 $B=100$ 次标签置换，每个条件完整运行 5 个外层折，每折固定一个优化器种子，即 $R_{\mathrm{perm}}=1$、seed=7。真实标签条件也必须使用同一个 seed=7 的完整 5 折结果；若套件 1 的划分、配置与日志完全一致，可复用其中该种子的 Pooled OOF 及 W 日志，**不能用真实条件的 10 次平均对比置换条件的单次运行**。标签置换随机源与优化器随机源分离，置换编号 b 的标签种子固定为 $10000+b$，优化器种子始终为 7。

每个数据集预先指定两个单侧上尾主统计量：3-NN 的 **Pooled OOF BAcc**，以及前述结束时分类信用分量的 **$T_W$**。共 2 个数据集乘 2 个统计量，形成一个含 4 个检验的家族。Acc、Macro-F1、相关系数和逐代轨迹只作描述，不筛选其中最显著者替换主统计量。

默认置换优化运行数为 $2\times100\times5\times1=1,000$，另加未能从套件 1 复用的真实条件运行。若在查看结果前决定采用 10 个种子，则真实与全部置换都使用同一完整种子列表，并按相同方式先跨种子平均形成统计量；置换运行数将为 10,000。不能看到 p 值后临时改变种子数、比较对象或统计量。总耗时须据压力测试估计，不承诺 20 分钟完成。

### 3. 与真实条件完全匹配的全流程置换
以 $\mathbf{y}^{(0)}=\mathbf{y}$ 表示真实条件，$\mathbf{y}^{(b)}=\pi_b(\mathbf{y})$、$b=1,\ldots,B$ 表示置换条件，X 与原始样本顺序不变。以下步骤对 $b=0$ 与每个 $b>0$ 使用相同程序，而不是仅置换最终分类器标签。

**按当前标签重建划分。** 对每个条件，按该条件的 $\mathbf{y}^{(b)}$ 使用 StratifiedKFold 的固定划分 seed=42 生成外层 5 折，再在各外层训练集内按当前训练标签生成内层 5 折。真实与置换的索引可以不同，因为“按当前标签分层”本身属于被检验程序。**不得先用真实标签固定分层索引，再全局任意置换标签并沿用这些索引。** 同一条件下的配置或种子共享其划分，保存全套索引并标记该条件标签指纹。执行前验证各外层与内层训练划分的类别样本数能支持既定折数；不对单个置换临时降低折数或静默跳过失败条件。若先决条件不满足，先统一修订并重新固定所有条件的协议。

**当前标签下重跑完整训练流程。** 每个外层折仅用该条件的外层训练 X、y 重新计算 MI、划定 MI 分位组、初始化、执行上限 2,000 次候选请求的搜索并拟合最终 3-NN。内层评价、权重分解、TPS 与预处理边界均与真实条件相同。缓存不得跨标签条件复用。所选子集只来自当前外层训练，测试折不参与先验、选择或调参。

**测试标签一致与 OOF 聚合。** 预测对照同一个 $\mathbf{y}^{(b)}$ 在外层测试索引上的标签；不能使用置换训练标签，却对原始测试标签评分。5 折预测按原始样本索引拼成覆盖所有样本的 OOF 向量，再与完整的 $\mathbf{y}^{(b)}$ 计算主指标。W 的统计量按同条件各折当前 MI 分组，从分类信用分量提取并跨 5 折等权汇总。真实与置换不得混比不同聚合方式、不同运行数或不同 W 分量。

**结果存储。** 使用 output/nested_cv/permutation/{dataset}/perm_{b}/，其中 perm_0 为真实条件。保存标签指纹、置换 seed、优化器 seed、outer/inner 索引、配置、OOF 预测、W 分量、候选请求及拟合计数、运行状态。置换划分不得覆盖或误用套件 1 的真实标签 splits 文件。

### 4. 经验 p 值、分辨率与多重比较
对每个预设统计量 T，令 $T_0$ 为真实条件值、$T_b$ 为第 b 个置换条件值。采用含真实条件修正的 Monte Carlo 上尾 p 值
$$p_{\mathrm{emp}}=\frac{1+\sum_{b=1}^{B}\mathbb{I}(T_b\ge T_0)}{B+1}.$$
并列按大于等于计入。此处不称该公式为“严格无偏估计”。$B=100$ 时最小原始 p 为 $1/101\approx0.0099$；不报告 p=0 或 p<0.001，也不由此自动宣称高度显著。

将 Colon、SRBCT 的 BAcc 与 $T_W$ 共 4 个原始 p 统一进行 **Holm 逐步校正，家族 $\alpha=0.05$**。这替代早期草案中未校正的 $\alpha=0.01$，使当前置换次数与家族检验分辨率相容；分别报告原始 p、校正 p、效应方向与是否拒绝。没有达到阈值时如实报告证据不足，不推断不存在预测信号，也不追加未预设检验寻找显著结果。

### 5. 零分布解释与描述性效应量
BAcc 在理想无关联条件下的机会参照为 $1/C$，但本设计以**实际完整流程的经验零分布**为判定依据，不要求有限次置换均值精确等于该值。失衡数据的普通 Acc 不固定为 50%；Macro-F1 同样报告经验分布，不能套用 BAcc 的机会参照。

对任一主统计量，可附带报告
$$Z_{\mathrm{desc}}=\frac{T_0-\mu_{\mathrm{perm}}}{s_{\mathrm{perm}}},$$
以及真实值、零分布均值、样本 SD、IQR 和预定经验分位数。该 Z 仅是描述性标准化偏离量，不假定零分布正态，也不据其转换 p 值或要求某个固定门槛；零分布 SD 为 0 时记 NA。经验分位数范围描述零分布，不是模型泛化表现或净效应的置信区间。置换后的 MI 初始化、尺寸反馈与搜索选择仍可产生结构化 W，零均值白噪声及零相关均不是验收条件。

---

## ⚡ 六、 套件 5 详细设计：历史竞品掩码补充指标离线描述性再分析 (Post-Hoc Re-Analysis of Competitor Masks)

### 1. 严格的数据源口径隔离与黑名单防护
针对工作区物理存储现状，制定不可逾越的数据隔离红线：
* **数据目录**：`output/formal_experiment_20260905_211755/masks/`；
* **严格只读白名单**：脚本**只能且仅能读取 3 款新顶会竞品**的掩码文件：
  $$\text{ALLOWED\_ALGOS} = [\text{'bIRIME'}, \text{'BinCOA'}, \text{'DENCA\_SO'}]$$
  物理目录包含历史 20 个数据集 $\times$ 10 次运行 = 200 个掩码/竞品；经 `BENCHMARK_EVAL_DATASETS`（19 个独立基准）精确过滤后，每个竞品严格提取 19 个独立数据集 $\times$ 10 次运行 = 190 个文件，3 款竞品共计 **570 个有效独立基准历史掩码**（同源重复的 `ALL_AML` 掩码被自动隔离）。
* **绝对黑名单防御（防错载）**：
  * 该目录中历史遗留的 200 个 `mask_KDS_EL_TwoPhase_*.npy` 属于早期 0.9460 的临时测试重跑版，**与论文正文主表的 0.9545 权威数据源（`output/formal_experiment_final/`）存在版本脱节**；
  * **脚本必须内置断言校验**：若遍历到包含 `KDS_EL` 关键字的掩码文件，脚本强制直接跳过或抛出异常，**坚决杜绝误载该目录中的 KDS-EL 掩码**！

### 2. 统计学定位界定：描述性再分析而非无偏泛化评估
必须在手稿与设计中严谨阐明本套件的统计学边界：
* **方法论真实属性**：这批历史竞品掩码是在完整数据集上运行算法后最终保留的特征子集。以此特征子集在相同数据集上重新执行 5 折划分计算 BAcc 与 Macro-F1，**属于“特征选择后的内部交叉验证描述性再分析（Post-Hoc Descriptive Re-Analysis）”**；
* **功能边界（可以做什么 vs 不能做什么）**：
  * **允许用途**：为历史主表补充抗失衡指标（BAcc、Macro-F1），补充跨分类器一致性观察，响应审稿人对失衡数据集评价指标单一的质询；
  * **严禁宣称**：**绝不能用于宣称“产生了新的无偏外层泛化估计”，也不能宣称“解决了原始协议的测试泄露”，更绝对不能将这批内部再分析数据与套件 1 的外层嵌套式评估（方案 A）盲测结果直接混合求均值**！

### 3. 基准数据集过滤规范与独立性死锁（终结 19 vs 20 模糊性）
* **禁止全表求平均**：`output/formal_experiment_final/results_summary.csv` 包含 26 个历史数据集，绝不能简单地对全表行求平均；
* **基准数据集受控引用与唯一性自检**：
  * 运行前自动检查基准数据集列表的唯一性，并记录最终纳入分析的数据集名称、样本数、特征维度和类别数；
  * 脚本必须显式导入权威基准数据集配置列表（`from config import BENCHMARK_EVAL_DATASETS`，列表长度严格锁定为 19）；
* **同源数据去重与正文口径关系彻底澄清**：
  * **去重归正与基准定稿**：经核实，历史原稿中的 `ALL_AML` 与 `Leukaemia`（均为 $72 \times 7{,}129$）源自 Golub et al. (1999) 的同一微阵列实验批次。为从根本上杜绝 Reviewer 1 Point 9 严厉指出的“同一数据集计算两次人为虚增检验自由度 $N$”的硬伤，**正式剔除同源重复项 `ALL_AML`，将修订版官方基准集最终定稿为 19 个严格独立的问题实例（`BENCHMARK_EVAL_DATASETS`，保留 `Leukaemia`）**；
  * **正文历史 20 数据集描述与本次 19 独立基准的关系彻底统一**：
    * 历史原稿（R0）表格与正文因历史沿袭列入了 20 个基准名称（包含 `ALL_AML` 与 `Leukaemia`）；
    * 修订版的基准名单、历史内部评估与新增外层评估均按去重后的 19 个数据集分别整理。历史 Acc、特征数、耗时、秩次与 Wilcoxon/Holm 统计量须从各算法对应真实来源重新汇总；记录并列、零差值处理及有效配对数，不预填理论极小 p 作为实测结果。新增外层结果另行制表，不能与历史内部 CV 分数混合汇总。
    * 补充附录并列历史 20 集与去重后 19 集结果，真实报告均值、排序和显著性变化，不承诺所有优势保持不变。**0.9545 是 output/formal_experiment_final/ 中历史 20 集的纯分类 Acc 均值，不是已计算的 19 集均值，更不是本轮外层测试结果。0.9574 为旧 1-fitG，不能作为 Acc。** 19 集的新均值与统计结论必须待实际重算后填写。
  * 离线脚本必须采用受控迭代机制：`for dataset in BENCHMARK_EVAL_DATASETS:`，确保统计均值与样本量 $N$ 严格与论文正文基准名单 100% 同步。

### 4. 自动化批处理离线评估流程
```python
# 离线评估核心逻辑伪代码：
from config import BENCHMARK_EVAL_DATASETS  # 严格使用官方受控基准集 (N = 19 严格独立基准)

ALLOWED_COMPETITORS = ['bIRIME', 'BinCOA', 'DENCA_SO']

for algo in ALLOWED_COMPETITORS:
    for dataset in BENCHMARK_EVAL_DATASETS:
        X, y = load_dataset(dataset)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        for run_id in range(1, 11):
            mask_path = f"masks/mask_{algo}_{dataset}_run{run_id}.npy"
            # 严格防御：若意外触及 KDS-EL 文件名立即触发断言
            assert "KDS_EL" not in mask_path, "Error: Unauthorized KDS-EL mask detected!"
            
            mask = np.load(mask_path)
            # 在 5 折上离线拟合 3-NN，输出并记录 Balanced Accuracy 与 Macro-F1
```
* **产出目标**：生成《历史竞品特征掩码补充指标再分析表》，作为历史对比表的描述性支撑附件（Supplementary Metric Table），清晰标明其为特征选择后同分布再分析。

---

## 🧬 七、 套件 6 详细设计：受控肿瘤微阵列 KEGG/GO 功能富集与特征稳定性分析 (Biomedical Rigor, Platform-Bounded Enrichment & Stability)

### 1. 适用数据集范围严格限定（严禁非基因数据集跨界富集）
* **基准数据类别严密二分**：
  * **受控基因表达微阵列芯片（纳入本套件分析）**：真实人类癌症基因表达微阵列数据集，重点针对审稿人明确质询的三大典型病种微阵列：
    1. `Colon` (Alon et al., 1999, $62 \times 2{,}000$, 结直肠腺癌与正常粘膜对照)；
    2. `Prostate` (Singh et al., 2002, $102 \times 12{,}625$, 前列腺肿瘤与良性组织对照)；
    3. `Leukaemia` (Golub et al., 1999, $72 \times 7{,}129$, 急性淋巴细胞白血病 ALL 与急性髓系白血病 AML 对照)。
    *(其余人类肿瘤芯片如 `DLBCL`、`SRBCT`、`Adenoma` 按完全相同的探针映射与检验协议作为备选扩展)*。
  * **通用机器学习基准（绝对严禁执行 KEGG/GO 富集分析）**：
    * `COIL20` (图像像素，20 类实体物体灰度图像，1,024 维)；
    * `ISOLET` (语音声学信号，26 个英文字母发音特征，617 维)；
    * `BASEHOCK`、`PCMAC`、`RELATHE` (文本分类，Usenet 新闻组词频词袋向量)；
    * Madelon：人工合成分类数据，含 5 个信息维度、15 个线性组合维度和 480 个干扰维度；本地列级真值映射未核验时仅用于分类，不计算信号恢复率；
    * `USPS` (手写数字灰度图像像素，256 维)；
    * `HAPTDataSet` (智能手机加速度计与陀螺仪时序传感统计特征)；
    * `MultipleFeaturesDigit` (手写数字形态多视点抽取特征)。
* **方法论边界铁律**：非生物特征在本体论上不存在任何生物学信号通路或基因本体属性，对图像像素或词频执行 KEGG/GO 分析属于严重的学术低级错误。本套件严格且仅在上述受控人类肿瘤微阵列芯片上执行。

### 2. 特征标识符审计与溯源映射管线 (Traceable Gene Identifier Mapping Protocol)
* **原始特征标识符现状审计**：
  * `Colon.txt`：特征标识符为 UniGene Cluster IDs（前缀 `Hsa.`，如 `Hsa.3004`, `Hsa.13491`, `Hsa.37254`）。**源码审计发现存在同名重复行**（例如 `Hsa.13491` 连续占据第 3 行和第 4 行）；
  * `Prostate.txt`：特征标识符为 Affymetrix HG-U95Av2 探针集 ID（如 `100_g_at`, `1000_at` 等）；
  * `Leukaemia.txt`：特征标识符为 Affymetrix Hu6800 / HuGeneFL 探针集 ID（如 `AFFX-BioB-5_at`, `M19507_at` 等）。
* **规范化映射标准与权威注释库**：
  * **目标标识符体系**：所有原始特征统一映射至国际权威的 **NCBI Entrez Gene ID** 以及 **HGNC Approved Gene Symbol**；
  * **注释数据库版本与可溯源文件**：
    * `Colon`：基于 NCBI UniGene Build 33/34 历史注释索引表与 Alon et al. (1999) 官方探针映射表；
    * `Prostate`：基于 Bioconductor 权威注释包 `hgu95av2.db` (AnnotationDbi) 与 NCBI GEO GPL91 平台注释文件；
    * `Leukaemia`：基于 Bioconductor 权威注释包 `hu6800.db` 与 NCBI GEO GPL80 平台注释文件；
  * **多探针兼并与重复行去重规则（Deduplication & Many-to-One Aggregation）**：
    * 在计算特征选择算法选出的基因签名时，若芯片中存在多个探针集或重复行映射至同一个 Entrez Gene ID，按**唯一基因实体集合（Unique Gene Entity Set）**取并集去重，避免同一基因因多探针重复加权导致富集统计检验虚增；
    * 严格剔除无明确生物实体的技术质控探针（如 Affymetrix 的 `AFFX-*` 外部 Spike-in 质控序列、寡聚核苷酸杂交对照探针）以及无法溯源的探针，并在实验输出中严格汇报有效映射探针比例（Mapping Coverage，例如 Colon 映射率达 96.5%）。

### 3. 富集分析背景全集界定（Platform-Specific Universe Definition $\mathcal{U}$）
* **严禁全基因组背景虚假膨胀（Anti-Inflation Protocol）**：
  * 在超几何检验（Hypergeometric Test）与 Fisher 精确检验中，背景基因全集 $\mathcal{U}$ **绝对严禁直接采用人类全基因组（~20,000+ 蛋白质编码基因）**！
  * **科学原理**：早期的肿瘤微阵列芯片在探针设计阶段就已高度富集了组织表达丰度高或肿瘤相关的特异探针。若以全基因组为背景，任意随机抽取的探针都会因芯片本身的先验选择而“显著富集”于癌症通路，造成严重的假阳性膨胀；
* **芯片特异性封闭域背景构建**：
  * 对于芯片数据集 $\mathcal{D}$，其背景集合 $\mathcal{U}_{\mathcal{D}}$ 严格限定为**该芯片测量包含的全部特征中，成功映射到 Entrez Gene ID 的唯一基因全集**：
    $$\mathcal{U}_{\mathcal{D}} = \left\{ \mathrm{Map}(j) \mid j \in \{1, 2, \dots, D\}, \; \mathrm{Map}(j) \neq \varnothing \right\}$$
    例如：`Colon` 芯片背景严格限定为其 2,000 个特征所映射出的平台基因实体（约 1,900+ 个唯一 Entrez ID），`Prostate` 严格限定为其 12,600 个探针所映射出的平台基因实体；
  * 富集检验列联表严格在 $2 \times 2$ 封闭列联阵（选出基因 vs 未选基因，通路内基因 vs 通路外基因）内构建。

### 4. 统计推断假说检验框架与 FDR 多重比较校正 (Falsifiable Hypothesis Testing & BH Protocol)
* **确立客观可证伪的假设检验规程，杜绝预设肯定性结论**：
  * **严谨重构为假设检验规程**：
    * **检验目标**：用于检验所选特征是否在预先注册的癌症相关通路或 GO 类别中呈现统计显著富集；
    * **可证伪退出分支**：若在经过严格多重比较校正后，未达到校正后假发现率阈值（$q \ge 0.05$），**则必须如实、客观地在论文与回复信中报告“未观察到显著富集（No significant enrichment observed after FDR adjustment）”**，不得进行主观粉饰或选择性报告。
* **多重比较校正协议**：
  * 采用 Benjamini-Hochberg (BH) 逐步校正程序对测试的所有通路/条目名录进行假发现率（False Discovery Rate, FDR）校正：
    $$q_i = \min_{k \ge i} \left( \frac{M}{k} p_{(k)} \right) \le 0.05$$
    其中 $M$ 为该数据库在该芯片背景下有效测试的总通路条目数；
  * 富集分析工具与数据库溯源锁死：Python `gseapy` (v1.1+) 或 R `clusterProfiler` (v4.x)，底层对接 KEGG Human Pathway (Release 2024) 与 Gene Ontology (GO Biological Process, Release 2024)，明确记录分析执行日期与数据库版本哈希。

### 5. 组织异质性混杂因素客观辨析（平滑肌混杂病理机制正面剖析）
* **真值审计：DES 与 ACTG2 在 Colon 数据集中的客观存在形式**：
  * 经源码与数据集真实核查，`Colon.txt` 中：
    * 第 2 行特征 `Hsa.3004` $\longrightarrow$ 溯源映射为 **`DES`**（结蛋白，Desmin）；
    * 第 3 行与第 4 行重复特征 `Hsa.13491` $\longrightarrow$ 溯源映射为 **`ACTG2`**（平滑肌 $\gamma$-肌动蛋白，Actin Gamma 2, Smooth Muscle）；
    * 第 5 行特征 `Hsa.37254` $\longrightarrow$ 溯源映射为 **`MYH11`**（平滑肌肌球蛋白重链 11，Myosin Heavy Chain 11）。
* **病理生理学溯源（正面直面 Reviewer 1 质询）**：
  * 在 Alon et al. (1999) 结肠癌经典组织活检实验中，正常对照样本取自包含粘膜下层（Submucosa）和固有肌层（Muscularis Propria）的全层或厚层肠壁，富含平滑肌细胞；而结肠腺癌（Carcinoma）活检样本主要为上皮源性恶性增殖细胞，组织结构重塑，肌层平滑肌成分急剧减少；
  * 因此，`DES`、`ACTG2`、`MYH11` 在正常组与肿瘤组之间表现出的巨大表达落差，**在病理机制上属于组织活检样本中平滑肌细胞浸润比例差异（Biopsy Smooth-Muscle Content Heterogeneity）所造成的解剖学混杂因素（Histological/Anatomical Confounder）**，绝非结肠癌细胞内在特异性的致癌驱动突变（Tumour-Intrinsic Driver Oncogenes）；
* **学术辩护与手稿修订规范**：
  1. **明确区分模式分类与病理驱动**：在模式识别视角下，平滑肌结构差异构成了区分正常组织与肿瘤组织的强判别信号，特征选择算法将其保留符合数据驱动的统计优化目标；但在生物医学可解释性章节中，**必须严谨纠正以往研究将 DES/ACTG2 误读为“结直肠癌新型致癌基因”的表述**，客观标注其为“组织构成异质性生物标志物（Biopsy Composition / Histological Architecture Markers）”；
  2. **通路级功能去混杂验证**：在剥离单纯结构性平滑肌基因后，系统评估算法所选其余特征在癌症特征通路（如 Wnt 信号通路、细胞周期、结直肠癌特异信号等）中的富集分布，客观呈现真实生物学图景。

### 6. 同一外层训练折内的跨运行特征稳定性
本轮以 **Jaccard 为主指标**，使用套件 1 在同一外层训练折内经 10 个优化器种子新搜索得到的掩码。KDS-EL、MEL、bIRIME 及实际纳入的 Filter 均遵守相同训练数据边界；不能拿历史全数据搜索掩码代替新外层训练掩码。

对固定外层折内的两个特征集合 $\mathcal{S}_a,\mathcal{S}_b\subseteq\{1,\ldots,D\}$，定义
$$J(\mathcal{S}_a,\mathcal{S}_b)=\frac{|\mathcal{S}_a\cap\mathcal{S}_b|}{|\mathcal{S}_a\cup\mathcal{S}_b|}.$$
每折计算 $\binom{10}{2}=45$ 对并描述其均值与分布，再描述性汇总 5 折。45 对共享掩码，不是 45 个独立统计样本；不能混合 50 个来自不同外层训练集的掩码当作同条件重复。同步报告子集规模分布，因为 Jaccard 会受大小影响。单边空集时为 0；双空集的分母为 0，单独标记退化情况，不用默认相似度掩盖搜索失败。

**Kuncheva 仅作等长可选指标。** 对 $|\mathcal{S}_a|=|\mathcal{S}_b|=k$、$0<k<D$ 且 $r=|\mathcal{S}_a\cap\mathcal{S}_b|$ 时，可使用
$$\mathrm{KI}=\frac{rD-k^2}{k(D-k)}.$$
不得把此式直接套用到不同长度子集，或通过任意截断掩码“凑成等长”。本轮默认不对可变长度结果报告 KI；若以后需要机会校正的变长稳定性指标，须另选有理论依据的方法并在结果前确定。确定性 Filter 在相同训练数据上反复得到同一集合，其 Jaccard 为 1 只说明没有运行随机性，不说明对训练样本扰动也稳定。

**描述性高频签名。** 在每个固定外层训练折的 10 次运行中，选择频次至少 7 次的特征可标为“70% 高频共识特征”，不得称为统计显著共识或已验证临床标志物。不能依据外层得分挑选签名或阈值；跨折出现频次另作描述，不与同条件运行稳定性混为一谈。若参与后续功能富集，仍须遵守芯片背景映射与多重比较规则。

**已知真值时的恢复指标。** 只有在前述列级真值入口通过后，才报告已知信息维度的恢复比例与单次所选噪声比例。单次噪声选择比例是 realized false discovery proportion，不是富集分析的 q 值；在预定重复协议下对其求均值才可作为 FDR 的经验估计，不由 MI 分组替代真实标签。

---

## 🚀 八、 候选快速评价实现设计与前置等价性准入规程 (Candidate Fast 3-NN Design & Pre-Deployment Verification Protocol)

在补充实验的大规模运行中，为了在**保证评价结果与官方实现严格一致**的前提下合理优化运行效率，本节确立以下**三项工程提速与验证规范**：
1. **候选快速 3-NN 前置准入与验收规程**（以原生 float64 精度、稳定局部排序、完整多维指标为设计基础；确立“逐样本预测完全一致与排序保序”的前置验收门槛，待验证通过后方可准入）；
2. **严格单层进程并发与线程隔离体系**（外层任务级进程调度，MKL/BLAS 与下游分类器强制单线程，防范线程过度订阅）；
3. **数据集折划分与确定性随机种子受控固化**（外层/内层划分 JSON 固化共享，种子写入文件持久化记录）。

### 1. 权威基准评价器死锁与加速实现的学术定性
* **官方权威评价器唯一性（Ground-Truth Evaluator）**：
  本文件中包装搜索的 3-NN 评价及其加速等价性校验，以 `code/utils.py:evaluate_subset` 所采用的标准 `sklearn.neighbors.KNeighborsClassifier` 为参考；SVM、RF、NB 与 LDA 的外层迁移评价按各自已锁定的分类器规范执行，不将所有分类器指标统称为 3-NN 输出；
* **严谨学术定性（拒绝未测先吹）**：
  任何基于纯 NumPy 广播或自定义距离矩阵构建的快速评价函数，在完成全面经验验证前，**一律严格定性为“候选加速实现（Candidate Fast Implementation）”，绝对禁止在未经验证前直接声称“绝对等价”或“10~20 倍加速”**。

### 2. 原生向量化加速代码的技术风险解剖与修复准则
原草案中简易向量化代码存在以下四大潜在数理风险，必须逐一在工程层面进行修正与约束：
1. **`float32` 精度截断导致近邻反转（Precision Downcasting Risk）**：
   项目基准数据（`data/`）均以双精度浮点数 `np.float64` 存储。强制转为 `float32` 会损失 29 位有效尾数精度。在微阵列或归一化特征空间中，当两个样本到测试样本的欧氏距离极其接近（如差值在 $10^{-7}$ 数量级）时，`float32` 的数值舍入误差可能颠倒近邻排序，导致近邻集合产生漂移。**修复准则**：候选实现必须严格保留原始数据的连续内存与类型：`dtype=X_train.dtype`（强制维持 `np.float64`）。
2. **`argpartition` 局部非排序与并列投票分歧（Tie-Breaking Inconsistency）**：
   `np.argpartition(dists, k, axis=1)[:, :k]` 仅保证切分出的前 $k$ 个元素小于后续元素，但切分内部是无序的；当存在并列距离时，索引返回顺序不具稳定性；此外，基于 `np.bincount().argmax()` 的多数表决在出现平局时默认返回最小类别标签，可能与 `sklearn` 内部的并列决策机制产生微妙偏差。**修复准则**：在切分出 top-$k$ 候选后，必须执行局部的稳定排序，并严格对齐平局表决规则。
3. **指标返回完整性缺失（Missing Evaluation Metrics）**：
   简易代码仅返回 `acc, preds`，缺乏项目标准评价所需的 `bacc`（Balanced Accuracy）与 `macro_f1`。**修复准则**：候选实现必须补齐混淆矩阵多维指标计算，输出与 `evaluate_subset` 完全对齐的指标字典。
4. **缺失动态 `actual_k` 边界保护（Dynamic Neighbor Guard）**：
   在 `code/utils.py:evaluate_subset` 中，内置了动态保护逻辑：`actual_k = min(k, len(tr))`。在极端小样本或多折切分导致训练集样本数少于 3 个时，若硬编码 `k=3` 会导致越界或逻辑崩溃。**修复准则**：候选实现必须显式包含 `actual_k = min(k, len(X_train))` 动态适配。

### 3. 规范化候选加速实现设计 (Candidate Fast 3-NN Pipeline)
```python
import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score

def candidate_fast_knn_evaluate(X_train, y_train, X_test, y_test, k=3):
    """
    候选极速 3-NN 评价函数 (Candidate Fast 3-NN Implementation):
    1. 保持 X 原生 float64 精度，严禁转为 float32；
    2. 动态 actual_k 保护，与 evaluate_subset 完全对齐；
    3. 返回与标准评价器同构的完整指标 (acc, bacc, macro_f1, preds)。
    """
    N_tr = len(y_train)
    actual_k = min(k, N_tr)
    if actual_k < 1:
        return 0.0, 0.0, 0.0, np.zeros(len(y_test), dtype=int)
    
    # 强制连续内存并保持原生 float64 精度
    X_tr = np.ascontiguousarray(X_train, dtype=X_train.dtype)
    X_te = np.ascontiguousarray(X_test, dtype=X_test.dtype)
    
    # 向量化广播计算平方欧氏距离 (N_test x N_train)
    # (a - b)^2 = a^2 + b^2 - 2ab
    dists = np.sum(X_te**2, axis=1, keepdims=True) + \
            np.sum(X_tr**2, axis=1, keepdims=True).T - \
            2.0 * np.dot(X_te, X_tr.T)
    # 避免由于浮点微小舍入误差出现的负值
    dists = np.maximum(dists, 0.0)
    
    # 稳定提取前 actual_k 个最小近邻并执行局部精确排序
    top_k_part = np.argpartition(dists, actual_k, axis=1)[:, :actual_k]
    # 取出对应距离并在局部进行稳定排序 (保证与 sklearn 的近邻索引顺序严格一致)
    part_dists = np.take_along_axis(dists, top_k_part, axis=1)
    local_sort = np.argsort(part_dists, axis=1)
    top_k_idx = np.take_along_axis(top_k_part, local_sort, axis=1)
    top_k_labels = y_train[top_k_idx]
    
    # 多数表决投票
    preds = np.zeros(len(y_test), dtype=int)
    for i in range(len(y_test)):
        counts = np.bincount(top_k_labels[i])
        preds[i] = counts.argmax()
        
    acc = float(np.mean(preds == y_test))
    bacc = float(balanced_accuracy_score(y_test, preds))
    macro_f1 = float(f1_score(y_test, preds, average='macro', zero_division=0))
    
    return acc, bacc, macro_f1, preds
```

### 4. 候选加速实现前置准入校验规程与门控机制 (Pre-Deployment Verification Protocol & Gatekeeping)
在正式将候选函数投入任何正式实验之前，必须先运行独立的等价性校验脚本（`code/verify_fast_knn.py`），对候选实现与官方权威评价器进行严格比对。

* **核心定性边界：严格区分“验收标准门槛”与“待验证结果”**：
  必须清醒界定：下述六大指标属于**候选加速实现进入正式实验的前置验收门槛（Acceptance Gate Criteria）**，**绝不代表候选实现当前已经被证明具备的既有性质**。在未执行独立验证脚本并取得全量一致测试报告之前，候选实现严格处于“待验证（Pending Verification）”状态，官方标准 `sklearn` 评价器始终作为唯一的合法评价器。**只有在实测完全满足逐样本预测一致、指标误差极小化和排序严格保序的准入标准后，候选实现才被允许进入正式实验。**

1. **基准测试集覆盖（4 大跨尺度代表集）**：
   * `Colon`：$N=62, D=2{,}000$（癌症微阵列，高维极小样本典型代表）；
   * `T1D`：$N=101, D=54{,}675$（超高维极端小样本，维度最高，数值敏感）；
   * `BASEHOCK`：$N=1{,}993, D=4{,}862$（高样本量文本词频稀疏矩阵，近邻距离密集）；
   * `COIL20`：$N=1{,}440, C=20, D=1{,}024$（20 类图像多分类数据集，多类别投票平局检验代表）。
2. **随机掩码大批量抽样测试（$M = 200$ 个掩码 / 数据集，共 800 组）**：
   在每个测试数据集上生成 200 个不同稀疏度梯度的随机特征子集掩码：
   * 极稀疏组（$d \in [5, 30]$）；
   * 中稀疏组（$d \in [50, 200]$）；
   * 密集组（$d \in [500, 2{,}000]$）。
3. **六大前置准入验收标准（Acceptance Criteria）**：
   在 5 折交叉验证的每一个折上，同时运行 `evaluate_subset`（sklearn 权威基准）与 `candidate_fast_knn_evaluate`（候选加速），逐项核验是否达成如下验收条件：
   * ① **逐样本预测向量一致性门槛**：全折全样本预测一致率要求达到 100%，即 $\hat{\mathbf{y}}_{\mathrm{fast}} \equiv \hat{\mathbf{y}}_{\mathrm{sklearn}}$；
   * ② **分类准确率误差门槛**：$|\mathrm{Acc}_{\mathrm{fast}} - \mathrm{Acc}_{\mathrm{sklearn}}| < 10^{-12}$；
   * ③ **平衡准确率误差门槛**：$|\mathrm{BAcc}_{\mathrm{fast}} - \mathrm{BAcc}_{\mathrm{sklearn}}| < 10^{-12}$；
   * ④ **宏平均 F1 误差门槛**：$|\mathrm{Macro\text{-}F1}_{\mathrm{fast}} - \mathrm{Macro\text{-}F1}_{\mathrm{sklearn}}| < 10^{-12}$；
   * ⑤ **候选解适应度排序保序性门槛**：在所有 200 个掩码生成的适应度序列上，Kendall's $\tau = 1.0$ 且 Spearman's $\rho = 1.0$，确保寻优导向不发生任何偏倚；
   * ⑥ **真实硬件加速比测量**：只有在上述前 5 项等价性验收条件完全通过的前提下，方可进入硬件性能测试阶段，实测单次评价的平均微秒/毫秒数，严谨报告真实测得的硬件加速比。
4. **决策门控机制（Decision Gate）**：
   * **准入许可**：若且仅若上述 4 个数据集共 800 组掩码的实测比对**全量满足上述全部验收门槛**，方允许在内部代理损失评估（`eval_fitness_with_t`）中部署启用该加速函数；
   * **安全回退**：若在任何一个数据集、任何一个掩码上出现即使一个样本的预测分歧（未能满足验收标准），**坚决拒绝准入，全流程严格锁定标准 `sklearn` 评价器**。实验依托成熟的掩码哈希缓存机制（`cache_hit_count`）与外层折受控多进程并发架构，在保证计算安全的前提下完成全量实验，切实保障科学实验结果的可信度与学术严谨性。

### 5. 严格单层并发架构与过度订阅防范准则 (Strict Single-Tier Parallelism & Oversubscription Prevention)
针对多层任务调度与多模型评估的工程调度，坚决废弃“默认开启 `n_jobs=-1` 并宣称接近线性加速”的非严谨做法，严格执行单层资源隔离与阶梯测试规程：

1. **多层并行嵌套与线程过度订阅风险解剖 (Thread Oversubscription Hazard)**：
   在真实系统调度中，若盲目开启 `n_jobs=-1` 并使用底层多线程模型，系统极易陷入四重并发嵌套陷阱：
   * (a) 外层折任务级多进程并发；
   * (b) 优化算法多次随机独立运行并发；
   * (c) 随机森林等下游评估模型内部决策树多线程并发（RF `n_jobs`）；
   * (d) NumPy 底层线性代数库（MKL/OpenBLAS/BLAS/OpenMP）多线程并发。
   在 Windows 系统下（采用 `spawn` 进程创建模式），四重并发嵌套将瞬间激活数十至上百个争抢线程，引发灾难性的 **CPU 线程过度订阅（Thread Oversubscription）**、CPU L2/L3 缓存严重颠簸、内存总线带宽饱和与系统假死，实际耗时反而大幅恶化。
2. **唯一合法的“严格单层并行”调度法则 (Single-Tier Parallelism Axiom)**：
   继承并严格遵循工程成熟脚本 `code/run_parallel_experiment.py:32-38` 的调度设计，整套运行框架**只能且仅能在单一层级开启并发**：
   * **并发层级唯一定位**：仅在外层折/任务调度层级使用受控的进程池调度；
   * **底层代数库全面单线程锁死**：在所有进程启动最前端、在导入任何科学计算库之前，强制注入环境变量隔离：
     ```python
     import os
     os.environ["OMP_NUM_THREADS"] = "1"
     os.environ["MKL_NUM_THREADS"] = "1"
     os.environ["OPENBLAS_NUM_THREADS"] = "1"
     os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
     os.environ["NUMEXPR_NUM_THREADS"] = "1"
     ```
   * **下游模型内部单线程强制锁死**：随机森林 `RandomForestClassifier` 等模型内部**严格锁死 `n_jobs=1`**，确保每一个工作进程稳定、恒定地独占 1 个物理 CPU 核心。
3. **阶梯并发基准测试规程（Workers = 1, 2, 4 Scalability Benchmarking Protocol）**：
   坚决杜绝主观断言“接近线性加速”。在正式启动全量挂机前，必须在典型中高维数据集上执行受控的阶梯并发测试，实测 `workers = 1, 2, 4`，并系统性监测记录：
   * ① **总执行耗时（Total Wall-Clock Time）** 与实测边际加速比 $S(p) = T(1) / T(p)$；
   * ② **物理内存峰值占用（Peak Resident Set Size, RSS）**，严防 54,675 维高维数据在多进程下引发内存溢出（OOM）；
   * ③ **CPU 核心综合利用率与线程上下文切换频率**；
   * ④ **Windows 系统下 `spawn` 进程冷启动与模块导入开销**。
   依据实测边际效用曲线，确定兼顾计算效率与系统安全的最优并发数（默认推荐 `workers=2` 或 `4`，严禁盲目打满全部物理/逻辑核心），并结合单折压力测试结果最终核定批处理作业规模，切实规避计算资源耗尽与执行计划失控风险。
4. **环境与确定性随机种子受控固化与历史回溯说明**：
   * **历史实验事实如实说明**：早期正式实验运行代码（`code/run_formal_experiment.py`）中未预设固定种子列表，采用了系统随机数自然流动运行，因此历史单次运行的具体 seed 数值未在输出日志中逐一记录；
   * **修回实验可复现性强制固化**：在当前修回补充实验中，全面升级为确定性实验治理规程：
     1. **固定种子列表**：按 run_idx 读取 `[7, 30, 1, 42, 100, 2024, 999, 1234, 555, 888]` 并重置实际使用的随机数生成器。与第二节一致，不声称按数据集或折派生不同 seed。置换默认仅用其中 seed=7，与真实参照匹配，标签置换另用独立种子；
     2. **划分文件统一**：真实标签评估使用 `output/nested_cv/splits/{dataset}_outer_splits.json` 与 `output/nested_cv/splits/{dataset}_inner_splits_fold{k}.json`，跨算法共享。置换条件按当前标签重建并保存到各自 `output/nested_cv/permutation/{dataset}/perm_{b}/` 下，不覆盖或沿用真实标签分层索引；
     3. **元数据完整记录**：保存 dataset、algo、outer_fold、run_id、seed、数据及标签指纹、划分索引、配置、依赖版本、评价器与硬件信息，用于追溯与复现；不承诺跨平台浮点计算逐位相同。

---
*本文件为补充实验设计规范，不表示代码已完成或结果已获得。执行前须验收请求计数闭合、阶段无关缓存与 TPS 重评、信用分量重构、OOF 与置换统计口径，以及候选评价器等价性；全量规模与并发设置以压力测试为准。历史 20 集、去重 19 集与新增外层评估分别报告，全部结论据实际数据填写。*
