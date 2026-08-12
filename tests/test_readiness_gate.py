import json


def _deploy(direct_deploy):
    return direct_deploy(
        "contracts/ResolutionReadinessGate.py", "gate-1", "Example certified event",
        json.dumps([{"id": "final", "text": "The official result is final"}]),
        json.dumps(["https://official.example.org/result"]),
        "2030-01-01T00:00:00Z", "2030-02-01T00:00:00Z", "gate-v1",
    )


def test_contract_derives_ready_and_ignores_model_decision(direct_vm, direct_deploy, direct_owner):
    contract = _deploy(direct_deploy)
    direct_vm.sender = direct_owner
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "certified final result"})
    direct_vm.mock_llm(r".*", json.dumps({
        "decision": "WAIT", "criterion_results": {"final": "SATISFIED"},
        "official_event_time": "2030-01-10", "evidence_state": "FINAL",
    }))
    assert contract.assess()["decision"] == "READY"
    assert direct_vm.run_validator()
    assert contract.can_resolve()
    assert contract.consume_ready()["consumed"] is True
    assert not contract.can_resolve()


def test_max_wait_voids_deterministically(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-02-01T00:00:00Z")
    assert contract.assess()["reason_code"] == "MAX_WAIT_EXPIRED"
