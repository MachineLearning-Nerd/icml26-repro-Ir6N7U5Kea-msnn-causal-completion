# Claim 2 — exact Corollary 4.10 certificate

**Current verdict: VERIFIED.** This page supersedes the historical proxy that
compared 11.5x/5.6x/1.4x finite feasible-indicator ratios.

## Exact claim and assumptions

Under Theorem 4.8's MCAR sparsity setting, for any entry `(i,j)`, treatment
`d`, and fixed positive anchor sizes `r,c`,

`E[K_MSNN(d)] / E[K_SNN(d)] = (1+o(1))
[sum_d'(p_d'/p_d)^(r+1)]^c`.

The complete numerical assumption audit and source anchors are in
[source_audit.md](../../../.openresearch/artifacts/claim_2/source_audit.md).
The retrieved paper HTML has SHA-256
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.

## Direct evidence

Dividing the two Theorem 4.8 leading terms cancels the common binomial factor:

`gamma^c p_d^r p_max^((r+1)c) / p_d^(rc+r+c)
 = gamma^c (p_max/p_d)^((r+1)c)
 = [sum_d'(p_d'/p_d)^(r+1)]^c`.

Raw result:

```json
{
  "claim_id": "claim_2",
  "evidence_type": "exact symbolic certificate plus independent checker",
  "identity": "E[K_MSNN(d)]/E[K_SNN(d)] = (1+o(1))*[sum_d'(p_d'/p_d)^(r+1)]^c",
  "negative_control_exit_code": 1,
  "verdict": "VERIFIED"
}
```

Download the [claim contract](../../../.openresearch/artifacts/claim_2/claim_contract.json),
[proof certificate](../../../.openresearch/artifacts/claim_2/proof_certificate.json),
and [raw result](../../../.openresearch/artifacts/claim_2/raw_result.json).

## Executable verification

- [Fail-closed verifier](../../../repro/claims/claim2_cor410/verifier.py)
- [Independent checker](../../../repro/claims/claim2_cor410/independent_checker.py)
- [Checker output](../../../.openresearch/artifacts/claim_2/checker_output.txt)
- [Negative-control output](../../../.openresearch/artifacts/claim_2/negative_control_output.txt)
- [Method](../../../.openresearch/artifacts/claim_2/method.md)
- [Exact command and environment](../../../.openresearch/artifacts/claim_2/environment.md)
- [Limitations](../../../.openresearch/artifacts/claim_2/limitations.md)

The negative control changes one exponent in the SNN term. The independent
checker exits 1 with the intended exponent-mismatch diagnosis. The cumulative
fixed command exits nonzero if the certificate, checker, raw result, or control
is altered.
