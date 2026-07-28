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


def max_balanced_biclique_lexicographic(
    edges: np.ndarray,
) -> tuple[np.ndarray, np.ndarray] | None:
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


def networkx_compatible_find_cliques(
    adjacency: dict[int, set[int]],
):
    """Dependency-free transcription of NetworkX 3.6.1 ``find_cliques``.

    NetworkX is BSD-3-Clause licensed. The pinned upstream clique.py SHA-256 is
    480bce4406d9ad9f88a5356e11c6ab11342284d7acfa0969362aa867b8448273.
    """

    if not adjacency:
        return
    neighbors = {
        node: {other for other in adjacency[node] if other != node}
        for node in adjacency
    }
    clique: list[int | None] = []
    candidates = set(adjacency)
    subgraph = candidates.copy()
    stack = []
    clique.append(None)
    pivot = max(
        subgraph,
        key=lambda node: len(candidates & neighbors[node]),
    )
    extensions = candidates - neighbors[pivot]
    try:
        while True:
            if extensions:
                chosen = extensions.pop()
                candidates.remove(chosen)
                clique[-1] = chosen
                chosen_neighbors = neighbors[chosen]
                child_subgraph = subgraph & chosen_neighbors
                if not child_subgraph:
                    yield [int(value) for value in clique if value is not None]
                else:
                    child_candidates = candidates & chosen_neighbors
                    if child_candidates:
                        stack.append((subgraph, candidates, extensions))
                        clique.append(None)
                        subgraph = child_subgraph
                        candidates = child_candidates
                        pivot = max(
                            subgraph,
                            key=lambda node: len(candidates & neighbors[node]),
                        )
                        extensions = candidates - neighbors[pivot]
            else:
                clique.pop()
                subgraph, candidates, extensions = stack.pop()
    except IndexError:
        return


def first_clique_with_balanced_score(
    adjacency: dict[int, set[int]],
    row_count: int,
    target_score: int,
) -> list[int] | None:
    """Return the first author-order clique attaining a certified score.

    This is the same iterative Bron--Kerbosch traversal as
    :func:`networkx_compatible_find_cliques`.  A branch is omitted only when
    the current clique plus every remaining candidate cannot contain
    ``target_score`` nodes from both bipartite sides.
    """

    if not adjacency:
        return None
    neighbors = {
        node: {other for other in adjacency[node] if other != node}
        for node in adjacency
    }
    clique: list[int | None] = [None]
    candidates = set(adjacency)
    subgraph = candidates.copy()
    stack = []
    pivot = max(
        subgraph,
        key=lambda node: len(candidates & neighbors[node]),
    )
    extensions = candidates - neighbors[pivot]
    try:
        while True:
            if extensions:
                chosen = extensions.pop()
                candidates.remove(chosen)
                clique[-1] = chosen
                chosen_neighbors = neighbors[chosen]
                child_subgraph = subgraph & chosen_neighbors
                if not child_subgraph:
                    rows = sum(
                        value is not None and value < row_count
                        for value in clique
                    )
                    columns = len(clique) - rows
                    if min(rows, columns) == target_score:
                        return [
                            int(value)
                            for value in clique
                            if value is not None
                        ]
                else:
                    child_candidates = candidates & chosen_neighbors
                    if child_candidates:
                        current_rows = sum(
                            value is not None and value < row_count
                            for value in clique
                        )
                        current_columns = len(clique) - current_rows
                        possible_rows = current_rows + sum(
                            node < row_count for node in child_candidates
                        )
                        possible_columns = current_columns + sum(
                            node >= row_count for node in child_candidates
                        )
                        if (
                            min(possible_rows, possible_columns)
                            >= target_score
                        ):
                            stack.append(
                                (subgraph, candidates, extensions)
                            )
                            clique.append(None)
                            subgraph = child_subgraph
                            candidates = child_candidates
                            pivot = max(
                                subgraph,
                                key=lambda node: len(
                                    candidates & neighbors[node]
                                ),
                            )
                            extensions = candidates - neighbors[pivot]
            else:
                clique.pop()
                subgraph, candidates, extensions = stack.pop()
    except IndexError:
        return None


