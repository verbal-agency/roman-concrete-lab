# G10R-F fresh Phase-A freeze

## Handoff

`PHASE_A_READY_FOR_OWNER_ACTIVATION`

This freeze recomputed the G10R Phase-A preflight after G10R-C constraint
remediation. It made no model, network, subscription, credential, promotion,
laboratory, or external communication call. Historical `phase-a.json` and
`manifest.json` were not overwritten.

## Checks

- `phase_status`: `AWAITING_OWNER_ACTIVATION`
- `manifest_hash_present`: `True`
- `manifest_matches_phase`: `True`
- `sealed_case_count`: `4`
- `development_case_count`: `2`
- `identity_preflight`: `True`
- `mechanism_preflight`: `True`
- `a0_headroom`: `True`
- `pdf_benchmark`: `True`
- `source_policy_default_deny`: `True`
- `equal_budget_limits`: `True`
- `repaired_runner_in_manifest`: `True`
- `repaired_locator_contract_in_runner`: `True`
- `historical_phase_preserved`: `True`
- `historical_manifest_preserved`: `True`
- `repeated_freeze_byte_stable`: `True`

The distinct artifacts are `phase-a-post-constraint-20261023.json` and `manifest-post-constraint-20261023.json`. The manifest
retains the exact runner, action schema, source-policy, society, evidence-bus,
fixture, and budget hashes used for a separately authorized Phase-B decision.
This goal does not authorize Phase B.
