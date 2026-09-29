# GP2 cycle report — complete

**Date:** 2026-09-28
**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; GP3 is the next eligible goal

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. One primary functional endpoint; closure remains secondary | **PASS** | `docs/protocols/prelab-study-specification.md` names functional water-flow/permeability recovery as primary and crack closure as non-equivalent secondary |
| 2. Every included treatment has a process-matched comparator and rationale | **PASS** | Candidate/comparator matrix defines `E-RC01-01`/`C-RC01-01` and `E-RC01-02`/`C-RC01-02`; RC-04/RC-05 are explicitly abstained or deferred where comparators/endpoints are unresolved |
| 3. Rival hypotheses map to observations | **PASS** | Hypothesis-to-observation map covers RC-01, RC-04, and RC-05 with preserved rival explanations |
| 4. Specimen, batch, units, uncertainty, and provenance fields defined | **PASS** | `schemas/prelab-result.schema.json` and the required data contract |
| 5. Expert-review watermark and no execution instruction | **PASS** | Study specification is watermarked `DRAFT — EXPERT REVIEW REQUIRED`; exact formulations, hazards, and execution settings remain unresolved/review-only |
| 6. Deterministic outcome decision table | **PASS** | Study specification, `tools/prelab/decision.py`, five offline fixtures, and replay manifest |
| 7. Conditional ranking with abstention | **PASS** | `data/processed/gp2-conditional-ranking.json` makes RC-01 conditional `PROVISIONAL_BEST`, abstains RC-04/RC-02/RC-03, and carries uncertainty/support limits |

## Verification

```text
python3 tools/prelab/replay.py
python3 -m pytest -q
git diff --check
```

Result: offline replay matched the manifest and **12 tests passed**.

## Decision and limitations

RC-01 is the conditional leading experiment because it best matches the declared functional endpoint and has a recorded comparator path. This is not evidence that RC-01 works. The ranking has no composite numeric utility score; feasibility, cost, safety, and exact formulation remain `UNKNOWN` or `REVIEW_REQUIRED`.

RC-04 is abstained outside the v1 support region; RC-05 is deferred pending a functional endpoint; RC-02 and RC-03 are endpoint/comparator-gap inputs. No recipe, safety approval, partner contact, purchase, or physical execution is authorized.

## Handoff to GP3

GP3 may package this draft portfolio for facility evaluation, capability questions, data return, ownership, and review responsibilities. It may not send outreach, select a facility, negotiate terms, or authorize physical work.
