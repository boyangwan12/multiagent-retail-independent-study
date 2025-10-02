# Requirements Extract

**Purpose:** Comprehensive extraction of requirements and constraints from user interviews
**Date Created:** October 2, 2025
**Source:** INT-001 through INT-005 interview notes

---

## Functional Requirements

### FR-01: Multi-Source Data Integration
**Source:** INT-005, INT-004, INT-002
**Description:** System must integrate multiple heterogeneous data sources including:
- Historical sales data (POS)
- Weather data (granular, near-real-time preferred)
- Social media trends
- Inventory levels (real-time)
- Demographics (store-level, geographic)
- Seasonality markers (event-based)
- Competitor data
- Macro-economic indicators (StatsCan, etc.)
- Loyalty/CRM data
- Product placement data

**Derived from Pain Points:** PP-023, PP-033, PP-005

---

### FR-02: Store-Level Forecasting Granularity
**Source:** INT-001, INT-002, INT-003, INT-004, INT-005
**Description:** System must produce forecasts at individual store location level, not just regional or national aggregates

**Rationale:**
- Enables inventory reallocation between locations
- Supports localization of assortments
- Allows for demographic-specific predictions

**Derived from Pain Points:** PP-002, PP-009, PP-015

---

### FR-03: SKU-Level Forecasting
**Source:** INT-002, INT-003, INT-004
**Description:** System must forecast at individual SKU or style-color level

**Scale Requirements:**
- Walmart: Millions of SKUs
- Canadian Tire: ~250k active SKUs
- La Vie En Rose: 3,500 SKUs per season

**Derived from Pain Points:** PP-001, PP-019

---

### FR-04: Event-Based Seasonality Intelligence
**Source:** INT-005, INT-004
**Description:** System must recognize and forecast for specific seasonal events, not just general seasonal patterns:
- Black Friday
- Christmas
- Halloween
- Back-to-school
- Sale/clearance periods
- Weather events (snow/no-snow, heat waves)

**Quote:** "Seasonality can vary based on the sale on the product that comes in. It can be during festivals like Christmas or Halloween" (INT-005)

**Derived from Pain Points:** PP-021, PP-014

---

### FR-05: Continuous Learning & Adaptation
**Source:** INT-001, INT-004
**Description:** System must continuously learn from actual vs. forecasted performance and adapt predictions

**Features:**
- Closed-loop feedback mechanisms
- Performance penalty/correctness signals
- Feature/parameter auto-adjustment
- Real-time or near-real-time updates (not just monthly)

**Quote:** "Lightweight correctness/penalty features as a feedback mechanism" (INT-004)

**Derived from Pain Points:** PP-006, PP-025, PP-029

---

### FR-06: External Factor Incorporation
**Source:** INT-001, INT-004, INT-005
**Description:** System must factor in external economic and policy conditions:
- Tariff policy changes
- Economic conditions
- Competitor actions (especially Amazon)
- Weather shocks
- Macro trends (population, income, spend patterns)

**Derived from Pain Points:** PP-005, PP-021, PP-030

---

### FR-07: Inventory Reallocation Support
**Source:** INT-001, INT-003, INT-005
**Description:** System should support or enable inventory redistribution decisions:
- Identify shortage vs. surplus locations
- Suggest transfer routes (store-to-store, warehouse-to-store)
- Consider transfer costs and logistics
- Support cross-border transfers (US/Canada)

**Derived from Pain Points:** PP-003, PP-032, PP-004

---

### FR-08: Omnichannel Coordination
**Source:** INT-002, INT-003, INT-005
**Description:** System must account for interconnected sales channels:
- Brick-and-mortar stores
- E-commerce platforms
- Warehouse fulfillment
- Store fulfillment of online orders
- Cross-channel inventory visibility

**Quote:** "There can be a connection between store sales and online sales - omnichannel" (INT-005)

**Derived from Pain Points:** PP-031

---

### FR-09: Automated Data Pipeline & Cleaning
**Source:** INT-002, INT-003, INT-004, INT-005
**Description:** System must automate data preparation to reduce manual effort:
- Automated data extraction from multiple sources
- Data cleaning and anomaly removal
- Format standardization
- Reconciliation across systems
- Model-ready data output

**Current State:** 50% of project time spent on manual data cleaning (INT-005)

**Derived from Pain Points:** PP-027, PP-023, PP-013, PP-010, PP-008

---

### FR-10: Real-Time or Near-Real-Time Processing
**Source:** INT-002, INT-003, INT-004
**Description:** System should support rapid forecast updates and scenario testing:
- Reduce lag between data capture and forecast update
- Enable what-if scenario runs without breaking production
- Support weekly (ideally daily) re-forecasting cadence
- Trigger alerts on threshold deviations

