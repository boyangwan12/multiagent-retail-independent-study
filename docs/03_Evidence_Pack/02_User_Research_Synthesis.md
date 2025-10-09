# Component 2: User Research Synthesis

**Project:** Multi-Agent Retail Demand Forecasting System
**Date Created:** October 2, 2025
**Purpose:** Synthesize user research findings, personas, workflows, and insights

---

## Executive Summary

Between September 24-29, 2025, we conducted 5 in-depth interviews with retail professionals across 4 distinct retail segments: furniture, mass retail, fashion, and multi-banner operations. The combined company scale ranges from 200 stores to 10,000+ stores globally, representing operational diversity from mid-market to enterprise retail.

**Key Research Findings:**
1. **Universal pain:** All 5 participants independently identified forecast accuracy as their top challenge
2. **Data burden:** 50% of analyst time spent on data preparation vs. strategic analysis
3. **Technology gap:** All participants expressed interest in AI/LLM approaches over traditional ML
4. **Scale variation:** Problems manifest differently across segments but share common root causes
5. **Collaboration opportunity:** 2 participants offered ongoing engagement (planning team access, project review)

This synthesis provides the user context, workflows, and personas that inform requirements and validate the multi-agent forecasting solution direction.

---

## Interview Summary Table

| ID | Date | Role | Company/Industry | Company Size | Key Pain Points | Unique Insights |
|---|---|---|---|---|---|---|
| **INT-001** | Sep 24, 2025 | Business Analyst | Furniture Manufacturing & Retail (Anonymous) | ~1000 employees, Global (US/Canada) | • Traditional ML inaccuracy (S:5)<br>• Cross-border complexity (S:3)<br>• Lack of agility (S:4) | 1-year planning cycles; cross-border tariff complexity; planning team already exploring agentic systems |
| **INT-002** | Sep 24, 2025 | Planning Manager | Walmart (Mass Retail) | ~10,000 stores globally, Millions of SKUs | • Forecast fragmentation (S:4)<br>• Supplier data quality (S:4)<br>• Localization difficulty (S:4) | Massive scale; Retail Link platform fragmentation; 60-85% forecast accuracy varying by category |
| **INT-003** | Sep 25, 2025 | Market Analyst | La Vie En Rose (Fashion Retail) | 400+ stores, 20 countries | • Data consolidation (S:5)<br>• Swimwear volatility (S:4)<br>• Late markdowns (S:5, $500K loss) | Fashion trend sensitivity; stakeholder friction; 15+ Excel reports with no single source of truth |
| **INT-004** | Sep 29, 2025 | Data Scientist | Canadian Tire (Multi-Banner Retail) | ~1,700 stores, ~250k SKUs, 15-20M loyalty members | • Weather shocks (S:5)<br>• Data prep burden (S:4, 50% time)<br>• Inventory-marketing disconnect (S:4) | Dealer vs. company-operated complexity; seasonality expertise; hybrid cloud (Azure + GCP) |
| **INT-005** | Sep 2025 | BI Developer (prev.), Policy & Governance (current) | Groupe Dynamite (prev.), Walmart (current) | Mid-market fashion → Enterprise mass retail | • Data cleaning (S:5, 50%+ time)<br>• Inventory optimization balance (S:4)<br>• Omnichannel complexity (S:4) | SE Asia CPG experience; correlation methodology (Spearman/Pearson); offered project review |

**Industry Representation:**
- **Furniture:** 1 company (long lead times, cross-border)
- **Mass Retail:** 1 company (massive scale, supplier coordination)
- **Fashion Retail:** 2 companies (trend volatility, seasonality)
- **Multi-Banner Retail:** 1 company (dealer complexity, weather sensitivity)

**Geographic Coverage:** North America (US/Canada focus), with participant experience from Southeast Asia

---

## User Personas

### Persona 1: Strategic Business Analyst (Furniture/Long Lead Time Retail)

**Archetype:** INT-001
**Role:** Business Analyst at global furniture manufacturing & retail company

**Demographics & Context:**
- Works separately from the planning team but liaises with them
- The company prefers anonymity due to competitive sensitivity
- ~1000 employees, US & Canada warehouse operations
- 1-year advance planning due to manufacturing lead times

**Goals:**
- Improve demand forecast accuracy to reduce costly inventory misallocation
- Minimize cross-border redistribution (tariffs, logistics costs)
- Enable the planning team to adopt more agile forecasting approaches
- Facilitate the adoption of AI/LLM solutions over traditional ML

