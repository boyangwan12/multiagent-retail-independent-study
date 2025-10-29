# Phase 4 Integration - Master Checklist

**Phase:** Phase 4 - Frontend/Backend Integration
**Status:** Not Started
**Started:** [DATE]
**Completed:** [DATE]
**Total Stories:** 9
**Estimated Effort:** 48 hours (6 days)

---

## Story Progress Tracker

| Story ID | Story Name | Status | Estimated Effort | Actual Effort | Completion Date |
|----------|------------|--------|------------------|---------------|-----------------|
| PHASE4-001 | Environment Configuration | ⬜ Not Started | 4 hours | | |
| PHASE4-002 | Section 0 - Parameter Gathering | ⬜ Not Started | 6 hours | | |
| PHASE4-003 | Section 1 - Agent Cards + WebSocket | ⬜ Not Started | 8 hours | | |
| PHASE4-004 | Sections 2-3 - Forecast + Clusters | ⬜ Not Started | 6 hours | | |
| PHASE4-005 | Sections 4-5 - Weekly Chart + Replenishment | ⬜ Not Started | 6 hours | | |
| PHASE4-006 | Sections 6-7 - Markdown + Performance Metrics | ⬜ Not Started | 6 hours | | |
| PHASE4-007 | CSV Upload Workflows | ⬜ Not Started | 8 hours | | |
| PHASE4-008 | Integration Tests | ⬜ Not Started | 8 hours | | |
| PHASE4-009 | Documentation Updates | ⬜ Not Started | 4 hours | | |

**Legend:** ⬜ Not Started | 🟡 In Progress | ✅ Completed | ❌ Blocked

---

## PHASE4-001: Environment Configuration

### Backend Setup
- [ ] Create backend/.env file with 9 required variables
- [ ] Install UV package manager
- [ ] Set up virtual environment with UV
- [ ] Install dependencies from pyproject.toml
- [ ] Verify FastAPI runs on port 8000
- [ ] Test CORS configuration with frontend origin

### Frontend Setup
- [ ] Create frontend/.env file with VITE_API_BASE_URL
- [ ] Install Node.js dependencies (npm install)
- [ ] Verify Vite dev server runs on port 5173
- [ ] Test API client connection to backend

### API Client Configuration
- [ ] Create src/config/api.config.ts with all 15 endpoints
- [ ] Create src/services/apiClient.ts with GET/POST/PUT/DELETE methods
- [ ] Test buildUrl utility function
- [ ] Test error handling for 404, 422, 500

### Testing
- [ ] Postman: Test backend /health endpoint
- [ ] Frontend: Test API_BASE_URL environment variable
- [ ] Frontend: Test CORS with actual API call
- [ ] Verify hot reload works for both frontend and backend

---

## PHASE4-002: Section 0 - Parameter Gathering

### Backend Testing (Postman)
- [ ] Test Case 1: All parameters specified (4 test scenarios)
- [ ] Test Case 2: No replenishment strategy
- [ ] Test Case 3: No markdown checkpoint
- [ ] Test Case 4: Invalid input (empty string)

### Frontend Service
- [ ] Create src/services/parameterService.ts
- [ ] Implement extractParameters method
- [ ] Create TypeScript interfaces (SeasonParameters, ParameterExtractionResponse)
- [ ] Test error handling for 422 responses

### Frontend Component
- [ ] Create src/components/ParameterGathering.tsx
- [ ] Implement textarea with user input
- [ ] Implement "Extract Parameters" button
- [ ] Add loading state with spinner
- [ ] Display extracted parameters in card
- [ ] Display adaptation reasoning
- [ ] Handle extraction errors with error messages
- [ ] Test with 4 different user inputs

### Manual Testing
- [ ] Submit natural language input
- [ ] Verify parameters extracted correctly
- [ ] Verify workflow_id returned
- [ ] Verify error handling for invalid input

---

## PHASE4-003: Section 1 - Agent Cards + WebSocket

### Backend WebSocket Testing (wscat)
- [ ] Install wscat globally
- [ ] Test WebSocket connection to /api/workflows/{id}/stream
- [ ] Receive agent_started message
- [ ] Receive agent_progress message
- [ ] Receive agent_completed message
- [ ] Receive workflow_complete message
- [ ] Test connection close

### Frontend WebSocket Service
- [ ] Create src/services/websocketService.ts
- [ ] Implement connect method
- [ ] Implement onMessage handler
- [ ] Implement disconnect method
- [ ] Implement reconnection logic (max 5 attempts)
- [ ] Test reconnection after disconnect

### Frontend useWebSocket Hook
- [ ] Create src/hooks/useWebSocket.ts
- [ ] Manage connection lifecycle
- [ ] Manage message state
- [ ] Return connect, disconnect, messages, connectionStatus
- [ ] Test with multiple components

