"""EcoMD v1+ (MACE-lite + Student-t + learnable β) Mac smoke runner.

Reuses experiments/006_ecomd_v1/run.py's pipeline but redirects output to
this experiment's results/ directory.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
SIBLING_RUN = HERE.parents[1] / "006_ecomd_v1" / "run.py"

spec = importlib.util.spec_from_file_location("_v1_runner", SIBLING_RUN)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Override output directory to point at THIS experiment's results/.
module.OUT = HERE.parent / "results"

if __name__ == "__main__":
    if not any(arg.startswith("--config") for arg in sys.argv[1:]):
        sys.argv.extend(["--config", str(HERE.parent / "config_mac_smoke.yaml")])
    module.main()
