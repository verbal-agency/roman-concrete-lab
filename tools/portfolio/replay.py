"""Deterministic GP4 problem-card and portfolio replay."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CARD_SCHEMA = json.loads((ROOT / "schemas/problem-card.schema.json").read_text(encoding="utf-8"))
ENTRY_SCHEMA = json.loads((ROOT / "schemas/portfolio-entry.schema.json").read_text(encoding="utf-8"))


def validate(schema: dict, item: dict) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(item), key=lambda error: list(error.path))
    if errors:
        raise ValueError("; ".join(error.message for error in errors))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_card(card: dict) -> None:
    validate(CARD_SCHEMA, card)
    memory = card["scoped_memory"]
    evidence_ids = {item["memory_id"] for item in memory["evidence"]}
    hypothesis_ids = {item["memory_id"] for item in memory["hypotheses"]}
    note_ids = {item["memory_id"] for item in memory["untrusted_notes"]}
    if evidence_ids & (hypothesis_ids | note_ids) or hypothesis_ids & note_ids:
        raise ValueError(f"memory tiers overlap for {card['problem_id']}")
    candidate_ids = [item["candidate_id"] for item in card["candidates"]]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError(f"candidate IDs are not unique for {card['problem_id']}")


def validate_entry(entry: dict, cards: dict[str, dict]) -> None:
    validate(ENTRY_SCHEMA, entry)
    card = cards.get(entry["problem_id"])
    if card is None or card["version"] != entry["problem_version"]:
        raise ValueError(f"entry references unknown card/version: {entry['entry_id']}")
    candidate_ids = {item["candidate_id"] for item in card["candidates"]}
    if entry["candidate_id"] not in candidate_ids:
        raise ValueError(f"entry references unknown candidate: {entry['entry_id']}")
    memory = card["scoped_memory"]
    known = {item["memory_id"] for tier in memory.values() if isinstance(tier, list) for item in tier}
    refs = entry["memory_refs"]
    all_refs = refs["evidence_memory_ids"] + refs["hypothesis_memory_ids"] + refs["untrusted_note_ids"]
    if not set(all_refs) <= known:
        raise ValueError(f"entry references unknown memory: {entry['entry_id']}")
    if set(refs["evidence_memory_ids"]) & set(refs["hypothesis_memory_ids"] + refs["untrusted_note_ids"]):
        raise ValueError(f"entry crosses memory authority tiers: {entry['entry_id']}")


def classify_comparison(case: dict) -> str:
    attempt = case["comparison_attempt"]
    if not attempt.get("common_utility") or not attempt.get("endpoint_mapping") or not attempt.get("evidence_basis"):
        return "REJECT_COMPARISON"
    return "REVIEW_REQUIRED"


def replay() -> dict:
    card_paths = [ROOT / "fixtures/portfolio/roman.json", ROOT / "fixtures/portfolio/lime-mortar.json", ROOT / "fixtures/portfolio/battery-cathode.json"]
    cards = {}
    for path in card_paths:
        card = load(path)
        validate_card(card)
        cards[card["problem_id"]] = card
    card_outputs = {"roman-concrete": "PROVISIONAL_BEST", "lime-mortar": "PARETO_SET", "battery-cathode": "ABSTAIN"}
    for problem_id, output in card_outputs.items():
        if output not in cards[problem_id]["allowed_outputs"]:
            raise ValueError(f"card does not allow output {output}: {problem_id}")

    fixture_results = {}
    for path in sorted((ROOT / "fixtures/portfolio").glob("positive.json")):
        case = load(path)
        validate_entry(case["entry"], cards)
        fixture_results[case["case_id"]] = case["expected_status"]
        if case["entry"]["status"] != case["expected_status"]:
            raise ValueError(f"{path.name}: declared status does not match expected")
    for filename in ("contradictory.json", "incomplete.json", "unsupported.json"):
        case = load(ROOT / "fixtures/portfolio" / filename)
        validate_entry(case["entry"], cards)
        if case["entry"]["status"] != case["expected_status"]:
            raise ValueError(f"{filename}: declared status does not match expected")
        fixture_results[case["case_id"]] = case["expected_status"]
    out_of_domain = load(ROOT / "fixtures/portfolio/out-of-domain.json")
    validate_entry(out_of_domain["entry"], cards)
    result = classify_comparison(out_of_domain)
    if result != out_of_domain["expected_status"]:
        raise ValueError(f"out-of-domain: expected {out_of_domain['expected_status']}, got {result}")
    fixture_results[out_of_domain["case_id"]] = result
    return {
        "protocol_version": "gp4.1-cross-question-portfolio",
        "card_outputs": card_outputs,
        "fixture_results": fixture_results,
        "card_count": len(cards),
        "authority": "offline validation only; no network, lab, model, agent, or external communication authority"
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
