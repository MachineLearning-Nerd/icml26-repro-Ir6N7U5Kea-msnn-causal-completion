"""Exact paper-scale reproduction of MNAR Tables 2 and 3.

The clean-room implementation uses the paper-stated absolute-entry DGP and the
algorithm from XiaoxiangRdM/MixedSNN commit 12bd881.  It also records that the
current released positive-factor DGP does not generate the paper's treatment
proportions.  The clique/PCR kernel is reused from the exact Table 1 audit.
"""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import json
import math
import platform
import statistics
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from repro.claims.claim4_table1.experiment import (  # noqa: E402
    exhaustive_solver_control,
    max_balanced_biclique,
    prediction_and_diagnostics,
    solver_order_control,
)


M, N, RANK = 300, 100, 3
LEVELS = (0, 1, 2, 3, 4)
OBSERVED_LEVELS = (1, 2, 3, 4)
LABELS = {1: "low", 2: "medium", 3: "high"}
SCALES = {0: np.nan, 1: 1.0, 2: 5.0, 3: 25.0, 4: 625.0}
LAMBDAS = (0.05, 0.02)
SEEDS = tuple(range(10))
TARGET_LEVELS = (1, 2, 3)
EPSILON = 0.1
WORKERS = 8

PAPER_TABLES = {
    "0.05": {
        "low": {
            "snn": {"fr_mean": 0.19, "fr_std": 0.07, "mre_mean": 0.349, "mre_std": 0.139},
            "msnn": {"fr_mean": 3.13, "fr_std": 0.41, "mre_mean": 0.117, "mre_std": 0.006},
        },
        "medium": {
            "snn": {"fr_mean": 0.38, "fr_std": 0.12, "mre_mean": 0.390, "mre_std": 0.143},
            "msnn": {"fr_mean": 3.26, "fr_std": 0.34, "mre_mean": 0.114, "mre_std": 0.007},
        },
        "high": {
            "snn": {"fr_mean": 4.17, "fr_std": 0.84, "mre_mean": 0.351, "mre_std": 0.050},
            "msnn": {"fr_mean": 4.52, "fr_std": 0.62, "mre_mean": 0.106, "mre_std": 0.004},
        },
    },
    "0.02": {
        "low": {
            "snn": {"fr_mean": 9.57, "fr_std": 0.85, "mre_mean": 0.366, "mre_std": 0.027},
            "msnn": {"fr_mean": 26.96, "fr_std": 3.50, "mre_mean": 0.129, "mre_std": 0.008},
        },
        "medium": {
            "snn": {"fr_mean": 11.70, "fr_std": 1.62, "mre_mean": 0.379, "mre_std": 0.037},
            "msnn": {"fr_mean": 33.88, "fr_std": 4.20, "mre_mean": 0.135, "mre_std": 0.010},
        },
        "high": {
            "snn": {"fr_mean": 22.66, "fr_std": 2.24, "mre_mean": 0.383, "mre_std": 0.025},
            "msnn": {"fr_mean": 54.16, "fr_std": 4.30, "mre_mean": 0.118, "mre_std": 0.009},
        },
    },
}
PAPER_ASSIGNMENT_PROPORTIONS = {
    "0.05": {
        "low": {"mean_percent": 1.30, "std_percent": 0.06},
        "medium": {"mean_percent": 1.49, "std_percent": 0.06},
        "high": {"mean_percent": 2.50, "std_percent": 0.10},
    },
    "0.02": {
        "low": {"mean_percent": 3.54, "std_percent": 0.12},
        "medium": {"mean_percent": 3.76, "std_percent": 0.12},
        "high": {"mean_percent": 4.59, "std_percent": 0.11},
    },
}


def normalize_rows(values: np.ndarray) -> np.ndarray:
    return values / np.linalg.norm(values, axis=1, keepdims=True)


