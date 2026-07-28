# Claim 4 command and environment

Fixed command inherited by every experiment:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Environment: repository `.venv`, Python 3.12, `uv.lock`, NumPy 2.5.1, and image
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

NetworkX-order evidence run:

- experiment `88f8524d-99b3-4fb4-a39c-2cddcf67271b`
- run `ac16ab19-ebe2-4d47-a37b-168d79ec7851`
- Git SHA `159ad67c5bcfd5cc26af91f9dd165140fce99ca7`
- estimated and selected workers: 8
- official HF allocation: `cpu-upgrade`, 8 vCPU / 32 GB
- container-visible logical CPUs: 64
- Claim 4 generator runtime: 875.271385 seconds
- formal cumulative run duration: 1,933 seconds

Lexicographic sensitivity run:

- experiment `2c315245-56a8-4584-a2a7-19ccb65bdc89`
- run `1f2b794c-e990-498d-8037-8a082bc01eb8`
- Git SHA `d2db042354ef8f0fa6933f0ce548724842d6292f`
- same HF allocation and eight workers
- Claim 4 generator runtime: 89.14188 seconds
- formal cumulative run duration: 271 seconds

Current strict evidence freeze:

- run `3d5c38e8-0f54-4614-a1c8-22f25df79b42`
- Git SHA `b88906567b8c0fa21c1f2b39fe5cc722adbef956`
- pre-run estimate and process cap: 8 workers, one thread each
- selected and actual allocation: HF `cpu-upgrade`, 8 vCPU / 32 GB
- container-visible logical CPUs: 64
- generator runtime: 571.115738 seconds
- verifier runtime: 0.128842 seconds
- cumulative wall time: 948 seconds (15m48s)
- seeds: 0–9
