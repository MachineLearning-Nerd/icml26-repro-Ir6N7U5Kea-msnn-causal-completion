# Claim 5 method

The accepted route is an exact primary-source falsification, not an incomplete
simulation result.

1. Pin the retrieved paper HTML by URL, retrieval date, SHA-256, Section 5.1,
   and Tables 2–3 anchors.
2. Transcribe all 12 method/treatment/lambda table cells, including their
   displayed standard deviations.
3. Independently compute the MSNN feasible-rate range, maximum SNN feasible
   rate, and all six displayed SNN/MSNN error ratios.
4. Reject the imported conjunction if any exact range or universal ratio
   condition is contradicted.
5. Run both source-range and metric-definition mutations; each must make the
   checker exit nonzero.

The DGP corroboration uses the paper-scale 300×100 rank-three model for both
lambda values and all seeds 0–9. It audits treatment proportions under the
Appendix-B absolute-entry construction and under the current released
positive-factor construction. This reproduces all six displayed assignment
proportions under the paper route and exposes released-code drift, but it is
not needed for the logical source-table falsification.

The metric audit stores a numerical witness for the distinction between
Section 5.1's feasible-entry mean of `abs((prediction-truth)/truth)` and the
released aggregator's `mean(abs(prediction-truth))/treatment_scale`.
