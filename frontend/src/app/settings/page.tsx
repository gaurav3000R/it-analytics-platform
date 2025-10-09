'use client';

import { ThemeSwitcher } from '@/components/ui/ThemeSwitcher';
import { useTheme } from '@/contexts/ThemeContext';
import { ArrowLeft, Palette, Sparkles, Info } from 'lucide-react';
import Link from 'next/link';

export default function ThemeSettingsPage() {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/"
              className="p-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-3xl lg:text-4xl font-bold text-white flex items-center gap-3">
                <Palette className="w-8 h-8" />
                Theme Settings
              </h1>
              <p className="text-white/60 mt-2">
                Customize your IT Analytics Platform experience with beautiful themes
              </p>
            </div>
          </div>
        </div>

        {/* Current Theme Info */}
        <div className="glass rounded-2xl p-6 border border-white/10">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20">
              <Sparkles className="w-6 h-6 text-purple-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-white mb-2">
                Current Theme: {theme.name}
              </h2>
              <p className="text-white/70 mb-4">
                {theme.description}
              </p>
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded-lg border border-white/20"
                    style={{ 
                      backgroundColor: theme.preview.primaryColor,
                      boxShadow: theme.shadows.glow 
                    }}
                  />
                  <span className="text-sm text-white/70">Primary</span>
                </div>
                <div className="flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded-lg border border-white/20"
                    style={{ 
                      backgroundColor: theme.preview.secondaryColor,
                      boxShadow: theme.shadows.glowSecondary 
                    }}
                  />
                  <span className="text-sm text-white/70">Secondary</span>
                </div>
                <div className="flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded-lg border border-white/20"
                    style={{ backgroundColor: theme.colors.success }}
                  />
                  <span className="text-sm text-white/70">Success</span>
                </div>
                <div className="flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded-lg border border-white/20"
                    style={{ backgroundColor: theme.colors.warning }}
                  />
                  <span className="text-sm text-white/70">Warning</span>
                </div>
                <div className="flex items-center gap-2">
                  <div 
                    className="w-8 h-8 rounded-lg border border-white/20"
                    style={{ backgroundColor: theme.colors.destructive }}
                  />
                  <span className="text-sm text-white/70">Destructive</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Theme Selection */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-white">
              Available Themes
            </h2>
            <div className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-sm font-medium">
              4 Themes
            </div>
          </div>
          <p className="text-white/60">
            Choose a theme that matches your style and workflow
          </p>
        </div>

        {/* Theme Switcher Grid */}
        <ThemeSwitcher />

        {/* Info Section */}
        <div className="glass rounded-2xl p-6 border border-white/10">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-lg bg-blue-500/20">
              <Info className="w-5 h-5 text-blue-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-white mb-2">
                About Themes
              </h3>
              <div className="space-y-2 text-white/70 text-sm">
                <p>
                  • Your theme preference is saved automatically and will persist across sessions
                </p>
                <p>
                  • Each theme is carefully crafted with accessibility in mind
                </p>
                <p>
                  • Themes affect all pages and components throughout the platform
                </p>
                <p>
                  • The theme system uses CSS custom properties for optimal performance
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Theme Preview Samples */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white">
            Component Previews
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Button Preview */}
            <div className="glass rounded-xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold text-white mb-4">Buttons</h3>
              <div className="flex flex-wrap gap-3">
                <button className="btn-primary">
                  Primary Button
                </button>
                <button className="btn-secondary">
                  Secondary Button
                </button>
                <button className="btn-ghost">
                  Ghost Button
                </button>
              </div>
            </div>

            {/* Card Preview */}
            <div className="glass rounded-xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold text-white mb-4">Cards</h3>
              <div className="card-base p-4">
                <h4 className="font-semibold text-white mb-2">Sample Card</h4>
                <p className="text-white/70 text-sm">
                  This is how cards look with the current theme applied.
                </p>
              </div>
            </div>

            {/* Input Preview */}
            <div className="glass rounded-xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold text-white mb-4">Inputs</h3>
              <input 
                type="text" 
                placeholder="Sample input field"
                className="input-field"
              />
            </div>

            {/* Badge Preview */}
            <div className="glass rounded-xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold text-white mb-4">Badges</h3>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-300 text-sm font-medium border border-green-500/30">
                  Success
                </span>
                <span className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-300 text-sm font-medium border border-yellow-500/30">
                  Warning
                </span>
                <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-300 text-sm font-medium border border-red-500/30">
                  Error
                </span>
                <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-sm font-medium border border-blue-500/30">
                  Info
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
