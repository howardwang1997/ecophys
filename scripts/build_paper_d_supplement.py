"""Validate and package the Paper D reproducibility artifact."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CubeBlock:
    name: str
    benchmark_id: str
    mandatory_cells: int
    primary_case: str
    primary_horizon: int
    core_config: str
    cube_config: str
    core_records: str
    core_analysis: str
    checkpoint_lock: str
    cube_records: str
    cube_analysis: str


CUBE_BLOCKS = (
    CubeBlock(
        name="advection_fno",
        benchmark_id="pdebench_advection_beta0.4_fno_factorial_v1",
        mandatory_cells=12,
        primary_case="ood_r512",
        primary_horizon=16,
        core_config=(
            "configs/constraint_iclr/pdebench_advection_fno_factorial_20260901.yaml"
        ),
        cube_config=(
            "configs/constraint_iclr/"
            "pdebench_advection_fno_enforcement_cube_20260901.yaml"
        ),
        core_records=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "factorial_confirmation_20260901.jsonl"
        ),
        core_analysis=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "factorial_analysis_20260901.json"
        ),
        checkpoint_lock=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_factorial_checkpoint_lock_20260901.json"
        ),
        cube_records=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_enforcement_cube_20260901.jsonl"
        ),
        cube_analysis=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_enforcement_cube_analysis_20260901.json"
        ),
    ),
    CubeBlock(
        name="advection_unet",
        benchmark_id="pdebench_advection_beta0.4_unet_factorial_v1",
        mandatory_cells=12,
        primary_case="ood_r512",
        primary_horizon=16,
        core_config=(
            "configs/constraint_iclr/"
            "pdebench_advection_unet_enforcement_cube_20260903.yaml"
        ),
        cube_config=(
            "configs/constraint_iclr/"
            "pdebench_advection_unet_enforcement_cube_20260903.yaml"
        ),
        core_records=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "unet_factorial_merged_20260902.jsonl"
        ),
        core_analysis=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "unet_factorial_analysis_20260903.json"
        ),
        checkpoint_lock=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "unet_factorial_checkpoint_lock_20260903.json"
        ),
        cube_records=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "unet_enforcement_cube_20260903.jsonl"
        ),
        cube_analysis=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "unet_enforcement_cube_analysis_20260903.json"
        ),
    ),
    CubeBlock(
        name="shallow_water_fno2d",
        benchmark_id="pdebench_swe_rdb_fno2d_factorial_v1",
        mandatory_cells=8,
        primary_case="ood_r128",
        primary_horizon=16,
        core_config=(
            "configs/constraint_iclr/"
            "pdebench_swe_rdb_factorial_distributed_20260902.yaml"
        ),
        cube_config=(
            "configs/constraint_iclr/"
            "pdebench_swe_rdb_enforcement_cube_distributed_20260902.yaml"
        ),
        core_records=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_factorial_confirmation_20260902.jsonl"
        ),
        core_analysis=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_factorial_analysis_20260902.json"
        ),
        checkpoint_lock=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_checkpoint_lock_20260902.json"
        ),
        cube_records=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_enforcement_cube_derived_20260902.jsonl"
        ),
        cube_analysis=(
            "experiments/constraint_attribution_iclr/pdebench/"
            "swe_enforcement_cube_analysis_20260902.json"
        ),
    ),
)

PAPER_DIR = Path("papers/paper_d_constraints")
MANIFEST_PATH = PAPER_DIR / "artifact_manifest.json"
ARCHIVE_ROOT = "paper_d_constraint_attribution_artifact"
ARTIFACT_SCHEMA_VERSION = "paper-d-constraint-attribution-artifact-v2"
FORBIDDEN_BULK_SUFFIXES = {".ckpt", ".h5", ".hdf5", ".pt", ".pth", ".safetensors"}
BASE_RELEASE_FILES = frozenset(
    {
        Path("LICENSE"),
        Path("output/pdf/paper_d_constraints_iclr2027.pdf"),
        PAPER_DIR / "ARTIFACT_README.md",
        PAPER_DIR / "requirements-analysis.txt",
        PAPER_DIR / "figures/pdebench_cube_mechanism.pdf",
        Path("scripts/build_paper_d_supplement.py"),
        Path("tests/test_build_paper_d_supplement.py"),
    }
)

TEXT_SUFFIXES = {
    ".bib",
    ".files",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".py",
    ".sha256",
    ".sha256s",
    ".sh",
    ".sty",
    ".tex",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
IDENTITY_REDACTIONS = (
    (
        "personal_macos_home",
        re.compile(rb"/Users/(?!anonymous\b)[A-Za-z0-9._-]+"),
        b"/Users/anonymous",
    ),
    (
        "personal_linux_home",
        re.compile(rb"/home/(?!anonymous\b)[A-Za-z0-9._-]+"),
        b"/home/anonymous",
    ),
    (
        "named_private_ssh_login",
        re.compile(
            rb"(?<![A-Za-z0-9._-])(?!root@|anonymous@)"
            rb"[A-Za-z][A-Za-z0-9._-]*@(?:[0-9]{1,3}\.){3}[0-9]{1,3}"
        ),
        b"anonymous@redacted-host",
    ),
    (
        "personal_email",
        re.compile(
            rb"(?<![A-Za-z0-9._%+-])(?!anonymous@example\.invalid)"
            rb"[A-Za-z0-9._%+-]+@"
            rb"[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
        ),
        b"anonymous@example.invalid",
    ),
    (
        "private_network_address",
        re.compile(
            rb"(?<![0-9])(?:"
            rb"10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}|"
            rb"192\.168\.(?:[0-9]{1,3}\.)[0-9]{1,3}|"
            rb"172\.(?:1[6-9]|2[0-9]|3[01])\.(?:[0-9]{1,3}\.)[0-9]{1,3}|"
            rb"100\.(?:6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\."
            rb"(?:[0-9]{1,3}\.)[0-9]{1,3}"
            rb")(?![0-9])"
        ),
        b"redacted-host",
    ),
)
LICENSE_HOLDER_REDACTION = (
    "copyright_holder",
    re.compile(rb"(?im)^(Copyright\s+\(c\)\s+\d{4}(?:-\d{4})?\s+).+$"),
    rb"\1Anonymous Authors",
)
PYPROJECT_AUTHOR_REDACTION = (
    "package_author",
    re.compile(rb'(?im)^(authors\s*=\s*\[\s*\{\s*name\s*=\s*)"[^"]*"'),
    rb'\1"Anonymous Authors"',
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_text_path(path: Path) -> bool:
    return path.name == "LICENSE" or path.suffix.lower() in TEXT_SUFFIXES


def _requires_byte_preservation(path: Path) -> bool:
    return (
        path.suffix.lower() == ".jsonl"
        or (path.parts and path.parts[0] == "configs")
        or (path.suffix.lower() == ".json" and "analysis" in path.stem)
    )


def redact_identity(payload: bytes, path: Path) -> tuple[bytes, tuple[str, ...]]:
    if not _is_text_path(path):
        return payload, ()
    redacted = payload
    categories: list[str] = []
    rules = IDENTITY_REDACTIONS
    if path.name == "LICENSE":
        rules = (*rules, LICENSE_HOLDER_REDACTION)
    if path.name == "pyproject.toml":
        rules = (*rules, PYPROJECT_AUTHOR_REDACTION)
    for category, pattern, replacement in rules:
        previous = redacted
        redacted, substitutions = pattern.subn(replacement, redacted)
        if substitutions and redacted != previous:
            categories.append(category)
    return redacted, tuple(categories)


def _normalized_bytes_info(arcname: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(arcname)
    info.size = size
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def redact_snapshot(
    payload: bytes, archive_path: Path
) -> tuple[bytes, list[dict[str, Any]]]:
    members: list[tuple[str, bytes]] = []
    redactions: list[dict[str, Any]] = []
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as source:
        for member in source.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name)
            if any(part.startswith("._") for part in relative.parts):
                continue
            if relative.is_absolute() or ".." in relative.parts:
                raise RuntimeError(
                    f"unsafe member in deployment snapshot {archive_path}: {member.name}"
                )
            extracted = source.extractfile(member)
            if extracted is None:
                raise RuntimeError(
                    f"could not read snapshot member {member.name}: {archive_path}"
                )
            original = extracted.read()
            released, categories = redact_identity(original, relative)
            members.append((relative.as_posix(), released))
            if categories:
                redactions.append(
                    {
                        "archive_path": archive_path.as_posix(),
                        "path": relative.as_posix(),
                        "source_sha256": sha256_bytes(original),
                        "released_sha256": sha256_bytes(released),
                        "categories": list(categories),
                    }
                )
    output = io.BytesIO()
    with (
        gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0) as compressed,
        tarfile.open(fileobj=compressed, mode="w") as archive,
    ):
        for name, released in sorted(members):
            archive.addfile(
                _normalized_bytes_info(name, len(released)), io.BytesIO(released)
            )
    return output.getvalue(), redactions


def artifact_payload(
    root: Path, relative: Path
) -> tuple[bytes, list[dict[str, Any]]]:
    path = root / relative
    original = path.read_bytes()
    if relative.name.endswith(".tar.gz"):
        released, redactions = redact_snapshot(original, relative)
        if released != original:
            redactions.append(
                {
                    "archive_path": None,
                    "path": relative.as_posix(),
                    "source_sha256": sha256_bytes(original),
                    "released_sha256": sha256_bytes(released),
                    "categories": ["archive_metadata_normalization"],
                }
            )
        return released, redactions
    released, categories = redact_identity(original, relative)
    redactions: list[dict[str, Any]] = []
    if categories:
        redactions.append(
            {
                "archive_path": None,
                "path": relative.as_posix(),
                "source_sha256": sha256_bytes(original),
                "released_sha256": sha256_bytes(released),
                "categories": list(categories),
            }
        )
    return released, redactions


def validate_no_bulk_payloads(root: Path, paths: Iterable[Path]) -> None:
    for relative in paths:
        if relative.suffix.lower() in FORBIDDEN_BULK_SUFFIXES:
            raise RuntimeError(f"forbidden model/data payload in artifact: {relative}")
        if not relative.name.endswith(".tar.gz"):
            continue
        payload, _ = artifact_payload(root, relative)
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            forbidden = [
                member.name
                for member in archive.getmembers()
                if member.isfile()
                and Path(member.name).suffix.lower() in FORBIDDEN_BULK_SUFFIXES
            ]
        if forbidden:
            raise RuntimeError(
                f"forbidden model/data payload in nested artifact {relative}: {forbidden}"
            )


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected a JSON object: {path}")
    return value


def jsonl_count(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise RuntimeError(f"blank JSONL line {line_number}: {path}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise RuntimeError(f"non-object JSONL line {line_number}: {path}")
            count += 1
    return count


def validate_cube_block(root: Path, block: CubeBlock) -> None:
    paths = {
        "core_records": root / block.core_records,
        "core_analysis": root / block.core_analysis,
        "checkpoint_lock": root / block.checkpoint_lock,
        "cube_records": root / block.cube_records,
        "cube_analysis": root / block.cube_analysis,
        "core_config": root / block.core_config,
        "cube_config": root / block.cube_config,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"{block.name} is incomplete; missing={missing}")
    if jsonl_count(paths["core_records"]) != 150:
        raise RuntimeError(f"{block.name} does not have exactly 150 core records")
    if jsonl_count(paths["cube_records"]) != 90:
        raise RuntimeError(f"{block.name} does not have exactly 90 cube records")

    core_analysis = load_json(paths["core_analysis"])
    expected_core = {
        "benchmark_id": block.benchmark_id,
        "record_count": 150,
        "integrity_gates_passed": True,
        "input_sha256": sha256_file(paths["core_records"]),
        "config_sha256": sha256_file(paths["core_config"]),
    }
    core_mismatches = {
        key: {"expected": value, "observed": core_analysis.get(key)}
        for key, value in expected_core.items()
        if core_analysis.get(key) != value
    }
    if core_mismatches:
        raise RuntimeError(f"{block.name} core binding mismatch: {core_mismatches}")

    analysis = load_json(paths["cube_analysis"])
    expected = {
        "benchmark_id": block.benchmark_id,
        "core_record_count": 150,
        "derived_record_count": 90,
        "checkpoint_count": 120,
        "integrity_gates_passed": True,
        "core_input_sha256": sha256_file(paths["core_records"]),
        "core_analysis_sha256": sha256_file(paths["core_analysis"]),
        "checkpoint_lock_sha256": sha256_file(paths["checkpoint_lock"]),
        "derived_input_sha256": sha256_file(paths["cube_records"]),
        "config_sha256": sha256_file(paths["cube_config"]),
    }
    mismatches = {
        key: {"expected": value, "observed": analysis.get(key)}
        for key, value in expected.items()
        if analysis.get(key) != value
    }
    if mismatches:
        raise RuntimeError(f"{block.name} cube binding mismatch: {mismatches}")
    if len(analysis.get("all_cases", [])) != block.mandatory_cells:
        raise RuntimeError(f"{block.name} has an unexpected mandatory-cell count")
    primary = analysis.get("primary", {})
    if not isinstance(primary, dict) or (
        primary.get("case"), primary.get("horizon")
    ) != (block.primary_case, block.primary_horizon):
        raise RuntimeError(f"{block.name} has the wrong frozen primary cell")


def validate_semantics(root: Path) -> None:
    for block in CUBE_BLOCKS:
        validate_cube_block(root, block)

    diagnostic_specs = (
        (
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gradient_coupling_20260901.jsonl",
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gradient_coupling_analysis_v4_20260901.json",
            "diagnostic_input_sha256",
        ),
        (
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gauge_feedback_provenance_rerun_20260902.jsonl",
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gauge_feedback_provenance_rerun_analysis_20260902.json",
            "input_sha256",
        ),
    )
    for records_rel, analysis_rel, binding_key in diagnostic_specs:
        records = root / records_rel
        analysis_path = root / analysis_rel
        if jsonl_count(records) != 60:
            raise RuntimeError(f"diagnostic does not have exactly 60 records: {records}")
        analysis = load_json(analysis_path)
        if analysis.get("integrity_gates_passed") is not True:
            raise RuntimeError(f"diagnostic integrity gate failed: {analysis_path}")
        if analysis.get("record_count") != 60:
            raise RuntimeError(f"diagnostic analysis has wrong coverage: {analysis_path}")
        if analysis.get(binding_key) != sha256_file(records):
            raise RuntimeError(f"diagnostic analysis is not bound to records: {analysis_path}")

    synthetic_dir = (
        root / "experiments/constraint_attribution_iclr/confirmation/formal_amended_20260901"
    )
    analysis = load_json(synthetic_dir / "analysis_amended_20260901.json")
    integrity = analysis.get("integrity", {})
    if not isinstance(integrity, dict) or integrity.get("record_count") != 1830:
        raise RuntimeError("synthetic analysis does not certify exactly 1,830 records")
    record_files = sorted(synthetic_dir.glob("*.jsonl"))
    if sum(jsonl_count(path) for path in record_files) != 1830:
        raise RuntimeError("synthetic JSONL files do not contain exactly 1,830 records")


def _run(root: Path, *arguments: str | Path) -> None:
    subprocess.run(
        [sys.executable, *(str(value) for value in arguments)],
        cwd=root,
        check=True,
    )


def _require_identical(generated: Path, canonical: Path) -> None:
    if generated.read_bytes() != canonical.read_bytes():
        raise RuntimeError(
            f"deterministic reanalysis differs from the released artifact: {canonical}"
        )


def run_reanalysis(root: Path) -> None:
    pde = root / "experiments/constraint_attribution_iclr/pdebench"
    configs = root / "configs/constraint_iclr"
    scripts = root / "scripts"
    with tempfile.TemporaryDirectory(prefix="paper-d-reanalysis-") as raw_directory:
        temporary = Path(raw_directory)
        outputs: dict[str, Path] = {}
        specifications = (
            (
                "fno",
                scripts / "analyze_constraint_iclr_pdebench_factorial.py",
                configs / "pdebench_advection_fno_factorial_20260901.yaml",
                pde / "factorial_confirmation_20260901.jsonl",
                pde / "factorial_analysis_20260901.json",
            ),
            (
                "unet",
                scripts / "analyze_constraint_iclr_pdebench_factorial.py",
                configs / "pdebench_advection_unet_enforcement_cube_20260903.yaml",
                pde / "unet_factorial_merged_20260902.jsonl",
                pde / "unet_factorial_analysis_20260903.json",
            ),
            (
                "swe",
                scripts / "analyze_constraint_iclr_pdebench_swe.py",
                configs / "pdebench_swe_rdb_factorial_distributed_20260902.yaml",
                pde / "swe_factorial_confirmation_20260902.jsonl",
                pde / "swe_factorial_analysis_20260902.json",
            ),
        )
        for name, analyzer, config, records, canonical in specifications:
            output = temporary / f"{name}-core.json"
            _run(
                root,
                analyzer,
                "--config",
                config,
                "--input",
                records,
                "--output",
                output,
            )
            _require_identical(output, canonical)
            outputs[name] = output

        cube_specifications = (
            (
                "fno",
                scripts / "analyze_constraint_iclr_pdebench_enforcement_cube.py",
                configs / "pdebench_advection_fno_enforcement_cube_20260901.yaml",
                pde / "advection_enforcement_cube_20260901.jsonl",
                pde / "factorial_confirmation_20260901.jsonl",
                pde / "advection_factorial_checkpoint_lock_20260901.json",
                pde / "advection_enforcement_cube_analysis_20260901.json",
            ),
            (
                "unet",
                scripts / "analyze_constraint_iclr_pdebench_enforcement_cube.py",
                configs / "pdebench_advection_unet_enforcement_cube_20260903.yaml",
                pde / "unet_enforcement_cube_20260903.jsonl",
                pde / "unet_factorial_merged_20260902.jsonl",
                pde / "unet_factorial_checkpoint_lock_20260903.json",
                pde / "unet_enforcement_cube_analysis_20260903.json",
            ),
            (
                "swe",
                scripts / "analyze_constraint_iclr_pdebench_swe_enforcement_cube.py",
                configs / "pdebench_swe_rdb_enforcement_cube_distributed_20260902.yaml",
                pde / "swe_enforcement_cube_derived_20260902.jsonl",
                pde / "swe_factorial_confirmation_20260902.jsonl",
                pde / "swe_checkpoint_lock_20260902.json",
                pde / "swe_enforcement_cube_analysis_20260902.json",
            ),
        )
        for name, analyzer, config, records, core_records, lock, canonical in cube_specifications:
            output = temporary / f"{name}-cube.json"
            _run(
                root,
                analyzer,
                "--config",
                config,
                "--derived-input",
                records,
                "--core-input",
                core_records,
                "--core-analysis",
                outputs[name],
                "--checkpoint-lock",
                lock,
                "--output",
                output,
            )
            _require_identical(output, canonical)
            outputs[f"{name}-cube"] = output

        gradient = temporary / "gradient.json"
        _run(
            root,
            scripts / "analyze_constraint_iclr_pdebench_gradient_coupling_v4.py",
            "--config",
            configs / "pdebench_advection_fno_gradient_coupling_v4_20260901.yaml",
            "--diagnostic-input",
            pde / "advection_gradient_coupling_20260901.jsonl",
            "--factorial-input",
            pde / "factorial_confirmation_20260901.jsonl",
            "--cube-input",
            pde / "advection_enforcement_cube_20260901.jsonl",
            "--checkpoint-lock",
            pde / "advection_factorial_checkpoint_lock_20260901.json",
            "--factorial-analysis",
            outputs["fno"],
            "--cube-analysis",
            outputs["fno-cube"],
            "--output",
            gradient,
        )
        _require_identical(
            gradient, pde / "advection_gradient_coupling_analysis_v4_20260901.json"
        )

        gauge = temporary / "gauge.json"
        _run(
            root,
            scripts / "analyze_constraint_iclr_pdebench_gauge_feedback.py",
            "--config",
            configs / "pdebench_advection_fno_gauge_feedback_identity_runtime_20260902.yaml",
            "--input",
            pde / "advection_gauge_feedback_provenance_rerun_20260902.jsonl",
            "--core-input",
            pde / "factorial_confirmation_20260901.jsonl",
            "--core-analysis",
            outputs["fno"],
            "--cube-input",
            pde / "advection_enforcement_cube_20260901.jsonl",
            "--cube-analysis",
            outputs["fno-cube"],
            "--checkpoint-lock",
            pde / "advection_factorial_checkpoint_lock_20260901.json",
            "--output",
            gauge,
        )
        _require_identical(
            gauge,
            pde / "advection_gauge_feedback_provenance_rerun_analysis_20260902.json",
        )

        synthetic_dir = (
            root
            / "experiments/constraint_attribution_iclr/confirmation/formal_amended_20260901"
        )
        synthetic_output = temporary / "synthetic.json"
        synthetic_arguments: list[str | Path] = [
            scripts / "analyze_constraint_iclr_confirmation_amended.py",
            "--records",
            *(
                path.relative_to(root)
                for path in sorted(synthetic_dir.glob("*.jsonl"))
            ),
            "--lock",
            Path(
                "experiments/constraint_attribution_iclr/pilot/"
                "pilot_lock_final_idonly_20260831.json"
            ),
            "--failure-decision",
            Path(
                "research/discovery/decisions/"
                "constraint_attribution_iclr_v100b_failure_continuation_20260901.yaml"
            ),
            "--out",
            synthetic_output,
        ]
        artifact_manifest = root / MANIFEST_PATH
        if artifact_manifest.is_file():
            synthetic_arguments.extend(("--artifact-manifest", artifact_manifest))
        _run(root, *synthetic_arguments)
        _require_identical(
            synthetic_output, synthetic_dir / "analysis_amended_20260901.json"
        )


def run_regeneration(root: Path) -> None:
    figures = root / PAPER_DIR / "figures"
    pde = root / "experiments/constraint_attribution_iclr/pdebench"
    synthetic = (
        root
        / "experiments/constraint_attribution_iclr/confirmation/formal_amended_20260901/"
        "analysis_amended_20260901.json"
    )
    specifications = (
        (
            "make_pdebench_factorial_macros.py",
            [pde / "factorial_analysis_20260901.json", figures / "pdebench_factorial_macros.tex"],
            [1],
        ),
        (
            "make_pdebench_cube_macros.py",
            [
                pde / "advection_enforcement_cube_analysis_20260901.json",
                pde / "advection_gradient_coupling_analysis_v4_20260901.json",
                figures / "pdebench_cube_macros.tex",
            ],
            [2],
        ),
        (
            "make_pdebench_cube_table.py",
            [
                pde / "advection_enforcement_cube_analysis_20260901.json",
                figures / "pdebench_cube_rows.tex",
            ],
            [1],
        ),
        (
            "make_pdebench_cube_mechanism.py",
            [
                pde / "advection_enforcement_cube_analysis_20260901.json",
                figures / "pdebench_cube_mechanism.pdf",
            ],
            [1],
        ),
        (
            "make_pdebench_swe_macros.py",
            [
                pde / "swe_factorial_analysis_20260902.json",
                pde / "swe_enforcement_cube_analysis_20260902.json",
                figures / "pdebench_swe_macros.tex",
            ],
            [2],
        ),
        (
            "make_pdebench_gauge_feedback_macros.py",
            [
                pde / "advection_gauge_feedback_provenance_rerun_analysis_20260902.json",
                figures / "pdebench_gauge_feedback_macros.tex",
            ],
            [1],
        ),
        (
            "make_pdebench_unet_macros.py",
            [
                pde / "unet_enforcement_cube_analysis_20260903.json",
                figures / "pdebench_unet_macros.tex",
            ],
            [1],
        ),
        (
            "make_pdebench_cube_table.py",
            [
                pde / "unet_enforcement_cube_analysis_20260903.json",
                figures / "pdebench_unet_cube_rows.tex",
            ],
            [1],
        ),
        (
            "make_synthetic_amended_table.py",
            [
                synthetic,
                figures / "synthetic_amended_rows.tex",
                "--macros",
                figures / "synthetic_amended_macros.tex",
            ],
            [1, 3],
        ),
    )
    with tempfile.TemporaryDirectory(prefix="paper-d-figures-") as raw_directory:
        temporary = Path(raw_directory)
        for specification_index, (script, raw_arguments, output_indices) in enumerate(
            specifications
        ):
            arguments = list(raw_arguments)
            comparisons: list[tuple[Path, Path]] = []
            for output_index in output_indices:
                canonical = Path(arguments[output_index])
                generated = temporary / f"{specification_index}-{canonical.name}"
                arguments[output_index] = generated
                comparisons.append((generated, canonical))
            _run(root, figures / script, *arguments)
            for generated, canonical in comparisons:
                _require_identical(generated, canonical)


def snapshot_source_catalog(
    root: Path,
    archives: Iterable[Path],
    redactions: Iterable[dict[str, Any]] = (),
) -> dict[Path, set[str]]:
    redaction_lookup: dict[tuple[Path, Path, str], str] = {}
    for entry in redactions:
        raw_archive = entry.get("archive_path")
        if raw_archive is None:
            continue
        key = (
            Path(str(raw_archive)),
            Path(str(entry["path"])),
            str(entry["released_sha256"]),
        )
        redaction_lookup[key] = str(entry["source_sha256"])
    catalog: dict[Path, set[str]] = {}
    for archive_relative in archives:
        archive_path = root / archive_relative
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                relative = Path(member.name)
                if (
                    relative.is_absolute()
                    or ".." in relative.parts
                    or any(part.startswith("._") for part in relative.parts)
                ):
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise RuntimeError(
                        f"could not read snapshot member {member.name}: {archive_path}"
                    )
                digest = hashlib.sha256(extracted.read()).hexdigest()
                catalog.setdefault(relative, set()).add(digest)
                original_digest = redaction_lookup.get(
                    (archive_relative, relative, digest)
                )
                if original_digest is not None:
                    catalog[relative].add(original_digest)
    return catalog


def collect_provenance_sources(
    root: Path,
    record_paths: Iterable[Path],
    snapshot_archives: Iterable[Path] = (),
    redactions: Iterable[dict[str, Any]] = (),
) -> set[Path]:
    expected: set[tuple[Path, str]] = set()
    for records_relative in record_paths:
        records_path = root / records_relative
        with records_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                record = json.loads(line)
                sources = record.get("provenance", {}).get("source_sha256", {})
                if not isinstance(sources, dict):
                    raise RuntimeError(
                        f"invalid source manifest at {records_path}:{line_number}"
                    )
                for raw_path, raw_digest in sources.items():
                    relative = Path(str(raw_path))
                    digest = str(raw_digest)
                    if relative.is_absolute() or ".." in relative.parts:
                        raise RuntimeError(f"unsafe provenance source path: {raw_path}")
                    if len(digest) != 64:
                        raise RuntimeError(f"invalid provenance SHA-256 for {raw_path}")
                    expected.add((relative, digest))
    archives = tuple(snapshot_archives)
    redaction_entries = tuple(redactions)
    catalog = snapshot_source_catalog(root, archives, redaction_entries)
    direct_redactions = {
        (
            Path(str(entry["path"])),
            str(entry["released_sha256"]),
        ): str(entry["source_sha256"])
        for entry in redaction_entries
        if entry.get("archive_path") is None
    }
    current_matches: set[Path] = set()
    for relative, digest in expected:
        path = root / relative
        if path.is_file():
            current_digest = sha256_file(path)
            if current_digest == digest or direct_redactions.get(
                (relative, current_digest)
            ) == digest:
                current_matches.add(relative)
                continue
        if digest in catalog.get(relative, set()):
            continue
        raise RuntimeError(
            f"provenance source version is absent from current files and snapshots: "
            f"{relative} sha256={digest}"
        )
    return current_matches


def collect_release_files(root: Path) -> list[Path]:
    explicit = set(BASE_RELEASE_FILES)
    for block in CUBE_BLOCKS:
        explicit.update(
            Path(value)
            for value in (
                block.core_config,
                block.cube_config,
                block.core_records,
                block.core_analysis,
                block.checkpoint_lock,
                block.cube_records,
                block.cube_analysis,
            )
        )
    explicit.update(
        Path(value)
        for value in (
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gradient_coupling_20260901.jsonl",
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gradient_coupling_analysis_v4_20260901.json",
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gauge_feedback_provenance_rerun_20260902.jsonl",
            "experiments/constraint_attribution_iclr/pdebench/"
            "advection_gauge_feedback_provenance_rerun_analysis_20260902.json",
            "experiments/constraint_attribution_iclr/pdebench/data_lock_v2_beta0.4.json",
            "experiments/constraint_attribution_iclr/pdebench/data_lock_swe_rdb_20260902.json",
            "experiments/constraint_attribution_iclr/pdebench/data_admission_failure_v1_20260901.yaml",
            "experiments/constraint_attribution_iclr/pdebench/burgers_nu0p01_source_20260901.json",
            "experiments/constraint_attribution_iclr/pdebench/cns_eta0p01_source_20260901.json",
            "experiments/constraint_attribution_iclr/pilot/"
            "pilot_lock_final_idonly_20260831.json",
            "experiments/constraint_attribution_iclr/deployment/"
            "v100a_aburgers_nonfinite_incident_20260831.yaml",
            "experiments/constraint_attribution_iclr/deployment/"
            "v100b_bburgers_nonfinite_incident_20260901.yaml",
        )
    )
    patterns = (
        "papers/paper_d_constraints/*.tex",
        "papers/paper_d_constraints/*.bib",
        "papers/paper_d_constraints/*.sty",
        "papers/paper_d_constraints/*.bst",
        "papers/paper_d_constraints/figures/*.py",
        "papers/paper_d_constraints/figures/*.tex",
        "papers/proposal/ecomd_constraint_attribution_iclr*.md",
        "configs/constraint_iclr/*.yaml",
        "research/discovery/decisions/constraint_attribution_iclr*.yaml",
        "scripts/*constraint_iclr*.py",
        "scripts/*constraint_iclr*.sh",
        "tests/test_constraint_iclr*.py",
        "tests/test_paper_d*.py",
        "experiments/constraint_attribution_iclr/confirmation/formal_amended_20260901/*",
        "experiments/constraint_attribution_iclr/deployment/*.tar.gz",
        "experiments/constraint_attribution_iclr/deployment/*.sha256",
        "experiments/constraint_attribution_iclr/deployment/*.sha256s",
        "experiments/constraint_attribution_iclr/deployment/*.files",
        "experiments/constraint_attribution_iclr/deployment/*.log",
        "experiments/constraint_attribution_iclr/deployment/*receipt*.yaml",
    )
    for pattern in patterns:
        explicit.update(path.relative_to(root) for path in root.glob(pattern) if path.is_file())
    record_paths = sorted(path for path in explicit if path.suffix == ".jsonl")
    snapshot_archives = sorted(
        path
        for path in explicit
        if path.parent == Path("experiments/constraint_attribution_iclr/deployment")
        and path.name.endswith(".tar.gz")
    )
    explicit.update(collect_provenance_sources(root, record_paths, snapshot_archives))
    missing = sorted(path for path in explicit if not (root / path).is_file())
    if missing:
        raise RuntimeError(f"release payload is incomplete; missing={[str(path) for path in missing]}")
    paths = sorted(explicit, key=lambda path: path.as_posix())
    validate_no_bulk_payloads(root, paths)
    return paths


def build_manifest(root: Path, paths: Iterable[Path]) -> dict[str, Any]:
    paths = list(paths)
    for relative in paths:
        if "deployment" in relative.parts or any(
            token in relative.name for token in ("admission_failure", "nonfinite_incident")
        ):
            raise RuntimeError(
                "public artifact includes internal provenance; rebuild its explicit "
                f"scientific whitelist before release: {relative}"
            )
    entries = []
    redactions: list[dict[str, Any]] = []
    for relative in paths:
        path = root / relative
        payload, file_redactions = artifact_payload(root, relative)
        entry: dict[str, Any] = {
            "path": relative.as_posix(),
            "bytes": len(payload),
            "sha256": sha256_bytes(payload),
        }
        if file_redactions:
            if _requires_byte_preservation(relative):
                raise RuntimeError(
                    "double-blind redaction would alter a frozen numerical record, "
                    f"analysis, or scientific config: {relative}"
                )
            entry["source_sha256"] = sha256_file(path)
            entry["redacted_for_double_blind"] = True
            redactions.extend(file_redactions)
        entries.append(entry)
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "checkpoint_bytes_included": False,
        "public_dataset_bytes_included": False,
        "provenance_source_versions_verified": True,
        "double_blind_redactions": redactions,
        "record_contract": {
            "core_records": 450,
            "derived_cube_records": 270,
            "checkpoint_locks": 360,
            "gradient_records": 60,
            "gauge_records": 60,
            "synthetic_valid_records": 1830,
        },
        "files": entries,
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> bytes:
    payload = (
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return payload


def create_archive(
    root: Path, paths: Iterable[Path], manifest_payload: bytes, output: Path
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with (
        temporary.open("wb") as raw,
        gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed,
        tarfile.open(fileobj=compressed, mode="w") as archive,
    ):
        for relative in paths:
            payload, _ = artifact_payload(root, relative)
            info = _normalized_bytes_info(
                f"{ARCHIVE_ROOT}/{relative.as_posix()}", len(payload)
            )
            archive.addfile(info, io.BytesIO(payload))
        manifest_names = (
            f"{ARCHIVE_ROOT}/ARTIFACT_MANIFEST.json",
            f"{ARCHIVE_ROOT}/{MANIFEST_PATH.as_posix()}",
        )
        for manifest_name in manifest_names:
            manifest_info = _normalized_bytes_info(
                manifest_name, len(manifest_payload)
            )
            archive.addfile(manifest_info, io.BytesIO(manifest_payload))
    temporary.replace(output)
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{sha256_file(output)}  {output.name}\n", encoding="utf-8"
    )


def verify_manifest(root: Path, manifest_path: Path) -> None:
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != ARTIFACT_SCHEMA_VERSION:
        raise RuntimeError("unexpected artifact-manifest schema")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise RuntimeError("artifact manifest has no files")
    redactions = manifest.get("double_blind_redactions", [])
    if not isinstance(redactions, list) or any(
        not isinstance(entry, dict) for entry in redactions
    ):
        raise RuntimeError("artifact redaction manifest is malformed")
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise RuntimeError("artifact-manifest entry is not an object")
        raw_path = str(entry.get("path"))
        if raw_path in seen:
            raise RuntimeError(f"duplicate artifact-manifest path: {raw_path}")
        seen.add(raw_path)
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"unsafe artifact-manifest path: {raw_path}")
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"artifact file is missing: {path}")
        payload, _ = artifact_payload(root, relative)
        if len(payload) != int(entry.get("bytes", -1)):
            raise RuntimeError(f"artifact byte-count mismatch: {path}")
        if sha256_bytes(payload) != entry.get("sha256"):
            raise RuntimeError(f"artifact SHA-256 mismatch: {path}")
        source_sha256 = entry.get("source_sha256")
        if source_sha256 is not None and sha256_file(path) not in {
            str(source_sha256),
            str(entry.get("sha256")),
        }:
            raise RuntimeError(f"artifact redaction source mismatch: {path}")
    validate_semantics(root)
    manifest_paths = [Path(str(entry["path"])) for entry in files]
    validate_no_bulk_payloads(root, manifest_paths)
    records = sorted(path for path in manifest_paths if path.suffix == ".jsonl")
    snapshots = sorted(
        path
        for path in manifest_paths
        if path.parent == Path("experiments/constraint_attribution_iclr/deployment")
        and path.name.endswith(".tar.gz")
    )
    collect_provenance_sources(root, records, snapshots, redactions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--regenerate", action="store_true")
    action.add_argument("--verify", action="store_true")
    action.add_argument("--package", type=Path)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    manifest_path = args.manifest
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    if args.regenerate:
        validate_semantics(root)
        run_reanalysis(root)
        run_regeneration(root)
        print("reproduced all Paper D analyses, figures, and result-derived TeX")
        return
    if args.verify:
        verify_manifest(root, manifest_path)
        print(f"verified_manifest={manifest_path}")
        print(f"manifest_sha256={sha256_file(manifest_path)}")
        return

    validate_semantics(root)
    paths = collect_release_files(root)
    manifest = build_manifest(root, paths)
    payload = write_manifest(manifest_path, manifest)
    output = args.package
    if not output.is_absolute():
        output = root / output
    create_archive(root, paths, payload, output)
    print(f"artifact={output}")
    print(f"artifact_sha256={sha256_file(output)}")
    print(f"manifest={manifest_path}")
    print(f"manifest_sha256={sha256_file(manifest_path)}")
    print(f"file_count={len(paths)}")


if __name__ == "__main__":
    main()
