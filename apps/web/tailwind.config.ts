import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg:       '#26150B',
        accent:   '#91B2DD',
        card:     '#321C0E',
        border:   '#4A2E18',
        'text-primary': '#F5EDE3',
        'text-muted':   '#9E8A7A',
        'tag-bg': '#3D2415',
        open:     '#6DBF8E',
        closing:  '#E8C468',
        upcoming: '#91B2DD',
        closed:   '#4A3A30',
      },
      fontFamily: {
        serif: ['DM Serif Display', 'Georgia', 'serif'],
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans:  ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '8px',
        chip: '4px',
      },
      animation: {
        'fade-in':   'fadeIn 600ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-dot': 'pulseDot 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseDot: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.4' },
        },
      },
      transitionDuration: {
        '500': '500ms',
      },
      transitionTimingFunction: {
        'effortless': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}

export default config
