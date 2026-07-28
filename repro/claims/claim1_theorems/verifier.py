"""Fail-closed verifier for the Claim 1 theorem counterexample."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_1" / "raw_result.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def strict_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def main() -> int:
    started = time.perf_counter()
    raw = json.loads(RAW.read_text(), parse_constant=strict_constant)
    if raw["config"] != {
        "algorithm": "Algorithm 2 exact rank-one PCR",
        "audit_sizes": [
            16,
            81,
            256,
            4096,
            65536,
            16777216,
            4294967296,
            1099511627776,
        ],
        "repetitions": 24,
        "sigma": 0.25,
        "sizes": [16, 81, 256],
        "workers": 8,
    }:
        print("CLAIM_1_FAIL: protocol drift")
        return 1

    checked = subprocess.run(
        [sys.executable, str(CHECKER)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_1_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        print(checked.stderr)
        return 1
    control = subprocess.run(
        [sys.executable, str(CHECKER), "--pretend-snn-energy-holds"],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_1_NEGATIVE_CONTROL={control.stdout.strip()}")
    if control.returncode == 0:
        print("CLAIM_1_FAIL: false SNN energy premise was accepted")
        return 1
    control_payload = json.loads(control.stdout, parse_constant=strict_constant)
    if control_payload["errors"] != [
        "signal_frobenius_squared exponent mismatch: derived -1, declared 2"
    ]:
        print("CLAIM_1_FAIL: mutation failed for an unexpected reason")
        return 1

    largest = raw["aggregates"]["256"]
    if largest["weak_error"]["mean_ci95"][1] > -0.8:
        print("CLAIM_1_FAIL: weak-signal error CI does not exclude theorem behavior")
        return 1
    if abs(largest["strong_error"]["mean"]) >= 0.1:
        print("CLAIM_1_FAIL: restored-signal mechanism control failed")
        return 1

    result = {
        "claim_id": "claim_1",
        "counterexample": {
            "finite_bound_rhs_exponent": "-1/8 up to logarithms",
            "limiting_estimation_error": "-1 in probability",
            "normality_statistic": "-N^(1/8)/sigma in probability",
        },
        "evidence_type": (
            "assumption-satisfying asymptotic counterexample certificate "
            "plus exact Algorithm 2 calibration"
        ),
        "negative_control_exit_code": control.returncode,
        "verdict": "FALSIFIED",
    }
    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": "1000003 + 10000*K + repetition",
    }
    print(f"CLAIM_1_PROVENANCE_FINAL={json.dumps(provenance, sort_keys=True)}")
    print(f"CLAIM_RESULT_JSON={json.dumps(result, sort_keys=True)}")
    print("CLAIM_1_FALSIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
