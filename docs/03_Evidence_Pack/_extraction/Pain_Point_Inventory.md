# Pain Point Inventory

**Purpose:** Comprehensive extraction of all pain points identified across 5 user interviews
**Date Created:** October 2, 2025
**Source:** INT-001 through INT-005 interview notes

---

## Pain Point Table

| ID | Interview Source | Pain Point | Category | Severity | Impact | Frequency | Supporting Quote |
|---|---|---|---|---|---|---|---|
| **PP-001** | INT-001 | Inaccurate demand forecasting with traditional ML | Forecast Accuracy | 5 | Poor allocation → expensive redistribution | Ongoing | "Traditional numerical ML models don't provide enough accuracy and agility to predict demand" |
| **PP-002** | INT-001 | Location-specific demand prediction failures | Forecast Accuracy | 4 | Inventory misallocation across warehouses | Ongoing | "When forecasts are off, they must quickly reallocate inventory" |
| **PP-003** | INT-001 | Complex inventory redistribution decisions | Cost & Agility | 4 | Time-consuming optimization | Frequent | Cross-border complexity adds tariff/logistics overhead |
| **PP-004** | INT-001 | Cross-border transfer cost/time overhead | Cost | 3 | Increased operational costs | Per transfer | Canada-US transfers require tariff management |
| **PP-005** | INT-001 | Inability to factor external economic factors | Forecast Accuracy | 4 | Misses market condition impacts | Ongoing | Traditional models can't capture policy changes |
| **PP-006** | INT-001 | Lack of agility in forecast adjustments | Agility | 4 | Slow response to market changes | Ongoing | Static models require manual reconfiguration |
| **PP-007** | INT-002 | Forecast fragmentation across teams using different tools/views | Data Integration | 4 | 8-16 hrs/week wasted | Weekly | Multiple planning systems create conflicting views |
| **PP-008** | INT-002 | Supplier data quality and inconsistent lead time info | Data Quality | 4 | 4-10 hrs/week on reconciliation | Ongoing | Retail Link data requires extensive cleaning |
| **PP-009** | INT-002 | Difficulty mapping national assortments to local demand (localization) | Forecast Accuracy | 4 | 6-12 hrs/week on manual adjustments | Seasonal | Store-level preferences not captured in national plans |
| **PP-010** | INT-002 | Manual consolidation of Retail Link extracts and internal spreadsheets | Data Integration | 4 | 10-20 hrs/week | Daily | No single source of truth |
| **PP-011** | INT-002 | Long cross-functional meetings to solve allocation/assortment disagreements | Collaboration | 3 | 6-12 hrs/week | Weekly | Buying, supply, and merchandising teams lack alignment |
| **PP-012** | INT-002 | Out-of-stock emergencies and rush allocations | Inventory | 4 | 6-18 hrs/week firefighting | Weekly | Reactive rather than proactive inventory management |
| **PP-013** | INT-003 | Data consolidation across systems (e-commerce, POS, dashboards) | Data Integration | 5 | 10 hrs/week | Daily | "Reconciling inventory numbers between warehouse system and store systems - always discrepancies" |
| **PP-014** | INT-003 | Swimwear demand volatility due to weather dependency | Forecast Accuracy | 4 | 2 months/year of uncertainty | Seasonal | High fashion sensitivity to unpredictable factors |
| **PP-015** | INT-003 | Store allocation mismatches | Inventory | 4 | 5 hrs/week + stockouts/overstock | Weekly | Store clustering (A/B/C) too simplistic |
| **PP-016** | INT-003 | Late markdown decisions causing margin loss | Cost | 5 | $500K lost margin annually | Monthly | 3-day data lag prevents timely action |
| **PP-017** | INT-003 | Manual Excel model maintenance and formula breakage | Data Quality | 3 | 8 hrs/week | Daily | "Rebuilding Excel forecast models when someone breaks a formula - happens monthly" |
| **PP-018** | INT-003 | Cross-team alignment issues (merchandising vs operations) | Collaboration | 4 | 3 hrs/week | Weekly | "The merchandising team treats our forecasts like 'suggestions' until the numbers prove them wrong" |
| **PP-019** | INT-003 | New product performance unknowns | Forecast Accuracy | 4 | 20% forecast error on launches | Each launch | Limited ability to test before bulk orders |
| **PP-020** | INT-003 | Inventory reconciliation discrepancies between systems | Data Quality | 4 | Continuous reconciliation effort | Daily | Legacy systems don't sync properly |
| **PP-021** | INT-004 | Weather/seasonality shocks drive forecast misses | Forecast Accuracy | 5 | Lost sales or excess stock | Seasonal + ad hoc | "Monthly weather updates too coarse; need finer granularity" |
| **PP-022** | INT-004 | Inventory as lagging constraint to marketing plans | Integration | 4 | Sub-optimal promo/price decisions | Ongoing | "Inventory is a lagging factor—it helps to forecast inventory first, then layer marketing/pricing AI" |
| **PP-023** | INT-004 | Heavy multi-source data prep (POS, GA4, loyalty, StatsCan, competitor) | Data Integration | 4 | ~20 hrs/week (~50% of time) | Weekly | "We spend about half the week on data prep" |
| **PP-024** | INT-004 | Dealer vs company-operated complexity | Process | 3 | Slower reactions, more coordination | Ongoing | Different approval/PO cycles by ownership model |
| **PP-025** | INT-004 | Model frequency & infra cost constraints | Agility | 3 | Models run monthly vs desired weekly | Ongoing | Cost/latency reduces responsiveness to shocks |
| **PP-026** | INT-004 | High cost of inventory reallocation | Cost | 3 | Freight/ops costs limit flexibility | Ad hoc | Only done with strong business case |
| **PP-027** | INT-005 | Data cleaning consumes majority of time | Data Quality | 5 | 50%+ of total project time | Ongoing | "50% of the time was data cleaning - removing anomalies, making the data clean" |
| **PP-028** | INT-005 | Inventory optimization balance (overstock vs understock) | Inventory | 4 | Lost sales or excess costs | Ongoing | Avoiding both extremes requires accurate forecasting |
| **PP-029** | INT-005 | Manual interventions required in automated processes | Agility | 3 | Human insight generation needed | Regular | Some steps require business judgment between automation |
| **PP-030** | INT-005 | Uncontrollable factors management (unexpected events, trends) | Forecast Accuracy | 4 | Model performance degradation | Irregular | Events outside model scope cause failures |
| **PP-031** | INT-005 | Multi-channel complexity (online vs brick-and-mortar) | Integration | 4 | Coordination overhead | Ongoing | "There can be a connection between store sales and online sales - omnichannel" |
| **PP-032** | INT-005 | Store-to-store and warehouse-to-store transfer coordination | Inventory | 3 | Logistics complexity | Regular | Stock balancing across locations is manual |
| **PP-033** | INT-005 | Social media trend tracking for fashion retail | Data Integration | 3 | Fast-changing trends missed | Daily/Weekly | "Social media trends... fashion trends change weekly/daily and directly affect buying patterns" |

