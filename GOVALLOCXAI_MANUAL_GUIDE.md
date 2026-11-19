# GovAllocXAI: Prototype Operation & Academic Evaluator Guide
**Aavishkar University-Level Research Competition 2026–27**  
**Category: Commerce, Management & Law**

---

## 1. Addressing the "Predefined Data" Question: Technical Rationale & Evaluator Defense

### Is "Predefined Data" a Flaw?
**No. It is an intentional enterprise engineering pattern designed for high-availability decision-support.**

When presenting to evaluators, use the following points:

1. **Dual-Mode Architecture (CDN Instant Cache + Real-Time Dynamic Inference):**
   - **Predefined/Precomputed Cache (`precomputed/`):** Contains pre-calculated model references and SHAP values for **218 economies** across 10-division and 16-division COFOG panels. In physical academic competitions, relying entirely on live cloud server compute introduces network latency, cold-start delays (30–60 seconds on free-tier cloud servers like Render), and potential venue Wi-Fi failures. Caching ensures a zero-latency (under 50 ms) baseline presentation.
   - **Dynamic Inference Mode (`POST /api/v2/recommend`):** When you toggle **"Advanced options"**, the application shifts to live algorithmic computation. The backend runs an **XGBoost + Ridge Stacking Ensemble with Centred Log-Ratio (CLR) target transformation** to compute new budget splits, conformal prediction intervals, and TreeSHAP/LIME feature attributions in real time.

2. **Why Real-World National Budgets Don't Change Randomly:**
   - In **Public Financial Management (PFM)** and **Medium-Term Expenditure Frameworks (MTEF)**, national budget baselines are anchored to official macroeconomic accounts (World Bank WDI, IMF GFS, UN COFOG).
   - Our system provides official baseline benchmarks, while empowering policymakers and evaluators to run **counterfactual "what-if" simulations** and **stress tests** (e.g., recessions, demographic aging, stagflation).

---

## 2. Two Live Demo Scenarios for Evaluators

When the evaluator asks: *"Can I enter custom values?"* or *"Show me how the model responds to changing conditions"*, open **Advanced options** and demonstrate these two scenarios:

### Scenario 1: High-Growth Developing Economy (India / Emerging Market Push)
*Demonstrates how rapid growth and a youthful demographic dividend reallocate public spending towards infrastructure, capital formation, and education.*

- **Preset / Quick Click:** Click **"Preset 1: Developing Growth & Fiscal Push (India)"** (or enter manually below).
- **Manual Input Values:**
  - **Country:** India (`IND`)
  - **Level of detail:** `10 main areas` (`cofog10`)
  - **Your total budget (US$):** `450000000000` ($450 Billion)
  - **GDP growth (%):** `8.2`
  - **Inflation (%):** `4.5`
  - **Unemployment (%):** `4.0`
  - **Population 65+ (%):** `6.8`
  - **Central debt (% GDP):** `55.0`
- **Expected Outcome & Evaluator Narrative:**
  > *"When we simulate an economy with 8.2% GDP growth and a young demographic (only 6.8% over 65), the SHAP feature attribution reveals that high economic momentum drives resources into **Economic Affairs** (capital infrastructure) and **Education** (human capital development), while **Social Protection** expenditure remains modest compared to European welfare states. The total budget amount scales dynamically to our \$450 Billion input."*

---

### Scenario 2: Aging Economy Under Fiscal Consolidation (Germany / Advanced Welfare State)
*Demonstrates how demographic aging and elevated debt levels create mandatory spending commitments in social security and health.*

- **Preset / Quick Click:** Click **"Preset 2: Aging & Fiscal Consolidation (Germany)"** (or enter manually below).
- **Manual Input Values:**
  - **Country:** Germany (`DEU`)
  - **Level of detail:** `16 detailed areas` (`cofog16`)
  - **Your total budget (US$):** `600000000000` ($600 Billion)
  - **GDP growth (%):** `1.2`
  - **Inflation (%):** `2.0`
  - **Unemployment (%):** `3.5`
  - **Population 65+ (%):** `24.5`
  - **Central debt (% GDP):** `85.0`
