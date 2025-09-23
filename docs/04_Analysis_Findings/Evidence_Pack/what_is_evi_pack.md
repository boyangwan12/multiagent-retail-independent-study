# Evidence Pack & Interview Strategy Guide
## For Multi-Agent Retail Operations System

---

## 1. WHAT IS THE EVIDENCE PACK?

### Definition
The **Evidence Pack** is a structured, de-identified compilation of coded interview findings that serves as the empirical foundation for your multi-agent system design. It transforms raw interview data into actionable insights while maintaining participant confidentiality.

### Purpose & Value
- **Validates Problem Significance**: Proves the business problems you're solving are real and impactful
- **Grounds Technical Requirements**: Ensures your system addresses actual industry needs, not assumptions
- **Provides Design Rationale**: Justifies every feature and architectural decision with real-world evidence
- **Enables Prioritization**: Helps rank features based on frequency and severity of pain points

### Key Components
1. **Coded Interview Transcripts** - Anonymized, thematically tagged conversations
2. **Pain Point Inventory** - Categorized list of challenges with frequency/severity ratings
3. **Workflow Diagrams** - Visual maps of current retail planning processes
4. **Requirements Traceability Matrix** - Links interview insights to system features
5. **Persona Profiles** - Composite user archetypes based on interview patterns
6. **Quote Bank** - Direct, de-identified quotes supporting key findings

---

## 2. INTERVIEW INFORMATION REQUIREMENTS

### A. Current State Discovery

#### **Workflow & Process Mapping**
- **Daily/Weekly Tasks**: "Walk me through your typical planning cycle"
- **Decision Points**: "What triggers a reforecast or assortment change?"
- **Handoffs**: "How does forecast data flow to assortment planning?"
- **Iteration Cycles**: "How many rounds of revision typically occur?"
- **Timeline Constraints**: "What are your critical deadlines?"

#### **Tool & System Landscape**
- **Current Solutions**: "What software/tools do you use for demand forecasting?"
- **Integration Points**: "How do different systems communicate?"
- **Manual Workarounds**: "What do you handle in Excel because systems can't?"
- **Data Sources**: "Where does your historical sales data come from?"

### B. Pain Points & Challenges

#### **Quantifiable Problems**
- **Time Waste**: "How many hours spent on manual data reconciliation?"
- **Error Rates**: "How often do forecasts miss by >20%?"
- **Revenue Impact**: "What's the cost of allocation mistakes?"
- **Rework Frequency**: "How often do plans need complete revision?"

#### **Qualitative Frustrations**
- **Biggest Headaches**: "What keeps you up at night during planning season?"
- **Wish List**: "If you had a magic wand, what would you fix?"
- **Workarounds**: "What shortcuts have you developed?"
- **Team Friction**: "Where do conflicts arise between teams?"

### C. Decision-Making Context

#### **Business Rules & Constraints**
- **Hierarchy Logic**: "How do you decide store allocation priorities?"
- **Minimum/Maximum Rules**: "What constraints govern assortment width?"
- **Exception Handling**: "How do you handle new products without history?"
- **Regional Variations**: "How do plans differ by geography?"

#### **Success Metrics**
- **KPIs Tracked**: "How do you measure planning success?"
- **Performance Reviews**: "What metrics determine your bonus?"
- **Reporting Cadence**: "Who reviews plans and how often?"

### D. Future State Vision

#### **Ideal Capabilities**
- **Automation Desires**: "What would you want AI to handle automatically?"
- **Human-in-Loop Needs**: "What decisions must remain human-controlled?"
- **Transparency Requirements**: "How important is understanding AI reasoning?"
- **Trust Factors**: "What would make you trust an AI recommendation?"

---

## 3. INTERVIEW QUESTION FRAMEWORK

