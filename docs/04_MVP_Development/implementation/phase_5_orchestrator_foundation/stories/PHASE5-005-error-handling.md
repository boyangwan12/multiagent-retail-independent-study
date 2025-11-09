# Story: Implement Comprehensive Error Handling for Orchestrator

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-005
**Status:** Ready for Implementation
**Estimate:** 4 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001, PHASE5-002, PHASE5-003, PHASE5-004

**Planning References:**
- PRD v3.3: Section 5.3 (Error Handling & Recovery)
- Technical Architecture v3.3: Section 6.2 (Error Handling Strategy)
- Product Brief v3.3: Section 3.4 (Reliability & Error Recovery)

---

## Story

As a backend developer,
I want to implement comprehensive error handling across the orchestrator workflow,
So that failures are caught gracefully, logged for debugging, and users receive helpful error messages.

**Business Value:** Robust error handling is the difference between a production-ready system and a prototype. When forecasting fails (API timeout, missing data, agent error), users need clear feedback about what went wrong and how to fix it. Good error handling also enables rapid debugging - detailed logs help developers identify root causes within minutes instead of hours, reducing downtime and improving reliability.

**Epic Context:** This is Story 5 of 6 in Phase 5 (Orchestrator Foundation). It wraps all previous stories (parameter extraction, agent handoffs, WebSocket updates, context assembly) with error handling. This establishes error handling patterns that will be followed in Phase 6-8 as we add more agents.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ Custom exception classes defined for common failure scenarios
2. ✅ FastAPI exception handlers catch and transform exceptions to HTTP responses
3. ✅ WebSocket error messages sent when workflow fails
4. ✅ Parameter extraction errors return 400 with specific missing fields
5. ✅ Data not found errors return 404 with helpful message
6. ✅ Agent timeout errors return 503 with retry suggestion
7. ✅ Azure OpenAI API errors return 503 without exposing API keys
8. ✅ Validation errors return 422 with field-level details
9. ✅ All errors logged to application logs with full context
10. ✅ Error responses follow consistent JSON schema

### Quality Requirements

11. ✅ Sensitive data (API keys, internal paths) never exposed in errors
12. ✅ Error messages are user-friendly and actionable
13. ✅ Stack traces logged but not sent to frontend
14. ✅ Error handling doesn't swallow original exceptions
15. ✅ Logging includes request IDs for tracing
16. ✅ Unit tests for each exception handler
17. ✅ Integration test with deliberate failures

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete
- [x] PHASE5-003 (WebSocket Streaming) complete
- [x] PHASE5-004 (Context-Rich Handoffs) complete

**FastAPI Error Handling:**
- [ ] FastAPI exception handlers supported
- [ ] Python logging configured
- [ ] Request ID middleware available (or will be created)

**Why This Matters:**
Poor error handling creates support nightmares. When users report "it doesn't work," you need logs that show exactly what failed and why. This story ensures every failure scenario is handled deliberately, not as an afterthought.

---

## Tasks

### Task 1: Define Custom Exception Classes

**Goal:** Create specific exceptions for common failure scenarios

**Subtasks:**
- [ ] Create file: `backend/app/exceptions.py`
- [ ] Define base exception:
  ```python
  class OrchestratorError(Exception):
      """Base exception for orchestrator errors"""

      def __init__(self, message: str, details: str = None):
          self.message = message
          self.details = details or ""
          super().__init__(self.message)
  ```
- [ ] Define specific exceptions:
  ```python
  class ParameterExtractionError(OrchestratorError):
      """Raised when parameter extraction fails or is incomplete"""

      def __init__(self, message: str, missing_params: list = None):
          super().__init__(message)
          self.missing_params = missing_params or []

  class DataNotFoundError(OrchestratorError):
      """Raised when required historical data is not found"""
      pass

  class DataValidationError(OrchestratorError):
      """Raised when data doesn't meet quality requirements"""
      pass

  class AgentTimeoutError(OrchestratorError):
      """Raised when agent exceeds execution timeout"""

      def __init__(self, agent_name: str, timeout: int):
          message = f"Agent '{agent_name}' timed out after {timeout} seconds"
          super().__init__(message)
          self.agent_name = agent_name
          self.timeout = timeout

  class AgentExecutionError(OrchestratorError):
      """Raised when agent execution fails"""

      def __init__(self, agent_name: str, original_error: Exception):
          message = f"Agent '{agent_name}' execution failed"
          super().__init__(message, details=str(original_error))
          self.agent_name = agent_name
          self.original_error = original_error

  class ExternalServiceError(OrchestratorError):
      """Raised when external service (Azure OpenAI, etc.) fails"""

      def __init__(self, service: str, details: str):
          message = f"External service '{service}' is unavailable"
          super().__init__(message, details=details)
          self.service = service
  ```
- [ ] Test exception creation and attributes

