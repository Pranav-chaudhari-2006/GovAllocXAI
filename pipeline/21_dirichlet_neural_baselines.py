"""Missing model families (reviewer concern): Dirichlet regression, log-ratio Gaussian ridge, neural tabular (MLP, small FT-Transformer).
Protocols identical to the main study:
  COLD   : leave-country-out, 6 folds, seeds 0 and 1 (fold assignment copied from 06_stack_architecture.run_cold); baselines peer_mean, xgb_raw.
  ANNUAL : train <=2019 (rows with lag), test 2020-24, one-step; lag share is an input; baseline persistence (+xgb delta).
Cluster-bootstrap CIs over countries (gov_common.boot_ci); paired gains vs peer_mean (cold) / persistence (annual) and vs xgb.
Neural nets: standardised features, early stopping on an inner validation split of TRAINING ECONOMIES; 5-seed ensembles (FT: 3).
Outputs results/16_dirichlet_neural_baselines/cold_<panel>.csv, 16_dirichlet_neural_baselines/annual_<panel>.csv, 16_dirichlet_neural_baselines/summary.json.  Usage: python pipeline/21_dirichlet_neural_baselines.py [A16|A10|both]
"""
import importlib.util
import json
import os
import pathlib
import sys
import time

os.environ["OMP_NUM_THREADS"] = "4"
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

torch.set_num_threads(4)
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from gov_common import *  # noqa: F401,F403

spec = importlib.util.spec_from_file_location("arch21", HERE / "06_stack_architecture.py")
arch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arch)
clr, inv_clr = arch.clr, arch.inv_clr
T0 = time.time()
LO = 1e-3


def comp(Y):
    """shares (0-100) -> clipped composition on the simplex (sum 1), strictly positive."""
    P = np.clip(np.asarray(Y, float), LO, 100.0)
    return P / P.sum(1, keepdims=True)


def prep(Xtr, Xte, extra_tr=None, extra_te=None):
    imp = SimpleImputer(strategy="median").fit(Xtr)
    sc = StandardScaler().fit(imp.transform(Xtr))
    A, B = sc.transform(imp.transform(Xtr)), sc.transform(imp.transform(Xte))
    if extra_tr is not None:  # lag log-shares (already centred); standardise too
        s2 = StandardScaler().fit(extra_tr)
        A, B = np.hstack([A, s2.transform(extra_tr)]), np.hstack([B, s2.transform(extra_te)])
    return A.astype(np.float32), B.astype(np.float32)


def split_inner(groups, seed, frac=0.2):
    u = np.unique(groups)
    rng = np.random.default_rng(1000 + seed)
    val = set(rng.choice(u, max(2, int(round(frac * len(u)))), replace=False))
    m = np.array([g in val for g in groups])
    return ~m, m


# ----------------------------- Dirichlet regression -----------------------------
def dir_nll(logalpha, y):
    a = torch.exp(logalpha.clamp(-10, 12))
    return -(torch.lgamma(a.sum(1)) - torch.lgamma(a).sum(1) + ((a - 1) * torch.log(y)).sum(1)).mean()


def fit_dirichlet(A, Y, lam, base=None, steps=200):
    """alpha_k = exp(w_k.x + b_k) (+ base_k log-mean offset for the 'resid' variant: alpha = exp(b0 + log m_k(lag)) with
    m = base composition, precision exp(b0 + w.x)). Returns predict(B, base_te)."""
    X, y = torch.tensor(A), torch.tensor(comp(Y), dtype=torch.float32)
    K, p = y.shape[1], X.shape[1]
    mean = y.mean(0)
    W = torch.zeros(p, K, requires_grad=True)
    b = torch.log(mean * 10).clone().requires_grad_(True)
    if base is not None:
        Wp = torch.zeros(p, 1, requires_grad=True)
        bp = torch.tensor([2.5], requires_grad=True)
        Bt = torch.tensor(base, dtype=torch.float32)
        gw = torch.tensor([0.5], requires_grad=True)  # mixture of persistence vs mean in the mean-structure (logit space)
    params = [W, b] + ([Wp, bp, gw] if base is not None else [])
    opt = torch.optim.LBFGS(params, lr=0.5, max_iter=steps, line_search_fn="strong_wolfe")

    def alpha(X_, Bt_=None):
        if base is None:
            return X_ @ W + b
        # mean = softmax(log base + (X W))  ; precision = exp(bp + X Wp)
        logit = torch.log(Bt_) * (1.0 + gw) + X_ @ W
        mu = torch.softmax(logit, 1)
        phi = torch.exp((bp + X_ @ Wp).clamp(-2, 9))
        return torch.log(mu * phi + 1e-8)

    def closure():
        opt.zero_grad()
        loss = dir_nll(alpha(X, Bt if base is not None else None), y) + lam * sum((q ** 2).sum() for q in ([W] + ([Wp] if base is not None else [])))
        loss.backward()
        return loss

    opt.step(closure)

    def predict(B, base_te=None):
        with torch.no_grad():
            a = torch.exp(alpha(torch.tensor(B), torch.tensor(base_te, dtype=torch.float32) if base_te is not None else None).clamp(-10, 12))
            return (a / a.sum(1, keepdim=True)).numpy() * 100
    return predict


