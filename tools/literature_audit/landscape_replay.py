"""Build and replay the deterministic G-LR landscape/evidence map.

The replay consumes the frozen G-1 ledgers. It does not fetch papers, infer
measurements, or promote screening judgments to scientific evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES = ROOT / "data/manifests/literature-sufficiency-sources.jsonl"
DEFAULT_SCREENING = ROOT / "data/manifests/literature-sufficiency-screening.csv"
DEFAULT_FAMILIES = ROOT / "data/processed/literature-sufficiency-study-families.jsonl"
DEFAULT_CANDIDATES = ROOT / "data/processed/literature-sufficiency-material-candidates.jsonl"
DEFAULT_ACCESS = ROOT / "data/manifests/literature-sufficiency-access-register.csv"
DEFAULT_DECISION = ROOT / "artifacts/goals/G-1/decision.json"
DEFAULT_PROTOCOL = ROOT / "docs/protocols/landscape-readiness.md"
DEFAULT_OUTPUT = ROOT / "artifacts/goals/G-LR"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    """Keep manifests portable for repository and temporary fixture paths."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object")
        records.append(value)
    return records


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def index_unique(records: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        value = record.get(key)
        if not value:
            raise ValueError(f"{label}: missing {key}")
        if value in result:
            raise ValueError(f"{label}: duplicate {key} {value}")
        result[value] = record
    return result


def split_urls(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def field_state(status: str, value: Any = None, locator: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"status": status}
    if value not in (None, ""):
        result["value"] = value
    if locator:
        result["locator"] = locator
    return result


def run_id(protocol_version: str, input_hashes: dict[str, str]) -> str:
    """Return a stable snapshot identity; any input/protocol change yields a new run."""
    payload = json.dumps(
        {"protocol_version": protocol_version, "inputs": input_hashes},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def build_landscape(
    sources_path: Path,
    screening_path: Path,
    families_path: Path,
    candidates_path: Path,
    access_path: Path,
    decision_path: Path,
    protocol_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    sources = index_unique(load_jsonl(sources_path), "record_id", "sources")
    screening = index_unique(load_csv(screening_path), "record_id", "screening")
    families = index_unique(load_jsonl(families_path), "study_family_id", "families")
    candidates = load_jsonl(candidates_path)
    access = index_unique(load_csv(access_path), "record_id", "access register")

    source_ids = set(sources)
    if set(screening) != source_ids:
        raise ValueError("source/screening IDs do not reconcile")
    candidate_ids_by_record: dict[str, list[str]] = {record_id: [] for record_id in sources}
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id")
        if not candidate_id:
            raise ValueError("candidate missing candidate_id")
        for record_id in candidate.get("supporting_record_ids", []):
            if record_id not in sources:
                raise ValueError(f"candidate {candidate_id} references unknown source {record_id}")
            candidate_ids_by_record[record_id].append(candidate_id)

    rows: list[dict[str, Any]] = []
    for record_id in sorted(sources):
        source = sources[record_id]
        screen = screening[record_id]
        family_id = screen.get("study_family_id") or None
        family = families.get(family_id) if family_id else None
        if family_id and family is None:
            raise ValueError(f"{record_id} references unknown study family {family_id}")
        access_row = access.get(record_id)
        locator = screen.get("exact_locator") or None
        endpoint = screen.get("endpoint_class") or ""
        endpoint_status = "REPORTED_SCREENING" if endpoint else "UNRESOLVED"
        rows.append(
            {
                "record_id": record_id,
                "provenance": {
                    "discovery": source.get("discovery"),
                    "retrieval_date": source.get("retrieval_date"),
                    "source_type": source.get("source_type"),
                },
                "canonical_citation": {
                    "title": source.get("title"),
                    "authors": source.get("authors", []),
                    "year": source.get("year"),
                    "doi": source.get("doi"),
                    "source_type": source.get("source_type"),
                    "locator": source.get("locator"),
                },
                "access": {
                    "source_access_class": source.get("access_class"),
                    "route_audit_present": access_row is not None,
                    "route_attempts": access_row.get("route_attempts") if access_row else None,
                    "public_copy_urls": split_urls(access_row.get("public_copy_urls")) if access_row else [],
                    "version_equivalence": access_row.get("version_equivalence") if access_row else "UNRESOLVED",
                    "content_hash_present": bool(source.get("content_hash")),
                },
                "screening": {
                    "decision": screen.get("decision"),
                    "tier": screen.get("tier"),
                    "study_family_id": family_id,
                    "independence": screen.get("independence"),
                    "arm_count": screen.get("arm_count"),
                    "specimen_count": screen.get("specimen_count"),
                    "endpoint_class": endpoint or "UNRESOLVED",
                    "numeric_data_status": screen.get("numeric_data_status") or "UNRESOLVED",
                    "core_covariate_completeness": screen.get("core_covariate_completeness") or None,
                    "reviewer_a": screen.get("reviewer_a"),
                    "reviewer_b_or_adjudicator": screen.get("reviewer_b_or_adjudicator"),
                    "exact_locator": locator,
                    "rationale": screen.get("rationale"),
                },
                "study_family": family,
                "lineage_state": {
                    "study_family_id": family_id,
                    "independence": screen.get("independence") or "UNRESOLVED",
                    "adjudication_status": family.get("adjudication_status") if family else "UNRESOLVED",
                },
                "candidate_ids": sorted(candidate_ids_by_record[record_id]),
                "contradiction_ids": list(screen.get("contradiction_ids", [])) if isinstance(screen.get("contradiction_ids"), list) else [],
                "evidence_fields": {
                    "material_process": field_state(
                        "DERIVED_LINEAGE" if candidate_ids_by_record[record_id] else "UNRESOLVED",
                        candidate_ids_by_record[record_id] or None,
                        locator,
                    ),
                    "intervention": field_state("UNRESOLVED", locator=locator),
                    "comparator": field_state("UNRESOLVED", locator=locator),
                    "damage_crack_protocol": field_state("UNRESOLVED", locator=locator),
                    "exposure": field_state("UNRESOLVED", locator=locator),
                    "timepoint": field_state("UNRESOLVED", locator=locator),
                    "endpoint": field_state(endpoint_status, endpoint or None, locator),
                    "mechanism": field_state("UNRESOLVED", locator=locator),
                    "null_negative_result": field_state("UNRESOLVED", locator=locator),
                    "contradiction": field_state("UNRESOLVED", locator=locator),
                },
                "missing_fields": [
                    "intervention",
                    "comparator",
                    "damage_crack_protocol",
                    "exposure",
                    "timepoint",
                    "mechanism",
                    "null_negative_result",
                    "contradiction",
                ],
            }
        )

    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    sample_ids = ["S01", "S03", "S17", "S25", "S38"]
    second_review: list[dict[str, Any]] = []
    for record_id in sample_ids:
        row = next(item for item in rows if item["record_id"] == record_id)
        checks = {
            "source_identity_join": row["record_id"] == record_id,
            "exact_locator_present": bool(row["screening"]["exact_locator"]),
            "access_state_present": bool(row["access"]["source_access_class"]),
            "family_reference_valid": row["study_family"] is not None,
            "missingness_explicit": all(field in row["missing_fields"] for field in (
                "intervention", "comparator", "mechanism", "contradiction"
            )),
        }
        second_review.append(
            {
                "record_id": record_id,
                "reviewer": "landscape-structural-audit",
                "scope": "provenance, joins, locators, lineage references, and missingness semantics; not scientific eligibility",
                "checks": checks,
                "result": "PASS" if all(checks.values()) else "REVIEW_REQUIRED",
            }
        )

    family_adjudication_pending = sum(
        1 for family in families.values() if family.get("tier") == "A" and family.get("adjudication_status") != "adjudicated"
    )
    reviewer_pending = sum(
        1 for row in rows if row["screening"]["reviewer_b_or_adjudicator"] in {"", "pending-human-adjudication"}
    )
    structured_fields = [
        "intervention", "comparator", "damage_crack_protocol", "exposure", "timepoint",
        "mechanism", "null_negative_result", "contradiction",
    ]
    coverage = {
        field: sum(row["evidence_fields"][field]["status"] not in {"UNRESOLVED", "EVIDENCE_PENDING"} for row in rows)
        for field in structured_fields + ["material_process", "endpoint"]
    }
    checks = {
        "protocol_frozen": protocol_path.exists(),
        "source_screening_reconciled": set(sources) == set(screening),
        "family_references_reconciled": all(
            not row["screening"]["study_family_id"] or row["study_family"] is not None for row in rows
        ),
        "source_access_state_visible": all(bool(row["access"]["source_access_class"]) for row in rows),
        "route_audit_complete": len(access) == len(sources),
        "content_hashes_complete": all(bool(source.get("content_hash")) for source in sources.values()),
        "critical_field_extraction_complete": all(coverage[field] == len(rows) for field in structured_fields),
        "lineage_adjudication_complete": family_adjudication_pending == 0,
        "contradiction_map_complete": coverage["contradiction"] == len(rows),
        "second_review_sample_complete": all(item["result"] == "PASS" for item in second_review),
        "saturation_evidence_recorded": bool(decision.get("saturated")),
        "scientific_adjudication_complete": reviewer_pending == 0,
    }
    blockers = []
    if not checks["route_audit_complete"]:
        blockers.append(f"route-level access register covers {len(access)}/{len(sources)} source records")
    if not checks["content_hashes_complete"]:
        blockers.append("source content/version hashes are absent for one or more records")
    if not checks["critical_field_extraction_complete"]:
        blockers.append("critical evidence fields remain normalized as UNRESOLVED rather than source-located extraction")
    if not checks["lineage_adjudication_complete"]:
        blockers.append(f"{family_adjudication_pending} Tier-A study families remain pending adjudication")
    if not checks["contradiction_map_complete"]:
        blockers.append("no explicit contradiction ledger is present")
    if not checks["scientific_adjudication_complete"]:
        blockers.append(f"{reviewer_pending} screening rows remain pending human adjudication")

    status = "LANDSCAPE_READY" if all(checks.values()) else "LANDSCAPE_INCOMPLETE"
    map_document = {
        "map_version": "glr.1-landscape-map",
        "problem_context": "modern terrestrial Roman-inspired hot-mixed lime-pozzolan mortar; functional water-transport recovery after controlled cracking",
        "record_count": len(rows),
        "study_family_count": len(families),
        "candidate_count": len(candidates),
        "records": rows,
        "coverage": coverage,
        "second_review": second_review,
        "checks": checks,
        "blockers": blockers,
        "readiness": status,
        "permitted_outputs": [
            "provisional evidence-gap synthesis",
            "provisional candidate dossier",
            "explicitly provisional hypothesis seeds with locators and uncertainty",
        ] if status == "LANDSCAPE_INCOMPLETE" else [
            "discovery-grade evidence-grounded hypothesis generation within the support region",
            "rival critique and bounded experiment-question design",
        ],
        "prohibited_outputs": [
            "validated performance claim",
            "recipe or physical execution authorization",
            "generalizable predictive model",
            "claim that the entire literature has been found",
        ],
    }
    run = {
        "goal": "G-LR",
        "protocol_version": "glr.1-landscape-map",
        "run_id": run_id(
            "glr.1-landscape-map",
            {
                "sources": sha256(sources_path),
                "screening": sha256(screening_path),
                "families": sha256(families_path),
                "candidates": sha256(candidates_path),
                "access_register": sha256(access_path),
                "g1_decision": sha256(decision_path),
                "protocol": sha256(protocol_path),
            },
        ),
        "execution_date": "2026-10-09",
        "network": "none during replay",
        "model_calls": "none",
        "physical_execution": "prohibited",
        "inputs": {
            "sources": {"path": display_path(sources_path), "sha256": sha256(sources_path)},
            "screening": {"path": display_path(screening_path), "sha256": sha256(screening_path)},
            "families": {"path": display_path(families_path), "sha256": sha256(families_path)},
            "candidates": {"path": display_path(candidates_path), "sha256": sha256(candidates_path)},
            "access_register": {"path": display_path(access_path), "sha256": sha256(access_path)},
            "g1_decision": {"path": display_path(decision_path), "sha256": sha256(decision_path)},
            "protocol": {"path": display_path(protocol_path), "sha256": sha256(protocol_path)},
        },
        "counts": {
            "source_count": len(sources),
            "screening_count": len(screening),
            "study_family_count": len(families),
            "candidate_count": len(candidates),
            "access_register_count": len(access),
            "route_audit_coverage": len(access) / len(sources) if sources else 0.0,
        },
        "checks": checks,
        "blockers": blockers,
        "readiness": status,
        "outputs": {
            "landscape_sources": "data/manifests/landscape-sources.jsonl",
            "evidence_map": "data/processed/evidence-landscape.json",
            "second_review": "data/manifests/landscape-second-review.json",
        },
    }
    return run, rows, map_document


def write_outputs(run: dict[str, Any], rows: list[dict[str, Any]], map_document: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "data/manifests").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/manifests/landscape-sources.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"
    )
    (ROOT / "data/manifests/landscape-second-review.json").write_text(
        json.dumps(map_document["second_review"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ROOT / "data/processed/evidence-landscape.json").write_text(
        json.dumps(map_document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "run.json").write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def replay(**paths: Path) -> dict[str, Any]:
    run, rows, map_document = build_landscape(**paths)
    return {"run": run, "record_count": len(rows), "map": map_document}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    paths = {
        "sources_path": DEFAULT_SOURCES,
        "screening_path": DEFAULT_SCREENING,
        "families_path": DEFAULT_FAMILIES,
        "candidates_path": DEFAULT_CANDIDATES,
        "access_path": DEFAULT_ACCESS,
        "decision_path": DEFAULT_DECISION,
        "protocol_path": DEFAULT_PROTOCOL,
    }
    run, rows, map_document = build_landscape(**paths)
    if args.write:
        write_outputs(run, rows, map_document, args.output_dir)
    print(json.dumps(run, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
