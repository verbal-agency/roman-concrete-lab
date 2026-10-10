"""Validate the authority boundaries of the three memory tiers."""

from __future__ import annotations

from typing import Any


def validate_memory_tiers(card: dict[str, Any]) -> dict[str, Any]:
    memory = card["scoped_memory"]
    evidence = {item["memory_id"] for item in memory["evidence"]}
    hypotheses = {item["memory_id"] for item in memory["hypotheses"]}
    notes = {item["memory_id"] for item in memory["untrusted_notes"]}
    if evidence & hypotheses or evidence & notes or hypotheses & notes:
        raise ValueError(f"memory tiers overlap for {card['problem_id']}")
    return {
        "problem_id": card["problem_id"],
        "problem_version": card["version"],
        "evidence_count": len(evidence),
        "hypothesis_count": len(hypotheses),
        "untrusted_note_count": len(notes),
        "immutable_evidence": True,
        "write_policy": memory["write_policy"],
    }
