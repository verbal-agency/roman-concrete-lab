import tempfile
import unittest
import hashlib
from pathlib import Path

from src.roman_concrete_lab.agents.investigation import (
    BRANCHES,
    ActiveInvestigationRunner,
    InvestigationOrchestrator,
    OwnerActivationRequired,
    PrivateBranchWorkspace,
    RunStateMachine,
    allocate_focus,
    load_checkpoint,
    load_jsonl,
    phase_a,
    public_case,
    record_checkpoint_action,
    run_phase_b,
    schema,
    score_portfolio,
    source_identity_map,
    source_policy,
    validate_source_identity_map,
    validate_paper_evidence_card,
)
from src.roman_concrete_lab.retrieval import (
    InvestigationBudget,
    PolicyBlocked,
    RecordedRetrievalAdapter,
    StaleContext,
)
from tools.tournament.replay import ROOT


def hypothesis(source_id="SRC-S30-QUICKLIME"):
    return {
        "schema_version": "1.0",
        "hypothesis_id": "H1",
        "problem_id": "roman-hot-mix",
        "problem_version": "1.0",
        "source_candidate_ids": [source_id],
        "novelty_basis": "The quicklime and silica fume record is a transfer hypothesis, not direct evidence.",
        "transfer_type": "TRANSFER_HYPOTHESIS",
        "intervention": "quicklime and silica fume",
        "comparator": "a process-matched hot-mixed control is absent",
        "predicted_observation": "A matched control with a functional water endpoint would separate transfer from direct support.",
        "falsifier": "No functional recovery under a matched control would falsify transfer.",
        "support_region": "cement-based transfer domain; not hot-mixed lime-pozzolan mortar",
        "uncertainty": "Comparator and target-domain fit are unresolved.",
        "provenance": [source_id],
        "promotion_status": "REVIEW_REQUIRED",
    }


def portfolio(case_id="S-ACTIVE-TRANSFER", source_id="SRC-S30-QUICKLIME"):
    return {
        "schema_version": "1.0",
        "case_id": case_id,
        "status": "REVIEW_REQUIRED",
        "summary": "The public quicklime and silica fume record concerns a cement-based system and impermeability, not a process-matched hot-mixed target.",
        "source_candidate_ids": [source_id],
        "hypotheses": [hypothesis(source_id)],
        "leading_hypothesis_id": "H1",
        "credible_rival_ids": [],
        "unresolved_disputes": ["Whether transfer survives a process-matched functional recovery comparison."],
        "negative_searches": [],
        "next_discriminating_action": "Use a matched control and functional recovery endpoint; do not treat this as direct evidence.",
        "authority_note": "Review required; this source cannot promote performance or authorize laboratory work.",
    }


def branch_report(branch_id):
    return {
        "schema_version": "1.0",
        "case_id": "S-ACTIVE-TRANSFER",
        "branch_id": branch_id,
        "charter": f"frozen charter for {branch_id}",
        "action_ids": [f"A-{branch_id}"],
        "source_candidate_ids": [],
        "hypotheses": [],
        "negative_searches": ["no direct record"],
        "unresolved_questions": ["domain fit"],
        "proposed_next_action": "search the assigned frontier",
        "claimed_unique_contribution": "none yet",
        "status": "ABSTAIN",
    }


class FakeProvider:
    def __init__(self, case):
        self.case = case
        self.calls = []

    def call(self, **kwargs):
        self.calls.append(kwargs["call_id"])
        if kwargs["format_name"] == "g10r_a1_plan":
            output = {
                "schema_version": "1.0",
                "case_id": self.case["case_id"],
                "branch_id": "single_investigator",
                "primary_queries": [{"query": "quicklime self-healing bridge deck thesis", "index": "catalog", "rationale": "find lineage"}],
                "follow_up_queries": [],
                "requested_fetch_locators": [],
                "simulation_requests": [],
                "abstain_reason": "",
            }
        else:
            output = portfolio(self.case["case_id"], "SRC-USU-THESIS")
            output["summary"] = "Utah bridge record is derivative, not independent; permeability water-flow is a functional endpoint. Review required."
            output["hypotheses"][0]["source_candidate_ids"] = ["SRC-USU-THESIS"]
            output["hypotheses"][0]["provenance"] = ["SRC-USU-THESIS"]
        return {
            "call_id": kwargs["call_id"], "provider": "fake", "model": "fake", "reasoning_effort": "low", "store": False, "tools": [],
            "response_id_sha256": "sha256:fake", "output": output,
            "usage": {"input_tokens": 10, "output_tokens": 10},
            "estimated_maximum_cost_usd": 0.001, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0,
        }


