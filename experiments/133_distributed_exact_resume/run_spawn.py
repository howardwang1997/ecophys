"""Launch local Gloo ranks with a file-store rendezvous."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

STAGE = Path(__file__).with_name("run_stage.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nproc", type=int, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--stage-record", type=Path, required=True)
    parser.add_argument("--n-iters", type=int, required=True)
    parser.add_argument("--stop-after", type=int)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    if args.nproc < 2:
        raise ValueError("run_spawn is only needed for nproc >= 2")
    rendezvous = args.stage_record.with_suffix(f".{time.time_ns()}.store")
    command = [
        sys.executable,
        str(STAGE),
        "--checkpoint",
        str(args.checkpoint),
        "--stage-record",
        str(args.stage_record),
        "--n-iters",
        str(args.n_iters),
        "--seed",
        str(args.seed),
        "--device",
        "cpu",
    ]
    if args.stop_after is not None:
        command.extend(("--stop-after", str(args.stop_after)))
    processes: list[subprocess.Popen[str]] = []
    for rank in range(args.nproc):
        environment = os.environ.copy()
        environment.update(
            {
                "RANK": str(rank),
                "WORLD_SIZE": str(args.nproc),
                "LOCAL_RANK": str(rank),
                "DIST_BACKEND": "gloo",
                "DIST_INIT_METHOD": f"file://{rendezvous}",
                "OMP_NUM_THREADS": "1",
            }
        )
        processes.append(
            subprocess.Popen(
                command,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    failures: list[str] = []
    for rank, process in enumerate(processes):
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            failures.append(
                f"rank {rank} exited {process.returncode}\nstdout:\n{stdout}\n"
                f"stderr:\n{stderr}"
            )
    if failures:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        raise RuntimeError("\n".join(failures))


if __name__ == "__main__":
    main()
