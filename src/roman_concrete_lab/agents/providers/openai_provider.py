"""Least-privilege OpenAI Responses adapter for the G10B signal pilot."""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from jsonschema import validate
from openai import OpenAI


class ProviderUnavailable(RuntimeError):
    """The configured provider cannot be called."""


class BudgetExceeded(RuntimeError):
    """The next call would exceed the frozen cost cap."""


def _response_debug(response: Any, raw_output: str) -> str:
    """Return bounded provider diagnostics without logging credentials or packets."""
    status = getattr(response, "status", None)
    incomplete = getattr(response, "incomplete_details", None)
    reason = getattr(incomplete, "reason", None) if incomplete is not None else None
    output_tokens = getattr(getattr(response, "usage", None), "output_tokens", None)
    details = [f"status={status!r}", f"incomplete_reason={reason!r}", f"output_tokens={output_tokens!r}"]
    details.append(f"output_chars={len(raw_output)}")
    return ", ".join(details)


@dataclass(frozen=True)
class Pricing:
    input_per_million_usd: float = 0.10
    cached_input_per_million_usd: float = 0.01
    output_per_million_usd: float = 0.50


class BudgetLedger:
    def __init__(self, cap_usd: float = 25.0, spent_usd: float = 0.0) -> None:
        self.cap_usd = cap_usd
        self.spent_usd = spent_usd

    @staticmethod
    def conservative_input_tokens(text: str) -> int:
        return math.ceil(len(text) / 3)

    def preflight(self, text: str, max_output_tokens: int, pricing: Pricing) -> float:
        input_tokens = self.conservative_input_tokens(text)
        maximum = (
            input_tokens * pricing.input_per_million_usd
            + max_output_tokens * pricing.output_per_million_usd
        ) / 1_000_000
        if self.spent_usd + maximum > self.cap_usd:
            raise BudgetExceeded(
                f"next call maximum ${maximum:.6f} would exceed ${self.cap_usd:.2f} cap"
            )
        return maximum

    def record(self, actual_cost_usd: float) -> None:
        self.spent_usd += actual_cost_usd


class OpenAIProvider:
    model = "gpt-6-luna"
    reasoning_effort = "low"

    def __init__(
        self,
        *,
        root: Path,
        schema: dict[str, Any],
        budget: BudgetLedger,
        pricing: Pricing | None = None,
        client: OpenAI | None = None,
        model: str | None = None,
        reasoning_effort: str | None = None,
        format_name: str = "g10b_output",
    ) -> None:
        load_dotenv(root / ".env", override=False)
        key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_AI_API_KEY")
        if client is None and not key:
            raise ProviderUnavailable(
                f"OPENAI_API_KEY (or local OPEN_AI_API_KEY alias) is not available in {root / '.env'} or the environment"
            )
        self.client = client or OpenAI(api_key=key)
        self.schema = schema
        self.budget = budget
        self.pricing = pricing or Pricing()
        self.model = model or type(self).model
        self.reasoning_effort = reasoning_effort or type(self).reasoning_effort
        self.format_name = format_name

    def call(
        self,
        *,
        call_id: str,
        instructions: str,
        packet: dict[str, Any],
        max_output_tokens: int,
        schema: dict[str, Any] | None = None,
        format_name: str | None = None,
    ) -> dict[str, Any]:
        active_schema = schema or self.schema
        active_format_name = format_name or self.format_name
        input_text = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        request_text = instructions + "\n" + input_text
        maximum_cost = self.budget.preflight(request_text, max_output_tokens, self.pricing)
        started = time.monotonic()
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=input_text,
                reasoning={"effort": self.reasoning_effort},
                max_output_tokens=max_output_tokens,
                store=False,
                service_tier="default",
                text={
                    "format": {
                        "type": "json_schema",
                        "name": active_format_name,
                        "schema": active_schema,
                        "strict": True,
                    },
                    "verbosity": "low",
                },
            )
        except Exception as exc:  # provider SDK exposes several transport/status subclasses
            raise ProviderUnavailable(f"OpenAI call {call_id} failed: {type(exc).__name__}: {exc}") from exc
        elapsed = time.monotonic() - started
        raw_output = str(getattr(response, "output_text", ""))
        try:
            output = json.loads(raw_output)
            validate(output, active_schema)
        except Exception as exc:
            debug = _response_debug(response, raw_output)
            raise ValueError(f"MALFORMED_OUTPUT for {call_id}: {exc} ({debug})") from exc
        usage = response.usage
        input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
        details = getattr(usage, "input_tokens_details", None)
        cached_tokens = int(getattr(details, "cached_tokens", 0) or 0)
        uncached_tokens = max(0, input_tokens - cached_tokens)
        actual_cost = (
            uncached_tokens * self.pricing.input_per_million_usd
            + cached_tokens * self.pricing.cached_input_per_million_usd
            + output_tokens * self.pricing.output_per_million_usd
        ) / 1_000_000
        self.budget.record(actual_cost)
        return {
            "call_id": call_id,
            "provider": "openai",
            "model": str(response.model),
            "reasoning_effort": self.reasoning_effort,
            "store": False,
            "tools": [],
            "response_id_sha256": "sha256:" + hashlib.sha256(str(response.id).encode()).hexdigest(),
            "output": output,
            "usage": {
                "input_tokens": input_tokens,
                "cached_input_tokens": cached_tokens,
                "output_tokens": output_tokens,
            },
            "estimated_maximum_cost_usd": round(maximum_cost, 8),
            "estimated_actual_cost_usd": round(actual_cost, 8),
            "latency_seconds": round(elapsed, 4),
        }