### Frontend AgentCards Component
- [ ] Create src/components/AgentCards.tsx
- [ ] Display 3 agent cards (Demand, Inventory, Pricing)
- [ ] Show status badges (pending, running, completed)
- [ ] Show progress bars (0-100%)
- [ ] Show current message from agent
- [ ] Update cards in real-time from WebSocket messages
- [ ] Test with all 6 WebSocket message types

### Manual Testing
- [ ] Start workflow and connect to WebSocket
- [ ] Verify agent cards update in real-time
- [ ] Verify progress bars animate correctly
- [ ] Verify workflow_complete message marks all agents complete
- [ ] Test reconnection after disconnect

---

## PHASE4-004: Sections 2-3 - Forecast + Clusters

### Backend Testing (Postman)
- [ ] Test GET /api/forecasts/{id} returns ForecastSummary
- [ ] Test GET /api/stores/clusters returns 3 clusters
- [ ] Verify manufacturing order calculation
- [ ] Test 404 for invalid workflow_id

### Frontend ForecastService
- [ ] Create src/services/forecastService.ts
- [ ] Implement getForecastSummary method
- [ ] Create ForecastSummary interface
- [ ] Test error handling

### Frontend ClusterService
- [ ] Create src/services/clusterService.ts
- [ ] Implement getClusters method
- [ ] Implement exportClustersCSV method
- [ ] Create ClusterData interface

### Frontend ForecastSummary Component
- [ ] Create src/components/ForecastSummary.tsx
- [ ] Display total demand
- [ ] Display safety stock percentage
- [ ] Display manufacturing order with calculation
- [ ] Display MAPE with color coding
- [ ] Display adaptation reasoning
- [ ] Test with mock and real data

### Frontend ClusterCards Component
- [ ] Create src/components/ClusterCards.tsx
- [ ] Display 3 cluster cards (A, B, C)
- [ ] Show store count per cluster
- [ ] Show average demand per cluster
- [ ] Add "Export CSV" button
- [ ] Test CSV export functionality

### Manual Testing
- [ ] Verify forecast summary displays correctly
- [ ] Verify manufacturing order calculation matches backend
- [ ] Verify MAPE color coding (green <15%, yellow 15-25%, red >25%)
- [ ] Verify 3 cluster cards display
- [ ] Test CSV export downloads file

---

## PHASE4-005: Sections 4-5 - Weekly Chart + Replenishment

### Backend Testing (Postman)
- [ ] Test GET /api/variance/{id}/week/3 returns variance data
- [ ] Test GET /api/allocations/{id} returns allocations
- [ ] Test replenishment_strategy = "none" hides Section 5
- [ ] Verify variance calculation (forecast vs. actual)

### Frontend VarianceService
- [ ] Create src/services/varianceService.ts
- [ ] Implement getWeeklyVariance method
- [ ] Create VarianceData interface

### Frontend AllocationService
- [ ] Create src/services/allocationService.ts
- [ ] Implement getAllocations method
- [ ] Create AllocationData interface

### Frontend WeeklyPerformanceChart Component
- [ ] Create src/components/WeeklyPerformanceChart.tsx
- [ ] Use Recharts ComposedChart
- [ ] Display forecast line (blue)
- [ ] Display actual bars (blue)
- [ ] Highlight variance >20% (red), 10-20% (yellow), <10% (green)
- [ ] Add tooltip with variance percentage
- [ ] Test with 12-week forecast

### Frontend ReplenishmentQueue Component
- [ ] Create src/components/ReplenishmentQueue.tsx
- [ ] Display store-level allocations in table
- [ ] Show replenishment schedule
- [ ] Conditional display (hidden if replenishment_strategy = "none")
- [ ] Test with weekly, bi-weekly, and none strategies

### Manual Testing
- [ ] Verify weekly chart displays 12 weeks
- [ ] Verify variance color coding correct
- [ ] Verify replenishment queue shows when strategy != "none"
- [ ] Verify replenishment queue hidden when strategy = "none"

---

## PHASE4-006: Sections 6-7 - Markdown + Performance Metrics

### Backend Testing (Postman)
- [ ] Test GET /api/markdowns/{id} with markdown_checkpoint_week set
- [ ] Test GET /api/markdowns/{id} returns 404 when markdown_checkpoint_week = null
- [ ] Test GET /api/variance/{id}/summary returns average variance
- [ ] Verify Gap × Elasticity calculation

### Frontend MarkdownService
- [ ] Create src/services/markdownService.ts
- [ ] Implement getMarkdownAnalysis method
- [ ] Handle 404 gracefully (return null)
- [ ] Create MarkdownAnalysis interface

