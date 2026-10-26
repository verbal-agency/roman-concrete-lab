"""Additive G10R-Z acquisition treatment for the Phase-A freeze.

The historical investigation runner remains immutable.  This module supplies
the next live-capable entrypoint as a thin subclass: it resolves every fetch
through the shared exact-route resolver and records typed no-content outcomes
before the underlying runner can debit a fetch or create a card.

The class is provider- and network-neutral until a caller supplies adapters;
the G10R-AA freeze and its tests use recorded fixtures only.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jsonschema import validate

from .acquisition import resolve_public_locator, resolution_replay_key
from .investigation import (
    ActiveInvestigationRunner,
    InvestigationBudget,
    record_checkpoint_action,
    schema,
    source_policy,
)
from ..retrieval import PolicyBlocked, digest


class AcquisitionHeadroomRunner(ActiveInvestigationRunner):
    """Phase-B-compatible runner with G10R-Z acquisition semantics.

    Construction is inert and does not create providers or network clients.
    The base runner still owns model orchestration, support-task persistence,
    delayed admission, checkpointing, and scoring; this class only changes the
    locator boundary so metadata-only and malformed routes cannot become
    content fetches by accident.
    """

    treatment_id = "G10R-Z-COMBINED"

    def __init__(self, *, policy: Any | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.g10r_z_policy = policy or getattr(self.adapter, "policy", None) or source_policy()
        self.checkpoint.setdefault("locator_resolutions", {})

    def _candidate_for_locator(self, locator: str) -> dict[str, Any] | None:
        for candidate in self.candidates.values():
            if locator in {
                candidate.get("source_candidate_id"),
                candidate.get("locator"),
                candidate.get("content_locator"),
            }:
                return candidate
        return None

    def resolve_g10r_z_locator(self, locator: str) -> dict[str, Any]:
        """Resolve a recorded route and retain the typed result in the checkpoint."""
        candidate = self._candidate_for_locator(locator)
        if candidate is None:
            resolution = {
                "schema_version": "1.0",
                "resolution_id": f"RES-{digest({'locator': locator})[7:23]}",
                "case_id": self.case["case_id"],
                "problem_id": self.case["problem_id"],
                "problem_version": self.case["problem_version"],
                "need_id": "UNBOUND",
                "source_candidate_id": "UNKNOWN",
                "discovery_action_ids": [],
                "original_locator": locator,
                "candidate_routes": [],
                "selected_exact_content_locator": None,
                "source_policy_hash": self.g10r_z_policy.sha256,
                "policy_decision": "DENY",
                "status": "NOT_FOUND",
                "failure_reason": "locator does not match a recorded candidate route",
                "provenance": [],
            }
        else:
            enriched = deepcopy(candidate)
            enriched.update(
                {
                    "case_id": self.case["case_id"],
                    "problem_id": self.case["problem_id"],
                    "problem_version": self.case["problem_version"],
                    "need_id": enriched.get("need_id", "UNBOUND"),
                    "discovery_action_ids": sorted(set(enriched.get("discovery_action_ids", []))),
                }
            )
            resolution = resolve_public_locator(
                enriched,
                policy=self.g10r_z_policy,
                policy_hash=self.g10r_z_policy.sha256,
            )
        resolution["replay_key"] = resolution_replay_key(resolution, operation="RESOLVE_LOCATOR")
        self.checkpoint["locator_resolutions"][resolution["replay_key"]] = deepcopy(resolution)
        return resolution

    def _resolve_fetch_locator(self, locator: str) -> tuple[str, str]:
        resolution = self.resolve_g10r_z_locator(locator)
        selected = resolution.get("selected_exact_content_locator")
        return selected or locator, f"G10R_Z_SHARED_RESOLVER:{resolution['status']}"

    def _record_no_content_fetch(
        self,
        *,
        branch_id: str,
        locator: str,
        resolution: dict[str, Any],
        rationale: str,
    ) -> list[tuple[str, dict[str, Any]]]:
        """Record a typed no-content terminal action without adapter work."""
        action_id = digest({"run": self.run_id, "branch": branch_id, "fetch": locator})[7:23]
        if any(item["action_id"] == action_id for item in self.actions):
            return []
        before = deepcopy(self.budget.usage)
        policy_status = {
            "RIGHTS_BLOCKED": "RIGHTS_BLOCKED",
            "METADATA_ONLY": "RUNNER_REJECTED",
            "INVALID": "RUNNER_REJECTED",
            "NOT_FOUND": "RUNNER_REJECTED",
        }[resolution["status"]]
        action = {
            "schema_version": "1.0",
            "action_id": action_id,
            "run_id": self.run_id,
            "case_id": self.case["case_id"],
            "problem_id": self.case["problem_id"],
            "problem_version": self.case["problem_version"],
            "arm": self.arm,
            "branch_id": branch_id,
            "action_type": "FETCH_PERMITTED_CONTENT",
            "rationale": rationale,
            "input": {
                "locator": locator,
                "resolved_locator": None,
                "locator_resolution": f"G10R_Z_SHARED_RESOLVER:{resolution['status']}",
                "resolution": resolution,
                "failure_reason": resolution.get("failure_reason"),
            },
            "policy_status": policy_status,
            "budget_debit": {
                key: max(0, getattr(self.budget.usage, key) - getattr(before, key))
                for key in asdict(before)
            },
            "output_ids": [],
            "replay_key": digest({"action": "FETCH", "locator": locator}),
            "timestamp": self.timestamp,
        }
        validate(action, schema("investigation-action.schema.json"))
        self.actions.append(action)
        record_checkpoint_action(self.checkpoint, action_id=action_id, action=action)
        if self.viewpoint_society is not None:
            self.viewpoint_society.register_action(action)
        if self.research_loop is not None:
            self.research_loop.record_fetch(
                branch_id=branch_id,
                action_id=action_id,
                candidate_ids=[],
                status=resolution["status"],
            )
        self._checkpoint()
        return []

    def _fetch(self, *, branch_id: str, locator: str, rationale: str) -> list[tuple[str, dict[str, Any]]]:
        resolution = self.resolve_g10r_z_locator(locator)
        if resolution["status"] != "RESOLVED_PUBLIC":
            return self._record_no_content_fetch(
                branch_id=branch_id,
                locator=locator,
                resolution=resolution,
                rationale=rationale,
            )
        return super()._fetch(branch_id=branch_id, locator=locator, rationale=rationale)

    def _run_a2m(self) -> dict[str, Any]:
        """Defer the inherited open-slot admission until after sharing.

        The historical runner admits a placeholder before its first private
        round.  The additive treatment intercepts that transition, allowing
        incumbent viewpoints to complete and share first.  A later run may
        admit a source-backed rival; this run records a pending or abstained
        decision instead of granting an unearned viewpoint dossier.
        """
        society = self.viewpoint_society
        if society is None:
            return super()._run_a2m()
        pending: dict[str, Any] = {}
        original_admit = society.admit_open_viewpoint

        def defer_admission(card: dict[str, Any], *, reason: str) -> None:
            pending.update({"card": deepcopy(card), "reason": reason})

        society.admit_open_viewpoint = defer_admission  # type: ignore[method-assign]
        try:
            portfolio = super()._run_a2m()
        finally:
            society.admit_open_viewpoint = original_admit  # type: ignore[method-assign]

        open_card = pending.get("card")
        open_viewpoint_id = open_card.get("viewpoint_id") if open_card else None
        open_sources: list[str] = []
        if self.research_loop is not None:
            for record in self.research_loop.state.get("open_slot", []):
                open_sources.extend(record.get("source_candidate_ids", []))
        card_sources = {card.get("source_candidate_id") for card in self.paper_cards.values()}
        source_backed = sorted(set(open_sources).intersection(card_sources))
        admission_status = "PENDING_ADMISSION_REVIEW" if source_backed else "ABSTAINED_NO_DISTINCT_VIEWPOINT"
        delayed = {
            "schema_version": "g10r-z.1",
            "viewpoint_id": open_viewpoint_id,
            "status": admission_status,
            "shared_before_admission": True,
            "tasks_created_before_admission": 0,
            "dossier_created_before_admission": 0,
            "source_candidate_ids": sorted(set(open_sources)),
            "source_backed_candidate_ids": source_backed,
            "reason": pending.get("reason", "no open-slot proposal was produced"),
        }
        if self.research_loop is not None:
            for record in self.research_loop.state.get("open_slot", []):
                record["status"] = admission_status
                record["promotion_status"] = "REVIEW_REQUIRED"
        self.checkpoint["delayed_open_admission"] = delayed
        self._checkpoint()
        return portfolio


__all__ = ["AcquisitionHeadroomRunner"]
