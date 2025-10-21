# Story: Parameter Extraction API with OpenAI Integration

**Epic:** Phase 3 - Backend Architecture
**Story ID:** PHASE3-005
**Status:** Draft
**Estimate:** 4 hours
**Agent Model Used:** _TBD_
**Dependencies:** PHASE3-003 (Pydantic Schemas), PHASE3-004 (FastAPI Application Setup)

---

## Story

As a backend developer,
I want to create a parameter extraction service that uses OpenAI API to extract 5 key parameters from natural language input,
So that users can describe their retail strategy in free-form text and the system automatically configures the multi-agent workflow without code changes.

**Business Value:** This is the core innovation of v3.3 - parameter-driven architecture. By extracting parameters from natural language, the system can adapt to different retail strategies (Zara-style, luxury, furniture) without code modifications. This enables the same codebase to handle multiple retail archetypes, dramatically reducing development complexity and maintenance burden.

**Epic Context:** This is Task 5 of 14 in Phase 3. It builds on the Pydantic schemas (PHASE3-003) and FastAPI setup (PHASE3-004) to create the first AI-powered endpoint. Parameter extraction is the gateway to the entire workflow - all subsequent agent decisions depend on these extracted parameters. This story focuses on the LLM integration; actual agent reasoning happens in later phases.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ `POST /api/v1/parameters/extract` endpoint accepts natural language input (up to 500 characters)
2. ✅ Service calls OpenAI gpt-4o-mini with structured extraction prompt
3. ✅ LLM extracts 5 parameters:
   - `forecast_horizon_weeks` (1-52 weeks)
   - `season_start_date` and `season_end_date` (calculated from horizon)
   - `replenishment_strategy` ("none", "weekly", "bi-weekly")
   - `dc_holdback_percentage` (0.0-1.0)
   - `markdown_checkpoint_week` (optional, null if no markdowns)
   - `markdown_threshold` (optional, 0.0-1.0)
4. ✅ Response includes extracted parameters as `SeasonParameters` object
5. ✅ Response includes confidence level ("high", "medium", "low")
6. ✅ Response includes reasoning (LLM explanation of extraction logic)
7. ✅ Fallback logic applies defaults for missing parameters (e.g., 12 weeks, next Monday, 45% holdback)
8. ✅ Validation rejects invalid input (empty text, >500 chars, no meaningful content)
9. ✅ Error handling for OpenAI API failures (timeout, rate limit, invalid response)
10. ✅ Endpoint completes in <5 seconds for typical input

### Quality Requirements

11. ✅ OpenAI client configured with retry logic (exponential backoff, max 3 attempts)
12. ✅ LLM prompt uses structured output format (JSON mode)
13. ✅ Confidence scoring based on extraction completeness (all 5 vs partial)
14. ✅ Unit tests cover Zara-style, standard, and ambiguous inputs
15. ✅ Integration test with actual OpenAI API call

---

## Tasks

### Task 1: Create OpenAI Client Configuration

**Subtasks:**
- [ ] Create `backend/app/core/openai_client.py` with OpenAI client setup
- [ ] Load OpenAI credentials from environment variables (API key, model)
- [ ] Configure retry logic with exponential backoff (max 3 attempts, 2s initial delay)
- [ ] Add timeout configuration (10 seconds per request)
- [ ] Implement client singleton pattern for reuse
- [ ] Test connection with simple API call
- [ ] Handle authentication errors gracefully

**Expected Output:** Reusable OpenAI client with retry and timeout logic

**Complete Code Template (`backend/app/core/openai_client.py`):**
```python
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from backend.app.core.config import settings

logger = logging.getLogger("fashion_forecast")

class OpenAIClient:
    """Singleton OpenAI client with retry logic"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            logger.info("Initializing OpenAI client...")
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=10.0,  # 10 second timeout
            )
            logger.info("✓ OpenAI client initialized")

    @property
    def client(self) -> OpenAI:
        """Get the OpenAI client instance"""
        return self._client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def chat_completion(self, messages: list[dict], **kwargs) -> str:
        """
        Make a chat completion request with retry logic.

        Args:
            messages: List of message dicts (role, content)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Response content string

        Raises:
            openai.APIError: If API call fails after retries
        """
        try:
            logger.debug(f"Calling OpenAI with {len(messages)} messages")

            response = self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                **kwargs
            )

            content = response.choices[0].message.content
            logger.debug(f"✓ Received response ({len(content)} chars)")

            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

# Singleton instance
openai_client = OpenAIClient()
```

