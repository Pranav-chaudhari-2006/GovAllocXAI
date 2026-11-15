# Literature, base papers and novelty search

Gap analysis, base papers, search protocol and results, Crossref proxy search, public-finance reading notes.


---

## A. Literature gap and base papers

*Index of every PDF with its role: `literature/README.md`. Search date: 14 Nov 2026. Method: web search (Google-style) + direct PDF retrieval. Eleven query strings were used (listed in §5). "Not found" below means **not found by this search**, not a proof of absence — before submission you must repeat the search on Scopus / Web of Science / IEEE Xplore with the strings in §5 and cite anything new.*

## 1. Is the v1 literature survey aligned with the research problem?

**Partly. 14 of 27 references are on-topic; 13 are weakly related or padding.**

| Group | v1 refs | Verdict |
|---|---|---|
| Boosted trees for public-money prediction (Caravaggio, Santschi, Chand & Zhang, Di Stefano & Resce, Valle-Cruz, Dragulin, Nzazi) | r3, r6–r9, r12, r13 | **On topic – keep** |
| XAI methods and XGBoost-SHAP template (Lundberg, Ribeiro, Zhang 2026, Cheng & Feng, Ren et al.) | r14–r18 | Method refs OK; r17 and r18 (green TFP, crop irrigation) are *application* papers in unrelated fields – keep one as "template", drop the other |
| SDG ↔ public spending (Nguyen et al. 2026) | r19 | **On topic – keep** |
| Energy-allocation XGBoost; PAYG pension; disaster funds | r4, r5, r10, r11 | Analogy only; compress to one sentence or drop |
| Islamic funds, CSR/ESG, biodiversity finance, village funds, farmland, SDG-11 tech, gender grants | r20–r27 | **Padding – remove** (none of them predicts or explains budget allocation) |
| Dataset "references" (IMF-GFS, UNDP-HDR, WHO-GHO, FAOSTAT) | r29–r32 | Never actually used → remove; v2 cites the sources that *were* used (WDI, WGI, Eurostat COFOG, OECD COFOG) |

All 24 PDFs you stored were opened: **every cited paper exists and its DOI/venue matches** (no fabricated reference). Full list moved to `literature/base_papers/`.

## 2. Closest prior work – and why GovAllocXAI v2 is different

Downloaded to `literature/related_work_pdfs/` (PDFs) or already in `01_cited_in_paper_v1/`:

| # | Work | What it does | What it does **not** do (our gap) |
|---|---|---|---|
| **B1** | **Gür, Yıldız & Ünal (2025), *Panoeconomicus*** – "Advanced AI models for future forecasting of budget expenditures via ML and DL" (PDF ✓) | One country (Türkiye), monthly **aggregate** budget expenditure 2008–2024, ML + DL time-series forecasting | No sector/functional split, no cross-country panel, no allocation constraints, no explainability |
| **B2** | **Santschi, Grau, Fehrenbacher & Blohm (2024), ICIS** – "AI to improve public budgeting" (PDF ✓, in survey) | XGBoost/CatBoost vs. human experts on Swiss cantonal account groups; human–AI collaboration | One country, account groups not COFOG functions, **no XAI evaluation**, no allocation |
| **B3** | **Guerrero & Castañeda (2022), *Sustainability Science*** – SDG development gaps vs. spending, 140 countries (PDF ✓) | Agent-based/complexity model of *how spending moves SDG indicators* | Models outcomes of spending, **does not predict or recommend how a budget is split**; no ML explanation |
| B4 | Yao & Zhu (2025), *Informatica* – SHAP-interpretable hospital budget cost prediction (PDF ✓) | RF/XGBoost + SHAP for a single hospital | Micro-level, not government, no allocation |
| B5 | Rădulescu, Banica & Zamfiroiu (2015), *Econ. Res.-Ekon. Istraž.* | Feed-forward NNs forecasting public expenditure **by function** for 4 CEE countries (PDF ✓ downloaded) | 4 countries, pre-boosting era, no XAI, no composition-aware evaluation |
| B6 | Valle-Cruz et al. (2022), *GIQ* (PDF ✓, in survey) | NN + NSGA-II on 217 countries: which expenditure strategies relate to the Gini index | Predicts outcomes of strategies, not sector shares; no per-decision explanation |
| B7 | Dragulin et al. (2025), *Electronics* (PDF ✓, in survey) | TCN/LSTM/GRU vs SARIMA/VAR for expenditure forecasting | Aggregate time-series, no allocation, no XAI |
| B8 | Peru fiscal-policy + SHAP (IJACSA 2025), Cambodia hybrid ARIMA-RF (IJEFI 2026) (PDFs ✓) | SHAP / hybrid ML on single-country macro series | Single country, outcome = growth or aggregate spending |
| B9 | Nonato (2024), University of Brasília MSc dissertation (Portuguese), *Alocação orçamentária inteligente de recursos públicos*: Brazilian federal budget by function 2000–2023, multi-output XGBoost + Bayesian-optimisation search (PDF ✓ downloaded; the journal version was **not** retrieved) | Single country, N = 24 years, poor R² on 2 of 3 outputs | Illustrates the small-N limit that our multi-country panel overcomes |
| B10 | Brazil STN – AI classifies expenditure into COFOG (IMF PFM blog, PDF ✓) | NLP classification of records into COFOG codes | Classification of *past* records, not forecasting/allocation |

**Defensible novelty statement (v2):** *to the best of our search*, no published study (i) predicts the **composition** of general-government expenditure across **COFOG functions** for a **multi-country panel (36 economies, 2000–2024)** using **officially reported** targets, (ii) evaluates it under **temporal, leave-country-out and shock-period** protocols against the **persistence/peer baselines that practitioners actually use**, (iii) wraps predictions in a **bounded allocation engine**, and (iv) evaluates **SHAP and LIME quantitatively (agreement, stability, deletion-faithfulness)** – together with (v) a forensic audit that shows how an apparently excellent result (R² > 0.99) arises from a synthetic target. Items (iv) and (v) are what most distinguish the paper from B1–B8.

**What we explicitly do NOT claim** (a reviewer will test these): "first ML budget model", "ML beats persistence" (our result: it does so only marginally on one-step-ahead forecasts – see paper), "causal effects of indicators on budgets", "ready for operational use".

## 3. Three base papers to anchor the manuscript

| Role | Paper | Why it is the right anchor |
|---|---|---|
| Base 1 – ML budget forecasting vs. experts | **Santschi et al. 2024 (ICIS)** | Same learners (XGBoost/CatBoost), same motivation (human-AI collaboration), but single country and no XAI → we extend to multi-country functional shares + XAI |
| Base 2 – AI forecasting of expenditure under shocks | **Gür et al. 2025 (Panoeconomicus)** | Explicit evaluation through crisis periods (GFC, COVID) → motivates our 2020–24 shock test; aggregate-only → our functional split is the gap |
| Base 3 – spending ↔ SDGs at global scale | **Guerrero & Castañeda 2022 (Sustainability Science)** | 140-country, SDG-linked view of public spending → motivates SDG reporting layer; outcome-side only → our allocation-side model is complementary |

## 4. Suggested additions to the reference list (all verified to exist)
Gür 2025 · Guerrero & Castañeda 2022 · Yao & Zhu 2025 · Rădulescu 2015 · Rudin 2019 (post-hoc explanation risk) · Slack 2020 (LIME/SHAP can be fooled) · Alvarez-Melis & Jaakkola 2018 · Lundberg 2020 (TreeSHAP) · Kaufman 2012 (leakage) · Roberts 2017 (block CV) · Grinsztajn 2022 (trees on tabular data) · Aitchison 1986 (compositional data) · Hyndman & Koehler 2006 · Kaufmann 2011 (WGI) · UN COFOG 2000. All appear in `papers/references.bib`.

## 5. Query log (reproduce on Scopus/WoS/IEEE)
1. machine learning government budget allocation sectors explainable SHAP COFOG prediction
2. public expenditure forecasting COFOG functional spending machine learning panel countries
3. participatory budgeting allocation explainable AI SDG-aligned resource allocation decision support
4. "government expenditure" budget allocation gradient boosting SHAP cross-country panel sectoral spending education health defence prediction
5. budget allocation optimization reinforcement learning OR neural network SDG government spending prioritisation
6. multi-output XGBoost executed expenditure budgetary function allocation optimisation
Add for the final check: `TITLE-ABS-KEY(("budget allocation" OR "public expenditure") AND ("machine learning" OR "XGBoost") AND (COFOG OR "functional classification") AND (SHAP OR LIME))`.

Result of the searches: no paper that combines (i)–(iv). Related-but-different works are tabulated above.


---

## B. Novelty search report

*Date of search: 2026-11-15. Scope: novelty of GovAllocXAI v2.1 against prior literature. This report supplements `docs/02_Literature_Gap_and_Base_Papers.md` (11 queries, 14 Nov 2026).*

