# Tailwind CSS v4 Configuration Guide

## 🎨 What's New in Tailwind v4

### CSS-First Configuration
Tailwind v4 introduces a revolutionary CSS-first approach using the `@theme` directive. No more JavaScript config files!

### Key Changes from v3 to v4:
1. **No `tailwind.config.js`** - Configuration now lives in CSS
2. **`@theme` directive** - Define your design system in CSS
3. **CSS Variables** - Native CSS custom properties
4. **Better Performance** - Faster builds and smaller bundles
5. **Modern CSS Features** - OKLCH colors, container queries, etc.

---

## 📁 File Structure

```
frontend/
├── src/
│   └── app/
│       └── globals.css          # Main Tailwind v4 config
├── postcss.config.mjs           # PostCSS setup
└── package.json                 # Dependencies
```

---

## 🎨 Design System Overview

### Color Palette

Our design system uses a futuristic purple-based theme:

```css
Primary:     #a855f7 (Purple)
Secondary:   #1e293b (Slate)
Accent:      #8b5cf6 (Violet)
Success:     #10b981 (Green)
Warning:     #f59e0b (Amber)
Danger:      #ef4444 (Red)
Info:        #3b82f6 (Blue)
```

### Using Colors in Components

```tsx
// Background colors
<div className="bg-primary">
<div className="bg-secondary">
<div className="bg-accent">

// Text colors
<span className="text-primary">
<span className="text-success">
<span className="text-warning">

// Borders
<div className="border-primary">
<div className="border-destructive">
```

---

## 🎭 Custom Utilities

### Glass Effects

```tsx
// Basic glass effect
<div className="glass">
  Glassmorphism effect
</div>

// Glass with hover
<div className="glass glass-hover">
  Interactive glass
</div>

// Strong glass
<div className="glass-strong">
  More opaque glass
</div>
```

### Glow Effects

```tsx
// Purple glow (default)
<div className="glow">

// Large purple glow
<div className="glow-lg">

// Colored glows
<div className="glow-green">
<div className="glow-red">
<div className="glow-blue">
```

### Gradient Text

```tsx
// Purple gradient text
<h1 className="gradient-text">
  Amazing Title
</h1>

// Blue gradient
<h2 className="gradient-text-blue">
  Cool Subtitle
</h2>

// Green gradient
<span className="gradient-text-green">
  Success!
</span>
```

### Gradient Backgrounds

```tsx
// Purple gradient background
<div className="gradient-bg">

// Purple to pink
<div className="gradient-bg-purple">

// Blue to cyan
<div className="gradient-bg-blue">
```

---

## ✨ Animations

### Available Animations

```tsx
// Fade animations
<div className="animate-[fade-in]">Fade In</div>
<div className="animate-[fade-out]">Fade Out</div>

// Slide animations
<div className="animate-[slide-in-right]">Slide from Right</div>
<div className="animate-[slide-in-left]">Slide from Left</div>
<div className="animate-[slide-in-up]">Slide from Bottom</div>
<div className="animate-[slide-in-down]">Slide from Top</div>

// Scale animation
<div className="animate-[scale-in]">Scale In</div>

// Special effects
<div className="animate-[pulse-glow]">Pulsing Glow</div>
<div className="shimmer">Shimmer Effect</div>
<div className="animate-[spin-slow]">Slow Spin</div>
<div className="animate-[bounce-subtle]">Subtle Bounce</div>
```

### Custom Animation Example

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  className="glass glow animate-[fade-in]"
>
  Combined Framer Motion + Tailwind
</motion.div>
```

---

## 🎯 Component Patterns

### Button Patterns

```tsx
// Primary button
<button className="btn-primary">
  Click Me
</button>

// Secondary button
<button className="btn-secondary">
  Secondary
</button>

// Ghost button
<button className="btn-ghost">
  Ghost
</button>

// Custom button with utilities
<button className="glass glass-hover px-6 py-3 rounded-lg glow">
  Futuristic Button
</button>
```

### Card Patterns

```tsx
// Basic card
<div className="card-base p-6">
  <h3>Card Title</h3>
  <p>Card content</p>
</div>

// Interactive card
<div className="card-base p-6 glass-hover card-hover">
  Hover for effect
</div>

// Glowing card
<div className="card-base p-6 glow">
  Glowing card
</div>
```

### Input Patterns

```tsx
// Standard input
<input 
  className="input-field" 
  placeholder="Enter text..."
/>

// With icon
<div className="relative">
  <input className="input-field pl-10" />
  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2" />
</div>
```

---

## 🎨 Border Radius System

```tsx
// Radius values
<div className="rounded-sm">   {/* 0.375rem */}
<div className="rounded-md">   {/* 0.5rem */}
<div className="rounded-lg">   {/* 0.75rem */}
<div className="rounded-xl">   {/* 1rem */}
<div className="rounded-2xl">  {/* 1.5rem */}
<div className="rounded-full"> {/* 9999px */}
```

---

## 🎭 Shadow System

```tsx
// Using glow effects
<div className="shadow-[0_0_20px_rgba(168,85,247,0.4)]">
  Custom purple glow
</div>

