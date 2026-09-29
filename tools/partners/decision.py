"""Deterministic GP3 offline partner-readiness gate."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/partner-result.schema.json"
REQUIRED_CAPABILITIES = {"C01", "C02", "C03", "C04", "C05", "C06", "C07", "C09", "C10"}


def validate_response(response: dict) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(response), key=lambda error: list(error.path))
    if errors:
        raise ValueError("; ".join(error.message for error in errors))


def classify_response(response: dict) -> str:
    """Classify feasibility without approving safety or physical work."""
    validate_response(response)
    capabilities = {item["capability_id"]: item for item in response["capabilities"]}
    missing = REQUIRED_CAPABILITIES - capabilities.keys()
    if missing:
        raise ValueError(f"missing required capability rows: {sorted(missing)}")
    unavailable = [item["capability_id"] for item in capabilities.values() if item["requirement_level"] == "required" and item["status"] == "unavailable"]
    if unavailable:
        return "NO_MATCH"
    unresolved = [item["capability_id"] for item in capabilities.values() if item["requirement_level"] == "required" and item["status"] == "unknown"]
    if unresolved:
        return "REVISE"
    if response["safety_review"]["status"] != "reviewable":
        return "REVISE"
    if response["ownership_review"]["status"] != "answerable":
        return "REVISE"
    if response["data_return_review"]["status"] != "answerable":
        return "REVISE"
    return "FEASIBLE_FOR_REVIEW"
