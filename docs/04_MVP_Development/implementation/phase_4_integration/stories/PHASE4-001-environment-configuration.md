# Story: Configure Environment Variables & CORS for Frontend/Backend Integration

**Epic:** Phase 4 - Frontend/Backend Integration
**Story ID:** PHASE4-001
**Status:** Ready for Implementation
**Estimate:** 3 hours
**Agent:** `*agent dev`
**Dependencies:** None (foundational story)

**Planning References:**
- Technical Architecture v3.3: Section 4 (API Architecture & Endpoints)
- Frontend Spec v3.3: Section 2 (Environment Configuration)
- PRD v3.3: Section 5 (Technical Requirements)

---

## Story

As a full-stack developer,
I want to configure environment variables for both frontend and backend, and set up CORS properly,
So that the React frontend can successfully communicate with the FastAPI backend without errors.

**Business Value:** This is the foundational step that enables ALL subsequent integration work. Without proper environment configuration and CORS setup, the frontend cannot make API calls to the backend, blocking all Phase 4 progress. This story eliminates the #1 blocker for frontend/backend integration.

**Epic Context:** This is Story 1 of 9 in Phase 4 (Frontend/Backend Integration). It's the prerequisite for all other stories. The professor specifically requested that frontend and backend be connected BEFORE building AI agents, making this configuration story the critical first step.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ Frontend `.env` file created with `VITE_API_URL` pointing to backend
2. ✅ Backend `.env` file created with `OPENAI_API_KEY` and other required variables
3. ✅ CORS middleware configured in FastAPI to allow frontend origin
4. ✅ Frontend can reach backend health endpoint (`GET /api/health`)
5. ✅ OPTIONS preflight requests return 200 OK
6. ✅ No CORS errors in browser console

### Quality Requirements

7. ✅ `.env` files are in `.gitignore` (not committed to repo)
8. ✅ `.env.example` files created for both frontend and backend
9. ✅ README.md updated with environment setup instructions
10. ✅ All environment variables load correctly on server startup

### WebSocket & Advanced Requirements

11. ✅ WebSocket CORS configuration included (for PHASE4-003)
12. ✅ WebSocket connection test passes (basic connectivity)
13. ✅ All required environment variables documented in checklist
14. ✅ Environment variable validation on startup (missing vars cause clear errors)

---

## Tasks

### Task 1: Create Frontend Environment Configuration

**Subtasks:**
- [ ] Create `frontend/.env` file with the following variables:
  ```bash
  # Backend API Configuration
  VITE_API_URL=http://localhost:8000
  VITE_WS_URL=ws://localhost:8000

  # Development Settings
  VITE_ENV=development
  VITE_DEBUG=true
  ```

- [ ] Create `frontend/.env.example` with the same structure (placeholder values):
  ```bash
  # Backend API Configuration
  VITE_API_URL=http://localhost:8000
  VITE_WS_URL=ws://localhost:8000

  # Development Settings
  VITE_ENV=development
  VITE_DEBUG=true
  ```

- [ ] Verify `frontend/.gitignore` includes `.env`:
  ```gitignore
  # Environment variables
  .env
  .env.local
  .env.*.local
  ```

- [ ] Test that Vite loads environment variables:
  ```typescript
  // Test in frontend/src/App.tsx
  console.log('API URL:', import.meta.env.VITE_API_URL)
  console.log('WS URL:', import.meta.env.VITE_WS_URL)
  ```

**Expected Output:**
```
API URL: http://localhost:8000
WS URL: ws://localhost:8000
```

**Validation:**
- Run `npm run dev` in frontend/
- Check browser console for environment variable values
- Verify no errors

---

### Task 2: Create Backend Environment Configuration

**Subtasks:**
- [ ] Create `backend/.env` file with the following variables:
  ```bash
  # OpenAI Configuration
  OPENAI_API_KEY=sk-your_actual_api_key_here
  OPENAI_MODEL=gpt-4o-mini
  OPENAI_ORG_ID=org-your_org_id_here  # Optional

  # Database Configuration
  DATABASE_URL=sqlite:///./fashion_forecast.db

  # Server Configuration
  HOST=0.0.0.0
  PORT=8000
  DEBUG=true
  RELOAD=true

  # CORS Configuration
  CORS_ORIGINS=http://localhost:5173,http://localhost:3000
  CORS_ALLOW_CREDENTIALS=true
  CORS_ALLOW_METHODS=*
  CORS_ALLOW_HEADERS=*

  # Logging
  LOG_LEVEL=INFO
  LOG_FILE=logs/app.log
  ```

