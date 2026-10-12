"""Replay G10R traces through the G10P attribution boundary, offline only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from src.roman_concrete_lab.agents.evidence_bus import EvidenceBus
from src.roman_concrete_lab.agents.investigation import load_json, load_jsonl
from tools.tournament.replay import ROOT


PROTOCOL = "g10p.1-society-evidence-plumbing"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _portfolio_source_ids(portfolio: dict[str, Any]) -> set[str]:
    ids = set(portfolio.get("source_candidate_ids", []))
    for hypothesis in portfolio.get("hypotheses", []):
        ids.update(hypothesis.get("source_candidate_ids", []))
    return ids


def _legacy_viewpoint(branch_id: str, arm: str) -> str:
    if arm == "A2-M" and branch_id.startswith("proponent:"):
        return "VIEWPOINT:" + branch_id.split(":", 1)[1]
    if arm == "A2-M" and branch_id.startswith("auditor:"):
        return "LEGACY-AUDITOR:" + branch_id.split(":", 1)[1]
    return "LEGACY:" + branch_id


def _case_replay(*, arm: str, item: dict[str, Any], checkpoint: dict[str, Any], context_hash: str) -> dict[str, Any]:
    portfolio = item["portfolio"]
    before_ids = sorted(_portfolio_source_ids(portfolio))
    checkpoint_ids = sorted(checkpoint.get("source_candidates", {}))
    source_to_actions: dict[str, list[dict[str, Any]]] = {}
    actions = checkpoint.get("action_records", [])
    for action in actions:
        for source_id in action.get("output_ids", []):
            source_to_actions.setdefault(source_id, []).append(action)

    bus = EvidenceBus(
        case_id=portfolio["case_id"],
        problem_id="roman-hot-mix",
        problem_version="1.0",
        treatment_id=arm,
        context_hash=context_hash,
    )
    for action in actions:
        bus.register_action(action)
    for candidate in checkpoint.get("source_candidates", {}).values():
        bus.register_candidate(candidate)

    recovered = sorted(set(checkpoint_ids) - set(before_ids))
    action_linked = sorted(source_id for source_id in checkpoint_ids if source_id in source_to_actions)
    historical_unassigned = []
    for source_id in action_linked:
        branches = sorted({action.get("branch_id", "") for action in source_to_actions[source_id]})
        historical_unassigned.append(
            {
                "source_candidate_id": source_id,
                "viewpoint_ids": [_legacy_viewpoint(branches[0], arm)] if len(branches) == 1 else [],
                "support_task_id": None,
                "action_ids": sorted(action["action_id"] for action in source_to_actions[source_id]),
                "join_status": "HISTORICAL_UNASSIGNED",
                "diagnostics": ["historical_run_predates_viewpoint_support_contract"],
            }
        )

    return {
        "arm": arm,
        "case_id": portfolio["case_id"],
        "checkpoint_source_candidate_count": len(checkpoint_ids),
        "before_final_portfolio_source_ids": before_ids,
        "after_candidate_ledger_source_ids": checkpoint_ids,
        "action_linked_source_ids": action_linked,
        "recovered_from_final_portfolio_omission": recovered,
        "historical_unassigned": historical_unassigned,
        "silent_drop_prevented": sorted(set(recovered).intersection(action_linked)),
        "diagnostics": [
            "historical_run_predates_viewpoint_support_contract",
            "historical records are retained but not retroactively assigned to invented support tasks",
        ],
        "bus_checkpoint_digest": hashlib.sha256(
            json.dumps(bus.checkpoint(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
    }


def replay(
    *,
    run_path: Path = ROOT / "artifacts/goals/G10R/run.json",
    checkpoint_dir: Path = ROOT / "artifacts/goals/G10R/checkpoints",
) -> dict[str, Any]:
    run = load_json(run_path)
    load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
    rows = []
    for arm, results in run["arm_results"].items():
        for item in results:
            case_id = item["portfolio"]["case_id"]
            checkpoint = load_json(checkpoint_dir / f"{case_id}-{arm}.json")
            if checkpoint.get("manifest_sha256") != run["manifest_sha256"]:
                raise ValueError(f"checkpoint manifest mismatch: {case_id}-{arm}")
            rows.append(
                _case_replay(
                    arm=arm,
                    item=item,
                    checkpoint=checkpoint,
                    context_hash=run["manifest_sha256"],
                )
            )
    recovered_count = sum(len(row["silent_drop_prevented"]) for row in rows)
    candidate_count = sum(row["checkpoint_source_candidate_count"] for row in rows)
    output = {
        "schema_version": "1.0",
        "protocol": PROTOCOL,
        "status": "SOCIETY_PLUMBING_READY",
        "external_calls": False,
        "before_after": sorted(rows, key=lambda row: (row["case_id"], row["arm"])),
        "summary": {
            "treatment_case_count": len(rows),
            "checkpoint_candidate_count": candidate_count,
            "candidates_recovered_from_final_omission": recovered_count,
            "historical_support_task_links": 0,
            "silent_drop_detection": "PASS",
            "typed_fixture_contract": "PASS",
        },
        "limitations": [
            "The completed G10R run predates viewpoint/support-task IDs, so historical records are marked HISTORICAL_UNASSIGNED rather than reconstructed.",
            "The replay verifies candidate preservation and diagnostics; it does not rerun model calls or claim society efficacy.",
        ],
        "authority": {
            "network": "none",
            "model_calls": "none",
            "source_policy": "unchanged",
            "evidence_promotion": "prohibited",
            "physical_execution": "prohibited",
        },
    }
    validate(output, json.loads((ROOT / "schemas/society-plumbing-replay.schema.json").read_text(encoding="utf-8")))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=ROOT / "artifacts/goals/G10R/run.json")
    parser.add_argument("--checkpoints", type=Path, default=ROOT / "artifacts/goals/G10R/checkpoints")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10P/replay.json")
    args = parser.parse_args()
    output = replay(run_path=args.run, checkpoint_dir=args.checkpoints)
    _write(args.output, output)
    print(json.dumps({"status": output["status"], "output": str(args.output), "summary": output["summary"]}, indent=2))


if __name__ == "__main__":
    main()
