# GL2 — Replication result ingestion

**Status:** proposed  
**Dependencies:** GL1 approved; qualified facility returns the agreed dataset  
**Advances:** converts physical results into a reproducible candidate decision

## Objective

Ingest, validate, and interpret the first controlled study without overstating a single experiment as a general material law.

## In scope

- raw-data manifest and checksum capture;
- specimen/batch/protocol lineage validation;
- missingness, exclusions, censoring, and instrument QC;
- predefined primary and secondary analyses;
- replication decision: `SUPPORTED`, `NARROW_USE_CASE`, `INCONCLUSIVE`, or `NOT_REPRODUCED`;
- report of deviations and next evidence required.

## Excluded

Post-hoc endpoint substitution, hidden data repair, global optimization, or model-driven discovery without the ratified data threshold.

## Acceptance criteria

1. Every released observation traces to a specimen, batch, instrument, source file, and protocol version.
2. Primary analysis runs from a frozen manifest and preserves null and failed observations.
3. The result decision follows the GP2 matrix exactly; no favorable subgroup is promoted without a preregistered rule.
4. The report distinguishes reproducibility, mechanism evidence, and application relevance.
5. The next branch is selected deterministically: stop, revise candidate, or unlock GD1 only if the ratified threshold passes.

## Verification evidence

Immutable result manifest, validation report, analysis replay, decision artifact, and `artifacts/goals/GL2/report.md`.

## Stop conditions

Incomplete raw data, untraceable specimens, failed controls, missing safety documentation, or non-comparable measurements produce `INCONCLUSIVE` or `NOT_REPRODUCED`; they do not unlock GD1.
