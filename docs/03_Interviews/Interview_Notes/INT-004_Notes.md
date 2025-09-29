# INT-004 Notes

**Interview ID:** INT-004  
**Date:** September 29, 2025  
**Participant:** Anonymous
**Role:** Data Scientist (Marketing / DS)  
**Company:** Canadian Tire (multi-banner)  
**Company Size:** Large (~1,700 stores; ~250k active SKUs; 15–20M loyalty members)

---

## 1. WORKFLOW UNDERSTANDING

### Their Current Process:
**Step 1:** Seasonal planning window defined by banner and store ownership model. Dealer-operated banners set promo/flyer calendars up to **~12 months** ahead; company-operated banners plan **~6–8 months** ahead.  
**Step 2:** DS builds SKU- and category-level forecasts and decision support for **pricing & promotions**; outputs delivered to Category Managers (who retain override rights).  
**Step 3:** Feature and signal assembly from **POS & e-comm**, **seasonality & weather**, **competitor/market (esp. Amazon)**, **loyalty/CRM**, and **macro (StatsCan: population, income, spend, birth rates; rural/urban)**.  
**Step 4:** Price/promo selection support including **cannibalization** and **halo** effects; “flyer SKU” selection.  
**Step 5:** Build & deploy interpretable models on hybrid cloud (**Azure Databricks/MLflow** + **GCP Vertex/Kubeflow**). Results land in dashboards, batch reports, and experiment readouts.  
**Step 6:** In-season weekly monitoring—promo uplift reads, anomaly checks, short-horizon signals; campaign experiments (Braze → GCP).  
**Step 7:** Feedback loop—post-event outcomes feed back as correctness/penalty signals; parameters/features adjusted for next cycle.

### Planning (Pre-Season):
- **MFP/Target Setting:** Top-down commercial targets; Marketing’s north-star KPI is **ROI**. Targets differ by banner/season.  
- **Forecasting Process:** Forecasts at **SKU level** with strong **seasonality/weather** sensitivity; weather provider updated **monthly** (desire: higher frequency).  
- **Buying/Promo Setup:** Category Managers choose flyer/promo items with DS input; overrides allowed and tracked informally.

### Execution (In-Season):
- **Decision Drivers:** Weekly cadence—promo uplift estimates, short-term demand signals, anomaly detection; scenario tests for price/promo messaging; experimentation for push/app campaigns (Braze).  
- **Deviation Handling:** **Weather shocks** (e.g., no-snow/snow events) dominate variance; triggers re-reads and quick recalibration.  
- **Inventory Interface:** DS (Marketing) **does not own** inventory or allocation; treats inventory as a **downstream/lagging constraint** that must be considered upstream in modeling and promo selection.

### Optimization (Continuous):
- **Markdown Process:** Owned by Category Managers; triggers include **aging**, **sell-through shortfalls**, and **excess inventory**. Typical governance with approval thresholds; reviews often **quarterly** with annual assortment refresh. “Reverse markdown”/price-up cases may occur on sudden trend spikes.  
- **Analytics/Reports:** Weekly business reviews; promo post-mortems; uplift/ROI tracking; what-if scenario runs; learnings captured into features/parameters and shared with partners.

---

## 2. PAIN POINTS

| Pain Point | How Often? | Time / Cost Impact | Severity (1–5) | Notes |
|---|---:|---:|---:|---|
| **Weather/seasonality shocks** drive forecast misses | Seasonal + ad hoc | Lost sales or excess stock | 5 | Monthly weather updates too coarse; need finer granularity |
| **Inventory as lagging constraint** to marketing plans | Ongoing | Sub-optimal promo/price if inventory reality lags | 4 | Desire to **ingest inventory signals** or **forecast inventory first** |
| **Heavy multi-source data prep** (POS, GA4, loyalty, partners, StatsCan, competitor) | Weekly | ~**20 hrs/week** | 4 | Join/clean/model-ready steps dominate |
| **Dealer vs company-operated complexity** | Ongoing | Slower reactions, more coordination | 3 | Approvals/PO cycles differ by ownership model |
| **Model frequency & infra cost constraints** | Ongoing | Models run **monthly** vs desired weekly | 3 | Latency reduces responsiveness to shocks |
| **High cost of inventory reallocation** | Ad hoc | Freight/ops costs → high approval bar | 3 | Only done with strong business case |
| **Macro shocks (tariffs, pandemics)** | Rare | Org-level cost; not primarily modeling | 2 | Handled by supply/process changes rather than DS |

