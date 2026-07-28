# Claim 1 — finite-sample bound and asymptotic normality

**Current verdict: FALSIFIED under the coherent intended conditioning.**

Theorems 4.5 and 4.6 claim that MSNN transfers SNN's finite-sample error bound
and asymptotic normality after replacing same-treatment anchor sets by mixed
anchor sets. The transfer proof omits a load-bearing premise of the cited SNN
theorems: a lower bound on the population anchor matrix's signal energy.

## Headline evidence

The certified rank-one sequence satisfies the MSNN paper's displayed
assumptions and every theorem side condition. Its claimed finite-bound
right-hand side is `O(N^-1/8 polylog(N)) -> 0`, but Algorithm 2's error tends
to `-1`. Its normality statistic behaves as `-N^(1/8)/sigma` and diverges
rather than approaching `N(0,1)`.

| N | K=N^(1/4) | Weak-signal error mean (95% CI) | Strong-signal control error mean (95% CI) | Weak standardized mean |
|---:|---:|---:|---:|---:|
| 16 | 2 | -1.001632 [-1.022283, -0.980981] | -0.009765 [-0.030819, 0.011289] | -5.666735 |
| 81 | 3 | -0.998081 [-1.002816, -0.993345] | -0.005003 [-0.014997, 0.004991] | -6.914911 |
| 256 | 4 | -1.000268 [-1.002294, -0.998241] | -0.002056 [-0.011139, 0.007026] | -8.002141 |

These 72 exact-PCR repetitions calibrate the mechanism; the asymptotic
counterexample, not a fitted slope, bears the theorem verdict.

## Exact premise audit

The [source and quantifier audit](../../../.openresearch/artifacts/claim_1/source_audit.md)
shows that cited SNN Assumption 6 requires

`||E[S | environment]||_F^2 >= c' |AC| |AR|`.

MSNN Assumption 4.3 retains only a singular-value ratio and an upper bound on
the leading singular value. In the counterexample, signal energy is
`Theta(N^-1)` while the cited lower bound is `Theta(N^2)`: a factor
`Theta(N^-3)` short. The paper's proof says it reduces to the cited SNN
theorems but never restores that lower bound.

The paper also defines its conditioning environment to include realized noise,
which is incompatible with non-degenerate conditionally mean-zero noise. The
[limitations](../../../.openresearch/artifacts/claim_1/limitations.md) state
this explicitly. The verdict uses the strongest charitable coherent reading:
condition on latent factors and treatment design.

## Reproduce and inspect

- [Formal generator](../../../repro/claims/claim1_theorems/experiment.py)
- [Fail-closed verifier](../../../repro/claims/claim1_theorems/verifier.py)
- [Independent checker](../../../repro/claims/claim1_theorems/independent_checker.py)
- [Proof certificate](../../../.openresearch/artifacts/claim_1/proof_certificate.json)
- [Raw 72-repetition JSON](../../../.openresearch/artifacts/claim_1/raw_result.json)
- [Independent checker output](../../../.openresearch/artifacts/claim_1/checker_output.txt)
- [Negative-control output](../../../.openresearch/artifacts/claim_1/negative_control_output.txt)
- [Claim contract](../../../.openresearch/artifacts/claim_1/claim_contract.json)
- [Derivation and method](../../../.openresearch/artifacts/claim_1/method.md)
- [Command, lock hashes, CPU, seeds, and runtime](../../../.openresearch/artifacts/claim_1/environment.md)
- [Limitations and deviations](../../../.openresearch/artifacts/claim_1/limitations.md)

The fixed command is:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Current evidence-freeze run `4498c980-5971-49b7-a9d9-dfd452ff2241` used Git
SHA `b01cf6ff3166e5e0ed72f876614e1a4d3f5cb3dc` on HF `cpu-upgrade` (officially
8 vCPU/32 GB; 64 logical CPUs container-visible), with eight worker processes.
It completed the cumulative suite in 758 seconds. The checker passed; the
false energy-premise mutation exited nonzero for exactly the intended exponent
mismatch.
