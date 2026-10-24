# G10R-U activation request

## Status

`PHASE_A_READY_FOR_OWNER_ACTIVATION` is a preparation state only. It does not
start Phase B, create a provider client, or authorize a paid call.

## Frozen execution boundary

- Provider: `openai`, Responses API
- Model: `gpt-6-luna`
- Reasoning effort: `low`
- Store: `false`
- Source-policy version: `g10r-source-policy-1.0`
- Source-policy mode: exact-host, read-only, GET-only, no credentials
- Per-treatment-case limits: `{"document_fetches": 4, "estimated_cost_usd": 25.0, "input_tokens": 80000, "output_tokens": 12000, "payload_bytes": 5000000, "queries": 12, "retained_sources": 24, "simulation_calls": 4}`
- Hard aggregate external-spend cap: `$25.00`
- Declared simulation adapter: `SIMULATOR_UNAVAILABLE`; simulation output cannot earn empirical evidence credit

### Frozen hosts

- `api.crossref.org`
- `api.openalex.org`
- `biblio.ugent.be`
- `citeseerx.ist.psu.edu`
- `digibug.ugr.es`
- `digitalcommons.usu.edu`
- `docs.lib.purdue.edu`
- `doi.org`
- `dspace.ucacue.edu.ec`
- `dspace.uevora.pt`
- `ebuah.uah.es`
- `ecommons.udayton.edu`
- `fileserver-az.core.ac.uk`
- `heronjournal.nl`
- `journal.uitm.edu.my`
- `orca.cardiff.ac.uk`
- `papers.ssrn.com`
- `patents.google.com`
- `pmc.ncbi.nlm.nih.gov`
- `research.unl.pt`
- `researchportal.bath.ac.uk`
- `rosap.ntl.bts.gov`
- `shura.shu.ac.uk`
- `upcommons.upc.edu`
- `www.jstage.jst.go.jp`
- `www.nature.com`
- `www.repository.cam.ac.uk`

## Required activation

Before any paid execution, the owner must review this manifest and explicitly
authorize the separately defined Phase-B goal. That activation must confirm the
provider key, network permission, exact manifest ID, spend cap, and output
namespace. No activation is implied by this artifact, by the offline
`SOCIETY_RESEARCH_LOOP_READY` result, or by committing this file.
