/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f0518', // Deep purple-black
          card: '#1a0b2e', // Deep purple
          border: '#3b1f5f', // Purple border
        },
        primary: {
          400: '#22d3ee', // Cyan-400
          500: '#06b6d4', // Cyan-500
          600: '#0891b2', // Cyan-600
        },
        accent: {
          pink: '#f472b6',
          purple: '#c084fc',
          amber: '#fbbf24',
        },
        glass: 'rgba(255, 255, 255, 0.1)',
        'glass-hover': 'rgba(255, 255, 255, 0.15)',
      },
      fontFamily: {
        sans: ['Outfit', 'sans-serif'], // More modern font
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gradient-x': 'gradient-x 15s ease infinite',
        'spin-slow': 'spin 8s linear infinite',
        'bounce-slow': 'bounce 3s infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
      },
      backgroundImage: {
        'mesh': 'radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%)',
      },
    },
  },
  plugins: [],
}
