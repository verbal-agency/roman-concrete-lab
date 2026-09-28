# GP1 — Candidate evidence and hypothesis dossier

**Status:** proposed  
**Dependencies:** G00 `PRELAB_REPLICATION` track; complete paired G-1 decision with at least one `LAB_CANDIDATE_PLAUSIBLE` candidate  
**Advances:** converts the public evidence audit into a falsifiable, lab-readable candidate dossier without claiming material performance

## Objective

Freeze the candidate families, evidence claims, uncertainties, and competing hypotheses that a qualified laboratory would need before reviewing a Roman-inspired concrete study.

## In scope

- reconcile the material-candidate ledger with the source and study-family ledgers;
- produce one dossier per candidate, including material/process identity, comparator, endpoint, supporting locators, and missing fields;
- separate measured observations, author interpretations, curator interpretations, and proposed hypotheses;
- define rival hypotheses and the observations that would distinguish them;
- identify which candidates are candidates for lab review versus contextual or transfer evidence;
- preserve derivative lineages and conflicting results.

## Excluded

Exact recipe invention, unverified proportions, physical mixing, hazardous handling instructions, partner contact, predictive modeling, and claims that any candidate is superior.

## Acceptance criteria

1. Every candidate has a stable ID, supporting record IDs, exact locators, material/process identity status, comparator status, endpoint status, and explicit blockers.
2. Every hypothesis has a named intervention, comparator, measurable outcome, applicable domain, and at least one rival prediction.
3. No candidate is promoted from provisional to approved without the human adjudication and lab-safety gates recorded in G-1/G00.
4. A deterministic replay reconstructs candidate counts and statuses from the frozen ledgers.
5. The dossier labels all formulation and performance claims as reported, derived, proposed, or unresolved.

## Expected implementation surface

`data/processed/literature-sufficiency-material-candidates.jsonl`, `data/processed/candidate-hypotheses.jsonl`, `docs/reports/material-candidate-dossier.md`, `artifacts/goals/GP1/`.

## Authority boundaries

Network access is read-only and limited to lawful sources already permitted by G-1. No lab, external message, model call, or physical execution is authorized.

## Verification evidence

Candidate-ledger replay, claim/locator audit, hypothesis matrix, and `artifacts/goals/GP1/report.md`.

## Stop conditions

Stop if no candidate has inspectable material identity and a falsifiable measurement path, or if a material interpretation would require inventing unreported formulation details.
