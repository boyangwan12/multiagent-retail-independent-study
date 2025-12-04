# Story: Integrate Section 0 - Parameter Gathering with Backend API

**Epic:** Phase 4 - Frontend/Backend Integration
**Story ID:** PHASE4-002
**Status:** Ready for Implementation
**Estimate:** 5 hours
**Agent:** `*agent dev`
**Dependencies:** PHASE4-001 (Environment Configuration)

**Planning References:**
- PRD v3.3: Section 3.1 (Parameter-Driven Workflow Approach)
- Technical Architecture v3.3: Section 4.2 (Parameter Extraction API)
- Frontend Spec v3.3: Section 3.1 (Section 0 - Parameter Gathering Design)

---

## Story

As a user,
I want to input my season planning strategy in natural language and have the system extract structured parameters using AI,
So that I can quickly configure a forecasting workflow without filling out complex forms.

**Business Value:** This is the critical first user interaction that enables the entire parameter-driven workflow. Natural language parameter extraction is a core innovation of v3.3, making the system accessible to non-technical users. Without this working, users cannot start workflows, blocking all downstream value.

**Epic Context:** This is Story 2 of 9 in Phase 4. It connects the very first section of the frontend (Section 0: Parameter Gathering) to the backend parameter extraction API. This is the entry point for all workflows - everything else depends on parameters being extracted correctly. The backend extracts 7 parameters from natural language input: forecast_horizon_weeks, season_start_date, season_end_date, replenishment_strategy, dc_holdback_percentage, markdown_checkpoint_week, and markdown_threshold.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ User can select category from dropdown before entering parameters
2. ✅ User can enter natural language text in Section 0 textarea
3. ✅ "Extract Parameters" button calls POST /api/parameters/extract
4. ✅ Backend endpoint tested independently with Postman (returns 200 OK)
5. ✅ Backend returns SeasonParameters JSON with all 7 parameters
6. ✅ Frontend displays extracted parameters in confirmation modal
7. ✅ User can confirm parameters to start workflow
8. ✅ Confirmed parameters stored in global state (Context API)
9. ✅ Parameter banner displays after confirmation
10. ✅ "Edit Parameters" button returns user to Section 0
11. ✅ Loading state shows while extraction is in progress

### Quality Requirements

12. ✅ Extraction completes in <5 seconds for typical input
13. ✅ JSON structure matches TypeScript SeasonParameters interface exactly
14. ✅ No console errors during extraction flow
15. ✅ Error handling for API failures (network error, 500, 429, 401, etc.)
16. ✅ Test with 3-4 different natural language inputs

### Parameter Validation

17. ✅ Extracted parameters validated client-side:
  - forecast_horizon_weeks > 0 and <= 52
  - season_start_date is not in the past
  - season_end_date is after season_start_date
  - dc_holdback_percentage between 0.0 and 1.0
  - markdown_threshold between 0.0 and 1.0 (if present)
18. ✅ Invalid parameters show warning message with option to edit

### Accessibility

19. ✅ Category dropdown has proper label and keyboard navigation
20. ✅ Textarea has proper ARIA labels and aria-describedby for character count
21. ✅ Modal is accessible (focus trap, ESC to close, proper ARIA roles)
22. ✅ Character counter announced to screen readers
23. ✅ All interactive elements accessible via keyboard (Tab, Enter, ESC)

---

## Tasks

### Task 1: Test Backend Parameter Extraction Endpoint with Postman

**Goal:** Verify the endpoint works correctly BEFORE integrating with frontend.

**Subtasks:**
- [ ] Start backend server: `uv run uvicorn app.main:app --reload`
- [ ] Open Postman and create new request:
  - Method: POST
  - URL: `http://localhost:8000/api/parameters/extract`
  - Headers: `Content-Type: application/json`
  - Body (raw JSON):
    ```json
    {
      "user_input": "I'm planning a 12-week spring season starting next Monday. We'll use weekly replenishment with 45% holdback at the DC. I want to check for markdowns at week 6 if we're below 60% sell-through."
    }
    ```

- [ ] Send request and verify response (200 OK):
  ```json
  {
    "parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-11-03",
      "season_end_date": "2026-01-25",
      "replenishment_strategy": "weekly",
      "dc_holdback_percentage": 0.45,
      "markdown_checkpoint_week": 6,
      "markdown_threshold": 0.60
    },
    "confidence": "high",
    "extraction_reasoning": "Successfully extracted all 5 key parameters. Forecast horizon: 12 weeks. Replenishment: weekly with 45% DC holdback. Markdown checkpoint: Week 6 at 60% threshold."
  }
  ```

