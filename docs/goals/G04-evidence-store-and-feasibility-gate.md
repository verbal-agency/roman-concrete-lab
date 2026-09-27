# G04 — Ingest evidence and issue the feasibility verdict

**Status:** proposed  
**Dependencies:** G03 permits a reviewed extraction workflow  
**Advances:** determines whether predictive modeling is scientifically supportable

## Objective

Implement deterministic, replayable ingestion for the eligible corpus, build the minimal evidence store and query layer, and issue the preregistered NO-GO/LIMITED/GO verdict defined in the program.

## In scope

- idempotent ingestion with checkpoints, resumability, duplicate detection, and content-addressed lineage;
- a minimal relational/file-backed store justified by actual scale and queries;
- review queue enforcing the G03 policy;
- queries for source-to-measurement lineage, contradictions, missingness, study independence, controls, outcomes, and protocol comparability;
- feasibility metrics and sensitivity to admissible comparability decisions;
- immutable evidence snapshot and feasibility report.

## Excluded

Predictive modeling, candidate optimization, vector search, graph database, agent orchestration, and resolving scientific contradictions by majority vote.

## Stateful behavior

- Duplicate call with identical source/version: no duplicate records; returns prior ingestion ID.
- Same source ID with changed content: creates a new version and invalidates derived artifacts transitively.
- Interrupted run: resumes from the last committed source without partial records.
- Budget exhaustion: stops cleanly with pending items and no gate verdict until required review is complete.
- Schema mismatch: quarantines the record and fails the snapshot build.
- Source removal/licensing change: tombstones availability while preserving the provenance record; derived release policy is reevaluated.

## Expected implementation surface

`src/roman_concrete_lab/evidence/`, migrations or versioned store schema, `tests/evidence/`, `data/processed/evidence-snapshot.*`, `docs/reports/feasibility-gate.md`.

## Acceptance criteria

1. Ingestion is idempotent, resumable, schema-validated, and tested for duplicate, contradiction, malformed, partial-failure, budget-exhaustion, and invalidation cases.
2. Every released measurement can be traced to a source locator and every transformation to its parents.
3. Store counts reconcile with the corpus, extraction, exclusion, quarantine, and review ledgers.
4. The evidence snapshot is immutable and identified by manifest plus content hash.
5. Feasibility metrics implement the frozen thresholds without post-hoc relaxation.
6. The report emits exactly one verdict—NO-GO, LIMITED, or GO—with criterion-level evidence and sensitivity analysis.
7. The roadmap branch is updated without starting its next goal.

## Verification evidence

`artifacts/goals/G04/report.md`, snapshot manifest/hash, replay and recovery tests, reconciliation report, gate calculator output, and signed scientific review of comparability assumptions.

## Stop conditions

No verdict may issue while mandatory extraction review, lineage deduplication, or licensing classification is incomplete. NO-GO completes this goal successfully and makes G05A the only eligible next goal.

