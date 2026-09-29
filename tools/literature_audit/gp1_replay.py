"""Deterministic GP1 candidate and hypothesis dossier replay."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from tools.literature_audit.decision import decide_exploration_seedability, load_candidates
except ModuleNotFoundError:  # direct script invocation from the repository root
    from decision import decide_exploration_seedability, load_candidates


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{line_number}: expected object")
        records.append(item)
    return records


def replay(
    candidates_path: Path,
    sources_path: Path,
    hypotheses_path: Path,
    families_path: Path = Path("data/processed/literature-sufficiency-study-families.jsonl"),
    screening_path: Path = Path("data/manifests/literature-sufficiency-screening.csv"),
) -> dict:
    candidates = load_candidates(candidates_path)
    sources = load_jsonl(sources_path)
    families = load_jsonl(families_path)
    hypotheses = load_jsonl(hypotheses_path)
    with screening_path.open(encoding="utf-8", newline="") as handle:
        screening = list(csv.DictReader(handle))
    candidate_ids = [item["candidate_id"] for item in candidates]
    source_ids = {item.get("record_id") for item in sources}
    family_ids = {item.get("study_family_id") for item in families}
    screening_by_record = {item.get("record_id"): item for item in screening}
    if len(screening_by_record) != len(screening):
        raise ValueError("screening record IDs must be unique")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("candidate IDs must be unique")
    for candidate in candidates:
        missing = set(candidate["supporting_record_ids"]) - source_ids
        if missing:
            raise ValueError(f"{candidate['candidate_id']}: missing source IDs {sorted(missing)}")
        missing_screening = set(candidate["supporting_record_ids"]) - screening_by_record.keys()
        if missing_screening:
            raise ValueError(f"{candidate['candidate_id']}: missing screening IDs {sorted(missing_screening)}")
        if not candidate.get("exact_locator"):
            raise ValueError(f"{candidate['candidate_id']}: exact_locator is required")
    for record_id, row in screening_by_record.items():
        family_id = row.get("study_family_id")
        if family_id and family_id not in {"not_applicable"} and family_id not in family_ids:
            raise ValueError(f"{record_id}: screening references unknown study family {family_id}")
    hypothesis_ids = [item.get("hypothesis_id") for item in hypotheses]
    if len(hypothesis_ids) != len(set(hypothesis_ids)) or any(not item for item in hypothesis_ids):
        raise ValueError("hypothesis IDs must be unique and non-empty")
    for hypothesis in hypotheses:
        if hypothesis.get("candidate_id") not in candidate_ids:
            raise ValueError(f"hypothesis references unknown candidate: {hypothesis.get('candidate_id')}")
        for field in ("intervention", "comparator", "measurable_outcome", "applicable_domain", "falsification_observation", "rival_predictions"):
            if not hypothesis.get(field):
                raise ValueError(f"{hypothesis.get('hypothesis_id')}: missing {field}")
        if hypothesis.get("claim_type") not in {"REPORTED", "DERIVED", "PROPOSED", "UNRESOLVED"}:
            raise ValueError(f"{hypothesis.get('hypothesis_id')}: invalid claim_type")
    seedability = decide_exploration_seedability(candidates)
    statuses = {}
    for candidate in candidates:
        supported_records = candidate["supporting_record_ids"]
        statuses[candidate["candidate_id"]] = {
            "provisional_candidate_verdict": candidate["provisional_candidate_verdict"],
            "adjudication_status": candidate["adjudication_status"],
            "exploration_seedable": candidate["candidate_id"] in seedability["seedable_candidate_ids"],
            "study_family_ids": sorted(
                {screening_by_record[record_id]["study_family_id"] for record_id in supported_records}
            ),
        }
    return {
        "protocol_version": "gp1.1-candidate-dossier",
        "candidate_count": len(candidates),
        "hypothesis_count": len(hypotheses),
        "study_family_count": len(families),
        "reconciled_supporting_record_count": len(
            {record_id for candidate in candidates for record_id in candidate["supporting_record_ids"]}
        ),
        "provisional_plausible_candidate_count": sum(
            item["provisional_candidate_verdict"] == "LAB_CANDIDATE_PLAUSIBLE" for item in candidates
        ),
        "exploration_seedability": seedability,
        "candidate_statuses": statuses,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ledger", type=Path, default=Path("data/processed/literature-sufficiency-material-candidates.jsonl"))
    parser.add_argument("--sources", type=Path, default=Path("data/manifests/literature-sufficiency-sources.jsonl"))
    parser.add_argument("--families", type=Path, default=Path("data/processed/literature-sufficiency-study-families.jsonl"))
    parser.add_argument("--screening", type=Path, default=Path("data/manifests/literature-sufficiency-screening.csv"))
    parser.add_argument("--hypotheses", type=Path, default=Path("data/processed/candidate-hypotheses.jsonl"))
    args = parser.parse_args()
    print(json.dumps(replay(args.candidate_ledger, args.sources, args.hypotheses, args.families, args.screening), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
