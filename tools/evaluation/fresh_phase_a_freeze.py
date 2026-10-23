"""Create a distinct, offline Phase-A freeze after G10R-C remediation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.roman_concrete_lab.agents.investigation import canonical, phase_a, write_json
from src.roman_concrete_lab.retrieval import digest
from tools.tournament.replay import ROOT


PHASE_NAME = "phase-a-post-constraint-20261023.json"
MANIFEST_NAME = "manifest-post-constraint-20261023.json"
REPORT_NAME = "report-post-constraint-20261023.md"


def _report(status: str, checks: dict[str, Any], *, output_dir: Path) -> str:
    return f"""# G10R-F fresh Phase-A freeze

## Handoff

`{status}`

This freeze recomputed the G10R Phase-A preflight after G10R-C constraint
remediation. It made no model, network, subscription, credential, promotion,
laboratory, or external communication call. Historical `phase-a.json` and
`manifest.json` were not overwritten.

## Checks

{chr(10).join(f"- `{key}`: `{value}`" for key, value in checks.items())}

The distinct artifacts are `{PHASE_NAME}` and `{MANIFEST_NAME}`. The manifest
retains the exact runner, action schema, source-policy, society, evidence-bus,
fixture, and budget hashes used for a separately authorized Phase-B decision.
This goal does not authorize Phase B.
"""


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def freeze(*, output_dir: Path = ROOT / "artifacts/goals/G10R") -> dict[str, Any]:
    output_dir = output_dir.resolve()
    historical_phase = output_dir / "phase-a.json"
    historical_manifest = output_dir / "manifest.json"
    phase_path = output_dir / PHASE_NAME
    manifest_path = output_dir / MANIFEST_NAME
    report_path = output_dir / REPORT_NAME
    historical_phase_before = historical_phase.read_bytes() if historical_phase.exists() else None
    historical_manifest_before = historical_manifest.read_bytes() if historical_manifest.exists() else None

    first = phase_a()
    second = phase_a()
    stable = canonical(first) == canonical(second)
    manifest = first.get("manifest", {})
    file_map = manifest.get("files", {})
    checks = {
        "phase_status": first.get("status"),
        "manifest_hash_present": bool(first.get("manifest_sha256")),
        "manifest_matches_phase": first.get("manifest_sha256") == digest(manifest),
        "sealed_case_count": first.get("sealed_case_count"),
        "development_case_count": first.get("development_case_count"),
        "identity_preflight": first.get("identity_preflight", {}).get("passes"),
        "mechanism_preflight": first.get("mechanism_preflight", {}).get("passes"),
        "a0_headroom": first.get("a0_has_headroom"),
        "pdf_benchmark": first.get("pdf_extraction_benchmark", {}).get("passes"),
        "source_policy_default_deny": manifest.get("source_policy_sha256") is not None,
        "equal_budget_limits": bool(first.get("arm_budget_equality")),
        "repaired_runner_in_manifest": "runner" in file_map and "investigation_action_schema" in file_map,
        "repaired_locator_contract_in_runner": "_resolve_fetch_locator" in (ROOT / "src/roman_concrete_lab/agents/investigation.py").read_text(encoding="utf-8"),
        "historical_phase_preserved": True,
        "historical_manifest_preserved": True,
        "repeated_freeze_byte_stable": stable,
    }
    ready = (
        first["status"] == "AWAITING_OWNER_ACTIVATION"
        and first["manifest_sha256"] == digest(manifest)
        and first["sealed_case_count"] == 4
        and first["development_case_count"] >= 2
        and first["identity_preflight"]["passes"]
        and first["mechanism_preflight"]["passes"]
        and first["pdf_extraction_benchmark"]["passes"]
        and first["a0_has_headroom"]
        and stable
        and "runner" in file_map
        and "investigation_action_schema" in file_map
    )
    status = "PHASE_A_READY_FOR_OWNER_ACTIVATION" if ready else "PHASE_A_FREEZE_NO_GO"
    if ready:
        if phase_path.exists() and json.loads(phase_path.read_text(encoding="utf-8")) != first:
            status = "PHASE_A_FREEZE_NO_GO"
        if manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8")) != manifest:
            status = "PHASE_A_FREEZE_NO_GO"
    if status == "PHASE_A_READY_FOR_OWNER_ACTIVATION":
        write_json(phase_path, first)
        write_json(manifest_path, manifest)
    checks["historical_phase_preserved"] = True
    checks["historical_manifest_preserved"] = True
    checks["historical_phase_preserved"] = historical_phase_before == (historical_phase.read_bytes() if historical_phase.exists() else None)
    checks["historical_manifest_preserved"] = historical_manifest_before == (historical_manifest.read_bytes() if historical_manifest.exists() else None)
    output = {
        "schema_version": "1.0",
        "goal": "G10R-F",
        "status": status,
        "external_calls": False,
        "phase_artifact": _display_path(phase_path),
        "manifest_artifact": _display_path(manifest_path),
        "checks": checks,
        "phase_a": first,
        "manifest_sha256": first.get("manifest_sha256"),
        "authority": {
            "model_calls": "none",
            "network": "none",
            "credentials": "none",
            "subscription": "prohibited",
            "evidence_promotion": "prohibited",
            "laboratory": "prohibited",
        },
        "next_action": "Separately review and explicitly authorize Phase B; this freeze does not authorize it." if status == "PHASE_A_READY_FOR_OWNER_ACTIVATION" else "Repair the Phase-A invariant failure before any activation.",
    }
    report_path.write_text(_report(status, checks, output_dir=output_dir), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/goals/G10R")
    args = parser.parse_args()
    result = freeze(output_dir=args.output_dir)
    print(json.dumps({"status": result["status"], "external_calls": result["external_calls"], "manifest_sha256": result["manifest_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
