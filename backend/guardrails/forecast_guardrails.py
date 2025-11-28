"""
Forecast Guardrails - Validate ForecastResult Output

These guardrails validate the demand agent's output BEFORE returning to the workflow.
They ensure forecast integrity and catch common issues.

SDK Pattern:
    @output_guardrail
    async def validate_forecast(ctx, agent, output) -> GuardrailFunctionOutput:
        if invalid:
            return GuardrailFunctionOutput(tripwire_triggered=True, output_info={...})
        return GuardrailFunctionOutput(tripwire_triggered=False)

Usage:
    demand_agent = Agent(
        ...
        output_guardrails=[validate_forecast_output]
    )
"""

import logging
from typing import List

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    output_guardrail,
)

from schemas.forecast_schemas import ForecastResult

logger = logging.getLogger("forecast_guardrails")


@output_guardrail
async def validate_forecast_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ForecastResult,
) -> GuardrailFunctionOutput:
    """
    Validate forecast output before returning to workflow.

    NOW WORKS because agent has output_type=ForecastResult!

    Validation Rules:
    1. Total demand must equal sum of weekly forecasts (unit conservation)
    2. Safety stock must be in valid range (10-50%)
    3. No negative forecasts
    4. Confidence must be valid (0.0-1.0)
    5. Forecast must have at least one week
    6. Model used must be a known model

    Args:
        ctx: Run context wrapper
        agent: The agent being validated
        output: ForecastResult to validate

    Returns:
        GuardrailFunctionOutput with tripwire_triggered=True if validation fails
    """
    errors: List[str] = []
    warnings: List[str] = []

    logger.info("Validating forecast output...")

    # Rule 1: Unit conservation - total must equal sum of weeks
    if output.forecast_by_week:
        expected_total = sum(output.forecast_by_week)
        if output.total_demand != expected_total:
            errors.append(
                f"Unit conservation violated: total_demand ({output.total_demand}) "
                f"!= sum(forecast_by_week) ({expected_total})"
            )

    # Rule 2: Safety stock must be in valid range
    if not (0.10 <= output.safety_stock_pct <= 0.50):
        errors.append(
            f"Safety stock {output.safety_stock_pct:.0%} out of valid range [10%, 50%]"
        )

    # Rule 3: No negative forecasts
    if output.forecast_by_week:
        negative_weeks = [
            i + 1 for i, f in enumerate(output.forecast_by_week) if f < 0
        ]
        if negative_weeks:
            errors.append(
                f"Negative forecast values detected in weeks: {negative_weeks}"
            )

    # Rule 4: Confidence must be valid
    if not (0.0 <= output.confidence <= 1.0):
        errors.append(
            f"Invalid confidence: {output.confidence}. Must be between 0.0 and 1.0"
        )

    # Rule 5: Must have at least one week of forecast
    if not output.forecast_by_week or len(output.forecast_by_week) == 0:
        errors.append("Forecast must have at least one week of predictions")

    # Rule 6: Model must be known
    valid_models = {"prophet_arima_ensemble", "prophet", "arima", "none"}
    if output.model_used not in valid_models:
        warnings.append(
            f"Unknown model: {output.model_used}. Expected one of: {valid_models}"
        )

    # Rule 7: Bounds validation (if provided)
    if output.lower_bound and output.upper_bound:
        if len(output.lower_bound) != len(output.forecast_by_week):
            warnings.append(
                f"Lower bound length ({len(output.lower_bound)}) doesn't match "
                f"forecast length ({len(output.forecast_by_week)})"
            )
        if len(output.upper_bound) != len(output.forecast_by_week):
            warnings.append(
                f"Upper bound length ({len(output.upper_bound)}) doesn't match "
                f"forecast length ({len(output.forecast_by_week)})"
            )

        # Check bounds ordering
        for i, (low, pred, high) in enumerate(
            zip(output.lower_bound, output.forecast_by_week, output.upper_bound)
        ):
            if not (low <= pred <= high):
                warnings.append(
                    f"Week {i+1}: bounds ordering violated "
                    f"(lower={low}, pred={pred}, upper={high})"
                )

    # Log results
    if errors:
        logger.error(f"Forecast validation FAILED: {errors}")
    if warnings:
        logger.warning(f"Forecast validation warnings: {warnings}")

    if errors:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "validation_errors": errors,
                "validation_warnings": warnings,
                "forecast_summary": {
                    "total_demand": output.total_demand,
                    "weeks": len(output.forecast_by_week) if output.forecast_by_week else 0,
                    "safety_stock": output.safety_stock_pct,
                    "confidence": output.confidence,
                },
            },
        )

    logger.info("Forecast validation PASSED")
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={
            "validation_warnings": warnings if warnings else None,
        },
    )


@output_guardrail
async def validate_forecast_reasonableness(
    ctx: RunContextWrapper,
    agent: Agent,
    output: ForecastResult,
) -> GuardrailFunctionOutput:
    """
    Validate forecast reasonableness (soft checks).

    These are warning-level checks that don't block the output but
    flag potential issues for review.

    Checks:
    1. Total demand should be reasonable (not zero, not extremely high)
    2. Weekly variance should not be extreme
    3. Confidence should match data quality expectations

    Args:
        ctx: Run context wrapper
        agent: The agent being validated
        output: ForecastResult to validate

    Returns:
        GuardrailFunctionOutput (tripwire_triggered=False, just warnings)
    """
    warnings: List[str] = []

    # Check 1: Total demand reasonableness
    if output.total_demand == 0:
        warnings.append("Total demand is zero - is this expected?")
    elif output.total_demand > 1_000_000:
        warnings.append(
            f"Very high total demand ({output.total_demand:,}) - verify data quality"
        )

    # Check 2: Weekly variance
    if output.forecast_by_week and len(output.forecast_by_week) > 1:
        avg_weekly = output.total_demand / len(output.forecast_by_week)
        max_weekly = max(output.forecast_by_week)
        min_weekly = min(output.forecast_by_week)

        if avg_weekly > 0:
            max_deviation = (max_weekly - avg_weekly) / avg_weekly
            min_deviation = (avg_weekly - min_weekly) / avg_weekly

            if max_deviation > 1.0:  # More than 100% above average
                warnings.append(
                    f"High weekly variance: max ({max_weekly}) is {max_deviation:.0%} above average"
                )
            if min_deviation > 0.8:  # More than 80% below average
                warnings.append(
                    f"High weekly variance: min ({min_weekly}) is {min_deviation:.0%} below average"
                )

    # Note: Safety stock is now user-controlled via WorkflowParams
    # No longer validated against confidence score

    if warnings:
        logger.warning(f"Forecast reasonableness warnings: {warnings}")

    # This guardrail never trips - it just logs warnings
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={"reasonableness_warnings": warnings} if warnings else None,
    )
