# Claim 5 method

The formal grid contains 60 independent cell/seed tasks:

`2 lambda values × 3 target treatments × 10 seeds`.

Every task uses a 300×100 rank-three potential-outcome model, relative
Gaussian noise 0.001, and evaluates SNN and MSNN on all 30,000 entries.
Treatment assignment uses the four-way softmax from the paper and author code.
The primary DGP follows Appendix B: signed normalized latent factors are
multiplied, scaled by treatment, and then each ground-truth entry is made
nonnegative. The legacy RNG also consumes the unused `not_observed` potential
and noise draws in the author's dictionary order.

The estimator reuses the exact, dependency-free NetworkX 3.6.1 maximal-clique
traversal and PCR implementation validated for Claim 4. The balanced-biclique
objective is first certified by a pruned row-set search. The unchanged
author-order traversal then prunes only branches whose remaining row/column
candidates cannot attain that certified score and returns the first optimum.
This is not a heuristic: the cumulative run exhaustively checks all 673
nonempty binary matrices through 3×3 and requires exact selected-index
agreement with full author-order enumeration on 927 seeded matrices,
including equal-score tie cases.

The estimator implements the author's strict score-improvement tie behavior,
universal singular-value threshold, two squared 0.1 feasibility tests, and
SNN 1×1 exclusion. For MSNN, mixed columns are divided by their treatment
scales before PCR.

Every feasible prediction contributes to both:

1. released-code normalized MAE:
   `mean(abs(prediction-truth))/treatment_scale`;
2. paper-defined entrywise MRE:
   `mean(abs((prediction-truth)/truth))`.

The generator prints one progress record per completed task and the complete
strict JSON result. The independent checker reconstructs every seed mean,
sample standard deviation, formula, paper-table transcription, assignment
proportion, source range, and error ratio without importing the generator.

Controls:

- all 673 nonzero binary matrices through 3×3 exhaustively verify the clique
  objective;
- a 927-case deterministic suite requires exact selected-index agreement
  between the optimized and full NetworkX-order traversals, while separately
  recording lexicographic equal-score differences;
- every selected edge is audited against the treatment design;
- a metric mutation substitutes normalized MAE for the paper's formula and
  must exit nonzero;
- a source mutation clips the true paper cells to the imported 26%/5% ranges
  and must exit nonzero.
