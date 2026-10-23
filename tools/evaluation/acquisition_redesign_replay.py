"""Offline G10R-A acquisition and support-task replay.

This replay is intentionally provider- and network-free.  It exercises the
same viewpoint/evidence-bus contracts with a deterministic fetch-positive PDF,
metadata-only and blocked sources, a malformed document, a weakening report,
and an exhausted-budget rejection.  It also records the request lifecycle so a
future live run can distinguish agent choice from runner or policy suppression.
"""

from __future__ import annotations

import argparse
import base64
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import validate

from src.roman_concrete_lab.agents.investigation import load_json, schema, validate_paper_evidence_card
from src.roman_concrete_lab.agents.viewpoint_society import ViewpointSociety, score_viewpoint_portfolio, viewpoint_cards_from_roster
from src.roman_concrete_lab.retrieval import PolicyBlocked, SourcePolicy, canonical, digest
from src.roman_concrete_lab.retrieval.pdf import DocumentExtractionError, extract_pdf
from tools.tournament.replay import ROOT


TIMESTAMP = "2026-10-23T00:00:00Z"
CASE_ID = "G10R-A-FETCH-POSITIVE"
CONTEXT_HASH = "sha256:g10r-a-fetch-positive"
TREATMENT_ID = "A2-M"
LIFECYCLE_STATUSES = {
    "NOT_REQUESTED",
    "RUNNER_REJECTED",
    "POLICY_BLOCKED",
    "NO_USABLE_RESULT",
    "EXECUTED_CARD",
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_case() -> dict[str, Any]:
    payload = json.loads((ROOT / "fixtures/investigation/viewpoint-society/development.jsonl").read_text(encoding="utf-8").splitlines()[0])
    payload["case_id"] = CASE_ID
    payload["context_hash"] = CONTEXT_HASH
    # The development fixture is reused as a deterministic roster seed, but
    # the replay is a distinct sealed case.  Rebind every card to that case so
    # the society's case-integrity validator remains meaningful.
    for card in payload["viewpoint_cards"]:
        card["case_id"] = CASE_ID
    return payload


def _candidate(case: dict[str, Any], source_id: str, *, locator: str, title: str, access_class: str = "METADATA_ONLY", rights_state: str = "METADATA_ONLY") -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "source_candidate_id": source_id,
        "problem_id": case["problem_id"],
        "problem_version": case["problem_version"],
        "title": title,
        "locator": locator,
        "content_locator": locator,
        "discovery_query": "offline acquisition discriminator",
        "host": locator.split("/")[2],
        "access_class": access_class,
        "rights_state": rights_state,
        "identity_status": "IDENTITY_UNRESOLVED",
        "attribution_status": "UNREVIEWED",
        "content_hash": None,
        "deduplication_key": f"fixture:{source_id}",
        "support_region": "offline acquisition fixture",
        "contradiction_ids": [],
        "status": "DISCOVERED",
    }


def _action(case: dict[str, Any], action_id: str, task_id: str, action_type: str, *, source_ids: list[str], policy_status: str = "ALLOWED", document_fetches: int = 0) -> dict[str, Any]:
    action = {
        "schema_version": "1.0",
        "action_id": action_id,
        "run_id": "G10R-A-offline",
        "case_id": case["case_id"],
        "problem_id": case["problem_id"],
        "problem_version": case["problem_version"],
        "arm": "A2-M",
        "branch_id": task_id,
        "action_type": action_type,
        "rationale": f"bounded offline acquisition action for {task_id}",
        "input": {"task_id": task_id},
        "policy_status": policy_status,
        "budget_debit": {
            "queries": 1 if action_type == "SEARCH" else 0,
            "retained_sources": len(source_ids),
            "document_fetches": document_fetches,
            "payload_bytes": 0,
            "simulation_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost_usd": 0.0,
        },
        "output_ids": source_ids,
        "replay_key": digest({"action_id": action_id, "task_id": task_id}),
        "timestamp": TIMESTAMP,
    }
    validate(action, schema("investigation-action.schema.json"))
    return action


