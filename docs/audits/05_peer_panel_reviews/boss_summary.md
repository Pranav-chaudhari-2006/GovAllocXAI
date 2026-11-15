# Boss/editor summary of the three-reviewer review (15 Nov 2026)

Nothing was committed or pushed. All numbers below come from `results/` (new files: `results/19_annual_seed_robustness/*`, produced by `pipeline/25_annual_seed_robustness.py`, about 2.5 min CPU) or from existing result files. Both papers were compiled with Tectonic on a copy of the rebuilt zips: journal 55 pages (12 pt preprint), conference 6 pages; no undefined citations or references; largest overfull box 11 pt (journal); conference has none. Compile count: conference 2; journal 3 (the first aborted after 1 s on a float-option error), i.e. one over the budget.

Cross-checks I did myself (reviewers were right on all that I tested): paired-gain arithmetic (5-seed values in `15_robustness_holm/holm.csv`); annual-gain seed fragility (rerun: gains 0.140, 0.107, 0.112, 0.116, 0.104, only seed 42 has CI above 0, same as review A); the TAB bug in `tab_A2_conf.tex` (source was `"$\times$"` in a non-raw Python string in `06b`); Fig. 10 numbers (pooled 2020-21 r = 0.41/0.31/0.51 vs 2020-only 0.27/0.34; both are now stated); LRO health R2 = 0.4949 (so 0.49 is right and the text said 0.50); housing/water mapping (code: housing = GF06 minus GF0603, so no double counting; residual = 04.1 + 04.9, not 04.7 as review C guessed). One reviewer claim I corrected: review C said the residual absorbs 04.7; in the code 04.7 is inside "industry and construction".

## (a) Findings and dispositions

### Review A (results integrity)
| Finding | Disposition |
|---|---|
| No fabrication; 62 numbers traced | Accepted; no change needed |
| H1 paired cold-start gains = fold-seed 0, adjacent TVDs = 2-seed means | APPLIED. Text/abstract use five-seed Holm-table values (A10 stack 1.26 [0.68, 1.84], A16 0.81 [0.20, 1.34]); the hybrid's fold-seed-0 gain 0.35 is labelled as such next to the 2-seed difference 0.57; new `tab_holm.tex`; Table E_cold caption explains 1.24 vs 1.26 |
| M1 annual 0.140 significance not robust | APPLIED (verified by rerun, new `expU`). Abstract/intro/results/conclusion/website: 0.140 for seed 42, mean 0.12 over 5 seeds, CI excludes 0 in 1 of 5, XGB-only 0.04, not in the Holm family. Adding the raw-delta hybrid to the Holm family was NOT done (would need the 10,000-draw study rerun) |
| M3 total budget "36 economies" | APPLIED in paper (30 economies, 716 rows) and `backend/service.py`; near-proxy feature disclosed with review A's audit numbers (flagged in the text as an internal check, not in the pipeline); "income-group mean = global mean" stated in the caption |
| M4 3.51 vs 3.50 | APPLIED (macro `\HistStackSixteen`); gain 0.11 noted as computed on unrounded values |
| M5 "persistence best at every horizon" | APPLIED ("best deployable"; oracle h=1 TVD 2.80 vs 2.92, CI -0.13..0.45, verified in `09_multi_year_projection/summary.json`) |
| M6 sign wording of institutional results | APPLIED (gain defined as baseline minus extended TVD; negative means worse; annual gains -0.016..-0.006) |
| M7 "significant 0.96 pp" XGB on A10 | APPLIED (now 0.89 [0.19, 1.58], Holm p = 0.06, stated as not surviving) |
| M8 API in-sample fits | PARTLY: disclosed in paper, Home.jsx banner and Guide; no leave-economy-out refit or "in training data" flag in the API itself |
| L1 "all 775 rows share one mix" | APPLIED (eleven synthetic sectors only; `04b` now rounds at 1e-9, JSON regenerated: 22 -> 1) |
| L2 | no action needed |
| L3 stale "fairness not performed" | APPLIED (Discussion and conference) |
| L4 stale "four WDI series only" | APPLIED (rewritten) |
| L5 "211 economies" for health and R&D | APPLIED (the intro sentence was rewritten; panel B 211 is stated as panel size only) |
| L6 tab_selection caption | APPLIED (generator caption now mentions the history-regime improvement 2.27 vs 2.33, still worse than persistence 2.26) |
| L7 ddof mismatch | PARTLY (ablation caption now says population SD, not comparable with Table A2; values unchanged) |
| L8 LRO 0.495 and "negative R2 in some regions" | APPLIED (0.49; "negative pooled R2 under leave-region-out") |
| L9 several XGB numbers | APPLIED as a note (13.96 / 14.12 / 14.11 explained) |
| L10 imputation and static income group | APPLIED as limitation paragraph (not re-run) |
| L11 CatBoost shock variant | APPLIED (4.01 vs 4.07, worse than own baseline 3.73) |
| L12 synthetic test ceiling | APPLIED |
| L13 results.js hand-typed | PARTLY (comments added, annual gain and cold-start notes; no generator written) |
| L14 external literature numbers | PARTLY (Nonato figures weakened to what the abstract supports) |
| L15 NMasterCountries -1 | APPLIED (comment in `06b`) |
| Methodology: contemporaneous covariates | APPLIED (nowcast paragraph in intro, Methods, Discussion, Home.jsx) |
| Methodology: k=8 selected from a grid | APPLIED (disclosed; not added to Holm family) |
| Stale docstring "3 fold-seeds" | APPLIED |

