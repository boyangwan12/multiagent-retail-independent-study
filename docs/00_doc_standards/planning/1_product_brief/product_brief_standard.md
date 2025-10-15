# Product Brief Standard

## 🎯 How to Create This Document

### Step 1: Create Product Brief with Analyst (45-60 minutes)

```bash
*agent analyst

I need to create a product brief for a new project.

*create-project-brief
```

**The analyst will:**
- Use the BMad `*task create-doc` workflow with the `project-brief-tmpl.yaml` template
- Ask you questions **one section at a time** to populate the template
- After each section, present **9 elicitation options** (numbered 1-9):
  - Option 1: Proceed to next section
  - Options 2-9: Advanced elicitation methods to refine the section
- Wait for your response before continuing

**How to respond:**
- Type **1** to proceed to the next section
- Type **2-9** to use an elicitation method for deeper exploration
- Or just type your feedback/questions directly

**The template includes all 11 required sections** - the agent will guide you through each one.

---

### Step 2: Review & Refine (As Needed)

**During the workflow**, you can refine any section by:
- Typing feedback directly (agent will update the section)
- Using elicitation options 2-9 for deeper exploration
- Asking questions

**After completion**, you can request changes:
- "Go back to Section X and add more detail on Y"
- "Update the MVP timeline"

---

### Step 3: Technical Validation (Optional)

```bash
*agent architect

Please review this product brief and validate:
- Technical feasibility
- Architecture approach
- Data requirements
- Technology stack choices
- Risks and constraints

Provide feedback on any technical concerns.
```

---

### Step 4: Update Planning Guide

After completing the Product Brief, update the PLANNING_GUIDE.md to track your progress:

```bash
# Open the planning guide
# File: docs/00_doc_standards/planning/PLANNING_GUIDE.md

# Update Document #1 status:
- Change status from ❌ Not Started to ✅ Complete
- Update "Progress" counter (0/5 → 1/5)
- Update "Last Updated" date

# Save the file
```

**What to update:**
- Row 1 (Product Brief): `❌ Not Started` → `✅ Complete`
- Progress line: `**Progress**: 0/5 complete` → `**Progress**: 1/5 complete`
- Top of file: Update "Last Updated" date to today

---

## 📋 Required Sections (Agent will include these)

The product brief should contain:

1. **Executive Summary** - Problem we solve + Our solution
2. **Business Value** - Quantified benefits
3. **Product Scope** - What we're building (and NOT building)
4. **Target Users** - 2-4 personas with pain points
5. **Core Features** - 5-7 key capabilities
6. **MVP Scope** - What's in MVP, what's post-MVP, timeline
7. **Data Requirements** - Input data needed, output data generated
8. **Technical Architecture** - High-level system overview
9. **Assumptions & Constraints** - What we're assuming, limitations
10. **Risks & Mitigation** - Potential problems and solutions
11. **Next Steps** - Immediate actions

---

## 💡 Tips

**Do:**
- ✅ Let the analyst ask you questions - don't dump everything at once
- ✅ Provide specific examples and quantified impact
- ✅ Be honest about constraints and unknowns
- ✅ Iterate on the draft - first version won't be perfect

**Don't:**
- ❌ Try to write it yourself - let the agents do the work
- ❌ Skip the analyst research phase - it provides crucial context
- ❌ Accept first draft without review - always refine
- ❌ Mix planning with implementation - stay high-level

---

## 📁 File Naming

Save the output as: `product_brief_v1.0.md`

When you update it later:
- Minor changes: `product_brief_v1.1.md`, `v1.2.md`
- Major revisions: `product_brief_v2.0.md`
- Move old versions to `archive/` folder

---

## ✅ Completion Checklist

Before moving to next planning document, verify:

- [ ] Analyst research phase completed
- [ ] PM drafted complete product brief
- [ ] All 11 required sections present
- [ ] Pain points quantified (hours lost, $ impact, etc.)
- [ ] 2-4 user personas defined
- [ ] 5-7 core features described
- [ ] MVP scope clearly bounded
- [ ] Technical architecture validated by architect
- [ ] Document reviewed and approved by stakeholders
- [ ] Saved as `product_brief_v1.0.md`

**Time Investment:** 1-2 hours total
**Output:** Complete product brief (typically 5-10 pages)
**Next Document:** Process Workflow

---

## 🔄 Example Conversation Flow

**You:**
```
*agent analyst
*create-project-brief
```

**Analyst (Mary):**
```
I'll help you create a product brief using the project-brief template.
Let me walk you through each section.

=== Section 1: Executive Summary ===

[Analyst drafts initial content based on context or asks questions]

Here's my draft for the Executive Summary:
[Draft content]

**Rationale:** [Explains assumptions and decisions made]

Please review. You can:
1. Proceed to next section
2. Challenge Assumptions
3. Explore Alternatives
4. Identify Risks
5. Stakeholder Perspective
6. Scale Up/Down
7. Critique and Refine
8. Red Team Analysis
9. Tree of Thoughts

Select 1-9 or just type your question/feedback:
```

**You:**
```
1
```

**Analyst:**
```
Great! Moving to Section 2: Business Value...
[Process repeats for all 11 sections]
```

---

**That's it!** The analyst guides you through the template section-by-section with built-in elicitation options.
