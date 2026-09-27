# G07 — Formalize rival hypotheses and rank bounded experiments

**Status:** proposed  
**Dependencies:** G06 complete  
**Advances:** turns evidence into falsifiable, budget-aware physical experiment choices

## Objective

Create typed rival-hypothesis records, enumerate a safe in-domain experiment space, and rank experiment sets for discrimination, coverage, feasibility, and—only when G06 permits—predicted functional performance.

## In scope

- at least one scientifically reviewed rival set relevant to the primary estimand;
- intervention, comparator, domain, outcome, confounders, prediction, observation model, and adjudication rule for each hypothesis;
- experiment constraints, forbidden combinations, material substitutions, controls, and declared lab budget;
- deterministic qualitative discrimination rubric;
- numeric expected information gain only for rivals with validated predictive distributions;
- Pareto/frontier output rather than an opaque scalar “best” score;
- ranking stability across uncertainty draws, evidence weights, and reasonable utility weights;
- draft protocols labeled for expert review.

## Excluded

Closed-loop BO, optimizing outside the support region, invented material properties/costs, physical execution, and claims that a proposed experiment validates a mechanism.

## Canonical candidate states

`eligible`, `dominated`, `infeasible`, `unsupported`, `ood_abstain`, `expert_review_required`.

An experiment cannot be both `eligible` and `infeasible/unsupported/ood_abstain`. Illegal transitions fail. Expert approval is not granted by software.

## Ranking behavior

| Evidence/model condition | Allowed ranking |
|---|---|
| G06 model usable | in-support predictive utility plus discrimination/coverage/cost/risk |
| explanatory only | qualitative discrimination and coverage; no performance optimization |
| model rejected | qualitative rival separation or evidence-gap design only |
| no predictive distributions for rivals | rubric score; EIG field absent, not zero |
| unstable top set | return a robust set/tie and instability warning |

## Expected implementation surface

`src/roman_concrete_lab/design/`, `schemas/hypothesis.*`, `schemas/experiment.*`, `fixtures/design/`, `tests/design/`, `docs/reports/experiment-ranking.md`, `docs/protocols/drafts/`.

## Acceptance criteria

1. Every hypothesis satisfies the program's hypothesis contract and has scientific review status.
2. Forbidden, unsafe, unsupported, and OOD combinations are rejected before scoring.
3. Numeric EIG is impossible unless predictive and observation distributions validate.
4. Ranking exposes separate utility components, constraints, and Pareto/dominance relationships.
5. Duplicate calls are deterministic or return recorded-seed distributions; top-set stability is reported.
6. Synthetic, contradictory, malformed, partial, budget-exhaustion, and no-feasible-candidate fixtures have named tests.
7. Every recommended experiment includes controls, replicate rationale, randomization, measurements, timepoints, expected outcomes by hypothesis, adjudication rule, uncertainty, and expert-review watermark.

## Verification evidence

`artifacts/goals/G07/report.md`, hypothesis review log, constraint tests, ranking manifest, sensitivity/stability report, and criterion-to-test map.
