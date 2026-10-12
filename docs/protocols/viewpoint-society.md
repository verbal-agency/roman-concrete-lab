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

## State and invariants

- Viewpoints are case/problem/version scoped and remain `REVIEW_REQUIRED`.
- A support task belongs to exactly one viewpoint and cannot be assigned after sharing begins.
- A support report must identify its task, action IDs, source IDs, claim IDs, stance, and unresolved questions.
- Dossiers are private until every active viewpoint commits; cross-viewpoint critics cannot read partial dossiers.
- Focus allocation is deterministic and must preserve the null and one credible rival when the budget permits.
- The adjudicator preserves all credible rivals, dissent, unresolved joins, and the next discriminator; it cannot promote evidence or authorize physical work.
- Duplicate IDs replay identical payloads; conflicting duplicates, stale contexts, cross-problem writes, unsupported task types, and budget violations fail closed.

## Scoring

Credit is awarded only for typed support contributions, weakening/disconfirming contributions, and proposed discriminators. Viewpoint count, consensus, answer length, rhetoric, and advocacy receive zero credit. Candidate records remain derived and may be unresolved; they never become immutable evidence through this protocol.

## Authority boundary

Phase A is offline-only. No model calls, network retrieval, subscriptions, credentials, subprocesses, arbitrary document instructions, external communication, laboratory work, source-policy changes, evidence promotion, or budget expansion are permitted.
