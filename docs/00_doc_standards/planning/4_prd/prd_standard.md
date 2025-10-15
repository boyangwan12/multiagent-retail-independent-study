# PRD (Product Requirements Document) Standard

## 🎯 How to Create This Document

### Step 1: Create PRD with PM (60-90 minutes)

```bash
*agent pm

I need to create a comprehensive Product Requirements Document (PRD) for my system.

*create-prd
```

**The PM will:**
- Use the BMad `*task create-doc` workflow with the `prd-tmpl.yaml` template
- Walk you through all **15 sections** (listed below) one at a time
- After each section, present **9 elicitation options** (numbered 1-9):
  - Option 1: Proceed to next section
  - Options 2-9: Advanced elicitation methods to refine the section
- Help you define clear, testable requirements
- Wait for your response before continuing

**How to respond:**
- Type **1** to proceed to the next section
- Type **2-9** to use an elicitation method for deeper exploration
- Or just type your feedback/questions directly

**The template includes all 15 required sections** covering executive summary, user personas, requirements, features, success metrics, and more.

---

### Step 2: Review & Refine (As Needed)

**During the workflow**, you can refine any section by:
- Typing feedback directly (PM will update the section)
- Using elicitation options 2-9 for requirements exploration
- Asking for clarification on acceptance criteria or metrics

**After completion**, you can request changes:
- "Go back to Section X and add more detail"
- "Include specific acceptance criteria for the forecast feature"
- "Define the success metrics more precisely"

---

### Step 3: Consistency Check & Update Prior Documents (30-45 minutes)

After drafting the PRD, check for contradictions with prior documents.

```bash
*agent pm

Now that we have the PRD drafted, please:

1. **Compare with prior documents**: Read the Product Brief, Process Workflow, and Technical Architecture, and identify any contradictions between:
   - User stories vs. business features in Product Brief
   - Functional requirements vs. technical components in Technical Architecture
   - Success metrics vs. business objectives in Product Brief
   - Data requirements vs. data models in Technical Architecture
   - Release plan vs. workflow phases in Process Workflow
   - Acceptance criteria vs. system capabilities in Technical Architecture

2. **List contradictions one by one**: For each contradiction, show:
   - What the prior document says (specify Product Brief/Process Workflow/Technical Architecture)
   - What the PRD says
   - Why they conflict

3. **Ask for approval to update**: For each contradiction, ask me:
   "Should we update [Product Brief/Process Workflow/Technical Architecture] to align with this PRD insight?"

Do NOT auto-update. Present contradictions one at a time and wait for my approval.
```

**The PM will:**
- Identify specific contradictions (e.g., "Product Brief targets 85% accuracy, but PRD acceptance criteria specifies 90%")
- Present each contradiction with line numbers/sections
- Ask: "Should we update Product Brief Section 4 to reflect 90% accuracy target instead of 85%?"
- Wait for your approval before moving to next contradiction
- Update prior documents to v1.1 if changes are made

**If contradictions found:**
- Update prior documents to new version (v1.0 → v1.1)
- Move old version to `archive/`
- Update PRD to reference updated version numbers

---

### Step 4: Update Planning Guide

After completing the PRD, update the PLANNING_GUIDE.md to track your progress:

```bash
# Open the planning guide
# File: docs/00_doc_standards/planning/PLANNING_GUIDE.md

# Update Document #4 status:
- Change status from ❌ Not Started to ✅ Complete
- Update "Progress" counter (3/5 → 4/5)
- Update "Last Updated" date

# Save the file
```

