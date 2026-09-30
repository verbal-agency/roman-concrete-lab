# GP4 cycle report — complete

**Date:** 2026-09-29
**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; exploratory pre-lab branch is now validated across three problem cards

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. Versioned cards contain required problem, endpoint, utility, provenance, memory, support, uncertainty, and authority fields | **PASS** | `schemas/problem-card.schema.json`; Roman, lime-mortar, and battery-cathode cards |
| 2. Cards round-trip without losing lineage, claim type, or missingness | **PASS** | `schemas/portfolio-entry.schema.json`; replay and portfolio fixtures preserve candidate IDs, memory tiers, claim types, and missingness fields |
| 3. Conditional best/Pareto/abstention outputs | **PASS** | replay emits Roman `PROVISIONAL_BEST`, lime-mortar `PARETO_SET`, and battery-cathode `ABSTAIN` |
| 4. Cross-domain comparison rejection | **PASS** | out-of-domain fixture returns `REJECT_COMPARISON` without common utility, endpoint mapping, or evidence basis |
| 5. Positive, contradictory, incomplete, unsupported, and out-of-domain behavior | **PASS** | five portfolio fixtures return prescribed statuses and reasons |
| 6. Reusable substrate with explicit domain assumptions and separated memory authority | **PASS** | `docs/protocols/problem-specific-discovery.md`; no network, model, agent, lab, or external authority introduced |

## Verification

```text
python3 tools/portfolio/replay.py
python3 -m pytest -q
git diff --check
```

Result: three cards and five behavior fixtures replayed successfully; **20 tests passed**.

## What this validates

The reusable part is the contract surface: context, provenance, candidate lineage, hypotheses, utilities, uncertainty, abstention, and scoped memory. The scientific assumptions remain card-specific. Roman water-flow recovery, lime-mortar sorptivity recovery, and battery capacity retention are not treated as one endpoint or one universal objective.

## Handoff and limits

GP4 does not create new scientific evidence, compare material performance across domains, contact partners, run a lab, train a model, or introduce agents. The exploratory pre-lab branch has now produced a reusable non-agent substrate suitable for later review. GL1 remains required before any physical handoff, but its current state is `DEFERRED_NOT_REQUESTED`; GP4 completion does not authorize facility coordination.
