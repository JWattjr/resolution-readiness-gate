# Resolution Readiness Gate

A standalone GenLayer Intelligent Contract that prevents prediction markets from resolving too early or being delayed forever.

## GenLayer-native decision

Validators independently extract criterion statuses, evidence finality, conflict/cancellation state, coverage, and an official date. Contract code alone derives WAIT, READY, VOID, or CONTESTED.

## Lifecycle and API

`ARMED → WAIT/CONTESTED/READY/VOID`; READY can be consumed once by the owner. Cutoff and max-wait checks are deterministic and happen without web/LLM calls.

Constructor: `gate_id, event_description, criteria, sources, cutoff, max_wait, spec_id`. Public methods: `assess()`, `consume_ready()`, `can_resolve()`, and `get_state()`.

Every evidence URL is frozen, bounded, public HTTPS. Fetched text is untrusted input; prompts instruct validators to ignore embedded commands. Leader and validator closures snapshot ordinary values and independently re-fetch evidence.

## Live evidence

- [StudioNet contract](https://explorer-studio.genlayer.com/address/0x76A7141d99e5abbDB737BFE672001F429bF654B7)
- [Bradbury contract](https://explorer-bradbury.genlayer.com/address/0x14422853944268a400a15B76EC733383d625A542)
- Exact StudioNet transaction hashes, constructor arguments, state, and execution results are in `deployments/studionet.json`.

## Verify

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/ResolutionReadinessGate.py
python -m pytest tests -q
```

The contract uses a concrete pinned GenVM runner. See `docs/SECURITY_AUDIT.md`, `docs/TEST_MATRIX.md`, and `PORTAL_SUBMISSION.md` for reviewer evidence. This primitive does not custody funds; consumers must wait for GenLayer finality and remain idempotent.
