# AGENTS.md — KDS-EL Academic Writing, Rigor & Elsevier Submission Protocols

This document defines the strict academic standards, mathematical conventions, experimental protocols, and Elsevier-specific submission guidelines governing all writing, revising, and LaTeX code generation for the **KDS-EL** research paper targeting top-tier Elsevier SCI journals (e.g., *Applied Soft Computing* [ASOC], *Expert Systems with Applications* [ESWA], *Swarm and Evolutionary Computation* [SWEVO], *Information Sciences*, *Knowledge-Based Systems*).

**Core Axiom (绝对铁律)**: All text, formulas, algorithmic pseudocode, parameter values, and empirical claims must strictly and faithfully mirror the actual code in `code/` and the actual experimental data in `output/`. Zero hallucination, zero data fabrication, zero conceptual misalignment, and zero unverified literature copying.

Every generation and modification must strictly comply with all criteria outlined below.

---

## 📌 Section I: Core Academic Writing & Narrative Protocols

### Pillar 1: Zero Parenthetical Clutter & Duplicate Acronyms
- **No Duplicate Acronym Expansions**: Once an acronym (e.g., `KDS-EL`, `KER`, `TPS`, `PSO`, `MI`) is defined in the Abstract/Introduction, do not expand it again with parenthetical tags like `Knowledge-Guided Elite Refinement (KER)`. Use the formal terms directly (e.g., `the KER strategy`, `the dynamic TPS strategy`, `the MII mechanism`).
- **Strict Prohibition of "Operator" for Proposed Components**: Strictly prohibit referring to KDS-EL's own constituent components as an `operator` (e.g., never write `KER operator`, `refinement operator`, or `our operators`). KDS-EL's components must strictly be termed `strategy` or `mechanism` (e.g., `the KER strategy`, `the elite refinement mechanism`, `the dynamic TPS strategy`). The term `operator` is reserved exclusively for standard low-level genetic/evolutionary heuristics of peer algorithms (e.g., `crossover operator`, `stochastic bit-flip operator`, `swarm variation operators`).
- **Eliminate Parenthetical Inequalities & Dimensional Clutter**: Never append parenthetical inequality shorthands or dimension fragments like `($D \gg N_{\mathrm{samp}}$)` or `($N_{\mathrm{samp}} \ll 100$)` to dataset or population nouns. Express dimensional regimes and sample scarcity naturally through running academic prose (e.g., *"Given a high-dimensional dataset $\mathcal{D}$ characterized by severe sample scarcity..."* or *"in ultra-high-dimensional and sample-scarce regimes where candidate dimensions $D \gg 10^3$ vastly exceed sample observations $N_{\mathrm{samp}} \ll 100$..."*).
- **Eliminate Parenthetical Symbol Dumps & Calculations**: Never dump mathematical symbols, subpopulation tags, or arithmetic expressions into parentheses following a noun phrase (e.g., strictly prohibit `collaborative dual-swarm co-evolution ($\mathcal{P}_1$ and $\mathcal{P}_2$)`, `equal size ($N/2$)`, or `guided by the global best solution of $\mathcal{P}_2$ ($\mathbf{g}_{\mathrm{best},2}$)`). Express them as natural appositive or prepositional prose (e.g., *"collaborative dual-swarm co-evolution between subpopulations $\mathcal{P}_1$ and $\mathcal{P}_2$"*, *"each comprising $N/2$ particles"*, *"guided by the global best solution $\mathbf{g}_{\mathrm{best},2}$ of $\mathcal{P}_2$"*).
- **No Premature Parameter Dumping**: In high-level architecture/framework sections (such as Section 3.1) and general prose, never hardcode specific hyperparameter values (e.g., `(wf,1 = 0.30)`, `(wa,2 = 0.95)`, `(theta = 0.60)`, `(knn = 3)`) or inline formula fragments in parentheses. Specific parameter values belong strictly in dedicated technical subsections (where they are introduced as standard syntactic sentences, e.g., *"where $k_{\mathrm{nn}} = 3$ is the neighborhood parameter..."*) and the experimental parameter setup table.
- **Eliminate Pseudo-Code Conditions & Explanatory Clauses in Text**: Never write parenthetical code-like logic in prose (e.g., `(rank(i) <= N/2)` or `(MI_init_ratio = 0.50)`). Translate them into rigorous academic English (e.g., *"the superior half of the swarm is preserved intact..."*). Furthermore, never enclose entire English explanatory sub-clauses in parentheses; integrate them directly into the sentence cadence using commas, appositive phrases, or participial clauses (strictly avoiding disruptive em-dashes).
- **Two-Tier Parenthesis Taxonomy (Banned Clutter vs. Mandatory Math)**:
  - *Prohibited Parenthetical Clutter (Strictly Banned)*: Inline hyperparameter values `($k_{\mathrm{nn}} = 3$)`, dimension attractor notes `($d \approx D/2$)`, embedded Big-$\mathcal{O}$ complexity insertions `($\mathcal{O}(N_{\mathrm{samp}}^2 d)$)`, parenthetical subpopulation lists `($\mathcal{P}_1$ and $\mathcal{P}_2$)`, parenthetical inequality bounds `($D \gg N_{\mathrm{samp}}$)`, and English explanatory clauses.
  - *Mandatory Mathematical Notations (Strictly Preserved)*: Standard continuous intervals ($\theta \in (0.5, 1)$, $\rho \in (0, 1)$, $\gamma \in (0, 1)$), probability distribution arguments ($\boldsymbol{\varepsilon}_i \sim \mathcal{N}(\mathbf{0}, \sigma^2 \mathbf{I}_D)$, $\mathbf{u}_i \sim \mathcal{U}(0, 1)^D$), standard function/operator placeholders ($\mathbb{I}(\cdot)$, $\psi(\cdot)$, $\mathrm{clip}(z, 0, 1)$), algebraic grouping factors ($(1 - \rho)N$, $(2 x_{i,j}^{(t)} - 1)$), and LaTeX cross-references (`Eq.~\eqref{eq:importance_update}`, `Section~\ref{sec:framework}`).
