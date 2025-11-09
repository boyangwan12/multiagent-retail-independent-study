# Story: Enhanced Error Handling and Resilience for Polling-Based Orchestrator

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-005
**Status:** Review
**Estimate:** 2 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001, PHASE5-002, PHASE5-004

**Planning References:**
- PRD v3.3: Section 5.3 (Error Handling & Recovery)
- Technical Architecture v3.3: Section 6.2 (Error Handling Strategy)

---

## Story

As a backend developer,
I want to enhance error handling across the orchestrator workflow with clear error states and logging,
So that failures are caught gracefully, users receive helpful status updates via polling, and developers can debug issues quickly.

**Business Value:** Production-ready error handling is what separates a prototype from a reliable system. When agents fail (timeout, missing data, internal error), users need clear feedback via the polling status endpoint. Developers need detailed logs to diagnose issues. This story enhances the existing timeout handling in AgentHandoffManager with additional error scenarios, better logging, and graceful degradation.

**Epic Context:** This is Story 5 of 6 in Phase 5 (Orchestrator Foundation). It builds on the timeout handling already implemented in AgentHandoffManager (Story 2) and adds error scenarios discovered during agent execution. This establishes error handling patterns for Phase 6+ when real agents may encounter data issues, API failures, or ML model errors.

**Phase 5 Update:** This story is simplified from the original PHASE5-005 which assumed WebSocket-based error streaming and complex exception hierarchies. Since we use polling-based status updates, errors are communicated through workflow status fields (`status="failed"`, `error_message="..."`). We already have timeout handling in AgentHandoffManager - this story enhances it with additional error scenarios and better logging.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ Workflow status includes clear error states for polling clients
   - `status="failed"` when workflow encounters unrecoverable error
   - `error_message` field populated with user-friendly message
   - `error_details` field (optional) with technical details for debugging

2. ✅ Agent timeout errors handled gracefully (already exists, enhance logging)
   - Workflow marked as "failed" with error_message: "Agent {name} timed out after {timeout}s"
   - Timeout logged with agent name, context summary, and duration

3. ✅ Agent execution errors caught and reported
   - Python exceptions during agent execution caught
   - Workflow marked as "failed" with sanitized error message
   - Full stack trace logged (not sent to frontend)

4. ✅ Database errors handled gracefully
   - Connection failures during status updates logged and retried (1 retry)
   - Workflow state preserved even if DB write fails

5. ✅ Parameter validation errors return clear 422 responses
   - Missing required fields listed
   - Invalid value ranges explained
   - Example valid input provided

6. ✅ Workflow not found errors return 404 with helpful message
   - "Workflow {id} not found. Verify workflow was created successfully."

### Quality Requirements

7. ✅ All errors logged with structured context:
   ```python
   logger.error(
       f"Agent execution failed",
       extra={
           "workflow_id": workflow_id,
           "agent_name": agent_name,
           "error_type": type(e).__name__,
           "error_message": str(e)
       }
   )
   ```

8. ✅ Error messages are user-friendly (no stack traces, no internal paths)
9. ✅ Sensitive data never exposed (no API keys, no database credentials)
10. ✅ Error handling doesn't swallow original exceptions (re-raise after logging)
11. ✅ Unit tests for each error scenario

---

## Prerequisites

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete - includes timeout handling
- [x] PHASE5-004 (Enhanced Mock Agents) complete

**Existing Error Handling:**
- [x] AgentHandoffManager has timeout handling (asyncio.TimeoutError)
- [x] MockOrchestratorService catches exceptions and updates workflow status
- [x] Basic logging configured

**Why This Matters:**
When users report "the workflow failed," you need logs that show exactly what failed. This story ensures every error scenario is logged with enough context for rapid debugging.

---

## Tasks

### Task 1: Enhance Timeout Error Handling

**Goal:** Improve logging and error messages for agent timeouts

**File:** `backend/app/orchestrator/agent_handoff.py`

**Current Code (Lines 109-115):**
```python
except asyncio.TimeoutError:
    status = "timeout"
    self.logger.error(f"Agent '{agent_name}' timed out after {timeout}s")
    raise
```

