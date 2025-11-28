"""
Retail Forecasting Multi-Agent System - Streamlit UI

This Streamlit application provides a user interface for the 3-agent
retail forecasting system (Demand, Inventory, Pricing agents).

Features:
- Pre-season planning (forecast + allocation)
- In-season updates with actual sales data
- Variance analysis and re-forecasting
- Markdown/pricing optimization

Usage:
    streamlit run streamlit_app.py
"""

import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import uuid

from utils.data_loader import TrainingDataLoader
from utils.context import ForecastingContext
from schemas.workflow_schemas import WorkflowParams, SeasonResult
from schemas.forecast_schemas import ForecastResult
from schemas.allocation_schemas import AllocationResult
from schemas.pricing_schemas import MarkdownResult
from schemas.variance_schemas import VarianceResult
from schemas.reallocation_schemas import ReallocationAnalysis, TransferOrder
from workflows.season_workflow import (
    run_full_season,
    run_preseason_planning,
    run_inseason_update,
)
from workflows.forecast_workflow import run_forecast
from agent_tools.variance_tools import check_variance
from agent_tools.bayesian_reforecast import bayesian_reforecast
from agent_tools.demand_tools import (
    clean_historical_sales,
    aggregate_to_weekly,
    EnsembleForecaster,
)
from schemas.forecast_schemas import ForecastResult
from utils.workflow_hooks import (
    WorkflowState,
    WorkflowUIHooks,
    create_workflow_hooks,
    render_phased_progress_sidebar,
)


# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Retail Forecasting System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Session State Initialization
# =============================================================================
def init_session_state():
    """Initialize session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]

    if "data_loader" not in st.session_state:
        st.session_state.data_loader = TrainingDataLoader()

    if "workflow_result" not in st.session_state:
        st.session_state.workflow_result = None

    if "running" not in st.session_state:
        st.session_state.running = False

    if "current_week" not in st.session_state:
        st.session_state.current_week = 0

    if "actual_sales" not in st.session_state:
        st.session_state.actual_sales = []

    if "total_sold" not in st.session_state:
        st.session_state.total_sold = 0

    if "variance_result" not in st.session_state:
        st.session_state.variance_result = None

    if "planning_mode" not in st.session_state:
        st.session_state.planning_mode = "pre-season"

    if "inseason_result" not in st.session_state:
        st.session_state.inseason_result = None

    # Reforecast state for auto-reforecast feature
    if "reforecast_result" not in st.session_state:
        st.session_state.reforecast_result = None

    if "reforecast_triggered" not in st.session_state:
        st.session_state.reforecast_triggered = False

    # In-Season Timeline State
    if "inseason_setup_complete" not in st.session_state:
        st.session_state.inseason_setup_complete = False

    if "total_season_weeks" not in st.session_state:
        st.session_state.total_season_weeks = 12  # Default

    if "season_start_date" not in st.session_state:
        st.session_state.season_start_date = None

    if "selected_week" not in st.session_state:
        st.session_state.selected_week = 1  # Currently selected week in timeline

    if "week_data" not in st.session_state:
        # Stores data for each week: {week_num: {status, actual_sales, variance, etc}}
        st.session_state.week_data = {}

    # Strategic Replenishment state
    if "reallocation_result" not in st.session_state:
        st.session_state.reallocation_result = None

    if "selected_reallocation_strategy" not in st.session_state:
        st.session_state.selected_reallocation_strategy = "dc_only"

    # Pending upload data for callback pattern
    if "pending_week_sales" not in st.session_state:
        st.session_state.pending_week_sales = {}  # {week_num: sales_value}

    # Store-level sales tracking (for Strategic Replenishment)
    if "store_actual_sales" not in st.session_state:
        st.session_state.store_actual_sales = {}  # {store_id: [week1_sales, week2_sales, ...]}

    if "pending_store_sales" not in st.session_state:
        st.session_state.pending_store_sales = {}  # {week_num: {store_id: sales_value}}

    # Workflow visualization state
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = WorkflowState()

    if "show_workflow_drawer" not in st.session_state:
        st.session_state.show_workflow_drawer = False

    # ==========================================================================
    # FLOW STATE TRACKING - Controls locked/active states of UI sections
    # ==========================================================================
    if "flow_state" not in st.session_state:
        st.session_state.flow_state = {
            # Gate: Pre-season must complete before in-season
            "preseason_complete": False,
            # Track which weeks have sales data uploaded
            "weeks_with_sales": [],
            # Track which weeks have been variance-analyzed
            "weeks_analyzed": [],
            # Markdown state
            "markdown_unlocked": False,
            "markdown_calculated": False,
            # Parameter change tracking for stale results warning
            "last_run_params": None,
        }


init_session_state()


# =============================================================================
# Flow State Helper Functions
# =============================================================================
def is_inseason_unlocked() -> bool:
    """Check if in-season tab should be unlocked (pre-season complete)."""
    return st.session_state.flow_state.get("preseason_complete", False)


def is_variance_unlocked(week: int) -> bool:
    """Check if variance section should be unlocked for a given week."""
    return week in st.session_state.flow_state.get("weeks_with_sales", [])


def is_markdown_unlocked(current_week: int, markdown_week: int) -> bool:
    """Check if markdown section should be unlocked."""
    return current_week >= markdown_week


def mark_preseason_complete():
    """Mark pre-season as complete, unlocking in-season."""
    st.session_state.flow_state["preseason_complete"] = True


def mark_week_sales_uploaded(week: int):
    """Mark a week as having sales data uploaded."""
    weeks = st.session_state.flow_state.get("weeks_with_sales", [])
    if week not in weeks:
        weeks.append(week)
        st.session_state.flow_state["weeks_with_sales"] = sorted(weeks)


def mark_week_analyzed(week: int):
    """Mark a week as variance-analyzed."""
    weeks = st.session_state.flow_state.get("weeks_analyzed", [])
    if week not in weeks:
        weeks.append(week)
        st.session_state.flow_state["weeks_analyzed"] = sorted(weeks)


def check_params_changed(current_params) -> bool:
    """Check if parameters changed since last workflow run."""
    last_params = st.session_state.flow_state.get("last_run_params")
    if last_params is None:
        return False
    return current_params != last_params


def save_run_params(params):
    """Save the parameters used for a workflow run."""
    st.session_state.flow_state["last_run_params"] = params


# =============================================================================
# Sidebar - Phased Progress Tracker
# =============================================================================
def render_sidebar_agent_status():
    """Render the sidebar with the Phased Progress Tracker."""
    state = st.session_state.workflow_state

    # Render phased progress directly in sidebar (not collapsed)
    with st.sidebar:
        render_phased_progress_sidebar(state, show_header=True)


# =============================================================================
# Locked/Active Section Rendering Helpers
# =============================================================================
def render_locked_section(title: str, icon: str, unlock_message: str):
    """Render a locked/disabled section with clear messaging."""
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"{icon} {title}")
        with col2:
            st.caption("🔒 LOCKED")

        st.info(f"⏳ {unlock_message}")


def render_active_section_header(title: str, icon: str):
    """Render header for an active section."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"{icon} {title}")
    with col2:
        st.caption("✅ ACTIVE")


# =============================================================================
# Pre-Season Parameters (rendered in Pre-Season tab)
# =============================================================================
def render_forecast_settings() -> tuple[str, int, date]:
    """Render forecast settings (Category, Horizon, Start Date). Returns (category, forecast_horizon, season_start_date)."""
    categories = st.session_state.data_loader.get_categories()

    with st.container(border=True):
        st.subheader("⚙️ Forecast Settings")
        col1, col2, col3 = st.columns(3)

        with col1:
            category = st.selectbox(
                "Product Category",
                options=categories,
                index=0 if categories else None,
                help="Select the product category to forecast",
                key="preseason_category",
            )

        with col2:
            forecast_horizon = st.slider(
                "Forecast Horizon (weeks)",
                min_value=4,
                max_value=52,
                value=12,
                help="Number of weeks to forecast (also sets season length)",
                key="preseason_forecast_horizon",
            )

        with col3:
            season_start_date = st.date_input(
                "Season Start Date",
                value=date.today(),
                help="When does your season start? Forecast will align to this date's seasonality patterns.",
                key="preseason_season_start_date",
            )

    return category, forecast_horizon, season_start_date


def render_inventory_settings() -> tuple[float, float]:
    """Render inventory settings (DC Holdback, Safety Stock). Returns (dc_holdback, safety_stock)."""
    with st.container(border=True):
        st.subheader("📦 Inventory Settings")
        st.caption("Adjust these to dynamically recalculate allocation")
        col1, col2 = st.columns(2)

        with col1:
            dc_holdback = st.slider(
                "DC Holdback %",
                min_value=20,
                max_value=60,
                value=45,
                step=5,
                format="%d%%",
                help="Percentage to hold at Distribution Center",
                key="preseason_dc_holdback",
            ) / 100

        with col2:
            safety_stock = st.slider(
                "Safety Stock %",
                min_value=10,
                max_value=50,
                value=20,
                step=5,
                format="%d%%",
                help="Safety stock buffer percentage",
                key="preseason_safety_stock",
            ) / 100

    return dc_holdback, safety_stock


def recalculate_allocation_dynamic(forecast, dc_holdback_pct: float, safety_stock_pct: float):
    """Recalculate allocation dynamically based on forecast and inventory settings."""
    from schemas.allocation_schemas import AllocationResult, ClusterAllocation, StoreAllocation

    # Get the original allocation to preserve cluster/store structure
    original_allocation = st.session_state.workflow_result.allocation

    # Recalculate manufacturing quantity
    total_demand = forecast.total_demand
    manufacturing_qty = int(total_demand * (1 + safety_stock_pct))

    # Recalculate DC holdback and store allocation
    dc_holdback = int(manufacturing_qty * dc_holdback_pct)
    initial_store_allocation = manufacturing_qty - dc_holdback

    # Scale cluster allocations proportionally
    original_store_total = original_allocation.initial_store_allocation
    scale_factor = initial_store_allocation / original_store_total if original_store_total > 0 else 1

    new_cluster_allocations = []
    for c in original_allocation.cluster_allocations:
        new_units = int(c.allocation_units * scale_factor)
        new_cluster_allocations.append(ClusterAllocation(
            cluster_id=c.cluster_id,
            cluster_name=c.cluster_name,
            store_count=c.store_count,
            allocation_percentage=c.allocation_percentage,
            allocation_units=new_units,
        ))

    # Scale store allocations proportionally
    new_store_allocations = []
    for s in original_allocation.store_allocations:
        new_units = int(s.allocation_units * scale_factor)
        new_store_allocations.append(StoreAllocation(
            store_id=s.store_id,
            cluster=s.cluster,
            cluster_id=s.cluster_id,
            allocation_units=new_units,
            allocation_factor=s.allocation_factor,
        ))

    return AllocationResult(
        manufacturing_qty=manufacturing_qty,
        safety_stock_pct=safety_stock_pct,
        dc_holdback=dc_holdback,
        dc_holdback_percentage=dc_holdback_pct,
        initial_store_allocation=initial_store_allocation,
        cluster_allocations=new_cluster_allocations,
        store_allocations=new_store_allocations,
        replenishment_strategy=original_allocation.replenishment_strategy,
        explanation=f"Dynamically recalculated: {manufacturing_qty:,} units manufactured "
                   f"({dc_holdback_pct:.0%} DC holdback, {safety_stock_pct:.0%} safety stock)",
    )


def render_preseason_parameters() -> WorkflowParams:
    """Render pre-season parameters within the Pre-Season tab and return WorkflowParams.
    Note: This is now only used for building WorkflowParams for the forecast workflow.
    """
    categories = st.session_state.data_loader.get_categories()

    # Get values from session state (set by individual render functions)
    category = st.session_state.get("preseason_category", categories[0] if categories else "")
    forecast_horizon = st.session_state.get("preseason_forecast_horizon", 12)
    dc_holdback = st.session_state.get("preseason_dc_holdback", 45) / 100
    safety_stock = st.session_state.get("preseason_safety_stock", 20) / 100

    season_start = date.today()
    replenishment = "weekly"
    markdown_week = min(6, forecast_horizon)
    markdown_threshold = 0.60
    elasticity = 2.0
    variance_threshold = 0.20
    max_reforecasts = 2

    return WorkflowParams(
        category=category,
        forecast_horizon_weeks=forecast_horizon,
        season_start_date=season_start,
        dc_holdback_pct=dc_holdback,
        safety_stock_pct=safety_stock,
        replenishment_strategy=replenishment,
        markdown_week=markdown_week,
        markdown_threshold=markdown_threshold,
        elasticity=elasticity,
        variance_threshold=variance_threshold,
        max_reforecasts=max_reforecasts,
    )


# =============================================================================
# In-Season Parameters (rendered conditionally in In-Season tab)
# =============================================================================
def render_operational_parameters(forecast_horizon: int) -> tuple[str, int]:
    """Render operational parameters (always shown in In-Season). Returns (replenishment, markdown_week)."""
    with st.container(border=True):
        render_active_section_header("Operational Settings", "⚙️")

        col1, col2 = st.columns(2)

        with col1:
            replenishment = st.selectbox(
                "Replenishment Strategy",
                options=["weekly", "bi-weekly", "none"],
                index=0,
                help="How often to replenish stores from DC",
                key="inseason_replenishment",
            )

        with col2:
            markdown_week = st.slider(
                "Markdown Checkpoint Week",
                min_value=4,
                max_value=min(forecast_horizon, 12),
                value=min(6, forecast_horizon),
                help="Week when markdown decision becomes available",
                key="inseason_markdown_week",
            )

    return replenishment, markdown_week


def render_variance_parameters() -> float:
    """Render variance parameters (shown after sales upload). Returns threshold."""
    with st.container(border=True):
        render_active_section_header("Variance Settings", "📉")

        variance_threshold = st.slider(
            "Variance Threshold",
            min_value=10,
            max_value=40,
            value=20,
            step=5,
            format="%d%%",
            help="Variance above this % triggers re-forecast recommendation",
            key="inseason_variance_threshold",
        ) / 100

    return variance_threshold


