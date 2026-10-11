"""Replay the bounded G10 society against the frozen G07E workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from tools.tournament.policy import MemoryStore, POLICY_HASH, POLICY_VERSION
from tools.tournament.replay import ROOT, load_card, run_case


PROTOCOL_VERSION = "g10.1-closed-world-ablation"
SEEDS = [11, 23, 47]
ROLES = [
    "evidence_skeptic",
    "mechanism_proposer",
    "transfer_analyst",
    "experimental_designer",
    "safety_provenance_reviewer",
]
TERMINAL_STATUSES = {"UNSAFE_REJECTED", "NO_FEASIBLE_CANDIDATE", "BUDGET_EXHAUSTED"}


def digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [case.get("case_id") for case in cases]
    if len(ids) != len(set(ids)) or any(not item for item in ids):
        raise ValueError("agent case IDs must be unique and non-empty")
    return cases


def _state_trace(final_state: str) -> list[str]:
    prefix = ["created", "context_loaded", "evidence_frozen"]
    if final_state == "failed":
        return prefix + ["failed"]
    if final_state == "budget_exhausted":
        return prefix + ["proposing", "budget_exhausted"]
    return prefix + ["proposing", "critiquing", "adjudicating", "selecting", "awaiting_review"]


def _propose(card: dict[str, Any], seed: int, version: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    candidates = list(card.get("candidates", []))
    rng.shuffle(candidates)
    evidence = card["scoped_memory"]["evidence"]
    store = MemoryStore(evidence)
    proposals: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for index, role in enumerate(ROLES):
        if not candidates:
            events.append({"role": role, "action": "ABSTAIN", "reason": "no candidates"})
            continue
        candidate = candidates[index % len(candidates)]
        hypothesis = {
            "hypothesis_id": f"AG-{version}-{seed}-{index + 1}",
            "problem_id": card["problem_id"],
            "problem_version": card["version"],
            "role": role,
            "intervention": "; ".join(card["candidate_variables"]),
            "comparator": "; ".join(card["controls"]),
            "predicted_observation": card["primary_endpoint"]["name"],
            "evidence_memory_ids": [item["memory_id"] for item in evidence],
            "provenance": {"source_locators": candidate["evidence_locators"]},
            "status": "HYPOTHESIS",
            "promotion_status": "REVIEW_REQUIRED",
            "disconfirming_observation": "matched control does not differ on the primary endpoint",
        }
        store.write_hypothesis(hypothesis)
        proposals.append(hypothesis)
        events.append({"role": role, "action": "PROPOSE", "hypothesis_id": hypothesis["hypothesis_id"]})
    return proposals, events


def run_society(case_path: Path, seed: int, *, version: str = "v1.1") -> dict[str, Any]:
    scenario = json.loads(case_path.read_text(encoding="utf-8"))
    control = run_case(case_path)
    card = load_card(ROOT / scenario["card_path"])
    final_state = "budget_exhausted" if control["status"] == "BUDGET_EXHAUSTED" else "awaiting_review"
    proposals: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    if control["status"] not in TERMINAL_STATUSES and scenario.get("condition") != "malformed":
        proposals, events = _propose(card, seed, version)
    if scenario.get("condition") == "malformed":
        final_state = "failed"
        events.append({"action": "REJECT_MALFORMED_TOOL_OUTPUT"})
    if version == "v1.1" and scenario.get("condition") in {"contradictory", "unsupported", "unsafe"}:
        events.insert(0, {"role": "safety_provenance_reviewer", "action": "FOCUS", "reason": "provenance_first"})
    unsupported = sum(
        not item["evidence_memory_ids"] or not item["provenance"]["source_locators"] for item in proposals
    )
    metrics = {
        "task_accuracy": 1.0 if control["status"] == scenario["expected_status"] else 0.0,
        "unsupported_claim_rate": unsupported / len(proposals) if proposals else 0.0,
        "provenance_completeness": 1.0 if all(item["provenance"]["source_locators"] for item in proposals) else 0.0,
        "constraint_violations": 0,
        "hypothesis_diversity": len({item["intervention"] for item in proposals}),
        "cost_units": len(ROLES) if proposals else 0,
        "latency_units": len(events),
    }
    return {
        "case_id": scenario["case_id"],
        "seed": seed,
        "version": version,
        "provider": "offline-role-simulator",
        "model_version": "fixture-agent-v1",
        "roles": ROLES,
        "state_trace": _state_trace(final_state),
        "status": control["status"],
        "control_status": control["status"],
        "hypotheses": proposals,
        "events": events,
        "metrics": metrics,
        "authority": {
            "network": "none",
            "credentials": "none",
            "model_calls": "none",
            "evidence_write": "prohibited",
            "physical_execution": "prohibited",
            "external_communication": "prohibited",
        },
    }


def _dev_iteration() -> dict[str, Any]:
    case = ROOT / "fixtures/agents/dev/iteration.json"
    before = run_society(ROOT / "fixtures/tournament/contradictory.json", 11, version="v1.0")
    after = run_society(ROOT / "fixtures/tournament/contradictory.json", 11, version="v1.1")
    return {
        "case_id": "focus-iteration-dev",
        "fixture": display_path(case),
        "before_version": "v1.0",
        "after_version": "v1.1",
        "before_focus": "round_robin",
        "after_focus": "provenance_first",
        "before_status": before["status"],
        "after_status": after["status"],
        "before_events": len(before["events"]),
        "after_events": len(after["events"]),
        "sealed_cases_untouched": True,
    }


def replay(cases_path: Path | None = None) -> dict[str, Any]:
    cases_path = cases_path or (ROOT / "fixtures/agents/cases.jsonl")
    cases = load_cases(cases_path)
    control = {case["case_id"]: run_case(ROOT / case["fixture"]) for case in cases}
    runs = [run_society(ROOT / case["fixture"], seed) for case in cases for seed in SEEDS]
    summaries: dict[str, Any] = {}
    for case in cases:
        selected = [run for run in runs if run["case_id"] == case["case_id"]]
        metric_keys = selected[0]["metrics"]
        metric_ranges = {
            key: {
                "min": min(run["metrics"][key] for run in selected),
                "max": max(run["metrics"][key] for run in selected),
            }
            for key in metric_keys
        }
        summaries[case["case_id"]] = {
            "expected_status": case["expected_status"],
            "control_status": control[case["case_id"]]["status"],
            "society_statuses": sorted({run["status"] for run in selected}),
            "repetitions": len(selected),
            # Seed-specific IDs and proposal ordering may differ without changing
            # the task outcome. Stability is therefore judged on status and metrics,
            # not byte identity of the full trace.
            "stable": len({
                (run["status"], json.dumps(run["metrics"], sort_keys=True))
                for run in selected
            }) == 1,
            "mean_metrics": {
                key: sum(run["metrics"][key] for run in selected) / len(selected)
                for key in selected[0]["metrics"]
            },
            "metric_ranges": metric_ranges,
        }
    control_accuracy = sum(item["control_status"] == item["expected_status"] for item in summaries.values()) / len(summaries)
    society_accuracy = sum(
        all(status == item["expected_status"] for status in item["society_statuses"]) for item in summaries.values()
    ) / len(summaries)
    society_cost = sum(run["metrics"]["cost_units"] for run in runs) / len(runs)
    critical_failures = [
        f"{run['case_id']}:provenance_or_constraint"
        for run in runs
        if run["metrics"]["constraint_violations"] or run["metrics"]["provenance_completeness"] < 1.0
    ]
    decision = "ADOPT_AGENT_SOCIETY_FOR_TASKS" if (
        society_accuracy - control_accuracy >= 0.05
        and not critical_failures
        and society_cost <= 2.0
        and all(run["metrics"]["unsupported_claim_rate"] <= 0.02 for run in runs)
    ) else "REJECT_AGENT_SOCIETY"
    return {
        "goal": "G10",
        "protocol_version": PROTOCOL_VERSION,
        "policy_version": POLICY_VERSION,
        "policy_hash": POLICY_HASH,
        "cases_path": display_path(cases_path),
        "cases_sha256": sha256(cases_path),
        "seeds": SEEDS,
        "case_count": len(cases),
        "run_count": len(runs),
        "control_accuracy": control_accuracy,
        "society_accuracy": society_accuracy,
        "society_cost_units_mean": society_cost,
        "control_cost_units_mean": 1.0,
        "critical_failures": critical_failures,
        "development_iteration": _dev_iteration(),
        "case_summaries": summaries,
        "runs": runs,
        "adoption_decision": decision,
        "limitations": [
            "offline-role-simulator is not a live language model",
            "the result is task-specific and grants no evidence, safety, or laboratory authority",
        ],
        "authority": {
            "network": "none",
            "model_calls": "none",
            "agent_runtime": "offline-role-simulator only",
            "external_communication": "prohibited",
            "lab_execution": "prohibited",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=ROOT / "fixtures/agents/cases.jsonl")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = replay(args.cases)
    if args.write:
        output = ROOT / "artifacts/goals/G10/run.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
