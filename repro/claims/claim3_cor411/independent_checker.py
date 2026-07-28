"""Independent exact checker for the Corollary 4.11 proof certificate."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path


EXPECTED_SOURCE_SHA256 = (
    "f2c8f7a37e8ade697a3ec605688a7a99b84bac4638385e1d1cb7f3dd93d18448"
)


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


def check(certificate: dict, mutate_msnn_sparse: bool = False) -> tuple[bool, list[str]]:
    errors: list[str] = []
    terms = certificate["theorem_4_8_leading_terms"]
    msnn_sparse = {
        name: dict(poly) for name, poly in terms["msnn_sparse"]["exponents"].items()
    }
    if mutate_msnn_sparse:
        msnn_sparse["p_d"]["constant"] = 1

    snn_ratio = _ratio(
        terms["snn_sparse"]["exponents"],
        terms["msnn_rich"]["exponents"],
    )
    msnn_ratio = _ratio(msnn_sparse, terms["msnn_rich"]["exponents"])
    claimed = certificate["corollary_4_11_ratios"]
    if snn_ratio != claimed["snn_sparse_over_msnn_rich"]["exponents"]:
        errors.append("SNN sparse-to-rich exponent vector mismatch")
    if msnn_ratio != claimed["msnn_sparse_over_msnn_rich"]["exponents"]:
        errors.append("MSNN sparse-to-rich exponent vector mismatch")

    if certificate["source"]["sha256"] != EXPECTED_SOURCE_SHA256:
        errors.append("paper source SHA-256 is not the audited source")

    r = 3
    c = 2
    p_d = Fraction(1, 100)
    p_max = Fraction(4, 5)
    probabilities = [
        Fraction(1, 100),
        Fraction(1, 40),
        Fraction(1, 20),
        Fraction(4, 5),
    ]
    gamma = sum((p / p_max) ** (r + 1) for p in probabilities)
    common = Fraction(17, 13)
    snn_sparse_value = common * p_d ** (r * c + r + c)
    msnn_sparse_value = common * gamma**c * p_d**r * p_max ** ((r + 1) * c)
    msnn_rich_value = (
        common * gamma**c * p_max**r * p_max ** ((r + 1) * c)
    )
    claimed_snn = gamma ** (-c) * (p_d / p_max) ** (r * c + r + c)
    claimed_msnn = (p_d / p_max) ** r
    if snn_sparse_value / msnn_rich_value != claimed_snn:
        errors.append("exact rational SNN ratio substitution failed")
    if msnn_sparse_value / msnn_rich_value != claimed_msnn:
        errors.append("exact rational MSNN ratio substitution failed")

    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--mutate-msnn-sparse", action="store_true")
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text())
    passed, errors = check(certificate, args.mutate_msnn_sparse)
    payload = {
        "checker": "independent_sparse_rich_exponent_checker",
        "checks": 5,
        "errors": errors,
        "mutation": args.mutate_msnn_sparse,
        "passed": passed,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
