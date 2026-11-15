"""Download IMF GFS 'Government Expenditures by Function' (COFOG) for ALL World-Bank economies: general government (S13),
percent of total expenditure (POTO_PT), annual, 2000+. Adds non-OECD economies (India, Brazil, Indonesia, ...) to the real-data panel.
Output: data/raw/imf/imf_gfs_cofog_S13_POTO.csv (slim: COUNTRY, COFOG, TIME_PERIOD, OBS_VALUE, STATUS)
Re-runnable: per-country raw files are cached in data/raw/imf/by_country/.
"""
import io
import json
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data/raw/imf"
BYC = OUT / "by_country"
BYC.mkdir(parents=True, exist_ok=True)
meta = json.load(open(ROOT / "data/raw/worldbank/countries.json"))
ISO3 = sorted(c["id"] for c in meta if c["region"]["id"] != "NA")
URL = "https://api.imf.org/external/sdmx/2.1/data/IMF.STA,GFS_COFOG/{c}.S13.G2MF.*.POTO_PT?startPeriod=2000"
KEEP = ["COUNTRY", "COFOG", "TIME_PERIOD", "OBS_VALUE", "STATUS"]


def job(c):
    f = BYC / f"{c}.csv"
    if f.exists():
        return c, "cached"
    for i in range(4):
        try:
            r = requests.get(URL.format(c=c), headers={"Accept": "application/vnd.sdmx.data+csv"}, timeout=90)
            if r.status_code == 404 or (r.status_code == 200 and len(r.content) < 300):
                f.write_text("")            # no data for this economy
                return c, "empty"
            r.raise_for_status()
            d = pd.read_csv(io.BytesIO(r.content), usecols=lambda x: x in KEEP, low_memory=False)
            d.to_csv(f, index=False)
            return c, f"ok {len(d)}"
        except Exception as e:  # noqa: BLE001
            time.sleep(2 * (i + 1))
    return c, "FAIL"


with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(job, ISO3))
print({k: sum(1 for _, s in res if s.startswith(k)) for k in ["ok", "empty", "cached", "FAIL"]}, flush=True)
parts = [pd.read_csv(f) for f in sorted(BYC.glob("*.csv")) if f.stat().st_size > 5]
allp = pd.concat(parts, ignore_index=True)
allp.to_csv(OUT / "imf_gfs_cofog_S13_POTO.csv", index=False)
print("rows", len(allp), "countries", allp.COUNTRY.nunique(), flush=True)
