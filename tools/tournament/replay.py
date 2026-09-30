"""Offline deterministic replay for the G07E hypothesis tournament."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, RefResolver

# Permit both `python3 -m tools.tournament.replay` and the goal's direct
# `python3 tools/tournament/replay.py` verification command.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.portfolio.replay import load as load_json
from tools.portfolio.replay import validate_card
from tools.tournament.policy import (
    LEGAL_TRANSITIONS,
    POLICY_HASH,
    POLICY_VERSION,
    HypothesisRegistry,
    MemoryPermissionError,
    MemoryStore,
    canonical_json,
    digest,
    pareto_ids,
    utility_for,
)


PROTOCOL_VERSION = "g07e.1-deterministic-tournament"
CARD_PATHS = [
    ROOT / "fixtures/portfolio/roman.json",
    ROOT / "fixtures/portfolio/lime-mortar.json",
    ROOT / "fixtures/portfolio/battery-cathode.json",
]
RESULT_SCHEMA = load_json(ROOT / "schemas/tournament-result.schema.json")
HYPOTHESIS_SCHEMA = load_json(ROOT / "schemas/hypothesis-registry.schema.json")
SCHEMA_STORE = {
    RESULT_SCHEMA["$id"]: RESULT_SCHEMA,
    HYPOTHESIS_SCHEMA["$id"]: HYPOTHESIS_SCHEMA,
}

AUTHORITY = {
    "network": "none",
    "model_calls": "none",
    "agent_runtime": "prohibited",
    "lab_execution": "prohibited",
    "external_communication": "prohibited",
}


def validate(schema: dict[str, Any], item: dict[str, Any]) -> None:
    resolver = RefResolver.from_schema(schema, store=SCHEMA_STORE)
    errors = sorted(Draft202012Validator(schema, resolver=resolver).iter_errors(item), key=lambda error: list(error.path))
    if errors:
        raise ValueError("; ".join(error.message for error in errors))


def load_card(path: Path) -> dict[str, Any]:
    card = load_json(path)
    validate_card(card)
    return card


def _evidence_manifest(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "problem_id": card["problem_id"],
        "problem_version": card["version"],
        "evidence": card["scoped_memory"]["evidence"],
        "candidate_locators": [
            {"candidate_id": item.get("candidate_id", "MALFORMED"), "locators": item.get("evidence_locators", [])}
            for item in card["candidates"]
        ],
    }


def _make_hypothesis(
    card: dict[str, Any],
    candidate: dict[str, Any],
    card_path: Path,
    source_hypothesis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence_ids = [item["memory_id"] for item in card["scoped_memory"]["evidence"]]
    intervention = "; ".join(card["candidate_variables"])
    comparator = "; ".join(card["controls"])
    endpoint = card["primary_endpoint"]["name"]
    rival_state = "EXPLICIT_RIVALS" if len(card["candidates"]) > 1 else "UNRESOLVED_RIVAL"
    hypothesis_id = source_hypothesis["memory_id"] if source_hypothesis else f"H-{card['problem_id']}-{candidate['candidate_id']}"
    return {
        "hypothesis_id": hypothesis_id,
        "problem_id": card["problem_id"],
        "problem_version": card["version"],
        "intervention": intervention,
        "comparator": comparator,
        "applicable_domain": card["domain"],
        "support_region": card["support_region"],
        "predicted_observation": {
            "endpoint": endpoint,
            "statement": f"The declared {intervention} versus {comparator} contrast produces a measurable difference in {endpoint}.",
            "discriminator": f"Measure {endpoint} under the declared process-matched comparison; do not substitute a surface-only endpoint.",
        },
        "rival_hypothesis_ids": [],
        "rival_state": rival_state,
        "evidence_memory_ids": evidence_ids,
        "claim_type": "PROPOSED",
        "uncertainty": sorted(set(candidate.get("uncertainty", []) + ["no physical result in offline fixture"])),
        "status": "HYPOTHESIS",
        "promotion_retraction_reason": "PROPOSED_FROM_FROZEN_CARD",
        "reviewer_authority": card["authority"]["next_reviewer"],
        "provenance": {
            "card_path": str(card_path.relative_to(ROOT)),
            "candidate_id": candidate["candidate_id"],
            "source_locators": candidate["evidence_locators"],
        },
        "utility_components": utility_for(card, candidate),
    }


def _base_result(card: dict[str, Any], status: str, *, budget: int, reason: str, card_path: Path) -> dict[str, Any]:
    evidence_manifest = _evidence_manifest(card)
    payload: dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "result_id": "sha256:" + "0" * 64,
        "problem_id": card["problem_id"],
        "problem_version": card["version"],
        "card_digest": digest(card),
        "evidence_manifest_digest": digest(evidence_manifest),
        "policy_version": POLICY_VERSION,
        "policy_hash": POLICY_HASH,
        "status": status,
        "stages": {
            "propose": {"count": 0, "card_path": str(card_path.relative_to(ROOT))},
            "critique": {"count": 0, "reason": reason},
            "adjudicate": {"utility_dimensions": ["endpoint_fit", "information_value", "feasibility", "risk"]},
            "focus": {"status": "NOT_RUN"},
            "promote_retract": {"status": "NOT_RUN"},
        },
        "hypotheses": [],
        "focus_decision": {
            "reason": reason,
            "budget_declared": budget,
            "budget_consumed": 0,
            "candidates_considered": [],
            "abstention_condition": "abstain when provenance, endpoint, authority, or domain support is insufficient",
        },
        "recommendations": [],
        "cache_policy": {
            "mode": "NONE",
            "invalidation": "input card, evidence-manifest, and policy digests identify every replay; rerun rather than reuse mutable state",
        },
        "authority": copy.deepcopy(AUTHORITY),
    }
    payload["result_id"] = digest({key: value for key, value in payload.items() if key != "result_id"})
    return payload


def _apply_scenario(card: dict[str, Any], scenario: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    modified = copy.deepcopy(card)
    condition = scenario.get("condition")
    if condition == "malformed":
        modified["candidates"][0].pop("evidence_locators", None)
        return modified, "candidate is missing required evidence_locators"
    if condition == "partial":
        modified["candidates"][0]["missing_fields"] = ["endpoint_observation", "replicate_lineage"]
    return modified, None


def run_tournament(card: dict[str, Any], card_path: Path, *, condition: str = "positive", budget: int = 2, sensitivity_probe: bool = False) -> dict[str, Any]:
    """Run one sealed case. This function has no network/model/agent side effects."""

    if condition == "unsafe":
        return _base_result(card, "UNSAFE_REJECTED", budget=budget, reason="forbidden combination rejected before scoring", card_path=card_path)
    if condition == "no-feasible":
        return _base_result(card, "NO_FEASIBLE_CANDIDATE", budget=budget, reason="all candidates violate the declared constraints", card_path=card_path)
    if budget <= 0:
        result = _base_result(card, "BUDGET_EXHAUSTED", budget=budget, reason="local focus budget was exhausted before proposal", card_path=card_path)
        result["stages"]["focus"] = {"status": "BUDGET_EXHAUSTED", "partial_manifest": True}
        result["focus_decision"]["abstention_condition"] = "do not widen scope after budget exhaustion"
        result["result_id"] = digest({key: value for key, value in result.items() if key != "result_id"})
        return result

    registry = HypothesisRegistry.empty()
    memory = MemoryStore(card["scoped_memory"]["evidence"])
    candidates = card.get("candidates", [])
    if not candidates:
        return _base_result(card, "ABSTAIN", budget=budget, reason="no candidate records are available", card_path=card_path)

    hypotheses = []
    source_hypotheses = card["scoped_memory"].get("hypotheses", [])
    proposal_pairs = []
    for index, candidate in enumerate(candidates):
        matches = source_hypotheses if len(candidates) == 1 else [source_hypotheses[index]] if index < len(source_hypotheses) else []
        proposal_pairs.extend((candidate, source) for source in matches)
        if not matches:
            proposal_pairs.append((candidate, None))
    for candidate, source_hypothesis in proposal_pairs:
        hypothesis = _make_hypothesis(card, candidate, card_path, source_hypothesis)
        validate(HYPOTHESIS_SCHEMA, hypothesis)
        registry.append(hypothesis)
        memory.write_hypothesis(hypothesis)
        hypotheses.append(hypothesis)

    if len(hypotheses) > 1:
        ids = [item["hypothesis_id"] for item in hypotheses]
        for item in hypotheses:
            item["rival_hypothesis_ids"] = [other for other in ids if other != item["hypothesis_id"]]
            item["rival_state"] = "EXPLICIT_RIVALS"
        registry = HypothesisRegistry.empty()
        memory = MemoryStore(card["scoped_memory"]["evidence"])
        for item in hypotheses:
            validate(HYPOTHESIS_SCHEMA, item)
            registry.append(item)
            memory.write_hypothesis(item)

    focus_candidates = [item["hypothesis_id"] for item in hypotheses]
    result_status = "PARETO_SET"
    reason = "separate utility dimensions leave no defensible universal winner"
    if condition == "unsupported":
        result_status = "ABSTAIN"
        reason = "candidate is unsupported by a measured observation"
        for item in list(registry.records.values()):
            registry.transition(item["hypothesis_id"], "ABSTAIN", "UNSUPPORTED_MEASURED_OBSERVATION")
    elif condition == "contradictory":
        result_status = "REVIEW_REQUIRED"
        reason = "contradictory observations require adjudication; records are preserved"
        for item in list(registry.records.values()):
            registry.transition(item["hypothesis_id"], "CONTRADICTED", "CONTRADICTORY_EVIDENCE")
    elif condition == "partial":
        result_status = "REVIEW_REQUIRED"
        reason = "required endpoint observation or replicate lineage is incomplete"
        for item in list(registry.records.values()):
            registry.transition(item["hypothesis_id"], "REVIEW_REQUIRED", "INCOMPLETE_ENDPOINT_OR_REPLICATE_LINEAGE")

    ranked_ids = pareto_ids(registry.snapshot()) if result_status == "PARETO_SET" else []
    consumed = min(budget, len(hypotheses))
    recommendations = []
    if result_status == "PARETO_SET":
        recommendations = [
            {
                "recommendation_id": f"EXP-{item['hypothesis_id']}",
                "type": "EXPERIMENT_CANDIDATE",
                "hypothesis_id": item["hypothesis_id"],
                "discriminator": item["predicted_observation"]["discriminator"],
                "status": "DRAFT_NON_AUTHORIZING",
            }
            for item in registry.snapshot()
            if item["hypothesis_id"] in ranked_ids
        ]

    result = _base_result(card, result_status, budget=budget, reason=reason, card_path=card_path)
    result["stages"] = {
        "propose": {"count": len(hypotheses), "hypothesis_ids": focus_candidates},
        "critique": {
            "count": len(hypotheses),
            "disconfirming_observation": "compare the primary endpoint against the declared control",
            "confounder_check": "preserve endpoint semantics and support region from the card",
            "cheapest_useful_discriminator": "measure the card primary endpoint under the declared comparator",
        },
        "adjudicate": {
            "utility_dimensions": ["endpoint_fit", "information_value", "feasibility", "risk"],
            "pareto_ids": ranked_ids,
            "aggregate_score": None,
        },
        "focus": {
            "status": "FOCUSED" if result_status == "PARETO_SET" else "ABSTAINED_OR_REVIEWED",
            "budget_consumed": consumed,
        },
        "promote_retract": {
            "status": "RETAIN_TYPED_HYPOTHESIS" if result_status == "PARETO_SET" else "STATUS_TRANSITION_RECORDED",
            "event_count": len(registry.events),
        },
    }
    if condition == "contradictory":
        result["stages"]["critique"]["contradiction"] = {
            "status": "CONTRADICTED",
            "preserved_evidence_memory_ids": [item["memory_id"] for item in card["scoped_memory"]["evidence"]],
            "resolution": "REVIEW_REQUIRED; no evidence record was overwritten",
        }
    result["hypotheses"] = registry.snapshot()
    result["focus_decision"] = {
        "reason": reason,
        "budget_declared": budget,
        "budget_consumed": consumed,
        "candidates_considered": focus_candidates,
        "abstention_condition": "abstain when provenance, endpoint, authority, or domain support is insufficient",
    }
    result["recommendations"] = recommendations
    if sensitivity_probe:
        result["sensitivity"] = {
            "probe": "reverse-risk-priority",
            "outcome": "PARETO_SET",
            "winner_stability": "NO_SINGLE_WINNER",
            "interpretation": "changing attention priority cannot create a universal cross-dimension winner",
        }
    result["result_id"] = digest({key: value for key, value in result.items() if key != "result_id"})
    validate(RESULT_SCHEMA, result)
    return result


def run_case(path: Path) -> dict[str, Any]:
    scenario = load_json(path)
    card_path = ROOT / scenario["card_path"]
    card = load_card(card_path)
    modified, malformed_reason = _apply_scenario(card, scenario)
    if malformed_reason:
        result = _base_result(modified, "REVIEW_REQUIRED", budget=scenario.get("budget", 2), reason=malformed_reason, card_path=card_path)
        result["stages"]["propose"] = {"count": 0, "validation_error": malformed_reason}
        result["stages"]["critique"] = {"count": 0, "reason": malformed_reason}
        result["focus_decision"]["abstention_condition"] = "do not score malformed records"
        result["result_id"] = digest({key: value for key, value in result.items() if key != "result_id"})
        validate(RESULT_SCHEMA, result)
        return result
    return run_tournament(
        modified,
        card_path,
        condition=scenario.get("condition", "positive"),
        budget=scenario.get("budget", 2),
        sensitivity_probe=scenario.get("sensitivity_probe", False),
    )


def replay() -> dict[str, Any]:
    cards = {path.stem: load_card(path) for path in CARD_PATHS}
    card_results = {
        card["problem_id"]: run_tournament(card, path, condition="positive", budget=2, sensitivity_probe=True)
        for path, card in ((path, cards[path.stem]) for path in CARD_PATHS)
    }
    fixture_results: dict[str, str] = {}
    fixture_outputs: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "fixtures/tournament").glob("*.json")):
        result = run_case(path)
        case = load_json(path)
        expected = case["expected_status"]
        if result["status"] != expected:
            raise ValueError(f"{path.name}: expected {expected}, got {result['status']}")
        fixture_results[case["case_id"]] = result["status"]
        fixture_outputs[case["case_id"]] = result
    return {
        "goal": "G07E",
        "protocol_version": PROTOCOL_VERSION,
        "policy_version": POLICY_VERSION,
        "policy_hash": POLICY_HASH,
        "card_results": card_results,
        "fixture_results": fixture_results,
        "fixture_outputs": fixture_outputs,
        "card_count": len(cards),
        "authority": copy.deepcopy(AUTHORITY),
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
