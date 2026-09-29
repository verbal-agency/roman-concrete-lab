import json
import unittest
from pathlib import Path

from tools.prelab.decision import classify_result, validate_result


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "fixtures/prelab"


class PrelabSpecificationTests(unittest.TestCase):
    def test_all_offline_fixtures_validate_and_classify_deterministically(self):
        for path in sorted(FIXTURES.glob("*.json")):
            case = json.loads(path.read_text())
            validate_result(case["result"])
            self.assertEqual(classify_result(case["result"]), case["expected_status"], path.name)

    def test_draft_is_watermarked_and_non_authorizing(self):
        text = (ROOT / "docs/protocols/prelab-study-specification.md").read_text()
        self.assertIn("DRAFT — EXPERT REVIEW REQUIRED", text)
        self.assertIn("not a laboratory protocol", text)
        self.assertIn("must not be used for physical execution", text)

    def test_ranking_is_conditional_and_abstains_outside_support(self):
        ranking = json.loads((ROOT / "data/processed/gp2-conditional-ranking.json").read_text())
        self.assertEqual(ranking["ranking_status"], "PROVISIONAL_BEST")
        self.assertEqual(ranking["provisional_best"]["candidate_id"], "RC-01")
        statuses = {entry["candidate_id"]: entry["status"] for entry in ranking["entries"]}
        self.assertEqual(statuses["RC-04"], "ABSTAIN")
        self.assertEqual(statuses["RC-02"], "ABSTAIN")
        self.assertIn("support_limit", ranking["provisional_best"])


if __name__ == "__main__":
    unittest.main()
