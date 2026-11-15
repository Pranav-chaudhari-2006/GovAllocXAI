# Known issues and future work (read this before the next revision / peer-review round)

Written 15 Nov 2026 after the internal peer-panel review (`docs/audits/05_peer_panel_reviews/`). Everything below is a real, open item.

## 1. Reproducibility issue: pipeline/09 does not reproduce exactly
* **What:** re-running `pipeline/09_wdi_panel_and_legacy_audit.py` (Panel B, WDI global panel, leave-country/region results) gives results that differ from the committed `results/03_wdi_panel/wdi_results.csv`. Over the 210 rows, the maximum absolute difference was **0.106 for MAE, 0.115 for RMSE and 0.042 for R²** (same shape and columns).
* **What was done:** the committed (original) results file was restored, so `papers/tables/tab_B.tex`, Fig. 6 and the numbers quoted in the paper (e.g. leave-country R² 0.63 health, 0.60 R&D) match the committed file, not a fresh re-run.
* **Likely cause (not yet diagnosed):** some learners in script 09 are not fully seeded or are fitted with multi-threaded non-deterministic routines. Scripts 03-08 and 19-25 were checked as deterministic (macros and tables regenerated identically after the restructure); 09 is the exception.
* **To fix:** (a) seed every estimator (`random_state`, LightGBM `seed`/`deterministic=True`, `n_jobs=1`), (b) rerun 09, (c) rerun `pipeline/27_make_figures_tables.py`, (d) compare `papers/results_macros.tex` and the tables, update any quoted number, (e) rebuild the zips (`python tools/build_overleaf_zips.py`).
* **If a reviewer asks:** state that Panel B figures come from a single run, that repeated runs vary by up to about 0.04 R² in this one experiment, and that none of the paper's conclusions depends on differences of that size.

## 2. Analyses reviewers asked for that were NOT re-run (listed as limitations in the paper)
Rolling-origin headline test (more than one train/test split); fold-internal feature imputation (currently transductive); Panel B without fiscal-total features; stronger cold-start baselines (region x income mean, GDP-per-capita regression); permutation-importance and null baselines for the explanations; a strict forecasting version with lagged covariates (current annual setting is a nowcast); stack vs k-NN vs Dirichlet head-to-head test; a notation table; the total-budget module without its near-proxy feature (3.82 -> 4.73 pp MAE internal check not stored in `results/`).

## 3. Software issues
* The API returns **in-sample** fits for economies that are part of the training panel (disclosed on the website and in the paper, not fixed). Fix: leave-one-economy-out refit per request or cached out-of-fold predictions.
* Website items not done: first-request timer, sorted-bar replacement for the 16-slice donut, inline glossary links.
* CSV column names still contain `legacy_v1` (e.g. `has_legacy_v1_row`) because renaming them requires regenerating the datasets.

## 4. Evidence / citation caveats
* **Mohith et al. 2026:** judged from the abstract only (paywalled IEEE paper). **Nonato et al. 2026:** the open-access page was read; its methods and results tables could not be extracted by our tools; the figures quoted in the paper (24 real observations, 1 048 synthetic points, R^2 0.97 vs -0.45) are all in the Crossref abstract. **Kisman et al. 2026:** abstract (via Crossref) only; the publisher blocks automated access. All three carry a dagger in the positioning table. Read the full texts before submission.
* The literature search was Google Scholar plus Crossref. **Scopus, Web of Science and IEEE Xplore were not searched** (they need an institutional login); strings are in `docs/literature_and_novelty.md`.
* Santschi et al. 2024 has no DOI (AIS eLibrary URL only, which is how the proceedings are published). Holm (1979) is now in the bibliography with its JSTOR stable URL (no Crossref DOI record exists).

## 5. Before submission
Zenodo DOI placeholder (`XXXXXXX`) in `papers/main_journal.tex`; confirm CRediT roles and the AI-use declaration; run similarity/AI-writing reports; Overleaf compile; choose venue (`docs/guides/03_journals_and_conferences.md`).

## 6. Not obtained / out of scope
BOOST low-income country databases (portal links did not open); human-subject study (protocol and analysis script in `docs/guides/human_study/`); Polity/V-Dem.
