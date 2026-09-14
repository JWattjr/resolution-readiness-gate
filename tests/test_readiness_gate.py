import importlib
import json
import sys

import pytest


SPEC_HASH = "a" * 64
ACTION_DIGEST = "b" * 64
DEFAULT_CRITERIA = [
    {"id": "complete", "text": "The official record is complete"},
]
DEFAULT_SOURCES = ["https://official.example.org/result"]


def _args(
    criteria=None,
    sources=None,
    cutoff="2030-01-01T00:00:00Z",
    expiry="2030-02-01T00:00:00Z",
    max_wait="2030-03-01T00:00:00Z",
    spec_id="readiness-v1",
    spec_hash=SPEC_HASH,
    action_id="settle-market-1",
    action_digest=ACTION_DIGEST,
):
    return (
        "gate-1",
        "The official result of the example event",
        json.dumps(DEFAULT_CRITERIA if criteria is None else criteria),
        json.dumps(DEFAULT_SOURCES if sources is None else sources),
        cutoff,
        max_wait,
        expiry,
        spec_id,
        spec_hash,
        action_id,
        action_digest,
    )


def _deploy(direct_deploy, **kwargs):
    _reset_contract_registry()
    return direct_deploy("contracts/ResolutionReadinessGate.py", *_args(**kwargs))


class _DirectAddress:
    """Small direct-loader stand-in accepted by the SDK Address descriptor."""

    def __init__(self, value):
        self.as_bytes = bytes(value)

    def __str__(self):
        return "0x" + self.as_bytes.hex()


def _address(value, direct_vm=None):
    """Convert direct-test bytes to the SDK Address calldata/storage type."""
    if hasattr(value, "as_bytes"):
        return value
    if direct_vm is not None:
        # The direct loader injects ``genlayer`` lazily. Load the module once
        # without allocating a contract so Address is available for calldata.
        if "genlayer" not in sys.modules:
            from pathlib import Path
            from gltest.direct.loader import load_contract_class

            load_contract_class(Path("contracts/ResolutionReadinessGate.py"), direct_vm)
        from genlayer.py.types import Address

        return Address(value)
    return _DirectAddress(value)


def _reset_contract_registry():
    """Allow the direct harness to load the separate consumer class."""
    try:
        module = importlib.import_module("genlayer.gl.genvm_contracts")
    except ModuleNotFoundError:
        return
    module.__known_contract__ = None


def _mock_final(direct_vm, statuses=None, evidence_state="FINAL", refs=None, body="official final record"):
    statuses = statuses or {"complete": "SATISFIED"}
    direct_vm.mock_web(r".*", {"status": 200, "body": body})
    direct_vm.mock_llm(
        r".*",
        json.dumps(
            {
                "criterion_results": statuses,
                "evidence_refs": ["0"] if refs is None else refs,
                "evidence_state": evidence_state,
                "official_event_time": "2030-01-15",
            }
        ),
    )


class _FakeEmitter:
    def __init__(self):
        self.on = None
        self.calls = []

    def emit(self, on=None):
        self.on = on
        return self

    def execute_bound_action(self, *args):
        self.calls.append(args)

    def consume_ready(self, *args):
        self.calls.append(args)


class _FakeConsumer:
    def __init__(self, binding=None):
        self.binding = binding or {}
        self.emitter = _FakeEmitter()

    def view(self):
        return self

    def get_binding(self):
        return self.binding

    def emit(self, on=None):
        self.emitter.on = on
        return self.emitter


def _patch_gate_gl(monkeypatch, fake):
    gl = importlib.import_module("genlayer.gl")
    monkeypatch.setattr(gl, "get_contract_at", lambda address: fake)
    return gl


