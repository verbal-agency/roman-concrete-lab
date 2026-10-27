"""Offline open-world intake for provisional arguments and source leads.

This module deliberately separates exploration from evidence.  A viewpoint may
make a useful argument and point to a new source before that source is in the
corpus, but neither receives scientific credit until a separate vetting path
binds an exact claim to an identified, retrieved source.
"""

from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

from jsonschema import validate

from ..retrieval.contracts import PolicyBlocked, canonical, digest
from tools.tournament.replay import ROOT


EDGE_STATUSES = {"SUPPORTED", "CONTRADICTED", "UNRESOLVED", "MISATTRIBUTED", "UNRETRIEVABLE"}
SOURCE_STATUSES = {"DISCOVERED", "RETRIEVAL_PENDING", "RETRIEVED_UNVETTED", "VETTING", "ADMITTED_CORPUS", "REJECTED", "UNRETRIEVABLE", "DUPLICATE"}
ARGUMENT_STATUSES = {"PROVISIONAL", "REVISED", "WEAKENED", "CONTRADICTED", "UNRESOLVED"}
EDGE_TRANSITIONS = {"UNRESOLVED": EDGE_STATUSES - {"UNRESOLVED"}}
SOURCE_TRANSITIONS = {
    "DISCOVERED": {"RETRIEVAL_PENDING", "REJECTED", "DUPLICATE", "UNRETRIEVABLE"},
    "RETRIEVAL_PENDING": {"RETRIEVED_UNVETTED", "UNRETRIEVABLE", "REJECTED"},
    "RETRIEVED_UNVETTED": {"VETTING", "UNRETRIEVABLE", "REJECTED", "DUPLICATE"},
    "VETTING": {"ADMITTED_CORPUS", "REJECTED", "UNRETRIEVABLE", "DUPLICATE"},
}


def _schema(name: str) -> dict[str, Any]:
    return __import__("json").loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _hash_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _host(locator: str) -> str:
    parsed = urlparse(locator)
    return (parsed.hostname or "unknown").lower()


def _identity_key(*, doi: str | None, title: str, authors: list[str], content_hash: str | None, ancestors: list[str]) -> str:
    if doi:
        return "doi:" + doi.casefold().strip()
    if content_hash:
        return content_hash
    normalized = re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()
    author_key = ",".join(sorted(item.casefold().strip() for item in authors))
    ancestor_key = ",".join(sorted(ancestors))
    return digest({"title": normalized, "authors": author_key, "ancestors": ancestor_key})


