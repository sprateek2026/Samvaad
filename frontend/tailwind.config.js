/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        saffron: {
          50:  '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
        },
        emerald: {
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
        },
        gold: {
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
        },
        slate: {
          850: '#1a2035',
          900: '#0f172a',
          950: '#080f1e',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        card:       '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        raised:     '0 4px 16px rgba(99,102,241,0.10), 0 1px 4px rgba(0,0,0,0.06)',
        modal:      '0 25px 50px rgba(0,0,0,0.18)',
        'indigo-glow': '0 8px 25px rgba(99,102,241,0.22)',
        'saffron-glow': '0 8px 25px rgba(249,115,22,0.22)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.25rem',
        '4xl': '1.5rem',
      },
      animation: {
        'fade-up':    'fadeInUp 0.4s ease-out forwards',
        'scale-in':   'scaleIn 0.3s ease-out forwards',
        'slide-right':'slideInRight 0.3s ease-out forwards',
        'login-card': 'fadeUpCard 0.42s cubic-bezier(0.22, 0.61, 0.36, 1) forwards',
      },
      backgroundImage: {
        'maharashtra-gradient': 'linear-gradient(160deg, #0d1b35 0%, #102a5c 22%, #1a4a8a 42%, #6b2206 64%, #c24a0a 80%, #e8760e 92%, #f5a31a 100%)',
      },
      height: {
        nav: '3.5rem',
      },
      spacing: {
        nav: '3.5rem',
      },
    },
  },
  safelist: [
    { pattern: /^(bg|from|to|text|border)-(indigo|amber|green|red|purple|teal|emerald|orange|rose|blue|gray|slate|saffron|primary|gold)-(50|100|200|400|500|600|700|800)$/ },
    { pattern: /^(bg|text)-(white|black)$/ },
    { pattern: /^opacity-(0|25|50|75|80|100)$/ },
    'bg-gradient-to-br', 'bg-gradient-to-r', 'bg-gradient-to-b',
    'text-white', 'text-black',
  ],
  plugins: [],
}
