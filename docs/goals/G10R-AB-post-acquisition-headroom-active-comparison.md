# G10R-AB — Instrumented post-acquisition-headroom integration pilot

**Status:** complete — `INCONCLUSIVE_ACTIVE_INVESTIGATION` (common content-headroom collapse)
**Dependencies:** G10R-AA `PHASE_A_READY_FOR_OWNER_ACTIVATION`; explicit owner
activation naming the exact G10R-AA manifest ID and SHA-256, provider/model,
read-only network permission, frozen source policy, `$25.00` cap, and output
namespace
**Authority:** no provider, network, credential, subscription, or paid action
is permitted until the owner activates this goal; the run remains an
engineering evaluation and cannot promote evidence, authorize a laboratory, or
adopt the society for production

## Objective

Run one separately namespaced, instrumented A1 single-investigator versus
A2-M society integration pilot using the G10R-AA manifest and the additive
`AcquisitionHeadroomRunner`. The pilot must test the repaired stack as a whole
while retaining the scientific comparison: it should expose failures at
admission, retrieval, parsing, evidence credit, viewpoint contribution,
synthesis, replay, and budget boundaries in one bounded run, then determine
whether A2-M produces a unique, source-backed contribution under equal
aggregate budgets. A typed case-level failure should be recorded and the run
should continue where safe; a common zero-content or unresolved integration
result is `INCONCLUSIVE_ACTIVE_INVESTIGATION`, not evidence that the society is
useful or useless.

## Activation gate

Before provider or network initialization, the execution must verify the exact
G10R-AA manifest ID and SHA-256, `openai` Responses API model policy, the
read-only exact-host source policy, the `$25.00` hard aggregate cap, and the
distinct output namespace `artifacts/goals/G10R-AB/`. A cycle invocation,
committed manifest, or pending request does not satisfy activation.

## In scope

- the four frozen sealed cases and A1/A2-M treatments from G10R-AA;
- exact-route resolution, public-content fetch/map, typed metadata-only and
  rights-blocked outcomes, delayed open-slot admission, need-driven support,
  checkpointed dossier/research-loop state, and source-backed scoring;
- per-case and aggregate provider calls, queries, fetches, tokens, payload,
  cost, stop state, and source-policy decisions;
- blinded scoring and a report separating discovery, evidence cards,
  hypotheses, discriminators, contradictions, unresolved identity, blocked
  access, open-slot work, and society overhead; and
- an end-to-end event ledger for each boundary transition, including case,
  arm, agent, stage, action, locator, outcome, evidence delta, configuration
  flags, retries, latency, tokens, cost, and terminal/continuation status;
- a frozen repair/configuration manifest that records which bundled fixes are
  active and makes their presence observable without changing behavior during
  the run;
- a pre-run offline fault-injection matrix covering malformed provider output,
  empty or blocked retrieval, duplicate evidence, stale joins, open-slot
  admission, partial failure, budget exhaustion, and replay; and
- a post-run infrastructure postmortem that classifies failures as plumbing,
  acquisition, agent design, scoring, provider integration, or scientific
  outcome before applying the society decision rule; and
- deterministic offline replay of the completed run.

## Explicit exclusions

No source-policy or budget expansion, new hosts, subscriptions, Sci-Hub
access, laboratory work, evidence promotion, automatic retry after a terminal
outcome, or follow-on paid run. Simulation remains
`SIMULATOR_UNAVAILABLE`; synthetic or unvalidated output earns no empirical
credit.

## Canonical records and implementation surface

Expected implementation surface: an additive paid-run wrapper under
`tools/evaluation/`, `src/roman_concrete_lab/agents/investigation_g10r_z.py`,
the frozen `artifacts/goals/G10R-AA/manifest.json`, focused tests under
`tests/agents/`, and an explicit event/repair configuration schema. Canonical
outputs are immutable after completion:

- `artifacts/goals/G10R-AB/activation.json`;
- `artifacts/goals/G10R-AB/manifest.json`;
- `artifacts/goals/G10R-AB/repair-config.json`;
- `artifacts/goals/G10R-AB/preflight.json`;
- `artifacts/goals/G10R-AB/criterion-ledger.json`;
- `artifacts/goals/G10R-AB/run.json` plus per-case checkpoints;
- `artifacts/goals/G10R-AB/replay.json`;
- `artifacts/goals/G10R-AB/spend-ledger.json`;
- `artifacts/goals/G10R-AB/event-ledger.json`;
- `artifacts/goals/G10R-AB/infrastructure-postmortem.json`;
- `artifacts/goals/G10R-AB/report.md`.

