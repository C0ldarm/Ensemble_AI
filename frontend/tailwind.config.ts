import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class", 
  theme: {
    extend: {
      colors: {
        // Кастомні кольори для світлої теми
        light: {
          bg: "#ffffff",
          surface: "#f9fafb",
          border: "#e5e7eb",
          text: "#1f2937",
          textSecondary: "#6b7280",
        }
      }
    },
  },
  plugins: [],
};
export default config;