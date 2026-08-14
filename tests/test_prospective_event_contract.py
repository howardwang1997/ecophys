from copy import deepcopy
from pathlib import Path

from ecomd.research.prospective_event_contract import (
    REQUIRED_GATES,
    analyse_documentation,
    documentation_url_error,
    gate_summary,
    load_event_contract,
    validate_event_contract,
)

CONTRACT_PATH = Path("data/manifests/gc0166_prospective_event_contract_v1.yaml")


def test_canonical_gc0166_contract_is_valid_but_not_g1_ready() -> None:
    contract = load_event_contract(CONTRACT_PATH)

    assert validate_event_contract(contract) == []
    summary = gate_summary(contract)
    assert summary["g1_ready"] is False
    assert summary["gate_counts"] == {"fail": 0, "pass": 5, "unresolved": 5}
    assert summary["failed_gates"] == []
    assert summary["unresolved_gates"] == [
        "eligible_population",
        "identity_history",
        "independent_replication",
        "null_failure_capture",
        "response_freeze",
    ]


def test_target_access_and_unallowlisted_data_endpoint_are_rejected() -> None:
    contract = load_event_contract(CONTRACT_PATH)
    broken = deepcopy(contract)
    boundary = broken["access_boundary"]
    sources = broken["sources"]
    assert isinstance(boundary, dict)
    assert isinstance(sources, list)
    boundary["target_rows_opened"] = True
    sources[0]["url"] = "https://data.elexon.co.uk/bmrs/api/v1/datasets/MDO?settlementDate=2026-08-14"

    errors = validate_event_contract(broken)

    assert any("target_rows_opened must be false" in error for error in errors)
    assert any("query, fragment, or credentials" in error for error in errors)


def test_all_pass_contract_is_ready_only_after_every_required_gate_passes() -> None:
    contract = load_event_contract(CONTRACT_PATH)
    ready = deepcopy(contract)
    gates = ready["gates"]
    assert isinstance(gates, dict)
    assert set(gates) == REQUIRED_GATES
    for gate in gates.values():
        assert isinstance(gate, dict)
        gate["status"] = "pass"

    assert gate_summary(ready)["g1_ready"] is True


def test_documentation_analysis_is_content_free_and_checks_markers() -> None:
    content = b"Maximum Delivery Offer publishTime"
    probe = analyse_documentation(
        "mdo_docs",
        "https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MDO",
        ["Maximum Delivery Offer", "publishTime", "serialNumber"],
        status_code=200,
        content_type="text/html",
        content=content,
    )

    assert probe.byte_count == len(content)
    assert len(probe.sha256) == 64
    assert probe.missing_markers == ("serialNumber",)
    assert "Maximum Delivery Offer" not in str(probe.to_dict())
    assert probe.retrieval_error is None


def test_documentation_analysis_records_http_failure_without_page_content() -> None:
    probe = analyse_documentation(
        "neso_rule",
        "https://www.neso.energy/news/gc0166-goes-live-enabling-smarter-use-limited-duration-assets",
        ["5 November 2026"],
        status_code=403,
        content_type="text/html",
        content=b"blocked response body",
        retrieval_error="http_status_403",
    )

    record = probe.to_dict()
    assert record["retrieval_error"] == "http_status_403"
    assert record["byte_count"] == len(b"blocked response body")
    assert "blocked response body" not in str(record)


def test_documentation_url_allowlist_excludes_live_data_api() -> None:
    assert documentation_url_error(
        "https://www.neso.energy/news/gc0166-goes-live-enabling-smarter-use-limited-duration-assets"
    ) is None
    assert documentation_url_error(
        "https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MDB"
    ) is None
    assert documentation_url_error("https://www.neso.energy/document/381641/download") is None
    assert documentation_url_error(
        "https://bscdocs.elexon.co.uk/bsc-procedures/bscp-15-bm-unit-registration"
    ) is None
    error = documentation_url_error("https://data.elexon.co.uk/bmrs/api/v1/datasets/MDB")
    assert error is not None and "not allowlisted" in error
