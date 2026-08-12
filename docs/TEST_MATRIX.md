# Test matrix

| Requirement | Direct test | Integration evidence |
| --- | --- | --- |
| Adversarial model decision is ignored | Direct mocked GenVM | StudioNet/Bradbury evidence where applicable |
| All-satisfied FINAL vector derives READY | Direct mocked GenVM | StudioNet/Bradbury evidence where applicable |
| One-time readiness consumption | Direct mocked GenVM | StudioNet/Bradbury evidence where applicable |
| Maximum wait derives VOID without consensus | Direct mocked GenVM | StudioNet/Bradbury evidence where applicable |
| Finalized StudioNet deployment and assess transaction | Direct mocked GenVM | StudioNet/Bradbury evidence where applicable |
| Nondeterministic storage isolation | AST closure regression | Receipt inspected for successful execution |
| Public URL controls | Constructor rejection paths | Frozen official GovInfo HTTPS source |
| Prompt injection boundary | Untrusted evidence schema/prompt | Independent validator re-fetch |
| Replay/finality safety | Terminal/idempotent transition checks | Consumers instructed to wait for finality |

StudioNet evidence must show both protocol `FINALIZED` and leader execution `SUCCESS`; a lifecycle label alone is not a passing test. Bradbury evidence records all five deployment hashes before any finality polling.