- [ ] Test with different inputs:

  **Test Case 1: Zara-style (no replenishment, no markdown)**
  ```json
  {
    "user_input": "Fast fashion launch, 8 weeks, all inventory goes to stores upfront, no replenishment, no markdowns - premium positioning"
  }
  ```
  **Expected Response:**
  ```json
  {
    "parameters": {
      "forecast_horizon_weeks": 8,
      "season_start_date": "2025-11-03",
      "season_end_date": "2025-12-29",
      "replenishment_strategy": "none",
      "dc_holdback_percentage": 0.0,
      "markdown_checkpoint_week": null,
      "markdown_threshold": null
    },
    "confidence": "high",
    "extraction_reasoning": "Fast fashion model: 8 weeks, no replenishment (100% allocation), no markdown strategy."
  }
  ```

  **Test Case 2: Traditional retail**
  ```json
  {
    "user_input": "Standard 12-week season with bi-weekly replenishment, keep 55% at DC for later, markdown check at week 4 if below 50% sell-through"
  }
  ```
  **Expected Response:**
  ```json
  {
    "parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-11-03",
      "season_end_date": "2026-01-25",
      "replenishment_strategy": "bi-weekly",
      "dc_holdback_percentage": 0.55,
      "markdown_checkpoint_week": 4,
      "markdown_threshold": 0.50
    },
    "confidence": "high",
    "extraction_reasoning": "Traditional retail model: 12 weeks, bi-weekly replenishment with 55% DC holdback, markdown checkpoint Week 4 at 50%."
  }
  ```

  **Test Case 3: Minimal input (defaults)**
  ```json
  {
    "user_input": "Just a normal spring season"
  }
  ```
  **Expected Response:**
  ```json
  {
    "parameters": {
      "forecast_horizon_weeks": 12,
      "season_start_date": "2025-11-03",
      "season_end_date": "2026-01-25",
      "replenishment_strategy": "weekly",
      "dc_holdback_percentage": 0.45,
      "markdown_checkpoint_week": 6,
      "markdown_threshold": 0.60
    },
    "confidence": "medium",
    "extraction_reasoning": "Used default values: 12-week season, weekly replenishment, 45% DC holdback, Week 6 markdown at 60% threshold."
  }
  ```

- [ ] Document any issues found
- [ ] Verify JSON structure matches TypeScript interface

**Validation:**
- All 4 test cases return 200 OK
- JSON structure is consistent across all responses
- `confidence` field present (high/medium/low)
- `extraction_reasoning` explains what was extracted

---

### Task 2: Add Category Selection to Section 0

**Goal:** Allow users to select a product category before entering parameters.

**Subtasks:**
- [ ] Test GET /api/categories endpoint with Postman:
  - Method: GET
  - URL: `http://localhost:8000/api/categories`
  - Expected Response (200 OK):
    ```json
    {
      "categories": [
        {
          "category_id": "cat_001",
          "category_name": "Women's Dresses",
          "department": "Women's Apparel"
        },
        {
          "category_id": "cat_002",
          "category_name": "Men's Shirts",
          "department": "Men's Apparel"
        },
        {
          "category_id": "cat_003",
          "category_name": "Children's Shoes",
          "department": "Children's"
        }
      ]
    }
    ```

- [ ] Create TypeScript types for categories:
  ```typescript
  // frontend/src/types/category.ts
  export interface Category {
    category_id: string;
    category_name: string;
    department: string;
  }

  export interface CategoriesResponse {
    categories: Category[];
  }
  ```

- [ ] Create CategoryService:
  ```typescript
  // frontend/src/services/category-service.ts
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type { CategoriesResponse } from '@/types/category';

  export class CategoryService {
    static async getCategories(): Promise<CategoriesResponse> {
      return ApiClient.get<CategoriesResponse>(API_ENDPOINTS.CATEGORIES);
    }
  }
  ```

- [ ] Add category dropdown to ParameterGathering component:
  ```typescript
  import { CategoryService } from '@/services/category-service';
  import type { Category } from '@/types/category';

  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await CategoryService.getCategories();
        setCategories(data.categories);
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      }
    };
    fetchCategories();
  }, []);

  // Add before textarea
  <div className="mb-4">
    <Label htmlFor="category-select">Select Category</Label>
    <Select
      value={selectedCategory}
      onValueChange={setSelectedCategory}
    >
      <SelectTrigger id="category-select" aria-label="Select product category">
        <SelectValue placeholder="Choose a category..." />
      </SelectTrigger>
      <SelectContent>
        {categories.map(cat => (
          <SelectItem key={cat.category_id} value={cat.category_id}>
            {cat.category_name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  </div>
  ```

- [ ] Add validation to prevent extraction without category:
  ```typescript
  const handleExtractParameters = async () => {
    if (!selectedCategory) {
      setState(prev => ({
        ...prev,
        error: 'Please select a category first',
      }));
      return;
    }

    if (!state.userInput.trim()) {
      setState(prev => ({
        ...prev,
        error: 'Please enter your season planning strategy',
      }));
      return;
    }

    // ... proceed with extraction
  };
  ```

