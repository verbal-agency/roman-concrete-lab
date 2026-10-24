# G10R-W — Wire the research loop into the live A2-M runner

**Status:** complete — `RUNTIME_RESEARCH_LOOP_WIRED`
**Dependencies:** G10R-T completed; G10R-U freeze exists but is stale for this
change; no model or network calls

## Why this goal exists

The G10R-V paid run was correctly stopped before provider initialization. The
frozen manifest named the G10R-T research-loop implementation, but the live
`ActiveInvestigationRunner` still executed the older A2-M path: it did not bind
candidate selection to fetch, did not persist research-loop transitions in its
checkpoint, and could not revise the dossiers consumed by adjudication after
focused work. A paid comparison at that boundary would have tested the wrong
system.

## Changes

- Added a provider-neutral `ResearchLoopLedger` seam for the live A2-M path.
- Bound search observations to typed needs and candidate selections before any
  requested content fetch.
- Rejected unselected fetch locators in A2-M and recorded the rejection for
  replay rather than silently bypassing selection.
- Persisted fetch/map transitions, dossier revisions, focus decisions, and
  evidence-conditioned open-slot decisions in the runner checkpoint.
- Added shared-dossier refresh after later support reports so adjudication sees
  the revised dossier while the earlier dossier remains in the evidence bus.
- Added hash-addressed manifest validation to the Phase-B entry point; legacy
  phase-a files remain replayable, while a historical post-freeze manifest is
  rejected if any checked-in source hash has drifted.
- Added deterministic checkpoint restoration and a no-provider-call replay
  assertion.

## Verification

The offline integration fixture passed:

```text
python3 -m pytest -q tests/agents/test_g10r_v_research_loop_wiring.py
2 passed
```

The existing active-runner and remediation suites also pass:

```text
python3 -m pytest -q tests/agents/test_g10r_v_research_loop_wiring.py tests/agents/test_active_investigation.py tests/agents/test_offline_remediation_integration.py
30 passed
```

No OpenAI/model call, network request, subscription retrieval, or paid action
was made. This goal proves wiring and replay behavior only; it does not prove
that the society produces a useful scientific result.

## Handoff

Because the code and runner contract changed after G10R-U, the G10R-U manifest
must remain historical and must not be reused for a paid run. A new freeze goal
(G10R-X) must hash this wiring and record a new owner activation request before
G10R-V can be activated.
