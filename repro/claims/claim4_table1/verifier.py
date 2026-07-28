"""Fail-closed verifier for Claim 4's exact Table 1 contract."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".openresearch" / "artifacts" / "claim_4" / "raw_result.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def main() -> int:
    started = time.perf_counter()
    raw = json.loads(
        RAW.read_text(), parse_constant=reject_nonstandard_constant
    )
    if (
        raw["config"]["m"] != 300
        or raw["config"]["n"] != 100
        or raw["config"]["seeds"] != list(range(10))
        or raw["config"]["target_treatment_probability"] != 0.01
    ):
        print("CLAIM_4_FAIL: protocol is not the paper-scale low-treatment setup")
        return 1
    if not raw["solver_control"]["passed"] or not raw["solver_order_control"]["passed"]:
        print("CLAIM_4_FAIL: clique solver controls did not pass")
        return 1
    if any(
        record[method]["invariant_failures"]
        for record in raw["per_seed"]
        for method in ("snn", "msnn")
    ):
        print("CLAIM_4_FAIL: selected anchor violated treatment invariants")
        return 1

    checked = subprocess.run(
        [sys.executable, str(CHECKER)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_4_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        print(checked.stderr)
        return 1
    control = subprocess.run(
        [sys.executable, str(CHECKER), "--mutate-metric-substitution"],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_4_NEGATIVE_CONTROL={control.stdout.strip()}")
    if control.returncode == 0:
        print("CLAIM_4_FAIL: metric substitution mutation was accepted")
        return 1

    msnn = raw["aggregates"]["msnn"]
    summary = {
        "author_code_normalized_mae": msnn["code_normalized_mae"]["mean"],
        "msnn_feasible_rate_percent": msnn["feasible_rate_percent"]["mean"],
        "paper_defined_entrywise_mre": (
            msnn["paper_defined_entrywise_mre"]["mean"]
        ),
        "published_value_labeled_mre": 0.0391,
    }
    provenance = {
        "actual_cpu_allocation": "HF cpu-upgrade: 8 vCPU, 32 GB",
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "logical_cpu_count_visible": os.cpu_count(),
        "platform": platform.platform(),
        "runtime_seconds": round(time.perf_counter() - started, 6),
        "seeds": raw["config"]["seeds"],
    }
    result = {
        "claim_id": "claim_4",
        "evidence_type": "paper-scale author-code-equivalent run plus metric audit",
        "negative_control_exit_code": control.returncode,
        "summary": summary,
        "verdict": "FALSIFIED",
    }
    print(f"CLAIM_4_PROVENANCE_FINAL={json.dumps(provenance, sort_keys=True)}")
    print(f"CLAIM_RESULT_JSON={json.dumps(result, sort_keys=True)}")
    print("CLAIM_4_FALSIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
