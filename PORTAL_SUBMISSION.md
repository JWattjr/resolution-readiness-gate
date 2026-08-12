# GenLayer Portal submission

**Contribution type:** Builder → Intelligent Contracts
**Title:** Resolution Readiness Gate
**Contribution date:** August 12, 2026

## Notes / Description

Built and deployed an MIT-licensed Resolution Readiness Gate that prevents prediction markets from resolving prematurely or being delayed indefinitely. Deployment freezes required criteria, official HTTPS sources, cutoff, maximum wait, and spec ID. Validators independently extract criterion statuses, evidence finality, conflicts/cancellation, coverage, and an official date; the LLM does not choose the gate decision. Deterministic code derives WAIT, READY, VOID, or CONTESTED, and READY can be consumed once by the owner. Before-cutoff assessment stays WAIT, all-source outage fails closed, and max-wait becomes terminal VOID. Includes pinned GenVM source, adversarial decision tests, full schema validation, audit, test matrix, and finalized StudioNet READY consensus evidence. It does not execute payouts.

## Evidence to add

1. GitHub Repository — https://github.com/JWattjr/resolution-readiness-gate
2. GitHub File — https://github.com/JWattjr/resolution-readiness-gate/blob/main/contracts/ResolutionReadinessGate.py
3. GitHub File — https://github.com/JWattjr/resolution-readiness-gate/blob/main/tests/test_readiness_gate.py
4. GitHub File — https://github.com/JWattjr/resolution-readiness-gate/blob/main/docs/SECURITY_AUDIT.md
5. GitHub File — https://github.com/JWattjr/resolution-readiness-gate/blob/main/docs/TEST_MATRIX.md
6. GitHub File — https://github.com/JWattjr/resolution-readiness-gate/blob/main/deployments/studionet.json
7. GitHub File — https://github.com/JWattjr/resolution-readiness-gate/blob/main/deployments/bradbury.json
8. GenLayer Explorer Contract — https://explorer-bradbury.genlayer.com/address/0x14422853944268a400a15B76EC733383d625A542

The repository is private. Grant Portal reviewers repository access before submission.
