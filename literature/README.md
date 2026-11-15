# Literature Survey Index — what is here, which are the BASE papers, and why

*Checked 14 Nov 2026. Two folders: `01_cited_in_paper_v1/` (24 PDFs cited or collected for the v1 paper) and `02_downloaded_similar_work/` (12 PDFs: 10 downloaded + 2 added manually). The gap analysis is in `docs/02_Literature_Gap_and_Base_Papers.md`.*

## A. The three BASE papers (anchor the novelty claim)
| # | Paper | File | Why it is a base paper |
|---|---|---|---|
| **Base 1** | Santschi, Grau, Fehrenbacher, Blohm (2024) *Artificial Intelligence to Improve Public Budgeting*, ICIS 2024 | `01_cited_in_paper_v1/ArtificialIntelligencetoImprovePublicBudgeting (1).pdf` | Same learners (XGBoost/CatBoost), same motivation (AI assisting budget experts); one country, account groups, no XAI evaluation |
| **Base 2** | Gür, Yıldız, Ünal (2025) *Advanced AI Models for Future Forecasting of Budget Expenditures via ML and DL*, Panoeconomicus | `02_downloaded_similar_work/Gur_2024_Turkey_Budget_Expenditure_Forecast_Panoeconomicus.pdf` | Forecasting budget expenditure through crisis periods; aggregate, one country |
| **Base 3** | Guerrero & Castañeda (2022) *How does government expenditure impact sustainable development?*, Sustainability Science | `02_downloaded_similar_work/Guerrero_Castaneda_GovExpenditure_SDG_Agent_RL.pdf` | 140-country, SDG-linked view of public spending; outcome side, not allocation recommendation |

## B. Closest similar work (downloaded) — `02_downloaded_similar_work/`
| File | What it is | Relation to GovAllocXAI |
|---|---|---|
| `Nonato_2024_UnB_Brazil_Budget_Function_XGBoost_Optimisation_Dissertation.pdf` | Master's dissertation (Portuguese), University of Brasília: "Alocação orçamentária inteligente de recursos públicos" — Brazilian federal budget by function 2000–2023, XGBoost + Bayesian optimisation | **Closest functional-allocation + optimisation precedent**; single country, N≈24 years, small-data limits that our panel addresses. (A journal version exists; not retrieved.) |
| `Radulescu_2015_Forecasting_Public_Expenditure_FeedForward_NN.pdf` | Rădulescu, Banica, Zamfiroiu (2015), Economic Research-Ekonomska Istraživanja | Forecasts public expenditure by function with feed-forward NNs for 4 CEE economies; pre-boosting era, no XAI |
| `Afonso_2025_AI_Fiscal_Transparency_Brazil_COFOG.pdf` | IMF PFM blog on Brazil's Treasury classifying spending into COFOG with CNN/RNN | Shows COFOG is the operational standard and AI is entering public finance; classification, not allocation |
| `Informatica_candidate_7981.pdf` | Yao & Zhu (2025), SHAP-interpretable public-hospital budget cost prediction | SHAP in a budgeting task (micro level) |
| `Cambodia_Public_Expenditure_Hybrid_ML.pdf` | Hybrid ARIMA–RF / XGBoost for monthly government expenditure, Cambodia | Boosting beats ARIMA on aggregate spending; single country |
| `Peru_Fiscal_Policy_SHAP_IJACSA2025.pdf` | Peru fiscal-policy variables → economic growth with ML + SHAP | SHAP on fiscal variables; outcome is growth |
| `arXiv_2508.06060_LLM_ParticipatoryBudgeting.pdf` | LLMs for participatory-budgeting resource allocation | Allocation under constraints with LLMs; different problem (project selection) |
| `Tekbas_2026_BMC_PublicHealth_WDI_Panel_Health_Expenditure.pdf` | Tekbaş & Aktepe (2026), BMC Public Health: ML on WDI panel (health/economy/environment indicators) | Background: same data source (WDI panel) and ML comparison; not about budget allocation |

## C. Papers cited in v1 (`01_cited_in_paper_v1/`) and what to do with them
All 24 were opened: **every one exists and matches its DOI/venue**.

| Verdict | Papers |
|---|---|
| **Keep — on topic** | Caravaggio et al. 2025 (*Predicting policy funding allocation*), Di Stefano & Resce 2025 (*missed funding*), Chand & Zhang 2022 (NDIS), Valle-Cruz et al. 2022 (*From e-budgeting to smart budgeting*), Dragulin et al. 2025 (*AI-driven models for forecasting public expenditures*), Nzazi et al. 2025 (*AI for public expenditure analysis in low-income countries*), Nguyen et al. 2026 (*Towards SDGs: government expenditure*), Santschi et al. 2024 (Base 1) |
| Keep as a single XGBoost-SHAP template | Zhang 2026 (*digital transformation and enterprise performance: XGBoost-SHAP*) |
| Analogy only — compress or drop | Cheng & Feng 2026 (green TFP), Ren et al. 2026 (crop irrigation), Madrigal et al. 2026 (energy allocation coefficients), van Eekelen et al. 2026 (PAYG pensions), Costa et al. 2026 and Wang et al. 2026 (disaster-funding) |
| **Padding — removed from v2** | Islamic funds & SRI; CSR/ESG double materiality; farmland green production; SDG-11 digital technologies; emerging technologies for SDGs; biodiversity-finance bibliometrics; gender split of Spanish research grants; Indonesian village funds; district-level SDG/public-spending (Assam); oasis ecosystem services |

## D. Added manually by the authors (15 Nov 2026)
| File | Paper | Relation |
|---|---|---|
| `Yang_2023_GRU_Government_Expenditure_15_Economies_Mathematics.pdf` | Yang, Molefyane, Lin (2023), *The Forecasting of a Leading Country's Government Expenditure Using a Recurrent Neural Network with a Gated Recurrent Unit*, Mathematics 11(14):3085 | GRU forecasting of total government expenditure for 15 large economies (1990–2020); aggregate, no functional split, no XAI |
| `OECD_2023_WKP38_Government_Spending_Reallocation_COFOG.pdf` | Barnes, Cournède, Pascal (2023), *Do governments re-prioritise spending? First insights from COFOG data on public spending reallocation in OECD countries*, OECD Economics Department Working Paper No. 1785 (ECO/WKP(2023)38) | Descriptive evidence on how OECD governments reallocate across COFOG functions and when (crises); supports our shock/reallocation framing; no prediction model |

Still not retrieved: the journal version of the Brazilian budget-function XGBoost + Bayesian-optimisation study (the Nonato dissertation above is the thesis form).

## E. How to cite in the paper
All entries are in `papers/references.bib` and were checked against these PDFs or the publisher page. The paper's related-work section and Table "gap" use B1–B8 above; the claim of novelty is conditional on repeating the search on Scopus/Web of Science (queries in `docs/02_Literature_Gap_and_Base_Papers.md`).
