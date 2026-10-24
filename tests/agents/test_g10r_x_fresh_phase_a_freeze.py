from __future__ import annotations

import json
from pathlib import Path

from src.roman_concrete_lab.agents.investigation import file_digest
from tools.tournament.replay import ROOT


def test_g10r_x_is_ready_and_hashes_the_post_wiring_inputs():
    artifact_dir = ROOT / "artifacts/goals/G10R-X"
    manifest = json.loads((artifact_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_id"] == "G10R-X-fresh-phase-a-research-loop-wiring-v1"
    assert manifest["predecessor_manifest_id"] == "G10R-U-fresh-phase-a-research-loop-v1"
    assert manifest["g10r_w_verdict"] == "RUNTIME_RESEARCH_LOOP_WIRED"
    assert all(
        file_digest(ROOT / item["path"]) == item["sha256"]
        for item in manifest["g10r_w_wiring"]["files"].values()
    )
