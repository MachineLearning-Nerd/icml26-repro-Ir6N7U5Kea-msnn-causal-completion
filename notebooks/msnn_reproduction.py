import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Mixed SNN, audited claim by claim

    **Start with the evidence.** The paper's MNAR tables show a genuine
    qualitative gain for MSNN, but they do not support the imported
    `3–26% versus <5%` range summary.

        ![Paper Tables 2–3 feasible rates](https://raw.githubusercontent.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/master/reports/reproduction-campaign/images/claim5_mnar_feasible_rates.svg)

    This notebook is a bounded, tutorial-style view of already-generated
    evidence. It does not rerun the expensive formal experiments.
    """)
    return


@app.cell
def _():
    claim_rows = [
        {"claim": 1, "topic": "Theorems 4.5–4.6", "verdict": "FALSIFIED", "decisive evidence": "Weak-signal error → −1 while claimed bound → 0"},
        {"claim": 2, "topic": "Corollary 4.10", "verdict": "VERIFIED", "decisive evidence": "Exact Laurent-exponent identity"},
        {"claim": 3, "topic": "Corollary 4.11", "verdict": "VERIFIED", "decisive evidence": "Sparse/rich exponents rc+r+c versus r"},
        {"claim": 4, "topic": "Table 1", "verdict": "FALSIFIED", "decisive evidence": "0.0391 normalized MAE versus 0.252483 stated MRE"},
        {"claim": 5, "topic": "Tables 2–3", "verdict": "FALSIFIED", "decisive evidence": "Source ranges 3.13–54.16% and SNN max 22.66%"},
        {"claim": 6, "topic": "Algorithms 2–3", "verdict": "VERIFIED", "decisive evidence": "382/382 invariants and controls"},
    ]
    return (claim_rows,)


@app.cell
def _(claim_rows, mo):
    mo.vstack([
        mo.md("## Verdict map"),
        mo.ui.table(claim_rows, selection=None),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What MSNN changes

    Standard SNN requires a same-treatment rectangular anchor block.
    MSNN allows anchor columns to use different treatment levels while
    requiring each selected row to preserve the target treatment. That is
    legitimate only because Assumption 2.5 shares the latent row factor
    across treatment-specific outcome matrices.

    The implementation test is deliberately structural:

    1. select a bipartite clique with Algorithms 2–3;
    2. check every target-treatment edge and row invariant;
    3. corrupt one required treatment label and require rejection;
    4. compare reconstruction with and without the shared-factor premise.

    At paper scale, 382/382 valid cliques passed and 382/382 corruptions
    were rejected. Violating the shared factor raised scaled MAE from
    `0.003497` to `2.232891`.
    """)
    return


@app.cell
def _(mo):
    metric_values = {
        "Paper table label": 0.0391,
        "Released normalized MAE": 0.03908573,
        "Section 5.1 entrywise MRE": 0.25248262,
    }
    metric = mo.ui.dropdown(
        options=list(metric_values),
        value="Section 5.1 entrywise MRE",
        label="Choose the Table 1 quantity",
    )
    metric
    return metric, metric_values


@app.cell
def _(metric, metric_values, mo):
    mo.callout(
        mo.md(
            f"**{metric.value}: `{metric_values[metric.value]:.8f}`.** "
            "The same predictions produce both error values; the difference "
            "comes from the denominator being applied before or after averaging."
        ),
        kind="info",
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## How to inspect or regenerate

    The immutable evidence is already embedded in the repository under
    `.openresearch/artifacts/claim_1` through `claim_6`. To regenerate the
    cumulative suite in the locked environment:

    ```sh
    uv sync --frozen
    uv run --frozen python repro/src/verify.py && uv run --frozen python repro/tests/test_controls.py
    ```

    Formal results were produced on CPU-only Hugging Face `cpu-upgrade`
    jobs. The verifier exits nonzero when evidence or controls fail. See
        the [illustrated report](https://github.com/MachineLearning-Nerd/icml26-repro-Ir6N7U5Kea-msnn-causal-completion/blob/master/reports/reproduction-campaign/report.md)
    for source quantifiers, limitations, and branch provenance.
    """)
    return


if __name__ == "__main__":
    app.run()
