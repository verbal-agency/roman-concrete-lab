# G10R-I — Offline society runtime integration gate

**Status:** proposed
**Dependencies:** G10R-P complete with `TARGET_STATE_READY_FOR_OFFLINE_BUILD`; G10D and G10P complete; no model, network, subscription, credential, or laboratory execution
**Advances:** wires the intended G10D viewpoint society and G10P evidence bus into the live-capable investigation runner and proves the target-state invariants offline before another paid evaluation

## Why this goal exists

The G10R paid pilot used the legacy `mechanism_tournament` path rather than the
intended G10D `ViewpointSociety` plus G10P `EvidenceBus` topology. Its
checkpoints therefore contained no viewpoint, support-task, dossier, or
evidence-bus records, and the open slot was filtered out of live proponent
execution. G10R-P identified this as an integration gap, not a reason to spend
again immediately.

This goal makes runtime fidelity a separately testable gate. It does not claim
that the integrated society is useful, and it does not authorize live calls.

## Objective

Integrate the versioned G10D/G10P contracts into the A1/A2-M runner and prove,
using deterministic providers and repository-local fixtures, that:

1. viewpoint cards and private first-round dossiers are instantiated for each
   active viewpoint, the null, and the open slot;
2. retrieval, extraction/identity, contradiction, and experiment-design tasks
   are assigned to viewpoints and produce typed support reports;
3. support reports, source candidates, claims, actions, dossiers, critiques,
   focus decisions, and portfolios retain valid evidence-bus joins through
   checkpoint and score serialization;
4. open-slot admission and bounded follow-up work are exercised rather than
   merely represented in a roster;
5. permitted fetches produce page-aware evidence cards on the positive fixture,
   while unresolved candidates, weakening evidence, dissent, nulls, and rivals
   remain reviewable and unpromoted; and
6. A1 and A2-M retain equal aggregate budgets, deterministic replay, and the
   existing authority boundary.

## Scope and authority

This is an offline implementation and verification goal. It may modify the
runner, schemas, fixtures, checkpoints, replay tools, and tests. It may not call
an LLM, access the network or subscriptions, use credentials, send external
communications, promote evidence, authorize laboratory work, widen source
policy, or increase the G10R budget.

## Required implementation changes

- Replace the live A2-M legacy-only path with an explicit G10D/G10P runtime
  adapter or successor whose contract version is recorded in the manifest.
- Instantiate the open slot through the typed admission rule; do not silently
  treat a roster entry as an active viewpoint.
- Serialize typed viewpoint, support-task, support-report, dossier, critique,
  focus, candidate, claim, and portfolio records into checkpoints and the score
  ledger.
- Give each support task a bounded action budget, stance (`SUPPORTS`,
  `WEAKENS`, or `NON_DISCRIMINATING`), and an attributable outcome or abstention
  reason.
- Add a deterministic positive public-content fixture with page-aware
  extraction and a negative fixture for rights/policy blocking.
- Preserve the existing open-world semantics: unresolved or unattributed
  candidates remain in the canon, receive no direct-evidence credit, and do not
  become fabricated merely because identity is incomplete.

## Acceptance criteria

1. The runner's manifest identifies the G10D/G10P runtime path and no longer
   relies on the legacy mechanism tournament as the sole A2-M implementation.
2. Offline traces contain private first-round viewpoint records, assigned
   support tasks for all required task types, typed support reports, shared
   dossiers, cross-viewpoint critiques, focus decisions, and an adjudicated
   portfolio.
3. The open slot is admitted through a typed record and receives bounded work;
   the null and at least one credible rival remain visible to adjudication.
4. The evidence-bus join rate is 100% for accepted support reports, claims,
   actions, source candidates, dossiers, critiques, and portfolios; conflicting
   or stale joins fail deterministically.
5. A positive fetch fixture yields a page-aware evidence card, while negative
   rights/policy fixtures retain diagnostics without prohibited payloads.
6. Offline replay is byte-stable across checkpoint/resume, duplicate action,
   unresolved identity, weakening support, dissent, and partial-failure cases.
7. Budget and authority equality checks pass for A1 and A2-M; no role receives
   extra aggregate capability, and no record can promote evidence or authorize
   a lab.
8. The full test suite passes and the goal emits exactly one handoff:
   `RUNTIME_INTEGRATION_READY`, `RUNTIME_INTEGRATION_NO_GO`, or
   `INCONCLUSIVE_RUNTIME_INTEGRATION`.

## Handoff

`RUNTIME_INTEGRATION_READY` is necessary but not sufficient for another paid
run. A later goal must freeze a fresh Phase-A manifest, revalidate reachable
sealed cases, and obtain explicit owner activation of the lawful source policy,
model, and spend cap. Any failure leaves G10R's `DO_NOT_ESCALATE_ACTIVE_SOCIETY`
decision authoritative.

## Stop conditions

Emit `RUNTIME_INTEGRATION_NO_GO` if the intended topology cannot be enforced,
support-task joins are lossy, open-slot work cannot be bounded, or evidence and
authority boundaries cannot be preserved. Emit
`INCONCLUSIVE_RUNTIME_INTEGRATION` if deterministic replay or budget equality
cannot be demonstrated. Do not request another paid run from a partial gate.
