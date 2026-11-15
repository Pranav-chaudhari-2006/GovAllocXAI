"""Multi-year projection (expI): rolling-origin evaluation, horizons h=1..5, origins T=2012..2019 (train only on year<=T).

Methods
  persistence      : share at T
  recursive_oracle : one-step Delta-xgb (FEATURES + lag share) applied h times, each step using the TRUE macros of that future year
                     (optimistic: assumes perfect macro forecasts)
  recursive_frozen : same but macros held at their year-T values (what a user without macro forecasts would do)
  direct           : separate Delta-xgb per horizon, features at T (FEATURES + share at T) -> share_{T+h} - share_T
Eval sample (same for all methods): economies observed in every year T..T+h. Metric: TVD (pp), cluster bootstrap by iso3, pooled over origins.
Outputs: results/09_multi_year_projection/multiyear_<panel>.csv, results/09_multi_year_projection/multiyear_<panel>_byorigin.csv, results/09_multi_year_projection/summary.json
Usage: python pipeline/13_multi_year_projection.py [A16|A10|both]
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

ORIGINS = list(range(2012, 2020))
HORIZONS = [1, 2, 3, 4, 5]
METHODS = ["persistence", "recursive_oracle", "recursive_frozen", "direct"]


def load(kind):
    if kind == "A16":
        d = load_cofog(); T = TARGETS_A
    else:
        d = pd.read_csv(PROC / "govalloc_cofog_panel_a10.csv")
        T = [f"cofog10_GF{i:02d}_pct_total" for i in range(1, 11)]
    d = d.sort_values(["iso3", "year"]).reset_index(drop=True)
    d = d.dropna(subset=T).reset_index(drop=True)
    return d, T


class DeltaModel:
    """Per-target standardised xgb on Delta; keeps fitted models so it can be applied repeatedly."""
    def __init__(self, X, D, seed=42):
        self.cols = list(X.columns)
        self.mu, self.sd = D.mean(0), D.std(0).replace(0, 1)
        Z = (D - self.mu) / self.sd
        self.models = {}
        for c in D.columns:
            m = make_model("xgb", seed); m.set_params(n_jobs=1); m.fit(X, Z[c]); self.models[c] = m   # n_jobs=1: avoids thread oversubscription on a shared CPU

    def predict(self, X):
        P = np.column_stack([self.models[c].predict(X[self.cols]) for c in self.mu.index])
        return P * self.sd.values + self.mu.values


def pair_frame(d, T, h):
    """Rows (iso3, t) with features at t and shares at t and t+h (if year t+h exists for that country)."""
    f = d[["iso3", "year"] + FEATURES + T]
    fut = d[["iso3", "year"] + T].copy(); fut["year"] = fut["year"] - h
    m = f.merge(fut, on=["iso3", "year"], suffixes=("", "_fut"))
    return m


def run_panel(kind):
    d, T = load(kind)
    idx = d.set_index(["iso3", "year"])
    byorig, recs = [], []
    for Tyr in ORIGINS:
        tr_all = d[d.year <= Tyr]
        # ---- one-step model (target year <= Tyr)
        # the one-step model uses macros of the TARGET year (as the 03c delta model: features of year t, lag share of year t-1)
        nxt = tr_all[["iso3", "year"] + FEATURES].copy()
        lagm = tr_all[["iso3", "year"] + T].copy(); lagm["year"] = lagm["year"] + 1
        tr1 = nxt.merge(lagm, on=["iso3", "year"], suffixes=("", "_lag")).merge(tr_all[["iso3", "year"] + T], on=["iso3", "year"], suffixes=("_lag", ""))
        lagc = [f"{t}_lag" for t in T]
        X1 = tr1[FEATURES + lagc]
        D1 = pd.DataFrame(tr1[T].values - tr1[lagc].values, columns=T, index=tr1.index)
        m1 = DeltaModel(X1, D1)
        # ---- direct models
        direct = {}
        for h in HORIZONS:
            pf = pair_frame(tr_all, T, h)
            if len(pf) < 100:
                continue
            Xh = pf[FEATURES + T]
            Dh = pd.DataFrame(pf[[f"{t}_fut" for t in T]].values - pf[T].values, columns=T, index=pf.index)
            direct[h] = DeltaModel(Xh, Dh)
        # ---- evaluation entities: economies with rows at Tyr
        base = d[d.year == Tyr].set_index("iso3")
        for h in HORIZONS:
            ents = [c for c in base.index if all((c, Tyr + s) in idx.index for s in range(1, h + 1))]
            if not ents or h not in direct:
                continue
            S0 = base.loc[ents, T].values
            actual = np.vstack([idx.loc[(c, Tyr + h), T].values for c in ents]).astype(float)
            out = {"persistence": S0}
            for scen in ["oracle", "frozen"]:
                S = S0.copy()
                for s in range(1, h + 1):
                    if scen == "oracle":
                        mac = pd.DataFrame([idx.loc[(c, Tyr + s), FEATURES].values for c in ents], columns=FEATURES).astype(float)
                    else:
                        mac = base.loc[ents, FEATURES].reset_index(drop=True).astype(float)
                    X = pd.concat([mac, pd.DataFrame(S, columns=lagc)], axis=1)
                    S = simplex_renorm(S + m1.predict(X))
                out[f"recursive_{scen}"] = S
            Xd = pd.concat([base.loc[ents, FEATURES].reset_index(drop=True).astype(float), pd.DataFrame(S0, columns=T)], axis=1)
            out["direct"] = S0 + direct[h].predict(Xd)
            for m in METHODS:
                t = tvd(simplex_renorm(out[m]), actual)
                for c, v in zip(ents, t):
                    recs.append({"panel": kind, "origin": Tyr, "h": h, "iso3": c, "method": m, "tvd": float(v)})
        print(kind, "origin", Tyr, "done", flush=True)
    R = pd.DataFrame(recs)
    byo = R.groupby(["panel", "origin", "h", "method"]).tvd.agg(["mean", "count"]).reset_index().rename(columns={"mean": "TVD", "count": "n"})
    byo.to_csv(RES / f"09_multi_year_projection/multiyear_{kind}_byorigin.csv", index=False)
    rows = []
    for h in HORIZONS:
        sub = R[R.h == h]
        if sub.empty:
            continue
        piv = sub.pivot_table(index=["origin", "iso3"], columns="method", values="tvd").reset_index()
        g = piv.iso3.values
        for m in METHODS:
            lo, hi = boot_ci(piv[m].values, g)
            r = {"panel": kind, "h": h, "method": m, "n": len(piv), "n_economies": int(piv.iso3.nunique()), "TVD": float(piv[m].mean()), "TVD_lo": lo, "TVD_hi": hi}
            if m != "persistence":
                gain = (piv["persistence"] - piv[m]).values
                glo, ghi = boot_ci(gain, g)
                r.update({"gain_vs_persistence": float(gain.mean()), "gain_lo": glo, "gain_hi": ghi, "beats_persistence_significantly": bool(glo > 0),
                          "share_rows_improved": float((gain > 0).mean())})
            rows.append(r)
    O = pd.DataFrame(rows); O.to_csv(RES / f"09_multi_year_projection/multiyear_{kind}.csv", index=False)
    print(O.round(3).to_string(), flush=True)
    verdict = {}
    for h in HORIZONS:
        s = O[(O.h == h) & (O.method != "persistence")]
        if s.empty:
            continue
        pers = float(O[(O.h == h) & (O.method == "persistence")].TVD.iloc[0])
        best = s.sort_values("TVD").iloc[0]
        verdict[f"h{h}"] = {"persistence_TVD": pers, "best_method": best.method, "best_TVD": float(best.TVD),
                            "best_gain_vs_persistence": float(best.gain_vs_persistence), "gain_ci95": [float(best.gain_lo), float(best.gain_hi)],
                            "any_method_significantly_beats_persistence": bool(s.beats_persistence_significantly.any()),
                            "methods_significantly_beating": s[s.beats_persistence_significantly].method.tolist()}
    return {"rows": rows, "verdict_by_horizon": verdict, "origins": ORIGINS, "note": "oracle = true future macros (optimistic); frozen = macros held at year-T values"}


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    out = {}
    for kind in (["A16", "A10"] if which == "both" else [which]):
        out[kind] = run_panel(kind)
    fn = RES / "09_multi_year_projection/summary.json"
    old = json.load(open(fn)) if fn.exists() else {}
    old.update(out)
    json.dump(old, open(fn, "w"), indent=1, default=float)
    print("done")
