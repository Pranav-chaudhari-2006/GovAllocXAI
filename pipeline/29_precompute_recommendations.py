"""Precompute the default recommendation (latest year, no shock, model-estimated budget) for every economy and both panels, as static JSON files.

The website loads these files from the CDN instantly (even on slow connections and while the free API server is asleep); only advanced options
(other year, stress test, own budget, LIME) need the live API.

Outputs: frontend/public/precomputed/economies.json, frontend/public/precomputed/{cofog16,cofog10}/<ISO3>.json
Run: python pipeline/29_precompute_recommendations.py   (about 5-10 minutes)
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.service import load_v2, recommend  # noqa: E402

OUT = ROOT / "frontend/public/precomputed"
OUT.mkdir(parents=True, exist_ok=True)
bundles = {"cofog16": load_v2("cofog16"), "cofog10": load_v2("cofog10")}
b16 = bundles["cofog16"]
g = b16.master.groupby(["iso3", "country"]).year.max().reset_index()
covered = set(b16.panel.iso3)
economies = [{"iso3": r.iso3, "country": r.country, "latest_feature_year": int(r.year), "has_official_cofog_history": r.iso3 in covered} for r in g.itertuples()]
(OUT / "economies.json").write_text(json.dumps(economies, separators=(",", ":")), encoding="utf8")
ok = {k: 0 for k in bundles}
bad = {k: [] for k in bundles}
for kind, b in bundles.items():
    (OUT / kind).mkdir(exist_ok=True)
    for e in economies:
        try:
            res = recommend(b, e["iso3"], None, {}, None, None, 5, None)
        except Exception as exc:  # noqa: BLE001
            bad[kind].append((e["iso3"], str(exc)[:60]))
            continue
        (OUT / kind / f"{e['iso3']}.json").write_text(json.dumps(res, separators=(",", ":"), default=float), encoding="utf8")
        ok[kind] += 1
    print(kind, "written", ok[kind], "failed", len(bad[kind]), flush=True)
json.dump({"written": ok, "failed": bad}, open(OUT / "_build_report.json", "w"), indent=1)
print("done")
