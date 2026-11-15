# Methods and experiments log

What was built, why, what changed relative to the original (semi-synthetic) benchmark, and every extension including negative results. Sections: change log, extensions and negative results, institutional features, expert-panel recommendations, paper-format review.


---

## A. Change log (before / now / why)

*Covers everything changed between the original v1 project (commit `47d6c19`, "Prepare backend for Render deployment" plus the untracked old paper/literature) and v2.1 (this state). Format for every row: **Before → Now → Why → Where**. Nothing has been pushed; all commits are local.*

---------------------------------------------------------------------------------------------------
## A. Data

| # | Before (v1) | Now (v2.1) | Why | Where |
|---|---|---|---|---|
| A1 | One semi-synthetic dataset: 31 countries, 775 rows, 59 columns; presented as the evidence | **Preserved verbatim** (`legacy_*` columns in the master + `govallocxai_old_dataset.csv`) but used only as an **audited negative control** | Audit showed its targets are not real (A2). Keeping it satisfies "old dataset preserved" and enables direct legacy-vs-real comparison | `data/dataset_new/`, `archive_v1_original/dataset_legacy/` |
| A2 | 15 sector targets in USD; 11 of them were **exact fixed multiples of one series** (identical mix in every row); `healthcare_usd` **= an input feature**; 12 identical column pairs | **Official targets**: COFOG shares of total spending (Eurostat, OECD, IMF) and WDI sector series (education, health, military, R&D) | A model cannot learn "allocation" from a target that has no allocation variation; leakage inflated R² | `pipeline/03_build_dataset.py` |
| A3 | Features: real WDI values (undocumented; paper said they were *not* from WDI) | Same real features **re-downloaded from the World Bank API** (26 WDI + 4 WGI indicators), matching the legacy values exactly; provenance documented | Honest provenance; reproducibility | `pipeline/01_fetch_worldbank_eurostat.py` |
| A4 | 31 economies (≈ 80 % high/upper-middle income); 1 typo'd country list (`Neatherland`, `Phillipines`) | **218 economies** in the master; modelling panels: **A16** 36 economies / 825 rows, **A10** 85 economies / 1,526 rows (incl. 35 middle/low-income), **B** 211 economies / 4,995 rows | The user's question: a model for a *new country* needs diverse training countries; measured that region transfer is poor | `data/dataset_new/*.csv` |
| A5 | No missing values ("MICE imputation" listed but a no-op) | **Targets never imputed.** Features: ≤3-yr interpolation → ≤3-yr edge fill → region×income×year median; every imputed cell flagged (`imp_*`); features with 65–81 % imputation (poverty, Gini, literacy) excluded | Transparent, reviewable handling of missing data | `03_build_dataset.py` |
| A6 | OECD/IMF not used | **OECD Table 11** added (9 economies); **IMF GFS_COFOG** added (190 economies fetched, 623 complete country-years used) | Extends coverage to developing economies | `01_fetch_worldbank_eurostat.py`, `02_fetch_imf_cofog.py` |
| A7 | No cross-source validation | Eurostat↔OECD (690 rows: median diff 0.025 pp, r ≥ 0.996) and IMF↔Eurostat (723 rows: median diff ≤ 0.06 pp, r ≥ 0.984) | Shows the merged data are consistent | `govallocxai_new_data_quality.json` |
| A8 | Column `social_welfare_freebies_usd` | COFOG **"social protection"** | "Freebies" is politically loaded; not acceptable in a government-facing paper | taxonomy in `gov_common.py` |
| A9 | Taiwan rows (25) with no World Bank counterpart | Kept as `legacy_only_row = 1` | Preserve every legacy row | master CSV |
| A10 | Raw data not stored | `data/raw/` holds verbatim API downloads (WDI/WGI JSON, Eurostat JSON, OECD CSV, IMF per-country CSV) | Auditability | `data/raw/` |

## B. Methodology and evaluation

