# G10R-Y — Diagnose the post-wiring paid comparison

**Status:** complete — `POST_V_DIAGNOSIS_READY`
**Dependencies:** G10R-V complete with `DO_NOT_ESCALATE_ACTIVE_SOCIETY`,
`artifacts/goals/G10R-V/run.json`, `replay.json`, `report.md`, and
`spend-ledger.json`
**Authority:** offline repository/artifact analysis only; no model, network,
subscription, credential, laboratory, or external communication

## Objective

Determine why the post-wiring A1 versus A2-M comparison produced no qualifying
society contribution, separating agent-design weakness from information-
acquisition conversion, task/fixture reachability, attribution/scoring, and
runtime overhead. Preserve useful unresolved candidates and hypotheses while
identifying the smallest offline interventions that could make a future test
informative.

## Required work

- reconstruct all eight completed case/arm traces from G10R-V;
- compare raw discovery/hypothesis material with source-backed rubric credit;
- measure candidate identity, fetch/evidence-card yield, attribution joins,
  support-task completion, focus/open-slot behavior, and budget overhead;
- determine whether A2-M used the intended viewpoint/support topology and where
  value was lost relative to A1;
- run deterministic offline ablations or fixtures for each high-severity cause;
- produce a ranked remediation set and a falsifiable rule for whether another
  paid run is justified.

## Deliverables

- `artifacts/goals/G10R-Y/diagnosis.json`;
- `artifacts/goals/G10R-Y/ablation-matrix.json`;
- `artifacts/goals/G10R-Y/replay.json`;
- `artifacts/goals/G10R-Y/report.md` with one of
  `POST_V_DIAGNOSIS_READY`, `POST_V_DIAGNOSIS_NO_GO`, or
  `INCONCLUSIVE_POST_V_DIAGNOSIS`.

## Acceptance criteria

1. Every case/arm has an evidence-located loss ledger covering acquisition,
   topology, attribution, scoring, and cost.
2. Raw candidate/hypothesis generation is not discarded merely because it did
   not earn evidence credit; unsupported and unresolved records remain typed.
3. At least one offline experiment distinguishes an agent-design defect from
   a plumbing or rubric conversion defect.
4. The proposed next treatment has measurable thresholds for unique attributable
   contribution, evidence-card yield, attribution completeness, and budget
   parity, plus an explicit stop rule.
5. Replay is deterministic and makes no external calls.

No result from this goal authorizes evidence promotion, lab work, or another
paid run by itself.

## Completion evidence

- `artifacts/goals/G10R-Y/diagnosis.json` reconstructs all eight case/arm
  traces and records the ranked remediations and next-treatment thresholds.
- `artifacts/goals/G10R-Y/ablation-matrix.json` separates shared content
  headroom from the independent open-slot/readiness-fixture false positive.
- `artifacts/goals/G10R-Y/replay.json` is deterministic, external-free, and
  confirms that all historical G10R-V artifacts remained unchanged.
- `artifacts/goals/G10R-Y/criterion-ledger.json` maps all five acceptance
  criteria to passing tests and artifacts.
- The handoff routes only to G10R-Z, an offline repair gate.