def balanced_biclique_optimum_score(edges: np.ndarray) -> int:
    """Find the exact objective with a pruned row-set search.

    A row set can attain score ``k`` exactly when it contains at least ``k``
    rows with at least ``k`` common adjacent columns.  Row sets whose common
    column count is already smaller than their size can never become feasible
    again after extension, so they are safely pruned.  Integer column masks
    keep this certificate inexpensive in the paper's sparse treatment graphs.
    """

    row_count, column_count = edges.shape
    if row_count == 0 or column_count == 0 or not np.any(edges):
        return 0
    if np.all(edges):
        return min(row_count, column_count)

    masks = [
        sum(1 << int(column) for column in np.flatnonzero(edges[row]))
        for row in range(row_count)
    ]
    frontier = [
        ((row,), masks[row])
        for row in range(row_count)
        if masks[row]
    ]
    optimum = 1
    for size in range(2, min(row_count, column_count) + 1):
        extended: list[tuple[tuple[int, ...], int]] = []
        for rows, common_mask in frontier:
            for new_row in range(rows[-1] + 1, row_count):
                new_common = common_mask & masks[new_row]
                if new_common.bit_count() >= size:
                    extended.append((rows + (new_row,), new_common))
        if not extended:
            break
        optimum = size
        frontier = extended
    return optimum