- **Strict Prohibition of Disruptive Em-Dashes (成对破折号严格禁用与学术重构规范)**:
  - In rigorous Elsevier SCI journal writing, strictly prohibit using paired em-dashes (`---` in LaTeX) to insert parenthetical examples, algorithm enumerations, or supplementary commentary (e.g., `components---such as mutual information initialization and differential elite refinement---into`). Paired em-dashes break core subject-verb-object continuity, impair academic readability, and are widely recognized in modern peer review as colloquial or LLM-generated stylistic artifacts.
  - All explanatory inclusions, illustrative algorithm lists, and supplementary details must be smoothly integrated via standard academic appositives (`..., including ...,`), prepositional phrases (`..., such as ...,`), or participial clauses (`..., reflecting ...`).
  - *Distinguish Em-Dashes from Mandatory Typographical Dashes (Strictly Preserved)*:
    - Standard compound proper name en-dashes (`Mann--Whitney`, `Holm--Bonferroni`, `Kraskov--St{\"o}gbauer--Grassberger`, `Iman--Davenport`);
    - Numerical intervals and parameter bounds (`0.90--1.00`, `\omega \in [0.4, 0.9]`);
    - Equation and citation page ranges (`Eqs.~\eqref{eq:mi_seeding}--\eqref{eq:binarize}`, `pp. 1157--1182`);
    - Standard table null/diagonal markers (`—`).

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
  - **Vectors**: Bold lowercase roman ($\mathbf{x}_i, \mathbf{p}_i, \mathbf{m}, \boldsymbol{\varepsilon}_i, \mathbf{w}(t)$).
  - **Scalars / Parameters**: Italic lowercase ($x_{i,j}, p_{i,j}, N, D, T, \theta, \gamma, \tau, \rho, \phi, \kappa, k_e$).
  - **Sets / Populations**: Calligraphic uppercase ($\mathcal{P}_1, \mathcal{P}_2, \mathcal{D}, \mathcal{S}_{\mathrm{know}}, \mathcal{S}_{\mathrm{rand}}, \mathcal{C}_i^{(t)}$).
  - **Standard Functions / Operators**: Upright roman ($\min, \max, \arg\max, \mathrm{clip}(\cdot), \mathbb{I}(\cdot), \mathrm{Acc}(\cdot)$).
- **Consistency in Vector Orientation**: If candidate solutions $\mathbf{x}_i = [x_{i,1}, \dots, x_{i,D}]$ are row vectors of $\mathbf{X}$, do not randomly add transpose signs $\mathbf{x}_i^T$ unless performing dot products or matrix transpositions.

---

### Pillar 5: Deep Figure-Table Linkage & Self-Containment
- **Figure/Table Self-Containment**: Captions must be descriptive enough that a reader can grasp the core mechanism purely from the visual artifact (complying strictly with Section V, Protocol CAP-2: self-contained 20–50 words structured into global subject, sub-panel guide, and visual cue decoding).
- **Exact Symbol Matching**: Symbols within PDF figures (`F1`, `F2`, `F3`, `F4`, `F8`, `F14`) must match the in-text LaTeX math notation 100%.
- **Directional Referencing**: Direct the reader to specific visual pathways within figures (e.g., *"As illustrated in the adaptive recovery branch of Fig.~2..."*, *"As depicted in Branch 2 of the KER flowchart in Fig.~4..."*).

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

### Pillar 8: Measured Academic Tone, Strict Colloquialism Prohibition & Tight Causality
- **Zero Promotional Fluff**: Strictly avoid unscientific subjective terms (`revolutionary`, `miraculous`, `flawless`, `unprecedented`).
- **Strict Prohibition of Colloquialisms, Pseudo-Jargon & Literal Translations**:
  - `one-to-one replacement` $\longrightarrow$ `greedy pairwise in-place replacement`, `elitist direct replacement`
  - `step by step` / `step-by-step` $\longrightarrow$ `progressively`, `sequentially`, `in an iterative pipeline`
  - `hand in hand` / `hand-in-hand` $\longrightarrow$ `synergistically`, `in concerted synergy`
  - `deal with` $\longrightarrow$ `address`, `mitigate`, `tackle`, `resolve`
  - `a lot of` / `lots of` $\longrightarrow$ `numerous`, `extensive`, `a substantial volume of`
  - `more and more` $\longrightarrow$ `increasingly`, `progressively`
  - `make sure` $\longrightarrow$ `ensure`, `guarantee`, `verify`
  - `get` / `got` $\longrightarrow$ `obtain`, `derive`, `harvest`, `extract`
  - `side effect` $\longrightarrow$ `unintended degeneration`, `suboptimal penalty`
  - `good result` / `good performance` $\longrightarrow$ `superior empirical performance`, `favorable convergence profile`
  - `try to` $\longrightarrow$ `is designed to`, `aims to`, `seeks to`
  - `huge` / `big` $\longrightarrow$ `substantial`, `pronounced`, `prominent`
- **Precision Causality**: Use precise inferential connectors:
  - *Mitigation*: `effectively mitigates`, `substantially alleviates`, `suppresses`.
  - *Improvement*: `significantly improves`, `consistently outperforms`.
  - *Causality*: `thereby facilitating...`, `consequently avoiding...`, `which in turn accelerates...`.
- **Strict Prohibition of the Term "Baseline"**: Strictly prohibit the words `baseline` / `baselines` across all LaTeX manuscript text, table captions, table footnotes, and agent dialogue responses. Peer algorithms must never be casually or dismissively labeled as "baselines" or "baseline MEL". Adhere strictly to formal scholarly terminology:
  - *For peer algorithms*: `competitor algorithms`, `competing methods`, `comparison approaches`, `peer algorithms`, `counterparts`, `benchmark methods`.
  - *For the backbone algorithm MEL*: `the original MEL algorithm` or directly `MEL` (never `baseline MEL`, `MEL baseline`, `precursor MEL`, or `the foundational MEL framework`).
  - *For unreduced data / raw feature sets*: `unreduced full-dimensional feature sets`, `raw feature spaces` (never `full-dimensional baselines`).
  - *For reference fitness / starting levels*: `initial fitness value`, `initial reference fitness` (never `fitness baseline`).
  - *For algorithmic comparison collections*: `comparison suite`, `benchmark suite`, `competitor suite` (never `baseline suite`).
- **Strict Prohibition of Machine Learning Jargon "Ablation"**:
  - In evolutionary computation and swarm intelligence literature (especially top Elsevier journals like *Applied Soft Computing*, strictly mirroring EMSWOA), strictly prohibit machine learning terminology such as `ablation study`, `ablation experiments`, `ablation configurations`, or `ablative variants`.
  - Component contribution analysis must strictly be formalized as **performance comparison before and after algorithm improvement** (`before and after algorithm improvement`, `intermediate algorithmic configurations before and after improvement`, `pre- and post-improvement algorithms`, `constituent mechanism analysis`).
