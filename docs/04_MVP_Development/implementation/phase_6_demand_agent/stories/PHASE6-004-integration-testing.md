# Story: Integrate Demand Agent with Phase 5 Orchestrator

**Epic:** Phase 6 - Demand Agent
**Story ID:** PHASE6-004
**Status:** Ready for Implementation
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE6-001, PHASE6-002, PHASE6-003 complete

**Planning References:**
- PRD v3.3: Section 5.4 (Demand Agent Integration)
- Technical Architecture v3.3: Section 4.6 (Agent Integration with Orchestrator)
- Phase 5 OVERVIEW: DemandAgentContext and agent registration
- technical_decisions.md: TD-6.7 (Output Contract)

---

## Story

As a backend developer,
I want to create the DemandAgent class that integrates EnsembleForecaster with the Phase 5 orchestrator,
So that the system can generate real AI-powered forecasts in the end-to-end workflow.

**Business Value:** This story completes Phase 6 by replacing the mock Demand Agent with a production-ready AI forecasting agent. It enables the core value proposition: accurate, parameter-driven demand forecasting. This is the first "real AI agent" in the multi-agent system.

**Epic Context:** This is Story 4 of 4 in Phase 6 (final story). It integrates all previous work (Prophet, ARIMA, Ensemble) with the Phase 5 orchestrator infrastructure. After this story, the system can generate real forecasts end-to-end from parameter extraction to forecast output.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ DemandAgent class created in `backend/app/agents/demand_agent.py`
2. ✅ DemandAgent implements standard agent interface: `execute(context: DemandAgentContext) -> dict`
3. ✅ DemandAgent uses EnsembleForecaster internally
4. ✅ DemandAgent consumes DemandAgentContext (parameters, historical_data, stores_data)
5. ✅ DemandAgent returns forecast_result matching DemandAgentOutput contract
6. ✅ Output includes: total_demand, forecast_by_week, safety_stock_pct, confidence, model_used
7. ✅ Safety stock calculated as: `safety_stock_pct = 1.0 - confidence` (inverse relationship)
8. ✅ DemandAgent registered with AgentHandoffManager
9. ✅ WebSocket progress messages sent during forecasting
10. ✅ Mock demand agent in orchestrator replaced with real agent

### Quality Requirements

11. ✅ End-to-end workflow completes in <15 seconds (parameter extraction → forecast)
12. ✅ Forecast generation alone completes in <10 seconds
13. ✅ Integration test with full orchestrator workflow passing
14. ✅ WebSocket messages received in correct order
15. ✅ Output validated against Pydantic DemandAgentOutput schema
16. ✅ Error handling integrated with Phase 5 error system
17. ✅ All docstrings complete
18. ✅ Performance profiled and optimized

---

## Prerequisites

**Phase 5 Complete:**
- [x] AgentHandoffManager operational
- [x] DemandAgentContext schema defined
- [x] ContextAssembler can build context
- [x] WebSocket streaming functional
- [x] Mock orchestrator service exists

**Previous Stories Complete:**
- [x] PHASE6-001 (Prophet) complete
- [x] PHASE6-002 (ARIMA) complete
- [x] PHASE6-003 (Ensemble) complete
- [x] All ML wrappers tested and working

---

## Tasks

### Task 1: Create DemandAgent Class Skeleton

**Goal:** Define agent class structure following Phase 5 contract

**Subtasks:**
- [ ] Create file: `backend/app/agents/demand_agent.py`
- [ ] Define `DemandAgent` class
- [ ] Add `__init__(self)` method
- [ ] Add `execute(self, context: DemandAgentContext) -> dict` method stub
- [ ] Import EnsembleForecaster
- [ ] Add type hints and docstrings

**Code Template:**
```python
from typing import Dict
import logging
import pandas as pd
from backend.app.ml.ensemble_forecaster import EnsembleForecaster
from backend.app.orchestrator.context_assembly import DemandAgentContext
from backend.app.agents.contracts import DemandAgentOutput

logger = logging.getLogger(__name__)

class DemandAgent:
    """Demand forecasting agent using Prophet + ARIMA ensemble.

    This agent generates weekly demand forecasts based on historical sales data
    and season parameters. It uses an ensemble of Prophet and ARIMA models
    for improved accuracy.

    Attributes:
        forecaster: EnsembleForecaster instance
    """

    def __init__(self):
        """Initialize DemandAgent with ensemble forecaster."""
        self.forecaster = EnsembleForecaster()
        logger.info("DemandAgent initialized")

    async def execute(self, context: DemandAgentContext) -> Dict:
        """Execute demand forecasting.

        Args:
            context: DemandAgentContext with parameters, historical data, stores

        Returns:
            dict: Forecast result matching DemandAgentOutput schema
        """
        pass
```

---

### Task 2: Implement execute() Method

