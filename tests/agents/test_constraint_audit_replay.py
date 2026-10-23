from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from src.roman_concrete_lab.agents.investigation import ActiveInvestigationRunner, bound_plan, load_jsonl, phase_a
from src.roman_concrete_lab.retrieval import InvestigationBudget
from tools.evaluation.constraint_audit_replay import replay
from tools.tournament.replay import ROOT


def test_pre_rerun_constraint_audit_is_ready_and_offline():
    result = replay()

    assert result["status"] == "PRE_RERUN_CONSTRAINTS_READY"
    assert result["external_calls"] is False
    assert len(result["constraint_matrix"]) == 8
    assert result["resolution_fixture"]["passes"] is True
    assert result["output_fixture"]["compact_schema_valid"] is True
    assert result["output_fixture"]["malformed_rejected"] is True
    assert result["replays"]["acquisition_byte_stable"] is True
    assert result["replays"]["open_world_byte_stable"] is True
    assert result["replays"]["open_world_manifest_matches"] is True
    assert result["replays"]["runtime_status"] == "RUNTIME_INTEGRATION_READY"
    assert result["replays"]["plumbing_status"] == "SOCIETY_PLUMBING_READY"
    assert result["join_fixture"]["candidate_variant_retained"] is True
    assert result["join_fixture"]["checkpoint_resume_stable"] is True
    assert result["join_fixture"]["duplicate_action_replayed"] is True
    assert result["join_fixture"]["envelope_diagnostics"] == []
    assert len(result["score_ledger"]) == 8
    assert all(set(row["request_cause"]) == {"NOT_REQUESTED", "RUNNER_REJECTED", "POLICY_BLOCKED", "NO_USABLE_RESULT", "EXECUTED_CARD"} for row in result["score_ledger"])


def test_runner_rejection_is_not_mislabeled_as_policy_block():
    case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
    with TemporaryDirectory() as directory:
        runner = ActiveInvestigationRunner(
            case=case,
            arm="A1",
            adapter=object(),
            provider=None,
            budget=InvestigationBudget(),
            checkpoint_path=Path(directory) / "runner.json",
            manifest_sha256=phase_a()["manifest_sha256"],
            run_id="G10R-C-runner-rejection",
        )
        runner._execute_requested_tools(
            "single_investigator",
            {"requested_fetch_locators": ["https://www.repository.cam.ac.uk/fixture.pdf"], "simulation_requests": []},
        )
        assert runner.actions[-1]["policy_status"] == "RUNNER_REJECTED"
        assert runner.tool_request_events[-1]["status"] == "RUNNER_REJECTED"


def test_plan_overflow_is_bounded_and_recorded():
    plan = {
        "requested_fetch_locators": ["OA-1", "OA-2", "OA-3", "OA-4", "OA-5"],
        "primary_queries": [], "follow_up_queries": [], "simulation_requests": [],
    }
    bounded, overflow = bound_plan(plan)
    assert bounded["requested_fetch_locators"] == ["OA-1", "OA-2", "OA-3", "OA-4"]
    assert overflow["requested_fetch_locators"] == ["OA-5"]
