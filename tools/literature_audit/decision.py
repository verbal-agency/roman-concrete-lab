"""Deterministic G-1 gates from study-family and candidate JSONL ledgers."""

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


def load_candidates(path: Path) -> list[dict]:
    candidates: list[dict] = []
    required = (
        "candidate_id",
        "supporting_record_ids",
        "material_identity_status",
        "process_identity_status",
        "comparator_status",
        "functional_endpoint_status",
        "lab_handoff_status",
        "provisional_candidate_verdict",
        "adjudication_status",
    )
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        for key in required:
            if key not in item:
                raise ValueError(f"candidate line {line_number}: missing {key}")
        if item["provisional_candidate_verdict"] not in {"LAB_CANDIDATE_PLAUSIBLE", "LAB_CANDIDATE_NOT_ESTABLISHED"}:
            raise ValueError(f"candidate line {line_number}: invalid provisional verdict")
        candidates.append(item)
    return candidates


def decide_material_candidates(candidates: list[dict], *, human_adjudicated: bool = False) -> dict:
    plausible = [item for item in candidates if item["provisional_candidate_verdict"] == "LAB_CANDIDATE_PLAUSIBLE"]
    all_adjudicated = all(item.get("adjudication_status") == "adjudicated" for item in candidates)
    effective_human_adjudicated = human_adjudicated and all_adjudicated
    if not candidates or not effective_human_adjudicated:
        verdict = "AUDIT_INCOMPLETE"
    elif plausible:
        verdict = "LAB_CANDIDATE_PLAUSIBLE"
    else:
        verdict = "LAB_CANDIDATE_NOT_ESTABLISHED"
    return {
        "verdict": verdict,
        "provisional_verdict": "LAB_CANDIDATE_PLAUSIBLE" if plausible else "LAB_CANDIDATE_NOT_ESTABLISHED",
        "candidate_count": len(candidates),
        "provisional_plausible_candidate_count": len(plausible),
        "human_adjudicated": effective_human_adjudicated,
        "human_adjudication_requested": human_adjudicated,
        "all_candidates_adjudicated": all_adjudicated,
    }


def decide_exploration_seedability(candidates: list[dict]) -> dict:
    """Decide whether the evidence can seed bounded, problem-specific exploration.

    This is intentionally weaker than the material-candidate and modelability
    verdicts. It may remain provisional and never authorizes lab work,
    performance claims, or a generalizable predictive model.
    """
    seedable: list[dict] = []
    for item in candidates:
        material = str(item.get("material_identity_status", ""))
        process = str(item.get("process_identity_status", ""))
        endpoint = str(item.get("functional_endpoint_status", ""))
        if (
            item.get("provisional_candidate_verdict") == "LAB_CANDIDATE_PLAUSIBLE"
            and item.get("supporting_record_ids")
            and item.get("exact_locator")
            and material not in {"", "unknown", "uninspectable"}
            and process not in {"", "unknown", "uninspectable"}
            and endpoint not in {"", "none", "unknown", "not_reported"}
        ):
            seedable.append(item)
    return {
        "verdict": "EXPLORATION_SEEDABLE" if seedable else "EXPLORATION_NOT_SEEDABLE",
        "seedable_candidate_ids": [item["candidate_id"] for item in seedable],
        "candidate_count": len(candidates),
        "seedable_candidate_count": len(seedable),
        "provisional_only": True,
        "human_adjudication_required_before_lab": True,
    }


def decide(
    families: list[dict],
    *,
    audit_complete: bool,
    saturated: bool,
    human_adjudicated: bool = False,
    candidates: list[dict] | None = None,
) -> dict:
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
    result = {
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
    if candidates is not None:
        result["material_candidate"] = decide_material_candidates(candidates, human_adjudicated=human_adjudicated)
        result["exploration_seedability"] = decide_exploration_seedability(candidates)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("families", type=Path)
    parser.add_argument("--audit-complete", action="store_true")
    parser.add_argument("--saturated", action="store_true")
    parser.add_argument("--human-adjudicated", action="store_true")
    parser.add_argument("--candidate-ledger", type=Path)
    args = parser.parse_args()
    candidates = load_candidates(args.candidate_ledger) if args.candidate_ledger else None
    print(json.dumps(decide(load_families(args.families), audit_complete=args.audit_complete, saturated=args.saturated, human_adjudicated=args.human_adjudicated, candidates=candidates), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
