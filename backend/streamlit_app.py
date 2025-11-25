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
from workflows.season_workflow import (
    run_full_season,
    run_preseason_planning,
    run_inseason_update,
)
from agent_tools.variance_tools import check_variance


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


init_session_state()


# =============================================================================
# Sidebar - Parameters
# =============================================================================
def render_sidebar():
    """Render the sidebar with workflow parameters."""
    st.sidebar.title("📊 Workflow Parameters")

    # Category selection
    categories = st.session_state.data_loader.get_categories()
    category = st.sidebar.selectbox(
        "Product Category",
        options=categories,
        index=0 if categories else None,
        help="Select the product category to forecast",
    )

    st.sidebar.divider()

    # Forecast parameters
    st.sidebar.subheader("🔮 Forecast Settings")
    forecast_horizon = st.sidebar.slider(
        "Forecast Horizon (weeks)",
        min_value=4,
        max_value=52,
        value=12,
        help="Number of weeks to forecast",
    )

    season_start = st.sidebar.date_input(
        "Season Start Date",
        value=date.today(),
        help="Start date for the season",
    )

    st.sidebar.divider()

    # Inventory parameters
    st.sidebar.subheader("📦 Inventory Settings")
    dc_holdback = st.sidebar.slider(
        "DC Holdback %",
        min_value=0.20,
        max_value=0.60,
        value=0.45,
        step=0.05,
        format="%.0f%%",
        help="Percentage to hold at Distribution Center",
    )

    safety_stock = st.sidebar.slider(
        "Safety Stock %",
        min_value=0.10,
        max_value=0.50,
        value=0.20,
        step=0.05,
        format="%.0f%%",
        help="Safety stock buffer percentage",
    )

    replenishment = st.sidebar.selectbox(
        "Replenishment Strategy",
        options=["weekly", "bi-weekly", "none"],
        index=0,
        help="How often to replenish stores from DC",
    )

    st.sidebar.divider()

    # Pricing parameters
    st.sidebar.subheader("💰 Pricing Settings")
    markdown_week = st.sidebar.slider(
        "Markdown Checkpoint Week",
        min_value=4,
        max_value=12,
        value=6,
        help="Week to check if markdown is needed",
    )

    markdown_threshold = st.sidebar.slider(
        "Sell-Through Target",
        min_value=0.40,
        max_value=0.80,
        value=0.60,
        step=0.05,
        format="%.0f%%",
        help="Target sell-through rate",
    )

    elasticity = st.sidebar.number_input(
        "Price Elasticity",
        min_value=1.0,
        max_value=4.0,
        value=2.0,
        step=0.5,
        help="Price elasticity factor for markdown calculation",
    )

    st.sidebar.divider()

    # Variance parameters
    st.sidebar.subheader("📉 Variance Settings")
    variance_threshold = st.sidebar.slider(
        "Variance Threshold",
        min_value=0.10,
        max_value=0.40,
        value=0.20,
        step=0.05,
        format="%.0f%%",
        help="Variance threshold to trigger re-forecast",
    )

    max_reforecasts = st.sidebar.slider(
        "Max Re-forecasts",
        min_value=0,
        max_value=5,
        value=2,
        help="Maximum number of re-forecasts allowed",
    )

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
    col1, col2, col3, col4 = st.columns(4)

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
        )

    with col4:
        st.metric(
            label="Safety Stock",
            value=f"{forecast.safety_stock_pct:.0%}",
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
        st.markdown(f"**Data Quality:** {forecast.data_quality}")
        st.info(forecast.explanation)


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
            delta=f"{allocation.dc_holdback_percentage:.0%}",
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

                if st.button(
                    label,
                    key=f"week_btn_{week_num}",
                    use_container_width=True,
                    type=btn_type,
                    help=f"Week {week_num} - {week_info['status'].replace('_', ' ').title()}{' (Markdown Checkpoint)' if week_info['is_markdown_week'] else ''}"
                ):
                    st.session_state.selected_week = week_num
                    st.rerun()

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
                        st.success(f"📊 Loaded {len(df)} rows, Total: **{total_sales:,}** units")

                        # Preview (no nested expander)
                        st.markdown("**Preview:**")
                        st.dataframe(df.head(10), use_container_width=True, height=200)

                        if st.button("💾 Save Week Data", key=f"save_upload_{selected_week}", type="primary", use_container_width=True):
                            _save_week_sales(selected_week, total_sales)
                    else:
                        st.error("CSV must contain 'quantity_sold' column")
                except Exception as e:
                    st.error(f"Error reading file: {e}")

        else:
            st.info("Complete previous weeks to unlock this week.")

    # Render remaining sections (Variance, Reallocation, Pricing)
    render_week_sections(params, selected_week, week_info)


def _save_week_sales(week_num: int, sales_value: int):
    """Helper to save week sales data and update session state."""
    # Save to week_data
    if week_num not in st.session_state.week_data:
        st.session_state.week_data[week_num] = {}
    st.session_state.week_data[week_num]["actual_sales"] = sales_value

    # Update current_week
    st.session_state.current_week = max(st.session_state.current_week, week_num)

    # Rebuild actual_sales list
    actual_sales_list = []
    for w in range(1, st.session_state.total_season_weeks + 1):
        wd = st.session_state.week_data.get(w, {})
        if wd.get("actual_sales") is not None:
            actual_sales_list.append(wd.get("actual_sales", 0))

    st.session_state.actual_sales = actual_sales_list
    st.session_state.total_sold = sum(actual_sales_list)

    st.rerun()


def render_week_sections(params: WorkflowParams, selected_week: int, week_info: dict):
    """Render the variance, reallocation, and pricing sections for a week."""
    markdown_week = params.markdown_week

    # Section 2: Variance Analysis
    with st.expander("📉 2. Variance Analysis", expanded=False):
        if week_info["actual_sales"] is not None and st.session_state.workflow_result:
            # Calculate and show variance
            forecast_val = st.session_state.workflow_result.forecast.forecast_by_week[selected_week - 1]
            actual_val = week_info["actual_sales"]
            variance_pct = (actual_val - forecast_val) / forecast_val if forecast_val > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Forecast", f"{forecast_val:,}")
            with col2:
                st.metric("Actual", f"{actual_val:,}")
            with col3:
                delta_color = "inverse" if abs(variance_pct) > params.variance_threshold else "normal"
                st.metric(
                    "Variance",
                    f"{variance_pct:+.1%}",
                    delta="High" if abs(variance_pct) > params.variance_threshold else "OK",
                    delta_color=delta_color,
                )

            if abs(variance_pct) > params.variance_threshold:
                st.error(f"⚠️ High variance detected! Exceeds {params.variance_threshold:.0%} threshold.")
                st.info("Consider re-forecasting with updated data.")
        else:
            st.info("Upload sales data to see variance analysis.")

    # Section 3: Reallocation Recommendations
    with st.expander("🔄 3. Reallocation", expanded=False):
        if week_info["actual_sales"] is not None:
            st.markdown("Based on sales performance, consider these adjustments:")
            st.info("Reallocation recommendations will appear here based on variance analysis.")
        else:
            st.info("Complete sales data entry to see reallocation recommendations.")

    # Section 4: Pricing Agent (only at/after markdown checkpoint)
    is_pricing_available = selected_week >= markdown_week
    with st.expander(
        f"💰 4. Pricing Agent {'🔓' if is_pricing_available else '🔒 (Week ' + str(markdown_week) + '+)'}",
        expanded=False,
    ):
        if is_pricing_available:
            st.success("✅ Pricing Agent is available!")

            # Show current sell-through if we have data
            if st.session_state.workflow_result and st.session_state.total_sold > 0:
                allocation = st.session_state.workflow_result.allocation
                sell_through = st.session_state.total_sold / allocation.initial_store_allocation
                st.metric("Current Sell-Through", f"{sell_through:.1%}")
                st.metric("Target Sell-Through", f"{params.markdown_threshold:.0%}")

                gap = params.markdown_threshold - sell_through
                if gap > 0:
                    st.warning(f"⚠️ Behind target by {gap:.1%}")
                    if st.button("🏷️ Calculate Markdown Recommendation", key=f"calc_markdown_{selected_week}"):
                        st.info("Markdown calculation would run here...")
                else:
                    st.success("✅ On track or ahead of target!")
            else:
                st.info("Run pre-season workflow and enter sales data to enable pricing recommendations.")
        else:
            st.info(f"🔒 Pricing agent unlocks at Week {markdown_week} (Markdown Checkpoint)")
            weeks_until = markdown_week - selected_week
            st.caption(f"{weeks_until} week(s) until pricing tools available")


def render_inseason_setup(params: WorkflowParams):
    """Render the in-season setup flow for first-time configuration."""
    st.markdown("### 🚀 In-Season Setup")
    st.info("Configure your season before starting in-season planning.")

    col1, col2 = st.columns(2)

    with col1:
        total_weeks = st.number_input(
            "Total Season Weeks",
            min_value=4,
            max_value=52,
            value=st.session_state.total_season_weeks,
            help="How many weeks is this season?",
        )

    with col2:
        start_date = st.date_input(
            "Season Start Date",
            value=st.session_state.season_start_date or date.today(),
            help="When does/did the season start?",
        )

    st.divider()

    # Show preview of timeline
    st.markdown("**Timeline Preview:**")
    preview_text = " → ".join([f"Wk{i}" for i in range(1, min(total_weeks + 1, 13))])
    if total_weeks > 12:
        preview_text += f" → ... → Wk{total_weeks}"
    st.code(preview_text)

    st.caption(f"Markdown checkpoint: Week {params.markdown_week}")

    if st.button("✅ Start In-Season Planning", type="primary", use_container_width=True):
        st.session_state.total_season_weeks = total_weeks
        st.session_state.season_start_date = start_date
        st.session_state.inseason_setup_complete = True
        st.session_state.selected_week = 1
        st.success("✅ In-season planning initialized!")
        st.rerun()


def render_inseason_planning(params: WorkflowParams):
    """Render the complete in-season planning interface with timeline."""

    # Check if setup is complete
    if not st.session_state.inseason_setup_complete:
        render_inseason_setup(params)
        return

    # Check if we have a pre-season forecast
    if st.session_state.workflow_result is None:
        st.warning(
            "⚠️ No pre-season forecast available. Please complete pre-season planning first."
        )
        if st.button("↩️ Go to Pre-Season", key="goto_preseason"):
            st.session_state.planning_mode = "pre-season"
            st.rerun()
        return

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
            st.success(f"Uploaded: {sales_file.name}")
            try:
                preview_df = pd.read_csv(sales_file)
                st.dataframe(preview_df.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Error previewing file: {e}")

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
            st.success(f"Uploaded: {stores_file.name}")
            try:
                preview_df = pd.read_csv(stores_file)
                st.dataframe(preview_df.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Error previewing file: {e}")

    st.divider()

    # Show available data summary
    st.markdown("### Available Training Data")
    summary = st.session_state.data_loader.get_context_summary()
    st.markdown(summary)


# =============================================================================
# Main Content
# =============================================================================
async def run_workflow_async(params: WorkflowParams):
    """Run the workflow asynchronously."""
    context = ForecastingContext(
        data_loader=st.session_state.data_loader,
        session_id=st.session_state.session_id,
        current_week=st.session_state.current_week,
        actual_sales=st.session_state.actual_sales if st.session_state.actual_sales else None,
        total_sold=st.session_state.total_sold,
    )

    if st.session_state.current_week > 0 and st.session_state.actual_sales:
        result = await run_inseason_update(
            context=context,
            params=params,
            current_week=st.session_state.current_week,
            actual_sales=st.session_state.actual_sales,
            total_sold=st.session_state.total_sold,
        )
    else:
        result = await run_preseason_planning(
            context=context,
            params=params,
        )

    return result


def render_preseason_tab(params: WorkflowParams):
    """Render the Pre-Season planning tab."""
    st.markdown("## 🌱 Pre-Season Planning")
    st.markdown(
        "Generate demand forecasts and initial inventory allocations before the season begins."
    )

    # Check if pre-season is already complete
    if st.session_state.workflow_result:
        st.success("✅ Pre-season planning complete! View results below or proceed to In-Season tab.")

    st.divider()

    # Workflow configuration display
    col_info, col_action = st.columns([2, 1])

    with col_info:
        st.markdown("### Workflow Configuration")
        st.markdown(
            f"""
            - **Category:** {params.category}
            - **Forecast Horizon:** {params.forecast_horizon_weeks} weeks
            - **DC Holdback:** {params.dc_holdback_pct:.0%}
            - **Safety Stock:** {params.safety_stock_pct:.0%}
            - **Replenishment:** {params.replenishment_strategy}
            """
        )

    with col_action:
        run_button = st.button(
            "▶️ Run Pre-Season Workflow",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running,
        )

    if run_button:
        st.session_state.running = True

        with st.status("Running pre-season workflow...", expanded=True) as status:
            st.write("🔮 Phase 1: Running Demand Agent...")

            try:
                result = asyncio.run(run_workflow_async(params))
                st.session_state.workflow_result = result
                st.write("📦 Phase 2: Running Inventory Agent...")
                st.write("✅ Pre-season planning complete!")
                status.update(
                    label="✅ Pre-season workflow complete!",
                    state="complete",
                    expanded=False,
                )
            except Exception as e:
                status.update(label=f"❌ Error: {e}", state="error")
                st.error(f"Workflow failed: {e}")
            finally:
                st.session_state.running = False
                st.rerun()

    # Show results if available
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result

        st.divider()
        st.markdown("### 📊 Pre-Season Results")

        # Forecast section
        render_forecast_section(
            result.forecast,
            params,
            actual_sales=None,  # No actuals in pre-season
        )

        st.divider()

        # Allocation section
        render_allocation_section(result.allocation)

        st.divider()

        # Data upload section
        with st.expander("📁 Data Management", expanded=False):
            render_data_upload()


def main():
    """Main application entry point."""
    st.title("📊 Retail Forecasting Multi-Agent System")
    st.markdown(
        """
        This system uses **3 specialized AI agents** to forecast demand, allocate inventory,
        and optimize pricing for fashion retail.
        """
    )

    # Render sidebar and get parameters
    params = render_sidebar()

    # NEW: Two primary tabs - Preseason and In-Season
    tab_preseason, tab_inseason = st.tabs(
        ["🌱 Pre-Season", "📅 In-Season"]
    )

    with tab_preseason:
        render_preseason_tab(params)

    with tab_inseason:
        render_inseason_planning(params)


if __name__ == "__main__":
    main()
