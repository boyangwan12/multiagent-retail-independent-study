"""
Retail Forecasting System - Streamlit UI
Interactive triage agent with NATIVE HANDOFFS to demand agent
Uses OpenAI Agents SDK Sessions for conversation memory
"""
import streamlit as st
from agents import Runner, set_tracing_disabled, SQLiteSession
from config import OPENAI_MODEL
from utils import SessionManager, TrainingDataLoader
from utils.context import ForecastingContext
from my_agents.triage_agent import create_triage_agent, ForecastParameters
from my_agents.demand_agent import demand_agent
import re
import pandas as pd

# ============================================================================
# RESULTS DISPLAY HELPERS
# ============================================================================

def _display_forecast_results(response: str):
    """Parse and display demand forecast results visually"""
    try:
        # Extract key metrics using regex
        total_demand = re.search(r'Total Demand.*?(\d+,?\d*)\s+units', response)
        weekly_avg = re.search(r'Weekly Average.*?(\d+,?\d*)\s+units', response)
        confidence = re.search(r'Forecast Confidence.*?(\d+)%', response)
        safety_stock = re.search(r'Safety Stock.*?(\d+)%', response)

        if total_demand or confidence:
            st.divider()
            st.subheader("📊 Forecast Summary Dashboard")

            # Metrics row
            cols = st.columns(4)
            if total_demand:
                cols[0].metric("Total Demand", f"{total_demand.group(1)} units")
            if weekly_avg:
                cols[1].metric("Weekly Average", f"{weekly_avg.group(1)} units/week")
            if confidence:
                conf_val = int(confidence.group(1))
                conf_delta = "Good" if conf_val >= 70 else "Fair" if conf_val >= 50 else "Poor"
                cols[2].metric("Confidence", f"{conf_val}%", delta=conf_delta)
            if safety_stock:
                cols[3].metric("Safety Stock", f"{safety_stock.group(1)}%")

            # Parse weekly breakdown if present
            weekly_match = re.search(r'Week \d+.*?(\d+,?\d*)\s+units', response)
            if weekly_match:
                st.caption("*Detailed weekly breakdown shown in chat above*")

    except Exception as e:
        # Silently fail - just show text response
        pass


