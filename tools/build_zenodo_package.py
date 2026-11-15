"""Build release/GovAlloc-COFOG_v1.0.zip: the files to upload to Zenodo (dataset record). Run: python tools/build_zenodo_package.py"""
import pathlib
import shutil
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "release"
OUT.mkdir(exist_ok=True)
NAME = "GovAlloc-COFOG_v1.0"
README = """GovAlloc-COFOG v1.0
Harmonised general-government expenditure by function (COFOG) panels with provenance and imputation flags
=====================================================================================================

Authors: Pranav S. Chaudhari, Aditi H. Joshi, Gaurav M. Jaypatre, Digvijay P. Birajdar
Affiliation: Department of Computer Engineering, Pimpri Chinchwad College of Engineering, Pune, India
Version 1.0, 15 November 2026. Code and papers: https://github.com/Pranav-chaudhari-2006/GovAllocXAI

WHAT IS INSIDE
  data/                      the dataset (CSV, UTF-8)
    govalloc_cofog_master.csv                  all economies x 2000-2024: features, every target series, flags
    govalloc_cofog_panel_a16.csv               Panel A16: 825 complete country-years, 36 economies, 16 COFOG functions (Eurostat, OECD)
    govalloc_cofog_panel_a10.csv               Panel A10: 1,526 country-years, 85 economies, 10 COFOG divisions (adds IMF)
    govalloc_cofog_panel_a10x.csv              A10 plus flagged relaxed-consistency rows for lower-income economies (exploratory)
    govalloc_cofog_panel_wdi.csv               Panel B: official WDI sector series (health, education, defence, R&D), 211 economies
    govalloc_cofog_institutional_features.csv  World Bank governance indicators used in an ablation
    govalloc_cofog_institutional_manual.csv    IMF fiscal rules, election timing (DPI) and IMF programme indicators used in an ablation
    govalloc_cofog_data_quality.json           counts and cross-source agreement statistics
  legacy/                    the ORIGINAL semi-synthetic dataset, kept only to document an audit. DO NOT use it for modelling.
  DATASET_CARD.md            full description, column dictionary summary, collection method, known limitations
  SOURCES_AND_LICENCES.txt   original data providers, access dates and the terms that apply

KEY FACTS
  * Targets (expenditure shares by COFOG function) are official published statistics and are never imputed.
  * Feature values that were filled in (<=3-year interpolation, then peer-group medians) are flagged per cell (columns starting with imp_).
  * Shares are percentages of total general-government expenditure and sum to 100 within each row.
  * The data are executed (outturn) spending, not planned budgets.

HOW TO CITE
  Chaudhari, P. S., Joshi, A. H., Jaypatre, G. M., Birajdar, D. P. (2026). GovAlloc-COFOG: harmonised general-government expenditure
  by function (COFOG) panels with provenance and imputation flags (v1.0) [Data set]. Zenodo. <DOI shown on the Zenodo record>

LICENCE
  The compilation, harmonisation, flags and documentation are released under CC BY 4.0. The underlying statistics remain subject to the
  terms of their original providers (see SOURCES_AND_LICENCES.txt); attribution to those providers is required.
"""
SOURCES = """SOURCES AND LICENCES (accessed 14 November 2026 through the providers' public APIs)

* World Bank, World Development Indicators (WDI) and Worldwide Governance Indicators (WGI) - open data, CC BY 4.0. https://data.worldbank.org
* Eurostat, government expenditure by function (gov_10a_exp) - free reuse with attribution. https://ec.europa.eu/eurostat
* OECD, National Accounts, Table 11 (government expenditure by function) - OECD terms and conditions apply. https://data-explorer.oecd.org
* International Monetary Fund, Government Finance Statistics (COFOG) - IMF data terms apply. https://data.imf.org
* IMF Fiscal Rules Dataset 1985-2024; IMF Monitoring of Fund Arrangements (MONA); Database of Political Institutions 2020 (IADB) -
  used only to derive the optional institutional-feature files; their own terms apply (attribution, non-commercial research use).

Users are responsible for checking the current terms of each provider before redistribution or commercial use.
"""

stage = OUT / NAME
if stage.exists():
    shutil.rmtree(stage)
(stage / "data").mkdir(parents=True)
(stage / "legacy").mkdir()
for f in sorted((ROOT / "data/dataset_new").glob("govalloc_cofog_*")):
    shutil.copy2(f, stage / "data" / f.name)
for f in sorted((ROOT / "data/dataset_old").glob("govalloc_cofog_legacy_dataset.csv")):
    shutil.copy2(f, stage / "legacy" / f.name)
(stage / "legacy" / "README_LEGACY.txt").write_text(
    "SEMI-SYNTHETIC LEGACY DATASET. Eleven of its fifteen sector columns are exact multiples of one series, so it must not be used for modelling.\n"
    "It is kept only so that the audit in the accompanying papers can be reproduced.\n", encoding="utf8")
shutil.copy2(ROOT / "docs/guides/04_dataset_card.md", stage / "DATASET_CARD.md")
(stage / "README.txt").write_text(README, encoding="utf8")
(stage / "SOURCES_AND_LICENCES.txt").write_text(SOURCES, encoding="utf8")
zpath = OUT / f"{NAME}.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(stage.rglob("*")):
        if f.is_file():
            z.write(f, f"{NAME}/{f.relative_to(stage).as_posix()}")
print(zpath, round(zpath.stat().st_size / 1e6, 1), "MB")
