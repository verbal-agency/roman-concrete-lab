# G10R-X — Fresh Phase-A freeze after live research-loop wiring

**Status:** complete — `PHASE_A_READY_FOR_OWNER_ACTIVATION`
**Dependencies:** G10R-W `RUNTIME_RESEARCH_LOOP_WIRED`; no model or network calls

## Objective

Create a new, separately namespaced Phase-A manifest that hashes the live
research-loop ledger, runner integration, dossier-refresh behavior, and wiring
tests. Preserve G10R-U and its activation request as historical artifacts; do
not mutate or silently reinterpret them.

## Acceptance

1. The manifest includes the exact source and schema files used by the live
   A2-M research loop and their current hashes.
2. Focused, full-suite, and offline replay tests pass without provider or
   network initialization.
3. The activation request names the new manifest ID/hash, exact model and
   source policy, the existing aggregate `$25` ceiling, and a fresh output
   namespace.
4. The freeze explicitly records that G10R-V remains blocked until a separate
   owner activation names this new manifest.

No Phase-B call is authorized by completing this goal.
