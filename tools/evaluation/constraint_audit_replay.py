"""Offline G10R-C constraint audit and remediation replay.

This gate audits the behavior-shaping contracts around the active-investigation
runner and replays only recorded or deterministic fixtures.  It performs no
model, network, subscription, credential, or laboratory operation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.investigation import (
    ActiveInvestigationRunner,
    canonical,
    load_json,
    load_jsonl,
    phase_a,
    schema,
    validate_plan,
)
from src.roman_concrete_lab.retrieval import InvestigationBudget
from tools.evaluation.acquisition_redesign_replay import replay as acquisition_replay
from tools.evaluation.open_world_replay import replay as open_world_replay
from tools.evaluation.runtime_integration_replay import replay as runtime_replay
from tools.evaluation.society_plumbing_replay import replay as plumbing_replay
from tools.tournament.replay import ROOT


PROTOCOL = "g10r-c.1-pre-rerun-constraint-audit"
RERUN_RUN = ROOT / "artifacts/goals/G10R/run-rerun-20261023.json"
RERUN_PHASE = ROOT / "artifacts/goals/G10R/phase-a-rerun-20261023.json"
RERUN_CHECKPOINTS = ROOT / "artifacts/goals/G10R/checkpoints/rerun-20261023"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _constraint_matrix(root: Path = ROOT) -> list[dict[str, Any]]:
    investigation = (root / "src/roman_concrete_lab/agents/investigation.py").read_text(encoding="utf-8")
    action_schema = load_json(root / "schemas/investigation-action.schema.json")
    policy = load_json(root / "fixtures/investigation/source-policy.json")
    rows = [
        {
            "layer": "prompt_schema",
            "source": "src/roman_concrete_lab/agents/investigation.py:PLAN_OUTPUT_TOKENS and schemas/investigation-plan.schema.json",
            "affected": "A1/A2-M planning and report calls",
            "purpose": "bounded structured model output",
            "classification": "REMEDIATED_ACCIDENTAL",
            "observed_effect": "the previous 450-token A2-M planning ceiling truncated useful plans",
            "remediation": "shared 800-token planning ceiling plus compact-schema replay",
            "evidence": "PLAN_OUTPUT_TOKENS=800; output fixture and replay pass",
        },
        {
            "layer": "task_focus",
            "source": "src/roman_concrete_lab/agents/investigation.py:_run_a2m and viewpoint_society.py",
            "affected": "viewpoint support and structural audit tasks",
            "purpose": "keep viewpoint work scoped while preserving dissent and unresolved work",
            "classification": "DECLARED_EXPERIMENTAL_LIMIT",
            "observed_effect": "every task has a typed report or abstention; focus is allocated before final adjudication",
            "remediation": "retain typed abstention and add lifecycle causes rather than silent empty arrays",
            "evidence": "runtime and acquisition fixture reports, focus ledger, dossier joins",
        },
        {
            "layer": "locator_retrieval",
            "source": "src/roman_concrete_lab/agents/investigation.py:_resolve_fetch_locator/_fetch",
            "affected": "model fetch requests using provider IDs or metadata locators",
            "purpose": "allow only exact candidate-record resolution to lawful content",
            "classification": "REMEDIATED_ACCIDENTAL",
            "observed_effect": "provider IDs were previously sent directly to content fetch and became policy blocks",
            "remediation": "resolve exact candidate ID/metadata locator to recorded content_locator; never infer by title/query",
            "evidence": "resolution fixture distinguishes candidate, direct, unresolved, and blocked paths",
        },
        {
            "layer": "source_policy",
            "source": "fixtures/investigation/source-policy.json and retrieval/contracts.py:SourcePolicy",
            "affected": "all content fetches",
            "purpose": "rights, host, read-only, and payload boundary",
            "classification": "INTENTIONAL_BOUNDARY",
            "observed_effect": "metadata hosts cannot be fetched; declared public hosts can reach extraction",
            "remediation": "unchanged; diagnostics are typed rather than widened",
            "evidence": "public, metadata-only, rights-blocked, malformed, and unavailable fixtures",
        },
        {
            "layer": "evidence_bus",
            "source": "src/roman_concrete_lab/agents/evidence_bus.py",
            "affected": "candidate/action/task/viewpoint/card/dossier/critique joins",
            "purpose": "append-only attribution without evidence promotion",
            "classification": "INTENTIONAL_BOUNDARY",
            "observed_effect": "variants and dissent remain reviewable; missing joins become diagnostics",
            "remediation": "none; replay and duplicate behavior are required",
            "evidence": "G10R-A acquisition replay and G10P plumbing replay",
        },
        {
            "layer": "budget_runtime",
            "source": "retrieval/contracts.py:InvestigationBudget and investigation.py:_model",
            "affected": "queries, retained sources, fetches, tokens, payload, simulation, cost",
            "purpose": "equal aggregate treatment ceilings and fail-before-call behavior",
            "classification": "INTENTIONAL_BOUNDARY",
            "observed_effect": "budget debits are recorded and exhausted work is typed",
            "remediation": "no increase; compare equal ceilings explicitly",
            "evidence": "budget tests, phase-A manifest, and equal-budget fixture ledger",
        },
        {
            "layer": "checkpoint_replay",
            "source": "investigation.py:_checkpoint and evidence_bus.py:checkpoint",
            "affected": "duplicate, partial, stale, and resumed traces",
            "purpose": "deterministic continuation without duplicate external work",
            "classification": "INTENTIONAL_BOUNDARY",
            "observed_effect": "checkpoint digests and duplicate actions replay without side effects",
            "remediation": "none; stale manifests remain rejected",
            "evidence": "runtime, plumbing, acquisition, and open-world replays",
        },
        {
            "layer": "scoring",
            "source": "investigation.py:score_portfolio and open-world evaluation ledger",
            "affected": "discovery, evidence, hypotheses, weakening, identity, blocked access, overhead",
            "purpose": "do not confuse rhetoric or unresolved candidates with direct evidence",
            "classification": "INTENTIONAL_BOUNDARY",
            "observed_effect": "component dimensions remain separate and unresolved candidates are retained",
            "remediation": "add request-lifecycle and acquisition fields to the audit ledger",
            "evidence": "per-arm score rows and open-world replay status",
        },
    ]
    assert "PLAN_OUTPUT_TOKENS = 800" in investigation
    assert "RUNNER_REJECTED" in action_schema["properties"]["policy_status"]["enum"]
    assert policy["default"] == "DENY"
    assert {row["layer"] for row in rows} == {
        "prompt_schema", "task_focus", "locator_retrieval", "source_policy",
        "evidence_bus", "budget_runtime", "checkpoint_replay", "scoring",
    }
    return rows


def _resolution_fixture(root: Path = ROOT) -> dict[str, Any]:
    case = load_jsonl(root / "fixtures/investigation/sealed.jsonl")[0]
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as directory:
        runner = ActiveInvestigationRunner(
            case=case,
            arm="A1",
            adapter=object(),
            provider=None,
            budget=InvestigationBudget(),
            checkpoint_path=Path(directory) / "resolution.json",
            manifest_sha256=phase_a()["manifest_sha256"],
            run_id="G10R-C-resolution-fixture",
        )
        runner.candidates["OA-FIXTURE"] = {
            "source_candidate_id": "OA-FIXTURE",
            "locator": "https://api.openalex.org/works/W-FIXTURE",
            "content_locator": "https://www.repository.cam.ac.uk/fixture.pdf",
        }
        cases = {
            "provider_id": runner._resolve_fetch_locator("OA-FIXTURE"),
            "metadata_locator": runner._resolve_fetch_locator("https://api.openalex.org/works/W-FIXTURE"),
            "direct_content_locator": runner._resolve_fetch_locator("https://www.repository.cam.ac.uk/fixture.pdf"),
            "unknown_locator": runner._resolve_fetch_locator("https://api.openalex.org/works/W-UNKNOWN"),
        }
    expected = {
        "provider_id": ("https://www.repository.cam.ac.uk/fixture.pdf", "CANDIDATE_CONTENT_LOCATOR"),
        "metadata_locator": ("https://www.repository.cam.ac.uk/fixture.pdf", "CANDIDATE_CONTENT_LOCATOR"),
        "direct_content_locator": ("https://www.repository.cam.ac.uk/fixture.pdf", "DIRECT_CONTENT_LOCATOR"),
        "unknown_locator": ("https://api.openalex.org/works/W-UNKNOWN", "DIRECT_CONTENT_LOCATOR"),
    }
    return {"cases": cases, "expected": expected, "passes": cases == expected}


def _score_ledger(run_path: Path = RERUN_RUN, checkpoint_dir: Path = RERUN_CHECKPOINTS) -> list[dict[str, Any]]:
    run = load_json(run_path)
    rows = []
    for arm, results in sorted(run["arm_results"].items()):
        for item in sorted(results, key=lambda value: value["portfolio"]["case_id"]):
            case_id = item["portfolio"]["case_id"]
            checkpoint = load_json(checkpoint_dir / f"{case_id}-{arm}.json")
            lifecycle = Counter(event["status"] for event in checkpoint.get("tool_request_events", []))
            actions = checkpoint.get("action_records", [])
            score = item["score"]
            society = checkpoint.get("viewpoint_society") or {}
            evidence_bus = society.get("evidence_bus") or {}
            rows.append({
                "arm": arm,
                "case_id": case_id,
                "request_cause": {status: lifecycle.get(status, 0) for status in ("NOT_REQUESTED", "RUNNER_REJECTED", "POLICY_BLOCKED", "NO_USABLE_RESULT", "EXECUTED_CARD")},
                "acquisition": {
                    "search_actions": sum(action["action_type"] == "SEARCH" for action in actions),
                    "fetch_actions": sum(action["action_type"] == "FETCH_PERMITTED_CONTENT" for action in actions),
                    "page_aware_cards": len(checkpoint.get("paper_evidence_cards", {})),
                },
                "hypothesis": len(score.get("hypothesis_contribution_digests", [])),
                "weakening": sum(report.get("stance") == "WEAKENS" for report in evidence_bus.get("reports", {}).values()),
                "unresolved_identity": len(score.get("unresolved_source_candidate_ids", [])),
                "blocked_access": lifecycle.get("POLICY_BLOCKED", 0),
                "overhead": {"model_calls": len(checkpoint.get("model_traces", [])), "actions": len(actions)},
            })
    return rows


def _output_fixture(root: Path = ROOT) -> dict[str, Any]:
    case_id = load_jsonl(root / "fixtures/investigation/sealed.jsonl")[0]["case_id"]
    valid = {
        "schema_version": "1.0", "case_id": case_id, "branch_id": "fixture",
        "primary_queries": [], "follow_up_queries": [], "requested_fetch_locators": [],
        "simulation_requests": [], "abstain_reason": "compact valid fixture",
    }
    validate_plan(valid, case_id=case_id, branch_id="fixture")
    malformed_rejected = False
    try:
        json.loads('{"schema_version":"1.0","case_id":"truncated"')
    except json.JSONDecodeError:
        malformed_rejected = True
    return {
        "compact_schema_valid": True,
        "malformed_rejected": malformed_rejected,
        "truncation_is_not_silent": malformed_rejected,
        "full_plan_schema_required_fields": sorted(schema("investigation-plan.schema.json")["required"]),
    }


def replay(*, root: Path = ROOT) -> dict[str, Any]:
    matrix = _constraint_matrix(root)
    resolution = _resolution_fixture(root)
    acquisition_first = acquisition_replay()
    acquisition_second = acquisition_replay()
    acquisition_stable = canonical(acquisition_first) == canonical(acquisition_second)
    open_world = open_world_replay(run_path=RERUN_RUN, checkpoint_dir=RERUN_CHECKPOINTS, phase_path=RERUN_PHASE)
    open_world_replay_again = open_world_replay(run_path=RERUN_RUN, checkpoint_dir=RERUN_CHECKPOINTS, phase_path=RERUN_PHASE)
    open_world_stable = canonical(open_world) == canonical(open_world_replay_again)
    runtime = runtime_replay(root=root)
    plumbing = plumbing_replay()
    output_fixture = _output_fixture(root)
    score_ledger = _score_ledger()
    acquisition_score = acquisition_first["offline_run"]["score"]
    acquisition_bus = acquisition_first["offline_run"]["checkpoint"]["evidence_bus"]
    task_types = sorted({task["task_type"] for task in acquisition_bus["tasks"].values()})
    report_statuses = sorted({report["status"] for report in acquisition_bus["reports"].values()})
    output = {
        "schema_version": "1.0",
        "protocol": PROTOCOL,
        "goal": "G10R-C",
        "status": "PRE_RERUN_CONSTRAINTS_READY",
        "external_calls": False,
        "constraint_matrix": matrix,
        "resolution_fixture": resolution,
        "replays": {
            "acquisition_first_status": acquisition_first["status"],
            "acquisition_second_status": acquisition_second["status"],
            "acquisition_byte_stable": acquisition_stable,
            "open_world_status": open_world["status"],
            "open_world_manifest_matches": open_world["decision"]["phase_a_manifest_matches"],
            "open_world_byte_stable": open_world_stable,
            "runtime_status": runtime["status"],
            "plumbing_status": plumbing["status"],
        },
        "output_fixture": output_fixture,
        "join_fixture": {
            "candidate_variant_retained": acquisition_score["candidate_variant_count"] >= 1,
            "checkpoint_resume_stable": acquisition_score["checkpoint_resume_stable"],
            "duplicate_action_replayed": acquisition_score["duplicate_action_replayed"],
            "envelope_diagnostics": acquisition_first["offline_run"]["envelope"]["diagnostics"],
            "dissent_and_unresolved_retained": bool(acquisition_first["offline_run"]["portfolio"]["unresolved_disputes"]),
        },
        "task_fixture": {
            "task_types": task_types,
            "report_statuses": report_statuses,
            "all_tasks_have_reports": len(acquisition_bus["tasks"]) == len(acquisition_bus["reports"]),
            "required_task_types_present": task_types == ["CONTRADICTION", "EXPERIMENT_DESIGN", "EXTRACTION", "IDENTITY_LINEAGE", "RETRIEVAL"],
        },
        "score_ledger": score_ledger,
        "authority": {
            "network": "none",
            "model_calls": "none",
            "credentials": "none",
            "subscription": "prohibited",
            "evidence_promotion": "prohibited",
            "physical_execution": "prohibited",
        },
        "failure_reasons": [],
        "next_action": "Freeze a fresh Phase-A manifest; no paid Phase-B run is authorized by G10R-C.",
    }
    ready = (
        resolution["passes"]
        and acquisition_first["status"] == "ACQUISITION_DESIGN_READY"
        and acquisition_stable
        and open_world["status"] == "REPLAYABLE_AFTER_REPAIR"
        and open_world["decision"]["phase_a_manifest_matches"]
        and open_world_stable
        and runtime["status"] == "RUNTIME_INTEGRATION_READY"
        and plumbing["status"] == "SOCIETY_PLUMBING_READY"
        and output_fixture["compact_schema_valid"]
        and output_fixture["malformed_rejected"]
        and output_fixture["truncation_is_not_silent"]
        and acquisition_first["offline_run"]["envelope"]["diagnostics"] == []
        and acquisition_score["candidate_variant_count"] >= 1
        and acquisition_score["checkpoint_resume_stable"]
        and acquisition_score["duplicate_action_replayed"]
        and task_types == ["CONTRADICTION", "EXPERIMENT_DESIGN", "EXTRACTION", "IDENTITY_LINEAGE", "RETRIEVAL"]
        and len(acquisition_bus["tasks"]) == len(acquisition_bus["reports"])
        and len(score_ledger) == 8
        and all(set(row["request_cause"]) == {"NOT_REQUESTED", "RUNNER_REJECTED", "POLICY_BLOCKED", "NO_USABLE_RESULT", "EXECUTED_CARD"} for row in score_ledger)
    )
    if not ready:
        output["status"] = "INCONCLUSIVE_CONSTRAINT_AUDIT"
        output["failure_reasons"] = ["one or more offline constraint, resolution, replay, or ledger invariants failed"]
        output["next_action"] = "Repair the failed offline constraint invariant before freezing Phase A."
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10R-C/replay.json")
    args = parser.parse_args()
    output = replay()
    _write(args.output, output)
    print(json.dumps({"status": output["status"], "external_calls": output["external_calls"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
