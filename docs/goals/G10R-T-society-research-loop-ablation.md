# G10R-T — Repair and ablate the society research loop offline

**Status:** complete — `SOCIETY_RESEARCH_LOOP_READY`
**Dependencies:** G10R-S complete with `RUNTIME_REMEDIATION_READY`; completed
post-G10R-S paid comparison at
`artifacts/goals/G10R-S-paid-20261024-final/` with
`DO_NOT_ESCALATE_ACTIVE_SOCIETY`
**Authority:** repository-local code, deterministic providers/adapters, and
recorded fixtures only; no network, credentials, model calls, subscriptions,
laboratory work, or paid Phase-B execution

## Why this goal exists

The post-G10R-S paid comparison completed without a critical authority,
provenance, or rights failure, but it did not test a functioning research
society cleanly. A1 scored 5 and A2-M scored 3 across four cases; three cases
were 0–0, and the only score difference included lexical-rubric effects even
though both arms found the same canonical simulation source. More decisively,
A2-M used 52 model calls, 152,767 input tokens, 35 searches, and about
`$0.0253`, versus A1's 8 calls, 20,533 input tokens, 33 searches, and about
`$0.0052`, while neither arm produced a successful document fetch or paper
evidence card.

The trace and implementation review found five causal defects that must be
repaired before another society-value claim is interpretable:

1. plans request search and fetch work before discovered candidate locators are
   available, with no post-search candidate-selection/fetch turn;
2. the focus allocator ranks ascending and can spend actions on lower-scored
   tasks while higher-scored tasks remain;
3. dossiers are committed before auditor and focus work and are not revised,
   so later reports do not enter the structured adjudication state;
4. the open slot is a pre-admitted placeholder with a generic query rather than
   an evidence-conditioned hypothesis agent; and
5. checkpoint retries can append new reports outside the committed dossier,
   making replay and final-state membership ambiguous.

The current task topology also creates structural task records without always
performing distinct research work, fragments evidence across many calls, and
uses a lexical rubric that can confuse wording differences with substantive
decision quality. G10R-T repairs those defects and isolates the value of each
society layer offline. It does not tune or rerun a live model.

## Objective

Implement a replay-safe, evidence-driven research cycle in which agents can
search, select a discovered candidate, lawfully fetch and map it, revise
viewpoint dossiers after new evidence, allocate focus to the highest-value
unresolved work, and admit an open-slot viewpoint only when the shared evidence
supports a distinct discriminator. Then run deterministic equal-actual-budget
ablations that separately measure the contribution of shared research support,
multiple viewpoints, and adaptive focus/open-slot discovery.

## Project outcomes advanced

- turns the agent overlay from discourse generation into attributable evidence
  acquisition and hypothesis revision;
- preserves the reusable problem-context, evidence, hypothesis, memory, focus,
  and authority contracts established by G07E, G10P, and G10D;
- produces an interpretable engineering verdict about whether another Phase-A
  freeze is worth proposing; and
- leaves scientific validation, source promotion, and physical execution with
  the existing human and laboratory gates.

## In scope

- the A1 and A2-M offline execution paths needed for a fair control;
- a two-stage search → candidate-selection → fetch/map tool loop;
- on-demand shared research, extraction, identity/lineage, contradiction, and
  experiment-design services driven by typed viewpoint evidence needs;
- versioned private dossiers and a post-evidence revision round;
- observed-yield focus scoring, highest-first allocation, task-specific
  follow-up work, and semantic work deduplication;
- post-landscape open-slot proposal, novelty review, admission, rejection, and
  abstention;
- exactly-once checkpoint/replay behavior across every state boundary;
- typed, wording-invariant task and discovery scoring; and
- deterministic ablations on recorded positive, negative, contradictory,
  malformed, partial-failure, budget-exhaustion, unsupported, and non-ceiling
  discovery fixtures.

## Explicit exclusions

- live OpenAI or other provider calls, network access, credentials, or paid
  execution;
- widening the source-host policy, query/fetch/token/cost ceilings, scientific
  support region, or evidence-promotion authority;