def render_markdown_parameters() -> tuple[float, float]:
    """Render markdown parameters (shown at checkpoint week). Returns (sell_through_target, elasticity)."""
    with st.container(border=True):
        render_active_section_header("Markdown Settings", "💰")

        col1, col2 = st.columns(2)

        with col1:
            markdown_threshold = st.slider(
                "Sell-Through Target",
                min_value=40,
                max_value=80,
                value=60,
                step=5,
                format="%d%%",
                help="Target sell-through rate",
                key="inseason_markdown_threshold",
            ) / 100

        with col2:
            elasticity = st.number_input(
                "Price Elasticity",
                min_value=1.0,
                max_value=4.0,
                value=2.0,
                step=0.5,
                help="Price elasticity factor for markdown calculation",
                key="inseason_elasticity",
            )

    return markdown_threshold, elasticity


# =============================================================================
# Forecast Visualization
# =============================================================================
def render_forecast_section(
    forecast: ForecastResult,
    params: WorkflowParams,
    actual_sales: list = None,
):
    """Render the forecast results section with optional actual sales comparison."""
    st.subheader("🔮 Demand Forecast")

    # Key metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total Demand",
            value=f"{forecast.total_demand:,} units",
        )

    with col2:
        st.metric(
            label="Weekly Average",
            value=f"{forecast.weekly_average:,} units",
        )

    with col3:
        confidence_label = (
            "Excellent"
            if forecast.confidence >= 0.85
            else "Good"
            if forecast.confidence >= 0.70
            else "Fair"
            if forecast.confidence >= 0.60
            else "Poor"
        )
        st.metric(
            label="Confidence",
            value=f"{forecast.confidence:.0%}",
            delta=confidence_label,
            help="Forecast confidence based on prediction interval width. Narrower intervals = higher confidence.",
        )

    # Forecast chart with optional actual sales
    weeks = list(range(1, len(forecast.forecast_by_week) + 1))

    fig = go.Figure()

    # Add confidence bands if available
    if forecast.lower_bound and forecast.upper_bound:
        fig.add_trace(
            go.Scatter(
                x=weeks + weeks[::-1],
                y=forecast.upper_bound + forecast.lower_bound[::-1],
                fill="toself",
                fillcolor="rgba(0, 100, 200, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% Confidence Interval",
                showlegend=True,
            )
        )

    # Main forecast line
    fig.add_trace(
        go.Scatter(
            x=weeks,
            y=forecast.forecast_by_week,
            mode="lines+markers",
            name="Forecast",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8),
        )
    )

    # Add actual sales line if available
    if actual_sales and len(actual_sales) > 0:
        actual_weeks = list(range(1, len(actual_sales) + 1))
        fig.add_trace(
            go.Scatter(
                x=actual_weeks,
                y=actual_sales,
                mode="lines+markers",
                name="Actual Sales",
                line=dict(color="#e74c3c", width=3, dash="dash"),
                marker=dict(size=10, symbol="diamond"),
            )
        )

    fig.update_layout(
        title=f"Weekly Demand Forecast vs Actual - {params.category}",
        xaxis_title="Week",
        yaxis_title="Units",
        hovermode="x unified",
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Agent explanation
    with st.expander("Agent Explanation", expanded=False):
        st.markdown(f"**Model Used:** {forecast.model_used}")
        st.info(forecast.explanation)

    # Seasonality insights (if available) - just the agent's natural language analysis
    if forecast.seasonality and forecast.seasonality.insight:
        with st.expander("🌡️ Seasonality Insights", expanded=True):
            st.success(forecast.seasonality.insight)


# =============================================================================
# Allocation Visualization
# =============================================================================
def render_allocation_section(allocation: AllocationResult):
    """Render the allocation results section."""
    st.subheader("📦 Inventory Allocation")

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Manufacturing Qty",
            value=f"{allocation.manufacturing_qty:,} units",
        )

    with col2:
        st.metric(
            label="DC Holdback",
            value=f"{allocation.dc_holdback:,} units",
        )

    with col3:
        st.metric(
            label="Store Allocation",
            value=f"{allocation.initial_store_allocation:,} units",
        )

    with col4:
        st.metric(
            label="Stores",
            value=f"{len(allocation.store_allocations)}",
        )

    # Two columns for charts
    col_cluster, col_store = st.columns(2)

    with col_cluster:
        # Cluster allocation pie chart
        # Calculate total units for actual percentage calculation
        total_cluster_units = sum(c.allocation_units for c in allocation.cluster_allocations)
        cluster_data = pd.DataFrame(
            [
                {
                    "Cluster": c.cluster_name,
                    "Units": c.allocation_units,
                    "Stores": c.store_count,
                    # Use actual unit percentage instead of historical sales percentage
                    "Percentage": (c.allocation_units / total_cluster_units * 100) if total_cluster_units > 0 else 0,
                }
                for c in allocation.cluster_allocations
            ]
        )

        fig_cluster = px.pie(
            cluster_data,
            values="Units",
            names="Cluster",
            title="Allocation by Store Cluster",
            color="Cluster",
            color_discrete_map={
                "Fashion_Forward": "#2ecc71",
                "Mainstream": "#3498db",
                "Value_Conscious": "#9b59b6",
            },
            hole=0.4,
        )
        fig_cluster.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_cluster, use_container_width=True)

    with col_store:
        # Cluster summary table
        st.markdown("**Cluster Summary**")
        st.dataframe(
            cluster_data,
            column_config={
                "Cluster": st.column_config.TextColumn("Cluster"),
                "Units": st.column_config.NumberColumn("Units", format="%d"),
                "Stores": st.column_config.NumberColumn("Stores"),
                "Percentage": st.column_config.NumberColumn(
                    "Allocation %", format="%.1f%%"
                ),
            },
            hide_index=True,
            use_container_width=True,
        )

    # Store allocation bar chart
    store_data = pd.DataFrame(
        [
            {
                "Store": s.store_id,
                "Units": s.allocation_units,
                "Cluster": s.cluster,
            }
            for s in allocation.store_allocations
        ]
    ).sort_values("Units", ascending=False)

    fig_stores = px.bar(
        store_data.head(20),  # Top 20 stores
        x="Store",
        y="Units",
        color="Cluster",
        title="Top 20 Store Allocations",
        color_discrete_map={
            "Fashion_Forward": "#2ecc71",
            "Mainstream": "#3498db",
            "Value_Conscious": "#9b59b6",
        },
    )
    fig_stores.update_layout(height=350)
    st.plotly_chart(fig_stores, use_container_width=True)

    # Full store details table (collapsed by default)
    with st.expander(f"📋 All Store Allocations ({len(allocation.store_allocations)} stores)", expanded=False):
        st.dataframe(
            store_data,
            column_config={
                "Store": st.column_config.TextColumn("Store ID"),
                "Units": st.column_config.NumberColumn("Allocated Units", format="%d"),
                "Cluster": st.column_config.TextColumn("Cluster"),
            },
            hide_index=True,
            use_container_width=True,
            height=400,
        )

        # Download button for store allocations
        csv = store_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Store Allocations CSV",
            data=csv,
            file_name="store_allocations.csv",
            mime="text/csv",
        )

    # Agent explanation
    with st.expander("Agent Explanation", expanded=False):
        st.markdown(f"**Replenishment Strategy:** {allocation.replenishment_strategy}")
        st.info(allocation.explanation)


