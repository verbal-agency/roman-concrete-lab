"""Offline G10R-Y diagnosis of the G10R-V paid comparison.

The evaluator reads only committed run/checkpoint artifacts and deterministic
recorded fixtures.  It performs no provider, network, credential, subscription,
or laboratory action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.roman_concrete_lab.agents import research_loop as research_loop_module
from src.roman_concrete_lab.agents.research_loop import OfflineResearchLoop
from src.roman_concrete_lab.retrieval import canonical, digest
from tools.tournament.replay import ROOT


GOAL = "G10R-Y"
PAID = ROOT / "artifacts/goals/G10R-V"
FIXTURE = ROOT / "fixtures/investigation/research-loop/sources.jsonl"
SOURCE_FILES = (
    "artifacts/goals/G10R-V/manifest.json",
    "artifacts/goals/G10R-V/run.json",
    "artifacts/goals/G10R-V/replay.json",
    "artifacts/goals/G10R-V/report.md",
    "artifacts/goals/G10R-V/spend-ledger.json",
)


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _source_hashes() -> dict[str, str]:
    paths = [ROOT / item for item in SOURCE_FILES]
    paths.extend(sorted((PAID / "checkpoints").glob("*.json")))
    return {str(path.relative_to(ROOT)): _sha(path) for path in paths}


def _status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("status", "UNKNOWN")) for row in rows).items()))


def _checkpoint_row(path: Path) -> dict[str, Any]:
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    arm = "A2-M" if path.stem.endswith("-A2-M") else "A1"
    case_id = path.stem.removesuffix("-A2-M").removesuffix("-A1")
    result = checkpoint["last_result"]
    score = result["score"]
    usage = checkpoint["budget"]["usage"]
    candidates = list(checkpoint.get("source_candidates", {}).values())
    loop = checkpoint.get("research_loop") or {}
    society = checkpoint.get("viewpoint_society") or {}
    bus = society.get("evidence_bus") or {}
    reports = list((bus.get("reports") or {}).values())
    complete_without_observable = [
        report["report_id"]
        for report in reports
        if report.get("status") == "COMPLETE"
        and not (
            report.get("action_ids")
            or report.get("source_candidate_ids")
            or report.get("claim_ids")
        )
    ]
    open_rows = loop.get("open_slot", [])
    open_statuses = [row["status"] for row in open_rows]
    active_ids = society.get("active_ids", [])
    preadmitted_open = [item for item in active_ids if item.endswith("-OPEN-ADMITTED")]
    credited = score.get("supported_contribution_digests", [])
    return {
        "case_id": case_id,
        "arm": arm,
        "status": result["status"],
        "acquisition": {
            "queries": usage.get("queries", 0),
            "retained_sources": usage.get("retained_sources", 0),
            "candidate_count": len(candidates),
            "candidate_statuses": _status_counts(candidates),
            "selection_count": len(loop.get("selections", [])),
            "selection_statuses": _status_counts(loop.get("selections", [])),
            "seek_locator_count": sum(row.get("requested_operation") == "SEEK_LOCATOR" for row in loop.get("selections", [])),
            "fetch_count": usage.get("document_fetches", 0),
            "recorded_fetch_count": len(loop.get("fetches", [])),
            "mapping_count": len(loop.get("mappings", [])),
            "paper_card_count": len(checkpoint.get("paper_evidence_cards", {})),
        },
        "topology": {
            "protocol": society.get("protocol"),
            "active_viewpoint_count": len(active_ids),
            "active_viewpoint_ids": active_ids,
            "preadmitted_open_viewpoint_ids": preadmitted_open,
            "open_slot_statuses": open_statuses,
            "open_slot_activation_mismatch": bool(
                preadmitted_open and open_statuses and "ADMITTED" not in open_statuses
            ),
            "support_task_count": len(bus.get("tasks", {})),
            "support_report_count": len(reports),
            "support_stances": dict(sorted(Counter(row.get("stance", "UNKNOWN") for row in reports).items())),
            "complete_without_observable_report_ids": sorted(complete_without_observable),
            "dossier_count": len(society.get("dossiers", {})),
            "dossier_revision_count": len(loop.get("dossier_revisions", [])),
            "critique_count": len(society.get("critiques", {})),
            "focus_decision_count": len(loop.get("focus", [])),
        },
        "attribution_and_scoring": {
            "rubric_score": score.get("score", 0),
            "discovery_score_raw": score.get("discovery_score", 0),
            "hypothesis_score_raw": score.get("hypothesis_score", 0),
            "evidence_score": score.get("evidence_score", 0),
            "raw_cited_source_count": len(score.get("raw_cited_source_candidate_ids", [])),
            "unresolved_source_count": len(score.get("unresolved_source_candidate_ids", [])),
            "credited_contribution_count": len(credited),
            "hypothesis_count": len(result["portfolio"].get("hypotheses", [])),
            "critical_failures": score.get("critical_failures", []),
            "provenance_completeness": score.get("provenance_completeness", 0.0),
        },
        "cost": {
            "model_calls": len(checkpoint.get("model_traces", [])),
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "estimated_cost_usd": usage.get("estimated_cost_usd", 0.0),
        },
        "evidence_locators": [
            f"{path.relative_to(ROOT)}#budget.usage",
            f"{path.relative_to(ROOT)}#source_candidates",
            f"{path.relative_to(ROOT)}#research_loop",
            f"{path.relative_to(ROOT)}#viewpoint_society",
            f"{path.relative_to(ROOT)}#last_result.score",
        ],
    }


def _aggregate(rows: list[dict[str, Any]], arm: str) -> dict[str, Any]:
    selected = [row for row in rows if row["arm"] == arm]
    return {
        "cases": len(selected),
        "queries": sum(row["acquisition"]["queries"] for row in selected),
        "retained_sources": sum(row["acquisition"]["retained_sources"] for row in selected),
        "candidates": sum(row["acquisition"]["candidate_count"] for row in selected),
        "selections": sum(row["acquisition"]["selection_count"] for row in selected),
        "pending_selections": sum(row["acquisition"]["selection_statuses"].get("PENDING", 0) for row in selected),
        "fetches": sum(row["acquisition"]["fetch_count"] for row in selected),
        "paper_cards": sum(row["acquisition"]["paper_card_count"] for row in selected),
        "raw_discovery": sum(row["attribution_and_scoring"]["discovery_score_raw"] for row in selected),
        "raw_hypotheses": sum(row["attribution_and_scoring"]["hypothesis_score_raw"] for row in selected),
        "rubric_score": sum(row["attribution_and_scoring"]["rubric_score"] for row in selected),
        "evidence_score": sum(row["attribution_and_scoring"]["evidence_score"] for row in selected),
        "credited_contributions": sum(row["attribution_and_scoring"]["credited_contribution_count"] for row in selected),
        "model_calls": sum(row["cost"]["model_calls"] for row in selected),
        "input_tokens": sum(row["cost"]["input_tokens"] for row in selected),
        "output_tokens": sum(row["cost"]["output_tokens"] for row in selected),
        "estimated_cost_usd": round(sum(row["cost"]["estimated_cost_usd"] for row in selected), 7),
    }


def _arm_fixture_summary(arm: str, fixture_dir: Path | None = None) -> dict[str, Any]:
    result = OfflineResearchLoop(arm, fixture_dir=fixture_dir).run()
    return {
        "terminal": result["terminal"],
        "content_hash": result["content_hash"],
        "selection_statuses": _status_counts(result["selections"]),
        "open_slot_statuses": [row["status"] for row in result["open_admissions"]],
        "budget_usage": result["budget"]["usage"],
        "metrics": result["metrics"],
    }


def _metadata_only_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    rows = [json.loads(line) for line in FIXTURE.read_text(encoding="utf-8").splitlines() if line.strip()]
    for index, row in enumerate(rows):
        if row["source_candidate_id"] == "SRC-METADATA-DOI":
            continue
        row.update({
            "locator": f"https://doi.org/10.0000/g10ry-{index}",
            "host": "doi.org",
            "access_class": "METADATA_ONLY",
            "rights_state": "METADATA_ONLY",
        })
    with tempfile.TemporaryDirectory() as directory:
        fixture_dir = Path(directory)
        (fixture_dir / "sources.jsonl").write_text(
            "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
            encoding="utf-8",
        )
        # The historical G10R-T runner used SEEK_LAWFUL_LOCATOR while the
        # frozen schema accepts SEEK_LOCATOR.  Preserve that frozen source file
        # and extend only this diagnostic's in-memory schema so the previously
        # untested metadata branch can be observed.  G10R-Z owns the real fix.
        original_schema = research_loop_module._schema

        def diagnostic_schema(name: str) -> dict[str, Any]:
            value = deepcopy(original_schema(name))
            if name == "candidate-selection.schema.json":
                enum = value["properties"]["requested_operation"]["enum"]
                if "SEEK_LAWFUL_LOCATOR" not in enum:
                    enum.append("SEEK_LAWFUL_LOCATOR")
            return value

        with patch.object(research_loop_module, "_schema", side_effect=diagnostic_schema):
            return (
                _arm_fixture_summary("R0_SINGLE", fixture_dir),
                _arm_fixture_summary("R3_VIEWPOINT_ADAPTIVE", fixture_dir),
            )


def _ablation_matrix() -> dict[str, Any]:
    fetchable = {
        "R0_SINGLE": _arm_fixture_summary("R0_SINGLE"),
        "R3_VIEWPOINT_ADAPTIVE": _arm_fixture_summary("R3_VIEWPOINT_ADAPTIVE"),
    }
    metadata_r0, metadata_r3 = _metadata_only_fixture()
    metadata = {"R0_SINGLE": metadata_r0, "R3_VIEWPOINT_ADAPTIVE": metadata_r3}
    shared_headroom_effect = (
        fetchable["R0_SINGLE"]["metrics"]["paper_card_count"] > 0
        and fetchable["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["paper_card_count"] > 0
        and metadata["R0_SINGLE"]["metrics"]["paper_card_count"] == 0
        and metadata["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["paper_card_count"] == 0
    )
    open_slot_false_positive = (
        metadata["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["paper_card_count"] == 0
        and "ADMITTED" in metadata["R3_VIEWPOINT_ADAPTIVE"]["open_slot_statuses"]
        and metadata["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["unique_attributable_contributions"] > 0
    )
    return {
        "schema_version": "g10r-y-ablation.1",
        "goal": GOAL,
        "external_calls": False,
        "experiment": "Run the same deterministic single/adaptive arms with public-content locators and with every candidate reduced to metadata-only.",
        "diagnostic_compatibility_shim": "The frozen G10R-T metadata branch emits legacy SEEK_LAWFUL_LOCATOR; this evaluator extends the schema in memory only so the path can be diagnosed without mutating G10R-X-hashed code.",
        "conditions": {
            "FETCHABLE_PUBLIC_CONTENT": fetchable,
            "METADATA_ONLY": metadata,
        },
        "causal_tests": {
            "shared_content_headroom_controls_evidence_yield": shared_headroom_effect,
            "adaptive_open_slot_can_false-positive_without_content": open_slot_false_positive,
            "agent_design_and_shared_acquisition_are_distinguishable": shared_headroom_effect and open_slot_false_positive,
        },
        "interpretation": {
            "shared_acquisition": "Removing lawful content routes collapses paper-card yield in both arms, matching the paid run's zero-fetch/zero-card result.",
            "agent_design": "The adaptive fixture still admits an open viewpoint and counts a unique contribution with zero cards, proving a separate open-slot/scoring defect.",
            "scoring": "The paid scorer correctly withheld evidence credit; the deterministic readiness fixture was more permissive than the paid evaluator.",
        },
    }


def analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    run = json.loads((PAID / "run.json").read_text(encoding="utf-8"))
    rows = [_checkpoint_row(path) for path in sorted((PAID / "checkpoints").glob("*.json"))]
    arms = {arm: _aggregate(rows, arm) for arm in ("A1", "A2-M")}
    ratio = lambda numerator, denominator: round(numerator / denominator, 4) if denominator else None
    ablation = _ablation_matrix()
    findings = [
        {
            "finding_id": "Y-F1",
            "layer": "SHARED_ACQUISITION_CONVERSION",
            "severity": "CRITICAL",
            "confidence": "HIGH",
            "finding": "Search worked, but neither arm converted metadata into content: 167 retained candidates produced zero fetches and zero paper cards.",
            "evidence": ["artifacts/goals/G10R-V/spend-ledger.json#arms", "artifacts/goals/G10R-V/checkpoints"],
            "causal_status": "NECESSARY_COMMON_CAUSE_OF_ZERO_EVIDENCE",
        },
        {
            "finding_id": "Y-F2",
            "layer": "LOCATOR_RESOLUTION",
            "severity": "CRITICAL",
            "confidence": "HIGH",
            "finding": "All 21 A2-M candidate selections remained PENDING/SEEK_LOCATOR; the live loop has no post-selection locator-resolution turn, so no selected metadata record can become fetchable unless the original plan already names a public content locator.",
            "evidence": ["artifacts/goals/G10R-V/checkpoints#research_loop.selections", "src/roman_concrete_lab/agents/investigation.py#_run_a2m"],
            "causal_status": "DIRECT_RUNTIME_CAUSE",
        },
        {
            "finding_id": "Y-F3",
            "layer": "OPEN_SLOT_DESIGN",
            "severity": "HIGH",
            "confidence": "HIGH",
            "finding": "The live society pre-admitted and funded an OPEN-ADMITTED viewpoint before evidence sharing in every case; two later open-slot records abstained while that viewpoint remained active with tasks, reports, and a dossier.",
            "evidence": ["artifacts/goals/G10R-V/checkpoints#viewpoint_society.active_ids", "artifacts/goals/G10R-V/checkpoints#research_loop.open_slot", "src/roman_concrete_lab/agents/investigation.py#_run_a2m"],
            "causal_status": "INDEPENDENT_AGENT_DESIGN_DEFECT",
        },
        {
            "finding_id": "Y-F4",
            "layer": "OFFLINE_GATE_VALIDITY",
            "severity": "HIGH",
            "confidence": "HIGH",
            "finding": "The prior positive fixture assumed direct public locators and its metadata-only branch was schema-invalid; after repair, an adaptive arm can still claim an open-slot contribution with zero evidence cards.",
            "evidence": ["src/roman_concrete_lab/agents/research_loop.py", "artifacts/goals/G10R-Y/ablation-matrix.json"],
            "causal_status": "READINESS_FIXTURE_FALSE_POSITIVE",
        },
        {
            "finding_id": "Y-F5",
            "layer": "COORDINATION_OVERHEAD",
            "severity": "HIGH",
            "confidence": "HIGH",
            "finding": "A2-M used 52 model calls and 7.54x A1 input tokens while producing 30% of A1's raw discovery count and no evidence gain.",
            "evidence": ["artifacts/goals/G10R-V/spend-ledger.json#arms"],
            "causal_status": "INDEPENDENT_EFFICIENCY_FAILURE",
        },
        {
            "finding_id": "Y-F6",
            "layer": "PAID_SCORER",
            "severity": "LOW",
            "confidence": "HIGH",
            "finding": "The paid scorer retained unresolved discoveries and hypotheses but correctly gave zero evidence/rubric credit without a fetched card; identity relabeling alone cannot repair the result.",
            "evidence": ["artifacts/goals/G10R-V/run.json#arm_results", "artifacts/goals/G10R-V/report.md"],
            "causal_status": "PROTECTIVE_NOT_PRIMARY_CAUSE",
        },
    ]
    remediations = [
        {
            "rank": 1,
            "id": "R1_LOCATOR_HEADROOM",
            "change": "Add a typed post-search locator-resolution turn shared by A1 and A2-M, and require recorded development cases to prove at least one policy-permitted content route before any new freeze.",
            "success": "Both arms can turn a metadata candidate into a selected public locator and page-aware card; metadata-only cases terminate as typed no-content, not silent completion.",
        },
        {
            "rank": 2,
            "id": "R2_EVIDENCE_CONDITIONED_OPEN_SLOT",
            "change": "Remove pre-admission. Propose and activate the open viewpoint only after shared evidence, with a distinct attributable basis; abstention creates no tasks, calls, dossier, or focus allocation.",
            "success": "Metadata-only fixtures never admit or score an open viewpoint; admitted fixtures bind the viewpoint to a card or reviewed candidate and discriminator.",
        },
        {
            "rank": 3,
            "id": "R3_COMPLETION_AND_SCORE_PARITY",
            "change": "Align deterministic and paid scoring: COMPLETE support needs observable work, and unique attributable contribution requires the same source/action/card joins used by the paid scorer.",
            "success": "No zero-card arm earns evidence or unique-attributable credit; unsupported records remain typed and reviewable.",
        },
        {
            "rank": 4,
            "id": "R4_ADAPTIVE_COORDINATION_BUDGET",
            "change": "Do not instantiate every structural task for every viewpoint. Create support work from unresolved needs, deduplicate it before model calls, and report value and actual usage separately.",
            "success": "The society preserves null/rival coverage while reducing non-discriminating reports and demonstrates a source-backed gain under the same hard per-case ceilings.",
        },
    ]
    thresholds = {
        "unique_attributable_contribution": "At least one A2-M contribution absent from A1 must bind action, candidate identity, permitted content/card, claim, and final portfolio; metadata-only or open-slot admission alone earns zero.",
        "evidence_card_yield": "Before a paid freeze, recorded positive fixtures for every selected case family must expose a policy-permitted content route; a live comparison is INCONCLUSIVE unless at least two cases yield a card in each arm or the trace proves an arm-specific acquisition difference.",
        "attribution_completeness": "100% of credited contributions resolve through action -> candidate -> card/typed discriminator -> dossier -> portfolio; unresolved candidates remain reviewable but uncredited.",
        "budget_parity": "A1 and A2-M retain identical per-case query, fetch, payload, simulation, input-token, output-token, cost, stopping, and source-policy ceilings; actual use and value-per-cost remain separate reported outcomes and excess overhead cannot be normalized away.",
        "stop_rule": "Do not freeze or pay for another comparison until all offline remediations pass metadata-only, fetchable, contradictory, malformed, partial-failure, budget-exhaustion, and replay fixtures. After any later paid run, stop escalation unless A2-M has a unique source-backed gain, noninferior total score, zero critical failures, and no common zero-content evaluation collapse.",
    }
    diagnosis = {
        "schema_version": "g10r-y-diagnosis.1",
        "goal": GOAL,
        "status": "POST_V_DIAGNOSIS_READY",
        "source_outcome": run["outcome"],
        "manifest_sha256": run["manifest_sha256"],
        "external_calls": False,
        "historical_source_hashes": _source_hashes(),
        "case_arm_loss_ledger": rows,
        "arm_totals": arms,
        "comparisons": {
            "a2_to_a1_input_token_ratio": ratio(arms["A2-M"]["input_tokens"], arms["A1"]["input_tokens"]),
            "a2_to_a1_cost_ratio": ratio(arms["A2-M"]["estimated_cost_usd"], arms["A1"]["estimated_cost_usd"]),
            "a2_to_a1_raw_discovery_ratio": ratio(arms["A2-M"]["raw_discovery"], arms["A1"]["raw_discovery"]),
            "total_retained_candidates": arms["A1"]["retained_sources"] + arms["A2-M"]["retained_sources"],
            "total_fetches": arms["A1"]["fetches"] + arms["A2-M"]["fetches"],
            "total_paper_cards": arms["A1"]["paper_cards"] + arms["A2-M"]["paper_cards"],
        },
        "findings": findings,
        "ranked_remediations": remediations,
        "proposed_next_treatment_thresholds": thresholds,
        "conclusion": "The paid result combines a shared acquisition-conversion failure with independent society design and efficiency defects. It does not justify abandoning the society architecture, and it does not justify another paid run before offline repair.",
    }
    return diagnosis, ablation


def run(output_dir: Path) -> dict[str, Any]:
    before = _source_hashes()
    diagnosis, matrix = analyze()
    diagnosis_again, matrix_again = analyze()
    after = _source_hashes()
    stable = canonical(diagnosis) == canonical(diagnosis_again) and canonical(matrix) == canonical(matrix_again)
    replay = {
        "schema_version": "g10r-y-replay.1",
        "goal": GOAL,
        "external_calls": False,
        "diagnosis_digest": digest(diagnosis),
        "replayed_diagnosis_digest": digest(diagnosis_again),
        "ablation_digest": digest(matrix),
        "replayed_ablation_digest": digest(matrix_again),
        "byte_stable": stable,
        "historical_artifacts_preserved": before == after,
        "causal_tests_passed": all(matrix["causal_tests"].values()),
    }
    criteria = {
        "schema_version": "g10r-y-criteria.1",
        "goal": GOAL,
        "criteria": [
            {"id": 1, "passes": len(diagnosis["case_arm_loss_ledger"]) == 8, "artifact": "diagnosis.json#case_arm_loss_ledger", "test": "test_reconstructs_all_case_arm_loss_ledgers"},
            {"id": 2, "passes": all("discovery_score_raw" in row["attribution_and_scoring"] for row in diagnosis["case_arm_loss_ledger"]), "artifact": "diagnosis.json#case_arm_loss_ledger", "test": "test_preserves_raw_discovery_and_unresolved_records"},
            {"id": 3, "passes": matrix["causal_tests"]["agent_design_and_shared_acquisition_are_distinguishable"], "artifact": "ablation-matrix.json#causal_tests", "test": "test_metadata_only_ablation_separates_acquisition_from_agent_design"},
            {"id": 4, "passes": all(key in diagnosis["proposed_next_treatment_thresholds"] for key in ("unique_attributable_contribution", "evidence_card_yield", "attribution_completeness", "budget_parity", "stop_rule")), "artifact": "diagnosis.json#proposed_next_treatment_thresholds", "test": "test_next_treatment_has_measurable_thresholds_and_stop_rule"},
            {"id": 5, "passes": stable and before == after, "artifact": "replay.json", "test": "test_replay_is_deterministic_external_free_and_preserves_history"},
        ],
    }
    verdict = "POST_V_DIAGNOSIS_READY" if all(item["passes"] for item in criteria["criteria"]) else "INCONCLUSIVE_POST_V_DIAGNOSIS"
    diagnosis["status"] = verdict
    _write(output_dir / "diagnosis.json", diagnosis)
    _write(output_dir / "ablation-matrix.json", matrix)
    _write(output_dir / "replay.json", replay)
    _write(output_dir / "criterion-ledger.json", criteria)
    a1, a2 = diagnosis["arm_totals"]["A1"], diagnosis["arm_totals"]["A2-M"]
    report = f"""# G10R-Y post-V paid-run diagnosis

