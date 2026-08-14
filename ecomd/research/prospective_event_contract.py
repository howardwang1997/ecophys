"""Validation and documentation-only probing for prospective event contracts."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

import requests
import yaml

SCHEMA_VERSION = "ecophys-prospective-event-contract/v1"
STAGE = "metadata_only"
GATE_STATUSES = frozenset({"pass", "unresolved", "fail"})
INTERFACE_ROLES = frozenset({"action", "identity", "mechanism", "outcome", "state"})
REQUIRED_GATES = frozenset(
    {
        "action_schema",
        "clock",
        "eligible_population",
        "identity_history",
        "independent_replication",
        "licence",
        "mechanism_boundary",
        "null_failure_capture",
        "response_freeze",
        "revision_history",
    }
)
TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "event_id",
        "as_of",
        "stage",
        "access_boundary",
        "event",
        "sources",
        "interfaces",
        "gates",
        "response_draft",
        "next_actions",
    }
)
ACCESS_FLAGS = frozenset(
    {
        "target_rows_opened",
        "pilot_rows_opened",
        "external_workers_used",
        "paid_data_used",
        "documentation_examples_visible",
    }
)
SAFE_DOCUMENTATION_PATHS: Mapping[str, tuple[str, ...]] = {
    "bmrs.elexon.co.uk": ("/api-documentation/",),
    "bscdocs.elexon.co.uk": ("/bsc-procedures/", "/interface-definition-documents/"),
    "developer.data.elexon.co.uk": ("/",),
    "www.elexon.co.uk": ("/bsc/",),
    "www.neso.energy": ("/document/", "/industry-information/", "/news/"),
}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


@dataclass(frozen=True)
class DocumentationProbe:
    """Content-free provenance result for one allowlisted documentation page."""

    source_id: str
    url: str
    status_code: int
    content_type: str
    byte_count: int
    sha256: str
    missing_markers: tuple[str, ...]
    retrieval_error: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a YAML-safe representation without retaining page content."""

        return {
            "source_id": self.source_id,
            "url": self.url,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "byte_count": self.byte_count,
            "sha256": self.sha256,
            "missing_markers": list(self.missing_markers),
            "retrieval_error": self.retrieval_error,
        }


def load_event_contract(path: str | Path) -> dict[str, object]:
    """Load a YAML event contract at an object-typed validation boundary."""

    raw: object = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("event contract root must be a mapping")
    return cast(dict[str, object], raw)


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _mapping_list(value: object) -> list[Mapping[str, object]] | None:
    if not isinstance(value, list):
        return None
    result: list[Mapping[str, object]] = []
    for item in value:
        mapped = _mapping(item)
        if mapped is None:
            return None
        result.append(mapped)
    return result


