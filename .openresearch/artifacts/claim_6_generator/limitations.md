# Claim 6 generator limitations

- The paper leaves `maxBiclique` abstract. This implementation chooses maximum
  edge count and records the choice; it does not claim the authors used it.
- The latent-factor distribution and seeds are absent from the paper. Unit-row
  Gaussian factors are a transparent assumption-satisfying choice.
- This first node emits raw formal output. A descendant must commit that output,
  independently recompute its aggregates, and expose it on the candidate page
  before Claim 6 can receive a final VERIFIED/FALSIFIED/BLOCKED verdict.
