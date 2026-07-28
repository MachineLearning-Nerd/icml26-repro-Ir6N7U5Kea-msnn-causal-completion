# Claim 4 source audit

Paper HTML: `https://ar5iv.labs.arxiv.org/html/2603.11942`, retrieved
2026-07-28 with an explicit User-Agent, SHA-256
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.
Relevant anchors are Table 1 (`#S4.T3`), Section 5.1 (`#S5.SS1`), and Appendix
B (`#A2`).

Section 5.1 defines

`MRE = mean_feasible(abs((prediction - truth) / truth))`.

The pinned public author repository is
`https://github.com/XiaoxiangRdM/MixedSNN` at commit
`12bd881f82a93cd223989a6a8cd082a3dc9a0e47`. Its `compute_errors` instead
calculates

`mean_feasible(abs(prediction - truth)) / treatment_scale`,

and `src/syn_final_results.py` places this normalized MAE in the table's MRE
column. The source file hashes and retrieval record are preserved in the
generator audit.

The exact paper protocol is 300 rows, 100 columns, rank 3, relative Gaussian
noise 0.001, treatment probabilities `(0.115, 0.01, 0.025, 0.05, 0.8)`, all
30,000 target entries, and seeds 0–9. Results are mean plus sample standard
deviation over those ten seeds. The released dependency list does not pin a
NetworkX version and NetworkX documents maximal-clique order as arbitrary.
