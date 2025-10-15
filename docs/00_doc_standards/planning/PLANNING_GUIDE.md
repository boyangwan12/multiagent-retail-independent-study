# Planning Guide

**Purpose**: Track your progress through the planning phase. Update this document as you complete each planning document.

**Last Updated**: [Update this date when you check off a document]

---

## Planning Documents Checklist

| # | Document | Status | Agent | Output Path | Est. Time |
|---|----------|--------|-------|-------------|-----------|
| 1 | **Product Brief** | ❌ Not Started | `*agent analyst` → `*agent pm` | `product_brief/product_brief_v1.0.md` | 1-2 hours |
| 2 | **Process Workflow** | ❌ Not Started | `*agent architect` | `process_workflow/process_workflow_v1.0.md` | 1-2 hours |
| 3 | **Technical Architecture** | ❌ Not Started | `*agent architect` | `architecture/technical_architecture_v1.0.md` | 2-3 hours |
| 4 | **PRD** | ❌ Not Started | `*agent pm` | `prd/prd_v1.0.md` | 2-4 hours |
| 5 | **Frontend Spec** | ❌ Not Started | `*agent ux-expert` | `design/frontend_spec_v1.0.md` | 2-3 hours |

**Progress**: 0/5 complete

**Note**: Each document (except Product Brief) includes a built-in consistency check step. The agent will detect contradictions with prior documents and ask for your approval before updating them.

---

