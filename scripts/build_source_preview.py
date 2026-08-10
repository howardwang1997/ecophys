"""Build and verify an allow-listed EcoMD source-preview archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
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


def _tracked_files(repo: Path, manifest: list[str]) -> list[tuple[str, int]]:
    raw = _run_git(repo, "ls-files", "--stage", "-z", "--", *manifest)
    records: list[tuple[str, int]] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, encoded_path = item.split(b"\t", maxsplit=1)
        mode_text, _, stage_text = metadata.decode("ascii").split()
        if stage_text != "0":
            raise ValueError(f"unmerged release path: {encoded_path!r}")
        path = encoded_path.decode("utf-8")
        records.append((path, int(mode_text, 8)))
    tracked_paths = {path for path, _ in records}
    for entry in manifest:
        if entry not in tracked_paths and not any(
            path.startswith(f"{entry.rstrip('/')}/") for path in tracked_paths
        ):
            raise ValueError(f"manifest entry has no tracked files: {entry}")
    return sorted(records)


def _build_tar(
    repo: Path,
    records: list[tuple[str, int]],
    *,
    prefix: str,
    commit_time: int,
) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.GNU_FORMAT) as archive:
        for relative_text, git_mode in records:
            relative = PurePosixPath(relative_text)
            _validate_member(relative)
            source = repo / relative_text
            if not source.is_file():
                raise ValueError(f"tracked release file is not materialized: {relative}")
            if git_mode not in (0o100644, 0o100755):
                raise ValueError(f"unsupported git mode {git_mode:o}: {relative}")
            payload = source.read_bytes()
            info = tarfile.TarInfo(f"{prefix}{relative.as_posix()}")
            info.size = len(payload)
            info.mtime = commit_time
            info.mode = 0o755 if git_mode == 0o100755 else 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(payload))
    return output.getvalue()


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
    head_revision = _run_git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    if revision_text != head_revision:
        raise ValueError("working-tree builder currently requires --ref HEAD")
    dirty = _run_git(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        *manifest,
    ).decode("utf-8")
    if dirty:
        raise ValueError(f"release allow-list is not clean against HEAD:\n{dirty}")
    commit_time = int(
        _run_git(repo, "show", "-s", "--format=%ct", revision_text)
        .decode("ascii")
        .strip()
    )
    prefix = f"ecomd-source-preview-{revision_text[:12]}/"
    archive_tar = _build_tar(
        repo,
        _tracked_files(repo, manifest),
        prefix=prefix,
        commit_time=commit_time,
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