---

## Pain Point Categories Summary

### Forecast Accuracy (11 pain points)
- PP-001, PP-002, PP-005, PP-009, PP-014, PP-019, PP-021, PP-030
- **Severity Range:** 4-5
- **Key Theme:** Traditional ML insufficient; external factors not captured; weather/seasonality shocks; new product uncertainty

### Data Integration (8 pain points)
- PP-007, PP-010, PP-013, PP-023, PP-031, PP-033
- **Severity Range:** 3-5
- **Key Theme:** Multi-source data prep; system fragmentation; manual consolidation; omnichannel complexity

### Data Quality (5 pain points)
- PP-008, PP-017, PP-020, PP-027
- **Severity Range:** 3-5
- **Key Theme:** 50%+ time on cleaning; reconciliation issues; formula breakage; supplier data inconsistency

### Inventory Management (6 pain points)
- PP-012, PP-015, PP-028, PP-032
- **Severity Range:** 3-4
- **Key Theme:** Allocation mismatches; overstock/understock balance; transfer coordination; out-of-stock firefighting

### Cost (4 pain points)
- PP-004, PP-016, PP-026
- **Severity Range:** 3-5
- **Key Theme:** Cross-border overhead; late markdown losses ($500K); reallocation costs

### Agility (4 pain points)
- PP-006, PP-025, PP-029
- **Severity Range:** 3-4
- **Key Theme:** Static models; slow response; manual interventions needed; infrastructure constraints

### Collaboration/Process (4 pain points)
- PP-011, PP-018, PP-024
- **Severity Range:** 3-4
- **Key Theme:** Cross-functional alignment; team disagreements; ownership model complexity