### Review B (literature and references)
| Finding | Disposition |
|---|---|
| Radulescu four -> five CEE economies (4 places) | APPLIED (related, tab_gap, tab_gap_conf, conference) |
| Nzazi claim | APPLIED (narrative review; conceptual or pilot-scale; bib entry now `@inproceedings`, Procedia CS vol. 272, EUSPN 2025 as stated by review B) |
| Valle-Cruz, Yao, Guerrero, Santschi, Kisman, Nonato, Dragulin wording | APPLIED (Valle-Cruz explores allocation but does not predict an observed split; Yao = patient-level cost; Guerrero = causal framework; Santschi = short preliminary paper; Kisman = XAI methods, PDP/ALE dropped; Dragulin = LSTM/TCN vs SARIMA/VAR/ECM; Nonato "-0.45" and "no explanation method" weakened to abstract-level) |
| Mohith known only from abstract | APPLIED (dagger in table; "two held-out years" and "lagged covariates" removed as unverified) |
| Aitchison vs TVD | APPLIED (Aitchison cited for closure/compositional framework; TVD justified separately; no Aitchison-distance result reported, stated as limitation) |
| Grinsztajn "small data" | APPLIED ("medium-sized"; our panels are smaller) |
| Bib: Dragulin surname, Krishna authors, Rogoff-Sibert RES 1988 (10.2307/2297526), Chand issue 1, Nzazi type, UN COFOG URL, Santschi note, access dates, jones2005 year, lamartina apostrophe | APPLIED. Krishna: six authors, preprint, arXiv URL (Research Square DOI dropped); `rogoff1988` pages 1-16 taken from review B (Crossref gives only first page 1); Alvarez-Melis marked preprint |
| Four uncited entries | APPLIED (dropped blanchard2002, wildavsky1969; cited hyndman2006 in metrics and un2015agenda in SDG paragraph) |
| Missing literature: compositional, conformal, tabular DL, XAI evaluation, fairness, ML-in-economics, public finance, methods | APPLIED with 27 new entries, all DOIs/arXiv IDs re-verified on 15 Nov 2026 via Crossref/arXiv API in this session. Not added: Easterly-Rebelo and Makridakis (M4), which I could not tie to a sentence in the papers; Holm 1979 (no verified DOI, so the procedure is named without a citation). Journal cites all added entries; the conference cites four (davis1966, kumar2020, cameron2008, wolpert1992) |
| Placeholders (Zenodo, "to be made public", "DOI on acceptance", "[Authors to confirm]") | APPLIED. One Zenodo placeholder remains, worded as "to be created at acceptance", in Data availability; repository wording fixed |
| "Authors verified all references" claim | APPLIED (removed; replaced by what was actually done) |
| `references_publicfinance.bib` unused | NOT touched (file left in place; not loaded; harmless) |
| Curly apostrophe in bib | APPLIED |