## Document Creation Flow with Consistency Checks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PLANNING DOCUMENT WORKFLOW                         │
│                      (with backward consistency updates)                    │
└─────────────────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌──────────────────────┐
│  1. Product Brief    │
│  (*agent analyst →   │
│   *agent pm)         │
│                      │
│  Time: 1-2 hours     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. Process Workflow  │
│ (*agent architect)   │
│                      │
│ Time: 1-2 hours      │
└──────────┬───────────┘
           │
           │ Consistency Check ─────────────────┐
           │ (compares with #1)                 │
           │                                    │
           │                      Updates #1 if needed
           │                                    ▼
           │                          ┌─────────────────┐
           │                          │ 1. Product Brief│
           │                          │       v1.1      │
           │                          └─────────────────┘
           │
           ▼
┌──────────────────────┐
│ 3. Tech Architecture │
│ (*agent architect)   │
│                      │
│ Time: 2-3 hours      │
└──────────┬───────────┘
           │
           │ Consistency Check ────┬────────────────┐
           │ (compares with #1, #2)│                │
           │                       │                │
           │               Updates │1 if needed     │ Updates #2 if needed
           │                       ▼                ▼
           │              ┌────────────────┐ ┌─────────────────┐
           │              │ 1. Product     │ │ 2. Process      │
           │              │    Brief v1.1  │ │    Workflow v1.1│
           │              └────────────────┘ └─────────────────┘
           │
           ▼
┌──────────────────────┐
│    4. PRD            │
│  (*agent pm)         │
│                      │
│  Time: 2-4 hours     │
└──────────┬───────────┘
           │
           │ Consistency Check ────┬────────────┬──────────────┐
           │ (compares with        │            │              │
           │  #1, #2, #3)          │            │              │
           │                       │            │              │
           │           Updates #1  │ Updates #2 │ Updates #3   │
           │           if needed   │ if needed  │ if needed    │
           │                       ▼            ▼              ▼
           │              ┌─────────────┐ ┌──────────┐ ┌────────────┐
           │              │ 1. Product  │ │ 2. Process│ │ 3. Tech    │
           │              │    Brief    │ │   Workflow│ │   Arch     │
           │              └─────────────┘ └──────────┘ └────────────┘
           │
           ▼
┌──────────────────────┐
│ 5. Frontend Spec     │
│ (*agent ux-expert)   │
│                      │
│ Time: 2-3 hours      │
└──────────┬───────────┘
           │
           │ Consistency Check ────┬───────────┬──────────┬──────────┐
           │ (compares with        │           │          │          │
           │  #1, #2, #3, #4)      │           │          │          │
           │                       │           │          │          │
           │          Updates #1   │Updates #2 │Updates #3│Updates #4│
           │          if needed    │if needed  │if needed │if needed │
           │                       ▼           ▼          ▼          ▼
           │              ┌───────────┐ ┌─────────┐ ┌────────┐ ┌─────┐
           │              │ 1. Product│ │2. Process│ │3. Tech │ │4.PRD│
           │              │    Brief  │ │ Workflow │ │  Arch  │ │     │
           │              └───────────┘ └─────────┘ └────────┘ └─────┘
           │
           ▼
       ┌───────┐
       │  END  │ ← All 5 documents complete, all contradictions resolved
       └───────┘

LEGEND:
  ┌────┐
  │    │  = Document creation step
  └────┘

  │     = Forward flow (create next document)
  ▼

  Each consistency check can update ANY prior document (shown with arrows pointing
  back to specific documents). Updates only happen with user approval.
```

---

## Order of Document Creation

### Document #1: Product Brief
**Agent**: `*agent analyst` (research) → `*agent pm` (writing)
**Reference**: `00_doc_standards/planning/1_product_brief/product_brief_standard.md`

**What to do**:
1. Open the product_brief_standard.md
2. Follow Step 1: Copy the analyst prompt and start the interview
3. Answer the analyst's questions naturally
4. Follow Step 2: Analyst passes findings to PM agent
5. Review and iterate until satisfied
6. Save as `product_brief_v1.0.md` in your project's `product_brief/` folder
7. **Update this guide**: Change status to ✅ Complete

**Start command**:
```bash
*agent analyst

I need to create a product brief for a new project.
[See product_brief_standard.md for full prompt]
```

---

### Document #2: Process Workflow
**Agent**: `*agent architect`
**Reference**: `00_doc_standards/planning/2_process_workflow/process_workflow_standard.md`

**Prerequisites**: Product Brief must be complete

**What to do**:
1. Open the process_workflow_standard.md
2. Follow Step 1: Copy the architect prompt
3. Walk through concrete examples with real numbers
4. Review the draft process workflow
5. **Follow Step 3: Consistency check** - Agent will detect contradictions with Product Brief and ask for approval to update
6. Save as `process_workflow_v1.0.md` in your project's `process_workflow/` folder
7. **Update this guide**: Change status to ✅ Complete

**Start command**:
```bash
*agent architect

I need to create a process workflow document.
[See process_workflow_standard.md for full prompt]
```

**After drafting, the agent will automatically run a consistency check**:
- Compares Process Workflow with Product Brief
- Detects contradictions and presents them one-by-one
- Asks for your approval before updating Product Brief
- Updates Product Brief to v1.1 if you approve changes

---

### Document #3: Technical Architecture
**Agent**: `*agent architect`
**Reference**: `00_doc_standards/planning/3_architecture/technical_architecture_standard.md`

**Prerequisites**: Product Brief and Process Workflow must be complete

**What to do**:
1. Open the technical_architecture_standard.md
2. Follow Step 1: Copy the architect prompt
3. Go through all technical decisions systematically
4. Review the complete architecture specification
5. **Follow Step 4: Consistency check** - Agent will detect contradictions with Product Brief and Process Workflow, and ask for approval to update
6. Save as `technical_architecture_v1.0.md` in your project's `architecture/` folder
7. **Update this guide**: Change status to ✅ Complete

**Start command**:
```bash
*agent architect

I need to create a comprehensive technical architecture document.
[See technical_architecture_standard.md for full prompt]
```

**After drafting, the agent will automatically run a consistency check**:
- Compares Technical Architecture with Product Brief and Process Workflow
- Detects contradictions and presents them one-by-one
- Asks for your approval before updating any prior documents
- Updates prior documents to v1.1 if you approve changes

---

### Document #4: PRD (Product Requirements Document)
**Agent**: `*agent pm`
**Reference**: `00_doc_standards/planning/4_prd/prd_standard.md`

**Prerequisites**: Product Brief, Process Workflow, and Technical Architecture must be complete

**What to do**:
1. Open the prd_standard.md
2. Follow Step 1: Copy the PM prompt
3. Work through user stories, requirements, and acceptance criteria
4. Review the complete PRD
5. **Follow Step 4: Consistency check** - Agent will detect contradictions with Product Brief, Process Workflow, and Technical Architecture, and ask for approval to update
6. Save as `prd_v1.0.md` in your project's `prd/` folder
7. **Update this guide**: Change status to ✅ Complete

**Start command**:
```bash
*agent pm

I need to create a comprehensive Product Requirements Document (PRD).
[See prd_standard.md for full prompt]
```

**After drafting, the agent will automatically run a consistency check**:
- Compares PRD with Product Brief, Process Workflow, and Technical Architecture
- Detects contradictions and presents them one-by-one
- Asks for your approval before updating any prior documents
- Updates prior documents to v1.1 if you approve changes

---

### Document #5: Frontend Spec (Design Spec)
**Agent**: `*agent ux-expert`
**Reference**: `00_doc_standards/planning/5_design/frontend_spec_standard.md`

**Prerequisites**: Product Brief, PRD, and Technical Architecture must be complete

**What to do**:
1. Open the frontend_spec_standard.md
2. Follow Step 1: Copy the designer prompt
3. Work through UX goals, wireframes, user flows, and design system
4. Review the complete frontend specification
5. **Follow Step 4: Consistency check** - Agent will detect contradictions with Product Brief, Process Workflow, Technical Architecture, and PRD, and ask for approval to update
6. Save as `frontend_spec_v1.0.md` in your project's `design/` folder
7. **Update this guide**: Change status to ✅ Complete

**Start command**:
```bash
*agent ux-expert

I need to create a comprehensive Frontend UI/UX Specification.
[See frontend_spec_standard.md for full prompt]
```

**After drafting, the agent will automatically run a consistency check**:
- Compares Frontend Spec with Product Brief, Process Workflow, Technical Architecture, and PRD
- Detects contradictions and presents them one-by-one
- Asks for your approval before updating any prior documents
- Updates prior documents to v1.1 if you approve changes

---

## After Completing All 5 Documents

✅ **Planning Phase Complete!**

**What's next**:
1. **Final consistency check**: Review all 5 documents for remaining contradictions
2. **Version alignment**: Make sure all cross-references use correct version numbers
3. **Create a summary**: List all major decisions and version numbers
4. Move to the Implementation Phase
5. Refer to your project's IMPLEMENTATION_GUIDE.md (if you have one)

**Total Planning Time**: Approximately 8-14 hours for initial drafts + 2-4 hours for updates and alignment

---

## Tips

- ✅ Follow the order (1 → 2 → 3 → 4 → 5) for document creation
- ✅ **Trust the built-in consistency checks** - agents will detect contradictions automatically
- ✅ Don't skip the consistency check steps - they save time and prevent errors later
- ✅ Use the specified agent for each document
- ✅ **Review each contradiction carefully** before approving updates
- ✅ Version numbers are managed automatically (v1.0 → v1.1) when you approve updates
- ✅ Old versions are automatically moved to `archive/` folder
- ✅ Use Git commits to track changes: "Update Tech Architecture to v1.1: add WebSocket support"
- ✅ **Keep a changelog** in each document showing what changed between versions

---

## Status Legend

- ❌ **Not Started** - Document not yet created
- ⏳ **In Progress** - Currently working on this document
- ✅ **Complete** - Document finished and saved

---

**Remember**: This is a living document. Update the checklist table and "Last Updated" date as you progress!