### Integration (2 pain points)
- PP-003, PP-022
- **Severity Range:** 4
- **Key Theme:** Redistribution complexity; inventory-marketing disconnect

---

## High-Severity Pain Points (Severity 5)

| ID | Pain Point | Interview | Impact |
|---|---|---|---|
| **PP-001** | Inaccurate demand forecasting with traditional ML | INT-001 | Root cause of allocation failures |
| **PP-013** | Data consolidation across systems | INT-003 | 10 hrs/week wasted |
| **PP-016** | Late markdown decisions | INT-003 | $500K annual margin loss |
| **PP-021** | Weather/seasonality shocks | INT-004 | Lost sales or excess stock |
| **PP-027** | Data cleaning time burden | INT-005 | 50%+ of project time |

---

## Pain Point Cascade Analysis

### Primary Root Causes
1. **Traditional ML Limitations** (PP-001) → Location prediction failures (PP-002) → Inventory misallocation (PP-015) → Redistribution needs (PP-003) → Cross-border costs (PP-004)

2. **Data Integration Fragmentation** (PP-007, PP-010, PP-013) → Data quality issues (PP-008, PP-020, PP-027) → Time waste (50% on cleaning) → Slow response (PP-006, PP-025)

3. **Lack of External Factor Integration** (PP-005, PP-021, PP-030, PP-033) → Forecast misses → Inventory imbalance (PP-028) → Markdown losses (PP-016)

### Secondary Effects
- **Cross-functional friction** (PP-011, PP-018) stems from forecast inaccuracy (PP-001) and conflicting data views (PP-007)
- **Firefighting culture** (PP-012) results from reactive forecasting (PP-001, PP-006)
- **Manual workarounds** (PP-017, PP-029) compensate for system limitations

---

## Time Impact Summary

### Weekly Time Lost (from interviews)
- **INT-002 (Walmart):** 24-46 hrs/week across pain points
  - Data prep: 10-20 hrs
  - Forecast fragmentation: 8-16 hrs
  - Firefighting: 6-18 hrs

- **INT-003 (La Vie En Rose):** 38 hrs/week
  - Data consolidation: 10 hrs
  - Manual Excel work: 8 hrs
  - Allocation mismatches: 5 hrs
  - Firefighting: 12 hrs

- **INT-004 (Canadian Tire):** ~20 hrs/week
  - Data prep: ~20 hrs (50% of week)

### Annual Cost Impact
- **INT-003:** $500K margin loss from late markdowns (PP-016)
- **Cross-border transfers:** Variable but significant (PP-004, PP-026)

---

## Geographic/Industry Patterns

### Furniture Retail (INT-001)
- Long lead times (1 year planning)
- Cross-border complexity (US/Canada)
- Focus on location-based allocation

### Mass Retail (INT-002 - Walmart)
- Massive scale (10,000 stores, millions SKUs)
- Supplier coordination complexity
- System fragmentation across teams

### Fashion Retail (INT-003 - La Vie En Rose, INT-005 - Groupe Dynamite)
- High trend volatility (social media, weather)
- Seasonal event dependence
- New product uncertainty

### Multi-Banner Retail (INT-004 - Canadian Tire)
- Weather sensitivity (seasonal categories)
- Dealer vs corporate-operated complexity
- Multi-source data integration (loyalty, competitor, macro)

---

## Notes for Evidence Pack Development

### For Component 1 (Problem Validation):
- Use cascade analysis to show how root causes compound
- Highlight severity-5 pain points as primary justification
- Quantify time/cost impacts where available

### For Component 2 (User Research Synthesis):
- Group pain points by industry context
- Show patterns across all 5 interviews
- Use supporting quotes to validate themes

### For Component 3 (Requirements):
- Pain points PP-001, PP-005, PP-021, PP-030, PP-033 → Need for multi-source data integration
- Pain points PP-007, PP-010, PP-013, PP-027 → Need for automated data pipeline
- Pain points PP-006, PP-025, PP-029 → Need for adaptive/agile system
- Pain points PP-002, PP-009, PP-015 → Need for store-level forecasting

### For Component 4 (Approach Validation):
- PP-001 validates need for AI/LLM over traditional ML
- PP-005, PP-021, PP-030 validate multi-factor approach
- PP-006, PP-029 validate need for adaptive intelligence

---

**Status:** Phase 1 Extraction Complete
**Next Step:** Create Quote_Library.md and Requirements_Extract.md
