"""
Retail Forecasting System - Enhanced Streamlit UI
Professional UX with improved visual design and interactions
"""
import streamlit as st
from agents import Runner, set_tracing_disabled, SQLiteSession
from config import OPENAI_MODEL
from utils import SessionManager, TrainingDataLoader, StreamlitVisualizationHooks
from utils.context import ForecastingContext
from my_agents.coordinator_agent import create_coordinator_agent
from agent_tools.variance_tools import check_variance, calculate_mape
import re
import pandas as pd
from datetime import datetime
import os

# ============================================================================
# CUSTOM CSS FOR PROFESSIONAL LOOK
# ============================================================================

def inject_custom_css():
    """Inject custom CSS for enhanced visual design"""
    st.markdown("""
    <style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Custom header styling */
    .custom-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .custom-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .custom-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Upload section styling */
    .upload-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #cbd5e0;
        transition: all 0.3s ease;
    }

    .upload-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }

    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 10px;
    }

    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Button enhancements */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Success/Info boxes */
    .stSuccess, .stInfo {
        border-radius: 8px;
        padding: 1rem;
    }

    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #cbd5e0, transparent);
    }

    /* Quick action chips */
    .quick-action-chip {
        display: inline-block;
        background: #e0e7ff;
        color: #4c51bf;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .quick-action-chip:hover {
        background: #c7d2fe;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# RESULTS DISPLAY HELPERS (Enhanced with charts)
# ============================================================================

def _display_forecast_results(response: str):
    """Display demand forecast results using structured output data (Pydantic model)"""
    try:
        st.divider()

        # Get structured data from session state (captured by lifecycle hook)
        forecast_data = getattr(st.session_state, 'demand_forecast_data', None)

        # Check if this is a re-forecast
        is_reforecast = 'reforecast' in response.lower() or 'updated forecast' in response.lower()

        # Header
        if is_reforecast:
            st.subheader("🔄 Updated Forecast Summary Dashboard")
            st.success("**✅ Re-forecast complete!** New forecast incorporates actual sales data for improved accuracy.")
        else:
            st.subheader("📊 Forecast Summary Dashboard")

        # VALIDATION: Check if data exists
        if not forecast_data:
            # FALLBACK: Try to parse from agent response text (brittle but better than nothing)
            import re
            total_match = re.search(r'Total Demand.*?(\d+,?\d*)\s+units', response, re.IGNORECASE)
            confidence_match = re.search(r'Confidence.*?(\d+)%', response, re.IGNORECASE)

            if total_match or confidence_match:
                st.warning("⚠️ **Using fallback text parsing** (structured data wasn't captured)")
                st.info(f"""
                **Parsed from AI response:**
                - Total Demand: {total_match.group(1) if total_match else 'Not found'} units
                - Confidence: {confidence_match.group(1) if confidence_match else 'Not found'}%

                The full forecast details are in the AI response above.
                """)
            else:
                st.error("⚠️ **Forecast completed but visualization data is missing.**")
                st.info("""
                **What happened:** The AI agent completed the forecast, but the structured data wasn't captured.

                **What to do:**
                1. Check the AI response above for text-based results
                2. Try running the forecast again
                3. If this persists, check console logs for hook debug messages
                """)

            st.session_state.show_variance_section = True  # Still allow variance checking
            return

        # VALIDATION: Check required fields
        required_fields = ['total_demand', 'forecast_by_week', 'confidence', 'safety_stock_pct']
        missing_fields = [f for f in required_fields if f not in forecast_data or forecast_data[f] is None]

        if missing_fields:
            st.error(f"⚠️ **Incomplete forecast data. Missing: {', '.join(missing_fields)}**")
            st.warning("The forecast may have partially failed. Please review the AI response above and try again.")

            # Show whatever data we do have
            with st.expander("🔍 Available Data (Partial)", expanded=True):
                st.json(forecast_data)
            return

        if forecast_data:
            # Use structured data directly - no regex needed!
            total_demand = forecast_data.get('total_demand')
            weekly_avg = forecast_data.get('weekly_average')
            confidence = forecast_data.get('confidence')
            safety_stock_pct = forecast_data.get('safety_stock_pct')
            forecast_by_week = forecast_data.get('forecast_by_week', [])
            model_used = forecast_data.get('model_used', 'Unknown')
            data_quality = forecast_data.get('data_quality', 'Unknown')

            # Metrics row with enhanced styling
            cols = st.columns(4)
            if total_demand:
                cols[0].metric(
                    "Total Demand",
                    f"{total_demand:,} units",
                    help="Predicted total units needed for the forecast period"
                )
            if weekly_avg:
                cols[1].metric(
                    "Weekly Average",
                    f"{weekly_avg:,} units/week",
                    help="Average demand per week"
                )
            if confidence is not None:
                conf_delta = "High" if confidence >= 70 else "Medium" if confidence >= 50 else "Low"
                cols[2].metric(
                    "Confidence",
                    f"{confidence}%",
                    delta=conf_delta,
                    help="Forecast reliability score"
                )
            if safety_stock_pct is not None:
                safety_stock_display = int(safety_stock_pct * 100) if safety_stock_pct <= 1 else int(safety_stock_pct)
                cols[3].metric(
                    "Safety Stock",
                    f"{safety_stock_display}%",
                    help="Additional buffer inventory percentage"
                )

            # Additional info row
            st.caption(f"📊 Model: **{model_used}** | Data Quality: **{data_quality}**")

            # Weekly breakdown chart from structured data
            if forecast_by_week and len(forecast_by_week) > 0:
                st.caption("📈 Weekly Breakdown")

                # Create DataFrame for chart
                weeks = [item['week'] if isinstance(item, dict) else i+1 for i, item in enumerate(forecast_by_week)]
                units = [item['demand'] if isinstance(item, dict) else item for item in forecast_by_week]

                df_weekly = pd.DataFrame({
                    'Week': weeks,
                    'Forecast Units': units
                })

                # Display as line chart
                st.line_chart(df_weekly.set_index('Week'), use_container_width=True)

                # Store forecast data for variance checking
                st.session_state.forecast_by_week = units
                st.session_state.show_variance_section = True

            # Show summary from structured output
            summary = forecast_data.get('summary')
            if summary:
                with st.expander("📋 Detailed Analysis", expanded=False):
                    st.markdown(summary)

        else:
            # Fallback: no structured data available, show info message
            st.info("✅ **Demand forecast completed!** See the AI response above for detailed results.")
            st.session_state.show_variance_section = True

    except Exception as e:
        # Show error for debugging
        st.warning(f"Could not display forecast visualization: {str(e)}")
        import traceback
        st.caption(traceback.format_exc())


def _display_variance_results(response: str):
    """Parse and display variance checking results visually"""
    try:
        # Extract variance metrics using regex - try multiple patterns
        # Pattern 1: "Actual Sales: X units" or "actual_total=X"
        actual_sales = re.search(r'Actual Sales[:\s]+(\d+,?\d*)\s+units', response, re.IGNORECASE)
        if not actual_sales:
            actual_sales = re.search(r'actual[_\s]total[=:\s]+(\d+,?\d*)', response, re.IGNORECASE)

        # Pattern 2: "Forecasted: Y units" or "forecast_total=Y"
        forecasted = re.search(r'Forecast(?:ed)?[:\s]+(\d+,?\d*)\s+units', response, re.IGNORECASE)
        if not forecasted:
            forecasted = re.search(r'forecast[_\s]total[=:\s]+(\d+,?\d*)', response, re.IGNORECASE)

        # Pattern 3: Variance percentage
        variance_match = re.search(r'Variance[:\s]+(\+|\-)?\s*(\d+(?:\.\d+)?)%', response, re.IGNORECASE)
        if not variance_match:
            variance_match = re.search(r'variance[_\s]pct[=:\s]+(\+|\-)?\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)

        high_variance = re.search(r'High Variance|⚠️|is_high_variance[=:\s]+True', response, re.IGNORECASE)
        reforecast_triggered = re.search(r'HIGH_VARIANCE_REFORECAST_NEEDED|Triggering Automatic Re-Forecast', response, re.IGNORECASE)

        if actual_sales or variance_match or 'variance' in response.lower():
            st.divider()
            st.subheader("📊 Variance Analysis Results")

            # Metrics row
            cols = st.columns(4)
            if actual_sales:
                cols[0].metric(
                    "Actual Sales",
                    f"{actual_sales.group(1)} units",
                    help="Total actual sales for the week"
                )
            else:
                cols[0].metric("Actual Sales", "See debug", help="Could not parse from response")

            if forecasted:
                cols[1].metric(
                    "Forecasted",
                    f"{forecasted.group(1)} units",
                    help="Forecasted sales for the week"
                )
            else:
                cols[1].metric("Forecasted", "See debug", help="Could not parse from response")

            if variance_match:
                variance_val = float(variance_match.group(2))
                sign = variance_match.group(1) if variance_match.group(1) else ""
                cols[2].metric(
                    "Variance",
                    f"{sign}{variance_val}%",
                    delta="High" if high_variance else "OK",
                    delta_color="inverse" if high_variance else "normal",
                    help="Percentage difference between forecast and actual"
                )

            status_emoji = "⚠️" if high_variance else "✅"
            status_text = "High Variance" if high_variance else "On Track"
            cols[3].metric("Status", f"{status_emoji} {status_text}")

            # Recommendation box with re-forecasting indicator
            if reforecast_triggered:
                st.error("**🔄 AUTOMATIC RE-FORECASTING TRIGGERED!**")
                st.info("The AI coordinator is automatically generating a new forecast with updated data. This self-healing process improves forecast accuracy based on actual performance.")
            elif high_variance:
                st.warning("**⚠️ High variance detected!** See AI recommendation above for next steps.")
            else:
                st.success("**✅ Variance within acceptable range.** Forecast accuracy is good!")

            # Always show debug info for variance (temporarily, to diagnose)
            with st.expander("🔍 Debug: Raw Agent Response", expanded=not (actual_sales and forecasted)):
                st.text(response)
                if not actual_sales or not forecasted:
                    st.warning("⚠️ Could not parse all numbers from response. The tool ran successfully, but the agent's text format is incorrect.")
                    st.info("💡 **Tip:** Look for 'actual_total' and 'forecast_total' in the raw response above - those are the actual values!")

    except Exception as e:
        # Silently fail
        pass


def _display_inventory_results(response: str):
    """Display inventory allocation results using structured output data (Pydantic model)"""
    try:
        st.divider()
        st.subheader("🏭 Inventory Allocation Dashboard")

        # Get structured data from session state (captured by lifecycle hook)
        allocation_data = getattr(st.session_state, 'inventory_allocation_data', None)

        # VALIDATION: Check if data exists
        if not allocation_data:
            st.error("⚠️ **Allocation completed but visualization data is missing.**")
            st.info("""
            **What happened:** The AI agent completed the allocation, but the structured data wasn't captured.

            **What to do:**
            1. Check the AI response above for text-based results
            2. Try running the allocation again
            """)
            return

        # VALIDATION: Check required fields
        required_fields = ['manufacturing_qty', 'dc_holdback', 'initial_store_allocation']
        missing_fields = [f for f in required_fields if f not in allocation_data or allocation_data[f] is None]

        if missing_fields:
            st.error(f"⚠️ **Incomplete allocation data. Missing: {', '.join(missing_fields)}**")
            st.warning("The allocation may have partially failed. Please review the AI response above.")
            with st.expander("🔍 Available Data (Partial)", expanded=True):
                st.json(allocation_data)
            return

        if allocation_data:
            # Use structured data directly - no regex needed!
            manufacturing_qty = allocation_data.get('manufacturing_qty')
            dc_holdback = allocation_data.get('dc_holdback')
            dc_holdback_pct = allocation_data.get('dc_holdback_percentage')
            initial_store_allocation = allocation_data.get('initial_store_allocation')
            cluster_allocations = allocation_data.get('cluster_allocations', [])
            store_allocations = allocation_data.get('store_allocations', [])
            replenishment_strategy = allocation_data.get('replenishment_strategy', 'Unknown')
            summary = allocation_data.get('summary')

            # Top-level metrics
            cols = st.columns(3)
            if manufacturing_qty:
                cols[0].metric(
                    "Manufacturing Qty",
                    f"{manufacturing_qty:,} units",
                    help="Total units to manufacture (demand + safety stock)"
                )
            if dc_holdback:
                delta_text = f"{int(dc_holdback_pct * 100)}%" if dc_holdback_pct and dc_holdback_pct <= 1 else f"{int(dc_holdback_pct)}%" if dc_holdback_pct else None
                cols[1].metric(
                    "DC Holdback",
                    f"{dc_holdback:,} units",
                    delta=delta_text,
                    help="Units held at distribution center for replenishment"
                )
            if initial_store_allocation:
                cols[2].metric(
                    "Initial Store Allocation",
                    f"{initial_store_allocation:,} units",
                    help="Units allocated to stores initially"
                )

            st.caption(f"📦 Replenishment Strategy: **{replenishment_strategy}**")

            # Cluster allocations from structured data
            if cluster_allocations and len(cluster_allocations) > 0:
                st.caption("📊 Cluster Distribution")

                # Create DataFrame for chart
                cluster_data = []
                for cluster in cluster_allocations:
                    cluster_data.append({
                        'Cluster': cluster.get('cluster_name', 'Unknown').replace('_', ' '),
                        'Units': cluster.get('allocation_units', 0),
                        'Percentage': cluster.get('allocation_percentage', 0),
                        'Stores': cluster.get('store_count', 0)
                    })

                df_clusters = pd.DataFrame(cluster_data)
                st.bar_chart(df_clusters.set_index('Cluster')['Percentage'], use_container_width=True)

            # Store allocations from structured data
            if store_allocations and len(store_allocations) > 0:
                st.divider()
                st.subheader("🏪 Store-Level Allocations")

                # Create DataFrame for table
                store_data = []
                for store in store_allocations:
                    store_data.append({
                        'Store ID': store.get('store_id', 'Unknown'),
                        'Allocated Units': store.get('allocation_units', 0),
                        'Cluster': store.get('cluster', 'Unknown').replace('_', ' '),
                        'Factor': f"{store.get('allocation_factor', 1.0):.2f}"
                    })

                df_stores = pd.DataFrame(store_data)
                st.dataframe(
                    df_stores,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )

            # Show summary
            if summary:
                with st.expander("📋 Allocation Summary", expanded=False):
                    st.markdown(summary)

        else:
            # Fallback: no structured data, show info message
            st.info("✅ **Inventory allocation completed!** See the AI response above for detailed results.")

    except Exception as e:
        st.warning(f"Could not display inventory visualization: {str(e)}")
        import traceback
        st.caption(traceback.format_exc())


def _display_in_season_prompt():
    """Display prompt asking user if they want to start in-season planning with actual sales upload"""
    st.divider()

    # Prominent call-to-action box
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="margin: 0 0 0.5rem 0; color: #2d3748;">🎯 Pre-Season Planning Complete!</h3>
        <p style="margin: 0; color: #4a5568; font-size: 1.1rem;">
            Your forecast and allocation are ready. Would you like to start in-season planning?
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **In-Season Planning** allows you to:
    - Upload actual weekly sales data as your season progresses
    - Track forecast accuracy with variance analysis
    - Automatically trigger re-forecasting when variance exceeds thresholds
    - Continuously improve your predictions based on real performance
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Yes, Start In-Season Planning", type="primary", use_container_width=True, key="start_in_season"):
            st.session_state.in_season_started = True
            st.session_state.show_in_season_prompt = False
            st.rerun()

    with col2:
        if st.button("⏭️ Skip for Now", use_container_width=True, key="skip_in_season"):
            st.session_state.show_in_season_prompt = False
            st.rerun()

    # Show upload section if user clicked "Yes"
    if getattr(st.session_state, 'in_season_started', False):
        _display_actual_sales_upload(key_suffix="prompt")


def _display_actual_sales_upload(key_suffix="main"):
    """Display the actual sales CSV upload section for in-season planning

    Args:
        key_suffix: Suffix for widget keys to avoid conflicts when called from multiple places
    """
    st.subheader("📤 Upload Actual Sales Data")

    st.info("""
    **Upload your weekly actual sales data** to compare against forecasts.

    **Required CSV format:**
    - `date` - Date of sales (YYYY-MM-DD)
    - `store_id` - Store identifier
    - `quantity_sold` - Actual units sold

    Optional: `category`, `revenue`
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        actuals_file = st.file_uploader(
            "📊 Actual Sales CSV",
            type=["csv"],
            key=f"actuals_upload_{key_suffix}",
            help="CSV with columns: date, store_id, quantity_sold"
        )

        if actuals_file:
            st.success(f"✅ **{actuals_file.name}** uploaded")

            # Show preview
            df_actuals = pd.read_csv(actuals_file)
            with st.expander("👁️ Preview Data", expanded=True):
                st.dataframe(df_actuals.head(10), use_container_width=True)

                # Show data summary
                st.caption(f"**Rows:** {len(df_actuals)} | **Columns:** {', '.join(df_actuals.columns)}")

            actuals_file.seek(0)

    with col2:
        st.markdown("**Analysis Options**")

        # Week number selector
        max_weeks = len(getattr(st.session_state, 'forecast_by_week', [])) or 12
        week_num = st.number_input(
            "Week Number",
            min_value=1,
            max_value=max_weeks,
            value=1,
            help=f"Which week does this data represent? (1-{max_weeks})",
            key=f"week_num_{key_suffix}"
        )

        # Variance threshold
        variance_threshold = st.slider(
            "Variance Threshold %",
            min_value=5,
            max_value=30,
            value=15,
            help="Variance above this % triggers re-forecast recommendation",
            key=f"variance_threshold_{key_suffix}"
        )

    # Action button
    if actuals_file:
        if st.button("🔍 Analyze Variance & Save Data", type="primary", use_container_width=True, key=f"analyze_variance_btn_{key_suffix}"):
            with st.spinner("Saving file and preparing analysis..."):
                try:
                    # Save uploaded file
                    session_dir = st.session_state.session_manager.get_session_dir(st.session_state.session_id)
                    temp_path = os.path.join(session_dir, f"actuals_week_{week_num}.csv")

                    with open(temp_path, "wb") as f:
                        f.write(actuals_file.getvalue())

                    st.success(f"✅ File saved successfully!")

                    # Store in session state for agent
                    st.session_state.variance_file_path = temp_path
                    st.session_state.variance_week = week_num
                    st.session_state.variance_threshold = variance_threshold / 100

                    # Create suggested prompt
                    suggested_prompt = f"Check variance for week {week_num} using the uploaded actual sales data. Use {variance_threshold}% variance threshold."

                    st.info(f"**Ready for analysis!** Use the chat below to ask:\n\n`{suggested_prompt}`")

                    # Quick action button
                    if st.button("🚀 Run Variance Analysis Now", use_container_width=True, key=f"run_variance_now_{key_suffix}"):
                        st.session_state.quick_prompt = suggested_prompt
                        st.rerun()

                except Exception as e:
                    st.error(f"Error saving file: {str(e)}")


# ============================================================================
# QUICK ACTION HELPERS
# ============================================================================

def render_quick_actions():
    """Render quick action buttons for common tasks"""
    st.markdown("### 🚀 Quick Start")
    st.markdown("Click any option below to get started quickly:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Create Forecast", use_container_width=True, key="quick_forecast"):
            st.session_state.quick_prompt = "I need help with forecasting"
            st.rerun()

    with col2:
        if st.button("📦 Plan Inventory", use_container_width=True, key="quick_inventory"):
            st.session_state.quick_prompt = "Help me plan inventory allocation"
            st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

# Configure page
st.set_page_config(
    page_title="Retail Forecasting System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'About': "AI-Powered Retail Forecasting System v2.0"
    }
)

