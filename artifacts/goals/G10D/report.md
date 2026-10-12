# G10D viewpoint-centered society design report

## Outcome

`SOCIETY_DESIGN_READY`

The offline society now uses viewpoint-centered teams. Each viewpoint owns a falsifiable argument and receives assigned structural support tasks. Support agents can strengthen, weaken, or fail to discriminate for the viewpoint. Dossiers remain private until all active viewpoints commit; cross-viewpoint critics then compare typed dossiers, and deterministic focus preserves the null and a credible rival.

## Phase-A result

`artifacts/goals/G10D/phase-a.json` ran one development and one sealed fixture without model, network, subscription, credential, subprocess, external-communication, or laboratory calls.

| Check | Result |
|---|---|
| Lateral discovery | PASS |
| Contradiction/weakening dissent | PASS |
| Unresolved candidate retention | PASS |
| Null retention | PASS |
| Rival retention | PASS |
| Deterministic replay | PASS |
| Evidence promotion | prohibited |
| Viewpoint-count credit | zero |
| Consensus credit | zero |
| Rhetoric credit | zero |

The development case deliberately contains an unresolved source candidate; its envelope remains `REVIEW_REQUIRED`. The sealed case has complete fixture attribution and reaches `READY`. This demonstrates that uncertainty is preserved rather than treated as failure or silently promoted.

## Verification

- Focused viewpoint-society and Phase-A replay tests: `10 passed`.
- Full test suite: `120 passed`.
- `git diff --check`: passed.
- External calls: `false`.

## Boundary and next gate

This is an offline design gate, not evidence that a society outperforms a single investigator. It does not authorize a live rerun, source-policy expansion, evidence promotion, scientific approval, or laboratory work. G10R Phase B remains locked until this goal and G10P are complete and a new owner activation is recorded.