- [ ] Create `backend/.env.example` with placeholders:
  ```bash
  # OpenAI Configuration
  OPENAI_API_KEY=sk-your_api_key_here
  OPENAI_MODEL=gpt-4o-mini
  OPENAI_ORG_ID=org-your_org_id_here

  # Database Configuration
  DATABASE_URL=sqlite:///./fashion_forecast.db

  # Server Configuration
  HOST=0.0.0.0
  PORT=8000
  DEBUG=true
  RELOAD=true

  # CORS Configuration
  CORS_ORIGINS=http://localhost:5173,http://localhost:3000
  CORS_ALLOW_CREDENTIALS=true
  CORS_ALLOW_METHODS=*
  CORS_ALLOW_HEADERS=*

  # Logging
  LOG_LEVEL=INFO
  LOG_FILE=logs/app.log
  ```

- [ ] Verify `backend/.gitignore` includes `.env`:
  ```gitignore
  # Environment variables
  .env
  .env.*
  !.env.example
  ```

- [ ] Update `backend/app/core/config.py` to load environment variables:
  ```python
  from pydantic_settings import BaseSettings
  from typing import List

  class Settings(BaseSettings):
      # OpenAI
      OPENAI_API_KEY: str
      OPENAI_MODEL: str = "gpt-4o-mini"
      OPENAI_ORG_ID: str | None = None

      # Database
      DATABASE_URL: str = "sqlite:///./fashion_forecast.db"

      # Server
      HOST: str = "0.0.0.0"
      PORT: int = 8000
      DEBUG: bool = True
      RELOAD: bool = True

      # CORS
      CORS_ORIGINS: str = "http://localhost:5173"
      CORS_ALLOW_CREDENTIALS: bool = True
      CORS_ALLOW_METHODS: str = "*"
      CORS_ALLOW_HEADERS: str = "*"

      # Logging
      LOG_LEVEL: str = "INFO"
      LOG_FILE: str = "logs/app.log"

      @property
      def cors_origins_list(self) -> List[str]:
          return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

      class Config:
          env_file = ".env"
          case_sensitive = True

  settings = Settings()
  ```

- [ ] Test that backend loads environment variables:
  ```python
  # Test in backend/app/main.py
  from app.core.config import settings
  print(f"OpenAI Model: {settings.OPENAI_MODEL}")
  print(f"CORS Origins: {settings.cors_origins_list}")
  ```

**Expected Output:**
```
OpenAI Model: gpt-4o-mini
CORS Origins: ['http://localhost:5173', 'http://localhost:3000']
```

**Validation:**
- Run `uv run uvicorn app.main:app --reload` in backend/
- Check console output for environment variable values
- Verify no errors

---

### Task 3: Configure CORS Middleware in FastAPI

**Subtasks:**
- [ ] Update `backend/app/main.py` to add CORS middleware:
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from app.core.config import settings

  app = FastAPI(
      title="Fashion Forecast API",
      version="1.0.0",
      description="Multi-Agent Retail Demand Forecasting System"
  )

  # CORS Configuration (includes WebSocket support)
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.cors_origins_list,
      allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
      allow_methods=settings.CORS_ALLOW_METHODS.split(",") if settings.CORS_ALLOW_METHODS != "*" else ["*"],
      allow_headers=settings.CORS_ALLOW_HEADERS.split(",") if settings.CORS_ALLOW_HEADERS != "*" else ["*"],
      expose_headers=["*"],  # Required for WebSocket upgrade headers
  )

  # Note: WebSocket connections also respect CORS origins.
  # The allow_origins list applies to both HTTP and WebSocket connections.

  @app.get("/api/health")
  async def health_check():
      return {
          "status": "healthy",
          "environment": "development" if settings.DEBUG else "production",
          "api_version": "1.0.0"
      }
  ```

- [ ] Test CORS with browser DevTools:
  1. Start backend: `uv run uvicorn app.main:app --reload`
  2. Open browser to `http://localhost:5173`
  3. Open DevTools → Console
  4. Run this JavaScript:
     ```javascript
     fetch('http://localhost:8000/api/health')
       .then(res => res.json())
       .then(data => console.log('Health check:', data))
       .catch(err => console.error('CORS error:', err))
     ```

**Expected Output (Browser Console):**
```javascript
Health check: { status: "healthy", environment: "development", api_version: "1.0.0" }
```

