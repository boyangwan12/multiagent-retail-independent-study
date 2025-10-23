"""WebSocket connection manager for real-time agent updates."""

from fastapi import WebSocket
from typing import Dict, List
import logging
import json

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
