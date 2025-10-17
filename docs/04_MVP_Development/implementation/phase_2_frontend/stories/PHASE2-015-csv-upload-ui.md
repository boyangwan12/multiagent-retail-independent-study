# Story: Build CSV Upload UI (Optional for MVP)

**Epic:** Phase 2 - Complete Frontend Implementation
**Story ID:** PHASE2-015
**Status:** Draft (Optional - Mock Data Fallback)
**Estimate:** 2 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE2-001, PHASE2-002

---

## Story

As a retail planner,
I want to upload historical sales and store attribute CSV files,
So that I can trigger the forecast workflow with my own data instead of using mock data.

**Business Value:** Enables testing with real data during Phase 2 development. Without this, developers must manually edit JSON fixtures for every test scenario. This is optional for MVP since mock data suffices for UI development.

**Epic Context:** Flow 1 (Pre-Season Forecast) in planning spec describes CSV upload as the entry point for forecasting. This story implements that UI, but can be deferred if mock data is sufficient.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ "Upload Historical Sales CSV" button with file input
2. ✅ CSV validation (date, category, store_id, quantity_sold, revenue columns)
3. ✅ CSV preview modal showing first 10 rows
4. ✅ Category dropdown auto-populates from uploaded CSV
5. ✅ "Upload Store Attributes CSV" button with validation
6. ✅ Store attributes validation (50 stores, 7 required columns)
7. ✅ Season date picker (start and end dates)
8. ✅ "Run Forecast" button (disabled until both CSVs uploaded)
9. ✅ Error messages for invalid CSV format
10. ✅ Loading state during CSV parsing

### Quality Requirements

11. ✅ File size limit (10MB max per CSV)
12. ✅ Supports .csv files only (reject .xlsx, .xls)
13. ✅ Accessible file inputs (keyboard navigation)
14. ✅ Clear error messages with expected format examples

---

## Tasks

### Task 1: Create CSV Upload Button Component
- [ ] Create `src/components/CSVUpload/UploadButton.tsx`
- [ ] File input with accept=".csv"
- [ ] Icon: `Upload` from lucide-react
- [ ] Loading state during parse
- [ ] Disabled state after successful upload
- [ ] Shadcn Button component

### Task 2: Implement CSV Parser
- [ ] Create `src/utils/csvParser.ts`
- [ ] Use PapaParse library: `npm install papaparse @types/papaparse`
- [ ] Parse CSV to JSON array
- [ ] Validate required columns
- [ ] Validate data types (dates, numbers)
- [ ] Return errors with row numbers

### Task 3: Build CSV Preview Modal
- [ ] Create `src/components/CSVUpload/CSVPreviewModal.tsx`
- [ ] Use Shadcn Dialog component
- [ ] Display first 10 rows in table
- [ ] Show row count: "54,750 rows detected"
- [ ] Show columns detected
- [ ] "Cancel" and "Confirm Upload" buttons
- [ ] Display validation errors if any

### Task 4: Build Historical Sales Upload Section
- [ ] Create `src/components/CSVUpload/HistoricalSalesUpload.tsx`
- [ ] "Upload Historical Sales CSV" button
- [ ] Expected format help text:
  - "Columns: date, category, store_id, quantity_sold, revenue"
  - "Date range: 2+ years of daily data"
  - "~54,750 rows (50 stores × 365 days × 3 years)"
- [ ] Success state: "✓ 54,750 rows uploaded"
- [ ] Extract unique categories for dropdown

### Task 5: Build Store Attributes Upload Section
- [ ] Create `src/components/CSVUpload/StoreAttributesUpload.tsx`
- [ ] "Upload Store Attributes CSV" button
- [ ] Expected format help text:
  - "Columns: store_id, store_name, store_size_sqft, location_tier, median_income, store_format, region, avg_weekly_sales_12mo, fashion_tier"
  - "50 stores required (S01-S50)"
- [ ] Validate exactly 50 stores
- [ ] Success state: "✓ 50 stores uploaded"

### Task 6: Build Category Selector
- [ ] Create `src/components/CSVUpload/CategorySelector.tsx`
- [ ] Dropdown auto-populated from historical sales CSV
- [ ] Disabled until CSV uploaded
- [ ] Shadcn Select component
- [ ] Example categories: "Women's Dresses", "Men's Shirts", "Accessories"

### Task 7: Build Season Date Picker
- [ ] Create `src/components/CSVUpload/SeasonDatePicker.tsx`
- [ ] Start date and end date inputs
- [ ] Use Shadcn Calendar/Popover components
- [ ] Auto-calculate forecast horizon (weeks)
- [ ] Validation: End date must be after start date
- [ ] Display: "12 weeks (Mar 1 - May 23, 2025)"

### Task 8: Build Run Forecast Button
- [ ] Create `src/components/CSVUpload/RunForecastButton.tsx`
- [ ] Large primary button
- [ ] Disabled state logic:
  - Both CSVs uploaded
  - Category selected
  - Dates selected
- [ ] Click triggers Section 1 agent workflow
- [ ] Loading state: "Running Forecast..."

### Task 9: Error Handling & Validation
- [ ] Invalid CSV format → Toast error with details
- [ ] Missing columns → Toast: "Missing required columns: date, category"
- [ ] Wrong date range → Toast: "Expected 2+ years of data, found 6 months"
- [ ] Missing stores → Toast: "Missing stores: S15, S22, S38"
- [ ] Duplicate uploads → Confirm overwrite dialog
- [ ] File too large (>10MB) → Toast error