- [ ] Store category in state for later use (workflow creation):
  ```typescript
  const [workflowCategory, setWorkflowCategory] = useState<Category | null>(null);

  const handleConfirmParameters = () => {
    const category = categories.find(c => c.category_id === selectedCategory);
    setWorkflowCategory(category);
    // ... rest of confirmation logic
  };
  ```

**Validation:**
- GET /api/categories returns list of categories
- Dropdown populates with category options
- Cannot extract parameters without selecting category
- Selected category stored for workflow creation

---

### Task 3: Update TypeScript Interfaces to Match Backend

**Subtasks:**
- [ ] Create or update `frontend/src/types/parameters.ts`:
  ```typescript
  // Season Parameters (extracted from user input)
  export interface SeasonParameters {
    forecast_horizon_weeks: number;
    season_start_date: string; // ISO 8601 date
    season_end_date: string; // ISO 8601 date
    replenishment_strategy: "none" | "weekly" | "bi-weekly";
    dc_holdback_percentage: number; // 0.0 to 1.0
    markdown_checkpoint_week: number | null;
    markdown_threshold: number | null; // 0.0 to 1.0
  }

  // Parameter Extraction Request
  export interface ParameterExtractionRequest {
    user_input: string;
  }

  // Parameter Extraction Response
  export interface ParameterExtractionResponse {
    parameters: SeasonParameters;
    confidence: "high" | "medium" | "low";
    extraction_reasoning: string;
  }

  // Frontend state for parameter gathering
  export interface ParameterGatheringState {
    userInput: string;
    isExtracting: boolean;
    extractedParameters: SeasonParameters | null;
    extractionReasoning: string | null;
    confidence: "high" | "medium" | "low" | null;
    isConfirmed: boolean;
    error: string | null;
  }
  ```

- [ ] Verify types match backend Pydantic models exactly
- [ ] Export types for use in components

**Validation:**
- TypeScript compiles without errors
- Types match backend response structure

---

### Task 4: Create API Service for Parameter Extraction

**Subtasks:**
- [ ] Create `frontend/src/services/parameter-service.ts`:
  ```typescript
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';
  import type {
    ParameterExtractionRequest,
    ParameterExtractionResponse,
  } from '@/types/parameters';

  export class ParameterService {
    /**
     * Extract season parameters from natural language input
     */
    static async extractParameters(
      userInput: string
    ): Promise<ParameterExtractionResponse> {
      const request: ParameterExtractionRequest = {
        user_input: userInput,
      };

      return ApiClient.post<ParameterExtractionResponse>(
        API_ENDPOINTS.PARAMETERS_EXTRACT,
        request
      );
    }
  }
  ```

- [ ] Test service in isolation:
  ```typescript
  // Test in browser console
  import { ParameterService } from '@/services/parameter-service';

  ParameterService.extractParameters(
    "12-week spring season with weekly replenishment"
  )
    .then(response => {
      console.log('Extracted:', response.parameters);
      console.log('Confidence:', response.confidence);
      console.log('Reasoning:', response.extraction_reasoning);
    })
    .catch(error => console.error('Error:', error));
  ```

**Expected Output:**
```javascript
Extracted: {
  forecast_horizon_weeks: 12,
  season_start_date: "2025-11-03",
  ...
}
Confidence: high
Reasoning: Successfully extracted all 5 key parameters...
```

**Validation:**
- Service successfully calls backend
- Response structure matches TypeScript types
- Error handling works (test with backend offline)

---

### Task 5: Update ParameterGathering Component with Real API Call

**Subtasks:**
- [ ] Locate `frontend/src/components/ParameterGathering/ParameterGathering.tsx`
- [ ] Replace mock extraction logic with real API call:

  **Before (Mock):**
  ```typescript
  const handleExtractParameters = () => {
    setIsExtracting(true);
    // Mock extraction with setTimeout
    setTimeout(() => {
      const mockParams = {
        forecast_horizon_weeks: 12,
        // ... static mock data
      };
      setExtractedParameters(mockParams);
      setIsExtracting(false);
      setShowConfirmationModal(true);
    }, 2000);
  };
  ```

  **After (Real API):**
  ```typescript
  import { ParameterService } from '@/services/parameter-service';
  import type { ParameterGatheringState } from '@/types/parameters';

  const [state, setState] = useState<ParameterGatheringState>({
    userInput: '',
    isExtracting: false,
    extractedParameters: null,
    extractionReasoning: null,
    confidence: null,
    isConfirmed: false,
    error: null,
  });

  const handleExtractParameters = async () => {
    if (!state.userInput.trim()) {
      setState(prev => ({
        ...prev,
        error: 'Please enter your season planning strategy',
      }));
      return;
    }

    setState(prev => ({ ...prev, isExtracting: true, error: null }));

    try {
      const response = await ParameterService.extractParameters(state.userInput);

      setState(prev => ({
        ...prev,
        isExtracting: false,
        extractedParameters: response.parameters,
        extractionReasoning: response.extraction_reasoning,
        confidence: response.confidence,
      }));

      setShowConfirmationModal(true);
    } catch (error) {
      console.error('Parameter extraction failed:', error);
      setState(prev => ({
        ...prev,
        isExtracting: false,
        error: error instanceof Error ? error.message : 'Failed to extract parameters',
      }));
    }
  };
  ```