# =============================================================================
# Pricing/Markdown Visualization
# =============================================================================
def render_pricing_section(
    markdown: MarkdownResult | None, params: WorkflowParams
):
    """Render the pricing/markdown results section."""
    st.subheader("💰 Pricing & Markdown")

    if markdown is None:
        st.info(
            f"No markdown check performed. "
            f"Currently at week {st.session_state.current_week}, "
            f"markdown checkpoint is week {params.markdown_week}."
        )
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Recommended Markdown",
            value=f"{markdown.recommended_markdown_pct:.0%}",
            delta="Applied" if markdown.markdown_needed else "None needed",
        )

    with col2:
        st.metric(
            label="Current Sell-Through",
            value=f"{markdown.current_sell_through:.0%}",
        )

    with col3:
        st.metric(
            label="Target Sell-Through",
            value=f"{markdown.target_sell_through:.0%}",
        )

    with col4:
        st.metric(
            label="Gap",
            value=f"{markdown.gap:.0%}",
        )

    # Visual indicator
    if markdown.recommended_markdown_pct == 0:
        st.success("✅ On track! No markdown needed.")
    elif markdown.recommended_markdown_pct <= 0.15:
        st.warning(
            f"⚠️ Minor adjustment: {markdown.recommended_markdown_pct:.0%} markdown recommended"
        )
    elif markdown.recommended_markdown_pct <= 0.30:
        st.warning(
            f"⚠️ Significant markdown: {markdown.recommended_markdown_pct:.0%} recommended"
        )
    else:
        st.error(
            f"🚨 Aggressive markdown: {markdown.recommended_markdown_pct:.0%} (near 40% cap)"
        )

    # Markdown calculation visual
    col_calc, col_gauge = st.columns([2, 1])

    with col_calc:
        st.markdown("### Markdown Calculation")
        st.markdown(
            f"""
            | Step | Value |
            |------|-------|
            | Current Sell-Through | {markdown.current_sell_through:.0%} |
            | Target Sell-Through | {markdown.target_sell_through:.0%} |
            | **Gap** | {markdown.gap:.0%} |
            | Elasticity | {markdown.elasticity_used}x |
            | Raw Markdown | {markdown.raw_markdown_pct:.0%} |
            | **Final Markdown** | {markdown.recommended_markdown_pct:.0%} |
            """
        )

    with col_gauge:
        # Simple gauge visualization
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=markdown.recommended_markdown_pct * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 40]},
                    "bar": {"color": "#e74c3c"},
                    "steps": [
                        {"range": [0, 15], "color": "#2ecc71"},
                        {"range": [15, 30], "color": "#f39c12"},
                        {"range": [30, 40], "color": "#e74c3c"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": markdown.recommended_markdown_pct * 100,
                    },
                },
                number={"suffix": "%"},
            )
        )
        fig_gauge.update_layout(height=200, margin=dict(t=0, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Agent explanation
    with st.expander("Agent Explanation", expanded=False):
        st.markdown(f"**Week Number:** {markdown.week_number}")
        if markdown.is_max_markdown:
            st.warning("⚠️ Markdown hit the 40% cap")
        st.info(markdown.explanation)


# =============================================================================
# ENHANCED: Markdown Command Center (Solution A)
# =============================================================================
def render_markdown_command_center(
    params: WorkflowParams,
    current_sell_through: float = None,
    total_sold: int = None,
    total_allocated: int = None,
    current_week: int = None,
):
    """
    Render the enhanced Markdown Command Center dashboard.

    This is Solution A - a dashboard-first approach for interactive markdown
    optimization with visual scenario comparison and impact preview.

    Args:
        params: WorkflowParams with markdown settings
        current_sell_through: Current sell-through rate (0.0-1.0)
        total_sold: Total units sold so far
        total_allocated: Total units allocated to stores
        current_week: Current week number
    """
    st.subheader("💰 Markdown Command Center")

    # Calculate values from context or use defaults
    week = current_week or st.session_state.get("current_week", 6)

    # Initialize session state for pricing (use week-specific keys to avoid conflicts)
    scenario_key = f"selected_markdown_scenario_wk{week}"
    applied_key = f"markdown_applied_wk{week}"

    if scenario_key not in st.session_state:
        st.session_state[scenario_key] = None
    if applied_key not in st.session_state:
        st.session_state[applied_key] = False
    total_weeks = params.forecast_horizon_weeks
    weeks_remaining = total_weeks - week

    # Get sell-through from session state or calculate
    if current_sell_through is None:
        sold = total_sold or st.session_state.get("total_sold", 0)
        allocated = total_allocated or st.session_state.get("total_allocated", 1)
        if allocated > 0:
            current_sell_through = sold / allocated
        else:
            current_sell_through = 0.0

    target_sell_through = params.markdown_threshold
    elasticity = params.elasticity

    # Calculate gap and recommended markdown
    gap = max(0, target_sell_through - current_sell_through)
    raw_markdown = gap * elasticity
    recommended_markdown = min(round(raw_markdown * 20) / 20, 0.40)  # Round to 5%, cap at 40%

    # Status indicator
    if current_sell_through >= target_sell_through:
        st.success("✅ **On Track** - No markdown action required")
        return
    elif gap <= 0.10:
        status_color = "orange"
        status_text = "Minor Gap"
    else:
        status_color = "red"
        status_text = "Action Required"

    # Header with status badge
    col_header, col_status = st.columns([3, 1])
    with col_header:
        st.markdown(f"**Week {week} of {total_weeks}** • {weeks_remaining} weeks remaining")
    with col_status:
        st.markdown(f":{status_color}[**{status_text}**]")

    st.divider()

    # ==========================================================================
    # Key Metrics Row
    # ==========================================================================
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        delta_text = f"{gap:.0%} below target" if gap > 0 else "On target"
        st.metric(
            label="Current Sell-Through",
            value=f"{current_sell_through:.0%}",
            delta=delta_text,
            delta_color="inverse" if gap > 0 else "normal",
        )

    with col2:
        st.metric(
            label="Target Sell-Through",
            value=f"{target_sell_through:.0%}",
        )

    with col3:
        st.metric(
            label="Performance Gap",
            value=f"{gap:.0%}",
            delta="Needs intervention" if gap > 0.10 else "Minor",
            delta_color="inverse" if gap > 0.10 else "off",
        )

    with col4:
        st.metric(
            label="Weeks Remaining",
            value=f"{weeks_remaining}",
        )

    with col5:
        st.metric(
            label="🤖 Recommended",
            value=f"{recommended_markdown:.0%}",
            delta="Markdown",
        )

    # ==========================================================================
    # Formula Display
    # ==========================================================================
    st.markdown("---")
    formula_col1, formula_col2, formula_col3 = st.columns([1, 2, 1])
    with formula_col2:
        # Format values for formula display
        gap_display = f"{gap:.0%}"
        elasticity_display = f"{elasticity}"
        markdown_display = f"{recommended_markdown:.0%}"

        formula_html = f'''<div style="text-align: center; padding: 10px; background: #1e1e2e; border-radius: 8px;">
<div style="color: #888; font-size: 0.85rem; margin-bottom: 8px;">Pricing Agent Formula: Gap × Elasticity = Markdown</div>
<div style="font-size: 1.3rem; font-family: monospace;">
<span style="color: #e74c3c; font-weight: bold;">{gap_display}</span> ×
<span style="color: #3498db; font-weight: bold;">{elasticity_display}</span> =
<span style="color: #2ecc71; font-weight: bold;">{markdown_display}</span> markdown
</div>
<div style="color: #666; font-size: 0.8rem; margin-top: 8px;">Rounded to nearest 5%, capped at 40% maximum</div>
</div>'''

        st.markdown(formula_html, unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================================================
    # Scenario Selection
    # ==========================================================================
    st.markdown("### 📋 Select Markdown Scenario")

    scenarios = [
        {"pct": 0, "label": "No Markdown", "impact": "Risk: Low ST"},
        {"pct": 0.20, "label": "Conservative", "impact": "Moderate lift"},
        {"pct": 0.30, "label": "Optimal", "impact": "Target ST"},
        {"pct": 0.40, "label": "Aggressive", "impact": "Max clearance"},
    ]

    # Find recommended scenario
    recommended_idx = min(range(len(scenarios)),
                         key=lambda i: abs(scenarios[i]["pct"] - recommended_markdown))

    scenario_cols = st.columns(4)
    selected_scenario_pct = st.session_state.get(scenario_key) or recommended_markdown

    for idx, (col, scenario) in enumerate(zip(scenario_cols, scenarios)):
        with col:
            is_recommended = idx == recommended_idx
            is_selected = abs(scenario["pct"] - selected_scenario_pct) < 0.01

            # Calculate projected sell-through for this scenario
            projected_st = min(current_sell_through + (scenario["pct"] / elasticity), 0.85)

            # Style based on selection
            border_color = "#2ecc71" if is_selected else "#444"
            bg_color = "rgba(46, 204, 113, 0.1)" if is_selected else "transparent"

            # Build recommended badge separately
            recommended_badge = ""
            if is_recommended:
                recommended_badge = '<span style="position: absolute; top: -10px; right: 10px; background: #2ecc71; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: bold;">RECOMMENDED</span>'

            # Format values
            pct_display = f"{scenario['pct']:.0%}"
            label_display = scenario['label']
            projected_display = f"{projected_st:.0%}"

            html_content = f'''<div style="border: 2px solid {border_color}; border-radius: 8px; padding: 16px; text-align: center; background: {bg_color}; position: relative;">
{recommended_badge}
<div style="font-size: 1.8rem; font-weight: bold;">{pct_display}</div>
<div style="color: #888; font-size: 0.85rem;">{label_display}</div>
<div style="color: #2ecc71; font-size: 0.85rem; margin-top: 8px;">Est: {projected_display} ST</div>
</div>'''

            st.markdown(html_content, unsafe_allow_html=True)

            if st.button(
                "Select" if not is_selected else "✓ Selected",
                key=f"scenario_{idx}_wk{week}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state[scenario_key] = scenario["pct"]
                st.rerun()

    # ==========================================================================
    # Parameter Adjustment
    # ==========================================================================
    st.markdown("### 🎛️ Adjust Parameters")

    param_col1, param_col2, param_col3 = st.columns(3)

    with param_col1:
        adjusted_target = st.slider(
            "Target Sell-Through",
            min_value=0.50,
            max_value=0.80,
            value=target_sell_through,
            step=0.05,
            format="%.0f%%",
            key=f"pricing_target_slider_wk{week}",
        )

    with param_col2:
        adjusted_elasticity = st.slider(
            "Price Elasticity",
            min_value=1.0,
            max_value=3.0,
            value=elasticity,
            step=0.5,
            key=f"pricing_elasticity_slider_wk{week}",
        )

    with param_col3:
        custom_override = st.slider(
            "Custom Markdown Override",
            min_value=0.0,
            max_value=0.40,
            value=selected_scenario_pct,
            step=0.05,
            format="%.0f%%",
            key=f"pricing_override_slider_wk{week}",
        )
        if custom_override != selected_scenario_pct:
            st.session_state[scenario_key] = custom_override

    # Recalculate with adjusted parameters
    adjusted_gap = max(0, adjusted_target - current_sell_through)
    adjusted_raw = adjusted_gap * adjusted_elasticity
    adjusted_recommendation = min(round(adjusted_raw * 20) / 20, 0.40)

    if adjusted_recommendation != recommended_markdown:
        st.info(f"📊 With adjusted parameters: {adjusted_recommendation:.0%} markdown recommended")

    # ==========================================================================
    # Charts Row
    # ==========================================================================
    st.markdown("### 📈 Forecast Visualization")

    chart_col1, chart_col2 = st.columns(2)

    # Get the selected markdown for projections
    final_markdown = st.session_state.get(scenario_key) or recommended_markdown

    with chart_col1:
        # Sell-Through Trajectory Chart
        weeks_range = list(range(1, total_weeks + 1))

        # Simulated actual data up to current week
        actual_data = [current_sell_through * (w / week) for w in range(1, week + 1)]
        actual_data_padded = actual_data + [None] * (total_weeks - week)

        # Target line
        target_line = [(w / total_weeks) * target_sell_through for w in weeks_range]

        # Projection with markdown
        projection_with_markdown = [None] * (week - 1) + [current_sell_through]
        weekly_lift = final_markdown / elasticity / weeks_remaining if weeks_remaining > 0 else 0
        for w in range(week + 1, total_weeks + 1):
            next_val = projection_with_markdown[-1] + weekly_lift * 0.8
            projection_with_markdown.append(min(next_val, 0.85))

        # Projection without markdown
        projection_no_markdown = [None] * (week - 1) + [current_sell_through]
        for w in range(week + 1, total_weeks + 1):
            next_val = projection_no_markdown[-1] + 0.012  # Slow organic growth
            projection_no_markdown.append(min(next_val, 0.60))

        fig_trajectory = go.Figure()

        # Actual line
        fig_trajectory.add_trace(go.Scatter(
            x=weeks_range[:week],
            y=actual_data,
            mode="lines+markers",
            name="Actual",
            line=dict(color="#3498db", width=3),
            marker=dict(size=8),
        ))

        # Target line
        fig_trajectory.add_trace(go.Scatter(
            x=weeks_range,
            y=target_line,
            mode="lines",
            name="Target",
            line=dict(color="#888", width=2, dash="dash"),
        ))

        # Projection with markdown
        fig_trajectory.add_trace(go.Scatter(
            x=weeks_range[week-1:],
            y=projection_with_markdown[week-1:],
            mode="lines+markers",
            name=f"With {final_markdown:.0%} Markdown",
            line=dict(color="#2ecc71", width=3),
            marker=dict(size=8),
        ))

        # Projection without markdown
        fig_trajectory.add_trace(go.Scatter(
            x=weeks_range[week-1:],
            y=projection_no_markdown[week-1:],
            mode="lines",
            name="No Markdown",
            line=dict(color="#e74c3c", width=2, dash="dot"),
        ))

        # Vertical line at current week
        fig_trajectory.add_vline(x=week, line_dash="dot", line_color="#9b59b6")
        fig_trajectory.add_annotation(
            x=week, y=0.75, text="Decision Point", showarrow=False,
            font=dict(color="#9b59b6", size=10),
        )

        fig_trajectory.update_layout(
            title="Sell-Through Trajectory",
            xaxis_title="Week",
            yaxis_title="Sell-Through %",
            height=350,
            yaxis=dict(tickformat=".0%", range=[0, 0.80]),
            legend=dict(x=0, y=1, font=dict(size=10)),
        )

        st.plotly_chart(fig_trajectory, use_container_width=True)

    with chart_col2:
        # Revenue vs Margin Tradeoff
        markdown_options = [0, 0.10, 0.20, 0.30, 0.40]

        # Simulated revenue and margin curves
        base_revenue = 280
        base_margin = 42

        revenues = [base_revenue + (m * 100 * 0.35) for m in markdown_options]
        margins = [base_margin - (m * 100 * 0.28) for m in markdown_options]

        fig_tradeoff = go.Figure()

        fig_tradeoff.add_trace(go.Scatter(
            x=[f"{int(m*100)}%" for m in markdown_options],
            y=revenues,
            mode="lines+markers",
            name="Revenue ($K)",
            yaxis="y",
            line=dict(color="#2ecc71", width=3),
            marker=dict(size=10),
        ))

        fig_tradeoff.add_trace(go.Scatter(
            x=[f"{int(m*100)}%" for m in markdown_options],
            y=margins,
            mode="lines+markers",
            name="Margin %",
            yaxis="y2",
            line=dict(color="#e74c3c", width=3),
            marker=dict(size=10),
        ))

        # Highlight selected markdown
        selected_idx = min(range(len(markdown_options)),
                         key=lambda i: abs(markdown_options[i] - final_markdown))

        fig_tradeoff.add_vline(
            x=selected_idx,
            line_dash="solid",
            line_color="#9b59b6",
            line_width=2,
        )

        fig_tradeoff.update_layout(
            title="Revenue vs Margin Tradeoff",
            xaxis_title="Markdown %",
            height=350,
            yaxis=dict(
                title=dict(text="Revenue ($K)", font=dict(color="#2ecc71")),
                tickfont=dict(color="#2ecc71"),
                range=[270, 330],
            ),
            yaxis2=dict(
                title=dict(text="Margin %", font=dict(color="#e74c3c")),
                tickfont=dict(color="#e74c3c"),
                overlaying="y",
                side="right",
                range=[25, 50],
            ),
            legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center"),
        )

        st.plotly_chart(fig_tradeoff, use_container_width=True)

    # ==========================================================================
    # Impact Preview
    # ==========================================================================
    st.markdown("### ✨ Forecast Impact Preview")

    # Calculate impact metrics
    allocated = total_allocated or st.session_state.get("total_allocated", 8540)
    sold = total_sold or st.session_state.get("total_sold", int(allocated * current_sell_through))

    projected_final_st = min(current_sell_through + (final_markdown / elasticity), 0.85)
    projected_sold = int(allocated * projected_final_st)
    leftover = allocated - projected_sold

    base_price = 89
    cost_price = 35
    discounted_price = base_price * (1 - final_markdown)
    additional_sales = projected_sold - sold
    revenue = int((sold * base_price + additional_sales * discounted_price) / 1000)
    margin = int(((discounted_price - cost_price) / discounted_price) * 100)

    impact_cols = st.columns(4)

    with impact_cols[0]:
        st.metric(
            label="Projected Final ST",
            value=f"{projected_final_st:.0%}",
            delta=f"+{projected_final_st - current_sell_through:.0%} from current",
        )

    with impact_cols[1]:
        st.metric(
            label="Est. Leftover Units",
            value=f"{leftover:,}",
            delta=f"-{int(allocated * (1 - current_sell_through)) - leftover:,} units",
        )

    with impact_cols[2]:
        st.metric(
            label="Projected Revenue",
            value=f"${revenue}K",
        )

    with impact_cols[3]:
        margin_delta = margin - 42  # Baseline margin
        st.metric(
            label="Est. Final Margin",
            value=f"{margin}%",
            delta=f"{margin_delta}%" if margin_delta != 0 else None,
            delta_color="inverse" if margin_delta < 0 else "normal",
        )

    # ==========================================================================
    # Agent Explanation (using checkbox toggle instead of expander to avoid nesting)
    # ==========================================================================
    show_analysis = st.checkbox("🤖 Show Pricing Agent Analysis", key=f"show_agent_analysis_wk{week}")

    if show_analysis:
        st.markdown(
            """
            <div style="background: #1e1e2e; border-radius: 8px; padding: 16px; margin: 8px 0;">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"""
**Recommendation Summary:**

Current sell-through of **{current_sell_through:.0%}** is **{gap:.0%} below** the target ({target_sell_through:.0%})
at the mid-season checkpoint (Week {week}).

**Calculation:**
- Gap: {target_sell_through:.0%} - {current_sell_through:.0%} = **{gap:.0%}**
- Elasticity factor: **{elasticity}** (standard for fashion retail)
- Raw markdown: {gap:.0%} × {elasticity} = **{raw_markdown:.0%}**
- Final markdown: **{recommended_markdown:.0%}** (rounded to 5%, within 40% cap)

**Business Context:**

At Week {week}, there are {weeks_remaining} weeks remaining to clear inventory.
A {final_markdown:.0%} markdown at this stage provides sufficient time for the price
reduction to drive sales velocity. Based on historical elasticity, expect sell-through
to increase by approximately {final_markdown / elasticity:.0%} percentage points.

**Risk Assessment:**
- {"✅" if final_markdown <= 0.30 else "⚠️"} {final_markdown:.0%} markdown {'is within optimal range' if final_markdown <= 0.30 else 'is aggressive'}
- {"✅" if margin >= 30 else "⚠️"} Margin will {'remain healthy' if margin >= 30 else 'be under pressure'} at {margin}%
- ✅ Below 40% cap - preserves brand positioning
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================================================
    # Action Buttons
    # ==========================================================================
    st.markdown("---")

    action_col1, action_col2, action_col3 = st.columns([2, 1, 1])

    with action_col1:
        if st.button(
            f"✅ Apply {final_markdown:.0%} Markdown & Reforecast",
            type="primary",
            use_container_width=True,
            key=f"apply_markdown_wk{week}",
        ):
            with st.spinner(f"Applying {final_markdown:.0%} markdown and rerunning forecast..."):
                import time
                time.sleep(1.5)  # Simulate processing

                st.session_state[applied_key] = True
                st.session_state[f"applied_markdown_pct_wk{week}"] = final_markdown
                st.success(f"✅ {final_markdown:.0%} markdown applied! Forecast updated.")
                st.balloons()

    with action_col2:
        if st.button("📅 Schedule for Later", use_container_width=True, key=f"schedule_markdown_wk{week}"):
            st.info("📅 Scheduling feature coming soon!")

    with action_col3:
        if st.button("⏭️ Skip This Week", use_container_width=True, key=f"skip_markdown_wk{week}"):
            st.warning("Markdown skipped. Will reassess next week.")


# =============================================================================
# Variance Analysis Section
# =============================================================================
def render_variance_analysis(
    variance: VarianceResult,
    forecast_by_week: list,
    actual_sales: list,
    params: WorkflowParams,
):
    """Render detailed variance analysis section."""
    st.subheader("📉 Variance Analysis")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_color = "inverse" if variance.is_high_variance else "normal"
        st.metric(
            label="Variance",
            value=f"{abs(variance.variance_pct):.1%}",
            delta=variance.direction.upper(),
            delta_color=delta_color,
        )

    with col2:
        st.metric(
            label="Actual Total",
            value=f"{variance.actual_total:,}",
        )

    with col3:
        st.metric(
            label="Forecast Total",
            value=f"{variance.forecast_total:,}",
        )

    with col4:
        st.metric(
            label="Variance (Units)",
            value=f"{variance.variance_units:+,}",
        )

    # Status indicator
    if variance.is_high_variance:
        st.error(
            f"🚨 **HIGH VARIANCE DETECTED** - {variance.direction.upper()}-forecast by {abs(variance.variance_pct):.1%} "
            f"(threshold: {params.variance_threshold:.0%})"
        )
    else:
        st.success(
            f"✅ Variance within acceptable range ({abs(variance.variance_pct):.1%} < {params.variance_threshold:.0%})"
        )

    # Week-by-week comparison chart
    weeks_available = min(len(actual_sales), len(forecast_by_week))
    comparison_data = pd.DataFrame(
        {
            "Week": list(range(1, weeks_available + 1)),
            "Forecast": forecast_by_week[:weeks_available],
            "Actual": actual_sales[:weeks_available],
        }
    )
    comparison_data["Variance"] = comparison_data["Forecast"] - comparison_data["Actual"]
    comparison_data["Variance %"] = (
        comparison_data["Variance"] / comparison_data["Forecast"] * 100
    ).round(1)

    col_chart, col_table = st.columns([2, 1])

    with col_chart:
        # Bar chart comparison
        fig_comparison = go.Figure()

        fig_comparison.add_trace(
            go.Bar(
                x=comparison_data["Week"],
                y=comparison_data["Forecast"],
                name="Forecast",
                marker_color="#1f77b4",
            )
        )

        fig_comparison.add_trace(
            go.Bar(
                x=comparison_data["Week"],
                y=comparison_data["Actual"],
                name="Actual",
                marker_color="#e74c3c",
            )
        )

        fig_comparison.update_layout(
            title="Week-by-Week: Forecast vs Actual",
            xaxis_title="Week",
            yaxis_title="Units",
            barmode="group",
            height=350,
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99),
        )

        st.plotly_chart(fig_comparison, use_container_width=True)

    with col_table:
        st.markdown("**Weekly Breakdown**")
        st.dataframe(
            comparison_data,
            column_config={
                "Week": st.column_config.NumberColumn("Week"),
                "Forecast": st.column_config.NumberColumn("Forecast", format="%d"),
                "Actual": st.column_config.NumberColumn("Actual", format="%d"),
                "Variance": st.column_config.NumberColumn("Var (Units)", format="%+d"),
                "Variance %": st.column_config.NumberColumn("Var %", format="%.1f%%"),
            },
            hide_index=True,
            use_container_width=True,
        )

    # Cumulative variance chart
    comparison_data["Cumulative Forecast"] = comparison_data["Forecast"].cumsum()
    comparison_data["Cumulative Actual"] = comparison_data["Actual"].cumsum()

    fig_cumulative = go.Figure()

    fig_cumulative.add_trace(
        go.Scatter(
            x=comparison_data["Week"],
            y=comparison_data["Cumulative Forecast"],
            mode="lines+markers",
            name="Cumulative Forecast",
            line=dict(color="#1f77b4", width=2),
        )
    )

    fig_cumulative.add_trace(
        go.Scatter(
            x=comparison_data["Week"],
            y=comparison_data["Cumulative Actual"],
            mode="lines+markers",
            name="Cumulative Actual",
            line=dict(color="#e74c3c", width=2),
        )
    )

    # Add variance area
    fig_cumulative.add_trace(
        go.Scatter(
            x=comparison_data["Week"].tolist() + comparison_data["Week"].tolist()[::-1],
            y=comparison_data["Cumulative Forecast"].tolist()
            + comparison_data["Cumulative Actual"].tolist()[::-1],
            fill="toself",
            fillcolor="rgba(255, 0, 0, 0.1)",
            line=dict(color="rgba(255,255,255,0)"),
            name="Variance Gap",
            showlegend=True,
        )
    )

    fig_cumulative.update_layout(
        title="Cumulative Forecast vs Actual (Variance Area)",
        xaxis_title="Week",
        yaxis_title="Cumulative Units",
        height=350,
    )

    st.plotly_chart(fig_cumulative, use_container_width=True)

    # Recommendation
    st.markdown("### Recommendation")
    st.info(variance.recommendation)


# =============================================================================
# Variance History Section (for workflow results)
# =============================================================================
def render_variance_history(result: SeasonResult):
    """Render the variance history section from workflow results."""
    if not result.variance_history:
        return

    st.subheader("📉 Variance History")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(
            label="Re-forecasts Triggered",
            value=result.reforecast_count,
            delta="High variance detected" if result.had_high_variance else "All good",
        )

    with col2:
        variance_data = pd.DataFrame(
            [
                {
                    "Week": v.week_number,
                    "Variance": f"{v.variance_pct:.1%}",
                    "High Variance": v.is_high_variance,
                    "Direction": v.direction,
                    "Action": "Re-forecast" if v.is_high_variance else "Continue",
                }
                for v in result.variance_history
            ]
        )

        if not variance_data.empty:
            st.dataframe(
                variance_data,
                column_config={
                    "Week": st.column_config.NumberColumn("Week"),
                    "Variance": st.column_config.TextColumn("Variance"),
                    "High Variance": st.column_config.CheckboxColumn("High?"),
                    "Direction": st.column_config.TextColumn("Direction"),
                    "Action": st.column_config.TextColumn("Action"),
                },
                hide_index=True,
                use_container_width=True,
            )


# =============================================================================
# In-Season Timeline Visualization
# =============================================================================
def get_week_status(week_num: int, params: WorkflowParams) -> dict:
    """Get the status of a specific week."""
    week_data = st.session_state.week_data.get(week_num, {})
    current_week = st.session_state.current_week
    markdown_week = params.markdown_week

    # Determine status
    if week_data.get("actual_sales") is not None:
        status = "completed"
        icon = "✓"
    elif week_num == current_week + 1:
        status = "current"
        icon = "●"
    elif week_num == markdown_week:
        status = "markdown_checkpoint"
        icon = "◆"
    else:
        status = "locked"
        icon = "○"

    return {
        "status": status,
        "icon": icon,
        "week_num": week_num,
        "is_markdown_week": week_num == markdown_week,
        "actual_sales": week_data.get("actual_sales"),
        "variance": week_data.get("variance"),
    }


def _on_week_select(week_num: int):
    """Callback for week button selection - avoids double-rerun issues."""
    st.session_state.selected_week = week_num


def render_timeline(params: WorkflowParams):
    """Render a clean, modern timeline using native Streamlit components."""
    total_weeks = st.session_state.total_season_weeks
    markdown_week = params.markdown_week
    selected_week = st.session_state.selected_week

    # Calculate progress
    completed_weeks = len([w for w in range(1, total_weeks + 1)
                          if st.session_state.week_data.get(w, {}).get("actual_sales") is not None])
    progress_pct = (completed_weeks / total_weeks) * 100 if total_weeks > 0 else 0

    # Timeline header
    st.markdown("### 📅 Season Timeline")

    # Progress bar
    st.progress(progress_pct / 100, text=f"Season Progress: {completed_weeks} of {total_weeks} weeks completed ({progress_pct:.0f}%)")

    st.markdown("")  # Spacer

    # Week buttons in a clean grid
    cols_per_row = min(total_weeks, 12)

    for row_start in range(1, total_weeks + 1, cols_per_row):
        row_end = min(row_start + cols_per_row, total_weeks + 1)
        cols = st.columns(cols_per_row)

        for idx, week_num in enumerate(range(row_start, row_end)):
            week_info = get_week_status(week_num, params)
            is_selected = week_num == selected_week

            with cols[idx]:
                # Determine button style based on status
                if week_info["status"] == "completed":
                    icon = "✅"
                    btn_type = "secondary"
                elif week_info["status"] == "current":
                    icon = "🔵"
                    btn_type = "primary"
                elif week_info["is_markdown_week"]:
                    icon = "💰"
                    btn_type = "secondary"
                else:
                    icon = "⚪"
                    btn_type = "secondary"

                # Override to primary if selected
                if is_selected:
                    btn_type = "primary"

                # Button label
                label = f"{icon} {week_num}"
                if week_info["is_markdown_week"]:
                    label = f"💰 {week_num}"

                st.button(
                    label,
                    key=f"week_btn_{week_num}",
                    use_container_width=True,
                    type=btn_type,
                    help=f"Week {week_num} - {week_info['status'].replace('_', ' ').title()}{' (Markdown Checkpoint)' if week_info['is_markdown_week'] else ''}",
                    on_click=_on_week_select,
                    args=(week_num,),
                )

    # Legend using columns
    st.markdown("")  # Spacer
    leg_cols = st.columns(4)
    with leg_cols[0]:
        st.caption("✅ Completed")
    with leg_cols[1]:
        st.caption("🔵 Current")
    with leg_cols[2]:
        st.caption("💰 Markdown")
    with leg_cols[3]:
        st.caption("⚪ Upcoming")


def render_week_workspace(params: WorkflowParams):
    """Render the workspace for the selected week."""
    selected_week = st.session_state.selected_week
    week_info = get_week_status(selected_week, params)
    markdown_week = params.markdown_week

    st.markdown(f"---")
    st.markdown(f"## Week {selected_week} of {st.session_state.total_season_weeks}")

    # Status indicator
    if week_info["status"] == "completed":
        st.success(f"✓ **Week {selected_week} Complete** - View-only mode")
    elif week_info["status"] == "current":
        st.info(f"● **Week {selected_week} Active** - Ready for data entry")
    elif week_info["status"] == "markdown_checkpoint":
        st.warning(f"◆ **Markdown Checkpoint Week** - Pricing agent available")
    else:
        st.caption(f"○ **Week {selected_week} Locked** - Complete previous weeks first")

    # Week workspace sections
    st.markdown("---")

    # Section 1: Sales Data Upload
    with st.expander("📊 1. Sales Data", expanded=(week_info["status"] in ["current", "locked"])):
        if week_info["status"] == "completed":
            # View-only mode
            st.markdown(f"**Actual Sales:** {week_info['actual_sales']:,} units")
            if st.session_state.workflow_result:
                forecast_val = st.session_state.workflow_result.forecast.forecast_by_week[selected_week - 1]
                st.markdown(f"**Forecasted:** {forecast_val:,} units")
        elif week_info["status"] in ["current", "locked"]:
            st.markdown("Upload actual sales data for this week:")

            st.markdown("""
            **CSV Format:** Must contain `quantity_sold` column
            ```
            date,store_id,quantity_sold
            2025-03-01,S001,44
            2025-03-01,S002,46
            ```
            """)

            uploaded_file = st.file_uploader(
                "Upload sales CSV",
                type=["csv"],
                key=f"upload_week_{selected_week}",
                help="Upload a CSV file with sales data for this week",
            )

            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    if "quantity_sold" in df.columns:
                        total_sales = int(df["quantity_sold"].sum())

                        # Check for store-level data
                        has_store_data = "store_id" in df.columns
                        store_count = df["store_id"].nunique() if has_store_data else 0

                        if has_store_data:
                            st.success(f"📊 Loaded {len(df)} rows from **{store_count} stores**, Total: **{total_sales:,}** units")
                        else:
                            st.success(f"📊 Loaded {len(df)} rows, Total: **{total_sales:,}** units")
                            st.info("💡 CSV has no 'store_id' column - store-level analysis unavailable")

                        # Store pending data for callback (aggregate)
                        st.session_state.pending_week_sales[selected_week] = total_sales

                        # Store pending store-level data if available
                        if has_store_data:
                            store_sales = df.groupby("store_id")["quantity_sold"].sum().to_dict()
                            st.session_state.pending_store_sales[selected_week] = store_sales

                        # Preview (no nested expander)
                        st.markdown("**Preview:**")
                        st.dataframe(df.head(10), use_container_width=True, height=200)

                        # Show store summary if available (using container to avoid nested expander)
                        if has_store_data:
                            st.markdown("---")
                            st.markdown("**📊 Store Summary** (Top 10)")
                            store_summary = df.groupby("store_id")["quantity_sold"].sum().reset_index()
                            store_summary.columns = ["Store", "Units Sold"]
                            store_summary = store_summary.sort_values("Units Sold", ascending=False)
                            st.dataframe(store_summary.head(10), use_container_width=True, height=200)

                        st.button(
                            "💾 Save Week Data",
                            key=f"save_upload_{selected_week}",
                            type="primary",
                            use_container_width=True,
                            on_click=_save_week_sales_callback,
                            args=(selected_week,),
                        )
                    else:
                        st.error("CSV must contain 'quantity_sold' column")
                except Exception as e:
                    st.error(f"Error reading file: {e}")

        else:
            st.info("Complete previous weeks to unlock this week.")

    # Render remaining sections (Variance, Reallocation, Pricing)
    render_week_sections(params, selected_week, week_info)


def _save_week_sales_callback(week_num: int):
    """Callback for save button - reads from pending_week_sales to avoid double-rerun."""
    sales_value = st.session_state.pending_week_sales.get(week_num)
    if sales_value is None:
        return

    # Save to week_data
    if week_num not in st.session_state.week_data:
        st.session_state.week_data[week_num] = {}
    st.session_state.week_data[week_num]["actual_sales"] = sales_value

    # Update current_week
    st.session_state.current_week = max(st.session_state.current_week, week_num)

    # Mark week as having sales uploaded in flow state (unlocks variance section)
    mark_week_sales_uploaded(week_num)

    # Rebuild actual_sales list (aggregate)
    actual_sales_list = []
    for w in range(1, st.session_state.total_season_weeks + 1):
        wd = st.session_state.week_data.get(w, {})
        if wd.get("actual_sales") is not None:
            actual_sales_list.append(wd.get("actual_sales", 0))

    st.session_state.actual_sales = actual_sales_list
    st.session_state.total_sold = sum(actual_sales_list)

    # Save store-level data if available
    store_sales = st.session_state.pending_store_sales.get(week_num)
    if store_sales:
        for store_id, units_sold in store_sales.items():
            if store_id not in st.session_state.store_actual_sales:
                st.session_state.store_actual_sales[store_id] = []

            # Extend list if needed to accommodate the week
            while len(st.session_state.store_actual_sales[store_id]) < week_num:
                st.session_state.store_actual_sales[store_id].append(0)

            # Set the value (week is 1-indexed, list is 0-indexed)
            st.session_state.store_actual_sales[store_id][week_num - 1] = units_sold

        # Also save to week_data for reference
        st.session_state.week_data[week_num]["store_sales"] = store_sales

    # Clear pending data after save
    st.session_state.pending_week_sales.pop(week_num, None)
    st.session_state.pending_store_sales.pop(week_num, None)


# =============================================================================
# Variance Visualization & Auto-Reforecast Helpers
# =============================================================================
def _render_variance_chart(params: WorkflowParams, selected_week: int):
    """Render unified forecast vs actual comparison chart with full forecast horizon."""
    if not st.session_state.workflow_result:
        return

    forecast = st.session_state.workflow_result.forecast
    actual_sales = st.session_state.actual_sales

    # Full forecast horizon (show ALL forecast weeks, not truncated)
    full_forecast = forecast.forecast_by_week
    total_forecast_weeks = len(full_forecast)

    if total_forecast_weeks == 0:
        return

    # Actual sales data (only weeks we have)
    weeks_with_actuals = len(actual_sales) if actual_sales else 0

    # Create unified comparison chart
    fig = go.Figure()

    # 1. Add confidence bands for full forecast horizon (if available)
    if forecast.lower_bound and forecast.upper_bound:
        weeks = list(range(1, total_forecast_weeks + 1))
        fig.add_trace(
            go.Scatter(
                x=weeks + weeks[::-1],
                y=forecast.upper_bound + forecast.lower_bound[::-1],
                fill="toself",
                fillcolor="rgba(31, 119, 180, 0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% Confidence Interval",
                showlegend=True,
            )
        )

    # 2. FULL Forecast line (all weeks in horizon)
    fig.add_trace(
        go.Scatter(
            x=list(range(1, total_forecast_weeks + 1)),
            y=full_forecast,
            mode="lines+markers",
            name="Original Forecast",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=6),
        )
    )

    # 3. Actual sales line (only weeks with data)
    if weeks_with_actuals > 0:
        fig.add_trace(
            go.Scatter(
                x=list(range(1, weeks_with_actuals + 1)),
                y=actual_sales,
                mode="lines+markers",
                name="Actual Sales",
                line=dict(color="#e74c3c", width=3),
                marker=dict(size=10, symbol="diamond"),
            )
        )

        # 4. Variance shading (only for weeks with both forecast and actual)
        forecast_subset = full_forecast[:weeks_with_actuals]
        fig.add_trace(
            go.Scatter(
                x=list(range(1, weeks_with_actuals + 1)) + list(range(weeks_with_actuals, 0, -1)),
                y=forecast_subset + actual_sales[::-1],
                fill="toself",
                fillcolor="rgba(231, 76, 60, 0.15)",
                line=dict(color="rgba(255,255,255,0)"),
                name="Variance Gap",
                showlegend=True,
            )
        )

    # 5. Reforecast line (if triggered) - show full horizon
    if st.session_state.reforecast_result:
        reforecast = st.session_state.reforecast_result
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(reforecast.forecast_by_week) + 1)),
                y=reforecast.forecast_by_week,
                mode="lines+markers",
                name="Updated Forecast",
                line=dict(color="#2ecc71", width=3, dash="dash"),
                marker=dict(size=8, symbol="star"),
            )
        )

    # 6. Add vertical line for current week
    if weeks_with_actuals > 0:
        fig.add_vline(
            x=weeks_with_actuals,
            line_dash="dot",
            line_color="gray",
            annotation_text=f"Week {weeks_with_actuals}",
            annotation_position="top"
        )

    fig.update_layout(
        title=f"Season Performance: Forecast vs Actual - {params.category}",
        xaxis_title="Week",
        yaxis_title="Units",
        hovermode="x unified",
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        xaxis=dict(dtick=1, range=[0.5, total_forecast_weeks + 0.5]),
    )

    st.plotly_chart(fig, use_container_width=True)


