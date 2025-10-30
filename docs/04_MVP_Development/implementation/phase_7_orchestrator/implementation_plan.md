# Phase 4: Orchestrator Agent - Implementation Plan

**Phase:** 4 of 8
**Goal:** Implement central coordinator agent for parameter-driven multi-agent workflow
**Agent:** `*agent dev`
**Duration Estimate:** 4-5 days
**Actual Duration:** TBD
**Status:** Not Started

---

## Requirements Source

- **Primary:** `planning/2_process_workflow_v3.3.md` - Complete workflow with agent reasoning
- **Secondary:** `planning/3_technical_architecture_v3.3.md` - Orchestrator specs
- **Reference:** `planning/1_product_brief_v3.3.md` - Business context

---

## Key Deliverables

1. **Orchestrator Agent Core Logic**
   - Parameter-aware workflow coordination
   - Sequential agent handoff management
   - Dynamic handoff enabling/disabling

2. **Variance Monitoring System**
   - Track actual vs forecast weekly
   - Detect >20% variance threshold
   - Trigger re-forecast workflow

3. **Conditional Phase Execution**
   - Skip replenishment if parameters say "none"
   - Skip markdown if parameters say null
   - Parameter-driven phase control

4. **Context-Rich Handoffs**
   - Pass parameters to all agents
   - Include complete context objects
   - Enable agent-to-agent data flow

5. **Human-in-the-Loop Integration**
   - Manufacturing approval workflow
   - Markdown approval workflow
   - WebSocket status streaming

6. **LLM Reasoning Layer**
   - Orchestrator uses LLM to interpret parameters
   - Decision explanations for logging
   - Dynamic workflow adaptation

---

## Task Breakdown

### Task 1: Orchestrator Agent Foundation
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Phase 3 complete
**Status:** Not Started

**Subtasks:**
- [ ] Create `backend/app/agents/orchestrator.py`
- [ ] Define Orchestrator agent with OpenAI Agents SDK
- [ ] Implement LLM instructions for parameter interpretation
- [ ] Configure handoffs to 3 agents (demand, inventory, pricing)
- [ ] Add parameter context to agent initialization
- [ ] Test basic agent creation and handoff registration

**Orchestrator Agent Structure:**
```python
from openai_agents import Agent

orchestrator = Agent(
    name="Orchestrator",
    instructions="""
    You are the central coordinator for a parameter-driven forecasting system.

    Your responsibilities:
    1. Interpret user-provided parameters (forecast_horizon_weeks, replenishment_strategy,
       dc_holdback_percentage, markdown_checkpoint_week)
    2. Coordinate handoffs to 3 specialized agents: Demand, Inventory, Pricing
    3. Monitor weekly variance (actual vs forecast)
    4. Conditionally enable/disable phases based on parameters
    5. Trigger re-forecast when variance >20%

    Parameter reasoning examples:
    - IF replenishment_strategy = "none" → Skip Phase 3 (replenishment) entirely
    - IF markdown_checkpoint_week = null → Skip Phase 4 (markdown) entirely
    - IF dc_holdback_percentage = 0.0 → All inventory ships at Week 0

    Always pass full parameter context to agents via handoffs.
    """,
    model="gpt-4o-mini",
    handoffs=["demand", "inventory", "pricing"]
)
```

### Task 2: Parameter Context Handling
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 1
**Status:** Not Started

**Subtasks:**
- [ ] Create `ParameterContext` data class
- [ ] Implement parameter validation and defaults
- [ ] Build parameter distribution logic (orchestrator → agents)
- [ ] Add parameter logging for debugging
- [ ] Test parameter passing through handoffs

**ParameterContext Structure:**
```python
@dataclass
class ParameterContext:
    forecast_horizon_weeks: int
    season_start_date: date
    season_end_date: date
    replenishment_strategy: str  # "none" | "weekly" | "bi-weekly"
    dc_holdback_percentage: float  # 0.0-1.0
    markdown_checkpoint_week: Optional[int]
    markdown_threshold: Optional[float]

    def to_agent_context(self, agent_name: str) -> dict:
        """Return relevant parameters for specific agent"""
        if agent_name == "demand":
            return {
                "forecast_horizon_weeks": self.forecast_horizon_weeks,
                "replenishment_strategy": self.replenishment_strategy
            }
        elif agent_name == "inventory":
            return {
                "dc_holdback_percentage": self.dc_holdback_percentage,
                "replenishment_strategy": self.replenishment_strategy
            }
        elif agent_name == "pricing":
            return {
                "markdown_checkpoint_week": self.markdown_checkpoint_week,
                "markdown_threshold": self.markdown_threshold
            }
```

