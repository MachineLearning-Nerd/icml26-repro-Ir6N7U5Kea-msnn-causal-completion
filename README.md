# Claim-by-claim reproduction: MSNN causal matrix completion

This CPU-only campaign audits all six judged claims from
[*Causal Matrix Completion under Multiple Treatments via Mixed Synthetic
Nearest Neighbors*](https://arxiv.org/abs/2603.11942). The fixed cumulative
suite verifies the exact Corollaries 4.10 and 4.11 and the paper-scale
mixed-anchor construction. It falsifies the universal theorem transfer under
the paper's displayed assumptions, the Table 1 metric label, and the imported
Tables 2–3 range summary. “Falsified” here means a reproducible contradiction
of the exact audited statement—not a claim that MSNN has no practical value.

The sharpest empirical discrepancy is Table 1: the paper reports MSNN MRE
`0.0391`; the released implementation reproduces `0.0390857` only as
normalized MAE, while the paper's stated entrywise MRE on the same predictions
is `0.252483`. At the same time, the paper-scale mechanism test passes all
`382/382` mixed-anchor invariants and rejects all `382/382` corrupted controls.

All formal work used Hugging Face `cpu-upgrade` (8 allocated vCPU, 32 GB),
with deterministic seeds and a locked `uv` environment. The exact source
certificates for Claims 2, 3, and 5 are not downscaled. Claims 4 and 6 use the
paper's 300×100, rank-3, ten-seed configurations. Claim 1 uses an
assumption-satisfying asymptotic sequence and finite calibration at
`N ∈ {16,81,256}`; finite computation corroborates the symbolic
counterexample rather than proving it.

[Read the illustrated report](reports/reproduction-campaign/report.md) ·
[Open the tutorial notebook](notebooks/msnn_reproduction.py) ·
[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/blob/master/notebooks/msnn_reproduction.py)

## Experiment log

The command below is copied verbatim from every formal experiment status.
This repository uses `master` as its publication branch and has no separate
`main` branch; `master` is presentation-only and was never launched as an
experiment.

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `master` (publication “main”) | Public report, notebook, and evaluator-visible release | Not run as an experiment (publication surface) | Presentation-only; mirrors frozen evidence | N/A |
| [`orx/claim-1-evaluator-visible-proof-evidence`](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/tree/orx/claim-1-evaluator-visible-proof-evidence) | Theorems 4.5–4.6 premise audit and counterexample | `uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py` | Claim 1 FALSIFIED | HF `cpu-upgrade`; 8 vCPU |
| [`orx/exact-corollary-4-10-asymptotic-ratio-certificat`](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/tree/orx/exact-corollary-4-10-asymptotic-ratio-certificat) | Exact Corollary 4.10 certificate | `uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py` | Claim 2 VERIFIED | HF `cpu-upgrade`; 8 vCPU |
| [`orx/exact-corollary-4-11-sparse-rich-exponent-certif`](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/tree/orx/exact-corollary-4-11-sparse-rich-exponent-certif) | Exact Corollary 4.11 certificate | `uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py` | Claim 3 VERIFIED | HF `cpu-upgrade`; 8 vCPU |
| [`orx/claim-4-strict-evidence-and-metric-falsification`](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/tree/orx/claim-4-strict-evidence-and-metric-falsification) | Paper-scale Table 1 metric audit | `uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py` | Claim 4 FALSIFIED | HF `cpu-upgrade`; 8 vCPU |
| [`orx/freeze-and-independently-check-claim-6-evidence`](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/tree/orx/freeze-and-independently-check-claim-6-evidence) | Paper-scale noisy mixed-anchor mechanism | `uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py` | Claim 6 VERIFIED | HF `cpu-upgrade`; 8 vCPU |
| [`orx/claim-5-evaluator-visible-source-evidence`](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/tree/orx/claim-5-evaluator-visible-source-evidence) | Exact Tables 2–3 source certificate and cumulative suite | `uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py` | Claim 5 FALSIFIED; all six claims regress | HF `cpu-upgrade`; 8 vCPU |

## Reproduce

```sh
uv sync --frozen
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

The suite regenerates evidence and exits nonzero if an accepted verifier,
independent checker, or negative control fails. The lockfile pins Python 3.12
dependencies; formal runs use the immutable
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`
image.

## Original project description

ICML 2026 Agent Reproduction Challenge. OpenReview Ir6N7U5Kea. arXiv
2603.11942. Clean-room reproduction of standard SNN and Mixed Synthetic
Nearest Neighbors (MSNN) for multi-treatment causal matrix completion.
