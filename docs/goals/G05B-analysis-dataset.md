# G05B — Freeze the analysis dataset and validation plan

**Status:** proposed  
**Entry gate:** G04 verdict is LIMITED or GO  
**Dependencies:** G04 complete  
**Advances:** creates a leakage-resistant analytical view without erasing study structure

## Objective

Transform the immutable evidence snapshot into a versioned analysis dataset, feature dictionary, and preregistered split/metric plan suitable for honest grouped and temporal evaluation.

## In scope

- one explicit analysis unit (normally experimental arm or treatment-control contrast);
- endpoint harmonization with documented comparability classes;
- treatment/control pairing and effect-size construction where defensible;
- core covariates, categorical levels, missingness indicators, and support ranges;
- grouped study/material-lineage splits and temporal availability split;
- training-only transformation pipeline;
- dataset card, exclusion ledger, and immutable manifest;
- leakage tests and baseline metric thresholds fixed before G06.

## Excluded

Model selection, global imputation, row-random splitting, use of the sealed evaluation packet for design choices, and forced harmonization of incomparable endpoints.

## Required invariants

- repeated specimens/timepoints do not become independent experimental arms;
- no source/sample family crosses grouped split boundaries;
- transformations and imputation learn only from training folds;
- missing values are not converted to absence/zero;
- every feature has unit, semantics, allowed range, and derivation lineage;
- categorical levels appearing only in holdout remain unknown/OOD rather than leaked into training.

## Expected implementation surface

`src/roman_concrete_lab/analysis/dataset.py`, `src/roman_concrete_lab/analysis/splits.py`, `tests/analysis/`, `data/processed/analysis-v1.*`, `docs/reports/dataset-card.md`, `docs/protocols/model-evaluation-plan.md`.

## Acceptance criteria

1. The analysis unit and all inclusion/exclusion/harmonization rules are documented and machine-enforced.
2. Dataset rows trace losslessly to G04 evidence IDs and source locators.
3. Named tests prove no study, sample lineage, or learned transformation leaks across splits.
4. Dataset statistics match the G04 verdict thresholds or the goal returns to G04 for a versioned gate correction.
5. The sealed test partition cannot be loaded through the normal training API.
6. Metrics, baselines, acceptance thresholds, seeds, and model-selection rules are frozen before G06.
7. Rebuilding from the same G04 snapshot is byte-stable or differs only in explicitly exempted metadata.

## Verification evidence

`artifacts/goals/G05B/report.md`, dataset and manifest hashes, lineage audit, split-leakage tests, rebuild comparison, and approved evaluation plan.

