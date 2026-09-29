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

## Stop conditions

Stop if the candidate cannot be tested with a functional endpoint, if controls cannot isolate the proposed causal factor, or if safe execution cannot be assessed without expert input.
