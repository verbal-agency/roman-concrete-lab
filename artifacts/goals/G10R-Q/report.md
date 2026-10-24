# G10R-Q society failure-experiment loop

`SOCIETY_REMEDIATION_READY`

- Baseline source: `/Users/wcu/Desktop/portfolio/roman-concrete-lab/artifacts/goals/G10R-B2-retry-20261023/run.json`
- Manifest: `sha256:fb76226b4332f50ce3f5e8ad15a65d3d274d8cc3a031894918f5e020728e38bf`
- Arms executed: `BASELINE_B2_BEHAVIOR, ACQUISITION_FIRST, EXECUTABLE_SUPPORT, LOCATOR_BRIDGE, DEDUP_AND_OPEN_SLOT, COMBINED_JUSTIFIED`
- External calls: `false`

The society architecture is preserved. The experiment compares acquisition-first scheduling, executable support, locator bridging, deduplication, open-slot work, and their justified combination under fixed offline budgets.

## Effect summary
- `BASELINE_B2_BEHAVIOR`: fetches=0, cards=0, support-task-rate=0.20, duplicates-suppressed=0, coordination-cost=12
- `ACQUISITION_FIRST`: fetches=2, cards=1, support-task-rate=0.20, duplicates-suppressed=0, coordination-cost=12
- `EXECUTABLE_SUPPORT`: fetches=0, cards=0, support-task-rate=1.00, duplicates-suppressed=0, coordination-cost=0
- `LOCATOR_BRIDGE`: fetches=2, cards=1, support-task-rate=0.20, duplicates-suppressed=0, coordination-cost=12
- `DEDUP_AND_OPEN_SLOT`: fetches=0, cards=0, support-task-rate=0.15, duplicates-suppressed=1, coordination-cost=17
- `COMBINED_JUSTIFIED`: fetches=3, cards=1, support-task-rate=1.00, duplicates-suppressed=1, coordination-cost=0

## Fixture checks

- `budget_exhaustion_typed`: `True`
- `duplicate_query_fixture`: `True`
- `external_calls`: `False`
- `malformed_rejected`: `True`
- `open_slot_fixture`: `True`
- `partial_failure_replayed`: `True`
- `unique_discovery_fixture`: `True`
- `unresolved_candidate_fixture`: `True`
- `weakening_contradiction_fixture`: `True`

## Recommendation

Retain: `ACQUISITION_FIRST, EXECUTABLE_SUPPORT, LOCATOR_BRIDGE, COMBINED_JUSTIFIED`. Use `DEDUP_AND_OPEN_SLOT` only as an enabler, not as a standalone treatment.

No paid rerun is authorized by this goal.
