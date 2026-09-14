# GenLayer Portal submission

Contribution type: Builder → Intelligent Contracts
Title: Resolution Readiness Gate
Release source: ae1916cd447d2e9f8ed6e4f29e2107bec3fce40f
Network: StudioNet (fresh deployment; Bradbury records are historical only)

## Portal description (under 1,000 characters)

Resolution Readiness Gate is a reusable GenLayer primitive for evidence-backed downstream decisions. A frozen specification binds criteria, public sources, UTC timing, a spec hash, and an action digest. Validators independently retrieve untrusted evidence; strict canonicalization rejects missing/extra fields, invalid types, unknown criteria, duplicate references, and inconsistent decisions. Deterministic code derives WAIT, READY, VOID, or CONTESTED. Partial/truncated evidence is marked but can support READY when available facts suffice; otherwise it stays WAIT. A bound consumer may consume only an unexpired, protocol-finalized READY assessment for the exact spec/action; the callback is single-use and idempotent. StudioNet reached READY (3 AGREE, 2 IDLE), then executed the bound action exactly once. HTTPS is not authority proof and prompt-injection immunity is not guaranteed. No funds or payouts.

## Evidence links

- Repository: https://github.com/JWattjr/resolution-readiness-gate
- Current gate source: https://github.com/JWattjr/resolution-readiness-gate/blob/main/contracts/ResolutionReadinessGate.py
- Bound consumer source: https://github.com/JWattjr/resolution-readiness-gate/blob/main/contracts/ResolutionReadinessConsumer.py
- Behavioral tests: https://github.com/JWattjr/resolution-readiness-gate/blob/main/tests/test_readiness_gate.py
- Audit: https://github.com/JWattjr/resolution-readiness-gate/blob/main/docs/SECURITY_AUDIT.md
- Test matrix: https://github.com/JWattjr/resolution-readiness-gate/blob/main/docs/TEST_MATRIX.md
- Security model: https://github.com/JWattjr/resolution-readiness-gate/blob/main/docs/SECURITY.md
- Current StudioNet manifest: https://github.com/JWattjr/resolution-readiness-gate/blob/main/deployments/studionet.json
- Source commit: https://github.com/JWattjr/resolution-readiness-gate/commit/ae1916cd447d2e9f8ed6e4f29e2107bec3fce40f
- Gate explorer: https://explorer-studio.genlayer.com/contracts/0xa8Be5185b1fa8F4aE2CadF924A5F5dBCD429fBb5
- Consumer explorer: https://explorer-studio.genlayer.com/contracts/0x2394879de943F3E89BD18d9e48991cD543786954
- Gate deployment: https://explorer-studio.genlayer.com/transactions/0x4c2cac2a4bf8ea624e57b75b6527c9f9d6247033b0ea0c55bf2a63ada83e57e4
- Consumer deployment: https://explorer-studio.genlayer.com/transactions/0x3ba626a89e1a207caa5d7ca40333e03b9f3522be56c85b427479331b49201ab8
- Consumer binding: https://explorer-studio.genlayer.com/transactions/0xa9fc9682b47b7e8b8dd92c9b1fda0ae1e1c3e689026b04c2a6150a552325b489
- Final assessment: https://explorer-studio.genlayer.com/transactions/0x0911ef9df300b6b1041b2c33c5711d9fcc4e86667cfde94fb52f841106b2abc3
- Consumer request: https://explorer-studio.genlayer.com/transactions/0x226ef2652134dd513c1dc397699bdbbb348b772f45a8eb4902fb1915bfc3b541
- Gate consumption: https://explorer-studio.genlayer.com/transactions/0x9f6adf4f5e55b427b6fe7fb63d327d3bb49a3d4ae096b897a7a521667db3b652
- Consumer callback proof: https://explorer-studio.genlayer.com/transactions/0x2871c6bfd940a5eb2ab2bb2379dc81abb48557894c82d57553fa7eeead691a9a
- Authoritative source: https://www.govinfo.gov/app/details/PLAW-117publ58/summary

The links above are the exact current-source evidence. deployments/bradbury.json
and deployments/studionet-20260812-historical.json are retained as historical
records and must not be presented as current deployment proof.

## Submission gate

Post-push anonymous HEAD checks on 2026-09-14 returned 404 for the repository
and every GitHub file/commit URL. Make the repository publicly readable (or
provide an anonymous read URL), then re-run the checks before Portal submission.
A 200 response alone does not prove a transaction succeeded; use the current
manifest's separate protocol-finality and execution fields. Repository
visibility is the exact remaining blocker.
