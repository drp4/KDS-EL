"""
KDS-EL 算法注册表
==================
所有算法的统一入口。
"""
from .bpso import run_BPSO
from .sawde import run_SaWDE
from .fwpso import run_FWPSO
from .mel import run_MEL
from .mel_nhd import run_MEL_NHD
from .kds_el_ker import run_KDS_EL_KER
from .kds_el import run_KDS_EL
from .pso_csm import run_PSO_CSM
from .igpso import run_IGPSO

RUNNERS = {
    "BPSO":            run_BPSO,
    "SaWDE":           run_SaWDE,
    "FWPSO":           run_FWPSO,
    "MEL":             run_MEL,
    "MEL_NHD":         run_MEL_NHD,
    "KDS_EL_KER":      run_KDS_EL_KER,
    "KDS_EL":          run_KDS_EL,
    "PSO_CSM":         run_PSO_CSM,
    "IGPSO":           run_IGPSO,
}
