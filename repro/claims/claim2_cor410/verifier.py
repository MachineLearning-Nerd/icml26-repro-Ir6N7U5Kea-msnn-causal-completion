"""Fail-closed verifier for the exact Corollary 4.10 claim contract."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / ".openresearch" / "artifacts" / "claim_2"
CERTIFICATE = ARTIFACT / "proof_certificate.json"
EXPECTED_RESULT = ARTIFACT / "raw_result.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def _sub(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    keys = set(left) | set(right)
    result = {key: left.get(key, 0) - right.get(key, 0) for key in sorted(keys)}
    return {key: value for key, value in result.items() if value}


def main() -> int:
    started = time.perf_counter()
    certificate = json.loads(CERTIFICATE.read_text())
    theorem = certificate["theorem_4_8_leading_terms"]
    derived = {
        name: _sub(
            theorem["msnn"]["exponents"][name],
            theorem["snn"]["exponents"][name],
        )
        for name in sorted(theorem["snn"]["exponents"])
    }
    if derived != certificate["corollary_4_10_ratio"]["exponents"]:
        print("CLAIM_2_FAIL: direct exponent derivation mismatch")
        return 1

    checked = subprocess.run(
        [sys.executable, str(CHECKER), str(CERTIFICATE)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_2_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        print(checked.stderr)
        return 1

    control = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            str(CERTIFICATE),
            "--mutate-snn-exponent",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_2_NEGATIVE_CONTROL={control.stdout.strip()}")
    if control.returncode == 0:
        print("CLAIM_2_FAIL: mutated exponent was incorrectly accepted")
        return 1
    control_payload = json.loads(control.stdout)
    if control_payload["errors"] != [
        "derived exponent vector does not match the claimed ratio"
    ]:
        print("CLAIM_2_FAIL: mutation failed for an unexpected reason")
        return 1

    result = {
        "claim_id": "claim_2",
        "evidence_type": "exact symbolic certificate plus independent checker",
        "identity": (
            "E[K_MSNN(d)]/E[K_SNN(d)] = "
            "(1+o(1))*[sum_d'(p_d'/p_d)^(r+1)]^c"
        ),
        "negative_control_exit_code": control.returncode,
        "verdict": "VERIFIED",
    }
    if result != json.loads(EXPECTED_RESULT.read_text()):
        print("CLAIM_2_FAIL: committed raw result does not match regenerated result")
        return 1
    provenance = {
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "logical_cpu_count": os.cpu_count(),
        "platform": platform.platform(),
        "seed": "none_exact_symbolic",
        "verifier_runtime_seconds": round(time.perf_counter() - started, 6),
    }
    print(f"CLAIM_2_PROVENANCE={json.dumps(provenance, sort_keys=True)}")
    print(f"CLAIM_RESULT_JSON={json.dumps(result, sort_keys=True)}")
    print("CLAIM_2_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
