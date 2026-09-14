# Test matrix

Focused result: 26 passed, 1 skipped. The skipped check is the opt-in live
integration read (GENLAYER_INTEGRATION=1); the fresh StudioNet receipts and
read-back were independently verified separately and are recorded in
deployments/studionet.json.

| Invariant | Behavioral coverage | Evidence |
| --- | --- | --- |
| Exact raw and canonical schemas | Missing/extra keys, malformed wrappers, invalid enums, unknown criterion IDs, duplicate references, wrong vector length, inconsistent decision/reason | Direct mocked GenVM tests |
| Type safety | Bool/int confusion, non-string statuses, malformed nested values, invalid dates and digests | Direct mocked GenVM tests |
| Consensus boundary | Leader-field mutations, independent re-fetch, exact canonical comparison, validation before persistence, canonical-only storage | Direct mocked GenVM tests and nondeterministic-closure AST regression |
| Deterministic lifecycle | READY, WAIT, VOID, CONTESTED, all-satisfied FINAL, unknown criteria, provisional, conflict, cancellation, all-source outage | Direct mocked GenVM tests |
| Evidence semantics | Missing, partial, truncated, empty, non-success, and transport-failed sources; sufficient partial evidence can be READY, insufficient evidence remains WAIT | Direct mocked GenVM tests |
| Time semantics | Before/at/after cutoff, readiness expiry, reassessment/supersession, exact max-wait terminal VOID, timezone-naive rejection | Direct mocked GenVM tests |
| Authorization binding | Wrong consumer, action, spec, digest, assessment ID/version, unbound consumer, provisional/non-READY and expired use | Direct mocked GenVM tests |
| Exact-once action | Finalized consumer callback, wrong sender/proof rejection, replay/idempotent callback, safe retry path, consumed gate cannot be reused | Direct mocked GenVM tests; current StudioNet consumer execution_count=1 |
| Bounds and URL controls | Constructor length/count limits, duplicate criteria/sources, unsafe host/port/userinfo forms | Direct mocked GenVM tests |
| Source/runtime hygiene | Pinned runner, no storage-backed self capture inside nondeterministic closures | GenVM lint/schema and AST regression |

## Live release evidence

The current StudioNet gate and consumer deployments, binding, assessment,
request, gate-consumption child, callback, protocol FINALIZED status, execution
SUCCESS, validator vote observations, and state read-back are listed in
deployments/studionet.json. The assessment reached READY with 3 AGREE and 2
IDLE votes; this is a quorum result and not unanimity.

Mocked tests exercise the prompt boundary but cannot establish prompt-injection
immunity. HTTPS URL validation checks shape/reachability only; it does not prove
publisher authority.
