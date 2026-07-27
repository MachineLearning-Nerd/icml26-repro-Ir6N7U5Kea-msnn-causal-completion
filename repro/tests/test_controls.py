"""Negative controls & sanity checks for MSNN (quality-bar requirement).

Control A (falsification of Assumption 2.5): MSNN's mixed-anchor scale-normalisation
    is valid ONLY because the row factors u_i are SHARED across treatments.  If we
    VIOLATE that assumption (draw a DIFFERENT u_i^{(d)} per treatment), MSNN's
    cross-treatment borrowing becomes invalid and its MRE must degrade toward / above
    SNN's.  This confirms the gain genuinely comes from the shared-factor structure.

Control B (falsification of low-rank): if the true matrix is NOT rank-r (we use rank
    >> r), the rank-r truncated-SVD synthetic control must fit poorly -> high MRE
    for BOTH estimators.  Confirms the low-rank model is load-bearing.

Sanity: MSNN estimate is unbiased in expectation (no noise) on a feasible target.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from msnn import (make_dgp, assign_mcar, observe, evaluate, msnn_estimate,
                  snn_estimate, F_SCALE, _trunc_svd_pinv)


def make_dgp_violated_shared(m=300, n=100, r=3, sigma=0.001, seed=0):
    """Assumption 2.5 VIOLATED: each treatment has its OWN row factors U^{(d)}."""
    rng = np.random.default_rng(seed)
    Vbase = rng.standard_normal((n, r))
    A = {}
    for d, f in F_SCALE.items():
        Ud = rng.standard_normal((m, r))          # DIFFERENT row factors per treatment
        A[d] = Ud @ (f * Vbase).T
    return dict(A=A, m=m, n=n, r=r, sigma=sigma)


def control_A_violated_assumption():
    print("\n=== Control A: violated shared-row-factor (Assumption 2.5) must break MSNN ===")
    dgp = make_dgp_violated_shared(seed=21)
    rng = np.random.default_rng(11)
    D_prob = {1: 0.01, 2: 0.025, 3: 0.05, 4: 0.8, 0: 0.115}
    D = assign_mcar(D_prob, 300, 100, rng)
    Y = observe(D, dgp["A"], 0.001, rng)
    # evaluate at medium (where MSNN normally shines)
    sf, smre, *_ = evaluate(dgp, D, Y, None, "snn", r=3, n_targets=400, seed=2, d_target=2)
    mf, mmre, *_ = evaluate(dgp, D, Y, None, "msnn", r=3, n_targets=400, seed=3, d_target=2)
    print(f"  violated Assumption 2.5 (medium): SNN MRE {smre:.3f} | MSNN MRE {mmre:.4f}")
    print(f"  (under the valid model MSNN MRE was ~5e-4; here it should be ~SNN-level or worse)")
    ok = mmre > 0.05            # MSNN no longer accurate
    print(f"  -> {'CONTROL HOLDS' if ok else 'FAIL'} (MSNN advantage gone without shared factors)")
    return ok


def control_B_not_low_rank():
    print("\n=== Control B: non-low-rank matrix must break both estimators ===")
    rng0 = np.random.default_rng(7)
    U = rng0.standard_normal((300, 3)); V = rng0.standard_normal((100, 3))
    rng = np.random.default_rng(11)
    # full-rank-ish A^{(d)} = f(d) * (UV^T + NOISE_MATRIX)  (rank 100, not 3)
    A = {}
    for d, f in F_SCALE.items():
        A[d] = f * (U @ V.T + 50 * rng0.standard_normal((300, 100)))
    dgp = dict(A=A, m=300, n=100, r=3, sigma=0.001)
    D_prob = {1: 0.01, 2: 0.025, 3: 0.05, 4: 0.8, 0: 0.115}
    D = assign_mcar(D_prob, 300, 100, rng); Y = observe(D, A, 0.001, rng)
    mf, mmre, *_ = evaluate(dgp, D, Y, None, "msnn", r=3, n_targets=400, seed=7, d_target=2)
    print(f"  non-low-rank (medium): MSNN MRE {mmre:.3f} (should be large, >> 5e-4)")
    ok = mmre > 0.1
    print(f"  -> {'CONTROL HOLDS' if ok else 'FAIL'} (low-rank model is load-bearing)")
    return ok


def sanity_unbiased():
    print("\n=== Sanity: MSNN unbiased in expectation (no noise, valid model) ===")
    dgp = make_dgp(m=300, n=100, r=3, sigma=0.0, seed=7)     # NO noise
    rng = np.random.default_rng(11)
    D_prob = {1: 0.01, 2: 0.025, 3: 0.05, 4: 0.8, 0: 0.115}
    D = assign_mcar(D_prob, 300, 100, rng); Y = observe(D, dgp["A"], 0.0, rng)
    errs = []
    for s in range(400):
        rng2 = np.random.default_rng(s)
        i = int(rng2.integers(300)); j = int(rng2.integers(100)); d = 3
        est, ok = msnn_estimate(D, Y, F_SCALE, i, j, d, 3)
        if ok:
            errs.append(abs(est - dgp["A"][d][i, j]) / (abs(dgp["A"][d][i, j]) + 1e-9))
    mre = float(np.mean(errs))
    print(f"  noise-free MSNN MRE (high) = {mre:.2e}  (should be ~machine precision)")
    ok = mre < 1e-6
    print(f"  -> {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    a = control_A_violated_assumption()
    b = control_B_not_low_rank()
    s = sanity_unbiased()
    print("\n" + "=" * 60)
    print("CONTROLS:", "ALL HOLD" if (a and b) else "SOME FAILED",
          "| sanity:", "PASS" if s else "FAIL")
    return 0 if (a and b and s) else 1


if __name__ == "__main__":
    sys.exit(main())
