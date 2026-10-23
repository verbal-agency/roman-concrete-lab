# G10R-A — Offline evidence-acquisition and support-task redesign

**Status:** complete — `ACQUISITION_DESIGN_READY`
**Dependencies:** refreshed G10R-P postmortem against the integrated G10R run; G10R-I `RUNTIME_INTEGRATION_READY`; G10D and G10P complete
**Authority:** offline repository work only; no model, network, subscription, credential, laboratory, or external communication

## Why this goal exists

The repaired active-investigation run now exercises the intended viewpoint
society and evidence bus, so its topology is interpretable. It still does not
test the theory's central value proposition: no treatment/case run performed a
permitted document fetch or produced a page-aware evidence card. Trace review
found a likely design confound: the live A2-M proponent and auditor instructions
explicitly require empty follow-up, fetch, and simulation arrays; extraction,
identity, and experiment tasks are then auto-abstained; and focus executes only
search queries. The society spent substantially more model calls than A1 while
being structurally discouraged from acquiring content. This goal separates
planner non-request, runner suppression, policy blocking, fixture absence, and
agent choice before deciding whether viewpoint competition is useful.

## Objective

Redesign and offline-test the society's support-task loop so competing
mechanism viewpoints must seek, verify, weaken, or explicitly abstain on
evidence before critique and adjudication consume the common budget. Preserve
the current viewpoint, null, rival, open-slot, evidence-bus, candidate-variant,
and authority contracts.

## In scope

- deterministic fetch-positive, metadata-only, contradiction, malformed, and
  budget-exhaustion fixtures;
- explicit retrieval, extraction/identity, contradiction, and experiment-design
  obligations linked to a viewpoint and bounded by task budget;
- instrumentation that distinguishes a tool request not made, a request
  rejected by the runner, a request blocked by policy, a request executed with
  no usable result, and a successful evidence-card join;
- deterministic follow-up allocation based on expected information value,
  unresolved uncertainty, provenance risk, rival/null coverage, and remaining
  budget;
- page-aware evidence-card production on the positive fixture and reviewable
  diagnostics on blocked or malformed fixtures;
- candidate observations and substantive variants retained as reviewable,
  promotable records without direct-evidence credit;
- blind offline comparison against A1 and the current integrated A2-M under
  equal aggregate action, retrieval, token, and cost ceilings;
- replay, checkpoint, duplicate-action, partial-failure, and authority tests.

## Explicit exclusions

No live model or network calls, new hosts, subscription retrieval, OCR adapter,
lab work, evidence promotion, scientific validation, budget increase, or
production adoption. A positive offline result authorizes only a fresh Phase-A
manifest and a separately activated live evaluation; it does not authorize
another paid run in this goal.

## Execution contract

### Canonical records and invariants

Use the existing versioned `ViewpointCard`, `SupportTask`, `SupportReport`,
`ViewpointDossier`, `CrossViewpointCritique`, `FocusDecision`,
`SourceCandidate`, `PaperEvidenceCard`, and portfolio contracts. Add fields only
through versioned schemas. Every support task must have exactly one viewpoint,
one task type, a bounded action budget, and a terminal result of `SUPPORTS`,
`WEAKENS`, `NON_DISCRIMINATING`, or `ABSTAINED` with a reason. A task that has
an available bounded follow-up may not terminate as source-free `PARTIAL`.

Candidate identity and observations remain separate: repeated query/status
observations are retained; substantive metadata variants remain pending review
and promotable after validation; neither is silently overwritten or promoted.
Evidence cards require a permitted content hash and page locator. No model
assertion can become immutable evidence or authorize a laboratory action.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Fetch-positive source and bounded retrieval task | Fetch permitted fixture, emit page-aware card, and join card to source/action/task/viewpoint |
| Agent plan requests a fetch or follow-up | Preserve the request in the task ledger and execute or record the precise policy/runner block; never silently replace it with an abstention |
| Agent plan omits fetch despite actionable fetch-positive uncertainty | Record `NOT_REQUESTED` and test whether the focus/task policy should have required the action |
| Metadata-only source | Retain candidate and explicit `EVIDENCE_PENDING`/abstention reason; no direct-evidence credit |
| Candidate appears with another query or status | Preserve canonical candidate plus observation; no fatal duplicate error |
| Candidate metadata identity disagrees | Preserve canonical plus reviewable variant with differing fields; no silent overwrite |
| Support finds evidence against its viewpoint | Emit `WEAKENS`, preserve dissent, and make the result available to focus/adjudication |
| Rights-blocked or malformed document | Emit deterministic diagnostic without retaining prohibited payload or fabricating a card |
| Follow-up budget remains and uncertainty is actionable | Allocate the cheapest valid follow-up and record rationale |
| Follow-up budget is exhausted | Emit bounded abstention and preserve partial records; do not widen budget |
| Critique receives incomplete dossier | Preserve unresolved dispute and propose discriminator; do not force consensus |
| Duplicate action/checkpoint replay | Return byte-equivalent output without another external call |

