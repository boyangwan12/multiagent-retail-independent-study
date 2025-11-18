# OpenAI Agent SDK Migration Plan - Path 2 (Full LLM-Powered)

**Project:** Multi-Agent Retail Forecasting System
**Current State:** Demand Agent + Inventory Agent (Pure Python ML)
**Target State:** LLM-Powered Agents with OpenAI Agent SDK
**Migration Type:** Path 2 - Full LLM reasoning + tool calling
**Estimated Effort:** 2-4 weeks
**Risk Level:** High

---

## Executive Summary

This document outlines the complete migration strategy to transform the current Python-based Demand and Inventory agents into fully LLM-powered agents using the OpenAI Agent SDK.

**Why Path 2?**
- Enable LLM reasoning about forecasting strategies
- Dynamic decision-making based on data quality
- Better error handling and explanations
- Conversational capabilities for future features

**Trade-offs:**
- ✅ More flexible and adaptive
- ✅ Better error messages and explanations
- ❌ Higher latency (multiple LLM calls)
- ❌ Higher cost (GPT-4 usage)
- ❌ Non-deterministic (LLM behavior varies)
- ❌ More complex to test and validate

---

## Table of Contents

1. [Current Architecture Analysis](#1-current-architecture-analysis)
2. [Target SDK Architecture](#2-target-sdk-architecture)
3. [Tool Decomposition Strategy](#3-tool-decomposition-strategy)
4. [LLM Instructions Design](#4-llm-instructions-design)
5. [Implementation Phases](#5-implementation-phases)
6. [Testing Strategy](#6-testing-strategy)
7. [Cost & Performance Analysis](#7-cost--performance-analysis)
8. [Risk Mitigation](#8-risk-mitigation)
9. [Rollback Plan](#9-rollback-plan)

---

## 1. Current Architecture Analysis

### 1.1 Demand Agent (Current)

**File:** `backend/app/agents/demand_agent.py` (Pure Python)

**What it does:**
```python
async def execute(category_id, parameters, historical_data):
    # 1. Train Prophet + ARIMA ensemble
    forecaster = EnsembleForecaster()
    forecaster.train(historical_data)

    # 2. Generate forecast
    forecast_result = forecaster.forecast(horizon_weeks)

    # 3. Calculate safety stock
    safety_stock_pct = 1.0 - forecast_result['confidence']

    # 4. Return results
    return {
        "total_demand": sum(predictions),
        "forecast_by_week": predictions,
        "safety_stock_pct": safety_stock_pct,
        "confidence": confidence,
        "model_used": model_name
    }
```

**Characteristics:**
- ✅ Fast (1-3 seconds)
- ✅ Deterministic
- ✅ Low cost (no LLM calls)
- ❌ No reasoning about edge cases
- ❌ Fixed logic (can't adapt)

### 1.2 Inventory Agent (Current)

**File:** `backend/app/agents/inventory_agent.py` (Pure Python)

**What it does:**
```python
async def execute(forecast_result, parameters, stores_data):
    # 1. Calculate manufacturing
    manufacturing_qty = total_demand * (1 + safety_stock_pct)

    # 2. Train K-means clustering
    clusterer = StoreClusterer()
    clusterer.fit(stores_data)

    # 3. Allocate to clusters (sales-based %)
    cluster_allocations = allocate_to_clusters(...)

    # 4. Allocate to stores (70% historical + 30% attributes)
    store_allocations = allocate_to_stores(...)

    # 5. Plan replenishment (if enabled)
    replenishment = plan_replenishment(...)

    return allocation_results
```

**Characteristics:**
- ✅ Fast (2-5 seconds with K-means)
- ✅ Deterministic
- ✅ Low cost
- ❌ Fixed allocation logic
- ❌ Can't explain decisions

---

## 2. Target SDK Architecture

### 2.1 High-Level Flow

```
User Request
    ↓
[Orchestrator Agent (SDK)]
    ↓
┌─────────────────────────┐
│  Demand Agent (LLM)     │
│  ┌───────────────────┐  │
│  │ GPT-4 Reasoning   │  │
│  └────────┬──────────┘  │
│           ↓             │
│  ┌───────────────────┐  │
│  │ analyze_data()    │  │ ← Tool 1
│  │ forecast_prophet()│  │ ← Tool 2
│  │ forecast_arima()  │  │ ← Tool 3
│  │ calc_safety_stock│  │ ← Tool 4
│  └───────────────────┘  │
└─────────────────────────┘
    ↓ Handoff (forecast_result)
┌─────────────────────────┐
│ Inventory Agent (LLM)   │
│  ┌───────────────────┐  │
│  │ GPT-4 Reasoning   │  │
│  └────────┬──────────┘  │
│           ↓             │
│  ┌───────────────────┐  │
│  │ calc_mfg()        │  │ ← Tool 1
│  │ cluster_stores()  │  │ ← Tool 2
│  │ allocate_clusters│  │ ← Tool 3
│  │ allocate_stores() │  │ ← Tool 4
│  │ validate_units()  │  │ ← Tool 5
│  │ plan_replenish()  │  │ ← Tool 6
│  └───────────────────┘  │
└─────────────────────────┘
    ↓
Final Result
```

### 2.2 SDK Components

#### Agent Definition (Demand Agent Example)

```python
from openai import Client

client = Client(api_key="...")

demand_agent = client.beta.agents.create(
    name="demand_forecasting_agent",
    model="gpt-4-turbo",
    instructions=DEMAND_AGENT_INSTRUCTIONS,  # 100+ lines
    tools=DEMAND_TOOLS,  # 6 tool definitions
    handoffs=["inventory_allocation_agent"],
    temperature=0.2
)
```

#### Tool Registration

```python
DEMAND_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_historical_data",
            "description": "Analyze sales data for trends...",
            "parameters": {...}
        }
    },
    # ... 5 more tools
]
```

#### Execution Flow

```python
# Create session
session = client.beta.agents.sessions.create()

# Run agent
run = client.beta.agents.runs.create(
    session_id=session.id,
    agent_id=demand_agent.id,
    messages=[{"role": "user", "content": context}]
)

# LLM decides which tools to call
# SDK executes tools automatically
# Agent reasons about results
# Agent hands off to next agent
```

---

## 3. Tool Decomposition Strategy

### 3.1 Demand Agent Tools (6 tools)

Break down `DemandAgent.execute()` into:

| Tool Name | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `analyze_historical_data` | Detect trends, seasonality, anomalies | `historical_data: List[Dict]` | `{trend, seasonality, data_quality, recommendation}` |
| `forecast_with_prophet` | Prophet model forecasting | `historical_data, horizon_weeks` | `{predictions, confidence, mape}` |
| `forecast_with_arima` | ARIMA model forecasting | `historical_data, horizon_weeks` | `{predictions, confidence, mape}` |
| `forecast_with_ensemble` | Ensemble (Prophet+ARIMA) | `historical_data, horizon_weeks` | `{predictions, confidence, mape}` |
| `calculate_safety_stock_percentage` | Convert confidence to safety stock % | `forecast_confidence, data_quality, strategy` | `{safety_stock_pct, reasoning, risk_level}` |
| `calculate_total_demand` | Sum weekly forecasts | `forecast_predictions: List[int]` | `{total_demand, weekly_avg, peak_week}` |

**LLM Decision Points:**
- Which forecasting method to use (Prophet vs ARIMA vs Ensemble)
- Safety stock strategy (aggressive vs balanced vs conservative)
- How to handle forecast failures (retry with different model)

### 3.2 Inventory Agent Tools (8 tools)

Break down `InventoryAgent.execute()` into:

| Tool Name | Purpose | Input | Output |
|-----------|---------|-------|--------|
| `calculate_manufacturing_quantity` | Add safety stock to demand | `total_demand, safety_stock_pct` | `{manufacturing_qty, safety_units}` |
| `cluster_stores_kmeans` | K-means clustering | `stores_data, n_clusters=3` | `{store_clusters, silhouette_score}` |
| `get_cluster_statistics` | Calculate cluster stats | `stores_data, store_clusters` | `{clusters: [{...stats...}]}` |
| `calculate_dc_holdback` | Determine DC inventory | `mfg_qty, holdback_pct, strategy` | `{dc_qty, store_qty, replen_enabled}` |
| `allocate_to_clusters` | Allocate units to clusters | `initial_allocation, cluster_stats` | `{cluster_allocations}` |
| `allocate_to_stores` | Allocate units to stores | `cluster_allocs, stores, min_weeks=2` | `{store_allocations}` |
| `validate_unit_conservation` | Check unit conservation | `expected_total, actual_allocs` | `{is_valid, difference, error_pct}` |
| `plan_replenishment_schedule` | Weekly replenishment plan | `dc_qty, strategy, horizon_weeks` | `{schedule, total_replen_qty}` |

**LLM Decision Points:**
- How to handle clustering failures (retry with different K)
- Whether to enforce stricter minimum inventory per store
- How to balance cluster allocations if unit conservation fails
- Replenishment timing adjustments

---

## 4. LLM Instructions Design

### 4.1 Demand Agent Instructions Template

```
You are an expert Demand Forecasting Agent for fashion retail.

## WORKFLOW (MUST FOLLOW IN ORDER):

### Step 1: Analyze Data
ALWAYS call analyze_historical_data first to understand:
- Data quality (excellent/good/poor)
- Trend direction
- Seasonality presence
- Model recommendation

### Step 2: Choose Forecasting Method
Based on analysis:
- Use forecast_with_prophet IF seasonality_detected = true
- Use forecast_with_arima IF trend != stable
- Use forecast_with_ensemble for best accuracy (DEFAULT)

### Step 3: Validate Forecast
- Check success = true
- If confidence < 0.6, flag uncertainty
- If failed, try alternative method

### Step 4: Calculate Safety Stock
Call calculate_safety_stock_percentage with:
- forecast_confidence
- data_quality
- business_strategy = "balanced"

### Step 5: Calculate Total Demand
Sum weekly forecasts

### Step 6: Hand Off
Format output and hand off to Inventory Agent

## DECISION GUIDELINES:
- Excellent data (52+ weeks) → Use ensemble, trust highly
- Poor data (<26 weeks) → Use conservative safety stock
- High confidence (>0.8) → Low safety stock (10-15%)
- Low confidence (<0.6) → High safety stock (25-35%)

## ERROR HANDLING:
If forecasting fails:
1. Log error
2. Try alternative method
3. If all fail, use conservative estimates

## CRITICAL RULES:
- ALWAYS analyze data first
- NEVER skip validation
- Safety stock must be 10-50%
- ALWAYS explain reasoning
```

**Length:** ~150-200 lines of detailed instructions

### 4.2 Inventory Agent Instructions Template

```
You are an expert Inventory Allocation Agent for fashion retail.

## WORKFLOW (MUST FOLLOW IN ORDER):

### Step 1: Calculate Manufacturing
Call calculate_manufacturing_quantity with forecast from Demand Agent

### Step 2: Cluster Stores
Call cluster_stores_kmeans to segment stores (K=3)

### Step 3: Get Cluster Stats
Call get_cluster_statistics for allocation percentages

### Step 4: Calculate DC Holdback
- 0% if replenishment_strategy = "none" (Zara model)
- 45% if strategy = "weekly" (Standard retail)

### Step 5: Allocate to Clusters
Call allocate_to_clusters with cluster percentages

### Step 6: Validate Cluster Allocation
CRITICAL: Call validate_unit_conservation

### Step 7: Allocate to Stores
Call allocate_to_stores with hybrid 70/30 factors

### Step 8: Validate Store Allocation
CRITICAL: Call validate_unit_conservation again

### Step 9: Plan Replenishment
If strategy != "none", call plan_replenishment_schedule

## DECISION GUIDELINES:
- Fashion_Forward clusters get most units
- Enforce 2-week minimum per store
- Unit conservation is CRITICAL (must be exact)
- Zara model: No replenishment, all upfront
- Standard retail: 45% DC holdback

## ERROR HANDLING:
If clustering fails (silhouette < 0.4):
- Retry with different K
- Fall back to simple allocation

If unit conservation fails:
- Explain discrepancy
- Adjust allocations proportionally

## CRITICAL RULES:
- NEVER skip validation steps
- Unit conservation error must be <1%
- Every store must have ≥2 weeks inventory
```

**Length:** ~150-200 lines

---

## 5. Implementation Phases

### **Phase 1: Tool Development** (Week 1)

#### Tasks:
- [ ] Create `backend/app/agents/tools/demand_tools.py`
  - Implement 6 demand tools
  - Add JSON serialization (DataFrames → dicts)
  - Write tool docstrings
  - Add error handling

- [ ] Create `backend/app/agents/tools/inventory_tools.py`
  - Implement 8 inventory tools
  - Add JSON serialization
  - Write tool docstrings
  - Add validation logic

- [ ] Create `backend/app/agents/tools/__init__.py`
  - Export all tools
  - Create tool registries

#### Validation:
```python
# Test each tool independently
result = await analyze_historical_data(sample_data)
assert result["data_quality"] in ["excellent", "good", "poor"]
```

### **Phase 2: Agent Instructions** (Week 1)

#### Tasks:
- [ ] Write Demand Agent instructions (150-200 lines)
  - Workflow steps
  - Decision guidelines
  - Error handling rules
  - Examples (3-5 scenarios)

- [ ] Write Inventory Agent instructions (150-200 lines)
  - Workflow steps
  - Allocation rules
  - Validation requirements
  - Edge case handling

#### Validation:
- Review with domain expert
- Ensure clarity and completeness
- Test with GPT-4 directly (manual prompt testing)

### **Phase 3: SDK Integration** (Week 2)

#### Tasks:
- [ ] Create `backend/app/agents/sdk/demand_agent_sdk.py`
  - Agent creation function
  - Tool function registry
  - Execution wrapper
  - Response parsing

- [ ] Create `backend/app/agents/sdk/inventory_agent_sdk.py`
  - Same structure as Demand Agent

- [ ] Create `backend/app/agents/sdk/orchestrator_sdk.py`
  - Session management
  - Handoff coordination
  - Error propagation
  - Logging/monitoring

#### Validation:
```python
# Test agent creation
agent_id = create_demand_agent_sdk(client)
assert agent_id is not None

# Test tool execution
result = await execute_demand_agent_sdk(
    client, agent_id, category_id, data, horizon
)
assert "total_demand" in result
```

### **Phase 4: Testing & Validation** (Week 2-3)

#### Unit Tests:
- Test each tool independently
- Mock LLM responses
- Validate tool output schemas

#### Integration Tests:
- Test Demand Agent end-to-end
- Test Inventory Agent end-to-end
- Test full workflow (Demand → Inventory)
- Compare SDK results vs Legacy results

#### LLM Behavior Tests:
- Test with different data qualities
- Test error recovery paths
- Test decision-making consistency
- Measure determinism (run same input 10x, compare)

### **Phase 5: Cost & Performance Optimization** (Week 3)

#### Tasks:
- [ ] Measure token usage per workflow
- [ ] Optimize instructions (reduce tokens)
- [ ] Add caching for repeated tool calls
- [ ] Implement retry logic with exponential backoff
- [ ] Add timeout handling

#### Metrics to Track:
- Total tokens per workflow
- Cost per workflow ($$$)
- Latency (seconds)
- Success rate (%)

### **Phase 6: Parallel Deployment** (Week 4)

#### Tasks:
- [ ] Deploy SDK agents alongside legacy agents
- [ ] Add feature flag: `USE_SDK_AGENTS=false` (default)
- [ ] Create A/B testing framework
- [ ] Run both systems in parallel
- [ ] Compare results daily

#### Validation Criteria:
- SDK forecast accuracy ≥ Legacy accuracy
- SDK allocation distribution matches Legacy within 5%
- Unit conservation: 100% success
- Latency: <30 seconds (vs <10s legacy)

### **Phase 7: Gradual Rollout** (Week 4)

#### Tasks:
- [ ] Enable SDK for 10% of traffic
- [ ] Monitor errors and failures
- [ ] Collect user feedback
- [ ] Increase to 50% if stable
- [ ] Full cutover to SDK if successful

---

## 6. Testing Strategy

### 6.1 Test Pyramid

```
           /\
          /  \         E2E Tests (5)
         /────\        - Full workflow
        /  🔴  \       - 3 scenarios
       /────────\
      /    🟡    \     Integration Tests (15)
     /────────────\    - Agent workflows
    /      🟢      \   - Tool combinations
   /────────────────\
  /                  \ Unit Tests (50+)
 /____________________\ - Individual tools
                        - Edge cases
```

### 6.2 Critical Test Scenarios

#### Scenario 1: Excellent Data, High Confidence
```
Input: 52 weeks of clean seasonal data
Expected: Ensemble forecast, 15% safety stock
Validate: LLM chooses ensemble, explains confidence
```

#### Scenario 2: Poor Data, Low Confidence
```
Input: 12 weeks of erratic data
Expected: Conservative forecast, 35% safety stock
Validate: LLM flags uncertainty, uses high buffer
```

#### Scenario 3: Model Failure Recovery
```
Input: Data that crashes Prophet
Expected: LLM retries with ARIMA
Validate: Graceful fallback, no workflow failure
```

#### Scenario 4: Unit Conservation Failure
```
Input: Rounding errors in allocation
Expected: LLM detects discrepancy, adjusts
Validate: Final allocation sums correctly
```

#### Scenario 5: Zara Model (No Replenishment)
```
Input: dc_holdback=0%, strategy="none"
Expected: 100% store allocation, no replenishment
Validate: LLM skips replenishment steps
```

### 6.3 Determinism Testing

**Challenge:** LLM responses are non-deterministic

**Solution:** Run each scenario 10x, measure consistency

```python
results = []
for i in range(10):
    result = await execute_demand_agent_sdk(...)
    results.append(result)

# Check variance
total_demands = [r['total_demand'] for r in results]
variance = np.std(total_demands) / np.mean(total_demands)

assert variance < 0.05  # <5% variance acceptable
```

---

## 7. Cost & Performance Analysis

### 7.1 Token Usage Estimation

#### Demand Agent (per execution):
```
Instructions: ~2,000 tokens
User Context: ~500 tokens
Tool Calls: 6 tools × 200 tokens = 1,200 tokens
Tool Results: 6 results × 300 tokens = 1,800 tokens
Agent Reasoning: ~1,000 tokens
Final Response: ~500 tokens
────────────────────────────────────────
Total: ~7,000 tokens/execution
```

#### Inventory Agent (per execution):
```
Instructions: ~2,500 tokens
Handoff Context: ~800 tokens
Tool Calls: 8 tools × 250 tokens = 2,000 tokens
Tool Results: 8 results × 400 tokens = 3,200 tokens
Agent Reasoning: ~1,200 tokens
Final Response: ~600 tokens
────────────────────────────────────────
Total: ~10,300 tokens/execution
```

#### Full Workflow:
```
Demand Agent: 7,000 tokens
Inventory Agent: 10,300 tokens
Orchestrator Overhead: ~1,000 tokens
────────────────────────────────────────
Total: ~18,300 tokens/workflow
```

### 7.2 Cost Analysis

**GPT-4-Turbo Pricing (as of 2024):**
- Input: $10 / 1M tokens
- Output: $30 / 1M tokens

**Assuming 50/50 input/output split:**

```
Per Workflow:
- Input: 9,150 tokens × $10/1M = $0.09
- Output: 9,150 tokens × $30/1M = $0.27
────────────────────────────────────────
Total: ~$0.36 per workflow
```

**Monthly Cost (1,000 workflows/month):**
```
1,000 workflows × $0.36 = $360/month
```

**Comparison to Legacy:**
- Legacy: $0/month (no LLM calls)
- SDK: $360/month (100+ workflows)

### 7.3 Latency Analysis

#### Legacy (Current):
```
Demand Agent: 2-3 seconds (Prophet+ARIMA ensemble)
Inventory Agent: 3-5 seconds (K-means clustering)
────────────────────────────────────────
Total: 5-8 seconds
```

#### SDK (Estimated):
```
Demand Agent:
- LLM reasoning: 3-5 seconds
- Tool execution (Prophet/ARIMA): 2-3 seconds
- Total: 5-8 seconds

Inventory Agent:
- LLM reasoning: 4-6 seconds
- Tool execution (K-means): 3-5 seconds
- Total: 7-11 seconds

Handoff Overhead: 1-2 seconds
────────────────────────────────────────
Total: 13-21 seconds (2-3x slower)
```

**Optimization Opportunities:**
- Parallel tool calling (SDK supports this)
- Shorter instructions (reduce token count)
- Cache frequently used prompts
- Use GPT-4-Turbo (faster than GPT-4)

---

## 8. Risk Mitigation

### Risk 1: Non-Deterministic Results

**Problem:** LLM might make different decisions on same input

**Mitigation:**
- Set low temperature (0.2)
- Use detailed, prescriptive instructions
- Add validation checks in tools
- Run acceptance tests 10x, check variance
- Add human review for high-variance scenarios

### Risk 2: LLM Doesn't Follow Workflow

**Problem:** LLM might skip steps or call tools in wrong order

**Mitigation:**
- Use explicit step numbers in instructions
- Add tool dependencies (Tool B requires Tool A output)
- Validate tool call sequences in orchestrator
- Add "required_steps" validation after completion

### Risk 3: Higher Latency

**Problem:** 2-3x slower than legacy (15-20s vs 5-8s)

**Mitigation:**
- Optimize instructions (shorter = faster)
- Parallel tool execution where possible
- Cache LLM responses for repeated scenarios
- Use streaming for progress updates
- Set realistic user expectations (show progress)

### Risk 4: Higher Cost

**Problem:** $360/month vs $0 for legacy

**Mitigation:**
- Monitor token usage closely
- Optimize prompts to reduce tokens
- Use cheaper models for non-critical paths
- Batch workflows when possible
- ROI analysis: Better decisions = higher revenue

### Risk 5: Tool Execution Failures

**Problem:** Prophet/ARIMA might fail, LLM expects valid output

**Mitigation:**
- All tools return `{success: bool, error: str|null}`
- LLM instructions include error handling
- Fallback strategies (Prophet fails → try ARIMA)
- Always return valid JSON (never raise exceptions)

---

## 9. Rollback Plan

### Rollback Triggers:
- Success rate < 90%
- Latency > 30 seconds (P95)
- Cost > $1,000/month
- Accuracy degradation > 10% vs legacy
- Critical bugs in production

### Rollback Steps:

#### Immediate Rollback (< 5 minutes):
```python
# Set feature flag
USE_SDK_AGENTS = False

# All traffic routes to legacy agents
# No code deployment needed
```

#### Data Preservation:
- Keep SDK logs for analysis
- Archive SDK results for comparison
- Preserve tool execution traces

#### Post-Rollback Analysis:
- Identify failure patterns
- Fix issues in staging
- Re-test before retry

---

## 10. Success Criteria

### Must-Have (MVP):
- [ ] All tools implemented and tested
- [ ] Agents execute full workflow successfully
- [ ] Results match legacy within 10% variance
- [ ] Unit conservation: 100% success
- [ ] Latency < 30 seconds (P95)
- [ ] Cost < $500/month (for pilot)

### Nice-to-Have (V2):
- [ ] LLM explains all decisions in natural language
- [ ] Confidence scores for all predictions
- [ ] "Why did you choose this model?" feature
- [ ] Real-time progress streaming
- [ ] User can override LLM decisions

### Long-Term Vision:
- [ ] Conversational forecasting ("What if we increase safety stock?")
- [ ] Multi-turn workflows (LLM asks clarifying questions)
- [ ] Automatic strategy adaptation based on results
- [ ] Transfer learning from past forecasts

---

## 11. Next Steps

### Before Migration:
1. **Get stakeholder buy-in** - Present this plan, discuss trade-offs
2. **Secure budget** - $500-1000/month for pilot + development time
3. **Set up SDK access** - OpenAI API key, SDK beta access
4. **Define success metrics** - What does "successful migration" mean?

### Week 1 Actions:
1. Set up development environment
2. Implement 2-3 demand tools as proof of concept
3. Test tools manually with sample data
4. Write initial draft of agent instructions
5. Test instructions with GPT-4 directly (no SDK yet)

### Week 2 Checkpoint:
- Review tool architecture
- Validate LLM instruction quality
- Decide: Continue with full migration or pivot to Path 1?

---

## Appendix A: File Structure

```
backend/app/
├── agents/
│   ├── demand_agent.py          # LEGACY: Keep for comparison
│   ├── inventory_agent.py       # LEGACY: Keep for comparison
│   ├── sdk/                     # NEW: SDK-based agents
│   │   ├── __init__.py
│   │   ├── demand_agent_sdk.py
│   │   ├── inventory_agent_sdk.py
│   │   └── orchestrator_sdk.py
│   ├── tools/                   # NEW: Granular tools
│   │   ├── __init__.py
│   │   ├── demand_tools.py      # 6 tools
│   │   └── inventory_tools.py   # 8 tools
│   └── config.py                # MODIFY: Add SDK config
├── services/
│   └── workflow_service.py      # MODIFY: Add SDK workflow path
└── api/
    └── v1/endpoints/workflows.py # MODIFY: Add feature flag
```

---

## Appendix B: Code Snippets

### Feature Flag Pattern

```python
# backend/app/core/config.py
class Settings:
    USE_SDK_AGENTS: bool = False  # Feature flag

# backend/app/services/workflow_service.py
async def run_forecast_workflow(category_id, parameters):
    if settings.USE_SDK_AGENTS:
        return await run_forecast_workflow_sdk(...)
    else:
        return await run_forecast_workflow_legacy(...)
```

### Tool Error Handling Pattern

```python
async def forecast_with_prophet(...) -> Dict[str, Any]:
    try:
        # Run Prophet
        result = forecaster.forecast(...)
        return {
            "success": True,
            "predictions": result['predictions'],
            "confidence": result['confidence'],
            "error": None
        }
    except Exception as e:
        logger.error(f"Prophet failed: {e}")
        return {
            "success": False,
            "predictions": [],
            "confidence": 0.0,
            "error": str(e)
        }
```

---

## Appendix C: Decision Matrix

When to use Path 1 vs Path 2:

| Requirement | Path 1 (Handoff-Only) | Path 2 (Full LLM) |
|-------------|----------------------|-------------------|
| Need explanations | ❌ | ✅ |
| Cost-sensitive | ✅ | ❌ |
| Latency-sensitive | ✅ | ❌ |
| Want flexibility | ❌ | ✅ |
| Need determinism | ✅ | ⚠️ |
| Want conversational | ❌ | ✅ |
| Limited time | ✅ | ❌ |
| ML logic is proven | ✅ | ⚠️ |

**Recommendation:** Start with Path 1, migrate to Path 2 later if needed.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Author:** Claude (AI Assistant)
**Status:** Draft - Awaiting Review