def _render_forecast_only_chart(params: WorkflowParams):
    """Render forecast-only chart when no actuals are available."""
    if not st.session_state.workflow_result:
        return

    forecast = st.session_state.workflow_result.forecast

    fig = go.Figure()

    # Add confidence bands if available
    if forecast.lower_bound and forecast.upper_bound:
        weeks = list(range(1, len(forecast.forecast_by_week) + 1))
        fig.add_trace(
            go.Scatter(
                x=weeks + weeks[::-1],
                y=forecast.upper_bound + forecast.lower_bound[::-1],
                fill="toself",
                fillcolor="rgba(0, 100, 200, 0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                name="95% Confidence Interval",
                showlegend=True,
            )
        )

    # Forecast line
    fig.add_trace(
        go.Scatter(
            x=list(range(1, len(forecast.forecast_by_week) + 1)),
            y=forecast.forecast_by_week,
            mode="lines+markers",
            name="Forecast",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=8),
        )
    )

    fig.update_layout(
        title=f"Demand Forecast - {params.category}",
        xaxis_title="Week",
        yaxis_title="Units",
        hovermode="x unified",
        height=300,
    )

    st.plotly_chart(fig, use_container_width=True)


def _run_direct_reforecast(params: WorkflowParams) -> ForecastResult:
    """
    Run reforecast using Bayesian updating with actual sales performance.

    This uses a statistically rigorous Bayesian approach that:
    1. Treats original forecast as prior belief
    2. Updates beliefs based on actual sales data
    3. Applies adjustments proportional to statistical confidence
    4. Properly propagates uncertainty for future weeks
    """
    # Get original forecast and actuals
    original_forecast = st.session_state.workflow_result.forecast
    actual_sales = st.session_state.actual_sales
    original_by_week = original_forecast.forecast_by_week

    weeks_with_actuals = len(actual_sales)
    total_weeks = len(original_by_week)

    if weeks_with_actuals == 0 or total_weeks == 0:
        # No actuals yet, return original forecast
        return original_forecast

    # Run Bayesian reforecast
    bayesian_result = bayesian_reforecast(
        original_forecast_by_week=original_by_week,
        actual_sales=actual_sales,
        original_confidence=original_forecast.confidence,
        original_lower_bound=original_forecast.lower_bound,
        original_upper_bound=original_forecast.upper_bound,
    )

    # Determine trend direction for model name
    if bayesian_result.adjustment_applied > 1.05:
        direction = "upward"
    elif bayesian_result.adjustment_applied < 0.95:
        direction = "downward"
    else:
        direction = "stable"

    # Calculate weekly average
    weekly_average = bayesian_result.total_demand // total_weeks if total_weeks > 0 else 0

    return ForecastResult(
        total_demand=bayesian_result.total_demand,
        forecast_by_week=bayesian_result.forecast_by_week,
        safety_stock_pct=original_forecast.safety_stock_pct,
        confidence=bayesian_result.confidence,
        model_used=f"Bayesian-Reforecast ({direction})",
        lower_bound=bayesian_result.lower_bound,
        upper_bound=bayesian_result.upper_bound,
        weekly_average=weekly_average,
        data_quality="bayesian_updated",
        explanation=bayesian_result.explanation,
    )


