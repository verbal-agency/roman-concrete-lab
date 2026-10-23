from __future__ import annotations

from tools.evaluation.society_postmortem import build_postmortem


def test_postmortem_reconstructs_live_run_and_confirms_runtime_contract() -> None:
    output = build_postmortem()

    assert output["status"] == "TARGET_STATE_READY_FOR_OFFLINE_BUILD"
    assert output["external_calls"] is False
    assert output["source_run_outcome"] == "DO_NOT_ESCALATE_ACTIVE_SOCIETY"
    assert len(output["case_ledger"]) == 8
    assert output["runtime_contract_audit"]["legacy_mechanism_tournament_imported"] is False
    assert output["runtime_contract_audit"]["g10d_viewpoint_society_imported"] is True
    assert output["runtime_contract_audit"]["g10p_evidence_bus_imported"] is True
    assert output["runtime_contract_audit"]["open_slot_explicitly_filtered_from_live_cards"] is False


def test_postmortem_preserves_offline_remediation_evidence() -> None:
    output = build_postmortem()
    evidence = output["remediation_evidence"]

    assert evidence["g10d_offline_design_ready"] is True
    assert evidence["g10d_preserves_lateral_discovery"] is True
    assert evidence["g10d_preserves_contradiction"] is True
    assert evidence["g10d_preserves_unresolved_candidates"] is True
    assert evidence["g10d_preserves_null_and_rival"] is True
    assert evidence["g10d_blocks_evidence_promotion"] is True
    assert evidence["g10p_plumbing_ready"] is True
    assert evidence["all_external_calls_absent"] is True


def test_target_state_keeps_future_escalation_falsifiable() -> None:
    output = build_postmortem()
    thresholds = output["target_state"]["thresholds"]

    assert thresholds["topology_fidelity"]["legacy_path_only"] is False
    assert thresholds["support_task_link_rate"]["minimum"] == 1.0
    assert thresholds["future_escalation_rule"]["case_gain_min"] == 1
    assert thresholds["future_escalation_rule"]["critical_failures_allowed"] == 0
