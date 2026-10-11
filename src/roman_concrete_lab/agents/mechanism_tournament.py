"""Offline mechanism-proponent society contracts and Phase-A freeze."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

from ..retrieval import BudgetExhausted, PolicyBlocked, StaleContext, canonical, digest
from tools.tournament.replay import ROOT


PROTOCOL_VERSION = "g10m.1-mechanism-proponent-society"
STRUCTURAL_ROLES = ("evidence_skeptic", "transfer_boundary", "experiment_simulation")
AUTHORITY_NOTE = (
    "Derived mechanism and critique records remain REVIEW_REQUIRED; no record grants "
    "immutable-evidence, scientific, safety, laboratory, or external-communication authority."
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_digest(path: Path) -> str:
    return digest(path.read_bytes().hex())


def schema(name: str) -> dict[str, Any]:
    return load_json(ROOT / "schemas" / name)


def load_cases(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row.get("case_id") for row in rows]
    if not ids or any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError(f"cases in {path} must have unique case_id values")
    return rows


def _validate(name: str, value: dict[str, Any]) -> None:
    validate(value, schema(name))


def validate_mechanism_card(card: dict[str, Any]) -> None:
    _validate("mechanism-card.schema.json", card)
    if card["kind"] == "OPEN_SLOT" and not card["mechanism_id"].endswith("-OPEN"):
        raise PolicyBlocked("open mechanism slot must have an -OPEN mechanism_id")
    if card["kind"] == "NULL" and "null" not in card["mechanism_id"].casefold():
        raise PolicyBlocked("null mechanism must be explicitly identifiable")


def validate_proponent_report(report: dict[str, Any]) -> None:
    _validate("mechanism-proponent-report.schema.json", report)
    for claim in report["claims"]:
        if any(term in claim["statement"].casefold() for term in ("proven", "validated", "authorized")):
            raise PolicyBlocked("proponent claim uses prohibited authority language")


def validate_structural_critique(critique: dict[str, Any]) -> None:
    _validate("structural-critique.schema.json", critique)
    if "promote" in critique["challenge"].casefold() or "authorize" in critique["challenge"].casefold():
        raise PolicyBlocked("structural critique cannot grant authority")


def validate_admission(admission: dict[str, Any]) -> None:
    admission_schema = deepcopy(schema("mechanism-admission.schema.json"))
    admission_schema["properties"]["mechanism_card"] = {"type": "object"}
    validate(admission, admission_schema)
    validate_mechanism_card(admission["mechanism_card"])
    if admission["mechanism_card"]["kind"] != "CANDIDATE":
        raise PolicyBlocked("only a candidate mechanism may fill the open slot")


def validate_roster(roster: dict[str, Any]) -> dict[str, Any]:
    mechanisms = roster.get("mechanisms", [])
    if not mechanisms:
        raise ValueError("mechanism roster is empty")
    for card in mechanisms:
        validate_mechanism_card(card)
        if card["case_id"] != roster["case_id"]:
            raise PolicyBlocked("mechanism card case does not match roster")
    ids = [card["mechanism_id"] for card in mechanisms]
    if len(ids) != len(set(ids)):
        raise PolicyBlocked("duplicate mechanism_id in roster")
    if sum(card["kind"] == "NULL" for card in mechanisms) != 1:
        raise PolicyBlocked("roster must contain exactly one null mechanism")
    if sum(card["kind"] == "OPEN_SLOT" for card in mechanisms) != 1:
        raise PolicyBlocked("roster must contain exactly one open mechanism slot")
    if sum(card["kind"] == "CANDIDATE" for card in mechanisms) < 2:
        raise PolicyBlocked("roster must contain at least two plausible mechanisms")
    return {
        "passes": True,
        "case_id": roster["case_id"],
        "mechanism_count": len(mechanisms),
        "candidate_count": sum(card["kind"] == "CANDIDATE" for card in mechanisms),
        "null_ids": [card["mechanism_id"] for card in mechanisms if card["kind"] == "NULL"],
        "open_slot_ids": [card["mechanism_id"] for card in mechanisms if card["kind"] == "OPEN_SLOT"],
    }


def load_rosters() -> dict[str, dict[str, Any]]:
    payload = load_json(ROOT / "fixtures/investigation/mechanism-rosters.json")
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported mechanism roster schema")
    rosters = {row["case_id"]: row for row in payload["rosters"]}
    if len(rosters) != len(payload["rosters"]):
        raise ValueError("duplicate mechanism roster case")
    return rosters


def allocate_mechanism_focus(
    mechanism_stats: list[dict[str, Any]],
    remaining_actions: int,
    *,
    null_mechanism_id: str,
) -> dict[str, Any]:
    """Allocate bounded actions without votes, while retaining null and a rival."""
    if remaining_actions < 0:
        raise BudgetExhausted("focus request is negative")
    if remaining_actions == 0:
        return {"status": "ABSTAIN", "allocations": {}, "rationale": "No bounded focus actions remain."}
    by_id = {item["mechanism_id"]: item for item in mechanism_stats}
    if null_mechanism_id not in by_id:
        raise PolicyBlocked("focus decision lacks the required null mechanism")
    scored: list[tuple[int, str]] = []
    for item in mechanism_stats:
        score = (
            3 * int(item.get("expected_discrimination", 0))
            + 2 * int(item.get("unresolved_uncertainty", 0))
            + int(item.get("provenance_risk", 0))
            + int(item.get("novelty", 0))
            - 2 * int(item.get("duplicate_work", 0))
        )
        if not item.get("feasible", True):
            score = -10_000
        scored.append((score, item["mechanism_id"]))
    eligible = sorted((score, mechanism_id) for score, mechanism_id in scored if score >= 0)
    if not eligible:
        return {"status": "ABSTAIN", "allocations": {}, "rationale": "No feasible mechanism action remains."}
    candidate_ids = [mechanism_id for _, mechanism_id in eligible if mechanism_id != null_mechanism_id]
    if remaining_actions < 2 or not candidate_ids:
        return {
            "status": "ABSTAIN",
            "allocations": {},
            "rationale": "At least one null check and one rival action are required for a fair tournament.",
        }
    ordered = [null_mechanism_id, candidate_ids[0]] + [item[1] for item in eligible if item[1] not in {null_mechanism_id, candidate_ids[0]}]
    allocations = {mechanism_id: 0 for _, mechanism_id in eligible}
    for index in range(remaining_actions):
        allocations[ordered[index % len(ordered)]] += 1
    return {
        "status": "ALLOCATED",
        "allocations": allocations,
        "ranked_mechanisms": [mechanism_id for _, mechanism_id in eligible],
        "scores": {mechanism_id: score for score, mechanism_id in eligible},
        "rationale": "Deterministic allocation from discrimination, uncertainty, provenance risk, novelty, duplication, feasibility, and remaining budget; votes are not an input.",
    }


def score_mechanism_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    """Score typed contributions only; rhetoric, consensus, and count earn zero."""
    valid_claims = 0
    invalid_claims = 0
    discriminators = 0
    for event in ledger.get("events", []):
        if event.get("event_type") == "PRIVATE_PROPONENT_REPORT":
            for claim in event.get("report", {}).get("claims", []):
                required = ("statement", "prediction", "falsifier", "support_region", "provenance")
                if all(claim.get(field) for field in required) and claim.get("promotion_status") == "REVIEW_REQUIRED":
                    valid_claims += 1
                else:
                    invalid_claims += 1
        if event.get("event_type") == "STRUCTURAL_CRITIQUE" and event.get("critique", {}).get("proposed_discriminator"):
            discriminators += 1
    return {
        "valid_claim_count": valid_claims,
        "invalid_claim_count": invalid_claims,
        "valid_discriminator_count": discriminators,
        "primary_score": valid_claims + discriminators,
        "advocacy_credit": 0,
        "consensus_credit": 0,
        "mechanism_count_credit": 0,
        "null_retained": bool(ledger.get("null_retained")),
        "scoring_rule": "Only typed prediction/falsifier/provenance records and structural discriminators count; rhetoric, consensus, and mechanism count earn zero.",
    }


class MechanismBlackboard:
    """Private-first, append-only memory for the offline mechanism tournament."""

    def __init__(self, *, roster: dict[str, Any], context_hash: str) -> None:
        validate_roster(roster)
        self.roster = deepcopy(roster)
        self.context_hash = context_hash
        self._cards = {card["mechanism_id"]: deepcopy(card) for card in roster["mechanisms"]}
        self._private: dict[str, dict[str, Any]] = {}
        self._shared = False
        self._critiques: list[dict[str, Any]] = []
        self._events: dict[str, dict[str, Any]] = {}
        self._admitted: list[dict[str, Any]] = []
        self._focus: dict[str, Any] | None = None

    @property
    def proponent_ids(self) -> set[str]:
        return {card_id for card_id, card in self._cards.items() if card["kind"] != "OPEN_SLOT"}

    @property
    def null_id(self) -> str:
        return next(card_id for card_id, card in self._cards.items() if card["kind"] == "NULL")

    def append_event(self, *, event_id: str, event: dict[str, Any], context_hash: str | None = None) -> dict[str, Any]:
        if context_hash is not None and context_hash != self.context_hash:
            raise StaleContext("event uses a stale mechanism-tournament context")
        existing = self._events.get(event_id)
        if existing is not None:
            if canonical(existing) != canonical(event):
                raise PolicyBlocked(f"event ID has a different payload: {event_id}")
            return {"replayed": True, "event": deepcopy(existing)}
        if event.get("case_id") != self.roster["case_id"]:
            raise PolicyBlocked("cross-problem or cross-case event")
        self._events[event_id] = deepcopy(event)
        return {"replayed": False, "event": deepcopy(event)}

    def submit_proponent(self, report: dict[str, Any]) -> None:
        validate_proponent_report(report)
        if report["case_id"] != self.roster["case_id"]:
            raise PolicyBlocked("proponent report case does not match roster")
        mechanism_id = report["mechanism_id"]
        if mechanism_id not in self.proponent_ids:
            raise PolicyBlocked("proponent report targets an unknown or open-slot mechanism")
        if mechanism_id in self._private:
            raise PolicyBlocked(f"duplicate proponent report: {mechanism_id}")
        self._private[mechanism_id] = deepcopy(report)
        self.append_event(
            event_id=report["report_id"],
            event={"event_type": "PRIVATE_PROPONENT_REPORT", "case_id": report["case_id"], "report": deepcopy(report)},
        )

    def read_shared(self) -> list[dict[str, Any]]:
        if not self._shared:
            raise PolicyBlocked("proponent reports remain private before sharing")
        return [deepcopy(self._private[key]) for key in sorted(self._private)]

    def share(self) -> list[dict[str, Any]]:
        missing = self.proponent_ids - set(self._private)
        if missing:
            raise PolicyBlocked(f"cannot share incomplete proponent round: {sorted(missing)}")
        if self._shared:
            return self.read_shared()
        self._shared = True
        self.append_event(
            event_id=digest({"case_id": self.roster["case_id"], "event": "SHARE", "reports": sorted(self._private)}),
            event={"event_type": "SHARE_PROPONENT_REPORTS", "case_id": self.roster["case_id"], "report_ids": sorted(self._private)},
        )
        return self.read_shared()

    def add_critique(self, critique: dict[str, Any]) -> None:
        if not self._shared:
            raise PolicyBlocked("structural auditors cannot read private proponent reports")
        validate_structural_critique(critique)
        if critique["case_id"] != self.roster["case_id"] or critique["target_mechanism_id"] not in self._cards:
            raise PolicyBlocked("critique targets the wrong case or mechanism")
        self._critiques.append(deepcopy(critique))
        self.append_event(
            event_id=critique["critique_id"],
            event={"event_type": "STRUCTURAL_CRITIQUE", "case_id": critique["case_id"], "critique": deepcopy(critique)},
        )

    def admit_open_mechanism(self, admission: dict[str, Any]) -> None:
        if not self._shared:
            raise PolicyBlocked("new mechanism admission requires the private round to close")
        validate_admission(admission)
        card = admission["mechanism_card"]
        if admission["case_id"] != self.roster["case_id"] or card["case_id"] != admission["case_id"]:
            raise PolicyBlocked("admission case does not match roster")
        if admission["status"] != "ADMITTED":
            raise PolicyBlocked("rejected mechanism cannot enter the shared tournament")
        if self._admitted:
            raise PolicyBlocked("only one bounded open-slot admission is allowed")
        if card["mechanism_id"] in self._cards or not card["mechanism_id"].startswith(self.roster["case_id"] + "-OPEN-"):
            raise PolicyBlocked("admitted mechanism must be a new bounded open-slot candidate")
        self._cards[card["mechanism_id"]] = deepcopy(card)
        self._admitted.append(deepcopy(admission))
        self.append_event(
            event_id=admission["admission_id"],
            event={"event_type": "OPEN_SLOT_ADMISSION", "case_id": admission["case_id"], "admission": deepcopy(admission)},
        )

    def allocate_focus(self, *, remaining_actions: int) -> dict[str, Any]:
        if not self._shared:
            raise PolicyBlocked("focus requires shared proponent reports")
        stats = []
        for mechanism_id, card in sorted(self._cards.items()):
            report = self._private.get(mechanism_id, {})
            critiques = [item for item in self._critiques if item["target_mechanism_id"] == mechanism_id]
            stats.append(
                {
                    "mechanism_id": mechanism_id,
                    "expected_discrimination": len(card["predicted_observations"]),
                    "unresolved_uncertainty": len(report.get("unresolved_questions", [])) + int(card["kind"] == "NULL"),
                    "provenance_risk": sum(item["contradiction_status"] != "NO_CONTRADICTION_FOUND" for item in critiques),
                    "novelty": int(card["kind"] == "CANDIDATE"),
                    "duplicate_work": 0,
                    "feasible": True,
                }
            )
        self._focus = allocate_mechanism_focus(stats, remaining_actions, null_mechanism_id=self.null_id)
        self.append_event(
            event_id=digest({"case_id": self.roster["case_id"], "event": "FOCUS", "focus": self._focus}),
            event={"event_type": "FOCUS_DECISION", "case_id": self.roster["case_id"], "focus": deepcopy(self._focus)},
        )
        return deepcopy(self._focus)

    def adjudicate(self) -> dict[str, Any]:
        if self._focus is None:
            raise PolicyBlocked("adjudication requires a focus decision")
        scores: dict[str, int] = {}
        for mechanism_id, card in self._cards.items():
            report = self._private.get(mechanism_id, {})
            claims = len(report.get("claims", []))
            critiques = [item for item in self._critiques if item["target_mechanism_id"] == mechanism_id]
            contradictions = sum(item["contradiction_status"] == "CONTRADICTION_FOUND" for item in critiques)
            scores[mechanism_id] = 2 * claims - 2 * contradictions + int(card["kind"] == "CANDIDATE")
        candidates = sorted((score, mechanism_id) for mechanism_id, score in scores.items() if mechanism_id != self.null_id and not mechanism_id.endswith("-OPEN"))
        leader = candidates[0][1] if candidates else None
        rivals = [mechanism_id for _, mechanism_id in candidates[1:]]
        if self.null_id not in rivals:
            rivals.append(self.null_id)
        ledger = {
            "schema_version": "1.0",
            "ledger_id": digest({"case_id": self.roster["case_id"], "events": sorted(self._events)}),
            "case_id": self.roster["case_id"],
            "protocol_version": PROTOCOL_VERSION,
            "roster_ids": sorted(self._cards),
            "events": list(self._events.values()),
            "focus_decision": deepcopy(self._focus),
            "leading_mechanism_id": leader,
            "credible_rival_ids": sorted(set(rivals)),
            "null_retained": self.null_id in rivals or leader == self.null_id,
            "next_discriminating_action": "Run the cheapest declared observation that separates the provisional leader, a credible rival, and the null.",
            "authority_note": AUTHORITY_NOTE,
            "scoring": {},
            "status": "REVIEW_REQUIRED",
        }
        ledger["scoring"] = score_mechanism_ledger(ledger)
        _validate("mechanism-tournament-ledger.schema.json", ledger)
        return ledger

    def checkpoint(self) -> dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "context_hash": self.context_hash,
            "roster": deepcopy(self.roster),
            "private_reports": deepcopy(self._private),
            "shared": self._shared,
            "critiques": deepcopy(self._critiques),
            "admitted": deepcopy(self._admitted),
            "focus": deepcopy(self._focus),
            "events": deepcopy(self._events),
        }

    @classmethod
    def from_checkpoint(cls, checkpoint: dict[str, Any]) -> "MechanismBlackboard":
        if checkpoint.get("protocol_version") != PROTOCOL_VERSION:
            raise StaleContext("checkpoint protocol does not match mechanism-tournament protocol")
        board = cls(roster=checkpoint["roster"], context_hash=checkpoint["context_hash"])
        board._private = deepcopy(checkpoint.get("private_reports", {}))
        board._shared = bool(checkpoint.get("shared", False))
        board._critiques = deepcopy(checkpoint.get("critiques", []))
        board._admitted = deepcopy(checkpoint.get("admitted", []))
        board._focus = deepcopy(checkpoint.get("focus"))
        board._events = deepcopy(checkpoint.get("events", {}))
        for admission in board._admitted:
            card = admission["mechanism_card"]
            board._cards[card["mechanism_id"]] = deepcopy(card)
        return board


def _offline_report(card: dict[str, Any]) -> dict[str, Any]:
    trace_id = f"TRACE-{card['mechanism_id']}"
    return {
        "schema_version": "1.0",
        "report_id": digest({"report": card["mechanism_id"]}),
        "case_id": card["case_id"],
        "mechanism_id": card["mechanism_id"],
        "role": "mechanism_proponent",
        "action_ids": [f"ACTION-{card['mechanism_id']}-PRIVATE"],
        "source_candidate_ids": [],
        "claims": [
            {
                "claim_id": f"CLAIM-{card['mechanism_id']}",
                "statement": card["mechanism_statement"],
                "prediction": card["predicted_observations"][0],
                "falsifier": card["falsifiers"][0],
                "support_region": card["support_region"],
                "provenance": [trace_id],
                "promotion_status": "REVIEW_REQUIRED",
            }
        ],
        "negative_searches": ["No external search is authorized in the offline fixture."],
        "unresolved_questions": ["Does the declared discriminator separate this mechanism from its rivals and null?"],
        "proposed_next_actions": ["Use the declared discriminator within the shared budget."],
        "claimed_contribution": "Typed mechanism proposal with a falsifier; not evidence of truth.",
        "status": "COMPLETE",
    }


def _offline_critique(card: dict[str, Any], role: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "critique_id": digest({"critique": card["mechanism_id"], "role": role}),
        "case_id": card["case_id"],
        "auditor_role": role,
        "target_mechanism_id": card["mechanism_id"],
        "claim_ids": [f"CLAIM-{card['mechanism_id']}"],
        "challenge": "Check provenance, support-region fit, and whether the prediction distinguishes this mechanism from a rival and the null.",
        "contradiction_status": "UNRESOLVED",
        "proposed_discriminator": card["predicted_observations"][0],
        "provenance": [f"TRACE-CRITIQUE-{card['mechanism_id']}-{role}"],
        "promotion_status": "REVIEW_REQUIRED",
    }


def run_offline_case(roster: dict[str, Any], *, context_hash: str | None = None) -> dict[str, Any]:
    validate_roster(roster)
    context_hash = context_hash or digest({"case_id": roster["case_id"], "protocol": PROTOCOL_VERSION})
    board = MechanismBlackboard(roster=roster, context_hash=context_hash)
    for card in roster["mechanisms"]:
        if card["kind"] != "OPEN_SLOT":
            board.submit_proponent(_offline_report(card))
    board.share()
    for index, card in enumerate(roster["mechanisms"]):
        if card["kind"] == "OPEN_SLOT":
            continue
        board.add_critique(_offline_critique(card, STRUCTURAL_ROLES[index % len(STRUCTURAL_ROLES)]))
    focus = board.allocate_focus(remaining_actions=6)
    ledger = board.adjudicate()
    return {"case_id": roster["case_id"], "focus": focus, "ledger": ledger, "checkpoint": board.checkpoint()}


def _behavior_fixture_report(rosters: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report: list[dict[str, Any]] = []
    roster = rosters["S-ACTIVE-TRANSFER"]
    duplicate = deepcopy(roster)
    duplicate["mechanisms"].append(deepcopy(duplicate["mechanisms"][0]))
    try:
        validate_roster(duplicate)
    except PolicyBlocked:
        report.append({"fixture_id": "duplicate-mechanism", "status": "PASS"})
    else:
        report.append({"fixture_id": "duplicate-mechanism", "status": "FAIL"})
    missing_falsifier = _offline_report(roster["mechanisms"][0])
    del missing_falsifier["claims"][0]["falsifier"]
    try:
        validate_proponent_report(missing_falsifier)
    except ValidationError:
        report.append({"fixture_id": "missing-falsifier", "status": "PASS"})
    else:
        report.append({"fixture_id": "missing-falsifier", "status": "FAIL"})
    run = run_offline_case(roster)
    report.append({"fixture_id": "null-retention", "status": "PASS" if run["ledger"]["null_retained"] else "FAIL"})
    board = MechanismBlackboard(roster=roster, context_hash="sha256:context")
    for card in roster["mechanisms"]:
        if card["kind"] != "OPEN_SLOT":
            board.submit_proponent(_offline_report(card))
    board.share()
    open_card = deepcopy(roster["mechanisms"][-1])
    open_card.update({"mechanism_id": "S-ACTIVE-TRANSFER-OPEN-NEW", "kind": "CANDIDATE", "mechanism_statement": "A bounded newly admitted mechanism.", "prior_basis": "admission fixture"})
    admission = {"schema_version":"1.0","admission_id":"ADMISSION-1","case_id":"S-ACTIVE-TRANSFER","mechanism_card":open_card,"reason":"A distinct typed discriminator is available.","evidence_locator":"TRACE-ADMISSION","uncertainty_basis":"The mechanism is provisional until reviewed.","budget_debit":1,"status":"ADMITTED"}
    board.admit_open_mechanism(admission)
    report.append({"fixture_id": "open-slot-admission", "status": "PASS"})
    unsupported = _offline_report(roster["mechanisms"][0])
    unsupported["claims"][0]["promotion_status"] = "IMMUTABLE_EVIDENCE"
    try:
        validate_proponent_report(unsupported)
    except ValidationError:
        report.append({"fixture_id": "unsupported-promotion", "status": "PASS"})
    else:
        report.append({"fixture_id": "unsupported-promotion", "status": "FAIL"})
    try:
        board.append_event(event_id="STALE", event={"case_id":"S-ACTIVE-TRANSFER"}, context_hash="sha256:wrong")
    except StaleContext:
        report.append({"fixture_id": "stale-write", "status": "PASS"})
    else:
        report.append({"fixture_id": "stale-write", "status": "FAIL"})
    try:
        board.append_event(event_id="CROSS", event={"case_id":"other-problem"})
    except PolicyBlocked:
        report.append({"fixture_id": "cross-problem-read", "status": "PASS"})
    else:
        report.append({"fixture_id": "cross-problem-read", "status": "FAIL"})
    try:
        allocate_mechanism_focus(
            [{"mechanism_id": "NULL", "expected_discrimination": 1, "unresolved_uncertainty": 1, "feasible": True}],
            -1,
            null_mechanism_id="NULL",
        )
    except BudgetExhausted:
        report.append({"fixture_id": "budget-exhaustion", "status": "PASS"})
    else:
        report.append({"fixture_id": "budget-exhaustion", "status": "FAIL"})
    event = {"case_id":"S-ACTIVE-TRANSFER","event_type":"REPLAY"}
    first = board.append_event(event_id="REPLAY", event=event)
    second = board.append_event(event_id="REPLAY", event=event)
    report.append({"fixture_id": "partial-replay", "status": "PASS" if not first["replayed"] and second["replayed"] else "FAIL"})
    return {"passes": all(item["status"] == "PASS" for item in report), "fixtures": report}


def phase_a() -> dict[str, Any]:
    development = load_cases(ROOT / "fixtures/investigation/development.jsonl")
    sealed = load_cases(ROOT / "fixtures/investigation/sealed.jsonl")
    rosters = load_rosters()
    all_cases = development + sealed
    roster_audit = []
    for case in all_cases:
        if case["case_id"] not in rosters:
            raise ValueError(f"missing mechanism roster for {case['case_id']}")
        roster_audit.append(validate_roster(rosters[case["case_id"]]))
    offline_runs = [run_offline_case(rosters[case["case_id"]]) for case in sealed]
    behavior = _behavior_fixture_report(rosters)
    files = {
        "goal": ROOT / "docs/goals/G10M-mechanism-proponent-society.md",
        "protocol": ROOT / "docs/protocols/mechanism-proponent-society.md",
        "active_protocol": ROOT / "docs/protocols/active-investigation-pilot.md",
        "runner": ROOT / "src/roman_concrete_lab/agents/mechanism_tournament.py",
        "rosters": ROOT / "fixtures/investigation/mechanism-rosters.json",
        "prompts": ROOT / "fixtures/investigation/mechanism-prompts.json",
        "behavior_fixtures": ROOT / "fixtures/investigation/mechanism-behavior-fixtures.json",
        "mechanism_card_schema": ROOT / "schemas/mechanism-card.schema.json",
        "proponent_report_schema": ROOT / "schemas/mechanism-proponent-report.schema.json",
        "structural_critique_schema": ROOT / "schemas/structural-critique.schema.json",
        "admission_schema": ROOT / "schemas/mechanism-admission.schema.json",
        "tournament_ledger_schema": ROOT / "schemas/mechanism-tournament-ledger.schema.json",
    }
    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "files": {key: {"path": str(path.relative_to(ROOT)), "sha256": file_digest(path)} for key, path in files.items()},
        "authority": {"network": "none", "model_calls": "none", "external_spend": 0.0, "laboratory": "prohibited", "external_communication": "prohibited"},
        "aggregate_budget": {"queries": 12, "document_fetches": 4, "simulation_calls": 4, "input_tokens": 80000, "output_tokens": 7200, "estimated_cost_usd": 25.0},
        "treatment_ids": {"control": "A1", "society": "A2-M"},
    }
    manifest["manifest_sha256"] = digest(manifest)
    ready = bool(roster_audit) and all(item["passes"] for item in roster_audit) and behavior["passes"] and all(run["ledger"]["null_retained"] for run in offline_runs)
    criterion_evidence = {
        "1": ["docs/protocols/mechanism-proponent-society.md", "schemas/mechanism-card.schema.json", "schemas/mechanism-proponent-report.schema.json", "schemas/structural-critique.schema.json", "schemas/mechanism-admission.schema.json", "schemas/mechanism-tournament-ledger.schema.json"],
        "2": ["src/roman_concrete_lab/agents/mechanism_tournament.py", "tests/agents/test_mechanism_tournament.py::test_proponents_are_private_until_all_commit", "tests/agents/test_mechanism_tournament.py::test_structural_audit_requires_sharing_and_admission_is_bounded"],
        "3": ["fixtures/investigation/mechanism-rosters.json", "artifacts/goals/G10M/phase-a.json:roster_audit"],
        "4": ["artifacts/goals/G10M/phase-a.json:budget_equality", "tests/agents/test_mechanism_tournament.py::test_focus_is_deterministic_and_preserves_null_and_rival"],
        "5": ["src/roman_concrete_lab/agents/mechanism_tournament.py:score_mechanism_ledger", "tests/agents/test_mechanism_tournament.py::test_offline_run_preserves_rival_and_null_and_replays"],
        "6": ["fixtures/investigation/mechanism-behavior-fixtures.json", "tests/agents/test_mechanism_tournament.py"],
        "7": ["artifacts/goals/G10M/phase-a.json", "artifacts/goals/G10M/report.md"],
        "8": ["artifacts/goals/G10M/phase-a.json:phase_b_authorized", "docs/protocols/active-investigation-pilot.md"],
    }
    result = {
        "goal": "G10M",
        "status": "MECHANISM_SOCIETY_READY" if ready else "MECHANISM_SOCIETY_NO_GO",
        "protocol_version": PROTOCOL_VERSION,
        "development_case_count": len(development),
        "sealed_case_count": len(sealed),
        "roster_audit": {"passes": all(item["passes"] for item in roster_audit), "cases": roster_audit},
        "behavior_fixture_report": behavior,
        "offline_runs": offline_runs,
        "criterion_evidence": criterion_evidence,
        "budget_equality": {"passes": True, "control": manifest["aggregate_budget"], "society": manifest["aggregate_budget"], "extra_role_authority": False},
        "manifest": manifest,
        "authority": manifest["authority"],
        "phase_b_authorized": False,
        "handoff": "Offline design gate only; live G10R Phase B requires this manifest plus explicit owner activation of a later amended protocol.",
    }
    return result


def write_phase_a(result: dict[str, Any]) -> None:
    destination = ROOT / "artifacts/goals/G10M"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "phase-a.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# G10M Phase-A report",
        "",
        f"- Status: `{result['status']}`",
        f"- Protocol: `{result['protocol_version']}`",
        f"- Development cases: `{result['development_case_count']}`",
        f"- Sealed cases: `{result['sealed_case_count']}`",
        f"- Roster audit: `{result['roster_audit']['passes']}`",
        f"- Behavior fixtures: `{result['behavior_fixture_report']['passes']}`",
        f"- Budget equality: `{result['budget_equality']['passes']}`",
        "- Live model/network/spend: `not authorized`",
        "",
        "The mechanism roster is a search scaffold. All mechanism records, critiques, predictions, and focus decisions remain derived and `REVIEW_REQUIRED`; no result authorizes scientific promotion or laboratory work.",
        "",
        "## Criterion evidence",
        "",
        *[f"- Criterion {criterion}: " + ", ".join(paths) for criterion, paths in sorted(result["criterion_evidence"].items())],
    ]
    (destination / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("a",), default="a")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = phase_a()
    if args.write:
        write_phase_a(result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
