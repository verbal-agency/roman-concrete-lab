import unittest
from copy import deepcopy

from src.roman_concrete_lab.agents.mechanism_tournament import (
    MechanismBlackboard,
    allocate_mechanism_focus,
    load_rosters,
    phase_a,
    run_offline_case,
    validate_proponent_report,
    validate_roster,
)
from src.roman_concrete_lab.retrieval import BudgetExhausted, PolicyBlocked, StaleContext
from tools.tournament.replay import ROOT


class MechanismTournamentTests(unittest.TestCase):
    def setUp(self):
        self.roster = load_rosters()["S-ACTIVE-TRANSFER"]

    def test_rosters_have_candidates_null_and_open_slot(self):
        result = validate_roster(self.roster)
        self.assertTrue(result["passes"])
        self.assertEqual(result["candidate_count"], 2)
        self.assertEqual(len(result["null_ids"]), 1)
        self.assertEqual(len(result["open_slot_ids"]), 1)

    def test_proponents_are_private_until_all_commit(self):
        board = MechanismBlackboard(roster=self.roster, context_hash="sha256:context")
        cards = [card for card in self.roster["mechanisms"] if card["kind"] != "OPEN_SLOT"]
        from src.roman_concrete_lab.agents.mechanism_tournament import _offline_report

        board.submit_proponent(_offline_report(cards[0]))
        with self.assertRaises(PolicyBlocked):
            board.read_shared()
        board.submit_proponent(_offline_report(cards[1]))
        board.submit_proponent(_offline_report(cards[2]))
        self.assertEqual(len(board.share()), 3)

    def test_structural_audit_requires_sharing_and_admission_is_bounded(self):
        from src.roman_concrete_lab.agents.mechanism_tournament import _offline_critique, _offline_report

        board = MechanismBlackboard(roster=self.roster, context_hash="sha256:context")
        card = self.roster["mechanisms"][0]
        with self.assertRaises(PolicyBlocked):
            board.add_critique(_offline_critique(card, "evidence_skeptic"))
        for item in self.roster["mechanisms"]:
            if item["kind"] != "OPEN_SLOT":
                board.submit_proponent(_offline_report(item))
        board.share()
        board.add_critique(_offline_critique(card, "evidence_skeptic"))
        admission_card = deepcopy(self.roster["mechanisms"][-1])
        admission_card.update({"mechanism_id": "S-ACTIVE-TRANSFER-OPEN-NEW", "kind": "CANDIDATE", "mechanism_statement": "A bounded new mechanism.", "prior_basis": "typed uncertainty"})
        board.admit_open_mechanism({"schema_version":"1.0","admission_id":"A-1","case_id":"S-ACTIVE-TRANSFER","mechanism_card":admission_card,"reason":"distinct discriminator","evidence_locator":"TRACE-1","uncertainty_basis":"unresolved","budget_debit":1,"status":"ADMITTED"})
        with self.assertRaises(PolicyBlocked):
            board.admit_open_mechanism({"schema_version":"1.0","admission_id":"A-2","case_id":"S-ACTIVE-TRANSFER","mechanism_card":admission_card,"reason":"duplicate","evidence_locator":"TRACE-2","uncertainty_basis":"unresolved","budget_debit":1,"status":"ADMITTED"})

    def test_focus_is_deterministic_and_preserves_null_and_rival(self):
        stats = [
            {"mechanism_id":"M2","expected_discrimination":1,"unresolved_uncertainty":2,"provenance_risk":0,"novelty":1,"duplicate_work":0,"feasible":True},
            {"mechanism_id":"NULL","expected_discrimination":1,"unresolved_uncertainty":1,"provenance_risk":1,"novelty":0,"duplicate_work":0,"feasible":True},
            {"mechanism_id":"M1","expected_discrimination":2,"unresolved_uncertainty":1,"provenance_risk":0,"novelty":1,"duplicate_work":0,"feasible":True},
        ]
        first = allocate_mechanism_focus(stats, 6, null_mechanism_id="NULL")
        second = allocate_mechanism_focus(list(reversed(stats)), 6, null_mechanism_id="NULL")
        self.assertEqual(first, second)
        self.assertGreater(first["allocations"]["NULL"], 0)
        self.assertGreater(first["allocations"]["M1"], 0)

    def test_focus_abstains_when_budget_cannot_preserve_null_and_rival(self):
        stats = [{"mechanism_id":"NULL","expected_discrimination":1,"unresolved_uncertainty":1,"feasible":True}]
        result = allocate_mechanism_focus(stats, 1, null_mechanism_id="NULL")
        self.assertEqual(result["status"], "ABSTAIN")
        with self.assertRaises(BudgetExhausted):
            allocate_mechanism_focus(stats, -1, null_mechanism_id="NULL")

    def test_offline_run_preserves_rival_and_null_and_replays(self):
        result = run_offline_case(self.roster)
        self.assertEqual(result["ledger"]["status"], "REVIEW_REQUIRED")
        self.assertTrue(result["ledger"]["null_retained"])
        self.assertGreater(result["ledger"]["scoring"]["primary_score"], 0)
        self.assertEqual(result["ledger"]["scoring"]["advocacy_credit"], 0)
        self.assertEqual(result["ledger"]["scoring"]["consensus_credit"], 0)
        self.assertEqual(result["ledger"]["scoring"]["mechanism_count_credit"], 0)
        self.assertIn(self.roster["mechanisms"][2]["mechanism_id"], result["ledger"]["credible_rival_ids"])
        board = MechanismBlackboard(roster=self.roster, context_hash="sha256:context")
        event = {"case_id":"S-ACTIVE-TRANSFER","event_type":"CHECKPOINT"}
        self.assertFalse(board.append_event(event_id="E-1", event=event)["replayed"])
        self.assertTrue(board.append_event(event_id="E-1", event=event)["replayed"])
        with self.assertRaises(StaleContext):
            board.append_event(event_id="E-2", event=event, context_hash="sha256:stale")
        with self.assertRaises(PolicyBlocked):
            board.append_event(event_id="E-3", event={"case_id":"other-problem"})

    def test_checkpoint_resume_and_conflicting_claim_are_replayable(self):
        from src.roman_concrete_lab.agents.mechanism_tournament import _offline_critique, _offline_report

        board = MechanismBlackboard(roster=self.roster, context_hash="sha256:context")
        cards = [card for card in self.roster["mechanisms"] if card["kind"] != "OPEN_SLOT"]
        board.submit_proponent(_offline_report(cards[0]))
        resumed = MechanismBlackboard.from_checkpoint(board.checkpoint())
        for card in cards[1:]:
            resumed.submit_proponent(_offline_report(card))
        resumed.share()
        critique = _offline_critique(cards[0], "evidence_skeptic")
        critique["contradiction_status"] = "CONTRADICTION_FOUND"
        resumed.add_critique(critique)
        resumed.allocate_focus(remaining_actions=6)
        ledger = resumed.adjudicate()
        self.assertEqual(ledger["scoring"]["invalid_claim_count"], 0)
        self.assertTrue(any(event["event_type"] == "STRUCTURAL_CRITIQUE" for event in ledger["events"]))

    def test_missing_falsifier_and_unsupported_authority_fail_closed(self):
        from src.roman_concrete_lab.agents.mechanism_tournament import _offline_report

        report = _offline_report(self.roster["mechanisms"][0])
        del report["claims"][0]["falsifier"]
        with self.assertRaises(Exception):
            validate_proponent_report(report)
        report = _offline_report(self.roster["mechanisms"][0])
        report["claims"][0]["statement"] = "This mechanism is proven and validated."
        with self.assertRaises(PolicyBlocked):
            validate_proponent_report(report)

    def test_phase_a_is_ready_without_external_authority(self):
        result = phase_a()
        self.assertEqual(result["status"], "MECHANISM_SOCIETY_READY")
        self.assertTrue(result["roster_audit"]["passes"])
        self.assertTrue(result["behavior_fixture_report"]["passes"])
        self.assertTrue(result["budget_equality"]["passes"])
        self.assertFalse(result["phase_b_authorized"])
        self.assertEqual(result["authority"]["network"], "none")


if __name__ == "__main__":
    unittest.main()