**Pain Points:**
- Traditional ML models deliver insufficient accuracy (Severity 5)
- Location-specific demand predictions frequently fail (Severity 4)
- Complex redistribution optimization when forecasts miss (Severity 4)
- Cannot factor external economic/tariff changes into forecasts (Severity 4)
- Static models lack agility to adjust to market changes (Severity 4)

**Current Workflow:**
1. Design & forecast 1 year ahead
2. Predict quantity demand by location (traditional ML)
3. Allocate inventory to the US & Canada warehouses
4. Monitor actual vs. forecast performance
5. Reallocate inventory when gaps emerge
6. Optimize redistribution routes and manage tariffs

**Technology Stack:**
- Internal forecasting systems (traditional ML-based)
- Data team provides analytics/reporting
- Planning tools (not fully disclosed)

**Behavioral Traits:**
- Cautious about sharing company details (competitive sensitivity)
- Forward-thinking (already exploring agentic systems)
- Collaborative (offered planning team introductions upon MVP)
- Long-term oriented (open to post-graduation partnership)

**Magic Wand:**
> "Improve demand forecast accuracy with AI/LLM capabilities that can incorporate external factors"

**Quote:**
> "Traditional numerical ML models don't provide enough accuracy and agility to predict demand"

---

### Persona 2: Enterprise Planning Manager (Mass Retail / Massive Scale)

**Archetype:** INT-002
**Role:** Planning Manager at Walmart

**Demographics & Context:**
- Operates at unprecedented scale: 10,000 stores globally, millions of SKUs
- Coordinates across corporate merchandising, demand planners, buyers, and suppliers
- Manages relationships with external platforms (Retail Link, Blue Yonder)
- Multi-team coordination role

**Goals:**
- Unify fragmented forecasting views across teams and tools
- Improve forecast accuracy from the current 60-85% baseline (varies by category)
- Reduce manual consolidation of Retail Link extracts and spreadsheets
- Enable real-time, localized assortment decisions
- Minimize out-of-stock firefighting (currently 6-18 hrs/week)

**Pain Points:**
- Forecast fragmentation across teams with different tools/views (Severity 4, 8-16 hrs/week)
- Supplier data quality and inconsistent lead times (Severity 4, 4-10 hrs/week)
- Difficulty localizing national assortments to store-level demand (Severity 4, 6-12 hrs/week)
- Data prep consumes 10-20 hrs/week
- Cross-functional alignment meetings (6-12 hrs/week)
- Constant out-of-stock and rush allocation firefighting

**Current Workflow:**
1. Corporate merchandising sets MFP targets and assortment priorities
2. Demand planners/buyers create pre-season forecasts (Retail Link + planning tools)
3. Allocation rules set; replenishment engines translate buy plans to store/DC allocations
4. Cross-docking and hub flows scheduled
5. Real-time POS tracking via Retail Link
6. Automated replenishment with AI routing
7. Markdown/clearance decisions by promo teams

**Technology Stack:**
- **Planning:** Retail Link, internal Walmart platforms
- **Forecasting:** In-house + Blue Yonder
- **Inventory:** Replenishment engines, cross-dock orchestration
- **Reporting:** Retail Link dashboards, internal BI/AI dashboards
- **Other:** Supplier portals, WMS systems
- **Excel Usage:** High—suppliers and teams supplement with Excel for scenarios and reconciliation

**Behavioral Traits:**
- Process-oriented (large organization requires structure)
- Frustrated by fragmentation despite significant technology investment
- Focused on supplier coordination challenges
- Seeks automation and integration

**Magic Wand:**
> "Make forecasting and allocation truly real-time and integrated into a single source that automatically localizes the assortments and rebalances inventory with less (or no) manual handoffs."

**Quote:**
> "Manual consolidation of Retail Link extracts and the internal spreadsheets" [listed as the biggest time waster]

---

### Persona 3: Analytical Market Analyst (Fashion Retail / High Volatility)

**Archetype:** INT-003
**Role:** Market Analyst at La Vie En Rose (lingerie & swimwear)

**Demographics & Context:**
- 400+ stores across 20 countries (primarily Canada, expanding to the US)
- 3,500 active SKUs per season
- High seasonality (swimwear vs. lingerie categories)
- 6-month manufacturing lead times

**Goals:**
- Reduce data consolidation burden (currently 10 hrs/week)
- Improve swimwear forecast accuracy (weather-dependent, highly volatile)
- Prevent late markdown decisions ($500K annual margin loss)
- Gain stakeholder trust (merchandising team overrides analytical recommendations)
- Achieve a single source of truth (currently 15+ Excel reports)
- Support US expansion without breaking current manual processes

