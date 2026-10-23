# G10R-Q — Post-B2 society decision and offline redesign gate

**Status:** proposed
**Dependencies:** G10R-B2 complete with
`DO_NOT_ESCALATE_ACTIVE_SOCIETY`; `artifacts/goals/G10R-B2-retry-20261023/`;
no model, network, subscription, or laboratory execution
**Authority:** repository-local artifacts, deterministic code, and offline
fixtures only

## Objective

Determine whether the post-constraint society result is an actionable design
failure, a task/fixture ceiling, or a genuine lack of value, then choose one
bounded next state: an offline redesign goal, a stop decision for this society
architecture, or a non-agent exploration path. This gate must not authorize
another paid run merely because the result is negative.

## Why this goal exists

G10R-B2 completed the full paired comparison and replayed cleanly, but the
society produced no qualifying unique contribution. The live directional scorer
gave both arms zero total score; the repaired replay showed non-positive
society discovery and hypothesis deltas in every case. The result is stronger
than the earlier partial run, but it still does not by itself distinguish
agent-design weakness from an information-poor case surface or an overly
strict contribution path. The next decision must be made offline and must
preserve the distinction.

## In scope

- reconstruct the B2 retry run, all eight checkpoints, candidate ledger, score
  ledger, plan-constraint events, request lifecycle, and replay;
- compare executed A2-M topology with the intended G10D/G10P contracts;
- quantify acquisition headroom, candidate uniqueness, lawful fetches,
  evidence-card yield, attribution, support-task completion, dissent,
  open-slot activity, and society overhead;
- run deterministic positive, negative, contradictory, malformed, partial, and
  budget-exhaustion fixtures through the scorer and replay;
- identify the smallest offline change that could falsifiably improve
  attributable information acquisition, if any;
- issue a decision and create at most one successor offline goal.

## Explicit exclusions

No model or network calls, new retrieval hosts, subscription access, budget
increase, source-policy change, evidence promotion, laboratory work, external
communication, or automatic Phase-B rerun. Do not treat rhetoric, consensus,
answer length, or mechanism count as scientific credit.

## Execution contract

### Expected implementation surface

- `artifacts/goals/G10R-B2-retry-20261023/run.json`;
- `artifacts/goals/G10R-B2-retry-20261023/replay.json`;
- `artifacts/goals/G10R-B2-retry-20261023/checkpoints/*.json`;
- `src/roman_concrete_lab/agents/investigation.py`;
- `src/roman_concrete_lab/agents/viewpoint_society.py` and evidence-bus
  modules;
- `tools/evaluation/open_world_replay.py` and a new offline postmortem tool;
- `fixtures/investigation/` and focused tests under `tests/agents/`;
- `artifacts/goals/G10R-Q/{postmortem.json,gap-matrix.md,target-state.json,report.md}`.

### Required ledger fields

Every finding must include `finding_id`, `layer` (`architecture`,
`integration`, `acquisition`, `task_fixture`, `scorer`, or `plumbing`),
`evidence_locator`, `observed_behavior`, `confidence`, `severity`,
`remediation`, and `verification_test`. Findings must distinguish observed
facts from hypotheses about cause.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Complete B2 artifacts and matching manifest | reconstruct all eight rows |
| Missing or mismatched checkpoint | typed `INCONCLUSIVE_POSTMORTEM`, no guessed join |
| Unique attributable candidate fixture | credit discovery only when the join survives replay |
| Contradictory or unresolved candidate | preserve dissent/pending state; no silent discard or promotion |
| Malformed or unauthorized transition | classify the transition and preserve the record; do not grant authority |
| Budget exhaustion or partial treatment | retain partial traces and report untestable comparison |
| No falsifiable offline redesign remains | `POSTMORTEM_NO_GO` and stop paid society work |

### Authority and side effects

The goal may read repository-local artifacts and write generated artifacts under
`artifacts/goals/G10R-Q/`. It may not construct a model provider, network
adapter, credential reader, subscription client, lab adapter, or external write
path. Replay and tests must be deterministic and offline.

## Acceptance criteria

1. Every B2 case/arm is reconstructed with calls, tokens, actions, candidates,
   fetches, hypotheses, evidence, attribution, costs, and critical failures;
   missing fields are typed rather than inferred.
2. The postmortem contains a loss ledger with evidence locators and confidence,
   explicitly states whether the executed treatment matches G10D/G10P, and
   separates observed failure from causal hypothesis.
3. Offline fixtures demonstrate preservation and scoring of a unique discovery,
   a weakening/contradiction, an unresolved candidate, malformed output,
   partial failure, and budget exhaustion.
4. The target-state artifact defines binary thresholds for topology fidelity,
   unique attributable contribution, evidence acquisition, contradiction
   coverage, attribution completeness, budget parity, and replayability—or
   records why no safe threshold can be met.
5. The report emits exactly one of `TARGET_STATE_READY_FOR_OFFLINE_BUILD`,
   `POSTMORTEM_NO_GO`, or `INCONCLUSIVE_POSTMORTEM`, names the next goal if
   one is justified, and explicitly forbids an automatic paid rerun.
6. `python3 -m pytest -q` and the focused postmortem/replay tests pass; all
   generated artifacts are byte-stable on a second offline run.

## Stop conditions

Stop with `INCONCLUSIVE_POSTMORTEM` if the B2 artifacts cannot distinguish a
design, integration, acquisition, task/fixture, scorer, or plumbing cause.
Emit `POSTMORTEM_NO_GO` if no offline change can produce a measurable,
attributable information-acquisition advantage under equal budgets or if the
required topology cannot be enforced without unsafe authority. A positive
offline target state may authorize only a later offline build goal; it does
not authorize a paid run.
