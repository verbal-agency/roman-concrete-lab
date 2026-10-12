import json
import unittest

from tools.evaluation.society_plumbing_replay import replay


class SocietyPlumbingReplayTests(unittest.TestCase):
    def test_historical_run_preserves_omitted_candidates_without_inventing_support_tasks(self):
        output = replay()
        self.assertEqual(output["status"], "SOCIETY_PLUMBING_READY")
        self.assertFalse(output["external_calls"])
        self.assertGreater(output["summary"]["candidates_recovered_from_final_omission"], 0)
        self.assertEqual(output["summary"]["historical_support_task_links"], 0)
        society_transfer = next(
            row for row in output["before_after"]
            if row["arm"] == "A2-M" and row["case_id"] == "S-ACTIVE-TRANSFER"
        )
        self.assertEqual(society_transfer["before_final_portfolio_source_ids"], [])
        self.assertTrue(society_transfer["after_candidate_ledger_source_ids"])
        self.assertTrue(society_transfer["silent_drop_prevented"])
        self.assertTrue(all(item["support_task_id"] is None for item in society_transfer["historical_unassigned"]))

    def test_replay_is_stable(self):
        first = json.dumps(replay(), sort_keys=True, separators=(",", ":"))
        second = json.dumps(replay(), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