class PrivacyProvider(FakeProvider):
    def __init__(self, case):
        super().__init__(case)
        self.branch_plan_packets = []

    def call(self, **kwargs):
        name = kwargs["format_name"]
        packet = kwargs["packet"]
        if name == "g10r_branch_plan":
            self.calls.append(kwargs["call_id"])
            self.branch_plan_packets.append(packet)
            return {
                "call_id": kwargs["call_id"], "provider": "fake", "model": "fake", "reasoning_effort": "low", "store": False, "tools": [],
                "response_id_sha256": "sha256:fake", "usage": {"input_tokens": 10, "output_tokens": 10}, "estimated_maximum_cost_usd": 0.001, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0,
                "output": {"schema_version": "1.0", "case_id": self.case["case_id"], "branch_id": packet["branch_id"], "primary_queries": [], "follow_up_queries": [], "requested_fetch_locators": [], "simulation_requests": [], "abstain_reason": "no query"},
            }
        if name == "g10r_branch_report":
            self.calls.append(kwargs["call_id"])
            report = branch_report(packet["branch_id"])
            report["case_id"] = self.case["case_id"]
            return {"call_id": kwargs["call_id"], "provider": "fake", "model": "fake", "reasoning_effort": "low", "store": False, "tools": [], "response_id_sha256": "sha256:fake", "output": report, "usage": {"input_tokens": 10, "output_tokens": 10}, "estimated_maximum_cost_usd": 0.001, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0}
        if name == "g10r_adjudication":
            self.calls.append(kwargs["call_id"])
            output = portfolio(self.case["case_id"], "SRC-USU-THESIS")
            return {"call_id": kwargs["call_id"], "provider": "fake", "model": "fake", "reasoning_effort": "low", "store": False, "tools": [], "response_id_sha256": "sha256:fake", "output": output, "usage": {"input_tokens": 10, "output_tokens": 10}, "estimated_maximum_cost_usd": 0.001, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0}
        return super().call(**kwargs)


class PaperCardProvider(FakeProvider):
    def call(self, **kwargs):
        if kwargs["format_name"] != "g10r_paper_evidence_card":
            return super().call(**kwargs)
        document = kwargs["packet"]["document"]
        page = document["page_spans"][0]
        output = {
            "schema_version": "1.0", "card_id": "CARD-1", "source_candidate_id": kwargs["packet"]["source_candidate"]["source_candidate_id"],
            "document_hash": document["content_hash"], "parser": document["parser"], "extraction_status": "EXTRACTED", "page_count": document["page_count"],
            "facts": [{"field": "endpoint", "value": "reported water-flow endpoint", "reporting_status": "REPORTED", "support_type": "DIRECT", "page_locator": page["locator"], "page_text_hash": page["text_hash"], "confidence": "HIGH"}],
            "unresolved": [], "authority_note": "Derived extraction for review; no evidence promotion, performance claim, or laboratory authority.",
        }
        self.calls.append(kwargs["call_id"])
        return {"call_id": kwargs["call_id"], "provider": "fake", "model": "fake", "reasoning_effort": "low", "store": False, "tools": [], "response_id_sha256": "sha256:fake", "output": output, "usage": {"input_tokens": 10, "output_tokens": 10}, "estimated_maximum_cost_usd": 0.001, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0}


