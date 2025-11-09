# Story: Build Agent Handoff Framework for Multi-Agent Coordination

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-002
**Status:** Ready for Implementation
**Estimate:** 5 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001 (Parameter Extraction)

**Planning References:**
- PRD v3.3: Section 4.1 (Multi-Agent Workflow Coordination)
- Technical Architecture v3.3: Section 4.4 (Orchestrator - Agent Handoff Management)
- Product Brief v3.3: Section 2.2 (Sequential Agent Workflow)

---

## Story

As a backend developer,
I want to create a generic agent handoff framework to coordinate multiple agents sequentially,
So that the Orchestrator can call Demand, Inventory, and Pricing agents with context passing between them.

**Business Value:** The agent handoff framework is the backbone of the multi-agent orchestration system. Without this, we'd need custom code for each agent-to-agent transition, making the system brittle and hard to extend. This framework enables the PRD's vision of seamless agent coordination where Demand Agent's forecast automatically flows to Inventory Agent, then to Pricing Agent, creating an intelligent end-to-end workflow.

**Epic Context:** This is Story 2 of 6 in Phase 5 (Orchestrator Foundation). It builds on Story 5.1's parameter extraction and creates the infrastructure for Phase 6-8 agents to plug into. This framework will be extended throughout development as new agents are added - it's designed for incremental growth.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `AgentHandoffManager` class created with agent registry
2. ✅ `register_agent(name, handler)` method registers agents by name
3. ✅ `call_agent(name, context)` method executes single agent with timeout
4. ✅ `handoff_chain(agents[], context)` method executes multiple agents sequentially
5. ✅ Context passing works: Result from Agent N becomes context for Agent N+1
6. ✅ Agent registry stores: name, handler function, registration timestamp
7. ✅ Timeout enforcement: Default 30 seconds per agent, configurable
8. ✅ Error detection: Agent not registered raises ValueError
9. ✅ Error detection: Agent timeout raises asyncio.TimeoutError
10. ✅ Error detection: Agent failure propagates with original exception

### Quality Requirements

11. ✅ Execution logging captures: agent_name, start_time, duration, status (success/timeout/failed)
12. ✅ `get_execution_log()` method returns full execution history
13. ✅ Type hints use generics (TypeVar) for flexible context/result types
14. ✅ All public methods have comprehensive docstrings
15. ✅ Mock Demand Agent created for framework testing
16. ✅ Unit tests for: registration, single agent call, agent chaining, timeout, errors
17. ✅ Code follows async/await best practices

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] `SeasonParameters` Pydantic schema exists
- [x] Backend FastAPI project structure in place

**Python Environment:**
- [ ] Python 3.11+ with async/await support
- [ ] `asyncio` library available (standard library)
- [ ] Type hints working (`typing` module)

**Testing Setup:**
- [ ] pytest installed for unit tests
- [ ] pytest-asyncio installed for async test support

**Why This Matters:**
This framework is the foundation for all agent coordination. If it's not robust (timeouts, error handling, logging), every agent integration in Phase 6-8 will have issues. Getting this right now prevents compounding problems later.

---

## Tasks

### Task 1: Create AgentHandoffManager Class Structure

**Goal:** Define the main class with agent registry

**Subtasks:**
- [ ] Create file: `backend/app/orchestrator/agent_handoff.py`
- [ ] Import required modules:
  ```python
  from typing import Dict, Any, Callable, TypeVar, List
  import asyncio
  import time
  import logging
  ```
- [ ] Define type variables for generic context/result:
  ```python
  T = TypeVar('T')  # Context type
  R = TypeVar('R')  # Result type
  ```
- [ ] Create `AgentHandoffManager` class:
  ```python
  class AgentHandoffManager:
      """
      Manages agent registration and sequential handoff execution

      Attributes:
          _agents: Registry of agent handlers by name
          _execution_log: List of execution records for debugging
          logger: Python logger for operational logging
      """

      def __init__(self):
          self._agents: Dict[str, Callable] = {}
          self._execution_log: List[Dict] = []
          self.logger = logging.getLogger(__name__)
  ```
- [ ] Test class instantiation:
  ```python
  manager = AgentHandoffManager()
  assert len(manager._agents) == 0
  assert len(manager._execution_log) == 0
  ```

---

### Task 2: Implement Agent Registration

**Goal:** Allow agents to be registered with the manager

