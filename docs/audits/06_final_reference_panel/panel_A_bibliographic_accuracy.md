# Panel A - Bibliographic accuracy audit

Read-only audit; no repo file other than this report was changed.
Scope: papers/references.bib (84 entries), the Overleaf zips' references.bib, and the compiled PDFs (Journal 39 pp., Conference 6 pp.).
Method: Crossref API for all 63 DOI entries (authors/order/diacritics, title, year, venue, volume, issue, pages); arXiv API for 11 arXiv-linked entries; WebSearch for items Crossref lacks. The OECD and doiserbia pages refused automated fetch (403/refused) and were not bypassed; search snippets were used instead.

## 0. Structural findings
- Cited keys: the Journal cites all 84 bib entries; the Conference cites 27 (a subset). No uncited entries, no missing keys, no duplicate DOIs, no duplicate titles.
- Overleaf zips (Journal and Conference): references.bib is identical to the master except `doi = {X}` became `url = {https://doi.org/X}` on all 63 DOI entries (normalised diff empty). The two zip bibs are byte-identical.
- PDFs: 84 references printed in the Journal and 27 in the Conference; zero "??"; no printed-but-uncited entries; list order equals first-citation order and maps exactly to keys 1..84 / 1..27.
- In-text (Journal): 93 \cite occurrences; every number 1..84 appears in the text and none outside it. 18 random spot checks all matched (Yang et al. -> [15]; Di Stefano and Resce -> [8]; Kisman et al. -> [65]; Santschi et al. -> [11]; [40-42] = grinsztajn/shwartzziv/borisov; [57, 59] = alvarezmelis/slack; [62,63] = hooker/bhatt; [1, 2] = davis/jones; [33] = aitchison; [61] = kumar; [7, 8] = caravaggio/distefano). Ranges such as [22]-[24] and [28]-[32] are compressed by the cite package (correct).
- In-text (Conference): [1],[2] gur/dragulin; [7]-[10] santschi..mohith; [11],[12] lundberg2017/ribeiro; [19]-[24] data sources; [25] lundberg2020; [26] cameron; [27] wolpert. All consistent.
- Formatting: IEEEtran numeric in both; consistent "[Online]. Available:" links.

## 1. Per-entry results
(Checked: authors/order/spelling, title, year, venue, volume, number, pages, DOI/URL.)

All fields match Crossref, verdict OK, for: valle2022, guerrero2022, caravaggio2025, distefano2025, chand2022, nguyen2026 and zhang2026 (bib uses initials; Crossref has full given names), kisman2026, nonato2026, kaufmann2011 (Crossref issue "02" = 2), cameron2008, bergmeir2018, medeiros2021, adolph2020, lamartina2011, garrett2001, dunne2003, alesina1999, kneller1999, brender2005, jones2005 (online 2004, print vol 15(3) 2005: bib correct), devarajan1996, afonso2010, potrafke2010, bove2017, davis1966, wolpert1992, breiman2001, hyndman2006, lundberg2020, ribeiro2016, slack2020, chen2016xgboost, rudin2019, yang2023, egozcue2003, douma2019, ferrari2004, angelopoulos2023, barber2023, lei2018, shwartzziv2022, borisov2024, ghorbani2019, mehrabi2021, obermeyer2019, athey2019, mullainathan2017, goulet2022, grinsztajn2022, mohith2026, radulescu2015, rogoff1988 (Crossref stores only start page "1"; bib 1--16 is right), yao2025, holm1979, aitchison1986, ke2017, lundberg2017, santschi2024.
Crossref glitches (bib is right): radulescu2015 has given/family swapped; mohith2026 lists "Suhas S / M" for S. M. Suhas.

