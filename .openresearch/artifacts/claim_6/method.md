# Claim 6 method

The formal generator used deterministic seeds 0–9 and 40 target entries per
seed. Unit-normalized Gaussian row and column factors make unscaled inner
products bounded by one. Shared row factors across all four potential-outcome
matrices satisfy Assumption 2.5; a paired control redraws treatment-specific
row factors while holding the remaining protocol fixed.

For each target, the exact Algorithm 3 incidence matrix is constructed.
Because the low-treatment candidate-row count was at most ten, every nonempty
row subset was exhaustively enumerated. Each subset was paired with all common
columns and the maximum-edge biclique selected with deterministic tie-breaking.
Every selected edge was audited before Algorithm 2's rank-3 weighted SVD.

The independent checker does not import generator functions. It separately
recreates the RNG streams, incidence tables, exhaustive biclique search,
edge audit, weighted SVD, and all aggregates for 400 targets. It compares those
results to `raw_result.json` at 1e-10 relative tolerance. The mutation selects
anchor rows with treatment 2 for a treatment-1 target and must exit nonzero.
