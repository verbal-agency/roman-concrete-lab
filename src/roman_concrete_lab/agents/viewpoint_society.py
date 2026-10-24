"""Deterministic, offline viewpoint-centered society design.

Viewpoint agents own competing arguments.  Structural support tasks are
assigned beneath those viewpoints and may strengthen, weaken, or fail to
discriminate for the argument.  This module exercises the topology without
providers, network access, or scientific authority.
"""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from jsonschema import validate

from ..retrieval import BudgetExhausted, PolicyBlocked, StaleContext, canonical, digest
from .evidence_bus import EvidenceBus
from tools.tournament.replay import ROOT


PROTOCOL_VERSION = "g10d.1-viewpoint-centered-society"
TASK_TYPES = {"RETRIEVAL", "EXTRACTION", "IDENTITY_LINEAGE", "CONTRADICTION", "EXPERIMENT_DESIGN", "SIMULATION", "ADVERSARIAL_REVIEW"}


def _schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _validate(name: str, value: dict[str, Any]) -> None:
    validate(value, _schema(name))


def load_rosters() -> dict[str, dict[str, Any]]:
    """Load the frozen mechanism cards used as viewpoint-card inputs."""
    payload = json.loads((ROOT / "fixtures/investigation/mechanism-rosters.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("unsupported mechanism roster schema")
    rosters = {row["case_id"]: row for row in payload["rosters"]}
    if len(rosters) != len(payload["rosters"]):
        raise ValueError("duplicate mechanism roster case")
    return rosters


def validate_roster(roster: dict[str, Any]) -> dict[str, Any]:
    """Validate the frozen roster without importing the legacy tournament."""
    mechanisms = roster.get("mechanisms", [])
    if not mechanisms:
        raise ValueError("mechanism roster is empty")
    for card in mechanisms:
        _validate("mechanism-card.schema.json", card)
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


def viewpoint_cards_from_roster(roster: dict[str, Any]) -> list[dict[str, Any]]:
    """Translate frozen mechanism cards into the G10D viewpoint contract."""
    cards = []
    for mechanism in roster["mechanisms"]:
        cards.append({
            "schema_version": "1.0",
            "case_id": mechanism["case_id"],
            "viewpoint_id": mechanism["mechanism_id"],
            "kind": mechanism["kind"],
            "statement": mechanism["mechanism_statement"],
            "support_region": mechanism["support_region"],
            "prior_basis": mechanism["prior_basis"],
            "predictions": mechanism["predicted_observations"],
            "falsifiers": mechanism["falsifiers"],
            "known_alternatives": mechanism["known_alternatives"],
            "promotion_status": "REVIEW_REQUIRED",
        })
    return cards


def validate_viewpoint_card(card: dict[str, Any], *, case_id: str) -> None:
    _validate("viewpoint-card.schema.json", card)
    if card["case_id"] != case_id:
        raise PolicyBlocked("viewpoint card does not match the active case")
    if card["kind"] == "NULL" and "null" not in card["viewpoint_id"].casefold():
        raise PolicyBlocked("null viewpoint must be explicitly identifiable")
    if card["kind"] == "OPEN_SLOT" and not card["viewpoint_id"].endswith("-OPEN"):
        raise PolicyBlocked("open viewpoint slot must end with -OPEN")


def validate_viewpoint_roster(cards: list[dict[str, Any]], *, case_id: str) -> dict[str, Any]:
    if not cards:
        raise PolicyBlocked("viewpoint roster is empty")
    for card in cards:
        validate_viewpoint_card(card, case_id=case_id)
    ids = [card["viewpoint_id"] for card in cards]
    if len(ids) != len(set(ids)):
        raise PolicyBlocked("viewpoint roster contains duplicate IDs")
    if sum(card["kind"] == "NULL" for card in cards) != 1:
        raise PolicyBlocked("viewpoint roster must contain exactly one null")
    if sum(card["kind"] == "OPEN_SLOT" for card in cards) != 1:
        raise PolicyBlocked("viewpoint roster must contain exactly one open slot")
    if sum(card["kind"] == "CANDIDATE" for card in cards) < 2:
        raise PolicyBlocked("viewpoint roster must contain at least two candidate viewpoints")
    return {
        "passes": True,
        "case_id": case_id,
        "viewpoint_count": len(cards),
        "active_count": sum(card["kind"] != "OPEN_SLOT" for card in cards),
        "candidate_count": sum(card["kind"] == "CANDIDATE" for card in cards),
        "null_ids": [card["viewpoint_id"] for card in cards if card["kind"] == "NULL"],
        "open_slot_ids": [card["viewpoint_id"] for card in cards if card["kind"] == "OPEN_SLOT"],
    }


def allocate_viewpoint_focus(
    task_stats: list[dict[str, Any]],
    remaining_actions: int,
    *,
    null_viewpoint_id: str,
) -> dict[str, Any]:
    """Allocate actions by expected information, preserving null and a rival."""
    normalized_stats = sorted(task_stats, key=lambda item: item.get("task_id", ""))
    if remaining_actions < 0:
        raise BudgetExhausted("focus request is negative")
    if remaining_actions == 0:
        decision = {
            "schema_version": "1.0", "decision_id": digest({"tasks": normalized_stats, "remaining": 0})[7:23],
            "case_id": task_stats[0]["case_id"] if task_stats else "UNKNOWN", "treatment_id": task_stats[0].get("treatment_id", "A2-VIEWPOINT") if task_stats else "A2-VIEWPOINT",
            "remaining_actions": 0, "allocations": {}, "ranked_tasks": [], "scores": {},
            "null_retained": False, "rival_retained": False, "rationale": "No bounded focus actions remain.", "status": "ABSTAIN",
        }
        _validate("focus-decision.schema.json", decision)
        return decision
    if not task_stats:
        raise PolicyBlocked("focus decision has no support tasks")
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for item in normalized_stats:
        if item.get("case_id") != normalized_stats[0].get("case_id"):
            raise PolicyBlocked("focus tasks cross case boundaries")
        if not item.get("task_id") or not item.get("viewpoint_id"):
            raise PolicyBlocked("focus task is missing task or viewpoint ID")
        score = (
            3 * int(item.get("expected_information", 0))
            + 2 * int(item.get("unresolved_uncertainty", 0))
            + int(item.get("novelty", 0))
            + int(item.get("provenance_risk", 0))
            - 2 * int(item.get("duplicate_work", 0))
        )
        if not item.get("feasible", True):
            score = -10_000
        scored.append((score, item["task_id"], item))
    # Highest-value work must be considered first.  The previous ascending
    # ordering could spend the bounded follow-up budget on the least useful
    # eligible task while a higher-information task remained available.
    eligible = sorted(
        ((score, task_id, item) for score, task_id, item in scored if score >= 0),
        key=lambda value: (-value[0], value[1]),
    )
    by_viewpoint = {item["viewpoint_id"] for _, _, item in eligible}
    null_tasks = [task_id for _, task_id, item in eligible if item["viewpoint_id"] == null_viewpoint_id]
    rival_tasks = [task_id for _, task_id, item in eligible if item["viewpoint_id"] != null_viewpoint_id]
    if not null_tasks or not rival_tasks or remaining_actions < 2:
        decision = {
            "schema_version": "1.0", "decision_id": digest({"tasks": normalized_stats, "remaining": remaining_actions})[7:23],
            "case_id": normalized_stats[0]["case_id"], "treatment_id": normalized_stats[0].get("treatment_id", "A2-VIEWPOINT"),
            "remaining_actions": remaining_actions, "allocations": {},
            "ranked_tasks": [task_id for _, task_id, _ in eligible],
            "scores": {task_id: score for score, task_id, _ in eligible},
            "null_retained": bool(null_tasks), "rival_retained": bool(rival_tasks),
            "rationale": "Abstain because the bounded budget cannot preserve a null and a credible rival.", "status": "ABSTAIN",
        }
        _validate("focus-decision.schema.json", decision)
        return decision
    ordered = [null_tasks[0], rival_tasks[0]] + [task_id for _, task_id, _ in eligible if task_id not in {null_tasks[0], rival_tasks[0]}]
    allocations = {task_id: 0 for _, task_id, _ in eligible}
    for index in range(remaining_actions):
        allocations[ordered[index % len(ordered)]] += 1
    decision = {
        "schema_version": "1.0", "decision_id": digest({"tasks": normalized_stats, "remaining": remaining_actions})[7:23],
        "case_id": normalized_stats[0]["case_id"], "treatment_id": normalized_stats[0].get("treatment_id", "A2-VIEWPOINT"),
        "remaining_actions": remaining_actions, "allocations": allocations,
        "ranked_tasks": [task_id for _, task_id, _ in eligible],
        "scores": {task_id: score for score, task_id, _ in eligible},
        "null_retained": null_viewpoint_id in by_viewpoint, "rival_retained": bool(rival_tasks),
        "rationale": "Deterministic allocation by expected information, uncertainty, novelty, provenance risk, duplicate work, feasibility, and mandatory null/rival coverage; votes and prose length are not inputs.",
        "status": "ALLOCATED",
    }
    _validate("focus-decision.schema.json", decision)
    return decision


class ViewpointSociety:
    """Private-first viewpoint teams backed by the G10P evidence bus."""

    def __init__(
        self,
        *,
        case_id: str,
        problem_id: str,
        problem_version: str,
        treatment_id: str,
        viewpoint_cards: list[dict[str, Any]],
        context_hash: str,
        action_budget: int = 8,
    ) -> None:
        validate_viewpoint_roster(viewpoint_cards, case_id=case_id)
        if action_budget < 0:
            raise BudgetExhausted("viewpoint action budget is negative")
        self.case_id = case_id
        self.problem_id = problem_id
        self.problem_version = problem_version
        self.treatment_id = treatment_id
        self.context_hash = context_hash
        self.action_budget = action_budget
        self.cards = {card["viewpoint_id"]: deepcopy(card) for card in viewpoint_cards}
        self.active_ids = [card["viewpoint_id"] for card in viewpoint_cards if card["kind"] != "OPEN_SLOT"]
        self.null_id = next(card["viewpoint_id"] for card in viewpoint_cards if card["kind"] == "NULL")
        self.bus = EvidenceBus(
            case_id=case_id, problem_id=problem_id, problem_version=problem_version,
            treatment_id=treatment_id, context_hash=context_hash,
        )
        self.private_reports: dict[str, list[str]] = {viewpoint_id: [] for viewpoint_id in self.active_ids}
        self.dossiers: dict[str, dict[str, Any]] = {}
        self._shared = False
        self.critiques: dict[str, dict[str, Any]] = {}
        self.focus: dict[str, Any] | None = None
        self.portfolio: dict[str, Any] | None = None

    def register_action(self, action: dict[str, Any]) -> None:
        self.bus.register_action(action)

    def register_candidate(self, candidate: dict[str, Any]) -> None:
        self.bus.register_candidate(candidate)

    def admit_open_viewpoint(self, card: dict[str, Any], *, reason: str) -> None:
        """Admit one typed candidate through the reserved open viewpoint slot."""
        if self._shared:
            raise PolicyBlocked("open viewpoint admission closes after sharing")
        validate_viewpoint_card(card, case_id=self.case_id)
        if card["kind"] != "CANDIDATE":
            raise PolicyBlocked("only a candidate viewpoint may fill the open slot")
        if not any(existing["kind"] == "OPEN_SLOT" for existing in self.cards.values()):
            raise PolicyBlocked("viewpoint roster has no open slot")
        if card["viewpoint_id"] in self.cards:
            raise PolicyBlocked("viewpoint ID is already present")
        if not reason.strip():
            raise PolicyBlocked("open viewpoint admission requires a bounded reason")
        self.cards[card["viewpoint_id"]] = deepcopy(card)
        self.active_ids.append(card["viewpoint_id"])
        self.private_reports[card["viewpoint_id"]] = []

    def assign_support_task(self, task: dict[str, Any]) -> None:
        if self._shared:
            raise PolicyBlocked("support tasks cannot be assigned after viewpoints share dossiers")
        if task["viewpoint_id"] not in self.active_ids:
            raise PolicyBlocked("support task targets an inactive or unknown viewpoint")
        if task.get("task_type") not in TASK_TYPES:
            raise PolicyBlocked("unsupported structural support task")
        self.bus.assign_task(task)

    def submit_support_report(self, report: dict[str, Any]) -> None:
        viewpoint_id = report["viewpoint_id"]
        if viewpoint_id not in self.private_reports:
            raise PolicyBlocked("support report targets an unknown viewpoint")
        self.bus.add_support_report(report)
        if report["report_id"] not in self.private_reports[viewpoint_id]:
            self.private_reports[viewpoint_id].append(report["report_id"])

    def commit_viewpoint(self, viewpoint_id: str) -> dict[str, Any]:
        if self._shared:
            raise PolicyBlocked("viewpoint commit is closed after sharing")
        if viewpoint_id not in self.private_reports:
            raise PolicyBlocked("unknown viewpoint")
        if viewpoint_id in self.dossiers:
            return deepcopy(self.dossiers[viewpoint_id])
        report_ids = self.private_reports[viewpoint_id]
        if not report_ids:
            raise PolicyBlocked("viewpoint cannot commit without a typed support report")
        dossier = self.bus.build_dossier(
            dossier_id=f"DOSSIER-{viewpoint_id}", viewpoint_id=viewpoint_id, report_ids=report_ids
        )
        self.dossiers[viewpoint_id] = dossier
        return deepcopy(dossier)

    def share(self) -> list[dict[str, Any]]:
        missing = sorted(set(self.active_ids) - set(self.dossiers))
        if missing:
            raise PolicyBlocked(f"cannot share incomplete viewpoint round: {missing}")
        self._shared = True
        return [deepcopy(self.dossiers[viewpoint_id]) for viewpoint_id in sorted(self.dossiers)]

    def refresh_viewpoint(self, viewpoint_id: str) -> dict[str, Any]:
        """Rebuild a shared dossier after later support reports arrive.

        Sharing is a visibility boundary, not a freeze boundary.  Follow-up
        retrieval and critique must be able to revise the dossier that
        adjudication consumes while retaining the prior dossier in the
        evidence bus for replay and dissent analysis.
        """
        if not self._shared:
            raise PolicyBlocked("dossier refresh requires an initial shared round")
        if viewpoint_id not in self.private_reports:
            raise PolicyBlocked("unknown viewpoint")
        report_ids = self.private_reports[viewpoint_id]
        if not report_ids:
            raise PolicyBlocked("viewpoint cannot refresh without a typed support report")
        prior = self.dossiers.get(viewpoint_id)
        revision = 2 if prior is None else sum(
            1 for dossier_id in self.bus.dossiers if dossier_id.startswith(f"DOSSIER-{viewpoint_id}-R")
        ) + 2
        dossier = self.bus.build_dossier(
            dossier_id=f"DOSSIER-{viewpoint_id}-R{revision}",
            viewpoint_id=viewpoint_id,
            report_ids=report_ids,
        )
        self.dossiers[viewpoint_id] = dossier
        return deepcopy(dossier)

    def read_shared(self) -> list[dict[str, Any]]:
        if not self._shared:
            raise PolicyBlocked("viewpoint dossiers remain private before sharing")
        return [deepcopy(self.dossiers[viewpoint_id]) for viewpoint_id in sorted(self.dossiers)]

    def add_cross_viewpoint_critique(self, critique: dict[str, Any]) -> None:
        if not self._shared:
            raise PolicyBlocked("cross-viewpoint critique requires shared dossiers")
        if any(viewpoint_id not in self.dossiers for viewpoint_id in critique["compared_viewpoint_ids"] if viewpoint_id in self.active_ids):
            raise PolicyBlocked("critique references a viewpoint without a committed dossier")
        self.bus.add_critique(critique)
        self.critiques[critique["critique_id"]] = deepcopy(critique)

    def allocate_focus(self, task_stats: list[dict[str, Any]], remaining_actions: int) -> dict[str, Any]:
        if not self._shared:
            raise PolicyBlocked("focus allocation requires shared viewpoint dossiers")
        self.focus = allocate_viewpoint_focus(task_stats, remaining_actions, null_viewpoint_id=self.null_id)
        return deepcopy(self.focus)

    def adjudicate(self) -> dict[str, Any]:
        if not self._shared:
            raise PolicyBlocked("adjudication requires shared viewpoint dossiers")
        if self.focus is None:
            raise PolicyBlocked("adjudication requires a focus decision")
        scores: dict[str, int] = {}
        dissent: list[str] = []
        unresolved: list[str] = []
        for viewpoint_id, dossier in self.dossiers.items():
            reports = [self.bus.reports[report_id] for report_id in dossier["report_ids"]]
            scores[viewpoint_id] = sum(1 if report["stance"] == "SUPPORTS" else -1 if report["stance"] == "WEAKENS" else 0 for report in reports)
            dissent.extend(report["report_id"] for report in reports if report["stance"] == "WEAKENS")
            unresolved.extend(dossier["diagnostics"])
        leading = sorted(scores, key=lambda viewpoint_id: (-scores[viewpoint_id], viewpoint_id))[0] if scores else None
        rival_ids = sorted(viewpoint_id for viewpoint_id in self.dossiers if viewpoint_id != leading)
        all_report_ids = {item for ids in self.private_reports.values() for item in ids}
        support_ids = sorted(report_id for report_id in self.bus.reports if report_id in all_report_ids)
        source_ids = sorted({source_id for dossier in self.dossiers.values() for source_id in dossier["source_candidate_ids"]})
        portfolio = {
            "schema_version": "1.0",
            "portfolio_id": f"PORTFOLIO-{self.case_id}",
            "case_id": self.case_id,
            "status": "REVIEW_REQUIRED" if leading else "INCONCLUSIVE",
            "leading_viewpoint_id": leading,
            "credible_rival_ids": rival_ids or [self.null_id],
            "viewpoint_dossier_ids": sorted(dossier["dossier_id"] for dossier in self.dossiers.values()),
            "support_contribution_ids": support_ids,
            "source_candidate_ids": source_ids,
            "unresolved_disputes": sorted(set(unresolved + ["Viewpoint scores are provisional and do not establish evidence."])),
            "preserved_dissent_ids": sorted(set(dissent)),
            "next_discriminating_action": "Run the highest-ranked support task that distinguishes the leading viewpoint from its strongest rival.",
            "authority_note": "All viewpoints, support reports, and focus decisions remain REVIEW_REQUIRED; no evidence, safety, or laboratory authority is granted.",
        }
        _validate("tournament-portfolio.schema.json", portfolio)
        self.portfolio = portfolio
        return deepcopy(portfolio)

    def envelope(self) -> dict[str, Any]:
        if self.portfolio is None:
            raise PolicyBlocked("portfolio has not been adjudicated")
        return self.bus.portfolio_envelope(
            envelope_id=f"ENVELOPE-{self.case_id}",
            portfolio=self.portfolio,
            dossier_ids=[dossier["dossier_id"] for dossier in self.dossiers.values()],
            critique_ids=sorted(self.critiques),
        )

    def checkpoint(self) -> dict[str, Any]:
        return {
            "protocol": PROTOCOL_VERSION, "case_id": self.case_id, "problem_id": self.problem_id,
            "problem_version": self.problem_version, "treatment_id": self.treatment_id,
            "context_hash": self.context_hash, "action_budget": self.action_budget,
            "cards": deepcopy(self.cards), "active_ids": list(self.active_ids), "null_id": self.null_id,
            "private_reports": deepcopy(self.private_reports), "dossiers": deepcopy(self.dossiers),
            "shared": self._shared, "critiques": deepcopy(self.critiques), "focus": deepcopy(self.focus),
            "portfolio": deepcopy(self.portfolio), "evidence_bus": self.bus.checkpoint(),
        }

    @classmethod
    def from_checkpoint(cls, checkpoint: dict[str, Any], *, context_hash: str | None = None) -> "ViewpointSociety":
        if context_hash is not None and context_hash != checkpoint["context_hash"]:
            raise StaleContext("viewpoint checkpoint uses a stale context hash")
        society = cls(
            case_id=checkpoint["case_id"], problem_id=checkpoint["problem_id"], problem_version=checkpoint["problem_version"],
            treatment_id=checkpoint["treatment_id"], viewpoint_cards=list(checkpoint["cards"].values()),
            context_hash=checkpoint["context_hash"], action_budget=checkpoint["action_budget"],
        )
        society.bus = EvidenceBus.from_checkpoint(checkpoint["evidence_bus"], context_hash=checkpoint["context_hash"])
        society.private_reports = deepcopy(checkpoint["private_reports"])
        society.dossiers = deepcopy(checkpoint["dossiers"])
        society._shared = checkpoint["shared"]
        society.critiques = deepcopy(checkpoint["critiques"])
        society.focus = deepcopy(checkpoint["focus"])
        society.portfolio = deepcopy(checkpoint["portfolio"])
        return society


def score_viewpoint_portfolio(society: ViewpointSociety, portfolio: dict[str, Any]) -> dict[str, Any]:
    """Score typed contributions, not viewpoint count, prose, or consensus."""
    report_values = [society.bus.reports[report_id] for report_id in portfolio["support_contribution_ids"]]
    valid_support = sum(report["stance"] == "SUPPORTS" for report in report_values)
    weakening = sum(report["stance"] == "WEAKENS" for report in report_values)
    discriminators = len(society.critiques)
    return {
        "support_contribution_count": valid_support,
        "weakening_contribution_count": weakening,
        "discriminator_count": discriminators,
        "viewpoint_count_credit": 0,
        "consensus_credit": 0,
        "rhetoric_credit": 0,
        "primary_score": valid_support + weakening + discriminators,
        "dissent_retained": bool(portfolio["preserved_dissent_ids"]),
        "evidence_promotion": False,
    }


def _fixture_candidate(case: dict[str, Any], source_id: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0", "source_candidate_id": source_id,
        "problem_id": case["problem_id"], "problem_version": case["problem_version"],
        "title": f"Fixture source {source_id}", "locator": f"https://fixture.invalid/{source_id}",
        "content_locator": None, "discovery_query": case["case_id"], "host": "fixture.invalid",
        "access_class": "METADATA_ONLY", "rights_state": "METADATA_ONLY",
        "identity_status": "IDENTITY_UNRESOLVED", "attribution_status": "UNREVIEWED",
        "content_hash": None, "deduplication_key": f"fixture:{source_id}",
        "support_region": "offline-design-fixture", "contradiction_ids": [], "status": "DISCOVERED",
    }


def _fixture_action(case: dict[str, Any], task: dict[str, Any], action_id: str, source_ids: list[str]) -> dict[str, Any]:
    action = {
        "schema_version": "1.0", "action_id": action_id, "run_id": f"G10D-{case['case_id']}",
        "case_id": case["case_id"], "problem_id": case["problem_id"], "problem_version": case["problem_version"],
        "arm": "A2-M", "branch_id": task["viewpoint_id"], "action_type": "SEARCH",
        "rationale": task["charter"], "input": {"query": f"fixture query for {task['task_id']}"},
        "policy_status": "ALLOWED",
        "budget_debit": {"queries": 1, "retained_sources": len(source_ids), "document_fetches": 0, "payload_bytes": 0, "simulation_calls": 0, "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0},
        "output_ids": source_ids, "replay_key": digest({"case": case["case_id"], "action": action_id}),
        "timestamp": "2026-10-12T00:00:00Z",
    }
    return action


def run_offline_fixture(case: dict[str, Any]) -> dict[str, Any]:
    """Run one deterministic fixture through the full viewpoint topology."""
    society = ViewpointSociety(
        case_id=case["case_id"], problem_id=case["problem_id"], problem_version=case["problem_version"],
        treatment_id="A2-VIEWPOINT", viewpoint_cards=case["viewpoint_cards"],
        context_hash=case.get("context_hash", digest(case["case_id"])), action_budget=case.get("action_budget", 8),
    )
    for source_id in case.get("sources", []):
        society.register_candidate(_fixture_candidate(case, source_id))
    tasks_by_id: dict[str, dict[str, Any]] = {}
    for template in case["tasks"]:
        task = {
            "schema_version": "1.0", "task_id": template["task_id"], "case_id": case["case_id"],
            "problem_id": case["problem_id"], "problem_version": case["problem_version"], "treatment_id": "A2-VIEWPOINT",
            "viewpoint_id": template["viewpoint_id"], "task_type": template["task_type"],
            "charter": template["charter"], "status": template.get("status", "COMPLETED"),
        }
        society.assign_support_task(task)
        tasks_by_id[task["task_id"]] = task
    for template in case["reports"]:
        report = {
            "schema_version": "1.0", "report_id": template["report_id"], "case_id": case["case_id"],
            "viewpoint_id": template["viewpoint_id"], "support_task_id": template["support_task_id"],
            "stance": template["stance"], "action_ids": template["action_ids"],
            "source_candidate_ids": template.get("source_candidate_ids", []), "claim_ids": template.get("claim_ids", []),
            "summary": template["summary"], "unresolved_questions": template.get("unresolved_questions", []),
            "status": template.get("status", "COMPLETE"),
        }
        task = tasks_by_id[report["support_task_id"]]
        action_ids = report["action_ids"]
        for action_id in action_ids:
            society.register_action(_fixture_action(case, task, action_id, report["source_candidate_ids"]))
        society.submit_support_report(report)
    for viewpoint_id in society.active_ids:
        society.commit_viewpoint(viewpoint_id)
    society.share()
    for critique in case.get("critiques", []):
        item = dict(critique, schema_version="1.0", case_id=case["case_id"])
        society.add_cross_viewpoint_critique(item)
    focus = society.allocate_focus(case["focus_stats"], case.get("focus_budget", 4))
    portfolio = society.adjudicate()
    envelope = society.envelope()
    return {
        "case_id": case["case_id"], "status": "COMPLETE", "focus": focus,
        "portfolio": portfolio, "envelope": envelope,
        "score": score_viewpoint_portfolio(society, portfolio),
        "checkpoint": society.checkpoint(),
    }
