"""WebSocket endpoint for real-time agent updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
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

    heartbeat_task = None
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
        if heartbeat_task:
            heartbeat_task.cancel()
        manager.disconnect(websocket, workflow_id)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if heartbeat_task:
            heartbeat_task.cancel()
        manager.disconnect(websocket, workflow_id)