**What to update:**
- Row 4 (PRD): `❌ Not Started` → `✅ Complete`
- Progress line: `**Progress**: 3/5 complete` → `**Progress`: 4/5 complete`
- Top of file: Update "Last Updated" date to today

---

## 📋 Required Sections (Agent will include these)

The PRD must contain all 15 sections:

### Strategic Context (Sections 1-3):
1. **Executive Summary** - High-level overview, objectives, key deliverables
2. **Product Vision** - Long-term vision, strategic goals, business value
3. **Target Users** - User personas, pain points, use cases

### Requirements (Sections 4-7):
4. **User Stories** - Key user journeys with scenarios
5. **Functional Requirements** - What the system must do (categorized by component)
6. **Non-Functional Requirements** - Performance, scalability, reliability, security
7. **Acceptance Criteria** - How to verify each requirement is met

### Features & Data (Sections 8-10):
8. **Success Metrics** - KPIs, measurement strategy, baselines
9. **System Features** - Detailed feature specifications with priorities
10. **Data Requirements** - Data entities, flows, validation rules

### Constraints & Planning (Sections 11-15):
11. **Technical Constraints** - Limitations, boundaries, constraints
12. **Assumptions & Dependencies** - What we're assuming and relying on
13. **Out of Scope** - What we're explicitly NOT building
14. **Release Plan** - Phased rollout strategy with milestones
15. **Appendix** - References, glossary, additional context

---

## 💡 Tips

**Do:**
- ✅ Use specific, measurable requirements ("API response time < 200ms")
- ✅ Write testable acceptance criteria ("Given X, when Y, then Z")
- ✅ Prioritize features (P0/P1/P2 or Must-Have/Nice-to-Have)
- ✅ Include user persona details (job role, goals, pain points)
- ✅ Define success metrics with baselines (e.g., "improve forecast accuracy from 70% to 85%")
- ✅ Be explicit about what's out of scope
- ✅ Include rationale for major decisions
- ✅ Cross-reference related sections

**Don't:**
- ❌ Be vague ("system should be fast" → specify "API response < 200ms")
- ❌ Skip acceptance criteria (every requirement needs verification)
- ❌ Forget non-functional requirements (performance, security, etc.)
- ❌ Mix requirements with implementation details
- ❌ Leave priorities undefined (mark everything as P0/P1/P2)
- ❌ Skip the out-of-scope section (it's critical!)
- ❌ Forget to define success metrics

---

## 📁 File Naming

Save the output as: `prd_v1.0.md`

When you update it later:
- Minor changes: `prd_v1.1.md`, `v1.2.md`
- Major revisions: `prd_v2.0.md`
- Move old versions to `archive/` folder

---

## ✅ Completion Checklist

Before moving to implementation, verify:

- [ ] PM completed comprehensive requirements gathering session
- [ ] All 15 required sections present
- [ ] Executive summary with clear objectives complete
- [ ] Product vision and strategic goals defined
- [ ] Target user personas documented
- [ ] User stories written with scenarios
- [ ] All functional requirements specified (categorized)
- [ ] Non-functional requirements defined (performance, scalability, security)
- [ ] Acceptance criteria for all requirements (testable)
- [ ] Success metrics defined with baselines and targets
- [ ] System features detailed with priorities
- [ ] Data requirements documented
- [ ] Technical constraints identified
- [ ] Assumptions and dependencies listed
- [ ] Out of scope clearly defined
- [ ] Release plan with phased rollout
- [ ] Appendix with references and glossary
- [ ] All requirements are specific and measurable
- [ ] All acceptance criteria are testable
- [ ] Consistency check completed against Product Brief, Process Workflow, and Technical Architecture
- [ ] All contradictions resolved and prior documents updated if needed
- [ ] Document reviewed by product team
- [ ] Saved as `prd_v1.0.md`

**Time Investment:** 2-4 hours total
**Output:** Complete PRD (typically 30-80 pages)
**Next Document:** Frontend Spec (Design Spec)

---

## 🔄 Example Conversation Flow

**You:**
```
*agent pm
*create-prd
```

**PM (John):**
```
I'll help you create a comprehensive PRD using the prd template.
Let me walk you through each of the 15 sections.

=== Section 1: Executive Summary ===

[PM drafts initial content based on context or asks questions]

Here's my draft for the Executive Summary:
[Draft content including overview, objectives, key deliverables]

**Rationale:** [Explains decisions, assumptions, and alignment with business goals]

Please review. You can:
1. Proceed to next section
2. Challenge Assumptions
3. Explore Alternatives
4. Identify Risks
5. Stakeholder Perspective
6. Scale Analysis
7. Critique and Refine
8. User Impact Assessment
9. Prioritization Analysis

Select 1-9 or just type your question/feedback:
```

**You:**
```
1
```

**PM:**
```
Great! Moving to Section 2: Product Vision...

I'll help you articulate the long-term vision and strategic goals.
[Process repeats for all 15 sections]
```

---

**That's it!** The PM guides you through the template section-by-section with requirements-focused elicitation options.
