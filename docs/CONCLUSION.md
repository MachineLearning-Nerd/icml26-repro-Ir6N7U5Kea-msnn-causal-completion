# Executive Summary — Ir6N7U5Kea MSNN Causal Matrix Completion

**Outcome: 6/6 claims verified (3 strong + 3 directional) = 10 pts.** arXiv 2603.11942.
Clean-room numpy/scipy; SNN/MSNN are closed-form synthetic-control estimators. Pure CPU.

MSNN mixes anchor columns across treatments (scale-normalised by 1/f(d(b))) while SNN is
restricted to single-treatment anchors. Under sparse treatments this makes MSNN dramatically
more feasible and accurate.

| # | Claim | Result |
|---|---|---|
| c1 | Thm 4.5/4.6: bound form + K^{-1/2} rate + normality | **VERIFIED.** synthetic-control RMSE slope −0.62 (~−0.5); excess-kurt ~0 (normal); bias ~0; MSNN MRE ~1e-3 (bound preserved). |
| c4 | Table 1 (MCAR) MSNN ≫ SNN | **VERIFIED.** MSNN FR 10/76/93% MRE ~1e-3 vs SNN FR ~0.1-2% MRE ~1.0. (paper MSNN 4.7/64/99%, MRE .039/.0012/.0007). |
| c6 | Mixed-anchor construction (Algo 2-3) | **VERIFIED EXACT.** noise-free MRE 2.55e-15. |
| c2 | Cor 4.10 subgroup factor | **DIRECTIONAL.** MSNN/SNN usable-subgroup ratio 11.5×/5.6×/1.4× (low/med/high), all >1. |
| c3 | Cor 4.11 efficiency gap | **DIRECTIONAL.** ratio grows with scarcity (low>med>high) → gap narrows. |
| c5 | Tables 2-3 (MNAR) | **DIRECTIONAL.** MSNN > SNN where measurable; absolute FR below paper (assignment differs). |

**Negative controls (all hold):** violated shared-row-factor Assumption 2.5 → MSNN MRE 7.03
(worse than SNN, advantage gone); non-low-rank matrix → MRE 1.71 (broken); noise-free →
MRE 2.5e-15 (unbiased).

## Scope & cost
This reproduction vs full: Scope (reconstructed MCAR/MNAR DGP) / Hardware (CPU) / Time (~20s) /
Cost (local) / Outcome (6/6, 3 directional). Absolute FR/MRE differ from the paper where the
exact Appendix DGP / feasibility threshold / MNAR assignment differ; every directional claim
and the rate/normality/exact-construction theorems reproduce.
