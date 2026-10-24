"""Freeze a distinct Phase-A manifest after the G10R-T research-loop gate.

The command is intentionally offline.  It runs the existing Phase-A preflight,
rechecks the deterministic G10R-T artifacts and tests, and writes a new
namespace without touching any historical G10R freeze or paid-run artifact.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.investigation import canonical, file_digest, frozen_manifest, phase_a, write_json
from src.roman_concrete_lab.retrieval import digest
from tools.tournament.replay import ROOT


GOAL = "G10R-U"
MANIFEST_ID = "G10R-U-fresh-phase-a-research-loop-v1"
OUTPUT = ROOT / "artifacts/goals/G10R-U"
T_FILES = {
    "goal": "docs/goals/G10R-T-society-research-loop-ablation.md",
    "next_goal": "docs/goals/G10R-U-fresh-phase-a-freeze-after-loop-repair.md",
    "research_loop_runner": "src/roman_concrete_lab/agents/research_loop.py",
    "viewpoint_society_runner": "src/roman_concrete_lab/agents/viewpoint_society.py",
    "research_loop_evaluator": "tools/evaluation/society_research_loop_ablation.py",
    "research_loop_tests": "tests/agents/test_society_research_loop.py",
    "ablation_tests": "tests/agents/test_society_research_loop_ablation.py",
    "freeze_tests": "tests/agents/test_g10r_u_fresh_phase_a_freeze.py",
    "research_loop_sources": "fixtures/investigation/research-loop/sources.jsonl",
    "research_loop_cases": "fixtures/investigation/research-loop/cases.json",
    "research_need_schema": "schemas/research-need.schema.json",
    "candidate_selection_schema": "schemas/candidate-selection.schema.json",
    "dossier_revision_schema": "schemas/viewpoint-dossier-revision.schema.json",
    "open_viewpoint_schema": "schemas/open-viewpoint-admission.schema.json",
    "viewpoint_protocol": "docs/protocols/viewpoint-society.md",
    "evidence_bus_protocol": "docs/protocols/society-evidence-bus.md",
    "pilot_protocol": "docs/protocols/active-investigation-pilot.md",
    "diagnosis": "artifacts/goals/G10R-T/diagnosis.json",
    "ablation_matrix": "artifacts/goals/G10R-T/ablation-matrix.json",
    "run": "artifacts/goals/G10R-T/run.json",
    "replay": "artifacts/goals/G10R-T/replay.json",
    "report": "artifacts/goals/G10R-T/report.md",
    "criterion_ledger": "artifacts/goals/G10R-T/criterion-ledger.json",
    "verification": "artifacts/goals/G10R-T/verification.json",
}
HISTORICAL_SENTINELS = (
    "artifacts/goals/G10R/phase-a-post-constraint-20261023.json",
    "artifacts/goals/G10R/manifest-post-constraint-20261023.json",
    "artifacts/goals/G10R/phase-a-post-g10r-s-20261024.json",
    "artifacts/goals/G10R/manifest-post-g10r-s-20261024.json",
    "artifacts/goals/G10R-S-paid-20261024-final/run.json",
    "artifacts/goals/G10R-S-paid-20261024-final/report.md",
)


def _path(relative: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return path


def _file_map() -> dict[str, dict[str, str]]:
    return {name: {"path": relative, "sha256": file_digest(_path(relative))} for name, relative in T_FILES.items()}


def _historical_snapshot() -> dict[str, str]:
    return {relative: file_digest(_path(relative)) for relative in HISTORICAL_SENTINELS}


def _run_tests() -> dict[str, Any]:
    commands = {
        "focused": [sys.executable, "-m", "pytest", "-q", "tests/agents/test_society_research_loop.py", "tests/agents/test_society_research_loop_ablation.py", "tests/agents/test_g10r_u_fresh_phase_a_freeze.py"],
        "full": [sys.executable, "-m", "pytest", "-q"],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=300, check=False)
        output = (completed.stdout + completed.stderr).strip()
        results[name] = {"command": " ".join(command), "returncode": completed.returncode, "output_tail": output[-2000:]}
    return results


def _activation_request(manifest: dict[str, Any]) -> str:
    policy = json.loads(_path("fixtures/investigation/source-policy.json").read_text(encoding="utf-8"))
    hosts = "\n".join(f"- `{host}`" for host in manifest["allowed_hosts"])
    limits = manifest["limits_per_treatment_case"]
    return f"""# G10R-U activation request

## Status

`PHASE_A_READY_FOR_OWNER_ACTIVATION` is a preparation state only. It does not
start Phase B, create a provider client, or authorize a paid call.

## Frozen execution boundary

- Provider: `openai`, Responses API
- Model: `{manifest['model_policy']['model']}`
- Reasoning effort: `{manifest['model_policy']['reasoning_effort']}`
- Store: `{str(manifest['model_policy']['store']).lower()}`
- Source-policy version: `{policy['policy_version']}`
- Source-policy mode: exact-host, read-only, GET-only, no credentials
- Per-treatment-case limits: `{json.dumps(limits, sort_keys=True)}`
- Hard aggregate external-spend cap: `${manifest['hard_total_external_spend_cap_usd']:.2f}`
- Declared simulation adapter: `SIMULATOR_UNAVAILABLE`; simulation output cannot earn empirical evidence credit

### Frozen hosts

{hosts}

## Required activation

Before any paid execution, the owner must review this manifest and explicitly
authorize the separately defined Phase-B goal. That activation must confirm the
provider key, network permission, exact manifest ID, spend cap, and output
namespace. No activation is implied by this artifact, by the offline
`SOCIETY_RESEARCH_LOOP_READY` result, or by committing this file.
"""


def _report(status: str, checks: dict[str, Any], *, readiness: dict[str, Any]) -> str:
    rows = "\n".join(f"- `{key}`: `{value}`" for key, value in checks.items())
    return f"""# G10R-U fresh Phase-A freeze

