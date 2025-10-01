# INT-005: Vaibhav Vishal - Groupe Dynamite/Walmart

**Date:** September 2024
**Interviewee:** Vaibhav Vishal
**Company:** Groupe Dynamite (previously), currently at Walmart
**Role:** Policy & Governance Team (Data Analytics)
**Previous Role:** BI Developer

---

## Key Insights

### 1. Demand Forecasting Factors

**Seasonality:**
- Not just weather-based (summer/winter), but event-driven:
  - Black Friday
  - Christmas
  - Halloween
  - Back-to-school
  - Sale periods for inventory clearance

**Other Critical Factors:**
- **Product Placement:** Location in stores (front vs. side) significantly impacts sales - first impression matters
- **Social Media Trends:** Fashion trends change weekly/daily and directly affect buying patterns
- **Inventory Levels:** Stock availability during spike periods is critical for capturing demand
- **Demographics:** Geographic and population density data influence demand patterns
- **Discounting Patterns:** Historical sale periods to clear inventory affect forecasting models

---

### 2. Previous Work Experience

**Use Case:** Price optimization and inventory management for chocolates, biscuits, and cookies in Southeast Asia

**Methodology:**
1. **Data Cleaning** (50%+ of total time)
   - Removing anomalies
   - Standardizing formats
   - Making data usable for models

2. **Correlation Analysis**
   - Used Spearman and Pearson correlation models
   - From 100+ columns, identified metrics correlated to sales
   - Ran multiple algorithms to find best correlations

3. **Time Series Forecasting**
   - Primarily used ARIMA models
   - Multiple algorithm testing with data shuffling
   - D-Score edition models for validation

4. **Simulator Creation**
   - Built using Excel worksheets and Power BI
   - User inputs numbers → system generates scenario and expected output
   - Used for business user insights

**Output:**
- Predictive models for stock optimization
- Pricing strategies based on seasonality and inventory
- Prescriptive recommendations for next year planning

---

### 3. Pain Points & Challenges

**Inventory Optimization:**
- Avoiding overstocking (excess inventory costs)
- Avoiding understocking (lost sales opportunities)
- Maintaining optimal levels backed by historical data (e.g., 2-5% growth year-over-year)

**Process Challenges:**
- **Manual Interventions:** Some processes required human insight generation between automated steps
- **Data Quality:** 50%+ time spent on cleaning and preparation
- **Uncontrollable Factors:** Managing situations beyond model control (unexpected events, trends)

**Multi-Channel Complexity:**
- Online vs. brick-and-mortar inventory coordination
- Warehouse to store shipping
- Store-to-store transfers for stock balancing
- Order fulfillment from multiple sources (warehouse, nearby stores, current store)

---

### 4. Recommendations for Project

**Scope Management:**
- **Focus on One Domain:** Don't try to cover all retail aspects (inventory, revenue, finance) - pick one specific use case
- **Be Specific:** Choose one category of products (fashion vs. groceries vs. electronics)
- Retail sectors differ: Fashion retail, CPG companies (P&G, PepsiCo), general retail (Walmart)

**Data Strategy:**
- **Use Kaggle** for public datasets
- Test multiple data sources to find best fit
- Look for datasets with 100+ columns/features
- Ensure data includes:
  - Historical sales data (10+ years ideal)
  - Seasonality markers
  - Inventory levels
  - Geographic/demographic data
  - If possible: social media trends, weather data

**Feature Selection:**
- Start with correlation models (Spearman, Pearson)
- Identify categorical vs. numerical columns
- Find significant correlations with sales/inventory
- Select only highly correlated features for model

**Architecture Considerations:**
- **Omnichannel:** Include online sales, warehouse, and store interconnectivity
- **Store-Level Granularity:** Forecast for specific stores, not just overall demand
- This enables inventory reallocation/rebalancing between stores

**Model Approach:**
- More **prediction modeling** than pure forecasting
- Use historical patterns to prescribe future actions
- Build simulator for scenario testing
- Expect manual insight generation steps

---

### 5. Current Role at Walmart

**Team:** Policy & Governance
**Focus Areas:**
- Safety data analytics (food safety, customer safety, store safety)
- Training compliance tracking
- Policy adherence monitoring