## 1. Method

* **Tools:** the searcher had only a general web search engine and a page fetcher. **Scopus, Web of Science, IEEE Xplore and Google Scholar were NOT accessible.** This is a proxy for a database search, not a replacement. The exact strings to run on Scopus/WoS are in section 6.
* **Queries:** 37 distinct queries (5 in "extended" mode, 32 in "standard" mode), including 6 with domain filters (arXiv, SSRN, RePEc/IDEAS, MPRA, ScienceDirect, Springer, MDPI, IEEE, PMC).
* **Coverage of topics:** ML + budget allocation; COFOG + ML/forecasting; compositional data / log-ratio / Dirichlet for budget shares; SHAP/LIME + public finance; XAI + public-sector allocation; cold-start / leave-country-out spending prediction; peer-benchmark budget recommendation; AI budgeting decision support; SDG-aligned allocation; leakage/synthetic-benchmark audits; participatory budgeting + XAI; fiscal forecasting with boosting; SHAP-vs-LIME evaluation literature.
* **Verification:** a hit is marked **verified** only if its page (publisher, RePEc/IDEAS, PMC, arXiv, university press release) was opened or its metadata was returned by the search engine for a specific bibliographic record. Otherwise "not verified". Fetches that returned 403/404 are noted. Nothing here is invented; where details are missing they are marked.
* **Verdict scale** against our six points: (i) share/composition prediction across COFOG functions on a multi-country panel; (ii) two modes (annual update / cold-start) vs practitioner baselines; (iii) bounded-simplex allocation engine; (iv) quantitative SHAP+LIME evaluation (agreement, stability, deletion-faithfulness); (v) forensic leakage audit of a synthetic benchmark; (vi) applicability/novelty score by income group. **DIRECT** = does >= 3 of them; **CLOSE** = 1-2; **ADJACENT** = same domain/method but none.

**Headline result: no DIRECT competitor was found.** Several CLOSE works cover one or two of the points, and a few strong adjacent ones will be raised by reviewers (section 4).

## 2. Query log

Mode: S = standard, E = extended. Filters in brackets.

| # | Mode | Query |
|---|---|---|
| 1 | S | machine learning government budget allocation across sectors explainable SHAP |
| 2 | S | COFOG functional classification public expenditure forecasting machine learning neural network |
| 3 | S | budget composition expenditure shares compositional data Dirichlet regression log-ratio government spending |
| 4 | S | LIME SHAP explainable public finance government spending prediction |
| 5 | E | explainable AI public sector resource allocation decision support government budget |
| 6 | S | machine learning predict health expenditure education spending military expenditure cross-country World Development Indicators random forest XGBoost |
| 7 | S | AI-assisted budgeting decision support system government budget recommendation peer countries benchmark |
| 8 | S | SDG-aligned budget allocation machine learning optimization government spending |
| 9 | S | data leakage synthetic benchmark audit public finance machine learning budget dataset R2 0.99 |
| 10 | S | participatory budgeting explainable AI allocation recommendation |
| 11 | E | fiscal forecasting gradient boosting government expenditure shares predict composition of public spending |
| 12 | S | machine learning predict government spending by function COFOG cross-country panel [arxiv, ssrn, repec] |
| 13 | S | government budget allocation machine learning explainable [ieee, sciencedirect, mdpi, springer] |
| 14 | S | defence spending share of budget prediction machine learning SHAP countries |
| 15 | S | R&D expenditure education expenditure forecasting countries machine learning cold-start new country transfer |
| 16 | E | "budget allocation" "machine learning" "government expenditure" functions optimization reinforcement learning countries |
| 17 | S | Mexican federal budget distribution artificial intelligence optimization social development economic development |
| 18 | S | OECD working paper reallocation of government spending across COFOG functions |
| 19 | E | determinants of government expenditure composition by function panel OECD machine learning random forest |
| 20 | S | forecasting government expenditure GRU leading country Mathematics 2023 Yang |
| 21 | S | spending review AI tool budget analysts explainable recommendation ministry of finance machine learning prototype |
| 22 | S | "public expenditure" "machine learning" cross-country sectoral allocation SHAP WDI health education budget share [sciencedirect, springer, mdpi, ieee] |
| 23 | S | government budget shares forecasting simplex constraint sum to one neural network softmax public spending categories |
| 24 | S | persistence baseline hard to beat incremental budgeting machine learning forecast budget shares |
| 25 | S | Fernandez-Cortez Valle-Cruz Gil-Garcia 2020 Can artificial intelligence help optimize the public budget Mexico MLP NSGA-II |
| 26 | S | Obeng 2022 determinants and interrelationship of components of government spending Review of Development Economics |
| 27 | S | smart budget allocation predictive analytics optimization Agriculture Health Education Rural Development Road Transport IJRSI 2025 |
| 28 | S | Nzazi artificial intelligence public expenditure analysis low-income countries |
| 29 | S | Caravaggio Predicting policy funding allocation with machine learning Socio-Economic Planning Sciences 2025 |
| 30 | S | Explainable machine learning for public policy use cases gaps research directions Amarasinghe Data & Policy |
| 31 | E | benchmark leakage synthetic dataset exact multiple of one variable regression perfect R2 reproducibility audit tabular ML |
| 32 | S | Korea Ministry of Planning and Budget AI fiscal planning budget allocation model dBrain explainable |
| 33 | S | "Analysis of Factors Affecting Defense Expenditures" XAI-based model |
| 34 | S | Valle-Cruz From e-budgeting to smart budgeting ... Government Information Quarterly |
| 35 | S | government expenditure by function forecasting deep learning OR random forest OR XGBoost education health social protection shares panel [ssrn, arxiv, ideas, econpapers, mpra] |
| 36 | S | LIME SHAP agreement stability faithfulness evaluation tabular explanations disagreement problem |
| 37 | S | leave-one-country-out cross-validation predict government health education spending share developing countries ML [sciencedirect, springer, mdpi, ieee, pmc] |

Page fetches (verification): IDEAS/RePEc (Adolph 2020; Caravaggio 2026; Obeng 2022; OECD WP 1785; Goulet Coulombe 2025; IJRSI), RSIS journal page (IJRSI), PMC (Lee 2026), UCentral repository (Hashemi 2024), arXiv abs 2010.14374, Albany press release (Valle-Cruz 2022), RIDE journal page (Tavera 2024), ownyourai.com summary. **Blocked (403/404), not verified by fetch:** ScienceDirect (R&D DSS paper), MDPI Electronics 2025, MDPI Systems 2026, Wiley (Obeng; verified via IDEAS instead), Doaj (Data & Policy tagging paper).

## 3. Hits and verdicts

### 3a. CLOSE (cover 1-2 of points i-vi)

| # | Title | Authors | Year | Venue | URL | Covers | Verified | Verdict |
|---|---|---|---|---|---|---|---|---|
| H1 | Analysis of Factors Affecting Defense Expenditures: An XAI-Based Model | Kisman, Uzun, Guler (Firat Univ.) | 2026 | *Systems* (MDPI) 14(3):283, doi 10.3390/systems14030283 | https://ownyourai.com/?p=45410 (vendor summary only); journal DOI above | Cross-country 2002-2023; tree models; SHAP vs PDP vs ALE compared on fidelity/faithfulness; targets = military spending as share of GDP / of government spending / per capita (classification, ROC-AUC) | Partly: bibliographic record from search; MDPI page 403; metrics seen only on a vendor summary | **CLOSE** (a quantitative XAI comparison in a single spending function; no composition, no LIME, no allocation) |
| H2 | From e-budgeting to smart budgeting: Exploring the potential of AI in government decision-making for resource allocation | Valle-Cruz, Fernandez-Cortez, Gil-Garcia | 2022 | *Government Information Quarterly* 39(2):101644, doi 10.1016/j.giq.2021.101644 | https://www.albany.edu/news-center/news/2022-exploring-potential-ai-government-decision-making | World Bank data, 217 countries 1960-2019; multilayer model + multi-objective genetic algorithm to find budget policies for GDP/inflation/inequality; names lack of explainability as a risk | Yes (press release + search metadata) | **CLOSE** (cross-country AI budget optimisation, outcome-driven; no COFOG shares, no XAI evaluation, no baselines) |
| H3 | Smart Budget Allocation in Public Policy: A Data-Driven Approach for Equitable Resource Distribution | Kaki, Srikanth, Venkatesh, Kumar | 2025 | *Int. J. Research and Scientific Innovation* 12(9):3768-3774 | https://rsisinternational.org/journals/ijrsi/article.php?id=389 ; https://ideas.repec.org/a/bjc/journl/v12y2025i9p3768-3774.html | 5 sectors, 2020-2025, linear regression forecast + constrained linear programming + dashboard; some indicators simulated | Yes (page opened) | **CLOSE** (forecast + constrained allocation + dashboard, but 1 country-level toy dataset, simulated inputs, no XAI, no baselines; low-tier venue) |
| H4 | Forecasting public expenditure by function with feed-forward neural networks (Radulescu, Banica, Zamfiroiu) | Radulescu, Banica, Zamfiroiu | 2015 | *Economic Research-Ekonomska Istrazivanja* 28(1):668-686 | https://ideas.repec.org/a/taf/reroxx/v28y2015i1p668-686.html | Functional spending forecasts, 4-5 CEE countries | Yes (record + search summary; PDF already in repo) | **CLOSE** (functional spending forecasting; no XAI, no baselines of today, tiny panel) |
| H5 | Determinants and interrelationship of components of government spending | S. K. Obeng | 2022 | *Review of Development Economics* 26(4):2414-2435, doi 10.1111/rode.12921 | https://ideas.repec.org/a/bla/rdevec/v26y2022i4p2414-2435.html | Up to 142 countries 1990-2017; COFOG-type spending shares; FE/GMM/SUR (not ML) | Yes (IDEAS page opened) | **CLOSE** (same target family and country breadth, but econometric, in-sample, no prediction/XAI) |
| H6 | The political economy of budget trade-offs | Adolph, Breunig, Koski | 2020 | *Journal of Public Policy* 40(1):25-50 | https://ideas.repec.org/a/cup/jnlpup/v40y2020i1p25-50_2.html | Compositional-data methods that build the budget constraint into models; 8 US-state spending categories 1984-2009 | Yes | **CLOSE** (compositional/budget-constraint modelling of shares; econometric, US states, no ML/XAI) |
| H7 | Alocacao orcamentaria inteligente de recursos publicos (Nonato) | Nonato | 2024 | MSc dissertation, Univ. of Brasilia | already in `literature/related_work_pdfs/` | Brazil federal budget by function, XGBoost + Bayesian optimisation | In repo (not re-fetched now) | **CLOSE** (single country, N~24) |

