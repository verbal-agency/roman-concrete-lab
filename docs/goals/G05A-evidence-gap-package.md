# G05A — Publish the evidence-gap package

**Status:** proposed  
**Entry gate:** G04 verdict is NO-GO  
**Dependencies:** G04 complete  
**Advances:** converts insufficient literature into the smallest useful physical study

## Objective

Produce a reproducible descriptive synthesis of what can and cannot be concluded and a draft minimum laboratory study designed to close the specific evidence gaps that blocked modeling.

## In scope

- evidence map by material, intervention, endpoint, protocol, and study;
- explicit unidentifiable claims and reasons;
- sensitivity of conclusions to comparability/exclusion decisions;
- prioritized missing measurements and covariates;
- a minimal controlled experiment matrix with controls, replicate rationale, randomization, timepoints, measurement methods, expected outcomes, and analysis plan;
- cost/equipment/material inputs marked unknown unless supplied;
- `DRAFT — EXPERT REVIEW REQUIRED` protocol and safety checklist.

## Excluded

Surrogate fitting, Bayesian optimization, numeric information gain without probabilistic rivals, performance ranking, physical execution, and invented cost/safety values.

## Expected implementation surface

`src/roman_concrete_lab/analysis/descriptive.py`, `tests/analysis/test_descriptive.py`, `docs/reports/evidence-gap.md`, `docs/protocols/minimum-lab-study.md`, and release manifests.

## Acceptance criteria

1. Every reported count and summary is reproducible from the G04 snapshot.
2. Each blocking gap maps to one or more proposed measurements and an observable decision it would enable.
3. The experiment matrix includes positive/process-matched controls and does not vary multiple causal factors unintentionally.
4. Claims are limited to evidence synthesis; no candidate is labeled superior or validated.
5. The protocol is visibly unapproved and names the required materials-science and safety reviewers.
6. The package states what new evidence would move the program from NO-GO to LIMITED or GO.

## Verification evidence

`artifacts/goals/G05A/report.md`, reproducibility run, claim audit, gap-to-measurement matrix, and protocol completeness checklist.

## Terminal condition

This is the terminal scientific-content package for the NO-GO branch; G09 still performs release assembly and audit. G05B–G08 remain ineligible until new evidence is ingested and G04 is rerun under a versioned amendment.
