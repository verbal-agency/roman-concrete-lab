# G10R-Q — Post-B2 society acquisition-remediation build

**Status:** proposed
**Dependencies:** G10R-B2 complete with
`DO_NOT_ESCALATE_ACTIVE_SOCIETY`; `artifacts/goals/G10R-B2-retry-20261023/`;
no model, network, subscription, or laboratory execution
**Authority:** repository-local artifacts, deterministic code, and offline
fixtures only; this goal does not reconsider the society architecture

## Objective

Repair the concrete mechanics that caused the post-constraint society to
produce discourse instead of attributable evidence. This is an implementation
goal, not a referendum on the society architecture. Build and verify an
acquisition-first offline treatment in which viewpoint proponents and their
structural support agents can open new evidence paths, resolve lawful locators,
execute contradiction and identity work, and preserve every result through the
evidence bus. This goal must not authorize another paid run.

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
- implement the smallest coherent offline remediation for those symptoms;
- prove the remediation on deterministic fixtures before any further paid
  evaluation.

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
  and a new offline remediation runner;
- `fixtures/investigation/` and focused tests under `tests/agents/`;
- `artifacts/goals/G10R-Q/{loss-ledger.json,remediation-manifest.json,report.md}`.

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
3. The repaired offline runner executes, rather than merely assigns, at least
   one retrieval task and one identity, extraction, contradiction, or
   experiment-design task for every active viewpoint; any true abstention has a
   typed reason and survives replay.
4. A candidate with an exact lawful content locator produces a deterministic
   fetch/identity request and page-card join; a metadata-only candidate remains
   pending without receiving evidence credit.
5. Query deduplication prevents repeated work unless a novelty or decision-value
   justification is recorded; the focus policy reserves work for acquisition
   before critique and adjudication.
6. The admitted open slot receives bounded work and its unresolved or positive
   result remains visible in the portfolio and score ledger.
7. Offline fixtures demonstrate a unique discovery, a weakening/contradiction,
   an unresolved candidate, malformed output, partial failure, budget
   exhaustion, duplicate-query suppression, and open-slot work.
8. The remediation manifest defines binary thresholds for support-task
   execution, fetch-request yield, evidence-card yield, contradiction
   coverage, attribution completeness, budget parity, and replayability.
9. The report emits exactly one of `SOCIETY_REMEDIATION_READY` or
   `INCONCLUSIVE_SOCIETY_REMEDIATION`, explicitly preserves the society
   architecture, and forbids an automatic paid rerun.
10. `python3 -m pytest -q` and focused remediation/replay tests pass; all
    generated artifacts are byte-stable on a second offline run.

## Stop conditions

Stop with `INCONCLUSIVE_SOCIETY_REMEDIATION` if the B2 artifacts or fixtures
cannot identify which repair failed. Do not use this goal to stop the society
architecture. A passing offline remediation may authorize only a later Phase-A
freeze and separately activated paid test; it never authorizes a paid run by
itself.