### 3b. ADJACENT (same domain or method, none of i-vi in substance)

| # | Title | Authors | Year | Venue | URL | Relevance | Verified |
|---|---|---|---|---|---|---|---|
| A1 | Do governments re-prioritise spending? First insights from COFOG data on public spending reallocation in OECD countries | Barnes, Cournede, Pascal | 2023 | OECD Economics Dept WP No. 1785, doi 10.1787/56dda017-en | https://ideas.repec.org/p/oec/ecoaaa/1785-en.html | COFOG 1996-2017: reallocation is small, health/social rarely cut; backs the "persistence is hard to beat" finding | Yes |
| A2 | The determinants of health expenditure: a machine learning approach | Caravaggio, Lagravinese, Resce | 2026 | *Empirical Economics* 70(2) | https://ideas.repec.org/a/spr/empeco/v70y2026i2d10.1007_s00181-025-02854-6.html | Gradient boosting best out of sample for Italian NHS regional health spending; "distribute national health funds" | Yes |
| A3 | Panel Machine Learning with Mixed-Frequency Data: Monitoring State-Level Fiscal Variables | Goulet Coulombe, Marcellino, Stevanovic | 2025 | CIRANO/UQAM WP 25-04 | https://ideas.repec.org/p/bbh/wpaper/25-04.html | Pooled panel neural nets beat linear models for US state expenditures/deficits (levels, not shares) | Yes |
| A4 | Explainable ML framework with Granger-based temporal predictive validation for monitoring fiscal risk in national health insurance expenditure | Gwangsu Lee | 2026 | *PLoS One* 21(10):e0361904 | https://pmc.ncbi.nlm.nih.gov/articles/PMC13719042 | LightGBM+SHAP on Korean health-insurance spending; autoregressive baselines gave the best short-term forecasts (mirrors our persistence result) | Yes |
| A5 | A User-Centric Exploration of Axiomatic Explainable AI in Participatory Budgeting | Hashemi, Darejeh, Cruz | 2024 | UbiComp Companion '24 (ACM), pp.126-130 | https://pure.ucentral.cl/es/publications/a-user-centric-exploration-of-axiomatic-explainable-ai-in-partici/ | XAI for PB allocation as axioms-as-constraints; pilot user study; project selection, not budget composition | Yes |
| A6 | Explainable Machine Learning for Public Policy: Use Cases, Gaps, and Research Directions | Amarasinghe, Rodolfa, Lamba, Ghani | 2023 | *Data & Policy* 5:e5, doi 10.1017/dap.2023.2; arXiv 2010.14374 | https://arxiv.org/abs/2010.14374 | Frames XAI user needs in public policy; mentions LIME/SHAP | Yes |
| A7 | The Disagreement Problem in Explainable Machine Learning: A Practitioner's Perspective | Krishna, Han, Gu, et al. | 2022 (arXiv) | arXiv 2202.01602 | https://arxiv.org/pdf/2202.01602 | Defines/measures disagreement between LIME/SHAP/etc.; our SHAP-LIME agreement metrics should cite it | Search record only (not opened) |
| A8 | The Forecasting of a Leading Country's Government Expenditure Using a Recurrent Neural Network with a Gated Recurrent Unit | Yang, Molefyane, Lin | 2023 | *Mathematics* 11(14):3085, doi 10.3390/math11143085 | https://ideas.repec.org/a/gam/jmathe/v11y2023i14p3085-d1192712.html | World Bank aggregate expenditure, 15 largest economies, GRU vs ARIMA/SVR/XGB/CNN/LSTM | Yes (record + abstract via search) |
| A9 | Advanced AI Models for Future Forecasting of Budget Expenditures via ML and DL | Gur, Yildiz, Unal | 2025 | *Panoeconomicus* | https://panoeconomicus.org/index.php/jorunal/article/view/2307 | Base 2; aggregate, Turkiye | Yes (listed; PDF in repo) |
| A10 | AI-Driven Models for Forecasting Public Expenditures in the Digital Era | Dragulin et al. | 2025 | *Electronics* 14(20):4047 | https://www.mdpi.com/2079-9292/14/20/4047 | Aggregate time-series | Search record only (403) |
| A11 | Nowcasting R&D Expenditures: A Machine Learning Approach | (authors not captured) | 2024 | arXiv 2407.11765 | https://arxiv.org/abs/2407.11765 | Cross-country neural net with country embeddings for GERD in 8 countries; a single function | Search record only |
| A12 | Predicting policy funding allocation with Machine Learning | Caravaggio, Resce, Vaquero-Pineiro | 2025 | *Socio-Economic Planning Sciences* 98, doi 10.1016/j.seps.2025.102175 | https://ideas.repec.org/a/eee/soceps/v98y2025ics0038012125000242.html | Predicts EU-fund recipients (Italy); allocation across actors, not sectors | Yes (record via search) |
| A13 | A decision support framework for robust R&D budget allocation using machine learning and optimization | (authors not captured) | 2019 | *Decision Support Systems* (doi 10.1016/j.dss.2019.03.010) | https://www.sciencedirect.com/science/article/pii/S0167923619300569 | ML prediction + robust optimisation splitting a national R&D budget (Korea); optimisation of outcome, no XAI | Search record only (403) |
| A14 | Brazil STN: AI classifies subnational spending into COFOG | IMF PFM blog (Afonso) | 2024 | IMF PFM Blog | https://blog-pfm.imf.org/en/pfmblog/2024/12/ai-is-enhancing-fiscal-transparency-in-brazil | Classification of records, not allocation | Yes |
| A15 | Policy Prioritization Inference / budgeting for SDGs (Guerrero, Castaneda; Guariso et al.) | Guerrero, Castaneda et al. | 2021-2023 | *Socio-Economic Planning Sciences* (2021); UN WPSR 2023; *Data & Policy* 2023 | https://publicadministration.desa.un.org/sites/default/files/publications/2023/16_%20WPSR%202023%20Omar%20A_%20Guerrero%20and%20Gonzalo%20Castaneda.pdf | SDG-aware optimal allocation of Mexican federal transfers (agent-based); closest "SDG-aligned allocation" work | Search record; not opened in full |
| A16 | Efficient budget allocation in Mexico (Asignacion eficiente del presupuesto en Mexico) | Tavera Cortes, Torres Sandoval, Sandoval Gomez | 2024 | RIDE 14(28), doi 10.23913/ride.v14i28.1764 | https://ride.org.mx/index.php/RIDE/article/view/1764 | Qualitative/conceptual; not ML | Yes (opened) |
| A17 | Komitee Equal Shares (Yang, Scheurer); LLMs for resource allocation via PB (Damle) | various | 2025 | arXiv 2510.02040; arXiv 2508.06060 | https://arxiv.org/html/2510.02040v1 ; https://arxiv.org/html/2508.06060v1 | Explainable proportional PB algorithm; LLM allocator benchmark | Search records only |
| A18 | Korea MoPB AI budget assistant; UK Treasury AI tool; Sweden ESV explainable GDP ML | news/official | 2026 / 2025 | Korea Times, OECD.AI | https://www.koreatimes.co.kr/southkorea/20260430/budget-ministry-turns-to-ai-to-help-steer-fiscal-planning | Practice evidence that ministries adopt AI for budgeting; no published methods | News only |
| A19 | TabReD (SULFUR target-as-feature case); ERP-RiskBench leakage-safe protocols | various | 2024 / 2026 | arXiv 2406.19380; arXiv 2603.06671 | https://arxiv.org/pdf/2406.19380 | Precedents for benchmark-leakage findings in tabular ML (not public finance) | Search records only |
| A20 | The Cambodia hybrid ML study; Peru SHAP; Yao & Zhu hospital budgets; Tekbas & Aktepe WDI panel | various | 2025-2026 | IJEFI; IJACSA; Informatica 7981; BMC Public Health | in repo | Already cited | In repo |