**If you see CORS error:**
```
Access to fetch at 'http://localhost:8000/api/health' from origin 'http://localhost:5173'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```
→ This means CORS is NOT configured correctly. Double-check `settings.cors_origins_list`.

- [ ] Test OPTIONS preflight request:
  ```bash
  curl -X OPTIONS http://localhost:8000/api/health \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: GET" \
    -v
  ```

**Expected Response Headers:**
```
< HTTP/1.1 200 OK
< access-control-allow-origin: http://localhost:5173
< access-control-allow-credentials: true
< access-control-allow-methods: *
< access-control-allow-headers: *
```

**Validation:**
- No CORS errors in browser console
- OPTIONS preflight returns 200 OK
- `access-control-allow-origin` header present in response

---

### Task 4: Environment Variable Validation Checklist

**Goal:** Ensure all required environment variables are set and valid before proceeding with integration.

**Subtasks:**

- [ ] Create comprehensive environment variable checklist:

**Backend Environment Variables:**
```bash
# Required (will cause startup failure if missing)
✅ OPENAI_API_KEY - OpenAI API key (starts with 'sk-')
✅ DATABASE_URL - Database connection string

# Recommended (has defaults but should be configured)
✅ CORS_ORIGINS - Frontend URL(s) for CORS
✅ PORT - Backend server port (default: 8000)
✅ HOST - Backend server host (default: 0.0.0.0)

# Optional (system will use defaults)
✅ OPENAI_MODEL - OpenAI model name (default: gpt-4o-mini)
✅ OPENAI_ORG_ID - OpenAI organization ID
✅ LOG_LEVEL - Logging level (default: INFO)
✅ LOG_FILE - Log file path (default: logs/app.log)
✅ DEBUG - Debug mode (default: true)
✅ RELOAD - Auto-reload on code changes (default: true)
```

**Frontend Environment Variables:**
```bash
# Required
✅ VITE_API_URL - Backend API base URL (default: http://localhost:8000)
✅ VITE_WS_URL - Backend WebSocket URL (default: ws://localhost:8000)

# Optional
✅ VITE_ENV - Environment name (default: development)
✅ VITE_DEBUG - Debug mode (default: true)
```

- [ ] Add startup validation in `backend/app/main.py`:
  ```python
  from app.core.config import settings
  import sys

  def validate_environment():
      """Validate required environment variables on startup"""
      errors = []

      # Required variables
      if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-your_api_key_here":
          errors.append("OPENAI_API_KEY is not set or using placeholder value")

      if not settings.CORS_ORIGINS or settings.CORS_ORIGINS == "":
          errors.append("CORS_ORIGINS is not set")

      # Validate format
      if not settings.OPENAI_API_KEY.startswith("sk-"):
          errors.append("OPENAI_API_KEY must start with 'sk-'")

      if errors:
          print("\n❌ ENVIRONMENT CONFIGURATION ERRORS:")
          for error in errors:
              print(f"  - {error}")
          print("\n📝 Please check your .env file and restart the server.\n")
          sys.exit(1)
      else:
          print("✅ Environment configuration validated successfully")

  @app.on_event("startup")
  async def startup_event():
      validate_environment()
      print(f"🚀 Server starting on {settings.HOST}:{settings.PORT}")
      print(f"📡 CORS enabled for: {', '.join(settings.cors_origins_list)}")
  ```

- [ ] Test validation by starting backend without OPENAI_API_KEY:
  ```bash
  # Remove OPENAI_API_KEY from .env temporarily
  uv run uvicorn app.main:app --reload
  ```

**Expected Output:**
```
❌ ENVIRONMENT CONFIGURATION ERRORS:
  - OPENAI_API_KEY is not set or using placeholder value

📝 Please check your .env file and restart the server.
```

- [ ] Test validation with correct environment variables:
  ```bash
  # Restore OPENAI_API_KEY to .env
  uv run uvicorn app.main:app --reload
  ```

**Expected Output:**
```
✅ Environment configuration validated successfully
🚀 Server starting on 0.0.0.0:8000
📡 CORS enabled for: http://localhost:5173, http://localhost:3000
```

**Validation:**
- Missing required variables cause clear error messages
- Startup validation prevents running with invalid configuration
- Error messages guide developer to fix issues

---

### Task 5: WebSocket Connection Test

**Goal:** Verify WebSocket connections work with CORS configuration (preparation for PHASE4-003).

**Subtasks:**

- [ ] Install wscat for WebSocket testing:
  ```bash
  npm install -g wscat
  ```