---

### Task 2: Create Standardized Error Response Schema

**Goal:** Define consistent error response format

**Subtasks:**
- [ ] Add to `backend/app/schemas/responses.py`:
  ```python
  from pydantic import BaseModel, Field
  from typing import Optional, Dict, Any

  class ErrorResponse(BaseModel):
      """
      Standardized error response format

      All API errors return this structure for consistency
      """
      error: str = Field(..., description="Error type or category")
      message: str = Field(..., description="User-friendly error message")
      details: Optional[str] = Field(None, description="Additional context")
      request_id: Optional[str] = Field(None, description="Request ID for debugging")
      suggestions: Optional[list[str]] = Field(
          None,
          description="Actionable suggestions for fixing the error"
      )

      class Config:
          json_schema_extra = {
              "example": {
                  "error": "DataNotFoundError",
                  "message": "Historical sales data not found for category CAT001",
                  "details": "File not found: data/historical_sales.csv",
                  "request_id": "req_a3f8b2c1",
                  "suggestions": [
                      "Ensure Phase 1 CSV file exists in the data directory",
                      "Check DATA_DIR environment variable is set correctly"
                  ]
              }
          }
  ```
- [ ] Test schema validation

---

### Task 3: Implement FastAPI Exception Handlers

**Goal:** Catch exceptions and convert to HTTP responses

**Subtasks:**
- [ ] Create file: `backend/app/core/exception_handlers.py`
- [ ] Import dependencies:
  ```python
  from fastapi import Request, status
  from fastapi.responses import JSONResponse
  from app.exceptions import *
  from app.schemas.responses import ErrorResponse
  import logging

  logger = logging.getLogger(__name__)
  ```
- [ ] Implement handler for ParameterExtractionError:
  ```python
  async def parameter_extraction_error_handler(
      request: Request,
      exc: ParameterExtractionError
  ) -> JSONResponse:
      """
      Handle parameter extraction failures

      Returns 400 Bad Request with missing parameter details
      """
      request_id = request.state.request_id if hasattr(request.state, "request_id") else None

      logger.error(
          f"Parameter extraction failed: {exc.message}",
          extra={"request_id": request_id, "missing_params": exc.missing_params}
      )

      error_response = ErrorResponse(
          error="ParameterExtractionError",
          message=exc.message,
          details=f"Missing parameters: {', '.join(exc.missing_params)}" if exc.missing_params else None,
          request_id=request_id,
          suggestions=[
              "Provide more details in your strategy description",
              "Specify all required parameters: forecast horizon, start date, replenishment strategy, holdback percentage"
          ]
      )

      return JSONResponse(
          status_code=status.HTTP_400_BAD_REQUEST,
          content=error_response.dict()
      )
  ```
- [ ] Implement handler for DataNotFoundError:
  ```python
  async def data_not_found_error_handler(
      request: Request,
      exc: DataNotFoundError
  ) -> JSONResponse:
      """
      Handle missing historical data

      Returns 404 Not Found
      """
      request_id = request.state.request_id if hasattr(request.state, "request_id") else None

      logger.error(
          f"Data not found: {exc.message}",
          extra={"request_id": request_id}
      )

      error_response = ErrorResponse(
          error="DataNotFoundError",
          message=exc.message,
          details=exc.details,
          request_id=request_id,
          suggestions=[
              "Verify Phase 1 CSV files exist in data directory",
              "Check DATA_DIR environment variable",
              "Ensure category ID is valid"
          ]
      )

      return JSONResponse(
          status_code=status.HTTP_404_NOT_FOUND,
          content=error_response.dict()
      )
  ```
- [ ] Implement handler for AgentTimeoutError:
  ```python
  async def agent_timeout_error_handler(
      request: Request,
      exc: AgentTimeoutError
  ) -> JSONResponse:
      """
      Handle agent timeout

      Returns 503 Service Unavailable with retry suggestion
      """
      request_id = request.state.request_id if hasattr(request.state, "request_id") else None

      logger.error(
          f"Agent timeout: {exc.agent_name} exceeded {exc.timeout}s",
          extra={"request_id": request_id, "agent": exc.agent_name, "timeout": exc.timeout}
      )

      error_response = ErrorResponse(
          error="AgentTimeoutError",
          message=f"Forecast generation timed out",
          details=f"Agent '{exc.agent_name}' exceeded {exc.timeout} second timeout",
          request_id=request_id,
          suggestions=[
              "Retry the request - this is usually a temporary issue",
              "Reduce forecast horizon if possible",
              "Contact support if timeouts persist"
          ]
      )

      return JSONResponse(
          status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
          content=error_response.dict()
      )
  ```