| # | Before | Now | Why | Where |
|---|---|---|---|---|
| B1 | Paper claimed temporal split; notebooks used **random** 80/20 split | **Temporal** (train ≤ 2019 → test 2020–24 incl. COVID), **leave-country-out** (6 folds × 2 seeds), **leave-region-out**, **by income group** | Random splits leak neighbouring years/countries; the new protocols match real use | `04_experiments_main.py`, `09_wdi_panel_and_legacy_audit.py`, `03d` |
| B2 | Targets in absolute USD; R² dominated by 3–4 big economies | **Shares of total spending** (simplex, Σ=100) and metric **TVD** = % of budget that must move | Scale-free and meaningful to officials; fixes GDP dominance | `gov_common.py` |
| B3 | No baselines ("no baseline other than the three compared configurations") | Persistence, country mean, income-group peer mean, global mean, ridge | A learner is only useful if it beats what practitioners do; persistence turned out very strong | all `03*` |
| B4 | Single point estimates, one seed | 95 % **cluster-bootstrap CIs over countries**, 2 fold-seeds, paired comparisons | Years within a country are not independent | `gov_common.boot_ci` |
| B5 | "Hybrid" = 50/50 average, no ablation | Hybrid kept but **tested against its parts**; plus **Stack v2.1** (NNLS weights, validation-window / nested-CV) | A "hybrid" claim needs evidence | `06_stack_architecture.py` |
| B6 | Two undefined regimes | Explicit **Mode 1 annual update** (Δ-learner on last year) and **Mode 2 cold-start** | Matches the two real use cases | `03`, `03c` |
| B7 | Allocation via SLSQP, unevidenced | **Exact bounded-simplex projection** (bisection) + SLSQP cross-check (agree to 4e-15) + **bound-width study** (tight 1–99 pct bounds clip 37 % and hurt; 0.5×min…1.5×max clips < 2 %) | Verified, explainable constraint layer | `gov_common.py`, `02_main_experiments/bounds_sensitivity.csv` |
| B8 | "Accuracy (%)" undefined | Removed; metrics TVD/MAE/RMSE/R² only | Not a regression metric | — |
| B9 | "Total-budget predictor R² 0.91" with no traceable code | Real **total-expenditure module** (% of GDP): temporal MAE 1.83 vs persistence 2.87 pp of GDP; cold-start 3.82 vs 5.63 | Shares need a total to become money | `08_total_budget.py` |
| B10 | Stress test "100 % compliance" undefined, no code | **What-if sensitivities** (recession, stagflation, severe stress) reported honestly: small shifts, social protection moves the wrong way | Don't claim what the model can't do | `11_explain_shap_lime.py` |
| B11 | Hyper-parameters differed between paper and code | Fixed, documented hyper-parameters; richer feature specs tested **on a validation window only** (not adopted: no gain) | No test-set tuning | `05_feature_spec_selection.py` |
| B12 | — | **Architecture v2.1** tested: history features, CLR targets, stacking. Result: **cold-start significantly better** (A16 +0.78 pp, A10 +1.33 pp vs peer mean); **annual update: no gain, stack worse than persistence on A10** | The user asked to improve accuracy; we report what really helped and what did not | `03c`, `04_stack_architecture/*` |
| B13 | — | **Income-group error + applicability (novelty) score** (ρ = 0.70 with error) | Answers "can a new low-income country be predicted?" → errors 2–3× larger, so warn | `07_cold_start_by_income.py` |
| B14 | Feature `health_expenditure_usd` = target | Removed; features cannot be transformations of targets | Leakage | `gov_common.FEATURES` |

## C. Explainability

| # | Before | Now | Why |
|---|---|---|---|
| C1 | "LIME" = hand-written Gaussian-noise ridge (σ=0.1) | **Reference `lime` package**; SHAP via exact TreeSHAP | Faithful implementation of the cited method |
| C2 | One SHAP waterfall (top driver = the leaked feature) | **Global** SHAP heat-map (17 components), local case studies, **deletion-faithfulness** (3.1× random), **SHAP–LIME agreement** (ρ 0.59, sign 0.85), **LIME stability/fit** | Explanations must be measured, not displayed. In both case studies SHAP and LIME disagree on the leading sign — reported |
| C3 | "Explainability designed, not evaluated" (own limitation) | Evaluated (see `05_explainability/*`) | Close the gap the paper admitted |

## D. Backend / API
| # | Before | Now | Why |
|---|---|---|---|
| D1 | One endpoint trained on leaky v1 data with random split | **`/api/v2/*`**: `health`, `economies`, `recommend` (composition + SHAP + optional LIME + shocks + **applicability** + **total budget & amounts** + **two panels** 16/10) | Serve the real model |
| D2 | v1 endpoint | Kept, **deprecated**, repointed to archived dataset | Don't break old clients silently |
| D3 | 2 tests | **8 tests** (sum = 100, SHAP/LIME present, shocks, applicability, wide panel for India, totals/amounts) | Regression safety |

## E. Frontend (dashboard)
| # | Before | Now | Why |
|---|---|---|---|
| E1 | Demo/synthetic numbers labelled "research" (R² 0.9952…), 15 fake sectors, leaked-feature SHAP example | Pages call `/api/v2/recommend`; real SHAP/LIME, applicability banner, disclaimer; headline numbers taken from `results/`; demo data and 11 demo components/pages **removed** (`npm run build` passes; **UI not visually verified**) | A dashboard must not present synthetic numbers as results |

## F. Papers
| # | Before | Now | Why |
|---|---|---|---|
| F1 | One v1 paper (+ LaTeX zip built from .docx); duplicated paragraph; 9 padding references; R² > 0.99 headline | **Journal** (elsarticle) and **conference** (IEEEtran) packages; new narrative: official data, baselines, audit, XAI evaluation, honest limits; 36 verified references | Publishable, defensible claims |
| F2 | Numbers typed by hand | Numbers are **LaTeX macros generated from `results/`** (`results_macros.tex`), tables/figures auto-generated | Text can never drift from results |
| F3 | No highlights, no AI-use statement | Highlights (5), data-availability, ethics, **AI-use declaration (draft)** | Journal requirements |
| F4 | Overfull wide tables | Tables wrapped in `resizebox`; both packages test-compiled once with Tectonic (PDF produced) | Layout |
| F5 | Zip rebuilt manually | `build_overleaf_zips.py` lints + zips (`papers/dist/`) | One-command update |
| F6 | Folder `paper_v2` | Renamed **`papers/`** | Clearer structure |

## G. Literature
| # | Before | Now | Why |
|---|---|---|---|
| G1 | 24 PDFs in one folder, 9 irrelevant | Split into `01_cited_in_paper_v1/` and `02_downloaded_similar_work/` (**10 PDFs** incl. Nonato 2024, Rădulescu 2015, Tekbaş 2026), index with roles and **3 base papers** (`literature/README.md`) | Know what is base/similar/background |
| G2 | No novelty evidence | Query log + gap table (`docs/02`) | Defend originality; repeat on Scopus/WoS |

