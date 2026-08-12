import json
import os
from pathlib import Path

import pytest


MANIFEST = Path("deployments/studionet.json")
EXPECTED_STATE = {"state":"READY"}


def test_studionet_manifest_records_successful_finalized_execution():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["network"] == "studionet"
    assert data["deployment_status"] == "FINALIZED"
    assert data["deployment_execution"] == "SUCCESS"
    assert data["consensus_test_status"] == "FINALIZED"
    assert data["consensus_test_execution"] == "SUCCESS"
    assert data["contract_address"].startswith("0x")
    assert data["deployment_transaction"].startswith("0x")
    for field, value in EXPECTED_STATE.items():
        assert data["consensus_test_state"][field] == value


@pytest.mark.slow
@pytest.mark.skipif(os.environ.get("GENLAYER_INTEGRATION") != "1", reason="set GENLAYER_INTEGRATION=1 for a live StudioNet read")
def test_live_studionet_state_matches_manifest():
    from genlayer_py import create_client
    from genlayer_py.chains import studionet

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    client = create_client(chain=studionet, endpoint=studionet.rpc_urls["default"]["http"][0])
    state = client.read_contract(address=data["contract_address"], function_name="get_state", args=[])
    for field, value in EXPECTED_STATE.items():
        assert state[field] == value
