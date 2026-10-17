/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        sage: {
          50: '#F2F6F4',
          100: '#E4ECE7',
          200: '#C9D9CF',
          300: '#A4C0B0',
          400: '#7AA38D',
          500: '#56846C',
          600: '#436B56',
          700: '#355444',
          800: '#2C4337',
          900: '#24372D',
        },
        blush: {
          50: '#FAF5F5',
          100: '#F5EBEB',
          200: '#ECD5D5',
          300: '#DFB5B5',
          400: '#CE8D8D',
          500: '#BA6B6B',
          600: '#A15151',
          700: '#834040',
          800: '#6D3737',
          900: '#5A3131',
        },
        lavender: {
          50: '#F6F5FA',
          100: '#ECE9F4',
          200: '#DDD8EB',
          300: '#C5BDDD',
          400: '#A79BCB',
          500: '#8B7BB8',
          600: '#725FA2',
          700: '#5E4E86',
          800: '#4F426F',
          900: '#42385C',
        }
      },
    },
  },
  plugins: [],
};
