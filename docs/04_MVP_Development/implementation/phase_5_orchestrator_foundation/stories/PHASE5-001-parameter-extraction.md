# Story: Extract Season Parameters from Natural Language Input

**Epic:** Phase 5 - Orchestrator Foundation
**Story ID:** PHASE5-001
**Status:** Ready for Implementation
**Estimate:** 4 hours
**Agent:** `*agent dev`
**Dependencies:** Phase 4 Integration complete

**Planning References:**
- PRD v3.3: Section 4.0 (Story 0.1-0.4 - Parameter Gathering via Natural Language)
- Technical Architecture v3.3: Section 4.4 (Orchestrator - Parameter Extraction Service)
- Product Brief v3.3: Section 1.3 (Parameter-Driven Agent System)

---

## Story

As a backend developer,
I want to extract 5 key season parameters from user's natural language strategy description using LLM,
So that the system can configure agent behavior dynamically without code changes.

**Business Value:** Parameter extraction is the foundation of the v3.3 parameter-driven architecture. Without this capability, users would need to fill out rigid forms and the system couldn't adapt to different retail strategies (Zara vs. traditional retail). This LLM-powered extraction enables the "describe your strategy in natural language" user experience that differentiates this system.

**Epic Context:** This is Story 1 of 6 in Phase 5 (Orchestrator Foundation). It's the entry point for the entire workflow - all subsequent stories depend on having clean, validated parameters. This story enables the PRD's Story 0.1-0.4 parameter gathering flow, which must happen before any forecasting begins.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ POST /api/orchestrator/extract-parameters endpoint created
2. ✅ Endpoint accepts JSON payload with `strategy_description` field (string, up to 500 chars)
3. ✅ LLM (Azure OpenAI gpt-4o-mini) extracts 5 parameters:
   - `forecast_horizon_weeks`: Integer (4-52 weeks)
   - `season_start_date`: Date in YYYY-MM-DD format
   - `season_end_date`: Date (calculated from start + horizon)
   - `replenishment_strategy`: Enum ("none" | "weekly" | "bi-weekly")
   - `dc_holdback_percentage`: Float (0.0-1.0)
4. ✅ Response includes `extraction_reasoning` explaining how parameters were derived
5. ✅ Response includes `confidence_score` (0.0-1.0) indicating extraction quality
6. ✅ Parameters are validated against business rules (horizon 4-52, valid dates, etc.)
7. ✅ If parameters incomplete, return 400 error with list of missing parameters
8. ✅ If parameters invalid, return 422 error with validation details
9. ✅ Extraction completes in <5 seconds
10. ✅ SeasonParameters Pydantic schema defined with full validation

### Quality Requirements

