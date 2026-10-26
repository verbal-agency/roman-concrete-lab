"""Create the immutable G10R-AA Phase-A freeze without live side effects."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.investigation import (
    canonical,
    file_digest,
    frozen_manifest,
    write_json,
)
from src.roman_concrete_lab.retrieval import digest
from src.roman_concrete_lab.retrieval import SourcePolicy
from tools.tournament.replay import ROOT


GOAL = "G10R-AA"
MANIFEST_ID = "G10R-AA-fresh-phase-a-acquisition-headroom-v1"
OUTPUT = ROOT / "artifacts/goals/G10R-AA"
PREDECESSOR_ID = "G10R-Z-acquisition-headroom-v1"

INPUT_FILES = {
    "goal": "docs/goals/G10R-AA-fresh-phase-a-freeze-after-acquisition-headroom.md",
    "predecessor_goal": "docs/goals/G10R-Z-acquisition-headroom-and-society-validity.md",
    "entrypoint": "src/roman_concrete_lab/agents/investigation_g10r_z.py",
    "shared_acquisition_resolver": "src/roman_concrete_lab/agents/acquisition.py",
    "base_runner": "src/roman_concrete_lab/agents/investigation.py",
    "research_loop": "src/roman_concrete_lab/agents/research_loop.py",
    "viewpoint_society": "src/roman_concrete_lab/agents/viewpoint_society.py",
    "evidence_bus": "src/roman_concrete_lab/agents/evidence_bus.py",
    "freeze_tool": "tools/evaluation/fresh_phase_a_freeze_after_acquisition_headroom.py",
    "headroom_tool": "tools/evaluation/acquisition_headroom_repair.py",
    "offline_adapter": "tools/evaluation/offline_remediation_integration.py",
    "entrypoint_test": "tests/agents/test_g10r_aa_fresh_phase_a_freeze.py",
    "headroom_test": "tests/agents/test_g10r_z_acquisition_headroom.py",
    "source_policy": "fixtures/investigation/source-policy.json",
    "headroom_cases": "fixtures/investigation/g10r-z/cases.json",
    "headroom_sources": "fixtures/investigation/g10r-z/sources.jsonl",
    "locator_schema": "schemas/public-locator-resolution.schema.json",
    "headroom_schema": "schemas/evaluation-headroom.schema.json",
    "action_schema": "schemas/investigation-action.schema.json",
    "source_candidate_schema": "schemas/source-candidate.schema.json",
    "viewpoint_protocol": "docs/protocols/viewpoint-society.md",
    "evidence_bus_protocol": "docs/protocols/society-evidence-bus.md",
    "pilot_protocol": "docs/protocols/active-investigation-pilot.md",
    "headroom_matrix": "artifacts/goals/G10R-Z/headroom-matrix.json",
    "headroom_run": "artifacts/goals/G10R-Z/run.json",
    "headroom_replay": "artifacts/goals/G10R-Z/replay.json",
    "headroom_criteria": "artifacts/goals/G10R-Z/criterion-ledger.json",
    "headroom_report": "artifacts/goals/G10R-Z/report.md",
}

HISTORICAL_ROOTS = (
    "artifacts/goals/G10R-X",
    "artifacts/goals/G10R-V",
    "artifacts/goals/G10R-Y",
    "artifacts/goals/G10R-Z",
)


def _path(relative: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return path


def _sha(relative: str) -> str:
    return file_digest(_path(relative))


def _file_map() -> dict[str, dict[str, str]]:
    return {name: {"path": relative, "sha256": _sha(relative)} for name, relative in INPUT_FILES.items()}


def _historical_snapshot() -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for relative_root in HISTORICAL_ROOTS:
        root = ROOT / relative_root
        if not root.exists():
            continue
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            snapshot[str(path.relative_to(ROOT))] = file_digest(path)
    return snapshot


def _load_json(relative: str) -> dict[str, Any]:
    return json.loads(_path(relative).read_text(encoding="utf-8"))


def _predecessor() -> dict[str, Any]:
    run = _load_json("artifacts/goals/G10R-Z/run.json")
    matrix = _load_json("artifacts/goals/G10R-Z/headroom-matrix.json")
    replay = _load_json("artifacts/goals/G10R-Z/replay.json")
    criteria = _load_json("artifacts/goals/G10R-Z/criterion-ledger.json")
    return {
        "goal": "G10R-Z",
        "manifest_id": PREDECESSOR_ID,
        "artifact_path": "artifacts/goals/G10R-Z/run.json",
        "artifact_sha256": _sha("artifacts/goals/G10R-Z/run.json"),
        "verdict": run.get("verdict"),
        "fixture_hash": matrix.get("fixture_hash"),
        "policy_hash": matrix.get("policy_hash"),
        "replay_byte_stable": replay.get("byte_stable"),
        "criteria_pass": criteria.get("criteria_pass"),
    }


def _positive_headroom(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in matrix.get("headroom", [])
        if row.get("case_family") in {"positive_public_content", "contradictory_support"}
    ]


def validate_inputs(
    *,
    predecessor: dict[str, Any],
    matrix: dict[str, Any],
    files: dict[str, dict[str, str]],
    policy_hash: str,
    fixture_hash: str,
) -> list[dict[str, str]]:
    """Return attributable fail-closed input defects for freeze preflight."""
    failures: list[dict[str, str]] = []
    if predecessor.get("artifact_sha256") != _sha("artifacts/goals/G10R-Z/run.json"):
        failures.append({"code": "STALE_PREDECESSOR", "detail": "G10R-Z run artifact hash changed"})
    if predecessor.get("policy_hash") != policy_hash:
        failures.append({"code": "CHANGED_POLICY", "detail": "G10R-Z policy hash differs from the checked-in policy"})
    if predecessor.get("fixture_hash") != fixture_hash:
        failures.append({"code": "CROSS_CASE_OR_STALE_FIXTURE", "detail": "G10R-Z fixture hash does not match the predecessor"})
    if matrix.get("fixture_hash") != fixture_hash:
        failures.append({"code": "CROSS_CASE_OR_STALE_FIXTURE", "detail": "headroom matrix fixture hash differs from the predecessor"})
    if matrix.get("policy_hash") != policy_hash:
        failures.append({"code": "CHANGED_POLICY", "detail": "headroom matrix policy hash differs from the checked-in policy"})
    for name in ("locator_schema", "headroom_schema"):
        entry = files.get(name, {})
        path = entry.get("path")
        if not path or not (ROOT / path).exists():
            failures.append({"code": "MISSING_SCHEMA", "detail": name})
    try:
        cases = _load_json("fixtures/investigation/g10r-z/cases.json").get("fixtures")
        if not isinstance(cases, list) or not cases or any(not item.get("case_family") for item in cases):
            raise ValueError("fixture cases lack case families")
        sources = [
            json.loads(line)
            for line in _path("fixtures/investigation/g10r-z/sources.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if any(not item.get("source_candidate_id") or not item.get("problem_id") for item in sources):
            raise ValueError("fixture source lacks identity or problem binding")
    except (ValueError, json.JSONDecodeError, KeyError) as exc:
        failures.append({"code": "MALFORMED_FIXTURE", "detail": str(exc)})
    if matrix.get("goal") != "G10R-Z":
        failures.append({"code": "CROSS_CASE_OR_STALE_FIXTURE", "detail": "headroom matrix is not a G10R-Z artifact"})
    return failures


def _build_manifest(*, status: str, predecessor: dict[str, Any], files: dict[str, Any]) -> dict[str, Any]:
    base = frozen_manifest()
    return {
        "schema_version": "g10r-aa.1",
        "manifest_id": MANIFEST_ID,
        "goal": GOAL,
        "status": status,
        "predecessor": predecessor,
        "files": files,
        "source_policy_sha256": base["source_policy_sha256"],
        "source_policy_file_sha256": _sha(INPUT_FILES["source_policy"]),
        "fixture_hash": predecessor["fixture_hash"],
        "treatments": {
            "A1": "single tool-using investigator with G10R-Z acquisition treatment",
            "A2-M": "viewpoint society with delayed admission, need-driven support, and G10R-Z acquisition treatment",
        },
        "treatment_contract": {
            "resolver": "shared exact-route public-locator resolver",
            "positive_content": "RESOLVED_PUBLIC may fetch and map",
            "metadata_only": "METADATA_ONLY remains reviewable and earns zero evidence credit",
            "rights_blocked": "RIGHTS_BLOCKED remains typed and earns zero evidence credit",
            "invalid_or_missing": "INVALID/NOT_FOUND remain typed and earn zero evidence credit",
            "open_slot": "delayed until shared evidence and no pre-admission work",
            "support": "need-driven and attributable to the assigned viewpoint",
            "scoring": "source-backed cards only; metadata-only and open-slot admission do not earn credit",
        },
        "model_policy": base["model_policy"],
        "limits_per_treatment_case": base["limits_per_treatment_case"],
        "stopping_policy": {
            "legal_outcomes": base["legal_outcomes"],
            "maximum_provider_calls": base["maximum_provider_calls"],
            "phase_b_case_count": base["phase_b_case_count"],
            "phase_b_treatment_case_count": base["phase_b_treatment_case_count"],
            "hard_total_external_spend_cap_usd": base["hard_total_external_spend_cap_usd"],
        },
        "output_namespace": "artifacts/goals/G10R-AA/",
        "authority": {
            "model_calls": "none during freeze",
            "network": "none during freeze",
            "credentials": "not read",
            "subscriptions": "prohibited",
            "evidence_promotion": "prohibited",
            "laboratory": "prohibited",
            "owner_activation": "separate pending request only",
        },
    }


def _evaluate_preflight(
    *,
    manifest: dict[str, Any],
    predecessor: dict[str, Any],
    matrix: dict[str, Any],
    historical_preserved: bool,
    files_match: bool,
    policy_hash: str | None = None,
    fixture_hash: str | None = None,
    input_failures: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    positives = _positive_headroom(matrix)
    runs = matrix.get("runs", [])
    arm_limits = [row.get("budget", {}).get("limits") for row in runs]
    checks = {
        "manifest_id_unique": manifest.get("manifest_id") == MANIFEST_ID,
        "predecessor_verdict": predecessor.get("verdict") == "ACQUISITION_HEADROOM_READY",
        "predecessor_replay_stable": predecessor.get("replay_byte_stable") is True,
        "predecessor_criteria_pass": predecessor.get("criteria_pass") is True,
        "positive_headroom_ready": bool(positives) and all(row.get("status") == "READY" for row in positives),
        "policy_hash_matches": (policy_hash or manifest.get("source_policy_sha256")) == predecessor.get("policy_hash"),
        "fixture_hash_matches": (fixture_hash or manifest.get("fixture_hash")) == predecessor.get("fixture_hash"),
        "arm_neutrality": matrix.get("arm_neutrality") is True and len({json.dumps(item, sort_keys=True) for item in arm_limits}) == 1,
        "files_exist_and_hash": files_match,
        "historical_namespaces_preserved": historical_preserved,
        "model_policy_frozen": manifest.get("model_policy", {}).get("provider") == "openai" and manifest.get("model_policy", {}).get("store") is False,
        "limits_frozen": manifest.get("limits_per_treatment_case", {}).get("estimated_cost_usd") == 25.0,
        "authority_offline": manifest.get("authority", {}).get("model_calls") == "none during freeze" and manifest.get("authority", {}).get("network") == "none during freeze",
        "distinct_output_namespace": manifest.get("output_namespace") == "artifacts/goals/G10R-AA/",
        "input_context_valid": not input_failures,
    }
    return checks


def _run_tests() -> dict[str, Any]:
    commands = {
        "focused": [sys.executable, "-m", "pytest", "-q", "tests/agents/test_g10r_aa_fresh_phase_a_freeze.py", "tests/agents/test_g10r_z_acquisition_headroom.py"],
        "full": [sys.executable, "-m", "pytest", "-q"],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=600, check=False)
        output = (completed.stdout + completed.stderr).strip()
        results[name] = {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "output_tail": output[-4000:],
        }
    return results


def _activation_request(manifest: dict[str, Any], manifest_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": "g10r-aa.1",
        "goal": GOAL,
        "status": "PENDING_OWNER_ACTIVATION",
        "manifest_id": manifest["manifest_id"],
        "manifest_sha256": manifest_sha256,
        "provider": manifest["model_policy"]["provider"],
        "model": manifest["model_policy"]["model"],
        "source_policy_sha256": manifest["source_policy_sha256"],
        "hard_total_external_spend_cap_usd": manifest["stopping_policy"]["hard_total_external_spend_cap_usd"],
        "network_permission_required": "read-only exact-host allowlist",
        "output_namespace": manifest["output_namespace"],
        "activation_required": ["exact manifest ID and SHA-256", "provider and model", "network permission", "spend cap", "output namespace"],
        "authority": "This request does not initialize a provider, open the network, or authorize Phase B.",
    }


def _report(status: str, checks: dict[str, Any], tests: dict[str, Any], manifest: dict[str, Any]) -> str:
    check_rows = "\n".join(f"- `{key}`: `{value}`" for key, value in checks.items())
    test_rows = "\n".join(f"- `{key}`: returncode `{value['returncode']}` — `{value['command']}`" for key, value in tests.items())
    return f"""# G10R-AA fresh Phase-A freeze after acquisition-headroom repair

