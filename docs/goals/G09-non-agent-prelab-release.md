# G09 — Release the non-agent pre-lab research package

**Status:** proposed  
**Dependencies:** G05A complete or G08 complete  
**Advances:** delivers the program's scientific result before any agent is credited

## Objective

Assemble, reproduce, audit, and version the complete non-agent pre-lab package for the selected branch: either evidence-gap, qualitative/LIMITED, or bounded-ranking/GO.

## In scope

- one command/workflow that rebuilds all redistributable artifacts from frozen manifests and recorded fixtures;
- corpus, rights, extraction, evidence, feasibility, modeling, hypothesis, ranking, mechanistic, and claim manifests as applicable;
- machine-readable candidate/experiment records and a human-readable research report;
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

The release must use exactly one and explain the downstream implication.

## Expected implementation surface

`src/roman_concrete_lab/release/`, `tests/release/`, `docs/reports/prelab-report.md`, `artifacts/releases/<version>/manifest.*`, and a documented build command.

## Acceptance criteria

1. A clean, offline reproduction from permitted fixtures/manifests regenerates every redistributable release artifact and verifies hashes.
2. The release mode matches the unmodified gate verdicts from G04/G06/G08.
3. Every public claim links to evidence and a claim type; a linter rejects prohibited empirical language for unvalidated outputs.
4. Restricted source content and secrets are absent; license/access obligations are summarized.
5. Rankings/protocols preserve support, uncertainty, stability, and expert-review status.
6. An independent reviewer can trace a reported value to its source locator and transformation history using documented commands.
7. The release has no runtime dependency on a live LLM, network service, or unavailable database.

## Verification evidence

`artifacts/goals/G09/report.md`, clean-build log, release hash manifest, claim audit, rights/security scan, software bill of materials, and independent reproduction record.
