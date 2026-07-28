# Claim 2 method

This is a proof-level check of a corollary, not a Monte Carlo proxy.

The certificate encodes each Theorem 4.8 leading term as a Laurent monomial in
`gamma`, `p_d`, and `p_max`; polynomial exponents in `r,c` are represented by
integer coefficient maps. Exact division cancels the shared binomial factor and
subtracts exponent vectors. Substituting the definition of `gamma` yields the
Corollary 4.10 expression.

The independent checker shares no verifier code. It reconstructs the exponent
division, checks the audited source hash and asymptotic prefactor rule, and
performs an exact-rational identity substitution. A mutation control removes
one factor of `p_d` from the SNN exponent; the checker must reject it with exit
status 1 for the intended exponent-mismatch reason.
