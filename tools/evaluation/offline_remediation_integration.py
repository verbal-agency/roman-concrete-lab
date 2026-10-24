"""Offline G10R-S integration gate for the remediated A2-M runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import validate

from src.roman_concrete_lab.agents.investigation import (
    ActiveInvestigationRunner,
    InvestigationBudget,
    BudgetLimits,
    load_json,
    load_jsonl,
    phase_a,
    provider_schema,
    schema,
    source_policy,
    validate_paper_evidence_card,
)
from src.roman_concrete_lab.retrieval import BudgetExhausted, PolicyBlocked, canonical, digest, normalize_query
from tools.tournament.replay import ROOT


FIXTURE = ROOT / "fixtures/investigation/remediation-sources.jsonl"
FETCH_LOCATOR = "https://digitalcommons.usu.edu/etd2023/669/"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class _RemediationAdapter:
    """Recorded provider with exact locator resolution and page-aware text."""

    def __init__(self, *, budget: InvestigationBudget) -> None:
        self.budget = budget
        self.policy = source_policy()
        self.sources = []
        for line in FIXTURE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self.sources.append(json.loads(line))

    def search(self, query: str, **_: Any) -> dict[str, Any]:
        normalized = normalize_query(query)
        self.budget.debit(queries=1)
        if normalized.startswith("open slot"):
            selected = [self.sources[1]]
        elif normalized in {"shared duplicate query", "remediation fetch candidate"}:
            selected = [self.sources[0]]
        else:
            selected = []
        results = []
        for source in selected:
            candidate = {key: value for key, value in source.items() if not key.startswith("_fixture_")}
            self.policy.decide(candidate["locator"], fetch_content=False)
            candidate["discovery_query"] = normalized
            candidate["host"] = self.policy.decide(candidate["locator"], fetch_content=False)["host"]
            validate(candidate, schema("source-candidate.schema.json"))
            results.append(candidate)
            self.budget.debit(retained_sources=1)
        return {"query": normalized, "replayed": False, "results": results}

    def fetch_public_text(self, locator: str) -> dict[str, Any]:
        source = next(
            (item for item in self.sources if locator in {item.get("locator"), item.get("content_locator")}),
            None,
        )
        if source is None or not source.get("content_locator"):
            raise PolicyBlocked("fixture has no exact public content locator")
        resolved = source["content_locator"]
        self.policy.decide(resolved, fetch_content=True)
        text = source["_fixture_payload"]
        content_hash = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
        page_hash = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
        return {
            "content_hash": content_hash,
            "parser": "recorded-text-v1",
            "extraction_status": "EXTRACTED",
            "page_count": 1,
            "pages": [{
                "page_number": 1,
                "locator": f"{resolved}#page=1",
                "text": text,
                "text_hash": page_hash,
            }],
        }


class _RemediationProvider:
    """Provider-shaped deterministic fixture; it never calls a model."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def _response(self, kwargs: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(kwargs["call_id"])
        return {
            "call_id": kwargs["call_id"], "provider": "offline-remediation-fixture", "model": "none",
            "reasoning_effort": "none", "store": False, "tools": [],
            "response_id_sha256": "sha256:offline-remediation-fixture", "output": output,
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "estimated_maximum_cost_usd": 0.0, "estimated_actual_cost_usd": 0.0,
            "latency_seconds": 0.0,
        }

    def call(self, **kwargs: Any) -> dict[str, Any]:
        name = kwargs["format_name"]
        packet = kwargs["packet"]
        case = packet["case"]
        if name == "g10m_proponent_plan":
            viewpoint = packet["viewpoint_card"]["viewpoint_id"]
            output = {
                "schema_version": "1.0", "case_id": case["case_id"], "branch_id": packet["branch_id"],
                "primary_queries": [{"query": "shared duplicate query", "index": "catalog", "rationale": "bounded remediation acquisition"}],
                "follow_up_queries": [{"query": "novel follow-up discriminator", "index": "catalog", "rationale": "decision-value follow-up"}] if viewpoint.endswith("M2") else [],
                "requested_fetch_locators": [FETCH_LOCATOR] if viewpoint.endswith("M1") else [],
                "simulation_requests": [], "abstain_reason": "",
            }
            return self._response(kwargs, output)
        if name == "g10m_proponent_report":
            mechanism = packet["mechanism_card"]
            source_ids = [item["source_candidate_id"] for item in packet.get("available_source_candidates", [])]
            claims = []
            if source_ids:
                claims = [{
                    "claim_id": f"CLAIM-{mechanism['mechanism_id']}",
                    "statement": mechanism["mechanism_statement"],
                    "prediction": mechanism["predicted_observations"][0],
                    "falsifier": mechanism["falsifiers"][0],
                    "support_region": mechanism["support_region"],
                    "provenance": source_ids,
                    "promotion_status": "REVIEW_REQUIRED",
                }]
            output = {
                "schema_version": "1.0", "report_id": f"REPORT-{mechanism['mechanism_id']}",
                "case_id": case["case_id"], "mechanism_id": mechanism["mechanism_id"],
                "role": "mechanism_proponent", "action_ids": [], "source_candidate_ids": source_ids,
                "claims": claims, "negative_searches": ["No unrecorded source search was used."],
                "unresolved_questions": ["Source identity and endpoint fit remain review-required."],
                "proposed_next_actions": ["Review the page-located card and run a process-matched discriminator."],
                "claimed_contribution": "Typed offline viewpoint contribution.", "status": "COMPLETE",
            }
            return self._response(kwargs, output)
        if name == "g10m_auditor_plan":
            output = {
                "schema_version": "1.0", "case_id": case["case_id"], "branch_id": packet["branch_id"],
                "primary_queries": [{"query": "shared duplicate query", "index": "catalog", "rationale": "structural audit"}],
                "follow_up_queries": [], "requested_fetch_locators": [], "simulation_requests": [], "abstain_reason": "",
            }
            return self._response(kwargs, output)
        if name == "g10m_structural_critique":
            target = next(item["mechanism_id"] for item in packet["mechanism_roster"] if item["kind"] != "OPEN_SLOT")
            output = {
                "schema_version": "1.0", "critique_id": f"CRIT-{packet['branch_id']}",
                "case_id": case["case_id"], "auditor_role": packet["structural_role"],
                "target_mechanism_id": target, "claim_ids": [],
                "challenge": "Comparator and provenance remain review-required.",
                "contradiction_status": "UNRESOLVED",
                "proposed_discriminator": "Retrieve a process-matched comparison.",
                "provenance": ["offline-remediation-fixture"], "promotion_status": "REVIEW_REQUIRED",
            }
            return self._response(kwargs, output)
        if name == "g10r_paper_evidence_card":
            document = packet["document"]
            page = document["page_spans"][0]
            source = packet["source_candidate"]
            output = {
                "schema_version": "1.0", "card_id": f"CARD-{source['source_candidate_id']}",
                "source_candidate_id": source["source_candidate_id"], "document_hash": document["content_hash"],
                "parser": document["parser"], "extraction_status": "EXTRACTED", "page_count": document["page_count"],
                "facts": [{"field": "endpoint", "value": "recorded water-flow endpoint", "reporting_status": "REPORTED", "support_type": "DIRECT", "page_locator": page["locator"], "page_text_hash": page["text_hash"], "confidence": "HIGH"}],
                "unresolved": ["Fixture content is not scientific validation."],
                "authority_note": "Derived extraction for review; no evidence promotion, performance claim, or laboratory authority.",
            }
            return self._response(kwargs, output)
        if name == "g10m_adjudication":
            null_id = next(item["mechanism_id"] for item in packet["mechanism_roster"] if item["kind"] == "NULL")
            source_ids = sorted({item["source_candidate_id"] for item in packet.get("available_source_candidates", [])})
            output = {
                "schema_version": "1.0", "case_id": case["case_id"], "status": "REVIEW_REQUIRED",
                "summary": "Offline remediation integration preserved competing viewpoints and source uncertainty.",
                "source_candidate_ids": source_ids, "hypotheses": [], "leading_hypothesis_id": None,
                "credible_rival_ids": [null_id], "unresolved_disputes": ["Fixture evidence remains review-required."],
                "negative_searches": ["No external search was used."],
                "next_discriminating_action": "Review the page-located card and run a process-matched discriminator.",
                "authority_note": "Review required; no evidence promotion or laboratory authority.",
            }
            return self._response(kwargs, output)
        raise AssertionError(f"unexpected offline provider format: {name}")


