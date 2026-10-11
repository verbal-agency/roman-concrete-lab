# Active-investigation society pilot protocol

**Protocol version:** `g10r.2-active-investigation-pilot`

G10R compares one tool-using investigator (A1) with three protected investigation branches plus deterministic focus and bounded adjudication (A2). A0 is a recorded-fixture control for policy, replay, and scoring plumbing. The comparison asks whether society structure improves information acquisition under equal aggregate resources; it does not retest closed-world discourse quality.

## Frozen treatments

A1 and A2 receive identical base packets, problem context, model (`gpt-6-luna`), reasoning policy (`low`), source policy, retrieval/simulation adapters, schemas, stopping conditions, and aggregate per-case budgets: 12 queries, two rounds, 24 retained candidates, 5 MB permitted payload, 4 declared simulation calls, 80,000 input tokens, and 7,200 output tokens. Phase B has a proposed $25 total external-spend cap and cannot start until the owner reviews the Phase A manifest and activates the frozen network/model policy.

A2 branches are evidence skeptic/contradiction hunter, mechanism/transfer explorer, and experiment/simulation designer. Their round-one charters are non-overlapping, their state is private until typed reports are shared, and duplicate normalized queries return one cached result. The deterministic focus allocator assigns remaining actions from unresolved uncertainty, expected decision change, provenance risk, unique source yield, duplication, feasibility, and remaining budget. It does not count votes.

## Retrieval and simulation boundary

Only exact HTTPS hosts in `fixtures/investigation/source-policy.json` are eligible. Search indexes provide metadata only. Any relevant PDF from a listed `PUBLIC` host may be fetched and parsed page by page; restricted, authenticated, or rights-unclear documents remain metadata-only. Redirects are rechecked, PDF actions/instructions are inert data, no credentials are sent, and source candidates remain `EVIDENCE_PENDING` until human adjudication. Raw permitted PDFs/page text live only in ignored local raw storage for replay. Checkpoints and reports retain hashes, page locators, parser/quality state, and compact typed evidence cards.

The mapper receives bounded page spans and must attach each extracted fact to an exact page locator and page-text hash. It records `NOT_REPORTED`, `ILLEGIBLE`, `AMBIGUOUS`, or `OCR_REQUIRED` rather than guessing. It never promotes a card to empirical evidence.

The frozen native-text parser is `pypdf==6.20.0` (`requirements-g10r.txt`). It is a parser only: it does not execute PDF actions, provide OCR, reconstruct missing tables, or infer values from figures. Those capabilities require separately declared and validated adapters.

Simulation requires a declared adapter and trace. Every output is `MODEL_ASSERTION`. Synthetic diagnostics are excluded from the live scientific score. No validated Roman-concrete adapter exists in Phase A, so the required live state is `SIMULATOR_UNAVAILABLE` unless a pre-existing validation artifact is added before the manifest is frozen; adding one afterward invalidates the run.

## Freeze, replay, and failure

Development and sealed cases, prompts, hidden rubrics, source policy, fixtures, schemas, provider/runner code, focus policy, budgets, and decision thresholds are hashed before treatment. Checkpoints bind those hashes. Completed action IDs and normalized queries replay without external calls or additional budget debits. Stale, duplicate-write, cross-problem, rights-blocked, malformed, unavailable, partial, prompt-injection, and budget paths fail closed with attributable states.

## Scoring and outcome

Treatment identity is removed before deterministic case-specific scoring. Credit requires a policy-compliant source or eligible model trace, a supported novel hypothesis/contradiction/discriminator, falsifiable prediction, useful uncertainty partition, complete provenance, and appropriate rival or negative-result retention. Source count, answer length, persona variation, and consensus earn no standalone credit.

The legal outcomes are `ESCALATE_ACTIVE_SOCIETY_EVALUATION`, `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, and `INCONCLUSIVE_ACTIVE_INVESTIGATION`. Escalation requires at least one case-level A2 gain of one point, noninferior total score, one unique valid source-backed contribution absent from A1, equal-budget compliance, and zero critical failures. It creates only a proposed G10S adoption-grade evaluation.
