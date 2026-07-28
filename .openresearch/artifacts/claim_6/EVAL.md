# Claim 6 evaluator record

Verdict: **VERIFIED** for the exact mechanism/construction claim.

Direct evidence: ten paper-scale 300x100 noisy matrices, 382 selected cliques,
382 invariant audits, 382 rejected corrupted-edge controls, 26 genuinely mixed
cliques, and 215 estimable targets. Shared-factor scaled MAE was 0.003497;
violating Assumption 2.5 raised it to 2.232891 (>638x).

The independent implementation regenerated all 400 target searches and matched
the frozen evidence. The current verifier exits nonzero if raw counts, MAEs,
acceptance criteria, independent reconstruction, or the negative control fail.
This supersedes the historical noise-free toy check.
