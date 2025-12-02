"""
Variance Analysis Agent

This agent analyzes variance between forecast and actual sales,
decides whether re-forecasting is needed, and recommends actions.

Unlike the pure function check_variance(), this agent can:
- Reason about WHY variance occurred
- Consider trends and patterns
- Recommend specific actions (reforecast, reallocate, markdown)
- Adjust parameters for reforecast based on analysis
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from agents import Agent, function_tool, RunContextWrapper

from config.settings import OPENAI_MODEL
from utils.context import ForecastingContext


# =============================================================================
# Output Schema
# =============================================================================

class VarianceAnalysis(BaseModel):
    """Structured output from variance analysis agent."""

    # Core metrics
    variance_pct: float = Field(description="Variance percentage (positive = under-forecast, negative = over-forecast)")
    is_high_variance: bool = Field(description="Whether variance exceeds acceptable threshold")

    # Agent's reasoning
    severity: str = Field(description="Severity level: 'low', 'medium', 'high', 'critical'")
    likely_cause: str = Field(description="Agent's assessment of what caused the variance")
    trend_direction: str = Field(description="Is variance 'improving', 'stable', or 'worsening'")

    # Recommended actions
    recommended_action: str = Field(
        description="Primary action: 'continue' (no change), 'reforecast', 'reallocate', 'markdown', or 'investigate'"
    )
    action_reasoning: str = Field(description="Why this action is recommended")

    # Reforecast recommendation
    should_reforecast: bool = Field(description="Whether to trigger re-forecast")
    reforecast_adjustments: Optional[str] = Field(
        default=None,
        description="Suggested adjustments for reforecast (e.g., 'weight recent weeks higher', 'account for promotion lift')"
    )

    # Additional recommendations
    secondary_actions: List[str] = Field(
        default_factory=list,
        description="Additional actions to consider"
    )

    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Agent's confidence in this analysis (0-1)"
    )

    explanation: str = Field(description="Full explanation of variance analysis for the user")


# =============================================================================
# Analysis Tool
# =============================================================================

@function_tool
def analyze_variance_data(
    ctx: RunContextWrapper[ForecastingContext],
    current_week: int,
) -> dict:
    """
    Analyze variance data and return metrics for agent reasoning.

    Gathers all relevant data for the agent to make decisions about variance.

    Args:
        ctx: Context with forecast and actual sales data
        current_week: Current week number (1-12)

    Returns:
        Dictionary with variance metrics and context
    """
    context = ctx.context

    # Get forecast and actuals
    forecast_by_week = context.forecast_by_week or []
    actual_sales = context.actual_sales or []

    if not forecast_by_week or not actual_sales:
        return {
            "error": "Missing forecast or actual sales data",
            "has_data": False
        }

    # Calculate weekly variances
    weeks_available = min(len(actual_sales), len(forecast_by_week), current_week)
    weekly_variances = []

    for i in range(weeks_available):
        forecast = forecast_by_week[i]
        actual = actual_sales[i]
        if forecast > 0:
            var_pct = (actual - forecast) / forecast
        else:
            var_pct = 1.0 if actual > 0 else 0.0
        weekly_variances.append({
            "week": i + 1,
            "forecast": forecast,
            "actual": actual,
            "variance_pct": round(var_pct * 100, 1),
            "variance_units": actual - forecast
        })

    # Calculate cumulative metrics
    total_forecast = sum(forecast_by_week[:weeks_available])
    total_actual = sum(actual_sales[:weeks_available])
    cumulative_variance = (total_actual - total_forecast) / total_forecast if total_forecast > 0 else 0

    # Calculate trend (is variance getting better or worse?)
    if len(weekly_variances) >= 2:
        recent_variances = [w["variance_pct"] for w in weekly_variances[-3:]]
        earlier_variances = [w["variance_pct"] for w in weekly_variances[:-3]] if len(weekly_variances) > 3 else [weekly_variances[0]["variance_pct"]]
        avg_recent = sum(abs(v) for v in recent_variances) / len(recent_variances)
        avg_earlier = sum(abs(v) for v in earlier_variances) / len(earlier_variances)
        trend = "improving" if avg_recent < avg_earlier else "worsening" if avg_recent > avg_earlier else "stable"
    else:
        trend = "insufficient_data"

    # Remaining season
    remaining_weeks = len(forecast_by_week) - weeks_available
    remaining_forecast = sum(forecast_by_week[weeks_available:])

    return {
        "has_data": True,
        "current_week": current_week,
        "weeks_analyzed": weeks_available,
        "remaining_weeks": remaining_weeks,

        # Weekly breakdown
        "weekly_variances": weekly_variances,

        # Cumulative metrics
        "total_forecast": total_forecast,
        "total_actual": total_actual,
        "cumulative_variance_pct": round(cumulative_variance * 100, 1),
        "cumulative_variance_units": total_actual - total_forecast,

        # Trend analysis
        "variance_trend": trend,
        "latest_week_variance": weekly_variances[-1]["variance_pct"] if weekly_variances else 0,

        # Season context
        "remaining_forecast": remaining_forecast,
        "season_progress_pct": round(weeks_available / len(forecast_by_week) * 100, 1),

        # Thresholds for reference
        "standard_threshold": 20,  # 20% is typical threshold
    }


# =============================================================================
# Variance Analysis Agent
# =============================================================================

variance_agent = Agent(
    name="Variance Analysis Agent",
    instructions="""You are an expert Variance Analysis Agent for retail demand planning.