### Task 3: Workflow State Machine
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 1, Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Define workflow states (Enum)
- [ ] Implement state transition logic
- [ ] Create workflow persistence (save to database)
- [ ] Add state validation
- [ ] Implement workflow resumption (after human approval)
- [ ] Test state machine with mock data

**Workflow States:**
```python
class WorkflowState(Enum):
    PARAMETERS_EXTRACTED = "parameters_extracted"
    PHASE_1_FORECASTING = "phase_1_forecasting"
    WAITING_MFG_APPROVAL = "waiting_mfg_approval"
    PHASE_2_ALLOCATION = "phase_2_allocation"
    PHASE_3_MONITORING = "phase_3_monitoring"
    PHASE_3_REPLENISHMENT = "phase_3_replenishment"  # May be skipped
    PHASE_4_MARKDOWN_CHECK = "phase_4_markdown_check"  # May be skipped
    WAITING_MARKDOWN_APPROVAL = "waiting_markdown_approval"
    PHASE_5_REFORECAST = "phase_5_reforecast"
    COMPLETED = "completed"
    ERROR = "error"
```

### Task 4: Variance Monitoring System
**Estimate:** 5 hours
**Actual:** TBD
**Dependencies:** Task 3
**Status:** Not Started

**Subtasks:**
- [ ] Create `VarianceMonitor` class
- [ ] Implement weekly variance calculation
- [ ] Add >20% threshold detection
- [ ] Implement re-forecast trigger logic
- [ ] Create variance history tracking (database)
- [ ] Add WebSocket notifications for variance events
- [ ] Test variance detection with Phase 1 CSV data

**Variance Calculation Logic:**
```python
class VarianceMonitor:
    def calculate_weekly_variance(
        self,
        forecast: int,
        actual: int,
        week_number: int
    ) -> VarianceResult:
        """Calculate variance and determine if re-forecast needed"""
        variance_pct = abs((actual - forecast) / forecast) * 100

        return VarianceResult(
            week_number=week_number,
            forecast=forecast,
            actual=actual,
            variance_percentage=variance_pct,
            variance_direction="over" if actual > forecast else "under",
            reforecast_triggered=variance_pct > 20.0,
            timestamp=datetime.now()
        )

    async def monitor_weekly_actuals(
        self,
        workflow_id: str,
        week_number: int,
        actuals: List[StoreActual]
    ):
        """Monitor weekly actuals and trigger re-forecast if needed"""
        forecast = await self.get_forecast_for_week(workflow_id, week_number)
        total_actual = sum(a.quantity_sold for a in actuals)

        variance = self.calculate_weekly_variance(
            forecast=forecast,
            actual=total_actual,
            week_number=week_number
        )

        if variance.reforecast_triggered:
            await self.trigger_reforecast(workflow_id, variance)
            await self.send_websocket_alert(workflow_id, variance)
```

### Task 5: Conditional Phase Execution
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 2, Task 3
**Status:** Not Started

**Subtasks:**
- [ ] Implement replenishment phase skip logic
- [ ] Implement markdown phase skip logic
- [ ] Add LLM reasoning for phase decisions
- [ ] Log skip decisions to database
- [ ] Send WebSocket notifications for skipped phases
- [ ] Test phase skipping with different parameter sets

**Conditional Logic:**
```python
async def should_execute_phase_3_replenishment(
    self,
    parameters: ParameterContext
) -> tuple[bool, str]:
    """Determine if replenishment phase should run"""
    if parameters.replenishment_strategy == "none":
        reasoning = (
            f"Replenishment strategy is '{parameters.replenishment_strategy}'. "
            f"DC holdback is {parameters.dc_holdback_percentage * 100}%. "
            f"All inventory was shipped to stores at Week 0. "
            f"Skip Phase 3 (replenishment) entirely."
        )
        return False, reasoning

    reasoning = (
        f"Replenishment strategy is '{parameters.replenishment_strategy}'. "
        f"DC holdback is {parameters.dc_holdback_percentage * 100}%. "
        f"Execute Phase 3 (replenishment) with {parameters.replenishment_strategy} cadence."
    )
    return True, reasoning

async def should_execute_phase_4_markdown(
    self,
    parameters: ParameterContext
) -> tuple[bool, str]:
    """Determine if markdown phase should run"""
    if parameters.markdown_checkpoint_week is None:
        reasoning = (
            "No markdown checkpoint configured (markdown_checkpoint_week = null). "
            "User specified luxury/premium positioning with no markdowns. "
            "Skip Phase 4 (markdown) entirely."
        )
        return False, reasoning

    reasoning = (
        f"Markdown checkpoint configured for Week {parameters.markdown_checkpoint_week} "
        f"with {parameters.markdown_threshold * 100}% threshold. "
        f"Execute Phase 4 (markdown check) at Week {parameters.markdown_checkpoint_week}."
    )
    return True, reasoning
```