- **Strict Prohibition of Academic Over-claiming & NFL Alignment**:
  - Algorithms are fundamentally governed by the No Free Lunch theorem. Sweeping assertions of universal dominance, "decisive leadership", or "unprecedented" superiority are strictly banned. KDS-EL's genuine scientific contribution resides in its principled multi-criteria trade-off (achieving competitive accuracy while reducing feature counts by orders of magnitude) and substantial advancement over its architectural precursor (the original MEL algorithm).
  - *Strict Blacklist of Banned Over-Claiming Words*:
    - `decisive leadership`, `global leadership`, `unquestionable superiority`, `absolute dominance`, `unprecedented`, `miraculous`
    - `strictly bounded` (when describing heuristic budgets without proofs)
    - `eliminate` / `eliminates` (evolutionary mechanisms mitigate, suppress, or substantially alleviate; they do not deterministically "eliminate")
    - `seamlessly` (subjective filler)
    - `intrinsically salient` (over-claiming unsupervised ground truth)
    - `optimal trade-off` (replace with `favorable trade-off` or `balanced trade-off`)
    - `all null hypotheses are formally rejected` / `statistically confirms its absolute superiority`
  - *Empirical Boundary Nuance & Anti-Contradiction Rule*:
    - When empirical metrics exhibit mixed outcomes (e.g., Table 4 accuracy against bIRIME exhibits 11 wins, 5 ties, 4 losses in raw mean alongside 8 wins, 11 ties, 1 loss under Mann--Whitney $U$ tests), the running text **must never claim universal accuracy supremacy**.
    - Explicitly acknowledge where peer algorithms maintain localized competitive parity, while rigorously framing KDS-EL's multi-objective contribution: delivering comparable classification accuracy alongside an order-of-magnitude reduction in feature cardinality (87.8 vs hundreds or thousands of features), yielding superior overall scalarized fitness.

---

## 📌 Section Ib: Code-Grounded Truth & Mathematical Reality Protocols (实验数据与代码真值死锁规范)

*This subsection defines the non-negotiable ground-truth anchors derived directly from `code/` and `output/`. Every number, equation, and protocol in the paper must strictly align with these facts.*

### Protocol TRUTH-1: Ground-Truth Performance Data Deadlock (真实实验数据死锁表)
All text, tables, abstracts, and discussion must strictly draw from the verified pure classification performance on the 20 benchmark datasets. Mixing composite fitness ($1 - fitG$) with pure classification accuracy is strictly prohibited.

#### Master Empirical Reference Table (20 Benchmark Datasets Aggregate)
| Algorithm / Configuration | True Pure Accuracy ($\mathrm{Acc}$) | Mean Feature Count ($d$) | Wall-Clock Time (s) | Historical $1-fitG$ Artifact (BANNED as Accuracy) |
| :--- | :---: | :---: | :---: | :---: |
| **KDS-EL (TwoPhase)** [Ours] | **0.9545** (0.954530) | **87.8** | **51.3** | *0.9574* (strictly $1-fitG$, not pure acc) |
| **KDS-EL (TwoPhase, 20260905 rerun)** | 0.9460 (0.946021) | 90.9 | 49.8 | — |
| **KDS_EL_NoPool** (w/o TPS) | **0.9462** (0.946186) | **121.7** | 48.5 | *0.9488* |
| **MEL_MI** (w/o TPS & KER) | **0.9348** (0.934837) | **290.5** | 62.4 | *0.9325* |
| **bIRIME** (*iScience* 2024) | **0.9454** (0.945449) | **407.7** | **326.2** | — (already pure accuracy) |
| **FWPSO** (Wang & Jia 2022) | **0.9242** (0.924183) | **1068.9** | 175.0 | *0.9177* |
| **SaWDE** (*KBS* 2022) | **0.9180** (0.918003) | **3521.1** | 210.4 | *0.8944* |
| **MEL** (*IEEE TKDE* 2024 Precursor) | **0.9093** (0.909287) | **2722.2** | 175.0 | *0.8868* |
| **PSO_CSM** (*SWEVO* 2025) | **0.9085** (0.908503) | **1559.4** | 188.6 | *0.9021* |
| **BPSO** (Kennedy & Eberhart 1997) | **0.9075** (0.907519) | **5296.5** | 134.2 | *0.8698* |
| **BinCOA** (*IEEE Access* 2024) | **0.8973** (0.897340) | **5420.7** | 245.8 | — (already pure accuracy) |
| **IGPSO** (*SWEVO* 2024) | **0.8985** (0.898459) | **2538.2** | 136.4 | *0.8839* |
| **DENCA_SO** (*KBS* 2023) | **0.8712** (0.871206) | **5323.4** | 185.7 | — (already pure accuracy) |

- **Strict bIRIME Ground-Truth Anchoring**: In running text (such as Section 4.2), bIRIME's feature cardinality is **407.7** (NOT 424.8), and runtime is **326.2 s** (NOT 375.2 s). Never contradict the values generated in Table 5 and Table 8.
- **Strict 4-Stage Monotonic Improvement Progression**: The constituent mechanism progression (before and after algorithm improvement) must report the verified pure accuracy and feature counts:
  $$\text{MEL: } (0.9093, 2722.2) \xrightarrow{+\text{MII+AIR}} \text{MEL+MI: } (0.9348, 290.5) \xrightarrow{+\text{KER}} \text{NoPool: } (0.9462, 121.7) \xrightarrow{+\text{TPS}} \text{KDS-EL: } (0.9545, 87.8)$$
  Notice that pure accuracy monotonically increases ($+2.55\text{ pp} \to +1.14\text{ pp} \to +0.83\text{ pp}$) while active features monotonically shrink ($-89.3\% \to -58.1\% \to -27.9\%$).

---

### Protocol TRUTH-2: Code-Faithful Formula Synchronization (公式与代码实现绝对一致规范)
Equations in Section 3 and Section 4 must 100% match the actual lines of code in `code/algorithms/kds_el_twophase.py` and `code/utils.py`.

