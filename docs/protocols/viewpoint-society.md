# Viewpoint-centered society protocol

**Protocol version:** `g10d.1-viewpoint-centered-society`

G10D tests a topology, not a model capability claim. Persistent viewpoint agents own competing mechanisms, interpretations, or null positions. Structural support agents are assigned beneath each viewpoint to retrieve, extract, verify, challenge, or design discriminators. Cross-viewpoint critics compare typed dossiers only after the private support round.

## Architecture

```text
viewpoint card
  ├─ retrieval / extraction support
  ├─ identity / lineage support
  ├─ contradiction support
  └─ experiment / simulation design support
        ↓
private viewpoint dossier
        ↓ (all teams commit)
common evidence ledger → cross-viewpoint critique → focus tournament
        ↓
provisional portfolio with rivals, dissent, and next discriminator
```

Support agents do not inherit the viewpoint as truth. Every report states `SUPPORTS`, `WEAKENS`, or `NON_DISCRIMINATING`. A weakening report remains in the dossier and can reduce focus priority. A null viewpoint and an open slot are required; open-slot admission requires a typed candidate card, reason, and bounded scope.

## Provisional arguments and open-world sources

Viewpoints may advance a `PROVISIONAL` argument before any cited source has
been accepted. An argument records its mechanism, prediction, uncertainty,
requested discriminators, and the exact source references the agent is asking
the society to investigate. A source reference is a lead, not evidence credit.

Acquisition agents may discover new public locators and citation trails. A
previously unknown route is stored in a quarantined source record with its
locator, identity fields, retrieval outcome, rights state, content hash, parser
status, and citation ancestry. Unknown hosts cannot earn direct evidence credit
until the source is vetted and admitted to the reviewable corpus; the agent may
still use the lead to defend or revise its provisional argument.

Vetting operates on the claim–source edge, not only on the source record. Each
edge must resolve to exactly one of `SUPPORTED`, `CONTRADICTED`, `UNRESOLVED`,
`MISATTRIBUTED`, or `UNRETRIEVABLE`. A real source that does not address the
claim is not support, and a failed fetch is not contradiction. Every supported
or contradicted edge requires a page, figure, table, or exact locator plus a
content hash when available.

Arguments, source records, and edge decisions are append-only revisions.
Contradiction, rejection, and failed retrieval remain visible; they cannot
erase the original argument or silently rewrite its provenance. Work identity,
content hash, and citation ancestry deduplicate apparent corroboration so one
paper repeated by several agents does not become independent support. Consensus,
repetition, rhetoric, and agent count receive zero scientific credit. An
adversarial vetter, null position, and credible rival remain in the tournament
when the case permits.

## State and invariants

- Viewpoints are case/problem/version scoped and remain `REVIEW_REQUIRED`.
- A support task belongs to exactly one viewpoint and cannot be assigned after sharing begins.
- A support report must identify its task, action IDs, source IDs, claim IDs, stance, and unresolved questions.
- Dossiers are private until every active viewpoint commits; cross-viewpoint critics cannot read partial dossiers.
- Focus allocation is deterministic and must preserve the null and one credible rival when the budget permits.
- The adjudicator preserves all credible rivals, dissent, unresolved joins, and the next discriminator; it cannot promote evidence or authorize physical work.
- Duplicate IDs replay identical payloads; conflicting duplicates, stale contexts, cross-problem writes, unsupported task types, and budget violations fail closed.
- Illegal transitions fail closed: a provisional argument cannot become
  supported without a vetted claim–source edge; an unreviewed source cannot
  become corpus-admitted without identity/rights/provenance checks; and no
  agent can self-promote an argument to immutable evidence or laboratory
  authority.

## Scoring

Credit is awarded only for typed support contributions, weakening/disconfirming contributions, and proposed discriminators. Viewpoint count, consensus, answer length, rhetoric, and advocacy receive zero credit. Candidate records remain derived and may be unresolved; they never become immutable evidence through this protocol.

## Authority boundary

Phase A is offline-only. No model calls, network retrieval, subscriptions, credentials, subprocesses, arbitrary document instructions, external communication, laboratory work, source-policy changes, evidence promotion, or budget expansion are permitted.

## G10R-T research loop

The society's structural agents are not allowed to request a fetch from prose.
They create a typed `ResearchNeed`, search, select a discovered candidate by
stable ID, and only then invoke fetch/map. A page-aware card is joined to the
need before a report can claim evidence. Private dossiers are revised after
sharing, critique, and focused follow-up; adjudication reads the latest
monotonic revision. The open slot is evaluated only after the first shared
round and can be admitted, rejected as redundant, or abstained when no
distinct discriminator exists. `tools/evaluation/society_research_loop_ablation.py`
is the provider-free reference execution.
