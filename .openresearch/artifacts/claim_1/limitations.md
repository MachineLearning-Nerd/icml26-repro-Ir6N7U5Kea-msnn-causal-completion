# Claim 1 limitations and deviations

- The paper's literal environment includes the realized noise and therefore
  makes its non-degenerate conditional-noise assumptions internally
  inconsistent. The counterexample uses the coherent, stronger charitable
  interpretation—conditioning on latent factors and treatment design. Under
  the literal self-conditioning, the theorem is vacuous.
- The finite experiment covers `N=16,81,256`; it is not presented as a finite
  proof of an asymptotic statement. Exact arithmetic audits extend through
  `N=1024^4`, and the verdict relies on the closed-form asymptotic sequence.
- The construction is deliberately weak-signal because the point at issue is
  the paper's omitted lower signal-energy premise. It is not a claim that
  typical paper simulations use weak signal.
- Gaussian noise is used for calibration, but the derivation requires only
  independent fixed-variance sub-Gaussian noise.
- The result falsifies the theorem as stated under its coherent intended
  semantics. It does not challenge the cited SNN theorem, whose omitted
  energy assumption excludes this construction.
