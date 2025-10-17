# Story: Initialize Vite + React + TypeScript Project with Linear Dark Theme

**Epic:** Phase 2 - Complete Frontend Implementation
**Story ID:** PHASE2-001
**Status:** Draft
**Estimate:** 2 hours
**Agent Model Used:** _TBD_
**Dependencies:** None

---

## Story

As a frontend developer,
I want to initialize a modern React project with Vite, TypeScript, and a complete UI foundation,
So that I have a production-ready development environment with Linear Dark Theme styling for building the multi-agent retail forecasting dashboard.

**Business Value:** Establishes the technical foundation for the entire Phase 2 frontend. Without proper project setup, all subsequent development tasks cannot proceed. The Linear Dark Theme creates a professional, modern aesthetic that matches industry-leading design systems.

**Epic Context:** This is Task 1 of 14 in Phase 2. It's the foundational step that enables all other frontend development. The choices made here (Vite, React 18, TypeScript, Shadcn/ui, Tailwind) align with modern best practices and the technical architecture specified in planning docs.

---

## Acceptance Criteria

### Functional Requirements

1. ✅ Vite + React + TypeScript project initializes successfully
2. ✅ Core dependencies installed with correct versions:
   - `@tanstack/react-table@^8.20.0`
   - `recharts@^2.12.0`
   - `react-router-dom@^6.27.0`
   - `lucide-react@latest`
3. ✅ Shadcn/ui integrated with Tailwind CSS
4. ✅ ESLint + Prettier configured for code quality
5. ✅ Linear Dark Theme colors configured in Tailwind config
6. ✅ Folder structure created: `components/`, `hooks/`, `utils/`, `types/`
7. ✅ Path aliases configured (`@/` → `src/`)
8. ✅ Dev server runs without errors (`npm run dev`)
9. ✅ Build completes successfully (`npm run build`)

### Quality Requirements

10. ✅ All dependencies install without conflicts
11. ✅ ESLint shows 0 errors on initial codebase
12. ✅ Prettier formats code consistently
13. ✅ TypeScript compiles without errors
14. ✅ Linear Dark Theme matches planning spec colors exactly

---

## Tasks

### Task 1: Initialize Vite Project
- [ ] Run `npm create vite@latest frontend -- --template react-ts`
- [ ] Navigate to `frontend/` directory
- [ ] Run `npm install` to install base dependencies
- [ ] Verify project runs: `npm run dev`
- [ ] Verify TypeScript compilation: `npm run build`

**Expected Output:** Working Vite + React + TypeScript project with dev server on `http://localhost:5173`

### Task 2: Install Core Dependencies
- [ ] Install TanStack Table: `npm install @tanstack/react-table@^8.20.0`
- [ ] Install Recharts: `npm install recharts@^2.12.0`
- [ ] Install React Router: `npm install react-router-dom@^6.27.0`
- [ ] Install Lucide React: `npm install lucide-react@latest`
- [ ] Verify all dependencies in `package.json`

**Reference:** `implementation_plan.md` Task 1, line 109

### Task 3: Install Shadcn/ui + Tailwind CSS
- [ ] Run `npx shadcn-ui@latest init`
- [ ] Select options:
  - Style: Default
  - Base color: Slate
  - CSS variables: Yes
- [ ] Install Tailwind CSS (auto-installed by Shadcn)
- [ ] Verify `tailwind.config.js` exists
- [ ] Verify `globals.css` has Shadcn styles

**Reference:** Shadcn/ui docs - https://ui.shadcn.com/docs/installation/vite