- tuning prompts or rubrics on the four paid sealed-case answers and then
  treating the replay as independent evidence;
- automatic Phase-A freezing or Phase-B activation;
- claims that deterministic fixtures establish real-model society value;
- laboratory contact, experiment authorization, safety approval, or material
  performance claims; and
- replacing the reusable substrate with a Roman-concrete-specific framework.

## Execution contract

### Expected implementation surface

- `src/roman_concrete_lab/agents/investigation.py`;
- `src/roman_concrete_lab/agents/viewpoint_society.py`;
- `src/roman_concrete_lab/agents/evidence_bus.py`;
- a bounded research-loop module under
  `src/roman_concrete_lab/agents/` if separation from the runner is clearer;
- `schemas/research-need.schema.json`;
- `schemas/candidate-selection.schema.json`;
- `schemas/viewpoint-dossier-revision.schema.json`;
- `schemas/open-viewpoint-admission.schema.json`;
- the existing focus, support-report, portfolio, and attribution schemas when
  compatible, or versioned replacements with migration tests;
- fixtures under `fixtures/investigation/research-loop/`;
- `tools/evaluation/society_research_loop_ablation.py`;
- `tests/agents/test_society_research_loop.py` and
  `tests/agents/test_society_research_loop_ablation.py`;
- `docs/protocols/viewpoint-society.md`,
  `docs/protocols/society-evidence-bus.md`, and
  `docs/protocols/active-investigation-pilot.md`; and
- `artifacts/goals/G10R-T/{diagnosis.json,ablation-matrix.json,run.json,replay.json,report.md}`.

Equivalent module or schema names are allowed only when the goal report maps
them explicitly to this contract.

### Canonical records and invariants

`ResearchNeed` contains `need_id`, case/problem/version, owning viewpoint and
claim IDs, task type, question, expected decision change, required evidence
kind, known candidate IDs, unresolved uncertainty, duplication key, budget
request, status, and provenance.

`CandidateSelection` contains the need and action IDs, selected stable
candidate ID, selection reason, candidate status, exact recorded content
locator when present, requested operation, policy decision, and status. A model
or fixture may select a candidate ID; it may not invent a free-form fetch
instruction and have it interpreted as a locator.

`ViewpointDossierRevision` contains a stable dossier ID, monotonic revision,
parent revision, included report/action/source/claim/critique IDs, unresolved
joins, revision reason, status, and content hash. Every accepted late report
creates or is included in a later revision before adjudication.

`OpenViewpointAdmission` is created only after the first shared evidence round.
It contains the proposed viewpoint, novelty basis, source/claim IDs, predicted
observation, falsifier, discriminator, overlap decision, and one of
`ADMITTED`, `REJECTED_REDUNDANT`, or `ABSTAINED_NO_DISTINCT_VIEWPOINT`. All
admitted claims remain `REVIEW_REQUIRED`.

The following invariants are mandatory:

- searching and fetching are separate turns; only a recorded candidate ID or
  exact policy-approved HTTPS locator may enter the fetch adapter;
- metadata discovery never becomes evidence credit without permitted content
  mapping and review;
- support services answer typed `ResearchNeed` records and may return
  `SUPPORTS`, `WEAKENS`, `NON_DISCRIMINATING`, or a reasoned abstention;
- task completion requires an observable action, mapped artifact, or typed
  discriminator; creating a status report alone is not completion;
- focus ranking is highest-first and uses observed source yield, unresolved
  decision value, novelty, provenance risk, duplication, and feasibility;
- null and credible-rival preservation constrains selection among the
  highest-value eligible tasks rather than forcing arbitrary low-value work;
- round-two evidence, critiques, and focus work are included in the latest
  dossier revisions and final adjudication packet;
- every checkpoint transition is exactly-once; resume may replay identical
  records but may not add a new report, debit, provider trace, or dossier member
  for completed work;
- discovery credit, evidence credit, task accuracy, and authority failures are
  separate; pending novel candidates are retained without direct-evidence
  promotion; and
- final scoring uses typed facts and source identity, not the presence of an
  exact phrase or morphological variant in free text.

### State and transition contract

The research cycle has these ordered stages:

