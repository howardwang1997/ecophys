import json
from copy import deepcopy
from pathlib import Path
from typing import cast

from ecomd.research.compound_v3_metadata import (
    audit_source_tree,
    load_metadata_preflight,
    validate_metadata_preflight,
)

MANIFEST_PATH = Path("data/manifests/compound_v3_metadata_preflight_v1.yaml")


def _write_fixture(root: Path, manifest: dict[str, object]) -> None:
    markets = cast(list[dict[str, object]], manifest["markets"])
    required_config = cast(list[str], manifest["required_configuration_keys"])
    required_rates = cast(list[str], manifest["required_rate_keys"])
    for index, market in enumerate(markets):
        config_path = root / cast(str, market["configuration_path"])
        roots_path = root / cast(str, market["roots_path"])
        migrations_path = root / cast(str, market["migrations_path"])
        config_path.parent.mkdir(parents=True, exist_ok=True)
        roots_path.parent.mkdir(parents=True, exist_ok=True)
        migrations_path.mkdir(parents=True, exist_ok=True)
        config = {key: f"value-{key}" for key in required_config}
        config.update(
            {
                "name": f"Market {index}",
                "symbol": f"cM{index}",
                "baseToken": f"M{index}",
                "baseTokenAddress": f"0x{index + 1:040x}",
                "governor": "0x0000000000000000000000000000000000000100",
                "pauseGuardian": "0x0000000000000000000000000000000000000200",
                "rates": {key: 0 for key in required_rates},
                "assets": {"COLLATERAL": {"address": f"0x{index + 100:040x}"}},
            }
        )
        roots = {
            "comet": f"0x{index + 1000:040x}",
            "configurator": f"0x{index + 2000:040x}",
        }
        config_path.write_text(json.dumps(config), encoding="utf-8")
        roots_path.write_text(json.dumps(roots), encoding="utf-8")
        (migrations_path / f"170000000{index}_fixture.ts").write_text("fixture", encoding="utf-8")
    contracts = cast(dict[str, object], manifest["contracts"])
    marker_keys = {
        "action_interface": "required_action_markers",
        "configurator": "required_configurator_markers",
        "storage": "required_storage_markers",
    }
    for contract_key, marker_key in marker_keys.items():
        path = root / cast(str, contracts[contract_key])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(cast(list[str], manifest[marker_key])), encoding="utf-8")
    license_contract = cast(dict[str, object], manifest["license_contract"])
    license_path = root / cast(str, license_contract["path"])
    license_path.write_text("\n".join(cast(list[str], license_contract["expected_markers"])), encoding="utf-8")


def test_canonical_metadata_preflight_is_valid_and_zero_row() -> None:
    manifest = load_metadata_preflight(MANIFEST_PATH)

    assert validate_metadata_preflight(manifest) == []
    boundary = manifest["access_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["chain_rpc_used"] is False
    assert boundary["participant_action_rows_opened"] is False
    assert boundary["official_code_blobs_opened"] is True


def test_synthetic_complete_source_tree_passes_all_metadata_gates(tmp_path: Path) -> None:
    manifest = load_metadata_preflight(MANIFEST_PATH)
    _write_fixture(tmp_path, manifest)
    source = cast(dict[str, object], manifest["source"])

    artifact = audit_source_tree(
        tmp_path,
        manifest,
        source_commit=cast(str, source["commit"]),
        source_remote=cast(str, source["repo_url"]),
        source_clean=True,
    )

    assert artifact["decision"] == "PASS_SOURCE_METADATA_AUTHORIZE_CHAIN_METADATA_ONLY"
    assert artifact["gate_counts"] == {"pass": 9, "fail": 0}
    assert artifact["market_totals"] == {
        "market_count": 6,
        "complete_schema_count": 6,
        "unique_comet_count": 6,
        "collateral_asset_count": 6,
        "migration_file_count": 6,
    }
    assert str(tmp_path) not in json.dumps(artifact)


def test_duplicate_comet_and_missing_action_marker_fail_without_crashing(tmp_path: Path) -> None:
    manifest = load_metadata_preflight(MANIFEST_PATH)
    _write_fixture(tmp_path, manifest)
    markets = cast(list[dict[str, object]], manifest["markets"])
    first_roots = json.loads((tmp_path / cast(str, markets[0]["roots_path"])).read_text(encoding="utf-8"))
    second_roots_path = tmp_path / cast(str, markets[1]["roots_path"])
    second_roots = json.loads(second_roots_path.read_text(encoding="utf-8"))
    second_roots["comet"] = first_roots["comet"]
    second_roots_path.write_text(json.dumps(second_roots), encoding="utf-8")
    contracts = cast(dict[str, object], manifest["contracts"])
    action_path = tmp_path / cast(str, contracts["action_interface"])
    action_path.write_text("event Supply(address indexed from, address indexed dst, uint amount);", encoding="utf-8")
    source = cast(dict[str, object], manifest["source"])

    artifact = audit_source_tree(
        tmp_path,
        manifest,
        source_commit=cast(str, source["commit"]),
        source_remote=cast(str, source["repo_url"]),
        source_clean=True,
    )

    assert artifact["decision"] == "FAIL_SOURCE_METADATA_KEEP_COMPOUND_UNADMITTED"
    gates = artifact["gates"]
    assert isinstance(gates, dict)
    assert gates["unique_comet_roots"] is False
    assert gates["action_surface"] is False


def test_manifest_rejects_chain_access_and_unpinned_source() -> None:
    manifest = load_metadata_preflight(MANIFEST_PATH)
    broken = deepcopy(manifest)
    boundary = broken["access_boundary"]
    source = broken["source"]
    assert isinstance(boundary, dict)
    assert isinstance(source, dict)
    boundary["chain_rpc_used"] = True
    source["commit"] = "main"

    errors = validate_metadata_preflight(broken)

    assert any("chain_rpc_used must be false" in error for error in errors)
    assert any("40-character Git SHA" in error for error in errors)
