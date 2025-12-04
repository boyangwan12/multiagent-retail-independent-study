# Quote Library

**Purpose:** Organized collection of key quotes from user interviews
**Date Created:** October 2, 2025
**Source:** INT-001 through INT-005 interview notes and transcripts

---

## Theme 1: Forecast Accuracy Challenges

### Traditional ML Limitations

> "Traditional numerical ML models don't provide enough accuracy and agility to predict demand"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Describing current forecasting approach and why it fails

---

> "They want to adopt AI/LLMs to improve prediction accuracy, instead of only traditional machine learning models"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Magic wand question - desired solution direction

---

### Forecast Accuracy Metrics

> "Forecast Accuracy: 60-85% varying by category per item and location. Must measure by SKU per store."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Current performance levels across massive scale

---

> "Forecast Accuracy: 60% at style level, 70% at category level"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Fashion retail performance metrics

---

### Weather and Seasonality Impact

> "Seasonality is the lowest-hanging fruit—we stress it across categories."

**Source:** INT-004 (Data Scientist, Canadian Tire)
**Context:** Identifying primary forecast driver

---

> "Weather/seasonality shocks drive forecast misses [...] Monthly weather updates too coarse; need finer granularity"

**Source:** INT-004 (Data Scientist, Canadian Tire)
**Context:** Pain point - severity 5

---

> "Seasonality can vary based on the sale on the product that comes in. It can be during festivals like Christmas or Halloween, or periods where there are heavy discounts just to get rid of the inventories."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Defining seasonality as event-driven, not just weather

---

---

## Theme 2: Data Integration & Quality

### Data Preparation Time Burden

> "50% of the time was data cleaning - removing anomalies, making the data clean."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Previous work experience in SE Asia CPG forecasting

---

> "We spend about half the week on data prep, ~10 hours with the business, ~10 hours on the model and visuals."

**Source:** INT-004 (Data Scientist, Canadian Tire)
**Context:** Weekly time breakdown - 20 hrs/week on data prep alone

---

> "Data Prep: 10-20 hrs/week in pulling POS, promos, supplier data, and cleaning Retail Link extracts."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Time breakdown showing massive data integration effort

---

> "Data Prep: 15 hrs/week"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Time spent on data consolidation across systems

---

### System Fragmentation and Reconciliation

> "Reconciling inventory numbers between warehouse system and store systems - always discrepancies"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Biggest time waster - system synchronization issues

---

> "Manual consolidation of Retail Link extracts and the internal spreadsheets."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Biggest time waster despite having advanced systems

---

> "15+ different Excel reports circulated weekly, no single source of truth, constant reconciliation issues"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Reporting chaos despite investment in analytics

---

### Multi-Source Data Complexity

> "There are a lot of factors... weather, seasonality, inventory, historical data, even social media trends... demographic data, product placement in stores."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Comprehensive list of data sources needed for accurate forecasting

---

> "From 100 columns, we used to figure out which metrics are correlated to sales using Spearman and Pearson correlation models."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Feature selection methodology from previous work

---

---

## Theme 3: Inventory Management & Allocation

### Reallocation Complexity

> "When forecasts are off, they must quickly reallocate inventory"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Describing pain cascade from poor forecasts

---

> "Inventory is a lagging factor—it helps to forecast inventory first, then layer marketing/pricing AI."

**Source:** INT-004 (Data Scientist, Canadian Tire)
**Context:** Recognizing inventory as constraint to marketing decisions

---

### Localization Challenges

> "Difficulty mapping national assortments to local demand (localization)"

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Pain point - 6-12 hrs/week on manual adjustments

---

> "Initial allocation based on store clustering (A/B/C stores by volume), manual adjustments for new store openings, Quebec stores get different mix than rest of Canada"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Current allocation method - too simplistic

---

### Omnichannel Coordination

> "There can be a connection between store sales and online sales - omnichannel. Orders can be dispatched from warehouse or nearby stores if the current store doesn't have stock."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Multi-channel inventory complexity

---

---

## Theme 4: Business Impact & Consequences

### Margin and Cost Impact

> "$500K lost margin"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Annual impact from late markdown decisions (Pain Point PP-016)

---

> "First markdown at week 6 if sell-through below 40%, deeper cuts at week 10, outlets get transfers after second markdown"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Markdown process triggered by poor initial forecasts

---

### Firefighting Culture

> "Firefighting: 6-18 hrs/week in out of stock, rush allocations and supplier exceptions."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Time spent on reactive problem-solving

---

> "Firefighting: 12 hrs/week"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Weekly time lost to reactive issues

---

---

## Theme 5: Stakeholder Alignment Issues

### Cross-Functional Friction

> "The merchandising team treats our forecasts like 'suggestions' until the numbers prove them wrong - but by then it's too late to course-correct."

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Pain point - analytical recommendations ignored by buyers

---