**Reference:** `planning/3_technical_architecture_v3.3.md` lines 230-240 (OpenAI configuration)

---

### Task 2: Create Parameter Extraction Service

**Subtasks:**
- [ ] Create `backend/app/services/__init__.py`
- [ ] Create `backend/app/services/parameter_extractor.py`
- [ ] Implement LLM prompt template for parameter extraction
- [ ] Parse LLM JSON response to `SeasonParameters` object
- [ ] Implement confidence scoring logic
- [ ] Add fallback defaults for missing parameters
- [ ] Add input validation (length, content quality)
- [ ] Test with sample inputs (Zara-style, standard, ambiguous)

**Expected Output:** Service module that converts natural language → SeasonParameters

**Complete Code Template (`backend/app/services/parameter_extractor.py`):**
```python
import json
import logging
from datetime import date, timedelta
from typing import Tuple, Optional
from pydantic import ValidationError

from backend.app.core.openai_client import openai_client
from backend.app.schemas.parameters import (
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
```

**Reference:** `implementation_plan.md` lines 225-238 (LLM prompt template)

---

### Task 3: Create Parameter Extraction Endpoint

**Subtasks:**
- [ ] Create `backend/app/api/v1/endpoints/parameters.py`
- [ ] Implement `POST /api/v1/parameters/extract` endpoint
- [ ] Accept `ParameterExtractionRequest` in request body
- [ ] Call `parameter_extractor.extract()` service
- [ ] Return `ParameterExtractionResponse` with 200 status
- [ ] Handle errors (400 for invalid input, 500 for service failures)
- [ ] Add to main API router
- [ ] Test with Postman/cURL

**Expected Output:** Working endpoint that returns extracted parameters

**Complete Code Template (`backend/app/api/v1/endpoints/parameters.py`):**
```python
from fastapi import APIRouter, HTTPException, status
import logging

from backend.app.schemas.parameters import (
    ParameterExtractionRequest,
    ParameterExtractionResponse,
)
from backend.app.services.parameter_extractor import parameter_extractor

logger = logging.getLogger("fashion_forecast")

router = APIRouter()

@router.post("/parameters/extract", response_model=ParameterExtractionResponse, status_code=status.HTTP_200_OK)
async def extract_parameters(request: ParameterExtractionRequest):
    """
    Extract season parameters from natural language input using OpenAI.

    **Example Input:**
    ```json
    {
      "user_input": "I'm planning a 12-week spring fashion season starting March 1st. Send all inventory to stores at launch with no DC holdback. I don't want ongoing replenishment - just one initial allocation. Check for markdown opportunities at week 6 if we're below 60% sell-through."
    }
    ```

    **Example Output:**
    ```json
    {
      "parameters": {
        "forecast_horizon_weeks": 12,
        "season_start_date": "2025-03-01",
        "season_end_date": "2025-05-23",
        "replenishment_strategy": "none",
        "dc_holdback_percentage": 0.0,
        "markdown_checkpoint_week": 6,
        "markdown_threshold": 0.60
      },
      "confidence": "high",
      "reasoning": "All 5 core parameters explicitly mentioned: 12 weeks, March 1st start, no replenishment (Zara-style one-shot), 0% holdback, week 6 markdown checkpoint at 60% threshold.",
      "raw_llm_output": "{...}"
    }
    ```

    **Errors:**
    - 400: Invalid input (empty, too long, no meaningful content)
    - 500: OpenAI API failure or service error
    """
    try:
        logger.info("POST /api/v1/parameters/extract")

        # Extract parameters using service
        response = parameter_extractor.extract(request)

        logger.info(f"✓ Parameters extracted | Confidence: {response.confidence}")

        return response

    except ValueError as e:
        # Invalid input (empty, too long, etc.)
        logger.warning(f"Invalid extraction request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Service failure (OpenAI error, etc.)
        logger.error(f"Parameter extraction service failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parameter extraction failed: {str(e)}"
        )
```

