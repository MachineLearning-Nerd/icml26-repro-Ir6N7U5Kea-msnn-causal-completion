# Claim 3 command and environment

Fixed project command:

`uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py`

Python `3.12.*`, NumPy `2.5.1`, committed `uv.lock`, and pinned image
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

The verifier prints Git SHA, visible logical CPU count, platform, exact-symbolic
seed declaration, and measured verifier runtime to the captured run log.

Formal run provenance:

- run `92a2a72f-4845-4b14-b85a-f86549a0cded`
- Git SHA `15488a94a06ac8a58213224b49014b1901efc7f3`
- pre-run core estimate: one core for this symbolic certificate, but uncertain
  cumulative-suite runtime
- selected and actual allocation: HF `cpu-upgrade`, 8 vCPU / 32 GB
- container-visible logical CPUs: 64
- verifier runtime: 0.074451 seconds
- cumulative wall time: 223 seconds (3m43s)
- deterministic seed: `none_exact_symbolic`
