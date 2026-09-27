# G-1 criterion-to-evidence report

**Outcome:** blocked — `AUDIT_INCOMPLETE`; provisional finding `REPLICATION_STUDY_REQUIRED`  
**Primary report:** `docs/reports/literature-sufficiency-audit.md`  
**Decision:** `artifacts/goals/G-1/decision.json`

| Criterion | Evidence | Result |
|---|---|---|
| 1. Frozen protocol | `docs/protocols/literature-sufficiency-search.md`, amended protocol `g1.1-public-expansion`, dated before expanded screening artifacts | pass |
| 2. Complete source/screening ledger | `data/manifests/literature-sufficiency-sources.jsonl` (34 records), `data/manifests/literature-sufficiency-screening.csv` (34 rows) | pass |
| 3. Independent screening/adjudication | Screening ledger records agent screening passes, but qualified human adjudication is still `pending-human-adjudication` for the provisional Tier A record | blocked |
| 4. Family/arm/endpoint/replication counts | `data/processed/literature-sufficiency-study-families.jsonl`, report deterministic-count table | pass |
| 5. Offline failure fixtures | `fixtures/literature_audit/cases.jsonl` covers positive, negative, duplicate, contradictory, malformed, partial, budget, and unsupported cases | pass |
| 6. Deterministic replay/verdict | `tools/literature_audit/decision.py`; `tests/literature_audit/test_decision.py`; replay supports `AUDIT_INCOMPLETE` until all direct families are adjudicated and shows the provisional 2-family/3-arm result | pass |
| 7. Direct/transfer/contextual synthesis | `docs/reports/literature-sufficiency-audit.md` sections “What the direct/adjacent split found” and “Why this is a replication problem” | pass |
| 8. Saturation within budget | 34 records and 24 full-text/preview assessments; two expanded focused search/citation waves added no new Tier A family after the Utah lineage | pass, with provider-rate-limit and subscription-access limitations recorded |
| 9. Inspectable handoff | this report and `decision.json` preserve the provisional finding, but no downstream goal is eligible until the human-adjudication blocker is resolved | blocked |

## Verification commands

```text
python3 -m unittest discover -s tests/literature_audit -v
python3 tools/literature_audit/decision.py data/processed/literature-sufficiency-study-families.jsonl --audit-complete --saturated
```

The tests passed on 2026-09-27. The deterministic decision function flags missing human adjudication as `AUDIT_INCOMPLETE`; a separate replay with an adjudicated Tier A ledger emits the provisional `REPLICATION_STUDY_REQUIRED` result.

## Routed findings

- **G00:** blocked until a qualified human adjudicates the provisional Tier A record and signs the final verdict.
- **Owner action:** provide or perform qualified adjudication for S01 and confirm the final G-1 verdict.
- **Backlog:** none; the remaining issues are required inputs to G-1 completion or the next replication-first goal, not optional backlog work.
