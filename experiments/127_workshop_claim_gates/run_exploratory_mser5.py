"""Run the post-primary MSER-5 analytic comparator declared in the exploratory amendment."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, TypeAlias, cast

import numpy as np
import numpy.typing as npt

from ecomd.eval.stylized_facts import hill_tail_index

ArrayF: TypeAlias = npt.NDArray[np.float64]
REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_ANALYTIC_ROOT = Path("/private/tmp/ecophys-exp127-analytic-output")
DEFAULT_OUTPUT = EXPERIMENT_DIR / "EXPLORATORY_MSER5_RESULTS.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mser5_w(calibration: ArrayF, batch_size: int = 5, max_w: int = 4000) -> int:
    if calibration.ndim != 2 or calibration.shape[1] < batch_size:
        raise ValueError("calibration must be a trajectory-by-time matrix")
    if batch_size < 1 or max_w < 0:
        raise ValueError("batch_size must be positive and max_w non-negative")
    time_series = np.mean(np.abs(calibration), axis=0)
    n_batches = time_series.size // batch_size
    batches = np.mean(time_series[: n_batches * batch_size].reshape(n_batches, batch_size), axis=1)
    max_delete = min(n_batches // 2, max_w // batch_size)
    reverse_sum = np.cumsum(batches[::-1], dtype=np.float64)[::-1]
    reverse_square_sum = np.cumsum(np.square(batches[::-1]), dtype=np.float64)[::-1]
    starts = np.arange(max_delete + 1)
    remaining = n_batches - starts
    sums = reverse_sum[starts]
    square_sums = reverse_square_sum[starts]
    sse = np.maximum(square_sums - np.square(sums) / remaining, 0.0)
    scores = sse / np.square(remaining)
    return int(np.argmin(scores)) * batch_size


def repository_state() -> dict[str, Any]:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (FileNotFoundError, subprocess.CalledProcessError):
        if (REPO_ROOT / "ARTIFACT_MANIFEST.json").is_file():
            return {
                "git_sha": "anonymous-artifact-snapshot",
                "clean": True,
                "status_entries": [],
            }
        raise
    return {"git_sha": sha, "clean": not status, "status_entries": status}


def run_comparator(analytic_root: Path, output: Path, allow_dirty: bool = False) -> dict[str, Any]:
    state = repository_state()
    if not state["clean"] and not allow_dirty:
        raise RuntimeError("formal exploratory analysis requires a clean worktree")
    params = cast(
        dict[str, Any], json.loads((EXPERIMENT_DIR / "ANALYTIC_PARAMS.json").read_text())
    )
    generation_path = analytic_root / "generation_manifest.json"
    generation = cast(dict[str, Any], json.loads(generation_path.read_text()))
    artifact_hashes = {
        str(record["artifact"]): str(record["artifact_sha256"])
        for record in generation["artifacts"]
    }
    rows: list[dict[str, Any]] = []
    for model in ("garch_t", "ar1_sv"):
        for condition in params[model]["conditions"]:
            filename = f"{model}__{condition}.npy"
            path = analytic_root / filename
            if sha256_file(path) != artifact_hashes[filename]:
                raise RuntimeError(f"analytic artifact hash mismatch: {filename}")
            matrix = np.load(path, mmap_mode="r", allow_pickle=False)
            for pseudo_checkpoint in range(int(params["pseudo_checkpoints_per_condition"])):
                start = pseudo_checkpoint * int(params["pseudo_checkpoint_size"])
                stop = start + int(params["pseudo_checkpoint_size"])
                checkpoint = np.asarray(matrix[start:stop], dtype=np.float64)
                n_calibration = int(params["calibration_per_pseudo_checkpoint"])
                calibration = checkpoint[:n_calibration]
                heldout = checkpoint[n_calibration:]
                selected_w = mser5_w(calibration)
                hill_values = [
                    float(hill_tail_index(row[selected_w:selected_w + 4000], k_frac=0.05).estimate)
                    for row in heldout
                ]
                rows.append(
                    {
                        "model": model,
                        "condition": condition,
                        "pseudo_checkpoint": pseudo_checkpoint,
                        "selected_w": selected_w,
                        "detected_transient": selected_w > 0,
                        "heldout_hill_median": float(np.median(hill_values)),
                        "heldout_hill_values": hill_values,
                    }
                )
    _attach_reference_errors(rows, analytic_root, params)
    result = {
        "schema_version": 1,
        "status": "post_primary_exploratory",
        "amendment": "EXPLORATORY_AMENDMENT_2026-08-07.md",
        "repository": state,
        "generation_manifest_sha256": sha256_file(generation_path),
        "method": {
            "name": "MSER-5",
            "input": "calibration across-trajectory mean absolute returns",
            "batch_size": 5,
            "max_w": 4000,
            "scoring_length": 4000,
        },
        "summary": _summarize(rows),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def _attach_reference_errors(
    rows: list[dict[str, Any]], analytic_root: Path, params: dict[str, Any]
) -> None:
    reference_conditions = {"garch_t": "long_burn", "ar1_sv": "stationary"}
    references: dict[tuple[str, int], float] = {}
    for model, condition in reference_conditions.items():
        matrix = np.load(
            analytic_root / f"{model}__{condition}.npy", mmap_mode="r", allow_pickle=False
        )
        for pseudo_checkpoint in range(int(params["pseudo_checkpoints_per_condition"])):
            start = pseudo_checkpoint * int(params["pseudo_checkpoint_size"])
            stop = start + int(params["pseudo_checkpoint_size"])
            n_calibration = int(params["calibration_per_pseudo_checkpoint"])
            heldout = np.asarray(matrix[start:stop], dtype=np.float64)[n_calibration:]
            estimates = [
                float(hill_tail_index(trajectory[:4000], k_frac=0.05).estimate)
                for trajectory in heldout
            ]
            references[(model, pseudo_checkpoint)] = float(np.median(estimates))
    for row in rows:
        reference = references[(str(row["model"]), int(row["pseudo_checkpoint"]))]
        row["hill_reference"] = reference
        row["hill_abs_error_to_reference"] = abs(float(row["heldout_hill_median"]) - reference)


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stationary = {("garch_t", "long_burn"), ("ar1_sv", "stationary")}
    cold = {
        ("garch_t", "cold_low"),
        ("garch_t", "cold_high"),
        ("ar1_sv", "cold_low"),
        ("ar1_sv", "cold_high"),
    }
    stationary_rows = [
        row for row in rows if (str(row["model"]), str(row["condition"])) in stationary
    ]
    cold_rows = [row for row in rows if (str(row["model"]), str(row["condition"])) in cold]
    condition_rows: list[dict[str, Any]] = []
    for model, condition in dict.fromkeys(
        (str(row["model"]), str(row["condition"])) for row in rows
    ):
        group = [
            row
            for row in rows
            if str(row["model"]) == model and str(row["condition"]) == condition
        ]
        condition_rows.append(
            {
                "model": model,
                "condition": condition,
                "n": len(group),
                "selection_rate": float(np.mean([row["detected_transient"] for row in group])),
                "median_selected_w": float(np.median([row["selected_w"] for row in group])),
                "median_hill_abs_error": float(
                    np.median([row["hill_abs_error_to_reference"] for row in group])
                ),
                "mean_hill_abs_error": float(
                    np.mean([row["hill_abs_error_to_reference"] for row in group])
                ),
            }
        )
    return {
        "stationary_unnecessary_discard_count": int(
            sum(bool(row["detected_transient"]) for row in stationary_rows)
        ),
        "stationary_n": len(stationary_rows),
        "stationary_unnecessary_discard_rate": float(
            np.mean([row["detected_transient"] for row in stationary_rows])
        ),
        "cold_selection_count": int(sum(bool(row["detected_transient"]) for row in cold_rows)),
        "cold_n": len(cold_rows),
        "cold_selection_rate": float(np.mean([row["detected_transient"] for row in cold_rows])),
        "cold_median_hill_abs_error": float(
            np.median([row["hill_abs_error_to_reference"] for row in cold_rows])
        ),
        "cold_mean_hill_abs_error": float(
            np.mean([row["hill_abs_error_to_reference"] for row in cold_rows])
        ),
        "by_condition": condition_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analytic-root", type=Path, default=DEFAULT_ANALYTIC_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--allow-dirty", action="store_true", help="debug only")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_comparator(args.analytic_root, args.output, allow_dirty=args.allow_dirty)
    print(json.dumps({"output": str(args.output), "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