def test_ready_derivation_and_keyed_state(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm)
    result = contract.assess()
    assert result["state"] == "READY"
    assert result["reason_code"] == "EVIDENCE_FINAL"
    assert result["criterion_vector"] == ["SATISFIED"]
    assert result["evidence_refs"] == ["0"]
    assert contract.get_state()["criterion_results"] == {"complete": "SATISFIED"}
    assert contract.get_state()["assessment_id"] == "readiness-v1:1"
    assert direct_vm.run_validator()


def test_consensus_result_mutations_are_rejected(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm)
    accepted = contract.assess()
    mutations = [
        {**accepted, "state": "WAIT"},
        {**accepted, "evidence_state": "PROVISIONAL"},
        {**accepted, "criterion_vector": ["UNKNOWN"]},
        {**accepted, "evidence_refs": ["0", "0"]},
        {**accepted, "evidence_refs": ["9"]},
        {**accepted, "source_coverage": 0},
        {**accepted, "source_coverage": True},
        {**accepted, "reason_code": "CRITERION_UNKNOWN"},
        {**accepted, "unexpected": "persist me"},
        {key: value for key, value in accepted.items() if key != "reason_code"},
        ["not", "an", "object"],
    ]
    for mutation in mutations:
        assert direct_vm.run_validator(leader_result=mutation) is False


@pytest.mark.parametrize(
    "payload",
    [
        {"criterion_results": {"complete": "SATISFIED"}, "evidence_refs": ["0"], "evidence_state": "FINAL"},
        {"criterion_results": {"complete": "SATISFIED"}, "evidence_refs": ["0"], "evidence_state": "FINAL", "official_event_time": 1, "extra": 2},
        {"criterion_results": {"complete": True}, "evidence_refs": ["0"], "evidence_state": "FINAL", "official_event_time": "2030-01-15"},
        {"criterion_results": {"complete": "SATISFIED", "invented": "UNKNOWN"}, "evidence_refs": ["0"], "evidence_state": "FINAL", "official_event_time": "2030-01-15"},
        {"criterion_results": {"complete": "SATISFIED"}, "evidence_refs": ["0", "0"], "evidence_state": "FINAL", "official_event_time": "2030-01-15"},
        [],
        "not-json",
    ],
)
def test_malformed_model_results_fail_closed(direct_vm, direct_deploy, payload):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": "evidence"})
    direct_vm.mock_llm(r".*", payload if isinstance(payload, str) else json.dumps(payload))
    with direct_vm.expect_revert():
        contract.assess()
    assert contract.get_state()["attempts"] == 0


def test_partial_and_truncated_evidence_are_explicit(direct_vm, direct_deploy):
    criteria = [
        {"id": "decisive", "text": "The decisive official fact is present"},
        {"id": "context", "text": "Context remains relevant"},
    ]
    sources = ["https://a.example.org/fact", "https://b.example.org/fact"]
    contract = _deploy(direct_deploy, criteria=criteria, sources=sources)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r"a\.example\.org", {"status": 503, "body": "offline"})
    direct_vm.mock_web(r"b\.example\.org", {"status": 200, "body": "decisive final fact"})
    direct_vm.mock_llm(r".*", json.dumps({"criterion_results": {"context": "UNKNOWN", "decisive": "UNKNOWN"}, "evidence_refs": ["1"], "evidence_state": "FINAL", "official_event_time": ""}))
    result = contract.assess()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "CRITERION_UNKNOWN"
    assert result["source_coverage"] == 1
    assert result["evidence_refs"] == ["1"]

    # Truncation is explicitly marked in the evidence prompt, but does not
    # mechanically force WAIT when the available facts still support FINAL.
    direct_vm.clear_mocks()
    direct_vm.mock_web(r"a\.example\.org", {"status": 200, "body": "x" * 6001})
    direct_vm.mock_web(r"b\.example\.org", {"status": 200, "body": "complete final fact"})
    direct_vm.mock_llm(r"SOURCE_TRUNCATED", json.dumps({"criterion_results": {"context": "SATISFIED", "decisive": "SATISFIED"}, "evidence_refs": ["0", "1"], "evidence_state": "FINAL", "official_event_time": "2030-01-15"}))
    assert contract.assess()["state"] == "READY"


