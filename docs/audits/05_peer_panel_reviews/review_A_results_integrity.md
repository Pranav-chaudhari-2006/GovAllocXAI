# Review A: Results-integrity audit (independent, read-only)

Scope: papers/main_journal.tex, main_conference.tex, sections/*.tex, tables/*.tex, results_macros.tex; pipeline/*.py; results/*; data/dataset_new/*; archive_v1_original; backend/service.py; src/data/results.js.
Method: every number was traced to a results/ or data/dataset_new/ file; 14 quantities were recomputed independently with pandas / the project's own helper functions (scratch scripts outside the repo). No paper or code was edited; nothing committed.

## 1. Verdict

**Fabrication found: NO.** Every number in the abstracts, Results, Discussion and tables that I checked (about 120 values, 62 listed below) traces to a file in results/ or data/dataset_new/, and the 14 recomputations reproduced the stored values to the printed precision (several to 1e-12). Legacy-audit claims reproduce from the raw archive xlsx. Dashboard/API contain no invented performance numbers.

**Integrity problems found: 0 critical, 1 high (presentation/arithmetic), 6 medium, about 12 low.** The most important: (H1) the headline cold-start "paired gains" (1.33, 0.78, 0.35 pp ...) are computed on fold-seed 0 only, while the TVDs printed next to them are two-seed means, so the abstract's own numbers do not subtract to the quoted gain; (M1) the headline "statistically significant" annual gain (0.140 pp, CI 0.025-0.277) is not robust to the learner seed (4 of 5 seeds have a CI that includes 0).

No evidence of target leakage into the reported test numbers was found (Section 3). Leakage-type issues are limited to feature-side transductive imputation (low) and a near-proxy feature in the total-budget module (medium, disclosure).

## 2. Verified numbers (62 claims; R = recomputed by me from raw/processed data)

Legend: OK = matches; the "Trace" column gives file and field.

| # | Claim (where) | Paper value | Trace (file : field) | Result |
|---|---|---|---|---|
| 1 | Master rows / cols / economies (macros, sec_data) | 5,450 / 217 / 217 | data_quality.json master_rows, master_cols, countries(218)-1; **R** master.csv shape (5450,217), 217 WB economies + TWN 25 legacy-only rows | OK (rows=217x25+25; cols==economies=217 is a coincidence, both verified) |
| 2 | A16 panel 825 rows, 36 economies, 2000-2024 | 825/36 | 02_main_experiments/summary.json panel; **R** panel_a16.csv (825, 36, 2000-2024, shares sum to 100 within 2.8e-14) | OK |
| 3 | A16 source split, OECD-added economies, complete rows | 6 / 109 | **R** cofog_panel cofog_source_name: Eurostat 716, OECD 109 rows, 6 OECD economies | OK (data_quality lists 9 OECD-only economies, 6 have complete A16 rows; wording could say so) |
| 4 | WDI panel 4,995 rows / 211 economies | 4,995 / 211 | **R** panel_wdi.csv | OK |
| 5 | A10 panel 1,526 / 85 economies, 623 IMF rows | 1526/85/623 | **R** panel_a10.csv; source counts Eurostat 740, IMF 623, OECD 163 | OK |
| 6 | "35 middle- and low-income economies" in A10 | 35 | **R** income_group != High: 35 | OK |
| 7 | Legacy-matched rows | 750 | data_quality legacy_vs_real n=750 | OK |
| 8 | Cross-source Eurostat vs OECD | median 0.025 pp, r>=0.996 (except communication) | data_quality eurostat_vs_oecd_crosscheck: medians 0.023-0.028, min r=0.9959 (water), communication r=0.9637; n=690 | OK |
| 9 | IMF vs Eurostat, 723 overlap, median <=0.07, r>=0.984 | as stated | data_quality cofog10_imf_vs_eurostat: n=723, max median 0.0619, min r 0.9845 | OK |
| 10 | Structurally missing features 65-81 % imputed | 65-81 | data_quality feature_imputed_cells_pct: poverty 65.0, gini 65.0, literacy 81.0 | OK |
| 11 | Persistence TVD (2020-24) | 3.62 [3.17, 4.08] | 02_main_experiments/temporal_history.csv row 0; **R** from panel: 3.6157 raw / 3.6164 after renorm, CI 3.171-4.075 | OK |
| 12 | n test / n train | 178 / 611 | **R** has_lag rows: 178 / 611 | OK |
| 13 | Country-mean TVD | 6.96 | **R** 6.9582 | OK |
| 14 | Hybrid TVD | 3.48 [3.06, 3.91] | **R** 02_main_experiments/best_predictions.csv: 3.4764 (post-engine 3.4637) | OK |
| 15 | Paired gain 0.140, CI 0.025-0.277, 53 % rows | 0.140 / 53 | 02_main_experiments/summary A1_paired; **R** (seed 42) 0.14000, CI 0.0252-0.2772, 94/178=52.8 % | OK, but see M1 (seed fragility) |
| 16 | Features-only range 6.3-9.2; Delta learners 3.47-3.76 | as stated | 02_main_experiments/temporal_history.csv | OK |
| 17 | Health 2020 mean change actual +0.22, predicted -0.12; r=0.27 (health), 0.34 (soc. prot.) | as stated | 02_main_experiments/summary covid | OK (pred delta -0.1208 is the raw learned change; after renorm/clipping it is -0.196) |
| 18 | Delta-learner direction correlations 0.47 edu, 0.37 GPS, 0.30 health, ~0 defence/R&D | as stated | 02_main_experiments/delta_dynamics.csv: 0.470, 0.369, 0.301, 0.016, 0.014 | OK |
| 19 | Cold start hybrid 10.77 [9.60,12.05], peer 11.34, global 11.35 | as stated | 02_main_experiments/cold_start.csv; **R** peer-mean seeds 0/1 = 11.2930 / 11.3775 (mean 11.335), global 11.303/11.398 | OK |
| 20 | Cold-start ridge 11.98 | 11.98 | **R** ridge, 2 seeds: 12.114, 11.853, mean 11.9838 (identical to csv 11.98377) | OK |
| 21 | Cold-start paired gain 0.35 [-0.44, 1.10] | 0.35 | 02_main_experiments/summary A2_paired (seed 0 only; 04_experiments_main.py:136, 143-145) | Value traces, but **inconsistent with the 11.34 - 10.77 = 0.57 printed beside it** (H1) |
| 22 | Ablation: all 10.83, minus groups 10.94-11.14 | as stated | 02_main_experiments/ablation.csv | OK ("two seed SD" claim: see L7) |
| 23 | Bounds sensitivity: 37 % clipped, 43 % outside, TVD 3.65 vs 3.48; 0.5x-1.5x clips <2 % | as stated | 02_main_experiments/bounds_sensitivity.csv; **R** 0.3708, 0.4326, 3.6487; 0.0169; 3.4637 | OK |
| 24 | Engine sum error 3e-14; SLSQP diff 3.6e-15 | as stated | 02_main_experiments/summary engine: 2.84e-14, 3.55e-15 | OK |
| 25 | Panel B table (7 targets x LCO/LRO/temporal) | Table B | 03_wdi_panel/wdi_results.csv: all 7x6 cells match to 2 dp except LRO health 0.495 (table 0.49, text 0.50) | OK (L8) |
| 26 | Panel B n per target | 4547/2212/3365/3814 | **R** wdi_panel non-null counts | OK |
| 27 | Ridge R2 0.50 (health), 0.53 (R&D); gains +0.13/+0.07 | as stated | expB: 0.503, 0.534 | OK |
| 28 | A16 history: stack 3.51 pp, gain 0.11 [0.03, 0.20] | 3.51 | 04_stack_architecture/summary A16 history: TVD_test 3.5046; paired 0.1118 [0.0265, 0.2029]; table E_hist prints 3.50 | **Mismatch 3.51 vs 3.50** (M4) |
| 29 | A10 history: persistence 4.62, best 4.56, stack 4.82; stack vs persistence -0.20 [-0.35, -0.03] | as stated | 04_stack_architecture/summary A10 history; tab_E_hist | OK |
| 30 | Cold A16: stack 10.53 [9.48, 11.67], peer 11.34; gain 0.78 [0.07, 1.46]; xgb 0.34 | as stated | 04_stack_architecture/summary A16 cold: 10.530, 0.7847 [0.068, 1.457], 0.344 | OK (gains are seed-0, H1) |
| 31 | Cold A10: stack 13.77 [12.30, 15.45], peer 15.01, xgb 14.12; gain 1.33 [0.72, 1.94]; xgb 0.96 [0.25, 1.69] | as stated | 04_stack_architecture/summary A10 cold: 13.766, 15.011, 14.115; 1.3320 [0.7175, 1.9389]; 0.965 [0.246, 1.687] | OK as numbers; 15.01-13.77=1.24, not 1.33 (H1) |
| 32 | Income table: 50/23/9/3 economies; 1064/371/61/30 rows | Table | **R** cofog10_panel groupby; 06_cold_start_by_income/cold_by_income.csv | OK |
| 33 | Income-group peer-mean TVD 12.5/18.3/28.1/32.1 | Table | **R** peer mean seed 0 by group: 12.53/18.26/28.07/32.06 | OK (single seed) |
| 34 | XGB by income 11.4/18.5/22.0/33.4; high 11.4, low 33.4 | Table/macros | 06_cold_start_by_income/cold_by_income.csv; 12_fairness_audit/A10_group_error.csv | OK (expJ reruns give 33.1; L9) |
| 35 | Spearman novelty vs error 0.70 | 0.70 | 06_cold_start_by_income/applicability.json 0.7037 (n=1526 rows, pooled) | OK |
| 36 | Total budget: persistence 2.87, delta ridge 1.83, group mean 5.63, ridge 3.82 | Table G | 07_total_budget/total_budget.csv | OK; **"36 economies" is wrong, 07_total_budget/summary: 30 economies, 716 rows** (M3) |
| 37 | Hyper-opt: XGB 13.96->13.91 (gain 0.05, CI -0.19..0.30); Cat 13.69->13.53 (0.17, -0.09..0.43) | as stated | 13_hyperparameter_tuning/summary.json | OK |
| 38 | kNN k=8: 13.73 vs XGB 13.96, 1.20 better than peer, CI 0.67-1.72 | as stated | 11_knn_and_conformal/summary A10 knn_rows, paired knn8_vs_peer_mean 1.1951 [0.670, 1.721]; **R** kNN8 TVD 13.7316, peer 14.9267, gain 1.19513, CI 0.67017-1.72072 (exact) | OK (seed 0; mixes with 2-seed 14.12 elsewhere, L9) |
| 39 | Conformal 80 -> 80.1 %, 90 -> 90.3 %; low-income 47 %, lower-middle 61 % | as stated | 11_knn_and_conformal/summary conformal 0.8007, 0.9034; 11_knn_and_conformal/A10_conformal_by_group.csv 0.4733, 0.6115 | OK |
| 40 | Fairness: low 33.4 [23.7, 40.9], high 11.4, max/min 2.94 [2.09, 3.85] vs 2.56; social-protection bias +4.1 [2.5, 7.0] | as stated | 12_fairness_audit/summary.json; 12_fairness_audit/A10_signed_bias.csv 4.050 [2.496, 7.001] | OK |
| 41 | Low-income: IMF empty for 22/25 low and 35/47 lower-middle; 13 added rows, mean TVD 7.5; weighting 33.1->32.0 | as stated | 10_low_income_expansion/summary diagnosis; new_rows total 13; central_vs_general mean 7.48; TVD_xgb 33.138, weighted 32.034 (delta -1.10, CI -2.93..1.29) | OK |
| 42 | Shock-aware 2020-21: 4.16 vs 3.89, diff -0.26 [-0.41,-0.11], persistence 4.07; GFC 4.07 vs 3.43 | as stated | 08_shock_experiments/summary A16 a_covid 2020-21 xgb_shock 4.159, base 3.894, -0.264 [-0.405,-0.105], pers 4.072; b_gfc 4.067 vs 3.432 | OK (XGB variant reported; CatBoost variant 4.005 also reported in file, L11) |
| 43 | Multi-year: A16 persistence 2.92 (h=1), 5.63 (h=5) | as stated | 09_multi_year_projection/summary A16 rows: 2.916, 5.632 | OK; "best at every horizon" see M5 |
| 44 | Econometric: RW-drift 3.73 (diff -0.12 [-0.15,-0.09]), AR(1) 3.86, FE 3.88; A10 persistence 4.62, 4.85-5.24 | as stated | 14_econometric_baselines/summary.json 3.7329, 3.8560, 3.8818 | OK (alpha=1 variants only; alpha=10 variants 4.63-5.0 not mentioned) |
| 45 | Holm: stack A10 p=0.0008; kNN8 A10 0.0008, A16 0.034; stack A16 0.060; xgb>=0.06; stack vs xgb>=0.06; CLR hybrid raw p=0.72 / 0.89 | as stated | 15_robustness_holm/holm.csv; **R** Holm step-down recomputed on the 8-test cold family: 0.060, 0.1712, 0.0336, 0.1404, 0.0008, 0.060, 0.0008, 0.060 | OK (exact) |
| 46 | Blend explanation: rho 0.42/0.29/0.37; Jaccard 0.32-0.39; sign 0.97/0.71/0.77; faith 2.6/1.3/2.8 | as stated | 17_blend_explanation/blend.csv | OK |
| 47 | Synthetic truth test: precision@3 0.67; 0.52 (TreeSHAP), 0.43 (LIME); driver share 0.46->0.38 | as stated | 17_blend_explanation/summary.json 0.667, 0.517, 0.433, 0.459->0.381 | OK (sd 0.0 in independent case = ceiling, L12) |
| 48 | Institutional (WGI): 13.96->13.91, gain 0.04 [-0.12, 0.21]; annual 4.74->4.71 (0.02), 2020-21 0.03 | as stated | 18_institutional_features/wgi_summary seed0 13.956->13.914, 0.0419; annual 4.735->4.712 | OK (seed-1 value 0.094 not shown; same null) |
| 49 | Manual institutional groups: -0.02 / -0.02 / 0.00 / -0.03 (cold); annual -0.02..-0.004 | as stated | 18_institutional_features/manual_summary: -0.0238, -0.0231, +0.0025, -0.0305; annual -0.0056..-0.0162 | Numbers OK; **sign wording** M6; coverage 78/77/100 % = 0.777/0.773/1.0 OK |
| 50 | Dirichlet 13.69 vs stack 13.77, 1.32 better [0.55, 2.01]; MLP 13.85; FT 14.14 vs XGB 14.08; annual best ridge-delta 4.58, direct nets 6.55-6.91 | as stated | 16_dirichlet_neural_baselines/summary.json (13.694, 1.316 [0.546,2.005], 13.849, 14.141, 14.077); expQ annual 4.582, 6.554, 6.906 | OK |
| 51 | SHAP/LIME table: rho 0.58/0.64/0.52/0.67/0.59/0.56 mean 0.59; Jaccard mean 0.48; sign 0.85; LIME R2 0.52; rerun 0.86; faith 2.0-3.8 mean 3.1 | Table xai, macros | 05_explainability/shap_lime_agreement.csv / 05_explainability/summary.json (means recomputed: 0.594, 0.85, 3.12) | OK |
| 52 | Global SHAP drivers per function (agri VA, 65+, trade openness, ...) | prose | 05_explainability/global_shap.csv top-5 per function | OK |
| 53 | Case studies Germany/Italy: leading feature opposite sign SHAP vs LIME | prose | 05_explainability/case_studies.csv: DEU tax_revenue shap -0.61 / lime +0.83; ITA total_expense shap -0.77 / lime +0.77 | OK |
| 54 | What-if: all shifts <0.7 pp; GPS +0.6, soc. prot. -0.7 | prose | 05_explainability/whatif_shock.csv delta_pp 0.612 / -0.683 | OK |
| 55 | Legacy: 11/15 exact multiples of agriculture; ratios 2.0, 3.0, 1.5, 1.25, 1.125, 0.875 (x2), 0.75, 0.625, 0.5; sd ~1e-12 | audit text | 01_legacy_audit/legacy_structure.json; **R** from archive xlsx: ratio sd 1e-12..2.5e-12, all ratios exact | OK |
| 56 | Legacy latent total 16.7 % GDP, CV 2.8 %, r=0.84 with GDP growth | audit text | **R** archive xlsx: mean 16.685, CV 0.02849, r=0.84107 | OK |
| 57 | 12 identical column pairs; healthcare == health_expenditure feature | audit text | **R** np.allclose over all *_usd pairs: 12 pairs (same list as 01_legacy_audit/legacy_audit.json) | OK |
| 58 | Legacy R2: XGB 0.996, k x GDP 0.924 (15 sectors); 0.9991 vs 0.9997 (11); real-4: 0.987 vs 0.714; const share -0.0002 | macros/Table audit | 01_legacy_audit/legacy_audit.json replication (means recomputed by me: 0.9959, 0.9236, 0.9872, 0.714) | OK |
| 59 | Legacy vs official: edu diff <1e-9, defence <0.001 pp (r=0.998), health median gap 2.4 pp r=0.88; inflation within 0.4 % on 90 % | audit text | data_quality legacy_vs_real: 3.05e-13, 7.3e-4 (0.9982), 2.4355 (0.8791), p90 0.0040 | OK |
| 60 | Table audit rows (mean %GDP, CV) | Table | **R** archive xlsx: defence 1.820 / 81.9, R&D 1.584 / 70.2, edu 5.428 / 79.4, health 7.309 / 44.3, 11 synthetic 2.8 CV | OK |
| 61 | Archive xlsx identical to data/dataset_new legacy csv | -- | **R** max relative difference 2.1e-16 (775 x 59) | OK |
| 62 | Dashboard KPIs (src/data/results.js) | 3.62/3.48/0.14; 10.53/11.34; 13.77/15.01; R2 0.63/0.31...; 11.4/18.5/22.0/33.4 | match results/ above | OK (hand-copied constants, no generator; see L13) |

Recomputations performed directly (R): items 1-6, 11-15, 17, 19-20, 23, 32-33, 38, 45 (Holm), 55-61, plus a 5-seed rerun of the headline Delta-hybrid (M1) and drop-feature checks (M3). Rerunning the project's own `gov_common`/`peer_module` code on seed 0 reproduced stored outputs exactly (hybrid gain 0.14000071196875932; kNN8 gain 1.195127045652003; ridge cold 11.983771574151788).

## 3. Methodology / leakage review (concrete lines)

| Check | Verdict | Evidence |
|---|---|---|
| Temporal split | CLEAN | 04_experiments_main.py:39 `tr = d[(d.year <= 2019) & d.has_lag]; te = d[(d.year >= 2020) & d.has_lag]`; bounds from `Ytr` only (line 89, 99-101); country mean from `tr` (44-45). Lag only when previous calendar year exists (gov_common.py:56-58). |
| Features at t not using t targets | CLEAN | History features shift targets (03c:42-49); expanding mean `s.shift(1).expanding().mean()` (03c:49) uses past only. FEATURES (gov_common.py:34-38) are WDI/WGI macro series; none is a function of the COFOG shares. |
| Contemporaneous macro features | DESIGN NOTE | x_{c,t} (e.g. GDP growth, inflation in the target year) are used, so the one-step "forecast" is conditional on same-year macro outcomes (nowcast). Persistence has no such advantage. Worth one sentence in Methods. |
| Leave-country-out grouping | CLEAN | Folds assigned per country, then mapped to rows: 04_experiments_main.py:119-121; 03c:168-169; same pattern in 14, 15, 20, 03d, 03e, 21. |
| Stack weights nested | CLEAN | 03c:174-185 (inner 4-fold grouped CV inside each outer training set; `W` from `inner_oof` and `Y.iloc[a]`; test fold predictions blended with `W`). Same in 16_knn_and_conformal.py:88-110 and 20_robustness_holm.py:56-64. History-mode stack: weights fitted on 2017-19 validation window (03c:113, 125-127), test used once. |
| Target never imputed | CLEAN | 03_build_dataset.py header and :166-175 impute FEATS only (`FEATS = [v for v in WB_IND.values() if not v.startswith("T_")]`, line 163); COFOG shares computed with `min_count`/NaN propagation (:72, :77). Residual `cofog_other_residual` = 100 - sum is a derived target, not imputed. |
| Hyper-parameters not tuned on test | CLEAN (as far as verifiable) | gov_common.py:73-81 fixed values, file has a single commit in git history (no tuning history). 17_hyperparameter_tuning.py is properly nested (inner 3-fold grouped CV on training economies, defaults enqueued as trial 0, lines 69-88, 99-112). 03b selection uses train<=2016/val 2017-19 only (:21). |
| Bootstrap by cluster | CLEAN | gov_common.py:152-163 resamples countries (sum/count per cluster); 2,000 draws default (matches Methods); Holm study uses 10,000 (20_robustness_holm.py:23, 97-101). |
| Holm implementation | CLEAN | 20_robustness_holm.py:111-115 is a correct step-down Holm; family = 8 cold-start comparisons (4 per panel); I reproduced all adjusted p-values. |
| kNN / novelty standardisation | CLEAN | peer_module.py:23-29 mean/sd/medians from training economies only; 03d:33-37 per fold. |
| Early stopping in neural baselines | CLEAN | 21_dirichlet_neural_baselines.py:54-58, 173 validation split taken from training economies (grouped), not from the test fold. |
| Explanations | CLEAN | 11_explain_shap_lime.py:14-20 model trained <=2019, explained on 2020-24 test rows; 80 random rows (`rng.choice(len(te), 80)`, line 37) match Table xai caption. |
| Feature imputation (transductive) | LOW | 03_build_dataset.py:168-170: interpolation/bfill (limit 3) can use values after 2019 for rows that end up in the training window, and the region x income x year median (line 170) pools all economies incl. test economies. Features only, flagged, never targets; effect likely negligible but Methods says "no test information" in places. Disclose or restrict imputation to the training window. |
| Static current income group | LOW | 03_build_dataset.py:28 uses the World Bank's current classification for every year; used by peer-mean baselines and the by-income error tables. Not target leakage, but the classification is partly an outcome of the same economic history. |
| Near-proxy feature for total budget | MEDIUM (disclosure) | 08_total_budget.py:35, 46 use FEATURES that include `total_expense_pct_gdp` (WDI central-government expense), r=0.75 with the target `cofog_total_expenditure_pct_gdp` (**R**). Dropping it raises cold-start ridge MAE from 3.82 to 4.73 pp, dropping tax, debt and expense gives 5.97 (vs 5.63 for the mean baseline, so the module has no skill without the proxy). This is a legitimate feature, not leakage, but the paper's claim "No feature is a transformation of a target" should be accompanied by this caveat. Panel B is not affected: removing `total_expense_pct_gdp` changes XGB LCO R2 for health from 0.633 to 0.626, education 0.273 to 0.268, defence 0.079 to 0.081 (**R**). |
| Selection of k for kNN | LOW-MEDIUM | 16_knn_and_conformal.py:43 `KS = [3, 5, 8, 12]`; 20_robustness_holm.py:44-54 carries only k=8 into the Holm family. In the same OOF data k=12 is marginally better (13.707 vs 13.732) and five stack variants were also screened; neither the k grid nor the other screened variants enter the Holm family. Mild forking-paths exposure; say k=8 was fixed a priori (if true) or add k to the family. |
| Stale docstring | LOW | 04_experiments_main.py:4 says "3 fold-seeds"; code (:118) and paper use 2. |
| Panel B protocol asymmetry | LOW | 09_wdi_panel_and_legacy_audit.py:106 uses a single fold seed (no seed SD, no CIs on R2); Methods (sec_method.tex) says "repeated with two fold seeds" without restricting to Panel A. LRO R2 is pooled across held-out regions (:119-120), whereas the text says "negative R2 in some regions". |

## 4. Statements checked against the numbers (significant / CI / Holm)

* "Significant" CI-based statements: A10 stack vs peer (CI 0.72-1.94), kNN vs peer (0.67-1.72), A10 stack worse than persistence (-0.35..-0.03), econometric baselines worse than persistence (all CIs exclude 0), A16 stack vs persistence (0.03-0.20): all CIs exclude 0 as claimed. Non-significant claims (cold-start A16 gain 0.35, XGB A16 0.34, tuning, institutional features, shock features) all have CIs that include 0 as claimed.
* Holm statements: all adjusted p-values and the survives/does-not-survive classification reproduce (Section 2, item 45).
* **Not robust / inconsistent**: see M1 (annual 0.140 significance), M7 (XGB "significant 0.96 pp" on A10 vs Holm p=0.06, same paper), M6 (sign wording).
* The abstract's "significantly better than the peer mean (1.33 pp)" is supported after Holm (A10 stack p_holm 0.0008; 5-seed gain 1.263, CI 0.685-1.837); only the 1.33 figure itself is the seed-0 value (H1).

## 5. Legacy-audit claim ("eleven of fifteen sectors are exact multiples")

CONFIRMED from `archive_v1_original/dataset_legacy/ML_Budget_Dataset_WorldBank_Completed.xlsx` (sheet Completed_Dataset, 775 x 59; max relative difference to data/dataset_new/govalloc_cofog_legacy_dataset.csv 2.1e-16; the second copy in dataset_source_files has the same shape).
Ratio to agriculture (mean, sd): infrastructure 2.000 (2.2e-12), rural development 0.875 (1.2e-12), social welfare 3.000 (2.5e-12), energy 1.250, transport 1.500, housing 1.125, water 0.750, environment 0.625, digital 0.500, industry 0.875 (identical to rural development). The four others (defence, R&D, education, health) vary (ratio sd 0.9-3.4). Distinct sector-mix patterns among the eleven: 1 (rounded at 1e-9); max share sd 7.9e-14. Total of the eleven = 16.685 % of GDP (CV 2.85 %, r=0.841 with GDP growth). Twelve identical column pairs including `healthcare_usd == health_expenditure_usd` and all SDG budgets. Minor wording points: L1, L2.

## 6. Dashboard / API (backend/service.py, src/data/results.js)

* No fabricated numbers. All model outputs are computed at request time from the processed panels (service.py:122-123 XGBoost fits, :132 ridge for totals, :154 stack members; weights and conformal quantiles come from pipeline/18_export_stack_weights.py via backend/stack_weights.json, computed from out-of-fold predictions, lines 33-54).
* Hard-coded numbers that are NOT generated: service.py:229 source string ("36 OECD/EU economies; cross-validated MAE 3.8 pp ... 1.8 pp with history"): 3.8 matches expG (ridge cold start 3.82), but the economy count is 30 (M3) and 1.8 belongs to the delta-ridge-with-history model that the API does not serve (the served model is the cold-start ridge). backend/main.py:356 panel labels ("36 economies", "85 economies") are correct. src/data/results.js:5-24 are hand-copied constants that match results/ today (item 62) but have no generator, so they can drift (L13).
* Honesty point (M8): for a country that is in the training panel, `recommend()` returns an in-sample XGBoost/stack fit (service.py:122-123 fit on all rows; :199-204 predicts for the same economy-year; only the kNN peers exclude the query economy, :247). The headline accuracy figures are leave-country-out, so a user querying an OECD economy will see predictions more accurate than the documented cold-start error. Add a "in training data" flag or a leave-economy-out refit.

## 7. Discrepancies, ranked by severity

### High (presentation integrity; no fabrication)
**H1. Paired cold-start gains use fold-seed 0 only; adjacent TVDs are 2-seed means.**
Code: 04_experiments_main.py:136 `if seed == 0: oof_store[k] = t` and :143-145; 06_stack_architecture.py:189 `if seed == 0: keep[n] = t` and :194-196. Paper: sec_results.tex:16 (11.34 vs 10.77 = 0.57 but gain printed 0.35), :34 (15.01 vs 13.77 = 1.24 but gain 1.33; also A16 11.34-10.53 = 0.81 vs 0.78), main_journal.tex:43 (abstract: "1.33 pp, CI 0.72-1.94"), sec_intro.tex:13, main_conference.tex:46, plus the same constant in the dashboard text. The 5-seed values (15_robustness_holm/summary / 15_robustness_holm/holm) are 1.26 (A10 stack, CI 0.68-1.84) and 0.81 (A16 stack, p_holm 0.06). 
Fix: either (a) report gains averaged over both seeds (as 21_dirichlet_neural_baselines.py:262 already does: "paired gains averaged over the two seeds"), or (b) state "fold-seed 0" next to each gain, or (c) quote the 5-seed Holm table values (1.26 [0.68, 1.84]) in the abstract. Option (c) is the most defensible.

### Medium
**M1. Headline annual significance is seed-dependent.** Rerunning the exact hybrid (XGB + CatBoost delta learners, 04_experiments_main.py:55-60) with five learner seeds (42..46) on the same split gave paired gains 0.140, 0.107, 0.112, 0.116, 0.104 pp with CIs [0.025, 0.277], [-0.005, 0.229], [-0.007, 0.248], [-0.0004, 0.248], [-0.008, 0.233]: only the stored seed has a CI excluding zero (mean gain 0.116). The paper's 5-seed robustness (20_robustness_holm.py:75-95) tests a different model (CLR hybrid), whose gain is negative. Also expH: XGB-delta alone gains +0.016 [-0.12, 0.14]; the gain is mostly CatBoost. Statements affected: abstract and sec_intro.tex:13 "statistically significant", sec_results.tex:11 "statistically distinguishable from zero", sec_conclusion "improves by about 0.140". Fix: report the 5-seed mean (0.12 pp) with its CI and say "marginal/not robust to the learner seed"; add the raw-delta hybrid to the Holm family.
**M3. Total-budget module description.** sec_results.tex:39 "observed, 36 economies" -> 30 economies, 716 country-years (07_total_budget/summary.json; the 6 OECD-only economies lack a %GDP total). Same wrong count in backend/service.py:229. Also disclose the near-proxy feature (Section 3) and that the "income-group mean" row equals the global mean (all but one economy are high income). 
**M4. A16 stack TVD "3.51" (sec_results.tex:32)** vs 3.5046 in 04_stack_architecture/summary.json and 3.50 in tab_E_hist.tex. Fix: 3.50 (use a macro).
**M5. "Persistence was the best method at every horizon" (sec_results.tex:44; main_conference.tex:48).** In 09_multi_year_projection/summary A16 h=1 the oracle recursive model has TVD 2.804 < persistence 2.916 (gain +0.112, CI -0.13..0.45, not significant). The text itself notes the oracle is "at best equal at h=1", so the fix is to say "best deployable method" or "no method significantly beats persistence".
**M6. Sign convention in the institutional-feature results (sec_results.tex:52).** "the TVD change was -0.02 pp for fiscal rules" reads as TVD falling (improvement); 18_institutional_features/manual_summary reports gain = base - spec = -0.024, i.e. TVD rose from 14.099 to 14.123. Same for "annual changes between -0.02 and -0.004". Fix: "TVD increased by 0.02 pp" or "gain -0.02 pp".
**M7. "A significant 0.96 pp (0.25-1.69) on A10" for single XGBoost (sec_results.tex:34)** is an uncorrected seed-0 CI; the same paper reports (sec_results.tex:50) that XGBoost vs peer does not survive Holm (p_holm 0.06 on A10, 0.17 on A16). Fix: add "uncorrected" or drop "significant".
**M8. API in-sample predictions** (Section 6).

### Low
* L1. sec_results.tex:4 and main_conference.tex:40: "All 775 country-years therefore share the same sector mix" is true only for the eleven synthetic sectors (the four real sectors vary). Add "among these eleven". 01_legacy_audit/legacy_structure.json reports `n_distinct_country_year_mixes: 22` (10_legacy_structure_audit.py:16 rounds at 1e-12, i.e. floating noise); at 1e-9 the count is 1. Use `round(9)` so the JSON agrees with the prose.
* L2. Hard-coded "Pearson r=0.998" etc. in prose are correct; no action.
* L3. Discussion (sec_discussion.tex:11) says a fairness analysis by income group and region is "not performed here", but Section Results ("Fairness audit", sec_results.tex:47; docs/08) performs it. Stale sentence.
* L4. sec_discussion.tex:8 (External validity): "results for low- and middle-income economies rest on the four WDI series only" is stale: panel A10 contains 35 middle/low-income economies (IMF).
* L5. sec_intro.tex:13: health and R&D results "across 211 economies": the health target covers 193 economies, R&D 155 (211 is the panel size).
* L6. tab_selection caption says richer specs "did not improve validation error"; PLUS_changes in the history regime does (2.269 vs 2.329) though it remains worse than persistence (2.259) (02_main_experiments/feature_spec_selection.csv).
* L7. 04_experiments_main.py:166 `np.std(ts)` (ddof=0, 2 seeds) for "SD over seeds" in tab_ablation, vs pandas ddof=1 in tab_A2; with ddof=1 the SDs are 1.41x larger. The "within about two seed SDs" statement still holds but the SDs are not comparable across tables.
* L8. LRO health R2 0.495: text 0.50 (sec_results.tex:19) vs table 0.49. "Negative R2 in some regions" is a pooled-LRO statement (09_wdi_panel_and_legacy_audit.py:119-120), not per region.
* L9. Several different XGBoost numbers for the same A10 cold-start protocol (13.93 expL, 13.96 expK/expM/expS, 14.08 expQ, 14.12 expE, 14.13 expJ) differ only by seed/run; the paper uses 13.96 in the kNN/tuning/institutional paragraphs and 14.12 in Table E_cold, and 33.4 vs 33.1 for low-income error. Add a note that single-seed (seed 0) values are used in those paragraphs, or switch to the 5-seed table.
* L10. Imputation and static income-group notes (Section 3).
* L11. Selective reporting detail: shock-aware paragraph reports the XGB variant (4.16) only; the CatBoost shock variant (4.005) was slightly better than persistence (4.072) in 08_shock_experiments/summary though worse than its own baseline (3.729).
* L12. Synthetic-driver test (17_blend_explanation/sanity.csv): precision@3 equals exactly 0.667 with sd 0 in all 20 repetitions, i.e. a ceiling of 2 of 3 drivers; fine, but the description "recovered 2 of the 3 true drivers on average" understates that it is deterministic.
* L13. src/data/results.js constants are typed by hand; generate them from results/ in 27_make_figures_tables.py to guarantee no drift.
* L14. Literature numbers in sec_related.tex (e.g. 217 countries, 15 economies, 24 observations and 1,048 synthetic points, R2 0.97 to -0.45) are external claims, not traceable to results/; their verification belongs to docs/19_reference_audit.md.
* L15. Table 3-rounding: sec_data/macros `NMasterCountries` is computed as `dq["countries"] - 1` (27_make_figures_tables.py:59) to exclude Taiwan; fine, but the manuscript phrase "217 economies x 2000-2024 plus 25 legacy-only rows" is correct only because of this subtraction; mention in a code comment.

## 8. Items I could not verify
* That hyper-parameters were never tuned on test data before the first commit: the git history of gov_common.py has a single commit; the paper's statement is consistent with all evidence but cannot be proved from code alone.
* External literature statistics (L14).
* Figures (PDF/PNG) were not inspected; only tables, macros and text.

Files written: docs/reviews/review_A_results_integrity.md (this file). Scratch scripts live in the session scratchpad, outside the repository.
