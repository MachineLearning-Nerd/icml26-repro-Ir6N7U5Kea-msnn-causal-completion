# Claim 6 generator source audit

Paper source: ar5iv HTML for arXiv 2603.11942, retrieved 2026-07-28,
SHA-256 `f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.

Anchors: Assumption 2.5 `#S2.Thmtheorem5`; mixed-anchor conditions in Section
3.2; Algorithm 2 `#alg2`; Algorithm 3 `#alg3`; Appendix B simulation details.

Exact construction conditions for target `(i,j,d)` are
`D_ab=D_ib=d(b)!=0` for every selected row `a` and column `b`, and `D_aj=d`
for every selected row. Algorithm 3 forms the corresponding binary incidence
matrix and calls an abstract `maxBiclique`.

Appendix B fixes `m=300`, `n=100`, rank 3, relative noise 0.001, four treatment
scales `1,5,25,625`, MCAR probabilities `0.01,0.025,0.05,0.8` plus 0.115
unobserved, `K=1`, and ten repetitions. It does not define the latent-factor
distribution, normalization, seeds, feasibility tolerances, or the objective
and tie-breaking of `maxBiclique`.
