# Scope Definition Guide: Demand Forecasting & Inventory Allocation System

This guide helps you define your project scope by answering a series of questions. Your answers determine the problem you're solving and what data you need to build the system.

---

## Building a Generic System vs Specific Use Case

**IMPORTANT:** You have two goals that might seem contradictory:
1. **Build a GENERIC system** (works for furniture, fashion, CPG, etc.)
2. **Demonstrate with SPECIFIC use case** (need concrete examples to validate)

**The Solution:** Build generic architecture, validate with specific parameters.

### **How to Stay Generic:**

```yaml
# ❌ BAD: Hard-coding for fashion only
class DemandAgent:
    def forecast(self, product):
        # Hard-coded: assumes 12-week season
        weeks = 12
        # Hard-coded: assumes new products
        use_similar_item_matching()

# ✅ GOOD: Parameterized for any retail
class DemandAgent:
    def __init__(self, config):
        self.season_length = config['season_length']  # Could be 12 weeks, 6 months, continuous
        self.new_product_ratio = config['new_product_ratio']  # Could be 5%, 80%

    def forecast(self, product):
        if self.season_length == "continuous":
            return self.time_series_forecast(product)
        else:
            return self.seasonal_forecast(product)
```

**Key Principle:** The system **behavior adapts based on configuration**, not hard-coded for one industry.

---

### **Strategy: Generic System + Specific Validation**

**Phase 1: Build Generic (Your Research Contribution)**
```python
# Generic 3-agent architecture
class RetailAllocationSystem:
    def __init__(self, config):
        self.demand_agent = DemandAgent(config)
        self.inventory_agent = InventoryAgent(config)
        self.pricing_agent = PricingAgent(config)
        self.orchestrator = Orchestrator(config)

    # Works for ANY retail by reading config
```

**Phase 2: Validate with Specific Use Case (MVP/Demo)**
```yaml
# config_archetype1_fashion.yaml
industry: "Fashion Retail (Archetype 1)"
season_length: 12 weeks
new_product_ratio: 70-80%
replenishment_cadence: weekly
# ... fashion-specific parameters

# config_archetype2_furniture.yaml ⭐ MVP FOCUS
industry: "Furniture Retail (Archetype 2)"
season_length: 26 weeks
new_product_ratio: 20-30%
replenishment_cadence: bi-weekly
# ... furniture-specific parameters

# config_archetype3_cpg.yaml
industry: "CPG (Archetype 3)"
season_length: continuous
new_product_ratio: 5-10%
replenishment_cadence: daily
# ... CPG-specific parameters
```

**Your Contribution:**
- ✅ **Generic architecture** (3 agents + orchestrator)
- ✅ **Parameter-driven behavior** (agents adapt to config)
- ✅ **Validated on Archetype 2** (50 stores, 50 SKUs, 26-week season, furniture retail)
- ✅ **Extensible to other retail** (just change config, same code)

---

### **Do You NEED to Pick an Industry for MVP?**

**Short Answer: YES, for validation. NO, for architecture.**

**What You Define for MVP:**
- One set of parameter values to test with
- One mock dataset to demonstrate functionality
- One success metric to validate against

**What Stays Generic:**
- Agent logic (adapts based on parameters)
- System architecture (same 3 agents for all retail)
- Data structures (flexible schemas)

**Recommended Approach:**

```
┌──────────────────────────────────────────────────────┐
│ LAYER 1: GENERIC ARCHITECTURE (Your Core Research)  │
├──────────────────────────────────────────────────────┤
│ • 3-agent system (Demand, Inventory, Pricing)       │
│ • Orchestrator for coordination                     │
│ • Parameter-driven behavior                         │
│ • Configurable for any retail sector                │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ LAYER 2: PARAMETER CONFIGURATION (Industry-Agnostic)│
├──────────────────────────────────────────────────────┤
│ • season_length: [4 weeks | 12 weeks | continuous]  │
│ • new_product_ratio: [5% | 20% | 80%]              │
│ • lead_time: [1 week | 6 weeks | 6 months]         │
│ • ... (all parameters are configurable)             │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ LAYER 3: VALIDATION USE CASE (Pick ONE to Demo)     │
├──────────────────────────────────────────────────────┤
│ Option A: Fashion Retail (12 weeks, 80% new)        │
│ Option B: Furniture Retail (6 months, 20% new)      │
│ Option C: CPG (continuous, 5% new)                  │
│                                                      │
│ You pick ONE to generate mock data and validate     │
└──────────────────────────────────────────────────────┘
```

**Example: How Your Thesis Would Present This**

**Chapter 1: Problem Statement**
> "Retailers across industries face demand forecasting and inventory allocation challenges. While specifics vary (fashion has 80% new products, CPG has 5%), the core problem is universal: predict demand for products and allocate inventory to locations to maximize profitability."

**Chapter 2: Solution Architecture**
> "We propose a generic 3-agent system that adapts to different retail contexts through parameterization. The same architecture serves fashion, furniture, and CPG by adjusting behavior based on configuration."