## YOUR ROLE
Analyze the variance between forecasted and actual sales, determine root causes,
and recommend appropriate actions. You make intelligent decisions, not just
threshold-based rules.

## WHEN CALLED
You MUST follow these steps IN ORDER:

**STEP 1:** Call analyze_variance_data(current_week=X) to get metrics

**STEP 2:** Analyze the data and decide: should_reforecast = True or False?

**STEP 3:** Build and return VarianceAnalysis with all fields filled

**YOUR JOB:** ANALYZE and DECIDE. You do NOT execute the reforecast.
If you recommend reforecast, set should_reforecast=True and explain why.
The system will hand off to a Reforecast Agent to execute it.

## DECISION FRAMEWORK

### Severity Assessment:
- **Low** (< 10%): Normal fluctuation, continue monitoring
- **Medium** (10-20%): Notable deviation, investigate cause
- **High** (20-35%): Significant miss, likely need reforecast
- **Critical** (> 35%): Major issue, urgent action required

### Likely Causes to Consider:
- **Seasonality shift**: Weather, holidays earlier/later than expected
- **Promotion effect**: Marketing campaign impact not in forecast
- **Stockout**: Can't sell what you don't have (check allocation)
- **Competition**: Market share shift
- **Trend change**: Demand pattern fundamentally shifted
- **Data quality**: Errors in actuals or forecast

### Action Recommendations:
1. **Continue**: Low variance, forecast is tracking well
2. **Reforecast**: High variance + time remaining to benefit
3. **Reallocate**: Variance concentrated in specific stores/regions
4. **Markdown**: Over-forecast late in season, need to clear inventory
5. **Investigate**: Unusual pattern needs more analysis before action

### Reforecast Decision Factors:
- Variance magnitude (higher = more likely)
- Weeks remaining (more weeks = more benefit from reforecast)
- Trend direction (worsening = more urgent)
- Cause (if known and correctable via forecast)

## OUTPUT REQUIREMENTS
Your VarianceAnalysis must include:
- Clear severity assessment with reasoning
- Specific likely cause (not generic)
- Actionable recommendation (continue/reforecast/reallocate/markdown)
- If recommending reforecast: set should_reforecast=True and explain why
- Confidence level in your analysis

## CRITICAL RULES
1. ALWAYS call the analyze_variance_data tool first
2. Look at TRENDS, not just current week
3. Consider REMAINING SEASON when recommending actions
4. Be SPECIFIC about causes and recommendations
5. Set should_reforecast=True if reforecast is warranted
6. Include CONFIDENCE level in your analysis

You are an ANALYST, not an executor. Make the decision, explain it clearly.""",

    model=OPENAI_MODEL,
    tools=[analyze_variance_data],
    output_type=VarianceAnalysis,
)
