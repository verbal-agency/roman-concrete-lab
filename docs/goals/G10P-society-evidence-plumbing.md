# G10P — Society evidence-bus and attribution plumbing

**Status:** pending
**Dependencies:** G10R-R complete; completed G10R trace and checkpoints available; no new live model or network execution
**Advances:** makes viewpoint, support-task, candidate, claim, branch, and adjudication records survive end to end so useful work cannot disappear before scoring

## Why this goal exists

The first active-investigation run exposed a plumbing failure in addition to the evaluator defect. Society branches produced candidate and provenance material in checkpoints, but many proponent, auditor, and final-adjudicator records carried empty `source_candidate_ids`. The scorer therefore saw no attributable discovery contribution even when intermediate records contained candidate information. This goal repairs that evidence bus without changing the scientific authority boundary or adding live calls.

## Objective

Repair and verify the typed handoffs across:

```text
viewpoint assignment -> support task -> action result -> source-candidate ledger
  -> viewpoint dossier -> cross-viewpoint critique -> adjudication
  -> final portfolio -> blinded score ledger
```

Every retained candidate, claim, contradiction, hypothesis, and branch contribution must remain attributable to its viewpoint, support task, source/action, and treatment/branch, or be explicitly marked unresolved/unattributed with a reason. A support report must also state whether the result supports, weakens, or fails to discriminate for the assigned viewpoint.

## Scope and non-goals

This is an offline contract and implementation goal. It authorizes no provider calls, network retrieval, subscription access, laboratory work, evidence promotion, new source policy, or budget increase. It does not redesign agent roles; that is G10D.

## Required work

1. Define typed joins among `ViewpointCard`, `SupportTask`, `InvestigationAction`, `SourceCandidate`, `InvestigationClaim`, `ViewpointDossier`, `CrossViewpointCritique`, `InvestigationPortfolio`, and score-ledger records.
2. Make the shared candidate ledger append-only, problem/version scoped, replayable, and available to viewpoint teams, support agents, critics, and adjudicators through stable IDs.
3. Require every support report to identify its assigned viewpoint and task, its stance (`SUPPORTS`, `WEAKENS`, or `NON_DISCRIMINATING`), and the candidate/action records it used.
4. Require every source-backed claim to carry a candidate ID or an explicit `UNATTRIBUTED` record; prohibit silent dropping during serialization, checkpointing, dossier assembly, cross-viewpoint critique, or adjudication.
5. Require the adjudicator to preserve viewpoint IDs, support-task IDs, source IDs, branch contribution IDs, contradictions, unresolved candidates, and discarded-claim reasons in its final portfolio.
6. Add deterministic attribution and deduplication at the scorer boundary without converting unresolved candidates into evidence.
7. Add fixtures for successful viewpoint-to-support propagation, support that weakens its assigned viewpoint, duplicate candidates, unresolved identity, unattributed citation, cross-viewpoint disagreement, checkpoint/resume, and deliberate candidate loss.
8. Replay the existing G10R traces and report how many contributions were previously lost, newly attributable, unresolved, or still unsupported; identify which records cannot be assigned to a viewpoint because the historical run predates this contract.

## Acceptance criteria

1. The end-to-end schemas and join rules are versioned and documented.
2. A candidate created by a tool action can be traced byte-stably through support task, viewpoint dossier, cross-viewpoint critique, adjudication, portfolio, and score ledger.
3. No source ID can disappear silently; missing joins produce an explicit diagnostic and preserve the raw record.
4. The scorer awards discovery credit only for reproducible attributable contributions and awards no evidence credit to unresolved or metadata-only records.
5. Replay is deterministic and uses no provider or network calls.
6. Tests cover positive viewpoint/support propagation, support-agent weakening evidence, unresolved/unattributed retention, duplicate handling, stale/cross-problem writes, serialization, checkpoint/resume, and silent-drop detection.
7. The handoff contains a before/after attribution ledger for the completed G10R run and emits `SOCIETY_PLUMBING_READY` or `SOCIETY_PLUMBING_NO_GO`.

## Stop conditions

Stop with `SOCIETY_PLUMBING_NO_GO` if candidate provenance cannot survive the handoffs without manual reconstruction, if the scorer promotes unresolved records, or if replay is not deterministic. Completion does not authorize a live rerun; G10D must also complete.
