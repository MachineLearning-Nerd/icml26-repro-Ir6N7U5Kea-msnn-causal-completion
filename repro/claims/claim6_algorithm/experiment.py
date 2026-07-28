"""Paper-scale noisy audit of the mixed-anchor construction (Algorithms 2–3).

The run is deterministic and prints all raw per-seed evidence to stdout because
OpenResearch local mode persists run logs as the evidence channel.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
M = 300
N = 100
RANK = 3
SIGMA = 0.001
TARGET_TREATMENT = 1
F_SCALE = {1: 1.0, 2: 5.0, 3: 25.0, 4: 625.0}
LEVELS = np.array([0, 1, 2, 3, 4], dtype=int)
PROBABILITIES = np.array([0.115, 0.01, 0.025, 0.05, 0.8])
SEEDS = tuple(range(10))
TARGETS_PER_SEED = 40


@dataclass(frozen=True)
class Clique:
    rows: np.ndarray
    cols: np.ndarray


def _unit_rows(values: np.ndarray) -> np.ndarray:
    return values / np.linalg.norm(values, axis=1, keepdims=True)


def make_potential_outcomes(seed: int, shared_rows: bool) -> dict[int, np.ndarray]:
    rng = np.random.default_rng(10_000 + seed)
    v_base = _unit_rows(rng.normal(size=(N, RANK)))
    shared = _unit_rows(rng.normal(size=(M, RANK)))
    outcomes = {}
    for treatment, scale in F_SCALE.items():
        rows = shared if shared_rows else _unit_rows(rng.normal(size=(M, RANK)))
        outcomes[treatment] = scale * (rows @ v_base.T)
    return outcomes


def assign_mcar(seed: int) -> np.ndarray:
    rng = np.random.default_rng(20_000 + seed)
    return rng.choice(LEVELS, size=(M, N), p=PROBABILITIES)


def observe(
    assignment: np.ndarray,
    outcomes: dict[int, np.ndarray],
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    observed = np.full((M, N), np.nan)
    for treatment, scale in F_SCALE.items():
        selected = assignment == treatment
        noise = rng.normal(scale=scale * SIGMA, size=int(selected.sum()))
        observed[selected] = outcomes[treatment][selected] + noise
    return observed


def incidence_matrix(
    assignment: np.ndarray,
    i: int,
    j: int,
    treatment: int,
) -> np.ndarray:
    row_matches = assignment[:, j] == treatment
    column_treatments = assignment[i, :]
    matrix = (
        row_matches[:, None]
        & (assignment == column_treatments[None, :])
        & (column_treatments[None, :] != 0)
    )
    matrix[i, :] = False
    matrix[:, j] = False
    return matrix


def maximum_edge_biclique(matrix: np.ndarray) -> Clique | None:
    """Exact maximum-edge biclique with deterministic tie-breaking.

    Algorithm 3 leaves ``maxBiclique`` abstract. For the low-treatment regime,
    candidate row counts are small enough to enumerate every nonempty row subset.
    Each subset is paired with all common neighboring columns, so maximizing its
    edge count is globally exact for this stated objective.
    """

    candidate_rows = np.flatnonzero(matrix.any(axis=1))
    if not len(candidate_rows):
        return None
    if len(candidate_rows) > 20:
        raise RuntimeError(
            f"exact enumeration guard exceeded: {len(candidate_rows)} candidate rows"
        )
    best: tuple[tuple[int, int, int, tuple[int, ...], tuple[int, ...]], Clique] | None = None
    for mask in range(1, 1 << len(candidate_rows)):
        chosen = candidate_rows[
            [position for position in range(len(candidate_rows)) if mask >> position & 1]
        ]
        cols = np.flatnonzero(matrix[chosen].all(axis=0))
        if not len(cols):
            continue
        key = (
            len(chosen) * len(cols),
            len(chosen) + len(cols),
            len(chosen),
            tuple(-int(value) for value in chosen),
            tuple(-int(value) for value in cols),
        )
        clique = Clique(rows=chosen, cols=cols)
        if best is None or key > best[0]:
            best = (key, clique)
    return None if best is None else best[1]


def audit_clique(
    assignment: np.ndarray,
    matrix: np.ndarray,
    clique: Clique,
    i: int,
    j: int,
    treatment: int,
) -> None:
    if not matrix[np.ix_(clique.rows, clique.cols)].all():
        raise AssertionError("selected rows and columns are not a bipartite clique")
    if not np.all(assignment[clique.rows, j] == treatment):
        raise AssertionError("mixed anchor rows do not preserve target treatment")
    expected = assignment[i, clique.cols]
    if np.any(expected == 0):
        raise AssertionError("mixed anchor columns include an unobserved target-row entry")
    if not np.all(assignment[np.ix_(clique.rows, clique.cols)] == expected[None, :]):
        raise AssertionError("anchor-column treatments do not match the target row")


def corrupted_edge_control(
    assignment: np.ndarray,
    matrix: np.ndarray,
    clique: Clique,
    i: int,
    j: int,
    treatment: int,
) -> bool:
    for col in range(N):
        if col == j or col in clique.cols:
            continue
        if not matrix[clique.rows, col].all():
            corrupted = Clique(
                rows=clique.rows,
                cols=np.append(clique.cols, col),
            )
            try:
                audit_clique(assignment, matrix, corrupted, i, j, treatment)
            except AssertionError:
                return True
            return False
    raise RuntimeError("could not construct a corrupted-edge control")


def estimate(
    assignment: np.ndarray,
    observed: np.ndarray,
    clique: Clique,
    i: int,
    j: int,
    treatment: int,
) -> float | None:
    if len(clique.rows) < RANK or len(clique.cols) < RANK:
        return None
    column_treatments = assignment[i, clique.cols]
    scales = np.array([F_SCALE[int(level)] for level in column_treatments])
    anchor = observed[np.ix_(clique.rows, clique.cols)] / scales[None, :]
    q_weighted = observed[i, clique.cols] / scales
    x_target = observed[clique.rows, j]
    u, singular, vt = np.linalg.svd(anchor, full_matrices=False)
    keep = min(RANK, int((singular > 1e-12).sum()))
    if keep < RANK:
        return None
    beta = (u[:, :keep] * (1.0 / singular[:keep])) @ (
        vt[:keep] @ q_weighted
    )
    return float(x_target @ beta)


def run_seed(seed: int) -> tuple[dict, list[float], list[float]]:
    assignment = assign_mcar(seed)
    valid_outcomes = make_potential_outcomes(seed, shared_rows=True)
    invalid_outcomes = make_potential_outcomes(seed, shared_rows=False)
    valid_observed = observe(assignment, valid_outcomes, 30_000 + seed)
    invalid_observed = observe(assignment, invalid_outcomes, 40_000 + seed)
    target_rng = np.random.default_rng(50_000 + seed)
    targets = target_rng.choice(M * N, size=TARGETS_PER_SEED, replace=False)

    valid_scaled_errors: list[float] = []
    invalid_scaled_errors: list[float] = []
    clique_count = 0
    estimable_count = 0
    mixed_count = 0
    invariant_checks = 0
    control_rejections = 0
    max_candidate_rows = 0
    for flat in targets:
        i, j = divmod(int(flat), N)
        matrix = incidence_matrix(assignment, i, j, TARGET_TREATMENT)
        max_candidate_rows = max(max_candidate_rows, int(matrix.any(axis=1).sum()))
        clique = maximum_edge_biclique(matrix)
        if clique is None:
            continue
        clique_count += 1
        audit_clique(assignment, matrix, clique, i, j, TARGET_TREATMENT)
        invariant_checks += 1
        control_rejections += int(
            corrupted_edge_control(
                assignment,
                matrix,
                clique,
                i,
                j,
                TARGET_TREATMENT,
            )
        )
        column_levels = np.unique(assignment[i, clique.cols])
        mixed_count += int(len(column_levels) >= 2)
        valid_estimate = estimate(
            assignment,
            valid_observed,
            clique,
            i,
            j,
            TARGET_TREATMENT,
        )
        invalid_estimate = estimate(
            assignment,
            invalid_observed,
            clique,
            i,
            j,
            TARGET_TREATMENT,
        )
        if valid_estimate is None or invalid_estimate is None:
            continue
        estimable_count += 1
        valid_truth = float(valid_outcomes[TARGET_TREATMENT][i, j])
        invalid_truth = float(invalid_outcomes[TARGET_TREATMENT][i, j])
        valid_scaled_errors.append(abs(valid_estimate - valid_truth) / F_SCALE[1])
        invalid_scaled_errors.append(abs(invalid_estimate - invalid_truth) / F_SCALE[1])

    record = {
        "cliques": clique_count,
        "controls_rejected": control_rejections,
        "estimable": estimable_count,
        "invariant_checks": invariant_checks,
        "max_candidate_rows": max_candidate_rows,
        "mixed_cliques": mixed_count,
        "seed": seed,
        "targets": TARGETS_PER_SEED,
    }
    return record, valid_scaled_errors, invalid_scaled_errors


def main() -> int:
    started = time.perf_counter()
    records = []
    valid_errors: list[float] = []
    invalid_errors: list[float] = []
    for seed in SEEDS:
        record, valid, invalid = run_seed(seed)
        records.append(record)
        valid_errors.extend(valid)
        invalid_errors.extend(invalid)

    total_cliques = sum(item["cliques"] for item in records)
    total_estimable = sum(item["estimable"] for item in records)
    total_mixed = sum(item["mixed_cliques"] for item in records)
    total_checks = sum(item["invariant_checks"] for item in records)
    total_controls = sum(item["controls_rejected"] for item in records)
    valid_mae = float(np.mean(valid_errors)) if valid_errors else float("nan")
    invalid_mae = float(np.mean(invalid_errors)) if invalid_errors else float("nan")
    summary = {
        "claim_id": "claim_6_generator",
        "config": {
            "m": M,
            "n": N,
            "noise_sigma_relative": SIGMA,
            "rank": RANK,
            "seeds": list(SEEDS),
            "target_treatment": TARGET_TREATMENT,
            "targets_per_seed": TARGETS_PER_SEED,
        },
        "controls_rejected": total_controls,
        "estimable_targets": total_estimable,
        "invalid_shared_factor_scaled_mae": invalid_mae,
        "invariant_checks": total_checks,
        "mixed_clique_fraction": total_mixed / total_cliques if total_cliques else 0.0,
        "mixed_cliques": total_mixed,
        "per_seed": records,
        "selected_cliques": total_cliques,
        "valid_shared_factor_scaled_mae": valid_mae,
    }
    acceptance = {
        "all_corrupted_controls_rejected": total_controls == total_checks,
        "all_selected_cliques_audited": total_checks == total_cliques,
        "assumption_control_degrades_error": invalid_mae > 5 * valid_mae,
        "full_paper_scale": M == 300 and N == 100 and len(SEEDS) == 10,
        "mixed_treatments_observed": total_mixed > 0,
        "noisy_valid_reconstruction": valid_mae < 0.05,
        "sufficient_estimable_targets": total_estimable >= 100,
    }
    provenance = {
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "logical_cpu_count": os.cpu_count(),
        "platform": platform.platform(),
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": list(SEEDS),
    }
    print(f"CLAIM_6_RAW_JSON={json.dumps(summary, sort_keys=True)}")
    print(f"CLAIM_6_ACCEPTANCE={json.dumps(acceptance, sort_keys=True)}")
    print(f"CLAIM_6_PROVENANCE={json.dumps(provenance, sort_keys=True)}")
    if not all(acceptance.values()):
        print("CLAIM_6_GENERATOR_FAILED")
        return 1
    print("CLAIM_6_GENERATOR_PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
