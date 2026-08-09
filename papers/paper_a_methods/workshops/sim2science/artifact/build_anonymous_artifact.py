"""Build a deterministic, identity-screened review artifact for the Sim2Science paper."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from collections.abc import Sequence
from pathlib import Path

ARTIFACT_SOURCE_DIR = Path(__file__).resolve().parent
PAPER_DIR = ARTIFACT_SOURCE_DIR.parent
REPO_ROOT = ARTIFACT_SOURCE_DIR.parents[4]
EXPERIMENT_DIR = REPO_ROOT / "experiments/127_workshop_claim_gates"

CONFIG_PATHS = (
    "experiments/113_gabaix_solve/config_concave_d050_seed0.yaml",
    "experiments/113_gabaix_solve/config_baseline_seed0.yaml",
    "experiments/114_concave_confirm/config_ndx_concave_d050_seed0.yaml",
    "experiments/114_concave_confirm/config_gold_concave_d050_seed0.yaml",
    "experiments/114_concave_confirm/config_eurusd_concave_d050_seed0.yaml",
    "experiments/114_concave_confirm/config_btcusdt_concave_d050_seed0.yaml",
    "experiments/114_concave_confirm/config_btcusdt_baseline_seed0.yaml",
    "experiments/108_neural_sde_scout/config_sv_d3_both_seed0.yaml",
    "experiments/108_neural_sde_scout/config_sv_d3_both_seed1.yaml",
    "experiments/108_neural_sde_scout/config_sv_d3_both_seed2.yaml",
)

ECOMD_AUDIT_PATHS = (
    "ecomd/__init__.py",
    "ecomd/baselines/__init__.py",
    "ecomd/baselines/ar1_sv.py",
    "ecomd/baselines/garch.py",
    "ecomd/eval/__init__.py",
    "ecomd/eval/canonical_bands.py",
    "ecomd/eval/stationarity_baselines.py",
    "ecomd/eval/stationarity_gate.py",
    "ecomd/eval/stylized_facts.py",
    "ecomd/inference/__init__.py",
    "ecomd/inference/seed_manifest.py",
)

EXPERIMENT_SOURCE_PATHS = (
    "experiments/127_workshop_claim_gates/run_analytic_controls.py",
    "experiments/127_workshop_claim_gates/fit_learned_calibration.py",
    "experiments/127_workshop_claim_gates/analyze_learned_results.py",
    "experiments/127_workshop_claim_gates/analyze_learned_robustness.py",
    "experiments/127_workshop_claim_gates/run_exploratory_mser5.py",
)

TEST_PATHS = (
    "tests/test_ar1_sv.py",
    "tests/test_canonical_bands.py",
    "tests/test_exp127_analytic_controls.py",
    "tests/test_exp127_analyze_learned.py",
    "tests/test_exp127_fit_learned_calibration.py",
    "tests/test_exp127_learned_robustness.py",
    "tests/test_exp127_exploratory_mser5.py",
    "tests/test_garch.py",
    "tests/test_seed_manifest.py",
    "tests/test_sim2science_apply_results.py",
    "tests/test_sim2science_figures.py",
    "tests/test_sim2science_submission_check.py",
    "tests/test_stationarity_baselines.py",
    "tests/test_stationarity_gate.py",
)

ANALYTIC_SOURCE_PATHS = (
    "experiments/080_baselines_30seed/results_garch_seed0/inference_merged.json",
    "experiments/080_baselines_30seed/results_ar1_sv_seed0/inference_merged.json",
)

TEXT_SUFFIXES = {".json", ".md", ".py", ".tex", ".bib", ".toml", ".txt", ".yaml", ".yml"}
FINAL_RESULT_FILES = (
    "LEARNED_GATE_FITS.json",
    "LEARNED_RESULTS.json",
    "LEARNED_ROBUSTNESS.json",
)
GIT_SHA_PATTERN = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.IGNORECASE)
GPU_UUID_PATTERN = re.compile(r"GPU-[0-9a-f-]{20,}", re.IGNORECASE)
USER_HOME_PATTERN = re.compile(r"/Users/[^/\s\"']+")
FORBIDDEN_PATTERNS = {
    "author name": re.compile(r"howard(?:wang)?", re.IGNORECASE),
    "macOS user path": re.compile(r"/Users/[^/\s\"']+"),
    "first compute address": re.compile(r"100\.80\.236\.112"),
    "second compute address": re.compile(r"100\.123\.220\.57"),
}

ANONYMOUS_LICENSE = """MIT License

Copyright (c) 2026 Anonymous Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

