"""Runner-facing adapter for the G10R-AC provisional intake contracts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from jsonschema import validate

from ..retrieval.contracts import PolicyBlocked, StaleContext, canonical, digest
from tools.tournament.replay import ROOT
from .conflict_adjudication import ConflictAdjudicationLedger
from .provisional_intake import ProvisionalIntakeLedger


def _schema(name: str) -> dict[str, Any]:
    import json

    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


class RunnerProvisionalIntake:
    """Binds G10R-AC records to a real runner case/arm checkpoint.

    The adapter is inert until the runner explicitly attaches it. It accepts
    exploratory output but cannot write immutable evidence or authorize work.
    """

    def __init__(self, *, case_id: str, problem_id: str, problem_version: str, arm: str, run_id: str, context_hash: str) -> None:
        if arm not in {"A1", "A2-M"}:
            raise ValueError(arm)
        self.case_id = case_id
        self.problem_id = problem_id
        self.problem_version = problem_version
        self.arm = arm
        self.run_id = run_id
        self.context_hash = context_hash
        self.ledger = ProvisionalIntakeLedger(case_id=case_id)
        self.conflicts = ConflictAdjudicationLedger(case_id=case_id, problem_id=problem_id, problem_version=problem_version)
        self.lineage: dict[str, dict[str, Any]] = {}

    def ingest_viewpoint(self, *, viewpoint_id: str, argument: dict[str, Any], source_leads: list[dict[str, Any]], action_ids: list[str], dossier_revision_ids: list[str], portfolio_ids: list[str]) -> dict[str, Any]:
        argument_id = argument["argument_id"]
        existing = self.ledger.arguments.get(argument_id)
        if existing is not None:
            if canonical(existing) != canonical(argument):
                raise PolicyBlocked(f"conflicting duplicate argument: {argument_id}")
            return deepcopy(existing)
        for lead in source_leads:
            if lead["source_id"] not in self.ledger.sources:
                self.ledger.discover_source(**{key: lead[key] for key in ("source_id", "locator", "title", "doi", "authors", "citation_ancestors", "rights_state", "content_hash", "retrieval_note")})
        created = self.ledger.create_argument(
            argument_id=argument_id, viewpoint_id=viewpoint_id, thesis=argument["thesis"],
            claims=argument["claims"], predictions=argument["predictions"],
            uncertainty=argument["uncertainty"], requested_discriminators=argument["requested_discriminators"],
            source_ids=argument["source_ids"], null_or_rival=argument.get("null_or_rival", False),
        )
        self.lineage[argument_id] = {"argument_id": argument_id, "viewpoint_id": viewpoint_id, "action_ids": sorted(action_ids), "dossier_revision_ids": sorted(dossier_revision_ids), "portfolio_ids": sorted(portfolio_ids), "case_id": self.case_id, "arm": self.arm}
        return created

    def add_edge(self, *, edge_id: str, argument_id: str, claim_id: str, source_id: str, claim_scope: str, action_ids: list[str]) -> dict[str, Any]:
        if argument_id not in self.ledger.arguments or source_id not in self.ledger.sources:
            raise PolicyBlocked("edge is not bound to this runner case")
        if edge_id in self.ledger.edges:
            existing = self.ledger.edges[edge_id]
            if existing["argument_id"] != argument_id or existing["source_id"] != source_id:
                raise PolicyBlocked(f"conflicting duplicate edge: {edge_id}")
            return deepcopy(existing)
        edge = self.ledger.create_edge(edge_id=edge_id, argument_id=argument_id, claim_id=claim_id, source_id=source_id, claim_scope=claim_scope)
        self.lineage[edge_id] = {"edge_id": edge_id, "argument_id": argument_id, "claim_id": claim_id, "source_id": source_id, "action_ids": sorted(action_ids), "case_id": self.case_id, "arm": self.arm}
        return edge

    def transition_source(self, *, source_id: str, next_status: str, reason: str) -> dict[str, Any]:
        return self.ledger.transition_source(source_id=source_id, next_status=next_status, reason=reason)

    def record_vetting(self, **decision: Any) -> dict[str, Any]:
        return self.ledger.record_vetting(**decision)

    def adjudicate_edge(self, **decision: Any) -> dict[str, Any]:
        return self.ledger.adjudicate_edge(**decision)

    def revise_argument(self, **revision: Any) -> dict[str, Any]:
        return self.ledger.revise_argument(**revision)

    def open_conflict(self, *, claim_id: str, edge_ids: list[str], scope: dict[str, str]) -> dict[str, Any]:
        edges = [self.ledger.edges[edge_id] for edge_id in edge_ids]
        return self.conflicts.open_set(claim_id=claim_id, edges=edges, scope=scope)

    def adjudicate_conflict(self, *, conflict_set_id: str, reviewer_role: str, comparable: bool, scope_checks: dict[str, bool], outcome: str, rationale: str, unresolved_questions: list[str]) -> dict[str, Any]:
        return self.conflicts.adjudicate(conflict_set_id=conflict_set_id, reviewer_role=reviewer_role, comparable=comparable, scope_checks=scope_checks, outcome=outcome, rationale=rationale, unresolved_questions=unresolved_questions)

    def checkpoint(self) -> dict[str, Any]:
        output = {
            "schema_version": "1.0", "case_id": self.case_id, "arm": self.arm, "run_id": self.run_id,
            "context_hash": self.context_hash,
            "arguments": [deepcopy(self.ledger.arguments[key]) for key in sorted(self.ledger.arguments)],
            "sources": [deepcopy(self.ledger.sources[key]) for key in sorted(self.ledger.sources)],
            "edges": [deepcopy(self.ledger.edges[key]) for key in sorted(self.ledger.edges)],
            "revisions": deepcopy(self.ledger.revisions),
            "conflict_sets": deepcopy(self.conflicts.checkpoint()["conflict_sets"]),
            "adjudications": deepcopy(self.conflicts.checkpoint()["adjudications"]),
            "lineage": [deepcopy(self.lineage[key]) for key in sorted(self.lineage)],
            "authority": {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0},
        }
        validate(output, _schema("runner-provisional-intake.schema.json"))
        return output

    def attach_to_checkpoint(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        if checkpoint.get("case_id", self.case_id) != self.case_id or checkpoint.get("arm", self.arm) != self.arm:
            raise PolicyBlocked("cross-case or cross-arm provisional intake write")
        if checkpoint.get("manifest_sha256") and checkpoint["manifest_sha256"] != self.context_hash:
            raise StaleContext("runner checkpoint context does not match provisional intake")
        existing = checkpoint.get("provisional_intake")
        current = self.checkpoint()
        if existing is not None and canonical(existing) != canonical(current):
            raise PolicyBlocked("conflicting provisional intake checkpoint")
        checkpoint["provisional_intake"] = current
        return checkpoint


class RunnerIntakeActiveInvestigationRunner(__import__("src.roman_concrete_lab.agents.investigation", fromlist=["ActiveInvestigationRunner"]).ActiveInvestigationRunner):
    """Additive runner seam that preserves the historical base-runner hash."""

    def __init__(self, *, provisional_intake: RunnerProvisionalIntake | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.provisional_intake = provisional_intake

    def attach_provisional_intake(self, intake: RunnerProvisionalIntake) -> None:
        if intake.case_id != self.case["case_id"] or intake.arm != self.arm:
            raise PolicyBlocked("provisional intake case or arm does not match runner")
        if intake.context_hash != self.manifest_sha256:
            raise StaleContext("provisional intake context does not match runner manifest")
        self.provisional_intake = intake
        self._checkpoint()

    def _checkpoint(self) -> None:
        super()._checkpoint()
        if self.provisional_intake is not None:
            self.provisional_intake.attach_to_checkpoint(self.checkpoint)
            from .investigation import write_json

            write_json(self.checkpoint_path, self.checkpoint)


__all__ = ["RunnerProvisionalIntake", "RunnerIntakeActiveInvestigationRunner"]