### 3c. Not found / not verifiable
* "Nzazi et al. 2025, AI for public expenditure analysis in low-income countries" (cited in v1 survey): **no record found by the search engine in query 28.** The repo's own survey says the PDF was opened; keep as is but re-check DOI.
* No paper was found that does all of: share prediction across COFOG + peer baselines + XAI evaluation + audit (queries 1, 2, 4, 11, 12, 35).
* No paper found auditing leakage of a *public-finance* synthetic benchmark (query 9, 31); only generic tabular precedents (A19).
* No paper found doing leave-country-out *cold-start* prediction of spending shares (queries 15, 37); closest = A11, A3 (pooled panel nets) and A2.

## 4. Risk assessment of the novelty claim (brutally honest)

**Strongest competitors, ranked by reviewer threat.**
1. **Valle-Cruz et al. 2022 (GIQ)** - same flagship theme ("smart budgeting", 217 countries, AI for resource allocation). A reviewer will say "AI-assisted cross-country budget allocation already exists." Our defence is real but narrow: they optimise towards GDP/inflation/inequality outcomes with an NN + genetic algorithm; they do not predict official COFOG shares, have no baselines, no XAI evaluation. We *must* position against it explicitly and not use phrasing like "first AI budget allocation".
2. **Kisman et al. 2026 (Systems, defence XAI)** - the only found paper that compares SHAP with other explainers quantitatively on a government-spending target across countries. It undermines any claim that quantitative XAI evaluation in government spending is "unprecedented". What remains: LIME agreement/stability, deletion-faithfulness, multi-function, share-based targets. (Their details seen only on a vendor summary; read the paper before submission.)
3. **Obeng 2022 + Adolph et al. 2020 + Barnes et al. 2023 (OECD)** - the econometric literature already models COFOG shares, treats them as compositional, and documents that reallocation is slow. Reviewers from public economics will say "shares of COFOG are old; ML adds little". These papers actually *support* our headline (persistence is hard to beat) and should be cited as motivation, not ignored.
4. **Radulescu et al. 2015** - already forecast spending by function with NNs for CEE countries; kills "first ML forecast of functional spending".
5. **H3 (IJRSI 2025)** - weak venue and data (simulated inputs), but its description (forecast + constrained LP + dashboard) overlaps our engine/UI in the abstract; a careless reviewer may use it against "bounded allocation engine" novelty. Cheap to cite and dismiss.

**What is NOT novel (do not claim):** first ML budget model; first ML on COFOG; first SHAP in public finance; first compositional treatment of budget shares; first use of persistence baselines (any forecasting paper does this); first LIME-vs-SHAP comparison (Krishna et al. 2022 and others); first leakage audit generally (precedents in A19).

**What remains defensible (to the extent of this search):**
* the *combination*: composition-of-expenditure prediction on an official multi-country COFOG panel (Eurostat/OECD/IMF; 36 and 85 economies) evaluated in two practitioner modes (annual update vs cold-start) against persistence and income-group peer-mean baselines, with country-clustered bootstrap CIs;
* the honest negative result: persistence is hard to beat; ML gains concentrate in cold-start for health and R&D; stack significantly worse than persistence on A10 annual mode;
* a quantitative SHAP+LIME evaluation (agreement, top-k Jaccard, sign agreement, LIME stability, deletion-faithfulness) *on budget-share targets*, with the finding that signs can flip between the two methods;
* applicability/novelty score and error by income group (no comparable item found);
* the leakage audit with the specific, checkable finding (11 of 15 targets exact multiples of one series; `k x GDP` reaches R^2 0.9997).

**Weak spots inside our own text:**
* The audit (v) is of **our own earlier paper's dataset**, not of a third-party benchmark. It must not be worded as a benchmark audit of the field; call it a "forensic audit of our v1 semi-synthetic dataset" (a lesson in reproducibility).
* "No prior study ..." is conditional on this web proxy search. Scopus/WoS were not queried. The README already says "to the best of our web search"; keep that qualifier everywhere, and add it to the abstracts.
* Point (iii) (bounded-simplex projection) is a standard Euclidean projection; present it as an engineering component, not a methodological novelty.
* Point (ii) cold-start vs annual is standard train/test design; the novelty is the framing for budget analysts and the results, not the protocol.
* The "SDG tags" and "applicability score" are descriptive additions; no claim of validity should exceed the Spearman 0.70 evidence.

**Overall risk:** novelty as a *combination plus rigorous negative/honest evaluation* = LOW-to-MODERATE risk of a direct "already done" rejection. Novelty as "first ML/XAI for budget allocation" = HIGH risk. Probability that a Scopus/WoS run surfaces additional CLOSE items (Spanish/Portuguese and regional journals, conference papers) = moderate; budget time to read them.

## 5. Additional references we should cite (verified; key facts)

1. **Valle-Cruz, Fernandez-Cortez, Gil-Garcia (2022)**, GIQ 39(2):101644 (doi 10.1016/j.giq.2021.101644). 217 countries (World Bank 1960-2019), multilayer model + multi-objective GA; identifies GDP growth, inequality, inflation as target outcomes; flags explainability as a risk. (Already in `01_cited_in_paper_v1/`; make it the principal contrast.)
2. **Obeng (2022)**, Rev. Dev. Econ. 26(4):2414-2435. Up to 142 countries 1990-2017; FE, system GMM, SUR on COFOG spending components; little support for Wagner's law; pure public goods and merit goods complements.
3. **Adolph, Breunig, Koski (2020)**, J. Public Policy 40(1):25-50. Compositional-data methods to embed the budget constraint; 8 US-state categories 1984-2009; partisan trade-offs. Supports the CLR/simplex choice.
4. **Barnes, Cournede, Pascal (2023)**, OECD Economics Dept WP 1785 (doi 10.1787/56dda017-en). COFOG 1996-2017; reallocation differs by governance and fiscal rules; reluctance to cut health/social; partial convergence (Nordic group distinct, Greece diverges). Motivates persistence baseline and annual-mode result. (PDF also listed in `literature/related_work_pdfs/` as ECO-WKP(2023)38.)
5. **Kisman, Uzun, Guler (2026)**, Systems 14(3):283. Cross-country 2002-2023 defence-spending XAI; SHAP vs PDP vs ALE (details unverified; read paper first).
6. **Lee (2026)**, PLoS One 21(10):e0361904. SHAP + LightGBM on Korean health-insurance spending; autoregressive baselines best for short-term forecasts; indicators add only hypothesis-generating value. Strong external support for our "persistence is hard to beat" and cautious-interpretation stance.
7. **Goulet Coulombe, Marcellino, Stevanovic (2025)**, CIRANO WP 2025s-15 / UQAM WP 25-04. Pooled panel neural networks for state fiscal variables; gains largest for expenditures; pooling improves stability. Supports panel/cold-start pooling logic.
8. **Caravaggio, Lagravinese, Resce (2026)**, Empirical Economics 70(2). Gradient boosting best for regional health-spending prediction; motivates ML for fund distribution.
9. **Amarasinghe, Rodolfa, Lamba, Ghani (2023)**, Data & Policy 5:e5. Use cases and gaps of XAI in public policy; frame analysts as the explanation audience.
10. **Krishna et al. (2022)**, "The Disagreement Problem in Explainable ML", arXiv 2202.01602. Quantifies explainer disagreement; justifies our agreement metrics and the "treat one explanation as a hypothesis" message.
11. **Hashemi, Darejeh, Cruz (2024)**, UbiComp Companion '24. Explainability in PB through axioms-as-constraints; user study with preference for general over counterfactual explanations. Cite in future work (human-subject study).
12. **Yang, Molefyane, Lin (2023)**, Mathematics 11(14):3085. GRU forecasts of aggregate expenditure for 15 economies (already flagged in the survey as not downloaded).
13. **Guerrero & Castaneda (2022)** and the budgeting-for-SDGs line (UN WPSR 2023; Guariso et al., Data & Policy 2023). SDG-aware allocation by optimisation; position our SDG tags as descriptive.
14. **Kaki et al. (2025)**, IJRSI 12(9):3768-3774. Cite only as a weak contrast (simulated inputs, linear regression + LP, no XAI) if a reviewer raises "forecast + LP allocation".

