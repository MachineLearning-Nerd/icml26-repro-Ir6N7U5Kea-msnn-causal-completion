# Claim 6 generator method

Rows and base columns are independent unit-normalized Gaussian vectors, making
every noiseless inner product lie in `[-1,1]`; treatment scaling therefore
satisfies the paper's bounded-outcome assumption. Noise standard deviation is
`f(d)*0.001`, satisfying the stated relative sub-Gaussian scale.

For each low-treatment target, the exact Algorithm 3 incidence matrix is built.
Because low-treatment candidate rows are sparse, every nonempty candidate-row
subset is enumerated and paired with all common neighboring columns. The chosen
biclique maximizes edge count, then vertex count, with deterministic index
tie-breaking. This is an exact implementation of one explicit `maxBiclique`
objective; the paper leaves that objective unspecified.

Algorithm 2 uses `K=1`, rank-3 truncated SVD, and inverse treatment-scale
weights. A paired control redraws independent row factors for each treatment,
violating only Assumption 2.5. A graph control appends one known non-edge to
each selected clique; the invariant audit must reject it.
