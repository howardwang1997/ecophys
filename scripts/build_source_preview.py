"""Build and verify an allow-listed EcoMD source-preview archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

FORBIDDEN_SUFFIXES = {
    ".ckpt",
    ".csv",
    ".feather",
    ".h5",
    ".npz",
    ".parquet",
    ".pt",
    ".pth",
    ".zip",
}
FORBIDDEN_PARTS = {
    ".aws",
    ".git",
    ".wandb",
    "checkpoints",
    "outputs",
    "results",
    "wandb",
}
FORBIDDEN_NAMES = {
    ".env",
    ".env.local",
    "credentials",
    "credentials.json",
    "secrets.json",
}


def _run_git(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def _load_manifest(path: Path) -> list[str]:
    entries = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not entries or len(entries) != len(set(entries)):
        raise ValueError("source-preview manifest must be non-empty and unique")
    for entry in entries:
        candidate = PurePosixPath(entry)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"unsafe manifest path: {entry}")
    return entries


def _validate_member(relative: PurePosixPath) -> None:
    lowered_parts = {part.lower() for part in relative.parts}
    if lowered_parts & FORBIDDEN_PARTS:
        raise ValueError(f"forbidden directory in archive: {relative}")
    if relative.name.lower() in FORBIDDEN_NAMES:
        raise ValueError(f"forbidden filename in archive: {relative}")
    if relative.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise ValueError(f"forbidden file type in archive: {relative}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-bytes", type=int, default=10 * 1024 * 1024)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    manifest_path = repo / "release" / "source_preview_manifest.txt"
    manifest = _load_manifest(manifest_path)
    revision = _run_git(repo, "rev-parse", "--verify", f"{args.ref}^{{commit}}")
    revision_text = revision.decode("ascii").strip()
    prefix = f"ecomd-source-preview-{revision_text[:12]}/"
    archive_tar = _run_git(
        repo,
        "archive",
        "--format=tar",
        f"--prefix={prefix}",
        revision_text,
        *manifest,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = args.output_dir / f"ecomd-source-preview-{revision_text[:12]}.tar.gz"
    with (
        archive_path.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed,
    ):
        compressed.write(archive_tar)

    if archive_path.stat().st_size > args.max_bytes:
        raise ValueError(
            f"archive is {archive_path.stat().st_size} bytes; limit is {args.max_bytes}"
        )

    member_count = 0
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if not path.parts or path.parts[0] != prefix.rstrip("/"):
                raise ValueError(f"archive member escaped prefix: {path}")
            relative = PurePosixPath(*path.parts[1:])
            if relative.parts:
                _validate_member(relative)
            if member.isfile():
                member_count += 1

    archive_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    report = {
        "artifact": archive_path.name,
        "artifact_bytes": archive_path.stat().st_size,
        "artifact_sha256": archive_hash,
        "file_count": member_count,
        "git_revision": revision_text,
        "manifest_sha256": manifest_hash,
        "ref": args.ref,
    }
    report_path = archive_path.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