11. ✅ LLM prompt includes 3+ examples for few-shot learning
12. ✅ Extraction reasoning logged to database for debugging
13. ✅ Low confidence (<0.7) triggers warning in response (but doesn't fail)
14. ✅ Azure OpenAI API errors handled gracefully (503 with retry suggestion)
15. ✅ API endpoint documented in FastAPI auto-generated docs
16. ✅ Unit tests for 5 scenarios (Zara, Standard, Luxury, Incomplete, Invalid)
17. ✅ Integration test with actual Azure OpenAI API call

---

## Prerequisites

Before implementing this story, ensure the following are ready:

**Phase 4 Integration:**
- [x] Phase 4 (Frontend/Backend Integration) complete
- [x] Backend FastAPI server running and accessible
- [x] Frontend can make API calls to backend (CORS configured)

**Azure OpenAI Configuration:**
- [ ] Azure OpenAI API keys configured in `.env` file
- [ ] `OPENAI_API_KEY` environment variable loaded
- [ ] Access to gpt-4o-mini model confirmed (test with simple API call)
- [ ] Azure OpenAI endpoint URL configured

**Database Setup:**
- [ ] Database tables for parameter extraction logs exist
- [ ] `parameter_extractions` table has columns: id, user_input, extracted_params, reasoning, confidence, timestamp

**Why This Matters:**
Without Azure OpenAI access, this story cannot be implemented or tested. The LLM is core to the parameter extraction feature - there's no fallback to manual form input in v3.3.

---

## Tasks

### Task 1: Define SeasonParameters Pydantic Schema

**Goal:** Create validated data model for extracted parameters

**Subtasks:**
- [ ] Create file: `backend/app/schemas/parameters.py`
- [ ] Define `SeasonParameters` class inheriting from `BaseModel`
- [ ] Add 5 required fields with type hints and validation:
  - `forecast_horizon_weeks: int = Field(..., ge=4, le=52)`
  - `season_start_date: date`
  - `season_end_date: date`
  - `replenishment_strategy: str = Field(..., regex="^(none|weekly|bi-weekly)$")`
  - `dc_holdback_percentage: float = Field(..., ge=0.0, le=1.0)`
- [ ] Add optional fields:
  - `extraction_reasoning: str`
  - `confidence_score: float = Field(..., ge=0.0, le=1.0)`
- [ ] Add `@validator` for `season_end_date`:
  ```python
  @validator('season_end_date')
  def validate_end_date(cls, v, values):
      start = values.get('season_start_date')
      horizon = values.get('forecast_horizon_weeks')
      if start and horizon:
          expected_end = start + timedelta(weeks=horizon)
          if v != expected_end:
              return expected_end  # Auto-calculate if missing/wrong
      return v
  ```
- [ ] Add `Config` class with example JSON schema for API docs
- [ ] Test schema validation with valid and invalid inputs

**Validation:**
```python
# Valid input
params = SeasonParameters(
    forecast_horizon_weeks=12,
    season_start_date=date(2025, 3, 1),
    season_end_date=date(2025, 5, 23),
    replenishment_strategy="none",
    dc_holdback_percentage=0.0
)
assert params.forecast_horizon_weeks == 12  # ✅

# Invalid input - should raise ValidationError
try:
    params = SeasonParameters(forecast_horizon_weeks=100, ...)  # 100 > 52
    assert False, "Should have raised ValidationError"
except ValidationError:
    pass  # ✅ Expected
```

---

### Task 2: Create LLM Prompt Template for Parameter Extraction

**Goal:** Design effective few-shot prompt for Azure OpenAI

**Subtasks:**
- [ ] Create file: `backend/app/orchestrator/prompts.py`
- [ ] Define `PARAMETER_EXTRACTION_SYSTEM_PROMPT` constant:
  ```python
  PARAMETER_EXTRACTION_SYSTEM_PROMPT = """
  You are a retail planning parameter extraction assistant.
  Extract these 5 parameters from the user's strategy description:

  1. forecast_horizon_weeks: Number of weeks to forecast (4-52)
  2. season_start_date: Start date in YYYY-MM-DD format
  3. replenishment_strategy: "none" (one-shot), "weekly", or "bi-weekly"
  4. dc_holdback_percentage: % kept at DC (0.0 = 0%, 0.45 = 45%)

  If any parameter is unclear or missing, indicate which ones in the response.
  Provide reasoning for your extraction showing which parts of the input you used.

  Return JSON format:
  {
    "forecast_horizon_weeks": <int>,
    "season_start_date": "<YYYY-MM-DD>",
    "replenishment_strategy": "<none|weekly|bi-weekly>",
    "dc_holdback_percentage": <float>,
    "extraction_reasoning": "<explain your extraction>",
    "confidence_score": <0.0-1.0>
  }
  """
  ```
- [ ] Add 3 few-shot examples to prompt:
  ```python
  PARAMETER_EXTRACTION_EXAMPLES = [
      {
          "input": "12-week season starting March 1, all inventory to stores, no replenishment",
          "output": {
              "forecast_horizon_weeks": 12,
              "season_start_date": "2025-03-01",
              "replenishment_strategy": "none",
              "dc_holdback_percentage": 0.0,
              "extraction_reasoning": "User specified '12-week' horizon, 'March 1' start, 'all inventory to stores' = 0% holdback, 'no replenishment' = none strategy",
              "confidence_score": 0.95
          }
      },
      # Add 2 more examples (weekly replenishment, bi-weekly replenishment)
  ]
  ```
- [ ] Test prompt with Azure OpenAI Playground before coding
- [ ] Validate JSON output parsing works reliably

---

### Task 3: Implement Parameter Extraction Service

**Goal:** Create service layer for LLM-based parameter extraction

**Subtasks:**
- [ ] Create file: `backend/app/orchestrator/parameter_extraction.py`
- [ ] Import Azure OpenAI client and schemas
- [ ] Implement `extract_parameters_from_text()` async function:
  ```python
  async def extract_parameters_from_text(
      strategy_description: str,
      openai_client: Any
  ) -> SeasonParameters:
      """
      Extract parameters from natural language using LLM

      Args:
          strategy_description: User's natural language input
          openai_client: Azure OpenAI client

      Returns:
          SeasonParameters object with extracted values

      Raises:
          ValueError: If extraction incomplete
          ValidationError: If extracted values invalid
      """
  ```
- [ ] Build full prompt with system message + examples + user input
- [ ] Call Azure OpenAI API with gpt-4o-mini:
  ```python
  response = await openai_client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {"role": "system", "content": PARAMETER_EXTRACTION_SYSTEM_PROMPT},
          {"role": "user", "content": example_1_input},
          {"role": "assistant", "content": json.dumps(example_1_output)},
          # ... more examples
          {"role": "user", "content": strategy_description}
      ],
      temperature=0.3,  # Low temp for consistent extraction
      max_tokens=300,
      response_format={"type": "json_object"}  # Force JSON output
  )
  ```
- [ ] Parse JSON response and validate with SeasonParameters schema
- [ ] Handle LLM API errors (timeout, rate limit, invalid JSON)
- [ ] Log extraction to database for debugging
- [ ] Return validated SeasonParameters object

---

### Task 4: Create FastAPI Endpoint

**Goal:** Expose parameter extraction via REST API

**Subtasks:**
- [ ] Create file: `backend/app/routers/orchestrator.py` (if doesn't exist)
- [ ] Define request schema:
  ```python
  class ParameterExtractionRequest(BaseModel):
      strategy_description: str = Field(
          ...,
          min_length=10,
          max_length=500,
          description="Natural language description of season strategy"
      )
  ```
- [ ] Define response schema:
  ```python
  class ParameterExtractionResponse(BaseModel):
      parameters: SeasonParameters
      warnings: List[str] = []  # e.g., ["Low confidence: 0.65"]
  ```
- [ ] Implement `POST /api/orchestrator/extract-parameters` endpoint:
  ```python
  @router.post("/extract-parameters", response_model=ParameterExtractionResponse)
  async def extract_parameters(
      request: ParameterExtractionRequest,
      openai_client: Any = Depends(get_openai_client)
  ):
      try:
          parameters = await extract_parameters_from_text(
              request.strategy_description,
              openai_client
          )

          warnings = []
          if parameters.confidence_score < 0.7:
              warnings.append(f"Low confidence: {parameters.confidence_score:.2f}")

          return ParameterExtractionResponse(
              parameters=parameters,
              warnings=warnings
          )

      except ValueError as e:
          raise HTTPException(status_code=400, detail=str(e))
      except ValidationError as e:
          raise HTTPException(status_code=422, detail=e.errors())
  ```
- [ ] Register router in `backend/app/main.py`
- [ ] Test endpoint with Postman or curl

---

### Task 5: Add Error Handling and Logging

**Goal:** Ensure robust error handling and debugging capability

**Subtasks:**
- [ ] Handle Azure OpenAI API errors:
  - Connection timeout → 503 Service Unavailable
  - Rate limit exceeded → 429 Too Many Requests
  - Invalid API key → 500 Internal Server Error (log, don't expose to user)
- [ ] Handle incomplete extraction:
  - Missing required parameters → 400 Bad Request with list of missing fields
  - Example error response:
    ```json
    {
      "detail": "Could not extract all parameters",
      "missing": ["season_start_date", "dc_holdback_percentage"],
      "extracted": {"forecast_horizon_weeks": 12, "replenishment_strategy": "none"}
    }
    ```
- [ ] Handle invalid values:
  - Out of range values → 422 Unprocessable Entity with Pydantic errors
- [ ] Add logging:
  - Log every extraction attempt (user input, extracted params, confidence)
  - Log to database table: `parameter_extractions`
  - Log errors to application logs with full context
- [ ] Add retry logic for transient Azure OpenAI errors (max 3 retries with exponential backoff)

---

### Task 6: Write Tests

**Goal:** Ensure parameter extraction works correctly for all scenarios

**Subtasks:**
- [ ] Create file: `backend/tests/test_parameter_extraction.py`
- [ ] **Test 1:** Zara-style (no replenishment)
  ```python
  async def test_zara_style_extraction():
      input_text = "12-week season starting March 1, all inventory to stores, no replenishment"
      params = await extract_parameters_from_text(input_text, mock_openai_client)

      assert params.forecast_horizon_weeks == 12
      assert params.season_start_date == date(2025, 3, 1)
      assert params.replenishment_strategy == "none"
      assert params.dc_holdback_percentage == 0.0
      assert params.confidence_score > 0.8
  ```
- [ ] **Test 2:** Standard retail (weekly replenishment)
  ```python
  async def test_standard_retail_extraction():
      input_text = "26-week season May 15, weekly shipments, 45% DC holdback"
      params = await extract_parameters_from_text(input_text, mock_openai_client)

      assert params.forecast_horizon_weeks == 26
      assert params.replenishment_strategy == "weekly"
      assert params.dc_holdback_percentage == 0.45
  ```
- [ ] **Test 3:** Incomplete input
  ```python
  async def test_incomplete_input():
      input_text = "Spring season with weekly replenishment"  # Missing horizon, dates, holdback

      with pytest.raises(ValueError, match="Could not extract all parameters"):
          await extract_parameters_from_text(input_text, mock_openai_client)
  ```
- [ ] **Test 4:** Invalid values
  ```python
  async def test_invalid_horizon():
      # Mock LLM to return horizon = 100 (exceeds 52 week limit)
      with pytest.raises(ValidationError):
          params = SeasonParameters(forecast_horizon_weeks=100, ...)
  ```
- [ ] **Test 5:** API endpoint integration test
  ```python
  async def test_extraction_endpoint(client: TestClient):
      response = client.post(
          "/api/orchestrator/extract-parameters",
          json={"strategy_description": "12-week season, no replenishment, 0% holdback"}
      )

      assert response.status_code == 200
      data = response.json()
      assert data["parameters"]["forecast_horizon_weeks"] == 12
  ```
- [ ] Run all tests: `uv run pytest backend/tests/test_parameter_extraction.py -v`

---

## Implementation Notes

**Azure OpenAI Configuration:**
```python
# backend/app/core/openai_client.py
from openai import AsyncAzureOpenAI

def get_openai_client():
    return AsyncAzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
```

**Database Logging Schema:**
```sql
CREATE TABLE parameter_extractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT NOT NULL,
    extracted_params JSON,
    extraction_reasoning TEXT,
    confidence_score REAL,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example Postman Test:**
```bash
POST http://localhost:8000/api/orchestrator/extract-parameters
Content-Type: application/json

{
  "strategy_description": "I'm planning a 12-week spring fashion season starting March 1st. Send all inventory to stores at launch with no DC holdback. I don't want ongoing replenishment - just one initial allocation."
}

# Expected 200 Response:
{
  "parameters": {
    "forecast_horizon_weeks": 12,
    "season_start_date": "2025-03-01",
    "season_end_date": "2025-05-23",
    "replenishment_strategy": "none",
    "dc_holdback_percentage": 0.0,
    "extraction_reasoning": "...",
    "confidence_score": 0.95
  },
  "warnings": []
}
```

---

## Definition of Done

- [ ] `SeasonParameters` Pydantic schema defined with full validation
- [ ] LLM prompt template created with 3+ examples
- [ ] `extract_parameters_from_text()` service function implemented
- [ ] `POST /api/orchestrator/extract-parameters` endpoint created
- [ ] Error handling for incomplete/invalid parameters
- [ ] Azure OpenAI API integration working
- [ ] Database logging for all extractions
- [ ] 5 unit tests passing (Zara, Standard, Luxury, Incomplete, Invalid)
- [ ] Integration test with actual LLM call passing
- [ ] API documentation visible in FastAPI Swagger UI
- [ ] Postman test successful
- [ ] Code reviewed and merged

---

**Created:** 2025-11-04
**Last Updated:** 2025-11-04
