import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Heritage Teal Ink & Cream Palette (Comfortable Harmonious Theme)
        tealInk: {
          DEFAULT: '#175A67',
          hover: '#0F3D47',
          dark: '#0B2E36',
          light: '#237382',
          soft: '#2A707C',
          mist: '#E2ECED',
          mistHover: '#D5E4E6',
          mistBorder: 'rgba(23, 90, 103, 0.2)',
        },
        cream: {
          DEFAULT: '#EAE3DE',
          paper: '#EAE3DE',
          light: '#F4EFEA',
          card: 'rgba(255, 255, 255, 0.82)',
        },
        // Warm glass neutral background
        bg: {
          DEFAULT: '#EAE3DE',
          surface: 'rgba(255, 255, 255, 0.78)',
          elevated: 'rgba(255, 255, 255, 0.90)',
        },
        // Deep typography
        text: {
          DEFAULT: '#101410',
          muted: '#4A5B5E',
          faint: '#7B8E91',
        },
        // Frosted glass borders
        border: {
          DEFAULT: 'rgba(224, 230, 230, 0.75)',
          subtle: 'rgba(234, 240, 240, 0.8)',
          glass: 'rgba(255, 255, 255, 0.85)',
        },
        // Primary Teal Ink accents
        accent: {
          DEFAULT: '#175A67',
          light: '#E2ECED',
          dark: '#0F3D47',
          soft: '#EDF4F5',
          glow: 'rgba(23, 90, 103, 0.25)',
        },
        // Status colors
        status: {
          success: '#175A67',
          successSoft: 'rgba(226, 236, 237, 0.90)',
          warning: '#B45309',
          warningSoft: 'rgba(254, 243, 226, 0.85)',
          danger: '#991B1B',
          dangerSoft: 'rgba(254, 226, 226, 0.85)',
          info: '#1D4ED8',
          infoSoft: 'rgba(219, 234, 254, 0.85)',
          neutral: '#4B5563',
          neutralSoft: 'rgba(243, 244, 246, 0.85)',
        },
        surface: {
          card: 'rgba(255, 255, 255, 0.80)',
          sidebar: 'rgba(255, 255, 255, 0.75)',
        },
        textLabel: {
          primary: '#101410',
          secondary: '#4A5B5E',
          highlight: '#175A67',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['"Inter Tight"', '"Inter"', 'sans-serif'],
        heading: ['"Cormorant Garamond"', '"Playfair Display"', 'Georgia', 'serif'],
        calligraphy: ['"Alex Brush"', 'cursive'],
        caveat: ['"Caveat"', 'cursive'],
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      fontWeight: {
        'medium': '500',
        'semibold': '600',
        'extrabold': '800',
      },
      borderRadius: {
        'sm': '0.375rem',
        'md': '0.5rem',
        'lg': '0.75rem',
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
        'full': '9999px',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(28, 37, 48, 0.05)',
        'glass-sm': '0 4px 16px 0 rgba(28, 37, 48, 0.04)',
        'glass-hover': '0 12px 36px -4px rgba(61, 122, 77, 0.12), 0 0 1px 1px rgba(255, 255, 255, 0.8)',
        'card': '0 8px 32px 0 rgba(28, 37, 48, 0.05)',
        'elevated': '0 16px 40px -8px rgba(28, 37, 48, 0.08)',
      },
    },
  },
  plugins: [],
};

export default config;