**Chapter 3: Implementation & Validation**
> "To validate our approach, we implement the system for **Archetype 2: Stable Catalog Retail (furniture)** with parameters: 26-week season, 50 stores, 50 SKUs, 20-30% new products. We generate synthetic data matching furniture retail patterns..."

**Chapter 4: Results**
> "The system achieved <XX%> MAPE on furniture retail validation. The generic architecture can be reconfigured for Archetype 1 (fashion: 12-week seasons, 70-80% new products) or Archetype 3 (CPG: continuous replenishment) without code changes."

**Chapter 5: Generalization**
> "We demonstrate generalizability by showing how the same system handles fashion, furniture, and CPG use cases with only parameter changes (see Appendix A: Configuration Examples)."

---

### **Answer to Your Question:**

**Q: "Do I have to define the industry, or can I stay generic?"**

**A: Do BOTH:**

1. **Architecture: Generic**
   - Don't hard-code "fashion" anywhere
   - Use parameters like `season_length`, `new_product_ratio`
   - Agent logic adapts based on config

2. **Validation: Specific**
   - Pick ONE industry for MVP (recommendation: **Fashion**)
   - Generate mock data for that industry
   - Demonstrate system works for that use case

3. **Thesis/Paper: Show Generalization**
   - Include section showing "how to configure for furniture"
   - Include section showing "how to configure for CPG"
   - Prove generic architecture by showing multiple configs

**You DON'T need to implement for all industries. You DO need to design so it COULD work for all.**

---

### **Practical Decision for You:**

**For Your Independent Study MVP:**

**Option 1: Pick Archetype 2 (Stable Catalog) for Validation** ✅ **SELECTED**
- **Why:** Moderate complexity problem, addresses evidence pack pain points (PP-001, PP-002, PP-015, PP-028)
- **Generic:** Architecture works for any retail archetype
- **Specific:** Validate with Archetype 2 parameters (furniture retail, 26-week season)
- **Thesis:** "We validate on furniture, but design is generalizable to fashion/CPG"

**Option 2: Build Fully Generic, No Specific Validation** ❌ Risky
- **Why:** Hard to validate without concrete use case
- **Problem:** Reviewers will ask "does it actually work?"
- **Risk:** Generic but unproven

**Option 3: Implement for ALL Archetypes** ❌ Too Much Scope
- **Why:** 3x the mock data, 3x the validation
- **Problem:** Scope creep for independent study
- **Better:** Save for future work

**Recommended Path:**
1. **Design:** Generic 3-agent architecture (works for any retail)
2. **Implement:** Parameterized system (config-driven)
3. **Validate:** Archetype 2 (Stable Catalog - Furniture Retail, 26-week season)
4. **Demonstrate Generalizability:** Show how same system adapts to Archetypes 1 & 3

**MVP Focus: Archetype 2 - Stable Catalog Retail** ✅ Selected
- **Why:** Moderate complexity (not as volatile as fashion, not as simple as CPG)
- **Example:** Furniture retail (Pottery Barn, West Elm)
- **Parameters:** 26-week season, 50 stores, 50 SKUs, 20-30% new products
- **Generic:** Architecture works for any retail archetype
- **Specific:** Validate with Archetype 2 parameters
- **Thesis:** "We validate on furniture, but design is generalizable to fashion/CPG"

---

## Understanding Parameter Types: User Input vs Agent Decisions

**CRITICAL DISTINCTION:** Not all parameters are "questions to answer." Some are:
- **User Configuration** - You define these (your business context)
- **Agent Decisions** - The agents calculate/optimize these

### **Parameter Classification:**

| Parameter Type | Who Decides? | Examples | Why |
|----------------|-------------|----------|-----|
| **🔧 User Configuration** | **You define** | Industry, season length, store count, lead time | Business constraints you can't change |
| **🤖 Agent Decisions** | **Agents calculate** | How much to allocate per store, when to markdown, reallocation moves | System optimizes based on data |
| **📊 Success Metrics** | **You define targets** | Target accuracy 75%, sell-through 85% | Your business goals |
| **⚙️ System Tuning** | **You or Agents** | Hold-back %, safety stock %, reallocation threshold | Can be configured OR learned |

---

## Part 1: Guided Questionnaire - Define Your Problem Scope

Answer these questions to define what problem you're solving. We'll explain each question and provide examples.

**Note:** Only questions marked **🔧 USER INPUT** need answers. Parameters marked **🤖 AGENT DECISION** are what the system will calculate for you.

---

### **Q1: What industry are you building this for?** 🔧 **USER INPUT**

**Why we need this:** Different industries have fundamentally different inventory challenges. This determines which demand patterns, external factors, and business constraints apply.

**Decision Type:** User Configuration - This defines your business domain.

**Options & Examples:**

| Industry | Characteristics | Example Companies |
|----------|----------------|-------------------|
| **Fashion Retail** | Seasonal collections, trend-driven, high new product ratio | Zara, H&M, La Vie En Rose |
| **Furniture Retail** | Longer lifecycles, bulky inventory, showroom model | IKEA, Ashley Furniture, Wayfair |
| **Consumer Packaged Goods (CPG)** | Continuous replenishment, stable demand, promotional cycles | Grocery stores, convenience stores |
| **Electronics** | Product refresh cycles, rapid obsolescence, high value | Apple Store, Best Buy |
| **Sporting Goods** | Seasonal categories, event-driven demand | Dick's Sporting Goods, REI |

