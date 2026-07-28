"""
KDS-EL 算法注册表
==================
所有算法的统一入口。
"""
from .bpso import run_BPSO
from .sawde import run_SaWDE
from .fwpso import run_FWPSO
from .mel import run_MEL
from .mel_mi_reinit import run_MEL_MI
from .kds_el_drs import run_KDS_EL_DRS
from .kds_el_ker import run_KDS_EL_KER
from .kds_el_no_pool import run_KDS_EL_NoPool
from .kds_el_twophase import run_KDS_EL_TwoPhase
from .kds_el import run_KDS_EL
from .pso_csm import run_PSO_CSM
from .igpso import run_IGPSO
from .nsga2_fs import run_NSGA_II_FS
from .mopso_fs import run_MOPSO_FS
from .moead_fs import run_MOEA_D_FS
from .fmopso_fs import run_fMOPSO_FS
from .vgs_moea import run_VGS_MOEA
from .wmopso_fs import run_W_MOPSO_FS

RUNNERS = {
    "BPSO":            run_BPSO,
    "SaWDE":           run_SaWDE,
    "FWPSO":           run_FWPSO,
    "MEL":             run_MEL,
    "MEL_MI":          run_MEL_MI,
    "KDS_EL_DRS":      run_KDS_EL_DRS,
    "KDS_EL_KER":      run_KDS_EL_KER,
    "KDS_EL_NoPool":   run_KDS_EL_NoPool,
    "KDS_EL_TwoPhase": run_KDS_EL_TwoPhase,
    "KDS_EL":          run_KDS_EL,
    "PSO_CSM":         run_PSO_CSM,
    "IGPSO":           run_IGPSO,
    "NSGA-II-FS":      run_NSGA_II_FS,
    "MOPSO-FS":        run_MOPSO_FS,
    "MOEA-D-FS":       run_MOEA_D_FS,
    "fMOPSO-FS":       run_fMOPSO_FS,
    "VGS-MOEA":        run_VGS_MOEA,
    "W-MOPSO-FS":      run_W_MOPSO_FS,
}
