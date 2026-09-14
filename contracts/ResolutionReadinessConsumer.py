# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

"""Minimal consumer for the ResolutionReadinessGate callback protocol."""

import json

from genlayer import *


MAX_ID = 96
MAX_SPEC_ID = 128
MAX_ACTION_ID = 128
MAX_DIGEST = 64
ZERO_ADDRESS = "0x" + ("0" * 40)


def _bounded_text(value, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise gl.vm.UserError(f"[EXPECTED] {label} must be a string")
    normalized = value.strip()
    if not 1 <= len(normalized) <= maximum:
        raise gl.vm.UserError(f"[EXPECTED] {label} length is invalid")
    return normalized


def _digest(value, label: str) -> str:
    if not isinstance(value, str):
        raise gl.vm.UserError(f"[EXPECTED] {label} must be a hex digest")
    normalized = value.strip().lower()
    if len(normalized) != MAX_DIGEST or any(ch not in "0123456789abcdef" for ch in normalized):
        raise gl.vm.UserError(f"[EXPECTED] {label} must be a 64-character hex digest")
    return normalized


def _address_text(value) -> str:
    return str(value).strip().lower()


def _is_zero_address(value) -> bool:
    return _address_text(value) == ZERO_ADDRESS


class ResolutionReadinessConsumer(gl.Contract):
    """Record one irreversible downstream action authorized by a gate.

    ``request_execution`` emits the gate consumption on ``finalized``. The
    gate then emits this callback on ``finalized`` after validating the exact
    specification, action, and assessment binding. A duplicate callback is a
    no-op, so retries cannot execute the bound action twice.
    """

    owner: Address
    consumer_id: str
    gate_address: Address
    spec_id: str
    spec_hash: str
    action_id: str
    action_digest: str
    executed: bool
    execution_count: u256
    request_count: u256
    last_execution_json: str

    def __init__(self, consumer_id: str, gate_address: Address, spec_id: str, spec_hash: str, action_id: str, action_digest: str):
        self.owner = gl.message.sender_address
        self.consumer_id = _bounded_text(consumer_id, "consumer_id", MAX_ID)
        if _is_zero_address(gate_address):
            raise gl.vm.UserError("[EXPECTED] gate address is required")
        self.gate_address = gate_address
        self.spec_id = _bounded_text(spec_id, "spec_id", MAX_SPEC_ID)
        self.spec_hash = _digest(spec_hash, "spec_hash")
        self.action_id = _bounded_text(action_id, "action_id", MAX_ACTION_ID)
        self.action_digest = _digest(action_digest, "action_digest")
        self.executed = False
        self.execution_count = u256(0)
        self.request_count = u256(0)
        self.last_execution_json = "{}"

    @gl.public.write
    def request_execution(self) -> dict:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("[EXPECTED] only the consumer owner may request execution")
        if self.executed:
            return self.get_state()
        gate = gl.get_contract_at(self.gate_address)
        authorization = gate.view().get_authorization()
        if not isinstance(authorization, dict) or authorization.get("state") != "READY":
            raise gl.vm.UserError("[EXPECTED] gate is not READY")
        if authorization.get("spec_id") != self.spec_id or authorization.get("spec_hash") != self.spec_hash or authorization.get("action_id") != self.action_id or authorization.get("action_digest") != self.action_digest:
            raise gl.vm.UserError("[EXPECTED] gate authorization does not match this consumer")
        if authorization.get("ready_consumed"):
            raise gl.vm.UserError("[EXPECTED] gate authorization is already consumed; use retry_execution")
        if not authorization.get("can_consume"):
            raise gl.vm.UserError("[EXPECTED] gate readiness is expired or unbound")
        gate.emit(on="finalized").consume_ready(self.spec_id, self.spec_hash, self.action_id, self.action_digest, authorization["assessment_id"], authorization["assessment_version"])
        self.request_count += u256(1)
        return {"queued": True, "callback": "FINALIZED", "assessment_id": authorization["assessment_id"]}

    @gl.public.write
    def retry_execution(self) -> dict:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("[EXPECTED] only the consumer owner may retry execution")
        if self.executed:
            return self.get_state()
        gate = gl.get_contract_at(self.gate_address)
        authorization = gate.view().get_authorization()
        if not isinstance(authorization, dict) or authorization.get("state") != "READY":
            raise gl.vm.UserError("[EXPECTED] gate is not READY")
        if authorization.get("spec_id") != self.spec_id or authorization.get("spec_hash") != self.spec_hash or authorization.get("action_id") != self.action_id or authorization.get("action_digest") != self.action_digest:
            raise gl.vm.UserError("[EXPECTED] gate authorization does not match this consumer")
        if authorization.get("ready_consumed"):
            gate.emit(on="finalized").retry_bound_action()
        else:
            gate.emit(on="finalized").consume_ready(self.spec_id, self.spec_hash, self.action_id, self.action_digest, authorization["assessment_id"], authorization["assessment_version"])
        self.request_count += u256(1)
        return {"queued": True, "callback": "FINALIZED", "assessment_id": authorization["assessment_id"]}

    @gl.public.write
    def execute_bound_action(self, assessment_id: str, assessment_version: u256, spec_id: str, spec_hash: str, action_id: str, action_digest: str) -> dict:
        if gl.message.sender_address != self.gate_address:
            raise gl.vm.UserError("[EXPECTED] only the bound gate may execute this action")
        expected_assessment_id = f"{self.spec_id}:{assessment_version}"
        if assessment_id != expected_assessment_id or type(assessment_version) is not int or spec_id != self.spec_id or _digest(spec_hash, "spec_hash") != self.spec_hash or action_id != self.action_id or _digest(action_digest, "action_digest") != self.action_digest:
            raise gl.vm.UserError("[EXPECTED] bound action proof mismatch")
        if self.executed:
            return self.get_state()
        self.executed = True
        self.execution_count += u256(1)
        self.last_execution_json = json.dumps({"consumer_id": self.consumer_id, "assessment_id": assessment_id, "assessment_version": assessment_version, "spec_id": spec_id, "spec_hash": self.spec_hash, "action_id": action_id, "action_digest": self.action_digest, "execution": "BOUND_ACTION"}, sort_keys=True, separators=(",", ":"))
        return self.get_state()

    @gl.public.view
    def get_binding(self) -> dict:
        return {"gate_address": _address_text(self.gate_address), "spec_id": self.spec_id, "spec_hash": self.spec_hash, "action_id": self.action_id, "action_digest": self.action_digest}

    @gl.public.view
    def get_state(self) -> dict:
        return {"consumer_id": self.consumer_id, "gate_address": _address_text(self.gate_address), "spec_id": self.spec_id, "spec_hash": self.spec_hash, "action_id": self.action_id, "action_digest": self.action_digest, "executed": self.executed, "execution_count": self.execution_count, "request_count": self.request_count, "last_execution": self.last_execution_json}
