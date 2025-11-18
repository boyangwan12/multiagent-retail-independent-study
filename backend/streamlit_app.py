"""
Retail Forecasting System - Streamlit UI
Interactive triage agent with data upload capability
"""
import streamlit as st
from agents import Runner, set_tracing_disabled
from config import OPENAI_MODEL
from utils import SessionManager, TrainingDataLoader
from my_agents.triage_agent import create_triage_agent

# Configure page
st.set_page_config(
    page_title="Retail Forecasting System",
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
    st.session_state.gathered_parameters = {}
    st.session_state.agent_messages = []  # Store agent conversation context

# Title
st.title("📊 Retail Forecasting System")
st.markdown("**AI-Powered Demand Forecasting & Inventory Planning**")
st.divider()

# Sidebar - Parameter Summary
with st.sidebar:
    st.header("📋 Session Info")
    st.caption(f"Session ID: {st.session_state.session_id[:8]}...")

    st.divider()

    st.header("📦 Gathered Parameters")
    if st.session_state.gathered_parameters:
        for key, value in st.session_state.gathered_parameters.items():
            st.text(f"• {key}: {value}")
    else:
        st.info("No parameters gathered yet")

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

                # Load data summary
                categories = st.session_state.data_loader.get_categories()
                store_count = st.session_state.data_loader.get_store_count()
                date_range = st.session_state.data_loader.get_date_range()

                # Create agent with this data
                st.session_state.agent = create_triage_agent(st.session_state.data_loader)
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
                    # Build message history for agent context
                    # Include previous messages to maintain context
                    if len(st.session_state.agent_messages) > 0:
                        # Continue existing conversation
                        context_messages = st.session_state.agent_messages.copy()
                        context_messages.append({"role": "user", "content": prompt})
                        full_input = "\n\n".join([
                            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                            for msg in context_messages
                        ])
                    else:
                        # First message
                        full_input = prompt
                        st.session_state.agent_messages.append({"role": "user", "content": prompt})

                    # Run agent with context
                    res = Runner.run_sync(
                        starting_agent=st.session_state.agent,
                        input=full_input if len(st.session_state.agent_messages) > 1 else prompt
                    )

                    response = res.final_output

                    # Save to agent message history
                    if len(st.session_state.agent_messages) == 1:
                        # First exchange
                        st.session_state.agent_messages.append({"role": "assistant", "content": response})
                    else:
                        # Add latest exchange
                        st.session_state.agent_messages[-1] = {"role": "user", "content": prompt}
                        st.session_state.agent_messages.append({"role": "assistant", "content": response})

                    # Display response
                    st.markdown(response)

                    # Check if parameters are being confirmed (agent always ends with this phrase)
                    if "All parameters gathered successfully!" in response:
                        st.divider()
                        st.success("✅ All parameters gathered successfully!")

                        # Parse parameters from response
                        params = {}
                        lines = response.split('\n')
                        for line in lines:
                            if ':' in line:
                                key_value = line.split(':', 1)
                                if len(key_value) == 2:
                                    key = key_value[0].strip().replace('*', '').replace('#', '')
                                    value = key_value[1].strip()
                                    if key and value and len(key) < 50:  # Reasonable key length
                                        params[key] = value

                        # Display in nice format
                        if params:
                            st.markdown("### 📋 Confirmed Parameters")

                            # Use columns for better layout
                            col1, col2 = st.columns(2)

                            param_list = list(params.items())
                            mid_point = (len(param_list) + 1) // 2

                            with col1:
                                for key, value in param_list[:mid_point]:
                                    st.metric(label=key, value=value)

                            with col2:
                                for key, value in param_list[mid_point:]:
                                    st.metric(label=key, value=value)

                            # Update sidebar
                            st.session_state.gathered_parameters = params

                        st.divider()
                        st.info("🚀 **Next Steps:** The agent will hand off to the Demand Agent for forecasting...")

                    # Add to UI history
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": response
                    })

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
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
