"""Materialize Claim 1 evidence from a complete OpenResearch run log.

Usage:
  orx logs <run-id> --bytes 1000000 \
    | uv run --frozen python repro/tools/capture_claim1_log.py \
        --run-id <run-id> --formal-runtime-seconds <seconds>

The formal remote process prints the raw result and verifier records because
OpenResearch local mode treats the run log as its evidence channel.  This
utility copies those exact records into the evaluator-visible artifact tree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / ".openresearch" / "artifacts" / "claim_1"
CERTIFICATE = ROOT / "repro" / "claims" / "claim1_theorems" / "proof_certificate.json"
REQUIRED_PREFIXES = {
    "raw_result": "CLAIM_1_RAW_JSON=",
    "generator_provenance": "CLAIM_1_PROVENANCE=",
    "checker": "CLAIM_1_CHECKER=",
    "negative_control": "CLAIM_1_NEGATIVE_CONTROL=",
    "verifier_provenance": "CLAIM_1_PROVENANCE_FINAL=",
}


def strict_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def parse_record(line: str, prefix: str) -> dict:
    return json.loads(
        line[len(prefix) :],
        parse_constant=strict_constant,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--formal-runtime-seconds", required=True, type=int)
    args = parser.parse_args()

    captured: dict[str, dict] = {}
    result_records: list[dict] = []
    terminal_markers: set[str] = set()
    for line in sys.stdin:
        line = line.rstrip("\n")
        for name, prefix in REQUIRED_PREFIXES.items():
            if line.startswith(prefix):
                captured[name] = parse_record(line, prefix)
        if line.startswith("CLAIM_RESULT_JSON="):
            record = parse_record(line, "CLAIM_RESULT_JSON=")
            if record.get("claim_id") == "claim_1":
                result_records.append(record)
        if line in {
            "CLAIM_1_GENERATOR_COMPLETED",
            "CLAIM_1_FALSIFIED",
            "CONTROLS: ALL HOLD | sanity: PASS",
        }:
            terminal_markers.add(line)

    missing = sorted(set(REQUIRED_PREFIXES) - set(captured))
    if missing:
        raise SystemExit(f"missing required Claim 1 log records: {missing}")
    if len(result_records) != 1:
        raise SystemExit(
            f"expected one Claim 1 result record, found {len(result_records)}"
        )
    required_terminal = {
        "CLAIM_1_GENERATOR_COMPLETED",
        "CLAIM_1_FALSIFIED",
        "CONTROLS: ALL HOLD | sanity: PASS",
    }
    if not required_terminal.issubset(terminal_markers):
        raise SystemExit(
            "missing terminal markers: "
            f"{sorted(required_terminal - terminal_markers)}"
        )
    if captured["checker"].get("passed") is not True:
        raise SystemExit("Claim 1 independent checker did not pass")
    if captured["negative_control"].get("passed") is not False:
        raise SystemExit("Claim 1 negative control did not fail")
    if result_records[0].get("verdict") != "FALSIFIED":
        raise SystemExit("Claim 1 verdict marker drifted")

    raw = captured["raw_result"]
    if raw.get("claim_id") != "claim_1_counterexample_generator":
        raise SystemExit("Claim 1 raw-result identifier drifted")
    generator_provenance = captured["generator_provenance"]
    certificate = json.loads(
        CERTIFICATE.read_text(),
        parse_constant=strict_constant,
    )
    if certificate.get("claim_id") != "claim_1":
        raise SystemExit("Claim 1 proof-certificate identifier drifted")
    provenance = {
        **generator_provenance,
        "fixed_command": (
            "uv run --frozen python repro/src/verify.py && "
            "uv run --frozen python repro/tests/test_controls.py"
        ),
        "formal_run_duration_seconds": args.formal_runtime_seconds,
        "formal_run_id": args.run_id,
        "verifier_provenance": captured["verifier_provenance"],
    }

    ARTIFACT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "raw_result.json": raw,
        "proof_certificate.json": certificate,
        "provenance.json": provenance,
        "checker_output.txt": captured["checker"],
        "negative_control_output.txt": captured["negative_control"],
        "verdict_output.json": result_records[0],
    }
    for name, value in outputs.items():
        text = json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n"
        (ARTIFACT / name).write_text(text)

    print(
        json.dumps(
            {
                "claim_id": "claim_1",
                "files_written": sorted(outputs),
                "run_id": args.run_id,
                "strict_json": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
