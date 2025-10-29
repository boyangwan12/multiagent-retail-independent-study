import json
import logging
from datetime import date, timedelta
from typing import Tuple, Optional
from pydantic import ValidationError

from app.core.openai_client import openai_client
from app.schemas.parameters import (
    SeasonParameters,
    ParameterExtractionRequest,
    ParameterExtractionResponse,
    ReplenishmentStrategy,
)

logger = logging.getLogger("fashion_forecast")

class ParameterExtractor:
    """Extract season parameters from natural language using OpenAI"""

    EXTRACTION_PROMPT_TEMPLATE = """You are a retail season planning assistant. Extract 5 key parameters from the user's description.

**Parameters to Extract:**

1. **forecast_horizon_weeks** (integer, 1-52):
   - How many weeks ahead to forecast
   - Examples: "12 weeks" → 12, "3 months" → 12, "quarter" → 13
   - Default: 12 if not specified

2. **season_start_date** (date, YYYY-MM-DD):
   - When the season begins
   - Examples: "March 1st" → "2025-03-01", "next Monday" → calculate next Monday
   - Default: Next Monday from today if not specified

3. **replenishment_strategy** (enum: "none", "weekly", "bi-weekly"):
   - How often to replenish from DC to stores
   - Keywords: "no replenishment" / "one-shot" → "none", "weekly" → "weekly", "every 2 weeks" → "bi-weekly"
   - Default: "weekly" if not specified

4. **dc_holdback_percentage** (float, 0.0-1.0):
   - % of inventory to hold at DC for replenishment
   - Examples: "45%" → 0.45, "zero holdback" → 0.0, "half" → 0.5
   - Default: 0.45 (45%) if not specified

5. **markdown_checkpoint_week** (integer, 1-52, optional):
   - Week number to check sell-through and apply markdown
   - Examples: "week 6" → 6, "mid-season" → (horizon / 2)
   - Default: null if no markdown mentioned

6. **markdown_threshold** (float, 0.0-1.0, optional):
   - Sell-through % threshold to trigger markdown
   - Examples: "60%" → 0.60, "below 50%" → 0.50
   - Default: null if no markdown mentioned

**User Input:**
"{user_input}"

**Your Task:**
1. Extract all parameters from the user input
2. Use defaults for any missing parameters
3. Calculate season_end_date from season_start_date + forecast_horizon_weeks
4. Return ONLY a valid JSON object with this exact structure:

{{
  "forecast_horizon_weeks": <integer>,
  "season_start_date": "<YYYY-MM-DD>",
  "season_end_date": "<YYYY-MM-DD>",
  "replenishment_strategy": "<none|weekly|bi-weekly>",
  "dc_holdback_percentage": <float>,
  "markdown_checkpoint_week": <integer or null>,
  "markdown_threshold": <float or null>,
  "confidence": "<high|medium|low>",
  "reasoning": "<brief explanation of extraction logic>"
}}

**Confidence Levels:**
- high: All 5 core parameters explicitly mentioned
- medium: 3-4 parameters explicit, 1-2 inferred from context
- low: Only 1-2 parameters explicit, most are defaults

**Today's Date:** {today}

Return ONLY the JSON object, no markdown formatting or extra text."""

    def extract(self, request: ParameterExtractionRequest) -> ParameterExtractionResponse:
        """
        Extract season parameters from natural language input.

        Args:
            request: Contains natural language input text

        Returns:
            ParameterExtractionResponse with extracted parameters, confidence, reasoning

        Raises:
            ValueError: If input is invalid or LLM extraction fails
        """
        # Validate input
        if not request.user_input or len(request.user_input.strip()) == 0:
            raise ValueError("Input cannot be empty")

        if len(request.user_input) > 500:
            raise ValueError("Input exceeds 500 character limit")

        # Build LLM prompt
        today_str = date.today().isoformat()
        prompt = self.EXTRACTION_PROMPT_TEMPLATE.format(
            user_input=request.user_input,
            today=today_str
        )

        logger.info(f"Extracting parameters from: '{request.user_input[:100]}...'")

        try:
            # Call OpenAI
            response_text = openai_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Deterministic extraction
                max_tokens=500,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Parse JSON response
            response_data = json.loads(response_text)

            # Extract parameters
            parameters = SeasonParameters(
                forecast_horizon_weeks=response_data["forecast_horizon_weeks"],
                season_start_date=date.fromisoformat(response_data["season_start_date"]),
                season_end_date=date.fromisoformat(response_data["season_end_date"]),
                replenishment_strategy=ReplenishmentStrategy(response_data["replenishment_strategy"]),
                dc_holdback_percentage=response_data["dc_holdback_percentage"],
                markdown_checkpoint_week=response_data.get("markdown_checkpoint_week"),
                markdown_threshold=response_data.get("markdown_threshold"),
            )

            confidence = response_data.get("confidence", "medium")
            reasoning = response_data.get("reasoning", "Parameters extracted successfully")

            logger.info(f"✓ Extraction complete | Confidence: {confidence} | Horizon: {parameters.forecast_horizon_weeks} weeks")

            return ParameterExtractionResponse(
                parameters=parameters,
                confidence=confidence,
                reasoning=reasoning,
                raw_llm_output=response_text,
            )

        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")

            # Fallback to defaults
            logger.warning("Falling back to default parameters")
            return self._fallback_defaults(request.user_input, error=str(e))

        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            raise ValueError(f"Parameter extraction failed: {str(e)}")

    def _fallback_defaults(self, user_input: str, error: str) -> ParameterExtractionResponse:
        """
        Return default parameters when extraction fails.

        Args:
            user_input: Original user input
            error: Error message from failed extraction

        Returns:
            ParameterExtractionResponse with default parameters
        """
        # Calculate next Monday
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # If today is Monday, use next Monday
        next_monday = today + timedelta(days=days_until_monday)

        # Default 12-week horizon
        season_end = next_monday + timedelta(weeks=12)

        parameters = SeasonParameters(
            forecast_horizon_weeks=12,
            season_start_date=next_monday,
            season_end_date=season_end,
            replenishment_strategy=ReplenishmentStrategy.WEEKLY,
            dc_holdback_percentage=0.45,
            markdown_checkpoint_week=None,
            markdown_threshold=None,
        )

        reasoning = (
            f"Extraction failed ({error}). Using defaults: "
            f"12 weeks starting {next_monday.isoformat()}, weekly replenishment, 45% holdback, no markdown."
        )

        return ParameterExtractionResponse(
            parameters=parameters,
            confidence="low",
            reasoning=reasoning,
            raw_llm_output=None,
        )

# Singleton instance
parameter_extractor = ParameterExtractor()
