"""Helper functions for broadcasting WebSocket messages."""

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