// Using utility classes
<div className="glow">Purple glow</div>
<div className="glow-lg">Large glow</div>
<div className="glow-green">Green glow</div>
```

---

## 📱 Responsive Design

### Breakpoints

```tsx
// Mobile first approach
<div className="
  text-sm          // Mobile
  md:text-base     // Tablet (768px+)
  lg:text-lg       // Desktop (1024px+)
  xl:text-xl       // Large (1280px+)
  2xl:text-2xl     // Extra large (1536px+)
">
  Responsive text
</div>
```

### Container Queries (New in v4)

```tsx
<div className="@container">
  <div className="@md:grid-cols-2 @lg:grid-cols-3">
    Container query responsive
  </div>
</div>
```

---

## 🌙 Dark Mode

Dark mode is the default theme. Light mode can be toggled:

```tsx
// In your component
const { theme, toggleTheme } = useThemeStore()

<button onClick={toggleTheme}>
  {theme === 'dark' ? <Sun /> : <Moon />}
</button>
```

Light mode styles are automatically applied via `prefers-color-scheme` media query.

---

## ♿ Accessibility Features

### Focus Visible

```tsx
// Add focus ring to interactive elements
<button className="focus-ring">
  Accessible button
</button>

// Custom focus style
<a className="focus-visible:ring-2 focus-visible:ring-primary">
  Accessible link
</a>
```

### Reduced Motion

The configuration automatically respects `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  /* All animations become instant */
}
```

### High Contrast

```css
@media (prefers-contrast: high) {
  /* Enhanced contrast styles */
}
```

---

## 🎨 Advanced Patterns

### Glassmorphism Card

```tsx
<div className="
  glass
  glass-hover
  glow
  rounded-2xl
  p-6
  backdrop-blur-xl
  border
  border-white/10
">
  <h3 className="gradient-text text-2xl mb-4">
    Futuristic Card
  </h3>
  <p className="text-gray-300">
    Beautiful glassmorphism effect
  </p>
</div>
```

### Animated Stat Card

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  className="
    card-base
    p-6
    glow
    hover:glow-lg
    transition-all
    duration-300
    hover:scale-105
  "
>
  <div className="flex items-center justify-between mb-4">
    <div className="p-3 rounded-xl bg-gradient-bg-purple">
      <Icon className="w-6 h-6" />
    </div>
    <span className="text-green-400 text-sm font-medium">
      +12%
    </span>
  </div>
  <h4 className="text-gray-400 text-sm mb-1">Total Users</h4>
  <p className="text-3xl font-bold">12,345</p>
</motion.div>
```

### Interactive Table Row

```tsx
<tr className="
  border-b
  border-white/5
  hover:bg-white/5
  transition-colors
  group
">
  <td className="py-4 px-6">
    <span className="group-hover:text-primary transition-colors">
      Project Name
    </span>
  </td>
</tr>
```

---

## 🛠️ Customization

### Adding Custom Colors

Edit `globals.css`:

```css
@theme {
  --color-brand: #ff6b6b;
  --color-brand-foreground: #ffffff;
}
```

Use in components:

```tsx
<div className="bg-[--color-brand] text-[--color-brand-foreground]">
  Custom brand color
</div>
```

### Adding Custom Animations

```css
@theme {
  @keyframes my-custom-animation {
    from {
      transform: scale(0);
    }
    to {
      transform: scale(1);
    }
  }
  
  --animate-my-custom: my-custom-animation 0.3s ease-out;
}
```

Use it:

```tsx
<div className="animate-[my-custom-animation]">
  Custom animation
</div>
```

---

## 📊 Performance Tips

### 1. Use CSS Variables for Dynamic Values

```tsx
// Instead of inline styles
<div style={{ color: dynamicColor }}>

// Use CSS variables
<div className="text-[--my-color]" style={{ '--my-color': dynamicColor }}>
```

### 2. Leverage @layer for Organization

```css
@layer utilities {
  .my-utility {
    /* Custom utility */
  }
}
```

### 3. Use Arbitrary Values Sparingly

```tsx
// Good - uses design system
<div className="p-6 rounded-xl">

// Avoid unless necessary
<div className="p-[23px] rounded-[13px]">
```

---

## 🐛 Troubleshooting

### Styles Not Applying?

1. **Check import order** in `globals.css`:
```css
@import "tailwindcss"; // Must be first
```

2. **Clear Next.js cache**:
```bash
rm -rf .next
npm run dev
```

3. **Check PostCSS config**:
```js
plugins: {
  '@tailwindcss/postcss': {},
}
```

### Build Errors?

```bash
# Reinstall dependencies
rm -rf node_modules .next
npm install --legacy-peer-deps
npm run build
```

---

## 📚 Resources

- [Tailwind CSS v4 Alpha Docs](https://tailwindcss.com/docs)
- [Tailwind CSS Discord](https://discord.gg/tailwindcss)
- [Tailwind Play](https://play.tailwindcss.com)

---

## ✅ Best Practices

1. **Use design system colors** instead of arbitrary colors
2. **Leverage utility classes** for consistency
3. **Combine with Framer Motion** for complex animations
4. **Test responsiveness** at all breakpoints
5. **Check accessibility** with screen readers
6. **Use semantic HTML** with Tailwind classes
7. **Keep animations subtle** for professional feel
8. **Test in dark/light modes**

---

**Updated**: October 2025
**Tailwind Version**: v4 (CSS-first)
**Status**: Production Ready ✅
