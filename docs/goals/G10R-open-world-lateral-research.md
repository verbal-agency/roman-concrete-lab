# G10R — Bounded open-world lateral research

**Status:** proposed and optional
**Dependencies:** G09 complete; G10 complete (any verdict); explicit owner activation of a configured source policy
**Advances:** tests whether lawful, bounded retrieval adds useful lateral hypotheses without confusing extra evidence with better orchestration

## Objective

Run a preregistered 2×2 comparison of orchestration and retrieval:

| Arm | Orchestration | Evidence access |
|---|---|---|
| C0 | deterministic control | frozen G09 packet |
| C1 | G10 agent society | frozen G09 packet |
| C2 | deterministic retrieval control | frozen packet plus configured retrieval |
| C3 | G10 agent society | frozen packet plus configured retrieval |

Determine whether C3 produces higher-value lateral hypotheses than C1 after accounting for source novelty, provenance, unsupported claims, cost, latency, and retrieval budget. The result is task-specific and cannot authorize physical work or promote new evidence by itself.

## Entry modes and fixed budget

- `RECORDED_FIXTURES` is mandatory for tests and reproducibility.
- `CONFIGURED_READ_ONLY_NETWORK` is permitted only after the owner activates an allowlist of lawful hosts and records the source-rights policy. No credentials are persisted.
- Each of 8 sealed cases receives 5 repetitions per arm. Deterministic arms must replay identically; agent arms record seed, model/provider, prompt version, tool calls, cost, and latency.
- Each retrieval run is limited to 12 queries, 2 retrieval rounds, 24 source candidates, and 5 MB of metadata/abstract payload. Full text is not stored unless a separately approved rights record permits it.

## In scope

- source-candidate ledger with locator, discovery query, access class, rights state, deduplication key, support region, and status;
- configured retrieval adapter with recorded fixtures and optional read-only network mode;
- the 2×2 factorial controls above using identical case packets, schemas, budgets, and stopping conditions;
- lateral-hypothesis records carrying novelty basis, transfer type, source-candidate IDs, falsifier, uncertainty, and support region;
- source lifecycle, contradiction handling, deduplication, stale-context detection, and cross-problem isolation;
- blind scoring of lateral utility, supported novelty, provenance, unsupported claims, constraint violations, stability, cost, and latency;
- checkpoint/resume, duplicate-query, cache invalidation, source-policy change, network-unavailable, malformed-source, budget-exhaustion, and no-lateral-candidate behavior.

## Excluded

Sci-Hub or access-control bypass, arbitrary open-web autonomy, unrestricted crawling, restricted full-text redistribution, physical execution, recipe invention, safety approval, direct writes to immutable evidence, prompt tuning on sealed cases, and adoption of a general-purpose agent framework.

## Canonical source lifecycle

`DISCOVERED -> METADATA_SCREENED -> CANDIDATE -> EVIDENCE_PENDING -> ADMISSIBLE_FOR_REVIEW`

Terminal or non-promoting states are `REJECTED`, `DUPLICATE`, `RIGHTS_BLOCKED`, `ABSTAIN`, and `UNSUPPORTED`. Agents may create `DISCOVERED`, `CANDIDATE`, and derived-hypothesis records only. A source candidate becomes immutable evidence only through the existing adjudication authority; retrieval does not grant promotion authority.

## Required run state

`created -> source_policy_loaded -> evidence_frozen -> querying -> screening -> proposing -> adjudicating -> scored -> awaiting_review | completed | failed | budget_exhausted`

Terminal states are immutable. A resumed run must verify the source-policy hash, base-packet hash, retrieval budget, and checkpoint before continuing. Replaying a completed run returns its artifact; it does not append a second mutation. A source-policy or context-version change invalidates the cache and requires a new run ID.

## Canonical lateral-hypothesis contract

Each lateral hypothesis contains `hypothesis_id`, `problem_id/version`, `source_candidate_ids`, `novelty_basis`, `transfer_type`, `intervention`, `comparator`, `predicted_observation`, `falsifier`, `support_region`, `evidence_claim_type`, `uncertainty`, `provenance`, and `promotion_status`. Cross-domain analogies must be marked `TRANSFER_HYPOTHESIS` and cannot be scored as Roman-concrete performance evidence.

## Metrics and preregistered decision

Primary metric: blinded lateral-utility score on a 0–4 rubric covering novelty, falsifiability, problem relevance, and discriminating value.

Secondary metrics: supported-novelty rate, provenance completeness, unsupported-claim rate, source deduplication accuracy, contradiction coverage, constraint violations, stability, source yield, cost, and latency.

Adopt only `ADOPT_AGENT_OPEN_WORLD_RETRIEVAL_FOR_LATERAL_QUERY_FORMULATION` if C3 exceeds C1 by at least 0.5 median rubric points with a deterministic-seed bootstrap lower bound above 0, has zero critical rights/safety/provenance violations, provenance completeness is at least 0.95, and unsupported-claim rate is no more than C1 plus 0.02. Otherwise emit `REJECT_AGENT_OPEN_WORLD_RETRIEVAL`. Neither outcome changes scientific or physical authority.

