# Claim 4 generator source audit

Paper HTML: `https://ar5iv.labs.arxiv.org/html/2603.11942`, retrieved
2026-07-28 with explicit User-Agent, SHA-256
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.
Anchors: Table 1 `#S4.T3`, Section 5.1 `#S5.SS1`, Appendix B `#A2`.

Author repository: `https://github.com/XiaoxiangRdM/MixedSNN`, retrieved
2026-07-28, pinned commit
`12bd881f82a93cd223989a6a8cd082a3dc9a0e47` (2026-05-22T00:19:57+08:00).
Relevant file hashes:

- `experiments/estimation_mcar.py`: `32bf78f96c9de84333e24a52f7db32a75369ffbdd9043d271f69f5f4b38fae35`
- `src/utils/generate_synthetic_multitreat_data.py`: `f38ccacdfeebb6f82c00e3ed2549573142bda64b27b53e91d4fd0c2462320d11`
- `src/utils/msnn.py`: `c4bcbd77ed10b8d0ea6654f0d0ec2e9f98d1531389aa885e3b4ffda462aaab21`
- `src/utils/snn.py`: `753b5594bf85345bae6b0d19c010705c3a3cbf17a2f599f517871017c86b954e`
- `src/utils/save_results.py`: `b3ec4f3e98511cfd60ba318d56119b1e2ba619c132bf9ef004841aaaacfd6570`

The released scripts establish seeds 0–9, all-entry evaluation, unit-normalized
Gaussian factors, relative noise, balanced-biclique score, universal PCR rank,
and feasibility thresholds 0.1. The paper alone omits these.

Metric discrepancy: Section 5.1 defines MRE as the mean of per-entry
`abs(pred-truth)/abs(truth)`. The released `compute_errors` instead reports
`mean(abs(pred-truth))/treatment_scale`; `syn_final_results.py` uses that
normalized MAE for the table. This generator reports both.
