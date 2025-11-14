/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Base colors - now using CSS variables for theme switching
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        hover: "hsl(var(--hover))",

        // Accent colors - remain consistent across themes
        success: "#00D084",     // Green (🟢 variance <10%)
        warning: "#F5A623",     // Amber (🟡 variance 10-20%)
        error: "#F97066",       // Soft red (🔴 variance >20%)
        info: "#5B8DEF",        // Soft blue

        // Agent colors - remain consistent across themes
        "agent-demand": "#5B8DEF",     // Soft blue
        "agent-inventory": "#00D084",  // Green
        "agent-pricing": "#F59E0B",    // Amber

        // Chart colors - remain consistent across themes
        "chart-forecast": "#5E6AD2",   // Purple-blue line
        "chart-actual": "#00D084",     // Green bars (on track)
        "chart-variance": "#F97066",   // Red bars (high variance)

        // Text colors - using CSS variables
        "text-primary": "hsl(var(--text-primary))",
        "text-secondary": "hsl(var(--text-secondary))",
        "text-muted": "hsl(var(--text-muted))",
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
