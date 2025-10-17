# Story: Build Section 0 - Parameter Gathering UI

**Epic:** Phase 2 - Complete Frontend Implementation
**Story ID:** PHASE2-003
**Status:** Draft
**Estimate:** 4 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE2-001, PHASE2-002

---

## Story

As a retail planner,
I want to provide season parameters in natural language,
So that the system can extract structured parameters and configure the forecast workflow.

**Business Value:** Reduces planning time from 15 minutes (manual forms) to <2 minutes (natural language). First user interaction - must be intuitive and transparent.

**Epic Context:** Section 0 is the entry point for all workflows. Without confirmed parameters, forecasting cannot begin.

---

## Acceptance Criteria

1. ✅ Textarea with 500 char limit + character counter
2. ✅ "Extract Parameters" button with 2-5s loading animation
3. ✅ Mock LLM extraction (regex-based, 5 parameters)
4. ✅ Parameter Confirmation Modal with 5 cards
5. ✅ Expandable extraction reasoning section
6. ✅ "Edit Parameters" returns to textarea
7. ✅ "Confirm" collapses to read-only banner
8. ✅ Error handling for incomplete extractions
9. ✅ Network error retry with exponential backoff
10. ✅ Agent Reasoning Preview section

---

## Tasks

### Task 1: Create Parameter Textarea Component
- [ ] Create `src/components/ParameterGathering/ParameterTextarea.tsx`
- [ ] Add 500 char limit with counter
- [ ] "Extract Parameters" button
- [ ] Loading state (2-5s delay)
- [ ] Linear Dark Theme styling

### Task 2: Implement Mock LLM Extraction
- [ ] Create `src/utils/extractParameters.ts`
- [ ] Regex for "X weeks" → forecast_horizon_weeks
- [ ] Regex for "starting [date]" → season_start_date
- [ ] Regex for replenishment strategy
- [ ] Regex for holdback percentage
- [ ] Regex for markdown checkpoint
- [ ] Return confidence: high/medium/low
- [ ] Generate reasoning explanation

### Task 3: Build Parameter Confirmation Modal
- [ ] Create `src/components/ParameterGathering/ParameterConfirmationModal.tsx`
- [ ] Use Shadcn Dialog component
- [ ] Display 5 parameter cards (grid layout)
- [ ] Expandable "Extraction Reasoning" (Accordion)
- [ ] "Edit Parameters" button
- [ ] "Confirm" button

### Task 4: Build Parameter Card Component
- [ ] Create `src/components/ParameterGathering/ParameterCard.tsx`
- [ ] Display name, value, icon (lucide-react)
- [ ] Handle types: number, date, enum, percentage
- [ ] Tooltips for explanations
- [ ] Reusable (used 5x in modal)

### Task 5: Build Confirmed Banner
- [ ] Create `src/components/ParameterGathering/ConfirmedBanner.tsx`
- [ ] Collapsed state after confirmation
- [ ] Show all 5 parameters inline
- [ ] "Edit" button to expand
- [ ] Muted background (#1f1f23)

### Task 6: Add Error Handling
- [ ] Handle incomplete extractions (<3 params)
- [ ] Toast error with missing parameters
- [ ] Network error retry button
- [ ] Exponential backoff (1s, 2s, 4s, 8s)

### Task 7: Build Agent Reasoning Preview
- [ ] Show how parameters affect each agent
- [ ] Demand: "Using X% safety stock"
- [ ] Inventory: "DC holdback at X%"
- [ ] Pricing: "Markdown checkpoint Week X"

### Task 8: Integration & Testing
- [ ] Test 5 input examples (Zara, Standard, Luxury, etc.)
- [ ] Verify character counter
- [ ] Test error states
- [ ] Test responsive design

---

## Dev Notes

**Example Input (Zara-style):**
```
"12-week spring season starting March 1st.
No replenishment, 0% holdback.
Markdown at week 6 if below 60% sell-through."
```

**Expected Extraction:**
```json
{
  "forecast_horizon_weeks": 12,
  "season_start_date": "2025-03-01",
  "replenishment_strategy": "none",
  "dc_holdback_percentage": 0.0,
  "markdown_checkpoint_week": 6,
  "markdown_threshold": 0.60,
  "extraction_confidence": "high"
}
```

**Reference:** `planning/5_front-end-spec_v3.3.md` lines 450-550

---

## Testing

- [ ] Test Case 1: Zara-style (no replenishment)
- [ ] Test Case 2: Standard retail (weekly replenishment)
- [ ] Test Case 3: Incomplete input (error handling)
- [ ] Test Case 4: Network error (retry logic)
- [ ] Test Case 5: Edit workflow

---

## File List

_Dev Agent populates during implementation_

---

## Dev Agent Record

### Debug Log
_Logs here_

### Completion Notes
_Notes here_

### Change Log
_Changes here_

---

## Definition of Done

- [x] All 8 tasks complete
- [x] 5 test cases pass
- [x] Responsive design verified
- [x] File List updated

---

**Created:** 2025-10-17
**Story Points:** 4
**Priority:** P0
