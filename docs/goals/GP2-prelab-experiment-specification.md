# GP2 — Pre-lab experiment specification

**Status:** proposed  
**Dependencies:** GP1 complete  
**Advances:** produces a reviewable study package without pretending that a repository document is a laboratory authorization

## Objective

Translate the strongest candidate dossier into a problem-specific provisional ranking and a draft study specification that lets a qualified facility judge feasibility, cost, safety, and scientific value.

## In scope

- candidate and process-matched control matrix;
- primary functional endpoint and secondary measurements;
- crack/damage definition, exposure, timepoints, specimen grouping, batching, randomization, and replicate rationale;
- hypotheses-to-observation decision table;
- data dictionary, provenance fields, missingness, censoring, and negative-result handling;
- analysis plan and candidate decision rules;
- provisional ranking of performance, information value, feasibility, and risk as separate dimensions;
- declared utility function, support region, uncertainty, and abstention conditions for any `PROVISIONAL_BEST` label;
- explicit unknowns for materials, equipment, cost, and safety.

## Excluded

Physical execution, unreviewed hazardous procedures, invented cost or safety values, optimization, and claims of validated performance.

## Acceptance criteria

1. The package names one primary functional endpoint and does not substitute surface crack closure for functional recovery; exploratory-only endpoints are labeled as such.
2. Every treatment condition has a process-matched comparator and a reason for inclusion.
3. Every rival hypothesis maps to at least one distinguishable observation or is labeled unresolved.
4. Specimen-level identifiers, batch lineage, measurement units, uncertainty, and exact source/protocol provenance are defined before any data are collected.
5. The package is watermarked `DRAFT — EXPERT REVIEW REQUIRED` and contains no unapproved physical execution instruction.
6. A deterministic decision table maps positive, null, contradictory, incomplete, and unsafe outcomes to `SUPPORTED`, `NARROW_USE_CASE`, `INCONCLUSIVE`, or `NOT_REPRODUCED`.
7. Any provisional ranking is conditional on the declared problem, utility, and support region; it emits uncertainty and abstains when those conditions are not met.

## Expected implementation surface

`docs/protocols/prelab-study-specification.md`, `schemas/prelab-result.schema.json`, `fixtures/prelab/`, `tests/prelab/`, `artifacts/goals/GP2/`.

## Authority boundaries

The package may be handed to a qualified facility for review, but no external message, purchase, physical execution, or safety approval is implied.

## Verification evidence

Protocol completeness checklist, schema validation, decision-matrix tests, and `artifacts/goals/GP2/report.md`.

## Execution contract

### Expected implementation surface

- `docs/protocols/prelab-study-specification.md` — one Roman-concrete draft study package, watermarked `DRAFT — EXPERT REVIEW REQUIRED`;
- `schemas/prelab-result.schema.json` — versioned specimen/batch/result contract;
- `fixtures/prelab/positive.json`, `null.json`, `contradictory.json`, `incomplete.json`, and `unsafe.json` — offline decision fixtures;
- `tests/prelab/test_specification.py` — schema, watermark, transition, and decision-matrix tests;
- `artifacts/goals/GP2/run.json` and `artifacts/goals/GP2/report.md` — hashes, replay command, criterion evidence, and stop decision.

Equivalent paths require an amendment to this goal before implementation.

### Canonical contract and invariants

The study package must consume one approved G00 context version and GP1 candidate/hypothesis IDs. Each proposed condition has `condition_id`, candidate/process reference, process-matched comparator, batch/specimen lineage, primary endpoint, secondary endpoint, units, timepoints, uncertainty/missingness semantics, source/protocol locators, and review status. Result statuses are `SUPPORTED`, `NARROW_USE_CASE`, `INCONCLUSIVE`, or `NOT_REPRODUCED`; unsafe or unreviewable conditions remain `REVIEW_REQUIRED` and cannot become a result.

Illegal states include a missing comparator, a surface-closure result substituted for the primary functional endpoint, an invented formulation value, an unwatermarked protocol, or a physical authorization implied by a document artifact. No field may convert `NOT_REPORTED` into zero.

### Deterministic behavior matrix

| Fixture/input | Required output |
|---|---|
| Complete condition, comparator, endpoint, and declared utility | Conditional `PROVISIONAL_BEST` or `PARETO_SET` with uncertainty and support region |
| Missing comparator, primary endpoint, or utility | `ABSTAIN` / `REVIEW_REQUIRED` with named missing field |
| Positive returned result | `SUPPORTED` only if all preregistered controls and provenance fields pass |
| Null or contradictory result | `INCONCLUSIVE` with preserved conflicting observations |
| Incomplete or censored result | `INCONCLUSIVE` / `REVIEW_REQUIRED`; never impute a measured value |
| Unsafe or facility-unassessed condition | `REVIEW_REQUIRED`; no execution instruction or approval |

### Authority, replay, and budget boundaries

GP2 may read repository artifacts and use offline fixtures. It may not browse, call an LLM, contact a partner, purchase materials, execute a lab, approve safety, or infer an unreported recipe. The output is a draft for expert review only. The run must record context/ledger hashes, a deterministic tie-break rule, a fixed local budget, and a replay command; duplicate replay must produce byte-equivalent statuses and ranking inputs. Any budget exhaustion terminates with `BUDGET_EXHAUSTED` and preserves partial evidence rather than silently widening scope.

### Criterion-to-test map

`tests/prelab/test_specification.py` must cover: primary-endpoint enforcement; process-matched comparator validation; rival-hypothesis observation mapping; specimen/batch/provenance fields; required watermark and no-authorization language; positive/null/contradictory/incomplete/unsafe transitions; conditional ranking and abstention; deterministic replay; duplicate-call behavior; and budget exhaustion.

## Stop conditions

Stop if the candidate cannot be tested with a functional endpoint, if controls cannot isolate the proposed causal factor, or if safe execution cannot be assessed without expert input.