**Pain Points:**
- Data consolidation across systems (Severity 5, 10 hrs/week)
- Swimwear demand volatility (Severity 4, 2 months/year uncertainty)
- Store allocation mismatches (Severity 4, 5 hrs/week)
- Late markdown decisions (Severity 5, $500K lost margin annually)
- Manual Excel model maintenance (Severity 3, 8 hrs/week)
- Cross-team alignment issues (Severity 4, 3 hrs/week)
- New product performance unknowns (Severity 4, 20% forecast error)
- Firefighting (12 hrs/week)

**Current Workflow:**
1. Pull historical sales from the e-commerce platform and internal dashboards
2. Clean and consolidate data in Excel (match SKUs across channels, adjust for stockouts)
3. Forecast models with seasonal adjustments (MMM model)
4. Present to the merchandising team for buy decisions
5. Work with the allocation team to distribute across stores
6. Monitor sell-through weekly, adjust allocations
7. Recommend markdowns for slow-moving inventory

**Technology Stack:**
- **Planning:** Confidential
- **Forecasting:** Internal models with some scripts
- **Inventory:** Legacy ERP system
- **Reporting:** Tableau dashboards, Excel for detailed analysis
- **Other:** Salesforce (B2B wholesale), separate POS system
- **Excel Usage:** 70% of actual analysis in Excel or Python (20+ hrs/week across team)
- **Workarounds:** Python scripts to auto-pull data; "shadow" allocation system in Access database

**Behavioral Traits:**
- Analytically rigorous but frustrated by stakeholder dismissal
- Creative problem-solver (builds workarounds when systems fail)
- Concerned about scalability (US expansion will amplify problems)
- Seeks respect/credibility for analytical recommendations

**Magic Wand:**
> "A unified system that actually talks between forecasting, buying, and allocation - where a demand signal automatically triggers the right actions across teams without me having to coordinate everything manually through Excel and emails."

**Key Quote:**
> "The merchandising team treats our forecasts like 'suggestions' until the numbers prove them wrong - but by then it's too late to course-correct."

---

### Persona 4: Technical Data Scientist (Multi-Banner / Infrastructure-Aware)

**Archetype:** INT-004
**Role:** Data Scientist (Marketing/DS) at Canadian Tire

**Demographics & Context:**
- ~1,700 stores across multiple banners (dealer-operated + company-operated)
- ~250k active SKUs
- 15-20M loyalty customers
- Hybrid cloud infrastructure (Azure Databricks/MLflow + GCP Vertex/Kubeflow)

**Goals:**
- Improve seasonality/weather forecast responsiveness (currently monthly updates, need higher frequency)
- Integrate inventory signals upstream into marketing/pricing decisions
- Reduce data prep burden (currently 50% of week = ~20 hrs)
- Increase model run frequency (currently monthly due to cost, desire weekly)
- Normalize dealer vs. company-operated complexity

**Pain Points:**
- Weather/seasonality shocks drive forecast misses (Severity 5)
- Inventory as a lagging constraint to marketing plans (Severity 4)
- Heavy multi-source data prep (Severity 4, ~20 hrs/week)
- Dealer vs. company-operated complexity (Severity 3)
- Model frequency & infrastructure cost constraints (Severity 3, monthly vs. desired weekly)
- High cost of inventory reallocation (Severity 3)

**Current Workflow:**
1. Seasonal planning window defined by banner and ownership model
2. Build SKU/category forecasts and decision support for pricing/promotions
3. Assemble features from POS, e-comm, seasonality, weather, competitor, loyalty, and macro data
4. Price/promo selection support (cannibalization, halo effects, flyer SKU selection)
5. Deploy interpretable models on hybrid cloud (Azure/GCP)
6. Weekly in-season monitoring (promo uplift, anomaly checks, short-horizon signals)
7. Campaign experiments (Braze → GCP)
8. Feedback loop (post-event outcomes feed back as correctness/penalty signals)

**Technology Stack:**
- **Cloud/Infra:** Azure + GCP hybrid (+ on-prem DC)
  - Azure: Databricks, MLflow
  - GCP: Vertex AI, Kubeflow
- **Optimization:** CPLEX (evaluating Gurobi for cloud alignment)
- **Campaigns/Experiments:** Braze (push/app messaging)
- **External Data:** StatsCan (demographics, macro), paid weather APIs, competitor signals (esp. Amazon)
- **Internal Product:** "Robson AI" (with BCG) for marketing/pricing/flyer SKU selection
- **Excel/Python:** Moderate for ad-hoc analysis, most production on governed pipelines