## H. Repository structure
| Before | Now |
|---|---|
| `dataset/`, `ml_models/` (3 Colab notebooks), `paper & related resources/`, `literature/` (flat), `src/`, `backend/` | `data/{raw,processed}`, `pipeline/` (numbered scripts), `results/`, `papers/`, `docs/`, `literature/{01,02}`, `archive_v1_original/` (all v1 files), `backend/`, `src/` (kept at root so existing deployment config keeps working) |

## I. Documentation
README rewritten (self-contained guide); `docs/01` audit, `02` literature gap, `03` expert panel, `04` paper-format review, `05` dataset card, `06` this log.

## J. Verification performed
Static LaTeX lint (labels, cites, macros, figures) on every build · both papers compiled once with Tectonic · 8 backend tests pass · `npm run build` passes · an independent read-only agent cross-checked hard-coded numbers against `results/` (see §K) · SLSQP cross-check of the allocation engine.

## K. Open items (not done)
Low-income coverage (3 economies); dashboard not visually checked in a browser; Overleaf layout check; author e-mail/CRediT/competing-interest/AI-use text; repeat literature search on Scopus/WoS; OECD/IMF redistribution terms; multi-year projection; fairness audit; human-subject study.

---------------------------------------------------------------------------------------------------
## L. Round 3 (16 Nov 2026) — review, extensions, corrections

| # | Before | Now | Why | Where |
|---|---|---|---|---|
| L1 | Authors: Birajdar, Jaypatre, Chaudhari, Joshi, Rajeswari, Surana; corresponding = Surana; email placeholder | Authors per your list: **Aditi H. Joshi (corresponding), Pranav S. Chaudhari, Gaurav M. Jaypatre, Digvijay P. Birajdar**, institutional emails in both papers and README | Your instruction. *(K. Rajeswari and Priya A. Surana, the guides on the original paper, are no longer listed — add them back if they should be authors.)* | `papers/main_*.tex`, README |
| L2 | Two papers (Yang 2023, OECD WKP 1785) missing from folder | Present (you added them); renamed consistently; indexed; both cited in related work after verifying their abstracts; claim about OECD paper corrected to what it actually says | Completeness; avoid unverified claims | `literature/`, `papers/sections/sec_related.tex`, `references.bib` |
| L3 | Novelty claim unchecked beyond a small search | **37-query novelty search** (`docs/07_Novelty_Search_Report.md`): no direct competitor, three close ones (Valle-Cruz 2022, Kisman 2026, econometric COFOG-share studies); wording softened ("our own earlier benchmark", "to our knowledge"); Krishna 2022 and Adolph 2020 added | Avoid over-claiming; defensible positioning | `docs/07`, papers, README |
| L4 | API recommended with a **single XGBoost** | API recommends with the **stack** (peer mean + ridge + XGBoost-CLR + CatBoost-CLR, NNLS weights); members fitted lazily on first request to keep start-up fast | The stack is the best cold-start method (−1.3 pp vs peer mean on A10); the API should serve the best model | `backend/service.py`, `pipeline/18_export_stack_weights.py`, `backend/stack_weights.json` |
| L5 | No uncertainty in the API | **Conformal-style 80 %/90 % intervals** per component (calibrated on out-of-fold stack residuals; income-group-specific when ≥150 rows) with a coverage warning for lower-income groups | Analysts need ranges, not points; honest about under-coverage | same + `11_knn_and_conformal/*` |
| L6 | SHAP/LIME only | + **kNN "similar economies"** (5 nearest training economies with distances, weights, shares) | Most intuitive explanation; as accurate as XGBoost | `backend/peer_module.py`, `pipeline/peer_module.py`, `16_knn_and_conformal.py` |
| L7 | Shocks, multi-year, low-income, fairness listed as "weak spots" | Each **implemented and evaluated** (shock module, multi-year, low-income expansion, fairness audit): **shock features and multi-year projection do not help; low-income data gap is a reporting gap; fairness gap is significant** — all reported honestly | You asked whether these can be implemented: yes, and the answers are in the results | `docs/10`, `docs/08`, `pipeline/10–13` |
| L8 | Human-subject study = "future work" sentence | Complete protocol, consent/instructions/vignette/questionnaire templates, response sheet and analysis script with self-test (cannot be run without participants and ethics approval) | Makes the study ready to execute | `docs/09`, `docs/study_materials/`, `pipeline/16` |
| L9 | Paper had hard-coded "exactly" claims about legacy data | Corrected after an independent number audit (defence/inflation match, 218 vs 217 economies, rounding) | Accuracy of claims | papers, README, dataset card |
| L10 | Paper sections up to v2.1 | New subsection "Extensions tested, including negative results", human-study note, conference paragraph | Keep papers synchronised with results | `papers/sections/sec_results.tex`, `sec_discussion.tex`, `main_conference.tex` |
| L12 | Defaults assumed adequate | Optuna nested-CV tuning run: **no significant gain** (XGB +0.05, CatBoost +0.17 pp; CI include 0) → defaults kept | Check whether accuracy was left on the table | `pipeline/17_hyperparameter_tuning.py`, `results/13_hyperparameter_tuning/*` |
| L11 | Tests: 8 | **9 tests** (adds peers + intervals) | Regression safety | `backend/tests/test_v2_api.py` |

## M. Honest status of "weak spots" after round 3
| Weak spot | Status |
|---|---|
| Low-income coverage | **Not fixable from reachable official APIs** (IMF has no data for 22/25 low-income economies); needs manual national-budget data collection; mitigations in place (applicability score, interval warning, fairness audit) |
| Shocks not anticipated | Tested; **not solvable with macro features**; remains a human-judgment area |
| Multi-year projection | Tested; **persistence is best**; not offered |
| Fairness audit | **Done** (`docs/08`) |
| Human-subject study | **Ready to run** by the authors (`docs/09`) |

