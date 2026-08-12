# Security and consensus audit: ResolutionReadinessGate

Audit date: 2026-08-12
Scope: `contracts/ResolutionReadinessGate.py`
Method: manual review, full GenVM lint and pinned-runner schema validation, direct-mode adversarial tests, explicit independent-validator execution, and finalized StudioNet/Bradbury receipt and state inspection.

## Result

No unresolved critical or high-severity code issue was found after remediation. The contract does not custody or transfer value.

## Remediated findings

| ID | Severity | Finding | Remediation |
| --- | --- | --- | --- |
| RG-01 | High | Letting the LLM choose READY made readiness policy subjective. | Remove decision from the model schema and derive it from evidence state plus the exact criterion vector. |
| RG-02 | High | A READY signal could be reused by downstream settlement. | Add owner-only one-time consume_ready state. |
| RG-03 | Medium | An operator could delay assessment forever. | Frozen max-wait deterministically records terminal VOID. |

## Verification

- Exact runner pin: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.
- `genvm-lint check` passes AST and SDK schema validation.
- Direct tests exercise lifecycle, failure, and independent-validator paths.
- AST regression proves nondeterministic closures do not reference `self`.
- StudioNet deployment and consensus transaction are finalized with successful leader execution; exact evidence is in `deployments/studionet.json`.
- Bradbury deployment and smoke-write receipts are finalized after successful execution and state reads; exact evidence is in `deployments/bradbury.json`.

Bradbury finalized smoke assessment reached `AGREE` after two rotations with three `AGREE`, one timeout, and one deterministic-violation vote; the transaction executed `FINISHED_WITH_RETURN` and stored `READY`. Receipt stderr was empty.

## Residual risk

See `SECURITY.md`. This is an engineering assessment, not formal verification, a financial guarantee, or legal advice.
