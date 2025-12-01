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
    description: Optional[str] = None  # Tool's purpose/description
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
    agent_instructions: Optional[str] = None  # WHY the agent was called
    agent_icon: str = "🤖"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    tools_used: List[ToolEvent] = field(default_factory=list)  # Tools run in this phase


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
        PhaseInfo("replenishment", "Replenishment", "🔄"),
        PhaseInfo("pricing", "Pricing", "💰"),
    ])
    current_phase_index: int = -1

    # Current agent state
    current_agent: Optional[str] = None
    current_agent_status: str = "idle"
    current_agent_message: str = ""
    current_agent_instructions: Optional[str] = None  # WHY the agent is called (purpose)
    current_agent_icon: str = "🤖"  # Agent-specific icon

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
        self.current_agent_instructions = None
        self.current_agent_icon = "🤖"
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

    def set_agent(self, agent_name: str, message: str = "", instructions: str = None, icon: str = "🤖"):
        """Set the current active agent."""
        self.current_agent = agent_name
        self.current_agent_status = "running"
        self.current_agent_message = message
        self.current_agent_instructions = instructions
        self.current_agent_icon = icon
        self.current_tools = []
        self._add_event("agent", f"{agent_name} started")

    def agent_completed(self, agent_name: str):
        """Mark agent as completed."""
        self.current_agent_status = "completed"
        self._add_event("agent", f"{agent_name} completed")

    def start_tool(self, tool_name: str, description: str = None):
        """Record tool start."""
        tool_event = ToolEvent(
            name=tool_name,
            status=ToolStatus.RUNNING,
            start_time=time.time(),
            description=description
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

        # Get agent instructions (the WHY)
        instructions = getattr(agent, 'instructions', None)
        if instructions:
            # Truncate long instructions for display
            if len(instructions) > 150:
                instructions = instructions[:147] + "..."

        # Get agent-specific icon
        icon = self._get_icon_for_agent(agent_name)

        self.state.set_agent(agent_name, "Processing...", instructions=instructions, icon=icon)

        # Auto-map agent to phase and start it
        phase_name = self._get_phase_for_agent(agent_name)
        if phase_name:
            self.state.start_phase(phase_name)
            # Store agent info in the phase for persistence after completion
            for phase in self.state.phases:
                if phase.name == phase_name:
                    phase.agent_name = agent_name
                    phase.agent_instructions = instructions
                    phase.agent_icon = icon
                    break

        self._notify()

    def _get_icon_for_agent(self, agent_name: str) -> str:
        """Get an icon for the agent based on its name."""
        agent_lower = agent_name.lower()

        if 'demand' in agent_lower or 'forecast' in agent_lower:
            return "📈"
        elif 'inventory' in agent_lower or 'allocation' in agent_lower:
            return "📦"
        elif 'realloc' in agent_lower or 'replenish' in agent_lower:
            return "🔄"
        elif 'pricing' in agent_lower or 'markdown' in agent_lower:
            return "💰"
        elif 'variance' in agent_lower:
            return "📊"
        elif 'coordinator' in agent_lower:
            return "🎯"

        return "🤖"

    def _get_phase_for_agent(self, agent_name: str) -> Optional[str]:
        """Map agent name to workflow phase name."""
        agent_lower = agent_name.lower()

        if 'demand' in agent_lower or 'forecast' in agent_lower:
            return 'forecast'
        elif 'inventory' in agent_lower or 'allocation' in agent_lower:
            return 'allocation'
        elif 'realloc' in agent_lower or 'replenish' in agent_lower:
            return 'replenishment'
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

        # Get tool description (try multiple attribute names)
        description = None
        for attr in ['description', '__doc__', 'docstring']:
            desc = getattr(tool, attr, None)
            if desc and isinstance(desc, str) and len(desc.strip()) > 0:
                description = desc.strip()
                break

        # Also try getting from the function if it's a function tool
        if not description:
            func = getattr(tool, 'fn', None) or getattr(tool, 'func', None)
            if func and hasattr(func, '__doc__') and func.__doc__:
                description = func.__doc__.strip()

        if description:
            # Get first line/sentence for brevity
            first_line = description.split('\n')[0].strip()
            if len(first_line) > 100:
                first_line = first_line[:97] + "..."
            description = first_line

        self.state.start_tool(tool_name, description=description)
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

        # Also store completed tool in the current phase for persistence
        current_phase = self.state.current_phase
        if current_phase:
            # Find the tool event we just completed and add to phase
            for tool_event in self.state.current_tools:
                if tool_event.name == tool_name and tool_event.status == ToolStatus.COMPLETED:
                    # Make a copy for the phase
                    current_phase.tools_used.append(tool_event)
                    break

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

    Args:
        workflow_state: WorkflowState instance containing current state
        show_header: Whether to show the section header
    """
    import streamlit as st

    # ==================== HEADER ====================
    if show_header:
        st.markdown("#### 🤖 Agent Workflow Status")

    # ==================== IDLE STATE ====================
    if not workflow_state.is_running and workflow_state.completed_phases == 0:
        st.info("Ready to run workflow")

        # Show available phases with expected agents
        phase_agents = {
            "forecast": ("📈 Demand Forecasting Agent", "📊 Variance Analysis Agent"),
            "allocation": ("📦 Inventory Allocation Agent",),
            "replenishment": ("🔄 Strategic Replenishment Agent",),
            "pricing": ("💰 Pricing Agent",),
        }

        for phase in workflow_state.phases:
            agents = phase_agents.get(phase.name, ())
            agent_hint = f" → {', '.join(agents)}" if agents else ""
            st.markdown(f"○ {phase.icon} {phase.display_name}{agent_hint}")
        return

    # ==================== PHASE LIST ====================
    for phase in workflow_state.phases:
        if phase.status == PhaseStatus.COMPLETED:
            _render_completed_phase(phase)
        elif phase.status == PhaseStatus.RUNNING:
            _render_running_phase(phase, workflow_state)
        elif phase.status == PhaseStatus.SKIPPED:
            st.markdown(f"⏭ ~~{phase.display_name}~~ *(skipped)*")
        elif phase.status == PhaseStatus.ERROR:
            st.error(f"Error: {phase.display_name}")
        else:
            st.markdown(f"○ {phase.display_name}")

    # ==================== STATS ====================
    _render_stats(workflow_state)

    # ==================== VARIANCE INFO ====================
    if workflow_state.variance_iterations > 0:
        st.markdown("---")
        st.caption(f"🔄 Variance Loop: {workflow_state.variance_iterations}/{workflow_state.variance_max}")
        if workflow_state.variance_reason:
            st.caption(workflow_state.variance_reason)


def _render_completed_phase(phase: PhaseInfo):
    """Render a completed phase card with full agent and tool details."""
    import streamlit as st

    duration_str = ""
    if phase.start_time and phase.end_time:
        duration_ms = (phase.end_time - phase.start_time) * 1000
        duration_str = f" ({duration_ms/1000:.1f}s)" if duration_ms > 1000 else f" ({duration_ms:.0f}ms)"

    # Show tool count in header
    tool_count = len(phase.tools_used) if phase.tools_used else 0
    tool_info = f" • {tool_count} tools" if tool_count > 0 else ""

    # Use checkbox toggle instead of expander to avoid nesting issues
    st.markdown(f"✅ **{phase.display_name}**{duration_str}{tool_info}")

    # Collapsible details using checkbox
    show_key = f"show_phase_{phase.name}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    if st.checkbox("Show details", key=f"toggle_{phase.name}", value=st.session_state[show_key]):
        st.session_state[show_key] = True
        with st.container():
            # Agent info with icon
            if phase.agent_name:
                icon = phase.agent_icon or "🤖"
                st.caption(f"{icon} {phase.agent_name}")

            # Tools section - show ALL tools
            if phase.tools_used:
                for tool in phase.tools_used:
                    dur = ""
                    if tool.duration_ms:
                        dur = f" ({tool.duration_ms/1000:.1f}s)" if tool.duration_ms > 1000 else f" ({tool.duration_ms:.0f}ms)"
                    st.caption(f"  ✓ `{tool.name}()`{dur}")
    else:
        st.session_state[show_key] = False


def _render_running_phase(phase: PhaseInfo, workflow_state: WorkflowState):
    """Render the currently running phase with live agent and tool status."""
    import streamlit as st

    with st.status(f"{phase.icon} {phase.display_name}", expanded=True, state="running"):
        # Agent info with details
        if workflow_state.current_agent:
            icon = workflow_state.current_agent_icon or "🤖"
            st.markdown(f"**{icon} {workflow_state.current_agent}**")

            # Show what the agent is doing
            if workflow_state.current_agent_instructions:
                st.caption(f"_{workflow_state.current_agent_instructions}_")

        # Tools - running
        running_tools = [t for t in workflow_state.current_tools if t.status == ToolStatus.RUNNING]
        completed_tools = [t for t in workflow_state.current_tools if t.status == ToolStatus.COMPLETED]

        if running_tools:
            st.markdown("**🔄 Running:**")
            for tool in running_tools:
                st.markdown(f"▸ `{tool.name}()` ...")
                if tool.description:
                    st.caption(f"   ↳ {tool.description}")

        # Tools - completed (show ALL, not just last 3)
        if completed_tools:
            st.markdown("**✅ Completed:**")
            for tool in completed_tools:
                dur = ""
                if tool.duration_ms:
                    dur = f" ({tool.duration_ms/1000:.1f}s)" if tool.duration_ms > 1000 else f" ({tool.duration_ms:.0f}ms)"
                st.markdown(f"✓ `{tool.name}()`{dur}")

        # Show tool count
        total_tools = len(running_tools) + len(completed_tools)
        if total_tools > 0:
            st.caption(f"Tools: {len(completed_tools)}/{total_tools} complete")


def _render_stats(workflow_state: WorkflowState):
    """Render stats row with detailed metrics."""
    import streamlit as st

    # Count completed tools across all phases
    all_phase_tools = []
    for phase in workflow_state.phases:
        if phase.tools_used:
            all_phase_tools.extend(phase.tools_used)
    # Also add current tools
    current_completed = [t for t in workflow_state.current_tools if t.status == ToolStatus.COMPLETED]
    total_tools = len(all_phase_tools) + len(current_completed)

    # Count unique agents from events
    agent_events = [e for e in workflow_state.events if e.get("type") == "agent" and "started" in e.get("message", "")]
    agent_names = list(set([e.get("message", "").replace(" started", "") for e in agent_events]))

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Time", f"{workflow_state.elapsed_seconds:.1f}s")
    col2.metric("Tools", total_tools)
    col3.metric("Agents", len(agent_names))

    # Event log (use checkbox toggle instead of expander to avoid nesting)
    if workflow_state.events:
        if st.checkbox("📜 Show Event Log", key="show_event_log", value=False):
            for event in reversed(workflow_state.events[-10:]):
                event_type = event.get("type", "")
                message = event.get("message", "")
                icon = {"agent": "🤖", "tool": "🔧", "phase": "📍", "workflow": "▶️", "guardrail": "🛡️"}.get(event_type, "•")
                st.caption(f"{icon} {message}")


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
    elif 'realloc' in agent_lower or 'replenish' in agent_lower:
        return 'replenishment'
    elif 'pricing' in agent_lower or 'markdown' in agent_lower:
        return 'pricing'
    elif 'variance' in agent_lower:
        return 'forecast'  # Variance triggers reforecast in forecast phase

    return None
