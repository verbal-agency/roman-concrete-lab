"""Deterministic GP1 candidate and hypothesis dossier replay."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

try:
    from tools.literature_audit.decision import decide_exploration_seedability, load_candidates
except ModuleNotFoundError:  # direct script invocation from the repository root
    from decision import decide_exploration_seedability, load_candidates


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATES = ROOT / "data/processed/literature-sufficiency-material-candidates.jsonl"
DEFAULT_SOURCES = ROOT / "data/manifests/literature-sufficiency-sources.jsonl"
DEFAULT_FAMILIES = ROOT / "data/processed/literature-sufficiency-study-families.jsonl"
DEFAULT_SCREENING = ROOT / "data/manifests/literature-sufficiency-screening.csv"
DEFAULT_HYPOTHESES = ROOT / "data/processed/candidate-hypotheses.jsonl"
DEFAULT_CONTEXT = ROOT / "docs/protocols/exploration-contracts.md"
DEFAULT_LANDSCAPE_MAP = ROOT / "data/processed/evidence-landscape.json"
DEFAULT_LANDSCAPE_RUN = ROOT / "artifacts/goals/G-LR/run.json"
DEFAULT_OUTPUT = ROOT / "artifacts/goals/GP1/run.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


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
    families_path: Path = DEFAULT_FAMILIES,
    screening_path: Path = DEFAULT_SCREENING,
    landscape_map_path: Path = DEFAULT_LANDSCAPE_MAP,
    landscape_run_path: Path = DEFAULT_LANDSCAPE_RUN,
    context_path: Path = DEFAULT_CONTEXT,
) -> dict:
    candidates = load_candidates(candidates_path)
    sources = load_jsonl(sources_path)
    families = load_jsonl(families_path)
    hypotheses = load_jsonl(hypotheses_path)
    landscape_map = json.loads(landscape_map_path.read_text(encoding="utf-8"))
    landscape_run = json.loads(landscape_run_path.read_text(encoding="utf-8"))
    if not context_path.exists():
        raise ValueError(f"missing context contract: {context_path}")
    landscape_verdict = landscape_map.get("readiness")
    if landscape_verdict not in {"LANDSCAPE_READY", "LANDSCAPE_INCOMPLETE"}:
        raise ValueError(f"invalid G-LR readiness verdict: {landscape_verdict}")
    if landscape_run.get("readiness") != landscape_verdict:
        raise ValueError("G-LR map/run readiness verdicts do not reconcile")
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
    result = {
        "protocol_version": "gp1.1-candidate-dossier",
        "execution_date": landscape_run.get("execution_date"),
        "replay_command": "python3 tools/literature_audit/gp1_replay.py --write",
        "inputs": {
            "candidate_ledger": {"path": display_path(candidates_path), "sha256": sha256(candidates_path)},
            "source_manifest": {"path": display_path(sources_path), "sha256": sha256(sources_path)},
            "study_family_ledger": {"path": display_path(families_path), "sha256": sha256(families_path)},
            "screening_ledger": {"path": display_path(screening_path), "sha256": sha256(screening_path)},
            "candidate_hypotheses": {"path": display_path(hypotheses_path), "sha256": sha256(hypotheses_path)},
            "context_contract": {"path": display_path(context_path), "sha256": sha256(context_path)},
            "landscape_manifest": {"path": display_path(landscape_map_path), "sha256": sha256(landscape_map_path)},
            "landscape_run": {"path": display_path(landscape_run_path), "sha256": sha256(landscape_run_path)},
        },
        "landscape_gate": {
            "verdict": landscape_verdict,
            "discovery_grade_authorized": landscape_verdict == "LANDSCAPE_READY",
            "landscape_manifest_path": str(landscape_map_path.relative_to(ROOT)) if landscape_map_path.is_relative_to(ROOT) else str(landscape_map_path),
            "landscape_manifest_sha256": sha256(landscape_map_path),
            "landscape_run_id": landscape_run.get("run_id"),
            "permitted_outputs": landscape_map.get("permitted_outputs", []),
            "prohibited_outputs": landscape_map.get("prohibited_outputs", []),
        },
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
        "outputs": {
            "candidate_hypotheses": {"path": "data/processed/candidate-hypotheses.jsonl", "sha256": sha256(hypotheses_path)},
            "dossier": "docs/reports/material-candidate-dossier.md",
            "replay_tool": {"path": "tools/literature_audit/gp1_replay.py", "sha256": sha256(Path(__file__))},
        },
        "authority": {
            "network": "none during replay",
            "model_calls": "none",
            "physical_execution": "prohibited",
            "human_adjudication_before_lab": True,
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ledger", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--families", type=Path, default=DEFAULT_FAMILIES)
    parser.add_argument("--screening", type=Path, default=DEFAULT_SCREENING)
    parser.add_argument("--hypotheses", type=Path, default=DEFAULT_HYPOTHESES)
    parser.add_argument("--landscape-map", type=Path, default=DEFAULT_LANDSCAPE_MAP)
    parser.add_argument("--landscape-run", type=Path, default=DEFAULT_LANDSCAPE_RUN)
    parser.add_argument("--context", type=Path, default=DEFAULT_CONTEXT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = replay(
        args.candidate_ledger,
        args.sources,
        args.hypotheses,
        args.families,
        args.screening,
        args.landscape_map,
        args.landscape_run,
        args.context,
    )
    if args.write:
        DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
