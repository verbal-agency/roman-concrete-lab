# Society evidence-bus protocol

**Protocol version:** `g10p.1-society-evidence-plumbing`

This protocol defines the offline evidence handoff for viewpoint-centered societies. It does not authorize model calls, network retrieval, subscriptions, physical work, evidence promotion, or a larger budget.

## Join model

```text
viewpoint assignment -> support task -> action result -> source candidate
  -> viewpoint dossier -> cross-viewpoint critique -> portfolio envelope
  -> blinded score ledger
```

Every record is scoped to one case, problem version, treatment, and frozen context. The evidence bus is append-only: a duplicate ID with the same payload replays; a duplicate ID with a different payload fails; stale context, cross-problem writes, and unknown parent references fail closed.

## Required lineage

- A support task has `viewpoint_id`, `task_id`, and one structural `task_type`.
- A support report has `viewpoint_id`, `support_task_id`, action IDs, source-candidate IDs, claim IDs, and a `stance`: `SUPPORTS`, `WEAKENS`, or `NON_DISCRIMINATING`.
- A dossier is assembled only from reports for one viewpoint. It carries the union of task, action, source, and claim IDs and records unresolved joins instead of dropping them.
- A cross-viewpoint critique names the compared dossiers and any source candidates it used.
- A portfolio envelope carries viewpoint IDs, support-task IDs, dossier IDs, critique IDs, and the union of source candidates from both the dossier and final portfolio. If the final portfolio omits a dossier candidate, the envelope records `portfolio_omitted_source_candidate:<id>` and remains `REVIEW_REQUIRED`.

Unresolved or unattributed sources remain candidate knowledge. They receive no direct-evidence credit and cannot mutate immutable evidence, but they remain available for later collective adjudication.

## Deterministic behavior matrix

| Condition | Required result |
|---|---|
| Same record ID and same payload | return the recorded record with `replayed=true` |
| Same record ID and different payload | fail closed with a duplicate-payload error |
| Stale context hash or cross-problem record | fail closed; do not append |
| Support report references unknown task | fail closed |
| Support report stance is weakening | retain it as dissent; do not reject the viewpoint |
| Dossier references an unknown source/action | retain the raw ID and mark `PARTIAL` with a diagnostic |
| Final portfolio omits a dossier candidate | preserve the candidate in the envelope and mark `REVIEW_REQUIRED` |
| Historical trace lacks viewpoint/support IDs | mark `HISTORICAL_UNASSIGNED`; never invent a task assignment |
| Unresolved candidate reaches scoring | discovery may remain attributable; direct-evidence credit is zero |

## Authority and side effects

The bus reads and writes repository-local derived records only. It makes no provider, network, credential, subprocess, subscription, laboratory, or external-communication calls. It cannot promote evidence or authorize a protocol. Retrieved documents remain untrusted data.

## Artifacts

- Schemas: `schemas/viewpoint-support-task.schema.json`, `viewpoint-support-report.schema.json`, `viewpoint-dossier.schema.json`, `cross-viewpoint-critique.schema.json`, `society-portfolio-envelope.schema.json`, and `society-attribution-ledger.schema.json`.
- Implementation: `src/roman_concrete_lab/agents/evidence_bus.py`.
- Offline replay: `tools/evaluation/society_plumbing_replay.py`.
- Tests: `tests/agents/test_evidence_bus.py` and `tests/agents/test_society_plumbing_replay.py`.

## Research-loop bus extensions

`ResearchNeed`, `CandidateSelection`, `ViewpointDossierRevision`, and
`OpenViewpointAdmission` make the search-to-adjudication joins explicit. A
metadata candidate is retained as pending, but cannot receive direct-evidence
credit. Semantic duplicate wording reuses the first action and records
provenance. Every accepted late report or critique must enter a newer dossier
revision before scoring; a completed checkpoint replays without a new debit or
membership mutation.
