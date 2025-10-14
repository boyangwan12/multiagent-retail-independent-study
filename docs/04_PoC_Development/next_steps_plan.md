# Next Steps: From Product Brief to PoC Implementation

**Status**: Planning Documents Complete ✅ → Ready for Implementation

**Last Updated**: 2025-10-13

---

## ✅ Completed Documents (All v3.2)

| Document | Status | Owner | Output Path |
|----------|--------|-------|-------------|
| **Product Brief v3.2** | ✅ Complete | architect | `product_brief/product_brief_v3.2.md` |
| **Operational Workflow v3.2** | ✅ Complete | architect | `product_brief/operational_workflow_v3.2.md` |
| **Technical Architecture v3.2** | ✅ Complete | architect | `architecture/technical_architecture_v3.2.md` |
| **Frontend UI/UX Spec v3.2** | ✅ Complete | designer | `design/front-end-spec_v3.2.md` |

**Key Achievements:**
- ✅ All documents aligned (no contradictions)
- ✅ Category auto-detection implemented
- ✅ Linear Dark Theme design system defined
- ✅ Complete API contracts + data models
- ✅ All wireframes and user flows complete

---

## Documents Still Needed

### 1. **Mock Data Generation Script** 📊
**Owner**: `*agent data` (Data Generator Agent)
**Purpose**: Create realistic test datasets for development
**What You Need**:
- Python script to generate `historical_sales_2022_2024.csv` (~54,750 rows)
- Python script to generate `store_attributes.csv` (50 rows)
- Support 3 test scenarios (normal, high demand, low demand)
- Categories: Women's Dresses, Men's Shirts, Accessories (mixed in one CSV)

**Output**: `data/mock/generate_mock_data.py` + 2 CSV files

---

### 2. **Backend Implementation** 🔧
**Owner**: `*agent dev` (Backend Developer Agent)
**Purpose**: Implement 3-agent system using OpenAI Agents SDK
**What You Need**:
- Project structure setup (backend/ with agents/, api/, ml/ folders)
- Demand Agent: Prophet + ARIMA ensemble, K-means clustering, allocation logic
- Inventory Agent: Manufacturing calculation, hierarchical allocation, replenishment
- Pricing Agent: Gap × Elasticity markdown, sell-through tracking
- Orchestrator: Workflow coordination, variance monitoring (>20% threshold)
- REST API + WebSocket implementation

**Output**: `backend/` folder with working agent system

---

### 3. **Frontend Implementation** 🎨
**Owner**: `*agent frontend` (Frontend Developer Agent)
**Purpose**: Build single-page dashboard with Linear Dark Theme
**What You Need**:
- Project structure setup (frontend/ with React + TypeScript + Vite)
- 7-section single-page dashboard (agent cards, forecast, clusters, weekly chart, replenishment, markdown, metrics)
- WebSocket integration (line-by-line agent progress)
- Linear Dark Theme (Shadcn/ui + Tailwind)
- Report page (`/reports/spring-2025`)

**Output**: `frontend/` folder with working UI

---

### 4. **Integration Testing** 🧪
**Owner**: `*agent qa` (QA/Testing Agent)
**Purpose**: Validate system accuracy and functionality
**What You Need**:
- Test 3 scenarios (normal season, high demand, low demand)
- Validate MAPE < 20%
- Test variance-triggered re-forecast (>20%)
- Test Week 6 markdown logic
- E2E testing (CSV upload → forecast → allocation → markdown)

**Output**: Test results and bug reports

---

## Recommended Sequence

### **Phase 1: Data Preparation** (First!)
1. **Talk to `*agent data`**
   - Generate mock CSV files
   - Validate data structure matches specs
   - Ensure 3 categories mixed in historical_sales.csv

### **Phase 2: Backend Foundation** (Week 5-8)
2. **Talk to `*agent dev`** (backend)
   - Set up project structure (backend/ folders)
   - Implement 3 agents (Demand, Inventory, Pricing)
   - Implement Orchestrator + variance monitoring
   - Build REST API + WebSocket

### **Phase 3: Frontend Development** (Week 9-12)
3. **Talk to `*agent frontend`**
   - Set up React + TypeScript + Vite
   - Build 7-section dashboard
   - Integrate WebSocket for real-time updates
   - Implement Linear Dark Theme

### **Phase 4: Testing & Validation** (Week 13-14)
4. **Talk to `*agent qa`**
   - Run 3 test scenarios
   - Validate forecast accuracy (MAPE)
   - Test variance triggers and re-forecasts
   - Bug fixes and polish

---

## Quick Start: Who to Talk to First

**Option 1: Generate Mock Data** (Recommended)
```
*agent data
→ "I need Python script to generate historical_sales_2022_2024.csv and store_attributes.csv with 3 categories (Women's Dresses, Men's Shirts, Accessories) mixed together"
```

**Option 2: Start Backend**
```
*agent dev
→ "I need backend implementation of 3-agent retail forecasting system using OpenAI Agents SDK"
```

**Option 3: Start Frontend**
```
*agent frontend
→ "I need React frontend for single-page dashboard with Linear Dark Theme based on front-end-spec_v3.2.md"
```

---

## Summary: What's Left to Build

| Task | Owner | Priority | Status |
|------|-------|----------|--------|
| **Mock Data Script** | data | **HIGH** | ⏳ Not Started |
| **Backend (3 Agents + API)** | dev | **HIGH** | ⏳ Not Started |
| **Frontend (Dashboard)** | frontend | **HIGH** | ⏳ Not Started |
| **Testing & Validation** | qa | MEDIUM | ⏳ Not Started |

---

## Recommended First Step

**Start with `*agent data`** to generate mock datasets:
1. Create Python script for CSV generation
2. Generate `historical_sales_2022_2024.csv` (~54,750 rows, 3 categories)
3. Generate `store_attributes.csv` (50 stores, 7 features)
4. Validate data structure matches front-end-spec_v3.2.md Section 12

Once mock data is ready, move to `*agent dev` for backend, then `*agent frontend` for UI.

---

**Ready?** Type:
- `*agent data` to generate mock data (recommended first step)
- `*agent dev` to start backend implementation
- `*agent frontend` to start frontend implementation
- `*agent qa` to plan testing strategy
