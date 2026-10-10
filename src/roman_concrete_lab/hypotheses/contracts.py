"""Validate typed derived hypotheses without promoting them to evidence."""

from __future__ import annotations

from typing import Any


ALLOWED_CLAIM_TYPES = {"PROPOSED", "DERIVED", "UNRESOLVED"}
ALLOWED_STATUSES = {
    "HYPOTHESIS",
    "SUPPORTED_WITHIN_CONTEXT",
    "NARROW_USE_CASE",
    "CONTRADICTED",
    "RETIRED",
    "REVIEW_REQUIRED",
    "ABSTAIN",
}


def validate_typed_hypotheses(records: list[dict[str, Any]]) -> dict[str, Any]:
    ids: set[str] = set()
    for record in records:
        hypothesis_id = record["hypothesis_id"]
        if hypothesis_id in ids:
            raise ValueError(f"duplicate hypothesis ID: {hypothesis_id}")
        ids.add(hypothesis_id)
        if record["claim_type"] not in ALLOWED_CLAIM_TYPES:
            raise ValueError(f"invalid hypothesis claim type: {record['claim_type']}")
        if record["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"invalid hypothesis status: {record['status']}")
        if not record["evidence_memory_ids"] or not record["provenance"]["source_locators"]:
            raise ValueError(f"hypothesis lacks provenance: {hypothesis_id}")
    return {"record_count": len(records), "unique_ids": len(ids), "evidence_promotion": "prohibited"}
