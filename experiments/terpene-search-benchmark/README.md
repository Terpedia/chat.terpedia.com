# Terpene molecule-search proxy benchmark

This is a reproducible **proxy experiment**, not a protein-docking result. It
compares two search policies against the same deterministic, hidden RDKit-based
score landscapes:

1. `naive_random`: uniformly samples molecules from the candidate library.
2. `diversity_evolution`: spends the same number of scoring calls, but exploits
   high-scoring chemical neighborhoods while preserving multiple fingerprint
   niches.

Both policies use the same terpene-derived library, validity filter, scoring
budget, and final diversity selector. Eight proxy target/antitarget tasks and
five paired random seeds are used by default.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python benchmark.py --output results
```

The command writes `runs.csv`, `summary.json`, and `REPORT.md`. For a quick
smoke test, use `--library-size 1500 --evaluation-budget 400 --repeats 2`.

## Connecting the private scorer

`SearchResult` and the two search functions deliberately accept a scorer with
the shape `score(smiles) -> float`. Replace `ProxyTask.score` with the client's
batched target/antitarget callback while retaining the paired seeds, time limit,
validity checks, and output-set evaluation.

Do not describe these scores as binding, docking, or private-harness results.
They establish that the implementation and A/B protocol work; only the
client's harness can establish a real protein-target improvement.
