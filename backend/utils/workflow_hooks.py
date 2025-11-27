"""
Workflow UI Hooks for OpenAI Agents SDK

This module provides RunHooks implementation for capturing agent workflow
events and updating UI state in real-time.

The hooks capture:
- Agent start/end events
- Tool start/end events
- Phase transitions (via workflow layer)

Usage:
    from utils.workflow_hooks import WorkflowUIHooks, WorkflowState

    # Initialize state (store in st.session_state)
    workflow_state = WorkflowState()

    # Create hooks with callback
    hooks = WorkflowUIHooks(workflow_state)

    # Pass to Runner.run
    result = await Runner.run(
        agent,
        input="...",
        context=context,
        hooks=hooks
    )
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

# Import from agents SDK
try:
    from agents import RunHooks, RunContextWrapper, Agent, Tool
    from agents.tracing import Trace
except ImportError:
    # Fallback for type hints if SDK not available
    RunHooks = object
    RunContextWrapper = Any
    Agent = Any
    Tool = Any
    Trace = Any


class PhaseStatus(str, Enum):
    """Status of a workflow phase."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"


class ToolStatus(str, Enum):
    """Status of a tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ToolEvent:
    """Record of a tool execution."""
    name: str
    status: ToolStatus
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    result_preview: Optional[str] = None


@dataclass
class AgentEvent:
    """Record of an agent execution."""
    name: str
    phase: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tools: List[ToolEvent] = field(default_factory=list)
    output_preview: Optional[str] = None


@dataclass
class PhaseInfo:
    """Information about a workflow phase."""
    name: str
    display_name: str
    icon: str
    status: PhaseStatus = PhaseStatus.PENDING
    agent_name: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class WorkflowState:
    """
    State container for workflow UI visualization.

    Store this in st.session_state to persist across reruns.
    """
    # Overall workflow state
    is_running: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    # Phase tracking
    phases: List[PhaseInfo] = field(default_factory=lambda: [
        PhaseInfo("forecast", "Forecast", "📊"),
        PhaseInfo("allocation", "Allocation", "📦"),
        PhaseInfo("reallocation", "Realloc", "🔄"),
        PhaseInfo("pricing", "Pricing", "💰"),
    ])
    current_phase_index: int = -1

    # Current agent state
    current_agent: Optional[str] = None
    current_agent_status: str = "idle"
    current_agent_message: str = ""

    # Tool tracking
    current_tools: List[ToolEvent] = field(default_factory=list)

    # Event history
    events: List[Dict[str, Any]] = field(default_factory=list)

    # Guardrail results
    guardrails: List[Dict[str, Any]] = field(default_factory=list)

    # Output summaries per phase
    outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Variance loop tracking
    variance_iterations: int = 0
    variance_max: int = 2
    variance_reason: Optional[str] = None

    def reset(self):
        """Reset state for a new workflow run."""
        self.is_running = False
        self.start_time = None
        self.end_time = None
        self.current_phase_index = -1
        self.current_agent = None
        self.current_agent_status = "idle"
        self.current_agent_message = ""
        self.current_tools = []
        self.events = []
        self.guardrails = []
        self.outputs = {}
        self.variance_iterations = 0
        self.variance_reason = None

        # Reset phases
        for phase in self.phases:
            phase.status = PhaseStatus.PENDING
            phase.start_time = None
            phase.end_time = None

    def start_workflow(self):
        """Mark workflow as started."""
        self.reset()
        self.is_running = True
        self.start_time = time.time()
        self._add_event("workflow", "Workflow started")

    def end_workflow(self):
        """Mark workflow as completed."""
        self.is_running = False
        self.end_time = time.time()
        self.current_agent = None
        self.current_agent_status = "idle"
        self._add_event("workflow", "Workflow completed")

    def start_phase(self, phase_name: str):
        """Start a workflow phase."""
        for i, phase in enumerate(self.phases):
            if phase.name == phase_name:
                phase.status = PhaseStatus.RUNNING
                phase.start_time = time.time()
                self.current_phase_index = i
                self._add_event("phase", f"Phase '{phase.display_name}' started")
                break

    def end_phase(self, phase_name: str, skipped: bool = False):
        """End a workflow phase."""
        for phase in self.phases:
            if phase.name == phase_name:
                phase.status = PhaseStatus.SKIPPED if skipped else PhaseStatus.COMPLETED
                phase.end_time = time.time()
                self._add_event("phase", f"Phase '{phase.display_name}' {'skipped' if skipped else 'completed'}")
                break

    def set_agent(self, agent_name: str, message: str = ""):
        """Set the current active agent."""
        self.current_agent = agent_name
        self.current_agent_status = "running"
        self.current_agent_message = message
        self.current_tools = []
        self._add_event("agent", f"{agent_name} started")

    def agent_completed(self, agent_name: str):
        """Mark agent as completed."""
        self.current_agent_status = "completed"
        self._add_event("agent", f"{agent_name} completed")

    def start_tool(self, tool_name: str):
        """Record tool start."""
        tool_event = ToolEvent(
            name=tool_name,
            status=ToolStatus.RUNNING,
            start_time=time.time()
        )
        self.current_tools.append(tool_event)
        self._add_event("tool", f"{tool_name}() started")

    def end_tool(self, tool_name: str, result_preview: str = None):
        """Record tool completion."""
        for tool in self.current_tools:
            if tool.name == tool_name and tool.status == ToolStatus.RUNNING:
                tool.status = ToolStatus.COMPLETED
                tool.end_time = time.time()
                tool.duration_ms = (tool.end_time - tool.start_time) * 1000
                tool.result_preview = result_preview
                self._add_event("tool", f"{tool_name}() completed")
                break

    def add_guardrail_result(self, name: str, passed: bool, message: str = ""):
        """Add guardrail validation result."""
        self.guardrails.append({
            "name": name,
            "passed": passed,
            "message": message,
            "timestamp": time.time()
        })
        status = "passed" if passed else "failed"
        self._add_event("guardrail", f"{name}: {status}")

    def set_output(self, phase_name: str, output_data: Dict[str, Any]):
        """Store output summary for a phase."""
        self.outputs[phase_name] = output_data

    def set_variance_info(self, iteration: int, max_iter: int, reason: str = None):
        """Update variance loop information."""
        self.variance_iterations = iteration
        self.variance_max = max_iter
        self.variance_reason = reason

    def _add_event(self, event_type: str, message: str):
        """Add event to history."""
        self.events.append({
            "type": event_type,
            "message": message,
            "timestamp": time.time()
        })
        # Keep last 50 events
        if len(self.events) > 50:
            self.events = self.events[-50:]

    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def current_phase(self) -> Optional[PhaseInfo]:
        """Get current phase info."""
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None

    @property
    def completed_phases(self) -> int:
        """Count completed phases."""
        return sum(1 for p in self.phases if p.status == PhaseStatus.COMPLETED)

    @property
    def total_phases(self) -> int:
        """Total number of phases."""
        return len(self.phases)


class WorkflowUIHooks(RunHooks):
    """
    RunHooks implementation for UI updates.

    Captures agent and tool lifecycle events and updates WorkflowState.

    Usage:
        state = WorkflowState()
        hooks = WorkflowUIHooks(state)

        result = await Runner.run(agent, input, hooks=hooks)
    """

    def __init__(self, state: WorkflowState, on_update: Optional[Callable] = None):
        """
        Initialize hooks.

        Args:
            state: WorkflowState to update
            on_update: Optional callback when state changes (for UI refresh)
        """
        self.state = state
        self.on_update = on_update

    def _notify(self):
        """Notify UI of state change."""
        if self.on_update:
            self.on_update()

    async def on_agent_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
    ) -> None:
        """Called when an agent starts."""
        agent_name = getattr(agent, 'name', str(agent))
        self.state.set_agent(agent_name, "Processing...")
        self._notify()

    async def on_agent_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        output: Any,
    ) -> None:
        """Called when an agent completes."""
        agent_name = getattr(agent, 'name', str(agent))
        self.state.agent_completed(agent_name)
        self._notify()

    async def on_tool_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
    ) -> None:
        """Called when a tool starts."""
        tool_name = getattr(tool, 'name', str(tool))
        self.state.start_tool(tool_name)
        self._notify()

    async def on_tool_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called when a tool completes."""
        tool_name = getattr(tool, 'name', str(tool))
        # Create a preview of the result (truncated)
        preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        self.state.end_tool(tool_name, preview)
        self._notify()

    async def on_handoff(
        self,
        context: RunContextWrapper,
        from_agent: Agent,
        to_agent: Agent,
    ) -> None:
        """Called on agent handoff (not used in deterministic workflow)."""
        # This won't be called in your deterministic architecture
        # but included for completeness
        from_name = getattr(from_agent, 'name', str(from_agent))
        to_name = getattr(to_agent, 'name', str(to_agent))
        self.state._add_event("handoff", f"{from_name} → {to_name}")
        self._notify()


def create_workflow_hooks(session_state) -> WorkflowUIHooks:
    """
    Factory function to create hooks with Streamlit session state.

    Usage in Streamlit:
        if "workflow_state" not in st.session_state:
            st.session_state.workflow_state = WorkflowState()

        hooks = create_workflow_hooks(st.session_state)
    """
    if not hasattr(session_state, 'workflow_state'):
        session_state.workflow_state = WorkflowState()

    return WorkflowUIHooks(session_state.workflow_state)
