import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.evaluation.fresh_phase_a_freeze_after_loop import freeze


class FreshPhaseAFreezeTests(unittest.TestCase):
    def _freeze(self, path: Path):
        test_results = {
            "focused": {"command": "focused", "returncode": 0, "output_tail": "14 passed"},
            "full": {"command": "full", "returncode": 0, "output_tail": "153 passed"},
        }
        with patch("tools.evaluation.fresh_phase_a_freeze_after_loop._run_tests", return_value=test_results):
            return freeze(output_dir=path)

    def test_freeze_includes_research_loop_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._freeze(Path(directory))
            self.assertEqual(result["status"], "PHASE_A_READY_FOR_OWNER_ACTIVATION")
            manifest = json.loads((Path(directory) / "manifest.json").read_text())
            self.assertEqual(manifest["manifest_id"], "G10R-U-fresh-phase-a-research-loop-v1")
            self.assertIn("research_loop_runner", manifest["g10r_t_research_loop"]["files"])
            self.assertIn("freeze_tests", manifest["g10r_t_research_loop"]["files"])
            self.assertTrue(result["checks"]["historical_namespaces_preserved"])

    def test_existing_conflicting_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            first = self._freeze(path)
            self.assertEqual(first["status"], "PHASE_A_READY_FOR_OWNER_ACTIVATION")
            manifest_path = path / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["manifest_id"] = "STALE-MANIFEST"
            manifest_path.write_text(json.dumps(manifest, sort_keys=True))
            second = self._freeze(path)
            self.assertEqual(second["status"], "PHASE_A_FREEZE_NO_GO")

    def test_activation_request_is_not_a_paid_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._freeze(Path(directory))
            request = (Path(directory) / "activation-request.md").read_text()
            self.assertEqual(result["status"], "PHASE_A_READY_FOR_OWNER_ACTIVATION")
            self.assertIn("explicitly", request)
            self.assertIn("$25.00", request)
            self.assertEqual(result["authority"]["model_calls"], "none")


if __name__ == "__main__":
    unittest.main()
