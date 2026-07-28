# Claim 3 command and environment

Fixed project command:

`uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py`

Python `3.12.*`, NumPy `2.5.1`, committed `uv.lock`, and pinned image
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

The verifier prints Git SHA, visible logical CPU count, platform, exact-symbolic
seed declaration, and measured verifier runtime to the captured run log.
