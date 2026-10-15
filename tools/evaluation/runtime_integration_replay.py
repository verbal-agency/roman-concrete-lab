"""Offline G10R-I runtime-integration gate.

The gate audits the live-capable runner without importing a provider or network
adapter, then replays the deterministic G10D viewpoint fixtures. A design
fixture can pass while the live runner still fails the integration gate; that
distinction is the purpose of this check.
"""

from __future__ import annotations

import argparse
import base64
import json
import tempfile
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.investigation import (
    ActiveInvestigationRunner,
    InvestigationBudget,
    load_json,
    phase_a,
    provider_schema,
    schema,
    source_policy,
    validate_paper_evidence_card,
)
from src.roman_concrete_lab.retrieval import PolicyBlocked, RecordedRetrievalAdapter
from src.roman_concrete_lab.retrieval.pdf import extract_pdf
from src.roman_concrete_lab.agents.viewpoint_society import run_offline_fixture
from tools.tournament.replay import ROOT


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _runner_audit(root: Path) -> dict[str, Any]:
    source = (root / "src/roman_concrete_lab/agents/investigation.py").read_text(encoding="utf-8")
    return {
        "legacy_mechanism_tournament_imported": "from .mechanism_tournament import" in source,
        "viewpoint_society_imported": "ViewpointSociety" in source,
        "evidence_bus_imported": "EvidenceBus" in source,
        "open_slot_filtered": 'card["kind"] != "OPEN_SLOT"' in source,
        "runtime_contract_ready": (
            "ViewpointSociety" in source
            and "EvidenceBus" in source
            and 'card["kind"] != "OPEN_SLOT"' not in source
        ),
    }


def _fixture_row(case: dict[str, Any]) -> dict[str, Any]:
    result = run_offline_fixture(case)
    checkpoint = result["checkpoint"]
    envelope = result["envelope"]
    bus = checkpoint["evidence_bus"]
    return {
        "case_id": case["case_id"],
        "status": result["status"],
        "envelope_status": envelope["status"],
        "viewpoint_count": len(checkpoint["active_ids"]),
        "null_retained": bool(envelope["portfolio"]["credible_rival_ids"]),
        "open_slot_present": any(card["kind"] == "OPEN_SLOT" for card in case["viewpoint_cards"]),
        "support_task_count": len(bus["tasks"]),
        "support_report_count": len(bus["reports"]),
        "dossier_count": len(bus["dossiers"]),
        "critique_count": len(bus["critiques"]),
        "source_candidate_count": len(bus["candidates"]),
        "evidence_bus_join_diagnostics": sorted(
            diagnostic
            for dossier in bus["dossiers"].values()
            for diagnostic in dossier.get("diagnostics", [])
        ),
        "dissent_retained": bool(result["score"]["dissent_retained"]),
        "evidence_promotion": result["score"]["evidence_promotion"],
        "primary_score": result["score"]["primary_score"],
    }


