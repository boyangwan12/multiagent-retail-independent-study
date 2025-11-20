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
        # Check if this is a re-forecast
        is_reforecast = re.search(r'Re-Forecast Complete|Updated Forecast|Re-forecasting', response, re.IGNORECASE)

        # Extract key metrics using regex
        total_demand = re.search(r'Total Demand.*?(\d+,?\d*)\s+units', response)
        weekly_avg = re.search(r'Weekly Average.*?(\d+,?\d*)\s+units', response)
        confidence = re.search(r'Forecast Confidence.*?(\d+)%', response)
        safety_stock = re.search(r'Safety Stock.*?(\d+)%', response)

        if total_demand or confidence:
            st.divider()

            # Different header for re-forecast
            if is_reforecast:
                st.subheader("🔄 Updated Forecast Summary Dashboard")
                st.success("**✅ Re-forecast complete!** New forecast incorporates actual sales data for improved accuracy.")
            else:
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

                # Parse and display detailed cluster characteristics
                st.divider()
                st.subheader("🎯 Cluster Characteristics")

                # Extract cluster characteristics from response
                # Pattern: Fashion_Forward (Cluster 0)
                #   - Store Count: 18 stores (36%)
                #   - Allocation Weight: 45.2%
                #   - Characteristics:
                #     * Avg Weekly Sales: $850
                #     * Avg Store Size: 52,000 sqft
                #     * Avg Median Income: $85,000

                cluster_details = []

                # Try to extract cluster info blocks
                cluster_blocks = re.findall(
                    r'(\d+)\.\s+\*\*([^*]+)\*\*[^-]+'
                    r'-\s+Store Count:\s+(\d+)\s+stores[^-]+'
                    r'-\s+Allocation Weight:\s+([\d.]+)%[^*]+'
                    r'\*\s+Avg Weekly Sales:\s+\$?([\d,]+)[^*]+'
                    r'\*\s+Avg Store Size:\s+([\d,]+)\s+sqft[^*]+'
                    r'\*\s+Avg Median Income:\s+\$?([\d,]+)',
                    response,
                    re.DOTALL
                )

                if cluster_blocks:
                    for block in cluster_blocks:
                        num, name, store_count, alloc_weight, avg_sales, avg_size, avg_income = block
                        cluster_details.append({
                            'Cluster': name.strip(),
                            'Stores': int(store_count),
                            'Allocation': f"{float(alloc_weight):.1f}%",
                            'Avg Weekly Sales': f"${int(avg_sales.replace(',', '')):,}",
                            'Avg Store Size': f"{int(avg_size.replace(',', '')):,} sqft",
                            'Avg Median Income': f"${int(avg_income.replace(',', '')):,}"
                        })

                if cluster_details:
                    # Display each cluster as a card with key metrics
                    cols = st.columns(len(cluster_details))

                    for idx, cluster in enumerate(cluster_details):
                        with cols[idx]:
                            # Determine emoji based on cluster type
                            if 'Fashion' in cluster['Cluster'] or 'Forward' in cluster['Cluster']:
                                emoji = "💎"
                            elif 'Mainstream' in cluster['Cluster']:
                                emoji = "🏬"
                            else:
                                emoji = "🏪"

                            st.markdown(f"### {emoji} {cluster['Cluster']}")
                            st.metric("Store Count", cluster['Stores'])
                            st.metric("Allocation", cluster['Allocation'])

                            with st.expander("📊 Details"):
                                st.write(f"**Avg Weekly Sales:** {cluster['Avg Weekly Sales']}")
                                st.write(f"**Avg Store Size:** {cluster['Avg Store Size']}")
                                st.write(f"**Avg Median Income:** {cluster['Avg Median Income']}")

                    # Add comparative visualization
                    st.caption("📈 Cluster Comparison")

                    # Create comparison dataframe for visualization
                    comparison_data = []
                    for cluster in cluster_details:
                        # Extract numeric values for comparison
                        sales = int(cluster['Avg Weekly Sales'].replace('$', '').replace(',', ''))
                        size = int(cluster['Avg Store Size'].replace(',', '').replace(' sqft', ''))
                        income = int(cluster['Avg Median Income'].replace('$', '').replace(',', ''))

                        comparison_data.append({
                            'Cluster': cluster['Cluster'].replace('_', ' '),
                            'Weekly Sales ($)': sales,
                            'Store Size (sqft)': size,
                            'Median Income ($)': income
                        })

                    if comparison_data:
                        df_comparison = pd.DataFrame(comparison_data)

                        # Show comparison in expandable section
                        with st.expander("📊 Visual Comparison", expanded=False):
                            # Normalize data for better visualization
                            metric_choice = st.radio(
                                "Compare by:",
                                ["Weekly Sales ($)", "Store Size (sqft)", "Median Income ($)"],
                                horizontal=True
                            )

                            chart_data = df_comparison.set_index('Cluster')[[metric_choice]]
                            st.bar_chart(chart_data, use_container_width=True)
                else:
                    # Fallback: show basic cluster summary table
                    with st.expander("📋 Detailed Cluster Breakdown"):
                        st.dataframe(df_clusters, use_container_width=True, hide_index=True)

        # Parse store-level allocations
        st.divider()
        st.subheader("🏪 Store-Level Allocations")

        # Extract store allocations with cluster and factor (enhanced pattern)
        # Pattern: STORE001: 156 units (Fashion_Forward, factor: 1.2×)
        store_pattern_enhanced = r'(STORE\d+):\s*(\d+)\s+units\s*\(([^,]+),\s*factor:\s*([\d.]+)'
        store_matches_enhanced = re.findall(store_pattern_enhanced, response)

        # Fallback to simple pattern if enhanced doesn't match
        if not store_matches_enhanced or len(store_matches_enhanced) == 0:
            store_pattern = r'(STORE\d+).*?(\d+)\s+units'
            store_matches = re.findall(store_pattern, response)

            if store_matches and len(store_matches) > 0:
                store_allocations = []
                for match in store_matches[:50]:
                    store_allocations.append({
                        'Store ID': match[0],
                        'Allocated Units': int(match[1]),
                        'Cluster': 'N/A',
                        'Factor': 'N/A'
                    })
            else:
                store_allocations = []
        else:
            # Use enhanced data with cluster and factor
            store_allocations = []
            for match in store_matches_enhanced[:50]:
                store_id, units, cluster, factor = match
                store_allocations.append({
                    'Store ID': store_id,
                    'Allocated Units': int(units),
                    'Cluster': cluster.strip(),
                    'Factor': f"{float(factor):.2f}×"
                })

        if store_allocations:
            df_stores = pd.DataFrame(store_allocations)

            # Show summary stats
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Stores", len(df_stores))
            col2.metric("Avg Allocation", f"{df_stores['Allocated Units'].mean():.0f} units")
            col3.metric("Total Allocated", f"{df_stores['Allocated Units'].sum():,} units")

            # Add min/max for context
            col4.metric("Range", f"{df_stores['Allocated Units'].min()}-{df_stores['Allocated Units'].max()}")

            # Show top 10 stores with enhanced formatting
            with st.expander("🔝 Top 10 Stores by Allocation", expanded=False):
                top_10 = df_stores.nlargest(10, 'Allocated Units')

                # Add rank column for top 10
                top_10_display = top_10.copy()
                top_10_display.insert(0, 'Rank', range(1, len(top_10) + 1))

                st.dataframe(
                    top_10_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Rank": st.column_config.NumberColumn("🏆 Rank", width="small"),
                        "Store ID": st.column_config.TextColumn("Store ID", width="medium"),
                        "Allocated Units": st.column_config.NumberColumn("Units", format="%d units", width="medium"),
                        "Cluster": st.column_config.TextColumn("Cluster", width="medium"),
                        "Factor": st.column_config.TextColumn("Factor", width="small")
                    }
                )

            # Show all stores in searchable table with enhanced display
            with st.expander("📋 All Store Allocations (Searchable)", expanded=False):
                st.caption(f"Showing all {len(df_stores)} stores - sorted by allocation (highest first)")

                df_display = df_stores.sort_values('Allocated Units', ascending=False).copy()

                # Add allocation tier for visual context (Low/Medium/High)
                if 'Allocated Units' in df_display.columns:
                    median_allocation = df_display['Allocated Units'].median()
                    q75 = df_display['Allocated Units'].quantile(0.75)
                    q25 = df_display['Allocated Units'].quantile(0.25)

                    def allocation_tier(units):
                        if units >= q75:
                            return "🟢 High"
                        elif units >= q25:
                            return "🟡 Medium"
                        else:
                            return "🔴 Low"

                    df_display.insert(1, 'Tier', df_display['Allocated Units'].apply(allocation_tier))

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    height=400,
                    column_config={
                        "Store ID": st.column_config.TextColumn("Store ID", width="medium"),
                        "Tier": st.column_config.TextColumn("Tier", width="small", help="High (top 25%), Medium (middle 50%), Low (bottom 25%)"),
                        "Allocated Units": st.column_config.NumberColumn("Allocated Units", format="%d units", width="medium"),
                        "Cluster": st.column_config.TextColumn("Cluster", width="medium"),
                        "Factor": st.column_config.TextColumn("Allocation Factor", width="small", help="Multiplier based on 70% historical + 30% attributes")
                    }
                )

                # Add legend
                st.caption("🟢 High = Top 25% | 🟡 Medium = Middle 50% | 🔴 Low = Bottom 25%")
        else:
            # If pattern matching fails, show a message to check detailed response
            st.info("💡 Store-level allocations are available in the AI response above. Scroll up to see individual store details.")

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
    st.session_state.allocation_complete = False  # Track if allocation was completed (for variance section expansion)

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

    # In-Season Planning Section (appears after forecast is generated)
    if st.session_state.show_variance_section and len(st.session_state.forecast_by_week) > 0:
        st.divider()
        st.markdown("## 🎯 In-Season Planning & Variance Checking")

        st.success("""
        **📊 Your forecast is active!** Once your season is underway, upload actual sales data below to:
        - ✅ Validate forecast accuracy
        - ⚠️ Detect high variance (>15%)
        - 🔄 Trigger automatic re-forecasting if needed
        - 📈 Continuously improve predictions
        """)

        # Expand on first view after allocation, then collapse
        is_first_view = st.session_state.allocation_complete and not st.session_state.variance_results
        with st.expander("📈 **Upload Actual Sales Data** (Click to Open)", expanded=is_first_view):
            st.markdown("""
            Upload weekly actual sales data to let the AI analyze forecast performance.
            Just upload the file below and ask the AI to "check variance for week X".
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

            # Save uploaded file and prompt user to use chat
            if actuals_file and st.button("💾 Save File & Ask AI to Analyze", type="primary", use_container_width=True):
                with st.spinner("Saving file..."):
                    try:
                        # Save uploaded file to the same session directory as other data files
                        session_dir = st.session_state.session_manager.get_session_dir(st.session_state.session_id)
                        temp_path = os.path.join(session_dir, f"actuals_week_{week_num}.csv")

                        with open(temp_path, "wb") as f:
                            f.write(actuals_file.getvalue())

                        st.success(f"✅ File saved successfully!")
                        st.caption(f"📁 Saved to: {temp_path}")

                        # Auto-populate chat with variance check request (simplified - no file paths needed)
                        suggested_prompt = f"Check variance for week {week_num} using the uploaded actual sales data. Use {int(variance_threshold*100)}% variance threshold."

                        st.info(f"**Suggested prompt:**\n\n{suggested_prompt}")
                        st.caption(f"📁 File stored in context (like historical sales and store data)")

                        # Store file path in session state for agent to access
                        st.session_state.variance_file_path = temp_path
                        st.session_state.variance_week = week_num
                        st.session_state.variance_threshold = variance_threshold

                        # Option to use suggested prompt
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("🚀 Use This Prompt", use_container_width=True, key="use_variance_prompt"):
                                st.session_state.quick_prompt = suggested_prompt
                                st.rerun()
                        with col_b:
                            if st.button("✏️ Write Your Own", use_container_width=True, key="write_own_variance"):
                                st.info("Scroll down to the chat input and type your own question!")

                    except Exception as e:
                        st.error(f"Error saving file: {str(e)}")
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
                    # Update context with variance data if available
                    if hasattr(st.session_state, 'variance_file_path') and st.session_state.variance_file_path:
                        st.session_state.forecast_context.variance_file_path = st.session_state.variance_file_path

                    if hasattr(st.session_state, 'variance_week'):
                        st.session_state.forecast_context.variance_week = st.session_state.variance_week
                    if hasattr(st.session_state, 'variance_threshold'):
                        st.session_state.forecast_context.variance_threshold = st.session_state.variance_threshold
                    if hasattr(st.session_state, 'forecast_by_week') and len(st.session_state.forecast_by_week) > 0:
                        st.session_state.forecast_context.forecast_by_week = st.session_state.forecast_by_week

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
                    if "Variance Analysis" in response or "check variance" in prompt.lower():
                        _display_variance_results(response)
                    elif "🏭 Inventory Agent Active" in response or "Inventory Allocation Complete" in response or "Allocation Complete" in response:
                        _display_inventory_results(response)
                        # Mark allocation as complete to expand variance section
                        st.session_state.allocation_complete = True
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
