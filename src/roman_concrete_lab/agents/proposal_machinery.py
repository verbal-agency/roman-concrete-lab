"""Typed, offline proposal packets for the G10R-AF readiness gate."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from jsonschema import validate

from ..retrieval.contracts import PolicyBlocked, StaleContext, canonical
from tools.tournament.replay import ROOT


SOURCE_EDGE_STATUSES = {"SUPPORTED", "CONTRADICTED", "UNRETRIEVABLE", "METADATA_ONLY", "REVIEW_REQUIRED"}
PROPOSAL_STATUSES = {"PROPOSAL_REVIEWABLE", "PROPOSAL_INCOMPLETE", "REVIEW_REQUIRED"}
REQUIRED_CONTENT = (
    "intervention_or_process", "comparator", "primary_endpoint", "predicted_observation",
    "falsifier", "discriminator", "support_region", "uncertainty",
)


def _schema() -> dict[str, Any]:
    import json

    return json.loads((ROOT / "schemas/proposal-packet.schema.json").read_text(encoding="utf-8"))


def _missing_content(packet: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_CONTENT if not str(packet.get(field, "")).strip()]
    if not packet.get("source_edges"):
        missing.append("source_edges")
    provenance = packet.get("provenance", {})
    if not any(provenance.get(field) for field in ("action_ids", "dossier_revision_ids", "portfolio_ids")):
        missing.append("provenance")
    return sorted(set(missing))


def validate_packet(packet: dict[str, Any], *, case_id: str | None = None) -> dict[str, Any]:
    """Validate the packet shape and its case/status invariants."""
    validate(packet, _schema())
    if case_id is not None and packet["case_id"] != case_id:
        raise PolicyBlocked("proposal packet is bound to a different case")
    if packet["status"] not in PROPOSAL_STATUSES:
        raise PolicyBlocked(f"illegal proposal status: {packet['status']}")
    for edge in packet["source_edges"]:
        if edge["status"] not in SOURCE_EDGE_STATUSES:
            raise PolicyBlocked(f"illegal source-edge status: {edge['status']}")
    return deepcopy(packet)


class ProposalLedger:
    """Case/arm-scoped append-only proposal ledger with fail-closed joins."""

    def __init__(self, *, case_id: str, arm: str, context_hash: str) -> None:
        if arm not in {"A1", "A2-M"}:
            raise ValueError(arm)
        self.case_id = case_id
        self.arm = arm
        self.context_hash = context_hash
        self.proposals: dict[str, dict[str, Any]] = {}

    def add(self, packet: dict[str, Any]) -> dict[str, Any]:
        packet = validate_packet(packet, case_id=self.case_id)
        if packet["arm"] != self.arm:
            raise PolicyBlocked("proposal packet arm does not match ledger")
        existing = self.proposals.get(packet["proposal_id"])
        if existing is not None:
            if canonical(existing) != canonical(packet):
                raise PolicyBlocked(f"conflicting duplicate proposal: {packet['proposal_id']}")
            return deepcopy(existing)
        missing = _missing_content(packet)
        if missing and packet["status"] == "PROPOSAL_REVIEWABLE":
            packet["status"] = "PROPOSAL_INCOMPLETE"
        self.proposals[packet["proposal_id"]] = packet
        return deepcopy(packet)

    def attach_checkpoint(self, checkpoint: dict[str, Any]) -> dict[str, Any]:
        if checkpoint.get("case_id") != self.case_id or checkpoint.get("arm") != self.arm:
            raise PolicyBlocked("cross-case or cross-arm proposal checkpoint")
        if checkpoint.get("context_hash") != self.context_hash:
            raise StaleContext("proposal checkpoint uses stale context")
        existing = checkpoint.get("proposals")
        current = self.snapshot()["proposals"]
        if existing is not None and canonical(existing) != canonical(current):
            raise PolicyBlocked("conflicting proposal checkpoint")
        checkpoint["proposals"] = current
        checkpoint["authority"] = {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0}
        return checkpoint

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema_version": "g10r-af.1",
            "case_id": self.case_id,
            "arm": self.arm,
            "context_hash": self.context_hash,
            "proposals": [deepcopy(self.proposals[key]) for key in sorted(self.proposals)],
            "authority": {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0},
        }


def blind_for_scoring(packet: dict[str, Any]) -> dict[str, Any]:
    """Remove treatment and viewpoint identity before deterministic scoring."""
    blinded = deepcopy(packet)
    blinded.pop("arm", None)
    blinded["viewpoint_id"] = "BLINDED"
    return blinded


def score_proposal(packet: dict[str, Any]) -> dict[str, Any]:
    """Score typed proposal utility only; rhetorical metadata is ignored."""
    missing = _missing_content(packet)
    edges = packet.get("source_edges", [])
    supported = [edge for edge in edges if edge.get("status") == "SUPPORTED" and edge.get("locator") and edge.get("content_hash")]
    contradicted = [edge for edge in edges if edge.get("status") == "CONTRADICTED"]
    pending = [edge for edge in edges if edge.get("status") in {"UNRETRIEVABLE", "METADATA_ONLY", "REVIEW_REQUIRED"}]
    complete = packet.get("status") == "PROPOSAL_REVIEWABLE" and not missing
    components = {
        "proposal_completeness": int(complete),
        "attributable_support": len(supported),
        "contradiction_retention": int(bool(contradicted)),
        "discriminator_quality": int(bool(str(packet.get("discriminator", "")).strip())),
        "falsifiability": int(bool(str(packet.get("falsifier", "")).strip())),
        "uncertainty_preservation": int(bool(str(packet.get("uncertainty", "")).strip())),
        "rival_retention": int(bool(packet.get("rival_proposal_ids") or packet.get("conflict_set_ids"))),
    }
    return {
        "proposal_id": packet.get("proposal_id"),
        "status": "PROPOSAL_REVIEWABLE" if complete else "PROPOSAL_INCOMPLETE",
        "missing_fields": missing,
        "components": components,
        "proposal_credit": sum(components.values()) if complete else 0,
        "supported_edge_count": len(supported),
        "contradicted_edge_count": len(contradicted),
        "pending_edge_count": len(pending),
        "rhetoric_credit": 0,
        "consensus_credit": 0,
        "answer_length_credit": 0,
        "viewpoint_count_credit": 0,
        "agent_count_credit": 0,
        "treatment_identity_available": False,
    }


__all__ = ["ProposalLedger", "blind_for_scoring", "score_proposal", "validate_packet"]
