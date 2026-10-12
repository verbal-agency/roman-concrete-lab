# G10D — Society role, incentive, and focus redesign

**Status:** pending
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

## Stop conditions

Stop with `SOCIETY_DESIGN_NO_GO` if viewpoint teams cannot produce distinct contributions, if support agents cannot be linked to the arguments they serve, if support agents are prevented from reporting disconfirming evidence, if the focus layer rewards advocacy over information gain, if critics only veto without useful follow-up, or if the redesign cannot preserve rivals and dissent. Completion does not authorize production adoption or lab work.
