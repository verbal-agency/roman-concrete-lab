# GL1 — Lab-partner and safety gate

**Status:** proposed / externally blocked until a qualified facility responds  
**Dependencies:** GP4 complete; owner supplies or authorizes a qualified facility review
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

## Stop conditions

No qualified reviewer, incomplete safety review, unclear ownership, or inability to measure the primary endpoint results in `BLOCKED`.
