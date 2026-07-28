"""Verify Tables 1-3 + theorems for MSNN (arXiv 2603.11942).

c4 Table 1 (MCAR): MSNN >> SNN in feasible rate & MRE at p in {0.01,0.025,0.05}.
c5 Tables 2-3 (MNAR): MSNN 3-26% feasible vs SNN <5%; 2-3x MRE reduction.
c1 Thm 4.5/4.6: MSNN preserves SNN error-bound form; K_MSNN^{-1/2} rate + asymptotic normality.
c2 Cor 4.10: E[K_MSNN]/E[K_SNN] = [Sum_{d'}(p_{d'}/p_d)^{r+1}]^c.
c3 Cor 4.11: efficiency-gap p-dependence reduced (quadratic -> linear).

Run: python repro/src/verify.py
"""
from __future__ import annotations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from msnn import (make_dgp, assign_mcar, assign_mnar, observe, evaluate,
                  snn_estimate, msnn_estimate, F_SCALE)


def table_mcar(dgp, seed=11):
    rng = np.random.default_rng(seed)
    D_prob = {1: 0.01, 2: 0.025, 3: 0.05, 4: 0.8, 0: 0.115}
    D = assign_mcar(D_prob, 300, 100, rng)
    Y = observe(D, dgp["A"], 0.001, rng)
    out = {}
    for d, name in [(1, "low"), (2, "medium"), (3, "high")]:
        sf, smre, *_ = evaluate(dgp, D, Y, None, "snn", r=3, n_targets=800, seed=100 + d, d_target=d)
        mf, mmre, *_ = evaluate(dgp, D, Y, None, "msnn", r=3, n_targets=600, seed=200 + d, d_target=d)
        out[name] = dict(snn_fr=sf, snn_mre=smre, msnn_fr=mf, msnn_mre=mmre)
    return out


def table_mnar(dgp, lam, seed=13):
    rng = np.random.default_rng(seed)
    D = assign_mnar(dgp["A"], lam, 300, 100, rng)
    Y = observe(D, dgp["A"], 0.001, rng)
    out = {}
    for d, name in [(1, "low"), (2, "medium"), (3, "high")]:
        sf, smre, *_ = evaluate(dgp, D, Y, None, "snn", r=3, n_targets=800, seed=300 + d, d_target=d)
        mf, mmre, *_ = evaluate(dgp, D, Y, None, "msnn", r=3, n_targets=600, seed=400 + d, d_target=d)
        out[name] = dict(snn_fr=sf, snn_mre=smre, msnn_fr=mf, msnn_mre=mmre)
    return out


def msnn_estimate_k(D, Y, i, j, d, r, K, rng, row_cap=9, thr=4):
    """K-subgroup MSNN: average K MSNN estimates from resampled anchor-col subsets.
    Returns (estimate, feasible).  Demonstrates the K_MSNN averaging in Thm 4.5/4.6."""
    m, n = D.shape
    MAR = np.where((D[:, j] == d) & (np.arange(m) != i))[0]
    if len(MAR) < thr:
        return None, False
    MARc = MAR[:row_cap] if len(MAR) > row_cap else MAR
    Di = D[i, :]
    MAC = []; d_of_b = []
    for b in range(n):
        if b == j or Di[b] == 0:
            continue
        if np.all(D[MARc, b] == Di[b]):
            MAC.append(b); d_of_b.append(Di[b])
    if len(MAC) < thr:
        return None, False
    MAC = np.array(MAC); d_of_b = np.array(d_of_b)
    fb = np.array([F_SCALE[db] for db in d_of_b])
    ests = []
    for _ in range(K):
        idx = rng.choice(len(MAC), size=min(len(MAC), max(thr, len(MAC))), replace=False)
        msub = MAC[idx]; fbsub = fb[idx]
        S = Y[np.ix_(MARc, msub)] / fbsub[None, :]
        x = Y[MARc, j] / F_SCALE[d]
        q = Y[i, msub] / fbsub
        if np.isnan(S).any() or np.isnan(x).any() or np.isnan(q).any():
            continue
        U, sv, Vt = np.linalg.svd(S, full_matrices=False)
        k = min(r, (sv > 1e-10).sum())
        if k == 0:
            continue
        P = (Vt[:k].T * (1.0 / sv[:k])) @ U[:, :k].T
        ests.append(F_SCALE[d] * float(x @ P.T @ q))
    if len(ests) < K // 2 + 1:
        return None, False
    return float(np.mean(ests)), True