### Task 6: Agent Handoff Management
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 1, Task 2
**Status:** Not Started

**Subtasks:**
- [ ] Implement handoff context builder
- [ ] Create agent handoff execution logic
- [ ] Add error handling for agent failures
- [ ] Implement handoff result parsing
- [ ] Add handoff history tracking (database)
- [ ] Test handoff flow with mock agents

**Handoff Flow:**
```python
async def execute_phase_1_forecast(
    self,
    workflow_id: str,
    parameters: ParameterContext
):
    """Orchestrator hands off to Demand Agent"""
    # Build context for Demand Agent
    context = {
        "workflow_id": workflow_id,
        "parameters": parameters.to_agent_context("demand"),
        "phase": "phase_1_forecasting",
        "instruction": (
            f"Forecast demand for {parameters.forecast_horizon_weeks} weeks. "
            f"Replenishment strategy: {parameters.replenishment_strategy}. "
            f"Adjust safety stock accordingly."
        )
    }

    # Hand off to Demand Agent
    result = await self.handoff_to_agent(
        agent_name="demand",
        context=context
    )

    # Parse result and update workflow
    forecast = result["forecast"]
    await self.update_workflow_state(
        workflow_id,
        state=WorkflowState.WAITING_MFG_APPROVAL,
        forecast=forecast
    )

    # Request human approval
    await self.request_manufacturing_approval(workflow_id, forecast)
```

### Task 7: Human Approval Workflow
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 3, Task 6
**Status:** Not Started

**Subtasks:**
- [ ] Implement manufacturing approval wait logic
- [ ] Implement markdown approval wait logic
- [ ] Create approval response handlers
- [ ] Add approval timeout handling
- [ ] Implement workflow resumption after approval
- [ ] Test approval workflow with frontend mock

**Approval Workflow:**
```python
async def request_manufacturing_approval(
    self,
    workflow_id: str,
    forecast: ForecastResult
):
    """Request human approval for manufacturing order"""
    approval_request = ApprovalRequest(
        workflow_id=workflow_id,
        type="manufacturing",
        data={
            "manufacturing_qty": forecast.manufacturing_qty,
            "safety_stock_pct": forecast.safety_stock_pct,
            "total_forecast": forecast.total_season_demand
        },
        status="pending"
    )

    await self.db.save_approval_request(approval_request)
    await self.send_websocket_approval_request(workflow_id, approval_request)

    # Pause workflow until approval received
    await self.pause_workflow(workflow_id)

async def handle_manufacturing_approval(
    self,
    workflow_id: str,
    approval: ApprovalResponse
):
    """Resume workflow after manufacturing approval"""
    if approval.action == "accept":
        # Continue with approved manufacturing order
        await self.resume_workflow(
            workflow_id,
            next_state=WorkflowState.PHASE_2_ALLOCATION
        )
    elif approval.action == "modify":
        # Re-run Demand Agent with modified parameters
        await self.rerun_phase_1_with_modifications(
            workflow_id,
            modifications=approval.modifications
        )
```

### Task 8: WebSocket Status Streaming
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 3
**Status:** Not Started

**Subtasks:**
- [ ] Implement orchestrator status updates
- [ ] Add agent progress notifications
- [ ] Create variance alert messages
- [ ] Implement approval request messages
- [ ] Add error notification messages
- [ ] Test WebSocket streaming with frontend

**WebSocket Message Types:**
```python
# Agent status update
{
    "type": "agent_status",
    "workflow_id": "wf_12345",
    "agent": "orchestrator",
    "status": "thinking",
    "message": "Evaluating replenishment parameters...",
    "progress": 0.25,
    "timestamp": "2025-10-17T14:23:45Z"
}

# Variance alert
{
    "type": "variance_alert",
    "workflow_id": "wf_12345",
    "week_number": 5,
    "variance_percentage": 31.8,
    "variance_direction": "over",
    "reforecast_triggered": true,
    "message": "Week 5 variance 31.8% exceeds 20% threshold. Triggering re-forecast.",
    "timestamp": "2025-10-17T14:24:10Z"
}

# Phase skip notification
{
    "type": "phase_skipped",
    "workflow_id": "wf_12345",
    "phase": "phase_3_replenishment",
    "reason": "Replenishment strategy is 'none'. All inventory shipped at Week 0.",
    "timestamp": "2025-10-17T14:25:00Z"
}
```

### Task 9: LLM Reasoning Integration
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 1, Task 5
**Status:** Not Started

