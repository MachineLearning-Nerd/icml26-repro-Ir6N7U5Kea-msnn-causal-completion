"""Independent aggregate and metric-semantics checker for Claim 4."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_4" / "raw_result.json"


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutate-metric-substitution", action="store_true")
    args = parser.parse_args()
    raw = json.loads(
        RAW.read_text(), parse_constant=reject_nonstandard_constant
    )
    errors: list[str] = []

    for method in ("snn", "msnn"):
        for metric in (
            "feasible_rate_percent",
            "code_normalized_mae",
            "paper_defined_entrywise_mre",
        ):
            values = [
                record[method][metric]
                for record in raw["per_seed"]
                if record[method][metric] is not None
            ]
            aggregate = raw["aggregates"][method][metric]
            if aggregate["finite_count"] != len(values):
                errors.append(f"{method}/{metric}: finite count mismatch")
                continue
            mean = statistics.fmean(values)
            sample_std = statistics.stdev(values)
            if not close(mean, aggregate["mean"]):
                errors.append(f"{method}/{metric}: mean mismatch")
            if not close(sample_std, aggregate["sample_std"]):
                errors.append(f"{method}/{metric}: sample std mismatch")

    for record in raw["per_seed"]:
        for method in ("snn", "msnn"):
            data = record[method]
            count = data["feasible_count"]
            if count == 0:
                if (
                    data["code_normalized_mae"] is not None
                    or data["paper_defined_entrywise_mre"] is not None
                ):
                    errors.append(f"seed {record['seed']} {method}: empty metric")
                continue
            normalized = data["normalized_absolute_error_sum"] / count
            relative = data["entrywise_relative_error_sum"] / count
            if not close(normalized, data["code_normalized_mae"]):
                errors.append(f"seed {record['seed']} {method}: normalized formula")
            if not close(relative, data["paper_defined_entrywise_mre"]):
                errors.append(f"seed {record['seed']} {method}: paper formula")

    msnn = raw["aggregates"]["msnn"]
    paper_metric = (
        msnn["code_normalized_mae"]
        if args.mutate_metric_substitution
        else msnn["paper_defined_entrywise_mre"]
    )
    if args.mutate_metric_substitution:
        errors.append("metric substitution: normalized MAE is not paper-defined MRE")
    if round(msnn["feasible_rate_percent"]["mean"], 2) != 4.69:
        errors.append("MSNN FR does not reproduce the published mean")
    if round(msnn["code_normalized_mae"]["mean"], 4) != 0.0391:
        errors.append("author-code normalized MAE does not reproduce table label")
    if round(paper_metric["mean"], 4) == 0.0391:
        errors.append("paper-defined MRE incorrectly matches the table label")

    snn_finite = raw["aggregates"]["snn"]["code_normalized_mae"]
    if round(snn_finite["mean"], 3) != 0.806:
        errors.append("finite-only SNN author aggregation mismatch")

    payload = {
        "checker": "independent_aggregate_and_metric_semantics",
        "errors": errors,
        "mutation": args.mutate_metric_substitution,
        "passed": not errors,
        "strict_json": True,
    }
    print(json.dumps(payload, allow_nan=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