def mnar_dgp(
    seed: int,
    lam: float,
    mode: str = "paper_absolute_entries",
) -> tuple[dict[int, np.ndarray], np.ndarray, np.ndarray]:
    """Generate the paper DGP or the released-code drift route.

    Appendix B says to take the absolute value of each ground-truth entry.  The
    current public code instead takes absolute values of both latent factors.
    Both routes preserve the same legacy RNG call order.
    """

    random = np.random.RandomState(seed)
    shared_rows = normalize_rows(random.randn(M, RANK))
    if mode == "released_positive_factors":
        shared_rows = np.abs(shared_rows)
    elif mode != "paper_absolute_entries":
        raise ValueError(f"unknown MNAR DGP mode: {mode}")
    potential: dict[int, np.ndarray] = {}
    noise: dict[int, np.ndarray] = {}
    with np.errstate(invalid="ignore"):
        for level in LEVELS:
            columns = normalize_rows(random.randn(N, RANK))
            if mode == "released_positive_factors":
                columns = np.abs(columns)
            columns = columns * SCALES[level]
            signal = shared_rows @ columns.T
            potential[level] = (
                np.abs(signal)
                if mode == "paper_absolute_entries"
                else signal
            )
            noise[level] = (
                random.normal(0, 0.001, (M, N)) * SCALES[level]
            )

    stack = np.stack([potential[level] for level in OBSERVED_LEVELS])
    logits = lam * stack
    logits -= np.max(logits, axis=0, keepdims=True)
    probabilities = np.exp(logits)
    probabilities /= np.sum(probabilities, axis=0, keepdims=True)
    uniforms = random.rand(M, N)
    cumulative = np.cumsum(probabilities, axis=0)
    indices = np.sum(uniforms[None, :, :] > cumulative, axis=0)
    design = np.array(OBSERVED_LEVELS, dtype=np.int8)[indices]

    observed = np.full((M, N), np.nan)
    for level in OBSERVED_LEVELS:
        mask = design == level
        observed[mask] = (potential[level] + noise[level])[mask]
    return potential, design, observed


def anchors(
    design: np.ndarray,
    row: int,
    column: int,
    target_level: int,
    mixed: bool,
) -> tuple[np.ndarray, np.ndarray] | None:
    candidate_rows = np.flatnonzero(design[:, column] == target_level)
    candidate_rows = candidate_rows[candidate_rows != row]
    if mixed:
        candidate_columns = np.flatnonzero(design[row, :] != 0)
    else:
        candidate_columns = np.flatnonzero(
            design[row, :] == target_level
        )
    candidate_columns = candidate_columns[candidate_columns != column]
    if not candidate_rows.size or not candidate_columns.size:
        return None

    block = design[np.ix_(candidate_rows, candidate_columns)]
    if mixed:
        edges = block == design[row, candidate_columns][None, :]
    else:
        edges = block == target_level
    selected = max_balanced_biclique(edges)
    if selected is None:
        return None
    selected_rows, selected_columns = selected
    return candidate_rows[selected_rows], candidate_columns[selected_columns]


def estimate(
    design: np.ndarray,
    observed: np.ndarray,
    row: int,
    column: int,
    target_level: int,
    mixed: bool,
) -> tuple[float, bool, tuple[int, int] | None, bool]:
    selected = anchors(
        design,
        row,
        column,
        target_level,
        mixed,
    )
    if selected is None:
        return float("nan"), False, None, True
    selected_rows, selected_columns = selected

    if mixed:
        column_scales = np.array(
            [
                SCALES[int(level)]
                for level in design[row, selected_columns]
            ]
        )
        anchor = (
            observed[np.ix_(selected_rows, selected_columns)]
            / column_scales
        )
        query = observed[row, selected_columns] / column_scales
        target = observed[selected_rows, column]
    else:
        anchor = observed[np.ix_(selected_rows, selected_columns)]
        query = observed[row, selected_columns]
        target = observed[selected_rows, column]

    if not (
        np.isfinite(anchor).all()
        and np.isfinite(query).all()
        and np.isfinite(target).all()
    ):
        raise AssertionError("selected anchor contains unavailable data")
    prediction, train_error, subspace_error = prediction_and_diagnostics(
        anchor,
        query,
        target,
    )
    feasible = train_error <= EPSILON and subspace_error <= EPSILON
    if not mixed and selected_rows.size == selected_columns.size == 1:
        feasible = False

    if mixed:
        target_levels = design[row, selected_columns]
        invariant_ok = bool(
            np.all(design[selected_rows, column] == target_level)
            and np.all(target_levels != 0)
            and np.all(
                design[np.ix_(selected_rows, selected_columns)]
                == target_levels[None, :]
            )
        )
    else:
        invariant_ok = bool(
            np.all(design[selected_rows, column] == target_level)
            and np.all(design[row, selected_columns] == target_level)
            and np.all(
                design[np.ix_(selected_rows, selected_columns)]
                == target_level
            )
        )
    return (
        prediction,
        bool(feasible),
        (int(selected_rows.size), int(selected_columns.size)),
        invariant_ok,
    )


