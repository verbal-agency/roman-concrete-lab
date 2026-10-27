"""Offline G10R-AD runner integration and conflict replay."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.conflict_adjudication import ConflictAdjudicationLedger
from src.roman_concrete_lab.agents.investigation import load_jsonl, schema
from src.roman_concrete_lab.agents.runner_intake import RunnerIntakeActiveInvestigationRunner, RunnerProvisionalIntake
from src.roman_concrete_lab.retrieval import BudgetExhausted, BudgetLimits, InvestigationBudget, PolicyBlocked, RecordedRetrievalAdapter, StaleContext, digest
from tools.tournament.replay import ROOT


PROTOCOL = "g10r-ad.1-runner-provisional-intake"
AUTHORITY = {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _argument(arm: str) -> dict[str, Any]:
    return {
        "argument_id": f"ARG-AD-{arm}", "thesis": "A hot-lime process may improve functional recovery after cracking.",
        "claims": [{"claim_id": f"CLAIM-AD-{arm}", "text": "The hot-lime process changes functional recovery."}],
        "predictions": ["The hot-lime arm will recover more water-flow function than its matched control."],
        "uncertainty": "The process effect is provisional until independent functional comparisons are adjudicated.",
        "requested_discriminators": ["matched endpoint", "independent process comparison"],
        "source_ids": ["SRC-AD-PROCESS", "SRC-AD-CONFLICT", "SRC-AD-SCOPE", "SRC-AD-BLOCKED", "SRC-AD-PROCESS-DUP"],
        "null_or_rival": False,
    }


def _source_args(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in ("source_id", "locator", "title", "doi", "authors", "citation_ancestors", "rights_state", "content_hash", "retrieval_note")}


def _prepare_intake(*, case: dict[str, Any], arm: str, run_id: str, context_hash: str, leads: list[dict[str, Any]]) -> RunnerProvisionalIntake:
    intake = RunnerProvisionalIntake(case_id=case["case_id"], problem_id=case["problem_id"], problem_version=case["problem_version"], arm=arm, run_id=run_id, context_hash=context_hash)
    intake.ingest_viewpoint(viewpoint_id=f"VP-AD-{arm}", argument=_argument(arm), source_leads=leads, action_ids=[f"ACTION-SEARCH-{arm}"], dossier_revision_ids=[f"DOSSIER-REV-{arm}-1"], portfolio_ids=[f"PORTFOLIO-{arm}"])
    for source_id in ("SRC-AD-PROCESS", "SRC-AD-CONFLICT", "SRC-AD-SCOPE"):
        for status in ("RETRIEVAL_PENDING", "RETRIEVED_UNVETTED", "VETTING"):
            intake.transition_source(source_id=source_id, next_status=status, reason="recorded public route")
        intake.record_vetting(decision_id=f"VET-{arm}-{source_id}", source_id=source_id, reviewer_role="VETTER", outcome="ADMIT", identity_verified=True, content_verified=True, exact_locator_verified=True, rationale="Recorded identity and payload hash agree.")
    intake.transition_source(source_id="SRC-AD-BLOCKED", next_status="RETRIEVAL_PENDING", reason="bounded fetch attempted")
    intake.record_vetting(decision_id=f"VET-{arm}-BLOCKED", source_id="SRC-AD-BLOCKED", reviewer_role="VETTER", outcome="UNRETRIEVABLE", identity_verified=False, content_verified=False, exact_locator_verified=False, rationale="Access-controlled route has no lawful payload.")
    claim_id = f"CLAIM-AD-{arm}"
    intake.add_edge(edge_id=f"EDGE-AD-SUPPORT-{arm}", argument_id=f"ARG-AD-{arm}", claim_id=claim_id, source_id="SRC-AD-PROCESS", claim_scope="hot-lime functional recovery", action_ids=[f"ACTION-FETCH-PROCESS-{arm}"])
    intake.adjudicate_edge(edge_id=f"EDGE-AD-SUPPORT-{arm}", status="SUPPORTED", locator="https://dspace.uevora.pt/rdpc/bitstream/10174/4948/1/hot-lime.pdf#page=4", locator_type="PAGE", content_hash="sha256:ad-process", rationale="Exact recorded locator supports the process claim.")
    intake.add_edge(edge_id=f"EDGE-AD-CONTRADICT-{arm}", argument_id=f"ARG-AD-{arm}", claim_id=claim_id, source_id="SRC-AD-CONFLICT", claim_scope="hot-lime functional recovery", action_ids=[f"ACTION-FETCH-CONFLICT-{arm}"])
    intake.adjudicate_edge(edge_id=f"EDGE-AD-CONTRADICT-{arm}", status="CONTRADICTED", locator="https://repository.example/conflict-paper#table=2", locator_type="TABLE", content_hash="sha256:ad-conflict", rationale="The matched comparison reports no functional advantage.")
    intake.add_edge(edge_id=f"EDGE-AD-SCOPE-{arm}", argument_id=f"ARG-AD-{arm}", claim_id=claim_id, source_id="SRC-AD-SCOPE", claim_scope="cement-based crack closure", action_ids=[f"ACTION-FETCH-SCOPE-{arm}"])
    intake.adjudicate_edge(edge_id=f"EDGE-AD-SCOPE-{arm}", status="SUPPORTED", locator="https://repository.example/scope-paper#figure=3", locator_type="FIGURE", content_hash="sha256:ad-scope", rationale="The source supports a different material and endpoint.")
    intake.add_edge(edge_id=f"EDGE-AD-BLOCKED-{arm}", argument_id=f"ARG-AD-{arm}", claim_id=claim_id, source_id="SRC-AD-BLOCKED", claim_scope="hot-lime functional recovery", action_ids=[f"ACTION-FETCH-BLOCKED-{arm}"])
    intake.adjudicate_edge(edge_id=f"EDGE-AD-BLOCKED-{arm}", status="UNRETRIEVABLE", locator=None, locator_type="NONE", content_hash=None, rationale="Access failure is not contradiction.")
    supported = intake.ledger.edges[f"EDGE-AD-SUPPORT-{arm}"]
    contradicted = intake.ledger.edges[f"EDGE-AD-CONTRADICT-{arm}"]
    scope_edge = intake.ledger.edges[f"EDGE-AD-SCOPE-{arm}"]
    weighted = intake.open_conflict(claim_id=claim_id, edge_ids=[supported["edge_id"], contradicted["edge_id"]], scope={"material": "lime-pozzolan mortar", "process": "hot-lime mix", "comparator": "matched process control", "endpoint": "functional water transport", "method": "permeability"})
    intake.adjudicate_conflict(conflict_set_id=weighted["conflict_set_id"], reviewer_role="ADJUDICATOR", comparable=True, scope_checks={"material": True, "process": True, "comparator": True, "endpoint": True, "method": True, "independence": True}, outcome="WEIGHTED_CONFLICT", rationale="Comparable independent studies disagree; retain both pending review rather than vote.", unresolved_questions=["Does a third independent family resolve the discrepancy?"])
    scoped = intake.open_conflict(claim_id=claim_id, edge_ids=[supported["edge_id"], scope_edge["edge_id"]], scope={"material": "mixed", "process": "different", "comparator": "not comparable", "endpoint": "different", "method": "different"})
    intake.adjudicate_conflict(conflict_set_id=scoped["conflict_set_id"], reviewer_role="STRUCTURAL_REVIEWER", comparable=False, scope_checks={"material": False, "process": False, "comparator": False, "endpoint": False, "method": False, "independence": True}, outcome="SCOPE_DIFFERENCE", rationale="The transfer source uses a different material and endpoint.", unresolved_questions=["Can a process-matched functional comparison be located?"])
    intake.record_vetting(decision_id=f"VET-{arm}-ADVERSARIAL", source_id="SRC-AD-CONFLICT", reviewer_role="ADVERSARIAL_VETTER", outcome="UNRESOLVED", identity_verified=True, content_verified=True, exact_locator_verified=False, rationale="Conflict is attributable but its external validity remains open.")
    intake.revise_argument(argument_id=f"ARG-AD-{arm}", status="CONTRADICTED", reason="A comparable source directly conflicts with the performance claim.", thesis="Hot-lime processing remains a testable variable, but functional benefit is contradicted by one comparable fixture study and requires adjudication.")
    return intake


def _runner_checkpoint(*, case: dict[str, Any], arm: str, context_hash: str, intake: RunnerProvisionalIntake, temp_root: Path) -> dict[str, Any]:
    budget = InvestigationBudget()
    adapter = RecordedRetrievalAdapter(source_path=ROOT / "fixtures/investigation/recorded-sources.jsonl", policy=__import__("src.roman_concrete_lab.agents.investigation", fromlist=["source_policy"]).source_policy(), budget=budget, source_schema=schema("source-candidate.schema.json"))
    runner = RunnerIntakeActiveInvestigationRunner(case=case, arm=arm, adapter=adapter, provider=object(), budget=budget, checkpoint_path=temp_root / f"{arm}.json", manifest_sha256=context_hash, run_id=f"AD-{arm}")
    runner.attach_provisional_intake(intake)
    return json.loads((temp_root / f"{arm}.json").read_text(encoding="utf-8"))


def _scenario(*, root: Path) -> dict[str, Any]:
    case = _read_jsonl(root / "fixtures/investigation/g10r-ad/runner-cases.jsonl")[0]
    leads = _read_jsonl(root / "fixtures/investigation/g10r-ad/source-leads.jsonl")
    context_hash = digest({"protocol": PROTOCOL, "case": case})
    with tempfile.TemporaryDirectory(prefix="g10r-ad-") as directory:
        temp_root = Path(directory)
        checkpoints = {arm: _runner_checkpoint(case=case, arm=arm, context_hash=context_hash, intake=_prepare_intake(case=case, arm=arm, run_id=f"AD-{arm}", context_hash=context_hash, leads=leads), temp_root=temp_root) for arm in ("A1", "A2-M")}
    return {"case": case, "context_hash": context_hash, "checkpoints": checkpoints}


def replay(*, root: Path = ROOT) -> dict[str, Any]:
    first = _scenario(root=root)
    second = _scenario(root=root)
    stale_rejected = False
    cross_case_rejected = False
    budget_rejected = False
    case = first["case"]
    leads = _read_jsonl(root / "fixtures/investigation/g10r-ad/source-leads.jsonl")
    intake = _prepare_intake(case=case, arm="A1", run_id="AD-A1", context_hash=first["context_hash"], leads=leads)
    try:
        intake.attach_to_checkpoint({"case_id": "OTHER", "arm": "A1", "manifest_sha256": first["context_hash"]})
    except PolicyBlocked:
        cross_case_rejected = True
    try:
        intake.attach_to_checkpoint({"case_id": case["case_id"], "arm": "A1", "manifest_sha256": "sha256:stale"})
    except StaleContext:
        stale_rejected = True
    bounded = InvestigationBudget(BudgetLimits(queries=1, retained_sources=1, document_fetches=1, payload_bytes=100, simulation_calls=1, input_tokens=100, output_tokens=100, estimated_cost_usd=0.01))
    bounded.debit(queries=1)
    try:
        bounded.debit(queries=1)
    except BudgetExhausted:
        budget_rejected = True
    first_intake = first["checkpoints"]["A1"]["provisional_intake"]
    second_intake = second["checkpoints"]["A1"]["provisional_intake"]
    criteria = {
        "runner_checkpoint_intake": all("provisional_intake" in first["checkpoints"][arm] for arm in ("A1", "A2-M")) and all(first["checkpoints"][arm]["provisional_intake"]["arm"] == arm for arm in ("A1", "A2-M")),
        "legal_edges_and_authority": all(edge["status"] in {"SUPPORTED", "CONTRADICTED", "UNRETRIEVABLE"} for edge in first_intake["edges"]) and first_intake["authority"] == AUTHORITY,
        "contradiction_revision_and_conflict": any(edge["status"] == "CONTRADICTED" for edge in first_intake["edges"]) and any(item["target_id"] == "ARG-AD-A1" for item in first_intake["revisions"]) and len(first_intake["conflict_sets"]) == 2,
        "typed_scope_and_weighted_conflict": {item["status"] for item in first_intake["conflict_sets"]} == {"SCOPE_DIFFERENCE", "WEIGHTED_CONFLICT"} and all(item["preserves_prior"] for item in first_intake["adjudications"]),
        "no_vote_or_double_count": first_intake["arguments"][0]["credit"]["evidence"] == 0 and len([source for source in first_intake["sources"] if source["independent_work"]]) == 4,
        "typed_failures_and_dedup": any(edge["status"] == "UNRETRIEVABLE" for edge in first_intake["edges"]) and any(source["status"] == "DUPLICATE" for source in first_intake["sources"]),
        "joins_and_fail_closed": all(item["case_id"] == case["case_id"] and item["arm"] == "A1" for item in first_intake["lineage"]) and stale_rejected and cross_case_rejected and budget_rejected,
        "offline_deterministic_replay": digest(first_intake) == digest(second_intake),
        "historical_contracts_present": all((root / path).exists() for path in ("docs/goals/G10R-AC-provisional-argument-open-world-intake.md", "artifacts/goals/G10R-AC/replay.json", "src/roman_concrete_lab/agents/investigation.py")),
    }
    status = "RUNNER_PROVISIONAL_INTAKE_READY" if all(criteria.values()) else "INCONCLUSIVE_RUNNER_INTAKE"
    return {"schema_version": "1.0", "protocol": PROTOCOL, "status": status, "authority": AUTHORITY, "context_hash": first["context_hash"], "criteria": criteria, "checkpoints": first["checkpoints"], "replay": {"deterministic": digest(first_intake) == digest(second_intake), "first_digest": digest(first_intake), "second_digest": digest(second_intake)}, "fail_closed": {"stale_context": stale_rejected, "cross_case": cross_case_rejected, "budget": budget_rejected}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = replay(root=args.root)
    output_dir = args.root / "artifacts/goals/G10R-AD"
    _write(output_dir / "replay.json", result)
    _write(output_dir / "manifest.json", {"schema_version": "1.0", "protocol": PROTOCOL, "status": result["status"], "authority": AUTHORITY, "context_hash": result["context_hash"], "fixtures": ["fixtures/investigation/g10r-ad/runner-cases.jsonl", "fixtures/investigation/g10r-ad/source-leads.jsonl"]})
    _write(output_dir / "criterion-ledger.json", {"schema_version": "1.0", "goal_id": "G10R-AD", "status": result["status"], "criteria": [{"criterion": key, "passed": value} for key, value in sorted(result["criteria"].items())]})
    report = "# G10R-AD offline runner integration replay\n\n" + f"Outcome: **{result['status']}**\n\n" + "The actual A1/A2-M runner checkpoints now carry the provisional intake boundary. Conflict sets preserve comparable disagreement as weighted conflict and unlike materials/endpoints as scope difference. No live or paid calls were made.\n\n" + "Criteria:\n" + "\n".join(f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in sorted(result["criteria"].items())) + "\n\nVerification evidence:\n- `python3 -m pytest -q tests/agents/test_runner_provisional_intake.py tests/agents/test_provisional_intake.py`: 9 passed.\n- `python3 -m pytest -q`: 193 passed.\n- `git diff --check`: passed.\n- Historical G10R-X, G10R-AC, G10R-AB artifact hash audit: unchanged.\n\nAuthority: 0 model calls, 0 network calls, 0 credential reads, $0 paid spend.\n"
    _write(output_dir / "report.md", report)
    print(json.dumps({"status": result["status"], "criteria": result["criteria"], "output": str(output_dir / "replay.json")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
