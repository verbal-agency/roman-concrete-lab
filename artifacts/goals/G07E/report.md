# G07E cycle report — complete

**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; deterministic tournament MVP implemented and replayed offline
**Execution date:** 2026-09-30

## Outcome

G07E converts the GP4 problem-card substrate into a bounded tournament loop: typed hypotheses are proposed from scoped card memory, critiqued against a process-matched comparator, adjudicated with separate qualitative utility dimensions, focused under a local budget, and retained or transitioned under an append-only policy. Roman concrete now has two explicit rival hypotheses; the lime-mortar and battery-cathode cards run through the same contracts without cross-domain scoring.

This is a discovery-platform capability, not a material-performance result. The output is a replayable `PARETO_SET` or a prescribed abstention/review terminal state plus draft, non-authorizing experiment questions.

## Acceptance criteria

| Criterion | Result | Evidence |
|---|---|---|
| 1. Typed registry and frozen-manifest replay | **PASS** | `schemas/hypothesis-registry.schema.json`; three card replays; Roman emits two explicit rivals |
| 2. Memory-tier permissions and provenance | **PASS** | `MemoryStore` permission tests; hypotheses retain evidence IDs and source locators |
| 3. Versioned focus/promotion policy and legal transitions | **PASS** | policy version/hash in run manifest; transition tests cover review, abstention, retraction, and context amendment |
| 4. Separate utilities and Pareto output | **PASS** | result schema; no aggregate score; all normal card runs emit `PARETO_SET` |
| 5. Required edge cases | **PASS** | eight sealed fixtures cover positive, contradictory, malformed, partial, unsupported, unsafe, no-feasible, and budget exhaustion |
| 6. No unvalidated EIG/model | **PASS** | no numeric EIG or predictive-model field; explicit test assertion and manifest flag |
| 7. Cross-card contract reuse | **PASS** | Roman, lime-mortar, and battery-cathode runs preserve distinct domains/support regions/endpoints |

## Fixture outcomes

| Fixture | Output |
|---|---|
| positive | `PARETO_SET` |
| contradictory | `REVIEW_REQUIRED` |
| malformed | `REVIEW_REQUIRED` |
| partial | `REVIEW_REQUIRED` |
| unsupported | `ABSTAIN` |
| unsafe | `UNSAFE_REJECTED` |
| no-feasible | `NO_FEASIBLE_CANDIDATE` |
| budget-exhaustion | `BUDGET_EXHAUSTED` |

## Verification

- `python3 tools/tournament/replay.py` — pass; all fixture expectations match.
- `python3 -m pytest -q` — **26 passed**.
- `git diff --check` — pass.
- Cache policy is explicit: no mutable cache is used; card, evidence-manifest, and policy digests define replay identity.
- No network, LLM, agent runtime, subprocess execution from retrieved content, external communication, lab execution, or immutable-evidence mutation occurred.

## Limitations and routed work

- The tournament uses ordinal qualitative utilities and deliberately does not estimate predictive performance or numeric information gain. Numeric EIG remains a future goal only if validated distributions become available.
- Agent society, shared-memory multi-agent orchestration, G09 release packaging, and physical validation remain later roadmap goals; none is silently included here.
- Recommendations are draft, non-authorizing experiment questions and require later qualified review before any physical work.
