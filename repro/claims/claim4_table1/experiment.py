"""Author-code-equivalent reproduction of Table 1's low-treatment cells.

The implementation is clean-room NumPy so the baseline's frozen lockfile does
not change. Its protocol is pinned to XiaoxiangRdM/MixedSNN commit 12bd881.
"""

from __future__ import annotations

import itertools
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
M, N, RANK = 300, 100, 3
LEVELS = (0, 1, 2, 3, 4)
SCALES = {0: np.nan, 1: 1.0, 2: 5.0, 3: 25.0, 4: 625.0}
PROBS = (0.115, 0.01, 0.025, 0.05, 0.8)
SEEDS = tuple(range(10))
EPSILON = 0.1


def normalize_rows(values: np.ndarray) -> np.ndarray:
    return values / np.linalg.norm(values, axis=1, keepdims=True)


def author_dgp(seed: int) -> tuple[dict[int, np.ndarray], np.ndarray, np.ndarray]:
    """Match the authors' legacy NumPy RNG call order, including level zero."""

    random = np.random.RandomState(seed)
    shared_rows = normalize_rows(random.randn(M, RANK))
    potential: dict[int, np.ndarray] = {}
    noise: dict[int, np.ndarray] = {}
    for level in LEVELS:
        columns = normalize_rows(random.randn(N, RANK)) * SCALES[level]
        potential[level] = shared_rows @ columns.T
        noise[level] = random.normal(0, 0.001, (M, N)) * SCALES[level]

    uniforms = random.rand(M, N)
    cumulative = np.cumsum(PROBS)
    design = np.empty((M, N), dtype=np.int8)
    lower = 0.0
    for level, upper in zip(LEVELS, cumulative):
        design[(uniforms > lower) & (uniforms <= upper)] = level
        lower = upper

    observed = np.full((M, N), np.nan)
    for level in (1, 2, 3, 4):
        mask = design == level
        observed[mask] = (potential[level] + noise[level])[mask]
    return potential, design, observed


