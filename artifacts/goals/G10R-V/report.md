# G10R-V post-run report

**Outcome:** `DO_NOT_ESCALATE_ACTIVE_SOCIETY`
**Manifest:** `sha256:8ddb3096705d3fbfa706361d93647574646d1c70e13f14987383a9c6e3d77b3c`
**Provider:** OpenAI Responses / `gpt-6-luna` / low reasoning
**External spend:** `$0.0320087` of `$25.00`

## What was tested

The frozen four-case comparison ran A1 (single investigator) and A2-M (viewpoint society with structural support agents) under the same source policy and ceilings. The run completed all eight case/arm checkpoints. No laboratory work, evidence promotion, subscription access, or source-policy expansion was authorized.

## Result

The terminal decision is `DO_NOT_ESCALATE_ACTIVE_SOCIETY`. Neither arm earned a positive rubric score or evidence score, and the society produced no qualifying unique contribution over A1:

```json
{
  "a1_total_score": 0,
  "a2_total_score": 0,
  "any_case_gain": false,
  "critical_failures": [],
  "per_case": [
    {
      "a1_score": 0,
      "a2_score": 0,
      "a2_unique_contributions": [],
      "case_id": "S-ACTIVE-ACCESS",
      "gain": 0
    },
    {
      "a1_score": 0,
      "a2_score": 0,
      "a2_unique_contributions": [],
      "case_id": "S-ACTIVE-LINEAGE",
      "gain": 0
    },
    {
      "a1_score": 0,
      "a2_score": 0,
      "a2_unique_contributions": [],
      "case_id": "S-ACTIVE-SIM",
      "gain": 0
    },
    {
      "a1_score": 0,
      "a2_score": 0,
      "a2_unique_contributions": [],
      "case_id": "S-ACTIVE-TRANSFER",
      "gain": 0
    }
  ],
  "qualifying_unique_contribution": false
}
```

The raw discovery/hypothesis counters are useful diagnostics, not evidence credit. A1 produced more raw discovery and hypothesis material in aggregate than A2-M, while A2-M did produce some candidates and hypotheses. Those records remained unresolved or unsupported by the typed source-backed rubric, so they could not change the decision.

## Arm diagnostics

| arm | raw discovery | raw hypotheses | rubric score | evidence score | unresolved sources | queries | estimated cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| A1 | 20 | 7 | 0 | 0 | 19 | 33 | $0.0051782 |
| A2-M | 6 | 4 | 0 | 0 | 6 | 39 | $0.0268305 |

## Replay and integrity

Offline replay was run for all eight completed checkpoints with inert provider/adapter objects. It made zero provider and zero network calls; `replay.json` records the per-checkpoint comparisons. The replay result is `true`. The exact G10R-X manifest was copied and hash-checked before finalization, and the hard aggregate cap was not exceeded.

## Interpretation and next goal

This is a fair negative signal for the current society wiring and task design, not proof that agent societies are intrinsically unhelpful. The bottleneck is conversion: the run generated some candidate and hypothesis material, but source identity, task-criterion matching, and evidence attribution did not turn it into supported contributions. The next goal should be offline diagnosis and targeted ablation of acquisition-to-rubric conversion (including why A1 outperformed A2-M on the same cases), with no automatic paid rerun until that diagnosis produces a new frozen treatment.
