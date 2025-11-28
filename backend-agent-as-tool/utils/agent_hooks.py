"""
Agent Lifecycle Hooks for Streamlit UI Integration

Provides event-based completion detection for agents instead of brittle string matching.
Uses OpenAI Agents SDK lifecycle hooks to trigger Streamlit visualizations and
real-time execution monitoring.

Integrates with the Phased Progress Tracker sidebar for visual workflow status.
"""

from agents import RunHooks
from typing import Any
from datetime import datetime

# Import phase tracking functions
from utils.sidebar_monitor import (
    start_phase,
    complete_phase,
    skip_phase,
    set_phase_tool,
    set_phase_message,
    initialize_phase_state,
    reset_workflow_phases,
)


class StreamlitVisualizationHooks(RunHooks):
    """
    Run-level hooks that detect agent execution events and trigger Streamlit UI updates.

    This replaces the previous string pattern matching approach with reliable
    event-based detection using the OpenAI Agents SDK lifecycle hooks.

    Provides:
    - Agent start/end detection for active status
    - LLM thinking indicators
    - Tool execution tracking
    - Real-time progress monitoring
    """

    def __init__(self, st_session_state=None):
        """
        Initialize with Streamlit session state for UI updates

        Args:
            st_session_state: Streamlit session_state object for storing completion signals
        """
        self.st_session_state = st_session_state

        # Initialize tracking lists if not present
        if st_session_state:
            if not hasattr(st_session_state, 'agent_timeline'):
                st_session_state.agent_timeline = []
            if not hasattr(st_session_state, 'tools_executing'):
                st_session_state.tools_executing = []
            if not hasattr(st_session_state, 'completed_tools'):
                st_session_state.completed_tools = []
            if not hasattr(st_session_state, 'llm_calls'):
                st_session_state.llm_calls = []

    # ==================== AGENT LIFECYCLE ====================

    async def on_agent_start(self, ctx, agent) -> None:
        """
        Called BEFORE agent is invoked.

        Use this to show which agent is currently active in the sidebar.
        Also triggers phase start in the Phased Progress Tracker.
        """
        if not self.st_session_state:
            return

        agent_name = getattr(agent, 'name', 'Unknown Agent')
        print(f"[AGENT START] {agent_name}")

        # Update active agent in session state
        self.st_session_state.active_agent = agent_name
        self.st_session_state.agent_is_running = True

        # Add to timeline
        self.st_session_state.agent_timeline.append({
            'agent': agent_name,
            'event': 'started',
            'timestamp': datetime.now().isoformat()
        })

        # ==================== PHASE TRACKING ====================
        # Map agent names to workflow phases
        phase_name = self._get_phase_for_agent(agent_name)
        if phase_name:
            start_phase(self.st_session_state, phase_name, f"Running {agent_name}...")
            print(f"📊 [PHASE] Started phase: {phase_name}")

        print(f"✨ [HOOK] Agent '{agent_name}' is now ACTIVE")

    def _get_phase_for_agent(self, agent_name: str) -> str:
        """Map agent name to workflow phase name."""
        agent_lower = agent_name.lower()

        if 'demand' in agent_lower or 'forecast' in agent_lower:
            # Check if this is a reforecast (variance triggered)
            if getattr(self.st_session_state, 'variance_check_completed', False):
                return 'reforecast'
            return 'forecast'
        elif 'inventory' in agent_lower or 'allocation' in agent_lower:
            return 'allocation'
        elif 'variance' in agent_lower:
            return 'variance'
        elif 'coordinator' in agent_lower:
            # Coordinator doesn't map to a specific phase
            return None

        return None

    async def on_agent_end(self, ctx, agent, output: Any) -> None:
        """
        Called when ANY agent in the run completes.

        This hook identifies which agent completed and captures structured data
        from agents that have output_type defined.

        Args:
            ctx: Run context
            agent: The agent that just completed
            output: The agent's final output (AgentResult object)
        """
        if not self.st_session_state:
            return

        agent_name = agent.name if hasattr(agent, 'name') else str(agent)

        # Log completion for debugging
        print(f"[LIFECYCLE HOOK] Agent completed: {agent_name}")
        print(f"[LIFECYCLE HOOK] Output type: {type(output)}")

        # NEW APPROACH: Extract structured data from AgentResult.final_output_as()
        # When agent has output_type, the structured data is in the result object

        # Detect Demand Forecasting Agent completion
        if "Demand" in agent_name or "Forecasting" in agent_name:
            self.st_session_state.demand_agent_completed = True
            self.st_session_state.demand_agent_output = output

            # Try to extract structured ForecastResult from output
            if hasattr(output, 'final_output_as'):
                try:
                    from agent_tools.demand_tools import ForecastResult
                    forecast_result = output.final_output_as(ForecastResult)
                    self.st_session_state.demand_forecast_data = forecast_result.model_dump()
                    print(f"✅ [HOOK] Demand agent structured data captured via output_type")
                    print(f"[HOOK DEBUG] Data keys: {list(self.st_session_state.demand_forecast_data.keys())}")
                except Exception as e:
                    print(f"⚠️ [HOOK] Could not extract structured forecast data: {e}")
            else:
                print(f"⚠️ [HOOK] Output doesn't have final_output_as method")

            print(f"✅ [HOOK] Demand agent completion flag set")

        # Detect Inventory Agent completion
        elif "Inventory" in agent_name or "Allocation" in agent_name:
            # Check if this is a variance check or allocation
            output_str = str(output).lower() if output else ""

            if "variance" in output_str:
                self.st_session_state.variance_check_completed = True
                self.st_session_state.variance_output = output
                print(f"✅ [HOOK] Variance check completion flag set")
            else:
                self.st_session_state.inventory_agent_completed = True
                self.st_session_state.inventory_agent_output = output

                # Try to extract structured allocation data
                if hasattr(output, 'final_output_as'):
                    try:
                        from agent_tools.inventory_tools import AllocationResult
                        allocation_result = output.final_output_as(AllocationResult)
                        self.st_session_state.inventory_allocation_data = allocation_result.model_dump()
                        print(f"✅ [HOOK] Inventory agent structured data captured via output_type")
                    except Exception as e:
                        print(f"⚠️ [HOOK] Could not extract structured allocation data: {e}")

                print(f"✅ [HOOK] Inventory agent completion flag set")

        # Mark agent as no longer running
        self.st_session_state.agent_is_running = False

        # Add to timeline
        self.st_session_state.agent_timeline.append({
            'agent': agent_name,
            'event': 'completed',
            'timestamp': datetime.now().isoformat()
        })

        # ==================== PHASE TRACKING ====================
        # Complete the phase for this agent
        phase_name = self._get_phase_for_agent(agent_name)
        if phase_name:
            complete_phase(self.st_session_state, phase_name)
            print(f"📊 [PHASE] Completed phase: {phase_name}")

        print(f"✅ [HOOK] Agent '{agent_name}' completed")

    # ==================== LLM LIFECYCLE ====================

    async def on_llm_start(self, ctx, agent, instructions, input_data) -> None:
        """
        Called just BEFORE invoking the LLM.

        Use this to show a "thinking..." indicator in the sidebar.

        Args:
            ctx: Run context
            agent: The agent making the LLM call
            instructions: The instructions being sent to the LLM
            input_data: The input data being sent to the LLM
        """
        if not self.st_session_state:
            return

        agent_name = getattr(agent, 'name', 'Unknown Agent')
        print(f"[LLM START] {agent_name} is calling the LLM")

        # Mark that LLM is active
        self.st_session_state.llm_is_thinking = True
        self.st_session_state.current_reasoning = "Thinking..."

        # Track LLM calls
        self.st_session_state.llm_calls.append({
            'agent': agent_name,
            'status': 'thinking',
            'started_at': datetime.now().isoformat()
        })

        print(f"🤔 [HOOK] LLM thinking for '{agent_name}'")

    async def on_llm_end(self, ctx, agent, response) -> None:
        """
        Called immediately AFTER LLM call returns.

        Use this to hide the thinking indicator and show the response.

        Args:
            ctx: Run context
            agent: The agent that made the LLM call
            response: The LLM response
        """
        if not self.st_session_state:
            return

        agent_name = getattr(agent, 'name', 'Unknown Agent')
        print(f"[LLM END] {agent_name} received LLM response")

        # LLM is done thinking
        self.st_session_state.llm_is_thinking = False
        self.st_session_state.current_reasoning = None

        # Update last LLM call status
        if self.st_session_state.llm_calls:
            self.st_session_state.llm_calls[-1]['status'] = 'completed'
            self.st_session_state.llm_calls[-1]['ended_at'] = datetime.now().isoformat()

        print(f"✅ [HOOK] LLM response received for '{agent_name}'")

    # ==================== TOOL LIFECYCLE ====================

    async def on_tool_start(self, ctx, agent, tool, input_data=None) -> None:
        """
        Called IMMEDIATELY BEFORE a tool is invoked.

        Use this to show which tool is currently executing.

        Args:
            ctx: Run context
            agent: The agent calling the tool
            tool: The tool being invoked
            input_data: Optional input data being passed to the tool
        """
        if not self.st_session_state:
            return

        tool_name = getattr(tool, 'name', 'unknown_tool')
        print(f"[TOOL START] {tool_name} is being called")

        # Add to executing tools list
        tool_entry = {
            'name': tool_name,
            'status': 'executing',
            'started_at': datetime.now().isoformat()
        }
        self.st_session_state.tools_executing.append(tool_entry)
        self.st_session_state.current_tool = tool_name

        # ==================== PHASE TRACKING ====================
        # Update current tool in the active phase
        agent_name = getattr(agent, 'name', 'Unknown Agent')
        phase_name = self._get_phase_for_agent(agent_name)
        if phase_name:
            set_phase_tool(self.st_session_state, phase_name, tool_name)

        print(f"🔧 [HOOK] Tool '{tool_name}' executing...")

    async def on_tool_end(self, ctx, agent, tool, output: Any) -> None:
        """
        Called after a tool completes execution.

        Useful for detecting when specific tools (like forecasting or allocation tools) finish.
        This is especially important for agents-as-tools pattern where sub-agents are called as tools.

        Args:
            ctx: Run context
            agent: The agent that called the tool
            tool: The tool that just completed
            output: The tool's output
        """
        if not self.st_session_state:
            return

        tool_name = getattr(tool, 'name', 'unknown')
        print(f"[TOOL END] {tool_name} completed")
        print(f"[TOOL OUTPUT] Type: {type(output).__name__}")
        print(f"[TOOL OUTPUT] Content preview: {str(output)[:200]}...")

        # Capture structured data from actual tools (not agent-as-tool wrappers)
        # The actual tools (run_demand_forecast, allocate_inventory, etc.) return structured dataclasses

        # Demand forecasting tool (actual tool inside demand agent)
        if tool_name == 'run_demand_forecast':
            self.st_session_state.demand_agent_completed = True
            # ForecastResult is a Pydantic model - convert to dict
            if hasattr(output, 'model_dump'):  # Pydantic v2
                self.st_session_state.demand_forecast_data = output.model_dump()
            elif hasattr(output, 'dict'):  # Pydantic v1
                self.st_session_state.demand_forecast_data = output.dict()
            elif hasattr(output, '__dict__'):  # Fallback to __dict__
                self.st_session_state.demand_forecast_data = vars(output)
            elif isinstance(output, dict):
                self.st_session_state.demand_forecast_data = output
            print(f"✅ [HOOK] run_demand_forecast completed - structured data captured")
            print(f"[HOOK DEBUG] Data keys: {list(self.st_session_state.demand_forecast_data.keys()) if self.st_session_state.demand_forecast_data else 'None'}")

        # Demand forecasting expert (agent-as-tool wrapper) - PARSE from text output
        elif tool_name == 'demand_forecasting_expert':
            self.st_session_state.demand_agent_completed = True
            print(f"✅ [HOOK] demand_forecasting_expert (agent-as-tool) completed")

            # Parse structured data from agent's formatted text response
            # The agent formats output in a consistent markdown structure
            if isinstance(output, str):
                import re

                # Debug: Show what we're parsing
                print(f"[HOOK DEBUG] Agent output length: {len(output)} chars")
                print(f"[HOOK DEBUG] Output preview: {output[:500]}...")

                forecast_data = {}

                # Parse Total Demand: "17,554 units" or "17554 units"
                total_match = re.search(r'Total Demand.*?(\d{1,3}(?:,\d{3})*|\d+)\s*units', output, re.IGNORECASE)
                if total_match:
                    forecast_data['total_demand'] = int(total_match.group(1).replace(',', ''))

                # Parse Weekly Average: "1,463 units/week"
                weekly_avg_match = re.search(r'Weekly Average.*?(\d{1,3}(?:,\d{3})*|\d+)\s*units', output, re.IGNORECASE)
                if weekly_avg_match:
                    forecast_data['weekly_average'] = float(weekly_avg_match.group(1).replace(',', ''))

                # Parse Confidence: "58%" or "58.5%"
                confidence_match = re.search(r'Forecast Confidence.*?(\d+(?:\.\d+)?)\s*%', output, re.IGNORECASE)
                if confidence_match:
                    forecast_data['confidence'] = float(confidence_match.group(1)) / 100.0

                # Parse Safety Stock: "42%" or "42.0%"
                safety_match = re.search(r'Safety Stock.*?(\d+(?:\.\d+)?)\s*%', output, re.IGNORECASE)
                if safety_match:
                    forecast_data['safety_stock_pct'] = float(safety_match.group(1)) / 100.0

                # Parse Model Used: "Prophet_Arima_Ensemble" or "prophet_arima_ensemble"
                model_match = re.search(r'Model Used:\s*([^\s\n,]+)', output, re.IGNORECASE)
                if model_match:
                    forecast_data['model_used'] = model_match.group(1)

                # Parse Weekly Breakdown - try multiple patterns
                weekly_breakdown = []

                # Pattern 1: "Week 1-4: 1436, 1433, 1431, 1430"
                week_pattern1 = r'Week\s+\d+-\d+:\s*([\d,\s]+)'
                for match in re.finditer(week_pattern1, output):
                    week_values = match.group(1).replace(',', '').split()
                    weekly_breakdown.extend([int(v) for v in week_values if v.isdigit()])

                # Pattern 2: Look for arrays like [1436, 1433, 1431, ...]
                if not weekly_breakdown:
                    array_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
                    array_match = re.search(array_pattern, output)
                    if array_match:
                        weekly_breakdown = [int(v.strip()) for v in array_match.group(1).split(',')]

                # Pattern 3: Find any list of 12 consecutive numbers (for 12-week forecast)
                if not weekly_breakdown:
                    # Look for patterns like: 3400, 3410, 3420, ... (12 numbers)
                    number_sequence = re.findall(r'\b(\d{3,5})\b', output)  # 3-5 digit numbers
                    if len(number_sequence) >= 12:
                        # Take first 12 that look like forecast values (not percentages, not years)
                        potential_forecast = [int(n) for n in number_sequence if 100 < int(n) < 100000]
                        if len(potential_forecast) >= 12:
                            weekly_breakdown = potential_forecast[:12]

                if weekly_breakdown:
                    forecast_data['forecast_by_week'] = weekly_breakdown
                    print(f"[HOOK DEBUG] Parsed {len(weekly_breakdown)} weekly values")

                # Store parsed data if we got the essential fields
                if 'total_demand' in forecast_data and 'confidence' in forecast_data:
                    self.st_session_state.demand_forecast_data = forecast_data
                    print(f"✅ [HOOK] Parsed structured data from agent text output")
                    print(f"[HOOK DEBUG] Parsed data keys: {list(forecast_data.keys())}")
                    print(f"[HOOK DEBUG] Confidence: {forecast_data.get('confidence', 'N/A')}")
                    print(f"[HOOK DEBUG] Forecast weeks: {len(forecast_data.get('forecast_by_week', []))}")

                    # Warn if data quality is poor
                    if forecast_data.get('confidence', 0) < 0.3:
                        print(f"⚠️ [HOOK WARNING] Very low forecast confidence ({forecast_data['confidence']:.0%}) - check data quality")
                else:
                    print(f"⚠️ [HOOK WARNING] Could not parse essential forecast data from agent output")
                    print(f"[HOOK DEBUG] Parsed keys so far: {list(forecast_data.keys())}")
            else:
                print(f"⚠️ [HOOK WARNING] demand_forecasting_expert output is not text: {type(output)}")

        # Inventory allocation tool (actual tool inside inventory agent)
        elif tool_name == 'allocate_inventory':
            self.st_session_state.inventory_agent_completed = True
            if hasattr(output, 'model_dump'):
                self.st_session_state.inventory_allocation_data = output.model_dump()
            elif hasattr(output, 'dict'):
                self.st_session_state.inventory_allocation_data = output.dict()
            elif hasattr(output, '__dict__'):
                self.st_session_state.inventory_allocation_data = vars(output)
            elif isinstance(output, dict):
                self.st_session_state.inventory_allocation_data = output
            print(f"✅ [HOOK] allocate_inventory completed - structured data captured")

        # Inventory allocation expert (agent-as-tool wrapper)
        elif tool_name == 'inventory_allocation_expert':
            self.st_session_state.inventory_agent_completed = True
            print(f"✅ [HOOK] inventory_allocation_expert (agent-as-tool) completed")
            if not hasattr(self.st_session_state, 'inventory_allocation_data') or not self.st_session_state.inventory_allocation_data:
                print(f"⚠️ [HOOK WARNING] inventory_allocation_expert completed but no data from inner tools")

        # Cluster stores tool
        elif tool_name == 'cluster_stores':
            if hasattr(output, '__dict__'):
                self.st_session_state.cluster_data = vars(output)
            elif hasattr(output, 'model_dump'):
                self.st_session_state.cluster_data = output.model_dump()
            elif isinstance(output, dict):
                self.st_session_state.cluster_data = output
            print(f"✅ [HOOK] cluster_stores completed - structured data captured")

        # Variance check tool
        elif tool_name == 'check_variance':
            self.st_session_state.variance_check_completed = True
            if hasattr(output, '__dict__'):
                self.st_session_state.variance_data = vars(output)
            elif hasattr(output, 'model_dump'):
                self.st_session_state.variance_data = output.model_dump()
            elif isinstance(output, dict):
                self.st_session_state.variance_data = output
            print(f"✅ [HOOK] check_variance completed - structured data captured")

        # Fallback: Also detect agent-as-tool completions by name pattern
        elif 'demand' in tool_name.lower() or 'forecast' in tool_name.lower():
            self.st_session_state.demand_agent_completed = True
            print(f"✅ [HOOK] Demand agent tool completed")

        elif 'inventory' in tool_name.lower() or 'allocation' in tool_name.lower():
            self.st_session_state.inventory_agent_completed = True
            print(f"✅ [HOOK] Inventory agent tool completed")

        # Update tool status in executing list
        for tool_entry in self.st_session_state.tools_executing:
            if tool_entry['name'] == tool_name and tool_entry['status'] == 'executing':
                tool_entry['status'] = 'completed'
                tool_entry['ended_at'] = datetime.now().isoformat()
                break

        # Add to completed tools list
        self.st_session_state.completed_tools.append(tool_name)
        self.st_session_state.current_tool = None

        print(f"✅ [HOOK] Tool '{tool_name}' finished")
