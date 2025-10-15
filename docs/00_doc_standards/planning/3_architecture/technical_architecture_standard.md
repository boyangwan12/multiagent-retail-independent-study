# Technical Architecture Standard

## 🎯 How to Create This Document

### Step 1: Create Technical Architecture with Architect (60-90 minutes)

```bash
*agent architect

I need to create a comprehensive technical architecture document for my system.

*create-full-stack-architecture
```

**The architect will:**
- Use the BMad `*task create-doc` workflow with the `fullstack-architecture-tmpl.yaml` template
- Walk you through all **20 sections** (listed below) one at a time
- After each section, present **9 elicitation options** (numbered 1-9):
  - Option 1: Proceed to next section
  - Options 2-9: Advanced elicitation methods to refine the section
- Provide technical recommendations and best practices
- Wait for your response before continuing

**How to respond:**
- Type **1** to proceed to the next section
- Type **2-9** to use an elicitation method for deeper exploration
- Or just type your feedback/questions directly

**The template includes all 20 required sections** covering system design, tech stack, data models, APIs, security, testing, and more.

---

### Step 2: Review & Refine (As Needed)

**During the workflow**, you can refine any section by:
- Typing feedback directly (architect will update the section)
- Using elicitation options 2-9 for deeper technical exploration
- Asking for alternatives or recommendations

**After completion**, you can request changes:
- "Go back to Section X and add more detail"
- "Include API request/response examples for the user endpoint"
- "Add a sequence diagram for the authentication flow"

---

### Step 3: Consistency Check & Update Prior Documents (30-45 minutes)

After drafting the Technical Architecture, check for contradictions with prior documents.

```bash
*agent architect

Now that we have the Technical Architecture drafted, please:

1. **Compare with prior documents**: Read the Product Brief and Process Workflow, and identify any contradictions between:
   - Technical stack choices vs. requirements in Product Brief
   - Data models vs. workflow phases in Process Workflow
   - Component design vs. business features in Product Brief
   - API specifications vs. operational flow in Process Workflow
   - ML approach vs. success metrics in Product Brief

2. **List contradictions one by one**: For each contradiction, show:
   - What the prior document says (specify Product Brief or Process Workflow)
   - What the Technical Architecture says
   - Why they conflict

3. **Ask for approval to update**: For each contradiction, ask me:
   "Should we update [Product Brief/Process Workflow] to align with this Technical Architecture insight?"

Do NOT auto-update. Present contradictions one at a time and wait for my approval.
```

**The architect will:**
- Identify specific contradictions (e.g., "Product Brief mentions 4 agents, but Technical Architecture defines 5 agents")
- Present each contradiction with line numbers/sections
- Ask: "Should we update Product Brief Section 5 to reflect 5 agents instead of 4?"
- Wait for your approval before moving to next contradiction
- Update prior documents to v1.1 if changes are made

**If contradictions found:**
- Update prior documents to new version (v1.0 → v1.1)
- Move old version to `archive/`
- Update Technical Architecture to reference updated version numbers

---

### Step 4: Update Planning Guide

After completing the Technical Architecture, update the PLANNING_GUIDE.md to track your progress:

```bash
# Open the planning guide
# File: docs/00_doc_standards/planning/PLANNING_GUIDE.md

# Update Document #3 status:
- Change status from ❌ Not Started to ✅ Complete
- Update "Progress" counter (2/5 → 3/5)
- Update "Last Updated" date

# Save the file
```

**What to update:**
- Row 3 (Technical Architecture): `❌ Not Started` → `✅ Complete`
- Progress line: `**Progress**: 2/5 complete` → `**Progress**: 3/5 complete`
- Top of file: Update "Last Updated" date to today

---

## 📋 Required Sections (Agent will include these)

The technical architecture must contain all 20 sections:

### Core Technical (Sections 1-8):
1. **Introduction** - Purpose, system overview, scope
2. **Starter Template Decision** - Framework/tech stack choice with rationale
3. **High Level Architecture** - System diagram and component overview
4. **Tech Stack** - Complete technology choices (versions, tools, frameworks)
5. **Data Models** - Core entities and relationships
6. **Components** - Major system components and responsibilities
7. **External APIs** - Third-party integrations (if applicable)
8. **Core Workflows** - Key operational flows with sequence