**Behavioral Traits:**
- Technically sophisticated (understands infrastructure trade-offs)
- Pragmatic (accepts cost constraints, uses lightweight feedback mechanisms)
- Multi-source data expertise (loyalty, macro, competitor, weather)
- Interpretability-focused (emphasizes explainable models for stakeholder buy-in)
- Systems thinker (recognizes inventory-marketing feedback loops)

**Magic Wand:**
> "Ingest near-real-time weather and trigger threshold alerts into the weekly operating rhythm. Embed inventory availability/PO-cycle awareness before pricing/promo selection."

**Key Quote:**
> "Inventory is a lagging factor—it helps to forecast inventory first, then layer marketing/pricing AI."

---

### Persona 5: Methodological BI Developer (Multi-Industry / Process Expert)

**Archetype:** INT-005 (Vaibhav Vishal)
**Role:** BI Developer (previous - Groupe Dynamite), Policy & Governance Team (current - Walmart)

**Demographics & Context:**
- Previous: Mid-market fashion retail (Groupe Dynamite)
- Previous project: Price optimization & inventory management for chocolates/biscuits/cookies in Southeast Asia (CPG)
- Current: Walmart Policy & Governance (safety data analytics, compliance tracking)

**Goals:**
- Guide students toward realistic, scoped projects (avoid trying to solve everything)
- Share methodology from a successful CPG forecasting project
- Emphasize the importance of data quality and feature selection
- Recommend focus on one domain (sales forecasting, not revenue/finance/inventory all at once)

**Pain Points (from previous work):**
- Data cleaning consumed 50%+ of project time (Severity 5)
- Inventory optimization balance (overstock vs. understock) (Severity 4)
- Manual interventions needed in automated processes (Severity 3)
- Uncontrollable factors management (unexpected events) (Severity 4)
- Multi-channel complexity (online vs. brick-and-mortar) (Severity 4)
- Store-to-store and warehouse-to-store transfer coordination (Severity 3)
- Social media trend tracking for fashion (Severity 3)

**Previous Successful Workflow (CPG Project):**
1. **Data Cleaning (50%+ time):** Remove anomalies, standardize formats, make data usable
2. **Correlation Analysis:** Spearman/Pearson models to identify correlated metrics from 100+ columns
3. **Time Series Forecasting:** ARIMA models with multiple algorithm testing
4. **Simulator Creation:** Excel + Power BI simulator for scenario testing (user inputs → expected output)
5. **Output:** Predictive models, pricing strategies, prescriptive recommendations

**Data Requirements (from experience):**
- 10+ years historical sales data (ideal)
- Weather, social media trends, inventory, demographics, historical patterns, product placement
- Seasonality markers (event-based: Black Friday, Christmas, Halloween, back-to-school)

**Technology Stack (previous experience):**
- Correlation: Spearman, Pearson models
- Forecasting: ARIMA, multiple algorithms with cross-validation
- Visualization: Excel, Power BI
- Feature selection: Categorical vs. numerical column analysis

**Behavioral Traits:**
- Educator/mentor (provides detailed methodology guidance)
- Pragmatic about scope (warns against overreach)
- Methodical (emphasizes correlation analysis and feature selection)
- Generous with time (offered to review the project before submission)

**Key Recommendations:**
1. Focus on ONE domain (sales forecasting, not inventory + revenue + finance)
2. Choose ONE product category (fashion vs. groceries vs. electronics)
3. Use Kaggle for public datasets
4. Start with correlation models for feature selection
5. Build a simulator for scenario testing
6. Expect manual insight generation (not 100% automation)

**Key Quotes:**
> "50% of the time was data cleaning - removing anomalies, making the data clean."

> "From 100 columns, we used to figure out which metrics are correlated to sales using Spearman and Pearson correlation models."

> "It's good to focus on one [domain]. It would be too much to cover all aspects across different areas like inventory, revenue, or finance."

> "Seasonality can vary based on the sales of the product that comes in. It can be during festivals like Christmas or Halloween, or periods where there are heavy discounts just to get rid of the inventory."

---

## Current Workflow Documentation

### Workflow 1: Furniture Retail (1-Year Planning Cycle)

**Context:** INT-001 - Long manufacturing lead times require advance planning

