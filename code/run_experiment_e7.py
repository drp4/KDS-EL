"""
Experiment E7: Tumor Microarray Functional Enrichment and Feature Stability Analysis
=====================================================================================
Protocol Reference:
  - review_round_1/05_executable_experiment_plan.md (Section 10)
  - review_round_1/04_detailed_supplementary_experiment_design.md (Section 7 / Suite 6)

Core Protocol Principles:
  1. Strict Domain Demarcation:
      - Functional KEGG/GO enrichment is STRICTLY restricted to bona fide human tumor
        microarray datasets (Colon, Prostate, Leukaemia, DLBCL, SRBCT, Adenoma).
      - ABSOLUTELY NEVER executed on non-biological benchmarks (e.g. COIL20, ISOLET, BASEHOCK).
  2. Platform-Specific Background Universe (Anti-Inflation Protocol):
      - Hypergeometric tests MUST use the platform-specific universe U_D of unique mapped genes
        measured on the specific chip, NEVER the entire human genome (~20,000 genes).
  3. Feature Stability via Pairwise Jaccard:
      - Within each outer fold across 10 optimization seeds (45 pairwise comparisons):
          J(S_a, S_b) = |S_a cap S_b| / |S_a cup S_b|
      - Report mean, median, IQR, min, max, and subset size distributions.
      - Features selected >= 7/10 times designated as "70% High-Frequency Consensus Features".
  4. Pathological Tissue Heterogeneity Analysis in Colon:
      - Mandatory dual-condition evaluation:
          (A) Original enrichment including structural smooth-muscle markers (DES, ACTG2, MYH11).
          (B) Deconfounded enrichment with smooth-muscle markers explicitly removed.
      - Discloses that DES, ACTG2, and MYH11 reflect biopsy tissue architecture heterogeneity
        (epithelial carcinoma vs muscular mucosal layers) rather than tumor-intrinsic oncogenes.
  5. Rigorous Multiple Testing Correction:
      - Benjamini-Hochberg (BH) False Discovery Rate (FDR) control at fixed threshold q < 0.05.
      - Objective reporting: If q >= 0.05, truthfully report "No significant enrichment observed".
"""

import os
import sys
import json
import time
import copy
import argparse
import numpy as np
from datetime import datetime
from scipy.stats import hypergeom

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import DATA_DIR_TXT, DATA_DIR_MAT
from utils import load_dataset
from nested_evaluator import NestedSplitsManager, BudgetEvaluator, BlindOuterEvaluator
from algorithms_nested import NESTED_RUNNERS


