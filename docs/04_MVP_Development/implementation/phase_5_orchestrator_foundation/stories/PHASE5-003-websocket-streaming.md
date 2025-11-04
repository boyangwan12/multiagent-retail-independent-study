# Story: Implement WebSocket Real-Time Progress Streaming

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-003
**Status:** Ready for Implementation
**Estimate:** 6 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE5-001, PHASE5-002

**Planning References:**
- PRD v3.3: Section 3.2 (Real-Time Workflow Execution & Transparency)
- Technical Architecture v3.3: Section 4.3 (WebSocket Architecture & Real-Time Communication)
- Product Brief v3.3: Section 2.3 (User Experience - Live Updates)

---

## Story

As a backend developer,
I want to stream agent execution progress to frontend via WebSocket,
So that users see real-time updates as the Orchestrator runs the forecasting workflow.

**Business Value:** Real-time visibility is critical for user trust and engagement. Without WebSocket updates, the 10-30 second forecasting workflow feels like a black box, creating anxiety and uncertainty. Live status messages ("Running Prophet forecast: 8,200 units") transform the experience from opaque to transparent, showing users exactly what the AI agents are doing and building confidence in the system's capabilities.

**Epic Context:** This is Story 3 of 6 in Phase 5 (Orchestrator Foundation). It integrates with Story 5.2's AgentHandoffManager to broadcast execution progress. This WebSocket infrastructure will be reused in Phase 6-8 as we add real agents. Frontend Phase 4 already has WebSocket client code - this story completes the backend half.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ WebSocket endpoint created at `/ws/orchestrator/{session_id}`
2. ✅ Frontend client can establish WebSocket connection
3. ✅ Connection accepts `session_id` parameter for routing messages to correct client
4. ✅ Server sends 5 message types: `agent_status`, `progress`, `complete`, `error`, `heartbeat`
5. ✅ Message format is consistent JSON structure with required fields
6. ✅ Progress updates sent during agent execution (0-100%)
7. ✅ Integration with AgentHandoffManager to trigger updates automatically
8. ✅ Multiple concurrent connections supported (different users/sessions)
9. ✅ Connection close handled gracefully on workflow completion
10. ✅ Auto-reconnect supported (frontend can reconnect if dropped)

### Quality Requirements

11. ✅ Message latency <100ms from event to frontend receipt
12. ✅ Heartbeat ping/pong every 30 seconds to keep connection alive
13. ✅ No memory leaks from unclosed connections
14. ✅ Error messages don't expose sensitive backend details
15. ✅ Connection manager tracks active connections for monitoring
16. ✅ Unit tests for message formatting and connection handling
17. ✅ Integration test with real WebSocket client

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Story Dependencies:**
- [x] PHASE5-001 (Parameter Extraction) complete
- [x] PHASE5-002 (Agent Handoff Framework) complete
- [x] AgentHandoffManager class exists

**FastAPI WebSocket Setup:**
- [ ] FastAPI installed with WebSocket support
- [ ] `websockets` library available (comes with FastAPI)
- [ ] CORS configured to allow WebSocket connections from frontend origin

**Frontend Integration:**
- [x] Phase 4 frontend has WebSocket client code
- [x] Frontend expects messages at `/ws/orchestrator/{session_id}`

**Why This Matters:**
WebSocket connections are stateful and require careful connection management. If not implemented correctly, connections can leak memory or clients won't receive updates. This is also the first real-time communication channel - getting it right establishes patterns for future features.

---

## Tasks

### Task 1: Define WebSocket Message Schemas

**Goal:** Create consistent message format for all WebSocket communications

**Subtasks:**
- [ ] Create file: `backend/app/schemas/websocket_messages.py`
- [ ] Define `WebSocketMessageType` enum:
  ```python
  from enum import Enum

  class WebSocketMessageType(str, Enum):
      AGENT_STATUS = "agent_status"
      PROGRESS = "progress"
      COMPLETE = "complete"
      ERROR = "error"
      HEARTBEAT = "heartbeat"
  ```
- [ ] Define base message schema:
  ```python
  from pydantic import BaseModel, Field
  from datetime import datetime

  class WebSocketMessage(BaseModel):
      type: WebSocketMessageType
      timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
      session_id: str

      class Config:
          use_enum_values = True
  ```
