# Component 3: Requirements & Constraints

**Evidence Pack Component**
**Date:** October 2, 2025
**Source:** User research interviews INT-001 through INT-005
**Purpose:** Define system requirements, data specifications, technical constraints, and scope boundaries for retail demand forecasting solution

---

## Executive Summary

This document presents the comprehensive requirements and constraints for a retail demand forecasting system, derived from five in-depth interviews based on five North American retail operations.

The system must operate at scale (thousands of stores, millions of SKUs) while delivering store-level and SKU-level forecasts that account for multiple data sources including historical sales, weather patterns, social media trends, and economic indicators. Technical constraints around cost, infrastructure, and existing system integration significantly shape the solution architecture.

**Key Statistics:**
- 12 Functional Requirements
- 10 Data Requirements
- 7 Technical Constraints
- 5 Scope Boundaries
- 7 User Success Criteria


---

## Part 1: Functional Requirements

This section defines what the system must do to address the identified pain points in retail demand forecasting operations.

### FR-01: Multi-Source Data Integration

**Priority:** High
**Source:** INT-005, INT-004, INT-002
**Addresses Pain Points:** PP-023 (Siloed data sources), PP-033 (No holistic view), PP-005 (Missing external factors)

The system must integrate and harmonize multiple heterogeneous data sources to create a comprehensive foundation for forecasting. Retail demand is influenced by numerous factors that exist in separate systems, and current approaches struggle to combine these effectively.

**Required Data Sources:**
- **Historical sales data** from Point-of-Sale (POS) systems
- **Weather data** with granular geographic resolution and near-real-time updates
- **Social media trends** including sentiment, mentions, and influencer activity
- **Inventory levels** in real-time across all locations
- **Demographics** at store-level and geographic area resolution
- **Seasonality markers** for event-based forecasting (Black Friday, Christmas, etc.)
- **Competitor data** including pricing, promotions, and availability
- **Macro-economic indicators** from sources like Statistics Canada
- **Loyalty/CRM data** capturing customer behavior patterns
- **Product placement data** indicating in-store positioning and merchandising

**Rationale:** As one interviewee noted, "We need to understand not just what sold, but why it sold." Successful forecasting requires understanding the full context of demand drivers, which are currently fragmented across 15+ different systems and reports in typical retail organizations.

---

### FR-02: Store-Level Forecasting Granularity

**Priority:** High
**Source:** INT-001, INT-002, INT-003, INT-004, INT-005
**Addresses Pain Points:** PP-002 (Regional averages miss local variation), PP-009 (Store-specific patterns ignored), PP-015 (Poor initial allocation)

The system must produce demand forecasts at individual store location level, not merely regional or national aggregates. This granularity is non-negotiable for effective inventory management in multi-location retail operations.

**Business Value:**
- **Enables inventory reallocation** between locations based on predicted demand differences
- **Supports assortment localization** to match demographic and geographic preferences
- **Allows demographic-specific predictions** leveraging local population characteristics
- **Reduces stockouts and overstock** by matching supply to location-specific demand

**Context:** Regional forecasts consistently fail to capture local variations driven by demographics, weather, store format, and competitive environment. A store in urban Toronto has fundamentally different demand patterns than a rural Ontario location, even for the same retailer and product category.

---

### FR-03: SKU-Level Forecasting

**Priority:** High
**Source:** INT-002, INT-003, INT-004
**Addresses Pain Points:** PP-001 (Category-level too coarse), PP-019 (Style/color variability)

The system must forecast demand at individual Stock Keeping Unit (SKU) or style-color level. Category-level forecasting masks critical variation in customer preferences for specific items.

**Scale Requirements by Organization Type:**
- **Large mass merchandisers (Walmart):** Millions of active SKUs
- **Multi-category retailers (Canadian Tire):** ~250,000 active SKUs
- **Specialty fashion retailers (La Vie En Rose):** ~3,500 SKUs per season

**Rationale:** As articulated by a fashion retail interviewee, "Two dresses in the same category can have completely different demand curves based on color, style, and how they photograph on social media. Category forecasts tell us almost nothing useful for buying decisions."

**Technical Implication:** This requirement, combined with store-level granularity (FR-02), creates a massive computational challenge. A mid-size retailer with 500 stores and 50,000 SKUs requires 25 million individual forecasts.

---

### FR-04: Event-Based Seasonality Intelligence

**Priority:** High
**Source:** INT-005, INT-004
**Addresses Pain Points:** PP-021 (Generic seasonality patterns), PP-014 (Event impacts not captured)

The system must recognize and forecast for specific seasonal events and their unique demand signatures, not just general seasonal patterns like "winter" or "summer."

**Critical Events to Model:**
- **Retail calendar events:** Black Friday, Boxing Day, Cyber Monday
- **Holiday seasons:** Christmas, Halloween, Easter, Valentine's Day
- **Back-to-school periods** (late summer/early fall)
- **Sale and clearance periods** (end-of-season, promotional events)
- **Weather-driven events:** First snowfall, heat waves, unseasonable conditions

**User Quote (INT-005):**
"Seasonality can vary based on the sale on the product that comes in. It can be during festivals like Christmas or Halloween. The demand pattern for winter coats during the first real snow is completely different than general 'winter' trends."

