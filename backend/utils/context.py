"""
Context classes for OpenAI Agents SDK

This module defines the local context objects passed to agents and tools.
Context objects contain dependencies and runtime data but are NOT sent to the LLM.
"""
from dataclasses import dataclass
from typing import Optional
from utils.data_loader import TrainingDataLoader


@dataclass
class ForecastingContext:
    """
    Local context for forecasting agents and tools.

    This context is passed to all agents and tools in a run but is NOT sent to the LLM.
    It provides access to:
    - data_loader: For fetching training data and historical sales
    - session_id: Unique identifier for the current user session

    Usage:
        context = ForecastingContext(
            data_loader=my_data_loader,
            session_id="abc123"
        )

        result = Runner.run_sync(
            starting_agent=agent,
            input="user message",
            session=session,
            context=context  # ← Provides dependencies to tools
        )
    """
    data_loader: TrainingDataLoader
    session_id: str

    def __post_init__(self):
        """Validate context after initialization"""
        if self.data_loader is None:
            raise ValueError("data_loader cannot be None")
        if not self.session_id:
            raise ValueError("session_id cannot be empty")
