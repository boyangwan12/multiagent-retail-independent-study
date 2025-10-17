# Phase 4: Orchestrator Agent - Technical Decisions

**Phase:** 4 of 8
**Agent:** `*agent dev`
**Date:** 2025-10-17
**Status:** Not Started

---

## Key Decisions Summary

1. OpenAI Agents SDK for agent orchestration
2. Parameter-driven conditional execution
3. LLM-based reasoning for workflow decisions
4. Workflow state machine with database persistence
5. >20% variance threshold for re-forecast
6. Context-rich handoffs between agents
7. Human-in-the-loop approval workflow
8. WebSocket for real-time status streaming
9. Synchronous workflow execution (no Celery)
10. Simple phase skip logic (if/else, not complex rule engine)

---

## Decision Log

### Decision 1: Conditional Phase Execution Strategy
**Date:** TBD
**Context:** Need to skip phases based on parameters (e.g., skip replenishment if parameter says "none")

**Options Considered:**
1. **Rules Engine (e.g., Python rules)**
   - Pros: Flexible, declarative rules, easy to add conditions
   - Cons: Overkill for MVP, learning curve, harder to debug

2. **Simple if/else logic**
   - Pros: Easy to understand, fast, straightforward debugging
   - Cons: Less flexible for complex conditions

3. **LLM decides dynamically**
   - Pros: Maximum flexibility, natural language reasoning
   - Cons: Unpredictable, slow, API costs

**Decision:** Simple if/else logic with LLM reasoning for logging

**Rationale:** MVP has clear parameter → phase mapping. If/else is sufficient, fast, and debuggable. Add LLM calls for reasoning explanations (logging only).

**Implementation Notes:**
```python
async def should_execute_phase_3(params):
    if params.replenishment_strategy == "none":
        return False, "No replenishment configured"
    return True, "Weekly replenishment enabled"
```

---

### Decision 2: Variance Monitoring Frequency
**Date:** TBD
**Context:** How often to check actual vs forecast variance

**Options Considered:**
1. **Real-time (every transaction)**
   - Pros: Immediate detection
   - Cons: Expensive, not needed for weekly forecasts

2. **Daily**
   - Pros: Responsive, catches issues early
   - Cons: Noisy data, too frequent for season-level forecasts

3. **Weekly**
   - Pros: Matches forecast granularity, stable data
   - Cons: Slower reaction time

**Decision:** Weekly monitoring

**Rationale:** Forecasts are weekly granularity. Daily monitoring adds noise without value. Weekly actuals uploaded manually (CSV), so monitoring cadence matches data availability.

**Implementation Notes:** Monitor when weekly actuals CSV uploaded via `POST /api/data/upload/actuals`

---

### Decision 3: Workflow State Persistence
**Date:** TBD
**Context:** Where to store workflow state for resumption after human approval

**Options Considered:**
1. **In-memory (Python dict)**
   - Pros: Fast, simple
   - Cons: Lost on server restart, not scalable

2. **Redis**
   - Pros: Fast, persistent, good for sessions
   - Cons: Extra dependency, overkill for single-user MVP

3. **SQLite database**
   - Pros: Persistent, no extra dependencies, query-able
   - Cons: Slightly slower than Redis

**Decision:** SQLite database

**Rationale:** Already using SQLite for data. No need for Redis. Persistence critical for human approval (user may close browser). Query-able for debugging.

**Implementation Notes:** Create `workflows` table with JSON column for state

---

### Decision 4: Human Approval Mechanism
**Date:** TBD
**Context:** How to pause workflow for human approval (manufacturing, markdown)

**Options Considered:**
1. **Polling (frontend polls backend)**
   - Pros: Simple, no WebSocket needed
   - Cons: Inefficient, delays, poor UX

2. **WebSocket bidirectional**
   - Pros: Real-time, instant updates, good UX
   - Cons: More complex, connection management

3. **Webhooks**
   - Pros: Clean API
   - Cons: Requires public URL, overkill for local MVP

**Decision:** WebSocket bidirectional

**Rationale:** Already using WebSocket for agent status updates. Reuse for approval requests/responses. Best UX (instant notifications). MVP is local (no webhook URL needed).

**Implementation Notes:**
```python
# Backend sends approval request via WebSocket
await websocket.send_json({
    "type": "approval_request",
    "data": manufacturing_order
})

# Frontend user clicks Accept/Modify
# Frontend sends approval response via WebSocket
await websocket.send_json({
    "type": "approval_response",
    "action": "accept"
})
```

---

### Decision 5: Re-Forecast Trigger Threshold
**Date:** TBD
**Context:** What variance percentage triggers automatic re-forecast

**Options Considered:**
1. **10% threshold (sensitive)**
   - Pros: Catches small issues early
   - Cons: Too many false positives, re-forecast fatigue

2. **20% threshold (moderate)**
   - Pros: Balanced, avoids false positives
   - Cons: May miss moderate issues

3. **30% threshold (conservative)**
   - Pros: Only triggers for major issues
   - Cons: Slow to react

**Decision:** 20% threshold

**Rationale:** Industry standard for "significant deviation". Balances responsiveness vs stability. Matches planning docs (process_workflow_v3.3.md).

**Implementation Notes:** Absolute variance: `abs((actual - forecast) / forecast) > 0.20`

---

### Decision 6: Handoff Context Structure
**Date:** TBD
**Context:** What data to pass between agents via handoffs