- [ ] Define specific message schemas:
  ```python
  class AgentStatusMessage(WebSocketMessage):
      type: WebSocketMessageType = WebSocketMessageType.AGENT_STATUS
      agent: str = Field(..., description="Agent name (demand, inventory, pricing)")
      status: str = Field(..., description="Human-readable status text")
      progress: int = Field(..., ge=0, le=100, description="Percentage complete")
      data: dict = Field(default_factory=dict, description="Optional payload")

  class ProgressMessage(WebSocketMessage):
      type: WebSocketMessageType = WebSocketMessageType.PROGRESS
      agent: str
      status: str
      progress: int = Field(..., ge=0, le=100)
      data: dict = Field(default_factory=dict)

  class CompleteMessage(WebSocketMessage):
      type: WebSocketMessageType = WebSocketMessageType.COMPLETE
      agent: str
      status: str = "Complete"
      progress: int = 100
      data: dict

  class ErrorMessage(WebSocketMessage):
      type: WebSocketMessageType = WebSocketMessageType.ERROR
      error: str = Field(..., description="User-friendly error message")
      details: str = Field(default="", description="Additional error context")

  class HeartbeatMessage(WebSocketMessage):
      type: WebSocketMessageType = WebSocketMessageType.HEARTBEAT
      message: str = "ping"
  ```
- [ ] Test schema validation and JSON serialization

---

### Task 2: Create WebSocket Connection Manager

**Goal:** Manage multiple concurrent WebSocket connections

**Subtasks:**
- [ ] Create file: `backend/app/orchestrator/websocket_manager.py`
- [ ] Implement `ConnectionManager` class:
  ```python
  from fastapi import WebSocket
  from typing import Dict
  import asyncio
  import logging

  class ConnectionManager:
      """
      Manages WebSocket connections for real-time progress updates

      Attributes:
          active_connections: Dict mapping session_id to WebSocket
          logger: Python logger
      """

      def __init__(self):
          self.active_connections: Dict[str, WebSocket] = {}
          self.logger = logging.getLogger(__name__)

      async def connect(self, session_id: str, websocket: WebSocket):
          """
          Accept and register new WebSocket connection

          Args:
              session_id: Unique session identifier
              websocket: FastAPI WebSocket instance
          """
          await websocket.accept()
          self.active_connections[session_id] = websocket
          self.logger.info(f"WebSocket connected: {session_id}")

      def disconnect(self, session_id: str):
          """
          Remove connection from active pool

          Args:
              session_id: Session identifier to disconnect
          """
          if session_id in self.active_connections:
              del self.active_connections[session_id]
              self.logger.info(f"WebSocket disconnected: {session_id}")

      async def send_message(self, session_id: str, message: WebSocketMessage):
          """
          Send message to specific session

          Args:
              session_id: Target session
              message: Message object (will be serialized to JSON)
          """
          if session_id in self.active_connections:
              websocket = self.active_connections[session_id]
              try:
                  await websocket.send_json(message.dict())
              except Exception as e:
                  self.logger.error(f"Failed to send message to {session_id}: {e}")
                  self.disconnect(session_id)

      async def broadcast(self, message: WebSocketMessage):
          """
          Broadcast message to all connected clients

          Args:
              message: Message object to broadcast
          """
          for session_id in list(self.active_connections.keys()):
              await self.send_message(session_id, message)

      def get_connection_count(self) -> int:
          """Return number of active connections"""
          return len(self.active_connections)
  ```
- [ ] Create singleton instance:
  ```python
  # Global connection manager instance
  connection_manager = ConnectionManager()
  ```
- [ ] Test connection management (connect, disconnect, send)

---

### Task 3: Implement WebSocket Endpoint

**Goal:** Create FastAPI WebSocket endpoint for client connections

**Subtasks:**
- [ ] Create file: `backend/app/routers/websocket.py`
- [ ] Import dependencies:
  ```python
  from fastapi import APIRouter, WebSocket, WebSocketDisconnect
  from app.orchestrator.websocket_manager import connection_manager
  from app.schemas.websocket_messages import HeartbeatMessage
  import asyncio
  ```
- [ ] Create router:
  ```python
  router = APIRouter(prefix="/ws", tags=["websocket"])
  ```
- [ ] Implement WebSocket endpoint:
  ```python
  @router.websocket("/orchestrator/{session_id}")
  async def websocket_orchestrator(websocket: WebSocket, session_id: str):
      """
      WebSocket endpoint for real-time orchestrator progress updates

      Args:
          websocket: FastAPI WebSocket connection
          session_id: Unique session identifier for routing messages

      Message Flow:
          1. Client connects with session_id
          2. Server sends heartbeat every 30s to keep connection alive
          3. Orchestrator sends progress updates during workflow execution
          4. Connection closes when workflow completes or client disconnects
      """
      await connection_manager.connect(session_id, websocket)

      try:
          # Start heartbeat task
          heartbeat_task = asyncio.create_task(
              send_heartbeat(session_id)
          )

          # Keep connection alive and listen for client messages
          while True:
              # Wait for client message (or disconnect)
              data = await websocket.receive_text()

              # Echo back or handle client messages if needed
              # (For Phase 5, we only send server -> client, no client -> server)

      except WebSocketDisconnect:
          connection_manager.disconnect(session_id)
          heartbeat_task.cancel()

      except Exception as e:
          connection_manager.logger.error(f"WebSocket error for {session_id}: {e}")
          connection_manager.disconnect(session_id)
          heartbeat_task.cancel()
  ```
