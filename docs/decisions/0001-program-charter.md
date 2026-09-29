# Program charter 0001 — exploratory Roman-concrete platform

**Status:** approved for the exploratory plane
**Drafted:** 2026-09-28
**Amendment rule:** amend this record, `docs/research_program_v2.md`, and `docs/roadmap.md` together whenever a decision changes the scientific domain, estimand, rights policy, safety responsibility, or goal eligibility.

## Evidence basis

This charter is grounded in the G-1 decision and its linked artifacts:

- `artifacts/goals/G-1/decision.json` (protocol `g1.2-material-candidate`)
- `data/manifests/literature-sufficiency-sources.jsonl`
- `data/manifests/literature-sufficiency-screening.csv`
- `data/processed/literature-sufficiency-study-families.jsonl`
- `data/processed/literature-sufficiency-material-candidates.jsonl`
- `docs/premise_review.md`

G-1 is `AUDIT_INCOMPLETE` overall and `REPLICATION_STUDY_REQUIRED` for modelability, but records `exploration_seedability=EXPLORATION_SEEDABLE` for RC-01, RC-04, and RC-05. That permits only the bounded exploratory branch; it does not authorize a recipe, effectiveness claim, predictive model, physical execution, or agent framework.

## Selected track and purpose

**Track:** `EXPLORATORY_PLATFORM` (the G-1 `EXPLORATION_SEEDABLE` path).

**Primary purpose:** discover and compare falsifiable, problem-specific Roman-inspired concrete questions and candidate material directions using provenance-preserving evidence, while preserving an auditable path to qualified physical testing.

**Secondary purpose:** exercise a reusable evidence-to-question substrate. Reuse is through versioned problem context and contracts, not generic claims or a problem-independent model.

**Program authority:** the repository owner is the product/scope decision owner for this exploratory plane. No scientific, safety, or physical-execution authority is delegated by G00.

## Version-1 problem context (ratified from the existing program direction)

- **Domain:** modern, terrestrial, Roman-inspired hot-mixed lime-pozzolan mortar.
- **Problem-specific question:** which evidenced hot-mixing, quicklime, or lime-clast process candidates merit a controlled experiment to distinguish functional crack-healing hypotheses?
- **Excluded domain:** archaeological performance labels, marine concrete, and unrelated self-healing systems are not interchangeable v1 observations.
- **Primary outcome:** functional water-flow/permeability recovery after controlled cracking.
- **Secondary outcome:** crack closure.
- **Constraint:** compressive-strength retention is a safety/performance constraint, not a freely traded objective.
- **Exploratory utility:** keep expected functional recovery, information value, feasibility, and risk as separate dimensions; do not collapse them into an unvalidated universal score.
- **Allowed exploratory outputs:** `PROVISIONAL_BEST`, `HYPOTHESIS`, and `EXPERIMENT_CANDIDATE`, each with evidence and uncertainty.
- **Forbidden outputs:** validated performance claims, inferred recipes, generalizable predictive models, and lab instructions.

## Decisions recorded from the current program

| Decision | Current record | Authority / evidence |
|---|---|---|
| G-1 track | Exploration-only | G-1 decision `exploration_seedability` |
| Problem context | Roman-inspired terrestrial mortar; scoped outcomes above | `docs/premise_review.md`; roadmap GP1–GP4 |
| No-GO semantics | A well-supported evidence or exploration stop is a valid result; no later gate may silently promote it | `docs/premise_review.md`; `docs/roadmap.md` |
| Physical/lab boundary | No physical execution before GL1; no effectiveness claim before qualified feedback | G-1 decision and roadmap stop rules |
| Agent boundary | No agent framework in G00 or GP1–GP4; deterministic contracts precede any G10 society test | roadmap; G07/G09/G10 |
| Data-rights baseline | Use only lawfully available, reviewable material; do not use Sci-Hub or bypass access controls | **Approved for current plane** |

## G00 decisions and deferred gates

| Decision area | G00 disposition | Decision state |
|---|---|---|
| Scientist of record / qualified reviewer | Not required for G00 or GP1–GP4 because they authorize no physical work. A qualified materials reviewer is mandatory before GL1 or any lab handoff. | **Deferred to GL1/G11** |
| Commercial-use intent and repository license | Not needed for the offline exploratory plane; source-derived redistribution and public/commercial release remain prohibited until reviewed. | **Deferred to GP3/G09 release decision** |
| Acceptable data-rights policy | Only lawful, reviewable sources; no Sci-Hub, access-control bypass, or unauthorized restricted-text storage. | **Approved for current plane** |
| Initial budget | G00 and GP1–GP4 authorize documentation/local computation only and no external spend. Each goal must declare a bounded time/compute budget before execution. | **Approved boundary; per-goal budgets deferred** |
| Exploration NO-GO | A supported exploration stop is a valid result and does not imply a material failure or terminate future evidence work. | **Approved** |
| Focus and promotion authority | No promotion authority exists in G00. GP2 may emit only conditional rankings; G07 must define focus/promotion policy; qualified human adjudication is required before GL1. | **Approved boundary; policy deferred to G07** |
| Network and model providers | No model calls or external network are required by G00. Later retrieval must be read-only and lawful; LLM/provider choice is deferred to G10. | **Approved boundary; providers deferred** |
| Extraction thresholds | Not applicable to the documentation-only exploratory plane. | **Deferred to G03 if that branch becomes eligible** |

## Eligibility after G00

G00 authorizes GP1–GP4 only. No source acquisition beyond the lawful, read-only scope already permitted by G-1, no extraction branch, model training, lab protocol, physical execution, or framework installation is authorized by this charter. GL1, GL2, GD1, G01–G10 remain gated by their own dependencies.

## Amendment and promotion rules

An owner-approved amendment must identify the changed field, rationale, evidence, affected goals, and new verification artifact. Human adjudication and a qualified facility review remain mandatory before any material candidate reaches lab consideration. Exploratory evidence can narrow questions and propose experiments; it cannot promote itself to a recipe, validated result, or safety approval.
