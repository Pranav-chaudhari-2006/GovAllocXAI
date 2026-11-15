# Publish the dataset on Zenodo and get its DOI (dataset record)

The file to upload is ready: **`release\GovAlloc-COFOG_v1.0.zip`** (6 MB, rebuilt any time with `python tools/build_zenodo_package.py`). You will make **one Zenodo record for the dataset** now. The code (GitHub release) is a separate record, made later.

## Steps
1. Open https://zenodo.org and click **Log in** (top right) > **Log in with GitHub** (or with your email / ORCID).
2. Click **+ New upload** (top right).
3. **Files:** drag `GovAlloc-COFOG_v1.0.zip` into the box and wait for the green bar. (Zenodo shows the files inside the zip after publishing.)
4. **Digital Object Identifier:** choose **"No"** (you do not have one yet). Zenodo will create it for you.
5. **Resource type:** `Dataset`.
6. **Title:** `GovAlloc-COFOG: Harmonised General-Government Expenditure by Function (COFOG) Panels with Provenance and Imputation Flags`
7. **Publication date:** today's date (15-11-2026 or the day you publish).
8. **Creators** (click *Add creator* for each; use this order; add affiliation `Pimpri Chinchwad College of Engineering, Pune, India` for all; add each ORCID if they have one):
   Chaudhari, Pranav S. · Joshi, Aditi H. · Jaypatre, Gaurav M. · Birajdar, Digvijay P.
9. **Description** (paste):
   > GovAlloc-COFOG is a harmonised, open panel of general-government expenditure shares by COFOG function (health, education, defence, social protection, ...) for up to 217 economies, 2000-2024, with socio-economic and governance features. Targets are official published statistics from Eurostat, OECD and the IMF and are never imputed; imputed feature values are flagged per cell. The release contains: Panel A16 (36 economies, 16 functions), Panel A10 (85 economies, 10 divisions), Panel B (WDI sector series, 211 economies), the master table, quality statistics and a data card. The original semi-synthetic dataset from our earlier study is included in a clearly marked "legacy" folder only to document an audit; it must not be used for modelling. Data are executed (outturn) spending, not planned budgets. Code and papers: https://github.com/Pranav-chaudhari-2006/GovAllocXAI
10. **Version:** `1.0`
11. **Language:** English.
12. **Keywords** (add each): `government expenditure`, `COFOG`, `public finance`, `budget allocation`, `open data`, `compositional data`, `World Bank`, `Eurostat`.
13. **Licenses:** pick **Creative Commons Attribution 4.0 International (CC-BY-4.0)**. (Source terms are listed in `SOURCES_AND_LICENCES.txt` inside the zip.)
14. **Related/alternate identifiers** (click *Add*): identifier `https://github.com/Pranav-chaudhari-2006/GovAllocXAI`, relation **`is supplemented by`**, resource type `Software`.
15. **Funding:** leave empty (no external funding). **Access:** *Open access* (public).
16. Scroll to the top, click **Save**, check the preview, then click **Publish** and confirm. **Publishing cannot be undone** (files are frozen; you can still edit the description and metadata, and upload a new version).
17. The record page now shows the **DOI** (for example `10.5281/zenodo.1234567`) on the right. Two numbers exist: the **version DOI** (this exact release) and the **concept DOI** ("Cite all versions"). Use the **concept DOI** in the papers.
18. Send me the DOI. I will insert it in the dataset paper, the benchmark paper, the README and the dataset card and push once.

## Features to leave ON
* Public (open access) visibility · "Request access" **off** · embargo **off** · community (optional, e.g. search "Open Science").

## Later changes
Files cannot be changed after publishing. To correct data, click **New version** on the record, upload a new zip and publish; the concept DOI keeps pointing to the latest version.

## Kaggle (optional, after Zenodo)
Upload only the `data/` CSVs and `DATASET_CARD.md`, use the same title and the CC BY 4.0 licence, set visibility **Public**, and write "Archived at Zenodo: <DOI>" in the description.