ANONYMOUS_PYPROJECT = """[build-system]
requires = [\"setuptools>=68\", \"wheel\"]
build-backend = \"setuptools.build_meta\"

[project]
name = \"sim2science-transient-audit\"
version = \"1.0.0\"
description = \"Anonymous reproducibility artifact for a simulator transient audit\"
requires-python = \">=3.11\"
license = { file = \"LICENSE\" }
dependencies = [
  \"numpy>=1.26\", \"scipy>=1.11\", \"matplotlib>=3.8\",
  \"statsmodels>=0.14\", \"pytest>=8.0\"
]

[tool.setuptools.packages.find]
include = [\"ecomd*\"]

[tool.pytest.ini_options]
testpaths = [\"tests\"]
addopts = \"-ra -q\"
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_text(text: str) -> str:
    sanitized = text.replace(str(REPO_ROOT), "<repository-root>")
    sanitized = USER_HOME_PATTERN.sub("<user-home>", sanitized)
    sanitized = GIT_SHA_PATTERN.sub("anonymous-review-snapshot", sanitized)
    return GPU_UUID_PATTERN.sub("redacted-gpu-uuid", sanitized)


def source_paths() -> list[Path]:
    paths = [REPO_ROOT / path for path in ECOMD_AUDIT_PATHS]
    paths.extend(REPO_ROOT / path for path in CONFIG_PATHS)
    paths.extend(REPO_ROOT / path for path in EXPERIMENT_SOURCE_PATHS)
    paths.extend(REPO_ROOT / path for path in TEST_PATHS)
    paths.extend(REPO_ROOT / path for path in ANALYTIC_SOURCE_PATHS)
    paths.extend(
        sorted(
            path
            for path in EXPERIMENT_DIR.iterdir()
            if path.is_file() and path.suffix in {".json", ".md"}
        )
    )
    paths.extend(
        [
            PAPER_DIR / "main.tex",
            PAPER_DIR / "BUILD.md",
            PAPER_DIR / "references.bib",
            PAPER_DIR / "checklist.tex",
            PAPER_DIR / "check_submission.py",
            PAPER_DIR / "apply_learned_results.py",
            PAPER_DIR / "make_figures.py",
            PAPER_DIR / "neurips_2026.sty",
            PAPER_DIR / "figures/fig_ecomd_object.pdf",
            PAPER_DIR / "figures/fig_protocol.pdf",
            PAPER_DIR / "figures/fig_analytic_controls.pdf",
            ARTIFACT_SOURCE_DIR / "README.md",
            ARTIFACT_SOURCE_DIR / "environment_cpu.yml",
        ]
    )
    learned_figure = PAPER_DIR / "figures/fig_learned_results.pdf"
    if learned_figure.is_file():
        paths.append(learned_figure)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"artifact source files are missing: {missing}")
    return sorted(set(paths))


def destination_relative(path: Path) -> Path:
    if path.parent == ARTIFACT_SOURCE_DIR and path.name in {"README.md", "environment_cpu.yml"}:
        return Path(path.name)
    return path.relative_to(REPO_ROOT)


def copy_sanitized(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in TEXT_SUFFIXES:
        destination.write_text(sanitize_text(source.read_text()))
    else:
        shutil.copy2(source, destination)


def copy_derived(derived_root: Path, destination_root: Path) -> None:
    allowed_suffixes = {".json", ".npz"}
    for source in sorted(path for path in derived_root.rglob("*") if path.is_file()):
        if source.suffix not in allowed_suffixes:
            continue
        destination = destination_root / "derived" / source.relative_to(derived_root)
        copy_sanitized(source, destination)


def scan_identity(root: Path) -> None:
    violations: list[str] = []
    for path in sorted(file for file in root.rglob("*") if file.is_file()):
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE"}:
            continue
        text = path.read_text(errors="replace")
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                violations.append(f"{path.relative_to(root)}: {label}")
    if violations:
        raise RuntimeError("identity scan failed:\n" + "\n".join(violations))


def manifest_rows(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(file for file in root.rglob("*") if file.is_file()):
        if path.name == "ARTIFACT_MANIFEST.json":
            continue
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return rows


def write_deterministic_zip(root: Path, archive: Path) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in sorted(file for file in root.rglob("*") if file.is_file()):
            relative = Path("sim2science_artifact") / path.relative_to(root)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes())


def build(output_dir: Path, derived_root: Path | None, allow_incomplete: bool) -> tuple[Path, Path]:
    missing_final = [name for name in FINAL_RESULT_FILES if not (EXPERIMENT_DIR / name).is_file()]
    if not (PAPER_DIR / "figures/fig_learned_results.pdf").is_file():
        missing_final.append("figures/fig_learned_results.pdf")
    if missing_final and not allow_incomplete:
        raise RuntimeError(f"final learned artifacts are missing: {missing_final}")
    if output_dir.exists() or output_dir.with_suffix(".zip").exists():
        raise FileExistsError(f"refusing to overwrite existing artifact target {output_dir}")

    output_dir.mkdir(parents=True)
    for source in source_paths():
        copy_sanitized(source, output_dir / destination_relative(source))
    (output_dir / "LICENSE").write_text(ANONYMOUS_LICENSE)
    (output_dir / "pyproject.toml").write_text(ANONYMOUS_PYPROJECT)
    if derived_root is not None:
        if not derived_root.is_dir():
            raise FileNotFoundError(f"derived artifact root does not exist: {derived_root}")
        copy_derived(derived_root, output_dir)

    scan_identity(output_dir)
    manifest = {
        "schema_version": 1,
        "double_blind": True,
        "complete": not missing_final and derived_root is not None,
        "reproduction_scope": "audit-analysis-from-frozen-trajectories",
        "simulator_training_source_included": False,
        "learned_checkpoint_binaries_included": False,
        "frozen_trajectory_outputs_included": derived_root is not None,
        "missing_final_files": missing_final,
        "derived_outputs_included": derived_root is not None,
        "files": manifest_rows(output_dir),
    }
    manifest_path = output_dir / "ARTIFACT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    scan_identity(output_dir)

    archive = output_dir.with_suffix(".zip")
    write_deterministic_zip(output_dir, archive)
    return manifest_path, archive


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--derived-root", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    manifest, archive = build(args.output_dir, args.derived_root, args.allow_incomplete)
    print(
        json.dumps(
            {
                "artifact": str(archive),
                "artifact_sha256": sha256_file(archive),
                "manifest": str(manifest),
                "manifest_sha256": sha256_file(manifest),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