### Review C (peer panel)
| Finding | Disposition |
|---|---|
| Reframe (benchmark + honest negatives), new title, drop "Constraint-Aware", demote stack and engine | APPLIED (both papers, README, abstracts, highlights, conclusion, website) |
| M1 central positive result fragile | APPLIED (wording). Rolling-origin evaluation of the headline and inclusion in the Holm family NOT done (new experiments); listed as future work |
| M2 novelty is a conjunction; self-graded table | APPLIED (table now lists objective attributes only; "we do not claim to be first"; Mohith/Nonato/Kisman described fairly). Scopus/WoS search NOT done (human) |
| M3 use case and covariate timing | APPLIED (use-case paragraph; nowcast statement). Strict lagged-covariate run NOT done |
| M4 imputation and Panel B near-leakage | PARTLY: disclosed as limitations in Data, Results, Discussion; no fold-internal imputation and no Panel B re-run without fiscal variables (not cheap) |
| M5 weak cold-start baselines | PARTLY: stated as a limitation; region-by-income mean, GDPpc regression and tuned ridge NOT run |
| M6 architecture over-engineered | APPLIED (stack/engine = evaluated components; kNN/Dirichlet promoted; the stack-vs-XGBoost test is in the Holm table; stack vs kNN/Dirichlet head-to-head NOT run) |
| M7 few clusters; gains vs tables | APPLIED (reconciled; low-income intervals declared not meaningful; fairness labelled exploratory). Wild bootstrap/mixed model NOT done |
| M8 XAI over-interpreted | PARTLY: wording corrected (weak evidence, off-manifold, synthetic result moved up, sign null noted); permutation/gain importance and null baselines NOT run; blend vs member disclosed in paper and website |
| M9 placeholders, stale build | APPLIED (journal macro, placeholders; zips rebuilt and compiled) |
| M10 lab-notebook structure | PARTLY: summary table added, section 4.8-4.10 split into three subsections, tables/figures placed near text; modules not moved to a supplement |
| M11 target definition and metrics | APPLIED (COFOG levels, residual mean 2.6 %, water/housing, "executed" in text, MAE dropped and explained as 2 TVD/K; share-weighted and relative errors NOT added) |
| M12 v1 audit | PARTLY: framed as a methodological lesson, v1 provenance disclosed; whether v1 was published is unknown to me (human item) |
| M13 website | APPLIED (see below) |
| Over-claims table #1-#16 | APPLIED except #5/#9 (re-run requests; wording qualified) and #14 (Fig. 1 retitled) |
| Minor: TAB/times bug, tab_bounds, code identifiers, "freebies", MAE columns, income table font, Fig. 1 text, Fig. 9b axis, Fig. 10, A16 definition, pipeline 01-25 -> 01-28, abstract length, notation table | APPLIED, except a notation table (not added). Abstract: 292 -> ~215 words (journal) |
| Minor: bbl apostrophe, uncited bib, Appendix A tense, search protocol, CRediT redundancy and "Principal responsibility" paragraph, "honest" tone, spelling | APPLIED (the principal-responsibility text was removed; move it to the cover letter); spelling not unified |
| Minor: journal class/reference style per target, `review` option | NOT done (venue-dependent) |
| Minor #28/#29 seeds/software table and version check | NOT done (no requirements file found to check against) |
| Layout: float dump, tiny Table 1, half-blank pages | APPLIED (floats placed in sections with `htbp`; Table 1 rebuilt as text columns; low-fill check finds no half-blank journal page other than the title page) |
| Conference: floats at end, tiny income table, 5 of 6 pages, undefined methods, tab_E_cold | APPLIED (floats inline, income table footnotesize without resize, methods defined, 6 pages); tab_E_cold NOT added (numbers given in text instead) |
| Authorship/CRediT plausibility | PARTLY: redundant role and extra paragraph removed; affiliation of A.H.J. and who did what is for the authors |
| Website items 1-10 | APPLIED: 3, 4, 5, 6, 10 and the 16-vs-10 explanation; REJECTED by owner decision: 1 (default India kept); NOT done: 2 (timer), 7 (donut), 8, 9 |

## (b) New headline numbers
- Persistence 3.62 pp [3.17, 4.08]; Delta-hybrid 3.48 pp [3.06, 3.91]; paired gain 0.140 [0.025, 0.277] for seed 42; five learner seeds: 0.104-0.140, mean 0.116, CI excludes 0 in 1 of 5; XGB-only mean 0.035 (0 of 5).
- Cold start A16 (5 fold seeds): stack 10.50 vs peer 11.31, gain 0.81 [0.20, 1.34], Holm p = 0.060; kNN8 0.66 [0.19, 1.14], p = 0.034; XGB 0.47 [-0.22, 1.13]. A10: stack 13.73 vs peer 14.99, gain 1.26 [0.68, 1.84], Holm p = 0.0008; kNN8 1.25 [0.71, 1.78], p = 0.0008; XGB 0.89 [0.19, 1.58], p = 0.060.
- A16 hybrid cold start: 2-seed 10.77 vs 11.34 (diff 0.57); fold-seed-0 gain 0.35 [-0.44, 1.10].
- A16 stack annual: 3.50 (gain 0.11 [0.03, 0.20]); A10: persistence 4.62, stack 4.82 (-0.20 [-0.35, -0.03]).
- Total-budget module: 30 economies, 716 country-years. Residual share: mean 2.6 %, median 1.8 %, max 29.7 %.
- Fig. 10 pooled r: health 0.41, social protection 0.31, education 0.51 (2020 only: 0.27, 0.34).

## (c) Items only the human can do
1. Create the Zenodo archive and insert its DOI (single placeholder, Data availability in `main_journal.tex`); push (fast-forward, see docs/17).
2. Run the Scopus / Web of Science / IEEE Xplore search; read Mohith, Nonato and Kisman in full and update the table (currently abstract-level, daggered).
3. Confirm CRediT roles, A.H.J.'s affiliation/role, and the generative-AI declaration text (it names Claude and states LLM involvement in v1; the authors must agree it is accurate). Decide whether v1 was published and cite/correct it.
4. Compile on Overleaf (elsarticle / IEEEtran) and re-check page counts; choose the target venue and swap class/reference style (GIQ uses APA).
5. Optional science that would raise acceptance odds: rolling-origin headline test; fold-internal imputation; Panel B without fiscal-envelope features; region-by-income and GDPpc baselines; permutation-importance and null baselines for XAI; stack vs kNN vs Dirichlet head-to-head; strict lagged-covariate forecast. Also the website: leave-economy-out refit or in-sample flag in the API, sorted-bar chart, timer.
