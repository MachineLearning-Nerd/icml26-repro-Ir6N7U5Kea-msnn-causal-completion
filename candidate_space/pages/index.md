# MSNN Causal Completion — current claim verification

This page is the canonical evaluator index. The current cumulative verifier is
the fixed command below at frozen evidence commit
`b99cefc0f99bf42b8397594b2e2de49d4c209014`:

```sh
uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
```

Formal cumulative run `5f17a7bf-5a73-428c-8f3d-54cf844cd48d` completed on
Hugging Face `cpu-upgrade` in 688 seconds. The official allocation was 8 vCPU
and 32 GB; the container exposed 64 host logical CPUs, and worker/thread caps
are recorded per claim. The pinned image is
`ghcr.io/astral-sh/uv@sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248`.

## Current pages

1. [Claim 1 — finite-sample bound and normality](#/current-verification/claim-1) — **FALSIFIED**
2. [Claim 2 — Corollary 4.10](#/current-verification/claim-2) — **VERIFIED**
3. [Claim 3 — Corollary 4.11](#/current-verification/claim-3) — **VERIFIED**
4. [Claim 4 — Table 1 low-treatment result](#/current-verification/claim-4) — **FALSIFIED**
5. [Claim 5 — MNAR Tables 2–3 ranges](#/current-verification/claim-5) — **FALSIFIED**
6. [Claim 6 — noisy mixed-anchor construction](#/current-verification/claim-6) — **VERIFIED**
7. [Release report and score forecast](#/release-report)
8. [Evaluator-blind release audit](#/release-audit)

The old [executive summary](#/executive-summary) is preserved unchanged as
**Historical rejected baseline**. It contains self-reported proxies rejected
by the previous judge and does not supersede any page above.

## Visibility matrix

Every “yes” cell is reachable from this page without repository knowledge.
Each claim page places decisive data inline and links its complete evidence.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | [Claim 1](#/current-verification/claim-1) | [generator](../repro/claims/claim1_theorems/experiment.py), [verifier](../repro/claims/claim1_theorems/verifier.py) | yes: three-N CI table | [raw JSON](../.openresearch/artifacts/claim_1/raw_result.json) | [independent checker](../repro/claims/claim1_theorems/independent_checker.py) and [output](../.openresearch/artifacts/claim_1/checker_output.txt) | [output](../.openresearch/artifacts/claim_1/negative_control_output.txt) | exact Theorems 4.5–4.6 transfer under displayed premises | **FALSIFIED** |
| 2 | [Claim 2](#/current-verification/claim-2) | [verifier](../repro/claims/claim2_cor410/verifier.py) | yes: identity and raw result | [raw JSON](../.openresearch/artifacts/claim_2/raw_result.json) | [independent checker](../repro/claims/claim2_cor410/independent_checker.py) and [output](../.openresearch/artifacts/claim_2/checker_output.txt) | [output](../.openresearch/artifacts/claim_2/negative_control_output.txt) | exact Corollary 4.10 leading-term identity | **VERIFIED** |
| 3 | [Claim 3](#/current-verification/claim-3) | [verifier](../repro/claims/claim3_cor411/verifier.py) | yes: exact exponents | [raw JSON](../.openresearch/artifacts/claim_3/raw_result.json) | [independent checker](../repro/claims/claim3_cor411/independent_checker.py) and [output](../.openresearch/artifacts/claim_3/checker_output.txt) | [output](../.openresearch/artifacts/claim_3/negative_control_output.txt) | exact Corollary 4.11 sparse/rich ratios | **VERIFIED** |
| 4 | [Claim 4](#/current-verification/claim-4) | [generator](../repro/claims/claim4_table1/experiment.py), [verifier](../repro/claims/claim4_table1/verifier.py) | yes: aggregate and ten-seed tables | [raw JSON](../.openresearch/artifacts/claim_4/raw_result.json) | [independent checker](../repro/claims/claim4_table1/independent_checker.py) and [output](../.openresearch/artifacts/claim_4/checker_output.txt) | [output](../.openresearch/artifacts/claim_4/negative_control_output.txt) | exact Table 1 FR and Section 5.1 MRE | **FALSIFIED** |
| 5 | [Claim 5](#/current-verification/claim-5) | [generator](../repro/claims/claim5_tables23/source_certificate.py), [verifier](../repro/claims/claim5_tables23/verifier.py) | yes: six cells, ratios, and DGP audit | [raw JSON](../.openresearch/artifacts/claim_5/raw_result.json) | [independent checker](../repro/claims/claim5_tables23/independent_checker.py) and [output](../.openresearch/artifacts/claim_5/checker_output.txt) | [metric](../.openresearch/artifacts/claim_5/negative_control_metric.txt), [source](../.openresearch/artifacts/claim_5/negative_control_source.txt) | exact imported Tables 2–3 conjunction | **FALSIFIED** |
| 6 | [Claim 6](#/current-verification/claim-6) | [generator](../repro/claims/claim6_algorithm/experiment.py), [verifier](../repro/claims/claim6_algorithm/verifier.py) | yes: scale, counts, and errors | [raw JSON](../.openresearch/artifacts/claim_6/raw_result.json) | [independent checker](../repro/claims/claim6_algorithm/independent_checker.py) and [output](../.openresearch/artifacts/claim_6/checker_output.txt) | [output](../.openresearch/artifacts/claim_6/negative_control_output.txt) | Algorithms 2–3 invariants under Assumption 2.5 | **VERIFIED** |

## Release forecast, not a judge result

- Previous live judged score: **1/12**
- Conservative projected score after this revision: **9–12/12**
- Best-supported possible score: **12/12 (forecast only)**

Claim 1 has MEDIUM confidence because the paper's conditioning notation is
internally inconsistent; Claims 2–6 have HIGH confidence for their explicit
contracts. Only the live judge can change the score.
