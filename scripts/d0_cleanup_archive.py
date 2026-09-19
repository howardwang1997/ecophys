#!/usr/bin/env python
"""D0-S1 node-cleanup archive tool (reexploration ops plan Part B §3 item 1;
relocation authorization prereg §4.1 / D1_09).

Implements the frozen cleanup procedure:

    every artifact in experiments/constraint_attribution_iclr/deployment/*.files
    + *.sha256s re-hash-verified -> uploaded to r2://ecophys/paper_d_archive/
    -> manifest-verified -> local delete -> re-verify.
    Nothing without a manifest is deleted.

Phases map 1:1 onto subcommands so the D0-S1 op session can run and audit each
step separately:

    plan    --root <repo> [--deployment-dir <rel>]
            [--include-singular-sha256] [--r2-prefix <prefix>]
            Dry-run (listing/hashes only). Resolves every manifest, re-hashes
            every artifact, verifies triple-set tarball contents against their
            .sha256s, dedups eligible rows by path, writes a plan JSON. No
            mutation, no network. The r2 prefix (default paper_d_archive) is
            recorded in the plan and keys every later upload; per-snapshot-copy
            prefixes keep identical rel_paths from different roots off the
            same R2 object.
    upload  --plan <plan.json> --yes
            Uploads status=eligible rows to r2://ecophys/paper_d_archive/
            via rclone, re-hashes the remote bytes streamingly, then uploads
            the manifest files themselves under <prefix>/manifests/ (the
            destination-side provenance), and writes an upload receipt. Any
            verification failure aborts before further uploads (uploads
            completed before the abort have no receipt and therefore can
            never be deleted — fail-closed).
    verify  --plan <plan.json>
            Re-checks remote bytes against the recorded hashes (no mutation).
    delete  --upload-receipt <receipt.json> --plan <plan.json> --yes
            Deletes local artifacts only under a receipt that provably binds
            the plan (plan file hash recorded in the receipt) and whose every
            entry matches an eligible plan row. Two passes: every entry is
            validated (safe path, present, hash unchanged, r2 key derived
            from the plan) before the first unlink. After deletion the
            archived bytes are re-hashed remotely and the receipt (written
            incrementally) records both re-verifications.
    check-free --path <mount> [--threshold 0.40]
            statvfs report for the >= 40%-free launch gate (prereg §8.3);
            thresholds below the prereg floor 0.40 are refused.

Manifest grammar found in the deployment directory (2026-09-19 survey):

    <n>.files + <n>.sha256s + <n>.tar.gz   triple set: .sha256s hashes the
                                          sources bundled into the tarball;
                                          no manifest pins the tarball's own
                                          bytes, so at plan time the tarball
                                          is opened and every manifest line
                                          is verified against the hashed
                                          tarball members (missing member or
                                          digest mismatch = ineligible).
                                          The tarball's own hash is recorded
                                          at plan time and verified
                                          post-upload.
    <n>.sha256 + <n>.tar.gz               pair set: the singular .sha256 pins
                                          the tarball hash directly. Only
                                          read under --include-singular-sha256
                                          (see policy below).
    <n>.sha256s (bare)                     hashes paths (repo-relative,
                                          repo-root files like pyproject.toml,
                                          or chunk names) that live outside
                                          the deployment dir; bare names are
                                          resolved to the deployment dir or
                                          the repo root, whichever holds a
                                          regular file.
    *.tar.gz with no manifest              reported under
                                          unmanifested_tarballs; never
                                          uploaded, never deleted. Three real
                                          bundles (constraint_iclr_* names
                                          whose .files/.sha256s stems differ)
                                          sit here today and stay retained.

Policy: the default manifest authority is the ops plan's literal enumeration
(*.files + *.sha256s). The inclusive reading that also grants authority to
singular *.sha256 pairs (a singular .sha256 pins the tarball hash directly)
is opt-in via --include-singular-sha256, recorded in the plan JSON either
way, so any widening at D0-S1 is an explicit, auditable choice rather than
a default.

Fail-closed: plan and delete refuse paths outside --root or crossing any
symlinked component (including the receipt root itself); upload re-validates
every path with the same rule before invoking rclone; any hash mismatch
aborts the phase; eligible rows are deduplicated by path (the real manifests
pin shared repo files in up to 11 manifests each — duplicate receipt entries
would abort a delete mid-phase); every receipt carries the hash of the
artifact and plan it authorizes. No RNG.

This tool grants no execution authority: node execution is the D0-S1
authorized op session (ops plan Part B §3 item 1, §5 timeline row D0-S1);
the pre-D0 dry-run is `plan` (listing/hashes only) and runs on the nodes
per the 2026-09-19 PI compute-location rule (no experiment of any size on
the MacBook).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

R2_BASE = "r2:ecophys"
DEFAULT_R2_PREFIX = "paper_d_archive"
PREREG_FREE_FLOOR = 0.40
CHUNK = 1024 * 1024

PLAN_SCHEMA = "d0-cleanup-plan-v2"
UPLOAD_RECEIPT_SCHEMA = "d0-cleanup-upload-receipt-v2"
DELETE_RECEIPT_SCHEMA = "d0-cleanup-delete-receipt-v2"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def sha256_stream(stream: Any) -> str:
    """Hash a byte stream chunk-by-chunk (never buffers the whole object)."""
    h = hashlib.sha256()
    while True:
        block = stream.read(CHUNK)
        if not block:
            break
        h.update(block)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Artifact:
    """One deletion-eligible unit resolved from a manifest."""

    manifest: str
    artifact_class: str  # triple_tarball | pair_tarball | bare_path
    rel_path: str
    pinned_hash: str | None  # from the manifest, when the manifest pins it
    size_bytes: int | None = None
    recorded_hash: str | None = None  # hash observed at plan time
    status: str = "unresolved"  # eligible | ineligible_*
    note: str = ""
    # For triple sets: every (digest, rel) line of the same-stem .sha256s,
    # used to verify the tarball's contents at plan time.
    manifest_entries: tuple[tuple[str, str], ...] | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "manifest": self.manifest,
            "artifact_class": self.artifact_class,
            "rel_path": self.rel_path,
            "pinned_hash": self.pinned_hash,
            "size_bytes": self.size_bytes,
            "recorded_hash": self.recorded_hash,
            "status": self.status,
            "note": self.note,
        }


def parse_sha_lines(text: str) -> list[tuple[str, str]]:
    """Parse `<sha256>  <path>` lines (sha256sum format, two-space or wider)."""
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if "  " not in line:
            raise ValueError(f"malformed sha256 manifest line: {line!r}")
        digest, path = line.split("  ", 1)
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"bad digest in manifest line: {line!r}")
        rows.append((digest, path))
    return rows


@dataclass
class Plan:
    root: Path
    deployment_dir: Path
    deployment_rel: str
    artifacts: list[Artifact] = field(default_factory=list)
    unmanifested: list[str] = field(default_factory=list)
    manifest_errors: list[dict[str, str]] = field(default_factory=list)
    manifest_files: list[str] = field(default_factory=list)
    policy_include_singular: bool = False


def safe_join(root: Path, rel: str) -> Path | None:
    """Resolve rel under root; refuse traversal, absolute paths, and any
    symlinked component (cold-data migration left symlinked directories on
    the nodes; deleting through one is the catastrophic case)."""
    parts = Path(rel).parts
    if rel.startswith("/") or not parts or "." in parts or ".." in parts:
        return None
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            return None
    return p


def path_has_symlink_component(p: Path) -> bool:
    """True if any component of an absolute path (final one included) is a
    symlink — used to refuse receipt roots that would delete through one."""
    cur = Path(p.root)
    for part in p.parts[1:]:
        cur = cur / part
        if cur.is_symlink():
            return True
    return False


def verify_tarball_contents(
    tar_path: Path, entries: tuple[tuple[str, str], ...]
) -> tuple[bool, str]:
    """Verify that every manifest line is covered by a tarball member with
    the pinned digest (streaming; nothing is extracted to disk)."""
    want = {rel: digest for digest, rel in entries}
    got: dict[str, str] = {}
    try:
        with tarfile.open(tar_path, "r:gz") as tf:
            for member in tf:
                if not member.isfile():
                    continue
                f = tf.extractfile(member)
                if f is None:
                    continue
                name = member.name[2:] if member.name.startswith("./") else member.name
                got[name] = sha256_stream(f)
    except (tarfile.TarError, OSError) as exc:
        return False, f"unreadable tarball: {exc}"
    missing = [rel for rel in want if rel not in got]
    bad = [rel for rel, d in want.items() if rel in got and got[rel] != d]
    ok = not missing and not bad
    note = (f"members={len(got)} manifest_lines={len(want)} "
            f"missing={len(missing)} mismatched={len(bad)}")
    return ok, note


def discover(plan: Plan) -> None:
    """Enumerate manifest sets and unmanifested tarballs in deployment_dir."""
    d = plan.deployment_dir
    names = sorted(p.name for p in d.iterdir())

    stems_sing = {n[: -len(".sha256")] for n in names
                  if n.endswith(".sha256") and not n.endswith(".sha256s")}
    stems_plur = {n[: -len(".sha256s")] for n in names if n.endswith(".sha256s")}
    tarballs = [n for n in names if n.endswith(".tar.gz")]

    def resolve_bare(rel: str) -> str:
        # Bare manifest names occur both as deployment-dir files (snapshot
        # tarballs, chunk parts) and as repo-root files (pyproject.toml);
        # pick the candidate that holds a regular file, preferring the
        # deployment dir when both do. The pinned digest still decides
        # eligibility downstream.
        in_dep = (d / rel).is_file()
        at_root = (plan.root / rel).is_file()
        if in_dep or not at_root:
            return f"{plan.deployment_rel}/{rel}"
        return rel

    def add_from_manifest(manifest: Path, stem: str) -> None:
        try:
            text = manifest.read_text()
            lines = parse_sha_lines(text)
        except (OSError, ValueError) as exc:
            plan.manifest_errors.append(
                {"manifest": manifest.name, "error": str(exc)})
            return
        plan.manifest_files.append(manifest.name)
        for digest, rel in lines:
            root_rel = rel if "/" in rel else resolve_bare(rel)
            plan.artifacts.append(
                Artifact(manifest=manifest.name, artifact_class="bare_path",
                         rel_path=root_rel, pinned_hash=digest))
        if manifest.name == f"{stem}.sha256s" and \
                (d / f"{stem}.files").is_file() and \
                (d / f"{stem}.tar.gz").is_file():
            plan.manifest_files.append(f"{stem}.files")
            plan.artifacts.append(
                Artifact(manifest=manifest.name, artifact_class="triple_tarball",
                         rel_path=f"{plan.deployment_rel}/{stem}.tar.gz",
                         pinned_hash=None, manifest_entries=tuple(lines)))

    for stem in sorted(stems_plur):
        add_from_manifest(d / f"{stem}.sha256s", stem)

    for stem in sorted(stems_sing):
        if not plan.policy_include_singular:
            continue
        manifest = d / f"{stem}.sha256"
        try:
            lines = parse_sha_lines(manifest.read_text())
        except (OSError, ValueError) as exc:
            plan.manifest_errors.append(
                {"manifest": manifest.name, "error": str(exc)})
            continue
        if len(lines) != 1:
            plan.manifest_errors.append(
                {"manifest": manifest.name,
                 "error": f"expected exactly one line, got {len(lines)}"})
            continue
        digest, rel = lines[0]
        root_rel = rel if "/" in rel else resolve_bare(rel)
        plan.manifest_files.append(manifest.name)
        plan.artifacts.append(
            Artifact(manifest=manifest.name, artifact_class="pair_tarball",
                     rel_path=root_rel, pinned_hash=digest))

    manifested_rels = {a.rel_path for a in plan.artifacts}
    plan.unmanifested = sorted(
        n for n in tarballs if f"{plan.deployment_rel}/{n}" not in manifested_rels)


def resolve(plan: Plan) -> None:
    """Re-hash every artifact; assign eligibility (fail-closed)."""
    for i, a in enumerate(plan.artifacts):
        p = safe_join(plan.root, a.rel_path)
        if p is None:
            plan.artifacts[i] = replace(
                a, status="ineligible_unsafe_path",
                note="symlinked component or outside --root")
            continue
        if not p.is_file():
            note = ("present but not a regular file" if p.exists()
                    else "not present at --root")
            plan.artifacts[i] = replace(
                a, status="ineligible_missing", note=note)
            continue
        size = p.stat().st_size
        recorded = sha256_file(p)
        if a.pinned_hash is not None and recorded != a.pinned_hash:
            plan.artifacts[i] = replace(
                a, size_bytes=size, recorded_hash=recorded,
                status="ineligible_mismatch",
                note="on-disk hash differs from manifest")
            continue
        if a.artifact_class == "triple_tarball" and a.manifest_entries is not None:
            ok, note = verify_tarball_contents(p, a.manifest_entries)
            if not ok:
                plan.artifacts[i] = replace(
                    a, size_bytes=size, recorded_hash=recorded,
                    status="ineligible_mismatch",
                    note=f"tarball contents fail manifest check: {note}")
                continue
        plan.artifacts[i] = replace(
            a, size_bytes=size, recorded_hash=recorded, status="eligible")


def dedup(plan: Plan) -> int:
    """Collapse duplicate rows: the real manifests pin shared repo files in
    up to 11 manifests each, and duplicate eligible rows would produce
    duplicate receipt entries that abort a delete mid-phase. Eligible rows
    dedup by rel_path (manifest provenance merged into the kept row);
    identical ineligible rows collapse too. Returns the merge count."""
    kept: list[Artifact] = []
    eligible_idx: dict[str, int] = {}
    seen_ineligible: set[tuple[str, str, str]] = set()
    merges = 0
    for a in plan.artifacts:
        if a.status == "eligible":
            idx = eligible_idx.get(a.rel_path)
            if idx is not None:
                kept[idx] = replace(
                    kept[idx], manifest=f"{kept[idx].manifest}+{a.manifest}")
                merges += 1
                continue
            eligible_idx[a.rel_path] = len(kept)
            kept.append(a)
        else:
            key = (a.rel_path, a.status, a.note)
            if key in seen_ineligible:
                merges += 1
                continue
            seen_ineligible.add(key)
            kept.append(a)
    plan.artifacts = kept
    return merges


def build_plan(root: Path, deployment_rel: str,
               include_singular_sha256: bool,
               r2_prefix: str = DEFAULT_R2_PREFIX) -> dict[str, Any]:
    plan = Plan(root=root, deployment_dir=root / deployment_rel,
                deployment_rel=deployment_rel,
                policy_include_singular=include_singular_sha256)
    if not plan.deployment_dir.is_dir():
        raise SystemExit(f"deployment dir not found: {plan.deployment_dir}")
    discover(plan)
    resolve(plan)
    merges = dedup(plan)
    rows = [a.to_row() for a in plan.artifacts]
    eligible = [r for r in rows if r["status"] == "eligible"]
    return {
        "schema": PLAN_SCHEMA,
        "root": str(root),
        "r2_prefix": r2_prefix,
        "deployment_dir": deployment_rel,
        "policy": {
            "include_singular_sha256": include_singular_sha256,
            "authority": ("*.files + *.sha256s + singular *.sha256 "
                          "(inclusive reading, opt-in; a singular .sha256 "
                          "pins the tarball hash directly)"
                          if include_singular_sha256 else
                          "*.files + *.sha256s only (ops plan Part B §3 "
                          "item 1 literal)"),
            "rule": "nothing without a manifest is deleted",
        },
        "artifacts": rows,
        "unmanifested_tarballs": plan.unmanifested,
        "manifest_errors": plan.manifest_errors,
        "manifest_files": sorted(set(plan.manifest_files)),
        "totals": {
            "artifacts": len(rows),
            "eligible": len(eligible),
            "eligible_bytes": sum(r["size_bytes"] or 0 for r in eligible),
            "ineligible": len(rows) - len(eligible),
            "duplicate_pins": merges,
            "unmanifested_tarballs": len(plan.unmanifested),
        },
    }


def r2_key(rel_path: str, prefix: str = DEFAULT_R2_PREFIX) -> str:
    # The per-copy prefix keeps identical rel_paths from different snapshot
    # roots off the same R2 object (a clobbered object would silently break
    # the earlier copy's upload receipt).
    return f"{R2_BASE}/{prefix}/{rel_path}"


def remote_hash(key: str) -> str:
    """Stream `rclone cat <key>` through the hasher (constant memory)."""
    proc = subprocess.Popen(["rclone", "cat", key], stdout=subprocess.PIPE)
    out = proc.stdout
    try:
        digest = sha256_stream(out)
    finally:
        if out is not None:
            out.close()
        rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"rclone cat failed (rc={rc}) for {key}")
    return digest


def run_upload(plan_path: Path) -> dict[str, Any]:
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    if plan.get("schema") != PLAN_SCHEMA:
        raise SystemExit("not a plan file")
    root = Path(plan["root"])
    rows = [r for r in plan["artifacts"] if r["status"] == "eligible"]
    prefix = plan.get("r2_prefix", DEFAULT_R2_PREFIX)
    uploads: list[dict[str, Any]] = []
    seen: set[str] = set()
    for r in rows:
        if r["rel_path"] in seen:
            raise SystemExit(
                f"duplicate eligible rel_path in plan: {r['rel_path']}")
        seen.add(r["rel_path"])
        local = safe_join(root, r["rel_path"])
        if local is None or not local.is_file():
            raise SystemExit(f"refusing unsafe or missing path: {r['rel_path']}")
        key = r2_key(r["rel_path"], prefix)
        subprocess.run(["rclone", "copyto", str(local), key], check=True)
        remote_digest = remote_hash(key)
        if remote_digest != r["recorded_hash"]:
            raise SystemExit(
                f"remote hash mismatch for {key}: {remote_digest} != "
                f"{r['recorded_hash']} — aborting before further uploads")
        uploads.append({"rel_path": r["rel_path"], "r2_key": key,
                        "size_bytes": r["size_bytes"],
                        "sha256": r["recorded_hash"],
                        "remote_verified_hash": remote_digest})
    # The manifests themselves are the destination-side provenance for the
    # archive ("relocate with manifest verification"): upload them too. They
    # are never deleted locally — they are the authority, not the payload.
    dep = safe_join(root, plan["deployment_dir"])
    if dep is None or not dep.is_dir():
        raise SystemExit("unsafe deployment dir in plan")
    manifests_uploaded: list[dict[str, Any]] = []
    for name in sorted(set(plan.get("manifest_files", []))):
        if "/" in name or name in {".", ".."}:
            raise SystemExit(f"refusing unsafe manifest name: {name!r}")
        src = dep / name
        if not src.is_file():
            raise SystemExit(f"manifest file missing at plan time: {name}")
        key = f"{R2_BASE}/{prefix}/manifests/{name}"
        subprocess.run(["rclone", "copyto", str(src), key], check=True)
        digest = remote_hash(key)
        if digest != sha256_file(src):
            raise SystemExit(f"manifest upload verify failed: {name}")
        manifests_uploaded.append(
            {"name": name, "r2_key": key, "sha256": digest})
    return {
        "schema": UPLOAD_RECEIPT_SCHEMA,
        "plan_sha256": sha256_bytes(plan_bytes),
        "root": plan["root"],
        "r2_prefix": prefix,
        "uploads": uploads,
        "manifests_uploaded": manifests_uploaded,
    }


def run_verify(plan_path: Path) -> list[dict[str, Any]]:
    plan = json.loads(plan_path.read_text())
    if plan.get("schema") != PLAN_SCHEMA:
        raise SystemExit("not a plan file")
    prefix = plan.get("r2_prefix", DEFAULT_R2_PREFIX)
    results: list[dict[str, Any]] = []
    for r in plan["artifacts"]:
        if r["status"] != "eligible":
            continue
        results.append({
            "rel_path": r["rel_path"],
            "ok": remote_hash(r2_key(r["rel_path"], prefix)) == r["recorded_hash"],
        })
    return results


def run_delete(receipt_path: Path, plan_path: Path,
               receipt_out: Path | None = None) -> dict[str, Any]:
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("schema") != UPLOAD_RECEIPT_SCHEMA:
        raise SystemExit("not an upload receipt")
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    if plan.get("schema") != PLAN_SCHEMA:
        raise SystemExit("not a plan file")
    if sha256_bytes(plan_bytes) != receipt.get("plan_sha256"):
        raise SystemExit("receipt does not bind this plan (plan_sha256 mismatch)")
    if receipt.get("root") != plan.get("root"):
        raise SystemExit("receipt root does not match plan root")
    root = Path(receipt["root"])
    if not root.is_absolute():
        raise SystemExit("receipt root must be absolute")
    if path_has_symlink_component(root):
        raise SystemExit("receipt root crosses a symlinked component")
    eligible = {r["rel_path"]: r for r in plan["artifacts"]
                if r["status"] == "eligible"}
    prefix = plan.get("r2_prefix", DEFAULT_R2_PREFIX)
    uploads = receipt.get("uploads", [])
    rels = [u["rel_path"] for u in uploads]
    if len(set(rels)) != len(rels):
        raise SystemExit("duplicate rel_path entries in receipt — refusing")

    # Pass 1: validate every entry before the first unlink.
    targets: list[tuple[Path, dict[str, Any]]] = []
    for u in uploads:
        row = eligible.get(u["rel_path"])
        if row is None:
            raise SystemExit(
                f"receipt entry not an eligible plan row: {u['rel_path']}")
        if u.get("sha256") != row.get("recorded_hash"):
            raise SystemExit(
                f"receipt hash disagrees with plan row: {u['rel_path']}")
        if u.get("r2_key") != r2_key(u["rel_path"], prefix):
            raise SystemExit(
                f"receipt r2_key disagrees with plan: {u['rel_path']}")
        p = safe_join(root, u["rel_path"])
        if p is None or not p.is_file():
            raise SystemExit(f"refusing unsafe or missing path: {u['rel_path']}")
        if sha256_file(p) != u["sha256"]:
            raise SystemExit(
                f"local file changed since upload: {u['rel_path']} — aborting")
        targets.append((p, u))

    def write(deleted: list[str], remote_ok: bool | None,
              complete: bool) -> None:
        if receipt_out is None:
            return
        receipt_out.write_text(json.dumps({
            "schema": DELETE_RECEIPT_SCHEMA,
            "upload_receipt_sha256": sha256_bytes(receipt_path.read_bytes()),
            "deleted": deleted,
            "reverify_all_absent": all(
                not (root / rel).exists() for rel in deleted),
            "reverify_remote_all_ok": remote_ok,
            "complete": complete,
        }, indent=2, sort_keys=True) + "\n")

    # Pass 2: unlink, rewriting the (incomplete) receipt after each removal
    # so an abort never leaves deletions unrecorded.
    deleted: list[str] = []
    write(deleted, None, False)
    for p, u in targets:
        p.unlink()
        if p.exists():
            raise SystemExit(f"delete did not remove file: {p}")
        deleted.append(u["rel_path"])
        write(deleted, None, False)

    # Pass 3: re-verify the archived bytes (local bytes are gone; the remote
    # copies are what "re-verify" can still check).
    remote_ok = all(remote_hash(u["r2_key"]) == u["sha256"] for u in uploads)
    if not remote_ok:
        write(deleted, False, False)
        raise SystemExit("post-delete remote re-verify failed")
    doc = {
        "schema": DELETE_RECEIPT_SCHEMA,
        "upload_receipt_sha256": sha256_bytes(receipt_path.read_bytes()),
        "deleted": deleted,
        "reverify_all_absent": all(
            not (root / rel).exists() for rel in deleted),
        "reverify_remote_all_ok": True,
        "complete": True,
    }
    write(deleted, True, True)
    return doc


def run_check_free(path: Path, threshold: float) -> int:
    if threshold < PREREG_FREE_FLOOR:
        raise SystemExit(
            f"refusing threshold {threshold} below the prereg §8.3 floor "
            f"{PREREG_FREE_FLOOR} (STOP-class gate is not ad-hoc descopable)")
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    frac = free / total if total else 0.0
    print(json.dumps({
        "path": str(path), "free_bytes": free, "total_bytes": total,
        "free_fraction": round(frac, 4), "threshold": threshold,
        "prereg_floor": PREREG_FREE_FLOOR,
        "passes": frac >= threshold,
    }, indent=2))
    return 0 if frac >= threshold else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="dry-run: listing/hashes only")
    p_plan.add_argument("--root", required=True, type=Path)
    p_plan.add_argument("--deployment-dir", default=(
        "experiments/constraint_attribution_iclr/deployment"))
    p_plan.add_argument("--include-singular-sha256", action="store_true",
                        help="grant manifest authority to singular *.sha256 "
                             "pair sets (default: ops-literal *.files + "
                             "*.sha256s only)")
    p_plan.add_argument("--r2-prefix", default=DEFAULT_R2_PREFIX)
    p_plan.add_argument("--out", type=Path)

    p_up = sub.add_parser("upload", help="rclone upload + stream re-hash")
    p_up.add_argument("--plan", required=True, type=Path)
    p_up.add_argument("--receipt-out", type=Path)
    p_up.add_argument("--yes", action="store_true")

    p_ver = sub.add_parser("verify", help="re-check remote bytes (no mutation)")
    p_ver.add_argument("--plan", required=True, type=Path)

    p_del = sub.add_parser("delete", help="delete receipted local artifacts")
    p_del.add_argument("--upload-receipt", required=True, type=Path)
    p_del.add_argument("--plan", required=True, type=Path,
                       help="the plan this receipt was issued against")
    p_del.add_argument("--receipt-out", type=Path)
    p_del.add_argument("--yes", action="store_true")

    p_free = sub.add_parser("check-free", help="statvfs >= threshold gate")
    p_free.add_argument("--path", required=True, type=Path)
    p_free.add_argument("--threshold", type=float, default=PREREG_FREE_FLOOR)

    args = ap.parse_args(argv)

    if args.cmd == "plan":
        result = build_plan(args.root.resolve(), args.deployment_dir,
                            args.include_singular_sha256, args.r2_prefix)
        text = json.dumps(result, indent=2, sort_keys=True)
        if args.out:
            args.out.write_text(text + "\n")
            print(f"wrote {args.out} "
                  f"(eligible {result['totals']['eligible']} / "
                  f"{result['totals']['artifacts']}, "
                  f"duplicate_pins {result['totals']['duplicate_pins']})")
        else:
            print(text)
        return 0

    if args.cmd == "upload":
        if not args.yes:
            raise SystemExit("upload mutates remote state: pass --yes")
        if shutil.which("rclone") is None:
            raise SystemExit("rclone not found")
        receipt = run_upload(args.plan)
        text = json.dumps(receipt, indent=2, sort_keys=True)
        if args.receipt_out:
            args.receipt_out.write_text(text + "\n")
            print(f"wrote {args.receipt_out} "
                  f"({len(receipt['uploads'])} uploads, "
                  f"{len(receipt['manifests_uploaded'])} manifests)")
        else:
            print(text)
        return 0

    if args.cmd == "verify":
        results = run_verify(args.plan)
        print(json.dumps(results, indent=2))
        if not results:
            print("no eligible rows in plan — nothing verified", file=sys.stderr)
            return 1
        return 0 if all(r["ok"] for r in results) else 1

    if args.cmd == "delete":
        if not args.yes:
            raise SystemExit("delete is destructive: pass --yes")
        if shutil.which("rclone") is None:
            raise SystemExit("rclone not found")
        receipt = run_delete(args.upload_receipt, args.plan, args.receipt_out)
        if not (receipt["reverify_all_absent"]
                and receipt["reverify_remote_all_ok"]):
            raise SystemExit("post-delete re-verify failed")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0

    if args.cmd == "check-free":
        return run_check_free(args.path, args.threshold)

    return 2


if __name__ == "__main__":
    sys.exit(main())