def run_method(
    potential: dict[int, np.ndarray],
    design: np.ndarray,
    observed: np.ndarray,
    target_level: int,
    mixed: bool,
) -> dict:
    feasible_count = 0
    normalized_error_sum = 0.0
    entrywise_relative_error_sum = 0.0
    anchor_rows: list[int] = []
    anchor_columns: list[int] = []
    invariant_failures = 0

    for row in range(M):
        for column in range(N):
            prediction, feasible, shape, invariant_ok = estimate(
                design,
                observed,
                row,
                column,
                target_level,
                mixed,
            )
            if shape is not None:
                anchor_rows.append(shape[0])
                anchor_columns.append(shape[1])
            if not invariant_ok:
                invariant_failures += 1
            if not feasible:
                continue
            feasible_count += 1
            truth = float(potential[target_level][row, column])
            absolute_error = abs(prediction - truth)
            normalized_error_sum += absolute_error / SCALES[target_level]
            entrywise_relative_error_sum += absolute_error / abs(truth)

    return {
        "anchor_columns_median": (
            float(np.median(anchor_columns)) if anchor_columns else None
        ),
        "anchor_rows_median": (
            float(np.median(anchor_rows)) if anchor_rows else None
        ),
        "code_normalized_mae": (
            normalized_error_sum / feasible_count
            if feasible_count
            else None
        ),
        "entrywise_relative_error_sum": entrywise_relative_error_sum,
        "feasible_count": feasible_count,
        "feasible_rate_percent": 100 * feasible_count / (M * N),
        "invariant_failures": invariant_failures,
        "normalized_absolute_error_sum": normalized_error_sum,
        "paper_defined_entrywise_mre": (
            entrywise_relative_error_sum / feasible_count
            if feasible_count
            else None
        ),
    }


def run_task(task: tuple[float, int, int]) -> dict:
    started = time.perf_counter()
    lam, target_level, seed = task
    potential, design, observed = mnar_dgp(seed, lam)
    record = {
        "design_target_proportion": float(
            np.mean(design == target_level)
        ),
        "lambda": lam,
        "seed": seed,
        "target_level": target_level,
        "treatment": LABELS[target_level],
        "msnn": run_method(
            potential,
            design,
            observed,
            target_level,
            mixed=True,
        ),
        "snn": run_method(
            potential,
            design,
            observed,
            target_level,
            mixed=False,
        ),
    }
    record["task_runtime_seconds"] = round(
        time.perf_counter() - started,
        6,
    )
    return record


def aggregate(records: list[dict], method: str, metric: str) -> dict:
    values = [
        record[method][metric]
        for record in records
        if record[method][metric] is not None
    ]
    return {
        "finite_count": len(values),
        "mean": statistics.fmean(values) if values else None,
        "sample_std": (
            statistics.stdev(values) if len(values) > 1 else None
        ),
        "values": [
            record[method][metric]
            for record in records
        ],
    }


def paper_source_audit() -> dict:
    msnn_fr = []
    snn_fr = []
    error_ratios = []
    for table in PAPER_TABLES.values():
        for treatment in table.values():
            msnn_fr.append(treatment["msnn"]["fr_mean"])
            snn_fr.append(treatment["snn"]["fr_mean"])
            error_ratios.append(
                treatment["snn"]["mre_mean"]
                / treatment["msnn"]["mre_mean"]
            )
    return {
        "all_paper_fr_cells_msnn_gt_snn": all(
            msnn > snn for msnn, snn in zip(msnn_fr, snn_fr)
        ),
        "error_reduction_ratio_max": max(error_ratios),
        "error_reduction_ratio_min": min(error_ratios),
        "error_reduction_ratios": error_ratios,
        "ratios_outside_closed_2_to_3": sum(
            not 2.0 <= ratio <= 3.0 for ratio in error_ratios
        ),
        "msnn_fr_max_percent": max(msnn_fr),
        "msnn_fr_min_percent": min(msnn_fr),
        "snn_fr_max_percent": max(snn_fr),
        "snn_fr_min_percent": min(snn_fr),
    }


def assignment_aggregates(records: list[dict]) -> dict:
    output: dict[str, dict] = {}
    for lam in LAMBDAS:
        lam_key = f"{lam:.2f}"
        output[lam_key] = {}
        for target_level in TARGET_LEVELS:
            values = [
                100 * record["design_target_proportion"]
                for record in records
                if math.isclose(record["lambda"], lam)
                and record["target_level"] == target_level
            ]
            output[lam_key][LABELS[target_level]] = {
                "mean_percent": statistics.fmean(values),
                "sample_std_percent": statistics.stdev(values),
                "values_percent": values,
            }
    return output


