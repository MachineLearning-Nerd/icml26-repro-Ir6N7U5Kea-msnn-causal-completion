"""Fail-closed verifier for the exact Corollary 4.11 claim contract."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / ".openresearch" / "artifacts" / "claim_3"
CERTIFICATE = ARTIFACT / "proof_certificate.json"
EXPECTED_RESULT = ARTIFACT / "raw_result.json"
CHECKER = Path(__file__).with_name("independent_checker.py")


def _sub(left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
    keys = set(left) | set(right)
    result = {key: left.get(key, 0) - right.get(key, 0) for key in sorted(keys)}
    return {key: value for key, value in result.items() if value}


def _ratio(
    numerator: dict[str, dict[str, int]],
    denominator: dict[str, dict[str, int]],
) -> dict[str, dict[str, int]]:
    return {
        name: _sub(numerator[name], denominator[name])
        for name in sorted(numerator)
    }


def main() -> int:
    started = time.perf_counter()
    certificate = json.loads(CERTIFICATE.read_text())
    terms = certificate["theorem_4_8_leading_terms"]
    expected = certificate["corollary_4_11_ratios"]
    direct_snn = _ratio(
        terms["snn_sparse"]["exponents"],
        terms["msnn_rich"]["exponents"],
    )
    direct_msnn = _ratio(
        terms["msnn_sparse"]["exponents"],
        terms["msnn_rich"]["exponents"],
    )
    if direct_snn != expected["snn_sparse_over_msnn_rich"]["exponents"]:
        print("CLAIM_3_FAIL: direct SNN ratio derivation mismatch")
        return 1
    if direct_msnn != expected["msnn_sparse_over_msnn_rich"]["exponents"]:
        print("CLAIM_3_FAIL: direct MSNN ratio derivation mismatch")
        return 1

    checked = subprocess.run(
        [sys.executable, str(CHECKER), str(CERTIFICATE)],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_3_CHECKER={checked.stdout.strip()}")
    if checked.returncode != 0:
        print(checked.stderr)
        return 1

    control = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            str(CERTIFICATE),
            "--mutate-msnn-sparse",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    print(f"CLAIM_3_NEGATIVE_CONTROL={control.stdout.strip()}")
    if control.returncode == 0:
        print("CLAIM_3_FAIL: mutated exponent was incorrectly accepted")
        return 1
    control_payload = json.loads(control.stdout)
    if control_payload["errors"] != [
        "MSNN sparse-to-rich exponent vector mismatch"
    ]:
        print("CLAIM_3_FAIL: mutation failed for an unexpected reason")
        return 1

    result = {
        "claim_id": "claim_3",
        "exact_exponents": {
            "msnn_sparse_to_rich": "r",
            "snn_sparse_to_rich": "r*c+r+c",
        },
        "negative_control_exit_code": control.returncode,
        "verdict": "VERIFIED",
    }
    if result != json.loads(EXPECTED_RESULT.read_text()):
        print("CLAIM_3_FAIL: committed raw result does not match regenerated result")
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
    print(f"CLAIM_3_PROVENANCE={json.dumps(provenance, sort_keys=True)}")
    print(f"CLAIM_RESULT_JSON={json.dumps(result, sort_keys=True)}")
    print("CLAIM_3_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
