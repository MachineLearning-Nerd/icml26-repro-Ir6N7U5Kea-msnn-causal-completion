# Claim 1 method

## Analytical counterexample

Let `N=t^4`, `K=t`, and use rank one. Each of the `K` disjoint subgroups has
`N` anchor rows and `N` mixed anchor columns. The two treatment levels alternate
across columns, both with scale one. The incidence matrix in Algorithm 3 is all
ones, so its complete block is a maximum bipartite clique.

For every subgroup, set the donor-row factors to

`u_N = (1, N^-2, ..., N^-2)`,

all anchor-column loadings to `delta_N=N^-1`, and both target loadings to one.
Add mutually independent, mean-zero Gaussian noise with fixed standard
deviation `sigma=0.25`. The target truth is exactly one.

This construction is an exact shared-row-factor, two-treatment, rank-one model.
All factors are bounded by one. Every nonempty scalar donor set spans the
target scalar factor. The population rank is one, subspace inclusion is exact,
and the rank-one spectral ratio is one. Its top population singular value
satisfies the paper's upper bound while vanishing:

`tau_1 = sqrt(1+(N-1)N^-4) / sqrt(N)`.

The imputation vector is

`beta_N = u_N / ||u_N||_2^2`,

so both beta norms remain bounded. The missing cited-SNN premise fails by
order `N^-3` because population signal energy is order `N^-1`, while the cited
lower bound is order `N^2`.

## Contradictions

For each exact rank-one PCR term, the noisy anchor matrix's leading singular
value is `Omega_p(sqrt(N))`. Its leading singular vectors are independent of
the query-row and target-column noise, so each relevant inner product is
`O_p(1)`. The Algorithm 2 estimate is therefore `O_p(N^-1/2)` (uniformly over
the polynomial number of subgroups), while the truth is one. Hence the
estimation error converges in probability to `-1`.

Theorem 4.5's displayed right-hand side is instead dominated by
`N^-1/8` up to logarithms and tends to zero. Every Theorem 4.6 side condition
holds, but its standardized statistic is

`-sqrt(K)/sigma * (1+o_p(1)) = -N^(1/8)/sigma * (1+o_p(1))`,

which diverges to negative infinity rather than converging to `N(0,1)`.

## Machine and empirical checks

The proof certificate states every exact identity and asymptotic exponent.
An independent checker reconstructs those exponents with rational arithmetic,
recomputes the exact audits, and reconstructs all means, standard deviations,
standard errors, and 95% confidence intervals from 72 raw repetitions.

The formal calibration runs Algorithm 2's exact rank-one PCR at
`N in {16,81,256}`, 24 deterministic repetitions per size. A strong-signal
control replaces the weak donor factors and anchor loading by ones. It should
recover the target; this distinguishes the missing-signal-premise mechanism
from a broken PCR implementation. A mutation that falsely declares the cited
SNN energy premise satisfied must make the independent checker exit nonzero.