**Update `backend/app/api/v1/router.py`:**
```python
from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, parameters

api_router = APIRouter()

# Include health check endpoint
api_router.include_router(health.router, tags=["Health"])

# Include parameter extraction endpoint
api_router.include_router(parameters.router, tags=["Parameters"])
```

**Reference:** `planning/4_prd_v3.3.md` lines 186-224 (Parameter extraction user story)

---

### Task 4: Add Confidence Scoring Logic

**Subtasks:**
- [ ] Implement confidence calculation in `parameter_extractor.py`
- [ ] High: All 5 core parameters explicitly mentioned (100% extraction rate)
- [ ] Medium: 3-4 parameters explicit, 1-2 inferred (60-80% extraction rate)
- [ ] Low: Only 1-2 parameters explicit, mostly defaults (<60% extraction rate)
- [ ] Include confidence in LLM prompt instructions
- [ ] Validate confidence levels in unit tests

**Expected Output:** Reliable confidence scoring based on extraction completeness

**Confidence Calculation Logic:**
```python
def calculate_confidence(response_data: dict, defaults_used: int) -> str:
    """
    Calculate confidence based on how many parameters were explicitly extracted.

    Args:
        response_data: Parsed LLM JSON response
        defaults_used: Number of parameters that fell back to defaults

    Returns:
        Confidence level ("high", "medium", "low")
    """
    # Count explicit parameters (5 core parameters)
    explicit_count = 5 - defaults_used

    if explicit_count >= 5:
        return "high"
    elif explicit_count >= 3:
        return "medium"
    else:
        return "low"
```

**Note:** Confidence scoring is instructed to the LLM in the prompt. The LLM determines confidence based on how many parameters were explicit vs inferred. This approach leverages LLM reasoning instead of manual heuristics.

---

### Task 5: Add Fallback Defaults Logic

**Subtasks:**
- [ ] Implement default value calculation in `_fallback_defaults()` method
- [ ] Default `forecast_horizon_weeks`: 12 weeks
- [ ] Default `season_start_date`: Next Monday from today
- [ ] Default `replenishment_strategy`: "weekly"
- [ ] Default `dc_holdback_percentage`: 0.45 (45%)
- [ ] Default `markdown_checkpoint_week`: null (no markdown)
- [ ] Default `markdown_threshold`: null
- [ ] Test fallback with empty/invalid inputs

**Expected Output:** Sensible defaults when extraction fails

**Fallback Logic (already in code template above):**
- Next Monday calculation prevents starting in the past
- 12 weeks is a standard retail season length
- Weekly replenishment is the most common strategy
- 45% holdback is a balanced allocation (55% initial, 45% reserve)
- No markdown by default (user must explicitly request it)

---

### Task 6: Create Unit Tests for Parameter Extraction

**Subtasks:**
- [ ] Create `backend/tests/services/__init__.py`
- [ ] Create `backend/tests/services/test_parameter_extractor.py`
- [ ] Test case 1: Zara-style input (0% holdback, no replenishment, week 6 markdown)
- [ ] Test case 2: Standard input (45% holdback, weekly replenishment, no markdown)
- [ ] Test case 3: Ambiguous input (only horizon specified, rest defaults)
- [ ] Test case 4: Empty input (ValueError)
- [ ] Test case 5: >500 character input (ValueError)
- [ ] Test case 6: OpenAI API failure (fallback to defaults)
- [ ] Mock OpenAI responses for deterministic tests
- [ ] Verify confidence levels are correct

**Expected Output:** 80%+ test coverage for parameter extraction service

