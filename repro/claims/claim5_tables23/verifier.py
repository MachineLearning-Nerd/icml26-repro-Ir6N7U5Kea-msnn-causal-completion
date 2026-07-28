"""Fail-closed verifier for Claim 5's exact source-level falsification."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_5" / "raw_result.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def run_checker(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    started = time.perf_counter()
    raw = json.loads(RAW.read_text())
    expected_config = {
        "dgp_audit": (
            "paper absolute-entry route versus released positive-factor route"
        ),
        "lambdas": [0.05, 0.02],
        "m": 300,
        "n": 100,
        "rank": 3,
        "seeds": list(range(10)),
        "target_treatments": ["low", "medium", "high"],
    }
    if raw["config"] != expected_config:
        print("CLAIM_5_FAIL: source-certificate protocol drift")
        return 1

    checked = run_checker()
    print(f"CLAIM_5_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        return 1
    metric_control = run_checker("--mutate-metric-substitution")
    print(f"CLAIM_5_NEGATIVE_CONTROL_METRIC={metric_control.stdout.strip()}")
    if metric_control.returncode == 0:
        print("CLAIM_5_FAIL: metric mutation accepted")
        return 1
    source_control = run_checker("--mutate-source-range")
    print(f"CLAIM_5_NEGATIVE_CONTROL_SOURCE={source_control.stdout.strip()}")
    if source_control.returncode == 0:
        print("CLAIM_5_FAIL: source-range mutation accepted")
        return 1

    source = raw["paper_source_audit"]
    if not (
        source["msnn_fr_min_percent"] == 3.13
        and source["msnn_fr_max_percent"] == 54.16
        and source["snn_fr_max_percent"] == 22.66
        and source["ratios_outside_closed_2_to_3"] == 3
    ):
        print("CLAIM_5_FAIL: exact source contradiction disappeared")
        return 1

    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": raw["config"]["seeds"],
    }
    result = {
        "claim_id": "claim_5",
        "evidence_type": (
            "pinned primary-source Tables 2-3 certificate, independent "
            "range/ratio checker, metric-definition witness, and full "
            "ten-seed Appendix-B assignment-proportion audit"
        ),
        "negative_control_exit_codes": {
            "metric_substitution": metric_control.returncode,
            "source_range": source_control.returncode,
        },
        "source_table_falsification": {
            "error_ratios_outside_2_to_3": 3,
            "msnn_fr_actual_range_percent": [3.13, 54.16],
            "snn_fr_actual_max_percent": 22.66,
        },
        "verdict": "FALSIFIED",
    }
    print("CLAIM_5_PROVENANCE_FINAL=" + json.dumps(provenance, sort_keys=True))
    print("CLAIM_RESULT_JSON=" + json.dumps(result, sort_keys=True))
    print("CLAIM_5_FALSIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
