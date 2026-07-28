# Claim 1 command, environment, and compute

Fixed command inherited unchanged by every experiment node:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Environment:

- Python constraint: `>=3.12,<3.13`; `.python-version` is `3.12`.
- Resolved runtime: CPython 3.12.12 and NumPy 2.5.1.
- `pyproject.toml` SHA-256:
  `9087d8468bfa21540d20899b939b405b0edb1b108ea4c7bf47454de2acd32e66`.
- `uv.lock` SHA-256:
  `002e7d7087a1e1481f53d51865943394057fb4e265d16a528cbf8279f7ae02f6`.
- `.python-version` SHA-256:
  `7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d`.
- Container image:
  `ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

Compute decision and actual allocation:

- Pre-run estimate: eight worker processes; runtime uncertain because every
  accepted claim is rerun cumulatively.
- Selected backend/flavor: Hugging Face `cpu-upgrade`.
- Official allocation: 8 vCPU and 32 GB RAM.
- Container-visible logical CPU count: 64.
- Worker cap: exactly 8; BLAS/OpenMP thread counts fixed to one per worker.
- Formal run: `78bb18c2-0c2a-4731-b79a-e0a625546591`.
- Formal run Git SHA:
  `4b4d33eba37072eb85d738a8ecf91282c9331888`.
- Formal cumulative runtime: 667 seconds (11m07s).
- Claim 1 generator runtime inside that run: 0.439259 seconds.
- Seed rule: `1000003 + 10000*K + repetition`.

The local machine performed only short one-core syntax, JSON, extraction, and
smoke checks. It did not run the formal multi-process experiment.