---

## 3. TIME BREAKDOWN

### Where They Spend Time:
- **Data Prep:** ~**20 hrs/week** (≈50% of week).  
- **Stakeholder/Alignment:** ~**10 hrs/week** (reviews, explaining results, iteration).  
- **Modeling/Visualization:** ~**10 hrs/week** (emphasis on interpretability).  
- **Firefighting:** Not constant; spikes when feeds break or urgent reads are needed.

### Biggest Time Wasters:
1. Multi-source integration & cleansing (loyalty, partner data, GA4, StatsCan, competitor).  
2. Reconciliation and manual conditioning to make data **model-ready**.

---

## 4. TECH STACK & TOOLS

### Systems They Use:
- **Cloud/Infra:** **Azure + GCP** hybrid (+ on-prem DC).  
  - **Azure:** **Databricks**, **MLflow**.  
  - **GCP:** **Vertex AI**, **Kubeflow**.  
- **Optimization:** **CPLEX** today; evaluating **Gurobi** for cloud alignment.  
- **Campaigns/Experiments:** **Braze** (push/app); data ingested to GCP for uplift experiments and readouts.  
- **External Data:** **StatsCan** (population, income, spend, birth rates; rural/urban class), **paid weather APIs**, **competitor signals** (esp. Amazon).  
- **Internal Product:** **“Robson AI”** (with BCG) supporting marketing/pricing/flyer SKU selection—needs stronger **inventory awareness**.

### Excel/Python Usage:
- **What for:** Ad-hoc analysis, quick scenario checks, and feature prototyping outside governed pipelines.  
- **How much:** Moderate; most production runs on governed cloud pipelines.

### Workarounds:
- Lightweight correctness/penalty features as a feedback mechanism when full retraining cadence is longer than business cycle.

---

## 5. KEY METRICS

- **North Star:** **Marketing ROI**.  
- **Operating Cadence:** Weekly reviews; **monthly** model runs (cost/volume trade-off).  
- **Scale:** ~**250k active SKUs**, **~1,700 stores**; **15–20M** loyalty customers.  
- **Planning Horizons:** Dealers **~12 months**; company-operated **~6–8 months**.  
- **Accuracy:** Not disclosed; closed-loop feedback is used to penalize misses and adjust features/parameters.

---

## 6. QUOTES TO REMEMBER

- “**Seasonality is the lowest-hanging fruit**—we stress it across categories.”  
- “We spend **about half the week on data prep**, ~10 hours with the business, ~10 hours on the model and visuals.”  
- “**Inventory is a lagging factor**—it helps to **forecast inventory first**, then layer marketing/pricing AI.”

---

## 7. MAGIC WAND QUESTION

**If they could fix ONE thing:** Bring **higher-frequency, location-aware seasonality/weather intelligence** directly into price/promo and upstream inventory signals so shocks don’t derail plans.

**What would need to happen:**
- Ingest **near-real-time weather** and trigger **threshold alerts** into the weekly operating rhythm.  
- Embed **inventory availability/PO-cycle awareness** before pricing/promo selection (e.g., upstream of Robson AI).  
- Normalize **dealer vs company-operated** PO-cycle differences with a dynamic abstraction layer.  
- Maintain a closed-loop **uplift vs predicted** readout to auto-penalize misses and refine features.

---

### Follow-ups / Evidence Pack Hooks
- Anchor the demand agent on **seasonality + weather**, enriched with **StatsCan** demographics at **store/FSA** granularity.  
- Provide **scenario & alerting**: e.g., “No snow next 14 days in GTA → reduce shovel promo depth; shift to de-icing accessories.”  