**Current Gap:** Monthly model runs vs. desired weekly (INT-004)

**Derived from Pain Points:** PP-025, PP-016

---

### FR-11: Interpretability & Transparency
**Source:** INT-004, INT-003
**Description:** System must provide interpretable outputs and explanations:
- Visual dashboards
- Explainable predictions
- Feature importance visibility
- Confidence scores or ranges

**Context:** "Emphasis on interpretability" (INT-004) needed for stakeholder buy-in

**Derived from Pain Points:** PP-018, PP-011

---

### FR-12: Scenario Simulation Capability
**Source:** INT-005, INT-004
**Description:** System should enable business users to run what-if scenarios:
- Price/promotion impact testing
- Inventory level adjustments
- Weather event simulations
- Demand shock scenarios

**Previous Work:** "Built using Excel worksheets and Power BI - User inputs numbers → system generates scenario" (INT-005)

**Derived from Pain Points:** PP-022, PP-029

---

## Data Requirements

### DR-01: Historical Sales Data
**Source:** INT-005, INT-002, INT-003, INT-004
**Specification:**
- **Time Horizon:** 10+ years ideal (INT-005)
- **Granularity:** SKU-level, store-level, daily/weekly
- **Channels:** POS (in-store), e-commerce, wholesale
- **Attributes:** Sales units, revenue, margins, returns

---

### DR-02: Inventory Data
**Source:** INT-005, INT-004, INT-003
**Specification:**
- **Real-time or near-real-time** stock levels
- Store inventory, warehouse inventory, in-transit inventory
- SKU availability by location
- Stockout events tracking

---

### DR-03: Weather Data
**Source:** INT-004, INT-003, INT-005
**Specification:**
- **Geographic Granularity:** Store-level or FSA (Forward Sortation Area)
- **Frequency:** Prefer higher than monthly; ideally weekly or daily updates
- **Variables:** Temperature, precipitation, snow depth, severe weather events
- **Forecast Horizon:** Short-term (2-4 weeks) for responsive adjustments

**Current Gap:** "Monthly weather updates too coarse" (INT-004)

---

### DR-04: Seasonality/Event Markers
**Source:** INT-005, INT-004
**Specification:**
- Event calendar (Black Friday, Christmas, Halloween, back-to-school, etc.)
- Promotional periods
- Sale/clearance windows
- Holiday calendars by region

---

### DR-05: Demographic & Geographic Data
**Source:** INT-004, INT-001, INT-003
**Specification:**
- Population density
- Income levels
- Urban vs. rural classification
- Age distribution, household size
- Birth rates (for certain categories like baby products)
- Store clustering attributes (A/B/C stores)

**Example:** "StatsCan: population, income, spend, birth rates; rural/urban" (INT-004)

---

### DR-06: Social Media & Trend Data
**Source:** INT-005, INT-003
**Specification:**
- Fashion trend signals
- Social media mentions/sentiment
- Influencer impact
- Real-time or near-real-time updates (daily/weekly)

**Context:** "Fashion trends change weekly/daily and directly affect buying patterns" (INT-005)

---

### DR-07: Competitor Data
**Source:** INT-004
**Specification:**
- Competitor pricing
- Competitor promotional activity
- Market share trends
- Especially Amazon pricing/availability (INT-004)

---

### DR-08: Macro-Economic Indicators
**Source:** INT-001, INT-004
**Specification:**
- Economic growth indicators
- Consumer spending patterns
- Tariff/trade policy data
- Employment rates
- Inflation/CPI

---

### DR-09: Product Attributes
**Source:** INT-005, INT-003
**Specification:**
- Product category/subcategory
- Style, color, size attributes
- Product placement in stores (front vs. side)
- New product launch dates
- Product lifecycle stage

---

### DR-10: Supplier & Lead Time Data
**Source:** INT-002, INT-003, INT-001
**Specification:**
- Supplier ETAs (Estimated Time of Arrival)
- Manufacturing lead times
- Shipping schedules
- Cross-border logistics timelines
- Vendor agreements and constraints

---

## Technical Constraints

### TC-01: Omnichannel Architecture
**Source:** INT-002, INT-005
**Description:** System must support multi-channel retail operations including online sales, warehouse fulfillment, and store networks

**Implications:**
- Unified inventory view across channels
- Cross-channel demand influence modeling
- Fulfillment routing logic (warehouse, nearby store, current store)

---

### TC-02: Cross-Border Operations
**Source:** INT-001
**Description:** System must handle cross-border complexity for US/Canada operations

**Implications:**
- Tariff cost modeling
- Logistics time/cost for international transfers
- Currency considerations
- Regulatory/policy differences

---

