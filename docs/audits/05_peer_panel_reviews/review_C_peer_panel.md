# Review C: simulated peer-review panel for GovAllocXAI v2

Panel: **R1** = senior public-finance/economics reviewer (Socio-Economic Planning Sciences / Government Information Quarterly). **R2** = senior ML/XAI reviewer (Expert Systems with Applications), who also sits on an IEEE conference programme committee.

Material read:
- `papers/main_journal.tex`, `papers/main_conference.tex`, `papers/sections/*`, `papers/tables/*`, `figs_all.tex`, `figs_conf.tex`, `results_macros.tex`, `references.bib`.
- Figures 1, 7, 9 and 10 viewed directly. Figures 2-6 and 8 were seen only as thumbnails inside the compiled PDFs.
- Compiled PDFs in the scratchpad (`bf_Journal_Q1/main.pdf`, 46 pages; `bf_Conference_IEEE/main.pdf`, 5 pages).
- `src/pages/Home.jsx` and `src/pages/Guide.jsx`.

Nothing was edited, committed or pushed. This file is the only thing written.

**The compiled PDFs are stale relative to the sources.** The conference Table I caption in the PDF says "judged from title and metadata only"; the source says "abstract only". The `sec_related.tex` hash also differs between the scratchpad build and the repo. Recompile before any layout judgement is final.

---

## 0. Verdict at a glance

| Item | Recommendation | P(accept at Q1 journal) | P(accept at an IEEE-type conference) |
|---|---|---|---|
| Journal paper as written (ESWA target) | **Reject / major revision at best.** Desk-reject risk about 35%. | **about 8-12%** | n/a |
| Journal paper reframed (see section 6) at SPS / GIQ / Data & Policy | Major revision | **about 25-35%** | n/a |
| Conference paper as written | Minor-to-major revision | n/a | **about 55-65%** (generic IEEE-sponsored conference); about 25% at a selective one |

The data work and the honesty of the negative results are the strongest assets. The weakest points are:
- The headline claim (a learned correction beats persistence) rests on a lower CI bound of 0.025 pp, 36 clusters and one COVID-dominated 5-year window.
- Novelty is claimed through a conjunction of four self-chosen criteria.
- The "constraint-aware engine" is a textbook projection that the paper itself shows does not help.
- The paper is a lab notebook. Section 5.9 alone is a 12-item wall of text, and the Methods do not describe half of what is reported.

---

## 1. R1 report (public finance / policy)

### 1.1 Relevance and use case
Predicting what a government "should" allocate across COFOG functions is not a task any finance ministry has. The paper never says who would use the output at what moment.

- Ministries know last year's outturn. Statistical offices publish COFOG with a lag of about 12-24 months. In a real budgeting cycle "last year's allocation" (the strong baseline) is not yet available when the next budget is drafted.
- The model uses **contemporaneous** covariates x_t (GDP growth, unemployment, debt in year t). Those are realised values unknown at budgeting time. The "one-step-ahead forecast" is a nowcast with realised covariates. The paper concedes this only for the multi-year module ("true future macro variables", `sec_results.tex:44`).
- A peer-based "recommendation" is descriptive ("what comparable economies do"), not normative. Calling the output a "recommendation" and rendering "Green = consider increasing, red = consider decreasing" on the website (`Home.jsx`, table caption) invites exactly the normative reading the Discussion warns against.
- The defensible use cases are (a) gap-filling and nowcasting missing COFOG for statistical agencies and international organisations, (b) peer benchmarking, and (c) a data/benchmark resource. Only (b) and (c) are actually supported, and they are not the framing.

### 1.2 Is the task well posed?
- **Target mixing.** The "16 COFOG functions" mix hierarchy levels. Agriculture, energy, industry/construction, transport, communication and R&D are COFOG groups under division 04 (economic affairs). Water supply is group 06.3, inside division 06 (housing). Environment and health are divisions. The residual "other/unallocated" silently absorbs 04.1, 04.7 and 04.9 (general economic affairs, other industries, economic-affairs n.e.c.). It is not a function and may be large. It is predicted and scored like one (K=17, `sec_method.tex:2`). State whether housing (06) includes water (06.3), or double counting occurs. Report the residual's mean share.
- **"Allocation" is outturn.** The title says "allocation" and "budget"; the data are executed general-government expenditure. The intro caveat (`sec_intro.tex:15`) is correct but buried. Put "executed" in the title or abstract.
- **TVD is a sound metric** (half the L1 distance equals the share of budget to move). Two caveats:
  - TVD is dominated by large functions (social protection about 30%, health about 15%). No relative or Aitchison-type error is shown, so "no gain" for small functions is invisible.
  - **MAE is not an independent metric.** For K=17, TVD = 8.5 x MAE (3.62/0.425 = 8.5; 10.77/1.267 = 8.5; for K=10 it is 5 x MAE). The MAE columns in Tables A1/A2 are padding. Drop them, or replace with a per-function weighted error.
- **TVD is too small to interpret without a reference.** 3.5 pp versus 3.6 pp is meaningless to a policy reader unless expressed relative to year-to-year change. Persistence misses by 3.6 pp while the validation-window miss is 2.26 pp (`tab_E_hist`), so the test window is about 60% harder (COVID). Say so in the text.

### 1.3 Domain omissions
- Nothing on the institutional literature the paper itself cites (Jones/Baumgartner punctuated equilibrium; Davis-Dempster-Wildavsky incrementalism). The result "persistence is hard to beat" is the **expected** result from that literature. The paper cites it (`sec_related.tex:14`) but then presents the finding as discovery.
- Fiscal-rule, election and IMF-programme data were tested (`sec_results.tex:52`) and found useless. That is a good robustness check but gets only one paragraph. It is relevant to R1's question "why should a model with only macro features know anything about priorities?".
- Interest payments, debt service and one-off bank-bailout spending sit in COFOG 01 and drive the "shock" years. No treatment.