**Unit Test Template (`backend/tests/services/test_parameter_extractor.py`):**
```python
import pytest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from backend.app.services.parameter_extractor import parameter_extractor
from backend.app.schemas.parameters import ParameterExtractionRequest, ReplenishmentStrategy

class TestParameterExtractor:
    """Test suite for parameter extraction service"""

    @patch("backend.app.services.parameter_extractor.openai_client")
    def test_zara_style_extraction(self, mock_client):
        """Test extraction with Zara-style parameters (0% holdback, no replenishment)"""

        # Mock LLM response
        mock_response = """
        {
          "forecast_horizon_weeks": 12,
          "season_start_date": "2025-03-01",
          "season_end_date": "2025-05-23",
          "replenishment_strategy": "none",
          "dc_holdback_percentage": 0.0,
          "markdown_checkpoint_week": 6,
          "markdown_threshold": 0.60,
          "confidence": "high",
          "reasoning": "All parameters explicitly mentioned: 12 weeks, March 1st, no replenishment, 0% holdback, week 6 markdown."
        }
        """
        mock_client.chat_completion.return_value = mock_response

        # Test input
        request = ParameterExtractionRequest(
            user_input="I'm planning a 12-week spring fashion season starting March 1st. "
                       "Send all inventory to stores at launch with no DC holdback. "
                       "I don't want ongoing replenishment - just one initial allocation. "
                       "Check for markdown opportunities at week 6 if we're below 60% sell-through."
        )

        # Extract parameters
        result = parameter_extractor.extract(request)

        # Assertions
        assert result.parameters.forecast_horizon_weeks == 12
        assert result.parameters.season_start_date == date(2025, 3, 1)
        assert result.parameters.replenishment_strategy == ReplenishmentStrategy.NONE
        assert result.parameters.dc_holdback_percentage == 0.0
        assert result.parameters.markdown_checkpoint_week == 6
        assert result.parameters.markdown_threshold == 0.60
        assert result.confidence == "high"

    @patch("backend.app.services.parameter_extractor.openai_client")
    def test_standard_extraction(self, mock_client):
        """Test extraction with standard parameters (45% holdback, weekly replenishment)"""

        mock_response = """
        {
          "forecast_horizon_weeks": 26,
          "season_start_date": "2025-04-01",
          "season_end_date": "2025-09-30",
          "replenishment_strategy": "weekly",
          "dc_holdback_percentage": 0.45,
          "markdown_checkpoint_week": null,
          "markdown_threshold": null,
          "confidence": "high",
          "reasoning": "All core parameters specified: 26 weeks (6 months), April 1st start, weekly replenishment, 45% holdback, no markdown."
        }
        """
        mock_client.chat_completion.return_value = mock_response

        request = ParameterExtractionRequest(
            user_input="Plan a 6-month summer season starting April 1st with weekly replenishment and 45% DC holdback."
        )

        result = parameter_extractor.extract(request)

        assert result.parameters.forecast_horizon_weeks == 26
        assert result.parameters.replenishment_strategy == ReplenishmentStrategy.WEEKLY
        assert result.parameters.dc_holdback_percentage == 0.45
        assert result.parameters.markdown_checkpoint_week is None
        assert result.confidence == "high"

    def test_empty_input_raises_error(self):
        """Test that empty input raises ValueError"""

        request = ParameterExtractionRequest(user_input="")

        with pytest.raises(ValueError, match="Input cannot be empty"):
            parameter_extractor.extract(request)

    def test_long_input_raises_error(self):
        """Test that input >500 chars raises ValueError"""

        request = ParameterExtractionRequest(user_input="x" * 501)

        with pytest.raises(ValueError, match="exceeds 500 character limit"):
            parameter_extractor.extract(request)

    @patch("backend.app.services.parameter_extractor.openai_client")
    def test_fallback_on_llm_failure(self, mock_client):
        """Test fallback to defaults when LLM returns invalid JSON"""

        # Mock invalid JSON response
        mock_client.chat_completion.return_value = "Invalid JSON response"

        request = ParameterExtractionRequest(
            user_input="Plan a season"
        )

        result = parameter_extractor.extract(request)

        # Should fall back to defaults
        assert result.parameters.forecast_horizon_weeks == 12
        assert result.parameters.replenishment_strategy == ReplenishmentStrategy.WEEKLY
        assert result.parameters.dc_holdback_percentage == 0.45
        assert result.confidence == "low"
        assert "Extraction failed" in result.reasoning
```

---

### Task 7: Integration Testing with OpenAI