def dirichlet_model(Xtr, Ytr, Xte, groups, seed, base_tr=None, base_te=None):
    """choose L2 on an inner holdout of training economies by Dirichlet NLL-proxy (TVD), refit on all training rows."""
    tr_i, va_i = split_inner(groups, seed)
    best, bl = 1e9, None
    for lam in [1e-3, 1e-2, 1e-1, 1.0]:
        pr = fit_dirichlet(Xtr[tr_i], Ytr[tr_i], lam, None if base_tr is None else comp(base_tr[tr_i]))
        e = tvd(pr(Xtr[va_i], None if base_tr is None else comp(base_tr[va_i])), Ytr[va_i]).mean()
        if e < best:
            best, bl = e, lam
    pr = fit_dirichlet(Xtr, Ytr, bl, None if base_tr is None else comp(base_tr))
    return pr(Xte, None if base_te is None else comp(base_te)), bl


def clr_ridge_model(Xtr, Ytr, Xte, groups, seed, base_tr=None, base_te=None):
    """Gaussian ridge on CLR (log-ratio) space; with base given, regresses the CLR delta from persistence."""
    tr_i, va_i = split_inner(groups, seed)
    Z = clr(Ytr) - (0 if base_tr is None else clr(base_tr))
    best, ba = 1e9, 10.0
    for a in [0.3, 3, 30, 300, 3000]:
        m = Ridge(alpha=a).fit(Xtr[tr_i], Z[tr_i])
        pv = inv_clr(m.predict(Xtr[va_i]) + (0 if base_tr is None else clr(base_tr[va_i])))
        e = tvd(pv, Ytr[va_i]).mean()
        if e < best:
            best, ba = e, a
    m = Ridge(alpha=ba).fit(Xtr, Z)
    return inv_clr(m.predict(Xte) + (0 if base_te is None else clr(base_te))), ba


# ----------------------------- neural tabular -----------------------------
class MLP(nn.Module):
    def __init__(self, p, K, h=(128, 64), drop=0.2, resid=False):
        super().__init__()
        L, d = [], p
        for w in h:
            L += [nn.Linear(d, w), nn.BatchNorm1d(w), nn.ReLU(), nn.Dropout(drop)]
            d = w
        self.net, self.out, self.resid = nn.Sequential(*L), nn.Linear(d, K), resid
        if resid:
            nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)

    def forward(self, x, base=None):
        z = self.out(self.net(x))
        if self.resid:
            z = z + torch.log(base)
        return torch.log_softmax(z, 1)


class FTT(nn.Module):
    """Small FT-Transformer (Gorishniy et al. 2021 style): per-feature linear tokenizer + [CLS], 2 pre-norm blocks, d=16, 2 heads."""
    def __init__(self, p, K, d=16, layers=2, heads=2, drop=0.1):
        super().__init__()
        self.W, self.b = nn.Parameter(torch.randn(p, d) * 0.1), nn.Parameter(torch.zeros(p, d))
        self.cls = nn.Parameter(torch.zeros(1, 1, d))
        enc = nn.TransformerEncoderLayer(d, heads, 2 * d, drop, batch_first=True, norm_first=True, activation="gelu")
        self.tr = nn.TransformerEncoder(enc, layers)
        self.head = nn.Sequential(nn.LayerNorm(d), nn.ReLU(), nn.Linear(d, K))

    def forward(self, x, base=None):
        tok = x.unsqueeze(-1) * self.W + self.b
        h = self.tr(torch.cat([self.cls.expand(len(x), -1, -1), tok], 1))
        return torch.log_softmax(self.head(h[:, 0]), 1)


