"""Simulation traces that cannot be mistaken for empirical evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from jsonschema import validate

from ..retrieval import InvestigationBudget, digest


class SimulationPolicyBlocked(RuntimeError):
    """A requested adapter is unavailable or outside its declared authority."""


@dataclass(frozen=True)
class AdapterDeclaration:
    adapter_id: str
    version: str
    validation_status: str
    support_region: str
    prohibited_interpretations: tuple[str, ...]
    runner: Callable[[dict[str, Any], int | None], dict[str, Any]] | None = None

    @property
    def adapter_hash(self) -> str:
        return digest(
            {
                "adapter_id": self.adapter_id,
                "version": self.version,
                "validation_status": self.validation_status,
                "support_region": self.support_region,
                "prohibited_interpretations": self.prohibited_interpretations,
            }
        )


class SimulationRegistry:
    def __init__(self, *, budget: InvestigationBudget, trace_schema: dict[str, Any]) -> None:
        self.budget = budget
        self.trace_schema = trace_schema
        self._adapters: dict[str, AdapterDeclaration] = {}

    def register(self, declaration: AdapterDeclaration) -> None:
        if declaration.adapter_id in self._adapters:
            raise SimulationPolicyBlocked(f"duplicate simulation adapter: {declaration.adapter_id}")
        self._adapters[declaration.adapter_id] = declaration

    def run(self, adapter_id: str, inputs: dict[str, Any], *, seed: int | None = None) -> dict[str, Any]:
        declaration = self._adapters.get(adapter_id)
        if declaration is None or declaration.validation_status in {"UNAVAILABLE", "UNVALIDATED"}:
            trace = self._unavailable(adapter_id, inputs, declaration)
            validate(trace, self.trace_schema)
            return trace
        self.budget.debit(simulation_calls=1)
        outputs = declaration.runner(inputs, seed) if declaration.runner else {}
        score_eligible = declaration.validation_status == "VALIDATED"
        trace = {
            "schema_version": "1.0",
            "trace_id": digest({"adapter_id": adapter_id, "inputs": inputs, "seed": seed})[7:23],
            "adapter_id": declaration.adapter_id,
            "adapter_version": declaration.version,
            "adapter_hash": declaration.adapter_hash,
            "validation_status": declaration.validation_status,
            "support_region": declaration.support_region,
            "inputs": inputs,
            "outputs": outputs,
            "seed": seed,
            "estimated_cost_usd": 0.0,
            "assertion_type": "MODEL_ASSERTION",
            "score_eligible": score_eligible,
            "status": "COMPLETED",
            "prohibited_interpretations": list(declaration.prohibited_interpretations),
        }
        validate(trace, self.trace_schema)
        return trace

    def _unavailable(
        self,
        adapter_id: str,
        inputs: dict[str, Any],
        declaration: AdapterDeclaration | None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "trace_id": digest({"adapter_id": adapter_id, "inputs": inputs, "status": "unavailable"})[7:23],
            "adapter_id": adapter_id,
            "adapter_version": declaration.version if declaration else "none",
            "adapter_hash": declaration.adapter_hash if declaration else digest({"adapter_id": adapter_id}),
            "validation_status": declaration.validation_status if declaration else "UNAVAILABLE",
            "support_region": declaration.support_region if declaration else "none",
            "inputs": inputs,
            "outputs": {},
            "seed": None,
            "estimated_cost_usd": 0.0,
            "assertion_type": "MODEL_ASSERTION",
            "score_eligible": False,
            "status": "SIMULATOR_UNAVAILABLE",
            "prohibited_interpretations": list(
                declaration.prohibited_interpretations
                if declaration
                else ("Do not infer material performance.",)
            ),
        }


def synthetic_echo(inputs: dict[str, Any], seed: int | None) -> dict[str, Any]:
    """Plumbing-only deterministic fixture; never score eligible."""

    return {"input_digest": digest(inputs), "seed": seed}
