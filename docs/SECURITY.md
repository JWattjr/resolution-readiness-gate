# Security model

## Threats addressed

- Malicious or drifting evidence is bounded, treated as untrusted text, and
  independently re-fetched by validators.
- The leader cannot widen the schema, invent criterion IDs, reuse references,
  or choose an inconsistent decision. Canonical validation runs before and
  after consensus.
- Frozen UTC cutoff, expiry, maximum-wait, specification, and action digests
  make timing and authorization explicit.
- Only the bound consumer can consume an unexpired READY assessment. The gate
  marks it consumed before the finalized callback; the consumer accepts only the
  exact proof and is idempotent.
- HTTP failure, empty content, non-success status, and truncation are explicit
  states. Unavailable evidence is not treated as a negative fact.
- Unsafe evidence URL shapes (userinfo, private/internal hosts, literal private
  IPs, whitespace, and non-default ports) are rejected.

## Contract boundary

Validators extract criterion statuses, evidence finality, conflict/cancellation
state, coverage, and an official date. Contract code derives WAIT, READY, VOID,
or CONTESTED. Partial/truncated evidence is marked, not automatically forced to
WAIT; validators must return UNKNOWN/PROVISIONAL when the available material is
insufficient. The cutoff is the earliest assessment time, not a historical
evidence boundary.

The separate ResolutionReadinessConsumer demonstrates the enforced relationship:
the gate address, frozen spec/action bindings, assessment ID/version, and
protocol-finalized callback are all checked. Consumers must keep real-world side
effects idempotent because retry is safe at the contract boundary but cannot
undo an external side effect.

## Residual risks

HTTPS reachability does not prove publisher authority, and there is no
deployment-specific publisher allowlist. Dynamic sources can disagree and model
classification can remain uncertain. Prompts reduce, but do not guarantee
resistance to, prompt injection. The contract relies on GenLayer protocol
finality for child messages and does not inspect its own finality. No payout or
financial settlement logic is included.
