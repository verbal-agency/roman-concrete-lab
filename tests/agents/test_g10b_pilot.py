import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jsonschema import validate

from src.roman_concrete_lab.agents.pilot import (
    CAP_USD,
    _call_or_replay,
    _load_checkpoint,
    load_jsonl,
    output_schema,
    phase_a,
    public_packet,
    score_output,
)
from src.roman_concrete_lab.agents.providers.openai_provider import (
    BudgetExceeded,
    BudgetLedger,
    OpenAIProvider,
    Pricing,
    ProviderUnavailable,
)
from tools.tournament.replay import ROOT


def valid_output(case_id="S-CONT-01", task_type="contradiction_triage"):
    return {
        "case_id": case_id,
        "task_type": task_type,
        "status": "REVIEW_REQUIRED",
        "summary": "The packet requires review.",
        "findings": [
            {
                "finding_id": "F1",
                "kind": "LIMITATION",
                "statement": "The evidence is incomplete.",
                "evidence_ids": ["E-S01"],
                "predicted_observation": "A matched result would reduce uncertainty.",
                "disconfirming_observation": "No matched difference would disconfirm the proposal.",
                "uncertainty": "No independent replication is established.",
            }
        ],
        "recommended_action": "Keep the result review-required.",
        "authority_note": "This derived output does not authorize laboratory work.",
    }


class FakeResponses:
    def __init__(self, output):
        self.output = output
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            id="response-secret-id",
            model="gpt-6-luna",
            output_text=json.dumps(self.output),
            usage=SimpleNamespace(
                input_tokens=400,
                output_tokens=200,
                input_tokens_details=SimpleNamespace(cached_tokens=100),
            ),
        )


class FakeClient:
    def __init__(self, output):
        self.responses = FakeResponses(output)


class MalformedResponses:
    def create(self, **kwargs):
        return SimpleNamespace(
            id="response-malformed",
            model="gpt-6-luna",
            output_text='{"summary":"truncated',
            status="incomplete",
            incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            usage=SimpleNamespace(
                input_tokens=10,
                output_tokens=100,
                input_tokens_details=SimpleNamespace(cached_tokens=0),
            ),
        )


class MalformedClient:
    def __init__(self):
        self.responses = MalformedResponses()


class CountingProvider:
    def __init__(self, trace):
        self.trace = trace
        self.calls = 0

    def call(self, **kwargs):
        self.calls += 1
        return dict(self.trace)


class G10BPilotTests(unittest.TestCase):
    def test_phase_a_freezes_four_non_ceiling_cases(self):
        result = phase_a()
        self.assertEqual(result["status"], "READY_FOR_LIVE_PILOT")
        self.assertTrue(result["c0_has_headroom"])
        self.assertEqual(len(result["controls"]), 4)
        self.assertEqual(result["manifest"]["call_count"], 20)
        self.assertEqual(result["manifest"]["budget_cap_usd"], CAP_USD)
        for item in result["controls"]:
            validate(item["output"], output_schema())

    def test_hidden_rubric_is_not_sent_to_treatments(self):
        case = load_jsonl(ROOT / "fixtures/agents/g10b/sealed.jsonl")[0]
        packet = public_packet(case)
        self.assertNotIn("rubric", packet)
        self.assertIn("evidence", packet)

    def test_budget_guard_fails_before_cap_and_records_usage(self):
        ledger = BudgetLedger(cap_usd=0.0001)
        with self.assertRaises(BudgetExceeded):
            ledger.preflight("x" * 3000, 1000, Pricing())
        normal = BudgetLedger(cap_usd=25.0)
        maximum = normal.preflight("short", 1800, Pricing())
        self.assertLess(maximum, 0.01)

    def test_provider_uses_frozen_responses_contract_without_storing(self):
        output = valid_output()
        client = FakeClient(output)
        provider = OpenAIProvider(
            root=ROOT,
            schema=output_schema(),
            budget=BudgetLedger(),
            client=client,
        )
        trace = provider.call(
            call_id="case:C1",
            instructions="closed world",
            packet={"case_id": "S-CONT-01"},
            max_output_tokens=1800,
        )
        request = client.responses.calls[0]
        self.assertEqual(request["model"], "gpt-6-luna")
        self.assertEqual(request["reasoning"], {"effort": "low"})
        self.assertFalse(request["store"])
        self.assertNotIn("tools", request)
        self.assertNotIn("response-secret-id", json.dumps(trace))
        self.assertGreater(trace["estimated_actual_cost_usd"], 0)

    def test_missing_key_and_malformed_output_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ProviderUnavailable):
                    OpenAIProvider(root=Path(directory), schema=output_schema(), budget=BudgetLedger())
        bad_client = FakeClient({"not": "the schema"})
        provider = OpenAIProvider(
            root=ROOT,
            schema=output_schema(),
            budget=BudgetLedger(),
            client=bad_client,
        )
        with self.assertRaises(ValueError):
            provider.call(call_id="bad", instructions="x", packet={}, max_output_tokens=100)

    def test_malformed_output_exposes_completion_diagnostics(self):
        provider = OpenAIProvider(
            root=ROOT,
            schema=output_schema(),
            budget=BudgetLedger(),
            client=MalformedClient(),
        )
        with self.assertRaisesRegex(ValueError, r"status='incomplete'.*incomplete_reason='max_output_tokens'.*output_chars=21"):
            provider.call(call_id="truncated", instructions="x", packet={}, max_output_tokens=100)

    def test_checkpoint_replays_duplicate_and_rejects_stale_context(self):
        trace = {"output": valid_output(), "estimated_actual_cost_usd": 0.0}
        provider = CountingProvider(trace)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            checkpoint = {"manifest_sha256": "sha256:one", "traces": {"duplicate": trace}}
            path.write_text(json.dumps(checkpoint), encoding="utf-8")
            replayed = _call_or_replay(
                provider,
                checkpoint,
                path,
                call_id="duplicate",
                instructions="x",
                packet={},
                max_output_tokens=100,
            )
            self.assertTrue(replayed["replayed"])
            self.assertEqual(provider.calls, 0)
            with self.assertRaises(ValueError):
                _load_checkpoint(path, "sha256:stale")

    def test_scorer_rejects_invalid_evidence_and_authority(self):
        case = load_jsonl(ROOT / "fixtures/agents/g10b/sealed.jsonl")[0]
        output = valid_output()
        output["findings"][0]["evidence_ids"] = ["FABRICATED"]
        output["authority_note"] = "Approved for execution."
        score = score_output(case, output)
        self.assertIn("FABRICATED", score["invalid_evidence_ids"])
        self.assertGreaterEqual(len(score["critical_failures"]), 2)


if __name__ == "__main__":
    unittest.main()