def max_balanced_biclique(edges: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    """Exact objective used by the released code, with an explicit tie rule.

    The author implementation enumerates maximal cliques and maximizes
    min(number of rows, number of columns). NetworkX documents enumeration
    order as arbitrary. Here every row subset is enumerated, closed to a
    maximal biclique, and equal-score ties use lexicographic indices.
    """

    row_count, column_count = edges.shape
    if row_count == 0 or column_count == 0:
        return None
    if np.all(edges):
        return np.arange(row_count), np.arange(column_count)
    if row_count > 20:
        raise RuntimeError(f"low-treatment enumeration guard exceeded: {row_count}")

    candidates: dict[tuple[tuple[int, ...], tuple[int, ...]], None] = {}
    for bits in range(1, 1 << row_count):
        rows = np.flatnonzero(
            np.fromiter(
                ((bits >> index) & 1 for index in range(row_count)),
                dtype=bool,
            )
        )
        columns = np.flatnonzero(np.all(edges[rows], axis=0))
        if columns.size == 0:
            continue
        closed_rows = np.flatnonzero(np.all(edges[:, columns], axis=1))
        closed_columns = np.flatnonzero(np.all(edges[closed_rows], axis=0))
        candidates[
            (
                tuple(int(value) for value in closed_rows),
                tuple(int(value) for value in closed_columns),
            )
        ] = None
    if not candidates:
        return None
    chosen = min(
        candidates,
        key=lambda item: (
            -min(len(item[0]), len(item[1])),
            item[0],
            item[1],
        ),
    )
    return np.array(chosen[0], dtype=int), np.array(chosen[1], dtype=int)


def universal_rank(singular: np.ndarray, rows: int, columns: int) -> int:
    ratio = rows / columns
    omega = 0.56 * ratio**3 - 0.95 * ratio**2 + 1.43 + 1.82 * ratio
    threshold = omega * np.median(singular)
    return max(int(np.count_nonzero(singular > threshold)), 1)


def prediction_and_diagnostics(
    anchor: np.ndarray,
    query: np.ndarray,
    target: np.ndarray,
) -> tuple[float, float, float]:
    """Released PCR, train-error, and subspace-inclusion calculations."""

    regression_matrix = anchor.T
    left, singular, right_t = np.linalg.svd(
        regression_matrix, full_matrices=False
    )
    rank = universal_rank(
        singular, regression_matrix.shape[0], regression_matrix.shape[1]
    )
    kept_singular = singular[:rank]
    kept_left = left[:, :rank]
    kept_right = right_t[:rank]
    beta = ((kept_right.T / kept_singular) @ kept_left.T) @ query
    prediction = float(target @ beta)
    query_norm = np.linalg.norm(query)
    target_norm = np.linalg.norm(target)
    if query_norm == 0 or target_norm == 0:
        return prediction, float("inf"), float("inf")
    train_error = (
        np.linalg.norm(regression_matrix @ beta - query) / query_norm
    ) ** 2
    residual = (
        np.eye(kept_right.shape[1]) - kept_right.T @ kept_right
    ) @ target
    subspace_error = (np.linalg.norm(residual) / target_norm) ** 2
    return prediction, float(train_error), float(subspace_error)


def anchors(
    design: np.ndarray,
    row: int,
    column: int,
    mixed: bool,
) -> tuple[np.ndarray, np.ndarray] | None:
    candidate_rows = np.flatnonzero(design[:, column] == 1)
    candidate_rows = candidate_rows[candidate_rows != row]
    if mixed:
        candidate_columns = np.flatnonzero(design[row, :] != 0)
    else:
        candidate_columns = np.flatnonzero(design[row, :] == 1)
    candidate_columns = candidate_columns[candidate_columns != column]
    if not candidate_rows.size or not candidate_columns.size:
        return None
    block = design[np.ix_(candidate_rows, candidate_columns)]
    if mixed:
        edges = block == design[row, candidate_columns][None, :]
    else:
        edges = block == 1
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
    mixed: bool,
) -> tuple[float, bool, tuple[int, int] | None]:
    selected = anchors(design, row, column, mixed)
    if selected is None:
        return float("nan"), False, None
    selected_rows, selected_columns = selected
    if mixed:
        column_scales = np.array(
            [SCALES[int(level)] for level in design[row, selected_columns]]
        )
        anchor = observed[np.ix_(selected_rows, selected_columns)] / column_scales
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
        anchor, query, target
    )
    feasible = train_error <= EPSILON and subspace_error <= EPSILON
    if not mixed and selected_rows.size == selected_columns.size == 1:
        feasible = False
    return prediction, bool(feasible), (
        int(selected_rows.size),
        int(selected_columns.size),
    )


def audit_selected_edges(
    design: np.ndarray,
    row: int,
    column: int,
    mixed: bool,
) -> bool:
    selected = anchors(design, row, column, mixed)
    if selected is None:
        return True
    selected_rows, selected_columns = selected
    if np.any(design[selected_rows, column] != 1):
        return False
    if mixed:
        target_levels = design[row, selected_columns]
        return bool(
            np.all(target_levels != 0)
            and np.all(
                design[np.ix_(selected_rows, selected_columns)]
                == target_levels[None, :]
            )
        )
    return bool(
        np.all(design[row, selected_columns] == 1)
        and np.all(design[np.ix_(selected_rows, selected_columns)] == 1)
    )


def run_method(
    potential: dict[int, np.ndarray],
    design: np.ndarray,
    observed: np.ndarray,
    mixed: bool,
) -> dict:
    feasible_count = 0
    normalized_errors: list[float] = []
    entrywise_relative_errors: list[float] = []
    anchor_rows: list[int] = []
    anchor_columns: list[int] = []
    invariant_failures = 0
    for row in range(M):
        for column in range(N):
            prediction, feasible, shape = estimate(
                design, observed, row, column, mixed
            )
            if shape is not None:
                anchor_rows.append(shape[0])
                anchor_columns.append(shape[1])
            if not audit_selected_edges(design, row, column, mixed):
                invariant_failures += 1
            if not feasible:
                continue
            feasible_count += 1
            truth = float(potential[1][row, column])
            absolute_error = abs(prediction - truth)
            normalized_errors.append(absolute_error / SCALES[1])
            entrywise_relative_errors.append(absolute_error / abs(truth))
    return {
        "anchor_columns_median": (
            float(np.median(anchor_columns)) if anchor_columns else None
        ),
        "anchor_rows_median": (
            float(np.median(anchor_rows)) if anchor_rows else None
        ),
        "code_normalized_mae": (
            float(np.mean(normalized_errors)) if normalized_errors else None
        ),
        "feasible_count": feasible_count,
        "feasible_rate_percent": 100 * feasible_count / (M * N),
        "invariant_failures": invariant_failures,
        "paper_defined_entrywise_mre": (
            float(np.mean(entrywise_relative_errors))
            if entrywise_relative_errors
            else None
        ),
    }


