# G10R-Q — Post-B2 society failure-experiment loop

**Status:** complete — `SOCIETY_REMEDIATION_READY`
**Dependencies:** G10R-B2 complete with
`DO_NOT_ESCALATE_ACTIVE_SOCIETY`; `artifacts/goals/G10R-B2-retry-20261023/`;
no model, network, subscription, or laboratory execution
**Authority:** repository-local artifacts, deterministic code, and offline
fixtures only; this goal does not reconsider the society architecture

## Objective

Experiment on the concrete failure modes that caused the post-constraint
society to produce discourse instead of attributable evidence. This is an
offline controlled-experiment goal, not a referendum on the society
architecture. Compare the current baseline with bounded interventions for
acquisition-first scheduling, executable support tasks, locator resolution,
query deduplication, and open-slot work. Keep only interventions that improve
attributable information acquisition without breaking budget, provenance, or
authority invariants. This goal must not authorize another paid run.

## Why this goal exists

G10R-B2 completed the full paired comparison and replayed cleanly, but the
society produced no qualifying unique contribution. The live directional scorer
gave both arms zero total score; the repaired replay showed non-positive
society discovery and hypothesis deltas in every case. The result is stronger
than the earlier partial run, but it still does not by itself distinguish
agent-design weakness from an information-poor case surface or an overly
strict contribution path. The symptoms to correct are specific: zero fetches,
metadata-only candidates, repeated searches, abstained support tasks, an open
slot with no work, and high coordination overhead with no unique contribution.

## In scope

- reconstruct the B2 retry run, all eight checkpoints, candidate ledger, score
  ledger, plan-constraint events, request lifecycle, and replay;
- compare executed A2-M topology with the intended G10D/G10P contracts;
- quantify acquisition headroom, candidate uniqueness, lawful fetches,
  evidence-card yield, attribution, support-task completion, dissent,
  open-slot activity, and society overhead;
- run deterministic positive, negative, contradictory, malformed, partial, and
  budget-exhaustion fixtures through the scorer and replay;
- define a failure matrix mapping each B2 symptom to one or more falsifiable
  interventions and a measurable outcome;
- run the baseline, single-factor interventions, and the smallest justified
  combined treatment on deterministic fixtures;
- preserve null, contradictory, malformed, partial, and budget-exhaustion
  cases so an apparent gain cannot come from relaxed safety or scoring;
- produce an experiment-backed remediation recommendation before any further
  paid evaluation.

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
- `tools/evaluation/open_world_replay.py`, the evidence-bus implementation,
  and a new offline failure-experiment runner;
- `fixtures/investigation/` and focused tests under `tests/agents/`;
- `artifacts/goals/G10R-Q/{loss-ledger.json,experiment-matrix.json,experiment-results.json,report.md}`.

### Required ledger fields

Every finding must include `finding_id`, `layer` (`architecture`,
`integration`, `acquisition`, `task_fixture`, `scorer`, or `plumbing`),
`evidence_locator`, `observed_behavior`, `confidence`, `severity`,
`remediation`, and `verification_test`. Findings must distinguish observed
facts from hypotheses about cause.

The remediation manifest must also record `support_task_id`, `viewpoint_id`,
`task_type`, `action_ids`, `source_candidate_ids`, `claim_ids`, `status`, and
`abstention_reason` for every assigned support task.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Complete B2 artifacts and matching manifest | reconstruct all eight rows |
| Missing or mismatched checkpoint | typed `INCONCLUSIVE_POSTMORTEM`, no guessed join |
| Unique attributable candidate fixture | credit discovery only when the join survives replay |
| Contradictory or unresolved candidate | preserve dissent/pending state; no silent discard or promotion |
| Malformed or unauthorized transition | classify the transition and preserve the record; do not grant authority |
| Budget exhaustion or partial treatment | retain partial traces and report untestable comparison |
| Society task is assigned but cannot execute | typed `ABSTAINED` with a bounded reason; never a silent placeholder |
| Candidate has an exact lawful content locator | enqueue a fetch/identity task and preserve the candidate-to-card join |
| Candidate has no lawful content locator | preserve metadata-only status and record the next locator-seeking action |
| Duplicate query is proposed | suppress it or require a typed novelty/decision-value justification |
| Open slot is admitted | allocate it bounded retrieval or contradiction work and preserve its result |
| No repair passes the deterministic thresholds | `INCONCLUSIVE_SOCIETY_REMEDIATION`; retain the society architecture and route the specific failed layer to follow-up |

### Required experiment arms

The offline runner must include:

1. `BASELINE_B2_BEHAVIOR` — the current society behavior, replayed unchanged;
2. `ACQUISITION_FIRST` — reserve an explicit acquisition budget before critique
   and adjudication;
3. `EXECUTABLE_SUPPORT` — execute identity, extraction, contradiction, and
   experiment-design tasks instead of auto-abstaining them;
4. `LOCATOR_BRIDGE` — resolve exact candidate IDs/content locators into typed
   fetch requests and page-card joins;
5. `DEDUP_AND_OPEN_SLOT` — suppress duplicate searches and give the admitted
   open slot bounded novel work; and
6. one combined arm only if the single-factor results justify it.

Each arm must declare its changed policy surface, hold all other budgets and
scoring rules fixed, and report unique attributable candidates, fetch-request
yield, evidence-card yield, contradiction coverage, attribution completeness,
useful-hypothesis yield, duplicate-work rate, and coordination cost.

### Authority and side effects

The goal may read repository-local artifacts and write generated artifacts under
`artifacts/goals/G10R-Q/`. It may not construct a model provider, network
adapter, credential reader, subscription client, lab adapter, or external write
path. Replay and tests must be deterministic and offline.

## Acceptance criteria

1. Every B2 case/arm is reconstructed with calls, tokens, actions, candidates,
   fetches, hypotheses, evidence, attribution, costs, and critical failures;
   missing fields are typed rather than inferred.
2. The loss ledger identifies the B2 symptoms with evidence locators and
   confidence, and separates observed failure from causal hypothesis.
3. The experiment matrix contains the unchanged baseline, every required
   single-factor arm, and a combined arm only when justified by the results.
4. Each arm changes only its declared intervention and is evaluated under
   equal action, retrieval, token, cost, authority, and scoring limits.
5. The executable-support arm runs, rather than merely assigns, at least one
   retrieval task and one identity, extraction, contradiction, or
   experiment-design task for every active viewpoint; true abstentions have
   typed reasons and survive replay.
6. The locator-bridge arm turns an exact lawful content locator into a typed
   fetch/identity request and page-card join; metadata-only candidates remain
   pending without evidence credit.
7. The acquisition-first and deduplication/open-slot arms report whether they
   increase unique attributable candidates, fetch-request yield, evidence-card
   yield, contradiction coverage, or useful hypotheses without increasing
   duplicate-work rate beyond the declared threshold.
8. Offline fixtures demonstrate a unique discovery, a weakening/contradiction,
   an unresolved candidate, malformed output, partial failure, budget
   exhaustion, duplicate-query suppression, and open-slot work in every arm
   where the fixture applies.
9. The results artifact records effect sizes against baseline, failed
   interventions, and the minimum combined treatment justified by evidence.
10. The report emits exactly one of `SOCIETY_REMEDIATION_READY` or
    `INCONCLUSIVE_SOCIETY_REMEDIATION`, explicitly preserves the society
    architecture, and forbids an automatic paid rerun.
11. `python3 -m pytest -q` and focused failure-experiment/replay tests pass;
    all generated artifacts are byte-stable on a second offline run.

## Stop conditions

Stop with `INCONCLUSIVE_SOCIETY_REMEDIATION` if the B2 artifacts or fixtures
cannot identify which repair failed. Do not use this goal to stop the society
architecture. A passing offline remediation may authorize only a later Phase-A
freeze and separately activated paid test; it never authorizes a paid run by
itself.

## Completed experiment

- Runner: `tools/evaluation/society_failure_experiments.py`
- Fixture: `fixtures/investigation/failure-experiment.json`
- Results: `artifacts/goals/G10R-Q/experiment-results.json`
- Matrix: `artifacts/goals/G10R-Q/experiment-matrix.json`
- Loss ledger: `artifacts/goals/G10R-Q/loss-ledger.json`
- Report: `artifacts/goals/G10R-Q/report.md`
- Outcome: `SOCIETY_REMEDIATION_READY`; external calls were `false`.
- Arms: baseline, acquisition-first, executable-support, locator-bridge,
  deduplication/open-slot, and a justified combined treatment.
- The combined treatment produced fetches, a page-aware evidence card, full
  support-task execution, contradiction coverage, open-slot work, and duplicate
  suppression under the same declared offline limits. Deduplication/open-slot
  is retained as an enabler, not as a standalone treatment.
- Verification: `python3 -m pytest -q` — `134 passed`; focused failure
  experiment tests passed; byte-stability and malformed, partial, budget,
  contradiction, metadata-only, and open-slot fixtures passed.
