# INT-002 Notes

**Interview ID:** INT-002

**Date:** September 24, 2025

**Participant:** Opted for Anonymity

**Role:** Planning Manager

**Company:** Walmart

**Company Size:** Large - Massive global retail company

---

## 1. WORKFLOW UNDERSTANDING

### Their Current Process:
**Step 1:** Corporate Merchandising team defines the seasonal targets (MFP / revenue & margin targets) and high-level assortment priorities for the different categories.

**Step 2:** Demand planners and category buyers create the pre-season forecasts and initial assortments by using Retail Link & other planning tools. And, buyers form initial purchase plans and negotiate with the suppliers.

**Step 3:** Allocation rules are set, and replenishment engines (vendor-managed inventory or Walmart replenishment systems) translate the buy plan into store/DC allocations. And, Cross-docking and hub flows are then scheduled for execution.

### Planning (Pre-Season):
- **MFP/Target Setting:** The corporate merchandising team sets the Market Financial Plan (MFP) targets per category and the high-level merchandise plan. This information is passed to category managers/buyers, whereas corporate sets revenue, margin, and promotional budgets.
  
- **Forecasting Process:** Item-level and location-level forecasts are produced from the historical POS, trade promotions, seasonality, and macro inputs from its systems like Retail Link and other third-party planning platforms. Forecasts are then iterated between planners and buyers. 
  
- **Buying Process:** Buyers determine the initial buys and supplier orders informed by target weeks of supply, vendor agreements, lead times, and allocation assumptions. Large suppliers may use the dashboards and shipping plans from Retail Link to manage inventory. 

### Execution (In-Season):
- **Allocation Method:** Allocation rules combine the planned buys with the store-level forecasts to split the inventory across the stores and DCs (Distribution Centers). Vendor-managed inventory is used for some categories and the automated allocation engines and cross-dock flows are common for the fast moving items. 
  
- **Sales Tracking:** Real-time and daily POS ingestion manages/drives the sales tracking. Retail Link platform provides metrics to buyers and suppliers. The internal dashboards and AI models possibly flag the anomalies and trends. 
  
- **Replenishment:** Automated replenishment systems, integrated with DC and carrier schedules, handles restocking. Walmart has invested in "Self-healing" inventory and AI routing to reduce shortages. 

### Optimization (Continuous):
- **Markdown Process:** Markdown/clearance decisions are run by the promotions/markdown teams, which are informed by sell-through, inventory aging, and seasonality signals. Markdowns may also be executed centrally or regionally based on assortment. 
  
- **Analytics/Reports:** Category and supply chain teams rely on Retail Link platform, internal BI, and AI dashboards for in-season reporting.

---

## 2. PAIN POINTS

| Pain Point | How Often? | Time Lost | Severity (1-5) |
|------------|------------|-----------|----------------|
|Forecast fragmentation across teams, involving different tools/views|Weekly|8-16 hrs/week|4|
|Supplier data quality and inconsistent lead time info|Ongoing|4-10 hrs/week|4|
|Difficulty mapping national assortments to local demand (localization)|Seasonal|6-12 hrs/week|4|

---

## 3. TIME BREAKDOWN

### Where They Spend Time:
- **Data Prep:** 10-20 hrs/week in pulling POS, promos, supplier data, and cleaning Retail Link extracts.
  
- **Analysis:** 8-15 hrs/week in forecast review and scenario runs.
  
- **Meetings:** 6-12 hrs/week in cross-functional alignment between buying, supply, and merchandising teams.
  
- **Firefighting:** 6-18 hrs/week in out of stock, rush allocations and supplier exceptions.
  
- **Reports:** 4-8 hrs/week in regular reporting to leadership and reconciliations.

### Biggest Time Wasters:
1. Manual consolidation of Retail Link extracts and the internal spreadsheets.
2. Long cross-functional meetings to solve allocation/assortment disagreements.

---

## 4. TECH STACK & TOOLS

### Systems They Use:
- **Planning:** Retail Link and other internal Walmart planning platforms.
  
- **Forecasting:** Combination of in-house forecasting and third-party platforms like Blue Yonder.
- **Inventory:** Replenishment engies, cross-dock ochestration.
  
- **Reporting:** Retail Link dashboards and Internal BI/AI dashboards.
  
- **Other:** Supplier portals, shipping and WMS systems.

### Excel Usage:
- **What for:** Ad-hoc reconciliation, scenario modelling, and manual allocation edits. Many suppliers still use spreadsheet workflows with Retail Link outputs. 
  
- **How much:** High usage, many teams supplement with Excel for scenario runs and one-off changes. 

### Workarounds:
1. Suppliers build custom Retail Link queries and local dashboards to reconcile with internal systems.
2. Buyers use spreadsheet models for local assortment adjustments.

---

## 5. KEY METRICS

- **Forecast Accuracy:** 60-85% varying by category per item and location. Must measure by SKU per store.
  
- **Planning Cycle Time:** 30-90 days for pre-season planning from targets to final buys depending on the categories.
  
- **Number of SKUs:** Millions globally.
  
- **Number of Stores:** Around 10,000 globally.

---

## 6. MAGIC WAND QUESTION

**If they could fix ONE thing:** Make forecasting and allocation truly real-time and integrated into a single source that automatically localizes the assortments and rebalances inventory with less (or no) manual handoffs. 


**What would need to happen:** Unify Retail Link outputs with a central orchestrator that ingests POS, promo, supplier ETAs and DC flows; Deploy AI models that flag and auto-apply allocation adjustments.
