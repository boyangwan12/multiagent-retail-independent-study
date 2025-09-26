# Interview Notes Template

**Interview ID:** INT-03
**Date:** September 25th, 2025
**Participant:** anonymous
**Role:** Market Analyst
**Company Size:** Large (400+ stores across 20 countries)

---

## 1. WORKFLOW UNDERSTANDING

### Their Current Process:
```
Step 1: Pull historical sales data from current systems (E-commerce platform, La Vie En Rose dashboard)
Step 2: Clean and consolidate data in Excel - match SKUs across channels, adjust for stockouts
Step 3: Forecast models with seasonal adjustments for swimwear vs lingerie categories (MMM model)
Step 4: Present to merchandising team for buy decisions
Step 5: Work with allocation team to distribute across multiple Canadian stores
Step 6: Monitor sell-through weekly and adjust allocations
Step 7: Recommend markdowns for slow-moving inventory
```

### Planning (Pre-Season):
- MFP/Target Setting: Annual process starts in September for next year, department targets cascade down to category level, but struggle to balance growth targets with realistic market conditions
- Forecasting Process: 6-month lead time for manufacturing, forecast at style-color level, heavy reliance on last year +/- adjustments, swimwear particularly challenging due to weather dependency
- Buying Process: Buyers often override analytical recommendations based on "gut feel" from trade shows, limited ability to test new styles before committing to bulk orders

### Execution (In-Season):
- Allocation Method: Initial allocation based on store clustering (A/B/C stores by volume), manual adjustments for new store openings, Quebec stores get different mix than rest of Canada
- Sales Tracking: Weekly sell-through reports, but 3-day lag in getting clean data from stores, e-commerce data comes separately
- Replenishment: Limited for fashion items due to long lead times, only basics get replenished mid-season

### Optimization (Continuous):
- Markdown Process: First markdown at week 6 if sell-through below 40%, deeper cuts at week 10, outlets get transfers after second markdown
- Analytics/Reports: 15+ different Excel reports circulated weekly, no single source of truth, constant reconciliation issues

---

## 2. PAIN POINTS

| Pain Point | How Often? | Time Lost | Severity (1-5) |
|------------|------------|-----------|----------------|
| Data consolidation across systems | Daily | 10 hrs/week | 5 |
| Swimwear demand volatility | Seasonal | 2 months/year | 4 |
| Store allocation mismatches | Weekly | 5 hrs/week | 4 |
| Late markdown decisions | Monthly | $500K lost margin | 5 |
| Manual Excel model maintenance | Daily | 8 hrs/week | 3 |
| Cross-team alignment (merch vs ops) | Weekly | 3 hrs/week | 4 |
| New product performance unknowns | Each launch | 20% forecast error | 4 |

---

## 3. TIME BREAKDOWN

### Where They Spend Time:
- Data Prep: 15 hrs/week
- Analysis: 10 hrs/week
- Meetings: 8 hrs/week
- Firefighting: 12 hrs/week
- Reports: 5 hrs/week

### Biggest Time Wasters:
1. Reconciling inventory numbers between warehouse system and store systems - always discrepancies
2. Rebuilding Excel forecast models when someone breaks a formula - happens monthly
3. Re-explaining analytical recommendations to stakeholders who prefer intuition

---

## 4. TECH STACK & TOOLS

### Systems They Use:
- Planning: Confidential
- Forecasting: Internal models with some scripts
- Inventory: Legacy ERP system
- Reporting: Tableau for dashboards, Excel for detailed analysis
- Other: Salesforce for B2B wholesale, separate POS system

### Excel Usage:
- What for: 70% of actual analysis happens in Excel or Python - forecasting models, allocation matrices, markdown optimization, ad-hoc analysis
- How much: 20+ hours per week across team

### Workarounds:
1. Built Python scripts to auto-pull data from different systems into Excel
2. Created "shadow" allocation system in Access database because main system can't handle store transfers
3. Teams group with store managers for real-time inventory visibility during promotions

---

## 5. KEY METRICS

- Forecast Accuracy: 60% at style level, 70% at category level
- Planning Cycle Time: 120 days from initial forecast to product in store
- Number of SKUs: 3,500 active SKUs per season
- Number of Stores: 200+ in Canada, expanding to US

---

## 6. QUOTES TO REMEMBER

"The merchandising team treats our forecasts like 'suggestions' until the numbers prove them wrong - but by then it's too late to course-correct."

"We're trying to expand into the US market but using the same manual processes that barely work for Canada. It's going to be a nightmare."

---

## 7. MAGIC WAND QUESTION

If they could fix ONE thing:
A unified system that actually talks between forecasting, buying, and allocation - where a demand signal automatically triggers the right actions across teams without me having to coordinate everything manually through Excel and emails.

What would need to happen:
- Real-time data flow between systems (not batch updates)
- Automated alerts when forecasts deviate from actuals
- AI that learns from past mistakes (like weather impacts on swimwear)
- Single version of truth that everyone trusts
- Ability to run "what-if" scenarios without breaking production models