class MechanismProvider(FakeProvider):
    def call(self, **kwargs):
        name = kwargs["format_name"]
        packet = kwargs["packet"]
        from src.roman_concrete_lab.agents.mechanism_tournament import _offline_critique, _offline_report, load_rosters

        if name == "g10m_proponent_plan":
            output = {"schema_version":"1.0","case_id":self.case["case_id"],"branch_id":packet["branch_id"],"primary_queries":[{"query":"quicklime mechanism discriminator","index":"catalog","rationale":"assigned mechanism frontier"}],"follow_up_queries":[],"requested_fetch_locators":[],"simulation_requests":[],"abstain_reason":""}
        elif name == "g10m_proponent_report":
            card = packet["mechanism_card"]
            output = _offline_report(card)
        elif name == "g10m_auditor_plan":
            output = {"schema_version":"1.0","case_id":self.case["case_id"],"branch_id":packet["branch_id"],"primary_queries":[{"query":"contradiction mechanism boundary","index":"catalog","rationale":"structural audit"}],"follow_up_queries":[],"requested_fetch_locators":[],"simulation_requests":[],"abstain_reason":""}
        elif name == "g10m_structural_critique":
            roster = load_rosters()[self.case["case_id"]]
            card = next(item for item in roster["mechanisms"] if item["kind"] != "OPEN_SLOT")
            output = _offline_critique(card, packet["structural_role"])
        elif name == "g10m_adjudication":
            output = portfolio(self.case["case_id"], "SRC-USU-THESIS")
        else:
            return super().call(**kwargs)
        self.calls.append(kwargs["call_id"])
        return {"call_id": kwargs["call_id"], "provider": "fake", "model": "fake", "reasoning_effort": "low", "store": False, "tools": [], "response_id_sha256": "sha256:fake", "output": output, "usage": {"input_tokens": 10, "output_tokens": 10}, "estimated_maximum_cost_usd": 0.001, "estimated_actual_cost_usd": 0.0, "latency_seconds": 0.0}


