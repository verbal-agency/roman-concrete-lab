# GD1 — Conditional discovery loop

**Status:** proposed / blocked until GL2 unlocks  
**Dependencies:** GL2 `SUPPORTED` plus the ratified minimum dataset and independent-batch threshold  
**Advances:** tests whether repeated physical evidence justifies a discovery platform

## Objective

Build the smallest deterministic experiment-selection or explanatory model that uses real, comparable Roman-inspired concrete results and abstains outside the supported domain.

## In scope

- study- and batch-grouped validation;
- explicit baselines and no-model comparisons;
- uncertainty and abstention;
- bounded hypothesis discrimination or experiment selection;
- sensitivity to candidate, batch, exposure, crack, and measurement choices;
- a model-use decision.

## Excluded

Training before GL2, synthetic-data claims presented as material evidence, unconstrained optimization, autonomous lab control, and global “best concrete” ranking.

## Acceptance criteria

1. The minimum data and independence threshold are verified from GL2 artifacts.
2. The model beats or usefully complements a deterministic baseline under held-out batch/study evaluation, or the goal returns `NO_GO`.
3. Predictions include uncertainty and abstain outside the declared support region.
4. Every selected experiment has a measurable rationale and a qualified-lab execution path.
5. The report distinguishes material evidence from model output and states whether the discovery loop is adopted or rejected.

## Verification evidence

Frozen dataset, split manifest, baseline comparison, uncertainty/abstention report, replay tests, and `artifacts/goals/GD1/report.md`.

## Stop conditions

No model or ranker is released if the real-data threshold, held-out validation, or provenance criteria fail.