### 1.4 Real-world value claims
- Home.jsx "Confidence: High/Medium/Low" is derived from a novelty distance, not calibrated probability. The paper's own conformal intervals **under-cover** low-income economies (47% and 61% at the nominal 80%). The UI nonetheless shows "likely range (8 in 10 cases)" for every country. This is a user-facing over-claim.
- For countries with history, the website shows "AI suggestion vs last actual", "Budget to move", "Biggest increase/decrease". The paper shows that on the wide panel the stack is significantly **worse** than persistence in annual updates (`sec_results.tex:32`). The UI therefore recommends deviations from a forecast the authors know is better than the model.

---

## 2. R2 report (ML / XAI)

### 2.1 Architecture justification
| Component | Verdict |
|---|---|
| Annual delta learner (y_{t-1} + f(x_t, y_{t-1})) | Sensible. But the gain over persistence is 0.14 pp, lower CI bound 0.025 pp, hybrid better on only 53% of rows, 36 clusters, one 5-year test window. The best single learner is RF (3.47), not the pre-declared hybrid (3.48); five learners with five variants each is a forking-paths setting. The CLR hybrid is indistinguishable from persistence (p = 0.72 / 0.89). The "learned gain is small but real" highlight is not robust. |
| Cold-start peer learning | The baseline is weak (income-group mean, 4 classes). Ridge is **worse** than this mean (11.98 vs 11.34), which signals under-tuned baselines. Missing: region x income mean, log-GDP-per-capita regression, k-NN on GDPpc. Panel B (health R² 0.63 vs peer 0.31) is largely GDP-per-capita; ridge gets 0.50 (`sec_results.tex:19`), so most of the "beats peers" is a straw-man effect. |
| NNLS stack | Weights per component, fitted on a 3-year validation window (about 100 rows). In annual mode on A10 it is significantly worse than persistence: overfitting, admitted in the text. In cold start it ties a Dirichlet regression (13.69 vs 13.77) and a k-NN predictor (13.73), and fails Holm on A16. The stack is **not justified** over the simplest alternative, yet it is in the title/abstract/website as "the best model". Also: NNLS does not enforce sum-to-one; state the normalisation. |
| Bounded-simplex projection | Textbook (water-filling / clip(y + lambda 1); Held et al. 1974, Duchi et al. 2008). Verified against SLSQP to 3.6e-15 (a unit test, not a result). Bounds from quantiles are arbitrary; the tight ones **hurt** (37% clipped, TVD 3.65 vs 3.48); no statutory constraints exist anywhere in the data. Title says "Constraint-Aware"; the evidence says it is a post-processing step. |
| SHAP/LIME evaluation | Mildly novel as an evaluation, but see 2.3. |
| Conformal intervals | Mentioned in one sentence (`sec_results.tex:47`), no method description. Out-of-fold residuals from grouped CV are not exchangeable with a new economy; per-component intervals ignore the simplex constraint. Conclusion lists conformal intervals as **future work** (`sec_conclusion.tex:3`), contradicting the Results. |

### 2.2 Baseline fairness and leakage
- **Imputation leakage.** Features are filled by linear interpolation (uses future values), edge-fill and a region x income x year **median** computed on the whole table before CV (`sec_data.tex:17`). Gov. expense %GDP is 45.7% imputed, tax revenue 43.2%, debt 69.3% (`tab_features`). Gov. expense %GDP is a top-SHAP feature for general public services (Fig. 7). Held-out economies' features are therefore partly peer medians, and peer medians include test economies. Compute imputation inside training folds, or show the result excluding rows with high imputed share.
- **Near-leakage in Panel B.** Targets are health/defence/education spending %GDP, but "Gov. expense %GDP" (the total) is a feature. Features that bound the target are exactly what the paper criticises in v1. Re-run Panel B without Gov. expense, tax revenue, and debt.
- **Population size as an identity proxy.** log10 population dominates 9 of 17 columns in Fig. 7. With 36 economies, tree models can partially identify countries. In leave-country-out this is harmless, but SHAP "plausibility" then reads size, not mechanism.
- **Panels differ.** A10 mixes Eurostat/OECD with IMF (which has cross-source differences: median at most 0.07 pp but r >= 0.984) and has a different K. TVD numbers across panels (10.5 vs 13.8) are not comparable and the text sometimes places them side by side.
- **Temporal protocol.** One split (train <= 2019, test 2020-24), with test and the shocks coinciding. Validation 2017-19 is used for stack weights, then "test used once". Show a rolling-origin result for the headline and drop the "(COVID) hard test" vs "typical year" ambiguity.

### 2.3 XAI claims
- "SHAP is faithful" (highlight, abstract, conclusion). The test is: reset 3 top-SHAP features to the mean and measure prediction change vs 3 random features. Ratios of 2-3.8x are weak evidence. Any feature-importance ranking (including permutation importance) passes, and a mean-replacement test produces off-manifold inputs. TreeSHAP of a tree model being "faithful to the model" is close to tautological. Say "SHAP concentrates on features that move the prediction"; compare against permutation importance and gain importance.
- The synthetic ground-truth test (`sec_results.tex:51`) reports **precision@3 = 0.67 for both TreeSHAP and LIME**, falling to 0.52/0.43 with correlated copies. That is a contradicting result and should be in the abstract rather than buried.
- Case studies show opposite signs for the leading feature between SHAP and LIME (Fig. 8). The abstract's "top-5 sign agreement 0.85" sounds reassuring, but with a baseline of 0.5 for random signs and most top-5 features being monotone development proxies, the agreement is partly trivial. Report a null (e.g. permuted-feature) baseline.
- SHAP is computed on the XGBoost member, but the product recommends the stack. Section 5.9 admits the explanations agree only at rho = 0.29-0.42. So the "explainability" shown on the website (top_shap) is an explanation of a different model. Either explain the blend, or ship kNN and its transparent nearest-economies explanation.

