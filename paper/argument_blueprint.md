# KDS-EL 论证蓝图 (Argument Blueprint)

> 用途：全文起草的唯一论证依据。融合 `论文写作.md` 的 6 条法则 + `paper/authoritative_numbers.md` 的 20-DS 数字 + `paper/paper_outline.md` 的结构。
> 核心目标：避免审稿人 "incremental addition" 批评。

---

## 一、核心论点 (Thesis)

**通用 PSO 在特征选择上存在三个结构性不适配，导致知识浪费、搜索刚性、探索-利用失衡。KDS-EL 通过三个互补机制逐一解决，在高维特征选择上实现"精度-稀疏性-效率"三赢。**

三个机制在同一多任务 PSO 骨架 (MEL) 内独立运作于不同层面（知识层 / 调度层 / 生命周期层），互不覆盖，各自可消融验证。

## 二、问题链 (Problem Chain) — 全文叙事的脊柱

```
问题 1: 知识浪费 — 随机初始化在高维稀疏解空间浪费搜索预算
  → 互信息排序提供高质量起点 → MI 引导初始化 + 自适应重初始化
问题 2: 特征重要性被忽略 — 传统翻转/变异算子均匀随机，不利用历史知识
  → 累积特征权重矩阵 + KER 精英翻转（90% 知识引导 / 10% 随机探索）
问题 3: 刚性调度 — 精度与特征数双目标权重全程固定
  → 两阶段权重调度（Phase1 激进压缩 / Phase2 精细调精度）
```

**论证基调**（法则 2, 6）：永远说 "KDS-EL incorporates / addresses / resolves"，不说 "We add X to MEL" / "improved" / "operator"。MEL 是 backbone，不单独成节。

## 三、主张-证据链 (Claim-Evidence Chains)

### 主张 A: MI 引导初始化解决冷启动（生命周期层）
- 证据（w/o 减法读法）: 去掉 MI 初始化+自适应重初始化 → MEL 残骸，**−4.58pp**，特征 291→2722（膨胀一个数量级），20-DS
- 参数佐证: MI_init_ratio 关闭 (0.0) 降 1.2pp 且时间 +21%（最敏感参数）
- 定位: 标准 filter-wrapper 操作，不列为核心创新，但构成后续的地基

### 主张 B: KER 解决知识浪费（核心创新 #1，知识层）
- 证据（w/o 减法读法）: 再去掉 KER → MI variant，**−1.63pp**，特征 122→291
- 关键卖点: KER 是**零评估开销**的机制（仅精英翻转，不新增 KNN 评估）
- 机制: 跨迭代累积 improvement-feedback 权重 W + 指数衰减(0.99) 防陈旧；90% 知识翻转 / 10% 随机保证遍历性
- 参数佐证: flip_frac 最优 0.01（每 100 维翻 1 个特征）

### 主张 C: 两阶段调度解决刚性权重（核心创新 #2，调度层）
- 证据（w/o 减法读法）: 去掉两阶段调度 → MI+KER variant，**−0.86pp**，特征 88→122，时间 51.3→54.2s，同批直接对比
- 机制依据: FS 问题的结构特性 — 噪声排除早期一次性，精度提升后期持续；"先粗后精"优于固定权重
- 参数佐证: PhaseSplit 最优 0.7，稳定 [0.6, 0.8]

### 主张 D: 组合实现 SOTA 级性能
- 证据（20-DS）: KDS-EL **0.9574 Acc / 88 特征**，14 方法排第 1
- vs FWPSO（最强单目标）**+3.97pp**；vs W-MOPSO-FS（最强 MOFS）**+4.42pp**
- 统计显著性: Wilcoxon 20/20 优于 MEL、19/20 优于 MEL+MI；Holm-Bonferroni 对全部 13 对手显著
- 效率: 51.3s 第 2 快，相对 MEL 3.4× 加速
- 稀疏性: 平均选择率 ~2-3%（88/平均维度），Pareto 意义上同时提升精度与压缩

## 四、对立论证处理 (Counter-argument Handling)

