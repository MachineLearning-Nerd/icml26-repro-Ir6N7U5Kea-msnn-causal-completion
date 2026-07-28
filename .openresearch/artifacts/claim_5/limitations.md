# Claim 5 pre-run limitations and deviations

- The public author dependency file does not pin NetworkX. The formal route
  freezes the NetworkX 3.6.1 traversal already exhaustively controlled in
  Claim 4, and retains a lexicographic sensitivity solver.
- The public author's current positive-factor DGP is incompatible with the
  paper's reported treatment proportions. The formal route follows Appendix
  B's absolute-entry statement, which reproduces all six proportions; the
  released route is preserved as a documented drift audit.
- The paper labels normalized MAE as MRE in released aggregation code even
  though Section 5.1 gives a per-entry relative-error formula. Both are
  computed from the same feasible predictions.
- Error summaries for a method/cell omit seeds with zero feasible estimates,
  matching the released aggregator; feasible-rate summaries retain all seeds.
- A final verdict will be recorded only after the complete 60-task run,
  independent checker, both negative controls, and cumulative regressions
  finish.
