# KDS-EL 消融叙事重构 & 论文推进计划

> 创建日期：2026-07-18 | 更新：2026-07-18（修正 DRS 评估框架：DRS 是多样性算子，不用精度衡量）
> 背景：完成多审稿人审查后，确认消融叙事需要重构。数据本身不差，但评估框架和呈现方式是错的。

---

## 零、根本原则（第一性原理）

**DRS 是多样性维持算子，KER 是精度提升引擎。**

| 模块 | 目标 | 成功标准 | 
|------|------|------|
| **DRS** | 防止种群结构坍缩 | NHD > 0，且不拖累精度 |
| **KER** | 提升分类精度 | ΔAcc > 0 over MEL |

用精度去衡量 DRS 的"贡献"是单位错误——就像用速度评价空调。同理 KER 不贡献多样性（NHD ≡ 0）。

**因此移除以下内容**：
- ❌ Synergy = ΔFull - ΔDRS - ΔKER（加性分解公式，不再使用）
- ❌ "DRS 贡献精度" 的论述（DRS 不贡献精度，它贡献多样性）
- ❌ "两模块协同增强" 的叙事（不在同一维度，不存在协同/加性）

---

## 一、消融现状诊断（修正后）

### DRS 做到了它的设计目标

| 评估 | 证据 | 结论 |
|------|------|:---:|
| DRS 维持多样性 | NHD: 0(MEL)=0(KER) → 0.453(DRS) → 0.310(Full) | ✅ |
| DRS 不拖累精度 | Full Acc ≈ KER Acc (Δ=+0.0020, 几乎无差异) | ✅ |
| DRS alone 的缺陷 | ALL2/ALL3/Stroke 上 DRS 单独负贡献 | 需要 KER 约束 |
| DRS boundary condition | COIL20/ISOLET/madelon 上 Full < KER (3/25) | Discussion 讨论 |

### 剩下的三个反例

| 数据集 | Full | KER | Δ | 原因 |
|--------|------|------|------:|------|
| COIL20 | 0.9809 | 0.9913 | -1.05pp | 天花板效应 |
| ISOLET | 0.8717 | 0.8804 | -0.87pp | 26类多分类 |
| madelon | 0.8445 | 0.8634 | -1.89pp | 人工数据，特征独立 |

---

## 二、新叙事策略

### 消融部分核心回答四个问题

```
Q1: DRS 有用吗？→ 看 NHD。MEL/KER/所有SOTA=0，DRS=0.453，Full=0.310。
    有 DRS 才有正 NHD。

Q2: KER 有用吗？→ 看 Acc。ΔKER=+4.68pp over MEL。几乎全部精度增益来自 KER。

Q3: DRS 拖累 KER 吗？→ Full Acc ≈ KER Acc (Δ=+0.0020)。不拖累。
    DRS 成功维持了多样性且没有精度代价。

Q4: DRS 有没有副作用？→ 3/25 反例，Discussion 中讨论 boundary condition。
```

### 严禁使用的术语

| ❌ 禁止 | ✅ 替代 |
|--------|--------|
| synergy / synergistic / 协同 | 不使用（不同维度，不能加性分解） |
| synergy = ΔFull - ΔDRS - ΔKER | 不使用这个公式 |
| DRS enhances accuracy | DRS maintains diversity without accuracy penalty |

---

## 三、写作执行计划

### Phase 1：消融部分重写（优先级最高）

| 任务 | 内容 | 预估 |
|------|------|:--:|
| 1.1 | 消融数据分组呈现：全量 25DS + 非饱和 13DS + 困难 3DS 三张子表 | 2h |
| 1.2 | 重写 §4.5 Ablation Study 正文（两层论证框架） | 3h |
| 1.3 | 全文搜索 "synerg" 替换为 "complementary"/"complementarity" | 0.5h |
| 1.4 | 全文搜索 "mutual enhancement"、"协同" 清除 | 0.5h |

### Phase 2：新增鲁棒性分析（轻量，不重新跑实验）

| 任务 | 内容 | 预估 |
|------|------|:--:|
| 2.1 | 计算各变体在 25DS 上的 Min Acc、Std、worst-case rank | 1h |
| 2.2 | 在正文中增加 "Robustness" 段落（~200 词） | 1h |
| 2.3 | 可选：生成 Robustness 补充图（箱线图已有 F7，可能已覆盖） | 0.5h |

### Phase 3：论文主体写作

| 任务 | 内容 | 预估 |
|------|------|:--:|
| 3.1 | §5.2 Accuracy（基于已有数据 + T4） | 3h |
| 3.2 | §5.3 Feature Size（基于 T5） | 1.5h |
| 3.3 | §5.4 Ablation（Phase 1 产物） | — |
| 3.4 | §5.5 MOFS Comparison（基于 T8） | 2h |
| 3.5 | §5.6-5.10 各分析小节 | 各 1-2h |
| 3.6 | §5.11 Discussion（ISOLET, COIL20, 天花板效应） | 2h |
| 3.7 | §2 Related Work（~1200 词） | 3h |
| 3.8 | §1 Introduction 更新数值 | 2h |
| 3.9 | §6 Conclusion | 1h |
| 3.10 | Abstract 精修 | 1h |

### Phase 4：收尾

| 任务 | 内容 | 预估 |
|------|------|:--:|
| 4.1 | 替换所有 [CITE_X] 占位符 | 2h |
| 4.2 | 全文命名一致性检查（DRS/KER/KDS-EL） | 1h |
| 4.3 | 表格数字与 CSV 核对 | 1h |
| 4.4 | 交叉引用验证 | 0.5h |

---

## 四、不建议做的事（成本收益比差）

- ❌ 补跑 weight_decay/α_cd/rand_flip_p 单独消融 — 对中等期刊不必要
- ❌ 补跑参数敏感性分析 — 时间成本高，边际收益低
- ❌ 测量 MOFS 方法的 NHD — 有趣但非必需
- ❌ 模拟数据集验证 — 20 个真实数据集足够

---

## 五、投稿前建议的轻量提升（如有余力）

| 优先级 | 任务 | 成本 | 收益 |
|:---:|------|:--:|:---:|
| 低 | KER weight 在 2-3 数据集上与已知 biomarker 交叉验证 | 3h | 增加生物学可信度 |
| 低 | 展示 DRS 使 Full 的 worst-case acc 优于 KER-only | 1h（纯分析） | 强化鲁棒性论证 |
| 极低 | α_cd fixed vs adaptive 迷你消融（只在 3 个困难数据集） | 4h | 回击 "DRS=NSGA-II 换目标" |

---

## 六、总时间估算

| Phase | 内容 | 时间 |
|-------|------|:--:|
| Phase 1 | 消融重构 | 6h |
| Phase 2 | 鲁棒性分析 | 2h |
| Phase 3 | 论文主体写作 | 20h |
| Phase 4 | 收尾 | 4.5h |
| **合计** | | **~32h（约 1 周）** |
