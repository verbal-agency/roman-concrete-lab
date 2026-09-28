import json
import unittest
from copy import deepcopy
from pathlib import Path

from tools.literature_audit.decision import decide, decide_material_candidates, load_candidates, load_families


ROOT = Path(__file__).resolve().parents[2]


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.families = load_families(ROOT / "data/processed/literature-sufficiency-study-families.jsonl")
        self.candidates = load_candidates(ROOT / "data/processed/literature-sufficiency-material-candidates.jsonl")

    def test_material_candidate_is_provisionally_plausible_but_blocked(self):
        result = decide_material_candidates(self.candidates)
        self.assertEqual(result["verdict"], "AUDIT_INCOMPLETE")
        self.assertEqual(result["provisional_verdict"], "LAB_CANDIDATE_PLAUSIBLE")
        self.assertEqual(result["provisional_plausible_candidate_count"], 3)

    def test_material_candidate_can_close_after_adjudication(self):
        adjudicated = deepcopy(self.candidates)
        for candidate in adjudicated:
            candidate["adjudication_status"] = "adjudicated"
        result = decide_material_candidates(adjudicated, human_adjudicated=True)
        self.assertEqual(result["verdict"], "LAB_CANDIDATE_PLAUSIBLE")

    def test_screened_corpus_is_replication_first(self):
        adjudicated = deepcopy(self.families)
        for family in adjudicated:
            if family["tier"] == "A":
                family["adjudication_status"] = "adjudicated"
        result = decide(adjudicated, audit_complete=True, saturated=True, human_adjudicated=True)
        self.assertEqual(result["verdict"], "REPLICATION_STUDY_REQUIRED")
        self.assertEqual(result["independent_tier_a_families"], 2)
        self.assertEqual(result["tier_a_arms"], 3)
        self.assertFalse(result["tier_a_external_replication"])

    def test_human_flag_cannot_override_pending_direct_family(self):
        result = decide(self.families, audit_complete=True, saturated=True, human_adjudicated=True)
        self.assertEqual(result["verdict"], "AUDIT_INCOMPLETE")
        self.assertFalse(result["human_adjudicated"])

    def test_incomplete_audit_never_emits_substantive_verdict(self):
        result = decide(self.families, audit_complete=True, saturated=True, human_adjudicated=False)
        self.assertEqual(result["verdict"], "AUDIT_INCOMPLETE")
        self.assertEqual(result["provisional_verdict"], "REPLICATION_STUDY_REQUIRED")

    def test_fixture_cases_include_failure_modes(self):
        cases = [json.loads(line) for line in (ROOT / "fixtures/literature_audit/cases.jsonl").read_text().splitlines()]
        self.assertEqual({case["case_id"] for case in cases}, {
            "positive_tier_a", "negative_context_review", "duplicate_derivative",
            "contradictory_screening", "malformed_missing_family", "partial_access",
            "budget_exhaustion", "unsupported_format",
        })


if __name__ == "__main__":
    unittest.main()
