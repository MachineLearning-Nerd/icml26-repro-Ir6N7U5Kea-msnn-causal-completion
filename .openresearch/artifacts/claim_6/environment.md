# Claim 6 command, environment, and runtime

Fixed command inherited by every node:

```text
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Environment: repository-level `.venv`, Python 3.12, `uv.lock`, NumPy 2.5.1.
Container image:
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

Generator branch SHA: `afc631917f7bbee635286bdd12bae69e892beaf7`.
Generator run: `c1943e83-3fff-440a-bd0c-10a7be105370`.
Backend/flavor: Hugging Face `cpu-upgrade`, officially 8 vCPU/32 GB; the
container reported 64 visible host logical CPUs. Pre-run algorithm estimate
was at most two CPU cores and seconds, but the cumulative runtime was uncertain.
Measured generator runtime was 0.335675 seconds; full fixed command was 3m47s.
Approximate compute charge at $0.03/hour: $0.0019.
