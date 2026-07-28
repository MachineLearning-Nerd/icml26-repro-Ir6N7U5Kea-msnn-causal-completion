# Claim 3 — exact Corollary 4.11 certificate

**Current verdict: VERIFIED.** This supersedes the historical
`11.5x > 5.6x > 1.4x` trend, which was not a test of either corollary ratio.

## Exact claim and assumptions

Under Theorem 4.8's MCAR sparsity setting, for sparse treatment `d` and a
richest treatment `d_max`,

`E[K_SNN(d)]/E[K_MSNN(d_max)]
= O(gamma^(-c)*(p_d/p_max)^(rc+r+c))`

and

`E[K_MSNN(d)]/E[K_MSNN(d_max)]
= O((p_d/p_max)^r)`.

The [source audit](../../../.openresearch/artifacts/claim_3/source_audit.md)
records all quantifiers, assumptions, the exact formulas, source anchors, and
the paper HTML SHA-256.

## Direct evidence

Specializing the Theorem 4.8 MSNN term at `p_d=p_max` gives
`common*gamma^c*p_max^(rc+r+c)`. Exact division yields the two displayed
ratios, so the complete scarcity exponent changes from `rc+r+c` to `r`.
Remark 4.12 summarizes the dominant change as quadratic `rc` to linear `r`.

```json
{
  "claim_id": "claim_3",
  "exact_exponents": {
    "msnn_sparse_to_rich": "r",
    "snn_sparse_to_rich": "r*c+r+c"
  },
  "negative_control_exit_code": 1,
  "verdict": "VERIFIED"
}
```

## Executable verification

- [Claim contract](../../../.openresearch/artifacts/claim_3/claim_contract.json)
- [Proof certificate](../../../.openresearch/artifacts/claim_3/proof_certificate.json)
- [Raw result](../../../.openresearch/artifacts/claim_3/raw_result.json)
- [Fail-closed verifier](../../../repro/claims/claim3_cor411/verifier.py)
- [Independent checker](../../../repro/claims/claim3_cor411/independent_checker.py)
- [Checker output](../../../.openresearch/artifacts/claim_3/checker_output.txt)
- [Negative control](../../../.openresearch/artifacts/claim_3/negative_control_output.txt)
- [Method](../../../.openresearch/artifacts/claim_3/method.md)
- [Environment](../../../.openresearch/artifacts/claim_3/environment.md)
- [Limitations](../../../.openresearch/artifacts/claim_3/limitations.md)

The negative control changes only the sparse MSNN exponent. The independent
checker exits 1 for the intended MSNN-ratio mismatch, and the cumulative fixed
command fails if any evidence check is weakened.

Formal run `92a2a72f-4845-4b14-b85a-f86549a0cded` used Git SHA
`15488a94a06ac8a58213224b49014b1901efc7f3` and completed in 223 seconds on
HF `cpu-upgrade` (8 vCPU/32 GB; 64 host logical CPUs visible). The exact
certificate uses no stochastic seed.
