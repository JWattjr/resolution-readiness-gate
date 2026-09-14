# Resolution Readiness Gate

Resolution Readiness Gate is a reusable GenLayer Intelligent Contract primitive
for evidence-backed downstream decisions. It freezes a specification, asks
validators to independently retrieve and interpret public evidence, and derives
one of WAIT, READY, VOID, or CONTESTED from the agreed facts. It does not hold
funds or execute a market payout.

## Frozen specification

The constructor freezes:

    gate_id, event_description, criteria_json, source_urls_json,
    cutoff_iso, max_wait_iso, readiness_expiry_iso, spec_id, spec_hash,
    action_id, action_digest

Criteria are bounded objects with exactly id and text. Source URLs are unique,
bounded HTTPS URLs. Criteria and sources are normalized and sorted before they
are stored. The two SHA-256 digests bind the intended specification and the
exact downstream action. All timestamps require an offset and are stored in
UTC.

The cutoff is the earliest time at which an assessment may be attempted; it is
not a historical "as-of" boundary for what evidence a validator may read.
Before cutoff, assess() deterministically records WAIT. At or after max_wait,
it deterministically records terminal VOID. A READY assessment expires at
readiness_expiry_iso and must be reassessed after expiry.

## Consensus boundary

Each nondeterministic execution fetches every frozen source, bounds the response,
and treats page text as untrusted data. The raw model response must contain
exactly criterion_results, evidence_refs, evidence_state, and
official_event_time. Every criterion ID must occur exactly once; references
must identify available, unique source indices. The leader result is
canonicalized, an independent validator re-fetches and canonicalizes the same
specification, and exact canonical objects are compared. The accepted result is
validated again before persistence, and only canonical fields are stored.

Evidence states have explicit meanings:

- FINAL: the available official record is conclusive and complete enough for
  the frozen criteria.
- PROVISIONAL: more final evidence is needed, so the deterministic result is
  WAIT.
- CONFLICT: authoritative sources or active official proceedings conflict, so
  the result is CONTESTED.
- CANCELLED: explicit official cancellation or impossibility, so the result is
  VOID.

Unavailable, empty, non-success, or transport-failed sources are not negative
evidence. Partial or truncated material is marked for validators; it does not
mechanically force WAIT when the available facts are sufficient for a final
judgement. If the available facts are insufficient, the validator must return
UNKNOWN/PROVISIONAL and the gate remains WAIT. HTTPS reachability does not prove
publisher authority. The prompts treat evidence as untrusted text, but this
project makes no guarantee of prompt-injection immunity.

## Bound-consumer authorization

The owner deploys a separate ResolutionReadinessConsumer with the gate address,
specification ID/hash, action ID/digest, and a consumer ID. bind_consumer()
verifies that frozen binding by calling the consumer's view and closes the
binding before any assessment. Only that bound consumer may consume READY.

The consumer's request_execution() emits gate.consume_ready() with
on="finalized". The gate checks READY, expiry, exact binding, assessment ID and
version, then marks the authorization consumed before emitting the
execute_bound_action() callback with on="finalized". The consumer accepts only
the bound gate and exact proof, records the action once, and makes duplicate
callbacks idempotent. retry_execution()/retry_bound_action() safely re-queue a
failed child message; they cannot create a second action. WAIT, VOID, CONTESTED,
expired, superseded, mismatched, or provisional readiness cannot execute.

## Current StudioNet proof

Fresh source commit: ae1916cd447d2e9f8ed6e4f29e2107bec3fce40f

- Gate contract: [0xa8Be5185b1fa8F4aE2CadF924A5F5dBCD429fBb5](https://explorer-studio.genlayer.com/contracts/0xa8Be5185b1fa8F4aE2CadF924A5F5dBCD429fBb5)
- Consumer contract: [0x2394879de943F3E89BD18d9e48991cD543786954](https://explorer-studio.genlayer.com/contracts/0x2394879de943F3E89BD18d9e48991cD543786954)
- Deployment: [gate transaction](https://explorer-studio.genlayer.com/transactions/0x4c2cac2a4bf8ea624e57b75b6527c9f9d6247033b0ea0c55bf2a63ada83e57e4)
- Assessment: [READY transaction](https://explorer-studio.genlayer.com/transactions/0x0911ef9df300b6b1041b2c33c5711d9fcc4e86667cfde94fb52f841106b2abc3)
- Bound consumer action: [callback transaction](https://explorer-studio.genlayer.com/transactions/0x2871c6bfd940a5eb2ab2bb2379dc81abb48557894c82d57553fa7eeead691a9a)
- Authoritative evidence: [GovInfo Public Law 117-58](https://www.govinfo.gov/app/details/PLAW-117publ58/summary)

The current manifest contains constructor arguments, all transaction hashes,
finality and execution results separately, observed validator votes, source
identity hashes, and read-back state. The demonstration reached a READY
assessment with 3 AGREE and 2 IDLE votes (quorum), then executed the bound
consumer action exactly once.

The prior StudioNet and Bradbury deployments are retained only as explicitly
historical records in the deployments directory; they are not the current
source or submission proof.

## Checks

    python -m pip install -r requirements.txt
    python -m genvm_linter.cli contracts/ResolutionReadinessGate.py
    python -m genvm_linter.cli contracts/ResolutionReadinessConsumer.py
    python -m pytest tests -q

See docs/SECURITY_AUDIT.md, docs/TEST_MATRIX.md, docs/SECURITY.md,
PORTAL_SUBMISSION.md, and deployments/studionet.json for the release evidence.
