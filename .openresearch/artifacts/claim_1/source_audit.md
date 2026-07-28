# Claim 1 source and quantifier audit

## Pinned sources

The primary source is
`https://ar5iv.labs.arxiv.org/html/2603.11942`, retrieved on 2026-07-28 with
an explicit browser User-Agent. Its SHA-256 is
`f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.
The relevant anchors are Section 4.1 (`#S4.SS1`), Section 4.2 (`#S4.SS2`),
Theorem 4.5 (`#S4.Thmtheorem5`), Theorem 4.6
(`#S4.Thmtheorem6`), Remark 4.7, and Appendix C.2.

The transferred result is from Agarwal et al., *Causal Matrix Completion*
(arXiv 2109.15154), retrieved on 2026-07-28. The pinned ar5iv HTML SHA-256 is
`3ffca53b29d11c708d8332ef53360e7aedc4602ff68ec66cb1e4e12e714f519f`;
its Assumption 6 anchor is
`https://ar5iv.labs.arxiv.org/html/2109.15154#Thmassumption6`.

## Exact theorem contract

Theorem 4.5 is conditioned on the paper's environment `E`. It fixes an entry
`(i,j)` and treatment `d`; requires every subgroup to have at least `mu` mixed
anchor rows; invokes Assumptions 2.1 through 4.3; requires

`K_MSNN = o(min_k |MAC^(k)|^10 |MAR^(k)|^10)`;

sets the PCR truncation rank to the population rank and the weight to
`1/f(d(b))`; and asserts

`estimate - truth = f(d) O_p((sum_k(error_k1+error_k2) + sqrt(sum_k ||beta_k||_2^2))/K_MSNN)`.

Theorem 4.6 imports that setup and additionally quantifies an asymptotic
sequence satisfying:

1. `K_MSNN -> infinity`;
2. every mixed anchor row and column count tends to infinity;
3. the displayed rank/beta/log term is little-o of the smaller anchor
   dimension product;
4. `f(d) * sum_k(error_k1+error_k2)` is little-o of the square root of the
   summed conditional variances.

It then claims that `K_MSNN` times the estimation error, divided by that
standard deviation, converges in distribution to `N(0,1)`. Remark 4.7 states
that these are the same SNN forms with `AR/AC` replaced by `MAR/MAC`.

## Missing premise in the transfer

Appendix C.2 says the proof reduces to Theorems 2 and 3 of the cited SNN paper.
Those results require SNN Assumptions 1 through 7. In particular, SNN
Assumption 6 requires both:

`tau_r / tau_1 >= c`

and

`||E[S^(k) | environment]||_F^2 >= c' |AC^(k)| |AR^(k)|`.

MSNN Assumption 4.3 retains the singular-value ratio but replaces the
signal-energy lower bound by the one-sided upper bound

`tau_1^(k)(d) <= c' |MAR^(k)(d)| |MAC^(k)(d)|`.

An upper bound cannot supply the cited lower bound. The counterexample targets
exactly this omitted premise; it does not vary a theorem tolerance or use an
unrelated estimator.

## Conditioning ambiguity

At the start of Section 4.1, the paper literally defines calligraphic `E` as
`{U,V,E}`, where the final `E` denotes the noise matrices. Conditioning a
non-degenerate noise variable on itself is incompatible with subsequently
requiring that same noise to be conditionally mean-zero. Assumption 4.4 and
the model elsewhere condition on `U,V,D`, which is coherent.

The verification therefore uses the strongest charitable intended reading:
condition on latent factors and treatment design, not on the realized noise.
Under the literal self-conditioning, the nonzero-noise theorem setup is
internally inconsistent and the theorem is vacuous rather than empirically
testable. This interpretive deviation is material and is not hidden.