- [ ] Implement handler for ExternalServiceError:
  ```python
  async def external_service_error_handler(
      request: Request,
      exc: ExternalServiceError
  ) -> JSONResponse:
      """
      Handle external service failures (Azure OpenAI, etc.)

      Returns 503 Service Unavailable

      IMPORTANT: Don't expose API keys or credentials in error messages
      """
      request_id = request.state.request_id if hasattr(request.state, "request_id") else None

      # Log full details internally
      logger.error(
          f"External service error: {exc.service}",
          extra={
              "request_id": request_id,
              "service": exc.service,
              "details": exc.details  # Full details logged, not exposed to user
          }
      )

      # Sanitized message for user
      error_response = ErrorResponse(
          error="ExternalServiceError",
          message=f"External service temporarily unavailable",
          details=f"Service: {exc.service}",  # Don't include exc.details (may contain sensitive info)
          request_id=request_id,
          suggestions=[
              "Retry in a few moments",
              "Check service status page if issue persists",
              "Contact support with request ID if problem continues"
          ]
      )

      return JSONResponse(
          status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
          content=error_response.dict()
      )
  ```
- [ ] Implement catch-all handler:
  ```python
  async def general_exception_handler(
      request: Request,
      exc: Exception
  ) -> JSONResponse:
      """
      Catch-all for unexpected exceptions

      Returns 500 Internal Server Error

      Logs full stack trace but returns generic message to user
      """
      request_id = request.state.request_id if hasattr(request.state, "request_id") else None

      logger.exception(
          f"Unexpected error: {str(exc)}",
          extra={"request_id": request_id},
          exc_info=True  # Include full stack trace
      )

      error_response = ErrorResponse(
          error="InternalServerError",
          message="An unexpected error occurred",
          details=None,  # Don't expose internal details
          request_id=request_id,
          suggestions=[
              "Retry the request",
              "Contact support with request ID if problem persists"
          ]
      )

      return JSONResponse(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          content=error_response.dict()
      )
  ```

---

### Task 4: Register Exception Handlers in FastAPI

**Goal:** Wire up exception handlers to FastAPI app

**Subtasks:**
- [ ] Update `backend/app/main.py`:
  ```python
  from app.core.exception_handlers import (
      parameter_extraction_error_handler,
      data_not_found_error_handler,
      agent_timeout_error_handler,
      external_service_error_handler,
      general_exception_handler
  )
  from app.exceptions import (
      ParameterExtractionError,
      DataNotFoundError,
      AgentTimeoutError,
      ExternalServiceError
  )

  # Register exception handlers
  app.add_exception_handler(ParameterExtractionError, parameter_extraction_error_handler)
  app.add_exception_handler(DataNotFoundError, data_not_found_error_handler)
  app.add_exception_handler(AgentTimeoutError, agent_timeout_error_handler)
  app.add_exception_handler(ExternalServiceError, external_service_error_handler)
  app.add_exception_handler(Exception, general_exception_handler)  # Catch-all
  ```
- [ ] Test that exceptions trigger handlers

---

### Task 5: Add Request ID Middleware

**Goal:** Add unique request IDs for tracing errors

**Subtasks:**
- [ ] Create file: `backend/app/middleware/request_id.py`:
  ```python
  from starlette.middleware.base import BaseHTTPMiddleware
  from starlette.requests import Request
  import uuid

  class RequestIDMiddleware(BaseHTTPMiddleware):
      """
      Add unique request ID to every request for tracing

      Request ID is:
      - Added to request.state.request_id
      - Added to response headers as X-Request-ID
      - Logged with every log message
      """

      async def dispatch(self, request: Request, call_next):
          # Generate unique request ID
          request_id = str(uuid.uuid4())
          request.state.request_id = request_id

          # Process request
          response = await call_next(request)

          # Add request ID to response headers
          response.headers["X-Request-ID"] = request_id

          return response
  ```
- [ ] Register middleware in `main.py`:
  ```python
  from app.middleware.request_id import RequestIDMiddleware

  app.add_middleware(RequestIDMiddleware)
  ```
- [ ] Test request ID appears in responses and logs

---

### Task 6: Enhance WebSocket Error Notifications

**Goal:** Send error messages via WebSocket when workflow fails

**Subtasks:**
- [ ] Update AgentHandoffManager error handling (already added in Task 4 of Story 5.3):
  ```python
  # In call_agent() method
  except Exception as e:
      status = "failed"

      # Send WebSocket error
      if session_id:
          await self._send_agent_error(agent_name, session_id, str(e))

      # Wrap in AgentExecutionError
      raise AgentExecutionError(agent_name, e) from e
  ```
