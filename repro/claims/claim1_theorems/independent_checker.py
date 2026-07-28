"""Independent algebra, aggregate, and source-premise checker for Claim 1."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "proof_certificate.json"
RAW = ROOT / ".openresearch" / "artifacts" / "claim_1" / "raw_result.json"
PAPER_HASH = "f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448"
SNN_HASH = "3ffca53b29d11c708d8332ef53360e7aedc4602ff68ec66cb1e4e12e714f519f"


def strict_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(), parse_constant=strict_constant)


def close(left: float, right: float, tolerance: float = 1e-11) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretend-snn-energy-holds", action="store_true")
    args = parser.parse_args()
    certificate = load_json(CERTIFICATE)
    raw = load_json(RAW)
    errors: list[str] = []

    if certificate["msnn_source"]["html_sha256"] != PAPER_HASH:
        errors.append("MSNN source hash mismatch")
    if certificate["cited_snn_assumption_6"]["html_sha256"] != SNN_HASH:
        errors.append("cited SNN source hash mismatch")
    expected_lower = (
        "||E[S^(k)|environment]||_F^2 >= c' |AC^(k)| |AR^(k)|"
    )
    if certificate["cited_snn_assumption_6"]["required_lower_bound"] != expected_lower:
        errors.append("cited SNN energy premise mismatch")
    expected_upper = (
        "tau_1^(k)(d) <= c' |MAR^(k)(d)| |MAC^(k)(d)|"
    )
    if certificate["msnn_source"]["upper_bound_only"] != expected_upper:
        errors.append("MSNN Assumption 4.3 upper bound mismatch")

    expected_exponents = {
        "K": Fraction(1, 4),
        "algorithm_estimate": Fraction(-1, 2),
        "anchor_columns": Fraction(1),
        "anchor_rows": Fraction(1),
        "beta_l1": Fraction(0),
        "beta_l2": Fraction(0),
        "condition_iv_ratio_first_term": Fraction(-1, 8),
        "condition_iv_ratio_second_term": Fraction(-3, 8),
        "finite_bound_dominant": Fraction(-1, 8),
        "normalized_statistic_magnitude": Fraction(1, 8),
        "signal_frobenius_squared": Fraction(-1),
        "signal_to_required_energy_ratio": Fraction(-3),
        "tau_1": Fraction(-1, 2),
    }
    declared = {
        name: Fraction(value)
        for name, value in certificate["asymptotic_exponents"].items()
    }
    if args.pretend_snn_energy_holds:
        declared["signal_frobenius_squared"] = Fraction(2)
    for name, expected in expected_exponents.items():
        if declared.get(name) != expected:
            errors.append(
                f"{name} exponent mismatch: derived {expected}, "
                f"declared {declared.get(name)}"
            )

    if expected_exponents["finite_bound_dominant"] >= 0:
        errors.append("Theorem 4.5 asserted RHS does not vanish")
    if expected_exponents["normalized_statistic_magnitude"] <= 0:
        errors.append("Theorem 4.6 statistic does not diverge")
    if expected_exponents["condition_iv_ratio_first_term"] >= 0:
        errors.append("Theorem 4.6 condition (iv), first term, does not hold")
    if expected_exponents["condition_iv_ratio_second_term"] >= 0:
        errors.append("Theorem 4.6 condition (iv), second term, does not hold")

    for audit in raw["exact_audit"]:
        N = audit["N"]
        norm_sq = 1.0 + (N - 1) * N**-4
        beta_l1 = (1.0 + (N - 1) * N**-2) / norm_sq
        beta_l2 = 1.0 / math.sqrt(norm_sq)
        error_k1 = N**-0.25
        error_k2 = beta_l1 * math.sqrt(math.log(N**2)) / math.sqrt(N)
        K = round(N ** 0.25)
        expected = {
            "K": K,
            "beta_l1": beta_l1,
            "beta_l2": beta_l2,
            "condition_iv_ratio": (
                K * (error_k1 + error_k2)
                / (math.sqrt(K) * 0.25 * beta_l2)
            ),
            "error_k1": error_k1,
            "error_k2": error_k2,
            "msnn_upper_bound_ratio": math.sqrt(norm_sq / N) / N**2,
            "normality_divergence_scale": math.sqrt(K) / (0.25 * beta_l2),
            "signal_energy_ratio_to_snn_requirement": norm_sq / N**3,
            "signal_frobenius_squared": norm_sq / N,
            "tau_1": math.sqrt(norm_sq / N),
            "theorem_4_5_rhs_scale": (
                error_k1 + error_k2 + beta_l2 / math.sqrt(K)
            ),
        }
        for name, value in expected.items():
            if not close(float(audit[name]), float(value)):
                errors.append(f"N={N} exact audit mismatch for {name}")

    records = raw["per_repetition"]
    for N_text, metrics in raw["aggregates"].items():
        N = int(N_text)
        selected = [record for record in records if record["N"] == N]
        for metric, aggregate in metrics.items():
            values = [record[metric] for record in selected]
            mean = statistics.fmean(values)
            sample_std = statistics.stdev(values)
            standard_error = sample_std / math.sqrt(len(values))
            expected_ci = [
                mean - 1.96 * standard_error,
                mean + 1.96 * standard_error,
            ]
            if aggregate["count"] != len(values):
                errors.append(f"N={N} {metric} count mismatch")
            for name, value in (
                ("mean", mean),
                ("sample_std", sample_std),
                ("standard_error", standard_error),
            ):
                if not close(aggregate[name], value):
                    errors.append(f"N={N} {metric} {name} mismatch")
            if any(
                not close(observed, expected)
                for observed, expected in zip(aggregate["mean_ci95"], expected_ci)
            ):
                errors.append(f"N={N} {metric} CI mismatch")

    payload = {
        "checker": "independent_claim_1_counterexample_checker",
        "errors": errors,
        "mutation": args.pretend_snn_energy_holds,
        "passed": not errors,
        "strict_json": True,
    }
    print(json.dumps(payload, allow_nan=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