| key | mismatch (old -> correct) | verdict |
|---|---|---|
| nordhaus1975 | pages `169` -> `169--190` (Crossref stores start page only; RES 42(2) is 169-190). Printed [30] shows "p. 169" | FIX |
| krishna2022 | authors `...Jabbari, Shahin and Wu, Zhiwei Steven and Lakkaraju...` -> arXiv 2202.01602 order `Krishna, Han, Gu, Wu (Steven), Jabbari, Lakkaraju`. Printed [56] "S. Jabbari, Z. S. Wu" -> "Z. S. Wu, S. Jabbari" | FIX |
| francies2026 | title truncated: Crossref title continues `: SHAP Attribution, Causal Inference, Counterfactual Reasoning, and the Budget Explainability Score` | FIX |
| nzazi2025 | @inproceedings with booktitle `Procedia Computer Science, vol. 272 (conference proceedings, EUSPN 2025)`; Crossref = journal-article, Procedia Computer Science, vol 272, pp 261-268. Printed [17] reads awkwardly | FIX |
| kaufman2012 | pages `15` -> `1--21` (Crossref; ACM article no. 15). Printed [84] "p. 15" | FIX (minor) |
| wdi, oecd_table11, imf_gfs, un2000cofog | IEEEtran lowercases titles in print: [68]/[19] "World development indicators", [71]/[22] "national accounts, dsd_nasec10@df_table11", [73]/[23] "Government finance statistics", [72]/[24] "Classification of the functions of government". Brace proper-noun titles | FIX |
| dragulin2025 | `{\c{S}}tefan`, `{\c{S}}cheau` print S-cedilla; Crossref and Romanian orthography use S-comma-below | FIX (minor) |
| barnes2023 | `Cournède` encoded with grave accent `Courn{\`e}de`; should be acute `Courn{\'e}de`. Authors confirmed by OECD/RePEc (Crossref has none). Title/number 1785/year OK | FIX (minor) |
| prokhorenkova2018 | no pages; NeurIPS 2018 vol 31 pages 6638--6648 (from memory, verify at papers.nips.cc). Authors/title verified on arXiv 1706.09516 | FIX (minor, verify) |
| gur2025 | Crossref has no vol/issue/pages (placeholders "00", "25-25"); journal lists online-first, accepted 8 Jul 2025. Names correct. Printed [5] has no vol/pages | OK (add "online first" note, optional) |
| dhungel2025 | LNCS volume number absent in Crossref and bib; prints "ser. Lecture Notes in Computer Science, 2025" | OK (minor, optional) |
| roberts2017 | `Roberts, David R. and others` (Crossref has 14 authors); prints "D. R. Roberts et al." | OK (minor) |
| alvarezmelis2018, doshi2017, gorishniy2021, hooker2018, kumar2020, bhatt2020, hardt2016, romano2019, krishna2022 | titles/authors/ids verified against arXiv API; venue notes (NeurIPS 2019, ICML 2020, IJCAI 2020...) not machine-verifiable | OK except krishna2022 |
| un2015agenda, eurostat_cofog | web sources, URLs well formed | OK |

## 2. PDF checks
- No "??", no truncated or garbled entries. "Dr(breve)agulin", "(cedilla)Stefan" in the extracted text are combining-accent extraction artefacts of the OT1 font, not errors; "https: //doi.org" is a \url line wrap.
- Lowercase proper nouns: only the four web-source titles above. OECD, COFOG, India, Brazilian, Australian, Turkiye, SHAP, LIME, AI, XGBoost, Worldwide Governance Indicators are all preserved.
- Duplicated DOIs: none. Every bib entry with a DOI/URL prints a link; aitchison1986 (book) has none by design.
- Conference list: same format; the four lowercase titles apply at [19], [22], [23], [24]. nordhaus/krishna/francies/nzazi/kaufman are not cited there.

## 3. Journal formatting consistency
Consistent IEEEtran numeric style. Volume/issue/pages are printed for every journal article where Crossref has them, except: [30] Nordhaus (range truncated), [84] Kaufman ("p. 15"), [5] Gur (none exist yet), [17] Nzazi (printed book-style), [66] Dhungel (no LNCS volume).

## Exact fix list (key | field | old | new)
1. nordhaus1975 | pages | 169 | 169--190
2. krishna2022 | author | ...Jabbari, Shahin and Wu, Zhiwei Steven... | ...Wu, Steven and Jabbari, Shahin... (arXiv order)
3. francies2026 | title | A multi-layer explainable {AI} framework for transparent urban budget allocation in smart cities | append `: {SHAP} attribution, causal inference, counterfactual reasoning, and the budget explainability score`
4. nzazi2025 | type/venue | @inproceedings, booktitle `Procedia Computer Science, vol. 272 (conference proceedings, EUSPN 2025)` | @article, journal `Procedia Computer Science`, volume 272, pages 261--268, note `EUSPN 2025`
5. kaufman2012 | pages | 15 | 1--21 (or keep and add note Art. no. 15)
6. wdi | title | World Development Indicators | {World Development Indicators}
7. oecd_table11 | title | ...National Accounts, DSD\_NASEC10@DF\_TABLE11 | ...{National Accounts}, {DSD\_NASEC10@DF\_TABLE11}
8. imf_gfs | title | Government Finance Statistics: ... | {Government Finance Statistics}: ...
9. un2000cofog | title | Classification of the Functions of Government | {Classification of the Functions of Government}
10. dragulin2025 | author | S-cedilla in Stefan, Scheau | S-comma-below (minor)
11. barnes2023 | author | Courn{\`e}de | Courn{\'e}de
12. prokhorenkova2018 | pages | (none) | 6638--6648 (verify)
13. gur2025 | note | (none) | add "Online first" (optional)
After editing papers/references.bib, regenerate both Overleaf zips so the doi -> url=https://doi.org/... transformation is reapplied.
