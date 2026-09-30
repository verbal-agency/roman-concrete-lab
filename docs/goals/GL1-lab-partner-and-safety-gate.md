# GL1 — Lab-partner and safety gate

**Status:** proposed / `DEFERRED_NOT_REQUESTED` until owner activation
**Dependencies:** GP4 complete; owner explicitly authorizes facility coordination or supplies an attributable qualified facility review
**Advances:** separates pre-lab planning from physical execution authority

## Objective

Obtain a qualified facility's feasibility, safety, scope, and data-return review before any physical material work begins.

## In scope

- facility capability review against GP3;
- materials and process hazard review by the facility;
- approved scope, roles, custody, data rights, and reporting terms;
- revised study specification or explicit rejection;
- documented authorization boundary for physical work.

## Excluded

The agent performing physical work, independently approving hazards, or converting a draft package into an executable lab procedure.

## Acceptance criteria

1. A qualified facility and responsible reviewer are identified.
2. The facility accepts, revises, or rejects the primary endpoint and controls in writing.
3. Safety, waste, equipment, training, and emergency responsibilities are assigned by the facility.
4. Data ownership, raw-data return, provenance, and publication terms are recorded.
5. Physical execution is authorized only if all required facility approvals are present; otherwise the gate is `BLOCKED`.

## Verification evidence

Signed or otherwise attributable facility review, revised protocol, responsibility matrix, and `artifacts/goals/GL1/report.md`.

## Execution contract

### Expected implementation surface

- `docs/partners/facility-review-response.md` — attributable review record or an explicit blocked-input record;
- `schemas/gl1-review.schema.json` — facility, safety, ownership, endpoint, and authorization contract;
- `fixtures/gl1/no-review.json`, `partial-review.json`, `revised-review.json`, and `approved-review.json` — offline state fixtures only;
- `tests/gl1/test_gate.py` — schema, status-transition, authority, and missing-approval tests;
- `artifacts/goals/GL1/run.json` and `artifacts/goals/GL1/report.md` — input provenance and gate evidence.

Equivalent paths require an amendment before implementation. A facility response must be supplied by the owner or obtained through separately authorized coordination; this goal does not discover or contact facilities automatically. GP4 completion does not activate GL1.

### Canonical contract and state transitions

The review record must include an attributable facility/reviewer role, reviewed GP3 condition IDs, primary endpoint decision, comparator decision, capability review, safety/waste/equipment/training/emergency responsibilities, custody, ownership, raw-data return, provenance, publication terms, and authorization scope. Legal gate states are `DEFERRED_NOT_REQUESTED`, `PENDING_INPUT`, `BLOCKED`, `REVISE`, `REJECTED`, and `APPROVED_FOR_EXECUTION`.

`DEFERRED_NOT_REQUESTED -> PENDING_INPUT` only after explicit owner activation or a supplied facility review. `PENDING_INPUT -> BLOCKED` when an activated gate has no attributable review; `PENDING_INPUT -> REVISE` when a review identifies resolvable gaps; `PENDING_INPUT -> REJECTED` when the facility cannot cover the endpoint; `PENDING_INPUT -> APPROVED_FOR_EXECUTION` only when every required safety, ownership, capability, and scope approval is present. No agent or repository artifact may create the final approval state.

### Deterministic behavior matrix

| Input condition | Required gate |
|---|---|
| No owner activation or facility response | `DEFERRED_NOT_REQUESTED` |
| Owner activates GL1 but no facility response exists | `BLOCKED` |
| Attributable response missing endpoint, comparator, or capability decision | `BLOCKED` or `REVISE` with named blocker |
| Safety, waste, training, or emergency responsibility unassigned | `BLOCKED` |
| Ownership, raw-data return, or publication terms unresolved | `BLOCKED` |
| Facility cannot measure the primary endpoint | `REJECTED` |
| All required approvals present and scope explicitly bounded | `APPROVED_FOR_EXECUTION` |

### Authority and side-effect boundary

GL1 may read the GP3 packet and a user-supplied facility review. It may not browse for facilities, send messages, choose vendors, negotiate terms, purchase materials, approve hazards independently, or authorize physical work from a fixture. Network access, credentials, and external coordination require separate owner authorization. `APPROVED_FOR_EXECUTION` is a qualified facility decision, not an agent decision.

### Criterion-to-test map

`tests/gl1/test_gate.py` must cover no-review blocking, partial/revised/rejected/approved transitions, endpoint and comparator decisions, safety responsibility completeness, ownership/data/publication terms, attributable reviewer identity, unauthorized outbound/contact rejection, deterministic replay, and duplicate-call behavior.

## Stop conditions

No owner activation results in `DEFERRED_NOT_REQUESTED`. After activation, no qualified reviewer, incomplete safety review, unclear ownership, or inability to measure the primary endpoint results in `BLOCKED`, `REVISE`, or `REJECTED` as specified above.
