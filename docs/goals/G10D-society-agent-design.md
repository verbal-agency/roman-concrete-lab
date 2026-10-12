# G10D — Society role, incentive, and focus redesign

**Status:** complete
**Dependencies:** G10M complete; G10R-R replay available; G10P complete or its typed interfaces frozen; no new live model or network execution
**Advances:** changes the society from a cautious review panel into viewpoint-centered research teams whose structural task agents compile, test, and challenge evidence for competing arguments

## Why this goal exists

The active run used many roles but did not create the intended relationship between perspective and research support. Structural roles operated as a global review panel instead of helping distinct viewpoint agents develop and test arguments. Proponents and auditors often returned partial, source-free reports; critics identified uncertainty without being required to resolve it; and adjudication collapsed branches into null or transfer summaries. Even with correct plumbing, that topology can yield more discourse without more information.

## Objective

Design and test offline a society organized around competing viewpoint teams:

1. **Viewpoint agents** own distinct mechanism, interpretation, or null cards. Each maintains a falsifiable argument, predictions, falsifiers, prior basis, support region, and unresolved questions.
2. **Viewpoint support agents** are assigned to a viewpoint for a bounded round. They include retrieval scouts, PDF/evidence extractors, lineage and identity verifiers, contradiction hunters, and experiment/simulation designers. They compile evidence for the viewpoint but may return evidence that weakens it.
3. **Cross-viewpoint critics** inspect typed dossiers after the private support round. They compare predictions, expose unsupported transfers, identify missing controls, and propose discriminating searches; they do not replace the viewpoint agents.
4. **Focus/promotion allocator** spends the common budget across viewpoint teams and support tasks using expected information gain, novelty, provenance risk, feasibility, and rival coverage.
5. **Tournament adjudicator** compares viewpoint dossiers and preserves multiple live hypotheses, dissent, unresolved candidates, and the cheapest discriminating next action instead of forcing premature consensus.

The intended topology is:

```text
viewpoint A ─┬─ retrieval scout
             ├─ evidence extractor / verifier
             ├─ contradiction hunter
             └─ experiment designer
viewpoint B ─┬─ retrieval scout
             ├─ evidence extractor / verifier
             ├─ contradiction hunter
             └─ experiment designer
             ↓
common evidence ledger → cross-viewpoint tournament → adjudicated portfolio
```

Support agents are not independent thesis owners and are not allowed to silently become advocates. Every support report is linked to the viewpoint, claim, source/action IDs, and whether the result supports, weakens, or is neutral to that viewpoint. A support agent may recommend abandoning its assigned viewpoint when the evidence warrants it.

## Required design changes

- Define versioned viewpoint cards, support-task contracts, cross-viewpoint critique records, and per-team success metrics; “PARTIAL” is not a sufficient terminal result when a bounded follow-up is available.
- Keep viewpoint teams private during the first round, then expose typed dossiers—not persuasive prose—to cross-viewpoint critics and the focus allocator.
- Assign structural support tasks to viewpoints while allowing support agents to return disconfirming or neutral findings.
- Permit contradiction and open-ended lateral hypotheses without treating them as validated evidence.
- Require every viewpoint to state what evidence would increase or decrease its priority, and require each support task to report whether it helped, weakened, or failed to discriminate.
- Give critics an action obligation: resolve, narrow, or explicitly abstain with a negative-search record.
- Preserve nulls and rivals, but do not allow the null to become the default merely because direct evidence is incomplete.
- Allocate resources adaptively across viewpoints and support tasks, recording why a team or task was promoted, paused, merged, or abandoned.
- Score unique attributable discoveries, useful uncertainty partitions, discriminators, contradiction coverage, and search efficiency—not consensus, answer length, or cautious language.

## Offline evaluation

Use deterministic fixtures derived from the completed G10R cases. Compare the viewpoint-centered society with the current A2-M and A1 control under identical aggregate action, retrieval, token, and cost ceilings. Include cases requiring a lateral source, a contradiction, a null-preserving result, and a mechanism whose evidence is incomplete but actionable. Test both a support agent that strengthens its assigned viewpoint and one that finds disconfirming evidence. No model or network call is authorized by this goal.

## Acceptance criteria

1. Versioned schemas define viewpoint cards, viewpoint dossiers, support-task reports, cross-viewpoint critiques, focus decisions, and adjudication records.
2. Offline fixtures demonstrate at least one valid lateral discovery, one preserved contradiction, one unresolved-but-useful candidate, and one null/rival case without evidence promotion.
3. Support agents are demonstrably linked to their assigned viewpoint while retaining the ability to report weakening or disconfirming evidence.
4. A viewpoint can request and receive multiple structural support tasks, and the resulting evidence remains attributable through the G10P ledger.
5. The focus allocator is deterministic, budget bounded, and records why it allocated work to a viewpoint or support task.
6. The adjudicator preserves competing viewpoints, support contributions, dissent, and unresolved disputes when evidence is incomplete.
7. Blind scoring distinguishes useful discovery from rhetoric, consensus, viewpoint count, and extra output volume.
8. Tests cover team isolation, viewpoint/support assignment, disconfirming support, cross-viewpoint critique, follow-up obligations, dissent retention, open-slot admission, focus fairness, budget equality, and replay.
9. The handoff emits `SOCIETY_DESIGN_READY` or `SOCIETY_DESIGN_NO_GO` and identifies the exact protocol manifest required for a later live rerun.

