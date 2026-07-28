"""Independent reconstruction checker for the frozen Claim 6 generator result."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_6" / "raw_result.json"
M, N, LATENT_RANK = 300, 100, 3
LEVELS = np.array([0, 1, 2, 3, 4], dtype=int)
PROBS = np.array([0.115, 0.01, 0.025, 0.05, 0.8])
SCALES = {1: 1.0, 2: 5.0, 3: 25.0, 4: 625.0}
SEEDS = range(10)


def normalize_rows(array: np.ndarray) -> np.ndarray:
    norms = np.sqrt(np.einsum("ij,ij->i", array, array))
    return array / norms[:, None]


def potential_matrices(seed: int, shared: bool) -> dict[int, np.ndarray]:
    random = np.random.default_rng(seed + 10_000)
    columns = normalize_rows(random.standard_normal((N, LATENT_RANK)))
    common_rows = normalize_rows(random.standard_normal((M, LATENT_RANK)))
    matrices: dict[int, np.ndarray] = {}
    for level in (1, 2, 3, 4):
        rows = (
            common_rows
            if shared
            else normalize_rows(random.standard_normal((M, LATENT_RANK)))
        )
        matrices[level] = SCALES[level] * np.einsum(
            "ir,jr->ij", rows, columns
        )
    return matrices


def assignments(seed: int) -> np.ndarray:
    random = np.random.default_rng(seed + 20_000)
    return random.choice(LEVELS, p=PROBS, size=(M, N))


def noisy_observations(
    design: np.ndarray,
    potential: dict[int, np.ndarray],
    noise_seed: int,
) -> np.ndarray:
    random = np.random.default_rng(noise_seed)
    result = np.full((M, N), np.nan)
    for level in (1, 2, 3, 4):
        mask = design == level
        result[mask] = potential[level][mask] + random.normal(
            loc=0.0,
            scale=SCALES[level] * 0.001,
            size=int(mask.sum()),
        )
    return result


def edge_table(
    design: np.ndarray,
    row: int,
    column: int,
    mutated: bool,
) -> np.ndarray:
    same_target_level = design[:, column] == (2 if mutated else 1)
    target_row_levels = design[row]
    edges = (
        same_target_level[:, None]
        & (design == target_row_levels)
        & (target_row_levels[None, :] != 0)
    )
    edges[row, :] = False
    edges[:, column] = False
    return edges


def exhaustive_biclique(edges: np.ndarray) -> tuple[np.ndarray, np.ndarray] | None:
    active_rows = np.flatnonzero(np.any(edges, axis=1))
    if active_rows.size == 0:
        return None
    if active_rows.size > 20:
        raise AssertionError("independent exact-enumeration bound exceeded")
    winner = None
    for bits in range(1, 2 ** active_rows.size):
        positions = np.flatnonzero(
            np.fromiter(
                ((bits >> index) & 1 for index in range(active_rows.size)),
                dtype=bool,
            )
        )
        rows = active_rows[positions]
        columns = np.flatnonzero(np.all(edges[rows], axis=0))
        if columns.size == 0:
            continue
        score = (
            int(rows.size * columns.size),
            int(rows.size + columns.size),
            int(rows.size),
            tuple(-int(item) for item in rows),
            tuple(-int(item) for item in columns),
        )
        if winner is None or score > winner[0]:
            winner = (score, rows, columns)
    if winner is None:
        return None
    return winner[1], winner[2]


def validate_edges(
    design: np.ndarray,
    rows: np.ndarray,
    columns: np.ndarray,
    target_row: int,
    target_column: int,
) -> None:
    if np.any(design[rows, target_column] != 1):
        raise AssertionError("selected row does not preserve target treatment")
    target_levels = design[target_row, columns]
    if np.any(target_levels == 0):
        raise AssertionError("selected column is unobserved in the target row")
    actual = design[np.ix_(rows, columns)]
    if np.any(actual != target_levels[None, :]):
        raise AssertionError("selected anchor treatment does not match target row")


def corruption_is_rejected(
    design: np.ndarray,
    edges: np.ndarray,
    rows: np.ndarray,
    columns: np.ndarray,
    target_row: int,
    target_column: int,
) -> bool:
    for candidate in range(N):
        if candidate == target_column or candidate in columns:
            continue
        if not np.all(edges[rows, candidate]):
            try:
                validate_edges(
                    design,
                    rows,
                    np.append(columns, candidate),
                    target_row,
                    target_column,
                )
            except AssertionError:
                return True
            return False
    raise AssertionError("no independent corrupted edge was available")


def reconstruct(
    design: np.ndarray,
    observed: np.ndarray,
    rows: np.ndarray,
    columns: np.ndarray,
    target_row: int,
    target_column: int,
) -> float | None:
    if rows.size < LATENT_RANK or columns.size < LATENT_RANK:
        return None
    weights = np.array([1.0 / SCALES[int(x)] for x in design[target_row, columns]])
    weighted_anchor = observed[np.ix_(rows, columns)] * weights
    weighted_query = observed[target_row, columns] * weights
    left, values, right_t = np.linalg.svd(weighted_anchor, full_matrices=False)
    usable = int(np.count_nonzero(values > 1e-12))
    if usable < LATENT_RANK:
        return None
    count = LATENT_RANK
    coefficients = (
        left[:, :count]
        @ np.diag(1.0 / values[:count])
        @ right_t[:count]
        @ weighted_query
    )
    return float(observed[rows, target_column] @ coefficients)


def regenerate(mutated: bool) -> dict:
    per_seed = []
    valid_errors: list[float] = []
    invalid_errors: list[float] = []
    for seed in SEEDS:
        design = assignments(seed)
        valid = potential_matrices(seed, shared=True)
        invalid = potential_matrices(seed, shared=False)
        valid_y = noisy_observations(design, valid, 30_000 + seed)
        invalid_y = noisy_observations(design, invalid, 40_000 + seed)
        target_random = np.random.default_rng(seed + 50_000)
        targets = target_random.choice(M * N, size=40, replace=False)
        cliques = estimable = mixed = checks = controls = max_rows = 0
        for flat in targets:
            target_row, target_column = divmod(int(flat), N)
            edges = edge_table(design, target_row, target_column, mutated)
            max_rows = max(max_rows, int(np.count_nonzero(np.any(edges, axis=1))))
            clique = exhaustive_biclique(edges)
            if clique is None:
                continue
            rows, columns = clique
            cliques += 1
            validate_edges(design, rows, columns, target_row, target_column)
            checks += 1
            controls += int(
                corruption_is_rejected(
                    design,
                    edges,
                    rows,
                    columns,
                    target_row,
                    target_column,
                )
            )
            mixed += int(np.unique(design[target_row, columns]).size >= 2)
            valid_est = reconstruct(
                design, valid_y, rows, columns, target_row, target_column
            )
            invalid_est = reconstruct(
                design, invalid_y, rows, columns, target_row, target_column
            )
            if valid_est is None or invalid_est is None:
                continue
            estimable += 1
            valid_errors.append(abs(valid_est - valid[1][target_row, target_column]))
            invalid_errors.append(
                abs(invalid_est - invalid[1][target_row, target_column])
            )
        per_seed.append(
            {
                "cliques": cliques,
                "controls_rejected": controls,
                "estimable": estimable,
                "invariant_checks": checks,
                "max_candidate_rows": max_rows,
                "mixed_cliques": mixed,
                "seed": seed,
                "targets": 40,
            }
        )
    selected = sum(record["cliques"] for record in per_seed)
    mixed = sum(record["mixed_cliques"] for record in per_seed)
    return {
        "claim_id": "claim_6_generator",
        "config": {
            "m": M,
            "n": N,
            "noise_sigma_relative": 0.001,
            "rank": LATENT_RANK,
            "seeds": list(SEEDS),
            "target_treatment": 1,
            "targets_per_seed": 40,
        },
        "controls_rejected": sum(
            record["controls_rejected"] for record in per_seed
        ),
        "estimable_targets": sum(record["estimable"] for record in per_seed),
        "invalid_shared_factor_scaled_mae": float(np.mean(invalid_errors)),
        "invariant_checks": sum(record["invariant_checks"] for record in per_seed),
        "mixed_clique_fraction": mixed / selected,
        "mixed_cliques": mixed,
        "per_seed": per_seed,
        "selected_cliques": selected,
        "valid_shared_factor_scaled_mae": float(np.mean(valid_errors)),
    }


def compare(actual: dict, expected: dict) -> list[str]:
    errors = []
    for key in (
        "claim_id",
        "config",
        "controls_rejected",
        "estimable_targets",
        "invariant_checks",
        "mixed_cliques",
        "per_seed",
        "selected_cliques",
    ):
        if actual.get(key) != expected.get(key):
            errors.append(f"{key} mismatch")
    for key in (
        "invalid_shared_factor_scaled_mae",
        "mixed_clique_fraction",
        "valid_shared_factor_scaled_mae",
    ):
        if not np.isclose(actual.get(key), expected.get(key), rtol=1e-10, atol=1e-12):
            errors.append(f"{key} mismatch")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutate-target-treatment", action="store_true")
    args = parser.parse_args()
    expected = json.loads(RAW.read_text())
    try:
        regenerated = regenerate(mutated=args.mutate_target_treatment)
        errors = compare(regenerated, expected)
    except AssertionError as exc:
        errors = [str(exc)]
    payload = {
        "checker": "independent_full_seed_reconstruction",
        "errors": errors,
        "mutation": args.mutate_target_treatment,
        "passed": not errors,
        "seeds_reconstructed": 10,
        "targets_reconstructed": 400,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
