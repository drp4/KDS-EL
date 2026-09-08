# -*- coding: utf-8 -*-
"""
KDS-EL Table Generator Forwarder (Elsevier Standard)
Delegates directly to code/generate_tables.py which implements the authoritative
12-method single-objective comparison suite (purged of all MOFS methods, strictly adhering to AGENTS.md).
"""
import sys
import subprocess
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
TARGET_SCRIPT = PROJ_ROOT / "code" / "generate_tables.py"

if __name__ == "__main__":
    cmd = [sys.executable, str(TARGET_SCRIPT)] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))
