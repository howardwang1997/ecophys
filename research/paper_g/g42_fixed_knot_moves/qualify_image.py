"""Outcome-free checks of the exact g42 scientific image, using the launcher."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.run_research_discovery_sandbox import capture_container, container_exists, inspect_local_image
from scripts.test_research_discovery_oci_conformance import (
    inspect_image_id,
    make_plan,
    read_probe_report,
    validate_probe_report,
)


def bind_image_files(root: Path, image: str, work: Path) -> dict[str, str]:
    name = "ecomd-g42-sourcecheck-" + uuid.uuid4().hex
    created = False
    hashes: dict[str, str] = {}
    pairs = [
        (
            f"/opt/g42_fixed_knot_moves/{name}",
            f"research/paper_g/g42_fixed_knot_moves/{name}",
        )
        for name in ("model.py", "runner.py", "oci_probe.py")
    ]
    try:
        subprocess.run(["docker", "create", "--name", name, "--network", "none", "--read-only", image],
                       check=True, capture_output=True, timeout=30)
        created = True
        for index, (inside, ref) in enumerate(pairs):
            target = work / f"image-source-{index}"
            subprocess.run(["docker", "cp", f"{name}:{inside}", str(target)],
                           check=True, capture_output=True, timeout=30)
            if target.is_symlink() or target.read_bytes() != (root / ref).read_bytes():
                raise RuntimeError(f"image content differs from recorded source: {inside}")
            hashes[inside] = hashlib.sha256(target.read_bytes()).hexdigest()
    finally:
        if created:
            subprocess.run(["docker", "rm", "-f", name], check=True, capture_output=True, timeout=30)
            if container_exists(name):
                raise RuntimeError("image inspection container cleanup unproven")
    return hashes


def qualify(root: Path, image: str) -> dict[str, Any]:
    # The launcher pins the exact image ID; resolve the reference once so
    # every case and the report carry the same frozen digest.
    image_id = inspect_image_id(image)
    with tempfile.TemporaryDirectory(prefix=".g42-conformance-", dir=root) as temporary:
        work = Path(temporary)
        image_files = bind_image_files(root, image, work)
        results: dict[str, str] = {}
        normal_report: dict[str, Any] = {}
        for name, mode, seconds, limit, expected in (
            ("normal", "normal", 120, 262144, "completed"),
            ("output_limit", "normal", 120, 128, "output_limit"),
            ("invalid_tar", "invalid_tar", 120, 262144, "container_failed"),
            ("timeout", "sleep", 1, 262144, "timeout"),
        ):
            plan = make_plan(work, image_id, name, mode=mode, cpu_seconds=seconds, output_bytes=limit)
            inspect_local_image(plan)
            status, exit_code, _, _, artifacts = capture_container(plan)
            if status != expected:
                receipt_dir = root / "logs/private/g42_conformance" / datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
                receipt_dir.mkdir(parents=True)
                for artifact in artifacts:
                    shutil.copyfile(artifact, receipt_dir / artifact.name)
                (receipt_dir / "incident.json").write_text(json.dumps({
                    "private_internal": True, "scientific_outcomes_accessed": False,
                    "case": name, "status": status, "image": image_id, "exit_code": exit_code,
                }, indent=2) + "\n")
                raise RuntimeError(f"{name}: expected {expected}, obtained {status}")
            results[name] = status
            if name == "normal":
                if exit_code != 0:
                    raise RuntimeError("normal conformance process did not exit successfully")
                normal_report = read_probe_report(next(p for p in artifacts if p.name == "bundle.tar"))
                validate_probe_report(normal_report)
        refs = [
            "scripts/run_research_discovery_sandbox.py",
            "scripts/quarantine_research_discovery_sandbox.py",
            "scripts/test_research_discovery_oci_conformance.py",
            "research/paper_g/g42_fixed_knot_moves/model.py",
            "research/paper_g/g42_fixed_knot_moves/runner.py",
            "research/paper_g/g42_fixed_knot_moves/Dockerfile",
            "research/paper_g/g42_fixed_knot_moves/qualify_image.py",
            "research/discovery/conformance/oci_probe.py",
            "research/paper_g/g42_fixed_knot_moves/oci_probe.py",
        ]
        return {
            "visibility": "private_internal", "public_evidence_eligible": False,
            "image_digest": image_id, "completed_at": datetime.now(UTC).isoformat(),
            "image_file_sha256": image_files,
            "passed": True, "cases": results, "isolation_checks": normal_report["checks"],
            "observed": normal_report["observed"], "scientific_outcomes_accessed": False,
            "independent_runtime_review": "not_performed_by_this_self_check",
            "dependency_snapshot": "none_pure_stdlib",
            "source_sha256": {ref: hashlib.sha256((root / ref).read_bytes()).hexdigest() for ref in refs},
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    report = qualify(root, args.image)
    destination = root / "research/paper_g/g42_fixed_knot_moves/preparation/image_conformance.json"
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"passed": True, "image": args.image, "report": str(destination)}))


if __name__ == "__main__":
    main()
