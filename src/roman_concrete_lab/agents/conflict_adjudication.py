"""Deterministic conflict grouping and adjudication for runner checkpoints."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from jsonschema import validate

from ..retrieval.contracts import PolicyBlocked, canonical, digest
from tools.tournament.replay import ROOT


CONFLICT_STATUSES = {"OPEN", "SCOPE_DIFFERENCE", "METHOD_DIFFERENCE", "WEIGHTED_CONFLICT", "UNRESOLVED"}
TERMINAL_CONFLICT_STATUSES = {"SCOPE_DIFFERENCE", "METHOD_DIFFERENCE", "WEIGHTED_CONFLICT", "UNRESOLVED"}


def _schema(name: str) -> dict[str, Any]:
    import json

    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


class ConflictAdjudicationLedger:
    """Groups attributable edges without selecting a scientific winner."""

    def __init__(self, *, case_id: str, problem_id: str, problem_version: str) -> None:
        self.case_id = case_id
        self.problem_id = problem_id
        self.problem_version = problem_version
        self.conflict_sets: dict[str, dict[str, Any]] = {}
        self.adjudications: list[dict[str, Any]] = []

    def open_set(self, *, claim_id: str, edges: list[dict[str, Any]], scope: dict[str, str]) -> dict[str, Any]:
        eligible = [edge for edge in edges if edge.get("status") in {"SUPPORTED", "CONTRADICTED"}]
        if not eligible:
            raise PolicyBlocked("a conflict set requires supported or contradicted edges")
        independent = sorted({edge["source_id"] for edge in eligible})
        set_id = "CONFLICT-" + digest({"case_id": self.case_id, "claim_id": claim_id, "edge_ids": sorted(edge["edge_id"] for edge in eligible)})[7:23]
        record = {
            "schema_version": "1.0", "conflict_set_id": set_id, "case_id": self.case_id,
            "problem_id": self.problem_id, "problem_version": self.problem_version,
            "claim_id": claim_id, "edge_ids": sorted(edge["edge_id"] for edge in eligible),
            "independent_source_ids": independent, "scope": scope, "status": "OPEN", "revision_number": 0,
        }
        existing = self.conflict_sets.get(set_id)
        if existing is not None and canonical(existing) != canonical(record):
            raise PolicyBlocked("conflicting duplicate conflict set")
        validate(record, _schema("conflict-set.schema.json"))
        self.conflict_sets[set_id] = record
        return deepcopy(record)

    def adjudicate(self, *, conflict_set_id: str, reviewer_role: str, comparable: bool, scope_checks: dict[str, bool], outcome: str, rationale: str, unresolved_questions: list[str]) -> dict[str, Any]:
        if outcome not in {"SCOPE_DIFFERENCE", "METHOD_DIFFERENCE", "WEIGHTED_CONFLICT", "UNRESOLVED"}:
            raise PolicyBlocked(f"illegal conflict outcome: {outcome}")
        conflict = self.conflict_sets[conflict_set_id]
        if conflict["status"] in TERMINAL_CONFLICT_STATUSES:
            raise PolicyBlocked("terminal conflict set is immutable")
        if outcome == "WEIGHTED_CONFLICT" and not comparable:
            raise PolicyBlocked("weighted conflict requires comparable sources")
        decision = {
            "schema_version": "1.0", "adjudication_id": f"ADJ-{len(self.adjudications) + 1:03d}",
            "conflict_set_id": conflict_set_id, "reviewer_role": reviewer_role,
            "comparable": comparable, "scope_checks": scope_checks, "outcome": outcome,
            "rationale": rationale, "unresolved_questions": unresolved_questions,
            "revision_ids": [], "preserves_prior": True,
        }
        validate(decision, _schema("conflict-adjudication.schema.json"))
        self.adjudications.append(decision)
        conflict["status"] = outcome
        conflict["revision_number"] += 1
        return deepcopy(decision)

    def checkpoint(self) -> dict[str, Any]:
        return {"conflict_sets": [deepcopy(self.conflict_sets[key]) for key in sorted(self.conflict_sets)], "adjudications": deepcopy(self.adjudications)}


__all__ = ["ConflictAdjudicationLedger", "CONFLICT_STATUSES"]