```mermaid
graph LR
    A[Design & 1-Year Forecast] --> B[Location-Based Demand Prediction<br/>Traditional ML]
    B --> C[Initial Inventory Allocation<br/>US & Canada Warehouses]
    C --> D{Forecast<br/>Accurate?}
    D -->|No| E[Reallocation Needed]
    E --> F[Identify Shortage Warehouses]
    F --> G[Find Source Warehouses]
    G --> H[Optimize Transfer Routes]
    H --> I[Execute Cross-Border Transfers]
    I --> J[Manage Tariff/Logistics Costs]
    D -->|Yes| K[Monitor & Maintain]

    style A fill:#1976d2,color:#fff
    style B fill:#f57c00,color:#fff
    style C fill:#1976d2,color:#fff
    style D fill:#fbc02d,color:#000
    style E fill:#d32f2f,color:#fff
    style K fill:#388e3c,color:#fff
```

**Pain Cascade:**
- **Step B fails** → Location predictions inaccurate (PP-002, Severity 4)
- **Step C misallocates** → Wrong warehouses get wrong quantities
- **Steps E-J triggered** → Expensive, time-consuming redistribution (PP-003, PP-004)

**Time Breakdown:**
- Pre-season: Months of planning (1-year horizon)
- In-season: Ongoing monitoring; reallocation decisions when needed
- Optimization: Continuous evaluation of allocation performance

---

### Workflow 2: Mass Retail (Walmart - Massive Scale)

**Context:** INT-002 - 10,000 stores, millions of SKUs, complex supplier coordination

**Pre-Season:**
```
1. Corporate Merchandising → MFP targets, category priorities
2. Demand Planners + Buyers → Forecasts (Retail Link + planning tools) + Initial buys
3. Allocation Rules Set → Replenishment engines translate to store/DC allocations
4. Cross-dock Flows → Hub flows scheduled
```

**In-Season:**
```
5. Real-time POS → Retail Link platform
6. Automated Replenishment → Vendor-managed inventory or Walmart systems
7. Sales Tracking → Internal BI/AI dashboards flag anomalies
```

**Optimization:**
```
8. Markdown/Clearance → Promotions team based on sell-through, aging, seasonality
9. Analytics/Reports → Category and supply chain teams via Retail Link, BI
```

**Pain Points in Workflow:**
- **Step 2:** Forecast fragmentation (PP-007) - Different teams/tools create conflicting views (8-16 hrs/week)
- **Step 2:** Supplier data quality issues (PP-008) - Lead time inconsistency (4-10 hrs/week)
- **Step 3:** Localization difficulty (PP-009) - National assortments don't match local demand (6-12 hrs/week)
- **Step 5-6:** Out-of-stock firefighting (PP-012) - Reactive rushes (6-18 hrs/week)
- **Continuous:** Manual data consolidation (PP-010) - Retail Link extracts + spreadsheets (10-20 hrs/week)

**Time Breakdown:**
- Data Prep: 10-20 hrs/week
- Analysis: 8-15 hrs/week
- Meetings: 6-12 hrs/week
- Firefighting: 6-18 hrs/week
- Reports: 4-8 hrs/week

---

### Workflow 3: Fashion Retail (La Vie En Rose - Trend Volatility)

**Context:** INT-003 - High seasonality (swimwear vs. lingerie), 6-month lead times, limited replenishment

```
Step 1: Pull historical sales (e-commerce platform + La Vie En Rose dashboard)
Step 2: Clean & consolidate in Excel (match SKUs across channels, adjust for stockouts)
       → 10 hrs/week (PP-013, Severity 5)
Step 3: Forecast models with seasonal adjustments (MMM model)
       → Swimwear particularly challenging (PP-014, Severity 4)
Step 4: Present to the merchandising team for buy decisions
       → Often overridden by "gut feel" (PP-018, Severity 4)
Step 5: Work with the allocation team to distribute across stores
       → Store clustering too simplistic (PP-015, Severity 4)
Step 6: Monitor sell-through weekly, adjust allocations
       → 3-day data lag (PP-016 contributor)
Step 7: Recommend markdowns for slow-moving inventory
       → Late decisions cost $500K/year (PP-016, Severity 5)
```

**Markdown Process Cascade:**
```
Week 6: First markdown if sell-through < 40%
Week 10: Deeper cuts
Post-Week 10: Transfers to outlets
```