**Goal:** Core agent logic that generates forecasts

**Subtasks:**
- [ ] Extract parameters from context:
  ```python
  params = context.parameters
  historical_data = pd.DataFrame(context.historical_data)
  horizon_weeks = params.forecast_horizon_weeks
  ```
- [ ] Log execution start
- [ ] Train ensemble forecaster:
  ```python
  self.forecaster.train(historical_data)
  ```
- [ ] Generate forecast:
  ```python
  forecast_result = self.forecaster.forecast(periods=horizon_weeks)
  ```
- [ ] Calculate total demand:
  ```python
  total_demand = sum(forecast_result['predictions'])
  ```
- [ ] Calculate safety stock percentage:
  ```python
  safety_stock_pct = 1.0 - forecast_result['confidence']
  # Clamp to reasonable range [0.1, 0.5]
  safety_stock_pct = max(0.1, min(0.5, safety_stock_pct))
  ```
- [ ] Format output:
  ```python
  output = {
      "total_demand": int(total_demand),
      "forecast_by_week": forecast_result['predictions'],
      "safety_stock_pct": round(safety_stock_pct, 2),
      "confidence": round(forecast_result['confidence'], 2),
      "model_used": forecast_result['model_used']
  }
  ```
- [ ] Validate output against DemandAgentOutput schema
- [ ] Log execution complete
- [ ] Return output

**Acceptance:**
- execute() runs successfully with valid context
- Output matches DemandAgentOutput contract
- All fields populated correctly

---

### Task 3: Add WebSocket Progress Messages

**Goal:** Send real-time updates during forecasting

**Subtasks:**
- [ ] Accept connection_manager and session_id in execute()
- [ ] Send "agent_status" message at start:
  ```python
  if connection_manager:
      await connection_manager.send_message(session_id, {
          "type": "agent_status",
          "agent_name": "Demand Agent",
          "status": "running"
      })
  ```
- [ ] Send "progress" messages during execution:
  ```python
  # After training
  await connection_manager.send_message(session_id, {
      "type": "progress",
      "agent_name": "Demand Agent",
      "progress": 50,
      "message": "Training Prophet and ARIMA models..."
  })

  # After forecasting
  await connection_manager.send_message(session_id, {
      "type": "progress",
      "agent_name": "Demand Agent",
      "progress": 90,
      "message": "Generating ensemble forecast..."
  })
  ```
- [ ] Send "complete" message with result:
  ```python
  await connection_manager.send_message(session_id, {
      "type": "complete",
      "agent_name": "Demand Agent",
      "result": output
  })
  ```

**Acceptance:**
- WebSocket messages sent in correct order
- Progress updates reflect actual execution stages
- Frontend receives messages correctly

---

### Task 4: Register Agent with AgentHandoffManager

**Goal:** Enable orchestrator to call DemandAgent

**Subtasks:**
- [ ] Locate agent registration in `backend/app/orchestrator/agent_registry.py` or similar
- [ ] Register demand agent:
  ```python
  from backend.app.agents.demand_agent import DemandAgent

  demand_agent = DemandAgent()

  handoff_manager.register_agent(
      name="demand",
      handler=demand_agent.execute
  )
  ```
- [ ] Update orchestrator to use real agent instead of mock
- [ ] Remove or comment out mock demand agent code
- [ ] Test agent registration

**Acceptance:**
- Agent registered successfully
- Orchestrator can call demand agent by name
- No mock agent conflicts

---

### Task 5: Write End-to-End Integration Test

**Goal:** Verify full workflow with real agent

**Subtasks:**
- [ ] Create file: `backend/tests/integration/test_demand_agent_integration.py`
- [ ] **Test:** `test_demand_agent_end_to_end_workflow()`
  - Create SeasonParameters (12 weeks, 2025-03-01 start)
  - Build DemandAgentContext using ContextAssembler
  - Execute DemandAgent
  - Assert output matches DemandAgentOutput schema
  - Assert total_demand > 0
  - Assert forecast_by_week has 12 elements
  - Assert safety_stock_pct in [0.1, 0.5]
  - Assert confidence in [0.0, 1.0]
  - Assert model_used is valid string
- [ ] **Test:** `test_demand_agent_with_orchestrator()`
  - Call orchestrator run_workflow endpoint
  - Verify WebSocket messages received
  - Verify forecast_result returned
  - Assert workflow completes in <15 seconds
- [ ] **Test:** `test_demand_agent_error_handling()`
  - Test with insufficient historical data
  - Test with invalid parameters
  - Assert errors raised correctly

**Acceptance:**
- All 3 integration tests pass
- End-to-end workflow verified

---

### Task 6: Performance Optimization

**Goal:** Meet <10 second forecast generation target

**Subtasks:**
- [ ] Profile code with cProfile:
  ```bash
  python -m cProfile -o demand_agent.prof test_demand_agent.py
  ```
