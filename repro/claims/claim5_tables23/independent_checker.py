"""Independent strict checker for Claim 5's source falsification certificate."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_5" / "raw_result.json"
LABELS = {1: "low", 2: "medium", 3: "high"}
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
PAPER_PROPORTIONS = {
    "0.05": {"low": [1.30, 0.06], "medium": [1.49, 0.06], "high": [2.50, 0.10]},
    "0.02": {"low": [3.54, 0.12], "medium": [3.76, 0.12], "high": [4.59, 0.11]},
}


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)


def source_audit() -> dict:
    msnn_fr, snn_fr, ratios = [], [], []
    for table in PAPER_TABLES.values():
        for treatment in table.values():
            snn, msnn = treatment["snn"], treatment["msnn"]
            snn_fr.append(snn[0])
            msnn_fr.append(msnn[0])
            ratios.append(snn[2] / msnn[2])
    return {
        "all_paper_fr_cells_msnn_gt_snn": all(
            left > right for left, right in zip(msnn_fr, snn_fr)
        ),
        "error_reduction_ratio_max": max(ratios),
        "error_reduction_ratio_min": min(ratios),
        "error_reduction_ratios": ratios,
        "ratios_outside_closed_2_to_3": sum(
            not 2 <= ratio <= 3 for ratio in ratios
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
    raw = json.loads(RAW.read_text(), parse_constant=reject_constant)
    errors: list[str] = []

    records = raw["assignment_records"]
    keys = {(record["lambda"], record["seed"]) for record in records}
    if len(records) != 20 or len(keys) != 20:
        errors.append("assignment audit is not the complete 2x10 grid")
    for mode, by_lambda in raw["assignment_aggregates"].items():
        for lam_key, treatments in by_lambda.items():
            lam = float(lam_key)
            for treatment, aggregate in treatments.items():
                values = [
                    record[mode][treatment]
                    for record in records
                    if close(record["lambda"], lam)
                ]
                if aggregate["values_percent"] != values:
                    errors.append(f"{mode}/{lam_key}/{treatment}: values")
                if not close(aggregate["mean_percent"], statistics.fmean(values)):
                    errors.append(f"{mode}/{lam_key}/{treatment}: mean")
                if not close(
                    aggregate["sample_std_percent"],
                    statistics.stdev(values),
                ):
                    errors.append(f"{mode}/{lam_key}/{treatment}: std")
                if mode == "paper_absolute_entries":
                    expected_mean, expected_std = PAPER_PROPORTIONS[
                        lam_key
                    ][treatment]
                    if round(aggregate["mean_percent"], 2) != expected_mean:
                        errors.append(f"{lam_key}/{treatment}: paper mean")
                    if (
                        round(aggregate["sample_std_percent"], 2)
                        != expected_std
                    ):
                        errors.append(f"{lam_key}/{treatment}: paper std")

    expected_tables = {
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
    }
    if raw["paper_tables"] != expected_tables:
        errors.append("paper table transcription mismatch")

    expected_source = source_audit()
    if args.mutate_source_range:
        expected_source["msnn_fr_max_percent"] = 26.0
        expected_source["snn_fr_max_percent"] = 5.0
    for key, expected in expected_source.items():
        observed = raw["paper_source_audit"][key]
        if isinstance(expected, list):
            if len(expected) != len(observed) or any(
                not close(left, right)
                for left, right in zip(expected, observed)
            ):
                errors.append(f"source audit mismatch: {key}")
        elif isinstance(expected, float):
            if not close(expected, observed):
                errors.append(f"source audit mismatch: {key}")
        elif expected != observed:
            errors.append(f"source audit mismatch: {key}")

    metric = raw["metric_definition_audit"]
    expected_paper_formula = (
        "mean(abs(prediction - truth)) / treatment_scale"
        if args.mutate_metric_substitution
        else "mean(abs((prediction - truth) / truth)) over feasible entries"
    )
    if metric["paper_section_5_1"] != expected_paper_formula:
        errors.append("paper metric definition mismatch")
    witness = metric["witness"]
    truth, prediction = witness["truth"], witness["prediction"]
    absolute = [abs(left - right) for left, right in zip(prediction, truth)]
    released = statistics.fmean(absolute) / witness["scale"]
    paper = statistics.fmean(
        error / abs(target) for error, target in zip(absolute, truth)
    )
    if not close(released, witness["released_normalized_mae"]):
        errors.append("released metric witness mismatch")
    if not close(paper, witness["section_5_1_entrywise_mre"]):
        errors.append("paper metric witness mismatch")
    if close(released, paper):
        errors.append("metric witness does not distinguish formulas")

    errors = sorted(set(errors))
    print(
        json.dumps(
            {
                "assignment_records_reconstructed": len(records),
                "checker": "independent_claim_5_source_certificate_checker",
                "errors": errors,
                "metric_mutation": args.mutate_metric_substitution,
                "passed": not errors,
                "source_mutation": args.mutate_source_range,
                "strict_json": True,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
