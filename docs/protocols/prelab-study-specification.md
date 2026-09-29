# DRAFT — EXPERT REVIEW REQUIRED

## GP2 Roman-concrete pre-lab study specification

**Status:** draft, non-authorizing
**Context:** `roman-concrete-v1`, version `1.0`
**Candidate dossier:** GP1 `gp1.1-candidate-dossier`
**Primary question:** does an evidenced quicklime/hot-mix intervention improve functional water-flow recovery after controlled cracking relative to a process-matched control in modern terrestrial Roman-inspired mortar or mortar-like concrete?

This document is a review package, not a laboratory protocol, recipe, safety approval, purchase request, or partner instruction. It contains no unreported formulation values and must not be used for physical execution without qualified materials and safety review.

## Decision target and support region

The package evaluates one bounded question in the G00 context:

- **Primary endpoint:** functional water-flow or permeability recovery after controlled cracking, with measurement semantics and units recorded at specimen level.
- **Secondary endpoint:** crack closure, explicitly non-equivalent to functional recovery.
- **Constraint:** compressive-strength retention; it is not freely traded against the primary endpoint.
- **Separate utility dimensions:** endpoint fit, information value, feasibility, and risk. No unvalidated composite score is used.
- **Support region:** modern terrestrial Roman-inspired lime-pozzolan mortar or explicitly marked mortar-like concrete with inspectable process identity and a reviewable comparator.

RC-01 is the only candidate currently inside the primary support region. RC-04 is deferred as an out-of-domain seawater transfer question. RC-05 is deferred until a functional transport endpoint and process-matched comparator are available. RC-02 and RC-03 remain context or endpoint-gap inputs.

## Included study-condition matrix

| Condition | Treatment envelope | Process-matched comparator | Primary observation | Reason for inclusion | Review state |
|---|---|---|---|---|---|
| `E-RC01-01` | Source-defined RC-01 quicklime/hot-mix candidate envelope; exact proportions and preparation details are `UNRESOLVED` | `C-RC01-01`: same declared material family and non-intervention control, with process matching to be specified by a qualified reviewer | Functional water-flow/permeability recovery after controlled cracking | Directly tests `H-RC01-01` and the G00 primary endpoint | `INCLUDED_FOR_REVIEW` |
| `E-RC01-02` | Same RC-01 candidate envelope | `C-RC01-02`: same material family without the declared hot-mix/quicklime intervention | Functional recovery compared with surface closure | Separates `H-RC01-02` from a surface-only explanation | `INCLUDED_FOR_REVIEW` |

Every included treatment condition has a process-matched comparator. The matrix does not authorize selecting quantities, heating conditions, mixing order, crack-generation settings, or exposure conditions. Those fields remain facility/scientist decisions.

### Deferred candidates (not study conditions)

`RC-05` remains an endpoint-gap follow-up: it has no included condition because a functional transport endpoint and process-matched comparator are unresolved. `RC-04` remains an out-of-domain transfer question: it has no included condition because its recorded seawater formulation and crack-closure-only endpoint do not satisfy the v1 support region. RC-02 and RC-03 are context inputs, not study conditions.

## Study-design fields to be completed by a qualified reviewer

The eventual facility specification must record these fields before any data collection:

1. **Damage definition:** the selected controlled-cracking or defined-damage standard, acceptance window, and pre-measurement verification. Numerical crack widths are intentionally not invented here.
2. **Exposure:** environment, containment, temperature/humidity or other relevant conditions, and start/stop timestamps. The facility must select and justify the method.
3. **Timepoints:** preregistered baseline and healing-observation timepoints, with no unplanned timepoint substitution.
4. **Grouping and lineage:** `batch_id`, `specimen_id`, condition, preparation lineage, damage event, instrument/run identifier, and operator/reviewer fields.
5. **Randomization:** assignment method and any blocking by batch or instrument; the package must preserve the assignment record.
6. **Replicates:** facility-proposed count and rationale based on the estimand, measurement variability, and available budget. No count is asserted by this draft.
7. **Controls:** process-matched comparator, baseline pre-damage measurement where feasible, and negative/zero-recovery handling.

## Required data contract

Every returned observation must use `schemas/prelab-result.schema.json` and include:

- context and condition identifiers;
- candidate, hypothesis, batch, and specimen lineage;
- endpoint name, value, unit, uncertainty, missingness, and censoring;
- exact source/protocol locator for the condition and instrument method;
- comparator status and provenance-completeness status;
- safety/review status;
- an outcome class and the deterministic result status.

`NOT_REPORTED`, `CENSORED`, and `UNRESOLVED` are not zero. Surface crack closure cannot populate the primary functional endpoint.

## Hypothesis-to-observation map

| Hypothesis | Required observation | Rival explanation preserved |
|---|---|---|
| `H-RC01-01` | Difference in functional transport recovery between `E-RC01-01` and `C-RC01-01` under matched damage/exposure/measurement | Difference is due to crack geometry, exposure, or measurement selection |
| `H-RC01-02` | Functional recovery and surface closure recorded as separate fields | Apparent closure does not imply through-depth recovery |
| `H-RC05-01` | Strength/occlusion can only inform a follow-up if a functional endpoint and comparator are added | Chemistry, thermal history, or sampling explains the observation |
| `H-RC04-01` | Crack closure may be recorded as transfer evidence only | Seawater-domain closure does not transfer to terrestrial functional recovery |

## Deterministic result decision table

| Required input state | Result status | Required treatment |
|---|---|---|
| Complete provenance, reviewed condition, matched comparator, and positive prespecified contrast | `SUPPORTED` | Preserve the measured result and exact uncertainty; does not validate a universal material claim |
| Complete provenance, reviewed condition, matched comparator, but null contrast | `NARROW_USE_CASE` or `INCONCLUSIVE` | The classifier must preserve the null; GP2 does not invent a practical-effect threshold |
| Contradictory measurements or rival predictions | `INCONCLUSIVE` | Preserve each observation and the contradiction reason |
| Missing/censored endpoint, comparator, unit, or provenance | `INCONCLUSIVE` or `REVIEW_REQUIRED` | Name the missing field; do not impute |
| Unsafe, unreviewed, or facility-unassessed condition | `REVIEW_REQUIRED` | No result status and no execution authorization |
| Complete negative result that fails to reproduce the candidate effect | `NOT_REPRODUCED` | Preserve the negative result and lineage |

## Analysis and ranking boundary

The ranking is conditional and qualitative. `RC-01` is the conditional `PROVISIONAL_BEST` for the declared primary endpoint because it has the closest endpoint and comparator evidence, not because effectiveness has been demonstrated. Feasibility, safety, and cost remain `UNKNOWN` or `REVIEW_REQUIRED` until a qualified facility evaluates them. RC-05 may be a high-information follow-up only after endpoint redesign; RC-04 abstains outside the support region; RC-02/RC-03 abstain from primary ranking.

Any later `PROVISIONAL_BEST` output must carry the context version, utility dimensions, support region, evidence coverage, uncertainty, tie-break rule, and abstention reason. It must never say “best concrete,” infer a recipe, or claim validated performance.

## Unknowns and required review

Materials availability, exact formulation, mixing/thermal conditions, equipment, safety controls, specimen geometry, exposure method, replicate count, cost, schedule, ownership, and measurement standard are all `UNKNOWN` or `REVIEW_REQUIRED`. A qualified materials scientist and facility safety reviewer must resolve them before GL1. This draft creates no external obligation and sends no communication.
