"""Fail-closed verifier for the exact Claim 5 contract."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_5" / "raw_result.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def main() -> int:
    started = time.perf_counter()
    raw = json.loads(
        RAW.read_text(),
        parse_constant=reject_nonstandard_constant,
    )
    if raw["config"] != {
        "dgp": "paper Appendix B: absolute value of each ground-truth entry",
        "feasibility_epsilons": [0.1, 0.1],
        "lambdas": [0.05, 0.02],
        "m": 300,
        "n": 100,
        "n_neighbors": 1,
        "noise_scale_relative": 0.001,
        "rank": 3,
        "seeds": list(range(10)),
        "target_treatments": ["low", "medium", "high"],
        "targets_per_cell": 30000,
        "workers": 8,
    }:
        print("CLAIM_5_FAIL: protocol drift")
        return 1
    if (
        not raw["solver_control"]["passed"]
        or not raw["solver_order_control"]["passed"]
    ):
        print("CLAIM_5_FAIL: clique solver controls")
        return 1
    if any(
        record[method]["invariant_failures"]
        for record in raw["per_cell_seed"]
        for method in ("snn", "msnn")
    ):
        print("CLAIM_5_FAIL: selected anchor invariant")
        return 1

    checked = subprocess.run(
        [sys.executable, str(CHECKER)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_5_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        print(checked.stderr)
        return 1

    metric_control = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--mutate-metric-substitution",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    print(
        "CLAIM_5_NEGATIVE_CONTROL_METRIC="
        f"{metric_control.stdout.strip()}"
    )
    if metric_control.returncode == 0:
        print("CLAIM_5_FAIL: metric mutation was accepted")
        return 1

    source_control = subprocess.run(
        [sys.executable, str(CHECKER), "--mutate-source-range"],
        check=False,
        capture_output=True,
        text=True,
    )
    print(
        "CLAIM_5_NEGATIVE_CONTROL_SOURCE="
        f"{source_control.stdout.strip()}"
    )
    if source_control.returncode == 0:
        print("CLAIM_5_FAIL: source-range mutation was accepted")
        return 1

    source = raw["paper_source_audit"]
    if (
        source["msnn_fr_max_percent"] <= 26.0
        or source["snn_fr_max_percent"] <= 5.0
        or source["ratios_outside_closed_2_to_3"] == 0
    ):
        print("CLAIM_5_FAIL: source-table contradiction disappeared")
        return 1

    cell_summary: dict[str, dict] = {}
    code_cells_matching_paper = 0
    total_code_cells = 0
    for lam, treatments in raw["aggregates"].items():
        cell_summary[lam] = {}
        for treatment, methods in treatments.items():
            cell_summary[lam][treatment] = {}
            for method, metrics in methods.items():
                paper = raw["paper_tables"][lam][treatment][method]
                observed = {
                    "code_normalized_mae": (
                        metrics["code_normalized_mae"]["mean"]
                    ),
                    "feasible_rate_percent": (
                        metrics["feasible_rate_percent"]["mean"]
                    ),
                    "paper_defined_entrywise_mre": (
                        metrics["paper_defined_entrywise_mre"]["mean"]
                    ),
                }
                cell_summary[lam][treatment][method] = observed
                total_code_cells += 2
                code_cells_matching_paper += int(
                    round(observed["feasible_rate_percent"], 2)
                    == paper["fr_mean"]
                )
                code_cells_matching_paper += int(
                    round(observed["code_normalized_mae"], 3)
                    == paper["mre_mean"]
                )

    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": raw["config"]["seeds"],
    }
    result = {
        "claim_id": "claim_5",
        "code_cells_matching_paper_after_display_rounding": (
            code_cells_matching_paper
        ),
        "evidence_type": (
            "paper-scale Appendix-B-DGP Tables 2-3 run, released-code "
            "DGP drift audit, source-table contradiction, and dual metric audit"
        ),
        "negative_control_exit_codes": {
            "metric_substitution": metric_control.returncode,
            "source_range": source_control.returncode,
        },
        "source_table_falsification": {
            "error_ratios_outside_2_to_3": (
                source["ratios_outside_closed_2_to_3"]
            ),
            "msnn_fr_actual_range_percent": [
                source["msnn_fr_min_percent"],
                source["msnn_fr_max_percent"],
            ],
            "snn_fr_actual_max_percent": source["snn_fr_max_percent"],
        },
        "total_code_cells_compared": total_code_cells,
        "verdict": "FALSIFIED",
    }
    print(f"CLAIM_5_CELL_SUMMARY={json.dumps(cell_summary, sort_keys=True)}")
    print(
        "CLAIM_5_PROVENANCE_FINAL="
        f"{json.dumps(provenance, sort_keys=True)}"
    )
    print(f"CLAIM_RESULT_JSON={json.dumps(result, sort_keys=True)}")
    print("CLAIM_5_FALSIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
