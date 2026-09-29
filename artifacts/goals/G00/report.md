# G00 cycle report — complete

**Date:** 2026-09-28
**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; GP1 is the next eligible goal

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. One compatible track and applicable decisions | **PASS** | `docs/decisions/0001-program-charter.md` selects `EXPLORATORY_PLATFORM`, approves current-plane rights/budget/NO-GO boundaries, and defers later-gate decisions explicitly |
| 2. Scope, estimand, NO-GO, eligibility, amendment rule | **PASS** | charter problem context and amendment sections; `docs/protocols/exploration-contracts.md` |
| 3. No unauthorized model/lab/agent scaffold | **PASS** | documentation-only contracts; no model, lab protocol, physical execution, or agent runtime added |
| 4. Clean verification | **PASS** | `git diff --check`; G-1 decision JSON validation; contract/report presence checks; existing decision tests remain unchanged |
| 5. Secret/restricted/generated-file handling | **PASS** | `.gitignore` covers credentials, restricted raw material, caches, and generated outputs without hiding manifests, schemas, fixtures, or reports |
| 6. No nonessential framework/service dependency | **PASS** | no dependencies, services, or runtime frameworks added |

## Authorized surface

- `docs/protocols/exploration-contracts.md` defines the versioned context card, candidate/hypothesis surface, conditional ranking, portfolio/feedback boundary, and deterministic behavior matrix.
- `README.md` states the scientific boundary and current stage.
- `docs/decisions/0001-program-charter.md` records the approved exploration charter and later-gate deferrals.
- `docs/roadmap.md` records the revised gate placement.

## Explicit exclusions preserved

G00 does not authorize source acquisition beyond G-1’s lawful read-only boundary, model calls, predictive training, recipe inference, physical execution, external communication, commercial release, or agent-framework construction. GL1 remains the qualified-facility/safety gate; GL2 remains the physical-feedback gate; G10 remains the agent-provider gate.

## Handoff

GP1 may now execute. It must consume the versioned problem context and produce the candidate evidence and rival-hypothesis dossier. It may not promote provisional evidence or bypass the GL1/GL2 boundaries.