**Options Considered:**
1. **Minimal (IDs only)**
   - Pros: Lightweight, forces database queries
   - Cons: Slow, requires database reads, not "context-rich"

2. **Full objects**
   - Pros: Fast, context-rich, no database queries
   - Cons: Larger payloads, JSON serialization

**Decision:** Full objects (context-rich handoffs)

**Rationale:** Technical architecture specifies "context-rich handoffs". Agents should receive complete context without database queries. Performance acceptable for MVP (<100 stores).

**Implementation Notes:**
```python
context = {
    "workflow_id": "wf_123",
    "parameters": {
        "forecast_horizon_weeks": 12,
        "replenishment_strategy": "none"
    },
    "forecast": {
        "total_season_demand": 8000,
        "weekly_curve": [...],
        "cluster_distribution": [...]
    }
}
```

---

### Decision 7: Error Handling Strategy
**Date:** TBD
**Context:** What to do when an agent fails

**Options Considered:**
1. **Fail fast (stop workflow)**
   - Pros: Simple, clear errors
   - Cons: Poor UX, no recovery

2. **Retry with exponential backoff**
   - Pros: Handles transient errors
   - Cons: Delays, may retry forever

3. **Retry 3 times, then human intervention**
   - Pros: Balanced, clear escalation
   - Cons: Slightly more complex

**Decision:** Retry 3 times, then human intervention

**Rationale:** Handles transient OpenAI API errors (rate limits). After 3 retries, escalate to user (WebSocket error notification). User can restart workflow manually.

**Implementation Notes:**
```python
for attempt in range(3):
    try:
        result = await agent.run(context)
        break
    except OpenAIError as e:
        if attempt == 2:
            await send_error_notification(workflow_id, e)
            raise
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

### Decision 8: Workflow Execution Model
**Date:** TBD
**Context:** Synchronous vs asynchronous workflow execution

**Options Considered:**
1. **Synchronous (blocking API call)**
   - Pros: Simple, no background tasks
   - Cons: Long HTTP requests (>60s), timeout risk

2. **Async with Celery**
   - Pros: Non-blocking, production-ready
   - Cons: Requires Redis/RabbitMQ, overkill for MVP

3. **Async with FastAPI BackgroundTasks**
   - Pros: No extra dependencies, non-blocking
   - Cons: Lost on server restart

**Decision:** Synchronous for MVP (with timeout warnings)

**Rationale:** MVP workflows run locally. Forecast takes <10s (mocked ML). User waits for result. Celery adds complexity without value for single-user local dev.

**Future:** Migrate to Celery for production (multi-user, slower ML).

**Implementation Notes:** FastAPI endpoint with 60s timeout, WebSocket for progress

---

### Decision 9: LLM Reasoning Integration
**Date:** TBD
**Context:** When to call LLM for orchestrator reasoning

**Options Considered:**
1. **Every decision**
   - Pros: Maximum reasoning, rich logs
   - Cons: Slow, expensive, API quota

2. **Never (pure logic)**
   - Pros: Fast, deterministic
   - Cons: Loses parameter-driven intelligence

3. **Key decisions only (phase skip, variance)**
   - Pros: Balanced, explanations where needed
   - Cons: Selective reasoning

**Decision:** Key decisions only

**Rationale:** Use LLM for reasoning explanations (why phase skipped, variance interpretation). Pure logic for execution (faster, deterministic). Best balance.

**Implementation Notes:** LLM calls only for logging/explanations, not execution decisions

---

### Decision 10: Parameter Validation
**Date:** TBD
**Context:** Where to validate extracted parameters

**Options Considered:**
1. **Frontend only**
   - Pros: Immediate feedback
   - Cons: Can be bypassed, no backend safety

2. **Backend only**
   - Pros: Secure, single source of truth
   - Cons: Late feedback, poor UX

3. **Both (frontend + backend)**
   - Pros: Best UX + security
   - Cons: Duplicate code

**Decision:** Both (Pydantic on backend, Zod on frontend)

**Rationale:** Frontend validation (Zod) for instant UX. Backend validation (Pydantic) for security/safety. Pydantic is source of truth (models shared).

**Implementation Notes:** Use Pydantic's `SeasonParameters` model on backend, generate TypeScript types for frontend

---

## Key Metrics (TBD after implementation)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Workflow execution time | <60s | TBD | TBD |
| Variance detection accuracy | >90% | TBD | TBD |
| Phase skip logic correctness | 100% | TBD | TBD |
| Human approval response time | <30s | TBD | TBD |
| WebSocket message delivery | >99% | TBD | TBD |

---

## Future Enhancements

### Enhancement 1: Celery for Background Tasks
**Description:** Move workflow execution to Celery background tasks
**Benefit:** Non-blocking API, better for production, resumable after server restart
**Effort:** Medium (add Celery + Redis broker)
**Priority:** High (needed for production)

### Enhancement 2: Workflow Visualization
**Description:** DAG visualization of workflow execution
**Benefit:** Better debugging, user understanding
**Effort:** Medium (frontend D3.js graph)
**Priority:** Low (nice-to-have)

### Enhancement 3: A/B Testing Parameters
**Description:** Run multiple parameter sets in parallel, compare results
**Benefit:** Data-driven parameter tuning
**Effort:** High (parallel execution, comparison UI)
**Priority:** Low (post-MVP)

---

## Key Takeaways (to be filled after implementation)

### What Worked Well
- TBD

### Lessons Learned
- TBD

### For Next Phase (Phase 5: Demand Agent)
- TBD

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Status:** Phase 4 Not Started
