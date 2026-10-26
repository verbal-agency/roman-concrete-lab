from __future__ import annotations

import json
import tempfile
from pathlib import Path

from jsonschema import validate

from src.roman_concrete_lab.agents.acquisition import resolve_public_locator
from src.roman_concrete_lab.retrieval import SourcePolicy
from tools.evaluation.acquisition_headroom_repair import execute, execute_replay


ROOT = Path(__file__).resolve().parents[2]


def test_both_arms_resolve_and_map_same_public_candidate():
    with tempfile.TemporaryDirectory() as directory:
        result = execute(Path(directory))
    runs = {(row["case_family"], row["arm"]): row for row in result["run"]["runs"]}
    a1 = runs[("positive_public_content", "A1")]
    a2 = runs[("positive_public_content", "A2-M")]
    assert a1["resolutions"] == a2["resolutions"]
    assert a1["metrics"]["paper_card_count"] == a2["metrics"]["paper_card_count"] == 1
    assert a1["selections"][0]["content_locator"] == a2["selections"][0]["content_locator"]


def test_metadata_rights_and_malformed_routes_are_typed_and_uncredited():
    with tempfile.TemporaryDirectory() as directory:
        result = execute(Path(directory))
    runs = result["run"]["runs"]
    for family in ("metadata_only", "rights_blocked", "malformed_locator"):
        for row in [item for item in runs if item["case_family"] == family]:
            assert row["metrics"]["evidence_score"] == 0
            assert row["metrics"]["unique_source_backed_contributions"] == 0
            assert row["resolutions"][0]["status"] in {"METADATA_ONLY", "RIGHTS_BLOCKED", "INVALID"}


def test_positive_fixtures_require_arm_neutral_headroom():
    with tempfile.TemporaryDirectory() as directory:
        result = execute(Path(directory))
    assert all(row["status"] == "READY" for row in result["matrix"]["headroom"] if row["case_family"] in {"positive_public_content", "contradictory_support"})
    assert result["matrix"]["arm_neutrality"] is True


def test_open_slot_is_delayed_and_abstention_creates_no_work():
    with tempfile.TemporaryDirectory() as directory:
        result = execute(Path(directory))
    row = next(item for item in result["run"]["runs"] if item["case_family"] == "metadata_only" and item["arm"] == "A2-M")
    admission = row["open_admission"]
    assert admission["shared_before_admission"] is True
    assert admission["tasks_created_before_admission"] == 0
    assert admission["dossier_created_before_admission"] == 0


def test_replay_is_byte_stable_and_external_free():
    with tempfile.TemporaryDirectory() as directory:
        result = execute(Path(directory))
    assert result["replay"] == execute_replay(
        json.loads((ROOT / "fixtures/investigation/g10r-z/cases.json").read_text())["fixtures"],
        {row["source_candidate_id"]: row for row in [json.loads(line) for line in (ROOT / "fixtures/investigation/g10r-z/sources.jsonl").read_text().splitlines() if line.strip()]},
        SourcePolicy.load(ROOT / "fixtures/investigation/source-policy.json"),
    )
    assert result["replay"]["byte_stable"] is True
    assert result["replay"]["external_calls"] is False


def test_resolution_never_derives_route_from_prose():
    policy = SourcePolicy.load(ROOT / "fixtures/investigation/source-policy.json")
    candidate = {
        "source_candidate_id": "PROSE",
        "problem_id": "roman-hot-mix",
        "problem_version": "1.0",
        "locator": "https://doi.org/10.0000/prose",
        "route_records": [{"locator": "download this paper", "recorded_exact": False, "route_kind": "prose"}],
    }
    resolution = resolve_public_locator(candidate, policy=policy)
    assert resolution["status"] == "INVALID"
    assert resolution["selected_exact_content_locator"] is None


def test_all_criteria_pass_and_artifacts_are_validated():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        result = execute(path)
        assert result["verdict"] == "ACQUISITION_HEADROOM_READY"
        assert result["criterion_ledger"]["criteria_pass"] is True
        assert all(status["status"] == "PASS" for status in result["matrix"]["edge_cases"].values())
        for name, schema_name in (("headroom-matrix.json", None), ("run.json", None), ("replay.json", None), ("criterion-ledger.json", None)):
            assert json.loads((path / name).read_text())
        for row in result["criterion_ledger"]["criteria"]:
            assert row["status"] == "PASS"
