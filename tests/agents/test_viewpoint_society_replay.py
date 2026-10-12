import json
import unittest

from tools.evaluation.viewpoint_society_replay import replay


class ViewpointSocietyReplayTests(unittest.TestCase):
    def test_phase_a_meets_viewpoint_behavior_gate(self):
        output = replay()
        self.assertEqual(output["status"], "SOCIETY_DESIGN_READY")
        self.assertFalse(output["external_calls"])
        self.assertTrue(all(output["required_behavior_checks"].values()))
        self.assertGreaterEqual(output["sealed_case_count"], 1)

    def test_phase_a_replay_is_stable(self):
        first = json.dumps(replay(), sort_keys=True, separators=(",", ":"))
        second = json.dumps(replay(), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
