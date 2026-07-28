# Claim 4 — Table 1 low-treatment result

**Current verdict: FALSIFIED.** The exact author-scale run reproduces the MSNN
feasible rate and the number placed in the table, but the table number is not
the MRE formula defined by the paper.

## Headline evidence

| Quantity | Paper | Observed |
|---|---:|---:|
| MSNN feasible rate | 4.69 ± 1.11% | 4.689333 ± 1.114224% |
| MSNN value labeled MRE | 0.0391 ± 0.0109 | 0.03908573 ± 0.01090279 using released-code normalized MAE |
| MSNN paper-defined entrywise MRE | 0.0391 ± 0.0109 | **0.25248262 ± 0.11621787** |
| SNN feasible rate | 0.03 ± 0.00% | 0.015667 ± 0.019941% |
| SNN finite-only released-code error | 0.806 ± 0.240 | 0.805548 ± 0.239593 |

The [source audit](../../../.openresearch/artifacts/claim_4/source_audit.md)
shows that Section 5.1 defines mean per-entry
`abs((prediction-truth)/truth)`, while the released code divides mean absolute
error by the treatment scale. The same predictions were evaluated under both
formulas. This is a direct metric contradiction, not a tolerance choice.

## Exact protocol and raw seed data

The run uses 300x100 matrices, rank 3, relative noise 0.001, low-treatment
probability 0.01, all 30,000 targets, and seeds 0–9.

| Seed | MSNN FR % | Code normalized MAE | Paper MRE |
|---:|---:|---:|---:|
| 0 | 6.053333 | 0.03119599 | 0.14611820 |
| 1 | 6.206667 | 0.03303353 | 0.16582375 |
| 2 | 4.046667 | 0.04891254 | 0.25054092 |
| 3 | 5.300000 | 0.03771685 | 0.21990690 |
| 4 | 4.496667 | 0.03182434 | 0.14530843 |
| 5 | 4.373333 | 0.03264826 | 0.46623415 |
| 6 | 3.633333 | 0.04494634 | 0.34264536 |
| 7 | 5.766667 | 0.02478228 | 0.20691897 |
| 8 | 4.223333 | 0.04401528 | 0.16541676 |
| 9 | 2.793333 | 0.06178188 | 0.41591272 |

[Download strict raw JSON](../../../.openresearch/artifacts/claim_4/raw_result.json).

## Independent checks and controls

- [Formal generator](../../../repro/claims/claim4_table1/experiment.py)
- [Fail-closed verifier](../../../repro/claims/claim4_table1/verifier.py)
- [Independent aggregate/formula checker](../../../repro/claims/claim4_table1/independent_checker.py)
- [Checker output](../../../.openresearch/artifacts/claim_4/checker_output.txt)
- [Metric-substitution negative control](../../../.openresearch/artifacts/claim_4/negative_control_output.txt)
- [Claim contract](../../../.openresearch/artifacts/claim_4/claim_contract.json)
- [Method](../../../.openresearch/artifacts/claim_4/method.md)
- [Exact command, environment, CPU and runtime](../../../.openresearch/artifacts/claim_4/environment.md)
- [Limitations](../../../.openresearch/artifacts/claim_4/limitations.md)

The exact NetworkX-order solver passes all 673 exhaustive finite-domain cases.
A separate 927-case comparison with the lexicographic solver finds 229
different tied choices but identical objectives. The mutation substitutes the
released-code metric for the paper metric and exits nonzero.

The fixed command is:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

The formal NetworkX route ran at Git SHA
`159ad67c5bcfd5cc26af91f9dd165140fce99ca7` on HF `cpu-upgrade` (officially
8 vCPU/32 GB; 64 logical CPUs container-visible), using exactly eight workers.
The Claim 4 generator took 875.271385 seconds; the cumulative run took 1,933
seconds.
