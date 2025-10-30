from fastapi import APIRouter, HTTPException, status
import logging

from app.schemas.workflow_schemas import (
    ParameterExtractionRequest,
    ParameterExtractionResponse,
)
from app.services.parameter_extractor import parameter_extractor

logger = logging.getLogger("fashion_forecast")

router = APIRouter()

@router.post("/parameters/extract", response_model=ParameterExtractionResponse, status_code=status.HTTP_200_OK)
async def extract_parameters(request: ParameterExtractionRequest):
    """
    Extract season parameters from natural language input using Azure OpenAI.

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
    - 500: Azure OpenAI API failure or service error
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
        # Service failure (Azure OpenAI error, etc.)
        logger.error(f"Parameter extraction service failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parameter extraction failed: {str(e)}"
        )
