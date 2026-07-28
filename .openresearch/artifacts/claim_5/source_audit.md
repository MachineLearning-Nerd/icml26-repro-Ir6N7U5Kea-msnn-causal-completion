# Claim 5 source and quantifier audit

Primary paper source:
`https://ar5iv.labs.arxiv.org/html/2603.11942`, retrieved 2026-07-28 with an
explicit User-Agent, SHA-256
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.
Relevant locations are Section 5.1, Tables 2–3, and Appendix B.

Section 5.1 states that, across the MCAR and both MNAR settings, MSNN
consistently has substantially higher feasible ratios and that MRE is reduced
by a factor of two to three for all treatment levels. The claim imported by
the judge further summarizes Tables 2–3 as MSNN attaining 3–26% feasible rates
versus under 5% for SNN.

The paper's own MNAR cells are:

| lambda | Method | Low FR/MRE | Medium FR/MRE | High FR/MRE |
|---:|---|---:|---:|---:|
| 0.05 | SNN | 0.19 / 0.349 | 0.38 / 0.390 | 4.17 / 0.351 |
| 0.05 | MSNN | 3.13 / 0.117 | 3.26 / 0.114 | 4.52 / 0.106 |
| 0.02 | SNN | 9.57 / 0.366 | 11.70 / 0.379 | 22.66 / 0.383 |
| 0.02 | MSNN | 26.96 / 0.129 | 33.88 / 0.135 | 54.16 / 0.118 |

Thus the actual MSNN FR range is 3.13–54.16%, SNN reaches 22.66%, and three
of six displayed SNN/MSNN error ratios exceed 3. The literal imported range
and the paper's “two to three ... for all” statement are contradicted by the
source table before considering reproduction noise.

Section 5.1 defines MRE as the feasible-entry mean of
`abs((prediction-truth)/truth)`. The pinned author repository
`https://github.com/XiaoxiangRdM/MixedSNN` at commit
`12bd881f82a93cd223989a6a8cd082a3dc9a0e47` instead reports
`mean(abs(prediction-truth))/treatment_scale`.

Appendix B says that MNAR simulation takes the absolute value of every
ground-truth entry. That interpretation exactly reproduces the reported
treatment proportions:

- lambda 0.05: 1.30%, 1.49%, 2.50%;
- lambda 0.02: 3.54%, 3.76%, 4.59%.

The current released experiment calls `signal_matrix_positive`, which takes
absolute values of the latent factors separately. At the same seeds it yields
approximately 0.02–0.04% for lambda 0.05 and 0.29–0.37% for lambda 0.02, so
it cannot be the DGP that produced the paper tables. The formal route uses the
paper-stated absolute-entry construction and records the released-code route
as a drift audit.

Pinned author-source SHA-256 values:

- `experiments/estimation_mnar.py`:
  `00a22be08101313e7214a64798b330470bb462eb5f7c20ed5af2c488c4c47c72`;
- `src/utils/generate_synthetic_multitreat_data.py`:
  `f38ccacdfeebb6f82c00e3ed2549573142bda64b27b53e91d4fd0c2462320d11`;
- `src/utils/save_results.py`:
  `b3ec4f3e98511cfd60ba318d56119b1e2ba619c132bf9ef004841aaaacfd6570`;
- `scripts/syn_mnar.sh`:
  `e4b62934338ee2cdfd0b5e3bda038ba7020cfc555d846f7faaab1d838e58d46d`.