- [ ] Add a test WebSocket endpoint to backend (temporary for validation):
  ```python
  # Add to backend/app/main.py
  from fastapi import WebSocket

  @app.websocket("/ws/test")
  async def websocket_test(websocket: WebSocket):
      await websocket.accept()
      await websocket.send_json({"message": "WebSocket connection successful!"})
      await websocket.close()
  ```

- [ ] Test WebSocket connection from command line:
  ```bash
  wscat -c ws://localhost:8000/ws/test
  ```

**Expected Output:**
```
Connected (press CTRL+C to quit)
< {"message":"WebSocket connection successful!"}
Disconnected
```

- [ ] Test WebSocket connection from browser console:
  ```javascript
  const ws = new WebSocket('ws://localhost:8000/ws/test');
  ws.onopen = () => console.log('✅ WebSocket connected');
  ws.onmessage = (event) => console.log('📨 Message:', JSON.parse(event.data));
  ws.onerror = (error) => console.error('❌ WebSocket error:', error);
  ```

**Expected Output (Browser Console):**
```
✅ WebSocket connected
📨 Message: {message: "WebSocket connection successful!"}
```

**Validation:**
- WebSocket connection establishes successfully
- No CORS errors in browser console
- Message received from backend
- This confirms WebSocket will work for PHASE4-003

---

### Task 6: Create Frontend API Client Configuration

**Subtasks:**
- [ ] Create `frontend/src/config/api.ts`:
  ```typescript
  // API Configuration
  export const API_CONFIG = {
    BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
  } as const;

  // API Endpoints
  export const API_ENDPOINTS = {
    // Health
    HEALTH: '/api/health',

    // Parameters
    PARAMETERS_EXTRACT: '/api/parameters/extract',

    // Workflows
    WORKFLOWS_FORECAST: '/api/workflows/forecast',
    WORKFLOWS_REFORECAST: '/api/workflows/reforecast',
    WORKFLOWS_GET: (id: string) => `/api/workflows/${id}`,
    WORKFLOWS_STREAM: (id: string) => `/api/workflows/${id}/stream`,

    // Resources
    FORECASTS: '/api/forecasts',
    FORECASTS_GET: (id: string) => `/api/forecasts/${id}`,
    ALLOCATIONS_GET: (id: string) => `/api/allocations/${id}`,
    MARKDOWNS_GET: (id: string) => `/api/markdowns/${id}`,
    VARIANCE_GET: (id: string, week: number) => `/api/variance/${id}/week/${week}`,

    // Data Management
    DATA_UPLOAD_HISTORICAL: '/api/data/upload-historical-sales',
    DATA_UPLOAD_WEEKLY: '/api/data/upload-weekly-sales',
    CATEGORIES: '/api/categories',
    STORES: '/api/stores',
    STORES_CLUSTERS: '/api/stores/clusters',

    // Approvals
    APPROVALS_MANUFACTURING: '/api/approvals/manufacturing',
    APPROVALS_MARKDOWN: '/api/approvals/markdown',
  } as const;

  // Helper function to build full URL
  export function buildUrl(endpoint: string): string {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
  }

  // Helper function to build WebSocket URL
  export function buildWsUrl(endpoint: string): string {
    return `${API_CONFIG.WS_URL}${endpoint}`;
  }
  ```

- [ ] Create `frontend/src/utils/api-client.ts`:
  ```typescript
  import { API_CONFIG, buildUrl } from '@/config/api';

  export interface ApiError {
    message: string;
    status: number;
    details?: any;
  }

  export class ApiClient {
    private static async request<T>(
      endpoint: string,
      options: RequestInit = {}
    ): Promise<T> {
      const url = buildUrl(endpoint);

      const defaultOptions: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      };

      try {
        const response = await fetch(url, defaultOptions);

        if (!response.ok) {
          const error: ApiError = {
            message: response.statusText,
            status: response.status,
          };

          try {
            const errorData = await response.json();
            error.details = errorData;
          } catch {
            // Ignore JSON parse errors
          }

          throw error;
        }

        return await response.json();
      } catch (error) {
        if (error instanceof Error) {
          throw {
            message: error.message,
            status: 0,
          } as ApiError;
        }
        throw error;
      }
    }

    static async get<T>(endpoint: string): Promise<T> {
      return this.request<T>(endpoint, { method: 'GET' });
    }

    static async post<T>(endpoint: string, data?: any): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    }

    static async put<T>(endpoint: string, data?: any): Promise<T> {
      return this.request<T>(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    }

    static async delete<T>(endpoint: string): Promise<T> {
      return this.request<T>(endpoint, { method: 'DELETE' });
    }
  }
  ```

