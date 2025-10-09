'use client'

import React from 'react'
import { Bell, Search, Moon, Sun, RefreshCw } from 'lucide-react'
import { useThemeStore } from '@/store'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export function Header() {
  const { theme, toggleTheme } = useThemeStore()
  const [searchQuery, setSearchQuery] = React.useState('')

  return (
    <header className="sticky top-0 z-30 glass border-b border-white/10">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search projects, risks, insights..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg bg-white/5 border border-white/10 py-2 pl-10 pr-4 text-sm text-white placeholder-gray-400 focus:border-purple-500/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 ml-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => window.location.reload()}
            title="Refresh data"
          >
            <RefreshCw className="h-5 w-5" />
          </Button>

          <button
            onClick={toggleTheme}
            className="relative p-2 rounded-lg hover:bg-white/10 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </button>

          <button className="relative p-2 rounded-lg hover:bg-white/10 transition-colors">
            <Bell className="h-5 w-5" />
            <Badge
              variant="danger"
              className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              3
            </Badge>
          </button>

          <div className="flex items-center gap-3 pl-3 border-l border-white/10">
            <div className="text-right">
              <div className="text-sm font-medium">Admin User</div>
              <div className="text-xs text-gray-400">admin@example.com</div>
            </div>
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-sm font-bold">
              AU
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
