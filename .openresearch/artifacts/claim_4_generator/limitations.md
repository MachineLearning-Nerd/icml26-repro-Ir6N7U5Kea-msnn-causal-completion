# Claim 4 generator limitations

- Equal-score maximal-biclique tie order is unspecified by NetworkX and therefore
  cannot be reconstructed portably. The clean-room solver uses a disclosed
  deterministic tie rule while exactly matching the released objective.
- The author's dependency file is unpinned. The locked reproduction environment
  is intentionally not changed; only NumPy is used.
- This generator makes no pass/fail claim about the paper numbers. It emits both
  the code's normalized MAE and the paper-defined entrywise MRE so the metric
  mismatch is visible.
- A child must freeze the run output and add an independent aggregate checker
  before a final Claim 4 verdict.
