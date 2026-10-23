# G10R-F — Fresh Phase-A freeze after constraint remediation

**Status:** complete — `PHASE_A_READY_FOR_OWNER_ACTIVATION`
**Dependencies:** G10R-C `PRE_RERUN_CONSTRAINTS_READY`; G10R-A `ACQUISITION_DESIGN_READY`; no paid run authorized
**Authority:** offline repository work only; no model, network, subscription, credential, laboratory, or external communication

## Objective

Recompute and freeze a fresh G10R Phase-A manifest after the broad constraint
remediation. Prove that the repaired runner, schemas, source policy, society,
evidence bus, fixtures, and budgets are the exact inputs to the next evaluation.
This goal prepares a run; it does not execute Phase B or spend money.

## In scope

- run the deterministic `phase_a()` preflight against the repaired tree;
- write a separately named Phase-A artifact and manifest hash under
  `artifacts/goals/G10R/` without overwriting historical manifests;
- verify all development/sealed cases, behavior fixtures, PDF benchmark,
  identity map, mechanism rosters, prompt hashes, source-policy hash, and equal
  arm budgets;
- verify the new locator-resolution and action-status schema contracts are in
  the manifest input set;
- produce a frozen activation request that states the model/provider, exact
  hosts, aggregate cap, and explicit owner activation requirement.

## Explicit exclusions

No model or network calls, no retrieval, no subscription access, no new cases,
no budget increase, no source-policy change, no evidence promotion, no paid
Phase-B execution, and no laboratory or external communication.

## Execution contract

### Expected implementation surface

- `src/roman_concrete_lab/agents/investigation.py:phase_a` and
  `frozen_manifest`;
- `schemas/investigation-action.schema.json`;
- `artifacts/goals/G10R/phase-a-post-constraint-20261023.json`;
- `artifacts/goals/G10R/manifest-post-constraint-20261023.json`;
- `artifacts/goals/G10R/report-post-constraint-20261023.md`;
- focused tests in `tests/agents/test_active_investigation.py` and a new
  Phase-A freeze test.

### Canonical invariants

- Phase-A status is exactly `AWAITING_OWNER_ACTIVATION`;
- manifest hash is derived from the manifest bytes and matches the Phase-A
  record;
- all four sealed cases and at least two development cases are present and
  disjoint;
- source policy is unchanged, exact-host, read-only, and default-deny;
- A1, A2-M, and A0 use equal per-treatment aggregate limits;
- no credentials, raw source payloads, model traces, or external side effects
  are written by the freeze;
- historical `phase-a.json` and manifests remain untouched.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Repaired tree and complete fixtures | `AWAITING_OWNER_ACTIVATION` with a manifest hash |
| Missing/changed input fixture | `PHASE_A_INVALID` or a deterministic validation error |
| Repeated freeze with unchanged inputs | byte-equivalent manifest and Phase-A output |
| Existing historical artifact | preserved; new artifact uses a distinct name |
| Any model/network/provider invocation | prohibited and treated as a goal failure |

## Acceptance criteria

1. A fresh named Phase-A artifact and manifest are produced without overwriting
   historical G10R artifacts.
2. The artifact reports `AWAITING_OWNER_ACTIVATION`, a matching manifest hash,
   four sealed cases, at least two development cases, passing identity,
   mechanism-roster, behavior-fixture, and PDF benchmarks.
3. The manifest includes the repaired runner/schema inputs, exact source-policy
   hash and hosts, equal budgets, model/provider declaration, and $25 hard cap.
4. Two offline freezes are byte-stable and make no model, network, credential,
   subscription, promotion, laboratory, or external write.
5. The report emits exactly one handoff:
   `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or
   `INCONCLUSIVE_PHASE_A_FREEZE`.

## Stop conditions

Emit `PHASE_A_FREEZE_NO_GO` if any manifest input is missing or changed during
the freeze, if budgets or source policy differ, if a benchmark/preflight fails,
or if historical artifacts would be overwritten. A positive handoff only makes
Phase B eligible for a separately authorized paid run; it does not authorize
that run.