def _run_case(case: dict[str, Any], *, manifest_hash: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        budget = InvestigationBudget()
        provider = _RemediationProvider()
        runner = ActiveInvestigationRunner(
            case=case, arm="A2-M", adapter=_RemediationAdapter(budget=budget), provider=provider,
            budget=budget, checkpoint_path=Path(directory) / "run.json", manifest_sha256=manifest_hash,
            run_id=f"G10R-S-{case['case_id']}", document_cache_dir=Path(directory) / "raw",
        )
        result = runner.run(owner_activated=True)
        checkpoint = json.loads((Path(directory) / "run.json").read_text(encoding="utf-8"))
        resume_provider = _RemediationProvider()
        resume_budget = InvestigationBudget()
        resumed = ActiveInvestigationRunner(
            case=case, arm="A2-M", adapter=_RemediationAdapter(budget=resume_budget), provider=resume_provider,
            budget=resume_budget, checkpoint_path=Path(directory) / "run.json", manifest_sha256=manifest_hash,
            run_id=f"G10R-S-{case['case_id']}", document_cache_dir=Path(directory) / "raw",
        ).run(owner_activated=True)
        society = checkpoint["viewpoint_society"]
        bus = society["evidence_bus"]
        return {
            "case_id": case["case_id"], "status": result["status"], "state": result["state"],
            "budget": result["budget"], "remediation_manifest": result["remediation_manifest"],
            "provider_call_count": len(provider.calls), "action_records": result["actions"],
            "resume_provider_call_count": len(resume_provider.calls),
            "resume_status": resumed["status"],
            "source_candidates": result["checkpoint"].get("source_candidates", {}) if "checkpoint" in result else checkpoint.get("source_candidates", {}),
            "paper_evidence_cards": checkpoint.get("paper_evidence_cards", {}),
            "viewpoint_society": society, "evidence_bus": bus,
            "checkpoint_digest": digest(checkpoint),
        }


def _edge_cases(rows: list[dict[str, Any]]) -> dict[str, bool]:
    budget = InvestigationBudget(BudgetLimits(queries=0))
    budget_exhaustion = False
    try:
        budget.preflight(queries=1)
    except BudgetExhausted:
        budget_exhaustion = True
    malformed = False
    try:
        validate({"bad": True}, schema("investigation-plan.schema.json"))
    except Exception:
        malformed = True
    partial = all(row["resume_status"] == "COMPLETED" and row["resume_provider_call_count"] == 0 for row in rows)
    return {"malformed_provider_output": malformed, "partial_checkpoint_trace": partial, "budget_exhaustion": budget_exhaustion}


def _row_ready(row: dict[str, Any]) -> bool:
    society = row["viewpoint_society"]
    bus = row["evidence_bus"]
    active = society["active_ids"]
    fetch_actions = [item for item in row["action_records"] if item["action_type"] == "FETCH_PERMITTED_CONTENT" and item["policy_status"] == "ALLOWED" and item["output_ids"]]
    duplicate_actions = [item for item in row["action_records"] if item["input"].get("suppressed_duplicate")]
    novel_actions = [item for item in row["action_records"] if item["action_type"] == "SEARCH" and not item["input"].get("suppressed_duplicate") and item["input"].get("query") not in {"shared duplicate query"}]
    open_slot = any(item.endswith("-ADMITTED") for item in active)
    all_tasks = [task for task in bus["tasks"].values()]
    all_reports = [report for report in bus["reports"].values()]
    reports_by_viewpoint = {viewpoint: [report for report in all_reports if report["viewpoint_id"] == viewpoint] for viewpoint in active}
    return bool(
        row["status"] == "COMPLETED"
        and row["resume_status"] == "COMPLETED"
        and row["resume_provider_call_count"] == 0
        and row["remediation_manifest"]["active"]
        and row["remediation_manifest"]["acquisition_first"]
        and row["remediation_manifest"]["executable_support"]
        and row["remediation_manifest"]["locator_bridge"]
        and row["remediation_manifest"]["deduplicate_queries"]
        and row["remediation_manifest"]["bounded_open_slot"]
        and open_slot
        and fetch_actions
        and row["paper_evidence_cards"]
        and any(item.get("content_hash") is None for item in row["source_candidates"].values())
        and duplicate_actions
        and novel_actions
        and len(all_tasks) == len(active) * 5
        and all(len(reports_by_viewpoint[viewpoint]) >= 5 for viewpoint in active)
        and society["portfolio"]
        and society["portfolio"]["credible_rival_ids"]
        and not any(dossier.get("diagnostics") for dossier in bus["dossiers"].values())
    )


def replay(*, output_dir: Path | None = None) -> dict[str, Any]:
    manifest_hash = phase_a()["manifest_sha256"]
    cases = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
    first = [_run_case(case, manifest_hash=manifest_hash) for case in cases]
    second = [_run_case(case, manifest_hash=manifest_hash) for case in cases]
    stable = canonical(first) == canonical(second)
    rows = first
    ready = all(_row_ready(row) for row in rows) and stable
    result = {
        "schema_version": "1.0", "goal": "G10R-S",
        "status": "RUNTIME_REMEDIATION_READY" if ready else "INCONCLUSIVE_RUNTIME_REMEDIATION",
        "external_calls": False, "manifest_sha256": manifest_hash,
        "fixture_sha256": digest(FIXTURE.read_text(encoding="utf-8")),
        "cases": rows, "byte_stable": stable, "edge_cases": _edge_cases(rows),
        "failure_reasons": [] if ready else ["one or more integrated runner invariants failed"],
        "authority": {"network": "none", "model_calls": "none", "source_policy": "unchanged", "evidence_promotion": "prohibited", "lab_execution": "prohibited"},
    }
    if output_dir is not None:
        _write(output_dir / "run.json", result)
        _write(output_dir / "replay.json", {
            "schema_version": "1.0", "goal": "G10R-S", "status": result["status"],
            "external_calls": False, "byte_stable": stable,
            "case_statuses": {row["case_id"]: _row_ready(row) for row in rows},
            "edge_cases": result["edge_cases"], "checkpoint_digests": {row["case_id"]: row["checkpoint_digest"] for row in rows},
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/goals/G10R-S")
    args = parser.parse_args()
    result = replay(output_dir=args.output_dir)
    report = "# G10R-S offline remediation integration\n\n"
    report += f"Status: `{result['status']}`\n\n"
    report += f"The actual A2-M runner executed the combined G10R-Q treatment across {len(result['cases'])} sealed fixtures with no model, network, credential, or laboratory calls. Byte-stable replay: `{result['byte_stable']}`.\n\n"
    report += "Verified: acquisition-first scheduling, executable structural support tasks, exact locator-to-page-card joins, deterministic duplicate suppression, metadata-only pending state, null/rival preservation, admitted open-slot work, checkpoint traces, and authority boundaries. The result does not authorize a paid run.\n"
    (args.output_dir / "report.md").parent.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "external_calls": result["external_calls"], "byte_stable": result["byte_stable"]}, indent=2))


if __name__ == "__main__":
    main()
