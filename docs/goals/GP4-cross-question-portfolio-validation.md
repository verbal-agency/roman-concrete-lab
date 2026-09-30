# GP4 — Cross-question portfolio validation

**Status:** complete
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

## Execution contract

### Expected implementation surface

- `schemas/problem-card.schema.json` — versioned problem, endpoint, utility, authority, support, and scoped-memory contract;
- `schemas/portfolio-entry.schema.json` — candidate/hypothesis/experiment portfolio contract;
- `fixtures/portfolio/roman.json`, `lime-mortar.json`, and `battery-cathode.json` — one Roman card and two offline distinct-domain cards;
- `fixtures/portfolio/positive.json`, `contradictory.json`, `incomplete.json`, `unsupported.json`, and `out-of-domain.json` — behavior fixtures;
- `tests/portfolio/test_validation.py` — schema, replay, lineage, missingness, and cross-domain rejection tests;
- `docs/protocols/problem-specific-discovery.md` — non-agent contract and scope boundary;
- `tools/portfolio/replay.py` — deterministic serialization/replay;
- `artifacts/goals/GP4/run.json` and `artifacts/goals/GP4/report.md` — hashes, outputs, and criterion evidence.

Equivalent paths require an amendment before implementation.

### Canonical contract and invariants

Each problem card has `problem_id/version`, question, domain/process boundary, primary and secondary endpoints, candidate variables, controls, constraints, utility dimensions, support region, allowed outputs, authority, and scoped-memory policy. Each portfolio entry has candidate/hypothesis references, claim type, evidence locators, endpoint mapping, utility, support region, uncertainty, abstention reason, and status (`INCLUDED`, `DEFERRED`, `REJECTED`, `REVIEW_REQUIRED`, or `ABSTAIN`).

Evidence memory is immutable and source-located; hypothesis memory is typed derived/proposed content; reflection or episodic notes are untrusted. No cross-domain performance score is legal without explicit endpoint mapping, common utility, and evidence basis. A missing or contradictory field is preserved, not defaulted.

### Deterministic behavior matrix

| Fixture/input | Required output |
|---|---|
| Complete in-domain card and evidence | Conditional `PROVISIONAL_BEST` or `PARETO_SET` with uncertainty and support region |
| No defensible single utility | `PARETO_SET`; no forced winner |
| Missing endpoint, utility, provenance, or authority | `ABSTAIN` or `REVIEW_REQUIRED` with named reason |
| Contradictory evidence | Preserve claims and emit review/uncertainty status |
| Unsupported or out-of-domain card | `ABSTAIN`; never rank as performance evidence |
| Cross-domain comparison without common utility/endpoint mapping | Reject comparison with explicit reason |
| Request for agent, lab, or external communication | Reject as unauthorized |

### Authority, replay, and budget boundaries

GP4 uses repository artifacts and recorded offline fixtures only. No network, model call, external message, partner contact, physical execution, or agent runtime is permitted. Replay must preserve candidate lineage, claim type, missingness, and scoped-memory tier byte-for-byte; duplicate replay must be equivalent. A fixed local budget is recorded, and exhaustion returns `BUDGET_EXHAUSTED` without widening the fixture set.

### Criterion-to-test map

`tests/portfolio/test_validation.py` must cover schema validation, Roman and two cross-domain round trips, positive/contradictory/incomplete/unsupported/out-of-domain outcomes, evidence-versus-hypothesis memory separation, conditional ranking, Pareto output, cross-domain rejection, unauthorized-action rejection, deterministic replay, duplicate replay, and budget exhaustion.

## Stop conditions

Stop if the contracts require silently treating domain-specific endpoints, utilities, or safety rules as interchangeable, or if a provisional ranking cannot expose its support and uncertainty boundaries.
