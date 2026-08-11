"""Repository ownership checks for market-world experiments."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def git_commit(repository: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def require_clean_repository(repository: Path) -> str:
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal experiment requires a clean Git worktree")
    return git_commit(repository)


def research_code_sha256(repository: Path) -> str:
    patterns = (
        "ecomd/market_world/*.py",
        "experiments/141_multiclock_intervention_feasibility/*.py",
    )
    paths: set[Path] = set()
    for pattern in patterns:
        paths.update(repository.glob(pattern))
    paths.add(repository / "configs/market_world/intervention_feasibility_v1.yaml")
    paths.add(repository / "experiments/141_multiclock_intervention_feasibility/PREREGISTRATION.md")
    digest = hashlib.sha256()
    for path in sorted(paths):
        relative = path.relative_to(repository).as_posix()
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
