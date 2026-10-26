from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from src.roman_concrete_lab.agents.investigation import InvestigationBudget, load_jsonl, phase_a
from src.roman_concrete_lab.agents.investigation_g10r_z import AcquisitionHeadroomRunner
from src.roman_concrete_lab.retrieval import SourcePolicy
from tools.evaluation.fresh_phase_a_freeze_after_acquisition_headroom import (
    MANIFEST_ID,
    _file_map,
    _load_json,
    _predecessor,
    _sha,
    freeze,
    validate_inputs,
)
from tools.evaluation.offline_remediation_integration import _RemediationAdapter, _RemediationProvider
from tools.tournament.replay import ROOT


def test_live_wrapper_preserves_g10r_z_contracts() -> None:
    case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        budget = InvestigationBudget()
        runner = AcquisitionHeadroomRunner(
            case=case,
            arm="A2-M",
            adapter=_RemediationAdapter(budget=budget),
            provider=_RemediationProvider(),
            budget=budget,
            checkpoint_path=directory / "run.json",
            manifest_sha256=phase_a()["manifest_sha256"],
            run_id="g10r-aa-wrapper-smoke",
            document_cache_dir=directory / "raw",
        )
        result = runner.run(owner_activated=True)
        assert result["status"] == "COMPLETED"
        resolutions = runner.checkpoint["locator_resolutions"].values()
        assert any(item["status"] == "RESOLVED_PUBLIC" for item in resolutions)
        assert runner.checkpoint["research_loop"]["open_slot"]
        assert runner.checkpoint["viewpoint_society"]["evidence_bus"]["reports"]
        delayed = runner.checkpoint["delayed_open_admission"]
        assert delayed["shared_before_admission"] is True
        assert delayed["tasks_created_before_admission"] == 0
        assert delayed["dossier_created_before_admission"] == 0
        assert not any(item.endswith("-ADMITTED") for item in runner.checkpoint["viewpoint_society"]["active_ids"])
        assert result["score"]["evidence_score"] == sum(item["points"] for item in result["score"]["rubric_hits"])

        metadata_candidate = {
            "source_candidate_id": "Z-METADATA",
            "problem_id": "roman-hot-mix",
            "problem_version": "1.0",
            "case_id": case["case_id"],
            "locator": "https://doi.org/10.0000/z-metadata",
            "route_records": [{"locator": "https://doi.org/10.0000/z-metadata", "route_kind": "doi_metadata", "recorded_exact": True}],
        }
        runner.candidates["Z-METADATA"] = metadata_candidate
        resolution = runner.resolve_g10r_z_locator(metadata_candidate["locator"])
        assert resolution["status"] == "METADATA_ONLY"
        before = runner.budget.snapshot()
        assert runner._fetch(branch_id="viewpoint:metadata", locator=metadata_candidate["locator"], rationale="typed no-content smoke") == []
        assert runner.budget.snapshot() == before
        assert runner.actions[-1]["policy_status"] == "RUNNER_REJECTED"
        assert not runner.paper_cards.get("Z-METADATA")


def test_manifest_links_predecessor_and_hashes_inputs() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = freeze(output_dir=Path(directory), run_tests=False)
        manifest = result["manifest"]
        assert result["status"] == "PHASE_A_READY_FOR_OWNER_ACTIVATION"
        assert manifest["manifest_id"] == MANIFEST_ID
        assert manifest["predecessor"]["manifest_id"] == "G10R-Z-acquisition-headroom-v1"
        assert all(Path(ROOT / entry["path"]).exists() and _sha(entry["path"]) == entry["sha256"] for entry in manifest["files"].values())


def test_positive_headroom_and_policy_hash_match() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = freeze(output_dir=Path(directory), run_tests=False)
        preflight = result["preflight"]
        assert preflight["checks"]["positive_headroom_ready"] is True
        assert preflight["checks"]["policy_hash_matches"] is True
        assert preflight["checks"]["arm_neutrality"] is True