### ML/AI & Integration (Sections 9-12) if needed:
9. **ML Approach** - Algorithms, models, training (if applicable)
10. **Agent Handoff Flow** - Multi-agent coordination (if applicable)
11. **REST API Specification** - Endpoints, request/response schemas
12. **Frontend Flow** - UI flow and state management (if applicable)

### Implementation Details (Sections 13-14):
13. **Database Schema** - Tables, fields, types, relationships
14. **Source Tree Structure** - Project folder structure

### Operations & Quality (Sections 15-20):
15. **Infrastructure & Deployment** - Hosting, CI/CD, monitoring
16. **Error Handling Strategy** - How to handle failures
17. **Coding Standards** - Style guide, linting, conventions
18. **Test Strategy** - Unit, integration, E2E testing approach
19. **Security** - Authentication, authorization, data protection
20. **Validation Checklist** - Completeness checklist

---

## 💡 Tips

**Do:**
- ✅ Be specific with versions (Python 3.11+, React 18, etc.)
- ✅ Include architecture diagrams (ASCII art is fine)
- ✅ Provide rationale for all major technical decisions
- ✅ List alternatives considered and why rejected
- ✅ Include code examples for complex logic
- ✅ Specify exact folder structure
- ✅ Define all database tables with field types
- ✅ Document all REST endpoints with request/response schemas
- ✅ Include error codes and handling strategies

**Don't:**
- ❌ Be vague ("we'll use a modern framework" → specify "FastAPI 0.104+")
- ❌ Skip rationale ("we chose X" → explain "we chose X because Y, Z")
- ❌ Forget to document APIs (define all endpoints clearly)
- ❌ Leave database schema incomplete (specify all tables, fields, types)
- ❌ Mix architecture with implementation details (stay high-level but complete)
- ❌ Skip error handling and security sections

---

## 📁 File Naming

Save the output as: `technical_architecture_v1.0.md`

When you update it later:
- Minor changes: `technical_architecture_v1.1.md`, `v1.2.md`
- Major revisions: `technical_architecture_v2.0.md`
- Move old versions to `archive/` folder

---

## ✅ Completion Checklist

Before moving to implementation, verify:

- [ ] Architect completed comprehensive planning session
- [ ] All 20 required sections present
- [ ] Introduction with purpose, overview, scope complete
- [ ] Starter template/framework decision documented with rationale
- [ ] High-level architecture diagram included
- [ ] Complete tech stack specified (all tools, versions)
- [ ] Data models defined (entities, relationships)
- [ ] All major components documented with responsibilities
- [ ] Core workflows documented with sequence
- [ ] Database schema complete (all tables, fields, types)
- [ ] API specification complete (if applicable)
- [ ] ML/AI approach documented (if applicable)
- [ ] Error handling strategy defined
- [ ] Test strategy defined
- [ ] Security considerations addressed
- [ ] Source tree structure specified
- [ ] Infrastructure & deployment plan included
- [ ] Coding standards defined
- [ ] Validation checklist included
- [ ] Consistency check completed against Product Brief and Process Workflow
- [ ] All contradictions resolved and prior documents updated if needed
- [ ] Document reviewed by technical team
- [ ] Saved as `technical_architecture_v1.0.md`

**Time Investment:** 2-3 hours total
**Output:** Complete technical architecture (typically 15-40 pages)
**Next Document:** PRD (Product Requirements Document)

---

## 🔄 Example Conversation Flow

**You:**
```
*agent architect
*create-full-stack-architecture
```

**Architect (Winston):**
```
I'll help you create a comprehensive technical architecture using the fullstack-architecture template.
Let me walk you through each of the 20 sections.

=== Section 1: Introduction ===

[Architect drafts initial content based on context or asks questions]

Here's my draft for the Introduction:
[Draft content including purpose, system overview, scope]

**Rationale:** [Explains technical decisions, trade-offs, alternatives considered]

Please review. You can:
1. Proceed to next section
2. Challenge Assumptions
3. Explore Alternatives
4. Identify Risks
5. Technical Deep Dive
6. Compare Approaches
7. Security Analysis
8. Performance Review
9. Tree of Thoughts

Select 1-9 or just type your question/feedback:
```

**You:**
```
1
```

**Architect:**
```
Great! Moving to Section 2: Starter Template Decision...

I'll recommend specific frameworks and tech stack choices with rationale.
[Process repeats for all 20 sections]
```

---

**That's it!** The architect guides you through the template section-by-section with technical recommendations and elicitation options.
