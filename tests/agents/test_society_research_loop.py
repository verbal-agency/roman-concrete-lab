import json
import unittest

from jsonschema import validate

from src.roman_concrete_lab.agents.research_loop import OfflineResearchLoop, run_arm
from src.roman_concrete_lab.retrieval import PolicyBlocked
from tools.tournament.replay import ROOT


class SocietyResearchLoopTests(unittest.TestCase):
    def test_search_selection_fetch_and_page_card_are_separate(self):
        partial = run_arm("R0_SINGLE", stop_after_stage="CANDIDATE_TRIAGE")
        self.assertEqual(partial["cards"], [])
        self.assertTrue(partial["selections"])
        final = OfflineResearchLoop("R0_SINGLE", checkpoint=partial).run()
        self.assertEqual(final["metrics"]["paper_card_count"], 1)
        self.assertEqual(final["cards"][0]["facts"][0]["page_locator"], "#page=1")

    def test_prose_fetch_request_is_rejected_before_adapter(self):
        loop = OfflineResearchLoop("R0_SINGLE")
        result = loop.fetch_request({"locator": "https://digitalcommons.usu.edu/etd2023/669/", "instruction": "download this paper"})
        self.assertEqual(result["status"], "INVALID_FETCH_REQUEST")
        self.assertFalse(result["adapter_called"])

    def test_metadata_candidate_is_retained_without_evidence_credit(self):
        loop = OfflineResearchLoop("R0_SINGLE")
        result = loop.fetch_request({"source_candidate_id": "SRC-METADATA-DOI"})
        self.assertEqual(result["status"], "METADATA_ONLY")
        self.assertFalse(result["adapter_called"])
        self.assertEqual(loop.state["cards"], [])

    def test_late_reports_enter_latest_dossier_revision(self):
        result = run_arm("R3_VIEWPOINT_ADAPTIVE")
        revisions = result["dossier_revisions"]
        self.assertEqual([item["revision"] for item in revisions], [1, 2, 3])
        self.assertTrue(set(revisions[-1]["report_ids"]) > set(revisions[0]["report_ids"]))
        self.assertTrue(set(revisions[-1]["critique_ids"]))

    def test_deliberate_dossier_omission_is_a_failing_diagnostic(self):
        loop = OfflineResearchLoop("R3_VIEWPOINT_ADAPTIVE")
        loop.run()
        loop.state["dossier_revisions"][-1]["report_ids"] = loop.state["dossier_revisions"][-1]["report_ids"][:-1]
        self.assertFalse(loop.dossier_integrity()["passes"])
        loop._score()
        self.assertEqual(loop.state["metrics"]["dossier_membership_integrity"], 0)

    def test_focus_is_highest_first_and_task_specific(self):
        result = run_arm("R3_VIEWPOINT_ADAPTIVE")
        focus = result["focus"][0]
        self.assertEqual(focus["ranked_tasks"][0], "TASK-VP-MECHANISM")
        self.assertEqual(focus["allocations"], ["TASK-VP-MECHANISM", "TASK-VP-RIVAL"])
        self.assertTrue(any(item["kind"] == "FOCUS_FOLLOW_UP" and item["payload"]["task_id"] == "TASK-VP-MECHANISM" for item in result["actions"]))

    def test_open_slot_is_evidence_conditioned(self):
        fixed = run_arm("R2_VIEWPOINT_FIXED")
        adaptive = run_arm("R3_VIEWPOINT_ADAPTIVE")
        single = run_arm("R0_SINGLE")
        self.assertEqual(fixed["open_admissions"][0]["status"], "REJECTED_REDUNDANT")
        self.assertEqual(adaptive["open_admissions"][0]["status"], "ADMITTED")
        self.assertEqual(single["open_admissions"][0]["status"], "ABSTAINED_NO_DISTINCT_VIEWPOINT")
        self.assertEqual(adaptive["open_admissions"][0]["promotion_status"], "REVIEW_REQUIRED")

    def test_semantic_duplicate_does_not_fetch_twice(self):
        result = run_arm("R1_SHARED_SUPPORT")
        self.assertEqual(result["budget"]["usage"]["document_fetches"], 1)
        self.assertTrue(any(item["kind"] == "SEMANTIC_DUPLICATE" for item in result["actions"]))

    def test_typed_score_is_invariant_to_wording(self):
        loop = OfflineResearchLoop("R3_VIEWPOINT_ADAPTIVE")
        result = loop.run()
        original = dict(result["metrics"])
        for report in loop.state["reports"]:
            report["narrative"] = "A completely different wording with the same typed IDs and stance."
        loop._score()
        self.assertEqual(loop.state["metrics"], original)

    def test_support_need_requires_observable_work_for_completion(self):
        loop = OfflineResearchLoop("R0_SINGLE")
        need = {
            "schema_version": "1.0", "need_id": "NEED-TEST", "case_id": "CASE-RESEARCH-LOOP", "problem_id": "roman-hot-mix", "problem_version": "1.0", "viewpoint_id": "VP-TEST", "claim_ids": ["CLAIM-TEST"], "task_type": "RETRIEVAL", "question": "test", "expected_decision_change": 1, "required_evidence_kind": "PAGE_CARD", "known_candidate_ids": [], "unresolved_uncertainty": 1, "duplication_key": "test", "budget_request": 1, "status": "OPEN", "provenance": ["test"],
        }
        self.assertEqual(loop.support_need(need, stance="SUPPORTS")["status"], "ABSTAINED")
        self.assertEqual(loop.support_need(need, stance="WEAKENS", discriminator="a typed discriminator")["status"], "COMPLETE")

    def test_resume_is_byte_identical_at_boundary(self):
        full = run_arm("R3_VIEWPOINT_ADAPTIVE")
        for stage in ("SEARCHING", "SHARING", "FOCUSING", "ROUND_2", "ADJUDICATING"):
            partial = run_arm("R3_VIEWPOINT_ADAPTIVE", stop_after_stage=stage)
            resumed = OfflineResearchLoop("R3_VIEWPOINT_ADAPTIVE", checkpoint=partial).run()
            self.assertEqual(resumed["content_hash"], full["content_hash"], stage)
            self.assertEqual(resumed["budget"], full["budget"], stage)

    def test_stale_checkpoint_fails_closed(self):
        partial = run_arm("R3_VIEWPOINT_ADAPTIVE", stop_after_stage="SHARING")
        partial["arm"] = "R2_VIEWPOINT_FIXED"
        with self.assertRaises(PolicyBlocked):
            OfflineResearchLoop("R3_VIEWPOINT_ADAPTIVE", checkpoint=partial)


if __name__ == "__main__":
    unittest.main()
