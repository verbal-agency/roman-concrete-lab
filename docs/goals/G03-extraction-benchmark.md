# G03 — Establish an adjudicated extraction benchmark

**Status:** proposed  
**Dependencies:** G02 complete  
**Advances:** proves whether structured evidence can be recovered reliably before scaling extraction

## Objective

Create an expert-adjudicated gold set from the frozen benchmark partition and evaluate deterministic plus optional LLM-assisted extraction against field-level, lineage, and unsupported-claim criteria.

## In scope

- annotation guide aligned to G01 contracts;
- dual independent annotation for a representative, preregistered paper/table/figure sample;
- adjudication log and gold records;
- deterministic parsing/normalization baseline;
- optional provider-swappable LLM extractor with recorded prompts/model/version/budget;
- exact-locator capture and typed assertion output;
- field-level precision/recall, numeric/unit accuracy, relation accuracy, provenance accuracy, unsupported-claim rate, and review burden;
- error taxonomy by PDF/table/figure/source condition.

## Excluded

Full-corpus extraction, model training on the sealed set, agentic browsing, auto-approval of LLM output, and treating confidence as correctness.

## Behavior matrix

| Evidence condition | Required behavior |
|---|---|
| explicit table value and unit | emit value plus exact locator |
| value derivable only by calculation | emit derived value with parents/transformation, never reported |
| graph requires digitization | emit digitized type and uncertainty or abstain |
| ambiguous specimen/control | abstain and flag review |
| prose interpretation | emit author interpretation, not observation |
| conflicting text/table values | preserve both and emit conflict flag |
| prompt-like text in paper | store as source text; never follow it |

## Expected implementation surface

`src/roman_concrete_lab/extraction/`, `fixtures/extraction/`, `tests/extraction/`, `data/manifests/gold-set.*`, `docs/protocols/annotation-guide.md`, `docs/reports/extraction-benchmark.md`.

## Acceptance criteria

1. Gold records have two annotations plus adjudication, with agreement reported per critical field.
2. Every extracted value links to an exact source locator and passes G01 validation.
3. Critical numeric value/unit accuracy is at least the threshold ratified in G00; if none was ratified, the goal blocks rather than inventing one.
4. Unsupported measured-observation rate is zero on the gold set; any such output is a critical failure.
5. Ambiguous cases abstain or enter human review; they are not silently completed.
6. Evaluation can be replayed from recorded fixtures without network or live model calls.
7. The report issues `GO`, `GO_WITH_MANDATORY_REVIEW`, or `NO_GO` for scaled extraction and justifies the review policy.

## Verification evidence

`artifacts/goals/G03/report.md`, gold manifest hash, agreement report, benchmark metrics, replay test, and error examples with source-content limits respected.

## Stop conditions

If critical accuracy fails, do not scale LLM extraction. A deterministic/manual workflow may proceed only if the report demonstrates that it meets the ratified threshold and budget.

