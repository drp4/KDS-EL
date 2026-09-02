# AGENTS.md — KDS-EL Academic Writing, Rigor & Elsevier Submission Protocols

This document defines the strict academic standards, mathematical conventions, experimental protocols, and Elsevier-specific submission guidelines governing all writing, revising, and LaTeX code generation for the **KDS-EL** research paper targeting top-tier Elsevier SCI journals (e.g., *Applied Soft Computing* [ASOC], *Expert Systems with Applications* [ESWA], *Swarm and Evolutionary Computation* [SWEVO], *Information Sciences*, *Knowledge-Based Systems*).

Every generation and modification must strictly comply with all criteria outlined below.

---

## 📌 Section I: Core Academic Writing & Narrative Protocols

### Pillar 1: Zero Parenthetical Clutter & Duplicate Acronyms
- **No Duplicate Acronym Expansions**: Once an acronym (e.g., `KDS-EL`, `KER`, `TPS`, `PSO`, `MI`) is defined in the Abstract/Introduction, do not expand it again with parenthetical tags like `Knowledge-Guided Elite Refinement (KER)`. Use the formal terms directly (e.g., `the KER operator`, `the dynamic TPS strategy`).
- **No Premature Parameter Dumping**: In high-level architecture/framework sections (such as Section 3.1), never hardcode specific hyperparameter values (e.g., `(wf,1 = 0.30)`, `(wa,2 = 0.95)`, `(theta = 0.60)`) or inline formula fragments in parentheses. Specific parameter values belong strictly in dedicated technical subsections and the experimental parameter setup table.
- **Eliminate Pseudo-Code Conditions in Text**: Never write parenthetical code-like logic in prose (e.g., `(rank(i) <= N/2)` or `(MI_init_ratio = 0.50)`). Translate them into rigorous academic English (e.g., *"the superior half of the swarm is preserved intact..."*).

---

### Pillar 2: Natural Pipeline Narrative & Temporal Transitions
- **Avoid Mechanical Ordinal Lists**: Do not construct paragraphs with repetitive, rigid ordinals (`First, ... Second, ... Third, ... Finally, ...`).
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
- **Figure/Table Self-Containment**: Captions must be descriptive enough that a reader can grasp the core mechanism purely from the visual artifact.
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
- **Zero Vertical Lines**: In accordance with Elsevier style guides, **never include vertical rules (`|`)** in tables.
- **Booktabs Macros**: Construct all tables using `\toprule`, `\midrule`, and `\bottomrule` from the `booktabs` package.
- **Statistical Significance Highlighting**: Highlight the best-performing metric in **boldface** and underline the second-best across all comparison tables.
- **Multi-Row & Column Sizing**: Use `\cmidrule(lr){...}` to separate grouped benchmark categories (e.g., Single-Objective vs. Multi-Objective FS).

---

### Pillar 11: Statistical Testing Gold Standard for Evolutionary Algorithms
- **Independent Runs**: Report all quantitative metrics across at least 30 independent runs in the standard format: $\mathrm{Mean} \pm \mathrm{Std}$.
- **Wilcoxon Signed-Rank Test**: Conduct non-parametric Wilcoxon signed-rank tests at significance level $\alpha = 0.05$. Report pairwise statistical counts as $+ / - / \approx$ (win / loss / tie) in table summaries.
- **Friedman Global Ranking & Post-Hoc Correction**: Apply the Friedman test to establish overall algorithmic rankings across multi-dataset benchmarks, followed by post-hoc **Holm-Bonferroni** or **Nemenyi** corrections to guard against family-wise error accumulation.

---

### Pillar 12: Vector Figures & Resolution Standards
- **Vector PDF Format**: All workflow schematics, convergence curves, and radar plots must be generated and embedded as vector PDFs (`.pdf`), never raster images (`.png` / `.jpg`).
- **Standardized Multi-Panel Layout**: Multi-part figures must use `\begin{subfigure}` with standardized sub-labels `(a)`, `(b)`, `(c)` and synchronized aspect ratios.
- **Font & Linewidth Legibility**: Minimum font size within figures must remain fully legible ($> 7\text{ pt}$) when scaled to single-column width ($8.5\text{ cm}$) or full double-column width ($17.5\text{ cm}$).

---

### Pillar 13: Literature Benchmark Coverage & Citation Freshness
- **Balanced Baseline Hierarchy**: Benchmark against three distinct categories:
  1. *Classical filter & wrapper methods* (e.g., BPSO, IG-PSO);
  2. *State-of-the-art Single-Objective Swarm Feature Selectors* (e.g., SaWDE, MEL);
  3. *State-of-the-art Multi-Objective Evolutionary Algorithms* (e.g., NSGA-II-FS, MOEA/D-FS, W-MOPSO-FS, fMOPSO-FS).
- **Recent Literature Density**: Ensure at least $30\%$ of cited references are from top-tier venues published within the last 3–4 years (2022–2026).
- **BibTeX Completeness**: Every reference must include complete author lists, journal title, volume, issue, page range, year, and DOI where applicable.

---

## 🔍 Automated Pre-Response & Pre-Compilation Verification Checklist

For **every user prompt, LaTeX edit, or section rewriting**, the agent must execute the following 12-point internal audit before outputting:

1. [ ] **Acronym Check**: Are there duplicate acronym expansions (e.g., `(KER)`, `(TPS)`)?
2. [ ] **Parameter Leakage Check**: Are specific numbers/parameters prematurely leaked into high-level descriptive sections?
3. [ ] **Parenthetical Scan**: Are there redundant parenthetical explanations or code-like conditions?
4. [ ] **Narrative Rhythm Check**: Does the text use natural pipeline verbs instead of mechanical bulleted ordinals?
5. [ ] **Mathematical Rigor Check**: Are all variables given explicit mathematical domains? Are vector orientations consistent?
6. [ ] **Figure/Equation Cross-Ref Check**: Are all figure, table, and equation references resolved with 0 compilation errors?
7. [ ] **Causal Logic Check**: Does every proposed design component have a clearly articulated physical motivation?
8. [ ] **Elsevier Booktabs Check**: Do all tables strictly avoid vertical lines (`|`) and use standard `\toprule`, `\midrule`, `\bottomrule`?
9. [ ] **Statistical Verification Check**: Are standard deviation ($\pm \mathrm{Std}$) and Wilcoxon $+/-/\approx$ counts properly presented?
10. [ ] **Vector Graphic Check**: Are all embedded figures in pure vector `.pdf` format?
11. [ ] **Highlight Length Check**: Are Research Highlights strictly between 3–5 bullets and under 85 characters each?
12. [ ] **BibTeX Integrity Check**: Are all `\cite{...}` keys resolved without undefined reference warnings?
