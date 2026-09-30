# G09 — Release the non-agent pre-lab research package

**Status:** proposed  
**Dependencies:** G05A complete, G08 complete, GD1 complete, or G07E complete
**Advances:** delivers the program's scientific result and the reusable context/memory/hypothesis substrate before any agent is credited

## Objective

Assemble, reproduce, audit, and version the complete non-agent pre-lab package for the selected branch: evidence-gap, qualitative/LIMITED, bounded-ranking/GO, or the model-free `EXPLORATORY_PLATFORM` tournament path.

## In scope

- one command/workflow that rebuilds all redistributable artifacts from frozen manifests and recorded fixtures;
- corpus, rights, extraction, evidence, feasibility, modeling, hypothesis, ranking, mechanistic, and claim manifests as applicable;
- machine-readable candidate/experiment records and a human-readable research report;
- versioned problem-context cards, scoped memory contracts, append-only hypothesis registry, deterministic tournament, and focus-policy manifests;
- full limitation and rejected-model ledger;
- environment lock, seeds/configs, artifact hashes, and software bill of materials;
- redaction/release check for restricted content, credentials, and unsafe instructions;
- independent reproduction on a clean environment.

## Excluded

Agent orchestration, physical validation, final safety approval, journal-style claims of discovery, and bundling restricted full text.

## Release modes

- `NO_GO_EVIDENCE_GAP`
- `LIMITED_QUALITATIVE_DESIGN`
- `GO_BOUNDED_RANKING`
- `EXPLORATORY_PLATFORM`

The release must use exactly one and explain the downstream implication.

## Expected implementation surface

`src/roman_concrete_lab/release/`, `src/roman_concrete_lab/memory/`, `src/roman_concrete_lab/hypotheses/`, `src/roman_concrete_lab/focus/`, `tests/release/`, `docs/reports/prelab-report.md`, `artifacts/releases/<version>/manifest.*`, and a documented build command.

## Acceptance criteria

1. A clean, offline reproduction from permitted fixtures/manifests regenerates every redistributable release artifact and verifies hashes.
2. The release mode matches the unmodified gate verdicts and completed source branch: G04/G06/G08 when a model branch is applicable, G05A for an evidence-gap release, or GP4/G07E for `EXPLORATORY_PLATFORM`.
3. Every public claim links to evidence and a claim type; a linter rejects prohibited empirical language for unvalidated outputs.
4. Restricted source content and secrets are absent; license/access obligations are summarized.
5. Rankings/protocols preserve support, uncertainty, stability, and expert-review status.
6. Evidence memory is immutable and provenance-linked; hypothesis and episodic memory are typed derived records with explicit write and promotion rules.
7. The deterministic hypothesis tournament and focus policy replay from a frozen context/evidence manifest without a live agent.
8. The release freezes the approved focus and promotion policies, legal transitions, abstention rules, reviewer authority, and retraction/context-amendment behavior for later agent evaluation.
9. An independent reviewer can trace a reported value to its source locator and transformation history using documented commands.
10. The release has no runtime dependency on a live LLM, network service, or unavailable database.

## Verification evidence

`artifacts/goals/G09/report.md`, clean-build log, release hash manifest, claim audit, rights/security scan, software bill of materials, and independent reproduction record.
