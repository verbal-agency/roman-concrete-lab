# G08 — Run one mechanistic feasibility spike and synthesize evidence

**Status:** proposed  
**Dependencies:** G07 complete  
**Advances:** tests whether physics/chemistry adds a relevant constraint without false “multi-fidelity” fusion

## Objective

Select at most one mechanistic question tied to an active hypothesis, evaluate one candidate model/tool against the program's mechanistic gate, and combine its result with other evidence through typed juxtaposition and sensitivity—not an unjustified scalar fidelity score.

## In scope

- decision memo comparing `no model` with a small set of candidate methods;
- one model card with governing assumptions, inputs, output, validity domain, and validation case;
- recorded/offline input fixtures and deterministic runner if the candidate passes the paper gate;
- validation against a published or synthetic analytical case clearly labeled as such;
- typed mechanistic assertions linked to—but distinct from—measurements and predictions;
- evidence table across directness, quality, validity, applicability, independence, and uncertainty;
- disagreement-preserving synthesis and leave-one-modality-out sensitivity.

## Excluded

Adding multiple simulators, molecular simulation for prestige, treating equilibrium as proof of kinetic behavior, parameter fitting to the sealed test outcome, and averaging modalities into a single unexplained support score.

## Decision outcomes

- `ADOPT`: inputs exist, validation passes, and the output changes a specified experiment decision.
- `RESEARCH_ONLY`: model is informative but not validated/decision-relevant enough for ranking.
- `REJECT`: assumptions, inputs, validation, or relevance fail.

All three complete the goal.

## Expected implementation surface

`src/roman_concrete_lab/mechanistic/` only for ADOPT/RESEARCH_ONLY runners, `fixtures/mechanistic/`, `tests/mechanistic/`, `docs/reports/mechanistic-spike.md`, `docs/reports/evidence-synthesis.md`.

## Acceptance criteria

1. The selected question, rival hypotheses, observable output, and decision impact are explicit before tool execution.
2. Required inputs are traced to evidence or marked unavailable; unavailable inputs are never filled with convenient defaults.
3. Validation has a frozen metric and emits ADOPT, RESEARCH_ONLY, or REJECT.
4. Mechanistic outputs retain type, assumptions, model/version, parameters, and lineage.
5. Synthesis preserves conflicting evidence and shows sensitivity to removing each modality/source.
6. Ranking changes, if any, are explainable and reversible; rejected models cannot affect ranking.
7. Tests replay without network access and cover malformed input, out-of-domain input, nonconvergence, partial failure, and cache invalidation.

## Verification evidence

`artifacts/goals/G08/report.md`, decision memo, model card, validation artifacts, replay tests, evidence-synthesis table, and before/after ranking comparison if applicable.