def _render_reforecast_comparison(params: WorkflowParams):
    """Render re-forecast metrics summary (chart is now unified in _render_variance_chart)."""
    if not st.session_state.reforecast_result or not st.session_state.workflow_result:
        return

    original = st.session_state.workflow_result.forecast
    reforecast = st.session_state.reforecast_result
    actuals = st.session_state.actual_sales

    st.markdown("### 📊 Re-forecast Summary")

    # Metrics comparison - 4 columns for better insight
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Original Forecast",
            f"{original.total_demand:,}",
        )

    with col2:
        st.metric(
            "Actual (To Date)",
            f"{sum(actuals):,}",
        )

    with col3:
        change_pct = (reforecast.total_demand - original.total_demand) / original.total_demand if original.total_demand > 0 else 0
        st.metric(
            "Updated Forecast",
            f"{reforecast.total_demand:,}",
            delta=f"{change_pct:+.1%}",
        )

    with col4:
        # Show remaining demand projection
        remaining = reforecast.total_demand - sum(actuals)
        st.metric(
            "Remaining Demand",
            f"{remaining:,}",
        )

    # Re-forecast details
    st.markdown("---")
    detail_cols = st.columns(3)
    with detail_cols[0]:
        st.markdown(f"**Model:** {reforecast.model_used}")
    with detail_cols[1]:
        st.markdown(f"**Confidence:** {reforecast.confidence:.0%}")
    with detail_cols[2]:
        st.markdown(f"**Data Quality:** {reforecast.data_quality}")

    st.info(reforecast.explanation)


def _render_agentic_variance_analysis(params: WorkflowParams, selected_week: int, variance_pct: float, is_high_variance: bool):
    """
    Render agentic variance analysis with automatic reforecast on high variance.

    This performs intelligent analysis directly (no LLM call to avoid hanging)
    and automatically triggers reforecast when variance is high.
    """
    # Compute analysis directly (fast, no LLM)
    analysis = _compute_variance_analysis(params, selected_week, variance_pct)

    # Display the analysis
    _display_variance_analysis(analysis, params, selected_week)

    # AUTO-TRIGGER reforecast if agent analysis recommends it
    # (analysis already accounts for severity, trend, and weeks remaining)
    if analysis["should_reforecast"]:
        reforecast_key = f"reforecast_week_{selected_week}"

        # Check if already reforecasted
        if not st.session_state.get(reforecast_key):
            st.warning("🔄 Auto-triggering re-forecast based on analysis...")

            with st.spinner("Running re-forecast with updated data..."):
                try:
                    reforecast_result = _run_direct_reforecast(params)
                    st.session_state.reforecast_result = reforecast_result
                    st.session_state[reforecast_key] = True
                    st.success("✅ Re-forecast complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Re-forecast failed: {e}")
        else:
            # Already reforecasted - show the comparison
            if st.session_state.reforecast_result:
                _render_reforecast_comparison(params)


def _compute_variance_analysis(params: WorkflowParams, selected_week: int, current_variance_pct: float) -> dict:
    """
    Compute variance analysis using intelligent rules (no LLM needed).

    Analyzes:
    - Weekly variance trend
    - Severity based on magnitude
    - Likely causes based on patterns
    - Recommended actions
    """
    forecast_by_week = st.session_state.workflow_result.forecast.forecast_by_week
    actual_sales = st.session_state.actual_sales
    total_weeks = len(forecast_by_week)
    weeks_remaining = total_weeks - selected_week

    # Calculate weekly variances
    weekly_variances = []
    for i in range(min(len(actual_sales), selected_week)):
        if forecast_by_week[i] > 0:
            var = (actual_sales[i] - forecast_by_week[i]) / forecast_by_week[i] * 100
        else:
            var = 0
        weekly_variances.append(var)

    # Determine trend
    if len(weekly_variances) >= 2:
        recent = weekly_variances[-1]
        earlier = weekly_variances[0]
        if abs(recent) > abs(earlier) + 5:
            trend = "worsening"
        elif abs(recent) < abs(earlier) - 5:
            trend = "improving"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    # Determine severity
    abs_variance = abs(current_variance_pct * 100)
    if abs_variance < 10:
        severity = "low"
    elif abs_variance < 20:
        severity = "medium"
    elif abs_variance < 35:
        severity = "high"
    else:
        severity = "critical"

    # Determine likely cause
    if current_variance_pct > 0:  # Under-forecast (actual > forecast)
        if trend == "worsening":
            likely_cause = "Systematic under-forecasting - demand stronger than predicted, possibly due to favorable market conditions or unaccounted promotions"
        else:
            likely_cause = "Demand exceeding forecast - may indicate seasonal strength or successful marketing"
    else:  # Over-forecast (actual < forecast)
        if trend == "worsening":
            likely_cause = "Systematic over-forecasting - demand weaker than predicted, possibly due to competition or market softness"
        else:
            likely_cause = "Sales below forecast - may indicate inventory issues, weather impact, or changing consumer preferences"

    # Determine recommended action
    if severity == "low":
        recommended_action = "continue"
        action_reasoning = "Variance is within acceptable range. Continue monitoring."
        should_reforecast = False
    elif severity == "medium" and trend != "worsening":
        recommended_action = "continue"
        action_reasoning = "Moderate variance but trend is stable/improving. Monitor closely."
        should_reforecast = False
    elif weeks_remaining < 2:
        recommended_action = "markdown" if current_variance_pct < 0 else "continue"
        action_reasoning = "Too few weeks remaining for reforecast to be effective."
        should_reforecast = False
    else:
        recommended_action = "reforecast"
        action_reasoning = f"High variance ({abs_variance:.1f}%) with {weeks_remaining} weeks remaining. Reforecast recommended to capture demand shift."
        should_reforecast = True

    # Build explanation
    explanation = f"""
**Variance Analysis for Week {selected_week}:**

- Current variance: {current_variance_pct*100:+.1f}%
- Trend: {trend.title()} (comparing week 1 to week {selected_week})
- Weeks remaining: {weeks_remaining} of {total_weeks}

**Weekly Breakdown:**
{', '.join([f'W{i+1}: {v:+.1f}%' for i, v in enumerate(weekly_variances)])}

**Assessment:**
{likely_cause}

**Recommendation:**
{action_reasoning}
"""

    return {
        "variance_pct": current_variance_pct * 100,
        "severity": severity,
        "trend_direction": trend,
        "likely_cause": likely_cause,
        "recommended_action": recommended_action,
        "action_reasoning": action_reasoning,
        "should_reforecast": should_reforecast,
        "confidence": 0.85 if len(weekly_variances) >= 3 else 0.70,
        "explanation": explanation,
        "weekly_variances": weekly_variances,
        "weeks_remaining": weeks_remaining,
    }


