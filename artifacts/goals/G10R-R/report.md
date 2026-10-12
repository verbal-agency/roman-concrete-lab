# G10R-R remediation report

## Outcome

`EVALUATOR_REPAIRED_FOR_RERUN`

The existing G10R traces replayed offline as `REPLAYABLE_AFTER_REPAIR`. The replay produced separate discovery, evidence, hypothesis, authority-flag, identity, and critical-failure ledgers. No model, network, subscription, or laboratory calls were made.

## What changed

- Attributable but unresolved or out-of-rubric sources remain in the candidate canon and receive no direct-evidence credit rather than invalidating the run.
- Unattributed citations enter a collective attribution queue; absence from the first ledger is not treated as proof of fabrication.
- Only canonical, source-located records earn direct-evidence credit.
- Provisional hypotheses remain visible when they carry predictions, falsifiers, support regions, uncertainty, and attributable provenance.
- Negated authority language is retained as a review flag; only unnegated unauthorized transitions, contradicted provenance, unsafe actions, or promotion attempts are critical failures.
- Replay treatment identities are blinded in the score ledger and restored only in the comparison section.

## Verification

- `python3 -m pytest -q`: 100 passed.
- Focused remediation and active-investigation tests: 30 passed.
- `python3 -m tools.evaluation.open_world_replay`: `REPLAYABLE_AFTER_REPAIR`.
- `git diff --check`: passed.

## Boundary

This result does not establish that the society outperforms A1. It establishes that the prior live traces are now evaluable without discarding open-world candidates or treating negated safety language as an unauthorized claim. A fresh G10R Phase-B run requires a new Phase-A freeze under the amended evaluator and explicit owner activation.
