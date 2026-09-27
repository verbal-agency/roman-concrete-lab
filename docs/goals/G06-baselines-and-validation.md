# G06 — Fit baselines and validate prediction with abstention

**Status:** proposed  
**Dependencies:** G05B complete  
**Advances:** determines whether any predictive model is useful beyond simple evidence summaries

## Objective

Fit preregistered simple baselines and, only if justified, a small-data model; evaluate them by held-out study and time; calibrate intervals; define the empirical support region; and issue a model-use verdict.

## In scope

- no-model, study-mean, and simple regularized/hierarchical baselines;
- at most the model families preregistered in G05B;
- nested/grouped model selection with fixed budgets;
- leave-one-study-out and temporal evaluation;
- uncertainty/interval calibration evaluated on held-out studies;
- OOD/support score for mixed numeric/categorical inputs;
- explicit abstention policy;
- study-removal, comparability, feature, and seed sensitivity;
- model cards and rejected-model record.

## Excluded

Neural networks unless explicitly justified by the data card, optimizing the sealed test set, causal claims, unrestricted hyperparameter sweeps, and candidate ranking.

## Behavior matrix

| Condition | Required result |
|---|---|
| model fails primary baseline threshold | reject model; qualitative design only |
| interval coverage fails | no calibrated-uncertainty claim; reject model-based ranking |
| input outside support | abstain; do not return high-confidence prediction |
| unseen category | OOD/abstain |
| single-study dependence | flag instability and fail use gate if threshold exceeded |
| fixed manifest/config/seed | reproducible metrics and predictions |

## Expected implementation surface

`src/roman_concrete_lab/analysis/models.py`, `validation.py`, `support.py`, `tests/analysis/test_models.py`, `docs/reports/model-evaluation.md`, `artifacts/models/` manifests.

## Acceptance criteria

1. All preregistered baselines and only allowed candidate families are evaluated under identical splits.
2. Hyperparameter selection never accesses the sealed test partition and is bounded by the recorded budget.
3. Results report error, interval coverage/width, calibration, support-stratified performance, and abstention rate.
4. OOD, malformed, partial, and unseen-category fixtures trigger documented abstention behavior.
5. Sensitivity analyses identify dependence on individual studies and admissible data decisions.
6. The report emits exactly one verdict: `MODEL_USABLE_IN_DOMAIN`, `EXPLANATORY_ONLY`, or `MODEL_REJECTED` using frozen thresholds.
7. Every released model has a model card, training-manifest hash, environment/version record, and deterministic inference test.

## Verification evidence

`artifacts/goals/G06/report.md`, full metric tables, split hashes, leakage audit, replayed inference fixtures, model/rejection cards, and criterion-to-test map.

## Stop conditions

Do not rescue a failed model by changing metrics, splits, endpoints, or thresholds in place. Any amendment returns to G05B with a dated rationale and preserves the original result.

