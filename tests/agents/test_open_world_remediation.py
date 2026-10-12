import json
import unittest

from tools.evaluation.open_world_replay import replay


class OpenWorldRemediationTests(unittest.TestCase):
    def test_existing_g10r_traces_replay_without_external_calls(self):
        output = replay()
        self.assertEqual(output["status"], "REPLAYABLE_AFTER_REPAIR")
        self.assertFalse(output["decision"]["all_external_calls"])
        self.assertEqual(len(output["score_ledger"]), 8)
        self.assertTrue(output["candidate_ledger"])
        self.assertTrue(all("discovery_score" in row for row in output["score_ledger"]))
        self.assertTrue(all("evidence_score" in row for row in output["score_ledger"]))
        self.assertTrue(all("hypothesis_score" in row for row in output["score_ledger"]))

    def test_replay_is_json_stable(self):
        first = json.dumps(replay(), sort_keys=True, separators=(",", ":"))
        second = json.dumps(replay(), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
