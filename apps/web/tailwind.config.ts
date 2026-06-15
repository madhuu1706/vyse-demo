import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0c",
        panel: "#111114",
        border: "#1f1f24",
        muted: "#8b8b94",
        fg: "#ededf0",
        accent: "#6366f1",
        viral: "#f43f5e",
        evergreen: "#10b981",
        sleeper: "#f59e0b",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
} satisfies Config;