**Subtasks:**
- [ ] Implement `register_agent()` method:
  ```python
  def register_agent(self, name: str, handler: Callable):
      """
      Register an agent handler

      Args:
          name: Agent name (e.g., "demand", "inventory", "pricing")
          handler: Async function that processes context and returns result
              Signature: async def handler(context: Any) -> Any

      Example:
          manager.register_agent("demand", demand_agent_handler)
      """
      if name in self._agents:
          self.logger.warning(f"Agent '{name}' already registered, overwriting")

      self._agents[name] = handler
      self.logger.info(f"Agent '{name}' registered successfully")
  ```
- [ ] Add agent validation (ensure handler is callable):
  ```python
  if not callable(handler):
      raise TypeError(f"Handler for agent '{name}' must be callable")
  ```
- [ ] Test registration:
  ```python
  async def mock_agent(ctx):
      return {"result": "success"}

  manager.register_agent("test_agent", mock_agent)
  assert "test_agent" in manager._agents
  assert manager._agents["test_agent"] == mock_agent
  ```

---

### Task 3: Implement Single Agent Execution

**Goal:** Execute individual agent with timeout and error handling

**Subtasks:**
- [ ] Implement `call_agent()` method:
  ```python
  async def call_agent(
      self,
      agent_name: str,
      context: T,
      timeout: int = 30
  ) -> R:
      """
      Execute agent with context

      Args:
          agent_name: Name of agent to call
          context: Input context (SeasonParameters, ForecastResult, etc.)
          timeout: Max execution time in seconds (default: 30)

      Returns:
          Agent result

      Raises:
          ValueError: If agent not registered
          asyncio.TimeoutError: If agent exceeds timeout
          Exception: If agent execution fails (original exception propagated)

      Example:
          result = await manager.call_agent("demand", parameters, timeout=60)
      """
      if agent_name not in self._agents:
          raise ValueError(f"Agent '{agent_name}' not registered")

      handler = self._agents[agent_name]
      start_time = time.time()

      self.logger.info(f"Calling agent '{agent_name}'")

      try:
          result = await asyncio.wait_for(
              handler(context),
              timeout=timeout
          )
          status = "success"
          self.logger.info(f"Agent '{agent_name}' completed successfully")

      except asyncio.TimeoutError:
          status = "timeout"
          self.logger.error(f"Agent '{agent_name}' timed out after {timeout}s")
          raise

      except Exception as e:
          status = "failed"
          self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
          raise

      finally:
          duration = time.time() - start_time
          self._log_execution(agent_name, start_time, duration, status)

      return result
  ```
- [ ] Test single agent execution (success case)
- [ ] Test timeout handling (slow agent)
- [ ] Test error handling (agent raises exception)
- [ ] Test invalid agent name (not registered)

---

### Task 4: Implement Agent Chain Execution

**Goal:** Execute multiple agents sequentially with result passing

**Subtasks:**
- [ ] Implement `handoff_chain()` method:
  ```python
  async def handoff_chain(
      self,
      agents: List[str],
      initial_context: Any
  ) -> Any:
      """
      Chain multiple agents sequentially, passing results between them

      The result from Agent N becomes the context for Agent N+1.

      Args:
          agents: List of agent names to execute in order
              Example: ["demand", "inventory", "pricing"]
          initial_context: Context for first agent (usually SeasonParameters)

      Returns:
          Final result from last agent in chain

      Raises:
          ValueError: If any agent not registered
          asyncio.TimeoutError: If any agent times out
          Exception: If any agent fails

      Example:
          final_result = await manager.handoff_chain(
              agents=["demand", "inventory", "pricing"],
              initial_context=season_parameters
          )
      """
      context = initial_context

      self.logger.info(f"Starting agent chain: {' → '.join(agents)}")

      for i, agent_name in enumerate(agents):
          self.logger.info(f"Chain step {i+1}/{len(agents)}: Calling '{agent_name}'")

          result = await self.call_agent(agent_name, context)
          context = result  # Pass result as context to next agent

      self.logger.info("Agent chain completed successfully")
      return context
  ```