**Context:** Generic seasonal decomposition fails to capture these event-specific spikes and the behavioral changes they drive. Halloween costume demand, for example, has a precise and sharp peak that doesn't align with general fall seasonality.

---

### FR-05: Continuous Learning & Adaptation

**Priority:** High
**Source:** INT-001, INT-004
**Addresses Pain Points:** PP-006 (Models don't adapt), PP-025 (Outdated parameters), PP-029 (No feedback loop)

The system must continuously learn from actual performance versus forecasted performance and adapt its predictions over time. Static models become obsolete as market conditions, customer preferences, and competitive dynamics evolve.

**Required Capabilities:**
- **Closed-loop feedback mechanisms** comparing forecast to actuals
- **Performance penalty/correctness signals** that inform model adjustments
- **Automated feature and parameter tuning** based on recent performance
- **Real-time or near-real-time updates** rather than manual monthly retraining

**User Quote (INT-004):**
"We need lightweight correctness and penalty features as a feedback mechanism. The model should get smarter every week, not wait for us to manually retrain it quarterly."

**Current State vs. Desired State:**
Currently, models are retrained manually on quarterly cycles, meaning they operate with 1-3 month old parameter estimates. The desired state is continuous adaptation with weekly or daily parameter updates.

---

### FR-06: External Factor Incorporation

**Priority:** High
**Source:** INT-001, INT-004, INT-005
**Addresses Pain Points:** PP-005 (External shocks not modeled), PP-021 (Weather impacts ignored), PP-030 (Competitor actions)

The system must incorporate external economic, policy, competitive, and environmental factors that influence retail demand but exist outside the organization's operational data.

**Required External Factors:**
- **Tariff and trade policy changes** affecting product costs and availability
- **Economic conditions** including employment, inflation, and consumer confidence
- **Competitor actions** particularly from e-commerce giants like Amazon
- **Weather shocks** beyond normal seasonal patterns
- **Macro demographic trends** including population growth, income changes, and spending patterns

**Context:** Retail demand doesn't exist in isolation. As one interviewee explained, "When Amazon drops their price 20%, we need to know that within days, not find out retrospectively when we're analyzing why our forecast was off."

**Data Sources:**
Statistics Canada, weather services, competitor monitoring tools, economic indicators (CPI, employment rates), social listening platforms.

---

### FR-07: Inventory Reallocation Support

**Priority:** Medium
**Source:** INT-001, INT-003, INT-005
**Addresses Pain Points:** PP-003 (Expensive redistribution), PP-032 (Reactive transfers), PP-004 (Transfer costs)

The system should support inventory redistribution decisions by identifying opportunities and quantifying trade-offs, though not necessarily automating the execution of transfers.

**Required Capabilities:**
- **Identify shortage versus surplus locations** based on forecast vs. inventory position
- **Suggest transfer routes** (store-to-store, warehouse-to-store, cross-border)
- **Quantify transfer costs** including logistics, handling, and time
- **Support scenario analysis** of different reallocation strategies

**Scope Note:** This is decision support, not autonomous execution. High-value inventory transfers require business judgment and approval workflows. As INT-005 noted, "Manual insights are still valuable - we need recommendations, not autonomous robots moving inventory."

**Cross-Border Consideration:**
For retailers operating in both US and Canada, the system must account for tariffs, customs, longer transit times, and regulatory differences when suggesting cross-border transfers.

---

### FR-08: Omnichannel Coordination

**Priority:** Medium
**Source:** INT-002, INT-003, INT-005
**Addresses Pain Points:** PP-031 (Channel cannibalization not modeled)

The system must account for the interconnected nature of modern retail sales channels and their mutual influence on demand patterns.

**Channels to Coordinate:**
- **Brick-and-mortar stores** with walk-in traffic
- **E-commerce platforms** (company website, marketplaces)
- **Warehouse fulfillment** for online orders
- **Store fulfillment** of online orders (click-and-collect, ship-from-store)
- **Cross-channel inventory visibility** for customers

**User Quote (INT-005):**
"There can be a connection between store sales and online sales - omnichannel. When we run a store promotion, online sales in that region often drop. We need to forecast total demand, not just channel-specific demand."

**Complexity:** Demand in one channel can cannibalize or stimulate demand in another. Online product availability can drive store visits. Store inventory visibility online can drive e-commerce conversion. These dynamics must be captured in the forecast.

---

### FR-09: Automated Data Pipeline & Cleaning

**Priority:** High
**Source:** INT-002, INT-003, INT-004, INT-005
**Addresses Pain Points:** PP-027 (Manual data wrangling), PP-023 (Siloed sources), PP-013 (Format inconsistency), PP-010 (Data quality issues), PP-008 (Time-consuming prep)

The system must dramatically reduce manual data preparation effort through automation of extraction, cleaning, standardization, and reconciliation processes.

**Required Automation:**
- **Automated extraction** from multiple source systems
- **Data cleaning** including outlier detection, missing value imputation, and anomaly removal
- **Format standardization** across disparate systems
- **Reconciliation** when sources provide conflicting information
- **Model-ready output** requiring no manual transformation

**Current State Baseline:**
Across all interviewed organizations, 50% of forecasting project time is spent on manual data preparation. Specific time investments include:
- 10-20 hours per week (INT-002 - Walmart)
- 15 hours per week (INT-003 - La Vie En Rose)
- 50% of total project time (INT-005, INT-004)

**Target State:**
Reduce manual data preparation to less than 20% of project time, with the remaining 20% focused on data validation and exception handling rather than routine cleaning.

---

### FR-10: Real-Time or Near-Real-Time Processing

**Priority:** Medium
**Source:** INT-002, INT-003, INT-004
**Addresses Pain Points:** PP-025 (Slow refresh cycles), PP-016 (Can't respond to changes)

The system should support rapid forecast updates and scenario testing to enable responsive decision-making.

**Required Capabilities:**
- **Reduce lag** between data capture and forecast update
- **Enable what-if scenarios** without breaking production forecasts
- **Support weekly forecast refresh** as minimum viable cadence, with daily as aspirational target
- **Trigger alerts** when actual demand deviates from forecast beyond defined thresholds

**Current Gap (INT-004):**
"We run models monthly because of infrastructure costs, but business needs weekly updates. By the time we see a trend, it's already been happening for 2-3 weeks."

**Infrastructure Consideration:**
This requirement conflicts with TC-04 (infrastructure cost constraints), requiring optimization to achieve frequent updates cost-effectively.

---

### FR-11: Interpretability & Transparency

**Priority:** Medium
**Source:** INT-004, INT-003
**Addresses Pain Points:** PP-018 (Black box models), PP-011 (No stakeholder trust)

The system must provide interpretable outputs and explanations to build stakeholder confidence and enable informed decision-making.

**Required Transparency Features:**
- **Visual dashboards** presenting forecasts and key drivers
- **Explainable predictions** showing what factors influenced the forecast
- **Feature importance visibility** indicating which data sources matter most
- **Confidence scores or ranges** quantifying uncertainty

**Context (INT-004):**
"Emphasis on interpretability is critical. If planners don't understand why the model is predicting something, they won't trust it. And if they don't trust it, they won't use it - they'll just keep doing Excel forecasts."

**Stakeholder Challenge:**
Retail planning teams have historically used simple methods (moving averages, exponential smoothing) that they fully understand. Advanced ML models are viewed with skepticism. Interpretability is the bridge to adoption.

---

### FR-12: Scenario Simulation Capability

**Priority:** Medium
**Source:** INT-005, INT-004
**Addresses Pain Points:** PP-022 (Can't test alternatives), PP-029 (No what-if analysis)

The system should enable business users to run what-if scenarios to understand potential outcomes under different assumptions.

**Scenario Types:**
- **Pricing and promotion testing:** What if we discount 20% vs. 30%?
- **Inventory level adjustments:** What if we stock 20% more in Region A?
- **Weather event simulations:** What if we get early snow this year?
- **Demand shock scenarios:** What if a competitor closes nearby stores?

**Previous Implementation (INT-005):**
"We built scenario testing using Excel worksheets and Power BI - users input numbers and the system generates scenarios. This was heavily used by planners for pre-season planning."

**Value Proposition:**
Planners need to test multiple strategies before committing to expensive inventory decisions. Scenario simulation reduces risk by allowing consequence-free experimentation.

---

## Part 2: Data Requirements

This section specifies the data inputs required to fulfill the functional requirements and achieve forecasting objectives.

### DR-01: Historical Sales Data

**Source:** INT-005, INT-002, INT-003, INT-004
**Supporting Requirements:** FR-02, FR-03, FR-05

**Specifications:**
- **Time Horizon:** 10+ years ideal (INT-005), minimum 3-5 years
- **Granularity:** SKU-level, store-level, daily or weekly resolution
- **Channels:** Point-of-Sale (in-store), e-commerce, wholesale/B2B
- **Attributes Required:**
  - Sales units (quantity sold)
  - Revenue (dollar value)
  - Margins and costs where available
  - Returns and exchanges
  - Promotions/discounts applied

**Rationale:**
Historical sales form the foundation of demand patterns. Longer history enables better detection of multi-year trends and anomaly context. Daily granularity preserves event-specific spikes that weekly aggregation would smooth out.

**Quality Considerations:**
Sales data must be cleaned for anomalies (system errors, duplicate entries) and tagged for known disruptions (store closures, system outages, stockout periods where demand was constrained by supply).

---

### DR-02: Inventory Data

**Source:** INT-005, INT-004, INT-003
**Supporting Requirements:** FR-07, FR-02, FR-10

**Specifications:**
- **Refresh Frequency:** Real-time or near-real-time (hourly minimum)
- **Location Coverage:** Store inventory, warehouse inventory, in-transit inventory
- **Attributes Required:**
  - Current stock levels by SKU and location
  - Stockout events and duration
  - Safety stock targets
  - Reorder points

**Rationale:**
Inventory position influences demand forecast interpretation (was low sales due to low demand or stockout?) and enables reallocation recommendations. Real-time inventory enables responsive decision-making.

**Integration Challenge:**
Inventory systems are often separate from POS systems, requiring reconciliation. INT-003 noted 3-day lag to receive clean, reconciled inventory data.

---

### DR-03: Weather Data

**Source:** INT-004, INT-003, INT-005
**Supporting Requirements:** FR-01, FR-04, FR-06

**Specifications:**
- **Geographic Granularity:** Store-level or Forward Sortation Area (FSA) level
- **Frequency:** Daily updates minimum; hourly ideal for real-time categories
- **Variables Required:**
  - Temperature (actual, feels-like)
  - Precipitation (rain, snow depth)
  - Severe weather events (storms, extreme cold/heat)
  - Forecast horizon: 2-4 weeks for planning purposes
- **Historical Archive:** 10+ years for training

**Current Gap (INT-004):**
"Monthly weather updates are too coarse. We need at least weekly, ideally daily. The first snowfall drives winter product demand, and it varies by weeks across our geography."

**Rationale:**
Weather significantly impacts retail demand for numerous categories: apparel, seasonal products, outdoor equipment, grocery items. Current approaches use generic seasonal indicators, missing weather-driven demand shifts.

---

### DR-04: Seasonality & Event Markers

**Source:** INT-005, INT-004
**Supporting Requirements:** FR-04

**Specifications:**
- **Event Calendar:**
  - Fixed holidays (Christmas, Halloween, Canada Day)
  - Floating holidays (Easter, Thanksgiving)
  - Retail events (Black Friday, Boxing Day, Prime Day)
  - Back-to-school periods
  - Cultural events (Ramadan, Lunar New Year)
- **Promotional Periods:** Company-specific sale windows
- **Regional Variations:** Event timing differences (Canadian vs. US Thanksgiving)

**Format:**
Structured calendar with event metadata (type, importance, typical demand impact) to enable model feature engineering.

---

### DR-05: Demographic & Geographic Data

**Source:** INT-004, INT-001, INT-003
**Supporting Requirements:** FR-02, FR-06

**Specifications:**
- **Population Demographics:**
  - Population density and growth
  - Income levels and distribution
  - Age distribution
  - Household size
  - Birth rates (relevant for baby/child product categories)
- **Geographic Classifications:**
  - Urban vs. rural vs. suburban
  - Store clustering attributes (A/B/C store classifications)
  - Trade area definitions
  - Proximity to competitors

**Source Example (INT-004):**
"We use Statistics Canada data: population, income, consumer spending, birth rates; also urban-rural classifications. These explain a lot of store-level variation."

**Refresh Frequency:**
Annual updates sufficient (demographics change slowly), except for new store openings requiring immediate classification.

---

### DR-06: Social Media & Trend Data

**Source:** INT-005, INT-003
**Supporting Requirements:** FR-01, FR-06

**Specifications:**
- **Fashion Trend Signals:**
  - Trending styles, colors, patterns
  - Influencer endorsements
  - Celebrity appearances
  - Runway and fashion week coverage
- **Social Media Metrics:**
  - Brand mentions and sentiment
  - Product-specific buzz
  - Competitor comparisons
- **Refresh Frequency:** Daily or weekly for fast-fashion categories

**Context (INT-005):**
"Fashion trends change weekly or even daily and directly affect buying patterns. When an influencer wears a specific style, demand can spike within days. Historical sales alone can't predict this."

**Challenge:**
Translating unstructured social media signals into structured forecast features requires NLP and domain expertise to identify relevant signals amid noise.

---

### DR-07: Competitor Data

**Source:** INT-004
**Supporting Requirements:** FR-06

**Specifications:**
- **Competitor Pricing:** Regular price and promotional pricing
- **Competitor Promotions:** Timing, depth, and types of sales
- **Market Share Trends:** Category-level share shifts
- **Product Availability:** Stockouts or discontinuations
- **Special Focus:** Amazon pricing and availability (INT-004 emphasis)

**Rationale:**
Competitor actions directly impact demand but are external to company systems. Price drops, stockouts, and promotions at competitors shift customer behavior in real-time.

**Data Sources:**
Web scraping, competitive intelligence services, manual market research, industry reports.

---

### DR-08: Macro-Economic Indicators

**Source:** INT-001, INT-004
**Supporting Requirements:** FR-06

**Specifications:**
- **Economic Indicators:**
  - GDP growth rates
  - Employment and unemployment rates
  - Consumer confidence indices
  - Inflation and Consumer Price Index (CPI)
  - Consumer spending patterns by category
- **Trade Policy Data:**
  - Tariffs and trade agreements
  - Cross-border trade costs
  - Regulatory changes

**Rationale:**
Retail demand is sensitive to economic conditions. Discretionary spending categories (furniture, fashion) are particularly affected by employment and confidence levels.

**Geographic Scope:**
National and regional indicators for US and Canada, reflecting North American operational focus.

---

### DR-09: Product Attributes

**Source:** INT-005, INT-003
**Supporting Requirements:** FR-03, FR-04

**Specifications:**
- **Product Taxonomy:**
  - Category, subcategory, department
  - Brand and vendor
- **Style Attributes:**
  - Style, color, size, material
  - Fashion season
  - Price point
- **Merchandising Data:**
  - Product placement (front vs. side, featured vs. standard)
  - New product launch dates
  - Product lifecycle stage (new, core, markdown)

**Context:**
Product attributes enable cross-item learning (how do similar products perform?) and placement-specific forecasting (featured items have different demand curves).

---

### DR-10: Supplier & Lead Time Data

**Source:** INT-002, INT-003, INT-001
**Supporting Requirements:** FR-07

**Specifications:**
- **Supplier Information:**
  - Estimated time of arrival (ETA) for in-transit orders
  - Manufacturing lead times by supplier and product category
  - Shipping schedules and frequency
  - Cross-border logistics timelines
- **Vendor Constraints:**
  - Minimum order quantities
  - Production capacity
  - Vendor agreement terms

**Rationale:**
Lead times determine how far ahead forecasts must be accurate and constrain reallocation opportunities. Long lead times require longer forecast horizons with higher uncertainty.

---

## Part 3: Technical Constraints

This section documents environmental, architectural, and operational constraints that shape solution design.

### TC-01: Omnichannel Architecture

**Source:** INT-002, INT-005
**Impact:** System design, data model, forecast structure

**Description:**
Modern retail operates across multiple interconnected channels: physical stores, e-commerce websites, marketplaces (Amazon, Walmart.com), warehouse fulfillment, and store-based fulfillment (click-and-collect, ship-from-store).

**Design Implications:**
- **Unified inventory view** across all channels and locations
- **Cross-channel demand influence modeling** (online promotions affecting store sales, etc.)
- **Fulfillment routing logic** determining optimal fulfillment location
- **Channel-specific behavior modeling** with cross-channel effects

**Complexity:**
Demand in one channel can cannibalize or stimulate demand in another. Forecasting must account for these interdependencies rather than treating channels independently.

---

### TC-02: Cross-Border Operations

**Source:** INT-001
**Impact:** Data requirements, cost modeling, scenario analysis

**Description:**
Retailers operating in both United States and Canada face additional complexities that constrain operational flexibility.

**Implications:**
- **Tariff cost modeling** for cross-border inventory transfers
- **Logistics time and cost** accounting for customs, longer transit, handling
- **Currency considerations** for pricing and cost comparisons
- **Regulatory differences** in product standards, labeling, returns policies
- **Forecast calibration** accounting for market differences

**Context:**
Cross-border transfers are expensive and slow but sometimes necessary for inventory optimization. The system must quantify these trade-offs accurately.

---

### TC-03: Scalability Requirements

**Source:** INT-002, INT-004, project scope
**Impact:** Architecture, algorithm selection, infrastructure

**Description:**
The solution must scale to enterprise retail dimensions.

**Scale Parameters:**
- **Store Count:** Up to 10,000+ locations (Walmart scale)
- **SKU Count:** Millions of SKUs (mass merchandisers) to thousands (specialty retailers)
- **Customer Count:** 15-20 million loyalty program members
- **Forecast Refresh:** Daily or weekly cycles
- **Forecast Horizon:** 6-12 months forward

**Calculation Example:**
A mid-size retailer with 500 stores and 50,000 SKUs requires 25 million store-SKU forecasts. At weekly refresh, this is 1.3 billion forecasts per year.

**Implication:**
Solution must be computationally efficient and parallelizable. Algorithms that scale linearly (or better) with data volume are preferred over quadratic or exponential approaches.

---

### TC-04: Infrastructure Cost Constraints

**Source:** INT-004
**Impact:** Refresh frequency, model complexity, optimization strategy

**Description:**
Cloud computing infrastructure costs limit model run frequency and complexity.

**Current Trade-off (INT-004):**
"We run models monthly instead of weekly because of cloud compute costs. Running weekly would triple our costs, and the business won't approve that budget."

**Implication:**
The solution must either:
1. Optimize for compute efficiency to enable frequent runs within budget, or
2. Demonstrate ROI sufficient to justify increased infrastructure investment, or
3. Use incremental update approaches rather than full retraining

**Cost Drivers:**
- Data volume processed
- Model training time and complexity
- Number of forecasts generated
- Storage for historical forecasts and feature data

---

### TC-05: Multi-Banner Operating Model Complexity

**Source:** INT-004
**Impact:** Planning horizon, approval workflows, system flexibility

**Description:**
Large retail organizations often operate multiple banners (brands) with different ownership and operating models.

**Operating Models:**
- **Dealer-operated stores:** Independently owned, corporate supply chain
  - Planning horizon: ~12 months
  - Approval cycles: More complex, dealer input required
- **Company-operated stores:** Fully corporate-owned
  - Planning horizon: ~6-8 months
  - Approval cycles: Centralized

**Implication:**
The system must support configurable planning horizons and approval workflows. A one-size-fits-all approach won't accommodate operational diversity across banners.

---

### TC-06: Integration with Existing Systems

**Source:** INT-002, INT-003, INT-004
**Impact:** Data pipelines, deployment architecture, user experience

**Description:**
The solution must integrate with complex existing enterprise technology stacks.

**Typical Systems:**
- **Enterprise Resource Planning (ERP):** SAP, Oracle, Microsoft Dynamics
- **Retail-Specific Platforms:** Retail Link (Walmart), vendor portals
- **Point-of-Sale (POS) Systems:** Various by retailer
- **Warehouse Management Systems (WMS):** Manhattan, SAP, custom
- **Business Intelligence Tools:** Tableau, Power BI, Looker
- **Cloud Platforms:** Azure, Google Cloud Platform, AWS
- **Optimization Solvers:** CPLEX, Gurobi (for allocation problems)
- **Marketing Tools:** Braze, Salesforce (for promotional coordination)

**Challenge (INT-003):**
"We have 15+ different Excel reports circulated weekly. There's no single source of truth. Different teams use different numbers, and we spend hours in meetings reconciling discrepancies."

**Integration Requirements:**
- **API connectivity** to source and destination systems
- **Data format translation** between system schemas
- **Authentication and security** meeting enterprise standards
- **Auditability** for compliance and troubleshooting

---

### TC-07: Data Latency & Freshness

**Source:** INT-003, INT-004
**Impact:** Forecast timeliness, reactive capability, system design

**Description:**
Data does not arrive instantaneously; latency between real-world events and data availability constrains system responsiveness.

**Observed Latencies:**
- **Store POS data:** 1-3 days to clean and reconcile (INT-003)
- **E-commerce data:** Separate pipeline from POS, additional delays
- **Inventory data:** 3-day lag for reconciled, clean data (INT-003)
- **Weather data:** Currently monthly updates, need weekly/daily (INT-004)
- **External data:** Variable, often weekly or monthly

**Requirement:**
The system must minimize impact of data latency on forecast accuracy through:
- **Nowcasting techniques** to estimate current state from lagged data
- **Expectation propagation** forward from last known state
- **Anomaly detection** to flag when data seems stale or incorrect

---

## Part 4: Scope Boundaries

Clear scope boundaries prevent scope creep and focus effort on high-value problems.

### SB-01: Focus on Demand Forecasting, Not Revenue Optimization

**Source:** INT-005
**Rationale:** Maintain manageable scope for independent study project

**In Scope:**
- Sales unit forecasting by SKU and location
- Demand drivers and influencing factors
- Seasonal and event-based patterns
- External factor incorporation

**Explicitly Out of Scope:**
- Revenue optimization and financial modeling
- Pricing strategy recommendations (prices are inputs, not outputs)
- Profit margin optimization
- Financial planning and budgeting

---

### SB-02: Focus on Pre-Season & In-Season Forecasting

**Source:** INT-001, INT-002, INT-003
**Rationale:** Address highest-pain planning phases

**Primary Focus:**
- **Pre-season planning:** Setting targets, initial buy quantities, allocation
- **In-season adjustments:** Replenishment, reallocation, responsive changes

**Lower Priority (Related but Not Primary):**
- **Markdown optimization:** Often owned by separate teams with different tools
- **Long-term strategic planning:** Multi-year assortment strategy

**Rationale:**
Pre-season and in-season forecasting errors have the most direct and immediate financial impact through stockouts, overstock, and misallocation.

---

### SB-03: Single Product Category Focus

**Source:** INT-005
**Rationale:** Different categories have fundamentally different forecasting dynamics

**Recommendation:**
Focus on ONE of the following retail categories:

- **Fashion Retail** (La Vie En Rose, Groupe Dynamite context)
  - High style/color variability
  - Social media influence
  - Rapid trend changes
  - Short product lifecycles

- **Seasonal Categories** (Canadian Tire outdoor/seasonal)
  - Weather-dependent demand
  - Event-based spikes
  - Inventory obsolescence risk

- **Consumer Packaged Goods / Grocery** (Walmart context)
  - High volume, low margin
  - Frequent purchase cycles
  - Promotion sensitivity

**Selected Focus (Recommended):**
Fashion retail or seasonal categories best align with event-based seasonality emphasis (FR-04) and provide richest research context for external factors.

---

### SB-04: Geographic Scope - North America

**Source:** INT-001, INT-002, INT-003, INT-004
**Rationale:** Interview base and data availability

**Geographic Coverage:**
- United States
- Canada

**Out of Scope:**
- International markets (Europe, Asia, Latin America)
- Global supply chain optimization
- International trade beyond US-Canada

**Consideration:**
All interviewed organizations operate primarily in North America. Data sources, economic indicators, and weather services are North America-focused.

---

### SB-05: Decision Support, Not Autonomous Automation

**Source:** INT-001, INT-005
**Rationale:** Maintain human judgment for high-stakes decisions

**Approach:**
The system provides **recommendations and scenario analysis**, not autonomous execution of business decisions.

**Rationale:**
- **Manual insights remain valuable** for exception handling (INT-005)
- **Business judgment required** for expensive decisions like large inventory transfers
- **High approval bar** exists for capital-intensive actions (INT-004)
- **Stakeholder buy-in** requires transparency and control

**Output Format:**
Recommendations with confidence levels, supporting data, and scenario comparisons. Humans make final decisions with system support.

---

## Part 5: User Success Criteria

Success criteria define measurable outcomes that validate solution value.

### USC-01: Improved Forecast Accuracy

**Source:** All interviews
**Measurement:** Forecast vs. actual sales comparison using industry-standard metrics

**Current Baseline Accuracy:**
- **Walmart (INT-002):** 60-85% varying by category
- **La Vie En Rose (INT-003):** 60% at style-level, 70% at category-level
- **General Industry:** 50-70% for new/fashion items, 70-85% for replenishment items

**Target:**
Measurable improvement over current baselines, with specific targets defined during technical design phase. Even 5-10 percentage point improvements translate to millions in inventory savings.

**Metric Recommendations:**
- Mean Absolute Percentage Error (MAPE)
- Weighted MAPE (higher-volume items weighted more heavily)
- Forecast bias (systematic over- or under-forecasting)
- Hit rate (percentage of forecasts within acceptable range)

---

### USC-02: Reduced Data Preparation Time

**Source:** INT-002, INT-003, INT-004, INT-005
**Measurement:** Hours per week spent on data cleaning and preparation

**Current Baseline:**
- **50% of total project time** (INT-005, INT-004)
- **10-20 hours per week** (INT-002 - Walmart)
- **15 hours per week** (INT-003 - La Vie En Rose)

**Target:**
Reduce manual data preparation to less than 20% of project time through automated pipelines (FR-09).

**Value Calculation:**
For a data analyst at $80K annual salary, reducing data prep from 50% to 20% of time frees up ~12 hours weekly or $30K annual value in redeployed productivity.

---

### USC-03: Better Inventory Allocation

**Source:** INT-001, INT-003
**Measurement:** Stockout frequency, overstock frequency, reallocation costs

**Current Pain Points:**
- Frequent misallocation (PP-015, PP-002)
- Expensive post-allocation redistribution (PP-003, PP-004)
- Stockouts causing lost sales
- Overstock requiring markdowns

**Target Outcomes:**
- **Reduced stockout events** by 20-30%
- **Reduced overstock** requiring markdown by 15-25%
- **Lower reallocation frequency and cost** by 30%+

**Financial Impact:**
Even modest improvements compound quickly. INT-003 reported $500K annual margin loss from late markdown decisions - better initial forecasts directly protect margin.

---

### USC-04: Faster Responsiveness to Changes

**Source:** INT-001, INT-004, INT-003
**Measurement:** Time from data availability to forecast update, scenario analysis turnaround time

**Current Gaps:**
- **Monthly model runs** vs. desired weekly (INT-004)
- **3-day data lag** prevents timely responses (INT-003)
- **No scenario testing capability** without breaking production (INT-004)

**Target Outcomes:**
- **Weekly forecast refresh minimum**, daily aspirational
- **Same-day scenario analysis** capability for what-if testing
- **Automated alerts** when demand deviates from forecast by >X%
- **Real-time dashboards** showing current forecast vs. actual trends

---

### USC-05: Reduced Markdown Losses

**Source:** INT-003
**Measurement:** End-of-season markdown depth and frequency

**Current Impact:**
$500K annual margin loss from late markdown decisions at a 250-store specialty fashion retailer (INT-003).

**Root Cause:**
Poor initial forecasts lead to overbuying, which isn't detected until late in season when markdown is the only option.

**Target Outcome:**
Better initial forecasts reduce overbuying, enabling earlier, shallower markdowns or avoiding markdowns entirely. Target 20-30% reduction in markdown-driven margin loss.

---

### USC-06: Reduced Firefighting Time

**Source:** INT-002, INT-003
**Measurement:** Hours per week spent on reactive problem-solving

**Current Baseline:**
- **6-18 hours per week** (INT-002 - Walmart)
- **12 hours per week** (INT-003 - La Vie En Rose)

**Definition:**
"Firefighting" is reactive problem-solving: addressing stockouts, explaining forecast errors, manually adjusting forecasts, and crisis meetings.

**Target Outcome:**
Proactive, accurate forecasting reduces reactive problems. Target 40-50% reduction in firefighting time through:
- Fewer stockout crises
- More trusted forecasts requiring fewer manual overrides
- Automated alerting for proactive intervention

---

### USC-07: Cross-Functional Alignment

**Source:** INT-002, INT-003
**Measurement:** Meeting time, forecast acceptance rate, override frequency

**Current Pain Points:**
- **6-12 hours per week in alignment meetings** (INT-002)
- **Forecasts treated as "suggestions"** rather than plans (INT-003)
- **Multiple conflicting forecasts** from different teams (INT-003)
- **High manual override rates** indicating lack of trust

**Target Outcomes:**
- **Single source of truth** that all teams reference
- **Trusted, interpretable outputs** reducing need for validation meetings
- **Reduced coordination overhead** by 40-50%
- **Lower override rates** indicating higher baseline trust

---

## Part 6: Requirements Traceability

Each functional requirement was directly linked to validated user pain points from interviews.

| Requirement | Pain Points Addressed | Interview Sources | Priority |
|-------------|----------------------|-------------------|----------|
| FR-01: Multi-Source Data Integration | PP-023, PP-033, PP-005 | INT-002, INT-004, INT-005 | High |
| FR-02: Store-Level Forecasting | PP-002, PP-009, PP-015 | INT-001, INT-002, INT-003, INT-004, INT-005 | High |
| FR-03: SKU-Level Forecasting | PP-001, PP-019 | INT-002, INT-003, INT-004 | High |
| FR-04: Event-Based Seasonality | PP-021, PP-014 | INT-004, INT-005 | High |
| FR-05: Continuous Learning | PP-006, PP-025, PP-029 | INT-001, INT-004 | High |
| FR-06: External Factor Integration | PP-005, PP-021, PP-030 | INT-001, INT-004, INT-005 | High |
| FR-07: Inventory Reallocation Support | PP-003, PP-032, PP-004 | INT-001, INT-003, INT-005 | Medium |
| FR-08: Omnichannel Coordination | PP-031 | INT-002, INT-003, INT-005 | Medium |
| FR-09: Automated Data Pipeline | PP-027, PP-023, PP-013, PP-010, PP-008 | INT-002, INT-003, INT-004, INT-005 | High |
| FR-10: Real-Time Processing | PP-025, PP-016 | INT-002, INT-003, INT-004 | Medium |
| FR-11: Interpretability | PP-018, PP-011 | INT-003, INT-004 | Medium |
| FR-12: Scenario Simulation | PP-022, PP-029 | INT-004, INT-005 | Medium |

**Priority Rationale:**
- **High Priority:** Requirements addressing multiple high-severity pain points across multiple interviews
- **Medium Priority:** Requirements addressing specific pain points or enabling higher-priority capabilities

---

## Part 7: Validation Checkpoints

To ensure requirements remain grounded in user reality, the following validation checkpoints are established:

### VC-01: Planning Team Deep Dive (INT-001)

**Stakeholder:** Planning Team Manager at national furniture retailer
**Timeline:** Upon MVP delivery or prototype demonstration
**Purpose:**
- Deep-dive into specific operational workflows
- Validate integration requirements with actual systems
- Establish performance benchmarks based on historical data
- Define detailed success criteria and acceptance tests

**Deliverable:**
Validation report confirming requirements alignment with operational reality or documenting necessary adjustments.

---

### VC-02: Expert Project Review (INT-005)

**Stakeholder:** Vaibhav Vishal (Groupe Dynamite, previously Walmart)
**Timeline:** Before final project submission
**Purpose:**
- Methodology validation from experienced practitioner perspective
- Scope appropriateness review
- Technical approach critique
- Industry relevance confirmation

**Format:**
Presentation of approach, findings, and solution design with feedback session.

---

### VC-03: Long-Term Collaboration Opportunity (INT-001)

**Stakeholder:** National furniture retailer (INT-001)
**Condition:** If MVP demonstrates sufficient value
**Opportunity:** Real-world deployment and testing with actual company data
**Timeline:** Beyond independent study project period

**Context:**
This represents potential transition from academic project to practical implementation, validating real-world applicability of the solution.

---

## Part 8: Summary Statistics

**Requirements Summary:**
- 12 Functional Requirements
- 10 Data Requirements
- 7 Technical Constraints
- 5 Scope Boundaries
- 7 User Success Criteria
- **Total: 41 distinct requirements and constraints**

**Validation Foundation:**
- Derived from 5 in-depth user interviews
- Traces to 33+ validated pain points
- Represents perspectives from:
  - 2 large mass merchandisers (Walmart, Canadian Tire)
  - 2 specialty fashion retailers (La Vie En Rose, Groupe Dynamite)
  - 1 national furniture retailer
- Combined experience: 40+ years in retail operations and analytics

**Coverage:**
- All functional requirements trace to specific pain points
- All data requirements support functional capabilities
- All technical constraints reflect real operational environments
- Scope boundaries validated by user recommendation (INT-005)

---

## Conclusion

This requirements document establishes a comprehensive, validated foundation for developing a retail demand forecasting solution. 

The requirements balance ambition with pragmatism: they reflect the ideal capabilities needed to transform retail forecasting (multi-source integration, continuous learning, real-time processing) while acknowledging real-world constraints (infrastructure costs, data latency, existing system integration complexity).

Key themes emerge across requirements:
1. **Granularity matters:** Store-level and SKU-level forecasting are non-negotiable
2. **Context is everything:** External factors, events, and multi-source data are critical
3. **Automation is essential:** 50% of time spent on data prep is unacceptable
4. **Trust requires transparency:** Interpretability is as important as accuracy
5. **Scale is a first-class concern:** Millions of forecasts weekly demand efficient algorithms

The scope boundaries (focus on demand forecasting, pre-season/in-season planning, single category, North America, decision support) create a manageable project while addressing the highest-value problems.

Success will be measured not just by technical metrics (forecast accuracy), but by operational impact (time savings, inventory optimization, markdown reduction) and user adoption (trust, reduced override rates, cross-functional alignment).

**Next Steps:**
1. Select specific product category focus (fashion retail recommended)
2. Develop technical approach that addresses functional requirements within constraints
3. Design solution architecture integrating all required data sources
4. Define specific accuracy targets and success metrics
5. Plan validation approach with identified stakeholders

---

**Document Status:** Complete
**Approval Required:** Project advisor, validation stakeholders
**Related Documents:**
- Component 1: Problem Validation (Pain Point Inventory)
- Component 2: Current State Analysis
- Component 4: Approach Validation
- Component 5: Success Metrics Definition
