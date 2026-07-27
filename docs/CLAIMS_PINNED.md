# Pinned claims — Ir6N7U5Kea "Causal Matrix Completion under Multiple Treatments via Mixed Synthetic Nearest Neighbors"

arXiv 2603.11942. No released code (clean-room; SNN/MSNN are closed-form synthetic-control estimators).

Model: Y_{ij}^{(d)} = <u_i, v_j^{(d)}> + eps, U in R^{m x r} SHARED across treatments (Assumption 2.5:
u_i^{(d)} = u_i), V^{(d)} in R^{n x r} scaled by f(d). So A_{ij}^{(d)} = f(d)<u_i, v_j^{base}>.
DGP: m=300, n=100, r=3, sigma=0.001; treatments L={low,med,high,vhigh}, f(d)={1,5,25,625}.

## c1 — Thm 4.5 (MSNN preserves SNN finite-sample error bound) + Thm 4.6 (asymptotic normality, rate K_MSNN^{-1/2}).
Â_{ij}^{(d)} - A_{ij}^{(d)} = f(d)·O_p(1/K_MSNN{...}); K_MSNN^{1/2}(Â-A)/[Σ(σ̃^k)^2]^{1/2} ->^d N(0,1).
VERIFY: MC — error ~ 1/sqrt(K); standardized residual ~ N(0,1).

## c2 — Cor 4.10: E[K_MSNN]/E[K_SNN] = (1+o(1))[Σ_{d'}(p_{d'}/p_d)^{r+1}]^c.  (algebraic + MC)

## c3 — Cor 4.11: efficiency gap exponent rc+r+c (SNN) -> r (MSNN) [quadratic rc -> linear r].

## c4 — Table 1 (MCAR): p=0.01 SNN FR 0.03% / MRE 0.806 ; MSNN FR 4.69% / MRE 3.91e-2.
       p=0.025 SNN 1.20%/0.577 ; MSNN 63.73%/1.18e-3.  p=0.05 SNN 11.34%/0.515 ; MSNN 99.29%/7.05e-4.

## c5 — Tables 2-3 (MNAR): MSNN 3-26% feasible vs SNN <5%; 2-3x MRE reduction.

## c6 — Mixed-anchor construction via bipartite cliques (Algo 2-3): MAR(d)=rows a with D[a,j]=d;
       MAC(d)=cols b with D[i,b]=d(b)!=0 consistent across MAR; block S_w[a,b]=Y[a,b]/f(d(b)).

## Key mechanism
SNN anchor block must be observed at treatment d (D[a,b]=d for all a in AR, b in AC) -> under sparse
p(d) this is exponentially unlikely -> FR ~0. MSNN allows each col b to use its OWN treatment d(b)
(scale-normalized by 1/f(d(b))) -> anchor cols available from ANY treatment -> far more feasible.
