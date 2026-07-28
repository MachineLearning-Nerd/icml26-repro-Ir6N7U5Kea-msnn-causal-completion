"""Calibrated exact-Algorithm-2 corroboration for the Claim 1 counterexample."""

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
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / ".openresearch" / "artifacts" / "claim_1"
SIGMA = 0.25
SIZES = (16, 81, 256)
AUDIT_SIZES = tuple(root**4 for root in (2, 3, 4, 8, 16, 64, 256, 1024))
REPETITIONS = 24
WORKERS = 8


def rank_one_pcr(S: np.ndarray, q: np.ndarray, x: np.ndarray) -> float:
    """Algorithm 2 with the theorem-mandated population rank lambda=1."""
    left, singular, right_t = np.linalg.svd(S, full_matrices=False)
    beta = left[:, 0] * (right_t[0] @ q) / singular[0]
    return float(x @ beta)


def one_repetition(task: tuple[int, int]) -> dict:
    N, repetition = task
    K = round(N ** 0.25)
    if K**4 != N:
        raise ValueError("N must be a perfect fourth power")
    rng = np.random.default_rng(1_000_003 + 10_000 * K + repetition)

    epsilon = N**-2
    delta = N**-1
    weak_u = np.concatenate(([1.0], np.full(N - 1, epsilon)))
    weak_q = np.full(N, delta) + rng.normal(0.0, SIGMA, N)
    weak_estimates = []
    for _ in range(K):
        weak_S = (
            delta * weak_u[:, None]
            + rng.normal(0.0, SIGMA, (N, N))
        )
        weak_x = weak_u + rng.normal(0.0, SIGMA, N)
        weak_estimates.append(rank_one_pcr(weak_S, weak_q, weak_x))

    strong_u = np.ones(N)
    strong_q = np.ones(N) + rng.normal(0.0, SIGMA, N)
    strong_estimates = []
    for _ in range(K):
        strong_S = (
            strong_u[:, None]
            + rng.normal(0.0, SIGMA, (N, N))
        )
        strong_x = strong_u + rng.normal(0.0, SIGMA, N)
        strong_estimates.append(rank_one_pcr(strong_S, strong_q, strong_x))

    weak = statistics.fmean(weak_estimates)
    strong = statistics.fmean(strong_estimates)
    weak_u_norm_sq = float(weak_u @ weak_u)
    normalizer = math.sqrt(K * SIGMA**2 / weak_u_norm_sq)
    return {
        "K": K,
        "N": N,
        "repetition": repetition,
        "seed": 1_000_003 + 10_000 * K + repetition,
        "strong_error": strong - 1.0,
        "strong_estimate": strong,
        "weak_error": weak - 1.0,
        "weak_estimate": weak,
        "weak_normalized_statistic": K * (weak - 1.0) / normalizer,
    }


def summarize(values: list[float]) -> dict:
    mean = statistics.fmean(values)
    sample_std = statistics.stdev(values)
    standard_error = sample_std / math.sqrt(len(values))
    return {
        "count": len(values),
        "mean": mean,
        "sample_std": sample_std,
        "standard_error": standard_error,
        "mean_ci95": [mean - 1.96 * standard_error, mean + 1.96 * standard_error],
        "values": values,
    }


def exact_audit(N: int) -> dict:
    K = round(N ** 0.25)
    norm_sq = 1.0 + (N - 1) * N**-4
    tau = math.sqrt(norm_sq / N)
    beta_l1 = (1.0 + (N - 1) * N**-2) / norm_sq
    beta_l2 = 1.0 / math.sqrt(norm_sq)
    error_k1 = N**-0.25
    error_k2 = beta_l1 * math.sqrt(math.log(N**2)) / math.sqrt(N)
    return {
        "K": K,
        "N": N,
        "beta_l1": beta_l1,
        "beta_l2": beta_l2,
        "condition_iv_ratio": (
            K * (error_k1 + error_k2)
            / (math.sqrt(K) * SIGMA * beta_l2)
        ),
        "error_k1": error_k1,
        "error_k2": error_k2,
        "msnn_upper_bound_ratio": tau / N**2,
        "normality_divergence_scale": math.sqrt(K) / (SIGMA * beta_l2),
        "signal_energy_ratio_to_snn_requirement": (norm_sq / N) / N**2,
        "signal_frobenius_squared": norm_sq / N,
        "tau_1": tau,
        "theorem_4_5_rhs_scale": (
            error_k1 + error_k2 + beta_l2 / math.sqrt(K)
        ),
    }


def main() -> int:
    started = time.perf_counter()
    tasks = [(N, repetition) for N in SIZES for repetition in range(REPETITIONS)]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        records = list(pool.map(one_repetition, tasks))

    aggregates = {}
    for N in SIZES:
        selected = [record for record in records if record["N"] == N]
        aggregates[str(N)] = {
            metric: summarize([record[metric] for record in selected])
            for metric in (
                "strong_error",
                "strong_estimate",
                "weak_error",
                "weak_estimate",
                "weak_normalized_statistic",
            )
        }

    result = {
        "aggregates": aggregates,
        "claim_id": "claim_1_counterexample_generator",
        "config": {
            "algorithm": "Algorithm 2 exact rank-one PCR",
            "audit_sizes": list(AUDIT_SIZES),
            "repetitions": REPETITIONS,
            "sigma": SIGMA,
            "sizes": list(SIZES),
            "workers": WORKERS,
        },
        "exact_audit": [exact_audit(N) for N in AUDIT_SIZES],
        "per_repetition": records,
    }
    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "process_workers": WORKERS,
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seed_rule": "1000003 + 10000*K + repetition",
    }
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    raw_text = json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n"
    (ARTIFACT / "raw_result.json").write_text(raw_text)
    (ARTIFACT / "provenance.json").write_text(
        json.dumps(provenance, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )
    print(
        "CLAIM_1_RAW_JSON="
        + json.dumps(result, allow_nan=False, sort_keys=True)
    )
    print(
        "CLAIM_1_PROVENANCE="
        + json.dumps(provenance, allow_nan=False, sort_keys=True)
    )
    largest = aggregates[str(SIZES[-1])]
    if abs(largest["weak_error"]["mean"]) < 0.8:
        print("CLAIM_1_GENERATOR_FAIL: weak-signal contradiction disappeared")
        return 1
    if abs(largest["strong_error"]["mean"]) > 0.1:
        print("CLAIM_1_GENERATOR_FAIL: strong-signal mechanism control failed")
        return 1
    print("CLAIM_1_GENERATOR_COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