### Opening Questions (Build Rapport)
1. "Tell me about your role in the retail planning process"
2. "How long have you been in merchandise planning?"
3. "What's the scale of your planning responsibility?" (# SKUs, stores, $ value)

### Core Process Questions
```markdown
DEMAND FORECASTING
- "How do you currently forecast demand for new vs. carry-over products?"
- "What external factors do you consider?" (weather, trends, competition)
- "How do you handle products with limited history?"
- "What's your forecast accuracy typically?"

ASSORTMENT PLANNING
- "How do you determine the right product mix?"
- "What constraints affect your assortment decisions?"
- "How do you balance breadth vs. depth?"
- "How often do assortments change?"

ALLOCATION OPTIMIZATION
- "How do you decide store-level allocations?"
- "What data drives allocation decisions?"
- "How do you handle slow-moving inventory?"
- "What's the reallocation process?"
```

### Problem Discovery Questions
- "Describe a recent planning disaster - what went wrong?"
- "Where do you spend most time that feels unproductive?"
- "What information do you wish you had but don't?"
- "If you could automate one thing, what would it be?"

### Solution Validation Questions
- "How would AI-powered demand sensing help your process?"
- "What if agents could coordinate forecast-assortment-allocation automatically?"
- "What concerns would you have about AI-driven planning?"
- "What would convince you to trust automated recommendations?"

---

## 4. EVIDENCE PACK STRUCTURE

### Document Organization
```
Evidence_Pack/
├── 1_Executive_Summary.md
│   ├── Key Findings (3-5 bullets)
│   ├── Problem Validation
│   └── Solution Opportunity
│
├── 2_Interview_Methodology.md
│   ├── Participant Demographics
│   ├── Interview Protocol
│   └── Coding Framework
│
├── 3_Current_State_Analysis/
│   ├── Workflow_Diagrams.md
│   ├── System_Landscape.md
│   ├── Pain_Point_Inventory.xlsx
│   └── Time_Motion_Analysis.md
│
├── 4_Requirements_Discovery/
│   ├── Functional_Requirements.md
│   ├── Non_Functional_Requirements.md
│   ├── User_Stories.md
│   └── Acceptance_Criteria.md
│
├── 5_Coded_Transcripts/
│   ├── Interview_01_Coded.md
│   ├── Interview_02_Coded.md
│   └── [Additional interviews...]
│
└── 6_Synthesis_Artifacts/
    ├── Persona_Profiles.md
    ├── Journey_Maps.md
    ├── Opportunity_Matrix.md
    └── Quote_Bank.md
```

### Coding Schema Example
```markdown
## Pain Points Coding
[PP-TIME] - Time-consuming manual process
[PP-ERROR] - Error-prone/inaccurate
[PP-INTEGRATE] - System integration issue
[PP-VISIBILITY] - Lack of visibility/transparency
[PP-COORDINATE] - Cross-team coordination challenge

## Requirements Coding
[REQ-FORECAST] - Demand forecasting need
[REQ-ASSORT] - Assortment planning need
[REQ-ALLOC] - Allocation optimization need
[REQ-ORCHESTRATE] - Workflow orchestration need
[REQ-EXPLAIN] - Explainability/transparency need

## Value Coding
[VALUE-EFFICIENCY] - Time/cost savings
[VALUE-ACCURACY] - Improved accuracy/quality
[VALUE-REVENUE] - Revenue/margin improvement
[VALUE-AGILITY] - Faster response to changes
```

---

## 5. FROM EVIDENCE TO PRD

### Translation Framework

#### **Evidence Pack Finding → PRD Section Mapping**

| Evidence Pack Component | PRD Section | Translation Method |
|------------------------|-------------|-------------------|
| Pain Point Inventory | Problem Statement | Prioritize by frequency × severity |
| Workflow Diagrams | Use Cases | Extract key interaction patterns |
| User Quotes | User Stories | Convert quotes to "As a... I want..." |
| System Landscape | Technical Context | Identify integration requirements |
| Success Metrics | Acceptance Criteria | Transform KPIs into measurable outcomes |
| Persona Profiles | User Requirements | Define role-based access/features |

### PRD Structure Informed by Evidence

```markdown
# PRODUCT REQUIREMENTS DOCUMENT

## 1. Problem Definition [Source: Pain Point Inventory]
- Primary Problem: [Most frequent/severe pain point]
- Supporting Evidence: [3-5 interview quotes]
- Business Impact: [Quantified from interviews]

## 2. User Personas [Source: Persona Profiles]
- Demand Planner Profile
- Merchandise Planner Profile
- Allocation Analyst Profile

## 3. Functional Requirements [Source: Coded Requirements]
### 3.1 Demand Forecasting Agent
- FR1: [Requirement] | Evidence: [Interview Quote/Code]
- FR2: [Requirement] | Evidence: [Interview Quote/Code]

## 4. User Stories [Source: Journey Maps + Quotes]
- "As a demand planner, I want automated outlier detection
   so I don't spend hours cleaning data" [INT-03, INT-05]

## 5. Success Metrics [Source: Current KPIs]
- Forecast Accuracy: >85% (current: 70% per INT-02)
- Planning Cycle Time: <2 days (current: 5 days per INT-04)
```

---

## 6. INTERVIEW EXECUTION CHECKLIST

### Pre-Interview
- [ ] Send consent form 48 hours prior
- [ ] Share high-level topics (not specific questions)
- [ ] Test recording equipment
- [ ] Prepare backup questions
- [ ] Review participant's company/role

### During Interview
- [ ] Obtain verbal consent confirmation
- [ ] Start with easy rapport-building questions
- [ ] Use "tell me about..." open-ended prompts
- [ ] Ask for specific examples/stories
- [ ] Probe with "why" and "how" follow-ups
- [ ] Request permission to contact for clarification

### Post-Interview
- [ ] Transcribe within 24 hours
- [ ] Apply coding schema
- [ ] Extract key quotes
- [ ] Update pain point inventory
- [ ] Send thank you note
- [ ] Schedule follow-up if needed

---

## 7. QUALITY CRITERIA FOR EVIDENCE PACK

### Completeness
- ✓ Minimum 5 interviews conducted
- ✓ All three agent areas covered (forecast, assortment, allocation)
- ✓ Multiple company types represented
- ✓ Both current state and future needs explored

### Rigor
- ✓ Consistent coding schema applied
- ✓ Inter-rater reliability check (if team coding)
- ✓ Triangulation across interviews
- ✓ Negative cases acknowledged

### Actionability
- ✓ Clear problem-solution mapping
- ✓ Prioritized requirements list
- ✓ Measurable success criteria
- ✓ Technical feasibility validated

### Confidentiality
- ✓ All names/companies anonymized
- ✓ Proprietary details removed
- ✓ Consent documentation complete
- ✓ Data stored securely

---

## 8. COMMON PITFALLS TO AVOID

### During Interviews
- ❌ Leading questions ("Don't you think AI would help?")
- ❌ Technical jargon without explanation
- ❌ Interrupting stories for clarification
- ❌ Accepting vague answers without probing
- ❌ Focusing only on problems, not current successes

### In Evidence Pack Creation
- ❌ Cherry-picking quotes that support preconceptions
- ❌ Over-generalizing from single interviews
- ❌ Losing nuance through over-coding
- ❌ Mixing interpretation with direct evidence
- ❌ Forgetting edge cases and exceptions

### In PRD Translation
- ❌ Adding features not supported by evidence
- ❌ Ignoring conflicting requirements
- ❌ Assuming technical solutions
- ❌ Overlooking change management needs
- ❌ Missing non-functional requirements

---

## APPENDIX: Sample Interview Output

### Example Coded Transcript Excerpt
```markdown
**[Participant 04 - Merchandise Planner, 7 years experience]**

INTERVIEWER: "Tell me about your biggest challenge in assortment planning?"

PARTICIPANT: "The worst part [PP-TIME] is manually combining data
from five different systems [PP-INTEGRATE]. Our demand forecast
lives in System A, inventory in System B, and financial targets
in Excel [PP-VISIBILITY]. I spend two full days [PP-TIME] just
getting data aligned before I can even start planning [REQ-ORCHESTRATE].
What I really need [REQ-INTEGRATE] is something that pulls it
all together and shows me conflicts automatically [VALUE-EFFICIENCY]."

[Analysis Note: Strong evidence for orchestration layer requirement.
Time savings of 2 days = 40% of planning cycle. Integration across
5 systems suggests API/connector needs.]
```

---

*This guide provides the framework for building a robust Evidence Pack that will directly inform your PRD and ensure your multi-agent system addresses real retail planning challenges.*