def test_manifest_preserves_frozen_ceilings_and_pending_activation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        result = freeze(output_dir=output, run_tests=False)
        manifest = result["manifest"]
        request = json.loads((output / "owner-activation-request.json").read_text())
        assert manifest["limits_per_treatment_case"]["estimated_cost_usd"] == 25.0
        assert manifest["model_policy"]["provider"] == "openai"
        assert manifest["model_policy"]["store"] is False
        assert request["status"] == "PENDING_OWNER_ACTIVATION"
        assert request["manifest_sha256"] == result["preflight"]["manifest_sha256"]


def test_historical_hashes_and_namespace_are_distinct() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = freeze(output_dir=Path(directory), run_tests=False)
        assert result["preflight"]["checks"]["historical_namespaces_preserved"] is True
        assert result["manifest"]["output_namespace"] == "artifacts/goals/G10R-AA/"
        replay = freeze(output_dir=Path(directory), run_tests=False)
        assert replay["replay"]["byte_stable"] is True
        assert replay["replay"]["provider_calls"] == 0
        assert replay["replay"]["budget_debit"] == 0


def test_replay_is_byte_stable_and_external_free() -> None:
    with tempfile.TemporaryDirectory() as directory:
        first = freeze(output_dir=Path(directory), run_tests=False)
        second = freeze(output_dir=Path(directory), run_tests=False)
        assert first["manifest"] == second["manifest"]
        assert second["replay"]["external_calls"] is False
        assert second["replay"]["network_calls"] == 0
        assert second["replay"]["credentials_read"] is False


def test_stale_malformed_and_cross_case_inputs_fail_closed() -> None:
    predecessor = _predecessor()
    matrix = _load_json("artifacts/goals/G10R-Z/headroom-matrix.json")
    files = _file_map()
    policy_hash = SourcePolicy.load(ROOT / "fixtures/investigation/source-policy.json").sha256
    fixture_hash = predecessor["fixture_hash"]

    stale = deepcopy(predecessor)
    stale["artifact_sha256"] = "sha256:stale"
    assert any(item["code"] == "STALE_PREDECESSOR" for item in validate_inputs(predecessor=stale, matrix=matrix, files=files, policy_hash=policy_hash, fixture_hash=fixture_hash))

    missing = deepcopy(files)
    missing["headroom_schema"]["path"] = "schemas/missing.json"
    assert any(item["code"] == "MISSING_SCHEMA" for item in validate_inputs(predecessor=predecessor, matrix=matrix, files=missing, policy_hash=policy_hash, fixture_hash=fixture_hash))

    malformed = deepcopy(matrix)
    malformed["goal"] = "OTHER-CASE"
    assert any(item["code"] == "CROSS_CASE_OR_STALE_FIXTURE" for item in validate_inputs(predecessor=predecessor, matrix=malformed, files=files, policy_hash=policy_hash, fixture_hash=fixture_hash))

    changed_policy = deepcopy(matrix)
    changed_policy["policy_hash"] = "sha256:changed"
    assert any(item["code"] == "CHANGED_POLICY" for item in validate_inputs(predecessor=predecessor, matrix=changed_policy, files=files, policy_hash=policy_hash, fixture_hash=fixture_hash))


def test_activation_request_is_pending_only() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = freeze(output_dir=Path(directory), run_tests=False)
        request = json.loads((Path(directory) / "owner-activation-request.json").read_text())
        assert request["status"] == "PENDING_OWNER_ACTIVATION"
        assert result["preflight"]["authority"] == {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0.0}


def test_criterion_ledger_and_single_verdict_artifacts_are_ready() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = freeze(output_dir=Path(directory), run_tests=False)
        assert result["status"] in {"PHASE_A_READY_FOR_OWNER_ACTIVATION", "PHASE_A_FREEZE_NO_GO"}
        report = (Path(directory) / "report.md").read_text()
        assert report.count("`PHASE_A_READY_FOR_OWNER_ACTIVATION`") + report.count("`PHASE_A_FREEZE_NO_GO`") == 1
