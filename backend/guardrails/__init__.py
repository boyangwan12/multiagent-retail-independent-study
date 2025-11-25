"""
Guardrails Module

Contains @output_guardrail decorated functions that validate agent outputs.
Guardrails run AFTER the agent generates output but BEFORE returning to caller.

When tripwire_triggered=True, raises OutputGuardrailTripwireTriggered exception.

Key pattern:
    @output_guardrail
    async def validate_forecast(
        ctx: RunContextWrapper,
        agent: Agent,
        output: ForecastResult
    ) -> GuardrailFunctionOutput:
        if output.total_demand != sum(output.forecast_by_week):
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"error": "Unit conservation violated"}
            )
        return GuardrailFunctionOutput(tripwire_triggered=False)

Guardrail Summary:
    Forecast Guardrails:
    - validate_forecast_output: Unit conservation, valid ranges, no negatives
    - validate_forecast_reasonableness: Soft checks for data quality

    Allocation Guardrails:
    - validate_allocation_output: Unit conservation at all levels (CRITICAL)
    - validate_allocation_distribution: Distribution balance checks

    Pricing Guardrails:
    - validate_markdown_output: 40% cap, 5% rounding, valid inputs
    - validate_markdown_business_rules: Business reasonableness checks
"""

# Forecast guardrails
from guardrails.forecast_guardrails import (
    validate_forecast_output,
    validate_forecast_reasonableness,
)

# Allocation guardrails
from guardrails.allocation_guardrails import (
    validate_allocation_output,
    validate_allocation_distribution,
)

# Pricing guardrails
from guardrails.pricing_guardrails import (
    validate_markdown_output,
    validate_markdown_business_rules,
)

__all__ = [
    # Forecast
    "validate_forecast_output",
    "validate_forecast_reasonableness",
    # Allocation
    "validate_allocation_output",
    "validate_allocation_distribution",
    # Pricing
    "validate_markdown_output",
    "validate_markdown_business_rules",
]