def test_empty_or_transport_failure_is_not_negative_evidence(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    direct_vm.mock_web(r".*", {"status": 200, "body": ""})
    result = contract.assess()
    assert result["state"] == "WAIT"
    assert result["reason_code"] == "SOURCE_UNAVAILABLE"
    assert result["criterion_vector"] == ["UNKNOWN"]
    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-15T00:00:00Z")
    result = contract.assess()
    assert result["reason_code"] == "SOURCE_UNAVAILABLE"


@pytest.mark.parametrize(
    "evidence_state,expected_state,expected_reason",
    [("PROVISIONAL", "WAIT", "EVIDENCE_PROVISIONAL"), ("CONFLICT", "CONTESTED", "AUTHORITATIVE_CONFLICT"), ("CANCELLED", "VOID", "EVENT_CANCELLED")],
)
def test_non_ready_evidence_states_are_deterministic(direct_vm, direct_deploy, evidence_state, expected_state, expected_reason):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm, evidence_state=evidence_state)
    result = contract.assess()
    assert result["state"] == expected_state
    assert result["reason_code"] == expected_reason


def test_time_boundaries_expiry_supersession_and_terminal_void(direct_vm, direct_deploy):
    contract = _deploy(direct_deploy, cutoff="2030-01-15T00:00:00Z", expiry="2030-01-20T00:00:00Z", max_wait="2030-01-25T00:00:00Z")
    direct_vm.warp("2030-01-14T23:59:59Z")
    before = contract.assess()
    assert before["state"] == "WAIT" and before["reason_code"] == "BEFORE_CUTOFF"
    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm)
    first = contract.assess()
    assert contract.get_state()["assessment_id"] == "readiness-v1:2"
    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-20T00:00:00Z")
    _mock_final(direct_vm, evidence_state="PROVISIONAL")
    expired = contract.assess()
    assert expired["state"] == "WAIT"
    assert contract.get_state()["assessment_id"] == "readiness-v1:3"
    assert expired["reason_code"] == "EVIDENCE_PROVISIONAL"
    direct_vm.clear_mocks()
    direct_vm.warp("2030-01-25T00:00:00Z")
    voided = contract.assess()
    assert voided["state"] == "VOID" and voided["reason_code"] == "MAX_WAIT_EXPIRED"
    attempts = contract.get_state()["attempts"]
    assert contract.assess() == contract.get_state()
    assert contract.get_state()["attempts"] == attempts