```text
CREATED -> SEARCHING -> CANDIDATE_TRIAGE -> CONTENT_ACQUISITION
  -> EVIDENCE_MAPPING -> PRIVATE_REVISION -> SHARING -> CRITIQUING
  -> FOCUSING -> ROUND_2 -> ADJUDICATING -> SCORED -> COMPLETED
```

`BUDGET_EXHAUSTED`, `POLICY_BLOCKED`, and `INCONCLUSIVE` preserve the last
valid checkpoint and are terminal for that run. A run may skip
`CONTENT_ACQUISITION` or `EVIDENCE_MAPPING` only with an explicit typed reason
such as metadata-only, rights-blocked, no useful candidate, or unsupported
content. Illegal backward transitions, cross-case writes, stale manifests, and
conflicting duplicate IDs fail closed. A completed run replays its artifact
without work or budget debit.

### Offline ablation arms

All arms receive identical recorded source opportunities and identical actual
query, fetch, retained-source, token-equivalent, action, and stopping ceilings:

| Arm | Purpose |
|---|---|
| `R0_SINGLE` | one investigator using the repaired complete research loop |
| `R1_SHARED_SUPPORT` | one hypothesis owner delegating typed needs to shared research services; isolates support plumbing |
| `R2_VIEWPOINT_FIXED` | two candidate proponents plus a null using the same services and fixed equal focus; isolates viewpoint diversity |
| `R3_VIEWPOINT_ADAPTIVE` | R2 plus post-landscape open-slot admission and observed-yield adaptive focus; isolates discovery/focus behavior |

The runner records both declared and actual resource use. An arm that exceeds
an actual ceiling is invalid; unused resources are not imputed as work. The
ablation must report task accuracy, canonical-source recall, successful
fetch/card count, evidence-to-final handoff retention, unique attributable
contributions, contradiction/discriminator value, duplicate-work rate,
authority integrity, and cost/token-equivalent efficiency separately.

An added layer counts as directionally useful only when at least one frozen
non-ceiling fixture gains a unique attributable contribution or resolves a
decision-relevant uncertainty, total task accuracy is noninferior, no critical
authority failure occurs, and the arm stays within the same actual ceilings.
Fixture success is an engineering-readiness signal, never an adoption claim.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Search returns a permitted candidate with content locator | a later candidate-selection action may fetch it, map a page-aware card, and join it to the requesting need |
| Search returns metadata only | retain `CANDIDATE_PENDING`; issue a typed locator-seeking need or abstain; no evidence credit |
| Fetch request contains prose instead of candidate ID/HTTPS locator | `INVALID_FETCH_REQUEST`; preserve the request; do not call the adapter |
| Support finds evidence against its assigned viewpoint | retain `WEAKENS` in the next dossier revision and adjudication |
| A high- and low-value feasible focus task compete | allocate to the higher score, subject to high-value null/rival coverage |
| Two queries have different wording but the same need/candidate/decision target | reuse the first result and record semantic duplicate provenance |
| Round-two work adds a source or critique | increment the dossier revision and expose it to final adjudication and scoring |
| Open-slot proposal is distinct and attributable | admit after sharing with prediction, falsifier, and discriminator |
| Open-slot proposal duplicates an incumbent | record `REJECTED_REDUNDANT`; do not create an active placeholder |
| No distinct open viewpoint exists | record `ABSTAINED_NO_DISTINCT_VIEWPOINT`; continue normally |
| Checkpoint resumes after any completed stage | no repeated call, action, report, debit, or dossier membership |
| Wording changes but typed facts and source IDs do not | task score remains identical |
| Malformed, contradictory, unsupported, rights-blocked, or budget-exhausted input | preserve the typed failure/review state without evidence or authority promotion |

## Deliverables

1. A machine-readable diagnosis reproducing the paid-run resource and outcome
   facts and mapping every observed failure to a repair and test.
2. Versioned research-loop, dossier-revision, focus, open-slot, replay, and
   scoring contracts.
3. The repaired offline A1/A2-M execution paths and deterministic fixtures.
4. A four-arm ablation matrix and results with equal actual ceilings.
5. A criterion-to-test/artifact ledger, byte-stable replay artifact, and final
   report with one legal terminal verdict.

