# G10M Phase-A report

- Status: `MECHANISM_SOCIETY_READY`
- Protocol: `g10m.1-mechanism-proponent-society`
- Development cases: `2`
- Sealed cases: `4`
- Roster audit: `True`
- Behavior fixtures: `True`
- Budget equality: `True`
- Live model/network/spend: `not authorized`

The mechanism roster is a search scaffold. All mechanism records, critiques, predictions, and focus decisions remain derived and `REVIEW_REQUIRED`; no result authorizes scientific promotion or laboratory work.

## Criterion evidence

- Criterion 1: docs/protocols/mechanism-proponent-society.md, schemas/mechanism-card.schema.json, schemas/mechanism-proponent-report.schema.json, schemas/structural-critique.schema.json, schemas/mechanism-admission.schema.json, schemas/mechanism-tournament-ledger.schema.json
- Criterion 2: src/roman_concrete_lab/agents/mechanism_tournament.py, tests/agents/test_mechanism_tournament.py::test_proponents_are_private_until_all_commit, tests/agents/test_mechanism_tournament.py::test_structural_audit_requires_sharing_and_admission_is_bounded
- Criterion 3: fixtures/investigation/mechanism-rosters.json, artifacts/goals/G10M/phase-a.json:roster_audit
- Criterion 4: artifacts/goals/G10M/phase-a.json:budget_equality, tests/agents/test_mechanism_tournament.py::test_focus_is_deterministic_and_preserves_null_and_rival
- Criterion 5: src/roman_concrete_lab/agents/mechanism_tournament.py:score_mechanism_ledger, tests/agents/test_mechanism_tournament.py::test_offline_run_preserves_rival_and_null_and_replays
- Criterion 6: fixtures/investigation/mechanism-behavior-fixtures.json, tests/agents/test_mechanism_tournament.py
- Criterion 7: artifacts/goals/G10M/phase-a.json, artifacts/goals/G10M/report.md
- Criterion 8: artifacts/goals/G10M/phase-a.json:phase_b_authorized, docs/protocols/active-investigation-pilot.md
