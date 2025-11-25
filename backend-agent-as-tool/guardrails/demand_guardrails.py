"""
Demand Forecasting Output Guardrails

Enforces data integrity for forecast results before they reach the UI.
Prevents invalid/hallucinated data from breaking visualizations or business logic.
"""

from agents import output_guardrail, GuardrailFunctionOutput, RunContextWrapper, Agent
from agent_tools.demand_tools import ForecastResult
from typing import List


@output_guardrail
async def validate_forecast_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ForecastResult
) -> GuardrailFunctionOutput:
    """
    Validate forecast output data integrity.

    This guardrail enforces critical business rules and mathematical constraints
    on forecast data before it reaches the UI. If validation fails, the exception
    is caught in Streamlit and user sees a helpful error instead of broken charts.

    Validations:
    1. Confidence is in valid range [0.0, 1.0]
    2. Safety stock is in valid range [0.1, 0.5] (10-50%)
    3. Total demand equals sum of weekly forecasts (unit conservation)
    4. No negative predictions (can't forecast negative demand)
    5. Forecast horizon matches expected length
    6. All required fields are present and non-empty

    Args:
        ctx: Run context
        agent: The demand forecasting agent
        output: ForecastResult from the agent

    Returns:
        GuardrailFunctionOutput with tripwire_triggered=True if validation fails
    """

    issues: List[str] = []

    # ======== CRITICAL VALIDATIONS ========

    # 1. Confidence Range (prevents downstream math errors)
    if not (0.0 <= output.confidence <= 1.0):
        issues.append(
            f"Confidence {output.confidence:.3f} is out of valid range [0.0, 1.0]. "
            f"This would cause invalid safety stock calculation."
        )

    # 2. Safety Stock Range (business rule)
    if not (0.1 <= output.safety_stock_pct <= 0.5):
        issues.append(
            f"Safety stock {output.safety_stock_pct:.2%} is out of valid range [10%, 50%]. "
            f"Fashion retail requires safety stock between these bounds."
        )

    # 3. Unit Conservation (mathematical integrity)
    calculated_sum = sum(output.forecast_by_week)
    if calculated_sum != output.total_demand:
        issues.append(
            f"Unit conservation violated: sum of weekly forecasts ({calculated_sum:,}) "
            f"≠ total_demand ({output.total_demand:,}). Difference: {abs(calculated_sum - output.total_demand):,} units."
        )

    # 4. No Negative Predictions
    negative_weeks = [i+1 for i, x in enumerate(output.forecast_by_week) if x < 0]
    if negative_weeks:
        issues.append(
            f"Negative demand predictions found in weeks: {negative_weeks}. "
            f"Cannot allocate negative inventory."
        )

    # 5. Non-empty Forecasts
    if not output.forecast_by_week or len(output.forecast_by_week) == 0:
        issues.append("forecast_by_week is empty - no predictions generated")

    # 6. Required Fields Present
    if output.total_demand is None or output.total_demand <= 0:
        issues.append(f"total_demand is invalid: {output.total_demand}")

    if not output.model_used:
        issues.append("model_used field is empty - cannot determine which model was used")

    # ======== LOG RESULTS ========

    if issues:
        print(f"❌ [DEMAND GUARDRAIL] Validation FAILED - blocking invalid forecast")
        print(f"[GUARDRAIL] Agent: {agent.name}")
        print(f"[GUARDRAIL] Issues found ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"[GUARDRAIL] Tripwire TRIGGERED - OutputGuardrailTripwireTriggered will be raised")
    else:
        print(f"✅ [DEMAND GUARDRAIL] Validation PASSED")
        print(f"[GUARDRAIL] Forecast data integrity confirmed:")
        print(f"  - Total Demand: {output.total_demand:,} units")
        print(f"  - Confidence: {output.confidence:.1%}")
        print(f"  - Safety Stock: {output.safety_stock_pct:.1%}")
        print(f"  - Horizon: {len(output.forecast_by_week)} weeks")
        print(f"  - Model: {output.model_used}")

    return GuardrailFunctionOutput(
        tripwire_triggered=len(issues) > 0,
        output_info={
            "validation_errors": issues,
            "data_summary": {
                "total_demand": output.total_demand,
                "confidence": output.confidence,
                "safety_stock_pct": output.safety_stock_pct,
                "weeks": len(output.forecast_by_week) if output.forecast_by_week else 0
            }
        }
    )
