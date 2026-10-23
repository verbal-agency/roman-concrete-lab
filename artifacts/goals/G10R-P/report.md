# G10R-P society postmortem report

## Outcome

`TARGET_STATE_READY_FOR_OFFLINE_BUILD`

The postmortem can distinguish the completed run's negative signal from the
previous implementation mismatch. The current paid result exercised the
intended G10D `ViewpointSociety` and G10P `EvidenceBus` topology, preserved
open-slot work, and serialized typed society records. The theory therefore
remains testable; this run is not grounds to abandon viewpoint competition.

The strongest remaining finding is acquisition: all eight treatment/case runs
performed zero permitted document fetches and produced zero page-aware evidence
cards. A2-M consumed thirteen model calls per case versus A1's two, while its
discovery scores were lower on all four cases. The repaired scorer is not the
primary failure explanation: replay is deterministic, has no critical
failures, and preserves unresolved candidates and provisional hypotheses. The
trace also reveals a design confound: A2-M proponent/auditor instructions
require empty fetch arrays, extraction/identity and experiment tasks are
auto-abstained, and focus executes only search queries. The next question is
whether removing that suppression and making support obligations genuinely
information-seeking allows the society to acquire useful evidence before it
spends its budget on critique and adjudication.

## Acceptance-criterion map

| Criterion | Evidence | Result |
|---|---|---|
| 1. Reconstruct every case | `postmortem.json` case ledger; G10R run/checkpoints/replay | PASS: 8 arm/case rows with calls, tokens, queries, candidates, fetches, cards, scores, and costs. |
| 2. Typed loss ledger | `postmortem.json` loss ledger; `gap-matrix.md` | PASS: architecture, integration, acquisition, task/fixture, scorer, and plumbing causes are separated with evidence and confidence. |
| 3. State what actually ran | `postmortem.json.runtime_contract_audit` | PASS: current A2-M used ViewpointSociety and EvidenceBus; open-slot work was active; typed society records were serialized. |
| 4. Offline remediation evidence | G10D Phase-A replay, G10P replay, and `postmortem.json.remediation_evidence` | PASS: lateral discovery, contradiction, unresolved candidates, null/rival retention, no promotion, and no external calls are preserved offline. |
| 5. Measurable target state | `target-state.json` | PASS: topology, open-world, support joins, acquisition, budget, and replay thresholds are explicit. |
| 6. Falsifiable future comparison | `target-state.json.thresholds.future_escalation_rule` | PASS: requires case gain, noninferior total score, unique source-backed contribution, and zero critical failures; otherwise stop. |
| 7. No external execution | tool/tests and `external_calls: false` | PASS: no model, network, subscription, credential, laboratory, promotion, or external communication was used. |
| 8. One readiness outcome and next goal | this report | PASS: next goal is G10R-A offline evidence-acquisition and support-task redesign; no new paid run is authorized. |

## Target state

Before another paid evaluation, the implementation must retain the now-proven
G10D/G10P runtime topology and complete G10R-A: exercise fetch-positive and
metadata-only cases, require support tasks to attempt retrieval/extraction,
identity, contradiction, or an explicit bounded abstention, demonstrate at
least one attributable acquisition and one weakening/contradiction path in
offline fixtures, expose society overhead under equal budgets, and replay
without evidence promotion. No new paid run is authorized by this postmortem.