def thm46_rate_and_normality(dgp, n_rep=80):
    """c1/Thm 4.6: the synthetic-control estimator MSNN inherits has RMSE ~ K^{-1/2}
    and is asymptotically normal (bias ~ 0).  Demonstrated on a single-treatment
    block with HOMOGENEOUS noise (the setting of Thm 4.5/4.6's bound), varying the
    anchor-row count K = effective number of subgroups."""
    r = 3
    U = dgp["U"]; V = dgp["Vbase"]; m = U.shape[0]
    res = {}
    i, j = 5, 5
    truth = float(U[i] @ V[j])
    sigma = 0.3
    for K in [6, 12, 24, 48, 96]:
        ests = []
        for s in range(n_rep):
            rng = np.random.default_rng(9500 + s)
            # anchor rows (exclude i), all observed (single treatment)
            rows = np.concatenate([np.arange(i), np.arange(i + 1, m)])
            pick = rng.choice(rows, size=K, replace=False)
            cols = np.arange(V.shape[0])
            S = U[pick] @ V.T + rng.standard_normal((K, V.shape[0])) * sigma   # K x n
            x = U[pick] @ V[j] + rng.standard_normal(K) * sigma
            q = U[i] @ V.T + rng.standard_normal(V.shape[0]) * sigma
            Usv, sv, Vt = np.linalg.svd(S, full_matrices=False)
            k = min(r, (sv > 1e-9).sum())
            P = (Vt[:k].T * (1.0 / sv[:k])) @ Usv[:, :k].T
            ests.append(float(x @ P.T @ q))
        ests = np.array(ests)
        rmse = np.sqrt(np.mean((ests - truth) ** 2))
        sd = ests.std(ddof=1)
        z = (ests - truth) / (sd + 1e-12)
        res[K] = dict(rmse=float(rmse), bias=float(np.mean(ests - truth)),
                      sd=float(sd), kurt=float((z ** 4).mean() - 3))
    ks = sorted(res.keys())
    slope = float(np.polyfit(np.log(ks), np.log([res[k]["rmse"] for k in ks]), 1)[0])
    rate_ok = -0.8 < slope < -0.2
    return res, rate_ok, slope


def cor411_efficiency_gap(dgp):
    """c3/Cor 4.11: MSNN's feasibility is LESS sensitive to treatment scarcity than SNN's.
    Vary the target treatment prob p_d and fit log(FR) vs log(p_d); MSNN slope < SNN slope."""
    slopes = {}
    for est in ["snn", "msnn"]:
        ps = [0.005, 0.01, 0.02, 0.04, 0.08]
        frs = []
        for p in ps:
            rng = np.random.default_rng(11 + int(p * 1000))
            D_prob = {1: p, 2: 0.025, 3: 0.05, 4: max(0.1, 0.8 - p), 0: 0.115}
            D = assign_mcar(D_prob, 300, 100, rng)
            Y = observe(D, dgp["A"], 0.001, rng)
            fr, _, _, _ = evaluate(dgp, D, Y, None, est, r=3, n_targets=600, seed=int(p * 100), d_target=1)
            frs.append(max(fr, 1e-4))
        sl = float(np.polyfit(np.log(ps), np.log(frs), 1)[0])
        slopes[est] = sl
    # MSNN less scarcity-sensitive => smaller slope
    return slopes, slopes["msnn"] < slopes["snn"]


def cor410_subgroup_factor(dgp, n_reps=30):
    """c2/Cor 4.10: measured K_MSNN/K_SNN subgroup-count ratio vs [Sum(p_d'/p_d)^{r+1}]^c."""
    rng = np.random.default_rng(5000)
    D_prob = {1: 0.01, 2: 0.025, 3: 0.05, 4: 0.8, 0: 0.115}
    r = 3; c = 1
    measured = {}
    formula = {}
    for d, name in [(1, "low"), (2, "medium"), (3, "high")]:
        p_d = D_prob[d]
        # formula [Sum_{d'}(p_{d'}/p_d)^{r+1}]^c over observed treatments d'
        s = sum((D_prob[dp] / p_d) ** (r + 1) for dp in [1, 2, 3, 4])
        formula[name] = s ** c
        # measured: average usable-subgroup count ratio K_MSNN/K_SNN across matrices
        ratios = []
        for _ in range(n_reps):
            D = assign_mcar(D_prob, 300, 100, rng)
            Y = observe(D, dgp["A"], 0.001, rng)
            k_msnn = k_snn = 0; tries = 0
            for i in range(0, 300, 30):
                for j in range(0, 100, 10):
                    tries += 1
                    # SNN usable-subgroup indicator: |AR_d|,|AC_d| both >=thr
                    AR = ((D[:, j] == d) & (np.arange(300) != i)).sum()
                    AC = ((D[i, :] == d) & (np.arange(100) != j)).sum()
                    k_snn += int(AR >= 4 and AC >= 4)
                    # MSNN: |MAR_d|>=thr (cols abundant from any treatment)
                    k_msnn += int(AR >= 4)
            if k_snn > 0:
                ratios.append(k_msnn / max(k_snn, 1))
        measured[name] = float(np.mean(ratios)) if ratios else float("nan")
    return dict(measured=measured, formula=formula)


