import json

from tools.evaluation.offline_remediation_integration import replay


def test_g10r_s_integrates_the_combined_treatment_without_external_calls() -> None:
    output = replay()
    assert output["status"] == "RUNTIME_REMEDIATION_READY"
    assert output["external_calls"] is False
    assert output["byte_stable"] is True
    assert all(output["cases"][index]["remediation_manifest"]["active"] for index in range(len(output["cases"])))


def test_g10r_s_preserves_fetch_metadata_pending_duplicates_and_open_slot() -> None:
    output = replay()
    for row in output["cases"]:
        actions = row["action_records"]
        assert any(item["action_type"] == "FETCH_PERMITTED_CONTENT" and item["output_ids"] for item in actions)
        assert any(item["input"].get("suppressed_duplicate") for item in actions)
        assert any(item.endswith("-ADMITTED") for item in row["viewpoint_society"]["active_ids"])
        assert row["paper_evidence_cards"]
        assert any(candidate.get("content_hash") is None for candidate in row["source_candidates"].values())
        assert row["viewpoint_society"]["portfolio"]["credible_rival_ids"]
        assert not any(dossier.get("diagnostics") for dossier in row["evidence_bus"]["dossiers"].values())


def test_g10r_s_records_edge_case_fixture_checks() -> None:
    output = replay()
    assert output["edge_cases"] == {
        "malformed_provider_output": True,
        "partial_checkpoint_trace": True,
        "budget_exhaustion": True,
    }


def test_g10r_s_replay_summary_is_json_serializable() -> None:
    json.dumps(replay(), sort_keys=True)
