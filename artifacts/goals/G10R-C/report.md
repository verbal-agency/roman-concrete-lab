# G10R-C pre-rerun constraint audit

## Handoff

`PRE_RERUN_CONSTRAINTS_READY`

The audit found and repaired one material accidental confound: the runner
treated provider IDs and metadata locators as fetch URLs even when the
candidate record already contained a lawful public `content_locator`. The
runner now resolves only exact candidate-record references and records the
resolution type. Runner rejection, policy blocking, and budget exhaustion are
also distinct action/event outcomes. The source allowlist, rights boundary,
authority boundary, and aggregate budgets were not widened.

## Verification

The machine-readable evidence is in `replay.json`. It records an eight-layer
constraint matrix, provider-ID/direct-locator resolution fixtures, compact and
malformed output fixtures, equal-budget score rows for A1/A2-M, two stable
offline acquisition replays, two stable open-world replays, runtime
integration, evidence-plumbing, candidate-variant, dissent, checkpoint, and
duplicate-action checks.

| Criterion | Evidence |
|---|---|
| 1–2 | `constraint_matrix` with eight layers and classifications; source/policy boundaries unchanged |
| 3 | `resolution_fixture`, public PDF acquisition fixture, metadata-only and blocked cases |
| 4 | `output_fixture`, shared planning ceiling, replay artifacts |
| 5–6 | acquisition, runtime, and plumbing replay; typed task/report and join diagnostics |
| 7 | `score_ledger` with request cause, acquisition, hypotheses, weakening, identity, blocked access, and overhead per arm/case |
| 8 | `acquisition_byte_stable`, `open_world_byte_stable`, runtime/plumbing replay, no external calls |
| 9 | this report and `replay.json` emit exactly `PRE_RERUN_CONSTRAINTS_READY` |

## Boundaries

This goal did not make model or network calls, add hosts, increase budgets,
retrieve subscription content, promote evidence, authorize a laboratory, or
authorize another paid Phase-B run. The next permitted action is a fresh
Phase-A freeze using the repaired contracts.
