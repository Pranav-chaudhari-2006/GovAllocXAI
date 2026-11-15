#!/usr/bin/env python
"""
16_analyze_human_study.py -- analysis of the GovAllocXAI human-subject study.

Reads a CSV in the docs/study_materials/response_template.csv format (long
format: one row per participant x vignette) and computes, per condition
(A = recommendation only, B = + SHAP, C = + SHAP + LIME + applicability warning):

  * decision error  = TVD(participant split, actual official split), pre and post
  * improvement     = pre error - post error
  * reliance        = fraction of the pre->model gap closed by the participant
                      (clipped to [-1, 1]); appropriate reliance is high when the
                      model is right and low when it is wrong / extrapolating
  * trust calibration = reliance(correct) - reliance(incorrect)  (higher = better)
  * time, trust, SUS, NASA-TLX, quiz, confidence
  * one-way ANOVA and Kruskal-Wallis (+ eta^2 / epsilon^2), pairwise
    Mann-Whitney U with Holm correction (family = all pairwise tests over the
    pre-registered primary outcomes), optional mixed model if statsmodels exists.

Usage:
    python pipeline/16_analyze_human_study.py --data path/to/responses.csv
    python pipeline/16_analyze_human_study.py --selftest

--selftest generates SYNTHETIC dummy data in a temp folder to verify that the
pipeline runs. Synthetic output is NEVER a result and must never be reported.
"""
import argparse
import itertools
import json
import os
import sys
import tempfile

import numpy as np
import pandas as pd
from scipy import stats

try:
    import statsmodels.formula.api as smf  # optional
    HAVE_SM = True
except Exception:  # pragma: no cover
    HAVE_SM = False

SECTORS = ["health", "education", "defence", "other"]
CONDS = ["A", "B", "C"]
INCORRECT_TYPES = {"model_wrong", "extrapolation"}
PRIMARY = ["post_error", "improvement", "reliance_correct", "reliance_incorrect",
           "calibration", "time_seconds"]
