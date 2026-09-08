# AGENTS.md — KDS-EL Academic Writing, Rigor & Elsevier Submission Protocols

This document defines the strict academic standards, mathematical conventions, experimental protocols, and Elsevier-specific submission guidelines governing all writing, revising, and LaTeX code generation for the **KDS-EL** research paper targeting top-tier Elsevier SCI journals (e.g., *Applied Soft Computing* [ASOC], *Expert Systems with Applications* [ESWA], *Swarm and Evolutionary Computation* [SWEVO], *Information Sciences*, *Knowledge-Based Systems*).

Every generation and modification must strictly comply with all criteria outlined below.

---

## 📌 Section I: Core Academic Writing & Narrative Protocols

### Pillar 1: Zero Parenthetical Clutter & Duplicate Acronyms
- **No Duplicate Acronym Expansions**: Once an acronym (e.g., `KDS-EL`, `KER`, `TPS`, `PSO`, `MI`) is defined in the Abstract/Introduction, do not expand it again with parenthetical tags like `Knowledge-Guided Elite Refinement (KER)`. Use the formal terms directly (e.g., `the KER strategy`, `the dynamic TPS strategy`, `the MII mechanism`).
- **Strict Prohibition of "Operator" for Proposed Components**: Strictly prohibit referring to KDS-EL's own constituent components as an `operator` (e.g., never write `KER operator`, `refinement operator`, or `our operators`). KDS-EL's components must strictly be termed `strategy` or `mechanism` (e.g., `the KER strategy`, `the elite refinement mechanism`, `the dynamic TPS strategy`). The term `operator` is reserved exclusively for standard low-level genetic/evolutionary heuristics of peer algorithms (e.g., `crossover operator`, `stochastic bit-flip operator`, `swarm variation operators`).
- **No Premature Parameter Dumping**: In high-level architecture/framework sections (such as Section 3.1), never hardcode specific hyperparameter values (e.g., `(wf,1 = 0.30)`, `(wa,2 = 0.95)`, `(theta = 0.60)`) or inline formula fragments in parentheses. Specific parameter values belong strictly in dedicated technical subsections and the experimental parameter setup table.
- **Eliminate Pseudo-Code Conditions in Text**: Never write parenthetical code-like logic in prose (e.g., `(rank(i) <= N/2)` or `(MI_init_ratio = 0.50)`). Translate them into rigorous academic English (e.g., *"the superior half of the swarm is preserved intact..."*).

---

### Pillar 2: Natural Pipeline Narrative & Paragraph Density (Zero Bullet-Point Syndrome)
- **Eliminate Mechanical Bullet Lists & Itemize Environments**: In main text and conceptual reviews (especially Section 2), strictly avoid breaking text into bulleted `\begin{itemize}` / `\begin{enumerate}` lists or short, choppy 1--2 sentence paragraphs. Maintain dense, coherent, narrative-driven paragraphs (strictly 3 to 4 substantial paragraphs per subsection, perfectly mirroring EMSWOA).
- **Prohibit Continuous Bullet-Point Responses in Dialogue**: In all agent-user interactions, avoid mechanical bullet-point itemization (`1. ... 2. ... 3. ...`); articulate explanations, comparisons, and rationale through structured, analytical prose paragraphs.
- **Use Dynamic Pipeline Verbs**: Drive the narrative using progressive, cause-and-effect pipeline verbs:
  $$\text{quantify} \longrightarrow \text{normalize} \longrightarrow \text{construct / initialize} \longrightarrow \text{transform / binarize} \longrightarrow \text{harvest / accumulate} \longrightarrow \text{refine} \longrightarrow \text{recover}$$
- **Natural Temporal Connectors**: Use phrases such as *"The search begins by..."*, *"An initial population is subsequently generated via..."*, *"Throughout evolution, the subpopulations undergo..."*, *"Upon meeting the stopping criterion, the algorithm outputs..."*.

---

### Pillar 3: "Why Before How" (Physical Motivation Precedes Formulas)
- **Never Introduce an Isolated Formula**: Before presenting any mathematical equation, explain:
  1. The **physical bottleneck or search degeneration** encountered by traditional methods in ultra-high-dimensional spaces ($D \gg 10^3$);
  2. The **design rationale** of the proposed strategy;
  3. The formal mathematical formulation;
  4. The boundary behaviors and physical interpretation of the variables.

---

