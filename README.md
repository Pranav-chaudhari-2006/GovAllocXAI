# GovAllocXAI

**A benchmark of explainable machine learning for predicting functional government expenditure shares (COFOG) from official multi-country data, with an open dataset, a reproducible pipeline, two papers and a small web tool.**

Authors: Aditi H. Joshi, Pranav S. Chaudhari, Gaurav M. Jaypatre, Digvijay P. Birajdar — Department of Computer Engineering, Pimpri Chinchwad College of Engineering, Pune, India.

> The tool gives a **reference point and a second opinion** for a human budget analyst. It never replaces the decision, and it is not a causal or forecasting claim.

## 1. What the project does

| Question | Answer |
|---|---|
| Task | Predict the **shares (%) of general-government expenditure** spent on each COFOG function (health, education, defence, social protection, ...) for a country-year. Metric: total-variation distance (TVD) = the % of the budget that would have to be moved. |
| Two settings | **Annual update:** last year's split + this year's indicators. **Cold start:** an economy with no history, learned from peer economies (leave-country-out). |
| Data | Official sources only: World Bank (WDI, WGI), Eurostat, OECD, IMF. Panels: A16 (36 economies, 16 functions), A10 (85 economies, 10 divisions), B (WDI, 211 economies, 4 functions). Targets are never imputed. |
| Honest headline | Last year's split is very hard to beat. A learned correction gains about 0.1 pp (not robust across seeds). For economies without history, a stack of learners and a k-nearest-economies average beat the income-group mean on A10 by about 1.3 pp (Holm-corrected). Explanations (SHAP, LIME) agree more on direction than on ranking. Shock years are not anticipated. |
| Also included | Bounded-simplex allocation engine, conformal intervals, applicability score, fairness audit by income group, econometric / Dirichlet / neural baselines, institutional-feature ablations, a forensic audit of the earlier semi-synthetic benchmark. |

Full numbers, tables and caveats are in the papers and in `docs/methods_and_experiments_log.md`.

## Live demo

* Website: https://govallocxai-xi.vercel.app (React, hosted on Vercel)
* API: https://govallocxai-api.onrender.com/api/v2/health (FastAPI, free Render plan: it sleeps after 15 minutes idle and needs 3-5 minutes to wake up and fit its models; the website shows a "warming up" message)

## 2. Repository map

```
GovAllocXAI/
├── README.md  LICENSE
├── data/
│   ├── raw/                  official downloads used by the pipeline (World Bank, Eurostat, OECD, IMF, institutional)
│   ├── dataset_new/          the released dataset (govalloc_cofog_*.csv, data-quality report)
│   └── dataset_old/          the original semi-synthetic dataset, preserved verbatim for the audit
├── pipeline/                 numbered scripts 01-27 (fetch -> build -> experiments -> explainability -> figures/tables)
├── results/                  one folder per experiment (01_legacy_audit ... 19_annual_seed_robustness)
├── papers/
│   ├── main_journal.tex  main_conference.tex  sections/  tables/  figures/  references.bib  results_macros.tex
│   └── overleaf_zips/        ready-to-upload Overleaf projects (journal: elsarticle, conference: IEEEtran)
├── backend/                  FastAPI service (service.py: stack, SHAP/LIME, intervals, peers)
├── frontend/                 React + Vite website (one-input guided page, guide and glossary)
├── tools/                    LaTeX lint, Overleaf zip builder, reference audit, literature search helpers
├── literature/               base papers and related-work PDFs with an index
└── docs/
    ├── guides/               run the website, GitHub + Zenodo release, venues, dataset card, human-study protocol
    ├── audits/               original-benchmark audit, readiness audit, fairness audit, reference audit, peer-panel reviews
    ├── methods_and_experiments_log.md
    └── literature_and_novelty.md
```

## 3. Run it

**Website** (two terminals; details in `docs/guides/01_run_the_website.md`)
```bash
python -m pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --port 8000
```
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173 . The first request takes about a minute while the models are fitted.

**Tests:** `python -m pytest backend/tests -q`

**Reproduce the research** (each script reads `data/` and writes `results/`)
```bash
python pipeline/01_fetch_worldbank_eurostat.py      # download raw data
python pipeline/02_fetch_imf_cofog.py
python pipeline/03_build_dataset.py                 # build data/dataset_new
python pipeline/04_experiments_main.py              # then 05 ... 25 as needed
python pipeline/27_make_figures_tables.py           # figures, tables and LaTeX macros for the papers
python tools/build_overleaf_zips.py                 # papers/overleaf_zips/*.zip
```
Every number in the papers is generated from `results/` through `papers/results_macros.tex` and the table files, so text and tables cannot drift apart.

## 4. Data

`data/dataset_new/` holds the harmonised panels with provenance and imputation flags (`docs/guides/04_dataset_card.md`). `data/dataset_old/` is the original dataset, kept only to document the audit that showed its high R² came from synthetic targets (eleven of fifteen sector columns are exact multiples of one series). Sources and licences: World Bank (CC BY 4.0), Eurostat and OECD (attribution), IMF (attribution, non-commercial research use).

## 5. Papers

Both papers (journal, Elsevier `elsarticle`; conference, IEEE two-column) are built from the same sources in `papers/`. Upload the zips in `papers/overleaf_zips/` to Overleaf and compile with pdfLaTeX (pdflatex, bibtex, pdflatex ×2). Submission checklist and venue list: `docs/guides/03_journals_and_conferences.md`.

## 6. Limitations (short)

OECD/EU-centred COFOG panel; executed, not proposed, spending; the annual setting is a nowcast (same-year indicators); associational explanations; low-income conclusions rest on very few economies; no human-subject study yet (protocol in `docs/guides/human_study/`).

## 7. Citation and licence

Code: MIT (see `LICENSE`). Dataset: CC BY 4.0 for our harmonisation, subject to the original providers' terms. Cite the Zenodo release once published (DOI to be added).

## 8. Known issues
Open items, including a non-reproducible experiment script, are listed in `docs/guides/05_known_issues_and_future_work.md`.