def _display_variance_analysis(analysis: dict, params: WorkflowParams, selected_week: int):
    """Display the variance analysis results."""

    # Severity badge
    severity_colors = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }
    severity = analysis.get("severity", "medium")
    severity_icon = severity_colors.get(severity, "⚪")

    st.markdown(f"### {severity_icon} Analysis: **{severity.upper()}** Severity")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Variance", f"{analysis['variance_pct']:+.1f}%")
    with col2:
        trend = analysis.get("trend_direction", "stable")
        st.metric("Trend", trend.title())
    with col3:
        st.metric("Confidence", f"{analysis.get('confidence', 0.75):.0%}")
    with col4:
        action_icons = {
            "continue": "✅",
            "reforecast": "🔄",
            "reallocate": "📦",
            "markdown": "💰",
            "investigate": "🔍"
        }
        action = analysis.get("recommended_action", "continue")
        icon = action_icons.get(action, "❓")
        st.metric("Action", f"{icon} {action.title()}")

    # Likely cause
    st.markdown("---")
    st.markdown("#### 🔍 Likely Cause")
    st.info(analysis.get("likely_cause", "Unknown"))

    # Analysis reasoning
    st.markdown("#### 💭 Analysis")
    st.markdown(analysis.get("explanation", ""))

    # Action recommendation box
    st.markdown("#### 🎯 Recommended Action")
    action = analysis.get("recommended_action", "continue")
    action_reasoning = analysis.get("action_reasoning", "")

    if action == "continue":
        st.success(f"**{action.upper()}**: {action_reasoning}")
    elif action == "reforecast":
        st.warning(f"**{action.upper()}**: {action_reasoning}")
    elif action == "markdown":
        st.warning(f"**{action.upper()}**: {action_reasoning}")
    else:
        st.info(f"**{action.upper()}**: {action_reasoning}")


# =============================================================================
# Strategic Replenishment Visualization
# =============================================================================

def _generate_reallocation_data(params: WorkflowParams, selected_week: int, strategy: str) -> dict:
    """Generate reallocation data using real store sales when available.

    Uses REAL per-store velocity calculation when store_actual_sales is available.
    Falls back to estimated distribution when only aggregate data exists.
    """
    if not st.session_state.workflow_result:
        return None

    allocation = st.session_state.workflow_result.allocation
    forecast = st.session_state.workflow_result.forecast
    actual_sales = st.session_state.actual_sales or []
    store_actual_sales = st.session_state.store_actual_sales or {}
    total_weeks = len(forecast.forecast_by_week)
    weeks_remaining = total_weeks - selected_week

    # Check if we have real per-store data
    has_real_store_data = len(store_actual_sales) > 0

    # Calculate overall variance from actual uploaded data
    if actual_sales and len(actual_sales) > 0:
        total_forecast = sum(forecast.forecast_by_week[:len(actual_sales)])
        total_actual = sum(actual_sales)
        overall_variance = (total_actual - total_forecast) / total_forecast if total_forecast > 0 else 0

        # Calculate week-over-week trend
        if len(actual_sales) >= 2:
            recent_forecast = forecast.forecast_by_week[len(actual_sales)-1]
            recent_actual = actual_sales[-1]
            recent_variance = (recent_actual - recent_forecast) / recent_forecast if recent_forecast > 0 else 0
        else:
            recent_variance = overall_variance
    else:
        overall_variance = 0
        recent_variance = 0

    # Generate store performance data
    store_performances = []
    high_performers = []
    underperformers = []
    on_target = []

    for store_alloc in allocation.store_allocations:
        store_id = store_alloc.store_id
        allocated = store_alloc.allocation_units
        cluster = store_alloc.cluster

        # Get actual sales for this store
        if has_real_store_data and store_id in store_actual_sales:
            # REAL DATA: sum sales up to selected_week
            store_sales_list = store_actual_sales[store_id]
            store_sold = sum(store_sales_list[:selected_week])
        else:
            # ESTIMATED: distribute total proportionally
            total_sold = st.session_state.total_sold or 0
            total_allocated = allocation.initial_store_allocation
            if total_allocated > 0:
                store_sold = int(total_sold * (allocated / total_allocated))
            else:
                store_sold = 0

        # Calculate velocity = (actual/allocated) / (expected_fraction)
        if allocated > 0 and selected_week > 0:
            expected_fraction = selected_week / total_weeks
            expected_sold = allocated * expected_fraction
            velocity = store_sold / expected_sold if expected_sold > 0 else 1.0
        else:
            velocity = 1.0

        velocity = max(0.3, min(2.0, velocity))  # Clamp to realistic range

        # Calculate remaining and weeks of supply
        remaining = max(0, allocated - store_sold)
        weekly_rate = store_sold / selected_week if selected_week > 0 else 0
        weeks_of_supply = remaining / weekly_rate if weekly_rate > 0 else 99

        status = "needs_more" if velocity > 1.15 else "excess" if velocity < 0.85 else "on_target"

        perf = {
            "store_id": store_id,
            "cluster": cluster,
            "allocated": allocated,
            "sold": store_sold,
            "remaining": remaining,
            "velocity": round(velocity, 2),
            "weeks_of_supply": round(min(weeks_of_supply, 99), 1),
            "status": status,
        }
        store_performances.append(perf)

        if status == "needs_more":
            high_performers.append(perf)
        elif status == "excess":
            underperformers.append(perf)
        else:
            on_target.append(perf)

    # ==========================================================================
    # DYNAMIC TRANSFER LOGIC
    # - Variance-proportional: bigger gaps = bigger transfers
    # - Time-sensitive: more aggressive as season progresses
    # - Velocity-weighted: high-velocity stores get proportionally more
    # ==========================================================================

    transfers = []
    dc_released = 0

    # Calculate URGENCY FACTOR based on time remaining (0.5 to 1.5)
    # Early season (week 1-3): conservative (0.5-0.7)
    # Mid season (week 4-8): moderate (0.8-1.0)
    # Late season (week 9+): aggressive (1.1-1.5)
    season_progress = selected_week / total_weeks if total_weeks > 0 else 0
    urgency_factor = 0.5 + (season_progress * 1.0)  # Ranges from 0.5 to 1.5

    # Calculate VARIANCE SEVERITY multiplier (1.0 to 2.0)
    # Higher variance = more aggressive rebalancing
    variance_severity = 1.0 + min(abs(overall_variance), 0.5) * 2  # Max 2.0x at 50%+ variance

    # Sort high performers by velocity (highest first) - take more stores later in season
    max_high_perf = min(3 + int(season_progress * 4), 7)  # 3-7 stores based on progress
    high_performers_sorted = sorted(high_performers, key=lambda x: x["velocity"], reverse=True)[:max_high_perf]

    # Calculate total velocity weight for proportional distribution
    total_velocity_weight = sum(max(0, p["velocity"] - 1.0) for p in high_performers_sorted)

    if strategy == "dc_only":
        # DC-only transfers - DYNAMIC release based on urgency and variance
        # Base: 30% of DC, scales up to 70% based on urgency and variance
        base_release_pct = 0.30
        dynamic_release_pct = base_release_pct + (0.40 * urgency_factor * (variance_severity - 1.0))
        dynamic_release_pct = min(dynamic_release_pct, 0.70)  # Cap at 70%

        available = int(allocation.dc_holdback * dynamic_release_pct)

        for perf in high_performers_sorted:
            if available < 50:
                break

            # VELOCITY-WEIGHTED distribution
            velocity_excess = max(0, perf["velocity"] - 1.0)  # How much above target
            if total_velocity_weight > 0:
                store_share = velocity_excess / total_velocity_weight
            else:
                store_share = 1.0 / max(len(high_performers_sorted), 1)

            # Calculate units based on share, urgency, and store's remaining capacity
            base_units = int(available * store_share)

            # Scale by urgency (more aggressive later)
            urgency_adjusted = int(base_units * urgency_factor)

            # Cap based on store's weeks of supply need
            if perf["weeks_of_supply"] < weeks_remaining:
                supply_gap_weeks = weeks_remaining - perf["weeks_of_supply"]
                weekly_rate = perf["sold"] / selected_week if selected_week > 0 else 0
                supply_gap_units = int(supply_gap_weeks * weekly_rate * 0.5)  # Fill 50% of gap
                units = min(urgency_adjusted, supply_gap_units, available, 800)
            else:
                units = min(urgency_adjusted, available, 400)

            units = max(units, 50) if units >= 30 else 0  # Minimum viable transfer

            if units > 0:
                # Dynamic priority based on velocity AND weeks of supply
                if perf["velocity"] > 1.4 or perf["weeks_of_supply"] < 2:
                    priority = "high"
                elif perf["velocity"] > 1.2 or perf["weeks_of_supply"] < 4:
                    priority = "medium"
                else:
                    priority = "low"

                transfers.append({
                    "from": "DC",
                    "to": perf["store_id"],
                    "units": units,
                    "priority": priority,
                    "reason": f"Velocity {perf['velocity']:.2f}x, {perf['weeks_of_supply']:.1f} wks supply"
                })
                dc_released += units
                available -= units

    elif strategy == "hybrid":
        # Hybrid: DC transfers + store-to-store rebalancing

        # DC portion (slightly less than dc_only since we also do store transfers)
        base_release_pct = 0.25
        dynamic_release_pct = base_release_pct + (0.30 * urgency_factor * (variance_severity - 1.0))
        dynamic_release_pct = min(dynamic_release_pct, 0.55)

        available = int(allocation.dc_holdback * dynamic_release_pct)

        # DC to top performers (velocity-weighted)
        for perf in high_performers_sorted[:4]:
            if available < 50:
                break

            velocity_excess = max(0, perf["velocity"] - 1.0)
            if total_velocity_weight > 0:
                store_share = velocity_excess / total_velocity_weight
            else:
                store_share = 0.25

            base_units = int(available * store_share * 1.5)  # Concentrate on fewer stores
            urgency_adjusted = int(base_units * urgency_factor)
            units = min(urgency_adjusted, available, 600)
            units = max(units, 50) if units >= 30 else 0

            if units > 0:
                priority = "high" if perf["velocity"] > 1.3 else "medium"
                transfers.append({
                    "from": "DC",
                    "to": perf["store_id"],
                    "units": units,
                    "priority": priority,
                    "reason": f"Velocity {perf['velocity']:.2f}x, {perf['weeks_of_supply']:.1f} wks supply"
                })
                dc_released += units
                available -= units

        # Store-to-store transfers (from underperformers to high performers)
        underperformers_sorted = sorted(underperformers, key=lambda x: x["velocity"])[:5]

        for under in underperformers_sorted:
            # Find best recipient (highest velocity that hasn't received store transfer)
            recipients = [p for p in high_performers_sorted
                         if not any(t["to"] == p["store_id"] and t["from"] != "DC" for t in transfers)]
            if not recipients:
                recipients = high_performers_sorted[:2]

            if not recipients:
                break

            high = max(recipients, key=lambda x: x["velocity"])

            # Calculate transfer based on underperformer's excess inventory
            velocity_deficit = max(0, 1.0 - under["velocity"])  # How much below target
            excess_inventory = int(under["remaining"] * velocity_deficit * urgency_factor)

            # Also consider high performer's need
            high_need = int((high["velocity"] - 1.0) * high["allocated"] * 0.3)

            units = min(excess_inventory, high_need, int(under["remaining"] * 0.4), 500)
            units = max(units, 50) if units >= 30 else 0

            if units > 0:
                velocity_diff = high["velocity"] - under["velocity"]
                priority = "high" if velocity_diff > 0.5 else "medium" if velocity_diff > 0.3 else "low"

                transfers.append({
                    "from": under["store_id"],
                    "to": high["store_id"],
                    "units": units,
                    "priority": priority,
                    "reason": f"Rebalance: {under['velocity']:.2f}x → {high['velocity']:.2f}x (Δ{velocity_diff:.2f})"
                })

    total_units = sum(t["units"] for t in transfers)

    # Confidence based on data quality and variance significance
    weeks_of_data = len(actual_sales)
    variance_magnitude = abs(overall_variance)
    confidence = 0.60 + (min(weeks_of_data, 6) * 0.05)  # 60-90% based on weeks of data
    if variance_magnitude > 0.15:
        confidence += 0.05  # Higher confidence when variance is significant

    # Boost confidence if using real store data
    if has_real_store_data:
        confidence += 0.10

    return {
        "should_reallocate": len(transfers) > 0 and total_units >= 100,
        "strategy": strategy,
        "dc_available": allocation.dc_holdback,
        "dc_released": dc_released,
        "dc_remaining": allocation.dc_holdback - dc_released,
        "transfers": transfers,
        "total_units": total_units,
        "high_performers": [p["store_id"] for p in high_performers],
        "underperformers": [p["store_id"] for p in underperformers],
        "on_target": [p["store_id"] for p in on_target],
        "store_performances": store_performances,
        "weeks_remaining": weeks_remaining,
        "confidence": min(confidence, 0.95),
        # Data quality indicators
        "has_real_store_data": has_real_store_data,
        "overall_variance": overall_variance,
        "recent_variance": recent_variance,
        "weeks_of_data": weeks_of_data,
        "selected_week": selected_week,
        # Dynamic factors (NEW)
        "urgency_factor": urgency_factor,
        "variance_severity": variance_severity,
        "season_progress_pct": season_progress * 100,
    }


def _on_strategy_select(strategy: str):
    """Callback for strategy button selection - avoids double-rerun issues."""
    st.session_state.selected_reallocation_strategy = strategy


