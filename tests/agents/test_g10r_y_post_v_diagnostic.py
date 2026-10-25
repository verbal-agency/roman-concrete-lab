from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tools.evaluation.post_v_paid_run_diagnostic import run


def _run() -> dict:
    with tempfile.TemporaryDirectory() as directory:
        result = run(Path(directory))
        result["artifact_names"] = sorted(path.name for path in Path(directory).iterdir())
        result["report"] = (Path(directory) / "report.md").read_text(encoding="utf-8")
        result["replay_artifact"] = json.loads((Path(directory) / "replay.json").read_text(encoding="utf-8"))
        return result


def test_reconstructs_all_case_arm_loss_ledgers():
    result = _run()
    rows = result["diagnosis"]["case_arm_loss_ledger"]
    assert result["verdict"] == "POST_V_DIAGNOSIS_READY"
    assert len(rows) == 8
    assert {(row["case_id"], row["arm"]) for row in rows} == {
        (case, arm)
        for case in ("S-ACTIVE-ACCESS", "S-ACTIVE-LINEAGE", "S-ACTIVE-SIM", "S-ACTIVE-TRANSFER")
        for arm in ("A1", "A2-M")
    }
    assert all(row["acquisition"]["fetch_count"] == 0 for row in rows)
    assert all(row["acquisition"]["paper_card_count"] == 0 for row in rows)


def test_preserves_raw_discovery_and_unresolved_records():
    result = _run()
    totals = result["diagnosis"]["arm_totals"]
    assert totals["A1"]["raw_discovery"] == 20
    assert totals["A2-M"]["raw_discovery"] == 6
    assert totals["A1"]["evidence_score"] == 0
    assert totals["A2-M"]["evidence_score"] == 0
    assert result["diagnosis"]["findings"][-1]["causal_status"] == "PROTECTIVE_NOT_PRIMARY_CAUSE"


def test_metadata_only_ablation_separates_acquisition_from_agent_design():
    result = _run()
    matrix = result["matrix"]
    assert matrix["causal_tests"] == {
        "adaptive_open_slot_can_false-positive_without_content": True,
        "agent_design_and_shared_acquisition_are_distinguishable": True,
        "shared_content_headroom_controls_evidence_yield": True,
    }
    metadata = matrix["conditions"]["METADATA_ONLY"]
    assert metadata["R0_SINGLE"]["metrics"]["paper_card_count"] == 0
    assert metadata["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["paper_card_count"] == 0
    assert metadata["R3_VIEWPOINT_ADAPTIVE"]["open_slot_statuses"] == ["ADMITTED"]
    assert metadata["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["unique_attributable_contributions"] == 1


def test_next_treatment_has_measurable_thresholds_and_stop_rule():
    result = _run()
    thresholds = result["diagnosis"]["proposed_next_treatment_thresholds"]
    assert set(thresholds) == {
        "attribution_completeness",
        "budget_parity",
        "evidence_card_yield",
        "stop_rule",
        "unique_attributable_contribution",
    }
    assert "Do not freeze or pay" in thresholds["stop_rule"]


def test_replay_is_deterministic_external_free_and_preserves_history():
    result = _run()
    replay = result["replay_artifact"]
    assert replay["external_calls"] is False
    assert replay["byte_stable"] is True
    assert replay["historical_artifacts_preserved"] is True
    assert replay["causal_tests_passed"] is True
    assert result["artifact_names"] == [
        "ablation-matrix.json",
        "criterion-ledger.json",
        "diagnosis.json",
        "replay.json",
        "report.md",
    ]
