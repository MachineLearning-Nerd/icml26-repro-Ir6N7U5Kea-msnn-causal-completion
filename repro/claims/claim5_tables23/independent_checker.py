"""Independent aggregate, source-range, and metric checker for Claim 5."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_5" / "raw_result.json"

PAPER_TABLES = {
    "0.05": {
        "low": {"snn": [0.19, 0.07, 0.349, 0.139], "msnn": [3.13, 0.41, 0.117, 0.006]},
        "medium": {"snn": [0.38, 0.12, 0.390, 0.143], "msnn": [3.26, 0.34, 0.114, 0.007]},
        "high": {"snn": [4.17, 0.84, 0.351, 0.050], "msnn": [4.52, 0.62, 0.106, 0.004]},
    },
    "0.02": {
        "low": {"snn": [9.57, 0.85, 0.366, 0.027], "msnn": [26.96, 3.50, 0.129, 0.008]},
        "medium": {"snn": [11.70, 1.62, 0.379, 0.037], "msnn": [33.88, 4.20, 0.135, 0.010]},
        "high": {"snn": [22.66, 2.24, 0.383, 0.025], "msnn": [54.16, 4.30, 0.118, 0.009]},
    },
}
PAPER_ASSIGNMENT_PROPORTIONS = {
    "0.05": {
        "low": [1.30, 0.06],
        "medium": [1.49, 0.06],
        "high": [2.50, 0.10],
    },
    "0.02": {
        "low": [3.54, 0.12],
        "medium": [3.76, 0.12],
        "high": [4.59, 0.11],
    },
}


def reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def expected_source_audit() -> dict:
    msnn_fr: list[float] = []
    snn_fr: list[float] = []
    ratios: list[float] = []
    for table in PAPER_TABLES.values():
        for treatment in table.values():
            snn = treatment["snn"]
            msnn = treatment["msnn"]
            snn_fr.append(snn[0])
            msnn_fr.append(msnn[0])
            ratios.append(snn[2] / msnn[2])
    return {
        "all_paper_fr_cells_msnn_gt_snn": all(
            msnn > snn for msnn, snn in zip(msnn_fr, snn_fr)
        ),
        "error_reduction_ratio_max": max(ratios),
        "error_reduction_ratio_min": min(ratios),
        "error_reduction_ratios": ratios,
        "ratios_outside_closed_2_to_3": sum(
            not 2.0 <= ratio <= 3.0 for ratio in ratios
        ),
        "msnn_fr_max_percent": max(msnn_fr),
        "msnn_fr_min_percent": min(msnn_fr),
        "snn_fr_max_percent": max(snn_fr),
        "snn_fr_min_percent": min(snn_fr),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutate-metric-substitution", action="store_true")
    parser.add_argument("--mutate-source-range", action="store_true")
    args = parser.parse_args()
    raw = json.loads(
        RAW.read_text(),
        parse_constant=reject_nonstandard_constant,
    )
    errors: list[str] = []

    if len(raw["per_cell_seed"]) != 60:
        errors.append("cell/seed grid does not contain 60 records")
    keys = {
        (record["lambda"], record["target_level"], record["seed"])
        for record in raw["per_cell_seed"]
    }
    if len(keys) != 60:
        errors.append("cell/seed grid contains duplicates")

    for lam_key, treatments in raw["aggregates"].items():
        lam = float(lam_key)
        for treatment, methods in treatments.items():
            selected = [
                record
                for record in raw["per_cell_seed"]
                if close(record["lambda"], lam)
                and record["treatment"] == treatment
            ]
            for method, metrics in methods.items():
                for metric, aggregate in metrics.items():
                    values = [
                        record[method][metric]
                        for record in selected
                        if record[method][metric] is not None
                    ]
                    if aggregate["finite_count"] != len(values):
                        errors.append(
                            f"{lam_key}/{treatment}/{method}/{metric}: "
                            "finite count mismatch"
                        )
                        continue
                    if aggregate["values"] != [
                        record[method][metric] for record in selected
                    ]:
                        errors.append(
                            f"{lam_key}/{treatment}/{method}/{metric}: "
                            "value ordering mismatch"
                        )
                    if values:
                        if not close(
                            aggregate["mean"],
                            statistics.fmean(values),
                        ):
                            errors.append(
                                f"{lam_key}/{treatment}/{method}/{metric}: "
                                "mean mismatch"
                            )
                        if len(values) > 1 and not close(
                            aggregate["sample_std"],
                            statistics.stdev(values),
                        ):
                            errors.append(
                                f"{lam_key}/{treatment}/{method}/{metric}: "
                                "sample std mismatch"
                            )

    for record in raw["per_cell_seed"]:
        for method in ("snn", "msnn"):
            data = record[method]
            count = data["feasible_count"]
            if count == 0:
                if (
                    data["code_normalized_mae"] is not None
                    or data["paper_defined_entrywise_mre"] is not None
                ):
                    errors.append("zero-count metric is not null")
                continue
            normalized = data["normalized_absolute_error_sum"] / count
            relative = data["entrywise_relative_error_sum"] / count
            if not close(normalized, data["code_normalized_mae"]):
                errors.append("released-code normalized-MAE formula mismatch")
            checked_relative = (
                normalized
                if args.mutate_metric_substitution
                else relative
            )
            if not close(
                checked_relative,
                data["paper_defined_entrywise_mre"],
            ):
                errors.append("paper-defined entrywise-MRE formula mismatch")

    for lam_key, treatments in raw[
        "assignment_proportion_aggregates"
    ].items():
        lam = float(lam_key)
        for treatment, aggregate in treatments.items():
            values = [
                100 * record["design_target_proportion"]
                for record in raw["per_cell_seed"]
                if close(record["lambda"], lam)
                and record["treatment"] == treatment
            ]
            if aggregate["values_percent"] != values:
                errors.append("assignment proportion value ordering mismatch")
            if not close(
                aggregate["mean_percent"],
                statistics.fmean(values),
            ):
                errors.append("assignment proportion mean mismatch")
            if not close(
                aggregate["sample_std_percent"],
                statistics.stdev(values),
            ):
                errors.append("assignment proportion std mismatch")
            paper_mean, paper_std = PAPER_ASSIGNMENT_PROPORTIONS[
                lam_key
            ][treatment]
            if round(aggregate["mean_percent"], 2) != paper_mean:
                errors.append("paper assignment-proportion mean not reproduced")
            if round(aggregate["sample_std_percent"], 2) != paper_std:
                errors.append("paper assignment-proportion std not reproduced")

    source = expected_source_audit()
    if args.mutate_source_range:
        source = {
            **source,
            "msnn_fr_max_percent": 26.0,
            "snn_fr_max_percent": 5.0,
        }
    observed_source = raw["paper_source_audit"]
    for name, expected in source.items():
        observed = observed_source[name]
        if isinstance(expected, list):
            if len(expected) != len(observed) or any(
                not close(left, right)
                for left, right in zip(expected, observed)
            ):
                errors.append(f"source audit mismatch: {name}")
        elif isinstance(expected, float):
            if not close(expected, observed):
                errors.append(f"source audit mismatch: {name}")
        elif expected != observed:
            errors.append(f"source audit mismatch: {name}")

    if raw["paper_tables"] != {
        lam: {
            treatment: {
                method: {
                    "fr_mean": values[0],
                    "fr_std": values[1],
                    "mre_mean": values[2],
                    "mre_std": values[3],
                }
                for method, values in methods.items()
            }
            for treatment, methods in treatments.items()
        }
        for lam, treatments in PAPER_TABLES.items()
    }:
        errors.append("paper table transcription mismatch")
    if raw["paper_assignment_proportions"] != {
        lam: {
            treatment: {
                "mean_percent": values[0],
                "std_percent": values[1],
            }
            for treatment, values in treatments.items()
        }
        for lam, treatments in PAPER_ASSIGNMENT_PROPORTIONS.items()
    }:
        errors.append("paper assignment-proportion transcription mismatch")

    errors = sorted(set(errors))
    payload = {
        "checker": "independent_mnar_tables_source_and_metric_checker",
        "errors": errors,
        "metric_mutation": args.mutate_metric_substitution,
        "passed": not errors,
        "source_mutation": args.mutate_source_range,
        "strict_json": True,
    }
    print(json.dumps(payload, allow_nan=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
