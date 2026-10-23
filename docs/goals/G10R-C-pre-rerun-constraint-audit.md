# G10R-C — Pre-rerun constraint audit and remediation

**Status:** complete — `PRE_RERUN_CONSTRAINTS_READY`
**Dependencies:** completed G10R-A; refreshed G10R Phase-B rerun with `DO_NOT_ESCALATE_ACTIVE_SOCIETY`; no new model, network, subscription, or laboratory work
**Authority:** offline repository work only

## Why this goal exists

The latest paid retry removed one confound (planner-output truncation), but it
still produced no page-aware evidence card. A2-M made three fetch requests and
all were blocked because the model supplied provider IDs rather than permitted
content locators. That is evidence of a broader contract problem, not proof
that one locator string is the only defect. Before another run, the system
needs a complete audit of the constraints that may be shaping behavior.

## Objective

Inventory every behavior-shaping restriction across prompts, output schemas,
task and focus policy, locator and retrieval adapters, source policy, evidence
joins, runtime budgets, checkpoint/replay, and scoring. Classify each
restriction as an intentional boundary, declared experimental limit, accidental
confound, or unknown. Remediate accidental confounds offline, preserve rights,
safety, authority, and aggregate-budget boundaries, and prove the repaired
system through deterministic replay before any fresh Phase-A freeze.

## In scope

- a constraint matrix naming the source file/field, affected arm or task,
  intended purpose, observed effect, classification, remediation, and test
  evidence;
- fetch semantics that distinguish provider IDs, metadata locators, permitted
  direct-content locators, page locators, and unresolved references; IDs may be
  resolved only through bounded candidate records or precise policy blocks;
- positive public-PDF, metadata-only, rights-blocked, malformed, unavailable,
  and no-useful-result fixtures;
- robust plan, report, critique, and portfolio output handling for truncation,
  compact schema-valid output, retry/resume, and equal per-arm aggregate
  output ceilings;
- task/focus allocation, retrieval, extraction, identity, contradiction,
  experiment-design, and explicit `NOT_REQUESTED` versus runner/policy
  rejection semantics;
- candidate, action, task, viewpoint, card, dossier, and score-ledger joins;
- checkpoint duplicate, partial, stale, and replay behavior;
- scorer distinctions among request cause, acquisition, card yield, useful
  hypothesis, weakening, unresolved identity, blocked access, and overhead;
- deterministic equal-budget A1, A2-M, and no-fetch control comparisons.

## Explicit exclusions

No paid/model/network calls, new hosts, subscription retrieval, budget increase,
new sealed cases, lab work, source-policy widening, evidence promotion, or
production adoption. A positive handoff authorizes only a fresh Phase-A
manifest; it does not authorize a paid Phase-B run.

## Constraint classification rule

Every restriction must state what behavior it shapes, why it is necessary, which
arm it affects, and how its effect is observed. Rights, safety, authority, and
aggregate cost ceilings remain frozen. Silent abstention, an unreachable
permitted locator, output truncation, dropped joins, or unequal capabilities
are treated as accidental confounds until demonstrated otherwise. Open-world
agents may surface new candidates, arguments, and sources; those remain
reviewable and provisional until the existing evidence and authority contracts
validate them.

## Audit matrix

| Layer | Questions to answer |
|---|---|
| Prompt and schema | Can each role state a useful plan, uncertainty, dissent, and request without forced-empty fields or truncation? |
| Task and focus | Can actionable uncertainty allocate retrieval, extraction, contradiction, and design work before rhetoric or adjudication? |
| Locator and retrieval | Can a lawful provider ID be resolved or clearly blocked, and can a permitted direct locator reach a page-aware fixture? |
| Source policy | Are public, metadata-only, blocked, malformed, and unavailable sources distinguishable without silently narrowing discovery? |
| Evidence bus | Do source, action, task, viewpoint, card, candidate, and dossier joins survive variants and dissent? |
| Budget and runtime | Are action, retrieval, token, and cost ceilings equal in aggregate, with retry/resume visible rather than silently suppressed? |
| Checkpoint and replay | Do duplicate, partial, stale, and resumed traces remain byte-stable and side-effect free? |
| Scoring | Are acquisition, evidence, hypotheses, weakening, unresolved work, blocked access, and overhead scored separately? |

## Acceptance criteria

1. The constraint matrix covers every behavior-shaping restriction found in the
   audit and classifies it with inspectable evidence.
2. Accidental confounds are remediated or explicitly owner-accepted;
   intentional boundaries are unchanged and documented.
3. Provider-ID, permitted direct-content locator, metadata-only, and blocked
   locator cases are distinct; the permitted case reaches a page-aware card.
4. Truncated, compact, malformed, and schema-valid outputs are handled without
   silent abstention; retry/resume and equal aggregate output ceilings are
   recorded.
5. Every required support task can be requested, allocated, executed, or
   reported as a typed block/stance rather than disappearing.
6. Candidate, evidence, viewpoint, dossier, dissent, and score joins survive
   duplicate, partial, and stale checkpoint replay.
7. The score ledger reports request cause, acquisition, card yield, hypothesis,
   weakening, unresolved identity, blocked access, and overhead separately for
   A1, A2-M, and the no-fetch control.
8. Two offline replays are byte-stable, the full test suite passes, and no
   network, credential, subscription, promotion, or external side effect
   occurs.
9. The report emits exactly one handoff:
   `PRE_RERUN_CONSTRAINTS_READY`, `PRE_RERUN_CONSTRAINTS_NO_GO`, or
   `INCONCLUSIVE_CONSTRAINT_AUDIT`.

## Stop conditions

Emit `PRE_RERUN_CONSTRAINTS_NO_GO` if an accidental confound remains in
permitted acquisition, capabilities or aggregate budgets are unequal, joins or
replay remain lossy, or authority boundaries are weakened. Only
`PRE_RERUN_CONSTRAINTS_READY` unlocks a fresh Phase-A manifest; it does not
authorize a paid run by itself.
