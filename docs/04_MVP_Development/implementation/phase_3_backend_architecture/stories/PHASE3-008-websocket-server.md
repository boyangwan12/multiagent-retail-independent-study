# Story: WebSocket Server for Real-Time Agent Updates

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-008
**Status:** Ready for Review
**Estimate:** 4 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-004 (FastAPI Setup), PHASE3-007 (Workflow Orchestration)

---

## Story

As a backend developer,
I want to implement a WebSocket server that streams real-time agent progress updates to the frontend,
So that users can see live workflow status instead of polling, providing transparency and reducing perceived wait time.

**Business Value:** Real-time updates are **critical for user experience**. Without WebSockets, the frontend must poll the status endpoint every 2-5 seconds, causing network overhead and delayed updates. WebSocket streaming provides instant feedback as agents execute, making the 60-second workflow feel responsive and transparent. This directly supports PRD requirements FR-7.1, FR-7.2 (agent progress cards), and NFR-1.5 (WebSocket latency <100ms).

**Epic Context:** This is Task 8 of 14 in Phase 3. It builds on FastAPI setup (PHASE3-004) and workflow orchestration (PHASE3-007) to add real-time communication. The WebSocket server enables frontend Section 1 (agent progress cards), Section 4 (variance monitoring), and Section 6 (markdown workflow updates). Phase 8 (Orchestrator Agent) will broadcast messages through this WebSocket infrastructure.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ WebSocket endpoint created at `WS /api/workflows/{workflow_id}/stream`
2. ✅ Connection manager handles multiple concurrent connections (one per user)
3. ✅ Connection lifecycle managed (connect, disconnect, heartbeat ping/pong)
4. ✅ 6 message types implemented with Pydantic schemas: `agent_started`, `agent_progress`, `agent_completed`, `human_input_required`, `workflow_complete`, `error`
5. ✅ Message broadcasting sends updates to all connected clients for a workflow
6. ✅ Heartbeat keepalive sends ping every 30 seconds, expects pong response
7. ✅ Graceful disconnection cleanup (remove from connection manager)

### Quality Requirements

8. ✅ All message schemas validate with Pydantic (type safety)
9. ✅ WebSocket connection errors logged with meaningful messages
10. ✅ Connection manager thread-safe (async/await pattern)
11. ✅ Message latency <100ms (measured from send to receive)
12. ✅ OpenAPI documentation includes WebSocket endpoint (FastAPI supports /docs WebSocket display)

---

## Tasks

### Task 1: Create WebSocket Message Schemas

Create Pydantic models for all 6 WebSocket message types.

**File:** `backend/app/schemas/websocket.py`

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Any
from datetime import datetime


class AgentStartedMessage(BaseModel):
    """Message sent when agent begins execution."""

    type: Literal["agent_started"] = "agent_started"
    agent: str = Field(..., description="Agent name (e.g., 'Demand Agent', 'Inventory Agent', 'Pricing Agent')")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "agent_started",
                "agent": "Demand Agent",
                "timestamp": "2025-10-12T10:30:15Z"
            }
        }
    )


class AgentProgressMessage(BaseModel):
    """Message sent during agent execution (line-by-line updates)."""

    type: Literal["agent_progress"] = "agent_progress"
    agent: str = Field(..., description="Agent name")
    message: str = Field(..., description="Progress message (e.g., 'Running Prophet forecasting model...')")
    progress_pct: int = Field(..., ge=0, le=100, description="Overall workflow progress (0-100)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "agent_progress",
                "agent": "Demand Agent",
                "message": "Running Prophet forecasting model...",
                "progress_pct": 33,
                "timestamp": "2025-10-12T10:30:20Z"
            }
        }
    )


class AgentCompletedMessage(BaseModel):
    """Message sent when agent finishes execution."""

    type: Literal["agent_completed"] = "agent_completed"
    agent: str = Field(..., description="Agent name")
    duration_seconds: float = Field(..., description="Agent execution time in seconds")
    result: Optional[dict] = Field(None, description="Agent output (optional)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "agent_completed",
                "agent": "Demand Agent",
                "duration_seconds": 15.3,
                "result": {
                    "total_season_demand": 8000,
                    "prophet_forecast": 8200,
                    "arima_forecast": 7800
                },
                "timestamp": "2025-10-12T10:30:30Z"
            }
        }
    )


