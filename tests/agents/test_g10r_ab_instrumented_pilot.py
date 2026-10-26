from __future__ import annotations

import json
import tempfile
from pathlib import Path

from tools.evaluation.instrumented_integration_pilot import (
    FAILURE_MATRIX,
    REPAIR_FLAGS,
    prepare,
)


def test_offline_pilot_freezes_repairs_and_typed_failure_matrix() -> None:
    with tempfile.TemporaryDirectory() as directory:
        result = prepare(output_dir=Path(directory), run_tests=False)
        assert result["status"] == "OFFLINE_PILOT_READY_FOR_OWNER_ACTIVATION"
        config = json.loads((Path(directory) / "repair-config.json").read_text())
        events = json.loads((Path(directory) / "event-ledger.json").read_text())["events"]
        assert config["flags"] == REPAIR_FLAGS
        assert config["mutable_during_run"] is False
        assert len(events) == len(FAILURE_MATRIX)
        assert all(event["evidence_delta"] == 0.0 for event in events)


def test_offline_pilot_continues_safe_failures_and_stops_unsafe_ones() -> None:
    with tempfile.TemporaryDirectory() as directory:
        prepare(output_dir=Path(directory), run_tests=False)
        events = json.loads((Path(directory) / "event-ledger.json").read_text())["events"]
        assert any(event["continuation"] == "CONTINUE_RUN" for event in events)
        assert any(event["continuation"] == "TERMINAL_RUN" for event in events)
        postmortem = json.loads((Path(directory) / "postmortem.json").read_text())
        assert postmortem["status"] == "OFFLINE_FAILURE_MATRIX_PASS"
        assert postmortem["scientific_conclusion"] == "NONE; no model, network, or evidence promotion occurred"


def test_offline_pilot_replay_is_external_free_and_stable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        prepare(output_dir=Path(directory), run_tests=False)
        replay = json.loads((Path(directory) / "replay.json").read_text())
        assert replay["byte_stable"] is True
        assert replay["provider_calls"] == 0
        assert replay["network_calls"] == 0
        assert replay["paid_spend_usd"] == 0.0


def test_offline_pilot_does_not_claim_paid_criteria() -> None:
    with tempfile.TemporaryDirectory() as directory:
        prepare(output_dir=Path(directory), run_tests=False)
        ledger = json.loads((Path(directory) / "criterion-ledger.json").read_text())
        by_number = {item["criterion"]: item["status"] for item in ledger["criteria"]}
        assert by_number[10] == "PASS"
        assert by_number[11] == "PASS"
        assert by_number[1] == "PENDING_OWNER_ACTIVATION"
        assert by_number[9] == "PENDING_OWNER_ACTIVATION"
        assert ledger["criteria_pass"] is False