### Pillar 4: Mathematical Typography & Domain Completeness
- **Explicit Domain Definition**: Every vector, matrix, scalar, and set must have its mathematical space explicitly defined upon first appearance ($\mathbf{X} \in \{0, 1\}^{N \times D}$, $\mathbf{W} \in \mathbb{R}^D$, $\mathbf{m} \in [0, 1]^D$, $\gamma \in (0, 1)$).
- **Standard LaTeX Typography**:
  - **Matrices**: Bold uppercase roman ($\mathbf{X}, \mathbf{W}$).
  - **Vectors**: Bold lowercase roman ($\mathbf{x}_i, \mathbf{p}_i, \mathbf{m}, \boldsymbol{\varepsilon}_i$).
  - **Scalars / Parameters**: Italic lowercase ($x_{i,j}, p_{i,j}, N, D, T, \theta, \gamma, \tau, \rho, \phi, \kappa$).
  - **Sets / Populations**: Calligraphic uppercase ($\mathcal{P}_1, \mathcal{P}_2, \mathcal{D}, \mathcal{S}_{\mathrm{know}}, \mathcal{S}_{\mathrm{rand}}$).
  - **Standard Functions / Operators**: Upright roman ($\min, \max, \arg\max, \mathrm{clip}(\cdot), \mathbb{I}(\cdot), \mathrm{Acc}(\cdot)$).
- **Consistency in Vector Orientation**: If candidate solutions $\mathbf{x}_i = [x_{i,1}, \dots, x_{i,D}]$ are row vectors of $\mathbf{X}$, do not randomly add transpose signs $\mathbf{x}_i^T$ unless performing dot products or matrix transpositions.

---

### Pillar 5: Deep Figure-Table Linkage & Self-Containment
- **Figure/Table Self-Containment**: Captions must be descriptive enough that a reader can grasp the core mechanism purely from the visual artifact (complying strictly with Section V, Protocol CAP-2: self-contained 20–50 words structured into global subject, sub-panel guide, and visual cue decoding).
- **Exact Symbol Matching**: Symbols within PDF figures (`F1`, `F2`, `F3`, `F8`, `F14`) must match the in-text LaTeX math notation 100%.
- **Directional Referencing**: Direct the reader to specific visual pathways within figures (e.g., *"As illustrated in the adaptive recovery branch of Fig.~2..."*, *"As depicted in Branch 2 of the KER flowchart in Fig.~3..."*).

---

### Pillar 6: Standardized Algorithmic Pseudocode
- **Complete Require / Ensure**: `\Require` must declare all inputs, dimensions, and hyperparameters with mathematical domains; `\Ensure` must declare the optimal feature subset $\mathbf{x}^{\star}$ and optimal fitness $f_{\mathrm{gbest}}$.
- **Stage-Wise Segmentation**: Group pseudocode into clear functional blocks using `\Statex \textbf{Stage 1: ...}`.
- **Hierarchical Modular Design**: Complex sub-routines (e.g., KER) must be formalized as self-contained sub-algorithms (`Algorithm 1`), while the main coordination framework remains concise (`Algorithm 2`).

---

### Pillar 7: Comprehensive Complexity Closed-Loop
- **Decouple Offline & Online Costs**: Separate one-time preprocessing $\mathcal{T}_{\mathrm{pre}} = \mathcal{O}(D N_{\mathrm{samp}} + D \log D)$ from generational evaluations $\mathcal{T}_{\mathrm{eval}} = \mathcal{O}(N N_{\mathrm{samp}}^2 d_{\mathrm{selected}})$.
- **Time & Space Asymptotic Completeness**: Provide both time complexity $\mathcal{O}(T N N_{\mathrm{samp}}^2 d_{\mathrm{selected}})$ and linear space complexity $\mathcal{S}_{\mathrm{total}} = \mathcal{O}((N + N_{\mathrm{samp}})D)$.
- **Empirical Wall-Clock Speedup Rationale**: Explicitly explain why identical Big-$\mathcal{O}$ order yields a $3.4\times$ real-world speedup (active feature compression from $d_{\mathrm{MEL}} \approx 2{,}722$ to $d_{\mathrm{KDS-EL}} \approx 88$, with $k$-NN distance cost scaling linearly with $d_{\mathrm{selected}}$).

---

