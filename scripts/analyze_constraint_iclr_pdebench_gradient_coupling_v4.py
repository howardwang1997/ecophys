"""Join gradient coupling to the construct-corrected enforcement-cube target."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from analyze_constraint_iclr_pdebench import load_config, read_records
from analyze_constraint_iclr_pdebench_enforcement_cube import (
    cube_seed_effects,
    validate_cube_records,
)
from analyze_constraint_iclr_pdebench_gradient_coupling import (
    _mean_summary,
    spearman_bootstrap,
    validate_diagnostic_records,
    validate_factorial_join_pairing,
)
from constraint_iclr_common import sha256_file, stable_seed


def analyze_gradient_coupling_v4(
    diagnostic_records: list[dict[str, Any]],
    factorial_records: list[dict[str, Any]],
    cube_records: list[dict[str, Any]],
    checkpoint_lock: dict[str, Any],
    config: dict[str, Any],
    *,
    factorial_records_sha256: str,
    factorial_analysis_sha256: str,
    checkpoint_lock_sha256: str,
) -> dict[str, Any]:
    diagnostic = validate_diagnostic_records(diagnostic_records, config)
    factorial, cube = validate_cube_records(
        cube_records,
        factorial_records,
        checkpoint_lock,
        config,
        core_records_sha256=factorial_records_sha256,
        core_analysis_sha256=factorial_analysis_sha256,
        checkpoint_lock_sha256=checkpoint_lock_sha256,
    )
    seeds = [int(value) for value in config["seeds"]]
    validate_factorial_join_pairing(diagnostic, factorial, seeds)
    case = str(config["evaluation"]["primary_case"])
    horizon = int(config["evaluation"]["primary_horizon"])
    draws = 50_000

    d_absolute = np.asarray(
        [
            diagnostic[(seed, "absolute")]["one_step"][
                "one_step_enforcement_credit"
            ]
            for seed in seeds
        ],
        dtype=np.float64,
    )
    d_residual = np.asarray(
        [
            diagnostic[(seed, "residual")]["one_step"][
                "one_step_enforcement_credit"
            ]
            for seed in seeds
        ],
        dtype=np.float64,
    )
    d_interaction = d_absolute - d_residual
    effects = cube_seed_effects(factorial, cube, seeds, case, horizon)
    training_interaction_projected_inference = effects["T1"]
    bundled_interaction = effects["I_bundle"]
    cosine_absolute = np.asarray(
        [diagnostic[(seed, "absolute")]["gradients"]["cosine"] for seed in seeds],
        dtype=np.float64,
    )
    cosine_residual = np.asarray(
        [diagnostic[(seed, "residual")]["gradients"]["cosine"] for seed in seeds],
        dtype=np.float64,
    )
    return {
        "schema_version": "constraint-iclr-gradient-coupling-analysis-v2",
        "benchmark_id": config["benchmark_id"],
        "record_count": len(diagnostic_records),
        "factorial_record_count": len(factorial_records),
        "cube_record_count": len(cube_records),
        "seeds": seeds,
        "primary_case": case,
        "primary_horizon": horizon,
        "integrity_gates_passed": True,
        "one_step": {
            "absolute": _mean_summary(d_absolute, name="D_A_v4", draws=draws),
            "residual": _mean_summary(d_residual, name="D_R_v4", draws=draws),
            "interaction": _mean_summary(
                d_interaction, name="D_I_v4", draws=draws
            ),
        },
        "gradient_cosine": {
            "absolute": _mean_summary(
                cosine_absolute, name="cos_A_v4", draws=draws
            ),
            "residual": _mean_summary(
                cosine_residual, name="cos_R_v4", draws=draws
            ),
        },
        "primary_final_training_interaction": _mean_summary(
            training_interaction_projected_inference,
            name="T1_final_v4",
            draws=draws,
        ),
        "primary_mechanistic_association": spearman_bootstrap(
            d_interaction,
            training_interaction_projected_inference,
            draws=draws,
            seed=stable_seed(20260901, "gradient-coupling-v4:T1-spearman"),
        ),
        "secondary_bundled_interaction": _mean_summary(
            bundled_interaction, name="I_bundle_final_v4", draws=draws
        ),
        "secondary_bundled_association": spearman_bootstrap(
            d_interaction,
            bundled_interaction,
            draws=draws,
            seed=stable_seed(20260901, "gradient-coupling-v4:I-bundle-spearman"),
        ),
        "estimand_note": (
            "The primary rollout target is T1: the coordinate interaction of training "
            "through the projector with projected inference at both endpoints. The "
            "hard-versus-free bundled interaction remains secondary."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/constraint_iclr/"
            "pdebench_advection_fno_gradient_coupling_v4_20260901.yaml"
        ),
    )
    parser.add_argument("--diagnostic-input", type=Path)
    parser.add_argument("--factorial-input", type=Path)
    parser.add_argument("--cube-input", type=Path)
    parser.add_argument("--checkpoint-lock", type=Path)
    parser.add_argument("--factorial-analysis", type=Path, required=True)
    parser.add_argument("--cube-analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config_path = args.config if args.config.is_absolute() else root / args.config
    config = load_config(config_path)
    cube_config = config["cube"]

    def resolved_path(value: Path | str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else root / path

    diagnostic_path = resolved_path(args.diagnostic_input or config["gradient_output"])
    factorial_path = resolved_path(args.factorial_input or config["output"])
    cube_path = resolved_path(args.cube_input or cube_config["output"])
    checkpoint_lock_path = resolved_path(
        args.checkpoint_lock or cube_config["checkpoint_lock"]
    )
    factorial_analysis_path = resolved_path(args.factorial_analysis)
    cube_analysis_path = resolved_path(args.cube_analysis)
    output_path = resolved_path(args.output)

    factorial_analysis = json.loads(
        factorial_analysis_path.read_text(encoding="utf-8")
    )
    cube_analysis = json.loads(cube_analysis_path.read_text(encoding="utf-8"))
    factorial_sha256 = sha256_file(factorial_path)
    cube_sha256 = sha256_file(cube_path)
    checkpoint_lock_sha256 = sha256_file(checkpoint_lock_path)
    factorial_analysis_sha256 = sha256_file(factorial_analysis_path)
    if factorial_analysis.get("input_sha256") != factorial_sha256:
        raise RuntimeError("factorial analysis is not bound to the supplied JSONL")
    expected_cube_bindings = {
        "derived_input_sha256": cube_sha256,
        "core_input_sha256": factorial_sha256,
        "core_analysis_sha256": factorial_analysis_sha256,
        "checkpoint_lock_sha256": checkpoint_lock_sha256,
    }
    for field, expected in expected_cube_bindings.items():
        if cube_analysis.get(field) != expected:
            raise RuntimeError(f"cube analysis has the wrong {field} binding")
    if not cube_analysis.get("integrity_gates_passed", False):
        raise RuntimeError("cube analysis did not pass its integrity gates")

    result = analyze_gradient_coupling_v4(
        read_records(diagnostic_path),
        read_records(factorial_path),
        read_records(cube_path),
        json.loads(checkpoint_lock_path.read_text(encoding="utf-8")),
        config,
        factorial_records_sha256=factorial_sha256,
        factorial_analysis_sha256=factorial_analysis_sha256,
        checkpoint_lock_sha256=checkpoint_lock_sha256,
    )
    result.update(
        {
            "diagnostic_input_sha256": sha256_file(diagnostic_path),
            "factorial_input_sha256": factorial_sha256,
            "cube_input_sha256": cube_sha256,
            "checkpoint_lock_sha256": checkpoint_lock_sha256,
            "factorial_analysis_sha256": factorial_analysis_sha256,
            "cube_analysis_sha256": sha256_file(cube_analysis_path),
            "config_sha256": sha256_file(config_path),
        }
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"analysis={output_path}")
    print(f"analysis_sha256={sha256_file(output_path)}")


if __name__ == "__main__":
    main()