*Do not cite without reading:* H1 beyond its abstract; A10, A11, A13, A17, A19 (search records only).

## 6. Exact database queries to paste

### Scopus (Advanced search). Filters: Document type = Article, Conference paper, Review; Language = English (and again without it); Years 2015-2026; Subject areas: Economics, Computer Science, Social Sciences, Decision Sciences, Business. Run each, export CSV, screen titles/abstracts, then forward/backward citation search on H2, H5, H1.

```
S1  TITLE-ABS-KEY ( ( "budget allocation" OR "public expenditure" OR "government expenditure" OR "government spending" OR "public spending" ) AND ( "machine learning" OR "deep learning" OR XGBoost OR "gradient boosting" OR "random forest" OR "neural network" ) AND ( COFOG OR "functional classification" OR "by function" OR "sectoral" ) )

S2  TITLE-ABS-KEY ( ( COFOG OR "classification of the functions of government" ) AND ( forecast* OR predict* OR "machine learning" OR "neural network" ) )

S3  TITLE-ABS-KEY ( ( "budget allocation" OR "public expenditure" OR "government spending" OR "fiscal" ) AND ( SHAP OR LIME OR "explainable AI" OR XAI OR "feature attribution" OR interpretab* ) )

S4  TITLE-ABS-KEY ( ( "expenditure composition" OR "spending composition" OR "budget shares" OR "expenditure shares" OR "budget composition" ) AND ( "compositional data" OR "log-ratio" OR "log ratio" OR Dirichlet OR "machine learning" ) )

S5  TITLE-ABS-KEY ( ( "artificial intelligence" OR "machine learning" ) AND ( "public budget*" OR "government budget*" OR "budgeting" ) AND ( "decision support" OR "recommend*" OR "allocation" ) )

S6  TITLE-ABS-KEY ( ( "cross-country" OR "panel of countries" OR "leave-one-country-out" OR "cold start" ) AND ( "health expenditure" OR "education spending" OR "military expenditure" OR "defence spending" OR "R&D expenditure" ) AND ( "machine learning" OR "random forest" OR XGBoost ) )

S7  TITLE-ABS-KEY ( ( "participatory budgeting" ) AND ( "explainab*" OR XAI OR "machine learning" OR "artificial intelligence" ) )

S8  TITLE-ABS-KEY ( ( "SDG*" OR "sustainable development goals" ) AND ( "budget allocation" OR "public spending" OR "government expenditure" ) AND ( "machine learning" OR optimi?ation OR "artificial intelligence" ) )

S9  TITLE-ABS-KEY ( ( "data leakage" OR "target leakage" OR "synthetic dataset" OR "synthetic data" ) AND ( "public finance" OR "government budget" OR "public expenditure" OR "fiscal" ) AND ( audit OR reproducib* OR benchmark ) )

S10 TITLE-ABS-KEY ( ( "LIME" AND "SHAP" ) AND ( agreement OR stability OR faithfulness OR fidelity OR disagreement ) AND ( "public sector" OR government OR "public policy" OR fiscal ) )

S11 TITLE-ABS-KEY ( ( "persistence" OR "naive forecast" OR "random walk" ) AND ( "government expenditure" OR "public expenditure" OR "budget" ) AND ( "machine learning" OR "XGBoost" ) )
```
Combined "kill-shot" check (should return ~0 relevant hits): 
```
TITLE-ABS-KEY ( ( "budget allocation" OR "public expenditure" ) AND ( "machine learning" OR XGBoost ) AND ( COFOG OR "functional classification" ) AND ( SHAP OR LIME ) )
```

### Web of Science Core Collection (Advanced search). Filters: Document types = Article, Proceedings Paper, Review Article; Timespan 2015-2026; Research Areas: Economics, Public Administration, Computer Science, Business & Economics, Government & Law. Also search "Emerging Sources Citation Index" separately.

```
W1  TS=(("budget allocation" OR "public expenditure" OR "government expenditure" OR "government spending" OR "public spending") AND ("machine learning" OR "deep learning" OR XGBoost OR "gradient boosting" OR "random forest" OR "neural network") AND (COFOG OR "functional classification" OR "by function" OR sectoral))

W2  TS=(COFOG AND (forecast* OR predict* OR "machine learning" OR "neural network"))

W3  TS=(("budget allocation" OR "public expenditure" OR "government spending" OR fiscal) AND (SHAP OR LIME OR "explainable AI" OR XAI OR interpretab*))

W4  TS=(("expenditure composition" OR "spending composition" OR "budget shares" OR "expenditure shares") AND ("compositional data" OR "log-ratio" OR Dirichlet OR "machine learning"))

W5  TS=(("artificial intelligence" OR "machine learning") AND ("public budget*" OR "government budget*" OR budgeting) AND ("decision support" OR recommend* OR allocation))

W6  TS=(("cross-country" OR "leave-one-country-out" OR "cold start") AND ("health expenditure" OR "education spending" OR "military expenditure" OR "defence spending" OR "R&D expenditure") AND ("machine learning" OR "random forest" OR XGBoost))

W7  TS=("participatory budgeting" AND (explainab* OR XAI OR "machine learning" OR "artificial intelligence"))

W8  TS=(("data leakage" OR "target leakage" OR "synthetic data") AND ("public finance" OR "government budget" OR "public expenditure" OR fiscal) AND (audit OR reproducib* OR benchmark))
```
Also run **IEEE Xplore** ("Command Search"): `("All Metadata":budget) AND ("All Metadata":government) AND ("All Metadata":"machine learning") AND ("All Metadata":SHAP OR "All Metadata":LIME)`, and **Google Scholar**: `allintitle: budget allocation machine learning government COFOG`, plus "cited by" on H2 (Valle-Cruz 2022) and H5 (Obeng 2022) for 2024-2026 citations.

### Screening protocol (to record in the paper's supplement)
Record date, database, query string, hit count, records screened, records retained; screen first by title/abstract; keep a PRISMA-style flow figure; re-run immediately before submission (this report is dated 2026-11-15).

## 7. Recommended novelty statement (defensible wording)

> **"To the best of our knowledge, and on the basis of searches of Scopus, Web of Science and the open web conducted in November 2026 [update after the database run], we found no prior study that jointly (i) predicts the composition of general-government expenditure across COFOG functions on a multi-country panel of officially reported data (36-85 economies, 2000-2024) for both an annual-update setting and a cold-start setting, (ii) evaluates it against the persistence and peer-mean baselines that budget analysts actually use under temporal, leave-country-out and shock-period protocols, and (iii) quantitatively assesses the agreement, stability and faithfulness of SHAP and LIME explanations of these predictions. Earlier work forecasts aggregate expenditure or single functions [Gur 2025; Dragulin 2025; Radulescu 2015], estimates the determinants of spending shares econometrically [Obeng 2022; Adolph 2020; Barnes 2023], or optimises cross-country budgets toward development outcomes without evaluating explanations [Valle-Cruz 2022]. In addition, we document how an apparently near-perfect benchmark result (R^2 > 0.99) in our own earlier version arose from synthetic targets (11 of 15 sector columns being exact multiples of one series), and we show that, with official data, persistence is hard to beat for annual updates, while cold-start learning helps for health and R&D but not for defence."**

Shorter abstract version (<= 60 words): *"We are not aware of earlier work that predicts COFOG expenditure composition across a multi-country official panel in annual-update and cold-start modes against practitioner baselines and quantitatively evaluates SHAP and LIME explanations; we also report a forensic audit showing how synthetic targets produced R^2 > 0.99 in our earlier benchmark."*

**Wording to avoid:** "first", "novel allocation algorithm", "outperforms existing methods", "no prior work exists" (without the "to our knowledge/search" qualifier), "audit of public-finance benchmarks" (it is an audit of our own v1 dataset).

### Edits suggested to existing text
* `README.md` section 7 ("Novelty claim ... no prior ... study"): keep the qualifier, add Valle-Cruz 2022, Obeng 2022 and Kisman 2026 to the "closest works" list; remove the implication that the SHAP/LIME comparison is generically new (cite Krishna 2022).
* `README.md` section 0 and `docs/02` ("forensic audit of a synthetic benchmark"): say "of our own earlier semi-synthetic dataset".
* `docs/02` section 2 sentence "Items (iv) and (v) most distinguish the paper": soften; (iv) has precedent in H1 (single function), and (v) has generic precedents (A19).
* `docs/02`/survey: add the five missing items from section 5 to `papers/references.bib`; re-verify "Nzazi et al. 2025" citation record.


---

## C. Crossref proxy search

Run by `tools/search_crossref_novelty.py` (re-runnable). Crossref returns relevance-ranked records from 2015 onward; titles only (abstracts mostly unavailable), so every hit must still be screened by a human. Citation counts are Crossref's (`is-referenced-by`).

