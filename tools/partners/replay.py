"""Replay the GP3 offline facility-readiness fixtures."""

from __future__ import annotations

import json
from pathlib import Path

try:
    from tools.partners.decision import classify_response
except ModuleNotFoundError:  # direct script invocation from the repository root
    from decision import classify_response


ROOT = Path(__file__).resolve().parents[2]


def replay() -> dict:
    results = {}
    for path in sorted((ROOT / "fixtures/partners").glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        actual = classify_response(case["response"])
        if actual != case["expected_gate"]:
            raise ValueError(f"{path.name}: expected {case['expected_gate']}, got {actual}")
        if case["response"]["gate_result"] != actual:
            raise ValueError(f"{path.name}: declared gate does not match replay")
        results[case["case_id"]] = actual
    return {
        "protocol_version": "gp3.1-partner-readiness",
        "fixture_count": len(results),
        "gate_results": results,
        "authority": "offline validation only; no outbound communication or safety authority",
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
