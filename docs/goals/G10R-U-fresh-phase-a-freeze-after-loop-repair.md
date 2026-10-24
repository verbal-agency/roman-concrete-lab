# G10R-U — Freeze a fresh Phase-A manifest after research-loop repair

**Status:** proposed
**Dependencies:** G10R-T complete with `SOCIETY_RESEARCH_LOOP_READY`; G10R-F
historical freeze remains immutable; no paid activation
**Authority:** repository-local manifest and deterministic preflight work only;
no model calls, network retrieval, subscriptions, credentials, laboratory work,
or external communication

## Objective

Freeze a new, separately named Phase-A manifest that includes the G10R-T
research-loop contracts and implementation, proves the exact tree intended for
a later evaluation, and records an owner activation request. This goal prepares
an optional fresh paid evaluation; it does not execute Phase B or imply that the
offline fixture result generalizes to real-model agents.

## In scope

- recompute the repository, schema, fixture, protocol, and evaluator hashes;
- include the four research-loop schemas, fixture, runner, evaluator, tests,
  and `G10R-T` artifacts in the manifest;
- verify the four-arm offline result and byte-stable replay before freezing;
- preserve the historical G10R-F/B2/S artifacts and namespaces;
- record the exact model/provider, source policy, aggregate budgets, $25 cap,
  and explicit owner/provider/network activation requirement for a later goal;
- write a manifest, readiness report, and activation request under a new
  `artifacts/goals/G10R-U/` namespace.

## Explicit exclusions

No model or network calls, document retrieval, subscription or Sci-Hub access,
new source hosts, budget increase, evidence promotion, scientific or safety
approval, laboratory work, or paid rerun. A successful freeze authorizes only a
future separately invoked paid goal after the owner reviews the request.

## Required deliverables

- `artifacts/goals/G10R-U/manifest.json` with immutable input hashes and a new
  manifest ID;
- `artifacts/goals/G10R-U/readiness.json` with the G10R-T verdict, replay hash,
  full-suite test result, and no-live-side-effect assertion;
- `artifacts/goals/G10R-U/activation-request.md` naming the exact model,
  source-policy version, aggregate ceilings, and explicit activation boundary;
- `tests/agents/test_g10r_u_fresh_phase_a_freeze.py` covering stale historical
  manifest protection, hash inclusion, and owner-activation separation.

## Goal-level acceptance criteria

1. The manifest is deterministic, has a new ID, includes all G10R-T source,
   schema, fixture, protocol, evaluator, test, and artifact paths, and does not
   overwrite G10R-F or G10R-B2 artifacts.
2. Every listed input exists and its recorded SHA-256 matches at freeze time;
   a changed input or stale manifest fails closed.
3. The freeze report records `SOCIETY_RESEARCH_LOOP_READY`, the replay artifact
   hash, and a passing full-suite test command; no model, network, credential,
   subscription, or laboratory side effect occurs.
4. The activation request states the exact model/provider, frozen source policy
   and hosts, per-arm ceilings, aggregate `$25` cap, and that owner/provider/
   network activation is required before any paid call.
5. Focused tests and `python3 -m pytest -q` pass, and the report emits exactly
   one of `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or
   `INCONCLUSIVE_PHASE_A_FREEZE`.

## Handoff

Only `PHASE_A_READY_FOR_OWNER_ACTIVATION` may make a separately authored paid
run goal eligible. It does not activate that goal automatically.
