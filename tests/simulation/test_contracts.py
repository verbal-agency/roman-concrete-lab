import unittest

from src.roman_concrete_lab.agents.investigation import schema
from src.roman_concrete_lab.retrieval import InvestigationBudget
from src.roman_concrete_lab.simulation.contracts import (
    AdapterDeclaration,
    SimulationPolicyBlocked,
    SimulationRegistry,
    synthetic_echo,
)


class SimulationContractTests(unittest.TestCase):
    def test_missing_or_unvalidated_adapter_is_unavailable_without_debit(self):
        budget = InvestigationBudget()
        registry = SimulationRegistry(
            budget=budget, trace_schema=schema("simulation-trace.schema.json")
        )
        missing = registry.run("roman-performance", {"mix": "unknown"})
        self.assertEqual(missing["status"], "SIMULATOR_UNAVAILABLE")
        self.assertFalse(missing["score_eligible"])
        self.assertEqual(budget.usage.simulation_calls, 0)
        registry.register(
            AdapterDeclaration(
                adapter_id="unvalidated",
                version="1",
                validation_status="UNVALIDATED",
                support_region="unknown",
                prohibited_interpretations=("No performance inference.",),
            )
        )
        self.assertEqual(
            registry.run("unvalidated", {})["status"], "SIMULATOR_UNAVAILABLE"
        )
        self.assertEqual(budget.usage.simulation_calls, 0)

    def test_synthetic_diagnostic_is_model_assertion_and_not_score_eligible(self):
        budget = InvestigationBudget()
        registry = SimulationRegistry(
            budget=budget, trace_schema=schema("simulation-trace.schema.json")
        )
        registry.register(
            AdapterDeclaration(
                adapter_id="synthetic-echo",
                version="1",
                validation_status="SYNTHETIC_DIAGNOSTIC",
                support_region="software plumbing only",
                prohibited_interpretations=("Not material performance.",),
                runner=synthetic_echo,
            )
        )
        trace = registry.run("synthetic-echo", {"value": 1}, seed=7)
        self.assertEqual(trace["assertion_type"], "MODEL_ASSERTION")
        self.assertFalse(trace["score_eligible"])
        self.assertEqual(budget.usage.simulation_calls, 1)

    def test_duplicate_adapter_registration_fails(self):
        registry = SimulationRegistry(
            budget=InvestigationBudget(),
            trace_schema=schema("simulation-trace.schema.json"),
        )
        declaration = AdapterDeclaration(
            adapter_id="synthetic",
            version="1",
            validation_status="SYNTHETIC_DIAGNOSTIC",
            support_region="test",
            prohibited_interpretations=("Not evidence.",),
            runner=synthetic_echo,
        )
        registry.register(declaration)
        with self.assertRaises(SimulationPolicyBlocked):
            registry.register(declaration)


if __name__ == "__main__":
    unittest.main()