## Query: `machine learning government budget allocation functions`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2020 | Budget Allocation, Regional Government and Parliament Relationship in Making Poverty Alleviation Policy | Journal of Advanced Research in Dynamica | 0 | 10.5373/jardcs/v12i5/20201972 |
| 2020 | Improve Budget Analysis With Machine Learning, Data Analytics | International Journal of Government Audi | 0 | 10.56251/slqb6384 |
| 2026 | Adaptive Privacy Budget Allocation for Differential Privacy Optimization in Fleet Federated Learning: Algorith | Artificial Intelligence and Machine Lear | 1 | 10.69987/aimlr.2026.70102 |
| 2019 | A decision support framework for robust R&amp;D budget allocation using machine learning and optimization | Decision Support Systems | 77 | 10.1016/j.dss.2019.03.010 |
| 2025 | Screening Smarter, Not Harder: Budget Allocation Strategies for Technology-Assisted Reviews (TARs) in Empirica | Machine Learning and Knowledge Extractio | 2 | 10.3390/make7030104 |
| 2022 | Government Construction Project Budget Prediction Using Machine Learning | Journal of Advances in Information Techn | 34 | 10.12720/jait.13.1.29-35 |
| 2023 | Intelligent Financial Governance: The Role of AI and Machine Learning in Enhancing Fiscal Impact Analysis and  | Journal for ReAttach Therapy and Develop | 2 | 10.53555/jrtdd.v6i10s(2).3480 |
| 2026 | The pattern of government expenditure and budget allocation in India | International Journal of Commerce and Ec | 0 | 10.66856/ijce.2026.8.3.8063 |
| 2026 | The Influence of Budget Allocation on Sustainability of Fiscal Resources in Government Primary Schools at Bari | Journal of Teaching, Learning &amp; Curr | 0 | 10.61227/0z14b703 |
| 2024 | Priority Setting and Resource Allocation in Coastal Local Government Marine Regulatory Reform: Application of  | Water | 4 | 10.3390/w16111544 |

## Query: `COFOG expenditure forecasting machine learning`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2025 | An analytics framework for healthcare expenditure forecasting with machine learning | Healthcare Analytics | 2 | 10.1016/j.health.2025.100428 |
| 2026 | Public Expenditure Forecasting in Cambodia: A Hybrid Econometric and Machine Learning Approach | International Journal of Economics and F | 0 | 10.32479/ijefi.24858 |
| 2024 | A fusion of machine learning algorithms and traditional statistical forecasting models for analyzing American  | Healthcare Analytics | 22 | 10.1016/j.health.2024.100312 |
| 2024 | A Fusion of Machine Learning and Traditional Statistical Forecasting Models for Analyzing American Healthcare  | Journal of Medical and Health Studies | 0 | 10.32996/jmhs.2024.5.1.12 |
| 2025 | Enhancing Stock Market Forecasting Using Machine Learning Models | International Journal of Science and Res | 0 | 10.21275/sr25730031803 |
| 2021 | Forecasting with Machine Learning Techniques | Forecasting | 4 | 10.3390/forecast3040052 |
| 2023 | Comparative Analysis of Machine Learning, Hybrid, and Deep Learning Forecasting Models: Evidence from European | Forecasting | 28 | 10.3390/forecast5020026 |
| 2023 | Performance Analysis of Machine Learning Models in Solar Energy Forecasting | International Journal of Machine Learnin | 1 | 10.18178/ijml.2023.13.3.1140 |
| 2025 | Day-Ahead Energy Price Forecasting with Machine Learning: Role of Endogenous Predictors | Forecasting | 15 | 10.3390/forecast7020018 |
| 2023 | On Forecasting Cryptocurrency Prices: A Comparison of Machine Learning, Deep Learning, and Ensembles | Forecasting | 91 | 10.3390/forecast5010010 |

## Query: `public expenditure by function prediction neural network`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2022 | Network Public Opinion Prediction Based on Improved Particle Swarm Optimization and BP Neural Network | International Journal of Neural Network | 0 | 10.38007/nn.2022.030404 |
| 2022 | Neural Network Algorithm for Budget Expenditure Prediction in LPP RRI Gorontalo | Journal La Multiapp | 0 | 10.37899/journallamultiapp.v3i2.596 |
| 2021 | Prediction of network public opinion based on bald eagle algorithm optimized radial basis function neural netw | International Journal of Intelligent Com | 16 | 10.1108/ijicc-07-2021-0148 |
| 2025 | Hybrid recurrent neural network using custom activation function for COVID-19 short term time series predictio | South Eastern European Journal of Public | 0 | 10.70135/seejph.vi.3854 |
| 2024 | GEPAF: A non-monotonic generalized activation function in neural network for improving prediction with diverse | Neural Networks | 8 | 10.1016/j.neunet.2024.106738 |
| 2017 | Prediction of protein function using a deep convolutional neural network ensemble | PeerJ Computer Science | 28 | 10.7717/peerj-cs.124 |
| 2016 | Prediction for network traffic of radial basis function neural network model based on improved particle swarm  | Neural Computing and Applications | 30 | 10.1007/s00521-016-2483-5 |
| 2016 | Estimation of Energy Expenditure Using a Patch-Type Sensor Module with an Incremental Radial Basis Function Ne | Sensors | 8 | 10.3390/s16101566 |
| 2023 | Retracted: Prediction of Urban Scale Expansion Based on Genetic Algorithm Optimized Neural Network Model | Journal of Function Spaces | 0 | 10.1155/2023/9897063 |
| 2021 | Metro Water Fraudulent Prediction in Houses Using Convolutional Neural Network and Recurrent Neural Network | Revista Gestão Inovação e Tecnologias | 3 | 10.47059/revistageintec.v11i4.2177 |

## Query: `government expenditure composition shares compositional data`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2016 | Segmentation by Tourist Expenditure Composition: An Approach with Compositional Data Analysis and Latent Class | Tourism Analysis | 24 | 10.3727/108354216x14713487283075 |
| 2026 | Bayesian Poisson‐Lognormal Regression With Compositional Effect Shares for Multivariate Count Data | Environmetrics | 0 | 10.1002/env.70102 |
| 2025 | Government expenditure composition and long-run economic growth in the aging democracy | Economic Modelling | 11 | 10.1016/j.econmod.2025.107119 |
| 2021 | Oil bonanza and the composition of government expenditure | Economics of Governance | 8 | 10.1007/s10101-020-00246-3 |
| 2018 | Government Expenditure in India: Composition and Multipliers | Journal of Quantitative Economics | 11 | 10.1007/s40953-018-0122-y |
| 2022 | When Government Expenditure Meets Bank Regulation: The Impact of Government Expenditure on Credit Supply | SSRN Electronic Journal | 1 | 10.2139/ssrn.4010448 |
| 2022 | Structural Transformation, Income Inequality and Government Expenditure: Evidence from International Panel Dat | Jurnal Ekonomi Malaysia | 3 | 10.17576/jem-2022-5603-02 |
| 2024 | The expenditure composition and trade-offs in local government budgets | Socio-Economic Planning Sciences | 16 | 10.1016/j.seps.2024.101900 |
| 2019 | The effect of tobacco expenditure on expenditure shares in South African households: A genetic matching approa | PLOS ONE | 14 | 10.1371/journal.pone.0222000 |
| 2022 | Fiscal Decentralization and the Composition of Local Government Expenditure: Evidence from South Korea | Public Finance Review | 27 | 10.1177/10911421221093142 |

## Query: `explainable artificial intelligence public budget`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2025 | Architecture: explainable artificial intelligence and research into the creative process | European Public &amp; Social Innovation  | 1 | 10.31637/epsir-2025-1606 |
| 2026 | An Analysis of Explainable Artificial Intelligence for Intelligent Cybersecurity Applications | International Journal of Advanced Artifi | 0 | 10.55640/ijaair-v03i08-11 |
| 2022 | A Novel Approach to Adopt Explainable Artificial Intelligence in X-ray Image Classification | Advances in Machine Learning &amp; Artif | 0 | 10.33140/amlai.03.01.01 |
| 2022 | Special issue on Explainable Artificial Intelligence (XAI) | Artificial Intelligence | 24 | 10.1016/j.artint.2022.103705 |
| 2026 | Age-Stratified Mental Health Prediction Using SHAP: An Explainable Artificial Intelligence Framework | ADCAIJ: Advances in Distributed Computin | 0 | 10.14201/adcaij.32910 |
| 2024 | Frontiers of Artificial Intelligence Versus Generative, Explainable and Quantum Technologies: An Overview | Open Access Journal of Data Science and  | 0 | 10.23880/oajda-16000118 |
| 2019 | Explainable Artificial Intelligence | Research Library Issues | 7 | 10.29242/rli.299.3 |
| 2026 | Explainable Artificial Intelligence for Understanding Patterns of Educational Inequality | Artificial Intelligence in Learning | 0 | 10.63913/ail.v2i2.58 |
| 2026 | Unveiling structural patterns of global budget transparency using advanced machine learning and explainable ar | Economics of Governance | 10 | 10.1007/s10101-026-00365-3 |
| 2026 | Exploring Artificial Intelligence for Learning Enhancement with Predictive and Explainable Modelling | Artificial Intelligence in Learning | 0 | 10.63913/ail.v2i1.29 |