**Subtasks:**
- [ ] Create `backend/tests/integration/__init__.py`
- [ ] Create `backend/tests/integration/test_azure_openai.py`
- [ ] Test actual API call to OpenAI (requires valid credentials)
- [ ] Verify LLM returns valid JSON format
- [ ] Verify parameters are correctly extracted
- [ ] Mark as `@pytest.mark.integration` (skip in CI if no API key)
- [ ] Document how to run integration tests locally

**Expected Output:** Validated OpenAI integration with real API calls

**Integration Test Template:**
```python
import pytest
from backend.app.services.parameter_extractor import parameter_extractor
from backend.app.schemas.parameters import ParameterExtractionRequest

@pytest.mark.integration
class TestAzureOpenAIIntegration:
    """Integration tests for OpenAI parameter extraction"""

    def test_real_api_call_zara_style(self):
        """Test parameter extraction with real OpenAI API call"""

        request = ParameterExtractionRequest(
            user_input="I'm planning a 12-week spring fashion season starting March 1st. "
                       "Send all inventory to stores at launch with no DC holdback. "
                       "I don't want ongoing replenishment - just one initial allocation. "
                       "Check for markdown opportunities at week 6 if we're below 60% sell-through."
        )

        result = parameter_extractor.extract(request)

        # Verify structure
        assert result.parameters is not None
        assert result.confidence in ["high", "medium", "low"]
        assert result.reasoning is not None

        # Verify extracted parameters make sense
        assert 1 <= result.parameters.forecast_horizon_weeks <= 52
        assert result.parameters.season_start_date > date.today()
        assert 0.0 <= result.parameters.dc_holdback_percentage <= 1.0

        # For Zara-style input, expect specific values
        assert result.parameters.replenishment_strategy == "none"
        assert result.parameters.dc_holdback_percentage == 0.0
        assert result.parameters.markdown_checkpoint_week == 6

        print(f"✓ Integration test passed | Confidence: {result.confidence}")
        print(f"  Reasoning: {result.reasoning}")
```

---

### Task 8: Error Handling & Edge Cases

**Subtasks:**
- [ ] Handle OpenAI timeout errors (10s timeout)
- [ ] Handle rate limit errors (retry with exponential backoff)
- [ ] Handle invalid API key errors (clear error message)
- [ ] Handle malformed LLM responses (fall back to defaults)
- [ ] Handle date parsing errors (invalid date formats)
- [ ] Test with ambiguous inputs ("plan a season", "forecast demand")
- [ ] Log all errors with full context for debugging

**Expected Output:** Robust error handling for production readiness

**Error Scenarios:**
1. **Timeout:** LLM takes >10s → Return fallback defaults with "low" confidence
2. **Rate Limit:** 429 error → Retry 3 times with exponential backoff → Fail with 500 error
3. **Invalid Key:** 401 error → Fail immediately with clear message
4. **Malformed JSON:** LLM returns text → Parse error → Fallback to defaults
5. **Invalid Date:** LLM returns "March 32" → Validation error → Fallback
6. **Ambiguous Input:** "plan a season" → LLM uses all defaults → "low" confidence

---

## Dev Notes

### OpenAI Integration

**Why OpenAI?**
- **Enterprise-Ready:** SLA, data privacy (zero-day retention), compliance
- **Cost-Effective:** gpt-4o-mini is 60x cheaper than gpt-4 (~$0.01 per extraction)
- **Structured Output:** JSON mode ensures valid parameter extraction
- **Low Latency:** <2 seconds per request (regional dependent)

**API Configuration:**
- **Endpoint:** `https://YOUR_RESOURCE.openai.azure.com/`
- **Deployment:** `gpt-4o-mini` (recommended for parameter extraction)
- **API Version:** `2024-10-21` (latest stable)
- **Temperature:** 0.0 (deterministic extraction)
- **Max Tokens:** 500 (sufficient for JSON response)

---

### LLM Prompt Engineering

**Prompt Structure:**
1. **Role:** "You are a retail season planning assistant"
2. **Task:** "Extract 5 key parameters from user input"
3. **Parameter Definitions:** Detailed descriptions with examples
4. **Output Format:** JSON schema with exact structure
5. **Confidence Levels:** Definitions for high/medium/low
6. **Context:** Today's date for relative date calculations