class _ReplayProvider:
    """Deterministic provider-shaped stub; it never calls a model or network."""

    def call(self, **kwargs: Any) -> dict[str, Any]:
        packet = kwargs["packet"]
        case = packet["case"]
        name = kwargs["format_name"]
        branch = packet["branch_id"]
        if name in {"g10m_proponent_plan", "g10m_auditor_plan"}:
            output = {
                "schema_version": "1.0", "case_id": case["case_id"], "branch_id": branch,
                "primary_queries": [{"query": f"{branch} bounded discriminator", "index": "catalog", "rationale": "offline integration fixture"}],
                "follow_up_queries": [], "requested_fetch_locators": [], "simulation_requests": [], "abstain_reason": "",
            }
        elif name == "g10m_proponent_report":
            card = packet["mechanism_card"]
            mid = card["mechanism_id"]
            output = {
                "schema_version": "1.0", "report_id": f"REPORT-{mid}", "case_id": case["case_id"], "mechanism_id": mid,
                "role": "mechanism_proponent", "action_ids": [], "source_candidate_ids": [],
                "claims": [{"claim_id": f"CLAIM-{mid}", "statement": card["mechanism_statement"], "prediction": card["predicted_observations"][0], "falsifier": card["falsifiers"][0], "support_region": card["support_region"], "provenance": ["offline-fixture"], "promotion_status": "REVIEW_REQUIRED"}],
                "negative_searches": ["No external source search in offline fixture."], "unresolved_questions": ["Source support remains unresolved."], "proposed_next_actions": ["Retrieve a lawful discriminator."], "claimed_contribution": "Typed offline viewpoint contribution.", "status": "COMPLETE",
            }
        elif name == "g10m_structural_critique":
            target = next(item["mechanism_id"] for item in packet["mechanism_roster"] if item["kind"] != "OPEN_SLOT")
            output = {
                "schema_version": "1.0", "critique_id": f"CRIT-{branch}", "case_id": case["case_id"], "auditor_role": packet["structural_role"], "target_mechanism_id": target,
                "claim_ids": [], "challenge": "Comparator and provenance remain unresolved.", "contradiction_status": "UNRESOLVED", "proposed_discriminator": "Retrieve a process-matched comparison.", "provenance": ["offline-fixture"], "promotion_status": "REVIEW_REQUIRED",
            }
        else:
            null_id = next(item["mechanism_id"] for item in packet["mechanism_roster"] if item["kind"] == "NULL")
            output = {
                "schema_version": "1.0", "case_id": case["case_id"], "status": "REVIEW_REQUIRED",
                "summary": "Offline society integration fixture; no scientific conclusion.", "source_candidate_ids": [], "hypotheses": [],
                "leading_hypothesis_id": None, "credible_rival_ids": [null_id], "unresolved_disputes": ["Offline fixture is not evidence."],
                "negative_searches": ["No external search executed."], "next_discriminating_action": "Run a lawful source review.",
                "authority_note": "Review required; no evidence promotion or laboratory authority.",
            }
        return {
            "call_id": kwargs["call_id"], "provider": "offline-fixture", "model": "none", "reasoning_effort": "none", "store": False, "tools": [],
            "response_id_sha256": "sha256:offline-fixture", "output": output,
            "usage": {"input_tokens": 0, "output_tokens": 0}, "estimated_maximum_cost_usd": 0.0, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0,
        }


def _runtime_smoke(root: Path) -> dict[str, Any]:
    """Exercise the actual A2-M runner with a deterministic provider stub."""
    case = _load_jsonl(root / "fixtures/investigation/sealed.jsonl")[0]
    manifest_hash = phase_a()["manifest_sha256"]
    def run_once() -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as directory:
            budget = InvestigationBudget()
            adapter = RecordedRetrievalAdapter(
                source_path=root / "fixtures/investigation/recorded-sources.jsonl", policy=source_policy(), budget=budget,
                source_schema=schema("source-candidate.schema.json"),
            )
            runner = ActiveInvestigationRunner(
                case=case, arm="A2-M", adapter=adapter, provider=_ReplayProvider(), budget=budget,
                checkpoint_path=Path(directory) / "runtime.json", manifest_sha256=manifest_hash, run_id="G10R-I-offline",
            )
            result = runner.run(owner_activated=True)
            society = runner.viewpoint_society
            checkpoint = runner.checkpoint
            return {
            "status": result["status"], "state": result["state"], "action_count": len(result["actions"]),
            "model_trace_count": len(result["model_traces"]), "viewpoint_count": len(society.active_ids) if society else 0,
            "open_slot_admitted": bool(society and any(item.endswith("-ADMITTED") for item in society.active_ids)),
            "support_task_count": len(society.bus.tasks) if society else 0,
            "support_report_count": len(society.bus.reports) if society else 0,
            "dossier_count": len(society.bus.dossiers) if society else 0,
            "critique_count": len(society.bus.critiques) if society else 0,
            "focus_present": bool(society and society.focus), "portfolio_present": bool(society and society.portfolio),
            "checkpoint_has_society": bool(checkpoint.get("viewpoint_society")),
            "evidence_bus_join_diagnostics": sorted({diagnostic for dossier in society.bus.dossiers.values() for diagnostic in dossier.get("diagnostics", [])}) if society else ["missing_society"],
            "authority_safe": bool(society and society.portfolio and "no evidence" in society.portfolio["authority_note"].casefold()),
            }
    first = run_once()
    second = run_once()
    first_for_compare = {key: value for key, value in first.items() if key != "replay_stable"}
    second_for_compare = {key: value for key, value in second.items() if key != "replay_stable"}
    first["replay_stable"] = first_for_compare == second_for_compare
    return first


