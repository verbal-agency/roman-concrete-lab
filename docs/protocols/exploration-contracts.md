# G00 exploratory contracts (v1)

These contracts are the smallest reusable surface authorized by G00. They are documentation contracts, not a database schema, execution protocol, or agent API. GP1–GP4 may refine them only by versioned amendment.

## 1. Versioned problem context

Every run must load exactly one context card with:

| Field | Required meaning |
|---|---|
| `context_id`, `context_version` | Stable identity and immutable version |
| `question` | One falsifiable scientific question |
| `domain` | Material/process and exposure boundary |
| `primary_endpoint` | Functional outcome and measurement semantics |
| `secondary_endpoints` | Supporting outcomes, never substitutes for the primary endpoint |
| `candidate_variables` | Interventions or process factors that are actually evidenced |
| `controls` | Required comparator or explicit `UNRESOLVED` status |
| `constraints` | Material availability, safety, budget, and execution limits |
| `utility` | Conditional ranking dimensions and weights or a declared qualitative ordering |
| `support_region` | Evidence-backed applicability boundary |
| `allowed_outputs` | `PROVISIONAL_BEST`, `HYPOTHESIS`, `EXPERIMENT_CANDIDATE`, or `ABSTAIN` |
| `authority` | Current decision owner and next required reviewer |

Illegal states: missing context, multiple active contexts, an unbounded endpoint, or an output not listed in `allowed_outputs`. A Roman-concrete context must keep modern terrestrial mortar, functional water-flow/permeability recovery, crack closure, and strength-retention constraints distinct.

## 2. Candidate and hypothesis surface

Each candidate record contains `candidate_id`, evidence record IDs, exact locators, material/process identity status, comparator status, endpoint status, support region, uncertainty, missing fields, and one of `PROVISIONAL`, `CONTEXT_ONLY`, `BLOCKED`, or `ABSTAIN`.

Each hypothesis record contains `hypothesis_id`, intervention, comparator, applicable domain, predicted observation, rival hypothesis IDs, evidence locators, claim type (`REPORTED`, `DERIVED`, `PROPOSED`, `UNRESOLVED`), and a falsification observation. No hypothesis record may overwrite immutable evidence or imply a recipe absent from its sources.

## 3. Conditional ranking contract

A ranking is valid only when it carries `context_id/version`, utility and constraints, support region, evidence coverage, uncertainty, abstention reason (if applicable), and a deterministic tie-break rule. The only legal ranking labels before GL2 are:

- `PROVISIONAL_BEST`: conditional ordering inside one declared problem context;
- `PARETO_SET`: non-dominated candidates when no single utility is justified;
- `ABSTAIN`: insufficient, contradictory, or out-of-support evidence.

The ranking must never emit “best material,” validated effectiveness, a recipe, or a cross-domain comparison without an explicit common utility and endpoint mapping. GP2 may rank information value, feasibility, and risk separately from expected performance.

## 4. Portfolio and feedback boundary

An experiment-portfolio entry contains the candidate/hypothesis references, question, expected discriminating observation, controls, required facility capability, utility dimensions, uncertainty, and status. Legal statuses are `INCLUDED`, `DEFERRED`, `REJECTED`, `REVIEW_REQUIRED`, and `ABSTAIN`.

G00–GP4 may serialize proposed questions and accept offline or qualified-review feedback. They may not send external messages, purchase materials, execute a lab, accept safety approval, or treat unreturned feedback as evidence. Returned physical results enter only through GL2, which decides `SUPPORTED`, `NARROW_USE_CASE`, `INCONCLUSIVE`, or `NOT_REPRODUCED`.

## 5. Deterministic behavior matrix

| Input condition | Required output |
|---|---|
| Complete in-domain evidence and declared utility | Conditional ranking with support and uncertainty |
| Missing comparator, endpoint, or utility | `ABSTAIN` / `REVIEW_REQUIRED` with missing field |
| Contradictory evidence | Preserve both claims; emit uncertainty or `ABSTAIN` |
| Out-of-domain candidate | `CONTEXT_ONLY` or `ABSTAIN`; never rank as performance evidence |
| Requested recipe, safety approval, or physical execution | Reject as unauthorized |
| Physical feedback absent | Keep portfolio status provisional; do not unlock GL2/GD1 |
