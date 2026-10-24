# G10R-X activation request

## Status

`PHASE_A_READY_FOR_OWNER_ACTIVATION` is preparation only. It does not start
Phase B, construct a provider, open the network, read credentials, or spend
money.

## Frozen boundary

- Manifest ID: `G10R-X-fresh-phase-a-research-loop-wiring-v1`
- Manifest SHA-256: `sha256:8ddb3096705d3fbfa706361d93647574646d1c70e13f14987383a9c6e3d77b3c`
- Provider: `openai`, Responses API
- Model: `gpt-6-luna`
- Reasoning effort: `low`
- Store: `false`
- Source policy: `g10r-source-policy-1.0`, exact-host read-only GET-only, no credentials
- Per-treatment-case limits: `{"document_fetches": 4, "estimated_cost_usd": 25.0, "input_tokens": 80000, "output_tokens": 12000, "payload_bytes": 5000000, "queries": 12, "retained_sources": 24, "simulation_calls": 4}`
- Hard aggregate external-spend cap: `$25.00`
- Paid output namespace: `artifacts/goals/G10R-V/`

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

The owner must separately authorize G10R-V by naming this exact manifest ID and
hash, provider/model, read-only network permission, spend cap, and output
namespace. Completing or committing G10R-X is not activation.