### Task 10: Integration with Mock Data
- [ ] If no CSV uploaded → Use JSON fixtures from Phase 1
- [ ] "Use Sample Data" button as fallback
- [ ] Switch between uploaded data and mock data
- [ ] Store CSV data in React Context

---

## Dev Notes

### CSV Parser Setup

```bash
npm install papaparse @types/papaparse
```

### Historical Sales CSV Example

```csv
date,category,store_id,quantity_sold,revenue
2022-01-01,Women's Dresses,S01,15,450.00
2022-01-01,Women's Dresses,S02,12,360.00
2022-01-01,Men's Shirts,S01,8,240.00
```

**Expected:**
- 54,750 rows (50 stores × 365 days × 3 years)
- Categories: Women's Dresses, Men's Shirts, Accessories
- Date range: 2022-01-01 to 2024-12-31

### Store Attributes CSV Example

```csv
store_id,store_name,store_size_sqft,location_tier,median_income,store_format,region,avg_weekly_sales_12mo,fashion_tier
S01,Downtown NYC,20000,A,95000,MALL,NORTHEAST,285,PREMIUM
S02,LA Mall,18000,A,88000,MALL,WEST,260,PREMIUM
```

**Expected:**
- Exactly 50 stores (S01-S50)
- All 9 columns required

### Planning Spec Reference

**Flow 1 (Pre-Season Forecast):** `planning/5_front-end-spec_v3.3.md` lines 267-308

**Specific steps:**
- Line 274: "Click 'Upload Historical Sales CSV'"
- Line 275: "System validates & parses (must contain: date, category, store_id, quantity_sold)"
- Line 276: "Shows preview: '✓ 10,243 rows | Categories detected: Women's Dresses, Men's Shirts, Accessories'"
- Line 277: "Click 'Upload Store Attributes CSV'"
- Line 278: "System validates: 50 stores, 7 features (avg_weekly_sales_12mo, store_size_sqft, median_income, location_tier, fashion_tier, store_format, region)"
- Line 279: "Category dropdown auto-populates (detected from CSV)"
- Line 281: "Season date picker: Start 2025-03-01, End 2025-05-23"
- Line 282: "Forecast horizon auto-calculates: 12 weeks"
- Line 283: "Click 'Run Forecast' button"

### Data Generation Reference

**CSV Structure:** `planning/5_front-end-spec_v3.3.md` lines 1375-1454

---

## Testing

### Test Case 1: Valid CSV Upload
- [ ] Upload valid historical sales CSV (54,750 rows)
- [ ] Preview modal shows 10 rows correctly
- [ ] Category dropdown populates with 3 categories
- [ ] Upload store attributes CSV (50 stores)
- [ ] "Run Forecast" button becomes enabled
- [ ] Click button → Triggers agent workflow

### Test Case 2: Invalid Historical Sales CSV
- [ ] Upload CSV missing "date" column
- [ ] Toast error: "Missing required columns: date"
- [ ] Button remains disabled

### Test Case 3: Invalid Store Attributes CSV
- [ ] Upload CSV with only 45 stores
- [ ] Toast error: "Expected 50 stores, found 45. Missing: S46, S47, S48, S49, S50"

### Test Case 4: Duplicate Upload
- [ ] Upload historical sales CSV
- [ ] Upload again
- [ ] Confirm overwrite dialog appears
- [ ] Click "Overwrite" → Replaces data
- [ ] Click "Cancel" → Keeps existing data

### Test Case 5: Fallback to Mock Data
- [ ] No CSV uploaded
- [ ] Click "Use Sample Data" button
- [ ] Loads JSON fixtures from Phase 1
- [ ] Category dropdown shows "Women's Dresses"
- [ ] "Run Forecast" button enabled

---

## File List

_Dev Agent populates during implementation_

**New Files:**
- `src/components/CSVUpload/UploadButton.tsx`
- `src/components/CSVUpload/CSVPreviewModal.tsx`
- `src/components/CSVUpload/HistoricalSalesUpload.tsx`
- `src/components/CSVUpload/StoreAttributesUpload.tsx`
- `src/components/CSVUpload/CategorySelector.tsx`
- `src/components/CSVUpload/SeasonDatePicker.tsx`
- `src/components/CSVUpload/RunForecastButton.tsx`
- `src/utils/csvParser.ts`
- `src/utils/csvValidator.ts`

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

- [x] All 10 tasks complete
- [x] 5 test cases pass
- [x] PapaParse integrated
- [x] CSV validation works correctly
- [x] Error messages are clear and actionable
- [x] Fallback to mock data works
- [x] File List updated

---

## Optional vs Required Decision

**Decision:** This story is **OPTIONAL for Phase 2 MVP**.

**Rationale:**
- Mock data from Phase 1 (JSON fixtures) is sufficient for UI development
- CSV upload adds complexity without critical UI testing value
- Can be deferred to Phase 3 (Backend Integration)
- Mock data allows faster iteration on UI components

**If Not Implemented:**
- Developers use `src/data/fixtures/*.json` for all testing
- Section 0 (Parameter Gathering) becomes the true entry point
- Skip Flow 1 Steps 2-7 (CSV upload) in planning spec
- Document as "Phase 3 feature" in technical_decisions.md

**If Implemented:**
- Provides realistic data loading experience
- Tests CSV parsing/validation edge cases
- Enables manual testing with custom data
- 2 hours additional dev time

**Recommendation:** **Defer to Phase 3** unless dev team specifically requests it.

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Story Points:** 2
**Priority:** P3 (Low - Optional for MVP)
