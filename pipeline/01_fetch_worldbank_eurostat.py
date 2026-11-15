"""Download RAW official data (World Bank WDI/WGI + Eurostat COFOG). Re-runnable; saves JSON verbatim.
Usage: python pipeline/01_fetch_worldbank_eurostat.py
"""
import json, time, pathlib, requests, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
WB = ROOT/"data/raw/worldbank"; ES = ROOT/"data/raw/eurostat"
WB.mkdir(parents=True, exist_ok=True); ES.mkdir(parents=True, exist_ok=True)

WB_IND = {
 # --- features
 "NY.GDP.MKTP.CD":"gdp_usd","NY.GDP.PCAP.CD":"gdp_per_capita_usd","NY.GDP.MKTP.KD.ZG":"gdp_growth_pct",
 "FP.CPI.TOTL.ZG":"inflation_pct","SP.POP.TOTL":"population","SP.URB.TOTL.IN.ZS":"urban_pop_pct",
 "SP.POP.65UP.TO.ZS":"pop_65plus_pct","SP.POP.0014.TO.ZS":"pop_0_14_pct",
 "GC.TAX.TOTL.GD.ZS":"tax_revenue_pct_gdp","GC.DOD.TOTL.GD.ZS":"central_gov_debt_pct_gdp",
 "GC.REV.XGRT.GD.ZS":"revenue_pct_gdp","GC.XPN.TOTL.GD.ZS":"total_expense_pct_gdp","GC.NLD.TOTL.GD.ZS":"net_lending_pct_gdp",
 "SI.POV.DDAY":"poverty_215_pct","SL.UEM.TOTL.ZS":"unemployment_pct","SE.ADT.LITR.ZS":"adult_literacy_pct",
 "SP.DYN.LE00.IN":"life_expectancy","SH.DYN.MORT":"under5_mortality","IT.NET.USER.ZS":"internet_users_pct",
 "EG.ELC.ACCS.ZS":"electricity_access_pct","SH.H2O.BASW.ZS":"basic_water_access_pct",
 "EN.GHG.CO2.PC.CE.AR5":"co2_per_capita_t","NV.AGR.TOTL.ZS":"agri_value_added_pct_gdp","NV.IND.TOTL.ZS":"industry_value_added_pct_gdp",
 "NE.TRD.GNFS.ZS":"trade_pct_gdp","SI.POV.GINI":"gini",
 "GE.EST":"gov_effectiveness_wgi","CC.EST":"control_corruption_wgi","RL.EST":"rule_of_law_wgi","RQ.EST":"regulatory_quality_wgi",
 # --- official sector-spending targets
 "SE.XPD.TOTL.GD.ZS":"T_edu_pct_gdp","SE.XPD.TOTL.GB.ZS":"T_edu_pct_govexp",
 "SH.XPD.GHED.GD.ZS":"T_health_pct_gdp","SH.XPD.GHED.GE.ZS":"T_health_pct_govexp",
 "MS.MIL.XPND.GD.ZS":"T_defence_pct_gdp","MS.MIL.XPND.ZS":"T_defence_pct_govexp",
 "GB.XPD.RSDV.GD.ZS":"T_rnd_pct_gdp",
}
def get(url, tries=5, to=45):
    for i in range(tries):
        try:
            r = requests.get(url, timeout=to); r.raise_for_status(); return r
        except Exception as e:
            print("  retry", i, str(e)[:80]); time.sleep(2*(i+1))
    raise RuntimeError(url)

from concurrent.futures import ThreadPoolExecutor
def job_wb(code):
    f = WB/f"{code}.json"
    if f.exists() and f.stat().st_size>100: return code,"cached"
    try:
        api = ("GOV_WGI_"+code+"?source=3&") if code.endswith(".EST") else (code+"?")  # WGI lives in WB source 3
        url=f"https://api.worldbank.org/v2/country/all/indicator/{api}format=json&per_page=20000&date=2000:2024"
        f.write_text(get(url).text); return code,"ok"
    except Exception as e: return code,"FAIL"
BASE="https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10a_exp"
COFOG=["TOTAL","GF01","GF02","GF03","GF04","GF0402","GF0403","GF0404","GF0405","GF0406","GF0407","GF0408","GF05","GF06","GF0602","GF0603","GF07","GF08","GF09","GF10"]
def job_es(a):
    unit,c=a; f=ES/f"{unit}_{c}.json"
    if f.exists() and f.stat().st_size>100: return a,"cached"
    try:
        url=f"{BASE}?format=JSON&lang=EN&unit={unit}&sector=S13&na_item=TE&cofog99={c}&sinceTimePeriod=2000"
        f.write_text(get(url).text); return a,"ok"
    except Exception as e: return a,"FAIL"
if not (WB/"countries.json").exists():
    (WB/"countries.json").write_text(json.dumps(get("https://api.worldbank.org/v2/country?format=json&per_page=400").json()[1]))
with ThreadPoolExecutor(2) as ex:
    for r in ex.map(job_es,[(u,c) for u in ["PC_GDP","PC_TOT","MIO_EUR"] for c in COFOG]): print("ES",r,flush=True)
    for r in ex.map(job_wb,list(WB_IND)): print("WB",r,flush=True)
print("done",flush=True)