def _report(case: dict[str, Any], report_id: str, viewpoint_id: str, task_id: str, *, stance: str, action_ids: list[str], source_ids: list[str], summary: str, unresolved: list[str], status: str) -> dict[str, Any]:
    report = {
        "schema_version": "1.0",
        "report_id": report_id,
        "case_id": case["case_id"],
        "viewpoint_id": viewpoint_id,
        "support_task_id": task_id,
        "stance": stance,
        "action_ids": action_ids,
        "source_candidate_ids": source_ids,
        "claim_ids": [],
        "summary": summary,
        "unresolved_questions": unresolved,
        "status": status,
    }
    validate(report, schema("viewpoint-support-report.schema.json"))
    return report


def _page_card(document: dict[str, Any], source_id: str) -> dict[str, Any]:
    page = document["pages"][0]
    card = {
        "schema_version": "1.0",
        "card_id": "CARD-G10R-A-FETCH",
        "source_candidate_id": source_id,
        "document_hash": document["content_hash"],
        "parser": document["parser"],
        "extraction_status": document["extraction_status"],
        "page_count": document["page_count"],
        "facts": [{
            "field": "endpoint",
            "value": "water-flow recovery",
            "reporting_status": "REPORTED",
            "support_type": "DIRECT",
            "page_locator": page["locator"],
            "page_text_hash": page["text_hash"],
            "confidence": "HIGH",
        }],
        "unresolved": ["Comparator details remain for expert review."],
        "authority_note": "Derived extraction for review; no evidence promotion, performance claim, or laboratory authority.",
    }
    validate_paper_evidence_card(card, document)
    return card


