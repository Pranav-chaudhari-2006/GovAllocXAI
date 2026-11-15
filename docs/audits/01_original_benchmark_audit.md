# Senior-Reviewer Audit of GovAllocXAI v1 (paper, code, data, references)

*Scope: the v1 paper (`archive_v1_original/paper_v1/`), the three Colab notebooks (`archive_v1_original/notebooks_v1/`), the legacy dataset, the FastAPI backend, the React front-end, the 24 cited PDFs, and the Turnitin similarity/AI reports.*
*Method: every claim below was re-derived by running code on the data in this repository (`pipeline/09_wdi_panel_and_legacy_audit.py`, `pipeline/03_build_dataset.py`) or by opening the cited PDF. Numbers are reproducible; see `results/01_legacy_audit/legacy_audit.json` and `data/dataset_new/govalloc_cofog_data_quality.json`.*

**Verdict in one paragraph.** v1 is a clean engineering demo, not a publishable research result. Its headline numbers (R² > 0.99, "95.29 % accuracy") are produced by a dataset in which 11 of the 15 target columns are a fixed percentage of GDP (± a few % noise), one target is literally a copy of an input feature, and the validation protocol written in the paper is not the one executed in the notebooks. The model has therefore *not* learned "complex budget-allocation patterns": eleven of the fifteen targets are fixed multiples of a single series (identical sector mix in all 775 rows), so it has learned to multiply GDP by a constant. None of this is fixable by rewriting text: it required a new, real-target dataset and a new evaluation design, which is what v2 delivers.

Severity legend: **S1** invalidates a headline claim · **S2** serious methodological/ethical flaw · **S3** weakness a reviewer will penalise · **S4** minor/presentation.

---

## 1. Findings on the data

