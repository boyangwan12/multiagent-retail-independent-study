# Week 1 Updates

## Target Companies

| Company | Why They're Interesting |
|---------|------------------------|
| **Groupe Dynamite**<br/>(Dynamite & Garage) | Big fashion retailer based in Montréal. Digital + physical stores; Gen Z / millennial audience; supply chain, inventory, staffing, online-omni challenges. |
| **SSENSE** | High-end e-commerce + physical presence; fashion + global market. Their insight on tech, UX, fulfillment, brand partnerships would be very valuable. (Though likely harder to get access.) |
| **Salesfloor Inc.**<br/>**Lightspeed Commerce** | These are more tech / platform providers / enablers in retail space. Interviewing them gives insight into what retailers ask for, pain in features, what is possible. |
| **Simons**<br/>(La Maison Simons) | Mid- to higher-end fashion + home decor; they also focus on experience in stores, loyalty, aesthetics, omni-channel. |
| **Lululemon** | High-performance apparel / athletic wear. Strong brand, global presence. |
| **Vessi** | Combines style + functional tech (waterproof knit); strong online first presence and expanding into physical retail. |
| **La Vie en Rose** | Lingerie, swimwear, loungewear: comfort, fit, design are critical. Lots of stores in Canada, HQ in Montréal. They also have a digital presence, outlet/concept stores, expansion outside Canada. |

---

## Potential Contacts

| Name | Role / Job Title | Company | Industry | Location | Cohort |
| --- | --- | --- | --- | --- | --- |
| **David Ruiz Bermudez** | Functional Business Analyst | Metro Inc. | Retail (Grocery) | Montreal, QC | MMA-OL1 |
| **Maria Nino Tavera** | Senior Product Operation Analyst | ALDO | Retail (Fashion) | Montreal, QC | MMA-OL2 |
| **Onur Erkin Sucu** | Senior Data Scientist | ALDO Group | Retail (Fashion) | Toronto, ON | MMA1 |
| **Xin Rui (Leah) Ma** | Digital Merchandising Analyst | BestBuy | Retail (Electronics) | Vancouver, BC | MMA1 |
| **Yiming (Vivian) Yang** | Data Scientist II | Loblaws | Retail (Grocery) | Toronto, ON | MMA2 |
| **Sophie Courtemanche-Martel** | Analytical Developer | Altitude Sports | Retail (Outdoor / E-Commerce) | Montreal, QC | MMA3 |
| **Yi Kuang** | Business Analyst II | Canadian Tire Corporation | Retail (General Merchandise) | Montreal, QC | MMA4 |
| **Yulin Hong** | Replenishment Analyst | Dollarama | Retail (Discount) | Montreal, QC | MMA4 |
| **Arpit Nagpal** | Senior Data Scientist | Canadian Tire Corporation | Retail (General Merchandise) | Toronto, ON | MMA4 |
| **Vaibhav Vishal** | Business Intelligence Developer | Groupe Dynamite | Retail (Fashion) | Toronto, ON | MMA4 |
| **Yashica Na** | Senior Data Analyst | SSENSE | Retail (Fashion / E-commerce) | Toronto, ON | MMA4 |
| **Kritika Nayyar** | Manager, Customer Insights | Loblaws | Retail (Grocery) | Toronto, ON | MMA6 |
| **Cheuk Yee (Chelsea) Hon** | Business Intelligence Lead | L'Oréal | Consumer Products (Cosmetics) | Toronto, ON | MMA4 |
| **Aishwarya Rao** | Analyst | Mattel | Consumer Products (Toys) | Toronto, ON | MMA4 |
| **Nehal Jain** | Analytics & Insights Manager, Product Supply | Procter & Gamble | Consumer Products (FMCG) | Toronto, ON | MMA4 |
| **Ammad Sohail** | Data Engineer | Procter & Gamble | Consumer Products (FMCG) | Toronto, ON | MMA6 |
| **David Gao** | Business Analyst | Article | Furniture / E-commerce | Toronto, ON | MMA6 |
| **Hao Hao Duong** | Data Scientist | Philip Morris International | Consumer Products (Tobacco) | Toronto, ON | MMA6 |

---

## Retail Operations Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     RETAIL OPERATIONAL WORKFLOW                      │
└─────────────────────────────────────────────────────────────────────┘

1. PLANNING (Pre-Season)
   ┌──────────────┐
   │ MFP Planning │ ──► Set Sales, Margin, Inventory Targets
   └──────┬───────┘     (12-18 months ahead)
          │
          ▼
   ┌──────────────┐
   │  Forecasting │ ──► Predict demand by SKU/Store/Category
   └──────┬───────┘     (Statistical + ML models)
          │
          ▼
   ┌──────────────┐
   │    Buying    │ ──► Create purchase orders based on forecast
   └──────┬───────┘
          │
