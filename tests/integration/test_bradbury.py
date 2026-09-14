import json
from pathlib import Path


MANIFEST = Path("deployments/bradbury.json")


def test_bradbury_manifest_is_explicitly_historical():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["historical"] is True
    assert data["submission_status"] == "historical_only"
    assert data["source_revision"] == "pre-authorization-hardening"
    assert data["superseded_by"] == "deployments/studionet.json"
    assert data["network"] == "testnet-bradbury"
    assert data["protocol_status"] == "FINALIZED"
    assert data["deployment_execution"] == "FINISHED_WITH_RETURN"
    assert data["finalized_verified"] is True
    assert data["consensus_test_status"] == "FINALIZED"
    assert data["consensus_test_execution"] == "FINISHED_WITH_RETURN"
    assert data["consensus_finalized_verified"] is True
    assert data["storage_capture_warning_detected"] is False
    assert data["stderr_inspected_empty"] is True
