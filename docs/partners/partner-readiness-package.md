# OWNER REVIEW DRAFT — NO OUTBOUND CONTACT

## GP3 facility-readiness package

**Status:** owner-review-only, non-authorizing
**Context:** `roman-concrete-v1`, version `1.0`
**Source:** GP2 `gp2.1-conditional-ranking` and expert-review draft
**Primary candidate:** `RC-01`, conditions `E-RC01-01` and `E-RC01-02`

This packet is designed so a qualified materials facility can evaluate capability, safety responsibility, data return, ownership, schedule, and cost questions without reconstructing the research premise. It is not an outreach message, purchase request, vendor selection, safety approval, or physical execution authorization.

## Research premise the reviewer must see

The bounded question is whether an evidenced quicklime/hot-mix intervention improves functional water-flow/permeability recovery after controlled cracking relative to a process-matched control in modern terrestrial Roman-inspired mortar or mortar-like concrete.

- Primary endpoint: functional water-flow/permeability recovery.
- Secondary endpoint: crack closure, never a substitute for functional recovery.
- Constraint: compressive-strength retention.
- Utility dimensions: endpoint fit, information value, feasibility, and risk kept separate.
- Support region: modern terrestrial Roman-inspired lime-pozzolan mortar or explicitly marked mortar-like concrete with inspectable process identity and a reviewable comparator.
- Status of RC-01: conditional `PROVISIONAL_BEST`, not validated effectiveness.

The facility must review the GP2 draft specification before proposing any execution details. Exact formulation, quantities, thermal/mixing conditions, damage settings, exposure, specimen geometry, replicate count, equipment, cost, and safety controls remain unresolved.

## Portfolio disposition

| Candidate/question | Packet status | Why |
|---|---|---|
| `RC-01` / `E-RC01-01`, `E-RC01-02` | `INCLUDED_FOR_REVIEW` | Closest match to the primary functional endpoint and process-matched comparator path |
| `RC-05` | `DEFERRED_ENDPOINT_GAP` | No functional transport endpoint or reviewable process-matched comparator |
| `RC-04` | `ABSTAIN_OUT_OF_DOMAIN` | Seawater formulation and crack-closure-only endpoint fall outside v1 support |
| `RC-02` | `CONTEXT_ONLY` | Comparator and functional endpoint unclear |
| `RC-03` | `CONTEXT_ONLY` | No comparable controlled functional recovery test |

No portfolio status is a performance claim. A facility may return `FEASIBLE_FOR_REVIEW`, `REVISE`, or `NO_MATCH`; none is safety approval or authorization to proceed.

## Facility capability questions

For every row in `docs/partners/facility-capability-matrix.csv`, the reviewer should return:

1. `available`, `unavailable`, or `unknown`;
2. the facility's capability description or an exact internal method/provenance locator;
3. responsible role (not a private contact detail);
4. constraints, qualification requirements, and review questions;
5. whether the capability is required for the primary endpoint or optional characterization.

Required capabilities cover controlled preparation/casting, controlled damage, functional water-flow/permeability measurement, exposure control, strength retention, specimen/batch lineage, and calibrated measurement metadata. Microscopy/chemistry is optional characterization unless a qualified reviewer promotes it to a required discriminator.

## Safety, ownership, and data-return questions

These are questions for facility review, not assumptions:

- Who owns safety review for the proposed materials, thermal process, damage method, and equipment?
- What hazards, controls, training, waste handling, and stop conditions must be documented before any work?
- Who owns specimens, derived measurements, raw instrument files, images, and analysis outputs?
- What source-derived restrictions apply to the GP1/GP2 evidence and any resulting publication?
- Can the facility return specimen-level records with `context_id`, condition, batch, specimen, instrument/run, calibration, endpoint, unit, uncertainty, missingness, censoring, and provenance locator?
- Can it preserve negative, null, contradictory, incomplete, and unsafe outcomes without imputing values?
- What schedule and cost ranges are possible? Unknown values must remain `UNKNOWN`; this repository supplies no estimates.

The required response contract is `schemas/partner-result.schema.json`. It excludes private names, email addresses, phone numbers, credentials, and unapproved contact data.

## Data-return contract

Each returned data package must preserve:

- context and condition versions;
- candidate and hypothesis IDs;
- batch/specimen lineage and damage event;
- instrument/run and calibration identifiers;
- endpoint, value, unit, uncertainty, missingness, and censoring;
- comparator and provenance status;
- safety/review status and responsible role;
- raw-file or method locator where redistribution is permitted;
- a facility-review decision, never a silently inferred result.

`NOT_REPORTED`, `CENSORED`, `UNRESOLVED`, and `UNKNOWN` are valid states, not zeros or guessed values.

## Gate semantics

| Gate | Meaning | What it does not mean |
|---|---|---|
| `FEASIBLE_FOR_REVIEW` | Required capabilities appear available and safety, ownership, data, and review questions are answerable | Not safety approval, vendor selection, price acceptance, or execution authorization |
| `REVISE` | A potentially resolvable capability, data, ownership, safety, cost, or schedule blocker is named | Not a rejection and not permission to proceed |
| `NO_MATCH` | The primary endpoint or a required capability is unavailable or incompatible | Not a claim that the material fails scientifically |

## Owner-review draft language

> Please review the attached GP2 draft and capability matrix as a technical feasibility question only. We are not requesting a quote, purchase, protocol approval, or execution. Please identify which required capabilities are available, which questions require revision, what safety and ownership review would be required, and whether the data-return contract is feasible. Unknown cost, schedule, and materials fields should remain unknown.

This text is not to be sent by this goal. GP3 authorizes no outbound communication.

## Stop and handoff boundary

If no qualified facility capability can plausibly cover the primary functional endpoint, the packet returns `NO_MATCH` and the roadmap stops or revises. If the packet is reviewable, GL1 must still obtain qualified facility and safety approval before physical execution. GP3 never promotes the conditional RC-01 ranking to validated material performance.
