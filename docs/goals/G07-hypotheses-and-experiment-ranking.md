# G07 — Formalize rival hypotheses and rank bounded experiments

**Status:** proposed  
**Dependencies:** G06 complete  
**Advances:** turns evidence into falsifiable, budget-aware physical experiment choices and establishes the deterministic hypothesis-tournament/shared-memory contract that any later agent society must obey

## Objective

Create typed rival-hypothesis records, enumerate a safe in-domain experiment space, and rank experiment sets for discrimination, coverage, feasibility, and—only when G06 permits—predicted functional performance.

## In scope

- at least one scientifically reviewed rival set relevant to the primary estimand;
- append-only hypothesis registry with explicit statuses, provenance, rival links, and promotion/retirement rules;
- shared-memory read/write policy separating immutable evidence from derived hypotheses and agent reflections;
- intervention, comparator, domain, outcome, confounders, prediction, observation model, and adjudication rule for each hypothesis;
- experiment constraints, forbidden combinations, material substitutions, controls, and declared lab budget;
- deterministic qualitative discrimination rubric;
- numeric expected information gain only for rivals with validated predictive distributions;
- Pareto/frontier output rather than an opaque scalar “best” score;
- ranking stability across uncertainty draws, evidence weights, and reasonable utility weights;
- draft protocols labeled for expert review.

## Deterministic hypothesis tournament

Each hypothesis receives the same frozen evidence packet and problem context. Independent proposal/critique passes must state predictions, disconfirming observations, and the cheapest useful discriminator. A deterministic adjudicator scores evidence coverage, contradiction handling, prediction distinctness, feasibility, and uncertainty; majority vote cannot promote a hypothesis. The tournament output is a ranked or Pareto hypothesis/experiment set plus abstentions and unresolved conflicts.

## Required design discussion before implementation

The goal must explicitly resolve and record two policy layers rather than inheriting them from an agent framework:

- **Focus layer:** how the system allocates limited retrieval, analysis, and experiment budget across unresolved hypotheses, counterevidence, novelty, feasibility, risk, and expected information value; when it changes focus; and when it abstains.
- **Promotion layer:** the legal transitions from observation to derived assertion, hypothesis to supported/narrow/contradicted status, and candidate to experiment recommendation; required provenance, reviewer authority, contradiction handling, retraction, and context-amendment rules for each transition.

These are scientific-governance contracts. Agent prompts may propose focus or promotion actions, but they cannot define or silently relax the policies.

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

`src/roman_concrete_lab/design/`, `src/roman_concrete_lab/hypotheses/`, `src/roman_concrete_lab/memory/`, `src/roman_concrete_lab/focus/`, `schemas/hypothesis.*`, `schemas/experiment.*`, `fixtures/design/`, `tests/design/`, `docs/reports/experiment-ranking.md`, `docs/protocols/drafts/`.

## Acceptance criteria

1. Every hypothesis satisfies the program's hypothesis contract, has scientific review status, and is represented in the append-only registry.
2. Forbidden, unsafe, unsupported, and OOD combinations are rejected before scoring.
3. Numeric EIG is impossible unless predictive and observation distributions validate.
4. Ranking exposes separate utility components, constraints, and Pareto/dominance relationships.
5. Duplicate calls are deterministic or return recorded-seed distributions; top-set stability is reported.
6. Synthetic, contradictory, malformed, partial, budget-exhaustion, and no-feasible-candidate fixtures have named tests.
7. Every recommended experiment includes controls, replicate rationale, randomization, measurements, timepoints, expected outcomes by hypothesis, adjudication rule, uncertainty, and expert-review watermark.
8. The deterministic tournament replays from a frozen context/evidence manifest, preserves conflicting hypotheses, and rejects any attempt to promote an agent reflection or unsupported claim into immutable evidence.
9. The report records the approved focus and promotion policies, their legal state transitions, abstention rules, authority boundaries, and unresolved design questions before any agent implementation.

## Verification evidence

`artifacts/goals/G07/report.md`, hypothesis review log, constraint tests, ranking manifest, sensitivity/stability report, and criterion-to-test map.
