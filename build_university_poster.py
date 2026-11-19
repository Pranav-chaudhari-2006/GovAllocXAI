"""
Master script to generate the official AAVISHKAR University-Level Research Poster:
- Poster title: Avishkar University Level Poster
- Output files:
  - poster/Avishkar University Level Poster.svg
  - poster/Avishkar University Level Poster.pdf
  - poster/Avishkar University Level Poster.png (300 DPI target)
  - poster/Avishkar University Level Poster Preview.png (lightweight preview)
"""

import os
import base64
import fitz
from PIL import Image

def get_base64_image(path):
    if not os.path.exists(path):
        print(f"ERROR: Image not found at {path}")
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Encode figures
b64_cov = get_base64_image("papers/figures/fig2_data_coverage.png")
b64_audit = get_base64_image("papers/figures/fig3_legacy_audit.png")
b64_arch = get_base64_image("papers/figures/fig1_architecture.png")
b64_res = get_base64_image("papers/figures/fig4_main_results.png")
b64_wdi = get_base64_image("papers/figures/fig6_wdi_panel.png")
b64_xai = get_base64_image("papers/figures/fig8_shap_vs_lime.png")
b64_dash = get_base64_image("tests/avishkar_poster/dashboard_screenshot.png")

# Palette constants
NAVY_DEEP = "#071224"
NAVY_CARD_HEADER = "#0F264A"
BLUE_PRIMARY = "#1E40AF"
BLUE_ACCENT = "#0284C7"
CYAN_ACCENT = "#06B6D4"
CYAN_LIGHT = "#E0F2FE"
AMBER_ACCENT = "#D97706"
AMBER_LIGHT = "#FEF3C7"
BG_CANVAS = "#F1F5F9"
BG_CARD = "#FFFFFF"
BORDER_CARD = "#CBD5E1"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#334155"
TEXT_LIGHT = "#64748B"
TEXT_WHITE = "#FFFFFF"
GREEN_ACCENT = "#0D9488"
GREEN_LIGHT = "#CCFBF1"

def escape_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

svg = []
svg.append('<?xml version="1.0" encoding="UTF-8"?>')
svg.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000mm" height="1000mm" viewBox="0 0 2835 2835">')

# Definitions: Filters, Gradients, Icons
svg.append("""<defs>
  <!-- Drop shadow for cards -->
  <filter id="cardShadow" x="-2%" y="-1%" width="104%" height="103%" filterUnits="userSpaceOnUse">
    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.08" />
  </filter>

  <!-- Gradients -->
  <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#061021" />
    <stop offset="50%" stop-color="#0D244D" />
    <stop offset="100%" stop-color="#1E3A8A" />
  </linearGradient>

  <linearGradient id="accentBar" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#0284C7" />
    <stop offset="50%" stop-color="#06B6D4" />
    <stop offset="100%" stop-color="#10B981" />
  </linearGradient>

  <linearGradient id="cardHeaderGrad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#0F2448" />
    <stop offset="100%" stop-color="#1E3A8A" />
  </linearGradient>

  <linearGradient id="highlightPill" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#1E293B" />
    <stop offset="100%" stop-color="#334155" />
  </linearGradient>
</defs>""")

# Background
svg.append(f'<rect width="2835" height="2835" fill="{BG_CANVAS}"/>')

# =========================================================================
# 1. TOP HEADER BANNER (y: 35 to 295, height: 260)
# =========================================================================
svg.append(f'''
<!-- Header Card -->
<g id="header">
  <rect x="45" y="35" width="2745" height="260" rx="18" fill="url(#headerGrad)" filter="url(#cardShadow)"/>
  <rect x="45" y="291" width="2745" height="4" rx="2" fill="url(#accentBar)"/>

  <!-- Top Metadata Row -->
  <!-- Left Competition Badge -->
  <rect x="75" y="55" width="580" height="34" rx="8" fill="#1E293B" stroke="#334155" stroke-width="1.5"/>
  <text x="365" y="78" font-size="18" font-weight="bold" fill="#38BDF8" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">★ AAVISHKAR 2026–27 | UNIVERSITY-LEVEL RESEARCH CONVENTION</text>

  <!-- Center Category Badge -->
  <rect x="1100" y="52" width="635" height="40" rx="10" fill="#B45309" stroke="#F59E0B" stroke-width="2"/>
  <text x="1417" y="78" font-size="21" font-weight="bold" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">RESEARCH CATEGORY: COMMERCE, MANAGEMENT &amp; LAW</text>

  <!-- Right Blank Code Box -->
  <rect x="2385" y="55" width="375" height="34" rx="8" fill="#1E293B" stroke="#64748B" stroke-width="1.5"/>
  <text x="2572" y="78" font-size="18" font-weight="bold" fill="#E2E8F0" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">RESEARCH CODE: [                      ]</text>

  <!-- Main Title -->
  <text x="1417" y="145" font-size="64" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" letter-spacing="0.5">GovAllocXAI: Explainable Machine Learning Benchmark for Predicting</text>
  <text x="1417" y="212" font-size="60" font-weight="800" fill="#38BDF8" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" letter-spacing="0.5">Functional Government Expenditure Shares from Official Multi-Country Data</text>

  <!-- Subtitle -->
  <text x="1417" y="250" font-size="25" font-weight="600" fill="#CBD5E1" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">A Multi-Country Decision-Support Framework for Public Financial Management, Fiscal Governance &amp; Sustainable Resource Allocation</text>

  <!-- KPI Highlight Badges Ribbon -->
  <g id="kpi-ribbon" transform="translate(0, 10)">
    <!-- Pill 1 -->
    <rect x="75" y="248" width="640" height="28" rx="7" fill="#0F172A" stroke="#0284C7" stroke-width="1.2"/>
    <text x="395" y="268" font-size="15" font-weight="700" fill="#E0F2FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">📊 5,450 Country-Years across 217 Economies (2000–2024)</text>

    <!-- Pill 2 -->
    <rect x="735" y="248" width="665" height="28" rx="7" fill="#0F172A" stroke="#06B6D4" stroke-width="1.2"/>
    <text x="1067" y="268" font-size="15" font-weight="700" fill="#E0F2FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">🏛️ Official Harmonized Data (Eurostat · OECD · IMF · World Bank)</text>

    <!-- Pill 3 -->
    <rect x="1420" y="248" width="650" height="28" rx="7" fill="#0F172A" stroke="#10B981" stroke-width="1.2"/>
    <text x="1745" y="268" font-size="15" font-weight="700" fill="#E0F2FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">⚖️ Dual Formulations: Annual Nowcast vs. Cold-Start Allocation</text>

    <!-- Pill 4 -->
    <rect x="2090" y="248" width="670" height="28" rx="7" fill="#0F172A" stroke="#F59E0B" stroke-width="1.2"/>
    <text x="2425" y="268" font-size="15" font-weight="700" fill="#E0F2FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">🔍 Exact Simplex (Σ=100%) &amp; Validated Explainability (SHAP &amp; LIME)</text>
  </g>
</g>
''')

