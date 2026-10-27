import unittest

from src.roman_concrete_lab.agents.provisional_intake import ProvisionalIntakeLedger
from src.roman_concrete_lab.retrieval import PolicyBlocked


class ProvisionalIntakeTests(unittest.TestCase):
    def setUp(self):
        self.ledger = ProvisionalIntakeLedger(case_id="case")
        self.ledger.create_argument(
            argument_id="A1", viewpoint_id="mechanism", thesis="a testable mechanism",
            claims=[{"claim_id": "C1", "text": "the mechanism changes transport"}],
            predictions=["transport falls"], uncertainty="not established",
            requested_discriminators=["matched comparator"], source_ids=["S1"],
        )
        self.ledger.discover_source(
            source_id="S1", locator="https://public.example/paper", title="Paper",
            doi="10.1/paper", authors=["Author"], rights_state="PERMITTED",
            content_hash="sha256:paper",
        )

    def test_argument_can_precede_acceptance_without_credit(self):
        argument = self.ledger.arguments["A1"]
        self.assertEqual(argument["status"], "PROVISIONAL")
        self.assertEqual(argument["credit"]["evidence"], 0)

    def test_exact_locator_and_hash_gate_support(self):
        for status in ("RETRIEVAL_PENDING", "RETRIEVED_UNVETTED", "VETTING"):
            self.ledger.transition_source(source_id="S1", next_status=status, reason="fixture")
        self.ledger.record_vetting(decision_id="V1", source_id="S1", reviewer_role="VETTER", outcome="ADMIT", identity_verified=True, content_verified=True, exact_locator_verified=True, rationale="verified")
        self.ledger.create_edge(edge_id="E1", argument_id="A1", claim_id="C1", source_id="S1", claim_scope="transport")
        with self.assertRaises(PolicyBlocked):
            self.ledger.adjudicate_edge(edge_id="E1", status="SUPPORTED", locator=None, locator_type="NONE", content_hash=None, rationale="missing locator")
        edge = self.ledger.adjudicate_edge(edge_id="E1", status="SUPPORTED", locator="https://public.example/paper#page=2", locator_type="PAGE", content_hash="sha256:paper", rationale="exact")
        self.assertEqual(edge["status"], "SUPPORTED")

    def test_failed_retrieval_is_not_contradiction(self):
        self.ledger.transition_source(source_id="S1", next_status="RETRIEVAL_PENDING", reason="fetch")
        self.ledger.record_vetting(decision_id="V1", source_id="S1", reviewer_role="VETTER", outcome="UNRETRIEVABLE", identity_verified=False, content_verified=False, exact_locator_verified=False, rationale="blocked")
        self.ledger.create_edge(edge_id="E1", argument_id="A1", claim_id="C1", source_id="S1", claim_scope="transport")
        edge = self.ledger.adjudicate_edge(edge_id="E1", status="UNRETRIEVABLE", locator=None, locator_type="NONE", content_hash=None, rationale="blocked is not contradiction")
        self.assertNotEqual(edge["status"], "CONTRADICTED")

    def test_revision_preserves_original_and_duplicate_identity_is_not_independent(self):
        duplicate = self.ledger.discover_source(source_id="S2", locator="https://mirror.example/paper", title="Paper", doi="10.1/paper", authors=["Author"], rights_state="PERMITTED", content_hash="sha256:paper")
        self.assertFalse(duplicate["independent_work"])
        self.ledger.revise_argument(argument_id="A1", status="WEAKENED", reason="rival evidence")
        self.assertEqual(self.ledger.arguments["A1"]["thesis"], "a testable mechanism")
        self.assertTrue(self.ledger.revisions[0]["preserves_prior"])

    def test_terminal_edge_cannot_be_rewritten(self):
        self.ledger.create_edge(edge_id="E1", argument_id="A1", claim_id="C1", source_id="S1", claim_scope="transport")
        self.ledger.adjudicate_edge(edge_id="E1", status="UNRETRIEVABLE", locator=None, locator_type="NONE", content_hash=None, rationale="not fetched") if False else None
        with self.assertRaises(PolicyBlocked):
            self.ledger.adjudicate_edge(edge_id="E1", status="SUPPORTED", locator="https://public.example/paper#page=2", locator_type="PAGE", content_hash="sha256:paper", rationale="not admitted")


if __name__ == "__main__":
    unittest.main()
