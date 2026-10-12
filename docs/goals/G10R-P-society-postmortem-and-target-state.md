# G10R-P — Society postmortem and target-state design

**Status:** proposed
**Dependencies:** G10R complete with `DO_NOT_ESCALATE_ACTIVE_SOCIETY`, `artifacts/goals/G10R/run.json`, and `artifacts/goals/G10R-R/replay.json`; no new model, network, subscription, or laboratory execution
**Advances:** determines whether the negative live signal came from society design, runtime integration, information-acquisition policy, task/case construction, or scoring, then defines the measurable target state required before another paid evaluation

## Why this goal exists

The first repaired open-world pilot completed valid A1/A2-M comparisons but did
not show a qualifying society contribution. That result is useful only if we
separate a design failure from an implementation mismatch, an information
acquisition failure, a task/fixture ceiling, and an evaluator failure.

The run itself supplies reasons to investigate rather than immediately discard
the idea. A1 used two model calls per case and reached the query/source ceiling
with zero document fetches. A2-M used thirteen model calls per case, consumed
substantially more tokens on planning, proponent reports, audits, and
adjudication, and still produced no direct-evidence contribution. The repaired
component ledger showed discovery deltas of `-4`, `+2`, `-6`, and `-5` across
the four cases. Separately, the live runner still invokes the legacy
`mechanism_tournament` path and excludes `OPEN_SLOT` cards from proponent
execution; it does not yet execute the G10D `ViewpointSociety` plus evidence-bus
topology as a live treatment. The negative result therefore applies to the
executed A2-M implementation, not automatically to the intended target
architecture.

## Objective

Produce an evidence-backed postmortem and target-state specification that:

1. reconstructs the live comparison and repaired replay without new external calls;
2. identifies where value was lost at each layer: viewpoint formation, support-task assignment, retrieval, extraction/identity, contradiction search, focus allocation, cross-viewpoint critique, adjudication, serialization, and scoring;
3. distinguishes implementation-to-contract gaps from genuine society weaknesses and from task/fixture or scorer limitations;
4. defines a measurable target-state architecture and minimum acceptance thresholds for a future rerun; and
5. issues exactly one readiness outcome: `TARGET_STATE_READY_FOR_OFFLINE_BUILD`, `POSTMORTEM_NO_GO`, or `INCONCLUSIVE_POSTMORTEM`.

This goal does not authorize another paid run. It may read repository-local
artifacts, run deterministic analysis and tests, and amend contracts or create
follow-on offline goals only after the target state is explicit.

## Required diagnostic questions

### Architecture and integration

- Did the live A2-M treatment instantiate the intended G10D topology, or did it
  execute the older mechanism-tournament implementation?
- Were viewpoint cards, support tasks, support reports, evidence-bus joins,
  dossiers, critiques, focus decisions, and tournament portfolios all present
  in the live checkpoint and final score ledger?
- Was the open slot admitted and investigated, or merely present in a roster?
- Did private first-round isolation hold before sharing?

### Information acquisition

- How many actions produced unique attributable candidates, permitted document
  fetches, page-aware evidence cards, contradictions, and useful discriminators?
- Which tasks duplicated one another or spent tokens without opening a new
  evidence frontier?
- Did support agents have an obligation and budget to fetch, extract, verify,
  or weaken a viewpoint, or did they mostly generate cautious metadata prose?
- Did the focus layer allocate work by expected information value, preserve a
  credible rival and null, and redirect after negative evidence?

### Evaluation validity

- Did the cases contain reachable information that could distinguish A1 from
  A2-M under the frozen source policy?
- Did the scorer correctly separate discovery, hypothesis, evidence, authority,
  and critical-failure dimensions without rewarding rhetoric or punishing
  unresolved but attributable candidates?
- Did any serialization, checkpoint, identity, or attribution loss suppress a
  genuine contribution?
- Which conclusions are supported by the run, and which remain untestable until
  a live treatment actually uses the G10D topology?

## Target state for any future live evaluation

A future society is not ready for paid testing until all of the following are
true in an offline build and replay:

1. **Topology fidelity.** The live-capable runner uses the versioned G10D
   `ViewpointSociety` and G10P evidence bus, not a legacy substitute. Every
   active viewpoint has a private first-round dossier, assigned structural
   support tasks, typed support reports, cross-viewpoint critiques, a focus
   decision, and an adjudicated portfolio.
2. **Open-world coverage.** The null and a credible rival remain active; the
   open slot can be admitted through a typed record and receives bounded work
   when its admission basis warrants it.
3. **Support-task obligation.** Retrieval, extraction/identity, contradiction,
   and experiment-design tasks are explicitly assigned to viewpoints. Each task
   must support, weaken, or fail to discriminate and must either produce an
   attributable action/source/claim join or record a bounded abstention reason.
4. **Acquisition over discourse.** The target ledger reports unique candidate
   yield, nonduplicate query rate, permitted-fetch rate, evidence-card yield,
   contradiction coverage, attribution completeness, useful-hypothesis yield,
   and token/action cost. Planning, consensus, viewpoint count, and answer
   length receive zero scientific credit.
5. **Budget parity.** A1 and the society receive identical aggregate query,
   source, payload, fetch, simulation, input-token, output-token, elapsed-time,
   stopping, authority, and spend ceilings. Society overhead is visible and
   cannot silently consume the entire investigation budget before evidence work.
6. **Decision relevance.** Development fixtures demonstrate that the topology
   can produce a unique attributable discovery, a weakening result, a useful
   contradiction, and a cheapest discriminator. Sealed cases have reachable
   headroom and cannot be solved by metadata-only keyword matching.
7. **Reproducibility.** Checkpoints, duplicate actions, retries, identity
   resolution, evidence-bus joins, blind scoring, and replay are byte-stable;
   unresolved candidates remain reviewable and are not promoted automatically.

## Deliverables

- `artifacts/goals/G10R-P/postmortem.json` with per-case/per-layer diagnostics;
- `artifacts/goals/G10R-P/gap-matrix.md` mapping observed failure to evidence,
  severity, remediation, and verification;
- `artifacts/goals/G10R-P/target-state.json` with versioned thresholds and
  explicit non-goals;
- an implementation-to-contract comparison covering G10D, G10P, and the live
  G10R runner;
- deterministic fixtures/tests for every proposed remediation that can be
  tested without a model or network;
- `artifacts/goals/G10R-P/report.md` mapping every acceptance criterion to
  evidence and issuing one readiness outcome.

## Acceptance criteria

1. Every A1/A2-M case is reconstructed from `run.json`, checkpoints, and the
   repaired replay, including calls, tokens, queries, candidates, fetches,
   hypotheses, evidence, critiques, costs, and critical failures.
2. The postmortem contains a typed loss ledger distinguishing architecture,
   integration, acquisition, task/fixture, scorer, and plumbing causes; each
   finding has a repository evidence locator and confidence.
3. The report explicitly states whether the live runner executed G10D or a
   predecessor, whether the open slot was actually active, and whether support
   tasks were linked through the evidence bus.
4. At least one offline replay demonstrates that each proposed high-severity
   remediation can preserve provenance, dissent, unresolved candidates, and
   authority boundaries without new external calls.
5. The target-state contract defines measurable thresholds for topology
   fidelity, unique attributable contribution, evidence acquisition,
   contradiction coverage, attribution completeness, budget parity, and
   replayability.
6. The target state includes a falsifiable comparison rule for a future A1 vs
   society test and states what result would justify stopping rather than
   spending again.
7. No model, network, subscription, credential, laboratory, evidence
   promotion, or external communication is used by this goal.
8. The handoff emits exactly one of `TARGET_STATE_READY_FOR_OFFLINE_BUILD`,
   `POSTMORTEM_NO_GO`, or `INCONCLUSIVE_POSTMORTEM` and identifies the next
   goal, if any.

## Stop conditions

Stop with `INCONCLUSIVE_POSTMORTEM` if the artifacts cannot distinguish a
design failure from an integration or scorer failure. Emit `POSTMORTEM_NO_GO`
if the target state cannot produce a measurable information-acquisition
advantage under equal budgets, or if the required topology cannot be enforced
without granting unsafe authority. Do not authorize another paid evaluation
until this goal or an explicitly approved successor completes.
