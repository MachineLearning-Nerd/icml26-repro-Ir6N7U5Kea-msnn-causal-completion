# NetworkX-order method

All DGP, PCR, feasibility, all-entry, seed, and metric details are identical to
the parent Claim 4 generator. Only equal-score biclique selection changes:

1. Build the author's two-part block graph with cliques within each partition.
2. Enumerate maximal cliques using the pinned NetworkX 3.6.1 algorithm.
3. Retain the first clique that strictly improves
   `min(number of rows, number of columns)`.
4. Compare its objective to the independent exhaustive solver on 673 complete
   finite-domain cases and a larger deterministic random suite.

This route tests whether the remaining SNN discrepancy is caused by arbitrary
equal-score clique order. It does not retune feasibility or numerical results.