- **Expected Outcome & Evaluator Narrative:**
  > *"Here we simulate an advanced economy experiencing structural demographic aging (24.5% elderly) and high public debt (85% of GDP). Notice how **Social Protection** surges past 35% of total expenditure and **Health** rises, driven by statutory pension and healthcare obligations. Concurrently, SHAP highlights that high debt constrains discretionary allocations to general economic services, illustrating compliance with fiscal discipline rules like the EU Maastricht Treaty."*

---

## 3. Comprehensive Field & Box Directory

### A. Input Controls (Top Configuration Panel)

| Field Name | Type | Compulsory? | Description & Academic Meaning |
| :--- | :--- | :--- | :--- |
| **Country (`iso3`)** | Dropdown | **Compulsory** | The target nation (218 sovereign economies available). Sets the default socio-economic and governance baseline indicators. |
| **Year of indicators** | Numeric input | *Optional* | The baseline reference year (defaults to the latest verified data year, e.g., 2021/2022). |
| **Level of detail** | Dropdown | *Optional* | **Automatic / COFOG-10 / COFOG-16**. <br>• `COFOG-10`: 10 standard UN divisions (broad global panel of 85 economies). <br>• `COFOG-16`: 16 granular functional sub-divisions (36 OECD/Eurostat economies). |
| **Stress test (what-if)** | Dropdown | *Optional* | Standardized macroeconomic shocks: <br>• **Recession:** GDP -5 pp, Unemployment +3 pp, Debt +15 pp. <br>• **Stagflation:** GDP -2 pp, Inflation +8 pp, Unemployment +2 pp. <br>• **Severe stress:** GDP -15 pp, Inflation +12 pp, Debt +35 pp. |
| **Your total budget (US$)** | Numeric input | *Optional* | Custom monetary ceiling (e.g., `450000000000`). If left blank, the system estimates the national budget using an empirical Ridge model on GDP per capita. |
| **GDP growth (%)** | Decimal input | *Optional* | Real annual GDP growth rate. Drives capital vs. recurrent expenditure trade-offs. |
| **Inflation (%)** | Decimal input | *Optional* | Annual consumer price index change. Influences cost of public service delivery. |
| **Unemployment (%)** | Decimal input | *Optional* | National unemployment rate. Triggers counter-cyclical social safety nets. |
| **Population 65+ (%)** | Decimal input | *Optional* | Percentage of elderly citizens. Directly determines old-age pension and healthcare fiscal burdens. |
| **Central debt (% GDP)** | Decimal input | *Optional* | Sovereign debt-to-GDP ratio. Tests fiscal space and adherence to fiscal responsibility legislation (e.g., FRBM Act). |

---

### B. Summary Metric Cards (KPI Ribbon)

1. **Similarity to training economies (Novelty Score):**
   - **What it shows:** High / Medium / Low similarity, with an underlying Mahalanobis/Euclidean distance score.
   - **Academic Meaning:** Tests whether the country's economic structure lies within the empirical support of the training data. If Novelty is high, the model flags the output as an *extrapolation*, fulfilling responsible AI governance requirements.
2. **Difference from last year (Total Variation Distance / % to Move):**
   - **What it shows:** The percentage of the national budget that would need to be reallocated to match the model benchmark (e.g., `3.4%`).
   - **Academic Meaning:** Measures institutional inertia and policy variance against international peer benchmarks.
3. **Largest area:**
   - **What it shows:** The single largest public expenditure division (e.g., *General Public Services: 24.8%* or *Social Protection: 38.2%*).
4. **Total budget:**
   - **What it shows:** The overall public expenditure ceiling in Billions of USD (e.g., `$450B`), indicating whether it is user-supplied or an econometric estimate.

---

### C. Visual Charts & Analytical Modules

1. **Reference Split (Donut Chart):**
   - Visualizes the full compositional breakdown across all functional areas. All slices sum strictly to 100% via the Centred Log-Ratio (CLR) simplex constraint.
2. **Ranked Areas (Horizontal Bar Chart):**
   - Ranks public sectors from largest to smallest for rapid executive appraisal.
3. **Budget Flow (Sankey Diagram):**
   - Traces the flow of funds: **Total Budget $\rightarrow$ Functional Divisions (COFOG) $\rightarrow$ UN Sustainable Development Goals (SDGs)**.
   - *Legal & Policy Value:* Demonstrates how fiscal budgetary allocations directly operationalize international treaty commitments (e.g., Paris Agreement SDG 13, SDG 3 Good Health, SDG 4 Quality Education).