- [ ] Implement heartbeat function:
  ```python
  async def send_heartbeat(session_id: str):
      """
      Send periodic heartbeat to keep connection alive

      Args:
          session_id: Target session for heartbeat
      """
      while True:
          await asyncio.sleep(30)  # Every 30 seconds

          heartbeat = HeartbeatMessage(session_id=session_id)
          await connection_manager.send_message(session_id, heartbeat)
  ```
- [ ] Register router in `backend/app/main.py`:
  ```python
  from app.routers import websocket
  app.include_router(websocket.router)
  ```
- [ ] Test WebSocket connection with simple client

---

### Task 4: Integrate WebSocket with AgentHandoffManager

**Goal:** Automatically send progress updates during agent execution

**Subtasks:**
- [ ] Modify `AgentHandoffManager.call_agent()` to accept optional `session_id`:
  ```python
  async def call_agent(
      self,
      agent_name: str,
      context: T,
      timeout: int = 30,
      session_id: str = None  # NEW PARAMETER
  ) -> R:
      """
      Execute agent with context and optional WebSocket updates

      Args:
          agent_name: Name of agent to call
          context: Input context
          timeout: Max execution time
          session_id: Optional session ID for WebSocket updates
      """
      if agent_name not in self._agents:
          raise ValueError(f"Agent '{agent_name}' not registered")

      handler = self._agents[agent_name]
      start_time = time.time()

      # Send "started" message
      if session_id:
          await self._send_agent_started(agent_name, session_id)

      self.logger.info(f"Calling agent '{agent_name}'")

      try:
          result = await asyncio.wait_for(
              handler(context),
              timeout=timeout
          )
          status = "success"

          # Send "completed" message
          if session_id:
              await self._send_agent_completed(agent_name, session_id, result)

          self.logger.info(f"Agent '{agent_name}' completed successfully")

      except asyncio.TimeoutError:
          status = "timeout"

          # Send "error" message
          if session_id:
              await self._send_agent_error(
                  agent_name,
                  session_id,
                  f"Agent '{agent_name}' timed out after {timeout}s"
              )

          self.logger.error(f"Agent '{agent_name}' timed out after {timeout}s")
          raise

      except Exception as e:
          status = "failed"

          # Send "error" message
          if session_id:
              await self._send_agent_error(agent_name, session_id, str(e))

          self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
          raise

      finally:
          duration = time.time() - start_time
          self._log_execution(agent_name, start_time, duration, status)

      return result
  ```
- [ ] Add WebSocket helper methods to AgentHandoffManager:
  ```python
  async def _send_agent_started(self, agent_name: str, session_id: str):
      """Send agent started message via WebSocket"""
      from app.orchestrator.websocket_manager import connection_manager
      from app.schemas.websocket_messages import AgentStatusMessage

      message = AgentStatusMessage(
          session_id=session_id,
          agent=agent_name,
          status=f"Starting {agent_name} agent...",
          progress=0
      )
      await connection_manager.send_message(session_id, message)

  async def _send_agent_completed(self, agent_name: str, session_id: str, result: Any):
      """Send agent completed message via WebSocket"""
      from app.orchestrator.websocket_manager import connection_manager
      from app.schemas.websocket_messages import CompleteMessage

      message = CompleteMessage(
          session_id=session_id,
          agent=agent_name,
          data={"result_summary": str(result)[:200]}  # Truncate for message size
      )
      await connection_manager.send_message(session_id, message)

  async def _send_agent_error(self, agent_name: str, session_id: str, error: str):
      """Send agent error message via WebSocket"""
      from app.orchestrator.websocket_manager import connection_manager
      from app.schemas.websocket_messages import ErrorMessage

      message = ErrorMessage(
          session_id=session_id,
          error=f"Agent '{agent_name}' failed",
          details=error
      )
      await connection_manager.send_message(session_id, message)
  ```
- [ ] Test integration: Call agent with session_id and verify messages sent

---

### Task 5: Create Orchestrator Workflow Endpoint

**Goal:** Create main endpoint that runs parameter extraction + agent execution with WebSocket updates