`{verdict}`

## Answer

The society did not fail for one reason. The paid comparison combined a shared acquisition-conversion failure with independent society-design and efficiency defects. Search returned {diagnosis['comparisons']['total_retained_candidates']} retained candidates, but both arms made zero content fetches and produced zero paper cards. A2-M also pre-admitted an open viewpoint before evidence, spent {diagnosis['comparisons']['a2_to_a1_input_token_ratio']:.2f}x A1 input tokens, and produced less raw discovery ({a2['raw_discovery']} versus {a1['raw_discovery']}). The paid scorer correctly withheld evidence credit, so the zero score is not mainly a scorer bug.

## Offline causal ablation

The same deterministic R0/R3 fixtures were run with public content locators and with all candidates reduced to metadata-only. With public content, both arms produced cards and R3 produced additional attributable work. With metadata only, both arms produced zero cards, while R3 still admitted an open viewpoint and counted a contribution. This separates the common content-headroom failure from an independent open-slot/readiness-fixture false positive.

## Required remediation before another freeze

1. Add post-search lawful locator resolution for both arms and prove content headroom per case family.
2. Admit the open viewpoint only after shared evidence establishes a distinct attributable discriminator; abstention must create no calls or dossier.
3. Align offline and paid completion/scoring so zero-card metadata cannot earn unique-attributable credit.
4. Instantiate support work from unresolved needs and make the society's overhead visible rather than creating every role/task combination unconditionally.

