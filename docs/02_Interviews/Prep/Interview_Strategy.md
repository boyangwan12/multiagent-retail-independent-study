# Evidence Pack Interview Strategy

lets now understand the structure of evidence pack

```markdown
1_Executive_Summary.md

  High-level 2-3 page overview for stakeholders with key discoveries, validated problems, and proposed solution
  opportunities.

2_Interview_Methodology.md

  Documents your research approach - who you interviewed, how interviews were conducted, and the coding system used to
   analyze responses.

3_Current_State_Analysis/

  - Workflow_Diagrams.md: Visual flowcharts showing how retail planning currently works, including decision points and
   team handoffs
  - System_Landscape.md: Maps all software tools currently used and how they integrate (or don't)
  - Pain_Point_Inventory.xlsx: Spreadsheet cataloging all problems with frequency, severity scores, and business
  impact
  - Time_Motion_Analysis.md: Breakdown of where time is spent in current processes and bottlenecks

4_Requirements_Discovery/ (this we might not need to ask them directly, we can make some assumptions)

  - Functional_Requirements.md: What the system must DO (e.g., "consolidate data from 5 sources")
  - Non_Functional_Requirements.md: HOW it should perform (e.g., "process in under 30 minutes")
  - User_Stories.md: Features from user perspective ("As a planner, I want X so that Y")
  - Acceptance_Criteria.md: Measurable definitions of "done" for each requirement

5_Coded_Transcripts/

  Complete interview recordings with analytical tags [PP-TIME], [REQ-FORECAST] to identify patterns and trace
  requirements back to source.

6_Synthesis_Artifacts/

  - Persona_Profiles.md: Composite user archetypes based on interview patterns (e.g., "Sarah the Senior Demand
  Planner")
  - Journey_Maps.md: Step-by-step user workflows with emotions and pain points at each stage
  - Opportunity_Matrix.md: 2x2 grid plotting features by value vs. effort to prioritize development
  - Quote_Bank.md: Powerful direct quotes organized by theme for presentations and stakeholder buy-in
```

the evidence pack is one of our deliverables, and it is the context to create prd

in order to get all the content for evidence pack, we need to ask the right interview questions.

so we need to understand the retail operational workflow now:

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
```

these are the areas that we need to focus on

im thinking about creating 3 - 5 agents

- 1 agent for sth for PLANNING (Pre-Season)
- 1 agent for sth for EXECUTION (In-Season)
- 1 agent for sth for OPTIMIZATION (Continuous)

we might have some more agents, depends what we find

so interview,

first, we need to understand their workflow: the workflow up there is generic, we need to understand their workflow first

then anything matches what we mapped up there, we ask more questions on that part to really understand how they do things

eg

**How did your initial forecast/plan compare to what actually happened?**

What's your typical forecast accuracy rate?

then we ask about the pain points, get as many as pain points possible, cuz later on, we need to fill out (Pain_Point_Inventory.xlsx) and (Time_Motion_Analysis.md: Breakdown of where time is spent in current processes and bottlenecks) read these 2 files in \docs\04_Analysis_Findings\Evidence_Pack to have a idea what we need

then we need to understand their tech stack/ tools they are using rn

**Walk me through the different systems you had to navigate during this situation**

- "Any Excel heroics involved?" [usually gets honest laughs]
- "What takes the longest - getting the data or analyzing it?"
- "If you could consolidate three systems into one, which would they be?"
- "How much time do you spend on manual data prep vs actual analysis?"
- "What workarounds have become permanent solutions?"