# Claim 1 evaluation

Verdict: **FALSIFIED** under the coherent intended conditioning on latent
factors and treatment design.

The paper says its Theorems 4.5 and 4.6 inherit the cited SNN guarantees, but
the transfer omits SNN Assumption 6's population signal-energy lower bound.
The explicit rank-one sequence satisfies the MSNN paper's displayed
assumptions and every asymptotic side condition while violating that omitted
premise. Theorem 4.5's asserted right-hand side tends to zero, but Algorithm
2's error tends to `-1`; Theorem 4.6's statistic diverges to negative infinity.

The exact-algorithm calibration supports the analytical mechanism. At `N=256`,
the weak-signal error mean is `-1.00026756`, with 95% CI
`[-1.00229424,-0.99824088]`. Restoring the signal-energy premise gives mean
error `-0.00205631`, with 95% CI `[-0.01113887,0.00702625]`.

The independent checker passed. Its false-premise mutation exited one with
exactly one error:

`signal_frobenius_squared exponent mismatch: derived -1, declared 2`.

This is not an empirical claim that a few finite samples prove or disprove a
universal theorem. The verdict is borne by the explicit asymptotic
counterexample and independently reconstructed symbolic exponents; the finite
sweep is calibration and a mechanism control.
