"""Generate the staged g42 authorization payload under preparation/authorization/.

Draft, non-operative: nothing here creates or edits any canonical
research/discovery/ file. Re-runnable; pass --stamp to re-stamp and re-hash
the whole chain (members -> unit contract/configs/derivation -> provenance ->
snapshot -> asset fingerprint -> partition -> manifest -> genesis entry ->
decision) for the promotion-time re-freeze. The snapshot covers source and
preparation files only (dx-precedent shape); partition/provenance/snapshot
themselves are pinned directly by the manifest, so the asset fingerprint
sha256(canonical_json({asset_key, kind, snapshot_sha256, source, version}))
stays acyclic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SANDBOX_ID = "g42_fixed_knot_moves_20260916"
CAMPAIGN_ID = "g42_fixed_knot_moves_20260916"
ENGINE_VERSION = "g42_fixed_knot_moves_engine_1.1.1"
IMAGE_DIGEST = "sha256:3428e3025c64a17173365290951b780fcf9a0b2e998ffaa8e3445057cc31deda"
LAUNCHER_REF = "scripts/run_research_discovery_sandbox.py"
LAUNCHER_SHA = "4e8ae8a7aa1a3ed2b5d26fd765c5fa524d9167873218bfa2f4421ff0b33654ef"
HANDLER_REF = "scripts/quarantine_research_discovery_sandbox.py"
HANDLER_SHA = "5cda87cf44ac50e78f9dd23ee4e268ec4099252d3536bdb1841db62bc2d67e4e"
HYPOTHESIS_ID = "context_move_selection_matched_budget_decorrelation"
MULTIPLICITY_FAMILY_ID = "g42_fixed_knot_moves_7_cells_4_policies_8_seeds"
UNIT_NAMESPACE = "g42_fixed_knot_frozen_unit_ids_v1"
SEEDS = tuple(range(8))
CONFIRMATION_PREFIX = "g42_confirm_"

# cell: (knot, n_vertices, temperature, proposals, thin, branch_id,
#        branch_cpu_seconds). Unit cpu = (branch_cpu - 128) // 32: the launcher
# kills the container at wall time branch_cpu - 42 s and caps the docker cpu
# ulimit at branch_cpu, so per-unit caps must sum below the wall deadline or a
# fully cpu-capped branch (32 units each ending cpu_budget at its cap) is
# killed and the whole sandbox quarantined with no retry.
CELLS: dict[str, dict[str, Any]] = {
    "n128_01_t1": {
        "knot": "0_1", "n_vertices": 128, "temperature": 1.0,
        "proposals": 400_000, "thin": 1000, "branch_id": "g42_b01",
        "branch_cpu_seconds": 1920, "branch_order": 1,
    },
    "n128_01_t3": {
        "knot": "0_1", "n_vertices": 128, "temperature": 3.0,
        "proposals": 400_000, "thin": 1000, "branch_id": "g42_b02",
        "branch_cpu_seconds": 1920, "branch_order": 2,
    },
    "n160_31_t1": {
        "knot": "3_1", "n_vertices": 160, "temperature": 1.0,
        "proposals": 400_000, "thin": 1000, "branch_id": "g42_b03",
        "branch_cpu_seconds": 1760, "branch_order": 3,
    },
    "n160_31_t3": {
        "knot": "3_1", "n_vertices": 160, "temperature": 3.0,
        "proposals": 400_000, "thin": 1000, "branch_id": "g42_b04",
        "branch_cpu_seconds": 1760, "branch_order": 4,
    },
    "n256_41_t1": {
        "knot": "4_1", "n_vertices": 256, "temperature": 1.0,
        "proposals": 180_000, "thin": 500, "branch_id": "g42_b05",
        "branch_cpu_seconds": 2080, "branch_order": 5,
    },
    "n256_41_t3": {
        "knot": "4_1", "n_vertices": 256, "temperature": 3.0,
        "proposals": 180_000, "thin": 500, "branch_id": "g42_b06",
        "branch_cpu_seconds": 2080, "branch_order": 6,
    },
    "n96_01_t1": {
        "knot": "0_1", "n_vertices": 96, "temperature": 1.0,
        "proposals": 500_000, "thin": 1000, "branch_id": "g42_b07",
        "branch_cpu_seconds": 1440, "branch_order": 7,
    },
}

POLICY_TAGS = ("p0", "p1", "p2", "p3")
CONFIRMATION_POLICIES = ("p0", "p3")

CONTEXT_THRESHOLDS: dict[int, list[float]] = {
    96: [20.6, 107.2],
    128: [25.4, 150.5],
    160: [29.5, 195.4],
    256: [40.3, 339.7],
}


def policy_spec(tag: str, n_vertices: int) -> dict[str, Any]:
    if tag == "p0":
        return {"kind": "uniform"}
    if tag == "p1":
        return {"kind": "table", "weights": {"corner": 4, "pivot": 1, "self_loop": 1}}
    if tag == "p2":
        return {"kind": "table", "weights": {"corner": 1, "pivot": 4, "self_loop": 1}}
    if tag == "p3":
        return {
            "kind": "table",
            "weights": {"corner": 1, "pivot": 1, "self_loop": 1},
            "context": {
                "observable": "rg2_bucket",
                "thresholds": CONTEXT_THRESHOLDS[n_vertices],
                "multipliers": {
                    "corner": [4, 2, 1],
                    "pivot": [1, 2, 4],
                    "self_loop": [1, 1, 1],
                },
            },
        }
    raise ValueError(f"unknown policy tag {tag}")


def unit_cpu_seconds(branch_cpu_seconds: int) -> int:
    return (branch_cpu_seconds - 128) // 32


def unit_config(cell: str, tag: str, seed: int) -> dict[str, Any]:
    spec = CELLS[cell]
    branch_id = spec["branch_id"]
    unit_cpu = unit_cpu_seconds(spec["branch_cpu_seconds"])
    return {
        "branch_id": branch_id,
        "epistemic_class": "sandbox_exploratory_tainted",
        "unit_id": f"g42_explore_{cell}_{tag}_s{seed}",
        "mode": "normal",
        "system": {"n_vertices": spec["n_vertices"], "knot": spec["knot"]},
        "ensemble": {"temperature": spec["temperature"]},
        "policy": policy_spec(tag, spec["n_vertices"]),
        "budget": {
            "proposals": spec["proposals"],
            "cpu_seconds": unit_cpu,
            "thin": spec["thin"],
        },
    }


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def dump_json(path: Path, value: Any) -> str:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(text)
    return sha256_bytes(text.encode("utf-8"))


def write_members(path: Path, items: list[str]) -> str:
    data = "".join(item + "\n" for item in sorted(items, key=lambda s: s.encode("utf-8"))).encode("utf-8")
    path.write_bytes(data)
    return sha256_bytes(data)


def build(
    stamp: str,
    root: Path,
    preparation_commit: str | None,
    operative: bool,
) -> dict[str, str]:
    auth = root / "research/paper_g/g42_fixed_knot_moves/preparation/authorization"
    members_dir = auth / "members"
    configs_dir = auth / "configs"
    genesis_dir = auth / "genesis"
    for directory in (members_dir, configs_dir, genesis_dir):
        directory.mkdir(parents=True, exist_ok=True)

    exploration_units: list[str] = []
    for cell in sorted(CELLS, key=lambda c: CELLS[c]["branch_order"]):
        for tag in POLICY_TAGS:
            for seed in SEEDS:
                exploration_units.append(f"g42_explore_{cell}_{tag}_s{seed}")
    confirmation_templates: list[str] = []
    for cell in sorted(CELLS, key=lambda c: CELLS[c]["branch_order"]):
        for tag in CONFIRMATION_POLICIES:
            for seed in SEEDS:
                confirmation_templates.append(f"{cell}_{tag}_s{seed}")
    assert len(exploration_units) == 224
    assert len(set(exploration_units)) == 224
    assert len(confirmation_templates) == 112
    assert len(set(confirmation_templates)) == 112
    assert not set(exploration_units) & {
        CONFIRMATION_PREFIX + "x" + "_" + t for t in confirmation_templates
    }

    exploration_sha = write_members(
        members_dir / "exploration.txt", exploration_units
    )
    confirmation_sha = write_members(
        members_dir / "confirmation.txt", confirmation_templates
    )

    unit_contract: dict[str, Any] = {
        "schema_version": 1,
        "sandbox_id": SANDBOX_ID,
        "campaign_id": CAMPAIGN_ID,
        "engine_version": ENGINE_VERSION,
        "hypothesis_id": HYPOTHESIS_ID,
        "multiplicity_family_id": MULTIPLICITY_FAMILY_ID,
        "hypothesis": (
            "Context-bucket proposal selection (p3) reduces the integrated "
            "autocorrelation time of Rg^2 relative to uniform proposals (p0) at "
            "matched total proposal budget in fixed-knot lattice rings."
        ),
        "falsifier": (
            "Apply the frozen assess rule only to completed paired units: primary "
            "statistic is the per-cell tail-tau ratio p0/p3 pooled across seeds; "
            "secondary are the ESS-tail ratio and contacts-mean equilibrium "
            "consistency. Units ending certification_ambiguous or cpu_budget are "
            "excluded per the frozen exclusion rule, as are units whose "
            "rg2_var_tail is 0 (degenerate tail: the tau-tail estimator's floor "
            "0.5 is indistinguishable from ideal decorrelation); if more than "
            "half of a cell's units are excluded the cell is void. No threshold, "
            "seed, or policy replacement."
        ),
        "test_ids": [
            "rg2_tau_int_tail_ratio_p0_over_p3",
            "rg2_ess_tail_ratio_p0_over_p3",
            "contacts_mean_equilibrium_consistency",
        ],
        "seeds": list(SEEDS),
        "cells": CELLS,
        "policies": {
            tag: (policy_spec(tag, 0) if tag == "p0" else "parameterized-per-n-vertices")
            for tag in POLICY_TAGS
        },
        "context_thresholds": {str(k): v for k, v in CONTEXT_THRESHOLDS.items()},
        "confirmation": {
            "policies": list(CONFIRMATION_POLICIES),
            "template_count": 112,
            "unit_id_rule": (
                "unit_id = 'g42_confirm_' + first 16 hex characters of "
                "pulse.outputValue + '_' + template"
            ),
        },
        "branch_contingency": (
            "Planned branches g42_b01..g42_b07 consume 12960 of the 14400 "
            "CPU-second reservation and 7 of 8 branch slots; the remaining 1440 "
            "CPU-seconds and the 8th slot are in-envelope contingency only, "
            "never usable after a quarantine (stop rule forbids retry). "
            "Per-unit cpu cap = (branch_cpu_seconds - 128) // 32 = 56/56/51/51/"
            "61/61/41 s by branch order; the 128 s branch-level reserve keeps "
            "the worst-case all-capped branch (32 x unit cap + startup) inside "
            "the launcher wall deadline of branch_cpu_seconds - 42 s."
        ),
    }
    dump_json(auth / "unit_contract.json", unit_contract)

    for branch_id in sorted({spec["branch_id"] for spec in CELLS.values()}):
        cell = next(c for c, s in CELLS.items() if s["branch_id"] == branch_id)
        unit_ids = [
            f"g42_explore_{cell}_{tag}_s{seed}"
            for tag in POLICY_TAGS
            for seed in SEEDS
        ]
        envelope = {
            "branch_id": branch_id,
            "epistemic_class": "sandbox_exploratory_tainted",
            "unit_ids": unit_ids,
            "units": {unit_id: unit_config(cell, tag, seed)
                      for tag in POLICY_TAGS
                      for seed in SEEDS
                      for unit_id in [f"g42_explore_{cell}_{tag}_s{seed}"]},
        }
        assert len(envelope["units"]) == 32
        assert sum(u["budget"]["cpu_seconds"] for u in envelope["units"].values()) \
            == 32 * unit_cpu_seconds(CELLS[cell]["branch_cpu_seconds"])
        dump_json(configs_dir / f"{branch_id}.json", envelope)

    derivation: dict[str, str] = {
        "anti_selection": (
            "D0 timestamp, unit templates, and protocol must be immutable "
            "before T; no refreeze, pulse replacement, or template reordering "
            "after observing a pulse."
        ),
        "derivation": (
            "unit_id = 'g42_confirm_' + first 16 hex characters of "
            "pulse.outputValue + '_' + template; engine initstate = "
            "int(SHA256(UTF8(unit_id)).digest()[:16], 'big') with the frozen "
            "INITSEQ_EXPLORATION stream tag; templates are frozen in "
            "members/confirmation.txt"
        ),
        "endpoint_template": "https://beacon.nist.gov/beacon/2.0/pulse/time/next/{unix_milliseconds}",
        "failure_policy": (
            "If the designated pulse or verification is unavailable, "
            "confirmation stays sealed; no alternate pulse/provider/seed/template."
        ),
        "implementation": (
            "No confirmation generator or retrieval code is included in this "
            "scientific image."
        ),
        "provider": "NIST Randomness Beacon v2",
        "pulse_rule": "first signed pulse strictly after T; query pulse/time/next/{1000*T}",
        "release_gate": (
            "g42 sandbox terminal receipt and independently frozen D0 are both "
            "required"
        ),
        "source_documentation": "https://csrc.nist.gov/Projects/interoperable-randomness-beacons/beacon-20",
        "status": "future_rule_only_no_pulse_access",
        "time_rule": (
            "T = ceil(max(g42 sandbox terminal UTC epoch seconds, D0 freeze UTC "
            "epoch seconds)) + 600"
        ),
        "verification": (
            "verify pulse signature/certificate and timestamp > T; archive exact "
            "response and certificate"
        ),
    }
    dump_json(auth / "confirmation_derivation.json", derivation)

    inputs_root = f"research/discovery/sandbox_inputs/{SANDBOX_ID}"

    dependency_provenance = {
        "image_base": "python:3.11-slim-bookworm@sha256:2e32f7d302adc1c37428355c1e646897c0c53f4fd60b6a551245fb90ee129f91",
        "runtime_packages": [],
        "statement": (
            "pure Python standard library; no third-party runtime dependencies "
            "in the scientific image"
        ),
    }
    dump_json(auth / "dependency_provenance.json", dependency_provenance)

    appendix_ref = "papers/proposal/ecomd_g42_fixed_knot_moves_sandbox_preflight_2026-09-16.md"
    provenance: dict[str, Any] = {
        "confirmation_outcomes_materialized": False,
        "dependency_provenance": {
            "ref": f"{inputs_root}/dependency_provenance.json",
            "sha256": sha256_file(auth / "dependency_provenance.json"),
        },
        "license": (
            "MIT for repository source; pinned CPython base image under PSF "
            "license terms"
        ),
        "preflight": {
            "ref": appendix_ref,
            "sha256": sha256_file(root / appendix_ref),
        },
        "preprocessing": (
            "none; each exploration unit is generated only inside the governed "
            "image from its frozen unit_id"
        ),
        "public_evidence_eligible": False,
        "source": "repository_owned_g42_fixed_knot_lattice_mc",
    }
    dump_json(auth / "provenance.json", provenance)

    auth_rel = "research/paper_g/g42_fixed_knot_moves/preparation/authorization"
    branch_ids = sorted({spec["branch_id"] for spec in CELLS.values()})
    source_files = [
        "research/paper_g/g42_fixed_knot_moves/model.py",
        "research/paper_g/g42_fixed_knot_moves/runner.py",
        "research/paper_g/g42_fixed_knot_moves/oci_probe.py",
        "research/paper_g/g42_fixed_knot_moves/Dockerfile",
        "research/paper_g/g42_fixed_knot_moves/qualify_image.py",
        "research/paper_g/g42_fixed_knot_moves/stage_authorization.py",
        "tests/test_paper_g_g42_engine.py",
        LAUNCHER_REF,
        HANDLER_REF,
        appendix_ref,
        "research/paper_g/g42_fixed_knot_moves/preparation/image_conformance.json",
        f"{auth_rel}/dependency_provenance.json",
        f"{auth_rel}/unit_contract.json",
        f"{auth_rel}/confirmation_derivation.json",
        f"{auth_rel}/members/exploration.txt",
        f"{auth_rel}/members/confirmation.txt",
    ] + [f"{auth_rel}/configs/{bid}.json" for bid in branch_ids]
    source_sha256 = {ref: sha256_file(root / ref) for ref in source_files}
    snapshot: dict[str, Any] = {
        "image_digest": IMAGE_DIGEST,
        "preparation_commit": preparation_commit,
        "schema_version": "g42-source-snapshot-v1",
        "scientific_outcomes_materialized": False,
        "source_sha256": source_sha256,
        "staged_payload_note": (
            "source and preparation snapshot only (dx-precedent shape); "
            "partition/provenance/snapshot_manifest are pinned directly by the "
            "manifest, and the asset fingerprint is derived from this "
            "snapshot's sha256 at staging time; preparation_commit is stamped "
            "at promotion via --preparation-commit and this snapshot is "
            "re-hashed then"
        ),
    }
    snapshot_sha = dump_json(auth / "snapshot_manifest.json", snapshot)

    asset_key = "g42_fixed_knot_moves_lattice_ring_mc"
    asset_kind = "synthetic_simulator"
    asset_source = "repository_owned_g42_fixed_knot_lattice_mc"
    fingerprint = sha256_bytes(
        canonical_json(
            {
                "asset_key": asset_key,
                "kind": asset_kind,
                "snapshot_sha256": snapshot_sha,
                "source": asset_source,
                "version": ENGINE_VERSION,
            }
        )
    )

    partition: dict[str, Any] = {
        "asset_fingerprint_sha256": fingerprint,
        "sandbox_id": SANDBOX_ID,
        "schema_version": 1,
        "splits": [
            {
                "id": "exploration",
                "member_count": 224,
                "members_ref": f"{inputs_root}/members/exploration.txt",
                "members_sha256": exploration_sha,
                "role": "exploration",
            },
            {
                "id": "confirmation",
                "member_count": 112,
                "members_ref": f"{inputs_root}/members/confirmation.txt",
                "members_sha256": confirmation_sha,
                "role": "confirmation",
            },
        ],
        "unit_namespace": UNIT_NAMESPACE,
    }
    dump_json(auth / "partition.yaml", partition)

    manifest: dict[str, Any] = {
        "asset": {
            "evidence_refs": ["g42_fixed_knot_moves_preflight"],
            "fingerprint_sha256": fingerprint,
            "intervention_or_search_space": (
                "Fixed-knot lattice-ring equilibrium collapse: 7 frozen (knot, "
                "N, T) cells x 4 proposal policies x 8 seeds at matched total "
                "proposal budget; context-bucket move selection versus uniform "
                "under exact Metropolis-Hastings acceptance."
            ),
            "key": asset_key,
            "kind": asset_kind,
            "license": "MIT source with pinned CPython base image under PSF license terms",
            "provenance": {
                "ref": f"{inputs_root}/provenance.json",
                "sha256": sha256_file(auth / "provenance.json"),
            },
            "snapshot_manifest": {
                "ref": f"{inputs_root}/snapshot_manifest.json",
                "sha256": sha256_file(auth / "snapshot_manifest.json"),
            },
            "source": asset_source,
            "state_or_observation_coverage": (
                "closed self-avoiding rings on Z^3 with N in {96, 128, 160, "
                "256} and knot classes 0_1/3_1/4_1 enforced by an integer "
                "Alexander-determinant certificate; observables Rg^2, contacts, "
                "and integrated autocorrelation with tail statistics; 224 "
                "exploration units and 112 future confirmation templates."
            ),
            "version": ENGINE_VERSION,
        },
        "authorization": {
            "allowed_actions": [
                "cpu_simulator_probe",
                "disposable_outcome_inspection",
                "sandbox_analysis_implementation",
            ],
            "forbidden_actions": [
                "confirmation_holdout_access",
                "dataset_purchase",
                "gpu_use",
                "production_model_implementation",
                "ecomd_integration",
                "external_outreach",
                "paper_claim_support",
                "topic_status_promotion",
            ],
        },
        "campaign_id": CAMPAIGN_ID,
        "confirmation_contract": {
            "controller": (
                "PI frozen future NIST Beacon v2 rule; no pulse or confirmation "
                "seed retrieved"
            ),
            "derivation": {
                "ref": f"{inputs_root}/confirmation_derivation.json",
                "sha256": sha256_file(auth / "confirmation_derivation.json"),
            },
            "mode": "future_public_randomness",
            "outcomes_materialized": False,
            "release_condition": "after_sandbox_terminal_and_d0_freeze",
        },
        "created_at": stamp,
        "decision_ref": f"research/discovery/sandbox_decisions/{SANDBOX_ID}.yaml",
        "execution_contract": {
            "confirmation_materialization": "not_generated_not_staged_not_mounted",
            "device_access": "cpu_only",
            "executor": "oci_container",
            "image_digest": IMAGE_DIGEST,
            "incident_handler": {"ref": HANDLER_REF, "sha256": HANDLER_SHA},
            "input_channel": "read_only_config_with_enumerated_units_only",
            "launcher": {"ref": LAUNCHER_REF, "sha256": LAUNCHER_SHA},
            "network": "none",
            "output_channel": "bounded_stdout_tar",
            "repository_tree_mount": "none",
            "root_filesystem": "read_only",
            "secrets": "none",
        },
        "expires_at": _expires(stamp),
        "id": SANDBOX_ID,
        "integrity": {
            "ledger_ref": f"research/discovery/sandbox_artifacts/{SANDBOX_ID}/events.jsonl",
            "result_disposition": "child_card_d_minus_3_only",
            "stop_rule": "first_of_budget_expiry_forbidden_access_or_manual_close",
        },
        "parent_route_ids": ["g42_fixed_knot_learned_moves"],
        "partition": {
            "ref": f"{inputs_root}/partition.yaml",
            "sha256": sha256_file(auth / "partition.yaml"),
        },
        "purpose": (
            "Private bounded g42 exploration: test whether context-dependent "
            "move selection reduces the integrated autocorrelation time of Rg^2 "
            "at matched total budget in fixed-knot ring equilibration; either "
            "answer supports screening only."
        ),
        "reservation": {
            "branches": 8,
            "cpu_seconds": 14400,
            "gpu_seconds": 0,
            "monetary_cost_usd_micros": 0,
            "storage_bytes": 1000000000,
        },
        "schema_version": 2,
    }
    manifest_sha = dump_json(auth / "manifest.yaml", manifest)

    event: dict[str, Any] = {
        "entry_sha256": "",
        "event_type": "authorized",
        "manifest_sha256": manifest_sha,
        "occurred_at": stamp,
        "previous_entry_sha256": None,
        "schema_version": 1,
        "seq": 0,
    }
    event.pop("entry_sha256")
    event["entry_sha256"] = sha256_bytes(canonical_json(event))
    ordered = {key: event[key] for key in sorted(event)}
    (genesis_dir / "events.jsonl").write_bytes(
        canonical_json(ordered) + b"\n"
    )
    genesis_sha = event["entry_sha256"]

    if operative:
        authorized_by = (
            "PI authorization-only merge (merge executed; payload operative)"
        )
        rationale = (
            "Authorization-only merge executed by PI order on the staged g42 "
            "preflight payload per the g42 preflight appendix 2026-09-16; all "
            "exploratory taint and the child_card_d_minus_3_only disposition "
            "retained."
        )
    else:
        authorized_by = (
            "PI authorization-only merge (draft staged 2026-09-16; not yet "
            "operative)"
        )
        rationale = (
            "Execute only this reviewed CPU sandbox after the PI orders the "
            "authorization-only merge of the staged payload, per the g42 "
            "preflight appendix 2026-09-16; all exploratory taint and the "
            "child_card_d_minus_3_only disposition retained."
        )
    decision: dict[str, Any] = {
        "authorized_by": authorized_by,
        "decided_at": stamp,
        "decision": "authorized",
        "genesis_entry_sha256": genesis_sha,
        "manifest_sha256": manifest_sha,
        "rationale": rationale,
        "sandbox_id": SANDBOX_ID,
        "schema_version": 2,
    }
    dump_json(auth / "decision.yaml", decision)

    return {
        "asset_fingerprint_sha256": fingerprint,
        "manifest_sha256": manifest_sha,
        "genesis_entry_sha256": genesis_sha,
        "exploration_members_sha256": exploration_sha,
        "confirmation_members_sha256": confirmation_sha,
        "payload_root": str(auth),
    }


def _expires(stamp: str) -> str:
    from datetime import UTC, datetime, timedelta

    moment = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    return (moment + timedelta(seconds=604800)).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stamp", required=True, help="UTC instant YYYY-MM-DDTHH:MM:SSZ")
    parser.add_argument(
        "--preparation-commit",
        default=None,
        help="promotion-time preparation commit sha to stamp into the snapshot",
    )
    parser.add_argument(
        "--operative",
        action="store_true",
        help="emit operative decision wording for the authorization-only merge",
    )
    args = parser.parse_args()
    from datetime import datetime

    try:
        datetime.strptime(args.stamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        sys.exit("--stamp must be formatted YYYY-MM-DDTHH:MM:SSZ")
    root = Path(__file__).resolve().parents[3]
    summary = build(args.stamp, root, args.preparation_commit, args.operative)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