class ActiveInvestigationTests(unittest.TestCase):
    def test_phase_a_freezes_non_ceiling_cases_and_owner_gate(self):
        result = phase_a()
        self.assertEqual(result["status"], "AWAITING_OWNER_ACTIVATION")
        self.assertTrue(result["a0_has_headroom"])
        self.assertEqual(result["development_case_count"], 2)
        self.assertEqual(result["sealed_case_count"], 4)
        self.assertEqual(result["manifest"]["model_policy"]["model"], "gpt-6-luna")
        self.assertFalse(result["manifest"]["model_policy"]["store"])
        self.assertLess(result["activation_request"]["maximum_estimated_model_cost_usd"], 1.0)
        self.assertEqual(result["activation_request"]["hard_total_external_spend_cap_usd"], 25.0)
        self.assertTrue(result["identity_preflight"]["passes"])

    def test_live_metadata_identity_is_canonicalized_only_at_blinded_scoring(self):
        case = next(item for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl") if item["case_id"] == "S-ACTIVE-TRANSFER")
        candidate_id = "OA-W-LIVE-TRANSFER"
        output = portfolio(case["case_id"], candidate_id)
        candidate = {
            "source_candidate_id": candidate_id,
            "deduplication_key": "doi:10.24191/scl.v20i2.10259",
            "locator": "https://api.openalex.org/works/W-LIVE-TRANSFER",
            "content_locator": "https://journal.uitm.edu.my/index.php/ScL/article/view/10259",
            "title": "Self-Healing Effects of Silica Fume and Quicklime on Microcracks in Cement-Based Materials",
        }
        score = score_portfolio(
            case,
            output,
            candidate_records={candidate_id: candidate},
            identity_map=source_identity_map(),
        )
        self.assertGreaterEqual(score["score"], 5)
        self.assertEqual(score["invalid_source_candidate_ids"], [])
        self.assertEqual(score["cited_source_candidate_ids"], ["SRC-S30-QUICKLIME"])
        self.assertEqual(score["raw_cited_source_candidate_ids"], [candidate_id])

    def test_identity_map_rejects_missing_expected_entry(self):
        cases = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
        sources = load_jsonl(ROOT / "fixtures/investigation/recorded-sources.jsonl")
        identities = source_identity_map()
        del identities["entries"]["SRC-S16-SIM"]
        with self.assertRaisesRegex(ValueError, "missing expected IDs"):
            validate_source_identity_map(identities, recorded_sources=sources, cases=cases)

    def test_hidden_rubric_and_information_need_are_not_sent(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        packet = public_case(case)
        self.assertNotIn("rubric", packet)
        self.assertNotIn("expected_source_ids", packet)
        self.assertNotIn("hidden_information_need", packet)

    def test_arm_budgets_are_equal_and_focus_is_deterministic_not_vote_based(self):
        result = phase_a()
        self.assertEqual(result["arm_budget_equality"], result["manifest"]["limits_per_treatment_case"])
        stats = [
            {"branch_id": "evidence_skeptic", "expected_decision_change": 3, "unresolved_uncertainty": 2, "provenance_risk": 2, "unique_source_yield": 1, "duplicate_work": 0, "feasible": True},
            {"branch_id": "mechanism_transfer", "expected_decision_change": 1, "unresolved_uncertainty": 1, "provenance_risk": 0, "unique_source_yield": 2, "duplicate_work": 0, "feasible": True},
            {"branch_id": "experiment_simulation", "expected_decision_change": 0, "unresolved_uncertainty": 1, "provenance_risk": 0, "unique_source_yield": 0, "duplicate_work": 1, "feasible": True},
        ]
        first = allocate_focus(stats, 6)
        second = allocate_focus(list(reversed(stats)), 6)
        self.assertEqual(first, second)
        self.assertEqual(first["ranked_branches"][0], "evidence_skeptic")
        self.assertIn("votes are not an input", first["rationale"])

    def test_round_one_is_private_until_every_branch_commits(self):
        workspace = PrivateBranchWorkspace()
        workspace.submit(branch_report(BRANCHES[0]))
        with self.assertRaises(PolicyBlocked):
            workspace.read_shared()
        with self.assertRaises(PolicyBlocked):
            workspace.share()
        for branch in BRANCHES[1:]:
            workspace.submit(branch_report(branch))
        shared = workspace.share()
        self.assertEqual({item["branch_id"] for item in shared}, set(BRANCHES))

    def test_state_machine_rejects_illegal_and_terminal_transitions(self):
        machine = RunStateMachine()
        with self.assertRaises(PolicyBlocked):
            machine.transition("round_1")
        for state in ["policy_loaded", "context_frozen", "planning", "round_1", "sharing", "focus_allocated", "round_2", "adjudicating", "scored", "completed"]:
            machine.transition(state)
        with self.assertRaises(PolicyBlocked):
            machine.transition("failed")

    def test_checkpoint_replays_equal_action_and_rejects_stale_or_conflicting(self):
        action = {"id": "A1", "value": 1}
        checkpoint = {"manifest_sha256": "sha256:one", "actions": {}, "state": "round_1"}
        self.assertFalse(record_checkpoint_action(checkpoint, action_id="A1", action=action)["replayed"])
        self.assertTrue(record_checkpoint_action(checkpoint, action_id="A1", action=action)["replayed"])
        with self.assertRaises(PolicyBlocked):
            record_checkpoint_action(checkpoint, action_id="A1", action={"id": "A1", "value": 2})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            path.write_text('{"manifest_sha256":"sha256:old","actions":{},"state":"created"}')
            with self.assertRaises(StaleContext):
                load_checkpoint(path, "sha256:new")

    def test_orchestrator_records_typed_action_and_deduplicates_replay(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        budget = InvestigationBudget()
        adapter = RecordedRetrievalAdapter(
            source_path=ROOT / "fixtures/investigation/recorded-sources.jsonl",
            policy=source_policy(),
            budget=budget,
            source_schema=schema("source-candidate.schema.json"),
        )
        orchestrator = InvestigationOrchestrator(
            case=case,
            arm="A2",
            adapter=adapter,
            budget=budget,
            run_id="fixture-run",
        )
        first = orchestrator.search(
            branch_id="evidence_skeptic",
            query="quicklime self-healing bridge deck thesis",
            rationale="check lineage",
        )
        second = orchestrator.search(
            branch_id="mechanism_transfer",
            query=" QUICKLIME self-healing bridge deck thesis ",
            rationale="duplicate query should replay",
        )
        self.assertNotEqual(first["action"]["action_id"], second["action"]["action_id"])
        self.assertEqual(first["action"]["replay_key"], second["action"]["replay_key"])
        self.assertEqual(second["action"]["policy_status"], "REPLAYED")
        self.assertEqual(len(orchestrator.actions), 2)
        self.assertEqual(budget.usage.queries, 1)

    def test_scorer_records_hits_and_rejects_proven_fabrication_and_authority(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-TRANSFER"
        )
        score = score_portfolio(case, portfolio())
        self.assertGreaterEqual(score["score"], 5)
        self.assertEqual(score["provenance_completeness"], 1.0)
        bad = portfolio(source_id="FABRICATED")
        bad["authority_note"] = "Approved for execution."
        bad_score = score_portfolio(
            case,
            bad,
            attribution_audit={
                "FABRICATED": {
                    "status": "FABRICATION_CONFIRMED",
                    "proof": {
                        "method": "LOCATOR_RESOLVES_TO_DIFFERENT_WORK",
                        "evidence_locators": ["https://doi.org/10.0000/observed-record"],
                        "claimed_identity": "claimed Roman-concrete record",
                        "observed_identity": "unrelated battery paper",
                    },
                }
            },
        )
        self.assertIn("FABRICATED", bad_score["invalid_source_candidate_ids"])
        self.assertGreaterEqual(len(bad_score["critical_failures"]), 2)

    def test_scientific_contradiction_is_preserved_not_treated_as_fabrication(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-TRANSFER"
        )
        output = portfolio(source_id="SRC-S30-QUICKLIME")
        score = score_portfolio(
            case,
            output,
            identity_map=source_identity_map(),
            attribution_audit={"SRC-S30-QUICKLIME": "CONTRADICTS_INCUMBENT"},
        )
        self.assertEqual(score["critical_failures"], [])
        self.assertEqual(score["invalid_source_candidate_ids"], [])
        self.assertEqual(score["contradiction_source_candidate_ids"], ["SRC-S30-QUICKLIME"])
        self.assertEqual(score["identity_statuses"]["SRC-S30-QUICKLIME"], "CANONICAL")

    def test_unproven_fabrication_label_stays_in_provenance_review(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-TRANSFER"
        )
        score = score_portfolio(
            case,
            portfolio(source_id="UNPROVEN"),
            attribution_audit={"UNPROVEN": "FABRICATION_CONFIRMED"},
        )
        self.assertEqual(score["critical_failures"], [])
        self.assertEqual(score["invalid_source_candidate_ids"], [])
        self.assertEqual(score["provenance_review_source_candidate_ids"], ["UNPROVEN"])

    def test_open_world_candidate_is_retained_without_evidence_credit(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-TRANSFER"
        )
        candidate = {
            "source_candidate_id": "OA-UNRESOLVED",
            "title": "A newly discovered transfer record",
            "locator": "https://example.org/unresolved-record",
            "content_locator": None,
            "deduplication_key": "provider:unresolved",
        }
        pending = portfolio(source_id="OA-UNRESOLVED")
        score = score_portfolio(
            case,
            pending,
            candidate_records={"OA-UNRESOLVED": candidate},
            identity_map=source_identity_map(),
        )
        self.assertEqual(score["critical_failures"], [])
        self.assertEqual(score["identity_statuses"]["OA-UNRESOLVED"], "IDENTITY_UNRESOLVED")
        self.assertIn("OA-UNRESOLVED", score["unresolved_source_candidate_ids"])
        self.assertEqual(score["evidence_score"], 0)
        self.assertGreater(score["discovery_score"], 0)
        self.assertGreater(score["hypothesis_score"], 0)

    def test_unattributed_citation_is_pending_not_fabricated(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-TRANSFER"
        )
        pending = portfolio(source_id="NEW-CITATION")
        score = score_portfolio(case, pending, identity_map=source_identity_map())
        self.assertEqual(score["identity_statuses"]["NEW-CITATION"], "UNATTRIBUTED")
        self.assertIn("NEW-CITATION", score["unattributed_source_candidate_ids"])
        self.assertEqual(score["invalid_source_candidate_ids"], [])
        self.assertEqual(score["critical_failures"], [])

    def test_negated_authority_language_is_flagged_not_invalidated(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-TRANSFER"
        )
        pending = portfolio()
        pending["authority_note"] = "This is not validated performance and does not authorize laboratory work."
        score = score_portfolio(case, pending)
        self.assertEqual(score["critical_failures"], [])
        self.assertTrue(any(flag["negated"] for flag in score["authority_flags"]))

    def test_requirement_language_is_flagged_not_invalidated(self):
        case = next(
            item
            for item in load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")
            if item["case_id"] == "S-ACTIVE-SIM"
        )
        pending = portfolio(case["case_id"], "SRC-S16-SIM")
        pending["hypotheses"][0]["comparator"] = (
            "The eligibility criteria in the case question: an accessible paper must supply "
            "a validated performance simulator."
        )
        score = score_portfolio(case, pending, identity_map=source_identity_map())
        self.assertEqual(score["critical_failures"], [])
        self.assertTrue(any(flag["contextual_reference"] for flag in score["authority_flags"]))

    def test_live_runner_refuses_without_activation_and_replays_checkpoint_without_calls(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "checkpoint.json"

            def make_runner(provider):
                budget = InvestigationBudget()
                return ActiveInvestigationRunner(
                    case=case,
                    arm="A1",
                    adapter=RecordedRetrievalAdapter(
                        source_path=ROOT / "fixtures/investigation/recorded-sources.jsonl",
                        policy=source_policy(),
                        budget=budget,
                        source_schema=schema("source-candidate.schema.json"),
                    ),
                    provider=provider,
                    budget=budget,
                    checkpoint_path=checkpoint,
                    manifest_sha256=phase_a()["manifest_sha256"],
                    run_id="fixture-live-a1",
                )

            first_provider = FakeProvider(case)
            with self.assertRaises(OwnerActivationRequired):
                make_runner(first_provider).run(owner_activated=False)
            result = make_runner(first_provider).run(owner_activated=True)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(len(first_provider.calls), 2)
            replay_provider = FakeProvider(case)
            replay = make_runner(replay_provider).run(owner_activated=True)
            self.assertEqual(replay["status"], "COMPLETED")
            self.assertEqual(replay_provider.calls, [])

    def test_phase_b_entrypoint_refuses_before_constructing_provider_or_network(self):
        with self.assertRaises(OwnerActivationRequired):
            run_phase_b(owner_activated=False)

    def test_a2_round_one_plans_cannot_read_other_branch_candidates(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        with tempfile.TemporaryDirectory() as directory:
            budget = InvestigationBudget()
            provider = PrivacyProvider(case)
            runner = ActiveInvestigationRunner(
                case=case,
                arm="A2",
                adapter=RecordedRetrievalAdapter(source_path=ROOT / "fixtures/investigation/recorded-sources.jsonl", policy=source_policy(), budget=budget, source_schema=schema("source-candidate.schema.json")),
                provider=provider,
                budget=budget,
                checkpoint_path=Path(directory) / "a2.json",
                manifest_sha256=phase_a()["manifest_sha256"],
                run_id="fixture-live-a2",
            )
            result = runner.run(owner_activated=True)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(len(provider.branch_plan_packets), 3)
            self.assertTrue(all(not item["available_source_candidates"] for item in provider.branch_plan_packets))

    def test_a2m_live_orchestration_uses_mechanism_proponents_and_structural_auditors(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        with tempfile.TemporaryDirectory() as directory:
            budget = InvestigationBudget()
            provider = MechanismProvider(case)
            runner = ActiveInvestigationRunner(
                case=case,
                arm="A2-M",
                adapter=RecordedRetrievalAdapter(source_path=ROOT / "fixtures/investigation/recorded-sources.jsonl", policy=source_policy(), budget=budget, source_schema=schema("source-candidate.schema.json")),
                provider=provider,
                budget=budget,
                checkpoint_path=Path(directory) / "a2m.json",
                manifest_sha256=phase_a()["manifest_sha256"],
                run_id="fixture-live-a2m",
            )
            result = runner.run(owner_activated=True)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(len(provider.calls), 13)
            self.assertEqual(result["arm"], "A2-M")

    def test_undeclared_simulation_becomes_non_scoring_unavailable_trace(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        with tempfile.TemporaryDirectory() as directory:
            budget = InvestigationBudget()
            runner = ActiveInvestigationRunner(
                case=case,
                arm="A1",
                adapter=RecordedRetrievalAdapter(source_path=ROOT / "fixtures/investigation/recorded-sources.jsonl", policy=source_policy(), budget=budget, source_schema=schema("source-candidate.schema.json")),
                provider=FakeProvider(case), budget=budget,
                checkpoint_path=Path(directory) / "simulation.json", manifest_sha256=phase_a()["manifest_sha256"], run_id="fixture-simulation",
            )
            runner._simulate(branch_id="single_investigator", request={"adapter_id": "roman-concrete", "inputs": {}, "rationale": "check availability"})
            self.assertEqual(runner.simulation_traces[0]["status"], "SIMULATOR_UNAVAILABLE")
            self.assertFalse(runner.simulation_traces[0]["score_eligible"])
            self.assertEqual(runner.actions[0]["policy_status"], "SIMULATOR_UNAVAILABLE")

    def test_paper_card_requires_real_page_locator_and_hash(self):
        document = {
            "content_hash": "sha256:document",
            "pages": [{"locator": "https://public.example/paper.pdf#page=1", "text_hash": "sha256:page"}],
        }
        card = {
            "schema_version": "1.0", "card_id": "CARD-1", "source_candidate_id": "SRC-USU-THESIS",
            "document_hash": "sha256:document", "parser": "fixture", "extraction_status": "EXTRACTED", "page_count": 1,
            "facts": [{"field": "endpoint", "value": "reported falling-head water-flow endpoint", "reporting_status": "REPORTED", "support_type": "DIRECT", "page_locator": "https://public.example/paper.pdf#page=1", "page_text_hash": "sha256:page", "confidence": "HIGH"}],
            "unresolved": [], "authority_note": "Derived extraction for review; no evidence promotion, performance claim, or laboratory authority.",
        }
        validate_paper_evidence_card(card, document)
        card["facts"][0]["page_text_hash"] = "sha256:wrong"
        with self.assertRaises(PolicyBlocked):
            validate_paper_evidence_card(card, document)

    def test_permitted_document_maps_to_card_while_raw_text_stays_out_of_checkpoint(self):
        case = load_jsonl(ROOT / "fixtures/investigation/sealed.jsonl")[0]
        document = {
            "locator": "https://digitalcommons.usu.edu/paper.pdf", "content_type": "application/pdf", "payload_bytes": 100,
            "content_hash": "sha256:document", "parser": "fixture", "page_count": 1, "extraction_status": "EXTRACTED",
            "pages": [{"page_number": 1, "locator": "https://digitalcommons.usu.edu/paper.pdf#page=1", "text": "Quicklime water-flow result", "text_hash": "sha256:" + hashlib.sha256(b"Quicklime water-flow result").hexdigest(), "text_characters": 27, "status": "EXTRACTED"}],
        }
        class FetchAdapter:
            def fetch_public_text(self, locator):
                return document
        with tempfile.TemporaryDirectory() as directory:
            budget = InvestigationBudget()
            checkpoint = Path(directory) / "checkpoint.json"
            runner = ActiveInvestigationRunner(
                case=case, arm="A1", adapter=FetchAdapter(), provider=PaperCardProvider(case), budget=budget,
                checkpoint_path=checkpoint, manifest_sha256=phase_a()["manifest_sha256"], run_id="fixture-paper", document_cache_dir=Path(directory) / "raw",
            )
            runner.candidates["SRC-USU-THESIS"] = {
                "schema_version": "1.0", "source_candidate_id": "SRC-USU-THESIS", "problem_id": "roman-hot-mix", "problem_version": "1.0",
                "title": "Utah thesis", "locator": "https://api.openalex.org/works/W1", "content_locator": document["locator"], "discovery_query": "fixture", "host": "api.openalex.org",
                "access_class": "METADATA_ONLY", "rights_state": "METADATA_ONLY", "content_hash": None, "deduplication_key": "fixture", "support_region": "fixture", "contradiction_ids": [], "status": "METADATA_SCREENED",
            }
            runner._execute_requested_tools("single_investigator", {"requested_fetch_locators": [document["locator"]], "simulation_requests": []})
            self.assertEqual(runner.candidates["SRC-USU-THESIS"]["status"], "EVIDENCE_PENDING")
            self.assertEqual(len(runner.paper_cards), 1)
            checkpoint_text = checkpoint.read_text()
            self.assertNotIn("Quicklime water-flow result", checkpoint_text)
            self.assertTrue((Path(directory) / "raw" / "document.json").exists())


if __name__ == "__main__":
    unittest.main()
