# Panel C: citation-claim support audit (independent)

Date: 2026-11-15. Scope: papers/main_journal.tex, papers/sections/*.tex (incl. tab_gap.tex), papers/main_conference.tex (incl. tab_gap_conf.tex), papers/references.bib.
Method: Crossref abstracts, arXiv abstracts, open-access PDFs in literature/ read with PyMuPDF (Santschi, Nzazi, Dragulin, Gur, Yang, Radulescu, Valle-Cruz, Guerrero, Barnes/OECD, Yao, Nonato dissertation), WebSearch/WebFetch for Dhungel, Kisman, Mohith. Honest user agent, no blocks bypassed. No repo file edited; nothing committed.
Labels: SUPPORTED / PARTLY / UNSUPPORTED / UNVERIFIABLE (by tool). "abstract only" = full text not read.
Blocked or empty for the tool: MDPI (Kisman) HTTP 403; Springer (Dhungel) redirects to an auth-cookie page (not followed); IEEE Xplore (Mohith) empty page. Crossref has no abstract for Mohith, Dhungel, Radulescu, Valle-Cruz, Nzazi, Barnes.

## 0. Headline findings (new in this round)
1. **Nonato 2026 is mis-described in the journal, the conference paper and tab_gap.** Crossref abstract: "a multi-output XGBoost model is estimated to link spending profiles to GDP growth, inflation, and the Gini index; Bayesian optimisation ... search[es] ... for allocation vectors that maximise a stated objective". The Nonato UnB dissertation in literature/ confirms: Brazil's federal spending by budget function are the input (independent) variables; the dependent variables are GDP, inflation, Gini. So Nonato does NOT predict spending by function. Its R2 0.97 (random K-fold on augmented data) and R2 -0.45 (anti-leakage check; GDP growth and inflation; Gini +0.60) refer to macro outcomes, not spending shares. The -0.45 is checkable from the Crossref abstract (the manuscript says it could not be verified). "Closest allocation-prediction study" is overstated.
2. **Kisman 2026 row of tab_gap is probably wrong** ("expenditure level", "shown"). Only a third-party summary (ownyourai.com; secondary, unverified) was reachable: classification models (ROC-AUC), three targets (military spending as share of GDP, share of government spending, per capita), SHAP/PDP/ALE with fidelity and faithfulness scores reported for SHAP. If true, "explanations tested" is not "shown". Publisher blocked: UNVERIFIABLE by tool, but the current cells are not safe.
3. **Francies 2026 abstract** (Crossref): SHAP + structural causal model + DiCE; Chicago (10,172 records, 2023-26) and NYC (681,131); strict temporal hold-out, R2 0.959; "strong algorithmic budget inertia, with prior allocation dominating feature importance"; a Budget Explainability Score combining fidelity, interpretability and equity; fairness evaluation. This weakens "SHAP/LIME are usually shown rather than evaluated" and "a test of the explanations rather than their display", and it independently reports a persistence/inertia result. Francies is not in tab_gap.
4. **Gur 2025 row of tab_gap says "none reported"** for explanation method, but the Gur PDF reports feature-importance scores for TFT, RF, XGB, MLP (Fig. 6, Table 4). Cell wrong.
5. **Mohith 2026**: every detail in the manuscript (twelve sectors, FY2005-06 to 2024-25, GB and ridge beat deep models, SHAP + permutation + LIME + intervals) is UNVERIFIABLE by tool; nothing in the repo records the source of that abstract. The text says "known to us from the abstract only"; I could not reproduce it.

## 1. Status of the previous audit (review_B) findings
| review_B finding | status now |
|---|---|
| Radulescu "four" -> five CEE | FIXED everywhere (sec_related, tab_gap, tab_gap_conf, conference). Source: Hungary, Poland, Czech Republic, Bulgaria, Romania. |
| Nzazi conclusion "explainable systems rare" | FIXED in substance ("conceptual or pilot-scale"). Residual: "mostly" vs source "many"; source is a short PRISMA-style review of ten LIC papers, not just "narrative". |
| Dragulin GRU/ECM | FIXED (LSTM and TCN vs SARIMA, VAR, ECM; PDF lines 163-168). |
| Valle-Cruz "rather than predicting" | FIXED (now "relate expenditure strategies to outcomes ... explore how resources could be allocated"). |
| Guerrero "agent-based" | FIXED ("bottom-up causal framework", matches abstract). |
| Yao "one hospital" | FIXED ("patient-level insurance cost data"; PDF: 1 338-record medical cost dataset). |
| Santschi short paper | FIXED ("short paper with preliminary results"). |
| Kisman PDP/ALE | FIXED in text (not named); table cells still doubtful (0.2). |
| Nonato -0.45 / "no explanation method" | PARTLY: number removed from text, hedged "as far as we can tell from the abstract"; the larger mischaracterisation (target) is NOT fixed, and -0.45 is in fact checkable. |
| Mohith unverified | NOT FIXED (daggered, still unverifiable). |
| Aitchison/TVD | FIXED (TVD justified separately; "not a log-ratio (Aitchison) distance"). |
| Grinsztajn "small" | PARTLY: method and related say "medium-sized"; sec_results l.92 still says "small tabular data". |
| Missing method references | ADDED (Egozcue, Ferrari, Douma, Lei, Angelopoulos, Romano, Barber, Gorishniy, Shwartz-Ziv, Borisov, Hooker, Kumar, Bhatt, Ghorbani, Mehrabi, Obermeyer, Hardt, Athey, Mullainathan, Medeiros, Goulet, Afonso, Potrafke, Bove, Davis, Wolpert, Cameron, Bergmeir, Holm). All keys exist in references.bib. |
| Krishna authors, Rogoff, Chand, Nzazi type | FIXED in bib (6 authors, preprint flag; Rogoff-Sibert RES 1988 doi 10.2307/2297526; Nzazi inproceedings). |
| Repo URL | Journal uses https://github.com/Pranav-chaudhari-2006/GovAllocXAI- (trailing hyphen): HTTP 200 today; the URL without the hyphen returns 404 now. Keep as is. |

## 2. Sentence-by-sentence claims about cited sources
(Journal sec_related unless stated.)

### 2a. ML for budgets
| # | sentence | key | verdict | note |
|---|---|---|---|---|
| 1 | "Gur et al. compare machine- and deep-learning forecasters on Turkiye's monthly budget expenditure (2008--2024), including crisis periods" | gur2025 | SUPPORTED | Crossref: Jan 2008-May 2024, GFC, euro crisis, COVID; PDF compares TFT, XGBoost, MLP, LSTM, RF, ensembles. |
| 2 | "Dragulin et al. benchmark LSTM and TCN networks (among other models) against SARIMA, VAR and ECM" | dragulin2025 | SUPPORTED | PDF lines 163-168. Data are local public institutions. |
| 3 | "Yang et al. forecast the government expenditure of 15 large economies with a GRU network and find it superior to ARIMA, ETS, SVR and XGBoost baselines" | yang2023 | SUPPORTED | abstract also lists CNN, LSTM; 1990-2020. |
| 4 | "Barnes et al. ... reallocate spending across COFOG functions (1996--2017) ... countries with sounder governance and tighter fiscal rules reallocate more, but they build no predictive model" | barnes2023 | SUPPORTED | OECD WP abstract. |
| 5 | "Nzazi et al. provide a narrative review ... and conclude that applications are mostly conceptual or pilot-scale" | nzazi2025 | PARTLY | source: "short review", PRISMA-style, ten LIC papers; "many ... conceptual or pilot-scale". |
| 6 | "Santschi et al. train XGBoost and CatBoost on Swiss cantonal accounts and study human--AI collaboration against expert forecasters (a short paper with preliminary results); one country and account groups" | santschi2024 | SUPPORTED | 36 accounts, 26 cantons, train 2011-21, test 2022; AI better in 3 of 4 groups. |
| 7 | "Radulescu et al. forecast public expenditure by function with feed-forward networks for five CEE economies" | radulescu2015 | SUPPORTED | |
| 8 | "Valle-Cruz et al. combine neural networks and a multi-objective genetic algorithm on 217 countries to relate expenditure strategies to outcomes ... and to explore how resources could be allocated; they do not predict an observed functional split" | valle2022 | SUPPORTED | World Bank 1960-2019, 217 countries, GDP/inflation/Gini. |
| 9 | Caravaggio / Di Stefano and Resce / Chand and Zhang sentence | caravaggio2025, distefano2025, chand2022 | SUPPORTED | carried over from review_B; not re-read. |
| 10 | "Guerrero and Castaneda propose a bottom-up causal framework linking spending to development gaps in 140 countries" | guerrero2022 | SUPPORTED | |
| 11 | "Nguyen et al. document a non-linear association between government expenditure and SDG progress" | nguyen2026 | SUPPORTED | carried over. |
| 12 | "SHAP ... attached to gradient-boosted models ... for instance for enterprise performance [zhang2026] or patient-level health-insurance cost prediction [yao2025]" | zhang2026, yao2025 | SUPPORTED as examples | Yao: XGBoost R2 0.89, SHAP names smoking, BMI, age. |
| 13 | "Such studies usually display attribution plots without testing whether the attributions are faithful, stable or consistent across methods" | (general) | PARTLY | true for those two; not for Francies (fidelity in its score) and probably not Kisman. "usually" rests on two examples. |

### 2b. Closest-work paragraph
| # | sentence | key | verdict | note |
|---|---|---|---|---|
| 14 | "Nonato et al. predict Brazil's federal executed spending by budgetary function with a multi-output XGBoost and Bayesian optimisation" | nonato2026 | **UNSUPPORTED** | spending by function is the INPUT; outputs are GDP growth, inflation, Gini; Bayesian optimisation searches allocation vectors. |
| 15 | "24 annual observations that they augment with 1 048 synthetic points" | nonato2026 | SUPPORTED | N = 24, 2000-2023; 1048 synthetic. |
| 16 | "$R^2$ up to 0.97 and a separate leakage-free check with much lower performance (we could verify the first figure but not the second ...)" | nonato2026 | SUPPORTED, outdated | abstract gives both 0.97 and -0.45 (macro outcomes). Delete "could not verify". |
| 17 | "covers one country and does not use COFOG; ... uses no explanation method" | nonato2026 | PARTLY | dissertation has XGBoost input-importance table and discusses explicability; "COFOG" absent from abstract. |
| 18 | "Kisman et al. explain cross-country defence expenditure (2002--2023) with explainable-AI methods; it targets one function and an expenditure level" | kisman2026 | PARTLY / UNVERIFIABLE | abstract supports years, cross-country, XAI, defence; "level" unsupported (third party: shares and per capita, classification). |
| 19 | "Dhungel et al. report an exploratory case study of AI decision support for budget preparation in Germany" | dhungel2025 | SUPPORTED (abstract only, catalogue pages) | state and municipal level; LLMs, anomaly detection prototype. |
| 20 | "Francies et al. propose a SHAP, causal and counterfactual framework for urban budget allocation in smart cities (preprint)" | francies2026 | SUPPORTED | but incomplete (see 0.3). |
| 21 | "Mohith et al., known to us from the abstract only, benchmark classical and deep-learning models ... twelve sectors (FY 2005--06 to 2024--25), find that gradient boosting and ridge regression beat the deep-learning models, and add SHAP, permutation importance, LIME and prediction intervals" | mohith2026 | UNVERIFIABLE | title only confirmed (India, sectoral budget allocations, classical ML vs DL). |
| 22 | "Their finding that simple models win on short annual series agrees with ours, as does the caution about leakage in Nonato et al." | mohith2026, nonato2026 | UNVERIFIABLE / SUPPORTED | Nonato half supported by abstract. |
| 23 | "found five recent studies that touch our setting" | - | SUPPORTED (count) | |
| 24 | "What we add is ... a test of the explanations rather than their display." | - | PARTLY | Francies and possibly Kisman test fidelity; the distinct parts are SHAP-LIME agreement, LIME stability, deletion test, synthetic ground truth. |
| 25 | Intro: "Studies on budgets by function are few, mostly single-country or older [santschi2024, radulescu2015, nonato2026, mohith2026]" | four | PARTLY | Santschi = accounts, Nonato = function as input, Mohith unverifiable; only Radulescu is a clean by-function forecast. |
| 26 | Intro: "SHAP and LIME are usually shown rather than evaluated" | (uncited) | PARTLY | see 13, 24. |

### 2c. Positioning and conference wording
| # | sentence | verdict | note |
|---|---|---|---|
| 27 | "We do not claim to be the first ... To the best of our (non-systematic) search no single prior study covers all four, but each is individually covered by some of the work above." | PARTLY | tone is adequate; "each is individually covered" is not established for (iii) (no study found comparing SHAP with LIME on budget shares). |
| 28 | Conference intro: "to our (non-systematic) search no single prior study covers the conjunction of (i)--(iv)" | SUPPORTED as hedged | |
| 29 | Conference related: "Nonato et al. (Brazil, 24 years) and Mohith et al. ... are the closest functional-allocation studies" | UNSUPPORTED for Nonato; Mohith UNVERIFIABLE | |
| 30 | Conference: "the latter finds that gradient boosting and ridge beat deep learning" | UNVERIFIABLE | |
| 31 | Conference: "Explanations are typically shown, not tested" | PARTLY | see 13. |

### 2d. tab_gap.tex and tab_gap_conf.tex, cell by cell (the two tables are cell-identical)
| study | setting | target | explanation method | explanations tested |
|---|---|---|---|---|
| Gur | SUPPORTED | SUPPORTED | **UNSUPPORTED** ("none reported"; PDF reports feature importance for TFT, RF, XGB, MLP) | SUPPORTED (no) |
| Santschi | SUPPORTED (26 cantons) | SUPPORTED (account groups) | SUPPORTED | SUPPORTED |
| Radulescu | SUPPORTED (5 CEE) | SUPPORTED | SUPPORTED (no SHAP/LIME/explain in PDF) | SUPPORTED |
| Valle-Cruz | SUPPORTED (217) | SUPPORTED | SUPPORTED | SUPPORTED |
| Guerrero and Castaneda | SUPPORTED (140) | SUPPORTED | SUPPORTED ("causal framework") | n/a acceptable |
| Yao and Zhu | SUPPORTED | SUPPORTED | SUPPORTED (SHAP) | SUPPORTED (shown) |
| Nonato (dagger) | SUPPORTED | **UNSUPPORTED** ("spending by function" is the input) | PARTLY ("none in abstract" true of abstract only) | SUPPORTED (no) |
| Kisman (dagger) | SUPPORTED | PARTLY / UNVERIFIABLE ("level") | SUPPORTED ("XAI methods") | **PARTLY / likely UNSUPPORTED** ("shown"; secondary source: fidelity and faithfulness scores) |
| Mohith (dagger) | UNVERIFIABLE | UNVERIFIABLE | UNVERIFIABLE | UNVERIFIABLE |
| Missing | Francies (Chicago/NYC budgets; SHAP + SCM + DiCE; explainability score) and Dhungel are in the text but not in the table. | | | |
Caption claim "cells come from the full text where we read it": true for Gur, Santschi, Radulescu, Valle-Cruz, Guerrero, Yao; the Gur explanation cell is nevertheless wrong.

## 3. Method and background citations
| sentence | key | verdict | note |
|---|---|---|---|
| intro: "last year's allocation is adjusted for political priorities and expert judgment [davis1966, jones2005]" | | SUPPORTED | incrementalism; Jones 2005 title-level only |
| intro: "ML can detect non-linear regularities [athey2019, mullainathan2017]" | | SUPPORTED | |
| "Budgeting has long been described as incremental, with occasional large punctuations [jones2005]" | | SUPPORTED (title-level) | |
| "Wagner's law [lamartina2011]"; "composition ... related to growth [devarajan1996, kneller1999, afonso2010]" | | SUPPORTED | |
| "globalisation, military-spending determinants and budget institutions ... drivers of spending patterns [garrett2001, dunne2003, alesina1999]" | | PARTLY | Alesina et al. 1999 is about budget institutions and fiscal performance (deficits), not spending composition |
| "ideology and electoral cycles have been linked to the composition of spending [potrafke2010, bove2017, nordhaus1975, rogoff1988, brender2005]" | | PARTLY | only Potrafke and Bove are about composition; Nordhaus (macro), Rogoff-Sibert (policy cycles), Brender-Drazen (deficits) are not |
| "Shares ... compositional data [aitchison1986]; log-ratio [egozcue2003]; Dirichlet or beta regression [ferrari2004, douma2019]; applied to budget categories [adolph2020]" | | SUPPORTED | |
| "clr ... eps=0.05 [aitchison1986, egozcue2003]" | | SUPPORTED | clr is Aitchison; Egozcue is ilr (acceptable companion) |
| "Tree ensembles remain strong on medium-sized tabular data [grinsztajn2022, shwartzziv2022, borisov2024]" | | SUPPORTED | Grinsztajn abstract: ~10K samples |
| "tabular deep models need careful design [gorishniy2021]"; "feature-tokenising transformer [gorishniy2021]" | | SUPPORTED | |
| results l.92 "tree and linear models being hard to beat on small tabular data [grinsztajn2022, shwartzziv2022]" | | PARTLY | those papers compare trees with deep nets on medium data; nothing on linear models or small data |
| "Split-conformal ... [lei2018, angelopoulos2023]; adapt to heteroscedasticity [romano2019]; can fail when exchangeability fails [barber2023]" | | SUPPORTED | |
| method: "income group (Mondrian variant)" | none | UNSUPPORTED (no cite) | add Vovk et al. or drop label |
| "systematically different error is an equity issue [mehrabi2021]; under-serve disadvantaged groups [obermeyer2019]; error-rate parity [hardt2016]" | | SUPPORTED | |
| "explainers disagree [krishna2022]" | | SUPPORTED | arXiv 2202.01602 |
| "post-hoc explanations can be unstable [alvarezmelis2018, ghorbani2019]" | | SUPPORTED (domain caveat) | both concern neural-network interpretation |
| "manipulable [slack2020]; inferior in high stakes [rudin2019]" | | SUPPORTED | |
| "Shapley-value attributions have specific conceptual problems [kumar2020]" | | SUPPORTED | |
| "removal-based evaluations ... have their own pitfalls [hooker2018, bhatt2020]" | | PARTLY | Hooker (ROAR) supports; Bhatt proposes faithfulness/sensitivity/complexity criteria, not pitfalls |
| "rigorous evaluation of interpretability [doshi2017]" | | SUPPORTED | |
| "Exact TreeSHAP [lundberg2017, lundberg2020]"; "tabular LIME [ribeiro2016]" | | SUPPORTED | |
| "cluster-bootstrap ... years within a country are not independent [cameron2008]" | | PARTLY | supports clustering rationale; their method is the wild cluster bootstrap-t, the manuscript's is a percentile cluster bootstrap |
| "Holm step-down procedure [holm1979]" | | SUPPORTED | |
| "block-wise validation respects temporal dependence [roberts2017, bergmeir2018]" | | PARTLY | Bergmeir et al. show ordinary CV is valid for pure autoregressions; and the manuscript's split is a single hold-out |
| "Persistence is the naive benchmark recommended for forecast comparison [hyndman2006]" | | SUPPORTED | MASE scales by the naive forecast |
| "leakage taxonomy of [kaufman2012]"; "Stacking [wolpert1992]" | | SUPPORTED | Breiman 1996 is the classical NNLS source (optional) |
| "evidence on reallocation frictions [barnes2023]" | | SUPPORTED | governments avoid nominal cuts, especially health and social |
| data citations (wdi, kaufmann2011, eurostat_cofog, oecd_table11, imf_gfs, un2000cofog) | | SUPPORTED | |

## 4. Numbers attributed to other works
| number | source value | verdict |
|---|---|---|
| Nonato 24 annual observations | N = 24, 2000-2023 | SUPPORTED |
| 1 048 synthetic points | 1048 | SUPPORTED |
| R2 up to 0.97 | mean R2 0.97 (random K-fold, augmented), macro outcomes | SUPPORTED, but not spending shares |
| -0.45 (docs only) | mean R2 -0.45, growth and inflation; Gini 0.60 | SUPPORTED, macro outcomes |
| Radulescu five CEE | five | SUPPORTED |
| Valle-Cruz 217 | 217 (1960-2019) | SUPPORTED |
| Guerrero 140 | 140 | SUPPORTED |
| Yang 15 | 15 largest economies, 1990-2020 | SUPPORTED |
| Barnes 1996-2017 | same | SUPPORTED |
| Gur 2008-2024 | Jan 2008-May 2024 | SUPPORTED |
| Santschi 26 cantons | 26 cantons, 36 accounts | SUPPORTED |
| Kisman 2002-2023 | same | SUPPORTED |
| Mohith 12 sectors, FY2005-06 to 2024-25 | not retrievable | UNVERIFIABLE |

## 5. Conference vs journal; reference-list completeness
- All 27 keys cited in main_conference.tex (including tab_gap_conf.tex) exist in references.bib; all 84 keys cited in the journal exist; no bib key is uncited by both papers.
- Cited facts are consistent between the papers for Radulescu (five), Santschi, Gur, Dragulin, Valle-Cruz, Guerrero, Nonato (24 years), Mohith (12 sectors); the two gap tables are cell-identical, so both carry the same Nonato, Gur and Kisman errors.
- Claims made in the conference paper that are cited only in the journal: split-conformal (cite lei2018, angelopoulos2023); Holm correction (holm1979); log-ratio targets (aitchison1986, egozcue2003); Dirichlet regression (ferrari2004); equity concern (mehrabi2021, obermeyer2019). The conference prose also omits Francies and Kisman although the table lists Kisman.

## 6. Novelty wording
Tone is acceptable ("not the first", "conjunction", "non-systematic search", dagger table, appendix says Scopus/WoS/IEEE not yet run). Three overreaches remain: (1) Nonato presented as the closest allocation-prediction study although it models macro outcomes and optimises allocations; (2) "explanations are shown rather than evaluated" ignores Francies and (unverified) Kisman; (3) "each is individually covered" for item (iii) is not established.

## 7. Sentences to change, with suggested replacements
1. sec_related, Nonato sentences (14-17): "Nonato et al.~\cite{nonato2026} use Brazil's federal executed spending by budgetary function (2000--2023; 24 annual observations, augmented with 1\,048 synthetic points) as the \emph{input} of a multi-output XGBoost that predicts GDP growth, inflation and the Gini index, and then apply Bayesian optimisation to search for allocation vectors that satisfy a stated objective; they report $R^2=0.97$ under random K-fold validation on the augmented data, falling to a mean of $-0.45$ for growth and inflation (0.60 for the Gini index) when synthetic data are generated only inside training folds. They do not predict the functional split, use a national functional classification rather than COFOG, and, as far as the abstract shows, report no explanation analysis."
2. tab_gap.tex and tab_gap_conf.tex, Nonato Target: "GDP growth, inflation, Gini given spending by function (allocation by optimisation)".
3. Both tables, Gur Explanation method: "feature importance (TFT, RF, XGB, MLP)".
4. Both tables, Kisman: Target "defence spending (share of GDP, share of spending, per capita)$^{\dagger}$"; Explanations tested "fidelity/faithfulness reported$^{\ddagger}$" with "$^{\ddagger}$ from a secondary summary; publisher page not accessible" (or grade from the paper once read).
5. Add a Francies row (Chicago and NYC municipal budgets 2023--2026; fund allocations; SHAP, causal model, counterfactuals; composite explainability score) to both tables.
6. sec_related Kisman: "Kisman et al.~\cite{kisman2026} study cross-country defence spending (2002--2023) with tree-based models and explainable-AI methods; the target is a single function (defence), not the composition of the whole budget."
7. sec_related Francies: append "(Chicago and New York City budgets; strict temporal hold-out, $R^2=0.959$, prior allocation dominating feature importance, and an explainability score that includes fidelity)".
8. sec_related Mohith: "Mohith et al.~\cite{mohith2026} study sectoral budget allocations in India with classical and deep-learning models (we could not access the abstract or full text and describe only what the title states)." Delete the twelve sectors/FY range/XAI-method/"simple models win" details and the sentence "Their finding ... agrees with ours" until verified; keep "as does the caution about leakage in Nonato et al." only if rewritten as "Nonato et al.'s anti-leakage check likewise shows a collapse of fit".
9. "What we add": "What we add is scope and protocol: an official multi-country COFOG panel with leave-country-out and temporal splits, persistence and peer baselines reported alongside every learner, a cluster-bootstrap and Holm-corrected comparison, and tests of SHAP--LIME agreement, LIME stability, deletion and synthetic ground truth."
10. XAI paragraph: "The two applications just cited display attribution plots without testing whether the attributions are faithful, stable or consistent across methods; a few recent budget studies report fidelity-type scores~\cite{francies2026,kisman2026}, but we found none that compares SHAP with LIME or recovers known drivers, although explainers are known to disagree ..."
11. sec_intro l.5: "Studies of budgets by function or account group are few and mostly single-country~\cite{santschi2024,radulescu2015,nonato2026,mohith2026}, and explanation methods such as SHAP and LIME are rarely tested against each other or against known drivers."
12. Conference intro: "SHAP/LIME~\cite{lundberg2017,ribeiro2016} are rarely tested against each other or against known drivers".
13. Conference related work: "Nonato et al.~\cite{nonato2026} (Brazil, 24 years) model macro outcomes as a function of spending by function and optimise allocations; Mohith et al.~\cite{mohith2026} (India, sectoral allocations; abstract not accessible to us) appears to be the closest allocation-prediction study; Francies et al.~\cite{francies2026} and Kisman et al.~\cite{kisman2026} apply SHAP-type explanations to municipal budgets and defence spending." Delete "the latter finds that gradient boosting and ridge beat deep learning". Replace "Explanations are typically shown, not tested" by "Explanations are rarely tested against each other or against known drivers".
14. Conference methods: add "Holm correction~\cite{holm1979}", "split-conformal~\cite{lei2018,angelopoulos2023}", "log-ratio targets~\cite{aitchison1986,egozcue2003}", "Dirichlet regression~\cite{ferrari2004}", equity "\cite{mehrabi2021,obermeyer2019}".
15. Nzazi: "Nzazi et al.~\cite{nzazi2025} provide a short PRISMA-style review of AI for public expenditure analysis in low-income countries (ten LIC-focused studies) and note that many applications are conceptual or pilot-scale."
16. sec_results l.92: "...consistent with tree ensembles remaining strong on medium-sized tabular data~\cite{grinsztajn2022,shwartzziv2022}; our panels are smaller, so we read this only as a prior."
17. Determinants paragraph: "...budget institutions have been related to fiscal performance~\cite{alesina1999}; ideology has been linked to the \emph{composition} of spending~\cite{potrafke2010,bove2017}, while electoral cycles have been studied mainly in fiscal aggregates~\cite{nordhaus1975,rogoff1988,brender2005}."
18. Removal clause: "removal-based evaluations of attributions, which our deletion test resembles, are confounded by off-distribution inputs unless the model is retrained~\cite{hooker2018}, and quantitative criteria such as faithfulness, sensitivity and complexity have been proposed~\cite{bhatt2020}."
19. sec_method cluster bootstrap: "...because years within a country are not independent, we resample economies as clusters (cf.~\cite{cameron2008}; with few clusters the intervals are approximate)."
20. sec_method: drop "(Mondrian variant)" or cite a Mondrian conformal reference.
21. sec_method temporal split: "(a single-origin hold-out; blocked validation is advised for dependent data~\cite{roberts2017}, although ordinary cross-validation can be valid for purely autoregressive models~\cite{bergmeir2018})".
22. "post-hoc explanations of neural networks can be unstable~\cite{alvarezmelis2018,ghorbani2019}".
23. Remove "(we could verify the first figure but not the second from the accessible record)" from sec_related and the matching line 21 of docs/guides/05_known_issues_and_future_work.md; both Nonato figures are in the Crossref abstract.

## 8. Not verified by tool
Mohith (all details); Kisman (full text; MDPI 403; secondary source only); Dhungel (abstract via catalogue pages only); Caravaggio, Di Stefano, Chand, Nguyen, Zhang (carried over from review_B); Jones 2005 and Alesina 1999 (no abstract; judged by title); Ghorbani, Mehrabi, Obermeyer, Hardt, Athey, Mullainathan, Medeiros, Goulet (judged by title and general knowledge, not re-read).
