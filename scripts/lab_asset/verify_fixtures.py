"""A-2 exit verifier: consume an exported bundle and re-validate it from disk.

Verifies the bundle manifest hashes, rebuilds each fixture prestate from JSON,
re-executes the tape through the deterministic replay validator, and checks the
regenerated tape equals the recorded tape byte-for-byte. A hardened platform
fork must pass this verifier on the frozen bundle to qualify.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab_asset.replay import ReplayReport, regenerate, replay
from lab_asset.schema import EventType, TapeRecord, prestate_from_json, record_to_json


def load_tape(path: Path) -> list[TapeRecord]:
    records: list[TapeRecord] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        records.append(
            TapeRecord(
                sequence=raw["sequence"],
                event_type=EventType(raw["event_type"]),
                payload=raw["payload"],
                pre_state_hash=raw["pre_state_hash"],
                post_state_hash=raw["post_state_hash"],
                pre_aggregate_state_hash=raw["pre_aggregate_state_hash"],
                post_aggregate_state_hash=raw["post_aggregate_state_hash"],
            )
        )
    return records


def verify_bundle(bundle_dir: Path) -> bool:
    manifest_path = bundle_dir / "bundle_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    files = manifest["files"]
    assert isinstance(files, dict)
    for relative, expected in sorted(files.items()):
        digest = hashlib.sha256((bundle_dir / relative).read_bytes()).hexdigest()
        if digest != expected:
            print(f"HASH MISMATCH: {relative}")
            return False
    print(f"manifest: {len(files)} files verified")

    ok = True
    for fixture_dir in sorted(p for p in bundle_dir.iterdir() if p.is_dir()):
        prestate = prestate_from_json((fixture_dir / "prestate.json").read_text())
        tape = load_tape(fixture_dir / "tape.jsonl")
        report: ReplayReport = replay(prestate, tape)
        regenerated_bytes = "".join(
            record_to_json(r) + "\n" for r in regenerate(prestate, tape)
        )
        recorded_bytes = (fixture_dir / "tape.jsonl").read_text()
        byte_exact = regenerated_bytes == recorded_bytes
        status = "OK" if report.ok and byte_exact else "FAIL"
        print(
            f"fixture {fixture_dir.name}: replay={report.ok} "
            f"byte_exact={byte_exact} records={len(tape)} [{status}]"
        )
        ok = ok and report.ok and byte_exact
    return ok


def main() -> int:
    bundle_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/lab_asset_a2_exit")
    if not bundle_dir.is_dir():
        print(f"bundle directory not found: {bundle_dir}")
        return 1
    passed = verify_bundle(bundle_dir)
    print(f"lab_asset_a2_bundle_verify={'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