- [ ] Update textarea onChange handler:
  ```typescript
  const handleUserInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setState(prev => ({ ...prev, userInput: e.target.value, error: null }));
  };
  ```

- [ ] Add loading state to "Extract Parameters" button:
  ```typescript
  <Button
    onClick={handleExtractParameters}
    disabled={state.isExtracting || !state.userInput.trim()}
  >
    {state.isExtracting ? (
      <>
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        Extracting...
      </>
    ) : (
      <>
        <Sparkles className="mr-2 h-4 w-4" />
        Extract Parameters
      </>
    )}
  </Button>
  ```

- [ ] Display error message if extraction fails:
  ```typescript
  {state.error && (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{state.error}</AlertDescription>
    </Alert>
  )}
  ```

**Validation:**
- Button shows loading state while extracting
- Error message displays if API fails
- Button is disabled when input is empty

---

### Task 6: Update ParameterConfirmationModal with Backend Data

**Subtasks:**
- [ ] Locate `frontend/src/components/ParameterGathering/ParameterConfirmationModal.tsx`
- [ ] Pass extracted data as props:
  ```typescript
  interface ParameterConfirmationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    parameters: SeasonParameters | null;
    extractionReasoning: string | null;
    confidence: "high" | "medium" | "low" | null;
  }
  ```

- [ ] Update modal to display backend data:
  ```typescript
  <DialogContent className="max-w-2xl">
    <DialogHeader>
      <DialogTitle>Confirm Extracted Parameters</DialogTitle>
      <DialogDescription>
        Review the parameters extracted from your input.
        {confidence && (
          <Badge variant={confidence === 'high' ? 'default' : 'secondary'}>
            {confidence} confidence
          </Badge>
        )}
      </DialogDescription>
    </DialogHeader>

    <div className="space-y-4">
      {/* Extraction Reasoning */}
      {extractionReasoning && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>{extractionReasoning}</AlertDescription>
        </Alert>
      )}

      {/* Parameter Cards */}
      <div className="grid grid-cols-2 gap-4">
        <ParameterCard
          label="Forecast Horizon"
          value={`${parameters?.forecast_horizon_weeks} weeks`}
          icon={<Calendar />}
        />
        <ParameterCard
          label="Season Dates"
          value={`${formatDate(parameters?.season_start_date)} - ${formatDate(parameters?.season_end_date)}`}
          icon={<Calendar />}
        />
        <ParameterCard
          label="Replenishment Strategy"
          value={parameters?.replenishment_strategy || 'none'}
          icon={<Truck />}
        />
        <ParameterCard
          label="DC Holdback"
          value={`${(parameters?.dc_holdback_percentage || 0) * 100}%`}
          icon={<Package />}
        />
        <ParameterCard
          label="Markdown Checkpoint"
          value={
            parameters?.markdown_checkpoint_week
              ? `Week ${parameters.markdown_checkpoint_week} @ ${(parameters.markdown_threshold || 0) * 100}%`
              : 'No markdown'
          }
          icon={<TrendingDown />}
        />
      </div>
    </div>

    <DialogFooter>
      <Button variant="outline" onClick={onClose}>
        Cancel
      </Button>
      <Button onClick={onConfirm}>
        Confirm & Start Workflow
      </Button>
    </DialogFooter>
  </DialogContent>
  ```

- [ ] Add date formatting helper:
  ```typescript
  function formatDate(dateString: string | undefined): string {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }
  ```

**Validation:**
- Modal displays all 5 parameters correctly
- Confidence badge shows (high/medium/low)
- Extraction reasoning displays
- Dates format correctly
- Replenishment strategy displays correctly
- Markdown displays "No markdown" if null

---

### Task 7: Implement Parameter Confirmation Flow

**Subtasks:**
- [ ] Update `handleConfirm` in ParameterGathering component:
  ```typescript
  const handleConfirmParameters = () => {
    setState(prev => ({ ...prev, isConfirmed: true }));
    setShowConfirmationModal(false);

    // Store parameters in global state (Context or Zustand)
    // This will be used by PHASE4-003 (workflow initiation)
    console.log('Parameters confirmed:', state.extractedParameters);

    // Scroll to Section 1 (Agent Cards)
    document.getElementById('section-1-agent-cards')?.scrollIntoView({
      behavior: 'smooth',
    });
  };
  ```