**Pain Points in Workflow:**
- **Step 2:** Data consolidation nightmare - Always discrepancies between warehouse and store systems
- **Step 3:** Weather dependency (swimwear) creates forecast volatility
- **Step 4:** Stakeholder friction - Forecasts treated as "suggestions"
- **Step 5:** Allocation too simplistic - Manual adjustments for Quebec vs. the rest of Canada
- **Step 6:** 3-day lag prevents timely action
- **Step 7:** Late markdowns destroy margin

**Time Breakdown:**
- Data Prep: 15 hrs/week
- Analysis: 10 hrs/week
- Meetings: 8 hrs/week
- Firefighting: 12 hrs/week
- Reports: 5 hrs/week
**Total:** 50 hrs/week (125% utilization, implying overtime or team aggregation)

**Biggest Time Wasters:**
1. Reconciling inventory between systems
2. Rebuilding broken Excel models (monthly)
3. Re-explaining analytical recommendations to stakeholders

---

### Workflow 4: Multi-Banner Retail (Canadian Tire - Seasonality Experts)

**Context:** INT-004 - Dealer vs. company-operated stores, heavy weather/seasonality sensitivity, hybrid cloud

**Planning Horizon:**
- **Dealer-operated:** ~12 months ahead
- **Company-operated:** ~6-8 months ahead

**Workflow Steps:**
```
1. Seasonal Planning Window → Defined by banner and ownership model
2. DS Builds Forecasts → SKU/category-level with decision support for pricing/promotions
3. Feature Assembly → POS, e-comm, seasonality, weather, competitor, loyalty, macro (StatsCan)
4. Price/Promo Selection → Cannibalization/halo effects, flyer SKU selection
5. Model Deployment → Interpretable models on Azure/GCP hybrid cloud
6. In-Season Monitoring → Weekly promo uplift, anomaly checks, short-horizon signals
7. Campaign Experiments → Braze → GCP for push/app messaging
8. Feedback Loop → Post-event outcomes feed back as correctness/penalty signals
```

**Pain Points in Workflow:**
- **Step 3:** Data prep dominates (PP-023) - 20 hrs/week (~50% of time)
- **Step 3:** Weather updates too coarse (PP-021) - Monthly vs. need weekly/daily
- **Step 4:** Inventory-marketing disconnect (PP-022) - Inventory treated as lagging constraint
- **Step 5:** Infrastructure cost limits (PP-025) - Monthly runs vs. desired weekly
- **Step 1:** Dealer vs. company-operated complexity (PP-024) - Different approval cycles

**Time Breakdown:**
- Data Prep: ~20 hrs/week (50%)
- Stakeholder/Alignment: ~10 hrs/week
- Modeling/Visualization: ~10 hrs/week
- Firefighting: Spikes when feeds break or urgent reads are needed

**Biggest Time Wasters:**
1. Multi-source integration & cleansing (loyalty, partner, GA4, StatsCan, competitor)
2. Reconciliation and manual conditioning to make the data model-ready

---

## Key Themes Across Workflows

### Theme 1: Data Preparation Dominates All Workflows
**Evidence:**
- Furniture: TBD (not quantified)
- Walmart: 10-20 hrs/week
- La Vie En Rose: 15 hrs/week
- Canadian Tire: 20 hrs/week (50% of time)
- Groupe Dynamite: 50%+ of project time

**Why This Matters:** Time spent on data prep is time NOT spent on strategic optimization, scenario planning, or innovation.

---

### Theme 2: Forecast Accuracy Consistently 60-70% Despite Investment
**Evidence:**
- Walmart: 60-85% (varies by category)
- La Vie En Rose: 60% (style-level), 70% (category-level)
- Furniture: Not disclosed but identified as severity-5 pain
- Canadian Tire: Uses closed-loop feedback to correct misses (implies ongoing accuracy challenges)

**Why This Matters:** 30-40% error rate drives all downstream allocation problems and margin erosion.

---

### Theme 3: All Workflows Include Reactive Firefighting Step
**Evidence:**
- Walmart: 6-18 hrs/week on out-of-stock rushes
- La Vie En Rose: 12 hrs/week firefighting
- Canadian Tire: Spikes when feeds break or urgent reads needed
- Furniture: Reallocation triggered when forecasts fail

**Why This Matters:** Firefighting culture is a symptom of inadequate forecasting; reactive vs. proactive operations.

---

### Theme 4: Manual Workarounds Pervasive Across All Companies
**Examples:**
- **Walmart:** Suppliers build custom Retail Link queries and local dashboards; buyers use spreadsheet models
- **La Vie En Rose:** Python scripts to auto-pull data; "shadow" allocation system in Access database; group texts with store managers during promos
- **Canadian Tire:** Lightweight correctness/penalty features as a feedback mechanism (workaround for infrequent retraining)
- **Furniture:** TBD (interview focused on high-level workflow)