**Different from previous role:**
- Not merchandising or demand forecasting
- Still data-driven insights generation
- Demonstrates data is used across all departments in large retail organizations

---

## Relevant to Our Project

### ✅ Directly Applicable

**Seasonality Definition Confirmed:**
- Seasonality = events (Black Friday, Christmas, etc.) not just weather patterns
- This validates our project focus on seasonal demand forecasting

**Multi-Agent Approach Validated:**
- Multiple data sources needed (weather, social media, inventory, demographics, historical sales)
- Different agents for different data types makes sense
- Correlation analysis needed to determine which agents/features to activate

**Inventory Reallocation:**
- Store-level forecasting is necessary for post-forecast inventory rebalancing
- Need to consider omnichannel (online, warehouse, multiple stores)
- Transfer logistics between locations important

### ✅ Methodology Validation

**Process Flow Confirmed:**
1. Historical data collection
2. Data cleaning (major time investment)
3. Correlation analysis
4. Time series models (ARIMA and others)
5. Simulator/scenario testing
6. Business insights generation

**Tools & Techniques:**
- Correlation models: Spearman, Pearson
- Time series: ARIMA
- Visualization: Power BI, Excel
- Multiple algorithm testing with cross-validation

### ⚠️ Considerations & Warnings

**Project Scope:**
- Must focus on ONE specific use case
- Example: Sales forecasting for specific SKUs at specific stores
- Don't try to solve inventory + revenue + finance simultaneously

**Data Challenges:**
- Expect 50%+ time on data cleaning
- May need synthetic/mock data if real data unavailable
- Need significant historical data (multiple years)

**Automation Limits:**
- Manual insights may still be needed between automated steps
- Not 100% automated process expected
- Business user interpretation important

**Model Complexity:**
- Need to handle uncontrollable factors
- Models should be prescriptive, not just predictive
- Must account for interconnected systems (stores, warehouses, online)

---

## Action Items for Our Project

1. **Dataset Selection:**
   - Search Kaggle for retail sales datasets with seasonality markers
   - Prioritize datasets with store-level granularity
   - Look for 10+ years of historical data
   - Ensure includes: sales, inventory, dates, locations, product categories

2. **Use Case Refinement:**
   - Narrow to: "Sales forecasting for [specific product category] during [specific seasonal events] at store level"
   - Example: "Fashion retail sales forecasting for Black Friday and Christmas at individual store locations"

3. **Architecture Adjustments:**
   - Ensure data agents include: seasonality, inventory, historical patterns, demographic, weather
   - Add correlation analysis step before agent activation
   - Plan for store-level output to enable reallocation

4. **Additional Features to Consider:**
   - Omnichannel sales (online + in-store)
   - Store-to-store and warehouse-to-store transfer capabilities
   - Product placement data (if available)
   - Social media trend data (if available)

5. **Success Metrics:**
   - Forecast accuracy vs. actual sales
   - Inventory optimization (reduced overstock/understock)
   - Scenario simulation capability

---

## Quotes

> "Seasonality can vary based on the sale on the product that comes in. It can be during festivals like Christmas or Halloween, or periods where there are heavy discounts just to get rid of the inventories."

> "There are a lot of factors... weather, seasonality, inventory, historical data, even social media trends... demographic data, product placement in stores."

> "50% of the time was data cleaning - removing anomalies, making the data clean."

> "From 100 columns, we used to figure out which metrics are correlated to sales using Spearman and Pearson correlation models."

> "It's good to focus on one [domain]. It would be too much to cover all aspects across different areas like inventory, revenue, or finance."

> "There can be a connection between store sales and online sales - omnichannel. Orders can be dispatched from warehouse or nearby stores if the current store doesn't have stock."

---

## Contact Information

**LinkedIn:** [Not provided in interview]
**Email:** [Not provided in interview]
**Available for follow-up:** Yes - offered to review project work

---

## Interview Metadata

**Duration:** ~30 minutes
**Format:** Video call (1-on-1)
**Interviewer:** [Team member]
**Recording:** No
**Notes Quality:** High - full transcript available
**Follow-up Needed:** Potential project review before submission