- [ ] Update ConfirmedBanner component to display confirmed parameters:
  ```typescript
  <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
    <CardContent className="py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <CheckCircle2 className="h-5 w-5 text-green-600" />
          <div>
            <p className="text-sm font-medium text-gray-900">
              Parameters Confirmed
            </p>
            <p className="text-xs text-gray-600">
              {parameters.forecast_horizon_weeks}-week season •{' '}
              {parameters.replenishment_strategy} replenishment •{' '}
              {parameters.dc_holdback_percentage * 100}% DC holdback
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={onEdit}>
          <Edit2 className="mr-2 h-4 w-4" />
          Edit Parameters
        </Button>
      </div>
    </CardContent>
  </Card>
  ```

- [ ] Implement "Edit Parameters" flow:
  ```typescript
  const handleEditParameters = () => {
    setState(prev => ({
      ...prev,
      isConfirmed: false,
      extractedParameters: null,
      extractionReasoning: null,
      confidence: null,
    }));

    // Scroll back to Section 0
    document.getElementById('section-0-parameter-gathering')?.scrollIntoView({
      behavior: 'smooth',
    });
  };
  ```

**Validation:**
- Confirming parameters updates state
- Banner displays confirmed parameters
- "Edit Parameters" button returns to Section 0
- User input remains in textarea after editing
- Parameters clear when editing

---

### Task 8: Add Client-Side Parameter Validation

**Goal:** Validate extracted parameters to catch unrealistic or invalid values before workflow creation.

**Subtasks:**
- [ ] Create validation utility function:
  ```typescript
  // frontend/src/utils/parameter-validation.ts
  import type { SeasonParameters } from '@/types/parameters';

  export interface ValidationError {
    field: string;
    message: string;
  }

  export function validateParameters(params: SeasonParameters): ValidationError[] {
    const errors: ValidationError[] = [];

    // Validate forecast_horizon_weeks
    if (params.forecast_horizon_weeks <= 0 || params.forecast_horizon_weeks > 52) {
      errors.push({
        field: 'forecast_horizon_weeks',
        message: 'Forecast horizon must be between 1 and 52 weeks',
      });
    }

    // Validate dates
    const startDate = new Date(params.season_start_date);
    const endDate = new Date(params.season_end_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (startDate < today) {
      errors.push({
        field: 'season_start_date',
        message: 'Season start date cannot be in the past',
      });
    }

    if (endDate <= startDate) {
      errors.push({
        field: 'season_end_date',
        message: 'Season end date must be after start date',
      });
    }

    // Validate dc_holdback_percentage
    if (params.dc_holdback_percentage < 0 || params.dc_holdback_percentage > 1.0) {
      errors.push({
        field: 'dc_holdback_percentage',
        message: 'DC holdback percentage must be between 0% and 100%',
      });
    }

    // Validate markdown_threshold if present
    if (params.markdown_threshold !== null) {
      if (params.markdown_threshold < 0 || params.markdown_threshold > 1.0) {
        errors.push({
          field: 'markdown_threshold',
          message: 'Markdown threshold must be between 0% and 100%',
        });
      }
    }

    // Validate markdown_checkpoint_week if present
    if (params.markdown_checkpoint_week !== null) {
      if (params.markdown_checkpoint_week < 1 || params.markdown_checkpoint_week > params.forecast_horizon_weeks) {
        errors.push({
          field: 'markdown_checkpoint_week',
          message: `Markdown checkpoint must be between week 1 and ${params.forecast_horizon_weeks}`,
        });
      }
    }

    return errors;
  }
  ```

- [ ] Integrate validation in ParameterConfirmationModal:
  ```typescript
  import { validateParameters } from '@/utils/parameter-validation';

  const validationErrors = validateParameters(parameters);

  // Display warnings if validation errors exist
  {validationErrors.length > 0 && (
    <Alert variant="warning">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>Parameter Validation Warnings</AlertTitle>
      <AlertDescription>
        <ul className="list-disc list-inside">
          {validationErrors.map((error, idx) => (
            <li key={idx}>{error.message}</li>
          ))}
        </ul>
        <p className="mt-2 text-sm">
          You can still proceed, but please review these parameters carefully.
        </p>
      </AlertDescription>
    </Alert>
  )}
  ```

**Validation:**
- Invalid forecast horizons (0, -5, 100) show warnings
- Past dates show warnings
- Invalid percentages (>100%, negative) show warnings
- Warnings appear in modal but don't block confirmation

---

### Task 9: Add Error Handling and Edge Cases