def _string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_list(value: object, *, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or any(_string(item) is None for item in value):
        errors.append(f"{path} must be a non-empty list of strings")
        return []
    return [cast(str, item).strip() for item in value]


def documentation_url_error(url: str) -> str | None:
    """Return why a URL is unsafe for the metadata-only probe, if applicable."""

    parsed = urlparse(url)
    if parsed.scheme != "https":
        return "URL must use https"
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        return "URL cannot contain query, fragment, or credentials"
    prefixes = SAFE_DOCUMENTATION_PATHS.get(parsed.hostname or "")
    if prefixes is None:
        return f"host is not allowlisted: {parsed.hostname}"
    if not any(parsed.path.startswith(prefix) for prefix in prefixes):
        return f"path is not an allowlisted documentation path: {parsed.path}"
    return None


def validate_event_contract(contract: Mapping[str, object]) -> list[str]:
    """Return deterministic structural and no-outcome-access violations."""

    errors: list[str] = []
    unknown_top = sorted(set(contract) - TOP_LEVEL_KEYS)
    missing_top = sorted(TOP_LEVEL_KEYS - set(contract))
    if unknown_top:
        errors.append(f"unknown top-level keys: {unknown_top}")
    if missing_top:
        errors.append(f"missing top-level keys: {missing_top}")
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must equal {SCHEMA_VERSION}")
    event_id = _string(contract.get("event_id"))
    if event_id is None or ID_PATTERN.fullmatch(event_id) is None:
        errors.append("event_id must be a lowercase stable identifier")
    as_of = _string(contract.get("as_of"))
    if as_of is None or DATE_PATTERN.fullmatch(as_of) is None:
        errors.append("as_of must be an ISO date")
    if contract.get("stage") != STAGE:
        errors.append(f"stage must equal {STAGE}")

    boundary = _mapping(contract.get("access_boundary"))
    if boundary is None or set(boundary) != ACCESS_FLAGS:
        errors.append(f"access_boundary must contain exactly {sorted(ACCESS_FLAGS)}")
        boundary = {}
    for flag in ("target_rows_opened", "pilot_rows_opened", "external_workers_used", "paid_data_used"):
        if boundary.get(flag) is not False:
            errors.append(f"access_boundary.{flag} must be false")
    if not isinstance(boundary.get("documentation_examples_visible"), bool):
        errors.append("access_boundary.documentation_examples_visible must be boolean")

    event = _mapping(contract.get("event"))
    if event is None:
        errors.append("event must be a mapping")
    else:
        for key in ("jurisdiction", "system", "rule", "operational_deadline", "pilot_policy"):
            if _string(event.get(key)) is None:
                errors.append(f"event.{key} must be a non-empty string")
        deadline = _string(event.get("operational_deadline"))
        if deadline is not None and DATE_PATTERN.fullmatch(deadline) is None:
            errors.append("event.operational_deadline must be an ISO date")

    sources = _mapping_list(contract.get("sources"))
    if not sources:
        errors.append("sources must be a non-empty list of mappings")
        sources = []
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        prefix = f"sources[{index}]"
        source_id = _string(source.get("id"))
        url = _string(source.get("url"))
        if source_id is None or ID_PATTERN.fullmatch(source_id) is None or source_id in source_ids:
            errors.append(f"{prefix}.id must be unique and stable")
        else:
            source_ids.add(source_id)
        if _string(source.get("kind")) is None:
            errors.append(f"{prefix}.kind must be non-empty")
        if url is None:
            errors.append(f"{prefix}.url must be non-empty")
        else:
            url_error = documentation_url_error(url)
            if url_error is not None:
                errors.append(f"{prefix}.url {url_error}")
        _string_list(source.get("expected_markers"), path=f"{prefix}.expected_markers", errors=errors)

    interfaces = _mapping_list(contract.get("interfaces"))
    if not interfaces:
        errors.append("interfaces must be a non-empty list of mappings")
        interfaces = []
    interface_ids: set[str] = set()
    for index, interface in enumerate(interfaces):
        prefix = f"interfaces[{index}]"
        interface_id = _string(interface.get("id"))
        role = _string(interface.get("role"))
        source_id = _string(interface.get("docs_source_id"))
        endpoint = _string(interface.get("endpoint"))
        if interface_id is None or ID_PATTERN.fullmatch(interface_id) is None or interface_id in interface_ids:
            errors.append(f"{prefix}.id must be unique and stable")
        else:
            interface_ids.add(interface_id)
        if role not in INTERFACE_ROLES:
            errors.append(f"{prefix}.role is invalid: {role}")
        if source_id not in source_ids:
            errors.append(f"{prefix}.docs_source_id is unknown: {source_id}")
        if endpoint is None or not endpoint.startswith("/") or "?" in endpoint:
            errors.append(f"{prefix}.endpoint must be a query-free relative API path")
        _string_list(interface.get("fields"), path=f"{prefix}.fields", errors=errors)
        if interface.get("access_after_gate") != "G1":
            errors.append(f"{prefix}.access_after_gate must equal G1")

    gates = _mapping(contract.get("gates"))
    if gates is None or set(gates) != REQUIRED_GATES:
        errors.append(f"gates must contain exactly {sorted(REQUIRED_GATES)}")
        gates = {}
    for gate_name, gate_object in gates.items():
        gate = _mapping(gate_object)
        if gate is None:
            errors.append(f"gates.{gate_name} must be a mapping")
            continue
        status = _string(gate.get("status"))
        if status not in GATE_STATUSES:
            errors.append(f"gates.{gate_name}.status is invalid: {status}")
        if _string(gate.get("reason")) is None:
            errors.append(f"gates.{gate_name}.reason must be non-empty")
        evidence = _string_list(gate.get("source_ids"), path=f"gates.{gate_name}.source_ids", errors=errors)
        unknown = sorted(set(evidence) - source_ids)
        if unknown:
            errors.append(f"gates.{gate_name} references unknown sources: {unknown}")

    response = _mapping(contract.get("response_draft"))
    if response is None:
        errors.append("response_draft must be a mapping")
    else:
        if response.get("status") != "not_frozen":
            errors.append("response_draft.status must equal not_frozen before G1")
        for key in ("unit", "pilot_exclusion", "treatment_boundary"):
            if _string(response.get(key)) is None:
                errors.append(f"response_draft.{key} must be non-empty")
        _string_list(response.get("components"), path="response_draft.components", errors=errors)
        _string_list(response.get("negative_controls"), path="response_draft.negative_controls", errors=errors)
    _string_list(contract.get("next_actions"), path="next_actions", errors=errors)
    return sorted(errors)


def gate_summary(contract: Mapping[str, object]) -> dict[str, object]:
    """Summarize event-contract gates without treating a metadata lead as admitted."""

    errors = validate_event_contract(contract)
    if errors:
        raise ValueError("invalid prospective event contract:\n- " + "\n- ".join(errors))
    gates = cast(Mapping[str, Mapping[str, object]], contract["gates"])
    counts = {status: 0 for status in sorted(GATE_STATUSES)}
    unresolved: list[str] = []
    failed: list[str] = []
    for name, gate in gates.items():
        status = cast(str, gate["status"])
        counts[status] += 1
        if status == "unresolved":
            unresolved.append(name)
        elif status == "fail":
            failed.append(name)
    return {
        "event_id": contract["event_id"],
        "stage": contract["stage"],
        "gate_counts": counts,
        "unresolved_gates": sorted(unresolved),
        "failed_gates": sorted(failed),
        "g1_ready": counts["pass"] == len(REQUIRED_GATES),
    }


def analyse_documentation(
    source_id: str,
    url: str,
    expected_markers: Sequence[str],
    *,
    status_code: int,
    content_type: str,
    content: bytes,
    retrieval_error: str | None = None,
) -> DocumentationProbe:
    """Check marker presence and hash one documentation response without retaining it."""

    if documentation_url_error(url) is not None:
        raise ValueError(f"unsafe documentation URL: {url}")
    text = html.unescape(content.decode("utf-8", errors="ignore")).casefold()
    missing = tuple(sorted(marker for marker in expected_markers if marker.casefold() not in text))
    return DocumentationProbe(
        source_id=source_id,
        url=url,
        status_code=status_code,
        content_type=content_type,
        byte_count=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        missing_markers=missing,
        retrieval_error=retrieval_error,
    )


def probe_documentation_sources(
    contract: Mapping[str, object], *, timeout_seconds: float = 20.0, max_bytes: int = 8_000_000
) -> list[DocumentationProbe]:
    """Fetch only allowlisted documentation pages and return content-free provenance."""

    errors = validate_event_contract(contract)
    if errors:
        raise ValueError("invalid prospective event contract:\n- " + "\n- ".join(errors))
    sources = cast(list[Mapping[str, object]], contract["sources"])
    probes: list[DocumentationProbe] = []
    for source in sources:
        source_id = cast(str, source["id"])
        url = cast(str, source["url"])
        markers = cast(list[str], source["expected_markers"])
        try:
            response = requests.get(
                url,
                timeout=timeout_seconds,
                allow_redirects=False,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "User-Agent": "Mozilla/5.0 (compatible; EcoPhysMetadataAudit/1.0)",
                },
            )
            content = response.content
            if len(content) > max_bytes:
                raise ValueError(f"documentation response exceeds {max_bytes} bytes: {source_id}")
            error = None if response.ok else f"http_status_{response.status_code}"
            probes.append(
                analyse_documentation(
                    source_id,
                    url,
                    markers,
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type", ""),
                    content=content,
                    retrieval_error=error,
                )
            )
        except requests.RequestException as error:
            probes.append(
                analyse_documentation(
                    source_id,
                    url,
                    markers,
                    status_code=0,
                    content_type="",
                    content=b"",
                    retrieval_error=type(error).__name__,
                )
            )
    return probes


def main(argv: Sequence[str] | None = None) -> int:
    """Validate a contract and optionally probe its documentation-only sources."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--probe-documentation", action="store_true")
    args = parser.parse_args(argv)
    contract = load_event_contract(args.contract)
    errors = validate_event_contract(contract)
    if errors:
        for error in errors:
            print(error)
        return 1
    output: dict[str, object] = {"summary": gate_summary(contract)}
    if args.probe_documentation:
        probes = probe_documentation_sources(contract)
        output["documentation_probes"] = [probe.to_dict() for probe in probes]
        output["all_markers_present"] = all(
            probe.retrieval_error is None and not probe.missing_markers for probe in probes
        )
    print(yaml.safe_dump(output, sort_keys=False).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