### Frontend PerformanceService
- [ ] Create src/services/performanceService.ts
- [ ] Implement getPerformanceMetrics method (aggregates 3 endpoints)
- [ ] Calculate sell-through percentage
- [ ] Determine system status (Healthy, Moderate, Needs Attention)
- [ ] Create PerformanceMetrics interface

### Frontend MarkdownDecision Component
- [ ] Create src/components/MarkdownDecision.tsx
- [ ] Display Gap × Elasticity formula
- [ ] Display recommended markdown percentage
- [ ] Display expected sell-through after markdown
- [ ] Display risk assessment
- [ ] Conditional display (hidden if markdown_checkpoint_week = null)
- [ ] Test with markdown enabled and disabled

### Frontend PerformanceMetrics Component
- [ ] Create src/components/PerformanceMetrics.tsx
- [ ] Display 3 metric cards (MAPE, Variance, Sell-Through)
- [ ] Color code each metric (green/yellow/red)
- [ ] Display System Status badge
- [ ] Add tooltips explaining each metric
- [ ] Test with all metrics in healthy, moderate, critical ranges

### Manual Testing
- [ ] Test Section 6 displays when markdown_checkpoint_week set
- [ ] Test Section 6 hidden when markdown_checkpoint_week = null
- [ ] Verify Gap × Elasticity calculation displayed correctly
- [ ] Test Section 7 displays all 3 metrics
- [ ] Verify System Status badge updates based on metrics

---

## PHASE4-007: CSV Upload Workflows

### Backend Testing (Postman)
- [ ] Test Case 1: Valid CSV upload (sales_data.csv)
- [ ] Test Case 2: Invalid CSV - missing required column
- [ ] Test Case 3: Invalid CSV - wrong data type
- [ ] Test Case 4: File too large (>10MB)
- [ ] Test Case 5: Wrong file extension (.xlsx)
- [ ] Test Case 6: Multiple file upload

### Frontend UploadService
- [ ] Create src/services/uploadService.ts
- [ ] Implement uploadFile method (FormData)
- [ ] Implement uploadMultipleFiles method
- [ ] Validate file size before upload (max 10MB)
- [ ] Validate file extension (.csv only)
- [ ] Create UploadResponse interface

### Frontend UploadZone Component
- [ ] Create src/components/UploadZone.tsx
- [ ] Implement drag-and-drop zone
- [ ] Implement file picker (click to browse)
- [ ] Show selected file preview
- [ ] Show upload progress bar
- [ ] Show success state (green checkmark)
- [ ] Show error state with validation errors
- [ ] Add "Download Error Report" button

### Frontend UploadModal Component
- [ ] Create src/components/UploadModal.tsx
- [ ] Add 3 tabs (Demand, Inventory, Pricing)
- [ ] Add UploadZone for each file type
- [ ] Show green checkmark on tab when file uploaded
- [ ] Display upload status summary

### Dashboard Integration
- [ ] Add "Upload Data" button below Agent Cards
- [ ] Button opens UploadModal
- [ ] Modal closes correctly

### Manual Testing
- [ ] Test drag-and-drop file upload
- [ ] Test file picker upload
- [ ] Test valid CSV upload (success state)
- [ ] Test invalid CSV with missing column (error state)
- [ ] Test invalid CSV with wrong data type (error with row number)
- [ ] Test file >10MB (rejected)
- [ ] Test .xlsx file (rejected)
- [ ] Download error report as .txt file
- [ ] Upload multiple files in one agent tab

---

## PHASE4-008: Integration Tests

### Backend Test Environment
- [ ] Install pytest, pytest-asyncio, pytest-cov
- [ ] Create pytest.ini configuration
- [ ] Create tests/conftest.py with fixtures
- [ ] Create test directory structure

### Backend Integration Tests
- [ ] Create test_parameters.py (4 test cases)
- [ ] Create test_websocket.py (3 test cases)
- [ ] Create test_forecasts.py (4 test cases)
- [ ] Create test_allocations.py (2 test cases)
- [ ] Create test_markdowns.py (2 test cases)
- [ ] Create test_uploads.py (2 test cases)
- [ ] Run all tests: `pytest tests/integration/ -v`
- [ ] Generate coverage report: `pytest --cov=app --cov-report=html`
- [ ] Verify coverage >80%

### Frontend Test Environment
- [ ] Install Vitest, Testing Library, MSW
- [ ] Create vitest.config.ts
- [ ] Create src/tests/setup.ts (MSW setup)
- [ ] Create src/tests/mocks/handlers.ts (API mocks)

### Frontend Integration Tests
- [ ] Create ParameterService.test.ts (2 test cases)
- [ ] Create ForecastService.test.ts (2 test cases)
- [ ] Create ParameterGathering.test.tsx (2 test cases)
- [ ] Create UploadZone.test.tsx (1 test case)
- [ ] Run all tests: `npm run test`
- [ ] Generate coverage report: `npm run test:coverage`
- [ ] Verify coverage >70%

