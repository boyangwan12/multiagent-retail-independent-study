# Process Workflow Standard

## 🎯 How to Create This Document

### Step 1: Create Process Workflow with Architect (45-60 minutes)

**Note:** This document uses a **conversational approach** (no template). The architect will interview you and draft the document naturally.

```bash
*agent architect

I need to create a process workflow document that explains how my system works operationally with concrete examples.

Based on the Product Brief, please interview me to understand:

1. **Core Methodology**: What's the key concept/approach? (e.g., "forecast once, allocate with math")
2. **Workflow Phases**: What are the major operational phases? (e.g., pre-season, in-season, etc.)
3. **Concrete Examples**: Walk through examples with real numbers
4. **Decision Logic**: What are the key decision thresholds and triggers?

Ask me questions **one at a time**. After gathering information, draft the process workflow document with these 3 sections:
1. Key Concept/Methodology
2. Workflow Phases
3. Concrete Examples

Use concrete examples and real numbers throughout.
```

**The architect will:**
- Ask questions one-by-one to understand your operational flow
- Probe for concrete examples with actual numbers
- Draft the document conversationally (not using a template)
- Include all 3 required sections with detailed examples

**Answer with concrete examples:**
- Use real numbers (8,000 units, 50 stores, Week 6, etc.)
- Provide step-by-step walkthroughs
- Explain decision thresholds (>20% variance, etc.)

---

### Step 2: Review & Add Examples (15-30 minutes)

**Review the draft and:**
- Add 2-4 example scenarios showing different system behaviors
- Validate all formulas with concrete numbers
- Ensure decision thresholds are clearly specified
- Check that examples are complete (inputs → process → outputs)

**Provide feedback like:**
- "Add a scenario for when demand exceeds forecast"
- "The calculation needs a concrete example"
- "Show the workflow example with actual numbers"

**The architect will iterate** until all examples are concrete and complete.

---

### Step 3: Consistency Check & Update Prior Documents (30-45 minutes)

After drafting the Process Workflow, check for contradictions with the Product Brief.

```bash
*agent architect

Now that we have the Process Workflow drafted, please:

1. **Compare with Product Brief**: Read the Product Brief and identify any contradictions between:
   - The workflow phases vs. features described in Product Brief
   - Concrete examples vs. business requirements
   - Decision thresholds vs. success metrics

2. **List contradictions one by one**: For each contradiction, show:
   - What the Product Brief says
   - What the Process Workflow says
   - Why they conflict

3. **Ask for approval to update**: For each contradiction, ask me:
   "Should we update the Product Brief to align with this Process Workflow insight?"

Do NOT auto-update. Present contradictions one at a time and wait for my approval.
```

**The architect will:**
- Identify specific contradictions (e.g., "Product Brief mentions 4 phases, but Process Workflow defines 5 phases")
- Present each contradiction with line numbers/sections
- Ask: "Should we update Product Brief Section 3 to reflect 5 phases instead of 4?"
- Wait for your approval before moving to next contradiction
- Update Product Brief to v1.1 if changes are made

**If contradictions found:**
- Update Product Brief to new version (v1.0 → v1.1)
- Move old version to `archive/`
- Update Process Workflow to reference "Product Brief v1.1"

---

### Step 4: Update Planning Guide

After completing the Process Workflow, update the PLANNING_GUIDE.md to track your progress:

```bash
# Open the planning guide
# File: docs/00_doc_standards/planning/PLANNING_GUIDE.md

# Update Document #2 status:
- Change status from ❌ Not Started to ✅ Complete
- Update "Progress" counter (1/5 → 2/5)
- Update "Last Updated" date

# Save the file
```

**What to update:**
- Row 2 (Process Workflow): `❌ Not Started` → `✅ Complete`
- Progress line: `**Progress**: 1/5 complete` → `**Progress**: 2/5 complete`
- Top of file: Update "Last Updated" date to today

---

## 📋 Required Sections (Agent will include these)

The process workflow should contain:

1. **Key Concept/Methodology** - Core approach in simple terms with visual example
2. **Workflow Phases** - Step-by-step operational flow with timing
3. **Concrete Examples** - Detailed walkthrough with real numbers (at least 1 major example)

---

## 💡 Tips

**Do:**
- ✅ Use real numbers in examples (8,000 units, 50 stores, Week 6, etc.)
- ✅ Show complete calculation flows (input → formula → output)
- ✅ Include multiple scenarios (success case, high demand, low demand)
- ✅ Specify exact decision thresholds (>20% variance, Week 6 checkpoint, etc.)
- ✅ Use ASCII diagrams or bullet hierarchies to show flows
- ✅ Reference other documents (Product Brief, Architecture) for context

**Don't:**
- ❌ Be vague ("some number of stores" → use "50 stores")
- ❌ Skip calculations ("then we calculate" → show: "8,000 × 1.20 = 9,600")
- ❌ Only document happy path - show failure scenarios too
- ❌ Mix conceptual explanation with implementation details
- ❌ Forget to show phase transitions and triggers

---

## 📁 File Naming

Save the output as: `process_workflow_v1.0.md`

When you update it later:
- Minor changes: `process_workflow_v1.1.md`, `v1.2.md`
- Major revisions: `process_workflow_v2.0.md`
- Move old versions to `archive/` folder

---

## ✅ Completion Checklist

Before moving to next planning document, verify:

- [ ] Architect completed technical deep-dive
- [ ] Key concept/methodology clearly explained
- [ ] All workflow phases documented with timing
- [ ] At least 1 major example with complete calculations
- [ ] All formulas validated with concrete numbers
- [ ] Decision thresholds clearly specified
- [ ] Consistency check completed against Product Brief
- [ ] All contradictions resolved and Product Brief updated if needed
- [ ] Document reviewed by technical stakeholders
- [ ] Saved as `process_workflow_v1.0.md`

**Time Investment:** 1-2 hours total
**Output:** Complete process workflow (typically 10-20 pages with examples)
**Next Document:** Technical Architecture

---

## 🔄 Example Conversation Flow

**You:**
```
*agent architect
I need to create a process workflow document.
[paste the initiation prompt above]
```

**Architect:**
```
I'd be happy to help! Let's start by understanding your core operational approach.

Question 1: What's the key concept or methodology your system uses?
Can you explain it in simple terms?
```

**You:**
```
We forecast demand once at the category level, then use clustering and
historical patterns to allocate to stores. We don't forecast at the
store-by-week level.
```

**Architect:**
```
Excellent. That's a "forecast once, allocate with math" approach.

Question 2: Can you walk me through a concrete example? Let's say you
need to forecast for 50 stores over 12 weeks. What are the actual numbers?
```

**You:**
```
Sure. We forecast 8,000 units total for Women's Dresses. Then we cluster
the 50 stores into 3 groups: Fashion Forward (40%), Mainstream (35%),
Value (25%). Within each cluster we allocate by historical sales patterns...
```

**[Conversation continues with concrete examples...]**

**Architect (Winston):**
```
Excellent! Based on our conversation, I'll now draft the process workflow document.

I'll structure it with the 3 required sections:
1. Key Concept: "Forecast Once, Allocate with Math"
2. Workflow Phases: 5 phases (Pre-Season, Season Start, In-Season, Mid-Season, Season End)
3. Concrete Example: 8,000 units → 3 clusters → 50 stores with complete calculations

Let me draft this now...

[Architect creates document conversationally, section by section]
```

---

**That's it!** The architect walks through concrete examples with you and creates a detailed process workflow.
