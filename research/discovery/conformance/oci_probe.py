#!/usr/bin/env python3
from __future__ import annotations

import errno
import hashlib
import io
import json
import os
import socket
import sys
import tarfile
import time
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def write_is_blocked(path: Path) -> bool:
    try:
        with path.open("ab") as handle:
            handle.write(b"x")
    except OSError as exc:
        return exc.errno in {errno.EACCES, errno.EROFS}
    return False


def proc_status() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in read_text(Path("/proc/self/status")).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key] = value.strip()
    return values


def tmp_mount_options() -> set[str]:
    for line in read_text(Path("/proc/mounts")).splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[1] == "/tmp":
            return set(fields[3].split(","))
    return set()


def cpu_is_one_core() -> bool:
    quota, period = read_text(Path("/sys/fs/cgroup/cpu.max")).split()
    return quota != "max" and int(quota) == int(period)


def emit_tar(report: dict[str, Any]) -> None:
    payload = json.dumps(
        report,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8") + b"\n"
    info = tarfile.TarInfo("conformance.json")
    info.size = len(payload)
    info.mode = 0o444
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as archive:
        archive.addfile(info, io.BytesIO(payload))


def main() -> int:
    config_path = Path(os.environ.get("ECOMD_DX_CONFIG", ""))
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    mode = config.get("mode", "normal")
    if mode == "sleep":
        time.sleep(30)
        return 0
    if mode == "invalid_tar":
        sys.stdout.buffer.write(b"not-a-tar\n")
        return 0

    root_probe = Path("/ecomd-dx-root-write-probe")
    config_write_blocked = write_is_blocked(config_path)
    root_write_blocked = write_is_blocked(root_probe)
    status = proc_status()
    mount_options = tmp_mount_options()
    sandbox_members = sorted(path.name for path in Path("/sandbox").iterdir())
    interfaces = sorted(name for _, name in socket.if_nameindex())
    secret_prefixes = (
        "ANTHROPIC_",
        "AWS_",
        "AZURE_",
        "CLOUDFLARE_",
        "GH_",
        "GITHUB_",
        "GOOGLE_",
        "HF_",
        "HUGGINGFACE_",
        "OPENAI_",
        "R2_",
        "WANDB_",
    )
    exposed_secret_names = sorted(
        name
        for name in os.environ
        if name.upper().startswith(secret_prefixes)
        or "SECRET" in name.upper()
        or "TOKEN" in name.upper()
    )
    checks = {
        "config_is_read_only": config_write_blocked,
        "cpu_quota_is_one_core": cpu_is_one_core(),
        "effective_capabilities_are_empty": status.get("CapEff") == "0000000000000000",
        "gpu_devices_are_absent": not list(Path("/dev").glob("nvidia*")),
        "memory_limit_is_2gib": read_text(Path("/sys/fs/cgroup/memory.max"))
        == "2147483648",
        "network_namespace_has_only_loopback": interfaces == ["lo"],
        "no_new_privileges_is_set": status.get("NoNewPrivs") == "1",
        "no_secret_named_environment_variables": exposed_secret_names == [],
        "pids_limit_is_128": read_text(Path("/sys/fs/cgroup/pids.max")) == "128",
        "repository_tree_is_absent": sandbox_members == ["config.yaml"],
        "root_filesystem_is_read_only": root_write_blocked and not root_probe.exists(),
        "seccomp_filter_is_active": status.get("Seccomp") == "2",
        "tmp_is_restricted_and_writable": {
            "rw",
            "nodev",
            "noexec",
            "nosuid",
        }.issubset(mount_options)
        and os.access("/tmp", os.W_OK),
        "uid_gid_are_nobody": os.getuid() == 65534 and os.getgid() == 65534,
    }
    report: dict[str, Any] = {
        "schema_version": 1,
        "probe": "ecomd_discovery_oci_runtime",
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
            "interfaces": interfaces,
            "sandbox_members": sandbox_members,
            "tmp_mount_options": sorted(mount_options),
        },
    }
    emit_tar(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
