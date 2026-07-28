# Claim 2 source audit

Source: ar5iv HTML for arXiv 2603.11942, retrieved with explicit User-Agent on
2026-07-28 from `https://ar5iv.labs.arxiv.org/html/2603.11942`.

SHA-256: `f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448`.

Anchors:

- Theorem 4.8: `#S4.Thmtheorem8`
- Corollary 4.10: `#S4.Thmtheorem10`
- Appendix proof: `#A3.SS3.SSS1`

Exact scope: MCAR treatment assignment; fixed anchor sizes
`|AR|=|MAR|=r` and `|AC|=|MAC|=c`; positive treatment probabilities; an
`alpha in (0,1)` for which
`m*r*p_d*p_max^(alpha*c)=o(1)` and
`n*c*gamma*p_max^((1-alpha)r+1+alpha)=o(1)`, where
`gamma=sum_d'(p_d'/p_max)^(r+1)`. The result is asymptotic and applies to the
expectation of the maximum extractable subgroup counts, not to feasible-rate
proxies from one finite matrix.

The paper states, for any entry `(i,j)` and treatment `d`,
`E[K_MSNN(d)]/E[K_SNN(d)] = (1+o(1))
[sum_d'(p_d'/p_d)^(r+1)]^c`.
