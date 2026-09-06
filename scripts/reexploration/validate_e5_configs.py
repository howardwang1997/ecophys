#!/usr/bin/env python
"""E-5 validation entry point (CPU, second-scale, run once per freeze check).

Validates that (a) every Hydra config under ``configs/reexploration``
composes and matches the frozen sibling build surfaces, (b) the C14-restated
campaign arithmetic (450 trainings / 299,520 records) is reproduced by the
enumeration, and (c) the on-disk seed/stream manifest is byte-identical to a
fresh rebuild. Exit code 1 on any failure. No GPU, no training, no outcomes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ecomd.reexploration import campaign  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=campaign.MANIFEST_PATH,
        help="seeds_manifest.json to compare against a fresh rebuild",
    )
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="rewrite the manifest from a fresh validated build",
    )
    args = parser.parse_args()

    failures: list[str] = []

    tree_failures = campaign.validate_config_tree()
    failures.extend(tree_failures)
    print(f"config tree: {'OK' if not tree_failures else 'FAIL'}")

    try:
        counts = campaign.validate_counts()
        print(
            "campaign arithmetic: OK "
            f"({counts.trainings_total} trainings, "
            f"{counts.confirmatory_total} confirmatory records, "
            f"{counts.horizon_one_probes} horizon-one probes)"
        )
    except campaign.CampaignArithmeticError as exc:
        failures.append(f"campaign arithmetic: {exc}")
        print("campaign arithmetic: FAIL")

    try:
        checks = campaign.assert_disjointness()
        print(f"seed disjointness: OK ({len(checks)} checks)")
    except campaign.SeedCollisionError as exc:
        failures.append(f"seed disjointness: {exc}")
        print("seed disjointness: FAIL")

    if args.write_manifest:
        digest = campaign.write_seed_manifest(args.manifest)
        print(f"manifest rewritten: sha256 {digest}")
    if args.manifest.exists():
        on_disk = args.manifest.read_bytes()
        rebuilt = campaign.canonical_json_bytes(campaign.build_seed_manifest())
        if on_disk == rebuilt:
            print(f"manifest byte-identical to rebuild: OK ({args.manifest})")
        else:
            failures.append(
                f"manifest differs from rebuild: {args.manifest} "
                f"(on-disk sha256 {campaign.sha256_bytes(on_disk)} vs "
                f"rebuilt {campaign.sha256_bytes(rebuilt)})"
            )
            print("manifest byte-identical to rebuild: FAIL")
    else:
        failures.append(f"manifest missing: {args.manifest}")
        print("manifest: MISSING")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("E-5 validation: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
