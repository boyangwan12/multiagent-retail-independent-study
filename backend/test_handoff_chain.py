"""Test to see if handoffs complete in a single Runner.run_sync() call"""

from agents import Runner, SQLiteSession
from my_agents.triage_agent import create_triage_agent
from my_agents.demand_agent import demand_agent
from utils import get_data_loader, ForecastingContext
import os

# Setup
data_loader = get_data_loader()
session_id = "test_handoff_chain"
session = SQLiteSession(f".sessions/{session_id}.db")
forecast_context = ForecastingContext(data_loader=data_loader, session_id=session_id)

# Create triage agent with demand agent linked
triage = create_triage_agent(data_loader=data_loader, demand_agent=demand_agent)

print("=" * 80)
print("TEST: Multi-agent handoff chain")
print("=" * 80)

# Simulate user providing parameters and confirming
messages = [
    "Forecast Accessories for 12 weeks",  # Triage: category and horizon
    "1",  # Triage: Next Monday for start date
    "1",  # Triage: Weekly replenishment
    "1",  # Triage: 45% DC holdback
    "1",  # Triage: No markdown planning
    "1",  # Triage: Confirm parameters → handoff to Demand Agent
    "1",  # Demand: After forecast, proceed with inventory → handoff to Inventory Agent
]

output_file = open("test_handoff_output.txt", "w", encoding="utf-8")

for i, msg in enumerate(messages):
    print(f"\n{'=' * 80}")
    print(f"Message {i+1}: {msg}")
    print(f"{'=' * 80}\n")
    output_file.write(f"\n{'=' * 80}\n")
    output_file.write(f"Message {i+1}: {msg}\n")
    output_file.write(f"{'=' * 80}\n\n")

    try:
        result = Runner.run_sync(
            starting_agent=triage,
            input=msg,
            session=session,
            context=forecast_context
        )

        output = result.final_output if hasattr(result, 'final_output') else str(result)

        # Write to file first (avoid encoding issues with console)
        output_file.write(output)
        output_file.write("\n\n")

        # Check which agent produced the output
        if "Triage Agent" in output or "parameters" in output.lower():
            output_file.write("[INFO] Triage agent is active\n")
        elif "Demand Forecasting Agent Active" in output or "Demand Forecast Complete" in output:
            output_file.write("[INFO] Demand agent is active\n")
        elif "Inventory Agent Active" in output or "Inventory Allocation Complete" in output:
            output_file.write("[INFO] Inventory agent is active!\n")
        else:
            output_file.write("[INFO] Unknown agent state\n")

        output_file.flush()  # Ensure it's written immediately

    except Exception as e:
        output_file.write(f"ERROR: {e}\n")
        import traceback
        output_file.write(traceback.format_exc())
        output_file.flush()

output_file.close()
print(f"\nOutput written to test_handoff_output.txt")
