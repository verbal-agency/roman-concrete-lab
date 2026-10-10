"""Expose the frozen G07E focus/promotion policy for release manifests."""

from __future__ import annotations

from tools.tournament.policy import LEGAL_TRANSITIONS, POLICY_HASH, POLICY_VERSION


def policy_snapshot() -> dict[str, object]:
    return {
        "policy_version": POLICY_VERSION,
        "policy_hash": POLICY_HASH,
        "legal_transitions": {key: sorted(value) for key, value in sorted(LEGAL_TRANSITIONS.items())},
        "focus_budget": "declared local attention budget; no scope widening",
        "promotion_authority": "deterministic policy plus later qualified reviewer; no lab authority",
    }
