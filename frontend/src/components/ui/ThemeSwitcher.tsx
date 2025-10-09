'use client';

import { useTheme } from '@/contexts/ThemeContext';
import { getAllThemes } from '@/lib/themes';
import { Check } from 'lucide-react';
import { ThemeId } from '@/types/theme';

export function ThemeSwitcher() {
  const { themeId, setTheme } = useTheme();
  const themes = getAllThemes();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {themes.map((theme) => {
        const isActive = themeId === theme.id;
        
        return (
          <button
            key={theme.id}
            onClick={() => setTheme(theme.id as ThemeId)}
            className={`
              relative group rounded-xl border-2 transition-all duration-300
              ${isActive 
                ? 'border-white/50 shadow-lg scale-105' 
                : 'border-white/10 hover:border-white/30 hover:scale-102'
              }
            `}
          >
            {/* Theme Preview */}
            <div className="p-4 space-y-4">
              {/* Color Preview */}
              <div 
                className="h-24 rounded-lg relative overflow-hidden"
                style={{ background: theme.gradients.bodyGradient }}
              >
                <div className="absolute inset-0 flex items-center justify-center gap-2">
                  <div
                    className="w-8 h-8 rounded-full shadow-lg"
                    style={{ 
                      backgroundColor: theme.preview.primaryColor,
                      boxShadow: theme.shadows.glow 
                    }}
                  />
                  <div
                    className="w-8 h-8 rounded-full shadow-lg"
                    style={{ 
                      backgroundColor: theme.preview.secondaryColor,
                      boxShadow: theme.shadows.glowSecondary 
                    }}
                  />
                </div>
                
                {/* Active Check Mark */}
                {isActive && (
                  <div className="absolute top-2 right-2 bg-white rounded-full p-1">
                    <Check className="w-4 h-4 text-black" />
                  </div>
                )}
              </div>

              {/* Theme Info */}
              <div className="text-left">
                <h3 className="font-semibold text-lg text-white">
                  {theme.name}
                </h3>
                <p className="text-sm text-white/60 mt-1">
                  {theme.description}
                </p>
              </div>

              {/* Color Swatches */}
              <div className="flex gap-2">
                <div
                  className="w-6 h-6 rounded border border-white/20"
                  style={{ backgroundColor: theme.preview.primaryColor }}
                  title="Primary Color"
                />
                <div
                  className="w-6 h-6 rounded border border-white/20"
                  style={{ backgroundColor: theme.preview.secondaryColor }}
                  title="Secondary Color"
                />
                <div
                  className="w-6 h-6 rounded border border-white/20"
                  style={{ backgroundColor: theme.colors.success }}
                  title="Success Color"
                />
                <div
                  className="w-6 h-6 rounded border border-white/20"
                  style={{ backgroundColor: theme.colors.warning }}
                  title="Warning Color"
                />
              </div>
            </div>

            {/* Hover Effect */}
            <div 
              className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-10 transition-opacity pointer-events-none"
              style={{ background: theme.gradients.primaryGradient }}
            />
          </button>
        );
      })}
    </div>
  );
}
