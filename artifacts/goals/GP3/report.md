# GP3 cycle report — complete

**Date:** 2026-09-29
**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; GP4 is the next eligible goal

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. Facility can answer capability, safety, schedule, data, and ownership questions | **PASS** | `docs/partners/partner-readiness-package.md` and structured response schema |
| 2. Required versus optional capability distinction | **PASS** | `docs/partners/facility-capability-matrix.csv`: C01–C07/C09–C10 required; C08 optional |
| 3. Unknown cost/material/safety fields preserved | **PASS** | Packet and schema use `UNKNOWN`, `owner_decision_required`, `unassigned`, and explicit blockers; no estimates are generated |
| 4. Data-return contract preserves lineage and measurement metadata | **PASS** | `schemas/partner-result.schema.json` and packet data-return section |
| 5. Binary partner gate | **PASS** | `tools/partners/decision.py`; offline fixtures produce `FEASIBLE_FOR_REVIEW`, `REVISE`, and `NO_MATCH` |
| 6. Portfolio preserves exploratory versus validated status and utility assumptions | **PASS** | Packet portfolio disposition and GP2 context/ranking references |

## Verification

```text
python3 tools/partners/replay.py
python3 -m pytest -q
git diff --check
```

Result: replay produced one `FEASIBLE_FOR_REVIEW`, three `REVISE`, and one `NO_MATCH`; **16 tests passed**.

## Important boundary

This package is not outreach, vendor selection, a quote request, safety approval, or lab authorization. The feasible fixture only means the required questions appear answerable for review. GL1 must still obtain qualified facility and safety approval before any physical execution.

## Handoff to GP4

GP4 may validate that the context, evidence, candidate, hypothesis, utility, uncertainty, and partner-readiness contracts work across the Roman vertical slice and two offline cross-domain fixtures. It must not generalize Roman-concrete performance claims or initiate partner contact.