def _document_fixture(root: Path) -> dict[str, Any]:
    benchmark = load_json(root / "fixtures/investigation/pdf-benchmark.json")
    payload = base64.b64decode((root / "fixtures/investigation/pdf-benchmark.b64").read_text(encoding="utf-8").strip())
    document = extract_pdf(payload, locator=benchmark["locator"], max_pages=4, max_characters=45_000)
    page = document["pages"][0]
    card = {
        "schema_version": "1.0", "card_id": "CARD-G10R-I", "source_candidate_id": "SRC-G10R-I-PDF",
        "document_hash": document["content_hash"], "parser": document["parser"], "extraction_status": document["extraction_status"], "page_count": document["page_count"],
        "facts": [{"field": "endpoint", "value": "water-flow recovery", "reporting_status": "REPORTED", "support_type": "DIRECT", "page_locator": page["locator"], "page_text_hash": page["text_hash"], "confidence": "HIGH"}],
        "unresolved": [], "authority_note": "Derived extraction for review; no evidence promotion, performance claim, or laboratory authority.",
    }
    validate_paper_evidence_card(card, document)
    rights_blocked = False
    try:
        source_policy().decide("https://api.openalex.org/works/W-offline", fetch_content=True)
    except PolicyBlocked:
        rights_blocked = True
    return {"positive_page_card": True, "page_locator": page["locator"], "negative_rights_blocked": rights_blocked, "payload_retained": False}


def replay(*, root: Path = ROOT) -> dict[str, Any]:
    runner = _runner_audit(root)
    fixture_cases = _load_jsonl(root / "fixtures/investigation/viewpoint-society/development.jsonl")
    fixture_cases += _load_jsonl(root / "fixtures/investigation/viewpoint-society/sealed.jsonl")
    fixtures = [_fixture_row(case) for case in fixture_cases]
    runtime_smoke = _runtime_smoke(root)
    document_fixture = _document_fixture(root)
    runtime_ready = (
        runtime_smoke["status"] == "COMPLETED"
        and runtime_smoke["open_slot_admitted"]
        and runtime_smoke["checkpoint_has_society"]
        and runtime_smoke["support_task_count"] > 0
        and runtime_smoke["support_report_count"] > 0
        and runtime_smoke["dossier_count"] > 0
        and runtime_smoke["critique_count"] > 0
        and runtime_smoke["focus_present"]
        and runtime_smoke["portfolio_present"]
        and runtime_smoke["replay_stable"]
        and runtime_smoke["authority_safe"]
        and not runtime_smoke["evidence_bus_join_diagnostics"]
    )
    fixture_ready = all(
        row["status"] == "COMPLETE"
        and row["support_task_count"] > 0
        and row["support_report_count"] > 0
        and row["dossier_count"] > 0
        and row["critique_count"] > 0
        and row["dissent_retained"]
        and row["evidence_promotion"] is False
        for row in fixtures
    )
    status = "RUNTIME_INTEGRATION_READY" if runner["runtime_contract_ready"] and fixture_ready and runtime_ready and document_fixture["positive_page_card"] and document_fixture["negative_rights_blocked"] else "RUNTIME_INTEGRATION_NO_GO"
    return {
        "schema_version": "1.0",
        "goal": "G10R-I",
        "status": status,
        "external_calls": False,
        "runner_audit": runner,
        "fixture_ready": fixture_ready,
        "runtime_smoke": runtime_smoke,
        "runtime_ready": runtime_ready,
        "document_fixture": document_fixture,
        "fixtures": fixtures,
        "failure_reasons": sorted(
            reason
            for reason, failed in {
                "runner_missing_g10d_viewpoint_society": not runner["viewpoint_society_imported"],
                "runner_missing_g10p_evidence_bus": not runner["evidence_bus_imported"],
                "runner_uses_legacy_mechanism_tournament": runner["legacy_mechanism_tournament_imported"],
                "runner_filters_open_slot": runner["open_slot_filtered"],
                "offline_fixture_failure": not fixture_ready,
                "runtime_smoke_failure": not runtime_ready,
                "document_fixture_failure": not (document_fixture["positive_page_card"] and document_fixture["negative_rights_blocked"] and not document_fixture["payload_retained"]),
            }.items()
            if failed
        ),
        "next_action": (
            "Integrate ViewpointSociety and EvidenceBus into the A2-M runner, then rerun this gate."
            if status != "RUNTIME_INTEGRATION_READY"
            else "Freeze a fresh Phase-A manifest before any future paid evaluation."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10R-I/replay.json")
    args = parser.parse_args()
    output = replay()
    _write(args.output, output)
    print(json.dumps({"status": output["status"], "external_calls": output["external_calls"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