# Helper to generate a structured card
def render_card(card_id, x, y, w, h, title, icon, subtitle=""):
    c = []
    c.append(f'<g id="{card_id}">')
    c.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{BG_CARD}" stroke="{BORDER_CARD}" stroke-width="1.5" filter="url(#cardShadow)"/>')
    header_h = 46 if not subtitle else 56
    c.append(f'<rect x="{x}" y="{y}" width="{w}" height="{header_h}" rx="14" fill="url(#cardHeaderGrad)"/>')
    c.append(f'<rect x="{x}" y="{y + header_h - 10}" width="{w}" height="10" fill="url(#cardHeaderGrad)"/>')
    c.append(f'<rect x="{x}" y="{y + header_h}" width="{w}" height="3" fill="url(#accentBar)"/>')
    c.append(f'<text x="{x + 22}" y="{y + 31}" font-size="22" font-weight="800" fill="#FFFFFF" font-family="\'Segoe UI\', Arial, sans-serif">{icon}  {escape_xml(title)}</text>')
    if subtitle:
        c.append(f'<text x="{x + 22}" y="{y + 49}" font-size="14" font-weight="600" fill="#93C5FD" font-family="\'Segoe UI\', Arial, sans-serif">{escape_xml(subtitle)}</text>')
    return "\n".join(c)

def close_card():
    return '</g>'

# =========================================================================
# COLUMN 1: LEFT (x: 45, width: 898) - FOUNDATIONS & DATA
# =========================================================================
col1_x = 45
col1_w = 898

# --- CARD 1A: Research Problem & Motivation in Public Management (y: 315 to 830, h: 515) ---
svg.append(render_card("card-1a", col1_x, 315, col1_w, 515, "1. RESEARCH PROBLEM & FISCAL MOTIVATION", "⚖️", "Public Financial Management, Medium-Term Budgeting & Explainable AI"))
svg.append(f'''
<g transform="translate({col1_x + 22}, 385)">
  <!-- Problem Statement Box -->
  <rect x="0" y="0" width="854" height="96" rx="9" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
  <rect x="0" y="0" width="6" height="96" rx="3" fill="#DC2626"/>
  <text x="18" y="24" font-size="16" font-weight="800" fill="#991B1B" font-family="'Segoe UI', Arial, sans-serif">REAL-WORLD CHALLENGE: INCREMENTAL INERTIA IN PUBLIC EXPENDITURE</text>
  <text x="18" y="47" font-size="15" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
    Sovereign governments allocate trillions in public revenue across competing socio-economic functions (health,
  </text>
  <text x="18" y="68" font-size="15" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
    education, social protection, economic infrastructure). In actual fiscal practice, budgeting is strictly <tspan font-weight="bold">incremental</tspan>:
  </text>
  <text x="18" y="88" font-size="15" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
    last year's split is carried forward with marginal adjustments, ignoring cross-country peer regularities and macro shifts.
  </text>

  <!-- The Two Core Research Questions -->
  <g transform="translate(0, 110)">
    <rect x="0" y="0" width="418" height="110" rx="9" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.2"/>
    <text x="15" y="24" font-size="15" font-weight="800" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">SETTING 1: ANNUAL UPDATE (NOWCAST)</text>
    <text x="15" y="47" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Baseline:</tspan> Last year's budget persistence (y<tspan font-size="10" dy="3">t-1</tspan><tspan font-size="14" dy="-3">)</tspan>
    </text>
    <text x="15" y="70" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Question:</tspan> How much can machine learning
    </text>
    <text x="15" y="90" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      genuinely add over inertia using same-year indicators?
    </text>

    <rect x="436" y="0" width="418" height="110" rx="9" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.2"/>
    <text x="451" y="24" font-size="15" font-weight="800" fill="#166534" font-family="'Segoe UI', Arial, sans-serif">SETTING 2: COLD START (UNSEEN PEERS)</text>
    <text x="451" y="47" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Baseline:</tspan> Income-group peer group mean
    </text>
    <text x="451" y="70" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Question:</tspan> What can comparable peer economies
    </text>
    <text x="451" y="90" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      and explanations tell an analyst when no history exists?
    </text>
  </g>

  <!-- PFM & Legal Governance Box -->
  <g transform="translate(0, 235)">
    <rect x="0" y="0" width="854" height="175" rx="9" fill="#FFFBEB" stroke="#FDE68A" stroke-width="1.2"/>
    <rect x="0" y="0" width="6" height="175" rx="3" fill="#D97706"/>
    <text x="18" y="25" font-size="16" font-weight="800" fill="#B45309" font-family="'Segoe UI', Arial, sans-serif">RELEVANCE TO COMMERCE, MANAGEMENT &amp; LEGAL GOVERNANCE</text>
    
    <text x="18" y="52" font-size="14.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Public Financial Management (PFM):</tspan> Empirically anchors Medium-Term Expenditure Frameworks (MTEF).
    </text>
    <text x="18" y="75" font-size="14.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Fiscal Governance &amp; Anti-Corruption:</tspan> Worldwide Governance Indicators (WGI: Government Effectiveness,
    </text>
    <text x="32" y="96" font-size="14.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      Regulatory Quality, Corruption Control) directly link administrative competence to public resource outturns.
    </text>
    <text x="18" y="121" font-size="14.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Legal Accountability &amp; AI Compliance:</tspan> Public sector AI demands explainability, strict conservation laws
    </text>
    <text x="32" y="142" font-size="14.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      (sum = 100%), and human-in-the-loop oversight to satisfy non-arbitrariness and emerging AI governance statutes.
    </text>
    <text x="18" y="165" font-size="14.5" font-weight="700" fill="#0369A1" font-family="'Segoe UI', Arial, sans-serif">
      Decision Philosophy: "The tool provides an advisory reference point; it never replaces accountable human judgment."
    </text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 1B: Research Objectives (y: 845 to 1320, h: 475) ---
svg.append(render_card("card-1b", col1_x, 845, col1_w, 475, "2. RESEARCH OBJECTIVES", "🎯", "Concrete, Measurable & Domain-Aligned Goals"))
svg.append(f'''
<g transform="translate({col1_x + 22}, 915)">
  <!-- Objective 1 -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="78" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <circle cx="32" cy="39" r="18" fill="#0284C7"/>
    <text x="32" y="45" font-size="16" font-weight="bold" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">O1</text>
    <text x="62" y="26" font-size="15" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Curate an Open, Provenance-Flagged Multi-Country Benchmark Dataset</text>
    <text x="62" y="47" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Harmonize general-government expenditure shares across 217 economies from Eurostat, OECD, IMF GFS, and</text>
    <text x="62" y="66" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">World Bank (2000–2024). Enforce strict zero-imputation policy on all target columns with full provenance tags.</text>
  </g>

  <!-- Objective 2 -->
  <g transform="translate(0, 88)">
    <rect x="0" y="0" width="854" height="78" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <circle cx="32" cy="39" r="18" fill="#0D9488"/>
    <text x="32" y="45" font-size="16" font-weight="bold" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">O2</text>
    <text x="62" y="26" font-size="15" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Establish Methodologically Honest Compositional Benchmark Protocols</text>
    <text x="62" y="47" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Evaluate realistic practitioner baselines (persistence, peer group mean) across temporal, leave-country-out,</text>
    <text x="62" y="66" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">and leave-region-out splits using Total-Variation Distance (TVD), cluster bootstrap, and Holm correction.</text>
  </g>

  <!-- Objective 3 -->
  <g transform="translate(0, 176)">
    <rect x="0" y="0" width="854" height="78" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <circle cx="32" cy="39" r="18" fill="#D97706"/>
    <text x="32" y="45" font-size="16" font-weight="bold" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">O3</text>
    <text x="62" y="26" font-size="15" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Develop Constrained Simplex Allocation Models with Conformal Uncertainty</text>
    <text x="62" y="47" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Implement GBDT ensembles (XGBoost, CatBoost, LightGBM) and NNLS stacking with exact bisection projection</text>
    <text x="62" y="66" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">guaranteeing budget closure (Σ=100%) and split-conformal 80% error intervals with applicability filtering.</text>
  </g>

  <!-- Objective 4 -->
  <g transform="translate(0, 264)">
    <rect x="0" y="0" width="854" height="78" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <circle cx="32" cy="39" r="18" fill="#7C3AED"/>
    <text x="32" y="45" font-size="16" font-weight="bold" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">O4</text>
    <text x="62" y="26" font-size="15" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Validate Explainable AI (XAI) &amp; Deploy Decision-Support Application</text>
    <text x="62" y="47" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Statistically test SHAP and LIME agreement, feature deletion faithfulness, and stability. Deliver an interactive</text>
    <text x="62" y="66" font-size="13.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">decision-support platform providing Sankey budget flows, peer benchmarking, stress testing, and UN SDG mapping.</text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 1C: Multi-Country Official Dataset (y: 1335 to 2075, h: 740) ---
svg.append(render_card("card-1c", col1_x, 1335, col1_w, 740, "3. OFFICIAL MULTI-COUNTRY DATASET: GovAlloc-COFOG v1.0", "📊", "Harmonized General-Government Expenditure by Function across 217 Economies"))
svg.append(f'''
<g transform="translate({col1_x + 22}, 1400)">
  <!-- 4 Dataset Statistics Cards -->
  <g transform="translate(0, 0)">
    <!-- Stat 1 -->
    <rect x="0" y="0" width="204" height="80" rx="8" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.2"/>
    <text x="102" y="26" font-size="13" font-weight="700" fill="#1E40AF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">PANEL A16 (DETAILED)</text>
    <text x="102" y="52" font-size="24" font-weight="800" fill="#0F172A" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">825 Rows</text>
    <text x="102" y="70" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">36 Economies · 16 COFOG</text>

    <!-- Stat 2 -->
    <rect x="216" y="0" width="204" height="80" rx="8" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.2"/>
    <text x="318" y="26" font-size="13" font-weight="700" fill="#166534" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">PANEL A10 (WIDE)</text>
    <text x="318" y="52" font-size="24" font-weight="800" fill="#0F172A" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">1,526 Rows</text>
    <text x="318" y="70" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">85 Economies · 10 Divisions</text>

    <!-- Stat 3 -->
    <rect x="432" y="0" width="204" height="80" rx="8" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1.2"/>
    <text x="534" y="26" font-size="13" font-weight="700" fill="#B45309" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">PANEL B (GLOBAL)</text>
    <text x="534" y="52" font-size="24" font-weight="800" fill="#0F172A" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">4,995 Rows</text>
    <text x="534" y="70" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">211 Economies · 4 Sectors</text>

    <!-- Stat 4 -->
    <rect x="648" y="0" width="206" height="80" rx="8" fill="#F5F3FF" stroke="#DDD6FE" stroke-width="1.2"/>
    <text x="751" y="26" font-size="13" font-weight="700" fill="#6D28D9" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">MASTER REPOSITORY</text>
    <text x="751" y="52" font-size="24" font-weight="800" fill="#0F172A" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">5,450 Rows</text>
    <text x="751" y="70" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">217 Columns · 2000–2024</text>
  </g>

  <!-- Data Coverage Figure -->
  <g transform="translate(0, 90)">
    <rect x="0" y="0" width="854" height="390" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
    <image x="10" y="6" width="834" height="378" xlink:href="data:image/png;base64,{b64_cov}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Strict Data Quality & Provenance Banner -->
  <g transform="translate(0, 490)">
    <rect x="0" y="0" width="854" height="135" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>
    <text x="16" y="24" font-size="15" font-weight="800" fill="#1E293B" font-family="'Segoe UI', Arial, sans-serif">RIGOROUS DATA QUALITY POLICY &amp; PROVENANCE CONTROLS</text>
    <text x="16" y="48" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Executed Outturns, Not Proposals:</tspan> Reflects actual audited government expenditures, eliminating political proposal noise.
    </text>
    <text x="16" y="70" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Zero Imputation on Targets:</tspan> Target expenditure shares are published official figures and are <tspan font-weight="bold" fill="#DC2626">NEVER imputed</tspan>.
    </text>
    <text x="16" y="92" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Transductive Feature Flags:</tspan> 25 macro-fiscal indicators; ≤3-yr bounded interpolation with explicit per-cell flags (imp_*).
    </text>
    <text x="16" y="114" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Cross-Source Validation:</tspan> Eurostat vs. OECD cross-checked on 690 overlapping rows; median discrepancy = 0.025 pp.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 1D: Forensic Audit of Legacy Benchmark (y: 2090 to 2795, h: 705) ---
svg.append(render_card("card-1d", col1_x, 2090, col1_w, 705, "4. FORENSIC AUDIT OF LEGACY BENCHMARK (RESEARCH INTEGRITY)", "🔍", "Why Earlier R² > 0.99 Claims Were Artefacts of Synthetic Target Leakage"))
svg.append(f'''
<g transform="translate({col1_x + 22}, 2155)">
  <!-- Audit Explanation Box -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="85" rx="8" fill="#FEF2F2" stroke="#FECACA" stroke-width="1.2"/>
    <rect x="0" y="0" width="6" height="85" rx="3" fill="#DC2626"/>
    <text x="18" y="24" font-size="15.5" font-weight="800" fill="#991B1B" font-family="'Segoe UI', Arial, sans-serif">DISCOVERY OF TARGET LEAKAGE &amp; EXACT FIXED MULTIPLES IN LEGACY BENCHMARK</text>
    <text x="18" y="47" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      A forensic re-audit revealed that the legacy v1 dataset's headline score (R² &gt; 0.99, "95.29% accuracy") was completely
    </text>
    <text x="18" y="67" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      artificial: <tspan font-weight="bold" fill="#DC2626">11 of 15 sector targets were exact fixed linear multiples of one latent series</tspan> (CV = 2.8%, k × GDP).
    </text>
  </g>

  <!-- Legacy Audit Figure -->
  <g transform="translate(0, 92)">
    <rect x="0" y="0" width="854" height="340" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
    <image x="10" y="6" width="834" height="328" xlink:href="data:image/png;base64,{b64_audit}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Scientific Integrity Lesson -->
  <g transform="translate(0, 440)">
    <rect x="0" y="0" width="854" height="150" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <text x="18" y="25" font-size="15" font-weight="800" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">SCIENTIFIC LESSON &amp; COMPLETE BENCHMARK REBUILD</text>
    <text x="18" y="50" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Artifact Disproven:</tspan> A single-parameter formula (k × GDP) scored R² = 0.9997 vs. 0.9991 for XGBoost on those sectors.
    </text>
    <text x="18" y="72" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Methodological Flaw Fixed:</tspan> The legacy code ran a random train/test split, leaking neighbouring years of identical countries.
    </text>
    <text x="18" y="94" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Commitment to Truth:</tspan> Rather than hiding the audit, we preserved the old dataset as a negative control and rebuilt
    </text>
    <text x="32" y="115" font-size="14" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      the entire benchmark exclusively on genuine multi-country official statistics (GovAlloc-COFOG v1.0).
    </text>
    <text x="18" y="136" font-size="13.5" font-weight="700" fill="#0D9488" font-family="'Segoe UI', Arial, sans-serif">
      Outcome: Replaced inflated synthetic metrics with transparent, verifiable scientific evidence suitable for academic peer review.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# =========================================================================
# COLUMN 2: CENTER (x: 968, width: 898) - METHODOLOGY & ARCHITECTURE
# =========================================================================
col2_x = 968
col2_w = 898

# --- CARD 2A: Proposed Research Methodology (y: 315 to 945, h: 630) ---
svg.append(render_card("card-2a", col2_x, 315, col2_w, 630, "5. PROPOSED RESEARCH METHODOLOGY & PIPELINE", "⚙️", "End-to-End Pipeline: Ingestion → Dual Modeling → Simplex Projection → XAI"))
svg.append(f'''
<g transform="translate({col2_x + 22}, 385)">
  <!-- Stage 1 -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="62" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <rect x="0" y="0" width="130" height="62" rx="8" fill="#1E3A8A"/>
    <text x="65" y="26" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">STAGE 1</text>
    <text x="65" y="46" font-size="11" font-weight="600" fill="#93C5FD" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">DATA INGESTION</text>
    <text x="145" y="26" font-size="14" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Automated Harmonization of Official Multi-Country Statistical Sources</text>
    <text x="145" y="47" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Extract Eurostat COFOG, OECD Table 11, IMF GFS, and World Bank WDI/WGI.</text>
  </g>

  <!-- Arrow Down -->
  <text x="427" y="74" font-size="14" fill="#0284C7" text-anchor="middle">▼</text>

  <!-- Stage 2 -->
  <g transform="translate(0, 80)">
    <rect x="0" y="0" width="854" height="62" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <rect x="0" y="0" width="130" height="62" rx="8" fill="#0D9488"/>
    <text x="65" y="26" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">STAGE 2</text>
    <text x="65" y="46" font-size="11" font-weight="600" fill="#CCFBF1" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">PREPROCESSING</text>
    <text x="145" y="26" font-size="14" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Leakage Prevention, Compositional Scaling &amp; Provenance Flagging</text>
    <text x="145" y="47" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">25 macro features (≤3-yr interpolation flagged). Centered log-ratio (CLR) &amp; simplex shares (% of budget).</text>
  </g>

  <!-- Arrow Down -->
  <text x="427" y="154" font-size="14" fill="#0284C7" text-anchor="middle">▼</text>

  <!-- Stage 3: Dual-Regime Formulation -->
  <g transform="translate(0, 160)">
    <rect x="0" y="0" width="854" height="104" rx="8" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.2"/>
    <rect x="0" y="0" width="130" height="104" rx="8" fill="#0284C7"/>
    <text x="65" y="42" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">STAGE 3</text>
    <text x="65" y="60" font-size="11" font-weight="600" fill="#E0F2FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">DUAL-REGIME</text>
    <text x="65" y="76" font-size="11" font-weight="600" fill="#E0F2FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">MODELING</text>
    
    <text x="145" y="26" font-size="14.5" font-weight="800" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">Mode 1: Annual Update (Δ-Learner Nowcasting)</text>
    <text x="145" y="46" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">ŷ<tspan font-size="9" dy="2">t</tspan><tspan font-size="13" dy="-2"> = y</tspan><tspan font-size="9" dy="2">t-1</tspan><tspan font-size="13" dy="-2"> + f(x</tspan><tspan font-size="9" dy="2">t</tspan><tspan font-size="13" dy="-2">, y</tspan><tspan font-size="9" dy="2">t-1</tspan><tspan font-size="13" dy="-2">) → Baseline: Persistence (y</tspan><tspan font-size="9" dy="2">t-1</tspan><tspan font-size="13" dy="-2">). Tests incremental budget drift.</tspan></text>
    
    <text x="145" y="71" font-size="14.5" font-weight="800" fill="#15803D" font-family="'Segoe UI', Arial, sans-serif">Mode 2: Cold-Start (NNLS Stacking &amp; k-NN Peer Aggregation)</text>
    <text x="145" y="91" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">ŷ<tspan font-size="9" dy="2">t</tspan><tspan font-size="13" dy="-2"> = f(x</tspan><tspan font-size="9" dy="2">t</tspan><tspan font-size="13" dy="-2">) without historical allocations. Stacks XGBoost, CatBoost, Ridge &amp; k-NN (k=8).</tspan></text>
  </g>

  <!-- Arrow Down -->
  <text x="427" y="276" font-size="14" fill="#0284C7" text-anchor="middle">▼</text>

  <!-- Stage 4 -->
  <g transform="translate(0, 282)">
    <rect x="0" y="0" width="854" height="62" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <rect x="0" y="0" width="130" height="62" rx="8" fill="#D97706"/>
    <text x="65" y="26" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">STAGE 4</text>
    <text x="65" y="46" font-size="11" font-weight="600" fill="#FEF3C7" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">ALLOCATION</text>
    <text x="145" y="26" font-size="14" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Exact Bounded-Simplex Projection (Bisection Algorithm)</text>
    <text x="145" y="47" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Solve min ||a - ŷ||² s.t. Σ a_i = 100% and l ≤ a ≤ u. Exact machine precision match with SLSQP (3.6e-15).</text>
  </g>

  <!-- Arrow Down -->
  <text x="427" y="356" font-size="14" fill="#0284C7" text-anchor="middle">▼</text>

  <!-- Stage 5 -->
  <g transform="translate(0, 362)">
    <rect x="0" y="0" width="854" height="62" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <rect x="0" y="0" width="130" height="62" rx="8" fill="#7C3AED"/>
    <text x="65" y="26" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">STAGE 5</text>
    <text x="65" y="46" font-size="11" font-weight="600" fill="#DDD6FE" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">UNCERTAINTY</text>
    <text x="145" y="26" font-size="14" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Split-Conformal Prediction Bounds &amp; Novelty/Applicability Score</text>
    <text x="145" y="47" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Empirical 80% coverage intervals; Mahalanobis applicability score flags atypical, high-risk economies.</text>
  </g>

  <!-- Arrow Down -->
  <text x="427" y="436" font-size="14" fill="#0284C7" text-anchor="middle">▼</text>

  <!-- Stage 6 -->
  <g transform="translate(0, 442)">
    <rect x="0" y="0" width="854" height="62" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <rect x="0" y="0" width="130" height="62" rx="8" fill="#059669"/>
    <text x="65" y="26" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">STAGE 6</text>
    <text x="65" y="46" font-size="11" font-weight="600" fill="#A7F3D0" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">EXPLAINABILITY</text>
    <text x="145" y="26" font-size="14" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Quantitative XAI Validation (SHAP &amp; LIME Agreement + Deletion Faithfulness)</text>
    <text x="145" y="47" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Evaluate sign consensus, feature rankings, and synthetic ground truth to audit interpretability claims.</text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 2B: System Architecture & Allocation Engine (y: 965 to 1715, h: 750) ---
svg.append(render_card("card-2b", col2_x, 965, col2_w, 750, "6. SYSTEM ARCHITECTURE & ALLOCATION ENGINE", "🏛️", "Technical Blueprint: Data Layer → Allocation Engine → Human Oversight"))
svg.append(f'''
<g transform="translate({col2_x + 22}, 1030)">
  <!-- Architecture Diagram Image -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="380" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
    <image x="10" y="6" width="834" height="368" xlink:href="data:image/png;base64,{b64_arch}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Mathematical & Algorithmic Highlights -->
  <g transform="translate(0, 395)">
    <!-- Box 1: Bounded Simplex Projection -->
    <rect x="0" y="0" width="418" height="140" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>
    <text x="16" y="24" font-size="14.5" font-weight="800" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">EXACT BOUNDED SIMPLEX PROJECTION</text>
    <text x="16" y="46" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Objective:</tspan> a* = argmin ½ ||a - ŷ||²
    </text>
    <text x="16" y="66" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Constraints:</tspan> 1ᵀa = 100% and l ≤ a ≤ u
    </text>
    <text x="16" y="86" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">
      • Solved via continuous piecewise bisection.
    </text>
    <text x="16" y="106" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">
      • Matches SLSQP solver to 3.6 × 10⁻¹⁵ pp.
    </text>
    <text x="16" y="124" font-size="13" font-weight="700" fill="#15803D" font-family="'Segoe UI', Arial, sans-serif">
      Result: Zero fiscal budget leak; sums strictly to 100%.
    </text>

    <!-- Box 2: NNLS Stacking & k-NN Peers -->
    <rect x="436" y="0" width="418" height="140" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>
    <text x="452" y="24" font-size="14.5" font-weight="800" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">NNLS STACKING &amp; k-NN PEER BENCHMARK</text>
    <text x="452" y="46" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      <tspan font-weight="bold">Stacked Ensemble:</tspan> Non-negative least squares
    </text>
    <text x="452" y="66" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      weights (w_i ≥ 0, Σ w_i = 1) fitted via nested CV.
    </text>
    <text x="452" y="86" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">
      • Blends linear ridge stability with GBDT flexibility.
    </text>
    <text x="452" y="106" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">
      • 8-Nearest Peers: Inverse-distance weighted average.
    </text>
    <text x="452" y="124" font-size="13" font-weight="700" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">
      Advantage: Intuitive, transparent peer comparisons.
    </text>
  </g>

  <!-- Human-in-the-Loop Governance Bar -->
  <g transform="translate(0, 545)">
    <rect x="0" y="0" width="854" height="80" rx="8" fill="#F0FDF4" stroke="#86EFAC" stroke-width="1.2"/>
    <text x="18" y="24" font-size="15" font-weight="800" fill="#166534" font-family="'Segoe UI', Arial, sans-serif">HUMAN-IN-THE-LOOP GOVERNANCE &amp; POLICY INTERFACE</text>
    <text x="18" y="46" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      The system does not mandate budget figures. It operates as an analyst co-pilot: (1) Baseline Reference Split,
    </text>
    <text x="18" y="66" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      (2) Uncertainty Intervals, (3) Model Applicability Warning, (4) Top Macro Factor Explanations, (5) Human Approval.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 2C: Comprehensive Algorithmic Comparison (y: 1735 to 2795, h: 1060) ---
svg.append(render_card("card-2c", col2_x, 1735, col2_w, 1060, "7. COMPREHENSIVE ALGORITHMIC COMPARISON", "📈", "Total-Variation Distance (TVD) Benchmark Across Learners & Protocols"))
svg.append(f'''
<g transform="translate({col2_x + 22}, 1800)">
  <!-- Main Comparative Chart Figure -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="430" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
    <image x="10" y="8" width="834" height="414" xlink:href="data:image/png;base64,{b64_res}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Verified Benchmark Comparison Table -->
  <g transform="translate(0, 445)">
    <rect x="0" y="0" width="854" height="355" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>
    
    <!-- Table Header -->
    <rect x="0" y="0" width="854" height="38" rx="8" fill="#0F264A"/>
    <rect x="0" y="28" width="854" height="10" fill="#0F264A"/>
    <text x="15" y="24" font-size="13.5" font-weight="700" fill="#FFFFFF" font-family="'Segoe UI', Arial, sans-serif">EVALUATED MODEL / METHOD</text>
    <text x="350" y="24" font-size="13.5" font-weight="700" fill="#FFFFFF" font-family="'Segoe UI', Arial, sans-serif">PROTOCOL</text>
    <text x="500" y="24" font-size="13.5" font-weight="700" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">TVD (pp) [95% CI]</text>
    <text x="690" y="24" font-size="13.5" font-weight="700" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">GAIN vs. BASELINE</text>
    <text x="815" y="24" font-size="13.5" font-weight="700" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">HOLM p</text>

    <!-- Table Rows -->
    <!-- Row 1: Persistence -->
    <g transform="translate(0, 38)">
      <rect x="0" y="0" width="854" height="34" fill="#FFFFFF"/>
      <text x="15" y="22" font-size="13.5" font-weight="700" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">Persistence Baseline (Last Year)</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Annual Update (A16)</text>
      <text x="500" y="22" font-size="13.5" font-weight="700" fill="{TEXT_DARK}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">3.62 [3.17, 4.08]</text>
      <text x="690" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">— [Null Baseline]</text>
      <text x="815" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">—</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 2: Learned Hybrid -->
    <g transform="translate(0, 72)">
      <rect x="0" y="0" width="854" height="34" fill="#F8FAFC"/>
      <text x="15" y="22" font-size="13.5" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">Learned Δ-Hybrid (XGB + Cat)</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Annual Update (A16)</text>
      <text x="500" y="22" font-size="13.5" font-weight="700" fill="#0284C7" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">3.48 [3.06, 3.91]</text>
      <text x="690" y="22" font-size="13" font-weight="700" fill="#15803D" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">+0.140 pp (mean: 0.12)</text>
      <text x="815" y="22" font-size="13" fill="#D97706" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">1/5 seeds</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 3: Country Mean -->
    <g transform="translate(0, 106)">
      <rect x="0" y="0" width="854" height="34" fill="#FFFFFF"/>
      <text x="15" y="22" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">Country Historical Mean</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Annual Update (A16)</text>
      <text x="500" y="22" font-size="13.5" fill="{TEXT_DARK}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">6.96 [6.12, 7.84]</text>
      <text x="690" y="22" font-size="13" fill="#DC2626" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">-3.34 pp (worse)</text>
      <text x="815" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">&lt; 0.001</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#CBD5E1" stroke-width="1.5"/>
    </g>

    <!-- Row 4: Peer Mean Cold Start -->
    <g transform="translate(0, 140)">
      <rect x="0" y="0" width="854" height="34" fill="#EFF6FF"/>
      <text x="15" y="22" font-size="13.5" font-weight="700" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">Income-Group Peer Mean Baseline</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Cold Start (A10, 85 Econ)</text>
      <text x="500" y="22" font-size="13.5" font-weight="700" fill="{TEXT_DARK}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">15.01 [13.50, 16.55]</text>
      <text x="690" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">— [Null Baseline]</text>
      <text x="815" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">—</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 5: NNLS Stacking Cold Start -->
    <g transform="translate(0, 174)">
      <rect x="0" y="0" width="854" height="34" fill="#F0FDF4"/>
      <text x="15" y="22" font-size="13.5" font-weight="800" fill="#166534" font-family="'Segoe UI', Arial, sans-serif">NNLS Stacking (Proposed)</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Cold Start (A10, 85 Econ)</text>
      <text x="500" y="22" font-size="13.5" font-weight="800" fill="#166534" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">13.77 [12.30, 15.45]</text>
      <text x="690" y="22" font-size="13" font-weight="800" fill="#166534" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">+1.26 pp [0.68, 1.84]</text>
      <text x="815" y="22" font-size="13" font-weight="800" fill="#166534" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">p = 0.0008 ★</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 6: 8-Nearest Peers -->
    <g transform="translate(0, 208)">
      <rect x="0" y="0" width="854" height="34" fill="#FFFFFF"/>
      <text x="15" y="22" font-size="13.5" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">8-Nearest Economies Average (k-NN)</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Cold Start (A10, 85 Econ)</text>
      <text x="500" y="22" font-size="13.5" font-weight="700" fill="{TEXT_DARK}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">13.74 [12.28, 15.40]</text>
      <text x="690" y="22" font-size="13" font-weight="700" fill="#15803D" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">+1.25 pp [0.71, 1.78]</text>
      <text x="815" y="22" font-size="13" font-weight="700" fill="#15803D" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">p = 0.0008 ★</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 7: XGBoost -->
    <g transform="translate(0, 242)">
      <rect x="0" y="0" width="854" height="34" fill="#F8FAFC"/>
      <text x="15" y="22" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">XGBoost (Raw Covariates)</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Cold Start (A10, 85 Econ)</text>
      <text x="500" y="22" font-size="13.5" fill="{TEXT_DARK}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">14.12 [12.55, 15.80]</text>
      <text x="690" y="22" font-size="13" fill="#15803D" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">+0.89 pp [0.19, 1.58]</text>
      <text x="815" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">p = 0.060</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 8: Ridge Reference -->
    <g transform="translate(0, 276)">
      <rect x="0" y="0" width="854" height="34" fill="#FFFFFF"/>
      <text x="15" y="22" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">Ridge Regression (Linear Reference)</text>
      <text x="350" y="22" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Cold Start (A10, 85 Econ)</text>
      <text x="500" y="22" font-size="13.5" fill="{TEXT_DARK}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">14.35 [12.78, 16.02]</text>
      <text x="690" y="22" font-size="13" fill="#15803D" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">+0.66 pp [0.05, 1.30]</text>
      <text x="815" y="22" font-size="13" fill="{TEXT_LIGHT}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">p = 0.082</text>
      <line x1="0" y1="34" x2="854" y2="34" stroke="#E2E8F0" stroke-width="1"/>
    </g>

    <!-- Row 9: Panel A16 Note -->
    <g transform="translate(0, 310)">
      <rect x="0" y="0" width="854" height="42" fill="#FEF3C7"/>
      <text x="15" y="26" font-size="13" font-weight="700" fill="#92400E" font-family="'Segoe UI', Arial, sans-serif">
        Panel A16 (36 Economies): Stack TVD = 10.53 pp vs. Peer = 11.34 pp (gain 0.81 pp does NOT survive Holm correction, p = 0.060).
      </text>
    </g>
  </g>

  <!-- Scientific Takeaway Callout -->
  <g transform="translate(0, 815)">
    <rect x="0" y="0" width="854" height="70" rx="8" fill="#EFF6FF" stroke="#93C5FD" stroke-width="1.2"/>
    <text x="18" y="25" font-size="14.5" font-weight="800" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">CRITICAL SCIENTIFIC TAKEAWAY FOR PUBLIC MANAGEMENT</text>
    <text x="18" y="48" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      ML cannot easily beat persistence where history exists; its true power is in <tspan font-weight="bold">Cold-Start peer benchmarking</tspan>
    </text>
    <text x="645" y="48" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      (p = 0.0008) for data-scarce nations.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# =========================================================================
# COLUMN 3: RIGHT (x: 1891, width: 898) - RESULTS, XAI, APP & POLICY
# =========================================================================
col3_x = 1891
col3_w = 898

# --- CARD 3A: Key Empirical Findings & Numerical Evidence (y: 315 to 985, h: 670) ---
svg.append(render_card("card-3a", col3_x, 315, col3_w, 670, "8. KEY EMPIRICAL FINDINGS & NUMERICAL EVIDENCE", "📊", "Traceable, Verified Statistics with 95% Bootstrap Confidence Intervals"))
svg.append(f'''
<g transform="translate({col3_x + 22}, 385)">
  <!-- 4 Verified Numerical Highlight Cards -->
  <g transform="translate(0, 0)">
    <!-- Metric 1 -->
    <rect x="0" y="0" width="418" height="88" rx="8" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.2"/>
    <text x="16" y="22" font-size="12.5" font-weight="700" fill="#166534" font-family="'Segoe UI', Arial, sans-serif">COLD START GAIN (PANEL A10)</text>
    <text x="16" y="50" font-size="26" font-weight="800" fill="#15803D" font-family="'Segoe UI', Arial, sans-serif">+1.26 pp (p = 0.0008)</text>
    <text x="16" y="70" font-size="11.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">NNLS Stack TVD 13.77 vs 15.01 pp [0.68, 1.84] (Holm-corrected)</text>

    <!-- Metric 2 -->
    <rect x="436" y="0" width="418" height="88" rx="8" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.2"/>
    <text x="452" y="22" font-size="12.5" font-weight="700" fill="#1E40AF" font-family="'Segoe UI', Arial, sans-serif">ANNUAL CORRECTION GAIN</text>
    <text x="452" y="50" font-size="26" font-weight="800" fill="#0284C7" font-family="'Segoe UI', Arial, sans-serif">0.140 pp (mean: 0.12)</text>
    <text x="452" y="70" font-size="11.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Δ-Hybrid TVD 3.48 vs 3.62 pp (significant in only 1 of 5 seeds)</text>
  </g>

  <!-- Metric 3 & 4 -->
  <g transform="translate(0, 98)">
    <!-- Metric 3 -->
    <rect x="0" y="0" width="418" height="88" rx="8" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1.2"/>
    <text x="16" y="22" font-size="12.5" font-weight="700" fill="#B45309" font-family="'Segoe UI', Arial, sans-serif">HEALTH &amp; R&amp;D PREDICTABILITY</text>
    <text x="16" y="50" font-size="26" font-weight="800" fill="#B45309" font-family="'Segoe UI', Arial, sans-serif">R² = 0.63 &amp; 0.60</text>
    <text x="16" y="70" font-size="11.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">Unseen economies (Panel B) vs. Peer Mean 0.31 &amp; 0.25</text>

    <!-- Metric 4 -->
    <rect x="436" y="0" width="418" height="88" rx="8" fill="#FEF2F2" stroke="#FECACA" stroke-width="1.2"/>
    <text x="452" y="22" font-size="12.5" font-weight="700" fill="#991B1B" font-family="'Segoe UI', Arial, sans-serif">GLOBAL EQUITY ERROR GAP</text>
    <text x="452" y="50" font-size="26" font-weight="800" fill="#DC2626" font-family="'Segoe UI', Arial, sans-serif">11.4 pp vs. 33.4 pp</text>
    <text x="452" y="70" font-size="11.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">High-Income vs Low-Income cold-start error (data scarcity)</text>
  </g>

  <!-- WDI Sector Predictability Figure -->
  <g transform="translate(0, 196)">
    <rect x="0" y="0" width="854" height="310" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
    <image x="10" y="6" width="834" height="298" xlink:href="data:image/png;base64,{b64_wdi}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Summary Line -->
  <g transform="translate(0, 516)">
    <rect x="0" y="0" width="854" height="54" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <text x="18" y="22" font-size="13.5" font-weight="700" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">
      Socio-Demographic Spending is Highly Systematic; Geopolitical Spending Resists Macro Modeling.
    </text>
    <text x="18" y="42" font-size="12.5" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">
      Health, Education, and R&amp;D follow structural demographic paths, whereas Defence reflects independent security doctrine.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 3B: Explainable AI (XAI) Quantitative Validation (y: 1005 to 1585, h: 580) ---
svg.append(render_card("card-3b", col3_x, 1005, col3_w, 580, "9. EXPLAINABLE AI (XAI) QUANTITATIVE VALIDATION", "🔍", "Testing Explanations Statistically: Agreement, Stability & Faithfulness"))
svg.append(f'''
<g transform="translate({col3_x + 22}, 1070)">
  <!-- 3 XAI Metric Badges -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="270" height="74" rx="8" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.2"/>
    <text x="135" y="24" font-size="12" font-weight="700" fill="#1E40AF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">DIRECTIONAL SIGN AGREEMENT</text>
    <text x="135" y="52" font-size="24" font-weight="800" fill="#0284C7" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">85.0%</text>
    <text x="135" y="67" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">SHAP &amp; LIME agree on direction</text>

    <rect x="292" y="0" width="270" height="74" rx="8" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.2"/>
    <text x="427" y="24" font-size="12" font-weight="700" fill="#166534" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">RANKING CORRELATION</text>
    <text x="427" y="52" font-size="24" font-weight="800" fill="#15803D" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">ρ = 0.59 (J = 0.48)</text>
    <text x="427" y="67" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">Spearman ρ &amp; Top-5 Jaccard</text>

    <rect x="584" y="0" width="270" height="74" rx="8" fill="#FEF3C7" stroke="#FDE68A" stroke-width="1.2"/>
    <text x="719" y="24" font-size="12" font-weight="700" fill="#B45309" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">DELETION FAITHFULNESS</text>
    <text x="719" y="52" font-size="24" font-weight="800" fill="#B45309" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">3.1× Impact</text>
    <text x="719" y="67" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">vs. random feature perturbation</text>
  </g>

  <!-- SHAP vs. LIME Figure -->
  <g transform="translate(0, 84)">
    <rect x="0" y="0" width="854" height="280" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>
    <image x="10" y="6" width="834" height="268" xlink:href="data:image/png;base64,{b64_xai}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- XAI Scientific Summary -->
  <g transform="translate(0, 374)">
    <rect x="0" y="0" width="854" height="110" rx="8" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.2"/>
    <text x="16" y="24" font-size="14.5" font-weight="800" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">EMPIRICAL LESSON: EXPLANATIONS AGREE ON DIRECTION, NOT RANKING</text>
    <text x="16" y="46" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">High Qualitative Consensus:</tspan> 85% sign agreement demonstrates that TreeSHAP and LIME identify the same macroeconomic
    </text>
    <text x="30" y="66" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      drivers as increasing or decreasing public allocations (e.g. GDP per capita, Population 65+, Governance Effectiveness).
    </text>
    <text x="16" y="87" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Cautionary Guardrail:</tspan> Feature ranking disagreement (ρ = 0.59) proves that analysts must not over-interpret precise decimal
    </text>
    <text x="30" y="104" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      attributions. Explanations reflect empirical macro associations, not causal policy levers.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 3C: Interactive Decision-Support Web Application (y: 1605 to 2225, h: 620) ---
svg.append(render_card("card-3c", col3_x, 1605, col3_w, 620, "10. INTERACTIVE DECISION-SUPPORT APPLICATION", "💻", "Operational Implementation: React 18 · FastAPI · Budget Explorer · What-If Engine"))
svg.append(f'''
<g transform="translate({col3_x + 22}, 1670)">
  <!-- Dashboard UI Screenshot (Fully Anonymous) -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="380" rx="8" fill="#0F172A" stroke="#334155" stroke-width="1.5"/>
    <image x="4" y="4" width="846" height="372" xlink:href="data:image/png;base64,{b64_dash}" preserveAspectRatio="xMidYMid slice"/>
  </g>

  <!-- Application Capabilities Grid -->
  <g transform="translate(0, 392)">
    <rect x="0" y="0" width="854" height="130" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <text x="16" y="24" font-size="14.5" font-weight="800" fill="#0F172A" font-family="'Segoe UI', Arial, sans-serif">CORE OPERATIONAL CAPABILITIES FOR FISCAL BUDGET ANALYSTS</text>
    <text x="16" y="48" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Interactive Budget Flow (Sankey):</tspan> Maps total national fiscal envelope → 16 COFOG functional shares → UN SDGs.
    </text>
    <text x="16" y="70" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Peer Benchmarking:</tspan> Instant visual comparisons against the 8 most similar socio-economic peer economies.
    </text>
    <text x="16" y="92" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Macroeconomic What-If Stress-Testing:</tspan> Real-time sensitivity simulation (recession, stagflation, debt shocks).
    </text>
    <text x="16" y="114" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Conformal Uncertainty &amp; Applicability Guardrail:</tspan> Displays 80% error bars and warns if an economy is out-of-distribution.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# --- CARD 3D: Policy Relevance, Limitations & Future Scope (y: 2245 to 2795, h: 550) ---
svg.append(render_card("card-3d", col3_x, 2245, col3_w, 550, "11. POLICY RELEVANCE, LIMITATIONS & FUTURE SCOPE", "⚖️", "Commerce, Management & Law Alignment · Ethical Governance · Future Roadmap"))
svg.append(f'''
<g transform="translate({col3_x + 22}, 2310)">
  <!-- Commerce & Law Alignment Box -->
  <g transform="translate(0, 0)">
    <rect x="0" y="0" width="854" height="150" rx="8" fill="#FFFBEB" stroke="#FDE68A" stroke-width="1.2"/>
    <text x="16" y="24" font-size="15" font-weight="800" fill="#B45309" font-family="'Segoe UI', Arial, sans-serif">ALIGNMENT WITH COMMERCE, MANAGEMENT &amp; LEGAL FRAMEWORKS</text>
    <text x="16" y="48" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Administrative Law &amp; Non-Arbitrariness:</tspan> Public finance laws require that allocation decisions be reasoned, documented,
    </text>
    <text x="30" y="68" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      and traceable. Our XAI layer and exact simplex constraints ensure computational reproducibility without black-box drift.
    </text>
    <text x="16" y="90" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Public Sector Management (PFM):</tspan> Medium-term fiscal projections gain an objective peer reference baseline, reducing
    </text>
    <text x="30" y="110" font-size="13.5" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      subjective ministerial bargaining and political allocation distortions during fiscal crises.
    </text>
    <text x="16" y="132" font-size="13" font-weight="700" fill="#B45309" font-family="'Segoe UI', Arial, sans-serif">
      High-Risk AI Governance: Adheres to emerging public administration standards (conformal bounds, error bounds, human veto).
    </text>
  </g>

  <!-- Limitations & Future Work Grid -->
  <g transform="translate(0, 160)">
    <!-- Limitations -->
    <rect x="0" y="0" width="418" height="175" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.2"/>
    <text x="16" y="24" font-size="14.5" font-weight="800" fill="#991B1B" font-family="'Segoe UI', Arial, sans-serif">RESEARCH LIMITATIONS</text>
    <text x="16" y="48" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Coverage Concentration:</tspan> Official COFOG data is
    </text>
    <text x="16" y="68" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      concentrated in Europe and OECD; only 3 low-income
    </text>
    <text x="16" y="88" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      nations possess complete IMF 10-division series.
    </text>
    <text x="16" y="112" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Nowcast vs. Forecast:</tspan> Annual update uses realized
    </text>
    <text x="16" y="132" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      same-year indicators; true forecasting requires lags.
    </text>
    <text x="16" y="152" font-size="13" fill="{TEXT_MUTED}" font-family="'Segoe UI', Arial, sans-serif">
      • SHAP/LIME reflect associations, not causal laws.
    </text>

    <!-- Future Scope -->
    <rect x="436" y="0" width="418" height="175" rx="8" fill="#F0FDF4" stroke="#BBF7D0" stroke-width="1.2"/>
    <text x="452" y="24" font-size="14.5" font-weight="800" fill="#166534" font-family="'Segoe UI', Arial, sans-serif">FUTURE RESEARCH ROADMAP</text>
    <text x="452" y="48" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Global South Expansion:</tspan> Automated ingestion of
    </text>
    <text x="452" y="68" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      unstructured national budget gazettes and audit
    </text>
    <text x="452" y="88" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      reports across developing economies.
    </text>
    <text x="452" y="112" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      • <tspan font-weight="bold">Multi-Year Forecasting:</tspan> Extending from nowcasting
    </text>
    <text x="452" y="132" font-size="13" fill="{TEXT_DARK}" font-family="'Segoe UI', Arial, sans-serif">
      to 1–5 year medium-term forecasting horizons.
    </text>
    <text x="452" y="154" font-size="13" font-weight="700" fill="#15803D" font-family="'Segoe UI', Arial, sans-serif">
      • Controlled user study with professional budget analysts.
    </text>
  </g>

  <!-- Final Conclusion Strip -->
  <g transform="translate(0, 345)">
    <rect x="0" y="0" width="854" height="70" rx="8" fill="#0F2448" stroke="#1E40AF" stroke-width="1.2"/>
    <text x="427" y="28" font-size="15" font-weight="800" fill="#FFFFFF" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">
      CORE CONCLUSION: LAST YEAR'S ALLOCATION IS A FORMIDABLE BASELINE;
    </text>
    <text x="427" y="52" font-size="14" font-weight="600" fill="#38BDF8" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif">
      PEERS EMPOWER COLD-START POLICY DESIGN WHEN RIGOROUSLY CONSTRAINED &amp; EXPLAINED.
    </text>
  </g>
</g>
''')
svg.append(close_card())

# =========================================================================
# FOOTER BANNER (y: 2805 to 2828)
# =========================================================================
svg.append(f'''
<g id="footer">
  <rect x="45" y="2805" width="2745" height="24" rx="6" fill="#0F172A"/>
  <text x="1417" y="2822" font-size="14" font-weight="700" fill="#94A3B8" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" letter-spacing="1">
    AAVISHKAR UNIVERSITY-LEVEL RESEARCH COMPETITION 2026–27  ·  CATEGORY: COMMERCE, MANAGEMENT &amp; LAW  ·  RESEARCH CODE ALLOTTED AT VENUE
  </text>
</g>
''')

svg.append('</svg>')

# Write SVG
svg_content = "\n".join(svg)
svg_path = "poster/Avishkar University Level Poster.svg"
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"Generated {svg_path} (size: {len(svg_content)} bytes)")

# Convert to PDF using PyMuPDF
doc = fitz.open(svg_path)
pdf_bytes = doc.convert_to_pdf()
pdf_doc = fitz.open("pdf", pdf_bytes)
pdf_path = "poster/Avishkar University Level Poster.pdf"
pdf_doc.save(pdf_path)
print(f"Generated {pdf_path} (page rect: {pdf_doc[0].rect})")

# Render HD PNG (300 DPI target: ~11,811 x 11,811 pixels)
print("Rendering 300 DPI print-ready PNG...")
page = pdf_doc[0]
pix_hd = page.get_pixmap(dpi=300)
png_path = "poster/Avishkar University Level Poster.png"
pix_hd.save(png_path)
print(f"Generated {png_path} ({pix_hd.width} x {pix_hd.height} px)")

# Render Lightweight Preview PNG (~1500 x 1500 px)
print("Rendering lightweight preview PNG...")
pix_preview = page.get_pixmap(dpi=38)
preview_path = "poster/Avishkar University Level Poster Preview.png"
pix_preview.save(preview_path)
print(f"Generated {preview_path} ({pix_preview.width} x {pix_preview.height} px)")

print("All deliverables generated successfully!")
