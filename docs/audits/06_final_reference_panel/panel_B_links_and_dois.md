# Panel B: link and DOI audit (15 Nov 2026)

Method: plain HTTP (User-Agent GovAllocXAI-linkcheck/1.0), doi.org HEAD, Crossref API, GitHub public API; PyMuPDF on the compiled PDFs. No repo files edited.

## Summary
- 63 DOIs in references.bib: all 63 resolve through doi.org (HTTP 200/202, or 403 = publisher blocks robots) and every Crossref title matches the bib title (differences only in TeX braces/case/subtitle truncation, e.g. "XGBoost" for "XGBoost: A scalable tree boosting system"). No retraction, expression-of-concern or update-to flags in Crossref for any entry. Document types are consistent: only francies2026 is a preprint DOI (10.21203/rs.3.rs-9087087/v1, Research Square) and the bib marks it @misc "Preprint", so it is not presented as a journal article. barnes2023 is a Crossref "report" (OECD working paper), correctly cited as one.
- gur2025 (10.2298/pan240929025g): first doi.org attempt timed out; retry returned 302 to doiserbia.nb.rs, Crossref OK.
- 28 plain URLs (bib + Data/Code availability): all answered 200 except sdmx.oecd.org (403 to scripts, an API root, "blocked to robots") and jstor.org/stable/4615733 (Client Challenge page, "blocked to robots", cannot verify by tool; DOI-less Holm 1979 entry).
- Data portals (WDI databank, WGI, Eurostat gov_10a_exp, OECD Data Explorer, IMF data.imf.org, IMF GFS_COFOG, UNSD classifications/Econ, sdgs.un.org/2030agenda, data.worldbank.org) are live and the titles match the cited resources (IMF GFS_COFOG title "GFS_COFOG"; UNSD "Classifications on economic statistics"; 2030 Agenda page title "Transforming our world"). Eurostat and OECD pages are JavaScript apps with empty titles, so content could not be confirmed by tool; they load (200).
- Journal PDF: 96 link annotations; all 63 bib DOIs have a https://doi.org/<doi> annotation and none extra; all bib URLs (arXiv, portals, AISeL, NeurIPS, JSTOR) have annotations; all link text is coloured 0x0052a4 (linkblue). Reference-list links match their entries.
- Conference PDF: 0 link annotations (expected). URLs/DOIs are printed in full (36 DOI strings plus arXiv/portal URLs) but wrap across lines in the extraction (e.g. "https://doi.org/10.1016/" then remainder, "https://data.worldbank." then rest); acceptable for print. The conference paper cites no GitHub URL and has no placeholders.

## Items needing action
| # | Item | Finding | Exact fix |
|---|------|---------|-----------|
| 1 | Code availability URL https://github.com/Pranav-chaudhari-2006/GovAllocXAI- (main_journal.tex l.120) | Repo exists, public, created 15 Nov 2026 10:51Z, but EMPTY ("This repository is empty", size 0). `git ls-remote origin` (origin = ...GovAllocXAI-.git) returns nothing. The link resolves (200) but points to no code. The trailing hyphen is unusual; confirm it is the intended repo name. | Push the branch (`git push -u origin clean-main:main` or as per docs/guides/02) before submission; optionally rename repo to GovAllocXAI and update URL. |
| 2 | Journal PDF is stale | scratchpad g_Journal_Q1/main.pdf (16:06) links to https://github.com/Pranav-chaudhari-2006/GovAllocXAI (no hyphen, HTTP 404 in the PDF annotation and printed text). Source main_journal.tex (16:24) has the hyphen; g_Journal_Q1/main.tex (16:03) lacks it. | Recompile the PDF from the current main_journal.tex and re-check the annotation. |
| 3 | Zenodo DOI (Data availability, main_journal.tex l.117) | Placeholder remains as wording: "a permanent Zenodo archive with a DOI is to be created at acceptance and its DOI inserted here". The literal string XXXXXXX is no longer in papers/*.tex or in the PDFs. XXXXXXX remains only in docs/guides/02_github_and_zenodo_release.md (l.30), docs/guides/05_known_issues_and_future_work.md (l.26) and older audit files. | Create the Zenodo release, replace the sentence with the real `https://doi.org/10.5281/zenodo.<n>` (concept DOI), recompile; or keep the wording if a post-acceptance archive is intended. |
| 4 | sdmx.oecd.org (bib oecd_table11, printed in both PDFs) | 403 to scripts; API root, not a human page, cannot verify. | Optional: replace with https://sdmx.oecd.org/public/rest/ or drop; or leave and accept. |
| 5 | JSTOR holm1979 https://www.jstor.org/stable/4615733 | Bot challenge; cannot verify by tool. | Optional manual check in a browser. |
| 6 | Eurostat/OECD portal pages | Load but JS-rendered; content match not machine-verifiable. | Optional manual check that gov_10a_exp and the OECD Data Explorer still show COFOG/Table 11. |
| 7 | Duplicated URL pairs in bib | eurostat_cofog has two URLs (with and without /default/table); imf_gfs has two URLs (data.imf.org/Datasets/GFS_COFOG and .../en/datasets/IMF.STA:GFS_COFOG), all 200. Cosmetic only. | None required. |

No DOI resolves to a different paper, none is retracted, and no preprint DOI is presented as a journal article.

Raw output: scratchpad res.txt and pdf.txt (session scratchpad).