| # | Sev | Finding | Evidence |
|---|-----|---------|----------|
| D1 | **S1** | **Target leakage.** `healthcare_usd` is *identical* (ratio = 1.000000, std 0) to the input feature `health_expenditure_usd`, which is in the 18-feature list of every notebook and of the backend. | `01_legacy_audit/legacy_audit.json → healthcare_equals_feature_health_expenditure = true`. |
| D2 | **S1** | **11 of 15 sector targets are exact fixed multiples of ONE latent series.** Relative to agriculture they are exactly infrastructure 2.0×, rural development 0.875×, social welfare 3.0×, energy 1.25×, transport 1.5×, housing 1.125×, water 0.75×, environment 0.625×, digital 0.5×, industry/MSME 0.875× (standard deviation of the ratio ≈ 1e-12). Hence **every one of the 775 country-years has the identical 11-sector mix**; there is no allocation pattern to learn. The common latent series is ≈ 16.7 % of GDP (CV 2.8 %) and correlates r = 0.84 with GDP growth. A one-parameter formula `k × GDP` scores R² = 0.9997 on these sectors versus 0.9991 for XGBoost (USD scale): **ML does not beat multiplying GDP by a constant**. On the share-of-GDP scale a constant predictor scores R² ≈ 0. | `01_legacy_audit/legacy_audit.json`, `01_legacy_audit/legacy_structure.json`, Fig. 3 of paper v2. |
| D3 | **S1** | **12 identical column pairs.** `defence = sdg16`, `education = sdg4`, `healthcare = sdg3 = health_expenditure`, `agriculture = sdg2`, `energy = sdg7`, `water = sdg6`, `environment = sdg13`, `rural_development = industry_msme = sdg8`. The "SDG-aligned overall model" therefore re-labels the same numbers; its R² is not independent evidence. | `identical_column_pairs`. |
| D4 | **S1** | **Provenance statement is wrong in both directions.** The paper says the data is "not drawn row-for-row from World Bank … releases". In fact the *features* (GDP, population, life expectancy, growth, unemployment, internet) match the live World Bank API **exactly** (relative error 0 on all 750 matched rows), and the `defence`, `education` and `R&D` columns equal official WDI ratios to ~1e-13. Only the other ~11 sector columns are fabricated (fixed ratios + noise). The honest description is "real macro features + 4 real sector series + 11 synthetic sector series". | `govalloc_cofog_data_quality.json → legacy_vs_real`; `expC … legacy_vs_official`. |
| D5 | S2 | Targets are modelled in **absolute USD**. Tree ensembles cannot extrapolate, so the largest economies are systematically under-predicted (the paper's own Fig. 2 and Fig. 5 show this "saturation") and R² is dominated by 3–4 giant economies (USA, China, Japan). Shares of the budget are the scale-free, policy-relevant target. | Paper Figs 2, 5; v2 uses shares. |
| D6 | S2 | 25 Taiwan rows are not a World-Bank economy (no WDI counterpart); country strings contain typos (`Neatherland`, `Phillipines`, `Saudi arabia`). 31 countries are 80 % high/upper-middle-income → no low-income representation, contradicting the "global" framing. | Legacy file. |
| D7 | S3 | Column `social_welfare_freebies_usd` uses the politically loaded word "freebies"; unacceptable in a government-facing journal paper. v2 uses COFOG "social protection". | — |
| D8 | S3 | The SDR-2026 SDG-index workbook is shipped in `dataset/` and cited as a source, but **no SDG indicator is used anywhere** – SDG alignment is a hand-made 15-row lookup table. | Notebooks, paper §III-C. |
| D9 | S3 | In the legacy file the sum of the 15 sectors is 2.8x tax revenue on average but ranges 0.19-30x (std 3.07): the 'total budget' is not tied to any fiscal identity, so the 'total-budget predictor' predicts the sum of a synthetic generator, not a budget constraint. | Summary of `Σ sectors / tax_revenue_usd`. |

## 2. Findings on methodology and implementation vs. what the paper says

| # | Sev | Finding | Evidence |
|---|-----|---------|----------|
| M1 | **S1** | **Paper protocol ≠ executed protocol.** The paper (Tables, Section IV-A, abstract) claims a *temporal* split (train 2000–2019, test 2020–2024). All three notebooks use `train_test_split(test_size=0.20, random_state=42)` — a **random** row split, which leaks the same country's neighbouring years into the test set; the backend does the same. The paper's headline numbers cannot have come from the described protocol. | `archive_v1_original/notebooks_v1/*.ipynb`, `backend/main.py:128`. |
| M2 | **S1** | **Headline numbers are not reproducible from shipped artifacts.** The notebooks' own `ML_Model_Performance` sheet reports R² = 0.9278 and MAPE = 11.92 %, whereas the paper reports R² = 0.9952 and "accuracy" = 95.29 %. "Accuracy (%)" for regression is never defined (apparently 100 − MAPE). The front-end shows yet another set (`sdgAlignedOverallR2 = 0.9823` vs paper 0.9035; `autonomousAllocationR2 = 0.9051` vs paper 0.9013). | `ML_Model_Performance` sheet; `src/data/demoData.js:36-38`. |
| M3 | **S1** | **No baselines.** The paper itself admits "no baseline other than the three compared configurations". A reviewer will immediately ask for persistence (last year's budget – the actual practice in government), country-mean, peer-group mean and linear models. In v2, persistence is a *very* strong baseline (TVD 3.6 pp); a paper that omits it overstates ML value. | v2 `expA1`. |
| M4 | S2 | **Configuration drift between paper and code.** Paper: ExtraTrees `n_estimators = 50, max_iter = 15`; code: `n_estimators = 10, max_depth = 8`. Paper: SLSQP `maxiter = 500, ftol = 1e-9`; code: `maxiter = 300, ftol = 1e-8`. Backend XGBoost: 100 trees / depth 5 / lr 0.08 vs paper 500 / 6 / 0.03. The "MICE imputation" is applied to a dataset with **0 missing cells** (paper's own Table), i.e. it is a no-op that is nonetheless listed as a methodological contribution. | Notebook cells; paper Table III. |
| M5 | S2 | **"LIME" is not LIME.** The code hand-rolls a Gaussian-noise (σ = 0.1 in standardised space) weighted Ridge surrogate. That is a single-scale local linearisation; it has no kernel-width tuning, no feature selection, no discretisation, and no stability analysis. Calling it LIME in a journal paper is a misnomer (it is "LIME-style"). v2 uses the reference `lime` package and reports agreement/stability/faithfulness. | `backend/main.py:260-277`. |
| M6 | **S1** | **XAI is promised but not delivered.** Title/abstract say "Explainable"; the paper's own Limitations say "SHAP and LIME are designed but not yet fully evaluated". One SHAP waterfall of one prediction exists — and its **largest attribution is the leaked feature** `health_expenditure_usd` (−1.0 × 10¹¹ USD, front-end `BENCHMARK_XAI_RESULT`), i.e. the explanation *advertises* the leakage. No faithfulness, stability, or human evaluation. | `src/data/demoData.js:330-340`. |
| M7 | S2 | **"Hybrid" = 50/50 mean of two GBDT models.** It is not an architecture; it is an unweighted ensemble, and the paper reports it *worse* than XGBoost on its own accuracy metric (89.11 vs 95.29). No ablation, no justification of weights, no diversity analysis. Claiming a "hybrid framework" in the title is not supported. | Paper Table IV. |
| M8 | S2 | **'Total-budget predictor' and 'autonomous allocation system' (R² 0.90–0.91)** are reported without a reproducible, single traceable path from the shipped notebooks to the table values (the notebooks contain SLSQP allocation cells, but with different settings than Table III and no evaluation of the reported R² values). In the synthetic data the total is the sum of the sector columns. The stress-test figures (−15 % GDP, +12 % inflation, +35 % debt, '100 % compliance') are described as 'reported by the pipeline description': 'compliance' is never defined and the Monte-Carlo (100 runs) has no stated distribution. | Notebooks; paper §V-E. |
| M9 | S2 | **No uncertainty quantification.** Single point estimates, one seed, no confidence intervals, no significance test. | — |
| M10 | S2 | **Tuning on the test set / no validation split.** "Training and hyper-parameter tuning" are both said to use the 620 training rows without any inner validation protocol. | Paper §IV-A. |
| M11 | S3 | The inter-sector correlation matrix (r̄ = 0.97, Fig. 3 of v1) is presented as a result; for 11 sectors r = 1.000 exactly because they are multiples of each other, and for the rest it reflects the common GDP scale. | `expC`, `expC2`. |
| M12 | S3 | Reproducibility: notebooks depend on `google.colab.files.upload`, three notebooks duplicate cells, there is no environment file, no ML unit test, no random-seed policy. | Notebooks. |
| M13 | S3 | The sector-to-SDG mapping (Defence → SDG 16, R&D/Transport/Digital → SDG 9) is arbitrary, un-validated and not tied to any official SDG indicator or UN statistical crosswalk. v2 anchors sectors to the UN COFOG classification and treats SDGs as a reporting layer only. | Paper Table II. |

## 3. Findings on the literature survey and references

All 27 *research* references were opened and checked against the PDFs in `literature/base_papers/`: **no fabricated references were found** — DOIs, journals, years and first authors match. The problems are relevance and writing:

| # | Sev | Finding |
|---|-----|---------|
| L1 | S2 | **Citation padding.** Nine references (r20–r27, r5, plus r4, r10, r11 used rhetorically) have nothing to do with ML-based budget allocation: Islamic funds & SRI (r25), CSR/ESG double-materiality (r24), farmland green production (r21), SDG-11 digital technologies (r22), biodiversity-finance bibliometrics (r26), gender split of Spanish research grants (r27), Indonesian village funds (r20), PAYG pension reserve funds (r5), peer-to-peer energy coefficients (r4). A Q1 reviewer reads this as "survey filled up to a number". |
| L2 | S2 | **Duplicated paragraph.** Section II-A repeats the XGBoost/CatBoost/"Beyond the public sector…" sentences twice in succession (lines 26 of `body.tex`) – a visible copy-paste defect that also inflates self-similarity. |
| L3 | S2 | **Missing the genuinely closest work.** Cross-country *functional* (COFOG) spending, Gür et al. 2025 (Türkiye budget forecasting, ML + DL), Guerrero & Castañeda 2022 (SDG gaps vs. spending, 140 countries), Radulescu et al. 2015 (functional spending by NN), Valle-Cruz et al. (multi-objective), Yao & Zhu 2025 (SHAP-interpretable hospital budget) are not engaged. Positioning is therefore incomplete. |
| L4 | S3 | Several citation claims are stated more strongly than the sources (e.g. "XGBoost beat human experts in three of four account groups", "ensembles outperform classical baselines" generalised across 13 papers); they were not all re-verified and should be softened or checked against the full text. |
| L5 | S3 | Reference formatting: `Chand and Zhang` has no initials; Romanian diacritics (`Drăgulin`, `Ștefan`) were destroyed; `Result.in Eng.` abbreviations inconsistent. 5 dataset references (WDI, GFS, HDR, GHO, FAOSTAT) are cited as sources though IMF-GFS, UNDP-HDR, WHO-GHO and FAOSTAT were never actually used. |
| L6 | S3 | Dates: 2026-dated journal articles are cited in a document submitted 16 Oct 2026 – acceptable only if the volumes were truly online; I verified their DOIs resolve to the PDFs you provided. |

## 4. Findings on the engineering artefacts

| # | Sev | Finding |
|---|-----|---------|
| E1 | S2 | Front-end displays "exact reported metrics" next to synthetic "demo" data; a viewer can mistake demo values for model output. Four numbers disagree with the paper (see M2). |
| E2 | S2 | Backend trains on the leaky 18-feature set with a random split, so the live SHAP page's top driver for healthcare is the label itself. |
| E3 | S3 | CORS regex allows every `*.onrender.com` origin with credentials; no rate-limit; model retrained at every cold start. |
| E4 | S3 | `README` refers to `dataset/ML_Budget_Dataset_WorldBank_Completed (1).xlsx` – a file name that a download dialog produced. |

## 5. Plagiarism / AI-writing reports

* **Similarity 4 %** (all "Not cited or quoted", ten sources < 1 % each): well within acceptable limits (< 15 %); nothing to fix except removing the duplicated paragraph (L2).
* **AI writing: marked `*%` (< 20 % threshold)**: Turnitin deliberately suppresses scores below 20 %. Do not read this as 0 %: the v1 prose is regular and could be flagged by stricter detectors. v2 text is rewritten to report numbers, uncertainty and limitations in the authors' own analytic voice; run it through your institution's checker before submission.

## 6. What a Q1 reviewer's decision would have been on v1

*Reject* (or "major revision, new data required"). The three fatal items: **D1/D2/M1** (leakage, trivial target, protocol mismatch). Everything else is repairable. v2 addresses all S1/S2 items; see `docs/02_Literature_Gap_and_Base_Papers.md` for positioning and `docs/03_Expert_Panel_Recommendations.md` for what was added.

## 7. Claims in v1 that were *true* (credit where due)
* Reference list is real; the temporal split *idea* was right (just not executed).
* Limitations section already admitted synthetic origin and unevaluated XAI.
* Human-in-the-loop framing ("AI → policy review → human approval") is correct and is kept as the core of v2.