1. **Importance Vector $\mathbf{W}$ Updating (Both Success & Failure Branches)**:
   - In `code/algorithms/kds_el_twophase.py:122-142`, the update rule handles both fitness improvements and non-improvements:
     - When candidate solution $\mathbf{x}_i^{(t)}$ achieves a strict fitness improvement over personal best $\mathbf{p}_{\mathrm{best},i}$ ($\delta_i^{(t)} = f(\mathbf{p}_{\mathrm{best},i}) - f(\mathbf{x}_i^{(t)}) > 0$):
       $$W_j \leftarrow W_j + \delta_i^{(t)} \cdot (2 x_{i,j}^{(t)} - 1), \quad \forall j \in \mathcal{C}_i^{(t)}$$
     - When candidate solution $\mathbf{x}_i^{(t)}$ fails to improve ($\Delta_i^{(t)} = f(\mathbf{x}_i^{(t)}) - f(\mathbf{p}_{\mathrm{best},i}) \ge 0$):
       $$W_j \leftarrow W_j - \Delta_i^{(t)} \cdot (2 x_{i,j}^{(t)} - 1), \quad \forall j \in \mathcal{C}_i^{(t)}$$
   - *Strict Prohibition*: Strictly prohibit claiming that non-improving candidates "leave $\mathbf{W}$ unaltered" when the implementation executes bidirectional credit/penalty updating. Mathematical descriptions must precisely state this symmetric reward-penalty dynamic.

2. **KER Perturbation Noise in Score Ranking**:
   - In `code/utils.py:369-371`, the directional flip score ranking is perturbed by Gaussian noise scaled to the empirical standard deviation of the weight vector:
     $$\sigma_j = (1 - 2 x_{e,j}) W_j + \xi_j, \quad \xi_j \sim \mathcal{N}\left(0, \left(\mathrm{std}(\mathbf{W}) + 10^{-5}\right)^2\right)$$
   - *Strict Prohibition*: Strictly prohibit claiming that KER adds an "infinitesimal tie-breaking jitter with variance $10^{-12}$". The text must honestly describe $\xi_j$ as an adaptive stochastic perturbation proportional to the dispersion of learned feature importance ($\mathrm{std}(\mathbf{W}) + 10^{-5}$), balancing directional guidance with exploratory diversity.

3. **Competitor Implementation Fidelity (IGPSO)**:
   - In `code/algorithms/igpso.py:8-11, 24-32`, feature importance is estimated via the contrast of ANOVA F-statistics:
     $$\mathrm{Imp}_j = \max\left(0, F_{\mathrm{true}, j} - F_{\mathrm{perm}, j}\right)$$
   - *Strict Prohibition*: Strictly prohibit claiming that IGPSO uses a "multi-layer perceptron (MLP)" or "neural network". Formally describe IGPSO as **two-stage importance-guided PSO using ANOVA F-statistic permutation contrast**.

---

### Protocol TRUTH-3: Benchmark Instance & Experimental Protocol (基准优化实例与实验设置学术界定规范)

1. **Banning "50 Distinct Folds" (坚决剔除 50 个互不相同折的虚假陈述)**:
   - In `code/config.py:76` and `code/utils.py:170`, `StratifiedKFold` fixes `random_state=42`. All 10 independent runs of an algorithm evaluate candidate subsets against the **exact same 5 stratified folds**.
   - *Mandatory Academic Phrasing*: Formally define the experimental protocol:
     > *"To evaluate stochastic optimization stability and algorithmic convergence, each algorithm undergoes 10 independent runs initialized with distinct random seeds on each benchmark dataset. Following the established benchmarking protocol of the foundational MEL algorithm~\cite{mel2024} and peer evolutionary feature selection literature, each benchmark dataset is evaluated as a self-contained combinatorial optimization instance where an internal 5-fold stratified cross-validation wrapper serves as the fitness evaluation surrogate."*
   - Strictly prohibit claiming "50 distinct folds".

2. **Offline Mutual Information Prior Injection (互信息离线先验学术定界)**:
   - In `code/algorithms/kds_el_twophase.py:54`, mutual information vector $\mathbf{m}$ is computed once offline on the dataset before the evolutionary loop begins.
   - *Mandatory Framing*: Formally frame this strictly as **problem-level heuristic domain knowledge injection**, fully aligned with the benchmark instance paradigm of IEEE TKDE 2024 MEL. It is not an unseen clinical cohort test, but an offline filter-wrapper hybridization for combinatorial optimization benchmarking.

3. **Fair Evaluation Budget vs. Generation Cutoff Definition**:
   - Algorithms were evaluated under an **identical population size ($N=20$) and generation cutoff ($T=100$)**.
   - *Mandatory Disambiguation*: Strictly prohibit asserting "identical evaluation budgets" without qualification. In runtime and efficiency analysis (Section 4.2.6), explicitly acknowledge structural differences in per-generation fitness function calls: BPSO evaluates 20 particles/gen; KDS-EL evaluates 20 particles plus $k_e=3$ KER elites and periodic stagnation restarts; bIRIME evaluates up to 80 candidates/gen due to composite mutation strategies (CMS). Explain that KDS-EL's runtime advantage over bIRIME (51.3 s vs 326.2 s) stems both from feature compression and from avoiding wasteful unguided multi-operator evaluations.

---

### Protocol TRUTH-4: Cross-Classifier Inductive Transferability Protocol (表 S9 实事求是分析规范)
In Section 4.2 and Supplementary Section S9, cross-classifier evaluation (Table S9) must be analyzed with absolute factual honesty:
- **Adenoma**: Compact subsets ($d=66$) achieve 100% accuracy across all three architectures (3-NN, SVM, Random Forest).
- **ALL4**: Compact subsets ($d=124$) achieve substantial performance gains across all three classifiers (3-NN improves by +17.31 pp, SVM improves by +3.33 pp, Random Forest improves by +11.99 pp).
- **Colon**: Compact subsets ($d=14$, compressing 2,000 features by >99.3%) elevate 3-NN accuracy from 79.23% to 88.59% (+9.36 pp). However, this extreme compression incurs a slight trade-off on inductive learners with divergent inductive biases (SVM drops from 85.51% to 80.51%; Random Forest drops from 85.38% to 82.18%).
- *Strict Prohibition*: Never claim that "compact subsets deliver substantial classification gains across all architectures on all datasets". Frankly and scholarly analyze the trade-off: extreme feature compression specifically optimized for non-parametric local metric geometry (3-NN) may exhibit minor boundary sensitivity when transferred to hyper-plane margins (SVM) or orthogonal partition ensembles (RF) on small cohorts. This measured honesty earns profound reviewer respect.

