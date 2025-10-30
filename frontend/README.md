# Multi-Agent Retail Forecasting Dashboard - Frontend

A modern, interactive dashboard for retail season forecasting using a multi-agent AI system. Built with React 18, TypeScript, and Tailwind CSS following the Linear Dark Theme design system.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Linear Dark Theme](#linear-dark-theme)
- [Development Guide](#development-guide)
- [Dashboard Sections](#dashboard-sections)
- [State Management](#state-management)
- [Testing](#testing)
- [Building for Production](#building-for-production)

---

## 🎯 Overview

The Multi-Agent Retail Forecasting Dashboard is a sophisticated frontend application that visualizes the collaborative work of three specialized AI agents:

- **Demand Agent**: Forecasts seasonal demand using Prophet and ARIMA models
- **Inventory Agent**: Optimizes store-level inventory allocation with clustering
- **Pricing Agent**: Determines markdown strategies to minimize excess stock

This dashboard provides retail planners with a transparent, intuitive interface to:
1. Input season parameters in natural language
2. Monitor real-time agent workflow execution
3. Review forecast results with visual analytics
4. Make data-driven inventory and pricing decisions

## ✨ Features

### Core Functionality
- ✅ **Natural Language Parameter Extraction** - Describe your season in plain English
- ✅ **Real-time Agent Monitoring** - Watch agents collaborate via mock WebSocket
- ✅ **Interactive Data Tables** - Sort, filter, and export cluster allocations
- ✅ **Responsive Charts** - Weekly forecast vs actuals with variance indicators
- ✅ **Markdown Decision Support** - Interactive slider with revenue impact preview
- ✅ **Performance Metrics** - MAPE tracking and agent contribution analysis

### UI/UX Features
- ✅ **Linear Dark Theme** - Professional dark mode with purple-blue accents
- ✅ **Keyboard Navigation** - Alt+1-8 shortcuts for section jumping
- ✅ **Error Boundaries** - Isolated section failures prevent full app crashes
- ✅ **Toast Notifications** - Success/error/warning feedback system
- ✅ **Mobile Warning** - Graceful degradation for small screens (<768px)
- ✅ **Accessibility** - WCAG 2.1 AA compliant with ARIA labels

---

## 🛠️ Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React | 19.1.1 | UI library |
| **Language** | TypeScript | 5.9.3 | Type safety |
| **Build Tool** | Vite | 7.1.7 | Fast dev server & bundler |
| **Styling** | Tailwind CSS | 3.4.18 | Utility-first CSS |
| **Components** | Shadcn/ui | - | Radix UI primitives |
| **Data Fetching** | TanStack Query | 5.90.5 | Server state management |
| **Tables** | TanStack Table | 8.21.3 | Powerful data grids |
| **Charts** | Recharts | 2.15.4 | React chart library |
| **Icons** | Lucide React | 0.546.0 | Icon library |
| **Error Handling** | react-error-boundary | 6.0.0 | Error boundaries |

---

## 🚀 Getting Started

### Prerequisites

- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- **Modern browser**: Chrome, Firefox, Safari (latest versions)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multiagent-retail-independent-study/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   Navigate to `http://localhost:5173`

### Available Scripts

```bash
# Start development server with hot reload
npm run dev

# Type-check TypeScript files and build
npm run build

# Lint code with ESLint
npm run lint

# Preview production build locally
npm run preview
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components (41 files)
│   │   ├── ParameterGathering/   # Section 0: Natural language input
│   │   ├── AgentWorkflow/        # Section 1: Agent status cards
│   │   ├── ForecastSummary/      # Section 2: Metric cards
│   │   ├── ClusterCards/         # Section 3: Store clustering tables
│   │   ├── WeeklyChart/          # Section 4: Forecast vs actuals chart
│   │   ├── ReplenishmentQueue/   # Section 5: Inventory recommendations
│   │   ├── MarkdownDecision/     # Section 6: Pricing strategy slider
│   │   ├── PerformanceMetrics/   # Section 7: System accuracy metrics
│   │   ├── Layout/               # App layout, sidebar, headers
│   │   ├── ErrorBoundary/        # Error handling components
│   │   ├── Toast/                # Notification system
│   │   └── ui/                   # Shadcn/ui primitives (dialog)
│   │
│   ├── contexts/            # React Context providers
│   │   ├── ParametersContext.tsx  # Season parameters state
│   │   └── WorkflowContext.tsx    # Agent workflow state
│   │
│   ├── hooks/               # Custom React hooks (9 files)
│   │   ├── useAgentStatus.ts      # Mock WebSocket for agent updates
│   │   ├── useForecast.ts         # Fetch forecast data
│   │   ├── useClusters.ts         # Fetch cluster allocations
│   │   └── ...
│   │
│   ├── types/               # TypeScript type definitions (11 files)
│   ├── utils/               # Utility functions
│   ├── lib/                 # Library utilities
│   ├── mocks/               # Mock JSON data (7 files)
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles & Tailwind imports
│
├── package.json             # Dependencies & scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

---

## 🎨 Linear Dark Theme

The dashboard uses a carefully designed dark theme inspired by Linear's design system.

### Color System

#### Base Colors
```typescript
background: "#0D0D0D"   // Near-black page background
card: "#1A1A1A"         // Dark gray cards
primary: "#5E6AD2"      // Purple-blue (buttons, links, active states)
border: "#2A2A2A"       // Subtle borders
hover: "#1F1F1F"        // Hover states
```

#### Text Colors
```typescript
text-primary: "#FFFFFF"     // White text (headings, important text)
text-secondary: "#9CA3AF"   // Light gray (descriptions, labels)
text-muted: "#6B7280"       // Muted gray (disabled states)
```

#### Status Colors
```typescript
success: "#00D084"   // Green (✅ positive metrics, low variance)
warning: "#F5A623"   // Amber (⚠️  moderate variance)
error: "#F97066"     // Soft red (❌ high variance, errors)
info: "#5B8DEF"      // Soft blue (ℹ️  informational)
```

#### Agent Colors
```typescript
agent-demand: "#5B8DEF"     // Demand Agent (soft blue)
agent-inventory: "#00D084"  // Inventory Agent (green)
agent-pricing: "#F59E0B"    // Pricing Agent (amber)
```

#### Chart Colors
```typescript
chart-forecast: "#5E6AD2"   // Purple-blue line (forecast)
chart-actual: "#00D084"     // Green bars (actuals on track)
chart-variance: "#F97066"   // Red bars (high variance weeks)
```

### Typography
- **Font Family**: Inter (sans), SF Mono (monospace)
- **Font Sizes**: `text-sm` (14px), `text-base` (16px), `text-2xl` (24px), `text-3xl` (30px)

### Using the Theme

#### Card Component
```tsx
<div className="bg-card border border-border rounded-lg p-6">
  <h3 className="text-lg font-semibold text-text-primary">Card Title</h3>
  <p className="text-sm text-text-secondary">Card description</p>
</div>
```

#### Button Component
```tsx
<button className="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg">
  Primary Action
</button>
```

#### Status Badge
```tsx
<span className="bg-success/10 text-success border border-success/20 px-2 py-1 rounded">
  ✓ Success
</span>
```

---

## 💻 Development Guide

### Component Architecture

1. **Container Components** (e.g., `AgentWorkflow.tsx`)
   - Fetch data using custom hooks
   - Manage local state
   - Handle loading/error states

2. **Presentation Components** (e.g., `AgentCard.tsx`)
   - Receive data via props
   - Pure rendering (no data fetching)
   - Reusable across sections

### State Management

#### Global State (Context API)
- **ParametersContext**: Season parameters extracted from user input
- **ToastContext**: Toast notification system

#### Server State (TanStack Query)
- **useForecast**: Fetch forecast data
- **useClusters**: Fetch cluster allocations
- **useWeeklyData**: Fetch weekly actuals
- **useReplenishment**: Fetch replenishment queue
- **useMarkdown**: Fetch markdown scenarios
- **usePerformance**: Fetch performance metrics

---

## 📊 Dashboard Sections

### Section 0: Parameter Gathering
Extract structured parameters from natural language input.

**Example Input**:
```
12-week spring season starting March 1st.
No replenishment, 0% holdback.
Markdown at week 6 if below 60% sell-through.
```

**Extracted Parameters**:
- Forecast horizon: 12 weeks
- Season start: 2025-03-01
- Replenishment: none
- DC holdback: 0%

### Section 1: Agent Workflow
Monitor multi-agent collaboration in real-time with status indicators.

### Section 2: Forecast Summary
Display 4 key metrics with delta calculations vs baseline.

### Section 3: Cluster Distribution
Show store clustering with sortable tables (High/Medium/Low volume).

### Section 4: Weekly Performance
Compare forecast vs actuals with variance tracking chart.

### Section 5: Replenishment Queue
Display store-level inventory recommendations with action buttons.

### Section 6: Markdown Decision
Interactive slider for markdown strategy optimization.

### Section 7: Performance Metrics
Track MAPE, accuracy, and agent contribution breakdown.

---

## 🔐 State Management

### ParametersContext

```typescript
import { useParameters } from '@/contexts/ParametersContext';

function MyComponent() {
  const { parameters, setParameters, clearParameters } = useParameters();
}
```

### Toast Notifications

```typescript
import { useToast } from '@/components/Toast';

function MyComponent() {
  const { showToast } = useToast();

  showToast('success', 'Action completed!', 5000);
  showToast('error', 'Something went wrong!', 5000);
}
```

---

## 🧪 Testing

### Manual Testing Checklist

See [TESTING_CHECKLIST.md](../docs/TESTING_CHECKLIST.md) for comprehensive test cases.

**Quick Test**:
1. ✅ Parameter extraction works
2. ✅ Agent cards update status
3. ✅ Tables sort/filter
4. ✅ Chart renders with variance
5. ✅ Keyboard shortcuts work (Alt+1-8)
6. ✅ Error boundaries catch errors
7. ✅ Toast notifications appear

### Accessibility Testing

```bash
npx axe-cli http://localhost:5173 --exit
```

**WCAG 2.1 AA Compliance**:
- ✅ Color contrast: 21:1 (white on black)
- ✅ Keyboard navigation
- ✅ ARIA labels
- ✅ Focus indicators
- ✅ Screen reader support

---

## 🏗️ Building for Production

```bash
npm run build
```

**Output**:
- `dist/` folder with optimized assets
- Bundle Size: ~852 KB
- Gzipped Size: ~241 KB

### Preview Production Build

```bash
npm run preview
```

---

## 📚 Additional Resources

- **Project Documentation**: `docs/04_MVP_Development/implementation/phase_2_frontend/`
- **User Flows**: [USER_FLOWS.md](../docs/USER_FLOWS.md)
- **Testing Checklist**: [TESTING_CHECKLIST.md](../docs/TESTING_CHECKLIST.md)

### External Documentation
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/ui Components](https://ui.shadcn.com)
- [TanStack Query](https://tanstack.com/query/latest)
- [Recharts](https://recharts.org/en-US/)

---

## 🚀 Current Project Status

**Phase 4 Integration (October 29, 2025)**:
- ✅ Frontend foundation complete (Phase 2)
- ✅ Backend architecture complete (Phase 3)
- 🚀 **Phase 4 PO Validation Complete** - Ready for backend integration
- ⏳ Next: Connect frontend to FastAPI backend (55 hours, 9 stories)

**Key Phase 4 Updates**:
- React Context API for global state (eliminates prop drilling)
- WCAG 2.1 Level AA accessibility compliance
- Comprehensive error handling (401, 404, 422, 429, 500, network)
- Real WebSocket integration (replacing mock setTimeout)
- Parameter validation across all components

**Integration Status**:
- Current: Frontend uses mock data (7 JSON files in `src/mocks/`)
- Phase 4: Will connect to FastAPI backend at `http://localhost:8000`
- See: `docs/04_MVP_Development/implementation/phase_4_integration/PHASE4_HANDOFF.md`

---

**Last Updated**: October 29, 2025
**Version**: 1.0.0
**Status**: Phase 2 Complete ✅ | Phase 4 Ready 🚀
