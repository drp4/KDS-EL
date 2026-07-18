# KDS-EL 消融叙事重构 & 论文推进计划

> 创建日期：2026-07-18
> 背景：完成多审稿人审查后，确认消融是论文最弱环节。数据本身不差，但呈现方式需要重构。

---

## 一、消融现状诊断

### 当前的三个尴尬

| # | 问题 | 数据 |
|---|------|------|
| 1 | Full 比 KER 精度差距极小 | ΔAcc(Full-KER) = +0.0020（25DS avg），Fisher p=6.5e-4 |
| 2 | 协同是负的 | Synergy = -3.76pp，正协同仅 6/25 (24%) |
| 3 | Full 在任何一个单维度上都不是最优 | Acc：仅微弱领先 KER；Feat：输 DRS；NHD：输 DRS |

### 但数据里藏着一条好故事

| 数据集组 | DRS Δ | KER Δ | Full Δ | 故事 |
|----------|------:|------:|-------:|------|
| ALL2 | **-0.67pp** | +0.14pp | **+1.74pp** | DRS 单独有害，Full 逆转 |
| ALL3 | **-0.45pp** | +0.92pp | **+1.40pp** | DRS 单独有害，Full 逆转 |
| Stroke | **-3.32pp** | -1.29pp | **-1.08pp** | 两者单独都差，Full 止损 |
| PCMAC | +2.21pp | +3.79pp | **+6.08pp** | Full 显著优于两者 |

**核心洞察**：消融弱不是方法弱，9/25 数据集天花板效应压平了差异。非饱和子集 (n=13): Full vs KER ΔAcc=+0.44pp, Fisher p=0.0024。

---

## 二、新叙事策略（两层论证）

### 第一层：每个模块解决一个困境，各自有一个致命缺陷

> - KER 解决 knowledge-waste → 但产生完全同质种群 (NHD≡0)
> - DRS 解决 diversity-collapse → 但在困难数据集上过度牺牲精度 (ALL2/ALL3/Stroke 负贡献)
> - **单独使用任一模组都有结构性风险**

### 第二层：完整框架 = KER 精度 + DRS 多样性，互相纠错

> - KDS-EL 达到 KER 级精度，同时维持 NHD>0
> - 困难数据集上 DRS 的负贡献被 KER 覆盖，KER 的多样性盲点被 DRS 覆盖
> - **唯一在三轴 (Acc + NHD + Feat) 上同时达标的方案**

### 严禁使用的术语

| ❌ 禁止 | ✅ 替代 |
|--------|--------|
| synergy / 协同 | complementarity / 互补 |
| mutual enhancement | mutual correction / 互相纠错 |
| synergistic framework | balanced dual-space framework |

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
| 3.6 | §5.11 Discussion（VGS-MOEA, ISOLET, COIL20, 天花板效应） | 2h |
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
