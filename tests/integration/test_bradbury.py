import json
from pathlib import Path


MANIFEST = Path("deployments/bradbury.json")
EXPECTED_STATE = {"state":"READY"}


def test_bradbury_manifest_records_finalized_successful_execution():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["network"] == "testnet-bradbury"
    assert data["batch_submitted_before_finality_check"] is True
    assert data["consensus_batch_submitted_before_finality_check"] is True
    assert data["protocol_status"] == "FINALIZED"
    assert data["deployment_execution"] == "FINISHED_WITH_RETURN"
    assert data["finalized_verified"] is True
    assert data["consensus_test_status"] == "FINALIZED"
    assert data["consensus_test_execution"] == "FINISHED_WITH_RETURN"
    assert data["consensus_finalized_verified"] is True
    assert data["storage_capture_warning_detected"] is False
    assert data["stderr_inspected_empty"] is True
    assert data["consensus_receipt_summary"]["consensus_result"] == "AGREE"
    for field, value in EXPECTED_STATE.items():
        assert data["consensus_test_state"][field] == value
