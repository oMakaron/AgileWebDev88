/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html"],
    safelist: [
    'text-white',
    'text-red-600',
    'text-red-500',
    'bg-red-600',
    'bg-red-500',
    'text-[10px]',
    'font-bold',
    'rounded-full'
  ],
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