def render_strategic_replenishment_section(params: WorkflowParams, selected_week: int):
    """Render the Strategic Replenishment analysis and recommendations."""

    if not st.session_state.workflow_result:
        st.info("Run pre-season workflow first to enable strategic replenishment.")
        return

    if not st.session_state.actual_sales or len(st.session_state.actual_sales) == 0:
        st.info("Upload sales data to enable strategic replenishment analysis.")
        return

    # Strategy selector
    st.markdown("#### 📋 Select Replenishment Strategy")

    col_dc, col_hybrid = st.columns(2)

    with col_dc:
        dc_selected = st.session_state.selected_reallocation_strategy == "dc_only"
        st.button(
            "🏭 DC-to-Store",
            key="strategy_dc",
            type="primary" if dc_selected else "secondary",
            use_container_width=True,
            on_click=_on_strategy_select,
            args=("dc_only",),
        )
        st.caption("Release from DC to high-performers. Simple logistics.")

    with col_hybrid:
        hybrid_selected = st.session_state.selected_reallocation_strategy == "hybrid"
        st.button(
            "🔀 Hybrid (DC + Store)",
            key="strategy_hybrid",
            type="primary" if hybrid_selected else "secondary",
            use_container_width=True,
            on_click=_on_strategy_select,
            args=("hybrid",),
        )
        st.caption("DC release + store-to-store transfers.")

    st.markdown("---")

    # Generate reallocation data (uses real store data when available)
    strategy = st.session_state.selected_reallocation_strategy
    realloc_data = _generate_reallocation_data(params, selected_week, strategy)

    if not realloc_data:
        st.warning("Unable to generate reallocation analysis.")
        return

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "DC Available",
            f"{realloc_data['dc_available']:,}",
            delta="Release recommended" if realloc_data['should_reallocate'] else None,
        )

    with col2:
        st.metric(
            "Units to Move",
            f"{realloc_data['total_units']:,}",
            delta=f"{len(realloc_data['transfers'])} transfers",
        )

    with col3:
        strategy_label = "🏭 DC Only" if strategy == "dc_only" else "🔀 Hybrid"
        st.metric("Strategy", strategy_label)

    with col4:
        st.metric("Confidence", f"{realloc_data['confidence']:.0%}")

    # Sankey-style transfer visualization
    if realloc_data['transfers']:
        st.markdown("#### 📊 Transfer Flow")

        # Build Sankey data
        transfers = realloc_data['transfers']

        # Get unique nodes
        sources = list(set([t['from'] for t in transfers]))
        destinations = list(set([t['to'] for t in transfers]))
        all_nodes = sources + [d for d in destinations if d not in sources]

        # Add stores with no changes (sample)
        on_target_sample = realloc_data['on_target'][:5]
        for store in on_target_sample:
            if store not in all_nodes:
                all_nodes.append(store)

        # Build indices
        source_indices = []
        target_indices = []
        values = []
        colors = []

        priority_colors = {
            "high": "rgba(231, 76, 60, 0.6)",
            "medium": "rgba(241, 196, 15, 0.6)",
            "low": "rgba(46, 204, 113, 0.6)",
        }

        for t in transfers:
            source_indices.append(all_nodes.index(t['from']))
            target_indices.append(all_nodes.index(t['to']))
            values.append(t['units'])
            colors.append(priority_colors.get(t['priority'], "rgba(149, 165, 166, 0.6)"))

        # Add dim flows for no-change stores
        for store in on_target_sample:
            if "DC" in all_nodes:
                source_indices.append(all_nodes.index("DC"))
                target_indices.append(all_nodes.index(store))
                values.append(50)  # Small representative flow
                colors.append("rgba(149, 165, 166, 0.2)")

        # Node colors
        node_colors = []
        for node in all_nodes:
            if node == "DC":
                node_colors.append("#3498db")
            elif node in [t['to'] for t in transfers]:
                node_colors.append("#2ecc71")
            elif node in [t['from'] for t in transfers if t['from'] != "DC"]:
                node_colors.append("#e74c3c")
            else:
                node_colors.append("#95a5a6")

        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=node_colors,
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=colors,
            )
        )])

        fig_sankey.update_layout(
            title=f"Inventory Transfer Flow - {strategy.replace('_', ' ').title()} Strategy",
            font_size=12,
            height=400,
        )

        st.plotly_chart(fig_sankey, use_container_width=True)

        # Legend
        leg_cols = st.columns(4)
        with leg_cols[0]:
            st.caption("🔵 Distribution Center")
        with leg_cols[1]:
            st.caption("🟢 Receiving (needs more)")
        with leg_cols[2]:
            st.caption("🔴 Sending (excess)")
        with leg_cols[3]:
            st.caption("⚪ No Change")

    # Two columns: Performance chart + Transfer table
    col_perf, col_table = st.columns([1.5, 1])

    with col_perf:
        st.markdown("#### 🌡️ Store Velocity")

        # Get sample of stores for visualization
        sample_perfs = realloc_data['store_performances'][:12]
        stores = [p['store_id'] for p in sample_perfs]
        velocities = [p['velocity'] for p in sample_perfs]
        colors_bar = ['#2ecc71' if v > 1.15 else '#e74c3c' if v < 0.85 else '#95a5a6' for v in velocities]

        fig_perf = go.Figure(data=[
            go.Bar(
                x=stores,
                y=velocities,
                marker_color=colors_bar,
                text=[f"{v:.2f}x" for v in velocities],
                textposition='outside',
            )
        ])

        fig_perf.add_hline(y=1.0, line_dash="dash", line_color="gray",
                          annotation_text="Target", annotation_position="right")

        fig_perf.update_layout(
            xaxis_title="Store",
            yaxis_title="Velocity",
            height=300,
            margin=dict(t=20, b=50),
            yaxis=dict(range=[0, max(velocities) * 1.2]),
        )

        st.plotly_chart(fig_perf, use_container_width=True)

    with col_table:
        st.markdown("#### 📋 Transfer Orders")

        if realloc_data['transfers']:
            transfer_df = pd.DataFrame([
                {
                    "From": t['from'],
                    "To": t['to'],
                    "Units": t['units'],
                    "Priority": t['priority'].upper(),
                }
                for t in realloc_data['transfers']
            ])

            st.dataframe(
                transfer_df,
                column_config={
                    "From": st.column_config.TextColumn("From", width="small"),
                    "To": st.column_config.TextColumn("To", width="small"),
                    "Units": st.column_config.NumberColumn("Units", format="%d"),
                    "Priority": st.column_config.TextColumn("Priority", width="small"),
                },
                hide_index=True,
                use_container_width=True,
                height=280,
            )
        else:
            st.info("No transfers recommended.")

    # Agent explanation (using container instead of expander to avoid nesting)
    st.markdown("---")
    st.markdown("#### 🤖 Agent Analysis")

    # Show data source indicator
    has_real_data = realloc_data.get('has_real_store_data', False)
    if has_real_data:
        st.success("✅ **Using REAL per-store sales data** from uploaded CSVs")
    else:
        st.info("📊 Using estimated store-level data (proportional distribution)")

    # Show variance-driven insights
    overall_var = realloc_data.get('overall_variance', 0)
    recent_var = realloc_data.get('recent_variance', 0)
    weeks_data = realloc_data.get('weeks_of_data', 0)

    var_trend = "improving" if recent_var > overall_var else "worsening" if recent_var < overall_var else "stable"
    var_direction = "overperforming" if overall_var > 0 else "underperforming" if overall_var < 0 else "on target"

    # Get dynamic factors
    urgency = realloc_data.get('urgency_factor', 1.0)
    var_severity = realloc_data.get('variance_severity', 1.0)
    season_pct = realloc_data.get('season_progress_pct', 0)

    # Determine urgency label
    if urgency < 0.7:
        urgency_label = "🟢 Conservative (early season)"
    elif urgency < 1.0:
        urgency_label = "🟡 Moderate (mid season)"
    else:
        urgency_label = "🔴 Aggressive (late season)"

    st.markdown(f"""
**Week {realloc_data.get('selected_week', selected_week)} Analysis** (based on {weeks_data} weeks of data)

**📊 Dynamic Factors:**
- Season Progress: **{season_pct:.0f}%** ({realloc_data['weeks_remaining']} weeks remaining)
- Urgency Level: **{urgency:.2f}x** {urgency_label}
- Variance Severity: **{var_severity:.2f}x** multiplier

**📈 Variance Summary:**
- Overall Variance: **{overall_var:+.1%}** ({var_direction})
- Recent Trend: **{recent_var:+.1%}** ({var_trend})

**🏪 Store Performance:**
- High Performers (need more): **{len(realloc_data['high_performers'])}** stores
- Underperformers (excess): **{len(realloc_data['underperformers'])}** stores
- On Target: **{len(realloc_data['on_target'])}** stores

**💡 Strategy:** {strategy.replace('_', ' ').title()}

**🎯 Recommendation:**
{"✅ Strategic replenishment recommended - transfers sized by velocity differential and urgency." if realloc_data['should_reallocate'] else "⏸️ No significant reallocation needed at this time."}

**Expected Impact:**
- Reduce stockout risk at high-velocity stores
- {"Rebalance inventory from slow to fast movers" if strategy == "hybrid" else "Release DC holdback to high-demand stores"}
- Transfer amounts scaled by: velocity gap × urgency × variance severity
    """)

    # Action buttons
    st.markdown("---")
    col_approve, col_skip = st.columns(2)

    with col_approve:
        if st.button(
            "✅ Approve Transfers",
            key=f"approve_realloc_{selected_week}",
            type="primary",
            use_container_width=True,
            disabled=not realloc_data['should_reallocate'],
        ):
            st.success(f"Approved {len(realloc_data['transfers'])} transfers ({realloc_data['total_units']:,} units)")
            st.session_state.reallocation_result = realloc_data

    with col_skip:
        if st.button(
            "⏭️ Skip Replenishment",
            key=f"skip_realloc_{selected_week}",
            use_container_width=True,
        ):
            st.info("Strategic replenishment skipped for this week.")


def render_week_sections(params: WorkflowParams, selected_week: int, week_info: dict):
    """Render the variance, reallocation, and pricing sections for a week."""
    markdown_week = params.markdown_week

    # ==========================================================================
    # VARIANCE PARAMETERS - Show ONLY after sales uploaded for this week
    # ==========================================================================
    if is_variance_unlocked(selected_week):
        # Show variance parameters (user can adjust threshold)
        variance_threshold = render_variance_parameters()
        # Update params with user-selected values
        params = WorkflowParams(
            category=params.category,
            forecast_horizon_weeks=params.forecast_horizon_weeks,
            season_start_date=params.season_start_date,
            dc_holdback_pct=params.dc_holdback_pct,
            safety_stock_pct=params.safety_stock_pct,
            replenishment_strategy=params.replenishment_strategy,
            markdown_week=params.markdown_week,
            markdown_threshold=params.markdown_threshold,
            elasticity=params.elasticity,
            variance_threshold=variance_threshold,
            max_reforecasts=2,  # Default value
        )
    else:
        # Show locked variance section
        render_locked_section(
            "Variance Settings",
            "📉",
            f"Upload Week {selected_week} sales data to unlock variance analysis"
        )

    st.markdown("")  # Spacer

    # Section 2: Variance Analysis (Always Agentic)
    with st.expander("📉 2. Variance Analysis", expanded=True):
        if week_info["actual_sales"] is not None and st.session_state.workflow_result:
            # Calculate and show variance metrics
            forecast_val = st.session_state.workflow_result.forecast.forecast_by_week[selected_week - 1]
            actual_val = week_info["actual_sales"]
            variance_pct = (actual_val - forecast_val) / forecast_val if forecast_val > 0 else 0
            is_high_variance = abs(variance_pct) > params.variance_threshold

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Forecast", f"{forecast_val:,}")
            with col2:
                st.metric("Actual", f"{actual_val:,}")
            with col3:
                delta_color = "inverse" if is_high_variance else "normal"
                st.metric(
                    "Variance",
                    f"{variance_pct:+.1%}",
                    delta="High" if is_high_variance else "OK",
                    delta_color=delta_color,
                )

            # ALWAYS show visualization (forecast vs actual chart)
            _render_variance_chart(params, selected_week)

            # AGENTIC MODE: Always use intelligent analysis
            _render_agentic_variance_analysis(params, selected_week, variance_pct, is_high_variance)
        else:
            st.info("Upload sales data to see variance analysis.")

            # Show forecast-only chart if we have a forecast
            if st.session_state.workflow_result:
                _render_forecast_only_chart(params)

    # Section 3: Strategic Replenishment
    with st.expander("🔄 3. Strategic Replenishment", expanded=False):
        render_strategic_replenishment_section(params, selected_week)

    # ==========================================================================
    # MARKDOWN PARAMETERS - Show ONLY at/after markdown checkpoint week
    # ==========================================================================
    is_pricing_available = is_markdown_unlocked(selected_week, markdown_week)

    st.markdown("")  # Spacer

    if is_pricing_available:
        # Show markdown parameters (user can adjust sell-through target/elasticity)
        markdown_threshold, elasticity = render_markdown_parameters()
        # Update params with user-selected values
        params = WorkflowParams(
            category=params.category,
            forecast_horizon_weeks=params.forecast_horizon_weeks,
            season_start_date=params.season_start_date,
            dc_holdback_pct=params.dc_holdback_pct,
            safety_stock_pct=params.safety_stock_pct,
            replenishment_strategy=params.replenishment_strategy,
            markdown_week=params.markdown_week,
            markdown_threshold=markdown_threshold,
            elasticity=elasticity,
            variance_threshold=params.variance_threshold,
            max_reforecasts=params.max_reforecasts,
        )
    else:
        # Show locked markdown section
        weeks_until = markdown_week - selected_week
        render_locked_section(
            "Markdown Settings",
            "💰",
            f"Available at Week {markdown_week} ({weeks_until} week(s) until markdown checkpoint)"
        )

    st.markdown("")  # Spacer

    # Section 4: Pricing Agent (only at/after markdown checkpoint)
    with st.expander(
        f"💰 4. Markdown Command Center {'🔓' if is_pricing_available else '🔒 (Week ' + str(markdown_week) + '+)'}",
        expanded=is_pricing_available,  # Auto-expand when available
    ):
        if is_pricing_available:
            # Show current sell-through if we have data
            if st.session_state.workflow_result and st.session_state.total_sold > 0:
                allocation = st.session_state.workflow_result.allocation
                sell_through = st.session_state.total_sold / allocation.initial_store_allocation

                # Use the enhanced Markdown Command Center (Solution A)
                render_markdown_command_center(
                    params=params,
                    current_sell_through=sell_through,
                    total_sold=st.session_state.total_sold,
                    total_allocated=allocation.initial_store_allocation,
                    current_week=selected_week,
                )
            else:
                st.info("📊 Run pre-season workflow and enter sales data to enable the Markdown Command Center.")
                st.caption("The pricing agent needs actual sales data to calculate optimal markdown recommendations.")
        else:
            st.info(f"🔒 Markdown Command Center unlocks at Week {markdown_week} (Markdown Checkpoint)")
            weeks_until = markdown_week - selected_week
            st.caption(f"{weeks_until} week(s) until pricing tools available")

            # Show a preview of what's coming
            with st.container():
                st.markdown("**Coming at Week {}:**".format(markdown_week))
                st.markdown("""
                - 📊 Interactive markdown scenario comparison
                - 📈 Sell-through trajectory visualization
                - 💵 Revenue vs margin tradeoff analysis
                - ✨ Forecast impact preview
                - 🤖 AI-powered pricing recommendations
                """)


