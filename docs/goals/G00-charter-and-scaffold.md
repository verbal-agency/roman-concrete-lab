# G00 — Ratify the verdict-specific charter and authorized scaffold

**Status:** proposed  
**Dependencies:** G-1 with a complete paired decision; `AUDIT_INCOMPLETE` does not satisfy this dependency
**Advances:** a falsifiable program with explicit authority, scope, and stop conditions

## Objective

Convert the G-1 literature-sufficiency verdict and the compatible defaults in `docs/research_program_v2.md` into an approved, versioned decision record. Create only the minimal project surface authorized by that verdict.

## Entry gate and track behavior

Read the G-1 decision, report, frozen manifest, and criterion evidence. Record one track in the charter:

- `MODELABLE_NOW`: ratify the bounded synthesis/modeling program and create the minimal Python project skeleton described below.
- `EVIDENCE_SYNTHESIS_ONLY`: ratify a synthesis-first program and create only minimal corpus, provenance, and reporting tooling. Predictive modeling, candidate ranking, and agent development remain unauthorized.
- `REPLICATION_STUDY_REQUIRED`: ratify a replication-first program, define the owner/expert decisions needed to design the controlled study, and amend the roadmap with a dedicated study-design goal. Do not create the general software scaffold or begin G01–G10.
- `LAB_CANDIDATE_PLAUSIBLE` plus `REPLICATION_STUDY_REQUIRED`: ratify the pre-lab replication track, authorize GP1–GP3 only, and preserve GL1 as the external facility/safety gate. Do not authorize physical execution or GD1.

G00 may tighten the G-1 conclusion. It may not promote the program to a less conservative track without a versioned literature amendment that re-runs and passes G-1's frozen decision rules.

## Required owner decisions

Record the selected G-1 track and explicit answers for program purpose, v1 material domain, primary/secondary outcomes, scientist-of-record status, acceptable data rights, acceptance of NO-GO, initial budgets, commercial-use intent, allowed network/LLM providers, and—only when the selected track reaches extraction—the quality thresholds that G03 must enforce. Recommended defaults are in `docs/premise_review.md`; recommended extraction defaults are at least 0.95 exact value/unit accuracy on critical numeric fields, at least 0.99 provenance-locator accuracy, and zero unsupported measured observations on the gold set.

If any choice changes the scientific domain, estimand, rights policy, or physical-safety responsibility, update the program and roadmap before scaffolding. Do not silently adopt a different direction.

## In scope

- `docs/decisions/0001-program-charter.md` with dated decisions, rationale, owner, and amendment rule;
- the G-1 verdict and evidence references, selected track, and list of goals made eligible or blocked;
- for `MODELABLE_NOW`, a Python package/test skeleton, lockfile, formatter/linter/test configuration;
- for `EVIDENCE_SYNTHESIS_ONLY`, only the minimal corpus/provenance/reporting skeleton required by the amended charter;
- for `REPLICATION_STUDY_REQUIRED`, a roadmap amendment and study-design decision surface, with no general software scaffold;
- for `LAB_CANDIDATE_PLAUSIBLE`, a roadmap amendment and pre-lab handoff decision surface, with no physical-lab or model scaffold;
- top-level `README.md` explaining the scientific boundary and stage gates;
- `LICENSE` decision or an explicit `LICENSE-PENDING.md` blocker;
- `.gitignore` rules for credentials, restricted raw documents, caches, and generated artifacts;
- for any track that introduces executable tooling, a tiny CLI that reports package version and active charter version;
- a CI-compatible local verification command appropriate to the selected track.

## Excluded

Literature retrieval, scientific schemas, databases, LLM calls, modeling, UI, PostgreSQL, vector/graph storage, LangGraph, BoTorch, and lab protocols.

## Expected implementation surface

All tracks require `README.md`, `.gitignore`, and `docs/decisions/0001-program-charter.md`. The `MODELABLE_NOW` track also expects `pyproject.toml`, lockfile, `src/roman_concrete_lab/__init__.py`, `src/roman_concrete_lab/cli.py`, and `tests/test_cli.py`. The other tracks must record their smaller or amended surface in the goal report.

Equivalent paths are allowed only if recorded in the goal report.

## Acceptance criteria

1. The decision record cites the completed G-1 artifacts, records exactly one compatible track, answers every applicable owner decision, and identifies unresolved items as blockers, not defaults.
2. The decision record defines v1 inclusions/exclusions, the primary estimand or replication question, NO-GO semantics, eligible/blocked goals, and the rule for charter/evidence amendments.
3. On `MODELABLE_NOW`, `python -m roman_concrete_lab --version` (or recorded equivalent) exits zero and prints package plus charter versions. On another track, the report demonstrates that this criterion is not applicable and verifies that no unauthorized scaffold was created.
4. Any introduced test suite and static checks run from a clean checkout using the locked environment; a documentation-only replication track instead passes link, schema, and decision-record checks.
5. Secret-like files, restricted raw documents, and generated outputs are ignored without hiding manifests, fixtures, schemas, or goal reports.
6. No nonessential framework or service dependency is introduced, and no component belonging to a blocked track exists.

## Verification evidence

- `artifacts/goals/G00/report.md` mapping criteria 1–6 to files/commands and showing consistency with the G-1 verdict;
- output from applicable link/schema checks and, when code exists, lockfile validation, tests, and static checks;
- when dependencies exist, a list showing why each runtime dependency is required.

## Stop conditions

Block if G-1 is absent, incomplete, or internally inconsistent; if the requested track contradicts its verdict without a passing amendment; or if the owner does not decide the research domain, acceptable data rights, commercial intent, or whether NO-GO is acceptable. Those choices materially change every later goal.
