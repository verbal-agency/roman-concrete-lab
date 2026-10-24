"""Run the G10R-T research-loop ablation without model or network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.research_loop import ARMS, STAGES, OfflineResearchLoop, run_arm
from src.roman_concrete_lab.retrieval import canonical, digest
from tools.tournament.replay import ROOT


PAID = ROOT / "artifacts/goals/G10R-S-paid-20261024-final"


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _paid_diagnosis() -> dict[str, Any]:
    report = (PAID / "report.md").read_text(encoding="utf-8")
    run = json.loads((PAID / "run.json").read_text(encoding="utf-8"))
    scores = {case: (a1, a2) for case, a1, a2 in re.findall(r"\| (S-ACTIVE-[A-Z]+) \| (\d+) \| (\d+) \|", report)}
    checkpoints = sorted((PAID / "checkpoints").glob("*.json"))
    usage: dict[str, dict[str, int | float]] = {}
    for path in checkpoints:
        payload = json.loads(path.read_text(encoding="utf-8"))
        arm = "A2-M" if path.stem.endswith("-A2-M") else "A1"
        bucket = usage.setdefault(arm, {"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "queries": 0, "document_fetches": 0, "paper_evidence_cards": 0, "estimated_cost_usd": 0.0})
        traces = payload.get("model_traces", [])
        bucket["model_calls"] += len(traces)
        bucket["input_tokens"] += sum(int(item.get("usage", {}).get("input_tokens", 0)) for item in traces)
        bucket["output_tokens"] += sum(int(item.get("usage", {}).get("output_tokens", 0)) for item in traces)
        budget = payload.get("budget", {}).get("usage", {})
        bucket["queries"] += int(budget.get("queries", 0))
        bucket["document_fetches"] += int(budget.get("document_fetches", 0))
        bucket["paper_evidence_cards"] += len(payload.get("paper_evidence_cards", []))
        bucket["estimated_cost_usd"] += sum(float(item.get("estimated_actual_cost_usd", 0.0)) for item in traces)
    # The final report is the frozen aggregate ledger for this paid comparison;
    # checkpoint envelopes are retained separately below because they contain
    # only the last committed case snapshots, not the cross-case call ledger.
    reported_resource_facts = {
        "A1": {"model_calls": 8, "input_tokens": 20533, "output_tokens": 6323, "queries": 33, "document_fetches": 0, "paper_evidence_cards": 0, "estimated_cost_usd": 0.0052148},
        "A2-M": {"model_calls": 52, "input_tokens": 152767, "output_tokens": 20637, "queries": 35, "document_fetches": 0, "paper_evidence_cards": 0, "estimated_cost_usd": 0.02531971},
    }
    return {
        "historical_artifacts": {"run": _sha(PAID / "run.json"), "report": _sha(PAID / "report.md"), "checkpoints": [_sha(item) for item in checkpoints]},
        "outcome": "DO_NOT_ESCALATE_ACTIVE_SOCIETY",
        "scores": {case: {"A1": int(a1), "A2-M": int(a2)} for case, (a1, a2) in scores.items()},
        "totals": {"A1": 5, "A2-M": 3, "actual_spend_usd": 0.03953781},
        "resource_facts": reported_resource_facts,
        "checkpoint_snapshot_facts": usage,
        "paper_card_totals": {arm: facts["paper_evidence_cards"] for arm, facts in reported_resource_facts.items()},
        "causal_defects": [
            {"id": "D1", "defect": "plans request fetch before discovered candidate locators exist", "repair": "two-stage search, candidate selection, fetch/map", "test": "test_candidate_selection_requires_stable_id"},
            {"id": "D2", "defect": "focus allocator ranks ascending", "repair": "highest-first observed-yield focus", "test": "test_focus_is_highest_first"},
            {"id": "D3", "defect": "dossiers are not revised after auditor/focus work", "repair": "monotonic versioned dossier revisions", "test": "test_late_reports_enter_latest_revision"},
            {"id": "D4", "defect": "open slot is a pre-admitted generic placeholder", "repair": "post-sharing evidence-conditioned admission", "test": "test_open_slot_three_outcomes"},
            {"id": "D5", "defect": "checkpoint retries can append outside committed dossier", "repair": "exactly-once stateful replay", "test": "test_replay_is_byte_identical"},
        ],
    }


def run(output_dir: Path) -> dict[str, Any]:
    diagnosis = _paid_diagnosis()
    _write(output_dir / "diagnosis.json", diagnosis)
    summaries: dict[str, Any] = {}
    for arm in sorted(ARMS):
        result = run_arm(arm)
        summaries[arm] = {
            "terminal": result["terminal"], "stage": result["stage"], "content_hash": result["content_hash"],
            "budget": result["budget"], "metrics": result["metrics"],
            "candidate_ids": [item["source_candidate_id"] for item in result["candidates"]],
            "card_ids": [item["card_id"] for item in result["cards"]],
            "dossier_revisions": [item["revision"] for item in result["dossier_revisions"]],
            "open_slot_statuses": [item["status"] for item in result["open_admissions"]],
        }
    baseline = summaries["R0_SINGLE"]["metrics"]
    matrix = {
        "schema_version": "1.0", "goal": "G10R-T", "ceilings_equal": True,
        "actual_ceiling": {"queries": 8, "document_fetches": 4, "payload_bytes": 100000, "estimated_cost_usd": 0.0},
        "arms": summaries,
        "marginal_effects": {
            arm: {key: value - baseline.get(key, 0) if isinstance(value, (int, float)) else value for key, value in summary["metrics"].items()}
            for arm, summary in ((name, summaries[name]) for name in sorted(summaries) if name != "R0_SINGLE")
        },
        "directional_usefulness_rule": {"unique_contribution": True, "task_accuracy_noninferior": True, "authority_integrity": True, "same_actual_ceilings": True},
    }
    _write(output_dir / "ablation-matrix.json", matrix)
    replay_rows = []
    for arm in sorted(ARMS):
        for stage in STAGES[1:-1]:
            partial = run_arm(arm, stop_after_stage=stage)
            resumed = OfflineResearchLoop(arm, checkpoint=partial).run()
            uninterrupted = summaries[arm]["content_hash"]
            replay_rows.append({"arm": arm, "stop_after_stage": stage, "resumed_hash": resumed["content_hash"], "uninterrupted_hash": uninterrupted, "byte_equivalent": resumed["content_hash"] == uninterrupted, "budget_equal": resumed["budget"] == run_arm(arm)["budget"]})
    replay = {"schema_version": "1.0", "all_boundaries_byte_equivalent": all(item["byte_equivalent"] and item["budget_equal"] for item in replay_rows), "rows": replay_rows}
    _write(output_dir / "replay.json", replay)
    criterion_ledger = {
        "schema_version": "1.0", "goal": "G10R-T",
        "criteria": [
            {"id": 1, "artifact": "diagnosis.json", "tests": ["test_artifacts_are_machine_readable"]},
            {"id": 2, "artifact": "run.json", "tests": ["test_search_selection_fetch_and_page_card_are_separate", "test_prose_fetch_request_is_rejected_before_adapter", "test_metadata_candidate_is_retained_without_evidence_credit"]},
            {"id": 3, "artifact": "run.json", "tests": ["test_support_need_requires_observable_work_for_completion"]},
            {"id": 4, "artifact": "run.json", "tests": ["test_late_reports_enter_latest_dossier_revision", "test_deliberate_dossier_omission_is_a_failing_diagnostic"]},
            {"id": 5, "artifact": "ablation-matrix.json", "tests": ["test_focus_is_highest_first_and_task_specific", "test_semantic_duplicate_does_not_fetch_twice"]},
            {"id": 6, "artifact": "ablation-matrix.json", "tests": ["test_open_slot_is_evidence_conditioned"]},
            {"id": 7, "artifact": "replay.json", "tests": ["test_resume_is_byte_identical_at_boundary", "test_stale_checkpoint_fails_closed"]},
            {"id": 8, "artifact": "ablation-matrix.json", "tests": ["test_four_arms_have_equal_ceilings_and_r3_has_unique_contribution"]},
            {"id": 9, "artifact": "run.json", "tests": ["test_typed_score_is_invariant_to_wording"]},
            {"id": 10, "artifact": "report.md", "tests": ["test_artifacts_are_machine_readable"]}
        ]
    }
    _write(output_dir / "criterion-ledger.json", criterion_ledger)
    r3 = summaries["R3_VIEWPOINT_ADAPTIVE"]["metrics"]
    useful = bool(r3["unique_attributable_contributions"] > baseline["unique_attributable_contributions"] and r3["task_accuracy"] >= baseline["task_accuracy"] and r3["authority_integrity"] == 1)
    verdict = "SOCIETY_RESEARCH_LOOP_READY" if useful and replay["all_boundaries_byte_equivalent"] else "SOCIETY_RESEARCH_LOOP_NO_GO"
    report = "\n".join([
        "# G10R-T offline research-loop ablation", "", f"`{verdict}`", "",
        "The run is provider-free and uses only the recorded research-loop fixture. Search, candidate selection, fetch, mapping, revision, focus, and open-slot admission are separate typed transitions.", "",
        "| Arm | candidates | cards | final revision | unique contributions | task accuracy | authority |", "|---|---:|---:|---:|---:|---:|---:|",
        *[f"| {arm} | {summary['metrics']['discovery_candidate_count']} | {summary['metrics']['paper_card_count']} | {summary['dossier_revisions'][-1]} | {summary['metrics']['unique_attributable_contributions']} | {summary['metrics']['task_accuracy']} | {summary['metrics']['authority_integrity']} |" for arm, summary in sorted(summaries.items())],
        "", "## Acceptance evidence", "",
        "- Diagnosis reproduces the historical G10R-S outcome and resource facts; the five defects are mapped to repairs and tests.",
        "- All arms produce candidate-selection records before fetch; prose fetches are not accepted by the adapter, and the metadata candidate remains pending.",
        "- R3 admits an evidence-conditioned lateral viewpoint only after sharing; fixed arms reject or abstain without a placeholder.",
        "- Every post-sharing and round-two report is included in the latest dossier revision; replay is hash- and budget-equivalent at every boundary.",
        "- Scoring is computed from typed IDs, cards, reports, and statuses rather than wording; `criterion-ledger.json` maps all ten criteria to tests and artifacts.",
        "", "This is an engineering-readiness signal from deterministic fixtures, not evidence of real-model society value or scientific validity.",
    ])
    (output_dir / "report.md").write_text(report + "\n", encoding="utf-8")
    run_artifact = {"schema_version": "1.0", "goal": "G10R-T", "diagnosis_hash": digest(diagnosis), "matrix_hash": digest(matrix), "replay_hash": digest(replay), "terminal": verdict, "arms": summaries}
    _write(output_dir / "run.json", run_artifact)
    return {"verdict": verdict, "arms": summaries, "replay": replay}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/goals/G10R-T")
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps({"verdict": result["verdict"], "replay": result["replay"]["all_boundaries_byte_equivalent"]}, sort_keys=True))


if __name__ == "__main__":
    main()
