# KDS-EL 论文起草简报 (Drafting Brief)

> 供 draft_writer 代理使用的统一简报。所有起草必须遵守本文件 + `argument_blueprint.md` + `authoritative_numbers.md` + `论文写作.md`。
> 目标期刊: Applied Soft Computing (Elsevier)。LaTeX, Elsevier numbered 引用。

## 1. 必须阅读的文件
- `E:\多目标优化\KDS-EL\paper\paper_outline.md` — 结构 + 段落要点 + 字数分配
- `E:\多目标优化\KDS-EL\paper\argument_blueprint.md` — 论证链 + 语言纪律 + 数字纪律
- `E:\多目标优化\KDS-EL\paper\authoritative_numbers.md` — **唯一合法数字源**
- `E:\多目标优化\KDS-EL\paper\references_master.md` — 文献库 + 引用键
- `E:\多目标优化\KDS-EL\论文写作.md` — 6 条写作法则

## 2. 引用键约定 (Elsevier numbered 最终由 Phase 5 编号)
起草时用 `\cite{key}` 占位。key 定义如下：

| key | 文献 |
|---|---|
| mel2024 | Wang et al., MEL, IEEE TKDE 2024 (DOI 10.1109/TKDE.2024.3366333) |
| kennedy1997 | BPSO (Kennedy & Eberhart 1997) |
| wangjia2022 | FWPSO (Wang & Jia BIBM 2022) |
| wang2022 | SaWDE (Wang et al. KBS 2022) |
| xuezhang2024 | IGPSO (Xue & Zhang SwarmEvo 2024) |
| wei2025 | PSO-CSM (Wei et al. SwarmEvo 2025) |
| deb2002 | NSGA-II (Deb et al. 2002) |
| coello2004 | MOPSO (Coello et al. 2004) |
| zhang2007 | MOEA/D (Zhang & Li 2007) |
| han2024 | fMOPSO (Han et al. NPL 2024) |
| cheng2023 | VGS-MOEA (Cheng et al. TEVC 2023) |
| kennedy1995 | PSO (Kennedy & Eberhart 1995) |
| shi1998 | Modified PSO (Shi & Eberhart 1998) |
| lili2017 | Feature selection survey (Li et al. ACM CSUR 2017) |
| guyon2003 | Guyon & Elisseeff JMLR 2003 |
| kohavi1997 | Kohavi & John AIJ 1997 |
| peng2005 | mRMR (Peng et al. TPAMI 2005) — 需补引 |
| demsar2006 | Demsar, Statistical comparisons of classifiers (JMLR 2006) — 需补引 |
| friedman1940 | Friedman, rank test (Ann. Math. Statist. 1940) — 需补引 |
| holm1979 | Holm-Bonferroni (Scand. J. Stat. 1979) — 需补引 |
| cover1991 | Cover & Thomas, Elements of Information Theory — 需补引 |
| weil2025 | RLPSO (Wei et al. SwarmEvo 2025) |
| chen2025 | DCGA (Chen et al. ESWA 2025) |
| liang2025 | EC biomarker survey (Liang et al. TEVC 2025) |
| xia2026 | ISA-EFS (Xia et al. TEVC 2026) |
| lin2025 | Surrogate gene selection (Lin et al. TEVC 2025) |
| liu2024 | SAEA survey (Liu et al. CIS 2024) |
| ye2026 | KMHBO (Ye et al. ESWA 2026) |
| vgs2022/mel_refs | MEL 论文原有 [1]-[68]（references_master 第一节），用其原编号 [1]~[68] 引用 |

> 注意: MEL 论文原参考文献 [1]-[68] 保留原编号（即正文中写 [4], [12], [23] 等对应 references_master 第一节）。新增引用用上述命名 key，Phase 5 统一编号排序。

## 3. 数字硬约束（违反即返工）
- KDS-EL: **0.9574 Acc / 88 特征**（禁用 0.9442 / 107）
- 消融链路: MEL 0.8868 → MEL+MI 0.9325 → KDS_EL_KER 0.9488 → KDS-EL 0.9574
- 增量: +4.58 / +1.63 / +0.86pp（禁用 +3.89 / +1.42 / +1.07 作为 20-DS 宣称）
- 可选补充（若写）: 全量 25 数据集上 TwoPhase vs NoPool **+1.07pp / 22/25 胜** / 特征 -46 / 时间 -3.6s，措辞必须标注 "full 25-dataset suite"（见 authoritative_numbers.md 补充节）
- vs FWPSO **+3.97pp**，vs W-MOPSO-FS **+4.42pp**，vs #2 **+0.86pp**
- 运行: KDS-EL 51.3s (第2), MEL 175s, 3.4× 加速; MOFS >110s
- Wilcoxon: 20/20 vs MEL, 19/20 vs MEL+MI; Holm: 全部 13 对手显著
- 天花板数据集 (8): ALL1, ALL_AML, Adenoma, DLBCL, Gastric2, Leukaemia, Lymphoma, SRBCT
- 消融逐组件: MI+Reinit +4.58pp(特征2722→291), KER +1.63pp(→122), TwoPhase +0.86pp(→88, 时间54.2→51.3s)
- 参数敏感性: 5 参数波动 ≤1.5pp, MI_init_ratio 最敏感

## 4. 命名纪律
- KER → **Knowledge-guided Elite Refinement (KER) strategy**
- TwoPhase → **Two-Phase Weight Scheduling strategy**
- KDS-EL = KDS_EL_TwoPhase；KDS-EL_KER = KDS_EL_NoPool（消融基线，去两阶段）
- 消融章节标题: **"Component Contribution Analysis"**（不是 Ablation Study）
- 自己的组件用 strategy/mechanism；baseline 的才叫 operator
- 动词: addresses/resolves/incorporates/employs（禁 improved/enhanced/add）
- 不宣称 synergy；用 complementary/independent

## 5. 写作质量要求
- 每个主张必须由引用或本论文数据支撑，禁止编造文献
- 每节一个统一论点（见 blueprint），段落逻辑连贯
- 学术英文，避免 AI 典型套话（delve, crucial, it is important to note）
- 句子节奏变化，段落长度 2-8 句自然变化，禁止 em dash 滥用
- 数学用 LaTeX 公式；表格用 \ref 占位（Phase 7 填真实表格）

## 6. 输出
- 每节写入独立 .tex 文件到 `E:\多目标优化\KDS-EL\paper\sections\`
- 纯节内容（\section 起），不含 documentclass/preamble
- 字数符合 outline 预算（±10%）
