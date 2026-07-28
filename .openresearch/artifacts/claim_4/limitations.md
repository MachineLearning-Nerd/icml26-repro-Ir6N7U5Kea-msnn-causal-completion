# Claim 4 limitations and deviations

- The author dependency file is unpinned. The reproduction therefore freezes a
  current NetworkX 3.6.1 transcription and retains an exhaustive
  lexicographic route as a sensitivity analysis.
- NetworkX equal-score clique order changes a few SNN estimates. It does not
  materially change MSNN or reconcile the metric-definition discrepancy.
- The released SNN table aggregator omits seeds with zero feasible estimates
  for error but includes them for feasible rate. This behavior is reproduced
  and explicitly reported.
- The verdict falsifies the exact Table 1 conjunction because its MRE-labeled
  number contradicts the paper's stated formula. It does not dispute that the
  released code reproduces the MSNN feasible rate or normalized-MAE number.
