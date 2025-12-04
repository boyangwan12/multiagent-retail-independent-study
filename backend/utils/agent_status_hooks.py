"""
Native OpenAI Agent SDK hooks for agent/tool status tracking.

This module provides a minimal RunHooks implementation that tracks:
- Which agent is currently running
- Which tool is currently being called
- Event history for the session

Usage:
    from utils.agent_status_hooks import AgentStatus, AgentStatusHooks

    status = AgentStatus()
    hooks = AgentStatusHooks(status)
    result = await Runner.run(agent, input="...", hooks=hooks)
"""

from dataclasses import dataclass, field
from typing import Any

from agents import RunHooks, RunContextWrapper, Agent, Tool


@dataclass
class AgentStatus:
    """Minimal status state for UI display."""

    current_agent: str | None = None
    current_tool: str | None = None
    is_running: bool = False
    history: list[dict] = field(default_factory=list)

    def reset(self):
        """Reset status for a new workflow run."""
        self.current_agent = None
        self.current_tool = None
        self.is_running = False
        self.history = []

    def start(self):
        """Mark workflow as started."""
        self.reset()
        self.is_running = True

    def end(self):
        """Mark workflow as ended."""
        self.is_running = False
        self.current_agent = None
        self.current_tool = None


class AgentStatusHooks(RunHooks):
    """
    Pure native OpenAI Agent SDK RunHooks implementation.

    Tracks current agent and tool for UI display with optional toast notifications.

    Usage:
        status = AgentStatus()
        hooks = AgentStatusHooks(status, on_event=st.toast)  # Pass st.toast for notifications
        result = await Runner.run(agent, input="...", hooks=hooks)
    """

    def __init__(self, status: AgentStatus, on_event: callable = None):
        self.status = status
        self.on_event = on_event  # Optional callback for UI notifications (e.g., st.toast)

    def _notify(self, message: str, icon: str = None):
        """Fire notification callback if provided."""
        if self.on_event:
            self.on_event(f"{icon} {message}" if icon else message)

    async def on_agent_start(self, ctx: RunContextWrapper, agent: Agent) -> None:
        """Called when an agent starts running."""
        self.status.current_agent = agent.name
        self.status.current_tool = None
        self.status.history.append({
            "type": "agent_start",
            "name": agent.name
        })
        # Keep history bounded
        if len(self.status.history) > 50:
            self.status.history = self.status.history[-50:]

        self._notify(f"{agent.name} thinking...", "🤖")

    async def on_agent_end(self, ctx: RunContextWrapper, agent: Agent, output: Any) -> None:
        """Called when an agent finishes running."""
        self.status.history.append({
            "type": "agent_end",
            "name": agent.name
        })
        self.status.current_agent = None
        self.status.current_tool = None

        self._notify(f"{agent.name} done", "✅")

    async def on_tool_start(self, ctx: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        """Called when a tool starts executing."""
        self.status.current_tool = tool.name
        self.status.history.append({
            "type": "tool_start",
            "name": tool.name,
            "agent": agent.name
        })

        self._notify(f"{tool.name}", "🔧")

    async def on_tool_end(self, ctx: RunContextWrapper, agent: Agent, tool: Tool, result: str) -> None:
        """Called when a tool finishes executing."""
        self.status.history.append({
            "type": "tool_end",
            "name": tool.name,
            "agent": agent.name
        })
        self.status.current_tool = None

    async def on_handoff(self, ctx: RunContextWrapper, from_agent: Agent, to_agent: Agent) -> None:
        """Called on agent handoff (if using handoff patterns)."""
        self.status.history.append({
            "type": "handoff",
            "from": from_agent.name,
            "to": to_agent.name
        })
        self.status.current_agent = to_agent.name
        self.status.current_tool = None

        self._notify(f"Handoff → {to_agent.name}", "🔄")
