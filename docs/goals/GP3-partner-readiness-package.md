# GP3 — Partner-readiness package

**Status:** proposed  
**Dependencies:** GP2 complete  
**Advances:** turns the pre-lab design into a facility-evaluable request without initiating external coordination

## Objective

Prepare a concise problem-specific experiment portfolio and partner packet that allows qualified materials facilities to decide whether they can safely execute, price, and return data for selected draft studies.

## In scope

- required capability matrix: mixing, casting, controlled damage, permeability/flow, strength, microscopy/chemistry;
- facility questions, review responsibilities, and acceptance checklist;
- data-return contract and file formats;
- sample custody, provenance, licensing, publication, and IP questions;
- unknown cost/equipment/material fields, never guessed values;
- partner selection criteria and a comparison template;
- draft outreach language for owner review only.
- portfolio view showing why each candidate/question is included, deferred, or rejected under the declared utility and evidence limits.

## Excluded

Sending messages, selecting a vendor, purchasing materials, negotiating terms, approving safety, or authorizing physical work.

## Acceptance criteria

1. A facility can answer capability, safety, schedule, data, and ownership questions from the packet without reconstructing the research premise.
2. The packet distinguishes required capabilities from optional characterization.
3. Every unknown cost, material, and safety item is explicitly marked unknown or owner/facility decision-required.
4. The data-return contract preserves specimen, batch, instrument, calibration, unit, uncertainty, and missingness metadata.
5. The packet contains a binary partner gate: `FEASIBLE_FOR_REVIEW`, `REVISE`, or `NO_MATCH`.
6. The portfolio distinguishes exploratory rankings from validated performance and preserves the problem-specific utility assumptions behind each selection.

## Expected implementation surface

`docs/partners/partner-readiness-package.md`, `docs/partners/facility-capability-matrix.csv`, `schemas/partner-result.schema.json`, `artifacts/goals/GP3/`.

## Authority boundaries

No outbound communication or external state change is authorized. Credentials and private contact information are excluded from repository artifacts.

## Verification evidence

Packet completeness checklist, schema validation, and `artifacts/goals/GP3/report.md`.

## Execution contract

### Expected implementation surface

- `docs/partners/partner-readiness-package.md` — owner-review-only packet carrying the GP2 context, ranking, draft conditions, and explicit boundary;
- `docs/partners/facility-capability-matrix.csv` — required versus optional capability rows;
- `schemas/partner-result.schema.json` — versioned facility capability/review response contract;
- `fixtures/partners/feasible.json`, `revise.json`, `no-match.json`, `unknown.json`, and `unsafe.json` — offline gate fixtures;
- `tests/partners/test_readiness.py` — packet, schema, gate, unknown-field, and authority tests;
- `artifacts/goals/GP3/run.json` and `artifacts/goals/GP3/report.md` — hashes, replay command, and criterion evidence.

Equivalent paths require a goal amendment before implementation.

### Canonical contract and invariants

Every capability row has `capability_id`, required/optional status, facility question, evidence/provenance requirement, owner, and response status. A facility response has `context_id/version`, reviewed condition IDs, capability statuses, safety/ownership/data questions, schedule/cost fields with explicit `UNKNOWN` semantics, and one gate result: `FEASIBLE_FOR_REVIEW`, `REVISE`, or `NO_MATCH`.

Illegal states include a guessed price or schedule, an unqualified safety approval, a missing data-return field, a private contact credential, a packet that omits the GP2 support region, or an outbound message represented as if sent. No response may promote a provisional ranking to validated performance.

### Deterministic behavior matrix

| Fixture/input | Required gate |
|---|---|
| Required capabilities present; safety, ownership, and data questions answerable | `FEASIBLE_FOR_REVIEW` |
| Required capability or data field unresolved but potentially reviewable | `REVISE` with named blocker |
| Primary endpoint unavailable or facility scope incompatible | `NO_MATCH` |
| Safety or ownership responsibility unassigned | `REVISE`; never approval |
| Cost, schedule, or material unknown | Preserve `UNKNOWN`; never estimate |
| Private credential or outbound-contact attempt | Reject as unauthorized |

### Authority, replay, and budget boundaries

GP3 reads only repository artifacts and offline fixtures. It may draft owner-review language but may not send email, contact a facility, choose a vendor, purchase materials, negotiate terms, approve safety, or authorize physical execution. The run records input hashes, a deterministic capability ordering, fixture outcomes, and a bounded local budget; replay is byte-equivalent and budget exhaustion stops with `BUDGET_EXHAUSTED`.

### Criterion-to-test map

`tests/partners/test_readiness.py` must cover packet completeness, required/optional capability distinction, unknown cost/material/safety preservation, specimen/batch/instrument/calibration/unit/uncertainty/missingness fields, all three gate outcomes, malformed/partial responses, credential rejection, no-outbound authority, deterministic replay, and budget exhaustion.

## Stop conditions

Stop if no qualified facility capability can plausibly cover the primary endpoint, or if the safety/ownership questions cannot be stated clearly enough for review.
