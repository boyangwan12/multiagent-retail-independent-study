/** @type {import('tailwindcss').Config} */
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