**Subtasks:**
- [ ] Handle network and API errors:
  ```typescript
  try {
    const response = await ParameterService.extractParameters(state.userInput);
    // ... success
  } catch (error) {
    let errorMessage = 'Failed to extract parameters';

    if (error.status === 0) {
      errorMessage = 'Cannot connect to backend. Is the server running?';
    } else if (error.status === 401) {
      errorMessage = 'API authentication error. Please check your OpenAI API key configuration.';
    } else if (error.status === 429) {
      errorMessage = 'Rate limit exceeded. Please wait a moment and try again.';
    } else if (error.status === 500) {
      errorMessage = 'Server error. Please try again or simplify your input.';
    } else if (error.status === 422) {
      errorMessage = 'Invalid input format. Please check your text and try again.';
    } else if (error.message) {
      errorMessage = error.message;
    }

    setState(prev => ({
      ...prev,
      isExtracting: false,
      error: errorMessage,
    }));
  }
  ```

- [ ] Handle empty input:
  ```typescript
  const handleExtractParameters = async () => {
    const trimmedInput = state.userInput.trim();

    if (!trimmedInput) {
      setState(prev => ({
        ...prev,
        error: 'Please enter your season planning strategy',
      }));
      return;
    }

    if (trimmedInput.length < 10) {
      setState(prev => ({
        ...prev,
        error: 'Please provide more details about your season plan',
      }));
      return;
    }

    // ... proceed with extraction
  };
  ```

- [ ] Handle character limit (500 chars):
  ```typescript
  <Textarea
    value={state.userInput}
    onChange={handleUserInputChange}
    maxLength={500}
    placeholder="Example: I'm planning a 12-week spring season..."
  />
  <p className="text-xs text-gray-500 text-right">
    {state.userInput.length}/500 characters
  </p>
  ```

**Validation:**
- Network error shows helpful message
- Empty input shows validation error
- Character limit enforced
- Error messages are user-friendly

---

### Task 10: Set Up Global State Management for Parameters

**Goal:** Make extracted and confirmed parameters accessible across all sections using React Context API.

**Subtasks:**
- [ ] Create ParameterContext:
  ```typescript
  // frontend/src/contexts/ParameterContext.tsx
  import React, { createContext, useContext, useState, ReactNode } from 'react';
  import type { SeasonParameters } from '@/types/parameters';
  import type { Category } from '@/types/category';

  interface ParameterContextState {
    parameters: SeasonParameters | null;
    category: Category | null;
    isConfirmed: boolean;
    setParameters: (params: SeasonParameters) => void;
    setCategory: (cat: Category) => void;
    confirmParameters: () => void;
    resetParameters: () => void;
  }

  const ParameterContext = createContext<ParameterContextState | undefined>(undefined);

  export function ParameterProvider({ children }: { children: ReactNode }) {
    const [parameters, setParametersState] = useState<SeasonParameters | null>(null);
    const [category, setCategoryState] = useState<Category | null>(null);
    const [isConfirmed, setIsConfirmed] = useState(false);

    const setParameters = (params: SeasonParameters) => {
      setParametersState(params);
    };

    const setCategory = (cat: Category) => {
      setCategoryState(cat);
    };

    const confirmParameters = () => {
      setIsConfirmed(true);
    };

    const resetParameters = () => {
      setParametersState(null);
      setCategoryState(null);
      setIsConfirmed(false);
    };

    return (
      <ParameterContext.Provider
        value={{
          parameters,
          category,
          isConfirmed,
          setParameters,
          setCategory,
          confirmParameters,
          resetParameters,
        }}
      >
        {children}
      </ParameterContext.Provider>
    );
  }

  export function useParameters() {
    const context = useContext(ParameterContext);
    if (!context) {
      throw new Error('useParameters must be used within a ParameterProvider');
    }
    return context;
  }
  ```

- [ ] Wrap App with ParameterProvider:
  ```typescript
  // frontend/src/App.tsx or main.tsx
  import { ParameterProvider } from '@/contexts/ParameterContext';

  function App() {
    return (
      <ParameterProvider>
        {/* App content */}
      </ParameterProvider>
    );
  }
  ```

- [ ] Update ParameterGathering component to use context:
  ```typescript
  import { useParameters } from '@/contexts/ParameterContext';

  const { setParameters, setCategory, confirmParameters } = useParameters();

  const handleConfirmParameters = () => {
    // Store in context
    setParameters(state.extractedParameters!);
    setCategory(selectedCategoryObject);
    confirmParameters();

    // Close modal
    setShowConfirmationModal(false);

    // Scroll to next section
    document.getElementById('section-1-agent-cards')?.scrollIntoView({
      behavior: 'smooth',
    });
  };
  ```

- [ ] Test context from another component:
  ```typescript
  // Test in any component
  import { useParameters } from '@/contexts/ParameterContext';

  function SomeOtherComponent() {
    const { parameters, category, isConfirmed } = useParameters();

    if (!isConfirmed) {
      return <p>Please configure parameters first</p>;
    }

    return (
      <div>
        <p>Category: {category?.category_name}</p>
        <p>Forecast horizon: {parameters?.forecast_horizon_weeks} weeks</p>
      </div>
    );
  }
  ```

**Validation:**
- Context provides parameters to all components
- Parameters persist across component re-renders
- useParameters hook works from any component
- resetParameters clears all state
- Later stories (PHASE4-003) can access parameters via useParameters()

