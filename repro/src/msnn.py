"""MSNN / SNN — Causal Matrix Completion under Multiple Treatments (clean-room repro).

arXiv 2603.11942.  Y_{ij}^{(d)} = <u_i, v_j^{(d)}> + eps, with U shared across treatments
(Assumption 2.5) and V^{(d)} scaled by f(d).  Estimator = synthetic-nearest-neighbors
truncated-SVD synthetic control on anchor blocks.

SNN : anchor rows AR(d)={a: D[a,j]=d}, anchor cols AC(d)={b: D[i,b]=d}, anchor block must
      be observed at treatment d (D[a,b]=d).  Â = x^T (truncSVD^+ S) q.
MSNN: anchor rows MAR(d)={a: D[a,j]=d} (single treatment d), anchor cols MAC(d) any treatment
      d(b)=D[i,b]!=0 that is CONSISTENT across MAR; block scale-normalised by 1/f(d(b)).
      Â = f(d) * x_norm^T (truncSVD^+ S_w) q_norm.

Pure numpy/scipy, CPU, deterministic given a seed.
"""
from __future__ import annotations
import numpy as np

TREATMENTS = {"low": 1, "medium": 2, "high": 3, "veryhigh": 4}   # D=0 => unobserved
F_SCALE = {1: 1.0, 2: 5.0, 3: 25.0, 4: 625.0}


# --------------------------------------------------------------------------- #
#  Data-generating process
# --------------------------------------------------------------------------- #
def make_dgp(m=300, n=100, r=3, sigma=0.001, seed=0):
    """Shared U (m x r), per-treatment V^{(d)} = f(d) * V_base; A^{(d)} = <U, V^{(d)}>."""
    rng = np.random.default_rng(seed)
    U = rng.standard_normal((m, r))                                 # shared row factors, O(1) entries
    Vbase = rng.standard_normal((n, r))                             # base column factors
    A = {}                                                          # A^{(d)} (m x n)
    for d, f in F_SCALE.items():
        A[d] = U @ (f * Vbase).T                                    # A^{(d)}_{ij} = f(d)<u_i, v_j>
    return dict(U=U, Vbase=Vbase, A=A, m=m, n=n, r=r, sigma=sigma)


def assign_mcar(D_prob, m, n, rng):
    """D_prob: dict treatment->prob (may include 0=unobserved). Returns D (m,n) int."""
    levels = sorted(D_prob.keys())
    p = np.array([D_prob[l] for l in levels])
    p = p / p.sum()
    flat = rng.choice(len(levels), size=m * n, p=p)
    D = levels[flat].reshape(m, n) if isinstance(levels, np.ndarray) else np.array(levels)[flat].reshape(m, n)
    return D.astype(int)


def assign_mnar(A, lam, m, n, rng, unobs_prob=0.115):
    """MNAR: P(D=d) ~ exp(lam * A^{(d)}) over observed treatments; plus unobserved mass."""
    # logits for each treatment
    logit = np.stack([lam * A[d] for d in F_SCALE], axis=0)         # (L,m,n)
    # add unobserved channel as a constant logit
    obs_levels = list(F_SCALE)
    logit_obs = logit
    # softmax over observed treatments
    logit_obs -= logit_obs.max(axis=0, keepdims=True)
    e = np.exp(logit_obs)
    p_obs = e / e.sum(axis=0)                                       # (L,m,n) sums to 1 over L
    u = rng.random((m, n))
    # with prob unobs_prob -> unobserved (D=0)
    mask_obs = u >= unobs_prob
    u2 = rng.random((m, n))
    cum = np.cumsum(p_obs, axis=0)
    chosen = (u2[None] < cum).argmax(axis=0)                        # (m,n) index into obs_levels
    D = np.zeros((m, n), dtype=int)
    D[mask_obs] = np.array(obs_levels)[chosen[mask_obs]]
    return D


def observe(D, A, sigma, rng):
    """Y[a,b] = A^{(D[a,b])}_{ab} + eps  (only where D!=0)."""
    m, n = D.shape
    Y = np.full((m, n), np.nan)
    for d in F_SCALE:
        sel = (D == d)
        Y[sel] = A[d][sel] + rng.standard_normal(sel.sum()) * sigma
    return Y


# --------------------------------------------------------------------------- #
#  Estimators
# --------------------------------------------------------------------------- #
def _trunc_svd_pinv(S, r):
    """Rank-r truncated-SVD pseudoinverse of S."""
    U, sv, Vt = np.linalg.svd(S, full_matrices=False)
    k = min(r, (sv > 1e-10).sum())
    if k == 0:
        return None
    return (Vt[:k].T * (1.0 / sv[:k])) @ U[:, :k].T


