/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary:   "#0B2948", // Oxford Navy
        secondary: "#3A4E3E", // Ivy Green
        action:    "#B3925F", // Camel Tweed (buttons / CTAs)
        accent:    "#733A3A", // Oxblood Ink (badges / charts)
        surface:   "#F4F1E8", // Parchment Paper (backgrounds)
        neutral:   "#242628", // Graphite Charcoal (body text)
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
