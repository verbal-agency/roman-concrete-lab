# G10R-B2 — Post-constraint active-investigation rerun

**Status:** complete — `DO_NOT_ESCALATE_ACTIVE_SOCIETY`
**Dependencies:** G10R-F `PHASE_A_READY_FOR_OWNER_ACTIVATION`; G10R-C
`PRE_RERUN_CONSTRAINTS_READY`; explicit owner activation of the frozen Phase-B
run and configured provider/network credentials
**Authority:** model and exact-host read-only network calls are permitted only
after explicit owner activation; aggregate external spend is capped at $25

## Objective

Run one fresh, preregistered Phase-B comparison of the single investigator
(A1) and the repaired viewpoint society (A2-M) under the distinct G10R-F
manifest. Determine whether the repaired society produces a qualifying unique
source-backed contribution, useful hypothesis, or discriminator under equal
aggregate budgets. This is a directional evaluation, not evidence promotion,
scientific validation, laboratory authorization, or production adoption.

## In scope

- the four frozen sealed cases and both treatment arms;
- the exact manifest from G10R-F, including the repaired locator and action
  status contracts;
- the frozen exact-host, read-only source policy and configured model provider;
- checkpointed model traces, request-lifecycle events, candidate/evidence
  ledgers, component scores, cumulative spend, and offline replay;
- preregistered comparison and a post-run interpretation that separates
  acquisition, evidence, hypotheses, weakening, unresolved identity, blocked
  access, and overhead.

## Explicit exclusions

No new hosts, subscription retrieval, source-policy widening, budget increase,
new sealed cases, laboratory work, evidence promotion, external writes, or
production adoption. A negative or inconclusive result does not reject agent
societies generally; it determines only whether this repaired design merits
the next design goal.

## Execution contract

### Expected implementation surface

- `src/roman_concrete_lab/agents/investigation.py:run_phase_b`;
- `artifacts/goals/G10R/phase-a-post-constraint-20261023.json` and
  `manifest-post-constraint-20261023.json`;
- a separately named run/checkpoint/report/replay artifact set, never the
  historical `run.json` set;
- `tools/evaluation/open_world_replay.py` with the explicit Phase-A path;
- focused active-investigation and open-world replay tests plus the full suite.

### Canonical invariants

- the run's manifest hash equals the G10R-F Phase-A hash;
- A1 and A2-M receive equal per-treatment action, retrieval, token, and cost
  limits, and cumulative provider spend never exceeds $25;
- provider IDs resolve only through exact candidate records; unknown or
  blocked locators remain typed and are not guessed;
- all candidates, variants, dissent, unresolved claims, request causes, and
  authority diagnostics remain in checkpoints and replay;
- no direct evidence is promoted and no lab or safety authority is granted;
- a partial provider/network failure produces a typed inconclusive result,
  not a fabricated comparison.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Owner activation absent | reject before constructing model or network adapters |
| Frozen manifest missing or stale | reject with a manifest/context error |
| All eight treatment/case runs complete | apply the preregistered directional decision rule |
| Provider/network/budget failure | preserve traces and emit typed inconclusive result |
| Candidate has lawful content locator | resolve, fetch under policy, and record page-aware card or typed extraction failure |
| Candidate is metadata-only or blocked | preserve candidate and diagnostic without evidence credit |
| Society has no qualifying unique contribution | `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; route design findings to a later goal |

## Acceptance criteria

1. Without owner activation, the runner makes no provider or network call.
2. With activation, every run artifact binds to the G10R-F manifest hash and
   uses a distinct output/checkpoint namespace.
3. The complete comparison either finishes all eight runs or records a typed
   inconclusive state with no fabricated score.
4. Aggregate spend, per-arm budgets, source policy, locator resolution, request
   lifecycle, candidate/evidence joins, authority flags, and replay are
   inspectable and pass their frozen invariants.
5. The final report emits exactly one legal outcome:
   `ESCALATE_ACTIVE_SOCIETY_EVALUATION`, `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, or
   `INCONCLUSIVE_ACTIVE_INVESTIGATION`.
6. No evidence, laboratory action, safety approval, or production adoption is
   authorized by the run.

## Stop conditions

Stop immediately on manifest mismatch, source-policy widening, unequal budgets,
critical provenance/authority/safety failure, or spend-cap violation. A valid
`DO_NOT_ESCALATE_ACTIVE_SOCIETY` result routes only to a new design/postmortem
goal; it does not authorize repeated paid runs automatically.

## Completed run

- Run: `artifacts/goals/G10R-B2-retry-20261023/run.json`
- Replay: `artifacts/goals/G10R-B2-retry-20261023/replay.json`
- Report: `artifacts/goals/G10R-B2-retry-20261023/report.md`
- Manifest: `sha256:fb76226b4332f50ce3f5e8ad15a65d3d274d8cc3a031894918f5e020728e38bf`
- All eight paired treatment/case runs completed; replay status was
  `REPLAYABLE_AFTER_REPAIR`.
- Cumulative recorded spend was `$0.33173708` of the `$25.00` cap, including
  the preserved partial attempt in the prior B2 namespace.
- The preregistered decision found no qualifying unique society contribution:
  A1 and A2-M totals were both zero under the live directional scorer, while
  the repaired replay showed society discovery deltas of `0`, `-3`, `-2`, and
  `-3` and hypothesis deltas of `-1`, `0`, `-1`, and `-1` across the four
  cases. This is a result about the executed design and task surface, not a
  rejection of agent societies generally.

## Verification evidence

- `python3 -m pytest -q` — `130 passed`.
- `python3 -m pytest -q tests/agents/test_open_world_remediation.py tests/agents/test_constraint_audit_replay.py` — `5 passed`.
- `python3 -m py_compile src/roman_concrete_lab/agents/investigation.py tools/evaluation/open_world_replay.py tools/evaluation/post_constraint_phase_b.py` — passed.
- The retry contains four completed A1 checkpoints and four completed A2-M
  checkpoints, a replayable eight-row score ledger, no critical failures, and
  no incomplete treatment cases.