**Enhancement:**
```python
except asyncio.TimeoutError:
    status = "timeout"

    # Enhanced logging with context
    self.logger.error(
        f"Agent timeout: '{agent_name}' exceeded {timeout}s limit",
        extra={
            "agent_name": agent_name,
            "timeout_seconds": timeout,
            "context_summary": str(context)[:200] if context else "None"  # Truncate long context
        }
    )

    # Re-raise with more helpful message
    raise TimeoutError(
        f"Agent '{agent_name}' exceeded maximum execution time ({timeout}s). "
        f"This may indicate a problem with the agent logic or external API calls."
    )
```

**Subtasks:**
- [ ] Update `call_agent()` method in `agent_handoff.py` (line 109-115)
- [ ] Add structured logging with extra context
- [ ] Improve error message for users

---

### Task 2: Enhance General Exception Handling

**Goal:** Catch and log all agent execution errors gracefully

**File:** `backend/app/orchestrator/agent_handoff.py`

**Current Code (Lines 117-120):**
```python
except Exception as e:
    status = "failed"
    self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
    raise
```

**Enhancement:**
```python
except Exception as e:
    status = "failed"

    # Enhanced logging with stack trace
    self.logger.error(
        f"Agent execution failed: '{agent_name}'",
        exc_info=True,  # Includes full stack trace in logs
        extra={
            "agent_name": agent_name,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "context_type": type(context).__name__
        }
    )

    # Re-raise with sanitized message (no internal details)
    raise RuntimeError(
        f"Agent '{agent_name}' encountered an error during execution. "
        f"Check server logs for details."
    ) from e
```

**Subtasks:**
- [ ] Update exception handler in `call_agent()` (line 117-120)
- [ ] Add `exc_info=True` for stack traces in logs
- [ ] Sanitize error messages before re-raising

---

### Task 3: Enhance MockOrchestratorService Error Handling

**Goal:** Add database retry logic and better error reporting

**File:** `backend/app/services/mock_orchestrator_service.py`

**Current Code (Lines 109-123):**
```python
except asyncio.TimeoutError:
    logger.error(f"[ORCHESTRATOR] Workflow timed out: {workflow_id}")
    workflow.status = WorkflowStatus.failed
    workflow.error_message = "Agent timeout - exceeded maximum execution time"
    workflow.completed_at = datetime.utcnow()
    self.db.commit()
    raise

except Exception as e:
    logger.error(f"[ORCHESTRATOR] Workflow execution failed: {e}", exc_info=True)
    workflow.status = WorkflowStatus.failed
    workflow.error_message = str(e)
    workflow.completed_at = datetime.utcnow()
    self.db.commit()
    raise
```

**Enhancement:**
```python
except asyncio.TimeoutError as e:
    error_msg = str(e)  # Includes enhanced message from AgentHandoffManager
    logger.error(
        f"[ORCHESTRATOR] Workflow timed out: {workflow_id}",
        extra={"workflow_id": workflow_id, "error_message": error_msg}
    )

    # Update workflow status with retry
    try:
        workflow.status = WorkflowStatus.failed
        workflow.error_message = error_msg
        workflow.completed_at = datetime.utcnow()
        self.db.commit()
    except Exception as db_error:
        logger.error(f"Failed to update workflow status after timeout: {db_error}")
        # Try one more time with fresh session
        try:
            self.db.rollback()
            workflow = self.db.query(Workflow).filter_by(workflow_id=workflow_id).first()
            if workflow:
                workflow.status = WorkflowStatus.failed
                workflow.error_message = error_msg
                workflow.completed_at = datetime.utcnow()
                self.db.commit()
        except:
            logger.critical(f"Cannot update workflow status - database issue", exc_info=True)

    raise

except Exception as e:
    error_msg = str(e)
    logger.error(
        f"[ORCHESTRATOR] Workflow execution failed: {workflow_id}",
        exc_info=True,
        extra={
            "workflow_id": workflow_id,
            "error_type": type(e).__name__,
            "error_message": error_msg
        }
    )

    # Update workflow status with retry (same pattern)
    try:
        workflow.status = WorkflowStatus.failed
        workflow.error_message = error_msg
        workflow.completed_at = datetime.utcnow()
        self.db.commit()
    except Exception as db_error:
        logger.error(f"Failed to update workflow status: {db_error}")
        try:
            self.db.rollback()
            workflow = self.db.query(Workflow).filter_by(workflow_id=workflow_id).first()
            if workflow:
                workflow.status = WorkflowStatus.failed
                workflow.error_message = error_msg
                workflow.completed_at = datetime.utcnow()
                self.db.commit()
        except:
            logger.critical(f"Cannot update workflow status - database issue", exc_info=True)

    raise
```