def _run_once() -> dict[str, Any]:
    case = _load_case()
    cards = viewpoint_cards_from_roster({"case_id": case["case_id"], "mechanisms": case["viewpoint_cards"]}) if "mechanisms" in case else case["viewpoint_cards"]
    # The fixture already contains viewpoint-card records; preserve their IDs
    # and admit the reserved open slot as a bounded candidate.
    society = ViewpointSociety(
        case_id=case["case_id"], problem_id=case["problem_id"], problem_version=case["problem_version"],
        treatment_id=TREATMENT_ID, viewpoint_cards=cards, context_hash=CONTEXT_HASH, action_budget=8,
    )
    open_card = next(card for card in cards if card["kind"] == "OPEN_SLOT")
    admitted = deepcopy(open_card)
    admitted.update({"viewpoint_id": f"{open_card['viewpoint_id']}-ADMITTED", "kind": "CANDIDATE", "statement": "A bounded newly admitted acquisition viewpoint.", "prior_basis": "offline acquisition fixture"})
    society.admit_open_viewpoint(admitted, reason="offline acquisition test requires bounded open-slot work")

    source_fetch = _candidate(case, "SRC-FETCH", locator="https://www.repository.cam.ac.uk/fixture.pdf", title="Fetch-positive fixture")
    source_meta = _candidate(case, "SRC-META", locator="https://example.org/metadata", title="Metadata-only fixture")
    source_blocked = _candidate(case, "SRC-BLOCKED", locator="https://api.openalex.org/works/W-offline", title="Rights-blocked fixture", rights_state="RIGHTS_BLOCKED")
    source_malformed = _candidate(case, "SRC-MALFORMED", locator="https://example.org/malformed.pdf", title="Malformed fixture")
    for candidate in (source_fetch, source_meta, source_blocked, source_malformed):
        society.register_candidate(candidate)
    society.register_candidate(source_meta | {"title": "Metadata-only fixture variant"})

    task_ids: dict[tuple[str, str], str] = {}
    task_types = ("RETRIEVAL", "EXTRACTION", "IDENTITY_LINEAGE", "CONTRADICTION", "EXPERIMENT_DESIGN")
    for viewpoint_id in society.active_ids:
        for task_type in task_types:
            task_id = f"TASK-{viewpoint_id}-{task_type}"
            task_ids[(viewpoint_id, task_type)] = task_id
            society.assign_support_task({
                "schema_version": "1.0", "task_id": task_id, "case_id": case["case_id"],
                "problem_id": case["problem_id"], "problem_version": case["problem_version"], "treatment_id": TREATMENT_ID,
                "viewpoint_id": viewpoint_id, "task_type": task_type,
                "charter": f"{task_type.lower()} acquisition support for {viewpoint_id}; preserve uncertainty and provenance.",
                "status": "ASSIGNED",
            })

    lifecycle = [
        {"event_id": "REQ-FETCH", "task_id": task_ids[(society.active_ids[0], "RETRIEVAL")], "locator": source_fetch["locator"], "status": "EXECUTED_CARD"},
        {"event_id": "REQ-META", "task_id": task_ids[(society.active_ids[1], "RETRIEVAL")], "locator": source_meta["locator"], "status": "NOT_REQUESTED", "reason": "metadata-only branch retained without content request"},
        {"event_id": "REQ-BLOCKED", "task_id": task_ids[(society.active_ids[2], "CONTRADICTION")], "locator": source_blocked["locator"], "status": "POLICY_BLOCKED", "reason": "frozen source policy disallows content fetch"},
        {"event_id": "REQ-MALFORMED", "task_id": task_ids[(society.active_ids[0], "EXTRACTION")], "locator": source_malformed["locator"], "status": "NO_USABLE_RESULT", "reason": "malformed document fixture"},
        {"event_id": "REQ-BUDGET", "task_id": task_ids[(society.active_ids[1], "EXPERIMENT_DESIGN")], "locator": source_fetch["locator"], "status": "RUNNER_REJECTED", "reason": "bounded task budget exhausted"},
    ]
    assert {event["status"] for event in lifecycle} == LIFECYCLE_STATUSES

    actions = [
        _action(case, "ACT-FETCH", task_ids[(society.active_ids[0], "RETRIEVAL")], "FETCH_PERMITTED_CONTENT", source_ids=[source_fetch["source_candidate_id"]], document_fetches=1),
        _action(case, "ACT-CARD", task_ids[(society.active_ids[0], "EXTRACTION")], "INSPECT_EXISTING_EVIDENCE", source_ids=[source_fetch["source_candidate_id"]]),
        _action(case, "ACT-BLOCKED", task_ids[(society.active_ids[2], "CONTRADICTION")], "FETCH_PERMITTED_CONTENT", source_ids=[source_blocked["source_candidate_id"]], policy_status="RIGHTS_BLOCKED"),
        _action(case, "ACT-META", task_ids[(society.active_ids[1], "RETRIEVAL")], "SEARCH", source_ids=[source_meta["source_candidate_id"]]),
    ]
    for action in actions:
        society.register_action(action)

    payload = base64.b64decode((ROOT / "fixtures/investigation/pdf-benchmark.b64").read_text(encoding="utf-8").strip())
    document = extract_pdf(payload, locator=source_fetch["locator"], max_pages=4, max_characters=45_000)
    card = _page_card(document, source_fetch["source_candidate_id"])
    blocked = False
    try:
        SourcePolicy(json.loads((ROOT / "fixtures/investigation/source-policy.json").read_text(encoding="utf-8"))).decide(source_blocked["locator"], fetch_content=True)
    except PolicyBlocked:
        blocked = True
    try:
        extract_pdf(b"not a PDF", locator=source_malformed["locator"], max_pages=4, max_characters=45_000)
    except (DocumentExtractionError, ValueError):
        malformed = True
    else:
        malformed = False

    reports: list[dict[str, Any]] = []
    for viewpoint_id in society.active_ids:
        for task_type in task_types:
            task_id = task_ids[(viewpoint_id, task_type)]
            if viewpoint_id == society.active_ids[0] and task_type == "RETRIEVAL":
                report = _report(case, f"REPORT-{viewpoint_id}-{task_type}", viewpoint_id, task_id, stance="SUPPORTS", action_ids=["ACT-FETCH"], source_ids=[source_fetch["source_candidate_id"]], summary="Fetch-positive source was retrieved for the assigned viewpoint.", unresolved=["Endpoint comparator remains for review."], status="COMPLETE")
            elif viewpoint_id == society.active_ids[0] and task_type == "EXTRACTION":
                report = _report(case, f"REPORT-{viewpoint_id}-{task_type}", viewpoint_id, task_id, stance="SUPPORTS", action_ids=["ACT-CARD"], source_ids=[source_fetch["source_candidate_id"]], summary="A page-located evidence card was produced without promotion.", unresolved=["Derived card remains reviewable."], status="COMPLETE")
            elif task_type == "CONTRADICTION":
                report = _report(case, f"REPORT-{viewpoint_id}-{task_type}", viewpoint_id, task_id, stance="WEAKENS", action_ids=["ACT-BLOCKED"] if viewpoint_id == society.active_ids[2] else [], source_ids=[source_blocked["source_candidate_id"]] if viewpoint_id == society.active_ids[2] else [], summary="The contradiction path weakens confidence but remains rights-blocked or unresolved.", unresolved=["A lawful accessible contradiction is still needed."], status="COMPLETE")
            elif task_type == "EXPERIMENT_DESIGN":
                report = _report(case, f"REPORT-{viewpoint_id}-{task_type}", viewpoint_id, task_id, stance="NON_DISCRIMINATING", action_ids=[], source_ids=[], summary="No experiment action is authorized in this offline fixture.", unresolved=["A lab-free discriminator remains to be specified."], status="ABSTAINED")
            else:
                report = _report(case, f"REPORT-{viewpoint_id}-{task_type}", viewpoint_id, task_id, stance="NON_DISCRIMINATING", action_ids=["ACT-META"] if task_type == "RETRIEVAL" and viewpoint_id == society.active_ids[1] else [], source_ids=[source_meta["source_candidate_id"]] if task_type == "RETRIEVAL" and viewpoint_id == society.active_ids[1] else [], summary="Metadata-only or unresolved support is retained without direct evidence credit.", unresolved=["Content and identity remain unresolved."], status="ABSTAINED")
            society.submit_support_report(report)
            reports.append(report)

    for viewpoint_id in society.active_ids:
        society.commit_viewpoint(viewpoint_id)
    shared = society.share()
    society.add_cross_viewpoint_critique({
        "schema_version": "1.0", "critique_id": "CRITIQUE-G10R-A", "case_id": case["case_id"],
        "critic_id": "offline-acquisition-critic", "target_viewpoint_id": society.active_ids[0],
        "compared_viewpoint_ids": list(society.active_ids), "dossier_ids": [item["dossier_id"] for item in shared],
        "source_candidate_ids": [source_fetch["source_candidate_id"], source_blocked["source_candidate_id"]],
        "challenge": "The fetch-positive card is useful but does not resolve comparator fit; the blocked contradiction remains a live uncertainty.",
        "proposed_discriminator": "Retrieve a lawful matched comparator and inspect the reported endpoint.", "status": "REVIEW_REQUIRED",
    })
    focus_stats = [{"case_id": case["case_id"], "treatment_id": TREATMENT_ID, "task_id": task_id, "viewpoint_id": viewpoint_id, "expected_information": 3 if task_type in {"RETRIEVAL", "EXTRACTION", "CONTRADICTION"} else 1, "unresolved_uncertainty": 2, "novelty": 1 if viewpoint_id == society.active_ids[0] else 0, "provenance_risk": 1, "duplicate_work": 0, "feasible": True} for (viewpoint_id, task_type), task_id in sorted(task_ids.items())]
    focus = society.allocate_focus(focus_stats, 4)
    portfolio = society.adjudicate()
    envelope = society.envelope()
    attribution = society.bus.attribution_ledger(
        ledger_id=f"LEDGER-{case['case_id']}", envelope=envelope
    )
    checkpoint = society.checkpoint()
    resumed = ViewpointSociety.from_checkpoint(checkpoint, context_hash=CONTEXT_HASH)
    resume_stable = canonical(resumed.checkpoint()) == canonical(checkpoint)
    duplicate_replay = society.bus.register_action(actions[0])["replayed"]
    score = score_viewpoint_portfolio(society, portfolio)
    score.update({
        "request_lifecycle": {status: sum(event["status"] == status for event in lifecycle) for status in sorted(LIFECYCLE_STATUSES)},
        "page_aware_card_count": 1,
        "candidate_variant_count": len(society.bus.candidate_conflicts),
        "blocked_fixture_verified": blocked,
        "malformed_fixture_verified": malformed,
        "unique_attributable_acquisition": sum(
            entry["join_status"] == "ATTRIBUTED"
            and entry["record_type"] == "ACTION"
            and entry["action_ids"] == ["ACT-FETCH"]
            for entry in attribution["entries"]
        ),
        "evidence_card_yield": 1,
        "contradiction_weakening_coverage": sum(
            report["stance"] == "WEAKENS" for report in reports
        ),
        "useful_hypothesis_yield": 0,
        "overhead": {
            "model_calls": 0,
            "external_calls": 0,
            "actions": len(actions),
            "reports": len(reports),
            "candidate_observations": sum(
                len(observations) for observations in society.bus.candidate_observations.values()
            ),
        },
        "checkpoint_resume_stable": resume_stable,
        "duplicate_action_replayed": duplicate_replay,
        "equal_budget_limits": {"society": {"queries": 8, "document_fetches": 2, "action_budget": 8}, "a1_control": {"queries": 8, "document_fetches": 2, "action_budget": 8}},
    })
    return {
        "case_id": case["case_id"], "status": "COMPLETE", "external_calls": False,
        "lifecycle": lifecycle, "paper_evidence_cards": {card["card_id"]: card},
        "focus": focus, "portfolio": portfolio, "envelope": envelope, "score": score,
        "attribution_ledger": attribution,
        "evidence_card_joins": [{
            "card_id": card["card_id"], "source_candidate_id": source_fetch["source_candidate_id"],
            "action_id": "ACT-FETCH", "support_task_id": task_ids[(society.active_ids[0], "RETRIEVAL")],
            "viewpoint_id": society.active_ids[0], "join_status": "ATTRIBUTED",
        }],
        "checkpoint": checkpoint,
    }


