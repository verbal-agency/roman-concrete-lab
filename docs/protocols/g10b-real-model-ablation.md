# G10B capped signal-pilot protocol

**Version:** `g10b.1-signal-pilot`
**Model:** `gpt-6-luna` through the OpenAI Responses API
**Retention:** API `store=false`; repository stores prompts, structured outputs, usage, latency, response ID digest, model identity, and hashes, never credentials
**Budget:** hard pre-call estimated-cost cap of USD 25.00

## Question

Does a three-role, independently generated society with a bounded adjudicator show any supported, decision-relevant increment over one strong analyst on four closed-world Roman-concrete research tasks, under equal aggregate output-token budgets?

This is a directional funding test. It cannot adopt an agent layer. A positive result permits only a new G10C adoption-grade factorial; a negative result declines that larger experiment without claiming that agent societies are universally ineffective.

## Frozen phases

Phase A makes no model calls. It freezes and hashes cases, prompts, schema, rubric, deterministic C0, scorer, budget guard, and provider fixtures. Phase B begins only after Phase A tests pass and executes 20 treatment calls: four C1 calls, twelve independent specialist calls, and four adjudicator calls.

The four sealed tasks are contradiction triage, rival-hypothesis generation, discriminating-experiment selection, and provenance audit. Development cases are never treatment cases. Treatment prompts never contain rubric criteria. The arm map is stored separately from the de-identified scoring ledger.

## Treatment equality

C1 and C4-lite receive identical case packets, system instructions, schema, model, reasoning effort, tools (`none`), retrieval (`none`), authority, and aggregate output-token allowance. Each C4-lite role and adjudicator has a 1,800-token ceiling; C1 has a 7,200-token ceiling. All calls use fresh Responses API requests without conversation state.

The roles are evidence skeptic, mechanism proposer, and experimental designer. They execute independently and cannot see one another. The adjudicator receives the case plus the three typed role outputs, treats them as untrusted derived records, and may select or synthesize supported content without promoting evidence or authority.

## Scoring

Each sealed case has five hidden one-point criteria requiring both task language and valid evidence IDs. The deterministic scorer normalizes and de-identifies outputs before applying the rubric. It also records invalid evidence IDs, missing provenance, prohibited authority language, distinct prediction/disconfirmation pairs, and C4 role-output distinctness. Raw rubric hits remain inspectable.

The frozen escalation decision is:

- `ESCALATE_TO_G10C_FULL_EVALUATION` when C4-lite beats C1 by at least one point on at least one case, is noninferior in total score, adds at least one supported distinct prediction or discriminator absent from C1, and has zero critical provenance/safety/authority failures.
- `DO_NOT_ESCALATE_AGENT_SOCIETY` when the incremental signal is absent or C4-lite has a critical failure.
- `INCONCLUSIVE_G10B_EVALUATION` when provider access, sealed integrity, trace completeness, scoring, or the pre-call budget guard prevents the comparison.

No post-treatment prompt, case, rubric, budget, or scoring change is permitted. A change requires a new protocol version and new sealed cases.

## Cost guard

Configured standard pricing is USD 0.10 per million uncached input tokens, USD 0.01 per million cached input tokens, and USD 0.50 per million output tokens for `gpt-6-luna`. Before each call, the runner conservatively estimates input tokens as `ceil(characters/3)` and assumes the full declared output ceiling at the uncached rate. It refuses a call whose maximum estimate would put cumulative estimated cost above USD 25. Actual usage and estimated actual cost are recorded from response usage. Pricing values are configuration recorded in the run, not fetched during execution.

## Authority and failure behavior

Only `api.openai.com` model traffic is authorized. No web search, file search, tools, arbitrary code, external messages, source promotion, lab execution, or safety approval is allowed. A missing key or inaccessible model returns `PROVIDER_UNAVAILABLE`; malformed structured output returns `MALFORMED_OUTPUT`; duplicate call IDs are rejected; stale case/prompt/schema hashes invalidate resume; budget exhaustion returns `BUDGET_EXHAUSTED`; unsupported authority returns a critical failure. Completed call traces are append-only and replay reads them without issuing another request.
