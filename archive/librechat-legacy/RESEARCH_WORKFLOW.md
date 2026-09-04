# Terpedia research chat workflow

The `terpedia/research` model is the chat entry point for evidence-graded target-fishing and docking analysis.

It requires the assistant to:

- Preserve chemical and protein identifiers, provenance, versions, retrieval dates, checksums, missing records, and failures.
- Treat target-fishing consensus as hypothesis generation rather than binding evidence.
- Distinguish experimental evidence, source-label agreement, and computational prediction.
- Treat docking scores as ranking heuristics rather than affinity measurements.
- Require receptor-ensemble sensitivity, repeated seeds, native-ligand redocking, active/decoy controls, and rank stability before calling a docking result validated.
- End analyses with uncertainty, limitations, and a falsifiable next step.

The model is exposed through `api.terpedia.com` and appears in LibreChat after the endpoint configuration is reloaded.