### 2.4 Statistical rigour
- **Cluster bootstrap with 3 clusters.** Low-income group = 3 economies / 30 country-years (`tab_income`). The CI "23.7-40.9" and max/min ratio CI "2.09-3.85" (`sec_results.tex:46`) are not meaningful. Lower-middle has 9 economies. State that fairness claims are anecdotal.
- **Reported paired gains disagree with table differences.** Table means: A10 peer 15.01 - stack 13.77 = **1.24**, but the text says 1.33. A16 hybrid vs peer: 11.34 - 10.77 = **0.57**, but `\ResColdGain` = 0.35. A16 stack vs peer: 11.34 - 10.53 = **0.81**, text says 0.78. In the temporal case 3.62 - 3.48 = 0.14 matches. Explain (cluster-weighted? seed-averaged?) or fix. A reviewer will compute these in 30 seconds.
- **Multiplicity.** Holm is applied only to cold-start comparisons (`sec_results.tex:50`). The headline temporal 0.14 pp result is outside the family. Abstract still says "significantly better ... (1.33 pp, CI 0.72-1.94)" for A10 while the A16 stack result (p = 0.060) fails. Report it in the abstract as a single conditional finding, not a general one.
- **Practical vs statistical significance.** 1.33 pp is 9% of A10 peer error of 15 pp. "Makes the peer-learning mode demonstrably useful" (`sec_results.tex:34`) is too strong when 14% of the budget is still mismatched, and error is 33 pp for low-income economies, which are the ones that lack COFOG data and so are the real use case.
- Test sample: 178 country-years, 36 clusters, 5 serially correlated years each.

### 2.5 Novelty vs related work (Nonato 2026, Kisman 2026, Mohith 2026)
- The novelty statement (`sec_related.tex:18`) is the **conjunction** of four attributes (multi-country + functional + persistence baseline + engine + XAI evaluation). Each is individually done: Nonato (functional, XGBoost, leakage-free check dropping R² from 0.97 to -0.45, optimiser), Kisman (cross-country SHAP/PDP/ALE on defence), Mohith (ML vs DL, SHAP/LIME/permutation importance/prediction intervals, 2 held-out years). Intersection novelty of this kind is weak at Q1.
- **Table `tab_gap` is self-graded and tilted.** The columns "Persistence baseline" and "Alloc. constraints" are exactly the properties of the authors' own system; every competitor gets a dash and the authors get 7 ticks. Mohith is graded "n/a" (judged from abstract only) and the text then argues from the silence of the abstract ("no persistence or peer baseline is reported in the abstract", `sec_related.tex:16`). Read the full Mohith, Nonato and Kisman papers and grade from them, or drop the table.
- Mohith's result (simple models beat DL on short annual series) and Nonato's (leakage collapses R²) already say what this paper says. The claim to be "first" must be replaced by "we extend this to a multi-country official panel".
- **Over-claim:** "to the best of our knowledge no study ..." with a Google-Scholar-only search. State the evidence limits, or run Scopus/WoS before submission (the appendix itself says "repeat ... before submission").
- The **forensic audit** (contribution 5) is of the authors' own LLM-populated v1 dataset (Discussion 6.6 admits "partly populated with the help of an LLM"). It is an honest correction, but it is not a research contribution; reviewers will ask (a) was v1 published, and if so, where is the correction/retraction; (b) why should the community care. Move it to a short section or an appendix, and state the status of v1 explicitly.

---

## 3. Negative results: is the message publishable at Q1?

The paper's message ("persistence is hard to beat; gains are small; peer learning helps for health/R&D and more diverse economies; shocks are not anticipated") **is publishable**, but not in its current wrapper.

- At ESWA the expected contribution is a new or improved expert system. Here the "system" loses to the trivial baseline. Expect: "no methodological novelty; incremental benchmark". Desk-reject or reject.
- A negative-result paper works when the question is sharp, the benchmark is strong, and the evidence is sufficient to make the negative result **credible**. Here the negative result is credible in some places (many econometric baselines, institutional features, shock features), but is weakened by the fragile "small but real" positive claim and by weak cold-start baselines.
- The contribution that is hardest to dismiss is the **dataset plus protocol plus leakage audit**. Frame the paper as a **benchmark and "how much can ML add to persistence?" evaluation** (the title question), not as "an explainable constraint-aware framework". The honest, strong sentence is: *"Across 36-85 economies and five seeds, no learner reliably beats last year's allocation; peer information helps only when there is no history, and it helps unevenly."*