class HumanInputRequiredMessage(BaseModel):
    """Message sent when agent needs human approval."""

    type: Literal["human_input_required"] = "human_input_required"
    agent: str = Field(..., description="Agent name")
    action: str = Field(..., description="Action identifier (e.g., 'approve_manufacturing_order', 'approve_markdown')")
    data: dict = Field(..., description="Data for approval modal")
    options: list[str] = Field(..., description="Available actions (e.g., ['modify', 'accept'])")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "human_input_required",
                "agent": "Inventory Agent",
                "action": "approve_manufacturing_order",
                "data": {
                    "manufacturing_qty": 9600,
                    "initial_allocation": 5280,
                    "holdback": 4320,
                    "safety_stock_pct": 0.20
                },
                "options": ["modify", "accept"],
                "timestamp": "2025-10-12T10:30:45Z"
            }
        }
    )


class WorkflowCompleteMessage(BaseModel):
    """Message sent when entire workflow finishes."""

    type: Literal["workflow_complete"] = "workflow_complete"
    workflow_id: str = Field(..., description="Workflow identifier")
    duration_seconds: float = Field(..., description="Total workflow execution time")
    result: dict = Field(..., description="Final workflow results")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "workflow_complete",
                "workflow_id": "wf_abc123",
                "duration_seconds": 58.7,
                "result": {
                    "forecast_id": "f_spring_2025",
                    "allocation_id": "a_spring_2025",
                    "total_season_demand": 8000,
                    "manufacturing_qty": 9600
                },
                "timestamp": "2025-10-12T10:30:58Z"
            }
        }
    )


class ErrorMessage(BaseModel):
    """Message sent when agent encounters error."""

    type: Literal["error"] = "error"
    agent: Optional[str] = Field(None, description="Agent name (null if orchestrator error)")
    error_message: str = Field(..., description="Error description")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "error",
                "agent": "Demand Agent",
                "error_message": "Prophet model failed to converge: insufficient historical data",
                "timestamp": "2025-10-12T10:30:25Z"
            }
        }
    )


# Union type for all message types
WebSocketMessage = (
    AgentStartedMessage
    | AgentProgressMessage
    | AgentCompletedMessage
    | HumanInputRequiredMessage
    | WorkflowCompleteMessage
    | ErrorMessage
)
```

**Expected Output:**
- 6 Pydantic message models with validation
- Example JSON payloads for OpenAPI docs
- Union type for type safety

---

### Task 2: Create WebSocket Connection Manager

Create connection manager to handle multiple WebSocket connections.

**File:** `backend/app/websocket/manager.py`

```python
from fastapi import WebSocket
from typing import Dict, List
import logging
import asyncio
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time agent updates.

    Supports multiple connections per workflow_id (e.g., multiple browser tabs).
    Thread-safe using asyncio patterns.
    """

    def __init__(self):
        # workflow_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workflow_id: str):
        """
        Accept WebSocket connection and register it.

        Args:
            websocket: FastAPI WebSocket instance
            workflow_id: Workflow to subscribe to
        """
        await websocket.accept()

        if workflow_id not in self.active_connections:
            self.active_connections[workflow_id] = []

        self.active_connections[workflow_id].append(websocket)

        logger.info(f"WebSocket connected: workflow={workflow_id}, total_connections={len(self.active_connections[workflow_id])}")

    def disconnect(self, websocket: WebSocket, workflow_id: str):
        """
        Remove WebSocket connection from registry.

        Args:
            websocket: FastAPI WebSocket instance
            workflow_id: Workflow to unsubscribe from
        """
        if workflow_id in self.active_connections:
            if websocket in self.active_connections[workflow_id]:
                self.active_connections[workflow_id].remove(websocket)

                logger.info(f"WebSocket disconnected: workflow={workflow_id}, remaining_connections={len(self.active_connections[workflow_id])}")

                # Clean up empty workflow keys
                if len(self.active_connections[workflow_id]) == 0:
                    del self.active_connections[workflow_id]

    async def send_message(self, workflow_id: str, message: dict):
        """
        Send message to all connections for a workflow.

        Args:
            workflow_id: Workflow to broadcast to
            message: JSON-serializable message dict
        """
        if workflow_id not in self.active_connections:
            logger.warning(f"No active connections for workflow {workflow_id}, message not sent")
            return

        # Broadcast to all connections for this workflow
        disconnected = []

        for connection in self.active_connections[workflow_id]:
            try:
                await connection.send_json(message)
                logger.debug(f"Sent message to workflow {workflow_id}: {message.get('type', 'unknown')}")

            except Exception as e:
                logger.error(f"Failed to send message to connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, workflow_id)

    async def send_heartbeat(self, workflow_id: str):
        """
        Send heartbeat ping to all connections for a workflow.

        Args:
            workflow_id: Workflow to send heartbeat to
        """
        if workflow_id not in self.active_connections:
            return

        disconnected = []

        for connection in self.active_connections[workflow_id]:
            try:
                # Send ping, FastAPI WebSocket handles pong response automatically
                await connection.send_text("ping")
                logger.debug(f"Sent heartbeat ping to workflow {workflow_id}")

            except Exception as e:
                logger.error(f"Heartbeat failed for connection: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, workflow_id)

    def get_connection_count(self, workflow_id: str) -> int:
        """
        Get number of active connections for workflow.

        Args:
            workflow_id: Workflow to check

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(workflow_id, []))


