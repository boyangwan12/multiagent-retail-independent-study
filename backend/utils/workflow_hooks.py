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

        # Auto-map agent to phase and start it
        phase_name = self._get_phase_for_agent(agent_name)
        if phase_name:
            self.state.start_phase(phase_name)

        self._notify()

    def _get_phase_for_agent(self, agent_name: str) -> Optional[str]:
        """Map agent name to workflow phase name."""
        agent_lower = agent_name.lower()

        if 'demand' in agent_lower or 'forecast' in agent_lower:
            return 'forecast'
        elif 'inventory' in agent_lower or 'allocation' in agent_lower:
            return 'allocation'
        elif 'realloc' in agent_lower:
            return 'reallocation'
        elif 'pricing' in agent_lower or 'markdown' in agent_lower:
            return 'pricing'

        return None

    async def on_agent_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        output: Any,
    ) -> None:
        """Called when an agent completes."""
        agent_name = getattr(agent, 'name', str(agent))
        self.state.agent_completed(agent_name)

        # Auto-map agent to phase and complete it
        phase_name = self._get_phase_for_agent(agent_name)
        if phase_name:
            self.state.end_phase(phase_name)

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


# ============================================================================
# STREAMLIT SIDEBAR RENDERER - Phased Progress Tracker
# ============================================================================

def render_phased_progress_sidebar(workflow_state: WorkflowState, show_header: bool = False):
    """
    Render the Phased Progress Tracker in the Streamlit sidebar.

    Shows:
    - Overall progress bar with percentage
    - Phase list with status indicators
    - Current tool execution under active phase
    - Active agent status
    - Elapsed time and metrics

    Args:
        workflow_state: WorkflowState instance containing current state
        show_header: Whether to show the section header (default False for use in expanders)

    Usage:
        import streamlit as st
        from utils.workflow_hooks import WorkflowState, render_phased_progress_sidebar

        if "workflow_state" not in st.session_state:
            st.session_state.workflow_state = WorkflowState()

        with st.sidebar:
            render_phased_progress_sidebar(st.session_state.workflow_state)
    """
    # Import streamlit here to avoid import at module level
    import streamlit as st

    if show_header:
        st.markdown("### 🔬 Workflow Progress")

    # ==================== OVERALL PROGRESS ====================

    # Calculate progress
    completed = workflow_state.completed_phases
    total = workflow_state.total_phases

    # Check if any phase is running
    running_phase = next(
        (p for p in workflow_state.phases if p.status == PhaseStatus.RUNNING),
        None
    )

    # Calculate percentage - include partial progress for running phase
    if running_phase:
        # Add 0.5 for the running phase to show partial progress
        progress_value = (completed + 0.5) / total
    else:
        progress_value = completed / total if total > 0 else 0

    progress_value = min(max(progress_value, 0), 1.0)  # Clamp between 0 and 1

    # Show minimum progress if workflow is running
    if workflow_state.is_running and progress_value < 0.05:
        progress_value = 0.05

    st.progress(progress_value, text=f"{int(progress_value * 100)}% Complete")

    st.divider()

    # ==================== PHASE LIST ====================

    for phase in workflow_state.phases:
        if phase.status == PhaseStatus.COMPLETED:
            # Completed phase - green success with duration
            duration_str = ""
            if phase.start_time and phase.end_time:
                duration_ms = (phase.end_time - phase.start_time) * 1000
                if duration_ms > 1000:
                    duration_str = f" [{duration_ms/1000:.1f}s]"
                else:
                    duration_str = f" [{duration_ms:.0f}ms]"
            st.success(f"✅ {phase.display_name}{duration_str}")

        elif phase.status == PhaseStatus.RUNNING:
            # Running phase - expandable status container
            with st.status(f"🔄 {phase.display_name}", expanded=True, state="running") as status:
                # Show current tools
                running_tools = [t for t in workflow_state.current_tools if t.status == ToolStatus.RUNNING]
                if running_tools:
                    for tool in running_tools:
                        st.write(f"🔧 `{tool.name}()`")

                # Show agent message if any
                if workflow_state.current_agent_message:
                    st.caption(workflow_state.current_agent_message)

        elif phase.status == PhaseStatus.SKIPPED:
            # Skipped phase - dimmed
            st.caption(f"⏭️ ~~{phase.display_name}~~ (skipped)")

        elif phase.status == PhaseStatus.ERROR:
            # Error phase - red error
            st.error(f"❌ {phase.display_name}")

        else:
            # Pending phase - waiting
            st.caption(f"⏳ {phase.display_name}")

    st.divider()

    # ==================== ACTIVE AGENT STATUS ====================

    st.markdown("#### 🤖 Agent Status")

    if workflow_state.current_agent and workflow_state.current_agent_status == "running":
        st.info(f"🟢 {workflow_state.current_agent}")
    elif workflow_state.current_agent:
        st.caption(f"✅ {workflow_state.current_agent} (done)")
    else:
        st.caption("⏸️ Idle")

    st.divider()

    # ==================== RECENT TOOLS ====================

    st.markdown("#### 🔧 Recent Tools")

    completed_tools = [t for t in workflow_state.current_tools if t.status == ToolStatus.COMPLETED]

    if completed_tools:
        # Show last 4 completed tools
        for tool in completed_tools[-4:]:
            duration_str = ""
            if tool.duration_ms:
                if tool.duration_ms > 1000:
                    duration_str = f" ({tool.duration_ms/1000:.1f}s)"
                else:
                    duration_str = f" ({tool.duration_ms:.0f}ms)"
            st.caption(f"✓ `{tool.name}`{duration_str}")
    else:
        st.caption("*No tools executed yet*")

    st.divider()

    # ==================== METRICS ROW ====================

    col1, col2 = st.columns(2)

    with col1:
        elapsed = workflow_state.elapsed_seconds
        st.metric("⏱️ Time", f"{elapsed:.1f}s")

    with col2:
        tool_count = len(completed_tools)
        st.metric("🔧 Tools", tool_count)

    # ==================== VARIANCE INFO (if applicable) ====================

    if workflow_state.variance_iterations > 0:
        st.divider()
        st.markdown("#### 🔄 Variance Loop")
        st.caption(f"Iteration {workflow_state.variance_iterations} of {workflow_state.variance_max}")
        if workflow_state.variance_reason:
            st.caption(f"Reason: {workflow_state.variance_reason}")


def get_phase_for_agent(agent_name: str) -> Optional[str]:
    """
    Map agent name to workflow phase name.

    Args:
        agent_name: Name of the agent

    Returns:
        Phase name string or None if no mapping
    """
    agent_lower = agent_name.lower()

    if 'demand' in agent_lower or 'forecast' in agent_lower:
        return 'forecast'
    elif 'inventory' in agent_lower or 'allocation' in agent_lower:
        return 'allocation'
    elif 'realloc' in agent_lower:
        return 'reallocation'
    elif 'pricing' in agent_lower or 'markdown' in agent_lower:
        return 'pricing'
    elif 'variance' in agent_lower:
        return 'forecast'  # Variance triggers reforecast in forecast phase

    return None
