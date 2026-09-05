"""CLI conformance runner for the lab-asset reference engine (A-2, deliverable D-2.4).

Runs the same checks as the pytest suite in a single deterministic pass and prints a
machine-readable verdict for the A-2 qualification record. Exit code 0 on pass, 1 on fail.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_TARGETS = (
    "tests/test_lab_asset_conformance.py",
    "tests/test_lab_asset_adapter.py",
)


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *TEST_TARGETS, "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    print(result.stdout.strip())
    passed = result.returncode == 0
    print(f"lab_asset_conformance_suite={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