# Global connection manager instance
manager = ConnectionManager()
```

**Expected Output:**
- ConnectionManager class with 5 methods
- Supports multiple connections per workflow_id
- Thread-safe async implementation
- Automatic cleanup of disconnected clients

---

### Task 3: Create WebSocket Endpoint

Create FastAPI WebSocket endpoint.

**File:** `backend/app/api/websocket.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.manager import manager
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/api/workflows/{workflow_id}/stream")
async def workflow_stream(websocket: WebSocket, workflow_id: str):
    """
    WebSocket endpoint for real-time agent updates.

    **Connection URL:** `ws://localhost:8000/api/workflows/{workflow_id}/stream`

    **Message Types:**
    1. `agent_started` - Agent begins execution
    2. `agent_progress` - Line-by-line progress updates
    3. `agent_completed` - Agent finishes execution
    4. `human_input_required` - Approval modal needed
    5. `workflow_complete` - All agents finished
    6. `error` - Agent error occurred

    **Heartbeat:**
    - Server sends ping every 30 seconds
    - Client must respond with pong (automatic in browser WebSocket)

    **Example Usage (JavaScript):**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/workflows/wf_abc123/stream');

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log(`[${message.type}]`, message);

      if (message.type === 'agent_progress') {
        updateProgressBar(message.progress_pct);
        appendLogLine(message.agent, message.message);
      }

      if (message.type === 'human_input_required') {
        showApprovalModal(message.data, message.options);
      }

      if (message.type === 'workflow_complete') {
        showSuccessNotification(message.result);
        ws.close();
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };
    ```
    """
    # Accept connection
    await manager.connect(websocket, workflow_id)

    # Send initial connection confirmation
    await websocket.send_json({
        "type": "connection_established",
        "workflow_id": workflow_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    try:
        # Start heartbeat task (every 30 seconds)
        async def heartbeat_loop():
            while True:
                await asyncio.sleep(30)
                await manager.send_heartbeat(workflow_id)

        heartbeat_task = asyncio.create_task(heartbeat_loop())

        # Listen for messages from client (e.g., pong responses)
        while True:
            data = await websocket.receive_text()

            # Handle pong responses
            if data == "pong":
                logger.debug(f"Received pong from workflow {workflow_id}")
                continue

            # Handle other client messages (currently none expected)
            logger.info(f"Received client message: {data}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: workflow={workflow_id}")
        heartbeat_task.cancel()
        manager.disconnect(websocket, workflow_id)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        heartbeat_task.cancel()
        manager.disconnect(websocket, workflow_id)
```

**Expected Output:**
- WebSocket endpoint at `/api/workflows/{workflow_id}/stream`
- Connection lifecycle handling (connect, disconnect)
- Heartbeat loop sends ping every 30 seconds
- Error handling with cleanup

---

### Task 4: Register WebSocket Router in Main Application

Add WebSocket router to FastAPI app.

**File:** `backend/app/main.py` (modifications)

```python
from fastapi import FastAPI
from .api import workflows, websocket  # Import WebSocket router

app = FastAPI(
    title="Fashion Forecast API",
    description="Multi-agent retail forecasting system with parameter-driven workflows",
    version="0.1.0"
)

# Include routers
app.include_router(workflows.router)
app.include_router(websocket.router)  # Register WebSocket endpoint

# Other routers...
```

**Expected Output:**
- WebSocket endpoint registered
- Accessible at `ws://localhost:8000/api/workflows/{workflow_id}/stream`

---

### Task 5: Create Helper Functions for Message Broadcasting

Create utility functions for agents to broadcast messages.

**File:** `backend/app/websocket/broadcaster.py`

```python
from .manager import manager
from ..schemas.websocket import (
    AgentStartedMessage,
    AgentProgressMessage,
    AgentCompletedMessage,
    HumanInputRequiredMessage,
    WorkflowCompleteMessage,
    ErrorMessage
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat() + "Z"


async def broadcast_agent_started(workflow_id: str, agent_name: str):
    """
    Broadcast agent_started message.

    Args:
        workflow_id: Workflow to broadcast to
        agent_name: Name of agent starting (e.g., "Demand Agent")
    """
    message = AgentStartedMessage(
        agent=agent_name,
        timestamp=get_timestamp()
    )
    await manager.send_message(workflow_id, message.model_dump())


async def broadcast_agent_progress(
    workflow_id: str,
    agent_name: str,
    progress_message: str,
    progress_pct: int
):
    """
    Broadcast agent_progress message.

    Args:
        workflow_id: Workflow to broadcast to
        agent_name: Name of agent
        progress_message: Progress text (e.g., "Running Prophet forecasting model...")
        progress_pct: Overall workflow progress (0-100)
    """
    message = AgentProgressMessage(
        agent=agent_name,
        message=progress_message,
        progress_pct=progress_pct,
        timestamp=get_timestamp()
    )
    await manager.send_message(workflow_id, message.model_dump())


async def broadcast_agent_completed(
    workflow_id: str,
    agent_name: str,
    duration_seconds: float,
    result: dict = None
):
    """
    Broadcast agent_completed message.

    Args:
        workflow_id: Workflow to broadcast to
        agent_name: Name of agent
        duration_seconds: Agent execution time
        result: Agent output (optional)
    """
    message = AgentCompletedMessage(
        agent=agent_name,
        duration_seconds=duration_seconds,
        result=result,
        timestamp=get_timestamp()
    )
    await manager.send_message(workflow_id, message.model_dump())


async def broadcast_human_input_required(
    workflow_id: str,
    agent_name: str,
    action: str,
    data: dict,
    options: list[str]
):
    """
    Broadcast human_input_required message.

    Args:
        workflow_id: Workflow to broadcast to
        agent_name: Name of agent
        action: Action identifier (e.g., "approve_manufacturing_order")
        data: Data for approval modal
        options: Available actions (e.g., ["modify", "accept"])
    """
    message = HumanInputRequiredMessage(
        agent=agent_name,
        action=action,
        data=data,
        options=options,
        timestamp=get_timestamp()
    )
    await manager.send_message(workflow_id, message.model_dump())


async def broadcast_workflow_complete(
    workflow_id: str,
    duration_seconds: float,
    result: dict
):
    """
    Broadcast workflow_complete message.

    Args:
        workflow_id: Workflow to broadcast to
        duration_seconds: Total workflow execution time
        result: Final workflow results
    """
    message = WorkflowCompleteMessage(
        workflow_id=workflow_id,
        duration_seconds=duration_seconds,
        result=result,
        timestamp=get_timestamp()
    )
    await manager.send_message(workflow_id, message.model_dump())


async def broadcast_error(
    workflow_id: str,
    error_message: str,
    agent_name: str = None
):
    """
    Broadcast error message.

    Args:
        workflow_id: Workflow to broadcast to
        error_message: Error description
        agent_name: Name of agent (null if orchestrator error)
    """
    message = ErrorMessage(
        agent=agent_name,
        error_message=error_message,
        timestamp=get_timestamp()
    )
    await manager.send_message(workflow_id, message.model_dump())
```

**Expected Output:**
- 6 helper functions for broadcasting messages
- Type-safe message construction with Pydantic
- Automatic timestamp generation
- Logging for debugging

---

### Task 6: Test WebSocket Connection with Mock Messages

Create pytest tests for WebSocket functionality.

**File:** `backend/tests/test_websocket.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_websocket_connection():
    """Test WebSocket connection establishment."""

    workflow_id = "wf_test123"

    with client.websocket_connect(f"/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection_established"
        assert data["workflow_id"] == workflow_id
        assert "timestamp" in data


def test_websocket_disconnect():
    """Test WebSocket graceful disconnection."""

    workflow_id = "wf_test456"

    with client.websocket_connect(f"/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        data = websocket.receive_json()
        assert data["type"] == "connection_established"

        # Close connection
        websocket.close()

    # Connection should be removed from manager
    # (Manager state is internal, so we just verify no errors)


@pytest.mark.asyncio
async def test_broadcast_agent_progress():
    """Test broadcasting agent progress message."""

    from app.websocket.broadcaster import broadcast_agent_progress

    workflow_id = "wf_test789"

    # Connect WebSocket in background
    with client.websocket_connect(f"/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        websocket.receive_json()

        # Broadcast progress message
        await broadcast_agent_progress(
            workflow_id=workflow_id,
            agent_name="Demand Agent",
            progress_message="Running Prophet forecasting model...",
            progress_pct=33
        )

        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "agent_progress"
        assert data["agent"] == "Demand Agent"
        assert data["message"] == "Running Prophet forecasting model..."
        assert data["progress_pct"] == 33
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_broadcast_workflow_complete():
    """Test broadcasting workflow complete message."""

    from app.websocket.broadcaster import broadcast_workflow_complete

    workflow_id = "wf_test_complete"

    with client.websocket_connect(f"/api/workflows/{workflow_id}/stream") as websocket:
        # Receive connection confirmation
        websocket.receive_json()

        # Broadcast workflow complete message
        await broadcast_workflow_complete(
            workflow_id=workflow_id,
            duration_seconds=58.7,
            result={
                "forecast_id": "f_spring_2025",
                "total_season_demand": 8000
            }
        )

        # Receive broadcasted message
        data = websocket.receive_json()
        assert data["type"] == "workflow_complete"
        assert data["workflow_id"] == workflow_id
        assert data["duration_seconds"] == 58.7
        assert data["result"]["forecast_id"] == "f_spring_2025"
```

**Expected Output:**
- WebSocket connection tests passing
- Message broadcasting tests passing
- Pytest confirms WebSocket functionality

---

### Task 7: Manual Testing with WebSocket Client

Test WebSocket endpoint manually using Python or JavaScript client.

**Test Script (Python):**

```python
# test_websocket_client.py
import asyncio
import websockets
import json


async def test_websocket():
    """Test WebSocket connection and message receiving."""

    workflow_id = "wf_manual_test"
    uri = f"ws://localhost:8000/api/workflows/{workflow_id}/stream"

    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")

        # Receive connection confirmation
        message = await websocket.recv()
        data = json.loads(message)
        print(f"[CONNECTED] {data}")

        # Listen for messages (or timeout after 60 seconds)
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=60)
                data = json.loads(message)
                print(f"[{data['type'].upper()}] {data}")

                if data['type'] == 'workflow_complete':
                    print("Workflow completed, closing connection")
                    break

        except asyncio.TimeoutError:
            print("No messages received for 60 seconds, closing connection")


if __name__ == "__main__":
    asyncio.run(test_websocket())
```

**Run Test:**

```bash
# Terminal 1: Start FastAPI server
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Run WebSocket client
python test_websocket_client.py
```

**Expected Output:**
```
Connected to ws://localhost:8000/api/workflows/wf_manual_test/stream
[CONNECTED] {'type': 'connection_established', 'workflow_id': 'wf_manual_test', 'timestamp': '2025-10-19T10:30:00Z'}
```

**Test Script (JavaScript - Browser Console):**

```javascript
// Open browser console at http://localhost:8000/docs
const ws = new WebSocket('ws://localhost:8000/api/workflows/wf_browser_test/stream');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`[${message.type}]`, message);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

**Expected Output:**
```
WebSocket connected
[connection_established] {type: 'connection_established', workflow_id: 'wf_browser_test', timestamp: '2025-10-19T10:30:00Z'}
```

---

### Task 8: Document WebSocket Usage in README

Add WebSocket documentation to backend README.

**File:** `backend/README.md` (section to add)

```markdown
## WebSocket API

### Real-Time Agent Updates

The backend provides a WebSocket endpoint for streaming agent progress updates in real-time.

**Endpoint:** `WS /api/workflows/{workflow_id}/stream`

**Example (JavaScript):**

\`\`\`javascript
const ws = new WebSocket('ws://localhost:8000/api/workflows/wf_abc123/stream');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'agent_started':
      console.log(`${message.agent} started`);
      break;

    case 'agent_progress':
      console.log(`${message.agent}: ${message.message} (${message.progress_pct}%)`);
      updateProgressBar(message.progress_pct);
      break;

    case 'agent_completed':
      console.log(`${message.agent} completed in ${message.duration_seconds}s`);
      break;

    case 'human_input_required':
      showApprovalModal(message.action, message.data, message.options);
      break;

    case 'workflow_complete':
      console.log('Workflow completed!', message.result);
      ws.close();
      break;

    case 'error':
      console.error(`Error in ${message.agent}: ${message.error_message}`);
      break;
  }
};
\`\`\`

**Message Types:**

1. **agent_started** - Agent begins execution
2. **agent_progress** - Line-by-line progress updates (every 2-5 seconds)
3. **agent_completed** - Agent finishes execution
4. **human_input_required** - Approval modal needed (e.g., manufacturing order)
5. **workflow_complete** - All agents finished
6. **error** - Agent error occurred

**Heartbeat:**
- Server sends `ping` every 30 seconds
- Browser WebSocket handles `pong` responses automatically
```

**Expected Output:**
- WebSocket documentation in README
- Example code for frontend developers
- Message type reference

---

## Dev Notes

### WebSocket vs Polling Comparison

**Polling (Status Endpoint):**
```javascript
// Poll every 2 seconds
setInterval(async () => {
  const response = await fetch(`/api/workflows/${workflowId}`);
  const data = await response.json();
  updateUI(data.status, data.progress_pct);
}, 2000);
```

**Pros:** Simple, stateless
**Cons:**
- Network overhead (30 requests per minute)
- Delayed updates (up to 2 seconds lag)
- Server load (processing 30 requests/min per user)

**WebSocket (Real-Time):**
```javascript
// One persistent connection
const ws = new WebSocket(`ws://localhost:8000/api/workflows/${workflowId}/stream`);
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  updateUI(message);
};
```

**Pros:**
- Instant updates (<100ms latency)
- Low network overhead (one connection)
- Low server load (one connection per user)
**Cons:** Requires WebSocket support (all modern browsers)

### Message Latency Targets

**NFR-1.5:** WebSocket message latency shall be <100ms

**Measurement:**
```python
# In broadcaster.py
import time

start = time.time()
await manager.send_message(workflow_id, message)
latency_ms = (time.time() - start) * 1000
logger.info(f"WebSocket latency: {latency_ms:.2f}ms")
```

**Expected:** <10ms for local development, <100ms for production

### Heartbeat Rationale

**Why 30 seconds?**
- Prevents idle connection timeout (most proxies timeout at 60s)
- Detects disconnected clients quickly
- Low overhead (2 pings per minute)

**How it works:**
1. Server sends `ping` text message every 30 seconds
2. Browser WebSocket API sends `pong` response automatically
3. If `pong` not received, connection is dead → cleanup

### Connection Manager Thread Safety

**Async/Await Pattern:**
- All methods are `async def` (non-blocking)
- `asyncio` handles concurrency automatically
- No locks needed (single-threaded event loop)

**Multiple Connections:**
- One workflow can have multiple connections (e.g., 2 browser tabs)
- All connections receive same messages (broadcast pattern)
- Disconnections don't affect other connections

### Integration with Orchestrator Agent (Phase 8)

**Current (Phase 3 - Scaffolding):**
- WebSocket server exists but no messages broadcast (no agent execution yet)
- Manual testing uses broadcaster helper functions

**Future (Phase 8 - Orchestrator Agent):**
```python
# In orchestrator agent execution
from app.websocket.broadcaster import broadcast_agent_progress

async def run_demand_agent(workflow_id: str):
    await broadcast_agent_started(workflow_id, "Demand Agent")

    # Run Prophet
    await broadcast_agent_progress(workflow_id, "Demand Agent", "Running Prophet model...", 10)
    prophet_result = run_prophet_model()

    # Run ARIMA
    await broadcast_agent_progress(workflow_id, "Demand Agent", "Running ARIMA model...", 20)
    arima_result = run_arima_model()

    # Complete
    await broadcast_agent_completed(workflow_id, "Demand Agent", 15.3, result={"forecast": 8000})
```

### Critical References

- **Planning Spec:** `planning/3_technical_architecture_v3.3.md` lines 1925-2010 (WebSocket endpoint)
- **Implementation Plan:** `implementation_plan.md` lines 274-318 (Task 8 details)
- **PRD:** `planning/4_prd_v3.3.md` lines 800-829 (FR-7.1-7.5 Real-time updates)

---

## Testing

### Manual Testing Checklist

- [ ] WebSocket connects successfully at `ws://localhost:8000/api/workflows/{id}/stream`
- [ ] Connection confirmation message received
- [ ] Heartbeat ping sent every 30 seconds
- [ ] Multiple connections to same workflow_id work simultaneously
- [ ] Disconnection cleans up connection from manager
- [ ] Broadcasting messages works (all 6 types)
- [ ] OpenAPI docs display WebSocket endpoint
- [ ] Error handling gracefully closes connections
- [ ] JavaScript client can connect from browser
- [ ] Python client can connect with websockets library

### Verification Commands

```bash
# Start FastAPI server
cd backend
uv run uvicorn app.main:app --reload

# Open browser to OpenAPI docs
open http://localhost:8000/docs

# Test with Python WebSocket client
python test_websocket_client.py

# Run pytest tests
uv run pytest tests/test_websocket.py -v

# Monitor connection manager logs
tail -f logs/backend.log | grep WebSocket
```

---

## File List

**Files to Create:**
- `backend/app/schemas/websocket.py` (6 Pydantic message models + WebSocketMessage union type)
- `backend/app/websocket/manager.py` (ConnectionManager class)
- `backend/app/api/websocket.py` (FastAPI WebSocket endpoint)
- `backend/app/websocket/broadcaster.py` (6 helper functions for broadcasting)
- `backend/tests/test_websocket.py` (pytest tests for WebSocket)
- `test_websocket_client.py` (manual testing script)

**Files to Modify:**
- `backend/app/main.py` (register WebSocket router)
- `backend/README.md` (add WebSocket documentation section)

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Added Change Log and QA Results sections for template compliance | Product Owner |

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

---

## Definition of Done

- [ ] 6 WebSocket message schemas created with Pydantic validation
- [ ] ConnectionManager class with 5 methods implemented
- [ ] WebSocket endpoint functional at `/api/workflows/{workflow_id}/stream`
- [ ] Connection lifecycle handled (connect, disconnect, heartbeat)
- [ ] Heartbeat ping sends every 30 seconds
- [ ] Message broadcasting works for all 6 message types
- [ ] Broadcaster helper functions created (6 functions)
- [ ] WebSocket router registered in main.py
- [ ] All pytest tests passing
- [ ] Manual testing with Python/JavaScript client successful
- [ ] Multiple connections to same workflow work
- [ ] OpenAPI docs display WebSocket endpoint
- [ ] README.md includes WebSocket documentation
- [ ] Logging shows connection/disconnection events
- [ ] File List updated with all created/modified files

---

## QA Results

_This section will be populated by QA Agent after story implementation and testing_

**QA Status:** Pending
**QA Agent:** TBD
**QA Date:** TBD

### Test Execution Results
- TBD

### Issues Found
- TBD

### Sign-Off
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No critical issues found
- [ ] Story approved for deployment

---

**Created:** 2025-10-19
**Last Updated:** 2025-10-21 (Implementation completed)
**Story Points:** 4
**Priority:** P0 (Blocker for real-time agent updates)
