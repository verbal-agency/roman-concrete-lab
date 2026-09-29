# G00 — Ratify the verdict-specific charter and authorized scaffold

**Status:** complete
**Dependencies:** G-1 with either a complete substantive paired decision or `exploration_seedability=EXPLORATION_SEEDABLE` for the exploration-only track
**Advances:** a falsifiable program with explicit authority, scope, and stop conditions

## Objective

Convert the G-1 literature-sufficiency verdict and the compatible defaults in `docs/research_program_v2.md` into an approved, versioned decision record. Create only the minimal project surface authorized by that verdict.

## Entry gate and track behavior

Read the G-1 decision, report, frozen manifest, and criterion evidence. Record one track in the charter:

- `MODELABLE_NOW`: ratify the bounded synthesis/modeling program and create the minimal Python project skeleton described below.
- `EVIDENCE_SYNTHESIS_ONLY`: ratify a synthesis-first program and create only minimal corpus, provenance, and reporting tooling. Predictive modeling, candidate ranking, and agent development remain unauthorized.
- `REPLICATION_STUDY_REQUIRED`: ratify a replication-first program, define the owner/expert decisions needed to design the controlled study, and amend the roadmap with a dedicated study-design goal. Do not create the general software scaffold or begin G01–G10.
- `LAB_CANDIDATE_PLAUSIBLE` plus `REPLICATION_STUDY_REQUIRED`: ratify the pre-lab replication track, authorize GP1–GP4 only, and preserve GL1 as the external facility/safety gate. Do not authorize physical execution or GD1.
- `EXPLORATION_SEEDABLE` (including while the overall G-1 state remains `AUDIT_INCOMPLETE`): ratify the reusable evidence-to-question substrate instantiated with a declared problem context, authorize GP1–GP4 to generate provisional candidates, hypotheses, experiment questions, and a cross-question portfolio checkpoint, and prohibit physical execution, effectiveness claims, predictive-model training, and agent-framework construction.

G00 may tighten the G-1 conclusion. It may not promote exploratory outputs to a validated material, predictive model, or physical protocol without the applicable adjudication, modelability, and GL1 gates. The product substrate may be reusable across problems, but every execution must load a versioned problem context; generic abstractions do not replace domain-specific scientific assumptions, endpoints, utilities, or safety rules.

## Required owner decisions

Record the selected G-1 track and explicit answers for program purpose, the problem-specific question, v1 material/domain boundary, primary/secondary outcomes, utility and constraints for any provisional ranking, authority status, acceptable data rights, acceptance of NO-GO, and the budget and provider boundary for the current exploratory plane. Defer commercial licensing to the release gate, extraction thresholds to G03, and LLM/provider policy to G10; do not make those later-stage decisions a prerequisite for documentation-only G00 work.

If any choice changes the scientific domain, estimand, rights policy, or physical-safety responsibility, update the program and roadmap before scaffolding. Do not silently adopt a different direction.

## In scope

- `docs/decisions/0001-program-charter.md` with dated decisions, rationale, owner, and amendment rule;
- the G-1 verdict and evidence references, selected track, and list of goals made eligible or blocked;
- for `MODELABLE_NOW`, a Python package/test skeleton, lockfile, formatter/linter/test configuration;
- for `EVIDENCE_SYNTHESIS_ONLY`, only the minimal corpus/provenance/reporting skeleton required by the amended charter;
- for `REPLICATION_STUDY_REQUIRED`, a roadmap amendment and study-design decision surface, with no general software scaffold;
- for `LAB_CANDIDATE_PLAUSIBLE`, a roadmap amendment and pre-lab handoff decision surface, with no physical-lab or model scaffold;
- for `EXPLORATION_SEEDABLE`, a problem specification, candidate/hypothesis surface, provisional-ranking contract, cross-question portfolio checkpoint, and portfolio/feedback boundary, with no physical-lab, predictive-model, or agent scaffold;
- top-level `README.md` explaining the scientific boundary and stage gates;
- `LICENSE` decision or an explicit `LICENSE-PENDING.md` blocker;
- `.gitignore` rules for credentials, restricted raw documents, caches, and generated artifacts;
- for any track that introduces executable tooling, a tiny CLI that reports package version and active charter version;
- a CI-compatible local verification command appropriate to the selected track.

## Excluded

Literature retrieval, scientific schemas, databases, LLM calls, modeling, UI, PostgreSQL, vector/graph storage, LangGraph, BoTorch, and lab protocols.

## Expected implementation surface

All tracks require `README.md`, `.gitignore`, and `docs/decisions/0001-program-charter.md`. The exploratory track also records the versioned problem-context, memory-authority, and hypothesis-tournament contracts without introducing an agent runtime. The `MODELABLE_NOW` track also expects `pyproject.toml`, lockfile, `src/roman_concrete_lab/__init__.py`, `src/roman_concrete_lab/cli.py`, and `tests/test_cli.py`. The other tracks must record their smaller or amended surface in the goal report.

Equivalent paths are allowed only if recorded in the goal report.

## Acceptance criteria

1. The decision record cites the G-1 artifacts, records exactly one compatible track, answers every applicable owner decision, and identifies unresolved items as blockers, not defaults. An exploration track may cite a provisional G-1 state only when `exploration_seedability=EXPLORATION_SEEDABLE` is recorded.
2. The decision record defines v1 inclusions/exclusions, the primary estimand or replication question, NO-GO semantics, eligible/blocked goals, and the rule for charter/evidence amendments.
3. On `MODELABLE_NOW`, `python -m roman_concrete_lab --version` (or recorded equivalent) exits zero and prints package plus charter versions. On an exploration or other non-model track, the report demonstrates that this criterion is not applicable and verifies that no unauthorized predictive, lab, or agent scaffold was created.
4. Any introduced test suite and static checks run from a clean checkout using the locked environment; a documentation-only replication track instead passes link, schema, and decision-record checks.
5. Secret-like files, restricted raw documents, and generated outputs are ignored without hiding manifests, fixtures, schemas, or goal reports.
6. No nonessential framework or service dependency is introduced, and no component belonging to a blocked track exists.

## Verification evidence

- `artifacts/goals/G00/report.md` mapping criteria 1–6 to files/commands and showing consistency with the G-1 verdict;
- output from applicable link/schema checks and, when code exists, lockfile validation, tests, and static checks;
- when dependencies exist, a list showing why each runtime dependency is required.

## Stop conditions

Block the substantive model, synthesis, or physical tracks if G-1 is absent, incomplete, or internally inconsistent. The exploration-only track may proceed from a provisional G-1 state only when the seedability gate is explicit and its no-lab/no-model boundaries are preserved. Also block if the requested track contradicts its verdict without a passing amendment, or if the owner has not decided the problem context, current-plane data rights, or whether an exploration NO-GO is acceptable. Commercial licensing, extraction thresholds, LLM providers, and facility/scientist-of-record approval are later-gate decisions and must not be implied by G00.
