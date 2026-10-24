"""Create the post-wiring G10R-X Phase-A freeze without live side effects."""

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


GOAL = "G10R-X"
MANIFEST_ID = "G10R-X-fresh-phase-a-research-loop-wiring-v1"
OUTPUT = ROOT / "artifacts/goals/G10R-X"
W_FILES = {
    "goal": "docs/goals/G10R-W-live-research-loop-wiring.md",
    "next_goal": "docs/goals/G10R-X-fresh-phase-a-freeze-after-wiring.md",
    "research_loop_ledger": "src/roman_concrete_lab/agents/research_loop.py",
    "live_runner": "src/roman_concrete_lab/agents/investigation.py",
    "viewpoint_society_runner": "src/roman_concrete_lab/agents/viewpoint_society.py",
    "wiring_test": "tests/agents/test_g10r_v_research_loop_wiring.py",
    "freeze_test": "tests/agents/test_g10r_x_fresh_phase_a_freeze.py",
    "research_need_schema": "schemas/research-need.schema.json",
    "candidate_selection_schema": "schemas/candidate-selection.schema.json",
    "dossier_revision_schema": "schemas/viewpoint-dossier-revision.schema.json",
    "open_viewpoint_schema": "schemas/open-viewpoint-admission.schema.json",
    "viewpoint_dossier_schema": "schemas/viewpoint-dossier.schema.json",
    "viewpoint_protocol": "docs/protocols/viewpoint-society.md",
    "evidence_bus_protocol": "docs/protocols/society-evidence-bus.md",
    "pilot_protocol": "docs/protocols/active-investigation-pilot.md",
    "wiring_report": "artifacts/goals/G10R-W/report.json",
}
HISTORICAL_FILES = (
    "artifacts/goals/G10R-U/manifest.json",
    "artifacts/goals/G10R-U/readiness.json",
    "artifacts/goals/G10R-U/activation-request.md",
    "artifacts/goals/G10R-U/report.md",
    "artifacts/goals/G10R-T/run.json",
    "artifacts/goals/G10R-T/replay.json",
)


def _path(relative: str) -> Path:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return path


def _file_map() -> dict[str, dict[str, str]]:
    return {name: {"path": relative, "sha256": file_digest(_path(relative))} for name, relative in W_FILES.items()}


def _refresh_manifest_hashes(value: Any) -> None:
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            value["sha256"] = file_digest(_path(value["path"]))
            return
        for child in value.values():
            _refresh_manifest_hashes(child)
    elif isinstance(value, list):
        for child in value:
            _refresh_manifest_hashes(child)


def _snapshot() -> dict[str, str]:
    return {relative: file_digest(_path(relative)) for relative in HISTORICAL_FILES}


def _tests() -> dict[str, Any]:
    commands = {
        "focused": [sys.executable, "-m", "pytest", "-q", "tests/agents/test_g10r_v_research_loop_wiring.py", "tests/agents/test_society_research_loop.py", "tests/agents/test_society_research_loop_ablation.py", "tests/agents/test_g10r_u_fresh_phase_a_freeze.py", "tests/agents/test_g10r_x_fresh_phase_a_freeze.py"],
        "full": [sys.executable, "-m", "pytest", "-q"],
    }
    results: dict[str, Any] = {}
    for name, command in commands.items():
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=360, check=False)
        output = (completed.stdout + completed.stderr).strip()
        results[name] = {"command": " ".join(command), "returncode": completed.returncode, "output_tail": output[-3000:]}
    return results


def _activation_request(manifest: dict[str, Any]) -> str:
    policy = json.loads(_path("fixtures/investigation/source-policy.json").read_text(encoding="utf-8"))
    hosts = "\n".join(f"- `{host}`" for host in manifest["allowed_hosts"])
    return f"""# G10R-X activation request

## Status

`PHASE_A_READY_FOR_OWNER_ACTIVATION` is preparation only. It does not start
Phase B, construct a provider, open the network, read credentials, or spend
money.

## Frozen boundary

- Manifest ID: `{manifest['manifest_id']}`
- Manifest SHA-256: `{digest(manifest)}`
- Provider: `{manifest['model_policy']['provider']}`, Responses API
- Model: `{manifest['model_policy']['model']}`
- Reasoning effort: `{manifest['model_policy']['reasoning_effort']}`
- Store: `{str(manifest['model_policy']['store']).lower()}`
- Source policy: `{policy['policy_version']}`, exact-host read-only GET-only, no credentials
- Per-treatment-case limits: `{json.dumps(manifest['limits_per_treatment_case'], sort_keys=True)}`
- Hard aggregate external-spend cap: `${manifest['hard_total_external_spend_cap_usd']:.2f}`
- Paid output namespace: `artifacts/goals/G10R-V/`

### Frozen hosts

{hosts}

## Required activation

The owner must separately authorize G10R-V by naming this exact manifest ID and
hash, provider/model, read-only network permission, spend cap, and output
namespace. Completing or committing G10R-X is not activation.
"""


