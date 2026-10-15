from __future__ import annotations

from tools.evaluation.runtime_integration_replay import replay


def test_runtime_gate_exercises_the_integrated_society_without_external_calls() -> None:
    output = replay()

    assert output["external_calls"] is False
    assert output["status"] == "RUNTIME_INTEGRATION_READY"
    assert output["runner_audit"]["legacy_mechanism_tournament_imported"] is False
    assert output["runner_audit"]["viewpoint_society_imported"] is True
    assert output["runner_audit"]["evidence_bus_imported"] is True
    assert output["runtime_ready"] is True
    assert output["runtime_smoke"]["open_slot_admitted"] is True
    assert output["runtime_smoke"]["evidence_bus_join_diagnostics"] == []


def test_g10d_fixtures_themselves_pass_the_viewpoint_topology() -> None:
    output = replay()

    assert output["fixture_ready"] is True
    assert len(output["fixtures"]) == 2
    assert all(row["support_task_count"] > 0 for row in output["fixtures"])
    assert all(row["dossier_count"] > 0 for row in output["fixtures"])
    assert all(row["evidence_promotion"] is False for row in output["fixtures"])
    assert output["document_fixture"]["positive_page_card"] is True
    assert output["document_fixture"]["negative_rights_blocked"] is True
    assert output["document_fixture"]["payload_retained"] is False
