# G10R-AE — Freeze Phase A after runner intake integration

**Status:** complete — `PHASE_A_READY_FOR_OWNER_ACTIVATION`
**Dependencies:** G10R-AD `RUNNER_PROVISIONAL_INTAKE_READY`; no live model,
network, subscription, credential, laboratory, or paid execution
**Authority:** offline manifest construction, fault injection, and deterministic
verification only; this goal may not initialize a provider, open the network,
or authorize a Phase-B run

## Objective

Create a new, immutable Phase-A manifest that includes the runner-facing
provisional-intake adapter, conflict-set schemas, source policy, budgets,
fixtures, and replay contract. Verify that the exact manifest can be activated
later only by a separate owner decision, without mutating G10R-X, G10R-AC, or
any historical paid artifacts.

## In scope

- hash the additive runner adapter, intake/conflict schemas, protocol, source
  policy, deterministic fixtures, and focused test contract;
- record a pending owner activation request naming the exact manifest ID/hash,
  provider/model policy, read-only source policy, budgets, output namespace,
  and no-promotion authority boundary;
- run offline fault injection for stale manifest, changed schema, conflicting
  duplicate, cross-case checkpoint, malformed conflict record, budget limit,
  and byte-stable replay; and
- produce a handoff that distinguishes freeze readiness from scientific or
  society usefulness.

## Explicit exclusions

No provider or network initialization, credentials, subscription retrieval,
new source host, budget increase, paid run, automatic activation, evidence
promotion, laboratory authorization, or prompt tuning against sealed outputs.

## Expected implementation surface

- `tools/evaluation/fresh_phase_a_freeze_after_runner_intake.py`;
- additive manifest/preflight schemas or explicitly mapped equivalents;
- `tests/agents/test_g10r_ae_fresh_phase_a_freeze.py`;
- `artifacts/goals/G10R-AE/{manifest,preflight,criterion-ledger,report}.json/md`;
- unchanged historical artifacts under `artifacts/goals/G10R-X/`,
  `artifacts/goals/G10R-AC/`, and `artifacts/goals/G10R-AB/`.

## Canonical manifest requirements

The manifest must bind the G10R-AD protocol version, runner-adapter hash,
conflict schemas, provisional-intake schema, source-policy hash, budget
limits, fixture hashes, focused-test hash, output namespace, and a distinct
manifest ID. Any changed input requires a new manifest namespace. Activation
remains `PENDING_OWNER_ACTIVATION` and cannot be inferred from the freeze.

## Acceptance criteria

1. The manifest is distinct from and does not overwrite G10R-X or earlier
   manifests; every declared input has a stable SHA-256 hash.
2. The manifest includes the runner-facing intake adapter, conflict-set and
   adjudication schemas, source policy, budgets, fixtures, and protocol
   versions used by G10R-AD.
3. Offline preflight rejects stale manifests, changed inputs, conflicting
   duplicate records, cross-case checkpoints, malformed conflict records, and
   cap violations before any external adapter could initialize.
4. Offline replay is byte-stable, performs zero provider/network/credential
   calls, and debits zero budget; historical artifacts remain byte-identical.
5. The activation request names the exact manifest ID/hash and preserves the
   no-promotion, read-only, and scientific-authority boundaries.
6. Focused tests, the full repository suite, `git diff --check`, and the
   criterion ledger pass.

## Handoff

Return exactly one of `PHASE_A_READY_FOR_OWNER_ACTIVATION`,
`PHASE_A_FREEZE_NO_GO`, or `INCONCLUSIVE_PHASE_A_FREEZE`. The first permits a
separately authorized owner activation; it does not itself make live calls or
authorize a paid run.

## Completion evidence

The freeze artifacts under `artifacts/goals/G10R-AE/` pass all six criteria.
The focused freeze/intake tests pass (`11 passed`); the full repository suite
passes (`195 passed`); and `git diff --check` passes. The fault matrix exercises
the real rejection paths for stale manifests, changed inputs, conflicting
duplicates, cross-case checkpoints, malformed conflict records, and cap
violations. Historical G10R-X, G10R-AC,
and G10R-AB artifacts remain unchanged. The freeze made zero model calls,
network calls, credential reads, or paid spend.
