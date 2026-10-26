# G10R-Z acquisition headroom and society validity

`ACQUISITION_HEADROOM_READY`

The offline gate uses one exact-route resolver and one policy hash for A1 and A2-M. Public fixtures produce page-aware cards; metadata-only, rights-blocked, and malformed routes remain typed nonfatal outcomes. The open slot is recorded only after initial sharing and receives no pre-admission tasks or dossier.

Positive public-content cards: A1=1, A2-M=1. Metadata-only source-backed contribution: A1=0, A2-M=0.

## Acceptance ledger

- Criterion 1: **PASS** — headroom-matrix.json, run.json
- Criterion 2: **PASS** — headroom-matrix.json
- Criterion 3: **PASS** — headroom-matrix.json
- Criterion 4: **PASS** — run.json#open_admission
- Criterion 5: **PASS** — run.json#support_reports
- Criterion 6: **PASS** — run.json#metadata_only
- Criterion 7: **PASS** — run.json#budget
- Criterion 8: **PASS** — headroom-matrix.json#edge_cases, replay.json
- Criterion 9: **PASS** — replay.json
- Criterion 10: **PASS** — tests/agents/test_g10r_z_acquisition_headroom.py, python3 -m pytest -q

Replay: byte-stable=True; external calls=False; duplicate calls=0.

This result validates the offline plumbing and fixture headroom only. It does not authorize a Phase-A freeze, a paid run, evidence promotion, or laboratory work.
