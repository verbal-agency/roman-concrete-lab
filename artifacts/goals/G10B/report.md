# G10B real-model agent-society signal pilot report

**Status:** complete
**Decision:** `DO_NOT_ESCALATE_AGENT_SOCIETY`
**Protocol:** `g10b.1-signal-pilot`
**Provider:** `gpt-6-luna` via the OpenAI Responses API
**Execution:** 4 sealed cases; C1 single analyst, three independent C4-lite roles, and one C4-lite adjudicator per case; 20 treatment calls

## Result

The configured-provider pilot completed without an evaluation failure. C1 and C4-lite both scored 19/20 total on the frozen deterministic rubric, with zero case-level score deltas. C4-lite produced distinguishable role outputs on all four cases (`role_output_distinct_count = 3` for each), but it introduced no supported distinct prediction or discriminator absent from C1. There were no critical provenance, safety, authority, or invalid-evidence failures.

The preregistered escalation rule therefore does not pass: the society did not beat C1 on any sealed case, did not produce a qualifying supported distinct increment, and does not justify a larger G10C factorial evaluation. This is a decision not to fund the next agent-society experiment under this protocol—not a universal rejection of agent societies and not a production-adoption decision. The authoritative workflow remains the non-agent G09 release.

## Execution and cost

| Measure | Result |
|---|---:|
| Sealed cases | 4 |
| Completed treatment calls | 20 |
| Estimated actual cost | $0.00946470 |
| Hard estimated-cost cap | $25.00 |
| Critical failures | 0 |
| C1 total | 19/20 |
| C4-lite total | 19/20 |
| Case deltas | 0, 0, 0, 0 |

The provider ran with `reasoning.effort=low`, `store=false`, no tools, no retrieval, and the frozen structured-output schema. The checkpoint contains 20 replayable traces and no credential material. The arm map is stored separately from blinded scores and is hashed in `run.json`.

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. Freeze and hash Phase A before treatment | **PASS** | `artifacts/goals/G10B/phase-a.json`; protocol, prompts, schema, runner/provider, and case hashes; C0 headroom is nonzero |
| 2. Identical evidence, schema, aggregate budget, tools, stopping, and authority | **PASS** | `docs/protocols/g10b-real-model-ablation.md`; `run.json` authority and arm records |
| 3. Four sealed cases and 20 calls under the cap | **PASS** | `run.json` (`COMPLETED`, 20 calls, $0.00946470); `live/checkpoint.json` (20 traces) |
| 4. Distinguishable role behavior | **PASS** | Each sealed record reports three distinct role-output digests |
| 5. Blind deterministic scoring and separate arm map | **PASS** | `run.json` blinded scores, rubric hits, arm-map hash; no model judge was used |
| 6. Typed/replay-safe state boundaries | **PASS** | G10 replay contracts plus `tests/agents/test_replay.py` and checkpoint/resume tests |
| 7. Failure, malformed, duplicate, stale, replay, and budget coverage | **PASS** | `tests/agents/test_g10b_pilot.py`, `tests/agents/test_replay.py` |
| 8. Bounded focus/promotion behavior | **PASS** | G10 replay artifacts and protocol authority rules; no consensus promotion is permitted |
| 9. Exactly one preregistered decision | **PASS** | This report and `run.json` emit only `DO_NOT_ESCALATE_AGENT_SOCIETY` |
| 10. No authority expansion | **PASS** | `run.json` authority block; no lab, source, safety, external-communication, or evidence-write authority |

## Limitations and routing

- This was a directional four-case pilot, not an adoption-grade factorial evaluation. It does not test repeated seeds, C2/C3 layer ablations, broader case classes, model judges, or open-world retrieval.
- The null result is task- and protocol-scoped. It does not prove that agent societies cannot help on other tasks, models, prompts, or evidence regimes.
- No G10C is activated. Any future reconsideration should use a separately frozen protocol and new sealed cases; it must not reuse this run as positive evidence.
- G10R remains a separate, optional lawful-retrieval evaluation. G11 remains the expert-review gate for any capability that is later adopted.
