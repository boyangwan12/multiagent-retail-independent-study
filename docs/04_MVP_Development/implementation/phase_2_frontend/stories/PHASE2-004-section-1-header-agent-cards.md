# Story: Build Section 1 - Fixed Header & Agent Cards

**Epic:** Phase 2 - Complete Frontend Implementation
**Story ID:** PHASE2-004
**Status:** Draft
**Estimate:** 3 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE2-002

---

## Story

As a user,
I want to see a fixed header with scenario details and real-time agent progress cards,
So that I can track the forecast workflow execution at a glance.

**Business Value:** Provides transparency into the multi-agent workflow. Users see which agent is working and overall progress.

---

## Acceptance Criteria

1. ✅ Fixed header with scenario name, date range, progress bar
2. ✅ 3 agent cards (Demand, Inventory, Pricing)
3. ✅ WebSocket mock for agent status updates
4. ✅ Animated transitions: Idle → Thinking → Complete
5. ✅ Agent icons (lucide-react)
6. ✅ Progress indicators per agent

---

## Tasks

### Task 1: Create FixedHeader Component
- [ ] Create `src/components/FixedHeader.tsx`
- [ ] Display scenario name ("Spring 2025 Forecast")
- [ ] Display date range from parameters
- [ ] Overall progress bar (0-100%)
- [ ] Sticky positioning (top of page)

### Task 2: Build AgentCard Component
- [ ] Create `src/components/AgentCard.tsx`
- [ ] Agent name + icon
- [ ] Status badge (Idle/Thinking/Complete)
- [ ] Progress percentage
- [ ] Animated pulse effect when "Thinking"
- [ ] Props: `{name, icon, status, progress, message}`

### Task 3: Integrate Mock WebSocket
- [ ] Use `MockWebSocket` from PHASE2-002
- [ ] Subscribe to agent status updates
- [ ] Update AgentCard states in real-time
- [ ] Test 3 agents progress sequentially

### Task 4: Add Status Animations
- [ ] Idle: Gray color (#878787)
- [ ] Thinking: Blue pulse animation (#5e6ad2)
- [ ] Complete: Green checkmark (#10b981)
- [ ] Error: Red (#ef4444)
- [ ] Smooth transitions (300ms ease)

### Task 5: Create Agent Icons
- [ ] Demand Agent: TrendingUp icon
- [ ] Inventory Agent: Package icon
- [ ] Pricing Agent: DollarSign icon
- [ ] Use lucide-react library

### Task 6: Add Progress Bar
- [ ] Overall progress across all 3 agents
- [ ] Calculate: (completed_agents / total_agents) * 100
- [ ] Animated width transition
- [ ] Show percentage text

---

## Dev Notes

**Agent Progression:**
1. Demand Agent: 0% → 100% (6 seconds)
2. Inventory Agent: 33% → 100% (4 seconds)
3. Pricing Agent: 66% → 100% (2 seconds)

**Reference:** `planning/5_front-end-spec_v3.3.md` lines 550-650

---

## Testing

- [ ] Fixed header stays at top when scrolling
- [ ] Agent cards update in sequence
- [ ] Animations smooth and visible
- [ ] Progress bar accurate
- [ ] Responsive on mobile

---

## File List

_Dev Agent populates_

---

## Dev Agent Record

### Debug Log
_Logs here_

---

## Definition of Done

- [x] All 6 tasks complete
- [x] WebSocket integration working
- [x] Animations tested
- [x] Responsive design verified

---

**Created:** 2025-10-17
**Story Points:** 3
**Priority:** P1
