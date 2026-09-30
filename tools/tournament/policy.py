"""Frozen policies for the G07E deterministic hypothesis tournament."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any


POLICY_VERSION = "g07e-policy.1"
POLICY_DEFINITION = {
    "policy_version": POLICY_VERSION,
    "utility_dimensions": ["endpoint_fit", "information_value", "feasibility", "risk"],
    "ordinal_order": ["LOW", "MEDIUM", "HIGH"],
    "risk_is_minimized": True,
    "focus_budget_unit": "one candidate attention slot",
    "promotion_requires": ["evidence_locator", "distinguishable_prediction", "rival_state", "reviewer_authority"],
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


POLICY_HASH = digest(POLICY_DEFINITION)


LEGAL_TRANSITIONS = {
    "HYPOTHESIS": {"SUPPORTED_WITHIN_CONTEXT", "NARROW_USE_CASE", "CONTRADICTED", "REVIEW_REQUIRED", "ABSTAIN", "RETIRED"},
    "SUPPORTED_WITHIN_CONTEXT": {"NARROW_USE_CASE", "CONTRADICTED", "REVIEW_REQUIRED", "RETIRED"},
    "NARROW_USE_CASE": {"CONTRADICTED", "REVIEW_REQUIRED", "RETIRED"},
    "CONTRADICTED": {"REVIEW_REQUIRED", "RETIRED"},
    "REVIEW_REQUIRED": {"HYPOTHESIS", "ABSTAIN", "RETIRED"},
    "ABSTAIN": {"HYPOTHESIS"},
    "RETIRED": set(),
}


class MemoryPermissionError(PermissionError):
    """Raised when a stage crosses a memory authority boundary."""


class MemoryStore:
    """Three-tier append-only memory store used by the tournament."""

    def __init__(self, evidence: list[dict[str, Any]] | None = None) -> None:
        self._evidence = {item["memory_id"]: copy.deepcopy(item) for item in (evidence or [])}
        self._hypotheses: dict[str, dict[str, Any]] = {}
        self._notes: dict[str, dict[str, Any]] = {}

    @property
    def evidence(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(self._evidence[key]) for key in sorted(self._evidence)]

    @property
    def hypotheses(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(self._hypotheses[key]) for key in sorted(self._hypotheses)]

    @property
    def notes(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(self._notes[key]) for key in sorted(self._notes)]

    def write_evidence(self, record: dict[str, Any]) -> None:
        raise MemoryPermissionError("immutable_evidence is read-only to the tournament")

    def write_hypothesis(self, record: dict[str, Any]) -> None:
        memory_id = record.get("hypothesis_id") or record.get("memory_id")
        if not memory_id:
            raise ValueError("typed hypothesis requires an ID")
        if memory_id in self._hypotheses:
            raise MemoryPermissionError(f"typed hypothesis is append-only: {memory_id}")
        if not record.get("evidence_memory_ids") or not record.get("provenance"):
            raise ValueError("typed hypothesis requires evidence IDs and provenance")
        self._hypotheses[memory_id] = copy.deepcopy(record)

    def write_note(self, record: dict[str, Any]) -> None:
        memory_id = record.get("memory_id")
        if not memory_id:
            raise ValueError("untrusted note requires memory_id")
        if memory_id in self._notes:
            raise MemoryPermissionError(f"untrusted note is append-only: {memory_id}")
        self._notes[memory_id] = copy.deepcopy(record)


@dataclass
class HypothesisRegistry:
    """Append-only registry with explicit status transitions."""

    records: dict[str, dict[str, Any]]
    events: list[dict[str, Any]]

    @classmethod
    def empty(cls) -> "HypothesisRegistry":
        return cls(records={}, events=[])

    def append(self, record: dict[str, Any]) -> None:
        hypothesis_id = record["hypothesis_id"]
        if hypothesis_id in self.records:
            raise ValueError(f"duplicate hypothesis ID: {hypothesis_id}")
        self.records[hypothesis_id] = copy.deepcopy(record)
        self.events.append({"event": "APPEND", "hypothesis_id": hypothesis_id, "status": record["status"]})

    def transition(
        self,
        hypothesis_id: str,
        next_status: str,
        reason: str,
        *,
        new_context_version: str | None = None,
    ) -> dict[str, Any]:
        if hypothesis_id not in self.records:
            raise KeyError(hypothesis_id)
        current = self.records[hypothesis_id]
        current_status = current["status"]
        if next_status not in LEGAL_TRANSITIONS[current_status]:
            raise ValueError(f"illegal transition {current_status} -> {next_status}")
        if not reason:
            raise ValueError("status transition requires a reason")
        if current_status == "ABSTAIN" and next_status == "HYPOTHESIS":
            if not new_context_version or reason != "CONTEXT_AMENDED":
                raise ValueError("ABSTAIN -> HYPOTHESIS requires CONTEXT_AMENDED and a new context version")
        updated = copy.deepcopy(current)
        updated["status"] = next_status
        updated["promotion_retraction_reason"] = reason
        if new_context_version:
            updated["problem_version"] = new_context_version
        self.records[hypothesis_id] = updated
        self.events.append({
            "event": "TRANSITION",
            "hypothesis_id": hypothesis_id,
            "from": current_status,
            "to": next_status,
            "reason": reason,
            "previous_record": copy.deepcopy(current),
            "next_record": copy.deepcopy(updated),
        })
        return copy.deepcopy(updated)

    def snapshot(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(self.records[key]) for key in sorted(self.records)]


def utility_for(card: dict[str, Any], candidate: dict[str, Any]) -> dict[str, str]:
    """Return separate qualitative utilities; never aggregate them."""

    missing = set(candidate.get("missing_fields", []))
    endpoint_fit = "LOW" if "endpoint_mapping" in missing else "HIGH"
    information_value = "HIGH" if missing else "MEDIUM"
    feasibility = "HIGH" if card.get("controls") and card.get("candidate_variables") else "LOW"
    safety_missing = any("safety" in field.lower() for field in missing)
    risk = "HIGH" if safety_missing or "no physical execution before GL1" not in card.get("constraints", []) else "MEDIUM"
    return {
        "endpoint_fit": endpoint_fit,
        "information_value": information_value,
        "feasibility": feasibility,
        "risk": risk,
    }


def dominates(left: dict[str, str], right: dict[str, str]) -> bool:
    """Return whether left dominates right with risk minimized."""

    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    at_least = True
    strictly = False
    for dimension in POLICY_DEFINITION["utility_dimensions"]:
        left_value = order[left[dimension]]
        right_value = order[right[dimension]]
        if dimension == "risk":
            left_value, right_value = -left_value, -right_value
        if left_value < right_value:
            at_least = False
        if left_value > right_value:
            strictly = True
    return at_least and strictly


def pareto_ids(records: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for candidate in records:
        if not any(dominates(other["utility_components"], candidate["utility_components"]) for other in records if other is not candidate):
            ids.append(candidate["hypothesis_id"])
    return sorted(ids)
