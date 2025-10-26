/** @type {import('tailwindcss').Config} */
import colors from '@tailwindcss/colors'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gray: colors.gray,
        blue: colors.blue,
      },
    },
  },
  plugins: [],
}