- [ ] Test API client with health check:
  ```typescript
  // Test in frontend/src/App.tsx
  import { ApiClient } from '@/utils/api-client';
  import { API_ENDPOINTS } from '@/config/api';

  useEffect(() => {
    ApiClient.get(API_ENDPOINTS.HEALTH)
      .then(data => console.log('Health check:', data))
      .catch(err => console.error('API error:', err));
  }, []);
  ```

**Expected Output (Browser Console):**
```javascript
Health check: { status: "healthy", environment: "development", api_version: "1.0.0" }
```

**Validation:**
- API client successfully calls backend
- No CORS errors
- Health check response displays in console

---

### Task 7: Update .gitignore Files

**Subtasks:**
- [ ] Verify `frontend/.gitignore` includes:
  ```gitignore
  # Environment variables
  .env
  .env.local
  .env.development.local
  .env.test.local
  .env.production.local
  .env.*.local
  ```

- [ ] Verify `backend/.gitignore` includes:
  ```gitignore
  # Environment variables
  .env
  .env.*
  !.env.example

  # Database
  *.db
  *.db-journal

  # Logs
  logs/
  *.log
  ```

- [ ] Test that `.env` files are NOT tracked by git:
  ```bash
  git status
  # Should NOT show .env files

  git add .
  git status
  # Should show .env.example but NOT .env
  ```

**Validation:**
- `.env` files are ignored by git
- `.env.example` files are tracked by git
- No sensitive data committed

---

### Task 8: Update README.md with Environment Setup Instructions

**Subtasks:**
- [ ] Update root `README.md` with environment setup section:
  ```markdown
  ## Environment Setup

  ### Prerequisites
  - Python 3.11+
  - Node.js 18+
  - UV package manager (`pip install uv`)

  ### Backend Setup

  1. Navigate to backend directory:
     ```bash
     cd backend
     ```

  2. Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```

  3. Edit `.env` and add your OpenAI API key:
     ```bash
     OPENAI_API_KEY=sk-your_actual_api_key_here
     ```

  4. Install dependencies:
     ```bash
     uv sync
     ```

  5. Run the backend server:
     ```bash
     uv run uvicorn app.main:app --reload
     ```

  6. Verify backend is running:
     - Open http://localhost:8000/docs (Swagger UI)
     - Check health endpoint: http://localhost:8000/api/health

  ### Frontend Setup

  1. Navigate to frontend directory:
     ```bash
     cd frontend
     ```

  2. Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```

  3. Edit `.env` if needed (defaults should work):
     ```bash
     VITE_API_URL=http://localhost:8000
     VITE_WS_URL=ws://localhost:8000
     ```

  4. Install dependencies:
     ```bash
     npm install
     ```

  5. Run the frontend development server:
     ```bash
     npm run dev
     ```

  6. Verify frontend is running:
     - Open http://localhost:5173
     - Check browser console for no CORS errors

  ### Troubleshooting

  **CORS Errors:**
  - Ensure backend is running on http://localhost:8000
  - Ensure frontend is running on http://localhost:5173
  - Check `backend/.env` has correct `CORS_ORIGINS`

  **Environment Variables Not Loading:**
  - Restart backend/frontend after changing `.env`
  - Verify `.env` file is in the correct directory
  - Check for syntax errors in `.env`
  ```

**Validation:**
- README.md has clear setup instructions
- Instructions are tested and work
- All prerequisites listed

---

## Testing Requirements

### Unit Tests
- N/A for this story (configuration only)

### Integration Tests
1. **Test: Frontend can reach backend health endpoint**
   ```typescript
   describe('API Configuration', () => {
     it('should successfully call backend health endpoint', async () => {
       const response = await ApiClient.get(API_ENDPOINTS.HEALTH);
       expect(response).toHaveProperty('status', 'healthy');
     });
   });
   ```

2. **Test: CORS is configured correctly**
   ```python
   def test_cors_headers(client):
       response = client.options(
           "/api/health",
           headers={
               "Origin": "http://localhost:5173",
               "Access-Control-Request-Method": "GET"
           }
       )
       assert response.status_code == 200
       assert "access-control-allow-origin" in response.headers
       assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
   ```

3. **Test: Environment variables load correctly**
   ```python
   def test_environment_variables():
       from app.core.config import settings
       assert settings.OPENAI_MODEL == "gpt-4o-mini"
       assert "http://localhost:5173" in settings.cors_origins_list
   ```