---

### Task 11: Add Accessibility Support

**Goal:** Ensure Section 0 is fully accessible via keyboard and screen readers.

**Subtasks:**
- [ ] Add ARIA labels to category dropdown:
  ```typescript
  <Label htmlFor="category-select">
    Select Category <span aria-label="required">*</span>
  </Label>
  <Select
    value={selectedCategory}
    onValueChange={setSelectedCategory}
    aria-required="true"
    aria-label="Select product category for forecasting"
  >
    {/* ... */}
  </Select>
  ```

- [ ] Add ARIA labels to textarea:
  ```typescript
  <Label htmlFor="parameter-input">
    Describe Your Season Plan <span aria-label="required">*</span>
  </Label>
  <Textarea
    id="parameter-input"
    value={state.userInput}
    onChange={handleUserInputChange}
    maxLength={500}
    aria-required="true"
    aria-describedby="char-count error-message"
    aria-label="Enter your season planning strategy in natural language"
  />
  <p id="char-count" className="text-xs text-gray-500 text-right" aria-live="polite">
    {state.userInput.length}/500 characters
  </p>
  {state.error && (
    <p id="error-message" role="alert" className="text-sm text-red-600">
      {state.error}
    </p>
  )}
  ```

- [ ] Add focus trap to modal:
  ```typescript
  import { Dialog, DialogContent } from '@/components/ui/dialog';

  <Dialog open={showConfirmationModal} onOpenChange={setShowConfirmationModal}>
    <DialogContent
      onEscapeKeyDown={() => setShowConfirmationModal(false)}
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
    >
      <DialogHeader>
        <DialogTitle id="modal-title">Confirm Extracted Parameters</DialogTitle>
        <DialogDescription id="modal-description">
          Review the parameters extracted from your input.
        </DialogDescription>
      </DialogHeader>
      {/* ... modal content */}
    </DialogContent>
  </Dialog>
  ```

- [ ] Test keyboard navigation:
  ```
  - [ ] Tab through all interactive elements in correct order
  - [ ] Category dropdown opens with Enter/Space
  - [ ] Textarea receives focus and accepts input
  - [ ] Extract button activates with Enter/Space
  - [ ] Modal opens and focus moves to first element
  - [ ] ESC closes modal and returns focus to trigger
  - [ ] Tab within modal stays trapped until closed
  ```

- [ ] Test screen reader announcements:
  ```
  - [ ] Category label announced
  - [ ] Textarea label and description announced
  - [ ] Character count updates announced (aria-live)
  - [ ] Error messages announced immediately (role="alert")
  - [ ] Loading state announced
  - [ ] Modal title and description announced on open
  ```

**Validation:**
- All interactive elements accessible via keyboard
- Screen reader announces all labels and state changes
- Focus management works correctly in modal
- Error messages announced immediately

---

## Testing Requirements

### Unit Tests
```typescript
describe('ParameterService', () => {
  it('should extract parameters from natural language', async () => {
    const response = await ParameterService.extractParameters(
      '12-week season with weekly replenishment'
    );

    expect(response.parameters.forecast_horizon_weeks).toBe(12);
    expect(response.parameters.replenishment_strategy).toBe('weekly');
    expect(response.confidence).toBeDefined();
  });

  it('should handle extraction errors', async () => {
    // Mock backend offline
    await expect(
      ParameterService.extractParameters('')
    ).rejects.toThrow();
  });
});
```

### Integration Tests
```typescript
describe('ParameterGathering Component', () => {
  it('should display extraction results in modal', async () => {
    render(<ParameterGathering />);

    const textarea = screen.getByPlaceholderText(/season planning/i);
    const extractButton = screen.getByText(/extract parameters/i);

    fireEvent.change(textarea, {
      target: { value: '12-week spring season' },
    });
    fireEvent.click(extractButton);

    await waitFor(() => {
      expect(screen.getByText(/confirm extracted parameters/i)).toBeInTheDocument();
    });
  });

  it('should display error on API failure', async () => {
    // Mock API failure
    jest.spyOn(ParameterService, 'extractParameters').mockRejectedValue(
      new Error('API Error')
    );

    render(<ParameterGathering />);

    const textarea = screen.getByPlaceholderText(/season planning/i);
    const extractButton = screen.getByText(/extract parameters/i);

    fireEvent.change(textarea, { target: { value: 'test input' } });
    fireEvent.click(extractButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to extract parameters/i)).toBeInTheDocument();
    });
  });
});
```

