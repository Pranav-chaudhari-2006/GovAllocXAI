# Senior-Researcher Readiness Audit — Conference and Q1 Journal

*Reviewer stance: 10+ years in applied ML / public-sector analytics, acted as handling editor + 3 simulated referees. Written 15 Nov 2026 after all experiments. Brutal on purpose; every weakness lists the fix and the time it needs.*

## 1. Verdict

| Target | Verdict | One-line reason |
|---|---|---|
| **Conference (IEEE-style, applied AI / GovTech / data-science track)** | **READY after small fixes (≈ 3–4 h)** | Clear problem, real data, honest evaluation, 6 pages, compiles. Needs Overleaf layout check, author declarations, proof-reading. |
| **Q1 journal (e.g. ESWA, SEPS, GIQ, DSS)** | **NOT READY today — "major revision" risk (high) → achievable in ≈ 2–3 weeks** | Contribution is an evaluation/benchmark with small accuracy gains; no human evaluation; evidence concentrated in high-income economies; construct-validity gap ("budget" vs executed spending). |
| **Q1-adjacent fast venue (IEEE Access, Heliyon-class, Sustainability-class Q2)** | **READY after the same small fixes** | Scope is broad; rigor is above typical. |

Probability estimates (subjective): conference accept 55–70 %; ESWA/SEPS first-round outcome today: reject 45 % / major revision 45 % / minor 10 %; GIQ desk-reject risk 40 % (too technical, thin policy argument); IEEE Access accept-with-revision 65 %.

## 2. What is genuinely strong (keep, lead with it)
1. **Real, multi-source, cross-validated data** (Eurostat + OECD + IMF + WDI/WGI; 85 economies; flags; legacy preserved) — a citable dataset.
2. **Honest evaluation design:** temporal + leave-country + leave-region + by-income, cluster bootstrap, paired gains, practitioner baselines (persistence, peer mean) **and** econometric baselines (random walk with drift, AR(1)+FE — all worse than persistence).
3. **Negative results reported** (shock features, multi-year, tuning, low-income data) — rare and credible.
4. **XAI is measured, not decorated** (agreement, stability, faithfulness, sign flips) + applicability score, conformal intervals, kNN peers, fairness audit.
5. **Reproducibility:** one-command pipeline, auto-generated tables/macros, 9 tests, dataset card, change log.
6. **Self-audit (legacy leakage)** is an instructive lesson.

## 3. Weaknesses a Q1 referee will raise (ranked)