def snn_estimate(D, Y, i, j, d, r, thr=4):
    """Standard SNN for A_{ij}^{(d)}.

    AR(d)={a!=i: D[a,j]=d}, AC(d)={b!=j: D[i,b]=d}; anchor block S=Y[AR,AC] uses the
    OBSERVED values (mixed treatments -> scale-corrupted -> biased, high MRE, as the
    paper reports for SNN).  Feasible iff |AR|>=thr and |AC|>=thr (stable rank-r fit).
    """
    m, n = D.shape
    AR = np.where((D[:, j] == d) & (np.arange(m) != i))[0]
    AC = np.where((D[i, :] == d) & (np.arange(n) != j))[0]
    if len(AR) < thr or len(AC) < thr:
        return None, False
    # anchor block must be FULLY OBSERVED (no unobserved cells); filter cols accordingly
    Sraw = Y[np.ix_(AR, AC)]
    col_ok = ~np.isnan(Sraw).any(axis=0)
    AC = AC[col_ok]
    if len(AC) < thr:
        return None, False
    S = Y[np.ix_(AR, AC)]
    x = Y[AR, j]; q = Y[i, AC]
    if np.isnan(x).any() or np.isnan(q).any():
        return None, False
    P = _trunc_svd_pinv(S, r)
    if P is None:
        return None, False
    return float(x @ P.T @ q), True


def msnn_estimate(D, Y, A_scales, i, j, d, r, thr=6, row_cap=9):
    """Mixed SNN.  MAR(d)={a!=i: D[a,j]=d} (capped); MAC=cols b with D[i,b]=d(b)!=0
    consistent across MAR; block SCALE-NORMALISED by 1/f(d(b)) -> low MRE.
    Â = f(d) * x_norm^T (truncSVD^+ S_w) q_norm.  Feasible iff |MAR|>=thr, |MAC|>=thr."""
    m, n = D.shape
    MAR = np.where((D[:, j] == d) & (np.arange(m) != i))[0]
    if len(MAR) < thr:
        return None, False
    if len(MAR) > row_cap:
        MAR = MAR[:row_cap]
    Di = D[i, :]
    MAC = []; d_of_b = []
    for b in range(n):
        if b == j or Di[b] == 0:
            continue
        db = Di[b]
        if np.all(D[MAR, b] == db):
            MAC.append(b); d_of_b.append(db)
    if len(MAC) < thr:
        return None, False
    MAC = np.array(MAC); d_of_b = np.array(d_of_b)
    fb = np.array([A_scales[db] for db in d_of_b])
    S = Y[np.ix_(MAR, MAC)] / fb[None, :]                          # normalised to base scale
    x = Y[MAR, j] / A_scales[d]
    q = Y[i, MAC] / fb
    if np.isnan(S).any() or np.isnan(x).any() or np.isnan(q).any():
        return None, False
    P = _trunc_svd_pinv(S, r)
    if P is None:
        return None, False
    return A_scales[d] * float(x @ P.T @ q), True


# --------------------------------------------------------------------------- #
#  Experiment: feasible rate + MRE over many targets
# --------------------------------------------------------------------------- #
def evaluate(dgp, D, Y, p_label, estimator, r, n_targets=400, seed=0,
             d_target=None):
    """Sample target (i,j,d), estimate, measure feasible-rate and MRE over feasible."""
    rng = np.random.default_rng(seed)
    m, n = D.shape
    A = dgp["A"]
    feasible = 0; errs = []
    attempts = 0
    levels = [d_target] if d_target else list(F_SCALE)
    while feasible < n_targets // 2 and attempts < n_targets * 8:
        attempts += 1
        d = int(rng.choice(levels))
        i = int(rng.integers(m)); j = int(rng.integers(n))
        if estimator == "snn":
            est, ok = snn_estimate(D, Y, i, j, d, r)
        else:
            est, ok = msnn_estimate(D, Y, F_SCALE, i, j, d, r)
        if ok:
            feasible += 1
            truth = A[d][i, j]
            rel = abs(est - truth) / (abs(truth) + 1e-9)
            errs.append(rel)
    fr = feasible / attempts if attempts else 0.0
    mre = float(np.mean(errs)) if errs else float("nan")
    return fr * 100.0, mre, feasible, attempts
