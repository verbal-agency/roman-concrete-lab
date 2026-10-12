# Active-investigation society pilot protocol

**Protocol version:** `g10r.4-active-investigation-pilot`

G10R compares one tool-using investigator (A1) with the mechanism-proponent and structural-auditor society (A2-M). A0 is a recorded-fixture control for policy, replay, and scoring plumbing. The comparison asks whether a two-layer society improves information acquisition under equal aggregate resources; it does not retest closed-world discourse quality.

## Frozen treatments

A1 and A2 receive identical base packets, problem context, model (`gpt-6-luna`), reasoning policy (`low`), source policy, retrieval/simulation adapters, schemas, stopping conditions, and aggregate per-case budgets: 12 queries, two rounds, 24 retained candidates, 5 MB permitted payload, 4 declared simulation calls, 80,000 input tokens, and 7,200 output tokens. Phase B has a proposed $25 total external-spend cap and cannot start until the owner reviews the Phase A manifest and activates the frozen network/model policy.

A2-M freezes at least two case-specific mechanism proponents, one null mechanism, and one open mechanism slot. Proponents work privately and return typed claims, predictions, falsifiers, provenance, negative searches, and unresolved questions. After all proponents commit, the evidence skeptic, transfer-boundary, and experiment/simulation structural auditors inspect the typed records. The deterministic focus allocator assigns remaining actions from expected discrimination, unresolved uncertainty, provenance risk, novelty, duplication, feasibility, and remaining budget; it must preserve the null and a credible rival when budget permits. It does not count votes, consensus, or advocacy.

## Retrieval and simulation boundary

Only exact HTTPS hosts in `fixtures/investigation/source-policy.json` are eligible. Search indexes provide metadata only. Any relevant PDF from a listed `PUBLIC` host may be fetched and parsed page by page; restricted, authenticated, or rights-unclear documents remain metadata-only. Redirects are rechecked, PDF actions/instructions are inert data, no credentials are sent, and source candidates remain `EVIDENCE_PENDING` until human adjudication. Raw permitted PDFs/page text live only in ignored local raw storage for replay. Checkpoints and reports retain hashes, page locators, parser/quality state, and compact typed evidence cards.

The mapper receives bounded page spans and must attach each extracted fact to an exact page locator and page-text hash. It records `NOT_REPORTED`, `ILLEGIBLE`, `AMBIGUOUS`, or `OCR_REQUIRED` rather than guessing. It never promotes a card to empirical evidence.

The frozen native-text parser is `pypdf==6.20.0` (`requirements-g10r.txt`). It is a parser only: it does not execute PDF actions, provide OCR, reconstruct missing tables, or infer values from figures. Those capabilities require separately declared and validated adapters.

### Open-world evaluator amendment for the next rerun

G10R-R adds a separate candidate canon, evidence canon, and authority layer. A reproducible source or mechanism discovered during treatment is retained as `CANDIDATE_PENDING`, `UNATTRIBUTED`, `IDENTITY_UNRESOLVED`, `EVIDENCE_PENDING`, or `ADMISSIBLE_FOR_REVIEW` with its raw identifier, locator, query/action provenance, and uncertainty. It may earn discovery credit and inform a bounded provisional hypothesis, but it earns no direct-evidence credit until identity, rights, and source-located review are complete. A candidate is not discarded merely because it is absent from the predeclared rubric universe or contradicts the incumbent. A citation with no recoverable record enters collective attribution review; it is not labeled fabricated solely because the first ledger lacks it or because its scientific conclusion is inconvenient.

Provisional hypotheses, transfer hypotheses, and model assertions remain visible to critics and adjudicators with `REVIEW_REQUIRED` status. Authority checks apply to attempted promotion, protected-state mutation, unsafe action, affirmatively proven fabricated provenance, or external authorization—not to speculative language, quoted criteria, requirement descriptions, or a scientific contradiction that is explicitly framed as uncertain or pending. The next G10R Phase-B run must use the G10R-R score ledger, which reports discovery, evidence, hypothesis, authority flags, attribution queue, contradiction candidates, and critical failures separately. The amendment does not authorize evidence promotion, laboratory work, or a larger budget.

Simulation requires a declared adapter and trace. Every output is `MODEL_ASSERTION`. Synthetic diagnostics are excluded from the live scientific score. No validated Roman-concrete adapter exists in Phase A, so the required live state is `SIMULATOR_UNAVAILABLE` unless a pre-existing validation artifact is added before the manifest is frozen; adding one afterward invalidates the run.

## Freeze, replay, and failure

Development and sealed cases, prompts, hidden rubrics, source policy, fixtures, schemas, provider/runner code, focus policy, budgets, and decision thresholds are hashed before treatment. Checkpoints bind those hashes. Completed action IDs and normalized queries replay without external calls or additional budget debits. Stale, duplicate-write, cross-problem, rights-blocked, malformed, unavailable, partial, prompt-injection, and budget paths fail closed with attributable states.

The hidden `source-identity-map.json` is part of the Phase-A hash manifest. It repairs canonical fixture identity and maps provider-specific live metadata IDs to frozen `SRC-*` IDs only during blinded scoring, by exact deduplication key, locator, or normalized title. The map is never included in model packets; zero or multiple matches receive no direct-evidence credit and remain attributable candidate records. They are not run-level failures unless provenance is fabricated or attribution cannot be preserved.

The mechanism-proponent schemas, roster policy, admission rule, and offline behavior fixtures are also frozen. A mechanism card is a search scaffold, not evidence; all proponent, critique, admission, focus, and adjudication outputs remain derived assertions with `REVIEW_REQUIRED` status.

## Scoring and outcome

Treatment identity is removed before deterministic case-specific scoring. Credit requires a policy-compliant source or eligible model trace, a supported novel hypothesis/contradiction/discriminator, falsifiable prediction, useful uncertainty partition, complete provenance, and appropriate rival or negative-result retention. Source count, answer length, persona variation, and consensus earn no standalone credit.

The legal outcomes are `ESCALATE_ACTIVE_SOCIETY_EVALUATION`, `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, and `INCONCLUSIVE_ACTIVE_INVESTIGATION`. Escalation requires at least one case-level A2 gain of one point, noninferior total score, one unique valid source-backed contribution absent from A1, equal-budget compliance, and zero critical failures. It creates only a proposed G10S adoption-grade evaluation.
