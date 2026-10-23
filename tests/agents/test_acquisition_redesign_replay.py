from __future__ import annotations

from tools.evaluation.acquisition_redesign_replay import replay


def test_offline_acquisition_replay_exercises_lifecycle_and_support_tasks():
    result = replay()

    assert result["status"] == "ACQUISITION_DESIGN_READY"
    assert result["external_calls"] is False
    assert result["replay_stable"] is True

    score = result["offline_run"]["score"]
    assert score["request_lifecycle"] == {
        "EXECUTED_CARD": 1,
        "NO_USABLE_RESULT": 1,
        "NOT_REQUESTED": 1,
        "POLICY_BLOCKED": 1,
        "RUNNER_REJECTED": 1,
    }
    assert score["page_aware_card_count"] >= 1
    assert score["support_contribution_count"] >= 1
    assert score["weakening_contribution_count"] >= 1
    assert score["evidence_promotion"] is False
    assert score["blocked_fixture_verified"] is True
    assert score["malformed_fixture_verified"] is True
    assert result["offline_run"]["focus"]["status"] == "ALLOCATED"
    assert result["offline_run"]["envelope"]["diagnostics"] == []