## Goal-level acceptance criteria

1. `diagnosis.json` reproduces the paid-run score, call, token, query, fetch,
   paper-card, and cost facts and identifies the five causal defects above
   without modifying historical artifacts.
2. A discovered candidate can be selected and lawfully fetched in a later turn
   by stable candidate ID, producing a validated page-aware card; prose fetch
   instructions and metadata-only candidates cannot enter the content adapter
   or receive evidence credit.
3. Shared support services execute typed viewpoint needs, preserve supporting,
   weakening, non-discriminating, and abstaining outcomes, and cannot mark work
   complete without an observable action, mapped artifact, or discriminator.
4. Every post-sharing report, critique, and focused action appears in a
   monotonic dossier revision consumed by adjudication; deliberate omission is
   detected as a failing diagnostic.
5. Focus allocation is highest-first, uses observed rather than constant
   branch statistics, performs task-specific follow-up, preserves a high-value
   null and rival, and suppresses semantic duplicate work with provenance.
6. The open slot runs only after first-round evidence sharing and deterministically
   exercises distinct admission, redundant rejection, and no-candidate
   abstention without a pre-admitted placeholder.
7. Resume from every stage boundary is exactly-once and produces the same final
   content hash, resource ledger, dossier memberships, and score as an
   uninterrupted run; stale/conflicting replay fails closed.
8. The four ablation arms run under identical actual ceilings, and the artifact
   separately reports the marginal effect of shared support, viewpoint
   diversity, and adaptive focus/open-slot behavior. Any noncompliant arm is
   invalid rather than normalized after the fact.
9. Typed scoring is invariant to wording-only changes, retains pending novel or
   contradictory candidates for collective review, and separates discovery,
   evidence, task-accuracy, efficiency, and authority outcomes.
10. Focused tests and `python3 -m pytest -q` pass; `run.json` and `replay.json`
    are byte-equivalent; the report emits exactly one of
    `SOCIETY_RESEARCH_LOOP_READY`, `SOCIETY_RESEARCH_LOOP_NO_GO`, or
    `INCONCLUSIVE_SOCIETY_RESEARCH_LOOP`.

## Criterion-to-evidence map

| Criterion | Required evidence |
|---|---|
| 1 | `artifacts/goals/G10R-T/diagnosis.json` plus immutable-input hash checks |
| 2 | search/select/fetch/map and invalid-fetch tests in `test_society_research_loop.py` |
| 3 | support-service stance/completion fixtures and tests |
| 4 | dossier-revision propagation and deliberate-omission tests |
| 5 | descending-focus, observed-statistics, task-specific follow-up, and semantic-dedup tests |
| 6 | admitted/redundant/abstained open-slot fixtures and tests |
| 7 | per-stage resume matrix, stale/conflicting replay tests, and `replay.json` |
| 8 | `ablation-matrix.json`, equal-actual-budget assertions, and ablation tests |
| 9 | synonym/permutation invariance, open-world candidate retention, and split-ledger tests |
| 10 | focused/full test logs, `run.json`, `replay.json`, and `report.md` |

## Stop conditions and handoff

Emit `SOCIETY_RESEARCH_LOOP_NO_GO` when the completed offline experiment shows
that no society layer improves attributable information flow or uncertainty
resolution without reducing task accuracy, violating authority, or exceeding
the actual control ceiling. Emit `INCONCLUSIVE_SOCIETY_RESEARCH_LOOP` when an
implementation, fixture, replay, or measurement defect prevents that
determination. Emit `SOCIETY_RESEARCH_LOOP_READY` only when all ten criteria
pass and at least one society layer meets the directional-usefulness rule.

No verdict authorizes a paid run. A positive handoff may propose a separate
fresh Phase-A freeze goal with new non-ceiling evaluation cases, repeated runs,
typed scoring, and an explicitly reviewed spend/model/network activation. A
no-go handoff preserves the society code for bounded task-specific use but
stops further active-investigation escalation until a materially different,
testable architecture is proposed.