def run_seed(seed: int) -> dict:
    potential, design, observed = author_dgp(seed)
    return {
        "design_low_proportion": float(np.mean(design == 1)),
        "msnn": run_method(potential, design, observed, mixed=True),
        "seed": seed,
        "snn": run_method(potential, design, observed, mixed=False),
    }


def exhaustive_solver_control() -> dict:
    """Check the solver's objective over every nonzero binary matrix through 3x3."""

    cases = 0
    for row_count in (1, 2, 3):
        for column_count in (1, 2, 3):
            for values in itertools.product(
                (False, True), repeat=row_count * column_count
            ):
                edges = np.array(values, dtype=bool).reshape(
                    row_count, column_count
                )
                if not np.any(edges):
                    continue
                cases += 1
                selected = max_balanced_biclique(edges)
                if selected is None:
                    return {"cases": cases, "passed": False}
                achieved = min(selected[0].size, selected[1].size)
                brute = 0
                for row_bits in range(1, 1 << row_count):
                    rows = [
                        index
                        for index in range(row_count)
                        if (row_bits >> index) & 1
                    ]
                    for column_bits in range(1, 1 << column_count):
                        columns = [
                            index
                            for index in range(column_count)
                            if (column_bits >> index) & 1
                        ]
                        if np.all(edges[np.ix_(rows, columns)]):
                            brute = max(brute, min(len(rows), len(columns)))
                if achieved != brute:
                    return {"cases": cases, "passed": False}
    return {"cases": cases, "passed": True}


def aggregate(records: list[dict], method: str, metric: str) -> dict:
    values = np.array([record[method][metric] for record in records], dtype=float)
    return {
        "mean": float(np.mean(values)),
        "sample_std": float(np.std(values, ddof=1)),
        "values": [float(value) for value in values],
    }


def main() -> int:
    started = time.perf_counter()
    control = exhaustive_solver_control()
    with ProcessPoolExecutor(max_workers=8) as executor:
        records = list(executor.map(run_seed, SEEDS))
    records.sort(key=lambda item: item["seed"])
    aggregates = {
        method: {
            metric: aggregate(records, method, metric)
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
        "claim_id": "claim_4_generator",
        "config": {
            "feasibility_epsilons": [EPSILON, EPSILON],
            "m": M,
            "n": N,
            "n_neighbors": 1,
            "noise_scale_relative": 0.001,
            "rank": RANK,
            "seeds": list(SEEDS),
            "target_treatment": "low",
            "target_treatment_probability": 0.01,
        },
        "paper_table_1": {
            "msnn_code_labeled_mre_mean": 0.0391,
            "msnn_code_labeled_mre_std": 0.0109,
            "msnn_fr_percent_mean": 4.69,
            "msnn_fr_percent_std": 1.11,
            "snn_code_labeled_mre_mean": 0.806,
            "snn_code_labeled_mre_std": 0.240,
            "snn_fr_percent_mean": 0.03,
            "snn_fr_percent_std": 0.00,
        },
        "per_seed": records,
        "solver_control": control,
    }
    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "process_workers": 8,
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": list(SEEDS),
    }
    print(f"CLAIM_4_RAW_JSON={json.dumps(result, sort_keys=True)}")
    print(f"CLAIM_4_PROVENANCE={json.dumps(provenance, sort_keys=True)}")
    if not control["passed"]:
        print("CLAIM_4_GENERATOR_FAILED: finite solver control")
        return 1
    if any(
        record[method]["invariant_failures"]
        for record in records
        for method in ("snn", "msnn")
    ):
        print("CLAIM_4_GENERATOR_FAILED: selected-edge invariant")
        return 1
    print("CLAIM_4_GENERATOR_COMPLETED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
