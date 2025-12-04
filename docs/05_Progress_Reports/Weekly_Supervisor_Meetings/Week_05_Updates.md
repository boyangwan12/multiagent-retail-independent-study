# Week 5 Updates: Architecture Evolution & Strategic Pivot

## Key Milestones

### v3.1: Granularity Adjustment (Post-Week 4 Meeting)
**Problem Identified**: SKU-level, store-level, weekly forecasting was too granular

**Solution Implemented**:
```
┌─────────────────────────────────────────────────────────────┐
│ DEMAND FORECASTING                                          │
│ • Category-level (not SKU-level)                            │
│ • Weekly frequency                                          │
│ • Total demand (not store-level)                            │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ ALLOCATION STRATEGY                                         │
│ 1. Clustering → Cluster percentages                         │
│ 2. Store percentages (within clusters)                      │
│ 3. Initial: DC holds 45% inventory                          │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│ DYNAMIC OPTIMIZATION                                        │
│ • Weekly replenishment                                      │
│ • Reforecast using actual sales data                        │
│ • Mid-season markdown (elasticity-based)                    │
└─────────────────────────────────────────────────────────────┘
```

---

### v3.3: Parameter-Driven Architecture (Post-Wednesday Meeting with Arnav)

**Critical Insight**: Hardcoded parameters don't fit all retail companies

**Strategic Pivot**:

| **v3.1-3.2 Approach** | **v3.3 Approach** |
|----------------------|------------------|
| Hardcoded 45% DC hold | LLM asks: "What % should DC hold initially?" |
| Fixed season length | LLM asks: "What is your season length?" |
| Predetermined markdown timing | LLM asks: "When do you typically markdown?" |
| Assumes single workflow | Adapts to company-specific workflows |

**New LLM-Driven Parameter Gathering**:
```
User Input (via LLM) → Key Parameters
├── Initial Allocation: 100% release? 55%? 45%? Custom?
├── Season Length: 12 weeks? 16 weeks? 26 weeks?
├── Markdown Timing: Week 8? Week 10? Dynamic?
├── Clustering Approach: Geographic? Sales volume? Demographic?
└── Replenishment Frequency: Weekly? Bi-weekly? On-demand?
```

---

## Strategic Positioning

### What This Means for Our Solution

**Before**: Deep-dive forecasting tool for a specific workflow
**After**: **Generic retail planning solution emphasizing agentic coordination**

```
┌──────────────────────────────────────────────────────────────┐
│                    CORE VALUE PROPOSITION                     │
├──────────────────────────────────────────────────────────────┤
│  ✓ Flexible parameter-driven framework                       │
│  ✓ Multi-agent coordination (not siloed expertise)           │
│  ✓ Adapts to diverse retail business models                  │
│  ✓ Real-world applicability across companies                 │
│                                                               │
│  → Focus: Intelligent workflow orchestration                 │
│  → Not: Hyper-specialized forecasting algorithms             │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture Comparison

### Workflow Flexibility Example

**Scenario 1: Fast Fashion Retailer**
- 100% initial allocation (no DC hold)
- 8-week season
- Aggressive early markdowns (Week 4)

**Scenario 2: Premium Department Store**
- 55% DC hold
- 16-week season
- Conservative markdowns (Week 12)

**Both supported by the same system through parameter configuration**

---

## Next Steps

1. mock data generation, data spec is read
2. frontend mockup
3. backend architecture implementation

---