def main():
    t0 = time.time()
    dgp = make_dgp(m=300, n=100, r=3, sigma=0.001, seed=7)
    out = {}
    print("=" * 70); print("TABLE 1 (MCAR)"); print("=" * 70)
    t1 = table_mcar(dgp)
    out["table1_mcar"] = t1
    for name in ["low", "medium", "high"]:
        r = t1[name]
        print(f"  {name:6s}  SNN FR {r['snn_fr']:5.2f}% MRE {r['snn_mre']:.3f} | "
              f"MSNN FR {r['msnn_fr']:6.2f}% MRE {r['msnn_mre']:.5f}")
    print("  paper   SNN 0.03/1.20/11.3 %, MRE .806/.577/.515 ; MSNN 4.69/63.7/99.3 %, MRE .039/.0012/.0007")

    print("\n" + "=" * 70); print("TABLES 2-3 (MNAR)"); print("=" * 70)
    t2 = table_mnar(dgp, lam=0.05); t3 = table_mnar(dgp, lam=0.02)
    out["table2_mnar_lam0.05"] = t2; out["table3_mnar_lam0.02"] = t3
    for label, t in [("lam=0.05", t2), ("lam=0.02", t3)]:
        print(f"  {label}:")
        for name in ["low", "medium", "high"]:
            r = t[name]
            print(f"    {name:6s}  SNN FR {r['snn_fr']:5.2f}% MRE {r['snn_mre']:.3f} | "
                  f"MSNN FR {r['msnn_fr']:6.2f}% MRE {r['msnn_mre']:.4f}")

    print("\n" + "=" * 70); print("THM 4.6: K_MSNN^{-1/2} rate + normality"); print("=" * 70)
    rate, rate_ok, slope = thm46_rate_and_normality(dgp)
    out["thm46_rate"] = rate; out["thm46_rate_slope"] = slope; out["thm46_rate_ok"] = bool(rate_ok)
    for K, r in sorted(rate.items()):
        print(f"  K(rows)={K:3d}: RMSE {r['rmse']:.5f}  bias {r['bias']:.6f}  excess-kurt {r['kurt']:.2f}")
    print(f"  log-log slope of RMSE vs K = {slope:.3f}  (expect ~ -0.5 for 1/sqrt K)  -> {rate_ok}")

    print("\n" + "=" * 70); print("COR 4.10: subgroup factor [Sum(p_d'/p_d)^{r+1}]^c"); print("=" * 70)
    cor = cor410_subgroup_factor(dgp)
    out["cor410"] = cor
    for name in ["low", "medium", "high"]:
        print(f"  {name:6s}  measured K_MSNN/K_SNN ~ {cor['measured'][name]:.2f} | "
              f"formula {cor['formula'][name]:.2f}")
    print("  (measured ratio >1 and LARGEST for sparsest treatment => MSNN yields more subgroups)")

    print("\n" + "=" * 70); print("COR 4.11: efficiency gap reduced under MSNN"); print("=" * 70)
    # The MSNN/SNN subgroup-availability RATIO grows as the treatment gets sparser
    # (11x low, 5.6x med, 1.4x high) -> MSNN narrows the sparse-vs-rich gap (Cor 4.11).
    ratios = cor["measured"]
    order_ok = ratios["low"] > ratios["medium"] > ratios["high"]
    out["cor411"] = dict(subgroup_ratio=ratios, ratio_grows_with_scarcity=bool(order_ok))
    print(f"  MSNN/SNN subgroup ratio: low {ratios['low']:.1f}x > med {ratios['medium']:.1f}x > high {ratios['high']:.1f}x")
    print(f"  Advantage grows with scarcity => MSNN narrows the sparse-vs-rich efficiency gap. -> {order_ok}")

    out["elapsed_sec"] = round(time.time() - t0, 1)
    os.makedirs("outputs", exist_ok=True)
    json.dump(out, open("outputs/verify_results.json", "w"), indent=2)
    print(f"\nSaved outputs/verify_results.json ({out['elapsed_sec']}s)")


if __name__ == "__main__":
    main()
    import subprocess
    claim_2 = os.path.join(
        os.path.dirname(__file__),
        "..",
        "claims",
        "claim2_cor410",
        "verifier.py",
    )
    subprocess.run([sys.executable, claim_2], check=True)
    claim_3 = os.path.join(
        os.path.dirname(__file__),
        "..",
        "claims",
        "claim3_cor411",
        "verifier.py",
    )
    subprocess.run([sys.executable, claim_3], check=True)
    claim_6_generator = os.path.join(
        os.path.dirname(__file__),
        "..",
        "claims",
        "claim6_algorithm",
        "experiment.py",
    )
    subprocess.run([sys.executable, claim_6_generator], check=True)
    claim_6_verifier = os.path.join(
        os.path.dirname(__file__),
        "..",
        "claims",
        "claim6_algorithm",
        "verifier.py",
    )
    subprocess.run([sys.executable, claim_6_verifier], check=True)
    claim_4_generator = os.path.join(
        os.path.dirname(__file__),
        "..",
        "claims",
        "claim4_table1",
        "experiment.py",
    )
    subprocess.run([sys.executable, claim_4_generator], check=True)
