"""
Pricing Guardrails - Validate MarkdownResult Output

These guardrails validate the pricing agent's output BEFORE returning to the workflow.
They ensure markdown recommendations follow business rules (40% cap, 5% rounding).

SDK Pattern:
    @output_guardrail
    async def validate_markdown(ctx, agent, output) -> GuardrailFunctionOutput:
        if output.recommended_markdown_pct > 0.40:
            return GuardrailFunctionOutput(tripwire_triggered=True, output_info={...})
        return GuardrailFunctionOutput(tripwire_triggered=False)

Usage:
    pricing_agent = Agent(
        ...
        output_guardrails=[validate_markdown_output]
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

from schemas.pricing_schemas import MarkdownResult

logger = logging.getLogger("pricing_guardrails")


def is_rounded_to_5_percent(value: float, tolerance: float = 0.001) -> bool:
    """Check if value is rounded to nearest 5% (0.05)."""
    # Multiply by 20 and check if it's close to an integer
    scaled = value * 20
    return abs(scaled - round(scaled)) < tolerance


@output_guardrail
async def validate_markdown_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: MarkdownResult,
) -> GuardrailFunctionOutput:
    """
    Validate markdown output before returning to workflow.

    NOW WORKS because agent has output_type=MarkdownResult!

    Validation Rules:
    1. Markdown must not exceed 40% cap
    2. Markdown must be rounded to nearest 5%
    3. Markdown must be non-negative
    4. Sell-through rates must be valid (0-100%)
    5. Gap calculation must be correct
    6. Elasticity must be positive

    Args:
        ctx: Run context wrapper
        agent: The agent being validated
        output: MarkdownResult to validate

    Returns:
        GuardrailFunctionOutput with tripwire_triggered=True if validation fails
    """
    errors: List[str] = []
    warnings: List[str] = []

    logger.info("Validating markdown output...")

    # Rule 1: Markdown must not exceed 40% cap
    if output.recommended_markdown_pct > 0.40:
        errors.append(
            f"Markdown {output.recommended_markdown_pct:.0%} exceeds 40% cap"
        )

    # Rule 2: Markdown must be non-negative
    if output.recommended_markdown_pct < 0:
        errors.append(
            f"Negative markdown: {output.recommended_markdown_pct:.0%}"
        )

    # Rule 3: Markdown must be rounded to nearest 5%
    if output.recommended_markdown_pct > 0:
        if not is_rounded_to_5_percent(output.recommended_markdown_pct):
            warnings.append(
                f"Markdown {output.recommended_markdown_pct:.2%} not rounded to nearest 5%"
            )

    # Rule 4: Sell-through rates must be valid
    if not (0.0 <= output.current_sell_through <= 1.0):
        errors.append(
            f"Invalid current sell-through: {output.current_sell_through}. "
            f"Must be between 0.0 and 1.0"
        )

    if not (0.0 <= output.target_sell_through <= 1.0):
        errors.append(
            f"Invalid target sell-through: {output.target_sell_through}. "
            f"Must be between 0.0 and 1.0"
        )

    # Rule 5: Gap calculation must be correct
    expected_gap = output.target_sell_through - output.current_sell_through
    if abs(output.gap - expected_gap) > 0.001:
        errors.append(
            f"Gap calculation incorrect: reported {output.gap:.2%}, "
            f"expected {expected_gap:.2%}"
        )

    # Rule 6: Elasticity must be positive
    if output.elasticity_used < 0:
        errors.append(
            f"Negative elasticity: {output.elasticity_used}"
        )

    # Rule 7: Raw markdown should match formula (Gap × Elasticity)
    if output.gap > 0:
        expected_raw = output.gap * output.elasticity_used
        if abs(output.raw_markdown_pct - expected_raw) > 0.01:
            warnings.append(
                f"Raw markdown ({output.raw_markdown_pct:.2%}) doesn't match "
                f"Gap × Elasticity ({expected_raw:.2%})"
            )

    # Rule 8: If gap <= 0, markdown should be 0
    if output.gap <= 0 and output.recommended_markdown_pct > 0:
        errors.append(
            f"Markdown recommended ({output.recommended_markdown_pct:.0%}) "
            f"when gap is non-positive ({output.gap:.2%})"
        )

    # Log results
    if errors:
        logger.error(f"Markdown validation FAILED: {errors}")
    if warnings:
        logger.warning(f"Markdown validation warnings: {warnings}")

    if errors:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "validation_errors": errors,
                "validation_warnings": warnings,
                "markdown_summary": {
                    "recommended": output.recommended_markdown_pct,
                    "current_sell_through": output.current_sell_through,
                    "target_sell_through": output.target_sell_through,
                    "gap": output.gap,
                    "elasticity": output.elasticity_used,
                },
            },
        )

    logger.info("Markdown validation PASSED")
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={
            "validation_warnings": warnings if warnings else None,
        },
    )


@output_guardrail
async def validate_markdown_business_rules(
    ctx: RunContextWrapper,
    agent: Agent,
    output: MarkdownResult,
) -> GuardrailFunctionOutput:
    """
    Validate markdown against business rules (soft checks).

    These are warning-level checks that don't block the output but
    flag potential business concerns.

    Checks:
    1. Early season markdowns should be conservative
    2. Very high markdowns should be flagged
    3. Markdown when already above target is unusual
    4. Check elasticity is within typical range

    Args:
        ctx: Run context wrapper
        agent: The agent being validated
        output: MarkdownResult to validate

    Returns:
        GuardrailFunctionOutput (tripwire_triggered=False, just warnings)
    """
    warnings: List[str] = []

    # Check 1: Early season markdowns
    if output.week_number <= 4 and output.recommended_markdown_pct > 0.15:
        warnings.append(
            f"High markdown ({output.recommended_markdown_pct:.0%}) early in season "
            f"(week {output.week_number}). Consider waiting for more sales data."
        )

    # Check 2: Very high markdowns
    if output.recommended_markdown_pct >= 0.35:
        warnings.append(
            f"Very high markdown ({output.recommended_markdown_pct:.0%}) recommended. "
            f"This will significantly impact margins. Verify sell-through data is accurate."
        )

    # Check 3: Markdown at max cap
    if output.is_max_markdown:
        warnings.append(
            f"Markdown hit 40% cap. Raw calculation was {output.raw_markdown_pct:.0%}. "
            f"Even maximum markdown may not achieve target sell-through."
        )

    # Check 4: Elasticity range
    if output.elasticity_used < 1.5:
        warnings.append(
            f"Low elasticity ({output.elasticity_used}) - markdown may have limited impact"
        )
    elif output.elasticity_used > 3.0:
        warnings.append(
            f"High elasticity ({output.elasticity_used}) - markdown impact may be overestimated"
        )

    # Check 5: Very low sell-through
    if output.current_sell_through < 0.30 and output.week_number >= 6:
        warnings.append(
            f"Very low sell-through ({output.current_sell_through:.0%}) at week {output.week_number}. "
            f"Even with markdown, inventory may not clear by season end."
        )

    if warnings:
        logger.warning(f"Markdown business rule warnings: {warnings}")

    # This guardrail never trips - it just logs warnings
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={"business_warnings": warnings} if warnings else None,
    )
