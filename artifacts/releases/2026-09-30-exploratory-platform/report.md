# Exploratory platform release 2026-09-30-exploratory-platform

**Release mode:** `EXPLORATORY_PLATFORM`
**Source branch:** GP4 → G07E
**Authority:** offline, non-agent, non-lab; no physical performance claim

## What is released

This bundle contains the versioned problem cards, scoped-memory summaries, typed hypothesis/tournament replay, focus and promotion policy, claim ledger, rights summary, security scan, software bill of materials, and reproducibility manifest. It contains no restricted full text, credentials, live service dependency, lab instructions, or agent runtime.

## Tournament outcomes

| Fixture | Status |
|---|---|
| budget-exhaustion | `BUDGET_EXHAUSTED` |
| contradictory | `REVIEW_REQUIRED` |
| malformed | `REVIEW_REQUIRED` |
| no-feasible | `NO_FEASIBLE_CANDIDATE` |
| partial | `REVIEW_REQUIRED` |
| positive | `PARETO_SET` |
| unsafe | `UNSAFE_REJECTED` |
| unsupported | `ABSTAIN` |

The normal card outputs are conditional `PARETO_SET` results. They preserve endpoint semantics, uncertainty, support regions, and expert-review boundaries; they do not identify a universal best material or validate physical performance.

## Reproduction

```text
PYTHONPATH=src python3 -m roman_concrete_lab.release.build --version 2026-09-30-exploratory-platform --output artifacts/releases/2026-09-30-exploratory-platform
python3 tools/tournament/replay.py
python3 -m pytest -q
```

The manifest hashes every release artifact except the manifest itself. A clean reproduction must regenerate byte-equivalent artifact contents and pass the claim, rights, security, schema, and replay checks.
