# Claim 5 evaluation

## Verdict

**FALSIFIED** for the exact imported conjunction:

> Across MNAR Tables 2–3, MSNN consistently attains 3–26% feasible rates
> versus under 5% for SNN, with 2–3x error reductions across treatment levels.

The pinned paper tables instead give:

- MSNN feasible-rate range: 3.13–54.16%;
- maximum SNN feasible rate: 22.66%;
- displayed SNN/MSNN error ratios:
  2.982906, 3.421053, 3.311321, 2.837209, 2.807407, 3.245763;
- ratios outside the closed 2–3 interval: 3 of 6.

Any one contradiction falsifies the conjunction. These values come from every
displayed Tables 2–3 cell, not from a selected simulation tolerance.

## Machine checks

- Independent strict checker: PASS; 20/20 lambda/seed DGP records
  reconstructed and every source aggregate recomputed.
- Source-range mutation: FAIL as intended, exit 1.
- Metric-definition substitution: FAIL as intended, exit 1.
- Appendix-B absolute-entry DGP: all six displayed treatment-assignment means
  and standard deviations reproduced after paper rounding.
- Current released positive-factor DGP: does not reproduce those proportions.
- Cumulative suite: Claims 1–6 all emit their accepted VERIFIED/FALSIFIED
  markers; legacy controls hold.

## Scope

This result does not falsify the broader qualitative observation that MSNN has
higher feasible rates than SNN in the displayed cells; all six cells do.
It falsifies the exact imported numerical ranges and universal 2–3x wording.

Two full 60-task imputation attempts were canceled after 1h48m (30/60) and
1h42m (47/60) because exact author-order clique enumeration had pathological
dense tails. Their partial metrics are rejected and are not used. The source
certificate is the current verifier and supersedes those incomplete routes.