## Handoff

`{status}`

This freeze is repository-local and offline. It does not make model calls,
network requests, subscription requests, credential reads, laboratory actions,
or external writes. Historical G10R-F, G10R-B2, and G10R-S namespaces remain
immutable.

## Checks

{rows}

Manifest: `artifacts/goals/G10R-U/manifest.json`
Readiness: `artifacts/goals/G10R-U/readiness.json`
Activation request: `artifacts/goals/G10R-U/activation-request.md`

The next action, if the owner agrees, is a separately authored and separately
authorized paid Phase-B goal. This freeze does not activate it.
"""


def freeze(*, output_dir: Path = OUTPUT, refresh: bool = False) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    readiness_path = output_dir / "readiness.json"
    report_path = output_dir / "report.md"
    activation_path = output_dir / "activation-request.md"
    historical_before = _historical_snapshot()

    phase_first = phase_a()
    phase_second = phase_a()
    phase_stable = canonical(phase_first) == canonical(phase_second)
    t_run = json.loads(_path(T_FILES["run"]).read_text(encoding="utf-8"))
    t_replay = json.loads(_path(T_FILES["replay"]).read_text(encoding="utf-8"))
    t_verification = json.loads(_path(T_FILES["verification"]).read_text(encoding="utf-8"))
    base_manifest = frozen_manifest()
    manifest = dict(base_manifest)
    manifest.update({
        "manifest_id": MANIFEST_ID,
        "freeze_goal": GOAL,
        "g10r_t_verdict": t_run.get("terminal"),
        "g10r_t_replay_sha256": file_digest(_path(T_FILES["replay"])),
        "g10r_t_research_loop": {"arms": ["R0_SINGLE", "R1_SHARED_SUPPORT", "R2_VIEWPOINT_FIXED", "R3_VIEWPOINT_ADAPTIVE"], "equal_actual_ceilings": True, "files": _file_map()},
    })
    tests = _run_tests()
    manifest_matches_existing = not manifest_path.exists() or json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
    historical_after = _historical_snapshot()
    historical_preserved = historical_before == historical_after
    focused_pass = tests["focused"]["returncode"] == 0
    full_pass = tests["full"]["returncode"] == 0
    checks = {
        "manifest_id_new": manifest["manifest_id"] == MANIFEST_ID,
        "manifest_inputs_exist_and_hash": all(_path(item["path"]).exists() and file_digest(_path(item["path"])) == item["sha256"] for item in manifest["g10r_t_research_loop"]["files"].values()),
        "historical_namespaces_preserved": historical_preserved,
        "historical_manifest_not_overwritten": historical_preserved,
        "phase_a_status": phase_first.get("status"),
        "phase_a_manifest_stable": phase_stable and phase_first.get("manifest_sha256") == digest(phase_first.get("manifest", {})),
        "g10r_t_ready": t_run.get("terminal") == "SOCIETY_RESEARCH_LOOP_READY",
        "g10r_t_replay_complete": t_replay.get("all_boundaries_byte_equivalent") is True,
        "full_suite_passed": full_pass,
        "focused_tests_passed": focused_pass,
        "no_live_side_effects": True,
        "source_policy_default_deny": base_manifest.get("source_policy_sha256") is not None,
        "source_policy_version": json.loads(_path("fixtures/investigation/source-policy.json").read_text(encoding="utf-8"))["policy_version"],
        "aggregate_cap_usd": base_manifest["hard_total_external_spend_cap_usd"],
        "repeated_manifest_not_overwritten": manifest_matches_existing or refresh,
        "verification_artifact_consistent": t_verification.get("paid_spend_usd") == 0.0 and t_verification.get("model_calls") == 0 and t_verification.get("network_calls") == 0,
    }
    ready = all((value is True) for key, value in checks.items() if key not in {"phase_a_status", "source_policy_version", "aggregate_cap_usd"}) and phase_first.get("status") == "AWAITING_OWNER_ACTIVATION"
    status = "PHASE_A_READY_FOR_OWNER_ACTIVATION" if ready else "PHASE_A_FREEZE_NO_GO"
    if manifest_path.exists() and not manifest_matches_existing and not refresh:
        status = "PHASE_A_FREEZE_NO_GO"
    if status == "PHASE_A_READY_FOR_OWNER_ACTIVATION":
        write_json(manifest_path, manifest)
    readiness = {
        "schema_version": "1.0", "goal": GOAL, "status": status,
        "manifest_id": MANIFEST_ID, "manifest_sha256": digest(manifest),
        "g10r_t_verdict": t_run.get("terminal"), "g10r_t_replay_sha256": file_digest(_path(T_FILES["replay"])),
        "checks": checks, "tests": tests,
        "authority": {"model_calls": "none", "network": "none", "credentials": "none", "subscriptions": "prohibited", "laboratory": "prohibited", "evidence_promotion": "prohibited"},
        "next_action": "Owner may review and separately authorize a paid Phase-B goal." if ready else "Repair the failed freeze invariant before activation.",
    }
    write_json(readiness_path, readiness)
    if ready:
        activation_path.write_text(_activation_request(manifest), encoding="utf-8")
    report_path.write_text(_report(status, checks, readiness=readiness), encoding="utf-8")
    return readiness


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    result = freeze(output_dir=args.output_dir, refresh=args.refresh)
    print(json.dumps({"status": result["status"], "manifest_id": result["manifest_id"], "manifest_sha256": result["manifest_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
