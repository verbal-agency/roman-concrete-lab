# G11 — Complete expert review and issue the laboratory handoff

**Status:** proposed  
**Dependencies:** G09 complete; G10 only if its agent output is included  
**Advances:** converts the pre-lab package into an externally reviewable physical-validation proposal

## Objective

Submit the candidate experiment package to qualified materials-science and laboratory-safety reviewers, resolve or record every material finding, and issue either an approved lab handoff or a clearly blocked review package.

## In scope

- reviewer qualification/role record and conflict-of-interest statement;
- review checklist covering material identity, mix/process feasibility, controls, replication, randomization, specimen geometry, cracking, curing, measurements, equipment, analysis, handling, hazards, waste, and stop conditions;
- traceable comments and dispositions: accepted, revised, rejected, or unresolved;
- revised protocol/version and change impact on rankings/hypotheses;
- release status and explicit claim boundary;
- if G10 adopts any agent-society task: shared-memory permissions, hypothesis-tournament logs, focus-policy limits, model/provider identity, and human override boundaries;
- a machine-readable handoff manifest for later physical results.

## Excluded

Purchasing materials, scheduling or running experiments, certifying regulatory compliance, suppressing unresolved reviewer concerns, and treating approval as empirical validation.

## External dependency

At least one qualified cementitious-materials reviewer and one responsible laboratory safety reviewer must participate. One person may fill both roles only if qualifications and institutional responsibility are documented.

## Expected implementation surface

`docs/reviews/`, `docs/protocols/lab-handoff.md`, `schemas/lab-result.*`, `artifacts/releases/<version>/lab-handoff-manifest.*`, and validation tests for future result ingestion.

## Acceptance criteria

1. Every required review area has a named reviewer, disposition, date, and linked protocol version.
2. No unresolved high-severity scientific or safety finding is marked accepted.
3. Any protocol revision that changes the design space, estimand, or ranking triggers the documented upstream invalidation/rebuild path.
4. The final protocol contains exact materials/specifications or explicit substitution approval rules, controls, replicate rationale, randomization, batching, methods, timepoints, analysis, safety flags, and stop conditions.
5. The handoff manifest can accept future results without erasing deviations, failed specimens, censoring, or provenance.
6. The release emits exactly one status: `APPROVED_FOR_LAB_PLANNING`, `REVISION_REQUIRED`, or `BLOCKED_NO_REVIEWER`.
7. All materials remain labeled unvalidated until physical results are ingested and analyzed under a future charter.
8. Any adopted agent-society task has a documented read/write scope and cannot write empirical results, safety approvals, or protocol authorization.

## Verification evidence

`artifacts/goals/G11/report.md`, signed/attributed review records, comment-disposition matrix, final protocol hash, upstream invalidation audit, result-schema tests, and release status.

## Terminal condition

`APPROVED_FOR_LAB_PLANNING` authorizes planning with the responsible lab; it does not authorize Codex or any agent to conduct experiments or make procurement/safety decisions.
