# Claim 6 source audit

Source: `https://ar5iv.labs.arxiv.org/html/2603.11942`, retrieved
2026-07-28 with an explicit browser User-Agent, SHA-256
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.

Anchors: Assumption 2.5 `#S2.Thmtheorem5`; Section 3.2 weighted mixed
anchors; Algorithm 2 `#alg2`; Algorithm 3 `#alg3`; Appendix B simulation
details.

For target `(i,j,d)`, Algorithm 3 defines
`B_ab=1{D_ab=D_ib, D_aj=d, a!=i, b!=j}`. Section 3.2 additionally requires
the target-row treatment `D_ib=d(b)` to be observed, so every selected edge
must satisfy `D_ab=D_ib=d(b)!=0` while every anchor row satisfies `D_aj=d`.
Algorithm 2 weights each anchor and query column by `w(b,d(b))`, computes a
truncated SVD, forms the synthetic coefficients, and takes their inner product
with the same-treatment target column.

Appendix B fixes matrix shape 300x100, rank 3, relative noise 0.001, treatment
scales 1/5/25/625, MCAR probabilities 0.01/0.025/0.05/0.8 plus 0.115 missing,
`K=1`, and ten repetitions. It omits factor distributions, seeds, numerical
tolerances, and the `maxBiclique` objective/tie-break.
