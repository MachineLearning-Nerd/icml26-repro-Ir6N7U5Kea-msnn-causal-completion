# Claim 5 command and environment

Fixed inherited command:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

- Formal run: `afc2ec12-c40a-4402-8ed2-4bbb15e1f13f`
- Git SHA: `59feea01de004bbbfbc78f0755cf09f3be2def76`
- Backend/flavor: Hugging Face `cpu-upgrade`
- Official allocation: 8 vCPU, 32 GB RAM
- Container-visible logical CPUs: 64
- Claim 5 process workers: 1
- Fixed container image:
  `ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`
- Python: 3.12 from the repository `.python-version`
- Environment: repository-level `.venv`, `uv run --frozen`, committed
  `pyproject.toml` and `uv.lock`
- NumPy: 2.5.1
- Claim 5 certificate runtime: 0.279163 seconds
- Claim 5 verifier runtime: 0.123628 seconds
- Cumulative formal runtime: 705 seconds
- Formal log SHA-256:
  `a1919fd73ab9ccb5e74206b496c1824b0fc42733d588e8db3a194a18942830f6`

The certificate is a one-process task, but the unchanged cumulative command
also reruns multi-process and uncertain-runtime checks from Claims 1, 4, and 6;
therefore the formal run used HF `cpu-upgrade`, not local CPU.

Evaluator-visible cumulative freeze:

- run `5f17a7bf-5a73-428c-8f3d-54cf844cd48d`
- Git SHA `b99cefc0f99bf42b8397594b2e2de49d4c209014`
- cumulative wall time: 688 seconds (11m28s)
- certificate runtime: 0.287237 seconds
- verifier runtime: 0.156670 seconds
- actual allocation: HF `cpu-upgrade`, 8 vCPU / 32 GB; 64 logical host CPUs
  visible; Claim 5 used one process