def render_inseason_planning(params: WorkflowParams):
    """Render the complete in-season planning interface with timeline."""

    # Check if we have a pre-season forecast
    if st.session_state.workflow_result is None:
        st.warning(
            "⚠️ No pre-season forecast available. Please complete pre-season planning first."
        )
        if st.button("↩️ Go to Pre-Season", key="goto_preseason"):
            st.session_state.planning_mode = "pre-season"
            st.rerun()
        return

    # Auto-initialize in-season from pre-season params (no setup page needed)
    if not st.session_state.inseason_setup_complete:
        # Inherit total_season_weeks from forecast_horizon
        st.session_state.total_season_weeks = params.forecast_horizon_weeks
        # Inherit season_start_date from pre-season params
        st.session_state.season_start_date = params.season_start_date
        st.session_state.inseason_setup_complete = True
        st.session_state.selected_week = 1
        st.rerun()

    # Season header with key metrics
    st.markdown(f"## 📅 In-Season: {params.category}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Season Week", f"{st.session_state.current_week} of {st.session_state.total_season_weeks}")
    with col2:
        st.metric("Total Sold", f"{st.session_state.total_sold:,}" if st.session_state.total_sold > 0 else "—")
    with col3:
        if st.session_state.workflow_result and st.session_state.total_sold > 0:
            allocation = st.session_state.workflow_result.allocation
            sell_through = st.session_state.total_sold / allocation.initial_store_allocation
            st.metric("Sell-Through", f"{sell_through:.1%}")
        else:
            st.metric("Sell-Through", "—")
    with col4:
        st.metric("Markdown Week", f"Week {params.markdown_week}")

    st.divider()

    # ==========================================================================
    # OPERATIONAL PARAMETERS - Always visible in In-Season (moved from Pre-Season)
    # ==========================================================================
    replenishment, markdown_week = render_operational_parameters(params.forecast_horizon_weeks)

    # Update params with user-selected operational values
    params = WorkflowParams(
        category=params.category,
        forecast_horizon_weeks=params.forecast_horizon_weeks,
        season_start_date=params.season_start_date,
        dc_holdback_pct=params.dc_holdback_pct,
        safety_stock_pct=params.safety_stock_pct,
        replenishment_strategy=replenishment,
        markdown_week=markdown_week,
        markdown_threshold=params.markdown_threshold,
        elasticity=params.elasticity,
        variance_threshold=params.variance_threshold,
        max_reforecasts=params.max_reforecasts,
    )

    st.divider()

    # Render the timeline
    render_timeline(params)

    # Render the week workspace
    render_week_workspace(params)


# =============================================================================
# Data Upload Section
# =============================================================================
def render_data_upload():
    """Render the data upload section."""
    st.subheader("📁 Data Management")

    # Get the data directory path
    data_dir = st.session_state.data_loader.data_dir

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Historical Sales Data")
        st.markdown(
            """
            Upload historical sales data for forecasting.

            **Required Columns:**
            - `date` - Date (YYYY-MM-DD)
            - `store_id` - Store identifier
            - `category` - Product category
            - `quantity_sold` - Units sold
            """
        )

        sales_file = st.file_uploader(
            "Upload historical sales CSV",
            type=["csv"],
            key="sales_upload",
            help="CSV with columns: date, store_id, category, quantity_sold",
        )
        if sales_file is not None:
            try:
                # Read and validate the file
                preview_df = pd.read_csv(sales_file)
                required_cols = ["date", "store_id", "category", "quantity_sold"]
                missing_cols = [c for c in required_cols if c not in preview_df.columns]

                if missing_cols:
                    st.error(f"Missing required columns: {missing_cols}")
                else:
                    st.success(f"✅ Valid file: {sales_file.name} ({len(preview_df):,} rows)")
                    st.dataframe(preview_df.head(10), use_container_width=True)

                    # Save button
                    if st.button("💾 Apply Sales Data", key="apply_sales_btn"):
                        # Save to data directory
                        save_path = data_dir / "historical_sales_2022_2024.csv"
                        sales_file.seek(0)  # Reset file pointer
                        preview_df.to_csv(save_path, index=False)

                        # Update data loader and clear old results
                        st.session_state.data_loader.clear_cache()
                        st.session_state.workflow_result = None
                        st.session_state.flow_state["preseason_complete"] = False
                        st.success(f"✅ Sales data saved and loaded!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with col2:
        st.markdown("### Store Attributes Data")
        st.markdown(
            """
            Upload store attributes for clustering.

            **Required Columns:**
            - `store_id` - Store identifier
            - `avg_weekly_sales_12mo` - Average weekly sales
            - `store_size_sqft` - Store size
            - `median_income` - Area median income
            - `location_tier` - A/B/C tier
            - `fashion_tier` - Premium/Mainstream/Value
            - `store_format` - Mall/Standalone/etc.
            - `region` - Geographic region
            """
        )

        stores_file = st.file_uploader(
            "Upload store attributes CSV",
            type=["csv"],
            key="stores_upload",
            help="CSV with store attribute columns",
        )
        if stores_file is not None:
            try:
                # Read and validate the file
                preview_df = pd.read_csv(stores_file)
                required_cols = ["store_id", "avg_weekly_sales_12mo", "store_size_sqft"]
                missing_cols = [c for c in required_cols if c not in preview_df.columns]

                if missing_cols:
                    st.error(f"Missing required columns: {missing_cols}")
                else:
                    st.success(f"✅ Valid file: {stores_file.name} ({len(preview_df):,} rows)")
                    st.dataframe(preview_df.head(10), use_container_width=True)

                    # Save button
                    if st.button("💾 Apply Store Data", key="apply_stores_btn"):
                        # Save to data directory
                        save_path = data_dir / "store_attributes.csv"
                        stores_file.seek(0)  # Reset file pointer
                        preview_df.to_csv(save_path, index=False)

                        # Update data loader and clear old results
                        st.session_state.data_loader.clear_cache()
                        st.session_state.workflow_result = None
                        st.session_state.flow_state["preseason_complete"] = False
                        st.success(f"✅ Store data saved and loaded!")
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

    st.divider()

    # Show available data summary
    st.markdown("### Current Training Data")
    summary = st.session_state.data_loader.get_context_summary()
    st.markdown(summary)


# =============================================================================
# Main Content
# =============================================================================
async def run_workflow_async(params: WorkflowParams):
    """Run the workflow asynchronously with UI hooks."""
    context = ForecastingContext(
        data_loader=st.session_state.data_loader,
        session_id=st.session_state.session_id,
        season_start_date=params.season_start_date,  # Pass for calendar-aligned forecasting
        current_week=st.session_state.current_week,
        actual_sales=st.session_state.actual_sales if st.session_state.actual_sales else None,
        total_sold=st.session_state.total_sold,
    )

    # Create hooks for UI updates
    hooks = WorkflowUIHooks(st.session_state.workflow_state)

    # Start workflow tracking
    st.session_state.workflow_state.start_workflow()

    try:
        if st.session_state.current_week > 0 and st.session_state.actual_sales:
            # Track phase transitions
            st.session_state.workflow_state.start_phase("forecast")
            result = await run_inseason_update(
                context=context,
                params=params,
                current_week=st.session_state.current_week,
                actual_sales=st.session_state.actual_sales,
                total_sold=st.session_state.total_sold,
                hooks=hooks,
            )
        else:
            st.session_state.workflow_state.start_phase("forecast")
            result = await run_preseason_planning(
                context=context,
                params=params,
                hooks=hooks,
            )

        # Mark workflow complete
        st.session_state.workflow_state.end_workflow()
        return result

    except Exception as e:
        st.session_state.workflow_state.end_workflow()
        raise e


def render_preseason_tab():
    """Render the Pre-Season planning tab with restructured layout."""
    st.markdown("## 🌱 Pre-Season Planning")
    st.markdown(
        "Generate demand forecasts and initial inventory allocations before the season begins."
    )

    # Check if pre-season is already complete
    if st.session_state.workflow_result:
        st.success("✅ Pre-season planning complete! View results below or proceed to In-Season tab.")

    # ===========================================================================
    # DATA MANAGEMENT SECTION - At the top for users to upload training data first
    # ===========================================================================
    with st.expander("📁 Data Management - Upload Training Data", expanded=False):
        render_data_upload()

    st.divider()

    # ===========================================================================
    # FORECAST SETTINGS - These require re-running the workflow
    # ===========================================================================
    category, forecast_horizon, season_start_date = render_forecast_settings()

    # Build params for forecast (inventory settings will be applied dynamically later)
    params = WorkflowParams(
        category=category,
        forecast_horizon_weeks=forecast_horizon,
        season_start_date=season_start_date,
        dc_holdback_pct=0.45,  # Default, will be overridden dynamically
        safety_stock_pct=0.20,  # Default, will be overridden dynamically
        replenishment_strategy="weekly",
        markdown_week=min(6, forecast_horizon),
        markdown_threshold=0.60,
        elasticity=2.0,
        variance_threshold=0.20,
        max_reforecasts=2,
    )

    # Check if forecast settings changed (category, horizon, or start date)
    last_params = st.session_state.flow_state.get("last_run_params")
    forecast_settings_changed = False
    if last_params and st.session_state.workflow_result:
        if (last_params.category != category or
            last_params.forecast_horizon_weeks != forecast_horizon or
            last_params.season_start_date != season_start_date):
            forecast_settings_changed = True
            st.warning("⚠️ **Forecast settings have changed.** Click 'Re-run' to update forecast.")

    # ===========================================================================
    # RUN WORKFLOW BUTTON
    # ===========================================================================
    col_action, col_spacer = st.columns([1, 2])

    with col_action:
        button_label = "🔄 Re-run Forecast" if st.session_state.workflow_result else "▶️ Run Forecast"
        run_button = st.button(
            button_label,
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running,
            key="run_preseason_workflow_btn",
        )
        if st.session_state.running:
            st.caption("⏳ Workflow running...")

    if run_button:
        st.toast("🚀 Starting forecast...")
        st.session_state.running = True

        with st.status("Running demand forecast...", expanded=True) as status:
            st.write(f"**Forecasting:** {params.category}, {params.forecast_horizon_weeks} weeks")
            st.write("🔮 Running Demand Agent...")

            try:
                result = asyncio.run(run_workflow_async(params))
                st.session_state.workflow_result = result

                # Mark pre-season as complete and save params
                mark_preseason_complete()
                save_run_params(params)

                st.write("📦 Running Inventory Agent...")
                st.write("✅ Forecast complete!")
                status.update(
                    label="✅ Forecast complete!",
                    state="complete",
                    expanded=False,
                )
                st.toast("✅ Forecast complete!")
            except Exception as e:
                status.update(label=f"❌ Error: {e}", state="error")
                st.error(f"Workflow failed: {e}")
                import traceback
                st.code(traceback.format_exc())
            finally:
                st.session_state.running = False
                st.rerun()

    # ===========================================================================
    # RESULTS SECTION (only shown after forecast is complete)
    # ===========================================================================
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        last_params = st.session_state.flow_state.get("last_run_params")

        st.divider()
        st.markdown("### 📊 Forecast Results")

        # Show forecast params
        if last_params:
            st.caption(f"Forecast for: {last_params.category} | "
                      f"Horizon: {last_params.forecast_horizon_weeks} weeks")

        # Forecast section
        render_forecast_section(
            result.forecast,
            params,
            actual_sales=None,  # No actuals in pre-season
        )

        st.divider()

        # ===========================================================================
        # INVENTORY SETTINGS - Dynamic allocation recalculation
        # ===========================================================================
        dc_holdback, safety_stock = render_inventory_settings()

        # Dynamically recalculate allocation based on current slider values
        dynamic_allocation = recalculate_allocation_dynamic(
            result.forecast,
            dc_holdback,
            safety_stock
        )

        # Update params for downstream use
        params.dc_holdback_pct = dc_holdback
        params.safety_stock_pct = safety_stock

        st.divider()

        # Allocation section with dynamically recalculated values
        st.markdown("### 📦 Allocation Results")
        st.caption(f"Manufacturing: {dynamic_allocation.manufacturing_qty:,} units | "
                  f"DC Holdback: {dc_holdback:.0%} | Safety Stock: {safety_stock:.0%}")

        render_allocation_section(dynamic_allocation)

    return params  # Return params for use in main


def main():
    """Main application entry point."""
    st.title("📊 Retail Forecasting Multi-Agent System")
    st.markdown(
        """
        This system uses **3 specialized AI agents** to forecast demand, allocate inventory,
        and optimize pricing for fashion retail.
        """
    )

    # Render sidebar with ONLY agent status (no parameters)
    render_sidebar_agent_status()

    # Two primary tabs - Preseason and In-Season
    tab_preseason, tab_inseason = st.tabs(
        ["🌱 Pre-Season", "📅 In-Season"]
    )

    with tab_preseason:
        # Pre-season tab renders its own parameters and returns them
        params = render_preseason_tab()

    with tab_inseason:
        # Check if In-Season should be locked
        if not is_inseason_unlocked():
            render_locked_section(
                "In-Season Updates",
                "📅",
                "Complete Pre-Season planning first to unlock In-Season updates."
            )
            st.caption("Run the Pre-Season workflow to generate forecasts and allocations before proceeding.")
        else:
            # Get params from pre-season (use stored params or create default)
            if st.session_state.workflow_result:
                # Use the params from the last run
                stored_params = st.session_state.flow_state.get("last_run_params")
                if stored_params:
                    render_inseason_planning(stored_params)
                else:
                    # Fallback: create default params with pre-season results
                    categories = st.session_state.data_loader.get_categories()
                    default_params = WorkflowParams(
                        category=categories[0] if categories else "Women's Dresses",
                        forecast_horizon_weeks=12,
                        season_start_date=date.today(),
                        dc_holdback_pct=0.45,
                        safety_stock_pct=0.20,
                        replenishment_strategy="weekly",
                        markdown_week=6,
                        markdown_threshold=0.60,
                        elasticity=2.0,
                        variance_threshold=0.20,
                        max_reforecasts=2,
                    )
                    render_inseason_planning(default_params)
            else:
                st.info("Pre-season results not found. Please run pre-season planning first.")


if __name__ == "__main__":
    main()
