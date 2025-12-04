"""
Workflows Module

Contains workflow orchestration that controls agent execution.
The workflow layer uses Python code (if/while) to decide WHEN agents run,
while agents use LLM reasoning to decide HOW they respond.

Key pattern:
    # Workflow controls the loop
    while reforecast_count < max_reforecasts:
        # Demand agent generates forecast
        result = await Runner.run(demand_agent, input, context=context)
        forecast = result.final_output

        # Variance agent analyzes and decides whether to reforecast
        variance_result = await Runner.run(variance_agent, ...)
        analysis = variance_result.final_output

        if not analysis.should_reforecast:
            break
        reforecast_count += 1

Workflow Summary:
    - forecast_workflow: Demand forecast with agentic variance analysis
    - allocation_workflow: Store clustering + hierarchical inventory allocation
    - pricing_workflow: Markdown checkpoint logic
    - season_workflow: Full season orchestration (all 3 agents)
"""

# Forecast workflow
from workflows.forecast_workflow import (
    run_forecast,
    run_forecast_with_variance_loop,
    check_forecast_variance,
)

# Allocation workflow
from workflows.allocation_workflow import (
    run_allocation,
    run_clustering_only,
)

# Pricing workflow
from workflows.pricing_workflow import (
    run_markdown_check,
    should_run_markdown_check,
    run_markdown_if_needed,
)

# Season workflow (main entry point)
from workflows.season_workflow import (
    run_full_season,
    run_preseason_planning,
    run_inseason_update,
)

__all__ = [
    # Forecast
    "run_forecast",
    "run_forecast_with_variance_loop",
    "check_forecast_variance",
    # Allocation
    "run_allocation",
    "run_clustering_only",
    # Pricing
    "run_markdown_check",
    "should_run_markdown_check",
    "run_markdown_if_needed",
    # Season (main)
    "run_full_season",
    "run_preseason_planning",
    "run_inseason_update",
]
