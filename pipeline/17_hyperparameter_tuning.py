"""Exp M: nested grouped-CV hyper-parameter optimisation (Optuna TPE) for XGBoost and CatBoost, cold-start regime.
Outer: 6 leave-country-out folds (seed 0) -> honest TVD.  Inner (per outer training set): Optuna study, inner 3-fold grouped CV
on training economies, objective = mean TVD (simplex_renorm) over rows.  Default hyper-parameters (gov_common.make_model) are
enqueued as trial 0, so the tuned config is never worse than default on the inner CV.
Time-box: each study stops at MAX_TRIALS or TIMEOUT_S seconds, whichever first (settings recorded in the summary).
Outputs: results/13_hyperparameter_tuning/<panel>_outer.csv, 13_hyperparameter_tuning/<panel>_best_params.json, 13_hyperparameter_tuning/summary.json
Usage: python pipeline/17_hyperparameter_tuning.py [A10|A16|both] [max_trials] [timeout_s]
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
import tempfile
os.chdir(tempfile.gettempdir())   # catboost writes catboost_info into cwd; keep it out of the repo / unwritable dirs
import importlib.util
import json
import pathlib
import sys
import time

import numpy as np
import optuna
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gov_common import *  # noqa: F401,F403

optuna.logging.set_verbosity(optuna.logging.WARNING)
_spec = importlib.util.spec_from_file_location("arch03c", str(pathlib.Path(__file__).parent / "06_stack_architecture.py"))
A = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(A)

MAX_TRIALS = int(sys.argv[2]) if len(sys.argv) > 2 else 25
TIMEOUT_S = int(sys.argv[3]) if len(sys.argv) > 3 else 100
CAT_TRIALS = int(sys.argv[4]) if len(sys.argv) > 4 else 12   # CatBoost is ~4x slower per fit -> fewer trials
CAT_TIMEOUT_S = int(sys.argv[5]) if len(sys.argv) > 5 else 240

DEFAULTS = {
    "xgb": dict(n_estimators=300, learning_rate=0.05, max_depth=3, subsample=0.8, colsample_bytree=0.8, min_child_weight=3, reg_lambda=5.0),
    "cat": dict(iterations=300, learning_rate=0.07, depth=4, l2_leaf_reg=5.0),
}


def build(name, p, seed=42):
    if name == "xgb":
        from xgboost import XGBRegressor
        return XGBRegressor(**p, random_state=seed, n_jobs=1, verbosity=0)
    from catboost import CatBoostRegressor
    return CatBoostRegressor(**p, random_seed=seed, verbose=0, thread_count=1)


def fit_pred(name, p, Xtr, Ytr, Xte, seed=42):
    mu, sd = Ytr.mean(0), Ytr.std(0).replace(0, 1)
    Z = (Ytr - mu) / sd
    out = {}
    for c in Ytr.columns:
        m = build(name, p, seed); m.fit(Xtr, Z[c]); out[c] = m.predict(Xte)
    return (pd.DataFrame(out, index=Xte.index) * sd + mu).values


def suggest(name, tr):
    if name == "xgb":
        return dict(learning_rate=tr.suggest_float("learning_rate", 0.01, 0.2, log=True), max_depth=tr.suggest_int("max_depth", 2, 8),
                    n_estimators=tr.suggest_int("n_estimators", 100, 600, step=50), subsample=tr.suggest_float("subsample", 0.5, 1.0),
                    colsample_bytree=tr.suggest_float("colsample_bytree", 0.4, 1.0),
                    min_child_weight=tr.suggest_float("min_child_weight", 1, 20, log=True),
                    reg_lambda=tr.suggest_float("reg_lambda", 0.1, 50, log=True))
    return dict(depth=tr.suggest_int("depth", 3, 8), l2_leaf_reg=tr.suggest_float("l2_leaf_reg", 1, 30, log=True),
                learning_rate=tr.suggest_float("learning_rate", 0.02, 0.2, log=True), iterations=tr.suggest_int("iterations", 100, 500, step=50))


def tune(name, Xa, Ya, ga, seed):
    n_trials, timeout = (MAX_TRIALS, TIMEOUT_S) if name == "xgb" else (CAT_TRIALS, CAT_TIMEOUT_S)
    ctry = np.unique(ga); pm = np.random.default_rng(500 + seed).permutation(len(ctry))
    mp = {c: i % 3 for i, c in zip(range(len(ctry)), ctry[pm])}
    inner = np.array([mp[c] for c in ga])
    folds = [(np.where(inner != g)[0], np.where(inner == g)[0]) for g in range(3)]

    def objective(trial):
        p = suggest(name, trial)
        errs = []
        for ia, ib in folds:
            P = fit_pred(name, p, Xa.iloc[ia], Ya.iloc[ia], Xa.iloc[ib])
            errs.append(tvd(simplex_renorm(P), Ya.iloc[ib].values))
        return float(np.concatenate(errs).mean())

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    d0 = DEFAULTS[name]
    study.enqueue_trial(d0)
    study.optimize(objective, n_trials=n_trials, timeout=timeout)
    return study.best_params, study.best_value, len(study.trials), study.trials[0].value


def setup(kind):
    d, T = A.load_panel(kind)
    d = d.reset_index(drop=True)
    ctry = d.iso3.unique(); perm = np.random.default_rng(0).permutation(len(ctry))
    fold = d.iso3.map({c: i % 6 for i, c in zip(range(len(ctry)), ctry[perm])}).values
    return d, T, fold


def fold_job(kind, f):
    d, T, fold = setup(kind)
    X, Y = d[FEATURES], d[T]
    a, b = np.where(fold != f)[0], np.where(fold == f)[0]
    out = {"b": b, "oof": {}, "best": {}}
    t0 = time.time()
    for name in ("xgb", "cat"):
        bp, bv, nt, dv = tune(name, X.iloc[a], Y.iloc[a], d.iso3.values[a], f)
        full = {**DEFAULTS[name], **bp}
        out["oof"][f"{name}_default"] = fit_pred(name, DEFAULTS[name], X.iloc[a], Y.iloc[a], X.iloc[b])
        out["oof"][f"{name}_tuned"] = fit_pred(name, full, X.iloc[a], Y.iloc[a], X.iloc[b])
        out["best"][name] = {"outer_fold": f, "params": full, "inner_cv_TVD_tuned": bv, "inner_cv_TVD_default": dv, "n_trials": nt}
        print(kind, "fold", f, name, "trials", nt, "inner default %.3f tuned %.3f" % (dv, bv), "elapsed %.0fs" % (time.time() - t0), flush=True)
    return out


def run(kind):
    from concurrent.futures import ProcessPoolExecutor
    d, T, fold = setup(kind)
    Y = d[T]
    oof = {n: np.zeros((len(d), len(T))) for n in ["xgb_default", "xgb_tuned", "cat_default", "cat_tuned"]}
    best = {"xgb": [], "cat": []}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(fold_job, [kind] * 6, range(6)))
    for r in results:
        for n in oof:
            oof[n][r["b"]] = r["oof"][n]
        for name in best:
            best[name].append(r["best"][name])
    t = {n: tvd(simplex_renorm(oof[n]), Y.values) for n in oof}
    rows = []
    for n in oof:
        lo, hi = boot_ci(t[n], d.iso3.values)
        rows.append({"method": n, "TVD": float(t[n].mean()), "TVD_lo": lo, "TVD_hi": hi})
    R = pd.DataFrame(rows); R.to_csv(RES / f"13_hyperparameter_tuning/{kind}_outer.csv", index=False); print(R.round(3).to_string(), flush=True)
    paired = {}
    for name in ("xgb", "cat"):
        dd = t[f"{name}_default"] - t[f"{name}_tuned"]
        lo, hi = boot_ci(dd, d.iso3.values)
        paired[f"{name}_tuned_vs_default"] = {"mean_gain_pp": float(dd.mean()), "ci95": [lo, hi], "share_rows_improved": float((dd > 0).mean())}
    # per-fold gain, to show consistency
    fg = {name: [float((t[f"{name}_default"][fold == f] - t[f"{name}_tuned"][fold == f]).mean()) for f in range(6)] for name in ("xgb", "cat")}
    json.dump(best, open(RES / f"13_hyperparameter_tuning/{kind}_best_params.json", "w"), indent=1, default=float)
    return {"rows": R.to_dict("records"), "paired": paired, "per_fold_gain_pp": fg, "n": len(d), "economies": int(d.iso3.nunique()),
            "settings": {"xgb_max_trials": MAX_TRIALS, "xgb_timeout_s": TIMEOUT_S, "cat_max_trials": CAT_TRIALS, "cat_timeout_s": CAT_TIMEOUT_S, "inner_folds": 3, "outer_folds": 6, "seed": 0,
                         "runtime_s": time.time() - t0}}


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "A10"
    out = {}
    for kind in (["A10", "A16"] if which == "both" else [which]):
        out[kind] = run(kind)
        fn = RES / "13_hyperparameter_tuning/summary.json"
        old = json.load(open(fn)) if fn.exists() else {}
        old.update(out)
        json.dump(old, open(fn, "w"), indent=1, default=float)
    print("done")