def train_net(kind, A, Y, groups, seed, base=None, epochs=300, patience=30):
    torch.manual_seed(seed)
    tr_i, va_i = split_inner(groups, seed)
    y = torch.tensor(comp(Y), dtype=torch.float32)
    X = torch.tensor(A)
    Bt = None if base is None else torch.tensor(comp(base), dtype=torch.float32)
    K, p = y.shape[1], X.shape[1]
    net = MLP(p, K, resid=base is not None) if kind == "mlp" else FTT(p, K)
    opt = torch.optim.AdamW(net.parameters(), lr=3e-3 if kind == "mlp" else 2e-3, weight_decay=1e-2)
    ti, vi = np.where(tr_i)[0], np.where(va_i)[0]
    bs = 64

    def kl(lp, yy):
        return (yy * (torch.log(yy) - lp)).sum(1).mean()

    best, bstate, bad = 1e9, None, 0
    for ep in range(epochs):
        net.train()
        perm = np.random.default_rng(seed * 997 + ep).permutation(ti)
        for i in range(0, len(perm), bs):
            idx = perm[i:i + bs]
            if len(idx) < 2:
                continue
            opt.zero_grad()
            loss = kl(net(X[idx], None if Bt is None else Bt[idx]), y[idx])
            loss.backward(); opt.step()
        net.eval()
        with torch.no_grad():
            v = (0.5 * (torch.exp(net(X[vi], None if Bt is None else Bt[vi])) - y[vi]).abs().sum(1)).mean().item() * 100
        if v < best - 1e-4:
            best, bad = v, 0
            bstate = {k: t.clone() for k, t in net.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    net.load_state_dict(bstate); net.eval()

    def predict(B, base_te=None):
        with torch.no_grad():
            return torch.exp(net(torch.tensor(B), None if base_te is None else torch.tensor(comp(base_te), dtype=torch.float32))).numpy() * 100
    return predict


def net_model(kind, Xtr, Ytr, Xte, groups, nseed, base_tr=None, base_te=None):
    P = 0
    for s in range(nseed):
        P = P + train_net(kind, Xtr, Ytr, groups, s, base_tr)(Xte, base_te)
    return P / nseed


# ----------------------------- evaluation helpers -----------------------------
def evaluate(P, Y, groups):
    t = tvd(simplex_renorm(np.asarray(P)), Y)
    lo, hi = boot_ci(t, groups)
    return t, lo, hi


def run_cold(kind, use_ft):
    d, T = arch.load_panel(kind)
    d = d.reset_index(drop=True)
    X, Y = d[FEATURES], d[T].values
    names = ["peer_mean", "xgb_raw", "dirichlet", "clr_ridge", "mlp", "ft_transformer"]
    rows, per = [], {}
    for seed in [0, 1]:
        ctry = d.iso3.unique(); perm = np.random.default_rng(seed).permutation(len(ctry))
        fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
        oof = {n: np.zeros((len(d), len(T))) for n in names}
        for f in range(6):
            a, b = np.where(fold != f)[0], np.where(fold == f)[0]
            tr, te = d.iloc[a], d.iloc[b]
            oof["peer_mean"][b] = np.vstack([tr.groupby("income_group")[T].mean().reindex([g]).fillna(tr[T].mean()).values[0] for g in te.income_group])
            oof["xgb_raw"][b] = fit_predict_multi("xgb", X.iloc[a], pd.DataFrame(Y[a], columns=T, index=tr.index), X.iloc[b], 42 + seed).values
            A, B = prep(X.iloc[a], X.iloc[b])
            g = tr.iso3.values
            oof["dirichlet"][b], lam = dirichlet_model(A, Y[a], B, g, seed)
            oof["clr_ridge"][b], al = clr_ridge_model(A, Y[a], B, g, seed)
            oof["mlp"][b] = net_model("mlp", A, Y[a], B, g, 5)
            if use_ft:
                oof["ft_transformer"][b] = net_model("ft", A, Y[a], B, g, 3)
            print(f"[{time.time()-T0:.0f}s] {kind} cold seed {seed} fold {f} lam={lam} ridge_a={al}", flush=True)
        for n in names:
            if n == "ft_transformer" and not use_ft:
                continue
            t, lo, hi = evaluate(oof[n], Y, d.iso3.values)
            rows.append({"method": n, "seed": seed, "TVD": float(t.mean()), "TVD_lo": lo, "TVD_hi": hi})
            per[(n, seed)] = t
    R = pd.DataFrame(rows)
    out = R.groupby("method").mean(numeric_only=True).drop(columns="seed").reset_index()
    pairs = []
    for n in out.method:
        # paired gains averaged over the two seeds (per-row differences averaged across seeds, then cluster bootstrap)
        for ref in ["peer_mean", "xgb_raw"]:
            if n == ref:
                continue
            dd = np.mean([per[(ref, s)] - per[(n, s)] for s in [0, 1]], axis=0)
            lo, hi = boot_ci(dd, d.iso3.values)
            pairs.append((n, ref, float(dd.mean()), lo, hi))
    for ref in ["peer_mean", "xgb_raw"]:
        out[f"gain_vs_{ref}"] = [np.nan if n == ref else [p for p in pairs if p[0] == n and p[1] == ref][0][2] for n in out.method]
        out[f"gain_vs_{ref}_lo"] = [np.nan if n == ref else [p for p in pairs if p[0] == n and p[1] == ref][0][3] for n in out.method]
        out[f"gain_vs_{ref}_hi"] = [np.nan if n == ref else [p for p in pairs if p[0] == n and p[1] == ref][0][4] for n in out.method]
    out["n"], out["n_economies"] = len(d), d.iso3.nunique()
    out = out.sort_values("TVD")
    out.to_csv(RES / f"16_dirichlet_neural_baselines/cold_{kind}.csv", index=False)
    print(out.round(3).to_string(), flush=True)
    return out.to_dict("records")


def run_annual(kind, use_ft):
    d, T = arch.load_panel(kind)
    d = d.reset_index(drop=True)
    ok = d.has_lag
    tr, te = d[ok & (d.year <= 2019)], d[ok & (d.year >= 2020)]
    L = [f"h1_{t}" for t in T]
    ytr, yte = tr[T].values, te[T].values
    pers_tr, pers_te = tr[L].values, te[L].values
    g = tr.iso3.values
    A, B = prep(tr[FEATURES], te[FEATURES], clr(pers_tr), clr(pers_te))   # features + lag CLR log-share
    rows = []
    base_t = tvd(simplex_renorm(pers_te), yte)

    def add(name, P):
        t, lo, hi = evaluate(P, yte, te.iso3.values)
        dlo, dhi = boot_ci(base_t - t, te.iso3.values)
        rows.append({"method": name, "TVD": float(t.mean()), "TVD_lo": lo, "TVD_hi": hi, "gain_vs_persistence": float((base_t - t).mean()),
                     "gain_lo": dlo, "gain_hi": dhi, "n": len(te), "n_economies": int(te.iso3.nunique()), "_t": t})

    add("persistence", pers_te)
    Xa = FEATURES + L
    Dx = fit_predict_multi("xgb", tr[Xa], pd.DataFrame(ytr - pers_tr, columns=T, index=tr.index), te[Xa]).values
    add("xgb_delta (v2)", pers_te + Dx)
    add("dirichlet_direct (lag as feature)", dirichlet_model(A, ytr, B, g, 0)[0])
    add("dirichlet_persistence_centred", dirichlet_model(A, ytr, B, g, 0, pers_tr, pers_te)[0])
    add("clr_ridge_direct", clr_ridge_model(A, ytr, B, g, 0)[0])
    add("clr_ridge_delta", clr_ridge_model(A, ytr, B, g, 0, pers_tr, pers_te)[0])
    add("mlp_direct", net_model("mlp", A, ytr, B, g, 5))
    print(f"[{time.time()-T0:.0f}s] {kind} annual mlp_direct done", flush=True)
    add("mlp_residual_on_persistence", net_model("mlp", A, ytr, B, g, 5, pers_tr, pers_te))
    if use_ft:
        add("ft_transformer_direct", net_model("ft", A, ytr, B, g, 3))
    xt = [r for r in rows if r["method"].startswith("xgb_delta")][0]["_t"]
    for r in rows:   # paired gain vs the xgb_delta learner
        dd = xt - r["_t"]
        r["gain_vs_xgb_delta"] = float(dd.mean())
        r["gain_vs_xgb_delta_lo"], r["gain_vs_xgb_delta_hi"] = boot_ci(dd, te.iso3.values)
    R = pd.DataFrame([{k: v for k, v in r.items() if k != "_t"} for r in rows])
    R.to_csv(RES / f"16_dirichlet_neural_baselines/annual_{kind}.csv", index=False)
    print(R.round(3).to_string(), flush=True)
    return R.to_dict("records")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    use_ft = os.environ.get("NO_FT") is None
    summ = {}
    for kind in (["A16", "A10"] if which == "both" else [which]):
        summ[kind] = {"cold": run_cold(kind, use_ft), "annual": run_annual(kind, use_ft)}
        json.dump(summ, open(RES / "16_dirichlet_neural_baselines/summary.json", "w"), indent=1, default=float)
    print("done", f"{time.time()-T0:.0f}s")