**Prompt Best Practices:**
- **Explicit Examples:** "March 1st" → "2025-03-01"
- **Default Values:** "Default: 12 if not specified"
- **Enum Values:** "none|weekly|bi-weekly" (closed set)
- **JSON Mode:** `response_format={"type": "json_object"}` forces JSON output
- **No Markdown:** "Return ONLY the JSON object" prevents code blocks

---

### Confidence Scoring Strategy

**Confidence Levels:**

**High (90%+ confidence):**
- All 5 core parameters explicitly mentioned
- Dates are specific (not "next week")
- Percentages are numeric (not "most of it")
- Example: "12 weeks starting March 1st, 0% holdback, no replenishment, week 6 markdown at 60%"

**Medium (60-80% confidence):**
- 3-4 parameters explicit, 1-2 inferred from context
- Dates are relative ("next Monday") but calculable
- Percentages are qualitative ("half") but clear
- Example: "12 weeks starting next Monday, send everything to stores"

**Low (<60% confidence):**
- Only 1-2 parameters explicit, most are defaults
- Ambiguous phrasing ("plan a season", "forecast demand")
- Missing critical details (no horizon, no dates)
- Example: "I need a forecast for spring"

---

### Fallback Defaults Rationale

**Default Values:**
- **12 weeks:** Standard retail season (quarterly)
- **Next Monday:** Industry standard for season start (avoid mid-week confusion)
- **Weekly replenishment:** Most common strategy for fashion retail
- **45% holdback:** Balanced allocation (55% initial, 45% reserve)
- **No markdown:** Conservative approach (user must explicitly request)

