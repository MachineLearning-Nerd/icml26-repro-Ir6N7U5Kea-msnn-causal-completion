# Claim 6 limitations and deviations

- Algorithm 3 calls an abstract `maxBiclique`; the paper does not specify its
  objective or tie-breaking. We use exact maximum edge count, then vertex and
  deterministic index tie-breaks, and do not claim this is the authors' code.
- The paper omits latent-factor distributions and seeds. Unit-normalized
  Gaussian factors are a transparent, bounded, assumption-satisfying choice.
- Only `K=1` is tested, matching Appendix B. The evidence verifies the
  construction and its load-bearing shared-factor mechanism at the paper's
  matrix scale; it does not independently establish Theorems 4.5–4.6.
- Only 26/382 selected maximum-edge cliques mixed treatment levels because the
  dominant treatment occupies 80% of entries. This is enough to directly test
  mixed construction but is reported rather than hidden.