> "Long cross-functional meetings to solve allocation/assortment disagreements."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Biggest time waster - 6-12 hrs/week in alignment meetings

---

> "Buyers often override analytical recommendations based on 'gut feel' from trade shows, limited ability to test new styles before committing to bulk orders"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Forecasting process challenges - human override of data

---

---

## Theme 6: Agility and Responsiveness

### System Rigidity

> "Lack of agility in forecast adjustments"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Pain point severity 4 - ongoing issue

---

> "Model frequency & infra cost constraints [...] Models run monthly vs desired weekly"

**Source:** INT-004 (Data Scientist, Canadian Tire)
**Context:** Infrastructure limitations reduce responsiveness

---

### Manual Intervention Needs

> "Some processes required human insight generation between automated steps"

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Manual interventions pain point from previous work

---

> "Rebuilding Excel forecast models when someone breaks a formula - happens monthly"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Biggest time waster - model maintenance overhead

---

---

## Theme 7: Solution Direction & Preferences

### Technology Preferences

> "They want to adopt AI/LLMs to improve prediction accuracy, instead of only traditional machine learning models"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Clear preference for advanced AI approaches

---

### Magic Wand Solutions

> "Make forecasting and allocation truly real-time and integrated into a single source that automatically localizes the assortments and rebalances inventory with less (or no) manual handoffs."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Magic wand question - ideal solution

---

> "A unified system that actually talks between forecasting, buying, and allocation - where a demand signal automatically triggers the right actions across teams without me having to coordinate everything manually through Excel and emails."

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Magic wand question - cross-system integration

---

> "Improve demand forecast accuracy with AI/LLM capabilities that can incorporate external factors"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Magic wand question - primary need

---

---

## Theme 8: Industry-Specific Challenges

### Fashion Retail Volatility

> "Swimwear particularly challenging due to weather dependency"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Forecasting process challenges

---

> "Social media trends... fashion trends change weekly/daily and directly affect buying patterns"

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Fast-changing external factors in fashion

---

### Long Lead Times

> "6-month lead time for manufacturing, forecast at style-color level, heavy reliance on last year +/- adjustments"

**Source:** INT-003 (Market Analyst, La Vie En Rose)
**Context:** Fashion retail planning challenges

---

> "Design & forecast 1 year ahead (furniture long lead time)"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Furniture industry unique constraint

---

### Scale Complexity

> "Number of SKUs: Millions globally. Number of Stores: Around 10,000 globally."

**Source:** INT-002 (Planning Manager, Walmart)
**Context:** Massive scale metrics

---

> "~250k active SKUs, ~1,700 stores; 15–20M loyalty customers."

**Source:** INT-004 (Data Scientist, Canadian Tire)
**Context:** Multi-banner retail scale

---

---

## Theme 9: Collaboration & Future Opportunities

### Stakeholder Engagement

> "Upon MVP delivery, interviewee will facilitate introduction to Planning Team Manager"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Proposed path forward

---

> "If MVP demonstrates value, company is open to continued collaboration beyond the independent study period"

**Source:** INT-001 (Business Analyst, Furniture Retail)
**Context:** Potential long-term collaboration

---

> "Potential project review before submission"

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Follow-up needed - offered to review project work

---

---

## Theme 10: Scope and Focus Recommendations

### Project Scoping Advice

> "It's good to focus on one [domain]. It would be too much to cover all aspects across different areas like inventory, revenue, or finance."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Recommendations for project scope

---

> "Must focus on ONE specific use case. Example: Sales forecasting for specific SKUs at specific stores. Don't try to solve inventory + revenue + finance simultaneously."

**Source:** INT-005 (Vaibhav Vishal, Groupe Dynamite/Walmart)
**Context:** Scope warning from notes

---

---

## Quotes by Interview Source

### INT-001 (Furniture - Business Analyst)
- 5 quotes
- **Themes:** Traditional ML limitations, AI/LLM preference, reallocation complexity, long lead times

### INT-002 (Walmart - Planning Manager)
- 6 quotes
- **Themes:** Massive scale, data prep burden, cross-functional alignment, magic wand integration

### INT-003 (La Vie En Rose - Market Analyst)
- 11 quotes
- **Themes:** Data reconciliation nightmares, stakeholder friction, markdown impact, system fragmentation

### INT-004 (Canadian Tire - Data Scientist)
- 6 quotes
- **Themes:** Seasonality focus, data prep time, inventory-marketing disconnect, infrastructure constraints

### INT-005 (Groupe Dynamite/Walmart - BI Developer)
- 8 quotes
- **Themes:** Data cleaning burden, correlation methodology, omnichannel complexity, scope recommendations

---

**Total Quotes:** 36 key quotes extracted
**Most Quoted Themes:** Data Integration (9), Forecast Accuracy (7), Business Impact (6)
**Status:** Phase 1 Extraction Complete
**Next Step:** Create Requirements_Extract.md