Every record binds the G10R-AA manifest ID/hash, case, arm, treatment, source
policy hash, output namespace, repair/configuration flags, and budget envelope.
Conflicting duplicate IDs, stale manifests, changed policy, cross-case
checkpoints, or cap violations fail closed. Typed provider, retrieval, parsing,
or scoring failures do not abort unrelated cases; they are preserved in the
event ledger and may only produce an inconclusive terminal result when they
prevent a fair comparison.

## Decision rule

Return `ESCALATE_ACTIVE_SOCIETY_EVALUATION` only if A2-M has at least one
unique source-backed contribution absent from A1, A2-M is non-inferior in total
score, there is at least one per-case gain, and there are no critical authority,
rights, provenance, or replay failures. Return
`DO_NOT_ESCALATE_ACTIVE_SOCIETY` when the comparison completes validly but the
rule is not met. Return `INCONCLUSIVE_ACTIVE_INVESTIGATION` when either arm
fails, the common content-headroom condition collapses, or attribution cannot
be resolved. A metadata-only contribution, open-slot admission, discourse,
consensus, or raw discovery count alone cannot qualify.

## Completed run result

The owner-activated run completed all eight case/arm checkpoints under the
frozen manifest and spent `$0.0289856` of the `$25.00` cap. All arms fetched
zero permitted documents and earned zero evidence score, so the legal result
is `INCONCLUSIVE_ACTIVE_INVESTIGATION`, not a valid society comparison. The
run produced 126 structured events and replayed byte-stably with zero calls or
spend during finalization. The infrastructure postmortem routes the remaining
problem to acquisition/content-headroom diagnosis.

## Goal-level acceptance criteria

1. Without the exact owner activation, the runner refuses before initializing
   a provider or network adapter; stale or altered G10R-AA inputs fail closed.
2. The run uses the exact G10R-AA manifest, distinct output namespace, frozen
   source policy, four sealed cases, and unchanged A1/A2-M ceilings.
3. Both arms record equal declared ceilings and actual queries, fetches,
   payload, input/output tokens, provider calls, cost, and stop states; the
   aggregate spend never exceeds `$25.00`.
4. Both arms use `AcquisitionHeadroomRunner`; every fetch records a shared
   resolver outcome, public content can produce a page-aware card, and
   metadata-only/rights-blocked/invalid routes produce zero card credit.
5. Every candidate, resolution, selection, fetch, card, support report,
   dossier revision, critique, focus decision, open-slot decision, portfolio,
   and score binds to stable case/arm/action lineage.
6. A2-M creates no open-slot task or dossier before the shared-evidence gate;
   support tasks are need-driven and an abstained open slot creates no work.
7. The score ledger separates raw discovery, evidence, useful hypotheses,
   discriminators, attribution, provenance, authority, and efficiency; wording
   alone cannot produce credit.
8. The report emits exactly one legal terminal outcome and states that the
   result is not scientific validation, evidence promotion, laboratory
   authorization, or production adoption.
9. Completed replay is byte-stable, makes zero provider/network calls, and
   debits zero budget; conflicting or partial checkpoints fail closed while
   preserving completed evidence.
10. The repair/configuration manifest and event schema are frozen before any
    provider call; every active repair is visible in the run records and no
    configuration changes during execution.
11. The offline fault-injection matrix exercises each listed boundary failure,
    proves typed continuation where safe, and proves fail-closed behavior for
    authority, cap, provenance, and cross-case violations.
12. Focused tests, the full repository suite, and the offline replay pass;
    G10R-AA, G10R-Z, and all earlier historical artifacts remain unchanged.

## Criterion-to-test/artifact map

| criterion | verification |
|---|---|
| 1 | activation-gate and stale-manifest tests; `activation.json` |
| 2 | manifest/policy/namespace tests; `manifest.json` |
| 3 | equal-ceiling and spend-ledger tests; `spend-ledger.json` |
| 4 | resolver/card/no-content tests; per-case `run.json` checkpoints |
| 5 | lineage-schema and checkpoint tests; `run.json` |
| 6 | delayed-admission/support tests; society checkpoint |
| 7 | blinded scorer tests; score ledger and `report.md` |
| 8 | terminal-verdict and authority-boundary tests; `report.md` |
| 9 | replay, duplicate, stale-checkpoint tests; `replay.json` |
| 10 | repair/configuration freeze tests; `manifest.json` and `event-ledger.json` |
| 11 | offline fault-injection tests; replay and criterion ledger |
| 12 | focused/full `pytest`, `git diff --check`, and historical hash audit |

## Stop conditions and handoff

Stop with `INCONCLUSIVE_ACTIVE_INVESTIGATION` for common zero-content
evaluation, provider/network failure, stale context, cap exhaustion, or
unresolved attribution. Preserve all typed failures and complete unaffected
cases before stopping. Stop with `DO_NOT_ESCALATE_ACTIVE_SOCIETY` for a valid
non-qualifying comparison. No result authorizes lab work; any later adoption
or physical work requires the existing expert and facility gates.
