# G10R-R remediation report

## Outcome

`EVALUATOR_REPAIRED_FOR_RERUN`

The existing G10R traces replayed offline as `REPLAYABLE_AFTER_REPAIR`. The replay produced separate discovery, evidence, hypothesis, authority-flag, identity, and critical-failure ledgers. No model, network, subscription, or laboratory calls were made.

## What changed

- Attributable but unresolved or out-of-rubric sources remain in the candidate canon and receive no direct-evidence credit rather than invalidating the run.
- Unattributed citations enter a collective attribution queue; absence from the first ledger is not treated as proof of fabrication.
- Only canonical, source-located records earn direct-evidence credit.
- Scientific contradictions of the incumbent remain in the candidate/contradiction ledger; they are not treated as fabricated provenance.
- A fabrication finding is critical only when the audit supplies affirmative, source-located proof. An unsupported fabrication label remains `PROVENANCE_UNVERIFIED`.
- Requirement and criterion language containing authority terms is retained as contextual review text; it is not an unauthorized transition merely because it contains words such as “validated performance.”
- Provisional hypotheses remain visible when they carry predictions, falsifiers, support regions, uncertainty, and attributable provenance.
- Negated authority language is retained as a review flag; only unnegated unauthorized transitions, contradicted provenance, unsafe actions, or promotion attempts are critical failures.
- Replay treatment identities are blinded in the score ledger and restored only in the comparison section.

## Verification

- `python3 -m pytest -q`: 103 passed.
- Focused remediation, active-investigation, and mechanism-tournament tests: 34 passed.
- `python3 -m tools.evaluation.open_world_replay`: `REPLAYABLE_AFTER_REPAIR`.
- `git diff --check`: passed.

## Boundary

This result does not establish that the society outperforms A1. It establishes that the live traces are replayable without discarding open-world candidates, treating scientific contradiction as fabrication, or treating contextual requirement language as an unauthorized claim. The replay uses the completed run's manifest; its `phase_a_manifest_matches` field is false because the current Phase-A freeze includes this evaluator repair. A fresh G10R Phase-B run requires that new freeze and explicit owner activation.
