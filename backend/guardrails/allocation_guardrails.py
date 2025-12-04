"""
Allocation Guardrails - Validate AllocationResult Output

These guardrails validate the inventory agent's output BEFORE returning to the workflow.
The most critical validation is UNIT CONSERVATION - ensuring no units are lost or gained.

SDK Pattern:
    @output_guardrail
    async def validate_allocation(ctx, agent, output) -> GuardrailFunctionOutput:
        if not output.validate_unit_conservation():
            return GuardrailFunctionOutput(tripwire_triggered=True, output_info={...})
        return GuardrailFunctionOutput(tripwire_triggered=False)

Usage:
    inventory_agent = Agent(
        ...
        output_guardrails=[validate_allocation_output]
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

from schemas.allocation_schemas import AllocationResult

logger = logging.getLogger("allocation_guardrails")


@output_guardrail
async def validate_allocation_output(
    ctx: RunContextWrapper,
    agent: Agent,
    output: AllocationResult,
) -> GuardrailFunctionOutput:
    """
    Validate allocation output before returning to workflow.

    NOW WORKS because agent has output_type=AllocationResult!

    Validation Rules:
    1. Unit conservation: DC + stores = manufacturing (CRITICAL)
    2. Cluster allocations must sum to initial store allocation
    3. Store allocations must sum to initial store allocation
    4. All quantities must be non-negative
    5. DC holdback percentage must be valid (0-100%)
    6. Must have at least one cluster and one store

    Args:
        ctx: Run context wrapper
        agent: The agent being validated
        output: AllocationResult to validate

    Returns:
        GuardrailFunctionOutput with tripwire_triggered=True if validation fails
    """
    errors: List[str] = []
    warnings: List[str] = []

    logger.info("Validating allocation output...")

    # Rule 1: Unit conservation at manufacturing level (CRITICAL)
    manufacturing_sum = output.dc_holdback + output.initial_store_allocation
    if manufacturing_sum != output.manufacturing_qty:
        errors.append(
            f"UNIT CONSERVATION FAILED at manufacturing level: "
            f"DC ({output.dc_holdback}) + Stores ({output.initial_store_allocation}) = "
            f"{manufacturing_sum} != Manufacturing ({output.manufacturing_qty})"
        )

    # Rule 2: Cluster allocations must sum correctly
    if output.cluster_allocations:
        cluster_sum = sum(c.allocation_units for c in output.cluster_allocations)
        if cluster_sum != output.initial_store_allocation:
            errors.append(
                f"UNIT CONSERVATION FAILED at cluster level: "
                f"sum(clusters) = {cluster_sum} != initial_store_allocation ({output.initial_store_allocation})"
            )

    # Rule 3: Store allocations must sum correctly
    if output.store_allocations:
        store_sum = sum(s.allocation_units for s in output.store_allocations)
        if store_sum != output.initial_store_allocation:
            errors.append(
                f"UNIT CONSERVATION FAILED at store level: "
                f"sum(stores) = {store_sum} != initial_store_allocation ({output.initial_store_allocation})"
            )

    # Rule 4: All quantities must be non-negative
    if output.manufacturing_qty < 0:
        errors.append(f"Negative manufacturing qty: {output.manufacturing_qty}")
    if output.dc_holdback < 0:
        errors.append(f"Negative DC holdback: {output.dc_holdback}")
    if output.initial_store_allocation < 0:
        errors.append(f"Negative initial store allocation: {output.initial_store_allocation}")

    # Check cluster allocations for negatives
    for cluster in output.cluster_allocations:
        if cluster.allocation_units < 0:
            errors.append(
                f"Negative allocation for cluster {cluster.cluster_name}: {cluster.allocation_units}"
            )

    # Check store allocations for negatives
    for store in output.store_allocations:
        if store.allocation_units < 0:
            errors.append(
                f"Negative allocation for store {store.store_id}: {store.allocation_units}"
            )

    # Rule 5: DC holdback percentage must be valid
    if not (0.0 <= output.dc_holdback_percentage <= 1.0):
        errors.append(
            f"Invalid DC holdback percentage: {output.dc_holdback_percentage}. "
            f"Must be between 0.0 and 1.0"
        )

    # Verify DC holdback percentage matches actual values
    if output.manufacturing_qty > 0:
        actual_dc_pct = output.dc_holdback / output.manufacturing_qty
        if abs(actual_dc_pct - output.dc_holdback_percentage) > 0.01:
            warnings.append(
                f"DC holdback percentage ({output.dc_holdback_percentage:.2%}) doesn't match "
                f"actual ({actual_dc_pct:.2%})"
            )

    # Rule 6: Must have allocations
    if not output.cluster_allocations:
        errors.append("No cluster allocations provided")
    if not output.store_allocations:
        errors.append("No store allocations provided")

    # Rule 7: Replenishment strategy must be valid
    valid_strategies = {"none", "weekly", "bi-weekly"}
    if output.replenishment_strategy not in valid_strategies:
        warnings.append(
            f"Unknown replenishment strategy: {output.replenishment_strategy}. "
            f"Expected one of: {valid_strategies}"
        )

    # Log results
    if errors:
        logger.error(f"Allocation validation FAILED: {errors}")
    if warnings:
        logger.warning(f"Allocation validation warnings: {warnings}")

    if errors:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={
                "validation_errors": errors,
                "validation_warnings": warnings,
                "allocation_summary": {
                    "manufacturing_qty": output.manufacturing_qty,
                    "dc_holdback": output.dc_holdback,
                    "initial_store_allocation": output.initial_store_allocation,
                    "cluster_count": len(output.cluster_allocations),
                    "store_count": len(output.store_allocations),
                },
            },
        )

    logger.info("Allocation validation PASSED")
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={
            "validation_warnings": warnings if warnings else None,
            "unit_conservation": "VERIFIED",
        },
    )


@output_guardrail
async def validate_allocation_distribution(
    ctx: RunContextWrapper,
    agent: Agent,
    output: AllocationResult,
) -> GuardrailFunctionOutput:
    """
    Validate allocation distribution reasonableness (soft checks).

    These are warning-level checks that don't block the output but
    flag potential distribution issues.

    Checks:
    1. No cluster should have 0 allocation (unless 0 stores)
    2. No store should have 0 allocation (minimum inventory check)
    3. Allocation factors should be reasonable (0.5-2.0 typical)
    4. Cluster percentages should be reasonable

    Args:
        ctx: Run context wrapper
        agent: The agent being validated
        output: AllocationResult to validate

    Returns:
        GuardrailFunctionOutput (tripwire_triggered=False, just warnings)
    """
    warnings: List[str] = []

    # Check 1: Zero cluster allocations
    zero_clusters = [
        c.cluster_name for c in output.cluster_allocations
        if c.allocation_units == 0 and c.store_count > 0
    ]
    if zero_clusters:
        warnings.append(
            f"Clusters with 0 allocation but stores exist: {zero_clusters}"
        )

    # Check 2: Zero store allocations
    zero_stores = [
        s.store_id for s in output.store_allocations
        if s.allocation_units == 0
    ]
    if zero_stores:
        warnings.append(
            f"Stores with 0 allocation: {len(zero_stores)} stores "
            f"(first 5: {zero_stores[:5]})"
        )

    # Check 3: Allocation factors
    extreme_factors = []
    for store in output.store_allocations:
        if store.allocation_factor < 0.3 or store.allocation_factor > 3.0:
            extreme_factors.append(
                f"{store.store_id}: {store.allocation_factor:.2f}"
            )
    if extreme_factors:
        warnings.append(
            f"Extreme allocation factors (outside 0.3-3.0): {len(extreme_factors)} stores"
        )

    # Check 4: Cluster percentage distribution
    if output.cluster_allocations:
        total_pct = sum(c.allocation_percentage for c in output.cluster_allocations)
        if abs(total_pct - 1.0) > 0.01:
            warnings.append(
                f"Cluster percentages don't sum to 100%: {total_pct:.1%}"
            )

        # Check for extreme imbalance
        max_pct = max(c.allocation_percentage for c in output.cluster_allocations)
        if max_pct > 0.70:
            warnings.append(
                f"One cluster has {max_pct:.0%} of allocation - highly imbalanced"
            )

    if warnings:
        logger.warning(f"Allocation distribution warnings: {warnings}")

    # This guardrail never trips - it just logs warnings
    return GuardrailFunctionOutput(
        tripwire_triggered=False,
        output_info={"distribution_warnings": warnings} if warnings else None,
    )
