# G-1 criterion-to-evidence report

**Outcome:** public-access audit complete; final model/lab gate remains `AUDIT_INCOMPLETE` pending qualified human adjudication; provisional exploration gate `EXPLORATION_SEEDABLE`; provisional modelability finding `REPLICATION_STUDY_REQUIRED`; provisional material-candidate finding `LAB_CANDIDATE_PLAUSIBLE`
**Primary report:** `docs/reports/literature-sufficiency-audit.md`  
**Decision:** `artifacts/goals/G-1/decision.json`

| Criterion | Evidence | Result |
|---|---|---|
| 1. Frozen protocol | `docs/protocols/literature-sufficiency-search.md`, protocol `g1.3-public-access-audit`, frozen 2026-10-09 before rerun artifacts | pass |
| 2. Complete source/screening ledger | `data/manifests/literature-sufficiency-sources.jsonl` (38 records), `data/manifests/literature-sufficiency-screening.csv` (38 rows) | pass |
| 3. Independent screening/adjudication | Screening ledger records agent screening passes, but qualified human adjudication is still `pending-human-adjudication` for the provisional Tier A records | blocked |
| 4. Family/arm/endpoint/replication counts | `data/processed/literature-sufficiency-study-families.jsonl`, report deterministic-count table | pass |
| 5. Offline failure fixtures | `fixtures/literature_audit/cases.jsonl` covers positive, negative, duplicate, contradictory, malformed, partial, budget, and unsupported cases | pass |
| 6. Deterministic replay/verdict | `tools/literature_audit/decision.py`; `tests/literature_audit/test_decision.py`; replay emits `EXPLORATION_SEEDABLE` separately while preserving `AUDIT_INCOMPLETE` until all direct families are adjudicated and shows the provisional 2-family/3-arm result | pass |
| 7. Direct/transfer/contextual synthesis | `docs/reports/literature-sufficiency-audit.md` sections “What the direct/adjacent split found” and “Why this is a replication problem” | pass |
| 8. Saturation within budget | 38 records and 27 full-text/preview assessments; follow-up waves added no new Tier A family after the Utah lineage | pass, with provider-coverage and rate-limit limitations recorded |
| 9. Inspectable handoff | this report and `decision.json` preserve the provisional findings; G00 `EXPLORATORY_PLATFORM` may authorize GP1–GP4 with no lab/model authority, while substantive PRELAB, GL1/GL2, and GD1 remain gated | pass for exploratory handoff; substantive handoff blocked |
| 10. Material-candidate and seedability audit | `data/processed/literature-sufficiency-material-candidates.jsonl` names five candidates; RC-01, RC-04, and RC-05 are provisionally plausible and deterministically seed exploration, while RC-02/RC-03 lack a qualifying functional or comparator record | pass provisionally; human adjudication remains required before lab consideration |
| 11. Public-copy exhaustion | `data/manifests/literature-sufficiency-access-register.csv` covers all 38 records; 34 have lawful public/local copies and four are `not_located_publicly`; no `publisher_metadata` status remains | pass |
| 12. Subscription-value assessment | Access register names missing content, barriers, decision relevance, and priority; S22 is the only `buy_or_borrow` candidate and broad subscription is deferred | pass |
| 13. Evidence/access distinction | `docs/reports/literature-sufficiency-audit.md` separates absent evidence, inaccessible records, public-but-unextracted evidence, and provider gaps | pass |

## Verification commands

```text
python3 -m unittest discover -s tests/literature_audit -v
python3 tools/literature_audit/decision.py data/processed/literature-sufficiency-study-families.jsonl --candidate-ledger data/processed/literature-sufficiency-material-candidates.jsonl --audit-complete --saturated
python3 -m pytest -q
```

The deterministic decision function was rerun on 2026-10-09 with `audit_complete=true` and `saturated=true`. It still flags missing human adjudication as `AUDIT_INCOMPLETE`, emits the separate provisional `EXPLORATION_SEEDABLE` gate, and returns the provisional `REPLICATION_STUDY_REQUIRED` result. The full test suite passed (`29 passed`).

## Routed findings

- **G00 exploratory track:** eligible for problem-specific GP1–GP4 only, with explicit provisional/no-lab/no-model boundaries.
- **G00 substantive tracks:** blocked until a qualified human adjudicates the provisional Tier A records and signs the final verdict.
- **Owner action:** provide or perform qualified adjudication for S01/S25 and confirm the final G-1 verdict before physical or predictive work. If desired, obtain targeted access to S22; a broad subscription is not recommended by this rerun.
- **Backlog:** none; the remaining issues are required inputs to G-1 completion or the next replication-first goal, not optional backlog work.
