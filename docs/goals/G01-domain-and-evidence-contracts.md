# G01 — Define domain, evidence, provenance, and claim contracts

**Status:** proposed  
**Dependencies:** G00 complete  
**Advances:** prevents unlike materials, measurements, and claim types from being silently combined

## Objective

Implement versioned, machine-validatable contracts for the canonical entities and illegal-state behavior in `docs/research_program_v2.md` before any corpus data is ingested.

## In scope

- entities for Source, Study, Material, MixBatch, SpecimenGroup, Intervention, MeasurementProtocol, Measurement, Assertion, Hypothesis, and lineage edges;
- controlled enums for material class, environment, assertion type, value origin, review status, access/license class, and null reason;
- quantity representation with unit, uncertainty/dispersion, sample count, aggregation level, and censoring;
- provenance fields for source hash/version, exact locator, extractor, reviewer, timestamps, transformation lineage, and schema version;
- migration policy and canonical serialization;
- validation fixtures for positive, negative, contradictory, malformed, incomplete, and unsupported records;
- a data dictionary explaining scientific semantics.

## Excluded

Database selection, source retrieval, automated extraction, confidence prediction, graph algorithms, scientific comparability decisions, and model features.

## Expected implementation surface

`src/roman_concrete_lab/domain/`, `schemas/`, `fixtures/domain/`, `tests/domain/`, `docs/protocols/data-dictionary.md`, and a schema-version constant.

## Required invariants and illegal states

- Measurement values cannot exist without units or an explicit dimensionless declaration.
- Reported zero, not reported, not applicable, and not extracted are distinct.
- Derived/converted/imputed values require parent IDs and a transformation record.
- LLM/model/curator assertions cannot have assertion type `measured_observation`.
- A measurement cannot be attached directly to a paper without study, arm/specimen-group, and protocol context.
- Contradictory assertions may coexist and link to one another; ingestion never resolves them by overwriting.
- Every identifier is stable and content collisions fail loudly.
- Unknown enum values are rejected or preserved through an explicit extension mechanism; they are never coerced silently.

## Deterministic behavior examples

| Input | Expected result |
|---|---|
| reported `0 mL/min` | valid numeric zero |
| blank cell with reason `not_reported` | valid missing value |
| blank cell with no reason | validation error |
| LLM assertion marked measured | validation error |
| converted permeability without parent | validation error |
| two conflicting reported values with unique IDs | both retained plus conflict edge |
| same stable ID, different payload | collision error |

## Acceptance criteria

1. All named entities and enums have versioned schemas and data-dictionary entries.
2. Every required invariant has a named positive and negative test.
3. Fixtures round-trip to canonical serialization without semantic loss.
4. Malformed, contradictory, partial, and unsupported cases behave exactly as documented.
5. Schema version mismatch and migration-required states fail with actionable errors.
6. The contracts contain no database-, LLM-, or vendor-specific types.

## Verification evidence

`artifacts/goals/G01/report.md`, schema validation output, named invariant tests, fixture inventory, and a criterion-to-test table.