- [ ] Identify bottlenecks (likely model training)
- [ ] Optimize slowest operations:
  - Cache trained models if parameters unchanged
  - Use Phase 5 cached historical data (don't reload from database)
  - Parallelize Prophet and ARIMA training (if beneficial)
- [ ] Re-measure performance after optimizations
- [ ] Document optimization results in commit message

**Acceptance:**
- Forecast generation <10 seconds
- End-to-end workflow <15 seconds
- Optimization documented

---

### Task 7: Update Frontend (Optional Verification)

**Goal:** Verify forecast data displays in frontend

**Subtasks:**
- [ ] Start backend server with real demand agent
- [ ] Open frontend (http://localhost:3000)
- [ ] Enter parameters, run workflow
- [ ] Verify Section 2 (Forecast Summary) shows real forecast data
- [ ] Verify Section 4 (Weekly Performance Chart) displays correctly
- [ ] Verify WebSocket agent status updates in real-time

**Acceptance:**
- Forecast data visible in frontend
- No UI errors
- Real-time updates working

---

## Testing Strategy

### Unit Tests (Deferred to Individual Wrappers)
- ProphetWrapper tested in Story 1
- ARIMAWrapper tested in Story 2
- EnsembleForecaster tested in Story 3

### Integration Tests (This Story)
- **Test 1:** DemandAgent execute() with valid context
- **Test 2:** DemandAgent with orchestrator workflow
- **Test 3:** DemandAgent error handling
- **Test 4:** WebSocket message flow
- **Test 5:** Output contract validation

### Performance Tests
- End-to-end workflow timing
- Forecast generation timing
- Memory usage profiling

---

## Definition of Done

**Code Complete:**
- [ ] DemandAgent class implemented
- [ ] execute() method working correctly
- [ ] WebSocket progress messages integrated
- [ ] Agent registered with orchestrator
- [ ] Mock agent removed/replaced
- [ ] Type hints and docstrings complete

**Testing Complete:**
- [ ] 3 integration tests passing
- [ ] End-to-end workflow test passing
- [ ] Performance targets met (<10s forecast, <15s workflow)
- [ ] Frontend verification complete

**Quality Checks:**
- [ ] Code follows project style
- [ ] Error handling integrated with Phase 5
- [ ] Logging informative
- [ ] No print or console.log statements

**Documentation:**
- [ ] Docstrings complete
- [ ] Performance results documented
- [ ] Integration with Phase 5 documented
- [ ] Ready for Phase 7 handoff

**Phase 6 Complete:**
- [ ] All 4 stories (001-004) complete
- [ ] MAPE < 15% achieved
- [ ] Real AI forecasting operational
- [ ] Ready to hand off forecast_result to Phase 7 (Inventory Agent)

---

## Notes

**Output Contract Reminder:**
The DemandAgentOutput must match exactly what Phase 7 (Inventory Agent) expects:
```python
{
    "total_demand": int,
    "forecast_by_week": List[int],  # Length = forecast_horizon_weeks
    "safety_stock_pct": float,      # 0.1-0.5 range
    "confidence": float,             # 0.0-1.0 range
    "model_used": str                # "prophet_arima_ensemble" | "prophet" | "arima"
}
```

**Safety Stock Logic:**
- High confidence (0.9) → Low safety stock (0.1 = 10%)
- Medium confidence (0.7) → Medium safety stock (0.3 = 30%)
- Low confidence (0.5) → High safety stock (0.5 = 50%)

**Performance Breakdown Target:**
- Context assembly (Phase 5): <1 second (cached)
- Prophet training: ~3 seconds
- ARIMA training: ~3 seconds
- Forecast generation: ~1 second
- Overhead: ~2 seconds
- **Total:** ~10 seconds

**WebSocket Message Order:**
1. agent_status: "running"
2. progress: 25% (context loaded)
3. progress: 50% (models training)
4. progress: 75% (forecasting)
5. progress: 90% (finalizing)
6. complete: result returned

**Common Issues:**
- Prophet installation on Windows: May require conda
- ARIMA parameter selection slow: Reduce max_p, max_q if needed
- WebSocket connection drops: Check heartbeat mechanism

---

## Handoff to Phase 7

After this story completes, Phase 7 (Inventory Agent) can begin. Phase 7 will:
- Consume forecast_result from DemandAgent
- Use total_demand and forecast_by_week for allocation
- Use safety_stock_pct for buffer calculations
- No changes to Phase 6 code required

**Contract Verification:**
Before starting Phase 7, run:
```python
# Verify output matches contract
output = demand_agent.execute(context)
validated = DemandAgentOutput(**output)  # Should not raise ValidationError
```

---

**Created:** 2025-11-11
**Last Updated:** 2025-11-11
**Version:** 1.0
