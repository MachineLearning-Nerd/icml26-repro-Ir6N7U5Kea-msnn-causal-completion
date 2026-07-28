# Claim 2 command and environment

Fixed project command:

`uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py`

Pinned inputs: Python `3.12.*`, NumPy `2.5.1`, `uv.lock` revision 3.

Pinned run image:
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

Formal compute is Hugging Face `cpu-upgrade` (8 vCPU, 32 GB). The exact proof
checker is single-process and expected to use one CPU core; the cumulative
historical regression dominates runtime.

The verifier prints the checked-out Git SHA, logical CPU allocation, platform,
deterministic-seed declaration (`none_exact_symbolic`), and its measured runtime
directly into the captured run log.

Formal run provenance:

- run `6411f20e-e068-4a91-a309-6fa6c59e3d6a`
- Git SHA `8e4d33cb954fa5f647008e7c9a4db81a68d32731`
- pre-run core estimate: one core for this symbolic certificate, but uncertain
  cumulative-suite runtime
- selected and actual allocation: HF `cpu-upgrade`, 8 vCPU / 32 GB
- container-visible logical CPUs: 64
- verifier runtime: 0.148996 seconds
- cumulative wall time: 271 seconds (4m31s)
- deterministic seed: `none_exact_symbolic`
