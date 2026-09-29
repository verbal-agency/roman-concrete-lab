# GP4 — Cross-question portfolio validation

**Status:** proposed  
**Dependencies:** GP3 complete; G00 `EXPLORATORY_PLATFORM` or `PRELAB_REPLICATION` track  
**Advances:** tests whether the problem-specific discovery substrate can represent more than one scientific question without making unsupported cross-domain claims

## Objective

Validate the reusable question, evidence, candidate, hypothesis, utility, and uncertainty contracts across the Roman-concrete vertical slice and at least two recorded offline problem-card fixtures from distinct materials/process domains.

## In scope

- canonical problem-card, scoped-memory, hypothesis-registry, and portfolio fields: question, endpoint, constraints, utility, candidate references, evidence locators, support region, uncertainty, and abstention status;
- one Roman-concrete card plus two offline cross-domain fixtures;
- deterministic candidate/hypothesis/experiment portfolio serialization and replay;
- conditional `PROVISIONAL_BEST` or Pareto outputs within each problem;
- explicit refusal to compare unrelated problem domains without a declared common utility and evidence basis;
- routing of missing, contradictory, unsupported, and out-of-domain cards to abstention or review.

## Excluded

New physical experiments, unsupported literature claims for fixture domains, cross-domain performance ranking, general-purpose agent frameworks, predictive model training, and external communications.

## Acceptance criteria

1. Every card validates against a versioned schema with the required problem, endpoint, utility, provenance, scoped-memory, support, uncertainty, and authority fields.
2. The Roman card and two offline fixtures round-trip deterministically without losing candidate lineage, claim type, or missingness.
3. Each card can emit a conditional `PROVISIONAL_BEST`, Pareto set, or explicit abstention; no card emits a universal “best material” claim.
4. Cross-domain comparisons are rejected unless a common utility, endpoint mapping, and evidence basis are explicitly recorded.
5. Positive, contradictory, incomplete, unsupported, and out-of-domain fixtures produce the prescribed portfolio status and review reason.
6. The report demonstrates that the reusable substrate is problem-configurable while domain-specific scientific assumptions remain explicit; hypothesis memory is separated from evidence memory; no agent or physical-lab authority is introduced.

## Expected implementation surface

`schemas/problem-card.schema.json`, `schemas/portfolio-entry.schema.json`, `fixtures/portfolio/`, `tests/portfolio/`, `docs/protocols/problem-specific-discovery.md`, and `artifacts/goals/GP4/`.

## Authority boundaries

Offline fixtures and repository artifacts only. No lab execution, external messages, unapproved literature retrieval, model calls, or agent framework is authorized.

## Verification evidence

Schema validation, deterministic replay, portfolio behavior matrix, cross-domain rejection tests, and `artifacts/goals/GP4/report.md`.

## Stop conditions

Stop if the contracts require silently treating domain-specific endpoints, utilities, or safety rules as interchangeable, or if a provisional ranking cannot expose its support and uncertainty boundaries.
