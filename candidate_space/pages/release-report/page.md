# Release report

- Previous live judged score: `1/12`
- Conservative projected score range after the proposed change: `9–12/12`
- Best-supported possible new score: `12/12` — **forecast, not a judge result**
- Protected HF Head: `6501ddc2ca77931a80822435fa93670c03c7d2dc`
- Protected Judge Head: `6501ddc2ca77931a80822435fa93670c03c7d2dc`

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
|---|---:|---:|---|---|---|
| 1 | 0 | 2 | MEDIUM | FALSIFIED | Analytic weak-signal counterexample satisfies the displayed premises and contradicts both theorem conclusions; risk is the paper's internally inconsistent conditioning notation. |
| 2 | 0 | 2 | HIGH | VERIFIED | Exact Laurent identity plus an independent symbolic checker; conditional on Theorem 4.8 as the corollary itself is. |
| 3 | 0 | 2 | HIGH | VERIFIED | Exact sparse/rich exponent certificate plus mutation control; conditional on Theorem 4.8. |
| 4 | 0 | 2 | HIGH | FALSIFIED | Paper-scale ten-seed run reproduces FR and isolates a direct mismatch between the displayed label and Section 5.1's metric. |
| 5 | 0 | 2 | HIGH | FALSIFIED | Exact source-table certificate contradicts all three bounded summaries; the broader qualitative MSNN improvement remains true. |
| 6 | 1 | 2 | HIGH | VERIFIED | Paper-scale noisy test passes 382/382 invariants and rejects 382/382 intended corruptions; this verifies the construction, not unrelated theorems. |

## What changed

All claims changed materially from the previous judge result. Claims 1–5 now
have exact contracts, source quantifiers, executable verification, raw data,
independent checkers, intended negative controls, compute provenance, and
limitations. Claim 6 replaces the historical noise-free toy with a noisy
300×100, rank-3, ten-seed mechanism test.

No claim remains BLOCKED. Claims 2, 3, and 6 are VERIFIED; Claims 1, 4, and 5
are FALSIFIED. The release does not promise a perfect score, and no projected
point is presented as earned.

## Previous judge criticisms answered

| Claim | Previous criticism | Current direct answer |
|---|---|---|
| 1 | No setup, sample sizes, DGP, code, or raw normality/rate data | Exact theorem contract, premise audit, symbolic counterexample, three-N 72-repetition calibration, raw JSON, proof certificate, checker, and intended mutation |
| 2 | Bare finite subgroup-ratio assertion | Exact Corollary 4.10 Laurent identity under Theorem 4.8; no proxy probability sweep |
| 3 | Trend was not the quadratic-to-linear order claim | Exact sparse/rich divisions and exponent vectors `rc+r+c` versus `r` |
| 4 | Different numbers and no faithful Table 1 setup | Paper-scale ten-seed run, all seed rows inline, both metric definitions on identical predictions |
| 5 | No MNAR details, feasible-rate table, or MRE values | Every Tables 2–3 cell and ratio inline, exact source certificate, ten-seed DGP audit, and rejected incomplete-run disclosure |
| 6 | Noise-free toy only | Noisy 300×100, rank-3, ten-seed mechanism audit with 382 valid and 382 corrupted cliques |

## Experiment tree and winning evidence

The tree grew as stacked claim rounds from the immutable baseline. Each child
reran all accepted checks. The frozen cumulative evidence branch is
`orx/claim-5-evaluator-visible-source-evidence` at
`b99cefc0f99bf42b8397594b2e2de49d4c209014`; its formal cumulative run is
`5f17a7bf-5a73-428c-8f3d-54cf844cd48d`.

Fixed command:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

All accepted formal runs used Hugging Face `cpu-upgrade` without GPU. The
allocation was 8 vCPU and 32 GB, while the container reported 64 visible host
logical CPUs. Claim-specific environments record estimates, caps, Git SHAs,
seeds, and runtimes. The accepted final cumulative run took 688 seconds. The
provider invoice is not exposed through the OpenResearch evidence channel, so
no unverified monetary total is asserted.

The [command ledger](../../release/command-ledger.md) records the exact fixed
command, accepted run IDs, orchestration commands, cancellations, and release
checks without credentials or generated backend wrappers.

## Historical safety and publication action

The exact judged revision
`6501ddc2ca77931a80822435fa93670c03c7d2dc` is the protected baseline.
Its old file set must be a byte-identical subset of the downloaded candidate,
apart from the three canonical metadata/navigation files intentionally
superseded additively (`README.md`, `pages/index.md`, `logbook.json`). Every
other historical file remains byte-identical and reachable, and its old
executive summary is labeled **Historical rejected baseline** in current
navigation.

The exact [judged-revision subset check](../../release/judged-subset-check.md)
records every protected hash and the three canonical navigation files
intentionally superseded.

After the allowlist, hash, secret, JSON, traversal, and blind-review gates pass,
the exact publication action is a text-only additive commit to the existing
Space `DineshAI/Ir6N7U5Kea`; no second Space will be created. The exact
published text paths will then be mirrored to GitHub `master`.
