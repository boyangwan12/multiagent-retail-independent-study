# Phase 2 Frontend Implementation - Quick Start

**To:** Jintao
**Phase:** Phase 2 - Complete Frontend Implementation
**Timeline:** 5-7 days (41 hours)
**Goal:** Build React dashboard with 8 sections using BMAD methodology

---

## What You're Building

A **React dashboard** with these 8 sections:
1. **Section 0:** Parameter Gathering (text input → extract 5 parameters)
2. **Section 1:** Agent Cards (3 agents with status animations)
3. **Section 2:** Forecast Summary (4 metric cards)
4. **Section 3:** Cluster Cards (3 tables with sorting/filtering)
5. **Section 4:** Weekly Chart (forecast vs actuals with variance)
6. **Section 5:** Replenishment Queue (store recommendations)
7. **Section 6:** Markdown Decision (slider with impact preview)
8. **Section 7:** Performance Metrics (MAPE, accuracy, system stats)

**Plus:** Navigation, error handling, report page, documentation

---

## How to Start (3 Steps)

### Step 1: Review Documents (30 mins)

Read these files in this order:
1. `docs/04_MVP_Development/implementation/phase_2_frontend/implementation_plan.md` (your roadmap)
2. `docs/04_MVP_Development/implementation/phase_2_frontend/checklist.md` (your progress tracker)
3. `docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md` (design specs)

### Step 2: Start Dev Agent (5 mins)

```bash
# Open Claude Code
claude code

# Activate orchestrator
/BMad:agents:bmad-orchestrator

# Switch to dev agent
*agent dev

# Start first story
Implement Phase 2: Start with story PHASE2-001
```

### Step 3: Follow the Stories (5-7 days)

The dev agent will read each story and implement it for you. Just tell it:
- "Continue with next story" (after each completes)
- "Start PHASE2-XXX" (to jump to specific story)

---

## 7-Day Plan

### Day 1: Setup
- **PHASE2-001:** Vite + React + TypeScript + Linear Dark Theme
- **PHASE2-002:** Convert CSV data to JSON fixtures, mock WebSocket

### Day 2: First Sections
- **PHASE2-003:** Section 0 (Parameter Gathering)
- **PHASE2-004:** Section 1 (Agent Cards)

### Day 3: Data Tables
- **PHASE2-005:** Section 2 (Forecast Summary)
- **PHASE2-006:** Section 3 (Cluster Cards with TanStack Table) ← Longest task (6h)

### Day 4: Charts
- **PHASE2-007:** Section 4 (Weekly Chart)
- **PHASE2-008:** Section 5 (Replenishment Queue)

### Day 5: Decisions & Metrics
- **PHASE2-009:** Section 6 (Markdown Decision)
- **PHASE2-010:** Section 7 (Performance Metrics)

### Day 6: Polish
- **PHASE2-011:** Navigation & Layout
- **PHASE2-012:** Error Handling & Accessibility
- **PHASE2-014:** Report Page

### Day 7: Documentation
- **PHASE2-013:** Write docs, test all flows, prepare demo

---

## Technology Stack

- **Vite** (build tool, super fast)
- **React 18** + **TypeScript** (UI framework)
- **Shadcn/ui** (component library)
- **Tailwind CSS** (styling with Linear Dark Theme)
- **TanStack Table** (data tables)
- **Recharts** (charts)

All dependencies installed automatically by dev agent in PHASE2-001.

---

## BMAD Workflow Basics

**BMAD = Story-Driven Development**

1. Each story has:
   - What to build (acceptance criteria)
   - How to build it (tasks)
   - How to test it (test cases)

2. Dev agent:
   - Reads story
   - Implements code
   - Runs tests
   - Updates story with what changed

3. Your job:
   - Tell agent which story to do next
   - Review the code it writes
   - Test the UI in browser (http://localhost:5173)
   - Commit daily to git

---

## Daily Git Commits

At end of each day:

```bash
git add .
git commit -m "Phase 2 Day X: Completed PHASE2-XXX through PHASE2-YYY

- Implemented Section X
- Implemented Section Y

Status: X/14 tasks complete"

git push origin main
```

---

## Testing Checklist

After Day 7, verify:

- [ ] `npm run build` (no errors)
- [ ] `npm run dev` (opens http://localhost:5173)
- [ ] All 8 sections visible on screen
- [ ] Parameter extraction works (Section 0)
- [ ] Agent cards animate (Section 1)
- [ ] Tables sort/filter (Sections 3, 5)
- [ ] Chart shows variance (Section 4)
- [ ] Markdown slider updates preview (Section 6)
- [ ] Report page accessible at `/reports/spring-2025`
- [ ] No console errors
- [ ] Accessibility audit passes: `npx axe-cli http://localhost:5173`

---

## Presentation Requirements (Friday)

Create **10-12 slides** covering:

1. **Title:** Phase 2 Progress Report
2. **Overview:** What you built (8 sections)
3. **BMAD Method:** How you built it (story-driven with AI agent)
4. **Tech Stack:** Vite, React, TypeScript, Shadcn, TanStack Table, Recharts
5. **Progress:** X/14 tasks complete (show checklist table)
6. **Achievements:** Linear Dark Theme, TanStack Table, Mock WebSocket
7. **Challenges:** What was hard and how you solved it
8. **Demo:** Live demo (or video if not ready) - 3 minutes
9. **Testing:** Build passes, accessibility passes, bundle <500KB
10. **Next Steps:** Phase 3 backend integration
11. **Q&A**

**Demo tips:**
- Test demo beforehand
- Record backup video (2 min)
- Show parameter extraction → agent cards → cluster table → chart

---

## Help & Support

**Stuck on a story?**
- Read "Dev Notes" section in the story (has code examples)
- Check planning spec: `docs/04_MVP_Development/planning/5_front-end-spec_v3.3.md`

**Build errors?**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Agent not working?**
```bash
*exit
/BMad:agents:bmad-orchestrator
*agent dev
```

**Questions?**
- Project docs: `docs/04_MVP_Development/implementation/phase_2_frontend/`
- Claude Code docs: https://docs.claude.com/claude-code
- Shadcn/ui docs: https://ui.shadcn.com
- TanStack Table docs: https://tanstack.com/table/latest

---

## Success Criteria

Phase 2 is complete when:

✅ All 14 stories complete (checklist.md shows 14/14)
✅ Build passes with no errors
✅ All 8 sections functional
✅ Accessibility audit passes (WCAG 2.1 AA)
✅ Documentation written (README.md)
✅ Presentation delivered on Friday
✅ Code pushed to git

---

**Good luck! The BMAD agent will guide you through each story.** 🚀

**Remember:** Take screenshots daily for your presentation slides!

---

**Last Updated:** 2025-10-17
**Status:** Ready for Implementation
