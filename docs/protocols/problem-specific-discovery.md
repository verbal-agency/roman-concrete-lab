# Problem-specific discovery contract (GP4)

This protocol validates the reusable substrate without making the scientific domains generic. A problem card supplies the question, endpoint semantics, controls, constraints, utility, support region, allowed outputs, authority, and memory policy. The card is the execution context; the substrate does not import assumptions from another card.

## Memory authority tiers

1. **Immutable evidence memory:** source-located observations or explicitly derived ledger facts. Append-only; no hypothesis or note may overwrite it.
2. **Typed hypothesis memory:** proposed or derived hypotheses tied to evidence locators, rival predictions, and a problem card. It is not ground truth.
3. **Untrusted notes:** reflections, scratch reasoning, or transfer ideas. They cannot change evidence, candidate status, utility, or authority.

Portfolio entries must reference the memory IDs used for their claim. A missing reference, cross-tier overwrite, or memory ID collision is invalid.

## Output policy

- `PROVISIONAL_BEST` is a conditional ordering within one card and support region.
- `PARETO_SET` is used when utility dimensions cannot justify a single winner.
- `ABSTAIN` or `REVIEW_REQUIRED` is required for missing, unsupported, contradictory, or out-of-domain evidence.
- `REJECT_COMPARISON` is required when cards lack a common utility, endpoint mapping, and evidence basis.

No output may claim a universal best material, validated performance, a recipe, a safety approval, a lab result, or agent authority. The protocol is offline-only and introduces no agent runtime, model call, network retrieval, or physical execution.

## Domain separation

Roman-concrete, lime-mortar, and battery-cathode cards use their own primary endpoint semantics and support regions. Shared field names make serialization reusable; they do not make water-flow recovery, sorptivity recovery, and capacity retention interchangeable. Cross-card comparison is rejected unless a future, explicit amendment supplies a defensible common utility and endpoint mapping.
