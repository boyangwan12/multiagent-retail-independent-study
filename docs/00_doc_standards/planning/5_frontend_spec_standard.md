# Frontend Spec (Design Spec) Standard

## 🎯 How to Create This Document

### Step 1: Create Frontend Spec with UX Expert (60-90 minutes)

```bash
*agent ux-expert

I need to create a comprehensive Frontend UI/UX Specification for my system.

*create-front-end-spec
```

**The UX Expert will:**
- Use the BMad `*task create-doc` workflow with the `front-end-spec-tmpl.yaml` template
- Walk you through all **13 sections** (listed below) one at a time
- After each section, present **9 elicitation options** (numbered 1-9):
  - Option 1: Proceed to next section
  - Options 2-9: Advanced elicitation methods to refine the section
- Provide UX best practices and design recommendations
- Wait for your response before continuing

**How to respond:**
- Type **1** to proceed to the next section
- Type **2-9** to use an elicitation method for deeper design exploration
- Or just type your feedback/questions directly

**The template includes all 13 required sections** covering design philosophy, user flows, wireframes, components, design system, accessibility, and more.

---

### Step 2: Review & Refine (As Needed)

**During the workflow**, you can refine any section by:
- Typing feedback directly (UX Expert will update the section)
- Using elicitation options 2-9 for design exploration
- Asking for wireframe refinements or component details

**After completion**, you can request changes:
- "Go back to Section X and add wireframes for the dashboard"
- "Include more detail on the button component specifications"
- "Define the color palette hex codes precisely"

---

### Step 3: Consistency Check & Update Prior Documents (30-45 minutes)

After drafting the Frontend Spec, check for contradictions with prior documents.

```bash
*agent ux-expert

Now that we have the Frontend Spec drafted, please:

1. **Compare with prior documents**: Read the Product Brief, Process Workflow, Technical Architecture, and PRD, and identify any contradictions between:
   - User flows vs. user stories in PRD
   - UI components vs. technical components in Technical Architecture
   - Design system vs. brand identity in Product Brief
   - Interaction patterns vs. workflow phases in Process Workflow
   - Performance targets vs. non-functional requirements in PRD
   - Accessibility requirements vs. user personas in PRD
   - State management vs. data models in Technical Architecture

2. **List contradictions one by one**: For each contradiction, show:
   - What the prior document says (specify Product Brief/Process Workflow/Technical Architecture/PRD)
   - What the Frontend Spec says
   - Why they conflict

3. **Ask for approval to update**: For each contradiction, ask me:
   "Should we update [Product Brief/Process Workflow/Technical Architecture/PRD] to align with this Frontend Spec insight?"

Do NOT auto-update. Present contradictions one at a time and wait for my approval.
```

**The UX Expert will:**
- Identify specific contradictions (e.g., "PRD specifies 3 user roles, but Frontend Spec shows 4 different dashboard layouts")
- Present each contradiction with line numbers/sections
- Ask: "Should we update PRD Section 3 to include the 4th user role (Admin) that needs a dashboard?"
- Wait for your approval before moving to next contradiction
- Update prior documents to v1.1 if changes are made

**If contradictions found:**
- Update prior documents to new version (v1.0 → v1.1)
- Move old version to `archive/`
- Update Frontend Spec to reference updated version numbers

---

### Step 4: Update Planning Guide

After completing the Frontend Spec, update the PLANNING_GUIDE.md to track your progress:

```bash
# Open the planning guide
# File: docs/00_doc_standards/planning/0_PLANNING_GUIDE.md

# Update Document #5 status:
- Change status from ❌ Not Started to ✅ Complete
- Update "Progress" counter (4/5 → 5/5)
- Update "Last Updated" date

# Save the file
```

**What to update:**
- Row 5 (Frontend Spec): `❌ Not Started` → `✅ Complete`
- Progress line: `**Progress**: 4/5 complete` → `**Progress**: 5/5 complete` 🎉
- Top of file: Update "Last Updated" date to today

**🎉 Congratulations!** You've completed all 5 planning documents. See "After Completing All 5 Documents" section in PLANNING_GUIDE.md for next steps.

---

## 📋 Required Sections (Agent will include these)

The frontend specification must contain all 13 sections:

### Foundation (Sections 1-3):
1. **Introduction** - Purpose, scope, target users, design philosophy
2. **UX Goals & Principles** - User experience objectives, design principles
3. **User Flows** - Key user journeys with step-by-step flows

### Visual Design (Sections 4-6):
4. **Wireframes/Mockups** - Visual representation of screens/components
5. **Component Library** - Reusable components with specifications
6. **Design System** - Colors, typography, spacing, icons, breakpoints

