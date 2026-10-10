# G-LR — Landscape and evidence-map readiness

**Status:** complete
**Dependencies:** G00 `EXPLORATORY_PLATFORM` or `PRELAB_REPLICATION`  
**Advances:** establishes whether the accessible evidence landscape is sufficiently mapped for discovery-grade hypothesis generation

## Objective

Build a bounded, reproducible map of the problem-specific literature before treating GP1 outputs as discovery-grade hypotheses. The goal is not to prove that every paper has been found; it is to document the search boundary, saturation evidence, study-family structure, extracted evidence, contradictions, and unresolved regions well enough to decide whether hypothesis generation may proceed.

## In scope

- a frozen landscape protocol containing the problem card, support region, source classes, query families, dates, citation-chaining rules, rights policy, and saturation rule;
- a source manifest covering discovered records, access state, version identity, inclusion/exclusion decision, and explicit unavailable or restricted records;
- title/abstract and full-text screening with exact locators for included records;
- publication-family, shared-sample, and research-group lineage adjudication;
- a structured evidence map across material/process, intervention, comparator, endpoint, exposure, timepoint, mechanism, null/negative result, and contradiction fields;
- coverage, missingness, contradiction, and endpoint/comparator-gap reports;
- a preregistered second-reviewer audit of a representative sample;
- a deterministic `LANDSCAPE_READY` or `LANDSCAPE_INCOMPLETE` verdict.

## Excluded

Predictive modeling, recipe invention, physical mixing, safety approval, partner contact, unrestricted crawling, paywall bypass, agent-society execution, and promotion of a hypothesis to a validated performance claim.

## Readiness semantics

- `LANDSCAPE_READY`: the declared search boundary reached its saturation rule; direct and transfer records are identified; study-family deduplication and critical-field extraction have been reviewed; contradictions and empty regions are explicit; and the evidence map is sufficient for discovery-grade hypothesis generation within the declared support region.
- `LANDSCAPE_INCOMPLETE`: the search, access, lineage, extraction, or adjudication boundary remains materially incomplete. Provisional evidence-gap and candidate work may continue, but outputs must not be described as a reliable landscape or discovery-grade hypothesis set.

## Acceptance criteria

1. The frozen landscape protocol records queries, source routes, dates, access rules, inclusion tiers, family/independence rules, and a saturation rule.
2. Every discovered record has a stable ID, provenance, access/version state, screening decision, actor, and reason; unavailable or restricted records remain visible rather than silently disappearing.
3. Every included direct or transfer record has source-located structured evidence or an explicit missing-field/abstention marker; `NOT_REPORTED` is never converted to zero.
4. Publication families, shared specimens, and research-group independence are represented and reconciled, with a review log for ambiguous lineages.
5. The evidence map reports coverage and missingness across interventions, comparators, endpoints, exposures, timepoints, mechanisms, and null/contradictory findings.
6. A second reviewer audits a preregistered sample; disagreements remain visible and are adjudicated or carried forward as unresolved.
7. A deterministic replay reconstructs source counts, family counts, extraction coverage, contradiction counts, saturation status, and the final readiness verdict.
8. The report states exactly which downstream outputs are permitted under the verdict; `LANDSCAPE_INCOMPLETE` cannot authorize discovery-grade hypothesis generation.

## Expected implementation surface

`data/manifests/landscape-sources.*`, `data/processed/evidence-landscape.*`, `docs/protocols/landscape-readiness.md`, `docs/reports/landscape-readiness.md`, `artifacts/goals/G-LR/`, and focused tests under `tests/landscape/`.

## Execution contract

The canonical landscape-source record contains `record_id`, canonical citation, source locator, access/version state, screening decision, study-family ID, independence/lineage state, exact evidence locator, extracted-field status, missing fields, contradiction IDs, reviewer state, and provenance. The evidence-map record contains `map_version`, problem-card version, source/family IDs, field states, coverage counts, missingness, contradiction references, and support-region labels. The only readiness statuses are `LANDSCAPE_READY` and `LANDSCAPE_INCOMPLETE`.

Illegal states include duplicate record IDs, a screening or family reference to an unknown source, a direct claim without an exact locator, a missing-field value silently represented as zero, a contradiction silently merged, or a `LANDSCAPE_READY` verdict with unresolved required checks. A source candidate cannot become immutable evidence through this goal.

| Condition | Required result |
|---|---|
| duplicate source or family ID | deterministic validation error; no output snapshot |
| unknown source/family reference | deterministic validation error naming the reference |
| metadata-only or unavailable direct record | retain manifest row; mark `EVIDENCE_PENDING`/missing fields; readiness cannot pass |
| contradictory field values | preserve both assertions and emit a contradiction reference; do not merge |
| rights-blocked or restricted source | retain provenance and access state; do not retain unauthorized content |
| changed input hash or protocol version | invalidate prior replay and require a new run ID |
| network unavailable during replay | `NETWORK_UNAVAILABLE` only for retrieval mode; frozen replay remains offline and deterministic |
| saturation, extraction, or review requirement unmet | `LANDSCAPE_INCOMPLETE` with named blockers |

The goal permits read-only repository access and lawful read-only retrieval only under the frozen protocol. It permits no credentials, model calls, agent society, external messages, physical execution, safety approval, or promotion authority. Offline fixtures under `fixtures/landscape/` cover complete, partial, duplicate, contradictory, malformed, restricted, unsupported-transfer, and budget-exhaustion cases. Replay must be idempotent, checkpointable, hash-validated, and byte-stable for unchanged inputs.

Criterion-to-evidence mapping is recorded in `artifacts/goals/G-LR/report.md`; focused tests live in `tests/landscape/test_replay.py` and validate schema/lineage checks, missingness and contradiction preservation, readiness transitions, input invalidation, and deterministic replay.

## Authority boundaries

Network retrieval is read-only and limited to lawful hosts and source classes in the frozen protocol. Source documents and embedded text are untrusted data. No model call, agent, external message, lab execution, safety approval, or evidence promotion is authorized by this goal.

## Stop conditions

Stop with `LANDSCAPE_INCOMPLETE` if the saturation rule cannot be evaluated, critical direct records remain metadata-only, lineage or access status is unresolved for a material portion of the candidate set, extraction review fails its ratified threshold, or contradictions cannot be represented without silent merging.