**Subtasks:**
- [ ] Create LLM prompt templates for orchestrator decisions
- [ ] Implement LLM call wrapper with retry logic
- [ ] Add reasoning extraction and parsing
- [ ] Log all LLM reasoning to database
- [ ] Test LLM reasoning with various parameter sets

**LLM Reasoning Example:**
```python
async def get_orchestrator_reasoning(
    self,
    parameters: ParameterContext,
    decision_point: str
) -> str:
    """Get LLM reasoning for orchestrator decision"""
    prompt = f"""
    You are the Orchestrator agent coordinating a retail forecasting workflow.

    Parameters:
    - Forecast horizon: {parameters.forecast_horizon_weeks} weeks
    - Replenishment strategy: {parameters.replenishment_strategy}
    - DC holdback: {parameters.dc_holdback_percentage * 100}%
    - Markdown checkpoint: Week {parameters.markdown_checkpoint_week}

    Decision point: {decision_point}

    Explain how these parameters affect the workflow execution.
    Focus on: Which phases to execute? Which to skip? Why?
    """

    response = await self.llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
```

### Task 10: Error Handling & Recovery
**Estimate:** 3 hours
**Actual:** TBD
**Dependencies:** Task 3, Task 6
**Status:** Not Started

**Subtasks:**
- [ ] Implement agent failure handling
- [ ] Add workflow retry logic
- [ ] Create error state management
- [ ] Implement partial workflow recovery
- [ ] Add error logging and notifications
- [ ] Test error scenarios

### Task 11: Integration Testing
**Estimate:** 4 hours
**Actual:** TBD
**Dependencies:** Task 1-10
**Status:** Not Started

**Subtasks:**
- [ ] Test end-to-end workflow with Zara parameters (no replenishment)
- [ ] Test end-to-end workflow with standard retail parameters (weekly replenishment)
- [ ] Test variance detection and re-forecast trigger
- [ ] Test phase skipping logic
- [ ] Test human approval workflow
- [ ] Test error handling and recovery
- [ ] Validate WebSocket message flow

### Task 12: Documentation & Logging
**Estimate:** 2 hours
**Actual:** TBD
**Dependencies:** Task 1-11
**Status:** Not Started

**Subtasks:**
- [ ] Document orchestrator logic
- [ ] Add inline code comments
- [ ] Create orchestrator API documentation
- [ ] Document parameter interpretation logic
- [ ] Add workflow state diagram
- [ ] Create troubleshooting guide

---

## Total Estimates vs Actuals

- **Total Tasks:** 12
- **Estimated Time:** 41 hours (4-5 days at 8-10h/day)
- **Actual Time:** TBD
- **Variance:** TBD

---

## Validation Checkpoints

### Checkpoint 1: Mid-Phase (40% complete)
**After:** Task 5 complete
**Verify:**
- [ ] Orchestrator agent created with OpenAI Agents SDK
- [ ] Parameters passed correctly through handoffs
- [ ] Workflow state machine functional
- [ ] Variance monitoring working (>20% detection)
- [ ] Conditional phase execution logic implemented

### Checkpoint 2: Pre-Completion (80% complete)
**After:** Task 10 complete
**Verify:**
- [ ] Agent handoffs working with mock agents
- [ ] Human approval workflow functional
- [ ] WebSocket status streaming working
- [ ] LLM reasoning integrated
- [ ] Error handling implemented
- [ ] All phase skip logic working

### Checkpoint 3: Final
**After:** Task 12 complete
**Verify:**
- [ ] End-to-end workflow test passing (Zara parameters)
- [ ] End-to-end workflow test passing (standard retail parameters)
- [ ] Variance detection triggers re-forecast correctly
- [ ] Documentation complete
- [ ] Ready for handoff to Phase 5 (Demand Agent)

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI Agents SDK handoff complexity | Medium | High | Study SDK docs thoroughly, create test harness for handoffs |
| Workflow state persistence issues | Low | Medium | Use robust database transactions, implement state recovery |
| LLM reasoning inconsistency | Medium | Medium | Test extensively with various parameter sets, add validation |
| WebSocket connection instability | Medium | Medium | Implement reconnection logic, use heartbeat ping/pong |
| Parameter interpretation errors | Low | High | Add comprehensive parameter validation, default fallbacks |

---

## Notes

- This phase implements orchestrator LOGIC only
- Agent implementations (demand, inventory, pricing) still use mocks
- Actual ML models integrated in Phase 5-7
- Focus on parameter-driven workflow adaptation
- LLM reasoning adds intelligence to workflow decisions
- Human-in-the-loop for critical decisions (manufacturing, markdown)

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Not Started