### Interaction & State (Sections 7-8):
7. **Interaction Patterns** - Click behaviors, hover states, forms, animations
8. **State Management** - How UI state is managed and synchronized

### Cross-Cutting Concerns (Sections 9-13):
9. **Responsive Design** - Mobile, tablet, desktop strategies
10. **Accessibility** - WCAG compliance, keyboard navigation, ARIA labels
11. **Performance** - Load time targets, bundle size, optimization
12. **Error Handling & Edge Cases** - Error messages, empty states, loading states
13. **Validation Checklist** - Completeness checklist

---

## 💡 Tips

**Do:**
- ✅ Include visual examples (ASCII art, diagrams, or reference screenshots)
- ✅ Specify exact design tokens (colors: #1E40AF, spacing: 16px, etc.)
- ✅ Document all component states (default, hover, active, disabled, error)
- ✅ Define responsive breakpoints (mobile: <768px, tablet: 768-1024px, desktop: >1024px)
- ✅ Include accessibility requirements (ARIA labels, keyboard shortcuts)
- ✅ Specify performance budgets (FCP < 1.5s, bundle < 200KB)
- ✅ Show error states and loading states for all interactive components
- ✅ Reference design system libraries (Material UI, Tailwind, etc.)

**Don't:**
- ❌ Be vague ("use nice colors" → specify "#1E40AF for primary brand color")
- ❌ Skip edge cases (error states, empty states, loading states)
- ❌ Forget mobile/responsive design
- ❌ Skip accessibility (keyboard navigation, screen readers)
- ❌ Leave interaction patterns undefined (what happens on click?)
- ❌ Mix design specs with implementation code
- ❌ Forget to document component props and variants

---

## 📁 File Naming

Save the output as: `frontend_spec_v1.0.md`

When you update it later:
- Minor changes: `frontend_spec_v1.1.md`, `v1.2.md`
- Major revisions: `frontend_spec_v2.0.md`
- Move old versions to `archive/` folder

---

## ✅ Completion Checklist

Before moving to implementation, verify:

- [ ] UX Expert completed comprehensive design planning session
- [ ] All 13 required sections present
- [ ] Introduction with purpose, scope, design philosophy complete
- [ ] UX goals and design principles defined
- [ ] All key user flows documented with step-by-step flows
- [ ] Wireframes/mockups for all major screens
- [ ] Component library defined with specifications
- [ ] Design system complete (colors, typography, spacing, icons)
- [ ] Interaction patterns documented (clicks, hovers, forms)
- [ ] State management strategy defined
- [ ] Responsive design strategy for all breakpoints
- [ ] Accessibility requirements specified (WCAG level, keyboard navigation)
- [ ] Performance targets defined (load time, bundle size)
- [ ] Error handling and edge cases documented
- [ ] Validation checklist included
- [ ] All components have states documented (default, hover, active, disabled, error)
- [ ] All design tokens specified (exact colors, spacing, fonts)
- [ ] Consistency check completed against Product Brief, Process Workflow, Technical Architecture, and PRD
- [ ] All contradictions resolved and prior documents updated if needed
- [ ] Document reviewed by design team
- [ ] Saved as `frontend_spec_v1.0.md`

**Time Investment:** 2-3 hours total
**Output:** Complete frontend specification (typically 20-50 pages)
**Next Step:** Implementation phase

---

## 🔄 Example Conversation Flow

**You:**
```
*agent ux-expert
*create-front-end-spec
```

**UX Expert (Sally):**
```
I'll help you create a comprehensive frontend specification using the front-end-spec template.
Let me walk you through each of the 13 sections.

=== Section 1: Introduction ===

[UX Expert drafts initial content based on context or asks questions]

Here's my draft for the Introduction:
[Draft content including purpose, scope, target users, design philosophy]

**Rationale:** [Explains design decisions, user research insights, UX trade-offs]

Please review. You can:
1. Proceed to next section
2. Challenge Assumptions
3. Explore Alternatives
4. User Perspective
5. Accessibility Review
6. Visual Design Deep Dive
7. Interaction Analysis
8. Mobile-First Assessment
9. Usability Critique

Select 1-9 or just type your question/feedback:
```

**You:**
```
1
```

**UX Expert:**
```
Great! Moving to Section 2: UX Goals & Principles...

I'll help you define user experience objectives and design principles.
[Process repeats for all 13 sections including wireframes, components, design system]
```

---

**That's it!** The UX Expert guides you through the template section-by-section with design-focused elicitation options.
