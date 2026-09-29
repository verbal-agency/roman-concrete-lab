# GP1 cycle report — complete

**Date:** 2026-09-28
**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; GP2 is the next eligible goal

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. Stable candidate records with evidence and blockers | **PASS** | `docs/reports/material-candidate-dossier.md`; source candidate ledger; replay validates five unique IDs, supporting records, and exact locators |
| 2. Rival hypotheses with interventions, comparators, outcomes, domains, and rival predictions | **PASS** | `data/processed/candidate-hypotheses.jsonl`; six machine-readable hypotheses |
| 3. No promotion to validated material | **PASS** | all candidate adjudication states remain `pending`; dossier preserves `PROVISIONAL`, `CONTEXT_ONLY`, or `REVIEW_REQUIRED` boundaries |
| 4. Deterministic replay reconstructs counts and statuses | **PASS** | `tools/literature_audit/gp1_replay.py`; `artifacts/goals/GP1/run.json`; replay reconciles 24 study families and 10 supporting records, then matches five candidates, six hypotheses, three provisional plausible candidates, and seedable IDs `RC-01`, `RC-04`, `RC-05` |
| 5. Claim labels and conditional-ranking limits | **PASS** | dossier distinguishes `REPORTED`, `DERIVED`, `PROPOSED`, and `UNRESOLVED`; no `PROVISIONAL_BEST` was emitted |

## Verification

```text
python3 tools/literature_audit/gp1_replay.py
python3 -m pytest -q
git diff --check
```

Result: replay matched the manifest and **9 tests passed**.

## Important limitations

- `RC-01` is the only candidate currently aligned with the primary functional water-transport question, but its Utah selected-specimen endpoint and S25/S26 lineage remain pending adjudication.
- `RC-04` is a transfer/context candidate because the ledger records seawater and crack closure rather than the v1 terrestrial functional endpoint.
- `RC-02` and `RC-03` remain contextual or endpoint-gap inputs; they are not primary candidates.
- No candidate is a validated material, recipe, effectiveness result, or lab authorization.

## Handoff to GP2

GP2 may construct a conditional candidate/experiment ranking and draft study specification. It must resolve or explicitly carry forward comparator and endpoint gaps, keep RC-04 outside the primary support region unless the context is amended, and emit `ABSTAIN` when utility, support, or functional endpoint requirements are unmet. Physical execution, partner contact, and safety approval remain prohibited.
