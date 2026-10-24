from __future__ import annotations

import json

from tools.evaluation.society_failure_experiments import run_experiments


def test_failure_experiment_matrix_is_complete_and_offline() -> None:
    result = run_experiments()

    assert result["status"] == "SOCIETY_REMEDIATION_READY"
    assert result["external_calls"] is False
    assert result["architecture_preserved"] is True
    assert [arm["arm_id"] for arm in result["arms"]] == [
        "BASELINE_B2_BEHAVIOR",
        "ACQUISITION_FIRST",
        "EXECUTABLE_SUPPORT",
        "LOCATOR_BRIDGE",
        "DEDUP_AND_OPEN_SLOT",
        "COMBINED_JUSTIFIED",
    ]
    assert all(arm["metrics"]["budget_limits"] == result["budget_limits"] for arm in result["arms"])


def test_failure_experiments_show_which_interventions_help() -> None:
    result = run_experiments()
    arms = {arm["arm_id"]: arm for arm in result["arms"]}

    assert arms["BASELINE_B2_BEHAVIOR"]["metrics"]["fetch_request_yield"] == 0
    assert arms["ACQUISITION_FIRST"]["metrics"]["evidence_card_yield"] >= 1
    assert arms["LOCATOR_BRIDGE"]["metrics"]["fetch_request_yield"] >= 1
    assert arms["EXECUTABLE_SUPPORT"]["metrics"]["support_task_execution_rate"] == 1.0
    assert arms["DEDUP_AND_OPEN_SLOT"]["metrics"]["duplicate_queries_suppressed"] >= 1
    assert arms["DEDUP_AND_OPEN_SLOT"]["metrics"]["open_slot_work"] is True
    assert arms["COMBINED_JUSTIFIED"]["metrics"]["evidence_card_yield"] >= 1
    assert arms["COMBINED_JUSTIFIED"]["metrics"]["contradiction_coverage"] >= 1


def test_failure_experiment_fixtures_preserve_safety_and_replay() -> None:
    result = run_experiments()
    checks = result["fixture_checks"]

    assert checks["external_calls"] is False
    assert all(value for key, value in checks.items() if key != "external_calls")
    assert result["recommendation"]["minimum_combined_treatment"] == "COMBINED_JUSTIFIED"
    assert "DEDUP_AND_OPEN_SLOT" in result["recommendation"]["retain_as_enabler_only"]
    assert all(arm["metrics"]["critical_failures"] == [] for arm in result["arms"])


def test_failure_experiment_is_byte_stable() -> None:
    first = json.dumps(run_experiments(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(run_experiments(), sort_keys=True, separators=(",", ":"))
    assert first == second
