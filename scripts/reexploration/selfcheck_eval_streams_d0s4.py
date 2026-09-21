#!/usr/bin/env python3
"""C2(b) stream-replay self-check for the D0-S4 eval driver (remote, CPU).

Evidences the mechanism-cadence fix: with a FRESH build_inference_mechanism
per record, draw k's realized engine randomness is identical across cells
(same inputs -> same allocation) regardless of what any other record consumed,
while a single advancing mechanism would not replay.  Seconds-scale; run on a
worker node, never the Mac (PI compute rule).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(sys.argv[1] if len(sys.argv) > 1 else "/data/ecophys-campaign/repo")
SEED_ROOT = 11000
FLOW = [5.0, 10.0, 20.0, 40.0, 80.0, 160.0, 320.0, 640.0]
DEMAND = 3


def main() -> int:
    import torch

    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "scripts"))
    from ecomd.training.train_fact_surrogate import (
        Enforcement,
        EstimatorKind,
        FactSurrogateTrainConfig,
        Kernel,
        MechanismBackend,
        build_inference_mechanism,
    )

    torch.set_num_threads(1)

    def make(kernel: Kernel, draw_index: int):
        config = FactSurrogateTrainConfig(
            enforcement=Enforcement.THROUGH_M,
            estimator=EstimatorKind.STRAIGHT_THROUGH,
            kernel=kernel,
            mechanism_backend=MechanismBackend.ENGINE_BRIDGE,
        )
        return build_inference_mechanism(
            config, seed_root=SEED_ROOT, draw_index=draw_index
        )

    flow = torch.tensor(FLOW, dtype=torch.float32)
    checks: list[tuple[str, bool]] = []

    for kernel in (Kernel.FIFO, Kernel("random_unit_within_price")):
        # 1. one advancing mechanism: successive calls differ where the kernel
        #    consumes randomness; fifo is deterministic (G8(i)) so its calls
        #    coincide by design
        m = make(kernel, 3)
        a1 = m(flow, DEMAND)
        a2 = m(flow, DEMAND)
        distinct = not torch.equal(a1, a2)
        expected_distinct = kernel.value == "random_unit_within_price"
        checks.append((
            f"{kernel.value}: advancing mechanism successive calls "
            f"{'differ (state advances)' if expected_distinct else 'coincide (deterministic)'}",
            distinct == expected_distinct,
        ))

        # 2. fresh mechanisms, same draw: identical replay across "cells"
        m_x = make(kernel, 3)
        m_y = make(kernel, 3)
        b1 = m_x(flow, DEMAND)
        b2 = m_y(flow, DEMAND)
        checks.append((
            f"{kernel.value}: fresh per-cell mechanisms replay identically",
            torch.equal(b1, b2),
        ))
        checks.append((
            f"{kernel.value}: fresh replay equals first call of the advancing one",
            torch.equal(a1, b1),
        ))

        # 3. different draw index -> distinct realization (where randomness
        #    exists; fifo is deterministic so draws coincide by design)
        m_k4 = make(kernel, 4)
        c1 = m_k4(flow, DEMAND)
        if kernel.value == "random_unit_within_price":
            checks.append((
                "random_unit: draw 4 differs from draw 3",
                not torch.equal(b1, c1),
            ))

    failures = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if failures:
        raise SystemExit(f"{len(failures)} self-check(s) failed")
    print("selfcheck: all stream-replay checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