def test_consume_requires_exact_bound_consumer_action_and_assessment(direct_vm, direct_deploy, monkeypatch, direct_owner, direct_bob):
    contract = _deploy(direct_deploy)
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm)
    contract.assess()
    fake = _FakeConsumer()
    _patch_gate_gl(monkeypatch, fake)
    contract.authorized_consumer = _address(direct_owner, direct_vm)
    contract.consumer_bound = True
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("authorized consumer"):
        contract.consume_ready("readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST, "readiness-v1:1", 1)
    direct_vm.sender = direct_owner
    with direct_vm.expect_revert("assessment binding"):
        contract.consume_ready("readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST, "readiness-v1:999", 999)
    proof = contract.consume_ready("readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST, "readiness-v1:1", 1)
    assert proof["consumed"] is True and proof["callback"] == "FINALIZED"
    assert fake.emitter.on == "finalized"
    assert len(fake.emitter.calls) == 1
    with direct_vm.expect_revert("already consumed"):
        contract.consume_ready("readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST, "readiness-v1:1", 1)


def test_expired_ready_cannot_be_consumed(direct_vm, direct_deploy, monkeypatch, direct_owner):
    contract = _deploy(direct_deploy, expiry="2030-01-20T00:00:00Z", max_wait="2030-01-25T00:00:00Z")
    direct_vm.warp("2030-01-15T00:00:00Z")
    _mock_final(direct_vm)
    contract.assess()
    _patch_gate_gl(monkeypatch, _FakeConsumer())
    contract.authorized_consumer = _address(direct_owner, direct_vm)
    contract.consumer_bound = True
    direct_vm.sender = direct_owner
    direct_vm.warp("2030-01-20T00:00:00Z")
    with direct_vm.expect_revert("expired"):
        contract.consume_ready("readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST, "readiness-v1:1", 1)


def test_consumer_callback_is_bound_and_idempotent(direct_vm, direct_deploy, direct_owner, direct_bob):
    gate_address = _address(direct_owner, direct_vm)
    _reset_contract_registry()
    consumer = direct_deploy("contracts/ResolutionReadinessConsumer.py", "consumer-1", gate_address, "readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("bound gate"):
        consumer.execute_bound_action("readiness-v1:1", 1, "readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST)
    direct_vm.sender = direct_owner
    result = consumer.execute_bound_action("readiness-v1:1", 1, "readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST)
    assert result["executed"] is True and result["execution_count"] == 1
    replay = consumer.execute_bound_action("readiness-v1:1", 1, "readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST)
    assert replay["execution_count"] == 1
    with direct_vm.expect_revert("proof mismatch"):
        consumer.execute_bound_action("readiness-v1:2", 2, "readiness-v1", SPEC_HASH, "other-action", ACTION_DIGEST)


def test_consumer_rejects_provisional_and_emits_only_finalized(direct_vm, direct_deploy, monkeypatch, direct_owner):
    gate_address = _address(direct_owner, direct_vm)
    _reset_contract_registry()
    consumer = direct_deploy("contracts/ResolutionReadinessConsumer.py", "consumer-1", gate_address, "readiness-v1", SPEC_HASH, "settle-market-1", ACTION_DIGEST)
    fake_gate = _FakeConsumer()
    fake_gate.get_authorization = lambda: {"state": "WAIT", "spec_id": "readiness-v1", "spec_hash": SPEC_HASH, "action_id": "settle-market-1", "action_digest": ACTION_DIGEST, "ready_consumed": False, "can_consume": False, "assessment_id": "readiness-v1:1", "assessment_version": 1}
    gl = importlib.import_module("genlayer.gl")
    monkeypatch.setattr(gl, "get_contract_at", lambda address: fake_gate)
    direct_vm.sender = direct_owner
    with direct_vm.expect_revert("not READY"):
        consumer.request_execution()

    fake_gate.get_authorization = lambda: {"state": "READY", "spec_id": "readiness-v1", "spec_hash": SPEC_HASH, "action_id": "settle-market-1", "action_digest": ACTION_DIGEST, "ready_consumed": False, "can_consume": True, "assessment_id": "readiness-v1:1", "assessment_version": 1}
    queued = consumer.request_execution()
    assert queued["queued"] is True and fake_gate.emitter.on == "finalized"
    assert len(fake_gate.emitter.calls) == 1


def test_constructor_rejects_bad_timezone(direct_vm, direct_deploy):
    with direct_vm.expect_revert("timezone offset"):
        _deploy(direct_deploy, cutoff="2030-01-01T00:00:00")


def test_constructor_rejects_bad_expiry(direct_vm, direct_deploy):
    with direct_vm.expect_revert("expiry"):
        _deploy(direct_deploy, expiry="2030-01-01T00:00:00Z")


def test_constructor_rejects_bad_digest(direct_vm, direct_deploy):
    with direct_vm.expect_revert("64-character"):
        _deploy(direct_deploy, spec_hash="bad")


def test_constructor_rejects_duplicate_sources(direct_vm, direct_deploy):
    with direct_vm.expect_revert("source URLs must be unique"):
        _deploy(direct_deploy, sources=[DEFAULT_SOURCES[0], DEFAULT_SOURCES[0]])