### TC-03: Scalability Requirements
**Source:** INT-002, INT-004, pitch document (inferred)
**Description:** System must scale to:
- 10,000+ stores (Walmart scale)
- Millions of SKUs
- 15-20M loyalty customers
- Daily/weekly forecast refresh cycles

---

### TC-04: Infrastructure Cost Constraints
**Source:** INT-004
**Description:** Cloud infrastructure costs limit model run frequency

**Current Trade-off:** Monthly runs vs. desired weekly due to cost/volume balance

**Implication:** System should optimize for compute efficiency or enable cost-effective frequent runs

---

### TC-05: Dealer vs. Company-Operated Model Complexity
**Source:** INT-004
**Description:** For multi-banner retailers, system must handle different ownership models:
- Dealer-operated: ~12-month planning horizon, different approval cycles
- Company-operated: ~6-8 month planning horizon

**Implication:** Flexible PO-cycle abstraction layer needed

---

### TC-06: Integration with Existing Systems
**Source:** INT-002, INT-003, INT-004
**Description:** System must integrate with existing enterprise platforms:
- Retail Link (Walmart)
- Legacy ERP systems
- POS systems
- WMS (Warehouse Management Systems)
- Supplier portals
- BI/analytics platforms (Tableau, Power BI)
- Cloud platforms (Azure, GCP)
- Optimization solvers (CPLEX, Gurobi)
- Campaign tools (Braze)

**Challenge:** "15+ different Excel reports circulated weekly, no single source of truth" (INT-003)

---

### TC-07: Data Latency & Freshness
**Source:** INT-003, INT-004
**Description:** System must accommodate data lag:
- 3-day lag in clean store data (INT-003)
- E-commerce data comes separately from POS
- Weather updates monthly (current), need more frequent

**Requirement:** Minimize impact of data latency on forecast accuracy

---

## Scope Boundaries

### SB-01: Focus on Demand Forecasting, Not Revenue Optimization
**Source:** INT-005
**Description:** Project should focus on sales forecasting for specific SKUs at store level during seasonal events

**Explicitly Out of Scope (per INT-005):**
- Revenue optimization
- Finance modeling
- Pricing strategy (except as input factor)

**Quote:** "It's good to focus on one [domain]. It would be too much to cover all aspects across different areas like inventory, revenue, or finance."

---

### SB-02: Focus on Pre-Season & In-Season Forecasting
**Source:** INT-001, INT-002, INT-003
**Description:** Primary focus on:
- Pre-season planning (MFP/target setting, initial buy)
- In-season adjustments (replenishment, reallocation)

**Related but Lower Priority:**
- Markdown optimization (owned by different teams)
- Long-term strategic assortment planning

---

### SB-03: Specific Product Category (to be determined)
**Source:** INT-005
**Description:** Recommend focusing on ONE retail category:
- Fashion retail (La Vie En Rose, Groupe Dynamite context)
- CPG (Walmart grocery context)
- Seasonal categories (Canadian Tire outdoor/seasonal)
- Furniture (INT-001 context)

**Recommendation:** Fashion retail or seasonal categories align best with event-based seasonality focus

---

### SB-04: Geographic Scope
**Source:** INT-001, INT-002, INT-003, INT-004
**Description:** North American focus (US/Canada) based on interview context

**Consideration:** All interviewed companies operate primarily in North America

---

### SB-05: Inventory Allocation Support, Not Full Automation
**Source:** INT-001, INT-005
**Description:** System should SUPPORT inventory reallocation decisions, not fully automate them

**Rationale:**
- Manual insights still valuable (INT-005)
- Business judgment needed for exceptions
- High approval bar for expensive reallocations (INT-004)

**Output:** Recommendations and scenario analysis, not autonomous execution

---

## User Success Criteria

### USC-01: Improved Forecast Accuracy
**Source:** All interviews
**Current Baseline:**
- 60-85% varying by category (INT-002 - Walmart)
- 60% style-level, 70% category-level (INT-003 - La Vie En Rose)

**User Expectation:** Measurable improvement over traditional ML baselines

**Measurement:** Forecast vs. actual sales; MAPE or similar metrics (specific targets in Technical Design Doc)

---

### USC-02: Reduced Data Preparation Time
**Source:** INT-002, INT-003, INT-004, INT-005
**Current Baseline:**
- 50% of project time (INT-005, INT-004)
- 10-20 hrs/week (INT-002)
- 15 hrs/week (INT-003)

**User Expectation:** Automated pipeline reduces manual data prep to <20% of time

---

### USC-03: Better Inventory Allocation
**Source:** INT-001, INT-003
**Current Pain:**
- Frequent misallocation (PP-015, PP-002)
- Expensive redistribution (PP-003, PP-004)

**User Expectation:**
- Reduced stockouts
- Reduced overstock
- Lower reallocation frequency/cost

---