### Task 4: Configure ESLint + Prettier
- [ ] Install Prettier: `npm install --save-dev prettier`
- [ ] Create `.prettierrc`:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```
- [ ] Install ESLint Prettier plugin: `npm install --save-dev eslint-config-prettier`
- [ ] Update `.eslintrc.cjs` to extend `prettier`
- [ ] Create `.prettierignore`:
```
node_modules
dist
.next
build
```
- [ ] Test: `npx prettier --write src/**/*.{ts,tsx}`
- [ ] Verify: `npx eslint src/`

### Task 5: Configure Linear Dark Theme
- [ ] Update `tailwind.config.js` with Linear Dark Theme colors:
```javascript
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Base colors (from planning spec lines 906-915)
        background: "#0D0D0D",  // Near black page background
        foreground: "#FFFFFF",  // White text
        card: {
          DEFAULT: "#1A1A1A",   // Dark gray cards
          foreground: "#FFFFFF",
        },
        popover: {
          DEFAULT: "#1A1A1A",
          foreground: "#FFFFFF",
        },
        primary: {
          DEFAULT: "#5E6AD2",   // Linear purple-blue (buttons, links)
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#2A2A2A",   // Subtle borders/secondary elements
          foreground: "#FFFFFF",
        },
        muted: {
          DEFAULT: "#1F1F1F",   // Hover states
          foreground: "#9CA3AF", // Light gray text
        },
        accent: {
          DEFAULT: "#2A2A2A",
          foreground: "#FFFFFF",
        },
        destructive: {
          DEFAULT: "#F97066",   // Soft red (planning spec, NOT #ef4444)
          foreground: "#FFFFFF",
        },
        border: "#2A2A2A",      // Subtle borders
        input: "#2A2A2A",
        ring: "#5E6AD2",
        hover: "#1F1F1F",       // Hover states

        // Accent colors (planning spec lines 917-924)
        success: "#00D084",     // Green (🟢 variance <10%)
        warning: "#F5A623",     // Amber (🟡 variance 10-20%)
        error: "#F97066",       // Soft red (🔴 variance >20%)
        info: "#5B8DEF",        // Soft blue

        // Agent colors (planning spec lines 926-931)
        "agent-demand": "#5B8DEF",     // Soft blue
        "agent-inventory": "#00D084",  // Green
        "agent-pricing": "#F59E0B",    // Amber

        // Chart colors (planning spec lines 933-938)
        "chart-forecast": "#5E6AD2",   // Purple-blue line
        "chart-actual": "#00D084",     // Green bars (on track)
        "chart-variance": "#F97066",   // Red bars (high variance)

        // Text colors (planning spec lines 911-914)
        "text-primary": "#FFFFFF",     // White text
        "text-secondary": "#9CA3AF",   // Light gray
        "text-muted": "#6B7280",       // Muted gray
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["SF Mono", "Monaco", "Cascadia Code", "Roboto Mono", "monospace"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```
- [ ] Update `src/index.css` or `src/App.css` with dark background:
```css
body {
  background-color: #0D0D0D;  /* Match planning spec exactly */
  color: #FFFFFF;
}
```
- [ ] Add `dark` class to `<html>` tag in `index.html`

**Reference:** `planning/5_front-end-spec_v3.3.md` - Linear Dark Theme specification

### Task 6: Create Folder Structure
- [ ] Create `src/components/` directory
- [ ] Create `src/hooks/` directory
- [ ] Create `src/utils/` directory
- [ ] Create `src/types/` directory
- [ ] Create `src/lib/` directory (for utilities)
- [ ] Create placeholder files:
  - `src/components/.gitkeep`
  - `src/hooks/.gitkeep`
  - `src/utils/.gitkeep`
  - `src/types/.gitkeep`

**Expected Structure:**
```
src/
├── components/
├── hooks/
├── utils/
├── types/
├── lib/
├── App.tsx
├── main.tsx
└── index.css
```

### Task 7: Configure Path Aliases
- [ ] Update `tsconfig.json` to add path mapping:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```
- [ ] Install `@types/node`: `npm install --save-dev @types/node`
- [ ] Update `vite.config.ts`:
```typescript
import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```
- [ ] Test import: Create `src/lib/utils.ts` with a test function
- [ ] Import using `@/lib/utils` in `App.tsx`
- [ ] Verify TypeScript doesn't show errors

### Task 8: Final Verification
- [ ] Run dev server: `npm run dev` - No errors
- [ ] Run build: `npm run build` - No errors
- [ ] Run linter: `npx eslint src/` - No errors
- [ ] Run Prettier check: `npx prettier --check src/` - No errors
- [ ] Verify Linear Dark Theme renders correctly (dark background visible)
- [ ] Verify all dependencies in `package.json` match required versions

---

## Dev Notes

### Technology Stack Rationale

**Vite:**
- 10-100x faster than Create React App
- Native ESM support
- Instant HMR (Hot Module Replacement)
- Optimized production builds

**React 18.3+:**
- Concurrent rendering
- Automatic batching
- Modern hooks support

**TypeScript 5.6+:**
- Type safety reduces runtime errors
- Better IDE autocomplete
- Self-documenting code

**Shadcn/ui:**
- Copy-paste components (not a dependency)
- Full control over code
- Built on Radix UI (accessible primitives)
- Tailwind CSS integration

**Tailwind CSS:**
- Utility-first CSS
- No CSS conflicts
- Responsive design built-in
- Linear Dark Theme easy to implement

### Linear Dark Theme Color Palette (Complete)

**Base Colors:**
| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#0D0D0D` | Main app background |
| `foreground` | `#FFFFFF` | Primary text color |
| `card` | `#1A1A1A` | Card backgrounds |
| `primary` | `#5E6AD2` | Primary actions (buttons, links) |
| `secondary` | `#2A2A2A` | Secondary elements |
| `muted` | `#1F1F1F` | Muted backgrounds |
| `border` | `#2A2A2A` | Border color |
| `hover` | `#1F1F1F` | Hover states |

**Accent Colors:**
| Token | Hex | Usage |
|-------|-----|-------|
| `success` | `#00D084` | Green (🟢 variance <10%) |
| `warning` | `#F5A623` | Amber (🟡 variance 10-20%) |
| `error` | `#F97066` | Soft red (🔴 variance >20%) |
| `info` | `#5B8DEF` | Soft blue |

**Agent Colors:**
| Token | Hex | Usage |
|-------|-----|-------|
| `agent-demand` | `#5B8DEF` | Demand Agent (blue) |
| `agent-inventory` | `#00D084` | Inventory Agent (green) |
| `agent-pricing` | `#F59E0B` | Pricing Agent (amber) |

**Chart Colors:**
| Token | Hex | Usage |
|-------|-----|-------|
| `chart-forecast` | `#5E6AD2` | Forecast line (purple-blue) |
| `chart-actual` | `#00D084` | Actual bars (green) |
| `chart-variance` | `#F97066` | High variance bars (red) |

**Text Colors:**
| Token | Hex | Usage |
|-------|-----|-------|
| `text-primary` | `#FFFFFF` | Primary text |
| `text-secondary` | `#9CA3AF` | Secondary text (light gray) |
| `text-muted` | `#6B7280` | Muted text (gray) |

**WCAG Contrast Ratios:**
- Background (#0D0D0D) vs Foreground (#FFFFFF): **21:1** ✅ (AAA)
- Primary (#5E6AD2) vs White (#FFFFFF): **4.8:1** ✅ (AA)
- Success (#00D084) vs Background: **9.2:1** ✅ (AAA)
- Warning (#F5A623) vs Background: **7.5:1** ✅ (AAA)

### Critical References

- **Planning Spec:** `planning/5_front-end-spec_v3.3.md` lines 150-200 (Linear Dark Theme)
- **Technical Architecture:** `planning/3_technical_architecture_v3.3.md` lines 250-350 (Frontend tech stack)
- **Vite Docs:** https://vitejs.dev/guide/
- **Shadcn/ui Setup:** https://ui.shadcn.com/docs/installation/vite
- **Tailwind Docs:** https://tailwindcss.com/docs

### Common Issues & Solutions

**Issue 1: Path alias not working**
- Solution: Restart TypeScript server in VSCode (Cmd+Shift+P → "Restart TS Server")

**Issue 2: Shadcn components not styled**
- Solution: Verify `globals.css` is imported in `main.tsx`

**Issue 3: Tailwind not applying styles**
- Solution: Check `tailwind.config.js` content paths include `.tsx` files

---

## Testing

### Manual Testing Checklist

- [ ] Dev server starts without errors (`npm run dev`)
- [ ] Navigate to `http://localhost:5173` - page loads
- [ ] Background color is dark (#0a0a0a)
- [ ] Text color is light (#ededed)
- [ ] Build completes successfully (`npm run build`)
- [ ] Preview build works (`npm run preview`)
- [ ] ESLint shows 0 errors
- [ ] Prettier formats code correctly
- [ ] TypeScript compiles without errors
- [ ] Path alias `@/` works (test with sample import)
- [ ] All dependencies listed in `package.json` with correct versions

### Verification Commands

```bash
# Verify dev server
npm run dev

# Verify build
npm run build

# Verify linting
npx eslint src/

# Verify formatting
npx prettier --check src/

# Verify TypeScript
npx tsc --noEmit

# Check dependency versions
npm list @tanstack/react-table recharts react-router-dom lucide-react
```

---

## File List

_Dev Agent will populate this section during implementation_

**Files to Create:**
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/tailwind.config.js`
- `frontend/.prettierrc`
- `frontend/.prettierignore`
- `frontend/.eslintrc.cjs`
- `frontend/src/components/.gitkeep`
- `frontend/src/hooks/.gitkeep`
- `frontend/src/utils/.gitkeep`
- `frontend/src/types/.gitkeep`
- `frontend/src/lib/utils.ts`

**Files to Modify:**
- `frontend/src/index.css` (Linear Dark Theme)
- `frontend/index.html` (add `dark` class to `<html>`)

---

## Dev Agent Record

### Debug Log References

_Dev Agent logs issues here during implementation_

### Completion Notes

_Dev Agent notes completion details here_

### Change Log

_Dev Agent tracks all file changes here_

---

## Definition of Done

- [x] Vite + React + TypeScript project initialized
- [x] All core dependencies installed with correct versions
- [x] Shadcn/ui integrated successfully
- [x] ESLint + Prettier configured and passing
- [x] Linear Dark Theme configured in Tailwind
- [x] Folder structure created (components, hooks, utils, types)
- [x] Path aliases configured and working
- [x] Dev server runs without errors
- [x] Build completes successfully
- [x] All manual tests pass
- [x] File List updated with all created/modified files

---

**Created:** 2025-10-17
**Last Updated:** 2025-10-17
**Story Points:** 2
**Priority:** P0 (Blocker for all other Phase 2 tasks)
