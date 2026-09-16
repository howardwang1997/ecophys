"""Write outcome-free review inputs; this does not authorize or execute a sandbox."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def prepare(root: Path) -> None:
    directory = root / "research/paper_g/response_dx/preparation"
    directory.mkdir(parents=True, exist_ok=True)
    groups = {name: [f"g_response_dx_explore_{name}_{i:03d}" for i in range(count)]
              for name, count in (("train", 128), ("diagnostic", 32), ("response", 32))}
    units = sorted(unit for values in groups.values() for unit in values)
    confirmation = [f"g_response_dx_confirm_{i:03d}" for i in range(64)]
    for name, values in (("exploration", units), ("confirmation", confirmation)):
        (directory / f"{name}_members.txt").write_text("".join(u + "\n" for u in values))
    write_json(directory / "unit_contract.json", {
        "status": "preparation_only", "campaign_id": "g_response_dx_20260911",
        "groups": groups, "confirmation_units": confirmation,
        "exploration_seed": "PCG64(int.from_bytes(SHA256(unit_id UTF-8), big))",
        "initialization": "eight independent Gaussian cosine/sine pairs divided by k; spatial RMS normalized to one",
        "confirmation_outcomes_materialized": False,
    })
    write_json(directory / "confirmation_derivation.json", {
        "status": "future_rule_only_no_pulse_access",
        "source_documentation": "https://csrc.nist.gov/Projects/interoperable-randomness-beacons/beacon-20",
        "provider": "NIST Randomness Beacon v2",
        "release_gate": "DX terminal receipt and independently frozen D0 are both required",
        "time_rule": "T = ceil(max(DX terminal UTC epoch seconds, D0 freeze UTC epoch seconds)) + 600",
        "pulse_rule": "first signed pulse strictly after T; query pulse/time/next/{1000*T}",
        "endpoint_template": "https://beacon.nist.gov/beacon/2.0/pulse/time/next/{unix_milliseconds}",
        "verification": "verify pulse signature/certificate and timestamp > T; archive exact response and certificate",
        "derivation": "SHA256(UTF8('g_response_dx_confirm_v1\\n'+unit_id+'\\n') || bytes.fromhex(pulse.outputValue)); interpret digest as unsigned big-endian PCG64 seed",
        "failure_policy": "If the designated pulse or verification is unavailable, confirmation stays sealed; no alternate pulse/provider/seed.",
        "anti_selection": "D0 timestamp and protocol must be immutable before T; no refreeze or pulse replacement after observing a pulse.",
        "implementation": "No confirmation generator or retrieval code is included in this scientific image.",
    })
    branches = []
    index = 0
    for observed in (16, 4):
        for frames, augmented in ((1, False), (1, True), (4, False), (4, True)):
            for seed in (201, 202):
                index += 1
                branch = f"branch_{index:02d}"
                width = 64 if frames == 4 else (92 if observed == 16 else 74)
                config = {
                    "branch_id": branch, "epistemic_class": "sandbox_exploratory_tainted",
                    "groups": groups, "unit_ids": units,
                    "dynamics": {"modes": 16, "viscosity": .05, "interval": .05, "rtol": 1e-10, "atol": 1e-12},
                    "observed_modes": observed, "frames": frames, "augmented": augmented,
                    "width": width, "initialization_seed": seed,
                    "optimizer": {"seed": 402, "epochs": 200, "batch": 128, "lr": .001},
                    "qualify_reference": index == 1,
                    "reference_cpu_reservation": 1200 if index == 1 else 0,
                    "fit_cpu_reservation": 600,
                }
                path = directory / "configs" / f"{branch}.json"
                write_json(path, config)
                branches.append({"branch_id": branch, "config_ref": path.relative_to(root).as_posix(),
                                 "config_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                 "cpu_seconds": 1800 if index == 1 else 600,
                                 "output_bytes": 60000000})
    write_json(directory / "campaign_review.json", {
        "status": "preparation_not_machine_authorization", "public_evidence_eligible": False,
        "pi_decision_ref": "research/discovery/decisions/pi_paper_g_response_dx_preparation_20260911.yaml",
        "branches": branches, "total_cpu_seconds": 1200 + len(branches) * 600,
        "remaining_gates": ["image qualification", "independent runtime review", "schema-v2 immutable authorization", "protected-base authorization merge"],
        "multiplicity_family": "all_16_fits_and_all_four_responses_per_fit",
        "new_topic_or_route_promotion": False,
    })


if __name__ == "__main__":
    prepare(Path(__file__).resolve().parents[3])
