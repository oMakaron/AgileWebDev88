/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      animation: {
        'toast-progress': 'shrinkProgress 10s linear forwards'
      },
      keyframes: {
        shrinkProgress: {
          '0%': { width: '100%' },
          '100%': { width: '0%' }
        }
      }
    }
  },
  plugins: [],
};