SECONDARY = ["trust_mean", "sus_score", "tlx_mean", "quiz_score", "conf_post",
             "overreliance_extrap"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tvd(a, b):
    """Total variation distance between two shares vectors (rows)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a / a.sum(axis=1, keepdims=True)
    b = b / b.sum(axis=1, keepdims=True)
    return 0.5 * np.abs(a - b).sum(axis=1)


def holm(pvals):
    """Holm-Bonferroni adjusted p-values (same order as input)."""
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adj[idx] = min(1.0, running)
    return adj


def load(path):
    df = pd.read_csv(path)
    need = ["participant_id", "condition", "vignette_id", "vignette_type"]
    for pre in ("pre", "post", "model", "actual"):
        need += [f"{pre}_{s}" for s in SECTORS]
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise SystemExit(f"Missing columns: {miss}")
    df["condition"] = df["condition"].astype(str).str.strip().str.upper()
    return df


def trial_metrics(df):
    g = lambda p: df[[f"{p}_{s}" for s in SECTORS]].to_numpy(float)
    pre, post, model, actual = g("pre"), g("post"), g("model"), g("actual")
    df = df.copy()
    df["pre_error"] = tvd(pre, actual)
    df["post_error"] = tvd(post, actual)
    df["improvement"] = df["pre_error"] - df["post_error"]
    df["model_error"] = tvd(model, actual)
    gap_pre = tvd(pre, model)
    gap_post = tvd(post, model)
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.where(gap_pre > 0.01, (gap_pre - gap_post) / gap_pre, np.nan)
    df["reliance"] = np.clip(rel, -1, 1)
    df["model_incorrect"] = df["vignette_type"].isin(INCORRECT_TYPES)
    return df


def participant_table(trials):
    rows = []
    for pid, d in trials.groupby("participant_id"):
        cor = d[~d["model_incorrect"]]
        inc = d[d["model_incorrect"]]
        ext = d[d["vignette_type"] == "extrapolation"]
        r = {
            "participant_id": pid,
            "condition": d["condition"].iloc[0],
            "pre_error": d["pre_error"].mean(),
            "post_error": d["post_error"].mean(),
            "improvement": d["improvement"].mean(),
            "reliance_correct": cor["reliance"].mean(),
            "reliance_incorrect": inc["reliance"].mean(),
            "overreliance_extrap": ext["reliance"].mean(),
        }
        r["calibration"] = r["reliance_correct"] - r["reliance_incorrect"]
        for c in ["time_seconds", "conf_post"]:
            if c in d:
                r[c] = pd.to_numeric(d[c], errors="coerce").mean()
        for c in ["trust_mean", "sus_score", "tlx_mean", "quiz_score"]:
            if c in d:
                r[c] = pd.to_numeric(d[c], errors="coerce").iloc[0]
        rows.append(r)
    return pd.DataFrame(rows)


def clean(x):
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def omnibus(pt, var):
    groups = [pt.loc[pt.condition == c, var].dropna().to_numpy() for c in CONDS]
    groups = [g for g in groups if len(g) >= 2]
    out = {"n": {c: int(pt.loc[pt.condition == c, var].notna().sum()) for c in CONDS}}
    if len(groups) < 2:
        out["note"] = "fewer than two usable groups"
        return out
    if np.ptp(np.concatenate(groups)) == 0:
        out["note"] = "all values identical; tests undefined"
        return out
    F, pF = stats.f_oneway(*groups)
    H, pH = stats.kruskal(*groups)
    allv = np.concatenate(groups)
    N, k = len(allv), len(groups)
    ss_b = sum(len(g) * (g.mean() - allv.mean()) ** 2 for g in groups)
    ss_t = ((allv - allv.mean()) ** 2).sum()
    eta2 = ss_b / ss_t if ss_t > 0 else np.nan
    eps2 = H * (N + 1) / (N ** 2 - 1) if N > 1 else np.nan  # epsilon^2 (rank)
    out.update(anova_F=F, anova_p=pF, eta_sq=eta2, kruskal_H=H, kruskal_p=pH,
               epsilon_sq=eps2)
    pairs = []
    for a, b in itertools.combinations(CONDS, 2):
        x = pt.loc[pt.condition == a, var].dropna().to_numpy()
        y = pt.loc[pt.condition == b, var].dropna().to_numpy()
        if len(x) < 2 or len(y) < 2:
            continue
        U, p = stats.mannwhitneyu(x, y, alternative="two-sided")
        sp = np.sqrt(((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1))
                     / (len(x) + len(y) - 2))
        d = (x.mean() - y.mean()) / sp if sp > 0 else np.nan
        rbc = 1 - 2 * U / (len(x) * len(y))  # rank-biserial (sign: x vs y)
        pairs.append({"pair": f"{a}-{b}", "U": U, "p_raw": p, "cohens_d": d,
                      "rank_biserial": rbc})
    out["pairwise"] = pairs
    return out


def mixed_model(trials):
    if not HAVE_SM:
        return {"note": "statsmodels not installed; mixed model skipped"}
    d = trials.dropna(subset=["post_error"]).copy()
    try:
        m = smf.mixedlm("post_error ~ C(condition) + C(vignette_type)", d,
                        groups=d["participant_id"]).fit(reml=True)
        return {"formula": "post_error ~ C(condition) + C(vignette_type) + (1|participant)",
                "params": {k: clean(v) for k, v in m.params.items()},
                "pvalues": {k: clean(v) for k, v in m.pvalues.items()}}
    except Exception as e:  # pragma: no cover
        return {"note": f"mixed model failed: {e}"}


def analyse(path, out_json, synthetic=False):
    df = load(path)
    trials = trial_metrics(df)
    pt = participant_table(trials)
    summary = {"source": os.path.abspath(path),
               "SYNTHETIC_DATA_DO_NOT_REPORT": bool(synthetic),
               "n_participants": int(pt.participant_id.nunique()),
               "n_trials": int(len(trials)),
               "per_condition_means": {}, "tests": {}}
    for var in PRIMARY + SECONDARY + ["pre_error"]:
        if var in pt:
            summary["per_condition_means"][var] = {
                c: {"mean": clean(pt.loc[pt.condition == c, var].mean()),
                    "sd": clean(pt.loc[pt.condition == c, var].std(ddof=1)),
                    "n": int(pt.loc[pt.condition == c, var].notna().sum())}
                for c in CONDS}
    summary["per_condition_by_vignette_type"] = (
        trials.groupby(["condition", "vignette_type"])[["post_error", "reliance"]]
        .mean().round(4).reset_index().to_dict(orient="records"))
    for var in PRIMARY + SECONDARY:
        if var in pt:
            summary["tests"][var] = omnibus(pt, var)
    # Holm over all pairwise tests of the primary family
    fam = [(v, p) for v in PRIMARY if v in summary["tests"]
           for p in summary["tests"][v].get("pairwise", [])]
    if fam:
        adj = holm([p["p_raw"] for _, p in fam])
        for (_, p), a in zip(fam, adj):
            p["p_holm"] = a
    # Holm over omnibus Kruskal p-values of primary family
    om = [(v, summary["tests"][v]["kruskal_p"]) for v in PRIMARY
          if "kruskal_p" in summary["tests"].get(v, {})]
    if om:
        for (v, _), a in zip(om, holm([p for _, p in om])):
            summary["tests"][v]["kruskal_p_holm"] = a
    summary["mixed_model"] = mixed_model(trials)
    summary["notes"] = ("Holm family = primary outcomes " + ", ".join(PRIMARY) +
                        ". Secondary outcomes are exploratory (uncorrected).")
    os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=clean)
    print_summary(summary)
    print(f"\nWrote {out_json}")
    return summary


def print_summary(s):
    if s["SYNTHETIC_DATA_DO_NOT_REPORT"]:
        print("*** SYNTHETIC DUMMY DATA -- pipeline check only, NOT results ***")
    print(f"participants={s['n_participants']} trials={s['n_trials']}")
    for var, d in s["per_condition_means"].items():
        cells = "  ".join(f"{c}: {v['mean']:.3f}" if v["mean"] is not None else f"{c}: NA"
                          for c, v in d.items())
        print(f"{var:20s} {cells}")
    print("\nOmnibus tests (ANOVA p / Kruskal p / eta2 / eps2):")
    for var, t in s["tests"].items():
        if "anova_p" in t:
            print(f"{var:20s} {t['anova_p']:.4f} / {t['kruskal_p']:.4f} / "
                  f"{t['eta_sq']:.3f} / {t['epsilon_sq']:.3f}")
    print("\nMixed model:", s["mixed_model"].get("note", "fitted (see JSON)"))


def synthetic_data(path, n_per_cond=12, seed=0):
    """SYNTHETIC dummy data -- for pipeline testing only."""
    rng = np.random.default_rng(seed)
    types = ["normal", "normal", "normal", "model_wrong", "model_wrong", "extrapolation"]
    rows = []
    pid = 0
    for c in CONDS:
        for _ in range(n_per_cond):
            pid += 1
            trust, sus, tlx, quiz = (rng.normal(4, .6), rng.normal(65, 10),
                                     rng.normal(40, 10), rng.integers(2, 6))
            for v, t in enumerate(types, 1):
                actual = rng.dirichlet([8, 8, 6, 20])
                if t == "normal":
                    model = np.clip(actual + rng.normal(0, .01, 4), .01, None)
                else:
                    model = rng.dirichlet([8, 8, 6, 20])
                model = model / model.sum()
                pre = np.clip(actual + rng.normal(0, .05, 4), .01, None)
                pre /= pre.sum()
                w = {"A": .5, "B": .55, "C": .5}[c]
                if c == "C" and t in INCORRECT_TYPES:
                    w = .25
                post = (1 - w) * pre + w * model
                row = {"participant_id": f"SYN{pid:03d}", "condition": c,
                       "vignette_id": f"V{v}", "vignette_type": t}
                for p, vec in (("pre", pre), ("post", post), ("model", model),
                               ("actual", actual)):
                    for s, x in zip(SECTORS, vec):
                        row[f"{p}_{s}"] = round(float(x), 4)
                row.update(time_seconds=int(rng.normal(150, 30)), conf_pre=3, conf_post=4,
                           trust_mean=trust, sus_score=sus, tlx_mean=tlx, quiz_score=quiz)
                rows.append(row)
    pd.DataFrame(rows).to_csv(path, index=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", help="responses CSV (response_template format)")
    ap.add_argument("--out", default=os.path.join(ROOT, "results",
                                                  "08_shock_experiments/human_study_summary.json"))
    ap.add_argument("--selftest", action="store_true",
                    help="run on SYNTHETIC data in a temp folder (never reportable)")
    a = ap.parse_args()
    if a.selftest:
        with tempfile.TemporaryDirectory() as td:
            csv = os.path.join(td, "SYNTHETIC_responses.csv")
            synthetic_data(csv)
            analyse(csv, os.path.join(td, "SYNTHETIC_summary.json"), synthetic=True)
        print("Selftest OK (temp files removed).")
        return
    if not a.data:
        sys.exit("Provide --data <csv> or --selftest")
    analyse(a.data, a.out)


if __name__ == "__main__":
    main()
