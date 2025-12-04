# Phase 1: Data Generation - Technical Decisions

**Phase:** 1 of 8
**Agent:** `*agent dev`
**Date:** 2025-10-17
**Status:** Complete

---

## Key Decisions Summary

1. Pure Python with minimal dependencies (pandas, numpy, scipy only)
2. Include leap year 2024 (164,400 rows total)
3. Single category (Women's Dresses) per weekly actuals file
4. Weighted store multiplier formula with ±20% noise
5. Differentiated noise levels (historical ±10-15%, actuals ±20-25%)
6. Week 5 black swan events (+30%, +40%, -25% for scenarios)
7. 6-technique realism strategy for MAPE 12-18%
8. Comprehensive 6-type validation suite
9. ASCII-only output for Windows compatibility
10. Multiplicative seasonality model

---

## Decision Log

### Decision 1: Pure Python with Minimal Dependencies
**Date:** 2025-10-17
**Context:** Need to generate realistic retail sales data without complex ML libraries

**Options Considered:**
1. **Use Prophet to generate synthetic time series**
   - Pros: Very realistic patterns
   - Cons: Slow (~10min), heavy dependency, overkill for generation

2. **Simple formulas with pandas/numpy**
   - Pros: Fast (<2min), full control, minimal dependencies
   - Cons: Manual pattern implementation

**Decision:** Simple formulas with pandas/numpy

**Rationale:** Prophet is for consumption (Phase 5), not generation. We need speed and control.

**Implementation Notes:** Multiplicative model with monthly × weekly × holiday × noise factors

---

### Decision 2: Leap Year Handling
**Date:** 2025-10-17
**Context:** 2022-2024 range includes leap year 2024 (Feb 29)

**Options Considered:**
1. **Ignore leap year, use 1,095 days (54,750 rows)**
   - Pros: Simpler math
   - Cons: Less realistic

2. **Include leap year, use 1,096 days (164,400 rows)**
   - Pros: Accurate, realistic
   - Cons: Slightly more complex

**Decision:** Include leap year (164,400 rows)

**Rationale:** Real systems handle leap years. More accurate = better training data.

**Implementation Notes:** Updated validation check to expect 164,400 rows

---

## Performance Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total Files | 38 | 38 | ✅ |
| Historical Rows | ~164,250 | 164,400 | ✅ |
| K-means Silhouette | >0.4 | 0.521 | ✅ |
| Week 5 Variance (Normal) | >20% | 31.8% | ✅ |
| Week 5 Variance (High) | >20% | 37.4% | ✅ |
| Week 5 Variance (Low) | >20% | 24.2% | ✅ |
| Validation Checks | 6/6 | 6/6 | ✅ |
| Generation Time | <5 min | ~2 min | ✅ |

---

## Future Enhancements

### Enhancement 1: Time-Varying Store Attributes
**Description:** Allow store attributes to change over time (renovations, demographic shifts)
**Benefit:** More realistic for longer time periods (>3 years)
**Effort:** Medium
**Priority:** Low (acceptable for MVP)

### Enhancement 2: Multi-Category Weekly Actuals
**Description:** Generate weekly files with all 3 categories simultaneously
**Benefit:** Test multi-category scenarios
**Effort:** Low
**Priority:** Low (current design auto-detects category)

### Enhancement 3: SKU-Level Data
**Description:** Generate individual SKU-level sales instead of category aggregates
**Benefit:** Test finer-grained forecasting
**Effort:** High
**Priority:** Low (out of scope for MVP)

---

## Key Takeaways

### What Worked Well
- **Single-file script**: All generation + validation in one executable
- **Modular functions**: Easy to tune seasonality, noise, multipliers
- **Fixed seed (42)**: Reproducible data for consistent testing
- **Comprehensive validation**: Caught issues immediately (e.g., leap year)

### Lessons Learned
- **Windows encoding**: Use ASCII from start (avoid Unicode checkmarks)
- **Documentation timing**: README as specification would help earlier
- **Validation-first approach**: Run checks before full generation

### For Next Phase (Phase 2: Frontend)
- Use generated CSVs as test data for upload workflow
- Convert to JSON fixtures for frontend mockups
- Validate UI can handle all 3 scenarios

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 1 Complete ✅