### End-to-End Testing
- [ ] Test full workflow with markdown enabled
- [ ] Test full workflow with markdown disabled
- [ ] Test error handling (invalid inputs, network errors)
- [ ] Test CSV upload workflow

---

## PHASE4-009: Documentation Updates

### Root README
- [ ] Add Phase 4 completion badge
- [ ] Update overview with integration-first approach
- [ ] Add quick start instructions
- [ ] Update phase status tracker
- [ ] Add links to Phase 4 documentation

### Backend README
- [ ] Document all 15+ API endpoints
- [ ] Add request/response examples
- [ ] Add environment variables reference
- [ ] Add database schema overview
- [ ] Add testing instructions
- [ ] Add troubleshooting guide

### Frontend README
- [ ] Document all 8 dashboard sections
- [ ] Add component architecture diagram
- [ ] Document service layer
- [ ] Add testing instructions
- [ ] Add build and deployment instructions
- [ ] Add troubleshooting guide

### API Documentation (OpenAPI/Swagger)
- [ ] Generate OpenAPI schema
- [ ] Verify accessible at http://localhost:8000/docs
- [ ] Add endpoint descriptions
- [ ] Add request/response examples
- [ ] Add error code documentation

### Architecture Documentation
- [ ] Create docs/architecture/ folder
- [ ] Create system_overview.md
- [ ] Create frontend_backend_integration.md
- [ ] Create websocket_flow.md
- [ ] Create parameter_driven_architecture.md
- [ ] Add architecture diagrams (Mermaid or images)

### Developer Guide
- [ ] Create docs/developer_guide.md
- [ ] Add local development setup instructions
- [ ] Add environment configuration guide
- [ ] Add testing workflows
- [ ] Add troubleshooting section
- [ ] Add code style guidelines

### Inline Code Documentation
- [ ] Add docstrings to all backend endpoint functions
- [ ] Add JSDoc comments to all frontend service methods
- [ ] Add example usage in comments
- [ ] Document parameters and return types

### Validation
- [ ] Test quick start instructions on fresh machine
- [ ] Test all API examples in Postman
- [ ] Validate all documentation links
- [ ] Check consistency across all docs

---

## Final Validation Checklist

### Functionality
- [ ] All 8 dashboard sections display correctly
- [ ] WebSocket real-time updates work
- [ ] CSV uploads work with validation
- [ ] Error handling works across all components
- [ ] Conditional sections (5, 6) show/hide correctly

### Testing
- [ ] All backend integration tests pass (17+ tests)
- [ ] All frontend integration tests pass (8+ tests)
- [ ] Backend coverage >80%
- [ ] Frontend coverage >70%
- [ ] No console errors or warnings

### Documentation
- [ ] Root README updated
- [ ] Backend README comprehensive
- [ ] Frontend README comprehensive
- [ ] OpenAPI docs complete
- [ ] Architecture docs created
- [ ] Developer guide complete
- [ ] Inline code documentation added

### Code Quality
- [ ] Backend follows PEP 8
- [ ] Frontend follows ESLint rules
- [ ] All type hints/annotations added
- [ ] No linting errors
- [ ] Code reviewed by team member

### Performance
- [ ] API response times <500ms
- [ ] WebSocket connection stable
- [ ] CSV uploads <5 seconds for 10MB files
- [ ] Frontend loads <2 seconds

---

## Blockers & Issues

| Issue ID | Description | Status | Resolution | Date Resolved |
|----------|-------------|--------|------------|---------------|
| | | | | |

---

## Notes & Observations

### Key Decisions Made

1. **Integration-First Approach:** Connected frontend/backend before implementing AI agents
2. **Mock Agents:** Return dynamic, parameter-driven data instead of static JSON
3. **WebSocket for Real-Time:** Used WebSocket instead of polling for agent updates
4. **Conditional Sections:** Sections 5 and 6 conditionally display based on parameters
5. **CSV Validation:** Backend validates CSV format and returns detailed errors

### Lessons Learned

- [Add lessons learned during implementation]

### Technical Debt

- [List any technical debt incurred during Phase 4]

---

## Phase 4 Completion Criteria

✅ **Phase 4 is complete when:**

1. All 9 stories completed and validated
2. All 8 dashboard sections integrated and functional
3. WebSocket real-time updates working
4. CSV uploads working with validation
5. All integration tests passing (backend + frontend)
6. Code coverage >80% (backend) and >70% (frontend)
7. All documentation updated and validated
8. Code reviewed and merged to main branch
9. Retrospective completed
10. Handoff document created for Phase 5

---

**Last Updated:** [DATE]
**Updated By:** [NAME]
