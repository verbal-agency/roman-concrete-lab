"""Offline G10R-R evaluator replay.

This module reads only the recorded G10R run and its checkpoints.  It never
constructs a provider or retrieval adapter, so replay cannot make network or
model calls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.investigation import (
    load_json,
    load_jsonl,
    schema,
    score_portfolio,
    source_identity_map,
)
from tools.tournament.replay import ROOT
from jsonschema import validate


PROTOCOL = "g10r-r.1-open-world-evaluation-remediation"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def replay(
    *,
    run_path: Path = ROOT / "artifacts/goals/G10R/run.json",
    checkpoint_dir: Path = ROOT / "artifacts/goals/G10R/checkpoints",
    phase_path: Path = ROOT / "artifacts/goals/G10R/phase-a.json",
) -> dict[str, Any]:
    run = load_json(run_path)
    phase = load_json(phase_path)
    cases = {item["case_id"]: item for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")}
    identities = source_identity_map()
    score_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    treatment_map: list[dict[str, Any]] = []
    arm_results: dict[str, dict[str, dict[str, Any]]] = {"A1": {}, "A2-M": {}}

    for arm, results in run["arm_results"].items():
        for item in results:
            case_id = item["portfolio"]["case_id"]
            checkpoint_path = checkpoint_dir / f"{case_id}-{arm}.json"
            checkpoint = load_json(checkpoint_path)
            if checkpoint.get("manifest_sha256") != run["manifest_sha256"]:
                raise ValueError(f"checkpoint manifest mismatch: {checkpoint_path}")
            candidate_records = checkpoint.get("source_candidates", {})
            blind_id = "BLIND-" + item["run_id"].split("G10R-", 1)[-1]
            treatment_map.append({"blind_treatment_id": blind_id, "arm": arm, "run_id": item["run_id"]})
            scored = score_portfolio(
                cases[case_id],
                item["portfolio"],
                candidate_records=candidate_records,
                identity_map=identities,
            )
            for source_id, record in sorted(candidate_records.items()):
                candidate_rows.append(
                    {
                        "blind_treatment_id": blind_id,
                        "case_id": case_id,
                        "source_candidate_id": source_id,
                        "title": record.get("title"),
                        "locator": record.get("locator"),
                        "content_locator": record.get("content_locator"),
                        "deduplication_key": record.get("deduplication_key"),
                        "status": record.get("status"),
                        "access_class": record.get("access_class"),
                        "rights_state": record.get("rights_state"),
                        "content_hash": record.get("content_hash"),
                        "identity_status": scored["identity_statuses"].get(source_id, "NOT_CITED"),
                        "attribution_status": scored["attribution_adjudications"].get(source_id, "UNREVIEWED"),
                        "resolved_id": scored["source_identity_aliases"].get(source_id),
                    }
                )
            score_rows.append(
                {
                    "blind_treatment_id": blind_id,
                    "case_id": case_id,
                    "evidence_score": scored["evidence_score"],
                    "discovery_score": scored["discovery_score"],
                    "hypothesis_score": scored["hypothesis_score"],
                    "max_evidence_score": scored["max_score"],
                    "identity_statuses": scored["identity_statuses"],
                    "unresolved_source_candidate_ids": scored["unresolved_source_candidate_ids"],
                    "unattributed_source_candidate_ids": scored["unattributed_source_candidate_ids"],
                    "out_of_rubric_source_candidate_ids": scored["out_of_rubric_source_candidate_ids"],
                    "contradiction_source_candidate_ids": scored["contradiction_source_candidate_ids"],
                    "provenance_review_source_candidate_ids": scored["provenance_review_source_candidate_ids"],
                    "fabrication_proof_source_candidate_ids": scored["fabrication_proof_source_candidate_ids"],
                    "attribution_adjudications": scored["attribution_adjudications"],
                    "authority_flags": scored["authority_flags"],
                    "critical_failures": scored["critical_failures"],
                    "discovery_contribution_digests": scored["discovery_contribution_digests"],
                    "hypothesis_contribution_digests": scored["hypothesis_contribution_digests"],
                    "supported_contribution_digests": scored["supported_contribution_digests"],
                }
            )
            arm_results[arm][case_id] = scored

    by_case = []
    for case_id in sorted(cases):
        a1 = arm_results["A1"][case_id]
        society = arm_results["A2-M"][case_id]
        by_case.append(
            {
                "case_id": case_id,
                "discovery_delta": society["discovery_score"] - a1["discovery_score"],
                "hypothesis_delta": society["hypothesis_score"] - a1["hypothesis_score"],
                "evidence_delta": society["evidence_score"] - a1["evidence_score"],
                "a1_critical_failures": a1["critical_failures"],
                "a2m_critical_failures": society["critical_failures"],
                "a1_discovery_contributions": a1["discovery_contribution_digests"],
                "a2m_discovery_contributions": society["discovery_contribution_digests"],
                "a1_hypothesis_contributions": a1["hypothesis_contribution_digests"],
                "a2m_hypothesis_contributions": society["hypothesis_contribution_digests"],
            }
        )
    critical = sorted(
        {
            failure
            for row in score_rows
            for failure in row["critical_failures"]
        }
    )
    output = {
        "schema_version": "1.0",
        "protocol": PROTOCOL,
        "manifest_sha256": run["manifest_sha256"],
        "status": "INCONCLUSIVE_EVALUATION_ARTIFACT" if critical else "REPLAYABLE_AFTER_REPAIR",
        "treatments": treatment_map,
        "candidate_ledger": candidate_rows,
        "score_ledger": score_rows,
        "decision": {
            "source_run_outcome": run.get("outcome"),
            "critical_failures": critical,
            "per_case": by_case,
            "all_external_calls": False,
            "phase_a_manifest_matches": phase.get("manifest_sha256") == run["manifest_sha256"],
            "interpretation": (
                "The traces are replayable with separated discovery, evidence, hypothesis, and authority dimensions."
                if not critical
                else "The traces are preserved, but one or more attributable policy failures still require adjudication before a society comparison."
            ),
        },
    }
    validate(output, schema("open-world-evaluation-ledger.schema.json"))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=ROOT / "artifacts/goals/G10R/run.json")
    parser.add_argument("--checkpoints", type=Path, default=ROOT / "artifacts/goals/G10R/checkpoints")
    parser.add_argument("--phase", type=Path, default=ROOT / "artifacts/goals/G10R/phase-a.json")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10R-R/replay.json")
    args = parser.parse_args()
    output = replay(run_path=args.run, checkpoint_dir=args.checkpoints, phase_path=args.phase)
    _write(args.output, output)
    print(json.dumps({"status": output["status"], "critical_failures": output["decision"]["critical_failures"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
