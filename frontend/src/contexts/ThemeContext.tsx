'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Theme, ThemeId } from '@/types/theme';
import { getTheme } from '@/lib/themes';

interface ThemeContextType {
  theme: Theme;
  themeId: ThemeId;
  setTheme: (themeId: ThemeId) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'it-analytics-theme';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeId, setThemeId] = useState<ThemeId>('purple');
  const [theme, setThemeState] = useState<Theme>(getTheme('purple'));
  const [mounted, setMounted] = useState(false);

  // Load theme from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ThemeId;
    if (savedTheme && ['purple', 'blue', 'green', 'sunset'].includes(savedTheme)) {
      setThemeId(savedTheme);
      setThemeState(getTheme(savedTheme));
    }
  }, []);

  // Apply theme to DOM
  useEffect(() => {
    if (!mounted) return;

    const root = document.documentElement;
    const currentTheme = getTheme(themeId);

    // Apply CSS variables
    Object.entries(currentTheme.colors).forEach(([key, value]) => {
      const cssVarName = key.replace(/([A-Z])/g, '-$1').toLowerCase();
      root.style.setProperty(`--color-${cssVarName}`, value);
    });

    // Apply gradients
    root.style.setProperty('--gradient-body', currentTheme.gradients.bodyGradient);
    root.style.setProperty('--gradient-primary', currentTheme.gradients.primaryGradient);
    root.style.setProperty('--gradient-secondary', currentTheme.gradients.secondaryGradient);

    // Apply shadows
    root.style.setProperty('--shadow-glow', currentTheme.shadows.glow);
    root.style.setProperty('--shadow-glow-lg', currentTheme.shadows.glowLg);
    root.style.setProperty('--shadow-glow-secondary', currentTheme.shadows.glowSecondary);

    // Set data attribute for theme
    root.setAttribute('data-theme', themeId);
  }, [themeId, mounted]);

  const setTheme = (newThemeId: ThemeId) => {
    setThemeId(newThemeId);
    setThemeState(getTheme(newThemeId));
    localStorage.setItem(THEME_STORAGE_KEY, newThemeId);
  };

  return (
    <ThemeContext.Provider value={{ theme, themeId, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
