# GP3 — Partner-readiness package

**Status:** proposed  
**Dependencies:** GP2 complete  
**Advances:** turns the pre-lab design into a facility-evaluable request without initiating external coordination

## Objective

Prepare a concise partner packet that allows qualified materials facilities to decide whether they can safely execute, price, and return data for the draft study.

## In scope

- required capability matrix: mixing, casting, controlled damage, permeability/flow, strength, microscopy/chemistry;
- facility questions, review responsibilities, and acceptance checklist;
- data-return contract and file formats;
- sample custody, provenance, licensing, publication, and IP questions;
- unknown cost/equipment/material fields, never guessed values;
- partner selection criteria and a comparison template;
- draft outreach language for owner review only.

## Excluded

Sending messages, selecting a vendor, purchasing materials, negotiating terms, approving safety, or authorizing physical work.

## Acceptance criteria

1. A facility can answer capability, safety, schedule, data, and ownership questions from the packet without reconstructing the research premise.
2. The packet distinguishes required capabilities from optional characterization.
3. Every unknown cost, material, and safety item is explicitly marked unknown or owner/facility decision-required.
4. The data-return contract preserves specimen, batch, instrument, calibration, unit, uncertainty, and missingness metadata.
5. The packet contains a binary partner gate: `FEASIBLE_FOR_REVIEW`, `REVISE`, or `NO_MATCH`.

## Expected implementation surface

`docs/partners/partner-readiness-package.md`, `docs/partners/facility-capability-matrix.csv`, `schemas/partner-result.schema.json`, `artifacts/goals/GP3/`.

## Authority boundaries

No outbound communication or external state change is authorized. Credentials and private contact information are excluded from repository artifacts.

## Verification evidence

Packet completeness checklist, schema validation, and `artifacts/goals/GP3/report.md`.

## Stop conditions

Stop if no qualified facility capability can plausibly cover the primary endpoint, or if the safety/ownership questions cannot be stated clearly enough for review.