## Expected implementation surface

- `schemas/source-candidate.schema.json` and `schemas/lateral-hypothesis.schema.json`;
- `src/roman_concrete_lab/retrieval/` for allowlist, ledger, deduplication, rights, and replay contracts;
- `src/roman_concrete_lab/agents/retrieval_adapter.py` as a provider/fixture boundary;
- `fixtures/lateral/` covering positive, duplicate, contradictory, rights-blocked, malformed, partial, unsupported, unavailable-network, no-lateral-candidate, and budget cases;
- `docs/protocols/open-world-lateral-research.md`;
- `tests/retrieval/` and `tests/agents/`;
- `artifacts/goals/G10R/run.json` and `artifacts/goals/G10R/report.md`.

Equivalent paths require an amendment before execution. Do not add unrestricted web crawling, hidden caches, or a database/vector store in this goal.

## Authority and side-effect boundaries

Read-only repository access and, only in activated network mode, read-only requests to the recorded host allowlist. No Sci-Hub, paywall bypass, credential persistence, external writes, external messages, lab execution, safety approval, or promotion of source candidates to immutable evidence. Source documents and retrieved text remain untrusted data; embedded instructions are never executable.

## Deterministic behavior matrix

| Condition | Required output |
|---|---|
| Duplicate locator or DOI | `DUPLICATE`, preserve first provenance |
| Rights or host policy failure | `RIGHTS_BLOCKED`, no payload retention |
| Contradictory source records | preserve both, `REVIEW_REQUIRED`, no silent merge |
| Malformed/partial metadata | `REVIEW_REQUIRED` or `ABSTAIN` with missing fields |
| Unsupported transfer to problem context | `TRANSFER_HYPOTHESIS` or `ABSTAIN`; never performance evidence |
| Network unavailable | replayable `NETWORK_UNAVAILABLE`; no fallback to unrecorded sources |
| Retrieval budget exhausted | `BUDGET_EXHAUSTED`; no scope widening |
| No useful lateral candidate | `NO_LATERAL_CANDIDATE` |
| Repeated query/replay | byte-equivalent candidate ledger and policy hash |

## Acceptance criteria

1. All four arms receive byte-identical base cases, equivalent schemas/tools, and the declared budgets; only retrieval access and orchestration treatment differ.
2. Eight sealed cases and five repetitions per arm are frozen before treatment tuning and replay from recorded fixtures.
3. Source-candidate lifecycle, rights policy, deduplication, provenance, and immutable-evidence boundaries pass schema and negative tests.
4. Lateral hypotheses include novelty basis, transfer type, falsifier, support region, source locators, and uncertainty; unsupported transfers cannot become performance evidence.
5. Duplicate, contradictory, rights-blocked, malformed, partial, unsupported, unavailable-network, no-lateral-candidate, and budget fixtures return prescribed statuses.
6. Checkpoint/resume, duplicate-query, cache invalidation, policy-version changes, and cross-problem isolation are deterministic and tested.
7. Metrics and uncertainty are computed from the preregistered blinded rubric without inspecting sealed treatment results during tuning.
8. The report emits exactly one adoption status using the frozen thresholds; adoption cannot grant evidence, safety, or laboratory authority.
9. The run manifest records source-policy hash, retrieval budget, provider/fixture mode, model/tool traces, focus/promotion policy hashes, and all source-candidate mutations.

## Verification evidence

`artifacts/goals/G10R/run.json`, `artifacts/goals/G10R/report.md`, source-candidate and lateral-hypothesis schema validation, fixture replay, blinded scoring record, rights/security scan, and deterministic reproduction log.

## Criterion-to-evidence map

| Criterion | Required evidence |
|---|---|
| 1 | Four-arm manifest showing identical base-packet, schema, tool, budget, and stopping-condition hashes |
| 2 | Sealed-case manifest with 8 cases × 5 repetitions per arm and pre-treatment protocol hash |
| 3 | Source-candidate schema, rights/allowlist tests, deduplication fixtures, and immutable-evidence negative tests |
| 4 | Lateral-hypothesis schema and transfer/unsupported fixture outputs with source locators and falsifiers |
| 5 | Fixture matrix covering every prescribed terminal status in the behavior table |
| 6 | Checkpoint/replay/duplicate/cache-invalidation tests and cross-problem isolation report |
| 7 | Blinded scoring ledger, deterministic bootstrap seed, rubric hash, and metric uncertainty report |
| 8 | Single adoption status in `artifacts/goals/G10R/report.md` plus critical-failure scan |
| 9 | Run manifest containing source-policy, retrieval-budget, provider/fixture, focus/promotion, and mutation hashes |

## Stop conditions

Stop and emit `REJECT_AGENT_OPEN_WORLD_RETRIEVAL` if source rights cannot be established, provenance falls below threshold, any critical fabricated source/measurement/approval appears, the retrieval budget is exhausted without a valid comparison, or the agent action would broaden authority.
