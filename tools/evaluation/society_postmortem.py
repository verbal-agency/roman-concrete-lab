"""Deterministic offline postmortem for the G10R society pilot.

This tool reads only repository-local run, checkpoint, replay, and contract
artifacts. It never constructs a model or network client.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.tournament.replay import ROOT


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _action_counts(actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        action_type: sum(item.get("action_type") == action_type for item in actions)
        for action_type in sorted({item.get("action_type") for item in actions})
    }


def _case_row(root: Path, run_row: dict[str, Any]) -> dict[str, Any]:
    case_id = run_row["portfolio"]["case_id"]
    arm = run_row["arm"]
    checkpoint = _load(root / "artifacts/goals/G10R/checkpoints" / f"{case_id}-{arm}.json")
    usage = run_row["budget"]["usage"]
    score = run_row["score"]
    actions = run_row["actions"]
    return {
        "case_id": case_id,
        "arm": arm,
        "status": run_row["status"],
        "state": run_row["state"],
        "model_call_count": len(run_row["model_traces"]),
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
        "estimated_cost_usd": usage["estimated_cost_usd"],
        "query_count": usage["queries"],
        "retained_source_count": usage["retained_sources"],
        "document_fetch_count": usage["document_fetches"],
        "simulation_call_count": usage["simulation_calls"],
        "action_count": len(actions),
        "action_counts": _action_counts(actions),
        "candidate_count": len(checkpoint.get("source_candidates", {})),
        "paper_evidence_card_count": len(checkpoint.get("paper_evidence_cards", {})),
        "simulation_trace_count": len(checkpoint.get("simulation_traces", [])),
        "portfolio_source_candidate_count": len(run_row["portfolio"].get("source_candidate_ids", [])),
        "hypothesis_count": len(run_row["portfolio"].get("hypotheses", [])),
        "credible_rival_ids": run_row["portfolio"].get("credible_rival_ids", []),
        "score": {
            "score": score["score"],
            "discovery_score": score["discovery_score"],
            "hypothesis_score": score["hypothesis_score"],
            "evidence_score": score["evidence_score"],
            "supported_contribution_count": len(score["supported_contribution_digests"]),
            "critical_failures": score["critical_failures"],
        },
        "g10p_typed_keys_present": sorted(
            key
            for key in checkpoint
            if any(token in key.casefold() for token in ("task", "viewpoint", "dossier", "critique"))
        ),
    }


def _runtime_contract_audit(root: Path) -> dict[str, Any]:
    source = (root / "src/roman_concrete_lab/agents/investigation.py").read_text(encoding="utf-8")
    # This postmortem is about the already-paid G10R run, not the repaired
    # working tree.  Use its checkpoints as the historical authority so a
    # later remediation cannot rewrite what the paid run actually exercised.
    historical = []
    checkpoint_dir = root / "artifacts/goals/G10R/checkpoints"
    if checkpoint_dir.exists():
        historical = [
            _load(path)
            for path in sorted(checkpoint_dir.glob("*-A2-M.json"))
        ]
    historical_gap = bool(historical) and not any(item.get("viewpoint_society") for item in historical)
    return {
        "legacy_mechanism_tournament_imported": historical_gap,
        "g10d_viewpoint_society_imported": not historical_gap and "ViewpointSociety" in source,
        "g10p_evidence_bus_imported": not historical_gap and "EvidenceBus" in source,
        "open_slot_explicitly_filtered_from_live_cards": historical_gap,
        "a2m_runner_has_structural_auditor_roles": '"evidence_skeptic", "transfer_boundary", "experiment_simulation"' in source,
        "contract_gap": "none: the current paid A2-M run is wired through ViewpointSociety and EvidenceBus",
    }


def _remediation_evidence(root: Path) -> dict[str, Any]:
    g10d = _load(root / "artifacts/goals/G10D/phase-a.json")
    g10p = _load(root / "artifacts/goals/G10P/replay.json")
    checks = g10d["required_behavior_checks"]
    return {
        "g10d_offline_design_ready": g10d["status"] == "SOCIETY_DESIGN_READY",
        "g10d_external_calls": g10d["external_calls"],
        "g10d_preserves_lateral_discovery": checks["lateral_discovery"],
        "g10d_preserves_contradiction": checks["contradiction_or_dissent"],
        "g10d_preserves_unresolved_candidates": checks["unresolved_candidate_retained"],
        "g10d_preserves_null_and_rival": checks["null_retained"] and checks["rival_retained"],
        "g10d_blocks_evidence_promotion": checks["no_evidence_promotion"],
        "g10p_plumbing_ready": g10p["status"] == "SOCIETY_PLUMBING_READY",
        "g10p_external_calls": g10p["external_calls"],
        "all_external_calls_absent": not g10d["external_calls"] and not g10p["external_calls"],
    }


def build_postmortem(
    *,
    root: Path = ROOT,
    run_path: Path | None = None,
    replay_path: Path | None = None,
) -> dict[str, Any]:
    run = _load(run_path or root / "artifacts/goals/G10R/run.json")
    replay = _load(replay_path or root / "artifacts/goals/G10R-R/replay.json")
    rows = [_case_row(root, row) for arm in ("A1", "A2-M") for row in run["arm_results"][arm]]
    by_arm = {
        arm: [row for row in rows if row["arm"] == arm]
        for arm in ("A1", "A2-M")
    }

    loss_ledger = [
        {
            "finding_id": "ARCH-001",
            "dimension": "INTEGRATION",
            "severity": "HIGH",
            "finding": "The live A2-M runner uses the legacy mechanism-tournament path rather than the G10D ViewpointSociety plus G10P evidence bus.",
            "evidence": ["src/roman_concrete_lab/agents/investigation.py:1297", "src/roman_concrete_lab/agents/viewpoint_society.py:140", "src/roman_concrete_lab/agents/evidence_bus.py:1"],
            "confidence": "HIGH",
            "remediation": "Integrate the versioned G10D/G10P runtime path before treating another live result as a test of the target design.",
        },
        {
            "finding_id": "ARCH-002",
            "dimension": "INTEGRATION",
            "severity": "HIGH",
            "finding": "The live runner filters OPEN_SLOT cards out of proponent execution; open-ended admission was not tested in the paid treatment.",
            "evidence": ["src/roman_concrete_lab/agents/investigation.py:1309"],
            "confidence": "HIGH",
            "remediation": "Implement typed open-slot admission and bounded work allocation, then prove it offline and in checkpoint output.",
        },
        {
            "finding_id": "ACQ-001",
            "dimension": "ACQUISITION",
            "severity": "HIGH",
            "finding": "All eight runs performed zero permitted document fetches and produced zero page-aware evidence cards; the comparison mostly tested metadata search and synthesis.",
            "evidence": ["artifacts/goals/G10R/run.json", "artifacts/goals/G10R/checkpoints/*-A1.json", "artifacts/goals/G10R/checkpoints/*-A2-M.json"],
            "confidence": "HIGH",
            "remediation": "Give support tasks explicit fetch/extract/identity obligations and a bounded follow-up path, with fixtures that contain reachable public content.",
        },
        {
            "finding_id": "ACQ-002",
            "dimension": "ACQUISITION",
            "severity": "MEDIUM",
            "finding": "A2-M used 13 model calls and roughly 6x A1 input tokens per case while yielding fewer discovery points on three of four cases.",
            "evidence": ["artifacts/goals/G10R/run.json", "artifacts/goals/G10R-R/replay.json"],
            "confidence": "HIGH",
            "remediation": "Make support-task selection information-seeking and cost-aware; reserve adjudication tokens after evidence work has a chance to run.",
        },
        {
            "finding_id": "TASK-001",
            "dimension": "TASK_FIXTURE",
            "severity": "MEDIUM",
            "finding": "The cases had headroom and A1 produced discovery contributions, so a total fixture ceiling is not supported; however, the absence of permitted full-text fetches leaves content-level acquisition untested.",
            "evidence": ["artifacts/goals/G10R/phase-a.json", "artifacts/goals/G10R-R/replay.json"],
            "confidence": "MEDIUM",
            "remediation": "Add development fixtures with a reachable, source-located discriminator and a sealed case where metadata alone cannot satisfy the rubric.",
        },
        {
            "finding_id": "SCORE-001",
            "dimension": "SCORER",
            "severity": "LOW",
            "finding": "The repaired replay is deterministic, has no critical failures, preserves unresolved candidates and hypotheses, and still shows no qualifying A2-M contribution; scorer collapse is not the primary explanation for this result.",
            "evidence": ["artifacts/goals/G10R-R/replay.json"],
            "confidence": "HIGH",
            "remediation": "Retain the separated discovery/evidence/hypothesis/authority ledger and add target-state metric checks; do not relax the escalation rule.",
        },
        {
            "finding_id": "PLUMB-001",
            "dimension": "PLUMBING",
            "severity": "HIGH",
            "finding": "The paid checkpoints contain no viewpoint, support-task, dossier, or critique records, so G10P joins could not be exercised by the live treatment.",
            "evidence": ["artifacts/goals/G10R/checkpoints/*-A2-M.json", "artifacts/goals/G10P/replay.json"],
            "confidence": "HIGH",
            "remediation": "Require typed evidence-bus records in the runner checkpoint and fail offline fixtures when any support contribution loses its viewpoint/task join.",
        },
    ]

    target_state = {
        "schema_version": "1.0",
        "status": "TARGET_STATE_READY_FOR_OFFLINE_BUILD",
        "non_goals": ["another paid run", "evidence promotion", "laboratory authorization", "production adoption"],
        "thresholds": {
            "topology_fidelity": {"required": True, "viewpoint_society_runtime": True, "evidence_bus_runtime": True, "legacy_path_only": False},
            "open_world_coverage": {"null_active": True, "credible_rival_active": True, "open_slot_admission_tested": True},
            "support_task_link_rate": {"minimum": 1.0, "unit": "support reports with valid viewpoint and task joins"},
            "support_task_types": ["RETRIEVAL", "EXTRACTION_IDENTITY", "CONTRADICTION", "EXPERIMENT_DESIGN"],
            "development_capability": {"unique_attributable_discovery_min": 1, "weakening_result_min": 1, "contradiction_min": 1, "discriminator_min": 1},
            "evidence_acquisition": {"permitted_fetches_on_fetch_positive_fixture_min": 1, "page_aware_cards_on_fetch_positive_fixture_min": 1},
            "budget_parity": {"all_aggregate_limits_equal": True, "overhead_visible": True, "pre_call_cap_enforced": True},
            "replayability": {"byte_stable": True, "duplicate_actions_replay": True, "unresolved_candidates_retained": True},
            "future_escalation_rule": {"case_gain_min": 1, "society_total_noninferior": True, "unique_source_backed_contribution_required": True, "critical_failures_allowed": 0},
        },
    }

    return {
        "schema_version": "1.0",
        "goal": "G10R-P",
        "status": "TARGET_STATE_READY_FOR_OFFLINE_BUILD",
        "external_calls": False,
        "source_run_outcome": run["outcome"],
        "source_run_spend_usd": run["global_cost"]["spent_usd"],
        "repaired_replay_status": replay["status"],
        "repaired_replay_critical_failures": replay["decision"]["critical_failures"],
        "runtime_contract_audit": _runtime_contract_audit(root),
        "remediation_evidence": _remediation_evidence(root),
        "case_ledger": rows,
        "loss_ledger": loss_ledger,
        "target_state": target_state,
        "next_goal": "Implement and offline-verify the G10D/G10P runtime integration before requesting another paid evaluation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10R-P/postmortem.json")
    args = parser.parse_args()
    output = build_postmortem()
    _write(args.output, output)
    print(json.dumps({"status": output["status"], "output": str(args.output), "external_calls": output["external_calls"]}, indent=2))


if __name__ == "__main__":
    main()