## Query: `SHAP government spending prediction countries`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2025 | How government spending matters to FDI inflows in developing countries? | European Journal of Government and Econo | 0 | 10.17979/ejge.2025.14.2.11723 |
| 2021 | Heterogeneity of government social spending in European Union countries | Future Business Journal | 4 | 10.1186/s43093-021-00084-7 |
| 2024 | IMF Conditionality and Government Education Spending: The Case of 10 MENA Countries | Economies | 3 | 10.3390/economies12090234 |
| 2015 | Government Spending Effects in Low-income Countries | IMF Working Papers | 2 | 10.5089/9781513578972.001 |
| 2023 | Government Spending and Exchange Rate in ASEAN Countries: Evidence from ARDL and Toda &amp;Yamamoto Approach | Research Journal of Finance and Accounti | 0 | 10.7176/rjfa/14-10-09 |
| 2019 | Impact of Government Spending on Private Consumption: Evidence from ECOWAS Countries | Modern Economy | 6 | 10.4236/me.2019.103041 |
| 2022 | The influences of government spending on energy poverty: Evidence from developing countries | Energy | 183 | 10.1016/j.energy.2021.121785 |
| 2026 | Government Spending Efficiency in BRICS Countries: Implications for Indonesia’s Accession | Signifikan: Jurnal Ilmu Ekonomi | 0 | 10.15408/sjie.v15i2.46845 |
| 2020 | The Government Spending Multiplier in Latin American Countries: Does the Institutional Environment Matter? | SSRN Electronic Journal | 0 | 10.2139/ssrn.3735100 |
| 2015 | VARIETIES OF CAPITALISM AND GOVERNMENT SPENDING IN DEVELOPED AND DEVELOPING COUNTRIES | Journal of Economic Development | 3 | 10.35866/caujed.2015.40.1.005 |

## Query: `budget allocation decision support system explainable`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2020 | Decision Support System Budget Allocation Fund Village With AHP method (Analytic Hierarchy Process) In the vil | Journal Of Computer Networks, Architectu | 0 | 10.47709/cnapc.v2i1.355 |
| 2019 | A decision support framework for robust R&amp;D budget allocation using machine learning and optimization | Decision Support Systems | 77 | 10.1016/j.dss.2019.03.010 |
| 2026 | An Explainable AI Decision Support System for Optimising Hospital Bed Allocation: A Predictive Modelling Study | International Journal of Medical Discove | 0 | 10.64220/ijmd.v2i2.001 |
| 2026 | Data Governance as a Decision Variable: A Model-Driven Decision Support System for Budget Allocation in Genera | Computation | 0 | 10.3390/computation14100234 |
| 2018 | Toward a real-time and budget-aware task package allocation in spatial crowdsourcing | Decision Support Systems | 47 | 10.1016/j.dss.2018.03.010 |
| 2025 | Enhancing cybersecurity risk assessment using temporal knowledge graph-based explainable decision support syst | Decision Support Systems | 11 | 10.1016/j.dss.2025.114526 |
| 2026 | Explainable Investment Decision Support System with Fallback Mechanism for Robust Portfolio Allocation | Indian Journal of Computer Science and T | 0 | 10.59256/indjcst.20260501080 |
| 2026 | A Closed-Loop Financial Decision Support System With Explainable AI for Manufacturing | International Journal of Decision Suppor | 0 | 10.4018/ijdsst.402902 |
| 2025 | AGRIML-INSIGHT: HYBRID EXPLAINABLE AI SYSTEM FOR ENHANCED AGRICULTURAL DECISION SUPPORT | Journal of Applied Bioanalysis | 0 | 10.53555/jab.v11si3.891 |
| 2021 | A novel decision support system for optimizing aircraft maintenance check schedule and task allocation | Decision Support Systems | 70 | 10.1016/j.dss.2021.113545 |

## Query: `cross-country sectoral public spending prediction health education defence`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2019 | Defence spending and women in research: A cross-country comparison | Science and Public Policy | 2 | 10.1093/scipol/scz021 |
| 2021 | Cross–Country Dependence, Heterogeneity and the Growth Effects of Military Spending | Defence and Peace Economics | 12 | 10.1080/10242694.2021.1893454 |
| 2015 | The effects of local elections on national military spending: A cross-country study | Defence and Peace Economics | 4 | 10.1080/10242694.2015.1061154 |
| 2021 | Public Spending on Education and Economic Growth: Cross-Country Analysis | Voprosy statistiki | 8 | 10.34023/2313-6383-2021-28-3-70-85 |
| 2018 | Sectoral cognitive skills, R&amp;D, and productivity: a cross-country cross-sector analysis | Education Economics | 10 | 10.1080/09645292.2018.1515309 |
| 2020 | Volatility in Discretionary Public Spending and Economic Growth:
      A Cross Country Analysis | The Pakistan Development Review | 1 | 10.30541/v59i1pp.45-68 |
| 2026 | Cross-country differences in household healthcare spending | Health Affairs Scholar | 0 | 10.1093/haschl/qxag234 |
| 2026 | Assessing the implementation of cross sectoral coordination and surveillance integration for One Health in the | Discover Public Health | 0 | 10.1186/s12982-026-02301-6 |
| 2026 | Sectoral public spending, human development, and income inequality in North Sumatra province: District-level e | Public and Municipal Finance | 0 | 10.21511/pmf.15(2).2026.11 |
| 2023 | Is School Funding Unequal in Latin America? A Cross-Country Analysis of Interregional Disparities in Public Sp | Comparative Education Review | 5 | 10.1086/722831 |

## Query: `gradient boosting public expenditure forecasting`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2025 | Public Debt Forecasting in Kenya: Integrating Macroeconomic Variables with Arimax and Extreme Gradient Boostin | International Journal of Mathematics And | 0 | 10.47191/ijmcr/v13i8.07 |
| 2022 | Disaggregated Retail Forecasting: A Gradient Boosting Approach | SSRN Electronic Journal | 1 | 10.2139/ssrn.4129889 |
| 2016 | Probabilistic gradient boosting machines for GEFCom2014 wind forecasting | International Journal of Forecasting | 122 | 10.1016/j.ijforecast.2016.02.002 |
| 2023 | Drought Forecasting Using Integrated Variational Mode Decomposition and Extreme Gradient Boosting | Water | 27 | 10.3390/w15193413 |
| 2022 | Forecasting public bicycle rental demand using an optimized eXtreme Gradient Boosting model | Journal of Intelligent &amp; Fuzzy Syste | 4 | 10.3233/jifs-211202 |
| 2023 | Silver Price Forecasting Using Extreme Gradient Boosting (XGBoost) Method | Mathematics | 20 | 10.3390/math11183813 |
| 2026 | A hybrid data-driven architecture for forecasting soil thermal conductivity using optimized gradient boosting  | Scientific Reports | 0 | 10.1038/s41598-026-66645-4 |
| 2022 | An Optimized Gradient Boosting Model by Genetic Algorithm for Forecasting Crude Oil Production | Energies | 20 | 10.3390/en15176416 |
| 2022 | A solution for M5 Forecasting - Uncertainty: Hybrid gradient boosting and autoregressive recurrent neural netw | International Journal of Forecasting | 7 | 10.1016/j.ijforecast.2022.01.009 |
| 2022 | Energy Forecasting in a Public Building: A Benchmarking Analysis on Long Short-Term Memory (LSTM), Support Vec | Applied Sciences | 41 | 10.3390/app12199788 |

## Query: `artificial intelligence budgeting public sector resource allocation`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2022 | From E-budgeting to smart budgeting: Exploring the potential of artificial intelligence in government decision | Government Information Quarterly | 127 | 10.1016/j.giq.2021.101644 |
| 2025 | Propensity factors of artificial intelligence technology adoption by public sector auditors | Journal of Public Budgeting, Accounting  | 7 | 10.1108/jpbafm-09-2024-0189 |
| 2023 | The impact of government form on resource allocation in local government, evidence from municipal court closur | Public Budgeting &amp; Finance | 1 | 10.1111/pbaf.12337 |
| 2026 | Artificial intelligence in public sector accounting information systems: adoption or resistance among accounta | Journal of Public Budgeting, Accounting  | 1 | 10.1108/jpbafm-12-2025-0382 |
| 2024 | Exploring the effect of International Public Sector Accounting Standards adoption on national resource allocat | Public and Municipal Finance | 9 | 10.21511/pmf.13(1).2024.01 |
| 2023 | Strategyproof Mechanism for Two-Sided Matching with Resource Allocation | Artificial Intelligence | 8 | 10.1016/j.artint.2023.103855 |
| 2023 | Multi resource allocation with partial preferences | Artificial Intelligence | 4 | 10.1016/j.artint.2022.103824 |
| 2022 | Artificial intelligence and public sector human resource management in South Africa: Opportunities, challenges | SA Journal of Human Resource Management | 74 | 10.4102/sajhrm.v20i0.1972 |
| 2026 | Zero-Based Budgeting and Artificial Intelligence Applied to the Brazilian Public Sector | Open Journal of Social Sciences | 0 | 10.4236/jss.2026.148049 |
| 2023 | Parameterized complexity of envy-free resource allocation in social networks | Artificial Intelligence | 6 | 10.1016/j.artint.2022.103826 |

