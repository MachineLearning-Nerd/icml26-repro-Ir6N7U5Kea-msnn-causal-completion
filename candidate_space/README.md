---
title: "MSNN Causal Completion"
emoji: 🎯
colorFrom: yellow
colorTo: red
sdk: static
pinned: false
tags:
 - trackio
 - trackio-logbook
 - open-experiment
 - icml2026-repro
 - paper-Ir6N7U5Kea
---

# MSNN Causal Completion — current verification

This is the canonical evaluator entrypoint for the claim-by-claim reproduction
of arXiv 2603.11942. Begin with the
[current verification index](pages/index.md), which exposes the exact claim
contracts, inline results, source and assumption audits, executable verifiers,
raw artifacts, independent checkers, negative controls, limitations, Git
revisions, seeds, and CPU runtimes for all six claims.

The previous judged revision
`6501ddc2ca77931a80822435fa93670c03c7d2dc` is preserved additively. Its
executive summary is labeled **Historical rejected baseline** in current
navigation and is not the current verifier.

Fixed cumulative command:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Current scientific results: Claims 2, 3, and 6 **VERIFIED**; Claims 1, 4, and
5 **FALSIFIED**. These are reproduction verdicts, not a new live-judge score.
The previous live judged score remains **1/12** until the evaluator records a
new revision.
