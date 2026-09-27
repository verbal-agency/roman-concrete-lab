"""Deterministic G-1 verdict from an adjudicated study-family JSONL ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_families(path: Path) -> list[dict]:
    families: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        for key in ("study_family_id", "tier", "arm_count", "functional_endpoint", "external_replication"):
            if key not in item:
                raise ValueError(f"line {line_number}: missing {key}")
        if item["tier"] not in {"A", "B", "C", "D"}:
            raise ValueError(f"line {line_number}: invalid tier")
        if not isinstance(item["arm_count"], int) or item["arm_count"] < 0:
            raise ValueError(f"line {line_number}: invalid arm_count")
        families.append(item)
    return families


def decide(families: list[dict], *, audit_complete: bool, saturated: bool, human_adjudicated: bool = False) -> dict:
    direct = [item for item in families if item["tier"] == "A"]
    all_direct_adjudicated = all(item.get("adjudication_status") == "adjudicated" for item in direct)
    effective_human_adjudicated = human_adjudicated and all_direct_adjudicated
    direct_arms = sum(item["arm_count"] for item in direct)
    comparable = [item for item in direct if item["functional_endpoint"]]
    external = any(item["external_replication"] for item in direct)
    completeness = [item.get("core_covariate_completeness") for item in direct]
    complete_core = sum(value is not None and value >= 0.70 for value in completeness)
    modelable = (
        audit_complete
        and saturated
        and len(direct) >= 5
        and direct_arms >= 75
        and len(comparable) >= 3
        and external
        and direct
        and complete_core / len(direct) >= 0.70
    )
    replication_required = (
        len(direct) < 3
        or direct_arms < 30
        or not external
        or not direct
    )
    provisional_verdict = "REPLICATION_STUDY_REQUIRED" if replication_required else ("MODELABLE_NOW" if modelable else "EVIDENCE_SYNTHESIS_ONLY")
    if not audit_complete or not saturated or not effective_human_adjudicated:
        verdict = "AUDIT_INCOMPLETE"
    elif modelable:
        verdict = "MODELABLE_NOW"
    elif replication_required:
        verdict = "REPLICATION_STUDY_REQUIRED"
    else:
        verdict = "EVIDENCE_SYNTHESIS_ONLY"
    return {
        "verdict": verdict,
        "provisional_verdict": provisional_verdict,
        "independent_tier_a_families": len(direct),
        "tier_a_arms": direct_arms,
        "tier_a_functional_families": len(comparable),
        "tier_a_external_replication": external,
        "tier_a_core_covariate_completeness_ge_70pct": complete_core,
        "audit_complete": audit_complete,
        "saturated": saturated,
        "human_adjudicated": effective_human_adjudicated,
        "human_adjudication_requested": human_adjudicated,
        "all_direct_families_adjudicated": all_direct_adjudicated,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("families", type=Path)
    parser.add_argument("--audit-complete", action="store_true")
    parser.add_argument("--saturated", action="store_true")
    parser.add_argument("--human-adjudicated", action="store_true")
    args = parser.parse_args()
    print(json.dumps(decide(load_families(args.families), audit_complete=args.audit_complete, saturated=args.saturated, human_adjudicated=args.human_adjudicated), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