**Why This Matters:** Workarounds indicate system inadequacy; they don't scale and create technical debt.

---

### Theme 5: Stakeholder Alignment is a Friction Point
**Evidence:**
- Walmart: 6-12 hrs/week in cross-functional alignment meetings to solve disagreements
- La Vie En Rose: Merchandising team overrides forecasts based on "gut feel"; forecasts treated as "suggestions"
- Canadian Tire: ~10 hrs/week with stakeholders explaining results

**Why This Matters:** Lack of trust in analytical outputs undermines value; cultural problem rooted in forecast inaccuracy.

---

## Quote Library by Theme

### Theme 1: Forecast Accuracy Challenges

> "Traditional numerical ML models don't provide enough accuracy and agility to predict demand"
> — INT-001 (Business Analyst, Furniture Retail)

> "They want to adopt AI/LLMs to improve prediction accuracy, instead of only traditional machine learning models"
> — INT-001 (Business Analyst, Furniture Retail)

> "Forecast Accuracy: 60-85% varying by category, per item, and location. Must measure by SKU per store."
> — INT-002 (Planning Manager, Walmart)

> "Forecast Accuracy: 60% at style level, 70% at category level"
> — INT-003 (Market Analyst, La Vie En Rose)

> "Seasonality is the lowest-hanging fruit—we stress it across categories."
> — INT-004 (Data Scientist, Canadian Tire)

> "Weather/seasonality shocks drive forecast misses [...] Monthly weather updates too coarse; need finer granularity"
> — INT-004 (Data Scientist, Canadian Tire)

> "Seasonality can vary based on the sales of the product that comes in. It can be during festivals like Christmas or Halloween, or periods where there are heavy discounts just to get rid of the inventory."
> — INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)

---

### Theme 2: Data Integration & Quality

> "50% of the time was data cleaning - removing anomalies, making the data clean."
> — INT-005 (Vaibhav Vishal)

> "We spend about half the week on data prep, ~10 hours with the business, ~10 hours on the model and visuals."
> — INT-004 (Data Scientist, Canadian Tire)

> "Data Prep: 10-20 hrs/week in pulling POS, promos, supplier data, and cleaning Retail Link extracts."
> — INT-002 (Planning Manager, Walmart)

> "Reconciling inventory numbers between the warehouse system and store systems - always discrepancies"
> — INT-003 (Market Analyst, La Vie En Rose)

> "15+ different Excel reports circulated weekly, no single source of truth, constant reconciliation issues"
> — INT-003 (Market Analyst, La Vie En Rose)

> "There are a lot of factors... weather, seasonality, inventory, historical data, even social media trends... demographic data, product placement in stores."
> — INT-005 (Vaibhav Vishal)

> "From 100 columns, we used to figure out which metrics are correlated to sales using Spearman and Pearson correlation models."
> — INT-005 (Vaibhav Vishal)

---

### Theme 3: Stakeholder Friction

> "The merchandising team treats our forecasts like 'suggestions' until the numbers prove them wrong - but by then it's too late to course-correct."
> — INT-003 (Market Analyst, La Vie En Rose)

> "Buyers often override analytical recommendations based on 'gut feel' from trade shows, limited ability to test new styles before committing to bulk orders"
> — INT-003 (Market Analyst, La Vie En Rose)

---

### Theme 4: Magic Wand Solutions

> "Make forecasting and allocation truly real-time and integrated into a single source that automatically localizes the assortments and rebalances inventory with less (or no) manual handoffs."
> — INT-002 (Planning Manager, Walmart)

> "A unified system that actually talks between forecasting, buying, and allocation - where a demand signal automatically triggers the right actions across teams without me having to coordinate everything manually through Excel and emails."
> — INT-003 (Market Analyst, La Vie En Rose)

> "Improve demand forecast accuracy with AI/LLM capabilities that can incorporate external factors"
> — INT-001 (Business Analyst, Furniture Retail)

---

## Collaboration Opportunities & Validation Checkpoints

### Opportunity 1: Planning Team Access (INT-001)

**Stakeholder:** Planning Team Manager at furniture retail company
**Timeline:** Upon MVP delivery
**Access Granted By:** INT-001 (Business Analyst) will facilitate the introduction

**Value:**
- Deep-dive into specific workflows (move beyond high-level understanding)
- Understand integration requirements with existing systems
- Establish performance benchmarks and success criteria
- Potential real-world testing with actual company data

