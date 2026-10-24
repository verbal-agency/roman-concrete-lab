import json
import tempfile
import unittest
from pathlib import Path

from tools.evaluation.society_research_loop_ablation import run


class SocietyResearchLoopAblationTests(unittest.TestCase):
    def test_four_arms_have_equal_ceilings_and_r3_has_unique_contribution(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run(Path(directory))
        self.assertEqual(result["verdict"], "SOCIETY_RESEARCH_LOOP_READY")
        self.assertTrue(result["replay"]["all_boundaries_byte_equivalent"])
        self.assertGreater(result["arms"]["R3_VIEWPOINT_ADAPTIVE"]["metrics"]["unique_attributable_contributions"], result["arms"]["R0_SINGLE"]["metrics"]["unique_attributable_contributions"])
        self.assertTrue(all(result["arms"][arm]["terminal"] == "COMPLETED" for arm in result["arms"]))

    def test_artifacts_are_machine_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            run(path)
            for name in ("diagnosis.json", "ablation-matrix.json", "run.json", "replay.json"):
                self.assertIsInstance(json.loads((path / name).read_text()), dict)
            self.assertIn("SOCIETY_RESEARCH_LOOP_READY", (path / "report.md").read_text())


if __name__ == "__main__":
    unittest.main()