- [ ] Update orchestrator workflow error handling:
  ```python
  @router.post("/run-workflow")
  async def run_workflow(...):
      try:
          # ... workflow steps

      except ParameterExtractionError as e:
          await connection_manager.send_message(
              session_id,
              ErrorMessage(
                  session_id=session_id,
                  error="Parameter extraction failed",
                  details=e.message
              )
          )
          raise  # Re-raise to trigger FastAPI exception handler

      except DataNotFoundError as e:
          await connection_manager.send_message(
              session_id,
              ErrorMessage(
                  session_id=session_id,
                  error="Historical data not found",
                  details=e.message
              )
          )
          raise

      except Exception as e:
          await connection_manager.send_message(
              session_id,
              ErrorMessage(
                  session_id=session_id,
                  error="Workflow failed",
                  details=str(e)
              )
          )
          raise
  ```
- [ ] Test WebSocket error notifications

---

### Task 7: Add Logging Configuration

**Goal:** Configure structured logging with proper levels

**Subtasks:**
- [ ] Create file: `backend/app/core/logging_config.py`:
  ```python
  import logging
  import sys

  def setup_logging():
      """
      Configure application logging

      Logs to stdout with structured format including request IDs
      """
      logging.basicConfig(
          level=logging.INFO,
          format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
          handlers=[
              logging.StreamHandler(sys.stdout)
          ]
      )

      # Set specific log levels
      logging.getLogger("uvicorn").setLevel(logging.WARNING)
      logging.getLogger("fastapi").setLevel(logging.INFO)
      logging.getLogger("app").setLevel(logging.DEBUG)  # Our app logs
  ```
- [ ] Call from `main.py`:
  ```python
  from app.core.logging_config import setup_logging

  setup_logging()
  ```
- [ ] Test logging output includes timestamps and levels

---

### Task 8: Write Tests

**Goal:** Test error handling scenarios

**Subtasks:**
- [ ] Create file: `backend/tests/test_error_handling.py`
- [ ] **Test 1:** Parameter extraction error
  ```python
  def test_parameter_extraction_error_handler(client):
      # Mock parameter extraction to fail
      response = client.post(
          "/api/orchestrator/extract-parameters",
          json={"strategy_description": "incomplete"}  # Will fail
      )

      assert response.status_code == 400
      data = response.json()
      assert data["error"] == "ParameterExtractionError"
      assert "request_id" in data
      assert len(data["suggestions"]) > 0
  ```
- [ ] **Test 2:** Data not found error
  ```python
  @pytest.mark.asyncio
  async def test_data_not_found_error():
      from app.orchestrator.context_assembler import ContextAssembler

      assembler = ContextAssembler()

      with pytest.raises(DataNotFoundError):
          await assembler.assemble_demand_context(params, "INVALID_CATEGORY")
  ```
- [ ] **Test 3:** Agent timeout error
  ```python
  @pytest.mark.asyncio
  async def test_agent_timeout_error():
      async def slow_agent(ctx):
          await asyncio.sleep(10)

      manager = AgentHandoffManager()
      manager.register_agent("slow", slow_agent)

      with pytest.raises(AgentTimeoutError) as exc_info:
          await manager.call_agent("slow", {}, timeout=1)

      assert exc_info.value.agent_name == "slow"
      assert exc_info.value.timeout == 1
  ```
- [ ] **Test 4:** Request ID in error response
  ```python
  def test_request_id_in_error(client):
      response = client.post("/api/orchestrator/invalid-endpoint")

      assert "X-Request-ID" in response.headers
      request_id = response.headers["X-Request-ID"]
      assert len(request_id) == 36  # UUID length
  ```
- [ ] Run tests: `uv run pytest backend/tests/test_error_handling.py -v`

---

## Implementation Notes

**Error Logging Example:**
```python
logger.error(
    "Agent execution failed",
    extra={
        "request_id": "req_a3f8b2c1",
        "agent_name": "demand",
        "error_type": "TimeoutError",
        "timeout_seconds": 30
    }
)
```

**Testing Error Scenarios:**
```python
# Deliberately trigger errors for testing
@router.get("/test/trigger-error")
async def trigger_error(error_type: str):
    if error_type == "parameter":
        raise ParameterExtractionError("Test error", missing_params=["forecast_horizon_weeks"])
    elif error_type == "data":
        raise DataNotFoundError("Test data not found")
    elif error_type == "timeout":
        raise AgentTimeoutError("demand", 30)
    else:
        raise Exception("Unknown error type")
```

---

## Definition of Done

- [ ] Custom exception classes defined for all failure scenarios
- [ ] ErrorResponse schema defined with consistent structure
- [ ] FastAPI exception handlers implemented for all custom exceptions
- [ ] Exception handlers registered in main FastAPI app
- [ ] Request ID middleware implemented and registered
- [ ] WebSocket error notifications working
- [ ] Logging configuration set up with proper levels
- [ ] All error responses include request IDs
- [ ] Sensitive data (API keys, stack traces) not exposed to users
- [ ] Unit tests for exception handlers
- [ ] Integration tests with deliberate failures
- [ ] Error messages are user-friendly and actionable
- [ ] Code reviewed and merged

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
