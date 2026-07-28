"""Fail-closed verifier for Claim 6's frozen full-scale evidence."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / ".openresearch" / "artifacts" / "claim_6"
RAW = ARTIFACT / "raw_result.json"
ACCEPTANCE = ARTIFACT / "acceptance.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def main() -> int:
    started = time.perf_counter()
    raw = json.loads(RAW.read_text())
    acceptance = json.loads(ACCEPTANCE.read_text())
    direct_checks = {
        "all_corrupted_controls_rejected": (
            raw["controls_rejected"] == raw["invariant_checks"]
        ),
        "all_selected_cliques_audited": (
            raw["invariant_checks"] == raw["selected_cliques"]
        ),
        "assumption_control_degrades_error": (
            raw["invalid_shared_factor_scaled_mae"]
            > 5 * raw["valid_shared_factor_scaled_mae"]
        ),
        "full_paper_scale": (
            raw["config"]["m"] == 300
            and raw["config"]["n"] == 100
            and len(raw["config"]["seeds"]) == 10
        ),
        "mixed_treatments_observed": raw["mixed_cliques"] > 0,
        "noisy_valid_reconstruction": (
            raw["valid_shared_factor_scaled_mae"] < 0.05
        ),
        "sufficient_estimable_targets": raw["estimable_targets"] >= 100,
    }
    if direct_checks != acceptance or not all(direct_checks.values()):
        print("CLAIM_6_FAIL: frozen acceptance does not match raw evidence")
        return 1

    checked = subprocess.run(
        [sys.executable, str(CHECKER)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_6_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        print(checked.stderr)
        return 1

    control = subprocess.run(
        [sys.executable, str(CHECKER), "--mutate-target-treatment"],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_6_NEGATIVE_CONTROL={control.stdout.strip()}")
    if control.returncode == 0:
        print("CLAIM_6_FAIL: wrong target treatment was accepted")
        return 1
    control_payload = json.loads(control.stdout)
    if control_payload["passed"] or not control_payload["errors"]:
        print("CLAIM_6_FAIL: mutation did not fail with a recorded reason")
        return 1

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
        "claim_id": "claim_6",
        "evidence_type": (
            "paper-scale noisy algorithm audit plus independent reconstruction"
        ),
        "negative_control_exit_code": control.returncode,
        "verdict": "VERIFIED",
    }
    print(f"CLAIM_6_PROVENANCE_FINAL={json.dumps(provenance, sort_keys=True)}")
    print(f"CLAIM_RESULT_JSON={json.dumps(result, sort_keys=True)}")
    print("CLAIM_6_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
