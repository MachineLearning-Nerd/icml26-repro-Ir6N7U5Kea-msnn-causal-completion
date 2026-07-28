# Claim 6 — full-scale noisy mixed-anchor construction

**Current verdict: VERIFIED.** This supersedes the historical noise-free toy
check. The exact construction in Algorithms 2–3 was tested at the paper's
300x100 scale with rank 3, relative noise 0.001, low-treatment probability
0.01, and ten deterministic seeds.

## Exact claim and assumptions

For target `(i,j,d)`, every selected mixed-anchor edge must satisfy
`D_ab=D_ib=d(b)!=0`, and every selected row must preserve `D_aj=d`. The weighted
anchor columns may span treatment levels because Assumption 2.5 shares the
latent row factor across treatment-specific potential-outcome matrices.

The [source audit](../../../.openresearch/artifacts/claim_6/source_audit.md)
pins the paper HTML hash and exact anchors. The
[claim contract](../../../.openresearch/artifacts/claim_6/claim_contract.json)
states every fail-closed requirement.

## Direct evidence

| Quantity | Observed |
|---|---:|
| Seeds / target searches | 10 / 400 |
| Selected cliques passing every invariant | 382 / 382 |
| Corrupted-edge controls rejected | 382 / 382 |
| Genuinely mixed-treatment cliques | 26 / 382 (6.806%) |
| Rank-3 estimable targets | 215 |
| Shared-factor noisy scaled MAE | 0.003497 |
| Assumption-2.5-violating scaled MAE | 2.232891 |
| Control/valid error ratio | 638.4x |

The complete per-seed counts and exact floating-point results are inline in
[raw_result.json](../../../.openresearch/artifacts/claim_6/raw_result.json).

## Executable verification

- [Formal generator](../../../repro/claims/claim6_algorithm/experiment.py)
- [Fail-closed verifier](../../../repro/claims/claim6_algorithm/verifier.py)
- [Independent reconstruction](../../../repro/claims/claim6_algorithm/independent_checker.py)
- [Checker output](../../../.openresearch/artifacts/claim_6/checker_output.txt)
- [Negative-control output](../../../.openresearch/artifacts/claim_6/negative_control_output.txt)
- [Method](../../../.openresearch/artifacts/claim_6/method.md)
- [Exact command, environment, CPU and runtime](../../../.openresearch/artifacts/claim_6/environment.md)
- [Limitations and deviations](../../../.openresearch/artifacts/claim_6/limitations.md)

The independent checker separately reconstructs all RNG streams, incidence
matrices, exact bicliques, weighted SVD estimates, and aggregates. Its mutation
selects treatment-2 anchor rows for a treatment-1 target and must exit nonzero
with the target-treatment invariant diagnosis. Every cumulative run regenerates
both results.
