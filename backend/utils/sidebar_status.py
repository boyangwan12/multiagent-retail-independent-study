"""
Streamlit sidebar renderer for agent status.

This module provides a simple sidebar UI that displays:
- Current running agent
- Current tool being called
- Event history log

Usage:
    from utils.sidebar_status import render_agent_status_sidebar
    from utils.agent_status_hooks import AgentStatus

    # In your Streamlit app
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = AgentStatus()

    render_agent_status_sidebar(st.session_state.agent_status)
"""

import streamlit as st
from utils.agent_status_hooks import AgentStatus


def render_agent_status_sidebar(status: AgentStatus, show_header: bool = True):
    """
    Render current agent/tool status in Streamlit sidebar.

    Args:
        status: AgentStatus instance containing current state
        show_header: Whether to show the section header
    """
    # Use st.sidebar prefix for all elements
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Agent Status")

    # Debug: show status state
    st.sidebar.caption(f"Running: {status.is_running} | History: {len(status.history)}")

    # Current status display
    if status.is_running:
        if status.current_agent:
            st.sidebar.success(f"▶️ **{status.current_agent}**")
            if status.current_tool:
                st.sidebar.info(f"🔧 `{status.current_tool}()`")
            else:
                st.sidebar.caption("💭 Thinking...")
        else:
            st.sidebar.warning("⏳ Initializing...")
    else:
        if status.history:
            # Count completed agents
            agents_run = len([e for e in status.history if e.get("type") == "agent_end"])
            tools_run = len([e for e in status.history if e.get("type") == "tool_end"])

            # Show last completed agent
            last_agent = None
            for event in reversed(status.history):
                if event.get("type") == "agent_end":
                    last_agent = event.get("name")
                    break

            if last_agent:
                st.sidebar.success(f"✅ **{last_agent}**")
            st.sidebar.caption(f"Agents: {agents_run} | Tools: {tools_run}")
        else:
            st.sidebar.info("💤 Ready - run an agent to see status")

    # Event history - always show if there's history
    if status.history:
        with st.sidebar.expander("📜 Event Log", expanded=True):
            # Show last 15 events, most recent first
            for event in reversed(status.history[-15:]):
                _render_event(event)
    else:
        # Show available agents hint when no history
        st.sidebar.markdown("---")
        st.sidebar.caption("**Available Agents:**")
        agents = [
            "📈 Demand Forecasting",
            "📊 Variance Analysis",
            "📦 Inventory Allocation",
            "🔄 Strategic Replenishment",
            "💰 Pricing"
        ]
        for agent in agents:
            st.sidebar.caption(f"• {agent}")


def _render_event(event: dict):
    """Render a single event in the log."""
    event_type = event.get("type", "")
    name = event.get("name", "")

    if event_type == "agent_start":
        st.caption(f"▶️ {name}")
    elif event_type == "agent_end":
        st.caption(f"✅ {name}")
    elif event_type == "tool_start":
        st.caption(f"  🔧 {name}()")
    elif event_type == "tool_end":
        st.caption(f"  ✓ {name}()")
    elif event_type == "handoff":
        from_agent = event.get("from", "?")
        to_agent = event.get("to", "?")
        st.caption(f"🔀 {from_agent} → {to_agent}")