### Manual Testing Checklist
- [ ] Enter natural language → Click "Extract Parameters"
- [ ] Verify loading state shows (button disabled, spinner visible)
- [ ] Verify modal appears with extracted parameters
- [ ] Verify all 5 parameters display correctly
- [ ] Verify confidence badge shows
- [ ] Verify extraction reasoning shows
- [ ] Click "Confirm & Start Workflow"
- [ ] Verify banner displays with confirmed parameters
- [ ] Click "Edit Parameters"
- [ ] Verify returns to Section 0 with original input
- [ ] Test with empty input → Verify error message
- [ ] Test with backend offline → Verify network error message
- [ ] Test with 4 different natural language inputs
- [ ] Verify character counter works (500 max)

---

## Implementation Notes

### Backend Parameter Extraction Expected Behavior

The backend uses OpenAI GPT-4o-mini to extract parameters. Expected behavior:

1. **High Confidence:** All 5 parameters explicitly mentioned
2. **Medium Confidence:** Some parameters inferred from context
3. **Low Confidence:** Most parameters use defaults

**Examples:**

- **High:** "12-week spring season, weekly replenishment, 45% DC holdback, Week 6 markdown at 60%"
- **Medium:** "Standard spring season with weekly replenishment"
- **Low:** "Just a normal season"

### UI/UX Considerations

1. **Loading State:**
   - Show spinner immediately on button click
   - Disable button during extraction
   - Show "Extracting..." text

2. **Error Messages:**
   - Network error: "Cannot connect to backend. Is the server running?"
   - API error: "Server error. Please try again or simplify your input."
   - Validation error: "Please enter your season planning strategy"

3. **Confidence Indicator:**
   - High → Green badge
   - Medium → Yellow badge
   - Low → Gray badge

4. **Parameter Display:**
   - Use icons for visual clarity
   - Format percentages: 0.45 → "45%"
   - Format dates: "2025-11-03" → "Nov 3, 2025"
   - Handle nulls: markdown_checkpoint_week = null → "No markdown"

---

## Dependencies

**Requires:**
- PHASE4-001 complete (environment configured, CORS working)
- Backend running on http://localhost:8000
- POST /api/parameters/extract endpoint functional

**Enables:**
- PHASE4-003 (Section 1 - Workflow initiation needs parameters)

---

## Definition of Done

**Backend Integration:**
- [ ] POST /api/parameters/extract tested with Postman (4 test cases)
- [ ] GET /api/categories tested with Postman
- [ ] All 7 parameters extracted correctly
- [ ] TypeScript interfaces match backend response

**Category Selection:**
- [ ] Category dropdown displays available categories
- [ ] Category selection required before parameter extraction
- [ ] Selected category stored and passed to workflow creation

**API Integration:**
- [ ] ParameterService created and tested
- [ ] CategoryService created and tested
- [ ] ParameterGathering component updated with real API call
- [ ] ParameterConfirmationModal displays backend data

**Parameter Validation:**
- [ ] Client-side parameter validation implemented
- [ ] Validation warnings display in modal
- [ ] Invalid parameters (dates, percentages, weeks) caught
- [ ] Validation doesn't block confirmation (warnings only)

**State Management:**
- [ ] ParameterContext created with React Context API
- [ ] useParameters hook provides access to parameters
- [ ] Parameters persist across components
- [ ] State management tested and working

**Error Handling:**
- [ ] Error handling implemented (network, 401, 429, 500, 422)
- [ ] User-friendly error messages for all scenarios
- [ ] Empty input validation
- [ ] Character limit enforced (500 chars)

**Accessibility:**
- [ ] Category dropdown has ARIA labels
- [ ] Textarea has ARIA labels and aria-describedby
- [ ] Modal has focus trap and ESC to close
- [ ] Character counter announced to screen readers
- [ ] All interactive elements accessible via keyboard
- [ ] Screen reader testing passed

**Quality:**
- [ ] Parameter confirmation flow works end-to-end
- [ ] Loading states work correctly
- [ ] All manual tests passing
- [ ] No console errors
- [ ] Integration tests passing

---

## Time Tracking

- **Estimated:** 5 hours
- **Actual:** ___ hours
- **Variance:** ___ hours

**Breakdown:**
- Task 1 (Postman testing): ___ min
- Task 2 (Category selection): ___ min
- Task 3 (TypeScript types): ___ min
- Task 4 (API service): ___ min
- Task 5 (Component update): ___ min
- Task 6 (Modal update): ___ min
- Task 7 (Confirmation flow): ___ min
- Task 8 (Parameter validation): ___ min
- Task 9 (Error handling): ___ min
- Task 10 (State management): ___ min
- Task 11 (Accessibility): ___ min
- Testing: ___ min
- Documentation: ___ min

---

## Related Stories

- **Depends On:** PHASE4-001 (Environment Configuration)
- **Blocks:** PHASE4-003 (Section 1 - needs parameters to start workflow)
- **Related:** PHASE4-009 (Documentation)

---

**Status:** ⏳ Ready for Implementation
**Assigned To:** Dev Team
**Priority:** P0 (Critical - First user interaction)
**Created:** 2025-10-29
**Updated:** 2025-10-29