**Subtasks:**
- [ ] Add database retry logic (1 retry with rollback)
- [ ] Add structured logging with workflow context
- [ ] Preserve enhanced error messages from AgentHandoffManager

---

### Task 4: Improve FastAPI Error Responses

**Goal:** Return helpful 404 and 422 responses

**File:** `backend/app/api/v1/endpoints/workflows.py`

**Current Code (Lines 159-165):**
```python
try:
    return service.get_workflow_status(workflow_id)
except ValueError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    logger.error(f"Failed to get workflow status: {e}")
    raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")
```

**Enhancement:**
```python
try:
    return service.get_workflow_status(workflow_id)
except ValueError as e:
    # Workflow not found
    raise HTTPException(
        status_code=404,
        detail={
            "error": "Workflow not found",
            "message": f"Workflow '{workflow_id}' does not exist. Verify the workflow was created successfully.",
            "workflow_id": workflow_id
        }
    )
except Exception as e:
    logger.error(
        f"Failed to get workflow status",
        exc_info=True,
        extra={"workflow_id": workflow_id, "error_type": type(e).__name__}
    )
    raise HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error",
            "message": "Failed to retrieve workflow status. Please try again or contact support if the issue persists."
        }
    )
```

**Subtasks:**
- [ ] Update error responses in `get_workflow_status()` endpoint
- [ ] Update error responses in `get_workflow_results()` endpoint
- [ ] Update error responses in `execute_workflow()` endpoint
- [ ] Add structured error response format (dict with error, message fields)

---

### Task 5: Add Unit Tests for Error Scenarios

**Goal:** Test each error handling path

**File:** `backend/tests/test_error_handling.py`

**Subtasks:**
- [ ] Test agent timeout scenario
  ```python
  @pytest.mark.asyncio
  async def test_agent_timeout_error_handling():
      manager = AgentHandoffManager()

      async def slow_agent(ctx):
          await asyncio.sleep(10)  # Exceeds timeout
          return {}

      manager.register_agent("slow", slow_agent)

      with pytest.raises(TimeoutError) as exc_info:
          await manager.call_agent("slow", {}, timeout=2)

      assert "exceeded maximum execution time" in str(exc_info.value)

      # Verify logging
      log = manager.get_execution_log()
      assert log[-1]["status"] == "timeout"
  ```

- [ ] Test agent execution error
  ```python
  @pytest.mark.asyncio
  async def test_agent_execution_error_handling():
      manager = AgentHandoffManager()

      async def failing_agent(ctx):
          raise ValueError("Invalid input data")

      manager.register_agent("failing", failing_agent)

      with pytest.raises(RuntimeError) as exc_info:
          await manager.call_agent("failing", {})

      assert "encountered an error" in str(exc_info.value)

      log = manager.get_execution_log()
      assert log[-1]["status"] == "failed"
  ```

- [ ] Test workflow not found (404)
- [ ] Test invalid parameters (422)

---

## Definition of Done

- [x] Timeout errors include enhanced logging with context
- [x] Agent execution errors logged with full stack traces
- [x] Database updates have retry logic (1 retry)
- [x] FastAPI error responses use structured format
- [x] 404 and 500 errors include helpful user messages
- [x] 5+ unit tests pass (timeout, execution error, not found, etc.) - **7 tests passing**
- [x] All error scenarios tested manually via API
- [x] Changes committed to phase4-integration branch

---

## Notes

**What Changed from Original Story:**

The original PHASE5-005 assumed:
- WebSocket error streaming (we use polling)
- Complex custom exception hierarchy (overkill for mock agents)
- FastAPI global exception handlers (can add later if needed)

**This version focuses on:**
- ✅ Enhancing existing timeout handling (already in AgentHandoffManager)
- ✅ Better structured logging for debugging
- ✅ Database retry logic for resilience
- ✅ Clear error messages via polling status endpoint
- ✅ Minimal code changes, maximum value

**Future Enhancement (Phase 6+):**
When implementing real agents with external APIs (Azure OpenAI, database queries), we may add:
- Retry logic with exponential backoff
- Circuit breaker pattern for external services
- Custom exception types for specific failure modes

For now, enhanced logging + timeout handling + graceful degradation is sufficient.
