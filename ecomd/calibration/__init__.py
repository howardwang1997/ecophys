"""Calibration-speed harness for Paper A's M1.6 headline shootout.

Records wall-clock × n_iters × final fact coverage tradeoffs for ECoMD,
ABIDES+SBI, and Lux-Marchesi+ABC. The ABIDES+SBI leg is blocked on H20
install (see `papers/proposal/paper_a_neurips_2027_state.md` §3.5);
ECoMD leg ships in batch 091.
"""

from ecomd.calibration.wallclock_harness import (
    CalibrationRun,
    analyze_calibration_dir,
    extract_run_metadata,
)

__all__ = ["CalibrationRun", "analyze_calibration_dir", "extract_run_metadata"]
