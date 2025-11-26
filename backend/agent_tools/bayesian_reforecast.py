"""
Bayesian Reforecasting Module

Implements intelligent reforecasting using Bayesian updating:
- Original forecast serves as the prior
- Actual sales data provides the likelihood
- Posterior forecast has properly calibrated uncertainty

This approach is more statistically rigorous than simple adjustment factors,
providing:
1. Uncertainty quantification that grows for distant weeks
2. Statistical significance testing before applying large adjustments
3. Intelligent, explainable reasoning for forecast changes
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger("bayesian_reforecast")


@dataclass
class BayesianReforecastResult:
    """Result of Bayesian reforecasting with rich metadata."""

    forecast_by_week: List[int]
    lower_bound: List[int]
    upper_bound: List[int]
    total_demand: int
    confidence: float
    explanation: str

    # Detailed statistics for transparency
    observed_bias: float  # Average deviation from forecast
    bias_significance: float  # t-statistic for bias
    adjustment_applied: float  # Actual multiplier used (after decay)
    uncertainty_growth_pct: float  # How much bounds widened


class BayesianReforecaster:
    """
    Bayesian approach to reforecasting that:
    1. Treats original forecast as prior belief
    2. Updates beliefs based on actual sales (likelihood)
    3. Computes posterior forecast with calibrated uncertainty
    4. Generates intelligent, context-aware explanations
    """

    # Constants for statistical calculations
    Z_95 = 1.96  # 95% confidence interval z-score
    MIN_CONFIDENCE = 0.50  # Floor for confidence score
    BIAS_DECAY_RATE = 0.1  # Exponential decay rate for bias adjustment
    UNCERTAINTY_GROWTH_RATE = 0.05  # 5% uncertainty growth per week

    def __init__(
        self,
        prior_forecast: List[int],
        prior_confidence: float = 0.80,
        prior_bounds: Optional[Tuple[List[int], List[int]]] = None,
    ):
        """
        Initialize with original forecast as prior.

        Args:
            prior_forecast: Original forecast by week
            prior_confidence: Original confidence score (0-1)
            prior_bounds: Optional (lower, upper) bounds from original forecast
        """
        self.prior_mean = np.array(prior_forecast, dtype=float)
        self.prior_confidence = prior_confidence

        # Estimate prior standard deviation from bounds or confidence
        if prior_bounds:
            lower, upper = prior_bounds
            # Assume bounds represent ~95% CI
            self.prior_std = (np.array(upper) - np.array(lower)) / (2 * self.Z_95)
        else:
            # Estimate std from confidence: higher confidence = lower std
            # At 80% confidence, assume ~15% relative std
            relative_std = 0.15 * (1.0 + (1.0 - prior_confidence))
            self.prior_std = self.prior_mean * relative_std

        # Ensure non-zero std
        self.prior_std = np.maximum(self.prior_std, 1.0)

        logger.info(
            f"BayesianReforecaster initialized: {len(prior_forecast)} weeks, "
            f"confidence={prior_confidence:.2f}"
        )

    def update_with_actuals(
        self,
        actual_sales: List[int],
    ) -> BayesianReforecastResult:
        """
        Perform Bayesian update with observed actual sales.

        The key insight: we don't just scale by performance ratio.
        We compute a statistically principled posterior that:
        - Applies larger adjustments when we have more data
        - Decays the adjustment for far-future weeks (less certain)
        - Widens uncertainty bounds appropriately

        Args:
            actual_sales: Actual sales for weeks elapsed

        Returns:
            BayesianReforecastResult with updated forecast and rich explanation
        """
        actuals = np.array(actual_sales, dtype=float)
        weeks_elapsed = len(actuals)
        total_weeks = len(self.prior_mean)
        weeks_remaining = total_weeks - weeks_elapsed

        logger.info(f"Bayesian update: {weeks_elapsed} weeks actual, {weeks_remaining} remaining")

        if weeks_elapsed == 0:
            # No actuals yet - return prior
            return self._create_result_from_prior()

        if weeks_remaining == 0:
            # Season complete - return actuals only
            return self._create_result_actuals_only(actuals)

        # ================================================================
        # STEP 1: Analyze observed performance vs prior
        # ================================================================
        prior_slice = self.prior_mean[:weeks_elapsed]

        # Calculate residuals (actual - forecast)
        residuals = actuals - prior_slice

        # Observed bias (systematic over/under performance)
        observed_bias = np.mean(residuals)

        # Observation noise (week-to-week variance)
        if weeks_elapsed > 1:
            obs_std = np.std(residuals, ddof=1)  # Sample std
        else:
            # Single observation - estimate from prior
            obs_std = self.prior_std[0] * 0.5

        # Ensure non-zero
        obs_std = max(obs_std, 1.0)

        # ================================================================
        # STEP 2: Statistical significance of bias
        # ================================================================
        # t-statistic: how many standard errors is the bias from zero?
        standard_error = obs_std / np.sqrt(weeks_elapsed)
        bias_significance = abs(observed_bias) / standard_error if standard_error > 0 else 0

        # Determine adjustment strength based on significance
        # - t < 1.0: weak evidence, apply 30% of bias
        # - t 1.0-2.0: moderate evidence, apply 60% of bias
        # - t > 2.0: strong evidence, apply 90% of bias
        if bias_significance < 1.0:
            significance_factor = 0.30
            significance_level = "weak"
        elif bias_significance < 2.0:
            significance_factor = 0.60
            significance_level = "moderate"
        else:
            significance_factor = 0.90
            significance_level = "strong"

        # ================================================================
        # STEP 3: Calculate posterior for remaining weeks
        # ================================================================
        posterior_mean = []
        posterior_std = []

        for i in range(weeks_remaining):
            week_idx = weeks_elapsed + i

            # Decay factor: bias influence decreases for far-future weeks
            # Week 0 after actuals: full effect, Week 10: ~37% effect
            decay = np.exp(-self.BIAS_DECAY_RATE * i)

            # Adjusted bias for this week
            week_bias = observed_bias * significance_factor * decay

            # Posterior mean: prior + adjusted bias
            post_mean = self.prior_mean[week_idx] + week_bias
            post_mean = max(0, post_mean)  # No negative forecasts

            # Posterior variance: combines prior uncertainty + observation uncertainty
            # Uncertainty GROWS for more distant weeks
            uncertainty_growth = 1 + (self.UNCERTAINTY_GROWTH_RATE * i)

            # Combine uncertainties (sum of variances for independent sources)
            combined_var = (
                self.prior_std[week_idx] ** 2 +
                (obs_std * decay) ** 2
            )
            post_std = np.sqrt(combined_var) * uncertainty_growth

            posterior_mean.append(post_mean)
            posterior_std.append(post_std)

        posterior_mean = np.array(posterior_mean)
        posterior_std = np.array(posterior_std)

        # ================================================================
        # STEP 4: Calculate prediction intervals
        # ================================================================
        lower_bound = np.maximum(0, posterior_mean - self.Z_95 * posterior_std)
        upper_bound = posterior_mean + self.Z_95 * posterior_std

        # ================================================================
        # STEP 5: Calculate posterior confidence
        # ================================================================
        # Confidence based on coefficient of variation of posterior
        avg_cv = np.mean(posterior_std / np.maximum(posterior_mean, 1))
        posterior_confidence = max(self.MIN_CONFIDENCE, 1.0 - avg_cv)

        # Adjust confidence based on data quality
        if weeks_elapsed >= 3:
            posterior_confidence = min(0.95, posterior_confidence + 0.05)

        # ================================================================
        # STEP 6: Assemble final forecast
        # ================================================================
        # Combine actuals + posterior forecast
        final_forecast = list(actuals.astype(int)) + list(posterior_mean.astype(int))
        final_lower = list(actuals.astype(int)) + list(lower_bound.astype(int))
        final_upper = list(actuals.astype(int)) + list(upper_bound.astype(int))

        total_demand = sum(final_forecast)

        # Calculate overall adjustment factor for reporting
        original_remaining = sum(self.prior_mean[weeks_elapsed:])
        new_remaining = sum(posterior_mean)
        if original_remaining > 0:
            effective_adjustment = new_remaining / original_remaining
        else:
            effective_adjustment = 1.0

        # Uncertainty growth percentage
        original_interval_width = np.mean(self.prior_std[weeks_elapsed:] * 2 * self.Z_95)
        new_interval_width = np.mean(posterior_std * 2 * self.Z_95)
        if original_interval_width > 0:
            uncertainty_growth_pct = (new_interval_width / original_interval_width - 1) * 100
        else:
            uncertainty_growth_pct = 0

        # ================================================================
        # STEP 7: Generate intelligent explanation
        # ================================================================
        explanation = self._generate_explanation(
            weeks_elapsed=weeks_elapsed,
            weeks_remaining=weeks_remaining,
            observed_bias=observed_bias,
            bias_significance=bias_significance,
            significance_level=significance_level,
            significance_factor=significance_factor,
            obs_std=obs_std,
            effective_adjustment=effective_adjustment,
            original_total=int(sum(self.prior_mean)),
            new_total=total_demand,
            posterior_confidence=posterior_confidence,
        )

        return BayesianReforecastResult(
            forecast_by_week=final_forecast,
            lower_bound=final_lower,
            upper_bound=final_upper,
            total_demand=total_demand,
            confidence=round(posterior_confidence, 2),
            explanation=explanation,
            observed_bias=round(observed_bias, 1),
            bias_significance=round(bias_significance, 2),
            adjustment_applied=round(effective_adjustment, 3),
            uncertainty_growth_pct=round(uncertainty_growth_pct, 1),
        )

    def _generate_explanation(
        self,
        weeks_elapsed: int,
        weeks_remaining: int,
        observed_bias: float,
        bias_significance: float,
        significance_level: str,
        significance_factor: float,
        obs_std: float,
        effective_adjustment: float,
        original_total: int,
        new_total: int,
        posterior_confidence: float,
    ) -> str:
        """
        Generate intelligent, context-aware explanation for the reforecast.

        This is what makes it "agentic" - the explanation demonstrates
        understanding of statistical concepts and business context.
        """
        # Direction and magnitude
        if observed_bias > 0:
            direction = "outperforming"
            direction_emoji = "📈"
        else:
            direction = "underperforming"
            direction_emoji = "📉"

        # Calculate percentage deviation
        prior_avg = np.mean(self.prior_mean[:weeks_elapsed])
        if prior_avg > 0:
            pct_deviation = abs(observed_bias) / prior_avg * 100
        else:
            pct_deviation = 0

        # Build explanation sections
        sections = []

        # Section 1: Observation summary
        sections.append(
            f"{direction_emoji} **Observation:** Based on {weeks_elapsed} week{'s' if weeks_elapsed > 1 else ''} "
            f"of actual sales, demand is {direction} forecast by {pct_deviation:.1f}% "
            f"({'+' if observed_bias > 0 else ''}{observed_bias:,.0f} units/week average)."
        )

        # Section 2: Statistical assessment
        if weeks_elapsed == 1:
            stat_assessment = (
                f"⚠️ **Statistical Confidence:** With only 1 week of data, this deviation "
                f"has {significance_level} statistical significance (t={bias_significance:.2f}). "
                f"Week-to-week variance (±{obs_std:,.0f} units) makes it difficult to distinguish "
                f"signal from noise."
            )
        elif weeks_elapsed == 2:
            stat_assessment = (
                f"📊 **Statistical Confidence:** With 2 weeks of data, evidence is {significance_level} "
                f"(t={bias_significance:.2f}). Observed consistency: ±{obs_std:,.0f} units variation. "
                f"Confidence will increase substantially with Week 3 data."
            )
        else:
            if significance_level == "strong":
                stat_assessment = (
                    f"✅ **Statistical Confidence:** With {weeks_elapsed} weeks of consistent data, "
                    f"the {direction} trend is statistically significant (t={bias_significance:.2f}, p<0.05). "
                    f"High confidence in forecast adjustment."
                )
            else:
                stat_assessment = (
                    f"📊 **Statistical Confidence:** {weeks_elapsed} weeks analyzed. "
                    f"Evidence is {significance_level} (t={bias_significance:.2f}) due to "
                    f"week-to-week variance of ±{obs_std:,.0f} units."
                )
        sections.append(stat_assessment)

        # Section 3: Adjustment methodology
        adjustment_pct = (effective_adjustment - 1) * 100
        if abs(adjustment_pct) < 1:
            adj_desc = "minimal adjustment applied"
        elif abs(adjustment_pct) < 10:
            adj_desc = f"conservative {adjustment_pct:+.1f}% adjustment applied"
        elif abs(adjustment_pct) < 25:
            adj_desc = f"moderate {adjustment_pct:+.1f}% adjustment applied"
        else:
            adj_desc = f"significant {adjustment_pct:+.1f}% adjustment applied"

        sections.append(
            f"🔄 **Bayesian Update:** {adj_desc.capitalize()} to remaining {weeks_remaining} weeks. "
            f"Adjustment strength: {significance_factor:.0%} of observed bias "
            f"(based on statistical confidence). Bias effect decays exponentially for distant weeks."
        )

        # Section 4: Uncertainty handling
        sections.append(
            f"📐 **Uncertainty:** Prediction intervals widen by ~5% per week into the future, "
            f"reflecting decreased certainty. Posterior confidence: {posterior_confidence:.0%}."
        )

        # Section 5: Result summary
        change_pct = (new_total - original_total) / original_total * 100 if original_total > 0 else 0
        sections.append(
            f"📋 **Result:** Original forecast {original_total:,} → Updated {new_total:,} units "
            f"({change_pct:+.1f}% change)."
        )

        # Section 6: Forward guidance
        if weeks_elapsed < 3:
            weeks_until_confident = 3 - weeks_elapsed
            sections.append(
                f"👁️ **Next Steps:** Monitor Week {weeks_elapsed + 1} actuals. "
                f"{weeks_until_confident} more week{'s' if weeks_until_confident > 1 else ''} of data "
                f"needed for high-confidence adjustment."
            )

        return "\n\n".join(sections)

    def _create_result_from_prior(self) -> BayesianReforecastResult:
        """Return prior forecast when no actuals available."""
        lower = (self.prior_mean - self.Z_95 * self.prior_std).astype(int).tolist()
        upper = (self.prior_mean + self.Z_95 * self.prior_std).astype(int).tolist()

        return BayesianReforecastResult(
            forecast_by_week=self.prior_mean.astype(int).tolist(),
            lower_bound=lower,
            upper_bound=upper,
            total_demand=int(sum(self.prior_mean)),
            confidence=self.prior_confidence,
            explanation="No actual sales data available yet. Showing original forecast.",
            observed_bias=0.0,
            bias_significance=0.0,
            adjustment_applied=1.0,
            uncertainty_growth_pct=0.0,
        )

    def _create_result_actuals_only(self, actuals: np.ndarray) -> BayesianReforecastResult:
        """Return actuals when season is complete."""
        actuals_list = actuals.astype(int).tolist()

        return BayesianReforecastResult(
            forecast_by_week=actuals_list,
            lower_bound=actuals_list,
            upper_bound=actuals_list,
            total_demand=int(sum(actuals)),
            confidence=1.0,
            explanation="Season complete. Showing actual sales data.",
            observed_bias=0.0,
            bias_significance=0.0,
            adjustment_applied=1.0,
            uncertainty_growth_pct=0.0,
        )


def bayesian_reforecast(
    original_forecast_by_week: List[int],
    actual_sales: List[int],
    original_confidence: float = 0.80,
    original_lower_bound: Optional[List[int]] = None,
    original_upper_bound: Optional[List[int]] = None,
) -> BayesianReforecastResult:
    """
    Convenience function for Bayesian reforecasting.

    This is the main entry point for the reforecasting logic.

    Args:
        original_forecast_by_week: Original forecast values by week
        actual_sales: Actual sales for weeks with data
        original_confidence: Confidence from original forecast
        original_lower_bound: Optional lower bounds from original forecast
        original_upper_bound: Optional upper bounds from original forecast

    Returns:
        BayesianReforecastResult with updated forecast and explanation

    Example:
        >>> result = bayesian_reforecast(
        ...     original_forecast_by_week=[1000, 1100, 1200, 1300, 1400],
        ...     actual_sales=[1300, 1400],  # Outperforming by ~20%
        ...     original_confidence=0.85,
        ... )
        >>> print(result.explanation)
        >>> print(f"Adjusted: {result.total_demand:,}")
    """
    bounds = None
    if original_lower_bound and original_upper_bound:
        bounds = (original_lower_bound, original_upper_bound)

    reforecaster = BayesianReforecaster(
        prior_forecast=original_forecast_by_week,
        prior_confidence=original_confidence,
        prior_bounds=bounds,
    )

    return reforecaster.update_with_actuals(actual_sales)
