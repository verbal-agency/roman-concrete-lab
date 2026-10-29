import json
import unittest

from jsonschema import ValidationError

from src.roman_concrete_lab.agents.proposal_machinery import (
    ProposalLedger,
    blind_for_scoring,
    score_proposal,
    validate_packet,
)
from src.roman_concrete_lab.retrieval import PolicyBlocked, StaleContext
from tools.tournament.replay import ROOT


def _fixtures() -> list[dict]:
    path = ROOT / "fixtures/investigation/g10r-af/proposals.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class ProposalMachineryTests(unittest.TestCase):
    def test_valid_packets_are_case_and_arm_bound(self):
        for packet in _fixtures():
            self.assertEqual(validate_packet(packet, case_id=packet["case_id"])["proposal_id"], packet["proposal_id"])
        illegal = dict(_fixtures()[0])
        illegal["status"] = "WINNER"
        with self.assertRaises(ValidationError):
            validate_packet(illegal)
        ledger = ProposalLedger(case_id="AF-HOT-LIME", arm="A1", context_hash="sha256:ctx")
        ledger.add(_fixtures()[0])
        with self.assertRaises(PolicyBlocked):
            ledger.add(_fixtures()[1])

    def test_incomplete_packet_is_retained_without_proposal_credit(self):
        packet = _fixtures()[2]
        ledger = ProposalLedger(case_id=packet["case_id"], arm=packet["arm"], context_hash="sha256:ctx")
        stored = ledger.add(packet)
        self.assertEqual(stored["status"], "PROPOSAL_INCOMPLETE")
        score = score_proposal(blind_for_scoring(stored))
        self.assertEqual(score["proposal_credit"], 0)
        self.assertEqual(score["pending_edge_count"], 1)

    def test_contradictions_and_pending_edges_are_preserved(self):
        packet = _fixtures()[1]
        score = score_proposal(blind_for_scoring(packet))
        self.assertEqual(score["contradicted_edge_count"], 1)
        self.assertEqual(score["pending_edge_count"], 1)
        self.assertEqual(score["rhetoric_credit"], 0)
        self.assertEqual(score["consensus_credit"], 0)
        self.assertEqual(score["answer_length_credit"], 0)
        self.assertEqual(score["viewpoint_count_credit"], 0)
        self.assertEqual(score["agent_count_credit"], 0)
        self.assertFalse(score["treatment_identity_available"])

    def test_malformed_duplicate_cross_case_and_stale_fail_closed(self):
        malformed = json.loads((ROOT / "fixtures/investigation/g10r-af/fault-cases.json").read_text(encoding="utf-8"))["malformed"]
        with self.assertRaises(ValidationError):
            validate_packet(malformed)
        packet = _fixtures()[0]
        ledger = ProposalLedger(case_id=packet["case_id"], arm=packet["arm"], context_hash="sha256:ctx")
        ledger.add(packet)
        changed = dict(packet)
        changed["predicted_observation"] = "changed payload"
        with self.assertRaises(PolicyBlocked):
            ledger.add(changed)
        with self.assertRaises(PolicyBlocked):
            ProposalLedger(case_id=packet["case_id"], arm=packet["arm"], context_hash="sha256:ctx").add({**packet, "case_id": "OTHER"})
        with self.assertRaises(StaleContext):
            ledger.attach_checkpoint({"case_id": packet["case_id"], "arm": packet["arm"], "context_hash": "sha256:other"})

    def test_checkpoint_contains_no_external_authority(self):
        packet = _fixtures()[3]
        ledger = ProposalLedger(case_id=packet["case_id"], arm=packet["arm"], context_hash="sha256:ctx")
        ledger.add(packet)
        checkpoint = ledger.attach_checkpoint({"case_id": packet["case_id"], "arm": packet["arm"], "context_hash": "sha256:ctx"})
        self.assertEqual(checkpoint["authority"]["model_calls"], 0)
        self.assertEqual(checkpoint["authority"]["network_calls"], 0)
        self.assertEqual(checkpoint["authority"]["paid_spend_usd"], 0)
        self.assertEqual(len(checkpoint["proposals"]), 1)


if __name__ == "__main__":
    unittest.main()
