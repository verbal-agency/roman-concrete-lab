"""Provider-neutral, exact-route acquisition contracts for G10R-Z.

The resolver accepts only locators recorded on a candidate or in an explicit
route-record list.  It never constructs a URL from a title, DOI, query, or
model prose.  Resolution is terminal and replay-safe; callers decide whether
to fetch a resolved route.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

from ..retrieval import PolicyBlocked, SourcePolicy, digest


RESOLUTION_STATUSES = {
    "RESOLVED_PUBLIC",
    "METADATA_ONLY",
    "RIGHTS_BLOCKED",
    "NOT_FOUND",
    "INVALID",
}


def _route_records(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only explicitly recorded exact route records."""
    records: list[dict[str, Any]] = []
    for route in candidate.get("route_records", []) or []:
        if isinstance(route, dict):
            records.append(deepcopy(route))
    # Existing candidate fixtures predate route_records.  Their locator and
    # content_locator fields are still recorded exact values, not guesses.
    # If route_records is present, it is the authoritative route register;
    # do not smuggle a metadata locator in as a content route when an explicit
    # malformed or unsupported route record is being evaluated.
    if not records:
        for field in ("content_locator", "locator"):
            value = candidate.get(field)
            if isinstance(value, str) and value.strip():
                if not any(row.get("locator") == value for row in records):
                    records.append({"locator": value, "route_kind": field, "recorded_exact": True})
    return records


def resolve_public_locator(
    candidate: dict[str, Any],
    *,
    policy: SourcePolicy,
    policy_hash: str | None = None,
) -> dict[str, Any]:
    """Resolve one candidate to a recorded route under the frozen policy."""
    candidate_id = candidate.get("source_candidate_id")
    resolution_id = digest({"candidate": candidate_id, "routes": _route_records(candidate), "policy": policy.sha256})[7:23]
    routes = _route_records(candidate)
    base = {
        "schema_version": "1.0",
        "resolution_id": f"RES-{resolution_id}",
        "case_id": candidate.get("case_id", "UNKNOWN"),
        "problem_id": candidate.get("problem_id", "UNKNOWN"),
        "problem_version": candidate.get("problem_version", "UNKNOWN"),
        "need_id": candidate.get("need_id", "UNBOUND"),
        "source_candidate_id": candidate_id or "UNKNOWN",
        "discovery_action_ids": sorted(set(candidate.get("discovery_action_ids", []))),
        "original_locator": candidate.get("locator"),
        "candidate_routes": routes,
        "selected_exact_content_locator": None,
        "source_policy_hash": policy_hash or policy.sha256,
        "policy_decision": "DENY",
        "status": "NOT_FOUND",
        "failure_reason": None,
        "provenance": sorted(set(candidate.get("provenance", []))),
    }
    if not candidate_id or not isinstance(candidate.get("locator"), str):
        base.update({"status": "INVALID", "failure_reason": "candidate is missing an identity or original locator"})
        return base
    if not routes:
        base.update({"status": "NOT_FOUND", "failure_reason": "no recorded exact route"})
        return base

    saw_metadata = False
    saw_blocked = False
    invalid_reasons: list[str] = []
    for route in routes:
        locator = route.get("locator")
        if route.get("recorded_exact") is not True or not isinstance(locator, str):
            invalid_reasons.append("route is not explicitly recorded exact")
            continue
        parsed = urlparse(locator)
        if parsed.scheme != "https" or not parsed.hostname or parsed.query and route.get("route_kind") == "prose":
            invalid_reasons.append(f"route is not an exact HTTPS locator: {locator!r}")
            continue
        try:
            decision = policy.decide(locator, fetch_content=False)
        except PolicyBlocked as exc:
            invalid_reasons.append(str(exc))
            continue
        if decision["access_class"] == "PUBLIC":
            base.update({
                "selected_exact_content_locator": locator,
                "policy_decision": "ALLOW_PUBLIC_CONTENT",
                "status": "RESOLVED_PUBLIC",
                "failure_reason": None,
            })
            return base
        if decision["access_class"] == "METADATA_ONLY":
            saw_metadata = True
        else:
            saw_blocked = True

    if saw_blocked:
        base.update({"status": "RIGHTS_BLOCKED", "failure_reason": "all recorded routes are outside content rights"})
    elif saw_metadata:
        base.update({"status": "METADATA_ONLY", "policy_decision": "RETAIN_METADATA", "failure_reason": "recorded routes expose metadata only"})
    elif invalid_reasons:
        base.update({"status": "INVALID", "failure_reason": "; ".join(sorted(set(invalid_reasons)))})
    return base


def resolution_replay_key(resolution: dict[str, Any], *, operation: str) -> str:
    """Key duplicate work by policy, candidate, route, and operation."""
    return digest({
        "policy": resolution.get("source_policy_hash"),
        "candidate": resolution.get("source_candidate_id"),
        "candidate_routes": resolution.get("candidate_routes", []),
        "selected": resolution.get("selected_exact_content_locator"),
        "operation": operation,
    })
