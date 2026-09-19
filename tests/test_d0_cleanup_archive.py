"""Unit tests for scripts/d0_cleanup_archive.py (pure logic, tmp fixtures).

Covers the manifest grammar (including bare-name resolution and CRLF/digest
edge cases), the fail-closed path rules (traversal, symlinked components,
upload-side safe_join), eligibility (eligible / mismatch / missing / unsafe /
unmanifested), triple-set tarball content verification, duplicate-pin dedup,
the strict-default policy switch, manifest-error capture, the plan-bound
two-pass delete gate with remote re-verify, upload receipts incl. manifest
upload, the vacuous-verify refusal, the check-free floor, and the main()
--yes gates. rclone is monkeypatched throughout; no network.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import d0_cleanup_archive as dca

DEP = "experiments/constraint_attribution_iclr/deployment"


def _write(root: Path, rel: str, data: bytes | str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode())
    return p


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tar_bytes(members: list[tuple[str, bytes]]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for name, data in members:
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


def _make_deployment(root: Path) -> None:
    """One triple set (real gzip tarball with manifested contents), one pair,
    one bare .sha256s over an outside path, one unmanifested tarball."""
    d = root / DEP
    d.mkdir(parents=True, exist_ok=True)
    src = _write(root, "scripts/thing.py", b"print('x')\n")
    _write(d, "snap.files", "scripts/thing.py\n")
    _write(d, "snap.sha256s", f"{_sha(src.read_bytes())}  scripts/thing.py\n")
    _write(d, "snap.tar.gz", _tar_bytes([("scripts/thing.py", b"print('x')\n")]))
    # Pair: singular .sha256 pins the tarball hash directly (opt-in policy).
    _write(d, "pair.tar.gz", b"tarball-bytes-pair")
    _write(d, "pair.sha256", f"{_sha(b'tarball-bytes-pair')}  pair.tar.gz\n")
    # Bare .sha256s over an outside path.
    other = _write(root, "outputs/chunk00", b"chunk")
    _write(d, "bare.sha256s", f"{_sha(other.read_bytes())}  outputs/chunk00\n")
    # Unmanifested tarball: must be reported, never eligible.
    _write(d, "lonely.tar.gz", b"never-delete-me")


def _plan_file(tmp_path: Path, include_singular: bool = False) -> Path:
    plan = dca.build_plan(tmp_path, DEP, include_singular)
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan, indent=2, sort_keys=True))
    return p


def _plan_rows(plan_path: Path) -> dict[str, dict]:
    plan = json.loads(plan_path.read_text())
    return {r["rel_path"]: r for r in plan["artifacts"]}


def _entry_for(plan_path: Path, rel: str) -> dict:
    row = _plan_rows(plan_path)[rel]
    prefix = json.loads(plan_path.read_text()).get(
        "r2_prefix", dca.DEFAULT_R2_PREFIX)
    return {"rel_path": rel, "r2_key": dca.r2_key(rel, prefix),
            "size_bytes": row["size_bytes"], "sha256": row["recorded_hash"],
            "remote_verified_hash": row["recorded_hash"]}


def _receipt_file(tmp_path: Path, plan_path: Path,
                  uploads: list[dict]) -> Path:
    plan = json.loads(plan_path.read_text())
    r = {
        "schema": dca.UPLOAD_RECEIPT_SCHEMA,
        "plan_sha256": dca.sha256_bytes(plan_path.read_bytes()),
        "root": plan["root"],
        "r2_prefix": plan.get("r2_prefix", dca.DEFAULT_R2_PREFIX),
        "uploads": uploads,
        "manifests_uploaded": [],
    }
    p = tmp_path / "receipt.json"
    p.write_text(json.dumps(r))
    return p


def _fake_remote_hash(tmp_path: Path, digest_map: dict[str, str]):
    def fake(key: str) -> str:
        return digest_map[key]
    return fake


# --- manifest parsing -------------------------------------------------------

def test_parse_sha_lines_edge_cases() -> None:
    assert dca.parse_sha_lines(
        f"{_sha(b'a')}  path/a\r\n\n{dca.sha256_bytes(b'')}  path/b\r\n"
    ) == [(_sha(b"a"), "path/a"), (dca.sha256_bytes(b""), "path/b")]
    for bad in ["nopespace path", "z" * 64 + "  path",
                "A" * 64 + "  path",  # uppercase hex rejected
                "a" * 63 + "  path"]:  # wrong length
        with pytest.raises(ValueError):
            dca.parse_sha_lines(bad)


# --- plan: classes, policy, unmanifested ------------------------------------

def test_plan_default_policy_is_strict_literal(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=False)
    rows = {r["rel_path"]: r for r in plan["artifacts"]}
    assert rows[f"{DEP}/snap.tar.gz"]["artifact_class"] == "triple_tarball"
    assert rows[f"{DEP}/snap.tar.gz"]["status"] == "eligible"
    assert "scripts/thing.py" in rows and rows["scripts/thing.py"]["status"] == "eligible"
    assert "outputs/chunk00" in rows and rows["outputs/chunk00"]["status"] == "eligible"
    # Singular .sha256 pairs are outside the frozen enumeration by default.
    assert f"{DEP}/pair.tar.gz" not in rows
    assert plan["unmanifested_tarballs"] == ["lonely.tar.gz", "pair.tar.gz"]
    assert plan["policy"]["include_singular_sha256"] is False
    assert plan["totals"]["eligible"] == 3


def test_plan_include_singular_sha256_promotes_pair(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=True)
    rows = {r["rel_path"]: r for r in plan["artifacts"]}
    assert rows[f"{DEP}/pair.tar.gz"]["artifact_class"] == "pair_tarball"
    assert rows[f"{DEP}/pair.tar.gz"]["status"] == "eligible"
    assert plan["unmanifested_tarballs"] == ["lonely.tar.gz"]
    assert plan["totals"]["eligible"] == 4


def test_pair_hash_mismatch_is_ineligible(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    (tmp_path / DEP / "pair.tar.gz").write_bytes(b"tampered")
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=True)
    row = next(r for r in plan["artifacts"] if r["rel_path"] == f"{DEP}/pair.tar.gz")
    assert row["status"] == "ineligible_mismatch"


def test_triple_tarball_content_verification(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    d = tmp_path / DEP
    # Tampered member bytes: manifest pins thing.py, tarball carries others.
    (d / "snap.tar.gz").write_bytes(
        _tar_bytes([("scripts/thing.py", b"print('tampered')\n")]))
    rows = _plan_rows(_plan_file(tmp_path))
    assert rows[f"{DEP}/snap.tar.gz"]["status"] == "ineligible_mismatch"
    assert "contents fail manifest check" in rows[f"{DEP}/snap.tar.gz"]["note"]
    # Missing member entirely.
    (d / "snap.tar.gz").write_bytes(_tar_bytes([("other.bin", b"zz")]))
    rows = _plan_rows(_plan_file(tmp_path))
    assert rows[f"{DEP}/snap.tar.gz"]["status"] == "ineligible_mismatch"
    # Intact tarball is eligible (also covered by the default-policy test).
    _make_deployment(tmp_path)
    rows = _plan_rows(_plan_file(tmp_path))
    assert rows[f"{DEP}/snap.tar.gz"]["status"] == "eligible"


def test_triple_demoted_when_files_half_missing(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    (tmp_path / DEP / "snap.files").unlink()
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=False)
    rels = {r["rel_path"] for r in plan["artifacts"]}
    assert f"{DEP}/snap.tar.gz" not in rels  # no triple row without .files
    assert "snap.tar.gz" in plan["unmanifested_tarballs"]
    # Sources from the same .sha256s stay eligible.
    assert any(r["rel_path"] == "scripts/thing.py"
               and r["status"] == "eligible" for r in plan["artifacts"])


def test_missing_artifact_is_ineligible_missing(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    (tmp_path / "outputs/chunk00").unlink()
    rows = _plan_rows(_plan_file(tmp_path))
    assert rows["outputs/chunk00"]["status"] == "ineligible_missing"
    assert rows["outputs/chunk00"]["note"] == "not present at --root"


def test_directory_at_manifest_path_gets_honest_note(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    d = tmp_path / DEP
    (d / "somedir").mkdir()
    digest = _sha(b"unused")
    (d / "dirline.sha256s").write_text(f"{digest}  somedir\n")
    rows = _plan_rows(_plan_file(tmp_path))
    row = rows[f"{DEP}/somedir"]
    assert row["status"] == "ineligible_missing"
    assert row["note"] == "present but not a regular file"


def test_bare_root_relative_name_resolves_to_repo_root(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    py = _write(tmp_path, "pyproject.toml", b"[project]\n")
    (tmp_path / DEP / "rootrel.sha256s").write_text(
        f"{_sha(py.read_bytes())}  pyproject.toml\n")
    rows = _plan_rows(_plan_file(tmp_path))
    assert rows["pyproject.toml"]["status"] == "eligible"
    assert f"{DEP}/pyproject.toml" not in rows


def test_unsafe_manifest_rows_are_ineligible(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    digest = _sha(b"unused")
    (tmp_path / DEP / "evil.sha256s").write_text(
        f"{digest}  ../escape.py\n"
        f"{digest}  a/../../escape.py\n")
    rows = _plan_rows(_plan_file(tmp_path))
    assert rows["../escape.py"]["status"] == "ineligible_unsafe_path"
    assert rows["a/../../escape.py"]["status"] == "ineligible_unsafe_path"


def test_unmanifested_collision_by_full_rel_path(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    lon = _write(tmp_path, "archive/lonely.tar.gz", b"elsewhere")
    (tmp_path / DEP / "far.sha256s").write_text(
        f"{_sha(lon.read_bytes())}  archive/lonely.tar.gz\n")
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=False)
    # The deployment-dir lonely.tar.gz is a different file: it must still be
    # reported unmanifested (basename collision must not hide it).
    assert "lonely.tar.gz" in plan["unmanifested_tarballs"]


def test_duplicate_pins_dedup_to_one_eligible_row(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    src = (tmp_path / "scripts/thing.py").read_bytes()
    (tmp_path / DEP / "snap2.sha256s").write_text(
        f"{_sha(src)}  scripts/thing.py\n")
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=False)
    thing_rows = [r for r in plan["artifacts"]
                  if r["rel_path"] == "scripts/thing.py"]
    assert len(thing_rows) == 1
    assert "+" in thing_rows[0]["manifest"]  # provenance merged
    assert plan["totals"]["eligible"] == 3
    assert plan["totals"]["duplicate_pins"] == 1


def test_manifest_files_listed_for_upload(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=False)
    assert set(plan["manifest_files"]) == {
        "snap.sha256s", "snap.files", "bare.sha256s"}


def test_safe_join_refusals(tmp_path: Path) -> None:
    assert dca.safe_join(tmp_path, "../escape") is None
    assert dca.safe_join(tmp_path, "/abs") is None
    assert dca.safe_join(tmp_path, ".") is None
    _write(tmp_path, "real.txt", b"x")
    assert dca.safe_join(tmp_path, "real.txt") == tmp_path / "real.txt"
    (tmp_path / "link").symlink_to(tmp_path / "real.txt")
    assert dca.safe_join(tmp_path, "link") is None  # symlinked file
    outside = tmp_path.parent / "outside_dca_test"
    outside.mkdir(exist_ok=True)
    (tmp_path / "dirlink").symlink_to(outside)
    assert dca.safe_join(tmp_path, "dirlink/file") is None  # symlinked dir


def test_path_has_symlink_component(tmp_path: Path) -> None:
    assert dca.path_has_symlink_component(tmp_path) is False
    outside = tmp_path.parent / "outside_dca_test2"
    outside.mkdir(exist_ok=True)
    mid = tmp_path / "sym_mid"
    mid.symlink_to(outside)
    assert dca.path_has_symlink_component(mid / "f") is True
    assert dca.path_has_symlink_component(mid) is True  # final component too


def test_malformed_manifest_captured_not_fatal(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    (tmp_path / DEP / "bad.sha256s").write_text("not-a-manifest-line\n")
    plan = dca.build_plan(tmp_path, DEP, include_singular_sha256=False)
    assert any(e["manifest"] == "bad.sha256s" for e in plan["manifest_errors"])


# --- upload -----------------------------------------------------------------

def test_upload_schema_gate(tmp_path: Path) -> None:
    # A receipt JSON is not a plan: controlled refusal, not a KeyError.
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    receipt_path = _receipt_file(tmp_path, plan_path, [])
    with pytest.raises(SystemExit):
        dca.run_upload(receipt_path)


def test_upload_refuses_unsafe_plan_paths(tmp_path: Path,
                                          monkeypatch: pytest.MonkeyPatch) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    plan = json.loads(plan_path.read_text())
    for r in plan["artifacts"]:
        if r["status"] == "eligible":
            r["rel_path"] = "../escape.txt"
    plan_path.write_text(json.dumps(plan))

    def boom(*a: object, **k: object) -> None:
        raise AssertionError("rclone must not run for an unsafe plan")

    monkeypatch.setattr(dca.subprocess, "run", boom)
    monkeypatch.setattr(dca, "remote_hash", boom)
    with pytest.raises(SystemExit):
        dca.run_upload(plan_path)


def test_upload_uploads_and_verifies_manifests(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)

    def fake_remote_hash(key: str) -> str:
        assert key.startswith("r2:ecophys/")
        tail = key[len("r2:ecophys/"):]
        tail = tail.split("/", 1)[1]  # strip r2 prefix
        if tail.startswith("manifests/"):
            return dca.sha256_file(tmp_path / DEP / tail[len("manifests/"):])
        return dca.sha256_file(tmp_path / tail)

    calls: list[list[str]] = []

    def fake_run(cmd: list[str], check: bool = True) -> None:
        calls.append(cmd)

    monkeypatch.setattr(dca.subprocess, "run", fake_run)
    monkeypatch.setattr(dca, "remote_hash", fake_remote_hash)
    receipt = dca.run_upload(plan_path)
    assert len(receipt["uploads"]) == 3
    assert {m["name"] for m in receipt["manifests_uploaded"]} == {
        "snap.sha256s", "snap.files", "bare.sha256s"}
    copyto = [c for c in calls if c[1] == "copyto"]
    assert len(copyto) == 3 + 3  # artifacts + manifests


# --- verify -----------------------------------------------------------------

def test_verify_schema_gate(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    receipt_path = _receipt_file(tmp_path, plan_path, [])
    with pytest.raises(SystemExit):
        dca.run_verify(receipt_path)


def test_verify_empty_eligible_set_is_not_vacuous_green(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    plan = json.loads(plan_path.read_text())
    for r in plan["artifacts"]:
        r["status"] = "ineligible_missing"
    plan_path.write_text(json.dumps(plan))
    monkeypatch.setattr(
        dca, "remote_hash",
        lambda key: (_ for _ in ()).throw(AssertionError("no rclone expected")))
    assert dca.main(["verify", "--plan", str(plan_path)]) == 1


# --- delete -----------------------------------------------------------------

def test_delete_gate_reverify_and_second_run_refusal(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    rel = f"{DEP}/snap.tar.gz"
    entry = _entry_for(plan_path, rel)
    receipt_path = _receipt_file(tmp_path, plan_path, [entry])
    monkeypatch.setattr(dca, "remote_hash",
                        _fake_remote_hash(tmp_path, {entry["r2_key"]: entry["sha256"]}))
    out = dca.run_delete(receipt_path, plan_path)
    assert out["complete"] is True
    assert out["reverify_all_absent"] is True
    assert out["reverify_remote_all_ok"] is True
    assert out["deleted"] == [rel]
    # Second run: file already gone -> refuse in pass 1 (fail-closed).
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path)


def test_delete_aborts_on_changed_local_file_before_any_unlink(
        tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    rel = f"{DEP}/snap.tar.gz"
    entry = _entry_for(plan_path, rel)
    (tmp_path / DEP / "snap.tar.gz").write_bytes(b"changed on disk")
    receipt_path = _receipt_file(tmp_path, plan_path, [entry])
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path)
    assert (tmp_path / DEP / "snap.tar.gz").exists()  # nothing removed


def test_delete_rejects_receipt_not_bound_to_plan(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    rel = f"{DEP}/snap.tar.gz"
    entry = _entry_for(plan_path, rel)
    receipt_path = _receipt_file(tmp_path, plan_path, [entry])
    r = json.loads(receipt_path.read_text())
    r["plan_sha256"] = "0" * 64  # forged binding
    receipt_path.write_text(json.dumps(r))
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path)
    assert (tmp_path / DEP / "snap.tar.gz").exists()


def test_delete_rejects_entry_outside_plan_eligible_set(
        tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    rogue = {"rel_path": "outputs/never-planned.bin",
             "r2_key": "r2:ecophys/paper_d_archive/outputs/never-planned.bin",
             "size_bytes": 1, "sha256": "0" * 64,
             "remote_verified_hash": "0" * 64}
    receipt_path = _receipt_file(tmp_path, plan_path, [rogue])
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path)


def test_delete_rejects_duplicate_entries_before_any_unlink(
        tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    rel = f"{DEP}/snap.tar.gz"
    entry = _entry_for(plan_path, rel)
    receipt_path = _receipt_file(tmp_path, plan_path, [entry, dict(entry)])
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path)
    assert (tmp_path / DEP / "snap.tar.gz").exists()


def test_delete_rejects_unsafe_rel_path(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    evil = {"rel_path": "../outside.py",
            "r2_key": "r2:ecophys/paper_d_archive/../outside.py",
            "size_bytes": 1, "sha256": "0" * 64,
            "remote_verified_hash": "0" * 64}
    receipt_path = _receipt_file(tmp_path, plan_path, [evil])
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path)


def test_delete_remote_reverify_failure_leaves_incomplete_receipt(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    e1 = _entry_for(plan_path, f"{DEP}/snap.tar.gz")
    e2 = _entry_for(plan_path, "scripts/thing.py")
    receipt_path = _receipt_file(tmp_path, plan_path, [e1, e2])
    receipt_out = tmp_path / "delete_receipt.json"
    monkeypatch.setattr(dca, "remote_hash",
                        lambda key: "0" * 64)  # archive bytes "gone"
    with pytest.raises(SystemExit):
        dca.run_delete(receipt_path, plan_path, receipt_out)
    doc = json.loads(receipt_out.read_text())
    assert doc["complete"] is False
    assert doc["deleted"] == [e1["rel_path"], e2["rel_path"]]
    assert doc["reverify_remote_all_ok"] is False
    assert not (tmp_path / DEP / "snap.tar.gz").exists()  # deletions happened
    assert not (tmp_path / "scripts/thing.py").exists()


# --- check-free (prereg §8.3 gate) -------------------------------------------

def _statvfs_frac(frac: float) -> SimpleNamespace:
    total = 1000
    return SimpleNamespace(f_bavail=int(total * frac), f_frsize=1,
                           f_blocks=total)


def test_check_free_boundary_and_floor(tmp_path: Path,
                                       monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dca.os, "statvfs", lambda p: _statvfs_frac(0.40))
    assert dca.run_check_free(tmp_path, 0.40) == 0  # inclusive boundary
    monkeypatch.setattr(dca.os, "statvfs", lambda p: _statvfs_frac(0.3999))
    assert dca.run_check_free(tmp_path, 0.40) == 1
    with pytest.raises(SystemExit):  # below prereg floor refused outright
        dca.run_check_free(tmp_path, 0.30)
    monkeypatch.setattr(
        dca.os, "statvfs",
        lambda p: SimpleNamespace(f_bavail=0, f_frsize=1, f_blocks=0))
    assert dca.run_check_free(tmp_path, 0.40) == 1  # total==0 fails closed


# --- main() authorization gates ----------------------------------------------

def test_main_yes_gates(tmp_path: Path) -> None:
    _make_deployment(tmp_path)
    plan_path = _plan_file(tmp_path)
    receipt_path = _receipt_file(tmp_path, plan_path, [])
    for argv in (["upload", "--plan", str(plan_path)],
                 ["delete", "--upload-receipt", str(receipt_path),
                  "--plan", str(plan_path)]):
        with pytest.raises(SystemExit):
            dca.main(argv)
