# Claim 5 — MNAR Tables 2–3 ranges

**Current verdict: FALSIFIED.** The literal range-and-ratio conjunction is
contradicted by the paper's own Tables 2–3. This is the current verification;
two incomplete full-imputation attempts are rejected and do not supply any
accepted metric.

## Exact source evidence

The source is the paper HTML retrieved on 2026-07-28:
`https://ar5iv.labs.arxiv.org/html/2603.11942`, SHA-256
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.
The audited anchors are Section 5.1, Table 2, Table 3, and Appendix B.

| λ | Method | Low FR / MRE | Medium FR / MRE | High FR / MRE |
|---:|---|---:|---:|---:|
| 0.05 | SNN | 0.19 / 0.349 | 0.38 / 0.390 | 4.17 / 0.351 |
| 0.05 | MSNN | 3.13 / 0.117 | 3.26 / 0.114 | 4.52 / 0.106 |
| 0.02 | SNN | 9.57 / 0.366 | 11.70 / 0.379 | 22.66 / 0.383 |
| 0.02 | MSNN | 26.96 / 0.129 | 33.88 / 0.135 | 54.16 / 0.118 |

Therefore:

- actual MSNN FR range = **3.13–54.16%**, not 3–26%;
- maximum SNN FR = **22.66%**, not under 5%;
- three of six displayed error-reduction ratios exceed 3.

| λ | Treatment | SNN MRE / MSNN MRE | Inside closed 2–3? |
|---:|---|---:|---|
| 0.05 | Low | 2.982906 | yes |
| 0.05 | Medium | 3.421053 | **no** |
| 0.05 | High | 3.311321 | **no** |
| 0.02 | Low | 2.837209 | yes |
| 0.02 | Medium | 2.807407 | yes |
| 0.02 | High | 3.245763 | **no** |

This falsifies the exact conjunction without choosing a simulation tolerance,
seed, or sample count. It does **not** claim that the broader qualitative
finding “MSNN improves feasible rates” is false; all six displayed cells favor
MSNN.

## Full ten-seed DGP audit

Appendix B says to take the absolute value of each ground-truth entry. That
route reproduces all six paper assignment proportions. The current author
release instead takes positive latent factors separately and does not.

| λ | Treatment | Paper absolute-entry, mean ± SD % | Released positive-factor, mean ± SD % |
|---:|---|---:|---:|
| 0.05 | Low | 1.2990 ± 0.0636 | 0.0230 ± 0.0110 |
| 0.05 | Medium | 1.4913 ± 0.0610 | 0.0187 ± 0.0119 |
| 0.05 | High | 2.4990 ± 0.0976 | 0.0437 ± 0.0186 |
| 0.02 | Low | 3.5443 ± 0.1182 | 0.2893 ± 0.0507 |
| 0.02 | Medium | 3.7597 ± 0.1227 | 0.2887 ± 0.0634 |
| 0.02 | High | 4.5923 ± 0.1076 | 0.3747 ± 0.0903 |

The audit uses 300×100 rank-three matrices, λ in {0.05, 0.02}, and seeds
0–9. It corroborates the source interpretation; it is not the logical basis
of the table-range falsification.

## Metric-definition audit

Section 5.1 defines feasible-entry mean
`abs((prediction-truth)/truth)`. The released result saver computes
`mean(abs(prediction-truth))/treatment_scale`. The raw certificate includes a
numerical witness where these formulas return 1.0 and 0.5 respectively.

## Reproducibility and controls

The fixed command is:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Current evidence-freeze run `5f17a7bf-5a73-428c-8f3d-54cf844cd48d` used Git
SHA `b99cefc0f99bf42b8397594b2e2de49d4c209014` on HF `cpu-upgrade` (official
8 vCPU/32 GB; 64 logical CPUs visible). Claim 5 used one process and took
0.287237 seconds; the cumulative run took 688 seconds.

- [Current source-certificate generator](../../../repro/claims/claim5_tables23/source_certificate.py)
- [Current fail-closed verifier](../../../repro/claims/claim5_tables23/verifier.py)
- [Independent checker](../../../repro/claims/claim5_tables23/independent_checker.py)
- [Strict raw JSON](../../../.openresearch/artifacts/claim_5/raw_result.json)
- [Formal raw log](../../../.openresearch/artifacts/claim_5/formal_run.log)
- [Checker output](../../../.openresearch/artifacts/claim_5/checker_output.txt)
- [Metric negative control](../../../.openresearch/artifacts/claim_5/negative_control_metric.txt)
- [Source-range negative control](../../../.openresearch/artifacts/claim_5/negative_control_source.txt)
- [Claim contract](../../../.openresearch/artifacts/claim_5/claim_contract.json)
- [Source audit](../../../.openresearch/artifacts/claim_5/source_audit.md)
- [Method](../../../.openresearch/artifacts/claim_5/method.md)
- [Exact environment and runtime](../../../.openresearch/artifacts/claim_5/environment.md)
- [Limitations and rejected attempts](../../../.openresearch/artifacts/claim_5/limitations.md)
- [Machine evaluation](../../../.openresearch/artifacts/claim_5/EVAL.md)

The independent checker reconstructs all 20 DGP records and every aggregate.
Changing the source ranges to the imported 26%/5% values exits 1. Replacing
the paper metric definition with the released formula also exits 1.
