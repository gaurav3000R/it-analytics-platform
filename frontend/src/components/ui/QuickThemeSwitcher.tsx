'use client';

import { useTheme } from '@/contexts/ThemeContext';
import { getAllThemes } from '@/lib/themes';
import { Palette } from 'lucide-react';
import { useState } from 'react';
import { ThemeId } from '@/types/theme';

export function QuickThemeSwitcher() {
  const { themeId, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const themes = getAllThemes();

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
        title="Change Theme"
      >
        <Palette className="w-5 h-5" />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-72 bg-black/95 backdrop-blur-xl border border-white/20 rounded-xl shadow-2xl z-50 overflow-hidden">
            <div className="p-3 border-b border-white/10">
              <h3 className="font-semibold text-sm text-white">Select Theme</h3>
            </div>
            
            <div className="p-2 space-y-1">
              {themes.map((theme) => {
                const isActive = themeId === theme.id;
                
                return (
                  <button
                    key={theme.id}
                    onClick={() => {
                      setTheme(theme.id as ThemeId);
                      setIsOpen(false);
                    }}
                    className={`
                      w-full flex items-center gap-3 p-3 rounded-lg transition-all
                      ${isActive 
                        ? 'bg-white/10 border border-white/20' 
                        : 'hover:bg-white/5 border border-transparent'
                      }
                    `}
                  >
                    {/* Color Preview */}
                    <div className="flex gap-1">
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: theme.preview.primaryColor }}
                      />
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: theme.preview.secondaryColor }}
                      />
                    </div>

                    {/* Theme Name */}
                    <div className="flex-1 text-left">
                      <div className="font-medium text-sm text-white">
                        {theme.name}
                      </div>
                    </div>

                    {/* Active Indicator */}
                    {isActive && (
                      <div 
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: theme.preview.primaryColor }}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
