# Push to GitHub, create a release, get a Zenodo DOI

Repository: https://github.com/Pranav-chaudhari-2006/GovAllocXAI (already set as `origin`; the local branch is ahead of the remote, so the push is a fast-forward).

## 1. Check
```powershell
cd C:\Users\prana\Desktop\GovAllocXAI
git remote -v
git status
git log --oneline | Select-Object -First 3
```

## 2. Push
```powershell
git push -u origin main
```
If GitHub says the remote has commits you do not have: `git pull origin main --allow-unrelated-histories`, resolve any conflict, push again. Never use `--force` unless you are sure the remote has nothing you need. Authentication failures: use a Personal Access Token (GitHub > Settings > Developer settings > Tokens (classic), scope `repo`) as the password, or run `gh auth login`.

## 3. Link GitHub to Zenodo (one time, free)
1. https://zenodo.org > **Log in with GitHub** > authorise.
2. https://zenodo.org/account/settings/github/ > switch **ON** the toggle for `Pranav-chaudhari-2006/GovAllocXAI` (click *Sync now* if it is missing).

## 4. Create the release (this triggers the DOI)
GitHub repo > **Releases** > *Create a new release* > tag `v1.0.0` (create on publish) > title `GovAllocXAI v1.0.0` > one-paragraph description > **Publish release**. Wait 1-3 minutes.

## 5. Read the DOI
Zenodo > your uploads > the new record > **DOI** (e.g. `10.5281/zenodo.1234567`). Use the *concept DOI* ("all versions") in the paper. Edit the record metadata (authors with affiliation, licence CC BY 4.0 for the data / MIT for the code, keywords) and **Publish**.

## 6. Put the DOI into the papers
Replace `XXXXXXX` in `papers/main_journal.tex` (Data availability / Code availability), rebuild the zips (`python tools/build_overleaf_zips.py`), push again.

## Common problems
* Repo not listed in Zenodo: make it Public and *Sync now*.
* No DOI after publishing: the toggle must be ON **before** the release; otherwise delete the release and publish `v1.0.1`.