**Your Answer:** ________________

---

### **Q2: What specific product category within that industry?** 🔧 **USER INPUT**

**Why we need this:** Even within an industry, categories behave differently. Outdoor furniture is seasonal; dining room furniture is year-round. This affects your forecasting approach.

**Decision Type:** User Configuration - Defines what products you're forecasting.

**Examples by Industry:**

**Fashion Retail:**
- Women's apparel (dresses, tops, bottoms)
- Lingerie & intimates
- Swimwear (highly seasonal)
- Accessories (bags, jewelry)
- Footwear

**Furniture Retail:**
- Outdoor/patio furniture (seasonal: Spring-Summer)
- Living room furniture (stable year-round)
- Bedroom furniture (stable year-round)
- Office furniture (back-to-school seasonality)

**CPG:**
- Dairy products (short shelf life, continuous)
- Snacks & beverages (stable with promotional spikes)
- Seasonal items (holiday-specific)

**Your Answer:** ________________

**Why this matters:** Swimwear has a 10-week season; bedroom furniture sells year-round. This changes `season_length`, `prediction_horizon`, and forecasting methods.

---

### **Q3: How long is the selling period for these products?** 🔧 **USER INPUT**

**Parameter Name:** `season_length`

**Why we need this:** This determines if you're solving a "fixed season" problem (allocate once, limited adjustments) or "continuous replenishment" (ongoing flow).

**Decision Type:** User Configuration - Your business/product lifecycle determines this.

**Options & What They Mean:**

| Season Length | What It Means | Industry Examples | Agent Behavior |
|---------------|---------------|-------------------|----------------|
| **4-6 weeks** | Very short season, fast fashion | Zara trend items, swimwear | Aggressive allocation, daily updates, limited reorder window |
| **10-14 weeks** | Standard fashion season | Spring/Fall collections | Weekly updates, planned markdown, similar-item forecasting |
| **6 months** | Long seasonal category | Outdoor furniture (Mar-Aug) | Monthly updates, reorder possible, weather-sensitive |
| **1 year+** | Stable catalog items | Quality furniture, core products | Quarterly updates, replenishment focus |
| **Continuous** | No season end | Grocery staples, basics | Time-series replenishment, perpetual reorder |

**Example:**
- **Spring fashion collection:** `12 weeks` (Jan-Mar selling period)
- **Outdoor patio furniture:** `24 weeks` (Mar-Aug, 6 months)
- **Milk in grocery store:** `continuous` (never ends)

**Your Answer:** ________________

**Impact on agents:**
- **Short season (6 weeks):** Demand agent uses trend signals, Inventory agent reallocates aggressively
- **Continuous:** Demand agent uses time-series patterns, Inventory agent uses reorder points

---

### **Q4: How far ahead do you need to forecast demand?** 🔧 **USER INPUT**

**Parameter Name:** `prediction_horizon`

**Why we need this:** This determines how far into the future the Demand Agent must predict. Longer horizons = more uncertainty.

**Decision Type:** User Configuration - Based on your lead time and planning needs.

**Options & What They Mean:**

| Prediction Horizon | When to Use | Uncertainty Level | Example |
|-------------------|-------------|-------------------|---------|
| **1-4 weeks** | Replenishment, short-term planning | Low (near-term visible) | Grocery weekly orders |
| **12 weeks** | Full season allocation | Medium | Fashion Spring season |
| **6 months** | Seasonal category planning | High | Outdoor furniture season |
| **1 year** | Annual strategic planning | Very High | New store inventory planning |

**Typical Pattern:** `prediction_horizon` ≈ `season_length`