def released_code_assignment_audit() -> dict:
    output: dict[str, dict] = {}
    for lam in LAMBDAS:
        lam_key = f"{lam:.2f}"
        values_by_level = {level: [] for level in TARGET_LEVELS}
        for seed in SEEDS:
            _, design, _ = mnar_dgp(
                seed,
                lam,
                mode="released_positive_factors",
            )
            for level in TARGET_LEVELS:
                values_by_level[level].append(
                    100 * float(np.mean(design == level))
                )
        output[lam_key] = {
            LABELS[level]: {
                "mean_percent": statistics.fmean(values_by_level[level]),
                "sample_std_percent": statistics.stdev(
                    values_by_level[level]
                ),
                "values_percent": values_by_level[level],
            }
            for level in TARGET_LEVELS
        }
    return output


def main() -> int:
    started = time.perf_counter()
    solver_control = exhaustive_solver_control()
    order_control = solver_order_control()
    tasks = [
        (lam, target_level, seed)
        for lam in LAMBDAS
        for target_level in TARGET_LEVELS
        for seed in SEEDS
    ]
    records: list[dict] = []
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        future_to_task = {
            executor.submit(run_task, task): task for task in tasks
        }
        for completed, future in enumerate(as_completed(future_to_task), 1):
            record = future.result()
            records.append(record)
            print(
                "CLAIM_5_PROGRESS "
                f"{completed}/{len(tasks)} "
                f"lambda={record['lambda']:.2f} "
                f"treatment={record['treatment']} "
                f"seed={record['seed']} "
                f"seconds={record['task_runtime_seconds']:.3f}",
                flush=True,
            )
    records.sort(
        key=lambda item: (
            -item["lambda"],
            item["target_level"],
            item["seed"],
        )
    )

    aggregates: dict[str, dict] = {}
    for lam in LAMBDAS:
        lam_key = f"{lam:.2f}"
        aggregates[lam_key] = {}
        for target_level in TARGET_LEVELS:
            treatment = LABELS[target_level]
            selected = [
                record
                for record in records
                if math.isclose(record["lambda"], lam)
                and record["target_level"] == target_level
            ]
            aggregates[lam_key][treatment] = {
                method: {
                    metric: aggregate(selected, method, metric)
                    for metric in (
                        "feasible_rate_percent",
                        "code_normalized_mae",
                        "paper_defined_entrywise_mre",
                    )
                }
                for method in ("snn", "msnn")
            }

    result = {
        "aggregates": aggregates,
        "author_source": {
            "commit": "12bd881f82a93cd223989a6a8cd082a3dc9a0e47",
            "repository": "https://github.com/XiaoxiangRdM/MixedSNN",
        },
        "assignment_proportion_aggregates": assignment_aggregates(records),
        "claim_id": "claim_5_generator",
        "config": {
            "dgp": "paper Appendix B: absolute value of each ground-truth entry",
            "feasibility_epsilons": [EPSILON, EPSILON],
            "lambdas": list(LAMBDAS),
            "m": M,
            "n": N,
            "n_neighbors": 1,
            "noise_scale_relative": 0.001,
            "rank": RANK,
            "seeds": list(SEEDS),
            "target_treatments": [
                LABELS[level] for level in TARGET_LEVELS
            ],
            "targets_per_cell": M * N,
            "workers": WORKERS,
        },
        "paper_source_audit": paper_source_audit(),
        "paper_assignment_proportions": PAPER_ASSIGNMENT_PROPORTIONS,
        "paper_tables": PAPER_TABLES,
        "per_cell_seed": records,
        "released_positive_factor_assignment_audit": (
            released_code_assignment_audit()
        ),
        "solver_control": solver_control,
        "solver_order_control": order_control,
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
        "process_workers": WORKERS,
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": list(SEEDS),
    }
    artifact = ROOT / ".openresearch" / "artifacts" / "claim_5"
    artifact.mkdir(parents=True, exist_ok=True)
    raw_json = json.dumps(
        result,
        allow_nan=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    provenance_json = json.dumps(
        provenance,
        allow_nan=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    (artifact / "raw_result.json").write_text(raw_json)
    (artifact / "provenance.json").write_text(provenance_json)
    print(
        "CLAIM_5_RAW_JSON="
        + json.dumps(result, allow_nan=False, sort_keys=True)
    )
    print(
        "CLAIM_5_PROVENANCE="
        + json.dumps(provenance, allow_nan=False, sort_keys=True)
    )

    if not solver_control["passed"] or not order_control["passed"]:
        print("CLAIM_5_GENERATOR_FAILED: clique solver control")
        return 1
    if len(records) != 60:
        print("CLAIM_5_GENERATOR_FAILED: incomplete cell/seed grid")
        return 1
    if any(
        record[method]["invariant_failures"]
        for record in records
        for method in ("snn", "msnn")
    ):
        print("CLAIM_5_GENERATOR_FAILED: selected-edge invariant")
        return 1
    print("CLAIM_5_GENERATOR_COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