- [ ] Test 2-agent chain (Demand → Inventory mock)
- [ ] Test 3-agent chain (Demand → Inventory → Pricing mock)
- [ ] Test chain failure (second agent fails - should not call third)
- [ ] Verify result passing (each agent receives previous agent's result)

---

### Task 5: Implement Execution Logging

**Goal:** Track agent execution for debugging and monitoring

**Subtasks:**
- [ ] Implement `_log_execution()` private method:
  ```python
  def _log_execution(
      self,
      agent_name: str,
      start_time: float,
      duration: float,
      status: str
  ):
      """
      Log agent execution for debugging and monitoring

      Args:
          agent_name: Name of agent executed
          start_time: Unix timestamp when execution started
          duration: Execution duration in seconds
          status: Execution status (success, timeout, failed)
      """
      log_entry = {
          "agent_name": agent_name,
          "start_time": start_time,
          "duration_seconds": round(duration, 2),
          "status": status,
          "timestamp": time.time()
      }
      self._execution_log.append(log_entry)
  ```
- [ ] Implement `get_execution_log()` method:
  ```python
  def get_execution_log(self) -> List[Dict]:
      """
      Return execution log for debugging

      Returns:
          List of execution records with agent name, duration, status

      Example:
          log = manager.get_execution_log()
          for entry in log:
              print(f"{entry['agent_name']}: {entry['duration_seconds']}s ({entry['status']})")
      """
      return self._execution_log
  ```
- [ ] Implement `clear_log()` method:
  ```python
  def clear_log(self):
      """Clear execution log (useful between tests)"""
      self._execution_log = []
  ```
- [ ] Test log entries created after agent execution
- [ ] Test log includes correct duration and status
- [ ] Test clear_log() removes all entries

---

### Task 6: Create Mock Agent for Testing

**Goal:** Create realistic mock agent to test framework

**Subtasks:**
- [ ] Create `mock_demand_agent()` function:
  ```python
  async def mock_demand_agent(context: SeasonParameters) -> Dict:
      """
      Mock Demand Agent for testing handoff framework

      Args:
          context: Season parameters from parameter extraction

      Returns:
          Dictionary mimicking forecast result structure
      """
      await asyncio.sleep(0.5)  # Simulate processing time

      # Adapt safety stock based on replenishment strategy (demonstrates parameter awareness)
      if context.replenishment_strategy == "none":
          safety_stock = 1.25  # 25% for no replenishment
      elif context.replenishment_strategy == "weekly":
          safety_stock = 1.20  # 20% for weekly
      else:  # bi-weekly
          safety_stock = 1.22  # 22% for bi-weekly

      return {
          "agent": "demand",
          "total_forecast": 8000,
          "safety_stock_multiplier": safety_stock,
          "weekly_curve": [650, 680, 720, 740, 760, 730, 710, 680, 650, 620, 580, 480],
          "clusters": ["Fashion_Forward", "Mainstream", "Value_Conscious"],
          "message": f"Mock forecast for {context.forecast_horizon_weeks}-week season"
      }
  ```
- [ ] Create `mock_inventory_agent()` function:
  ```python
  async def mock_inventory_agent(forecast_result: Dict) -> Dict:
      """
      Mock Inventory Agent that receives forecast from Demand Agent

      Args:
          forecast_result: Result from Demand Agent

      Returns:
          Dictionary mimicking manufacturing order
      """
      await asyncio.sleep(0.3)

      total_forecast = forecast_result["total_forecast"]
      safety_stock = forecast_result["safety_stock_multiplier"]
      manufacturing_qty = int(total_forecast * safety_stock)

      return {
          "agent": "inventory",
          "manufacturing_qty": manufacturing_qty,
          "forecast_received": total_forecast,
          "safety_stock_applied": safety_stock,
          "message": f"Mock manufacturing order: {manufacturing_qty} units"
      }
  ```
- [ ] Test mock agents independently
- [ ] Test mock agents in chain (Demand → Inventory)

---

### Task 7: Write Comprehensive Tests

**Goal:** Ensure framework works correctly for all scenarios

**Subtasks:**
- [ ] Create file: `backend/tests/test_agent_handoff.py`
- [ ] **Test 1:** Agent registration
  ```python
  def test_agent_registration():
      manager = AgentHandoffManager()

      async def test_handler(ctx):
          return {"result": "test"}

      manager.register_agent("test", test_handler)

      assert "test" in manager._agents
      assert manager._agents["test"] == test_handler
  ```
- [ ] **Test 2:** Single agent call (success)
  ```python
  @pytest.mark.asyncio
  async def test_single_agent_call():
      manager = AgentHandoffManager()
      manager.register_agent("demand", mock_demand_agent)

      params = SeasonParameters(
          forecast_horizon_weeks=12,
          season_start_date=date(2025, 3, 1),
          season_end_date=date(2025, 5, 23),
          replenishment_strategy="none",
          dc_holdback_percentage=0.0
      )

      result = await manager.call_agent("demand", params)

      assert result["total_forecast"] == 8000
      assert result["safety_stock_multiplier"] == 1.25  # 25% for no replenishment
  ```
- [ ] **Test 3:** Agent chain (2 agents)
  ```python
  @pytest.mark.asyncio
  async def test_agent_chain():
      manager = AgentHandoffManager()
      manager.register_agent("demand", mock_demand_agent)
      manager.register_agent("inventory", mock_inventory_agent)

      result = await manager.handoff_chain(
          agents=["demand", "inventory"],
          initial_context=mock_parameters
      )

      assert result["agent"] == "inventory"
      assert result["manufacturing_qty"] == 10000  # 8000 * 1.25
  ```
- [ ] **Test 4:** Timeout handling
  ```python
  @pytest.mark.asyncio
  async def test_agent_timeout():
      async def slow_agent(ctx):
          await asyncio.sleep(5)  # Exceeds timeout
          return {}

      manager = AgentHandoffManager()
      manager.register_agent("slow", slow_agent)

      with pytest.raises(asyncio.TimeoutError):
          await manager.call_agent("slow", {}, timeout=2)

      # Verify timeout logged
      log = manager.get_execution_log()
      assert log[0]["status"] == "timeout"
  ```
- [ ] **Test 5:** Agent not registered
  ```python
  @pytest.mark.asyncio
  async def test_agent_not_registered():
      manager = AgentHandoffManager()

      with pytest.raises(ValueError, match="Agent 'unknown' not registered"):
          await manager.call_agent("unknown", {})
  ```
- [ ] **Test 6:** Agent failure propagation
  ```python
  @pytest.mark.asyncio
  async def test_agent_failure():
      async def failing_agent(ctx):
          raise RuntimeError("Agent internal error")

      manager = AgentHandoffManager()
      manager.register_agent("failing", failing_agent)

      with pytest.raises(RuntimeError, match="Agent internal error"):
          await manager.call_agent("failing", {})

      # Verify failure logged
      log = manager.get_execution_log()
      assert log[0]["status"] == "failed"
  ```
- [ ] **Test 7:** Execution log
  ```python
  @pytest.mark.asyncio
  async def test_execution_log():
      manager = AgentHandoffManager()
      manager.register_agent("demand", mock_demand_agent)

      await manager.call_agent("demand", mock_parameters)

      log = manager.get_execution_log()
      assert len(log) == 1
      assert log[0]["agent_name"] == "demand"
      assert log[0]["status"] == "success"
      assert log[0]["duration_seconds"] > 0
  ```
- [ ] Run all tests: `uv run pytest backend/tests/test_agent_handoff.py -v`

---

## Implementation Notes

**Usage Example in Orchestrator:**
```python
# Initialize handoff manager (once)
handoff_manager = AgentHandoffManager()

# Register mock agent for Phase 5 testing
handoff_manager.register_agent("demand", mock_demand_agent)

# Later in Phase 6, replace with real agent:
# handoff_manager.register_agent("demand", real_demand_agent_handler)

# Execute single agent
parameters = await extract_parameters_from_text(user_input)
forecast = await handoff_manager.call_agent("demand", parameters)

# Execute agent chain (when Inventory and Pricing agents exist)
final_result = await handoff_manager.handoff_chain(
    agents=["demand", "inventory", "pricing"],
    initial_context=parameters
)
```

**Type Safety with Generics:**
```python
# Type hints ensure correct context/result types
async def typed_agent(context: SeasonParameters) -> ForecastResult:
    ...

# Manager handles generic types
result: ForecastResult = await manager.call_agent("demand", parameters)
```

**Error Handling Best Practices:**
```python
try:
    result = await manager.call_agent("demand", parameters, timeout=60)
except ValueError as e:
    # Agent not registered - programming error
    logger.critical(f"Agent missing: {e}")
except asyncio.TimeoutError:
    # Agent timed out - operational issue
    logger.error("Agent exceeded timeout, workflow failed")
except Exception as e:
    # Agent failed internally - log and investigate
    logger.error(f"Agent execution failed: {e}")
```

---

## Definition of Done

- [ ] `AgentHandoffManager` class created with agent registry
- [ ] `register_agent()` method implemented with validation
- [ ] `call_agent()` method implemented with timeout and error handling
- [ ] `handoff_chain()` method implemented for sequential execution
- [ ] Execution logging with `_log_execution()`, `get_execution_log()`, `clear_log()`
- [ ] Mock Demand Agent created for testing
- [ ] Mock Inventory Agent created for chaining tests
- [ ] 7 unit tests passing (registration, single call, chain, timeout, not registered, failure, logging)
- [ ] Type hints added for all methods with generics
- [ ] Docstrings added for all public methods
- [ ] Code follows PEP 8 style guidelines
- [ ] Code reviewed and merged

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
