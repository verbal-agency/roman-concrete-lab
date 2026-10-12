# G10R-P society postmortem report

## Outcome

`TARGET_STATE_READY_FOR_OFFLINE_BUILD`

The postmortem can distinguish the completed run's negative signal from an
implementation mismatch. The paid result is valid for the executed A2-M
implementation, but it is not a clean test of the intended G10D topology: the
runner still uses the legacy mechanism-tournament path, excludes open-slot
proponents, and emits no G10P viewpoint/support-task records in checkpoints.

The strongest acquisition finding is also concrete: all eight treatment/case
runs performed zero permitted document fetches and produced zero page-aware
evidence cards. A2-M consumed thirteen model calls per case and substantially
more input tokens than A1 while producing lower discovery scores on three of
four cases. The repaired scorer is not the primary failure explanation: replay
is deterministic, has no critical failures, and preserves unresolved candidates
and provisional hypotheses.

## Acceptance-criterion map

| Criterion | Evidence | Result |
|---|---|---|
| 1. Reconstruct every case | `postmortem.json` case ledger; G10R run/checkpoints/replay | PASS: 8 arm/case rows with calls, tokens, queries, candidates, fetches, cards, scores, and costs. |
| 2. Typed loss ledger | `postmortem.json` loss ledger; `gap-matrix.md` | PASS: architecture, integration, acquisition, task/fixture, scorer, and plumbing causes are separated with evidence and confidence. |
| 3. State what actually ran | `postmortem.json.runtime_contract_audit` | PASS: legacy mechanism tournament detected; G10D/G10P runtime absent; open slot filtered; typed support records absent. |
| 4. Offline remediation evidence | G10D Phase-A replay, G10P replay, and `postmortem.json.remediation_evidence` | PASS: lateral discovery, contradiction, unresolved candidates, null/rival retention, no promotion, and no external calls are preserved offline. |
| 5. Measurable target state | `target-state.json` | PASS: topology, open-world, support joins, acquisition, budget, and replay thresholds are explicit. |
| 6. Falsifiable future comparison | `target-state.json.thresholds.future_escalation_rule` | PASS: requires case gain, noninferior total score, unique source-backed contribution, and zero critical failures; otherwise stop. |
| 7. No external execution | tool/tests and `external_calls: false` | PASS: no model, network, subscription, credential, laboratory, promotion, or external communication was used. |
| 8. One readiness outcome and next goal | this report | PASS: next goal is offline G10D/G10P runtime integration and remediation verification. |

## Target state

Before another paid evaluation, the implementation must use the versioned G10D
`ViewpointSociety` and G10P evidence bus in the live-capable runner; exercise
null, rival, and open-slot paths; assign retrieval, extraction/identity,
contradiction, and experiment-design tasks; preserve 100% of support-task joins;
demonstrate fetch and page-card behavior on positive fixtures; expose overhead
under equal budgets; and replay byte-stably without evidence promotion.

The next implementation goal should wire and offline-test that runtime path. No
new paid run is authorized by this postmortem.
