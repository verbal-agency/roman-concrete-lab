"""Deterministic evidence-driven society research loop.

This module is intentionally provider-free.  It is the small executable
substrate used by G10R-T to test the society wiring before spending money on
model calls: discovery produces candidates, selection chooses a candidate,
content acquisition maps a page-aware card, and later reports revise the
private dossier that adjudication consumes.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import validate

from ..retrieval import (
    BudgetExhausted,
    BudgetLimits,
    InvestigationBudget,
    PolicyBlocked,
    SourcePolicy,
    canonical,
    digest,
    normalize_query,
)
from tools.tournament.replay import ROOT


STAGES = [
    "CREATED", "SEARCHING", "CANDIDATE_TRIAGE", "CONTENT_ACQUISITION",
    "EVIDENCE_MAPPING", "PRIVATE_REVISION", "SHARING", "CRITIQUING",
    "FOCUSING", "ROUND_2", "ADJUDICATING", "SCORED", "COMPLETED",
]
TERMINAL = {"BUDGET_EXHAUSTED", "POLICY_BLOCKED", "INCONCLUSIVE", "COMPLETED"}
ARMS = {"R0_SINGLE", "R1_SHARED_SUPPORT", "R2_VIEWPOINT_FIXED", "R3_VIEWPOINT_ADAPTIVE"}


def _schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _validate(name: str, value: dict[str, Any]) -> None:
    validate(value, _schema(name))


def _stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}-{digest(value)[7:19]}"


def _card(candidate: dict[str, Any], payload: str) -> dict[str, Any]:
    content_hash = digest(payload)
    page_hash = digest({"source": candidate["source_candidate_id"], "page": 1, "text": payload})
    card = {
        "schema_version": "1.0",
        "card_id": _stable_id("CARD", {"candidate": candidate["source_candidate_id"], "hash": content_hash}),
        "source_candidate_id": candidate["source_candidate_id"],
        "document_hash": content_hash,
        "parser": "recorded-research-loop-v1",
        "extraction_status": "EXTRACTED",
        "page_count": 1,
        "facts": [
            {"field": "material_process", "value": candidate["support_region"], "reporting_status": "REPORTED", "support_type": "DIRECT", "page_locator": "#page=1", "page_text_hash": page_hash, "confidence": "MEDIUM"},
            {"field": "mechanism", "value": payload[:400], "reporting_status": "REPORTED", "support_type": "DIRECT", "page_locator": "#page=1", "page_text_hash": page_hash, "confidence": "LOW"},
        ],
        "unresolved": ["independence and full experimental detail require review"],
        "authority_note": "Derived extraction for review; no evidence promotion, performance claim, or laboratory authority.",
    }
    _validate("paper-evidence-card.schema.json", card)
    return card


class OfflineResearchLoop:
    """Run one arm against immutable recorded opportunities."""

    def __init__(self, arm: str, *, fixture_dir: Path | None = None, checkpoint: dict[str, Any] | None = None) -> None:
        if arm not in ARMS:
            raise ValueError(f"unknown research-loop arm: {arm}")
        self.arm = arm
        self.fixture_dir = fixture_dir or (ROOT / "fixtures/investigation/research-loop")
        self.policy = SourcePolicy.load(ROOT / "fixtures/investigation/source-policy.json")
        self.sources = [json.loads(line) for line in (self.fixture_dir / "sources.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        self.by_id = {row["source_candidate_id"]: row for row in self.sources}
        self.budget = InvestigationBudget(BudgetLimits(queries=8, retained_sources=8, document_fetches=4, payload_bytes=100_000, input_tokens=0, output_tokens=0, estimated_cost_usd=0.0))
        self.state: dict[str, Any] = {
            "schema_version": "g10r-t.1",
            "run_id": _stable_id("RUN", {"arm": arm, "fixture": "research-loop-v1"}),
            "case_id": "CASE-RESEARCH-LOOP",
            "problem_id": "roman-hot-mix",
            "problem_version": "1.0",
            "arm": arm,
            "stage": "CREATED",
            "actions": [], "needs": [], "candidates": [], "selections": [],
            "cards": [], "reports": [], "critiques": [], "dossier_revisions": [],
            "focus": [], "open_admissions": [], "semantic_work": {}, "metrics": {},
            "terminal": None,
        }
        if checkpoint:
            self._restore(checkpoint)

    def _restore(self, checkpoint: dict[str, Any]) -> None:
        if checkpoint.get("arm") != self.arm or checkpoint.get("schema_version") != "g10r-t.1":
            raise PolicyBlocked("stale or conflicting research-loop checkpoint")
        self.state = deepcopy(checkpoint)
        usage = checkpoint.get("budget", {}).get("usage", {})
        # Derived envelope fields are not part of the mutable state; retaining
        # them would make a resumed digest depend on the checkpoint boundary.
        self.state.pop("budget", None)
        self.state.pop("content_hash", None)
        self.budget = InvestigationBudget(self.budget.limits)
        self.budget.debit(**{k: usage.get(k, 0) for k in usage})

    def _checkpoint(self) -> dict[str, Any]:
        result = deepcopy(self.state)
        result["budget"] = self.budget.snapshot()
        result["content_hash"] = digest(result)
        return result

    def _action(self, kind: str, payload: dict[str, Any], *, debit: dict[str, int | float] | None = None) -> str:
        action_id = _stable_id("ACT", {"kind": kind, "payload": payload})
        existing = next((item for item in self.state["actions"] if item["action_id"] == action_id), None)
        if existing:
            if canonical(existing["payload"]) != canonical(payload):
                raise PolicyBlocked("conflicting duplicate action")
            return action_id
        if debit:
            self.budget.debit(**debit)
        self.state["actions"].append({"action_id": action_id, "kind": kind, "payload": deepcopy(payload)})
        return action_id

    def _need(self, viewpoint: str, task_type: str, query: str, *, expected: str) -> str:
        need = {
            "schema_version": "1.0", "need_id": _stable_id("NEED", {"viewpoint": viewpoint, "query": query}),
            "case_id": self.state["case_id"], "problem_id": self.state["problem_id"], "problem_version": self.state["problem_version"],
            "viewpoint_id": viewpoint, "claim_ids": [f"CLAIM-{viewpoint}"], "task_type": task_type,
            "question": query, "expected_decision_change": 2 if expected else 1, "required_evidence_kind": "PAGE_CARD",
            "known_candidate_ids": [], "unresolved_uncertainty": 3,
            "duplication_key": normalize_query(query), "budget_request": 2,
            "status": "OPEN", "provenance": ["offline-research-loop"],
        }
        _validate("research-need.schema.json", need)
        if not any(item["need_id"] == need["need_id"] for item in self.state["needs"]):
            self.state["needs"].append(need)
        return need["need_id"]

    def _search_and_select(self, need_id: str, query: str) -> str | None:
        normalized = normalize_query(query)
        action = self._action("SEARCH", {"need_id": need_id, "query": normalized}, debit={"queries": 1})
        terms = set(normalized.split())
        candidates = []
        for row in self.sources:
            searchable = " ".join([row["title"], *row.get("_fixture_queries", [])]).lower()
            if normalized in [normalize_query(q) for q in row.get("_fixture_queries", [])] or terms.issubset(set(searchable.split())):
                candidate = {key: value for key, value in row.items() if not key.startswith("_fixture_")}
                decision = self.policy.decide(candidate["locator"], fetch_content=False)
                candidate["host"] = decision["host"]
                candidates.append(candidate)
        candidates.sort(key=lambda item: item["source_candidate_id"])
        for candidate in candidates:
            if not any(item["source_candidate_id"] == candidate["source_candidate_id"] for item in self.state["candidates"]):
                self.state["candidates"].append(candidate)
        if not candidates:
            return None
        # Choose the first candidate with content; metadata-only remains pending.
        selected = next((item for item in candidates if self._can_fetch(item)), candidates[0])
        selection = {
            "schema_version": "1.0", "selection_id": _stable_id("SEL", {"need": need_id, "candidate": selected["source_candidate_id"]}),
            "need_id": need_id, "action_ids": [action], "source_candidate_id": selected["source_candidate_id"],
            "selection_reason": "first stable candidate with a permitted recorded content route" if self._can_fetch(selected) else "metadata candidate retained pending lawful content locator",
            "candidate_status": selected["status"], "content_locator": selected.get("content_locator") or selected.get("locator"),
            "requested_operation": "FETCH_AND_MAP" if self._can_fetch(selected) else "SEEK_LAWFUL_LOCATOR",
            "policy_status": "ALLOWED" if self._can_fetch(selected) else "METADATA_ONLY",
            "status": "SELECTED" if self._can_fetch(selected) else "PENDING",
        }
        _validate("candidate-selection.schema.json", selection)
        self.state["selections"].append(selection)
        semantic_key = f"{selected['source_candidate_id']}|{selection['requested_operation']}"
        if semantic_key in self.state["semantic_work"]:
            self._action("SEMANTIC_DUPLICATE", {"semantic_key": semantic_key, "prior_action_id": self.state["semantic_work"][semantic_key], "query": normalized})
        else:
            self.state["semantic_work"][semantic_key] = action
        return selected["source_candidate_id"]

    def _can_fetch(self, candidate: dict[str, Any]) -> bool:
        try:
            return self.policy.decide(candidate["locator"], fetch_content=True)["rights_state"] == "PERMITTED"
        except PolicyBlocked:
            return False

    def fetch_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate the public fetch boundary before touching the adapter."""
        candidate_id = request.get("source_candidate_id")
        if not isinstance(candidate_id, str) or candidate_id not in self.by_id:
            action = self._action("INVALID_FETCH_REQUEST", {"request": deepcopy(request)})
            return {"status": "INVALID_FETCH_REQUEST", "action_id": action, "adapter_called": False}
        if not self._can_fetch(self.by_id[candidate_id]):
            action = self._action("METADATA_ONLY", {"source_candidate_id": candidate_id})
            return {"status": "METADATA_ONLY", "action_id": action, "adapter_called": False}
        self._fetch_and_map(candidate_id, request.get("need_id", "EXTERNAL"))
        return {"status": "FETCHED", "adapter_called": True, "card_ids": [item["card_id"] for item in self.state["cards"] if item["source_candidate_id"] == candidate_id]}

    def _fetch_and_map(self, candidate_id: str | None, need_id: str) -> None:
        if not candidate_id:
            return
        candidate = self.by_id[candidate_id]
        if not self._can_fetch(candidate):
            return
        semantic_key = f"{candidate_id}|FETCH_AND_MAP"
        if semantic_key in self.state["semantic_work"] and any(item["kind"] == "MAP" and item["payload"].get("candidate_id") == candidate_id for item in self.state["actions"]):
            self._action("SEMANTIC_DUPLICATE", {"semantic_key": semantic_key, "prior_action_id": self.state["semantic_work"][semantic_key], "need_id": need_id})
            return
        fetch_action = self._action("FETCH", {"candidate_id": candidate_id, "need_id": need_id}, debit={"document_fetches": 1})
        self.state["semantic_work"][semantic_key] = fetch_action
        payload = candidate.get("_fixture_payload", "")
        self.budget.debit(payload_bytes=len(payload.encode("utf-8")))
        card = _card(candidate, payload)
        if not any(item["card_id"] == card["card_id"] for item in self.state["cards"]):
            self.state["cards"].append(card)
        self.state["candidates"] = [dict(item, content_hash=card["document_hash"], status="EVIDENCE_PENDING") if item["source_candidate_id"] == candidate_id else item for item in self.state["candidates"]]
        self._action("MAP", {"candidate_id": candidate_id, "card_id": card["card_id"], "need_id": need_id})

    def _report(self, viewpoint: str, stance: str, source_ids: list[str], *, round_name: str) -> None:
        report = {
            "schema_version": "1.0", "report_id": _stable_id("REPORT", {"viewpoint": viewpoint, "round": round_name}),
            "case_id": self.state["case_id"], "viewpoint_id": viewpoint, "support_task_id": f"TASK-{viewpoint}-{round_name}",
            "stance": stance, "action_ids": sorted(item["action_id"] for item in self.state["actions"]), "source_candidate_ids": sorted(source_ids),
            "claim_ids": [f"CLAIM-{viewpoint}"], "summary": f"{round_name} typed support outcome: {stance}.",
            "unresolved_questions": ["independence and validation remain review-required"], "status": "COMPLETE",
            "round": round_name, "claim_id": f"CLAIM-{viewpoint}",
        }
        _validate("viewpoint-support-report.schema.json", {key: value for key, value in report.items() if key != "round" and key != "claim_id"})
        if not any(item["report_id"] == report["report_id"] for item in self.state["reports"]):
            self.state["reports"].append(report)

    def support_need(self, need: dict[str, Any], *, stance: str, source_candidate_ids: list[str] | None = None, discriminator: str | None = None) -> dict[str, Any]:
        """Return a typed support outcome; completion requires observable work."""
        _validate("research-need.schema.json", need)
        if stance not in {"SUPPORTS", "WEAKENS", "NON_DISCRIMINATING"}:
            raise PolicyBlocked("unsupported support stance")
        source_candidate_ids = sorted(source_candidate_ids or [])
        observable = bool(source_candidate_ids or discriminator or self.state["actions"])
        if not observable:
            return {"status": "ABSTAINED", "stance": "NON_DISCRIMINATING", "reason": "no observable action, mapped artifact, or discriminator"}
        return {"status": "COMPLETE", "stance": stance, "source_candidate_ids": source_candidate_ids, "discriminator": discriminator}

    def _revise(self, reason: str) -> None:
        reports = sorted(self.state["reports"], key=lambda item: item["report_id"])
        revision = len(self.state["dossier_revisions"]) + 1
        payload = {
            "schema_version": "1.0", "dossier_id": "DOSSIER-SOCIETY", "viewpoint_id": "SOCIETY", "revision": revision,
            "parent_revision": revision - 1 if revision > 1 else None,
            "report_ids": [item["report_id"] for item in reports],
            "action_ids": sorted(item["action_id"] for item in self.state["actions"]),
            "source_candidate_ids": sorted({source for item in reports for source in item["source_candidate_ids"]}),
            "claim_ids": sorted({item["claim_id"] for item in reports}),
            "critique_ids": sorted(item["critique_id"] for item in self.state["critiques"]),
            "unresolved_joins": [], "revision_reason": reason, "status": "CURRENT",
        }
        payload["status"] = "COMPLETE"
        payload["content_hash"] = digest(payload)
        _validate("viewpoint-dossier-revision.schema.json", payload)
        self.state["dossier_revisions"].append(payload)

    def _focus(self) -> None:
        tasks = []
        for viewpoint in ["VP-MECHANISM", "VP-RIVAL", "VP-NULL"]:
            tasks.append({"task_id": f"TASK-{viewpoint}", "viewpoint_id": viewpoint, "expected_information": 3 if viewpoint == "VP-MECHANISM" else 2, "unresolved_uncertainty": 3, "novelty": 2 if viewpoint == "VP-RIVAL" else 1, "provenance_risk": 1, "duplicate_work": 0, "feasible": True})
        ordered = sorted(tasks, key=lambda item: (-3 * item["expected_information"] - 2 * item["unresolved_uncertainty"] - item["novelty"] - item["provenance_risk"], item["task_id"]))
        allocation = [item["task_id"] for item in ordered[:2]]
        record = {"ranked_tasks": [item["task_id"] for item in ordered], "allocations": allocation, "observed_source_yield": len(self.state["cards"]), "highest_first": True}
        self.state["focus"].append(record)
        # The follow-up is task-specific and evidence-bearing, not a status-only report.
        for task_id in allocation:
            self._action("FOCUS_FOLLOW_UP", {"task_id": task_id, "source_ids": sorted(item["source_candidate_id"] for item in self.state["candidates"])})

    def _open_slot(self) -> None:
        if self.arm != "R3_VIEWPOINT_ADAPTIVE":
            status = "REJECTED_REDUNDANT" if self.arm == "R2_VIEWPOINT_FIXED" else "ABSTAINED_NO_DISTINCT_VIEWPOINT"
            proposal = {"schema_version": "1.0", "admission_id": "OPEN-STATIC", "case_id": self.state["case_id"], "viewpoint_id": "VP-OPEN", "novelty_basis": "no adaptive proposer", "source_candidate_ids": [], "claim_ids": [], "predicted_observation": "No distinct observation proposed", "falsifier": "No evidence-conditioned proposal", "discriminator": "No discriminator", "overlap_decision": "NO_COMPARABLE_INCUMBENT", "status": status, "promotion_status": "REVIEW_REQUIRED"}
        else:
            source = next((item for item in self.state["candidates"] if item["source_candidate_id"] == "SRC-LATERAL-HOTLIME"), None)
            proposal = {"schema_version": "1.0", "admission_id": "OPEN-ADAPTIVE", "case_id": self.state["case_id"], "viewpoint_id": "VP-OPEN-LATERAL", "novelty_basis": "hot-lime process source was not used by incumbent viewpoints", "source_candidate_ids": [source["source_candidate_id"]] if source else [], "claim_ids": ["CLAIM-VP-OPEN-LATERAL"] if source else [], "predicted_observation": "process identity changes interpretation of functional claims", "falsifier": "source is not independent or not process-matched", "discriminator": "process-matched comparator", "overlap_decision": "DISTINCT" if source else "NO_COMPARABLE_INCUMBENT", "status": "ADMITTED" if source else "ABSTAINED_NO_DISTINCT_VIEWPOINT", "promotion_status": "REVIEW_REQUIRED"}
        _validate("open-viewpoint-admission.schema.json", proposal)
        self.state["open_admissions"].append(proposal)

    def _score(self) -> None:
        source_ids = {item["source_candidate_id"] for item in self.state["candidates"]}
        card_ids = {item["source_candidate_id"] for item in self.state["cards"]}
        admitted = [item for item in self.state["open_admissions"] if item["status"] == "ADMITTED"]
        unique = len({source for item in self.state["reports"] for source in item["source_candidate_ids"]})
        dossier_check = self.dossier_integrity()
        self.state["metrics"] = {
            "task_accuracy": 1 if dossier_check["passes"] and self.state["dossier_revisions"] and self.state["dossier_revisions"][-1]["report_ids"] else 0,
            "canonical_source_recall": len(card_ids) / max(1, len(source_ids)),
            "successful_fetch_count": len(card_ids), "paper_card_count": len(self.state["cards"]),
            "evidence_to_final_handoff_retention": int(bool(self.state["dossier_revisions"] and card_ids.issubset(set(self.state["dossier_revisions"][-1]["source_candidate_ids"])) or not card_ids)),
            "unique_attributable_contributions": unique + len(admitted), "contradiction_discriminator_value": len(self.state["critiques"]) + len(admitted),
            "duplicate_work_rate": 0.0, "authority_integrity": 1, "cost_token_efficiency": 1 / max(1, len(self.state["actions"])),
            "discovery_candidate_count": len(source_ids), "pending_novel_candidates": len(source_ids - card_ids),
            "dossier_membership_integrity": int(dossier_check["passes"]),
        }

    def dossier_integrity(self) -> dict[str, Any]:
        """Detect a report deliberately omitted from the current revision."""
        if not self.state["dossier_revisions"]:
            return {"passes": False, "missing_report_ids": sorted(item["report_id"] for item in self.state["reports"])}
        included = set(self.state["dossier_revisions"][-1]["report_ids"])
        missing = sorted(item["report_id"] for item in self.state["reports"] if item["report_id"] not in included)
        return {"passes": not missing, "missing_report_ids": missing}

    def run(self, *, stop_after_stage: str | None = None) -> dict[str, Any]:
        if self.state.get("terminal") == "COMPLETED":
            return self._checkpoint()
        start = STAGES.index(self.state["stage"])
        for stage in STAGES[start + 1:]:
            try:
                if stage == "SEARCHING":
                    need = self._need("VP-MECHANISM", "RETRIEVAL", "quicklime self healing bridge deck thesis", expected="identify primary candidate")
                    self._search_and_select(need, "quicklime self healing bridge deck thesis")
                elif stage == "CANDIDATE_TRIAGE":
                    need = self.state["needs"][0]["need_id"]
                    # A second, differently worded request demonstrates semantic work identity.
                    if self.arm in {"R1_SHARED_SUPPORT", "R2_VIEWPOINT_FIXED", "R3_VIEWPOINT_ADAPTIVE"}:
                        self._need("VP-RIVAL", "CONTRADICTION", "Utah quicklime concrete thesis", expected="test rival explanation")
                        self._search_and_select(need, "utah quicklime concrete thesis")
                    self._action("CANDIDATE_TRIAGE", {"candidate_ids": sorted(item["source_candidate_id"] for item in self.state["candidates"])})
                elif stage == "CONTENT_ACQUISITION":
                    for selection in list(self.state["selections"]):
                        if selection["status"] == "SELECTED":
                            self._fetch_and_map(selection["source_candidate_id"], selection["need_id"])
                elif stage == "EVIDENCE_MAPPING":
                    self._action("EVIDENCE_MAPPING", {"card_ids": sorted(item["card_id"] for item in self.state["cards"])})
                elif stage == "PRIVATE_REVISION":
                    self._report("VP-MECHANISM", "SUPPORTS" if self.state["cards"] else "NON_DISCRIMINATING", [item["source_candidate_id"] for item in self.state["cards"]], round_name="PRIVATE")
                    if self.arm in {"R2_VIEWPOINT_FIXED", "R3_VIEWPOINT_ADAPTIVE"}:
                        self._report("VP-RIVAL", "WEAKENS", [item["source_candidate_id"] for item in self.state["cards"]], round_name="PRIVATE")
                    self._revise("initial private reports")
                elif stage == "SHARING":
                    self._action("SHARE", {"revision": self.state["dossier_revisions"][-1]["revision"]})
                elif stage == "CRITIQUING":
                    if self.arm in {"R2_VIEWPOINT_FIXED", "R3_VIEWPOINT_ADAPTIVE"}:
                        critique = {"critique_id": _stable_id("CRIT", self.arm), "target_viewpoint_id": "VP-MECHANISM", "compared_viewpoint_ids": ["VP-MECHANISM", "VP-RIVAL"], "source_ids": sorted(item["source_candidate_id"] for item in self.state["cards"]), "discriminator": "process-matched comparator"}
                        self.state["critiques"].append(critique)
                    self._revise("shared critique and evidence")
                elif stage == "FOCUSING":
                    self._focus()
                elif stage == "ROUND_2":
                    if self.arm == "R3_VIEWPOINT_ADAPTIVE":
                        need = self._need("VP-OPEN-LATERAL", "IDENTITY_LINEAGE", "traditional mortar preparation hot lime mix method", expected="test lateral process discriminator")
                        self._search_and_select(need, "traditional mortar preparation hot lime mix method")
                        self._fetch_and_map("SRC-LATERAL-HOTLIME", need)
                    self._report("VP-MECHANISM", "WEAKENS" if self.arm == "R3_VIEWPOINT_ADAPTIVE" else "SUPPORTS", [item["source_candidate_id"] for item in self.state["cards"]], round_name="ROUND_2")
                    self._revise("round-two focused evidence")
                elif stage == "ADJUDICATING":
                    self._open_slot()
                    self._action("ADJUDICATE", {"revision": self.state["dossier_revisions"][-1]["revision"], "open_slot": self.state["open_admissions"][-1]["status"]})
                elif stage == "SCORED":
                    self._score()
                elif stage == "COMPLETED":
                    self.state["terminal"] = "COMPLETED"
                self.state["stage"] = stage
                if stop_after_stage == stage:
                    break
            except BudgetExhausted:
                self.state["terminal"] = "BUDGET_EXHAUSTED"
                break
            except PolicyBlocked:
                self.state["terminal"] = "POLICY_BLOCKED"
                break
        return self._checkpoint()


def run_arm(arm: str, *, checkpoint: dict[str, Any] | None = None, stop_after_stage: str | None = None) -> dict[str, Any]:
    return OfflineResearchLoop(arm, checkpoint=checkpoint).run(stop_after_stage=stop_after_stage)
