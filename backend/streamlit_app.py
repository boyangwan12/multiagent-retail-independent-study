"""
Retail Forecasting System - Enhanced Streamlit UI
Professional UX with improved visual design and interactions
"""
import streamlit as st
from agents import Runner, set_tracing_disabled, SQLiteSession
from config import OPENAI_MODEL
from utils import SessionManager, TrainingDataLoader
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
    """Parse and display demand forecast results visually with enhanced charts"""
    try:
        # Extract key metrics using regex
        total_demand = re.search(r'Total Demand.*?(\d+,?\d*)\s+units', response)
        weekly_avg = re.search(r'Weekly Average.*?(\d+,?\d*)\s+units', response)
        confidence = re.search(r'Forecast Confidence.*?(\d+)%', response)
        safety_stock = re.search(r'Safety Stock.*?(\d+)%', response)

        if total_demand or confidence:
            st.divider()
            st.subheader("📊 Forecast Summary Dashboard")

            # Metrics row with enhanced styling
            cols = st.columns(4)
            if total_demand:
                cols[0].metric(
                    "Total Demand",
                    f"{total_demand.group(1)} units",
                    help="Predicted total units needed for the forecast period"
                )
            if weekly_avg:
                cols[1].metric(
                    "Weekly Average",
                    f"{weekly_avg.group(1)} units/week",
                    help="Average demand per week"
                )
            if confidence:
                conf_val = int(confidence.group(1))
                conf_delta = "High" if conf_val >= 70 else "Medium" if conf_val >= 50 else "Low"
                cols[2].metric(
                    "Confidence",
                    f"{conf_val}%",
                    delta=conf_delta,
                    help="Forecast reliability score"
                )
            if safety_stock:
                cols[3].metric(
                    "Safety Stock",
                    f"{safety_stock.group(1)}%",
                    help="Additional buffer inventory percentage"
                )

            # Parse weekly breakdown if present
            weekly_pattern = r'Week\s+(\d+).*?(\d+,?\d*)\s+units'
            weekly_matches = re.findall(weekly_pattern, response)

            if weekly_matches and len(weekly_matches) > 0:
                st.caption("📈 Weekly Breakdown")

                # Create DataFrame for chart
                weeks = [int(m[0]) for m in weekly_matches]
                units = [int(m[1].replace(',', '')) for m in weekly_matches]

                df_weekly = pd.DataFrame({
                    'Week': weeks,
                    'Forecast Units': units
                })

                # Display as line chart
                st.line_chart(df_weekly.set_index('Week'), use_container_width=True)

                # Store forecast data for variance checking
                st.session_state.forecast_by_week = units
                st.session_state.show_variance_section = True

    except Exception as e:
        # Silently fail - just show text response
        pass


def _display_inventory_results(response: str):
    """Parse and display inventory allocation results visually"""
    try:
        # Extract manufacturing and allocation metrics
        manufacturing_qty = re.search(r'(?:Total Manufacturing|Manufacturing Quantity).*?(\d+,?\d*)\s+units', response, re.IGNORECASE)
        dc_holdback = re.search(r'DC Holdback.*?\((\d+)%\).*?(\d+,?\d*)\s+units|DC Holdback.*?(\d+,?\d*)\s+units', response, re.IGNORECASE)
        initial_alloc = re.search(r'Initial (?:Store )?Allocation.*?\((\d+)%\).*?(\d+,?\d*)\s+units|Initial (?:Store )?Allocation.*?(\d+,?\d*)\s+units', response, re.IGNORECASE)

        if manufacturing_qty or dc_holdback or initial_alloc:
            st.divider()
            st.subheader("🏭 Inventory Allocation Dashboard")

            # Top-level metrics
            cols = st.columns(3)
            if manufacturing_qty:
                cols[0].metric(
                    "Manufacturing Qty",
                    f"{manufacturing_qty.group(1)} units",
                    help="Total units to manufacture (demand + safety stock)"
                )
            if dc_holdback:
                pct = dc_holdback.group(1) if dc_holdback.group(1) else None
                units = dc_holdback.group(2) if dc_holdback.group(2) else dc_holdback.group(3)
                delta_text = f"{pct}%" if pct else None
                cols[1].metric(
                    "DC Holdback",
                    f"{units} units",
                    delta=delta_text,
                    help="Units held at distribution center for replenishment"
                )
            if initial_alloc:
                pct = initial_alloc.group(1) if initial_alloc.group(1) else None
                units = initial_alloc.group(2) if initial_alloc.group(2) else initial_alloc.group(3)
                cols[2].metric(
                    "Initial Store Allocation",
                    f"{units} units",
                    help="Units allocated to stores initially"
                )

            # Parse cluster information
            cluster_data = []
            cluster_pattern = r'(\w+):\s*(\d+,?\d*)\s+units\s*\((\d+(?:\.\d+)?)%\)'

            for match in re.finditer(cluster_pattern, response):
                cluster_name = match.group(1)
                if cluster_name in ['Fashion_Forward', 'Mainstream', 'Value_Conscious']:
                    cluster_data.append({
                        'Cluster': cluster_name.replace('_', ' '),
                        'Units': match.group(2),
                        'Percentage': float(match.group(3))
                    })

            if cluster_data:
                st.caption("📊 Cluster Distribution")
                df_clusters = pd.DataFrame(cluster_data)

                # Display as bar chart
                st.bar_chart(df_clusters.set_index('Cluster')['Percentage'], use_container_width=True)

                # Also show table
                with st.expander("📋 Detailed Cluster Breakdown"):
                    st.dataframe(df_clusters, use_container_width=True, hide_index=True)

    except Exception as e:
        # Silently fail
        pass

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

