# Claim 4 generator method

This clean-room implementation preserves the pinned authors' legacy NumPy RNG
call order, including RNG consumption for the unused `not_observed` potential
matrix. It evaluates every one of 30,000 target entries for low treatment on
each seed 0–9.

The locked baseline environment contains only NumPy, so the author repository's
unpinned NetworkX/scikit-learn dependencies were not added. Instead, every
candidate-row subset is enumerated and closed to a maximal bipartite clique.
The selected clique maximizes the authors' released objective
`min(number of anchor rows, number of anchor columns)`. NetworkX says maximal
clique enumeration order is arbitrary; equal-score ties here use lexicographic
row then column indices. An exhaustive independent objective check covers every
nonzero binary matrix through 3x3.

The released PCR universal singular-value threshold, squared 0.1 train-error
and subspace-inclusion tests, SNN 1x1 exclusion, and MSNN scale normalization
are copied mathematically. Every selected SNN/MSNN edge is separately audited.
