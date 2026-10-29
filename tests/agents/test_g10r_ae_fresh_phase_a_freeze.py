import json
import unittest

from src.roman_concrete_lab.agents.investigation import file_digest
from tools.tournament.replay import ROOT


class G10RAEFreshPhaseAFeezeTests(unittest.TestCase):
    def test_manifest_is_distinct_and_all_inputs_hash(self):
        directory = ROOT / "artifacts/goals/G10R-AE"
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_id"], "G10R-AE-fresh-phase-a-runner-intake-v1")
        self.assertEqual(manifest["activation_status"], "PENDING_OWNER_ACTIVATION")
        self.assertTrue(all(file_digest(ROOT / item["path"]) == item["sha256"] for item in manifest["files"].values()))

    def test_preflight_and_criterion_ledger_are_ready(self):
        directory = ROOT / "artifacts/goals/G10R-AE"
        preflight = json.loads((directory / "preflight.json").read_text(encoding="utf-8"))
        ledger = json.loads((directory / "criterion-ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(preflight["manifest_id"], "G10R-AE-fresh-phase-a-runner-intake-v1")
        self.assertIn(preflight["status"], {"PHASE_A_READY_FOR_OWNER_ACTIVATION", "PHASE_A_FREEZE_NO_GO"})
        self.assertTrue("checks" in preflight and "fault_injection" in preflight)
        self.assertEqual(ledger["goal_id"], "G10R-AE")
        self.assertEqual(preflight["authority"]["paid_spend_usd"], 0)


if __name__ == "__main__":
    unittest.main()