**Framing that maximises acceptance** (applied in section 6):
1. Title: "How much can machine learning add to last year's budget? A benchmark of functional government expenditure forecasting on official COFOG data, with an audit of a leaky precursor". Drop "Explainable and Constraint-Aware".
2. Venue: Data & Policy (the Nonato paper's venue), GIQ (open government data), SPS, or a data-centric venue. ESWA only if a methods angle is added (e.g., a compositional model with a proper conformal wrapper).
3. Lead with the dataset and protocol. Make the explanation evaluation a secondary, carefully worded finding. Demote the engine and stack to "tested and not adopted".
4. Reduce Results to about 6 key experiments; move the other 12 run-in items of section 5.9 to a supplement.

---

## 4. Claims vs evidence: every over-claim found

| # | Claim | Where | Evidence | Fix |
|---|---|---|---|---|
| 1 | "A learned correction lowers..." / "learned gain is small but real" | Highlights L37; abstract; `sec_intro.tex:13` | CI lower bound 0.025 pp; 53% of rows; 36 clusters; one window; CLR hybrid p=0.72 | "A learned correction yields a statistically fragile 0.14 pp (95% CI 0.03-0.28) improvement over persistence, not robust to model variant" |
| 2 | "SHAP is faithful" | Highlights L38; abstract; conclusion | mean-replacement ratio 2-3.8x only | "SHAP-selected features change predictions 2-4x more than random ones" |
| 3 | "Stacked learner makes cold-start significantly better" | Abstract; intro; conf abstract | A10 only; A16 Holm p = 0.060; ties kNN and Dirichlet | "A stack, a Dirichlet regression and a k-NN predictor each beat the peer mean on A10 by 1.2-1.3 pp; only the A10 comparison survives Holm" |
| 4 | "Constraint-aware" (title) / "keeps recommendations legal" (Highlights L39) | Title; highlights | No statutory constraints; bounds from quantiles; tight bounds raise TVD | Remove from title; "enforces the budget identity and optional user bounds" |
| 5 | "Learners explain health and R&D in unseen economies" | Abstract | Panel B uses Gov. expense, tax and debt as features; ridge gets 0.50/0.53; baseline is a 4-class mean | Re-run without target-bounding features; add GDPpc-regression baseline |
| 6 | "Under temporal, leave-country-out and leave-region-out protocols" | Abstract | LRO only on WDI panel | State "on the WDI panel" |
| 7 | "Open ... benchmark" / "ready" | Highlights L35 | Zenodo DOI is `XXXXXXX` placeholder; repo "to be made public" | Publish before submission |
| 8 | "No study ... combines" | `sec_related.tex:18`; conf intro | Self-graded table; abstract-only reading; Google Scholar only | Read full texts; soften |
| 9 | Applicability score "tracks error" (rho 0.70) | `sec_results.tex:36` | Confounded by group sample size (3 economies in LI); computed on the same panel | Report by income-group-controlled partial correlation |
| 10 | "Peer-based learning clearly helps for health and R&D" | Conclusion L1 | See #5 | Qualify |
| 11 | Website: "Likely range (8 in 10 cases)", "Confidence: High" | `Home.jsx` | Under-coverage 47-61% for LI/LM | Show coverage by group, or hide intervals for non-high-income |
| 12 | Website: "best model (blend of four learners)" | `Home.jsx`, `Guide.jsx` | Paper: k-NN/Dirichlet tie; stack worse than persistence for annual | Align |
| 13 | "Every number in this paper is regenerated from raw downloads (pipeline/01-06)" | `sec_discussion.tex:14` | Elsewhere "01-25"; hand-typed numbers exist (1.33 pp, 0.63, 0.60, 723 overlap, 4.16 vs 3.89, ...) | Make all numbers macros, or soften the sentence |
| 14 | "Human-in-the-loop support", "supports analysts" | Fig. 1, throughout | No user study; protocol only | Say "intended to" (already partly done); remove "decision-support" from Fig. 1 title |
| 15 | "Fairness analysis not performed" | `sec_discussion.tex:11` | A fairness audit **is** reported (`sec_results.tex:46`) | Reconcile |
| 16 | Conference: "no human-subject study or fairness audit yet" while Results has a "fairness audit shows..." | `main_conference.tex:48 vs 55` | Self-contradiction | Reconcile |

---

## 5. Internal inconsistencies and errors

**Numbers and text**
1. Paired-gain mismatches as in 2.4 (1.33 vs 1.24; 0.35 vs 0.57 vs 0.51; 0.78 vs 0.81).
2. Stack TVD on A16: text "3.51 pp" (`sec_results.tex:32`) vs `tab_E_hist` 3.50; "gains 0.11 pp" vs 3.62 - 3.50 = 0.12.
3. Fig. 10 shows Health r = 0.41, Social protection r = 0.31, Education r = 0.51; text says health r about 0.27 and social protection r about 0.34 for the same 2020-21 window (`sec_results.tex:13`; also `main_conference.tex:42`).
4. Fig. 1: "218 economies" vs 217 everywhere else; "Leave-country-out (6-fold x 3 seeds)" vs 2 seeds in text; "floors/ceilings = 0.5 x min .. 1.5 x max" vs "bounds set from historical quantiles" in `sec_method.tex:19`; "SDR 2026 SDG index (context)" is not mentioned in the Data section; "USD split" output not in the paper; Fig. 1 title includes "assists, never replaces" (taglines in a figure title).
5. `results_macros.tex`: `\NMasterCols = 217` and `\NMasterCountries = 217`. Possibly a macro bug (columns equal to countries); check.
6. Data section says "775 rows, 31 economies, 59 columns" for v1 and "plus 25 legacy-only rows for Taiwan" (31 x 25 = 775 ok); the master count 217 x 25 + 25 = 5,450 is OK.
7. The text says "pipeline/01-06" (discussion) vs "01-25" (code availability).
8. "Panel A" (16 functions) vs "A16" vs "A10": the A16 label first appears undefined in `sec_results.tex:32`. Define "A16" in `sec_data.tex`.
9. Fig. 9(b) y-axis starts at 3.0, which magnifies a 0.2 pp difference into a large visual gap; start at 0 or annotate the CI.
10. Conclusion lists "Conformal prediction intervals per function" as future work; Results already reports split-conformal intervals (`sec_results.tex:47`).
11. Abstract: "SHAP passes ... (3.1 x random)" while the range 2.0-3.8 is for 6 of 17 functions only (80 rows each).

**Tables**
1. `tab_A2_conf.tex:2`: `$	imes$` contains a literal TAB, so the caption renders "6 FOLDS imes 2 SEEDS" (confirmed in the compiled PDF page 3). Replace with `$\times$`.
2. `tab_bounds.tex`: "min-ma$\times$ (train)" and "1.5$\times$ma$\times$" should read "min-max" and "1.5 x max".
3. Tables use code identifiers: `delta_clr_xgb_hist`, `STACK v2.1 (NNLS on validation)`, `hybrid_clr`, `Delta-ML: lgbm`. Rename to descriptive labels.
4. Legacy audit table labels sector 8 "social welfare freebies"; replace with a neutral label or quote with a note.
5. MAE column is a constant multiple of TVD (see 1.2).
6. Conference `tab_income.tex` is `\small` plus `resizebox`; in a single column it renders at a very small font (PDF page 5, Table VI). Use `\footnotesize` without resizebox and drop two columns.

**Language and style**
- "This paper reports what we did about it." (`sec_intro.tex:3`); "honest profile" (intro L13, conclusion); "a more reliable contribution than a higher score" (conclusion): defensive, informal. Remove "honest".
- Mixed British/American ("scrutinise", "artefact", "optimisation" vs "behavior"); pick one (Elsevier accepts either, but be consistent).
- Section 5.9 uses 13 bold run-in headers in one block; split into subsections or move to a supplement.
- Method section lacks descriptions of: k-NN predictor, conformal method, Dirichlet regression, MLP/transformer, KernelSHAP setup, Optuna, shock-aware features, applicability score. These appear only in Results. A reader cannot reproduce them from the paper.

---

## 6. Structure vs a typical Q1 paper

| Element | Present? | Comment |
|---|---|---|
| Abstract | Yes, **about 330 words** | Over the 250-word limit common to Elsevier journals. Cut to 200-250; move the 2/3 of numbers out. |
| Highlights | Yes (5) | OK in length. Content: see over-claims #1, #2, #4, #7. |
| Introduction | Yes, but 3 findings paragraphs repeat the abstract | Shorten; add a concrete use case and "who benefits". |
| Related work | Yes, 7 subsections | Long; reads as a list. Merge into 3 themes. |
| Methods | Partly | Missing items listed above; no pseudo-code, no notation table. |
| Results | Dense | 13-item "extensions" block; no summary table of "what worked / what didn't". Add one. |
| Discussion | Yes | Contains items that are not discussion ("Which economies to include", "Reproducibility", "AI declaration", "Open items"). |
| Limitations | Yes (threats to validity) | Good, but add imputation leakage, contemporaneous covariates, single test window. |
| Conclusion | Yes | Defensive tone. |
| Data / code availability | Yes | **Placeholders**: Zenodo DOI `XXXXXXX`, "[repository to be made public at submission]", "[DOI to be inserted]". Do not submit with these. |
| CRediT | Yes | See 8. |
| Ethics | Yes | Good. |
| AI-use declaration | In Discussion 6.6 only, with "[Authors to confirm before submission.]" | Elsevier requires a separate unnumbered statement before the references with a prescribed heading; resolve the placeholder. State precisely what the LLM did, including that v1 data were LLM-populated. |
| Competing interest / Funding | Yes | OK. |
| Journal macro | `\journal{Expert Systems with Applications (target; adapt as required)}` prints in the footer ("Preprint submitted to ... (target; adapt as required)") | Remove before submission. |
| References | `elsarticle-num`; 57 entries in `references.bib`; `references_publicfinance.bib` (12 entries) is **not** loaded by `\bibliography{references}` | Check that the public-finance citations (`jones2005`, `barnes2023`, `lamartina2011`, ...) are in `references.bib` (they compile now, so they appear merged; delete the unused file or note). Numeric style suits ESWA; **GIQ and SPS expect their own styles (GIQ: APA author-year)**; switch per target. |
| Bibliography glitch | `main.bbl:172` "Missing character: U+2019" (curly apostrophe in a title) | Replace with ASCII `'` or `\textquoteright`. |
| Literature protocol | Appendix A: "web search ... Google Scholar" | Not a systematic protocol. Run Scopus/WoS/IEEE Xplore as the appendix itself says; list the number of hits and exclusions. |

### Layout (journal PDF, 46 pages, 12pt preprint)
- Pages 20-27 are a float dump: tables at the top of the page with blank lower halves, one or two figures per page with about 50% white space (Figs. 2-10 at pages 23-27). Pages 28-31 start the Discussion after about 8 pages of floats.
- The related-work Table 1 (`tab_gap`) is squeezed into a single-column `table*` + `resizebox` and shrinks to a tiny font (page 7 of the PDF, about 5 pt). Make it a landscape or full-width table with larger text or cut columns.
- Page 31: Appendix A takes a quarter page and the rest is blank before the supplementary tables (FloatBarrier effect).
- Figure legibility: Fig. 7 (heatmap) is fine at full width; Fig. 8 (three panels in one) and Fig. 9 are readable only at full text width; Fig. 3/4 have small tick labels; Fig. 1 contains a long title text; avoid duplicated captions-in-figure. Colour scheme (orange/blue) is colour-blind safe: good. Add error bars/CI to Fig. 5.
- Fix: put floats near the text with `[htbp]`, group small tables in one page, and use `\clearpage` only before the appendix.

---

## 7. Conference paper (IEEE, 6-page limit)

**Format fit.** The compiled PDF is 5 pages, i.e. one page under the typical 6-page limit; the source comment says "Target length 7-8 pages". Decide the target venue's limit first.
- Page 2 ends with the conclusion; the **references start mid-page 2 and continue on pages 3-5, interleaved** with tables and figures that were `\input` after the Conclusion (`main_conference.tex:60-66`). Page 3 has Table I (full width), Fig. 1 and two small tables; page 4 has Figs. 2-4 plus references; page 5 is half empty with Table IV/V/VI and references. All figures and tables live at the end with no in-text proximity. Place floats inside their sections, or use `[!t]` after the first reference.
- Table VI (income) renders in a tiny font in the left column. The related-work Table I has a ragged "Guerrero & Castañeda" cell.
- There is room for about 0.8 page: add (a) a half-column description of the stack and kNN (otherwise results refer to concepts not defined in a paper section), (b) the A10 cold-start table (`tab_E_cold`) that supports the key positive claim, (c) a conformal-coverage line.
- **Content:** the conference version is a compressed copy of the journal Results. It claims (`main_conference.tex:48`) stack/Dirichlet/kNN/conformal/fairness results but never defines the methods and has no table for them; it says "no ... fairness audit yet" in the next section.
- The abstract reads well; about 190 words. Replace the first sentence ("We present ... leaves the decision to a human analyst") with the research question.
- Reference [23] etc. use `IEEEtran`: fine. Two web refs list "accessed 14 November 2026" correctly.
- The conference text duplicates the journal; check that the venue allows an extended journal follow-up (self-plagiarism policy) and cite the conference paper in the journal version, or vice versa.

---

## 8. Authorship and CRediT plausibility
- All four authors use same-pattern institutional addresses (`name.NN@pccoepune.org`, suffix 24), consistent with students of the same cohort. The corresponding author and "Supervision and project administration: A.H.J." carries the same pattern. If A.H.J. is faculty, say so in the affiliation; if all four are students, a reviewer may ask who supervised, and the "Supervision" role looks inconsistent.
- The repository history (single committer "Pranav Chaudhari") and the "Principal responsibility" paragraph place nearly all analysis with P.S.C. The CRediT lists G.M.J. for "Validation", "Formal analysis", "Investigation", "Resources" and "Data curation"; D.P.B. for Methodology and Software. Each author should be able to defend their listed contributions. Resources for a public-data study ("G.M.J.") is a stretch; "Funding acquisition" is correctly absent.
- "Writing - review & editing: A.H.J., D.P.B., all authors" is redundant (all authors includes them).
- The extra "Principal responsibility" paragraph is non-standard; keep CRediT to the standard 14 roles, and put the narrative in the cover letter.
- Elsevier: remove "Additional information" if not required; ensure each author's ORCID if the journal asks.
- The AI-use declaration (Discussion 6.6) and the unspoken fact that the paper, code, and dataset were produced in significant part with an AI coding assistant should be consistent with what the authors can defend in a revision round.

---

## 9. Website usability for a first-time user (`Home.jsx`, `Guide.jsx`)

Strengths: one input, automatic settings, plain-language "why" text, glossary, "Advice only; human approval required" notice, an explicit "Important limits" box.

Issues:
1. **Default country is India (IND)**, a country with no official 16-function history. First click yields the least-supported case (cofog10, IMF-sourced). Default to a high-income economy with history, or to nothing, and show a sample.
2. **Cold-start delay**: "The first request can take about a minute while the models warm up" (hosted API). Show a progress message and keep the page usable; a first-time user will assume it is broken. (The `Status` banner handles it; check that it shows an explicit timer.)
3. **Normative language**: "AI suggestion", "Biggest increase / Biggest decrease", "Green = consider increasing". For a descriptive peer benchmark use "Peer-typical share", "Differs from last year by". Avoid "Budget to move" as a headline stat.
4. **Calibration claims**: "Confidence: High" is a novelty bucket; "Likely range (8 in 10 cases)" is not valid for low/lower-middle income countries (47%/61% coverage). Add a visible line: "intervals are reliable for high-income economies only".
5. **Annual-update contradiction**: for countries with history the app compares the cold-start model with last year, while the paper shows persistence is better. Show "last year's actual" as the primary forecast and the model as a peer reference.
6. **Explanation target**: the SHAP bars explain one tree member, not the displayed blend (Section 2.3). The UI phrase "Each bar is one fact about the country" overstates causality; add "association, not cause" in the visible caption (currently only in the Guide).
7. **A 16-slice donut** with a long legend is hard to read; use a sorted bar only. Pie colours repeat (PALETTE cycled for 16 items).
8. Add a one-line "What is this? Who is it for?" at the top. The Guide is the only place a user learns what a COFOG area is; link glossary terms inline.
9. Accessibility: colour-only green/red cues (arrows are present: good); dark theme text is `text-slate-400` on navy, with contrast near 4.5:1 or lower at 11 px captions; check WCAG.
10. State the data year and the "executed, not planned" caveat on the results page itself, not only in the Guide.

---

## 10. MAJOR issues (numbered, with location and concrete fix)

**M1. The central positive result is fragile and over-sold.** Locations: abstract; Highlights L37; `sec_results.tex:11`; `sec_intro.tex:13`.
Fix: report "0.14 pp (95% CI 0.03-0.28), hybrid better on 53% of rows, not robust to CLR variant (p = 0.72)". Add a rolling-origin evaluation (origins 2012-2023) for the headline; include the temporal comparison in the Holm family; pre-declare the hybrid or report the best-of-five penalty. Change the highlight to "Last year's allocation is hard to beat; learned gains are small and fragile".

**M2. Novelty claim is a self-defined conjunction, with a self-graded table.** Locations: `sec_related.tex:16-18`; `tab_gap.tex` and `tab_gap_conf.tex`; `main_conference.tex:28`.
Fix: read Mohith/Nonato/Kisman in full; delete the dash/tick grid or grade only objective attributes (countries, years, target classification, baselines reported, XAI test). Replace "no study combines" with "we extend X, Y, Z to an official multi-country panel and add W". Run the Scopus/WoS/IEEE Xplore search and report counts.

**M3. Real-world use case and the timing of covariates are not defined.** Locations: `sec_intro.tex:1-4`; `sec_method.tex:2-3`.
Fix: add a "Use cases" paragraph (gap-filling for statistical agencies, peer benchmarking, teaching). State the information set available at forecast time (publication lags; x_t is realised). Rerun the annual model using x_{t-1} or forecasted covariates for a strict forecasting setting, or relabel as "nowcast".

**M4. Imputation and near-leakage in features, in a paper about leakage.** Locations: `sec_data.tex:17`; `tab_features` (43-69% imputed for fiscal variables); Panel B features vs targets.
Fix: impute within training folds only (no future-looking interpolation for temporal tests); add an ablation on rows with imputed fraction <= 10%; re-run Panel B without gov. expense, tax revenue and debt; report the changes in R² for health/R&D.

**M5. Baselines are weak for the cold-start claim.** Locations: `sec_results.tex:16, 19`; Table A2/B.
Fix: add region x income mean, a log-GDPpc (and GDPpc-bin) regression, and kNN-on-GDPpc baselines; tune ridge properly (it loses to the mean, which is a red flag). Report whether the ML gain survives these.

**M6. Architecture is over-engineered relative to evidence; title and website feature the wrong things.** Locations: title; abstract; `sec_method.tex:27-28`; `Home.jsx`.
Fix: demote the stack and engine; promote the k-NN/Dirichlet alternatives (simpler, explainable, equally good). Make the stack's gain over kNN/Dirichlet an explicit test. Remove "Constraint-Aware" from the title; describe the projection as a utility (cite Held 1974 / Duchi 2008), remove it from the contribution list or reword to "an open implementation".

**M7. Statistical inference with very few clusters, and paired-gain numbers that do not match the tables.** Locations: `sec_results.tex:34, 36, 46`; `tab_income.tex`; macros `ResColdGain*`.
Fix: reconcile 1.33/1.24, 0.35/0.57/0.51, 0.78/0.81 in a footnote explaining the paired estimator; report no CI for the 3-economy low-income group (show raw country-level errors instead); treat the fairness section as exploratory; use wild/block bootstrap or a mixed model for sensitivity.

**M8. XAI evaluation is over-interpreted and explains a different model from the one deployed.** Locations: abstract; `sec_results.tex:26, 51`; Highlights L38; `Home.jsx` SHAP panel.
Fix: add permutation importance and gain importance comparisons, a random-attribution null for sign agreement, and an on-manifold (conditional) deletion test. Move the synthetic ground-truth result (precision@3 = 0.67) into the abstract. Either explain the blend or deploy the kNN and its neighbours as the explanation.

**M9. Placeholders, stale build and incomplete submission package.** Locations: `main_journal.tex:17` (journal macro), L83, L126, L129; `sec_discussion.tex:17`.
Fix: publish the repo and Zenodo DOI; remove "(target; adapt as required)"; resolve "[Authors to confirm]"; recompile the PDFs from the current sources; do not submit with "XXXXXXX".

**M10. Structure: the paper is a lab notebook.** Locations: `sec_results.tex:41-53`; Methods.
Fix: write the Methods for every module reported, or move modules to a supplement; keep 5-6 headline experiments in the main text with a one-table "what worked / what didn't" summary; cut the abstract to 250 words; move non-discussion items out of Section 6.

**M11. Target definition and metric issues.** Locations: `sec_data.tex:12`; `sec_method.tex:2`; `tab_A1/A2`.
Fix: document the mapping to COFOG divisions/groups, the content of the residual and its mean share; clarify whether water is inside housing; drop the MAE columns (redundant with TVD); add a share-weighted and a per-function relative error; put "executed" in the title/abstract.

**M12. The v1 audit is about the authors' own LLM-populated dataset.** Locations: contribution 5; `sec_results.tex:1-9`; `sec_discussion.tex:17`.
Fix: state whether v1 was published; if so cite it and the correction; shorten the audit to one page / appendix; do not present it as a main contribution; disclose how the LLM was used for v1.

**M13. Website over-claims reliability and nudges normative use.** Locations: `Home.jsx` (Confidence card, "Likely range", "Biggest increase/decrease", green/red), `Guide.jsx` ("best model").
Fix: see section 9 items 3-6.

---

## 11. MINOR issues

1. `tab_A2_conf.tex:2`: `$	imes$` (literal TAB) -> `$\times$`.
2. `tab_bounds.tex`: "min-ma$\times$" -> "min-max"; "1.5$\times$ma$\times$" -> "1.5 x max".
3. Replace code identifiers in `tab_E_cold`, `tab_E_hist` with readable names.
4. "social welfare freebies" in `tab_audit.tex` (row 8) -> neutral wording with a note.
5. Fig. 1: "218 economies", "3 seeds", "0.5 x min .. 1.5 x max", "SDR 2026", and the title tagline; align with the text.
6. Fig. 9(b): y-axis starts at 3.0; start at 0 or show CIs.
7. Fig. 10 vs text correlations (0.41/0.31 vs 0.27/0.34).
8. `main.bbl:172`: curly apostrophe missing in the font; fix in the bib entry.
9. Define A16 at first use (`sec_data.tex`); Panel "A" vs "A16" naming.
10. Abstract 330 words, with hard-coded numbers (1.33, CI 0.72-1.94, 85 economies, 0.63/0.60/0.31/0.25) next to macros; make all macros so numbers cannot drift.
11. `sec_discussion.tex:14` "pipeline/01-06" vs `main_journal.tex:129` "01-25".
12. `sec_results.tex:32` "3.51" vs `tab_E_hist` "3.50"; "0.11" vs 0.12.
13. Journal Appendix A states the search was run "on 14 November 2026" and "repeat on Scopus ... before submission": do it and rewrite in past tense.
14. "Writing - review & editing: A.H.J., D.P.B., all authors" -> "all authors".
15. Remove the "Principal responsibility" paragraph from CRediT or move to the cover letter.
16. Tone: remove "honest", "This paper reports what we did about it", "more reliable contribution than a higher score".
17. Conference: tab_income font; ragged cell in Table I; floats all at the end; the bibliography starts on page 2 and is interleaved with floats; 5 of 6 pages used.
18. Conference Table I caption (stale in the PDF) must be rebuilt after the source update.
19. Related-work paragraphs are long single blocks (`sec_related.tex:2, 16`); break them up and cut by one third.
20. Journal `elsarticle` `preprint,12pt` gives 46 pages; use `review` (double-spaced) only if the journal asks; for final, use the journal's own class (`1p`/`3p`).
21. Reference style: numeric vs APA depending on journal (GIQ: APA).
22. `references_publicfinance.bib` is not referenced by `\bibliography`; merge or delete.
23. Figure captions should state sample sizes (n) and number of seeds in each panel.
24. Add a notation table (K, y, x, h, f, g, a*, l, u, lambda).
25. Define "applicability score" in Methods (it appears only in Results).
26. Table gap: caption refers to the "full texts or abstracts" but the 'n/a' cell says abstract only; make consistent.
27. Clarify TVD for A10 (K=10) vs A16 (K=17): "pp of total expenditure" is not comparable across panels.
28. State the random seeds and the software versions in a table, not a paragraph.
29. "Python 3.13 ... NumPy 2.2 ... SHAP 0.52" check against `requirements.txt`; confirm versions exist as stated.
30. Data availability: give licence terms (WB CC-BY 4.0, OECD/Eurostat/IMF terms) for redistributing derived panels, and a data-sheet link.

---

## 12. Before-submission checklist

**Science**
- [ ] Rolling-origin evaluation for the headline; include the headline in the Holm family; pre-declared learner.
- [ ] Reconcile every paired gain with table differences (M7); explain the estimator.
- [ ] Rerun with fold-internal imputation; Panel B without target-bounding features.
- [ ] Add region x income mean, GDPpc regression, tuned ridge as cold-start baselines.
- [ ] Strict-forecast variant (lagged covariates) or relabel as nowcast.
- [ ] Stack vs k-NN vs Dirichlet head-to-head test; decide the "deployed" model.
- [ ] XAI: null baselines, permutation importance, explanation of the deployed model.
- [ ] Treat low-income conclusions as exploratory (3 economies).

**Writing**
- [ ] New title (benchmark framing); drop "Constraint-Aware".
- [ ] Abstract <= 250 words; Highlights re-worded (#1, #2, #4, #7).
- [ ] Use-case paragraph; define "executed", A16/A10, the residual and COFOG mapping.
- [ ] Methods describe every reported module; extensions moved to a supplement; a one-table summary of what worked/failed.
- [ ] Self-graded novelty table removed or made objective; Mohith/Nonato/Kisman read in full.
- [ ] Tone edits (item 16); consistent spelling.

**Compliance**
- [ ] Zenodo DOI and public repo; remove all `XXXXXXX` and bracketed placeholders.
- [ ] Separate Elsevier AI-use statement with the exact use; v1 status declared.
- [ ] CRediT: standard roles only; each author can defend theirs; affiliation/role of A.H.J. clarified.
- [ ] Remove "(target; adapt as required)"; switch to the target journal's class and reference style.
- [ ] Systematic search (Scopus/WoS/IEEE Xplore) logged.
- [ ] Data licences stated.

**Layout and artefacts**
- [ ] Recompile both PDFs from the current sources; check no stale captions.
- [ ] Fix TAB-`imes`, "min-ma$\times$" and code-identifier tables; remove redundant MAE columns.
- [ ] Float placement: no half-blank pages (journal pp. 20-27, 31); Table 1 legible; conference floats inside sections, income table legible, page count to the venue limit.
- [ ] Redraw Fig. 1 (economies, seeds, bounds, title), Fig. 9b axis, Fig. 10 numbers vs text.

**Website**
- [ ] Default to a country with history; show a sample result.
- [ ] Replace "suggestion/increase/decrease" language with peer-benchmark language.
- [ ] Hide or caveat intervals/confidence for non-high-income countries.
- [ ] For countries with history, present last year's value as primary; model as reference.
- [ ] Add "association, not cause" and "executed spending, not budget" notes on the results page.

---

## 13. Probability summary
- **Journal, as is, ESWA:** P(accept) about 8-10%; P(desk reject) about 35%; most likely outcome reject-with-resubmission-encouraged.
- **Journal, reframed and fixed (M1-M12), at SPS/GIQ/Data & Policy:** P(accept after revisions) about 25-35%.
- **Conference, as is:** about 55-65% at a generic IEEE-sponsored conference; with the fixes in section 7, about 70%.