# Inject custom CSS
inject_custom_css()

# Disable tracing for cleaner output
set_tracing_disabled(True)

# Initialize session state
if "session_id" not in st.session_state:
    session_manager = SessionManager()
    st.session_state.session_id = session_manager.create_session()
    st.session_state.session_manager = session_manager
    st.session_state.uploaded = False
    st.session_state.data_loader = None
    st.session_state.agent = None
    st.session_state.conversation_history = []
    st.session_state.forecast_context = None
    st.session_state.quick_prompt = None

    # Forecast tracking for variance checking
    st.session_state.latest_forecast = None  # Store latest forecast result
    st.session_state.forecast_by_week = []   # Weekly forecast values
    st.session_state.variance_results = []   # Variance check results
    st.session_state.show_variance_section = False  # Toggle variance upload section
    st.session_state.allocation_complete = False  # Track if allocation was completed (for variance section expansion)
    st.session_state.show_in_season_prompt = False  # Show in-season planning prompt after allocation
    st.session_state.in_season_started = False  # Track if user started in-season planning

    # Lifecycle hook completion flags (replaces string pattern matching)
    st.session_state.demand_agent_completed = False
    st.session_state.demand_agent_output = None
    st.session_state.inventory_agent_completed = False
    st.session_state.inventory_agent_output = None
    st.session_state.variance_check_completed = False
    st.session_state.variance_output = None

    # Real-time execution monitoring state (used by sidebar monitor)
    st.session_state.active_agent = None
    st.session_state.agent_is_running = False
    st.session_state.llm_is_thinking = False
    st.session_state.current_reasoning = None
    st.session_state.current_tool = None
    st.session_state.agent_timeline = []
    st.session_state.tools_executing = []
    st.session_state.completed_tools = []
    st.session_state.llm_calls = []

    # Structured output data (from Pydantic models via lifecycle hooks)
    st.session_state.demand_forecast_data = None  # DemandForecastOutput as dict
    st.session_state.inventory_allocation_data = None  # InventoryAllocationOutput as dict
    st.session_state.variance_data = None  # VarianceCheckOutput as dict

    # Create SDK Session for conversation memory
    st.session_state.sdk_session = SQLiteSession(
        session_id=st.session_state.session_id,
        db_path=":memory:"
    )

