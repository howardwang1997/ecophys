from __future__ import annotations

import pytest

from scripts.run_research_discovery_sandbox import SandboxRuntimeError
from scripts.test_research_discovery_oci_conformance import validate_probe_report


def test_probe_report_requires_every_isolation_check() -> None:
    validate_probe_report(
        {
            "schema_version": 1,
            "passed": True,
            "checks": {"network_none": True, "read_only": True},
        }
    )


@pytest.mark.parametrize(
    "report",
    [
        {"schema_version": 1, "passed": False, "checks": {"network_none": True}},
        {"schema_version": 1, "passed": True, "checks": {"network_none": False}},
        {"schema_version": 1, "passed": True, "checks": {}},
    ],
)
def test_probe_report_fails_closed(report: dict[str, object]) -> None:
    with pytest.raises(SandboxRuntimeError):
        validate_probe_report(report)