| L13 | No classical panel baselines | Random walk with drift and AR(1)/AR(1)+FE on CLR shares added (all significantly worse than persistence) | Obvious reviewer objection | `pipeline/19_econometric_baselines.py`, `results/14_econometric_baselines/*` |
| L14 | No readiness assessment | Senior-researcher audit: conference ready after small fixes; Q1 not yet (W1–W15 with fixes and time) | Honest go/no-go | `docs/11_Senior_Researcher_Readiness_Audit.md` |
| L15 | Novelty search only by web agent | Crossref proxy search + Nzazi record re-verified | Partial substitute for Scopus/WoS (which need your login) | `docs/07b_Crossref_Proxy_Search.md`, `tools/search_crossref_novelty.py` |

| L16 | Extra Q1 modules pending | Dirichlet/MLP/FT baselines (A16+A10), blend explanation (KernelSHAP) + synthetic XAI test, institutional features ablation, 5-seed Holm robustness all completed and written into the papers; supplementary tables moved to an appendix, `[!t]` float placement + `placeins`; final compile: journal 41 pp, conference 5 pp, no errors | Q1-grade robustness and layout | `pipeline/20–24`, `papers/`, `docs/00`, `docs/12` |


---

## B. Extensions and negative results

*Answer to: "Can the weak spots (low-income coverage, shocks, multi-year projection, fairness audit, human-subject study) be implemented?" and "add modules for accuracy/optimisation". Every module below was implemented as a re-runnable script, evaluated with the same honest protocol (grouped / temporal splits, cluster-bootstrap CIs) and is reported **whether or not it helped**. Result files: `results/08_shock_experiments/* … 13_hyperparameter_tuning/*`.*

| Weak spot / idea | Implemented? | Script | Verdict |
|---|---|---|---|
| Shocks not anticipated | ✅ shock-aware features (growth change, unemployment change, recession dummy, global-shock feature, regime split) | `pipeline/12_shock_experiments.py` | ❌ **does not help — hurts** |
| Multi-year projection untested | ✅ rolling-origin horizons 1–5 (recursive with oracle macros, recursive with frozen macros, direct multi-horizon) | `pipeline/13_multi_year_projection.py` | ❌ **persistence wins at every horizon** |
| Low-income coverage | ✅ diagnosis + data expansion (IMF central-government, relaxed window) + income-weighted training | `pipeline/14_low_income_expansion.py` | ⚠ **data gap is real; cannot be fixed from IMF**; weighting only suggestive |
| Fairness audit | ✅ error/bias parity by income group & region, need-vs-allocation | `pipeline/15_fairness_audit.py`, `docs/08_Fairness_Audit.md` | ✅ done — **a significant income gap exists** |
| Explainable "similar economies" + accuracy | ✅ kNN peer module | `pipeline/peer_module.py`, `16_knn_and_conformal.py` | ✅ **as accurate as XGBoost, fully explainable** — in API |
| Prediction intervals | ✅ split-conformal (global + Mondrian by income group) | `16_knn_and_conformal.py` | ✅ near-nominal overall; ❌ under-covers lower-income groups — in API with warning |
| Hyper-parameter optimisation | ✅ Optuna, nested grouped CV | `17_hyperparameter_tuning.py` | ❌ **no significant gain** (truncated search) |
| Total budget (USD) | ✅ (earlier today) | `08_total_budget.py` | ✅ useful |
| Production stack | ✅ weights exported, API recommends with the **stack** (not single XGBoost) | `18_export_stack_weights.py`, `backend/` | ✅ |
| Human-subject study | ✅ protocol + materials + analysis script (**cannot be run by us — needs people and ethics approval**) | `docs/09_…`, `docs/study_materials/`, `pipeline/16_analyze_human_study.py` | ready to run |

## 1. Shock module — negative result
Features available in year *t*: country growth, change in growth/unemployment/inflation/debt, recession dummy, severity, a contemporaneous cross-country median growth ("global shock"), and a regime-split variant.
* **COVID 2020–21** (TVD pp): A16 persistence 4.07, baseline Δ-learner 3.89, **shock-aware 4.16** (−0.26 vs baseline, CI −0.41…−0.11, i.e. significantly worse); A10 shock-aware −0.40 vs baseline (CI −0.51…−0.29).
* **GFC hold-out** (train ≤ 2007, test 2009–10): A16 persistence 3.43, baseline 3.61, shock-aware 4.07/4.31 (worse).
* Health and social-protection shifts in 2020–21 are still not captured (health actually +0.62 pp on A16; predicted −0.08…+0.10).
* *Why it fails:* the training window contains almost no global-recession years, so the global-shock effect cannot be learned; spending reallocations in crises are policy decisions, not smooth functions of macro indicators.
**Decision:** not adopted. The paper keeps "shock years are not anticipated — human judgment dominates". (This is consistent with Barnes et al. 2023 on reallocation frictions.)

## 2. Multi-year projection — negative result
Rolling origins 2012–19, horizons 1–5, pooled TVD (pp).
* A16 persistence: 2.92 (h=1), 3.81, 4.56, 5.15, **5.63 (h=5)**. The best alternative at h=1 is the recursive Δ-model with *true future* macros (2.80, gain +0.11, CI −0.13…0.45, not significant); from h=2 on it is worse than persistence (gain −0.08 … −0.47).
* **Frozen-macro** projections (what a user without macro forecasts would run) are always worse than persistence, significantly.
* Direct multi-horizon models do no better (A16 h=5: 6.38 vs persistence 5.63).
**Decision:** multi-year projection is **not offered**; if a user wants a multi-year view, use "same split as last year" and treat shifts as scenarios.

