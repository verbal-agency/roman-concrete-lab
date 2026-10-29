# Proposal-machinery protocol

**Protocol version:** `g10r-af.1-proposal-machinery`

This boundary evaluates whether an investigation produces a reviewable
experiment proposal. It is not a debate scorer and it is not a material-result
or safety gate.

## Required proposal content

Each packet names the intervention or process, process-matched comparator,
primary endpoint, predicted observation, falsifier, discriminator, support
region, uncertainty, rival proposals, conflict sets, and action/dossier/portfolio
provenance. A packet can remain `PROPOSAL_INCOMPLETE` or `REVIEW_REQUIRED`; it
must not be padded with rhetorical language to become reviewable.

## Evidence and contradiction handling

Source edges remain typed as `SUPPORTED`, `CONTRADICTED`, `UNRETRIEVABLE`,
`METADATA_ONLY`, or `REVIEW_REQUIRED`. Supporting and contradictory edges are
retained together. A conflict set is not resolved by a vote, consensus, source
count, or viewpoint count. Pending and blocked sources may motivate a proposal
but earn no direct-evidence credit.

## Scoring boundary

The deterministic scorer awards only typed proposal components: completeness,
attributable support, contradiction retention, discriminator quality,
falsifiability, uncertainty preservation, and rival retention. Consensus,
answer length, rhetoric, viewpoint count, and agent count are recorded only as
ignored metadata and receive zero credit.

## Authority

G10R-AF is offline-only. It makes no model or network calls, reads no
credentials, promotes no evidence, approves no safety or laboratory action,
and cannot activate Phase B. A later live proposal evaluation must name the
exact G10R-AE manifest and receive separate owner/provider/network activation.
