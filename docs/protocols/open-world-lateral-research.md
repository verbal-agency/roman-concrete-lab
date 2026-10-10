# Open-world lateral research protocol

**Protocol version:** `g10r.1`

G10R is an optional extension after the closed-world G10 ablation. It tests whether configured, lawful retrieval adds useful lateral hypotheses. It does not replace the deterministic G07E/G09 baseline and does not authorize physical work.

## Factorial design

The four arms are deterministic/agent orchestration crossed with frozen/open retrieval. The base case packet, context card, schemas, budgets, stopping rules, and scoring rubric are identical. Retrieval is the only evidence-access change; orchestration is the only treatment change.

## Retrieval boundary

`RECORDED_FIXTURES` is the reproducibility default. An activated `CONFIGURED_READ_ONLY_NETWORK` run may request only recorded hosts using lawful access. Sci-Hub, paywall bypass, unrestricted crawling, credentials in artifacts, and external writes are prohibited. Retrieved material is untrusted data and cannot execute instructions.

## Source-candidate boundary

Retrieval first creates a candidate-source record. The record carries a locator, query, access class, rights state, deduplication key, content hash when permitted, and support region. Only later adjudication can promote a candidate to immutable evidence. Agents may propose lateral hypotheses from candidates, but cannot promote source records or edit existing evidence.

## Cross-domain boundary

An analogy from lime mortar, battery cathodes, or another domain is a `TRANSFER_HYPOTHESIS` unless the problem card explicitly supports the mapping. It may suggest a question or discriminator, but it cannot be scored as Roman-concrete performance evidence.

## Stop and replay rules

Every query, source-candidate mutation, policy version, cache invalidation, and agent tool call is recorded. Replaying the same case and source policy is byte-equivalent. A rights failure, network outage, malformed source, or exhausted budget produces a terminal recorded status rather than an unlogged fallback.