---

### Protocol TRUTH-5: Major Revision Supplementary Experiments Directory & Data Deadlock (一审修回补充实验体系目录与数据死锁规范)
All responses, supplementary reports, and manuscript revisions addressing Review Round 1 must strictly source data from the designated subdirectories under `output/nested_cv/` across the 19 independent benchmark datasets (excluding duplicate `ALL_AML`):
- **Splits Directory**: `output/nested_cv/splits/` — Rigorous 5-fold outer splits (`*_outer_splits.json`), ensuring zero-leakage isolation.
- **E0 (Gate Verification)**: `output/nested_cv/e0_verification/` — Equivalence verification of candidate fast 3-NN evaluator (`e0_equivalence_report.md/json`).
- **E1 (Acceptance & Concurrency)**: `output/nested_cv/e1_acceptance/` & `output/nested_cv/e1_stress/` — Single-fold workflow acceptance and concurrency stress tests.
- **E2 (Competitor Re-Analysis)**: `output/nested_cv/e2_reanalysis/` — Offline multi-metric descriptive re-analysis over 570 competitor masks (`e2_summary_table.json`, `e2_detailed_runs.json`). Verified aggregates:
  - `bIRIME`: Acc 0.9426, Balanced Acc 0.9343, Macro-F1 0.9360, Feats 422.9.
  - `BinCOA`: Acc 0.8926, Balanced Acc 0.8802, Macro-F1 0.8810, Feats 5526.1.
  - `DENCA_SO`: Acc 0.8656, Balanced Acc 0.8505, Macro-F1 0.8497, Feats 5432.5.
  - *Strict Boundary*: Serves strictly as descriptive internal re-analysis to resolve class imbalance concerns (Reviewer 1 Comment 2, Reviewer 4 Minor 7); never describe as new outer test generalization.
- **E3 (Filter Benchmarks)**: `output/nested_cv/e3_filters/` — Fold-internal filter benchmarks across $k \in [20, 50, 100]$ (`e3_summary_table.json`, `e3_pareto_curves.json`). Verified aggregates:
  - Top-k MI: 0.8627 ($k=20$), 0.8726 ($k=50$), 0.8801 ($k=100$).
  - Two-Stage mRMR: 0.8414 ($k=20$), 0.8685 ($k=50$), 0.8797 ($k=100$).
  - ReliefF: 0.8456 ($k=20$), 0.8538 ($k=50$), 0.8672 ($k=100$).
  - LASSO: 0.8754 ($k=20$), 0.8824 ($k=50$), 0.8943 ($k=100$).
  - *Strict Boundary*: Rebuts the claim that "pure MI ranking suffices" (Reviewer 1 Comment 3, Reviewer 4 Major 4).
- **E4 (Component Analysis)**: `output/nested_cv/e4_component_analysis/` — Controlled mechanism analysis across 7 configurations.
- **E5 (Full Nested Generalization)**: `output/nested_cv/e5_generalization/` — Full double-nested cross-validation unbiased generalization estimates.
- **E6 (Permutation Tests)**: `output/nested_cv/e6_permutation/` — Empirical permutation null distribution testing.
- **E7 (Biological Validation)**: `output/nested_cv/e7_enrichment/` — GO/KEGG functional enrichment and subset stability.
- *Strict Prohibition*: Never mix or average primary benchmark results (20 datasets, KDS-EL pure accuracy 0.9545 from `output/formal_experiment_final/`) with nested CV estimates (19 datasets from `output/nested_cv/`). Both empirical layers must be reported with strict methodological demarcation.

---

## 📌 Section II: Elsevier-Specific Submission & Formatting Standards

### Pillar 9: Elsevier Article Class & Metadata Standards (`elsarticle`)
- **Document Class Setup**: Use standard `\documentclass[5p,times,twocolumn]{elsarticle}`.
- **Author & Affiliation Block**: Declare affiliations using `\address[label]{...}` and specify the corresponding author using `\cortext[cor1]{Corresponding author. Email: ...}`.
- **Highlights Protocol**: Provide exactly 3 to 5 highlights in bullet points. Each bullet must be strictly **under 85 characters** (including spaces) and convey a quantifiable core innovation.
- **Abstract Word Limit**: Keep the abstract strictly within 150–250 words, structured into *Background $\to$ Problem & Limitations $\to$ Proposed Framework $\to$ Key Quantified Results $\to$ Broad Impact*.
- **Keywords**: Provide 4 to 6 indexed keywords separated by `\sep` (e.g., `Feature selection \sep Swarm intelligence \sep Particle swarm optimization \sep High-dimensional data \sep Knowledge-guided search`).

---

### Pillar 10: Elsevier Table Design Protocols (Strict Three-Line Tables)
- **Table Caption & Footnote Decoupling**: Captions placed strictly above tables must be ultra-concise noun phrases of 6–15 words defining only the entity and comparison scope (Protocol CAP-1). All definitions of boldface, underline, statistical testing notation, and parameter symbols must reside strictly in the table footnote (`\par\raggedright\footnotesize`) below the table.
- **Zero Vertical Lines**: In accordance with Elsevier style guides, **never include vertical rules (`|`)** in tables.
- **Booktabs Macros**: Construct all tables using `\toprule`, `\midrule`, and `\bottomrule` from the `booktabs` package.
- **Statistical Significance Highlighting**: Highlight the best-performing metric in **boldface** and underline the second-best across all comparison tables.
- **Multi-Row & Column Sizing**: Use `\cmidrule(lr){...}` to separate grouped benchmark categories.

---

### Pillar 11: Statistical Testing and Evaluation Protocols for Evolutionary Feature Selection
- **Multi-Dataset Non-Parametric Testing (Demšar Protocol)**: To evaluate statistical significance across benchmarks, strictly follow the multi-problem statistical framework of Demšar (2006). Pairwise Wilcoxon signed-rank tests at $\alpha = 0.05$ assess directional superiority across the $N=20$ independent benchmark problem instances, reporting pairwise counts as $+ / - / \approx$ (win / tie / loss).
- **Friedman Global Ranking & Family-Wise Error Correction**: Apply the Friedman test across the multi-dataset benchmark suite to establish omnibus algorithmic rankings, accompanied by post-hoc **Holm-Bonferroni** step-down correction to rigorously guard against family-wise type I error inflation across all competitor comparisons.
- **Per-Dataset Run Comparisons**: For per-dataset stochastic stability comparisons across 10 independent runs, because runs across different algorithms are evaluated with independent random seeds without pairwise random-number synchronization, statistical assessments must be designated as independent sample comparisons (e.g., Mann-Whitney U test) or reported as run-wise distributions ($\mathrm{Mean} \pm \mathrm{Std}$).

