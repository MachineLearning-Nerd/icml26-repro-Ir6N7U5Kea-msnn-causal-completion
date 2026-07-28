# Claim 4 evaluation

Verdict: **FALSIFIED**.

At the exact paper scale and across seeds 0–9, MSNN feasible rate is
`4.689333 ± 1.114224%`, reproducing `4.69 ± 1.11%`. The released-code
normalized MAE is `0.03908573 ± 0.01090279`, reproducing the value labeled MRE,
`0.0391 ± 0.0109`.

Applying the paper's explicit mean per-entry relative-error formula to the same
feasible predictions yields `0.25248262 ± 0.11621787`, not `0.0391`. Thus the
table number is reproducible only under a different metric from the one the
paper defines. Because the claim conjoins the feasible-rate and MRE assertions,
the exact claim is falsified even though two released-code numerical cells
reproduce.

The NetworkX route gives SNN FR `0.015667 ± 0.019941%`; finite-only normalized
MAE is `0.80554791 ± 0.23959303`. The arbitrary clique tie order does not
recover the reported `0.03 ± 0.00%` feasible rate.
