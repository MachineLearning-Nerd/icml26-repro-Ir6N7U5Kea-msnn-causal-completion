# Claim 4 method

The clean-room NumPy implementation preserves the author code's legacy RNG call
order, DGP, all-entry evaluation, PCR universal rank threshold, two squared
0.1 feasibility checks, SNN 1x1 exclusion, and MSNN scale normalization.

Two independently specified clique routes were run:

1. An exhaustive balanced-biclique solver with deterministic lexicographic
   equal-score ties.
2. A dependency-free transcription of NetworkX 3.6.1 `find_cliques`, SHA-256
   `480bce4406d9ad9f88a5356e11c6ab11342284d7acfa0969362aa867b8448273`,
   followed by the author's strict score-improvement loop.

The current route checks its optimum exhaustively on all 673 nonzero binary
matrices through 3x3. A 927-case deterministic suite confirms both routes
always attain the same objective while selecting different tied cliques in 229
cases. Every selected treatment edge is audited.

For each feasible prediction, the generator accumulates both absolute error
divided by treatment scale and absolute entrywise relative error. The
independent checker reconstructs all seed aggregates and both metric formulas
from counts and sums. Its mutation substitutes the code metric for the paper
metric and must exit nonzero.