---

### Pillar 12: Vector Figures & Resolution Standards
- **Vector PDF Format**: All workflow schematics, convergence curves, and radar plots must be generated and embedded as vector PDFs (`.pdf`), never raster images (`.png` / `.jpg`).
- **Standardized Multi-Panel Layout**: Multi-part figures must use `\begin{subfigure}` with standardized sub-labels `(a)`, `(b)`, `(c)` and synchronized aspect ratios.
- **Font & Linewidth Legibility**: Minimum font size within figures must remain fully legible ($> 7\text{ pt}$) when scaled to single-column width ($8.5\text{ cm}$) or full double-column width ($17.5\text{ cm}$).

---

## 📌 Section III: Specialized Protocols for Section 2 (Related Work & Background)

- **Not a Bibliographic Catalog**: Related Work must construct the motivation landscape, pinpointing the exact structural bottlenecks of existing paradigms under ultra-high-dimensional and sample-scarce regimes ($D \gg 10^3, N_{\mathrm{samp}} \ll 100$).
- **Critical 4-Step Narrative Chain**:
  1. *Mainstream Paradigm & Merits*: Core mechanism and theoretical advantage.
  2. *Physical/Mathematical Bottleneck in Ultra-High Dimensions ($D \gg 10^3$)*: Why it degrades under extreme dimensions and small samples.
  3. *Limitations of Existing Remedies*: Why previous incremental fixes remain insufficient.
  4. *Theoretical Rationale for the Proposed Design*: How KDS-EL's design philosophy fundamentally resolves the dilemma.
- **Exact 1-to-1 Problem-Solution Closed Loop**:
  - *Gap 1 (Initial Search Blindness & Diversity Loss)* $\longleftrightarrow$ **MII + AIR**: Mutual-information continuous soft prior initialization coupled with adaptive diversity re-initialization upon stagnation.
  - *Gap 2 (Discarded Iteration Feedback & Memoryless Perturbation)* $\longleftrightarrow$ **Dynamic Feature Importance Memory + KER**: Closed-loop accumulation of historical fitness feedback with exponential forgetting, driving targeted directional elite refinement within bounded computation ($k_e \ll N$).
  - *Gap 3 (Rigid Static Weighting & Evolutionary Phase Misalignment)* $\longleftrightarrow$ **Two-Phase Weight Scheduling (TPS)**: Temporally decoupling coarse dimensional pruning in Phase 1 from fine accuracy refinement in Phase 2.
- **100% Benchmark Competitor Anchoring**: All 12 comparison algorithms evaluated in experimental sections must be explicitly classified and cited in Section 2.

---

## 📌 Section IV: Hierarchical Section-Wise Data-Boundary & Anti-Dumping Protocols

- **Tier 1 (Strictly Zero Data / 绝对禁水区)**: Section 2 (Related Work) and Section 3 (Proposed KDS-EL Method). Zero experimental test outcomes, zero performance numbers.
- **Tier 2 (Macro Milestone Metrics Only)**: Abstract, Highlights, Section 1 (Introduction), and Conclusion. Limited to verified aggregate landmarks: mean pure accuracy **0.9545**, mean active features **87.8** (>98% compression), empirical speedup **3.4x**.
- **Tier 3 (Static Setup Constants Only)**: Section 4.1 (Experimental Setup). Only declare static benchmarking constants: 20 benchmark datasets, 10 independent runs, 5-fold stratified cross-validation wrapper, 3-NN classifier, and default hyperparameters.
- **Tier 4 (Mechanism-Driven Empirical Analysis)**: Section 4.2. Tables and figures host the numbers; prose synthesizes behavioral trends and explains causal mechanics. Strictly prohibit reciting numbers cell-by-cell.

---

## 📌 Section V: Scientific Figure and Table Caption Protocols

- **Protocol CAP-1: Table Caption & Footnote Decoupling**:
  - Captions placed strictly above tables (`\caption{...}`) must be ultra-concise noun phrases of **6 to 15 words** defining only the entity and comparison scope.
  - All definitions of boldface, underline, statistical testing notation, and parameter symbols must reside strictly in the table footnote (`\par\raggedright\footnotesize`) below the table.
- **Protocol CAP-2: Ultra-Concise Figure Caption Standards**:
  - Figure captions placed strictly below figures must be concise noun phrases of **8 to 15 words**.
  - Captions must never read like mini-abstracts or recite data numbers. All interpretations belong in main text paragraphs.

---

## 📌 Section VI: Specialized Protocols for Section 3 (The Proposed Method)

- **Tier 1 Zero-Data Boundary**: Section 3 is strictly classified under Data Tier 1. Zero post-hoc experimental test scores permitted.
- **"Why Before How" Causal Chain**: Every formula must be introduced through bottleneck analysis $\to$ structural intuition $\to$ mathematical formulation $\to$ boundary behavior.
- **Mathematical Space Completeness**: Every variable must declare its space ($\mathbf{X} \in \{0, 1\}^{N \times D}$, $\mathbf{W} \in \mathbb{R}^D$, $\mathbf{m} \in [0, 1]^D$, $\mathbf{w}(t) \in [0, 1]^2$, $\gamma \in (0, 1)$).
- **Two-Tier Pseudocode**: Algorithm 1 formalizes KER sub-routine; Algorithm 2 coordinates the master KDS-EL lifecycle with complete `\Require` and `\Ensure` blocks.
- **Asymptotic Complexity Closed-Loop**: Decouple offline preprocessing $\mathcal{T}_{\mathrm{pre}} = \mathcal{O}(D N_{\mathrm{samp}} + D \log D)$ from generational wrapper evaluation $\mathcal{T}_{\mathrm{eval}} = \mathcal{O}(T N N_{\mathrm{samp}}^2 \bar{d}_{\mathrm{selected}} + T N D)$.

---