## 3. Low-income coverage
* **Why coverage is low:** the IMF general-government COFOG file has **no COFOG values at all for 22 of 25 low-income and 35 of 47 lower-middle-income economies** (a reporting gap, not a filter).
* **Expansion attempt:** adding IMF central-government data (S1311) and relaxing the consistency window to 90–110 % adds **only 13 rows**: low-income economies 3 → 6 (30 → 37 rows), lower-middle 9 → 11. 12 of the 13 are *central*-government-only and differ from general-government shares by a mean 7.5 pp TVD on 78 overlapping country-years, so they are **not comparable**; the extended panel is kept as a separate flagged file (`data/dataset_new/govallocxai_new_cofog10x_panel.csv`) and **not used for headline results**.
* **Weighting:** inverse-frequency income-group sample weights cut low-income TVD from 33.1 → 32.0 on the original A10 (CI of the difference −2.9…+1.3, not significant); on the expanded panel 32.8 → 29.2 (CI −4.7…−2.7, but resting on 3 economies). Income one-hot features do nothing.
**Conclusion:** the missing low-income data cannot be created from official sources reachable by API; **the real fix is data collection** (national treasury publications, e.g. India's Union Budget, Kenya, Nigeria, Bangladesh budgets mapped to COFOG). Until then, the applicability warning is the honest safeguard.

## 4. Fairness audit (details: `docs/08_Fairness_Audit.md`)
Leave-country-out, A10, XGBoost:
* **Worst group = low income: TVD 33.4 pp (CI 23.7–40.9) vs high income 11.4**; max/min ratio 2.94 (CI 2.09–3.85) vs 2.56 for the peer-mean baseline → **ML does not close the gap for low-income economies** (it helps lower-middle and high income).
* The one detectable signed bias: **social protection in low-income economies is over-predicted by +4.1 pp** (CI 2.5–7.0; actual share 3.0 %). Health and education bias are not distinguishable from zero in any group.
* On the WDI series, relative error is 1.3–1.9× larger in poorer groups.
* Caveat: 3 low-income economies; economies that publish COFOG are likely better-reported, so true low-income error is probably larger.

## 5. Accuracy modules that worked
### 5.1 kNN "similar economies" (explainable)
Leave-country-out TVD (pp): **A10**: peer-mean 14.93, XGBoost 13.96, **kNN k=8 13.73** (gain over peer mean 1.20 pp, CI 0.67–1.72; vs XGBoost +0.23, CI −0.31…0.81 → equivalent). **A16**: peer-mean 11.29, XGBoost 10.96, **kNN k=8 10.59** (gain 0.70, CI 0.20–1.22). Adding kNN as a stack member gives a small extra gain (+0.06 … +0.16 pp, mostly not significant). **Adopted for explanation:** the API returns the 5 nearest training economies, their distances, weights and shares — the most intuitive explanation for an analyst ("countries like yours spend …").
### 5.2 Conformal prediction intervals
Out-of-fold, calibrated on training economies only (A10): nominal 80 % → **80.1 %** coverage, 90 % → **90.3 %** (mean width 8.7 / 12.6 pp). **But by income group** (global calibration, 80 % nominal): high-income 86 %, upper-middle 68 %, lower-middle 61 %, **low-income 47 %**; Mondrian (group-specific) calibration repairs upper-middle (81 %) but not the small groups. **Adopted with a warning:** the API returns 80 %/90 % intervals and states that coverage is unreliable for lower-income economies.
### 5.3 Production stack
The API now recommends with the nested-NNLS **stack** (peer mean + ridge + XGBoost-CLR + CatBoost-CLR); SHAP/LIME explain the XGBoost member (documented in every response).

## 6. Hyper-parameter optimisation (Optuna, nested grouped CV)
Nested grouped CV on the wide panel A10 (6 outer folds; inner 3-fold Optuna/TPE search, objective = TVD): XGBoost default 13.96 pp → tuned 13.91 pp (paired gain 0.05 pp, CI −0.19…0.30); CatBoost default 13.69 → tuned 13.53 pp (gain 0.17 pp, CI −0.09…0.43). **No significant gain**, and the search was truncated by the shared CPU (2–5 trials per fold instead of 25/12), so this is indicative: the default hyper-parameters are close to a good region and further accuracy gains are unlikely to come from tuning. Not adopted (defaults kept; no test-set tuning).

## 6b. Econometric panel baselines (added after the senior audit)
`pipeline/19_econometric_baselines.py`: random walk with drift, pooled AR(1) on CLR shares + macro covariates, AR(1) + country fixed effects. **All are significantly worse than persistence** (A16: 3.73 / 3.86 / 3.88 vs 3.62 pp; A10: 4.85–5.24 vs 4.62 pp). Closes an obvious reviewer objection (“why not a standard panel model?”).

## 7. Human-subject study
Protocol, materials and analysis script are ready (`docs/09_Human_Subject_Study_Protocol.md`, `docs/study_materials/`, `pipeline/16_analyze_human_study.py`, self-test passes). **It cannot be executed by us:** it needs ethics-committee approval, participants (≈159 for the primary ANOVA at medium effect; 90 is an exploratory fallback), filled-in vignettes, and OSF pre-registration. Estimated effort for your team: 2 weeks.

## 8. Take-aways for the paper
1. Honest negatives (shocks, multi-year, low-income data) are reported, not hidden. 2. kNN and conformal modules add explainability/uncertainty without hurting accuracy. 3. The fairness audit is a contribution in itself: a documented income gap with a concrete bias (social protection in low-income economies).

## 9. Robustness: 5 fold-seeds + Holm correction (`pipeline/20_robustness_holm.py`, `results/15_robustness_holm/*`)
After Holm correction only these headline claims survive (α = 0.05): **stack vs peer mean on A10** (p_holm 0.0008), **kNN-8 vs peer mean on A10** (0.0008) and **on A16** (0.034). **Do not claim as significant:** stack vs peer mean on A16 (p_holm 0.060), XGBoost vs peer mean (≥ 0.06), stack vs XGBoost (≥ 0.06); annual-update hybrid vs persistence (raw p 0.72 / 0.89). The paper text (journal §Extensions) states this.
## 10. Not finished (usage budget)
`pipeline/21_dirichlet_neural_baselines.py` (Dirichlet + MLP baselines) was started but **not completed**; explaining the blend with KernelSHAP and the institutional-features ablation were **not run**. They are listed as future work; do not cite partial files `results/16_dirichlet_neural_baselines/*` if present.

## 11. Dirichlet / neural baselines (`pipeline/21_dirichlet_neural_baselines.py`, `results/16_dirichlet_neural_baselines/*`)
Cold start A10 (TVD): **Dirichlet 13.69**, MLP 13.85, XGBoost 14.08, CLR-ridge 14.11, FT-Transformer 14.14, peer mean 15.01 (stack from §5: 13.77). A16: none significantly better than peer mean/XGBoost. Annual: persistence 4.62 (A10) / 3.62 (A16); best learner = ridge Δ-learner (+0.04 / +0.13 pp); direct neural models far worse (6.5–7.7). **Take-away:** a Dirichlet regression is as good as the stack for new countries — mention as a strong, simple alternative.
## 12. Blend explanation, synthetic sanity, institutional features
See `docs/12_Institutional_Features_Note.md` and `results/17_blend_explanation/*`: KernelSHAP of the blend agrees only moderately with the XGBoost member (Spearman 0.29–0.42); synthetic test: precision@3 = 0.67 (independent) → 0.43–0.52 (correlated copy); institutional WGI features: no significant gain.


---

## C. Institutional features

Script `pipeline/23_institutional_wgi.py`; results `results/18_institutional_features/wgi_*`; data `data/dataset_new/govallocxai_new_institutional_features.csv`.
* **Obtained (keyless, World Bank API source 3):** WGI Voice & Accountability, Political Stability (+ 2-year changes); coverage ≈ 97 % (91 % for changes) of panel A10 rows.
* **Obtained manually (Nov 2026):** IMF Fiscal Rules 1985-2024, DPI 2020 (elections), IMF MONA arrangements -> `pipeline/24_institutional_manual.py`, results `results/18_institutional_features/manual_*`. **No gain** in cold start or annual update (all CIs include 0; see paper, Results/Extensions). Polity/V-Dem not obtained..
* **Result (A10):** cold-start TVD 13.96 → 13.91 (gain 0.04 pp, CI −0.12…0.21; seed 1: 0.09, CI −0.07…0.26); annual update 4.74 → 4.71 (gain 0.02, CI −0.04…0.08; 2020–21: 0.03). **No significant gain.**


---

## D. Expert-panel recommendations

*Panel (simulated by the reviewer, each speaking from their discipline): public-finance economist · applied-ML/forecasting researcher · XAI researcher · data engineer/data-curation lead · governance & ethics reviewer · biostatistician (uncertainty/validity).*

## A. Verdict on the v1 architecture
Seven boxes (data → preprocessing → features → models → total-budget → allocation → SHAP/LIME → SDG) look complete, but:
1. The *economist*: a budget is a **composition under a fixed total**; modelling 15 absolute USD numbers independently is the wrong object (non-additive, GDP-dominated).
2. The *forecaster*: no persistence/peer baseline → no evidence of value; practitioners start from last year's budget.
3. The *XAI researcher*: SHAP/LIME were bolted on; never evaluated; LIME hand-rolled.
4. The *data lead*: targets were synthetic and leaked; no provenance, no flags, no official source for the allocation labels.
5. The *ethics reviewer*: no statement of who decides, what the model may not be used for, nor any fairness/coverage analysis.
6. The *statistician*: single split, single seed, no intervals, a metric ("accuracy %") that is not defined.

## B. Implemented in v2 (all reproducible from `pipeline/`)

| Area | Change | Why it matters | Where |
|---|---|---|---|
| **Targets** | Official COFOG shares (Eurostat + OECD) for 16 functions + residual; WDI official sector series for 211 economies | Real labels; removes synthetic-target trap | `03_build_dataset.py` |
| **Representation** | Composition on the simplex, TVD metric ("% of budget to be moved") | Scale-free, explainable to officials; fixes GDP-dominance | `gov_common.py` |
| **Two regimes** | (1) one-step-ahead Δ-learner on top of persistence; (2) cold-start peer learner | Mirrors the two real situations (annual update vs. country with no history) | `04_experiments_main.py` |
| **Baselines** | Persistence, country mean, income-group peer mean, global mean, ridge | A model that cannot beat these is not decision support | same |
| **Validation** | Temporal (incl. COVID/energy shock), leave-country-out (×2 seeds), leave-region-out, cluster-bootstrap CIs | Removes leakage across years/countries; honest uncertainty | same + `04_*.py` |
| **Allocation engine** | Exact bounded-simplex projection with policy floors/ceilings (+SLSQP cross-check), bound-sensitivity study | Guarantees sum = 100 % and statutory limits; where legal minima are entered | `gov_common.py`, `02_main_experiments/bounds_sensitivity.csv` |
| **Explainability** | TreeSHAP + reference `lime` package; agreement, stability, fidelity, deletion-faithfulness; case studies; what-if shocks | Turns "we use SHAP" into measured evidence | `11_explain_shap_lime.py` |
| **Leakage audit** | Forensic re-analysis of v1: constant-ratio targets, identical columns, protocol mismatch | The most reusable contribution to the community: shows how R² > 0.99 arises from a synthetic target | `09_wdi_panel_and_legacy_audit.py` |
| **Data release** | 5,450-row master with provenance + imputation flags + all legacy columns; Eurostat↔OECD cross-validation | Publishable, citable dataset | `data/dataset_new/` |
| **Software** | v2 API (`/api/v2/recommend`: composition + SHAP + LIME + shocks), tests, legacy endpoint deprecated | Demo now uses the real model | `backend/` |

## C. Recommended next (ranked by value / effort)

| Rank | Item | Value | Notes |
|---|---|---|---|
| 1 | **Add IMF GFS COFOG / national treasury data for non-OECD economies** (India, Brazil, Indonesia, South Africa, Egypt, Nigeria…) | Removes the biggest external-validity threat: the 36-economy COFOG panel is OECD/EU-heavy | IMF `GFSCOFOG` dataset; manual download if the API stays unreachable; keep the same schema and `cofog_source` flag |
| 2 | **Sub-national/ministry-level case study** for India (Union Budget "Expenditure Budget" tables, 2000–2025) with a human-review user study (n ≥ 10 analysts) | Real-world problem solving; supports the "assist the human" claim with a human-subjects result | Needs ethics approval; measure *time-to-decision*, *agreement*, *trust calibration* |
| 3 | **Conformal / quantile prediction intervals per sector** (split-conformal on the Δ-learner) | Gives the analyst "reasonable range" instead of a point share; makes the bounds data-driven | Cheap with `MAPIE`-style residual quantiles; evaluate coverage |
| 4 | **Statutory-floor library** (e.g. education ≥ x % GDP laws) as the bounds input of the engine | Makes the constraint layer policy-real rather than quantile-based | Requires a curated table of national rules |
| 5 | **Counterfactual / fairness audit**: error by income group and region; "need vs allocation" gap (à la Di Stefano & Resce) using SDG-index trends | Addresses equity and the need–allocation paradox | SDR-2026 workbook already in `archive_v1_original/dataset_source_files/` |
| 6 | **Dirichlet / log-ratio (ILR) regression** and a **Temporal Fusion Transformer** as additional learners | Respects compositional geometry; fair neural comparison | Only worth it if they beat Δ-hybrid with CIs |
| 7 | **Explanation robustness**: SHAP on correlated groups (grouped Shapley), interventional vs path-dependent, LIME kernel-width sweep | Correlated macro features make single-feature SHAP fragile | Add to `11_explain_shap_lime.py` |
| 8 | **Monitoring/drift**: PSI on features and rolling TVD on new COFOG releases; automated re-fit | Real deployment concern | Fits the existing pipeline scripts |
| 9 | **Model card + data sheet** (Gebru et al.) and an explicit "not for" list (no automated approval, no use for politically contested single-line items) | Governance | Skeleton in README |

## D. Honest limits of the present evidence (read before submitting)
* The official COFOG panel is OECD/EU-centred (36 economies); WDI panel is global but has only 4 sector series.
* One-step-ahead gains over persistence are **small** (≈0.14 pp of total spending, CI just above zero). In the 36-economy COFOG panel the cold-start learner is *not* significantly better than the income-group peer mean (paired gain 0.35 pp, CI spans 0). In the 211-economy WDI panel the cold-start learner clearly helps for health (R² 0.63 vs 0.31) and R&D (0.60 vs 0.25), modestly for education and not for defence. The paper states this plainly rather than selling R².
* SHAP/LIME are **associational**; "what-if" shocks are model sensitivities, not causal effects.
* No human-subject study yet (rank 2 above).


---

## E. Paper-format review

Packages (rebuilt by `python tools/build_overleaf_zips.py`):
* `papers/dist/GovAllocXAI_Journal_Q1_Overleaf.zip` – Elsevier `elsarticle`, single-column preprint.
* `papers/dist/GovAllocXAI_Conference_IEEE_Overleaf.zip` – `IEEEtran` two-column conference.

## 0. Compile status (updated)
**Both packages were compiled with Tectonic (a portable TeX engine) on 15 Nov 2026: no errors. Conference paper = 5 pages (within the usual 6-page limit). Journal manuscript = 41 pages (incl. supplementary tables) in Elsevier single-column *preprint* 12 pt format** (this is the review layout; the final two-column journal layout will be about 14–18 pages). Overleaf may still differ slightly in float placement.

## 0b. (older note) The first thing to know
**No TeX engine is installed on the machine that built these files, so neither package has been compiled here.** What *was* done: an automated static lint (`tools/latex_lint.py`) confirms balanced braces and environments, every `\ref` has a `\label`, every `\cite` key exists in `references.bib`, every `\Result` macro is defined, every figure file exists. That catches most compile-stoppers but not all (package/class warnings, overfull boxes, float placement, page count). **Compile both on Overleaf before judging layout, and send me the log if anything fails.** Everything below is therefore a *desk review*.

## 1. Journal package (elsarticle)

| Criterion | Status | Verdict |
|---|---|---|
| IMRaD structure (Intro → Related → Data → Method → Results → Discussion → Conclusion) | present | ✅ Standard; "Experimental setup" folded into Method (acceptable) |
| Abstract ≤ 250 words, no citations, quantitative | ≈ 225 words, numbers present | ✅ |
| Highlights (3–5 bullets, ≤ 85 chars) | 5 bullets, 67–71 chars | ✅ (Elsevier requirement) |
| Keywords (≤ 6) | 7 keywords | ⚠ drop one (e.g. "data leakage") for Elsevier |
| Contributions explicit | 5 numbered | ✅ |
| Research gap supported by a positioning table | Table "gap" | ✅ (judgements are the authors'; keep the "as judged by the authors" caption) |
| Baselines, CIs, significance | persistence/peer/ridge; cluster bootstrap | ✅ |
| Negative results reported | yes (cold-start n.s.; shocks missed; what-if wrong sign) | ✅ reviewers reward this; do not remove |
| Threats to validity, ethics, data availability, AI-use statement | present | ✅ — AI-use text is a *draft for authors to confirm* |
| CRediT author statement, competing-interest declaration, funding | **missing** | ❌ add before submission (journal systems ask for them) |
| Graphical abstract | missing | ◻ optional; Fig. 1 can be reused |
| Length | ≈ 5–6 k body words + 11 tables + 10 figures | ⚠ heavy for ESWA/GIQ (≈ 8–9 k words incl. everything is typical). If the editor complains, move `tab_features`, `tab_sdg`, `tab_hyper`, `tab_selection`, `tab_ablation` and Figs 2, 5, 10 to a supplementary file |
| References | 35 (33 cited) | ✅ adequate; add 8–10 more domain refs (e.g. IMF fiscal-forecasting, OECD *Government at a Glance*) after your own Scopus search |
| Notation consistency | `TVD`, `Δ-learner`, `hybrid` used consistently | ✅ |
| Self-plagiarism / v1 text reuse | v1 prose was rewritten; the duplicated v1 paragraph is gone | ✅ run iThenticate/Turnitin again |
| Claims vs evidence | every number in the text is a macro generated from `results/` (except ~15 hard-coded figures in Results prose, see §4) | ⚠ see §4 |

**Likely reviewer objections (and the honest answer):** (1) *COFOG panel is OECD/EU-centred* → true, stated, rank-1 roadmap item. (2) *Gains over persistence are small* → true, stated in abstract. (3) *Why not a deep/temporal model?* → future work; tabular GBDT are state of the art on this scale (cite Grinsztajn 2022). (4) *Tuning?* → fixed hyper-parameters, validation-only spec selection. (5) *Is the audit of your own v1 data a contribution?* → positioned as a cautionary methodological contribution; some venues will not value it, in that case shorten §6.1 to a paragraph.

**Venue fit.** Best fit by scope: *Government Information Quarterly*, *Socio-Economic Planning Sciences*, *Expert Systems with Applications*, *Engineering Applications of AI*, *IEEE Access* (fast, broader). Do **not** target a top ML venue (novelty is application/evaluation, not algorithmic).

## 2. Conference package (IEEEtran)

| Criterion | Status | Verdict |
|---|---|---|
| Template | `IEEEtran` `[conference]` (built into Overleaf) | ✅ |
| Abstract 150–200 words | ≈ 120 words | ✅ |
| Page budget | 4 full-width figures + 3 tables + 2 wide tables on ≈ 800 words of body | ⚠ estimate 6–7 pages; most IEEE conferences allow 6 (+2 over-length). If it reaches 8, drop Fig. 8 or Table "xai" |
| Required sections | Intro, Related Work, Data, Framework, Results, Discussion, Conclusion | ✅ |
| Self-contained | all numbers via macros; references in `references.bib` (19 cited) | ✅ |
| Weak points | very dense Method paragraph; reviewers may want the engine equation numbered; no per-sector table | ⚠ acceptable for a conference |
| Compile risk | `table*` and `figure*` only (no `[h]`), `cite` package loaded | low |

## 3. Things a format reviewer will flag in *both*
1. Author block lacks e-mail/ORCID (placeholders). 2. "Acknowledgements" empty. 3. Figure fonts are 6–8 pt in the PDFs; at column width in the conference version Fig. 8 (three sub-panels) will be small — enlarge or split if it is hard to read in the proof. 4. Tables use `booktabs`; no vertical rules ✅. 5. All figures have vector PDF + 300-dpi PNG ✅. 6. British/American spelling mixed (*defence* is used for COFOG "Defence"); pick one before submission.

## 4. Content hard-coded in the prose (not macro-generated)
Hard-coded numbers in `sections/sec_results.tex` / `main_conference.tex` that must be re-checked if you rerun experiments: WDI $R^2$ values (0.63/0.31, 0.60/0.25, 0.30/0.02, 0.12/−0.03, region-out values, ridge 0.50/0.53), "6.3–9.2 pp" and "3.47–3.76 pp" ranges, correlations 0.46/0.36/0.31, COVID +0.22/−0.12 pp, "37 %" and "43 %" clipping shares, "TVD 3.65". They are all currently consistent with `results/`; a future improvement is to emit them as macros too.

## 5. How the zips stay current
`27_make_figures_tables.py` rewrites `results_macros.tex`, `tables/*.tex` and `figures/*` from `results/`; `build_overleaf_zips.py` lints and re-zips. After any change to code or data: rerun `03`–`05` as needed, then `06b`, then `09`.
