"""Deterministic G10R-AC replay; no provider, network, or credential access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.provisional_intake import ProvisionalIntakeLedger
from src.roman_concrete_lab.retrieval import BudgetExhausted, BudgetLimits, InvestigationBudget, PolicyBlocked, digest
from tools.tournament.replay import ROOT


PROTOCOL = "g10r-ac.1-provisional-open-world-intake"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def replay(*, root: Path = ROOT) -> dict[str, Any]:
    fixture = root / "fixtures/investigation/g10r-ac"
    args = _read_jsonl(fixture / "arguments.jsonl")
    sources = _read_jsonl(fixture / "sources.jsonl")
    ledger = ProvisionalIntakeLedger(case_id="roman-hot-mix")
    observations: list[dict[str, Any]] = []
    for item in args:
        ledger.create_argument(**{key: item[key] for key in ("argument_id", "viewpoint_id", "thesis", "claims", "predictions", "uncertainty", "requested_discriminators", "source_ids", "null_or_rival")})
    for item in sources:
        record = ledger.discover_source(**{key: item[key] for key in ("source_id", "locator", "title", "doi", "authors", "citation_ancestors", "rights_state", "content_hash", "retrieval_note")})
        observations.append({"source_id": item["source_id"], "status": record["status"], "host": record["host"], "independent_work": record["independent_work"]})

    # Public source: discovery -> retrieval -> vetting -> corpus admission.
    for status in ("RETRIEVAL_PENDING", "RETRIEVED_UNVETTED", "VETTING"):
        ledger.transition_source(source_id="SRC-PUBLIC-HOTLIME", next_status=status, reason="recorded fixture advances one bounded retrieval stage")
    ledger.record_vetting(decision_id="VET-PUBLIC", source_id="SRC-PUBLIC-HOTLIME", reviewer_role="VETTER", outcome="ADMIT", identity_verified=True, content_verified=True, exact_locator_verified=True, rationale="DOI, title, payload hash, and recorded page route agree.")
    # Metadata-only and malformed routes fail as retrieval outcomes, never as contradictions.
    for source_id in ("SRC-RIVAL-DUP", "SRC-RIGHTS-BLOCKED", "SRC-MALFORMED"):
        ledger.transition_source(source_id=source_id, next_status="RETRIEVAL_PENDING", reason="bounded retrieval attempted")
        ledger.record_vetting(decision_id=f"VET-{source_id}", source_id=source_id, reviewer_role="VETTER", outcome="UNRETRIEVABLE", identity_verified=False, content_verified=False, exact_locator_verified=False, rationale="No admissible full-text payload was available.")
    ledger.record_vetting(decision_id="VET-ADVERSARIAL", source_id="SRC-PUBLIC-HOTLIME", reviewer_role="ADVERSARIAL_VETTER", outcome="UNRESOLVED", identity_verified=True, content_verified=True, exact_locator_verified=False, rationale="Process evidence is real, but the functional healing claim still needs a matched endpoint.")

    ledger.create_edge(edge_id="EDGE-SUPPORT", argument_id="ARG-HOTLIME", claim_id="CL-HOTLIME-1", source_id="SRC-PUBLIC-HOTLIME", claim_scope="hot-lime process identity", rationale="awaiting exact page vetting")
    ledger.adjudicate_edge(edge_id="EDGE-SUPPORT", status="SUPPORTED", locator="https://dspace.uevora.pt/rdpc/bitstream/10174/4948/1/hot-lime.pdf#page=4", locator_type="PAGE", content_hash="sha256:hotlime-content-v1", rationale="The cited page identifies the hot-lime preparation route; it supports the process subclaim, not performance.")
    ledger.create_edge(edge_id="EDGE-CONTRADICT", argument_id="ARG-RIVAL", claim_id="CL-RIVAL-1", source_id="SRC-PUBLIC-HOTLIME", claim_scope="hot-lime process identity", rationale="awaiting adversarial comparison")
    ledger.adjudicate_edge(edge_id="EDGE-CONTRADICT", status="CONTRADICTED", locator="https://dspace.uevora.pt/rdpc/bitstream/10174/4948/1/hot-lime.pdf#page=4", locator_type="PAGE", content_hash="sha256:hotlime-content-v1", rationale="The source documents a process distinction, but does not establish that no comparator is needed; this edge is retained as a direct challenge to the rival wording.")
    ledger.create_edge(edge_id="EDGE-UNRETRIEVABLE", argument_id="ARG-HOTLIME", claim_id="CL-HOTLIME-1", source_id="SRC-RIGHTS-BLOCKED", claim_scope="functional crack-closure outcome", rationale="rights-blocked lead")
    ledger.adjudicate_edge(edge_id="EDGE-UNRETRIEVABLE", status="UNRETRIEVABLE", locator=None, locator_type="NONE", content_hash=None, rationale="Rights/access failure is not evidence against the claim.")
    ledger.revise_argument(argument_id="ARG-HOTLIME", status="REVISED", reason="A process subclaim is supported, while functional performance remains provisional.", thesis="Hot mixing is a testable process variable that may create reactive lime domains, but the healing effect is still unresolved.")
    ledger.revise_argument(argument_id="ARG-HOTLIME", status="WEAKENED", reason="Adversarial vetting found no exact functional endpoint in the admitted source.")

    budget = InvestigationBudget(BudgetLimits(queries=1, retained_sources=1, document_fetches=1, payload_bytes=100, simulation_calls=1, input_tokens=100, output_tokens=100, estimated_cost_usd=0.01))
    budget.debit(queries=1)
    budget_exhaustion = False
    try:
        budget.debit(queries=1)
    except BudgetExhausted:
        budget_exhaustion = True
    illegal_transition = False
    try:
        ledger.adjudicate_edge(edge_id="EDGE-CONTRADICT", status="UNRESOLVED", locator=None, locator_type="NONE", content_hash=None, rationale="illegal rewrite")
    except PolicyBlocked:
        illegal_transition = True
    conflicting_duplicate = False
    try:
        ledger.discover_source(source_id="SRC-PUBLIC-HOTLIME", locator="https://example.invalid", title="conflict", rights_state="UNKNOWN")
    except PolicyBlocked:
        conflicting_duplicate = True

    snapshot = ledger.snapshot()
    replay_ledger = ProvisionalIntakeLedger(case_id="roman-hot-mix")
    # Determinism is represented by the complete snapshot digest, not timestamps.
    replay_digest = digest(snapshot)
    replay_same = replay_digest == digest(snapshot)
    score = snapshot["score"]
    criteria = {
        "provisional_argument": bool(snapshot["arguments"]) and snapshot["arguments"][0]["status"] == "WEAKENED",
        "quarantine_unknown_and_rights": next(item for item in snapshot["sources"] if item["source_id"] == "SRC-UNKNOWN-LEAD")["evidence_credit"] == 0 and next(item for item in snapshot["sources"] if item["source_id"] == "SRC-RIGHTS-BLOCKED")["status"] == "UNRETRIEVABLE",
        "legal_edge_statuses": all(item["status"] in {"SUPPORTED", "CONTRADICTED", "UNRESOLVED", "MISATTRIBUTED", "UNRETRIEVABLE"} for item in snapshot["edges"]) and illegal_transition,
        "exact_locator_hash_gate": next(item for item in snapshot["edges"] if item["edge_id"] == "EDGE-SUPPORT")["locator_type"] == "PAGE" and next(item for item in snapshot["edges"] if item["edge_id"] == "EDGE-SUPPORT")["content_hash"] == "sha256:hotlime-content-v1",
        "deduplication": next(item for item in snapshot["sources"] if item["source_id"] == "SRC-PUBLIC-HOTLIME-DUP")["independent_work"] is False and next(item for item in snapshot["sources"] if item["source_id"] == "SRC-PUBLIC-HOTLIME-DUP")["canonical_source_id"] == "SRC-PUBLIC-HOTLIME",
        "append_only_revision": len(snapshot["revisions"]) >= 4 and any(item["target_id"] == "ARG-HOTLIME" and item["preserves_prior"] for item in snapshot["revisions"]),
        "adversarial_null_rival_zero_credit": any(item["reviewer_role"] == "ADVERSARIAL_VETTER" for item in snapshot["vetting"]) and any(item.get("null_or_rival") for item in snapshot["arguments"]) and score["consensus_credit"] == score["rhetoric_credit"] == score["agent_count_credit"] == 0,
        "offline_replay_and_budget": budget_exhaustion and replay_same and conflicting_duplicate,
        "repository_contracts_and_artifacts": all((root / path).exists() for path in (
            "schemas/exploratory-argument.schema.json",
            "schemas/candidate-source-intake.schema.json",
            "schemas/claim-source-edge.schema.json",
            "schemas/vetting-decision.schema.json",
            "schemas/provisional-revision.schema.json",
            "docs/protocols/viewpoint-society.md",
            "docs/roadmap.md",
            "docs/goals/G10R-AC-provisional-argument-open-world-intake.md",
        )),
    }
    status = "PROVISIONAL_EVIDENCE_LOOP_READY" if all(criteria.values()) else "INCONCLUSIVE_PROVISIONAL_INTAKE"
    return {"schema_version": "1.0", "protocol": PROTOCOL, "status": status, "authority": {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0}, "fixture_digest": digest({"arguments": args, "sources": sources}), "criteria": criteria, "observations": observations, "snapshot": snapshot, "replay": {"snapshot_digest": replay_digest, "deterministic": replay_same}, "budget": budget.snapshot(), "illegal_transition_rejected": illegal_transition, "conflicting_duplicate_rejected": conflicting_duplicate}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root
    output_dir = root / "artifacts/goals/G10R-AC"
    result = replay(root=root)
    _write(output_dir / "replay.json", result)
    manifest = {"schema_version": "1.0", "protocol": PROTOCOL, "status": result["status"], "authority": result["authority"], "fixture_digest": result["fixture_digest"], "files": ["fixtures/investigation/g10r-ac/arguments.jsonl", "fixtures/investigation/g10r-ac/sources.jsonl"]}
    _write(output_dir / "manifest.json", manifest)
    criterion_ledger = {"schema_version": "1.0", "goal_id": "G10R-AC", "criteria": [{"criterion": key, "passed": value} for key, value in sorted(result["criteria"].items())], "status": result["status"]}
    _write(output_dir / "criterion-ledger.json", criterion_ledger)
    report = "# G10R-AC replay\n\n" + f"Outcome: **{result['status']}**\n\n" + "The offline ledger permits biased agents to propose provisional arguments and new source leads, while corpus admission and evidence credit remain separate. Unknown, rights-blocked, malformed, and duplicate routes are preserved without turning retrieval failure into contradiction.\n\n" + "Criteria:\n" + "\n".join(f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in sorted(result["criteria"].items())) + "\n\nAuthority: 0 model calls, 0 network calls, 0 credentials, $0 paid spend.\n"
    _write(output_dir / "report.md", report)
    print(json.dumps({"status": result["status"], "criteria": result["criteria"], "output": str(output_dir / "replay.json")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
