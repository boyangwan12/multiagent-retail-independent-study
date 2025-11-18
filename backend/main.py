from agents import Runner, set_tracing_disabled
from config import OPENAI_MODEL, GEMINI_MODEL
from utils import get_data_loader
from my_agents.triage_agent import triage_agent
from my_agents.demand_agent import demand_agent

set_tracing_disabled(True)
ACTIVE_MODEL = GEMINI_MODEL

triage_agent.model = ACTIVE_MODEL
demand_agent.model = ACTIVE_MODEL

# Load and display available data
data_loader = get_data_loader()
categories = data_loader.get_categories()
store_count = data_loader.get_store_count()
date_range = data_loader.get_date_range()

print(f"Using model: {ACTIVE_MODEL.model}")
print("=" * 60)
print("RETAIL FORECASTING SYSTEM - Training Data Loaded")
print("=" * 60)
print(f"Available Categories: {', '.join(categories)}")
print(f"Store Network: {store_count} stores")
print(f"Historical Data: {date_range['start']} to {date_range['end']}")
print("-" * 60)
print("Interactive Triage Agent - Parameter Gathering")
print("Type 'quit' or 'exit' to end the conversation")
print("-" * 60)

# Initialize conversation state
context = []

# Get initial message from user
print("\nWelcome! Please describe what you need to forecast:\n")
user_input = input("You: ").strip()

if not user_input:
    print("No input provided. Exiting.")
    exit()

print()  # Add blank line for readability

while True:
    # Run the agent with current input
    res = Runner.run_sync(
        starting_agent=triage_agent,
        input=user_input,
        context=context if context else None
    )

    # Display agent response
    print(f"Agent: {res.final_output}\n")

    # Check if conversation is complete
    if hasattr(res, 'is_complete') and res.is_complete:
        print("\n" + "=" * 50)
        print("Conversation complete!")
        print("=" * 50)
        break

    # Get user input
    try:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nExiting conversation.")
            break
        if not user_input:
            print("Please enter a message.")
            continue
        print()  # Add blank line for readability

        # Update context with conversation history
        context.append({"role": "user", "content": user_input})

    except KeyboardInterrupt:
        print("\n\nExiting conversation.")
        break
    except EOFError:
        print("\n\nExiting conversation.")
        break