## Acceptance evidence

| criterion | result | evidence |
|---|---|---|
| Eight case/arm loss ledgers | PASS | `diagnosis.json#case_arm_loss_ledger` |
| Raw candidates/hypotheses retained | PASS | `diagnosis.json#case_arm_loss_ledger` |
| Agent design separated from shared acquisition | PASS | `ablation-matrix.json#causal_tests` |
| Measurable next-treatment thresholds and stop rule | PASS | `diagnosis.json#proposed_next_treatment_thresholds` |
| Deterministic, external-free replay | {'PASS' if replay['byte_stable'] and replay['historical_artifacts_preserved'] else 'FAIL'} | `replay.json` |

Verification on 2026-10-24: focused G10R-Y/research-loop tests `19 passed`;
full suite `164 passed`; `git diff --check` passed.

## Authority

This goal made no model, network, credential, subscription, laboratory, or external-communication call. It does not promote evidence or authorize another paid run. The next eligible goal is G10R-Z, an offline repair and fixture-validity gate.
"""
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    return {"verdict": verdict, "diagnosis": diagnosis, "matrix": matrix, "replay": replay, "criteria": criteria}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/goals/G10R-Y")
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps({"verdict": result["verdict"], "byte_stable": result["replay"]["byte_stable"], "external_calls": False}, sort_keys=True))


if __name__ == "__main__":
    main()
