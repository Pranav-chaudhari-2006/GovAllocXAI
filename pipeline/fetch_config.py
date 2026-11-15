"""Shared indicator configuration for the GovAllocXAI v2 data pipeline."""
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
COFOG_CODES = ["TOTAL","GF01","GF02","GF03","GF04","GF0402","GF0403","GF0404","GF0405","GF0406","GF0407","GF0408","GF05","GF06","GF0602","GF0603","GF07","GF08","GF09","GF10"]
