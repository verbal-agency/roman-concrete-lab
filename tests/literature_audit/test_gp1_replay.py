import unittest
from pathlib import Path

from tools.literature_audit.gp1_replay import replay


ROOT = Path(__file__).resolve().parents[2]


class GP1ReplayTests(unittest.TestCase):
    def test_replay_reconstructs_seedable_candidate_set(self):
        result = replay(
            ROOT / "data/processed/literature-sufficiency-material-candidates.jsonl",
            ROOT / "data/manifests/literature-sufficiency-sources.jsonl",
            ROOT / "data/processed/candidate-hypotheses.jsonl",
        )
        self.assertEqual(result["candidate_count"], 5)
        self.assertEqual(result["hypothesis_count"], 6)
        self.assertEqual(result["study_family_count"], 24)
        self.assertEqual(result["reconciled_supporting_record_count"], 10)
        self.assertEqual(result["provisional_plausible_candidate_count"], 3)
        self.assertEqual(
            result["exploration_seedability"]["seedable_candidate_ids"],
            ["RC-01", "RC-04", "RC-05"],
        )


if __name__ == "__main__":
    unittest.main()
