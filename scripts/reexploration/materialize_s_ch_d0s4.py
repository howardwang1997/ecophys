#!/usr/bin/env python3
"""Materialize the Annex B(e) s_ch seal for D0-S4 eval (remote, CPU).

s_ch = DGP-native per-event innovation std from a hash-sealed DGP-only
sample branch: frozen generate_episode + frozen lab_asset.yaml DGPConfig at
the ID axis, reserved seed namespace 20260977 (disjoint from every training /
fixture / preflight namespace), 512 episodes.  s_ch = per-channel std of
channels_delta pooled over all rounds of all episodes (DGP-truth side only --
engine-realized increments of DGP sessions, never surrogate output, never the
paired 11000+/12000+ corpus).  PI decision pi_d0s4_eval_constants_20260922
item 3; the output file's sha256 is the seal recorded in that decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SEED_NAMESPACE = 20260977
N_EPISODES = 512
FREEZE_COMMIT = "f4e61bafed21f12a6ec73dbe82b9ed4ea87bdd37"
FREEZE_FILE_PINS: dict[str, str] = {
    "configs/reexploration/dgp/lab_asset.yaml": (
        "06b9691af333be8a6891ee1213032a785e61c03c3c26e8f8a4beb159b202c801"
    ),
    "scripts/lab_asset/dgp_request_generator.py": (
        "2cef5a334cc7f0020459062e3f37d76aab55d4440c8a305e50a222bfd4d72152"
    ),
}
DRAW_SEED_TAG = "draw"  # must equal generate_corpus_d0s2.py's tag


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    for rel, pinned in FREEZE_FILE_PINS.items():
        actual = sha256_file(repo_root / rel)
        if actual != pinned:
            raise RuntimeError(f"freeze pin violated for {rel}: {actual} != {pinned}")
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError("repo HEAD does not descend from the D0 freeze commit")

    sys.path.insert(0, str(repo_root / "scripts"))
    sys.path.insert(0, str(repo_root))

    import torch
    import yaml
    from lab_asset import dgp_request_generator as dgp
    from lab_asset.conserving_emitter import (
        conservation_violations,
        emit_conserving_channels,
        settlement_violations,
    )
    from lab_asset.matching import ReferenceEngine
    from lab_asset.schema import AllocationRule

    torch.set_num_threads(1)

    mapping = yaml.safe_load(
        (repo_root / "configs" / "reexploration" / "dgp" / "lab_asset.yaml").read_text()
    )["config"]
    cfg = dgp.config_for_axis(dgp.config_from_mapping(mapping), "id")

    increments = []
    n_rounds_total = 0
    started = time.time()
    for episode_index in range(N_EPISODES):
        stream = dgp.generate_episode(SEED_NAMESPACE, episode_index, cfg)
        draw_seed = dgp.derive_seed(SEED_NAMESPACE, DRAW_SEED_TAG, episode_index)
        prestate = dgp.build_prestate(stream, AllocationRule("fifo"), draw_seed)
        engine = ReferenceEngine(prestate)
        for request in dgp.order_requests(stream):
            engine.submit(request)
        engine.finish()
        series = emit_conserving_channels(prestate, engine.tape)
        violations = conservation_violations(series) + settlement_violations(
            prestate, engine.tape, series
        )
        if violations:
            raise RuntimeError(
                f"E-4 gate failed episode {episode_index}: {violations}"
            )
        increments.append(torch.tensor(series.increment_matrix(), dtype=torch.float64))
        n_rounds_total += increments[-1].shape[0]
        if (episode_index + 1) % 128 == 0:
            print(f"[s_ch] {episode_index + 1}/{N_EPISODES} episodes "
                  f"({time.time() - started:.0f}s)", flush=True)

    pooled = torch.cat(increments, dim=0)
    s_ch = pooled.std(dim=0, unbiased=False).tolist()

    payload: dict[str, Any] = {
        "s_ch": s_ch,
        "provenance": {
            "derivation": (
                "per-channel std of channels_delta (per-round increments) pooled "
                "over all rounds of all episodes; DGP-truth side (engine-realized "
                "increments of DGP-only sessions); never surrogate output, never "
                "the paired corpus"
            ),
            "n_episodes": N_EPISODES,
            "n_rounds_pooled": n_rounds_total,
            "seed_namespace": SEED_NAMESPACE,
            "axis": "id",
            "allocation_rule": "fifo",
            "generator": "scripts/lab_asset/dgp_request_generator.py",
            "config": "configs/reexploration/dgp/lab_asset.yaml",
            "config_fingerprint": dgp.config_fingerprint(cfg),
            "freeze_commit": FREEZE_COMMIT,
            "freeze_file_pins": FREEZE_FILE_PINS,
            "draw_seed_tag": DRAW_SEED_TAG,
            "decision": "pi_d0s4_eval_constants_20260922",
            "torch": torch.__version__,
            "numpy": __import__("numpy").__version__,
            "python": sys.version.split()[0],
        },
    }
    blob = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(blob)
    print(f"[s_ch] s_ch = {s_ch}")
    print(f"[s_ch] rounds pooled = {n_rounds_total}")
    print(f"[s_ch] wrote {args.out} sha256={hashlib.sha256(blob).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
