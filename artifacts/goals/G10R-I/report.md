# G10R-I offline society runtime integration report

## Outcome

`RUNTIME_INTEGRATION_READY`

The A2-M runner now executes through the G10D `ViewpointSociety` and G10P
`EvidenceBus` contracts. The verification was entirely offline: zero model,
network, subscription, credential, or laboratory calls.

This is a wiring result, not a society-efficacy result. It does not authorize a
paid rerun or promote evidence.

## Evidence

| Check | Result |
|---|---|
| Runner topology | PASS: ViewpointSociety and EvidenceBus are on the A2-M path; legacy-only import is absent |
| Actual runner smoke | PASS: deterministic provider-shaped replay completed; 13 traces, 9 actions |
| Society checkpoint | PASS: 4 viewpoints, 20 typed support tasks, 43 support reports, 4 dossiers, 3 critiques, focus, and portfolio persisted |
| Open slot | PASS: reserved slot admitted as a bounded candidate and received abstained support work |
| Evidence-bus joins | PASS: zero dossier join diagnostics in the runtime smoke |
| Positive PDF fixture | PASS: page-aware evidence card validated against page hash and locator |
| Rights-negative fixture | PASS: metadata-only fetch was blocked with no payload retained |
| Replay | PASS: deterministic smoke replay was byte-equivalent on recorded fields |
| Authority/budget boundary | PASS: authority remains REVIEW_REQUIRED; no evidence promotion or lab authority; existing limits unchanged |
| G10D development/sealed fixtures | PASS: support tasks, reports, dossiers, critiques, dissent, null/rival retention, and no promotion |

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. G10D/G10P runtime path | PASS | `replay.json.runner_audit` |
| 2. Typed offline traces | PASS | `replay.json.runtime_smoke` |
| 3. Open-slot admission/work | PASS | `runtime_smoke.open_slot_admitted` and 4 viewpoints |
| 4. Evidence-bus joins | PASS | zero runtime dossier diagnostics |
| 5. Fetch/evidence-card behavior | PASS | `replay.json.document_fixture` |
| 6. Deterministic replay | PASS | `runtime_smoke.replay_stable` plus fixture replay tests |
| 7. Budget/authority equality | PASS | frozen G10R limits and authority-safe portfolio |
| 8. Handoff | PASS: exact `RUNTIME_INTEGRATION_READY` emitted | `replay.json.status` |

## Handoff

The next paid evaluation, if desired, still requires a fresh Phase-A manifest,
reachable sealed-case checks, and explicit owner activation of the lawful source
policy, model, and spend cap. The historical G10R `DO_NOT_ESCALATE_ACTIVE_SOCIETY`
decision remains authoritative until a later evaluation is separately run and
scored.
