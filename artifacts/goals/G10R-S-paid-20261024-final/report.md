# G10R-S paid rerun — 2026-10-24

## Outcome

`DO_NOT_ESCALATE_ACTIVE_SOCIETY`

The post-G10R-S paired A1 versus A2-M comparison completed across all four
sealed cases under the frozen manifest and aggregate $25 cap. Recorded actual
model spend was `$0.03953781`. No critical authority, provenance, or rights
failure was recorded.

| Case | A1 | A2-M | Gain | A2-M unique contribution |
|---|---:|---:|---:|---|
| S-ACTIVE-ACCESS | 0 | 0 | 0 | none |
| S-ACTIVE-LINEAGE | 0 | 0 | 0 | none |
| S-ACTIVE-SIM | 5 | 3 | -2 | one, not enough to offset the lower score |
| S-ACTIVE-TRANSFER | 0 | 0 | 0 | none |

Totals were A1 `5` versus A2-M `3`. The remediated society therefore did not
deliver a qualifying improvement over the same-budget single investigator.

The first attempt exposed and preserved a legal enum mismatch (`ABSTAIN` in the
proponent contract versus `ABSTAINED` in the evidence-bus contract). After that
boundary was repaired and a fresh Phase-A manifest was frozen, the complete
comparison ran successfully. The result is an adoption-grade negative signal
for this configuration, not evidence that the society architecture is
impossible.

Primary artifact: `run.json`. Earlier failed and partial attempts remain in
the sibling `G10R-S-paid-20261024/` and `G10R-S-paid-20261024-retry/`
namespaces.
