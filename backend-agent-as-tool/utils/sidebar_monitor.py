"""
Phased Progress Tracker - Streamlit Sidebar Component

Displays workflow progress as a linear pipeline with phase-based visualization.
Uses Streamlit native components only (no custom components).

Phases:
1. Forecast - Demand forecasting agent
2. Allocation - Inventory allocation agent
3. Variance - Variance checking (in-season)
4. Reforecast - Re-forecasting after high variance
"""

import streamlit as st
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import time


class PhaseStatus(str, Enum):
    """Status of a workflow phase."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class PhaseInfo:
    """Information about a workflow phase."""
    name: str
    display_name: str
    icon: str
    status: PhaseStatus = PhaseStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    current_tool: Optional[str] = None
    message: Optional[str] = None


def get_default_phases() -> List[PhaseInfo]:
    """Get the default workflow phases."""
    return [
        PhaseInfo("forecast", "Demand Forecast", "📊"),
        PhaseInfo("allocation", "Inventory Allocation", "📦"),
        PhaseInfo("variance", "Variance Check", "🔍"),
        PhaseInfo("reforecast", "Re-Forecast", "🔄"),
    ]


def initialize_phase_state(st_session_state):
    """Initialize phase tracking in session state if not present."""
    if not hasattr(st_session_state, 'workflow_phases'):
        st_session_state.workflow_phases = get_default_phases()
    if not hasattr(st_session_state, 'workflow_start_time'):
        st_session_state.workflow_start_time = None
    if not hasattr(st_session_state, 'current_phase_index'):
        st_session_state.current_phase_index = -1


def reset_workflow_phases(st_session_state):
    """Reset all phases to pending state."""
    st_session_state.workflow_phases = get_default_phases()
    st_session_state.workflow_start_time = None
    st_session_state.current_phase_index = -1


def start_phase(st_session_state, phase_name: str, message: str = None):
    """Mark a phase as running."""
    initialize_phase_state(st_session_state)

    if st_session_state.workflow_start_time is None:
        st_session_state.workflow_start_time = time.time()

    for i, phase in enumerate(st_session_state.workflow_phases):
        if phase.name == phase_name:
            phase.status = PhaseStatus.RUNNING
            phase.start_time = time.time()
            phase.message = message
            st_session_state.current_phase_index = i
            break


def complete_phase(st_session_state, phase_name: str):
    """Mark a phase as completed."""
    initialize_phase_state(st_session_state)

    for phase in st_session_state.workflow_phases:
        if phase.name == phase_name:
            phase.status = PhaseStatus.COMPLETED
            phase.end_time = time.time()
            if phase.start_time:
                phase.duration_ms = (phase.end_time - phase.start_time) * 1000
            phase.current_tool = None
            break


def skip_phase(st_session_state, phase_name: str):
    """Mark a phase as skipped."""
    initialize_phase_state(st_session_state)

    for phase in st_session_state.workflow_phases:
        if phase.name == phase_name:
            phase.status = PhaseStatus.SKIPPED
            break


def set_phase_tool(st_session_state, phase_name: str, tool_name: str):
    """Set the current tool for a phase."""
    initialize_phase_state(st_session_state)

    for phase in st_session_state.workflow_phases:
        if phase.name == phase_name:
            phase.current_tool = tool_name
            break


def set_phase_message(st_session_state, phase_name: str, message: str):
    """Set the status message for a phase."""
    initialize_phase_state(st_session_state)

    for phase in st_session_state.workflow_phases:
        if phase.name == phase_name:
            phase.message = message
            break


def get_workflow_progress(st_session_state) -> tuple:
    """Get workflow progress as (completed, total, percentage)."""
    initialize_phase_state(st_session_state)

    phases = st_session_state.workflow_phases
    # Only count non-skipped phases for total
    active_phases = [p for p in phases if p.status != PhaseStatus.SKIPPED and p.status != PhaseStatus.PENDING]
    completed = sum(1 for p in phases if p.status == PhaseStatus.COMPLETED)

    # Calculate based on phases that have been touched
    total = max(len(active_phases), 1)
    if any(p.status == PhaseStatus.RUNNING for p in phases):
        # If something is running, we're partway through
        running_idx = next((i for i, p in enumerate(phases) if p.status == PhaseStatus.RUNNING), 0)
        total = running_idx + 1

    percentage = (completed / max(total, 1)) * 100
    return completed, total, percentage


def get_elapsed_time(st_session_state) -> float:
    """Get elapsed time since workflow start in seconds."""
    initialize_phase_state(st_session_state)

    if st_session_state.workflow_start_time is None:
        return 0.0
    return time.time() - st_session_state.workflow_start_time


def render_phased_progress_sidebar(st_session_state):
    """
    Render the Phased Progress Tracker in the Streamlit sidebar.

    Shows:
    - Overall progress bar with percentage
    - Phase list with status indicators
    - Current tool execution under active phase
    - LLM thinking status
    - Elapsed time

    Args:
        st_session_state: Streamlit session_state object
    """
    initialize_phase_state(st_session_state)

    with st.sidebar:
        st.markdown("### 🔬 Workflow Progress")

        # ==================== OVERALL PROGRESS ====================

        completed, total, percentage = get_workflow_progress(st_session_state)

        # Check if any phase is running
        is_running = any(
            p.status == PhaseStatus.RUNNING
            for p in st_session_state.workflow_phases
        )

        # Progress bar
        progress_value = min(percentage / 100, 1.0)
        if is_running and progress_value < 1.0:
            # Show partial progress for running phase
            progress_value = max(progress_value, 0.05)  # Minimum visible progress

        st.progress(progress_value, text=f"{int(percentage)}% Complete")

        st.divider()

        # ==================== PHASE LIST ====================

        for phase in st_session_state.workflow_phases:
            if phase.status == PhaseStatus.COMPLETED:
                # Completed phase - green success
                duration_str = ""
                if phase.duration_ms:
                    if phase.duration_ms > 1000:
                        duration_str = f" [{phase.duration_ms/1000:.1f}s]"
                    else:
                        duration_str = f" [{phase.duration_ms:.0f}ms]"
                st.success(f"✅ {phase.display_name}{duration_str}")

            elif phase.status == PhaseStatus.RUNNING:
                # Running phase - expandable status container
                with st.status(f"🔄 {phase.display_name}", expanded=True, state="running") as status:
                    # Show current tool if any
                    current_tool = getattr(st_session_state, 'current_tool', None) or phase.current_tool
                    if current_tool:
                        st.write(f"🔧 `{current_tool}()`")

                    # Show phase message if any
                    if phase.message:
                        st.caption(phase.message)

                    # Show LLM thinking indicator
                    if getattr(st_session_state, 'llm_is_thinking', False):
                        st.write("💭 Thinking...")

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

        active_agent = getattr(st_session_state, 'active_agent', None)
        agent_is_running = getattr(st_session_state, 'agent_is_running', False)
        llm_thinking = getattr(st_session_state, 'llm_is_thinking', False)

        if active_agent and agent_is_running:
            if llm_thinking:
                with st.spinner(f"💭 {active_agent} thinking..."):
                    pass
            else:
                st.info(f"🟢 {active_agent}")
        elif active_agent:
            st.caption(f"✅ {active_agent} (done)")
        else:
            st.caption("⏸️ Idle")

        st.divider()

        # ==================== TOOLS EXECUTED ====================

        st.markdown("#### 🔧 Recent Tools")

        completed_tools = getattr(st_session_state, 'completed_tools', [])

        if completed_tools:
            # Show last 4 completed tools
            for tool_name in reversed(completed_tools[-4:]):
                st.caption(f"✓ `{tool_name}`")
        else:
            st.caption("*No tools executed yet*")

        st.divider()

        # ==================== METRICS ROW ====================

        col1, col2 = st.columns(2)

        with col1:
            elapsed = get_elapsed_time(st_session_state)
            if elapsed > 0:
                st.metric("⏱️ Time", f"{elapsed:.1f}s")
            else:
                st.metric("⏱️ Time", "0.0s")

        with col2:
            tool_count = len(completed_tools) if completed_tools else 0
            st.metric("🔧 Tools", tool_count)


def render_compact_status(st_session_state) -> str:
    """
    Get a compact single-line status string.

    Useful for showing in the main content area during execution.

    Args:
        st_session_state: Streamlit session_state object

    Returns:
        Status string like "🤖 Demand Agent | 💭 Thinking | 🔧 run_forecast"
    """
    initialize_phase_state(st_session_state)

    parts = []

    active_agent = getattr(st_session_state, 'active_agent', None)
    agent_is_running = getattr(st_session_state, 'agent_is_running', False)

    if active_agent and agent_is_running:
        parts.append(f"🤖 {active_agent}")

    if getattr(st_session_state, 'llm_is_thinking', False):
        parts.append("💭 Thinking")

    current_tool = getattr(st_session_state, 'current_tool', None)
    if current_tool:
        parts.append(f"🔧 {current_tool}")

    if parts:
        return " | ".join(parts)
    return "⏸️ Idle"


# ==================== LEGACY COMPATIBILITY ====================
# Keep old function name for backward compatibility

def render_execution_monitor(st_session_state):
    """
    Legacy function name for backward compatibility.
    Redirects to the new phased progress sidebar.
    """
    render_phased_progress_sidebar(st_session_state)