**Why Next Monday?**
- Retail seasons typically start on Mondays (align with weekly replenishment cycles)
- Avoids starting in the past (if today is Friday, don't start last Monday)
- Prevents mid-week confusion (easier for store managers)

---

### JSON Mode vs Function Calling

**Why JSON Mode?**
- **Simpler:** Single API call, no function definitions
- **Flexible:** Can handle optional fields (markdown_checkpoint_week)
- **Deterministic:** Temperature=0.0 ensures consistent extraction
- **Cost-Effective:** Fewer tokens than function calling

**Function Calling Alternative (Not Used):**
- Requires defining parameter schema as function
- Less flexible for optional fields
- More complex error handling
- No significant accuracy benefit for this use case

---

### Common Issues & Solutions

**Issue 1: LLM returns markdown-formatted JSON**
- **Symptom:** Response starts with ` ```json\n{...}\n``` `
- **Solution:** Add "Return ONLY the JSON object, no markdown" to prompt
- **Fix:** Strip markdown formatting in parsing logic

**Issue 2: Date parsing fails for relative dates**
- **Symptom:** "next Monday" → LLM returns "next Monday" string
- **Solution:** Provide today's date in prompt, instruct LLM to calculate absolute dates
- **Fix:** Always return YYYY-MM-DD format

**Issue 3: Confidence is always "high"**
- **Symptom:** LLM doesn't adjust confidence based on extraction completeness
- **Solution:** Provide clear confidence definitions in prompt with examples
- **Fix:** Review LLM reasoning, adjust prompt if needed

**Issue 4: OpenAI rate limit exceeded**
- **Symptom:** 429 error on API calls
- **Solution:** Implement exponential backoff retry (already in `openai_client.py`)
- **Fix:** Upgrade Azure tier if frequent rate limits

**Issue 5: Extraction takes >5 seconds**
- **Symptom:** Slow LLM response times
- **Solution:** Reduce `max_tokens` from 500 to 300, use gpt-4o-mini (faster than gpt-4)
- **Fix:** Check Azure region latency, consider switching regions

---

## Testing

### Manual Testing Checklist

- [ ] Start dev server: `uvicorn backend.app.main:app --reload`
- [ ] Test Zara-style input via Postman:
  ```json
  POST http://localhost:8000/api/v1/parameters/extract
  {
    "user_input": "I'm planning a 12-week spring fashion season starting March 1st. Send all inventory to stores at launch with no DC holdback. I don't want ongoing replenishment - just one initial allocation. Check for markdown opportunities at week 6 if we're below 60% sell-through."
  }
  ```
- [ ] Verify response has all 5 parameters extracted correctly
- [ ] Verify confidence is "high"
- [ ] Test standard input (weekly replenishment, 45% holdback)
- [ ] Verify confidence adjusts appropriately
- [ ] Test ambiguous input ("plan a season")
- [ ] Verify fallback defaults are applied
- [ ] Verify confidence is "low"
- [ ] Test empty input → 400 error
- [ ] Test >500 character input → 400 error
- [ ] Test with invalid Azure API key → 500 error
- [ ] Verify logs show extraction details

### Verification Commands

```bash
# Test parameter extraction with cURL
curl -X POST http://localhost:8000/api/v1/parameters/extract \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Plan a 12-week season starting next Monday with no DC holdback and no replenishment."
  }'

# Expected output
{
  "parameters": {
    "forecast_horizon_weeks": 12,
    "season_start_date": "2025-10-27",
    "season_end_date": "2026-01-19",
    "replenishment_strategy": "none",
    "dc_holdback_percentage": 0.0,
    "markdown_checkpoint_week": null,
    "markdown_threshold": null
  },
  "confidence": "high",
  "reasoning": "All core parameters explicitly mentioned: 12 weeks, next Monday start, no holdback (0%), no replenishment strategy.",
  "raw_llm_output": "{...}"
}

# Run unit tests
pytest backend/tests/services/test_parameter_extractor.py -v

# Run integration tests (requires OpenAI API key)
pytest backend/tests/integration/test_azure_openai.py -v -m integration

# Check test coverage
pytest --cov=backend/app/services --cov-report=term-missing
```

---

## File List

**Files to Create:**

- `backend/app/core/openai_client.py` (OpenAI client with retry logic)
- `backend/app/services/__init__.py`
- `backend/app/services/parameter_extractor.py` (Parameter extraction service)
- `backend/app/api/v1/endpoints/parameters.py` (Parameter extraction endpoint)
- `backend/tests/services/__init__.py`
- `backend/tests/services/test_parameter_extractor.py` (Unit tests)
- `backend/tests/integration/__init__.py`
- `backend/tests/integration/test_azure_openai.py` (Integration tests)

**Files to Modify:**

- `backend/app/api/v1/router.py` (Add parameters router)
- `backend/app/core/config.py` (Already has OpenAI config from PHASE3-004)

**Files Created in Previous Stories (Referenced):**

- `backend/app/schemas/parameters.py` (PHASE3-003 - Pydantic schemas)
- `backend/app/core/config.py` (PHASE3-004 - Settings with Azure config)
- `backend/.env` (PHASE3-001 - Environment variables)

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial story creation | Product Owner |
| 2025-10-19 | 1.1 | Added Change Log and QA Results sections for template compliance | Product Owner |

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

---

## Definition of Done

- [ ] OpenAI client configured with retry logic and timeout
- [ ] Parameter extraction service extracts all 5 parameters from natural language
- [ ] `POST /api/v1/parameters/extract` endpoint returns valid `ParameterExtractionResponse`
- [ ] Confidence scoring works (high/medium/low based on extraction completeness)
- [ ] Fallback defaults applied when extraction fails
- [ ] Input validation rejects empty/long inputs
- [ ] Error handling for Azure API failures (timeout, rate limit, auth)
- [ ] Unit tests cover Zara-style, standard, and ambiguous inputs
- [ ] Integration test validates real OpenAI API call
- [ ] Manual tests pass (Postman requests return expected parameters)
- [ ] Endpoint completes in <5 seconds for typical input
- [ ] Logs show extraction details for debugging
- [ ] File List updated with all created files

---

## QA Results

_This section will be populated by QA Agent after story implementation and testing_

**QA Status:** Pending
**QA Agent:** TBD
**QA Date:** TBD

### Test Execution Results
- TBD

### Issues Found
- TBD

### Sign-Off
- [ ] All acceptance criteria verified
- [ ] All tests passing
- [ ] No critical issues found
- [ ] Story approved for deployment

---

**Created:** 2025-10-19
**Last Updated:** 2025-10-19 (Template compliance fixes added)
**Story Points:** 4
**Priority:** P0 (Blocker for all workflow tasks)
