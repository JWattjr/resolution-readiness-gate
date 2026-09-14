# Security and consensus audit: Resolution Readiness Gate

Audit date: 2026-09-14
Scope: contracts/ResolutionReadinessGate.py and contracts/ResolutionReadinessConsumer.py
Method: source review, direct behavioral tests, GenVM lint/schema extraction, and
read-only StudioNet receipt/source/state verification.

## Result

No unresolved critical or high-severity issue was identified in this bounded
engineering review. This is not formal verification, a financial guarantee, or
legal advice. The contracts do not custody or transfer value.

## Boundary and authorization findings

| ID | Severity | Finding and control |
| --- | --- | --- |
| RG-01 | High | The model cannot choose an arbitrary decision. Raw output has exactly four keys; criterion IDs, statuses, evidence references, dates, evidence state, and types are bounded and canonicalized. READY/WAIT/VOID/CONTESTED is derived from the agreed facts. |
| RG-02 | High | The leader result is independently re-fetched and canonicalized by validators. Exact canonical objects must match, and the accepted object is validated again before persistence. |
| RG-03 | High | Only canonical fields are stored; leader dictionaries are never copied into storage. Criteria are sorted and get_state() exposes an ID-keyed criterion_results map as well as the vector. |
| RG-04 | High | A frozen spec ID/hash, authorized consumer address, action ID/digest, assessment ID/version, expiry, and single-use flag bind each capability. Wrong consumers, actions, specifications, versions, superseded assessments, and replay are rejected. |
| RG-05 | High | The consumer requests gate consumption only through on="finalized". The gate marks the capability consumed before emitting the finalized callback. The callback checks the exact proof and is idempotent; explicit retry paths cannot increment execution twice. |
| RG-06 | Medium | Timestamps require offsets and normalize to UTC. Cutoff (earliest assessment), readiness expiry, and max-wait are separate. Before cutoff is WAIT; at/after max-wait is terminal VOID; an expired READY is reassessed. |
| RG-07 | Medium | HTTP status, empty bodies, transport errors, and truncation are distinct. Unavailable evidence is not negative evidence. Partial/truncated evidence may still support READY only when validators find the available facts sufficient; otherwise UNKNOWN/PROVISIONAL yields WAIT. |

## Tests and static checks

- Focused suite: 26 passed, 1 skipped (the skipped test is the opt-in live
  integration check).
- GenVM lint: both contracts passed AST validation.
- Schema extraction: Gate constructor 11 arguments and 7 methods; consumer
  constructor 6 arguments and 5 methods.
- AST regression confirms nondeterministic gate closures capture ordinary
  snapshots and do not reference storage-backed self.
- Tests mutate each consequential result field and cover extra keys,
  bool/int confusion, malformed nested values, evidence failure modes,
  deadline boundaries, expiry/reassessment, wrong bindings, provisional
  execution, replay, callback sender checks, and terminal idempotency.

Mocked tests do not prove prompt-injection immunity. Evidence interpretation and
publisher authority remain application-level risks.

## Fresh StudioNet evidence

Current source commit: ae1916cd447d2e9f8ed6e4f29e2107bec3fce40f

- Gate address: 0xa8Be5185b1fa8F4aE2CadF924A5F5dBCD429fBb5
- Consumer address: 0x2394879de943F3E89BD18d9e48991cD543786954
- Gate deployed source SHA-256: fbd6d8267b15a95231ef6b26f87d4c4a7fb242ad9b3dbd3bee6f34d679046b53
- Consumer deployed source SHA-256: ba45d49591f207d6e33439476f9dd3b1384e046b20af04fc2944b5b89c94325f

Read-only gen_getContractCode downloads matched the current local source
byte-for-byte for both contracts. This verifies deployed-source identity, not
EVM bytecode identity (bytecode identity is not claimed).

Every receipt below was independently read after submission. Protocol finality
and execution result are reported separately:

| Operation | Transaction | Protocol | Execution | Observed votes |
| --- | --- | --- | --- | --- |
| Gate deployment | 0x4c2cac2a4bf8ea624e57b75b6527c9f9d6247033b0ea0c55bf2a63ada83e57e4 | FINALIZED | SUCCESS | 5 AGREE |
| Consumer deployment | 0x3ba626a89e1a207caa5d7ca40333e03b9f3522be56c85b427479331b49201ab8 | FINALIZED | SUCCESS | 3 AGREE, 2 IDLE |
| Consumer binding | 0xa9fc9682b47b7e8b8dd92c9b1fda0ae1e1c3e689026b04c2a6150a552325b489 | FINALIZED | SUCCESS | 3 AGREE, 2 IDLE |
| Assessment | 0x0911ef9df300b6b1041b2c33c5711d9fcc4e86667cfde94fb52f841106b2abc3 | FINALIZED | SUCCESS | 3 AGREE, 2 IDLE |
| Consumer request | 0x226ef2652134dd513c1dc397699bdbbb348b772f45a8eb4902fb1915bfc3b541 | FINALIZED | SUCCESS | 3 AGREE, 2 IDLE |
| Gate consumption | 0x9f6adf4f5e55b427b6fe7fb63d327d3bb49a3d4ae096b897a7a521667db3b652 | FINALIZED | SUCCESS | 3 AGREE, 2 IDLE |
| Consumer callback | 0x2871c6bfd940a5eb2ab2bb2379dc81abb48557894c82d57553fa7eeead691a9a | FINALIZED | SUCCESS | 5 AGREE |

The assessment returned READY, evidence_state FINAL, both criteria SATISFIED,
source_coverage 1, official_event_time 2021-11-15, reason EVIDENCE_FINAL, and
assessment version 1. The read-back gate has ready_consumed=true,
action_queued=true, and can_consume=false. The consumer has executed=true,
execution_count=1, and request_count=1. The assessment's 3 AGREE/2 IDLE is a
quorum result, not unanimity.

Authoritative evidence used in the demo is the public GovInfo record for Public
Law 117-58. The gate records source interpretation; HTTPS reachability alone
does not establish publisher authority.

## Historical evidence

The former StudioNet deployment and the Bradbury deployment were made from the
pre-hardening source commit 58855ec2cc18ff95ca4f65e627a9e287adff8dda. Their
receipts and state remain available for audit in explicitly historical
manifests. They are not evidence for the current source or current Portal
submission. The old StudioNet contract code was independently matched to that
historical commit; no claim is made that either historical contract has the
current bound-consumer behavior.

## Residual limitations

Dynamic sources can drift or disagree, models can remain uncertain, and a
validator can misinterpret an ambiguous official record. Truncation is marked
but is not a mechanical WAIT rule. The contract relies on protocol-finalized
child messages and does not inspect its own protocol finality. Consumers must
keep their real-world side effects idempotent. There is no payout logic,
publisher allowlist, or guaranteed prompt-injection resistance.