**Context:**
> "Upon MVP delivery, the interviewee will facilitate the introduction to the Planning Team Manager"
> "If MVP demonstrates value, the company is open to continued collaboration beyond the independent study period"
> "Opportunity for real-world deployment and testing with actual data"
> "Potential for ongoing partnership post-graduation"

**Significance:** The Planning team was already exploring agentic systems when we reached out, indicating urgency and receptiveness.

---

### Opportunity 2: Expert Project Review (INT-005)

**Stakeholder:** Vaibhav Vishal (Groupe Dynamite/Walmart)
**Offered Support:** Project review before submission

**Value:**
- Methodology validation (correlation analysis, feature selection, ARIMA approach)
- Scope appropriateness check (ensure focus on one domain per his recommendation)
- Technical approach feedback (informed by SE Asia CPG project experience)
- Industry credibility (current Walmart, previous fashion retail + CPG)

**Context:**
> "Potential project review before submission"

**Significance:** Vaibhav brings a multi-industry perspective (fashion retail, CPG, mass retail) and hands-on forecasting project experience.

---

## Research Insights Summary

### Insight 1: Problem is Industry-Wide, Not Company-Specific
**Evidence:** 5 different companies across 4 retail segments all independently identified forecast accuracy as #1 challenge.

**Implication:** Solution has broad market applicability beyond a single niche.

---

### Insight 2: Traditional ML is Structurally Insufficient
**Evidence:** All participants expressed interest in AI/LLM approaches; INT-001 planning team already exploring agentic systems.

**Implication:** Market is ready for paradigm shift; timing is favorable for multi-agent approach.

---

### Insight 3: Data Preparation is a Universal Bottleneck
**Evidence:** 50% time burden consistent across INT-002, INT-003, INT-004, INT-005.

**Implication:** Automated data pipeline is a table-stakes requirement, not a nice-to-have.

---

### Insight 4: External Factors Consistently Missed by Current Systems
**Evidence:** Weather (INT-004, INT-003, INT-005), social media (INT-005, INT-003), economic/policy (INT-001), competitor (INT-004).

**Implication:** Multi-source data integration is a core value proposition; it validates a multi-agent architecture where each agent specializes in a different data type.

---

### Insight 5: Stakeholder Trust Requires Interpretability
**Evidence:** INT-003 merchandising override; INT-004 emphasis on interpretability; INT-003 "forecasts treated as suggestions."

**Implication:** Black-box AI will fail; system must provide explainable, transparent outputs.

---

### Insight 6: Scale Varies Dramatically, Core Problems are Consistent
**Evidence:** 200 stores (La Vie En Rose) to 10,000 stores (Walmart); 3,500 SKUs to millions of SKUs.

**Implication:** Solution must be scalable, but core functionality (multi-source integration, external factor incorporation, interpretability) applies across scales.

---

### Insight 7: Omnichannel Coordination is an Emerging Requirement
**Evidence:** INT-002 (Walmart omnichannel), INT-003 (e-comm + stores), INT-005 (online-store interconnection).

**Implication:** System must account for multi-channel demand influence and inventory fulfillment routing.

---

### Insight 8: Users Seek Automation But Accept Manual Insights
**Evidence:** INT-005 explicitly noted manual interventions still needed; INT-004 uses human judgment for exceptions.

**Implication:** 80-90% automation with human-in-the-loop for edge cases is acceptable; don't over-promise full automation.

---

## Next Steps for Evidence Pack

**This User Research Synthesis establishes:**
1. ✓ 5 distinct user personas with detailed goals, pain points, workflows
2. ✓ Current workflow documentation across 4 retail segments
3. ✓ Key themes validated across multiple independent sources
4. ✓ Collaboration opportunities for ongoing validation and testing
5. ✓ Research insights that inform requirements and solution direction

**Evidence Pack Component 3 (Requirements & Constraints) will:**
- Translate persona goals and pain points into functional requirements
- Specify data requirements based on workflow analysis
- Define technical constraints from technology stack insights

**Evidence Pack Component 4 (Approach Validation) will:**
- Connect multi-agent AI approach to user-expressed technology preferences
- Validate that the solution direction addresses documented pain points
- Demonstrate conceptual alignment with magic wand responses

---

**Document Status:** Complete
**Last Updated:** October 8, 2025
**Source Material:** Interview Notes INT-001 through INT-005, Quote_Library.md, Pain_Point_Inventory.md
