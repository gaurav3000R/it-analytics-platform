export interface ThemeColors {
  background: string;
  foreground: string;
  primary: string;
  primaryForeground: string;
  secondary: string;
  secondaryForeground: string;
  accent: string;
  accentForeground: string;
  muted: string;
  mutedForeground: string;
  destructive: string;
  destructiveForeground: string;
  success: string;
  warning: string;
  info: string;
  border: string;
  input: string;
  ring: string;
  card: string;
  cardForeground: string;
  popover: string;
  popoverForeground: string;
}

export interface ThemeGradients {
  bodyGradient: string;
  primaryGradient: string;
  secondaryGradient: string;
}

export interface ThemeShadows {
  glow: string;
  glowLg: string;
  glowSecondary: string;
}

export interface Theme {
  id: string;
  name: string;
  description: string;
  colors: ThemeColors;
  gradients: ThemeGradients;
  shadows: ThemeShadows;
  preview: {
    primaryColor: string;
    secondaryColor: string;
    backgroundColor: string;
  };
}

export type ThemeId = 'purple' | 'blue' | 'green' | 'sunset';
