# G10R-AA — Freeze Phase A after acquisition-headroom repair

**Status:** complete — `PHASE_A_READY_FOR_OWNER_ACTIVATION`
**Dependencies:** G10R-Z complete with `ACQUISITION_HEADROOM_READY`; owner
review of the offline report; no paid activation
**Authority:** repository-local manifest generation, fixture validation, and
deterministic subprocess tests only. No model, network, credential,
subscription, laboratory, external communication, or Phase-B execution.

## Objective

Wire the additive G10R-Z exact-locator, headroom, delayed-open-slot,
need-driven support, and scorer-parity contracts into a live-capable A1/A2-M
entrypoint without changing historical G10R-X inputs. Then create a new,
independently reviewable Phase-A manifest that hashes the wired entrypoint and
records an owner-activation request for a possible later paid run; do not
activate it.

## Project outcomes advanced

- makes the repaired acquisition treatment reproducible and reviewable;
- keeps source policy, budgets, stopping rules, and authority unchanged;
- preserves historical manifests and negative paid-run evidence; and
- separates freeze readiness from owner/provider/network activation.

## In scope and exclusions

In scope: manifest construction, file hashes, schema and fixture preflight,
fresh output namespace, predecessor linkage, owner-activation request, and
offline replay. Excluded: source-policy widening, new retrieval, model calls,
credentials, paid execution, evidence promotion, lab work, or edits to prior
goal artifacts.

## Execution contract

Expected implementation surface: a new additive live entrypoint such as
`src/roman_concrete_lab/agents/investigation_g10r_z.py` (or an equivalent
wrapper), `tools/evaluation/fresh_phase_a_freeze_after_acquisition_headroom.py`,
`artifacts/goals/G10R-AA/manifest.json`, `preflight.json`, `replay.json`,
`criterion-ledger.json`, `report.md`, and
`tests/agents/test_g10r_aa_fresh_phase_a_freeze.py`. The manifest must hash
`src/roman_concrete_lab/agents/acquisition.py`, the G10R-Z schemas, fixtures,
tool, tests, source policy, and relevant protocol documents.

Canonical records are immutable `manifest.json`, `preflight.json`, and
`owner-activation-request.json` with schema version `g10r-aa.1`, predecessor
manifest ID, source-policy hash, fixture hash, hard ceilings, treatment IDs,
and status `PHASE_A_READY_FOR_OWNER_ACTIVATION`, `PHASE_A_FREEZE_NO_GO`, or
`INCONCLUSIVE_PHASE_A_FREEZE`. A manifest may be created once; conflicting
duplicate IDs, stale predecessor hashes, changed policy, missing headroom, or
historical-path mutation fail closed.

Behavior matrix: unchanged G10R-Z fixture hashes and policy produce a fresh
owner-activation-ready manifest; any positive fixture without `READY` headroom
produces freeze no-go; changed source policy or schema produces stale-context
inconclusive; duplicate replay returns the same manifest with zero calls and
zero budget debit; malformed or cross-goal paths fail closed.

Authority boundary: only declared repository reads/writes and verification
subprocesses are allowed. The tool must not initialize providers, read API
credentials, open network access, spend money, mutate historical artifacts,
promote evidence, or authorize laboratory action.

## Goal-level acceptance criteria

1. The additive live entrypoint uses the shared resolver and preserves exact
   typed no-content outcomes, delayed admission, support completion, and
   source-backed score parity in an offline runner smoke test.
2. The new manifest has a unique ID, predecessor linkage to G10R-Z, and hashes
   every declared implementation, schema, fixture, protocol, and test input.
3. Every positive G10R-Z headroom fixture is `READY` under the same policy hash
   and both arm ceilings; otherwise the freeze is `PHASE_A_FREEZE_NO_GO`.
4. The manifest records unchanged source policy, model/provider policy, query,
   fetch, payload, simulation, token, cost, and stopping ceilings.
5. The new output namespace is distinct and no historical G10R-X, G10R-V,
   G10R-Y, or G10R-Z file hash changes during preflight.
6. The owner-activation request is recorded separately and has status
   `PENDING_OWNER_ACTIVATION`; it cannot be consumed by the freeze tool.
7. Duplicate manifest generation and replay are byte-stable with zero external
   calls, provider calls, credentials, or budget debit.
8. Stale predecessor, changed policy, missing schema, malformed fixture, and
   cross-case input each produce an attributable fail-closed result.
9. `criterion-ledger.json` maps each criterion to named tests and artifacts,
   and `report.md` emits exactly one legal verdict.
10. Focused tests and the full repository suite pass.
11. The report explicitly states that G10R-AA does not authorize Phase B,
    evidence promotion, or laboratory work.

## Criterion-to-test/artifact map

| criterion | verification |
|---|---|
| 1 | `tests/agents/test_g10r_aa_fresh_phase_a_freeze.py::test_live_wrapper_preserves_g10r_z_contracts`; wrapper smoke artifact |
| 2 | `test_manifest_links_predecessor_and_hashes_inputs`; `manifest.json` |
| 3 | `test_positive_headroom_and_policy_hash_match`; `preflight.json` |
| 4 | `test_manifest_preserves_frozen_ceilings`; `manifest.json#limits` |
| 5 | `test_historical_hashes_and_namespace_are_distinct`; `preflight.json` |
| 6 | `test_activation_request_is_pending_only`; `owner-activation-request.json` |
| 7 | `test_replay_is_byte_stable_and_external_free`; `replay.json` |
| 8 | `test_stale_malformed_and_cross_case_inputs_fail_closed`; `criterion-ledger.json` |
| 9 | `test_criterion_ledger_and_single_verdict`; `criterion-ledger.json`, `report.md` |
| 10 | focused and full `pytest` logs |
| 11 | `report.md` authority section |

## Stop conditions and handoff

Return `PHASE_A_FREEZE_NO_GO` for missing/invalid headroom, hash drift, or
historical mutation. Return `INCONCLUSIVE_PHASE_A_FREEZE` for an implementation
or replay defect. A ready result permits a separately authorized G10R-AB paid
comparison request; it does not execute or authorize that comparison.