| 审稿人可能质疑 | 回应策略 |
|---|---|
| "incremental addition"（就是 MEL 加两个模块） | 问题驱动叙事：三个不适配是通用 PSO 的结构性缺陷，KDS-EL 逐一解决；两个核心创新在不同维度独立验证 |
| 天花板数据集 (8 个 Acc≥0.998) 无区分度 | 专节 6.4：精度饱和时用特征数区分，KDS-EL 选 39~83 特征 vs 对手数百至数千 |
| 在 ALL1/COIL20/SRBCT 非最优（对手达 1.0） | 诚实承认，归因天花板效应；不掩盖，说明这些数据集精度差异 <0.002（1-2 个样本） |
| W-MOPSO-FS 无出处 | 明确为自建 baseline（Wrapper-Filter 混合 MOPSO），Related Work 描述实现细节，不冒充已发表算法 |
| ISOLET/COIL20 等数据集 KDS-EL 非最优 | 在正文如实报告，用统计检验（Wilcoxon/Holm）支撑整体优势而非单点最优 |
| 为什么消融用 20 数据集而非 25 | 主表/排名统一 20-DS 口径（SOTA/MOFS 只在 20-DS 上运行），消融链与主表同口径避免跨集合不公平比较；全量 25-DS 的 TwoPhase 验证（+1.07pp, 22/25 胜）仅作清晰标注的鲁棒性补充证据，不参与主表计算 |
| 参数敏感性只在 4 数据集 | 说明 4 个代表数据集覆盖小样本基因/中等/高维文本场景；默认值波动 ≤1.5pp |

## 五、语言纪律（法则 1, 6）— 起草时严格执行

- ✅ KER → **Knowledge-guided Elite Refinement (KER) strategy/mechanism**
- ✅ TwoPhase → **Two-Phase Weight Scheduling strategy**
- ❌ 禁用自己的组件叫 "operator"（baseline 的才叫 operator）
- ✅ addresses/resolves/incorporates/employs  |  ❌ improved/enhanced/add
- ✅ building upon the multi-task PSO backbone  |  ❌ based on MEL
- ✅ complementary/independent  |  ❌ synergy/synergistic（旧版教训）
- ✅ Component Contribution Analysis  |  ❌ Ablation Study（章节标题）
- ✅ 14 fixed-length methods  |  ❌ 15 methods

## 六、数字纪律（见 authoritative_numbers.md）

- 唯一合法聚合数字: 0.9574 / 88 特征 / +0.86 / +3.97 / +4.42 / +4.58 / +1.63 / +0.86 / +7.06 / 51.3s / 3.4× / 20/20 / 19/20
- 禁止（作为全局/20-DS 宣称）: 0.9442 / 107 / +1.08 / +2.65 / +3.10 / +3.89 / +1.42 / +1.07 / 6.38 / 18/25 / 25DS
- 例外: **+1.07pp / 22/25 胜** 可作为"full 25-dataset suite"鲁棒性补充证据（措辞必须明确标注 25 集，见 authoritative_numbers.md 补充节）
- 消融链路 (20-DS, w/o 减法读法): KDS-EL 0.9574 → 去 TwoPhase (MI+KER) 0.9488 → 去 KER (MI) 0.9325 → 全剥 (MEL) 0.8868
- 特征链路: 88 → 122 → 291 → 2722

## 七、消融叙事（法则 4, w/o 减法读法, 三层次）

1. 每个组件都配得上存在（去掉哪个都掉）：去 TwoPhase −0.86pp, 再剥 KER −1.63pp, 再剥 MI −4.58pp
2. 各贡献在不同维度: MI=起点+压缩, KER=精度(零评估开销), TwoPhase=三维提升
3. 全剥（MEL 残骸）: 累计 −7.06pp, 特征 88→2722 膨胀 ~30×
- 标题用 "Component Contribution Analysis"，**w/o 减法读法（2026-08-04 决定）**
- 对比表方法名保留 "MI variant / MI+KER variant"，§7 开头加映射句
- 不宣称 synergy；KER 和 TwoPhase 是独立可验证的互补贡献
