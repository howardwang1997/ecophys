"""E-2 preflight re-run (prereg v2 C2(e) as rewritten at v2; PI directive 2026-09-07).

Re-runs the frozen K-preflight PROTOCOL (k_preflight_20260906/run_preflight.py,
results sha256 f61e410c...) against the ACTUAL D0 corpus generator (build item E-2,
scripts/lab_asset/dgp_request_generator.py) instead of the calibration generator
(dgp_stream.py). Protocol identity is preserved by importing every statistical and
invariant component from run_preflight and rebinding ONLY the generator module:

    run_preflight.dgp_stream = dgp_request_generator

so build_episode / build_prestate / order_requests / derive_seed all execute the
E-2 implementations. derive_seed is byte-compatible between the two modules by
construction (E-2 docstring).

Result status: CAVEAT-AND-REPORTING-ONLY. K = 16 is immutable regardless of this
run's outcome (PI ruling D1_11). If any random_unit-arm draw-dependent statistic
shows a bootstrap 95% upper bound of ratio_vs_between(16) > 0.10, that fact is a
named STOP-class PI decision item at D0 (prereg v2 C2(e)) — the runner flags it
loudly but does not act on it.

Config: the protocol parameters are IDENTICAL to the calibration preflight
(seed_base 31000, n_seeds 32, episodes_per_seed 6, k_grid {4,8,16}, thresholds
{0.10, 0.05}, bootstrap 2000 draws @ 31099 — the calibration namespace is reused
by design: this is the same protocol re-run on the real generator). Only the
generator section changes, to the E-2 production defaults (DGPConfig(): ID axis,
N = 16 actors, 32 rounds, M1 feedback, lab_asset family).

Legality: CPU-only engine execution for instrument calibration; zero GPU, zero
trained models, zero cell endpoints, zero outcome access, zero market data, zero
writes under the frozen a2_exit_20260905 bundle. Executed on the remote worker
(v100ts) per the PI compute-location rule (2026-09-06).

Determinism: results.json is a pure function of (config, code); no timestamps,
no absolute paths. Byte-identical on re-run to any directory.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

KP_DIR = Path(__file__).resolve().parents[1] / "k_preflight_20260906"
HERE = Path(__file__).resolve().parent
REPO_ROOT = KP_DIR.parents[2]
for entry in (str(KP_DIR), str(REPO_ROOT / "scripts"), str(HERE)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import run_preflight  # noqa: E402
from lab_asset import dgp_request_generator as e2  # noqa: E402

SWAP_ASSERTIONS = {
    "build_episode": callable(e2.build_episode),
    "build_prestate": callable(e2.build_prestate),
    "order_requests": callable(e2.order_requests),
    "derive_seed": callable(e2.derive_seed),
}


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _instrument_progress() -> None:
    """Print episode-build progress; pure instrumentation, no semantic change."""

    original = e2.build_episode
    state = {"n": 0}

    def counting_build(seed_root: int, episode_index: int, cfg: object) -> object:
        state["n"] += 1
        if state["n"] % 12 == 0 or state["n"] == 1:
            print(f"[e2-preflight] episodes built: {state['n']}", flush=True)
        return original(seed_root, episode_index, cfg)

    e2.build_episode = counting_build


def _determinism_check(generator_cfg: dict[str, object]) -> dict[str, object]:
    """Episode-rebuild byte-identity + engine-replay byte-identity probes."""

    stream_a = e2.build_episode(31000, 0, generator_cfg)
    stream_b = e2.build_episode(31000, 0, generator_cfg)
    episode_rebuild_identical = (
        e2.episode_canonical_json(stream_a) == e2.episode_canonical_json(stream_b)
    )

    from lab_asset.matching import ReferenceEngine  # noqa: PLC0415
    from lab_asset.schema import AllocationRule  # noqa: PLC0415

    draw_seed = e2.derive_seed(stream_a.seed_root, "draw", 3, stream_a.episode_index)
    requests = e2.order_requests(stream_a)
    projections = []
    for _ in range(2):
        engine = ReferenceEngine(e2.build_prestate(stream_a, AllocationRule.RANDOM_UNIT_WITHIN_PRICE, draw_seed))
        for request in requests:
            engine.submit(request)
        engine.finish()
        projections.append(
            [
                (record.sequence, record.event_type.value, record.post_aggregate_state_hash)
                for record in engine.tape
            ]
        )
    replay_identical = projections[0] == projections[1]
    return {
        "episode_rebuild_canonical_json_identical": episode_rebuild_identical,
        "engine_replay_projection_identical": replay_identical,
        "probe": "seed_root=31000, episode_index=0, arm=random_unit, draw k=3",
    }


def main() -> None:
    assert all(SWAP_ASSERTIONS.values()), SWAP_ASSERTIONS
    _instrument_progress()
    run_preflight.dgp_stream = e2

    protocol_cfg = json.loads((KP_DIR / "preflight_config.json").read_text())
    generator_cfg = e2.config_to_mapping(e2.DGPConfig())
    cfg = dict(protocol_cfg)
    cfg["generator"] = generator_cfg
    cfg["generator_source"] = (
        "scripts/lab_asset/dgp_request_generator.py DGPConfig() defaults "
        "(ID axis, N=16 actors, n_rounds=32, M1 feedback, lab_asset family)"
    )
    (HERE / "preflight_config.json").write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")

    started = time.monotonic()
    results = run_preflight.run_pipeline(cfg)
    elapsed = time.monotonic() - started

    results["schema_version"] = "k-preflight-v1+e2-rerun"
    results["component"] = "c2e_e2_preflight_rerun_on_actual_d0_generator"
    results["authorization"] = (
        "prereg v2 section 3.2 C2(e) as rewritten at v2 (panel R1-8/R2-4); PI "
        "directive 2026-09-07 (D1_15 package); remote execution on v100ts per the "
        "PI compute-location rule 2026-09-06"
    )
    results["policy_class_note"] = (
        "E-2 production generator at its ID-axis defaults: M1 feedback (anonymous "
        "book state via the shadow engine), lab_asset family, N=16 actors, 32 "
        "rounds per episode. This IS the D0 corpus generator; the M1 own-state "
        "question is answered empirically by this run, per C2(e)."
    )
    results["status"] = (
        "caveat-and-reporting-only; K=16 immutable regardless of outcome (PI "
        "ruling D1_11); between-ratio UB > 0.10 on any endpoint-shaped statistic "
        "is a named STOP-class PI decision item at D0"
    )
    results["runtime_seconds_remote"] = round(elapsed, 3)
    results["provenance"]["dgp_request_generator_sha256"] = _sha256(
        REPO_ROOT / "scripts/lab_asset/dgp_request_generator.py"
    )
    results["provenance"]["generator_binding"] = (
        "run_preflight.dgp_stream rebound to lab_asset.dgp_request_generator; all "
        "statistics, invariants, decomposition, bootstrap and rule code executed "
        "from k_preflight_20260906/run_preflight.py unchanged"
    )

    (HERE / "results.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    (HERE / "determinism_check.json").write_text(
        json.dumps(_determinism_check(generator_cfg), indent=2, sort_keys=True) + "\n"
    )

    summary = results["k_table"]["min_k_draw_stats"]["threshold_0.1"]
    variance = results["variance_decomposition"]["random_unit_within_price"]
    print("\n[e2-preflight] conservative rule (ci_upper, threshold 0.10):", summary["ci_upper"])
    print("[e2-preflight] point estimate variant:", summary["point"])
    for stat in run_preflight.DRAW_STATS:
        ci16 = variance[stat]["ci95_ratio_vs_between"]["16"]
        print(f"[e2-preflight]   {stat}: K=16 CI95 ratio_vs_between = {ci16}")
    stop_flag = summary["ci_upper"] == "none_in_set"
    print(
        "\n[e2-preflight] STOP-CLASS FLAG:",
        "RAISED — at least one draw statistic has K=16 bootstrap UB > 0.10; "
        "PI decision item at D0" if stop_flag else "not raised",
    )
    print(f"[e2-preflight] invariants (all must be 0): {results['invariants']}")
    print(f"[e2-preflight] elapsed {elapsed:.1f}s; written to {HERE / 'results.json'}")


if __name__ == "__main__":
    main()