# Custom Header
st.markdown("""
<div class="custom-header">
    <h1>📊 Retail Forecasting System</h1>
    <p>AI-Powered Demand Forecasting & Inventory Planning</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Real-time Execution Monitor
with st.sidebar:
    # Only show execution monitor if data is uploaded and agent is initialized
    if st.session_state.uploaded and st.session_state.agent:
        # Import and render the real-time execution monitor
        from utils.sidebar_monitor import render_execution_monitor
        render_execution_monitor(st.session_state)
    else:
        # Show setup status when not yet ready
        st.markdown("### 📋 Session Info")
        st.caption(f"**Session ID:** `{st.session_state.session_id[:12]}...`")
        st.caption(f"**Started:** {datetime.now().strftime('%I:%M %p')}")

        st.divider()

        # Status indicators
        st.markdown("### 📡 System Status")

        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.uploaded:
                st.success("✅ Data")
            else:
                st.warning("⏳ Data")

        with col2:
            if st.session_state.agent:
                st.success("✅ Agent")
            else:
                st.info("⏳ Agent")

    st.divider()

    # Quick actions
    st.markdown("### ⚙️ Actions")
    if st.button("🔄 New Session", use_container_width=True, key="new_session"):
        st.session_state.session_manager.clear_session(st.session_state.session_id)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content area
if not st.session_state.uploaded:
    # Upload section with enhanced design
    st.markdown("## 📤 Step 1: Upload Your Data")
    st.info("🎯 Upload your historical sales and store data to begin AI-powered forecasting")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Historical Sales Data")
        historical_file = st.file_uploader(
            "Drag and drop or browse",
            type=["csv"],
            key="historical",
            help="CSV with: date, store_id, category, quantity_sold, revenue",
            label_visibility="collapsed"
        )

        if historical_file:
            st.success(f"✅ **{historical_file.name}**")
            st.caption(f"Size: {historical_file.size / 1024:.1f} KB")

            # Show preview
            df = pd.read_csv(historical_file)
            with st.expander("👁️ Preview Data"):
                st.dataframe(df.head(5), use_container_width=True)
            historical_file.seek(0)

    with col2:
        st.markdown("#### 🏪 Store Attributes")
        store_file = st.file_uploader(
            "Drag and drop or browse",
            type=["csv"],
            key="store",
            help="CSV with: store_id, size_sqft, income_level, location, etc.",
            label_visibility="collapsed"
        )

        if store_file:
            st.success(f"✅ **{store_file.name}**")
            st.caption(f"Size: {store_file.size / 1024:.1f} KB")

            # Show preview
            df = pd.read_csv(store_file)
            with st.expander("👁️ Preview Data"):
                st.dataframe(df.head(5), use_container_width=True)
            store_file.seek(0)

    st.divider()

    # Process uploads
    if historical_file and store_file:
        st.success("🎉 Both files uploaded successfully!")

        if st.button("🚀 Process Data & Start Forecasting", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing your data... This may take a moment."):
                # Save files
                st.session_state.session_manager.save_uploaded_files(
                    st.session_state.session_id,
                    historical_file,
                    store_file
                )

                # Create data loader
                st.session_state.data_loader = st.session_state.session_manager.get_data_loader(
                    st.session_state.session_id
                )

                # Create ForecastingContext
                st.session_state.forecast_context = ForecastingContext(
                    data_loader=st.session_state.data_loader,
                    session_id=st.session_state.session_id
                )

                # Get data summary
                categories = st.session_state.data_loader.get_categories()
                store_count = st.session_state.data_loader.get_store_count()
                date_range = st.session_state.data_loader.get_date_range()

                # Create coordinator agent (uses agents-as-tools pattern)
                st.session_state.agent = create_coordinator_agent(
                    data_loader=st.session_state.data_loader
                )
                st.session_state.agent.model = OPENAI_MODEL

                # Mark as uploaded
                st.session_state.uploaded = True

                # Show success
                st.success(f"""
                ✅ **Data processed successfully!**

                - **Categories**: {', '.join(categories)}
                - **Stores**: {store_count}
                - **Date Range**: {date_range['start']} to {date_range['end']}
                """)

                st.balloons()
                st.rerun()

else:
    # Chat interface with enhanced design
    st.markdown("## 💬 Chat with AI Assistant")

    # Show data summary
    with st.expander("📊 Your Data Overview", expanded=False):
        categories = st.session_state.data_loader.get_categories()
        store_count = st.session_state.data_loader.get_store_count()
        date_range = st.session_state.data_loader.get_date_range()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Product Categories", len(categories))
            st.caption(", ".join(categories))
        with col2:
            st.metric("Total Stores", store_count)
        with col3:
            st.metric("Data Period", f"{date_range['start_year']}-{date_range['end_year']}")

    # In-Season Planning Section - NOW ALWAYS VISIBLE after forecast completes
    # FIX: Previously hidden behind in_season_started flag, making it hard to discover
    if getattr(st.session_state, 'show_variance_section', False):
        st.divider()
        st.markdown("## 🎯 In-Season Planning & Variance Checking")

        # Show informative message if user hasn't opted in yet
        if not getattr(st.session_state, 'in_season_started', False):
            st.info("""
            **💡 Track forecast accuracy in real-time!**

            Once your season is underway, upload actual sales data here to:
            - ✅ Validate forecast accuracy
            - ⚠️ Detect high variance (>15%)
            - 🔄 Trigger automatic re-forecasting if needed
            - 📈 Continuously improve predictions

            Click below to get started.
            """)

            if st.button("📈 Enable In-Season Planning", type="primary", key="enable_variance"):
                st.session_state.in_season_started = True
                st.rerun()
        else:
            st.success("**📊 In-Season Mode Active!** Upload actual sales data below.")

        # Show the upload section if opted in
        if getattr(st.session_state, 'in_season_started', False):
            _display_actual_sales_upload(key_suffix="section")

        st.divider()

    # Quick actions (if no conversation started)
    if len(st.session_state.conversation_history) == 0:
        render_quick_actions()
        st.divider()

    # Display conversation history
    for msg in st.session_state.conversation_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "timestamp" in msg:
                st.caption(f"🕐 {msg['timestamp']}")

    # Handle quick prompt if set
    if st.session_state.quick_prompt:
        prompt = st.session_state.quick_prompt
        st.session_state.quick_prompt = None  # Clear it
    else:
        # Chat input
        prompt = st.chat_input("💭 Type your message here...", key="chat_input")

    if prompt:
        # Add timestamp
        timestamp = datetime.now().strftime("%I:%M %p")

        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {timestamp}")

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your request..."):
                try:
                    # Import guardrail exception for handling
                    from agents.exceptions import OutputGuardrailTripwireTriggered

                    # Reset completion flags before running agent
                    st.session_state.demand_agent_completed = False
                    st.session_state.inventory_agent_completed = False
                    st.session_state.variance_check_completed = False

                    # Update context with variance data if available
                    if hasattr(st.session_state, 'variance_file_path') and st.session_state.variance_file_path:
                        st.session_state.forecast_context.variance_file_path = st.session_state.variance_file_path

                    if hasattr(st.session_state, 'variance_week'):
                        st.session_state.forecast_context.variance_week = st.session_state.variance_week
                    if hasattr(st.session_state, 'variance_threshold'):
                        st.session_state.forecast_context.variance_threshold = st.session_state.variance_threshold
                    if hasattr(st.session_state, 'forecast_by_week') and len(st.session_state.forecast_by_week) > 0:
                        st.session_state.forecast_context.forecast_by_week = st.session_state.forecast_by_week

                    # Create lifecycle hooks for event-based visualization triggering
                    visualization_hooks = StreamlitVisualizationHooks(st.session_state)

                    # Run agent with lifecycle hooks
                    res = Runner.run_sync(
                        starting_agent=st.session_state.agent,
                        input=prompt,
                        session=st.session_state.sdk_session,
                        context=st.session_state.forecast_context,
                        hooks=visualization_hooks  # Pass hooks for agent completion detection
                    )

                    # Extract response
                    if hasattr(res, 'final_output'):
                        response = res.final_output
                    elif hasattr(res, 'output'):
                        response = res.output
                    else:
                        response = str(res)

                    # Display response
                    st.markdown(response)
                    st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

                    # Enhanced results display using lifecycle hook flags
                    # This replaces brittle string pattern matching with reliable event-based detection
                    # WRAPPED IN ERROR BOUNDARIES to prevent visualization failures from breaking the UI

                    # Check for variance check completion (via lifecycle hook)
                    if st.session_state.variance_check_completed:
                        try:
                            _display_variance_results(response)
                            print("[UI] Displayed variance results based on lifecycle hook")
                        except Exception as viz_error:
                            st.error(f"⚠️ **Failed to display variance visualization:** {str(viz_error)}")
                            st.info("The variance check completed successfully, but the chart couldn't render. Check the AI response above for results.")
                            import traceback
                            with st.expander("🔍 Technical Details"):
                                st.code(traceback.format_exc())

                    # Check for inventory allocation completion (via lifecycle hook)
                    if st.session_state.inventory_agent_completed:
                        try:
                            _display_inventory_results(response)
                            st.session_state.allocation_complete = True
                            st.session_state.show_in_season_prompt = True  # Trigger in-season planning prompt
                            print("[UI] Displayed inventory results based on lifecycle hook")

                            # Show in-season planning prompt immediately after allocation
                            _display_in_season_prompt()
                        except Exception as viz_error:
                            st.error(f"⚠️ **Failed to display inventory visualization:** {str(viz_error)}")
                            st.info("The allocation completed successfully, but the chart couldn't render. Check the AI response above for results.")
                            import traceback
                            with st.expander("🔍 Technical Details"):
                                st.code(traceback.format_exc())

                    # Check for demand forecast completion (via lifecycle hook)
                    if st.session_state.demand_agent_completed:
                        try:
                            _display_forecast_results(response)
                            print("[UI] Displayed forecast results based on lifecycle hook")
                        except Exception as viz_error:
                            st.error(f"⚠️ **Failed to display forecast visualization:** {str(viz_error)}")
                            st.info("The forecast completed successfully, but the chart couldn't render. Check the AI response above for results.")
                            import traceback
                            with st.expander("🔍 Technical Details"):
                                st.code(traceback.format_exc())

                    # Add to history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })

                except OutputGuardrailTripwireTriggered as guardrail_error:
                    # Guardrail caught invalid output - show user-friendly error
                    st.error("⚠️ **Data Validation Failed**")
                    st.warning("""
                    The AI completed your request, but the output failed quality checks.
                    This prevents invalid data from breaking your analysis.
                    """)

                    # Extract validation errors from guardrail
                    if hasattr(guardrail_error, 'guardrail_result') and guardrail_error.guardrail_result:
                        output_info = guardrail_error.guardrail_result.output_info
                        if output_info and 'validation_errors' in output_info:
                            st.markdown("**Issues detected:**")
                            for error in output_info['validation_errors']:
                                st.markdown(f"- {error}")

                    st.info("""
                    **What to do:**
                    1. Try running the request again
                    2. If this persists, the AI may be struggling with your data
                    3. Check console logs for detailed guardrail messages
                    """)

                    error_msg = f"❌ Output validation failed: {str(guardrail_error)}"
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })

                except Exception as e:
                    import traceback
                    error_msg = f"❌ **Error:** {str(e)}"
                    st.error(error_msg)

                    # Show detailed traceback in expander
                    with st.expander("🔍 Technical Details"):
                        st.code(traceback.format_exc())

                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    })

    # Initial greeting
    if len(st.session_state.conversation_history) == 0:
        with st.chat_message("assistant"):
            categories = st.session_state.data_loader.get_categories()
            store_count = st.session_state.data_loader.get_store_count()

            greeting = f"""
👋 **Welcome! I'm your AI retail planning assistant.**

I've analyzed your uploaded data and I'm ready to help you create accurate forecasts and optimize inventory.

📊 **Your Loaded Data:**
- **Product Categories**: {', '.join(categories)}
- **Store Network**: {store_count} locations
- **AI Models**: Demand Forecasting, Inventory Optimization, Markdown Planning

🎯 **How I can help:**
- Generate demand forecasts for any category
- Plan inventory allocation across stores
- Recommend markdown strategies
- Optimize replenishment schedules

💡 **Try saying:**
- "I need help with forecasting"
- "Forecast women's dresses for 12 weeks"
- "Plan inventory with weekly replenishment"

I'll guide you with numbered options at each step!
            """
            st.markdown(greeting)
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": greeting,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🤖 Powered by OpenAI Agents SDK")
with col2:
    st.caption("📊 Retail Forecasting System v2.0")
with col3:
    st.caption(f"⚡ {datetime.now().strftime('%B %d, %Y')}")
