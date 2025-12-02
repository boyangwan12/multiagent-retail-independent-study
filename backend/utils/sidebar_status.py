"""
Streamlit sidebar dashboard for session context, metrics, and workflow progress.

Displays:
- Session context (product, season, weeks)
- Key metrics (forecast, allocated, sell-through, current week)
- Completed workflow steps

Usage:
    from utils.sidebar_status import render_sidebar_dashboard

    # In your Streamlit app main function
    render_sidebar_dashboard()
"""

import streamlit as st


def render_sidebar_dashboard():
    """
    Render the sidebar dashboard with session context, metrics, and workflow progress.

    Pulls data from st.session_state to display current workflow state.
    """
    # Get params from flow_state if available
    params = None
    if "flow_state" in st.session_state:
        params = st.session_state.flow_state.get("last_run_params")

    workflow_result = st.session_state.get("workflow_result")
    current_week = st.session_state.get("current_week", 0)
    total_weeks = st.session_state.get("total_season_weeks", 12)
    actual_sales = st.session_state.get("actual_sales", [])
    total_sold = st.session_state.get("total_sold", 0)

    # =========================================================================
    # SESSION CONTEXT
    # =========================================================================
    st.sidebar.markdown("### 📊 Session Context")

    if params:
        st.sidebar.markdown(f"**Product:** {params.category}")
        if params.season_start_date:
            st.sidebar.markdown(f"**Season:** {params.season_start_date.strftime('%b %Y')}")
        else:
            st.sidebar.markdown("**Season:** Not set")
        st.sidebar.markdown(f"**Weeks:** 1-{params.forecast_horizon_weeks}")
    else:
        st.sidebar.caption("No workflow started yet")

    st.sidebar.markdown("---")

    # =========================================================================
    # KEY METRICS
    # =========================================================================
    st.sidebar.markdown("### 📈 Key Metrics")

    if workflow_result:
        # Total Forecast
        total_forecast = sum(workflow_result.forecast.forecast_by_week)
        st.sidebar.metric("Total Forecast", f"{total_forecast:,} units")

        # Total Allocated
        total_allocated = workflow_result.allocation.initial_store_allocation
        st.sidebar.metric("Allocated", f"{total_allocated:,} units")

        # Sell-Through %
        if total_allocated > 0 and total_sold > 0:
            sell_through = total_sold / total_allocated
            st.sidebar.metric("Sell-Through", f"{sell_through:.0%}")
        else:
            st.sidebar.metric("Sell-Through", "—")

        # Current Week
        st.sidebar.metric("Current Week", f"{current_week} of {total_weeks}")
    else:
        st.sidebar.caption("Run pre-season workflow to see metrics")

    st.sidebar.markdown("---")

    # =========================================================================
    # COMPLETED STEPS
    # =========================================================================
    st.sidebar.markdown("### ✅ Workflow Progress")

    # Pre-season Forecast
    forecast_done = workflow_result is not None
    _render_step("Pre-season Forecast", forecast_done)

    # Initial Allocation
    allocation_done = workflow_result is not None and workflow_result.allocation is not None
    _render_step("Initial Allocation", allocation_done)

    # Replenishment (check if any week has replenishment result)
    replenishment_done = False
    if current_week > 0:
        for wk in range(1, current_week + 1):
            key = f"replenishment_agent_result_wk{wk}"
            if st.session_state.get(key):
                replenishment_done = True
                break

    if current_week > 0:
        _render_step(f"Week {current_week} Replenishment", replenishment_done)
    else:
        _render_step("Replenishment", False, disabled=True)

    # Markdown Analysis (check if any week has pricing result)
    markdown_done = False
    if current_week > 0:
        for wk in range(1, current_week + 1):
            key = f"pricing_agent_result_wk{wk}"
            if st.session_state.get(key):
                markdown_done = True
                break

    _render_step("Markdown Analysis", markdown_done)


def _render_step(label: str, completed: bool, disabled: bool = False):
    """Render a single workflow step with checkbox indicator."""
    if disabled:
        st.sidebar.markdown(f"⬜ {label}", help="Not yet available")
    elif completed:
        st.sidebar.markdown(f"☑️ {label}")
    else:
        st.sidebar.markdown(f"☐ {label}")