### Manual Testing Checklist
- [ ] Start backend server → No errors
- [ ] Start frontend server → No errors
- [ ] Open browser to http://localhost:5173
- [ ] Open DevTools → Console → No CORS errors
- [ ] Test health endpoint from browser console
- [ ] Verify response: `{ status: "healthy", ... }`
- [ ] Check Network tab → Request to backend shows correct CORS headers
- [ ] Test with different browser (Chrome, Firefox, Edge)

---

## Implementation Notes

### CORS Configuration Gotchas

1. **Port Numbers Matter:**
   - Frontend runs on `:5173` (Vite default)
   - Backend runs on `:8000` (FastAPI default)
   - CORS origin MUST match exactly: `http://localhost:5173` (not `http://localhost:5174`)

2. **Trailing Slashes:**
   - Do NOT include trailing slashes in `CORS_ORIGINS`
   - ✅ Correct: `http://localhost:5173`
   - ❌ Wrong: `http://localhost:5173/`

3. **Multiple Origins:**
   - Separate with commas (no spaces): `http://localhost:5173,http://localhost:3000`
   - OR include spaces: `http://localhost:5173, http://localhost:3000`
   - The `cors_origins_list` property handles both

4. **Credentials:**
   - Set `allow_credentials=True` if frontend needs to send cookies/auth headers
   - Required for WebSocket connections with authentication

### Environment Variable Best Practices

1. **Never Commit `.env` Files:**
   - Always use `.env.example` with placeholder values
   - Add `.env` to `.gitignore`

2. **Use Descriptive Variable Names:**
   - ✅ `VITE_API_URL` (clear purpose)
   - ❌ `API` (ambiguous)

3. **Provide Defaults:**
   - Use `||` operator in JavaScript: `import.meta.env.VITE_API_URL || 'http://localhost:8000'`
   - Use default values in Pydantic: `OPENAI_MODEL: str = "gpt-4o-mini"`

4. **Validate Required Variables:**
   - Pydantic will raise error if required env var is missing
   - Frontend should warn if `VITE_API_URL` is undefined

---

## Dependencies

**Requires:**
- Phase 1 complete (data generation)
- Phase 2 complete (frontend mockups)
- Phase 3 complete (backend architecture)

**Enables:**
- PHASE4-002: Section 0 - Parameter Gathering Integration
- PHASE4-003: Section 1 - Agent Cards + Real WebSocket
- All subsequent Phase 4 stories

---

## Definition of Done

**Configuration Files:**
- [ ] Frontend `.env` created with `VITE_API_URL` and `VITE_WS_URL`
- [ ] Backend `.env` created with `OPENAI_API_KEY` and all required variables
- [ ] `.env.example` files created for both frontend and backend
- [ ] `.env` files added to `.gitignore`

**CORS & Connectivity:**
- [ ] CORS middleware configured in FastAPI (HTTP + WebSocket support)
- [ ] Frontend can call `GET /api/health` without CORS errors
- [ ] OPTIONS preflight requests return 200 OK
- [ ] WebSocket connection test passes (`/ws/test` endpoint)

**Validation & Quality:**
- [ ] Environment variable validation on backend startup
- [ ] Missing/invalid env vars cause clear error messages
- [ ] Comprehensive environment variable checklist documented
- [ ] All manual tests passing
- [ ] No console errors in browser
- [ ] Backend logs show no errors

**Documentation:**
- [ ] README.md updated with setup instructions
- [ ] Planning document references added to story
- [ ] Troubleshooting section included

---

## Time Tracking

- **Estimated:** 3 hours
- **Actual:** ___ hours
- **Variance:** ___ hours

**Breakdown:**
- Task 1 (Frontend .env): ___ min
- Task 2 (Backend .env): ___ min
- Task 3 (CORS config): ___ min
- Task 4 (Environment validation): ___ min
- Task 5 (WebSocket test): ___ min
- Task 6 (API client): ___ min
- Task 7 (.gitignore): ___ min
- Task 8 (README): ___ min
- Testing: ___ min
- Documentation: ___ min

---

## Related Stories

- **Blocks:** PHASE4-002 (Section 0), PHASE4-003 (WebSocket), PHASE4-007 (CSV Upload)
- **Related:** PHASE4-009 (Documentation)

---

**Status:** ⏳ Ready for Implementation
**Assigned To:** Dev Team
**Priority:** P0 (Critical - Blocks all other Phase 4 work)
**Created:** 2025-10-29
**Updated:** 2025-10-29
