"""
Pricing Schemas - Structured output for Pricing Agent

These Pydantic models define the output_type for the markdown pricing agent.
"""

from pydantic import BaseModel, Field


class MarkdownResult(BaseModel):
    """
    Structured output from Pricing Agent.

    This is used as output_type on the pricing agent, enabling:
    - Typed access via result.final_output
    - Output guardrail validation (40% cap, 5% rounding)
    - Direct data passing to UI for visualization

    Formula: Gap × Elasticity = Markdown
    - Gap = target_sell_through - current_sell_through
    - Markdown is rounded to nearest 5% and capped at 40%
    """

    recommended_markdown_pct: float = Field(
        ...,
        description="Recommended markdown percentage (0.0-0.40, rounded to 0.05)",
        ge=0.0,
        le=0.40,
    )
    current_sell_through: float = Field(
        ...,
        description="Current sell-through rate (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    target_sell_through: float = Field(
        ...,
        description="Target sell-through rate (typically 0.60)",
        ge=0.0,
        le=1.0,
    )
    gap: float = Field(
        ...,
        description="Gap between target and current sell-through",
    )
    elasticity_used: float = Field(
        ...,
        description="Price elasticity factor used in calculation (typically 2.0)",
        ge=0.0,
    )
    raw_markdown_pct: float = Field(
        default=0.0,
        description="Raw markdown before rounding (gap × elasticity)",
    )
    week_number: int = Field(
        default=6,
        description="Week number when markdown was calculated",
        ge=1,
    )
    explanation: str = Field(
        ...,
        description="Agent's reasoning about the markdown recommendation",
    )

    @property
    def markdown_needed(self) -> bool:
        """Returns True if markdown is recommended (> 0%)."""
        return self.recommended_markdown_pct > 0.0

    @property
    def is_max_markdown(self) -> bool:
        """Returns True if markdown hit the 40% cap."""
        return self.recommended_markdown_pct >= 0.40
