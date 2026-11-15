# Review B: literature and reference audit (independent)

Date: 2026-11-15. Scope: papers/main_journal.tex, papers/main_conference.tex, papers/sections/*.tex, papers/references.bib (57 entries, 53 cited).
Method: Crossref API (all 44 DOIs in the bib re-pulled: authors, year, venue, volume, pages), arXiv API (arXiv-only entries), local PDFs in literature/ (abstract and body), WebSearch (Dhungel, Mohith). HTTP checks used an honest user agent and HEAD requests; no header spoofing. No paper or code was edited; nothing committed or pushed.
Verdicts: SUPPORTED / PARTLY / UNSUPPORTED / UNVERIFIED (could not read abstract or body by tool).

## 1. Claim-by-claim table (every cited key)

### 1a. ML for budgets, funding allocation, SDGs
| key | claim in our paper | evidence found | verdict |
|---|---|---|---|
| gur2025 | ML/DL forecasters on Turkiye monthly budget expenditure 2008-2024 incl. crises; aggregate | Crossref abstract: Jan 2008-May 2024, GFC, euro crisis, COVID, ML+DL, evaluated with a Temporal Fusion Transformer | SUPPORTED |
| dragulin2025 | Benchmarks TCN, LSTM and GRU against SARIMA/VAR | PDF: benchmarks LSTM and TCN (plus ANN/SVM) against SARIMA, VAR and ECM; "GRU" occurs once in the text | PARTLY: replace "GRU" by what the paper uses, add ECM |
| yang2023 | GRU for 15 large economies, beats ARIMA, ETS, SVR, XGBoost | Abstract and PDF: GRU vs ARIMA, SVR, ETS, XGBoost, CNN, LSTM; 15 largest economies, 1990-2020 | SUPPORTED |
| barnes2023 | OECD reallocation across COFOG 1996-2017; sounder governance and tighter fiscal rules reallocate more; no predictive model | OECD WP 1785 abstract says exactly this; also finds governments avoid nominal cuts (health, social) | SUPPORTED (also supports the "reallocation frictions" use in sec_results) |
| nzazi2025 | Survey of AI for public expenditure in LICs "concluding that explainable, allocation-level systems remain rare" | PDF is a narrative review; the words explain*, XAI, interpretab* never occur; it concludes studies are "conceptual or pilot-scale" and more empirical work is needed | UNSUPPORTED for the stated conclusion. Rephrase |
| santschi2024 | XGBoost and CatBoost on Swiss cantonal accounts, human-AI vs experts, one country, account groups, no explanation analysis | PDF: 36 accounts, 26 cantons, XGBoost and CatBoost, AI beats experts in 3 of 4 account groups, decision-maker experiment. It is a 4-page ICIS short paper with preliminary results | SUPPORTED, but "closest methodological precedent" rests on a short preliminary paper |
| radulescu2015 | FFNN forecasts of spending by function for **four** CEE economies (sec_related, tab_gap, tab_gap_conf, main_conference say 4) | Abstract and body: **five** countries (Hungary, Poland, Czech Republic, Bulgaria, Romania), five expenditure indicators | PARTLY: factual error, fix to five |
| valle2022 | MLP + multi-objective GA, 217 countries, relates spending to outcomes "rather than predicting how a budget is split" | PDF: counts correct (World Bank 1960-2019, 217 countries); but the paper asks how to distribute public spending to raise GDP and cut inequality, i.e. it does propose allocations | PARTLY: soften |
| guerrero2022 | "Agent-based" model of spending vs SDG indicators, 140 countries | Abstract: "bottom-up causal framework", 140 countries, development gaps to 2030; "agent-based" not in abstract | PARTLY (verify in body or reword) |
| nguyen2026 | Non-linear association between government expenditure and SDG progress | PDF abstract: panel 2000-2024, conditional and non-linear, thresholds | SUPPORTED |
| caravaggio2025 | Predicts which actors win competitive EU rural-development funds | PDF: ML classification of beneficiaries, EU funding 2014-2020 in Italy, EAFRD calls | SUPPORTED |
| distefano2025 | Need-allocation paradox in Italian recovery-plan calls | PDF: NextGenEU childcare calls, predicts non-participating municipalities, high-need regions disadvantaged | SUPPORTED |
| chand2022 | Gap between funding and expenditure in Australia's NDIS | PDF abstract | SUPPORTED |
| yao2025 | SHAP on "hospital budget costs"; gap table says "one hospital" | Abstract: XGBoost+SHAP R2 0.89, drivers "smoking status, BMI, age" (patient-level insurance-type cost data, not a hospital budget); Informatica, a small regional journal | PARTLY: soften to patient-level cost prediction; "one hospital" unverifiable |
| zhang2026 | SHAP with gradient boosting for enterprise performance | Title: XGBoost-SHAP, digital transformation and enterprise performance | SUPPORTED (title); off-topic analogy |
| nonato2026 | Brazil federal spending by function, multi-output XGBoost + Bayesian optimisation, N=24, 1,048 synthetic points, leakage-free check R2 0.97 to -0.45, no COFOG, no explanation method | Crossref abstract confirms N=24, 1,048 synthetic, R2 0.97, XGBoost+TPE; abstract truncated before the leakage check value and says nothing on explanations | SUPPORTED for the first points; UNVERIFIED for "-0.45" and "no explanation method" in the journal version |
| kisman2026 | Cross-country defence spending 2002-2023 with SHAP, PDP, ALE | Abstract: 2002-2023, XAI to quantify drivers; PDP/ALE not named | PARTLY (detail unverified) |
| dhungel2025 | Exploratory case study of AI decision support for budgeting in Germany | Publisher and university pages: German state/municipal budget preparation, exploratory case study, LLMs, anomaly detection prototype | SUPPORTED |
| francies2026 | SHAP, causal and counterfactual framework for urban budget allocation (preprint) | Crossref abstract: SHAP + SCM do-calculus + DiCE, Chicago and NYC budgets; Research Square preprint | SUPPORTED |
| mohith2026 | India Union Budget, 12 sectors, FY2005-06 to 2024-25, GB/ridge beat LSTM/GRU/TCN/Transformer, SHAP+permutation+LIME+intervals, two held-out years | Crossref confirms the paper exists (IEEE ICMLT 2026); no abstract in Crossref; searches found none | UNVERIFIED by tool. This is the "closest in spirit" paper: re-read its abstract before submission |

### 1b. XAI
| key | claim | evidence | verdict |
|---|---|---|---|
| lundberg2017 | SHAP | arXiv 1705.07874, Lundberg and Lee (NeurIPS 2017) | SUPPORTED |
| lundberg2020 | TreeSHAP | Nat. Mach. Intell. 2(1):56-67, 10 authors match | SUPPORTED |
| ribeiro2016 | LIME | KDD 2016 pp. 1135-1144 | SUPPORTED |
| krishna2022 | Explainers disagree | arXiv 2202.01602 (disagreement problem) | SUPPORTED, but a preprint |
| alvarezmelis2018 | Post-hoc explanations unstable | arXiv 1806.08049, robustness of interpretability methods | SUPPORTED; bib has no venue (workshop/preprint) |
| slack2020 | LIME/SHAP manipulable | AIES 2020 pp. 180-186 | SUPPORTED |
| rudin2019 | Interpretable beats post-hoc in high stakes | NMI 1(5):206-215 | SUPPORTED |
| doshi2017 | Call for rigorous evaluation | arXiv 1702.08608 | SUPPORTED (preprint) |
| kaufman2012 | Leakage taxonomy | TKDD 6(4) art. 15 | SUPPORTED |

### 1c. Models, evaluation, compositional, data sources
| key | claim | evidence | verdict |
|---|---|---|---|
| chen2016xgboost, ke2017, prokhorenkova2018, breiman2001 | learners | metadata match | SUPPORTED |
| grinsztajn2022 | trees "dominate typical tabular data"; "hard to beat on small tabular data" (sec_results) | NeurIPS 2022 benchmark paper is about medium-sized data (roughly 10k+ rows) | PARTLY: "small" is a stretch |
| aitchison1986 | TVD "appropriate for compositions" | Aitchison advocates log-ratio geometry and Aitchison distance, not total variation | PARTLY: cite Aitchison for closure, justify TVD separately |
| adolph2020 | compositional treatments of budget shares | Abstract: compositional methods for budget categories (US states 1984-2009) | SUPPORTED (best-matched source) |
| roberts2017 | block-wise validation for temporal dependence | Abstract: CV with temporal/spatial/hierarchical structure (ecology) | SUPPORTED |
| un2000cofog, eurostat_cofog, oecd_table11, wdi, imf_gfs, kaufmann2011 | data sources | URL table below | SUPPORTED as data citations |
| hyndman2006, un2015agenda, blanchard2002, wildavsky1969 | not cited | | uncited bib entries |

### 1d. Public economics (one sentence, 11 keys)
| key | claim | evidence | verdict |
|---|---|---|---|
| lamartina2011 | Wagner's law | Abstract: 23 OECD countries, panel cointegration, consistent with Wagner's law | SUPPORTED |
| devarajan1996, kneller1999 | composition and growth | titles | SUPPORTED |
| garrett2001 | globalisation as driver | abstract: globalisation and welfare effort, OECD | SUPPORTED |
| dunne2003, alesina1999 | military demand; budget institutions | titles | SUPPORTED |
| nordhaus1975, rogoff1988, brender2005 | elections shift fiscal policy | titles/abstract; rogoff1988 bib points to the 1985 IFDP, not the journal paper | SUPPORTED; metadata issue |
| jones2005 | mostly incremental with punctuations | title only ("A model of choice for public policy") | PARTLY: better source is Baumgartner and Jones or True, Jones and Baumgartner |

## 2. Metadata verification against Crossref (mismatches)
All 44 DOIs resolve in Crossref and titles match. Real mismatches:
1. dragulin2025: bib surname "T{\u{a}}rc{\u{a}}" vs Crossref "Tăbîrcă" (Alina-Iuliana).
2. krishna2022: bib has 7 authors including "Pombra, Javin" and "Wu, Steven"; arXiv and Crossref list 6: Krishna, Han, Gu, Wu (Zhiwei Steven), Jabbari, Lakkaraju. Year 2022 (arXiv) vs 2023 (Research Square DOI). Preprint status not stated in the bib.
3. rogoff1988: key says 1988, bib cites the 1985 Fed IFDP No. 271 (doi 10.17016/ifdp.1985.271, "volume 1985.0"). The journal article is Review of Economic Studies 55(1):1-16, 1988, doi 10.2307/2297526 (Crossref-verified).
4. chand2022: bib number 2; Crossref says volume 2, issue 1.
5. jones2005: key 2005, bib year 2004 (Crossref online date); make key/year consistent with print year.
6. nzazi2025: bib treats it as a journal article; it is conference proceedings (EUSPN 2025) in Procedia CS 272.
7. dhungel2025: Crossref type is an LNCS book chapter; add series.
8. gur2025: Crossref has no volume/issue (article id 25); add when available.
9. barnes2023: Crossref lists no authors (report type); Barnes, Cournede, Pascal confirmed from the PDF cover. The docs/19 "CHECK" is a false alarm, as are those for chen2016xgboost, ribeiro2016, kaufman2012 and slack2020 (title-similarity artefacts only).
10. lamartina2011: title contains a curly apostrophe; confirm it compiles.
11. roberts2017: "and others" for 14 authors; acceptable but inconsistent with full lists elsewhere.
12. No DOI in bib where one exists: grinsztajn2022 (10.52202/068431-0037).

## 3. Links, DOIs, placeholders
HTTP (HEAD, honest user agent):
- 403, unverifiable by tool (publisher bot protection; each DOI exists in Crossref): doi.org for 10.1080/1331677X.2015.1081828, 10.1080/713673166, 10.1093/jopart/mui018, 10.1111/ecog.02881, 10.1145/2382577.2382579, 10.1145/2939672.2939778, 10.1145/2939672.2939785, 10.1145/3375627.3375830, 10.1162/003355302320935043, 10.1787/56dda017-en, 10.2307/2296528, 10.3390/electronics14204047, 10.3390/math11143085, 10.3390/systems14030283; also data.imf.org (3 URLs) and sdmx.oecd.org.
- 202: 10.1109/ICMLT69916.2026.11689177 and 10.1111/j.1468-0475.2010.00517.x.
- 404, dead: https://unstats.un.org/unsd/classifications/Econ/cofog (un2000cofog URL); parent /Econ/ returns 200. Fix and add access dates.
- 404, expected placeholder: https://doi.org/10.5281/zenodo.XXXXXXX.
- doi.org/10.2298/pan240929025g: first request failed (URLError), curl returned 302 and Crossref resolves it: fine.
- **https://github.com/Pranav-chaudhari-2006/GovAllocXAI returns 200 (public)**, contrary to the "not pushed yet" note. git: local main is 16 commits ahead and 0 behind origin/main, whose three existing commits (Oct 2026) are by another account (joshiaditi18, frontend/Render backend). A push is a fast-forward. docs/16 still says the repo is 404, and the manuscript says "[repository to be made public at submission]": both stale.
- All other URLs (arXiv, OECD data explorer, World Bank, Eurostat, ICIS AISeL, NeurIPS, UN SDG) return 200.

Placeholders remaining:
1. main_journal.tex line 126: `https://doi.org/10.5281/zenodo.XXXXXXX` and "[DOI to be inserted after upload]".
2. main_journal.tex line 129: "[repository to be made public at submission]" and "will be archived at Zenodo".
3. sections/sec_discussion.tex line 14: "(DOI to be added on acceptance)".
4. sections/sec_discussion.tex line 17: "[Authors to confirm before submission.]" in the generative-AI statement. The same sentence says the authors "verified all references against the source documents"; this audit found errors (Radulescu, Krishna, Dragulin, Nzazi), so the sentence is currently not accurate.
5. The text cites "search strings in the repository" and an "Appendix" for the literature search; they must exist before submission.

## 4. Literature survey strength by area
| area | cited | assessment |
|---|---|---|
| (a) public finance, COFOG, budget composition | Barnes 2023, Adolph 2020, Wagner, Devarajan, Kneller, political-cycle trio, Jones | Moderate for a CS venue, thin for Q1 public economics: no composition-ideology work, no fiscal-rule literature, no composition-growth work of the Afonso-Furceri type, no COFOG manual |
| (b) ML for budgets, forecasting | about 14 items, many from low-visibility venues | Niche well covered; macro-ML forecasting canon missing |
| (c) XAI evaluation | Lundberg x2, Ribeiro, Krishna, Alvarez-Melis, Slack, Rudin, Doshi-Velez | Good core; no removal/faithfulness benchmarks or SHAP-critique papers although a faithfulness test is a headline result |
| (d) compositional, Dirichlet, CLR | Aitchison 1986, Adolph 2020 | WEAK: the paper uses Dirichlet regression, log-ratio targets and TVD with no source for Dirichlet regression or ilr/clr |
| (e) conformal prediction | none | MISSING: conformal intervals are promised as future work |
| (f) tabular DL vs trees | Grinsztajn only | THIN: an MLP and a feature-tokenising transformer are run without citing Gorishniy et al. |
| (g) fairness | none | MISSING: the finding that errors are 2-3 times larger for lower-income economies is an equity issue |
| methods used but uncited | stacking, cluster bootstrap, Holm correction, block CV | add sources |

### Verified missing works (checked via Crossref or arXiv API on 2026-11-15)
Compositional and Dirichlet
- Egozcue, Pawlowsky-Glahn, Mateu-Figueras, Barcelo-Vidal (2003) Isometric logratio transformations for compositional data analysis. Math. Geology. doi 10.1023/A:1023818214614
- Douma, Weedon (2019) Analysing continuous proportions in ecology and evolution: a practical introduction to beta and Dirichlet regression. Methods Ecol. Evol. doi 10.1111/2041-210X.13234
- Ferrari, Cribari-Neto (2004) Beta regression for modelling rates and proportions. J. Applied Statistics. doi 10.1080/0266476042000214501

Conformal
- Angelopoulos, Bates (2023) Conformal prediction: a gentle introduction. Found. Trends Mach. Learn. doi 10.1561/2200000101 (arXiv 2107.07511)
- Lei, G'Sell, Rinaldo, Tibshirani, Wasserman (2018) Distribution-free predictive inference for regression. JASA. doi 10.1080/01621459.2017.1307116
- Romano, Patterson, Candes (2019) Conformalized quantile regression. arXiv 1905.03222 (NeurIPS 2019)
- Barber, Candes, Ramdas, Tibshirani (2023) Conformal prediction beyond exchangeability. Ann. Statist. doi 10.1214/23-AOS2276

Tabular DL vs trees
- Shwartz-Ziv, Armon (2022) Tabular data: deep learning is not all you need. Information Fusion. doi 10.1016/j.inffus.2021.11.011
- Borisov, Leemann, Sessler, Haug et al. (2024) Deep neural networks and tabular data: a survey. IEEE TNNLS. doi 10.1109/TNNLS.2022.3229161
- Gorishniy, Rubachev, Khrulkov, Babenko (2021) Revisiting deep learning models for tabular data. arXiv 2106.11959 (NeurIPS 2021)

XAI evaluation
- Hooker, Erhan, Kindermans, Kim (2018) A benchmark for interpretability methods in deep neural networks. arXiv 1806.10758 (NeurIPS 2019)
- Kumar, Venkatasubramanian, Scheidegger, Friedler (2020) Problems with Shapley-value-based explanations as feature importance measures. arXiv 2002.11097 (ICML 2020)
- Bhatt, Weller, Moura (2020) Evaluating and aggregating feature-based model explanations. arXiv 2005.00631 (IJCAI 2020)
- Ghorbani, Abid, Zou (2019) Interpretation of neural networks is fragile. AAAI. doi 10.1609/aaai.v33i01.33013681

Fairness
- Mehrabi, Morstatter, Saxena, Lerman, Galstyan (2021) A survey on bias and fairness in machine learning. ACM Comput. Surv. doi 10.1145/3457607
- Obermeyer, Powers, Vogeli, Mullainathan (2019) Dissecting racial bias in an algorithm used to manage the health of populations. Science. doi 10.1126/science.aax2342
- Hardt, Price, Srebro (2016) Equality of opportunity in supervised learning. arXiv 1610.02413 (NeurIPS 2016)

ML in economics and forecasting
- Athey, Imbens (2019) Machine learning methods that economists should know about. Annu. Rev. Econ. doi 10.1146/annurev-economics-080217-053433
- Mullainathan, Spiess (2017) Machine learning: an applied econometric approach. J. Econ. Perspectives. doi 10.1257/jep.31.2.87
- Medeiros, Vasconcelos, Veiga, Zilberman (2021) Forecasting inflation in a data-rich environment: the benefits of machine learning methods. JBES. doi 10.1080/07350015.2019.1637745
- Goulet Coulombe, Leroux, Stevanovic, Surprenant (2022) How is machine learning useful for macroeconomic forecasting? J. Appl. Econometrics. doi 10.1002/jae.2910
- Makridakis, Spiliotis, Assimakopoulos (2020) The M4 competition. Int. J. Forecasting. doi 10.1016/j.ijforecast.2019.04.014

Public finance
- Afonso, Furceri (2010) Government size, composition, volatility and economic growth. Eur. J. Polit. Econ. doi 10.1016/j.ejpoleco.2010.02.002
- Easterly, Rebelo (1993) Fiscal policy and economic growth. J. Monet. Econ. doi 10.1016/0304-3932(93)90025-B
- Potrafke (2010) Does government ideology influence budget composition? Empirical evidence from OECD countries. Econ. Governance. doi 10.1007/s10101-010-0092-9
- Bove, Efthyvoulou, Navas (2017) Political cycles in public expenditure: butter vs guns. J. Comp. Econ. doi 10.1016/j.jce.2016.03.004
- Davis, Dempster, Wildavsky (1966) A theory of the budgetary process. Am. Polit. Sci. Rev. doi 10.2307/1952969 (classic incrementalism source; the bib's wildavsky1969 is uncited)

Methods used in the paper
- Wolpert (1992) Stacked generalization. Neural Networks. doi 10.1016/S0893-6080(05)80023-1
- Cameron, Gelbach, Miller (2008) Bootstrap-based improvements for inference with clustered errors. Rev. Econ. Stat. doi 10.1162/rest.90.3.414
- Bergmeir, Hyndman, Koo (2018) A note on the validity of cross-validation for evaluating autoregressive time series prediction. Comput. Stat. Data Anal. doi 10.1016/j.csda.2017.11.003
- Holm (1979), Scand. J. Statist. 6:65-70: no Crossref DOI found; cite without DOI after checking the print record. Not verified by me, so confirm before adding.
Rejected during checking: two guessed DOIs returned 404 (not cited here); "Explaining by removing" (Covert, Lundberg, Lee, JMLR 2021) was not found in Crossref and is NOT verified.

## 5. Citation balance and dubious items
- 53 cited keys: 6 data/standards, about 20 ML/AI-budget items, 9 XAI, about 8 ML tools and methods, 11 public economics. No self-citation (good); but the authors' own v1 paper, discussed at length, is not cited (cite it if it was published or deposited).
- Recency: 13 of roughly 36 scholarly items are 2025-26 (gur, dragulin, nzazi, caravaggio, distefano, yao, nguyen, zhang, nonato, kisman, dhungel, mohith, francies). The methods foundation (XAI, statistics, tabular ML) is all pre-2023 and the economics block 1969-2011; nothing on conformal, tabular DL or XAI evaluation from 2023-26.
- Dubious or weak items:
  1. Preprints: krishna2022, francies2026, alvarezmelis2018, doshi2017; only Francies is labelled "(preprint)" in the text.
  2. Low-visibility venues carry the novelty claim: yao2025 (Informatica), nzazi2025 (Procedia CS conference), mohith2026 (IEEE conference), dhungel2025 (EGOV), dragulin2025 and kisman2026 (MDPI), gur2025. None looks predatory, but the "closest work" comparisons rest on short papers.
  3. Decorative or off-topic: zhang2026 (enterprise performance), yao2025, nguyen2026; the public-economics sentence cites mostly titles of 1999-2005 growth papers.
  4. Claim/source mismatches: Radulescu (4 vs 5), Nzazi (conclusion), Valle-Cruz ("rather than predicting"), Aitchison (TVD), Grinsztajn (small data), Dragulin (GRU), Guerrero ("agent-based").
  5. Novelty statement "to the best of our literature search, no study..." depends on a search protocol "in the repository"/"Appendix" that must be real and dated.
  6. Four uncited bib entries: blanchard2002, hyndman2006, un2015agenda, wildavsky1969.

## 6. Top 10 fixes
1. Radulescu et al.: change "four" to "five" CEE economies in sec_related, tab_gap, tab_gap_conf and main_conference.
2. Rewrite the Nzazi claim: the review concludes applications are conceptual or pilot-scale, not that explainable allocation-level systems are rare.
3. Fix bib metadata: Dragulin surname (Tăbîrcă); Krishna author list (6 authors, Zhiwei Steven Wu, no Pombra) and mark preprint; Chand issue 1; Rogoff-Sibert to RES 55(1) 1988 doi 10.2307/2297526; Nzazi as conference; fix the dead UN COFOG URL and add access dates.
4. Resolve placeholders (Zenodo DOI, "[repository to be made public]", "DOI to be added on acceptance", "[Authors to confirm]"), update the Data/Code wording (the GitHub repo already returns 200, fast-forward push possible), and drop "authors verified all references" until items 1-3 and 5 are closed.
5. Soften or verify precedent claims: Valle-Cruz, Yao (patient-level cost data), Guerrero, Santschi (short paper), Kisman (PDP/ALE), Nonato (-0.45, no explanations), and read the Mohith abstract (UNVERIFIED).
6. Add compositional foundations (Egozcue 2003; Douma-Weedon 2019; Ferrari-Cribari-Neto 2004) and justify TVD separately instead of attributing it to Aitchison.
7. Add conformal references (Angelopoulos-Bates 2023, Lei 2018, Romano 2019, Barber 2023).
8. Add XAI-evaluation and tabular-DL references (Hooker, Kumar, Bhatt, Ghorbani; Gorishniy, Shwartz-Ziv-Armon, Borisov) and restrict the Grinsztajn wording to medium-sized data.
9. Add a fairness/equity paragraph (Mehrabi 2021, Obermeyer 2019, Hardt 2016) tied to the 2-3x larger errors for lower-income economies, and cite Wolpert, Cameron-Gelbach-Miller, Holm, Bergmeir for stacking, cluster bootstrap, multiple comparisons and CV design.
10. Strengthen public-finance and ML-in-economics anchoring (Afonso-Furceri 2010, Potrafke 2010, Bove 2017, Davis-Dempster-Wildavsky 1966, Athey-Imbens 2019, Mullainathan-Spiess 2017, Goulet Coulombe 2022, Medeiros 2021).
