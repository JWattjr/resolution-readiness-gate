import json
import os
from pathlib import Path

import pytest


MANIFEST = Path("deployments/studionet.json")
EXPECTED_GATE_STATE = {
    "state": "READY",
    "evidence_state": "FINAL",
    "ready_consumed": True,
    "action_queued": True,
    "can_consume": False,
}


def test_studionet_manifest_records_current_finalized_execution():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["historical"] is False
    assert data["network"] == "studionet"
    assert data["source_commit"] == "ae1916cd447d2e9f8ed6e4f29e2107bec3fce40f"
    assert data["deployment_status"] == "FINALIZED"
    assert data["deployment_execution"] == "SUCCESS"
    assert data["assessment_status"] == "FINALIZED"
    assert data["assessment_execution"] == "SUCCESS"
    assert data["consumer_callback_status"] == "FINALIZED"
    assert data["consumer_callback_execution"] == "SUCCESS"
    assert data["source_identity"]["verified"] is True
    assert data["source_identity"]["bytecode_identity_verified"] is False
    assert data["gate_address"].startswith("0x")
    assert data["consumer_address"].startswith("0x")
    assert data["deployment_transaction"].startswith("0x")
    assert data["assessment_result"]["state"] == "READY"
    assert data["assessment_result"]["criterion_results"] == {
        "approval_date": "SATISFIED",
        "law_number": "SATISFIED",
    }
    for field, value in EXPECTED_GATE_STATE.items():
        assert data["readback"]["gate_state"][field] == value
    assert data["readback"]["consumer_state"]["executed"] is True
    assert data["readback"]["consumer_state"]["execution_count"] == 1
    assert data["readback"]["consumer_state"]["request_count"] == 1


@pytest.mark.slow
@pytest.mark.skipif(
    os.environ.get("GENLAYER_INTEGRATION") != "1",
    reason="set GENLAYER_INTEGRATION=1 for a live StudioNet read",
)
def test_live_studionet_state_matches_manifest():
    from genlayer_py import create_client
    from genlayer_py.chains import studionet

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    client = create_client(
        chain=studionet, endpoint=studionet.rpc_urls["default"]["http"][0]
    )
    gate_state = client.read_contract(
        address=data["gate_address"], function_name="get_state", args=[]
    )
    consumer_state = client.read_contract(
        address=data["consumer_address"], function_name="get_state", args=[]
    )
    for field, value in EXPECTED_GATE_STATE.items():
        assert gate_state[field] == value
    assert consumer_state["executed"] is True
    assert consumer_state["execution_count"] == 1