def _display_inventory_results(response: str):
    """Parse and display inventory allocation results visually"""
    try:
        # Extract manufacturing and allocation metrics (handle various formats)
        manufacturing_qty = re.search(r'(?:Total Manufacturing|Manufacturing Quantity).*?(\d+,?\d*)\s+units', response, re.IGNORECASE)
        dc_holdback = re.search(r'DC Holdback.*?\((\d+)%\).*?(\d+,?\d*)\s+units|DC Holdback.*?(\d+,?\d*)\s+units', response, re.IGNORECASE)
        initial_alloc = re.search(r'Initial (?:Store )?Allocation.*?\((\d+)%\).*?(\d+,?\d*)\s+units|Initial (?:Store )?Allocation.*?(\d+,?\d*)\s+units', response, re.IGNORECASE)

        if manufacturing_qty or dc_holdback or initial_alloc:
            st.divider()
            st.subheader("🏭 Inventory Allocation Dashboard")

            # Top-level metrics
            cols = st.columns(3)
            if manufacturing_qty:
                cols[0].metric("Manufacturing Qty", f"{manufacturing_qty.group(1)} units",
                              help="Total units to manufacture (demand + safety stock)")
            if dc_holdback:
                # Handle different match groups
                pct = dc_holdback.group(1) if dc_holdback.group(1) else None
                units = dc_holdback.group(2) if dc_holdback.group(2) else dc_holdback.group(3)
                delta_text = f"{pct}%" if pct else None
                cols[1].metric("DC Holdback", f"{units} units",
                              delta=delta_text,
                              help="Units held at distribution center for replenishment")
            if initial_alloc:
                # Handle different match groups
                pct = initial_alloc.group(1) if initial_alloc.group(1) else None
                units = initial_alloc.group(2) if initial_alloc.group(2) else initial_alloc.group(3)
                cols[2].metric("Initial Store Allocation", f"{units} units",
                              help="Units allocated to stores initially")

            # Parse cluster information (handle multiple formats)
            cluster_data = []

            # Try format 1: "Fashion_Forward: 2,387 units (45.2%)"
            cluster_pattern1 = r'(\w+):\s*(\d+,?\d*)\s+units\s*\((\d+(?:\.\d+)?)%\)'
            for match in re.finditer(cluster_pattern1, response):
                cluster_name = match.group(1)
                if cluster_name in ['Fashion_Forward', 'Mainstream', 'Value_Conscious']:
                    cluster_data.append({
                        'Cluster': cluster_name.replace('_', ' '),
                        'Units': match.group(2),
                        'Percentage': f"{match.group(3)}%"
                    })

            # If that didn't work, try format 2: "Fashion_Forward (Cluster 0) ... Store Count: 18 stores"
            if not cluster_data:
                for cluster_name in ['Fashion_Forward', 'Mainstream', 'Value_Conscious']:
                    pattern = rf'\*\*{cluster_name}\*\*.*?Store Count:\s*(\d+)\s+stores.*?Allocation Weight:\s*(\d+(?:\.\d+)?)%'
                    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                    if match:
                        cluster_data.append({
                            'Cluster': cluster_name.replace('_', ' '),
                            'Stores': int(match.group(1)),
                            'Percentage': f"{match.group(2)}%"
                        })

            if cluster_data:
                st.divider()
                st.subheader("📊 Cluster Breakdown")

                # Display as columns with color coding
                cols = st.columns(len(cluster_data))
                colors = ['🔴', '🟡', '🟢']
                for idx, (col, cluster) in enumerate(zip(cols, cluster_data)):
                    with col:
                        st.markdown(f"### {colors[idx % 3]} {cluster['Cluster']}")
                        if 'Stores' in cluster:
                            st.metric("Stores", cluster['Stores'])
                        if 'Units' in cluster:
                            st.metric("Allocation", cluster['Units'])
                        st.caption(f"Share: {cluster['Percentage']}")

                # Display as table
                st.divider()
                df = pd.DataFrame(cluster_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

            # Check for store-level details
            store_count_match = re.search(r'allocated to (\d+) stores', response)
            if store_count_match:
                st.info(f"✅ Successfully allocated inventory to {store_count_match.group(1)} stores across all clusters")

    except Exception as e:
        # Silently fail - just show text response
        pass

# Configure page
st.set_page_config(
    page_title="Retail Planning",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.session_state.forecast_context = None  # Will be created after data upload

    # Create SDK Session for conversation memory
    st.session_state.sdk_session = SQLiteSession(
        session_id=st.session_state.session_id,
        db_path=":memory:"  # In-memory for now (could use file for persistence)
    )

# Title
st.title("📊 Retail Planning")
st.markdown("**AI-Powered Demand Forecasting & Inventory Planning**")
st.divider()

# Sidebar
with st.sidebar:
    st.header("📋 Session Info")
    st.caption(f"Session ID: {st.session_state.session_id[:8]}...")

    st.divider()

    st.header("ℹ️ Native Handoffs")
    st.info("✅ Triage → Demand Agent handoff enabled via OpenAI Agents SDK")
    st.caption("The system uses native agent-to-agent communication with automatic data fetching.")

    st.divider()

    # Quick actions
    st.header("⚙️ Actions")
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.session_manager.clear_session(st.session_state.session_id)
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content area
if not st.session_state.uploaded:
    # Upload section
    st.header("📤 Step 1: Upload Training Data")
    st.markdown("""
    Please upload your historical sales data and store attributes to begin.
    The agent will analyze your data and provide options based on your actual inventory.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Historical Sales Data")
        historical_file = st.file_uploader(
            "Upload historical_sales_2022_2024.csv",
            type=["csv"],
            key="historical",
            help="CSV file with columns: date, store_id, category, quantity_sold, revenue"
        )

        if historical_file:
            st.success(f"✅ {historical_file.name} uploaded")
            # Show preview
            import pandas as pd
            df = pd.read_csv(historical_file)
            st.dataframe(df.head(5), use_container_width=True)
            historical_file.seek(0)  # Reset file pointer

    with col2:
        st.subheader("Store Attributes")
        store_file = st.file_uploader(
            "Upload store_attributes.csv",
            type=["csv"],
            key="store",
            help="CSV file with store information: store_id, size_sqft, income_level, etc."
        )

        if store_file:
            st.success(f"✅ {store_file.name} uploaded")
            # Show preview
            import pandas as pd
            df = pd.read_csv(store_file)
            st.dataframe(df.head(5), use_container_width=True)
            store_file.seek(0)  # Reset file pointer

    # Process uploads
    if historical_file and store_file:
        if st.button("🚀 Process Data & Start Chat", type="primary", use_container_width=True):
            with st.spinner("Processing your data..."):
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

                # **CRITICAL**: Create ForecastingContext for tools
                # This context is passed to Runner and provides data_loader to all tools
                st.session_state.forecast_context = ForecastingContext(
                    data_loader=st.session_state.data_loader,
                    session_id=st.session_state.session_id
                )

                # Load data summary
                categories = st.session_state.data_loader.get_categories()
                store_count = st.session_state.data_loader.get_store_count()
                date_range = st.session_state.data_loader.get_date_range()

                # Create triage agent WITH native handoff to demand agent
                # The triage agent now has a tool: transfer_to_demand_agent(params)
                # When the LLM calls this tool, the SDK automatically hands off to demand_agent
                # The demand agent can then call run_demand_forecast(category, horizon) and
                # the tool will automatically fetch historical data via ctx.context.data_loader
                st.session_state.agent = create_triage_agent(
                    data_loader=st.session_state.data_loader,
                    demand_agent=demand_agent  # Enable native handoff
                )
                st.session_state.agent.model = OPENAI_MODEL

                # Mark as uploaded
                st.session_state.uploaded = True

                # Show success
                st.success(f"""
                ✅ Data processed successfully!

                - **Categories**: {', '.join(categories)}
                - **Stores**: {store_count}
                - **Date Range**: {date_range['start']} to {date_range['end']}
                """)

                st.balloons()
                st.rerun()

else:
    # Chat interface
    st.header("💬 Chat with Triage Agent")

    # Show data summary
    with st.expander("📊 Uploaded Data Summary", expanded=False):
        categories = st.session_state.data_loader.get_categories()
        store_count = st.session_state.data_loader.get_store_count()
        date_range = st.session_state.data_loader.get_date_range()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Product Categories", len(categories))
            st.caption(", ".join(categories))
        with col2:
            st.metric("Store Count", store_count)
        with col3:
            st.metric("Data Coverage", f"{date_range['start_year']}-{date_range['end_year']}")

    st.divider()

    # Display conversation history
    for msg in st.session_state.conversation_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here...", key="chat_input"):
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Run agent with Session for conversation memory AND Context for tool dependencies
                    res = Runner.run_sync(
                        starting_agent=st.session_state.agent,
                        input=prompt,
                        session=st.session_state.sdk_session,  # For conversation history
                        context=st.session_state.forecast_context  # For tool data access
                    )

                    # Extract response - handle different return types
                    if hasattr(res, 'final_output'):
                        response = res.final_output
                    elif hasattr(res, 'output'):
                        response = res.output
                    else:
                        response = str(res)

                    # Display response
                    st.markdown(response)

                    # ========================================
                    # ENHANCED RESULTS DISPLAY: Parse and visualize structured results
                    # ========================================
                    # Check if response contains inventory allocation results
                    if "🏭 Inventory Agent Active" in response or "Inventory Allocation Complete" in response:
                        _display_inventory_results(response)
                    elif "📊 Demand Forecast Complete" in response or "✅ **Demand Forecast Complete**" in response:
                        _display_forecast_results(response)

                    # ========================================
                    # NATIVE HANDOFF with CONTEXT: Runner handles everything automatically
                    # ========================================
                    # When triage agent calls transfer_to_demand_agent(), the SDK:
                    # 1. Pauses triage agent
                    # 2. Passes parameters to demand agent
                    # 3. Demand agent calls run_demand_forecast(ctx, category, horizon)
                    # 4. Tool fetches historical data from ctx.context.data_loader
                    # 5. Returns final result
                    # No manual orchestration or global state needed!

                    # Add to UI history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    import traceback
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)

                    # Show detailed traceback in expander
                    with st.expander("🔍 Error Details (for debugging)"):
                        st.code(traceback.format_exc())

                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })

    # Initial greeting - NO questions, just welcome
    if len(st.session_state.conversation_history) == 0:
        with st.chat_message("assistant"):
            categories = st.session_state.data_loader.get_categories()
            store_count = st.session_state.data_loader.get_store_count()

            greeting = f"""
👋 **Hello! I'm your retail planning assistant.**

I've analyzed your uploaded data and I'm ready to help you create forecasts.

📊 **Your Data:**
- **Categories**: {', '.join(categories)}
- **Stores**: {store_count}

**To get started, just type:**
- "I need help with forecasting"
- "Forecast women's dresses for 12 weeks"
- Or any question you have!

I'll guide you through with numbered options at each step. 🎯
            """
            st.markdown(greeting)
            st.session_state.conversation_history.append({
                "role": "assistant",
                "content": greeting
            })

# Footer
st.divider()
st.caption("Powered by OpenAI Agents SDK | Retail Forecasting System v1.0")