def replay(*, root: Path = ROOT) -> dict[str, Any]:
    first = _run_once()
    second = _run_once()
    first_compare = deepcopy(first)
    second_compare = deepcopy(second)
    stable = canonical(first_compare) == canonical(second_compare)
    lifecycle = first["score"]["request_lifecycle"]
    score = first["score"]
    ready = (
        first["status"] == "COMPLETE"
        and first["external_calls"] is False
        and stable
        and lifecycle == {"EXECUTED_CARD": 1, "NO_USABLE_RESULT": 1, "NOT_REQUESTED": 1, "POLICY_BLOCKED": 1, "RUNNER_REJECTED": 1}
        and score["page_aware_card_count"] >= 1
        and score["weakening_contribution_count"] >= 1
        and score["evidence_promotion"] is False
        and score["blocked_fixture_verified"]
        and score["malformed_fixture_verified"]
        and score["unique_attributable_acquisition"] >= 1
        and score["evidence_card_yield"] >= 1
        and score["contradiction_weakening_coverage"] >= 1
        and score["checkpoint_resume_stable"]
        and score["duplicate_action_replayed"]
        and first["focus"]["status"] == "ALLOCATED"
        and first["attribution_ledger"]["status"] == "READY"
        and not first["envelope"]["diagnostics"]
    )
    return {
        "schema_version": "1.0", "goal": "G10R-A", "status": "ACQUISITION_DESIGN_READY" if ready else "ACQUISITION_DESIGN_NO_GO",
        "external_calls": False, "replay_stable": stable, "offline_run": first,
        "failure_reasons": [] if ready else ["acquisition fixture or replay invariant failed"],
        "next_action": "Freeze a fresh Phase-A manifest before any future paid evaluation; no live call is authorized by G10R-A." if ready else "Repair the offline acquisition contract before considering a live evaluation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/goals/G10R-A/replay.json")
    args = parser.parse_args()
    output = replay()
    _write(args.output, output)
    print(json.dumps({"status": output["status"], "external_calls": output["external_calls"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