## Execution contract

### Canonical records and invariants

- `ViewpointCard`: `viewpoint_id`, `case_id`, `kind` (`CANDIDATE`, `NULL`, or `OPEN_SLOT`), mechanism/interpretation statement, prior basis, support region, predictions, falsifiers, and `promotion_status=REVIEW_REQUIRED`.
- `SupportTask`: `task_id`, `viewpoint_id`, task type, bounded charter, budget debit, and status. A task cannot serve more than one viewpoint or cross problem/version boundaries.
- `SupportReport`: `report_id`, `viewpoint_id`, `support_task_id`, stance (`SUPPORTS`, `WEAKENS`, or `NON_DISCRIMINATING`), action IDs, source-candidate IDs, claim IDs, unresolved questions, and status. Weakening evidence is retained as dissent.
- `ViewpointDossier`: one viewpoint's typed reports, source/action/claim unions, dissenting report IDs, unresolved joins, and status.
- `CrossViewpointCritique`: compared dossier IDs, target viewpoint, challenge, source IDs, proposed discriminator, and review status.
- `FocusDecision`: deterministic ordered task allocations, expected information value, rival/null coverage, budget debit, and rationale. Votes and prose length are not inputs.
- `TournamentPortfolio`: leading viewpoint, credible rivals, unresolved disputes, support-task contributions, cheapest discriminator, and authority note. It cannot mutate evidence or authorize a lab.

All records carry `schema_version`, `case_id`, `problem_id`, `problem_version`, and context/treatment scope. Duplicate IDs with identical payloads replay; duplicate IDs with different payloads, stale context, cross-problem reads, and writes outside the declared budget fail closed. A viewpoint may be deprioritized or weakened, but cannot be silently deleted because support is incomplete.

### Deterministic behavior matrix

| Condition | Required result |
|---|---|
| First-round viewpoint team runs | Private dossier; competitor traces are unavailable until commit |
| Support task finds evidence against its viewpoint | Emit `WEAKENS`; preserve the report and reduce or redirect focus as justified |
| Support task finds an unresolved candidate | Retain raw candidate and diagnostic; no direct-evidence promotion |
| Viewpoint requests a task outside its charter | Reject the task and record an authority/contract diagnostic |
| Cross-viewpoint critique lacks a dossier | Reject the critique; do not synthesize from prose |
| Focus budget is insufficient for null and credible rival coverage | Abstain or record `INCONCLUSIVE`; do not declare a winner |
| Early majority forms | Preserve independent dossiers; allocate by the frozen information-value rule |
| Candidate/source IDs are omitted in serialization | Fail the fixture and preserve the pre-serialization record for diagnosis |
| Stale checkpoint or duplicate action | Replay identical payload; reject conflicting payload |
| Adjudicator receives incomplete evidence | Preserve multiple viewpoints, dissent, and next discriminator; do not force consensus |

### Expected implementation surface

- Schemas: `schemas/viewpoint-card.schema.json`, `viewpoint-support-task.schema.json`, `viewpoint-support-report.schema.json`, `viewpoint-dossier.schema.json`, `cross-viewpoint-critique.schema.json`, `focus-decision.schema.json`, and `tournament-portfolio.schema.json`.
- Implementation: `src/roman_concrete_lab/agents/viewpoint_society.py`; integrate with `src/roman_concrete_lab/agents/evidence_bus.py` without changing its authority boundary.
- Fixtures: `fixtures/investigation/viewpoint-society/development.jsonl`, `sealed.jsonl`, `support-behaviors.json`, and `focus-cases.json`.
- Tests: `tests/agents/test_viewpoint_society.py`, `tests/agents/test_viewpoint_support_assignment.py`, and `tests/agents/test_viewpoint_society_replay.py`.
- Documentation/artifacts: `docs/protocols/viewpoint-society.md`, `artifacts/goals/G10D/phase-a.json`, `artifacts/goals/G10D/report.md`, and a frozen manifest.

### Authority and side-effect boundary

G10D is offline-only. It may read/write repository-local fixtures, typed derived records, checkpoints, and manifests. It may not call a model provider, network, subscription, credential, subprocess, external communication channel, laboratory, or arbitrary code from a source document. Structural support records remain derived assertions; no agent can promote evidence, change rights/safety state, expand source policy, authorize a protocol, or increase the aggregate budget.

### Criterion-to-test/artifact map

| Criterion | Evidence |
|---|---|
| 1 | Versioned viewpoint/support/critique/focus schemas and protocol document |
| 2–4 | Sealed behavior fixtures and viewpoint/support assignment tests |
| 5 | Deterministic focus-decision ledger and replay artifact |
| 6–8 | Role-isolation, weakening-support, dissent, budget, and replay tests |
| 9 | `artifacts/goals/G10D/phase-a.json` and `report.md` with a binary handoff |

## Stop conditions

Stop with `SOCIETY_DESIGN_NO_GO` if viewpoint teams cannot produce distinct contributions, if support agents cannot be linked to the arguments they serve, if support agents are prevented from reporting disconfirming evidence, if the focus layer rewards advocacy over information gain, if critics only veto without useful follow-up, or if the redesign cannot preserve rivals and dissent. Completion does not authorize production adoption or lab work.