4. **Difference from Last Year (Diverging Bar Chart):**
   - Displays sector-by-sector variance (+ / - percentage points) relative to the country's last audited actual budget.
5. **Compared with Similar Economies (Peer Comparison Chart):**
   - Compares the recommended split against the weighted average of the **5 most structurally similar economies** identified through k-nearest-neighbors in macroeconomic feature space.
6. **Uncertainty / 80% Prediction Ranges (Conformal Intervals):**
   - Provides risk bounds $[L_i, U_i]$ for each sector calibrated through inductive conformal prediction. Proves to evaluators that the AI acknowledges empirical uncertainty rather than outputting false point estimates.
7. **Detailed Table:**
   - Interactive, sortable ledger listing Area Name, Reference %, Last Actual %, Difference (pp), 80% Range, Dollar Amount ($ bn), Expenditure Size Category (Large/Medium/Small), and linked SDGs.
8. **Explainable AI Feature Waterfall (SHAP & LIME):**
   - **Blue Bars (Positive SHAP):** Indicators that pull this sector's allocation higher than the global baseline.
   - **Pink Bars (Negative SHAP):** Indicators that depress this sector's allocation.
   - *Academic Value:* Converts the AI from an uninterpretable "black box" into a transparent decision-support tool acceptable under administrative law and audit standards.

---

## 4. Relevance to Commerce, Management & Law

When evaluators ask: *"How does this fit our category?"*, state these three core pillars:

1. **Commerce & Public Economics:**
   - Optimizes public sector resource allocation across competing developmental demands.
   - Balances capital investments (transport, digital infrastructure, renewable energy) with macroeconomic stability constraints (inflation, debt-to-GDP).
2. **Public Financial Management (PFM) & Strategic Management:**
   - Replaces subjective, politicized, or crude incremental budgeting ("last year + 5%") with **evidence-based peer benchmarking**.
   - Integrates seamlessly into **Medium-Term Expenditure Frameworks (MTEF)** and **Performance Budgeting Systems**.
3. **Law & Governance:**
   - **Fiscal Rule Compliance:** Ensures expenditure recommendations respect statutory debt and deficit ceilings under fiscal responsibility laws (e.g., India's FRBM Act 2003, EU Stability and Growth Pact).
   - **Explainability as a Legal Right:** Fulfills Article 22 GDPR / Administrative Law principles regarding the "Right to Explanation" in algorithmic public decision-making.
   - **SDG Treaty Accountability:** Legally bridges budget line items to UN Sustainable Development Goal commitments.

---

## 5. 3-Minute Presentation Walkthrough Script (Presenter Cheat Sheet)

- **Step 1 (0:00 - 0:45) - The Problem & Hook:**
  > *"Respected Evaluators, in public finance, governments allocate trillions of dollars annually. Yet, most national budgets still rely on incremental budgeting—simply copying last year's figures with political lobbying—often misallocating scarce resources. Our project, **GovAllocXAI**, provides an Explainable AI decision-support platform that generates benchmark budget allocations grounded in official UN COFOG standards and macroeconomic data."*

- **Step 2 (0:45 - 1:30) - Live Baseline Demonstration:**
  > *"On screen, we select India. Instantly, our system computes the reference split across all 10 COFOG functions. The donut and ranked charts show education, health, and economic affairs. Through our Sankey diagram, we map these expenditures directly to UN Sustainable Development Goals, establishing legal and policy accountability."*

- **Step 3 (1:30 - 2:15) - Manual Simulation & What-If Stress Testing:**
  > *"To show that this is not a static lookup table, let's open Advanced Options. We can input custom macroeconomic indicators or click 'Preset 1' for a high-growth developing scenario (8.2% GDP growth, \$450B budget). When we run the model, our XGBoost-Ridge Stacking Ensemble dynamically recalculates the allocations in real time, projecting an expansion in infrastructure and education while adhering to bounded mathematical constraints."*

- **Step 4 (2:15 - 3:00) - Explainability & Legal Governance Wrap-Up:**
  > *"Most importantly, we do not present a black box. Look at this SHAP waterfall: it proves to finance ministry auditors exactly WHY the model allocated each percentage point—attributing the shift to GDP growth, demographic structure, and governance indicators. GovAllocXAI brings algorithmic transparency, fiscal discipline, and data-driven equity to public financial management."*
