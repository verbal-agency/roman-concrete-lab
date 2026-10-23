from __future__ import annotations

from pathlib import Path

from tools.evaluation.fresh_phase_a_freeze import (
    MANIFEST_NAME,
    PHASE_NAME,
    freeze,
)
from src.roman_concrete_lab.agents.investigation import canonical


def test_fresh_phase_a_freeze_is_distinct_stable_and_offline(tmp_path: Path):
    first = freeze(output_dir=tmp_path)
    second = freeze(output_dir=tmp_path)

    assert first["status"] == "PHASE_A_READY_FOR_OWNER_ACTIVATION"
    assert second["status"] == first["status"]
    assert first["external_calls"] is False
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert canonical(first["phase_a"]) == canonical(second["phase_a"])
    assert (tmp_path / PHASE_NAME).exists()
    assert (tmp_path / MANIFEST_NAME).exists()
    assert first["phase_a"]["sealed_case_count"] == 4
    assert first["phase_a"]["development_case_count"] >= 2
    assert first["phase_a"]["identity_preflight"]["passes"] is True
    assert first["phase_a"]["mechanism_preflight"]["passes"] is True
    assert first["phase_a"]["pdf_extraction_benchmark"]["passes"] is True
