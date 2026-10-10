# GP1 cycle report — complete

**Date:** 2026-10-09
**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; replayed against the completed G-LR landscape gate; candidate and hypothesis content unchanged
**G-LR gate:** `LANDSCAPE_INCOMPLETE` (run `ee1b9bca61df457d`, evidence-map hash recorded in `run.json`)

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. Stable candidate records with evidence and blockers | **PASS** | `docs/reports/material-candidate-dossier.md`; source candidate ledger; replay validates five unique IDs, supporting records, and exact locators |
| 2. Rival hypotheses with interventions, comparators, outcomes, domains, and rival predictions | **PASS** | `data/processed/candidate-hypotheses.jsonl`; six machine-readable hypotheses |
| 3. No promotion to validated material | **PASS** | all candidate adjudication states remain `pending`; dossier preserves `PROVISIONAL`, `CONTEXT_ONLY`, or `REVIEW_REQUIRED` boundaries |
| 4. Deterministic replay reconstructs counts and statuses | **PASS** | `tools/literature_audit/gp1_replay.py --write`; `artifacts/goals/GP1/run.json`; replay reconciles 24 study families and 10 supporting records, then matches five candidates, six hypotheses, three provisional plausible candidates, and seedable IDs `RC-01`, `RC-04`, `RC-05` |
| 5. Claim labels and conditional-ranking limits | **PASS** | dossier distinguishes `REPORTED`, `DERIVED`, `PROPOSED`, and `UNRESOLVED`; no `PROVISIONAL_BEST` was emitted |
| 6. G-LR verdict and manifest binding | **PASS** | `artifacts/goals/GP1/run.json` records the G-LR verdict, run ID, evidence-map SHA-256, permitted outputs, and prohibited outputs; discovery-grade authorization is `false` |

## Verification

```text
python3 tools/literature_audit/gp1_replay.py --write
python3 -m pytest -q
git diff --check
```

Result: replay matched the updated source and G-LR manifests and **35 tests passed**.

The G-1 access rerun changed lawful-copy classifications and provenance, but did not change candidate IDs, candidate statuses, hypothesis count, seedability, or the primary-support-region decision. Newly accessible transfer papers remain outside the RC-01 primary candidate ledger unless a later evidence-enrichment amendment explicitly promotes them into the hypothesis layer.

## Important limitations

- `RC-01` is the only candidate currently aligned with the primary functional water-transport question, but its Utah selected-specimen endpoint and S25/S26 lineage remain pending adjudication.
- `RC-04` is a transfer/context candidate because the ledger records seawater and crack closure rather than the v1 terrestrial functional endpoint.
- `RC-02` and `RC-03` remain contextual or endpoint-gap inputs; they are not primary candidates.
- No candidate is a validated material, recipe, effectiveness result, or lab authorization.
- Because G-LR is `LANDSCAPE_INCOMPLETE`, the dossier is restricted to provisional candidate, evidence-gap, and hypothesis-seed outputs. It cannot serve as a discovery-grade hypothesis basis.

## Handoff to GP2

GP2 may construct a conditional candidate/experiment ranking and draft study specification. It must resolve or explicitly carry forward comparator and endpoint gaps, keep RC-04 outside the primary support region unless the context is amended, and emit `ABSTAIN` when utility, support, or functional endpoint requirements are unmet. Physical execution, partner contact, and safety approval remain prohibited.
