/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        comic: {
          bg: "#121212",
          card: "#1E1E1E",
          primary: "#FF5252",
          secondary: "#4ECDC4",
          accent: "#FFD166",
          text: "#F2F2F2",
          muted: "#BBBBBB",
          border: "#333333",
          highlight: "#2E2E2E",
        },
      },
      fontFamily: {
        comic: ['"Comic Neue"', "cursive", "sans-serif"],
        title: ['"Bangers"', "cursive", "sans-serif"],
      },
      boxShadow: {
        comic: "3px 3px 0 rgba(255, 82, 82, 0.7)",
        "comic-lg": "5px 5px 0 rgba(255, 82, 82, 0.7)",
      },
      borderWidth: {
        3: "3px",
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  darkMode: "class",
  daisyui: {
    themes: [
      {
        "comic-dark": {
          primary: "#FF5252",
          secondary: "#4ECDC4",
          accent: "#FFD166",
          neutral: "#2E2E2E",
          "base-100": "#121212",
          "base-200": "#1E1E1E",
          "base-300": "#2A2A2A",
          info: "#3ABFF8",
          success: "#36D399",
          warning: "#FBBD23",
          error: "#F87272",
        },
      },
    ],
  },
};