**Subtasks:**
- [ ] Add endpoint to `backend/app/routers/orchestrator.py`:
  ```python
  @router.post("/run-workflow")
  async def run_workflow(
      strategy_description: str,
      session_id: str,
      openai_client: Any = Depends(get_openai_client)
  ):
      """
      Run complete orchestrator workflow with real-time WebSocket updates

      Args:
          strategy_description: User's natural language strategy
          session_id: WebSocket session ID for progress updates
          openai_client: Azure OpenAI client

      Returns:
          Workflow result with forecast data
      """
      from app.orchestrator.agent_handoff import handoff_manager
      from app.orchestrator.websocket_manager import connection_manager
      from app.schemas.websocket_messages import ProgressMessage

      try:
          # Step 1: Extract parameters
          await connection_manager.send_message(
              session_id,
              ProgressMessage(
                  session_id=session_id,
                  agent="orchestrator",
                  status="Extracting parameters from your strategy...",
                  progress=10
              )
          )

          parameters = await extract_parameters_from_text(
              strategy_description,
              openai_client
          )

          # Step 2: Call Demand Agent (mock for Phase 5)
          await connection_manager.send_message(
              session_id,
              ProgressMessage(
                  session_id=session_id,
                  agent="orchestrator",
                  status="Calling Demand Agent for forecast...",
                  progress=30
              )
          )

          forecast = await handoff_manager.call_agent(
              "demand",
              parameters,
              session_id=session_id  # Enable WebSocket updates
          )

          # Step 3: Complete
          await connection_manager.send_message(
              session_id,
              CompleteMessage(
                  session_id=session_id,
                  agent="orchestrator",
                  data={"forecast": forecast}
              )
          )

          return {"status": "success", "forecast": forecast}

      except Exception as e:
          await connection_manager.send_message(
              session_id,
              ErrorMessage(
                  session_id=session_id,
                  error="Workflow failed",
                  details=str(e)
              )
          )
          raise HTTPException(status_code=500, detail=str(e))
  ```
- [ ] Test endpoint with Postman + WebSocket client simultaneously

---

### Task 6: Write Tests

**Goal:** Ensure WebSocket functionality works correctly

**Subtasks:**
- [ ] Create file: `backend/tests/test_websocket.py`
- [ ] **Test 1:** Connection manager add/remove
  ```python
  def test_connection_manager():
      from app.orchestrator.websocket_manager import ConnectionManager

      manager = ConnectionManager()
      assert manager.get_connection_count() == 0

      # Simulate connection (in real test use actual WebSocket)
      manager.active_connections["test_session"] = "mock_websocket"
      assert manager.get_connection_count() == 1

      manager.disconnect("test_session")
      assert manager.get_connection_count() == 0
  ```
- [ ] **Test 2:** Message schema validation
  ```python
  def test_message_schemas():
      from app.schemas.websocket_messages import AgentStatusMessage

      message = AgentStatusMessage(
          session_id="test123",
          agent="demand",
          status="Running forecast",
          progress=50
      )

      # Should serialize to JSON
      json_data = message.dict()
      assert json_data["type"] == "agent_status"
      assert json_data["agent"] == "demand"
      assert json_data["progress"] == 50
  ```
- [ ] **Test 3:** WebSocket integration with agent execution
  ```python
  @pytest.mark.asyncio
  async def test_websocket_integration():
      # This test requires actual WebSocket client
      # Use pytest-asyncio + websockets library

      from websockets import connect

      async with connect("ws://localhost:8000/ws/orchestrator/test123") as ws:
          # Trigger workflow in background
          asyncio.create_task(run_test_workflow("test123"))

          # Listen for messages
          messages = []
          async for message in ws:
              data = json.loads(message)
              messages.append(data)

              if data["type"] == "complete":
                  break

          # Verify received expected messages
          assert len(messages) > 0
          assert any(m["type"] == "agent_status" for m in messages)
  ```
- [ ] Run tests: `uv run pytest backend/tests/test_websocket.py -v`

---

## Implementation Notes

**Frontend Integration Example:**
```typescript
// Frontend connects to WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws/orchestrator/${sessionId}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case "agent_status":
      updateAgentCard(message.agent, message.status, message.progress);
      break;
    case "progress":
      updateProgressBar(message.progress);
      break;
    case "complete":
      showResults(message.data);
      break;
    case "error":
      showError(message.error);
      break;
    case "heartbeat":
      // Connection alive
      break;
  }
};
```

**Session ID Generation:**
```python
import uuid

session_id = str(uuid.uuid4())  # e.g., "a3f8b2c1-..."
```

**CORS Configuration for WebSocket:**
```python
# In backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Definition of Done

- [ ] WebSocket message schemas defined (5 types)
- [ ] ConnectionManager class created with connect/disconnect/send_message
- [ ] WebSocket endpoint `/ws/orchestrator/{session_id}` implemented
- [ ] Heartbeat mechanism implemented (30s intervals)
- [ ] AgentHandoffManager integrated with WebSocket updates
- [ ] Orchestrator workflow endpoint created with progress updates
- [ ] Multiple concurrent connections supported
- [ ] Unit tests for connection management and message schemas
- [ ] Integration test with real WebSocket client
- [ ] Frontend can connect and receive messages
- [ ] No memory leaks from unclosed connections
- [ ] Code reviewed and merged

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