| # | Weakness | Severity | Fix | Time |
|---|---|---|---|---|
| W1 | **Contribution type.** Gains over strong baselines are small (annual update 0.14 pp; cold-start +1.3 pp on 85 economies). No new algorithm. A referee asks "so what?" | **Critical** for Q1 | Re-frame the paper as **benchmark + dataset + evaluation + decision-support framework** (not "better model"); lead with the dataset, the evaluation protocol, the audit and the explainability findings; state the practical value (peer prior for new countries; explanation) | 1 day writing |
| W2 | **Construct validity: "budget allocation" vs executed general-government expenditure.** Data are outturns by COFOG function, not budget proposals/appropriations. Title/abstract overstate. | **Critical** | Retitle e.g. "…Functional Government Expenditure Allocation…"; add an explicit paragraph and a limitation; where possible add one **budget-vs-outturn** sanity check (e.g. one country's approved budget vs outturn) | 0.5 day |
| W3 | **External validity: evidence is mostly high-income / OECD-EU** (A10: 50 high, 23 UMC, 9 LMC, 3 LIC). Low-income error 33 pp. | High | State clearly in abstract; collect national budgets for 3–5 low/lower-middle economies (World Bank BOOST: Kenya, Uganda, Haiti, Moldova, Niger… COFOG-compatible; licences vary) as a **pilot external validation** | 1–2 weeks |
| W4 | **No human-subject evidence** although the title says "decision support / assists the analyst". Claims about usefulness are untested. | High | Soften wording to "intended to support"; run the prepared study (ethics + ≈160 participants) or a small pilot (n≈20) as a formative study | 2+ weeks (pilot: 3 days) |
| W5 | **Model-selection / multiple comparisons.** Dozens of variants compared; stack chosen after seeing results; only one seed for several experiments. Referee suspects forking paths. | Medium-High | Pre-declare the final configuration in the paper; report all variants (done); repeat key experiments with 5 fold-seeds; add Holm correction for the headline comparisons | 1 day |
| W6 | **Baselines missing in the ML family:** no deep tabular (TabNet/FT-Transformer), no temporal transformer, no Dirichlet regression. | Medium | Add Dirichlet/ILR regression and one neural tabular baseline; if they do not beat GBDT, say so (citing Grinsztajn 2022) | 2–3 days |
| W7 | **Features are macro-only.** Political/institutional drivers of budget shifts (elections, fiscal rules, coalition, IMF programmes) are absent; explains weak shock results. | Medium | Add fiscal-rule, election-year and IMF-programme indicators (public datasets: IMF Fiscal Rules DB, DPI) as a feature-group ablation | 3–5 days |
| W8 | **Explanation validity.** SHAP/LIME explain an XGBoost member, not the stacked output; SHAP vs LIME flip signs in both case studies; no ground-truth check. | Medium | Explain the stack via KernelSHAP on the blend (or explain the kNN-peer predictor, which is exact); add a synthetic-data sanity test where the true drivers are known | 2 days |
| W9 | **Related work thin in public-economics literature** (Wagner's law, budget incrementalism, fiscal-rules, COFOG convergence) | Medium | +15–20 references from public finance; positioning table vs Obeng 2022, Adolph 2020, Barnes 2023, Valle-Cruz 2022, Kisman 2026 | 1 day |
| W10 | **Novelty only checked by web proxy** (not Scopus/WoS) | Medium | Run the strings in `docs/07` on Scopus/WoS and screen (needs your institutional login) | 0.5 day |
| W11 | **Length/format:** journal draft is 36 pages single-column with 14 tables and 10 figures; hard-coded numbers in prose | Low-Med | Move 6 tables / 3 figures to a supplement; make remaining numbers macro-driven | 0.5 day |
| W12 | **Legacy-audit section** may read as self-criticism irrelevant to the contribution, or may annoy reviewers | Low | Move to an appendix + 1 paragraph in the main text; keep its lesson in the discussion | 1 h |
| W13 | **AI-use and data provenance disclosure** (legacy data partly LLM-generated; code/drafts AI-assisted) | Compliance | Finalise the declaration; state the legacy dataset is excluded from evidence | 1 h |
| W14 | **Shock behaviour:** the model cannot anticipate crises; what-if goes the wrong way | Low (stated) | Keep as honest limitation; do not present what-if as forecast | — |
| W15 | **Unverified items:** dashboard UI not visually checked; paper layout not checked on Overleaf; Scopus/WoS not run | Low | Do before submission | 2 h |

## 4. Simulated referee reports (condensed)
**Referee 1 (public-finance economist):** "Interesting dataset, but the title promises *budget* allocation while data are executed spending. Where is the link to budget processes, fiscal rules, politics? Econometric literature on COFOG shares is under-cited. Accept the honest negative results; major revision."
**Referee 2 (ML/XAI):** "Methods are standard; value lies in the evaluation. SHAP/LIME explain a member, not the final model; sign disagreements are reported but not resolved. No deep/tabular baselines; many variants, forking-paths risk. Minor-to-major revision."
**Referee 3 (decision-support/HCI):** "Claims of assisting analysts are unsupported by any user study; applicability score and intervals are good ideas but under-covered for the groups that matter. Reject unless a user study or strong softening."

## 5. Action plan

**Before tomorrow 11:30 (conference-ready, ≈ 3–4 h):** (1) compile both zips on Overleaf and fix any layout issue; (2) fill funding / competing-interest / acknowledgement and the AI-use declaration; (3) soften "decision support" wording to "intended to support" and retitle per W2 (suggested: *"GovAllocXAI: Explainable, Constraint-Aware Prediction of Functional Government Expenditure Allocation on Official Data"*); (4) proof-read abstract/introduction; (5) check the dashboard once in a browser.

**Within 2–3 weeks (Q1-ready):** W1 reframing, W2 construct paragraph + budget-vs-outturn check, W3 BOOST pilot for 3 low-income economies, W4 pilot user study (n≈20) or strong softening, W5 5-seed repeat + Holm, W6 Dirichlet + one neural baseline, W7 institutional features ablation, W8 explain the blend, W9 literature, W10 Scopus/WoS run, W11 supplement split.

## 6. Venue recommendation
1. **Conference now:** an applied AI / e-government / data-science conference (IEEE-style, 6 pages).
2. **Journal, realistic order:** *IEEE Access* (fast, broad) → *Socio-Economic Planning Sciences* or *Expert Systems with Applications* after W1–W6 → *Government Information Quarterly* only after W3/W4/W9 give a stronger policy argument.
3. Avoid top ML venues (no algorithmic novelty).

## 7. Is the implementation "finished"?
| Area | Status |
|---|---|
| Data pipeline, panels, cross-checks | ✅ finished |
| Models, stack, kNN, conformal, total budget, allocation engine | ✅ finished (accuracy gains are small by nature) |
| SHAP + LIME | ✅ implemented and evaluated (explain XGBoost member; blend not decomposed → W8) |
| Weak-spot experiments (shock, multi-year, low-income, fairness, tuning, econometric) | ✅ done; mostly negative or data-limited |
| API (v2) + tests (9) | ✅ |
| Dashboard | ⚠ built and re-pointed; **not visually verified** |
| Papers | ✅ compiled; ⚠ need Overleaf check, declarations, retitle |
| Human-subject study | 📄 ready to run, **not run** |
| Low-income data | ❌ blocked by data availability (BOOST pilot is the route) |
| Scopus/WoS search | ❌ needs your institutional access (strings ready) |
