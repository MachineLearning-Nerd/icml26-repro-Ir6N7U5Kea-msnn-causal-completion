"""Generate the exact primary-source falsification certificate for Claim 5."""

from __future__ import annotations

import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from repro.claims.claim5_tables23.experiment import (  # noqa: E402
    LABELS,
    LAMBDAS,
    M,
    N,
    PAPER_ASSIGNMENT_PROPORTIONS,
    PAPER_TABLES,
    RANK,
    SEEDS,
    TARGET_LEVELS,
    mnar_dgp,
    paper_source_audit,
)


def aggregate_assignment(records: list[dict], mode: str) -> dict:
    output: dict[str, dict] = {}
    for lam in LAMBDAS:
        lam_key = f"{lam:.2f}"
        output[lam_key] = {}
        for level in TARGET_LEVELS:
            treatment = LABELS[level]
            values = [
                record[mode][treatment]
                for record in records
                if record["lambda"] == lam
            ]
            output[lam_key][treatment] = {
                "mean_percent": statistics.fmean(values),
                "sample_std_percent": statistics.stdev(values),
                "values_percent": values,
            }
    return output


def main() -> int:
    started = time.perf_counter()
    assignment_records: list[dict] = []
    for lam in LAMBDAS:
        for seed in SEEDS:
            modes: dict[str, dict] = {}
            for mode in (
                "paper_absolute_entries",
                "released_positive_factors",
            ):
                _, design, _ = mnar_dgp(seed, lam, mode=mode)
                modes[mode] = {
                    LABELS[level]: 100 * float(np.mean(design == level))
                    for level in TARGET_LEVELS
                }
            assignment_records.append(
                {"lambda": lam, "seed": seed, **modes}
            )

    metric_witness = {
        "prediction": [1.5, 2.0],
        "released_normalized_mae": 0.5,
        "scale": 1.0,
        "section_5_1_entrywise_mre": 1.0,
        "truth": [0.5, 2.0],
    }
    result = {
        "assignment_aggregates": {
            mode: aggregate_assignment(assignment_records, mode)
            for mode in (
                "paper_absolute_entries",
                "released_positive_factors",
            )
        },
        "assignment_records": assignment_records,
        "author_source": {
            "commit": "12bd881f82a93cd223989a6a8cd082a3dc9a0e47",
            "file_sha256": {
                "experiments/estimation_mnar.py": (
                    "00a22be08101313e7214a64798b330470bb462eb5f7c20ed5af2c488c4c47c72"
                ),
                "scripts/syn_mnar.sh": (
                    "e4b62934338ee2cdfd0b5e3bda038ba7020cfc555d846f7faaab1d838e58d46d"
                ),
                "src/utils/generate_synthetic_multitreat_data.py": (
                    "f38ccacdfeebb6f82c00e3ed2549573142bda64b27b53e91d4fd0c2462320d11"
                ),
                "src/utils/save_results.py": (
                    "b3ec4f3e98511cfd60ba318d56119b1e2ba619c132bf9ef004841aaaacfd6570"
                ),
            },
            "repository": "https://github.com/XiaoxiangRdM/MixedSNN",
        },
        "claim_id": "claim_5_source_certificate",
        "config": {
            "dgp_audit": (
                "paper absolute-entry route versus released positive-factor route"
            ),
            "lambdas": list(LAMBDAS),
            "m": M,
            "n": N,
            "rank": RANK,
            "seeds": list(SEEDS),
            "target_treatments": [
                LABELS[level] for level in TARGET_LEVELS
            ],
        },
        "metric_definition_audit": {
            "paper_section_5_1": (
                "mean(abs((prediction - truth) / truth)) over feasible entries"
            ),
            "released_save_results": (
                "mean(abs(prediction - truth)) / treatment_scale"
            ),
            "witness": metric_witness,
        },
        "paper_assignment_proportions": PAPER_ASSIGNMENT_PROPORTIONS,
        "paper_source": {
            "html_sha256": (
                "f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448"
            ),
            "retrieved": "2026-07-28",
            "section_anchor": (
                "https://ar5iv.labs.arxiv.org/html/2603.11942#S5.SS1"
            ),
            "table_2_anchor": (
                "https://ar5iv.labs.arxiv.org/html/2603.11942#S5.T2"
            ),
            "table_3_anchor": (
                "https://ar5iv.labs.arxiv.org/html/2603.11942#S5.T3"
            ),
            "url": "https://ar5iv.labs.arxiv.org/html/2603.11942",
        },
        "paper_source_audit": paper_source_audit(),
        "paper_tables": PAPER_TABLES,
    }
    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "process_workers": 1,
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": list(SEEDS),
    }
    artifact = ROOT / ".openresearch" / "artifacts" / "claim_5"
    artifact.mkdir(parents=True, exist_ok=True)
    raw_json = json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n"
    provenance_json = (
        json.dumps(provenance, allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    )
    (artifact / "raw_result.json").write_text(raw_json)
    (artifact / "provenance.json").write_text(provenance_json)
    print("CLAIM_5_RAW_JSON=" + json.dumps(result, sort_keys=True))
    print("CLAIM_5_PROVENANCE=" + json.dumps(provenance, sort_keys=True))
    print("CLAIM_5_SOURCE_CERTIFICATE_COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