### USC-04: Faster Responsiveness to Changes
**Source:** INT-001, INT-004, INT-003
**Current Gap:**
- Monthly model runs vs. desired weekly (INT-004)
- 3-day data lag prevents timely action (INT-003)
- Lack of agility (INT-001)

**User Expectation:**
- Real-time or near-real-time adjustments
- Rapid scenario testing without breaking production
- Alert-driven responses to threshold deviations

---

### USC-05: Reduced Markdown Losses
**Source:** INT-003
**Current Impact:** $500K annual margin loss from late markdown decisions

**User Expectation:** Better initial forecasts → fewer late markdowns → margin protection

---

### USC-06: Reduced Firefighting Time
**Source:** INT-002, INT-003
**Current Baseline:**
- 6-18 hrs/week (INT-002)
- 12 hrs/week (INT-003)

**User Expectation:** Proactive forecasting reduces reactive problem-solving

---

### USC-07: Cross-Functional Alignment
**Source:** INT-002, INT-003
**Current Pain:**
- 6-12 hrs/week in alignment meetings (INT-002)
- Forecasts treated as "suggestions" (INT-003)

**User Expectation:**
- Single source of truth
- Trusted, interpretable outputs
- Reduced coordination overhead

---

## Validation Checkpoints

### VC-01: Planning Team Access (INT-001)
**Timeline:** Upon MVP delivery
**Stakeholder:** Planning Team Manager at furniture retail company
**Purpose:**
- Deep-dive into specific workflows
- Validate integration requirements
- Establish performance benchmarks
- Define success criteria

---

### VC-02: Expert Project Review (INT-005)
**Stakeholder:** Vaibhav Vishal (Groupe Dynamite/Walmart)
**Purpose:** Project review before submission
**Focus:** Methodology validation, scope appropriateness, technical approach

---

### VC-03: Long-term Collaboration Opportunity (INT-001)
**Condition:** If MVP demonstrates value
**Opportunity:** Real-world deployment and testing with actual company data
**Timeline:** Beyond independent study period

---

## Requirements Traceability Matrix

| Requirement | Pain Points Addressed | Interview Sources | Priority |
|---|---|---|---|
| FR-01: Multi-Source Data Integration | PP-023, PP-033, PP-005 | INT-002, INT-004, INT-005 | High |
| FR-02: Store-Level Forecasting | PP-002, PP-009, PP-015 | INT-001, INT-002, INT-003 | High |
| FR-03: SKU-Level Forecasting | PP-001, PP-019 | INT-002, INT-003, INT-004 | High |
| FR-04: Event-Based Seasonality | PP-021, PP-014 | INT-004, INT-005 | High |
| FR-05: Continuous Learning | PP-006, PP-025, PP-029 | INT-001, INT-004 | High |
| FR-06: External Factor Integration | PP-005, PP-021, PP-030 | INT-001, INT-004 | High |
| FR-07: Inventory Reallocation Support | PP-003, PP-032, PP-004 | INT-001, INT-003, INT-005 | Medium |
| FR-08: Omnichannel Coordination | PP-031 | INT-002, INT-003, INT-005 | Medium |
| FR-09: Automated Data Pipeline | PP-027, PP-023, PP-013, PP-010 | All interviews | High |
| FR-10: Real-Time Processing | PP-025, PP-016 | INT-002, INT-003, INT-004 | Medium |
| FR-11: Interpretability | PP-018, PP-011 | INT-003, INT-004 | Medium |
| FR-12: Scenario Simulation | PP-022, PP-029 | INT-004, INT-005 | Medium |

---

## Notes for Evidence Pack Development

### For Component 1 (Problem Validation):
- Requirements FR-01 through FR-06 directly address high-severity pain points
- FR-09 addresses the most time-consuming pain point (data cleaning)

### For Component 3 (Requirements & Constraints):
- All functional requirements trace to user pain points
- Data requirements reflect actual sources mentioned in interviews
- Technical constraints are realistic based on interview context
- Scope boundaries prevent scope creep per INT-005 warning

### For Component 4 (Approach Validation):
- FR-05 (Continuous Learning) validates adaptive AI approach
- FR-06 (External Factors) validates multi-source intelligence
- FR-11 (Interpretability) validates need for transparent AI
- User success criteria focus on business outcomes, not technical metrics

### For Component 5 (Success Metrics):
- Success criteria quantified where possible (time savings, accuracy baselines)
- Validation checkpoints established with real stakeholders
- Long-term collaboration opportunity demonstrates user confidence

---

**Total Requirements:** 12 Functional + 10 Data + 7 Technical Constraints + 4 Scope Boundaries + 7 Success Criteria = 40 requirements
**Status:** Phase 1 Extraction Complete
**Next Step:** Begin Phase 2 (Document Creation)
