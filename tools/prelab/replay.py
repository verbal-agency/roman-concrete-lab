"""Replay the GP2 offline ranking and result-decision fixtures."""

from __future__ import annotations

import json
from pathlib import Path

try:
    from tools.prelab.decision import classify_result
except ModuleNotFoundError:  # direct script invocation from the repository root
    from decision import classify_result


ROOT = Path(__file__).resolve().parents[2]


def replay() -> dict:
    ranking = json.loads((ROOT / "data/processed/gp2-conditional-ranking.json").read_text(encoding="utf-8"))
    expected = {"PROVISIONAL_BEST", "PARETO_SET", "ABSTAIN"}
    if ranking["ranking_status"] not in expected:
        raise ValueError("invalid ranking status")
    entries = ranking["entries"]
    if ranking["provisional_best"]["candidate_id"] not in {entry["candidate_id"] for entry in entries}:
        raise ValueError("provisional best is not in ranking entries")
    fixture_statuses = {}
    for path in sorted((ROOT / "fixtures/prelab").glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        actual = classify_result(case["result"])
        if actual != case["expected_status"]:
            raise ValueError(f"{path.name}: expected {case['expected_status']}, got {actual}")
        fixture_statuses[case["case_id"]] = actual
    return {
        "protocol_version": "gp2.1-conditional-ranking",
        "ranking_status": ranking["ranking_status"],
        "provisional_best": ranking["provisional_best"]["candidate_id"],
        "entry_count": len(entries),
        "fixture_statuses": fixture_statuses,
        "authority": "offline validation only; no lab or safety authority",
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