## 📌 Section VII: Response to Reviewers & Rebuttal Protocols (审稿意见回复与返修答辩铁律)

*This section defines the mandatory standards for author response letters (rebuttals), revised manuscript excerpts, and reviewer dialogue.*

### Pillar 13: Zero Algorithmic Subject Inversion (坚决杜绝主客颠倒与算法主体失踪)
- **KDS-EL Must Remain the Primary Subject**: In all rebuttal texts and revised sections, KDS-EL must strictly maintain its primary subject status as the proposed algorithm.
- **Strict Prohibition of Framing Competitors as Dominant**: Strictly prohibit phrasing that praises peer algorithms without establishing KDS-EL's supremacy (e.g., never write `bIRIME consistently achieves the top competitive performance` without qualification). When highlighting strong competitors, strictly designate them as `the strongest performance among competing methods` or `the leading competitive baseline among peer algorithms`, while explicitly asserting KDS-EL's overall leadership across metrics.
- **No Inadvertent Competitor Promotion**: Never write text that inadvertently reads as if a competitor algorithm is the proposed method or the overall benchmark champion.

### Pillar 14: Eradication of Biomedical Pseudo-Jargon (`cohorts`) and Anthropomorphic Terms (`dominance`) (彻底禁绝非专业词汇与拟人化修饰)
- **Strict Ban on `cohorts` / `benchmark cohorts`**: In evolutionary computation and machine learning (ASOC, ESWA, SWEVO), benchmark tabular datasets must strictly be termed `benchmark datasets` or `benchmark instances`. Strictly prohibit using `cohorts` or `benchmark cohorts` (which belong exclusively to clinical patient studies in bioinformatics).
- **Strict Ban on `dominance` / `resilient against dominance`**: Evaluation metrics are mathematical formulations; they do not possess psychological resilience (`resilient`). The phenomenon is a statistical sampling skew, not physical subjugation. Replace `resilient against majority-class dominance` with `mitigates majority-class bias` or `provides an equitable assessment under class imbalance`.

### Pillar 15: Strict Elimination of Internal Engineering Leaks (`deduplicated 19-dataset`) (严禁内部研发工程黑话外泄)
- **No Data Pipeline Staging Leaks**: Never expose internal data-cleaning, deduplication, or pipeline staging terminology to reviewers (e.g., strictly prohibit `deduplicated 19-dataset`, `570 competitor feature masks`, `deduplicated benchmark suite`).
- **Eliminate Reviewer Suspicions**: Mentioning `deduplicated` signals to reviewers that the benchmark suite originally contained duplicate, contaminated, or flawed datasets.
- **Mandatory Academic Nomenclature**: Formally refer to the suite as `the 19 benchmark datasets`, `the evaluated benchmark suite`, or `the feature subsets obtained by competing methods`.

### Pillar 16: Elimination of AI Sensationalist Adverbs & Dense Numerical Dumping (严禁典型 AI 浮夸词汇与报数疲劳)
- **Strict Blacklist of AI Sensationalist Adverbs**: Strictly eliminate colloquial or LLM-style introductory adverbs:
  - `Crucially, ...` $\longrightarrow$ delete or rephrase as `Specifically, ...`, `Across the evaluated datasets, ...`
  - `Remarkably, ...` $\longrightarrow$ delete or rephrase neutrally
  - `Interestingly, ...`, `It is worth noting that, ...`, `Seamlessly, ...`, `Unquestionably, ...` $\longrightarrow$ delete entirely
- **Prohibit Dense Inline Decimal Recitation**: Never string multiple tuples of 3-to-4-decimal metrics directly into prose (e.g., strictly prohibit `bIRIME (mean Acc: 0.9426, BAcc: 0.9343, Macro-F1: 0.9360), followed by BinCOA (0.8926, 0.8802, 0.8810) and DENCA_SO (0.8656, 0.8505, 0.8497)`).
- **Synthesis & Tabular Delegation**: Running text must synthesize qualitative trends or report a compact metric divergence range (`decreasing by 13.6 to 19.3 percentage points`). All exhaustive multi-metric figures must be delegated to clean, dedicated response tables (e.g., `Table R-BAcc`) or supplementary tables.

### Pillar 17: Strict Decoupling of Rebuttal Prose and Manuscript Revisions (禁止答辩信与修改正文机械雷同)
- **Distinct Communicative Roles**:
  - The **Response to Reviewers (Rebuttal)** is an interactive, deferential dialogue directly resolving the reviewer's specific questions.
  - The **Revised Manuscript** is an archival, permanent scientific record addressing a general international readership.
- **Strict Prohibition of Mechanical Copy-Paste**: Never copy-paste text verbatim between rebuttal analytical arguments and quoted manuscript sections (e.g., between item `(3)` of the rebuttal letter and `Section 4.2` of the paper). Both must be independently formulated with appropriate rhetorical focus.

### Pillar 18: One-to-One Close-Proximity Evidence Placement (论据与标蓝证据一对一就近对应原则)
- **Principle of Locality**: In all rebuttal responses, quoted manuscript revisions (highlighted in blue, `<font color="blue">“...”</font>`) must be placed directly beneath the specific numbered argument/action point `(1)`, `(2)`, etc. to which they physically correspond, rather than being collected into a disconnected, monolithic block at the end of the response.
- **Self-Contained Numbered Action Units**: Each numbered point must follow a complete closed loop:
  $$\text{Action Statement} \longrightarrow \text{Technical / Empirical Rationale} \longrightarrow \text{Transitional Lead-in} \longrightarrow \text{Blue Quoted Revision}$$
- **Zero Label Clutter inside Quotations**: Never prepend section labels (e.g., `In Section 4.1.3:`) inside the quotation marks, and strictly prohibit bracketed tags (e.g., `[Revision in Section 4.1.3]`). The location and scope of the revision must be smoothly introduced in the running transitional sentence (e.g., *"To reflect this enhancement, we have updated the evaluation protocol in Section 4.1.3 of the revised manuscript. The added content, which is highlighted in blue, is as follows:"*), leaving the quoted block as 100% pure, uninterrupted manuscript prose.

---

## 🔍 Automated Pre-Response & Pre-Compilation Verification Checklist

For **every user prompt, LaTeX edit, or section rewriting**, the agent must execute the following 34-point internal audit before outputting:

1. [ ] **Zero Fabricated Numbers Audit**: Is every empirical number strictly identical to Master Table in Protocol TRUTH-1? (e.g., KDS-EL pure accuracy = 0.9545, bIRIME features = 407.7, bIRIME runtime = 326.2 s). Is 0.9574 strictly banned as pure accuracy?
2. [ ] **Zero "50 Distinct Folds" Audit**: Has the unverified phrase "50 distinct folds" been completely eliminated and replaced by the standardized fixed 5-fold CV optimization instance protocol?
3. [ ] **W Update Formula Audit**: Does Equation~\eqref{eq:importance_update} include both improving reward and non-improving penalty matching `kds_el_twophase.py:122-142`?
4. [ ] **KER Perturbation Noise Audit**: Is the Gaussian perturbation in KER formulated as $\mathcal{N}(0, (\mathrm{std}(\mathbf{W}) + 10^{-5})^2)$ matching `utils.py:370`, rather than $10^{-12}$?
5. [ ] **IGPSO Description Audit**: Is IGPSO accurately described as ANOVA F-statistic contrast rather than a multi-layer perceptron (MLP)?
6. [ ] **Cross-Classifier S9 Honesty Audit**: Does discussion of Table S9 honestly disclose the slight accuracy drop on Colon for SVM and Random Forest, rather than claiming universal gains across all classifiers?
7. [ ] **Zero Baseline Terminology Check**: Is the word "baseline" / "baselines" completely eliminated from manuscript text, tables, captions, footnotes, and dialogue responses in favor of "competitor", "comparison method", "peer algorithm", or "benchmark"?
8. [ ] **Colloquialism & Literal Translation Scan**: Have all colloquial phrasing and literal translations ('one-to-one replacement' $\to$ 'greedy pairwise replacement', 'step by step', 'deal with', 'hand in hand', 'a lot of', 'make sure') been purged?
9. [ ] **Zero "Operator" for Proposed Components**: Are KDS-EL's own components strictly designated as "strategy" or "mechanism", never "operator"?
10. [ ] **Acronym Check**: Are there duplicate acronym expansions (e.g., `(KER)`, `(TPS)`)?
11. [ ] **Parameter Leakage Check**: Are specific numbers/parameters prematurely leaked into high-level descriptive sections?
12. [ ] **Parenthetical Clutter Audit**: Have all parenthetical inequalities (`($D \gg N_{\mathrm{samp}}$)`), parenthetical symbol dumps (`($\mathcal{P}_1$ and $\mathcal{P}_2$)`, `($N/2$)`, `($\mathbf{g}_{\mathrm{best},2}$)`), premature parameter values (`($k_{\mathrm{nn}} = 3$)`), dimension attractors (`($d \approx D/2$)`), and English explanatory clauses been purged?
13. [ ] **Narrative Rhythm Check**: Does the text use natural pipeline verbs instead of mechanical bulleted ordinals?
14. [ ] **Mathematical Rigor Check**: Are all variables given explicit mathematical domains? Are vector orientations consistent?
15. [ ] **Figure/Equation Cross-Ref Check**: Are all figure, table, and equation references resolved with 0 compilation errors?
16. [ ] **Causal Logic Check**: Does every proposed design component have a clearly articulated physical motivation?
17. [ ] **Elsevier Booktabs Check**: Do all tables strictly avoid vertical lines (`|`) and use standard `\toprule`, `\midrule`, `\bottomrule`?
18. [ ] **Statistical Verification Check**: Are standard deviation ($\pm \mathrm{Std}$) and Wilcoxon $+/-/\approx$ counts properly presented?
19. [ ] **Vector Graphic Check**: Are all embedded figures in pure vector `.pdf` format?
20. [ ] **Highlight Length Check**: Are Research Highlights strictly between 3–5 bullets and under 85 characters each?
21. [ ] **BibTeX Integrity Check**: Are all `\cite{...}` keys resolved without undefined reference warnings?
22. [ ] **Section 2 Narrative Chain**: Does each subsection follow the 4-step chain rather than mechanical literature listing?
23. [ ] **Section 2 Closed-Loop Check**: Are the three core gaps in Related Work in 1-to-1 correspondence with MII+AIR, KER, and TPS?
24. [ ] **Section-Wise Data Tier Audit**: Is the modified text strictly compliant with its designated Data Tier (Tier 1: zero data; Tier 2: macro landmarks only; Tier 3: setup constants only; Tier 4: table-free causal mechanisms)?
25. [ ] **Caption & Footnote Audit**: Are table captions ultra-concise noun phrases (6–15 words) free of formatting definitions? Are figure captions concise noun phrases (8–15 words)?
26. [ ] **Section 3 Code-Formula Mirror Audit**: Does every equation and algorithmic step strictly mirror the Python implementation in `code/algorithms/kds_el_twophase.py` and `code/utils.py`?
27. [ ] **Section 3 Modular Pseudocode Audit**: Are Algorithm 1 (KER) and Algorithm 2 (KDS-EL) fully declared with mathematical domains in `\Require`/`\Ensure`?
28. [ ] **Fair Budget Wording Audit**: Is "identical evaluation budgets" replaced by "identical population size ($N=20$) and iteration cutoff ($T=100$)"?
29. [ ] **Rebuttal Subject Alignment Audit**: Is KDS-EL strictly maintained as the primary subject, avoiding inadvertent framing of competitors (such as bIRIME) as the overall top performer?
30. [ ] **Zero Cohorts & Dominance Audit**: Have `cohorts` / `benchmark cohorts` and `majority-class dominance` been completely eradicated and replaced by `benchmark datasets` and `majority-class bias`?
31. [ ] **Zero Engineering Leak Audit**: Are internal pipeline terms like `deduplicated 19-dataset` or `570 competitor feature masks` completely purged?
32. [ ] **AI Adverb & Numerical Dumping Audit**: Are sensationalist adverbs (`Crucially, ...`) and consecutive inline multi-decimal lists purged in favor of qualitative synthesis and clean response tables?
33. [ ] **Rebuttal vs. Manuscript Decoupling Audit**: Are the response letter and revised manuscript text independently formulated with differentiated rhetorical registers, avoiding verbatim copy-paste?
34. [ ] **One-to-One Evidence Locality Audit**: Are blue-highlighted manuscript revisions placed directly beneath their corresponding numbered action points (rather than dumped at the end), free of bracketed tags or embedded section headers within quotation marks?
