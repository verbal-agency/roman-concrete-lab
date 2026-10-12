# G10P society evidence-bus and attribution plumbing report

## Outcome

`SOCIETY_PLUMBING_READY`

The offline evidence bus now preserves viewpoint, support-task, action, source-candidate, dossier, critique, portfolio, and score-attribution joins. Missing or unresolved joins remain visible as diagnostics; they are not silently dropped and they are not promoted to evidence.

## Replay result

`artifacts/goals/G10P/replay.json` replayed all eight completed G10R treatment/case traces without model, network, subscription, credential, or laboratory calls.

| Measure | Result |
|---|---:|
| Treatment/case traces | 8 |
| Checkpoint source candidates | 118 |
| Candidates omitted from historical final portfolios but preserved by the candidate ledger | 105 |
| Historical support-task links reconstructed | 0 |
| Silent-drop detection | PASS |

The historical run predates viewpoint and support-task IDs. The replay therefore preserves those records as `HISTORICAL_UNASSIGNED` rather than inventing assignments. The new contract is tested separately with typed viewpoint/support fixtures, including support that weakens its assigned viewpoint.

## Verification

- Focused evidence-bus, replay, remediation, active-investigation, and mechanism-tournament tests: `41 passed`.
- Full test suite: `110 passed`.
- `git diff --check`: passed.
- External calls: `false`.

## Criterion status

All seven G10P acceptance criteria pass. The implementation does not authorize a live rerun, change source policy, promote evidence, or grant scientific or laboratory authority. G10D must redesign the viewpoint-team agent behavior before G10R Phase B can run again.
