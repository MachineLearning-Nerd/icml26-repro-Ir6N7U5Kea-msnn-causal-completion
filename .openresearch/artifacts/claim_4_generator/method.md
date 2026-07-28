# Claim 4 generator method

This clean-room implementation preserves the pinned authors' legacy NumPy RNG
call order, including RNG consumption for the unused `not_observed` potential
matrix. It evaluates every one of 30,000 target entries for low treatment on
each seed 0–9.

The locked baseline environment contains only NumPy, so the author repository's
unpinned NetworkX/scikit-learn dependencies were not added. The current child
uses a dependency-free transcription of NetworkX 3.6.1 `find_cliques`, pinned
by source hash, and then applies the exact public author scoring loop. The
parent generator used an independently implemented exhaustive solver with
lexicographic equal-score ties. Both solvers' objective values are checked on
random matrices, and the current solver is exhaustively checked against brute
force on every nonzero binary matrix through 3x3.

The released PCR universal singular-value threshold, squared 0.1 train-error
and subspace-inclusion tests, SNN 1x1 exclusion, and MSNN scale normalization
are copied mathematically. Every selected SNN/MSNN edge is separately audited.
