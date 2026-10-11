# G10 agent-ablation report

**Status:** complete
**Protocol:** `g10.1-closed-world-ablation`
**Provider:** `offline-role-simulator` (`fixture-agent-v1`)
**Evaluation:** 8 sealed cases × 3 seeds = 24 society runs

## Recorded result and interpretation amendment

**Frozen run-level result:** `REJECT_AGENT_SOCIETY` for the tested closed-world fixture tasks.

**Amended interpretation:** `REJECT_CURRENT_OFFLINE_SOCIETY_PROTOTYPE` — **not** a rejection of agent societies generally.

The frozen decision remains in `run.json` because the run met its original threshold rule. It cannot support the broader conclusion, however: the provider was a deterministic role simulator rather than a language model, society status was inherited from the deterministic control, the control had no accuracy headroom, and the five roles emitted near-identical proposals. The run therefore establishes the safety, memory, replay, and focus contracts, while providing no valid estimate of whether a real-model society improves scientific work. G10B is required for that question.

The permitted development iteration changed focus ordering from round-robin to provenance-first for contradiction/unsupported-risk cases. It produced the intended review-first trace on the development fixture without changing any sealed case, rubric, budget, or control policy. On sealed cases, society task accuracy tied the deterministic control at 1.0, critical failures were zero, unsupported-claim rate stayed within threshold, and society cost averaged 2.5 units versus 1.0 for control. Adoption required at least a 0.05 accuracy improvement and no more than 2× control cost.

This rejects only the tested offline implementation as an adoption candidate. The experiment demonstrates that the memory, role, focus, and review contracts can be evaluated without granting agents scientific or physical authority.

## Acceptance-criterion map

| Criterion | Result | Evidence |
|---|---|---|
| 1. Identical controls/capabilities/budgets | **PASS** | `artifacts/goals/G10/run.json`; same eight cases, G07E policy, role/tool boundary, and declared budget |
| 2. Sealed cases before tuning | **PASS** | `fixtures/agents/cases.jsonl`; one development-only iteration is separately recorded and sealed cases are marked untouched |
| 3. Repeated runs without contamination | **PASS** | seeds `11`, `23`, `47`; 24 runs create fresh memory/state, replay byte-stably, and all cases are outcome/metric-stable across seeds |
| 4. Fabricated measurement/source/approval failure | **PASS** | proposals require fixture evidence IDs and locators; no role can write evidence or approval |
| 5. Metrics and uncertainty | **PASS** | per-run accuracy, unsupported claims, provenance, constraints, diversity, cost, and latency; case summaries include per-metric min/max ranges |
| 6. State/replay/duplicate/malformed/partial/budget behavior | **PASS** | `tests/agents/test_replay.py`; state traces and all eight sealed statuses |
| 7. Shared-memory authority | **PASS** | immutable evidence write is rejected; hypotheses are typed, source-located, and review-required |
| 8. Biased roles and disconfirming evidence | **PASS** | five named roles emit role-tagged proposals with disconfirming observations |
| 9. Focus rationale/abstention | **PASS** | development iteration records `round_robin` → `provenance_first`; malformed/unsafe/unsupported/budget cases fail closed |
| 10. Task-specific adoption status | **PASS** | exactly `REJECT_AGENT_SOCIETY` is emitted |
| 11. Frozen policy binding | **PASS** | run records G07E policy version/hash and rejects any authority expansion |

## Limitations and routed findings

- The provider is an offline role simulator, not a live LLM; no frontier-model capability claim is made.
- The society inherited control statuses and evaluated a ceilinged control, so its accuracy comparison is non-estimating. The role proposals had no meaningful semantic diversity. These are design limitations, not evidence against real-model orchestration.
- G10R open-world retrieval is not activated and remains a separate optional goal requiring an explicit source policy.
- G10B is the successor evaluation: real-model, non-ceiling, blind-scored factorial ablation before any agent-society adoption claim.
- The authoritative workflow remains the G09/G07E non-agent release.
- A future agent evaluation would require a new protocol and sealed case set; this result cannot be reused as evidence for a different task.