# Sidebar
with st.sidebar:
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

    # Help & Tips
    st.markdown("### 💡 Tips")
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        **Getting Started:**
        1. Upload your data files
        2. Start chatting with the AI assistant
        3. Follow numbered options for guidance

        **Pro Tips:**
        - Be specific about your forecast period
        - Mention the product category
        - Ask follow-up questions anytime
        """)

    with st.expander("🎯 Example Prompts"):
        st.markdown("""
        Try these:
        - "Forecast women's dresses for 12 weeks"
        - "Plan inventory with weekly replenishment"
        - "I need markdown planning at week 6"
        """)

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

    # Variance Checking Section (appears after forecast is generated)
    if st.session_state.show_variance_section and len(st.session_state.forecast_by_week) > 0:
        st.divider()
        with st.expander("📈 Upload Actual Sales Data & Check Variance", expanded=False):
            st.markdown("""
            Upload weekly actual sales data to compare against your forecast.
            The system will analyze variance and recommend re-forecasting if needed.
            """)

            col1, col2 = st.columns([2, 1])

            with col1:
                # File uploader for actual sales
                actuals_file = st.file_uploader(
                    "📊 Upload Actual Sales CSV",
                    type=["csv"],
                    key="actuals_upload",
                    help="CSV with columns: date, store_id, quantity_sold"
                )

                if actuals_file:
                    st.success(f"✅ **{actuals_file.name}**")

                    # Show preview
                    df_actuals = pd.read_csv(actuals_file)
                    with st.expander("👁️ Preview Data"):
                        st.dataframe(df_actuals.head(10), use_container_width=True)

                    actuals_file.seek(0)

            with col2:
                # Week number selector
                max_weeks = len(st.session_state.forecast_by_week)
                week_num = st.number_input(
                    "Week Number",
                    min_value=1,
                    max_value=max_weeks,
                    value=1,
                    help=f"Select which week to check (1-{max_weeks})"
                )

                # Variance threshold
                variance_threshold = st.slider(
                    "Variance Threshold %",
                    min_value=5,
                    max_value=30,
                    value=15,
                    help="Threshold to trigger re-forecast recommendation"
                ) / 100

            # Check variance button
            if actuals_file and st.button("🔍 Check Variance", type="primary", use_container_width=True):
                with st.spinner("Analyzing variance..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = f".sessions/{st.session_state.session_id}_actuals_week_{week_num}.csv"
                        os.makedirs(os.path.dirname(temp_path), exist_ok=True)

                        with open(temp_path, "wb") as f:
                            f.write(actuals_file.getvalue())

                        # Run variance check
                        variance_result = check_variance(
                            actual_sales_csv=temp_path,
                            forecast_by_week=st.session_state.forecast_by_week,
                            week_number=week_num,
                            variance_threshold=variance_threshold
                        )

                        # Display results
                        st.divider()
                        st.subheader(f"📊 Variance Analysis - Week {week_num}")

                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Actual Sales", f"{variance_result.actual_total:,} units")
                        col2.metric("Forecasted", f"{variance_result.forecast_total:,} units")

                        variance_pct_display = abs(variance_result.variance_pct) * 100
                        col3.metric(
                            "Variance",
                            f"{variance_pct_display:.1f}%",
                            delta="High" if variance_result.is_high_variance else "OK",
                            delta_color="inverse" if variance_result.is_high_variance else "normal"
                        )

                        status_emoji = "⚠️" if variance_result.is_high_variance else "✅"
                        col4.metric("Status", f"{status_emoji} {'High Variance' if variance_result.is_high_variance else 'On Track'}")

                        # Recommendation
                        if variance_result.is_high_variance:
                            st.error(variance_result.recommendation)

                            # Offer to re-forecast
                            st.markdown("**Would you like to re-forecast with updated data?**")
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✅ Yes, Re-forecast Now", use_container_width=True):
                                    st.session_state.quick_prompt = "Re-forecast with the latest data"
                                    st.rerun()
                            with col_b:
                                if st.button("📊 View Detailed Analysis", use_container_width=True):
                                    st.info("Detailed variance analysis would be shown here")
                        else:
                            st.success(variance_result.recommendation)

                        # Store result
                        st.session_state.variance_results.append(variance_result)

                    except Exception as e:
                        st.error(f"Error checking variance: {str(e)}")
                        import traceback
                        with st.expander("Technical Details"):
                            st.code(traceback.format_exc())

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
                    # Run agent
                    res = Runner.run_sync(
                        starting_agent=st.session_state.agent,
                        input=prompt,
                        session=st.session_state.sdk_session,
                        context=st.session_state.forecast_context
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

                    # Enhanced results display
                    if "🏭 Inventory Agent Active" in response or "Inventory Allocation Complete" in response:
                        _display_inventory_results(response)
                    elif "📊 Demand Forecast Complete" in response or "✅ **Demand Forecast Complete**" in response:
                        _display_forecast_results(response)

                    # Add to history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response,
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
