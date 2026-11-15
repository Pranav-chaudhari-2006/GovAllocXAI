"""Fill missing volume / number / pages in papers/references.bib from Crossref (DOI lookup). Only adds fields that are missing; never overwrites.
Usage: python tools/enrich_references.py"""
import json
import pathlib
import re
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / "papers/references.bib"
bib = F.read_text(encoding="utf8")
report = []


def has(body, name):
    return re.search(r"\b" + name + r"\s*=", body) is not None


def fix(m):
    kind, key, body = m.group(1).lower(), m.group(2), m.group(3)
    mdoi = re.search(r"\bdoi\s*=\s*[{\"]([^}\"]+)[}\"]", body)
    if not mdoi or kind not in ("article", "inproceedings", "incollection"):
        return m.group(0)
    doi = mdoi.group(1)
    time.sleep(1.1)
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request("https://api.crossref.org/works/" + urllib.request.quote(doi), headers={"User-Agent": "GovAllocXAI-refcheck/1.0"}), timeout=30))["message"]
    except Exception as e:  # noqa: BLE001
        report.append((key, "lookup failed", str(e)[:40]))
        return m.group(0)
    add = []
    if kind == "article":
        if not has(body, "volume") and r.get("volume"):
            add.append(("volume", r["volume"]))
        if not has(body, "number") and r.get("issue"):
            add.append(("number", r["issue"]))
    if not has(body, "pages"):
        pg = r.get("page") or r.get("article-number")
        if pg:
            add.append(("pages", pg.replace("-", "--") if "-" in pg and "--" not in pg else pg))
    if not add:
        return m.group(0)
    report.append((key, "added", ", ".join(f"{k}={v}" for k, v in add)))
    base = m.group(0)[:-2].rstrip().rstrip(",")
    return base + "".join(f",\n  {k} = {{{v}}}" for k, v in add) + "\n}"


out = re.sub(r"@(\w+)\{([^,]+),(.*?)\n\}", fix, bib, flags=re.S)
F.write_text(out, encoding="utf8")
for r in report:
    print(r)
