"""
Real-time Agent Execution Monitor for Streamlit Sidebar

Displays live status of agent execution including:
- Active agent
- LLM thinking status
- Tools executing
- Execution timeline
"""

import streamlit as st
from datetime import datetime


def render_execution_monitor(st_session_state):
    """
    Render a live execution status panel in Streamlit sidebar.

    Shows:
    - Current active agent with status indicator
    - LLM thinking status
    - Tools being executed
    - Recent execution timeline
    - Progress metrics

    Args:
        st_session_state: Streamlit session_state object containing execution tracking data
    """

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔬 Live Execution Monitor")

    # ==================== CURRENT AGENT STATUS ====================

    st.sidebar.markdown("#### 🤖 Active Agent")

    active_agent = getattr(st_session_state, 'active_agent', None)
    is_running = getattr(st_session_state, 'agent_is_running', False)

    if active_agent and is_running:
        st.sidebar.markdown(f"**{active_agent}** 🟢")
    elif active_agent:
        st.sidebar.markdown(f"*{active_agent}* ✅ (completed)")
    else:
        st.sidebar.markdown("*No agent active*")

    st.sidebar.divider()

    # ==================== LLM THINKING STATUS ====================

    st.sidebar.markdown("#### 💭 LLM Status")

    llm_thinking = getattr(st_session_state, 'llm_is_thinking', False)
    current_reasoning = getattr(st_session_state, 'current_reasoning', None)

    if llm_thinking:
        st.sidebar.markdown("🤔 **Thinking...**")
        if current_reasoning:
            st.sidebar.caption(current_reasoning)
    else:
        llm_calls = getattr(st_session_state, 'llm_calls', [])
        if llm_calls:
            st.sidebar.markdown("✅ **Ready**")
        else:
            st.sidebar.markdown("⏳ **Waiting**")

    st.sidebar.divider()

    # ==================== CURRENT TOOL EXECUTION ====================

    st.sidebar.markdown("#### 🔧 Current Tool")

    current_tool = getattr(st_session_state, 'current_tool', None)
    tools_executing = getattr(st_session_state, 'tools_executing', [])

    if current_tool:
        st.sidebar.markdown(f"⚙️ **{current_tool}**")
    else:
        # Check if any tools are still in executing state
        active_tools = [t for t in tools_executing if t.get('status') == 'executing']
        if active_tools:
            st.sidebar.markdown(f"⚙️ **{active_tools[0]['name']}**")
        else:
            st.sidebar.markdown("*No tool executing*")

    st.sidebar.divider()

    # ==================== EXECUTION TIMELINE ====================

    st.sidebar.markdown("#### 📅 Recent Activity")

    agent_timeline = getattr(st_session_state, 'agent_timeline', [])

    if agent_timeline:
        # Show last 5 events
        recent_events = agent_timeline[-5:]

        for event in reversed(recent_events):  # Most recent first
            agent = event.get('agent', 'Unknown')
            event_type = event.get('event', 'unknown')
            timestamp = event.get('timestamp', '')

            # Parse timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime('%I:%M:%S %p')
            except:
                time_str = ''

            if event_type == 'started':
                emoji = "▶️"
                text = f"Started"
            elif event_type == 'completed':
                emoji = "✅"
                text = f"Completed"
            else:
                emoji = "•"
                text = event_type

            # Shorten agent name if too long
            short_agent = agent.split()[0] if ' ' in agent else agent

            st.sidebar.caption(f"{emoji} {short_agent} - {text}")
            if time_str:
                st.sidebar.caption(f"   ⏰ {time_str}")
    else:
        st.sidebar.caption("*No activity yet*")

    st.sidebar.divider()

    # ==================== COMPLETED TOOLS ====================

    st.sidebar.markdown("#### ✅ Completed Tools")

    completed_tools = getattr(st_session_state, 'completed_tools', [])

    if completed_tools:
        # Show last 5 completed tools
        recent_tools = completed_tools[-5:]
        for tool in reversed(recent_tools):  # Most recent first
            st.sidebar.caption(f"✓ {tool}")
    else:
        st.sidebar.caption("*None yet*")

    st.sidebar.divider()

    # ==================== PROGRESS METRICS ====================

    st.sidebar.markdown("#### 📊 Session Metrics")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        # Count unique agents that have started
        unique_agents = len(set(
            e.get('agent') for e in agent_timeline
            if e.get('event') == 'started'
        )) if agent_timeline else 0
        st.sidebar.metric("Agents", unique_agents)

    with col2:
        tool_count = len(completed_tools) if completed_tools else 0
        st.sidebar.metric("Tools", tool_count)


def render_compact_status(st_session_state):
    """
    Render a compact single-line status indicator.

    Useful for showing in the main content area during execution.

    Args:
        st_session_state: Streamlit session_state object
    """
    active_agent = getattr(st_session_state, 'active_agent', None)
    is_running = getattr(st_session_state, 'agent_is_running', False)
    llm_thinking = getattr(st_session_state, 'llm_is_thinking', False)
    current_tool = getattr(st_session_state, 'current_tool', None)

    status_parts = []

    if active_agent and is_running:
        status_parts.append(f"🤖 {active_agent}")

    if llm_thinking:
        status_parts.append("💭 Thinking")

    if current_tool:
        status_parts.append(f"🔧 {current_tool}")

    if status_parts:
        return " | ".join(status_parts)
    else:
        return "⏸️ Idle"
