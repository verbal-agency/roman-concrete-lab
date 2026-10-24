from __future__ import annotations

import json
import tempfile
from pathlib import Path

from src.roman_concrete_lab.agents.investigation import (
    ActiveInvestigationRunner,
    InvestigationBudget,
    _validate_frozen_phase_input,
    load_jsonl,
    phase_a,
    schema,
    source_policy,
)
from src.roman_concrete_lab.retrieval import RecordedRetrievalAdapter
from src.roman_concrete_lab.retrieval import StaleContext
from tools.evaluation.offline_remediation_integration import _RemediationAdapter, _RemediationProvider
from tools.tournament.replay import ROOT


def test_live_a2m_persists_the_research_loop_contracts_and_replays_without_calls():
    case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        budget = InvestigationBudget()
        runner = ActiveInvestigationRunner(
            case=case,
            arm="A2-M",
            adapter=_RemediationAdapter(budget=budget),
            provider=_RemediationProvider(),
            budget=budget,
            checkpoint_path=directory / "a2m.json",
            manifest_sha256=phase_a()["manifest_sha256"],
            run_id="g10r-v-wiring-fixture",
            document_cache_dir=directory / "raw",
        )
        result = runner.run(owner_activated=True)
        assert result["status"] == "COMPLETED"
        loop = runner.checkpoint["research_loop"]
        assert loop["stage"] == "COMPLETED"
        assert loop["needs"]
        assert loop["searches"]
        assert loop["selections"]
        assert loop["dossier_revisions"]
        assert len(loop["dossier_revisions"]) >= 2
        assert loop["focus"]
        assert loop["open_slot"]
        assert loop["open_slot"][0]["promotion_status"] == "REVIEW_REQUIRED"
        json.dumps(loop, sort_keys=True)

        replay_provider = _RemediationProvider()
        replay_budget = InvestigationBudget()
        replay_runner = ActiveInvestigationRunner(
            case=case,
            arm="A2-M",
            adapter=_RemediationAdapter(budget=replay_budget),
            provider=replay_provider,
            budget=replay_budget,
            checkpoint_path=directory / "a2m.json",
            manifest_sha256=phase_a()["manifest_sha256"],
            run_id="g10r-v-wiring-fixture",
            document_cache_dir=directory / "raw",
        )
        replay = replay_runner.run(owner_activated=True)
        assert replay["status"] == "COMPLETED"
        assert replay_provider.calls == []


def test_historical_g10r_u_manifest_is_rejected_after_wiring_changes():
    phase_a_result = {"manifest_sha256": "sha256:legacy-phase-a"}
    try:
        _validate_frozen_phase_input(
            phase_a_result=phase_a_result,
            frozen_path=ROOT / "artifacts/goals/G10R-U/manifest.json",
        )
    except StaleContext:
        return
    raise AssertionError("historical G10R-U manifest must not authorize the rewired runner")