### Pillar 8: Measured Academic Tone & Tight Causality
- **Zero Promotional Fluff**: Strictly avoid unscientific subjective terms (`revolutionary`, `miraculous`, `flawless`, `unprecedented`).
- **Precision Causality**: Use precise inferential connectors:
  - *Mitigation*: `effectively mitigates`, `substantially alleviates`, `suppresses`.
  - *Improvement*: `significantly improves`, `consistently outperforms`.
  - *Causality*: `thereby facilitating...`, `consequently avoiding...`, `which in turn accelerates...`.
- **Strict Prohibition of the Term "Baseline"**: Strictly prohibit the words `baseline` / `baselines` across all LaTeX manuscript text, table captions, table footnotes, and agent dialogue responses. Peer algorithms must never be casually or dismissively labeled as "baselines" or "baseline MEL". Adhere strictly to formal scholarly terminology:
  - *For peer algorithms*: `competitor algorithms`, `competing methods`, `comparison approaches`, `peer algorithms`, `counterparts`, `benchmark methods`.
  - *For the backbone algorithm MEL*: `the original MEL algorithm`, `the foundational MEL framework`, or directly `MEL` (never `baseline MEL`, `MEL baseline`, or `precursor MEL`, perfectly aligning with EMSWOA's treatment of its base algorithm WOA as `the original WOA` or `the basic WOA`).
  - *For unreduced data / raw feature sets*: `unreduced full-dimensional feature sets`, `raw feature spaces` (never `full-dimensional baselines`).
  - *For reference fitness / starting levels*: `initial fitness value`, `initial reference fitness` (never `fitness baseline`).
  - *For algorithmic comparison collections*: `comparison suite`, `benchmark suite`, `competitor suite` (never `baseline suite`).

---

## 📌 Section II: Elsevier-Specific Submission & Formatting Standards

### Pillar 9: Elsevier Article Class & Metadata Standards (`elsarticle`)
- **Document Class Setup**: Use standard `\documentclass[5p,times,twocolumn]{elsarticle}`.
- **Author & Affiliation Block**: Declare affiliations using `\address[label]{...}` and specify the corresponding author using `\cortext[cor1]{Corresponding author. Email: ...}`.
- **Highlights Protocol**: Provide exactly 3 to 5 highlights in bullet points. Each bullet must be strictly **under 85 characters** (including spaces) and convey a quantifiable core innovation.
- **Abstract Word Limit**: Keep the abstract strictly within 150–250 words, structured into *Background $\to$ Problem & Limitations $\to$ Proposed Framework $\to$ Key Quantified Results $\to$ Broad Impact*.
- **Keywords**: Provide 4 to 6 indexed keywords separated by `\sep` (e.g., `Feature selection \sep Swarm intelligence \sep Particle swarm optimization \sep High-dimensional data \sep Transfer learning`).

---

### Pillar 10: Elsevier Table Design Protocols (Strict Three-Line Tables)
- **Table Caption & Footnote Decoupling**: Captions placed strictly above tables must be ultra-concise noun phrases of 6–15 words defining only the entity and comparison scope, strictly adhering to Section V (Protocol CAP-1). All definitions of boldface, underline, statistical testing notation, and parameter symbols must reside strictly in the table footnote (`\par\raggedright\footnotesize`) below the table.
- **Zero Vertical Lines**: In accordance with Elsevier style guides, **never include vertical rules (`|`)** in tables.
- **Booktabs Macros**: Construct all tables using `\toprule`, `\midrule`, and `\bottomrule` from the `booktabs` package.
- **Statistical Significance Highlighting**: Highlight the best-performing metric in **boldface** and underline the second-best across all comparison tables.
- **Multi-Row & Column Sizing**: Use `\cmidrule(lr){...}` to separate grouped benchmark categories (e.g., Single-Objective vs. Multi-Objective FS).

---

### Pillar 11: Statistical Testing and Evaluation Protocols for Evolutionary Feature Selection
- **Independent Runs & High-Dimensional Benchmark Alignment**: In ultra-high-dimensional wrapper feature selection ($D \gg 10^3$) where fitness evaluation requires repeated $k$-fold cross-validation across thousands of dimensions, report quantitative metrics across 10 independent runs (corresponding to 50 distinct cross-validation folds per dataset) in the standard format: $\mathrm{Mean} \pm \mathrm{Std}$. This protocol strictly mirrors the benchmark standard established in top-tier high-dimensional feature selection literature (e.g., MEL, *IEEE Transactions on Knowledge and Data Engineering* 2024), ensuring fair and computationally feasible comparisons across extensive comparison suites. For lightweight continuous benchmark suites with low-cost analytical evaluation, 30 runs remains the classical standard.
- **Multi-Dataset Non-Parametric Testing (Demšar Protocol)**: To evaluate statistical significance across benchmarks, strictly follow the multi-problem statistical framework of Demšar (2006). Pairwise Wilcoxon signed-rank tests at $\alpha = 0.05$ assess directional superiority across the $N=20$ benchmark datasets, reporting pairwise counts as $+ / - / \approx$ (win / tie / loss).
- **Friedman Global Ranking & Family-Wise Error Correction**: Apply the Friedman test across the multi-dataset benchmark suite to establish omnibus algorithmic rankings, accompanied by post-hoc **Holm-Bonferroni** step-down correction to rigorously guard against family-wise type I error inflation across all competitor comparisons.

---

### Pillar 12: Vector Figures & Resolution Standards
- **Vector PDF Format**: All workflow schematics, convergence curves, and radar plots must be generated and embedded as vector PDFs (`.pdf`), never raster images (`.png` / `.jpg`).
- **Standardized Multi-Panel Layout**: Multi-part figures must use `\begin{subfigure}` with standardized sub-labels `(a)`, `(b)`, `(c)` and synchronized aspect ratios.
- **Font & Linewidth Legibility**: Minimum font size within figures must remain fully legible ($> 7\text{ pt}$) when scaled to single-column width ($8.5\text{ cm}$) or full double-column width ($17.5\text{ cm}$).

---

### Pillar 13: Literature Benchmark Coverage & Citation Freshness
- **Balanced Competitor Hierarchy**: Benchmark against three distinct categories:
  1. *Classical filter & wrapper methods* (e.g., BPSO, IG-PSO);
  2. *State-of-the-art Single-Objective Swarm Feature Selectors* (e.g., SaWDE, MEL);
  3. *State-of-the-art Multi-Objective Evolutionary Algorithms* (e.g., NSGA-II-FS, MOEA/D-FS, W-MOPSO-FS, fMOPSO-FS).
- **Recent Literature Density**: Ensure at least $30\%$ of cited references are from top-tier venues published within the last 3–4 years (2022–2026).
- **BibTeX Completeness**: Every reference must include complete author lists, journal title, volume, issue, page range, year, and DOI where applicable.

---

## 📌 Section III: Specialized Protocols for Section 2 (Related Work & Background)

*These protocols must be strictly enforced whenever drafting, modifying, or reviewing Section 2.*

### 🎯 Core Mission & Philosophical Positioning
- **Not a Bibliographic Catalog**: Related Work must never read like a passive list of disconnected summaries ("Author A did X; Author B did Y").
- **Target-Setting & Runway-Building**: The primary function of Section 2 is to construct the motivation landscape, pinpoint the exact structural bottlenecks of existing paradigms under ultra-high-dimensional and sample-scarce regimes ($D \gg 10^3, N_{\mathrm{samp}} \ll 100$), and establish the theoretical necessity of KDS-EL.

### 🔑 Critical Operational Protocols

#### Protocol RW-1: Critical 4-Step Narrative Chain (Narrative over Listing)
Every thematic subsection must execute a coherent 4-step progressive narrative:
1. **Mainstream Paradigm & Merits**: What is the core mechanism and theoretical advantage of this class of methods?
2. **Physical/Mathematical Bottleneck in Ultra-High Dimensions ($D \gg 10^3$)**: Why does it degrade or fail under $D \gg 10^3$ and small sample sizes? (e.g., filter hard truncation permanently discards feature synergy; standard BPSO with Sigmoid mapping generates overly dense subsets $d \approx D/2$; MOFS non-dominated sorting suffers Pareto archive bloat and retains thousands of redundant features).
3. **Limitations of Existing Remedies**: Why do previous incremental fixes (e.g., one-shot offline MI injection, static filter pre-selection, black-box surrogate models) remain insufficient? (e.g., lacking online feedback adaptation, high surrogate training overhead, severe model misspecification risk).
4. **Theoretical Rationale for the Proposed Design**: How does KDS-EL's design philosophy fundamentally resolve this specific dilemma?

#### Protocol RW-2: Exact 1-to-1 Problem-Solution Closed Loop
Section 2 must establish three explicit, non-overlapping motivation gaps that directly map to the three core components in Sections 3 and 4:
- **Gap 1 (Initial Search Blindness & Diversity Loss)** $\longleftrightarrow$ **MII + AIR**: Mutual-information continuous soft prior initialization coupled with adaptive diversity re-initialization upon stagnation.
- **Gap 2 (Discarded Iteration Feedback & Memoryless Perturbation)** $\longleftrightarrow$ **Dynamic Feature Importance Memory + KER**: Closed-loop accumulation of historical fitness feedback with exponential forgetting, driving targeted directional elite refinement within bounded computation ($k_e \ll N$).
- **Gap 3 (Rigid Static Weighting & Evolutionary Phase Misalignment)** $\longleftrightarrow$ **Two-Phase Weight Scheduling (TPS)**: Temporally decoupling coarse dimensional pruning in Phase 1 from fine accuracy refinement in Phase 2.

#### Protocol RW-3: 100% Benchmark Competitor Anchoring
- **Zero Orphan Competitor Algorithms**: All comparison algorithms evaluated in the experimental sections (BPSO, FWPSO, PSO-CSM, SaWDE, IGPSO, W-MOPSO-FS, fMOPSO-FS, NSGA-II-FS, MOEA/D-FS, MOPSO-FS, MEL) must be explicitly classified, contextualized, and cited in Section 2.
- No competitor algorithm may appear in Section 5 or Section 6 without prior taxonomic grounding in Section 2.

#### Protocol RW-4: Measured Academic Critique & Structural Trade-Offs
- **No Subjective Dismissals**: Avoid non-academic assertions such as "fails completely" or "is useless".
- **Mathematical & Structural Grounding**: Frame all critiques through precise algorithmic trade-offs (e.g., *"incurs Pareto archive bloat"*, *"discards subtle feature synergy"*, *"lacks online dynamic adaptability"*, *"exhibits severe variance in stochastic binarization"*).

#### Protocol RW-5: Orthogonal Taxonomy Table Design (Table 1)
- **Multi-Dimensional Orthogonality**: The taxonomy table (`tab:comparison_literature`) must systematically contrast algorithms across mutually independent technical dimensions: *Paradigm, Prior Seeding, Online Memory, Memory Decay, Elite Refinement, Dynamic Weighting, and Computational Complexity*.
- **Elsevier Compliance**: Strict three-line table format (`\toprule`, `\midrule`, `\bottomrule`), zero vertical lines, with standardized indicators ($\checkmark$: Fully supported, $\circ$: Partially supported, $\times$: Absent / not supported).

#### Protocol RW-6: Zero Premature Parameter Dumping & Math Purposefulness
- **No Hardcoded Hyperparameters**: Do not leak specific internal tuning values (e.g., $\theta=0.60, w_f=0.30, k_e=3, \gamma=0.99$) into Section 2 prose. Use conceptual and mathematical terms; save numerical specifications for Sections 3, 4, and 5.
- **Formulas Must Serve the Critique**: Mathematical equations (e.g., standard PSO velocity/position, mutual information) must immediately connect to the structural failure mode analysis rather than functioning as isolated textbook filler.

---

## 📌 Section IV: Hierarchical Section-Wise Data-Boundary & Anti-Dumping Protocols (各章节数据与数值边界分级规范)

*These protocols must be strictly enforced whenever drafting, modifying, or reviewing any section of the manuscript. Before modifying any text, the agent must explicitly identify the chapter/section, inspect whether data is already dumped, and enforce the corresponding tier.*

### 🎯 Core Mission: "Tables & Figures Host the Data; Text Explains the Mechanisms"
The primary defect of amateur evolutionary computation manuscripts is "Table Regurgitation" (报账式写作) — reciting table cells, float numbers, seconds, and percentages inside text paragraphs. In top-tier Elsevier journals (mirroring EMSWOA in *Applied Soft Computing*), tables and figures are the sole designated hosts for granular empirical data. The running text exists strictly to synthesize high-level behavioral trends, guide the reader through the visual artifacts, and articulate underlying causal and physical mechanisms.

### 🔑 Four-Tier Data-Boundary Hierarchy

#### Tier 1: Absolutely Zero Experimental Data (Strictly Zero Data / 绝对禁水区)
- **Applicable Sections**: Section 2 (Related Work & Preliminaries) and Section 3 (The Proposed KDS-EL Framework).
- **Strict Prohibition**: Zero experimental results, zero empirical test metrics, zero forward-looking performance spoilers (strictly no mentions of 0.9574 accuracy, 87.8 features, 51.3\,s runtime, 3.4$\times$ speedup, or win/tie/loss counts).
- **Allowed Numerical Content**: Pure mathematical formulations, algorithmic state conditions, standard mathematical constants (e.g., $S(0) = 0.5$), Big-$\mathcal{O}$ asymptotic bounds, and high-level dimension orders of magnitude ($D \gg 10^3$, $N_{\mathrm{samp}} \ll 100$).

#### Tier 2: Landmark Global Milestone Metrics Only (宏观标志性核心指标区)
- **Applicable Sections**: Abstract, Highlights, Section 1 (Introduction), and Section 5 (Conclusion).
- **Strict Limitation**: Limited strictly to 2–3 macro omnibus landmark metrics representing the highest aggregate achievement of the entire paper:
  - Omnibus mean classification accuracy ($0.9574$ or $95.74\%$).
  - Omnibus mean selected feature cardinality ($87.8$ features, $>98\%$ compression).
  - Empirical speedup over the foundational MEL framework ($3.4\times$ acceleration).
- **Strict Prohibition**: Never recite per-dataset results, never list individual competitor accuracy values or runtime numbers, and never enumerate granular benchmark subsets.

#### Tier 3: Static Benchmarking & Configuration Constants Only (实验环境与参数配置区)
- **Applicable Section**: Section 4.1 (Experimental Setup).
- **Strict Limitation**: Only declare static benchmarking configuration constants: 20 benchmark datasets, 10 independent runs, 5-fold stratified cross-validation, 3-NN classifier, and default hyperparameter values defined in Table 3.
- **Strict Prohibition**: Absolutely zero post-hoc experimental test outcomes or performance values.

#### Tier 4: Mechanism-Driven & Insight-Focused Empirical Sections (机理驱动的实验分析区)
- **Applicable Section**: Section 4.2 (Experimental Analysis subsections 4.2.1 through 4.2.8).
- **Operational Rule for Each Subsection**:
  - **4.2.1 (Classification Accuracy)**: Report only the omnibus mean ($0.9574$) and overall directional superiority; explain the discriminative geometry in high dimensions; **strictly prohibit reciting per-dataset accuracy numbers for individual datasets**.
  - **4.2.2 (Feature Subset Size)**: Report only the omnibus average ($87.8$) and compression ratio ($>98\%$); explain the physical reason why unguided binarization collapses into the $D/2$ attractor and how two-phase scheduling resolves it; **do not enumerate feature numbers across individual datasets**.
  - **4.2.3 (Convergence Dynamics)**: Zero floating-point data recitation; strictly describe trajectory slopes, early rapid descent, avoidance of exploratory plateaus, and sustained escape from local minima based on Fig.~5.
  - **4.2.4 (Statistical Significance)**: State nominal $\alpha=0.05$ and overall ranking leadership; leave the full pairwise matrix to Table 6 and adjusted $p$-values to Table 7; **do not narrate the entire table cell by cell**.
  - **4.2.5 (Before/After Improvement)**: Strictly mirror EMSWOA Section 4.2.5 (exactly 3 paragraphs, zero parenthetical numerical clutter, zero laundry lists); guide the reader to Table 8 and Fig.~7/8, focusing entirely on the orthogonal theoretical synergy of MII+AIR, KER, and TPS.
  - **4.2.6 (Runtime & Efficiency)**: Report only the omnibus runtime ($51.3$\,s) and the $3.4\times$ speedup; dedicate prose to the asymptotic physical cause (the $k$-NN distance evaluation cost scaling linearly with selected feature cardinality $d_{\mathrm{selected}}$); **strictly prohibit reciting runtime seconds across individual datasets or listing numbers for each competitor**.
  - **4.2.7 (Parameter Sensitivity)**: Report only recommended optimal values and stable operating intervals (e.g., $\kappa \in [0.60, 0.80]$, maximum variation $\le 1.5\%$); leave all detailed grid values to Table 8 and Fig.~11.
  - **4.2.8 (Discussion & Ceiling Effects)**: State the ceiling saturation threshold ($>0.998$) and the representative sparse subset range ($39$ to $83$ features); focus on translational biology, RT-qPCR viability, and pathway enrichment, rather than listing feature counts for all peer algorithms.

### 🛠️ Mandatory Pre-Edit Protocol: "Section Identification & Data-Dumping Audit"
Before generating or applying any text edit to the manuscript:
1. **Identify Section Location**: Explicitly determine the exact chapter and subsection number (e.g., `Section 4.2.6`).
2. **Determine Data Tier**: Check whether the section is Tier 1, Tier 2, Tier 3, or Tier 4.
3. **Data-Dumping Scan (查重与查堆)**: Scan the existing text for table regurgitation (parenthetical numbers, lists of seconds, accuracy diffs, feature numbers).
4. **Purge & Sublimate**: If data is already dumped, aggressively remove the granular numbers, delegate them to the corresponding Table/Figure, and sublimate the text into deep mechanism analysis, physical rationale, and high-level trends.

---

## 📌 Section V: Scientific Figure and Table Caption Protocols (图表标题与图注设计规范)

*These protocols must be strictly enforced whenever creating, drafting, or revising any Figure or Table captions in the manuscript.*

### 🎯 Core Philosophy: "Table Captions Define the Entities; Table Footnotes Explain the Rules; Figure Captions Provide Self-Contained Visual Narratives"
In top-tier Elsevier journals, the functional boundaries of table titles, table footnotes, and figure captions are strictly decoupled to maximize visual legibility and self-containment:
1. **Table Titles (`\caption{...}` above tables)**: Act purely as high-level entity labels defining *what* is compared. They must remain extremely clean, concise, and completely unburdened by typographic or statistical rules.
2. **Table Footnotes (`\par\raggedright\footnotesize` below tables)**: Formally host all typographic definitions (e.g., boldface/underline criteria), mathematical notations, statistical indicators ($+/ \approx / -$), and evaluation metrics.
3. **Figure Captions (`\caption{...}` below figures)**: Serve as self-contained explanatory narratives that decode the complete visual story, guiding the reader through global trends, sub-panel mappings, and visual markers without requiring back-and-forth consultation with the main text.

---

### 🔑 Detailed Operational Caption Protocols

#### Protocol CAP-1: Table Caption Standards (表格标题规范)
- **Position**: Placed strictly **above** the tabular content (`\caption{...}` immediately follows `\begin{table}` or `\begin{table*}`).
- **Length & Style**: Ultra-concise noun phrase, strictly within **6 to 15 words** (ideally 1 line across the column width; never exceeding 2 lines).
- **Content Scope**: Solely describe the subject matter and benchmark scope (e.g., *"Table 4. Comparison of classification accuracy between KDS-EL and competitor algorithms across the benchmark suite."*).
- **Strict Anti-Clutter Rule**: Strictly prohibit dumping formatting rules (such as *"The best results are shown in bold and the second-best are underlined..."*), significance thresholds ($p < 0.05$), or win/tie/loss explanations into the `\caption{...}` title string.
- **Delegation to Table Footnotes**: All formatting definitions, abbreviations, and statistical testing notes must be placed exclusively at the base of the table using `\par\raggedright\footnotesize` or standard table note environments (e.g., *"Entries in bold denote the best performance, while underlined entries indicate the second-best. $+ / \approx / -$ indicates that KDS-EL is statistically significantly superior, statistically equivalent, or inferior to the corresponding competitor according to the pairwise Wilcoxon signed-rank test at $\alpha = 0.05$."*).

#### Protocol CAP-2: Figure Caption Standards (插图标题与图注规范)
- **Position**: Placed strictly **below** the visual graphic (`\caption{...}` placed after all subfigures or `\includegraphics`).
- **Length & Style**: Self-contained scientific paragraph, strictly within **20 to 50 words** (typically 1 to 3 structured sentences; occupying 1 to 3 printed lines).
- **Mandatory Three-Part Anatomy**:
  1. *Main Subject Clause (8–15 words)*: Succinct statement of the visual metric or architectural workflow (e.g., *"Overall convergence trajectories of mean objective fitness across 100 evolutionary generations."*).
  2. *Sub-Panel Navigation Guide (分图导引)*: Explicit mapping of all subfigures (e.g., *"(a) Omnibus mean trajectory across the 20 benchmark datasets, and (b)–(i) eight representative ultra-high-dimensional datasets."*).
  3. *Visual Cue & Landmark Decoding (图符与视觉标记解析)*: Explicit explanation of visual indicators, including dashed division lines, shaded confidence ribbons, secondary axes, and marker shapes (e.g., *"The vertical dotted line marks the transition boundary from Phase 1 (dimensional pruning) to Phase 2 (fine accuracy refinement) under Two-Phase Weight Scheduling."*).
- **Self-Containment Criterion**: An expert reader must be able to comprehend the entire figure, the meaning of each curve, and all graphical landmarks purely from the caption and the visual artifact, with zero ambiguity.

#### Protocol CAP-3: Typographic & Symbol Synchronization (符号完全同构规范)
- **100% Symbol Consistency**: Every mathematical symbol appearing in figure captions or table notes must match the in-text LaTeX math notation and the embedded vector PDF labels with 100% fidelity (e.g., $d_{\mathrm{selected}}$, $k_e$, $\kappa$, $\mathbf{W}$, $f_{\mathrm{gbest}}$).
- **Capitalization Standard**: Follow standard Elsevier sentence-style capitalization for caption titles (capitalizing only the first word and proper nouns/acronyms).

---

## 🔍 Automated Pre-Response & Pre-Compilation Verification Checklist

For **every user prompt, LaTeX edit, or section rewriting**, the agent must execute the following 20-point internal audit before outputting:

1. [ ] **Zero Baseline Terminology Check**: Is the word "baseline" / "baselines" completely eliminated from manuscript text, tables, captions, footnotes, and dialogue responses in favor of "competitor", "comparison method", "peer algorithm", or "benchmark"?
2. [ ] **Acronym Check**: Are there duplicate acronym expansions (e.g., `(KER)`, `(TPS)`)?
3. [ ] **Parameter Leakage Check**: Are specific numbers/parameters prematurely leaked into high-level descriptive sections?
4. [ ] **Parenthetical Scan**: Are there redundant parenthetical explanations or code-like conditions?
5. [ ] **Narrative Rhythm Check**: Does the text use natural pipeline verbs instead of mechanical bulleted ordinals?
6. [ ] **Mathematical Rigor Check**: Are all variables given explicit mathematical domains? Are vector orientations consistent?
7. [ ] **Figure/Equation Cross-Ref Check**: Are all figure, table, and equation references resolved with 0 compilation errors?
8. [ ] **Causal Logic Check**: Does every proposed design component have a clearly articulated physical motivation?
9. [ ] **Elsevier Booktabs Check**: Do all tables strictly avoid vertical lines (`|`) and use standard `\toprule`, `\midrule`, `\bottomrule`?
10. [ ] **Statistical Verification Check**: Are standard deviation ($\pm \mathrm{Std}$) and Wilcoxon $+/-/\approx$ counts properly presented?
11. [ ] **Vector Graphic Check**: Are all embedded figures in pure vector `.pdf` format?
12. [ ] **Highlight Length Check**: Are Research Highlights strictly between 3–5 bullets and under 85 characters each?
13. [ ] **BibTeX Integrity Check**: Are all `\cite{...}` keys resolved without undefined reference warnings?

### 🔬 Additional Section 2 (Related Work) Specific Audit Items:
14. [ ] **Section 2 Narrative Chain**: Does each subsection follow the 4-step chain (*Merits $\to$ High-D Bottleneck $\to$ Remedy Limits $\to$ Proposed Rationale*) rather than mechanical literature listing?
15. [ ] **Section 2 Closed-Loop Check**: Are the three core gaps in Related Work in 1-to-1 correspondence with MII+AIR, KER, and TPS?
16. [ ] **Section 2 Competitor Coverage**: Are all 13 experimental competitor algorithms explicitly introduced and taxonomically categorized?
17. [ ] **Section 2 No Parameter Dump**: Are specific tuning constants ($\theta=0.60, w_f=0.30, k_e=3, \gamma=0.99$) completely absent from Section 2 high-level narrative?
18. [ ] **Zero "Operator" for Proposed Components**: Are KDS-EL's own components (KER, TPS, MII, AIR) strictly designated as "strategy" or "mechanism", with the word "operator" strictly prohibited for proposed components and reserved exclusively for standard genetic/evolutionary heuristics of peer algorithms?

### 📊 Section-Wise Data-Boundary & Anti-Dumping Audit:
19. [ ] **Section-Wise Data Tier Audit**: Is the modified text strictly compliant with its designated Data Tier (Tier 1: zero data; Tier 2: macro landmarks only; Tier 3: setup constants only; Tier 4: table-free causal mechanisms)? Has all "table regurgitation" (cell-by-cell numerical dumping) been completely purged in favor of causal and mechanical analysis?

### 🏷️ Figure and Table Caption & Layout Audit:
20. [ ] **Caption & Footnote Audit**: Are table captions ultra-concise noun phrases (6–15 words) free of formatting definitions? Are boldface/underline definitions and statistical symbols delegated exclusively to table footnotes? Do figure captions adhere to the 3-part self-contained anatomy (20–50 words) with explicit sub-panel guides and visual landmark decodings?