2. EXECUTION (In-Season)
          │
          ▼
   ┌──────────────┐
   │  Allocation  │ ──► Distribute inventory to stores/channels
   └──────┬───────┘     (Push initial + Pull replenishment)
          │
          ▼
   ┌──────────────┐
   │    Sales     │ ──► Track actual vs plan performance
   └──────┬───────┘     (POS + E-commerce data)
          │
          ▼
   ┌──────────────┐
   │Replenishment │ ──► Restock based on sales velocity
   └──────┬───────┘
          │
3. OPTIMIZATION (Continuous)
          │
          ▼
   ┌──────────────┐
   │  Markdowns   │ ──► Optimize pricing to clear inventory
   └──────┬───────┘     (Time/Performance triggers)
          │
          ▼
   ┌──────────────┐
   │  Analytics   │ ──► Monitor KPIs & adjust plans
   └──────┬───────┘     (Dashboards + Reports)
          │
          └──────► FEEDBACK LOOP to Planning
```

### Key Process Interactions

**Planning → Execution Flow:**
- MFP sets financial guardrails → Forecasting predicts units → Buying procures inventory
- Allocation distributes to channels → Sales captures demand signals
- Replenishment maintains stock levels → Markdowns clear excess

**Cross-Functional Dependencies:**
```
Merchants ←→ Planners ←→ Allocation ←→ Supply Chain
    ↑            ↑            ↑            ↑
    └────────────┴────────────┴────────────┘
                     Finance
```

### Technology & Data Flow
```
Source Systems          Analytics Layer         Decision Systems
─────────────          ───────────────         ────────────────
POS/E-commerce   →     Data Warehouse    →     Planning Tools
ERP/Inventory    →     BI/Reporting      →     Allocation Engine
Supply Chain     →     Forecasting Models →     Pricing/Markdown
```

## Key ideas we want to learn: 
this is not the actual interview questions but are information we want to get from them

### 1. Forecasting & Demand Planning

- **Current Practices**
  - How do you currently forecast demand (tools, models, intuition)?
  - At what granularity do you forecast (banner/country, region, store, SKU, category)?

- **Frequency & Accuracy**
  - How often are forecasts updated (weekly, monthly, seasonally)?
  - What's the average forecast accuracy you achieve, and how do you measure it?

- **Challenges**
  - What are the biggest challenges (e.g., promotions, new product launches, seasonality, supply chain delays)?
  - How do you handle anomalies (outliers, black swan events, weather, holidays)?

---

### 2. Inventory Management & Allocation

- **Allocation Strategy**
  - How do you decide how much inventory to allocate to each store or region?
  - Do you use rules-based allocation, manual overrides, or AI-driven tools?

- **Replenishment**
  - How do you manage replenishment from DC → stores?
  - Do you cluster stores by performance/foot traffic/region for allocation decisions?

- **Pain Points**
  - What are your current pain points (stockouts, overstocks, high carrying costs, markdowns)?

---

### 3. Merchandise Financial Planning (MFP)

- **Planning Framework**
  - What planning horizon do you use (pre-season 12 months, in-season reforecasts)?
  - At what levels do you plan (company, banner, channel, category, subclass)?

- **Target Setting**
  - How do you set sales, receipts, markdowns, margins, and inventory targets?
  - Do you create multiple versions (Working Plan, Initial Plan, Forecast, Last Year)?

- **Friction Points**
  - Where do you face the most friction (time rollups, approvals, cross-functional alignment)?

---

### 4. Markdowns & Promotions

- **Strategy**
  - How do you decide when and how much to markdown?
  - Do you use a fixed cadence (e.g., end of season) or dynamic strategies (AI, elasticity models)?

- **Approval Process**
  - What's your threshold for approving a markdown (GM$ lift, sell-through, aging)?
  - How do you balance eComm vs. store markdown pricing?

- **Metrics**
  - What % of products end up needing markdowns, and how deep are they on average?

---

### 5. Technology & Tools

- **Current Stack**
  - Which systems are you using today (SAP, Oracle, Aptos, Excel, custom tools)?
  - What works well, and what doesn't (integration, user interface, flexibility)?

- **Shadow IT**
  - How much do you rely on Excel "shadow systems" outside of official tools?

- **AI Adoption**
  - How open is your team to AI-driven recommendations vs. human judgment?
  - What kind of dashboards/reports are most useful for decision making?

---

### 6. Cross-Functional Alignment

- **Collaboration**
  - How do merchants, planners, allocation, supply chain, and finance collaborate?
  - Where do misalignments usually happen (sales targets vs. receipts, forecast vs. reality)?

- **Governance**
  - How are approvals managed (top-down vs. bottom-up planning)?
  - Which KPIs matter most at executive vs. planner level (GM$, GM%, sales, inventory turns)?

---

### 7. Future State / Wish List

- **Automation Opportunities**
  - If you could automate one part of planning/forecasting, what would it be?
  - What would a "dream" planning or forecasting solution look like for your team?

- **Success Metrics**
  - How would you measure the success of a new tool (fewer hours spent, higher forecast accuracy, reduced markdowns)?

- **Barriers to Adoption**
  - What's holding you back from adopting more advanced solutions (budget, data quality, resistance to change)?

---