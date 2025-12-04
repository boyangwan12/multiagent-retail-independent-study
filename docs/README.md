This Readme file helps you navigate the docs folder
# Documentation

This folder contains all project documentation for the **Agentic Retail Forecasting System** - a McGill BUSA 611/613 Independent Study project.

## Folder Structure

```
docs/
├── 00_doc_standards/       # Documentation templates and standards
├── 01_Project_Foundation/  # Initial project setup and approvals
├── 02_Interviews/          # Stakeholder research interviews
├── 03_Evidence_Pack/       # Research synthesis and validation
├── 04_MVP_Development/     # Technical specs and implementation
└── 05_Progress_Reports/    # Weekly updates and team handoffs
```

---

## 00_doc_standards

Documentation standards and templates for consistent project documentation.

```
00_doc_standards/
├── planning/           # Planning document templates
├── implementation/     # Implementation document templates (empty)
└── archive/            # Archived standards (empty)
```

| File | Description |
|------|-------------|
| `planning/0_PLANNING_GUIDE.md` | Overview of planning document workflow |
| `planning/1_product_brief_standard.md` | Product brief template |
| `planning/2_process_workflow_standard.md` | Process workflow template |
| `planning/3_technical_architecture_standard.md` | Architecture document template |
| `planning/4_prd_standard.md` | PRD template |
| `planning/5_frontend_spec_standard.md` | Frontend specification template |
| `planning/peer_review_tracker.md` | Document review tracking |

---

## 01_Project_Foundation

Initial project setup documents and approvals.

```
01_Project_Foundation/
├── Initial_Correspondence/    # Email threads and screenshots
└── research/                  # Technical research documents
```

| File | Description |
|------|-------------|
| `BUSA_611-613_Independent_Study_Request_Form.pdf` | Official McGill course registration |
| `Initial_Correspondence/email.md.txt` | Email correspondence with supervisor |
| `Initial_Correspondence/screenshoot.md.txt` | Screenshot references |
| `research/OpenAI_Agents_SDK_Retail_PoC_Research.md` | OpenAI Agents SDK research for retail use case |

---

## 02_Interviews

Stakeholder research with retail operations professionals.

```
02_Interviews/
├── Prep/          # Interview guides and strategy
├── Notes/         # Summary notes (INT-001 to INT-005)
└── Transcripts/   # Full transcripts (INT-004, INT-005)
```

| Subfolder | Contents |
|-----------|----------|
| `Prep/` | Interview guides, strategy documents, Arnav interview guide |
| `Notes/` | INT-001 through INT-005 summary notes |
| `Transcripts/` | INT-004 and INT-005 full transcripts |

---

## 03_Evidence_Pack

Research synthesis validating the problem and proposed solution.

```
03_Evidence_Pack/
├── _extraction/    # Raw data extractions
└── *.md            # Synthesis documents
```

| File | Description |
|------|-------------|
| `Evidence_Pack_Preparation_Plan.md` | Planning document for evidence pack |
| `01_Problem_Validation.md` | Evidence that the problem exists |
| `02_User_Research_Synthesis.md` | Key insights from interviews |
| `03_Requirements_Constraints.md` | System requirements and constraints |
| `04_Approach_Validation.md` | Why multi-agent AI is the right approach |
| `05_Success_Metrics.md` | How we measure success |
| `06_Research_Methodology.md` | How research was conducted |
| `_extraction/Pain_Point_Inventory.md` | Raw pain points from interviews |
| `_extraction/Quote_Library.md` | Key quotes from interviews |
| `_extraction/Requirements_Extract.md` | Requirements extracted from interviews |

---

## 04_MVP_Development

Technical specifications and implementation documentation.

```
04_MVP_Development/
├── planning/        # Current v4.0 specifications
├── archive/         # Historical versions (v1.1 - v3.3)
└── implementation/  # Phase-by-phase implementation docs
```

### Current Version (v4.0)

Located in `planning/`:

| File | Description |
|------|-------------|
| `0_PLANNING_GUIDE.md` | Planning document guide |
| `1_product_brief_v4.0.md` | Business context and solution overview |
| `2_process_workflow_v4.0.md` | 12-week operational workflow |
| `3_technical_architecture_v4.0.md` | Technical architecture (6-agent system) |
| `4_prd_v4.0.md` | Product requirements document |
| `5_front-end-spec_v4.0.md` | Streamlit frontend specification |
| `6_data_specification_v4.0.md` | Data structure and scenarios |

### Archive

Historical versions preserved in `archive/`:

| Version | Contents |
|---------|----------|
| `v1.1/` | Initial architecture, PRD, product brief |
| `v2.1/` | Product brief, operational workflow, key parameters |
| `v3.1/` | Product brief, operational workflow |
| `v3.2/` | Full suite (product brief, workflow, architecture, PRD, frontend spec) |
| `v3.3/` | Full suite including data specification |

### Implementation Phases

| Phase | Description | Status |
|-------|-------------|--------|
| `phase_1_data_generation/` | Synthetic data generation | Complete |
| `phase_2_frontend/` | React frontend | Archived (deprecated) |
| `phase_3_backend_architecture/` | FastAPI backend | Archived (deprecated) |
| `phase_3.5_testing_cleanup/` | Architecture cleanup and testing | Complete |
| `phase_4_integration/` | Frontend-backend integration | Archived (deprecated) |
| `phase_4.5_data_upload/` | CSV data upload functionality | Complete |
| `phase_5_orchestrator_foundation/` | Agent orchestration framework | Complete |
| `phase_6_demand_agent/` | Demand forecasting agent (Prophet/ARIMA) | Complete |
| `phase_7_inventory_agent/` | Inventory allocation agent (K-means) | Complete |
| `phase_8_pricing_agent/` | Markdown pricing agent | Planned |
| `phase_9_pivot_streamlit_openai_agent_sdk/` | **PIVOT:** Streamlit + OpenAI Agents SDK | Active |

Each implementation phase contains:
- `implementation_plan.md` - Phase overview and goals
- `checklist.md` - Task checklist
- `technical_decisions.md` - Key technical decisions
- `retrospective.md` - Post-phase learnings
- `stories/` - Individual user stories (PHASE{N}-XXX-*.md)

---

## 05_Progress_Reports

Weekly updates and team collaboration documents.

```
05_Progress_Reports/
├── Weekly_Supervisor_Meetings/    # Weekly progress updates
│   └── notes/                     # Meeting notes
└── team_colab/                    # Team handoff documents
```

### Weekly Updates

| File | Description |
|------|-------------|
| `Week_01_Updates.md` | Week 1 progress |
| `Week_02_Updates.md` | Week 2 progress |
| `Week_03_Updates.md` | Week 3 progress |
| `Week_04_Updates.md` | Week 4 progress |
| `Week_05_Updates.md` | Week 5 progress |
| `Week_08_Updates.md` | Week 8 progress |
| `Week_09_Updates.md` | Week 9 progress |
| `notes/Week_03_Notes.md` | Week 3 meeting notes |

---