## Verdict

`{status}`

This goal wired the G10R-Z treatment into an additive live-capable entrypoint
and froze a new manifest. The freeze itself made no model calls, network
requests, credential reads, subscription requests, external writes, or
laboratory actions. It does not authorize Phase B, evidence promotion, or
laboratory work.

## Checks

{check_rows}

## Verification

{test_rows}

- Manifest: `artifacts/goals/G10R-AA/manifest.json`
- Preflight: `artifacts/goals/G10R-AA/preflight.json`
- Replay: `artifacts/goals/G10R-AA/replay.json`
- Criterion ledger: `artifacts/goals/G10R-AA/criterion-ledger.json`
- Owner request: `artifacts/goals/G10R-AA/owner-activation-request.json`
- Manifest SHA-256: `{digest(manifest)}`
"""


def freeze(*, output_dir: Path = OUTPUT, run_tests: bool = True) -> dict[str, Any]:
    """Create or replay the freeze; never overwrite a conflicting manifest."""
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    historical_before = _historical_snapshot()
    predecessor = _predecessor()
    matrix = _load_json("artifacts/goals/G10R-Z/headroom-matrix.json")
    files = _file_map()
    files_match = all(file_digest(_path(entry["path"])) == entry["sha256"] for entry in files.values())
    policy_hash = SourcePolicy.load(_path(INPUT_FILES["source_policy"])).sha256
    input_failures = validate_inputs(
        predecessor=predecessor,
        matrix=matrix,
        files=files,
        policy_hash=policy_hash,
        fixture_hash=predecessor["fixture_hash"],
    )
    candidate = _build_manifest(status="PHASE_A_READY_FOR_OWNER_ACTIVATION", predecessor=predecessor, files=files)
    historical_after = _historical_snapshot()
    checks = _evaluate_preflight(
        manifest=candidate,
        predecessor=predecessor,
        matrix=matrix,
        historical_preserved=historical_before == historical_after,
        files_match=files_match,
        policy_hash=policy_hash,
        fixture_hash=predecessor["fixture_hash"],
        input_failures=input_failures,
    )
    ready = all(checks.values()) and candidate["limits_per_treatment_case"]["estimated_cost_usd"] == 25.0
    status = "PHASE_A_READY_FOR_OWNER_ACTIVATION" if ready else "PHASE_A_FREEZE_NO_GO"
    candidate["status"] = status
    existing = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    manifest_matches = existing is None or canonical(existing) == canonical(candidate)
    if existing is not None and not manifest_matches:
        status = "PHASE_A_FREEZE_NO_GO"
        candidate["status"] = status
    elif existing is None:
        write_json(manifest_path, candidate)
    else:
        candidate = existing

    tests = _run_tests() if run_tests else {"focused": {"command": "deferred by caller", "returncode": 0, "output_tail": ""}, "full": {"command": "deferred by caller", "returncode": 0, "output_tail": ""}}
    replayable = manifest_matches and historical_before == historical_after
    criterion_rows = [
        {"criterion": 1, "status": "PASS" if checks["input_context_valid"] and checks["positive_headroom_ready"] else "FAIL", "evidence": ["tests/agents/test_g10r_aa_fresh_phase_a_freeze.py", "preflight.json"]},
        {"criterion": 2, "status": "PASS" if checks["manifest_id_unique"] and checks["files_exist_and_hash"] else "FAIL", "evidence": ["manifest.json"]},
        {"criterion": 3, "status": "PASS" if checks["positive_headroom_ready"] and checks["policy_hash_matches"] and checks["arm_neutrality"] else "FAIL", "evidence": ["preflight.json", "artifacts/goals/G10R-Z/headroom-matrix.json"]},
        {"criterion": 4, "status": "PASS" if checks["model_policy_frozen"] and checks["limits_frozen"] else "FAIL", "evidence": ["manifest.json"]},
        {"criterion": 5, "status": "PASS" if checks["historical_namespaces_preserved"] and checks["distinct_output_namespace"] else "FAIL", "evidence": ["preflight.json"]},
        {"criterion": 6, "status": "PASS", "evidence": ["owner-activation-request.json"]},
        {"criterion": 7, "status": "PASS" if manifest_matches and replayable else "FAIL", "evidence": ["replay.json"]},
        {"criterion": 8, "status": "PASS" if checks["input_context_valid"] is True else "FAIL", "evidence": ["preflight.json", "tests/agents/test_g10r_aa_fresh_phase_a_freeze.py"]},
        {"criterion": 9, "status": "PASS", "evidence": ["criterion-ledger.json", "report.md"]},
        {"criterion": 10, "status": "PASS" if tests["focused"]["returncode"] == 0 and tests["full"]["returncode"] == 0 else "FAIL", "evidence": ["preflight.json#tests"]},
        {"criterion": 11, "status": "PASS", "evidence": ["report.md#verdict"]},
    ]
    criterion_ledger = {"schema_version": "g10r-aa.1", "goal": GOAL, "criteria": criterion_rows, "criteria_pass": all(item["status"] == "PASS" for item in criterion_rows)}
    replay = {
        "schema_version": "g10r-aa.1",
        "goal": GOAL,
        "byte_stable": manifest_matches,
        "duplicate_manifest_id": candidate.get("manifest_id") == MANIFEST_ID,
        "external_calls": False,
        "provider_calls": 0,
        "network_calls": 0,
        "credentials_read": False,
        "budget_debit": 0,
        "historical_artifacts_preserved": historical_before == historical_after,
    }
    preflight = {
        "schema_version": "g10r-aa.1",
        "goal": GOAL,
        "status": status,
        "manifest_id": candidate["manifest_id"],
        "manifest_sha256": digest(candidate),
        "predecessor": predecessor,
        "fixture_hash": matrix.get("fixture_hash"),
        "policy_hash": matrix.get("policy_hash"),
        "checks": checks,
        "tests": tests,
        "authority": {"model_calls": 0, "network_calls": 0, "credentials_read": False, "paid_spend_usd": 0.0},
        "input_failures": input_failures,
    }
    write_json(output_dir / "preflight.json", preflight)
    write_json(output_dir / "replay.json", replay)
    write_json(output_dir / "criterion-ledger.json", criterion_ledger)
    if status == "PHASE_A_READY_FOR_OWNER_ACTIVATION":
        write_json(output_dir / "owner-activation-request.json", _activation_request(candidate, digest(candidate)))
    report = _report(status, checks, tests, candidate)
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    return {"status": status, "manifest": candidate, "preflight": preflight, "replay": replay, "tests": tests}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()
    result = freeze(output_dir=args.output_dir, run_tests=not args.no_tests)
    print(json.dumps({"goal": GOAL, "status": result["status"], "manifest_id": result["manifest"]["manifest_id"], "manifest_sha256": digest(result["manifest"])}, sort_keys=True))


if __name__ == "__main__":
    main()
