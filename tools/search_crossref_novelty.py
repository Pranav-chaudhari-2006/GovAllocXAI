"""Proxy novelty search on Crossref (keyless, open): runs the topical queries behind docs/07 and writes docs/audits/crossref_proxy_search.md.
Crossref is NOT Scopus/Web of Science: coverage differs (no abstracts-based keyword index, no subject filters), so this is a screening aid only.
"""
import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUERIES = [
    "machine learning government budget allocation functions",
    "COFOG expenditure forecasting machine learning",
    "public expenditure by function prediction neural network",
    "government expenditure composition shares compositional data",
    "explainable artificial intelligence public budget",
    "SHAP government spending prediction countries",
    "budget allocation decision support system explainable",
    "cross-country sectoral public spending prediction health education defence",
    "gradient boosting public expenditure forecasting",
    "artificial intelligence budgeting public sector resource allocation",
    "sustainable development goals budget allocation machine learning",
    "LIME SHAP agreement tabular economic data",
]
out = ["# Crossref proxy search (15 Nov 2026) — screening aid, NOT Scopus / Web of Science", "",
       "Run by `tools/search_crossref_novelty.py` (re-runnable). Crossref returns relevance-ranked records from 2015 onward; titles only (abstracts mostly unavailable), so every hit must still be screened by a human. Citation counts are Crossref's (`is-referenced-by`).", ""]
seen = {}
for q in QUERIES:
    rows = []
    for attempt in range(3):
        try:
            r = requests.get("https://api.crossref.org/works", params={"query.bibliographic": q, "filter": "from-pub-date:2015-01-01,type:journal-article", "rows": 10,
                                                                        "select": "title,issued,container-title,DOI,is-referenced-by-count"}, timeout=60)
            rows = r.json()["message"]["items"]
            break
        except Exception:  # noqa: BLE001
            time.sleep(3)
    out += [f"## Query: `{q}`", "", "| Year | Title | Venue | Cites | DOI |", "|---|---|---|---|---|"]
    for w in rows:
        t = (w.get("title") or [""])[0].replace("|", "/")[:110]
        y = (w.get("issued", {}).get("date-parts") or [[None]])[0][0]
        v = ((w.get("container-title") or [""])[0])[:40].replace("|", "/")
        out.append(f"| {y} | {t} | {v} | {w.get('is-referenced-by-count', 0)} | {w.get('DOI', '')} |")
        seen.setdefault(w.get("DOI"), (y, t, v))
    out.append("")
out += ["## How to use", "Screen the titles above for anything that predicts the composition of government expenditure by function across countries AND evaluates explanations. Add any new close work to `docs/07_Novelty_Search_Report.md` and `papers/references.bib` only after reading it.", f"Unique records returned: {len(seen)}"]
(ROOT / "docs/audits/crossref_proxy_search.md").write_text("\n".join(out), encoding="utf-8")
print("written", len(seen))
