"""Build release/kaggle_upload/: the files to drag into a new Kaggle dataset, plus release/kaggle_description.md (paste into the description box).
Run: python tools/build_kaggle_package.py"""
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "release/kaggle_upload"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
for f in sorted((ROOT / "data/dataset_new").glob("govalloc_cofog_*")):
    shutil.copy2(f, OUT / f.name)
shutil.copy2(ROOT / "docs/guides/04_dataset_card.md", OUT / "DATASET_CARD.md")
shutil.copy2(ROOT / "release/GovAlloc-COFOG_v1.0/SOURCES_AND_LICENCES.txt", OUT / "SOURCES_AND_LICENCES.txt")

DOI_ALL, DOI_V1 = "10.5281/zenodo.24248315", "10.5281/zenodo.24248316"
DESC = f"""# GovAlloc-COFOG v1.0

**Harmonised general-government expenditure by function (COFOG) for up to 217 economies, 2000-2024**, with socio-economic and governance indicators, provenance flags and imputation flags.

**Permanent archive (cite this):** https://doi.org/{DOI_ALL} (all versions) · version 1.0: https://doi.org/{DOI_V1}
**Code, papers and web tool:** https://github.com/Pranav-chaudhari-2006/GovAllocXAI

## What is inside
| File | What it is |
|---|---|
| `govalloc_cofog_master.csv` | All economies x 2000-2024: features, every target series, flags |
| `govalloc_cofog_panel_a16.csv` | **Panel A16:** 825 complete country-years, 36 economies, **16 COFOG functions** (Eurostat, OECD) |
| `govalloc_cofog_panel_a10.csv` | **Panel A10:** 1,526 country-years, 85 economies, **10 COFOG divisions** (adds IMF) |
| `govalloc_cofog_panel_a10x.csv` | A10 plus flagged relaxed-consistency rows for lower-income economies (exploratory) |
| `govalloc_cofog_panel_wdi.csv` | **Panel B:** official World Bank sector series (health, education, defence, R&D), 211 economies |
| `govalloc_cofog_institutional_*.csv` | Governance, fiscal-rule, election and IMF-programme indicators (optional ablations) |
| `govalloc_cofog_data_quality.json` | Counts and cross-source agreement statistics |
| `DATASET_CARD.md`, `SOURCES_AND_LICENCES.txt` | Full description, column dictionary summary, providers and terms |

## Key properties
* **Targets are official published statistics and are never imputed.**
* **Imputed feature values are flagged cell by cell** (columns starting with `imp_`).
* Shares are percentages of total general-government expenditure and **sum to 100** in each row.
* The data are **executed (outturn) spending, not planned budgets.**

## Good uses
Benchmarking models that predict budget composition, public-finance research, explainability studies. **Tips:** split by country or by time (never randomly across years of the same country); compare with the simple baseline "same split as last year", which is very hard to beat.

## Not included
The original **semi-synthetic** dataset of our earlier study (it must not be used for modelling) is available only in the Zenodo archive, in a clearly marked `legacy` folder.

## Licence and sources
Compilation, flags and documentation: **CC BY 4.0**. The underlying statistics remain subject to the terms of the World Bank, Eurostat, OECD and IMF (see `SOURCES_AND_LICENCES.txt`).

## How to cite
Chaudhari, P. S., Joshi, A. H., Jaypatre, G. M., Birajdar, D. P. (2026). *GovAlloc-COFOG: harmonised general-government expenditure by function (COFOG) panels with provenance and imputation flags (v1.0)* [Data set]. Zenodo. https://doi.org/{DOI_V1}
"""
(ROOT / "release/kaggle_description.md").write_text(DESC, encoding="utf8")
meta = {
    "title": "GovAlloc-COFOG: Government Spending by Function",
    "id": "pranavchaudhari/govalloc-cofog",
    "subtitle": "Harmonised COFOG expenditure shares for up to 217 economies, 2000-2024",
    "licenses": [{"name": "CC-BY-4.0"}],
    "keywords": ["government", "economics", "finance", "public spending", "open data"],
}
(OUT / "dataset-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf8")
print(len(list(OUT.iterdir())), "files in", OUT)
