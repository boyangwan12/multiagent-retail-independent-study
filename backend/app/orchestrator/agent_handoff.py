"""
Agent Handoff Manager for multi-agent coordination and sequential execution.

This module provides the core infrastructure for coordinating multiple agents
in a sequential workflow, with timeout enforcement and context passing.
"""

from typing import Dict, Any, Callable, TypeVar, List
import asyncio
import time
import logging

logger = logging.getLogger("fashion_forecast")

# Type variables for generic context/result types
T = TypeVar('T')  # Context type
R = TypeVar('R')  # Result type


class AgentHandoffManager:
    """
    Manages agent registration and sequential handoff execution.

    This class enables a multi-agent workflow where agents are executed
    sequentially, with each agent's output becoming the context for the next agent.

    Attributes:
        _agents: Registry of agent handlers by name
        _execution_log: List of execution records for debugging
        logger: Python logger for operational logging

    Example:
        >>> manager = AgentHandoffManager()
        >>> manager.register_agent("demand", demand_agent_handler)
        >>> manager.register_agent("inventory", inventory_agent_handler)
        >>>
        >>> # Execute single agent
        >>> result = await manager.call_agent("demand", parameters)
        >>>
        >>> # Execute agent chain
        >>> final_result = await manager.handoff_chain(
        ...     agents=["demand", "inventory", "pricing"],
        ...     initial_context=season_parameters
        ... )
    """

    def __init__(self):
        """Initialize the agent handoff manager."""
        self._agents: Dict[str, Callable] = {}
        self._execution_log: List[Dict] = []
        self.logger = logging.getLogger(__name__)

    def register_agent(self, name: str, handler: Callable):
        """
        Register an agent handler.

        Args:
            name: Agent name (e.g., "demand", "inventory", "pricing")
            handler: Async function that processes context and returns result
                Signature: async def handler(context: Any) -> Any

        Raises:
            TypeError: If handler is not callable

        Example:
            >>> async def mock_agent(ctx):
            ...     return {"result": "success"}
            >>> manager.register_agent("test_agent", mock_agent)
        """
        if not callable(handler):
            raise TypeError(f"Handler for agent '{name}' must be callable")

        if name in self._agents:
            self.logger.warning(f"Agent '{name}' already registered, overwriting")

        self._agents[name] = handler
        self.logger.info(f"Agent '{name}' registered successfully")

    async def call_agent(
        self,
        agent_name: str,
        context: T,
        timeout: int = 30
    ) -> R:
        """
        Execute agent with context.

        Args:
            agent_name: Name of agent to call
            context: Input context (SeasonParameters, ForecastResult, etc.)
            timeout: Max execution time in seconds (default: 30)

        Returns:
            Agent result

        Raises:
            ValueError: If agent not registered
            asyncio.TimeoutError: If agent exceeds timeout
            Exception: If agent execution fails (original exception propagated)

        Example:
            >>> result = await manager.call_agent("demand", parameters, timeout=60)
        """
        if agent_name not in self._agents:
            raise ValueError(f"Agent '{agent_name}' not registered")

        handler = self._agents[agent_name]
        start_time = time.time()

        self.logger.info(f"Calling agent '{agent_name}'")

        try:
            result = await asyncio.wait_for(
                handler(context),
                timeout=timeout
            )
            status = "success"
            self.logger.info(f"Agent '{agent_name}' completed successfully")

        except asyncio.TimeoutError:
            status = "timeout"
            self.logger.error(f"Agent '{agent_name}' timed out after {timeout}s")
            raise

        except Exception as e:
            status = "failed"
            self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
            raise

        finally:
            duration = time.time() - start_time
            self._log_execution(agent_name, start_time, duration, status)

        return result

    async def handoff_chain(
        self,
        agents: List[str],
        initial_context: Any
    ) -> Any:
        """
        Chain multiple agents sequentially, passing results between them.

        The result from Agent N becomes the context for Agent N+1.

        Args:
            agents: List of agent names to execute in order
                Example: ["demand", "inventory", "pricing"]
            initial_context: Context for first agent (usually SeasonParameters)

        Returns:
            Final result from last agent in chain

        Raises:
            ValueError: If any agent not registered
            asyncio.TimeoutError: If any agent times out
            Exception: If any agent fails

        Example:
            >>> final_result = await manager.handoff_chain(
            ...     agents=["demand", "inventory", "pricing"],
            ...     initial_context=season_parameters
            ... )
        """
        context = initial_context

        self.logger.info(f"Starting agent chain: {' → '.join(agents)}")

        for i, agent_name in enumerate(agents):
            self.logger.info(f"Chain step {i+1}/{len(agents)}: Calling '{agent_name}'")

            result = await self.call_agent(agent_name, context)
            context = result  # Pass result as context to next agent

        self.logger.info("Agent chain completed successfully")
        return context

    def _log_execution(
        self,
        agent_name: str,
        start_time: float,
        duration: float,
        status: str
    ):
        """
        Log agent execution for debugging and monitoring.

        Args:
            agent_name: Name of agent executed
            start_time: Unix timestamp when execution started
            duration: Execution duration in seconds
            status: Execution status (success, timeout, failed)
        """
        log_entry = {
            "agent_name": agent_name,
            "start_time": start_time,
            "duration_seconds": round(duration, 2),
            "status": status,
            "timestamp": time.time()
        }
        self._execution_log.append(log_entry)

    def get_execution_log(self) -> List[Dict]:
        """
        Return execution log for debugging.

        Returns:
            List of execution records with agent name, duration, status

        Example:
            >>> log = manager.get_execution_log()
            >>> for entry in log:
            ...     print(f"{entry['agent_name']}: {entry['duration_seconds']}s ({entry['status']})")
        """
        return self._execution_log

    def clear_log(self):
        """Clear execution log (useful between tests)."""
        self._execution_log = []


# Global singleton instance
handoff_manager = AgentHandoffManager()