## Query: `sustainable development goals budget allocation machine learning`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2024 | Forecasting sustainable development goals scores by 2030 using machine learning models | Sustainable Development | 54 | 10.1002/sd.3037 |
| 2019 | Global carbon budget allocation based on Rawlsian Justice by means of the Sustainable Development Goals Index | Environment, Development and Sustainabil | 11 | 10.1007/s10668-019-00433-1 |
| 2023 | IoT and machine learning for enabling sustainable development goals | Frontiers in Communications and Networks | 18 | 10.3389/frcmn.2023.1219047 |
| 2023 | Sustainable development through green innovation and resource allocation in cities: Evidence from machine lear | Sustainable Development | 43 | 10.1002/sd.2516 |
| 2023 | From Data to Impact: Machine Learning Models for Sustainable Development Region Classification- Accelerating t | International Journal For Multidisciplin | 1 | 10.36948/ijfmr.2023.v05i05.7180 |
| 2026 | Sustainable Engineering Design: Accelerating Thermoelastic Stress Prediction in Hybrid SiC–Ti6Al4V Components  | International Journal of Sustainable Dev | 0 | 10.59543/dbs4d790 |
| 2020 | Quantitative Analysis of the Impact of Public Policies on the Sustainable Development Goals through Budget All | Sustainability | 37 | 10.3390/su122410583 |
| 2025 | AI for Sustainable Development Goals: Leveraging Machine Learning for Climate-Resilient Wheat Production in Wa | Engineering and Technology Journal | 0 | 10.47191/etj/v10i11.29 |
| 2018 | Statistical Machine Learning Methods and Remote Sensing for Sustainable Development Goals: A Review | Remote Sensing | 241 | 10.3390/rs10091365 |
| 2024 | Renewable energy and sustainable development goals: Insights from
                    <scp>latent dirichlet al | Sustainable Development | 42 | 10.1002/sd.3027 |

## Query: `LIME SHAP agreement tabular economic data`

| Year | Title | Venue | Cites | DOI |
|---|---|---|---|---|
| 2026 | Reliability diagnostics for post-hoc explanations in network intrusion detection: a SHAP–LIME agreement study | Frontiers in Big Data | 0 | 10.3389/fdata.2026.1934235 |
| 2026 | Beyond Accuracy: A Comprehensive Comparative Study of Gradient Boosting Versus Tabular Deep Learning and Expla | International Journal on Artificial Inte | 6 | 10.1142/s0218213026400038 |
| 2026 | Quantifying Explanation Disagreement Between SHAP and LIME Across Tabular Classification Models | International Journal of Computer Scienc | 1 | 10.26438/ijcse.v14i1.7255 |
| 2024 | US-LIME: Increasing fidelity in LIME using uncertainty sampling on tabular data | Neurocomputing | 28 | 10.1016/j.neucom.2024.127969 |
| 2026 | Physics-informed, cost-aware fault classification with comparative explainability for predictive maintenance:  | Scientific Reports | 0 | 10.1038/s41598-026-64374-2 |
| 2021 | Comparing LIME and SHAP using Synthetic Polygonal Data Clusters | International Journal for Infonomics | 0 | 10.20533/iji.1742.4712.2021.0214 |
| 2023 | Specific-Input LIME Explanations for Tabular Data Based on Deep Learning Models | Applied Sciences | 31 | 10.3390/app13158782 |
| 2020 | The Best Way to Select Features? Comparing MDA, LIME, and SHAP | The Journal of Financial Data Science | 81 | 10.3905/jfds.2020.1.047 |
| 2026 | Predicting the UCS of lime-treated clay soils reinforced with polypropylene fibers using ensemble and deep tab | Asian Journal of Civil Engineering | 0 | 10.1007/s42107-026-01750-3 |
| 2026 | An Explainable AutoML Pipeline for Multi-Task Tabular Data Using Optuna and SHAP | Journal of ISMAC | 0 | 10.36548/jismac.2026.3.007 |

## How to use
Screen the titles above for anything that predicts the composition of government expenditure by function across countries AND evaluates explanations. Add any new close work to `docs/07_Novelty_Search_Report.md` and `papers/references.bib` only after reading it.
Unique records returned: 119

## Screening verdict (title-level, 15 Nov 2026)
No record predicts the composition of government expenditure across functions for a multi-country panel with an XAI evaluation. Items worth reading in full before submission: *Unveiling structural patterns of global budget transparency using advanced ML and explainable AI* (Economics of Governance, 2026; transparency, not allocation), *Zero-Based Budgeting and AI Applied to the Brazilian Public Sector* (2026), *Improve Budget Analysis With ML, Data Analytics* (IJGBR? 2020), *A decision support framework for robust R&D budget allocation using ML and optimization* (Decision Support Systems 2019; firm/R&D level), *Government Construction Project Budget Prediction Using ML* (2022; project level). None is a direct competitor on title screening.

## Nzazi et al. 2025 — record re-checked (Crossref, 15 Nov 2026)
Title *Artificial Intelligence for Public Expenditure Analysis in Low-Income Countries: Opportunities and Challenges*; 9 authors (Nzazi, Biaba, Bazie, Tashev, Kambale, Tuong, Kyamakya, Kasoro, Kasereka); Procedia Computer Science 272, pp. 261–268, 2025; DOI 10.1016/j.procs.2025.10.204 — **matches `papers/references.bib` exactly**; the earlier 'not found' note came from a web-search miss, not from the record.


---

## D. Public-finance literature notes

| key | title (Crossref) | venue | year | DOI | match |
|---|---|---|---|---|---|
| devarajan1996 | The composition of public expenditure and economic growth | Journal of Monetary Economics | 1996 | 10.1016/0304-3932(96)01249-4 | 1.00 |
| nordhaus1975 | The Political Business Cycle | The Review of Economic Studies | 1975 | 10.2307/2296528 | 1.00 |
| rogoff1988 | Elections and Macroeconomic Policy Cycles | International Finance Discussion Papers | 1985 | 10.17016/ifdp.1985.271 | 1.00 |
| brender2005 | Political budget cycles in new versus established democracies | Journal of Monetary Economics | 2005 | 10.1016/j.jmoneco.2005.04.004 | 1.00 |
| jones2005 | A Model of Choice for Public Policy | Journal of Public Administration Research and Theory | 2004 | 10.1093/jopart/mui018 | 1.00 |
| lamartina2011 | Increasing Public Expenditure: Wagner’s Law in OECD Countries | German Economic Review | 2011 | 10.1111/j.1468-0475.2010.00517.x | 1.00 |
| garrett2001 | Globalization, government spending and taxation in the OECD | European Journal of Political Research | 2001 | 10.1023/a:1011043120145 | 1.00 |
| dunne2003 | The Demand for Military Spending in Developing Countries | International Review of Applied Economics | 2003 | 10.1080/713673166 | 1.00 |
| blanchard2002 | An Empirical Characterization of the Dynamic Effects of Changes in Government Spending and Taxes on Output | The Quarterly Journal of Economics | 2002 | 10.1162/003355302320935043 | 1.00 |
| alesina1999 | Budget institutions and fiscal performance in Latin America | Journal of Development Economics | 1999 | 10.1016/s0304-3878(99)00012-7 | 1.00 |
| kneller1999 | Fiscal policy and growth: evidence from OECD countries | Journal of Public Economics | 1999 | 10.1016/s0047-2727(99)00022-5 | 1.00 |
| wildavsky1969 | Rescuing Policy Analysis from PPBS | Public Administration Review | 1969 | 10.2307/973700 | 1.00 |

**Dropped (could not verify, do not cite):** davis1966 (A theory of the budgetary process), hallerberg2009 (Fiscal governance in Europe), easterly1993 (Fiscal policy and economic growth: an empirical investigation), hughes2020 (Fiscal rules and budget composition)

Use: Wagner's law / government-size (lamartina2011), composition-and-growth (devarajan1996, easterly1993, kneller1999), political budget cycles (nordhaus1975, rogoff1988, brender2005), budget incrementalism/punctuations (davis1966, jones2005), globalisation and spending (garrett2001), military spending determinants (dunne2003), fiscal governance (hallerberg2009, alesina1999). Read each abstract before relying on a specific claim.
