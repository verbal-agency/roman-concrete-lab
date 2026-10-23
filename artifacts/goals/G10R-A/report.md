# G10R-A offline acquisition redesign report

## Outcome

`ACQUISITION_DESIGN_READY`

The acquisition redesign removes the forced-empty support-tool instruction from
the live A2-M path and adds request-lifecycle instrumentation. The offline
replay then exercises the full support loop: competing viewpoints receive
typed retrieval, extraction, identity, contradiction, and experiment-design
tasks; a fetch-positive fixture produces a page-aware card; a blocked source,
malformed document, omitted request, and exhausted budget remain distinct
diagnostics; and the result survives focus, critique, adjudication, and
attribution serialization.

This is a plumbing/design readiness result. It is not evidence that the
agent society outperforms A1, and it does not authorize a paid run or promote
any scientific evidence.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| 1. Fetch-positive card and negative diagnostics | **PASS** | `artifacts/goals/G10R-A/replay.json` (`paper_evidence_cards`, `evidence_card_joins`, blocked/malformed flags) |
| 2. Request lifecycle is explicit | **PASS** | Five deterministic statuses in `offline_run.score.request_lifecycle`; live runner persists `tool_request_events` |
| 3. Typed support work | **PASS** | 5 task types across all active viewpoints; support reports include `SUPPORTS`, `WEAKENS`, `NON_DISCRIMINATING`, and `ABSTAINED` |
| 4. Candidate observations/variants | **PASS** | Evidence-bus checkpoint and `candidate_variant_count: 1`; no direct-evidence credit |
| 5. Focus before adjudication | **PASS** | `offline_run.focus.status: ALLOCATED`; deterministic information/uncertainty/provenance rationale |
| 6. Null, rival, open slot, dissent | **PASS** | Viewpoint checkpoint, portfolio, preserved dissent, and unresolved dispute/critique |
| 7. Equal-budget ledger | **PASS** | `score.equal_budget_limits` plus attributable acquisition, card yield, weakening coverage, hypothesis yield, and overhead fields |
| 8. Replay and authority boundary | **PASS** | Byte-stable replay, checkpoint-resume and duplicate-action checks; zero external calls and no promotion |
| 9. Single handoff | **PASS** | `ACQUISITION_DESIGN_READY` in `phase-a.json` and `replay.json` |

## Verification

```text
python3 -m tools.evaluation.acquisition_redesign_replay --output artifacts/goals/G10R-A/replay.json
python3 -m pytest -q tests/agents/test_acquisition_redesign_replay.py tests/agents/test_active_investigation.py tests/agents/test_society_plumbing_replay.py
python3 -m pytest -q
git diff --check
```

Result: focused tests passed (26), full suite passed (126), and the replay
reported `external_calls: false` and `replay_stable: true`.

## Handoff

The next eligible step is a fresh Phase-A manifest freeze and separately
activated live evaluation of the redesigned acquisition path. G10R-A itself
does not authorize model calls, network retrieval, subscription access, a
spend increase, laboratory work, or scientific evidence promotion.
