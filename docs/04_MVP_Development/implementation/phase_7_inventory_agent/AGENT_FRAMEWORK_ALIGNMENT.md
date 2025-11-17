# Phase 7 Inventory Agent - OpenAI SDK Framework Alignment

**Date:** 2025-11-16
**Status:** Implementation Guidelines
**Target:** Ensure Phase 7 Inventory Agent is compatible with OpenAI SDK agent framework

---

## Executive Summary

The Phase 7 Inventory Agent must follow the **existing agent framework pattern** established by Phase 6 (DemandAgent). This pattern uses:

1. **Custom Agent Framework** built on top of OpenAI SDK (not the OpenAI Agents SDK, which isn't available yet)
2. **AgentHandoffManager** for orchestrator coordination
3. **AgentConfig** with OpenAI client for Phase 8 readiness
4. **Async execute() method** as the main entry point
5. **Tool definitions** in OpenAI function-calling format (prepared for Phase 8)

**No changes to existing infrastructure are needed.** Phase 7 simply follows the established pattern.

---

## Agent Framework Overview

### Current Architecture (Phase 6-7)

```
┌─────────────────────────────────────────────────────────────┐
│                   OpenAI SDK (v1.54.0+)                      │
│         Standard REST API Client (not Agents SDK)            │
└────────────┬────────────────────────────────────┬────────────┘
             │                                    │
    ┌────────▼────────┐                ┌──────────▼──────────┐
    │  AgentConfig    │                │  AgentFactory       │
    │                 │                │  (Singleton)        │
    │ - openai_client │                │                     │
    │ - model         │                │ - get_orchestrator()│
    │ - temperature   │                │ - get_demand_agent()│
    │ - timeout_sec   │                │ - get_inventory_... │
    └─────────────────┘                │ - get_pricing_...   │
                                       └──────────┬──────────┘
                                                  │
                          ┌───────────────────────┼───────────────────────┐
                          │                       │                       │
                    ┌─────▼──────┐        ┌──────▼────────┐    ┌────────▼──────┐
                    │   Demand   │        │  Inventory   │    │   Pricing     │
                    │   Agent    │        │   Agent      │    │   Agent       │
                    │            │        │              │    │               │
                    │ - execute()│        │ - execute()  │    │ - execute()   │
                    │ - get_tools│        │ - get_tools  │    │ - get_tools   │
                    │ - get_inst.│        │ - get_inst.  │    │ - get_inst.   │
                    └─────┬──────┘        └──────┬───────┘    └────────┬──────┘
                          │                      │                     │
                          └──────────────────────┼─────────────────────┘
                                                 │
                                    ┌────────────▼────────────┐
                                    │ AgentHandoffManager     │
                                    │ (Custom Orchestrator)   │
                                    │                         │
                                    │ - register_agent()      │
                                    │ - call_agent()          │
                                    │ - handoff_chain()       │
                                    └─────────────────────────┘
```

### Phase 8 Planned Architecture

When OpenAI Agents SDK becomes available:

```
┌──────────────────────────────────────────────────────────────┐
│              OpenAI Agents SDK (future)                       │
│         Agent Framework with built-in tool execution          │
└────────────┬──────────────────────────────────────────────────┘
             │
    ┌────────▼──────────────┐
    │   Agent Session       │
    │                       │
    │ - configure agents    │
    │ - set handoffs        │
    │ - run() workflow      │
    │ - stream events       │
    └────────────┬──────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
   Agent1      Agent2    Agent3
```

**Phase 7 does NOT need to migrate to Phase 8 architecture yet.** Just follow Phase 6 pattern.

---

## Phase 7 Implementation Requirements

### 1. Agent Class Structure

**Follow DemandAgent pattern:**

```python
from app.agents.config import AgentConfig

class InventoryAgent:
    """Docstring with Phase 7/8 context."""

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize with config from AgentFactory."""
        self.config = config
        self.client = config.openai_client if config else None
        # Initialize business logic (K-means clusterer, etc.)

    async def execute(
        self,
        forecast_result: Dict[str, Any],
        parameters: SeasonParameters,
        stores_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Main orchestrator entry point (async)."""
        # Execute allocation workflow
        # Return dictionary matching output schema

    def get_tools(self) -> List[Dict[str, Any]]:
        """Tool definitions in OpenAI format (Phase 8 ready)."""
        # Return list of function-calling tools

    def get_instructions(self) -> str:
        """System prompt for Phase 8 (not used in Phase 7)."""
        # Return instructions string
```

**Key Points:**
- ✅ Use `AgentConfig` for consistency
- ✅ Receive config from `AgentFactory` (dependency injection)
- ✅ Implement `async execute()` as main entry point
- ✅ Include `get_tools()` and `get_instructions()` (Phase 8 ready)
- ✅ No breaking changes to orchestrator

### 2. Integration with AgentHandoffManager

**How Phase 7 integrates with orchestrator:**

```python
# In orchestrator or workflow service
from app.agents.factory import AgentFactory

# Get agent instance (singleton)
inventory_agent = AgentFactory.get_inventory_agent()

# Call via orchestrator's handoff mechanism
result = await orchestrator.call_agent(
    agent_name="inventory",
    context={
        "forecast_result": demand_output,
        "parameters": season_params,
        "stores_data": stores_df
    }
)
```

**No changes to AgentHandoffManager needed.** It accepts:
- Agent name (string)
- Context (any type)
- Timeout (default 5 minutes)

### 3. Output Schema (InventoryAgentOutput)

Must match contract for Phase 8 handoff:

```python
{
    "manufacturing_qty": int,
    "safety_stock_pct": float,
    "initial_allocation_total": int,
    "dc_holdback_total": int,
    "clusters": [
        {
            "cluster_id": int,
            "cluster_label": str,  # "Fashion_Forward", "Mainstream", "Value_Conscious"
            "allocation_percentage": float,
            "total_units": int,
            "stores": [
                {
                    "store_id": str,
                    "initial_allocation": int,
                    "allocation_factor": float
                }
            ]
        }
    ],
    "replenishment_enabled": bool,
    "replenishment_queue": [
        {
            "store_id": str,
            "current_inventory": int,
            "replenish_needed": int,
            "dc_available": str
        }
    ]
}
```

### 4. Async/Await Pattern

**All agent methods must be async:**

```python
class InventoryAgent:
    async def execute(self, ...):
        """Async entry point."""
        manufacturing = self.calculate_manufacturing(...)  # Sync helper
        result = await self.allocate_initial(...)  # Can be async or sync
        return result
```

**Why:**
- AgentHandoffManager enforces async execution
- Compatible with asyncio event loop
- Prepared for Phase 8 SDK (all async)

---

## OpenAI SDK Compatibility Checklist

✅ **Phase 7 follows this pattern:**

| Requirement | Phase 7 | Status |
|-------------|---------|--------|
| Use standard OpenAI SDK (v1.54.0+) | ✅ Configured in AgentConfig | Ready |
| Receive client via AgentConfig | ✅ Optional in __init__ | Ready |
| Implement async execute() | ✅ Main entry point | To Implement |
| Define tools in OpenAI format | ✅ get_tools() method | To Implement |
| Define instructions string | ✅ get_instructions() method | To Implement |
| Register with AgentFactory | ✅ Factory.get_inventory_agent() | Ready |
| Return structured output dict | ✅ InventoryAgentOutput schema | To Implement |
| No blocking I/O in execute() | ✅ All async/threading | To Implement |
| Type hints on all methods | ✅ Google style | To Implement |
| Logging via logger instance | ✅ logger.info/warning/error | To Implement |
| Handle errors gracefully | ✅ Raise with context | To Implement |

✅ **No changes needed to:**
- OpenAI SDK configuration
- AgentFactory pattern
- AgentConfig structure
- AgentHandoffManager mechanism

---

## File Changes Required (Phase 7)

### 1. Create: `backend/app/ml/store_clustering.py`
- **Purpose:** K-means clustering logic (Story 001)
- **Uses:** scikit-learn (not OpenAI SDK)
- **Status:** New file, no SDK dependency

### 2. Update: `backend/app/agents/inventory_agent.py`
- **Purpose:** Real allocation logic (Stories 002-003)
- **Uses:** AgentConfig, DemandAgent output, StoreClusterer
- **Changes:**
  - Replace placeholder methods with real implementation
  - Keep existing class structure (already SDK-compatible)
  - Add Tool definitions for Phase 8
  - Add Instructions for Phase 8

### 3. Create: `backend/tests/unit/ml/test_store_clustering.py`
- **Purpose:** Unit tests for clustering (Story 001)
- **Uses:** pytest, pandas, scikit-learn
- **Status:** New file, no SDK dependency

### 4. Create: `backend/tests/unit/agents/test_inventory_agent.py`
- **Purpose:** Unit tests for allocation logic (Story 002-003)
- **Uses:** pytest, async pytest, AgentFactory
- **Status:** New file, follows existing test patterns

### 5. Create: `backend/tests/integration/test_inventory_agent_integration.py`
- **Purpose:** Integration tests with Phase 6 (Story 004)
- **Uses:** DemandAgent, InventoryAgent, AgentFactory
- **Status:** New file, follows existing test patterns

---

## Documentation Updates (Phase 7)

### Updated Documents:
1. ✅ **PHASE7-002-allocation-logic.md** - Updated code template to reference OpenAI SDK framework
2. **PHASE7-001-kmeans-clustering.md** - No changes needed (uses scikit-learn, not SDK)
3. **PHASE7-003-replenishment-scheduling.md** - No changes needed (extends InventoryAgent)
4. **PHASE7-004-integration-testing.md** - No changes needed (uses existing patterns)

### New Documents:
5. ✅ **AGENT_FRAMEWORK_ALIGNMENT.md** - This document

---

## Transition to Phase 8 (Future)

When OpenAI Agents SDK becomes available, Phase 7 code will transition by:

1. **Keep existing code as-is** (classes, methods, logic)
2. **Update orchestrator only:**
   - Replace AgentHandoffManager with SDK Session
   - Use SDK's handoff configuration
   - Enable automatic tool execution
3. **Minimal agent changes:**
   - Add `@agent.define` decorators (if SDK requires)
   - Tool definitions → `@tool` decorators
   - Instructions → Agent initialization parameter

**No breaking changes to Phase 7 implementation.**

---

## Summary

✅ **Phase 7 Inventory Agent aligns with OpenAI SDK framework by:**

1. **Using AgentConfig** - Consistent with Phase 6, prepared for Phase 8
2. **Implementing async execute()** - Compatible with orchestrator
3. **Following DemandAgent pattern** - No custom patterns
4. **Defining tools and instructions** - Phase 8 ready
5. **Using AgentFactory** - Dependency injection consistency
6. **Returning structured output** - Contract-based integration

✅ **No infrastructure changes needed.** Phase 7 is an implementation task, not a framework task.

✅ **Framework is ready for Phase 8 migration** when OpenAI Agents SDK is available.

---

**Implementation can proceed with Phase 7-001 (K-means clustering).**
