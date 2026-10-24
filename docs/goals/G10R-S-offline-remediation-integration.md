# G10R-S — Integrate the winning society remediation offline

**Status:** complete — `RUNTIME_REMEDIATION_READY`
**Dependencies:** G10R-Q `SOCIETY_REMEDIATION_READY`; no model, network,
subscription, laboratory, or paid Phase-B execution
**Authority:** repository-local code, deterministic providers/adapters, and
recorded fixtures only

## Objective

Integrate G10R-Q's winning combined treatment into the actual
`ActiveInvestigationRunner` A2-M path and prove that the live-capable topology,
not only a synthetic harness, can execute acquisition-first support work,
resolve exact candidate locators, suppress duplicate queries, and give the
admitted open slot bounded work while preserving evidence-bus and authority
invariants.

## In scope

- the A2-M execution path in `src/roman_concrete_lab/agents/investigation.py`;
- deterministic provider, retrieval, and document fixtures under
  `fixtures/investigation/`;
- `ViewpointSociety`, `EvidenceBus`, candidate transitions, paper-card
  validation, focus allocation, and replay;
- a distinct artifact namespace under `artifacts/goals/G10R-S/`;
- focused tests and the full offline suite.

## Explicit exclusions

No live model or network calls, credential access, source-policy widening,
budget increase, evidence promotion, laboratory authority, external writes, or
automatic Phase-A/Phase-B activation. This goal integrates and tests the
remediation; it does not claim that the society is ready for another paid run
until its acceptance evidence is reviewed.

## Execution contract

### Expected implementation surface

- `src/roman_concrete_lab/agents/investigation.py`;
- `src/roman_concrete_lab/agents/viewpoint_society.py`;
- `src/roman_concrete_lab/agents/evidence_bus.py`;
- `tools/evaluation/society_failure_experiments.py` and
  `tools/evaluation/offline_remediation_integration.py`;
- `fixtures/investigation/failure-experiment.json` and
  `fixtures/investigation/remediation-sources.jsonl`;
- `tests/agents/test_offline_remediation_integration.py`;
- `artifacts/goals/G10R-S/{run.json,replay.json,report.md}`.

### Canonical invariants

- A2-M uses the G10D `ViewpointSociety` and G10P `EvidenceBus` topology.
- Every active viewpoint receives retrieval plus structural support tasks;
  reports are `COMPLETE`, `PARTIAL`, `ABSTAINED`, or `FAILED` with reasons.
- Exact candidate IDs and content locators resolve only through recorded
  candidate records; metadata-only candidates never receive evidence credit.
- Query deduplication is deterministic and a suppressed duplicate retains its
  original provenance and a decision-value reason.
- The null, credible rival, and admitted open slot remain visible.
- All arms use identical declared action, query, fetch, token, cost,
  authority, and stopping ceilings.
- Unresolved candidates, dissent, malformed outputs, partial failures, and
  budget exhaustion remain replayable and are never promoted automatically.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Fetch-positive candidate ID | exact content locator resolved and page card joined |
| Metadata-only candidate | typed pending/locator-seeking result; no card or credit |
| Duplicate query | suppressed with stable replay key and provenance |
| Open slot admitted | bounded retrieval or contradiction task and visible result |
| Structural task cannot execute | typed abstention/failure, never silent omission |
| Malformed provider output | validation failure preserved; no authority transition |
| Partial failure | checkpoint resume without repeating completed actions |
| Budget exhaustion | stop before the next action and preserve ledger |

## Acceptance criteria

1. The actual A2-M runner emits a remediation manifest proving the combined
   treatment is active and no legacy-only path is used.
2. Every active viewpoint has executable retrieval and structural support-task
   records; the open slot receives bounded work; all task-to-report-to-dossier
   joins replay successfully.
3. A fetch-positive candidate produces a typed fetch action with resolved
   locator, content hash, page-aware card, and attribution join; a
   metadata-only candidate remains pending without evidence credit.
4. Duplicate queries are suppressed deterministically, while a genuinely novel
   follow-up remains executable and attributable.
5. Null/rival preservation, dissent, malformed output, partial failure, and
   budget exhaustion each have passing deterministic fixtures.
6. Arm budgets and authority boundaries are equal and inspectable; no external
   calls occur.
7. Run and replay artifacts are byte-stable, and `python3 -m pytest -q` plus
   focused integration tests pass.
8. The report emits exactly one of `RUNTIME_REMEDIATION_READY` or
   `INCONCLUSIVE_RUNTIME_REMEDIATION`; neither outcome authorizes a paid run.

## Stop conditions

Emit `INCONCLUSIVE_RUNTIME_REMEDIATION` if the integrated runner cannot
distinguish a failed policy intervention from a plumbing or fixture failure.
Do not widen authority or revert to a discourse-only society to make the
criteria pass.

## Completed verification

- The actual `ActiveInvestigationRunner` A2-M path executed the combined
  G10R-Q treatment across all four sealed fixtures with deterministic provider
  and retrieval adapters; no model, network, credential, subscription, or
  laboratory calls occurred.
- The runner now records a remediation manifest, performs acquisition before
  reporting, executes typed structural support checks, resolves exact content
  locators into page-aware cards, suppresses duplicate queries with replayable
  ledger actions, and assigns bounded work to the admitted open slot.
- Metadata-only candidates remain without evidence cards or evidence credit;
  null/rival preservation, dissent, malformed output, partial checkpoint
  traces, budget exhaustion, and authority boundaries remain observable;
  completed checkpoints replay without provider calls.
- Artifacts: `artifacts/goals/G10R-S/run.json`, `replay.json`, and `report.md`.
- Verification: `python3 -m tools.evaluation.offline_remediation_integration
  --output-dir artifacts/goals/G10R-S` returned `RUNTIME_REMEDIATION_READY`;
  focused integration tests passed; the full offline suite passed; and the
  generated run was byte-stable on an independent second execution.
- This result is an offline runtime-readiness gate only. It does not authorize
  a Phase-A freeze, a paid Phase-B run, evidence promotion, or laboratory work.
