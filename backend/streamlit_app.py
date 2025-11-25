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


init_session_state()


# =============================================================================
# Sidebar - Parameters
# =============================================================================
def render_sidebar():
    """Render the sidebar with workflow parameters."""
    st.sidebar.title("📊 Workflow Parameters")

    # Planning mode selection
    st.sidebar.subheader("📅 Planning Mode")
    planning_mode = st.sidebar.radio(
        "Select Mode",
        options=["Pre-Season", "In-Season"],
        index=0 if st.session_state.planning_mode == "pre-season" else 1,
        help="Pre-Season: Initial forecast & allocation. In-Season: Update with actual sales.",
    )
    st.session_state.planning_mode = planning_mode.lower().replace("-", "-")

    st.sidebar.divider()

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
        cluster_data = pd.DataFrame(
            [
                {
                    "Cluster": c.cluster_name,
                    "Units": c.allocation_units,
                    "Stores": c.store_count,
                    "Percentage": c.allocation_percentage,
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
# In-Season Planning Section
# =============================================================================
def render_inseason_planning(params: WorkflowParams):
    """Render the in-season planning interface."""
    st.subheader("📅 In-Season Planning")

    # Check if we have a pre-season forecast to compare against
    if st.session_state.workflow_result is None:
        st.warning(
            "⚠️ No pre-season forecast available. Please run a pre-season workflow first, "
            "or the system will generate one automatically."
        )

    # Current status
    col_status1, col_status2, col_status3 = st.columns(3)

    with col_status1:
        st.metric(
            label="Current Week",
            value=st.session_state.current_week if st.session_state.current_week > 0 else "Not started",
        )

    with col_status2:
        st.metric(
            label="Total Sold",
            value=f"{st.session_state.total_sold:,}" if st.session_state.total_sold > 0 else "No data",
        )

    with col_status3:
        if st.session_state.workflow_result and st.session_state.total_sold > 0:
            allocation = st.session_state.workflow_result.allocation
            sell_through = st.session_state.total_sold / allocation.initial_store_allocation
            st.metric(
                label="Current Sell-Through",
                value=f"{sell_through:.1%}",
            )
        else:
            st.metric(label="Current Sell-Through", value="N/A")

    st.divider()

    # Actual sales input section
    st.markdown("### Upload Actual Sales Data")

    upload_method = st.radio(
        "Input Method",
        options=["Upload CSV", "Manual Entry"],
        horizontal=True,
    )

    if upload_method == "Upload CSV":
        st.markdown(
            """
            **CSV Format Required:**
            ```
            week,actual_sales
            1,520
            2,485
            3,510
            ```
            """
        )

        actual_file = st.file_uploader(
            "Upload actual sales CSV",
            type=["csv"],
            key="inseason_actual_upload",
            help="CSV with columns: week, actual_sales",
        )

        if actual_file is not None:
            try:
                actual_df = pd.read_csv(actual_file)

                # Validate columns
                if "actual_sales" not in actual_df.columns:
                    st.error("CSV must contain 'actual_sales' column")
                else:
                    st.session_state.actual_sales = actual_df["actual_sales"].tolist()
                    st.session_state.total_sold = sum(st.session_state.actual_sales)
                    st.session_state.current_week = len(st.session_state.actual_sales)

                    st.success(
                        f"✅ Loaded {len(st.session_state.actual_sales)} weeks of actual sales data"
                    )

                    # Preview data
                    st.dataframe(actual_df, use_container_width=True)

            except Exception as e:
                st.error(f"Error loading file: {e}")

    else:  # Manual Entry
        st.markdown("Enter actual sales for each week:")

        # Dynamic week entry
        num_weeks = st.number_input(
            "Number of weeks to enter",
            min_value=1,
            max_value=params.forecast_horizon_weeks,
            value=max(1, st.session_state.current_week) if st.session_state.current_week > 0 else 1,
        )

        manual_sales = []
        cols = st.columns(min(4, num_weeks))

        for i in range(num_weeks):
            col_idx = i % 4
            with cols[col_idx]:
                default_val = (
                    st.session_state.actual_sales[i]
                    if i < len(st.session_state.actual_sales)
                    else 0
                )
                week_sales = st.number_input(
                    f"Week {i + 1}",
                    min_value=0,
                    value=int(default_val),
                    key=f"week_{i + 1}_sales",
                )
                manual_sales.append(week_sales)

        if st.button("Apply Manual Entry", type="secondary"):
            st.session_state.actual_sales = manual_sales
            st.session_state.total_sold = sum(manual_sales)
            st.session_state.current_week = len(manual_sales)
            st.success(f"✅ Applied {len(manual_sales)} weeks of sales data")
            st.rerun()

    st.divider()

    # Variance check section
    st.markdown("### Check Variance")

    if len(st.session_state.actual_sales) > 0:
        # Get forecast to compare against
        if st.session_state.workflow_result:
            forecast_by_week = st.session_state.workflow_result.forecast.forecast_by_week
        else:
            st.warning("No forecast available. Run pre-season workflow first.")
            forecast_by_week = None

        if forecast_by_week:
            col_check, col_result = st.columns([1, 2])

            with col_check:
                if st.button("🔍 Calculate Variance", type="primary", use_container_width=True):
                    # Calculate variance
                    variance_result = check_variance(
                        actual_sales=st.session_state.actual_sales,
                        forecast_by_week=forecast_by_week,
                        week_number=st.session_state.current_week,
                        threshold=params.variance_threshold,
                    )
                    st.session_state.variance_result = variance_result

            # Show variance result if calculated
            if st.session_state.variance_result:
                render_variance_analysis(
                    variance=st.session_state.variance_result,
                    forecast_by_week=forecast_by_week,
                    actual_sales=st.session_state.actual_sales,
                    params=params,
                )
    else:
        st.info("Upload or enter actual sales data to enable variance checking.")


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

    # Main content tabs based on planning mode
    if st.session_state.planning_mode == "pre-season":
        tab_run, tab_data, tab_results = st.tabs(
            ["🚀 Run Workflow", "📁 Data Management", "📊 Results"]
        )
    else:
        tab_run, tab_inseason, tab_data, tab_results = st.tabs(
            ["🚀 Run Workflow", "📅 In-Season Planning", "📁 Data Management", "📊 Results"]
        )

    with tab_run:
        st.markdown("### Run Season Planning Workflow")

        # Mode indicator
        mode_label = "Pre-Season" if st.session_state.planning_mode == "pre-season" else "In-Season"
        st.info(f"**Current Mode:** {mode_label} Planning")

        col_info, col_action = st.columns([2, 1])

        with col_info:
            st.markdown(
                f"""
                **Workflow Configuration:**
                - Category: **{params.category}**
                - Forecast Horizon: **{params.forecast_horizon_weeks} weeks**
                - DC Holdback: **{params.dc_holdback_pct:.0%}**
                - Markdown Week: **{params.markdown_week}**
                - Current Week: **{st.session_state.current_week}**
                - Actual Sales Data: **{"Yes" if st.session_state.actual_sales else "No"}**
                """
            )

        with col_action:
            button_label = (
                "▶️ Run Pre-Season Workflow"
                if st.session_state.planning_mode == "pre-season"
                else "▶️ Run In-Season Update"
            )

            run_button = st.button(
                button_label,
                type="primary",
                use_container_width=True,
                disabled=st.session_state.running,
            )

        if run_button:
            st.session_state.running = True

            with st.status("Running workflow...", expanded=True) as status:
                st.write("🔮 Phase 1: Running Demand Agent...")

                try:
                    result = asyncio.run(run_workflow_async(params))
                    st.session_state.workflow_result = result
                    st.write("📦 Phase 2: Running Inventory Agent...")
                    st.write("💰 Phase 3: Running Pricing Agent...")
                    status.update(
                        label="✅ Workflow complete!",
                        state="complete",
                        expanded=False,
                    )
                except Exception as e:
                    status.update(label=f"❌ Error: {e}", state="error")
                    st.error(f"Workflow failed: {e}")
                finally:
                    st.session_state.running = False
                    st.rerun()

        # Show results summary if available
        if st.session_state.workflow_result:
            result = st.session_state.workflow_result
            st.success(
                f"✅ Workflow completed in {result.total_duration_seconds:.2f}s | "
                f"Phases: {', '.join(result.phases_completed)}"
            )

    # In-Season tab (only shown in in-season mode)
    if st.session_state.planning_mode != "pre-season":
        with tab_inseason:
            render_inseason_planning(params)

    with tab_data:
        render_data_upload()

    with tab_results:
        if st.session_state.workflow_result is None:
            st.info("No results yet. Run the workflow to see results here.")
        else:
            result = st.session_state.workflow_result

            # Forecast section with actual sales comparison
            render_forecast_section(
                result.forecast,
                params,
                actual_sales=st.session_state.actual_sales if st.session_state.actual_sales else None,
            )

            st.divider()

            # Allocation section
            render_allocation_section(result.allocation)

            st.divider()

            # Pricing section
            render_pricing_section(result.markdown, params)

            st.divider()

            # Variance history section
            render_variance_history(result)

            # Export results
            st.divider()
            st.markdown("### Export Results")

            col_export1, col_export2, col_export3, col_export4 = st.columns(4)

            with col_export1:
                forecast_df = pd.DataFrame(
                    {
                        "Week": list(
                            range(1, len(result.forecast.forecast_by_week) + 1)
                        ),
                        "Forecast": result.forecast.forecast_by_week,
                    }
                )
                # Add actual sales if available
                if st.session_state.actual_sales:
                    forecast_df["Actual"] = (
                        st.session_state.actual_sales
                        + [None] * (len(forecast_df) - len(st.session_state.actual_sales))
                    )

                st.download_button(
                    "📥 Download Forecast",
                    forecast_df.to_csv(index=False),
                    "forecast.csv",
                    "text/csv",
                )

            with col_export2:
                allocation_df = pd.DataFrame(
                    [
                        {
                            "Store": s.store_id,
                            "Units": s.allocation_units,
                            "Cluster": s.cluster,
                        }
                        for s in result.allocation.store_allocations
                    ]
                )
                st.download_button(
                    "📥 Download Allocation",
                    allocation_df.to_csv(index=False),
                    "allocation.csv",
                    "text/csv",
                )

            with col_export3:
                if result.markdown:
                    markdown_data = {
                        "Recommended Markdown": [result.markdown.recommended_markdown_pct],
                        "Current Sell-Through": [result.markdown.current_sell_through],
                        "Target Sell-Through": [result.markdown.target_sell_through],
                        "Gap": [result.markdown.gap],
                    }
                    st.download_button(
                        "📥 Download Pricing",
                        pd.DataFrame(markdown_data).to_csv(index=False),
                        "pricing.csv",
                        "text/csv",
                    )

            with col_export4:
                if st.session_state.variance_result:
                    variance_data = {
                        "Week": [st.session_state.variance_result.week_number],
                        "Variance %": [st.session_state.variance_result.variance_pct],
                        "High Variance": [st.session_state.variance_result.is_high_variance],
                        "Direction": [st.session_state.variance_result.direction],
                    }
                    st.download_button(
                        "📥 Download Variance",
                        pd.DataFrame(variance_data).to_csv(index=False),
                        "variance.csv",
                        "text/csv",
                    )


if __name__ == "__main__":
    main()
