"""Materialize Claim 5 evidence from a complete OpenResearch run log."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / ".openresearch" / "artifacts" / "claim_5"
PREFIXES = {
    "raw_result": "CLAIM_5_RAW_JSON=",
    "generator_provenance": "CLAIM_5_PROVENANCE=",
    "checker": "CLAIM_5_CHECKER=",
    "negative_metric": "CLAIM_5_NEGATIVE_CONTROL_METRIC=",
    "negative_source": "CLAIM_5_NEGATIVE_CONTROL_SOURCE=",
    "verifier_provenance": "CLAIM_5_PROVENANCE_FINAL=",
}


def strict_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def parse(line: str, prefix: str) -> dict:
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
    log_lines: list[str] = []
    terminal: set[str] = set()
    for original in sys.stdin:
        log_lines.append(original)
        line = original.rstrip("\n")
        for name, prefix in PREFIXES.items():
            if line.startswith(prefix):
                captured[name] = parse(line, prefix)
        if line.startswith("CLAIM_RESULT_JSON="):
            record = parse(line, "CLAIM_RESULT_JSON=")
            if record.get("claim_id") == "claim_5":
                result_records.append(record)
        if line in {
            "CLAIM_5_SOURCE_CERTIFICATE_COMPLETED",
            "CLAIM_5_FALSIFIED",
            "CONTROLS: ALL HOLD | sanity: PASS",
        }:
            terminal.add(line)

    missing = sorted(set(PREFIXES) - set(captured))
    if missing:
        raise SystemExit(f"missing Claim 5 log records: {missing}")
    if len(result_records) != 1:
        raise SystemExit(
            f"expected one Claim 5 verdict record, found {len(result_records)}"
        )
    required_terminal = {
        "CLAIM_5_SOURCE_CERTIFICATE_COMPLETED",
        "CLAIM_5_FALSIFIED",
        "CONTROLS: ALL HOLD | sanity: PASS",
    }
    if not required_terminal.issubset(terminal):
        raise SystemExit(
            f"missing terminal markers: {sorted(required_terminal - terminal)}"
        )
    if captured["checker"].get("passed") is not True:
        raise SystemExit("Claim 5 checker did not pass")
    for name in ("negative_metric", "negative_source"):
        if captured[name].get("passed") is not False:
            raise SystemExit(f"Claim 5 {name} did not fail")
    if result_records[0].get("verdict") != "FALSIFIED":
        raise SystemExit("Claim 5 verdict drifted")

    raw = captured["raw_result"]
    if raw.get("claim_id") != "claim_5_source_certificate":
        raise SystemExit("Claim 5 raw identifier drifted")
    full_log = "".join(log_lines)
    provenance = {
        **captured["generator_provenance"],
        "fixed_command": (
            "uv run --frozen python repro/src/verify.py && "
            "uv run --frozen python repro/tests/test_controls.py"
        ),
        "formal_log_sha256": hashlib.sha256(full_log.encode()).hexdigest(),
        "formal_run_duration_seconds": args.formal_runtime_seconds,
        "formal_run_id": args.run_id,
        "verifier_provenance": captured["verifier_provenance"],
    }
    outputs = {
        "raw_result.json": json.dumps(
            raw, allow_nan=False, indent=2, sort_keys=True
        )
        + "\n",
        "provenance.json": json.dumps(
            provenance, allow_nan=False, indent=2, sort_keys=True
        )
        + "\n",
        "checker_output.txt": json.dumps(
            captured["checker"], allow_nan=False, indent=2, sort_keys=True
        )
        + "\n",
        "negative_control_metric.txt": json.dumps(
            captured["negative_metric"],
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "negative_control_source.txt": json.dumps(
            captured["negative_source"],
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "verdict_output.json": json.dumps(
            result_records[0],
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        "formal_run.log": full_log,
    }
    ARTIFACT.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        (ARTIFACT / name).write_text(content)
    print(
        json.dumps(
            {
                "claim_id": "claim_5",
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
