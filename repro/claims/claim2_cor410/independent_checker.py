"""Independent exact checker for the Corollary 4.10 proof certificate.

This module intentionally imports nothing from the production verifier.
"""

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


def _pow(base: Fraction, exponent: int) -> Fraction:
    return base**exponent


def check(certificate: dict, mutate_snn_exponent: bool = False) -> tuple[bool, list[str]]:
    errors: list[str] = []
    theorem = certificate["theorem_4_8_leading_terms"]
    snn = theorem["snn"]["exponents"]
    msnn = theorem["msnn"]["exponents"]
    if mutate_snn_exponent:
        snn = {name: dict(poly) for name, poly in snn.items()}
        snn["p_d"]["c"] -= 1

    derived = {name: _sub(msnn[name], snn[name]) for name in sorted(snn)}
    claimed = certificate["corollary_4_10_ratio"]["exponents"]
    if derived != claimed:
        errors.append("derived exponent vector does not match the claimed ratio")

    if certificate["source"]["sha256"] != EXPECTED_SOURCE_SHA256:
        errors.append("paper source SHA-256 is not the audited source")

    if certificate["asymptotic_rule"] != "(1-o(1))/(1-o(1)) = 1+o(1)":
        errors.append("asymptotic prefactor rule is missing or changed")

    r = 3
    c = 2
    probabilities = [
        Fraction(1, 100),
        Fraction(1, 40),
        Fraction(1, 20),
        Fraction(4, 5),
    ]
    p_d = probabilities[0]
    p_max = max(probabilities)
    gamma = sum(_pow(p / p_max, r + 1) for p in probabilities)
    theorem_ratio = (
        _pow(gamma, c)
        * _pow(p_d, r)
        * _pow(p_max, (r + 1) * c)
        / _pow(p_d, r * c + r + c)
    )
    claimed_ratio = _pow(
        sum(_pow(p / p_d, r + 1) for p in probabilities),
        c,
    )
    if theorem_ratio != claimed_ratio:
        errors.append("exact rational substitution does not satisfy the identity")

    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--mutate-snn-exponent", action="store_true")
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text())
    passed, errors = check(certificate, args.mutate_snn_exponent)
    payload = {
        "checker": "independent_laurent_monomial_checker",
        "checks": 4,
        "errors": errors,
        "mutation": args.mutate_snn_exponent,
        "passed": passed,
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
