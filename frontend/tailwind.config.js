/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        surface: "#12121a",
        primary: "#00f0ff", // Neon Cyan
        secondary: "#7000ff", // Neon Purple
        accent: "#ff003c", // Neon Red
        success: "#00ff9f", // Neon Green
        warning: "#fcee0a", // Neon Yellow
        text: {
          primary: "#ffffff",
          secondary: "#9ca3af",
          muted: "#6b7280",
        },
        border: "rgba(255, 255, 255, 0.1)",
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', "monospace"],
        sans: ['"Inter"', "sans-serif"],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'cyber-grid': "url('/grid.svg')", // We'll need to add this asset or use CSS
      },
    },
  },
  plugins: [],
};
