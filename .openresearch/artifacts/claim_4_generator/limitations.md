# Claim 4 generator limitations

- Equal-score maximal-clique order is documented by NetworkX as arbitrary. The
  current route transcribes NetworkX 3.6.1 exactly and pins its source hash;
  the parent route used a lexicographic tie rule. Agreement across both routes
  is stronger than relying on one unspecified order.
- The author's dependency file is unpinned. The locked reproduction environment
  is intentionally not changed; only NumPy is used.
- This generator makes no pass/fail claim about the paper numbers. It emits both
  the code's normalized MAE and the paper-defined entrywise MRE so the metric
  mismatch is visible.
- A child must freeze the run output and add an independent aggregate checker
  before a final Claim 4 verdict.