def _report(status: str, checks: dict[str, Any], manifest: dict[str, Any]) -> str:
    rows = "\n".join(f"- `{key}`: `{value}`" for key, value in checks.items())
    return f"""# G10R-X fresh Phase-A freeze after live wiring

## Handoff

`{status}`

This repository-local freeze made no model calls, network requests, subscription
requests, credential reads, laboratory actions, or external writes. G10R-U and
all earlier namespaces remain historical and unchanged.

## Checks

{rows}

- Manifest: `artifacts/goals/G10R-X/manifest.json`
- Readiness: `artifacts/goals/G10R-X/readiness.json`
- Activation request: `artifacts/goals/G10R-X/activation-request.md`
- Manifest SHA-256: `{digest(manifest)}`

Only a separate owner activation may make G10R-V eligible.
"""


def freeze(*, output_dir: Path = OUTPUT, refresh: bool = False) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    historical_before = _snapshot()
    phase_first = phase_a()
    phase_second = phase_a()
    phase_stable = canonical(phase_first) == canonical(phase_second)
    previous_u_manifest = json.loads(_path("artifacts/goals/G10R-U/manifest.json").read_text(encoding="utf-8"))
    wiring_report = json.loads(_path(W_FILES["wiring_report"]).read_text(encoding="utf-8"))
    manifest = dict(frozen_manifest())
    _refresh_manifest_hashes(manifest.get("files", {}))
    manifest["source_policy_sha256"] = file_digest(_path("fixtures/investigation/source-policy.json"))
    manifest.update({
        "manifest_id": MANIFEST_ID,
        "freeze_goal": GOAL,
        "predecessor_manifest_id": previous_u_manifest.get("manifest_id"),
        "predecessor_manifest_sha256": digest(previous_u_manifest),
        "g10r_w_verdict": wiring_report.get("status"),
        "g10r_w_wiring": {"files": _file_map(), "external_calls": False},
    })
    # Self-tests inspect the candidate manifest from the output namespace.
    # Materialize it before testing when the caller explicitly refreshes a
    # freeze; a failed run is still recorded as NO_GO in readiness.json.
    manifest_matches_existing = not manifest_path.exists() or json.loads(manifest_path.read_text(encoding="utf-8")) == manifest
    if refresh or not manifest_path.exists():
        write_json(manifest_path, manifest)
    tests = _tests()
    historical_after = _snapshot()
    checks = {
        "manifest_id_new": manifest["manifest_id"] == MANIFEST_ID,
        "manifest_inputs_exist_and_hash": all(file_digest(_path(item["path"])) == item["sha256"] for item in manifest["g10r_w_wiring"]["files"].values()),
        "predecessor_manifest_preserved": historical_before == historical_after,
        "phase_a_stable": phase_stable and phase_first.get("status") == "AWAITING_OWNER_ACTIVATION",
        "g10r_w_ready": wiring_report.get("status") == "RUNTIME_RESEARCH_LOOP_WIRED",
        "no_live_side_effects": wiring_report.get("external_calls") is False,
        "focused_tests_passed": tests["focused"]["returncode"] == 0,
        "full_suite_passed": tests["full"]["returncode"] == 0,
        "source_policy_hash_present": bool(manifest.get("source_policy_sha256")),
        "aggregate_cap_usd": manifest.get("hard_total_external_spend_cap_usd"),
        "repeated_manifest_not_overwritten": manifest_matches_existing or refresh,
    }
    ready = all(value is True for key, value in checks.items() if key not in {"aggregate_cap_usd"}) and manifest["hard_total_external_spend_cap_usd"] == 25.0
    status = "PHASE_A_READY_FOR_OWNER_ACTIVATION" if ready else "PHASE_A_FREEZE_NO_GO"
    if manifest_path.exists() and not manifest_matches_existing and not refresh:
        status = "PHASE_A_FREEZE_NO_GO"
    if status == "PHASE_A_READY_FOR_OWNER_ACTIVATION":
        write_json(manifest_path, manifest)
    readiness = {
        "schema_version": "1.0", "goal": GOAL, "status": status,
        "manifest_id": MANIFEST_ID, "manifest_sha256": digest(manifest),
        "predecessor_manifest_id": previous_u_manifest.get("manifest_id"),
        "predecessor_manifest_sha256": digest(previous_u_manifest),
        "checks": checks, "tests": tests,
        "authority": {"model_calls": "none", "network": "none", "credentials": "none", "subscriptions": "prohibited", "laboratory": "prohibited", "evidence_promotion": "prohibited"},
        "next_action": "Owner may review and separately authorize G10R-V with this exact manifest." if ready else "Repair the failed freeze invariant before activation.",
    }
    write_json(output_dir / "readiness.json", readiness)
    if ready:
        (output_dir / "activation-request.md").write_text(_activation_request(manifest), encoding="utf-8")
    (output_dir / "report.md").write_text(_report(status, checks, manifest), encoding="utf-8")
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
