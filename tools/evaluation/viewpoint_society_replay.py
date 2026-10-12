"""Offline Phase-A replay for the viewpoint-centered society."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from src.roman_concrete_lab.agents.viewpoint_society import run_offline_fixture
from tools.tournament.replay import ROOT


PROTOCOL = "g10d.1-viewpoint-centered-society"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _summary(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    portfolio = result["portfolio"]
    score = result["score"]
    return {
        "case_id": case["case_id"],
        "status": result["status"],
        "viewpoint_ids": sorted(card["viewpoint_id"] for card in case["viewpoint_cards"] if card["kind"] != "OPEN_SLOT"),
        "support_task_count": len(case["tasks"]),
        "dossier_count": len(portfolio["viewpoint_dossier_ids"]),
        "lateral_discovery": score["support_contribution_count"] > 0,
        "contradiction_or_dissent": score["weakening_contribution_count"] > 0 and score["dissent_retained"],
        "unresolved_candidate_retained": any("unresolved_source_candidate" in diagnostic for diagnostic in result["envelope"]["diagnostics"]),
        "null_retained": result["focus"]["null_retained"],
        "rival_retained": result["focus"]["rival_retained"] and bool(portfolio["credible_rival_ids"]),
        "discriminator_count": score["discriminator_count"],
        "score": score,
        "envelope_status": result["envelope"]["status"],
        "replay_digest": _digest({"portfolio": portfolio, "focus": result["focus"], "score": score}),
    }


def replay(
    *,
    development_path: Path = ROOT / "fixtures/investigation/viewpoint-society/development.jsonl",
    sealed_path: Path = ROOT / "fixtures/investigation/viewpoint-society/sealed.jsonl",
) -> dict[str, Any]:
    development = _load_jsonl(development_path)
    sealed = _load_jsonl(sealed_path)
    results = []
    for case in development + sealed:
        first = run_offline_fixture(case)
        second = run_offline_fixture(case)
        first_digest = _digest({"portfolio": first["portfolio"], "focus": first["focus"], "score": first["score"]})
        second_digest = _digest({"portfolio": second["portfolio"], "focus": second["focus"], "score": second["score"]})
        row = _summary(case, first)
        row["deterministic"] = first_digest == second_digest
        row["fixture_class"] = "development" if case in development else "sealed"
        results.append(row)
    required = {
        "lateral_discovery": all(row["lateral_discovery"] for row in results),
        "contradiction_or_dissent": all(row["contradiction_or_dissent"] for row in results),
        "unresolved_candidate_retained": any(row["unresolved_candidate_retained"] for row in results),
        "null_retained": all(row["null_retained"] for row in results),
        "rival_retained": all(row["rival_retained"] for row in results),
        "deterministic": all(row["deterministic"] for row in results),
        "no_evidence_promotion": all(not row["score"]["evidence_promotion"] for row in results),
        "no_viewpoint_count_credit": all(row["score"]["viewpoint_count_credit"] == 0 for row in results),
        "no_consensus_credit": all(row["score"]["consensus_credit"] == 0 for row in results),
        "no_rhetoric_credit": all(row["score"]["rhetoric_credit"] == 0 for row in results),
    }
    status = "SOCIETY_DESIGN_READY" if all(required.values()) else "SOCIETY_DESIGN_NO_GO"
    output = {
        "schema_version": "1.0",
        "goal": "G10D",
        "protocol": PROTOCOL,
        "status": status,
        "external_calls": False,
        "development_case_count": len(development),
        "sealed_case_count": len(sealed),
        "required_behavior_checks": required,
        "case_summaries": results,
        "authority": {
            "network": "none", "model_calls": "none", "credentials": "none",
            "evidence_promotion": "prohibited", "physical_execution": "prohibited",
            "external_communication": "prohibited",
        },
        "next_gate": "G10R Phase B remains locked until G10D and G10P are complete and a new owner activation is recorded.",
    }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development", type=Path, default=ROOT / "fixtures/investigation/viewpoint-society/development.jsonl")
    parser.add_argument("--sealed", type=Path, default=ROOT / "fixtures/investigation/viewpoint-society/sealed.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10D/phase-a.json")
    args = parser.parse_args()
    output = replay(development_path=args.development, sealed_path=args.sealed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "output": str(args.output), "checks": output["required_behavior_checks"]}, indent=2))


if __name__ == "__main__":
    main()