class ProvisionalIntakeLedger:
    """Append-only, deterministic argument/source/edge ledger."""

    def __init__(self, *, case_id: str) -> None:
        self.case_id = case_id
        self.arguments: dict[str, dict[str, Any]] = {}
        self.sources: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, dict[str, Any]] = {}
        self.revisions: list[dict[str, Any]] = []
        self.vetting: list[dict[str, Any]] = []
        self._identity_index: dict[str, str] = {}

    def create_argument(self, *, argument_id: str, viewpoint_id: str, thesis: str, claims: list[dict[str, str]], predictions: list[str], uncertainty: str, requested_discriminators: list[str], source_ids: list[str], null_or_rival: bool = False) -> dict[str, Any]:
        if argument_id in self.arguments or not claims:
            raise PolicyBlocked("argument must have a unique id and at least one claim")
        record = {
            "schema_version": "1.0", "argument_id": argument_id, "case_id": self.case_id,
            "viewpoint_id": viewpoint_id, "thesis": thesis, "claims": claims,
            "predictions": predictions, "uncertainty": uncertainty,
            "requested_discriminators": requested_discriminators, "source_ids": source_ids,
            "status": "PROVISIONAL", "revision_number": 0,
            "credit": {"evidence": 0, "reason": "provisional arguments and unaccepted sources earn no evidence credit"},
            "null_or_rival": null_or_rival,
        }
        validate(record, _schema("exploratory-argument.schema.json"))
        self.arguments[argument_id] = record
        return deepcopy(record)

    def discover_source(self, *, source_id: str, locator: str, title: str, doi: str | None = None, authors: list[str] | None = None, citation_ancestors: list[str] | None = None, rights_state: str = "UNKNOWN", content_hash: str | None = None, retrieval_note: str = "") -> dict[str, Any]:
        if source_id in self.sources:
            raise PolicyBlocked("duplicate source id")
        ancestors = citation_ancestors or []
        identity = _identity_key(doi=doi, title=title, authors=authors or [], content_hash=content_hash, ancestors=ancestors)
        duplicate_of = self._identity_index.get(identity)
        independent = duplicate_of is None
        status = "DISCOVERED" if independent else "DUPLICATE"
        record = {
            "schema_version": "1.0", "source_id": source_id, "case_id": self.case_id,
            "locator": locator, "title": title, "host": _host(locator), "status": status,
            "rights_state": rights_state, "identity_key": identity,
            "content_hash": content_hash, "citation_ancestors": ancestors,
            "independent_work": independent, "canonical_source_id": duplicate_of,
            "evidence_credit": 0, "retrieval_note": retrieval_note,
        }
        validate(record, _schema("candidate-source-intake.schema.json"))
        self.sources[source_id] = record
        if independent:
            self._identity_index[identity] = source_id
        return deepcopy(record)

    def transition_source(self, *, source_id: str, next_status: str, reason: str) -> dict[str, Any]:
        source = self.sources[source_id]
        if next_status not in SOURCE_TRANSITIONS.get(source["status"], set()):
            raise PolicyBlocked(f"illegal source transition: {source['status']} -> {next_status}")
        self._record_revision(source_id, "SOURCE", source["status"], next_status, reason)
        source["status"] = next_status
        if next_status != "ADMITTED_CORPUS":
            source["evidence_credit"] = 0
        validate(source, _schema("candidate-source-intake.schema.json"))
        return deepcopy(source)

    def record_vetting(self, *, decision_id: str, source_id: str, reviewer_role: str, outcome: str, identity_verified: bool, content_verified: bool, exact_locator_verified: bool, rationale: str) -> dict[str, Any]:
        decision = {"schema_version": "1.0", "decision_id": decision_id, "source_id": source_id, "reviewer_role": reviewer_role, "outcome": outcome, "identity_verified": identity_verified, "content_verified": content_verified, "exact_locator_verified": exact_locator_verified, "rationale": rationale}
        validate(decision, _schema("vetting-decision.schema.json"))
        self.vetting.append(decision)
        source = self.sources[source_id]
        if outcome == "ADMIT":
            if source["status"] != "VETTING" or not (identity_verified and content_verified):
                raise PolicyBlocked("admission requires vetted source identity and content")
            self.transition_source(source_id=source_id, next_status="ADMITTED_CORPUS", reason=rationale)
        elif outcome == "UNRETRIEVABLE":
            if source["status"] not in {"RETRIEVAL_PENDING", "RETRIEVED_UNVETTED", "VETTING"}:
                raise PolicyBlocked("unretrievable decision requires an active retrieval path")
            self.transition_source(source_id=source_id, next_status="UNRETRIEVABLE", reason=rationale)
        elif outcome == "REJECT":
            if source["status"] not in {"DISCOVERED", "RETRIEVAL_PENDING", "RETRIEVED_UNVETTED", "VETTING"}:
                raise PolicyBlocked("rejection cannot rewrite a terminal source")
            self.transition_source(source_id=source_id, next_status="REJECTED", reason=rationale)
        return deepcopy(decision)

    def create_edge(self, *, edge_id: str, argument_id: str, claim_id: str, source_id: str, claim_scope: str, rationale: str = "awaiting vetting") -> dict[str, Any]:
        if edge_id in self.edges or argument_id not in self.arguments or source_id not in self.sources:
            raise PolicyBlocked("edge references must be unique and known")
        edge = {"schema_version": "1.0", "edge_id": edge_id, "argument_id": argument_id, "claim_id": claim_id, "source_id": source_id, "status": "UNRESOLVED", "claim_scope": claim_scope, "locator": None, "locator_type": "NONE", "content_hash": None, "rationale": rationale, "revision_number": 0}
        validate(edge, _schema("claim-source-edge.schema.json"))
        self.edges[edge_id] = edge
        return deepcopy(edge)

    def adjudicate_edge(self, *, edge_id: str, status: str, locator: str | None, locator_type: str, content_hash: str | None, rationale: str) -> dict[str, Any]:
        if status not in EDGE_STATUSES:
            raise PolicyBlocked(f"unknown edge status: {status}")
        edge = self.edges[edge_id]
        if status not in EDGE_TRANSITIONS.get(edge["status"], set()):
            raise PolicyBlocked(f"illegal edge transition: {edge['status']} -> {status}")
        source = self.sources[edge["source_id"]]
        if status in {"SUPPORTED", "CONTRADICTED"}:
            if source["status"] != "ADMITTED_CORPUS" or not locator or locator_type == "NONE" or not content_hash or content_hash != source["content_hash"]:
                raise PolicyBlocked("support or contradiction requires admitted source, exact locator, and matching content hash")
        if status == "UNRETRIEVABLE" and source["status"] != "UNRETRIEVABLE":
            raise PolicyBlocked("retrieval failure must be recorded on the source before the edge")
        self._record_revision(edge_id, "EDGE", edge["status"], status, rationale)
        edge.update({"status": status, "locator": locator, "locator_type": locator_type, "content_hash": content_hash, "rationale": rationale, "revision_number": edge["revision_number"] + 1})
        validate(edge, _schema("claim-source-edge.schema.json"))
        return deepcopy(edge)

    def revise_argument(self, *, argument_id: str, status: str, reason: str, thesis: str | None = None) -> dict[str, Any]:
        if status not in ARGUMENT_STATUSES:
            raise PolicyBlocked(f"unknown argument status: {status}")
        argument = self.arguments[argument_id]
        if status == "PROVISIONAL" or status == argument["status"]:
            raise PolicyBlocked("argument revisions must change status")
        self._record_revision(argument_id, "ARGUMENT", argument["status"], status, reason)
        argument["status"] = status
        argument["revision_number"] += 1
        if thesis:
            argument["thesis"] = thesis
        validate(argument, _schema("exploratory-argument.schema.json"))
        return deepcopy(argument)

    def _record_revision(self, target_id: str, target_type: str, from_status: str, to_status: str, reason: str) -> None:
        revision = {"schema_version": "1.0", "revision_id": f"REV-{len(self.revisions) + 1:03d}", "target_id": target_id, "target_type": target_type, "from_status": from_status, "to_status": to_status, "reason": reason, "preserves_prior": True}
        validate(revision, _schema("provisional-revision.schema.json"))
        self.revisions.append(revision)

    def score(self) -> dict[str, Any]:
        supported = [edge for edge in self.edges.values() if edge["status"] == "SUPPORTED"]
        return {"evidence_credit": len(supported), "provisional_argument_count": len(self.arguments), "independent_source_count": sum(source["independent_work"] for source in self.sources.values()), "consensus_credit": 0, "rhetoric_credit": 0, "agent_count_credit": 0, "supported_edge_ids": [edge["edge_id"] for edge in supported]}

    def snapshot(self) -> dict[str, Any]:
        return {"case_id": self.case_id, "arguments": [deepcopy(self.arguments[key]) for key in sorted(self.arguments)], "sources": [deepcopy(self.sources[key]) for key in sorted(self.sources)], "edges": [deepcopy(self.edges[key]) for key in sorted(self.edges)], "vetting": deepcopy(self.vetting), "revisions": deepcopy(self.revisions), "score": self.score()}


__all__ = ["ProvisionalIntakeLedger", "EDGE_STATUSES", "SOURCE_STATUSES", "ARGUMENT_STATUSES"]