def max_balanced_biclique_full_enumeration(
    edges: np.ndarray,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Unoptimized author-order reference retained for regression controls."""

    row_count, column_count = edges.shape
    if row_count == 0 or column_count == 0:
        return None
    node_count = row_count + column_count
    adjacency: dict[int, set[int]] = {
        node: set() for node in range(node_count)
    }
    for left in range(row_count):
        adjacency[left].update(
            right for right in range(row_count) if right != left
        )
    for left in range(column_count):
        node = row_count + left
        adjacency[node].update(
            row_count + right
            for right in range(column_count)
            if right != left
        )
    for row in range(row_count):
        for column in np.flatnonzero(edges[row]):
            column_node = row_count + int(column)
            adjacency[row].add(column_node)
            adjacency[column_node].add(row)

    best_score = 0
    best = None
    for clique in networkx_compatible_find_cliques(adjacency):
        values = np.sort(np.array(clique, dtype=int))
        rows = values[values < row_count]
        columns = values[values >= row_count] - row_count
        score = min(rows.size, columns.size)
        if score > best_score:
            best_score = int(score)
            best = (rows, columns)
    return best


def max_balanced_biclique(edges: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    """Replicate author order, stopping at the first globally optimal clique."""

    row_count, column_count = edges.shape
    if row_count == 0 or column_count == 0:
        return None
    optimum = balanced_biclique_optimum_score(edges)
    if optimum == 0:
        return None

    node_count = row_count + column_count
    adjacency: dict[int, set[int]] = {
        node: set() for node in range(node_count)
    }
    for left in range(row_count):
        adjacency[left].update(
            right for right in range(row_count) if right != left
        )
    for left in range(column_count):
        node = row_count + left
        adjacency[node].update(
            row_count + right
            for right in range(column_count)
            if right != left
        )
    for row in range(row_count):
        for column in np.flatnonzero(edges[row]):
            column_node = row_count + int(column)
            adjacency[row].add(column_node)
            adjacency[column_node].add(row)

    clique = first_clique_with_balanced_score(
        adjacency,
        row_count,
        optimum,
    )
    if clique is not None:
        values = np.sort(np.array(clique, dtype=int))
        rows = values[values < row_count]
        columns = values[values >= row_count] - row_count
        return rows, columns
    raise AssertionError("optimum certificate was not attained by clique enumeration")


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
) -> tuple[float, bool, tuple[int, int] | None, bool]:
    selected = anchors(design, row, column, mixed)
    if selected is None:
        return float("nan"), False, None, True
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
    invariant_ok = bool(
        np.all(design[selected_rows, column] == 1)
        and (
            np.all(
                design[np.ix_(selected_rows, selected_columns)]
                == design[row, selected_columns][None, :]
            )
            and np.all(design[row, selected_columns] != 0)
            if mixed
            else (
                np.all(design[row, selected_columns] == 1)
                and np.all(
                    design[np.ix_(selected_rows, selected_columns)] == 1
                )
            )
        )
    )
    return (
        prediction,
        bool(feasible),
        (int(selected_rows.size), int(selected_columns.size)),
        invariant_ok,
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
            prediction, feasible, shape, invariant_ok = estimate(
                design, observed, row, column, mixed
            )
            if shape is not None:
                anchor_rows.append(shape[0])
                anchor_columns.append(shape[1])
            if not invariant_ok:
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
        "normalized_absolute_error_sum": float(np.sum(normalized_errors)),
        "feasible_count": feasible_count,
        "feasible_rate_percent": 100 * feasible_count / (M * N),
        "invariant_failures": invariant_failures,
        "paper_defined_entrywise_mre": (
            float(np.mean(entrywise_relative_errors))
            if entrywise_relative_errors
            else None
        ),
        "entrywise_relative_error_sum": float(
            np.sum(entrywise_relative_errors)
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


def solver_order_control() -> dict:
    """Require optimized and full author-order enumeration to match exactly."""

    random = np.random.default_rng(12345)
    cases = 0
    tie_differences = 0
    for row_count in range(1, 7):
        for column_count in range(1, 9):
            for _ in range(20):
                edges = random.random((row_count, column_count)) < 0.5
                if not np.any(edges):
                    continue
                cases += 1
                ordered = max_balanced_biclique(edges)
                full_reference = max_balanced_biclique_full_enumeration(edges)
                lexicographic = max_balanced_biclique_lexicographic(edges)
                if (
                    ordered is None
                    or full_reference is None
                    or lexicographic is None
                ):
                    return {"cases": cases, "passed": False}
                if not (
                    np.array_equal(ordered[0], full_reference[0])
                    and np.array_equal(ordered[1], full_reference[1])
                ):
                    return {
                        "cases": cases,
                        "exact_author_order_match": False,
                        "passed": False,
                    }
                ordered_score = min(ordered[0].size, ordered[1].size)
                lexicographic_score = min(
                    lexicographic[0].size, lexicographic[1].size
                )
                if ordered_score != lexicographic_score:
                    return {"cases": cases, "passed": False}
                tie_differences += int(
                    not (
                        np.array_equal(ordered[0], lexicographic[0])
                        and np.array_equal(ordered[1], lexicographic[1])
                    )
                )
    return {
        "cases": cases,
        "different_equal_score_choices": tie_differences,
        "exact_author_order_match": True,
        "passed": True,
    }


def aggregate(records: list[dict], method: str, metric: str) -> dict:
    values = np.array([record[method][metric] for record in records], dtype=float)
    finite = values[np.isfinite(values)]
    return {
        "finite_count": int(finite.size),
        "mean": float(np.mean(finite)) if finite.size else None,
        "sample_std": (
            float(np.std(finite, ddof=1)) if finite.size > 1 else None
        ),
        "values": [
            float(value) if np.isfinite(value) else None for value in values
        ],
    }


def main() -> int:
    started = time.perf_counter()
    control = exhaustive_solver_control()
    order_control = solver_order_control()
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
        "solver_order_control": order_control,
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
    artifact = ROOT / ".openresearch" / "artifacts" / "claim_4"
    artifact.mkdir(parents=True, exist_ok=True)
    raw_json = json.dumps(
        result, allow_nan=False, indent=2, sort_keys=True
    ) + "\n"
    provenance_json = json.dumps(
        provenance, allow_nan=False, indent=2, sort_keys=True
    ) + "\n"
    (artifact / "raw_result.json").write_text(raw_json)
    (artifact / "provenance.json").write_text(provenance_json)
    print(
        "CLAIM_4_RAW_JSON="
        + json.dumps(result, allow_nan=False, sort_keys=True)
    )
    print(
        "CLAIM_4_PROVENANCE="
        + json.dumps(provenance, allow_nan=False, sort_keys=True)
    )
    if not control["passed"]:
        print("CLAIM_4_GENERATOR_FAILED: finite solver control")
        return 1
    if not order_control["passed"]:
        print("CLAIM_4_GENERATOR_FAILED: solver-order control")
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
