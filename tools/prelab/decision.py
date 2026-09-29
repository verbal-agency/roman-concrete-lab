"""Deterministic GP2 result classification for offline fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas/prelab-result.schema.json"


def validate_result(result: dict) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(result), key=lambda error: list(error.path))
    if errors:
        raise ValueError("; ".join(error.message for error in errors))


def classify_result(result: dict) -> str:
    """Return the legal GP2 status without imputing missing observations."""
    validate_result(result)
    if result["safety_status"] in {"unsafe", "unreviewed", "not_assessed"}:
        return "REVIEW_REQUIRED"
    if result["outcome_class"] == "contradictory":
        return "INCONCLUSIVE"
    if result["outcome_class"] == "incomplete":
        return "REVIEW_REQUIRED"
    measurement = result["measurement"]
    if (
        result["comparator_status"] != "matched"
        or not result["provenance_complete"]
        or measurement["missingness"] != "observed"
        or measurement["unit"] is None
    ):
        return "REVIEW_REQUIRED"
    if result["outcome_class"] == "positive":
        return "SUPPORTED" if measurement["value"] is not None else "REVIEW_REQUIRED"
    if result["outcome_class"] == "null":
        return "INCONCLUSIVE"
    if result["outcome_class"] == "unsupported":
        return "NOT_REPRODUCED"
    raise ValueError(f"unsupported outcome class: {result['outcome_class']}")
