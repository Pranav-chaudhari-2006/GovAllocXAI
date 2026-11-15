# Dataset Card — GovAllocXAI-Data v2.1

*Built by `pipeline/01_fetch_worldbank_eurostat.py`, `02_fetch_imf_cofog.py`, `03_build_dataset.py` from official APIs on 14 Nov 2026. Raw downloads are in `data/raw/`, outputs in `data/dataset_new/`. Every cell is either an official observation, a flagged imputed feature, or a legacy v1 value (prefixed `legacy_`).*

## 1. Files
| File | Rows × cols | Purpose |
|---|---|---|
| `govallocxai_new_master.csv` | 5,450 × 217 | All economies × 2000–2024: features, every target series, flags, all legacy v1 columns (57 prefixed `legacy_`; country and year are keys) |
| `govallocxai_new_cofog_panel.csv` | 825 × ~220 | **Panel A16**: complete 16-function COFOG breakdown (Eurostat + OECD), 36 economies |
| `govallocxai_new_cofog10_panel.csv` | 1,526 × ~220 | **Panel A10 (new in v2.1)**: complete 10-division COFOG breakdown (Eurostat + OECD + **IMF**), **85 economies incl. 35 middle/low-income** |
| `govallocxai_new_wdi_panel.csv` | 4,995 × ~220 | **Panel B**: WDI official sector series (health, education, defence, R&D), 211 economies |
| `govallocxai_old_dataset.csv` | 775 × 59 | v1 dataset, verbatim |
| `govallocxai_new_data_quality.json` | — | Coverage, imputation, legacy-vs-real and cross-source audit |

## 2. Sources and cross-validation
| Source | Used for | Coverage | Cross-check |
|---|---|---|---|
| World Bank WDI (26 indicators) + WGI (4) | features; Panel B targets | 217 economies, 2000–2024 | v1 features reproduced exactly (750 rows) |
| Eurostat `gov_10a_exp` | COFOG targets (16 functions / 10 divisions) | 30 economies | — |
| OECD NAD Table 11 | COFOG targets for non-Eurostat OECD members | 6 (A16) / 9 (A10) economies | vs Eurostat: median diff 0.025 pp, r ≥ 0.996 (690 rows) |
| **IMF GFS `GFS_COFOG`** (general government, % of total expenditure) | COFOG 10-division targets for non-EU/OECD economies | 190 economies fetched; 623 complete, internally consistent (Σ = 100 ± 3) country-years used | vs Eurostat on 723 overlapping rows: median diff ≤ 0.07 pp, r ≥ 0.984 for all 10 divisions |

Priority when several sources cover a country-year: Eurostat > OECD > IMF. IMF series are renormalised to Σ = 100 (raw sums 97–103 %).

## 3. Targets
* **A16 (17 components):** general public services, defence, public order, agriculture, energy, industry & construction, transport, communication, R&D (economic affairs), environment, housing & community (excl. water), water supply, health, recreation & culture, education, social protection, *other/unallocated residual*. Unit: % of total general-government expenditure.
* **A10 (10 components):** COFOG divisions GF01–GF10. Same unit. Wider country coverage because IMF reports divisions (not groups) for most economies.
* **Panel B:** education, domestic general-government health, military, R&D as % of GDP; education/health/defence also as % of government expenditure.
* Targets are **never imputed**; a country-year enters a COFOG panel only if all components exist.

## 4. Coverage of Panel A10 (85 economies, 1,526 country-years)
* Income group: 50 high-income, 23 upper-middle, 9 lower-middle, 3 low-income.
* Regions: Europe & Central Asia 45, East Asia & Pacific 14, Latin America & Caribbean 9, MENA/AFG/PAK 7, Sub-Saharan Africa 6, North America 2, South Asia 2.
* By source: Eurostat 740, IMF 623, OECD 163 country-years.

## 5. Feature handling
30 features (26 WDI + 4 WGI); 25 used for modelling. Imputation: ≤ 3-year interpolation → ≤ 3-year edge fill → region × income × year median; every imputed cell flagged (`imp_*`); poverty, Gini and literacy (65–81 % imputed) excluded from models. History features for the v2.1 architecture (lag-1, lag-2, trend, expanding country mean of *past* values) are computed from targets of earlier years only.

## 6. Licences and terms
World Bank (CC BY 4.0) · Eurostat (CC BY 4.0 reuse policy) · IMF data: subject to IMF terms of use/attribution — **verify before redistributing IMF-derived rows** · OECD: OECD terms of use — **verify before redistributing**. COFOG: UN Statistics Division classification.

## 7. Known limitations
Executed general-government spending (not proposals) · definitions vary slightly across sources and countries · IMF series for developing economies are short and sometimes revised · Panel A10 has only 12 lower-middle/low-income economies (23 upper-middle) · sub-national budgets absent · the SDG cross-walk is the authors' reporting layer, not an official mapping.

## 8. Recommended citation
Authors (2026). *GovAllocXAI-Data v2.1: a provenance-flagged panel of government expenditure by function.* Repository `GovAllocXAI`, `data/dataset_new/`. Cite the underlying sources (World Bank, Eurostat, OECD, IMF) as well.