### Expected implementation surface

- `src/roman_concrete_lab/agents/viewpoint_society.py`
- `src/roman_concrete_lab/agents/evidence_bus.py`
- `src/roman_concrete_lab/agents/investigation.py`
- `src/roman_concrete_lab/retrieval/pdf.py` and existing retrieval contracts,
  only where required to exercise the declared fixture boundary
- `fixtures/investigation/viewpoint-society/` and existing PDF benchmark
  fixtures
- `tests/agents/test_viewpoint_society.py`,
  `tests/agents/test_evidence_bus.py`, and new focused acquisition/replay tests
- `tools/evaluation/` offline runner and replay artifact
- `artifacts/goals/G10R-A/phase-a.json`, `report.md`, and frozen manifests

### Acceptance criteria

1. A fetch-positive offline case produces at least one page-aware evidence card
   joined to its source, action, task, and viewpoint; a blocked/malformed case
   produces a deterministic diagnostic and no prohibited payload.
2. The offline trace distinguishes `NOT_REQUESTED`, `RUNNER_REJECTED`,
   `POLICY_BLOCKED`, `NO_USABLE_RESULT`, and `EXECUTED_CARD` for every attempted
   evidence action; no forced-empty prompt or synthetic abstention can hide the
   cause.
3. Every required support-task type is exercised with a valid attributed
   result, including at least one `WEAKENS` report and one bounded abstention.
4. Duplicate candidate observations and substantive variants remain visible,
   replayable, and promotable-after-validation without overwriting the
   canonical candidate or receiving direct-evidence credit.
5. The focus allocator spends evidence-acquisition work before adjudication
   when a valid fetch-positive discriminator remains, and records its rationale
   deterministically.
6. Null, credible rival, and admitted open-slot viewpoints remain visible;
   dissent and unresolved disputes survive dossier, critique, portfolio, and
   score serialization.
7. Under equal aggregate budgets, the society's offline ledger reports unique
   attributable acquisition, evidence-card yield, contradiction/weakening
   coverage, useful-hypothesis yield, and overhead separately from rhetoric or
   output volume.
8. Checkpoint/resume, duplicate actions, partial failures, and candidate
   conflicts replay byte-stably with no model, network, credential,
   subscription, laboratory, or evidence-promotion side effect.
9. The report emits exactly one handoff: `ACQUISITION_DESIGN_READY`,
   `ACQUISITION_DESIGN_NO_GO`, or `INCONCLUSIVE_ACQUISITION_DESIGN`, and names
   whether a fresh Phase-A/live evaluation is justified.

### Criterion-to-artifact map

| Criterion | Evidence |
|---|---|
| 1–2 | Positive/blocked/malformed fixtures, request-lifecycle ledger, evidence-card ledger, focused tests |
| 3–4 | Support-task and candidate-variant tests plus checkpoint replay |
| 5–7 | Focus ledger, equal-budget comparison, and blind offline score report |
| 8 | Replay artifact, authority scan, and full test suite |
| 9 | `artifacts/goals/G10R-A/report.md` and machine-readable handoff |

## Stop conditions

Emit `ACQUISITION_DESIGN_NO_GO` if the society cannot produce attributable
acquisition or weakening value on the positive fixtures, if support work still
spends the budget on discourse before available evidence actions, if joins or
dissent are lossy, or if the authority boundary cannot be preserved. A
successful offline handoff does not imply that a future paid run will be
positive; it only makes that question worth testing under a newly frozen
manifest and explicit activation.