**Example:**
- **Fashion 12-week season:** Forecast all 12 weeks at start (can't reorder from factory mid-season)
- **CPG continuous:** Forecast next 4 weeks (can reorder weekly, don't need to see far ahead)

**Your Answer:** ________________

**Why this matters:** If your lead time is 6 months (fashion), you must forecast 6+ months ahead just to place the order. If lead time is 1 week (CPG), you only need 2-4 weeks ahead.

---

### **Q5: How often will you update your forecast?** ⚙️ **USER OR AGENT**

**Parameter Name:** `forecast_cadence`

**Why we need this:** How frequently the Demand Agent re-runs predictions based on new sales data.

**Decision Type:** System Tuning - You can set this (e.g., "weekly"), OR the agent can learn optimal cadence based on forecast stability.

**Options & What They Mean:**

| Cadence | When to Use | Example Scenario | Why |
|---------|-------------|------------------|-----|
| **Daily** | High volatility, fast changes | Fast fashion, e-commerce flash sales | Trends change daily, need real-time updates |
| **Weekly** | Standard seasonal retail | Fashion collections, furniture | Sales patterns clear after 7 days |
| **Bi-weekly** | Moderate stability | Mid-market furniture | Balance cost vs reactivity |
| **Monthly** | Stable demand, long planning | Core catalog items, annual planning | Less volatility, monthly business reviews |

**Important:** `forecast_cadence` ≠ `prediction_horizon`

**Example:**
- **Prediction horizon:** 12 weeks (how far ahead)
- **Forecast cadence:** Weekly (how often you update that 12-week forecast)

**Analogy:** Weather forecast for next 7 days (horizon), updated every morning (cadence).

**Your Answer:** ________________

**Why this matters:** Weekly updates let you react to week 1 sales before week 2 starts. Monthly updates mean you live with week 1 forecast for 4 weeks before adjusting.

---

### **Q6: How long from ordering to receiving inventory?** 🔧 **USER INPUT**

**Parameter Name:** `lead_time`

**Why we need this:** Determines if you can correct mistakes mid-season or must "get it right" upfront.

**Decision Type:** User Configuration - This is a real business constraint (supplier lead time).

**Options & What They Mean:**

| Lead Time | Industry Example | Implication | Agent Strategy |
|-----------|------------------|-------------|----------------|
| **1-2 weeks** | Domestic CPG, nearby suppliers | Can quickly reorder if wrong | Lower safety stock, accept forecast errors |
| **6-8 weeks** | Domestic furniture, fast fashion | Limited mid-season correction | Moderate safety stock, weekly monitoring |
| **3-6 months** | Overseas fashion, complex manufacturing | No mid-season rescue | High safety stock, must forecast accurately |
| **6-12 months** | Custom furniture, long procurement | One-shot decision | Very high safety stock, extensive planning |

**Real Examples:**
- **Zara fast fashion:** 2-4 weeks (can adjust mid-season)
- **Traditional fashion:** 6 months from design → China → stores
- **IKEA furniture:** 6-8 weeks (Vietnam/China manufacturing)
- **Grocery store:** 1 week (local distribution)

**Your Answer:** ________________

**Why this matters:**
- **6-month lead time:** Must forecast perfectly in October for March-May season (no second chances)
- **1-week lead time:** Forecast roughly, adjust weekly based on actual sales

---

### **Q7: How many retail locations do you have?** 🔧 **USER INPUT**

**Parameter Name:** `store_count`

**Why we need this:** Determines complexity of allocation problem. More stores = more allocation decisions, more reallocation options, but also more complexity.

**Decision Type:** User Configuration - You know how many stores you have.

**Options & What They Mean:**

| Store Count | Scale | Allocation Complexity | Example |
|-------------|-------|----------------------|---------|
| **1-10 stores** | Small chain | Simple manual allocation possible | Local boutique chain |
| **10-50 stores** | Mid-size (MVP scale) | Need clustering (A/B/C), systematic allocation | Regional specialty retailer |
| **50-200 stores** | Large regional | Multi-cluster strategy, zone-based | La Vie En Rose (200 stores) |
| **200-1000+ stores** | National/International | Advanced clustering, localization critical | Zara (1,670 stores), IKEA (480 stores) |

**For MVP/Research Project:** **50 stores** is ideal
- Large enough to demonstrate clustering
- Small enough to compute and visualize
- Realistic for mid-market retailers

**Your Answer:** ________________

**Why this matters:**
- **5 stores:** Can manually allocate, don't need ML
- **50 stores:** Need clustering (group into A/B/C), benefits from agent system
- **500 stores:** Must have automated allocation, can do micro-targeting

---

### **Q8: How many different products (SKUs) do you need to forecast?** 🔧 **USER INPUT**

**Parameter Name:** `sku_count`

**Why we need this:** Determines scale of forecasting problem and data requirements.

**Decision Type:** User Configuration - Your catalog/assortment size.

**Options & What They Mean:**

| SKU Count | Scale | Forecast Approach | Example |
|-----------|-------|-------------------|---------|
| **100-500 SKUs** | Small category or single product line | Individual SKU forecasting feasible | Swimwear only, single furniture category |
| **500-2,000 SKUs** | Mid-size category (MVP scale) | Clustering + individual forecasting | Women's dresses, outdoor furniture |
| **2,000-10,000 SKUs** | Full department or multi-category | Hierarchical forecasting (category → SKU) | Full apparel assortment, full furniture catalog |
| **10,000+ SKUs** | Full store assortment | Must use attribute-based methods at scale | Full department store, IKEA catalog |

**Important:** If product has variations (color, size), each combination = 1 SKU
- **Example:** 1 dress style × 5 colors × 5 sizes = 25 SKUs

**For MVP/Research Project:** **1,000 SKUs** is ideal
- Demonstrates scalability
- Manageable computation
- Realistic for one season's new products

**Your Answer:** ________________

**Why this matters:**
- **100 SKUs:** Can manually review each forecast
- **1,000 SKUs:** Need automated forecasting, exception-based human review
- **10,000 SKUs:** Must rely on agent recommendations, only review outliers

---

### **Q9: What percentage of your products are NEW (no sales history)?** 🔧 **USER INPUT**

**Parameter Name:** `new_product_ratio`

**Why we need this:** This is the CORE CHALLENGE. New products = cold-start problem. This determines if you need similar-item matching or can use time-series forecasting.

**Decision Type:** User Configuration - You know your product refresh rate.

**Options & What They Mean:**

| New Product Ratio | Industry Type | Forecasting Challenge | Method Needed |
|------------------|---------------|----------------------|---------------|
| **0-10%** | Stable catalog (CPG, core furniture) | Easy - use historical patterns | Time-series models (ARIMA, etc.) |
| **10-30%** | Moderate refresh (furniture, basics) | Medium - mix of history + similarity | Hybrid: time-series + similar-item |
| **30-60%** | Regular seasonal updates | Hard - significant cold-start | Attribute-based, similar-item matching |
| **60-90%** | Fashion, fast fashion | Very Hard - mostly new each season | Must use product attributes, trends |

**Real Examples:**
- **Grocery staples:** 5% new (same milk, bread every week)
- **IKEA furniture:** 20% new (80% returning catalog items)
- **Fashion retailer:** 80% new (each season has mostly new designs)
- **Zara fast fashion:** 90%+ new (constant product rotation)

**Your Answer:** ________________

**Why this matters:**
- **5% new:** Can use historical sales data for 95% of products (easier problem)
- **80% new:** Must find similar products from history and use attributes (hard problem, requires ML)

**This is the KEY parameter that makes your research valuable!** If new_product_ratio is high, you're solving a harder, more interesting problem.

---

### **Q10: Can you replenish/reorder inventory during the season?** 🔧 **USER INPUT**

**Parameter Name:** `reorder_window`

**Why we need this:** Determines if Inventory Agent can correct allocation mistakes mid-season.

**Decision Type:** User Configuration - Based on your lead_time vs season_length (calculated from Q3 and Q6).

**Options & What They Mean:**

| Reorder Window | When Possible | Impact on Strategy | Example |
|---------------|---------------|-------------------|---------|
| **Never** | One-time allocation only | Must get initial allocation perfect | Fashion (6-month lead time exceeds season) |
| **Once mid-season** | Limited reorder opportunity | Strategic hold-back, monitor week 1-3 closely | Furniture with 6-week lead time in 24-week season |
| **Weekly** | Frequent replenishment | Lower initial allocation, react to demand | CPG with local suppliers |
| **Daily** | Continuous flow | Just-in-time, minimal forecasting needed | E-commerce dropship |

**Calculation:** Can you reorder if `lead_time` < `remaining season length`?

**Example:**
- **Fashion:** Lead time 6 months, season 12 weeks → **Cannot reorder** (6 months > 3 months remaining)
- **Furniture:** Lead time 6 weeks, season 24 weeks → **Can reorder once** at week 8 (6 weeks < 16 weeks remaining)
- **CPG:** Lead time 1 week, continuous season → **Can reorder weekly**

**Your Answer:** ________________

**Why this matters:**
- **No reorder:** Inventory Agent must allocate 100% upfront (high risk)
- **Weekly reorder:** Inventory Agent can allocate 60%, keep 40% at DC, react to week 1 sales (lower risk)

---

### **Q11: What are you trying to optimize? (Success Metrics)** 📊 **USER TARGETS**

**Parameter Names:** `target_forecast_accuracy`, `target_sell_through`, `target_markdown_rate`, `target_stockout_rate`

**Why we need this:** Defines what "success" means. Different goals = different agent behavior.

**Decision Type:** Success Metrics - You set the targets, agents optimize to achieve them.

**Pick Your Primary Goals (choose 2-3):**

| Goal | Success Metric | Target Value | When to Prioritize | Trade-off |
|------|---------------|--------------|-------------------|-----------|
| **Accurate forecasting** | Forecast accuracy | 75-85% | Research/academic focus | May not optimize revenue |
| **Maximize revenue** | Sell-through % at full price | 85%+ | High-margin products | Risk of stockouts |
| **Minimize waste** | Markdown % of revenue | <15% | Low-margin, perishable | May sacrifice some revenue |
| **Avoid stockouts** | Stockout rate | <3% | Customer satisfaction critical | Higher inventory costs |
| **Optimize margins** | Gross margin % | Industry-dependent | Profitability focus | Balances revenue vs cost |

**Example Scenarios:**

**Fashion Retailer:**
- Primary: `sell_through: 85%+` (sell at full price)
- Secondary: `markdown_rate: <13%` (minimize discounts)
- Acceptable: `stockout_rate: <5%` (some stockouts OK to avoid excess)

**Grocery Store:**
- Primary: `stockout_rate: <2%` (must have product available)
- Secondary: `waste: <3%` (perishables)
- Acceptable: `forecast_accuracy: 80%` (less critical if restocking fast)

**Your Answers:**
- Primary goal: ________________
- Target value: ________________
- Why this goal: ________________

---

## Part 2: Understanding Mock Data Needs

Based on your answers above, you now need to generate **synthetic data** to run the system. Here's what data you need and why:

---

### **Mock Dataset #1: Historical Sales Data**

**Why you need it:** The Demand Agent learns seasonal patterns and finds similar products by analyzing past sales.

**What to generate:**

| Data Element | Purpose | Example |
|-------------|---------|---------|
| **Past product sales** | Learn seasonal curves (what week peaks?) | "Pink Floral Dress sold 920 units over 12 weeks: [45, 78, 115, ...] |
| **Sales by store** | Learn which stores sell more | "Store A1 sold 52 units, Store C1 sold 9 units" |
| **Product attributes** | Find similar items for new products | "Pink Floral Dress: {style: floral, color: pink, price: 79, category: dress}" |

**How much history?**
- **Fashion (80% new products):** Generate 3 past seasons × 200-300 products = 600-900 historical SKUs
- **Furniture (20% new products):** Generate 2-3 years × 100 products = 200-300 historical SKUs
- **CPG (5% new):** Generate 1-2 years × 50 products = 50-100 historical SKUs (most products have real history)

**Example JSON:**
```json
{
  "sku_id": "SKU-11234",
  "name": "Pink Floral Dress",
  "season": "Spring 2025",
  "total_units_sold": 920,
  "weekly_sales": [45, 78, 115, 125, 110, 98, 85, 72, 60, 48, 42, 42],
  "by_store": {
    "A1": 52,
    "A2": 48,
    "B1": 28,
    "C1": 9
  },
  "attributes": {
    "style": "floral",
    "color": "pink",
    "category": "dress",
    "price": 79,
    "fabric": "cotton"
  }
}
```

---

### **Mock Dataset #2: Store Attributes**

**Why you need it:** The Inventory Agent groups stores into clusters (A/B/C) to allocate different amounts to different store types.

**What to generate:**

| Data Element | Purpose | Example |
|-------------|---------|---------|
| **Store clustering** | Group similar stores together | "Store A1 is cluster A (high volume)" |
| **Store performance** | Determine how much to allocate | "Store A1 avg 200 units/week, Store C1 avg 30 units/week" |
| **Store demographics** | Localize assortment (optional for MVP) | "Store A1: urban, high-income, age 25-40" |

**How many stores?** Based on your answer to Q7
- **MVP recommendation:** 50 stores
  - 15 A stores (high volume)
  - 25 B stores (medium volume)
  - 10 C stores (low volume)

**Example JSON:**
```json
{
  "store_id": "A1",
  "cluster": "A",
  "type": "Urban flagship",
  "avg_weekly_volume": 200,
  "location": {
    "city": "Toronto",
    "type": "urban",
    "climate_zone": "cold"
  },
  "demographics": {
    "income_level": "high",
    "age_range": "25-40",
    "population_density": "high"
  },
  "capacity": {
    "sqft": 3000,
    "max_inventory_units": 500
  }
}
```

---

### **Mock Dataset #3: Product Catalog (New Products)**

**Why you need it:** These are the NEW products you're trying to forecast (no sales history). The Demand Agent will find similar historical products based on attributes.

**What to generate:**

| Data Element | Purpose | Example |
|-------------|---------|---------|
| **Product attributes** | Match to similar historical products | "Red Floral Dress: {style: floral, color: red, price: 89}" |
| **Costs/pricing** | Pricing Agent needs this for markdown decisions | "COGS: $22.50, Retail: $89" |

**How many products?** Based on your answer to Q8
- **MVP recommendation:** 1,000 new SKUs
  - If `new_product_ratio = 80%`: These are 80% of your catalog
  - If `new_product_ratio = 20%`: These are 20% of your catalog

**Example JSON:**
```json
{
  "sku_id": "SKU-12345",
  "name": "Red Floral Dress",
  "season": "Spring 2026",
  "attributes": {
    "style": "floral",
    "color": "red",
    "category": "dress",
    "price": 89,
    "fabric": "cotton",
    "sleeve": "short",
    "length": "midi"
  },
  "costs": {
    "cogs": 22.50,
    "wholesale": 45.00,
    "retail": 89.00,
    "margin": 66.50
  },
  "variations": {
    "sizes": ["XS", "S", "M", "L", "XL"],
    "total_skus": 5
  },
  "is_new_product": true,
  "similar_to": "SKU-11234"
}
```

---

### **Mock Dataset #4: External Factors**

**Why you need it:** Weather, trends, events affect demand. The Demand Agent uses these as inputs to adjust forecasts.

**What to generate:**

| Data Element | When to Use | Example |
|-------------|-------------|---------|
| **Weather data** | Fashion, outdoor furniture | "Week 1: 15°C, Week 2: 18°C, Week 3: Cold snap 5°C" |
| **Trend signals** | Fashion, trendy products | "Week 1: 'floral' trend score 1.15 (+15%)" |
| **Event calendar** | All retail | "Week 3: Valentine's Day (+20% demand)" |

**How many weeks?** Based on your `prediction_horizon` (Q4)
- **12-week season:** Generate 12 weeks of data
- **24-week season:** Generate 24 weeks of data

**Example JSON:**
```json
{
  "week": 1,
  "date": "2026-01-01",
  "weather": {
    "avg_temperature_celsius": 15,
    "precipitation": "low",
    "anomaly": false
  },
  "trends": {
    "floral": 1.15,
    "red": 1.05,
    "midi_length": 0.95
  },
  "events": []
}
```

---

### **Mock Dataset #5: Operational Costs**

**Why you need it:** The Inventory Agent uses these to calculate ROI of moving inventory. The Pricing Agent uses these to set discounts.

**What to generate:**

| Data Element | Purpose | Example |
|-------------|---------|---------|
| **Transfer cost per unit** | Calculate reallocation ROI | "$5 to move 1 unit between stores" |
| **Markdown options** | Pricing Agent's discount choices | "Can discount 25%, 40%, or 50%" |
| **Reallocation budget** | Constraint on total moves | "$2,000 total budget for all reallocations this season" |

**Example JSON:**
```json
{
  "transfer_cost_per_unit": 5,
  "transfer_fixed_cost": 50,
  "markdown_depth_options": [0.25, 0.40, 0.50],
  "reallocation_budget": {
    "total_season": 2000,
    "per_move_max": 500
  },
  "markdown_triggers": {
    "week_6": {"threshold": 0.60, "discount": 0.25},
    "week_10": {"threshold": 0.40, "discount": 0.50}
  }
}
```

---

## Summary: Your Scope Definition Workflow

### **Step 1: Answer 11 Questions (Problem Definition)**
1. Industry? → ________________
2. Category? → ________________
3. Season length? → ________________
4. Prediction horizon? → ________________
5. Forecast cadence? → ________________
6. Lead time? → ________________
7. Store count? → ________________
8. SKU count? → ________________
9. New product ratio? → ________________
10. Reorder window? → ________________
11. Success metrics? → ________________

### **Step 2: Generate 5 Mock Datasets**
1. **Historical Sales:** ___ products × ___ seasons
2. **Store Attributes:** ___ stores (A/B/C clusters)
3. **Product Catalog:** ___ new SKUs
4. **External Factors:** ___ weeks of weather/trends
5. **Operational Costs:** Transfer costs, markdown options

### **Step 3: Validate Your Scope**
- [ ] Is your problem realistic? (matches real retail scenarios)
- [ ] Is it challenging enough? (high `new_product_ratio` = harder = more interesting)
- [ ] Is it feasible for MVP? (50 stores, 1,000 SKUs = manageable)
- [ ] Can you generate the mock data? (all 5 datasets)

---

## Recommended MVP Scope (If Unsure)

**Suggested Starting Point: Fashion Retail - Spring Season**

```yaml
# Problem Definition
industry: "Fashion Retail"
category: "Women's Seasonal Apparel (Dresses)"
season_length: 12 weeks
prediction_horizon: 12 weeks
forecast_cadence: weekly
lead_time: 6 months
store_count: 50
sku_count: 1000
new_product_ratio: 80%
reorder_window: never (lead time > season)
target_forecast_accuracy: 75%
target_sell_through: 85%
target_markdown_rate: <13%

# Mock Data Needs
historical_products: 200 products × 3 seasons = 600 historical SKUs
stores: 50 (15 A, 25 B, 10 C)
new_products: 1000 SKUs
external_data: 12 weeks
operational_costs: transfer_cost $5, markdown [25%, 40%, 50%]
```

**Why this scope is good for MVP:**
- ✅ Challenging (80% new products = cold-start problem)
- ✅ Manageable (50 stores, 1,000 SKUs = computable)
- ✅ Realistic (matches real fashion retailers)
- ✅ Generalizable (can extend to furniture, CPG later)
- ✅ Research-worthy (solving hard forecasting problem)

---

**Ready to define your scope? Fill in the 11 questions above!**

---

## Appendix: What Do The Agents Actually Decide?

You answered 11 questions above to **configure the system**. Now here's what the **agents decide/calculate** for you:

### **🤖 Demand Forecasting Agent Decisions:**

| What It Decides | Based On | Example Output |
|----------------|----------|----------------|
| **Total demand per SKU** | Similar product history, attributes | "Red Floral Dress will sell 1,000 units over 12 weeks" |
| **Weekly demand pattern** | Seasonal curves from history | Week 1: 50, Week 2: 80, ..., Week 4: 140 (peak) |
| **Demand per store** | Store clustering, historical performance | Store A1: 45 units, Store B1: 22 units, Store C1: 8 units |
| **Size/variant distribution** | Historical size mix | XS: 10%, S: 25%, M: 35%, L: 20%, XL: 10% |
| **Forecast updates** | Actual sales vs forecast variance | "Week 1 sold 30% above forecast → increase weeks 2-12" |
| **Confidence intervals** | Uncertainty based on newness | P10: 750 units, P50: 1,000 units, P90: 1,300 units |

**You DON'T decide:** How many units to forecast. The agent calculates this.

---

### **📦 Inventory Agent Decisions:**

| What It Decides | Based On | Example Output |
|----------------|----------|----------------|
| **Manufacturing quantity** | Demand forecast + safety stock | "Order 1,150 units (1,000 forecast + 15% safety stock)" |
| **Initial allocation per store** | Store clustering + demand forecast | Store A1: 18 units, Store B1: 12 units, Store C1: 6 units |
| **Hold-back amount at DC** | Uncertainty level, reorder capability | "Keep 520 units (45%) at DC, allocate 630 (55%) to stores" |
| **When to replenish** | Sell-through rate, remaining forecast | "Week 2: Send +12 units to Store A1 (sold 5/18 in week 1)" |
| **Reallocation decisions** | ROI calculation: transfer cost vs markdown savings | "Move 4 units from Store C3 to A1: Cost $20, Save $176 → DO IT" |
| **Consolidation timing** | End-of-season inventory levels | "Week 10: Pull inventory from 30 stores → 15 stores + outlet" |

**You DON'T decide:** Where to allocate inventory or how much per store. The agent calculates this based on forecast.

---

### **💰 Pricing Agent Decisions:**

| What It Decides | Based On | Example Output |
|----------------|----------|----------------|
| **When to markdown** | Sell-through thresholds you set (Q11) | "Week 6: 47% sell-through (target 60%) → trigger 25% markdown" |
| **Markdown depth** | Excess inventory amount, weeks remaining | "178 units excess, 6 weeks left → 25% off clears 90% of excess" |
| **Selective pricing** | Store-level performance | "A stores: full price ($89), B/C stores: 25% off ($67)" |
| **Price elasticity impact** | Historical response to discounts | "At 25% off, expect +40% demand lift" |
| **Clearance timing** | Final inventory levels, season end | "Week 10: 290 units remain → 50% off for all stores" |

**You DON'T decide:** Exact markdown timing or which stores get discounts. Agent calculates based on performance data.

---

### **⚙️ Parameters YOU Can Configure OR Let Agents Decide:**

Some parameters are flexible - you can either:
- **Set them yourself** (fixed value)
- **Let the agent learn/optimize** (adaptive)

| Parameter | If You Set It | If Agent Decides | Recommendation |
|-----------|---------------|------------------|----------------|
| **Hold-back %** | "Always hold 45% at DC" | Agent adjusts based on new_product_ratio | **Let agent decide** (adapts to uncertainty) |
| **Safety stock %** | "Always 15% buffer" | Agent adjusts based on forecast accuracy | **Let agent decide** (learns from errors) |
| **Reallocation threshold** | "Move if variance >30%" | Agent learns ROI threshold from outcomes | **Start with your rule, let agent refine** |
| **Forecast cadence** | "Update weekly" | Agent triggers update when variance >10% | **You set** (operational constraint) |
| **Markdown triggers** | "Week 6 if <60% sell-through" | Agent learns optimal timing from outcomes | **You set targets, agent decides timing** |

**Example: Hold-back Strategy**

**Option A - You Decide:**
```yaml
hold_back_percentage: 45%  # Fixed value
```
System always holds 45% at DC regardless of product uncertainty.

**Option B - Agent Decides:**
```yaml
hold_back_strategy: "adaptive"
agent_calculates_based_on:
  - new_product_ratio
  - forecast_confidence_interval
  - reorder_window_availability
```
Agent calculates:
- New product (no history) → 60% hold-back
- Similar item found (80% match) → 40% hold-back
- Existing product (has history) → 20% hold-back

**Recommended Approach:** Let agent decide hold-back % based on uncertainty.

---

### **Summary: Who Decides What?**

```
┌─────────────────────────────────────────────────────────┐
│ YOU CONFIGURE (Inputs)                                   │
├─────────────────────────────────────────────────────────┤
│ • Industry & Category                                    │
│ • Season length, Lead time                               │
│ • Store count, SKU count                                 │
│ • New product ratio                                      │
│ • Success metric targets                                 │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ AGENTS CALCULATE (Decisions)                            │
├─────────────────────────────────────────────────────────┤
│ 🔮 Demand Agent:                                        │
│    • How many units will sell                           │
│    • Weekly demand curve                                │
│    • Store-level demand                                 │
│                                                          │
│ 📦 Inventory Agent:                                     │
│    • Manufacturing quantity                             │
│    • Allocation per store                               │
│    • When to replenish/reallocate                       │
│                                                          │
│ 💰 Pricing Agent:                                       │
│    • When to markdown                                   │
│    • How much to discount                               │
│    • Which stores get discounts                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ SYSTEM MEASURES AGAINST YOUR TARGETS                    │
├─────────────────────────────────────────────────────────┤
│ • Forecast accuracy vs 75% target                       │
│ • Sell-through vs 85% target                            │
│ • Markdown rate vs <13% target                          │
│ • Stockout rate vs <3% target                           │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** You define the **problem and constraints**. The agents figure out the **optimal decisions** within those constraints.

**Example Workflow:**

1. **You configure:** "Fashion retail, 12-week season, 50 stores, 1,000 SKUs, 80% new products, 6-month lead time"
2. **Demand Agent calculates:** "Red Floral Dress: 1,000 units total, peak week 4, Store A1 needs 45 units"
3. **Inventory Agent calculates:** "Order 1,150 units, hold 520 at DC, allocate 18 to A1, 12 to B1, 6 to C1"
4. **Week 1 happens:** Store A1 sells 5 units (above forecast 2)
5. **Inventory Agent decides:** "Send +12 more units from DC to A1"
6. **Week 6 happens:** 47% sell-through (target 60%)
7. **Pricing Agent decides:** "Markdown B/C stores 25% off, keep A stores full price"
8. **System measures:** Achieved 94.7% sell-through, 12.8% markdown rate ✓ Beats targets!