def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (np.bool_, np.bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    return obj


# ══════════════════════════════════════════════════════════════════════════════
# Curated Standard Benchmark Pathways (KEGG & GO Biological Process)
# ══════════════════════════════════════════════════════════════════════════════

CANONICAL_PATHWAY_DATABASE = {
    # ── Oncogenic Signaling & Cancer Specific Pathways ──
    "KEGG_COLORECTAL_CANCER": [
        "APC", "CTNNB1", "KRAS", "BRAF", "TP53", "SMAD4", "TGFBR2", "PIK3CA",
        "PTEN", "MYC", "CCND1", "BAX", "MSH2", "MLH1", "PMS2", "MSH6", "CASP3",
        "CASP9", "AKT1", "MAPK1", "MAPK3", "FOS", "JUN", "TCF7L2", "AXIN1", "AXIN2",
    ],
    "KEGG_PATHWAYS_IN_CANCER": [
        "TP53", "RB1", "CDKN2A", "MYC", "CCND1", "CDK4", "MDM2", "PTEN", "PIK3CA",
        "AKT1", "MTOR", "EGFR", "ERBB2", "VEGFA", "HIF1A", "NFKB1", "RELA", "BCL2",
        "BAX", "CASP8", "CASP3", "FAS", "TRAF2", "STAT3", "JAK2", "KRAS", "BRAF",
        "MAPK1", "MAPK3", "WNT1", "CTNNB1", "APC", "SMAD2", "SMAD3", "SMAD4",
    ],
    "KEGG_WNT_SIGNALING_PATHWAY": [
        "WNT1", "WNT2", "WNT3A", "WNT5A", "FZD1", "FZD2", "DVL1", "DVL2", "AXIN1",
        "AXIN2", "GSK3B", "APC", "CTNNB1", "TCF7", "TCF7L1", "TCF7L2", "LEF1", "MYC",
        "CCND1", "PPARD", "DKK1", "DKK2", "SFRP1", "SFRP2", "CSNK1A1",
    ],
    "KEGG_CELL_CYCLE": [
        "CDK1", "CDK2", "CDK4", "CDK6", "CCNA1", "CCNA2", "CCNB1", "CCND1", "CCNE1",
        "RB1", "E2F1", "E2F2", "E2F3", "CDKN1A", "CDKN1B", "CDKN2A", "CDKN2B",
        "TP53", "ATM", "ATR", "CHEK1", "CHEK2", "CDC25A", "CDC25B", "CDC25C", "MCM2",
    ],
    "KEGG_APOPTOSIS": [
        "FAS", "FASLG", "TNFRSF10A", "TNFRSF10B", "FADD", "CASP8", "CASP10", "BID",
        "BAX", "BAK1", "BCL2", "BCL2L1", "CYCS", "APAF1", "CASP9", "CASP3", "CASP6",
        "CASP7", "XIAP", "BIRC2", "BIRC5", "TP53", "PMAIP1", "BBC3",
    ],
    "KEGG_P53_SIGNALING_PATHWAY": [
        "TP53", "MDM2", "MDM4", "CDKN1A", "CCND1", "CCNE1", "CDK2", "BAX", "BBC3",
        "PMAIP1", "FAS", "CASP8", "CASP3", "GADD45A", "RRM2", "PTEN", "TSC2", "SERPINE1",
    ],
    "KEGG_MAPK_SIGNALING_PATHWAY": [
        "EGFR", "GRB2", "SOS1", "HRAS", "KRAS", "NRAS", "RAF1", "BRAF", "MAP2K1",
        "MAP2K2", "MAPK1", "MAPK3", "MAPK8", "MAPK9", "MAPK14", "JUN", "FOS", "MYC",
    ],
    "KEGG_PROSTATE_CANCER": [
        "AR", "PTEN", "TP53", "RB1", "PIK3CA", "AKT1", "CCND1", "CDK4", "CDKN1B",
        "MYC", "BCL2", "EGFR", "ERBB2", "FGFR1", "PDGFA", "VEGFA", "GSTP1", "KLK3",
    ],
    "KEGG_ACUTE_MYELOID_LEUKEMIA": [
        "FLT3", "KIT", "NPM1", "DNMT3A", "IDH1", "IDH2", "TET2", "RUNX1", "CEBPA",
        "WT1", "TP53", "KRAS", "NRAS", "PML", "RARA", "MYH11", "CBFB", "RUNX1T1",
    ],
    # ── Structural & Heterogeneity Control Pathways ──
    "GO_SMOOTH_MUSCLE_CONTRACTION": [
        "DES", "ACTG2", "MYH11", "CNN1", "TAGLN", "ACTA2", "CALD1", "MYLK", "TPM1",
        "TPM2", "MYL9", "PRKG1", "PPP1R12A", "CAV1", "ITGA1", "ITGB1",
    ],
    "GO_CYTOSKELETON_ORGANIZATION": [
        "ACTA1", "ACTA2", "ACTB", "ACTG1", "ACTG2", "DES", "VIM", "MYH9", "MYH10",
        "MYH11", "TUBB", "TUBA1A", "MAP2", "MAPT", "FLNA", "FLNB", "TLN1", "VCL",
    ],
    "GO_IMMUNE_RESPONSE": [
        "CD4", "CD8A", "CD8B", "CD3D", "CD3E", "CD3G", "IL2", "IL4", "IL6", "IL10",
        "TNF", "IFNG", "HLA-A", "HLA-B", "HLA-C", "HLA-DRA", "CXCL8", "CCL2", "CD19",
    ],
    "GO_EXTRACELLULAR_MATRIX_ORGANIZATION": [
        "COL1A1", "COL1A2", "COL3A1", "COL4A1", "COL4A2", "FN1", "LAMA1", "LAMB1",
        "MMP1", "MMP2", "MMP9", "TIMP1", "TIMP2", "BGN", "DCN", "VCAN",
    ],
}

# Known tissue-heterogeneity smooth-muscle markers in Colon biopsy
COLON_SMOOTH_MUSCLE_CONFOUNDERS = {"DES", "ACTG2", "MYH11"}

PATHWAY_PANEL_METADATA = {
    "panel_name": "Curated Oncology & Muscle Architecture Benchmark Panel",
    "version": "1.0-exploratory",
    "n_pathways": len(CANONICAL_PATHWAY_DATABASE),
    "description": "Curated benchmark sets for oncogenic pathways and tissue-specific structural markers",
}


# ══════════════════════════════════════════════════════════════════════════════
# Feature Mapping Registry (UniGene & Affymetrix to Gene Symbols)
# ══════════════════════════════════════════════════════════════════════════════

def build_colon_probe_map():
    """
    Constructs deterministic mapping from Colon.txt UniGene Cluster IDs
    to standard HGNC Gene Symbols based on NCBI UniGene Build 33/34 & Alon et al. 1999.
    """
    mapping = {
        "Hsa.3004": "DES",       # Desmin (Line 2 / Feature 0)
        "Hsa.13491": "ACTG2",    # Actin Gamma 2, Smooth Muscle (Lines 3, 4 / Features 1, 2)
        "Hsa.37254": "MYH11",    # Myosin Heavy Chain 11, Smooth Muscle (Line 5 / Feature 3)
        "Hsa.541": "TAGLN",      # Transgelin
        "Hsa.20836": "CNN1",     # Calponin 1
        "Hsa.1977": "CALD1",     # Caldesmon 1
        "Hsa.44472": "TPM2",     # Tropomyosin 2
        "Hsa.3087": "VCL",       # Vinculin
        "Hsa.810": "FLNA",       # Filamin A
        "Hsa.692": "COL3A1",     # Collagen Type III Alpha 1
        "Hsa.1832": "COL1A2",    # Collagen Type I Alpha 2
        "Hsa.3331": "BGN",       # Biglycan
        "Hsa.36689": "FN1",      # Fibronectin 1
        "Hsa.6814": "SPARC",     # Osteonectin
        "Hsa.1224": "TIMP1",     # TIMP Metallopeptidase Inhibitor 1
        "Hsa.22762": "CTNNB1",   # Beta-catenin
        "Hsa.1006": "MYC",       # MYC Proto-oncogene
        "Hsa.2928": "CCND1",     # Cyclin D1
        "Hsa.1660": "TP53",      # Tumor Protein P53
        "Hsa.1410": "APC",       # APC Regulator of Wnt Signaling
        "Hsa.822": "MSH2",       # MutS Homolog 2
        "Hsa.3130": "MLH1",      # MutL Homolog 1
        "Hsa.2097": "KRAS",      # KRAS Proto-oncogene
        "Hsa.1491": "TGFBR2",    # TGF-Beta Receptor 2
        "Hsa.2796": "BAX",       # BCL2 Associated X
        "Hsa.1574": "CASP3",     # Caspase 3
        "Hsa.2471": "CASP9",     # Caspase 9
        "Hsa.1132": "MMP2",      # Matrix Metallopeptidase 2
        "Hsa.1134": "MMP9",      # Matrix Metallopeptidase 9
        "Hsa.627": "CDKN1A",     # Cyclin Dependent Kinase Inhibitor 1A (p21)
    }
    return mapping


def build_prostate_probe_map():
    """
    Constructs mapping from Prostate Affymetrix HG-U95Av2 probe sets to Gene Symbols.
    """
    mapping = {
        "100_g_at": "RABEP1",
        "1000_at": "MAPK3",
        "1001_at": "TIE1",
        "1002_f_at": "CYP2C19",
        "1003_s_at": "CXCR4",
        "31798_at": "AR",        # Androgen Receptor
        "38406_at": "KLK3",      # PSA (Prostate Specific Antigen)
        "37639_at": "PTEN",      # PTEN
        "1974_s_at": "TP53",     # TP53
        "32542_at": "MYC",       # MYC
        "32069_at": "CCND1",     # Cyclin D1
        "33880_at": "GSTP1",     # Glutathione S-Transferase P1
        "39642_at": "BCL2",      # BCL2
        "1600_at": "EGFR",       # EGFR
        "37028_at": "ERBB2",     # ERBB2 / HER2
        "38322_at": "VEGFA",     # VEGFA
        "32635_at": "CDKN1B",    # p27 Kip1
        "34320_at": "AKT1",      # AKT1
        "37160_at": "PIK3CA",    # PIK3CA
    }
    return mapping


def build_leukaemia_probe_map():
    """
    Constructs mapping from Leukaemia Affymetrix Hu6800 probe sets to Gene Symbols.
    """
    mapping = {
        "M19507_at": "MPO",      # Myeloperoxidase (AML marker)
        "M27891_at": "CST3",     # Cystatin C (AML marker)
        "X59417_at": "FAH",      # Fumarylacetoacetate
        "U05259_rna1_at": "MB-1", # CD79A (B-cell ALL marker)
        "M92287_at": "CCND3",    # Cyclin D3 (ALL marker)
        "U22376_cds2_at": "MYB", # MYB (ALL marker)
        "X17042_at": "PRG1",     # Proteoglycan 1
        "M23197_at": "CD33",     # CD33 (Myeloid marker)
        "M63138_at": "CTSD",     # Cathepsin D
        "M84526_at": "DF",       # Adipsin
        "M83652_s_at": "PFC",    # Properdin
        "X00437_at": "HLA-DRA",  # HLA-DRA
        "U50136_rna1_at": "LTC4S", # Leukotriene C4 Synthase
        "M13792_at": "ADA",      # Adenosine Deaminase
        "D88270_at": "CD19",     # CD19 B-cell marker
        "L09209_s_at": "APLP2",  # Amyloid Beta Precursor-Like
        "M28170_at": "CD13",     # ANPEP / CD13 (Myeloid marker)
        "M22960_at": "PPGB",     # Cathepsin A
        "M62762_at": "FLT3",     # FLT3 Receptor
        "U46499_at": "RUNX1",    # RUNX1 / AML1
    }
    return mapping


def get_dataset_probe_map(dataset_name):
    if dataset_name.lower() == "colon":
        return build_colon_probe_map()
    elif dataset_name.lower() == "prostate":
        return build_prostate_probe_map()
    elif dataset_name.lower() in ("leukaemia", "leukemia"):
        return build_leukaemia_probe_map()
    return {}


# ══════════════════════════════════════════════════════════════════════════════
# Feature Extraction and Probe Universe Construction
# ══════════════════════════════════════════════════════════════════════════════

def extract_probe_list(dataset_name):
    """
    Extracts the list of probe IDs from the original microarray dataset file.
    """
    file_path = os.path.join(DATA_DIR_TXT, f"{dataset_name}.txt")
    if not os.path.exists(file_path):
        return []

    probe_ids = []
    with open(file_path, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            parts = line_str.split("\t")
            probe_ids.append(parts[0].strip())
    return probe_ids


def construct_platform_universe(dataset_name, probe_ids, probe_map):
    """
    Constructs the platform-specific universe U_D of unique mapped gene symbols.
    Excludes Spike-in quality control probes (e.g. AFFX-*) and unmapped probes.
    """
    mapped_genes = set()
    unmapped_probes = []

    for idx, p in enumerate(probe_ids):
        # Exclude Spike-in technical probes
        if p.startswith("AFFX-"):
            continue

        if p in probe_map:
            mapped_genes.add(probe_map[p])
        else:
            # Fallback: if probe is already an identifiable gene symbol
            if not p.startswith("Hsa.") and not p.endswith("_at") and len(p) <= 10:
                mapped_genes.add(p)
            else:
                unmapped_probes.append((idx, p))

    universe = sorted(list(mapped_genes))
    coverage_rate = len(universe) / max(1, len(probe_ids))
    matched_probes = sum(1 for p in probe_ids if p in probe_map)

    return {
        "universe": universe,
        "size": len(universe),
        "total_probes": len(probe_ids),
        "matched_probes": matched_probes,
        "coverage_rate": float(coverage_rate),
        "unmapped_count": len(unmapped_probes),
        "is_limited_panel": bool(len(universe) < 100 or coverage_rate < 0.10),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Hypergeometric Over-Representation Analysis (ORA) with Benjamini-Hochberg FDR
# ══════════════════════════════════════════════════════════════════════════════

def perform_ora_enrichment(query_genes, universe_genes, pathway_db, alpha_fdr=0.05):
    """
    Executes platform-bounded Hypergeometric Over-Representation Test:
      M = N_universe (total mapped genes in chip platform)
      n = K_pathway (pathway genes present in universe)
      N = n_selected (query genes present in universe)
      k = k_overlap (overlap between query and pathway)
      p = P(X >= k) = hypergeom.sf(k - 1, M, n, N)
    Followed by Benjamini-Hochberg (BH) FDR correction.
    """
    universe_set = set(universe_genes)
    query_in_universe = set(query_genes).intersection(universe_set)
    M = len(universe_set)
    N = len(query_in_universe)

    if M == 0:
        return []

    test_records = []
    for path_name, path_genes in pathway_db.items():
        path_in_universe = set(path_genes).intersection(universe_set)
        n = len(path_in_universe)
        if n == 0:
            continue

        overlap_genes = query_in_universe.intersection(path_in_universe)
        k = len(overlap_genes)

        if k == 0 or N == 0:
            p_val = 1.0
        else:
            # Survival function sf(k-1) calculates P(X >= k)
            p_val = float(hypergeom.sf(k - 1, M, n, N))

        test_records.append({
            "pathway": path_name,
            "pathway_size_in_universe": n,
            "query_size_in_universe": N,
            "overlap_count": k,
            "overlap_genes": sorted(list(overlap_genes)),
            "gene_ratio": float(k / N) if N > 0 else 0.0,
            "bg_ratio": float(n / M) if M > 0 else 0.0,
            "p_raw": p_val,
        })

    # Benjamini-Hochberg FDR Correction
    total_tests = len(test_records)
    if total_tests == 0:
        return []

    # Sort ascending by p_raw
    sorted_records = sorted(test_records, key=lambda x: x["p_raw"])
    q_values = [1.0] * total_tests
    min_q = 1.0

    # Step-up calculation: q_i = min_{j >= i} (M / j * p_(j))
    for i in range(total_tests - 1, -1, -1):
        rank = i + 1
        q_calc = (total_tests / rank) * sorted_records[i]["p_raw"]
        min_q = min(min_q, q_calc)
        q_values[i] = min(1.0, min_q)

    for i in range(total_tests):
        sorted_records[i]["q_value"] = float(q_values[i])
        sorted_records[i]["significant"] = bool(q_values[i] < alpha_fdr)

    return sorted_records


# ══════════════════════════════════════════════════════════════════════════════
# Feature Stability Analysis (Pairwise Jaccard Index across 10 Seeds)
# ══════════════════════════════════════════════════════════════════════════════

def compute_pairwise_jaccard_stability(masks_list):
    """
    Computes all (10 choose 2) = 45 pairwise Jaccard similarities:
      J(S_a, S_b) = |S_a cap S_b| / |S_a cup S_b|
    Returns summary statistics: mean, median, IQR, min, max, consensus features.
    """
    n_runs = len(masks_list)
    if n_runs < 2:
        return {
            "mean": 0.0,
            "median": 0.0,
            "iqr": 0.0,
            "min": 0.0,
            "max": 0.0,
            "n_pairs": 0,
            "consensus_70_indices": [],
            "consensus_70_count": 0,
        }

    jaccards = []
    for i in range(n_runs):
        set_i = set(np.where(masks_list[i])[0])
        for j in range(i + 1, n_runs):
            set_j = set(np.where(masks_list[j])[0])
            intersection = len(set_i.intersection(set_j))
            union = len(set_i.union(set_j))
            if union == 0:
                jacc = 0.0
            else:
                jacc = float(intersection / union)
            jaccards.append(jacc)

    jacc_arr = np.array(jaccards)
    p25 = float(np.percentile(jacc_arr, 25))
    p75 = float(np.percentile(jacc_arr, 75))
    iqr = p75 - p25

    # 70% High-Frequency Consensus Features (selected in >= 7 of 10 runs)
    dim = len(masks_list[0])
    counts = np.zeros(dim, dtype=int)
    for m in masks_list:
        counts += m.astype(int)

    consensus_threshold = int(np.ceil(0.70 * n_runs))
    consensus_indices = np.where(counts >= consensus_threshold)[0].tolist()

    return {
        "mean": float(np.mean(jacc_arr)),
        "median": float(np.median(jacc_arr)),
        "iqr": float(iqr),
        "min": float(np.min(jacc_arr)),
        "max": float(np.max(jacc_arr)),
        "n_pairs": len(jaccards),
        "consensus_70_indices": consensus_indices,
        "consensus_70_count": len(consensus_indices),
    }


DEFAULT_SEEDS = [7, 30, 1, 42, 100, 2024, 999, 1234, 555, 888]


# ══════════════════════════════════════════════════════════════════════════════
# Master Execution Pipeline for Experiment E7
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_e7(
    datasets=None,
    algorithms=None,
    outer_folds=None,
    seeds=None,
    max_fes=2000,
    e5_runs_file=None,
    out_dir=None,
    verbose=True,
):
    """
    Executes stability and platform-bounded enrichment analysis on gene expression datasets.
    Can ingest pre-computed masks from E5 (e5_runs_file) or execute on-the-fly.
    """
    t0_all = time.perf_counter()
    if datasets is None:
        datasets = ["Colon", "Prostate", "Leukaemia"]
    if algorithms is None:
        algorithms = ["KDS_EL_TwoPhase", "MEL", "bIRIME"]
    if outer_folds is None:
        outer_folds = [1]  # Default to outer fold 1 for stability analysis
    if seeds is None:
        seeds = DEFAULT_SEEDS
    if out_dir is None:
        out_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e7_enrichment")

    os.makedirs(out_dir, exist_ok=True)
    splits_dir = os.path.join(PROJECT_ROOT, "output", "nested_cv", "splits")

    # Check for E5 precomputed runs file fallback
    if e5_runs_file is None:
        default_e5 = os.path.join(PROJECT_ROOT, "output", "nested_cv", "e5_generalization", "e5_detailed_runs.json")
        if os.path.exists(default_e5):
            e5_runs_file = default_e5

    e5_mask_db = {}
    if e5_runs_file and os.path.exists(e5_runs_file):
        try:
            with open(e5_runs_file, "r", encoding="utf-8") as f:
                e5_data = json.load(f)
            loaded_count = 0
            for rec in e5_data:
                # Rigorous validation: check audit pass and budget match
                if not rec.get("audit", {}).get("all_passed", False):
                    continue
                if max_fes and rec.get("max_fes", 0) != max_fes:
                    continue
                k = (rec["dataset"], rec["algorithm"], rec["outer_fold"], rec["seed"])
                e5_mask_db[k] = rec["selected_indices"]
                loaded_count += 1
            print(f"Loaded {loaded_count} validated pre-computed runs from E5 (audit-passed, Max_FEs={max_fes}): {e5_runs_file}")
        except Exception as e:
            print(f"Warning: Failed to load E5 runs file: {e}")

    # Safety Guard: Strictly verify that NO non-gene datasets are present
    disallowed_non_genes = [
        "COIL20", "ISOLET", "BASEHOCK", "PCMAC", "RELATHE", "madelon",
        "USPS", "HAPTDataSet", "MultipleFeaturesDigit",
    ]
    for ds in datasets:
        if ds in disallowed_non_genes:
            raise ValueError(
                f"Protocol Violation in E7: Non-biological dataset '{ds}' cannot undergo KEGG/GO enrichment!"
            )

    print("\n" + "=" * 80)
    print("STARTING EXPERIMENT E7: TUMOR MICROARRAY ENRICHMENT & STABILITY ANALYSIS")
    print(f"Target Gene Datasets ({len(datasets)}): {datasets}")
    print(f"Comparison Algorithms ({len(algorithms)}): {algorithms}")
    print(f"Outer Folds: {outer_folds} | Optimization Seeds ({len(seeds)}): {seeds}")
    print(f"Output Directory: {out_dir}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    stability_results = {}
    enrichment_results = {}
    colon_heterogeneity_results = {}

    splits_mgr = NestedSplitsManager(splits_dir)

    for ds in datasets:
        print(f"\n── Processing Microarray Dataset: {ds} ──")
        X, y = load_dataset(ds, DATA_DIR_TXT, DATA_DIR_MAT)
        N_samples, D = X.shape

        probe_ids = extract_probe_list(ds)
        probe_map = get_dataset_probe_map(ds)
        universe_info = construct_platform_universe(ds, probe_ids, probe_map)

        print(
            f"  Platform Universe U: {universe_info['size']} unique genes "
            f"(Mapping coverage: {universe_info['coverage_rate']*100:.1f}%)"
        )

        stability_results[ds] = {}
        enrichment_results[ds] = {}

        for algo in algorithms:
            print(f"  > Evaluating Algorithm: {algo}")
            fold_stabilities = []
            all_masks_for_algo = []

            for f in outer_folds:
                outer_splits = splits_mgr.get_outer_splits(ds, y, n_splits=5, seed=42)
                train_idx, test_idx = outer_splits[f - 1]
                X_tr, y_tr = X[train_idx], y[train_idx]
                inner_splits = splits_mgr.get_inner_splits(ds, f, y_tr, n_splits=5, seed=42)

                runner_fn = NESTED_RUNNERS[algo]
                opts = {
                    "N": 20,
                    "thres": 0.60,
                    "weight_decay": 0.99,
                    "ws_phase1": [0.70, 0.30],
                    "ws_phase2": [0.95, 0.05],
                    "ws": [0.90, 0.10],
                    "elite_k": 3,
                }

                fold_masks = []
                for s in seeds:
                    key = (ds, algo, f, s)
                    if key in e5_mask_db:
                        mask = np.zeros(D, dtype=bool)
                        mask[e5_mask_db[key]] = True
                        fold_masks.append(mask)
                    else:
                        evaluator = BudgetEvaluator(
                            X_train_outer=X_tr,
                            y_train_outer=y_tr,
                            inner_splits=inner_splits,
                            max_fes=max_fes,
                            knn_k=3,
                            use_fast_knn=False,
                        )
                        res = runner_fn(X_tr, y_tr, evaluator, opts, seed=s)
                        fold_masks.append(res["mask"])

                all_masks_for_algo.extend(fold_masks)

                # Stability within current outer fold across seeds
                f_stab = compute_pairwise_jaccard_stability(fold_masks)
                fold_stabilities.append(f_stab)

            # Summarize stability across evaluated folds
            mean_jacc = float(np.mean([fs["mean"] for fs in fold_stabilities]))
            median_jacc = float(np.mean([fs["median"] for fs in fold_stabilities]))
            iqr_jacc = float(np.mean([fs["iqr"] for fs in fold_stabilities]))
            min_jacc = float(np.min([fs["min"] for fs in fold_stabilities]))
            max_jacc = float(np.max([fs["max"] for fs in fold_stabilities]))

            # Global consensus: strictly features selected in >= 70% of ALL evaluated runs across folds
            total_runs = len(all_masks_for_algo)
            if total_runs > 0:
                stacked_masks = np.vstack(all_masks_for_algo)
                freqs = np.mean(stacked_masks, axis=0)
                global_consensus_indices = np.where(freqs >= 0.70)[0].tolist()
            else:
                global_consensus_indices = []

            stab_info = {
                "mean": mean_jacc,
                "median": median_jacc,
                "iqr": iqr_jacc,
                "min": min_jacc,
                "max": max_jacc,
                "n_pairs_per_fold": fold_stabilities[0]["n_pairs"] if fold_stabilities else 0,
                "n_folds_evaluated": len(fold_stabilities),
                "total_runs_evaluated": total_runs,
                "consensus_70_indices": global_consensus_indices,
                "consensus_70_count": len(global_consensus_indices),
                "fold_consensus_counts": [len(fs["consensus_70_indices"]) for fs in fold_stabilities],
            }
            stability_results[ds][algo] = stab_info

            print(
                f"    Jaccard Stability (across {len(fold_stabilities)} fold(s)): Mean={stab_info['mean']:.4f} | "
                f"Median={stab_info['median']:.4f} | IQR={stab_info['iqr']:.4f} | "
                f"Global Consensus Features (>=70% all runs)={stab_info['consensus_70_count']}"
            )

            # 2. Extract consensus gene symbols
            consensus_symbols = []
            for idx in global_consensus_indices:
                if idx < len(probe_ids):
                    pid = probe_ids[idx]
                    sym = probe_map.get(pid, pid)
                    consensus_symbols.append(sym)
                else:
                    consensus_symbols.append(f"Feature_{idx}")

            consensus_symbols_unique = sorted(list(set(consensus_symbols)))

            # Track mapping to platform universe
            universe_set = set(universe_info["universe"])
            mapped_in_universe = sorted(list(set(consensus_symbols_unique).intersection(universe_set)))
            effective_query_size = len(mapped_in_universe)
            unmapped_consensus = sorted(list(set(consensus_symbols_unique) - universe_set))

            # 3. Perform Platform-Bounded ORA Enrichment
            enrich_records = perform_ora_enrichment(
                query_genes=consensus_symbols_unique,
                universe_genes=universe_info["universe"],
                pathway_db=CANONICAL_PATHWAY_DATABASE,
                alpha_fdr=0.05,
            )
            enrichment_status = "evaluated" if effective_query_size > 0 else "insufficient_annotation"
            enrichment_results[ds][algo] = {
                "consensus_genes": consensus_symbols_unique,
                "mapped_consensus_genes": mapped_in_universe,
                "unmapped_consensus_genes": unmapped_consensus,
                "effective_query_size": effective_query_size,
                "status": enrichment_status,
                "enrichment": enrich_records,
            }

            sig_count = sum(1 for r in enrich_records if r["significant"])
            if effective_query_size == 0:
                print(f"    Platform ORA Enrichment: Insufficient annotation (effective mapped query size = 0, {len(consensus_symbols_unique)} consensus features unmapped)")
            else:
                print(f"    Platform ORA Enrichment: {sig_count} pathways significant at FDR q < 0.05 (effective query size: {effective_query_size})")

            # 4. Special Colon Tissue Heterogeneity Experiment for KDS-EL
            if ds.lower() == "colon" and algo == "KDS_EL_TwoPhase":
                print("\n  >> Running Colon Biopsy Smooth-Muscle Tissue Heterogeneity Control...")
                detected_confounders = sorted(list(COLON_SMOOTH_MUSCLE_CONFOUNDERS.intersection(set(consensus_symbols_unique))))

                # Condition A: With smooth muscle markers
                enrich_with_sm = enrich_records

                # Condition B: Deconfounded (DES, ACTG2, MYH11 removed)
                if len(detected_confounders) > 0 and effective_query_size > 0:
                    deconfounded_genes = [
                        g for g in consensus_symbols_unique
                        if g not in COLON_SMOOTH_MUSCLE_CONFOUNDERS
                    ]
                    enrich_without_sm = perform_ora_enrichment(
                        query_genes=deconfounded_genes,
                        universe_genes=universe_info["universe"],
                        pathway_db=CANONICAL_PATHWAY_DATABASE,
                        alpha_fdr=0.05,
                    )
                else:
                    deconfounded_genes = list(consensus_symbols_unique)
                    enrich_without_sm = copy.deepcopy(enrich_with_sm)

                colon_heterogeneity_results = {
                    "original_genes": consensus_symbols_unique,
                    "deconfounded_genes": deconfounded_genes,
                    "removed_confounders": detected_confounders,
                    "effective_query_size": effective_query_size,
                    "status": enrichment_status,
                    "has_valid_annotation": bool(effective_query_size > 0),
                    "enrichment_with_smooth_muscle": enrich_with_sm,
                    "enrichment_without_smooth_muscle": enrich_without_sm,
                }
                print(
                    f"    Original Genes ({len(consensus_symbols_unique)}): {len(enrich_with_sm)} tested pathways."
                )
                print(
                    f"    Deconfounded Genes ({len(deconfounded_genes)}): Removed {colon_heterogeneity_results['removed_confounders']}."
                )

    # Save artifacts
    stability_json_path = os.path.join(out_dir, "e7_stability_results.json")
    with open(stability_json_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(stability_results), f, indent=2)

    enrichment_json_path = os.path.join(out_dir, "e7_enrichment_results.json")
    with open(enrichment_json_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(enrichment_results), f, indent=2)

    heterogeneity_json_path = os.path.join(out_dir, "e7_colon_heterogeneity.json")
    with open(heterogeneity_json_path, "w", encoding="utf-8") as f:
        json.dump(sanitize_for_json(colon_heterogeneity_results), f, indent=2)

    # Generate Markdown Synthesis Report
    report_path = os.path.join(out_dir, "e7_biomedical_enrichment_report.md")
    generate_e7_markdown_report(
        stability_results,
        enrichment_results,
        colon_heterogeneity_results,
        report_path,
        time.perf_counter() - t0_all,
    )

    elapsed_total = time.perf_counter() - t0_all
    print("\n" + "=" * 80)
    print(f"EXPERIMENT E7 COMPLETED in {elapsed_total:.2f}s!")
    print(f"Artifacts saved:")
    print(f"  - Stability Analysis JSON: {stability_json_path}")
    print(f"  - Platform Enrichment JSON: {enrichment_json_path}")
    print(f"  - Colon Heterogeneity JSON: {heterogeneity_json_path}")
    print(f"  - Academic Markdown Report: {report_path}")
    print("=" * 80 + "\n")


def generate_e7_markdown_report(stability_res, enrich_res, heterogeneity_res, out_path, elapsed_time):
    """
    Renders academic markdown synthesis report complying with AGENTS.md.
    """
    lines = []
    lines.append("# E7: Tumor Microarray Functional Enrichment & Stability Analysis Report\n")
    lines.append(f"- **Execution Timestamp**: {datetime.now().isoformat()}")
    lines.append(f"- **Protocol Reference**: `review_round_1/05_executable_experiment_plan.md` (Section 10)")
    lines.append(f"- **Evaluated Gene Benchmarks**: Colon, Prostate, Leukaemia")
    lines.append(f"- **Platform-Bounded Universe**: Defined by unique genes mapped to chip platform")
    lines.append(f"- **FDR Multiple Testing Standard**: Benjamini-Hochberg (BH) Step-Up ($q < 0.05$)")
    lines.append(f"- **Total Elapsed Time**: `{elapsed_time:.2f} s`\n")

    lines.append("> **Formal Methodological Demarcation**:")
    lines.append("> In strict accordance with the biomedical rigor protocols defined in AGENTS.md, all functional over-representation tests are conducted within the platform-specific background universe U of the respective microarray chip, strictly prohibiting whole-genome background inflation. The 70% consensus features identified across 10 optimization runs are treated as descriptive signatures, and empirical observations are evaluated with falsifiable hypotheses under FDR control.\n")

    lines.append("## 1. Algorithmic Feature Stability Matrix (Pairwise Jaccard Similarity across 10 Runs)\n")
    lines.append("| Dataset | Algorithm | Mean Jaccard | Median Jaccard | IQR | [Min, Max] | 70% Consensus Features ($N_{70}$) |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

    for ds, algo_dict in stability_res.items():
        for algo, info in algo_dict.items():
            lines.append(
                f"| **`{ds}`** | **`{algo}`** | **{info['mean']:.4f}** | "
                f"{info['median']:.4f} | {info['iqr']:.4f} | "
                f"[{info['min']:.3f}, {info['max']:.3f}] | **{info['consensus_70_count']}** |"
            )

    lines.append("\n## 2. Platform-Bounded ORA Enrichment Results (FDR $q < 0.05$)\n")
    if not enrich_res:
        lines.append("*No enrichment results available.*\n")
    else:
        for ds, algo_dict in enrich_res.items():
            lines.append(f"### {ds} Microarray Benchmark\n")
            for algo, info in algo_dict.items():
                consensus = info.get("consensus_genes", [])
                eff_query = info.get("effective_query_size", len(consensus))
                status = info.get("status", "evaluated" if eff_query > 0 else "insufficient_annotation")
                sig_pathways = [r for r in info.get("enrichment", []) if r.get("significant", False)]
                lines.append(f"#### `{algo}` (Query: {len(consensus)} Consensus Feature(s), Effective Mapped Query: {eff_query})\n")
                if status == "insufficient_annotation" or eff_query == 0:
                    lines.append(f"*Insufficient annotation: None of the {len(consensus)} consensus features could be mapped to the curated benchmark panel universe. Formal hypergeometric enrichment is not assessable under this panel.*\n")
                elif not sig_pathways:
                    lines.append("*No canonical pathways achieved statistical significance after Benjamini-Hochberg FDR adjustment ($q < 0.05$).*\n")
                else:
                    lines.append("| Canonical Pathway | Overlap ($k / n$) | Gene Ratio | Raw $p$-value | Adjusted $q$-value | Overlapping Genes |")
                    lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
                    for r in sig_pathways:
                        overlap_genes = r.get("overlap_genes", [])
                        genes_str = ", ".join(overlap_genes[:6])
                        if len(overlap_genes) > 6:
                            genes_str += ", ..."
                        lines.append(
                            f"| **`{r.get('pathway', '')}`** | {r.get('overlap_count', 0)}/{r.get('pathway_size_in_universe', 0)} | "
                            f"{r.get('gene_ratio', 0.0):.3f} | {r.get('p_raw', 1.0):.4e} | **{r.get('q_value', 1.0):.4e}** | {genes_str} |"
                        )
                    lines.append("")

    if heterogeneity_res and heterogeneity_res.get("original_genes") is not None:
        lines.append("\n## 3. Colon Tissue Heterogeneity Analysis: Smooth-Muscle Deconfounding\n")
        orig_cnt = len(heterogeneity_res.get("original_genes", []))
        deconf_cnt = len(heterogeneity_res.get("deconfounded_genes", []))
        removed = heterogeneity_res.get("removed_confounders", [])
        eff_query = heterogeneity_res.get("effective_query_size", orig_cnt)
        status = heterogeneity_res.get("status", "evaluated" if eff_query > 0 else "insufficient_annotation")

        lines.append(f"- **Original 70% Consensus Genes**: `{orig_cnt}` features")
        lines.append(f"- **Structural Smooth-Muscle Confounders Detected in Mapped Set**: `{removed}` ({len(removed)} identified)")
        lines.append(f"- **Deconfounded Feature Signature**: `{deconf_cnt}` features\n")

        if orig_cnt > 0 and (eff_query == 0 or status == "insufficient_annotation"):
            lines.append("> **Histological Assessment (Indeterminate Due to Insufficient Annotation)**:")
            lines.append("> None of the consensus probe features could be resolved to annotated gene identities (effective mapped query size = 0). Consequently, it is indeterminate whether smooth-muscle structural markers (e.g., `DES`, `ACTG2`, `MYH11`) were selected or absent in this feature subset. Histological deconfounding cannot be evaluated without verifiable feature annotations.")
        elif len(removed) > 0:
            lines.append("### Comparative Enrichment Profiles (With vs. Without Structural Markers)\n")
            orig_sig = [r for r in heterogeneity_res.get("enrichment_with_smooth_muscle", []) if r.get("significant", False)]
            deconf_sig = [r for r in heterogeneity_res.get("enrichment_without_smooth_muscle", []) if r.get("significant", False)]

            lines.append(f"- **Original Condition (with smooth-muscle markers)**: `{len(orig_sig)}` significant pathways.")
            for r in orig_sig:
                lines.append(f"  * `{r['pathway']}`: Overlap={r['overlap_count']}, $q = {r['q_value']:.4e}$")

            lines.append(f"- **Deconfounded Condition (without smooth-muscle markers)**: `{len(deconf_sig)}` significant pathways.")
            for r in deconf_sig:
                lines.append(f"  * `{r['pathway']}`: Overlap={r['overlap_count']}, $q = {r['q_value']:.4e}$")

            lines.append("\n> **Pathological Context & Plausible Tissue Sampling Hypothesis**:")
            lines.append(f"> Predefined smooth-muscle structural markers ({', '.join(removed)}) were identified within the mapped consensus feature subset. While literature reports (such as Alon et al., 1999) suggest that normal colon biopsies typically contain full-thickness muscularis mucosae layers whereas adenocarcinoma specimens are dominated by epithelial neoplastic cells, computational feature selection alone cannot independently establish the physical tissue origin of these signals. Histological biopsy composition remains a plausible literature-supported explanation for their selection, but warrants independent biological validation rather than definitive algorithmic proof.")
        else:
            lines.append("> **Histological Assessment**:")
            lines.append("> Among the resolved consensus gene symbols, none of the predefined smooth-muscle structural markers (`DES`, `ACTG2`, `MYH11`) were identified. Within the scope of the annotated features, the subset contains no detectable structural smooth-muscle markers, and deconfounding does not alter the feature set.")

    lines.append("\n## 4. Academic Findings & Submission Protocol Alignment\n")
    # Aggregate summary metrics
    all_jaccards = []
    total_sig_pathways = 0
    total_effective_queries = 0
    total_consensus_genes = 0
    evaluated_algos_count = 0

    for ds, algo_dict in stability_res.items():
        for algo, info in algo_dict.items():
            all_jaccards.append(info.get("mean", 0.0))
            evaluated_algos_count += 1

    for ds, algo_dict in enrich_res.items():
        for algo, info in algo_dict.items():
            consensus = info.get("consensus_genes", [])
            total_consensus_genes += len(consensus)
            eff = info.get("effective_query_size", 0)
            total_effective_queries += eff
            sig_cnt = sum(1 for r in info.get("enrichment", []) if r.get("significant", False))
            total_sig_pathways += sig_cnt

    mean_global_jaccard = float(np.mean(all_jaccards)) if all_jaccards else 0.0

    # 1. Feature Stability statement
    if evaluated_algos_count == 0 or total_consensus_genes == 0:
        lines.append("1. **Feature Stability & Convergence**: No algorithm runs or consensus features were available for evaluation. Feature stability cannot be assessed.")
    elif total_sig_pathways > 0:
        lines.append(f"1. **Feature Stability & Convergence**: Across independent stochastic runs, the algorithms exhibit moderate pairwise feature overlap (mean Jaccard = {mean_global_jaccard:.4f}), while identifying consensus features that significantly over-represent specific canonical pathways (FDR $q < 0.05$). This indicates localized functional alignment despite stochastic feature variation.")
    elif total_effective_queries == 0:
        lines.append(f"1. **Feature Stability & Convergence**: Across independent stochastic runs, feature subsets exhibit a mean pairwise Jaccard similarity of {mean_global_jaccard:.4f}. However, consensus features could not be mapped to the curated panel universe, precluding statistical confirmation of functional convergence under this panel.")
    else:
        lines.append(f"1. **Feature Stability & Convergence**: Across independent stochastic runs, feature subsets exhibit a mean pairwise Jaccard similarity of {mean_global_jaccard:.4f}, and no canonical pathways in the curated panel achieve FDR-adjusted significance ($q < 0.05$). The observed variation reflects stochastic exploration across highly collinear feature spaces in small-sample microarray regimes, without evidence of functional convergence under the current curated panel.")

    # 2. Panel Scope statement
    if evaluated_algos_count == 0:
        lines.append("2. **Curated Panel Scope**: No platform universe was evaluated.")
    else:
        lines.append("2. **Curated Panel Scope**: Over-representation analysis was conducted strictly against a curated exploratory panel of canonical pathways. Given the limited mapping coverage of legacy microarray probe files, results are interpreted as targeted benchmark explorations rather than exhaustive genome-wide functional profiling.")

    # 3. Histological Assessment statement
    if not heterogeneity_res or heterogeneity_res.get("original_genes") is None:
        lines.append("3. **Histological Assessment**: Colon tissue heterogeneity deconfounding was not evaluated in this run configuration.\n")
    else:
        orig_cnt = len(heterogeneity_res.get("original_genes", []))
        eff_query = heterogeneity_res.get("effective_query_size", orig_cnt)
        status = heterogeneity_res.get("status", "evaluated" if eff_query > 0 else "insufficient_annotation")
        removed = heterogeneity_res.get("removed_confounders", [])

        if orig_cnt == 0:
            lines.append("3. **Histological Assessment**: No consensus features were generated; histological deconfounding could not be evaluated.\n")
        elif eff_query == 0 or status == "insufficient_annotation":
            lines.append("3. **Histological Assessment**: Because consensus features could not be mapped to verified gene annotations, the presence or absence of smooth-muscle structural markers is indeterminate and cannot be evaluated.\n")
        elif len(removed) > 0:
            lines.append(f"3. **Histological Assessment**: Specified smooth-muscle markers ({', '.join(removed)}) were observed within the mapped consensus feature set. While literature points to biopsy tissue composition disparity as a plausible contributing factor, this mechanism remains a hypothesis requiring independent biological validation rather than an algorithmically verified certainty.\n")
        else:
            lines.append("3. **Histological Assessment**: None of the specified smooth-muscle markers (`DES`, `ACTG2`, `MYH11`) appeared in the resolved consensus features, indicating that within the annotated subset, these candidate structural markers were not retained.\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Run Experiment E7: Tumor Microarray Functional Enrichment & Stability.")
    parser.add_argument("--datasets", nargs="+", default=["Colon", "Prostate", "Leukaemia"], help="Target gene datasets.")
    parser.add_argument("--algorithms", nargs="+", default=["KDS_EL_TwoPhase", "MEL", "bIRIME"], help="Algorithms.")
    parser.add_argument("--folds", nargs="+", type=int, default=[1], help="Outer folds (default: 1).")
    parser.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS, help="Random seeds.")
    parser.add_argument("--max-fes", type=int, default=2000, help="Budget Max_FEs.")
    parser.add_argument("--e5-runs-file", type=str, default=None, help="Path to E5 detailed runs JSON to reuse pre-computed masks.")
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory path.")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose stdout logs.")

    args = parser.parse_args()

    run_experiment_e7(
        datasets=args.datasets,
        algorithms=args.algorithms,
        outer_folds=args.folds,
        seeds=args.seeds,
        max_fes=args.max_fes,
        e5_runs_file=args.e5_runs_file,
        out_dir=args.out_dir,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
