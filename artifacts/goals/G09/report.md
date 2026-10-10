# G09 cycle report — complete

**Selected track:** `EXPLORATORY_PLATFORM`
**Status:** complete; deterministic non-agent release built and independently reproduced offline
**Execution date:** 2026-09-30
**Release:** `artifacts/releases/2026-09-30-exploratory-platform/`

## Outcome

G09 packages the GP4/G07E substrate as a redistributable, non-agent release. The bundle contains the replayable tournament output, context and memory summaries, typed hypothesis/promotion policy, claim ledger, lawful-access summary, security scan, software bill of materials, reproduction commands, and artifact hashes. Restricted full text, credentials, live services, lab instructions, and agent runtime are excluded.

## Acceptance criteria

| Criterion | Result | Evidence |
|---|---|---|
| 1. Clean offline reproduction and hashes | **PASS** | `tests/release/test_build.py`; two isolated builds are byte-identical; release manifest verifies 8 artifacts |
| 2. Release mode matches source branch | **PASS** | `release.json`: `EXPLORATORY_PLATFORM`, gate basis G-1/GP4/G07E |
| 3. Evidence-linked claims and prohibited-language lint | **PASS** | `claims.json`: 4 claims, all typed and evidence-linked; linter tests reject empirical overclaiming |
| 4. Rights, restricted content, and secrets | **PASS** | `rights.json`; `security-scan.json`; no restricted full text or secret findings |
| 5. Ranking support/uncertainty/stability/reviewer status | **PASS** | `release.json` ranking summaries for all three cards |
| 6. Typed memory and promotion rules | **PASS** | `release.json` memory summaries and frozen policy transition table |
| 7. Tournament/focus replay without agent | **PASS** | `tournament-replay.json`; G07E replay invoked directly by the builder |
| 8. Frozen policy and legal transitions | **PASS** | policy version/hash, legal transitions, abstention, reviewer authority, and retraction/context-amendment rules |
| 9. Independent traceability | **PASS** | every claim has source locators and transformation history; `reproduction.json` documents commands |
| 10. No live runtime dependency | **PASS** | SBOM declares no network, database, LLM, or agent dependency |

## Verification

- `PYTHONPATH=src python3 -m roman_concrete_lab.release.build --version 2026-09-30-exploratory-platform --output artifacts/releases/2026-09-30-exploratory-platform` — pass.
- `python3 -m pytest -q` — **29 passed**.
- `git diff --check` — pass.
- Two clean temporary output directories were compared byte-for-byte by the release tests.

## Limitations and routed work

- This is an exploratory platform release, not a physical validation, recipe, or performance release.
- Closed-world agent evaluation is G10; bounded open-world lateral research is separately gated in G10R. Qualified review and any lab handoff remain G11/GL1 work.
- No backlog item was required; later work is already represented by G10 and the deferred GL1 branch.
