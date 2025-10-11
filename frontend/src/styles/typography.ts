// Typography System - 2025-2030 Futuristic Design
// Consistent font sizes, weights, and colors across the application

export const typography = {
  // Display - Extra large headings for hero sections
  display: {
    xl: 'text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight',
    lg: 'text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight',
    md: 'text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight',
    sm: 'text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight',
  },
  
  // Headings - Standard page titles and section headers
  heading: {
    h1: 'text-4xl md:text-5xl font-bold tracking-tight text-gray-900',
    h2: 'text-3xl md:text-4xl font-bold tracking-tight text-gray-900',
    h3: 'text-2xl md:text-3xl font-semibold tracking-tight text-gray-800',
    h4: 'text-xl md:text-2xl font-semibold tracking-tight text-gray-800',
    h5: 'text-lg md:text-xl font-semibold tracking-tight text-gray-700',
    h6: 'text-base md:text-lg font-semibold tracking-tight text-gray-700',
  },
  
  // Body text - Regular content
  body: {
    xl: 'text-xl leading-relaxed text-gray-700',
    lg: 'text-lg leading-relaxed text-gray-700',
    md: 'text-base leading-relaxed text-gray-600',
    sm: 'text-sm leading-relaxed text-gray-600',
    xs: 'text-xs leading-relaxed text-gray-500',
  },
  
  // Labels - Form labels and small headings
  label: {
    lg: 'text-sm font-semibold text-gray-700',
    md: 'text-sm font-medium text-gray-700',
    sm: 'text-xs font-medium text-gray-600',
  },
  
  // Captions - Secondary information
  caption: {
    lg: 'text-sm text-gray-500',
    md: 'text-xs text-gray-500',
    sm: 'text-xs text-gray-400',
  },
  
  // Numbers - Metrics and statistics
  metric: {
    hero: 'text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900',
    xl: 'text-4xl md:text-5xl font-bold tracking-tight text-gray-900',
    lg: 'text-3xl md:text-4xl font-bold tracking-tight text-gray-900',
    md: 'text-2xl md:text-3xl font-bold tracking-tight text-gray-900',
    sm: 'text-xl md:text-2xl font-bold tracking-tight text-gray-800',
  },
  
  // Status and badges
  status: {
    lg: 'text-sm font-semibold',
    md: 'text-xs font-semibold',
    sm: 'text-xs font-medium',
  },
  
  // Code and monospace
  code: {
    lg: 'text-base font-mono text-gray-800',
    md: 'text-sm font-mono text-gray-700',
    sm: 'text-xs font-mono text-gray-600',
  },
  
  // Button text
  button: {
    lg: 'text-base font-semibold',
    md: 'text-sm font-semibold',
    sm: 'text-xs font-medium',
  },
  
  // Card titles
  cardTitle: {
    lg: 'text-xl font-semibold text-gray-900',
    md: 'text-lg font-semibold text-gray-900',
    sm: 'text-base font-semibold text-gray-800',
  },
  
  // Card descriptions
  cardDescription: {
    lg: 'text-base text-gray-600',
    md: 'text-sm text-gray-600',
    sm: 'text-xs text-gray-500',
  },
  
  // Gradient text effects
  gradient: {
    primary: 'bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 bg-clip-text text-transparent',
    success: 'bg-gradient-to-r from-green-600 via-green-500 to-emerald-500 bg-clip-text text-transparent',
    warning: 'bg-gradient-to-r from-orange-600 via-orange-500 to-yellow-500 bg-clip-text text-transparent',
    danger: 'bg-gradient-to-r from-red-600 via-red-500 to-pink-500 bg-clip-text text-transparent',
    cyber: 'bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 bg-clip-text text-transparent',
  },
  
  // Link styles
  link: {
    primary: 'text-blue-600 hover:text-blue-700 font-medium underline-offset-4 hover:underline',
    secondary: 'text-gray-600 hover:text-gray-800 font-medium underline-offset-4 hover:underline',
    subtle: 'text-gray-500 hover:text-gray-700 underline-offset-4 hover:underline',
  },
  
  // Color variants
  colors: {
    primary: 'text-gray-900',
    secondary: 'text-gray-700',
    muted: 'text-gray-500',
    success: 'text-green-600',
    warning: 'text-orange-600',
    danger: 'text-red-600',
    info: 'text-blue-600',
  },
};

// Font family utilities
export const fontFamily = {
  sans: 'font-sans', // Inter/Poppins
  heading: 'font-heading', // Space Grotesk
  mono: 'font-mono', // JetBrains Mono
  body: 'font-body', // Inter
};

// Font weight utilities
export const fontWeight = {
  light: 'font-light', // 300
  normal: 'font-normal', // 400
  medium: 'font-medium', // 500
  semibold: 'font-semibold', // 600
  bold: 'font-bold', // 700
};

// Line height utilities
export const lineHeight = {
  tight: 'leading-tight', // 1.25
  snug: 'leading-snug', // 1.375
  normal: 'leading-normal', // 1.5
  relaxed: 'leading-relaxed', // 1.625
  loose: 'leading-loose', // 2
};

// Letter spacing utilities
export const letterSpacing = {
  tighter: 'tracking-tighter', // -0.05em
  tight: 'tracking-tight', // -0.025em
  normal: 'tracking-normal', // 0
  wide: 'tracking-wide', // 0.025em
  wider: 'tracking-wider', // 0.05em
  widest: 'tracking-widest', // 0.1em
};

// Text alignment utilities
export const textAlign = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
  justify: 'text-justify',
};

// Helper function to combine typography classes
export const combineTypography = (...classes: string[]) => {
  return classes.filter(Boolean).join(' ');
};

export default typography;
